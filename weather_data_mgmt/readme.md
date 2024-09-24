Weather Data Management Project

Project Setup

This project is a Django application designed to manage weather data. To set it up on your local machine, please follow the instructions below.

### Prerequisites
Make sure you have the following installed:
- Python 3.x
- Django
- PostgreSQL
- `venv` package for virtual environment creation

### Setup Instructions

Create a Virtual Environment**
   	Open your terminal and navigate to the project directory. Then run:

   	```bash
   	python3 -m venv <virtual_env_name>

Activate the Virtual Environment

On macOS/Linux:
Bash
Copy code
source <virtual_env_name>/bin/activate

On Windows:
bash
Copy code
project_name\Scripts\activate
Create a Django Project

Setup Database Connection

In the settings.py file, change the database configuration to PostgreSQL:
Use pgAdmin or the terminal to create a new database

Running the Project

Run Migrations
python manage.py makemigrations
python manage.py migrate
Start the server with: python manage.py runserver

Access the Project
Open your browser and go to:
http://127.0.0.1:8000/
http://127.0.0.1:8000/apis/docs/


Data Ingestion
Assumptions:
We are provided with multiple text files containing records of day-wise temperatures.
Each file’s data belongs to one of the five states provided in the problem statement.
We assume that starting five letters of each file form a unique state code. Remaining characters of filename form the station, of which the records have been provided.


USC0011
Nebraska
USC0012
Iowa
USC0013
Illinois
USC0025
Indiana
USC0033
Ohio


To load data into the database, I have created a management command
Run the management command to load data:
python manage.py load_weather_data
This management command reads every txt file, loads the file content in a dataframe making it easier to operate on data. Based on the filename, I derived the state and station that this file belongs to. Based on these parameters, I created a list of records to be inserted in the weather data.
Then, I called the bulk creation method on the django model to reduce the total number of database hits, making efficient insertion of large data.


REST APIS
Fetch weather data
Endpoint - /weatherdata/
Query params
Start: starting index for pagination
End: end index for pagination
Station_id: Fetch stationwise data across all states
State: Fetch statewise data
Date: Fetch datewise data across all states and stations
Fetch statistics data
Endpoint - /stats/
Query params
Station_id: Filter stats only for a particular station id
Year: Fetch stats only for input year
State: Fetch stats only for state
Save statistics data
Endpoint: /calculatestats/
This will make an entry in the stats table, storing average max temperature, average min temperature and total precipitation for every station across all states
