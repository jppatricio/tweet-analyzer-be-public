from django.db import models

class TweetLabelerRequestModel(models.Model):
    tweet = models.CharField(max_length=120, blank=False, default='')
    password = models.CharField(max_length=20, blank=False, default='')
