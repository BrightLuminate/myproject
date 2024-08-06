from django.contrib import admin
from django.urls import path, include
from myapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('mail/', include('mail.urls')),
    path('send/', views.sendEmail, name='send'),
    path('', views.signin, name='signin'),
    path('signout/', views.signout, name='signout'),
    path('profile/', views.profile, name='profile'),
    path('mail/send/', views.send_mail, name='send_mail'),
    path('', include('myapp.urls')),  # myapp의 URL 설정을 포함합니다.
]
