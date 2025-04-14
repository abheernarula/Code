import pandas as pd

valid_gl_codes = pd.read_csv('methods/glCodesVendor.csv')
# valid_gl_codes = pd.read_csv('glCodes.csv')
# print(
#     int(float('66302020.0')) in valid_gl_codes[valid_gl_codes['Company Code'] == 5100]['G/L Account'].to_list()
# )

def validate_gl_codes_vendor(value):
    return str(int(float(value))) in valid_gl_codes['G/L Account'].to_list()