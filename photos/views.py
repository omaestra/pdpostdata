import StringIO
import urllib2
import datetime
from django.core.files import File
from django.core.files.storage import FileSystemStorage
from django.core.files.temp import NamedTemporaryFile
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from formtools.wizard.views import SessionWizardView
from os.path import sep
from os import path
import os
import json

from PIL import Image, ImageFilter, ImageEnhance, ImageOps

from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.shortcuts import render, HttpResponseRedirect, HttpResponse, Http404, render_to_response, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.core.urlresolvers import reverse
from django.http import QueryDict
from django.template import RequestContext
from django.forms import ValidationError
from django.contrib.auth.decorators import login_required

from .forms import PhotoUploadForm, PhotoSortForm, CartItemForm, CropForm
from .models import Photo, Cropped
from pdpostdata import settings
from products.models import Product

# Create your views here.

from django.views.generic.edit import FormView
from photos.models import Photo
from carts.models import Cart, CartItem

from django.shortcuts import render_to_response

TEMPLATES = {"0": "photos/wizard-upload.html",
             "1": "photos/wizard-sortable.html",
             "2": "photos/wizard-cart.html"}


class UploadPhotosWizard(SessionWizardView):
    file_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'tmp_photos'))
    # template_name = 'photos/wizard-test.html'
    photo_list = []

    def post(self, *args, **kwargs):
        print(self.request.POST)
        if self.steps.current == '0':
            if self.request.is_ajax() and self.request.FILES:
                try:
                    temp_hash = self.request.POST.get('0-temp_hash')
                    uploaded_photos = Photo.objects.filter(temp_hash=temp_hash).count()
                    product = Product.objects.get(slug=self.kwargs.get('slug', None))

                    if uploaded_photos < product.image_total:
                        photo = self.request.FILES.get('file')

                        new_image = Photo(image=photo, temp_hash=self.request.POST.get('0-temp_hash'))
                        new_image.save()

                        response = {'file': []}
                        response['file'].append({
                            'id': '%s' % new_image.id,
                            'name': '%s' % new_image.image.name,
                            'size': '%d' % self.request.FILES.__sizeof__(),
                            'url': '%s' % new_image.smart.url,
                            'thumbnailUrl': '%s' % new_image.thumbnail.url,
                            'deleteUrl': '\/image\/delete\/%s' % new_image.id,
                            "deleteType": 'DELETE'
                        })

                        return JsonResponse(response)

                    else:
                        return HttpResponseForbidden(self.request)

                except Exception as e:
                    print("Exception Uploading the image", e.message)
                    pass

            else:
                if self.request.POST.get('0-uploaded_photo_count') == '0':
                    raise ValidationError("Ocurrio un error, recibimos un total de 0 fotos cargadas!")

        elif self.steps.current == '1':
            # TODO: Cambiar el json.loads porque no todos los exploradores pueden enviar el JSON con los resultados del sort, ej: iPhone.
            try:
                sorted_photo_list = json.loads(self.request.POST.get('1-photo_sort_list', None))

                for index, sorted_photo in enumerate(sorted_photo_list):
                    photo = get_object_or_404(Photo, id=sorted_photo['id'])
                    Photo.objects.filter(id=sorted_photo['id']).update(sequence=index)
                    # photo.sequence = index
                    # photo.save()
            except Exception as e:
                print("AQUI2", e)
                pass

        # elif self.steps.current == '2':
        #     if not self.request.POST.get('wizard_goto_step'):
        #         product = Product.objects.get(slug=self.kwargs.get('slug', None))
        #         qty = self.request.POST['2-quantity']
        #         cart_id = self.request.POST.get('2-cart')
        #
        #         prev_data = self.storage.get_step_data('0')
        #         if prev_data:
        #             temp_hash = prev_data.get('0-temp_hash', None)
        #
        #         cart = Cart.objects.get(id=cart_id)
        #
        #         photos = Photo.objects.filter(temp_hash=temp_hash)
        #
        #         cart_item = CartItem.objects.create(cart=cart, product=product)
        #         cart_item.photo_set = photos
        #         cart_item.quantity = qty
        #         cart_item.line_total = product.price
        #         cart_item.save()

                # return HttpResponseRedirect(reverse("cart"))

        return super(UploadPhotosWizard, self).post(self.request, *args, **kwargs)

    def get_context_data(self, form, **kwargs):
        context = super(UploadPhotosWizard, self).get_context_data(form=form, **kwargs)

        product = Product.objects.get(slug=self.kwargs.get('slug', None))
        context.update({'product': product})

        if self.steps.current == '0':

            try:
                prev_data = self.storage.get_step_data('0')
                if prev_data:
                    temp_hash = prev_data.get('0-temp_hash', '')
                    photo_list = self.get_images_data(temp_hash)
                    context.update({'photo_list': photo_list})
            except Exception as e:
                print(e)
                pass

        if self.steps.current == '1':
            prev_data = self.storage.get_step_data('0')
            temp_hash = prev_data.get('0-temp_hash', '')
            photo_list = self.get_images_data(temp_hash)

            context.update({'photo_list': photo_list, })

        if self.steps.current == '2':
            prev_data = self.storage.get_step_data('0')
            temp_hash = prev_data.get('0-temp_hash', '')
            photo_list = self.get_images_data(temp_hash)

            context.update({'photo_list': photo_list, })
        return context

    # this runs for the step it's on as well as for the step before
    def get_form_initial(self, step):

        # steps are named 'step1', 'step2', 'step3'
        current_step = self.storage.current_step

        if step == '0':
            return self.initial_dict.get(
                step, {'step_title': 'Paso 1', 'step_description': 'Carga tus fotos y editalas'}
            )
        # get the data for step 1 on step 3
        if step == '1':
            prev_data = self.storage.get_step_data('0')
            temp_hash = prev_data.get('0-temp_hash', '')
            sorted_photo_list = self.get_images_data(temp_hash).values('id')
            return self.initial_dict.get(
                step, {'temp_hash': temp_hash, 'photo_sort_list': sorted_photo_list, }
            )

        if step == '2':

            try:
                cart_id = self.request.session['cart_id']
            except Exception as e:
                print(e)
                new_cart = Cart()
                new_cart.save()
                self.request.session['cart_id'] = new_cart.id
                cart_id = new_cart.id

            cart = Cart.objects.get(id=cart_id)
            return self.initial_dict.get(
                step, {'cart': cart, 'step_title': 'Paso 3', 'step_description': 'Revisa de tus fotos'}
            )

        return self.initial_dict.get(step, {})

    @staticmethod
    def get_images_data(temp_hash):
        photos = Photo.objects.filter(temp_hash=temp_hash).order_by('sequence')
        return photos

    def get_form_step_files(self, form):
        return form.files

    def process_step_files(self, form):
        return self.get_form_step_files(form)

    def get_form_step_data(self, form):
        return form.data

    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def done(self, form_list, **kwargs):

        try:
            product = Product.objects.get(slug=self.kwargs.get('slug', None))
            temp_hash = form_list[0].cleaned_data['temp_hash']
            photo_list = Photo.objects.filter(temp_hash=temp_hash)

            if photo_list.count() != product.image_total:

                qty = form_list[2].cleaned_data['quantity']
                cart_id = form_list[2].cleaned_data['cart'].id

                cart = Cart.objects.get(id=cart_id)

                cart_item = CartItem.objects.create(cart=cart, product=product)
                cart_item.photo_set = photo_list
                cart_item.quantity = qty
                cart_item.line_total = product.price
                cart_item.save()

                return HttpResponseRedirect(reverse("cart"))

            else:
                messages.error(self.request, "Ocurrio un error! Solo cargaste %s fotos de %s" % (photo_list.count(), product.image_total))
                return HttpResponseRedirect("/")

        except Exception as e:
            print(e)
            return HttpResponseForbidden(self.request)

        # return render_to_response('photos/done.html', {
        #     'form_data': [form.cleaned_data for form in form_list], 'request': self.request,
        # })


