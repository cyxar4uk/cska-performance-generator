from typing import Dict, List, Tuple, Callable
import numpy as np
import math

class FlashlightScenario:
    """Базовый класс для сценариев управления фонариками"""

    def __init__(self, seats: List[Dict], arena_width: int, arena_height: int):
        self.seats = seats
        self.arena_width = arena_width
        self.arena_height = arena_height

    def generate_frame(self, frame_number: int, total_frames: int) -> Dict[int, Tuple[int, int, int]]:
        """
        Генерация одного кадра сценария

        Returns:
            Dict с seat_id -> (r, g, b) для каждого места
        """
        raise NotImplementedError


class WaveScenario(FlashlightScenario):
    """Сценарий волны по трибунам"""

    def __init__(self, seats, arena_width, arena_height,
                 color1: Tuple[int, int, int] = (255, 0, 0),
                 color2: Tuple[int, int, int] = (0, 0, 255),
                 direction: str = "horizontal"):
        super().__init__(seats, arena_width, arena_height)
        self.color1 = color1
        self.color2 = color2
        self.direction = direction

    def generate_frame(self, frame_number: int, total_frames: int) -> Dict[int, Tuple[int, int, int]]:
        seat_colors = {}
        progress = frame_number / total_frames

        for seat in self.seats:
            if self.direction == "horizontal":
                position = seat['x'] / self.arena_width
            elif self.direction == "vertical":
                position = seat['y'] / self.arena_height
            else:  # circular
                center_x = self.arena_width / 2
                center_y = self.arena_height / 2
                dx = seat['x'] - center_x
                dy = seat['y'] - center_y
                position = math.sqrt(dx*dx + dy*dy) / (self.arena_width / 2)

            # Волна движется
            wave_position = (position + progress) % 1.0

            # Интерполяция между цветами
            if wave_position < 0.5:
                t = wave_position * 2
                color = self._interpolate_color(self.color1, self.color2, t)
            else:
                t = (wave_position - 0.5) * 2
                color = self._interpolate_color(self.color2, self.color1, t)

            seat_colors[seat['id']] = color

        return seat_colors

    def _interpolate_color(self, c1: Tuple[int, int, int], c2: Tuple[int, int, int], t: float) -> Tuple[int, int, int]:
        """Интерполяция между двумя цветами"""
        return (
            int(c1[0] + (c2[0] - c1[0]) * t),
            int(c1[1] + (c2[1] - c1[1]) * t),
            int(c1[2] + (c2[2] - c1[2]) * t)
        )


class FlashScenario(FlashlightScenario):
    """Сценарий вспышек"""

    def __init__(self, seats, arena_width, arena_height,
                 color: Tuple[int, int, int] = (255, 255, 255),
                 background: Tuple[int, int, int] = (0, 0, 0),
                 flash_duration: float = 0.2):
        super().__init__(seats, arena_width, arena_height)
        self.color = color
        self.background = background
        self.flash_duration = flash_duration

    def generate_frame(self, frame_number: int, total_frames: int) -> Dict[int, Tuple[int, int, int]]:
        seat_colors = {}
        progress = frame_number / total_frames

        # Синусоидальная вспышка
        intensity = abs(math.sin(progress * math.pi * 4))  # 4 вспышки за цикл

        for seat in self.seats:
            if intensity > 0.7:  # Вспышка
                seat_colors[seat['id']] = self.color
            else:  # Фон
                seat_colors[seat['id']] = self.background

        return seat_colors


class GradientScenario(FlashlightScenario):
    """Сценарий градиента"""

    def __init__(self, seats, arena_width, arena_height,
                 colors: List[Tuple[int, int, int]] = None,
                 direction: str = "horizontal"):
        super().__init__(seats, arena_width, arena_height)
        self.colors = colors or [(255, 0, 0), (0, 0, 255)]
        self.direction = direction

    def generate_frame(self, frame_number: int, total_frames: int) -> Dict[int, Tuple[int, int, int]]:
        seat_colors = {}

        for seat in self.seats:
            if self.direction == "horizontal":
                position = seat['x'] / self.arena_width
            else:  # vertical
                position = seat['y'] / self.arena_height

            # Определить между какими цветами интерполировать
            segment = position * (len(self.colors) - 1)
            idx = int(segment)
            t = segment - idx

            if idx >= len(self.colors) - 1:
                color = self.colors[-1]
            else:
                c1 = self.colors[idx]
                c2 = self.colors[idx + 1]
                color = (
                    int(c1[0] + (c2[0] - c1[0]) * t),
                    int(c1[1] + (c2[1] - c1[1]) * t),
                    int(c1[2] + (c2[2] - c1[2]) * t)
                )

            seat_colors[seat['id']] = color

        return seat_colors


