# # -*- coding: utf-8 -*- ####################################################
from PIL import ImageOps

from django.conf import settings
from django.utils.translation import ugettext

from photos.filters.basic import ImageEditToolBasic


class ImageGrayscaleFilter(ImageEditToolBasic):

    def render_button(self, attrs, filter_name):
        return '<img src="%(static_url)s%(image_url)s" /><br/>%(filter_title)s\
                <span class="filter_auto_apply" filter_name="%(name)s" filter_params="{}"></span>' % \
        dict(
            static_url=settings.STATIC_URL or settings.MEDIA_URL,
            image_url='image_editor/img/grayscale.jpeg',
            name=filter_name,
            filter_title=ugettext('Grayscale')
        )

    def render_initial(self, attrs, filter_name):
        return ""

    def proceed_image(self, image, params):
        if image.mode != "L":
            image = image.convert("L")

        # optional: apply greyscale enhancement here, e.g.
        image = ImageOps.grayscale(image)

        # convert back to RGB so we can save it as JPEG
        # (alternatively, save it in PNG or similar)
        return image.convert("RGB")
