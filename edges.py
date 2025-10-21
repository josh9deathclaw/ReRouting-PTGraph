import pandas as pd
import sys
from utils.geo import haversine_distance
from utils.time import parse_gtfs_time, time_diff
from tqdm import tqdm

PROCESSED_DIR = "data/processed/"

def get_mode_from_feed(feed_source, route_type):
    """
    Determine mode from feed source since PTV's route_type is unreliable
    """
    feed_str = str(feed_source).lower()
    
    # Check feed source name
    if 'regional_train' in feed_str or 'metro_train' in feed_str or '_train' in feed_str:
        return 'train'
    elif 'metro_tram' in feed_str or '_tram' in feed_str:
        return 'tram'
    elif 'metro_bus' in feed_str or 'regional_bus' in feed_str or 'skybus' in feed_str or '_bus' in feed_str:
        return 'bus'
    else:
        # Shouldn't reach here, but fallback to route_type
        print(f"Warning: Unknown feed_source '{feed_source}', using route_type={route_type}")
        mode_map = {
            0: 'tram',
            1: 'train',
            2: 'train',
            3: 'bus',  
            4: 'bus',
            6: 'bus',
            11: 'bus'
        }
        return mode_map.get(route_type, 'bus')

def create_edges():
    print("Creating edges...")
    
    # Load data
    print("  Loading stop_times...")
    stop_times = pd.read_csv(f'{PROCESSED_DIR}/stop_times.csv', low_memory=False)
    print("  Loading trips...")
    trips = pd.read_csv(f'{PROCESSED_DIR}/trips.csv')
    print("  Loading routes...")
    routes = pd.read_csv(f'{PROCESSED_DIR}/routes.csv')
    print("  Loading stops...")
    stops = pd.read_csv(f'{PROCESSED_DIR}/stops_cleaned.csv')
    stop_map = pd.read_csv(f'{PROCESSED_DIR}/stop_to_station_map.csv')
    
    print(f"  Loaded {len(stop_times)} stop_times")
    
    # ===== NEW: Get valid POC stations =====
    valid_stations = set(stops['station_id'].astype(str))
    print(f"  Valid POC stations: {len(valid_stations)}")
    # ===== END NEW =====
    
    # Create lookups
    print("  Building lookups...")
    stop_to_station = dict(zip(stop_map['stop_id'].astype(str), stop_map['station_id'].astype(str)))
    
    # Create lookup: stop_id → coords
    stops_raw = pd.read_csv(f'{PROCESSED_DIR}/stops_raw.csv')
    stop_coords = dict(zip(
        stops_raw['stop_id'].astype(str), 
        zip(stops_raw['stop_lat'], stops_raw['stop_lon'])
    ))
    
    # Convert stop_times stop_id to string
    stop_times['stop_id'] = stop_times['stop_id'].astype(str)
    
    # Merge trips with routes
    print("  Merging trips with routes...")
    trips = trips.merge(
        routes[['route_id', 'route_type', 'feed_source']], 
        on='route_id', 
        how='left',
        suffixes=('', '_from_routes')
    )
    
    if 'route_type_from_routes' in trips.columns:
        trips['route_type'] = trips['route_type_from_routes'].fillna(trips['route_type'])
        trips = trips.drop(columns=['route_type_from_routes'])
    
    # Create trip info dictionary
    trip_info_dict = trips.set_index('trip_id').to_dict('index')
    
    edges = []
    skipped = 0
    skipped_reasons = {
        'missing_station': 0,
        'missing_coords': 0,
        'self_loop': 0,
        'bad_time': 0,
        'bad_distance': 0,
        'missing_trip_info': 0,
        'outside_poc': 0  # NEW
    }
    
    # Group by trip
    print("  Processing trips...")
    grouped = stop_times.groupby('trip_id')
    total_trips = len(grouped)
    
    for trip_id, group in tqdm(grouped, total=total_trips, desc="  Creating edges"):
        group = group.sort_values('stop_sequence')
        
        if trip_id not in trip_info_dict:
            skipped += len(group) - 1
            skipped_reasons['missing_trip_info'] += len(group) - 1
            continue
            
        trip_info = trip_info_dict[trip_id]
        route_id = trip_info['route_id']
        route_type = trip_info.get('route_type', 3)
        route_name = trip_info.get('route_short_name', 'Unknown')
        feed_source = trip_info.get('feed_source', '')
        
        mode = get_mode_from_feed(feed_source, route_type)
        
        # Create edges between consecutive stops
        for i in range(len(group) - 1):
            from_stop = str(group.iloc[i]['stop_id'])
            to_stop = str(group.iloc[i+1]['stop_id'])
            
            # Map to station_id
            from_station = stop_to_station.get(from_stop)
            to_station = stop_to_station.get(to_stop)
            
            if not from_station or not to_station:
                skipped += 1
                skipped_reasons['missing_station'] += 1
                continue
            
            # Only skip edge if BOTH stops are outside PoC
            if from_station not in valid_stations and to_station not in valid_stations:
                skipped += 1
                skipped_reasons['outside_poc'] += 1
                continue
            # ===== END CHECK =====
            
            # Skip self-loops
            if from_station == to_station:
                skipped += 1
                skipped_reasons['self_loop'] += 1
                continue
            
            # Get coordinates
            from_coords = stop_coords.get(from_stop)
            to_coords = stop_coords.get(to_stop)
            
            if not from_coords or not to_coords:
                skipped += 1
                skipped_reasons['missing_coords'] += 1
                continue
            
            # Calculate time (seconds)
            dep_time = group.iloc[i]['departure_time']
            arr_time = group.iloc[i+1]['arrival_time']
            travel_time = time_diff(dep_time, arr_time)
            
            if travel_time > 7200 or travel_time <= 0:
                skipped += 1
                skipped_reasons['bad_time'] += 1
                continue
            
            # Calculate distance (meters)
            distance = haversine_distance(
                from_coords[0], from_coords[1],
                to_coords[0], to_coords[1]
            )
            
            if distance <= 0:
                skipped += 1
                skipped_reasons['bad_distance'] += 1
                continue
            
            # Create edge
            edges.append({
                'from_station': from_station,
                'to_station': to_station,
                'route_id': route_id,
                'route_name': route_name,
                'mode': mode,
                'time': travel_time,
                'distance': distance,
                'trip_id': trip_id
            })
    
    print(f"\n  Created {len(edges)} edges (skipped {skipped})")
    print(f"  Skipped breakdown:")
    for reason, count in skipped_reasons.items():
        if count > 0:
            print(f"    - {reason}: {count}")
    
    # Save
    print("  Saving edges...")
    edges_df = pd.DataFrame(edges)
    
    print(f"\n  Mode distribution:")
    print(edges_df['mode'].value_counts())
    
    edges_df.to_csv(f'{PROCESSED_DIR}/edges_raw.csv', index=False)
    print(f"  ✓ Saved to edges_raw.csv")
    
    return edges_df

def merge_edges(edges_df):
    """Merge duplicate edges inline"""
    print("\n  Merging duplicate edges...")
    
    # Sort by trip_id
    edges_df = edges_df.sort_values('trip_id')
    
    # Group by station pairs and keep first
    merged = edges_df.groupby(['from_station', 'to_station']).first().reset_index()
    
    # Drop trip_id
    merged = merged.drop(columns=['trip_id'])
    
    print(f"  ✓ Reduced to {len(merged)} unique edges")
    print(f"  Removed {len(edges_df) - len(merged)} duplicates")
    
    return merged

if __name__ == "__main__":

    edges_df = create_edges()
    edges_merged = merge_edges(edges_df)

    # Save merged
    edges_merged.to_csv(f'{PROCESSED_DIR}/edges_merged.csv', index=False)
    print(f"\n✓ Saved merged edges to edges_merged.csv")
    