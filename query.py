import os
from influxdb_client_3 import InfluxDBClient3, Point
import pandas as pd

import sys

def connectDB():
    token = os.environ.get("INFLUXDB_TOKEN")
    org = "Research"
    host = "https://us-east-1-1.aws.cloud2.influxdata.com"

    client = InfluxDBClient3(host=host, token=token, org=org, database="CG-Monitoramento")
    return client


def main():
    client = connectDB()
    database = "CG-Monitoramento"
    
    query = """
            SELECT *
            FROM "Experimentos"
            WHERE
            "ID" IN ('Ex5')
            """

    reader = client.query(query=query, language="sql")
    table = reader.read_all()
    print(table.to_pandas().to_markdown())      

main()

