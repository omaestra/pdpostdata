from decimal import Decimal
from django.conf import settings
from django.db import models

# Create your models here.
from accounts.models import UserAddress
from carts.models import Cart

RATE_CHOICES = zip(range(1, 6), range(1, 6))

STATUS_CHOICES = (
    ("Pendiente", "Pendiente"),
    ("Iniciado", "Iniciado"),
    ("Rechazado", "Rechazado"),
    ("Imprimiendo", "Imprimiendo"),
    ("Enviado", "Enviado"),
)

# python tuples
try:
    tax_rate = settings.DEFAULT_TAX_RATE
except Exception, e:
    print str(e)
    raise NotImplementedError(str(e))


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)
    order_id = models.CharField(max_length=120, default='ABC', unique=True)
    cart = models.ForeignKey(Cart)
    status = models.CharField(max_length=120, choices=STATUS_CHOICES, default="Pendiente")
    shipping_address = models.ForeignKey(UserAddress, related_name='shipping_address', default=1)
    billing_address = models.ForeignKey(UserAddress, related_name='billing_address', default=1)
    sub_total = models.DecimalField(default=10.99, max_digits=1000, decimal_places=2)
    tax_total = models.DecimalField(default=0.00, max_digits=1000, decimal_places=2)
    final_total = models.DecimalField(default=10.99, max_digits=1000, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __unicode__(self):
        return self.order_id

    def get_final_amount(self):
        instance = Order.objects.get(id=self.id)
        two_places = Decimal(10) ** -2
        tax_rate_dec = Decimal("%s" % tax_rate)
        sub_total_dec = Decimal(self.sub_total)
        tax_total_dec = Decimal(tax_rate_dec * sub_total_dec).quantize(two_places)
        instance.tax_total = tax_total_dec
        instance.final_total = sub_total_dec + tax_total_dec
        instance.save()
        return instance.final_total


class OrderRating(models.Model):
    order = models.OneToOneField(Order)
    comment = models.TextField(max_length=120)
    rate = models.DecimalField(max_digits=1, decimal_places=0, choices=RATE_CHOICES)
