
from pyhive import hive
import pandas as pd

def get_data(query):
    # Example Hive connection
    # Note: Requires sasl and thrift system libs
    conn = hive.Connection(host="localhost", port=10000, username="ashmeet")
    return pd.read_sql(query, conn)

if __name__ == "__main__":
    print("🐝 PyHive client initialized...")
