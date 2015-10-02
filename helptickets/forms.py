# coding=utf-8
from django import forms
from helptickets.models import HelpTicket


class HelpTicketForm(forms.ModelForm):
    class Meta:
        model = HelpTicket
        fields = [
            'subject', 'message',
        ]
        labels = {
            'subject': 'Asunto', 'message': 'Mensaje',
        }
        help_texts = {
            'message': 'Envíanos alguna duda o comentario  y pronto te responderemos a tu correo electrónico.'
        }
        error_messages = {
            'subject': {
                'max_length': "El asunto es muy largo!",
                'required': "Este campo es obligatorio.",
            },
            'message': {
                'max_length': "Tu mensaje es muy largo!",
                'required': "Este campo es obligatorio.",
            },
        }
        widgets = {
            'subject': forms.TextInput(attrs={'placeholder': 'Asunto'}),
            'message': forms.Textarea(attrs={'placeholder': 'Mensaje'}),
        }

    def __init__(self, *args, **kwargs):
        super(HelpTicketForm, self).__init__(*args, **kwargs)
        self.fields['subject'].widget.attrs['class'] = 'form-control'
        self.fields['message'].widget.attrs['class'] = 'form-control'
