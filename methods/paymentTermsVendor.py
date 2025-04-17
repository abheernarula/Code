import pandas as pd

valid_values = pd.read_csv('methods/paymentTermsVendor.csv')['Terms of Payment'].to_list()

def validatePaymentTermsVendor(value):
    try:
        str(int(float(value)))
    except:
        return str(value).upper() in valid_values
    return str(int(float(value))).upper() in valid_values