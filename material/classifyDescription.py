import pandas as pd
from tqdm import tqdm
import spacy
import re
tqdm.pandas()

nlp = spacy.load("en_core_web_sm")

# data = {
#     "Material_Description": [
#         ""
#     ]
# }

# df = pd.DataFrame(data)

# df = pd.read_excel('../../Material/ZSC1.xlsx', sheet_name='POTEXT')
df = pd.read_excel('potext.xlsx', sheet_name='Sheet1')
print(df.columns)

def classify_description(text):
    doc = nlp(text)
    
    nouns = []
    qualifiers = []
    attributes = []
    
    for token in doc:
        if re.match(r'\b\d+(\.\d+)?(mg|ml|g|kg|cm|mm|%)\b', token.text.lower()):
            attributes.append(token.text)
        elif token.pos_ == "NUM":
            attributes.append(token.text)
        elif token.pos_ == "ADJ":
            qualifiers.append(token.text)
        elif token.pos_ == "NOUN":
            nouns.append(token.text)
    
    noun = nouns[0] if nouns else ""
    
    return pd.Series({
        "Noun": noun,
        "Qualifiers": ", ".join(qualifiers),
        "Attributes": ", ".join(attributes)
    })

# classified_df = df["Material_Description"].apply(classify_description)
classified_df = df["Purchase Order Text"].astype(str).progress_apply(classify_description)
result_df = pd.concat([df, classified_df], axis=1)
# print(result_df)

result_df.to_csv('descriptionResults.csv')