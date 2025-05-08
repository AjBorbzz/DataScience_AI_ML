import streamlit as st
import pandas as pd
import pydeck as pdk


city_info_dict = {
    "Quezon City": {
        "image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRUIzpEZsoUYNiB87O7zCVyCcQ1Jbm2aoDpxw&s",
        "fact": "Quezon City is the most populous city in the Philippines and was the former capital."
    },
    "Manila": {
        "image": "https://upload.wikimedia.org/wikipedia/commons/8/8e/Manila_skyline.jpg",
        "fact": "Manila is the capital of the Philippines and one of the oldest cities in Asia."
    },
    "Cebu City": {
        "image": "https://upload.wikimedia.org/wikipedia/commons/8/85/Cebu_City_Skyline.jpg",
        "fact": "Cebu City is known as the 'Queen City of the South' and is one of the oldest cities in the country."
    },
    "Davao City": {
        "image": "https://upload.wikimedia.org/wikipedia/commons/d/db/Davao_City_skyline.jpg",
        "fact": "Davao City is the largest city by land area in the Philippines."
    },
    # Add more cities as needed
}


# Sample data of regions and their cities with coordinates
region_city_data = {
    "NCR (Metro Manila)": {
        "Quezon City": {"lat": 14.6760, "lon": 121.0437, "zoom": 12},
        "Manila": {"lat": 14.5995, "lon": 120.9842, "zoom": 13},
        "Makati": {"lat": 14.5547, "lon": 121.0244, "zoom": 13},
    },
    "Central Visayas": {
        "Cebu City": {"lat": 10.3157, "lon": 123.8854, "zoom": 12},
        "Lapu-Lapu City": {"lat": 10.3103, "lon": 123.9492, "zoom": 12},
        "Dumaguete": {"lat": 9.3075, "lon": 123.3054, "zoom": 12},
    },
    "Davao Region": {
        "Davao City": {"lat": 7.1907, "lon": 125.4553, "zoom": 12},
        "Tagum City": {"lat": 7.4474, "lon": 125.8045, "zoom": 12},
    },
    "Ilocos Region": {
        "Laoag City": {"lat": 18.1960, "lon": 120.5920, "zoom": 12},
        "Vigan": {"lat": 17.5747, "lon": 120.3869, "zoom": 12},
    }
}

# Sidebar layout
st.sidebar.title("🗺️ Explore the Philippines by Region")

# Region selection
selected_region = st.sidebar.selectbox("Select a region:", list(region_city_data.keys()))

# City selection based on region
selected_city = st.sidebar.selectbox("Select a city:", list(region_city_data[selected_region].keys()))

# Extract selected city data
city_data = region_city_data[selected_region][selected_city]

# Title
st.title("🇵🇭 Philippine Region and City Map Explorer")
st.write(f"**Region:** {selected_region}")
st.write(f"**City:** {selected_city}")

# Pydeck map layer
layer = pdk.Layer(
    "ScatterplotLayer",
    data=pd.DataFrame([{"lat": city_data["lat"], "lon": city_data["lon"]}]),
    get_position='[lon, lat]',
    get_radius=8000,
    get_fill_color=[0, 128, 255],
    pickable=True,
)

# Render map
st.pydeck_chart(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state=pdk.ViewState(
        latitude=city_data["lat"],
        longitude=city_data["lon"],
        zoom=city_data["zoom"],
        pitch=30,
    ),
    layers=[layer],
))

if selected_city in city_info_dict:
    city_data = city_info_dict[selected_city]
    st.markdown(f"### 🏙️ {selected_city}")
    st.image(city_data["image"], use_container_width=True)
    st.info(f"📌 {city_data['fact']}")
else:
    st.warning("No image or fact available for this city yet.")
