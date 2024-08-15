from django.urls import path, include
from . import views 
from .views import createTestDatas
from .views import get_chart_data
from .views import mail_view

urlpatterns = [
    # 기기제어, 품질검사, 로그기록 페이지
    path('profile/deviceState/', views.deviceState, name='deviceState'),
    path('profile/qualityInspect/', views.qualityInspect, name='qualityInspect'),
    path('profile/logRecord/', views.logRecord, name='logRecord'),
    
    # get 
    path('test01datas/<int:id>/', views.getTestDatas, name="test01datas"),
    path('test01date/', views.getTestDate, name="test01date"),
    path('test01week/', views.getTestweek, name="test01week"),
    path('test01day/', views.getTestday, name="test01day"),
    path('test01month/', views.getTestmonth, name="test01month"),
    path('test01year/', views.getTestyear, name="test01year"),
    path('getTestday/', views.getTestday, name="getTestday"),
    path('get_daily_classification_counts/', views.get_daily_classification_counts, name='get_daily_classification_counts'),
    # post
    path('create/', createTestDatas, name='createTestDatas'),
    path('images/', include('rest_framework.urls')),
   
    
    # 수치
    path('production_data/', views.get_production_data, name='get_production_data'),


    # 이메일
    path('mail/', mail_view, name='mail'),
    path('mail/send/', views.send_mail, name='send_mail'),
    path('profile/mail', views.mail_view, name='mail'),
    path('profile/qualityInspect/mail', views.mail_view, name='mail'),
    path('profile/deviceState/mail', views.mail_view, name='mail'),
]
