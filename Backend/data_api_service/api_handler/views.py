# import pyodbc
# import socket
# import time
# import logging
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from django.conf import settings
# from .utils import get_connection_string, connect_with_retry

# logger = logging.getLogger(__name__)

# class StockDataView(APIView):

#     def get(self, request):
#         conn = None
#         cursor = None
#         try:
#             logger.info("Resolving server name...")
#             server_ip = socket.gethostbyname("dash-gtd.database.windows.net")
#             logger.info(f"Server resolved to IP: {server_ip}")

#             conn_str = get_connection_string(settings.DATABASES['default'])
#             conn = connect_with_retry(conn_str)
#             cursor = conn.cursor()

#             # Verify tables
#             cursor.execute("SELECT 1 FROM sys.tables WHERE name = 'StockData'")
#             if not cursor.fetchone():
#                 raise Exception("StockData table not found in default DB")

#             # Check if symbol parameter is provided
#             symbol = request.GET.get('symbol')
            
#             if symbol:
#                 # Filter by specific symbol
#                 select_query = "SELECT StockName, Date, [Open], High, Low, [Close], Volume FROM StockData WHERE StockName = ?"
#                 cursor.execute(select_query, (symbol.upper(),))
#             else:
#                 # Get all stock data
#                 select_query = "SELECT StockName, Date, [Open], High, Low, [Close], Volume FROM StockData"
#                 cursor.execute(select_query)
            
#             data = []

#             # Fetch from first database
#             for row in cursor.fetchall():
#                 data.append({
#                     'symbol': row.StockName,
#                     'date': row.Date.isoformat().split('T')[0] if row.Date else None,
#                     'open': float(row.Open) if row.Open is not None else None,
#                     'high': float(row.High) if row.High is not None else None,
#                     'low': float(row.Low) if row.Low is not None else None,
#                     'close': float(row.Close) if row.Close is not None else None,
#                     'volume': int(row.Volume) if row.Volume is not None else None
#                 })

#             response_data = {
#                 'status': 'success',
#                 'data': {
#                     'stock_data': data,
#                     'total_db1_rows': len(data)
#                 }
#             }

#             return Response(response_data, status=status.HTTP_200_OK)

#         except pyodbc.Error as e:
#             logger.error(f"Database error: {e}")
#             return Response({
#                 'status': 'error',
#                 'message': str(e)
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#         except socket.gaierror as e:
#             logger.error(f"DNS resolution error: {e}")
#             return Response({
#                 'status': 'error',
#                 'message': 'DNS resolution failed'
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#         except Exception as e:
#             logger.error(f"General error: {e}")
#             return Response({
#                 'status': 'error',
#                 'message': str(e)
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#         finally:
#             if cursor:
#                 try:
#                     cursor.close()
#                 except pyodbc.Error as e:
#                     logger.error(f"Error closing cursor: {e}")
#             if conn:
#                 try:
#                     conn.close()
#                 except pyodbc.Error as e:
#                     logger.error(f"Error closing connection: {e}")

# class OptionsDataView(APIView):

#     def get(self, request):
#         conn = None
#         cursor1 = None
#         cursor2 = None
#         try:
#             # Resolve DNS
#             logger.info("Resolving server name...")
#             server_ip = socket.gethostbyname("dash-gtd.database.windows.net")
#             logger.info(f"Server resolved to IP: {server_ip}")

#             # Connect to first database
#             conn_str = get_connection_string(settings.DATABASES['default'])
#             conn = connect_with_retry(conn_str)
#             cursor1 = conn.cursor()
#             cursor2 = conn.cursor()

#             # Verify tables
#             cursor1.execute("SELECT 1 FROM sys.tables WHERE name = 'put_options'")
#             if not cursor1.fetchone():
#                 raise Exception("put_options table not found in default DB")
            
#             select_put_option_query = "SELECT contractSymbol, lastTradeDate, expirationDate, strike, lastPrice, bid, ask, change, percentChange, volume, openInterest, impliedVolatility, inTheMoney, contractSize, currency, StockName FROM put_options"
#             data1 = []

#             cursor1.execute(select_put_option_query)
#             for row in cursor1.fetchall():
#                 data1.append({
#                     'contractSymbol': row.contractSymbol,
#                     'lastTradeDate': row.lastTradeDate.isoformat().split('T')[0] if row.lastTradeDate else None,
#                     'expirationDate': row.expirationDate.isoformat().split('T')[0] if row.expirationDate else None,
#                     'strike': float(row.strike) if row.strike is not None else None,
#                     'lastPrice': float(row.lastPrice) if row.lastPrice is not None else None,
#                     'bid': float(row.bid) if row.bid is not None else None,
#                     'ask': float(row.ask) if row.ask is not None else None,
#                     'change': float(row.change) if row.change is not None else None,
#                     'percentChange': float(row.percentChange) if row.percentChange is not None else None,
#                     'volume': int(row.volume) if row.volume is not None else None,
#                     'openInterest': int(row.openInterest) if row.openInterest is not None else None,
#                     'impliedVolatility': float(row.impliedVolatility) if row.impliedVolatility is not None else None,
#                     'inTheMoney': bool(row.inTheMoney) if (row.inTheMoney)is not None else None,
#                     'contractSize': row.contractSize,
#                     'currency': row.currency,
#                     'StockName': row.StockName,
#                 })
            
