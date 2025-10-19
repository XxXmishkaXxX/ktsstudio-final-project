# KTS Studio Final Project

**Автор:** Куцов Михаил Владимирович  
**Email:** misha.kutsov1@gmail.com  
**Telegram:** [@MK_for_you](https://t.me/MK_for_you)

## Описание

Это финальный проект KTS Studio, бот-игра 100 к 1.  

Проект включает:  

- Бота-игру по мотивам "100 к 1"  
- API на Python  
- Webhook для внешних сервисов  
- CI/CD через GitHub Actions  
- Контейнеризацию с Docker  

Цель проекта — демонстрация навыков разработки полнофункционального приложения с современными инструментами и архитектурой.  

---

## Структура проекта
```
.ktsstudio-final-project/
│
├─ api/ # Основной backend
├─ bot/ # Логика бота (игра "100 к 1")
├─ webhook/ # Обработка входящих вебхуков
├─ db_core/ # ядро бд, модели, аксессоры
├─ rmq_core/ ядро RabbitMQ
├─ nginx/ # конфигурация nginx
├─ .github/workflows/ # CI/CD
├─ docker-compose.yaml # Конфигурация Docker
├─ doker-compose-prod.yaml # Конфигурация Docker для прода
├─ pyproject.toml # Зависимости и настройки Python
└─ README.md # Этот файл
```

## Установка и запуск

### 1. Клонирование репозитория

```bash
git clone https://github.com/XxXmishkaXxX/ktsstudio-final-project.git
cd ktsstudio-final-project
```
### 2. Настройка конфигураций

Перед запуском Docker необходимо заполнить все файлы конфигурации .yml своими значениями (например, токены бота, ключи API и другие настройки).

```
webhook/config.yml
bot/config.yml
api/config.yml
```
Рекомендую использовать tuna для локального тестирования.
```bash
tuna http 8080
```

### 3. Запуск через Docker (рекомендуется)
```bash
docker-compose up --build
```

## Технологии и зависимости

В этом проекте используются следующие инструменты и библиотеки:

- **Python 3.11+** – основной язык проекта  
- **aiohttp** – асинхронный веб-фреймворк для API и вебхуков  
- **Redis** – кэширование и хранение временных данных (например, состояние игры)
- **rabbitmq** - очередь для передачи данных между сервисами 
- **PostgreSQL** – основная база данных для хранения информации о пользователях и результатах игр  
- **Docker & Docker Compose** – контейнеризация всех сервисов для удобного запуска  
- **pytest** – для тестирования кода  
- **GitHub Actions** – CI/CD: автоматическая проверка тестов и сборка Docker-образов  

## Команды Telegram бота (игра "100 к 1")

Бот поддерживает следующие команды:

| Команда       | Описание |
|---------------|----------|
| `/start`      | Запустить бота и получить приветственное сообщение |
| `/play`       | Начать игру "100 к 1" |
| `/stop_game`  | Остановить текущую игру |
| `/ans` | Ответить во время игры | 


## API

Проект предоставляет REST API для работы с вопросами игры. Все эндпоинты асинхронные и реализованы с использованием **aiohttp + aiohttp-apispec**. Перед тем как работать с вопросами, нужно залогиниться, как админ.

### Эндпоинты
| Метод  | URL           | Описание |
|--------|---------------|----------|
| `POST` | `/admin.login` | Логин администратора. Принимает JSON с полями `email` и `password` (`AdminSchema`). Возвращает данные админа и создаёт сессию. |
| `GET`  | `/admin.current` | Получить данные текущего администратора (только для залогиненных админов). |
| `POST` | `/questions`       | Создать новый вопрос. Принимает JSON с полями вопроса (`QuestionSchema`). |
| `GET`  | `/questions/?page=1&limit=10` | Получить список вопросов с пагинацией. Возвращает объект с `page`, `limit`, `total` и `items`. |
| `DELETE` | `/questions`     | Удалить вопрос по `id`. Принимает JSON с полем `id` (`QuestionDeleteSchema`). |

### Логин администратора:

```bash
curl -X POST http://localhost:8082/admin.login \
-H "Content-Type: application/json" \
-d '{
  "email": "admin@example.com",
  "password": "your_password"
}'
```
### Создание вопроса:
```bash
curl -X POST http://localhost:8082/questions \
-H "Content-Type: application/json" \
-d '{
  "text": "Пример вопроса",
  "answers": [
    {"text": "Ответ 1", "points": 10, "position": 1},
    {"text": "Ответ 2", "points": 5, "position": 2},
    {"text": "Ответ 3", "points": 3, "position": 3},
    {"text": "Ответ 4", "points": 1, "position": 4},
    {"text": "Ответ 5", "points": 0, "position": 5}
  ]
}'
```
### Удаление вопроса:
```bash
curl -X DELETE http://localhost:8082/questions/ \
-H "Content-Type: application/json" \
-d '{"id": 1}'
```

### Получение вопросов (GET):
```bash
curl http://localhost:8082/questions/?page=1&limit=10
```

## Благодарности

- [KTS Studio](https://ktsstudio.ru/) — курс и поддержка




