# import pyodbc
# import socket
# import time
# from django.conf import settings
# from db_writer.utils.logConfig import LogConfig

# logger = LogConfig()

# class OptionsSQLHandler:
#     def __init__(self):
#         self.conn_strings = [
#             settings.AZURE_SQL_CONNECTION_STRING,
#             settings.AZURE_SQL_CONNECTION_STRING.replace("ODBC Driver 18", "ODBC Driver 17")
#         ]
#         self.max_retries = 5
#         self.retry_delay = 20
#         self.conn = None
#         self.cursor = None
#         self.connect()

#     def connect(self):
#         for conn_str in self.conn_strings:
#             driver = conn_str.split(';')[0].split('=')[1]
#             logger.info(f"Trying connection with {driver}")
#             for attempt in range(self.max_retries):
#                 try:
#                     logger.info(f"Connection attempt {attempt + 1}/{self.max_retries}")
#                     server_ip = socket.gethostbyname("dash-gtd02.database.windows.net")
#                     logger.info(f"Server resolved to IP: {server_ip}")
#                     self.conn = pyodbc.connect(conn_str)
#                     self.cursor = self.conn.cursor()

#                     # Check required tables
#                     self.cursor.execute("SELECT 1 FROM sys.tables WHERE name = 'put_options'")
#                     if not self.cursor.fetchone():
#                         raise Exception("Table 'put_options' does not exist")

#                     self.cursor.execute("SELECT 1 FROM sys.tables WHERE name = 'call_options'")
#                     if not self.cursor.fetchone():
#                         raise Exception("Table 'call_options' does not exist")

#                     logger.info("Connected successfully to Azure SQL")
#                     return
#                 except (pyodbc.Error, socket.gaierror) as e:
#                     logger.error(f"Connection failed with {driver}: {e}")
#                     if attempt < self.max_retries - 1:
#                         logger.info(f"Retrying in {self.retry_delay} seconds...")
#                         time.sleep(self.retry_delay)
#             logger.info(f"Failed with {driver}, trying next driver if available")
#         raise Exception("All connection attempts failed")

#     def write_data(self, data):
#         if not isinstance(data, list):
#             logger.error(f"Invalid data format: expected list, got {type(data)}")
#             return

#         for record in data:
#             try:
#                 table = 'put_options' if record.get('type', '').lower() == 'puts' else 'call_options'
#                 check_query = f"""
#                     SELECT COUNT(*) 
#                     FROM {table} 
#                     WHERE contractSymbol = ? AND lastTradeDate = ?
#                 """
#                 insert_query = f"""
#                     INSERT INTO {table} (
#                         contractSymbol, lastTradeDate, expirationDate, strike, lastPrice, bid, ask,
#                         change, percentChange, volume, openInterest, impliedVolatility, inTheMoney,
#                         contractSize, currency, StockName
#                     )
#                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
#                 """

#                 values = (
#                     record.get('contractSymbol', 'UNKNOWN'),
#                     record['lastTradeDate'],
#                     record['expirationDate'],
#                     float(record['strike']),
#                     float(record.get('lastPrice')) if record.get('lastPrice') is not None else None,
#                     float(record.get('bid')) if record.get('bid') is not None else None,
#                     float(record.get('ask')) if record.get('ask') is not None else None,
#                     float(record.get('change')) if record.get('change') is not None else None,
#                     float(record.get('percentChange')) if record.get('percentChange') is not None else None,
#                     int(record.get('volume')) if record.get('volume') is not None else None,
#                     int(record.get('openInterest')) if record.get('openInterest') is not None else None,
#                     float(record.get('impliedVolatility')) if record.get('impliedVolatility') is not None else None,
#                     1 if record.get('inTheMoney', False) else 0,
#                     record.get('contractSize', 'REGULAR'),
#                     record.get('currency', 'USD'),
#                     record['symbol']
#                 )

#                 self.cursor.execute(check_query, (record['contractSymbol'], record['lastTradeDate']))
#                 exists = self.cursor.fetchone()[0]

#                 if exists == 0:
#                     self.cursor.execute(insert_query, values)
#                     self.conn.commit()
#                     logger.info(f"Inserted option record for {record['contractSymbol']} in {table}")
#                 else:
#                     logger.info(f"Option record for {record['contractSymbol']} on {record['lastTradeDate']} already exists, skipping insertion")

