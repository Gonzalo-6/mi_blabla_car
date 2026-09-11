from src.extract import load_data
from src.transform import transform_data
from src.load import load_to_db

drivers, passengers = load_data()

data = transform_data(drivers, passengers)

load_to_db(data)

for name, df in data.items():
    print(f"\n{name.upper()}")
    print(df.head())


print(drivers['origin_coordinates'].head(10))