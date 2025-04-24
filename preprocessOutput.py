import re
import pandas as pd

def filter_issues(col, issues):
    filtered = issues.split(', ')
    res = []
    for i in filtered:
        if col in i:
            res.append(i)

    return ', '.join(res)

def preprocessOutput(df: pd.DataFrame, output_path):
    
    summary = [] 
    issueList = list(sorted(set([i.strip() for i in ','.join(df['Issues'].to_list()).split(',') if i.strip()])))
    i = 1
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Results', index=False)
        for issue in issueList:
            filter_df = df[df['Issues'].str.contains(re.escape(f"{issue}"), na=False)]
            filter_df['Issues'] = filter_df['Issues'].progress_apply(lambda x: filter_issues(issue,x))
            summary.append({'S.No.' : f'Annexure {i}', 'Particulars' : issue, 'Total Records': filter_df.shape[0]})
            filter_df.to_excel(writer, sheet_name=f'Annexure {i}', index=False)
            i+=1
        summary = pd.DataFrame(summary)
        summary.to_excel(writer, sheet_name='Summary', index=False)
    return output_path


# preprocessOutput(pd.read_excel('Outputs/Vendor/lfa1.xlsx', sheet_name='Results'))