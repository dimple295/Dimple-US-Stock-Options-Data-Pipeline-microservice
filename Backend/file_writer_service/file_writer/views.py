from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from .handler.DailyDataFileWriter import DailyDataFileWriter
from .handler.RealTimeDataFileWriter import RealTimeDataFileWriter
from .handler.OptionsDataFileWriter import OptionsDataFileWriter
from .handler.HistoricalDataFileWriter import HistoricalDataFileWriter

def store_each_day_data(request):
    try:
        writer = DailyDataFileWriter()
        writer.export_data()
        writer.close_connection()
        return JsonResponse({'status': 'success', 'message': 'Daily data stored successfully.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

def store_last_15min_data(request):
    try:
        writer = RealTimeDataFileWriter()
        writer.export_fifteen_min_data()
        writer.close_connection()
        return JsonResponse({'status': 'success', 'message': 'Real-time data stored successfully.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

def store_option_data(request):
    try:
        writer = OptionsDataFileWriter()
        writer.export_data()
        writer.close_connection()
        return JsonResponse({'status': 'success', 'message': 'Options data stored successfully.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

def store_historical_data(request):
    try:
        writer = HistoricalDataFileWriter()
        writer.export_historical_data()
        writer.close_connection()
        return JsonResponse({'status': 'success', 'message': 'Historical data stored successfully.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
