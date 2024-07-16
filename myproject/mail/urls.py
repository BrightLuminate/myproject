from django.urls import path
from .views import email_view, send_mail_view,sendEmail
from . import  views
urlpatterns = [
    path('', email_view, name='email'),
    path('mail/send/', views.send_mail, name='send_mail'),
]

