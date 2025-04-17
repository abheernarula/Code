
valid_codes = [
    "01", "1", # AGROCHEMICAL
    "02", "2",# BIG PHARMA / BIOTECH
    "03", "3",# MID -SIZE PHARMA / BIO
    "04", "4",# SMALL PHARMA / BIO
    "05", "5",# OTHERS
    "06", "6",# Pharma / Biotech
    "07", "7",# Animal health
    "AGROCHEMICAL",
    "BIG PHARMA /BIOTECH",
    "MID -SIZE PHARMA/BIO",
    "SMALL PHARMA/BIO",
    "OTHERS",
    "PHARMA / BIOTECH",
    "ANIMAL HEALTH"
]

def validate_customer_segment(value):
    try: 
        return (str(int(float(value))) in valid_codes)
    except:
        return (str(value).upper() in valid_codes)


# print(validate_customer_segment("01"))