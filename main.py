import sqlite3
import os
import datetime
from prettytable import PrettyTable
from rich.console import Console

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


# Function to display stock levels
def view_stock_levels():
    cursor.execute("SELECT * FROM Product")
    rows = cursor.fetchall()

    if not rows:
        print("No products in the inventory.")
        return

    # Create a PrettyTable and add columns
    table = PrettyTable()
    table.field_names = ["Product ID", "Name", "Stock", "Reorder Level", "Price", "Cost Per Unit"]

    # Add rows to the table
    for row in rows:
        table.add_row(row)

    # Print the table
    print(table)


# Function to display the main menu
def display_menu():
    # Check for reorder alerts
    cursor.execute('''
            SELECT COUNT(*)
            FROM Product
            WHERE QuantityInStock <= ReorderLevel
        ''')
    alert_count = cursor.fetchone()[0]

    if alert_count > 0:
        print(f"\n{alert_count} product(s) need to be reordered. Check option 3 for details.")

    print("\n1. View Stock Levels")
    print("2. View Sales Data")
    print("3. Generate Reorder Alerts")
    print("4. Generate Reports")
    print("5. Add Product")
    print("6. Update Product")
    print("7. Delete Product")
    print("8. Add Sales")
    print("9. Exit")


# Function to display sales data
def view_sales_data():
    cursor.execute("SELECT * FROM Sales")
    rows = cursor.fetchall()

    if not rows:
        print("No sales data available.")
        return

    # Create a PrettyTable and add columns
    table = PrettyTable()
    table.field_names = ["Sale ID", "Product ID", "Quantity Sold", "Sale Date"]

    # Add rows to the table
    for row in rows:
        table.add_row(row)

    # Print the table
    print(table)


# Function to generate reorder alerts
def generate_reorder_alerts():
    cursor.execute('''
        SELECT ProductID, ProductName, QuantityInStock, ReorderLevel
        FROM Product
        WHERE QuantityInStock <= ReorderLevel
    ''')

    rows = cursor.fetchall()

    if not rows:
        print("No products need to be reordered.")
        return

    # Create a PrettyTable and add columns
    table = PrettyTable()
    table.field_names = ["Product ID", "Name", "Stock", "Reorder Level"]

    # Add rows to the table
    for row in rows:
        table.add_row(row)

    # Print the table
    print(table)


# Function to add a new product
def add_product():
    print("\nEnter details for the new product:")
    product_name = input("Product Name: ")
    quantity_in_stock = int(input("Quantity in Stock: "))
    reorder_level = int(input("Reorder Level: "))
    cost_per_unit = float(input("Cost Per Unit: "))
    unit_price = float(input("Unit Price: "))

    cursor.execute('''
        INSERT INTO Product (ProductName, QuantityInStock, ReorderLevel, UnitPrice, CostPerUnit)
        VALUES (?, ?, ?, ?, ?)
    ''', (product_name, quantity_in_stock, reorder_level, unit_price, cost_per_unit))

    conn.commit()
    print("Product added successfully.")


# Function to add sales data
def add_sales():
    console = Console()

    # Get user input for sales data
    while True:
        product_id = input("Enter the Product ID for the product sold: ")

        # Check if there's enough quantity in stock
        cursor.execute('''
                SELECT QuantityInStock
                FROM Product
                WHERE ProductID = ?
            ''', (product_id,))
        product = cursor.fetchone()

        if not product:
            console.print(f"Product with Product ID {product_id} does not exist. Please enter a valid Product ID.")
        else:
            break

    while True:
        quantity_sold_str = input("Enter the quantity sold: ")

        current_quantity = product[0]

        if not quantity_sold_str.isdigit():
            console.print("Invalid input. Please enter a valid integer for the quantity sold.")

        else:
            quantity_sold = int(quantity_sold_str)
            if quantity_sold > current_quantity:
                print(
                    f"Error: Quantity in stock ({current_quantity}) is less than quantity sold ({quantity_sold}).")
                return
            break

    while True:
        sale_date_str = input("Enter the sale date (press Enter for today or YYYY-MM-DD): ")

        if not sale_date_str:
            sale_date = datetime.date.today()
            break
        else:
            try:
                sale_date = datetime.datetime.strptime(sale_date_str, "%Y-%m-%d").date()
                break
            except ValueError:
                console.print("Invalid date format. Please use YYYY-MM-DD.")

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
    console.print("Sales data added successfully.")


# Function to update a product
def update_product():
    print("\nEnter the details to update the product:")
    product_id = int(input("Product ID: "))
    new_quantity = int(input("New Quantity in Stock: "))
    new_reorder_level = int(input("New Reorder Level: "))
    new_unit_price = float(input("New Unit Price: "))
    new_cost_per_unit = float(input("New Cost Per Unit: "))

    cursor.execute('''
        UPDATE Product
        SET QuantityInStock = ?,
            ReorderLevel = ?,
            UnitPrice = ?,
            CostPerUnit = ?
        WHERE ProductID = ?
    ''', (new_quantity, new_reorder_level, new_unit_price, new_cost_per_unit, product_id))

    conn.commit()
    print("Product updated successfully.")


# Function to delete a product
def delete_product():
    product_id = int(input("\nEnter the Product ID to delete: "))

    # Delete associated sales data
    cursor.execute('''
            DELETE FROM Sales
            WHERE ProductID = ?
        ''', (product_id,))

    cursor.execute('''
        DELETE FROM Product
        WHERE ProductID = ?
    ''', (product_id,))

    conn.commit()
    print("Product and associated sales data deleted successfully.")


# Function to generate reports
def generate_reports():
    print("\nGenerating Reports:")

    cursor.execute('''
        SELECT Product.ProductID, Product.ProductName, SUM(Sales.QuantitySold) as TotalSales
        FROM Product
        LEFT JOIN Sales ON Product.ProductID = Sales.ProductID
        GROUP BY Product.ProductID
    ''')

    rows = cursor.fetchall()

    if not rows:
        print("No sales data available for generating reports.")
        return

    # Create a PrettyTable and add columns
    table = PrettyTable()
    table.field_names = ["Product ID", "Name", "Total Sales"]

    # Add rows to the table
    for row in rows:
        table.add_row(row)

    # Print the table
    print(table)

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

    # Display the report
    print(f"Total Revenue: ${total_revenue:.2f}")
    print(f"Total Cost of Goods Sold: ${total_cogs:.2f}")
    print(f"Overall Profit Margin: {overall_profit_margin:.2f}%")


# Function to clear the screen and wait for a key press
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')
    input("Press any key to continue...")


# Main loop
while True:
    display_menu()
    choice = input("Enter your choice (1-9): ")

    # Implement the functionality for each menu option
    if choice == "1":
        # View Stock Levels
        view_stock_levels()
        clear_screen()
    elif choice == "2":
        # View Sales Data
        view_sales_data()
        clear_screen()
    elif choice == "3":
        # Generate Reorder Alerts
        generate_reorder_alerts()
        clear_screen()
    elif choice == "4":
        # Generate Reports
        generate_reports()
        clear_screen()
    elif choice == "5":
        # Add Product
        add_product()
        clear_screen()
    elif choice == "6":
        # Update Product
        update_product()
        clear_screen()
    elif choice == "7":
        # Delete Product
        delete_product()
        clear_screen()
    elif choice == "8":
        # Add Sales
        add_sales()
        clear_screen()
    elif choice == "9":
        # Exit
        break
    else:
        print("Invalid choice. Please enter a number from 1 to 9.\n")
