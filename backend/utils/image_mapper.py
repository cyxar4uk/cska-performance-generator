from PIL import Image, ImageDraw
import numpy as np
from typing import List, Dict, Tuple

class ImageMapper:
    """Класс для маппинга изображений на координаты мест трибун"""

    def __init__(self, seats: List[Dict], arena_width: int, arena_height: int):
        self.seats = seats
        self.arena_width = arena_width
        self.arena_height = arena_height

    def map_image_to_seats(self, image: Image.Image, fill_rate: float = 0.8) -> Dict[int, Tuple[int, int, int]]:
        """
        Маппинг изображения на места трибун

        Args:
            image: PIL изображение для маппинга
            fill_rate: процент заполнения мест (0.8 = 80% мест участвуют)

        Returns:
            Dict с seat_id -> (r, g, b) цветом для каждого места
        """
        # Ресайз изображения под размеры арены
        img_resized = image.resize((self.arena_width, self.arena_height), Image.Resampling.LANCZOS)
        img_array = np.array(img_resized)

        seat_colors = {}

        # Симулируем "битые пиксели" - не все места участвуют
        participating_seats = np.random.choice(
            len(self.seats),
            size=int(len(self.seats) * fill_rate),
            replace=False
        )

        for idx in participating_seats:
            seat = self.seats[idx]
            x, y = int(seat['x']), int(seat['y'])

            # Получить цвет из изображения
            if 0 <= x < self.arena_width and 0 <= y < self.arena_height:
                color = img_array[y, x]
                seat_colors[seat['id']] = tuple(color[:3])  # RGB

        return seat_colors

    def create_preview_image(self, seat_colors: Dict[int, Tuple[int, int, int]]) -> Image.Image:
        """
        Создать превью изображения с отображением цветов на местах

        Args:
            seat_colors: Dict с seat_id -> (r, g, b)

        Returns:
            PIL изображение превью
        """
        preview = Image.new('RGB', (self.arena_width, self.arena_height), color=(0, 0, 0))
        draw = ImageDraw.Draw(preview)

        # Отрисовать каждое место как точку
        for seat in self.seats:
            seat_id = seat['id']
            if seat_id in seat_colors:
                x, y = int(seat['x']), int(seat['y'])
                color = seat_colors[seat_id]
                # Рисуем небольшой круг для каждого места
                radius = 2
                draw.ellipse([x-radius, y-radius, x+radius, y+radius], fill=color)

        return preview

    def generate_animation_frames(
        self,
        images: List[Image.Image],
        fill_rate: float = 0.8
    ) -> List[Dict[int, Tuple[int, int, int]]]:
        """
        Генерация кадров анимации

        Args:
            images: Список PIL изображений для кадров
            fill_rate: процент заполнения мест

        Returns:
            Список словарей с цветами для каждого кадра
        """
        frames = []
        for img in images:
            frame_colors = self.map_image_to_seats(img, fill_rate)
            frames.append(frame_colors)
        return frames
