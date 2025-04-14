valid_codes = [
    '01','1','1.0',
    '02','2','2.0',
    '03','3','3.0',
    '04','4','4.0',
    '05','5','5.0',
    '06','6','6.0',
    '99',
    'Z8',
    'Z9'
]


def validate_sales_order_blocking(value):
    return str(value) in valid_codes