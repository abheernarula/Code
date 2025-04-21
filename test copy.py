import datetime


print(str(datetime.date.today()).replace("-","") + str(datetime.datetime.now().time()).replace(":","").replace(".","_"))