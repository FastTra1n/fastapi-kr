## Локальный запуск приложения (без Docker)

1. Создайте виртуальное окружение

```sh
python -m venv .venv
```

2. Активируйте окружение

Windows:

```sh
.venv\Scripts\activate
```

Linux / Mac:

```sh
source .venv/bin/activate
```

3. Установите все необходимые зависимости

```sh
pip install -r requirements.txt
```

4. Запустите сервер с горячей перезагрузкой

```sh
uvicorn app.app:app --reload
```

5. Запустите тесты (при необходимости)

```sh
pytest
```

## Запуск приложения через Docker Compose

1. Соберите и запустите контейнер

```sh
docker compose up --build
```

2. Проверьте работу API

```sh
curl http://localhost:8000/health
```
