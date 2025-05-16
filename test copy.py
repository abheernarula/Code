import re
import pandas as pd
import phonenumbers
from phonenumbers.phonenumberutil import COUNTRY_CODE_TO_REGION_CODE, NumberParseException
from phonenumbers import format_number, PhoneNumberFormat

# build a quick lookup of all possible calling-codes as strings:
CALLING_CODES = {str(code): regions
                 for code, regions in COUNTRY_CODE_TO_REGION_CODE.items()}

def detect_cc_and_region(raw):
    """
    Returns (calling_code_str, primary_region_iso) 
    or (None, None) if no prefix found.
    """
    digits = re.sub(r"\D", "", raw)
    # try prefixes of length 1,2,3 (max country code length is 3)
    for length in (1, 2, 3):
        prefix = digits[:length]
        if prefix in CALLING_CODES:
            # pick the first region for that code
            return prefix, CALLING_CODES[prefix][0]
    return None, None

def auto_format(raw):
    """
    1) Use detect_cc_and_region to see if raw begins with a known calling-code.
    2) Parse with that region (or fallback to local parse if none).
    3) Format internationally.
    """
    cc, region = detect_cc_and_region(raw)
    try:
        if cc:
            # we know the number starts with +CC (or 00CC)
            # ensure it has a leading '+'
            candidate = raw.strip()
            if not candidate.startswith("+"):
                candidate = "+" + re.sub(r"^0+", "", re.sub(r"\D", "", candidate))
            pn = phonenumbers.parse(candidate, None)
        else:
            # no calling code → we can’t be sure; we could:
            #  • assume a default (e.g. “IN”), or 
            #  • skip region detection altogether
            pn = phonenumbers.parse(raw, None)
        if phonenumbers.is_valid_number(pn):
            intl = format_number(pn, PhoneNumberFormat.INTERNATIONAL)
            return re.sub(r"[-]+"," ", intl).strip(), region or phonenumbers.region_code_for_number(pn)
    except NumberParseException:
        pass

    # ultimate fallback: strip to digits
    digits = re.sub(r"\D", "", raw)
    return digits, None

# example
df = pd.DataFrame({
    "RawPhone": [
        "020-4116347",
        "9986497038",
        "+91 (80) 41784600",
        "1-800-422-6423",
        "(212)555-1234",
        "7973497565"
    ]
})

df[["Phone_Std","Region"]] = df["RawPhone"]\
    .apply(lambda x: pd.Series(auto_format(x)))

print(df)
