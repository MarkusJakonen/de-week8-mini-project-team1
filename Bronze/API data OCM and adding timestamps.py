#%%
import requests
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

OPENCHARGEMAP_API_KEY = os.getenv("OPENCHARGEMAP_API_KEY")

#%%
url = "https://api.openchargemap.io/v3/poi"

params = {
    "output": "json",
    "countrycode": "FI",
    "maxresults": 100000,
    "key": OPENCHARGEMAP_API_KEY
}

response = requests.get(url, params=params)

print(response.status_code)

data = response.json()

open_charge_raw_FI = pd.json_normalize(data)

open_charge_raw_FI["fetch_timestamp"] = pd.Timestamp.now('UTC')

open_charge_raw_FI.to_csv('open_charge_raw_FI.csv', index=False)

# %%

# import swedish data
url = "https://api.openchargemap.io/v3/poi"

params = {
    "output": "json",
    "countrycode": "SE",
    "maxresults": 100000,
    "key": OPENCHARGEMAP_API_KEY
}

response = requests.get(url, params=params)

print(response.status_code)

data = response.json()

open_charge_raw_SE = pd.json_normalize(data)

open_charge_raw_SE["fetch_timestamp"] = pd.Timestamp.now('UTC')

open_charge_raw_FI.to_csv('open_charge_raw_SE.csv', index=False)

#%%

new_car_registrations_finland = pd.read_csv('new_car_registrations_finland.csv',  encoding="latin1")
new_car_registrations_sweden = pd.read_csv('new_car_registrations_sweden.csv',  encoding="latin1")

new_car_registrations_finland["fetch_timestamp"] = pd.Timestamp.now('UTC')
new_car_registrations_sweden["fetch_timestamp"] = pd.Timestamp.now('UTC')

new_car_registrations_finland.to_csv('new_car_registrations_finland.csv',  encoding="utf-8", index=False)
new_car_registrations_sweden.to_csv('new_car_registrations_sweden.csv',  encoding="utf-8", index=False)
# %%
