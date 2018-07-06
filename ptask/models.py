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


class PurchaseTaskModel(models.Model):
    pass
    # TODO: add a model for how one purchase task instance should be stored
    # researcher_email?
    # participant ID?
    # timestamp?
    # prices
    # quantities (responses)
    # totals
    # raw_intensity
    # raw_omax
    # raw_pmax
    # raw_breakpoint
    #

