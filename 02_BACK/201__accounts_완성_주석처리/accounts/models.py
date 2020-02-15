from django.conf import settings
from django.db import models
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill

# 프로필 사진 업로드 처리과정
def user_path(instance, filename):
    from random import choice # 랜덤으로 아무 원소나 하나 뽑아주는 choice를 불러옴
    import string
    arr = [choice(string.ascii_letters) for _ in range(8)] # string.ascii_letters : 대소문자 모두 abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ 을 번 반복해서 리스트에 담는다
    pid = ''.join(arr) # arr의 리스트를 공백없이 붙인다
    extension = filename.split('.')[-1]  # 파일의 이름을 .기준으로 나눠서 리스트로 저장한다
    return 'accounts/{}/{}.{}'.format(instance.user.username, pid, extension) # format함수를 이용해서 {}안에 하나씩 배치한다
    # 예시 : accounts/kindfamily/aEbSADFa.png

# custom User Profile 모델 생성
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) # 장고의 기본 모델인 User를 일대일의 관계로 연결하고 둘중에 하나가 삭제되면 둘다 삭제되게 한다
    nickname = models.CharField('별명', max_length=30, unique=True) # admin 페이지에서 보여질 이름을 '별명'으로 하고 최대 30글자로 제한을 두고 해당 필드가 테이블에서 unique함을 나타낸다 
    picture = ProcessedImageField(upload_to=user_path, # 사진이 저장될 위치를 정함
                                 processors=[ResizeToFill(150,150)], # 사이즈를 150x150으로 정함
                                 format='JPEG', # 사진 포맷을 JPEG
                                 options={'quality': 90}, # 사진 퀄리티를 90
                                 blank=True, # Optional 필드로 지정
                                 )
    about = models.CharField(max_length=300, blank=True) # 자기소개필드 최대 300글자
    GENDER_C = ( # 성별 선택
        ('선택안함', '선택안함'),
        ('여성', '여성'),
        ('남성', '남성'),
    )
    
    gender = models.CharField('성별(선택사항)',
                             max_length=10,
                             choices=GENDER_C, # GENDER_C를 불러와서 선택창으로
                             default='N') # 기본값을 N으로
    
    def __str__(self):
        return self.nickname # __str__ 을 이용해서 nickname을 문자열로 표현해준다