from django.contrib.auth import authenticate, login
from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from users.forms import UserLoginForm, UserRegistrationForm, UserProfileForm
from users.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from cart.user_cart import Cart


def login_user(request):
    if request.method == 'POST':
        forms = UserLoginForm(data=request.POST)
        if forms.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = auth.authenticate(username=username, password=password) #проверка аутентификации
            if user:
                auth.login(request, user)
                return HttpResponseRedirect(reverse('index'))
    else:
        forms = UserLoginForm()
    context = {
        'forms': forms
    }

    return render(request, 'users/login.html', context)


def register(request):
    if request.method == 'POST': #определяем что это метод создания или отправки
        forms = UserRegistrationForm(data=request.POST) #то мы в клас кастомной формы записываем эти данные
        if forms.is_valid():
            forms.save()
            messages.success(request, 'Вы успешно зарегестрировались!') #если переданные данные корректны
            #то мы их сохраняем в нашу кастомную форму и после перебрасываем на страницу личного кабинета
            return HttpResponseRedirect(reverse('users:login')) #отвечает за перенаправления при успешной авторизации
    else:
        forms = UserRegistrationForm()
    context = {
        'forms': forms
        }

    return render(request, 'users/regester.html', context)


@login_required
def profile(request):
    if request.method == 'POST':
        forms = UserProfileForm(data=request.POST, instance=request.user)
        if forms.is_valid():
            forms.save()
            return HttpResponseRedirect(reverse('users:profile'))
        else:
            print(forms.errors)
    else:
        if not request.user.is_anonymous:
            forms = UserProfileForm(instance=request.user)
        else:
            return HttpResponseRedirect(reverse('users:login'))
    cart = Cart(request)
    cart_content_count = cart.get_cart_content_count()
    cart_content = cart.get_cart_content()
    context = {
        'forms': forms,
        'cart_content_count': cart_content_count,
        'cart_content': cart_content,
        'cart_info': cart,
    }
    return render(request, 'users/pro_file.html', context)


def logout(request):
    auth.logout(request)
    '''Эта строка выполняет выход пользователя, очищая его сессию и разрушая все связанные с ней данные аутентификации.
     Это означает, что текущий пользователь будет выйти из системы и больше не будет аутентифицирован.'''
    return HttpResponseRedirect(reverse('index'))
