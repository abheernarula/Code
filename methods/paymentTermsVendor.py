import pandas as pd

valid_values = pd.read_csv('methods/paymentTermsVendor.csv')['Terms of Payment'].to_list()
valid = list(filter(lambda x: x.startswith('ZS'), valid_values))
    

def validatePaymentTermsVendor(isMSME, value):
    if isMSME == '00' or isMSME == '0' or pd.isnull(isMSME) or str(isMSME).lower() == 'nan' or str(isMSME).strip() == '':
        try:
            str(int(float(value)))
        except:
            return str(value).upper() in valid
        return str(int(float(value))).upper() in valid
    else:
        return str(value) == 'ZSA9'