#             cursor2.execute("SELECT 1 FROM sys.tables WHERE name = 'call_options'")
#             if not cursor2.fetchone():
#                 raise Exception("call_options table not found in default DB")
            
#             select_call_option_query = "SELECT contractSymbol, lastTradeDate, expirationDate, strike, lastPrice, bid, ask, change, percentChange, volume, openInterest, impliedVolatility, inTheMoney, contractSize, currency, StockName FROM call_options"
#             data2 = []

#             cursor2.execute(select_call_option_query)
#             for row in cursor2.fetchall():
#                 data2.append({
#                     'contractSymbol': row.contractSymbol,
#                     'lastTradeDate': row.lastTradeDate.isoformat().split('T')[0] if row.lastTradeDate else None,
#                     'expirationDate': row.expirationDate.isoformat().split('T')[0] if row.expirationDate else None,
#                     'strike': float(row.strike) if row.strike is not None else None,
#                     'lastPrice': float(row.lastPrice) if row.lastPrice is not None else None,
#                     'bid': float(row.bid) if row.bid is not None else None,
#                     'ask': float(row.ask) if row.ask is not None else None,
#                     'change': float(row.change) if row.change is not None else None,
#                     'percentChange': float(row.percentChange) if row.percentChange is not None else None,
#                     'volume': int(row.volume) if row.volume is not None else None,
#                     'openInterest': int(row.openInterest) if row.openInterest is not None else None,
#                     'impliedVolatility': float(row.impliedVolatility) if row.impliedVolatility is not None else None,
#                     'inTheMoney': bool(row.inTheMoney) if (row.inTheMoney)is not None else None,
#                     'contractSize': row.contractSize,
#                     'currency': row.currency,
#                     'StockName': row.StockName,
#                 })

#             # Combine data
#             response_data = {
#                 'status': 'success',
#                 'data': {
#                     'put_options': data1,
#                     'call_options': data2,
#                 }
#             }

#             return Response(response_data, status=status.HTTP_200_OK)

#         except pyodbc.Error as e:
#             logger.error(f"Database error: {e}")
#             return Response({
#                 'status': 'error',
#                 'message': str(e)
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#         except socket.gaierror as e:
#             logger.error(f"DNS resolution error: {e}")
#             return Response({
#                 'status': 'error',
#                 'message': 'DNS resolution failed'
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#         except Exception as e:
#             logger.error(f"General error: {e}")
#             return Response({
#                 'status': 'error',
#                 'message': str(e)
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#         finally:
#             if cursor1:
#                 try:
#                     cursor1.close()
#                 except pyodbc.Error as e:
#                     logger.error(f"Error closing cursor1: {e}")
#             if cursor2:
#                 try:
#                     cursor2.close()
#                 except pyodbc.Error as e:
#                     logger.error(f"Error closing cursor2: {e}")
#             if conn:
#                 try:
#                     conn.close()
#                 except pyodbc.Error as e:
#                     logger.error(f"Error closing connection: {e}")


# class SearchStockView(APIView):
#     def get(self, request):
#         stock_name = request.query_params.get('stock_name', '')
#         if not stock_name:
#             return Response({
#                 'status': 'error',
#                 'message': 'stock_name parameter is required'
#             }, status=status.HTTP_400_BAD_REQUEST)

#         conn1 = None
#         conn2 = None
#         conn3 = None
#         cursor1 = None
#         cursor2 = None
#         cursor3 = None
        
#         try:
#             logger.info("Resolving server name...")
#             server_ip = socket.gethostbyname("dash-gtd.database.windows.net")
#             logger.info(f"Server resolved to IP: {server_ip}")

#             conn_str = get_connection_string(settings.DATABASES['default'])
#             conn1 = connect_with_retry(conn_str)
#             conn2 = connect_with_retry(conn_str)
#             conn3 = connect_with_retry(conn_str)
#             cursor1 = conn1.cursor()
#             cursor2 = conn2.cursor()
#             cursor3 = conn3.cursor()

#             cursor1.execute("SELECT 1 FROM sys.tables WHERE name = 'StockData'")
#             if not cursor1.fetchone():
#                 raise Exception("StockData table not found in default DB")
            
#             cursor2.execute("SELECT 1 FROM sys.tables WHERE name = 'put_options'")
#             if not cursor2.fetchone():
#                 raise Exception("put_options table not found in default DB")
            
#             cursor3.execute("SELECT 1 FROM sys.tables WHERE name = 'call_options'")
#             if not cursor3.fetchone():
#                 raise Exception("call_options table not found in default DB")

#             stock_query = """
#                 SELECT StockName, Date, [Open], High, Low, [Close], Volume 
#                 FROM StockData 
#                 WHERE UPPER(StockName) LIKE UPPER(?)
#             """
#             put_query = """
#                 SELECT contractSymbol, lastTradeDate, expirationDate, strike, lastPrice, 
#                        bid, ask, change, percentChange, volume, openInterest, 
#                        impliedVolatility, inTheMoney, contractSize, currency, StockName 
#                 FROM put_options 
#                 WHERE UPPER(StockName) LIKE UPPER(?)
#             """
#             call_query = """
#                 SELECT contractSymbol, lastTradeDate, expirationDate, strike, lastPrice, 
#                        bid, ask, change, percentChange, volume, openInterest, 
#                        impliedVolatility, inTheMoney, contractSize, currency, StockName 
#                 FROM call_options 
#                 WHERE UPPER(StockName) LIKE UPPER(?)
#             """

