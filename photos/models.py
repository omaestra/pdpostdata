import StringIO
import uuid
from imagekit.models import ImageSpecField
import os
from os.path import sep
from PIL import Image, ImageFilter
from django.core.exceptions import ValidationError

from django.utils.translation import ugettext_lazy as _

from django.db import models
from pilkit.processors import SmartResize, ResizeToFill, TrimBorderColor, Resize, ResizeToFit, Transpose
from carts.models import CartItem
from photos.storage import OverwriteStorage

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


# class SizeSet(models.Model):
#     name = models.CharField(max_length=255, db_index=True)
#     slug = models.SlugField(max_length=50, null=False, unique=True)
#
#     def __unicode__(self):
#         return u"%s" % self.name
#
#     def get_size_by_ratio(self):
#         """ Shorthand to get all the unique ratios for display in the admin,
#         rather than show every possible thumbnail
#         """
#
#         size_query = Size.objects.filter(size_set__id=self.id)
#         size_query.query.group_by = ["aspect_ratio"]
#         try:
#             return size_query
#         except ValueError:
#             return None
#
#
# class Size(models.Model):
#     # An Size not associated with a set is a 'one off'
#     size_set = models.ForeignKey(SizeSet, null=True)
#
#     date_modified = models.DateTimeField(auto_now=True, null=True)
#
#     name = models.CharField(max_length=255, db_index=True)
#
#     slug = models.SlugField(max_length=50, null=False)
#
#     height = models.PositiveIntegerField(null=True, blank=True)
#
#     width = models.PositiveIntegerField(null=True, blank=True)
#
#     aspect_ratio = models.FloatField(null=True, blank=True)
#
#     auto_crop = models.BooleanField(default=False)
#
#     retina = models.BooleanField(default=False)
#
#     def get_height(self):
#         """
#         Return calculated height, if possible.
#         @return: Height
#         @rtype: positive int
#         """
#         if self.height is None and self.width and self.aspect_ratio:
#             return nearest_int(self.width / self.aspect_ratio)
#
#         return self.height
#
#     def get_width(self):
#         """
#         Returns calculate width, if possible.
#         @return: Width
#         @rtype: positive int
#         """
#         if self.width is None and self.height and self.aspect_ratio:
#             return nearest_int(self.height * self.aspect_ratio)
#
#         return self.width
#
#     def get_aspect_ratio(self):
#         """
#         Returns calculated aspect ratio, if possible.
#         @return: Aspect Ratio
#         @rtype:  float
#         """
#         if self.aspect_ratio is None and self.height and self.width:
#             return round(self.width / float(self.height), 2)
#
#         return self.aspect_ratio
#
#     def get_dimensions(self):
#         """
#         Returns all calculated dimensions for the size.
#         @return: width, height, aspect ratio
#         @rtype: (int > 0, int > 0, float > 0)
#         """
#         return (self.get_width(), self.get_height(), self.get_aspect_ratio())
#
#     def calc_dimensions(self, width, height):
#         """
#         From a given set of dimensions, calculates the rendered size.
#         @param width: Starting width
#         @type  width: Positive int
#         @param height: Starting height
#         @type  height: Positive int
#         @return: rendered width, rendered height
#         @rtype: (Width, Height)
#         """
#         w, h, a = self.get_dimensions()
#         # Explicit dimension give explicit answers
#         if w and h:
#             return w, h, a
#
#         # Empty sizes are basically useless.
#         if not (w or h):
#             return width, height, None
#
#         aspect_ratio = round(width / float(height), 2)
#         if w:
#             h = nearest_int(w / aspect_ratio)
#         else:
#             w = nearest_int(h * aspect_ratio)
#
#         return w, h, round(w / float(h), 2)
#
#     def __unicode__(self):
#         return u"%s: %sx%s" % (self.name, self.width, self.height)
#
#     def save(self, *args, **kwargs):
#         if self.slug is None:
#             self.slug = uuid.uuid4().hex
#         w, h, a = self.get_dimensions()
#         self.width = w
#         self.height = h
#         self.aspect_ratio = a
#         super(Size, self).save(*args, **kwargs)


