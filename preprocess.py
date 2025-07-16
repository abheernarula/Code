import pandas as pd 

def load_csv_data(path, columns):
    df = pd.read_csv(path, low_memory=False)
    return df[columns]

def load_excel_data(path, sheet, columns):
    df = pd.read_excel(path, sheet_name=sheet, dtype=str)
    return df[columns]

# def consolidate_data(kna1, knb1, sfdc):
#     sap_master = kna1.merge(knb1, on="Customer", how="left")
#     customer_master = sap_master.merge(sfdc, left_on="Customer", right_on="SAP_Account_Number__c", how="left")
#     return customer_master