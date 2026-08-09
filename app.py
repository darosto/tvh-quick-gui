from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from routes.dashboard import router as dashboard_router
from routes.tv import router as tv_router
from routes.guide import router as guide_router
from routes.settings import router as settings_router

app = FastAPI(title="tvh-quick-gui")

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(dashboard_router)
app.include_router(tv_router)
app.include_router(guide_router)
app.include_router(settings_router)