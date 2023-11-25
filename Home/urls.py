from django.urls import path
from . import views

urlpatterns = [
    path('', views.Home, name='Home'),
    path('capture_frame/', views.capture_video_frame, name='capture_frame'),
]