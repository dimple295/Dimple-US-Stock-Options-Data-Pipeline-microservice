from django.urls import path
from . import views

urlpatterns = [
    path('predict/', views.predict, name='predict'),
    path('fine_tune/', views.fine_tune, name='fine_tune'),
    path('health/', views.health, name='health'),
]