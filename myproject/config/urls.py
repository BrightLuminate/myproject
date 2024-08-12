from django.contrib import admin
from django.urls import path, include
from myapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.signin, name='signin'),
    path('', include('myapp.urls')),  # myapp의 URL 설정을 포함합니다.
    path('profile/', views.profile, name='profile'),
    path('signout/', views.signout, name='signout'),
    # path('signup/', views.signup, name='signup'),
    # path('home/', views.home, name='home'),


]



