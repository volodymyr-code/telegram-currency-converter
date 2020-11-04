from django.http import HttpResponse, HttpResponseRedirect

from exchangerates_providers.base import ExchangeRatesProvider
from exchangerates_providers.helpers import parse_request


def exchange(request):
    provider = ExchangeRatesProvider()

    if 'q' in request.GET:
        result = provider.exchange(*parse_request(request.GET.get('q')))
    elif 'amount' not in request.GET:
        return HttpResponseRedirect('?amount=100&base=USD&target=UAH')
    else:
        result = provider.exchange(
            float(request.GET.get('amount', 100)),
            request.GET.get('base', 'USD'),
            request.GET.get('target', 'UAH')
        )
    return HttpResponse(result)


def exchange_history(request):
    currency = request.GET.get('target', 'UAH')
    provider = ExchangeRatesProvider()
    result = provider.exchange_history(currency)
    return HttpResponse(result)
