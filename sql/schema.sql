-- USERS
CREATE TABLE mi_blabla_car.users (
    user_id INT PRIMARY KEY
);

-- LOCATIONS
CREATE TABLE mi_blabla_car.locations (
    location_id SERIAL PRIMARY KEY,
    latitude FLOAT,
    longitude FLOAT,
    UNIQUE(latitude, longitude)
);

-- COMMUTES
CREATE TABLE mi_blabla_car.commutes (
    commute_id INT PRIMARY KEY,
    user_id INT REFERENCES mi_blabla_car.users(user_id),
    origin_id INT REFERENCES mi_blabla_car.locations(location_id),
    destination_id INT REFERENCES mi_blabla_car.locations(location_id),
    leaves_at TIMESTAMP,
    created_at TIMESTAMP,
    deleted_at TIMESTAMP
);

-- DRIVERS
CREATE TABLE mi_blabla_car.driver_commutes (
    commute_id INT PRIMARY KEY REFERENCES mi_blabla_car.commutes(commute_id),
    user_id INT REFERENCES mi_blabla_car.users(user_id),
    seats_offered INT
);

-- PASSENGERS
CREATE TABLE mi_blabla_car.passenger_commutes (
    id SERIAL PRIMARY KEY,
    commute_id INT REFERENCES mi_blabla_car.commutes(commute_id),
    user_id INT REFERENCES mi_blabla_car.users(user_id),
    seats_requested INT
);