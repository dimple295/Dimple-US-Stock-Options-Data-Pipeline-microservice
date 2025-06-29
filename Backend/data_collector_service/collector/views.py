from datetime import datetime, timedelta, timezone
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from datetime import datetime
import yfinance as yf
import pandas as pd
import logging
import requests
import os
import json
import time

from collector.utils.create_batch import create_batches
from collector.utils.symbols import symbols
from collector.kafka import kafkaConfig

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Kafka Producer setup
producer = kafkaConfig.create_producer()
# kafkaConfig.create_kafka_topics()

def fetch_each_day_data(request):
    """
    Fetches daily data for all symbols in batches and pushes each to Kafka.
    One batch per minute (batch size = 8).
    """

    logger.info(f"Scheduler Scheduled Job for Fetching Daily Data")

    URL = "https://api.twelvedata.com/time_series"
    api_key = os.getenv('TWELVE_DATA_API_KEY')

    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    tomorrow = (datetime.now(timezone.utc) + timedelta(days=1)).strftime('%Y-%m-%d')
    
    tod = "2025-06-02"    
    tomms = "2025-06-03"

    logger.info(f"today: {today}")
    logger.info(f"tomorrow: {tomorrow}")

    all_results = []

    for batch in create_batches(symbols, batch_size=8):
        batch_result = {}

        for symbol in batch:
            params = {
                "symbol": symbol,
                "interval": "1day",
                "start_date": tod,
                "end_date": tomms,
                "apikey": api_key,
                "outputsize": 1
            }

            response = requests.get(URL, params=params)
            logger.info(f"Response: {response}")

            if response.status_code == 200:
                data = response.json()

                if data.get('code') == 400:

                    logger.info(f"400 Error: {data}")

                    batch_result[symbol] = {"error": "No data available"}
                    continue
                else:
                    batch_result[symbol] = data
                    # Push to Kafka

                    data_value=json.dumps(data).encode('utf-8')

                    logger.info(f"Passing fetched data to daily-data Producer: {data_value}")

                    producer.produce(settings.KAFKA_TOPICS['daily'], value=data_value)
                    producer.flush()
            else:
                batch_result[symbol] = {
                    "error": f"Failed: {response.status_code}",
                    "details": response.text
                }
        
        all_results.append(batch_result)

        time.sleep(60)  # Wait 1 second before next batch

    return JsonResponse({
        "status": "success",
        "message": "Fetched and pushed all batches",
        "data": all_results
    }, status=200)


def fetch_last_15min_data(request):
    """
    Fetches last 15 minutes data for multiple symbols (in batches of 8) from Twelve Data API.
    """
    logger.info(f"Scheduler Scheduled Job for Fetching 15 minute interval Data")

    URL = "https://api.twelvedata.com/time_series"
    api_key = os.getenv('TWELVE_DATA_API_KEY')
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    tomorrow = (datetime.now(timezone.utc) + timedelta(days=1)).strftime('%Y-%m-%d')

    logger.info(f"today: {today}")
    logger.info(f"tomorrow: {tomorrow}")

    all_data = []

    tod = "2025-06-02"    
    tomms = "2025-06-03"

    for batch in create_batches(symbols, batch_size=8):
        batch_data = {}
        for symbol in batch:
            params = {
                "symbol": symbol,
                "interval": "1min",
                "start_date": tod,
                "end_date": tomms,
                "apikey": api_key,
                "outputsize": 15
            }

            response = requests.get(URL, params=params)

            logger.info(f"Response: {response}")

            if response.status_code == 200:
                data = response.json()

                if data.get('code') == 400:
                    logger.info(f"400 Error: {data}")

                    batch_data[symbol] = {"error": "No data available"}
                    continue
                else:
                    batch_data[symbol] = data

                    data_value=json.dumps(data).encode('utf-8')

                    logger.info(f"Passing fetched data to 15min-data Producer: {data_value}")

                    producer.produce(settings.KAFKA_TOPICS['15min'], value=data_value)
                    producer.flush()
            else:
                batch_data[symbol] = {
                    "error": f"Failed: {response.status_code}",
                    "details": response.text
                }

        all_data.append(batch_data)
        time.sleep(60)  # Optional delay: wait 1 min before next batch

    return JsonResponse({
        "status": "success",
        "message": "Fetched 5-minute data for all symbols in batches",
        "data": all_data
    }, status=200)

