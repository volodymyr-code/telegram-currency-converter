import datetime
import importlib
from abc import ABC, abstractmethod
from typing import Dict, List

from django.conf import settings
from django.core.cache import cache

from exchangerates_providers.helpers import find_currency
from exchangerates_providers.models import ExchangeRates

RatesDict = Dict[str, float]

HistoryList = List[Dict]

BASE_CURRENCY = 'USD'
CACHE_TIMEOUT = 60 * 10


class ExchangeRatesClient(ABC):

    @abstractmethod
    def history(self, date, base_currency: str = BASE_CURRENCY) -> RatesDict:
        pass

    @abstractmethod
    def execute(self, base_currency: str = BASE_CURRENCY) -> RatesDict:
        pass


class ExchangeRatesProvider:
    """
    Initializes exchange client

    Usage:

    >> from exchangerates_providers import ExchangeRatesProvider
    >> provider = ExchangeRatesProvider()
    >> result = provider.exchange(100, 'USD', 'UAH')
    """
    client: ExchangeRatesClient = None

    def __init__(self):
        module_name, class_name = settings.EXCHANGE_RATE_CLIENT.rsplit('.', 1)
        config = settings.EXCHANGE_RATE_CONFIG
        module = importlib.import_module(module_name)
        class_ = getattr(module, class_name)
        self.client = class_(*config)

    def rates(self, base_currency: str = BASE_CURRENCY) -> RatesDict:
        cache_key = '{}_get_rates_{}'.format(self.__class__.__name__, base_currency)
        rates_values: RatesDict = cache.get(cache_key)
        if not rates_values:
            rates_values = self.client.execute(base_currency)
            record = ExchangeRates(
                base_currency=base_currency,
            )
            record.rates = rates_values
            record.save()
            cache.set(cache_key, rates_values, CACHE_TIMEOUT)
        return rates_values

    def get_rate(self, from_currency: str, to_currency: str = BASE_CURRENCY) -> float:
        base_currency = find_currency(from_currency)
        target_currency = find_currency(to_currency)
        rates = self.rates()
        return rates[target_currency] / rates[base_currency]

    def exchange(self, amount: float, from_currency: str, to_currency: str = BASE_CURRENCY) -> float:
        rate = self.get_rate(from_currency, to_currency)
        return rate * amount

    def exchange_history(self, target_currency, base_currency: str = BASE_CURRENCY) -> HistoryList:
        today = datetime.date.today()
        dates = [
            '{}'.format(today - datetime.timedelta(days=day_num)) for day_num in range(7)
        ]
        dates.reverse()
        result = []
        for date in dates:
            cache_key = '{}_exchange_history_{}'.format(self.__class__.__name__, date)
            rates_values: RatesDict = cache.get(cache_key)
            if not rates_values:
                rates_values = self.client.history(date, base_currency)
                cache.set(cache_key, rates_values, CACHE_TIMEOUT)
            result.append({
                'date': date,
                'rate': rates_values[target_currency],
            })
        return result
