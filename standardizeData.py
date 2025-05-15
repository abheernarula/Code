import os
import re
import json
import argparse
import pandas as pd
import geonamescache
from tqdm import tqdm
from rapidfuzz import process, fuzz
tqdm.pandas()
gc = geonamescache.GeonamesCache()
all_cities = {c["name"] for c in gc.get_cities().values()}

def load_rules(path):
    with open(path, 'r') as rules:
        rules_json = json.load(rules)      
    return rules_json.get("rules", [])

def apply_rules(df, rules):
    return standardizeCol(df, rules)

def standardizeStreet(df, col):
    pattern = r"[^A-Za-z0-9\s\.,\-/']"
    df[col] = (
        df[col]
        .str.replace(pattern, '', regex=True)
        .str.replace(r'\s+', ' ', regex=True)
        .str.replace(r'^[^A-Za-z0-9]+|[^A-Za-z0-9]+$', '', regex=True)
        .str.strip()
    )
    return df[col]

def standardizeStreet(val, threshold=80):
    if pd.isna(val) or pd.isnull(val) or str(val).lower() == 'nan':
        return val
    
    res = val.strip().title()
    

def standardizeCol(df, rules):
    for rule in rules:
        
        col = rule.get('column')
        action = rule.get('action')
        # print(df_new.columns)
        
        if col in df.columns:
            
            if action == 'title':
                df[col] = df[col].astype(str).str.upper()
            
            elif action == 'standard-str':
                df[col] = standardizeStreet(df, col)
        
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
    sheets = ['5100', '5300', '5500']
elif args.isMaterial:
    rule_dir = os.path.join(args.rules, 'material.json')
    sheets = []
elif args.isCustomer:
    rule_dir = os.path.join(args.rules, 'customer.json')
    sheets = []
else:
    raise Exception("Please specify master data")

rules = load_rules(rule_dir)

for sheet in sheets:
    print(f'WORKING ON SHEET: {sheet}')
    df = pd.read_excel(args.data, sheet_name=sheet)
    results = apply_rules(df, rules)
    output_path = os.path.join(args.output, f'{sheet}_standardizedOutput.xlsx')

    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        results.to_excel(writer, sheet_name=sheet, index=False)