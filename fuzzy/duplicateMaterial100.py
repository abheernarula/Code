import pandas as pd
import numpy as np
import re
from rapidfuzz import fuzz
from tqdm import tqdm

# ----------------------------- CONFIG ---------------------------------
PO_COL = "Purchase Order Text"
MD_COL = "Material Description"
EXPORT_PATH = "zrdm_dupes.xlsx"

STRICT_EXACT_100 = True   # True => exact-normalized dupes only
THRESHOLD = 90             # fuzzy threshold when STRICT_EXACT_100 is False
LEN_DIFF_MAX = 0.30        # reject if |len(a)-len(b)|/maxlen > 30%
BLOCK_TOKENS = 2           # tokens for blocking key
KEYWORDS = [
    r'cas',
    r'p\.?/?n',            # p.n / pn / p/n
    r'gimmi',
    r'part(?:\s*number|\s*no)?',
    r'item(?:\s*number)?',
    r'product\s*code',
    r'(?<!\d)\d{4,}(?!\d)',
    r'ca',
    r'code',
    r'model'
]
# ----------------------------------------------------------------------

tqdm.pandas()


# ---------- helpers ----------------------------------------------------
def build_merged_desc(df, po_col=PO_COL, md_col=MD_COL):
    po = df[po_col].fillna("")
    md = df[md_col].fillna("")
    return np.where(po.str.strip().ne(""), po, md)

def norm_text(s: str) -> str:
    return re.sub(r"[^0-9a-z ]", " ", str(s).lower()).strip()

def block_key(text: str, n_tokens=BLOCK_TOKENS) -> str:
    toks = [t for t in text.split() if t not in {"the", "and", "of"}]
    return " ".join(toks[:n_tokens])

def length_ok(a, b, max_ratio=LEN_DIFF_MAX):
    la, lb = len(a), len(b)
    if max(la, lb) == 0:
        return True
    return abs(la - lb) / max(la, lb) <= max_ratio

def assign_groups_exact(block, col):
    codes, _ = pd.factorize(block[col])
    return pd.Series(np.where(codes >= 0, codes + 1, 0),
                     index=block.index, dtype=int)

def assign_groups_fuzzy(block, col):
    """
    Greedy, non-transitive grouping inside ONE block.
    Works on **positions**, then maps back to original indices.
    """
    texts = block[col].tolist()
    idxs  = block.index.tolist()

    groups = np.zeros(len(texts), dtype=int)
    reps   = []      # representative strings
    rep_id = []      # group ids

    for pos, txt in enumerate(texts):
        if not txt:
            gid = len(reps) + 1
            reps.append(txt); rep_id.append(gid)
            groups[pos] = gid
            continue

        placed = False
        for rpos, rep in enumerate(reps):
            if not length_ok(txt, rep):
                continue
            score = fuzz.token_sort_ratio(txt, rep)
            if score >= THRESHOLD:
                groups[pos] = rep_id[rpos]
                placed = True
                break

        if not placed:
            gid = len(reps) + 1
            reps.append(txt); rep_id.append(gid)
            groups[pos] = gid

    return pd.Series(groups, index=idxs, dtype=int)

def find_cat(text: str) -> str | None:
    t = text.lower()
    for kw in KEYWORDS:
        m = re.search(kw, t, flags=re.I)
        if m:
            start = m.start()
            return text[start:]
    return None   


# ----------------------------- MAIN -----------------------------------
if __name__ == "__main__":
    df = pd.read_excel("../../Material/ZRDM.xlsx", sheet_name='MARA')

    # 1) merged_desc
    df["merged_desc"] = build_merged_desc(df)
    df['catalogIfPresent'] = df.progress_apply(lambda row: find_cat(str(row['merged_desc'])), axis=1)

    # 2) normalized text
    df["__norm__"] = df["merged_desc"]#.map(norm_text)

    if STRICT_EXACT_100:
        df["dup_group"] = assign_groups_exact(df, "__norm__")
    else:
        # Blocking
        all_groups = np.zeros(len(df), dtype=int)
        offset = 0

        grouped = df.groupby(df["__norm__"].map(block_key), sort=False)
        for _, block in tqdm(grouped, desc="Blocks"):
            if len(block) == 1:
                offset += 1
                all_groups[block.index[0]] = offset
                continue

            block_groups = assign_groups_fuzzy(block, "__norm__")
            # shift to keep group ids unique across blocks
            mask = block_groups > 0
            block_groups.loc[mask] += offset
            all_groups[block_groups.index] = block_groups
            offset = all_groups.max()

        df["dup_group"] = all_groups.astype(int)

    df.drop(columns="__norm__", inplace=True)

    # 3) export
    ordered_cols = [MD_COL, PO_COL, "merged_desc", "dup_group"]
    keep_cols = [c for c in ordered_cols if c in df.columns]
    df.sort_values(["dup_group", "merged_desc"], inplace=True)
    df.to_excel(EXPORT_PATH, index=False,
                columns=keep_cols + [c for c in df.columns if c not in keep_cols])

    print("Done:", EXPORT_PATH)
    print("Top group sizes:")
    print(df["dup_group"].value_counts().head(10))
