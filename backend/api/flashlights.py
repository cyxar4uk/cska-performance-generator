from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Tuple
import base64
from io import BytesIO

from services.flashlight_scenarios import ScenarioManager
from utils.seats_loader import SeatsLoader
from utils.image_mapper import ImageMapper

router = APIRouter()

seats_loader = SeatsLoader()

class FlashlightRequest(BaseModel):
    scenario: str  # wave, flash, gradient, pulse, cascade, text_scroll
    tribune: Optional[str] = None
    frames: int = 20
    fill_rate: float = 0.8

    # Параметры цветов
    color1: Optional[List[int]] = [255, 0, 0]  # Красный
    color2: Optional[List[int]] = [0, 0, 255]  # Синий
    background: Optional[List[int]] = [0, 0, 0]  # Черный

    # Параметры направления
    direction: Optional[str] = "horizontal"  # horizontal, vertical, circular

    # Параметры для текста
    text: Optional[str] = None
    font_size: Optional[int] = 100

    # Параметры яркости
    min_brightness: Optional[float] = 0.2
    max_brightness: Optional[float] = 1.0

class FlashlightResponse(BaseModel):
    success: bool
    frames: List[str]  # base64 encoded images
    stats: dict
    scenario_info: dict

@router.get("/scenarios")
async def get_scenarios():
    """Получить список доступных сценариев"""
    return {
        "scenarios": ScenarioManager.list_scenarios()
    }

@router.post("/generate", response_model=FlashlightResponse)
async def generate_flashlight_scenario(request: FlashlightRequest):
    """
    Генерация сценария управления фонариками
    """
    try:
        # Загрузить данные о местах
        if not seats_loader.all_seats:
            seats_loader.load()

        # Выбрать места
        if request.tribune:
            seats = seats_loader.get_seats_by_tribune(request.tribune)
            if not seats:
                raise HTTPException(status_code=400, detail=f"Трибуна {request.tribune} не найдена")
        else:
            seats = seats_loader.all_seats

        # Подготовить параметры сценария
        scenario_params = {}

        if request.scenario in ['wave', 'gradient']:
            scenario_params['color1'] = tuple(request.color1)
            scenario_params['color2'] = tuple(request.color2)
            scenario_params['direction'] = request.direction

        elif request.scenario == 'flash':
            scenario_params['color'] = tuple(request.color1)
            scenario_params['background'] = tuple(request.background)

        elif request.scenario == 'pulse':
            scenario_params['color'] = tuple(request.color1)
            scenario_params['min_brightness'] = request.min_brightness
            scenario_params['max_brightness'] = request.max_brightness

        elif request.scenario == 'cascade':
            scenario_params['color'] = tuple(request.color1)
            scenario_params['background'] = tuple(request.background)

        elif request.scenario == 'text_scroll':
            if not request.text:
                raise HTTPException(status_code=400, detail="Текст обязателен для сценария text_scroll")
            scenario_params['text'] = request.text
            scenario_params['color'] = tuple(request.color1)
            scenario_params['background'] = tuple(request.background)
            scenario_params['font_size'] = request.font_size

        # Создать сценарий
        arena_width, arena_height = seats_loader.get_arena_dimensions()
        scenario = ScenarioManager.create_scenario(
            request.scenario,
            seats,
            arena_width,
            arena_height,
            **scenario_params
        )

        # Генерация кадров
        mapper = ImageMapper(seats, arena_width, arena_height)
        frame_previews = []

        for frame_idx in range(request.frames):
            # Получить цвета для этого кадра
            seat_colors = scenario.generate_frame(frame_idx, request.frames)

            # Применить fill_rate
            if request.fill_rate < 1.0:
                import random
                active_seats = random.sample(
                    list(seat_colors.keys()),
                    int(len(seat_colors) * request.fill_rate)
                )
                seat_colors = {k: v for k, v in seat_colors.items() if k in active_seats}

            # Создать превью
            preview = mapper.create_preview_image(seat_colors)

            # Конвертировать в base64
            buffered = BytesIO()
            preview.save(buffered, format="PNG")
            preview_base64 = base64.b64encode(buffered.getvalue()).decode()
            frame_previews.append(preview_base64)

        return FlashlightResponse(
            success=True,
            frames=frame_previews,
            stats={
                "total_seats": len(seats),
                "frames": len(frame_previews),
                "fill_rate": request.fill_rate,
                "scenario": request.scenario
            },
            scenario_info={
                "type": request.scenario,
                "direction": request.direction,
                "colors": {
                    "color1": request.color1,
                    "color2": request.color2,
                    "background": request.background
                }
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tribunes")
async def get_tribunes():
    """Получить список доступных трибун"""
    if not seats_loader.all_seats:
        seats_loader.load()

    return {
        "tribunes": seats_loader.get_all_tribunes(),
        "stats": seats_loader.get_stats()
    }