class PulseScenario(FlashlightScenario):
    """Сценарий пульсации"""

    def __init__(self, seats, arena_width, arena_height,
                 color: Tuple[int, int, int] = (255, 0, 0),
                 min_brightness: float = 0.2,
                 max_brightness: float = 1.0):
        super().__init__(seats, arena_width, arena_height)
        self.color = color
        self.min_brightness = min_brightness
        self.max_brightness = max_brightness

    def generate_frame(self, frame_number: int, total_frames: int) -> Dict[int, Tuple[int, int, int]]:
        seat_colors = {}
        progress = frame_number / total_frames

        # Синусоидальная пульсация
        brightness = self.min_brightness + (self.max_brightness - self.min_brightness) * \
                     (0.5 + 0.5 * math.sin(progress * math.pi * 2))

        for seat in self.seats:
            color = (
                int(self.color[0] * brightness),
                int(self.color[1] * brightness),
                int(self.color[2] * brightness)
            )
            seat_colors[seat['id']] = color

        return seat_colors


class SectorCascadeScenario(FlashlightScenario):
    """Сценарий каскада по секторам"""

    def __init__(self, seats, arena_width, arena_height,
                 color: Tuple[int, int, int] = (255, 0, 0),
                 background: Tuple[int, int, int] = (0, 0, 0)):
        super().__init__(seats, arena_width, arena_height)
        self.color = color
        self.background = background

        # Группировка мест по секторам
        self.sectors = {}
        for seat in seats:
            sector = seat.get('sector', 'unknown')
            if sector not in self.sectors:
                self.sectors[sector] = []
            self.sectors[sector].append(seat)

    def generate_frame(self, frame_number: int, total_frames: int) -> Dict[int, Tuple[int, int, int]]:
        seat_colors = {}
        progress = frame_number / total_frames

        sector_list = list(self.sectors.keys())
        active_sectors = int(progress * len(sector_list))

        for idx, sector_name in enumerate(sector_list):
            if idx < active_sectors:
                # Активный сектор
                for seat in self.sectors[sector_name]:
                    seat_colors[seat['id']] = self.color
            else:
                # Неактивный сектор
                for seat in self.sectors[sector_name]:
                    seat_colors[seat['id']] = self.background

        return seat_colors


class TextScrollScenario(FlashlightScenario):
    """Сценарий бегущей строки"""

    def __init__(self, seats, arena_width, arena_height,
                 text: str = "CSKA",
                 color: Tuple[int, int, int] = (255, 0, 0),
                 background: Tuple[int, int, int] = (0, 0, 0),
                 font_size: int = 100):
        super().__init__(seats, arena_width, arena_height)
        self.text = text
        self.color = color
        self.background = background
        self.font_size = font_size

    def generate_frame(self, frame_number: int, total_frames: int) -> Dict[int, Tuple[int, int, int]]:
        from PIL import Image, ImageDraw, ImageFont

        # Создать изображение с текстом
        img = Image.new('RGB', (self.arena_width, self.arena_height), self.background)
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype("arial.ttf", self.font_size)
        except:
            font = ImageFont.load_default()

        # Позиция текста (движется слева направо)
        progress = frame_number / total_frames
        text_x = int(-self.arena_width + progress * self.arena_width * 2)
        text_y = self.arena_height // 2 - self.font_size // 2

        draw.text((text_x, text_y), self.text, fill=self.color, font=font)

        # Конвертировать в цвета для мест
        img_array = np.array(img)
        seat_colors = {}

        for seat in self.seats:
            x, y = int(seat['x']), int(seat['y'])
            if 0 <= x < self.arena_width and 0 <= y < self.arena_height:
                color = tuple(img_array[y, x])
                seat_colors[seat['id']] = color

        return seat_colors


