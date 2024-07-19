import pandas as pd
import sqlite3
import json
import streamlit as st
import plotly.express as px
import os
import re

def create_dataframe(file, idx, table,config_json_path):
    try:
        with open(config_json_path) as f:
            config = json.load(f)
        name_dict = config['header_mapping'][table]
        if idx == -1:
            df = pd.read_excel(file)
        else:
            df = pd.read_excel(file, sheet_name=idx)

        new_columns = []
        for column in df.columns:
            if column in name_dict:
                new_columns.append(name_dict[column].split(" ")[0])
            else:
                print(f"Warning: Column '{column}' not found in the header mapping for table '{table}'")
                new_columns.append(column)
        df.columns = new_columns  
        return df
    except Exception as e:
        print(f"Error creating DataFrame from file '{file}': {e}")
        st.warning(f"Error creating DataFrame from file '{file}': {e}")
        return None

def table_exists(table_name, connection):
    cursor = connection.cursor()
    try:
        cursor.execute(f"SELECT count(*) FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        count = cursor.fetchone()[0]
        return count > 0
    except Exception as e:
        print("There is a problem with SQLite:", e)
        st.warning("There is a problem with SQLite:", e)
        return False
    finally:
        cursor.close()

def create_table(connection, table_name,config_json_path):
    try:
        with open(config_json_path) as f:
            config = json.load(f)
        name_dict = config['header_mapping'][table_name]
        column_definitions = []
        for key, val in name_dict.items():
            if key != "PRIMARY KEY":
                column_definitions.append(val)
        columns_str = ",\n    ".join(column_definitions)
        cursor = connection.cursor()
        query = f"""
            CREATE TABLE {table_name} (
                {columns_str},
                PRIMARY KEY ({name_dict["PRIMARY KEY"]})
            );
            """
        print(query,"\n\n\n")
        cursor.execute(query)
        print(f"Table {table_name} created sucessfully!")
        st.write(f"Table {table_name} created sucessfully!")
        return True
    except sqlite3.DatabaseError as e:
        print("There is a problem with SQLite:", e)
        st.write("Error creating table in database:",e)
        return False
    finally:
        if cursor:
            cursor.close()

def upsert_batch(table_name, df, connection,config_json_path):
    try:
        with open(config_json_path) as f:
            config = json.load(f)
        primary_keys = config['header_mapping'][table_name]['PRIMARY KEY'].split(",")
        columns = df.columns.tolist()
        cursor = connection.cursor()

        try:
            for _, row in df.iterrows():
                # Convert Timestamps to strings
                row = row.apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S') if isinstance(x, pd.Timestamp) else x)
                
                merge_sql = f"""
                INSERT INTO {table_name} ({', '.join(columns)}) 
                VALUES ({', '.join(['?' for _ in columns])})
                ON CONFLICT({', '.join(primary_keys)}) DO UPDATE SET
                {', '.join([f'{col} = excluded.{col}' for col in columns if col not in primary_keys])}
                """
                cursor.execute(merge_sql, tuple(row))
            connection.commit()
            print("Merge Executed and changes committed!")
            print(f"Sheet {table_name} upserted")
            st.write(f"Sheet {table_name} data inserted/updated")
        except Exception as e:
            connection.rollback()
            print(f"Error during upsert operation: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if cursor:
            cursor.close()

def connect_to_db(config_pth):
    with open(config_pth) as f:
        config = json.load(f)
    creds = config['db_config']
    table_name = creds.get("table_name").split(",")
    batch_size = creds.get("batch_size")
    db_path = creds.get("db_path")
    try:
        connection = sqlite3.connect(db_path)
        print("Connected to database!")
    except Exception as e:
        print(e)
        connection.close()
    return connection, table_name, batch_size

def insert_xls_to_database(file,config_json_path):
    try:
        connection, table_name, batch_size = connect_to_db(config_json_path)
    except Exception as e:
        print(f"Error in database connection: {e}")
        return
    try:
        if len(table_name) == 1:
            df = create_dataframe(file, -1, table_name[0],config_json_path)
            if df is not None:
                if not table_exists(table_name[0], connection):
                    if not create_table(connection, table_name[0],config_json_path):
                        print(f"Table {table_name[0]} does not exist and failed to create.")
                        return
                    else:
                        print(f"Table {table_name[0]} created successfully!")
                        upsert_batch(table_name[0], df, connection,config_json_path)
                else:
                    st.write(f"Table {table_name[0]} already exists, updating table contents!")
                    upsert_batch(table_name[0], df, connection,config_json_path)
            else:
                print("Empty dataframe !")
        # else:    
        #     for i in range(len(table_name)):
        #         df = create_dataframe(file, i, table_name[i])
        #         if df is not None:
        #             if not table_exists(table_name[i], connection):
        #                 if not create_table(connection, table_name[i]):
        #                     print(f"Table {table_name[i]} does not exist and failed to create.")
        #                     return
        #             else:
        #                 st.write(f"Table {table_name[i]}, already exists, updating table contents!")
        #                 upsert_batch(table_name[i], df, connection)
    except Exception as e:
        print(f"Error in inserting data to database: {e}")
    finally:
        if connection:
            connection.close()

def main():
    st.title('EXCEL DATABASE CONNECTION APPLICATION')
    #st.subheader('By Jay Pandya Jul 2024')
    tab_selection = st.radio('Select Action', ['Create configuration file for excel','Create/Update Database','Filter and view Data', 'Display Graphs'])
    st.subheader('If no config file then generate one by selecting: Create configuration file for excel')
    if tab_selection == 'Create configuration file for excel':
        generate_config_file()
    else:
        
        try:
            RELATIVE_PATH = "temp"
            os.makedirs(RELATIVE_PATH, exist_ok=True)
            config_json_file = st.file_uploader("Select Config file for your Excel database", type=['json'])
            if config_json_file is not None:
                config_json_path = os.path.join(RELATIVE_PATH, config_json_file.name)
                with open(config_json_path, "wb") as f:
                    f.write(config_json_file.getbuffer())
                st.success(f"File saved at: {config_json_path}")
            if tab_selection == 'Create/Update Database':
                insert_file_tab(config_json_path)
            elif tab_selection == 'Filter and view Data':
                filter_view_data(config_json_path)
            elif tab_selection == 'Display Graphs':
                display_graphs_tab(config_json_path)
        except Exception as e:
            print(f"Error in uploading config file: {e}")
            st.warning("Please upload config file")
        

def generate_config_file():
    st.subheader('Generate Configuration for your Xls dataset')
    if 'file' not in st.session_state:
        st.session_state['file'] = None

    st.session_state['file'] = st.file_uploader("Upload your Excel file", type=['xlsx'], key="file_uploader")

    if st.session_state['file'] is not None and st.button('Generate', key="generate_button"):
        try:
            df = pd.read_excel(st.session_state['file'])
            st.session_state['df'] = df
            config_select()
        except Exception as e:
            st.write(f"Error in reading xls file while generating config file: {e}")
            print(f"Error in reading xls file while generating config file: {e}")
    elif 'df' in st.session_state:
        config_select()

def infer_default_type(pandas_dtype):
    # Infer default data type from Pandas dtype
    if pd.api.types.is_bool_dtype(pandas_dtype):
        return 'True/False'
    elif pd.api.types.is_integer_dtype(pandas_dtype):
        return 'Number'
    elif pd.api.types.is_float_dtype(pandas_dtype):
        return 'Decimal point Number'
    elif pd.api.types.is_datetime64_any_dtype(pandas_dtype):
        return 'DATE'
    else:
        return 'Categorical/String'  # Default to Categorical/String if unable to infer

def config_select():
    try:
        df = st.session_state['df']
        cols = df.columns
        pro_cols = [(re.sub(r'\W+', '_', col.lower().strip())) for col in df.columns]

        # Initialize session state for inputs
        if 'table_name' not in st.session_state:
            st.session_state['table_name'] = ''

        if 'column_data_types' not in st.session_state:
            st.session_state['column_data_types'] = {}

        if 'primary_keys' not in st.session_state:
            st.session_state['primary_keys'] = []

        if 'graphs' not in st.session_state:
            st.session_state['graphs'] = []

        if 'histogram_columns' not in st.session_state:
            st.session_state['histogram_columns'] = []

        if 'bar_columns' not in st.session_state:
            st.session_state['bar_columns'] = []

        if 'pie_columns' not in st.session_state:
            st.session_state['pie_columns'] = []

        if 'line_columns' not in st.session_state:
            st.session_state['line_columns'] = []

        if 'scatter_columns' not in st.session_state:
            st.session_state['scatter_columns'] = []

        if 'categorical_filters' not in st.session_state:
            st.session_state['categorical_filters'] = []

        if 'numerical_filters' not in st.session_state:
            st.session_state['numerical_filters'] = []

        if 'date_filters' not in st.session_state:
            st.session_state['date_filters'] = []

        if 'json_file_name' not in st.session_state:
            st.session_state['json_file_name'] = 'config'

        if 'json_file_location' not in st.session_state:
            st.session_state['json_file_location'] = 'C:\\Users\\Jay Pandya\\Desktop\\data_handling_app\\'

        if 'db_name' not in st.session_state:
            st.session_state['db_name'] = 'database.db'

        table_name = st.text_input('Enter the name of the Table in lowercase single word', st.session_state['table_name'], key="table_name_input")
        st.session_state['table_name'] = table_name

        # Map selectbox options to SQL types
        dtype_dict_map = {
            'Decimal point Number': 'REAL',
            'Number': 'INTEGER',
            'Categorical/String': 'VARCHAR(100)',
            'True/False': 'BOOLEAN',
            'DATE': 'DATE'
        }

        # Iterate through columns to infer default data type
        column_data_types = {}
        for idx, col in enumerate(cols):
            default_type = infer_default_type(df[col].dtype)
            options = ['Decimal point Number', 'Number', 'Categorical/String', 'True/False', 'DATE']
            default_value = options.index(default_type) if default_type in options else 2  # Default to 'Categorical/String' if not found
            data_type = st.selectbox(f"Select data type for column '{col}'", options, index=default_value, key=f"col_{idx}")
            column_data_types[col] = f"{pro_cols[cols.get_loc(col)]} {dtype_dict_map[data_type]}"
        st.session_state['column_data_types'] = column_data_types

        # Select the primary keys
        primary_keys = st.multiselect("Select Primary keys", pro_cols, default=st.session_state['primary_keys'], key="primary_keys_multiselect")
        st.session_state['primary_keys'] = primary_keys

        # Multi-select for graphs and filters
        graphs = st.multiselect("Select graphs", ["histogram", "bar", "pie", "line", "scatter"], default=st.session_state['graphs'], key="graphs_multiselect")
        st.session_state['graphs'] = graphs

        if "histogram" in graphs:
            histogram_columns = st.multiselect("Select columns for histogram", pro_cols, default=st.session_state['histogram_columns'], key="histogram_columns_multiselect")
            st.session_state['histogram_columns'] = histogram_columns

        if "bar" in graphs:
            bar_columns = st.multiselect("Select columns for bar", pro_cols, default=st.session_state['bar_columns'], key="bar_columns_multiselect")
            st.session_state['bar_columns'] = bar_columns

        if "pie" in graphs:
            pie_columns = st.multiselect("Select columns for pie", pro_cols, default=st.session_state['pie_columns'], key="pie_columns_multiselect")
            st.session_state['pie_columns'] = pie_columns

        if "line" in graphs:
            line_columns = st.multiselect("Select columns for line", pro_cols, default=st.session_state['line_columns'], key="line_columns_multiselect")
            st.session_state['line_columns'] = line_columns

        if "scatter" in graphs:
            scatter_columns = st.multiselect("Select columns for scatter", pro_cols, default=st.session_state['scatter_columns'], key="scatter_columns_multiselect")
            st.session_state['scatter_columns'] = scatter_columns

        categorical_filters = st.multiselect("Select categorical filters", pro_cols, default=st.session_state['categorical_filters'], key="categorical_filters_multiselect")
        st.session_state['categorical_filters'] = categorical_filters

        numerical_filters = st.multiselect("Select numerical filters", pro_cols, default=st.session_state['numerical_filters'], key="numerical_filters_multiselect")
        st.session_state['numerical_filters'] = numerical_filters

        date_filters = st.multiselect("Select date filters", pro_cols, default=st.session_state['date_filters'], key="date_filters_multiselect")
        st.session_state['date_filters'] = date_filters

        # Input for JSON file name and location
        json_file_name = st.text_input("Enter the JSON file name (without .json extension)", st.session_state['json_file_name'], key="json_file_name_input")
        st.session_state['json_file_name'] = json_file_name

        json_file_location = st.text_input("Enter the location to save the JSON file", st.session_state['json_file_location'], key="json_file_location_input")
        st.session_state['json_file_location'] = json_file_location

        # Input for database name
        db_name = st.text_input("Enter the database name (with .db extension)", st.session_state['db_name'], key="db_name_input")
        st.session_state['db_name'] = db_name

        config = {
            'header_mapping': {
                table_name: column_data_types
            },
            'view_mapping': {
                table_name: {
                    'graphs': {
                        "histogram": ",".join(histogram_columns) if "histogram" in graphs else "",
                        "bar": ",".join(bar_columns) if "bar" in graphs else "",
                        "pie": ",".join(pie_columns) if "pie" in graphs else "",
                        "line": ",".join(line_columns) if "line" in graphs else "",
                        "scatter": ",".join(scatter_columns) if "scatter" in graphs else "",
                    },
                    "filters": {
                        "categorical": ",".join(categorical_filters),
                        "numerical": ",".join(numerical_filters),
                        "date": ",".join(date_filters)
                    }
                }
            },
            "db_config": {
                "db_path": f"{json_file_location}{db_name}",
                "table_name": table_name,
                "batch_size": 1000
            }
        }

        if st.button('Save Configuration', key="save_config_button"):
            try:
                s = ""
                n = len(primary_keys)
                for i in range(n):
                    if i!=(n-1):
                        s = s + primary_keys[i] + ","
                    else:
                        s = s + primary_keys[i]
                column_data_types['PRIMARY KEY'] = s
                with open(f"{json_file_location}{json_file_name}.json", 'w') as json_file:
                    json.dump(config, json_file, indent=4)
                st.write(f"Configuration saved as {json_file_location}{json_file_name}.json")
            except Exception as e:
                st.write(f"Error in saving the config file: {e}")
                print(f"Error in saving the config file: {e}")

    except Exception as e:
        st.write(f"Error in generating config file: {e}")
        print(f"Error in generating config file: {e}")

def insert_file_tab(config_json_path):
    st.subheader('Create database instance/update existing database instance')
    file = st.file_uploader("Upload Excel file for insertion", type=['xlsx'])
    if file and config_json_path is not None and st.button('Insert'):
        insert_xls_to_database(file,config_json_path)

def filter_view_data(config_json_path):
    st.subheader('Filter and view Data')
    connection,table_list,_=connect_to_db(config_json_path)
    tables = ['none'] + table_list
    table_name = st.selectbox('Select Table Name', tables)
    if table_name == "none":
        st.warning("Please select a table")
    else:
        df = pd.read_sql(f"SELECT * FROM {table_name}", con=connection)
        table_view(connection,df,config_json_path,table_name)
    
def table_view(connection,df,config_json_path,table_name):
    try:
        with open(config_json_path) as f:
            config = json.load(f)
        cat_cols = config['view_mapping'][table_name]["filters"]["categorical"].split(",")
        num_cols = config['view_mapping'][table_name]["filters"]["numerical"].split(",")
        
        #Handling the categorical columns
        cat_col_val_list = []
        for i in cat_cols:
            cat_col_val_list.append(['All'] + sorted(list(df[i].unique())))
        #print(cat_col_val_list)
        cat_response = []
        for i in range(len(cat_col_val_list)):
            cat_response.append(st.selectbox(cat_cols[i],cat_col_val_list[i]))

        #Handling the numerical columns
        num_min_max = []
        for i in num_cols:
            num_min_max.append([(df[i].min()),(df[i].max())])
        #print(num_min_max)
        num_response = []
        for i in range(len(num_min_max)):
            col1, col2 = st.columns([1, 1])
            with col1:
                min_val = st.number_input(f'Minimum:    {num_cols[i]}', value=num_min_max[i][0]) 
            with col2:
                max_val = st.number_input(f'Maximum:    {num_cols[i]}', value=num_min_max[i][1])
            num_response.append([min_val,max_val])

        if st.button('Show'):
            filtered_df = df.copy()
            #Handling categorical filter
            for i in range(len(cat_response)):
                if cat_response[i] != 'All':
                    filtered_df = filtered_df[filtered_df[cat_cols[i]] == cat_response[i]]
            #Handling numerical filter
            for i in range(len(num_response)):
                filtered_df = filtered_df[(filtered_df[num_cols[i]] >= num_response[i][0]) & (filtered_df[num_cols[i]] <= num_response[i][1])]
            print("Table view created Successfully")
            st.write(f"\n{filtered_df.shape[0]} rows found\n")
            st.write(filtered_df)

    except Exception as e:
        print(e)
        st.write(e)
    finally:
        if connection:
            connection.close()
            print("Connection ended")
    
def display_graphs_tab(config_json_path):
    st.subheader('View graphs and visuals')
    connection,table_list,_=connect_to_db(config_json_path)
    tables = ['none'] + table_list
    table_name = st.selectbox('Select Table Name', tables)
    if table_name == "none":
        st.warning("Please select a table")
    else:
        df = pd.read_sql(f"SELECT * FROM {table_name}", con=connection)
        display_graphs(df,config_json_path,table_name)

def display_graphs(df,config_json_path,table_name):
    try:
        with open(config_json_path) as f:
            config = json.load(f)
        hist_cols = config['view_mapping'][table_name]["graphs"]["histogram"].split(",")
        pie_cols = config['view_mapping'][table_name]["graphs"]["pie"].split(",")
        for i in hist_cols:
            st.subheader(f"Histogram of {i}")
            fig = px.histogram(df, x=i)
            st.plotly_chart(fig)
        for i in pie_cols:
            freq = df[i].value_counts()
            freq_df = pd.DataFrame({i: freq.index, 'count': freq.values})
            fig = px.pie(freq_df, values='count', names=i, title=f'Pie Chart of {i} Frequencies')
            st.plotly_chart(fig)


    except Exception as e:
        print("Error occured while displaying graphs:",e)
        st.write("Can't display graph:",e)

if __name__=="__main__":
    main()