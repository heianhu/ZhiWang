from django.contrib import admin

# Register your models here.
from user.models import UserProfile


class UserProfileAdmin(admin.ModelAdmin):
    pass


admin.site.register(UserProfile, UserProfileAdmin)  # 将其注册
