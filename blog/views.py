from django.http.response import HttpResponse
from django.shortcuts import render

# Create your views here.
def blog_home(request):
    return HttpResponse('blog home')
