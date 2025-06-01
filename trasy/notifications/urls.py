# notifications/urls.py
from django.urls import path
from .views import notifications_stream

urlpatterns = [
    path('notifications/', notifications_stream, name='notifications_stream'),
]