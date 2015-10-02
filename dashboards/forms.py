from django import forms

from orders.models import Order
from orders.models import STATUS_CHOICES

default_errors = {
    'required': 'Este campo es obligatorio!',
    'invalid': 'Por favor, ingresa un valor valido!',
    'min-length': '',
}


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status', ]

    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        self.fields['status'].widget.attrs['class'] = 'btn btn-default dropdown-toggle'


class AnswerHelpTicketForm(forms.Form):
    message = forms.CharField(error_messages=default_errors,
                              widget=forms.Textarea(
                                  attrs={
                                      'class': 'form-control', 'required': True, 'autofocus': True,
                                  }
                              ))
    help_ticket_id = forms.CharField(error_messages=default_errors,
                                     widget=forms.HiddenInput())

    def clean_message(self):
        message = self.cleaned_data.get("message")
        if len(message):
            return message
        else:
            raise forms.ValidationError("Oops! No puedes enviar un mensaje vacio!")
