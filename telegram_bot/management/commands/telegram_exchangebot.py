from django.core.management import BaseCommand

from telegram_bot import exchangebot


class Command(BaseCommand):
    help = 'Run telegram exchangebot as a django command'

    def handle(self, *args, **options):
        exchangebot.main()
