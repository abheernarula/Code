valid = [
    '01', '1',
    '02', '2',
    '03', '3',
    '04', '4',
    '05', '5',
    'RE'
]


def validate_shipping_conditions(value):
    try:
        str(int(float(value)))
    except:
        return str(value) in valid
    return str(int(float(value))) in valid