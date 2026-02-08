
import math

def get_bounds(lat, lon, radius_miles):
    """
    Calculate the bounding box for a given lat/lon and radius in miles.
    Returns a string "ymax,ymin,xmin,xmax" formatted for FlightRadarAPI.
    Note: 1 degree of latitude ~= 69 miles.
    1 degree of longitude ~= 69 miles * cos(lat).
    """
    lat_change = radius_miles / 69.0
    lon_change = radius_miles / (69.0 * math.cos(math.radians(lat)))

    ymax = lat + lat_change
    ymin = lat - lat_change
    xmax = lon + lon_change
    xmin = lon - lon_change

    # Format: "ymax,ymin,xmin,xmax" (North, South, West, East)
    # FlightRadarAPI expects this string format for bounds
    return f"{ymax},{ymin},{xmin},{xmax}"

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance in miles between two points 
    on the earth (specified in decimal degrees)
    """
    # Convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])

    # Haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a)) 
    r = 3956 # Radius of earth in miles. Use 6371 for km
    return c * r

def is_helicopter(aircraft_code):
    """
    Check if the aircraft code corresponds to a known helicopter type.
    """
    if not aircraft_code:
        return False
        
    code = aircraft_code.upper()
    
    # Common Helicopter Prefixes/Codes
    # H: H125, H135, H145, H60, etc. (Airbus/Eurocopter)
    # R: R44, R66 (Robinson)
    # B06, B407, B412, B429, B505 (Bell)
    # AS50, AS55, AS65, AS350, AS355 (Eurocopter/Airbus)
    # EC: EC120, EC130, EC135, EC145, EC155, EC225 (Eurocopter/Airbus)
    # S76, S92 (Sikorsky)
    # AW109, AW119, AW139, AW169, AW189 (AgustaWestland/Leonardo)
    # UH: UH60, UH1 (Military util)
    # CH: CH47 (Chinook)
    # MD: MD500, MD520, MD600, MD900
    # G2 (Guimbal Cabri)
    
    # Specific codes that are definitely helicopters
    helicopter_codes = {
        'R44', 'R66', 'R22',
        'B06', 'B407', 'B412', 'B429', 'B505', 'B206', 'B212', 'B214', 'B222', 'B230', 'B430',
        'H500', 'HU50' # Hughes/MD
    }
    
    if code in helicopter_codes:
        return True
        
    # Check prefixes
    if code.startswith(('H1', 'H2', 'EC', 'AS3', 'AS5', 'AW1', 'S76', 'S92', 'UH', 'AH', 'CH', 'MH', 'MD5', 'MD6', 'MD9', 'G2')):
        # Refine H prefix: H can be generic, but H1xx/H2xx is usually Airbus Heli. 
        # CAUTION: 'H' might be used for heavy? No, usually ICAO codes are distinct. 
        # H25B is a jet (HondaJet). So we need to be careful with 'H' prefix.
        if code.startswith('H25'): return False # HondaJet
        return True
        
    return False
