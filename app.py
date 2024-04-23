import streamlit as st
import pandas as pd

# Define function to remove specified columns
def remove_columns(df, columns_to_remove):
    return df.drop(columns=[col for col in columns_to_remove if col in df.columns], inplace=False)

# Define function to clean owner names
def last_first_clean(df, column_name, order, extra_clean):
    if extra_clean:
        df[column_name] = df[column_name].str.replace(',', '')
        df[column_name] = df[column_name].str.replace(r' \S ', ' ', regex=True)

    if order == "Last First":
        df[['Last_Name', 'First_Name']] = df[column_name].str.split(' ', n=1, expand=True)
        df['First_Name'] = df['First_Name'].str.split(' ').str[0]
    elif order == "First Last":
        df[['First_Name', 'Last_Name']] = df[column_name].str.split(' ', n=1, expand=True)
        df['Last_Name'] = df['Last_Name'].str.split(' ').str[0]

    df.drop(column_name, axis=1, inplace=True)
    return df

# Define function to split address into components
def split_address(df, column_name):
    address_components = df[column_name].apply(lambda x: pd.Series(split_address_helper(x)))
    address_components.columns = ['Address', 'City', 'State', 'Zip']
    df[column_name] = address_components['Address']
    return pd.concat([df, address_components[['City', 'State', 'Zip']]], axis=1)

def split_address_helper(address):
    parts = address.split()
    zip_code = parts[-1]
    state = parts[-2]
    city = parts[-3]
    address = ' '.join(parts[:-3])
    return address, city, state, zip_code

st.title('Data Processing Tool')

uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write("Uploaded Data:")
    st.dataframe(df)  # This will display the full DataFrame in the app

    # Checkboxes for selecting operations
    clean_names = st.checkbox('Clean names by splitting them into First and Last names')
    remove_cols = st.checkbox('Remove columns')
    clean_addresses = st.checkbox('Clean addresses')

    # Collect additional options based on prior selections using session_state
    if clean_names:
        column_to_process = st.selectbox('Select column to split into First Name and Last Name', df.columns)
        extra_clean = st.checkbox('Remove commas and 1 charachter long strings from the selected column')
        name_order = st.radio("Select name order in the column", ('Last First', 'First Last'))
        st.session_state.name_settings = (column_to_process, name_order, extra_clean)

    if remove_cols:
        columns_to_remove = st.multiselect('Select columns to remove', df.columns)
        st.session_state.remove_settings = columns_to_remove

    if clean_addresses:
        address_column = st.selectbox('Select the address column to clean', df.columns)
        st.session_state.address_settings = address_column

    if st.button('Process Data'):
        # Execute data processing if settings are stored in session_state
        if clean_names and 'name_settings' in st.session_state:
            df = last_first_clean(df, *st.session_state.name_settings)
        if remove_cols and 'remove_settings' in st.session_state:
            df = remove_columns(df, st.session_state.remove_settings)
        if clean_addresses and 'address_settings' in st.session_state:
            df = split_address(df, st.session_state.address_settings)

        st.write('Processed Data:', df)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download processed data", csv, "processed_data.csv", "text/csv", key='download-csv')
