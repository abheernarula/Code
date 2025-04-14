valid_values = [
    'compliant',
    'exception'
]


def validate_abac_status(value):
    return value.lower() in valid_values