class FireScenario(FlashlightScenario):
    """Сценарий огня - эффект пламени"""

    def __init__(self, seats, arena_width, arena_height,
                 intensity: float = 1.0):
        super().__init__(seats, arena_width, arena_height)
        self.intensity = intensity

    def generate_frame(self, frame_number: int, total_frames: int) -> Dict[int, Tuple[int, int, int]]:
        import random
        seat_colors = {}
        progress = frame_number / total_frames

        for seat in self.seats:
            # Огонь движется снизу вверх
            height_factor = 1.0 - (seat['y'] / self.arena_height)

            # Добавляем случайность для эффекта мерцания
            flicker = random.uniform(0.7, 1.0)
            time_wave = 0.5 + 0.5 * math.sin(progress * math.pi * 4 + seat['x'] * 0.1)

            # Интенсивность огня зависит от высоты
            fire_intensity = height_factor * flicker * time_wave * self.intensity

            # Цвета огня: от желтого к красному к черному
            if fire_intensity > 0.6:
                # Яркое пламя - желтый/оранжевый
                r = 255
                g = int(200 * fire_intensity)
                b = 0
            elif fire_intensity > 0.3:
                # Среднее пламя - оранжевый/красный
                r = 255
                g = int(100 * fire_intensity)
                b = 0
            else:
                # Слабое пламя - красный/темный
                r = int(200 * fire_intensity)
                g = int(50 * fire_intensity)
                b = 0

            seat_colors[seat['id']] = (r, g, b)

        return seat_colors


class RainbowScenario(FlashlightScenario):
    """Сценарий радуги - переливающиеся цвета"""

    def __init__(self, seats, arena_width, arena_height,
                 speed: float = 1.0,
                 direction: str = "horizontal"):
        super().__init__(seats, arena_width, arena_height)
        self.speed = speed
        self.direction = direction

    def generate_frame(self, frame_number: int, total_frames: int) -> Dict[int, Tuple[int, int, int]]:
        seat_colors = {}
        progress = frame_number / total_frames

        for seat in self.seats:
            # Определяем позицию для радуги
            if self.direction == "horizontal":
                position = seat['x'] / self.arena_width
            elif self.direction == "vertical":
                position = seat['y'] / self.arena_height
            else:  # circular
                center_x = self.arena_width / 2
                center_y = self.arena_height / 2
                angle = math.atan2(seat['y'] - center_y, seat['x'] - center_x)
                position = (angle + math.pi) / (2 * math.pi)

            # Радуга движется
            hue = (position + progress * self.speed) % 1.0

            # Конвертируем HSV в RGB
            color = self._hsv_to_rgb(hue, 1.0, 1.0)
            seat_colors[seat['id']] = color

        return seat_colors

    def _hsv_to_rgb(self, h: float, s: float, v: float) -> Tuple[int, int, int]:
        """Конвертация HSV в RGB"""
        import colorsys
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return (int(r * 255), int(g * 255), int(b * 255))


class StarsScenario(FlashlightScenario):
    """Сценарий звезд - мерцающие точки"""

    def __init__(self, seats, arena_width, arena_height,
                 color: Tuple[int, int, int] = (255, 255, 255),
                 density: float = 0.1,
                 twinkle_speed: float = 1.0):
        super().__init__(seats, arena_width, arena_height)
        self.color = color
        self.density = density
        self.twinkle_speed = twinkle_speed

        # Назначаем каждому месту случайную фазу мерцания
        import random
        self.star_phases = {seat['id']: random.random() for seat in seats}
        self.is_star = {seat['id']: random.random() < density for seat in seats}

    def generate_frame(self, frame_number: int, total_frames: int) -> Dict[int, Tuple[int, int, int]]:
        seat_colors = {}
        progress = frame_number / total_frames

        for seat in self.seats:
            if self.is_star[seat['id']]:
                # Мерцание звезды
                phase = self.star_phases[seat['id']]
                brightness = 0.3 + 0.7 * abs(math.sin((progress + phase) * math.pi * 2 * self.twinkle_speed))

                color = (
                    int(self.color[0] * brightness),
                    int(self.color[1] * brightness),
                    int(self.color[2] * brightness)
                )
                seat_colors[seat['id']] = color
            else:
                # Темный фон
                seat_colors[seat['id']] = (0, 0, 0)

        return seat_colors


