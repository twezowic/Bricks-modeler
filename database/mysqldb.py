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
            query = f"SELECT * FROM INVENTORY_PARTS WHERE inventory_id = {inventory_id};"

            cursor.execute(query)
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