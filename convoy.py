import pandas as pd
from os import path
import re

def xlsx_to_csv(name_file):
    name_two = name_file.replace('.xlsx', '.csv')
    data = pd.read_excel(name_file, sheet_name='Vehicles', dtype=str)
    index_len = len(data.index)

    if not path.exists(name_two):
        data.to_csv(name_two, index=None, header=True)
    else:
        data.to_csv(name_two, mode='a', index=None, header=False)

    if index_len == 1:
        print(str(index_len) + ' line was added to ' + name_two)
    else:
        print(str(index_len) + ' lines were added to ' + name_two)

    return name_two


def corrected_csv(name_file):
    name_two = name_file.replace('.csv', '[CHECKED].csv')
    data = pd.read_csv(name_file, delimiter=',', dtype='str')
    colums_tuple = tuple(data.columns)
    count = 0

    def regex_counter(value):
        regex = re.compile('[^0-9]')
        initial_value = value
        value = regex.sub('', value)
        nonlocal count
        if initial_value != value:
            count += 1
        return value

    for col in colums_tuple:
            data[col] = data[col].apply(lambda x: regex_counter(x))



    data.to_csv(name_two, index=None, header=True)  # maybe correct mode='a'

    if count == 1:
        print(str(count) + ' cell was corrected in ' + name_two)
    else:
        print(str(count) + ' cells were corrected in ' + name_two)




def pick_option(option):
    if '.csv' in option:
        corrected_csv(option)
    elif '.xlsx' in option:
        csv_file = xlsx_to_csv(option)
        corrected_csv(csv_file)


print('Input file name')
name = str(input(''))
pick_option(name)
