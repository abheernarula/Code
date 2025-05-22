import os
from tqdm import tqdm
import argparse
import pandas as pd
from rapidfuzz import fuzz
from rapidfuzz import process

parser = argparse.ArgumentParser(
    description="Fuzzy matching"
)

parser.add_argument("--data", '-d', required=True, help='Path to input excel file')
parser.add_argument("--output", "-o", default='duplicate.xlsx', help="Path to save output file")
parser.add_argument('--sheet', '-sh', help='Sheet name in excel')
parser.add_argument("--columns", "-c", required=True, help="Column names separated by ','")
parser.add_argument("--score", "-s", required=True, help="Similarity threshold for fuzzy match")
args = parser.parse_args()

print('[READING INPUT FILE]...')
input_file = args.data
output_file = args.output if args.output[-4:]=='xlsx' else os.path.join(args.output, 'duplicate.xlsx')
desc_columns = str(args.columns).split(',')
similarity_threshold = float(args.score)

df = pd.read_excel(input_file, sheet_name=args.sheet)
df['Combined_Description'] = df[desc_columns].fillna('').agg(' '.join, axis=1)

# 1) Create a tiny “block key” from the first 2 alphanumerics of each desc
df['block_key'] = (
    df['Combined_Description']
      .str.lower()
      .str.replace(r'[^a-z0-9]', '', regex=True)
      .str[:2]
)

df['Duplicate_Group'] = None
visited = set()
group_id = 1

# 2) Process each block separately
for block_key, block_df in df.groupby('block_key'):
    choices = block_df['Combined_Description'].to_dict()  # {idx: desc}
    # progress bar per block
    for idx, desc in tqdm(choices.items(), desc=f"Block '{block_key}' ({len(choices)})"):
        if idx in visited:
            continue
        # 3) Fuzzy‐match *only* within this block
        # print(idx)
        matches = process.extract(
            desc,
            choices,
            scorer=fuzz.token_sort_ratio,
            limit=None
        )
        # matches: list of (match_idx, score)
        # matched = [mid for mid, score in matches 
        #            if score >= similarity_threshold and mid != idx]
        matched = [
            mid
            for mid, score, _ in matches  # grab the third “extra” into _
            if score >= similarity_threshold and mid != idx
        ]
        if matched:
            group_idxs = [idx] + matched
            for midx in group_idxs:
                df.at[midx, 'Duplicate_Group'] = f"Group_{group_id}"
                visited.add(midx)
            group_id += 1

# 4) Write out only the duplicates
df[df['Duplicate_Group'].notna()] \
  .to_excel(output_file, index=False)
print(f"✅ Duplicates saved to: {output_file}")