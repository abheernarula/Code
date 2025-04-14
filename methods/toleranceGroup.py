valid_values = ['DEB1','DEB2','DEB3','DEB4','KRE1']

def validate_tolerance_group(value):
    return value.upper() in valid_values