class HeartScenario(FlashlightScenario):
    """Сценарий сердца - форма сердца пульсирует"""

    def __init__(self, seats, arena_width, arena_height,
                 color: Tuple[int, int, int] = (255, 0, 0),
                 background: Tuple[int, int, int] = (0, 0, 0),
                 scale: float = 0.5):
        super().__init__(seats, arena_width, arena_height)
        self.color = color
        self.background = background
        self.scale = scale

    def generate_frame(self, frame_number: int, total_frames: int) -> Dict[int, Tuple[int, int, int]]:
        seat_colors = {}
        progress = frame_number / total_frames

        # Пульсация сердца
        pulse = 0.8 + 0.2 * math.sin(progress * math.pi * 2)

        center_x = self.arena_width / 2
        center_y = self.arena_height / 2

        for seat in self.seats:
            # Нормализуем координаты относительно центра
            x = (seat['x'] - center_x) / (self.arena_width * self.scale * pulse)
            y = (seat['y'] - center_y) / (self.arena_height * self.scale * pulse)

            # Формула сердца: (x^2 + y^2 - 1)^3 - x^2*y^3 = 0
            # Упрощенная проверка принадлежности к форме сердца
            heart_value = (x*x + y*y - 1)**3 - x*x * y*y*y

            if heart_value < 0:
                # Внутри сердца - градиент от центра
                distance = math.sqrt(x*x + y*y)
                brightness = max(0.5, 1.0 - distance * 0.3)
                color = (
                    int(self.color[0] * brightness),
                    int(self.color[1] * brightness),
                    int(self.color[2] * brightness)
                )
                seat_colors[seat['id']] = color
            else:
                # Вне сердца
                seat_colors[seat['id']] = self.background

        return seat_colors


