from django.contrib import admin
from .models import UserProfile, EmailConfirmed, EmailMarketingSignUp, UserAddress, UserDefaultAddress

# Register your models here.


class UserProfileAdmin(admin.ModelAdmin):
    class Meta:
        model = UserProfile


admin.site.register(UserProfile, UserProfileAdmin)


class UserAddressAdmin(admin.ModelAdmin):
    class Meta:
        model = UserAddress


admin.site.register(UserAddress, UserAddressAdmin)
admin.site.register(UserDefaultAddress)
admin.site.register(EmailConfirmed)


class EmailMarketingSignUpAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', 'timestamp']

    class Meta:
        model = EmailMarketingSignUp


admin.site.register(EmailMarketingSignUp, EmailMarketingSignUpAdmin)