# Чатик на вебсокитах на фреймворке aiohttp

### Стек
- aiohttp
- gino orm
- pytest
- sqlalchemy

### Развертывание
- Склонируйте репозиторий
- Применить миграции ``` alembic  upgrade head ```
- Запускаем приложение ```  gunicorn app:init_app  ```

