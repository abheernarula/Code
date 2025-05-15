import re
import pandas as pd
import geonamescache
from rapidfuzz import process, fuzz

# 1) Load your DataFrame
# df = pd.read_csv("vendor_master.csv")  # example

# 2) Build your offline city list
gc = geonamescache.GeonamesCache()
all_cities = {c["name"] for c in gc.get_cities().values()}

def correct_city(val, threshold=95):
    if pd.isna(val):
        return val
    
    s = val.strip().title()
    
    # 4c) If there are digits or extra words, pull out the last “word group”
    #     e.g. "123 Street New York" → "New York"
    if re.search(r"\d", s) or "Street" in s or "(" in s:
        parts = re.findall(r"[A-Za-z ]+", s)
        if parts:
            s = parts[-1].strip()
    
    # 4d) Exact offline lookup
    if s in all_cities:
        return s
    
    # 4e) Fuzzy-match against known cities
    match, score, _ = process.extractOne(s, all_cities, scorer=fuzz.token_sort_ratio)
    if score >= threshold:
        return match
    
    # 4f) Nothing better found, return cleaned title case
    return s

s = {
    'City' : ['Bangalore', 'Bengaluru', 'BANGALO', 'Bengeluru', 'New York', 'Gujarat', 'Karnataka', 'Thane(W)',
              'Germany', 'India', '123 street, bangalore', 'Bangalore, karnataka']
}
df = pd.DataFrame(s)
# 5) Apply to your DataFrame
df["City_Clean"] = df["City"].apply(correct_city)

# 6) (Optional) See a few before/after
print(df[["City", "City_Clean"]].drop_duplicates())