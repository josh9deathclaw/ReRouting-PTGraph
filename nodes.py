import pandas as pd
import sys
sys.path.append('scripts')
from utils.geo import is_in_melbourne

PROCESSED_DIR = "data/processed/"

# POC BOUNDARIES
LAT_MIN = -37.850
LAT_MAX = -37.800
LON_MIN = 145.000
LON_MAX = 145.070

def is_in_poc_area(lat, lon):
    """Check if coordinates are in POC area"""
    return (LAT_MIN <= lat <= LAT_MAX and LON_MIN <= lon <= LON_MAX)

def process_stops():
    print("Processing stops...")
    
    # Load raw stops
    stops = pd.read_csv(f'{PROCESSED_DIR}/stops_raw.csv')
    print(f"  Loaded {len(stops)} raw stops (all Melbourne)")
    
    # Remove invalid coordinates
    stops = stops[
        (stops['stop_lat'] != 0) & 
        (stops['stop_lon'] != 0) &
        (stops['stop_lat'].notna()) &
        (stops['stop_lon'].notna())
    ]
    
    # Filter to POC area
    print(f"\n  Filtering to POC area...")
    print(f"  Bounds: Lat {LAT_MIN} to {LAT_MAX}, Lon {LON_MIN} to {LON_MAX}")
    
    stops['in_poc'] = stops.apply(
        lambda row: is_in_poc_area(row['stop_lat'], row['stop_lon']),
        axis=1
    )
    
    stops = stops[stops['in_poc']].copy()
    print(f"  ✓ {len(stops)} stops in POC area")
    
    # Keep both regular stops AND parent stations
    stops = stops[
        (stops['location_type'].isna()) | 
        (stops['location_type'] == 0) |
        (stops['location_type'] == 1)  
    ]
    print(f"  {len(stops)} after filtering location_type")
    
    # ===== CHANGED: ASSIGN STATION_ID DIFFERENTLY =====
    # For bus stops: station_id = stop_id (buses don't have parent stations)
    # For train/tram: Use parent_station if it exists
    
    stops['station_id'] = stops.apply(
        lambda row: (
            row['stop_id'] if row['location_type'] == 1  # Parent station
            else (
                row['parent_station'] if pd.notna(row['parent_station'])  # Has parent (train/tram platform)
                else row['stop_id']  # No parent (bus stop)
            )
        ),
        axis=1
    )
    # ===== END CHANGE =====
    
    # Create mapping: ALL stop_ids → station_id
    stop_to_station_map = stops[['stop_id', 'station_id']].copy()
    
    # For parent stations, also map them to themselves
    parent_stations = stops[stops['location_type'] == 1][['stop_id']].copy()
    parent_stations['station_id'] = parent_stations['stop_id']
    stop_to_station_map = pd.concat([stop_to_station_map, parent_stations], ignore_index=True)
    
    # Remove duplicates
    stop_to_station_map = stop_to_station_map.drop_duplicates(subset=['stop_id'], keep='first')
    
    # ===== CHANGED: DON'T GROUP FOR STATIONS =====
    # Create unique stations - NO grouping for bus stops
    # Each stop_id becomes a station_id (buses need individual stops)
    stations = stops[['station_id', 'stop_name', 'stop_lat', 'stop_lon']].copy()
    stations = stations.drop_duplicates(subset=['station_id'], keep='first')
    # ===== END CHANGE =====
    
    print(f"\n  ✓ Created {len(stations)} unique stations")
    print(f"  ✓ Created {len(stop_to_station_map)} stop→station mappings")
    
    # Show sample stations
    print(f"\n  Sample stations in POC area:")
    for i in range(min(10, len(stations))):
        station = stations.iloc[i]
        print(f"    - {station['stop_name']}")
    
    # Save
    stations.to_csv(f'{PROCESSED_DIR}/stops_cleaned.csv', index=False)
    stop_to_station_map.to_csv(f'{PROCESSED_DIR}/stop_to_station_map.csv', index=False)
    
    print(f"\n  ✓ Saved to stops_cleaned.csv and stop_to_station_map.csv")
    
    return stations, stop_to_station_map

if __name__ == "__main__":
    process_stops()