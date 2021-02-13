# Account Service
Account Management Service

Сервис работы с аккаунтами пользователей (регистрация, сброс пароля, подтверждение аккаунта и т.д.)

Может использоваться в качестве стартового шаблона для старта проекта.

Эндпоинты работы с аккаунтом покрыты тестами.

## Установка
```bash
python3 -m venv env
. env/bin/activate
pip install -r requirements.txt
# Перед миграцией подключить свою базу данных в settings/settings.py
python manage.py migrate
```

## Важно
При использовании на production сервере поменять SECRET_KEY и переместить в переменные окружения

## Документация api
Документацию эндпоинтов можно посмотреть в docs/swagger.yaml

## Настройка email сервера
Настройки email сервера находятся в settings/settings.py
```
EMAIL_HOST = ''
EMAIL_PORT = 2525
EMAIL_HOST_USER = ""
EMAIL_HOST_PASSWORD = ""
```

## Возможности сервиса
* Регистрация пользователя по email
* Аутентификация
* Смена пароля
* Смена email
* Подтверждение email
* Получение информации о пользователе
* Просмотр статистики по регистрациям

## Формат токена в заголовках 
```
Authorization: Token 30e7e3f452a772ecd0de17e9c080aad485e927c3
```