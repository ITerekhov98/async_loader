## Архивация данных и отправка их по сети с помощью aiohttp 

### Установка и запуск

Скачайте репозиторий с кодом, установите необходимые зависимости:
```
pip install -r -requirements.txt
```

Запустите сервер командой:
```
python server.py
```

### Настройка

Вы можете легко изменить некоторые конфигурационные настройки:
- С помощью аргументов командной строки:
  + `--skip_logging` - Отключает подробное логгирование, выводиться будут только сообщения уровня WARNING и выше.
  + `response_delay` - Задержка между отправками частей архива, может быть полезна для отладки.
- С помощью переменных окружения:
  + `PHOTOS_DIR_PATH` - директория в которой скрипт будет искать фото для архивации и отправки. По умолчанию используется *test_photos* в каталоге приложения.
  + `OUTGOING_ARCHIVE_NAME` - названия архива, который будет отправлен пользователю. По умолчанию *test_photos.zip*. Обратите внимание что указывать имя файла необходимо с *.zip* расширением. 
