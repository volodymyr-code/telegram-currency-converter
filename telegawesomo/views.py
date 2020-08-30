import tempfile

import chartify
import pandas
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
    name = '{}/exchangerates_providers__{}.png'.format(tempfile.gettempdir(), result[-1]['date'])
    ch.save(name, format='png')
    with open(name, 'rb') as buffer:
        return HttpResponse(content_type='image/png', content=buffer.read())
