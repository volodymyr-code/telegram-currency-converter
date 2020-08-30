import logging

import requests

from exchangerates_providers.base import ExchangeRatesClient, BASE_CURRENCY

logger = logging.getLogger(__name__)


class OpenExchangeRatesClient(ExchangeRatesClient):
    API_KEY = None
    API_URL = None

    def __init__(self, *config):
        self.API_URL, self.API_KEY = config

    def history(self, date, base_currency=BASE_CURRENCY):
        url = '{}/historical/{}.json?app_id={}&base={}'.format(self.API_URL, date, self.API_KEY, base_currency)
        logger.debug(url)
        return requests.get(url).json()['rates']

    def execute(self, base_currency=BASE_CURRENCY):
        url = '{}latest.json?app_id={}&base={}'.format(self.API_URL, self.API_KEY, base_currency)
        logger.debug(url)
        return requests.get(url).json()['rates']
