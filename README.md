# Wealthy

Wealthy is a web-based stock trading application.

The application allows users to simulate buying and selling stocks using virtual money. Users can register for an account, look up stock prices, buy and sell shares, and track their portfolio and transaction history.

## Features

- **User Registration:** Create an account with a username and password.
- **User Login:** Log in and log out of your account.
- **Stock Lookup:** Search for stocks using ticker symbols and view current stock prices.
- **Buy Stocks:** Purchase shares using available virtual cash.
- **Sell Stocks:** Sell shares that you currently own.
- **Portfolio:** View owned stocks, share quantities, current prices, and total values.
- **Transaction History:** Review previous stock purchases and sales.
- **Cash Balance:** Track your remaining virtual money.

## Technologies Used

- Python
- Flask
- SQLite
- HTML5
- CSS3
- Bootstrap
- Jinja2
- CS50 Library

## Project Structure

    finance/
    ├── app.py
    ├── .gitignore
    ├── helpers.py
    ├── finance.db
    ├── requirements.txt
    ├── static/
    │   └── styles.css
    └── templates/
        ├── apology.html
        ├── buy.html
        ├── history.html
        ├── layout.html
        ├── login.html
        ├── portofilio.html
        ├── quote.html
        ├── quoteresult.html
        ├── registration.html
        └── sell.html

## Installation and Setup

### 1. Clone the Repository

    git clone https://github.com/yosidani/Wealthy.git
    cd Wealthy

### 2. Install Dependencies

    pip install -r requirements.txt

### 3. Run the Application

    flask run

Open your browser and visit:

    http://127.0.0.1:5000

## Database

The application uses SQLite to store user information and transaction records.
* To run it locally, please rename finance.db.example to finance.db

The database includes:

- **users:** Stores usernames, hashed passwords, and cash balances.
- **transactions:** Stores stock purchases and sales, including ticker symbols, share quantities, prices, and timestamps.

## How to Use

1. Register a new account.
2. Log in using your credentials.
3. Search for a stock using its ticker symbol.
4. Check the stock's current price.
5. Buy shares using your available virtual cash.
6. View your updated portfolio.
7. Sell shares when desired.
8. Check your transaction history.

## Project Objectives

This project demonstrates practical knowledge of:

- Backend development using Python and Flask.
- Database management with SQL and SQLite.
- User authentication and session management.
- API integration.
- Form validation and error handling.
- Dynamic web page rendering using Jinja2.
- Financial calculations and transaction management.

## Disclaimer

This app is designed to simulates stock trading using virtual money and does not involve real financial transactions or investment advice.

## Author

**Yosias Demoz**
