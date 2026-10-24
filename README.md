# ЦСКА Performance Generator

> **EN:** A web service that turns images and light-show scenarios into "card stunt" choreographies for stadium stands. Every seat becomes a pixel (a fan's phone/flashlight), and the service maps pictures or procedural animations (wave, pulse, fire, rainbow, scrolling text...) onto the seat geometry of an arena, with a 3D "view from the pitch" preview. Python/FastAPI backend + React frontend. Unofficial fan/hackathon project.

> **Дисклеймер.** Проект не является официальным продуктом ПФК ЦСКА или ВЭБ Арены и не связан с ними. Названия, эмблемы и товарные знаки принадлежат их владельцам и упоминаются только для описания назначения. Файлы `cska_*` в библиотеке изображений — упрощённые программно нарисованные заглушки, а не официальная символика. Реальная схема мест арены в репозиторий не включена.

## О проекте

Подготовка трибунного перформанса (кричалки, «фанка», светошоу) вручную занимает дни: дизайнер адаптирует картинку под геометрию секторов. Идея проекта — считать каждое место трибуны пикселем и автоматически раскладывать изображение или анимацию по координатам мест, показывая результат в превью до выхода на стадион.

Проект родился как хакатонный прототип. Бизнес-обоснование и питч лежат в [`docs/`](docs/), но цифры экономии там — авторские оценки, а не измерения.

## Возможности

Всё ниже есть в коде v1.0.0:

- **Режим изображений**: библиотека готовых картинок, загрузка своих, масштаб, поворот, яркость, контраст, доля участвующих мест (`fill_rate`, имитация «битых пикселей»), выбор трибуны (A, C, K, S) или всей арены.
- **Режим сценариев фонариков** (REST API): волна, вспышки, градиент, пульсация, каскад по секторам, бегущий текст, огонь, радуга, звёзды, сердце, счёт, комбинирование сценариев; результат — набор PNG-кадров.
- **Маппинг на геометрию трибун**: цвет изображения берётся в координатах каждого места; превью рендерится в PNG.
- **3D-вид «с поля»** (React/canvas): камера в центре, вращение мышью, зум, подъём рядов, свечение активных мест, выбор сектора и статистика.
- **Демо на трёх телефонах** — наглядная иллюстрация принципа «телефон = пиксель».

Чего пока нет: генерации картинок по текстовому промпту (OpenAI/DALL-E упоминается в старых черновиках документации, но не реализован — см. [`docs/prompt-ideas.md`](docs/prompt-ideas.md)), использования сценариев фонариков во frontend.

## Архитектура

```
React (frontend, :3000) --/api--> FastAPI (backend, :8000)
                                   |- api/images.py       библиотека, загрузка, генерация из изображения
                                   |- api/flashlights.py  сценарии фонариков -> кадры
                                   |- api/preview.py      рендер превью, данные арены
                                   |- services/           ImageLibrary, ScenarioManager (11 сценариев)
                                   `- utils/              SeatsLoader (data/seats.json), ImageMapper
```

Подробнее: [`docs/technical.md`](docs/technical.md), [`docs/3d-visualization.md`](docs/3d-visualization.md).

## Стек

Python 3.9+ (проверено на 3.12), FastAPI, Uvicorn, Pillow, NumPy, Pydantic; React 18 (Create React App), axios.

## Быстрый старт

Нужны Python 3.9+ и Node.js 16+.

```bash
git clone https://github.com/cyxar4uk/cska-performance-generator.git
cd cska-performance-generator

# 1. Демо-схема мест (синтетическая; свою реальную положите в data/seats.json)
python scripts/generate_sample_seats.py

# 2. Backend
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # Windows: copy .env.example .env
python main.py                  # http://localhost:8000 , Swagger: /docs

# 3. Frontend (в другом терминале)
cd frontend
npm install
npm start                       # http://localhost:3000
```

Backend нужно запускать из каталога `backend/` (относительный путь к `assets/images`). Docker в проекте не предусмотрен.

## Конфигурация

| Переменная | Где | По умолчанию | Назначение |
|---|---|---|---|
| `PORT`, `HOST` | `backend/.env` | `8000`, `0.0.0.0` | адрес backend |
| `SEATS_FILE` | `backend/.env` | `data/seats.json` → `data/seats.sample.json` | файл со схемой мест |
| `BACKEND_URL` | окружение frontend | `http://127.0.0.1:8000` | куда проксировать `/api` в dev-режиме |

Формат `seats.json`: список секторов `{id, name, title, tribune, rows: {"<ряд>": [[seat_id, x, y, meta], ...]}}`; пример см. в `scripts/generate_sample_seats.py`.

## Тесты

```bash
pip install -r requirements-dev.txt
python -m pytest
```

Тесты используют синтетическую схему мест; CI (GitHub Actions) запускает их и сборку frontend.

## Структура

```
backend/    FastAPI-приложение (api/, services/, utils/, assets/images/)
frontend/   React-приложение (StadiumView, PhoneDemo, ImageUploader)
scripts/    generate_sample_seats.py
tests/      pytest
docs/       setup, technical, 3d-visualization, business-case, presentation, prompt-ideas
data/       схема мест (seats.json не публикуется)
```

## Лицензия

[MIT](LICENSE) © 2026 Ilia Melnikov. Лицензия распространяется на код; товарные знаки и название клуба/арены — собственность их владельцев.
