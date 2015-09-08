__author__ = 'omaestra'

from pdpostdata import settings

from django.forms.widgets import MultiWidget, HiddenInput
from django.contrib.admin.widgets import AdminFileWidget


class JCropWidget(AdminFileWidget):
    class Media:
        js = (settings.STATIC_URL + 'js/jquery.Jcrop.js',)
        css = {'all': (settings.STATIC_URL + 'css/jquery.Jcrop.css',)}

    def __init__(self, initial_crop_width=160, initial_crop_height=90, min_crop_width=None, min_crop_height=None,
                 max_crop_width=None, max_crop_height=None, min_image_width=None, min_image_height=None,
                 fix_aspect_ratio=False, attrs=None):

        # make sure the jcrop_file class is added to attrs
        if not attrs:
            attrs = {'class': 'jcrop_file'}
        elif attrs.has_key('class'):
            attrs['class'] += ' jcrop_file'

        # add some data attributes to the file input element to configure JCrop
        attrs['data-initial-crop-width'] = int(initial_crop_width)
        attrs['data-initial-crop-height'] = int(initial_crop_height)
        attrs['data-fix-aspect-ratio'] = int(fix_aspect_ratio)
        attrs['data-min-crop-width'] = min_crop_width if min_crop_width != None else 'null'
        attrs['data-min-crop-height'] = min_crop_height if min_crop_height != None else 'null'
        attrs['data-max-crop-width'] = max_crop_width if max_crop_width != None else 'null'
        attrs['data-max-crop-height'] = min_crop_width if min_crop_width != None else 'null'
        attrs['data-min-image-width'] = min_image_width if min_image_width != None else 'null'
        attrs['data-min-image-height'] = min_image_height if min_image_height != None else 'null'

        super(JCropWidget, self).__init__(attrs)

    def render(self, name, value, attrs):
        # used throughout JS code to consistently refer to target image element
        attrs['data-target-img-id'] = 'jcrop_img_' + name

        # if an image is already uploaded, add the url so that it can be displayed for cropping
        if value and hasattr(value, 'url'):
            attrs['data-existing-img-url'] = value.url

        return super(JCropWidget, self).render(name, value, attrs)


class CroppableImageWidget(MultiWidget):
    def __init__(self, file_widget=JCropWidget, coords_widget=HiddenInput, attrs=None):
        widgets = (
            file_widget,
            coords_widget
        )
        super(CroppableImageWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            croppable_image_file = value

            return [croppable_image_file, croppable_image_file.coords_csv]

        return [value, '']

    def render(self, name, value, attrs):
        attrs['data-coords-field-id'] = attrs['id'] + '_1'
        return super(CroppableImageWidget, self).render(name, value, attrs)


## -*- coding: utf-8 -*- ####################################################

from django.conf import settings
from django.forms.widgets import Widget, Media
from django.template.loader import render_to_string

from pdpostdata.settings import FILTER_CLASSES


class ImageEditWidget(Widget):
    def _get_media(self):
        media = Media(
            css={'all': ('image_editor/css/image_editor.css',)},
            js=('image_editor/js/image_editor.js', 'image_editor/js/jquery.json.js')
        )
        for n, f in FILTER_CLASSES.items():
            media = media + f.media
        return media

    media = property(_get_media)

    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        final_attrs = self.build_attrs(attrs, name=name)
        if value != '':
            # Only add the 'value' attribute if a value is non-empty.
            final_attrs['value'] = value
        buttons = {}
        initials = []
        for name, filter in FILTER_CLASSES.items():
            button = filter.render_button(attrs=final_attrs, filter_name=name)
            if button:
                buttons[name] = button
            initials.append(filter.render_initial(attrs=final_attrs, filter_name=name))
        final_attrs.update({
            'STATIC_URL': getattr(settings, 'STATIC_URL', settings.MEDIA_URL),
            'buttons': buttons,
            'initials': initials
        })
        return render_to_string('photos/wizard-upload.html', final_attrs)
