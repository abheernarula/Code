
valid_codes = [
    "Company",
    "Dr.",
    "Miss",
    "Mr",
    "Mrs",
    "Ms",
    "Prof."
]

def validate_vendor_title(value):
    try: 
        return (str(int(float(value))) in valid_codes)
    except:
        return (str(value).upper() in valid_codes)


# print(validate_customer_segment("01"))