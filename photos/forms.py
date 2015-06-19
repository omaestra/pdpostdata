import uuid

from django import forms
from .models import Photo

from photos.fields import MultiFileField


class UploadForm(forms.Form):
    photos = MultiFileField(max_num=10, min_num=1, maximum_file_size=1024*1024*5)


class PhotoForm(forms.ModelForm):
    # photos = MultiFileField(max_num=10, min_num=1, maximum_file_size=1024*1024*5)

    class Meta:
        model = Photo
        fields = ['temp_hash', ]

    def __init__(self, *args, **kwargs):
        super(PhotoForm, self).__init__(*args, **kwargs)
        self.fields['temp_hash'] = forms.CharField(max_length='255', widget=forms.HiddenInput())
        self.fields['temp_hash'].initial = uuid.uuid1()

