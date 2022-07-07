from django.shortcuts import render
from django.http import HttpResponse
from .forms import VideoForm
from .video import message

# Create your views here.
def upload_file(request):
    if request.method == 'POST':
        # form 은 html 코드
        form = VideoForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save()
            message(instance.file.name.split('/')[-1])
            return HttpResponse('success')
    else:
        form = VideoForm()
        return render(request, 'upload.html', {'form': form})