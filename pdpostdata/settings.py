"""
Django settings for pdpostdata project.

Generated by 'django-admin startproject' using Django 1.8.1.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from config import *
from django.conf import settings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'b-zsforqd)bxof+2+_nmkip8@qfjw+yxb68r9w0@9083xc7w-%'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['http://pdpostdata.net', ]

try:
    # from .email_settings import host, user, password

    EMAIL_HOST = 'smtp.gmail.com'  # smtp.gmail.com smtp.sendgrid.net
    EMAIL_HOST_USER = 'omaestra@gmail.com'  # "email@gmail.com"
    EMAIL_HOST_PASSWORD = 'omaestra192ex8'  # "password"
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
except:
    pass

SITE_URL = 'http://127.0.0.1:8000'


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'formtools',
    'navigation',
    'accounts',
    'carts',
    'marketing',
    'orders',
    'products',
    'photos',
    'helptickets',
    'social.apps.django_app.default',
    'imagekit',
    'rest_framework',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'marketing.middleware.DisplayMarketing',
)

ROOT_URLCONF = 'pdpostdata.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates'),
                 ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social.apps.django_app.context_processors.backends',
                'social.apps.django_app.context_processors.login_redirect',
            ],
        },
    },
]

WSGI_APPLICATION = 'pdpostdata.wsgi.application'


AUTHENTICATION_BACKENDS = (
    'accounts.backends.EmailBackend',
    'social.backends.google.GoogleOAuth2',
    'social.backends.instagram.InstagramOAuth2',
    'social.backends.facebook.FacebookOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)


SOCIAL_AUTH_PIPELINE = (
    'social.pipeline.social_auth.social_details',
    'social.pipeline.social_auth.social_uid',
    'social.pipeline.social_auth.auth_allowed',
    'social.pipeline.social_auth.social_user',
    'social.pipeline.user.get_username',
    'social.pipeline.mail.mail_validation',
    'social.pipeline.user.create_user',
    'social.pipeline.social_auth.associate_user',
    'social.pipeline.debug.debug',
    'social.pipeline.social_auth.load_extra_data',
    'social.pipeline.user.user_details',
    'social.pipeline.debug.debug',

    'accounts.pipeline.update_user_social_data',
)


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Caracas'

USE_I18N = True

USE_L10N = True

USE_TZ = False

MARKETING_HOURS_OFFSET = 3
MARKETING_SECONDS_OFFSET = 0
DEFAULT_TAX_RATE = 0.12  # 12%


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'

MEDIA_URL = '/media/'

MEDIA_ROOT = os.path.join(BASE_DIR, "static", "media")

STATIC_ROOT = os.path.join(BASE_DIR, "static", "static_root")

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static", "static_files"),
)

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR,  'templates'),
)

EDITED_PREVIEWS_ROOT = getattr(settings, 'EDITED_PREVIEWS_ROOT', os.path.join('image_editor', 'previews'))

IMAGE_EDITOR_FILTERS = getattr(settings, 'IMAGE_EDITOR_FILTERS', {
    'crop': 'photos.filters.crop.ImageCropTool',
    'sepia': 'photos.filters.sepia.ImageSepiaFilter',
    'blur': 'photos.filters.blur.ImageBlurFilter',
    'sharpen': 'photos.filters.sharpen.ImageSharpenFilter',
    'contour': 'photos.filters.contour.ImageContourFilter',
    'edge_enhance': 'photos.filters.edge_enhance.ImageEdgeEnhanceFilter',
    'detail': 'photos.filters.detail.ImageDetailFilter',
    'grayscale': 'photos.filters.grayscale.ImageGrayscaleFilter'
})

IMAGE_EDITOR_OPTIONS = getattr(settings, 'IMAGE_EDITOR_OPTIONS', {})

FILTER_CLASSES = {}
for name, image_filter in IMAGE_EDITOR_FILTERS.items():
    chain = image_filter.split('.')
    class_object = getattr(__import__('.'.join(chain[:-1]), globals(), locals(), [chain[-1]]), chain[-1])
    options = IMAGE_EDITOR_OPTIONS.get(name, {})
    FILTER_CLASSES[name] = class_object(name, options)

MAX_WIDTH = getattr(settings, 'CROPPER_MAX_WIDTH', 300)
MAX_HEIGHT = getattr(settings, 'CROPPER_MAX_HEIGHT', 300)


REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly',),
    'PAGE_SIZE': 10
}