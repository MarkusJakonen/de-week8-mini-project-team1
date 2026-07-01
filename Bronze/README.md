# Bronze Python Ingestion

This folder contains the Bronze-layer raw ingestion outputs for Open Charge Map charging point data and new car registration data.

## Ingestion Flow

The ingestion script is `API data OCM and adding timestamps.py`.

1. Environment variables are loaded with `python-dotenv`.
2. The Open Charge Map API key is read from `OPENCHARGEMAP_API_KEY`.
3. Charging point data is requested from the Open Charge Map `/v3/poi` endpoint.
4. The API is called separately for:
   - Finland, using `countrycode=FI`
   - Sweden, using `countrycode=SE`
5. API responses are parsed as JSON and flattened into tabular format with `pandas.json_normalize`.
6. A UTC `fetch_timestamp` column is added to show when the data was fetched.
7. The raw charging point datasets are written to CSV files:
   - `open_charge_raw_FI.csv`
   - `open_charge_raw_SE.csv`

## Car Registration Timestamping

The script also reads existing local car registration CSV files:

- `new_car_registrations_FI.csv`
- `new_car_registrations_SE.csv`

Source information:

- `new_car_registrations_FI.csv`: Traficom, https://trafi2.stat.fi/PXWeb/pxweb/en/TraFi/TraFi__Ensirekisteroinnit/060_ensirek_tau_106.px/
- `new_car_registrations_SE.csv`: SCB, https://www.statistikdatabasen.scb.se/pxweb/en/ssd/START__TK__TK1001__TK1001A/PersBilarDrivMedel/

Each file is loaded with `pandas.read_csv`, a UTC `fetch_timestamp` column is added, and the file is written back to the same path. The files use `latin1` encoding.

## Bronze Layer Purpose

The Bronze layer stores raw or minimally processed source data. The main transformation added during ingestion is the `fetch_timestamp`, which helps track when each dataset was collected or refreshed.
