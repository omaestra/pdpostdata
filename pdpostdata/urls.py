"""pdpostdata URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from photos.views import UploadView


urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),

    url(r'^accounts/password_change/$', 'django.contrib.auth.views.password_change',
        {'post_change_redirect': '/accounts/password_change/done/'},
        name="password_change"),
    url(r'^accounts/password_change/done/$',
        'django.contrib.auth.views.password_change_done'),

    url(r'^$', 'products.views.home', name='home'),
    url(r'^s/$', 'products.views.search', name='search'),
    url(r'^products/$', 'products.views.all', name='products'),
    url(r'^products/(?P<slug>[\w-]+)/$', 'products.views.single', name='single_product'),

    url(r'^cart/(?P<id>\d+)/$', 'carts.views.remove_from_cart', name='remove_from_cart'),
    url(r'^cart/(?P<slug>[\w-]+)/$', 'carts.views.add_to_cart', name='add_to_cart'),
    url(r'^cart/$', 'carts.views.view', name='cart'),

    url(r'^checkout/$', 'orders.views.checkout', name='checkout'),
    url(r'^orders/$', 'orders.views.orders', name='user_orders'),
    url(r'^ajax/rate_order/$', 'orders.views.rate_order', name='ajax_rate_order'),
    url(r'^orders/(?P<order_id>[\w-]+)/$', 'orders.views.order_details', name='order_details'),

    url(r'^ajax/dismiss_marketing_message/$', 'marketing.views.dismiss_marketing_message',
        name='dismiss_marketing_message'),
    url(r'^ajax/email_signup/$', 'marketing.views.email_signup', name='ajax_email_signup'),
    url(r'^ajax/add_user_address/$', 'accounts.views.add_user_address', name='ajax_add_user_address'),

    url(r'^accounts/logout/$', 'accounts.views.logout_view', name='auth_logout'),
    url(r'^accounts/login/$', 'accounts.views.login_view', name='auth_login'),
    url(r'^accounts/register/$', 'accounts.views.registration_view', name='auth_register'),
    url(r'^accounts/address/add/$', 'accounts.views.add_user_address', name='add_user_address'),
    url(r'^accounts/activate/(?P<activation_key>\w+)/$', 'accounts.views.activation_view', name='activation_view'),
    url(r'^accounts/profile/$', 'accounts.views.user_profile', name='user_profile'),
    url(r'^address/delete/(?P<address_id>\d+)/$', 'accounts.views.delete_user_address', name='delete_user_address'),

    url(r'^photos/upload/$', 'photos.views.upload', name='upload'),
    url(r'^upload2/(?P<slug>[\w-]+)/$', 'photos.views.make', name='upload2'),
    url(r'^make/(?P<slug>[\w-]+)/$', 'photos.views.make', name='make'),
    url(r'^crop/$', 'photos.views.crop_image', name='cropper'),
    url(r'^sort/$', 'photos.views.sort_photos', name='sort_photos'),

    url(r'^dashboard/$', 'dashboards.views.dashboard', name='dashboard'),
    url(r'^dashboard/orders/$', 'dashboards.views.orders', name='dashboard_orders'),
    url(r'^dashboard/orders/(?P<order_id>[\w-]+)/download/$', 'dashboards.views.send_zipfile', name='send_zipfile'),
    url(r'^dashboard/users/$', 'dashboards.views.users', name='dashboard_users'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
