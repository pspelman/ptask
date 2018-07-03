import datetime

from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from models import *

User = get_user_model()

class QuantityResponseForm(forms.ModelForm):
    quantity = forms.IntegerField(label='Drinks')
    class Meta:
        model = QuantityResponseModel
        fields = ['quantity']

    def clean_quantity(self, *args, **kwargs):
        quantity = self.cleaned_data.get('quantity')

        if quantity < 0:
            # raise forms.ValidationError("You may not enter negative numbers")
            raise forms.ValidationError("You may not enter negative numbers")
        if quantity > 100:
            raise forms.ValidationError("100-drink limit. Please enter fewer drinks.")
            # raise forms.ValidationError("100-drink limit. Please enter fewer drinks.")
        return quantity

    def __init__(self, *args, **kwargs):
        super(QuantityResponseForm, self).__init__(*args, **kwargs)
        self.fields['quantity'].widget.attrs= {'autofocus':'autofocus', 'size':'3'}
        # self.fields['quantity'].widget.attrs['autofocus'] = u'autofocus'


