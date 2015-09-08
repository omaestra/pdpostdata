from django import forms

from orders.models import Order
from orders.models import STATUS_CHOICES


class OrderForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = ['status', ]

    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        self.fields['status'].widget.attrs['class'] = 'btn btn-default dropdown-toggle'