def grouped(l, n):
    for i in xrange(0, len(l), n):
        yield l[i:i + n]


class MultiAttachmentMixin(object):
    def post(self, request, *args, **kwargs):
        # Ajax POST for file uploads
        if request.is_ajax():
            custom_post = QueryDict('temp_hash=%s' % request.POST.get('temp_hash'))
            file_form = PhotoUploadForm(request.POST, request.FILES)
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
    form_class = PhotoUploadForm
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
        photo_list = Photo.objects.filter(temp_hash=form_uuid)
        context = {'photo_list': photo_list, 'grouped_photo_list': grouped(photo_list, 4), }
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

    form = PhotoUploadForm()
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

        images_count = Photo.objects.filter(temp_hash=request.POST.get('temp_hash')).count()
        if images_count == product.image_total:
            return JsonResponse({'status': 'Total de imagenes cargadas!'})
        else:

            form = PhotoUploadForm(request.POST, request.FILES or None)
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
    instagram_images = get_instagram_images(user=request.user)
    form = PhotoUploadForm()
    context = {
        'upload_form': form,
        'product': product,
        'class_name': form.__class__.__name__,
        'images': instagram_images,
    }

    return render(request, "photos/upload2.html", context)


@require_POST
@csrf_exempt
def delete_uploaded_image(request):

    if request.POST:
        photo_id = request.POST.get('photo_id')
        photo = get_object_or_404(Photo, id=photo_id)

        photo.delete()

        return JsonResponse({'status': 'success', })

    return JsonResponse({'status': 'error', })


