from pyrfc import Connection
import pandas as pd
import time

# conn = Connection(
#     user='rfc1',
#     passwd='Uniqus@1234',
#     ashost='riseeccdev',      # Sandbox
#     sysnr='10',
#     client='300',
#     lang='EN'
# )
start = time.time()

conn = Connection(
    user='hammad',
    passwd='Uniqus@12345678',
    ashost='riseeccapp4',     # Production
    sysnr='04',
    client='300',
    lang='EN'
)


# --------------------------------ersa-------------------------------------------
tables = {
    "MARA": ['MATNR', 'MTART', 'MEINS', 'MTPOS_MARA', 'MATKL', 'ATTYP', 'MBRSH', 
             'BISMT', 'MSTAE', 'SPART', 'RBNRM', 'TRAGR', 'XCHPF', 'MPROF', 'EKWSL', 'QMPUR', 'ERSDA', 
             'ERNAM', 'LVORM'],  # Material No, Type, Group, UoM
    
    "MAKT": ['MATNR', 'MAKTX', 'MAKTG'],
    
    "MARC": ['MATNR', 'WERKS', 'STEUC', 'ZZONE', 'ZSTCOND', 'SSQSS', 'LADGR', 'PRCTR', 'DISPO', 
             'DISMM', 'EKGRP', 'LGPRO', 'XCHPF', 'MAABC', 'BESKZ', 'MTVFP', 'CASNR', 'FEVOR', 
             'SFEPR', 'QZGTP', 'ZZACCASSCAT', 'LVORM'],  # Plant, MRP Controller, Storage loc
    
    "MBEW": ['MATNR', 'BKLAS', 'VPRSV', 'BWKEY', 'BWTAR', 'BWTTY'],  # Valuation
    "MLAN": ["MATNR", "TAXIM"],           # Tax info
    "MVKE": ["MATNR", "MTPOS", "KTGRM"],  # Sales org data
    "ZMM60": ["MATNR", "ZPPPOTEXT"]                   # Custom table with Z field
}

# 3. Function to fetch from RFC_READ_TABLE
def fetch_table(table, fields, options=[], row_count=300000):
    # print(f"Fetching {table}...")
    rows = []
    offset = 0
    while True:
        result = conn.call('RFC_READ_TABLE',
                           QUERY_TABLE=table,
                           DELIMITER='|',
                           FIELDS=[{'FIELDNAME': f} for f in fields],
                           OPTIONS=options,
                           ROWSKIPS=offset,
                           ROWCOUNT=row_count)
        data = result['DATA']
        
        for row in data:
            split_row = row['WA'].split('|')
            if len(split_row) == len(fields):
                rows.append(split_row)
            else:
                print(f"⚠️ Skipping row due to mismatch: {split_row}")
        
        # rows.extend(data)
        if len(data) < row_count:
            break
        offset += row_count
    # df = pd.DataFrame([row['WA'].split('|') for row in rows], columns=fields)
    df = pd.DataFrame(rows, columns=fields)
    return df

# def batch_fetch(table, fields, materials, batch_size=50):
#     print(f"Fetching {table} in batches...")
#     df_total = pd.DataFrame()
#     for i in range(0, len(materials), batch_size):
#         batch = materials[i:i + batch_size]
#         options = " OR ".join([f"MATNR = '{mat}'" for mat in batch])
#         # print(options)
#         df_part = fetch_table(table, fields, options=[options])
#         df_total = pd.concat([df_total, df_part], ignore_index=True)
#     return df_total

# Step 1: Get MARA for material type ersa
print(f"Fetching MARA...")
mara_df = fetch_table("MARA", tables["MARA"], options=["MTART = 'ERSA'"])
material_list = mara_df['MATNR'].tolist()
mara_df.to_csv("MARA_unfiltered.csv", index=False)


# Step 2: Get MARC with plant like '5%'
print(f"Fetching MARC...")
marc_df = pd.DataFrame()
for mat in material_list:
    opts = [f"MATNR = '{mat}' AND WERKS LIKE '5%'"]
    df_part = fetch_table("MARC", tables["MARC"], options=opts)
    marc_df = pd.concat([marc_df, df_part], ignore_index=True)
    print(len(marc_df))
    
plants = marc_df.groupby('MATNR')['WERKS'].apply(lambda x: ', '.join(x)).reset_index()[['MATNR', 'WERKS']]
plants.rename(columns={'WERKS':"Plant list"}, inplace=True)
# print(plants)
# Step 3: Filter MARA with materials from MARC
filtered_materials = marc_df['MATNR'].unique().tolist()
mara_filtered = mara_df[mara_df['MATNR'].isin(filtered_materials)]

