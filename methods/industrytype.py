# Dictionary mapping valid industry type codes to their descriptions.
VALID_INDUSTRY_TYPES = {
    "Z001": "ELECTRONIC",
    "Z002": "PHARMA/ BIOTECH",
    "Z003": "MEDICAL DEVICES",
    "Z004": "AGROCHEMICAL",
    "Z005": "MEDICAL IMGNG & DGNS",
    "Z006": "PRFRMNCE & SP CHEMCL",
    "Z007": "POLYMER",
    "Z008": "UNIVERSITIES",
    "Z009": "PETROCHEMICAL",
    "Z010": "BIOPHARMACEUTICAL",
    "Z011": "CONTRACT SERVICE PRO",
    "Z012": "HOSPITALS",
    "Z013": "NUTRITION",
    "Z014": "CONSUMER HEALTH",
    "Z015": "VETERINARY"
}

def validate_industry_type(industry_code):
    return industry_code in VALID_INDUSTRY_TYPES

# # Example usage:
# test_industry_codes = ["Z001", "Z005", "Z016", "Z015"]

# for code in test_industry_codes:
#     if validate_industry_type(code):
#         print(f"Industry code '{code}' is valid: {VALID_INDUSTRY_TYPES[code]}")
#     else:
#         print(f"Industry code '{code}' is NOT valid.")
