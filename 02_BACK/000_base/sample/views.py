from django.shortcuts import render
from .models import Sample

def sample(request):
    sample = Sample.objects.all()
    return render(request, 'sample/index.html', {
        'samples' : sample,
    })