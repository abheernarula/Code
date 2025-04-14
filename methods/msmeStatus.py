valid_values = [
    '00', '0', # No MSME
    '01', '1', # Micro Scale
    '02', '2', # Small Scale
    '03', '3' # Medium Scale
]

def validate_msme_number(value):
    return (str(value) in valid_values) or (str(int(float(value))) in valid_values)