import os
import re
import json
import argparse
import pandas as pd
import geonamescache
from tqdm import tqdm
import phonenumbers
from phonenumbers import (
    NumberParseException,
    is_possible_number,
    number_type,
    PhoneNumberType
)
tqdm.pandas()
gc = geonamescache.GeonamesCache()
all_cities = {c["name"] for c in gc.get_cities().values()}
all_cities2 = pd.read_csv('city.csv')['City'].to_list()

def load_rules(path):
    with open(path, 'r') as rules:
        rules_json = json.load(rules)      
    return rules_json.get("rules", [])

def apply_rules(df, rules):
    return standardizeCol(df, rules)

# def standardizeStreet(df, col):
#     pattern = r"[^A-Za-z0-9\s\.,\-/']"
#     df[col] = (
#         df[col]
#         .str.replace(pattern, '', regex=True)
#         .str.replace(r'\s+', ' ', regex=True)
#         .str.replace(r'^[^A-Za-z0-9]+|[^A-Za-z0-9]+$', '', regex=True)
#         .str.strip()
#     )
#     return df[col]

def standardizeIndustryCust(value, country):
    if pd.isnull(value) or str(value).strip() == '' or value.lower() == 'nan':
        if country == 'IN': return 'DTA Customer'
        else: return 'Export Customer'
    else:
        return value
    
def standardizeAccAsgmtCust(value, country, sapId):
    if pd.isnull(value) or str(value).strip() == '' or value.lower() == 'nan':
        if str(sapId).startswith('7'): return '3'
        if country == 'IN': return '1'
        else: return "2"
    else: return value
    
def standardizeKTGRD(value, country, sapId):
    if pd.isnull(value) or str(value).strip() == '' or value.lower() == 'nan':
        if len(str(sapId)) == 4: return '30'
        if country == 'IN': return '10'
        else: return '20'
    else: return value

def standardizeKTOKD(value):
    if pd.isnull(value) or str(value).strip() == '' or value.lower() == 'nan':
        return 'Z001'
    else: return value
    
def standardizeSalesOrgCust(value):
    if pd.isnull(value) or str(value).strip() == '' or value.lower() == 'nan':
        return '5100'
    else: return value

    
def standardizeIncoCust(value, ref):
    if pd.isnull(value) or str(value).strip() == '' or value.lower() == 'nan':
        if ref == 1: return 'EXW'
        if ref == 2: return 'Ex Works'
    else: return value

    
def standardizeSPART(value, portfolio):
    if pd.isnull(value) or str(value).strip() == '' or value.lower() == 'nan':
        if str(portfolio).__contains__('Discovery'): return '52'
        elif str(portfolio).__contains__('Development'): return '51'
        elif str(portfolio).__contains__('Bioligics'): return '55'
        elif str(portfolio).__contains__('Clinical Development'): return '60'
        else: return '<TBF>'
    else: return value

def standardizeStreet(df, col):
    df2 = df.copy()
    pattern = r"[^A-Za-z0-9\s\.\-/',&#]"
    res = (
        df2[col]
        .str.replace('&', 'and')
        .str.replace(pattern, '', regex=True)
        .str.replace(r'\s+', ' ', regex=True)
        .str.replace(r'^[^A-Za-z0-9]+|[^A-Za-z0-9]+$', '', regex=True)
        .str.strip()
    )
    return res

def standardizeCity(val, threshold=80):
    val = val.strip().title()
    if val in all_cities or val in all_cities2:
        return val.upper()
    return ''

def standardizeIncoterms(row):
    
    coCode = int(row['Company Code'])
    inco1 = str(row['Incoterms (Part 1)']).strip()
    
    if coCode == 5100:
        if inco1 == 'DAP' or inco1 == 'CIF':
            return 'BENGALURU'
    
    if coCode == 5500:
        if inco1 == 'DAP' or inco1 == 'CIF':
            return 'HYDERABAD'
    
    if inco1 == 'EXW':
        return row['City']
    
    return row['Incoterms (Part 2)']

def standardizePhone(phone_str: str, default_region: str):
    if pd.isnull(phone_str) or pd.isna(phone_str) or phone_str.strip().lower()=='nan' or phone_str.strip()=='' or phone_str=='0':
        return ''
    if pd.isnull(default_region) or pd.isna(default_region) or default_region.strip().lower()=='nan' or default_region.strip()=='' or default_region=='0':
        return ''
    else:
        try:
            pn = phonenumbers.parse(phone_str, default_region)
            if is_possible_number(pn):
                t = number_type(pn)
                if t == PhoneNumberType.MOBILE:
                    std = f"+{pn.country_code} {pn.national_number}"
                    # tag = "Mobile"
                elif t in (
                    PhoneNumberType.FIXED_LINE,
                    PhoneNumberType.FIXED_LINE_OR_MOBILE,
                    PhoneNumberType.TOLL_FREE
                ):
                    # std = format_number(pn, PhoneNumberFormat.INTERNATIONAL)
                    std = f"+{pn.country_code} {pn.national_number}"
                    # tag = "Landline"
                else:
                    # std = format_number(pn, PhoneNumberFormat.INTERNATIONAL)
                    std = f"+{pn.country_code} {pn.national_number}"
                    # tag = "Other"

                std = std.replace('-', ' ')
                std = re.sub(r'\s+', ' ', std).strip()
                return std

        except NumberParseException:
            pass

        digits = re.sub(r"\D", "", phone_str).lstrip("0")
        default_cc = phonenumbers.country_code_for_region(default_region)
        std = f"+{default_cc} {digits}"
        return std

