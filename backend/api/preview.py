from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Tuple
import base64
from io import BytesIO
from PIL import Image

from utils.seats_loader import SeatsLoader
from utils.image_mapper import ImageMapper

router = APIRouter()

import os
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
seats_loader = SeatsLoader()

class PreviewRequest(BaseModel):
    seat_colors: Dict[str, List[int]]  # seat_id -> [r, g, b]
    tribune: str = None

@router.post("/render")
async def render_preview(request: PreviewRequest):
    """
    Рендер превью по заданным цветам мест
    """
    try:
        if not seats_loader.all_seats:
            seats_loader.load()

        seats = seats_loader.all_seats
        if request.tribune:
            seats = seats_loader.get_seats_by_tribune(request.tribune)

        arena_width, arena_height = seats_loader.get_arena_dimensions()
        mapper = ImageMapper(seats, arena_width, arena_height)

        # Конвертировать seat_colors в правильный формат
        seat_colors = {int(k): tuple(v) for k, v in request.seat_colors.items()}

        # Создать превью
        preview = mapper.create_preview_image(seat_colors)

        # Конвертировать в base64
        buffered = BytesIO()
        preview.save(buffered, format="PNG")
        preview_base64 = base64.b64encode(buffered.getvalue()).decode()

        return {
            "success": True,
            "preview_image": preview_base64
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/arena-info")
async def get_arena_info():
    """Получить информацию об арене"""
    if not seats_loader.all_seats:
        seats_loader.load()

    # Возвращаем только первые 1000 мест для предпросмотра (оптимизация)
    # Полные данные используются на backend для генерации
    sample_seats = seats_loader.all_seats[::30] if len(seats_loader.all_seats) > 1000 else seats_loader.all_seats

    return {
        "dimensions": seats_loader.get_arena_dimensions(),
        "bounds": seats_loader.bounds,
        "stats": seats_loader.get_stats(),
        "seats": sample_seats
    }
