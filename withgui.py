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
                  auto_size_columns=False, justification='right', display_row_numbers=False,
                  num_rows=min(25, len(rows)))],
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
                  auto_size_columns=False, justification='right', display_row_numbers=False,
                  num_rows=min(25, len(rows)))],
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
                  auto_size_columns=False, justification='right', display_row_numbers=False,
                  num_rows=min(25, len(rows)))],
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
            sg.popup(
                f'Product Added:\nName: {product_name}\nQuantity in Stock: {quantity_in_stock}\nReorder Level: {reorder_level}\nCost Per Unit: {cost_per_unit}\nUnit Price: {unit_price}')
            break

    add_product_window.close()


# Function to update a product using PySimpleGUI
def update_product_gui():
    layout = [
        [sg.Text('Product ID:'), sg.InputText(key='product_id')],
        [sg.Text('New Quantity in Stock:'), sg.InputText(key='new_quantity')],
        [sg.Text('New Reorder Level:'), sg.InputText(key='new_reorder_level')],
        [sg.Text('New Unit Price:'), sg.InputText(key='new_unit_price')],
        [sg.Text('New Cost Per Unit:'), sg.InputText(key='new_cost_per_unit')],
        [sg.Button('Update'), sg.Button('Cancel')]
    ]

    update_product_window = sg.Window('Update Product', layout)

    while True:
        event, values = update_product_window.read()

        if event == sg.WIN_CLOSED or event == 'Cancel':
            break
        elif event == 'Update':
            product_id = values['product_id']
            new_quantity = values['new_quantity']
            new_reorder_level = values['new_reorder_level']
            new_unit_price = values['new_unit_price']
            new_cost_per_unit = values['new_cost_per_unit']

            # Validate product ID
            cursor.execute('''
                SELECT *
                FROM Product
                WHERE ProductID = ?
            ''', (product_id,))
            product = cursor.fetchone()

            if not product:
                sg.popup(f"Product with Product ID {product_id} does not exist. Please enter a valid Product ID.")
                continue

            # Validate new quantity
            if new_quantity and not new_quantity.isdigit():
                sg.popup("Invalid input. Please enter a valid integer for the new quantity.")
                continue

            # Validate new reorder level
            if new_reorder_level and not new_reorder_level.isdigit():
                sg.popup("Invalid input. Please enter a valid integer for the new reorder level.")
                continue

            # Validate new unit price
            if new_unit_price:
                try:
                    new_unit_price = float(new_unit_price)
                except ValueError:
                    sg.popup("Invalid input. Please enter a valid float for the new unit price.")
                    continue

            # Validate new cost per unit
            if new_cost_per_unit:
                try:
                    new_cost_per_unit = float(new_cost_per_unit)
                except ValueError:
                    sg.popup("Invalid input. Please enter a valid float for the new cost per unit.")
                    continue

            # Generate SQL update statement based on non-null fields
            update_statement = "UPDATE Product SET"
            update_values = []

            if new_quantity:
                update_statement += " QuantityInStock = ?,"
                update_values.append(int(new_quantity))

            if new_reorder_level:
                update_statement += " ReorderLevel = ?,"
                update_values.append(int(new_reorder_level))

            if new_unit_price:
                update_statement += " UnitPrice = ?,"
                update_values.append(float(new_unit_price))

            if new_cost_per_unit:
                update_statement += " CostPerUnit = ?,"
                update_values.append(float(new_cost_per_unit))

            # Remove the trailing comma
            update_statement = update_statement.rstrip(',')

            # Add WHERE clause for the specific product ID
            update_statement += " WHERE ProductID = ?"
            update_values.append(int(product_id))

            # Update the product details in the database
            cursor.execute(update_statement, tuple(update_values))

            conn.commit()
            sg.popup(f'Product updated successfully:\nProduct ID: {product_id}\n'
                     f'New Quantity in Stock: {new_quantity if new_quantity else "Unchanged"}\n'
                     f'New Reorder Level: {new_reorder_level if new_reorder_level else "Unchanged"}\n'
                     f'New Unit Price: {new_unit_price if new_unit_price else "Unchanged"}\n'
                     f'New Cost Per Unit: {new_cost_per_unit if new_cost_per_unit else "Unchanged"}')
            break

    update_product_window.close()


