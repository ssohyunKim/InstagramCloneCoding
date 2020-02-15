from django.contrib.auth import authenticate, login
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import logout as django_logout
from .forms import SignupForm, LoginForm
from .models import Profile

import json
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST


# 회원가입뷰
def signup(request):
    if request.method == 'POST': # POST 방식으로 받았을때 
        form = SignupForm(request.POST, request.FILES) # SignupForm이용해서 을 통해서 
        if form.is_valid(): # 전달된 내용이 있다면 
            user = form.save() # 내용을 저장한다
            return redirect('accounts:login') # 완료되면 로그인 페이지로 이동한다
    else:
        form = SignupForm() # 오류상황에서는 다시 빈 회원가입 폼을 저장한다
        
    return render(request, 'accounts/signup.html', {       # 회원가입페이지로 이동
        'form': form,
    })

# 로그인확인뷰
def login_check(request):
    if request.method == "POST": 
        form = LoginForm(request.POST)
        name = request.POST.get('username') # name 변수에 username이름으로 받은 값을 넣고
        pwd = request.POST.get('password')  # pwd 변수에 password이름으로 받은 값을 넣는다
        user = authenticate(username=name, password=pwd) # authenticate을 이용해서 유저이름과 패스워드를 검사한다
        
        if user is not None: # user이름이 없는게 아니라면
            login(request, user) # login을 이용해서 로그인 한다
            return redirect("/") # 메인페이지로 이동 > post_list.html 화면
        else:
            return render(request, 'accounts/login_fail.html') # 실패했을때 보여질 페이지 // 나중에 ajax로 변경하기 :) 
    else:
        form = LoginForm() # 오류 발생시 빈로그인 폼을 담고 
        return render(request, 'accounts/login.html', {"form":form}) # 로그인창을 다시연다

# 로그아웃 뷰
def logout(request):
    django_logout(request) # django_logout을 통해 로그아웃을 한다
    return redirect("/") # 메인페이지로 이동