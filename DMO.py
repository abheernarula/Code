import os
import time
import datetime
import argparse
import pandas as pd
import re
import io
import ast
from azure.storage.blob import BlobServiceClient

# Import your existing modules
from rules import *
from preprocess import *
from methods.cityClustering import *
from preprocessVendor import *
from preprocessCustomer import *
from preprocessMaterial import *

class DataQualityProcessor:
    def __init__(self):
        self.storage_config = None
        self.blob_service_client = None
        
    def load_storage_config(self):
        """Load ADLS storage configuration from file"""
        config_file = r"ADLS_AccessKey.txt"
        
        try:
            with open(config_file, 'r') as f:
                content = f.read().strip()
                
            if content.startswith('{'):
                self.storage_config = ast.literal_eval(content)
            else:
                config = {}
                for line in content.split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip().strip("'\"")
                        value = value.strip().strip("',\"")
                        config[key] = value
                self.storage_config = config
            
            # Initialize blob service client
            self.blob_service_client = BlobServiceClient(
                account_url=f"https://{self.storage_config['account_name']}.blob.core.windows.net",
                credential=self.storage_config['account_key']
            )
            
            print(f"✓ ADLS config loaded:")
            print(f"  Account: {self.storage_config['account_name']}")
            print(f"  Container: {self.storage_config['container_name']}")
            return True
            
        except Exception as e:
            print(f"✗ ADLS config error: {e}")
            return False

    def upload_excel_to_blob(self, excel_buffer, blob_name):
        """Upload Excel file from memory buffer to blob storage"""
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.storage_config['container_name'], 
                blob=blob_name
            )
            
            excel_buffer.seek(0)
            blob_client.upload_blob(excel_buffer.getvalue(), overwrite=True)
            
            print(f"✓ Excel uploaded to blob: {blob_name}")
            return True
        except Exception as e:
            print(f"✗ Excel blob upload failed: {e}")
            return False

    def upload_csv_to_blob(self, dataframe, blob_path):
        """Upload DataFrame as CSV to blob storage"""
        try:
            # Convert DataFrame to CSV in memory
            csv_buffer = io.StringIO()
            dataframe.to_csv(csv_buffer, index=False)
            csv_content = csv_buffer.getvalue()
            
            # Upload to blob
            blob_client = self.blob_service_client.get_blob_client(
                container=self.storage_config['container_name'], 
                blob=blob_path
            )
            
            blob_client.upload_blob(csv_content, overwrite=True)
            print(f"✓ CSV uploaded to blob: {blob_path}")
            return True
        except Exception as e:
            print(f"✗ CSV blob upload failed: {e}")
            return False

    def create_annexures_data(self, summary_df, metadata, sheet_name, total_rows):
        """Create data for DMO.Annexures table"""
        annexures_data = []
        
        for idx, row in summary_df.iterrows():
            annexures_record = {
                'SNo': idx + 1,
                'Particulars': row['Particulars'],
                'TotalRecords': row['Total Records'],
                'Domain': metadata['domain'],
                'System': metadata['system'],
                'TableName': sheet_name.upper(),
                'MaterialType': metadata.get('material_type', ''),
                'Dimension': 'Data Quality',
                'TotalRows': total_rows,
                'CreateDate': metadata['timestamp']
            }
            annexures_data.append(annexures_record)
        
        return pd.DataFrame(annexures_data)

    def create_dqrules_data(self, rules, metadata, sheet_name):
        """Create data for DMO.DQRules table"""
        dqrules_data = []
        
        for rule in rules:
            dqrules_record = {
                'SourceFieldName': rule.get('field', ''),
                'RuleID': rule.get('rule_id', f"RULE_{len(dqrules_data)+1:03d}"),
                'Domain': metadata['domain'],
                'SourceSystem': metadata['system'],
                'SourceTable': sheet_name.upper(),
                'MaterialType': metadata.get('material_type', ''),
                'Dimension': rule.get('dimension', 'Data Quality'),
                'DataQualityRule': rule.get('description', ''),
                'TechnicalFieldName': rule.get('technical_field', rule.get('field', '')),
                'CreateDate': metadata['timestamp']
            }
            dqrules_data.append(dqrules_record)
        
        return pd.DataFrame(dqrules_data)

    def filter_issues(self, col, issues):
        """Filter issues by column"""
        filtered = issues.split(', ')
        res = []
        for i in filtered:
            if col in i:
                res.append(i)
        return ', '.join(res)

    def preprocess_output(self, df, filename, metadata, sheet_name, rules):
        """
        Process output data and upload directly to blob storage without local storage
        """
        
        summary = [] 
        issueList = list(sorted(set([i.strip() for i in ','.join(df['Issues'].to_list()).split(',') if i.strip()])))
        i = 1
        
        # Create Excel file in memory
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Results', index=False)
            rows = df.shape[0]
            
            for issue in issueList:
                filter_df = df[df['Issues'].str.contains(re.escape(f"{issue}"), na=False)]
                filter_df['Issues'] = filter_df['Issues'].apply(lambda x: self.filter_issues(issue, x))
                summary.append({
                    'S.No.': f'Annexure {i}', 
                    'Particulars': issue, 
                    'Total Records': filter_df.shape[0],
                    'Total Rows': rows,
                    'Dimension': ''
                })
                filter_df.to_excel(writer, sheet_name=f'Annexure {i}', index=False)
                i += 1
                
            summary_df = pd.DataFrame(summary)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        summary_df.to_csv('summary.csv')
        
        # Upload files to blob storage
        if self.blob_service_client and metadata:
            try:
                # 1. Upload Excel file to blob storage
                blob_path = f"DMO/DataQuality/{metadata['domain']}/{sheet_name.upper()}/{filename}"
                
                upload_success = self.upload_excel_to_blob(excel_buffer, blob_path)
                
                if upload_success:
                    print(f"✓ Excel file uploaded to: {blob_path}")
                
                # 2. Create and upload DMO.Annexures data
                if not summary_df.empty:
                    annexures_df = self.create_annexures_data(
                        summary_df, 
                        metadata, 
                        sheet_name, 
                        len(df)
                    )
                
                annexures_df.to_csv('annexures.csv')
                    
                    # # Upload Annexures CSV to blob
                    # annexures_blob_path = "DMO/Annexures.csv"
                    # self.upload_csv_to_blob(annexures_df, annexures_blob_path)
                    # print(f"✓ Annexures data uploaded to blob")
                
                # 3. Create and upload DMO.DQRules data
                # if rules:
                #     dqrules_df = self.create_dqrules_data(rules, metadata, sheet_name)
                    
                #     # Upload DQRules CSV to blob
                #     dqrules_blob_path = "DMO/DQRules.csv"
                #     self.upload_csv_to_blob(dqrules_df, dqrules_blob_path)
                #     print(f"✓ DQRules data uploaded to blob")
                
                # # 4. Create consolidated summary report for this sheet
                # sheet_summary = {
                #     'Sheet': sheet_name.upper(),
                #     'Domain': metadata['domain'],
                #     'System': metadata['system'],
                #     'MaterialType': metadata.get('material_type', 'N/A'),
                #     'TotalRecords': len(df),
                #     'TotalIssues': len(issueList),
                #     'ProcessedDate': metadata['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                #     'ExcelFile': blob_path,
                #     'AnnexuresCount': len(summary_df) if not summary_df.empty else 0,
                #     'RulesApplied': len(rules) if rules else 0
                # }
                
        #         # Upload sheet summary
        #         summary_df_detailed = pd.DataFrame([sheet_summary])
        #         summary_blob_path = f"DMO/ProcessingSummary/{metadata['domain']}/{sheet_name.upper()}_summary.csv"
        #         self.upload_csv_to_blob(summary_df_detailed, summary_blob_path)
        #         print(f"✓ Processing summary uploaded to blob")
                
        #         return blob_path
                
            except Exception as e:
                print(f"✗ Error in blob storage operations: {e}")
                return None
        # else:
        #     print("⚠ Blob storage not configured")
        #     return None

