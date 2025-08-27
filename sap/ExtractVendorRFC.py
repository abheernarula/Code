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
    "LFB1": ['LIFNR','BUKRS','ZTERM','AKONT','SPERR','LOEVM','FDGRV','TOGRU',
             'ZWELS','ERDAT','ERNAM'],
    
    "LFA1": ['LIFNR','NAME1','NAME2','NAME3','NAME4','STRAS','ORT01','LAND1',
             'PFACH','PSTL2','PSTLZ','TELF1','TELF2','SPRAS','ADRNR','WERKS',
             'TXJCD','KTOKK','STCD3','ERDAT','ERNAM','SPERQ','SPERZ','NODEL',
             'SPERR','SPERM'],
    
    "LFM1": ['LIFNR','SPERM','EKORG','EKGRP','ZTERM','WAERS','BSTAE','INCO1',
             'INCO2','ZZMSME_STAT','ZZMSME_NUM','ZZMSME_DAT','ZZABAC_ST',
             'ZZREASON','WEBRE','LEBRE','LOEVM'],
    
    "LFBK": ['LIFNR','KOINH','BANKS','BANKL','BANKN'],
    
    "ADRC": ['ADDRNUMBER','STREET','STR_SUPPL1','STR_SUPPL2','STR_SUPPL3',
             'LOCATION','POST_CODE1','POST_CODE2','PO_BOX','COUNTRY'],
    
    "ADR6": ['ADDRNUMBER','SMTP_ADDR'],
    
    "J_1IMOVEND": ['LIFNR','J_1IPANNO']
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


# -------------------- Step 1: Fetch LFB1 --------------------
print("Fetching LFB1...")
lfb1_df = fetch_table("LFB1", tables["LFB1"],
                      options=["BUKRS = '5100' OR BUKRS = '5500'"])
vendor_list = lfb1_df['LIFNR'].unique().tolist()


# -------------------- Step 2: Fetch Other Tables --------------------
print("Fetching LFA1...")
lfa1_df = pd.DataFrame()
for ven in vendor_list:
    opts = [f"LIFNR = '{ven}'"]
    df_part = fetch_table("LFA1", tables["LFA1"], options=opts)
    lfa1_df = pd.concat([lfa1_df, df_part], ignore_index=True)


print("Fetching LFM1...")
lfm1_df = pd.DataFrame()
for ven in vendor_list:
    opts = [f"LIFNR = '{ven}'"]
    df_part = fetch_table("LFM1", tables["LFM1"], options=opts)
    lfm1_df = pd.concat([lfm1_df, df_part], ignore_index=True)


print("Fetching LFBK...")
lfbk_df = pd.DataFrame()
for ven in vendor_list:
    opts = [f"LIFNR = '{ven}'"]
    df_part = fetch_table("LFBK", tables["LFBK"], options=opts)
    lfbk_df = pd.concat([lfbk_df, df_part], ignore_index=True)


print("Fetching ADRC...")
adrc_df = pd.DataFrame()
if not lfa1_df.empty and 'ADRNR' in lfa1_df.columns:
    addr_list = lfa1_df['ADRNR'].dropna().unique().tolist()
    for addr in addr_list:
        opts = [f"ADDRNUMBER = '{addr}'"]
        df_part = fetch_table("ADRC", tables["ADRC"], options=opts)
        adrc_df = pd.concat([adrc_df, df_part], ignore_index=True)


print("Fetching ADR6...")
adr6_df = pd.DataFrame()
if not lfa1_df.empty and 'ADRNR' in lfa1_df.columns:
    addr_list = lfa1_df['ADRNR'].dropna().unique().tolist()
    for addr in addr_list:
        opts = [f"ADDRNUMBER = '{addr}'"]
        df_part = fetch_table("ADR6", tables["ADR6"], options=opts)
        adr6_df = pd.concat([adr6_df, df_part], ignore_index=True)


print("Fetching J_1IMOVEND...")
j1movend_df = pd.DataFrame()
for ven in vendor_list:
    opts = [f"LIFNR = '{ven}'"]
    df_part = fetch_table("J_1IMOVEND", tables["J_1IMOVEND"], options=opts)
    j1movend_df = pd.concat([j1movend_df, df_part], ignore_index=True)


# -------------------- Save Results --------------------
tbs = [lfb1_df, lfa1_df, lfm1_df, lfbk_df, adrc_df, adr6_df, j1movend_df]
sheets = ['LFB1', 'LFA1', 'LFM1', 'LFBK', 'ADRC', 'ADR6', 'J_1IMOVEND']

out = 'Data/Vendor/vendor_master.xlsx'
with pd.ExcelWriter(out, engine='openpyxl') as writer:
    for idx, table in enumerate(tbs):
        table.to_excel(writer, sheet_name=sheets[idx], index=False)

print("All vendor tables downloaded successfully.")

end = time.time()
mins = (end-start)//60
sec = abs((end-start) - mins*60)
print(f'\n[TIME TAKEN - {mins:.0f} MINS {sec:.0f} SECONDS]')
