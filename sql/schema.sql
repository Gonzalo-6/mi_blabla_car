CREATE SCHEMA IF NOT EXISTS mi_blabla_car;

CREATE TABLE IF NOT EXISTS mi_blabla_car.passengers_trip (
    id INTEGER PRIMARY KEY,
	user_id INT,
    origin_lat FLOAT,
    origin_lon FLOAT,
    destination_lat FLOAT,
    destination_lon FLOAT,
	leaves_at TIMESTAMP,
    seats_requested FLOAT,
    created_at TIMESTAMP,
	deleted_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS mi_blabla_car.drivers_trip (
    id INTEGER PRIMARY KEY,
	user_id INT,
    origin_lat FLOAT,
    origin_lon FLOAT,
    destination_lat FLOAT,
    destination_lon FLOAT,
    leaves_at TIMESTAMP,
    seats_offered FLOAT,
    created_at TIMESTAMP,
	deleted_at TIMESTAMP
);
