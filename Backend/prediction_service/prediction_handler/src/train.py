import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader
from src.preprocess import fetch_data, preprocess_data
from src.model import TransformerLSTM
import os
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO, format='%(asctime)s -%(levelname)s - %(message)s')
from symbols import getSymbolList

SYMBOLS = getSymbolList()

def train_model(data_api_url, is_fine_tune=False):
    try:
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        num_features = len(SYMBOLS) * 5
        model = TransformerLSTM(num_features=num_features, num_stocks=len(SYMBOLS)).to(device)

        if is_fine_tune:
            model.load_state_dict(torch.load('app/models/transformer_lstm.pth'))
            logging.info("Loaded existing model for fine-tuning")
            end_date = datetime.now(datetime.timetz.utc)
            start_date = end_date - timedelta(days=7)
            interval = "1min"
            source = "influxdb"
            lr = 0.0001
            num_epochs = 10

        else:
            end_date = datetime.now(datetime.timetz.utc)
            start_date = end_date - timedelta(days=7)
            interval = "2min"
            source = "csv"
            lr = 0.001
            num_epochs = 50

        df = fetch_data(data_api_url, start_date, end_date, interval=interval, source=source)
        X_train, y_train, X_val, y_val, X_test, y_test, indices_test, scaler, feature_columns = preprocess_data(df, SYMBOLS, seq_length=120, forecast_horizon=240, is_1min=(interval == "1min"))

        train_dataset = TensorDataset(
            torch.tensor(X_train, dtype=torch.float32).to(device),
            torch.tensor(y_train, dtype=torch.float32).to(device)
        )
        train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)

        criterion = nn.MSELoss()
        optimizer = optim.Adam(model.parameters(), lr=lr)
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, 'min', patience=3, factor=0.5)
        best_val_loss = float('inf')
        for epoch in range(num_epochs):
            model.train()
            train_loss = 0
            for X_batch, y_batch in train_loader:
                optimizer.zero_grad()
                outputs = model(X_batch)
                loss = criterion(outputs, y_batch)
                loss.backward()
                optimizer.step()
                train_loss += loss.item()
            
            train_loss /= len(train_loader)

            model.eval()
            with torch.no_grad():
                val_outputs = model(torch.tensor(X_val, dtype=torch.float32).to(device))
                val_loss = criterion(val_outputs, torch.tensor(y_val, dtype=torch.float32).to(device))
            
            scheduler.step(val_loss)

            logging.info(f'Epoch {epoch+1}, Train Loss: {train_loss:.4f}, Val loss: {val_loss:.4f}')
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                torch.save(model.state_dict(), '/app/models/transformer_lstm.pth')
                logging.info("Saved best model")

        
        model.load_state_dict(torch.load('/app/models/transformer_lstm.pth'))
        model.eval()
        with torch.no_grad():
            test_outputs = model(torch.tensor(X_test, dtype=torch.float32).to(device))
            test_loss = criterion(test_outputs, torch.tensor(y_test, dtype=torch.float32).to(device))
            rmse = torch.sqrt(test_loss).item()
            logging.info(f'Test RMSE: {rmse:.4f}')

            y_true_diff = y_test[:, 1:, :] - y_test[:, :-1, :]
            y_pred_diff = test_outputs.cpu().numpy()[:, 1:, :] - test_outputs.cpu().numpy()[:,:-1,:]
            dir_acc = (y_true_diff * y_pred_diff > 0).mean() * 100
            logging.info(f'Directional Accuracy: {dir_acc:.2f}%')

                              
    except Exception as e:
        logging.error(f"Error in training: {str(e)}")
        raise


if __name__ == "__main__":
    data_api_url = os.getenv("DATA_API_URL", "http://data_api_service:8006/api/realtime_data/")
    train_model(data_api_url, is_fine_tune=False)
