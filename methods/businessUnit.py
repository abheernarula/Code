

valid_list = ['Biologics', 'Chemical Development', 'Clinical Development', 'Computational and Data Sciences',
              'Discovery Biology', 'Discovery Chemistry', 'Formulation', 'Safety Assessment', 'Stability']

def validateBU(value):
    vals = str(value).split(';')
    vals = [i.strip() for i in vals]
    
    res = True
    for val in vals:
        if val.lower() not in [i.lower() for i in valid_list]:
            res = False
            return res
    return res