#             except pyodbc.Error as e:
#                 logger.error(f"Failed to process option data for {record.get('contractSymbol', 'UNKNOWN')}: {e}")
#                 logger.info("Attempting to reconnect and retry...")
#                 self.connect()
#                 try:
#                     self.cursor.execute(check_query, (record['contractSymbol'], record['lastTradeDate']))
#                     exists = self.cursor.fetchone()[0]
#                     if exists == 0:
#                         self.cursor.execute(insert_query, values)
#                         self.conn.commit()
#                         logger.info(f"Retry: Inserted option record for {record['contractSymbol']} in {table}")
#                     else:
#                         logger.info(f"Retry: Option record for {record['contractSymbol']} on {record['lastTradeDate']} already exists, skipping insertion")
#                 except pyodbc.Error as retry_e:
#                     logger.error(f"Retry failed for {record.get('contractSymbol', 'UNKNOWN')}: {retry_e}")

#     def close(self):
#         if self.cursor:
#             self.cursor.close()
#         if self.conn:
#             self.conn.close()
#         logger.info("Azure SQL connection closed")




# import psycopg2
# import socket
# import traceback
# import os
# import time
# from django.conf import settings
# from db_writer.utils.logConfig import LogConfig

# logger = LogConfig()

# class OptionsSQLHandler:
#     def __init__(self):
#         # self.conn_strings = [os.getenv('POSTGRES_CONNECTION_STRING', 'postgresql://sa:Passw0rd!@postgres:5432/us_stock_options_db')]
#         self.max_retries = 5
#         self.retry_delay = 30
#         self.conn = None
#         self.cursor = None
#         logger.info("Waiting 30 seconds for PostgreSQL to be fully ready...")
#         time.sleep(30)
#         self.connect()

#     def connect(self):
#         """Establish a connection to the PostgreSQL database."""
#         # for conn_str in self.conn_strings:
#         # logger.info(f"Attempting connection using connection string: {conn_str}")
#         for attempt in range(1, self.max_retries + 1):
#             try:
#                 # server = "postgres"
#                 # server_ip = socket.gethostbyname(server)
#                 # logger.info(f"Resolved server '{server}' to IP: {server_ip}")

#                 # self.conn = psycopg2.connect(conn_str)
#                 self.conn = psycopg2.connect(
#                                 user="sa",
#                                 password="Passw0rd!",
#                                 host="postgres-service",  
#                                 port="5432",
#                                 database="us_stock_options_db"
#                             )
#                 self.cursor = self.conn.cursor()

#                 # Verify table existence
#                 self.cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name IN ('call_options', 'put_options'))")
#                 if not self.cursor.fetchone()[0]:
#                     raise Exception("Tables 'call_options' or 'put_options' do not exist in database.")

#                 logger.info("Successfully connected to PostgreSQL")
#                 return
#             except (psycopg2.Error, socket.gaierror) as e:
#                 logger.error(f"Connection attempt {attempt}/{self.max_retries} failed: {e}")
#                 if attempt < self.max_retries:
#                     logger.info(f"Waiting {self.retry_delay} seconds before retrying...")
#                     time.sleep(self.retry_delay)
#                 else:
#                     logger.warning(f"All attempts failed for connection string.")
#         raise Exception("All connection attempts failed.")

#     def insert_data(self, data):
#         """Write data to call_options or put_options table."""
#         if not isinstance(data, list):
#             logger.error(f"Invalid data format: expected list, got {type(data)}")
#             return

#         for record in data:
#             try:
#                 table = '"put_options"' if record.get('type', '').lower() == 'puts' else '"call_options"'
#                 check_query = f"""
#                     SELECT COUNT(*) 
#                     FROM {table} 
#                     WHERE "contractSymbol" = %s AND "lastTradeDate" = %s AND "StockName" = %s AND "expirationDate" = %s
#                 """
#                 insert_query = f"""
#                     INSERT INTO {table} (
#                         "contractSymbol", "lastTradeDate", "expirationDate", "strike", "lastPrice", "bid", "ask",
#                         "change", "percentChange", "volume", "openInterest", "impliedVolatility", "inTheMoney",
#                         "contractSize", "currency", "StockName", "created_at", "updated_at"
#                     )
#                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
#                     ON CONFLICT ("contractSymbol", "lastTradeDate", "StockName", "expirationDate") DO UPDATE 
#                     SET "lastPrice" = EXCLUDED."lastPrice",
#                         "bid" = EXCLUDED."bid",
#                         "ask" = EXCLUDED."ask",
#                         "change" = EXCLUDED."change",
#                         "percentChange" = EXCLUDED."percentChange",
#                         "volume" = EXCLUDED."volume",
#                         "openInterest" = EXCLUDED."openInterest",
#                         "impliedVolatility" = EXCLUDED."impliedVolatility",
#                         "inTheMoney" = EXCLUDED."inTheMoney",
#                         "updated_at" = CURRENT_TIMESTAMP
#                 """

