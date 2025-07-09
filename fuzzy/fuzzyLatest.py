# from rapidfuzz import fuzz, process
# import itertools, numpy as np
# import pandas as pd

# def fuzzy_block_dupes(df: pd.DataFrame, block_chars: int = 4,
#                       threshold: int = 100, col: str = "Purchase Order Text") -> pd.DataFrame:
#     df = df.copy()
#     # Quick-n-dirty block key on first X normalised chars
#     df["blk"] = df[col].str[:block_chars].str.lower().str.replace(r"[^a-z0-9]", "", regex=True)
#     dup_flags = np.zeros(len(df), dtype=bool)

#     for _, block in df.groupby("blk"):
#         # RapidFuzz's cdist: vectorised pair-wise ratios inside the block
#         candidates = block.index.to_list()
#         texts      = block[col].to_list()
#         matrix     = process.cdist(texts, texts, scorer=fuzz.token_sort_ratio)
#         # upper triangle contains unique pairs
#         i_idx, j_idx = np.triu_indices(len(texts), k=1)
#         hits = (matrix[i_idx, j_idx] >= threshold)
#         dup_flags[block.index[j_idx[hits]]] = True

#     df["is_duplicate_fuzzy"] = dup_flags
#     return df.drop(columns="blk")


# ---------------------------------------------------------------------------------------------------------------


import re, unicodedata, pandas as pd

def fingerprint_exact(txt: str) -> str:
    """Return a canonical form that ONLY collapses trivial formatting."""
    if pd.isna(txt):
        return ""
    txt = unicodedata.normalize("NFKD", str(txt))   # strip accents
    txt = re.sub(r"\s+", " ", txt.strip())          # collapse whitespace
    return txt.lower()                              # <- comment this line out
                                                    #    if case must matter

def add_exact_groups(df: pd.DataFrame, col="Purchase Order Text") -> pd.DataFrame:
    df = df.copy()
    df["fp_exact"]   = df[col].apply(fingerprint_exact)
    df["grp_exact"]  = df.groupby("fp_exact").ngroup()   # 0,1,2,…
    df["is_dup_100"] = df.duplicated("fp_exact", keep="first")
    return df

add_exact_groups(pd.read_excel('../../Material/potext/ZRDM_PO.xlsx')).to_csv('zrdm_fuzzy.csv')