@require_POST
def crop_image(request):
    try:
        if request.method == 'POST':
            print(request.POST)
            # crop_data = json.loads(request.POST.get('image_data', None))
            image_id = request.POST.get('image_id', None)
            photo = Photo.objects.get(id=image_id)

            filter_data = json.loads(request.POST.get('image_filter_data', None))
            if filter_data:
                from photos.utils import apply_filters_to_image
                from django.core.files.storage import default_storage as storage  # TODO: allow set storage via settings
                from pdpostdata.settings import EDITED_PREVIEWS_ROOT
                shortname, extension = os.path.splitext(photo.image.name)
                result_image = apply_filters_to_image(photo.smart.name, filter_data)
                # result_image = apply_filters_to_image(new_cropped_file.image_cropped.name, filter_data)

                # photo.cropped.image_cropped.save(photo.cropped.image_cropped.name, result_image)
                new_cropped_file, created = Cropped.objects.get_or_create(original=photo)
                # new_cropped_file.x = crop_data['x']
                # new_cropped_file.y = crop_data['y']
                # new_cropped_file.w = crop_data['width']
                # new_cropped_file.h = crop_data['height']
                new_cropped_file.image_cropped.save(photo.get_name("crop_"), result_image)
                # new_cropped_file.save()

            data = {
                'path': photo.cropped.image_cropped.url,
                'cropped_image_id': photo.cropped.id,
                'original_image_id': photo.id,
            }

            return JsonResponse(data)

    except Photo.DoesNotExist:
        print("Error el objeto 'Photo' no existe")

    except IOError:
        raise ValidationError("Error, no se pudo abrir el archivo de imagen")

    except Exception as e:
        print(e.message, type(e))
        return JsonResponse({'errors': 'ilegal request', })


@login_required(login_url='/login/instagram')
def upload_instagram_images(request, product_slug=None):

    product = get_object_or_404(Product, slug=product_slug)
    if request.POST:
        print(json.loads(request.POST.get('selected_images[]')))
        selected_images = json.loads(request.POST.get('selected_images[]'))
        for image_url in selected_images:
            img_temp = NamedTemporaryFile(delete=True)
            img_temp.write(urllib2.urlopen(image_url).read())
            img_temp.flush()

            im = Photo()
            im.image.save(image_url, File(img_temp))

        return HttpResponse('{"status":"success"}', content_type='application/json')

    from instagram.client import InstagramAPI
    social = request.user.social_auth.get(provider='instagram')

    access_token = social.extra_data['access_token']
    client_secret = "a7d35a06a9984f2483b5448d178f8a83"
    api = InstagramAPI(access_token=access_token, client_secret=client_secret)
    recent_media, next_ = api.user_recent_media(user_id=request.user.social_auth.last().uid, count=10)
    images = []
    for media in recent_media:
        print("AQUI1", media.images['standard_resolution'])
        images.append(media.images['standard_resolution'])

    form = PhotoUploadForm()

    context = RequestContext(request, {'request': request, 'user': request.user, 'images': images, 'product': product, 'upload_form': form, })

    return render_to_response('photos/upload2.html', context_instance=context)


def get_instagram_images(user=None):
    from instagram.client import InstagramAPI
    try:
        social = user.social_auth.get(provider='instagram')

        access_token = social.extra_data['access_token']
        client_secret = "a7d35a06a9984f2483b5448d178f8a83"
        api = InstagramAPI(access_token=access_token, client_secret=client_secret)
        recent_media, next_ = api.user_recent_media(user_id=social.uid, count=10)
        images = []
        for media in recent_media:
            print("AQUI1", media.images['standard_resolution'])
            images.append(media.images['standard_resolution'])

        return images

    except Exception as e:
        print('Error de social_auth:', e)
        pass

