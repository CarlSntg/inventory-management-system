import sqlite3
import PySimpleGUI as sg
import datetime

# Connect to SQLite database or create it if not exists
conn = sqlite3.connect("inventory_management.db")
cursor = conn.cursor()

# Create Product and Sales tables if not exists
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Product (
        ProductID INTEGER PRIMARY KEY,
        ProductName TEXT,
        QuantityInStock INTEGER,
        ReorderLevel INTEGER,
        UnitPrice REAL,
        CostPerUnit REAL
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Sales (
        SaleID INTEGER PRIMARY KEY,
        ProductID INTEGER,
        QuantitySold INTEGER,
        SaleDate TEXT,
        FOREIGN KEY (ProductID) REFERENCES Product(ProductID)
    )
''')

# Function to display stock levels in a PySimpleGUI window
def view_stock_levels_gui():
    cursor.execute("SELECT * FROM Product")
    rows = cursor.fetchall()

    if not rows:
        sg.popup("No products in the inventory.")
        return

    # Create a PrettyTable and add columns
    layout = [
        [sg.Table(values=rows, headings=["Product ID", "Name", "Stock", "Reorder Level", "Price", "Cost Per Unit"],
                  auto_size_columns=False, justification='right', display_row_numbers=False, num_rows=min(25, len(rows)))],
        [sg.Button('OK')]
    ]

    window = sg.Window('View Stock Levels', layout, grab_anywhere=False, resizable=True)

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED or event == 'OK':
            break

    window.close()

# Function to display sales data in a PySimpleGUI window
def view_sales_data_gui():
    cursor.execute("SELECT * FROM Sales")
    rows = cursor.fetchall()

    if not rows:
        sg.popup("No sales data available.")
        return

    # Create a PrettyTable and add columns
    layout = [
        [sg.Table(values=rows, headings=["Sale ID", "Product ID", "Quantity Sold", "Sale Date"],
                  auto_size_columns=False, justification='right', display_row_numbers=False, num_rows=min(25, len(rows)))],
        [sg.Button('OK')]
    ]

    window = sg.Window('View Sales Data', layout, grab_anywhere=False, resizable=True)

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED or event == 'OK':
            break

    window.close()

# Function to generate reorder alerts in a PySimpleGUI window
def generate_reorder_alerts_gui():
    cursor.execute('''
        SELECT ProductID, ProductName, QuantityInStock, ReorderLevel
        FROM Product
        WHERE QuantityInStock <= ReorderLevel
    ''')

    rows = cursor.fetchall()

    if not rows:
        sg.popup("No products need to be reordered.")
        return

    # Create a PrettyTable and add columns
    layout = [
        [sg.Table(values=rows, headings=["Product ID", "Name", "Stock", "Reorder Level"],
                  auto_size_columns=False, justification='right', display_row_numbers=False, num_rows=min(25, len(rows)))],
        [sg.Button('OK')]
    ]

    window = sg.Window('Reorder Alerts', layout, grab_anywhere=False, resizable=True)

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED or event == 'OK':
            break

    window.close()

# Function to add a new product using PySimpleGUI
def add_product_gui():
    layout = [
        [sg.Text('Product Name:'), sg.InputText(key='product_name')],
        [sg.Text('Quantity in Stock:'), sg.InputText(key='quantity_in_stock')],
        [sg.Text('Reorder Level:'), sg.InputText(key='reorder_level')],
        [sg.Text('Cost Per Unit:'), sg.InputText(key='cost_per_unit')],
        [sg.Text('Unit Price:'), sg.InputText(key='unit_price')],
        [sg.Button('Add'), sg.Button('Cancel')]
    ]

    add_product_window = sg.Window('Add Product', layout)

    while True:
        event, values = add_product_window.read()

        if event == sg.WIN_CLOSED or event == 'Cancel':
            break
        elif event == 'Add':
            product_name = values['product_name']
            quantity_in_stock = int(values['quantity_in_stock'])
            reorder_level = int(values['reorder_level'])
            cost_per_unit = float(values['cost_per_unit'])
            unit_price = float(values['unit_price'])

            cursor.execute('''
                INSERT INTO Product (ProductName, QuantityInStock, ReorderLevel, UnitPrice, CostPerUnit)
                VALUES (?, ?, ?, ?, ?)
            ''', (product_name, quantity_in_stock, reorder_level, unit_price, cost_per_unit))

            conn.commit()
            sg.popup(f'Product Added:\nName: {product_name}\nQuantity in Stock: {quantity_in_stock}\nReorder Level: {reorder_level}\nCost Per Unit: {cost_per_unit}\nUnit Price: {unit_price}')
            break

    add_product_window.close()

# Function to update a product using PySimpleGUI
def update_product_gui():
    sg.popup('Update Product Function')

# Function to delete a product using PySimpleGUI
def delete_product_gui():
    sg.popup('Delete Product Function')

# Function to add sales data using PySimpleGUI
def add_sales_gui():
    sg.popup('Add Sales Function')

# Define the layout of the main menu
menu_layout = [
    [sg.Button('View Stock Levels', size=(15, 1))],
    [sg.Button('View Sales Data', size=(15, 1))],
    [sg.Button('Reorder Alerts', size=(15, 1))],
    [sg.Button('Generate Reports', size=(15, 1))],
    [sg.Button('Add Product', size=(15, 1))],
    [sg.Button('Update Product', size=(15, 1))],
    [sg.Button('Delete Product', size=(15, 1))],
    [sg.Button('Add Sales', size=(15, 1))],
    [sg.Button('Exit', size=(15, 1))]
]

# Create the main menu window
menu_window = sg.Window('Main Menu', menu_layout, size=(200, 400), element_justification="c", resizable=True)

# Event loop for the main menu
while True:
    event, values = menu_window.read()

    if event == sg.WIN_CLOSED or event == 'Exit':
        break
    elif event == 'View Stock Levels':
        view_stock_levels_gui()
    elif event == 'View Sales Data':
        view_sales_data_gui()
    elif event == 'Reorder Alerts':
        generate_reorder_alerts_gui()
    elif event == 'Generate Reports':
        sg.popup('Generate Reports Function')  # Placeholder for now
    elif event == 'Add Product':
        menu_window.hide()  # Hide the main menu window
        add_product_gui()
        menu_window.un_hide()  # Show the main menu window again
    elif event == 'Update Product':
        update_product_gui()
    elif event == 'Delete Product':
        delete_product_gui()
    elif event == 'Add Sales':
        add_sales_gui()

# Close the main menu window
menu_window.close()
