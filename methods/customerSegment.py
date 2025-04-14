
valid_codes = [
    "01", # AGROCHEMICAL
    "02", # BIG PHARMA / BIOTECH
    "03", # MID -SIZE PHARMA / BIO
    "04", # SMALL PHARMA / BIO
    "05", # OTHERS
    "06", # Pharma / Biotech
    "07" # Animal health
]

def validate_customer_segment(value):
    return (str(value) in str(valid_codes)) or (str(int(float(value))) in str(valid_codes))