import streamlit as st
import folium
from streamlit_folium import folium_static
import requests
import time
import math
import urllib.parse

# Constants
TRUCK_TRANSPORT_DATA = {
    "Truck (>32t)": {
        "co2": 0.679,  # kg CO2 per km
        "description": "Heavy goods vehicle, gross weight over 32 tonnes"
    },
    "Truck (16-32t)": {
        "co2": 0.486,
        "description": "Heavy goods vehicle, gross weight 16-32 tonnes"
    },
    "Truck (7.5-16t)": {
        "co2": 0.368,
        "description": "Medium goods vehicle, gross weight 7.5-16 tonnes"
    },
    "Van (<3.5t)": {
        "co2": 0.298,
        "description": "Light commercial vehicle, gross weight up to 3.5 tonnes"
    }
}

# Maritime transport CO2 emissions (kg CO2 per tonne-km)
MARITIME_CO2 = 0.015  # Average for container ships

FACILITIES = {
    "Powerpipe AB": {
        "address": "Ellesbovägen 101, 42565 Kärra, Sweden",
        "description": "Production facility in Sweden"
    },
    "Kingspan LOGSTOR": {
        "address": "Danmarksvej 11, 9670 Løgstør, Denmark",
        "description": "Production facility in Denmark"
    }
}

# Helper Functions
def get_coordinates(location):
    encoded_location = urllib.parse.quote(location)
    url = f"https://nominatim.openstreetmap.org/search?q={encoded_location}&format=json"
    headers = {'User-Agent': 'EPD_Maps_App/1.0', 'Accept': 'application/json'}
    try:
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
    url = f"http://router.project-osrm.org/route/v1/driving/{start_coords[1]},{start_coords[0]};{end_coords[1]},{end_coords[0]}?overview=full&geometries=geojson"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            route_data = data['routes'][0]
            return {
                'coordinates': route_data['geometry']['coordinates'],
                'distance': route_data['distance'] / 1000  # km
            }
        else:
            st.error(f"Error fetching route. Status code: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error processing route: {str(e)}")
        return None

def calculate_boat_distance(start_coords, end_coords):
    R = 6371
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
    return {
        'coordinates': [start_coords, end_coords],
        'distance': calculate_boat_distance(start_coords, end_coords)
    }

