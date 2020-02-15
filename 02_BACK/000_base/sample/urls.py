from django.urls import path
from .views import sample

app_name = 'sample'

urlpatterns = [
    path('', sample, name='sample_list')
]