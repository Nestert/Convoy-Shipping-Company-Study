import pandas as pd
from os import path

print('Input file name')
name = input('')
name_two = name.replace('xlsx', 'csv')


data = pd.read_excel(name, sheet_name='Vehicles', dtype=str)
df = pd.DataFrame(data)
index = df.index
index_len = len(index)

if not path.exists(name_two):
    data.to_csv(name_two, index=None, header=True)
else:
    data.to_csv(name_two, mode='a', index=None, header=False)

if index_len == 1:
    print(str(index_len) + ' line was added to ' + name_two)
else:
    print(str(index_len) + ' lines were added to ' + name_two)
