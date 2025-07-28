import pandas as pd
from pathlib import Path


in_file  = Path("../../Material/dupe/zsc2.xlsx")        
out_file = "zsc2_action_plan.xlsx"

df = pd.read_excel(in_file)
df["PR"] = pd.to_datetime(df["PR"], errors="coerce")  

def assign_action(group: pd.DataFrame) -> pd.DataFrame:
    
    group = group.copy()
    group["Action"] = "Block"                     
    
    if group["PR"].notna().sum() == 0:
        group.iloc[0, group.columns.get_loc("Action")] = "Use"
        return group
    
    def latest_idx(mask=None):
        target = group if mask is None else group[mask]
        return target["PR"].idxmax()
    
    span_years = (group["PR"].max() - group["PR"].min()).days / 365.25
    
    # gmp_mask     = group["Plants Marc"].str.contains(r"\bGmp\b",     case=False, na=False)
    # non_gmp_mask = group["Plants Marc"].str.contains(r"\bNon.*Gmp\b",case=False, na=False)
    
    gmp_mask     = group["Plants Marc"] == 'Gmp'
    non_gmp_mask = group["Plants Marc"] == 'Non -Gmp'
    
    if span_years < 3 and not gmp_mask.any() and not non_gmp_mask.any():
        winner_idx = latest_idx(gmp_mask)
    else:
        winner_idx = latest_idx()
    
    group.loc[winner_idx, "Action"] = "Use"
    
    return group

def assign_block(grp: pd.DataFrame):
    
    grp = grp.copy()
    
    if grp['Action'].to_list()[0] == 'Use':
        return grp
    else:
        mask_block = grp["Action"] == "Block"
        grp.loc[mask_block & grp["PR"].notna(), "Action"] = "Block for procurement"

    return grp


df = (
    df.groupby("dup_group", group_keys=False)
      .apply(assign_action)
      .sort_values(["dup_group", "Action"], ascending=[True, False])
)

df = (
    df.groupby("Action", group_keys=False)
      .apply(assign_block)
      .sort_values(["dup_group", "Action"], ascending=[True, False])
)

df.to_excel(out_file, index=False)
print(f"✨Action plan saved to {out_file}")
