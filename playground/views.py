from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
# request -> response // aka request handler

def say_hello(request):
    x,y = 1,2
    return render(request, 'hello.html', {'name' : "Jimmy"})