valid = [
    "0001",
    "1"
]

def validateTransGroupMat(value):
    try:
        str(int(float(value)))
    except:
        return str(value) in valid
    return str(int(float(value))) in valid