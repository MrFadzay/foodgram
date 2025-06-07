# Foodgram

Foodgram - это веб-приложение для создания и публикации рецептов, а также для формирования списка покупок на основе выбранных рецептов.

## Рабочий сайт

[https://fadzay.zapto.org/](https://fadzay.zapto.org/)

## Автор

*   **ФИО:** Болог Ян
*   **GitHub:** [https://github.com/MrFadzay](https://github.com/MrFadzay)

## Технологический стек

*   **Backend:** Python, Django, PostgreSQL, Redis, Sentry
*   **Frontend:** React
*   **Инфраструктура:** Nginx, Docker, Docker Compose
*   **CI/CD:** GitHub Actions

## CI/CD для развертывания

Настроен автоматический деплой с использованием CI/CD через GitHub Actions.

## Локальное развертывание с Docker

Для локального развертывания проекта с использованием Docker выполните следующие шаги:

1.  **Клонирование репозитория:**
    ```bash
    git clone https://github.com/MrFadzay/foodgram.git
    ```

2.  **Переход в папку проекта:**
    ```bash
    cd foodgram
    ```

3.  **Создание файла `.env`:**
    Создайте файл `.env` в корневой директории проекта, используя `backend/.env.example` в качестве примера. Замените значения на свои.

    Пример `.env`:
    ```
    DEBUG=1
    DJANGO_SECRET_KEY=your-secret-key-here
    ALLOWED_HOSTS=127.0.0.1,localhost
    DJANGO_MEDIA_ROOT=/app/media

    DB_ENGINE=django.db.backends.postgresql
    POSTGRES_DB=foodgram
    POSTGRES_USER=foodgram_user
    POSTGRES_PASSWORD=foodgram_password
    DB_HOST=db
    DB_PORT=5432

    REDIS_HOST=redis
    REDIS_PORT=6379
    REDIS_URL=redis://redis:6379/1

    SENTRY_DSN="ВАШ_DSN_ИЗ_SENTRY"
    ```

4.  **Подъем контейнеров:**
    Запустите Docker Compose из корневой директории проекта.
    ```bash
    sudo docker-compose up -d --build
    # или docker-compose up -d --build (в зависимости от настроек Docker)
    ```
    Контейнер `frontend` подготовит файлы, необходимые для работы фронтенд-приложения, а затем прекратит свою работу.

5.  **Подготовка базы данных:**
    Выполните миграции, создайте суперпользователя и импортируйте фикстуры (ингредиенты).
    ```bash
    sudo docker-compose exec backend python manage.py migrate
    sudo docker-compose exec backend python manage.py createsuperuser
    sudo docker-compose exec backend python manage.py import_ingredients
    ```

6.  **Сборка статики:**
    ```bash
    sudo docker-compose exec backend python manage.py collectstatic --noinput
    ```

7.  **Запуск сервера:**
    После выполнения предыдущих шагов, контейнеры уже запущены. Если вы остановили их, вы можете запустить их снова:
    ```bash
    sudo docker-compose up -d
    ```

8.  **Доступ к приложению:**
    *   Фронтенд веб-приложения: [http://localhost/](http://localhost/)
    *   Спецификация API: [http://localhost/api/docs/](http://localhost/api/docs/)

## Локальное развертывание без Docker

Для локального развертывания проекта без использования Docker (только для бэкенда) выполните следующие шаги:

1.  **Клонирование репозитория:**
    ```bash
    git clone https://github.com/MrFadzay/foodgram.git
    ```

2.  **Переход в папку бэкенда:**
    ```bash
    cd foodgram/backend
    ```

3.  **Настройка виртуального окружения:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Для Linux/macOS
    # venv\Scripts\activate  # Для Windows
    pip install -r requirements.txt
    ```

4.  **Создание файла `.env`:**
    Создайте файл `.env` в директории `backend/foodgram/`, используя `backend/.env.example` в качестве примера. Убедитесь, что `DB_HOST` и `REDIS_HOST` указывают на `localhost` или на вашу локальную базу данных/Redis.

    Пример `.env` (для локального развертывания без Docker):
    ```
    DEBUG=1
    DJANGO_SECRET_KEY=your-secret-key-here
    ALLOWED_HOSTS=127.0.0.1,localhost
    DJANGO_MEDIA_ROOT=/app/media

    DB_ENGINE=django.db.backends.postgresql
    POSTGRES_DB=foodgram
    POSTGRES_USER=foodgram_user
    POSTGRES_PASSWORD=foodgram_password
    DB_HOST=localhost # Изменено для локального развертывания
    DB_PORT=5432

    REDIS_HOST=localhost # Изменено для локального развертывания
    REDIS_PORT=6379
    REDIS_URL=redis://localhost:6379/1

    SENTRY_DSN="ВАШ_DSN_ИЗ_SENTRY"
    ```

5.  **Миграция базы данных и создание суперпользователя:**
    ```bash
    python manage.py migrate
    python manage.py createsuperuser
    ```

6.  **Импорт продуктов из JSON фикстур:**
    ```bash
    python manage.py import_ingredients
    ```

7.  **Запуск сервера:**
    ```bash
    python manage.py runserver
    ```

8.  **Ссылка для получения полной технической документации к API:**
    *   [http://127.0.0.1:8000/api/docs/](http://127.0.0.1:8000/api/docs/)
