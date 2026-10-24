# Техническая документация

> **Примечание (v1.0.0).** В документе описана целевая концепция проекта. Генерация изображений через OpenAI/DALL-E в коде v1.0.0 **не реализована**: сейчас работают режим готовых изображений (библиотека + загрузка) и режим сценариев фонариков. Цифры экономии времени и денег — оценки авторов, а не измерения.


## Архитектура системы

### Общая схема

```
┌─────────────────────────────────────────────────────────────┐
│                        User Interface                        │
│                     (React Frontend)                         │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/REST
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      API Gateway                             │
│                     (FastAPI)                                │
├─────────────────────────────────────────────────────────────┤
│  /api/generate/image     │  /api/animation/animation        │
│  /api/generate/tribunes  │  /api/preview/render             │
│  /api/preview/arena-info │                                   │
└────────────┬────────────┴──────────────┬────────────────────┘
             │                           │
             ▼                           ▼
┌─────────────────────┐      ┌─────────────────────┐
│  Image Generator    │      │ Animation Generator │
│  (OpenAI DALL-E 3)  │      │  (PIL + NumPy)      │
└──────────┬──────────┘      └──────────┬──────────┘
           │                            │
           └────────────┬───────────────┘
                        ▼
           ┌─────────────────────────┐
           │     Image Mapper        │
           │  (Seats Coordinates)    │
           └────────────┬────────────┘
                        │
                        ▼
           ┌─────────────────────────┐
           │    Preview Generator    │
           │   (29,071 pixels)       │
           └─────────────────────────┘
```

## Компоненты системы

### 1. Frontend (React)

**Файлы:**
- `src/App.js` - главный компонент
- `src/App.css` - стили
- `src/index.js` - точка входа

**Функционал:**
- Форма ввода промпта
- Выбор трибуны
- Настройка параметров
- Отображение превью
- Статистика генерации

**API взаимодействие:**
```javascript
// Генерация изображения
POST /api/generate/image
{
  prompt: string,
  tribune: string | null,
  fill_rate: number,
  optimize_prompt: boolean
}

// Генерация анимации
POST /api/animation/animation
{
  prompt: string,
  effect: "wave" | "flash" | "pulse",
  frames: number,
  fill_rate: number
}
```

### 2. Backend (FastAPI)

#### 2.1 API Endpoints

**Generate API** (`api/generate.py`)
- `POST /api/generate/image` - генерация изображения
- `GET /api/generate/tribunes` - список трибун

**Preview API** (`api/preview.py`)
- `POST /api/preview/render` - рендер превью
- `GET /api/preview/arena-info` - информация об арене

**Animation API** (`api/animation.py`)
- `POST /api/animation/animation` - генерация анимации

#### 2.2 Services

**ImageGenerator** (`services/image_generator.py`)
```python
class ImageGenerator:
    def generate_image(prompt: str, size: str) -> Image
    def generate_pixel_art(prompt: str) -> Image
    def optimize_for_stadium(prompt: str) -> str
```

**AnimationGenerator** (`services/animation_generator.py`)
```python
class AnimationGenerator:
    @staticmethod
    def create_wave_effect(image, frames) -> List[Image]
    @staticmethod
    def create_flash_effect(image, frames) -> List[Image]
    @staticmethod
    def create_pulse_effect(image, frames) -> List[Image]
    @staticmethod
    def save_as_gif(frames, output_path)
```

#### 2.3 Utils

**SeatsLoader** (`utils/seats_loader.py`)
```python
class SeatsLoader:
    def load() -> self
    def get_seats_by_tribune(tribune: str) -> List[Dict]
    def get_all_tribunes() -> List[str]
    def get_arena_dimensions() -> Tuple[int, int]
    def get_stats() -> Dict
```

**ImageMapper** (`utils/image_mapper.py`)
```python
class ImageMapper:
    def map_image_to_seats(image, fill_rate) -> Dict[int, Tuple[int, int, int]]
    def create_preview_image(seat_colors) -> Image
    def generate_animation_frames(images) -> List[Dict]
```

## Алгоритмы

### 1. Маппинг изображения на места

```python
def map_image_to_seats(image, seats, fill_rate):
    # 1. Ресайз изображения под размеры арены
    img_resized = image.resize((arena_width, arena_height))
    
    # 2. Конвертация в numpy array
    img_array = np.array(img_resized)
    
    # 3. Выбор участвующих мест (симуляция "битых пикселей")
    participating = random.choice(seats, size=int(len(seats) * fill_rate))
    
    # 4. Для каждого места получить цвет из изображения
    for seat in participating:
        x, y = seat['x'], seat['y']
        color = img_array[y, x]  # RGB
        seat_colors[seat['id']] = color
    
    return seat_colors
```

### 2. Генерация волнового эффекта

```python
def create_wave_effect(image, frames, wave_speed):
    result = []
    for frame_idx in range(frames):
        frame = Image.new('RGB', image.size)
        
        for y in range(height):
            # Вычислить смещение волны
            offset = sin((y/height + frame_idx*wave_speed) * 2π) * 20
            
            # Копировать строку с смещением
            for x in range(width):
                src_x = (x + offset) % width
                frame[x, y] = image[src_x, y]
        
        result.append(frame)
    
    return result
```

