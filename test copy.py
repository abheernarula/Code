import pandas as pd
import re

a = str(input("Enter string: "))
print()

print(f"String length - {len(a)}")
print(f"Valid -> {bool(re.fullmatch(r".{0,40}",a))}")