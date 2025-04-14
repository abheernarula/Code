valid_values = [
    '01', # Distribtn Channel 01
    '10', # Domestic
    '20', # Exports
    '30', # Distributor
    '31', # Co–Marketed Products
    '35', # Corp. Hospital Sale
    '36', # X Urban
    '37', # E Pharmacies
    '40', # Retail
    '50', # Intitutional Sale
    '60' # STO(Stock Transfer)
]


def validate_dist_channel(value):
    return str(value) in valid_values