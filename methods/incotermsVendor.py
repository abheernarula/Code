valid_incoterms = {
        "CFR": "Costs & Freight",
        "CIF": "Costs, insurance & freight",
        "CIP": "Carriage and insurance paid to",
        "CPT": "Carriage paid to",
        "DAF": "Delivered at frontier",
        "DAP": "Delivered at Place",
        "DAT": "Delivery at Terminal",
        "DDP": "Delivered Duty Paid",
        "DDU": "Delivered Duty Unpaid",
        "DEQ": "Delivered ex quay (duty paid)",
        "DES": "Delivered ex ship",
        "DPP": "Destination - Prepay",
        "DPU": "Delivered at Place Unloaded",
        "EWH": "Ex Our Works without Handling",
        "EXO": "Ex Our Works",
        "EXW": "Ex Works",
        "EXY": "EX Your Works",
        "FAS": "Free Alongside Ship",
        "FCA": "Free Carrier",
        "FH":  "Free house",
        "FOB": "Free on board",
        "FOR": "Free on raod",
        "HSS": "CIF - HIGH SEAS",
        "OCO": "FOB Origin - Collect",
        "OPA": "FOB Origin - Prepay & Add",
        "OPP": "FOB Origin - Prepay",
        "TPB": "FOB Origin-Prepay & Bill 3rd P",
        "UN":  "Not Free"
}

def validate_incoterms_vendor(term):
    return term.upper() in valid_incoterms.keys()

# # Example usage:
# if __name__ == "__main__":
#     test_terms = ["CFR", "DAP", "XYZ", "FCA", "TPB", "AAA"]
#     for term in test_terms:
#         if validate_incoterm(term):
#             print(f"'{term}' is a valid Incoterm.")
#         else:
#             print(f"'{term}' is invalid.")
