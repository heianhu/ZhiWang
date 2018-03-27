#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'heianhu'
from django import forms
from captcha.fields import CaptchaField  # 验证码
from .models import UserProfile


class LoginForm(forms.Form):
    email = forms.CharField(required=True)
    password = forms.CharField(required=True, min_length=5, widget=forms.PasswordInput)


class RegisterForm(forms.Form):
    email = forms.EmailField(required=True)
    nick_name = forms.CharField(required=True)
    password = forms.CharField(required=True, min_length=5, widget=forms.PasswordInput)
    retype_password = forms.CharField(required=True, min_length=5, widget=forms.PasswordInput)

    captcha = CaptchaField(error_messages={'invalid': '验证码错误'})
