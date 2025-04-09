import streamlit as st
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from shapely.geometry import Point
import folium
from folium.plugins import MarkerCluster

# Load datasets
@st.cache
def load_datasets():
    # Assuming CSV format for the databases
    db1 = pd.read_csv("station.csv")  # Database for Part 1
    db2 = pd.read_csv("narrowresult.csv")  # Database for Part 2
    return db1, db2

# Function to create the map
def create_map(filtered_data):
    m = folium.Map(location=[filtered_data['latitude'].mean(), filtered_data['longitude'].mean()], zoom_start=6)
    marker_cluster = MarkerCluster().add_to(m)

    for idx, row in filtered_data.iterrows():
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=f"Station: {row['station_name']}\nContaminant: {row['contaminant']}\nValue: {row['value']}\nDate: {row['date']}"
        ).add_to(marker_cluster)
    return m

# Trend plot function
def plot_trend(filtered_data, contaminant):
    filtered_data['date'] = pd.to_datetime(filtered_data['date'])
    trend_data = filtered_data.groupby('date')['value'].mean().reset_index()

    fig, ax = plt.subplots()
    ax.plot(trend_data['date'], trend_data['value'], label=f'{contaminant} Trend', color='b')
    ax.set_xlabel('Date')
    ax.set_ylabel(f'{contaminant} Concentration')
    ax.set_title(f'Trend of {contaminant} Over Time')
    ax.legend()
    st.pyplot(fig)

# Main Streamlit App
def main():
    st.title("Contaminant Search in Water Quality Data")

    # Upload databases
    db1, db2 = load_datasets()
    
    # Combine the two datasets for easy searching
    combined_data = pd.concat([db1, db2], ignore_index=True)

    # Contaminant selection
    contaminants = combined_data['contaminant'].unique()
    selected_contaminant = st.selectbox("Select Contaminant", contaminants)

    # Date range selection
    min_date = pd.to_datetime(combined_data['date'].min())
    max_date = pd.to_datetime(combined_data['date'].max())
    start_date, end_date = st.date_input("Select Date Range", [min_date, max_date])

    # Value range selection
    min_value = combined_data['value'].min()
    max_value = combined_data['value'].max()
    value_range = st.slider("Select Value Range", min_value, max_value, (min_value, max_value))

    # Filter data based on user inputs
    filtered_data = combined_data[
        (combined_data['contaminant'] == selected_contaminant) &
        (combined_data['date'] >= start_date) &
        (combined_data['date'] <= end_date) &
        (combined_data['value'] >= value_range[0]) &
        (combined_data['value'] <= value_range[1])
    ]
    
    # Display the filtered data
    st.write(f"Showing data for {selected_contaminant} between {start_date} and {end_date}")
    st.write(f"Filtered data count: {filtered_data.shape[0]}")

    # Show the map
    if filtered_data.shape[0] > 0:
        st.subheader("Map of Stations with Selected Contaminant")
        map_ = create_map(filtered_data)
        st.components.v1.html(map_._repr_html_(), height=600)

        # Show the trend over time
        st.subheader("Trend Over Time")
        plot_trend(filtered_data, selected_contaminant)
    else:
        st.write("No data available for the selected filters")

if __name__ == "__main__":
    main()