def standardizeCol(df, rules):
    for rule in rules:
        
        col = rule.get('column')
        action = rule.get('action')
        try:
            refcol = rule.get('ref')
        except:
            pass
        # print(df_new.columns)
        
        if col in df.columns:
            
            if action == 'upper':
                df[col] = df[col].astype(str).str.upper()
            
            elif action == 'validation-street':
                df[f'{col}_new'] = standardizeStreet(df, col)
            
            elif action == 'validate-city':
                df[f'{col}_new'] = df[col].progress_apply(standardizeCity)
                
            elif action == 'validate-phone':
                df[f'{col}_std'] = df.progress_apply(lambda row: standardizePhone(str(row[col]), str(row[refcol])), 
                                                     axis=1)
            
            elif action == 'validate-incoterms':
                df[col] = df.progress_apply(lambda row: standardizeIncoterms(row), axis=1)
            
            elif action == 'validate-industry-cust':
                df[f'{col}_std'] = df.progress_apply(lambda row: standardizeIndustryCust(str(row[col]), str(row[refcol])), 
                                                     axis=1)
            elif action == 'validate-acc-asgmt-cust':
                df[f'{col}_std'] = df.progress_apply(lambda row: standardizeAccAsgmtCust(str(row[col]), str(row[refcol]), str(row['SAP_Account_Number__c'])),
                                                     axis=1)
            
            elif action == 'validate-ktgrd-cust':
                df[f'{col}_std'] = df.progress_apply(lambda row: standardizeKTGRD(str(row[col]), str(row[refcol]), str(row['SAP_Account_Number__c'])),
                                                     axis=1)
            
            elif action == 'validate-ktokd-cust':
                df[f'{col}_std'] = df.progress_apply(lambda row: standardizeKTOKD(str(row[col])),
                                                     axis=1)
            
            elif action == 'validate-ktokd-cust':
                df[f'{col}_std'] = df.progress_apply(lambda row: standardizeSPART(str(row[col]), str(row[refcol])),
                                                     axis=1)

            elif action == 'validate-inco1-cust':
                df[f'{col}_std'] = df.progress_apply(lambda row: standardizeIncoCust(str(row[col]), 1),
                                                     axis=1)
            
            elif action == 'validate-inco2-cust':
                df[f'{col}_std'] = df.progress_apply(lambda row: standardizeIncoCust(str(row[col]), 2),
                                                     axis=1)
            
            elif action == 'validate-sales-org-cust':
                df[f'{col}_std'] = df.progress_apply(lambda row: standardizeSalesOrgCust(str(row[col])),
                                                     axis=1)
            
        else:
            raise Exception(f'"{col}" not found!')
        
    return df

parser = argparse.ArgumentParser(
    description="Standardize master data"
)

parser.add_argument("--data", "-d", required=True, help="Path to excel data")
parser.add_argument("--isVendor", "-v", help="Check if the input file is Vendor Master", default=False)
parser.add_argument("--isCustomer", "-c", help="Check if the input file is Vendor Master", default=False)
parser.add_argument("--isMaterial", "-m", help="Check if the input file is Material Master", default=False)
parser.add_argument("--rules", "-r", required=True, help="Path to folder containing rulebooks")
parser.add_argument("--output", '-o', required=True, default='', help='Path to outpput file')

args = parser.parse_args()

if args.isVendor:
    rule_dir = os.path.join(args.rules, 'vendor.json')
    sheets = ['5100', '5300', '5500', 'No org']
elif args.isMaterial:
    rule_dir = os.path.join(args.rules, 'material.json')
    sheets = []
elif args.isCustomer:
    rule_dir = os.path.join(args.rules, 'customer.json')
    sheets = ['ACCOUNT']
else:
    raise Exception("Please specify master data")

rules = load_rules(rule_dir)
if args.isVendor:
    countryCode = pd.read_excel('../Vendor/VendorMaster.xlsx', sheet_name='LFA1', dtype=str)[['Supplier', 'Country']]
    companyCode = pd.read_excel('../Vendor/VendorMaster.xlsx', sheet_name='LFB1', dtype=str)[['Supplier', 'Company Code']]

for sheet in sheets:
    print(f'WORKING ON SHEET: {sheet}')
    df = pd.read_excel(args.data, sheet_name=sheet, dtype=str, keep_default_na=False)
    if args.isVendor:
        df = pd.merge(df, countryCode, 'left', left_on='Account Number of Supplier', right_on='Supplier')
        df = pd.merge(df, companyCode, 'left', left_on='Account Number of Supplier', right_on='Supplier')
    results = apply_rules(df, rules)
    output_path = os.path.join(args.output, f'{sheet}_standardizedOutput.xlsx')

    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        results.astype(str).to_excel(writer, sheet_name=sheet, index=False)