from django.shortcuts import render
from django.http import HttpResponse

from .models import Map

# Create your views here.
def index(request):
    map = Map(20, 20)

    return render(request, 'pathfinder/index.html', {
        'map': map
    })

def greet(request, name):
    return HttpResponse(f"Hello, {name}")

def speak(request, content):
    return HttpResponse(f"Speak {content}")