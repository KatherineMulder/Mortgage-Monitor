# Mortgage Monitor

## Description
The Mortgage Monitor is a web application to help users manage their mortgage details. 
With a range of features, the application provides users with tools to calculate payments, 
visualize data, and manage their mortgage information.
## Features

- **Calculate Monthly and Fortnightly Mortgage Payments**: Compute repayments based on different frequencies.
- **Override Payments**: Add extra payments to reduce the loan term and total interest.
- **Balloon Payment**: Plan for larger final payments to lower repayments.
- **Display Amortization Schedule**: Break down payments into principal and interest over time.
- **Interactive Graphics**: Visualize mortgage data with charts and graphs.
- **User Account Management**: Create, update, and delete user accounts.
- **CRUD for Mortgage Details**: Manage mortgage records with create, read, update, and delete operations.
- **Export Amortization Table as .xlsx**: Save the amortization schedule to an Excel file for easy sharing and analysis.



## Technologies Used

- Python 3.10
- Flask
- PostgreSQL
- Plotly
- HTML Bootstrap
- JavaScript

## File Structure and Responsibilities

- `Mortgage.py`: Handles all mortgage calculations.
- `Transaction.py`: Manages CRUD operations for mortgages and comments.
- `Database.py`: Contains functions to handle database connections and setup.
- `App.py`: Manages the Flask application and routes.
- `User.py`: Manages user-related operations.
- `graphing.py`: Generates interactive graphics for mortgage data using Plotly.
- `Main.py`: Entry point for running the application.


## Prerequisites

- Python 3.8 or higher
- PostgreSQL

## Installation and Setup

1. **Install PostgreSQL**: Ensure PostgreSQL is installed and running on the local machine.
   - [Download PostgreSQL](https://www.postgresql.org/download/)

2. **Clone the repository**:
   ```sh
   git clone <https://github.com/KatherineMulder/Mortgage-Monitor>
   cd mortgage-monitor

3. Install dependencies:
    ```
   pip install -r requirements.txt
   ```
4. Set up local PostgresSQL database:
   * Create a database named mortgage_monitor.
   * Update config.py with your PostgresSQL credentials.

5. Start the application:
    ```
   .\web.cmd
   ```
   
6. Access the application:
Open a web browser and navigate to http://127.0.0.1:5000
Run The Test Cases

   
- `run.py` to start the application in a minimized window.
- `build.py` to compile the application into an executable.
- `pip.cmd` to manage Python packages.
- `web.cmd` to start the application (which should point to main.py).
--------------------
Run the following command:

```
pytest
```

Screenshot
--------------------
