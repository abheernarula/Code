import re

gst_regex = '^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z]$'
pan_regex = '^[A-Z]{5}[0-9]{4}[A-Z]$'


def validate_gst_pan_number(value, isGST=False, isPan=False):
    if isGST:
        return bool(re.match(gst_regex, value))
    elif isPan:
        return bool(re.match(pan_regex, value))