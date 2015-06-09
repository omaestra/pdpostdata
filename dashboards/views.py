import datetime

from django.shortcuts import render, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

from django.contrib.auth.models import User
from orders.models import Order


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