from django.urls import path
from . import views


urlpatterns = [
    path('store_each_day_data/', views.store_each_day_data, name='store_each_day_data'),
    path('store_last_15min_data/', views.store_last_15min_data, name='store_last_15min_data'),
    path('store_option_data/', views.store_option_data, name='store_option_data'),
    path('store_historical_data/', views.store_historical_data, name='store_historical_data'),
]