from django import forms

from accounts.models import EmailMarketingSignUp


class EmailForm(forms.Form):
    subscribe_email = forms.EmailField(max_length=200)

    def clean_subscribe_email(self):
        email = self.cleaned_data.get("subscribe_email")
        email_count = EmailMarketingSignUp.objects.filter(email=email).count()
        if email_count > 0:
            raise forms.ValidationError("Este correo electronico ya esta subscrito al boletin")

        return email
