import os
import pandas as pd
from tqdm import tqdm
tqdm.pandas()

def checkInactive(table, row, inactiveList : list, visited : set, *cols):
    res = False
    for col in cols:
        if pd.isnull(row[col]) or str(row[col]).strip() == '' or str(row[col]).lower() == 'nan':
            pass
        else:
            res = True
            break
    # return not res
    if res:
        val = row['Supplier']
        if val in visited:
            pass
        else:
            inactiveList.append(val)
            visited.add(val)

def classifyInactive(table, row, inactive: list):
    return row['Supplier'] in inactive

def preprocessVendorData(vendorMaster):
    lfa1 = pd.read_excel(vendorMaster, sheet_name='LFA1')
    lfb1 = pd.read_excel(vendorMaster, sheet_name='LFB1')
    lfm1 = pd.read_excel(vendorMaster, sheet_name='LFM1')
    lfbk = pd.read_excel(vendorMaster, sheet_name='LFBK')
    adrc = pd.read_excel(vendorMaster, sheet_name='ADRC')
    
    adrc_required = adrc[['Address Number', 'Postal Code', 'Street', 'Street 2', 'Street 3', 'Street 4', 'Street 5', 
                          'Postal Code', 'PO Box Postal Code', 'PO Box']]
    right = lfa1[['Supplier', 'Address', 'Last PO Date', 'Last BFN Date', 'Invoice Open?', 
                  'Last Invoice Posting Date', 'Country']]
    adrc = pd.merge(adrc_required, right, how='left', left_on='Address Number', right_on='Address')
    
    
    inactiveVendors = []
    visited = set()
    lfb1.progress_apply(lambda row: checkInactive(lfb1, row, inactiveVendors, visited,
                                                'Posting block for company code', 
                                                'Deletion Flag for Company Code'), axis=1)
    
    lfm1.progress_apply(lambda row: checkInactive(lfm1, row, inactiveVendors, visited,
                                                'Purch. block for purchasing organization', 
                                                'Delete flag for purchasing organization'), axis=1)
    
    lfa1.progress_apply(lambda row: checkInactive(lfm1, row, inactiveVendors, visited,
                                                'Block function', 'Payment block', 'Central del.block',
                                                'Central posting block', 'Central purchasing block'), axis=1)
    lfa1['Inactive'] = lfa1.progress_apply(lambda row: classifyInactive(lfa1, row, inactiveVendors), axis=1)
    lfb1['Inactive'] = lfb1.progress_apply(lambda row: classifyInactive(lfb1, row, inactiveVendors), axis=1)
    lfm1['Inactive'] = lfm1.progress_apply(lambda row: classifyInactive(lfm1, row, inactiveVendors), axis=1)
    lfbk['Inactive'] = lfbk.progress_apply(lambda row: classifyInactive(lfbk, row, inactiveVendors), axis=1)
    adrc['Inactive'] = adrc.progress_apply(lambda row: classifyInactive(adrc, row, inactiveVendors), axis=1)
    
    # Comment [line 52 - 60] for Inctive Vendor output
    lfa1_active = lfa1[lfa1['Inactive']==False]
    lfb1_active = lfb1[lfb1['Inactive']==False]
    lfm1_active = lfm1[lfm1['Inactive']==False]
    lfbk_active = lfbk[lfbk['Inactive']==False]
    adrc_active = adrc[adrc['Inactive']==False]
    
    output_dir = "/".join(vendorMaster.split('/')[:-1])
    output_path = os.path.join(output_dir, 'activeVendorMaster.xlsx')
    tables = [lfa1_active, lfb1_active, lfm1_active, lfbk_active, adrc_active]
    sheets = ['LFA1', 'LFB1', 'LFM1', 'LFBK', 'ADRC']
    
    # Comment [line 64 - 72] for Active Vendor output
    # lfa1_inactive = lfa1[lfa1['Inactive']==True]
    # lfb1_inactive = lfb1[lfb1['Inactive']==True]
    # lfm1_inactive = lfm1[lfm1['Inactive']==True]
    # lfbk_inactive = lfbk[lfbk['Inactive']==True]
    # adrc_inactive = adrc[adrc['Inactive']==True]
    
    # output_dir = "/".join(vendorMaster.split('/')[:-1])
    # output_path = os.path.join(output_dir, 'inactiveVendorMaster.xlsx')
    # tables = [lfa1_inactive, lfb1_inactive, lfm1_inactive, lfbk_inactive, adrc_inactive]
    # sheets = ['LFA1', 'LFB1', 'LFM1', 'LFBK', 'ADRC']
    
    # with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
    #     for idx, table in enumerate(tables):
    #         table.to_excel(writer, sheet_name=sheets[idx], index=False)
            
    return output_path
    
    


# print(len(set(load_vendor_data('Vendor/LFA1_Syngene.xlsx')[0])))
# print()
# print(len(load_vendor_data('../Vendor/LFA1_Syngene.xlsx')[0]))
# print(len(load_vendor_data('../Vendor/LFA1_Syngene.xlsx')[1]))
# print(len(load_vendor_data('../Vendor/LFA1_Syngene.xlsx')[2]))
# print(len(load_vendor_data('../Vendor/LFA1_Syngene.xlsx')[3]))
 
# print(preprocessVendorData())