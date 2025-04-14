import pandas as pd

valid_gl_codes = pd.read_csv('methods/glCodesVendor.csv')['G/L Account'].astype(str).to_list()

def validate_gl_codes_vendor(value):
    return str(int(float(value))) in valid_gl_codes
