#!/usr/bin/env python
import logging
import os
import tempfile

import chartify
import pandas
from django.conf import settings
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Enable logging
from exchangerates_providers.base import ExchangeRatesProvider
from exchangerates_providers.helpers import parse_request, ExchangeException
from telegram_bot.models import MessageLog

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text(""
                              "usage: 100 USD to UAH\n"
                              "usage: 100$ to UAH\n"
                              "usage: 100UAH to USD\n"
                              "usage: /list\n"
                              "usage: /history\n"
                              "")


def rates(update, context):
    """Send a message when the command /list /lst is issued."""
    provider = ExchangeRatesProvider()
    update.message.reply_text('\n'.join(
        ['{}: {:.2f}'.format(k, v) for k, v in provider.rates().items()]
    ))


def history(update, context):
    """Show png image with 7 day history /history is issued."""
    update.message.reply_text('Generating chart. Please wait...')

    currency = 'CAD'
    provider = ExchangeRatesProvider()
    result = provider.exchange_history(currency)

    name = '{}/exchangerates_providers__{}.png'.format(tempfile.gettempdir(), result[-1]['date'])
    if not os.path.exists(name):
        chart_data = pandas.DataFrame(data={
            'dates': (line['date'] for line in result),
            'rates': (line['rate'] for line in result),
        })
        ch = chartify.Chart(blank_labels=True, x_axis_type='datetime')
        ch.set_title('Date {} - {} currency {}'.format(result[0]['date'], result[-1]['date'], currency))
        ch.plot.line(
            data_frame=chart_data,
            x_column='dates',
            y_column='rates',
        )
        # @todo find better way to generate png
        ch.save(name, format='png')
    context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(name, 'rb'))


def exchange(update, context):
    """Convert message to value"""
    message = update.message.text
    provider = ExchangeRatesProvider()
    message_log = MessageLog.objects.create(payload=update.to_json())
    try:
        amount, base, target = parse_request(message)
        result = '{}: {:.2f}'.format(target, provider.exchange(amount, base, target))
        update.message.reply_text('{}: {:.2f}'.format(base, provider.get_rate(base, target)), quote=False)
        update.message.reply_text(result, quote=False)
        message_log.bot_answer = result
    except ExchangeException:
        update.message.reply_text('Bad format!', quote=True)
        message_log.bot_answer = 'bad format'
        help(update, context)
    message_log.save()


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(settings.TELEGRAM_TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler('help', help))
    dp.add_handler(CommandHandler('start', help))
    dp.add_handler(CommandHandler(('list', 'lst'), rates))
    dp.add_handler(CommandHandler('history', history))
    dp.add_handler(CommandHandler('exchange', exchange, filters=Filters.text))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, exchange))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
