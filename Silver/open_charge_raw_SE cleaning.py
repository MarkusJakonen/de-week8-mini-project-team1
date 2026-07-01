# %%
import pandas as pd
import geopandas as gpd

df = pd.read_csv('../Bronze/open_charge_raw_SE.csv')

# %%
# take dates until 2026 May
df["DateCreated"] = pd.to_datetime(df["DateCreated"], errors="coerce")

df = df[
    df["DateCreated"] <= "2026-05-31 23:59:59"
]

# Standardize column text
df_silver = pd.DataFrame({
    "id": df["ID"],
    "number_of_points": df["NumberOfPoints"],
    "year": df["DateCreated"].dt.year,
    'month': df["DateCreated"].dt.month,
    "is_operational": df["StatusType.IsOperational"],
    "country": df["AddressInfo.Country.Title"],
    "longitude": df["AddressInfo.Longitude"],
    "latitude": df["AddressInfo.Latitude"],
    "fetch_timestamp": df["fetch_timestamp"],
    'rejection_reason' : pd.NA
})

def add_rejection_reason(mask, reason):
    df_silver.loc[mask, "rejection_reason"] = (
        df_silver.loc[mask, "rejection_reason"]
        .fillna("")
        .apply(lambda x: f"{x}; {reason}" if x else reason)
        .replace("", pd.NA)
    )
#%%
df_silver["id"] = (
    pd.to_numeric(df_silver["id"], errors="coerce")
    .astype("Int64")
)

# id should be numeric and >= 1
invalid_id = df_silver[
    df_silver["id"].isna()
    | (df_silver["id"] < 1)
]

add_rejection_reason(
    invalid_id.index,
    "INVALID_ID"
)

print("\n=== Ids ===")
print(f"Invalid ids: {len(invalid_id)}")

#%%
df_silver["number_of_points"] = (
    pd.to_numeric(df_silver["number_of_points"], errors="coerce")
    .astype("Int64")
)

# Number of points should be numeric and >= 1
invalid_number_of_points = df_silver[
    df_silver["number_of_points"].isna()
    | (df_silver["number_of_points"] < 1)
]

add_rejection_reason(
    invalid_number_of_points.index,
    "INVALID_NUMBER_OF_POINTS"
)

print("\n=== Number of points ===")
print(f"Invalid number of points: {len(invalid_number_of_points)}")

#%%

# Invalid dates
invalid_dates = df_silver[
    df_silver["year"].isna()
]

# Valid years: until 2026 May
invalid_dates = df_silver[
    (df_silver["year"] == 2026)
        & (df_silver["month"] > 5)
    | df_silver["year"].isna()
    | df_silver["month"].isna()
]

# Invalid month
invalid_month = df_silver[
    ~df_silver["month"].between(1, 12)
]

add_rejection_reason(
    invalid_dates.index,
    "INVALID_DATE"
)

add_rejection_reason(
    invalid_month.index,
    "INVALID_MONTH"
)

print("=== Date checks ===")
print(f"Invalid dates: {len(invalid_dates)}")
print(f"Invalid months: {len(invalid_month)}")
#%%
df_silver["country"] = df_silver["country"].astype("string").str.strip().str.title()

# Country should be Sweden
invalid_country = df_silver[
    df_silver["country"].isna()
    | (~df_silver["country"].eq('Sweden'))
]

add_rejection_reason(
    invalid_country.index,
    "INVALID_COUNTRY"
)

print("\n=== Countries ===")
print(f"Invalid Countries: {len(invalid_country)}")
# %%
df_silver["longitude"] = pd.to_numeric(df_silver["longitude"], errors="coerce")
df_silver["latitude"] = pd.to_numeric(df_silver["latitude"], errors="coerce")

# 1. Missing coordinates
missing_coordinates = df_silver[
    df_silver["longitude"].isna() | df_silver["latitude"].isna()
]

# 2. Zero coordinates
zero_coordinates = df_silver[
    (df_silver["longitude"] == 0) | (df_silver["latitude"] == 0)
]

# 3. Outside Sweden bounding box
outside_sweden = df_silver[
    df_silver["longitude"].notna()
    & df_silver["latitude"].notna()
    & (
        ~df_silver["latitude"].between(55.3, 69.1)
        | ~df_silver["longitude"].between(10.9, 24.2)
    )
]

# 4. Possible swapped lat/lon
swapped_coordinates = df_silver[
    df_silver["longitude"].between(55.3, 69.1)
    & df_silver["latitude"].between(10.9, 24.2)
]

add_rejection_reason(
    missing_coordinates.index,
    "MISSING_COORDINATES"
)

add_rejection_reason(
    zero_coordinates.index,
    "ZERO_COORDINATES"
)

add_rejection_reason(
    outside_sweden.index,
    "OUTSIDE_SWEDEN"
)

add_rejection_reason(
    swapped_coordinates.index,
    "POSSIBLE_SWAPPED_COORDINATES"
)

print("\n=== Coordinate checks ===")
print(f"Missing coordinates: {len(missing_coordinates)}")
print(f"Zero coordinates: {len(zero_coordinates)}")
print(f"Outside Sweden: {len(outside_sweden)}")
print(f"Swapped coordinates: {len(swapped_coordinates)}")

