# Mortgage Monitor

## Description

This project is a mortgage monitor where users can input their mortgage details (principal, interest rate, term, deposit, and extra costs). The calculator provides the initial payment breakdown, mortgage maturity, amortization schedule, and interactive graphics. Users can update their mortgage, delete entries, and create accounts. The calculation features include monthly and fortnightly payments.

## Features

- Calculate monthly and fortnightly mortgage payments
- Display amortization schedule
- Interactive graphics to visualize mortgage data
- User account creation, update, and deletion
- CRUD operations for mortgage details

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

--------------------
Run the following command:

```
pytest
```

Screenshot
--------------------
