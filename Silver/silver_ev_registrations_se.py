import pandas as pd
from pathlib import Path

input_path = Path("Bronze") / "new_car_registrations_SE.csv"
output_path = Path("Silver") / "silver_ev_registrations_se.csv"

county_map = {
    "01": "Stockholm",
    "03": "Uppsala",
    "04": "Södermanland",
    "05": "Östergötland",
    "06": "Jönköping",
    "07": "Kronoberg",
    "08": "Kalmar",
    "09": "Gotland",
    "10": "Blekinge",
    "12": "Skåne",
    "13": "Halland",
    "14": "Västra Götaland",
    "17": "Värmland",
    "18": "Örebro",
    "19": "Västmanland",
    "20": "Dalarna",
    "21": "Gävleborg",
    "22": "Västernorrland",
    "23": "Jämtland",
    "24": "Västerbotten",
    "25": "Norrbotten",
}

df = pd.read_csv(input_path, encoding="latin1")

df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
    .str.replace(",", "")
)

df = df.rename(columns={
    "fuel": "driving_power",
    "new_registered_passenger_cars_number": "number_of_new_registrations"
})

# Remove total Sweden rows
df = df[df["region"] != "00 Sweden"].copy()

# Save original geography column
df["area_raw"] = df["region"].astype(str).str.strip()

# Extract code and name from region column
df["area_code"] = df["area_raw"].str.extract(r"^(\d+)")
df["area_name"] = df["area_raw"].str.replace(r"^\d+\s+", "", regex=True)

# Keep only municipality rows
# County totals have 2-digit codes, municipalities have 4-digit codes
df = df[df["area_code"].str.len() > 2].copy()

# Create clean region and municipality
df["region"] = df["area_code"].str[:2].map(county_map)
df["municipality"] = df["area_name"]

df["country"] = "Sweden"

# Clean month column like 2006M01 → year 2006, month 1
df["year"] = df["month"].astype(str).str[:4].astype("Int64")
df["month"] = df["month"].astype(str).str[-2:].astype("Int64")
df = df[df["year"] >= 2016].copy()

# Clean driving power
df["driving_power"] = df["driving_power"].astype(str).str.strip().str.lower()

driving_power_map = {
    "petrol": "petrol",
    "diesel": "diesel",
    "electricity": "electricity",
    "electric hybrid": "electric hybrid",
    "plug-in hybrid": "plug-in hybrid",
    "ethanol/ethanol flexifuel": "petrol/ethanol",
    "gas/gas flex": "gas/gas flex",
    "other fuels": "other"
}

df["driving_power"] = df["driving_power"].replace(driving_power_map)

df["number_of_new_registrations"] = pd.to_numeric(
    df["number_of_new_registrations"],
    errors="coerce"
).astype("Int64")

df["fetch_timestamp"] = pd.to_datetime(df["fetch_timestamp"], errors="coerce")

silver_df = df[
    [
        "country",
        "year",
        "month",
        "region",
        "municipality",
        "number_of_new_registrations",
        "driving_power",
        "fetch_timestamp"
    ]
]

silver_df.to_csv(output_path, index=False)

print("Silver EV registrations Sweden created")
print("Rows:", len(silver_df))
print("Output:", output_path)
print(silver_df.head(20))
print(silver_df.dtypes)