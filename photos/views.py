from django.http import JsonResponse

from django.shortcuts import render, HttpResponseRedirect, HttpResponse, Http404, render_to_response
from django.core.urlresolvers import reverse
from django.http import QueryDict
from django.template import RequestContext

from .forms import PhotoForm
from .models import Photo
from carts.models import Cart, CartItem
from products.models import Product

# Create your views here.

from django.views.generic.edit import FormView
from photos.forms import JcropForm

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
                response = {'photos': []}
                for photo in request.FILES.getlist('photos'):
                    # Create a new entry in our database
                    new_image = Photo(image=photo,
                                      temp_hash=request.POST.get('temp_hash'))
                    # Save the image using the model's ImageField settings
                    new_image.save()
                    response['photos'].append({
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
        photo = Photo.objects.first()
        context['photo'] = photo

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


def make(request, slug):
    try:
        product = Product.objects.get(slug=slug)
    except Product.DoesNotExist:
        pass

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
        'form': form,
        'product': product,
        "class_name": form.__class__.__name__
    }

    return render(request, "photos/upload.html", context)
