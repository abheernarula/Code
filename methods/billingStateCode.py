import pandas as pd

valid_codes = pd.read_csv('methods/BillingStateCodeValidationSFDC.csv')

# print(
#     int('66302020') in valid_gl_codes[valid_gl_codes['Company Code'] == 5100]['G/L Account'].to_list()
# )

def validate_billingStateCode(companyKey, value):
    valid = valid_codes[valid_codes['Country Key']==str(companyKey)]['Region'].to_list()
    try:
        str(int(float(value)))
    except:
        return str(value).upper() in valid
    return str(int(float(value))).upper() in valid

# print(valid_codes[valid_codes['Country Key']=='DK'])