# %%
# Municipality boundaries
municipalities = gpd.read_file("Kommun_Sweref99TM/Kommun_Sweref99TM.shp")

# Region boundaries
regions = gpd.read_file("LanSweref99TM/Lan_Sweref99TM_region.shp")

# Create geospatial points from coordinates
points = gpd.GeoDataFrame(
    df_silver.reset_index(drop=True),
    geometry=gpd.points_from_xy(df_silver["longitude"], df_silver["latitude"]),
    crs="EPSG:4326"
)

# Match municipalities
points_municipality = points.to_crs(municipalities.crs)

municipality_result = gpd.sjoin_nearest(
    points_municipality,
    municipalities[["KnKod", "KnNamn", "geometry"]],
    how="left",
    distance_col="distance_to_municipality"
)

df_silver["municipality"] = municipality_result["KnNamn"].values
df_silver["distance_to_municipality"] = municipality_result["distance_to_municipality"].values

# Match regions
points_region = points.to_crs(regions.crs)

region_result = gpd.sjoin_nearest(
    points_region,
    regions[["LnKod", "LnNamn", "geometry"]],
    how="left",
    distance_col="distance_to_region"
)

df_silver["region"] = region_result["LnNamn"].values

# Fixing the names
COUNTY_NAME_MAP = {
    "Stockholms": "Stockholm",
    "Uppsala": "Uppsala",
    "Södermanlands": "Södermanland",
    "Östergötlands": "Östergötland",
    "Jönköpings": "Jönköping",
    "Kronobergs": "Kronoberg",
    "Kalmar": "Kalmar",
    "Gotlands": "Gotland",
    "Blekinge": "Blekinge",
    "Skåne": "Skåne",
    "Hallands": "Halland",
    "Västra Götalands": "Västra Götaland",
    "Värmlands": "Värmland",
    "Örebro": "Örebro",
    "Västmanlands": "Västmanland",
    "Dalarnas": "Dalarna",
    "Gävleborgs": "Gävleborg",
    "Västernorrlands": "Västernorrland",
    "Jämtlands": "Jämtland",
    "Västerbottens": "Västerbotten",
    "Norrbottens": "Norrbotten",
}

df_silver["region"] = df_silver["region"].replace(COUNTY_NAME_MAP)

# QUALITY TESTS
# Municipality should exist
missing_municipality = df_silver[
    df_silver["municipality"].isna()
]

# Region should exist
missing_region = df_silver[
    df_silver["region"].isna()
]

# Valid Swedish regions
VALID_REGIONS = {
    "Blekinge", "Dalarna", "Gotland", "Gävleborg",
    "Halland", "Jämtland", "Jönköping", "Kalmar",
    "Kronoberg", "Norrbotten", "Skåne", "Stockholm",
    "Södermanland", "Uppsala", "Värmland",
    "Västerbotten", "Västernorrland", "Västmanland",
    "Västra Götaland", "Örebro", "Östergötland"
}

invalid_regions = df_silver[
    df_silver["region"].notna()
    & ~df_silver["region"].isin(VALID_REGIONS)
]

# Municipality-region combinations should be unique
invalid_municipality_region = (
    df_silver.groupby("municipality")["region"]
    .nunique()
)

invalid_municipality_region = invalid_municipality_region[
    invalid_municipality_region > 1
]

bad_municipalities = invalid_municipality_region.index

invalid_municipality_region_rows = df_silver[
    df_silver["municipality"].isin(bad_municipalities)
]

add_rejection_reason(
    missing_region.index,
    "MISSING_REGION"
)

add_rejection_reason(
    missing_municipality.index,
    "MISSING_MUNICIPALITY"
)

add_rejection_reason(
    invalid_regions.index,
    "INVALID_REGION"
)

add_rejection_reason(
    invalid_municipality_region_rows.index,
    "INVALID_MUNICIPALITY_REGION"
)

far_from_municipality = df_silver[
    df_silver["distance_to_municipality"] > 1000
]

add_rejection_reason(
    far_from_municipality.index,
    "FAR_FROM_MUNICIPALITY"
)

print("\n=== Geospatial checks ===")
print(f"Missing municipalities: {len(missing_municipality)}")
print(f"Missing regions: {len(missing_region)}")
print(f"Invalid region names: {len(invalid_regions)}")
print(f"Municipalities with multiple regions: {len(invalid_municipality_region)}")
print(f"Coordinates far from municipality: {len(far_from_municipality)}")


# %%
valid_rows = df_silver[df_silver['rejection_reason'].isna()]
rejected_rows = df_silver[~df_silver["rejection_reason"].isna()]

valid_rows = valid_rows.drop(columns="distance_to_municipality")
rejected_rows = rejected_rows.drop(columns="distance_to_municipality")

# %%
valid_rows.to_csv('../Silver/silver_ev_charging_stations_SE.csv', index=False)
rejected_rows.to_csv('../Silver/REJECTED_silver_ev_charging_stations_SE.csv', index=False)