def fetch_option_data(request):
    """
    Fetches options data for multiple symbols (in batches of 8) from Yahoo Finance.
    """
    today = datetime.now().date()
    # today = datetime.strptime("2025-06-16", "%Y-%m-%d").date()
    # cutoff = datetime.strptime("2025-08-16", "%Y-%m-%d").date()
    cutoff = today + timedelta(days=65)
    full_result = []

    logger.info(f"today: {today}")
    logger.info(f"cutoff: {cutoff}")

    for batch in create_batches(symbols, batch_size=8):
        batch_result = {}
        for symbol in batch:
            try:

                ticker = yf.Ticker(symbol)
                logger.info(f"[{symbol}] - Ticker object created.")
                
                try:
                    expirations = ticker.options
                    logger.info(f"[{symbol}] - expiration date fetched")
                except Exception as e:
                    logger.error(f"[{symbol}] - Error creating expiration update to new yfinance version: {e}", exc_info=True)
                    continue
                
                if not expirations:
                    batch_result[symbol] = {
                        "status": "error",
                        "message": "No expiration dates found."
                    }
                    continue

                logger.info(f"expirations: {expirations}")

                valid_expirations = []
                for exp in expirations:
                    try:
                        exp_date = datetime.strptime(exp, "%Y-%m-%d").date()
                        if today <= exp_date <= cutoff:
                            valid_expirations.append(exp)
                    except Exception as e:
                        print(f"Invalid expiration format for {symbol}: {exp} — {e}")

                if not valid_expirations:
                    batch_result[symbol] = {
                        "status": "no_data",
                        "message": "No valid expirations in next 60 days."
                    }
                    continue
                
                logger.info(f"valid_expirations: {valid_expirations}")

                all_calls = []
                all_puts = []
                for expiry in valid_expirations:
                    try:
                        opt_chain = ticker.option_chain(expiry)
                        calls = opt_chain.calls.copy()
                        calls["expirationDate"] = expiry
                        all_calls.append(calls)
                        puts = opt_chain.puts.copy()
                        puts["expirationDate"] = expiry
                        all_puts.append(puts)
                        print(f"{symbol}: Fetched {len(calls)} calls for {expiry}")
                    except Exception as e:
                        print(f"{symbol}: Error fetching data for {expiry}: {e}")

                logger.info(f"all_calls: {all_calls}")

                if all_calls:
                    calls_df = pd.concat(all_calls, ignore_index=True)
                    calls_df["type"] = "calls"
                    if not calls_df.empty:
                        # Convert timestamp columns to string first
                        for col in ['lastTradeDate', 'expirationDate']:
                            if col in calls_df.columns:
                                calls_df[col] = calls_df[col].astype(str)

                        # Now convert DataFrame to list of dicts
                        data_batch = calls_df.to_dict(orient='records')

                        # Serialize data_batch with json.dumps and encode to bytes for Kafka
                        data_value = json.dumps(data_batch).encode('utf-8')
                        logger.info(f"Passing fetched data to option-data Producer: {data_value}")
                        producer.produce(settings.KAFKA_TOPICS['options'], value=data_value)
                        producer.flush()
                        
                        batch_result[symbol] = {
                            "status": "success",
                            "message": f"{len(data_batch)} option records",
                            "data": data_batch
                        }
                    else:
                        batch_result[symbol] = {
                            "status": "warning",
                            "message": "No option data found"
                        }
                else:
                    batch_result[symbol] = {
                        "status": "warning",
                        "message": "No valid expirations with data"
                    }
                
                if all_puts:
                    puts_df = pd.concat(all_puts, ignore_index=True)
                    puts_df["type"] = "puts"
                    if not puts_df.empty:
                        # Convert timestamp columns to string first
                        for col in ['lastTradeDate', 'expirationDate']:
                            if col in puts_df.columns:
                                puts_df[col] = puts_df[col].astype(str)

                        # Now convert DataFrame to list of dicts
                        data_batch = puts_df.to_dict(orient='records')

                        # Serialize data_batch with json.dumps and encode to bytes for Kafka
                        data_value = json.dumps(data_batch).encode('utf-8')
                        logger.info(f"Passing fetched data to option-data Producer: {data_value}")
                        producer.produce(settings.KAFKA_TOPICS['options'], value=data_value)
                        producer.flush()
                        
                        batch_result[symbol] = {
                            "status": "success",
                            "message": f"{len(data_batch)} option records",
                            "data": data_batch
                        }
                    else:
                        batch_result[symbol] = {
                            "status": "warning",
                            "message": "No option data found"
                        }
                else:
                    batch_result[symbol] = {
                        "status": "warning",
                        "message": "No valid expirations with data"
                    }

            except Exception as e:
                batch_result[symbol] = {
                    "status": "error",
                    "message": f"Unexpected error: {e}"
                }
            
        full_result.append(batch_result)
        time.sleep(5) 
        
    return JsonResponse({
        "status": "success",
        "message": "Options data fetched for all symbols in batches.",
        "data": full_result
    }, status=200)

