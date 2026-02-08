
from FlightRadar24 import FlightRadar24API
import json

fr_api = FlightRadar24API()

# Widen search for testing algorithm
# Approx bounds: north, south, west, east
bounds = "30.5,29.0,-96.0,-94.0"

try:
    print(f"Querying FlightRadar24 for bounds: {bounds}")
    flights = fr_api.get_flights(bounds=bounds)
    
    print(f"Found {len(flights)} aircraft in the wider area.")
    
    helicopters_found = 0
    
    for flight in flights:
        # flight object has specialized methods/attributes.
        # usually aircraft_code (e.g. B738), or 'ground_speed', 'altitude', etc.
        # We need to see if we can get the type description or category.
        
        # FlightRadarAPI usually returns flight objects.
        # attributes: id, icao_24bit, latitude, longitude, heading, altitude, ground_speed, squawk, aircraft_code, registration, time, origin_airport_iata, destination_airport_iata, number, airline_iata, on_ground, vertical_speed, callsign, airline_icao
        
        # Checking details requires a separate call sometimes, but let's see what's in the basic flight object.
        
        # In this library, the flight object might not have 'category'.
        # But 'aircraft_code' (e.g. H135 for Airbus H135) gives a hint.
        # Real categorization might require looking up the aircraft code.
        
        details = fr_api.get_flight_details(flight)
        # This fetching detail for every flight is slow and might get rate limited.
        # Let's just print basic info first for a few.
        
        print(f"Flight: {flight.callsign} ({flight.icao_24bit}), Type: {flight.aircraft_code}, Alt: {flight.altitude}")
        
        # A simple heuristic for helicopters based on code?
        # Or does the library have a helper?
        
        # We can try to get more details for the first one.
        if helicopters_found == 0 and len(flights) > 0:
             print("First flight details:", details)
             
        # Check if type code starts with H (often helicopters like H125, H145) or R (R44, R66) or B (Bell... but could be Boeing).
        # Actually, let's just see what data we get.

except Exception as e:
    print(f"Error: {e}")
