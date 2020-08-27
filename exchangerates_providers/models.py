import json
import re

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


def validate_currency(value):
    if not re.match('^[A-Z]{3}$', value):
        raise ValidationError(_('%(value)s is invalid currency code'), params={'value': value})


class ExchangeRates(models.Model):
    base_currency = models.CharField(max_length=3, validators=[validate_currency])
    json_rates = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def rates(self):
        return json.loads(self.json_rates)

    @rates.setter
    def rates(self, value):
        self.json_rates = json.dumps(value)

    def __str__(self):
        return '{} {}'.format(self.base_currency, self.created_at)
