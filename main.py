from ast import mod
import os
import time
import argparse
from rules import *
from preprocess import *
from methods.cityClustering import *
from preprocessVendor import *
from preprocessOutput import *

def filter_issues(col, issues):
    filtered = issues.split('; ')
    res = []
    for i in filtered:
        if col in i:
            res.append(i)

    return '; '.join(res)

parser = argparse.ArgumentParser(
    description="Apply data quality rules on consolidated customer master data"
)

parser.add_argument("--data", "-d", required=True, help="Path to excel data")
parser.add_argument("--isVendor", "-v", help="Check if the input file is Vendor Master", default=False)
parser.add_argument("--isCustomer", "-c", help="Check if the input file is Vendor Master", default=False)
parser.add_argument("--tables", "-t", help="Tables to apply rules", default="")
parser.add_argument("--rules", "-r", required=True, help="Path to folder containing rulebooks")

parser.add_argument("--output", "-o", help="Path to folder for output files")

args = parser.parse_args()
# rules = load_rules(args.rules)
output_dir = args.output
sheets = []

start = time.time()
print('\n[READING INPUT FILES]...')
if args.tables != '':
    sheets = args.tables.lower().split(',')
elif args.isVendor:
    args.data = preprocessVendorData(args.data)
    sheets = ['lfa1', 'lfb1', 'lfm1', 'lfbk']
elif args.isCustomer:
    sheets = ['kna1', 'knb1', 'knvv', 'knkk', 'knb5', 'adr6', 'account', 'contact']
else:
    pass
    

for sheet in sheets:
    print(f'\n[WORKING ON {sheet.upper()}]...')
    if sheet == 'lfa1':
        columns = ['Supplier', 'Name 1', 'Name 2', 'Name 3', 'Name 4', 'Street', 'City', 'Country', 'PO Box', 
                'P.O. Box Postal Code', 'Postal Code', 'Telephone 1', 'Telephone 2', 'Language Key',
                'Address', 'Plant', 'Tax Jurisdiction', 'Account Group', 'Tax Number 3', 'Created on', 'Created by',
                'Block function', 'Payment block', 'Central del.block', 'Central posting block', 
                'Central purchasing block']

    if sheet == 'lfb1':
        columns = ['Supplier', 'Company Code', 'Terms of Payment', 'Reconciliation acct', 'Posting block for company code',
                'Deletion Flag for Company Code', 'Planning group', 'Tolerance group', 'Payment methods', 
                'Created on', 'Created by']
        
    if sheet == 'lfm1':
        columns = ['Supplier', 'Purch. block for purchasing organization', 'Purch. Organization', 'Purchasing Group', 
                'Order currency', 'Confirmation Control', 'Incoterms', 'Incoterms (Part 2)', 'MSME Status', 
                'MSME Number', 'MSME Issue Date', 'ABAC Status', 'ABAC Reason', 'GR-Based Inv. Verif.', 
                'Service-Based Invoice Verification', 'Delete flag for purchasing organization']
        
    if sheet == 'lfbk':
        columns = ['Supplier', 'Account holder', 'Bank Country', 'Bank Key', 'Bank Account']
        
    if sheet == 'kna1':
        columns = ['Customer', 'Country', 'Name 1', 'Name 2', 'Telephone 1', 'Telephone 2', 'City', 'Street', 'Address',
                'Postal Code', 'PO Box', 'P.O. Box Postal Code', 'Account group', 'Tax Number 3', 'Tax Number 1',
                'VAT Registration No.', 'Industry', 'Title', 'Created by', 'Created on', 'Attribute 2']

    if sheet == 'knb1':
        columns = ['Customer', 'Company Code', 'Created by', 'Created on', 'Reconciliation acct', 'Terms of Payment']

    if sheet == 'knkk':
        columns = ['Customer', 'Credit limit', 'Created by', 'Created on']
        
    if sheet == 'knvv':
        columns = ['Customer', 'Created By', 'Created On', 'Cust.Acct.Assg.Group', 'Order block for sales area',
                'Sales Organization', 'Distribution Channel', 'Division', 'Cust.pric.procedure','Incoterms', 
                'Incoterms (Part 2)', 'Shipping Conditions']

    if sheet == 'knb5':
        columns = ['Customer', 'Dunning Procedure', 'Company Code']
        
    if sheet == 'adr6':
        columns = ['E-Mail Address']
        
    if sheet == 'account':
        columns = ['VAT_Number__c', 'Phone', 'GST_Number__c', 'PAN_Number__c', 'BillingStreet', 'BillingAddress.street',
                'BillingStateCode', 'BillingPostalCode', 'Name', 'Industry_Sector__c', 'Industry', 
                'SAP_Account_Number__c', 'BillingCountryCode', 'BillingAddress.countryCode', 'BillingCity', 'KTOKD__c',
                'Customer_Type__c', 'SAP_Customer_Creation_Date__c', 'CreatedDate', 'CreatedById','ZTERM__c',
                'AKONT__c', 'MAHNA__c', 'Total_Credit_Limit__c', 'Credit_Limit__c', 'VSBED__c', 
                'Sales_Organization__c','INCO1__c', 'INCO2__c', 'SPART__c', 'VTWEG__c', 'KALKS__c', 'KTGRD__c', 
                'CurrencyIsoCode', 'Account_Currency__c','Company_Size__c', 'Business_Unit__c', 'Portfolio__c', 
                'Customer_Category__c']

    if sheet == 'contact':
        columns = ['Email']
        
    df = load_excel_data(args.data, sheet.upper(), columns)
    
    print(f'\n[APPLYING DATA QUALITY RULES - {sheet.upper()}]...')
    rules_dir = os.path.join(args.rules, f'{sheet.lower()}_rulebook.json')
    rules = load_rules(rules_dir)
    results = apply_rules(df, rules)
    print('\n[DONE]')
    # print('\n[SAVING RESULTS]...')
    output_path = os.path.join(output_dir, f'{sheet.lower()}.xlsx')
    print('\n[PROCESSING RESULTS]...')
    final = preprocessOutput(results, output_path)

    print(f"\n[OUTPUT SAVED TO - {final}]")
end = time.time()
mins = (end-start)//60
sec = abs((end-start) - mins*60)

print(f'\n[TIME TAKEN - {mins:.0f} MINS {sec:.0f} SECONDS]')
# print(results[['MSME Status','Issues']])