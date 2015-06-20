from django.shortcuts import render, HttpResponseRedirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib import messages
# Create your views here.

from products.models import Product, Variation
from .models import Cart, CartItem
from photos.models import Photo


def view(request):
    try:
        the_id = request.session['cart_id']
        cart = Cart.objects.get(id=the_id)

    except:
        the_id = None

    if the_id and cart.cartitem_set.count() > 0:
        new_total = 0.00
        for item in cart.cartitem_set.all():
            line_total = float(item.product.price) * item.quantity
            new_total += line_total

        request.session['items_total'] = cart.cartitem_set.count()
        cart.total = new_total
        cart.save()
        context = {"cart": cart, }
    else:
        empty_message = "Tu carrito esta vacio! Continua comprando!"
        context = {"empty": True, "empty_message": empty_message}
        request.session['items_total'] = 0

    template = "carts/view.html"
    return render(request, template, context)


def remove_from_cart(request, id):
    try:
        the_id = request.session['cart_id']
        cart = Cart.objects.get(id=the_id)
    except:
        return HttpResponseRedirect(reverse("cart"))

    cartitem = CartItem.objects.get(id=id)
    cartitem.delete()
    # cartitem.carts = None
    # cartitem.save()

    messages.success(request, "Item Successfully Deleted!")

    return HttpResponseRedirect(reverse("cart"))


def add_to_cart(request, slug):
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
    except:
        pass

    product_var = []  # product variation
    if request.method == "POST":
        qty = request.POST['qty']
        for item in request.POST:
            key = item
            val = request.POST[key]
            try:
                v = Variation.objects.get(product=product, category__iexact=key, title__iexact=val)
                product_var.append(v)
            except:
                pass

        photos = Photo.objects.filter(temp_hash=request.POST.get('temp_hash'))
        cart_item = CartItem.objects.create(cart=cart, product=product)
        cart_item.photo_set = photos
        if len(product_var) > 0:
            cart_item.variations.add(*product_var)
        cart_item.quantity = qty
        cart_item.save()
        # success message
        return HttpResponseRedirect(reverse("cart"))
    # error message
    return HttpResponseRedirect(reverse("cart"))