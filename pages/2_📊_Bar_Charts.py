import streamlit as st
import pandas as pd

st.set_page_config(page_title="Bar Charts", page_icon="📊")

st.markdown("# Frost Days bar Charts 📊")
st.sidebar.header("Bar Charts")
st.write("""Let's visualise the behavior of each station.""")

if "dataframes_dict" in st.session_state:
    dataframes_dict = st.session_state.dataframes_dict

else:
    st.write("No data available. Is the data still loading?")

if "selected_departments" not in st.session_state:
    selected_departments = pd.DataFrame(columns=["code", "nom"])
    st.session_state.selected_departments = selected_departments
st.sidebar.write(st.session_state.selected_departments)


for dept, (df, ref_df) in dataframes_dict.items():

    for index, row in ref_df.iterrows():
        st.write(
            f"""
            Data for station {row['NOM_USUEL']} - {dept} - N°{row['NUM_POSTE']}
            Altitude : {row['ALTI']}m, Mean of frost days per year: {row['FROST_DAYS_MEAN_PER_YEAR']}
            """
        )

        st.bar_chart(data=df.loc[df['NUM_POSTE'] == row['NUM_POSTE']], x="DATE", y="FROST(%)")
        
        # # Create a bar chart
        # st.bar_chart(data=df.loc[df['NUM_POSTE'] == row['NUM_POSTE']], x="DATE", y="FROST(%)")

        # Add a separator
        st.markdown("---")
