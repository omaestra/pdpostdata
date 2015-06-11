# coding=utf-8
import re
import hashlib
import datetime
import random

from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.shortcuts import render, HttpResponseRedirect, Http404
from django.http import HttpResponseBadRequest
from django.contrib.auth import logout, login, authenticate
from django.contrib import messages
from django.core.urlresolvers import reverse

from .forms import LoginForm, RegistrationForm, UserAddressForm, UserProfileForm, UserForm
from .models import EmailConfirmed, UserDefaultAddress, UserProfile, UserAddress

# Create your views here.
@login_required
def user_profile(request):
    if request.POST:

        profile = request.user.userprofile

        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        user_form = UserForm(request.POST, instance=request.user)

        if profile_form.is_valid() and user_form.is_valid():
            profile_form.save()
            user_form.save()

            messages.success(request, "Perfil editado con exito!")

            return HttpResponseRedirect(reverse('user_profile'))
    else:

        try:
            profile = request.user.userprofile

        except:
            empty_message = "Tu Perfil esta vacio, por favor registrate."
            context = {'empty': True, 'empty_message': empty_message, }
            return HttpResponseBadRequest(reverse('user_profile'))

        profile = request.user.userprofile

        profile_form = UserProfileForm(instance=profile)
        user_form = UserForm(instance=request.user)
        address_form = UserAddressForm()

        context = {'user': request.user, 'user_form': user_form, 'profile_form': profile_form,
                   'address_form': address_form, }

        template = "accounts/profile.html"

        return render(request, template, context)


def logout_view(request):
    print "logging out"
    logout(request)
    messages.success(request,
                     u"<strong>Sesión cerrada con éxito</strong>. Puedes <a href='{0:s}'>iniciar sesion</a> nuevamente."
                     .format(reverse("auth_login")), extra_tags='safe, abc')
    # messages.warning(request, "There's a warning.")
    # messages.error(request, "There's an error.")
    return HttpResponseRedirect('%s' % (reverse("home")))


def login_view(request):
    login_form = LoginForm(request.POST or None)
    btn = "Iniciar sesion"

    if login_form.is_valid():
        redirect_to = request.REQUEST.get('next', '')
        username = login_form.cleaned_data['username']
        password = login_form.cleaned_data['password']
        user = authenticate(username=username, password=password)
        if user:
            # Is the account active? It could have been disabled.
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                login(request, user)
            else:
                # An inactive account was used - no logging in!
                messages.error(request, "Tu cuenta esta inactiva")
                return HttpResponseRedirect('%s' % (reverse("home")))

            messages.success(request, "Iniciaste sesion exitosamente. Bienvenido!")

            return HttpResponseRedirect(redirect_to)

    context = {
        "login_form": login_form,
        "submit_btn": btn,
        "class_name": login_form.__class__.__name__
    }
    return render(request, "form.html", context)


def registration_view(request):
    form = RegistrationForm(request.POST or None)
    btn = "Registrarme"
    if form.is_valid():
        new_user = form.save(commit=False)
        # new_user.first_name = "Justin" this is where you can do stuff with the model form
        new_user.save()
        messages.success(request, "Has sido registrado con exito! Por favor, confirma tu correo electronico ahora.")

        # Create and Save EmailConfirmed.
        salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
        activation_key = hashlib.sha1(salt + new_user.email).hexdigest()
        key_expires = datetime.datetime.today() + datetime.timedelta(2)

        new_email_confirmed = EmailConfirmed(user=new_user, activation_key=activation_key, key_expires=key_expires)
        new_email_confirmed.save()

        # Send register confirmation email to user
        new_email_confirmed.activate_user_email()

        return HttpResponseRedirect("/")

    context = {
        "form": form,
        "submit_btn": btn,
        "class_name": form.__class__.__name__
    }
    return render(request, "form.html", context)


SHA1_RE = re.compile('^[a-f0-9]{40}$')


def activation_view(request, activation_key):
    if SHA1_RE.search(activation_key):
        print "activation key is real"
        try:
            instance = EmailConfirmed.objects.get(activation_key=activation_key)
        except EmailConfirmed.DoesNotExist:
            instance = None
            messages.success(request, "There was an error with your request.")
            return HttpResponseRedirect("/")
        if instance is not None and not instance.confirmed:
            page_message = "Confirmation Successful! Welcome."
            instance.confirmed = True
            instance.activation_key = "Confirmed"
            instance.save()
            messages.success(request, "Successfully Confirmed! Please login.")
        elif instance is not None and instance.confirmed:
            page_message = "Already Confirmed"
            messages.success(request, "Already Confirmed.")
        else:
            page_message = ""

        context = {"page_message": page_message}
        return render(request, "accounts/activation_complete.html", context)
    else:
        raise Http404


def add_user_address(request):
    print request.GET
    try:
        next_page = request.GET.get("next")
    except:
        next_page = None

    address_form = UserAddressForm(request.POST or None)
    if request.method == "POST":
        if address_form.is_valid():
            new_address = address_form.save(commit=False)
            new_address.user = request.user
            phone_number = address_form.cleaned_data['phone_number']
            new_address.phone = phone_number
            new_address.save()

            messages.success(request, "Direccion de envio agregada con exito!")

            is_default = address_form.cleaned_data["default"]
            if is_default:
                default_address, created = UserDefaultAddress.objects.get_or_create(user=request.user)
                default_address.shipping = new_address
                default_address.save()

                messages.success(request, "Direccion de facturacion agregada con exito!")

            # if next_page is not None:
            return HttpResponseRedirect(reverse('user_profile'))

    submit_btn = "Guardar Direccion"
    form_title = "Agregar Nueva Direccion"
    return render(request, "accounts/profile.html",
                  {"address_form": address_form,
                   "submit_btn": submit_btn,
                   "form_title": form_title,
                   })

def delete_user_address(request, address_id):

    address = UserAddress.objects.get(id=address_id)
    address.delete()
    # cartitem.carts = None
    # cartitem.save()

    messages.success(request, "Direccion eliminada con exito!")

    return HttpResponseRedirect(reverse("user_profile"))