print(f"Fetching MAKT...")
makt_df = pd.DataFrame()
for mat in filtered_materials:
    opts = [f"MATNR = '{mat}'"]
    df_part = fetch_table("MAKT", tables["MAKT"], options=opts)
    makt_df = pd.concat([makt_df, df_part], ignore_index=True)
    print(len(makt_df))


print(f"Fetching MBEW...")
mbew_df = pd.DataFrame()
for mat in filtered_materials:
    opts = [f"MATNR = '{mat}' AND BWKEY LIKE '5%'"]
    df_part = fetch_table("MBEW", tables["MBEW"], options=opts)
    mbew_df = pd.concat([mbew_df, df_part], ignore_index=True)
    print(len(mbew_df))


print(f"Fetching MLAN...")
mlan_df = pd.DataFrame()
for mat in filtered_materials:
    opts = [f"MATNR = '{mat}'"]
    df_part = fetch_table("MLAN", tables["MLAN"], options=opts)
    mlan_df = pd.concat([mlan_df, df_part], ignore_index=True)
    print(len(mlan_df))

print(f"Fetching MVKE...")
mvke_df = pd.DataFrame()
for mat in filtered_materials:
    opts = [f"MATNR = '{mat}'"]
    df_part = fetch_table("MVKE", tables["MVKE"], options=opts)
    mvke_df = pd.concat([mvke_df, df_part], ignore_index=True)
    print(len(mvke_df))
    
# print(f"Fetching POTEXT...")
# po_df = pd.DataFrame()
# for mat in filtered_materials:
#     opts = [f"MATNR = '{mat}'"]
#     df_part = fetch_table("ZRMM_MATERIALS_LIST", tables["ZMM60"], options=opts)
#     po_df = pd.concat([po_df, df_part], ignore_index=True)

# Step 4: Fetch other tables
# mbew_df = batch_fetch("MBEW", tables["MBEW"], filtered_materials)
# mlan_df = batch_fetch("MLAN", tables["MLAN"], filtered_materials)
# mvke_df = batch_fetch("MVKE", tables["MVKE"], filtered_materials)
# zmm60_df = batch_fetch("ZMM60", tables["ZMM60"], filtered_materials)

# Step 5: Save all to CSV
# mara_filtered.to_csv("MARA_filtered.csv", index=False)
# marc_df.to_csv("MARC_filtered.csv", index=False)
# mara_filtered.to_csv("Data/Material/ersa/31july/MARA.csv", index=False)
# marc_df.to_csv("Data/Material/ersa/31july/MARC.csv", index=False)
# mbew_df.to_csv("Data/Material/ersa/31july/MBEW.csv", index=False)
# mlan_df.to_csv("Data/Material/ersa/31july/MLAN.csv", index=False)
# mvke_df.to_csv("Data/Material/ersa/31july/MVKE.csv", index=False)

mara_filtered = pd.merge(mara_filtered, makt_df, on='MATNR', how='left')
mara_filtered = pd.merge(mara_filtered, plants, on='MATNR', how='left')
marc_df = pd.merge(marc_df, plants, on='MATNR', how='left')
mbew_df = pd.merge(mbew_df, plants, on='MATNR', how='left')
mlan_df = pd.merge(mlan_df, plants, on='MATNR', how='left')
mvke_df = pd.merge(mvke_df, plants, on='MATNR', how='left')

end = time.time()
mins = (end-start)//60
sec = abs((end-start) - mins*60)

mara_filtered.to_csv('MARA.csv')
marc_df.to_csv('MARC.csv')
mbew_df.to_csv('MBEW.csv')
mlan_df.to_csv('MLAN.csv')
mvke_df.to_csv('MVKE.csv')

tbs = [mara_filtered, marc_df, mbew_df, mlan_df, mvke_df]
sheets = ['MARA', 'MARC', 'MBEW', 'MLAN', 'MVKE']

out = 'Data/Material/ersa/ersa.xlsx'
with pd.ExcelWriter(out, engine='openpyxl') as writer:
    for idx, table in enumerate(tbs):
        table.to_excel(writer, sheet_name=sheets[idx], index=False)

# zmm60_df.to_csv("ZMM60.csv", index=False)

print("✅ All tables downloaded successfully.")
end = time.time()
mins = (end-start)//60
sec = abs((end-start) - mins*60)

print(f'\n[TIME TAKEN - {mins:.0f} MINS {sec:.0f} SECONDS]')