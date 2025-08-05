import os
import time
import datetime
import pandas as pd
from rules import *
from preprocess import *
from methods.cityClustering import *
from preprocessVendor import *
from preprocessOutput import *
from preprocessCustomer import *
#from main_merge import run_pipeline  # import your refactored function


def run_pipeline(input_folder, isVendor, isCustomer, isMaterial, materialType, rules_dir, output_dir, preprocess):
    # -------------------------
    # CONFIGURATION SECTION
    # -------------------------

    # input_folder = r"C:\Users\avneka\OneDrive - Biocon Limited\Data Management Office - Documents\Data Management Office\Data Cleansing\Python\Scripts\Vendor\Input Sheets"
    # isVendor = True
    # isCustomer = False
    # isMaterial = False
    # materialType = ""
    # rules_dir = r"C:\Users\avneka\OneDrive - Biocon Limited\Data Management Office - Documents\Data Management Office\Data Cleansing\Python\Scripts\Code\rulebook"
    # output_dir = r"C:\Users\avneka\OneDrive - Biocon Limited\Data Management Office - Documents\Data Management Office\Data Cleansing\Python\Scripts\Vendor\GV test downloads"
    # preprocess = True

    # -------------------------
    # SHEET CONFIGURATION
    # -------------------------

    vendor_sheets = ['lfa1', 'lfb1', 'lfm1', 'lfbk', 'adrc']
    customer_sheets = ['kna1', 'knb1', 'knvv', 'knkk', 'knb5', 'adr6', 'account', 'contact']
    material_sheets = ['mara', 'marc', 'mbew', 'potext', 'mvke', 'mlan']

    if isVendor:
        allowed_sheets = vendor_sheets
        output_file = os.path.join(input_folder, "VendorMaster.xlsx")
    elif isCustomer:
        allowed_sheets = customer_sheets
        output_file = os.path.join(input_folder, "CustomerMaster.xlsx")
    elif isMaterial:
        if materialType == "":
            raise ValueError("Please specify materialType if isMaterial is True.")
        allowed_sheets = material_sheets
        output_file = os.path.join(input_folder, "MaterialMaster.xlsx")
    else:
        raise Exception("Please specify one of isVendor / isCustomer / isMaterial as True.")

    # -------------------------
    # FUNCTION TO COMBINE FILES
    # -------------------------

    def combine_excels_to_one_workbook(input_folder, output_file, allowed_sheets):
        print("[COMBINING INPUT FILES INTO ONE EXCEL WORKBOOK]...")

        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            for filename in os.listdir(input_folder):
                if filename.startswith('~$') or not filename.endswith(('.xlsx', '.xls','.XLSX')):
                    continue

                sheet_name = os.path.splitext(filename)[0].lower()
                if sheet_name not in allowed_sheets:
                    continue

                file_path = os.path.join(input_folder, filename)
                try:
                    df = pd.read_excel(file_path, sheet_name=0)
                    if not df.empty:
                        df.to_excel(writer, sheet_name=sheet_name.upper()[:31], index=False)
                        print(f" - Added sheet: {sheet_name}")
                    else:
                        print(f"   [SKIPPED] {sheet_name} is empty.")
                except Exception as e:
                    print(f"   [ERROR] Could not process {filename}: {e}")

        print(f"\n[SAVED CONSOLIDATED WORKBOOK TO]: {output_file}")
        return output_file

    # -------------------------
    # MAIN EXECUTION
    # -------------------------

    def filter_issues(col, issues):
        filtered = issues.split('; ')
        return '; '.join([i for i in filtered if col in i])

    start = time.time()

    # Step 1: Combine individual Excel files into a single workbook
    consolidated_file = combine_excels_to_one_workbook(input_folder, output_file, allowed_sheets)

    # Step 2: Set the consolidated file as the input data path
    data_path = consolidated_file

    # Step 3: Apply Preprocessing if enabled
    print('\n[READING INPUT FILES]...')

    if isVendor:
        if preprocess:
            data_path = preprocessVendorData(data_path)
        sheets = vendor_sheets
    elif isCustomer:
        if preprocess:
            data_path = preprocessCustomerData(data_path)
        sheets = customer_sheets
    elif isMaterial:
        sheets = material_sheets
    else:
        raise Exception("Please specify master data.")

    # Step 4: Loop through each relevant sheet in the workbook
    suffix = str(datetime.date.today()).replace("-", "") + str(datetime.datetime.now().time()).replace(":", "").replace(".", "_")

    for sheet in sheets:
        print(f'\n[WORKING ON {sheet.upper()}]...')

        if sheet == 'lfa1':
            #columns = ['Supplier', 'Last PO Date', 'Last BFN Date', 'Invoice Open?', 'Last Invoice Posting Date',
             columns = ['Supplier',
                       'Name 1', 'Name 2', 'Name 3', 'Name 4', 'Street', 'City', 'Country', 'PO Box', 
                       'P.O. Box Postal Code', 'Postal Code', 'Telephone 1', 'Telephone 2', 'Language Key', 'Address', 
                       'Plant', 'Tax Jurisdiction', 'Account Group', 'Tax Number 3', 'Created on', 'Created by',
                       'Block function', 'Payment block', 'Central del.block', 'Central posting block', 'Central purchasing block']
        if sheet == 'lfb1':
            #columns = ['Supplier', 'Last PO Date', 'Last BFN Date', 'Invoice Open?', 'Last Invoice Posting Date',
             columns = ['Supplier',
                       'Company Code', 'Terms of Payment', 'Reconciliation acct', 'Posting block for company code',
                       'Deletion Flag for Company Code', 'Planning group', 'Tolerance group', 'Payment methods', 
                       'Created on', 'Created by', 'MSME Status']
        if sheet == 'lfm1':
            #columns = ['Supplier', 'Last PO Date', 'Last BFN Date', 'Invoice Open?', 'Last Invoice Posting Date', 'City',
             columns = ['Supplier','City',
                       'Purch. block for purchasing organization', 'Purch. Organization', 'Purchasing Group', 
                       'Order currency', 'Confirmation Control', 'Incoterms', 'Incoterms (Part 2)', 'MSME Status', 
                       'MSME Number', 'MSME Issue Date', 'ABAC Status', 'ABAC Reason', 'GR-Based Inv. Verif.', 
                       'Service-Based Invoice Verification', 'Delete flag for purchasing organization']
        if sheet == 'lfbk':
            #columns = ['Supplier', 'Last PO Date', 'Last BFN Date', 'Invoice Open?', 'Last Invoice Posting Date',
            columns = ['Supplier',
                       'Account holder', 'Bank Country', 'Bank Key', 'Bank Account']
        if sheet == 'adrc':
            #columns = ['Supplier', 'Last BFN Date', 'Invoice Open?', 'Last Invoice Posting Date', 'Address Number',
             columns = ['Supplier', 'Address Number',
                       'Street', 'Street 2', 'Street 3', 'Street 4', 'Street 5', 'Postal Code', 'PO Box Postal Code', 
                       'PO Box', 'Country']
        if sheet == 'kna1':
            columns = ['Customer', 'SalesforceID', 'Open Pipeline', 'All Time Customer', 'Open Project?', 'Open Sales Order?', 
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
                       'Prod. stor. location', 'Batch management', 'ABC Indicator', 'Procurement type', 
                       'Availability check', 'CAS number (pharm.)', 'Prodn Supervisor', 'Prod.Sched.Profile', 
                       'Certificate type', 'Acct Assignment Cat.']
            
        if sheet == 'mbew':
            columns = ['Material', 'Valuation Category', 'Valuation Class', 'Price Control', 'Valuation Area', 
                       'Valuation Type']

        if sheet == 'potext':
            columns = ['Material', 'Purchase Order Text', 'Created On', 'Created By']
            
        if sheet == 'mvke':
            columns = ['Material', 'Item category group', 'Acct Assmt Grp Mat.']
            
        if sheet == 'mlan':
            columns = ['Material', 'Tax ind. f. material']
        else:
            print(f"[SKIPPED] No columns defined for sheet: {sheet}")
            continue

        df = load_excel_data(data_path, sheet.upper(), columns)

        print(f'\n[APPLYING DATA QUALITY RULES - {sheet.upper()}]...')
        rulebook_path = os.path.join(rules_dir, f'{sheet.lower()}_rulebook.json')
        rules = load_rules(rulebook_path)

        results = apply_rules(df, rules)
        print('\n[DONE]')

        output_file = f'{suffix}_{sheet.lower()}.xlsx'
        output_path = os.path.join(output_dir, output_file)

        print('\n[PROCESSING RESULTS]...')
        final = preprocessOutput(results, output_path)
        print(f"\n[OUTPUT SAVED TO - {final}]")

    end = time.time()
    mins = (end - start) // 60
    secs = (end - start) % 60
    print(f'\n[TIME TAKEN - {int(mins)} MINS {secs:.0f} SECONDS]')
    return "Processing complete! Output saved to: " + output_dir


