from django import forms

from .models import Order, OrderRating

class OrderRatingForm(forms.ModelForm):
    class Meta:
        model = OrderRating
        fields = '__all__'
        error_messages = {
            'comment': {
                'required': "Por favor, ingresa un comentario",
            },
            'rate': {
                'required': "Por favor, ingresa una calificacion",
                'invalid_choice': "Por favor, ingresa una calificacion",
            }
        }
