from django.contrib import admin

# Register your models here.
from user.models import UserProfile


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['nick_name', 'email']


admin.site.register(UserProfile, UserProfileAdmin)  # 将其注册
