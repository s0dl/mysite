from django.shortcuts import render
from django.conf import settings
from hello.forms import UploadFileForm
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from io import BytesIO
import os

from PIL import Image, ImageOps,ImageFilter

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
            
            return render(request, 'hello/process.html', {'outputfileURL': filtered_url})
    else:
        form = UploadFileForm()
    return render(request, 'hello/index.html', {'form': form})

def process(request):
    return render(request, 'hello/process.html', {})

"""
from django.shortcuts import render
from hello.forms import UploadFileForm
from PIL import Image, ImageOps,ImageFilter


# Create your views here.
def applyfilter(filename, preset):
    inputfile = '/media/' + filename
    f = filename.split('.')
    outputfilename = f[0] + '_out.jpg'
    
    outputfile = 'templates/static/output' + outputfilename
    
    im = Image.open(inputfile)
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
            sepia.extend((r*i/255, g*i/255, b*i/255))
        im = im.convert("L")
        im.putpalette(sepia)
        im = im.convert("RGB")
    
    im.save(outputfile)
    return outputfilename
  
def handle_uploaded_file(f, preset):
    uploadfilename = '/media/' + f.name
    with open(uploadfilename, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    
    outputfilename = applyfilter(f.name, preset)
    return outputfilename

def home(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            preset = request.POST.get('preset')
            outputfilename = handle_uploaded_file(request.FILES['myfilefield'], preset)
            return render(request, 'hello/process.html', {'outputfile': outputfilename})
    else:
        form = UploadFileForm()
    return render(request, 'hello/index.html', {'form': form})

def process(request):
    return render(request, 'hello/process.html', {})
  """