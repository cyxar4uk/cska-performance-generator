from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
import os
from dotenv import load_dotenv

from api.images import router as images_router
from api.flashlights import router as flashlights_router
from api.preview import router as preview_router

load_dotenv()

app = FastAPI(
    title="CSKA Performance Generator API",
    description="API для генерации визуальных перформансов на трибунах ВЭБ Арены",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(images_router, prefix="/api/images", tags=["images"])
app.include_router(flashlights_router, prefix="/api/flashlights", tags=["flashlights"])
app.include_router(preview_router, prefix="/api/preview", tags=["preview"])

# Дублируем роутеры без префикса /api для совместимости с proxy
app.include_router(images_router, prefix="/images", tags=["images-compat"])
app.include_router(flashlights_router, prefix="/flashlights", tags=["flashlights-compat"])
app.include_router(preview_router, prefix="/preview", tags=["preview-compat"])

@app.get("/")
async def root():
    return {
        "message": "CSKA Performance Generator API",
        "version": "2.0.0",
        "modes": ["images", "flashlights"],
        "description": "Два режима: готовые изображения и управление фонариками"
    }

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run(app, host=host, port=port)
