import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import talib
import requests
import logging
from datetime import datetime, timedelta

from symbols import getSymbolList

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

SYMBOLS = getSymbolList()

def fetch_data(data_api_url, start_date, end_date, interval="2min", source="csv"):
    try:
        if source == "csv":
            df = pd.read_csv("/app/data/stock_data_realtime.csv")
            df['Datetime'] = pd.to_datetime(df['Datetime'])
            df = df[(df['Datetime'] >= start_date) & (df['Datetime'] <= end_date)]
            df = df[df['Symbol'].isin(SYMBOLS)]
            return df.sort_values(['Datetime', 'Symbol'])
        else:
            params = {
                "symbols": ",".join(SYMBOLS),
                "start_date": start_date.strftime("%Y-%m-%d %H:%M:%S"),
                "end_date": end_date.strftime("%Y-%m-%d %H:%M:%S"),
                "interval": interval,
                "source": source
            }
            response = requests.get(f"{data_api_url}", params=params)
            response.raise_for_status()
            data = response.json()
            df = pd.DataFrame(data)
            df['Datetime'] = pd.to_datetime(df['Datetime'])
            return df.sort_values(['Datetime', 'Symbol'])
        
    except Exception as e:
        logging.error(f"Error while fetching data in preprocessor prediction service: {str(e)}")
        raise


def resample_to_1min(df):
    try:
        dfs = []
        for symbol in SYMBOLS:
            symbol_df = df[df['Symbol'] == symbol].set_index('Datetime')
            symbol_df = symbol_df.resample('1min').ffill()
            symbol_df['Symbol'] = symbol
            symbol_df = symbol_df.reset_index()
            dfs.append(symbol_df)
        
        return pd.concat(dfs).sort_values(['Datetime', 'Symbol'])
    except Exception as e:
        logging.error(f"Error in resampling data: {str(e)}")
        raise

def preprocess_data(df, symbols, seq_length=120, forecast_horizon=240, is_1min=False):
    try:
        if not is_1min:
            df = resample_to_1min(df)

        pivot_close = df.pivot(index='Datetime', columns='Symbol', values='Close')
        pivot_volume = df.pivot(index='Datetime', columns='Symbol', values='Volume')
        missing_symbols = [s for s in symbols if s not in pivot_close.columns]
        if missing_symbols:
            raise ValueError(f"Missing symbols in data: {missing_symbols}")
        log_returns = np.log(pivot_close / pivot_close.shift(1)).dropna()

        features = []
        for symbol in symbols:
            close = pivot_close[symbol].values
            volume = pivot_volume[symbol].values
            rsi = talib.RSI(close, timeperiod=14)
            macd, _, _ = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
            bb_upper, bb_middle, bb_lower = talib.BBANDS(close, timeperiod=20)
            fearure_df = pd.DataFrame({
                f'{symbol}_log_return': log_returns[symbol],
                f'{symbol}_rsi': rsi,
                f'{symbol}_macd': macd,
                f'{symbol}_bb_width': (bb_upper - bb_lower) / bb_middle,
                f'{symbol}_volume': volume
            }, index=pivot_close.index)
            features.append(fearure_df)
        
        fearure_df = pd.concat(features, axis=1).dropna()
        logging.info("Features engineered")

        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(fearure_df)
        scaled_df = pd.DataFrame(scaled_features, index=fearure_df.index, columns=fearure_df.columns)

        np.save('/app/models/scaler.npy', scaler)

        def create_sequences(data, seq_length, forecast_horizon, num_stocks):
            X, y = [], []
            for i in range(len(data) - seq_length - forecast_horizon):
                X.append(data[i:i + seq_length])
                y.append(data[i + seq_length:i + seq_length + forecast_horizon,:num_stocks])

            return np.array(X), np.array(y), scaled_df.index[seq_length + forecast_horizon:]
        
        X, y, indices = create_sequences(scaled_df.values, seq_length, forecast_horizon, len(symbols))
        logging.info(f"Created {len(X)} sequences with input shape {X.shape} and output shape {y.shape}")

        train_size = int(0.8 * len(X))
        val_size = int(0.1 * len(X))
        X_train, y_train = X[:train_size], y[:train_size]
        X_val, y_val = X[train_size:train_size + val_size], y[train_size:train_size + val_size]
        X_test, y_test = X[train_size + val_size:], y[train_size + val_size:]
        indices_test = indices[train_size + val_size:]

        return X_train, y_train, X_val, y_val, X_test, y_test, indices_test, scaler, scaled_df.columns
    except Exception as e:
        logging.error(f"Error in processing: {str(e)}")
        raise

def preprocess_inference_data(df, symbols, scaler, seq_length=120, is_1min=True):
    try:
        if len(df) < seq_length:
            raise ValueError(f"Input data must have at least {seq_length} rows")
        
        if not is_1min:
            df = resample_to_1min(df)
        
        pivot_close = df.pivot(index='Datetime', columns='Symbol', values='Close')
        pivot_volume = df.pivot(index='Datetime', columns='Symbol', values='Volume')
        missing_symbols = [s for s in symbols if s not in pivot_close.columns]
        if missing_symbols:
            raise ValueError(f"Missing symbols in inference data: {missing_symbols}")
        log_returns = np.log(pivot_close / pivot_close.shift(1)).dropna()

        features = []
        for symbol in symbols:
            close = pivot_close[symbol].values
            volume = pivot_volume[symbol].values
            rsi = talib.RSI(close, timeperiod=14)
            macd, _, _ = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
            bb_upper, bb_middle, bb_lower = talib.BBANDS(close, timeperiod=20)
            fearure_df = pd.DataFrame({
                f'{symbol}_log_return': log_returns[symbol],
                f'{symbol}_rsi': rsi,
                f'{symbol}_macd': macd,
                f'{symbol}_bb_width': (bb_upper - bb_lower) / bb_middle,
                f'{symbol}_volume': volume
            }, index=pivot_close.index)
            features.append(fearure_df)
        
        fearure_df = pd.concat(features, axis=1).dropna()
        fearure_df = fearure_df.iloc[-seq_length:]
        scaled_features = scaler.transform(fearure_df)
        return np.array([scaled_features])
    
    except Exception as e:
        logging.error(f"Error in inference preprocessing: {str(e)}")
        raise