#                 values = (
#                     record.get('contractSymbol', 'UNKNOWN'),
#                     record.get('lastTradeDate'),
#                     record.get('expirationDate'),
#                     float(record.get('strike')) if record.get('strike') is not None else None,
#                     float(record.get('lastPrice')) if record.get('lastPrice') is not None else None,
#                     float(record.get('bid')) if record.get('bid') is not None else None,
#                     float(record.get('ask')) if record.get('ask') is not None else None,
#                     float(record.get('change')) if record.get('change') is not None else None,
#                     float(record.get('percentChange')) if record.get('percentChange') is not None else None,
#                     int(record.get('volume')) if record.get('volume') is not None else None,
#                     int(record.get('openInterest')) if record.get('openInterest') is not None else None,
#                     float(record.get('impliedVolatility')) if record.get('impliedVolatility') is not None else None,
#                     bool(record.get('inTheMoney', False)),
#                     record.get('contractSize', 'REGULAR'),
#                     record.get('currency', 'USD'),
#                     record.get('symbol')
#                 )

#                 if not all([record.get('contractSymbol'), record.get('lastTradeDate'), record.get('expirationDate'), record.get('symbol')]):
#                     logger.error(f"Missing required fields in record: {record}")
#                     continue

#                 self.cursor.execute(check_query, (record.get('contractSymbol'), record.get('lastTradeDate'), record.get('symbol'), record.get('expirationDate')))
#                 exists = self.cursor.fetchone()[0]

#                 if exists == 0:
#                     self.cursor.execute(insert_query, values)
#                     self.conn.commit()
#                     logger.info(f"Inserted option record for {record.get('contractSymbol')} in {table}")
#                 else:
#                     self.cursor.execute(insert_query, values)
#                     self.conn.commit()
#                     logger.info(f"Updated option record for {record.get('contractSymbol')} in {table}")

#             except psycopg2.Error as e:
#                 logger.error(f"DB error processing record for {record.get('contractSymbol', 'UNKNOWN')}: {e}")
#                 self.conn.rollback()
#                 logger.info("Attempting to reconnect and retry insertion...")
#                 try:
#                     self.connect()
#                     self.cursor.execute(check_query, (record.get('contractSymbol'), record.get('lastTradeDate'), record.get('symbol'), record.get('expirationDate')))
#                     exists = self.cursor.fetchone()[0]
#                     self.cursor.execute(insert_query, values)
#                     self.conn.commit()
#                     logger.info(f"Retry successful: Inserted/Updated record for {record.get('contractSymbol', 'UNKNOWN')} in {table}")
#                 except psycopg2.Error as retry_e:
#                     logger.error(f"Retry failed for {record.get('contractSymbol', 'UNKNOWN')}: {retry_e}")
#             except Exception as ex:
#                 logger.error(f"Unexpected error processing record {record}: {ex}\n{traceback.format_exc()}")

#     def close(self):
#         """Close database cursor and connection."""
#         try:
#             if self.cursor:
#                 self.cursor.close()
#                 logger.info("Database cursor closed.")
#             if self.conn:
#                 self.conn.close()
#                 logger.info("Database connection closed.")
#         except Exception as e:
#             logger.error(f"Error during closing resources: {e}")
#         finally:
#             self.cursor = None
#             self.conn = None


import pyodbc
import socket
import time
from django.conf import settings
from db_writer.utils.logConfig import LogConfig

logger = LogConfig()

