from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from config.menu import menu

router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):

    menu = [
        {
            "title": "Live TV",
            "icon": "📺",
            "action": "/tv",
            "disabled": False,
        },
        {
            "title": "TV Guide",
            "icon": "📖",
            "action": "/guide",
            "disabled": False,
        },
        {
            "title": "Recordings",
            "icon": "⏺",
            "action": "/recordings",
            "disabled": True,
        },
        {
            "title": "Settings",
            "icon": "⚙",
            "action": "/settings",
            "disabled": True,
        },
        {
            "title": "Help",
            "icon": "?",
            "action": "/help",
            "disabled": True,
        },
        {
            "title": "Contact",
            "icon": "✉",
            "action": "/contact",
            "disabled": True,
        },
    ]
    return templates.TemplateResponse(
       request=request,
       name="dashboard.html",
       context={
           "menu": menu
       }
    )
