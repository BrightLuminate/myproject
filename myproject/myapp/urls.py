from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_image, name='upload_image'),
    path('success/', views.image_success, name='image_success'),
    path('image_success/<int:image_id>/', views.image_success, name='image_success'),
    path('show_image/', views.show_image, name='show_image'),
    path('images/', views.image, name='images'),
    # ko
    path('test01datas/<int:id>/', views.getTestDatas, name="test01datas"),
    path('test01date/', views.getTestDate, name="test01date"),
]