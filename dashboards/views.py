import zipfile
from zipfile import ZipFile
import cStringIO as StringIO
from django.core.servers.basehttp import FileWrapper
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
@staff_member_required
def dashboard(request):
    # Count of Users joined in the last 30 days
    start_date = datetime.datetime.today() - datetime.timedelta(days=30)
    end_date = datetime.datetime.today()
    new_users_count = User.objects.filter(is_active=True, date_joined__range=(start_date, end_date)).count()

    # Count of pending Orders
    pending_orders_count = Order.objects.filter(status='Pendiente').count()

    context = {'new_users': new_users_count, 'pending_orders': pending_orders_count, }
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

        messages.success(request, 'Estatus del pedido #%s cambiado de "%s" a "%s" con exito!' %(order.order_id, old_status, new_status))

    # Count of Users joined in the last 30 days
    start_date = datetime.datetime.today() - datetime.timedelta(days=30)
    end_date = datetime.datetime.today()

    # Count of pending Orders
    pending_orders = Order.objects.all()

    order_status_choices = STATUS_CHOICES

    context = {'order_status_choices': order_status_choices, 'pending_orders': pending_orders, }
    template = 'dashboards/dashboard_orders.html'

    return render(request, template, context)

# Download a zip file which contains all the photos of the selected Order.
@staff_member_required
def send_zipfile(request, order_id=None):

    order = Order.objects.get(order_id=order_id)
    buffer_var = StringIO.StringIO()
    z = ZipFile(buffer_var, "w")
    for item in order.cart.cartitem_set.all():
        files = []
        for photo in item.photo_set.all():
            files.append(photo.image_field.path)

        for f in files:
            z.write(f, os.path.join('%s-%s' % (item.product.title, item.id), os.path.basename(f)))

    z.close()
    buffer_var.seek(0)
    response = HttpResponse(buffer_var.read())
    response['Content-Disposition'] = 'attachment; filename='+order_id+'.zip'
    response['Content-Type'] = 'application/x-zip-compressed'
    return response
