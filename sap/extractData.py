from pyrfc import Connection
import pandas as pd
import time
import gc

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


# --------------------------------ERSA-------------------------------------------
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
def fetch_table(table, fields, options=[], row_count=50000, offset=0):
    df = pd.DataFrame()
    rows = []
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
        part_df = pd.DataFrame(rows, columns=fields)
        rows = []
        df = pd.concat([df, part_df], ignore_index=True)
        print(len(df))
        print(offset)
        # print(len(rows))
        # rows.extend(data)
        if len(data) < row_count:
            break
        offset += row_count
        if offset==1000000:
            return df
        # print(offset)
    # df = pd.DataFrame([row['WA'].split('|') for row in rows], columns=fields)
    # df = pd.DataFrame(rows, columns=fields)
    # print(len(df))
    return df


# Step 1: Get MARA for material type ERSA

# mara_df = pd.merge(mara_df, makt_df, on='MATNR', how='left')
# mara_df.to_csv("Data/Material/ersa/MARA.csv", index=False)

# print(f"Fetching MARA...")
# mara_df = fetch_table("MARA", tables["MARA"], options=["MTART = 'ERSA'"])
# mats = mara_df['MATNR'].unique().tolist()

# print(f"Fetching MAKT...")
# makt_df = fetch_table("MAKT", tables["MAKT"])
# mara_df = pd.merge(mara_df, makt_df, on='MATNR', how='left')

# mara_df.to_csv('ERSA_MARA.csv')

# del makt_df, mara_df
# gc.collect()

# Step 2: Get MARC with plant like '5%'
print(f"Fetching MARC...")
opts = ["WERKS LIKE '5%'"]
# marc_df = fetch_table("MARC", tables["MARC"], options=opts)
# marc_df_1 = marc = marc_df[marc_df['MATNR'].isin(mats)]
# print('1 - ', len(marc_df_1))
# marc_df.to_csv('ERSA_MARC_1.csv')

# del marc_df, marc_df_1
# gc.collect()
df = pd.read_csv('ERSA_MARA.csv')
mats = df['MATNR'].unique().tolist()
df = fetch_table("MARC", tables["MARC"], options=opts, offset=1000000)
marc_df_1 = marc = df[df['MATNR'].isin(mats)]
marc_df_1.to_csv('MARC_2')
print("2 - ", len(marc_df_1))
# marc_df_2 = marc = marc_df[marc_df['MATNR'].isin(mats)]
# marc_df_1 = pd.concat([marc_df_1, marc_df_2], ignore_index=True)

# del marc_df
# gc.collect()

print(marc_df_1.head(2))
print(len(marc_df_1))
# print(marc_df_2.head(2))


    
# plants = marc_df.groupby('MATNR')['WERKS'].apply(lambda x: ', '.join(x)).reset_index()[['MATNR', 'WERKS']]
# plants.rename(columns={'WERKS':"Plant list"}, inplace=True)
# print(plants)
# Step 3: Filter MARA with materials from MARC
# filtered_materials = marc_df['MATNR'].unique().tolist()
# mara_filtered = mara_df[mara_df['MATNR'].isin(filtered_materials)]



print(f"Fetching MBEW...")
opts = ["BWKEY LIKE '5%'"]
mbew_df_1 = fetch_table("MBEW", tables["MBEW"], options=opts)
mbew_df_2 = fetch_table("MBEW", tables["MBEW"], options=opts, offset=1000000)

print(f"Fetching MLAN...")
mlan_df = fetch_table("MLAN", tables["MLAN"], options=opts)

print(f"Fetching MVKE...")
mvke_df = fetch_table("MVKE", tables["MVKE"], options=opts)

# Step 4: Fetch other tables
# mbew_df = batch_fetch("MBEW", tables["MBEW"], filtered_materials)
# mlan_df = batch_fetch("MLAN", tables["MLAN"], filtered_materials)
# mvke_df = batch_fetch("MVKE", tables["MVKE"], filtered_materials)
# zmm60_df = batch_fetch("ZMM60", tables["ZMM60"], filtered_materials)

# Step 5: Save all to CSV
# mara_filtered.to_csv("MARA_filtered.csv", index=False)
mara_df = pd.merge(mara_df, makt_df, on='MATNR', how='left')
mara_df = pd.merge(mara_df, plants, on='MATNR', how='left')
marc_df = pd.merge(marc_df, plants, on='MATNR', how='left')
mbew_df = pd.merge(mbew_df, plants, on='MATNR', how='left')
mlan_df = pd.merge(mlan_df, plants, on='MATNR', how='left')
mvke_df = pd.merge(mvke_df, plants, on='MATNR', how='left')

mats = mara_df['MATNR'].unique().tolist()
marc = marc_df[marc_df['MATNR'].isin(mats)]
filter_mats = marc_df['MATNR'].unique().tolist()

mara = mara_df[mara_df['MATNR'].isin(filter_mats)]
mbew = mbew_df[mbew_df['MATNR'].isin(filter_mats)]
mlan = mlan_df[mlan_df['MATNR'].isin(filter_mats)]
mvke = mvke_df[mvke_df['MATNR'].isin(filter_mats)]

tbs = [mara, marc, mbew, mlan, mvke]
sheets = ['MARA', 'MARC', 'MBEW', 'MLAN', 'MVKE']

out = 'Data/Material/ersa/ERSA.xlsx'
with pd.ExcelWriter(out, engine='openpyxl') as writer:
    for idx, table in enumerate(tbs):
        table.to_excel(writer, sheet_name=sheets[idx], index=False)

# marc_df.to_csv("Data/Material/ersa/MARC.csv", index=False)
# mbew_df.to_csv("Data/Material/ersa/MBEW.csv", index=False)
# mlan_df.to_csv("Data/Material/ersa/MLAN.csv", index=False)
# mvke_df.to_csv("Data/Material/ersa/MVKE.csv", index=False)

end = time.time()
mins = (end-start)//60
sec = abs((end-start) - mins*60)

print(f'\n[TIME TAKEN - {mins:.0f} MINS {sec:.0f} SECONDS]')
print("✅ All tables downloaded successfully.")