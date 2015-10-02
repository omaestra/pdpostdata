from django.contrib import admin
from helptickets.models import HelpTicket


class HelpTicketAdmin(admin.ModelAdmin):
    list_display = ['user', 'subject', 'timestamp', ]

    class Meta:
        model = HelpTicket


admin.site.register(HelpTicket, HelpTicketAdmin)
