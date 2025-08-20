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
        if len(data) < row_count:
            break
        offset += row_count
    return df

fields = ['BUKRS', 'BELNR', 'GJAHR', 'HKONT']

# Common filters
gjahr_filter = "GJAHR BETWEEN '2021' AND '2025'"
bukrs_filter = "BUKRS LIKE '5%'"


# Simulate 2800 HKONT values
hkonts = [f"{x:010d}" for x in range(1000000000, 1000002800)]  # replace with real values

batch_size = 50  # SAP limit is 72 chars per OPTIONS line

all_data = pd.DataFrame()

for i in range(0, len(hkonts), batch_size):
    batch = hkonts[i:i+batch_size]
    hkont_conditions = " OR ".join([f"HKONT = '{acc}'" for acc in batch])
    full_condition = f"({bukrs_filter}) AND ({gjahr_filter}) AND ({hkont_conditions})"
    
    print(f"Fetching batch {i//batch_size+1} of HKONTs...")
    try:
        df = fetch_table("BSEG", fields, options=[full_condition])
        all_data = pd.concat([all_data, df], ignore_index=True)
    except Exception as e:
        print(f"❌ Batch {i//batch_size+1} failed: {e}")
        continue

# Save
all_data.to_csv("BSEG_filtered.csv", index=False)
print("✅ BSEG export completed.")

end = time.time()
mins = (end-start)//60
sec = abs((end-start) - mins*60)

print(f'\n[TIME TAKEN - {mins:.0f} MINS {sec:.0f} SECONDS]')
print("✅ All tables downloaded successfully.")