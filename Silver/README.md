# Silver Python Transformations

This folder contains the Silver-layer transformation scripts and outputs for new car registration data and Swedish EV charging station data.

## Transformation Scripts

| Script | Input | Output |
|---|---|---|
| `silver_car_registrations_finland_script.ipynb` | `Bronze/new_car_registrations_FI.csv` | `silver_car_registrations_finland.csv` |
| `silver_new_car_registrations_totals_lookup_finland_script.ipynb` | `Bronze/new_car_registrations_FI.csv` | `silver_new_car_registrations_totals_lookup_FI.csv` |
| `silver_new_car_registrations_totals_lookup_sweden_script.ipynb` | `Bronze/new_car_registrations_SE.csv` | `silver_new_car_registrations_totals_lookup_SE.csv` |
| `silver_ev_charging_stations_SE_script.ipynb` | `Bronze/open_charge_raw_SE.csv` | `silver_ev_charging_stations_SE.csv`, `REJECTED_silver_ev_charging_stations_SE.csv` |

All scripts read from the `Bronze` folder and write to the `Silver` folder.

## Output Files

### `silver_car_registrations_finland.csv`

Municipality-level car registration data for Finland. One row per municipality, month, and driving power category.

| Column | Type | Description |
|---|---|---|
| `country` | str | Always `"Finland"` |
| `year` | int | Registration year |
| `month` | int | Registration month (1–12) |
| `region` | str | Finnish region (maakunta), e.g. `"Uusimaa"` |
| `municipality` | str | Finnish municipality name |
| `number_of_new_registrations` | int | Number of newly registered passenger cars |
| `driving_power` | str | Standardized driving power category (see below) |
| `fetch_timestamp` | datetime | UTC timestamp from Bronze ingestion |

### `silver_new_car_registrations_totals_lookup_FI.csv`

Region-level summary data for Finland. One row per region, month, and driving power category. The country-level total (`MAINLAND FINLAND`) is excluded since it can be derived by summing all regions.

| Column | Type | Description |
|---|---|---|
| `country` | str | Always `"Finland"` |
| `year` | int | Registration year |
| `month` | int | Registration month (1–12) |
| `region` | str | Finnish region (maakunta), e.g. `"Uusimaa"` |
| `number_of_new_registrations` | int | Number of newly registered passenger cars |
| `driving_power` | str | Standardized driving power category (see below) |
| `fetch_timestamp` | datetime | UTC timestamp from Bronze ingestion |

### `silver_new_car_registrations_totals_lookup_SE.csv`

Region-level summary data for Sweden. One row per region, month, and driving power category. The country-level total (`00 Sweden`) is excluded since it can be derived by summing all regions. Data range: 01/2016–05/2026.

| Column | Type | Description |
|---|---|---|
| `country` | str | Always `"Sweden"` |
| `year` | int | Registration year |
| `month` | int | Registration month (1–12) |
| `region` | str | Swedish county name, e.g. `"Stockholm"` |
| `number_of_new_registrations` | int | Number of newly registered passenger cars |
| `driving_power` | str | Standardized driving power category (see below) |
| `fetch_timestamp` | datetime | UTC timestamp from Bronze ingestion |

### `silver_ev_charging_stations_SE.csv`

Validated and enriched Swedish EV charging station data. One row per charging station.

| Column | Type | Description |
|---|---|---|
| `id` | int | Charging station identifier from Open Charge Map |
| `number_of_points` | int | Number of charging points at the station |
| `year` | int | Year the station was created |
| `month` | int | Month the station was created |
| `is_operational` | bool | Operational status of the charging station |
| `country` | str | Always `"Sweden"` |
| `longitude` | float | Longitude coordinate |
| `latitude` | float | Latitude coordinate |
| `municipality` | str | Nearest Swedish municipality |
| `region` | str | Swedish county |
| `fetch_timestamp` | datetime | UTC timestamp from Bronze ingestion |
| `rejection_reason` | str | Empty for valid records |

### `REJECTED_silver_ev_charging_stations_SE.csv`

