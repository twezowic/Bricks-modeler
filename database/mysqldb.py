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