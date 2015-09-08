# # -*- coding: utf-8 -*- ####################################################
import tempfile
from PIL import Image
from StringIO import StringIO

from django.core.files import File
from django.core.files.images import ImageFile
from django.core.files.storage import default_storage as storage  # TODO: allow set storage via settings


from pdpostdata.settings import FILTER_CLASSES
from photos.filters.basic import ImageEditToolBasic


def apply_filters_to_image(image_name, operations):

    if not storage.exists(image_name):
        raise Exception('Image "%s" does not exist' % image_name)

    file = storage.open(image_name)
    file.seek(0)
    image = Image.open(StringIO(file.read()))

    if type(operations) != list:
        raise Exception('Wrong params received')

    for operation in operations:
        filter = FILTER_CLASSES.get(operation['name'], None)
        if not isinstance(filter, ImageEditToolBasic):
            raise Exception('Image filter with name "%s" is not found' % operation['name'])
        image = filter.proceed_image(image, operation.get('params', None))

    tmp = tempfile.NamedTemporaryFile()
    image.save(tmp.name, 'JPEG')
    tmp.seek(0, 0)

    return ImageFile(tmp)
