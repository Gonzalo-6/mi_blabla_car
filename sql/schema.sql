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
                f"{row[1]},{row[2]}": row[0]
                for row in rows
        }
        # COMMUTES

        for df in [data['commutes']]:
            df['origin_key'] = df['origin_id']  # si ya no tienes lat/lon, mejor rehacer antes 

        for _, row in data['commutes'].iterrows():
            cursor.execute("""
                INSERT INTO mi_blabla_car.commutes 
                (commute_id, user_id, origin_id, destination_id, leaves_at, created_at, deleted_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (
                int(row['commute_id']),
                int(row['user_id']),
                int(row['origin_id']),
                int(row['destination_id']),
                row['leaves_at'],
                row['created_at'],
                row['deleted_at']
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
                int(row['seats_requested'])  # ojo con el nombre
            ))

        conn.commit()
        print("Datos cargados correctamente")

    except Exception as e:
        conn.rollback()
        print(" Error:", e)

    finally:
        cursor.close()
        conn.close()


def clean_value(value):
    if pd.isna(value):
        return None
    return value        