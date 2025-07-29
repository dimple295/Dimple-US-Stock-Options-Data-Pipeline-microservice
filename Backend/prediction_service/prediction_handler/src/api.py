from fastapi import FastAPI, HTTPException
import pandas as pd
import numpy as np
import torch
from src.model import TransformerLSTM
from src.preprocess import fetch_data, preprocess_inference_data
from src.train import train_model
import os
import logging
from datetime import datetime, timedelta
from symbols import getSymbolList
app = FastAPI()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

SYMBOLS = getSymbolList()

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = TransformerLSTM(num_features=len(SYMBOLS) * 5, num_stocks=len(SYMBOLS)).to(device)
model.load_state_dict(torch.load(os.getenv("MODEL_PATH", "/app/models/transformer_lstm.pth")))
model.eval()
scaler = np.load(os.getenv("SCALER_PATH", "/app/models/scaler.npy"), allow_pickle=True).item()

@app.get("/predict")
async def predict():
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
        return response

    except Exception as e:
        logging.error(f"Error in prediction: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/fine_tune")
async def fine_tune():
    try:
        data_api_url = os.getenv("DATA_API_URL", "http://data_api_service:8006/api/realtime_data/")
        train_model(data_api_url, is_fine_tune=True)
        global model
        model.load_state_dict(torch.load(os.getenv("MODEL_PATH", "/app/models/transformer_lstm.pth")))
        model.eval()
        logging.info("Model fine-tuned successfully")
        return {"status": "Model fine-tuned successfully"}
    except Exception as e:
        logging.error(f"Error in fine-tuning: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "healthy"}