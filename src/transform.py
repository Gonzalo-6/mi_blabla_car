import pandas as pd


# Helpers


def split_coords(coord):
    if pd.isnull(coord):
        return None, None

    # Limpiar string
    coord = coord.replace(" ", "").replace("[", "").replace("]", "")

    try:
        lat, lon = coord.split(',')
        return float(lat), float(lon)
    except Exception:
        return None, None

def clean_dates(df):
    df['leaves_at'] = pd.to_datetime(df['leaves_at'], errors='coerce')
    df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
    df['deleted_at'] = pd.to_datetime(df['deleted_at'], errors='coerce')
    return df



# Main transform


def transform_data(drivers_df, passengers_df):

    
    # 1. LIMPIEZA INICIAL
   
    
    drivers_df = clean_dates(drivers_df)
    passengers_df = clean_dates(passengers_df)

    
    # 2. COORDENADAS
    
    
    for df in [drivers_df, passengers_df]:
        df[['origin_lat', 'origin_lon']] = df['origin_coordinates'].apply(
            lambda x: pd.Series(split_coords(x))
        )
        df[['dest_lat', 'dest_lon']] = df['destination_coordinates'].apply(
            lambda x: pd.Series(split_coords(x))
        )

   
    # 3. USERS
    
    
    df_users = pd.concat([
        drivers_df[['user_id']],
        passengers_df[['user_id']]
    ]).drop_duplicates().reset_index(drop=True)

    
    # 4. LOCATIONS
    
    
    df_locations = pd.concat([
        drivers_df[['origin_lat', 'origin_lon']].rename(columns={'origin_lat':'lat','origin_lon':'lon'}),
        drivers_df[['dest_lat', 'dest_lon']].rename(columns={'dest_lat':'lat','dest_lon':'lon'}),
        passengers_df[['origin_lat', 'origin_lon']].rename(columns={'origin_lat':'lat','origin_lon':'lon'}),
        passengers_df[['dest_lat', 'dest_lon']].rename(columns={'dest_lat':'lat','dest_lon':'lon'})
    ]).drop_duplicates().reset_index(drop=True)

    # Crear clave para mapear
    df_locations['key'] = list(zip(df_locations['lat'], df_locations['lon']))

   
    # 5. MAPEO LOCATION_ID
    
    for df in [drivers_df, passengers_df]:
        df['origin_lat'] = df['origin_lat'].round(6)
        df['origin_lon'] = df['origin_lon'].round(6)
        df['dest_lat'] = df['dest_lat'].round(6)
        df['dest_lon'] = df['dest_lon'].round(6)

    df_locations['lat'] = df_locations['lat'].round(6)
    df_locations['lon'] = df_locations['lon'].round(6)  

    location_dict = {k: i+1 for i, k in enumerate(df_locations['key'])}

    for df in [drivers_df, passengers_df]:
        df['origin_key'] = list(zip(df['origin_lat'], df['origin_lon']))
        df['dest_key'] = list(zip(df['dest_lat'], df['dest_lon']))

        df['origin_id'] = df['origin_key'].map(location_dict)
        df['destination_id'] = df['dest_key'].map(location_dict)

        
    # 6. COMMUTES
        
    
    df_commutes = pd.concat([
        drivers_df[['id','user_id','origin_lat','origin_lon','dest_lat','dest_lon','leaves_at','created_at','deleted_at']],
        passengers_df[['id','user_id','origin_lat','origin_lon','dest_lat','dest_lon','leaves_at','created_at','deleted_at']]
        ]).drop_duplicates(subset=['id']).rename(columns={'id':'commute_id'})

    df_commutes['leaves_date'] = df_commutes['leaves_at'].dt.date
    df_commutes['leaves_hour'] = df_commutes['leaves_at'].dt.hour

    df_commutes['created_date'] = df_commutes['created_at'].dt.date
    df_commutes['created_hour'] = df_commutes['created_at'].dt.hour

        
    # 7. DRIVER / PASSENGER
  
    
    df_driver = drivers_df[['id','seats_offered']].rename(columns={'id':'commute_id'})
    
    
    if 'seats_requested' in passengers_df.columns:
        df_passenger = passengers_df[['id','seats_requested']].rename(columns={'id':'commute_id'})
    else:
        df_passenger = passengers_df[['id']].copy()
        df_passenger['seats_requested'] = 1
        df_passenger = df_passenger.rename(columns={'id':'commute_id'})

   
    # 8. VALIDACIONES
        
    
        assert df_commutes['origin_lat'].isnull().sum() == 0
        assert df_commutes['origin_lon'].isnull().sum() == 0
        assert df_commutes['dest_lat'].isnull().sum() == 0
        assert df_commutes['dest_lon'].isnull().sum() == 0

        
    # OUTPUT
        
    
    return {
        "users": df_users,
        "locations": df_locations[['lat','lon']],
        "commutes": df_commutes,
        "drivers": df_driver,
        "passengers": df_passenger
    }