# Create your models here.
class Photo(models.Model):
    id = models.CharField(max_length=36, primary_key=True, default=make_uuid)
    temp_hash = models.CharField(max_length='255')
    message = models.TextField(max_length='120', blank=True)
    image = models.ImageField(upload_to=get_image_path, storage=OverwriteStorage())
    smart = ImageSpecField(
        source='image', processors=[Transpose(), ResizeToFit(768, 768)], format='JPEG', options={'quality': 80})
    thumbnail = ImageSpecField(
        source='image', processors=[Transpose(), ResizeToFill(120, 120)], format='JPEG',
        options={'quality': 80})
    sequence = models.PositiveSmallIntegerField(default=0, null=True, blank=True)
    cart_item = models.ForeignKey(CartItem, null=True, blank=True)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)

    def __unicode__(self):
        return str(id)

    def get_name(self, prefix=None):
        """Strips the name of a file into (pathname, extension)"""
        # Get the filename from the original image field, i.e: "image.jpg"
        filename = self.image.path.split(sep)[-1]
        # Get the extension of the original image
        ext = filename.split('.')[-1]

        return "%s%s.%s" % (prefix, str(self.id), ext)

    def crop_photo(self, crop_box=None):
        try:
            img = Image.open(self.image.path, mode='r')

            x = crop_box['x']
            y = crop_box['y']
            width = crop_box['width']
            height = crop_box['height']

            values = (x, y, x + width, y + height)

            if width and height and (width != img.size[0] or height != img.size[1]):
                cropped_image = img.crop(values).resize((width, height), Image.ANTIALIAS)
            else:
                raise

            # Get the filename from the original image field, i.e: "image.jpg"
            filename = self.get_name("crop_")
            tempfile_io = StringIO.StringIO()
            cropped_image.save(tempfile_io, format='JPEG', overwrite=True)
            # from django.core.files.uploadedfile import InMemoryUploadedFile
            from django.core.files.images import ImageFile

            image_file = ImageFile(tempfile_io, filename)
            # image_file = InMemoryUploadedFile(tempfile_io, None, 'crop.jpg', 'image/jpeg', tempfile_io.len, None)

            return image_file
        except IOError:
            raise ValidationError("Error, no se pudo abrir el archivo de imagen")


class Cropped(models.Model):
    """
    Cropped segment of original image
    """
    original = models.OneToOneField(Photo, related_name='cropped', verbose_name=_('Original image'),
                                    on_delete=models.CASCADE)
    image_cropped = models.ImageField(_('Image'), upload_to='uploads/', editable=False)
    smart = ImageSpecField(
        source='image_cropped', processors=[Transpose(), ResizeToFit(600, 600)], format='JPEG', options={'quality': 80})
    thumbnail = ImageSpecField(
        source='image_cropped', processors=[Transpose(), ResizeToFill(120, 120)], format='JPEG',
        options={'quality': 80})
    x = models.PositiveIntegerField(_('offset X'), default=0)
    y = models.PositiveIntegerField(_('offset Y'), default=0)
    w = models.PositiveIntegerField(_('cropped area width'), blank=True, null=True)
    h = models.PositiveIntegerField(_('cropped area height'), blank=True, null=True)

    def __str__(self):
        return u'%s-%sx%s' % (self.original, self.w, self.h)

    def __unicode__(self):
        return u"Crop: (%i, %i),(%i, %i) " % (
            self.crop_x,
            self.crop_y,
            self.crop_x + self.crop_w,
            self.crop_y + self.crop_h,
        )

    def save(self, *args, **kwargs):
        # delete old file when replacing by updating the file
        try:
            this = Cropped.objects.get(id=self.id)
            if this.image_cropped != self.image_cropped:
                this.image_cropped.delete(save=False)
        except Cropped.DoesNotExist:
            pass  # when new photo then we do nothing, normal case
        except Exception as e:
            raise e
        super(Cropped, self).save(*args, **kwargs)

