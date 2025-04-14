valid_values = [
    '01',
    '02',
    '03',
    '04',
    '05',
    'RE'
]


def validate_shipping_conditions(value):
    return str(value) in valid_values