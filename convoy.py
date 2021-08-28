import xml.etree.ElementTree

import pandas as pd
from os import path
import re
import sqlite3
import json
from lxml import etree


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

    data.to_csv(name_two, index=None, header=True)

    if count == 1:
        print(str(count) + ' cell was corrected in ' + name_two)
    else:
        print(str(count) + ' cells were corrected in ' + name_two)

    return name_two


def create_insert_sql_date(name_file):
    def count_score(engine_capacity, fuel_consumption, maximum_load):
        score = 0
        avg_route = 4.5
        fuel_used = avg_route * fuel_consumption
        if maximum_load >= 20:
            score += 2
        if fuel_used <= 230:
            score += 2
        else:
            score += 1
        if fuel_used // engine_capacity == 1:
            score += 1
        elif fuel_used // engine_capacity == 0:
            score += 2
        return score
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
maximum_load INT NOT NULL,
score INT NOT NULL)""")

    for row in df.itertuples():
        cursor.execute('''
                INSERT INTO convoy (vehicle_id, engine_capacity, fuel_consumption, maximum_load, score)
                VALUES (?,?,?,?,?)
                ''',
                       [row.vehicle_id,
                       row.engine_capacity,
                       row.fuel_consumption,
                       row.maximum_load,
                        count_score(int(row.engine_capacity), int(row.fuel_consumption), int(row.maximum_load))]
                       )
        count += 1
    conn.commit()

    if count == 1:
        print(str(count) + ' record was inserted into ' + name_two)
    else:
        print(str(count) + ' records were inserted into ' + name_two)

    return name_two




def create_json(name_file):
    name_two = name_file.replace('.s3db', '.json')
    conn = sqlite3.connect(name_file)
    cursor = conn.cursor()
    cursor.execute("""SELECT vehicle_id,engine_capacity,fuel_consumption,maximum_load FROM convoy WHERE score>3""")
    data = cursor.fetchall()
    header_data = list(map(lambda x: x[0], cursor.description))
    small_xui = []
    for i in range(len(data)):
        xui_dict = {}
        for index, item in enumerate(data[i]):
            xui_dict[header_data[index]] = item
        small_xui.append(xui_dict)

    big_xui = {'convoy': small_xui}
    with open(name_two, "w") as json_file:
        json.dump(big_xui, json_file)

    if len(small_xui) == 1:
        print(str(len(small_xui)) + ' vehicle was saved into ' + name_two)
    else:
        print(str(len(small_xui)) + ' vehicles were saved into ' + name_two)


def create_xml(name_file):
    name_two = name_file.replace('.s3db', '.xml')
    conn = sqlite3.connect(name_file)
    cursor = conn.cursor()
    cursor.execute("""SELECT vehicle_id,engine_capacity,fuel_consumption,maximum_load FROM convoy WHERE score<=3""")
    data = cursor.fetchall()
    header_data = list(map(lambda x: x[0], cursor.description))
    small_xui = ['<convoy>']
    count = 0
    for i in range(len(data)):
        small_xui.append('<vehicle>')
        for index, item in enumerate(data[i]):
            small_xui.append('<{}>'.format(header_data[index]) + str(item) + '</{}>'.format(header_data[index]))
        small_xui.append('</vehicle>')
        count += 1
    small_xui.append('</convoy>')

    big_xui = ''.join(small_xui)

    with open(name_two, "w") as xml_file:
        if big_xui == '<convoy></convoy>':
            xml_file.write(big_xui)
        else:
            root = etree.fromstring(big_xui)
            tree = etree.tostring(root, pretty_print=True)
            xml_file.write(tree.decode('utf-8'))

    if count == 1:
        print(str(count) + ' vehicle was saved into ' + name_two)
    else:
        print(str(count) + ' vehicles were saved into ' + name_two)

def pick_option(option):
    if '.s3db' in option:
        create_json(option)
        create_xml(option)
    elif '[CHECKED].csv' in option:
        sql_name = create_insert_sql_date(option)
        create_json(sql_name)
        create_xml(sql_name)
    elif '.csv' in option:
        checked_file = corrected_csv(option)
        sql_name = create_insert_sql_date(checked_file)
        create_json(sql_name)
        create_xml(sql_name)
    elif '.xlsx' in option:
        csv_file = xlsx_to_csv(option)
        checked_file = corrected_csv(csv_file)
        sql_name = create_insert_sql_date(checked_file)
        create_json(sql_name)
        create_xml(sql_name)


print('Input file name')
name = str(input(''))
pick_option(name)
