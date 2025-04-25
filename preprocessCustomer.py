import os
import pandas as pd
from tqdm import tqdm
tqdm.pandas()

def checkInactive(table, row, inactiveList : list, visited : set, *cols):
    pass

def classifyInactive(table, row, inactive: list):
    pass

def preprocessCustomerData(CustomerMaster):
    
    output_dir = ""
    output_path = os.path.join(output_dir, 'activeCustomerMaster.xlsx')
    tables = []
    sheets = []

    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        for idx, table in enumerate(tables):
            table.to_excel(writer, sheet_name=sheets[idx], index=False)
            
    return output_path