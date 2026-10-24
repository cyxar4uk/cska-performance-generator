# Инструкция по запуску ЦСКА Performance Generator

## Требования

- Python 3.9+
- Node.js 16+

## Установка

### 1. Backend

```bash
cd backend

# Создать виртуальное окружение
python -m venv venv

# Активировать (Windows)
venv\Scripts\activate

# Установить зависимости
pip install -r requirements.txt

# Создать .env файл
cp .env.example .env   # Windows: copy .env.example .env

# При необходимости отредактировать PORT / HOST / SEATS_FILE (OpenAI-ключ в v1.0.0 не используется)
```

### 2. Frontend

```bash
cd frontend

# Установить зависимости
npm install
```

### 3. Данные трибун

Скачайте файл `seats.json` с координатами мест и поместите его в папку `data/`:

```
cska-performance-generator/
└── data/
    └── seats.json
```

## Запуск

### Запуск Backend

```bash
cd backend
python main.py
```

Backend будет доступен на `http://localhost:8000`

API документация: `http://localhost:8000/docs`

### Запуск Frontend

```bash
cd frontend
npm start
```

Frontend будет доступен на `http://localhost:3000`

## Использование

1. Откройте `http://localhost:3000` в браузере
2. Введите описание перформанса (например: "логотип ЦСКА с красно-синими цветами")
3. Выберите трибуну (опционально)
4. Настройте процент заполнения мест
5. Нажмите "Сгенерировать"
6. Дождитесь результата и посмотрите превью

## API Endpoints

### Генерация изображения
```
POST /api/generate/image
{
  "prompt": "логотип ЦСКА",
  "tribune": "A",
  "fill_rate": 0.8,
  "optimize_prompt": true
}
```

### Генерация анимации
```
POST /api/animation/animation
{
  "prompt": "российский флаг",
  "effect": "wave",
  "frames": 10,
  "fill_rate": 0.8
}
```

### Получить список трибун
```
GET /api/generate/tribunes
```

### Информация об арене
```
GET /api/preview/arena-info
```

## Эффекты анимации

- `wave` - волновой эффект
- `flash` - вспышки
- `pulse` - пульсация

## Troubleshooting

### Ошибка "OpenAI API key не найден"
Убедитесь, что в файле `backend/.env` указан корректный API ключ OpenAI.

### Ошибка "seats.json не найден"
Проверьте, что файл `seats.json` находится в папке `data/`.

### Frontend не подключается к Backend
Убедитесь, что Backend запущен на порту 8000 и доступен.


## Данные о местах

Файл `data/seats.json` (реальная схема арены) в репозиторий не входит. Для запуска без него сгенерируйте демонстрационную схему:

```bash
python scripts/generate_sample_seats.py   # создаст data/seats.sample.json
```

Бэкенд автоматически использует `SEATS_FILE`, затем `data/seats.json`, затем `data/seats.sample.json`.
