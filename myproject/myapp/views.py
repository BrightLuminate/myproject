from datetime import datetime, date, timedelta
from calendar import monthrange
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
from django.db.models import Count
from .models import Images
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta,  date
from django.utils.timezone import make_aware
from django.db import connection
from django.http import JsonResponse
from rest_framework.decorators import api_view
from .models import ImageModel  # Assuming this is your model name
from django.shortcuts import render
from datetime import datetime
from django.views import View
from collections import defaultdict
# 이메일
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse
from django.db.models import Count, Q
from .models import Images  # MyAppImage 대신 Images로 수정


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
        return render(request, 'profile.html')
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

# 이메일 
def mail_view(request):
    return render(request, 'mail.html')

def send_mail(request):
    return render(request, 'send.html')

def quality_inspect(request):
    return render(request, 'quality_inspect.html')

def send_email(request):
    if request.method == "POST":
        recipient = request.POST.get('inputReceiver')
        subject = request.POST.get('inputTitle')
        message = request.POST.get('inputContent')

        if recipient and subject and message:
            try:
                send_mail(
                    subject,
                    message,
                    settings.EMAIL_HOST_USER,
                    [recipient],
                    fail_silently=False,
                )
                return render(request, 'send.html')  # 성공 시 페이지 리디렉션
            except Exception as e:
                return HttpResponse(f'Error sending email: {e}')
        else:
            return HttpResponse("All fields are required.")

    return render(request, 'mail.html')


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
    

# mysql 이미지 한장 나오는방법

def image(request):
    image_records = Images.objects.all()
    print(image_records)
    if image_records.exists():
        return render(request, 'images.html', {
            'image_data': image_records
        })
    else:
        return render(request, 'images.html', {'image_data_list': None})

# 기기제어, 품질검사, 로그기록 페이지
def deviceState(request) :
    return render(request,'deviceState.html')

def qualityInspect(request) :
    return render(request,'qualityInspect.html')

def logRecord(request) :
    return render(request,'logRecord.html')

# API 로직 테스트
def show_image(request) :
    return render(request,'show_image.html')

def show_video(request) :
    return render(request,'pos.html')


# create 해주는 api
@api_view(['POST'])
def createTestDatas(request):
    serialzer = TestDataSerializer(data=request.data)
    if serialzer.is_valid():
        serialzer.save()  
        return Response(serialzer.data, status=201)
    return Response(serialzer.errors, status=400)

# id 값을 받아서 read 해주는 api
@api_view(['GET'])
def getTestDatas(request, id):
    datas = Images.objects.get(id = id)
    serializer = TestDataSerializer(datas, many=False)
    print(serializer.data["image_url"])
    return Response(serializer.data)

# 특정 날짜 read 해주는 api
@api_view(['GET'])
def getTestDate(request):
    datas = Images.objects.filter(Detection_Time__date=datetime(2024,7,18))
    serializer = TestDataSerializer(datas, many=True)
    return Response(serializer.data)

def get_first_and_last_date(year, month):
    # 입력된 년도와 월의 첫 날을 구합니다.
    first_day = datetime(year, month, 1)
    
    # 해당 월의 마지막 날을 구합니다.
    # 다음 달의 첫 날을 구하고, 그 날에서 하루를 빼면 현재 월의 마지막 날이 됩니다.
    if month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year

    next_month_first_day = datetime(next_year, next_month, 1)
    last_day = next_month_first_day - timedelta(days=1)
    
    return first_day, last_day


# 일간 
@api_view(['GET'])
def getTestday(request):
    today = datetime.today().date()
    # print(today.year)
    # print(today.month)
    first_date, last_date = get_first_and_last_date(today.year, today.month)
    print(f"{today.year}-{today.month:02d}의 첫 날짜: {first_date.date()}")
    print(f"{today.year}-{today.month:02d}의 마지막 날짜: {last_date.date()}")
    datas = Images.objects.filter(Detection_Time__range=(first_date.date(), last_date.date()))
    serializer = TestDataSerializer(datas, many=True)
    return Response(serializer.data)