def filter_issues(col, issues):
    """Legacy function for compatibility"""
    filtered = issues.split('; ')
    res = []
    for i in filtered:
        if col in i:
            res.append(i)
    return '; '.join(res)

def get_sheet_columns(sheet):
    """Get column definitions for each sheet"""
    columns_dict = {
        'lfa1': ['Supplier', 'Name 1', 'Name 2', 'Name 3', 'Name 4', 'Street', 'City', 'Country', 'PO Box', 
                 'P.O. Box Postal Code', 'Postal Code', 'Telephone 1', 'Telephone 2', 'Language Key', 'Address', 
                 'Plant', 'Tax Jurisdiction', 'Account Group', 'Tax Number 3', 'Created on', 'Created by',
                 'Block function', 'Payment block', 'Central del.block', 'Central posting block', 
                 'Central purchasing block', 'Title'],
        'j_1imovend': ['Supplier', 'Country', 'Permanent account number'],
        'lfb1': ['Supplier', 'Country', 'Company Code', 'Terms of Payment', 'Reconciliation acct', 
                 'Posting block for company code', 'Deletion Flag for Company Code', 'Planning group', 
                 'Tolerance group', 'Payment methods', 'Created on', 'Created by', 'MSME Status'],
        'lfm1': ['Supplier', 'City', 'Country', 'Purch. block for purchasing organization', 'Purch. Organization', 
                 'Purchasing Group', 'Order currency', 'Confirmation Control', 'Incoterms', 'Incoterms (Part 2)', 
                 'MSME Status', 'MSME Number', 'MSME Issue Date', 'ABAC Status', 'ABAC Reason', 'GR-Based Inv. Verif.', 
                 'Service-Based Invoice Verification', 'Delete flag for purchasing organization', 'Terms of Payment'],
        'lfbk': ['Supplier', 'Account holder', 'Bank Country', 'Bank Key', 'Bank Account'],
        'adrc': ['Supplier', 'Address Number', 'Street', 'Street 2', 'Street 3', 'Street 4', 'Street 5', 
                 'Postal Code', 'PO Box Postal Code', 'PO Box', 'Country'],
        'v_adr6': ['Supplier', 'E-Mail Address'],
        'kna1': ['Customer', 'SalesforceID', 'Open Pipeline', 'All Time Customer', 'Open Project?', 'Open Sales Order?', 
                 'Open Invoices', 'Last Invoice Posting Date', 'Country', 'Name 1', 'Name 2', 'Telephone 1', 
                 'Telephone 2', 'City', 'Street', 'Address', 'Postal Code', 'PO Box', 'P.O. Box Postal Code', 
                 'Account group', 'Tax Number 3', 'Tax Number 1', 'VAT Registration No.', 'Industry', 'Title', 
                 'Created by', 'Created on', 'Attribute 2'],
        'knb1': ['Customer', 'Open Pipeline', 'All Time Customer', 'Open Project?', 'Open Sales Order?', 
                 'Open Invoices', 'Last Invoice Posting Date', 'Company Code', 'Created by', 'Created on', 
                 'Reconciliation acct', 'Terms of Payment'],
        'knkk': ['Customer', 'Open Pipeline', 'All Time Customer', 'Open Project?', 'Open Sales Order?', 
                 'Open Invoices', 'Last Invoice Posting Date', 'Credit limit', 'Created by', 'Created on'],
        'knvv': ['Customer', 'Open Pipeline', 'All Time Customer', 'Open Project?', 'Open Sales Order?', 
                 'Open Invoices', 'Last Invoice Posting Date', 'Created By', 'Created On', 'Cust.Acct.Assg.Group', 
                 'Order block for sales area', 'Sales Organization', 'Distribution Channel', 'Division', 
                 'Cust.pric.procedure','Incoterms', 'Incoterms (Part 2)', 'Shipping Conditions'],
        'knb5': ['Customer', 'Open Pipeline', 'All Time Customer', 'Open Project?', 'Open Sales Order?', 
                 'Open Invoices', 'Last Invoice Posting Date', 'Dunning Procedure', 'Company Code'],
        'adr6': ['Customer', 'Open Pipeline', 'All Time Customer', 'Open Project?', 'Open Sales Order?', 
                 'Open Invoices', 'Last Invoice Posting Date', 'E-Mail Address'],
        'account': ['SAP_Account_Number__c', 'Open Pipeline', 'All Time Customer', 'Open Project?', 
                    'Open Sales Order?', 'Open Invoices', 'Last Invoice Posting Date', 'VAT_Number__c', 'Phone', 
                    'GST_Number__c', 'PAN_Number__c', 'BillingStreet', 'BillingAddress.street', 'BillingStateCode', 
                    'BillingPostalCode', 'Name', 'Industry_Sector__c', 'Industry', 'BillingCountryCode', 
                    'BillingAddress.countryCode', 'BillingCity', 'KTOKD__c', 'Customer_Type__c', 
                    'SAP_Customer_Creation_Date__c', 'CreatedDate', 'CreatedById','ZTERM__c', 'AKONT__c', 
                    'MAHNA__c', 'Total_Credit_Limit__c', 'Credit_Limit__c', 'VSBED__c', 'Sales_Organization__c',
                    'INCO1__c', 'INCO2__c', 'SPART__c', 'VTWEG__c', 'KALKS__c', 'KTGRD__c', 'CurrencyIsoCode', 
                    'Account_Currency__c','Company_Size__c', 'Business_Unit__c', 'Portfolio__c', 'Customer_Category__c'],
        'contact': ['AccountId', 'SAP_Account_Number__c', 'Email', 'Open Pipeline', 'All Time Customer', 
                    'Open Project?', 'Open Sales Order?', 'Open Invoices', 'Last Invoice Posting Date'],
        'mara': ['Material', 'Plant list', 'Material Type', 'Material Description', 'Material description', 
                 'Base Unit of Measure', 'Gen. item cat. grp', 'Material Group', 'Material Category',
                 'Industry', 'Int. material number', 'X-plant matl status', 'Division', 'catalog', 
                 'Transportation Group', 'Batch management', 'Mfr Part Profile',
                 'Purchasing value key', 'QM proc. active', 'Created On', 'Created By'],
        'marc': ['Material', 'Plant list', 'Plant', 'Control code', 'Zone Category', 'Storage condition', 'QM Control Key', 
                 'Loading Group', 'Profit Center', 'MRP Controller', 'MRP Type', 'Purchasing Group', 
                 'Prod. stor. location', 'Batch management', 'ABC Indicator', 'Procurement type', 
                 'Availability check', 'CAS number (pharm.)', 'Prodn Supervisor', 'Prod.Sched.Profile', 
                 'Certificate type', 'Acct Assignment Cat.'],
        'mbew': ['Material', 'Plant list', 'Valuation Category', 'Valuation Class', 'Price Control', 'Valuation Area', 
                 'Valuation Type'],
        'mvke': ['Material', 'Plant list', 'Item category group', 'Acct Assmt Grp Mat.'],
        'mlan': ['Material', 'Plant list', 'Tax ind. f. material']
    }
    
    return columns_dict.get(sheet, [])

