import os
import json
import argparse
import pandas as pd
from tqdm import tqdm
tqdm.pandas()

def load_rules(path):
    with open(path, 'r') as rules:
        rules_json = json.load(rules)      
    return rules_json.get("rules", [])

def apply_rules(df, rules):
    return standardizeCol(df, rules)

def standardizeCol(df, rules):
    for rule in rules:
        
        col = rule.get('column')
        pattern = rule.get('pattern')
        # print(df_new.columns)
        
        if col in df.columns:
            
            if pattern == 'title':
                df[col] = df[col].str.title()
        
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