from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


CONFIG_PATH = Path("config/tvheadend.json")


@dataclass(slots=True)
class TVHeadendConfig:
    url: str
    username: str = ""
    password: str = ""

    @property
    def auth(self):
        username = self.username.strip()
        password = self.password.strip()

        if not username or not password:
            return None

        if (
            username.lower() == "none"
            or password.lower() == "none"
        ):
            return None

        return (username, password)


class TVHeadendConfigService:
    def __init__(
        self,
        config_path: Path = CONFIG_PATH,
    ) -> None:
        self.config_path = config_path

    def load(self) -> TVHeadendConfig:
        if not self.config_path.exists():
            return TVHeadendConfig(
                url="",
                username="",
                password="",
            )

        with self.config_path.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        return TVHeadendConfig(
            url=str(data.get("url", "")).strip(),
            username=str(
                data.get("username", "")
            ).strip(),
            password=str(
                data.get("password", "")
            ),
        )

    def save(
        self,
        config: TVHeadendConfig,
    ) -> None:
        self.config_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        data = {
            "url": config.url.rstrip("/"),
            "username": config.username,
            "password": config.password,
        }

        with self.config_path.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False,
            )