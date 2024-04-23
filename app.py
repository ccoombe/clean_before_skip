import streamlit as st
import pandas as pd

# Function to clean data
def last_first_clean(df, column_name, order, handle_commas):
    if handle_commas and column_name in df.columns:
        df[column_name] = df[column_name].str.replace(',', '')
        
        if order == "Last First":
            df[['Last_Name', 'First_Name']] = df[column_name].str.split(n=1, expand=True)
            df['First_Name'] = df['First_Name'].str.split(' ').str[0]
            
        elif order == "First Last":
            df[['First_Name', 'Last_Name']] = df[column_name].str.split(n=1, expand=True)
            df['Last_Name'] = df['Last_Name'].str.split(' ').str[0]

        # Drop the original column if no longer needed
        df.drop(column_name, axis=1, inplace=True)
        
    return df



# Streamlit user interface
st.title('First & Last Name Split')

# File uploader
uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'])
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    st.write("Preview of the uploaded data:")
    st.dataframe(df.head())

    if df is not None:
        column_to_process = st.selectbox('Select column to split into First Name and Last Name', df.columns)
        
        # Checkbox for user to choose if they want to handle commas
        handle_commas = st.checkbox('Remove commas from the selected column')

        # Radio button for user to specify the name order
        name_order = st.radio("Select name order in the column", ('Last First', 'First Last'))

        if st.button('Process Data'):
            # Process data based on user input
            processed_df = last_first_clean(df, column_to_process, name_order,handle_commas)
            st.write('Processed Data:', processed_df)

            # Optional: Allow user to download the processed data
            csv = processed_df.to_csv(index=False).encode('utf-8')
            st.download_button("Download processed data", csv, "processed_data.csv", "text/csv", key='download-csv')

