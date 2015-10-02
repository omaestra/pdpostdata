from django.contrib import admin
from orders.models import Order


class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'user', 'status', 'final_total', 'timestamp', ]

    class Meta:
        model = Order

admin.site.register(Order, OrderAdmin)
