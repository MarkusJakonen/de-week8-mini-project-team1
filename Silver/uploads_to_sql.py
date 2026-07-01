#%%
import os
import urllib.parse
from dotenv import load_dotenv
from sqlalchemy import create_engine
import pandas as pd

load_dotenv()

connection_string = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    f"SERVER={os.getenv('SQL_SERVER')};"
    f"DATABASE={os.getenv('SQL_DB_NAME')};"
    f"UID={os.getenv('SQL_USERNAME')};"
    f"PWD={os.getenv('SQL_PASSWORD')};"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
)

connection_url = (
    'mssql+pyodbc:///?odbc_connect='
    + urllib.parse.quote_plus(connection_string)
)

engine = create_engine(connection_url)
with engine.connect() as conn:
    print("Connected")
#%%
silver_df = pd.read_csv('../Silver/silver_ev_charging_stations_SE.csv')
rejected = pd.read_csv('../Silver/REJECTED_silver_ev_charging_stations_SE.csv')

silver_df.to_sql(
    "silver_ev_charging_stations",
    schema="silver",
    con=engine,
    if_exists="replace",
    index=False
)

rejected.to_sql(
    "REJECTED_silver_ev_charging_stations",
    schema="silver",
    con=engine,
    if_exists="replace",
    index=False
)
