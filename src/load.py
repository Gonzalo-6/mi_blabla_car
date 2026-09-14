import psycopg2
import pandas as pd


def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="mi_blabla_car",
        user="postgres",
        password="1234",
        port="5432"
    )


def load_to_db(data):

    conn = get_connection()
    cursor = conn.cursor()

    try:

        
        # USERS
        
        for _, row in data['users'].iterrows():
            cursor.execute("""
                INSERT INTO mi_blabla_car.users (user_id)
                VALUES (%s)
                ON CONFLICT DO NOTHING
            """, (int(row['user_id']),))

        
        # LOCATIONS
        
        for _, row in data['locations'].iterrows():
            cursor.execute("""
                INSERT INTO mi_blabla_car.locations (latitude, longitude)
                VALUES (%s, %s)
                ON CONFLICT (latitude, longitude) DO NOTHING
            """, (float(row['lat']), float(row['lon'])))

        
        cursor.execute("""
            SELECT location_id, latitude, longitude
            FROM mi_blabla_car.locations
        """)

        rows = cursor.fetchall()

        location_dict = {
            (round(row[1],6), round(row[2],6)): row[0]
            for row in rows
        }

        
        # COMMUTES
        
        for _, row in data['commutes'].iterrows():

            # AQUÍ está la clave
            origin_key = (round(row['origin_lat'],6), round(row['origin_lon'],6))
            dest_key = (round(row['dest_lat'],6), round(row['dest_lon'],6))

            if origin_key not in location_dict:
                raise Exception(f"Origin no existe: {origin_key}")

            if dest_key not in location_dict:
                raise Exception(f"Dest no existe: {dest_key}")

            origin_id = location_dict[origin_key]
            destination_id = location_dict[dest_key]

            if origin_key not in location_dict:
                print("NO EXISTE:", origin_key)

            cursor.execute("""
                INSERT INTO mi_blabla_car.commutes
                (commute_id, user_id, origin_id, destination_id, leaves_at, created_at, deleted_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (
                int(row['commute_id']),
                int(row['user_id']),
                origin_id,
                destination_id,
                clean_value(row['leaves_at']),
                clean_value(row['created_at']),
                clean_value(row['deleted_at'])
            ))

      
        # DRIVER_COMMUTES
        
        for _, row in data['drivers'].iterrows():
            cursor.execute("""
                INSERT INTO mi_blabla_car.driver_commutes (commute_id, seats_offered)
                VALUES (%s, %s)
                ON CONFLICT DO NOTHING
            """, (
                int(row['commute_id']),
                int(row['seats_offered'])
            ))

        
        # PASSENGER_COMMUTES
        
        for _, row in data['passengers'].iterrows():
            cursor.execute("""
                INSERT INTO mi_blabla_car.passenger_commutes (commute_id, seats_taken)
                VALUES (%s, %s)
                ON CONFLICT DO NOTHING
            """, (
                int(row['commute_id']),
                int(row['seats_requested'])
            ))

        conn.commit()
        print("Datos cargados correctamente")

    except Exception as e:
        conn.rollback()
        print("Error:", e)

    finally:
        cursor.close()
        conn.close()


def clean_value(value):
    if pd.isna(value):
        return None
    return value