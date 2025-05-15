# import re
import pandas as pd
# import phonenumbers
# from phonenumbers import (
#     NumberParseException,
#     is_possible_number,
#     number_type,
#     PhoneNumberType,
# )

# def standardize_and_tag(phone_str: str, default_region: str):
#     try:
#         pn = phonenumbers.parse(phone_str, default_region)
#         if is_possible_number(pn):
#             std = f"+{pn.country_code} {pn.national_number}"
#             t = number_type(pn)
#             if t == PhoneNumberType.MOBILE:
#                 tag = "Mobile"
#             elif t in (
#                 PhoneNumberType.FIXED_LINE,
#                 PhoneNumberType.FIXED_LINE_OR_MOBILE,
#                 PhoneNumberType.TOLL_FREE,
#             ):
#                 tag = "Landline"
#             else:
#                 tag = "Other"
#             return std
#     except NumberParseException:
#         pass

#     digits = re.sub(r"\D", "", phone_str).lstrip("0")
#     default_cc = phonenumbers.country_code_for_region(default_region)
#     return f"+{default_cc} {digits}"

df = pd.DataFrame({
    "RawPhone": [
        "020-4116347",         # Delhi landline
        "9986497038",          # Indian mobile
        "+91 (80) 41784600",   # Bangalore landline
        "1-800-422-6423",      # US toll-free
        "(212)555-1234"        # US fixed-line
    ],
    'Country': [
        'IN',
        'IN',
        'IN',
        'US',
        'US'
    ]
})

# # apply and split into two columns
# df[["Phone_Std"]] = df.apply(lambda row: pd.Series(standardize_and_tag(row['RawPhone'], row['Country'])), axis=1)

# print(df)

import re
# import pandas as pd
import phonenumbers
from phonenumbers import (
    NumberParseException,
    is_possible_number,
    number_type,
    PhoneNumberType,
    format_number,
    PhoneNumberFormat
)

def standardize_and_tag(phone_str: str, default_region: str):
    try:
        pn = phonenumbers.parse(phone_str, default_region)
        if is_possible_number(pn):
            t = number_type(pn)
            # MOBILE
            if t == PhoneNumberType.MOBILE:
                std = f"+{pn.country_code} {pn.national_number}"
                tag = "Mobile"
            # LANDLINE / TOLL_FREE
            elif t in (
                PhoneNumberType.FIXED_LINE,
                PhoneNumberType.FIXED_LINE_OR_MOBILE,
                PhoneNumberType.TOLL_FREE
            ):
                # proper international format, e.g. "+91 80 4116 347"
                std = format_number(pn, PhoneNumberFormat.INTERNATIONAL)
                tag = "Landline"
            # OTHER
            else:
                std = format_number(pn, PhoneNumberFormat.INTERNATIONAL)
                tag = "Other"
            return std, tag
    except NumberParseException:
        pass

    # FALLBACK: strip to digits + default CC
    digits = re.sub(r"\D", "", phone_str).lstrip("0")
    default_cc = phonenumbers.country_code_for_region(default_region)
    return f"+{default_cc} {digits}", "Unknown"

def processRow(row):
    std, tag = standardize_and_tag(row["RawPhone"], row["Country"])
    return pd.Series({"Phone_Std": std, "Phone_Type": tag})

# --- Example ---
# df = pd.DataFrame({
#     "RawPhone": [
#         "020-4116347",         # Bangalore landline
#         "9986497038",          # Indian mobile
#         "+91 (80) 41784600",   # Bangalore landline, explicit CC
#         "1-800-422-6423",      # US toll-free
#         "(212)555-1234"        # US fixed-line
#     ]
# })

# df[["Phone_Std", "Phone_Type"]] = df["RawPhone"].apply(lambda x: pd.Series(standardize_and_tag(x, default_region="IN")))
df[["Phone_Std", 'a']] = df.apply(lambda row: processRow(row), axis=1)

print(df)