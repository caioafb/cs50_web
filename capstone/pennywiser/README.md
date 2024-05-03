# PennyWiser

## Table of Contents
- [Introduction](#introduction)
- [Technologies](#technologies)
- [Installation](#installation)
- [How PennyWiser Works](#how-pennywiser-works)
- [File Structure](#file-structure)
- [Distinctiveness and Complexity](#distinctiveness-and-complexity)

## Introduction
PennyWiser is a web-based financial management tool designed for small businesses. It simplifies daily financial tasks, including managing accounts payable and receivable, budget projection, and cash flow analysis. This capstone project for the CS50 Web Programming with Python and Javascript course is designed to facilitate the daily financial control of small businesses. With PennyWiser, users can track expenses and incomes, including installments that repeat monthly, annually, or at other intervals. The app categorizes transactions, providing users with an overview of spending and income by category, with a percentage breakdown. Additionally, PennyWiser generates summaries resembling a bank statement for all accounts, allowing users to quickly check their balances.

## Technologies
- Python
- Django
- JavaScript
- Bootstrap

## Installation
To run PennyWiser locally, follow these steps:
1. Clone this repository.
2. Install Python from [python.org](https://www.python.org/).
3. Install dependencies using `pip install -r requirements.txt`.
4. Build the database by running `python manage.py makemigrations` and `python manage.py migrate`.
5. Start the server with `python manage.py runserver`.

## How PennyWiser Works
### Setup:
- Register a new user.
- In the Settings menu:
    - Create all accounts your company has.
    - Create all expense and income categories relevant to your company.

### Usage:
1. **Add Transactions:** Click the "+" sign in the horizontal menu to register a new transaction. Select appropriate options and replicate settings.
2. **Manage Transactions:** The index page displays all expiring and upcoming transactions. Click on a transaction's description to edit it. Settle accounts by clicking the "arrow down" symbol and providing appropriate information.
3. **View Account Summary:** Use the "Accounts" menu option to see a summary of all accounts' balances. Select an account and date to view a bank statement-like report.
4. **Search Transactions:** Use the "Archive" menu to search for all transactions by date, search query, expense or income, and/or settled or unsettled status.
5. **View Financial Overview:** The "Overview" page displays an overview of expenses and income by category for the selected date (month/year).
6. **Manage Settings:** Use the "Settings" menu to create new companies, categories, or accounts. Use "Swap company" to switch between multiple company accounts.

## File structure
In addition to the default Django structure, all PennyWiser's backend logic is inside the `views.py` file, the main functions are:

- **Index view**:
Renders the index page and handles account settlement and recurring transactions.

- **New transaction view**:
Renders the page for creating new transactions.

- **Archive view**
Allows users to search and view all registered transactions.

- **Edit view**
Enables users to modify transaction information.

- **Accounts view**
Shows a summary of company accounts, offering an account statement with all transactions.

- **Overview view**:
Displays a logistics overview of settled and projected expenses and income by category.

- **Settings view**:
Renders the settings page for creating new companies, categories and accounts.

- **Swap company view**
Allows users to switch between multiple company accounts.

Javascript functions are stored in `/static/pennywise` folder.

## Distinctiveness and Complexity
PennyWiser distinguishes itself by providing tailored financial solutions for tracking expenses, incomes, and accounts, specifically for small businesses. Its focus on financial control, categorization, and reporting sets it apart as a specialized tool for business owners. The project exhibits complexity beyond typical course projects in areas such as transaction handling, recurring transactions, and comprehensive reporting, requiring intricate backend logic, database management, and data aggregation processes.
