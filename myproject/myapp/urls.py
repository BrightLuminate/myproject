from django.urls import path, include
from . import views 
from .views import createTestDatas

urlpatterns = [
    # 테스트 파일
    # path('upload/', views.upload_image, name='upload_image'),
    # path('success/', views.image_success, name='image_success'),
    # path('image_success/<int:image_id>/', views.image_success, name='image_success'),
    # path('show_image/', views.show_image, name='show_image'),
    # path('images/', views.image, name='images'),

    # 기기제어, 품질검사, 로그기록 페이지
    path('profile/deviceState/', views.deviceState, name='deviceState'),
    path('profile/qualityInspect/', views.qualityInspect, name='qualityInspect'),
    path('profile/logRecord/', views.logRecord, name='logRecord'),
    

    # Test
    
    #  페이징
    path('show_image/', views.show_image, name='show_image'),
    #  스크롤
    path('pos/', views.show_video, name='pos'),


    # get 
    path('test01datas/<int:id>/', views.getTestDatas, name="test01datas"),
    path('test01date/', views.getTestDate, name="test01date"),
    path('test01week/', views.getTestweek, name="test01week"),
    path('test01month/', views.getTestmonth, name="test01month"),
    path('test01year/', views.getTestyear, name="test01year"),

    # post
    path('create/', createTestDatas, name='createTestDatas'),
    path('images/', include('rest_framework.urls')),
]
