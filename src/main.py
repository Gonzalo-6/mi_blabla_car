import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import ast

# conexión
conn = psycopg2.connect(
    host="localhost",
    database="mi_blabla_car",
    user="postgres",
    password="1234",
    port="5432"
)

cursor = conn.cursor()

# cargar CSVs
drivers = pd.read_csv("data/drivers_trip.csv")
passengers = pd.read_csv("data/passengers_trips.csv")



# DRIVERS
drivers['origin_coordinates'] = drivers['origin_coordinates'].apply(ast.literal_eval)
drivers['destination_coordinates'] = drivers['destination_coordinates'].apply(ast.literal_eval)

drivers['origin_lat'] = drivers['origin_coordinates'].apply(lambda x: x[0])
drivers['origin_lon'] = drivers['origin_coordinates'].apply(lambda x: x[1])
drivers['destination_lat'] = drivers['destination_coordinates'].apply(lambda x: x[0])
drivers['destination_lon'] = drivers['destination_coordinates'].apply(lambda x: x[1])

# PASSENGERS
passengers['origin_coordinates'] = passengers['origin_coordinates'].apply(ast.literal_eval)
passengers['destination_coordinates'] = passengers['destination_coordinates'].apply(ast.literal_eval)

passengers['origin_lat'] = passengers['origin_coordinates'].apply(lambda x: x[0])
passengers['origin_lon'] = passengers['origin_coordinates'].apply(lambda x: x[1])
passengers['destination_lat'] = passengers['destination_coordinates'].apply(lambda x: x[0])
passengers['destination_lon'] = passengers['destination_coordinates'].apply(lambda x: x[1])

# convertir fechas
drivers['leaves_at'] = pd.to_datetime(drivers['leaves_at'], errors='coerce')
drivers['created_at'] = pd.to_datetime(drivers['created_at'], errors='coerce')
drivers['deleted_at'] = pd.to_datetime(drivers['deleted_at'], errors='coerce')

passengers['leaves_at'] = pd.to_datetime(passengers['leaves_at'], errors='coerce')
passengers['created_at'] = pd.to_datetime(passengers['created_at'], errors='coerce')
passengers['deleted_at'] = pd.to_datetime(passengers['deleted_at'], errors='coerce')

# 🔥 CLAVE: convertir a object
for col in ['leaves_at', 'created_at', 'deleted_at']:
    drivers[col] = drivers[col].astype(object)
    passengers[col] = passengers[col].astype(object)

# 🔥 AHORA sí: NaT → None
drivers = drivers.where(pd.notnull(drivers), None)
passengers = passengers.where(pd.notnull(passengers), None)

# seleccionar columnas

drivers_data = drivers[[
    'id',
    'user_id',
    'origin_lat',
    'origin_lon',
    'destination_lat',
    'destination_lon',
    'leaves_at',
    'seats_offered',
    'created_at',
    'deleted_at'
]].values.tolist()

passengers_data = passengers[[
    'id',
    'user_id',
    'origin_lat',
    'origin_lon',
    'destination_lat',
    'destination_lon',
    'leaves_at',
    'seats_requested',
    'created_at',
    'deleted_at'
]].values.tolist()

print(drivers[['deleted_at']].head())
print(drivers_data[0])

print(drivers[['deleted_at']].head())
print(type(drivers_data[0][-1]))

# insertar drivers


execute_values(
    cursor,
    """
    INSERT INTO mi_blabla_car.drivers_trip 
    (id, user_id, origin_lat, origin_lon, destination_lat, destination_lon, leaves_at, seats_offered, created_at, deleted_at)
    VALUES %s
    ON CONFLICT (id) DO NOTHING
    """,
    drivers_data
)

# insertar passengers

execute_values(
    cursor,
    """
    INSERT INTO mi_blabla_car.passengers_trip 
    (id, user_id, origin_lat, origin_lon, destination_lat, destination_lon, leaves_at, seats_requested, created_at, deleted_at)
    VALUES %s
    ON CONFLICT (id) DO NOTHING
    """,
    passengers_data
)

conn.commit()
cursor.close()
conn.close()