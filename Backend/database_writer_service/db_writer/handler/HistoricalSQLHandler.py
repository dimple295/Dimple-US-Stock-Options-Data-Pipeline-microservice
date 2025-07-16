# import pyodbc
# import socket
# import time
# from django.conf import settings
# from db_writer.utils.logConfig import LogConfig

# logger = LogConfig()

# class HistoricalSQLHandler:
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
#             logger.info(f"Attempting connection using driver: {driver}")
#             for attempt in range(1, self.max_retries + 1):
#                 try:
#                     logger.info(f"Connection attempt {attempt} of {self.max_retries} for driver {driver}")
#                     server_ip = socket.gethostbyname("dash-gtd02.database.windows.net")
#                     logger.info(f"Resolved server 'dash-gtd02.database.windows.net' to IP: {server_ip}")

#                     self.conn = pyodbc.connect(conn_str)
#                     self.cursor = self.conn.cursor()

#                     self.cursor.execute("SELECT 1 FROM sys.tables WHERE name = 'StockData'")
#                     if not self.cursor.fetchone():
#                         raise Exception("Table 'StockData' does not exist in database.")

#                     logger.info(f"Successfully connected to Azure SQL DB using driver {driver}")
#                     return
#                 except (pyodbc.Error, socket.gaierror) as e:
#                     logger.error(f"Connection attempt {attempt} failed with error: {e}")
#                     if attempt < self.max_retries:
#                         logger.info(f"Retrying in {self.retry_delay} seconds...")
#                         time.sleep(self.retry_delay)
#             logger.warning(f"All connection attempts failed using driver {driver}, trying next driver if available.")
#         raise Exception("All connection attempts failed for all drivers.")

#     def write_data(self, data):
#         if not isinstance(data, list):
#             logger.error(f"Invalid data format: expected list, got {type(data)}")
#             return

#         check_query = """
#             SELECT COUNT(*) 
#             FROM StockData 
#             WHERE StockName = ? AND Date = ?
#         """

#         insert_query = """
#             INSERT INTO StockData (StockName, Date, [Open], High, Low, [Close], Volume)
#             VALUES (?, ?, ?, ?, ?, ?, ?)
#         """

#         for record in data:
#             try:
#                 symbol = record['symbol']
#                 date = record['datetime'].split(' ')[0]
#                 values = (
#                     symbol,
#                     date,
#                     float(record['open']),
#                     float(record['high']),
#                     float(record['low']),
#                     float(record['close']),
#                     int(record['volume'])
#                 )

#                 logger.debug(f"Processing record for {symbol} on {date}")

#                 self.cursor.execute(check_query, (symbol, date))
#                 exists = self.cursor.fetchone()[0]

#                 if exists == 0:
#                     self.cursor.execute(insert_query, values)
#                     self.conn.commit()
#                     logger.info(f"Inserted record for {symbol} on {date}")
#                 else:
#                     logger.info(f"Record already exists for {symbol} on {date}, skipping insertion.")
            
#             except pyodbc.Error as e:
#                 logger.error(f"Database error while processing record for {symbol} on {date}: {e}")
#                 logger.info("Attempting to reconnect and retry insertion...")
#                 self.connect()
#                 try:
#                     self.cursor.execute(check_query, (symbol, date))
#                     exists = self.cursor.fetchone()[0]
#                     if exists == 0:
#                         self.cursor.execute(insert_query, values)
#                         self.conn.commit()
#                         logger.info(f"Retry successful: Inserted record for {symbol} on {date}")
#                     else:
#                         logger.info(f"Retry: Record already exists for {symbol} on {date}, skipping insertion.")
#                 except pyodbc.Error as retry_e:
#                     logger.error(f"Retry failed for {symbol} on {date}: {retry_e}")
#             except Exception as ex:
#                 logger.error(f"Unexpected error processing record {record}: {ex}")

#     def close(self):
#         try:
#             if self.cursor:
#                 self.cursor.close()
#                 logger.info("Database cursor closed.")
#             if self.conn:
#                 self.conn.close()
#                 logger.info("Database connection closed.")
#         except Exception as e:
#             logger.error(f"Error during closing resources: {e}")

import psycopg2
import socket
import os
import time
import traceback
from django.conf import settings
from db_writer.utils.logConfig import LogConfig

logger = LogConfig()