#             search_pattern = f'%{stock_name}%'
#             cursor1.execute(stock_query, (search_pattern,))
#             stock_data = []
#             for row in cursor1.fetchall():
#                 stock_data.append({
#                     'symbol': row.StockName,
#                     'date': row.Date.isoformat().split('T')[0] if row.Date else None,
#                     'open': float(row.Open) if row.Open is not None else None,
#                     'high': float(row.High) if row.High is not None else None,
#                     'low': float(row.Low) if row.Low is not None else None,
#                     'close': float(row.Close) if row.Close is not None else None,
#                     'volume': int(row.Volume) if row.Volume is not None else None
#                 })

#             cursor2.execute(put_query, (search_pattern,))
#             put_options = []
#             for row in cursor2.fetchall():
#                 put_options.append({
#                     'contractSymbol': row.contractSymbol,
#                     'lastTradeDate': row.lastTradeDate.isoformat().split('T')[0] if row.lastTradeDate else None,
#                     'expirationDate': row.expirationDate.isoformat().split('T')[0] if row.expirationDate else None,
#                     'strike': float(row.strike) if row.strike is not None else None,
#                     'lastPrice': float(row.lastPrice) if row.lastPrice is not None else None,
#                     'bid': float(row.bid) if row.bid is not None else None,
#                     'ask': float(row.ask) if row.ask is not None else None,
#                     'change': float(row.change) if row.change is not None else None,
#                     'percentChange': float(row.percentChange) if row.percentChange is not None else None,
#                     'volume': int(row.volume) if row.volume is not None else None,
#                     'openInterest': int(row.openInterest) if row.openInterest is not None else None,
#                     'impliedVolatility': float(row.impliedVolatility) if row.impliedVolatility is not None else None,
#                     'inTheMoney': bool(row.inTheMoney) if row.inTheMoney is not None else None,
#                     'contractSize': row.contractSize,
#                     'currency': row.currency,
#                     'StockName': row.StockName,
#                 })

#             cursor3.execute(call_query, (search_pattern,))
#             call_options = []
#             for row in cursor3.fetchall():
#                 call_options.append({
#                     'contractSymbol': row.contractSymbol,
#                     'lastTradeDate': row.lastTradeDate.isoformat().split('T')[0] if row.lastTradeDate else None,
#                     'expirationDate': row.expirationDate.isoformat().split('T')[0] if row.expirationDate else None,
#                     'strike': float(row.strike) if row.strike is not None else None,
#                     'lastPrice': float(row.lastPrice) if row.lastPrice is not None else None,
#                     'bid': float(row.bid) if row.bid is not None else None,
#                     'ask': float(row.ask) if row.ask is not None else None,
#                     'change': float(row.change) if row.change is not None else None,
#                     'percentChange': float(row.percentChange) if row.percentChange is not None else None,
#                     'volume': int(row.volume) if row.volume is not None else None,
#                     'openInterest': int(row.openInterest) if row.openInterest is not None else None,
#                     'impliedVolatility': float(row.impliedVolatility) if row.impliedVolatility is not None else None,
#                     'inTheMoney': bool(row.inTheMoney) if row.inTheMoney is not None else None,
#                     'contractSize': row.contractSize,
#                     'currency': row.currency,
#                     'StockName': row.StockName,
#                 })

#             response_data = {
#                 'status': 'success',
#                 'data': {
#                     'stock_data': stock_data,
#                     'put_options': put_options,
#                     'call_options': call_options,
#                     'total_stock_rows': len(stock_data),
#                     'total_put_rows': len(put_options),
#                     'total_call_rows': len(call_options)
#                 }
#             }

#             return Response(response_data, status=status.HTTP_200_OK)

#         except pyodbc.Error as e:
#             logger.error(f"Database error: {e}")
#             return Response({
#                 'status': 'error',
#                 'message': str(e)
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#         except socket.gaierror as e:
#             logger.error(f"DNS resolution error: {e}")
#             return Response({
#                 'status': 'error',
#                 'message': 'DNS resolution failed'
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#         except Exception as e:
#             logger.error(f"General error: {e}")
#             return Response({
#                 'status': 'error',
#                 'message': str(e)
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#         finally:
#             for cursor in [cursor1, cursor2, cursor3]:
#                 if cursor:
#                     try:
#                         cursor.close()
#                     except pyodbc.Error as e:
#                         logger.error(f"Error closing cursor: {e}")
#             for conn in [conn1, conn2, conn3]:
#                 if conn:
#                     try:
#                         conn.close()
#                     except pyodbc.Error as e:
#                         logger.error(f"Error closing connection: {e}")

