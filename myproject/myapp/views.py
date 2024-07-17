from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.http import HttpResponseRedirect
from django.urls import reverse
import logging
import base64
from .forms import ImageUploadForm
from .models import *

#ko
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .ko_serializers import TestDataSerializer


logger = logging.getLogger('django')

def signup(request):
    if request.user.is_authenticated:
        return redirect('/')
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('/')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

def home(request):
    return render(request, 'home.html')

def signin(request):
    if request.user.is_authenticated:
        return render(request, 'home.html')
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('/profile')
        else:
            return render(request, 'login.html', {'form': form, 'msg': 'Error Login'})
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def profile(request):
    return render(request, 'profile.html')

def signout(request):
    logout(request)
    return redirect('/')

def email_view(request):
    return render(request, 'email.html')

def send_mail_view(request):
    return render(request, 'email_format.html')

def sendEmail(request):
    if request.method == 'POST':
        input_receiver = request.POST['inputReceiver']
        input_title = request.POST['inputTitle']
        input_content = request.POST['inputContent']

        content = {'inputReceiver': input_receiver, 'inputTitle': input_title, 'inputContent': input_content}
        msg_html = render_to_string('email_format.html', content)

        msg = EmailMessage(subject=input_title, body=msg_html, from_email="grace71394@gmail.com", to=[input_receiver])
        msg.content_subtype = 'html'

        try:
            msg.send()
            logger.debug("Email sent successfully")
        except Exception as e:
            logger.error("Error: unable to send email")
            logger.error(e)
        return HttpResponseRedirect(reverse('email'))
    else:
        return HttpResponseRedirect(reverse('email'))

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def send_email(request):
    if request.method == 'POST':
        input_receiver = request.POST.get('inputReceiver')
        input_title = request.POST.get('inputTitle')
        input_content = request.POST.get('inputContent')

        context = {
            'inputReceiver': input_receiver,
            'inputTitle': input_title,
            'inputContent': input_content,
        }
        return render(request, 'send.html', context)
    else:
        return render(request, 'email.html')
    
def send_mail(request):
    return render(request, 'send.html')

# 이미지 업로드를 처리하는 뷰

logger = logging.getLogger('django')

# Other view functions remain unchanged

def upload_image(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            name = form.cleaned_data['name']  # Retrieve the name from the form
            image_data = form.cleaned_data['image'].read()
            image_instance = ImageModel(
                name=name,
                image=image_data
            )
            image_instance.save()
            return redirect('image_success', image_id=image_instance.id)
    else:
        form = ImageUploadForm()
    return render(request, 'upload.html', {'form': form})

def image_success(request, image_id):
    image_record = get_object_or_404(ImageModel, id=image_id)
    if image_record and image_record.image:
        image_data = base64.b64encode(image_record.image).decode('utf-8')
    else:
        image_data = None
    return render(request, 'success.html', {'image_data': image_data, 'name': image_record.name})

def show_image(request):
    image_record = ImageModel.objects.first()  # 테스트를 위해 첫 번째 레코드 사용
    print(image_record)
    if image_record:
        image_data = base64.b64encode(image_record.image).decode('utf-8')
        return render(request, 'success.html', {'image_data': image_data, 'name': image_record.name})
    else:
        return render(request, 'success.html', {'image_data': None, 'name': None})
    

# mysql 이미지 한장 나오느방법

def image(request):
    image_records = Images.objects.all()
    print(image_records)
    if image_records.exists():
        return render(request, 'images.html', {
            'image_data': image_records
        })
    else:
        return render(request, 'images.html', {'image_data_list': None})



# ko 시리얼라이즈
@api_view(['GET'])
def getTestDatas(request, id):
    datas = Images.objects.get(id = id)
    serializer = TestDataSerializer(datas, many=False)
    print(serializer.data["image_url"])
    return Response(serializer.data)


