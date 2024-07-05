# https://stackoverflow.com/questions/39281594/error-1698-28000-access-denied-for-user-rootlocalhost

import mysql.connector

host = 'localhost'
database = 'LEGO' 
user = 'root'

def get_inventory_parts(inventory_id):
    try:
        connection = mysql.connector.connect(
            host=host,
            database=database,
            user=user
        )

        if connection.is_connected():
            cursor = connection.cursor()

            query = "SELECT * FROM INVENTORY_PARTS WHERE inventory_id = %s;"
            cursor.execute(query, (inventory_id,))

            results = cursor.fetchall()

            if results:
                for row in results:
                    print(row)
            else:
                print(f"inventory: {inventory_id} not found")

            
    except mysql.connector.Error as err:
        print(f"Connection error: {err}")

    finally:
        connection.close()


def get_part_description(part_num):
    try:
        connection = mysql.connector.connect(
            host=host,
            database=database,
            user=user
        )

        if connection.is_connected():
            cursor = connection.cursor()
            
            query = "SELECT name FROM PARTS WHERE part_num = %s;"
            cursor.execute(query, (part_num,))

            result = cursor.fetchone()

            if result:
                return result[0]
            else:
                print(f"inventory: {part_num} not found")

            
    except mysql.connector.Error as err:
        print(f"Connection error: {err}")

    finally:
        connection.close()


def get_parts_thumbnail():
    try:
        connection = mysql.connector.connect(
            host=host,
            database=database,
            user=user
        )

        if connection.is_connected():
            cursor = connection.cursor()
            
            query = """
                SELECT p.part_num, p.name, MAX(i.img_url) AS img_url 
                FROM PARTS p 
                LEFT JOIN INVENTORY_PARTS i ON p.part_num = i.part_num 
                WHERE i.img_url IS NOT NULL 
                GROUP BY p.part_num, p.name;
            """
            cursor.execute(query)

            result = cursor.fetchall()

            return result

    except mysql.connector.Error as err:
        print(f"Connection error: {err}")

    finally:
        connection.close()


res = []
for a, b, c in get_parts_thumbnail():
    if c is None:
        print('a')

# import pandas as pd

# inventory = pd.read_csv('database/parts/inventory_parts.csv')
# filtered_inventory = inventory[inventory['part_num'].isin(res)]
# first_occurrences = filtered_inventory.groupby('part_num').first().reset_index()
# first_occurrences.to_csv('database/filtered_parts/thumbnail.csv', index=False)