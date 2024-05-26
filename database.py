import pandas as pd
import csv
import os

def iterate_directory(directory):
    for foldername, subfolders, filenames in os.walk(directory):
        for filename in filenames:
            file_path = os.path.join(foldername, filename)
            yield file_path

def modify_int_value(text,header=False):
    for index, value in enumerate(text):
        if value.lstrip("-").isdigit():
            text[index] = int(value)
    return f'{text}'.replace("[", "").replace("]", "")

def csv_to_sql(filename):
    file = open(filename)
    csvreader = csv.reader(file)
    header = []
    header = modify_int_value(next(csvreader),header=True)

    sql_file_name = f"{os.path.basename(filename).split('.')[0]}"
    sql_file = open(f'sql_parts/{sql_file_name}.sql', 'w')
    for row in csvreader:
        sql_insert = f'INSERT INTO {sql_file_name.upper()} ({header})\nVALUES ({modify_int_value(row)});\n'
        sql_file.write(sql_insert)
    sql_file.close()

datas = {}
for file in iterate_directory('./parts'):
    bs = os.path.basename(file).split('.')[0]
    datas[bs] = pd.read_csv(file)


def get_parts(set_id):
    inventory_id = datas["inventories"][datas["inventories"]["set_num"] == set_id]
    if not inventory_id.empty:
        df = datas["inventory_parts"][datas["inventory_parts"]["inventory_id"] == inventory_id.iloc[0, 0]]
        df.to_csv(f'{set_id}_parts.txt', index_label=False)
        df = df[["part_num", "img_url"]]
        df.to_csv(f'{set_id}_parsed_parts.txt', index_label=False)
        print('Created file with parts of the set.')
    else:
        print('Set with given id not found.')


get_parts("40550-1") # part_num to plik.obj

# f = open("statistics.txt", "w")

# for data in datas.values():
#     f.write(data.head().to_csv())
#     f.write('\n')
#     # print(d)
#     # print(data.head(10))
# f.close()

# for file in iterate_directory('./parts'):
#     csv_to_sql(file)