import pandas as pd
import numpy as np
import re
import networkx as nx
from rapidfuzz import process, fuzz
from tqdm import tqdm
tqdm.pandas()

# ------------------------------------------------------------------------------
# CONFIG
PO_COL = "Purchase Order Text"
MD_COL = "Material Description"
THRESHOLD = 100          # similarity cutoff (0-100). Raise = stricter matches
BLOCK_TOKENS = 2        # how many leading tokens to use for blocking key
EXPORT_PATH = "zsc2_dupes.xlsx"
KEYWORDS = [
    r'cat',
    r'p\.?/?n',            # p.n / pn / p/n
    r'gimmi',
    r'part(?:\s*number|\s*no)?',
    r'item(?:\s*number)?',
    r'product\s*code',
    r'(?<!\d)\d{4,}(?!\d)',
]
# ------------------------------------------------------------------------------

# def build_merged_desc(df, po_col=PO_COL, md_col=MD_COL):
#     po = df[po_col].fillna("")
#     md = df[md_col].fillna("")
#     mask_po_nonempty = po.str.strip().ne("").to_numpy()
#     mask_desc_in_po  = np.array([mdi.lower() in poi.lower() for mdi, poi in zip(md, po)], dtype=bool)
#     return np.where(mask_po_nonempty , po,
#                     np.where(mask_po_nonempty & mask_desc_in_po, md, ""))

def norm_text(s: str) -> str:
    return re.sub(r"[^0-9a-z ]", " ", str(s).lower()).strip()

def block_key(text: str, n_tokens=BLOCK_TOKENS) -> str:
    toks = text.split()
    return " ".join(toks[:n_tokens])

def cdist_pairs(strs, scorer, threshold):
    """
    Version-agnostic wrapper for rapidfuzz.process.cdist.
    - v2.x returns a 2D numpy array
    - v3.x returns an iterable of (i, j, score [, extra]) tuples
    """
    out = process.cdist(strs, strs, scorer=scorer)
    if isinstance(out, np.ndarray):  # v2.x style
        for i in range(len(strs)):
            for j in range(i + 1, len(strs)):
                score = out[i, j]
                if score >= threshold:
                    yield i, j, score
    else:  # v3.x style
        for tpl in out:
            i, j, score = tpl[:3]
            if score >= threshold:
                yield i, j, score

def fuzzy_group(df, text_col="merged_desc", threshold=THRESHOLD):
    # Normalize
    df["__norm__"] = df[text_col].map(norm_text)

    # Blocking
    blocks = {}
    for idx, text in df["__norm__"].items():
        key = block_key(text)
        blocks.setdefault(key, []).append((idx, text))

    # Graph build
    G = nx.Graph()
    G.add_nodes_from(df.index)

    for block_rows in blocks.values():
        if len(block_rows) < 2:
            continue
        idxs = [r[0] for r in block_rows]
        strs = [r[1] for r in block_rows]

        # Add edges for similar pairs
        for i, j, score in cdist_pairs(strs, fuzz.token_set_ratio, threshold):
            if i < j:
                G.add_edge(idxs[i], idxs[j])

    # Connected components -> group ids
    components = sorted(nx.connected_components(G), key=len, reverse=True)
    group_id = {}
    for gid, comp in enumerate(components, start=1):
        for node in comp:
            group_id[node] = gid

    df["dup_group"] = df.index.map(group_id).fillna(0).astype(int)  # 0 = unique
    df.drop(columns="__norm__", inplace=True)
    return df

def find_cat(text: str) -> str | None:
    t = text.lower()
    for kw in KEYWORDS:
        m = re.search(kw, t, flags=re.I)
        if m:
            start = m.start()
            return text[start:]
    return None           
       
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    # Load your file
    df = pd.read_excel('ZSC2.xlsx') # , sheet_name='POTEXT')  # <-- change path
    

    # 1) Build merged description
    # df["merged_desc"] = build_merged_desc(df)
    po = df["Purchase Order Text"].fillna("")
    md = df["Material Description"].fillna("")
    df["merged_desc"] = np.where(po.str.strip().ne(""), po, md)
    
    df['catalogIfPresent'] = df.progress_apply(lambda row: find_cat(str(row['merged_desc'])), axis=1)

    # 2) Fuzzy group on merged_desc
    df = fuzzy_group(df, text_col="merged_desc", threshold=THRESHOLD)

    # 3) Optional: sort & export
    out_cols = [MD_COL, PO_COL, "merged_desc", "dup_group"]
    existing_cols = [c for c in out_cols if c in df.columns]
    df.sort_values(["dup_group", "merged_desc"], inplace=True)
    df.to_excel(EXPORT_PATH, index=False, columns=existing_cols + [c for c in df.columns if c not in existing_cols])

    print("Done! Exported to:", EXPORT_PATH)
    print("Unique rows:", (df["dup_group"] == 0).sum())
    print("Top groups:\n", df.groupby("dup_group").size().sort_values(ascending=False).head(10))
