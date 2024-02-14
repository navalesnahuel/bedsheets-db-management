import psycopg2
import sys
import os
configs_parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(configs_parent_dir)
from Configs.postgres_connection import postgres_conn

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def search_customer_id_by_name(cursor, customer_name):
    cursor.execute("SELECT customer_id FROM Customers WHERE name = %s", (customer_name,))
    result = cursor.fetchone()
    if result:
        return result[0]  
    else:
        return None  

def product_id_search():
    clear_screen()
    conn, cursor = postgres_conn('./Configs/connection.txt')
    materials = {1: 'Algodón', 2: 'Poliéster', 3: 'Microfibra', 4: 'Algodón y Poliéster', 5: 'Percal', 6: 'Ultra Soft'}
    product_types = {1: 'Sábanas', 2: 'Juegos de Sábanas', 3: 'Funda de Colchón'}
    sizes = {1: '1 1/2 Plaza', 2: '2 1/2 Plazas', 3: 'King', 4: 'Queen', 5: '2 Plazas', 6: '1 Plaza'}

    print("------ Especificaciones del Producto ------")

    # Selección de Categoría
    print("\nSeleccione la categoría del producto:")
    for num, product_type in product_types.items():
        print(f"{num}. {product_type}")
    while True:
        try:
            product_type_num = int(input('\u25CF Elija el número correspondiente al tipo de producto: '))
            if product_type_num in product_types:
                break
            else:
                print('\u25CF Número inválido. Por favor, elija entre las opciones proporcionadas.')
        except ValueError:
            print("\u25CF Por favor, ingrese un número válido.")
    
    category = product_types.get(product_type_num)
    clear_screen()

    # Selección de Material
    print("------ Especificaciones del Producto ------")
    print("\nSeleccione el material del producto:")
    for num, material in materials.items():
        print(f"{num}. {material}")
    while True:
        try:
            material_num = int(input('\u25CF Elija el número correspondiente al material del producto: '))
            if material_num in materials:
                break
            else:
                print('\u25CF Número inválido. Por favor, elija entre las opciones proporcionadas.')
        except ValueError:
            print("\u25CF Por favor, ingrese un número válido.")

    material = materials.get(material_num)
    clear_screen()

    # Selección de Tamaño
    print("------ Especificaciones del Producto ------")
    print("\nSeleccione el tamaño del producto:")
    for num, size in sizes.items():
        print(f"{num}. {size}")
    while True:
        try:
            size_num = int(input('\u25CF Elija el número correspondiente al tamaño del producto: '))
            if size_num in sizes:
                break
            else:
                print('\u25CF Número inválido. Por favor, elija entre las opciones proporcionadas.')
        except ValueError:
            print("\u25CFPor favor, ingrese un número válido.")

    size = sizes.get(size_num)
    clear_screen()

    # Imprimir Producto Seleccionado
    print(f"\nProducto Seleccionado: {category} - {material} - {size}")

    cursor.execute("""
        SELECT * FROM (
            SELECT product_id, stock_no, s.name AS size, c.name AS category, m.name AS material
            FROM products p
            JOIN sizes s ON s.size_id = p.size_id
            JOIN categories c ON c.category_id = p.category_id 
            JOIN materials m ON m.material_id = p.material_id
        ) a
        WHERE category = %s AND size = %s AND material = %s
    """, (category, size, material))

    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        return None

def manually_populate_customers():
    conn, cursor = postgres_conn("./Configs/connection.txt")
    insert_values = []

    clear_screen()

    customer_name = input("\u25CF Ingrese el nombre del cliente: ").lower().title() 
    email = input("\u25CF Ingrese el correo electrónico: ").lower()
    address = input("\u25CF Ingrese la dirección: ").lower().capitalize()
    phone = input("\u25CF Ingrese el número de teléfono: ").replace(" ", "")  

    clear_screen()

    cursor.execute("SELECT COUNT(*) FROM Customers WHERE name = %s", (customer_name,))
    count = cursor.fetchone()[0]

    if count > 0:
        print(f"El cliente con el nombre '{customer_name}' ya existe. Abortando la inserción.")
        input("Enter para seguir operando")
        return

    insert_values.append((customer_name, email, address, phone))

    for value in insert_values:
        print(f'\nNombre del Cliente: {value[0]}\nCorreo Electrónico: {value[1]}\nDirección: {value[2]}\nTeléfono: {value[3]}')
     
    while True:
        confirmation1 = input("\n\u25CF Por favor, verifique si los datos son correctos - [S/N]: ").lower() 
        if confirmation1 not in ['s', 'n']:
            print("Entrada inválida")
            continue

        if confirmation1 == 'n':
            return 'no_data'

        if confirmation1 == 's':
            while True:
                confirmation2 = input("\u25CF Por favor, confirme para agregar los datos - [S/N]: ").lower() 
                if confirmation2 not in ['s', 'n']:
                    print("Entrada inválida")
                    continue
                elif confirmation2 == 'n':
                    break
                elif confirmation2 == 's':
                    for values in insert_values:
                        cursor.execute("""
                            INSERT INTO Customers (name, email, address, phone) 
                            VALUES (%s, %s, %s, %s)
                        """, values)
                    conn.commit() 
                    print("\u2605 Datos agregados exitosamente a la tabla.")
                    input("Enter para seguir operando")               
                    return values[0]
            break

