import os
import httpx
from dotenv import load_dotenv
from collections.abc import AsyncIterator
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response, StreamingResponse
from fastapi.templating import Jinja2Templates

from services.tvheadend_channel_service import (
    TVHeadendChannelService,
)
from services.tvheadend_config_service import (
    TVHeadendConfigService,
)
load_dotenv()

router = APIRouter()
templates = Jinja2Templates(directory="templates")

channel_service = TVHeadendChannelService()
config_service = TVHeadendConfigService()

@router.get("/tv", response_class=HTMLResponse)
async def tv(request: Request):
    try:
        channels = await channel_service.get_channels()
    except (httpx.RequestError, RuntimeError) as error:
        return templates.TemplateResponse(
            request=request,
            name="tv.html",
            context={
                "channels": [],
                "selected_channel": 0,
                "tvh_error": str(error),
            },
            status_code=503,
        )

    return templates.TemplateResponse(
        request=request,
        name="tv.html",
        context={
            "channels": channels,
            "selected_channel": 0,
            "tvh_error": None,
        },
    )


@router.get("/tvh-image/{image_path:path}")
async def tvh_image(image_path: str):
    if not image_path.startswith("imagecache/"):
        raise HTTPException(status_code=404)

    config = config_service.load()

    if not config.url:
        raise RuntimeError(
            "TVHeadend ist noch nicht konfiguriert."
        )

    base_url = config.url.rstrip("/")
    auth = config.auth

    try:
        async with httpx.AsyncClient(
            auth=auth,
            timeout=10.0,
        ) as client:
            response = await client.get(
                f"{base_url}/{image_path}"
            )
            response.raise_for_status()

    except httpx.HTTPStatusError as error:
        raise HTTPException(
            status_code=error.response.status_code
        ) from error
    except httpx.RequestError as error:
        raise HTTPException(status_code=502) from error

    return Response(
        content=response.content,
        media_type=response.headers.get(
            "content-type",
            "image/png",
        ),
        headers={
            "Cache-Control": "public, max-age=3600",
        },
    )

@router.get("/tvh-stream/{channel_uuid}")
async def tvh_stream(channel_uuid: str):
    if not channel_uuid or not channel_uuid.isalnum():
        raise HTTPException(status_code=400, detail="Ungültige Sender-UUID")

    config = config_service.load()

    if not config.url:
        raise HTTPException(
            status_code=500,
            detail="TVHeadend ist nicht konfiguriert.",
        )

    base_url = config.url.rstrip("/")
    auth = config.auth

    params = {}
    profile = os.getenv(
        "TVH_STREAM_PROFILE",
        "",
    ).strip()
    if profile:
        params["profile"] = profile

    client = httpx.AsyncClient(
        auth=auth,
        timeout=httpx.Timeout(
            connect=10.0,
            read=None,
            write=10.0,
            pool=10.0,
        ),
        follow_redirects=True,
    )

    request = client.build_request(
        "GET",
        f"{base_url}/stream/channel/{channel_uuid}",
        params=params,
    )

    try:
        response = await client.send(request, stream=True)
        response.raise_for_status()
    except httpx.HTTPError as error:
        await client.aclose()

        raise HTTPException(
            status_code=502,
            detail="TVHeadend-Stream konnte nicht geöffnet werden. Prüfe Streaming-profile",
        ) from error

    async def stream_body() -> AsyncIterator[bytes]:
        try:
            async for chunk in response.aiter_bytes(64 * 1024):
                yield chunk
        finally:
            await response.aclose()
            await client.aclose()

    return StreamingResponse(
        stream_body(),
        media_type=response.headers.get(
            "content-type",
            "video/mp2t",
        ),
        headers={
            "Cache-Control": "no-store",
            "X-Accel-Buffering": "no",
        },
    )

@router.get("/api/tv/channels/{channel_uuid}/events")
async def channel_events(channel_uuid: str):
    if not channel_uuid or not channel_uuid.isalnum():
        raise HTTPException(
            status_code=400,
            detail="Ungültige Sender-UUID",
        )

    try:
        events = await channel_service.get_channel_events(
            channel_uuid=channel_uuid,
            limit=6,
        )
    except httpx.RequestError as error:
        raise HTTPException(
            status_code=502,
            detail="TVHeadend ist nicht erreichbar.",
        ) from error
    except RuntimeError as error:
        raise HTTPException(
            status_code=502,
            detail=str(error),
        ) from error

    return JSONResponse(
        {
            "channel_uuid": channel_uuid,
            "events": [event.to_dict() for event in events],
        }
    )
