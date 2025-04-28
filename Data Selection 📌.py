import streamlit as st
from frost_days_functions import *


dept_df = (
    pd.read_csv("data/references/departements-france.csv")
    .rename(
        columns={
            "code_departement": "code",
            "nom_departement": "nom",
        }
    )
    .drop(columns=["code_region", "nom_region"])
)


st.set_page_config(
    page_title="Introduction",
    page_icon="❄️",
)

st.write("# Welcome to the Frost Days Dashboard ❄️")

st.markdown(
    """
    This is a simple Streamlit app to visualize frost days in several departments in France.
"""
)

if "dataframes_dict" not in st.session_state:
    # st.sidebar.write("Initializing dataframes_dict...")
    dataframes_dict = {}
    st.session_state.dataframes_dict = dataframes_dict
    # st.sidebar.write("Done !")
    # st.sidebar.write(st.session_state)
    
# if "selected_departments" not in st.session_state:
#     selected_departments = pd.DataFrame(columns=["code", "nom"])
#     st.session_state.selected_departments = selected_departments

# Placeholder for selected departments
selected_placeholder = st.sidebar.empty()
status_placeholder = st.sidebar.empty()

if 'selected_departments' not in st.session_state:
    selected_departments = pd.DataFrame(columns=["code", "nom"])
    st.session_state.selected_departments = selected_departments
# selected_placeholder.write(st.session_state.selected_departments)

# Function to be launched when the button is clicked

def load_data(
    selected_departments,
    dataframes_dict=st.session_state.dataframes_dict,
    status_placeholder=status_placeholder,
):
    if not selected_departments.empty:
        dept_list = selected_departments["code"].tolist()
        for code_dept in dept_list:
            if code_dept not in dataframes_dict:
                status_placeholder.write(f"Loading data for department {code_dept}...")
                dataframes_dict[code_dept] = process_frost_days_data(
                    code_dept=code_dept, read_distant_file=True
                )
                # st.sidebar.write(
                #     "shape for dept",
                #     code_dept,
                #     ":",
                #     dataframes_dict[code_dept][0].shape,
                #     dataframes_dict[code_dept][1].shape,
                # )
            else:
                status_placeholder.write(f"Data for department {code_dept} already loaded.")

        # dataframes_dict = modify_dataframe_dict(dataframes_dict, dept_list)
        # st.sidebar.write("List of departments:", dept_list)
        # st.sidebar.write("keys of dataframes_dict", dataframes_dict.keys())
        status_placeholder.success("Data loaded successfully!", icon="✅")


# Add a checkbox column to the dataframe
dept_df["Select"] = False


# Button at the top
if st.button("Load Data"):
    load_data_triggered = True  # Use a flag to indicate the button was clicked
else:
    load_data_triggered = False

# Display the dataframe with checkboxes
edited_df = st.data_editor(
    dept_df,
    column_config={"Select": st.column_config.CheckboxColumn(required=True)},
    disabled=["code", "nom"],
    hide_index=True,
)

# Retrieve the selected departments
selected_departments = edited_df[edited_df["Select"]]
st.session_state.selected_departments = selected_departments.drop(columns=["Select"])

# # Update the placeholder with selected departments
# with selected_placeholder.container():
#     if not selected_departments.empty:
#         st.write("Selected Departments:")
#         st.write(selected_departments[["code", "nom"]])
#     else:
#         st.write("No departments selected.")

# Update the placeholder with selected departments
with selected_placeholder.container():
    st.write("Selected Departments:")
    if not st.session_state.selected_departments.empty:
        st.write(st.session_state.selected_departments[["code", "nom"]])
    else:
        st.write("No departments selected.")
        

# Trigger load_data only if the button was clicked
if load_data_triggered:
    dataframes_dict = load_data(selected_departments)


# st.write(selected_departments["code_departement"].tolist())
# st.write(selected_departments["code_departement"].tolist()[0])
# st.dataframe(ref_df)

# st.dataframe(df)
