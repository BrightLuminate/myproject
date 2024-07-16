from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello, Pybo!")
# Create your views here.