# 주간 데이터 API 엔드포인트
@api_view(['GET'])
def getTestweek(request):
    today = datetime.today().date()
    start_date = today - timedelta(days=today.weekday())
    end_date = start_date + timedelta(days=6)
    start_date = datetime.combine(start_date, datetime.min.time())
    end_date = datetime.combine(end_date, datetime.max.time())
    datas = Images.objects.filter(Detection_Time__range=(start_date, end_date))
    serializer = TestDataSerializer(datas, many=True)
    return Response(serializer.data)

# 월간 데이터 API 엔드포인트
@api_view(['GET'])
def getTestmonth(request):
    today = datetime.today().date()
    start_date = datetime.combine(today.replace(year=1, month=1,day=1), datetime.min.time())
    print(start_date)
    if today.month == 12:
        end_date = datetime.combine(today.replace(year=today.year + 1, month=1, day=1), datetime.min.time()) - timedelta(seconds=1)
    else:
        end_date = datetime.combine(today.replace(month=today.month + 1, day=1), datetime.min.time()) - timedelta(seconds=1)
    datas = Images.objects.filter(Detection_Time__range=(start_date, end_date))
    serializer = TestDataSerializer(datas, many=True)
    return Response(serializer.data)

# 년간 데이터 API 엔드포인트
@api_view(['GET'])
def getTestyear(request):
    today = datetime.today().date()
    start_date = datetime.combine(today.replace(year=2020, month=1, day=1), datetime.min.time())
    end_date = datetime.combine(today.replace(year=today.year + 1, month=1, day=1), datetime.min.time()) - timedelta(seconds=1)
    datas = Images.objects.filter(Detection_Time__range=(start_date, end_date))
    serializer = TestDataSerializer(datas, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_chart_data(request):
    defective_count = Images.objects.filter(category='defective').count()
    normal_count = Images.objects.filter(category='normal').count()

    return Response({'defective': defective_count, 'normal': normal_count})

#  정상률 불량률 수치 
def get_production_data(request):
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    # 이번 달의 모든 데이터를 가져옵니다.
    total_produced = Images.objects.filter(
        Detection_Time__year=current_year,
        Detection_Time__month=current_month
    ).count()
    
    # 양품 개수
    current_production = Images.objects.filter(
        Detection_Time__year=current_year,
        Detection_Time__month=current_month,
        classification='ok_front'
    ).count()
    
    # 불량 개수
    defective_count = Images.objects.filter(
        Detection_Time__year=current_year,
        Detection_Time__month=current_month,
        classification='def_front'
    ).count()
    
    target_production = 10000  # 이 값을 동적으로 설정할 수 있습니다.
    current_production_rate = (current_production / target_production) * 100 if target_production > 0 else 0
    defect_rate = (defective_count / total_produced) * 100 if total_produced > 0 else 0
    
    data = {
        'total_produced': total_produced,
        'current_production': current_production,
        'defective_count': defective_count,
        'current_production_rate': current_production_rate,
        'defect_rate': defect_rate,
    }
    
    return JsonResponse(data)



# 도넛
def get_daily_classification_counts(request):
    today = date.today()
    defective_count = Images.objects.filter(classification='def_front', Detection_Time__date=today).count()
    normal_count = Images.objects.filter(classification='ok_front', Detection_Time__date=today).count()

    data = {
        'chart_data': {
            'defective': defective_count,
            'normal': normal_count
        }
    }

    return JsonResponse(data)

def quality_inspect(request):
    # GET 요청에서 img 파라미터를 받음
    image_url = request.GET.get('img')

    if image_url:
        # 받은 이미지 URL을 처리하는 로직을 여기에 작성
        # 예를 들어, 이미지 분석, 검증, 데이터베이스에 기록 등
        print(f"Received image URL: {image_url}")

        # 처리가 완료된 후 렌더링할 페이지로 이동
        return render(request, 'quality_inspect.html', {'image_url': image_url})
    else:
        # img 파라미터가 없는 경우 오류 처리
        return render(request, 'error.html', {'error': 'No image URL provided'})
