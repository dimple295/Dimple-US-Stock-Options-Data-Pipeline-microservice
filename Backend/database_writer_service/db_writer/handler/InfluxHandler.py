# # db_writer/handler/InfluxHandler.py
# from django.conf import settings
# from influxdb_client import InfluxDBClient, Point, WritePrecision
# import os
# from db_writer.utils.logConfig import LogConfig

# logger = LogConfig()

# class InfluxHandler:
#     def __init__(self):
#         self.client = InfluxDBClient(
#             url=os.getenv("INFLUX_URL"),
#             token=os.getenv("INFLUX_TOKEN"),
#             org=os.getenv("INFLUX_ORG")
#         )
#         self.write_api = self.client.write_api()
#         self.bucket = os.getenv("INFLUX_BUCKET")

#     def write_data(self, data):
#         points = []
#         for r in data:
#             try:
#                 p = Point("stock_15min")\
#                     .tag("StockName", r["symbol"])\
#                     .time(r["datetime"], WritePrecision.NS)\
#                     .field("open", float(r["open"]))\
#                     .field("high", float(r["high"]))\
#                     .field("low", float(r["low"]))\
#                     .field("close", float(r["close"]))\
#                     .field("volume", int(r["volume"]))\
                    
#                 points.append(p)
#             except Exception as e:
#                 logger.warning(f"Skipping bad record: {e}")
#         if points:
#             self.write_api.write(bucket=self.bucket, record=points,write_precision=WritePrecision.NS)
#             logger.info(f"Influx: wrote {len(points)} points")



from django.conf import settings
from influxdb_client import InfluxDBClient, Point, WritePrecision
import os
from db_writer.utils.logConfig import LogConfig

logger = LogConfig()

class InfluxHandler:
    def __init__(self):
        try:
            self.client = InfluxDBClient(
                url=os.getenv("INFLUX_URL"),
                token=os.getenv("INFLUX_TOKEN"),
                org=os.getenv("INFLUX_ORG")
            )
            self.write_api = self.client.write_api()
            self.bucket = os.getenv("INFLUX_BUCKET")
            logger.info("InfluxDB client initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize InfluxDB client: {e}")
            raise

    def write_data(self, data):
        if not isinstance(data, list):
            logger.error(f"Invalid data format: expected list, got {type(data)}")
            return

        points = []
        for record in data:
            try:
                p = (
                    Point("stock_15min")
                    .tag("StockName", record["symbol"])
                    .time(record["datetime"], WritePrecision.NS)
                    .field("open", float(record["open"]))
                    .field("high", float(record["high"]))
                    .field("low", float(record["low"]))
                    .field("close", float(record["close"]))
                    .field("volume", int(record["volume"]))
                )
                points.append(p)
                logger.debug(f"Prepared InfluxDB point for symbol: {record['symbol']} at {record['datetime']}")
            except Exception as e:
                logger.warning(f"Skipping bad record for symbol {record.get('symbol', 'unknown')}: {e}")

        if points:
            try:
                self.write_api.write(bucket=self.bucket, record=points, write_precision=WritePrecision.NS)
                logger.info(f"Successfully wrote {len(points)} points to InfluxDB bucket '{self.bucket}'.")
            except Exception as e:
                logger.error(f"Failed to write points to InfluxDB: {e}")
        else:
            logger.warning("No valid points to write to InfluxDB.")

    def close(self):
        try:
            self.client.close()
            logger.info("InfluxDB client connection closed.")
        except Exception as e:
            logger.error(f"Error while closing InfluxDB client: {e}")
