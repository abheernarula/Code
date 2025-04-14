valid_values = [
    '5100', # Syngene Int Ltd
    '5300', # Syngene USA
    '5500' # Syngene Scientific
]


def validate_sales_org(value):
    return str(int(float(value))) in valid_values