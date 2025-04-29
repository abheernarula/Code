import os
import time
import datetime
import argparse
from rules import *
from preprocess import *
from methods.cityClustering import *
from preprocessVendor import *
from preprocessOutput import *
from preprocessCustomer import *

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
parser.add_argument("--isMaterial", "-m", help="Check if the input file is Material Master", default=False)
parser.add_argument("--materialType", "-mt", help="Material type", default="")
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
    sheets = ['lfa1', 'lfb1', 'lfm1', 'lfbk', 'adrc']
elif args.isCustomer:
    args.data = preprocessCustomerData(args.data)
    sheets = ['kna1', 'knb1', 'knvv', 'knkk', 'knb5', 'adr6', 'account', 'contact']
elif args.isMaterial:
    sheets = ['mara', 'marc', 'mbew', 'potext', 'mvke', 'mlan']
    if args.materialType == "":
        raise ValueError("Please specify Material type")
    print(f"[MATERIAL TYPE - {str(args.materialType).upper()}]")
else:
    raise Exception("Please specify master data")
    
suffix = str(datetime.date.today()).replace("-","") + str(datetime.datetime.now().time()).replace(":","").replace(".","_")
for sheet in sheets:
    print(f'\n[WORKING ON {sheet.upper()}]...')
    if sheet == 'lfa1':
        columns = ['Supplier', 'Last PO Date', 'Last BFN Date', 'Invoice Open?', 'Last Invoice Posting Date', 
                   'Name 1', 'Name 2', 'Name 3', 'Name 4', 'Street', 'City', 'Country', 'PO Box', 
                   'P.O. Box Postal Code', 'Postal Code', 'Telephone 1', 'Telephone 2', 'Language Key', 'Address', 
                   'Plant', 'Tax Jurisdiction', 'Account Group', 'Tax Number 3', 'Created on', 'Created by',
                   'Block function', 'Payment block', 'Central del.block', 'Central posting block', 
                   'Central purchasing block', 'Permanent account number']

    if sheet == 'lfb1':
        columns = ['Supplier', 'Last PO Date', 'Last BFN Date', 'Invoice Open?', 'Last Invoice Posting Date',
                   'Company Code', 'Terms of Payment', 'Reconciliation acct', 'Posting block for company code',
                   'Deletion Flag for Company Code', 'Planning group', 'Tolerance group', 'Payment methods', 
                   'Created on', 'Created by']
        
    if sheet == 'lfm1':
        columns = ['Supplier', 'Last PO Date', 'Last BFN Date', 'Invoice Open?', 'Last Invoice Posting Date', 'City',
                   'Purch. block for purchasing organization', 'Purch. Organization', 'Purchasing Group', 
                   'Order currency', 'Confirmation Control', 'Incoterms', 'Incoterms (Part 2)', 'MSME Status', 
                   'MSME Number', 'MSME Issue Date', 'ABAC Status', 'ABAC Reason', 'GR-Based Inv. Verif.', 
                   'Service-Based Invoice Verification', 'Delete flag for purchasing organization']
        
    if sheet == 'lfbk':
        columns = ['Supplier', 'Last PO Date', 'Last BFN Date', 'Invoice Open?', 'Last Invoice Posting Date',
                   'Account holder', 'Bank Country', 'Bank Key', 'Bank Account']
        
    if sheet == 'adrc':
        columns = ['Supplier', 'Last BFN Date', 'Invoice Open?', 'Last Invoice Posting Date', 'Address Number', 
                   'Street', 'Street 2', 'Street 3', 'Street 4', 'Street 5', 'Postal Code', 'PO Box Postal Code', 
                   'PO Box', 'Country']
        
    if sheet == 'kna1':
        columns = ['Customer', 'Open Pipeline', 'All Time Customer', 'Open Project?', 'Open Sales Order?', 
                   'Open Invoices', 'Last Invoice Posting Date', 'Country', 'Name 1', 'Name 2', 'Telephone 1', 
                   'Telephone 2', 'City', 'Street', 'Address', 'Postal Code', 'PO Box', 'P.O. Box Postal Code', 
                   'Account group', 'Tax Number 3', 'Tax Number 1', 'VAT Registration No.', 'Industry', 'Title', 
                   'Created by', 'Created on', 'Attribute 2']

    if sheet == 'knb1':
        columns = ['Customer', 'Open Pipeline', 'All Time Customer', 'Open Project?', 'Open Sales Order?', 
                   'Open Invoices', 'Last Invoice Posting Date', 'Company Code', 'Created by', 'Created on', 
                   'Reconciliation acct', 'Terms of Payment']

    if sheet == 'knkk':
        columns = ['Customer', 'Open Pipeline', 'All Time Customer', 'Open Project?', 'Open Sales Order?', 
                   'Open Invoices', 'Last Invoice Posting Date', 'Credit limit', 'Created by', 'Created on']
        
    if sheet == 'knvv':
        columns = ['Customer', 'Open Pipeline', 'All Time Customer', 'Open Project?', 'Open Sales Order?', 
                   'Open Invoices', 'Last Invoice Posting Date', 'Created By', 'Created On', 'Cust.Acct.Assg.Group', 
                   'Order block for sales area', 'Sales Organization', 'Distribution Channel', 'Division', 
                   'Cust.pric.procedure','Incoterms', 'Incoterms (Part 2)', 'Shipping Conditions']

    if sheet == 'knb5':
        columns = ['Customer', 'Open Pipeline', 'All Time Customer', 'Open Project?', 'Open Sales Order?', 
                   'Open Invoices', 'Last Invoice Posting Date', 'Dunning Procedure', 'Company Code']
        
    if sheet == 'adr6':
        columns = ['Customer', 'Open Pipeline', 'All Time Customer', 'Open Project?', 'Open Sales Order?', 
                   'Open Invoices', 'Last Invoice Posting Date', 'E-Mail Address']
        
    if sheet == 'account':
        columns = ['SAP_Account_Number__c', 'Open Pipeline', 'All Time Customer', 'Open Project?', 
                   'Open Sales Order?', 'Open Invoices', 'Last Invoice Posting Date', 'VAT_Number__c', 'Phone', 
                   'GST_Number__c', 'PAN_Number__c', 'BillingStreet', 'BillingAddress.street', 'BillingStateCode', 
                   'BillingPostalCode', 'Name', 'Industry_Sector__c', 'Industry', 'BillingCountryCode', 
                   'BillingAddress.countryCode', 'BillingCity', 'KTOKD__c', 'Customer_Type__c', 
                   'SAP_Customer_Creation_Date__c', 'CreatedDate', 'CreatedById','ZTERM__c', 'AKONT__c', 
                   'MAHNA__c', 'Total_Credit_Limit__c', 'Credit_Limit__c', 'VSBED__c', 'Sales_Organization__c',
                   'INCO1__c', 'INCO2__c', 'SPART__c', 'VTWEG__c', 'KALKS__c', 'KTGRD__c', 'CurrencyIsoCode', 
                   'Account_Currency__c','Company_Size__c', 'Business_Unit__c', 'Portfolio__c', 
                   'Customer_Category__c']

    if sheet == 'contact':
        columns = ['AccountId', 'SAP_Account_Number__c', 'Email', 'Open Pipeline', 'All Time Customer', 
                   'Open Project?', 'Open Sales Order?', 'Open Invoices', 'Last Invoice Posting Date', ]
        
    if sheet == 'mara':
        columns = ['Material', 'Material Type', 'Material Description', 'Material description', 
                   'Base Unit of Measure', 'Gen. item cat. grp', 'Material Group', 'Material Category',
                   'Industry', 'Int. material number', 'X-plant matl status', 'Division', 'catalog', 
                   'Transportation Group', 'Batch management', 'Mfr Part Profile',
                   'Purchasing value key', 'QM proc. active', 'Created On', 'Created By']
        
    if sheet == 'marc':
        columns = ['Material', 'Plant', 'Control code', 'Zone Category', 'Storage condition', 'QM Control Key', 
                   'Loading Group', 'Profit Center', 'MRP Controller', 'MRP Type', 'Purchasing Group', 
                   'Prod. stor. location', 'ABC Indicator', 'Procurement type', 'Availability check', 
                   'CAS number (pharm.)', 'Prodn Supervisor', 'Prod.Sched.Profile', 'Certificate type', 
                   'Acct Assignment Cat.']
        
    if sheet == 'mbew':
        columns = ['Material', 'Valuation Category', 'Valuation Class', 'Price Control', 'Valuation Area', 
                   'Valuation Type']

    if sheet == 'potext':
        columns = ['Material', 'Purchase Order Text', 'Created On', 'Created By']
        
    if sheet == 'mvke':
        columns = ['Material', 'Item category group', 'Acct Assmt Grp Mat.']
        
    if sheet == 'mlan':
        columns = ['Material', 'Tax ind. f. material']
        
    df = load_excel_data(args.data, sheet.upper(), columns)
    
    print(f'\n[APPLYING DATA QUALITY RULES - {sheet.upper()}]...')
    
    if args.isMaterial:
        rules_dir = os.path.join(args.rules, f'{args.materialType}_{sheet.lower()}_rulebook.json')
    else:
        rules_dir = os.path.join(args.rules, f'{sheet.lower()}_rulebook.json')
        
    rules = load_rules(rules_dir)
    results = apply_rules(df, rules)
    print('\n[DONE]')
    # print('\n[SAVING RESULTS]...')
    
    if args.isMaterial:
        output_path = os.path.join(output_dir, f'{suffix}_{args.materialType}_{sheet.lower()}.xlsx')
    else:
        output_path = os.path.join(output_dir, f'{suffix}_{sheet.lower()}.xlsx')
        
    print('\n[PROCESSING RESULTS]...')
    
    final = preprocessOutput(results, output_path)
    print(f"\n[OUTPUT SAVED TO - {final}]")
    
end = time.time()
mins = (end-start)//60
sec = abs((end-start) - mins*60)

print(f'\n[TIME TAKEN - {mins:.0f} MINS {sec:.0f} SECONDS]')
# print(results[['MSME Status','Issues']])