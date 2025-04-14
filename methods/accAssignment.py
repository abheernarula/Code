valid_values = [
    '01', # Domestic Revenues
    '02', # Foreign Revenues
    '03', # Affiliat Comp Revenue
    '04', # Dom. Rev. without CO
    '10', # Domestic  Customer
    '11', # Dom direct revenue
    '12', # Dom dealer revenue
    '13', # Dom assoc co revenue
    '14', # Dom subs co revenue
    '15', # Dom self
    '20', # Export Customer
    '21', # Exp direct revenue
    '23', # Exp assoc co revenue
    '24', # Exp subs co revenue
    '30' # Inter Company Cust
]


def validate_acc_assignment(value):
    return (str(int(float(value))) in valid_values)