from django.core.exceptions import ValidationError

__author__ = 'oswaldomaestra'

from django.utils.translation import ugettext_lazy as _
from django import forms


class MultiFileInput(forms.FileInput):
    def render(self, name, value, attrs={}):
        attrs['multiple'] = 'multiple'
        attrs['class'] = 'dz-hidden-input'
        attrs['accept'] = 'image/*'
        return super(MultiFileInput, self).render(name, None, attrs=attrs)

    def value_from_datadict(self, data, files, name):
        if hasattr(files, 'getlist'):
            return files.getlist(name)
        else:
            return [files.get(name)]


class MultiFileField(forms.FileField):
    widget = MultiFileInput
    default_error_messages = {
        'min_num': u"Ensure at least %(min_num)s files are uploaded (received %(num_files)s).",
        'max_num': u"Ensure at most %(max_num)s files are uploaded (received %(num_files)s).",
        'file_size': u"File: %(uploaded_file_name)s, exceeded maximum upload size."
    }

    def __init__(self, *args, **kwargs):
        self.min_num = kwargs.pop('min_num', 0)
        self.max_num = kwargs.pop('max_num', None)
        self.maximum_file_size = kwargs.pop('maximum_file_size', None)
        super(MultiFileField, self).__init__(*args, **kwargs)

    def to_python(self, data):
        ret = []
        for item in data:
            ret.append(super(MultiFileField, self).to_python(item))
        return ret

    def validate(self, data):
        super(MultiFileField, self).validate(data)
        num_files = len(data)
        if len(data) and not data[0]:
            num_files = 0
        if num_files < self.min_num:
            raise ValidationError(self.error_messages['min_num'] % {'min_num': self.min_num, 'num_files': num_files})
            return
        elif self.max_num and num_files > self.max_num:
            raise ValidationError(self.error_messages['max_num'] % {'max_num': self.max_num, 'num_files': num_files})
        for uploaded_file in data:
            if uploaded_file.size > self.maximum_file_size:
                raise ValidationError(self.error_messages['file_size'] % {'uploaded_file_name': uploaded_file.name})


from django.core.exceptions import ValidationError
from django.forms.fields import Field
import json
from json import JSONDecoder
from django.utils.translation import ugettext


from photos.widgets import ImageEditWidget
from photos.utils import apply_filters_to_image


class ImageEditFormField(Field):
    widget = ImageEditWidget
    operations = []

    def __init__(self, *args, **kwargs):
        super(ImageEditFormField, self).__init__(*args, **kwargs)

    def apply_to_image(self, image_name):
        return apply_filters_to_image(image_name, self.operations)

    def clean(self, value):
        try:
            data = json.loads(value)
            self.operations = data.get('operations')
            value = self.apply_to_image(data.get('image'))
        except Exception:
            raise ValidationError(ugettext('Image edit data is not valid'))

        return super(ImageEditFormField, self).clean(value)
