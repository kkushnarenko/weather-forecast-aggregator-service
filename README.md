# Weather Forecast Aggregator Service

Сервис для агрегации и отслеживания прогноза погоды по городам пользователей. Проект построен на базе **FastAPI**, **SQLAlchemy** и **SQLite**.


## Запуск проекта

Скрипт запускает ASGI-сервер Uvicorn с приложением FastAPI:

```bash
python3 script.py
```

После запуска интерактивная документация Swagger UI будет доступна по адресу: http://127.0.0.1:8000/

## Установка и настройка
### 1. Клонируйте репозиторий и перейдите в папку проекта:
```bash
git clone <URL_ВАШЕГО_РЕПОЗИТОРИЯ>
cd weather-forecast-aggregator-service
```
### 2. Создайте и активируйте виртуальное окружение:
```bash
python3 -m venv .venv
source .venv/bin/activate  # Для Linux / macOS
# .venv\Scripts\activate   # Для Windows
```

### 3. Установите зависимости:
```bash
pip install -r requirements.txt
```
### 4. Запуск автотестов (Pytest):
```bash
pytest
```

## Описание API методов
Базовый URL всех эндпоинтов: `/weather`

### 1. Пользователи

#### `POST /weather/users/register`
Регистрация нового пользователя.

* **Параметры (Query):**
  * `username` (*string*, обязательный) — Имя пользователя.
* **Успешный ответ (`201 Created`):**
  ```json
  {
    "id": 1,
    "username": "alice"
  }
  ```
* **Ошибки:**
* `400 Bad Request` — Пользователь с таким именем уже существует.

### 2. Города
#### `POST /weather/cities`
Добавить город для отслеживания погоды.
* **Параметры (Query):**
* `name` (string, обязательный) — Название города.
* `latitude` (float, обязательный) — Широта.
* `longitude` (float, обязательный) — Долгота.
* `user_id` (integer, обязательный) — ID пользователя.
* **Успешный ответ `201 Created`**
  ```json
  {
  "id": 1,
  "name": "Moscow",
  "latitude": 55.75,
  "longitude": 37.61,
  "user_id": 1
  }
  ```

#### `GET /weather/cities`
Получить список всех городов конкретного пользователя.

* **Параметры (Query):**
* `user_id` (integer, обязательный) — ID пользователя.
*  ** Успешный ответ (`200 OK`):**
  ``` json
  [
  {
    "id": 1,
    "name": "Moscow",
    "latitude": 55.75,
    "longitude": 37.61,
    "user_id": 1
  }
]
```

### 3. Прогноз погоды
#### `GET /weather/`
Получить текущую погоду по широте и долготе.

* **Параметры (Query)**
* `latitude` (float, обязательный) — Широта (`-90..90`).
* `longitude` (float, обязательный) — Долгота (`-180..180`).
*  **Успешный ответ (`200 OK`):**
  ``` json
{
  "temperature": 18.5,
  "wind_speed": 4.2
}
```

#### `GET /weather/city-weather`
Получить сохраненный прогноз погоды для города на указанное время.
* **Параметры (Query)**
* `city_name` (string, обязательный) — Название города.
* `target_time` (string, обязательный) — Время в ISO формате (например, `2026-08-03T15:00:00`).
*  `user_id` (integer, обязательный) — ID пользователя.
*  `include_temperature` (bool, опционально, по умолчанию `true`) — Включать температуру.
*  `include_humidity` (bool, опционально, по умолчанию `true`) — Включать влажность.
*  `include_wind_speed` (bool, опционально, по умолчанию `true`) — Включать скорость ветра.
*  `include_precipitation` (bool, опционально, по умолчанию `true`) — Включать осадки.
* **Успешный ответ(`200 OK`):**
```json
{
  "city_name": "Moscow",
  "timestamp": "2026-08-03T15:00:00",
  "temperature": 21.0,
  "humidity": 55.0,
  "wind_speed": 3.1,
  "precipitation": 0.0
}
```
* **Ошибки:
* `400 Bad Request` — Неверный формат даты.
* `404 Not Found` — Город не найден у пользователя.



  

