allowed_codes = {
        "0001", "0002", "0003", "0004", "0005", "0006", "0007",
        "0012", "0100", "0110", "0120", "0130", "0140", "0150", "0160", "0170",
        "CPD", "CPDA", "DEBI", "KUNA", "LCMS", "LCMX", "VVD",
        "X001", "X002",
        "YB01", "YB02", "YB03", "YBAC", "YBEC", "YBOC", "YBPC", "YBVC",
        "Z001", "Z002", "Z003", "Z004", "Z005", "Z006", "Z007", "Z008", "Z009",
        "Z010", "Z011", "Z012", "Z013", "Z014", "Z015", "Z016", "Z017", "Z018", "Z023",
        "ZNRM",
        "ZX01", "ZX02"
    }

def validate_account_group_vendor(account_group):
    return account_group.upper() in allowed_codes

# Example usage:
# if __name__ == "__main__":
#     test_code = "znrh"  # change to test different account groups
#     if validate_account_group(test_code):
#         print(f"Account group '{test_code}' is valid.")
#     else:
#         print(f"Account group '{test_code}' is invalid.")