# Function to delete a product using PySimpleGUI
def delete_product_gui():
    layout = [
        [sg.Text('Product ID to Delete:'), sg.InputText(key='product_id')],
        [sg.Button('Delete'), sg.Button('Cancel')]
    ]

    delete_product_window = sg.Window('Delete Product', layout)

    while True:
        event, values = delete_product_window.read()

        if event == sg.WIN_CLOSED or event == 'Cancel':
            break
        elif event == 'Delete':
            product_id = values['product_id']

            # Validate product ID
            cursor.execute('''
                SELECT *
                FROM Product
                WHERE ProductID = ?
            ''', (product_id,))
            product = cursor.fetchone()

            if not product:
                sg.popup(f"Product with Product ID {product_id} does not exist. Please enter a valid Product ID.")
                continue

            # Delete associated sales data
            cursor.execute('''
                DELETE FROM Sales
                WHERE ProductID = ?
            ''', (product_id,))

            # Delete the product from the database
            cursor.execute('''
                DELETE FROM Product
                WHERE ProductID = ?
            ''', (product_id,))

            conn.commit()
            sg.popup(f'Product and associated sales data deleted successfully:\nProduct ID: {product_id}')
            break

    delete_product_window.close()


# Function to add sales data using PySimpleGUI
def add_sales_gui():
    layout = [
        [sg.Text('Product ID:'), sg.InputText(key='product_id')],
        [sg.Text('Quantity Sold:'), sg.InputText(key='quantity_sold')],
        [sg.Text('Sale Date (YYYY-MM-DD):'), sg.InputText(key='sale_date')],
        [sg.Button('Add'), sg.Button('Cancel')]
    ]

    add_sales_window = sg.Window('Add Sales', layout)

    while True:
        event, values = add_sales_window.read()

        if event == sg.WIN_CLOSED or event == 'Cancel':
            break
        elif event == 'Add':
            product_id = values['product_id']
            quantity_sold = values['quantity_sold']
            sale_date_str = values['sale_date']

            # Validate product ID
            cursor.execute('''
                SELECT QuantityInStock
                FROM Product
                WHERE ProductID = ?
            ''', (product_id,))
            product = cursor.fetchone()

            if not product:
                sg.popup(f"Product with Product ID {product_id} does not exist. Please enter a valid Product ID.")
                continue

            current_quantity = product[0]

            # Validate quantity sold
            if not quantity_sold.isdigit():
                sg.popup("Invalid input. Please enter a valid integer for the quantity sold.")
                continue

            quantity_sold = int(quantity_sold)

            if quantity_sold > current_quantity:
                sg.popup(f"Error: Quantity in stock ({current_quantity}) is less than quantity sold ({quantity_sold}).")
                continue

            # Validate sale date
            if sale_date_str:
                try:
                    sale_date = datetime.datetime.strptime(sale_date_str, "%Y-%m-%d").date()
                except ValueError:
                    sg.popup("Invalid date format. Please use YYYY-MM-DD.")
                    continue
            else:
                sale_date = datetime.date.today()

            # Update the quantity in stock
            new_quantity = current_quantity - quantity_sold
            cursor.execute('''
                UPDATE Product
                SET QuantityInStock = ?
                WHERE ProductID = ?
            ''', (new_quantity, product_id))

            # Insert the sales data into the database
            cursor.execute('''
                INSERT INTO Sales (ProductID, QuantitySold, SaleDate)
                VALUES (?, ?, ?)
            ''', (product_id, quantity_sold, sale_date))

            conn.commit()
            sg.popup(f'Sales data added successfully:\nProduct ID: {product_id}\nQuantity Sold: {quantity_sold}\nSale '
                     f'Date: {sale_date}')
            break

    add_sales_window.close()


