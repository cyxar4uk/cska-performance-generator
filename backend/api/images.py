from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional, List, Dict
import base64
from io import BytesIO
from PIL import Image

from services.image_library import ImageLibrary
from utils.seats_loader import SeatsLoader
from utils.image_mapper import ImageMapper

router = APIRouter()

# Инициализация
import os
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
seats_loader = SeatsLoader()
seats_loader.load()  # Загрузить сразу при старте
image_library = ImageLibrary()

class ImageGenerateRequest(BaseModel):
    image_id: str  # ID изображения из библиотеки
    tribune: Optional[str] = None  # A, C, K, S или None для всей арены
    fill_rate: float = 0.8
    scale: float = 1.0  # Масштаб изображения
    rotation: int = 0  # Поворот в градусах
    brightness: float = 1.0  # Яркость (0.0 - 2.0)
    contrast: float = 1.0  # Контраст (0.0 - 2.0)

class ImageGenerateResponse(BaseModel):
    success: bool
    preview_image: str  # base64
    seat_colors: dict
    stats: dict

@router.get("/library")
async def get_image_library():
    """Получить список доступных изображений"""
    return {
        "images": image_library.list_images()
    }

@router.post("/generate", response_model=ImageGenerateResponse)
async def generate_from_image(request: ImageGenerateRequest):
    """
    Генерация перформанса из готового изображения
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

        # Получить изображение из библиотеки
        try:
            image = image_library.get_image(request.image_id)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))

        # Применить трансформации
        if request.rotation != 0:
            image = image.rotate(request.rotation, expand=True)

        if request.scale != 1.0:
            new_size = (int(image.width * request.scale), int(image.height * request.scale))
            image = image.resize(new_size)

        # Применить яркость и контраст
        from PIL import ImageEnhance
        if request.brightness != 1.0:
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(request.brightness)

        if request.contrast != 1.0:
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(request.contrast)

        # Маппинг на места
        arena_width, arena_height = seats_loader.get_arena_dimensions()
        mapper = ImageMapper(seats, arena_width, arena_height)
        seat_colors = mapper.map_image_to_seats(image, request.fill_rate)

        # Создать превью
        preview = mapper.create_preview_image(seat_colors)

        # Конвертировать превью в base64
        buffered = BytesIO()
        preview.save(buffered, format="PNG")
        preview_base64 = base64.b64encode(buffered.getvalue()).decode()

        return ImageGenerateResponse(
            success=True,
            preview_image=preview_base64,
            seat_colors={str(k): [int(c) for c in v] for k, v in seat_colors.items()},
            stats={
                "total_seats": len(seats),
                "active_seats": len(seat_colors),
                "fill_rate": len(seat_colors) / len(seats) if seats else 0,
                "image_id": request.image_id
            }
        )

    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        print(f"ERROR in generate_from_image: {error_detail}")
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

@router.post("/upload")
async def upload_image(file: UploadFile = File(...), name: Optional[str] = None):
    """Загрузить пользовательское изображение в библиотеку"""
    try:
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Файл должен быть изображением")

        contents = await file.read()
        image = Image.open(BytesIO(contents))

        image_name = name or file.filename.rsplit('.', 1)[0]
        image_library.add_custom_image(image_name, image)

        return {
            "success": True,
            "image_id": image_name,
            "message": f"Изображение '{image_name}' успешно загружено"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
