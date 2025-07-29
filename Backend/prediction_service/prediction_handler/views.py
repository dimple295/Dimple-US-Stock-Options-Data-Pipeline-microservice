from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
import pandas as pd
import numpy as np
import torch
from .src.model import TransformerLSTM
from .src.preprocess import fetch_data, preprocess_inference_data
from .src.train import train_model
from .src.symbols import getSymbolList
import os
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

SYMBOLS = getSymbolList()

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = TransformerLSTM(num_features=len(SYMBOLS) * 5, num_stocks=len(SYMBOLS)).to(device)
model.load_state_dict(torch.load(os.getenv("MODEL_PATH", "/app/models/transformer_lstm.pth")))
model.eval()
scaler = np.load(os.getenv("SCALER_PATH", "/app/models/scaler.npy"), allow_pickle=True).item()

@require_GET
def predict(request):
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(hours=2)
        df = fetch_data(os.getenv("DATA_API_URL", "http://data_api_service:8006/api/realtime_data/"), 
                        start_date, end_date, interval="1min", source="influxdb")

        X = preprocess_inference_data(df, SYMBOLS, scaler, seq_length=120, is_1min=True)
        X_tensor = torch.tensor(X, dtype=torch.float32).to(device)

        with torch.no_grad():
            pred = model(X_tensor)
            pred = pred.cpu().numpy()[0]

        response = {
            'predictions': {
                symbol: pred[:, i].tolist() for i, symbol in enumerate(SYMBOLS)
            }
        }
        return JsonResponse(response)
    except Exception as e:
        logging.error(f"Error in prediction: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@require_POST
def fine_tune(request):
    try:
        data_api_url = os.getenv("DATA_API_URL", "http://data_api_service:8006/api/realtime_data/")
        train_model(data_api_url, is_fine_tune=True)
        global model
        model.load_state_dict(torch.load(os.getenv("MODEL_PATH", "/app/models/transformer_lstm.pth")))
        model.eval()
        logging.info("Model fine-tuned successfully")
        return JsonResponse({"status": "Model fine-tuned successfully"})
    except Exception as e:
        logging.error(f"Error in fine-tuning: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@require_GET
def health(request):
    return JsonResponse({"status": "healthy"})