valid_values = {
        "A1", "A2", "A3", "A4", "A5", "A6",
        "C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9", "CA", "CB",
        "E1", "E2", "E3", "E4", "E5", "E6", "E7", "E8",
        "K1", "K2", "K3", "K4", "K5", "K6",
        "T0",
        "V1", "V2", "V3", "V4"
    }

def validate_planning_group(planning_group):
    return planning_group.upper() in valid_values

# Example usage:
# if __name__ == "__main__":
#     test_value = "v7"  # Change this value to test different planning groups
#     if validate_planning_group(test_value):
#         print(f"Planning group '{test_value}' is valid.")
#     else:
#         print(f"Planning group '{test_value}' is invalid.")
