"""Генерирует демонстрационную схему мест (data/seats.sample.json).

Формат совпадает с ожидаемым SeatsLoader: список секторов с полями
id, name, title, tribune и rows -> {номер ряда: [[seat_id, x, y, meta], ...]}.
Схема синтетическая и не повторяет реальную арену.
"""
import json
import os
import sys

TRIBUNES = {
    "A": (1000, 200, 1, 0),   # (x0, y0, dx_sign, dy_sign)
    "C": (1000, 2200, 1, 0),
    "K": (200, 700, 0, 1),
    "S": (2200, 700, 0, 1),
}


def build(sectors_per_tribune=3, rows=6, seats_per_row=12, step=40):
    sectors, seat_id, sector_id = [], 1, 1
    for tribune, (x0, y0, dx, dy) in TRIBUNES.items():
        for s in range(sectors_per_tribune):
            rows_dict = {}
            for r in range(1, rows + 1):
                row = []
                for i in range(seats_per_row):
                    along = s * (seats_per_row + 2) * step + i * step
                    across = r * step
                    if dx:
                        x, y = x0 + along, y0 + (across if tribune == "C" else -across) + 600
                    else:
                        x, y = x0 + (across if tribune == "S" else -across) + 600, y0 + along
                    row.append([seat_id, float(x), float(y), {}])
                    seat_id += 1
                rows_dict[str(r)] = row
            sectors.append({"id": sector_id, "name": f"{tribune}{s + 1}",
                            "title": f"Трибуна {tribune} Сектор {s + 1}",
                            "venueId": 0, "settings": None, "tribune": tribune,
                            "rows": rows_dict})
            sector_id += 1
    return sectors


if __name__ == "__main__":
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(root, "data", "seats.sample.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(build(), f, ensure_ascii=False)
    print(f"written {out}")
