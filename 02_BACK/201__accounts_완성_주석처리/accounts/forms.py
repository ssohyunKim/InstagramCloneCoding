from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import Profile
from django.contrib.auth.models import User

# 로그인 폼
class LoginForm(forms.ModelForm):
    class Meta: # Meta class를 이용해서 의 내부 옵션을 정의할수 있다
        model = User # 모델은 User 모델
        fields = ["username", "password"]
    
# 회원가입폼
class SignupForm(UserCreationForm): # UserCreationForm 장고에서제공하는 회원가입 폼
    username = forms.CharField(label='사용자명', widget=forms.TextInput(attrs={
        'pattern': '[a-zA-Z0-9]+',
        'title': '특수문자, 공백 입력불가',
    })) 
    
    nickname = forms.CharField(label='닉네임') # 개발자도구로 label 확인해보기
    picture = forms.ImageField(label='프로필 사진', required=False)
    
    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('email',)
        
    def clean_nickname(self): # 닉네임을 검사
        nickname = self.cleaned_data.get('nickname') # nickname을 통해서 받은 값을 cleaned_data를 이용해서 검사
        if Profile.objects.filter(nickname=nickname).exists(): # 값이 존재한다면
            raise forms.ValidationError('이미 존재하는 닉네임 입니다.') # 안내문출력
        return nickname # 최종적으로 문제없다면 nickname을 리턴함
    
    def clean_email(self): # 이메일을 검사
        email = self.cleaned_data.get('email')
        User = get_user_model() # get_user_model()을 이용해서 User모델을 가져온다
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('사용중인 이메일 입니다.')
        return email

    def clean_picture(self):
        picture = self.cleaned_data.get('picture')
        if not picture: # 사진이 아닌 값이 들어오면 
            picture = None # picture에는 빈 값을 가지게한다
        return picture
    
    def save(self):
        user = super().save() # super()를 이용해서 부모클래스의 값을 받아와서 user에 이름을 저장
        Profile.objects.create( 
            user=user,
            nickname=self.cleaned_data['nickname'],
            picture=self.cleaned_data['picture'],
        )
        return user 