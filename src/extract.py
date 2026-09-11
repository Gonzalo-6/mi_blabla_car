import pandas as pd

def load_data():
    drivers = pd.read_csv('data/drivers_commutes.csv')
    passengers = pd.read_csv('data/passengers_commutes.csv')
    
    return drivers, passengers