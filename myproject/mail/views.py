from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.urls import reverse
import logging

logger = logging.getLogger('django')

def email_view(request):
    return render(request, 'email.html')

def send_mail_view(request):
    if request.method == 'POST':
        return sendEmail(request)
    else:
        return render(request, 'email_format.html')

def sendEmail(request):
    if request.method == 'POST':
        inputReceiver = request.POST['inputReceiver']
        inputTitle = request.POST['inputTitle']
        inputContent = request.POST['inputContent']

        content = {'inputReceiver': inputReceiver, 'inputTitle': inputTitle, 'inputContent': inputContent}
        msg_html = render_to_string('email_format.html', content)

        msg = EmailMessage(subject=inputTitle, body=msg_html, from_email="grace71394@gmail.com", to=[inputReceiver])
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
def send_mail(request):
    return render(request, 'send.html')