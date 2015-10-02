# coding=utf-8
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render
from helptickets.forms import HelpTicketForm

from helptickets.utils import id_generator

@login_required
def send_helpticket(request):
    if request.POST:

        helpticket_form = HelpTicketForm(request.POST)

        if helpticket_form.is_valid():
            help_ticket = helpticket_form.save(commit=False)
            help_ticket.help_ticket_id = id_generator()
            help_ticket.user = request.user
            help_ticket.save()

            messages.success(request, "Tu ticket de ayuda #%s ha sido enviado con exito! Te responderemos lo más "
                                      "pronto posible! Revisa tu correo electrónico" % help_ticket.help_ticket_id)

            return HttpResponseRedirect(reverse('user_profile'))

        else:
            return HttpResponseForbidden('Error al procesar el formulario')

    else:
        return HttpResponseForbidden('Hey! Solo se aceptan peticiones POST')
