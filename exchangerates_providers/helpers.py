import re
from typing import Tuple


class ExchangeException(BaseException): pass


CURRENCY_ALIASES = {
    'CAD': ['CA$', 'CA', 'CAN'],
    'USD': ['$', 'US'],
    'UAH': ['₴', 'UA', 'ГРН'],
}


def find_currency(value):
    try:
        return list(dict(filter(lambda c: value.upper() in c[1], CURRENCY_ALIASES.items())).keys())[0]
    except IndexError:
        return value.upper()


def parse_request(convert_text: str) -> Tuple[float, str, str]:
    """
    :param convert_text:
    > 100 USD to UAH
    > $100 to UAH
    :return:
    """
    match_amount = re.search('\d+([.,]?\d+)?', convert_text)
    try:
        amount = float(match_amount.group().replace(',', '.'))
    except AttributeError:
        raise ExchangeException('Bad amount')

    match_codes = re.findall('[A-Za-z]{3}', convert_text)
    match_symbols = re.findall('[^\s\w\d,.]+', convert_text)

    if len(match_codes) == 2:
        base_currency, target_currency = match_codes
    elif len(match_symbols) == 2:
        base_currency, target_currency = match_symbols
    elif len(match_symbols) == 1 and len(match_codes) == 1:
        # @todo check symbol position
        base_currency, target_currency = match_symbols[0], match_codes[0]
    else:
        raise ExchangeException('Bad format')

    return amount, find_currency(base_currency), find_currency(target_currency)
