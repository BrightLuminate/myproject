from django.urls import path, include
from . import views 
from .views import createTestDatas

urlpatterns = [
    path('images/', views.image, name='images'),
    
    # ko
    path('test01datas/<int:id>/', views.getTestDatas, name="test01datas"),
    path('test01date/', views.getTestDate, name="test01date"),

    # post
    path('create/', createTestDatas, name='createTestDatas'),
    path('images/', include('rest_framework.urls')),
]
