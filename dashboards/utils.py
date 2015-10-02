from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings


def activate_user_email(self):
    # send email here & render a string
    context = {
        "user": self.user.username,
    }
    message = render_to_string("accounts/activation_message.txt", context)
    subject = "Respuesta al Ticket de ayuda"
    self.email_user(subject, message, settings.DEFAULT_FROM_EMAIL)


def email_user(self, subject, message, from_email, **kwargs):
    send_mail(subject, message, from_email, [self.user.email], kwargs)
