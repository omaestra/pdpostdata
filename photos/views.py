from django.http import JsonResponse

from django.shortcuts import render, HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.http import QueryDict

from .forms import PhotoForm
from .models import Photo
from carts.models import Cart, CartItem
from products.models import Product

# Create your views here.

from django.views.generic.edit import FormView

from photos.models import Photo

class MultiAttachmentMixin(object):

    def post(self, request, *args, **kwargs):
        # Ajax POST for file uploads
        if request.POST:
            custom_post = QueryDict('temp_hash=%s' % request.POST.get('temp_hash'))
            file_form = PhotoForm(request.POST, request.FILES)
            print(request.FILES)
            if file_form.is_valid():
                # file_form.save()
                response = {'files': []}
                # Create a new entry in our database
                new_image = Photo(image_field=request.FILES['image_field'],
                                  temp_hash=request.POST.get('temp_hash'))
                # Save the image using the model's ImageField settings
                new_image.save()
                response['files'].append({
                    'name': '%s' % new_image.id,
                    'size': '%d' % request.FILES.__sizeof__(),
                    'url': '%s' % new_image.image_field.url,
                    'thumbnailUrl': '%s' % new_image.image_field.url,
                    'deleteUrl': '\/image\/delete\/%s' % new_image.id,
                    "deleteType": 'DELETE'
                })
                # return HttpResponse('{"status":"success"}', content_type='application/json')
                return JsonResponse({'response': response, })
            # return HttpResponse('{"status":"error: %s"}' % file_form.errors, content_type='application/json')
            return JsonResponse({'response': file_form.errors, })

        return super(MultiAttachmentMixin, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        print("FJKHJH")
        # I load these uploaded files into django-filer objects.
        files = Photo.objects.filter(temp_hash=self.request.POST.get('temp_hash'))
        # folder = Folder.objects.get(name='Customer Service')
        for f in files:
            new_file = Photo(image_field=f)
            # Save the image using the model's ImageField settings
            new_file.save()
            # Attach the new Filer files to the original form object.
            self.object.attachments.add(new_file)
        files.delete()

        return super(MultiAttachmentMixin, self).form_valid(form)


class UploadView(MultiAttachmentMixin, FormView):
    template_name = 'photos/upload2.html'
    form_class = PhotoForm
    success_url = '/upload2/'


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
    request.session.set_expiry(120000)

    try:
        product = Product.objects.get(slug=slug)
    except Product.DoesNotExist:
        pass

    uploaded_images = []  # product variation
    if request.method == "POST":
        try:
            response = {'files': []}
            for photo in request.FILES.getlist('photos'):
                # Create a new entry in our database
                new_image = Photo(image_field=photo)
                # new_image.cart_item = cart_item
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
                uploaded_images.append(new_image)
        except:
            pass
        print(len(uploaded_images))
        if len(uploaded_images) > 0:
            cart_item.photo_set.add(*uploaded_images)

        # cart_item.save()
        # success message
        context = {
            'product': product,
            'photos': uploaded_images,
        }

        return render(request, "photos/upload.html", context)
        # return JsonResponse(response)
        # return HttpResponseRedirect(reverse('cart'))

    # error message
    form = PhotoForm()
    context = {
        'form': form,
        'product': product,
        "class_name": form.__class__.__name__
    }

    return render(request, "photos/upload.html", context)
