import pandas as pd
import os

def adds_zero_if_needed(x: int) -> str:
    if x < 10: return '0' + str(x)
    return str(x)

def process_frost_days_data(
    read_distant_file: bool = True,
    start_year: int = 2014,
    end_year: int = 2023,
    completion_rate: float = 0.65,
    raw_data_folder: str = "data/raw/",
    processed_data_folder: str = "data/processed",
    code_dept: str = '04',
    filename_start: str = "Q_",
    filename_end: str = "_previous-1950-2023_RR-T-Vent.csv.gz",
    url: str = "https://object.files.data.gouv.fr/meteofrance/data/synchro_ftp/BASE/QUOT/",
    placeholder_year: str = '2000',
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Process frost days data from Meteo France.
    Args:
        read_distant_file (bool): If True, read the file from the URL.
        start_year (int): Start year for the data.
        end_year (int): End year for the data.
        completion_rate (float): Minimum completion rate to keep a station.
        raw_data_folder (str): Path to the folder containing raw data.
        processed_data_folder (str): Path to the folder to save processed data.
        filename (str): Name of the file to process.
        url (str): URL to download the file if not present locally.
        placeholder_year (str): Year to use for the date column in the final DataFrame.
    Returns:
        tuple: A tuple containing the processed DataFrame and the reference DataFrame.
    """
    # Constants
    YEARS_SPAN = end_year - start_year + 1
    FILENAME = f"{filename_start}{code_dept}{filename_end}"
    LOCAL_FILEPATH = os.path.join(raw_data_folder, FILENAME)
    DISTANT_FILEPATH = os.path.join(url, FILENAME)

    # Reading, cleaning and parsing the data
    d = {
        "NUM_POSTE": "string",
        "NOM_USUEL": "string",
        "LAT": "float",
        "LON": "float",
        "ALTI": "int",
        "AAAAMMJJ": "string",
        "TN": "float",
    }
    
    # Choosing the file to read locally or from the URL
    if read_distant_file: filepath = DISTANT_FILEPATH
    else: filepath = LOCAL_FILEPATH
    
    # Loading the data
    df = pd.read_csv(
        filepath,
        sep=";",
        dtype=d,
        usecols=d.keys(),
        parse_dates=["AAAAMMJJ"],
    )

    ## Cleaning the data
    
    # Fixing the NUM_POSTE column
    df["NUM_POSTE"] = df["NUM_POSTE"].str.strip()
    # Renaming the columns
    df = df.rename(columns={"AAAAMMJJ": "DATE", "TN": "TMIN"})
    # Removing everything before the start year
    df = df.loc[df["DATE"] >= pd.to_datetime(start_year, format="%Y")].dropna()

    # Quality control: Deleting all the stations with less than 65% of the data
    observations_max = df.groupby("NUM_POSTE").size().max()
    threshold = observations_max * completion_rate
    num_poste_to_keep = (
        df.groupby("NUM_POSTE").size().loc[lambda x: x >= threshold].index
    )
    df = df.loc[df["NUM_POSTE"].isin(num_poste_to_keep)]

    # Final DataFrame: Dataframe Generation
    df = (
        df.loc[df["TMIN"] <= 0]
        .groupby(
            [
                df["NUM_POSTE"],
                df["NOM_USUEL"],
                df["LAT"],
                df["LON"],
                df["ALTI"],
                df["DATE"].dt.month,
                df["DATE"].dt.day,
            ]
        )
        .agg({"TMIN": "count"})
    )
    df.index.names = ["NUM_POSTE", "NOM_USUEL", "LAT", "LON", "ALTI", "MONTH", "DAY"]
    df = df.reset_index()
    df = df.rename(columns={"TMIN": "FROST_DAYS"})

    # Adding the "FROST(%)" completion column
    df["FROST(%)"] = round(df["FROST_DAYS"] / YEARS_SPAN * 100, 2)

    # Creating the reference DataFrame
    ref_df = (
        df.groupby(["NUM_POSTE", "NOM_USUEL", "LAT", "LON", "ALTI"])
        .agg({"FROST_DAYS": "sum"})
        .reset_index()
    )
    
    ref_df['FROST_DAYS_MEAN_PER_YEAR'] = (round(ref_df['FROST_DAYS'] / YEARS_SPAN).astype(int))

    # Dropping unnecessary columns from the main DataFrame
    df = df.drop(columns=["NOM_USUEL", "LAT", "LON", "ALTI"])
    
    # Adding the "DATE" column
    df['DATE'] = placeholder_year + '-' + df['MONTH'].apply(adds_zero_if_needed) + '-' + df['DAY'].apply(adds_zero_if_needed)
    df['DATE'] = pd.to_datetime(df['DATE'], format='%Y-%m-%d')
    
    # Complete the date range
    complete_date_range = pd.date_range(start=f"{placeholder_year}-01-01", end=f"{placeholder_year}-12-31", freq='D')
    complete_df = pd.DataFrame({'DATE': complete_date_range})
    
    # Merge with existing data
    df = pd.merge(complete_df, df, on='DATE', how='left')

    # Fill missing values with 0
    df['FROST(%)'] = df['FROST(%)'].fillna(0)
    
    return df, ref_df

# Example usage:
# processed_df, reference_df = process_frost_days_data()
