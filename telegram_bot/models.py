import json

from django.db import models


class MessageLog(models.Model):
    payload = models.JSONField()
    bot_answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        message = json.loads(self.payload)['message']
        return '{} {}: {}'.format(
            self.created_at,
            message['chat']['username'],
            message['text']
        )

    class Meta:
        ordering = ('-created_at',)