# class SearchStockName(APIView):
#     def get(self, request):
#         stock_name = request.query_params.get('stock_name', '')
#         if not stock_name:
#             return Response({
#                 'status': 'error',
#                 'message': 'stock_name parameter is required'
#             }, status=status.HTTP_400_BAD_REQUEST)

#         conn = None
#         cursor = None
        
#         try:
#             logger.info("Resolving server name...")
#             server_ip = socket.gethostbyname("dash-gtd.database.windows.net")
#             logger.info(f"Server resolved to IP: {server_ip}")

#             conn_str = get_connection_string(settings.DATABASES['default'])
#             conn = connect_with_retry(conn_str)
#             cursor = conn.cursor()

#             cursor.execute("SELECT 1 FROM sys.tables WHERE name = 'StockData'")
#             if not cursor.fetchone():
#                 raise Exception("StockData table not found in default DB")

#             stock_query = """
#                 SELECT DISTINCT StockName FROM StockData 
#                 WHERE UPPER(StockName) LIKE UPPER(?)
#             """

#             search_pattern = f'%{stock_name}%'
#             cursor.execute(stock_query, (search_pattern,))
#             stockname = []
#             for row in cursor.fetchall():
#                 stockname.append({
#                     'stocknames': row.StockName
#                 })

#             response_data = {
#                 'status': 'success',
#                 'data': {
#                     'stock_data': stockname,
#                     'total_stock_rows': len(stockname),
#                 }
#             }

#             return Response(response_data, status=status.HTTP_200_OK)

#         except pyodbc.Error as e:
#             logger.error(f"Database error: {e}")
#             return Response({
#                 'status': 'error',
#                 'message': str(e)
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#         except socket.gaierror as e:
#             logger.error(f"DNS resolution error: {e}")
#             return Response({
#                 'status': 'error',
#                 'message': 'DNS resolution failed'
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#         except Exception as e:
#             logger.error(f"General error: {e}")
#             return Response({
#                 'status': 'error',
#                 'message': str(e)
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#         finally:
#             if cursor:
#                 try:
#                     cursor.close()
#                 except pyodbc.Error as e:
#                     logger.error(f"Error closing cursor: {e}")
#             if conn:
#                 try:
#                     conn.close()
#                 except pyodbc.Error as e:
#                     logger.error(f"Error closing connection: {e}")

import os
import psycopg2
import time
import logging
import json
import math
from influxdb_client import InfluxDBClient
from requests.exceptions import HTTPError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import pandas as pd
from django.conf import settings

logger = logging.getLogger(__name__)

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, float):
            if math.isnan(obj) or math.isinf(obj):
                return None
        return super().default(obj)
    
def get_connection_string():
    """Construct PostgreSQL connection string from Django DATABASES settings."""
    db_settings = settings.DATABASES['default']
    return (
        f"dbname={db_settings['NAME']} "
        f"user={db_settings['USER']} "
        f"password={db_settings['PASSWORD']} "
        f"host={db_settings['HOST']} "
        f"port={db_settings['PORT']}"
    )

def connect_with_retry(max_retries=5, retry_delay=5):
    """Connect to PostgreSQL with retries."""
    conn_str = get_connection_string()
    for attempt in range(1, max_retries + 1):
        try:
            conn = psycopg2.connect(conn_str)
            logger.info("Successfully connected to PostgreSQL")
            return conn
        except psycopg2.Error as e:
            logger.error(f"Connection attempt {attempt}/{max_retries} failed: {e}")
            if attempt < max_retries:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                raise

def sanitize_option(option):
    for key in ['strike', 'lastPrice', 'bid', 'ask', 'change', 'percentChange', 'impliedVolatility']:
        value = option.get(key)
        if value is not None and isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
            option[key] = None
    return option

def influx_connString():
    """Establishes connection to InfluxDB using environment variables with defaults."""
    influx_url = os.getenv('INFLUXDB_URL', 'https://us-east-1-1.aws.cloud2.influxdata.com')
    influx_token = os.getenv('INFLUXDB_TOKEN', '-p4vPDiJyynco8tjaNhG2ch7A51SHtzN0ta3VsJ6Y1OqVyHtvuAL7K_gKOVmsYV47F_hqaNPlHKOdi6Y_C8Xjw==')
    influx_org = os.getenv('INFLUXDB_ORG', 'US_Stock_Data')
    influx_bucket = os.getenv('INFLUXDB_BUCKET', 'fifteenmin_stockdata')
    
    if not all([influx_url, influx_token, influx_org, influx_bucket]):
        raise ValueError("Missing required InfluxDB configuration: URL, token, org, or bucket")
    
    client = InfluxDBClient(url=influx_url, token=influx_token, org=influx_org)
    return client, influx_bucket