# Function to generate reports using PySimpleGUI
def generate_reports_gui():
    # Execute SQL queries to get data for the report
    cursor.execute('''
        SELECT Product.ProductID, Product.ProductName, SUM(Sales.QuantitySold) as TotalSales
        FROM Product
        LEFT JOIN Sales ON Product.ProductID = Sales.ProductID
        GROUP BY Product.ProductID
    ''')

    rows = cursor.fetchall()

    if not rows:
        sg.popup("No sales data available for generating reports.")
        return

    # Create a PySimpleGUI table to hold the report
    header = ["Product ID", "Name", "Total Sales"]
    table_data = [list(row) for row in rows]

    # Calculate total revenue
    cursor.execute('''
        SELECT SUM(QuantitySold * UnitPrice) AS TotalRevenue
        FROM Sales
        INNER JOIN Product ON Sales.ProductID = Product.ProductID
    ''')
    total_revenue = cursor.fetchone()[0] or 0

    # Calculate total cost of goods sold
    cursor.execute('''
        SELECT SUM(QuantitySold * CostPerUnit) AS TotalCOGS
        FROM Sales
        INNER JOIN Product ON Sales.ProductID = Product.ProductID
    ''')
    total_cogs = cursor.fetchone()[0] or 0

    # Calculate overall profit margin
    overall_profit_margin = 0 if total_revenue == 0 else ((total_revenue - total_cogs) / total_revenue) * 100

    # Create a PySimpleGUI window to display the report
    layout = [
        [sg.Table(values=table_data, headings=header, auto_size_columns=False,
                  justification='left', display_row_numbers=False, num_rows=min(25, len(rows * 2)), size=(800, 200))],
        [sg.Text(f"Total Revenue: ${total_revenue:.2f}", size=(80, 1))],
        [sg.Text(f"Total Cost of Goods Sold: ${total_cogs:.2f}")],
        [sg.Text(f"Overall Profit Margin: {overall_profit_margin:.2f}%")],
        [sg.Button('Close')]
    ]

    window = sg.Window('Generated Report', layout)

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED or event == 'Close':
            break

    window.close()


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
menu_window = sg.Window('Main Menu', menu_layout, element_justification="c", resizable=True)

# Event loop for the main menu
while True:

    # Check for reorder alerts
    cursor.execute('''
                SELECT COUNT(*)
                FROM Product
                WHERE QuantityInStock <= ReorderLevel
            ''')
    alert_count = cursor.fetchone()[0]

    if alert_count > 0:
        sg.popup(f"{alert_count} product(s) need to be reordered. Check option 3 for details.", title="Reorder Alerts")

    event, values = menu_window.read()

    if event == sg.WIN_CLOSED or event == 'Exit':
        break
    elif event == 'View Stock Levels':
        menu_window.hide()
        view_stock_levels_gui()
        menu_window.un_hide()
    elif event == 'View Sales Data':
        menu_window.hide()
        view_sales_data_gui()
        menu_window.un_hide()
    elif event == 'Reorder Alerts':
        menu_window.hide()
        generate_reorder_alerts_gui()
        menu_window.un_hide()
    elif event == 'Generate Reports':
        menu_window.hide()
        generate_reports_gui()
        menu_window.un_hide()
    elif event == 'Add Product':
        menu_window.hide()
        add_product_gui()
        menu_window.un_hide()
        menu_window.un_hide()
    elif event == 'Update Product':
        menu_window.hide()
        update_product_gui()
        menu_window.un_hide()
    elif event == 'Delete Product':
        menu_window.hide()
        delete_product_gui()
        menu_window.un_hide()
    elif event == 'Add Sales':
        menu_window.hide()
        add_sales_gui()
        menu_window.un_hide()

# Close the main menu window
menu_window.close()
