# Excel-Database-Connection-Application

Overview
The Excel Database Connection Application is a comprehensive tool designed to facilitate the seamless integration of Excel data into an SQLite database. With this application, users can create, update, filter, view, and visualize data from Excel files, all through an intuitive Streamlit interface.

Features
Configuration File Generation: Automatically generate configuration files for your Excel datasets.
Database Operations: Create or update database tables based on the Excel data.
Data Filtering and Viewing: Filter and view data from the database with user-friendly controls.
Data Visualization: Generate histograms, bar charts, pie charts, line charts, and scatter plots based on the data.
Requirements
Python 3.8+
pandas
sqlite3
json
streamlit
plotly
Installation
Clone the repository:

bash
Copy code
git clone https://github.com/yourusername/excel-db-connection-app.git
cd excel-db-connection-app
Install the required dependencies:

bash
Copy code
pip install pandas sqlite3 json streamlit plotly
Usage
Run the Streamlit application:

bash
Copy code
streamlit run app.py
Upload your Excel file and follow the prompts to generate a configuration file.

Use the provided interface to create or update the database, filter and view data, and visualize the data with various graphs.

Application Tabs
Create configuration file for excel: Generate a JSON configuration file for your Excel dataset.
Create/Update Database: Insert or update data from your Excel file into the SQLite database.
Filter and view Data: Filter and view the data stored in the database.
Display Graphs: Visualize the data with histograms, bar charts, pie charts, line charts, and scatter plots.
Configuration File Structure
The configuration file is a JSON file that maps the headers in your Excel file to database columns and defines the data types, primary keys, and visualization options.

Example Configuration
json
Copy code
{
  "header_mapping": {
    "your_table_name": {
      "column1": "col1_name SQL_TYPE",
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
License
This project is licensed under the MIT License. See the LICENSE file for details.

Contributing
Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

Acknowledgements
Special thanks to the open-source community for providing the tools and libraries used in this project.

