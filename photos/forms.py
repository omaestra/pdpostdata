import uuid
import os
import copy
from itertools import count
from collections import namedtuple

from PIL import Image as pil

from django.forms import ModelForm, ValidationError
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.safestring import mark_safe

from django import forms
from .models import Photo, Crop, Size, SizeSet
from pdpostdata import settings

from photos.fields import MultiFileField

BROWSER_WIDTH = 800

UPLOAD_IMG_ID = "new-img-file"


class JcropWidget(forms.Widget):
    class Media:
        # form media, i.e. CSS and JavaScript needed for Jcrop.
        # You'll have to adopt these to your project's paths.
        css = {
            'all': (settings.STATIC_URL + "css/jquery.Jcrop.css",)
        }
        js = (
            settings.STATIC_URL + "js/jquery.Jcrop.min.js",
        )

    # fixed Jcrop options; to pass options to Jcrop, use the jcrop_options
    # argument passed to the JcropForm constructor. See example above.
    jcrop_options = {
        "onSelect": "storeCoords",
        "onChange": "storeCoords",
    }

    # HTML template for the widget.
    #
    # The widget is constructed from the following parts:
    #
    #  * HTML <img> - the actual image used for displaying and cropping
    #  * HTML <label> and <input type="file> - used for uploading a new
    #                                          image
    #  * HTML <input type="hidden"> - to remember image path and filename
    #  * JS code - The JS code makes the image a Jcrop widget and
    #              registers an event handler for the <input type="file">
    #              widget. The event handler submits the form so the new
    #              image is sent to the server without the user having
    #              to press the submit button.
    #
    markup = """
  <img id="jcrop-img" src="%(MEDIA_URL)s%(img_fn)s"/><br/>
  <label for="new-img-file">Neues Bild hochladen:</label>
  <input type="file" name="%(UPLOAD_IMG_ID)s" id="%(UPLOAD_IMG_ID)s"/>
  <input type="hidden" name="imagefile" id="imagefile" value="%(imagefile)s"/>
  <script type="text/javascript">
  function storeCoords(c)
  {
    jQuery('#id_x1').val(c.x);
    jQuery('#id_x2').val(c.x2);
    jQuery('#id_y1').val(c.y);
    jQuery('#id_y2').val(c.y2);
  }
  jQuery(function() {
      jQuery('#jcrop-img').Jcrop(%(jcrop_options)s);
      jQuery('#%(UPLOAD_IMG_ID)s').change(function(e){
        var form = jQuery('#%(UPLOAD_IMG_ID)s').parents('form:first');
        form.submit();
      });
  });</script>
    """

    def __init__(self, attrs=None):
        """
    __init__ does nothing special for now
    """
        super(JcropWidget, self).__init__(attrs)

    def add_jcrop_options(self, options):
        """
    add jcrop options; options is expected to be a dictionary of name/value
    pairs that Jcrop understands;
    see http://deepliquid.com/content/Jcrop_Manual.html#Setting_Options
    """
        for k, v in options.items():
            self.jcrop_options[k] = v

    def render(self, name, value, attrs=None):
        """
    render the Jcrop widget in HTML
    """
        # translate jcrop_options dictionary to JavaScipt
        jcrop_options = "{";
        for k, v in self.jcrop_options.items():
            jcrop_options = jcrop_options + "%s: %s," % (k, v)
        jcrop_options = jcrop_options + "}"

        # fill in HTML markup string with actual data
        output = self.markup % {
            "MEDIA_URL": settings.MEDIA_URL,
            "img_fn": str(value),
            "UPLOAD_IMG_ID": UPLOAD_IMG_ID,
            "jcrop_options": jcrop_options,
            "imagefile": value,
        }
        return mark_safe(output)


