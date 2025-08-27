from pyrfc import Connection
import pandas as pd
import time

# -------------------- SAP Connection --------------------
conn = Connection(
    user='hammad',
    passwd='Uniqus@12345678',
    ashost='riseeccapp4',   # SAP Application Server
    sysnr='04',             # System number
    client='300',
    lang='EN'
)

start = time.time()

# -------------------- Tables & Columns --------------------
tables = {
    "KNA1": ['KUNNR','NAME1','NAME2','ORT01','STRAS','LAND1','REGIO','ADRNR',
             'TELF1','TELF2','SPRAS','KTOKD','STCD1','STCD2','LOEVM','ERNAM',
             'ERDAT'],
    
    "KNB1": ['KUNNR','BUKRS','AKONT','ZTERM','ZUAWA','FDGRV','VLIBB','VLIBB',
             'SPERR','LOEVM','ERNAM','ERDAT'],
    
    "KNVV": ['KUNNR','VKORG','VTWEG','SPART','KDGRP','BZIRK','WAERS','VKBUR',
             'VKGRP','KALKS','KDGRP','LIFNR','KURST','LOEVM','ERNAM','ERDAT'],
    
    "KNBK": ['KUNNR','BANKS','BANKL','BANKN','KOINH'],
    
    "ADRC": ['ADDRNUMBER','STREET','STR_SUPPL1','STR_SUPPL2','STR_SUPPL3',
             'LOCATION','POST_CODE1','POST_CODE2','PO_BOX','COUNTRY'],
    
    "ADR6": ['ADDRNUMBER','SMTP_ADDR'],
    
    "KNA1_STCD": ['KUNNR','STCDT','STCD1','STCD2']   # Sometimes customer PAN/VAT is stored here
}

# -------------------- Fetch Function --------------------
def fetch_table(table, fields, options=[], row_count=300000):
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
        
        if len(data) < row_count:
            break
        offset += row_count

    df = pd.DataFrame(rows, columns=fields)
    return df


# -------------------- Step 1: Fetch KNB1 --------------------
print("Fetching KNB1...")
knb1_df = fetch_table("KNB1", tables["KNB1"],
                      options=["BUKRS = '5100' OR BUKRS = '5500'"])
customer_list = knb1_df['KUNNR'].unique().tolist()


# -------------------- Step 2: Fetch Other Tables --------------------
print("Fetching KNA1...")
kna1_df = pd.DataFrame()
for cust in customer_list:
    opts = [f"KUNNR = '{cust}'"]
    df_part = fetch_table("KNA1", tables["KNA1"], options=opts)
    kna1_df = pd.concat([kna1_df, df_part], ignore_index=True)


print("Fetching KNVV...")
knvv_df = pd.DataFrame()
for cust in customer_list:
    opts = [f"KUNNR = '{cust}'"]
    df_part = fetch_table("KNVV", tables["KNVV"], options=opts)
    knvv_df = pd.concat([knvv_df, df_part], ignore_index=True)


print("Fetching KNBK...")
knbk_df = pd.DataFrame()
for cust in customer_list:
    opts = [f"KUNNR = '{cust}'"]
    df_part = fetch_table("KNBK", tables["KNBK"], options=opts)
    knbk_df = pd.concat([knbk_df, df_part], ignore_index=True)


print("Fetching ADRC...")
adrc_df = pd.DataFrame()
if not kna1_df.empty and 'ADRNR' in kna1_df.columns:
    addr_list = kna1_df['ADRNR'].dropna().unique().tolist()
    for addr in addr_list:
        opts = [f"ADDRNUMBER = '{addr}'"]
        df_part = fetch_table("ADRC", tables["ADRC"], options=opts)
        adrc_df = pd.concat([adrc_df, df_part], ignore_index=True)


print("Fetching ADR6...")
adr6_df = pd.DataFrame()
if not kna1_df.empty and 'ADRNR' in kna1_df.columns:
    addr_list = kna1_df['ADRNR'].dropna().unique().tolist()
    for addr in addr_list:
        opts = [f"ADDRNUMBER = '{addr}'"]
        df_part = fetch_table("ADR6", tables["ADR6"], options=opts)
        adr6_df = pd.concat([adr6_df, df_part], ignore_index=True)


print("Fetching KNA1_STCD...")
kna1stcd_df = pd.DataFrame()
for cust in customer_list:
    opts = [f"KUNNR = '{cust}'"]
    df_part = fetch_table("KNA1_STCD", tables["KNA1_STCD"], options=opts)
    kna1stcd_df = pd.concat([kna1stcd_df, df_part], ignore_index=True)


# -------------------- Save Results --------------------
tbs = [knb1_df, kna1_df, knvv_df, knbk_df, adrc_df, adr6_df, kna1stcd_df]
sheets = ['KNB1', 'KNA1', 'KNVV', 'KNBK', 'ADRC', 'ADR6', 'KNA1_STCD']

out = 'Data/Customer/customer_master.xlsx'
with pd.ExcelWriter(out, engine='openpyxl') as writer:
    for idx, table in enumerate(tbs):
        table.to_excel(writer, sheet_name=sheets[idx], index=False)

print("All customer tables downloaded successfully.")

end = time.time()
mins = (end-start)//60
sec = abs((end-start) - mins*60)
print(f'\n[TIME TAKEN - {mins:.0f} MINS {sec:.0f} SECONDS]')
