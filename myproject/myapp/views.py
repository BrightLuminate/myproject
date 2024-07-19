from datetime import datetime
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
from .serializers import TestDataSerializer
from dateutil import parser


logger = logging.getLogger('django')

# 로그인 
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

# 이메일 
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

def email_view(request):
    return render(request, 'email.html')

def send_mail_view(request):
    return render(request, 'email_format.html')
    
# 이메일 보내는것 
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



# API 로직

# id 값을 받아서 read 해주는 api
@api_view(['GET'])
def getTestDatas(request, id):
    datas = Images.objects.get(id = id)
    serializer = TestDataSerializer(datas, many=False)
    print(serializer.data["image_url"])
    return Response(serializer.data)

# create 해주는 api
@api_view(['POST'])
def createTestDatas(request):
    serialzer = TestDataSerializer(data=request.data)
    if serialzer.is_valid():
        serialzer.save()  
        return Response(serialzer.data, status=201)
    return Response(serialzer.errors, status=400)


# 특정 날짜 read 해주는 api
@api_view(['GET'])
def getTestDate(request):

    datas = Images.objects.filter(Detection_Time__date=datetime(2024,7,18))
    serializer = TestDataSerializer(datas, many=True)

    return Response(serializer.data)
