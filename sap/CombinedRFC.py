from pyrfc import Connection
import pandas as pd
import time
import os

# -------------------- SAP Connection --------------------
conn = Connection(
    user='hammad',
    passwd='Uniqus@12345678',
    ashost='riseeccapp4',   # SAP Application Server
    sysnr='04',
    client='300',
    lang='EN'
)

# -------------------- Table Dictionary --------------------
TABLES = {
    "vendor": {
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
    },

    "customer": {
        "KNA1": ['KUNNR','NAME1','NAME2','NAME3','NAME4','ORT01','LAND1','STRAS',
                 'PFACH','PSTLZ','REGIO','TELF1','TELF2','SPRAS','ADRNR','STCD1',
                 'STCD2','STCD3','STCD4','KTOKD','LOEVM','ZZCRLIMIT','ZZCRRISK'],
        "KNB1": ['KUNNR','BUKRS','AKONT','ZTERM','ZWELS','FDGRV','TOGRU','LNRZE',
                 'BEGRU','LOEVM','SPEER','ZAMIM','ZUAWA','EIKTO'],
        "KNVV": ['KUNNR','VKORG','VTWEG','SPART','KALKS','KDGRP','BZIRK','KONDA',
                 'PLTYP','AWKEY','LOEVM','VERSG'],
        "ADRC": ['ADDRNUMBER','STREET','STR_SUPPL1','STR_SUPPL2','STR_SUPPL3',
                 'LOCATION','POST_CODE1','POST_CODE2','PO_BOX','COUNTRY'],
        "ADR6": ['ADDRNUMBER','SMTP_ADDR']
    },

    "material": {
        "MARA": ['MATNR', 'MTART', 'MEINS', 'MTPOS_MARA', 'MATKL', 'ATTYP', 'MBRSH',
                 'BISMT','MSTAE','SPART','RBNRM','TRAGR','XCHPF','MPROF','EKWSL',
                 'QMPUR','ERSDA','ERNAM','LVORM'],
        "MAKT": ['MATNR','MAKTX','MAKTG'],
        "MARC": ['MATNR','WERKS','STEUC','ZZONE','ZSTCOND','SSQSS','LADGR','PRCTR',
                 'DISPO','DISMM','EKGRP','LGPRO','XCHPF','MAABC','BESKZ','MTVFP',
                 'CASNR','FEVOR','SFEPR','QZGTP','ZZACCASSCAT','LVORM'],
        "MBEW": ['MATNR','BKLAS','VPRSV','BWKEY','BWTAR','BWTTY'],
        "MLAN": ["MATNR","TAXIM"],
        "MVKE": ["MATNR","MTPOS","KTGRM"],
        "ZMM60": ["MATNR","ZPPPOTEXT"]
    }
}

# -------------------- RFC Fetch Function --------------------
def fetch_table(table, fields, options=[], row_count=300000):
    rows, offset = [], 0
    while True:
        result = conn.call('RFC_READ_TABLE',
                           QUERY_TABLE=table,
                           DELIMITER='|',
                           FIELDS=[{'FIELDNAME': f} for f in fields],
                           OPTIONS=[{'TEXT': o} for o in options] if options else [],
                           ROWSKIPS=offset,
                           ROWCOUNT=row_count)
        data = result['DATA']
        for row in data:
            split_row = row['WA'].split('|')
            if len(split_row) == len(fields):
                rows.append(split_row)
        if len(data) < row_count:
            break
        offset += row_count
    return pd.DataFrame(rows, columns=fields)

# -------------------- Main Extractor --------------------
def extract(object_type):
    start = time.time()
    print(f"🔄 Extracting {object_type.upper()} data...")
    out_dir = f"Data/{object_type.capitalize()}"
    os.makedirs(out_dir, exist_ok=True)

    dfs, sheets = [], []
    tables = TABLES[object_type]

    # Vendor logic
    if object_type == "vendor":
        lfb1 = fetch_table("LFB1", tables["LFB1"], options=["BUKRS = '5100' OR BUKRS = '5500'"])
        vendor_list = lfb1['LIFNR'].unique().tolist()
        dfs.append(lfb1); sheets.append("LFB1")

        for t in ["LFA1","LFM1","LFBK","J_1IMOVEND"]:
            df = pd.concat([fetch_table(t, tables[t], options=[f"LIFNR = '{v}'"]) for v in vendor_list], ignore_index=True)
            dfs.append(df); sheets.append(t)

        # ADRC + ADR6 via ADRNR
        if not dfs[1].empty and "ADRNR" in dfs[1].columns:
            addr_list = dfs[1]['ADRNR'].dropna().unique().tolist()
            for t in ["ADRC","ADR6"]:
                df = pd.concat([fetch_table(t, tables[t], options=[f"ADDRNUMBER = '{a}'"]) for a in addr_list], ignore_index=True)
                dfs.append(df); sheets.append(t)

    # Customer logic
    elif object_type == "customer":
        kna1 = fetch_table("KNA1", tables["KNA1"])
        customer_list = kna1['KUNNR'].unique().tolist()
        dfs.append(kna1); sheets.append("KNA1")

        for t in ["KNB1","KNVV"]:
            df = pd.concat([fetch_table(t, tables[t], options=[f"KUNNR = '{c}'"]) for c in customer_list], ignore_index=True)
            dfs.append(df); sheets.append(t)

        if not kna1.empty and "ADRNR" in kna1.columns:
            addr_list = kna1['ADRNR'].dropna().unique().tolist()
            for t in ["ADRC","ADR6"]:
                df = pd.concat([fetch_table(t, tables[t], options=[f"ADDRNUMBER = '{a}'"]) for a in addr_list], ignore_index=True)
                dfs.append(df); sheets.append(t)

    # Material logic
    elif object_type == "material":
        mara = fetch_table("MARA", tables["MARA"], options=["MTART = 'ERSA'"])
        mats = mara['MATNR'].tolist()
        dfs.append(mara); sheets.append("MARA")

        marc = pd.concat([fetch_table("MARC", tables["MARC"], options=[f"MATNR = '{m}' AND WERKS LIKE '5%'"]) for m in mats], ignore_index=True)
        dfs.append(marc); sheets.append("MARC")
        filtered = marc['MATNR'].unique().tolist()

        for t in ["MAKT","MBEW","MLAN","MVKE"]:
            df = pd.concat([fetch_table(t, tables[t], options=[f"MATNR = '{m}'"]) for m in filtered], ignore_index=True)
            dfs.append(df); sheets.append(t)

    # Save results
    out_xlsx = os.path.join(out_dir, f"{object_type}_data.xlsx")
    with pd.ExcelWriter(out_xlsx, engine="openpyxl") as writer:
        for df, name in zip(dfs, sheets):
            df.to_excel(writer, sheet_name=name, index=False)

    mins, sec = divmod(time.time()-start, 60)
    print(f"✅ {object_type.capitalize()} data extracted in {int(mins)}m {int(sec)}s → {out_xlsx}")

# -------------------- Run --------------------
if __name__ == "__main__":
    extract("vendor")
    extract("customer")
    extract("material")
