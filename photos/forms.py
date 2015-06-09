from django import forms
from .models import Photo


class PhotoForm(forms.Form):
    class Meta:
        model = Photo
        fields = "__all__"