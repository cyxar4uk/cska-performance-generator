from PIL import Image, ImageDraw, ImageFont
import os
from typing import Dict, List, Tuple

class ImageLibrary:
    """Библиотека готовых изображений для перформансов"""

    def __init__(self, assets_dir: str = "assets/images"):
        self.assets_dir = assets_dir
        self.images = {}
        self._load_library()

    def _load_library(self):
        """Загрузить все изображения из библиотеки"""
        if not os.path.exists(self.assets_dir):
            os.makedirs(self.assets_dir)
            self._create_default_images()

        # Загрузить существующие изображения
        for filename in os.listdir(self.assets_dir):
            if filename.endswith(('.png', '.jpg', '.jpeg')):
                name = os.path.splitext(filename)[0]
                path = os.path.join(self.assets_dir, filename)
                self.images[name] = path

    def _create_default_images(self):
        """Создать базовые изображения программно"""

        # 1. Конь ЦСКА (силуэт)
        self._create_cska_horse()

        # 2. Логотип ЦСКА (упрощенный)
        self._create_cska_logo()

        # 3. Российский флаг
        self._create_russian_flag()

        # 4. Красная звезда
        self._create_red_star()

        # 5. Текст "ЦСКА"
        self._create_text_image("ЦСКА", "cska_text")

        # 6. Текст "ВПЕРЕД"
        self._create_text_image("ВПЕРЕД", "forward_text")

        # 7. Цифры для счета
        for i in range(10):
            self._create_text_image(str(i), f"number_{i}")

    def _create_cska_horse(self):
        """Создать силуэт коня ЦСКА"""
        width, height = 1200, 1000
        img = Image.new('RGB', (width, height), color='blue')
        draw = ImageDraw.Draw(img)

        # Упрощенный силуэт коня (геометрические фигуры)
        # Тело коня
        body_points = [
            (width//2 - 200, height//2),
            (width//2 + 200, height//2),
            (width//2 + 150, height//2 + 200),
            (width//2 - 150, height//2 + 200)
        ]
        draw.polygon(body_points, fill='red')

        # Голова коня
        head_center_x = width//2 - 250
        head_center_y = height//2 - 100
        draw.ellipse(
            [head_center_x - 80, head_center_y - 100,
             head_center_x + 80, head_center_y + 100],
            fill='red'
        )

        # Шея
        neck_points = [
            (width//2 - 200, height//2 - 50),
            (head_center_x + 50, head_center_y + 50),
            (head_center_x + 30, head_center_y + 80),
            (width//2 - 180, height//2 + 20)
        ]
        draw.polygon(neck_points, fill='red')

        # Ноги
        leg_width = 40
        leg_height = 150
        # Передняя левая
        draw.rectangle([width//2 - 150, height//2 + 200, width//2 - 150 + leg_width, height//2 + 200 + leg_height], fill='red')
        # Передняя правая
        draw.rectangle([width//2 - 50, height//2 + 200, width//2 - 50 + leg_width, height//2 + 200 + leg_height], fill='red')
        # Задняя левая
        draw.rectangle([width//2 + 50, height//2 + 200, width//2 + 50 + leg_width, height//2 + 200 + leg_height], fill='red')
        # Задняя правая
        draw.rectangle([width//2 + 150, height//2 + 200, width//2 + 150 + leg_width, height//2 + 200 + leg_height], fill='red')

        # Хвост
        tail_points = [
            (width//2 + 200, height//2 + 50),
            (width//2 + 300, height//2 - 50),
            (width//2 + 280, height//2 + 100)
        ]
        draw.polygon(tail_points, fill='red')

        img.save(os.path.join(self.assets_dir, 'cska_horse.png'))

    def _create_cska_logo(self):
        """Создать упрощенный логотип ЦСКА"""
        size = 1000
        img = Image.new('RGB', (size, size), color='blue')
        draw = ImageDraw.Draw(img)

        # Красная звезда в центре
        center = size // 2
        star_size = size // 3

        # Рисуем красный круг как основу
        draw.ellipse(
            [center - star_size, center - star_size,
             center + star_size, center + star_size],
            fill='red'
        )

        img.save(os.path.join(self.assets_dir, 'cska_logo.png'))

    def _create_russian_flag(self):
        """Создать российский флаг"""
        width, height = 1500, 1000
        img = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(img)

        stripe_height = height // 3

        # Белая полоса
        draw.rectangle([0, 0, width, stripe_height], fill='white')
        # Синяя полоса
        draw.rectangle([0, stripe_height, width, stripe_height * 2], fill='blue')
        # Красная полоса
        draw.rectangle([0, stripe_height * 2, width, height], fill='red')

        img.save(os.path.join(self.assets_dir, 'russian_flag.png'))

    def _create_red_star(self):
        """Создать красную звезду"""
        size = 1000
        img = Image.new('RGBA', (size, size), color=(0, 0, 255, 255))
        draw = ImageDraw.Draw(img)

        # Рисуем большую красную звезду (упрощенно - круг)
        center = size // 2
        radius = size // 3

        draw.ellipse(
            [center - radius, center - radius,
             center + radius, center + radius],
            fill='red'
        )

        img.save(os.path.join(self.assets_dir, 'red_star.png'))

    def _create_text_image(self, text: str, filename: str):
        """Создать изображение с текстом"""
        size = 1000
        img = Image.new('RGB', (size, size), color='blue')
        draw = ImageDraw.Draw(img)

        # Используем базовый шрифт
        try:
            font = ImageFont.truetype("arial.ttf", 300)
        except:
            font = ImageFont.load_default()

        # Центрируем текст
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        position = ((size - text_width) // 2, (size - text_height) // 2)

        draw.text(position, text, fill='red', font=font)

        img.save(os.path.join(self.assets_dir, f'{filename}.png'))

    def get_image(self, name: str) -> Image.Image:
        """Получить изображение по имени"""
        if name not in self.images:
            raise ValueError(f"Изображение '{name}' не найдено в библиотеке")

        return Image.open(self.images[name])

    def list_images(self) -> List[Dict[str, str]]:
        """Получить список всех доступных изображений"""
        return [
            {
                "id": name,
                "name": name.replace('_', ' ').title(),
                "path": path
            }
            for name, path in self.images.items()
        ]

    def add_custom_image(self, name: str, image: Image.Image):
        """Добавить пользовательское изображение"""
        path = os.path.join(self.assets_dir, f'{name}.png')
        image.save(path)
        self.images[name] = path
