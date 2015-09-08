# # -*- coding: utf-8 -*- ####################################################
from PIL import Image

from django.conf import settings
from django.utils.translation import ugettext

from photos.filters.basic import ImageEditToolBasic

# CROP_RATIO


class ImageCropTool(ImageEditToolBasic):

    class Media:
        def __init__(self):
            pass

        js = ('jcrop/js/jquery.Jcrop.min.js', 'jcrop/js/cropper.js')
        css = { 'all': ('jcrop/css/jquery.Jcrop.css', ) }

    def render_button(self, attrs, filter_name):
        return """
               <img src="%(static_url)s%(image_url)s" style="margin: 6px;" /><br/>%(filter_title)s \
               <script>
                   $(function(){
                       $("#%(id)s_button_crop").cropper(
                           "%(id)s",
                           %(options)s
                       );
                   });
               </script>
               """ % \
                {
                    'static_url': settings.STATIC_URL or settings.MEDIA_URL,
                    'image_url': 'image_editor/img/crop.png',
                    'id': attrs['id'],
                    'filter_title': ugettext('Crop'),
                    'options': self.options
                }

    def render_initial(self, attrs, filter_name):
        return ""

    def proceed_image(self, image, params):
        image_width, image_height = image.size
        x = int(round(params['x'], 0))
        y = int(round(params['y'], 0))
        width = int(round(params['width'], 0))
        height = int(round(params['height'], 0))
        rotate = -int(round(params['rotate'], 0))
        values = (x, y, x + width, y + height)

        if width and height and (width != image.size[0] or height != image.size[1]):
            image = image.rotate(rotate, resample=Image.BICUBIC, expand=True).crop(values).resize((width, height), Image.ANTIALIAS)
        else:
            raise Exception
        # x_coef = float(image_width) / float(params['width'])
        # y_coef = float(image_height) / float(params['height'])
        # image = image.crop((
        #     int(params['x'] * x_coef), int(params['y'] * y_coef), int(params['width'] * x_coef), int(params['height'] * y_coef)))
        return image