def fetch_historical_data(request):
    """
    Fetches 10 years of daily historical data for multiple symbols (in batches of 8) from Twelve Data API.
    Publishes data to Kafka topic 'raw_stock_data'.
    """
    producer = kafkaConfig.create_producer()
    URL = "https://api.twelvedata.com/time_series"
    api_key = os.getenv('TWELVE_DATA_API_KEY')
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=365 * 1)  # 10 years ago
    all_data = []

    for batch in create_batches(symbols, batch_size=8):
        batch_data = {}
        for symbol in batch:
            current_start = start_date
            symbol_data = []
            while current_start < end_date:
                current_end = min(current_start + timedelta(days=365), end_date)  # 1 year at a time
                params = {
                    "symbol": symbol,
                    "interval": "1day",
                    "start_date": current_start.strftime("%Y-%m-%d"),
                    "end_date": current_end.strftime("%Y-%m-%d"),
                    "apikey": api_key,
                    "outputsize": 5000
                }

                try:
                    response = requests.get(URL, params=params)
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("code") == 400 or "values" not in data:
                            batch_data[symbol] = {"error": data.get("message", "No data available")}
                            logger.error("API error for %s: %s", symbol, batch_data[symbol]["error"])
                            continue
                        else:
                            batch_data[symbol] = data
                            for record in data["values"]:
                                record["symbol"] = symbol
                                producer.produce(settings.KAFKA_TOPICS["historical"], value=json.dumps(record).encode("utf-8"))
                                producer.flush()
                                symbol_data.append(record)
                    else:
                        batch_data[symbol] = {
                            "error": f"Failed: {response.status_code}",
                            "details": response.text
                        }
                        logger.error("Request failed for %s: %s", symbol, response.text)
                except requests.RequestException as e:
                    batch_data[symbol] = {"error": str(e)}
                    logger.error("Request exception for %s: %s", symbol, e)

                current_start = current_end + timedelta(days=1)
                time.sleep(1)  # Avoid API rate limits

            logger.info("Published %d records for %s", len(symbol_data), symbol)
            all_data.append(batch_data)
        time.sleep(60)  # Wait 1 min between batches

    logger.info("Data collection complete")
    return JsonResponse({
        "status": "success",
        "message": "Fetched 10 years of daily historical data for all symbols in batches",
        "data": all_data
    }, status=200)