class OptionsSQLHandler:
    def __init__(self):
        self.conn_strings = [
            settings.AZURE_SQL_CONNECTION_STRING,
            settings.AZURE_SQL_CONNECTION_STRING.replace("ODBC Driver 18", "ODBC Driver 17")
        ]
        self.max_retries = 5
        self.retry_delay = 20
        self.conn = None
        self.cursor = None
        self.connect()

    def connect(self):
        for conn_str in self.conn_strings:
            driver = conn_str.split(';')[0].split('=')[1]
            logger.info(f"Trying connection with {driver}")
            for attempt in range(self.max_retries):
                try:
                    logger.info(f"Connection attempt {attempt + 1}/{self.max_retries}")
                    server_ip = socket.gethostbyname("dash-gtd02.database.windows.net")
                    logger.info(f"Server resolved to IP: {server_ip}")
                    self.conn = pyodbc.connect(conn_str)
                    self.cursor = self.conn.cursor()

                    # Check required tables
                    self.cursor.execute("SELECT 1 FROM sys.tables WHERE name = 'put_options'")
                    if not self.cursor.fetchone():
                        raise Exception("Table 'put_options' does not exist")

                    self.cursor.execute("SELECT 1 FROM sys.tables WHERE name = 'call_options'")
                    if not self.cursor.fetchone():
                        raise Exception("Table 'call_options' does not exist")

                    logger.info("Connected successfully to Azure SQL")
                    return
                except (pyodbc.Error, socket.gaierror) as e:
                    logger.error(f"Connection failed with {driver}: {e}")
                    if attempt < self.max_retries - 1:
                        logger.info(f"Retrying in {self.retry_delay} seconds...")
                        time.sleep(self.retry_delay)
            logger.info(f"Failed with {driver}, trying next driver if available")
        raise Exception("All connection attempts failed")

    def write_data(self, data):
        if not isinstance(data, list):
            logger.error(f"Invalid data format: expected list, got {type(data)}")
            return

        for record in data:
            try:
                table = 'put_options' if record.get('type', '').lower() == 'puts' else 'call_options'
                check_query = f"""
                    SELECT COUNT(*) 
                    FROM {table} 
                    WHERE contractSymbol = ? AND lastTradeDate = ?
                """
                insert_query = f"""
                    INSERT INTO {table} (
                        contractSymbol, lastTradeDate, expirationDate, strike, lastPrice, bid, ask,
                        change, percentChange, volume, openInterest, impliedVolatility, inTheMoney,
                        contractSize, currency, StockName
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """

                values = (
                    record.get('contractSymbol', 'UNKNOWN'),
                    record['lastTradeDate'],
                    record['expirationDate'],
                    float(record['strike']),
                    float(record.get('lastPrice')) if record.get('lastPrice') is not None else None,
                    float(record.get('bid')) if record.get('bid') is not None else None,
                    float(record.get('ask')) if record.get('ask') is not None else None,
                    float(record.get('change')) if record.get('change') is not None else None,
                    float(record.get('percentChange')) if record.get('percentChange') is not None else None,
                    int(record.get('volume')) if record.get('volume') is not None else None,
                    int(record.get('openInterest')) if record.get('openInterest') is not None else None,
                    float(record.get('impliedVolatility')) if record.get('impliedVolatility') is not None else None,
                    1 if record.get('inTheMoney', False) else 0,
                    record.get('contractSize', 'REGULAR'),
                    record.get('currency', 'USD'),
                    record['symbol']
                )

                self.cursor.execute(check_query, (record['contractSymbol'], record['lastTradeDate']))
                exists = self.cursor.fetchone()[0]

                if exists == 0:
                    self.cursor.execute(insert_query, values)
                    self.conn.commit()
                    logger.info(f"Inserted option record for {record['contractSymbol']} in {table}")
                else:
                    logger.info(f"Option record for {record['contractSymbol']} on {record['lastTradeDate']} already exists, skipping insertion")

            except pyodbc.Error as e:
                logger.error(f"Failed to process option data for {record.get('contractSymbol', 'UNKNOWN')}: {e}")
                logger.info("Attempting to reconnect and retry...")
                self.connect()
                try:
                    self.cursor.execute(check_query, (record['contractSymbol'], record['lastTradeDate']))
                    exists = self.cursor.fetchone()[0]
                    if exists == 0:
                        self.cursor.execute(insert_query, values)
                        self.conn.commit()
                        logger.info(f"Retry: Inserted option record for {record['contractSymbol']} in {table}")
                    else:
                        logger.info(f"Retry: Option record for {record['contractSymbol']} on {record['lastTradeDate']} already exists, skipping insertion")
                except pyodbc.Error as retry_e:
                    logger.error(f"Retry failed for {record.get('contractSymbol', 'UNKNOWN')}: {retry_e}")

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        logger.info("Azure SQL connection closed")