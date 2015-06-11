from django import forms
from .models import Photo

from photos.fields import MultiFileField


class UploadForm(forms.Form):
    attachments = MultiFileField(min_num=1, max_num=3, max_file_size=1024*1024*5)


class PhotoForm(forms.Form):
    class Meta:
        model = Photo
        fields = "__all__"
