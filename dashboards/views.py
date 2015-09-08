from zipfile import ZipFile
import cStringIO as StringIO
import os
import datetime

from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages

from orders.models import Order
from orders.models import STATUS_CHOICES

# Shows the dashboard generic information
from photos.models import Cropped


from django.views.generic import TemplateView
from django.contrib.auth.models import User
from products.models import Product

from django.utils import timezone


def last_day_of_month(any_day):
    next_month = any_day.replace(day=28) + timezone.timedelta(days=4)
    return next_month - timezone.timedelta(days=next_month.day)


def first_day_of_month(any_day):
    return timezone.datetime(any_day.year, any_day.month, 1)


class AnalyticsIndexView(TemplateView):
    template_name = 'dashboards/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super(AnalyticsIndexView, self).get_context_data(**kwargs)
        context['monthly_registrations'] = self.monthly_registrations()
        context['monthly_sales'] = self.monthly_sales()
        context['orders_by_status'] = self.orders_by_status()
        context['favorite_products'] = self.favorite_products()

        # Users joined in the last 30 days
        start_date = datetime.datetime.today() - datetime.timedelta(days=30)
        end_date = datetime.datetime.today()
        new_users_count = User.objects.filter(is_active=True, date_joined__range=(start_date, end_date)).count()

        # Pending Orders
        pending_orders_count = Order.objects.filter(status='Pendiente').count()

        context['new_users'] = new_users_count
        context['pending_orders'] = pending_orders_count

        return context

    @staticmethod
    def monthly_registrations():
        final_data = []

        date = timezone.now()

        for month in xrange(1, 13):

            ceil = last_day_of_month(datetime.date(timezone.now().year, month, 1))
            floor = first_day_of_month(datetime.date(timezone.now().year, month, 1))
            date = date.replace(month=month)
            count = User.objects.filter(
                date_joined__gte=floor,
                date_joined__lte=ceil).count()
            final_data.append(count)
        return final_data

    @staticmethod
    def monthly_sales():
        final_data = []

        date = timezone.now()

        for month in xrange(1, 13):
            ceil = last_day_of_month(datetime.date(timezone.now().year, month, 1))
            floor = first_day_of_month(datetime.date(timezone.now().year, month, 1))
            sale_total = 0
            date = date.replace(month=month)
            orders = Order.objects.filter(
                timestamp__gte=floor,
                timestamp__lte=ceil)
            for order in orders:
                sale_total += float(order.final_total)
            final_data.append(sale_total)
        return final_data

    @staticmethod
    def orders_by_status():
        final_data = {}

        for index, status in STATUS_CHOICES:
            order_status_count = Order.objects.filter(status=index).count()
            final_data[status] = order_status_count

        return final_data

    @staticmethod
    def favorite_products():
        final_data = []

        products = Product.objects.all()
        for product in products:
            count = product.cartitem_set.count()
            final_data.append(count)

        return final_data


@staff_member_required
def dashboard(request):
    # Count of Users joined in the last 30 days
    start_date = datetime.datetime.today() - datetime.timedelta(days=30)
    end_date = datetime.datetime.today()
    new_users_count = User.objects.filter(is_active=True, date_joined__range=(start_date, end_date)).count()

    # Count of pending Orders
    pending_orders_count = Order.objects.filter(status='Pendiente').count()

    orders = Order.objects.all()

    context = {'new_users': new_users_count, 'pending_orders': pending_orders_count, 'orders': orders}
    template = 'dashboards/dashboard.html'

    return render(request, template, context)


# Return all the users joined in the last 30 days
@staff_member_required
def users(request):
    if request.POST:
        print("POST")
    # Count of Users joined in the last 30 days
    start_date = datetime.datetime.today() - datetime.timedelta(days=30)
    end_date = datetime.datetime.today()
    new_users = User.objects.filter(is_active=True, date_joined__range=(start_date, end_date))

    context = {'new_users': new_users, }
    template = 'dashboards/dashboard_users.html'

    return render(request, template, context)


# Return all the Orders
@staff_member_required
def orders(request):
    if request.POST:
        print(request.POST)
        try:
            the_id = request.POST.get('order_id')
        except:
            the_id = None

        order = Order.objects.get(order_id=the_id)

        try:
            old_status = order.status
            new_status = request.POST.get('status')
        except:
            new_status = None

        order.status = new_status
        order.save()

        messages.success(request, 'Estatus del pedido #%s cambiado de "%s" a "%s" con exito!' % (
        order.order_id, old_status, new_status))

    # Count of Users joined in the last 30 days
    start_date = datetime.datetime.today() - datetime.timedelta(days=30)
    end_date = datetime.datetime.today()

    # Count of pending Orders
    pending_orders = Order.objects.all().order_by('-timestamp')

    context = {'order_status_choices': STATUS_CHOICES, 'pending_orders': pending_orders, }
    template = 'dashboards/dashboard_orders.html'

    return render(request, template, context)


# Download a zip file which contains all photos of the selected Order.
@staff_member_required
def send_zipfile(request, order_id=None):
    order = Order.objects.get(order_id=order_id)
    buffer_var = StringIO.StringIO()
    z = ZipFile(buffer_var, "w")
    for item in order.cart.cartitem_set.all():
        files = []
        for photo in item.photo_set.all():
            files.append(photo.image.path)
            try:
                files.append(photo.cropped.image_cropped.path)
            except Cropped.DoesNotExist:
                pass

        print(files)
        for f in files:
            z.write(f, os.path.join('%s-%s' % (item.product.title, item.id), os.path.basename(f)))

    z.close()
    buffer_var.seek(0)
    response = HttpResponse(buffer_var.read())
    response['Content-Disposition'] = 'attachment; filename=' + order_id + '.zip'
    response['Content-Type'] = 'application/x-zip-compressed'
    return response