def show():
    st.title("Transport CO2 Calculator")

    # Start location: facility dropdown or custom
    facility_names = list(FACILITIES.keys())
    use_facility = st.checkbox("Start from facility?", value=True)
    if use_facility:
        selected_facility = st.selectbox("Starting Facility", facility_names)
        start_location = FACILITIES[selected_facility]['address']
    else:
        start_location = st.text_input("Enter starting location:", value="Ellesbovägen 101, 425 65 Hisings Kärra, Gothenburg, Sweden")

    destination = st.text_input("Enter destination:")

    # Transport mode and cargo
    transport_mode = st.selectbox("Road Vehicle Type", list(TRUCK_TRANSPORT_DATA.keys()))
    cargo_weight = st.number_input("Cargo Weight (tonnes)", min_value=0.1, max_value=100.0, value=20.0)

    # Boat option
    use_boat = st.checkbox("Use boat transport")
    port1_location = port2_location = None
    if use_boat:
        port1_location = st.text_input("Enter departure port (e.g., Gothenburg Port):")
        port2_location = st.text_input("Enter arrival port (e.g., Rotterdam Port):")

    calculate_button = st.button("Calculate Route & Emissions", use_container_width=True)

    if start_location and destination and calculate_button:
        with st.spinner('Geocoding locations...'):
            start_coords = get_coordinates(start_location)
            end_coords = get_coordinates(destination)
            port1_coords = port2_coords = None
            if use_boat and port1_location and port2_location:
                port1_coords = get_coordinates(port1_location)
                port2_coords = get_coordinates(port2_location)

        if start_coords and end_coords and (not use_boat or (port1_coords and port2_coords)):
            # Center map
            center_lat = (start_coords[0] + end_coords[0]) / 2
            center_lon = (start_coords[1] + end_coords[1]) / 2
            m = folium.Map(location=[center_lat, center_lon], zoom_start=6)
            # Markers
            folium.Marker(start_coords, popup=start_location, icon=folium.Icon(color='green')).add_to(m)
            folium.Marker(end_coords, popup=destination, icon=folium.Icon(color='red')).add_to(m)
            total_distance = 0
            total_co2 = 0
            details = []
            # Multi-modal
            if use_boat and port1_coords and port2_coords:
                folium.Marker(port1_coords, popup=f"Departure Port: {port1_location}", icon=folium.Icon(color='blue', icon='anchor')).add_to(m)
                folium.Marker(port2_coords, popup=f"Arrival Port: {port2_location}", icon=folium.Icon(color='blue', icon='anchor')).add_to(m)
                # Car to port
                first_leg = get_route(start_coords, port1_coords)
                if first_leg:
                    route_coords = [[coord[1], coord[0]] for coord in first_leg['coordinates']]
                    folium.PolyLine(route_coords, weight=2, color='blue', opacity=0.8, dash_array='5').add_to(m)
                    total_distance += first_leg['distance']
                    co2 = first_leg['distance'] * TRUCK_TRANSPORT_DATA[transport_mode]['co2'] * cargo_weight
                    total_co2 += co2
                    details.append(("Car to port", first_leg['distance'], co2))
                # Boat leg
                boat_leg = get_boat_route(port1_coords, port2_coords)
                if boat_leg:
                    route_coords = [[coord[1], coord[0]] for coord in boat_leg['coordinates']]
                    folium.PolyLine(route_coords, weight=2, color='red', opacity=0.8, dash_array='10').add_to(m)
                    total_distance += boat_leg['distance']
                    co2 = boat_leg['distance'] * MARITIME_CO2 * cargo_weight
                    total_co2 += co2
                    details.append(("Boat leg", boat_leg['distance'], co2))
                # Car from port
                final_leg = get_route(port2_coords, end_coords)
                if final_leg:
                    route_coords = [[coord[1], coord[0]] for coord in final_leg['coordinates']]
                    folium.PolyLine(route_coords, weight=2, color='blue', opacity=0.8, dash_array='5').add_to(m)
                    total_distance += final_leg['distance']
                    co2 = final_leg['distance'] * TRUCK_TRANSPORT_DATA[transport_mode]['co2'] * cargo_weight
                    total_co2 += co2
                    details.append(("Car from port", final_leg['distance'], co2))
            else:
                # Direct car route
                route_data = get_route(start_coords, end_coords)
                if route_data:
                    route_coords = [[coord[1], coord[0]] for coord in route_data['coordinates']]
                    folium.PolyLine(route_coords, weight=2, color='blue', opacity=0.8).add_to(m)
                    total_distance += route_data['distance']
                    co2 = route_data['distance'] * TRUCK_TRANSPORT_DATA[transport_mode]['co2'] * cargo_weight
                    total_co2 += co2
                    details.append(("Direct car route", route_data['distance'], co2))
            folium_static(m)
            # Results
            st.success(f"Total route distance: {total_distance:.2f} km\nTotal CO2: {total_co2:.1f} kg CO2eq")
            for label, dist, co2 in details:
                st.markdown(f"- **{label}:** {dist:.2f} km, {co2:.1f} kg CO2eq")
        else:
            st.error("Could not find all required locations. Please check the addresses and try again.")

    # Instructions
    with st.expander("Help & Information"):
        st.markdown("""
        ### How to use the Transport Calculator
        1. Select your starting facility or enter a custom address
        2. Enter the destination address
        3. Choose the road vehicle type and cargo weight
        4. (Optional) Add a boat leg by entering departure and arrival ports
        5. Click 'Calculate Route & Emissions' to see the results
        6. The map will show all route legs and markers
        7. Results include total and per-leg distances and CO2
        """)