class JcropForm(forms.Form):
    """
  Jcrop form class
  """
    imagefile = forms.Field(widget=JcropWidget(), label="", required=False)
    x1 = forms.DecimalField(widget=forms.HiddenInput)
    y1 = forms.DecimalField(widget=forms.HiddenInput)
    x2 = forms.DecimalField(widget=forms.HiddenInput)
    y2 = forms.DecimalField(widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        """
    overridden init func; check for Jcrop options and remove them
    from kwargs
    """
        # remove upload image post data (if present); this would make Django form
        # code hick up (since there is no upload image widget in the control)...
        try:
            post_data = args[0]
            if UPLOAD_IMG_ID in post_data:
                del post_data[UPLOAD_IMG_ID]
        except (IndexError):
            # no POST data passed; nothing to do anyway
            pass

        jcrop_options = {}
        if "jcrop_options" in kwargs:
            jcrop_options = kwargs["jcrop_options"]
            del (kwargs["jcrop_options"])

        # call base class __init__
        super(JcropForm, self).__init__(*args, **kwargs)

        # set Jcrop options for our crop widget
        self.fields["imagefile"].widget.add_jcrop_options(jcrop_options)

    def clean_imagefile(self):
        """
    instantiate PIL image; raise ValidationError if field contains no image
    """
        try:
            self.img = pil.open(settings.MEDIA_ROOT + self.cleaned_data["imagefile"])
        except IOError:
            raise forms.ValidationError("Invalid image file")
        return self.cleaned_data["imagefile"]

    def is_valid(self):
        """
    checks if self._errors is empty; if so, self._errors is set to None and
    full_clean() is called.
    This is necessary since the base class' is_valid() method does
    not populate cleaned_data if _errors is an empty ErrorDict (but not 'None').
    I just failed to work this out by other means...
    """
        if self._errors is not None and len(self._errors) == 0:
            self._errors = None
            self.full_clean()
        return super(JcropForm, self).is_valid()

    def crop(self):
        """
    crop the image to the user supplied coordinates
    """
        x1 = self.cleaned_data['x1']
        x2 = self.cleaned_data['x2']
        y1 = self.cleaned_data['y1']
        y2 = self.cleaned_data['y2']
        self.img = self.img.crop((x1, y1, x2, y2))

    def resize(self, dimensions, maintain_ratio=False):
        """
    resize image to dimensions passed in
    """
        if maintain_ratio:
            self.img = self.img.thumbnail(dimensions, pil.ANTIALIAS)
        else:
            self.img = self.img.resize(dimensions, pil.ANTIALIAS)

    def save(self):
        """
    save image...
    """
        self.img.save(settings.MEDIA_ROOT + self.cleaned_data['imagefile'])

    @staticmethod
    def prepare_uploaded_img(files, upload_to, profile, max_display_size=None):
        """
    stores an uploaded image in the proper destination path and
    optionally resizes it so it can be displayed properly.
    Returns path and filename of the new image (without MEDIA_ROOT).

    'upload_to' must be a function reference as expected by Django's
    FileField object, i.e. a function that expects a profile instance
    and a file name and that returns the final path and name for the
    file.
    """
        try:
            upload_file = files[UPLOAD_IMG_ID]
        except MultiValueDictKeyError:
            # files dict does not contain new image
            return None

        # copy image data to final file
        fn = upload_to(profile, upload_file.name)
        pfn = settings.MEDIA_ROOT + fn
        destination = open(pfn, 'wb+')
        for chunk in upload_file.chunks():
            destination.write(chunk)
        destination.close()

        if max_display_size:
            # resize image if larger than specified
            im = pil.open(pfn)
            if im.size[0] > max_display_size[0]:
                # image is wider than allowed; resize it
                im = im.resize((max_display_size[0],
                                im.size[1] * max_display_size[0] / im.size[0]),
                               pil.ANTIALIAS)
            if im.size[1] > max_display_size[1]:
                # image is taller than allowed; resize it
                im = im.resize((im.size[0] * max_display_size[1] / im.size[1],
                                im.size[1]), pil.ANTIALIAS)
            im.save(pfn)

        return fn


class UploadForm(forms.Form):
    photos = MultiFileField(max_num=10, min_num=1, maximum_file_size=1024 * 1024 * 5)


class PhotoForm(forms.ModelForm):
    # photos = MultiFileField(max_num=10, min_num=1, maximum_file_size=1024*1024*5)

    class Meta:
        model = Photo
        fields = ['temp_hash', ]

    def clean_image(self):
        image = self.cleaned_data.get('image')

        if not image:
            return image

        if os.path.splitext(image.name)[1] == '':
            raise ValidationError("Please make sure images have file "
                                  "extensions before uploading")

        try:
            pil_image = pil.open(image)
        except IOError:
            raise ValidationError("Unable to open image file")
        except Exception:
            # We need to log here!
            raise ValidationError("Unknown error processing image")

        size_set = self.data.get('size_set')
        if not size_set:
            raise ValidationError("No size set found!")
        else:
            img_size = pil_image.size
            for size in size_set.size_set.filter(auto_crop=False):
                if img_size[0] < size.width or img_size[1] < size.height:
                    (w, h) = img_size[0:2]
                    raise ValidationError((
                                              "Uploaded image (%s x %s) is smaller"
                                              " than a required thumbnail size: %s"
                                          ) % (w, h, size))

        return image

    def __init__(self, *args, **kwargs):
        super(PhotoForm, self).__init__(*args, **kwargs)
        self.fields['temp_hash'] = forms.CharField(max_length='255', widget=forms.HiddenInput())
        self.fields['temp_hash'].initial = uuid.uuid1()


class CropForm(ModelForm):
    class Meta:
        model = Crop
        fields = '__all__'

    def _clean(self):
        if not ('crop_x' in self.data and 'crop_y' in self.data):
            self._errors.clear()
            raise ValidationError("Missing crop values")

        if int(self.data['crop_x']) < 0 or int(self.data['crop_y']) < 0:
            self._errors.clear()
            raise ValidationError("Crop positions must be non-negative")

        if int(self.data['crop_w']) < 1 or int(self.data['crop_h']) < 1:
            self._errors.clear()
            raise ValidationError("Crop must have a height and width of at least one pixel")

        return self.cleaned_data


def get_image(request):
    image_id = request.GET.get('image_id') or request.POST.get('image_id')
    image_hash = request.GET.get('image_hash')
    cls = ImageRegistry.get(image_hash)
    if image_id is not None:
        image = cls.objects.get(id=image_id)
    else:
        image = cls()

    return image


def apply_size_set(image, size_set):
    # Do we already have the image_set?
    if image.size_sets.filter(id=size_set.id).count() == 1:
        sizes = Size.objects.filter(size_set__id=size_set.id)
        der_images = image.derived.filter(size__in=[s.id for s in sizes])
    else:
        der_images = image.add_size_set(size_set)

    images = []
    for i in der_images:
        if not i.id:
            i.save()
        if not i.size.auto_crop:
            images.append(i)

    return images


Dimensions = namedtuple('Dimensions', 'width,height,ar')


def get_inherited_dims(image):
    o = image.original
    return Dimensions(image.size.get_width(),
                      image.size.get_height(),
                      image.size.get_aspect_ratio())


def get_inherited_ar(image):
    return get_inherited_dims(image)[2]


def calc_min_dims(images):
    widths, heights, ars = zip(get_inherited_dims(i) for i in images)
    assert (min(ars) == max(ars))
    return max(widths), max(heights)


def calc_linked_crop(images, prefix):
    dims = [get_inherited_dims(i) for i in images]
    max_dim = max(dims)
    ids = ','.join(str(i.id) for i in images)

    if images[0].crop is not None:
        # Start from the current crop if it exists.
        c = images[0].crop
        crop = Crop(crop_x=c.crop_x,
                    crop_y=c.crop_y,
                    crop_w=c.crop_w,
                    crop_h=c.crop_h)
    else:
        crop = Crop(0, 0, 0, 0)

    return (ids, max_dim,
            CropForm(instance=crop,
                     prefix=prefix))


def get_crops(images):
    """
    Gets the crop objects for the thumbs.  It will group images by aspect ratio
    so the user will only need to create one crop per aspect ratio when
    creating.  However, during edit, each image will be broken out with
    unique crops.
    TODO: Solve the case where we want to edit a crop form.  Right now we are
    assuming that this is a new set of crops.
    @param images: Set of sizes and calculated dimensions.
    @type  images: <(image, (width, height, aspect_ratio)), ...>
    @return:
    @rtype:
    """
    # group sizes by aspect ratio
    crops = []
    counter = count(0)
    for aspect_ratio, imageset in categorize(images, get_inherited_ar).iteritems():
        if aspect_ratio is None:
            # We have an unbound dimension in this case, add them individually
            for img in imageset:
                crops.append(calc_linked_crop([img], `next(counter)`))
        else:
            crops.append(calc_linked_crop(imageset, `next(counter)`))

    return crops


def categorize(iterator, key=None):
    if callable(key):
        iterator = ((key(i), i) for i in iterator)

    d = {}
    for c, i in iterator:
        try:
            d[c].append(i)
        except KeyError:
            d[c] = [i]

    return d


def min_size(size_set):
    """
    Calculates the minimum dimensions from a size_set
    """
    width, height = 0, 0
    for s in size_set.size_set.all():
        w, h, a = s.get_dimensions()
        width = max(width, w)
        height = max(height, h)

    return width, height


def upload_image(request, image_form=None, metadata_form=None):
    size_set = SizeSet.objects.get(id=request.GET['size_set'])
    if image_form is None:
        image = get_image(request)
        image_form = ImageForm(instance=image)
    else:
        image = image_form.instance

    if metadata_form is None:
        metadata_form = MetadataForm(instance=image.metadata)

    m_width, m_height = min_size(size_set)
    context = {
        'image_form': image_form,
        'metadata_form': metadata_form,
        'image': image,
        'size_set': size_set,
        'm_width': m_width,
        'm_height': m_height,
        'next_stage': 'crop_images',
        'current_stage': 'upload',
        'is_popup': True,
    }

    return render_to_response('admin/upload_image.html', context)


def upload_crop_images(request):
    size_set = SizeSet.objects.get(id=request.GET['size_set'])
    image = get_image(request)

    # We need to inject the size set id into the form data,
    # or we can't validate that the image dimensions are big
    # enough.
    post = request.POST.copy()
    post['size_set'] = size_set
    image_form = ImageForm(post, request.FILES, instance=image)
    metadata_form = MetadataForm(post, instance=image.metadata)
    if image_form.is_valid() and metadata_form.is_valid():
        metadata = metadata_form.save()
        image = image_form.save()
        # this works, it's terrible, but it works.
        image.metadata = metadata
        image.save()

        sizes = apply_size_set(image, size_set)

        context = {
            'formset': image_form,
            'browser_width': BROWSER_WIDTH,
            'image_element_id': request.GET['image_element_id'],
            'image': image,
            'sizes': sizes,
            'crops': get_crops(sizes),
            'next_stage': 'apply_sizes',
            'current_stage': 'crop_images',
            'is_popup': True,
        }

        context = RequestContext(request, context)
        return render_to_response('admin/crop_images.html', context)

    else:
        return upload_image(request, image_form, metadata_form)


def get_ids(request, index):
    return (int(i) for i in request.POST['crop_ids_%i' % index].split(','))


def get_crops_from_post(request):
    total_crops = int(request.POST['total_crops'])
    crop_mapping = {}
    for i in xrange(total_crops):
        # Build a crop form
        cf = CropForm(request.POST, prefix=`i`)
        if cf.is_valid():
            for image_id in get_ids(request, i):
                crop_mapping[image_id] = cf.instance
        else:
            # Right now, just blow up
            raise Exception(cf.errors.values())

    return crop_mapping


def update_crop(der_image, crop):
    der_image.set_crop(crop.crop_x, crop.crop_y, crop.crop_w, crop.crop_h).save()
    der_image.crop = der_image.crop


def apply_sizes(request):
    # Get each crop and validate it
    crop_mapping = get_crops_from_post(request)

    # Get the derived images from the original image.
    image = get_image(request)

    # Copy each crop into each image, render, and get the thumbnail.
    thumbs = []
    for der_image in image.derived.all():
        if der_image.id in crop_mapping:
            update_crop(der_image, crop_mapping[der_image.id])

        # Render the thumbnail...
        der_image.render()
        der_image.save()

        # Only show cropped images in the admin.
        if der_image.id in crop_mapping:
            thumbs.append(der_image)

    context = {
        'image': image,
        'image_thumbs': thumbs,
        'image_element_id': request.GET['image_element_id'],
        'is_popup': True,
    }

    context = RequestContext(request, context)
    return render_to_response('admin/complete.html', context)


STAGES = {
    'upload': upload_image,
    'crop_images': upload_crop_images,
    'apply_sizes': apply_sizes,
}


def get_next_stage(request):
    return request.POST.get('next_stage', 'upload')


def dispatch_stage(request):
    stage = get_next_stage(request)
    if stage in STAGES:
        return STAGES[stage](request)

    # Raise error
    return None


@csrf_exempt
def upload(request):
    return dispatch_stage(request)