class StockDataView(APIView):
    def get(self, request):
        conn = None
        cursor = None
        try:
            conn = connect_with_retry()
            cursor = conn.cursor()

            # Verify table
            cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'StockData')")
            if not cursor.fetchone()[0]:
                raise Exception("StockData table not found")

            # Check if symbol parameter is provided
            symbol = request.GET.get('symbol')
            if symbol:
                select_query = 'SELECT "StockName", "Date", "Open", "High", "Low", "Close", "Volume" FROM public."StockData" WHERE "StockName" = %s'
                cursor.execute(select_query, (symbol.upper(),))
            else:
                select_query = 'SELECT "StockName", "Date", "Open", "High", "Low", "Close", "Volume" FROM public."StockData"'
                cursor.execute(select_query)

            data = []
            for row in cursor.fetchall():
                data.append({
                    'symbol': row[0],
                    'date': row[1].isoformat().split('T')[0] if row[1] else None,
                    'open': float(row[2]) if row[2] is not None else None,
                    'high': float(row[3]) if row[3] is not None else None,
                    'low': float(row[4]) if row[4] is not None else None,
                    'close': float(row[5]) if row[5] is not None else None,
                    'volume': int(row[6]) if row[6] is not None else None
                })

            response_data = {
                'status': 'success',
                'data': {
                    'stock_data': data,
                    'total_db1_rows': len(data)
                }
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except psycopg2.Error as e:
            logger.error(f"Database error: {e}")
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"General error: {e}")
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

class OptionsDataView(APIView):
    def get(self, request):
        conn = None
        cursor = None
        try:
            conn = connect_with_retry()
            cursor = conn.cursor()

            cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'put_options')")
            if not cursor.fetchone()[0]:
                raise Exception("put_options table not found")
            
            cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'call_options')")
            if not cursor.fetchone()[0]:
                raise Exception("call_options table not found")

            # Check if symbol parameter is provided for filtering
            symbol = request.GET.get('symbol')
            if symbol:
                symbol = symbol.upper()
                logger.info(f"Filtering options data for symbol: {symbol}")
                put_where_clause = 'WHERE "StockName" = %s'
                call_where_clause = 'WHERE "StockName" = %s'
                put_params = (symbol,)
                call_params = (symbol,)
            else:
                put_where_clause = ''
                call_where_clause = ''
                put_params = ()
                call_params = ()

            select_put_query = f"""
                SELECT "contractSymbol", "lastTradeDate", "expirationDate", "strike", "lastPrice", 
                       "bid", "ask", "change", "percentChange", "volume", "openInterest", 
                       "impliedVolatility", "inTheMoney", "contractSize", "currency", "StockName" 
                FROM public.put_options
                {put_where_clause}
            """
            cursor.execute(select_put_query, put_params)
            put_options = []
            put_rows = cursor.fetchall()
            logger.info(f"Found {len(put_rows)} put options records")
            
            for row in put_rows:
                put_option = {
                    'contractSymbol': row[0],
                    'lastTradeDate': row[1].isoformat() if row[1] else None,
                    'expirationDate': row[2].isoformat().split('T')[0] if row[2] else None,
                    'strike': float(row[3]) if row[3] is not None else None,
                    'lastPrice': float(row[4]) if row[4] is not None else None,
                    'bid': float(row[5]) if row[5] is not None else None,
                    'ask': float(row[6]) if row[6] is not None else None,
                    'change': float(row[7]) if row[7] is not None else None,
                    'percentChange': float(row[8]) if row[8] is not None else None,
                    'volume': int(row[9]) if row[9] is not None else None,
                    'openInterest': int(row[10]) if row[10] is not None else None,
                    'impliedVolatility': float(row[11]) if row[11] is not None else None,
                    'inTheMoney': bool(row[12]) if row[12] is not None else None,
                    'contractSize': row[13],
                    'currency': row[14],
                    'StockName': row[15],
                }
                put_option = sanitize_option(put_option)
                put_options.append(put_option)

            select_call_query = f"""
                SELECT "contractSymbol", "lastTradeDate", "expirationDate", "strike", "lastPrice", 
                       "bid", "ask", "change", "percentChange", "volume", "openInterest", 
                       "impliedVolatility", "inTheMoney", "contractSize", "currency", "StockName" 
                FROM public.call_options
                {call_where_clause}
            """
            cursor.execute(select_call_query, call_params)
            call_options = []
            call_rows = cursor.fetchall()
            logger.info(f"Found {len(call_rows)} call options records")
            
            for row in call_rows:
                call_option = {
                    'contractSymbol': row[0],
                    'lastTradeDate': row[1].isoformat() if row[1] else None,
                    'expirationDate': row[2].isoformat().split('T')[0] if row[2] else None,
                    'strike': float(row[3]) if row[3] is not None else None,
                    'lastPrice': float(row[4]) if row[4] is not None else None,
                    'bid': float(row[5]) if row[5] is not None else None,
                    'ask': float(row[6]) if row[6] is not None else None,
                    'change': float(row[7]) if row[7] is not None else None,
                    'percentChange': float(row[8]) if row[8] is not None else None,
                    'volume': int(row[9]) if row[9] is not None else None,
                    'openInterest': int(row[10]) if row[10] is not None else None,
                    'impliedVolatility': float(row[11]) if row[11] is not None else None,
                    'inTheMoney': bool(row[12]) if row[12] is not None else None,
                    'contractSize': row[13],
                    'currency': row[14],
                    'StockName': row[15],
                }
                call_option = sanitize_option(call_option)
                call_options.append(call_option)

            # Log unique stock names found
            put_stock_names = set(opt['StockName'] for opt in put_options)
            call_stock_names = set(opt['StockName'] for opt in call_options)
            all_stock_names = put_stock_names.union(call_stock_names)
            logger.info(f"Unique stock names in options data: {sorted(all_stock_names)}")

            response_data = {
                'status': 'success',
                'data': {
                    'put_options': put_options,
                    'call_options': call_options,
                    'total_put_rows': len(put_options),
                    'total_call_rows': len(call_options)
                }
            }
            return Response(response_data, status=status.HTTP_200_OK, content_type='application/json')

        except psycopg2.Error as e:
            logger.error(f"Database error: {e}")
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"General error: {e}")
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

