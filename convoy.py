import pandas as pd
from os import path
import re
import sqlite3


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

    return name_two


def create_insert_sql_date(name_file):
    name_two = name_file.replace('[CHECKED].csv', '.s3db')
    data = pd.read_csv(name_file)
    df = pd.DataFrame(data, dtype='str')
    count = 0

    conn = sqlite3.connect(name_two)
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS convoy 
(vehicle_id INT PRIMARY KEY,
engine_capacity INT NOT NULL,
fuel_consumption INT NOT NULL,
maximum_load INT NOT NULL)""")

    for row in df.itertuples():
        cursor.execute('''
                INSERT INTO convoy (vehicle_id, engine_capacity, fuel_consumption, maximum_load)
                VALUES (?,?,?,?)
                ''',
                       [row.vehicle_id,
                       row.engine_capacity,
                       row.fuel_consumption,
                       row.maximum_load]
                       )
        count += 1
    conn.commit()

    if count == 1:
        print(str(count) + ' record was inserted into ' + name_two)
    else:
        print(str(count) + ' records were inserted into ' + name_two)

def pick_option(option):
    if '[CHECKED].csv' in option:
        create_insert_sql_date(option)
    elif '.csv' in option:
        checked_file = corrected_csv(option)
        create_insert_sql_date(checked_file)
    elif '.xlsx' in option:
        csv_file = xlsx_to_csv(option)
        checked_file = corrected_csv(csv_file)
        create_insert_sql_date(checked_file)


print('Input file name')
name = str(input(''))
pick_option(name)
