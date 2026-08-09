
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime, timedelta

from services.tvheadend_epg_service import TVHeadendEPGService

service = TVHeadendEPGService()


router = APIRouter()
templates = Jinja2Templates(directory="templates")

PIXELS_PER_MINUTE = 8
GUIDE_HOURS = 3

def event_width(
    start: int,
    stop: int,
    guide_start: int,
    guide_stop: int,
) -> int:
    visible_start = max(start, guide_start)
    visible_stop = min(stop, guide_stop)

    if visible_stop <= visible_start:
        return 0

    minutes = (visible_stop - visible_start) / 60
    return max(1, int(minutes * PIXELS_PER_MINUTE))

def floor_to_half_hour(value: datetime) -> datetime:
    minute = 0 if value.minute < 30 else 30

    return value.replace(
        minute=minute,
        second=0,
        microsecond=0,
    )


def build_time_slots(
    start: datetime,
    hours: int,
) -> list[dict]:
    slots = []
    current = start
    stop = start + timedelta(hours=hours)

    while current <= stop:
        slots.append(
            {
                "timestamp": int(current.timestamp()),
                "label": current.strftime("%H:%M"),
                "offset": int(
                    (
                        current.timestamp()
                        - start.timestamp()
                    )
                    / 60
                    * PIXELS_PER_MINUTE
                ),
            }
        )

        current += timedelta(minutes=30)

    return slots

@router.get("/guide", response_class=HTMLResponse)
async def guide(request: Request):
    now = datetime.now()
    guide_start = floor_to_half_hour(now)
    guide_stop = guide_start + timedelta(hours=GUIDE_HOURS)
    guide_start_timestamp = int(guide_start.timestamp())
    guide_stop_timestamp = int(guide_stop.timestamp())

    events = await service.get_epg(
        guide_start_timestamp,
        guide_stop_timestamp,
    )

    channels = {}

    for event in events:
        channel = channels.setdefault(
            event.channel_uuid,
            {
                "uuid": event.channel_uuid,
                "number": event.channel_number,
                "name": event.channel_name,
                "icon": service.build_icon_url(
                    event.channel_icon
                ),
                "stream_url": f"/tvh-stream/{event.channel_uuid}",
                "events": [],
            },
        )

        channel["events"].append(
            {
                "event_id": event.event_id,
                "title": event.title,
                "subtitle": event.subtitle,
                "description": event.description,
                "start": event.start,
                "stop": event.stop,
                "start_label": datetime.fromtimestamp(
                    event.start
                ).strftime("%H:%M"),
                "stop_label": datetime.fromtimestamp(
                    event.stop
                ).strftime("%H:%M"),
                "width": event_width(
                    event.start,
                    event.stop,
                    guide_start_timestamp,
                    guide_stop_timestamp,
                ),
            }
        )

    channels = sorted(
        channels.values(),
        key=lambda channel: channel["number"],
    )

    guide_width = (
        GUIDE_HOURS
        * 60
        * PIXELS_PER_MINUTE
    )

    now_offset = int(
        (
            now.timestamp()
            - guide_start.timestamp()
        )
        / 60
        * PIXELS_PER_MINUTE
    )

    return templates.TemplateResponse(
        request=request,
        name="guide.html",
        context={
            "channels": channels,
            "time_slots": build_time_slots(
                guide_start,
                GUIDE_HOURS,
            ),
            "guide_width": guide_width,
            "now_offset": now_offset,
            "now_label": now.strftime("%H:%M"),
            "guide_start": int(
                guide_start.timestamp()
            ),
            "guide_stop": int(
                guide_stop.timestamp()
            ),
        },
    )