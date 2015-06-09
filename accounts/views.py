# coding=utf-8
import re
import hashlib
import datetime
import random

from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.shortcuts import render, HttpResponseRedirect, Http404
from django.contrib.auth import logout, login, authenticate
from django.contrib import messages
from django.core.urlresolvers import reverse

from .forms import LoginForm, RegistrationForm, UserAddressForm, UserProfileForm, UserForm
from .models import EmailConfirmed, UserDefaultAddress, UserProfile

# Create your views here.
@login_required
def user_profile(request):
    try:
        user_id = request.session['user_id']
        user = settings.AUTH_USER_MODEL.User.objects.get(id=user_id)

    except:
        user_id = None

    if user_id:

        context = {"user": user, }
    else:
        empty_message = "Tu Perfil esta vacio, por favor registrate."
        context = {"empty": True, "empty_message": empty_message}

    template = "accounts/profile.html"
    return render(request, template, context)

@login_required
def edit_user_profile(request):
    profile = UserProfile.objects.get(user=request.user)

    if request.POST:
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        user_form = UserForm(request.POST, instance=request.user)
        if profile_form.is_valid() and user_form.is_valid():

            profile_form.save()
            user_form.save()

            messages.success(request, "Perfil editado con exito!")

            return HttpResponseRedirect(reverse('user_profile'))
    else:
        profile_form = UserProfileForm(instance=profile)
        user_form = UserForm(instance=request.user)

        context = {'profile_form': profile_form, 'user_form': user_form, }
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
    form = LoginForm(request.POST or None)
    btn = "Iniciar sesion"
    if form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(username=username, password=password)
        login(request, user)
        messages.success(request, "Iniciaste sesion exitosamente. Bienvenido!")
        return HttpResponseRedirect("/")
    context = {
        "form": form,
        "submit_btn": btn,
        "class_name": form.__class__.__name__
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
    form = UserAddressForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            new_address = form.save(commit=False)
            new_address.user = request.user
            new_address.save()
            is_default = form.cleaned_data["default"]
            if is_default:
                default_address, created = UserDefaultAddress.objects.get_or_create(user=request.user)
                default_address.shipping = new_address
                default_address.save()

            if next_page is not None:
                return HttpResponseRedirect(reverse(str(next_page)))

    submit_btn = "Guardar Direccion"
    form_title = "Agregar Nueva Direccion"
    return render(request, "form.html",
                  {"form": form,
                   "submit_btn": submit_btn,
                   "form_title": form_title,
                   })
