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
    provider = ExchangeRatesProvider()
    result = provider.exchange_history(request.GET.get('target', 'CAD'))

    chart_data = pandas.DataFrame(data={
        'dates': (line['date'] for line in result),
        'rates': (line['rate'] for line in result),
    })

    from matplotlib import pyplot
    import numpy
    from io import StringIO

    y = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]
    x = numpy.arange(10)
    fig = pyplot.figure()
    ax = pyplot.subplot(111)
    ax.plot(x, y, label='$y = numbers')
    pyplot.title('Legend inside')
    ax.legend()

    buffer = StringIO()
    fig.savefig(buffer, format='png')

    return HttpResponse(content_type='image/png', content=buffer.read())
