
# EXCEL DATABASE CONNECTION APPLICATION

## Overview
The Excel Database Connection Application is a comprehensive tool designed to facilitate the seamless integration of Excel data into an SQLite database. With this application, users can create, update, filter, view, and visualize data from Excel files, all through an intuitive Streamlit interface.

## Features
- **Configuration File Generation**: Automatically generate configuration files for your Excel datasets.
- **Database Operations**: Create or update database tables based on the Excel data.
- **Data Filtering and Viewing**: Filter and view data from the database with user-friendly controls.
- **Data Visualization**: Generate histograms, bar charts, pie charts, line charts, and scatter plots based on the data.

## Requirements
- Python 3.8+
- pandas
- sqlite3
- json
- streamlit
- plotly

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/pjay001/excel-db-connection-app.git
   cd excel-db-connection-app
   ```

2. Install the required dependencies:
   ```bash
   pip install pandas sqlite3 json streamlit plotly
   ```

## Usage
1. Run the Streamlit application:
   ```bash
   streamlit run app.py
   ```

2. Upload your Excel file and follow the prompts to generate a configuration file.

3. Use the provided interface to create or update the database, filter and view data, and visualize the data with various graphs.

![1](https://github.com/user-attachments/assets/483b2f62-4b5e-4c78-87f9-ac31674fac60)

## Application Tabs
- **Create configuration file for excel**: Generate a JSON configuration file for your Excel dataset.
  ![Screenshot (1)](https://github.com/user-attachments/assets/fcc3aad2-13e9-4cdc-9b60-6127729fec4b)
  ![Screenshot (3)](https://github.com/user-attachments/assets/05fba07e-7d24-4389-857c-fdf674dd52eb)
  ![Screenshot (4)](https://github.com/user-attachments/assets/c45613b3-b1cc-42db-bd7e-bd12819d7947)

- **Create/Update Database**: Insert or update data from your Excel file into the SQLite database.
  ![Screenshot (6)](https://github.com/user-attachments/assets/e2727342-0768-40e0-b623-cf8dc1fa0b64)

- **Filter and view Data**: Filter and view the data stored in the database.
  ![Screenshot (8)](https://github.com/user-attachments/assets/da1cc946-3cbf-41b6-9a5f-070a177b498b)

- **Display Graphs**: Visualize the data with histograms, bar charts, pie charts, line charts, and scatter plots.
  ![Screenshot (11)](https://github.com/user-attachments/assets/4e7e6f7d-68e6-4176-b44e-5e35330a2d65)
  ![Screenshot (12)](https://github.com/user-attachments/assets/0c6676b4-6165-4789-b4e9-d5b0514eac9a)

## Configuration File Structure
The configuration file is a JSON file that maps the headers in your Excel file to database columns and defines the data types, primary keys, and visualization options.

### Example Configuration
```json
{
  "header_mapping": {
    "your_table_name": {
      "column1": "col1_name S![Screenshot (11)](https://github.com/user-attachments/assets/5a1df909-0787-4025-ae3b-362d547512ea)
QL_TYPE",
      "column2": "col2_name SQL_TYPE",
      "PRIMARY KEY": "primary_key_column"
    }
  },
  "view_mapping": {
    "your_table_name": {
      "graphs": {
        "histogram": "col1,col2",
        "bar": "col3",
        "pie": "col4",
        "line": "col5",
        "scatter": "col6"
      },
      "filters": {
        "categorical": "col7,col8",
        "numerical": "col9,col10",
        "date": "col11"
      }
    }
  },
  "db_config": {
    "db_path": "path_to_your_db",
    "table_name": "your_table_name",
    "batch_size": 1000
  }
}
```

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

