from django.http import JsonResponse

from django.shortcuts import render, HttpResponseRedirect
from django.core.urlresolvers import reverse
from .forms import PhotoForm
from .models import Photo
from carts.models import Cart, CartItem
from products.models import Product

# Create your views here.

from django.views.generic.edit import FormView

from photos.forms import UploadForm
from photos.models import Photo


class UploadView(FormView):
    template_name = 'photos/upload2.html'
    form_class = UploadForm
    success_url = '/upload2/'

    def form_valid(self, form):
        for each in form.cleaned_data['attachments']:
            Photo.objects.create(image_field=each)
        return super(UploadView, self).form_valid(form)


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
        the_id = request.session['cart_id']
    except:
        new_cart = Cart()
        new_cart.save()
        request.session['cart_id'] = new_cart.id
        the_id = new_cart.id

    cart = Cart.objects.get(id=the_id)

    try:
        product = Product.objects.get(slug=slug)
    except Product.DoesNotExist:
        pass

    try:
        cart_item_id = request.session['cart_item_id']
    except:
        # new_cart_item = CartItem()
        cart_item = CartItem.objects.create(cart=cart, product=product)
        # new_cart.save()
        request.session['cart_item_id'] = cart_item.id
        cart_item_id = new_cart.id

    cart_item = CartItem.objects.get(id=cart_item_id)

    request.session['cart_item_id'] = cart_item.id

    uploaded_images = []  # product variation
    if request.method == "POST":
        try:
            response = {'files': []}
            for photo in request.FILES.getlist('file'):
                # Create a new entry in our database
                new_image = Photo(image_field=photo)
                new_image.cart_item = cart_item
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
