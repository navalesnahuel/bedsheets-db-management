import sys
import os
configs_parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(configs_parent_dir)
from Configs.postgres_connection import postgres_conn
import psycopg2
from tabulate import tabulate
import random
from faker import Faker

def dummy_populate_tables():
    conn, cursor = postgres_conn('./Configs/connection.txt')

    fake = Faker('es_AR')
    for _ in range(random.randint(76, 135)):
        name = (f'{fake.first_name()} {fake.last_name()}')

        email = f"{name.split()[0]}{name.split()[-1]}@gmail.com".lower()

        temp_num = (fake.unique.phone_number())
        phone = f'11{temp_num.split()[-2]}{temp_num.split()[-1]}'

        address = fake.unique.street_address()

        cursor.execute ("""INSERT INTO customers (name, email, address, phone) 
                        VALUES (%s, %s, %s, %s)""", (name, email, address, phone))

        conn.commit()

    # Fetching customer IDs
    cursor.execute("SELECT customer_id FROM Customers")
    customer_ids = [row[0] for row in cursor.fetchall()]

    # Fetching products and their seventy percent stock
    cursor.execute("""
                    SELECT product_id, seventy_percent::INTEGER 
                    FROM (
                        SELECT product_id, 
                               CASE
                                   WHEN stock_no <> 0 THEN round(0.70 * stock_no)
                                   ELSE null
                               END AS seventy_percent
                        FROM products
                    ) a
                """)
    products = cursor.fetchall()

    for product_id, sold_stock in products:
        if sold_stock is not None:
            # Fetch unit price
            cursor.execute("SELECT cost_price FROM Products WHERE product_id = %s", (product_id,))
            unit_price = round(float(cursor.fetchone()[0]) * 1.67, 2)

            # Generate random number of orders within available stock
            remaining_stock = sold_stock
            
            for _ in range(sold_stock):
                # Check if remaining stock is greater than 0
                if remaining_stock <= 0:
                    break

                random_customer_id = random.choice(customer_ids)
                # Generate random order quantity for each order
                order_quantity = random.randint(1, remaining_stock)
                
                # Insert order into the database
                cursor.execute("""
                    INSERT INTO Orders (customer_id, product_id, quantity, unit_price) 
                    VALUES (%s, %s, %s, %s)
                    """, (random_customer_id, product_id, order_quantity, unit_price))
                conn.commit()

                # Update remaining stock
                remaining_stock -= order_quantity
            
            # Update stock_no in Products table
            cursor.execute("UPDATE Products SET stock_no = stock_no - %s WHERE product_id = %s", (sold_stock, product_id))
            conn.commit()
    print("Tablas cargadas con exito")
    input("Enter para volver al menu: ")

    cursor.close()
    conn.close()



