from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.db import models


# Create your models here.
# from django.contrib.auth.models import AbstractUser, User

class PriceList(models.Model):
    prices = models.FloatField(null=True)


class QuantityResponseModel(models.Model):
    quantity = models.IntegerField(blank=False)
    text_quantity = models.CharField(max_length=255)


