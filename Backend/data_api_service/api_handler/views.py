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

import psycopg2
import time
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings

logger = logging.getLogger(__name__)

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

            # Verify tables
            cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'put_options')")
            if not cursor.fetchone()[0]:
                raise Exception("put_options table not found")
            
            cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'call_options')")
            if not cursor.fetchone()[0]:
                raise Exception("call_options table not found")

            # Fetch put options
            select_put_query = """
                SELECT "contractSymbol", "lastTradeDate", "expirationDate", "strike", "lastPrice", 
                       "bid", "ask", "change", "percentChange", "volume", "openInterest", 
                       "impliedVolatility", "inTheMoney", "contractSize", "currency", "StockName" 
                FROM public.put_options
            """
            cursor.execute(select_put_query)
            put_options = []
            for row in cursor.fetchall():
                put_options.append({
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
                })

            # Fetch call options
            select_call_query = """
                SELECT "contractSymbol", "lastTradeDate", "expirationDate", "strike", "lastPrice", 
                       "bid", "ask", "change", "percentChange", "volume", "openInterest", 
                       "impliedVolatility", "inTheMoney", "contractSize", "currency", "StockName" 
                FROM public.call_options
            """
            cursor.execute(select_call_query)
            call_options = []
            for row in cursor.fetchall():
                call_options.append({
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
                })

            response_data = {
                'status': 'success',
                'data': {
                    'put_options': put_options,
                    'call_options': call_options,
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

class SearchStockView(APIView):
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

            # Verify tables
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
                stock_data.append({
                    'symbol': row[0],
                    'date': row[1].isoformat().split('T')[0] if row[1] else None,
                    'open': float(row[2]) if row[2] is not None else None,
                    'high': float(row[3]) if row[3] is not None else None,
                    'low': float(row[4]) if row[4] is not None else None,
                    'close': float(row[5]) if row[5] is not None else None,
                    'volume': int(row[6]) if row[6] is not None else None
                })

            cursor.execute(put_query, (search_pattern,))
            put_options = []
            for row in cursor.fetchall():
                put_options.append({
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
                })

            cursor.execute(call_query, (search_pattern,))
            call_options = []
            for row in cursor.fetchall():
                call_options.append({
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
                })

            response_data = {
                'status': 'success',
                'data': {
                    'stock_data': stock_data,
                    'put_options': put_options,
                    'call_options': call_options,
                    'total_stock_rows': len(stock_data),
                    'total_put_rows': len(put_options),
                    'total_call_rows': len(call_options)
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