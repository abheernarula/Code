import re
import pandas as pd
import phonenumbers
from phonenumbers import (
    NumberParseException,
    is_possible_number,
    number_type,
    PhoneNumberType,
    format_number,
    PhoneNumberFormat
)

def standardizePhone(phone_str: str, default_region: str = "IN"):
    try:
        pn = phonenumbers.parse(phone_str, default_region)
        if is_possible_number(pn):
            t = number_type(pn)
            if t == PhoneNumberType.MOBILE:
                std = f"+{pn.country_code} {pn.national_number}"
                tag = "Mobile"
            elif t in (
                PhoneNumberType.FIXED_LINE,
                PhoneNumberType.FIXED_LINE_OR_MOBILE,
                PhoneNumberType.TOLL_FREE
            ):
                std = format_number(pn, PhoneNumberFormat.INTERNATIONAL)
                # tag = "Landline"
            else:
                std = format_number(pn, PhoneNumberFormat.INTERNATIONAL)
                # tag = "Other"

            std = std.replace('-', ' ')
            std = re.sub(r'\s+', ' ', std).strip()
            return std

    except NumberParseException:
        pass

    digits = re.sub(r"\D", "", phone_str).lstrip("0")
    default_cc = phonenumbers.country_code_for_region(default_region)
    std = f"+{default_cc} {digits}"
    return std


# --- Example ---
# df = pd.DataFrame({
#     "RawPhone": [
#         "020-4116347",
#         "9986497038",
#         "+91 (80) 41784600",
#         "1-800-422-6423",
#         "(212)555-1234"
#     ],
#     "Country": ["IN", "IN", "IN", "US", "US"]
# })

# df[["Phone_Std"]] = df.apply(
#     lambda row: pd.Series(standardize_and_tag(row["RawPhone"], row["Country"])),
#     axis=1
# )

# print(df)
