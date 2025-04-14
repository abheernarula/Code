valid_codes = [
    '1',
    '2',
    '3',
    '4',
    '5',
    '6',
    '7',
    '8',
    '9'
]

def validate_price_procedure(value):
    return str(int(float(value))) in valid_codes