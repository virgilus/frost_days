import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static, st_folium

st.set_page_config(page_title="Mapping Demo", page_icon="🌍")

st.markdown("# Frost Days Mapping Demo 🌍")
st.sidebar.header("Frost Days Mapping Demo")
st.write(
    """Here is a simple Streamlit app to visualize frost days in France.""")
    
# if 'ref_df' in st.session_state:
#     ref_df = st.session_state.ref_df

if 'dataframes_dict' in st.session_state:
    dataframes_dict = st.session_state.dataframes_dict
    
    if dataframes_dict:
    
        # Compute average lon and lat for the map
        sum_lat = 0
        sum_lon = 0
        count = 0
        for dept, (df, ref_df) in dataframes_dict.items():
            sum_lat += ref_df['LAT'].sum()
            sum_lon += ref_df['LON'].sum()
            count += len(ref_df)
            
        if count > 0:
            avg_lon = sum_lon / count
            avg_lat = sum_lat / count
        else:
            avg_lat = 45
            avg_lon = 2
        
        # Create a map centered on the average location
        m = folium.Map(location=[avg_lat, avg_lon], zoom_start=6)
        
        for dept, (df, ref_df) in dataframes_dict.items():
            # st.write(f"Data for department {dept}:")

            for index, row in ref_df.iterrows():
                folium.Marker(
                    location=[row['LAT'], row['LON']],
                    popup=f"{row['NOM_USUEL']} - {row['FROST_DAYS_MEAN_PER_YEAR']}",
                    icon=folium.Icon(color='blue', icon='info-sign')
                ).add_to(m)
                
            
        st_folium(m, width=700, height=500)
        
    else: st.write("No data available. Is the data still loading?")
else: st.write("No data available. Please load the data first.")

if 'selected_departments' not in st.session_state:
    selected_departments = pd.DataFrame(columns=["code", "nom"])
    st.session_state.selected_departments = selected_departments
st.sidebar.write(st.session_state.selected_departments)

#st.write("latitude et longitude moyennes", avg_lat, avg_lon)

# What's in the session state?
# st.write(st.session_state)