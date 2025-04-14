valid_values = [
    '0001', # Confirmations
    '0004', # Inbound Delivery
    'Z001' # Confirmations on IBD
]

def validate_confirmation_controls(value):
    return (str(value) in valid_values) or (str(int(float(value))) in valid_values) 