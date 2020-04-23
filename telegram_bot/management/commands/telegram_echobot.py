from django.core.management import BaseCommand

from telegram_bot import echobot


class Command(BaseCommand):
    help = 'Run telegram echobot as a django command'

    def handle(self, *args, **options):
        echobot.main()
