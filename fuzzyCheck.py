import os
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
similarity_threshold = args.score

df = pd.read_excel(input_file, sheet_name=args.sheet)
df['Combined_Description'] = df[desc_columns].fillna('').agg(' '.join, axis=1)

print('[DONE]...')

df['Duplicate_Group'] = None
group_id = 1
visited = set()

print('[FINDING DUPES]...')

for i, desc in enumerate(df['Combined_Description']):
    if i in visited:
        continue
    matches = process.extract(desc, df['Combined_Description'], scorer=fuzz.token_sort_ratio, limit=None)
    # for idx, score in matches:
    #     if score >= similarity_threshold and idx != 1:
    #         matched_indices.append(idx)
    matched_indices = [idx for idx, score in matches if score >= similarity_threshold and idx != i]
    
    if matched_indices:
        all_indices = [i] + matched_indices
        for idx in all_indices:
            df.at[idx, 'Duplicate_Group'] = f"Group_{group_id}"
            visited.add(idx)
        group_id += 1

print('[DONE]...')

df_duplicates = df[df['Duplicate_Group'].notnull()]
df_duplicates.to_excel(output_file, index=False)
print(f"✅ Duplicates saved to: {output_file}")
