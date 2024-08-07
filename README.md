# Mortgage Monitor

## Description
The Mortgage Monitor is a web application to help users manage their mortgage details. 
With a range of features, the application provides users with tools to calculate payments, 
visualize data, and manage their mortgage information.

## Features List 
#### Mortgage Setup
- **Collect user inputs**:
<br> mortgage name, initial interest rate, initial principal, initial term, 
deposit, extra costs, start date, comments, payment override enabled, monthly payment override, 
fortnightly payment override, increment amounts, increment percentages.
- **Calculate Monthly and Fortnightly Mortgage Payments**: Compute repayments based on different frequencies.
- **Override Payments**: Add extra payments to reduce the loan term and total interest.
- **Balloon Payment**: Plan for larger final payments to lower repayments.
- **Display Amortization Schedule**: Break down payments into principal and interest over time.
- **Calculate Mortgage Maturity Date**: Refer to the Amortization tab for the detailed payment.
- **Projected Payments**: Calculate and display projected payments for different increment scenarios.
- **Graphics**: Visualize mortgage data with charts and graphs.
- **User Account Management**: Create, update, and delete user accounts.
- **CRUD for Mortgage Details**: Manage mortgage records with create, read, update, and delete operations.
- **Export Amortization Table as .xlsx**: Save the amortization schedule to an Excel file for easy sharing and analysis.
- **Initial Transaction Logging**: Log the creation of the mortgage and store initial transaction details.

#### Updating Mortgage
- **Adjust Interest Rates**: Allow users to update the interest rate of their mortgage.
- **Manage Extra Costs**: Facilitate the addition and tracking of extra costs.
- **Transaction Logging**: Record each transaction with details like datetime, updated principal, new interest rate, and new payment amounts.
- **Recalculate Mortgage**: Adjust the mortgage details based on new inputs without changing the remaining term.
- **Update Amortization Schedule**: Reflect changes in principle and payments in the updated amortization table.
- **Display Updated Information**: Present updated payment breakdown, mortgage maturity date, amortization table, and visualized payment schedules.

#### Adjust Analysis Period
- **Date Range Selector**: Provide an interface for users to specify the analysis period.
- **Filter Data**: Filter the amortization table and transaction logs to include only entries within the selected date range.
- **Recalculate Metrics**: Update metrics and visualizations to reflect the selected analysis period.
- **Display Filtered Information**: Show the filtered payment breakdown and amortization table, and visualize payment schedules and principal reduction for the selected period.

## Technologies Used
- Python 3.10
- Flask
- PostgreSQL
- Plotly
- HTML 
- Bootstrap
- JavaScript

## File Structure and Responsibilities
- `Mortgage.py`: Handles all initial mortgage calculations.
- `Update_mortgage.py` Handles all the updates.
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


3. Create and Activate a Virtual Environment (Optional):
   Creating a virtual environment is recommended to manage dependencies and avoid conflicts with other projects.
   <br>
   On Window:
   ```
   python -m venv venv
   venv\Scripts\activate
   ```
   On macOS and Linux:
   ```
   python -m venv venv
   source venv/bin/activate
   ```
   
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
   After installing the dependencies, you can verify the installation by listing the installed packages:
   ```
   pip freeze
   ```
5. start the database
   ```
    python database.py
   ```

6. Start the application:
    ```
   .\web.cmd
   ```
7. Access the application:
open a web browser and navigate to 
   ```
   http://127.0.0.1:5000
   ```

8. Run The Test Cases:
   ```
   pytest
   ```
   
### TO DO List
- [x] Fix override payment so that users can choose either monthly or fortnightly in the creating new mortgage selection. 
At the moment users have to input both the monthly and fortnightly override payment to be able to calculate the override payment.
- [x] Fix update mortgage payment based on the following:
  1. Extra Costs:
     - Users can add additional costs to the mortgage, which will increase the principal.
  2. Balloon Payments:
     - Users can make large one-time payments to reduce the principal amount significantly.
  3. Transaction History and Tracking:
     - **Transaction Date**: The date of the update or change, following the format in the amortization table (e.g., 01/01/2024, 01/01/2026).
     - **Current Principal**: The principal amount at the time of the transaction.
     - **Current Interest Rate**: The interest rate at the time of the transaction.
     - **Remaining Term**: The remaining term of the mortgage at the time of the transaction (e.g., 20, 18, 16 years).
     - **Extra Payments**: Any additional payments made towards the mortgage.
     - **Extra Costs**: Any additional costs added to the mortgage.
     - **Comments**: Any notes or comments related to the transaction.
  4. Display of Information:
     - **Per Monthly Balance**: The balance from the monthly amortization table.
     - **Per Fortnightly Balance**: The balance from the fortnightly amortization table.
     - **Interest Paid**: The amount of interest paid as per the amortization schedule.
     - **Term Year**: The remaining term in years (e.g., 20, 18, 16).


Additional Scripts
- 
--------------------
- `run.py` to start the application in a minimized window.
- `build.py` to compile the application into an executable.
- `pip.cmd` to manage Python packages.
- `web.cmd` to start the application (which should point to main.py).





