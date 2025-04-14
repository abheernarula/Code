valid_list = ['biologics', 'discovery', 'development', 'clinical development']

def validatePortfolio(value):
    list_values = value.split(';')
    for i in list_values:
        if i.strip().lower() not in valid_list:
            return False
    return True

# a = 'Biologics;Development;DISCOVERY'
# b = 'biologics;CLINICAL DEVELOPMENT'
# c = 'Biologics, devehu'

# print(
#     a, '-', validatePortfolio(a), '\n',
#     b, '-', validatePortfolio(b), '\n',
#     c, '-', validatePortfolio(c)
# )