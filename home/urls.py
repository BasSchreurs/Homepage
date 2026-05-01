from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('api/weather/', views.weather, name='weather'),
    path('api/favorites/', views.favorites, name='favorites'),
    path('api/news/', views.news, name='news'),
]