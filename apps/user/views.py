from django.shortcuts import render, redirect, render_to_response
from django.views.generic import View
from django.contrib.auth.backends import ModelBackend  # 用于添加邮箱登录
from django.contrib.auth import authenticate, login, logout  # 用于登录验证
from django.db.models import Q
from django.http import HttpResponse, FileResponse, JsonResponse, HttpResponseRedirect
from django.contrib.auth.hashers import make_password  # 密码做加密

from user.forms import LoginForm, RegisterForm
from user.models import UserProfile


# Create your views here.
class CustomBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = UserProfile.objects.get(email=username)
            if user.check_password(password):
                return user
        except Exception as e:
            return None


class RegisterView(View):
    def get(self, request):
        register_form = RegisterForm()
        return render(request, 'register.html', {'register_form': register_form})

    def post(self, request):
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            email = request.POST.get('email', '')
            nick_name = request.POST.get('nick_name', '')
            pass_word = request.POST.get('password', '')
            retype_password = request.POST.get('retype_password', '')
            if UserProfile.objects.filter(email=email):  # 检查是否已经注册过该用户
                return render(request, 'register.html', {'register_form': register_form, 'msg': '邮箱已存在!'})
            elif UserProfile.objects.filter(nick_name=nick_name):  # 检查是否已经注册过该用户
                return render(request, 'register.html', {'register_form': register_form, 'msg': '昵称已存在!'})
            elif pass_word != retype_password:
                return render(request, 'register.html', {'register_form': register_form, 'msg': '两次密码不一样'})
            else:
                user_profile = UserProfile()
                user_profile.nick_name = nick_name
                user_profile.email = email
                user_profile.password = make_password(pass_word)
                user_profile.is_active = True
                # user_profile.is_active = False  # 未激活
                # send_email_register(user_name)  # 发送邮件
                user_profile.save()

                # # 写入欢迎注册消息
                # user_message = UserMessage()
                # user_message.user = user_profile.id
                # user_message.message = '欢迎注册'
                # user_message.save()
                return render(request, 'login.html')
        else:
            print('adsf')
            return render(request, 'register.html', {'register_form': register_form})


class LoginView(View):

    def get(self, request):
        login_form = LoginForm()
        return render(request, 'login.html', {'form': login_form})

    def post(self, request):
        login_form = LoginForm(request.POST)
        if login_form.is_valid():  # 检查表单提交是否符合规定
            email = request.POST.get('email', '')
            pass_word = request.POST.get('password', '')
            print(pass_word)
            user = authenticate(username=email, password=pass_word)  # 验证是否存在或者对应正确
            print(user)
            if user is not None:
                if user.is_active:
                    login(request, user)  # django的auth自带的登录login
                    return redirect('index')
                else:
                    login_form.add_error(None, error='用户未激活!')
                    return render(request, 'login.html', {'form': login_form})
            else:
                login_form.add_error(None, error='用户名或密码错误!')
                return render(request, 'login.html', {'form': login_form, 'msg': '用户名或密码错误!'})

        else:
            print('asdfasd')
            return render(request, 'login.html', {'form': login_form})