class HistoricalSQLHandler:
    def __init__(self):
        self.conn_strings = [os.getenv('POSTGRES_CONNECTION_STRING', 'postgresql://sa:Passw0rd!@postgres:5432/us_stock_options_db')]
        self.max_retries = 5
        self.retry_delay = 30
        self.conn = None
        self.cursor = None
        logger.info("Waiting 30 seconds for PostgreSQL to be fully ready...")
        time.sleep(30)
        self.connect()

    def connect(self):
        """Establish a connection to the PostgreSQL database."""
        for conn_str in self.conn_strings:
            logger.info(f"Attempting connection using connection string: {conn_str}")
            for attempt in range(1, self.max_retries + 1):
                try:
                    server = "postgres"
                    server_ip = socket.gethostbyname(server)
                    logger.info(f"Resolved server '{server}' to IP: {server_ip}")

                    self.conn = psycopg2.connect(conn_str)
                    self.cursor = self.conn.cursor()

                    # Verify table existence
                    self.cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'StockData')")
                    if not self.cursor.fetchone()[0]:
                        raise Exception("Table 'StockData' does not exist in database.")

                    logger.info("Successfully connected to PostgreSQL")
                    return
                except (psycopg2.Error, socket.gaierror) as e:
                    logger.error(f"Connection attempt {attempt}/{self.max_retries} failed: {e}")
                    if attempt < self.max_retries:
                        logger.info(f"Waiting {self.retry_delay} seconds before retrying...")
                        time.sleep(self.retry_delay)
                    else:
                        logger.warning(f"All attempts failed for connection string.")
        raise Exception("All connection attempts failed.")

    def write_data(self, data):
        """Write data to the StockData table."""
        if not isinstance(data, list):
            logger.error(f"Data must be a list of records, got: {type(data)}")
            return

        logger.info(f"Starting edit_data for {len(data)} records")

        check_query = """
            SELECT COUNT(*) 
            FROM "StockData" 
            WHERE "StockName" = %s AND "Date" = %s
        """

        insert_query = """
            INSERT INTO "StockData" ("StockName", "Date", "Open", "High", "Low", "Close", "Volume")
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT ("StockName", "Date") DO UPDATE 
            SET "Open" = EXCLUDED."Open",
                "High" = EXCLUDED."High",
                "Low" = EXCLUDED."Low",
                "Close" = EXCLUDED."Close",
                "Volume" = EXCLUDED."Volume"
        """

        for record in data:
            try:
                symbol = record.get('symbol')
                date = record.get('datetime', '').split(' ')[0] if 'datetime' in record else None
                if not symbol or not date:
                    logger.error(f"Missing symbol or datetime in record: {record}")
                    continue

                values = (
                    symbol,
                    date,
                    float(record.get('open')) if record.get('open') is not None else None,
                    float(record.get('high')) if record.get('high') is not None else None,
                    float(record.get('low')) if record.get('low') is not None else None,
                    float(record.get('close')) if record.get('close') is not None else None,
                    int(record.get('volume')) if record.get('volume') is not None else None
                )
                logger.debug(f"Processing record: {symbol} on {date}")

                self.cursor.execute(check_query, (symbol, date))
                exists = self.cursor.fetchone()[0]

                if exists == 0:
                    self.cursor.execute(insert_query, values)
                    self.conn.commit()
                    logger.info(f"Inserted record for {symbol} on {date}")
                else:
                    self.cursor.execute(insert_query, values)
                    self.conn.commit()
                    logger.info(f"Updated record for {symbol} on {date}")

            except psycopg2.Error as e:
                logger.error(f"DB error processing record for {symbol} on {date}: {e}")
                self.conn.rollback()
                logger.info("Attempting to reconnect and retry insertion...")
                try:
                    self.connect()
                    self.cursor.execute(check_query, (symbol, date))
                    exists = self.cursor.fetchone()[0]
                    self.cursor.execute(insert_query, values)
                    self.conn.commit()
                    logger.info(f"Retry successful: Inserted/Updated record for {symbol} on {date}")
                except psycopg2.Error as retry_e:
                    logger.error(f"Retry failed for {symbol} on {date}: {retry_e}")
            except Exception as ex:
                logger.error(f"Unexpected error processing record {record}: {ex}\n{traceback.format_exc()}")

    def close(self):
        """Close database cursor and connection."""
        try:
            if self.cursor:
                self.cursor.close()
                logger.info("Database cursor closed.")
            if self.conn:
                self.conn.close()
                logger.info("Database connection closed.")
        except Exception as e:
            logger.error(f"Error during closing resources: {e}")
        finally:
            self.cursor = None
            self.conn = None