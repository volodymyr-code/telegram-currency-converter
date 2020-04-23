# Telegram bot demo

Telegram bot integrated into Django project

1. Install requirements
`pip install -r requirements.txt`
2. Copy `.env` from `.env.example` and fill with data below:
3. Django `SECRET_KEY` can be generated with command:
`python manage.py shell -c 'from django.core.management import utils; print(utils.get_random_secret_key())'`
4. Create telegram access token `TELEGRAM_TOKEN` https://core.telegram.org/bots#6-botfather
5. Run echobot with command `python manage.py telegram_echobot`