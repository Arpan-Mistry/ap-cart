from django import urls
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('',views.shop_home,name='shop home'),
    path('about/',views.shop_about,name='about'),
    path('tracker/',views.shop_tracker,name='tracker'),
    path('contact/',views.shop_contact,name='contact'),
    path('search/',views.shop_search,name='search'),
    path('products/<int:myid>/', views.productView, name='ProductView'),
    path('checkout/',views.shop_checkout,name='checkout'),
    path("handlepayment/", views.handlerequest, name="HandleRequest"),
]