class ScoreScenario(FlashlightScenario):
    """Сценарий счета - отображение счета матча крупными цифрами"""

    def __init__(self, seats, arena_width, arena_height,
                 home_score: int = 0,
                 away_score: int = 0,
                 color: Tuple[int, int, int] = (255, 255, 255),
                 background: Tuple[int, int, int] = (0, 0, 0)):
        super().__init__(seats, arena_width, arena_height)
        self.home_score = home_score
        self.away_score = away_score
        self.color = color
        self.background = background

    def generate_frame(self, frame_number: int, total_frames: int) -> Dict[int, Tuple[int, int, int]]:
        from PIL import Image, ImageDraw, ImageFont

        # Создать изображение со счетом
        img = Image.new('RGB', (self.arena_width, self.arena_height), self.background)
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype("arial.ttf", 200)
        except:
            font = ImageFont.load_default()

        # Текст счета
        score_text = f"{self.home_score} : {self.away_score}"

        # Центрируем текст
        bbox = draw.textbbox((0, 0), score_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        text_x = (self.arena_width - text_width) // 2
        text_y = (self.arena_height - text_height) // 2

        # Пульсация счета
        progress = frame_number / total_frames
        brightness = 0.7 + 0.3 * abs(math.sin(progress * math.pi * 2))

        pulse_color = (
            int(self.color[0] * brightness),
            int(self.color[1] * brightness),
            int(self.color[2] * brightness)
        )

        draw.text((text_x, text_y), score_text, fill=pulse_color, font=font)

        # Конвертировать в цвета для мест
        img_array = np.array(img)
        seat_colors = {}

        for seat in self.seats:
            x, y = int(seat['x']), int(seat['y'])
            if 0 <= x < self.arena_width and 0 <= y < self.arena_height:
                color = tuple(img_array[y, x])
                seat_colors[seat['id']] = color

        return seat_colors


class CombinedScenario(FlashlightScenario):
    """Комбинированный сценарий - объединяет несколько сценариев"""

    def __init__(self, seats, arena_width, arena_height,
                 scenarios: List[Tuple[FlashlightScenario, float]]):
        """
        scenarios: список кортежей (сценарий, вес)
        вес определяет влияние сценария на итоговый цвет (0.0 - 1.0)
        """
        super().__init__(seats, arena_width, arena_height)
        self.scenarios = scenarios

    def generate_frame(self, frame_number: int, total_frames: int) -> Dict[int, Tuple[int, int, int]]:
        seat_colors = {}

        # Собираем цвета от всех сценариев
        all_colors = []
        for scenario, weight in self.scenarios:
            colors = scenario.generate_frame(frame_number, total_frames)
            all_colors.append((colors, weight))

        # Комбинируем цвета
        for seat in self.seats:
            r, g, b = 0, 0, 0
            total_weight = 0

            for colors, weight in all_colors:
                if seat['id'] in colors:
                    color = colors[seat['id']]
                    r += color[0] * weight
                    g += color[1] * weight
                    b += color[2] * weight
                    total_weight += weight

            if total_weight > 0:
                seat_colors[seat['id']] = (
                    int(min(255, r / total_weight)),
                    int(min(255, g / total_weight)),
                    int(min(255, b / total_weight))
                )
            else:
                seat_colors[seat['id']] = (0, 0, 0)

        return seat_colors


class ScenarioManager:
    """Менеджер сценариев"""

    SCENARIOS = {
        'wave': WaveScenario,
        'flash': FlashScenario,
        'gradient': GradientScenario,
        'pulse': PulseScenario,
        'cascade': SectorCascadeScenario,
        'text_scroll': TextScrollScenario,
        'fire': FireScenario,
        'rainbow': RainbowScenario,
        'stars': StarsScenario,
        'heart': HeartScenario,
        'score': ScoreScenario
    }

    @classmethod
    def create_scenario(cls, scenario_type: str, seats, arena_width, arena_height, **params):
        """Создать сценарий по типу"""
        if scenario_type not in cls.SCENARIOS:
            raise ValueError(f"Неизвестный тип сценария: {scenario_type}")

        scenario_class = cls.SCENARIOS[scenario_type]
        return scenario_class(seats, arena_width, arena_height, **params)

    @classmethod
    def create_combined_scenario(cls, seats, arena_width, arena_height,
                                 scenario_configs: List[Dict]) -> CombinedScenario:
        """
        Создать комбинированный сценарий

        scenario_configs: список конфигураций вида:
        [
            {'type': 'wave', 'weight': 0.5, 'params': {...}},
            {'type': 'pulse', 'weight': 0.5, 'params': {...}}
        ]
        """
        scenarios = []
        for config in scenario_configs:
            scenario_type = config['type']
            weight = config.get('weight', 1.0)
            params = config.get('params', {})

            scenario = cls.create_scenario(scenario_type, seats, arena_width, arena_height, **params)
            scenarios.append((scenario, weight))

        return CombinedScenario(seats, arena_width, arena_height, scenarios)

    @classmethod
    def list_scenarios(cls) -> List[Dict[str, str]]:
        """Получить список доступных сценариев"""
        return [
            {
                'id': 'wave',
                'name': 'Волна',
                'description': 'Волна цветов по трибунам'
            },
            {
                'id': 'flash',
                'name': 'Вспышки',
                'description': 'Синхронные вспышки'
            },
            {
                'id': 'gradient',
                'name': 'Градиент',
                'description': 'Плавный переход цветов'
            },
            {
                'id': 'pulse',
                'name': 'Пульсация',
                'description': 'Пульсирующий свет'
            },
            {
                'id': 'cascade',
                'name': 'Каскад',
                'description': 'Последовательное включение секторов'
            },
            {
                'id': 'text_scroll',
                'name': 'Бегущая строка',
                'description': 'Прокручивающийся текст'
            },
            {
                'id': 'fire',
                'name': 'Огонь',
                'description': 'Эффект пламени с мерцанием'
            },
            {
                'id': 'rainbow',
                'name': 'Радуга',
                'description': 'Переливающиеся цвета радуги'
            },
            {
                'id': 'stars',
                'name': 'Звезды',
                'description': 'Мерцающие звезды на небе'
            },
            {
                'id': 'heart',
                'name': 'Сердце',
                'description': 'Пульсирующее сердце'
            },
            {
                'id': 'score',
                'name': 'Счет',
                'description': 'Отображение счета матча'
            }
        ]