def manually_populate_orders():
    conn, cursor = postgres_conn('./Configs/connection.txt')

    # Obtener el nombre del cliente
    customer_name = input('Ingrese el nombre del cliente: ').lower().title()
    customer_id = search_customer_id_by_name(cursor, customer_name)

    # Verificar si el cliente existe
    if customer_id is None:
        print('El cliente no existe.')
        answer = input('\n\u25CF ¿Desea crear un cliente? [S/N]: ').lower()
        if answer == 's': 
            result = manually_populate_customers()
            if result == 'no_data':
                input ("Enter para volver al menu")
                return
            else:
                customer_id = search_customer_id_by_name(cursor, result)
        elif answer == 'n':
            input ("Enter para volver al menu")
            return
        else:
            print('\nEntrada inválida')

    # Buscar el ID del producto
    product_id = product_id_search()
    cursor.execute("SELECT cost_price FROM Products WHERE product_id = %s", (product_id,))
    result = cursor.fetchone()
    unit_price = round(float(result[0]) * 1.67, 2)

    # Solicitar la cantidad de productos
    while True:
        quantity_input = input('\n[SALIR para detener el script]\n\u25CF Cantidad de productos: ').lower()
        if quantity_input == 'salir':
            input ("Enter para volver al menu")
            return
        try:
            quantity = int(quantity_input)
            cursor.execute("SELECT stock_no FROM Products WHERE product_id = %s", (product_id,))
            result = cursor.fetchone()
            if result:
                stock_no = result[0]
                if quantity <= stock_no:
                    break
                else:
                    print(f"\nStock insuficiente. Cantidad disponible: {stock_no}")
            else:
                print("\nProducto no encontrado.")
        except ValueError:
            print("[SALIR para detener el script]\n\u25CF Entrada inválida. Por favor, ingrese una cantidad válida")

    # Insertar la orden en la base de datos y actualizar la cantidad de stock
    cursor.execute("""
        INSERT INTO Orders (customer_id, product_id, quantity, unit_price) 
        VALUES (%s, %s, %s, %s)
        """, (customer_id, product_id, quantity, unit_price))
    conn.commit() 

    new_stock_quantity = stock_no - quantity
    cursor.execute("""
        UPDATE Products 
        SET stock_no = %s
        WHERE product_id = %s
        """, (new_stock_quantity, product_id))
    conn.commit() 

    print(f"\n\u2713 Pedido agregado exitosamente a Ordenes. Cantidad de stock actualizada: {new_stock_quantity}")
    input ("Enter para volver al menu")

def add_stock():
    conn, cursor = postgres_conn('./Configs/connection.txt')
    product_id = product_id_search()
    clear_screen()

    while True:
        new_stock_input = input(f"ID de Producto = {product_id}. Ingrese la nueva cantidad de stock (o 'salir' para salir): ")

        if new_stock_input.lower() == 'salir':
            input ("Enter para volver al menu")
            break

        if not new_stock_input.isdigit():
            print("Por favor, ingrese un número entero válido.")
            continue

        new_stock_input = int(new_stock_input)
        confirmation = input(f"Por favor, confirme que {new_stock_input} es la cantidad de productos que desea agregar al stock [S/N] ").lower()
        
        if confirmation == 's':
            cursor.execute("SELECT stock_no FROM products WHERE product_id = %s", (product_id,))
            result = cursor.fetchone()
            
            if result:
                stock_no = result[0]
                new_stock_quantity = stock_no + new_stock_input
                
                cursor.execute("UPDATE Products SET stock_no = %s WHERE product_id = %s", (new_stock_quantity, product_id))
                conn.commit() 
                
                print(f"\n\u2713 Cantidad de stock actualizada: {new_stock_quantity} para el Producto: {product_id}")
                input ("Enter para volver al menu")
            else:
                print("Producto no encontrado.")
                input ("Enter para volver al menu")
                
            break
        
        elif confirmation == 'n':
            input ("Enter para volver al menu")
            continue
        
        else:
            print("Entrada inválida. Por favor, ingrese 'S' para confirmar o 'N' para cancelar.")

    cursor.close()
    conn.close()