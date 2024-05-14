# Change Request

## Title
Entire layout for displaying the main page.

## Requester Information
- **Name:** Katherine Mulder

## Date
14/05/2024

## Change Description
For the programming part, my logical thinking differs from our original design. I will break down the programming into more classes to represent the outcome.

The original design consists of three class diagrams: users, mortgage, and transaction. The wireframe for the index page displays all the data in a table layout, matching the Excel spreadsheet details.

In my design, I have incorporated more classes into my programming:

- **Mortgage:** This class will be the core of your application, handling calculations related to mortgages, such as monthly payments, total interest paid, remaining balance, etc. It might contain methods like `calculateMonthlyPayment`, `calculateTotalInterest`, `calculateRemainingBalance`, etc.

- **Transaction:** This class represents a single transaction or adjustment made by the user, containing information about changes made to the mortgage, such as the new interest rate, loan amount, term, etc. This class may also have methods to apply the transaction to the current mortgage analysis.

- **MortgageSummary:** This class will represent the summary of the mortgage analysis, containing information such as total loan amount, interest rate, term, monthly payment, total interest paid, remaining balance, etc. It may have methods to generate and update the summary based on the current mortgage information.

- **User:** This class represents a user of your application, containing information about the user, such as their name, email, etc. It could also store a list of transactions made by the user.

- **AnalysisPeriod:** This class represents the period for which the analysis is being shown (e.g., monthly, annually, etc.), containing methods to adjust the period and update the analysis accordingly.

- **App:** This class will handle interactions with the web interface, taking user inputs such as mortgage details and transaction adjustments, and using the other classes to perform calculations and update the interface accordingly.

Due to the different class diagram, it directed me to represent the design differently than the original wireframe. Overall, it's just design changes, and the functionality remains the same.

## Scope
This change request focuses on updating the appearance and layout of our web application and programming class structure. It involves rearranging elements like menus, page structures, colors, fonts, and overall design to enhance the user experience without altering functionality.

## Proposed Solution
- Rearranging and resizing elements for better usability.
- Ensuring the design looks good.
- Updating style and code files to reflect the changes.

## Rationale
- Make the app easier to use.
- Improve its visual appeal.
- Improve clean code.
- Keep up with current design standards.

## Impact Assessment
- As a junior developer, there is a risk that I may encounter challenges in implementing the changes, which could impact the project's progress and result in delays. This may lead to the client not receiving the ideal solution within the expected timeframe.
- The proposed changes may require more time for implementation due to the need for additional development and testing efforts.
- Users may need a bit of guidance.
- It will need to establish a process for gathering feedback from users
after implementation to identify any impacts or issues.

## Attachments

