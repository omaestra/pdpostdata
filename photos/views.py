import StringIO
from django.core.files import File
from os.path import sep
from os import path
import os
import json

from PIL import Image

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import render, HttpResponseRedirect, HttpResponse, Http404, render_to_response, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.core.urlresolvers import reverse
from django.http import QueryDict
from django.template import RequestContext
from django.forms import ValidationError

from .forms import PhotoForm
from .models import Photo, Cropped
from pdpostdata import settings
from products.models import Product

# Create your views here.

from django.views.generic.edit import FormView
from photos.models import Photo


def grouped(l, n):
    for i in xrange(0, len(l), n):
        yield l[i:i + n]


class MultiAttachmentMixin(object):
    def post(self, request, *args, **kwargs):
        # Ajax POST for file uploads
        if request.is_ajax():
            custom_post = QueryDict('temp_hash=%s' % request.POST.get('temp_hash'))
            file_form = PhotoForm(request.POST, request.FILES)
            print(request.POST)
            print(request.FILES)

            if file_form.is_valid():
                # file_form.save()
                response = {'file': []}
                for photo in request.FILES.getlist('file'):
                    # Create a new entry in our database
                    new_image = Photo(image=photo,
                                      temp_hash=request.POST.get('temp_hash'))
                    # Save the image using the model's ImageField settings
                    new_image.save()
                    response['file'].append({
                        'name': '%s' % new_image.id,
                        'size': '%d' % request.FILES.__sizeof__(),
                        'url': '%s' % new_image.image.url,
                        'thumbnailUrl': '%s' % new_image.image.url,
                        'deleteUrl': '\/image\/delete\/%s' % new_image.id,
                        "deleteType": 'DELETE'
                    })

                # return HttpResponse('{"status":"success"}', content_type='application/json')
                return JsonResponse(response)
            # return HttpResponse('{"status":"error: %s"}' % file_form.errors, content_type='application/json')
            return JsonResponse({'response': file_form.errors, })

        return super(MultiAttachmentMixin, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        # I load these uploaded files into django-filer objects.
        files = Photo.objects.filter(temp_hash=self.request.POST.get('temp_hash'))
        # folder = Folder.objects.get(name='Customer Service')
        for f in files:
            new_file = Photo(image=f)
            # Save the image using the model's ImageField settings
            new_file.save()
            # Attach the new Filer files to the original form object.
            self.object.attachments.add(new_file)
        files.delete()

        return super(MultiAttachmentMixin, self).form_valid(form)

    def get_context_data(self, *args, **kwargs):
        # define a fixed aspect ratio for the user image
        aspect = 105.0 / 75.0
        # the final size of the user image
        final_size = (105, 75)
        context = super(MultiAttachmentMixin, self).get_context_data(*args, **kwargs)
        context['product'] = Product.objects.get(slug=self.kwargs['slug'])

        return context


class UploadView(MultiAttachmentMixin, FormView):
    template_name = 'photos/upload2.html'
    form_class = PhotoForm
    success_url = '/upload2/'


def upload_crop(request):
    # define a fixed aspect ratio for the user image
    aspect = 105.0 / 75.0
    # the final size of the user image
    final_size = (105, 75)

    profile = request.user.get_profile()

    if request.method == "POST" and len(request.FILES) == 0:
        # user submitted form with crop coordinates
        form = JcropForm(request.POST)
        if form.is_valid():
            # apply cropping
            form.crop()
            form.resize(final_size)
            form.save()
            # redirect to profile display page
        return HttpResponseRedirect("/")

    elif request.method == "POST" and len(request.FILES):
        # user uploaded a new image; save it and make sure it is not too large
        # for our layout
        img_fn = JcropForm.prepare_uploaded_img(request.FILES, image_upload_to,
                                                profile, (370, 500))
        if img_fn:
            # store new image in the member instance
            profile.avatar = img_fn  # 'avatar' is an ImageField
            profile.save()

            # redisplay the form with the new image; this is the same as for
            # GET requests -> fall through to GET

    elif request.method != "GET":
        # only POST and GET, please
        return HttpResponse(status=400)

    # for GET requests, just display the form with current image
    form = JcropForm(initial={"imagefile": profile.avatar},
                     jcrop_options={
                         "aspectRatio": aspect,
                         "setSelect": "[100, 100, 50, 50]",
                     }
                     )

    return render_to_response("photos/upload.html",
                              {
                                  "crop_form": form,
                              },
                              RequestContext(request))


def sort_photos(request):
    if request.POST:
        form_uuid = request.POST.get('temp_hash')
        print("SORTING", request.POST, form_uuid)
        photo_list = grouped(Photo.objects.filter(temp_hash=form_uuid), 4)
        context = {'photo_list': photo_list, }
        template = 'photos/sortable.html'

        return render(request, template, context)

    return Http404(request)


def upload(request):
    if request.method == 'POST':
        response = {'files': []}
        # Create a new entry in our database
        new_image = Photo(image_field=request.FILES['image_field'])
        # Save the image using the model's ImageField settings
        new_image.save()
        # Save output for return as JSON
        response['files'].append({
            'name': '%s' % new_image.id,
            'size': '%d' % request.FILES.__sizeof__(),
            'url': '%s' % new_image.image_field.url,
            'thumbnailUrl': '%s' % new_image.image_field.url,
            'deleteUrl': '\/image\/delete\/%s' % new_image.id,
            "deleteType": 'DELETE'
        })
        print(response)
        return JsonResponse(response)

    form = PhotoForm()
    context = {
        'form': form,
        "class_name": form.__class__.__name__
    }

    return render(request, "photos/upload.html", context)


def make(request, slug=None):
    product = get_object_or_404(Product, slug=slug)

    if request.method == "POST":
        print(request.POST)
        print(request.FILES)

        form = PhotoForm(request.POST, request.FILES or None)
        if form.is_valid():
            response = {'file': []}

            photo = request.FILES.get('file')
            # [...] Process the file. Resize it, create thumbnails, etc.
            # Get an instance of picture model (defined below)
            new_image = Photo(image=photo, temp_hash=request.POST.get('temp_hash'))
            # Save the image using the model's ImageField settings
            new_image.save()

            response['file'].append({
                'name': '%s' % new_image.id,
                'size': '%d' % request.FILES.__sizeof__(),
                'url': '%s' % new_image.image.url,
                'thumbnailUrl': '%s' % new_image.image.url,
                'deleteUrl': '\/image\/delete\/%s' % new_image.id,
                "deleteType": 'DELETE'
            })

            # return HttpResponse('{"status":"success"}', content_type='application/json')
            return JsonResponse(response)
        # return HttpResponse('{"status":"error: %s"}' % file_form.errors, content_type='application/json')
        return JsonResponse({'response': form.errors, })

    # uploaded_images = []  # product variation
    # if request.method == "POST":
    #     try:
    #         response = {'files': []}
    #         for photo in request.FILES.getlist('photos'):
    #             # Create a new entry in our database
    #             new_image = Photo(image_field=photo)
    #             # new_image.cart_item = cart_item
    #             # Save the image using the model's ImageField settings
    #             new_image.save()
    #             # Save output for return as JSON
    #             response['files'].append({
    #                 'name': '%s' % new_image.id,
    #                 'size': '%d' % request.FILES.__sizeof__(),
    #                 'url': '%s' % new_image.image_field.url,
    #                 'thumbnailUrl': '%s' % new_image.image_field.url,
    #                 'deleteUrl': '\/image\/delete\/%s' % new_image.id,
    #                 "deleteType": 'DELETE'
    #             })
    #             uploaded_images.append(new_image)
    #     except:
    #         pass
    #     print(len(uploaded_images))
    #     if len(uploaded_images) > 0:
    #         cart_item.photo_set.add(*uploaded_images)
    #
    #     # cart_item.save()
    #     # success message
    #     context = {
    #         'product': product,
    #         'photos': uploaded_images,
    #     }
    #
    #     return render(request, "photos/upload.html", context)
    #     # return JsonResponse(response)
    #     # return HttpResponseRedirect(reverse('cart'))

    # error message
    form = PhotoForm()
    context = {
        'upload_form': form,
        'product': product,
        'class_name': form.__class__.__name__
    }

    return render(request, "photos/upload2.html", context)


@require_POST
def crop_image(request):
    try:
        if request.method == 'POST':
            box = json.loads(request.POST.get('image_data', None))
            image_id = request.POST.get('image_id', None)
            photo = Photo.objects.get(id=image_id)
            img = Image.open(photo.image.path, mode='r')

            x = box['x']
            y = box['y']
            width = box['width']
            height = box['height']

            values = (x, y, x + width, y + height)

            if width and height and (width != img.size[0] or height != img.size[1]):
                cropped_image = img.crop(values).resize((width, height), Image.ANTIALIAS)
            else:
                raise

            tempfile_io = StringIO.StringIO()
            cropped_image.save(tempfile_io, format='JPEG', overwrite=True)
            from django.core.files.uploadedfile import InMemoryUploadedFile
            image_file = InMemoryUploadedFile(tempfile_io, None, 'crop.jpg', 'image/jpeg', tempfile_io.len, None)

            # Get the filename from the original image field, i.e: "image.jpg"
            filename = photo.image.path.split(sep)[-1]
            # Get the extension of the original image
            ext = filename.split('.')[-1]
            filename = "%s.%s" % (str(photo.id), ext)

            new_cropped_file, created = Cropped.objects.get_or_create(original=photo)
            new_cropped_file.x = x
            new_cropped_file.y = y
            new_cropped_file.w = width
            new_cropped_file.h = height

            new_cropped_file.image_cropped.save('crop_%s' % filename, image_file)
            new_cropped_file.save()

            data = {
                'path': new_cropped_file.image_cropped.url,
                'cropped_image_id': new_cropped_file.id,
                'original_image_id': photo.id,
            }

            return JsonResponse(data)

    except Photo.DoesNotExist:
        print("Error el objeto 'Photo' no existe")

    except IOError:
        print("HFJh")
        raise ValidationError("Error, no se pudo abrir el archivo de imagen")

    except Exception as e:
        print(e.message, type(e))
        return JsonResponse({'errors': 'ilegal request', })