### 3. Оптимизация промпта для стадиона

```python
def optimize_for_stadium(prompt):
    return f"""
    Create a bold, high-contrast image suitable for stadium display.
    The image should be visible from far away with clear shapes and vibrant colors.
    Style: simple, iconic, graphic design.
    Content: {prompt}
    """
```

## Структура данных

### seats.json

```json
[
  {
    "id": 216658,
    "name": "207",
    "title": "Трибуна C Сектор 207",
    "venueId": 1,
    "tribune": "C",
    "rows": {
      "1": [
        [216660, 6586.5, 4999.45, {"preferential": true}],
        [216668, 6736.5, 4999.45, {"preferential": true}]
      ]
    }
  }
]
```

**Формат места:** `[id, x, y, meta]`
- `id` - уникальный идентификатор
- `x, y` - координаты в пикселях (0-10495, 0-8086)
- `meta` - метаданные (preferential, vip, etc.)

### API Response

**GenerateResponse:**
```json
{
  "success": true,
  "preview_image": "base64_encoded_png",
  "seat_colors": {
    "216660": [255, 0, 0],
    "216668": [0, 0, 255]
  },
  "stats": {
    "total_seats": 29071,
    "active_seats": 23256,
    "fill_rate": 0.8
  }
}
```

## Производительность

### Время выполнения

| Операция | Время | Оптимизация |
|----------|-------|-------------|
| AI генерация | 30-60 сек | Кэширование, предзагрузка |
| Ресайз изображения | 0.1-0.5 сек | PIL оптимизирован |
| Маппинг на места | 1-2 сек | NumPy векторизация |
| Создание превью | 0.5-1 сек | Batch processing |
| **Итого** | **32-64 сек** | **< 2 мин** |

### Оптимизации

1. **Кэширование AI результатов** - сохранение сгенерированных изображений
2. **Lazy loading** - загрузка seats.json только при первом запросе
3. **Векторизация** - использование NumPy для быстрых операций
4. **Async/await** - асинхронная обработка запросов

## Масштабирование

### Горизонтальное

```
Load Balancer
    │
    ├─── Backend Instance 1
    ├─── Backend Instance 2
    └─── Backend Instance 3
         │
         └─── Shared Cache (Redis)
```

### Вертикальное

- Увеличение CPU для AI генерации
- Больше RAM для обработки изображений
- GPU для ускорения NumPy операций

## Безопасность

### API

1. **Rate limiting** - ограничение запросов
2. **API keys** - аутентификация
3. **CORS** - контроль доступа
4. **Input validation** - проверка входных данных

### Данные

1. **Env variables** - секреты в .env
2. **HTTPS** - шифрование трафика
3. **Sanitization** - очистка промптов

## Мониторинг

### Метрики

```python
# Prometheus metrics
generation_time = Histogram('generation_time_seconds')
api_requests = Counter('api_requests_total')
errors = Counter('errors_total')
active_seats = Gauge('active_seats_count')
```

### Логирование

```python
import logging

logger.info(f"Generated image for prompt: {prompt}")
logger.error(f"Failed to generate: {error}")
logger.warning(f"Low fill rate: {fill_rate}")
```

## Тестирование

### Unit тесты

```python
def test_seats_loader():
    loader = SeatsLoader("test_seats.json")
    loader.load()
    assert len(loader.all_seats) > 0

def test_image_mapper():
    mapper = ImageMapper(seats, 1000, 800)
    colors = mapper.map_image_to_seats(test_image, 0.8)
    assert len(colors) > 0
```

### Integration тесты

```python
def test_generate_endpoint():
    response = client.post("/api/generate/image", json={
        "prompt": "test",
        "fill_rate": 0.8
    })
    assert response.status_code == 200
    assert "preview_image" in response.json()
```

## Развертывание

### Docker

```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

### Docker Compose

```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
```

## Зависимости

### Backend

```
fastapi==0.115.0        # Web framework
uvicorn==0.32.0         # ASGI server
pillow==10.4.0          # Image processing
numpy==2.1.3            # Math operations
openai==1.54.3          # AI generation
python-dotenv==1.0.1    # Environment variables
pydantic==2.9.2         # Data validation
```

### Frontend

```
react==18.2.0           # UI framework
react-dom==18.2.0       # React DOM
axios==1.6.0            # HTTP client
react-scripts==5.0.1    # Build tools
```

## Troubleshooting

### Проблема: Медленная генерация

**Решение:**
- Использовать кэширование
- Предзагружать популярные промпты
- Уменьшить размер изображения

### Проблема: Низкое качество

**Решение:**
- Улучшить промпт
- Использовать quality="hd" в DALL-E
- Постобработка изображения

### Проблема: Высокая стоимость API

**Решение:**
- Кэшировать результаты
- Использовать более дешевые модели для тестов
- Batch processing

## Roadmap технических улучшений

### v1.1
- [ ] Кэширование AI результатов
- [ ] WebSocket для real-time превью
- [ ] Batch API для множественной генерации

### v1.2
- [ ] GPU ускорение
- [ ] Distributed processing
- [ ] Advanced animations (3D effects)

### v2.0
- [ ] Machine learning для оптимизации промптов
- [ ] Custom AI model (fine-tuned)
- [ ] Real-time collaboration
