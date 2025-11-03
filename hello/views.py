from django.shortcuts import render
from django.conf import settings
from hello.forms import UploadFileForm
from django.core.files.storage import default_storage
from django.http import HttpResponse
from django.core.files.base import ContentFile
from io import BytesIO
import os

from PIL import Image, ImageOps,ImageFilter

def download_file(request, filename):
    file_path = f"media/{filename}"
    
    if not default_storage.exists(file_path):
        return HttpResponse("File not found.", status=404)
    
    with default_storage.open(file_path, 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


# Create your views here.
def applyfilter(image_bytes, preset, filename):
    im = Image.open(image_bytes)
    im = im.convert("RGB")
    if preset == 'gray':
        im = ImageOps.grayscale(im)
    if preset == 'edge':
        im = ImageOps.grayscale(im)
        im = im.filter(ImageFilter.FIND_EDGES)
    if preset == 'solar':
        im = ImageOps.solarize(im, threshold=80)
    if preset == 'poster':
        im = ImageOps.posterize(im, 3)
    if preset == 'blur':
        im = im.filter(ImageFilter.BLUR)
        
    if preset == 'sepia':
        sepia = []
        r, g, b = (239, 224, 185)
        for i in range(255):
            sepia.extend((int(r*i/255), int(g*i/255), int(b*i/255)))
        im = im.convert("L")
        im.putpalette(sepia)
        im = im.convert("RGB")
    
    output = BytesIO()
    im.save(output, format='JPEG')
    output.seek(0)
    output.name = getattr(filename, 'name', 'filtered.jpg')
    return output

def home(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            preset = request.POST.get('preset')
            file = request.FILES['myfilefield']
            image_bytes = file.read()
            file.seek(0) 
            
            original_key = f"media/{file.name}"
            default_storage.save(original_key, file)
            
            filtered_file = applyfilter(BytesIO(image_bytes), preset, file.name)
            basename, ext = os.path.splitext(file.name)
            filtered_file.name = f"{basename}_out.jpg"
            filtered_key = f"media/{filtered_file.name}"
            filtered_path = default_storage.save(filtered_key, ContentFile(filtered_file.read()))
            
            if hasattr(default_storage, 'url'):
                filtered_url = default_storage.url(filtered_path)
            else:
                filtered_url = os.path.join(settings.MEDIA_URL, filtered_path)
            
            return render(request, 'hello/process.html', {
		'outputfileURL': filtered_url,
		'outputfileName': filtered_file.name
	})
    else:
        form = UploadFileForm()
    return render(request, 'hello/index.html', {'form': form})

def process(request):
    return render(request, 'hello/process.html', {})
