import json
import os
from typing import Dict, List, Tuple, Optional

_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data")


def resolve_seats_file(explicit: Optional[str] = None) -> str:
    """Найти файл с местами: аргумент -> $SEATS_FILE -> data/seats.json -> data/seats.sample.json."""
    candidates = [explicit, os.getenv("SEATS_FILE"),
                  os.path.join(_DATA_DIR, "seats.json"),
                  os.path.join(_DATA_DIR, "seats.sample.json")]
    for path in candidates:
        if path and os.path.exists(path):
            return path
    return os.path.join(_DATA_DIR, "seats.json")


class SeatsLoader:
    def __init__(self, seats_file: Optional[str] = None):
        self.seats_file = resolve_seats_file(seats_file)
        self.sectors = []
        self.all_seats = []
        self.bounds = {"min_x": float('inf'), "max_x": 0, "min_y": float('inf'), "max_y": 0}

    def load(self):
        """Загрузить данные о местах из JSON"""
        if not os.path.exists(self.seats_file):
            raise FileNotFoundError(f"Файл {self.seats_file} не найден")

        with open(self.seats_file, 'r', encoding='utf-8') as f:
            self.sectors = json.load(f)

        self._process_seats()
        return self

    def _process_seats(self):
        """Обработать все места и найти границы координат"""
        for sector in self.sectors:
            tribune = sector.get('tribune', 'unknown')
            sector_name = sector.get('name', '')

            for row_num, seats in sector.get('rows', {}).items():
                for seat in seats:
                    seat_id, x, y = seat[0], seat[1], seat[2]
                    meta = seat[3] if len(seat) > 3 else {}

                    self.all_seats.append({
                        'id': seat_id,
                        'x': x,
                        'y': y,
                        'tribune': tribune,
                        'sector': sector_name,
                        'row': int(row_num),
                        'meta': meta
                    })

                    # Обновить границы
                    self.bounds['min_x'] = min(self.bounds['min_x'], x)
                    self.bounds['max_x'] = max(self.bounds['max_x'], x)
                    self.bounds['min_y'] = min(self.bounds['min_y'], y)
                    self.bounds['max_y'] = max(self.bounds['max_y'], y)

    def get_seats_by_tribune(self, tribune: str) -> List[Dict]:
        """Получить все места конкретной трибуны"""
        return [s for s in self.all_seats if s['tribune'] == tribune]

    def get_all_tribunes(self) -> List[str]:
        """Получить список всех трибун"""
        return list(set(s['tribune'] for s in self.all_seats if s['tribune']))

    def get_arena_dimensions(self) -> Tuple[int, int]:
        """Получить размеры арены в пикселях"""
        width = int(self.bounds['max_x'] - self.bounds['min_x'])
        height = int(self.bounds['max_y'] - self.bounds['min_y'])
        return width, height

    def get_stats(self) -> Dict:
        """Получить статистику по местам"""
        tribunes = {}
        for seat in self.all_seats:
            t = seat['tribune']
            if t not in tribunes:
                tribunes[t] = 0
            tribunes[t] += 1

        return {
            'total_seats': len(self.all_seats),
            'tribunes': tribunes,
            'dimensions': self.get_arena_dimensions(),
            'bounds': self.bounds
        }