def main():
    parser = argparse.ArgumentParser(
        description="Apply data quality rules on consolidated master data with blob storage upload"
    )

    parser.add_argument("--data", "-d", required=True, help="Path to excel data")
    parser.add_argument("--isVendor", "-v", help="Check if the input file is Vendor Master", default=False)
    parser.add_argument("--isCustomer", "-c", help="Check if the input file is Customer Master", default=False)
    parser.add_argument("--isMaterial", "-m", help="Check if the input file is Material Master", default=False)
    parser.add_argument("--materialType", "-mt", help="Material type", default="")
    parser.add_argument("--tables", "-t", help="Tables to apply rules", default="")
    parser.add_argument("--rules", "-r", required=True, help="Path to folder containing rulebooks")

    args = parser.parse_args()
    
    # Initialize processor and load config
    processor = DataQualityProcessor()
    if not processor.load_storage_config():
        print("❌ Failed to load storage configuration. Cannot proceed without blob storage.")
        return
    
    sheets = []

    start = time.time()
    print('\n[READING INPUT FILES]...')

    # Determine domain and system based on data type
    if args.isVendor:
        sheets = ['lfa1', 'lfb1', 'lfm1', 'lfbk', 'adrc', 'v_adr6', 'j_1imovend']
        domain = "Vendor"
        system = "SAP"
    elif args.isCustomer:
        sheets = ['kna1', 'knb1', 'knvv', 'knkk', 'knb5', 'adr6', 'account', 'contact']
        domain = "Customer"
        system = "SAP"
    elif args.isMaterial:
        # args.data = preprocessMaterialData(args.data)
        sheets = ['mara', 'marc', 'mbew', 'mvke', 'mlan']
        domain = "Material"
        system = "SAP"
        if args.materialType == "":
            raise ValueError("Please specify Material type")
        print(f"[MATERIAL TYPE - {str(args.materialType).upper()}]")
    else:
        raise Exception("Please specify master data")

    if args.tables != '':
        sheets = args.tables.lower().split(',')
        
    suffix = str(datetime.date.today()).replace("-","") + str(datetime.datetime.now().time()).replace(":","").replace(".","_")
    
    # Store metadata for SQL table mapping
    processing_metadata = {
        'domain': domain,
        'system': system,
        'material_type': args.materialType if args.isMaterial else None,
        'timestamp': datetime.datetime.now()
    }
    
    uploaded_files = []
    
    for sheet in sheets:
        print(f'\n[WORKING ON {sheet.upper()}]...')
        
        # Get columns for the sheet
        columns = get_sheet_columns(sheet)
        
        df = load_excel_data(args.data, sheet.upper(), columns)
        
        print(f'\n[APPLYING DATA QUALITY RULES - {sheet.upper()}]...')
        
        if args.isMaterial:
            rules_dir = os.path.join(args.rules, f'{args.materialType}_{sheet.lower()}_rulebook.json')
        else:
            rules_dir = os.path.join(args.rules, f'{sheet.lower()}_rulebook.json')
            
        rules = load_rules(rules_dir)
        results = apply_rules(df, rules)
        print('\n[DONE]')
        
        # Generate filename
        if args.isMaterial:
            filename = f'{suffix}_{args.materialType}_{sheet.lower()}.xlsx'
        else:
            filename = f'{suffix}_{sheet.lower()}.xlsx'
            
        print('\n[PROCESSING AND UPLOADING TO BLOB STORAGE]...')
        
        # Process and upload directly to blob storage
        blob_path = processor.preprocess_output(
            results, 
            filename, 
            processing_metadata, 
            sheet,
            rules
        )
        
        if blob_path:
            uploaded_files.append({
                'sheet': sheet.upper(),
                'blob_path': blob_path,
                'records': len(results)
            })
            print(f"✓ {sheet.upper()} processed and uploaded successfully")
        else:
            print(f"✗ Failed to upload {sheet.upper()}")
    
    # Create final consolidated report
    if uploaded_files:
        print('\n[CREATING CONSOLIDATED UPLOAD REPORT]...')
        consolidate_data = []
        total_records = 0
        
        for file_info in uploaded_files:
            total_records += file_info['records']
            consolidate_data.append({
                'Sheet': file_info['sheet'],
                'BlobPath': file_info['blob_path'],
                'Records': file_info['records'],
                'Domain': domain,
                'System': system,
                'MaterialType': args.materialType if args.isMaterial else 'N/A',
                'ProcessedDate': processing_metadata['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
            })
        
        # Add summary row
        consolidate_data.append({
            'Sheet': 'TOTAL_SUMMARY',
            'BlobPath': 'ALL_FILES',
            'Records': total_records,
            'Domain': domain,
            'System': system,
            'MaterialType': args.materialType if args.isMaterial else 'N/A',
            'ProcessedDate': processing_metadata['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
        })
        
        consolidated_df = pd.DataFrame(consolidate_data)
        consolidated_blob_path = f"DMO/ConsolidatedReports/{domain}_{suffix}_upload_report.csv"
        
        processor.upload_csv_to_blob(consolidated_df, consolidated_blob_path)
        print(f"✓ Consolidated upload report created: {consolidated_blob_path}")
    
    end = time.time()
    mins = (end-start)//60
    sec = abs((end-start) - mins*60)

    print(f'\n[TIME TAKEN - {mins:.0f} MINS {sec:.0f} SECONDS]')
    print(f'\n[TOTAL FILES UPLOADED - {len(uploaded_files)}]')
    print('\n[BLOB STORAGE UPLOAD COMPLETED]')

if __name__ == "__main__":
    main()