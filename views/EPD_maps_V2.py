import streamlit as st
import folium
from folium import plugins
import requests
from streamlit_folium import folium_static
import time
import urllib.parse
import math

def get_coordinates(location):
    # Using Nominatim API for geocoding (free)
    # URL encode the location string
    encoded_location = urllib.parse.quote(location)
    url = f"https://nominatim.openstreetmap.org/search?q={encoded_location}&format=json"
    
    # Required headers for Nominatim API
    headers = {
        'User-Agent': 'EPD_Maps_App/1.0',
        'Accept': 'application/json'
    }
    
    try:
        # Add a small delay to respect rate limiting
        time.sleep(1)
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            if data:
                return float(data[0]['lat']), float(data[0]['lon'])
            else:
                st.warning(f"No results found for location: {location}")
                return None
        elif response.status_code == 403:
            st.error("Access denied. Please try again in a few moments.")
            return None
        else:
            st.error(f"Error fetching coordinates for {location}. Status code: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error processing location {location}: {str(e)}")
        return None

def get_route(start_coords, end_coords):
    # Using OSRM API for routing (free)
    url = f"http://router.project-osrm.org/route/v1/driving/{start_coords[1]},{start_coords[0]};{end_coords[1]},{end_coords[0]}?overview=full&geometries=geojson"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            # Extract both the route coordinates and distance
            route_data = data['routes'][0]
            return {
                'coordinates': route_data['geometry']['coordinates'],
                'distance': route_data['distance'] / 1000  # Convert meters to kilometers
            }
        else:
            st.error(f"Error fetching route. Status code: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error processing route: {str(e)}")
        return None

def calculate_boat_distance(start_coords, end_coords):
    # Calculate great circle distance for boat route
    R = 6371  # Earth's radius in kilometers
    
    lat1, lon1 = start_coords
    lat2, lon2 = end_coords
    
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    distance = R * c
    return distance

def get_boat_route(start_coords, end_coords):
    # Create a simple straight line for boat route
    # In a real application, you would use a maritime routing service
    return {
        'coordinates': [start_coords, end_coords],
        'distance': calculate_boat_distance(start_coords, end_coords)
    }

# Set up the Streamlit page
st.title("Multi-Modal Route Planning Dashboard")
st.write("Plan routes with car and boat transportation options")

# Set default start location
default_start = "Ellesbovägen 101, 425 65 Hisings Kärra, Gothenburg, Sweden"

# Get user input
start_location = st.text_input("Enter starting location:", value=default_start)
end_location = st.text_input("Enter destination:")

# Add option for boat transport
use_boat = st.checkbox("Use boat transport")
port1_location = None
port2_location = None
if use_boat:
    port1_location = st.text_input("Enter departure port (e.g., Gothenburg Port):")
    port2_location = st.text_input("Enter arrival port (e.g., Rotterdam Port):")

