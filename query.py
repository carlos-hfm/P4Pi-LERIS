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
    
    if len(sys.argv) == 2:
        query = f"""
                    SELECT *
                    FROM "Experimentos"
                    WHERE
                    "ID" IN ('{sys.argv[1]}')
                """

        data = client.query(query=query, language="sql")
        df = data.to_pandas().sort_values(by="time")
        print(df)
        df.to_csv(f"INT_data/{sys.argv[1]}.csv")
    else :
        print("Espera-se 1 argumento: ID do experimento...")  


main()

