from django.urls import path
from .views import *

app_name = 'accounts' 

urlpatterns = [
    path('signup/', signup, name='signup'), # accounts/signup 으로 접근하면 signup뷰를 실행하고 이름을 singup으로한다
    path('login/', login_check, name='login'),
    path('logout/', logout, name='logout'),
]