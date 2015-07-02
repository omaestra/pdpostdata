import uuid

import os
from django.db import models
from carts.models import CartItem


def make_uuid():
    random = str(uuid.uuid4())  # Convert UUID format to a Python string.
    random = random.replace("-", "")  # Remove the UUID '-'.
    return random


def get_image_path(instance, filename):
    """Returns a random string of length string_length."""
    # random =  str(uuid.uuid4()) # Convert UUID format to a Python string.
    # random = random.replace("-","") # Remove the UUID '-'.
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (str(instance.id), ext)
    return os.path.join('uploads', filename)


# Create your models here.
class Photo(models.Model):
    id = models.CharField(max_length=36, primary_key=True, default=make_uuid)
    temp_hash = models.CharField(max_length='255')
    # message = models.TextField(max_length='120')
    image_field = models.ImageField(upload_to=get_image_path)
    cart_item = models.ForeignKey(CartItem, null=True, blank=True)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)

    def __unicode__(self):
        return str(id)
