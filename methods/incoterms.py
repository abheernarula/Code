valid_values = [
    'CFR',
    'CIF',
    'CIP',
    'CPT',
    'DAF',
    'DAP',
    'DAT',
    'DDP',
    'DDU',
    'DEQ',
    'DES',
    'DPP',
    'DPU',
    'EWH',
    'EXO',
    'EXW',
    'EXY',
    'FAS',
    'FCA',
    'FH',
    'FOB',
    'FOR',
    'HSS',
    'OCO',
    'OPA',
    'OPP',
    'TPB',
    'UN'
]


def validate_incoterms(value):
    return str(value) in valid_values