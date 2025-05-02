from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.api.api_v1.api import api_router
from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    description="API для интернет-радиовещания Камыши",
    version="1.0.0",
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение маршрутов API
app.include_router(api_router, prefix="/api/v1")

# Статические файлы для загруженных медиа
os.makedirs(settings.MEDIA_DIR, exist_ok=True)
app.mount("/media", StaticFiles(directory=settings.MEDIA_DIR), name="media")

@app.get("/")
def read_root():
    return {"message": "Добро пожаловать в API Радио Камыши!"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 