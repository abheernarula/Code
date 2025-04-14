

valid_list = ['Biologics', 'Chemical Development', 'Clinical Development', 'Computational and Data Sciences',
              'Discovery Biology', 'Discovery Chemistry', 'Formulation', 'Safety Assessment', 'Stability']

def validateBU(value):
    return value.lower() in [i.lower() for i in valid_list]