if start_location and end_location:
    # Get coordinates for all locations
    with st.spinner('Searching for locations...'):
        start_coords = get_coordinates(start_location)
        end_coords = get_coordinates(end_location)
        
        # Only get port coordinates if boat transport is selected and both ports are entered
        port1_coords = None
        port2_coords = None
        if use_boat and port1_location and port2_location:
            port1_coords = get_coordinates(port1_location)
            port2_coords = get_coordinates(port2_location)
    
    if start_coords and end_coords:
        # Create a map centered between the points
        center_lat = (start_coords[0] + end_coords[0]) / 2
        center_lon = (start_coords[1] + end_coords[1]) / 2
        m = folium.Map(location=[center_lat, center_lon], zoom_start=10)
        
        # Add markers for start and end points
        folium.Marker(
            start_coords,
            popup=start_location,
            icon=folium.Icon(color='green')
        ).add_to(m)
        
        folium.Marker(
            end_coords,
            popup=end_location,
            icon=folium.Icon(color='red')
        ).add_to(m)
        
        total_distance = 0
        
        # Only proceed with boat route if we have all necessary coordinates
        if use_boat and port1_coords and port2_coords:
            # Add port markers
            folium.Marker(
                port1_coords,
                popup=f"Departure Port: {port1_location}",
                icon=folium.Icon(color='blue', icon='anchor')
            ).add_to(m)
            
            folium.Marker(
                port2_coords,
                popup=f"Arrival Port: {port2_location}",
                icon=folium.Icon(color='blue', icon='anchor')
            ).add_to(m)
            
            # Calculate first leg (car to first port)
            with st.spinner('Calculating first leg of the route...'):
                first_leg = get_route(start_coords, port1_coords)
                if first_leg:
                    route_coords = [[coord[1], coord[0]] for coord in first_leg['coordinates']]
                    folium.PolyLine(
                        route_coords,
                        weight=2,
                        color='blue',
                        opacity=0.8,
                        dash_array='5'
                    ).add_to(m)
                    total_distance += first_leg['distance']
            
            # Calculate boat leg
            with st.spinner('Calculating boat route...'):
                boat_leg = get_boat_route(port1_coords, port2_coords)
                if boat_leg:
                    route_coords = [[coord[1], coord[0]] for coord in boat_leg['coordinates']]
                    folium.PolyLine(
                        route_coords,
                        weight=2,
                        color='red',
                        opacity=0.8,
                        dash_array='10'
                    ).add_to(m)
                    total_distance += boat_leg['distance']
            
            # Calculate final leg (car from second port)
            with st.spinner('Calculating final leg of the route...'):
                final_leg = get_route(port2_coords, end_coords)
                if final_leg:
                    route_coords = [[coord[1], coord[0]] for coord in final_leg['coordinates']]
                    folium.PolyLine(
                        route_coords,
                        weight=2,
                        color='blue',
                        opacity=0.8,
                        dash_array='5'
                    ).add_to(m)
                    total_distance += final_leg['distance']
            
            # Display the map
            folium_static(m)
            
            # Display the distances
            if first_leg and boat_leg and final_leg:
                st.success(f"""
                Total route distance: {total_distance:.2f} kilometers
                - First leg (car to port): {first_leg['distance']:.2f} km
                - Boat leg: {boat_leg['distance']:.2f} km
                - Final leg (car from port): {final_leg['distance']:.2f} km
                """)
        else:
            # Calculate direct route
            with st.spinner('Calculating route...'):
                route_data = get_route(start_coords, end_coords)
            
            if route_data:
                route_coords = [[coord[1], coord[0]] for coord in route_data['coordinates']]
                folium.PolyLine(
                    route_coords,
                    weight=2,
                    color='blue',
                    opacity=0.8
                ).add_to(m)
                
                # Display the map
                folium_static(m)
                
                # Display the distance
                st.success(f"Total route distance: {route_data['distance']:.2f} kilometers")
            else:
                st.error("Could not generate route between the locations. Please try different locations.")
    else:
        st.error("Could not find one or both locations. Please check the addresses and try again.")

# Add instructions
st.markdown("""
### How to use:
1. The starting location is pre-filled with Powerpipe AB factory address
2. Enter your destination location
3. Check the "Use boat transport" box if you want to include a boat transport leg
4. If using boat transport, enter:
   - Departure port (e.g., "Gothenburg Port, Sweden")
   - Arrival port (e.g., "Rotterdam Port, Netherlands")
5. The map will show:
   - Green marker: Starting point
   - Blue anchor markers: Ports
   - Red marker: Destination
   - Blue dashed line: Car routes
   - Red dashed line: Boat route
6. The total route distance will be displayed in kilometers, broken down by leg

### Tips for entering locations:
- Use specific addresses or well-known places
- Include city and country for better results
- Try using postal codes or landmarks
- Avoid abbreviations unless they're widely recognized
- For Swedish addresses, try using the format: "Street Name, City, Sweden"
- For ports/harbors, include "port" or "harbor" in the name and the country
""")