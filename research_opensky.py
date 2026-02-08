
import requests
import json

# Widen search for testing algorithm
LAMIN = 29.0
LAMAX = 30.5
LOMIN = -96.0
LOMAX = -94.0

url = f"https://opensky-network.org/api/states/all?lamin={LAMIN}&lomin={LOMIN}&lamax={LAMAX}&lomax={LOMAX}"

try:
    print(f"Querying: {url}")
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()
    
    cities = data.get('states', [])
    if cities:
        print(f"Found {len(cities)} aircraft in the wider area.")
        helicopters_found = 0
        for state in cities:
            # 0: icao24, 1: callsign, ... 17: category
            
            icao24 = state[0]
            callsign = state[1].strip()
            lat = state[6]
            lon = state[5]
            
            category = state[17] if len(state) > 17 else None
            
            print(f"Aircraft: {callsign} ({icao24}), Category: {category}, StateLen: {len(state)}")
            
            if category == 7:
                helicopters_found += 1
                print(f"  -> HELICOPTER FOUND!")
                
        print(f"Total helicopters found in wide area: {helicopters_found}")
    else:
        print("No aircraft found in the area.")
        
except requests.exceptions.RequestException as e:
    print(f"Error fetching data: {e}")
except json.JSONDecodeError:
    print("Error decoding JSON")
