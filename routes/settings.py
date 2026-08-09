from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from services.tvheadend_config_service import (
    TVHeadendConfig,
    TVHeadendConfigService,
)
from services.tvheadend_connection_test_service import (
    TVHeadendConnectionTestService,
)

from routes.dashboard import menu

router = APIRouter()
templates = Jinja2Templates(directory="templates")

config_service = TVHeadendConfigService()
connection_test_service = TVHeadendConnectionTestService()


@router.get(
    "/settings",
    response_class=HTMLResponse,
)
async def settings_page(request: Request):
    config = config_service.load()

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "menu": menu,
            "view": "settings",
            "config": config,
            "saved": False,
        },
    )

@router.post(
    "/settings",
    response_class=HTMLResponse,
)
async def settings_save(
    request: Request,
    url: str = Form(...),
    username: str = Form(""),
    password: str = Form(""),
):
    current_config = config_service.load()

    config = TVHeadendConfig(
        url=url.strip(),
        username=username.strip(),
        password=(
            password
            if password
            else current_config.password
        ),
    )

    config_service.save(config)

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "menu": menu,
            "view": "settings",
            "config": config,
            "saved": True,
        },
    )


@router.post(
    "/settings/test",
    response_class=HTMLResponse,
)
async def settings_test(
    request: Request,
    url: str = Form(...),
    username: str = Form(""),
    password: str = Form(""),
):
    current_config = config_service.load()

    test_config = TVHeadendConfig(
        url=url.strip(),
        username=username.strip(),
        password=(
            password
            if password
            else current_config.password
        ),
    )

    result = await connection_test_service.test(
        test_config
    )

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "menu": menu,
            "view": "settings",
            "config": test_config,
            "saved": False,
            "test_result": result,
        },
    )