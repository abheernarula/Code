valid = [
    '90'
]

def validateAcctAssmtGrpMat(value):
    try:
        str(int(float(value)))
    except:
        return str(value).upper() in valid
    return str(int(float(value))).upper() in valid