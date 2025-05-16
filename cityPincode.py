import pandas as pd
import pgeocode

# 1. Read your Excel file
df = pd.read_excel("../Outputs/Vendor/Standard/5100_standardizedOutput.xlsx")         

SUPPORTED = set(pgeocode.Nominatim.available_postal_codes().keys())
nomi_cache = {}

def get_nominatim(country):
    if country not in SUPPORTED:
        raise KeyError(f"{country} not supported")
    if country not in nomi_cache:
        nomi_cache[country] = pgeocode.Nominatim(country)
    return nomi_cache[country]

def lookup_city(postal, country):
    if pd.isna(postal) or pd.isna(country):
        return None
    try:
        nomi = get_nominatim(country)
    except KeyError:
        return None  # or "Unsupported"
    res = nomi.query_postal_code(str(postal))
    return res.place_name


df["City_postal"] = df.apply(
    lambda row: lookup_city(row["Postal Code"], row["Country"]),
    axis=1
)

# 6) Write back out
df.to_excel("vendor_master_with_cities.xlsx", index=False)
