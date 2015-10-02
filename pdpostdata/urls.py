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
from photos.forms import PhotoSortForm, CartItemForm, PhotoUploadForm
from photos.views import UploadPhotosWizard
from dashboards.views import AnalyticsIndexView
from products import views

from django.contrib.admin.views.decorators import staff_member_required

from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets


# Serializers define the API representation.
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'is_staff')


# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'products', views.ProductViewSet)

urlpatterns = [
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^wizard/(?P<slug>[\w-]+)/$', UploadPhotosWizard.as_view([PhotoUploadForm, PhotoSortForm, CartItemForm]), name='wizard'),
    url(r'^wizard/edit/(?P<cart_item_id>\d+)/$', 'photos.views.edit_wizard', name='edit_wizard'),
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
    # url(r'^orders/(?P<order_id>[\w-]+)/$', 'orders.views.order_details', name='order_details'),

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
    url(r'^helpticket/send_helpticket/$', 'helptickets.views.send_helpticket', name='send_helpticket'),

    url(r'^photos/upload/$', 'photos.views.upload', name='upload'),
    url(r'^upload2/(?P<slug>[\w-]+)/$', 'photos.views.make', name='upload2'),
    url(r'^make/(?P<slug>[\w-]+)/$', 'photos.views.make', name='make'),
    url(r'^crop/$', 'photos.views.crop_image', name='cropper'),
    url(r'^sort/$', 'photos.views.sort_photos', name='sort_photos'),
    url(r'^delete_uploaded_image/$', 'photos.views.delete_uploaded_image', name='delete_uploaded_image'),

    url(r'^dashboard/$', staff_member_required(AnalyticsIndexView.as_view()), name='dashboard'),
    url(r'^dashboard/orders/$', 'dashboards.views.orders', name='dashboard_orders'),
    url(r'^dashboard/orders/(?P<order_id>[\w-]+)/download/$', 'dashboards.views.send_zipfile', name='send_zipfile'),
    url(r'^dashboard/users/$', 'dashboards.views.users', name='dashboard_users'),
    url(r'^dashboard/reports/$', 'dashboards.views.reports', name='dashboard_reports'),
    url(r'^dashboard/helptickets/$', 'dashboards.views.helptickets', name='dashboard_helptickets'),
    url(r'^dashboard/helptickets/answer/$', 'dashboards.views.answer_help_ticket', name='dashboard_answer_help_ticket'),


    url('', include('social.apps.django_app.urls', namespace='social')),
    url(r'^upload_from_instagram/(?P<product_slug>[\w-]+)/$', 'photos.views.upload_instagram_images', name='upload_instagram_images'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
