from django.db import models
from django.contrib.auth.models import AbstractUser  # 继承原有的user表


# Create your models here.

class UserProfile(AbstractUser):
    nick_name = models.CharField(max_length=50, verbose_name='昵称', default='')
    mobile = models.CharField(max_length=11, null=True, blank=True, verbose_name='手机号')

    class Meta:
        verbose_name = '用户信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username

