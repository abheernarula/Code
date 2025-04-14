import pandas as pd

valid_codes = pd.read_csv('methods/industryCode1.csv')

# print(
#     int('66302020') in valid_gl_codes[valid_gl_codes['Company Code'] == 5100]['G/L Account'].to_list()
# )
# print(valid_codes['Industry code'].to_list())

def validate_industry_code(value):
    return str(value) in valid_codes['Industry code'].to_list()
# def validate_billingStateCode(companyKey, value):
#     return str(value) in valid_codes[valid_codes['Country Key']==str(companyKey)]['Region'].to_list()