# import cImage as image
# from math import sqrt
# from os.path import splitext
#
#
# class ImageFilter(object):
#     def __init__(self, img_file, draw=1):
#         """Initialize image, clone it, get its size and create a canvas"""
#         self.img_file = img_file
#         self.oldimg = image.Image(self.img_file)
#         self.width = self.oldimg.getWidth()
#         self.height = self.oldimg.getHeight()
#         self.newimg = self.oldimg.copy()
#         # Decides whether to skip drawing the image in a popup window.
#         self.draw = draw
#         if self.draw:
#             self.win = image.ImageWin(self.img_file, self.width, self.height)
#
#     def write(self, func_name="_", draw=1):
#         """Draw and save a processed image"""
#         # Get file's root and extension from method strip_name().
#         img_name, img_ext = self.strip_name()
#         self.newimg.save(img_name + func_name + img_ext)
#         # Again, only execute this if we want to have a popup of the window.
#         if self.draw:
#             self.newimg.draw(self.win)
#             self.win.exitonclick()
#
#     def strip_name(self):
#         """Strips the name of a file into (pathname, extension)"""
#         return splitext(self.img_file)
#
#     def invert(self):
#         """Invert the colors of the image"""
#         for x in range(self.width):
#             for y in range(self.height):
#                 # For each pixel p, get the RGB values and invert them.
#                 p = self.newimg.getPixel(x, y)
#                 p.red = 255 - p.red
#                 p.green = 255 - p.green
#                 p.blue = 255 - p.blue
#                 # Write the modified pixel into our cloned window.
#                 self.newimg.setPixel(x, y, p)
#         # Call the method that draws, writes and decides the filename.
#         self.write("_inv")
#
#     def greyscale(self):
#         """Convert image to greyscale"""
#         for x in range(self.width):
#             for y in range(self.height):
#                 # For each pixel p get the RBG values and average them out.
#                 p = self.newimg.getPixel(x, y)
#                 avg = (p[0] + p[1] + p[2]) / 3
#                 p.red = p.green = p.blue = avg
#                 self.newimg.setPixel(x, y, p)
#         self.write("_grey")
#
#     def blackwhite(self):
#         """Convert image to black and white"""
#         for x in range(self.width):
#             for y in range(self.height):
#                 # Any pixel with an average r+g+b of >= 128 gets converted to
#                 # white (255), all others to black (0).
#                 p = self.newimg.getPixel(x, y)
#                 avg = (p[0] + p[1] + p[2]) / 3
#                 if avg >= 128:
#                     avg = 255
#                 else:
#                     avg = 0
#                 p.red = p.green = p.blue = avg
#                 self.newimg.setPixel(x, y, p)
#         self.write("_bw")
#
#     def removecolor(self, color="R"):
#         """Remove either (R)ed, (G)reen, (B)lue or a combination of those"""
#         # TODO: Add options for different colors.
#         for x in range(self.width):
#             for y in range(self.height):
#                 p = self.newimg.getPixel(x, y)
#                 p.red = 0
#                 self.newimg.setPixel(x, y, p)
#         self.write("_rc")
#
#     def sepia(self):
#         """Apply Sepia Toning to the image"""
#         for x in range(self.width):
#             for y in range(self.height):
#                 try:
#                     # Apply the Sepia filter to each value r, g, b of pixel p.
#                     p = self.newimg.getPixel(x, y)
#                     p.red = int(p.red * 0.393 + p.green * 0.769 + p.blue * 0.189)
#                     p.green = int(p.red * 0.349 + p.green * 0.686 + p.blue * 0.168)
#                     p.blue = int(p.red * 0.272 + p.green * 0.534 + p.blue * 0.131)
#                     self.newimg.setPixel(x, y, p)
#                 except:
#                     continue
#         self.write("_sepia")
#
#     def double(self, draw=0):
#         """Double the size of the image"""
#         # The canvas size gets annoyingly big so by default we avoid drawing here.
#         self.draw = draw
#         # We overwrite self.newimg because we need double the canvas size.
#         self.newimg = image.EmptyImage(self.width * 2, self.height * 2)
#         # In case we do decide to draw, self.win needs double canvas, too.
#         if self.draw:
#             self.win = image.ImageWin(self.img_file, self.width * 2, self.height * 2)
#
#         for y in range(self.height):
#             for x in range(self.width):
#                 p = self.oldimg.getPixel(x, y)
#                 self.newimg.setPixel(2 * x, 2 * y, p)
#                 self.newimg.setPixel(2 * x + 1, 2 * y, p)
#                 self.newimg.setPixel(2 * x, 2 * y + 1, p)
#                 self.newimg.setPixel(2 * x + 1, 2 * y + 1, p)
#         self.write("_double", 0)
#
#     def average(self):
#         """Average
#         Apply average of surrounding 8 pixels to the current pixel.
#         This should probably be updated to use Gaussian instead."""
#
#         for y in range(self.height):
#             for x in range(self.width):
#                 # Initialize both pixel p and the list to store neighbor pixels in.
#                 p = self.newimg.getPixel(x, y)
#                 neighbors = []
#                 # Nested for loop to check 9 pixels total: p plus it's 8 neighbors.
#                 # Use list comprehension here? Also get rid of try statements.
#                 for xx in range(x - 1, x + 2):
#                     for yy in range(y - 1, y + 2):
#                         try:
#                             neighbor = self.newimg.getPixel(xx, yy)
#                             neighbors.append(neighbor)
#                         except:
#                             continue
#                 nlen = len(neighbors)
#                 # Average out the RBG values
#                 if nlen:
#                     # Uncommented, the following line would leave most of the white
#                     # untouched which works a little better for real photographs, imo.
#                     # ~ if nlen and p[0]+p[1]+p[2] < 690:
#                     # Get the average of each r, g, b for all pixels in neighbors.
#                     p.red = sum([neighbors[i][0] for i in range(nlen)]) / nlen
#                     p.green = sum([neighbors[i][1] for i in range(nlen)]) / nlen
#                     p.blue = sum([neighbors[i][2] for i in range(nlen)]) / nlen
#                     self.newimg.setPixel(x, y, p)
#         self.write("_avg")
#
#     def median(self):
#         """Median
#         Apply median of surrounding 8 pixels to current pixel
#         This usually gives better results than average()"""
#
#         for y in range(self.height):
#             for x in range(self.width):
#                 # Initialize both pixel p and the list to store neighbor pixels in.
#                 p = self.newimg.getPixel(x, y)
#                 neighbors = []
#                 # Nested for loop to check 9 pixels total: p plus it's 8 neighbors.
#                 # Use list comprehension here? Also get rid of try statements.
#                 for xx in range(x - 1, x + 2):
#                     for yy in range(y - 1, y + 2):
#                         try:
#                             neighbor = self.newimg.getPixel(xx, yy)
#                             neighbors.append(neighbor)
#                         except:
#                             continue
#                 nlen = len(neighbors)
#                 # Making sure the list of pixels is not empty
#                 if nlen:
#                     red = [neighbors[i][0] for i in range(nlen)]
#                     green = [neighbors[i][1] for i in range(nlen)]
#                     blue = [neighbors[i][2] for i in range(nlen)]
#                     # Sort the lists so we can later find the median.
#                     for i in [red, green, blue]:
#                         i.sort()
#                     # If the list has an odd number of items in it, the median is easy.
#                     if nlen % 2:
#                         p.red = red[len(red) / 2]
#                         p.green = green[len(green) / 2]
#                         p.blue = blue[len(blue) / 2]
#                     # The median calculation if the list length is even:
#                     else:
#                         p.red = (red[len(red) / 2] + red[len(red) / 2 - 1]) / 2
#                         p.green = (green[len(green) / 2] + green[len(green) / 2 - 1]) / 2
#                         p.blue = (blue[len(blue) / 2] + blue[len(blue) / 2 - 1]) / 2
#                     self.newimg.setPixel(x, y, p)
#         self.write("_median")
#
#     def sobel(self, draw=0):
#         """Using the Sobel Algorithm to apply Edge Detection to an image."""
#         self.draw = draw
#         # Overwriting self.newimg because we need an empty canvas. Otherwise
#         # the existing pixels would influence the newly written ones.
#         self.newimg = image.EmptyImage(self.width, self.height)
#         if self.draw:
#             self.win = image.ImageWin(self.img_file, self.width * 2, self.height * 2)
#
#         # Abandon all hope, ye who enter here. Terrible nested logic incoming.
#         for x in range(1, self.width - 1):
#             for y in range(1, self.height - 1):
#                 # Apply the kx and ky gradient kernels to all pixels.
#                 kx = ky = 0
#                 # Nested for loop to check 9 pixels total: p plus it's 8 neighbors.
#                 # Use list comprehension here? Also get rid of try statements.
#                 for xx in range(x - 1, x + 2):
#                     for yy in range(y - 1, y + 2):
#                         # Extract RGB of the current neighbor pixel.
#                         p = self.oldimg.getPixel(xx, yy)
#                         r = p.getRed()
#                         g = p.getGreen()
#                         b = p.getBlue()
#
#                         ## The actual Sobel algorithm:
#                         # Left Row.
#                         if xx == x - 1:
#                             if yy == y - 1:
#                                 kx -= (r + g + b)
#                                 ky -= (r + g + b)
#                             elif yy == y:
#                                 kx -= 2 * (r + g + b)
#                             elif yy == y + 1:
#                                 kx -= (r + g + b)
#                                 ky += (r + g + b)
#                         # Middle Row.
#                         elif xx == x and yy == y - 1:
#                             ky -= 2 * (r + g + b)
#                         elif xx == x and yy == y + 1:
#                             ky += 2 * (r + g + b)
#                         # Right Row.
#                         elif xx == x + 1:
#                             if yy == y - 1:
#                                 kx += (r + g + b)
#                                 ky -= (r + g + b)
#                             elif yy == y:
#                                 kx += 2 * (r + g + b)
#                             elif yy == y + 1:
#                                 kx += (r + g + b)
#                                 ky += (r + g + b)
#                 # Use Pythagoras' theorem to calc the relative length of kx & ky.
#                 length = sqrt((kx ** 2) + (ky ** 2))
#                 # Each pixels r+g+b can have 3*255=765 and for +/-4 the maximum is
#                 # 4*765=3060. The final range is (sqrt(2*3060**2)=4328.
#                 # Now we can normalize the length to the possible range:
#                 length = int(length / 4328.0 * 255)
#
#                 # Finally, apply the normalized length to each pixel.
#                 p.red = p.green = p.blue = length
#                 self.newimg.setPixel(x, y, p)
#         self.write("_sobel")
#
#
# if __name__ == "__main__":
#     # Leave out the "draw=0" to produce a popup of the image once it's complete.
#     img = ImageFilter("example.png", draw=0)
#     img.sobel()
