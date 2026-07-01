# Silver Python Transformations

This folder contains the Silver-layer transformation scripts and outputs for new car registration data from Finland and Sweden.

## Transformation Scripts

| Script | Input | Output |
|---|---|---|
| `silver_car_registrations_finland_script.ipynb` | `Bronze/new_car_registrations_FI.csv` | `silver_car_registrations_finland.csv` |
| `silver_new_car_registrations_totals_lookup_finland_script.ipynb` | `Bronze/new_car_registrations_FI.csv` | `silver_new_car_registrations_totals_lookup_FI.csv` |
| `silver_new_car_registrations_totals_lookup_sweden_script.ipynb` | `Bronze/new_car_registrations_SE.csv` | `silver_new_car_registrations_totals_lookup_SE.csv` |

All scripts read from the `Bronze` folder and write to the `Silver` folder. The scripts use `Path.cwd().parent` to locate the Bronze folder, so they must be run from within the Silver folder.

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

Region-level summary data for Finland. One row per region, month, and driving power category. The country-level total (`MAINLAND FINLAND`) is excluded — it can be derived by summing all regions.

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

Region-level summary data for Sweden. One row per region, month, and driving power category. The country-level total (`00 Sweden`) is excluded — it can be derived by summing all regions. Data range: 01/2016–05/2026.

| Column | Type | Description |
|---|---|---|
| `country` | str | Always `"Sweden"` |
| `year` | int | Registration year |
| `month` | int | Registration month (1–12) |
| `region` | str | Swedish county name, e.g. `"Stockholm"` |
| `number_of_new_registrations` | int | Number of newly registered passenger cars |
| `driving_power` | str | Standardized driving power category (see below) |
| `fetch_timestamp` | datetime | UTC timestamp from Bronze ingestion |

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

`Total` rows from both source files are dropped at the Silver level — totals can be derived by aggregating the individual driving power rows.

## Key Transformations

**`silver_car_registrations_finland_script.ipynb`**
- Municipality-level rows are extracted from the source, which also contains region-level and country-level summary rows.
- Each municipality is mapped to its region using a hardcoded dictionary (`MUNICIPALITY_TO_REGION`).
- Swedish-only municipality names are translated to their official Finnish names using a secondary mapping (`SWEDISH_TO_FINNISH_NAME`). Korsnäs is kept as-is since it has no separate Finnish name.
- `Unknown` and `Foreign countries` rows are retained with the area name used as both `region` and `municipality`.
- `Total` driving power rows are dropped.

**`silver_new_car_registrations_totals_lookup_finland_script.ipynb`**
- Only region-level summary rows (`MKxx ...`) are kept.
- Region names are cleaned by stripping the numeric MK code prefix (e.g. `MK01 Uusimaa` → `Uusimaa`).
- `Total` driving power rows are dropped.

**`silver_new_car_registrations_totals_lookup_sweden_script.ipynb`**
- Only region-level rows (two-digit numeric code) are kept.
- Region names are cleaned by stripping the numeric code prefix and ` county` suffix (e.g. `01 Stockholm county` → `Stockholm`). Former counties retain their `former` prefix (e.g. `former Älvsborg`).
- Data is filtered to 01/2016–05/2026 to align with the Finnish dataset.

## Silver Layer Purpose

The Silver layer stores cleaned, validated, and structured data ready for analytical use. Compared to Bronze, the key changes are:

- Rows are filtered to the relevant granularity (municipality-level or region-level)
- Column names are standardized
- Driving power categories are normalized to a common set of values
- `year` and `month` are split into separate integer columns
- Municipality names are standardized to Finnish
- Data types are explicitly set for downstream compatibility with the Gold layer