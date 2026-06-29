#%%
import requests
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
import os

BASE_DIR = Path.cwd()
OUTPUT_DIR = BASE_DIR / "Bronze" 
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

load_dotenv()

OPENCHARGEMAP_API_KEY = os.getenv("OPENCHARGEMAP_API_KEY")
print(OPENCHARGEMAP_API_KEY)

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

print(len(open_charge_raw_FI))
print(open_charge_raw_FI['DateCreated'].tail())

open_charge_raw_FI.to_csv(OUTPUT_DIR / 'open_charge_raw_FI.csv', index=False)

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
print(len(open_charge_raw_SE))
print(open_charge_raw_SE['DateCreated'].tail())

open_charge_raw_FI.to_csv(OUTPUT_DIR / 'open_charge_raw_SE.csv', index=False)
# %%
