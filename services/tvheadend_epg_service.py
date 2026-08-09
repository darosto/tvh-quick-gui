from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx
from dotenv import load_dotenv
from services.tvheadend_config_service import (
    TVHeadendConfigService,
)

load_dotenv()


@dataclass(slots=True)
class GuideEvent:
    event_id: int
    channel_uuid: str
    channel_name: str
    channel_number: int
    channel_icon: str

    title: str
    subtitle: str
    description: str

    start: int
    stop: int

    recording: bool = False


class TVHeadendEPGService:
    def __init__(self) -> None:
        self.config_service = TVHeadendConfigService()

        self.timeout = httpx.Timeout(
            connect=10.0,
            read=20.0,
            write=10.0,
            pool=10.0,
        )

    async def get_epg(
        self,
        start_timestamp: int,
        stop_timestamp: int,
        limit: int = 5000,
    ) -> list[GuideEvent]:
        """
        Lädt EPG-Einträge für den angegebenen Zeitraum.
        """
        config = self.config_service.load()

        if not config.url:
            raise RuntimeError(
                "TVHeadend ist noch nicht konfiguriert."
            )

        if stop_timestamp <= start_timestamp:
            raise ValueError(
                "stop_timestamp muss größer als start_timestamp sein."
            )

        async with httpx.AsyncClient(
            base_url=config.url.rstrip("/"),
            auth=config.auth,
            timeout=self.timeout,
        ) as client:
            response = await client.get(
                "/api/epg/events/grid",
                params={
                    "start": 0,
                    "limit": limit,
                    "sort": "start",
                    "dir": "ASC",
                },
            )

            self._raise_for_status(response)

        entries = response.json().get("entries", [])

        if not isinstance(entries, list):
            raise ValueError(
                "TVHeadend lieferte keine gültige EPG-Liste."
            )

        events: list[GuideEvent] = []

        for entry in entries:
            event_start = self._optional_int(entry.get("start"))
            event_stop = self._optional_int(entry.get("stop"))

            if event_start is None or event_stop is None:
                continue

            # Nur Sendungen übernehmen, die den Zeitraum berühren.
            if event_stop <= start_timestamp:
                continue

            if event_start >= stop_timestamp:
                continue

            channel_uuid = str(
                entry.get("channelUuid", "")
            ).strip()

            if not channel_uuid:
                continue

            events.append(
                GuideEvent(
                    event_id=self._to_int(
                        entry.get("eventId")
                    ),
                    channel_uuid=channel_uuid,
                    channel_name=str(
                        entry.get(
                            "channelName",
                            "Unbekannter Sender",
                        )
                    ),
                    channel_number=self._to_int(
                        entry.get("channelNumber")
                    ),
                    channel_icon=str(
                        entry.get("channelIcon", "")
                    ),
                    title=str(
                        entry.get(
                            "title",
                            "Keine Information",
                        )
                    ),
                    subtitle=str(
                        entry.get("subtitle", "")
                    ),
                    description=str(
                        entry.get("description", "")
                    ),
                    start=event_start,
                    stop=event_stop,
                    recording=bool(
                        entry.get("dvrState")
                    ),
                )
            )

        events.sort(
            key=lambda event: (
                event.channel_number,
                event.start,
            )
        )

        return events

    def build_icon_url(self, icon_path: str) -> str:
        """
        Erzeugt eine tvh-quivk-gui Logo-URL.
        """

        icon_path = icon_path.strip()

        if not icon_path:
            return ""

        if icon_path.startswith(
            ("http://", "https://")
        ):
            return icon_path

        return f"/tvh-image/{icon_path.lstrip('/')}"

    @staticmethod
    def _raise_for_status(
        response: httpx.Response,
    ) -> None:
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as error:
            status = response.status_code

            if status == 401:
                message = (
                    "TVHeadend-Zugangsdaten sind ungültig."
                )
            elif status == 403:
                message = (
                    "Der TVHeadend-Benutzer besitzt "
                    "keine ausreichenden EPG-Rechte."
                )
            else:
                message = (
                    "TVHeadend antwortete mit "
                    f"HTTP {status}."
                )

            raise RuntimeError(message) from error

    @staticmethod
    def _to_int(
        value: Any,
        default: int = 0,
    ) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _optional_int(
        value: Any,
    ) -> int | None:
        try:
            return int(value)
        except (TypeError, ValueError):
            return None