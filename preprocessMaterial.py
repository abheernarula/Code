import os
import pandas as pd
from tqdm import tqdm
tqdm.pandas()

map_mara = {
    "MATNR": "Material",
    # "WERKS": "Plants",  # ⚠️ Not in MARA; this is from MARC
    "MTART": "Material Type",
    "MAKTX": "Material Description",      # ⚠️ Technically from MAKT
    "MAKTG": "Material description",      # ⚠️ SAP does not have both – likely duplicate or typo
    "MEINS": "Base Unit of Measure",
    "MTPOS_MARA": "Gen. item cat. grp",  # ⚠️ Could be MVGR1 in some custom systems
    "MATKL": "Material Group",
    "ATTYP": "Material Category",      # ⚠️ Likely custom, not standard MARA
    "MBRSH": "Industry",
    "BISMT": "Int. material number",
    "MSTAE": "X-plant matl status",
    "SPART": "Division",
    "RBNRM": "catalog",                   # ⚠️ WRKST is "Basic material description", catalog could be Z-field
    "TRAGR": "Transportation Group",
    "XCHPF": "Batch management",
    "MPROF": "Mfr Part Profile",          # ⚠️ MFRPN is Manufacturer Part Number; MFRNR is Manufacturer
    "EKWSL": "Purchasing value key",
    "QMPUR": "QM proc. active",
    "ERSDA": "Created On",
    "ERNAM": "Created By",
    "LVORM": "DF at client level"
}

map_marc = {
    "MATNR": "Material",
    # "WERKS": "Plants",                        # or "Plant"
    "WERKS": "Plant",                         # both map to same field
    "STEUC": "Control code",                  # ⚠️ Also known as "Commodity Code"
    "ZZONE": "Zone Category",                 # ⚠️ May be custom/localization-specific
    "ZSTCOND": "Storage condition",
    "SSQSS": "QM Control Key",                # or possibly QMAT table — verify
    "LADGR": "Loading Group",
    "PRCTR": "Profit Center",
    "DISPO": "MRP Controller",
    "DISMM": "MRP Type",
    "EKGRP": "Purchasing Group",
    "LGPRO": "Prod. stor. location",
    "XCHPF": "Batch management",
    "MAABC": "ABC Indicator",                 # ⚠️ Often custom (standard field is "ABCSCHL")
    "BESKZ": "Procurement type",
    "MTVFP": "Availability check",
    "CASNR": "CAS number (pharm.)",           # ⚠️ Not standard MARC – likely custom or from EH&S
    "FEVOR": "Prodn Supervisor",
    "SFEPR": "Prod.Sched.Profile",
    "QZGTP": "Certificate type",              # ⚠️ Likely custom Z-field
    "ZZACCASSCAT": "Acct Assignment Cat.",           # or sometimes "KZKUP"
    "LVORM": "DF at plant level"
}

map_mbew = {
    "MATNR": "Material",
    # "BWKEY": "Plants",              # Also known as "Valuation Area"
    "BKLAS": "Valuation Class",
    "VPRSV": "Price Control",
    "BWKEY": "Valuation Area",      # same as Plants (duplicate mapping to BWKEY)
    "BWTAR": "Valuation Type",
    "BWTTY": "Valuation Category"   # ⚠️ Not quite — standard SAP does **not** have a separate "Valuation Category" field in MBEW. Likely custom.
}

map_mlan = {
    "MATNR": "Material",
    # "ALAND": "Plants",                     # ⚠️ Actually: "Country" – may be misused as Plant in your context
    "TAXIM": "Tax ind. f. material"
}

map_mvke = {
    "MATNR": "Material",
    # "VKORG": "Plants",                    # ⚠️ Actually: "Sales Organization", not Plant!
    "MTPOS": "Item category group",       # or sometimes "TRAGR" for loading group — check context
    "KTGRM": "Acct Assmt Grp Mat."
}

# map_potext = {
#     "MATNR": "Material",
#     "ZPPPOTEXT": "Purchase Order Text"
# }

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
        val = row['Material']
        if val in visited:
            pass
        else:
            inactiveList.append(val)
            visited.add(val)

def classifyInactive(table, row, inactive: list):
    return row['Material'] in inactive


def preprocessMaterialData(vendorMaster):
    
    mara = pd.read_excel(vendorMaster, sheet_name='MARA').rename(columns=map_mara)
    marc = pd.read_excel(vendorMaster, sheet_name='MARC').rename(columns=map_marc)
    mbew = pd.read_excel(vendorMaster, sheet_name='MBEW').rename(columns=map_mbew)
    mlan = pd.read_excel(vendorMaster, sheet_name='MLAN').rename(columns=map_mlan)
    mvke = pd.read_excel(vendorMaster, sheet_name='MVKE').rename(columns=map_mvke)
    potext = pd.read_excel(vendorMaster, sheet_name='POTEXT')#.rename(columns=map_potext)
    
    inactiveVendors = []
    visited = set()
    mara.progress_apply(lambda row: checkInactive(mara, row, inactiveVendors, visited,
                                                'DF at client level'), axis=1)
    
    marc.progress_apply(lambda row: checkInactive(marc, row, inactiveVendors, visited,
                                                'DF at plant level'), axis=1)
    
    mara['Inactive'] = mara.progress_apply(lambda row: classifyInactive(mara, row, inactiveVendors), axis=1)
    marc['Inactive'] = marc.progress_apply(lambda row: classifyInactive(marc, row, inactiveVendors), axis=1)
    mbew['Inactive'] = mbew.progress_apply(lambda row: classifyInactive(mbew, row, inactiveVendors), axis=1)
    mlan['Inactive'] = mlan.progress_apply(lambda row: classifyInactive(mlan, row, inactiveVendors), axis=1)
    mvke['Inactive'] = mvke.progress_apply(lambda row: classifyInactive(mvke, row, inactiveVendors), axis=1)
    # potext['Inactive'] = potext.progress_apply(lambda row: classifyInactive(potext, row, inactiveVendors), axis=1)
    
    mara_active = mara[mara['Inactive']==False]
    marc_active = marc[marc['Inactive']==False]
    mbew_active = mbew[mbew['Inactive']==False]
    mlan_active = mlan[mlan['Inactive']==False]
    mvke_active = mvke[mvke['Inactive']==False]
    # potext_active = potext[potext['Inactive']==False]
    
    output_dir = "/".join(vendorMaster.split('/')[:-1])
    output_path = os.path.join(output_dir, 'materialMaster.xlsx')
    tables = [mara_active, marc_active, mbew_active, mlan_active, mvke_active]#, potext_active]
    sheets = ['MARA', 'MARC', 'MBEW', 'MLAN', 'MVKE']#, 'POTEXT']
    
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        for idx, table in enumerate(tables):
            table.to_excel(writer, sheet_name=sheets[idx], index=False)
            
    return output_path