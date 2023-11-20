# Inventory Management System

This is an Inventory Management System implemented in Python using SQLite for data storage and PySimpleGUI for the graphical user interface. The system allows you to manage products, track sales data, generate reports, and receive reorder alerts.

## Prerequisites
Make sure you have the following dependencies installed:

    sqlite3
    datetime
    PySimpleGUI
    matplotlib

Install missing dependencies using:

    pip install sqlite3 datetime PySimpleGUI matplotlib

## Setup

Download the script (inventory_management.py) to your local machine.
Run the script using a Python interpreter.

    python inventory_management.py

## Features
1. View Stock Levels
- Displays the current stock levels of all products in a tabular format.

2. View Sales Data
- Shows the sales data, including sale ID, product ID, quantity sold, and sale date.

3. Reorder Alerts
- Generates alerts for products that have quantity levels below the specified reorder level.

4. Add Product
- Adds a new product to the inventory with details such as product name, quantity in stock, reorder level, cost per unit, and unit price.

5. Update Product
- Allows you to modify existing product details such as quantity in stock, reorder level, unit price, and cost per unit.

6. Delete Product
- Deletes a product from the inventory, including associated sales data.

7. Add Sales
- Records sales data, including the product ID, quantity sold, and sale date.

8. Generate Reports
- Generates reports on total sales for each product, total revenue, total cost of goods sold, and overall profit margin. It also includes a graphical representation of monthly sales over time.

9. Exit
- Closes the application.

## Usage

Upon launching the application, you will be presented with a main menu.
Select the desired operation from the menu to perform specific tasks.
Follow the on-screen instructions for each operation.

## Note

The system utilizes SQLite for database management. The database file (inventory_management db) will be created in the same directory as the script.
Feel free to explore and customize the code based on your specific inventory management needs.
