from urllib2 import urlopen
import urllib2
from django.core.files.base import ContentFile
from django.http import response
from social.backends.facebook import FacebookOAuth2
from social.backends.google import GoogleOAuth2
from social.backends.instagram import InstagramOAuth2


def update_user_social_data(strategy, response, *args, **kwargs):
    """Set the name and avatar for a user only if is new.
    """
    # print 'update_user_social_data ::', strategy
    if not kwargs['is_new']:
        return

    full_name = ''
    backend = kwargs['backend']

    user = kwargs['user']

    if (
        isinstance(backend, GoogleOAuth2)
        or isinstance(backend, FacebookOAuth2)
    ):
        full_name = response.get('name')
    elif (
        isinstance(backend, InstagramOAuth2)
    ):

        if kwargs.get('details'):
            full_name = kwargs['details'].get('fullname')

    user.full_name = full_name

    if isinstance(backend, GoogleOAuth2):
        if response.get('image') and response['image'].get('url'):
            url = response['image'].get('url')
            url = url.split('?')[0]
            ext = url.split('.')[-1]
            image_name = 'google_avatar_%s' % user.username
            user.userprofile.avatar.save(
               '{0}.{1}'.format(image_name, ext),
               ContentFile(urllib2.urlopen(url).read())
            )
    elif isinstance(backend, FacebookOAuth2):
        fbuid = kwargs['response']['id']
        image_name = 'fb_avatar_%s.jpg' % fbuid
        image_url = 'http://graph.facebook.com/%s/picture?type=large' % fbuid
        image_stream = urlopen(image_url)

        user.avatar.save(
            image_name,
            ContentFile(image_stream.read()),
        )
    elif isinstance(backend, InstagramOAuth2):

        if response['data'].get('profile_picture'):
            image_name = 'instagram_avatar_%s.jpg' % user.username
            image_url = response['data'].get('profile_picture')
            image_stream = urlopen(image_url)

            user.userprofile.avatar.save(
                image_name,
                ContentFile(image_stream.read()),
            )

    user.save()
