#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.contrib.auth import get_user_model


class EmailBackend(object):
    def authenticate(self, username=None, password=None):
        print("fjdh")
        user_cls = get_user_model()
        try:
            user = user_cls.objects.get(email=username)
            if user.check_password(password):
                return user
        except user_cls.DoesNotExist:
            return None
        except Exception as e:
            print(e)
            return None

    def get_user(self, user_id):

        user_cls = get_user_model()
        try:
            return user_cls.objects.get(pk=user_id)
        except user_cls.DoesNotExist:
            return None