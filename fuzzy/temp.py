#!/usr/bin/env python3
"""
fuzzy_group.py  –  cluster near-duplicate strings and tag each row
------------------------------------------------------------------------------
usage: python fuzzy_group.py --in data.csv --col "Purchase Order Text"
                             --out grouped.parquet --th 95
"""
import argparse, re, unicodedata
from pathlib import Path

import numpy as np
import pandas as pd
from rapidfuzz import fuzz, process


# ---------- helpers ----------------------------------------------------------
def normalise(txt: str) -> str:
    """Cheap but effective text cannonicaliser."""
    if pd.isna(txt):
        return ""
    txt = unicodedata.normalize("NFKD", str(txt))
    txt = re.sub(r"[^A-Za-z0-9]+", " ", txt)    # keep letters / digits
    return txt.lower().strip()


class UnionFind:
    """Classic disjoint-set structure for clustering."""
    def __init__(self, n): self.parent = list(range(n))
    def find(self, i):
        while i != self.parent[i]:
            self.parent[i] = self.parent[self.parent[i]]
            i = self.parent[i]
        return i
    def union(self, a, b):
        pa, pb = self.find(a), self.find(b)
        if pa != pb: self.parent[pb] = pa


def fuzzy_group(df: pd.DataFrame, col: str, threshold: int = 100,
                block_chars: int = 4) -> pd.DataFrame:
    """
    Adds 'group_id' – same integer  => same fuzzy cluster.
    """
    df = df.copy().reset_index(drop=True)
    df["_blk"] = (df[col].map(normalise)
                        .str[:block_chars]              # crude blocking key
                        .fillna(""))

    uf = UnionFind(len(df))

    for _, block in df.groupby("_blk"):
        idx   = block.index.to_list()
        texts = block[col].tolist()
        # pair-wise token-sort ratios inside this block
        sim   = process.cdist(texts, texts, scorer=fuzz.token_sort_ratio)

        i_up, j_up = np.triu_indices(len(texts), k=1)
        hits = sim[i_up, j_up] >= threshold

        for i, j in zip(i_up[hits], j_up[hits]):
            uf.union(idx[i], idx[j])

    roots = [uf.find(i) for i in range(len(df))]
    root2grp = {root: g for g, root in enumerate(dict.fromkeys(roots))}
    df["group_id"] = [root2grp[r] for r in roots]
    return df.drop(columns="_blk")


# ---------- CLI glue ---------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in",  dest="infile",  required=True,
                    help="CSV / Excel to read")
    ap.add_argument("--col", dest="column",  required=True,
                    help="Column to fuzzy-match on")
    ap.add_argument("--out", dest="outfile", required=True,
                    help="Where to save the flagged file")
    ap.add_argument("--th",  dest="th",      type=int, default=90,
                    help="Similarity threshold (0-100, default=90)")
    args = ap.parse_args()

    path_in  = Path(args.infile)
    path_out = Path(args.outfile)

    # choose the right reader/writer from the file extension
    read  = pd.read_excel if path_in.suffix.lower() in {".xls", ".xlsx"} else pd.read_csv
    write = pd.DataFrame.to_excel if path_out.suffix.lower() in {".xls", ".xlsx"} else pd.DataFrame.to_csv

    print(f"📂  Reading {path_in} …")
    df = read(path_in)

    if args.column not in df.columns:
        raise SystemExit(f"❌ Column “{args.column}” not found.")

    print(f"🔍  Clustering duplicates (threshold ≥ {args.th}) …")
    df = fuzzy_group(df, args.column, threshold=args.th)

    print(f"💾  Writing {path_out} …")
    write(df, path_out, index=False)
    print("✅  Done.  Unique groups:", df["group_id"].nunique())


if __name__ == "__main__":
    main()
