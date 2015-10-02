import string
import random

from .models import HelpTicket


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    the_id = "".join(random.choice(chars) for x in range(size))
    try:
        help_ticket = HelpTicket.objects.get(help_ticket_id=the_id)
        id_generator()
    except HelpTicket.DoesNotExist:
        return the_id


__author__ = 'oswaldomaestra'