Contains records that failed one or more Silver-layer validation rules. The structure matches the valid dataset, but the `rejection_reason` column contains one or more validation codes describing why the row was rejected.

## Driving Power Categories

Both countries use the same standardized `driving_power` values where possible. `electric hybrid` appears only in Swedish data.

| Silver value | Finland source | Sweden source |
|---|---|---|
| `petrol` | Petrol | petrol |
| `diesel` | Diesel | diesel |
| `electricity` | Electricity | electricity |
| `plug-in hybrid` | Petrol/Electricity (plug-in hybrid), Diesel/Electricity (plug-in hybrid) | plug-in hybrid |
| `electric hybrid` | — | electric hybrid |
| `gas/gas flex` | Natural gas (CNG), Petrol/CNG | gas/gas flex |
| `petrol/ethanol` | Petrol/Ethanol | ethanol/ethanol flexifuel |
| `other` | Other | other fuels |

`Total` rows from both source files are dropped at the Silver level since totals can be derived by aggregating the individual driving power rows.

## Key Transformations

### `silver_car_registrations_finland_script.ipynb`

- Municipality-level rows are extracted from the source, which also contains region-level and country-level summary rows.
- Each municipality is mapped to its region using a hardcoded dictionary (`MUNICIPALITY_TO_REGION`).
- Swedish-only municipality names are translated to their official Finnish names using a secondary mapping (`SWEDISH_TO_FINNISH_NAME`). Korsnäs is kept as-is since it has no separate Finnish name.
- `Unknown` and `Foreign countries` rows are retained with the area name used as both `region` and `municipality`.
- `Total` driving power rows are dropped.

### `silver_new_car_registrations_totals_lookup_finland_script.ipynb`

- Only region-level summary rows (`MKxx ...`) are kept.
- Region names are cleaned by stripping the numeric MK code prefix (e.g. `MK01 Uusimaa` → `Uusimaa`).
- `Total` driving power rows are dropped.

### `silver_new_car_registrations_totals_lookup_sweden_script.ipynb`

- Only region-level rows (two-digit numeric code) are kept.
- Region names are cleaned by stripping the numeric code prefix and ` county` suffix (e.g. `01 Stockholm county` → `Stockholm`). Former counties retain their `former` prefix.
- Data is filtered to 01/2016–05/2026 to align with the Finnish dataset.

### `silver_ev_charging_stations_SE_script.ipynb`

- Records are filtered to charging stations created up to **31 May 2026**.
- Relevant columns are selected and standardized.
- Numeric fields are converted to appropriate data types.
- Validation checks are performed on IDs, charging point counts, dates, country values, and geographic coordinates.
- Charging stations are spatially matched to Swedish municipalities and regions using GeoPandas and official Swedish boundary shapefiles.
- Region names are standardized to official county names.
- Municipality-region consistency is validated.
- Invalid rows receive one or more rejection codes in the `rejection_reason` column.
- Valid and rejected records are written to separate output files.

### EV Charging Station Validation Rules

Possible rejection reasons include:

- `INVALID_ID`
- `INVALID_NUMBER_OF_POINTS`
- `INVALID_DATE`
- `INVALID_MONTH`
- `INVALID_COUNTRY`
- `MISSING_COORDINATES`
- `ZERO_COORDINATES`
- `OUTSIDE_SWEDEN`
- `POSSIBLE_SWAPPED_COORDINATES`
- `MISSING_REGION`
- `MISSING_MUNICIPALITY`
- `INVALID_REGION`
- `INVALID_MUNICIPALITY_REGION`
- `FAR_FROM_MUNICIPALITY`

## Silver Layer Purpose

The Silver layer stores cleaned, validated, standardized, and structured data ready for analytical use. Compared to Bronze, the key transformations include:

- Filtering rows to the required level of detail
- Standardizing column names
- Normalizing driving power categories
- Splitting dates into `year` and `month`
- Standardizing municipality and region names
- Validating data types and business rules
- Validating geographic coordinates
- Enriching EV charging stations with municipality and region information
- Separating valid and rejected records for data quality monitoring