class SearchStockView(APIView):
    def get(self, request):
        stock_name = request.query_params.get('stock_name', '')
        if not stock_name:
            return Response({
                'status': 'error',
                'message': 'stock_name parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        option_stock_name = stock_name[:3]
        conn = None
        cursor = None
        try:
            conn = connect_with_retry()
            cursor = conn.cursor()

            cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'StockData')")
            if not cursor.fetchone()[0]:
                raise Exception("StockData table not found")
            cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'put_options')")
            if not cursor.fetchone()[0]:
                raise Exception("put_options table not found")
            
            cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'call_options')")
            if not cursor.fetchone()[0]:
                raise Exception("call_options table not found")

            stock_query = """
                SELECT "StockName", "Date", "Open", "High", "Low", "Close", "Volume" 
                FROM public."StockData" 
                WHERE UPPER("StockName") LIKE UPPER(%s)
            """
            put_query = """
                SELECT "contractSymbol", "lastTradeDate", "expirationDate", "strike", "lastPrice", 
                        "bid", "ask", "change", "percentChange", "volume", "openInterest", 
                        "impliedVolatility", "inTheMoney", "contractSize", "currency", "StockName" 
                FROM public.put_options 
                WHERE UPPER("StockName") LIKE UPPER(%s)
            """
            call_query = """
                SELECT "contractSymbol", "lastTradeDate", "expirationDate", "strike", "lastPrice", 
                        "bid", "ask", "change", "percentChange", "volume", "openInterest", 
                        "impliedVolatility", "inTheMoney", "contractSize", "currency", "StockName" 
                FROM public.call_options
                WHERE UPPER("StockName") LIKE UPPER(%s)
            """

            search_pattern = f'%{stock_name}%'
            cursor.execute(stock_query, (search_pattern,))
            stock_data = []
            for row in cursor.fetchall():
                stock_entry = {
                    'symbol': row[0],
                    'date': row[1].isoformat().split('T')[0] if row[1] else None,
                    'open': float(row[2]) if row[2] is not None else None,
                    'high': float(row[3]) if row[3] is not None else None,
                    'low': float(row[4]) if row[4] is not None else None,
                    'close': float(row[5]) if row[5] is not None else None,
                    'volume': int(row[6]) if row[6] is not None else None
                }
                for key in ['open', 'high', 'low', 'close']:
                    if stock_entry[key] is not None and (math.isnan(stock_entry[key]) or math.isinf(stock_entry[key])):
                        logger.warning(f"Problematic value in stock_data, symbol={stock_entry['symbol']}, key={key}, value={stock_entry[key]}")
                        stock_entry[key] = None
                stock_data.append(stock_entry)
            
            option_search_pattern = f'%{option_stock_name}%'
            cursor.execute(put_query, (option_search_pattern,))
            put_options = []
            put_rows = cursor.fetchall()
            logger.info(f"Put Data: {put_rows}")
            for row in put_rows:
                put_option = {
                    'contractSymbol': row[0],
                    'lastTradeDate': row[1].isoformat() if row[1] else None,
                    'expirationDate': row[2].isoformat().split('T')[0] if row[2] else None,
                    'strike': float(row[3]) if row[3] is not None else None,
                    'lastPrice': float(row[4]) if row[4] is not None else None,
                    'bid': float(row[5]) if row[5] is not None else None,
                    'ask': float(row[6]) if row[6] is not None else None,
                    'change': float(row[7]) if row[7] is not None else None,
                    'percentChange': float(row[8]) if row[8] is not None else None,
                    'volume': int(row[9]) if row[9] is not None else None,
                    'openInterest': int(row[10]) if row[10] is not None else None,
                    'impliedVolatility': float(row[11]) if row[11] is not None else None,
                    'inTheMoney': bool(row[12]) if row[12] is not None else None,
                    'contractSize': row[13],
                    'currency': row[14],
                    'StockName': row[15],
                }
                for key in ['strike', 'lastPrice', 'bid', 'ask', 'change', 'percentChange', 'impliedVolatility']:
                    if put_option[key] is not None and (math.isnan(put_option[key]) or math.isinf(put_option[key])):
                        logger.warning(f"Problematic value in put_options, contractSymbol={put_option['contractSymbol']}, key={key}, value={put_option[key]}")
                        put_option[key] = None
                put_options.append(put_option)

            cursor.execute(call_query, (option_search_pattern,))
            call_options = []
            call_rows = cursor.fetchall()
            logger.info(f"Call Data: {call_rows}")
            for row in call_rows:
                call_option = {
                    'contractSymbol': row[0],
                    'lastTradeDate': row[1].isoformat() if row[1] else None,
                    'expirationDate': row[2].isoformat().split('T')[0] if row[2] else None,
                    'strike': float(row[3]) if row[3] is not None else None,
                    'lastPrice': float(row[4]) if row[4] is not None else None,
                    'bid': float(row[5]) if row[5] is not None else None,
                    'ask': float(row[6]) if row[6] is not None else None,
                    'change': float(row[7]) if row[7] is not None else None,
                    'percentChange': float(row[8]) if row[8] is not None else None,
                    'volume': int(row[9]) if row[9] is not None else None,
                    'openInterest': int(row[10]) if row[10] is not None else None,
                    'impliedVolatility': float(row[11]) if row[11] is not None else None,
                    'inTheMoney': bool(row[12]) if row[12] is not None else None,
                    'contractSize': row[13],
                    'currency': row[14],
                    'StockName': row[15],
                }
                for key in ['strike', 'lastPrice', 'bid', 'ask', 'change', 'percentChange', 'impliedVolatility']:
                    if call_option[key] is not None and (math.isnan(call_option[key]) or math.isinf(call_option[key])):
                        logger.warning(f"Problematic value in call_options, contractSymbol={call_option['contractSymbol']}, key={key}, value={call_option[key]}")
                        call_option[key] = None
                call_options.append(call_option)

            influx_client, influx_bucket = None, None
            try:
                influx_client, influx_bucket = influx_connString()
            except Exception as e:
                logger.error(f"Failed to initialize InfluxDB client: {e}")
                return Response({
                    'status': 'error',
                    'message': f"InfluxDB connection error: {str(e)}"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            us_tz = ZoneInfo("UTC")  # Use UTC to match data timestamps
            end_time = datetime.now(us_tz)
            start_time = end_time - timedelta(days=7)
            start_time_str = start_time.isoformat()
            end_time_str = end_time.isoformat()

            # Build InfluxDB query
            query = f'''
                from(bucket: "{influx_bucket}")
                |> range(start: {start_time_str}, stop: {end_time_str})
                |> filter(fn: (r) => r._measurement == "stock_15min")
            '''
            if stock_name:
                query += f' |> filter(fn: (r) => r.StockName == "{stock_name.upper()}" or r["StockName"] == "{stock_name.upper()}")'
            query += ' |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")'

            try:
                query_api = influx_client.query_api()
                logger.info(f"Executing InfluxDB query: {query}")
                
                # Debug: Check available measurements and tags
                schema_query = f'''
                    from(bucket: "{influx_bucket}")
                    |> range(start: -30d)
                    |> filter(fn: (r) => r._measurement == "stock_15min")
                    |> keep(columns: ["_measurement", "StockName", "_field", "_time"])
                    |> limit(n: 10)
                '''
                schema_tables = query_api.query_data_frame(schema_query, org=influx_client.org)
                logger.info(f"Schema debug result: {schema_tables}")

                tables = query_api.query_data_frame(query, org=influx_client.org)
                logger.info(f"Query result: {tables}")

                influx_stock_data = []
                if tables.empty:
                    logger.info(f"No InfluxDB data for stock_name: {stock_name} in range {start_time_str} to {end_time_str}")
                else:
                    # Drop unnecessary columns
                    tables = tables.drop(columns=[col for col in tables.columns if col.startswith('result') or col.startswith('table')], errors='ignore')
                    # Map InfluxDB fields to match response format
                    for _, row in tables.iterrows():
                        stock_entry = {
                            'symbol': row.get('StockName', ''),
                            'date': row['_time'].strftime('%Y-%m-%d') if pd.notnull(row['_time']) else None,
                            'open': float(row.get('open')) if pd.notnull(row.get('open')) else None,
                            'high': float(row.get('high')) if pd.notnull(row.get('high')) else None,
                            'low': float(row.get('low')) if pd.notnull(row.get('low')) else None,
                            'close': float(row.get('close')) if pd.notnull(row.get('close')) else None,
                            'volume': int(row.get('volume')) if pd.notnull(row.get('volume')) else None
                        }
                        for key in ['open', 'high', 'low', 'close']:
                            if stock_entry[key] is not None and (math.isnan(stock_entry[key]) or math.isinf(stock_entry[key])):
                                logger.warning(f"Problematic value in influx_stock_data, symbol={stock_entry['symbol']}, key={key}, value={stock_entry[key]}")
                                stock_entry[key] = None
                        influx_stock_data.append(stock_entry)

                    available_stocknames = tables['StockName'].unique().tolist() if 'StockName' in tables.columns else []
                    logger.info(f"Available StockNames in InfluxDB: {available_stocknames}")

            except HTTPError as http_err:
                logger.error(f"InfluxDB HTTP error: {http_err}")
                return Response({
                    'status': 'error',
                    'message': f"InfluxDB query error: {str(http_err)}"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except Exception as e:
                logger.error(f"InfluxDB general error: {e}")
                return Response({
                    'status': 'error',
                    'message': f"InfluxDB query error: {str(e)}"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            finally:
                if influx_client:
                    influx_client.close()

            response_data = {
                'status': 'success',
                'data': {
                    'stock_data': stock_data,
                    'put_options': put_options,
                    'call_options': call_options,
                    'realtime_data': influx_stock_data,
                    'total_stock_rows': len(stock_data),
                    'total_put_rows': len(put_options),
                    'total_call_rows': len(call_options),
                    'total_realtime_rows': len(influx_stock_data)
                }
            }
            return Response(response_data, status=status.HTTP_200_OK, content_type='application/json')

        except psycopg2.Error as e:
            logger.error(f"Database error: {e}")
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"General error: {e}")
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

class InfluxStockDataView(APIView):
    def get(self, request):
        stock_name = request.query_params.get('stock_name', '')
        influx_client, influx_bucket = None, None
        try:
            influx_client, influx_bucket = influx_connString()
        except Exception as e:
            logger.error(f"Failed to initialize InfluxDB client: {e}")
            return Response({
                'status': 'error',
                'message': f"InfluxDB connection error: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            us_tz = ZoneInfo("UTC")
            end_time = datetime.now(us_tz)
            start_time = end_time - timedelta(days=7)
            start_time_str = start_time.isoformat()
            end_time_str = end_time.isoformat()

            query = f'''
                from(bucket: "{influx_bucket}")
                |> range(start: {start_time_str}, stop: {end_time_str})
                |> filter(fn: (r) => r._measurement == "stock_15min")
            '''
            if stock_name:
                query += f' |> filter(fn: (r) => r.StockName == "{stock_name.upper()}" or r["StockName"] == "{stock_name.upper()}")'
            query += ' |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")'

            query_api = influx_client.query_api()
            logger.info(f"Executing InfluxDB query: {query}")
            
            schema_query = f'''
                from(bucket: "{influx_bucket}")
                |> range(start: -30d)
                |> filter(fn: (r) => r._measurement == "stock_15min")
                |> keep(columns: ["_measurement", "StockName", "_field", "_time"])
                |> limit(n: 10)
            '''
            schema_tables = query_api.query_data_frame(schema_query, org=influx_client.org)
            logger.info(f"Schema debug result: {schema_tables}")

            tables = query_api.query_data_frame(query, org=influx_client.org)
            logger.info(f"Query result: {tables}")

            influx_stock_data = []
            if tables.empty:
                logger.info(f"No InfluxDB data for stock_name: {stock_name} in range {start_time_str} to {end_time_str}")
            else:
                tables = tables.drop(columns=[col for col in tables.columns if col.startswith('result') or col.startswith('table')], errors='ignore')
                for _, row in tables.iterrows():
                    stock_entry = {
                        'symbol': row.get('StockName', ''),
                        'date': row['_time'].strftime('%Y-%m-%d') if pd.notnull(row['_time']) else None,
                        'open': float(row.get('open')) if pd.notnull(row.get('open')) else None,
                        'high': float(row.get('high')) if pd.notnull(row.get('high')) else None,
                        'low': float(row.get('low')) if pd.notnull(row.get('low')) else None,
                        'close': float(row.get('close')) if pd.notnull(row.get('close')) else None,
                        'volume': int(row.get('volume')) if pd.notnull(row.get('volume')) else None
                    }
                    for key in ['open', 'high', 'low', 'close']:
                        if stock_entry[key] is not None and (math.isnan(stock_entry[key]) or math.isinf(stock_entry[key])):
                            logger.warning(f"Problematic value in influx_stock_data, symbol={stock_entry['symbol']}, key={key}, value={stock_entry[key]}")
                            stock_entry[key] = None
                    influx_stock_data.append(stock_entry)

                available_stocknames = tables['StockName'].unique().tolist() if 'StockName' in tables.columns else []
                logger.info(f"Available StockNames in InfluxDB: {available_stocknames}")

            response_data = {
                'status': 'success',
                'data': {
                    'realtime_data': influx_stock_data,
                    'total_realtime_rows': len(influx_stock_data)
                }
            }
            return Response(response_data, status=status.HTTP_200_OK, content_type='application/json')

        except HTTPError as http_err:
            logger.error(f"InfluxDB HTTP error: {http_err}")
            return Response({
                'status': 'error',
                'message': f"InfluxDB query error: {str(http_err)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"InfluxDB general error: {e}")
            return Response({
                'status': 'error',
                'message': f"InfluxDB query error: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            if influx_client:
                influx_client.close()

class SearchStockName(APIView):
    def get(self, request):
        stock_name = request.query_params.get('stock_name', '')
        if not stock_name:
            return Response({
                'status': 'error',
                'message': 'stock_name parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        conn = None
        cursor = None
        try:
            conn = connect_with_retry()
            cursor = conn.cursor()

            cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'StockData')")
            if not cursor.fetchone()[0]:
                raise Exception("StockData table not found")

            stock_query = """
                SELECT DISTINCT "StockName" FROM public."StockData" 
                WHERE UPPER("StockName") LIKE UPPER(%s)
            """
            search_pattern = f'%{stock_name}%'
            cursor.execute(stock_query, (search_pattern,))
            stock_names = [{'stock_name': row[0]} for row in cursor.fetchall()]

            response_data = {
                'status': 'success',
                'data': {
                    'stock_names': stock_names,
                    'total_stock_rows': len(stock_names),
                }
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except psycopg2.Error as e:
            logger.error(f"Database error: {e}")
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"General error: {e}")
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()