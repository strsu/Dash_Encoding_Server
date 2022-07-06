from django.shortcuts import render
from django.http import HttpResponse
from .forms import VideoForm
from .video_encoding import h264_encoding 

# Create your views here.
def upload_file(request):
    if request.method == 'POST':
        # form 은 html 코드
        form = VideoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            h264_encoding(request.FILES['file'])
            return HttpResponse('success')
    else:
        form = VideoForm()
        return render(request, 'upload.html', {'form': form})