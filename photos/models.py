import uuid

import os
from django.db import models
from carts.models import CartItem

nearest_int = lambda a: int(round(a))
to_retina_path = lambda p: '%s@2x%s' % os.path.splitext(p)


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


class SizeSet(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=50, null=False, unique=True)

    def __unicode__(self):
        return u"%s" % self.name

    def get_size_by_ratio(self):
        """ Shorthand to get all the unique ratios for display in the admin,
        rather than show every possible thumbnail
        """

        size_query = Size.objects.filter(size_set__id=self.id)
        size_query.query.group_by = ["aspect_ratio"]
        try:
            return size_query
        except ValueError:
            return None


class Size(models.Model):
    # An Size not associated with a set is a 'one off'
    size_set = models.ForeignKey(SizeSet, null=True)

    date_modified = models.DateTimeField(auto_now=True, null=True)

    name = models.CharField(max_length=255, db_index=True)

    slug = models.SlugField(max_length=50, null=False)

    height = models.PositiveIntegerField(null=True, blank=True)

    width = models.PositiveIntegerField(null=True, blank=True)

    aspect_ratio = models.FloatField(null=True, blank=True)

    auto_crop = models.BooleanField(default=False)

    retina = models.BooleanField(default=False)

    def get_height(self):
        """
        Return calculated height, if possible.
        @return: Height
        @rtype: positive int
        """
        if self.height is None and self.width and self.aspect_ratio:
            return nearest_int(self.width / self.aspect_ratio)

        return self.height

    def get_width(self):
        """
        Returns calculate width, if possible.
        @return: Width
        @rtype: positive int
        """
        if self.width is None and self.height and self.aspect_ratio:
            return nearest_int(self.height * self.aspect_ratio)

        return self.width

    def get_aspect_ratio(self):
        """
        Returns calculated aspect ratio, if possible.
        @return: Aspect Ratio
        @rtype:  float
        """
        if self.aspect_ratio is None and self.height and self.width:
            return round(self.width / float(self.height), 2)

        return self.aspect_ratio

    def get_dimensions(self):
        """
        Returns all calculated dimensions for the size.
        @return: width, height, aspect ratio
        @rtype: (int > 0, int > 0, float > 0)
        """
        return (self.get_width(), self.get_height(), self.get_aspect_ratio())

    def calc_dimensions(self, width, height):
        """
        From a given set of dimensions, calculates the rendered size.
        @param width: Starting width
        @type  width: Positive int
        @param height: Starting height
        @type  height: Positive int
        @return: rendered width, rendered height
        @rtype: (Width, Height)
        """
        w, h, a = self.get_dimensions()
        # Explicit dimension give explicit answers
        if w and h:
            return w, h, a

        # Empty sizes are basically useless.
        if not (w or h):
            return width, height, None

        aspect_ratio = round(width / float(height), 2)
        if w:
            h = nearest_int(w / aspect_ratio)
        else:
            w = nearest_int(h * aspect_ratio)

        return w, h, round(w / float(h), 2)

    def __unicode__(self):
        return u"%s: %sx%s" % (self.name, self.width, self.height)

    def save(self, *args, **kwargs):
        if self.slug is None:
            self.slug = uuid.uuid4().hex
        w, h, a = self.get_dimensions()
        self.width = w
        self.height = h
        self.aspect_ratio = a
        super(Size, self).save(*args, **kwargs)


# Create your models here.
class Photo(models.Model):
    id = models.CharField(max_length=36, primary_key=True, default=make_uuid)
    temp_hash = models.CharField(max_length='255')
    message = models.TextField(max_length='120', blank=True)
    image = models.ImageField(upload_to=get_image_path)
    # image_height = models.PositiveIntegerField()
    # image_width = models.PositiveIntegerField()
    image_cropped = models.ImageField(upload_to=get_image_path)
    # image_cropped_height = models.PositiveIntegerField()
    # image_cropped_width = models.PositiveIntegerField()
    # caption = models.CharField(max_length=250, blank=True)
    cart_item = models.ForeignKey(CartItem, null=True, blank=True)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)

    def __unicode__(self):
        return str(id)


class Crop(models.Model):
    crop_x = models.PositiveIntegerField(default=0, blank=True, null=True)
    crop_y = models.PositiveIntegerField(default=0, blank=True, null=True)
    crop_w = models.PositiveIntegerField(default=0, blank=True, null=True)
    crop_h = models.PositiveIntegerField(default=0, blank=True, null=True)

    def __unicode__(self):
        return u"Crop: (%i, %i),(%i, %i) " % (
            self.crop_x,
            self.crop_y,
            self.crop_x + self.crop_w,
            self.crop_y + self.crop_h,
        )
