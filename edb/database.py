import psycopg2
from datetime import datetime
import sys

class Database:
    def __init__(self, host, port, user, password, database):
        self.connection_params = {
            'host': host,
            'port': port,
            'user': user,
            'password': password,
            'database': database
        }
        self._create_tables()
    
    def _get_connection(self):
        try:
            return psycopg2.connect(**self.connection_params)
        except Exception as e:
            print(f"Ошибка подключения к БД: {e}")
            raise
    
    def _create_tables(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Таблица складов
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS warehouses (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(200) NOT NULL,
                    address VARCHAR(300) NOT NULL
                )
            ''')
            
            # Таблица сотрудников 
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS employees (
                    id SERIAL PRIMARY KEY,
                    login VARCHAR(100) UNIQUE NOT NULL,
                    password VARCHAR(100) NOT NULL,
                    full_name VARCHAR(200) NOT NULL,
                    role VARCHAR(50) NOT NULL,
                    phone VARCHAR(20),
                    email VARCHAR(100),
                    warehouse_id INTEGER REFERENCES warehouses(id)
                )
            ''')
            
            # Таблица товаров
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(200) NOT NULL,
                    category VARCHAR(100) NOT NULL,
                    brand VARCHAR(100),
                    price DECIMAL(10, 2) NOT NULL,
                    min_quantity INTEGER NOT NULL DEFAULT 0
                )
            ''')
            
            # Таблица наличия товаров на складах
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS product_warehouse (
                    id SERIAL PRIMARY KEY,
                    product_id INTEGER REFERENCES products(id),
                    warehouse_id INTEGER REFERENCES warehouses(id),
                    quantity INTEGER NOT NULL DEFAULT 0,
                    UNIQUE(product_id, warehouse_id)
                )
            ''')
            
            # Таблица продаж
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sales (
                    id SERIAL PRIMARY KEY,
                    product_id INTEGER REFERENCES products(id),
                    quantity INTEGER NOT NULL,
                    total_price DECIMAL(10, 2) NOT NULL,
                    sale_date TIMESTAMP NOT NULL,
                    cashier_id INTEGER REFERENCES employees(id),
                    warehouse_id INTEGER REFERENCES warehouses(id),
                    status VARCHAR(20) DEFAULT 'completed'
                )
            ''')
            
            # НОВАЯ ТАБЛИЦА: Клиенты
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS customers (
                    id SERIAL PRIMARY KEY,
                    full_name VARCHAR(200) NOT NULL,
                    phone VARCHAR(20) NOT NULL,
                    email VARCHAR(100),
                    address TEXT NOT NULL,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # НОВАЯ ТАБЛИЦА: Доставки
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS deliveries (
                    id SERIAL PRIMARY KEY,
                    sale_id INTEGER REFERENCES sales(id),
                    customer_id INTEGER REFERENCES customers(id),
                    delivery_address TEXT NOT NULL,
                    status VARCHAR(50) DEFAULT 'pending', -- pending, assigned, in_progress, delivered, cancelled
                    assigned_storekeeper_id INTEGER REFERENCES employees(id),
                    delivery_date TIMESTAMP,
                    notes TEXT,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # НОВАЯ ТАБЛИЦА: Группы доставки (несколько заказов в одной машине)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS delivery_groups (
                    id SERIAL PRIMARY KEY,
                    storekeeper_id INTEGER REFERENCES employees(id),
                    vehicle_info VARCHAR(200),
                    status VARCHAR(50) DEFAULT 'preparing', -- preparing, in_progress, completed
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_date TIMESTAMP
                )
            ''')
            
            # НОВАЯ ТАБЛИЦА: Связь доставок с группами
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS delivery_group_items (
                    id SERIAL PRIMARY KEY,
                    delivery_group_id INTEGER REFERENCES delivery_groups(id),
                    delivery_id INTEGER REFERENCES deliveries(id),
                    UNIQUE(delivery_id)
                )
            ''')
            
            # Добавляем основной склад по умолчанию
            cursor.execute("SELECT COUNT(*) FROM warehouses")
            if cursor.fetchone()[0] == 0:
                cursor.execute(
                    "INSERT INTO warehouses (name, address) VALUES (%s, %s) RETURNING id",
                    ('Основной склад', 'Главный адрес склада')
                )
                main_warehouse_id = cursor.fetchone()[0]
                
            # Добавляем администратора по умолчанию
            cursor.execute("SELECT COUNT(*) FROM employees WHERE role = 'admin'")
            if cursor.fetchone()[0] == 0:
                cursor.execute(
                    "INSERT INTO employees (login, password, full_name, role, warehouse_id) VALUES (%s, %s, %s, %s, %s)",
                    ('admin', 'admin123', 'Администратор', 'admin', main_warehouse_id)
                )
                
            # Добавляем кассира по умолчанию
            cursor.execute("SELECT COUNT(*) FROM employees WHERE role = 'cashier'")
            if cursor.fetchone()[0] == 0:
                cursor.execute(
                    "INSERT INTO employees (login, password, full_name, role, warehouse_id) VALUES (%s, %s, %s, %s, %s)",
                    ('cashier', 'cashier123', 'Кассир', 'cashier', main_warehouse_id)
                )
                
            # Добавляем кладовщика по умолчанию
            cursor.execute("SELECT COUNT(*) FROM employees WHERE role = 'storekeeper'")
            if cursor.fetchone()[0] == 0:
                cursor.execute(
                    "INSERT INTO employees (login, password, full_name, role, warehouse_id) VALUES (%s, %s, %s, %s, %s)",
                    ('storekeeper', 'storekeeper123', 'Работник склада', 'storekeeper', main_warehouse_id)
                )
            
            conn.commit()
            print("Таблицы успешно созданы/проверены")
            
        except Exception as e:
            print(f"Ошибка при создании таблиц: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def create_customer(self, full_name, phone, email, address):
        """Создает нового клиента"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO customers (full_name, phone, email, address)
                VALUES (%s, %s, %s, %s)
            ''', (full_name, phone, email, address))
            conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка создания клиента: {e}")
            return False
        finally:
            conn.close()
    
    def get_customer_by_phone(self, phone):
        """Находит клиента по телефону"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT id, full_name, phone, email, address 
                FROM customers 
                WHERE phone = %s
            ''', (phone,))
            result = cursor.fetchone()
            
            if result:
                return {
                    'id': result[0],
                    'full_name': result[1],
                    'phone': result[2],
                    'email': result[3],
                    'address': result[4]
                }
            return None
        except Exception as e:
            print(f"Ошибка поиска клиента: {e}")
            return None
        finally:
            conn.close()
    
    def get_all_customers(self):
        """Получает всех клиентов"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT id, full_name, phone, email, address, created_date
                FROM customers 
                ORDER BY created_date DESC
            ''')
            customers = cursor.fetchall()
            
            result = []
            for customer in customers:
                result.append({
                    'id': customer[0],
                    'full_name': customer[1],
                    'phone': customer[2],
                    'email': customer[3],
                    'address': customer[4],
                    'created_date': customer[5].strftime("%Y-%m-%d %H:%M:%S")
                })
            return result
        except Exception as e:
            print(f"Ошибка получения клиентов: {e}")
            return []
        finally:
            conn.close()
    
    def get_customer_by_id(self, customer_id):
        """Получает клиента по ID"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT id, full_name, phone, email, address 
                FROM customers 
                WHERE id = %s
            ''', (customer_id,))
            result = cursor.fetchone()
            
            if result:
                return {
                    'id': result[0],
                    'full_name': result[1],
                    'phone': result[2],
                    'email': result[3],
                    'address': result[4]
                }
            return None
        except Exception as e:
            print(f"Ошибка получения клиента: {e}")
            return None
        finally:
            conn.close()
    
    def update_customer(self, customer_id, full_name, phone, email, address):
        """Обновляет данные клиента"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                UPDATE customers 
                SET full_name = %s, phone = %s, email = %s, address = %s
                WHERE id = %s
            ''', (full_name, phone, email, address, customer_id))
            conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка обновления клиента: {e}")
            return False
        finally:
            conn.close()
    
    def delete_customer(self, customer_id):
        """Удаляет клиента"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM customers WHERE id = %s", (customer_id,))
            conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка удаления клиента: {e}")
            return False
        finally:
            conn.close()
    
    def create_delivery(self, sale_id, customer_id, delivery_address, notes=''):
        """Создает доставку для продажи"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO deliveries (sale_id, customer_id, delivery_address, notes)
                VALUES (%s, %s, %s, %s)
            ''', (sale_id, customer_id, delivery_address, notes))
            conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка создания доставки: {e}")
            return False
        finally:
            conn.close()
    
    def get_pending_deliveries(self, warehouse_id=None):
        """Получает ожидающие доставки"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            if warehouse_id:
                cursor.execute('''
                    SELECT d.id, d.delivery_address, d.status, d.created_date,
                           c.full_name, c.phone, c.email,
                           p.name as product_name, s.quantity,
                           e.full_name as cashier_name,
                           w.name as warehouse_name
                    FROM deliveries d
                    JOIN customers c ON d.customer_id = c.id
                    JOIN sales s ON d.sale_id = s.id
                    JOIN products p ON s.product_id = p.id
                    JOIN employees e ON s.cashier_id = e.id
                    JOIN warehouses w ON s.warehouse_id = w.id
                    WHERE d.status = 'pending' AND s.warehouse_id = %s
                    ORDER BY d.created_date
                ''', (warehouse_id,))
            else:
                cursor.execute('''
                    SELECT d.id, d.delivery_address, d.status, d.created_date,
                           c.full_name, c.phone, c.email,
                           p.name as product_name, s.quantity,
                           e.full_name as cashier_name,
                           w.name as warehouse_name
                    FROM deliveries d
                    JOIN customers c ON d.customer_id = c.id
                    JOIN sales s ON d.sale_id = s.id
                    JOIN products p ON s.product_id = p.id
                    JOIN employees e ON s.cashier_id = e.id
                    JOIN warehouses w ON s.warehouse_id = w.id
                    WHERE d.status = 'pending'
                    ORDER BY d.created_date
                ''')
            
            deliveries = cursor.fetchall()
            
            result = []
            for delivery in deliveries:
                result.append({
                    'id': delivery[0],
                    'delivery_address': delivery[1],
                    'status': delivery[2],
                    'created_date': delivery[3].strftime("%Y-%m-%d %H:%M:%S"),
                    'customer_name': delivery[4],
                    'customer_phone': delivery[5],
                    'customer_email': delivery[6],
                    'product_name': delivery[7],
                    'quantity': delivery[8],
                    'cashier_name': delivery[9],
                    'warehouse_name': delivery[10]
                })
            return result
        except Exception as e:
            print(f"Ошибка получения доставок: {e}")
            return []
        finally:
            conn.close()
    
    def get_all_deliveries(self, warehouse_id=None):
        """Получает все доставки"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            if warehouse_id:
                cursor.execute('''
                    SELECT d.id, d.delivery_address, d.status, d.created_date, d.delivery_date,
                           c.full_name, c.phone, c.email,
                           p.name as product_name, s.quantity,
                           e.full_name as cashier_name, emp.full_name as storekeeper_name,
                           w.name as warehouse_name, dg.vehicle_info
                    FROM deliveries d
                    JOIN customers c ON d.customer_id = c.id
                    JOIN sales s ON d.sale_id = s.id
                    JOIN products p ON s.product_id = p.id
                    JOIN employees e ON s.cashier_id = e.id
                    LEFT JOIN employees emp ON d.assigned_storekeeper_id = emp.id
                    LEFT JOIN delivery_group_items dgi ON d.id = dgi.delivery_id
                    LEFT JOIN delivery_groups dg ON dgi.delivery_group_id = dg.id
                    JOIN warehouses w ON s.warehouse_id = w.id
                    WHERE s.warehouse_id = %s
                    ORDER BY d.created_date DESC
                ''', (warehouse_id,))
            else:
                cursor.execute('''
                    SELECT d.id, d.delivery_address, d.status, d.created_date, d.delivery_date,
                           c.full_name, c.phone, c.email,
                           p.name as product_name, s.quantity,
                           e.full_name as cashier_name, emp.full_name as storekeeper_name,
                           w.name as warehouse_name, dg.vehicle_info
                    FROM deliveries d
                    JOIN customers c ON d.customer_id = c.id
                    JOIN sales s ON d.sale_id = s.id
                    JOIN products p ON s.product_id = p.id
                    JOIN employees e ON s.cashier_id = e.id
                    LEFT JOIN employees emp ON d.assigned_storekeeper_id = emp.id
                    LEFT JOIN delivery_group_items dgi ON d.id = dgi.delivery_id
                    LEFT JOIN delivery_groups dg ON dgi.delivery_group_id = dg.id
                    JOIN warehouses w ON s.warehouse_id = w.id
                    ORDER BY d.created_date DESC
                ''')
            
            deliveries = cursor.fetchall()
            
            result = []
            for delivery in deliveries:
                result.append({
                    'id': delivery[0],
                    'delivery_address': delivery[1],
                    'status': delivery[2],
                    'created_date': delivery[3].strftime("%Y-%m-%d %H:%M:%S"),
                    'delivery_date': delivery[4].strftime("%Y-%m-%d %H:%M:%S") if delivery[4] else '',
                    'customer_name': delivery[5],
                    'customer_phone': delivery[6],
                    'customer_email': delivery[7],
                    'product_name': delivery[8],
                    'quantity': delivery[9],
                    'cashier_name': delivery[10],
                    'storekeeper_name': delivery[11] or 'Не назначен',
                    'warehouse_name': delivery[12],
                    'vehicle_info': delivery[13] or 'Не назначен'
                })
            return result
        except Exception as e:
            print(f"Ошибка получения доставок: {e}")
            return []
        finally:
            conn.close()
    
    def assign_delivery_to_storekeeper(self, delivery_id, storekeeper_id):
        """Назначает доставку кладовщику"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                UPDATE deliveries 
                SET assigned_storekeeper_id = %s, status = 'assigned'
                WHERE id = %s
            ''', (storekeeper_id, delivery_id))
            conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка назначения доставки: {e}")
            return False
        finally:
            conn.close()
    
    def create_delivery_group(self, storekeeper_id, vehicle_info):
        """Создает группу доставки"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO delivery_groups (storekeeper_id, vehicle_info)
                VALUES (%s, %s)
                RETURNING id
            ''', (storekeeper_id, vehicle_info))
            group_id = cursor.fetchone()[0]
            conn.commit()
            return group_id
        except Exception as e:
            print(f"Ошибка создания группы доставки: {e}")
            return None
        finally:
            conn.close()
    
    def add_delivery_to_group(self, delivery_group_id, delivery_id):
        """Добавляет доставку в группу"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO delivery_group_items (delivery_group_id, delivery_id)
                VALUES (%s, %s)
            ''', (delivery_group_id, delivery_id))
            
            cursor.execute('''
                UPDATE deliveries 
                SET status = 'in_progress'
                WHERE id = %s
            ''', (delivery_id,))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка добавления доставки в группу: {e}")
            return False
        finally:
            conn.close()
    
    def complete_delivery(self, delivery_id):
        """Завершает доставку"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                UPDATE deliveries 
                SET status = 'delivered', delivery_date = CURRENT_TIMESTAMP
                WHERE id = %s
            ''', (delivery_id,))
            conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка завершения доставки: {e}")
            return False
        finally:
            conn.close()
    
    def complete_delivery_group(self, delivery_group_id):
        """Завершает группу доставки"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                UPDATE delivery_groups 
                SET status = 'completed', completed_date = CURRENT_TIMESTAMP
                WHERE id = %s
            ''', (delivery_group_id,))
            conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка завершения группы доставки: {e}")
            return False
        finally:
            conn.close()
    
    def get_delivery_groups(self, storekeeper_id=None):
        """Получает группы доставки"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            if storekeeper_id:
                cursor.execute('''
                    SELECT dg.id, dg.vehicle_info, dg.status, dg.created_date, dg.completed_date,
                           e.full_name as storekeeper_name,
                           COUNT(dgi.delivery_id) as delivery_count
                    FROM delivery_groups dg
                    JOIN employees e ON dg.storekeeper_id = e.id
                    LEFT JOIN delivery_group_items dgi ON dg.id = dgi.delivery_group_id
                    WHERE dg.storekeeper_id = %s
                    GROUP BY dg.id, dg.vehicle_info, dg.status, dg.created_date, dg.completed_date, e.full_name
                    ORDER BY dg.created_date DESC
                ''', (storekeeper_id,))
            else:
                cursor.execute('''
                    SELECT dg.id, dg.vehicle_info, dg.status, dg.created_date, dg.completed_date,
                           e.full_name as storekeeper_name,
                           COUNT(dgi.delivery_id) as delivery_count
                    FROM delivery_groups dg
                    JOIN employees e ON dg.storekeeper_id = e.id
                    LEFT JOIN delivery_group_items dgi ON dg.id = dgi.delivery_group_id
                    GROUP BY dg.id, dg.vehicle_info, dg.status, dg.created_date, dg.completed_date, e.full_name
                    ORDER BY dg.created_date DESC
                ''')
            
            groups = cursor.fetchall()
            
            result = []
            for group in groups:
                result.append({
                    'id': group[0],
                    'vehicle_info': group[1],
                    'status': group[2],
                    'created_date': group[3].strftime("%Y-%m-%d %H:%M:%S"),
                    'completed_date': group[4].strftime("%Y-%m-%d %H:%M:%S") if group[4] else '',
                    'storekeeper_name': group[5],
                    'delivery_count': group[6]
                })
            return result
        except Exception as e:
            print(f"Ошибка получения групп доставки: {e}")
            return []
        finally:
            conn.close()
    
    def get_deliveries_in_group(self, delivery_group_id):
        """Получает доставки в группе"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT d.id, d.delivery_address, d.status,
                       c.full_name, c.phone,
                       p.name as product_name, s.quantity
                FROM deliveries d
                JOIN delivery_group_items dgi ON d.id = dgi.delivery_id
                JOIN customers c ON d.customer_id = c.id
                JOIN sales s ON d.sale_id = s.id
                JOIN products p ON s.product_id = p.id
                WHERE dgi.delivery_group_id = %s
            ''', (delivery_group_id,))
            
            deliveries = cursor.fetchall()
            
            result = []
            for delivery in deliveries:
                result.append({
                    'id': delivery[0],
                    'delivery_address': delivery[1],
                    'status': delivery[2],
                    'customer_name': delivery[3],
                    'customer_phone': delivery[4],
                    'product_name': delivery[5],
                    'quantity': delivery[6]
                })
            return result
        except Exception as e:
            print(f"Ошибка получения доставок в группе: {e}")
            return []
        finally:
            conn.close()
           
    def authenticate_user(self, username, password):
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT e.id, e.full_name, e.role, e.warehouse_id, w.name as warehouse_name
                FROM employees e
                LEFT JOIN warehouses w ON e.warehouse_id = w.id
                WHERE e.login = %s AND e.password = %s
            ''', (username, password))
            result = cursor.fetchone()
            
            if result:
                return {
                    'id': result[0],
                    'full_name': result[1],
                    'role': result[2],
                    'warehouse_id': result[3],
                    'warehouse_name': result[4]
                }
            return None
        except Exception as e:
            print(f"Ошибка аутентификации: {e}")
            return None
        finally:
            conn.close()
    
    def register_employee(self, login, password, full_name, role, warehouse_id, phone=' ', email=' '):
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO employees (login, password, full_name, role, warehouse_id, phone, email)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (login, password, full_name, role, warehouse_id, phone, email))
            conn.commit()
            return True
        except psycopg2.IntegrityError:
            return False
        except Exception as e:
            print(f"Ошибка регистрации: {e}")
            return False
        finally:
            conn.close()
    
    def get_all_warehouses(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id, name, address FROM warehouses ORDER BY id")
            warehouses = cursor.fetchall()
            
            result = []
            for warehouse in warehouses:
                result.append({
                    'id': warehouse[0],
                    'name': warehouse[1],
                    'address': warehouse[2]
                })
            return result
        except Exception as e:
            print(f"Ошибка получения складов: {e}")
            return []
        finally:
            conn.close()
    
    def add_warehouse(self, name, address):
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO warehouses (name, address) VALUES (%s, %s)",
                (name, address)
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка добавления склада: {e}")
            return False
        finally:
            conn.close()
    
    def get_products_with_quantity(self, warehouse_id=None):
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            if warehouse_id:
                # Товары с количеством на конкретном складе
                cursor.execute('''
                    SELECT p.id, p.name, p.category, p.brand, p.price, p.min_quantity,
                           COALESCE(pw.quantity, 0) as quantity
                    FROM products p
                    LEFT JOIN product_warehouse pw ON p.id = pw.product_id AND pw.warehouse_id = %s
                    ORDER BY p.id
                ''', (warehouse_id,))
            else:
                # Товары с общим количеством по всем складам
                cursor.execute('''
                    SELECT p.id, p.name, p.category, p.brand, p.price, p.min_quantity,
                           COALESCE(SUM(pw.quantity), 0) as quantity
                    FROM products p
                    LEFT JOIN product_warehouse pw ON p.id = pw.product_id
                    GROUP BY p.id, p.name, p.category, p.brand, p.price, p.min_quantity
                    ORDER BY p.id
                ''')
            
            products = cursor.fetchall()
            
            result = []
            for product in products:
                result.append({
                    'id': product[0],
                    'name': product[1],
                    'category': product[2],
                    'brand': product[3],
                    'price': float(product[4]),
                    'min_quantity': product[5],
                    'quantity': product[6]
                })
            return result
        except Exception as e:
            print(f"Ошибка получения товаров: {e}")
            return []
        finally:
            conn.close()
    
    def add_product(self, name, category, brand, price, min_quantity):
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO products (name, category, brand, price, min_quantity)
                VALUES (%s, %s, %s, %s, %s)
            ''', (name, category, brand, price, min_quantity))
            conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка добавления товара: {e}")
            return False
        finally:
            conn.close()
    
    def update_product_quantity(self, product_id, warehouse_id, new_quantity):
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            # Проверяем существует ли запись
            cursor.execute('''
                SELECT COUNT(*) FROM product_warehouse 
                WHERE product_id = %s AND warehouse_id = %s
            ''', (product_id, warehouse_id))
            
            if cursor.fetchone()[0] > 0:
                # Обновляем существующую запись
                cursor.execute('''
                    UPDATE product_warehouse 
                    SET quantity = %s 
                    WHERE product_id = %s AND warehouse_id = %s
                ''', (new_quantity, product_id, warehouse_id))
            else:
                # Создаем новую запись
                cursor.execute('''
                    INSERT INTO product_warehouse (product_id, warehouse_id, quantity)
                    VALUES (%s, %s, %s)
                ''', (product_id, warehouse_id, new_quantity))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка обновления количества: {e}")
            return False
        finally:
            conn.close()
    
    def delete_product(self, product_id):
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
            conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка удаления товара: {e}")
            return False
        finally:
            conn.close()
    
    def add_sale(self, product_id, quantity, total_price, cashier_id, warehouse_id):
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO sales (product_id, quantity, total_price, sale_date, cashier_id, warehouse_id)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (product_id, quantity, total_price, datetime.now(), cashier_id, warehouse_id))
            
            # Обновляем количество на складе
            cursor.execute('''
                UPDATE product_warehouse 
                SET quantity = quantity - %s 
                WHERE product_id = %s AND warehouse_id = %s
            ''', (quantity, product_id, warehouse_id))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка добавления продажи: {e}")
            return False
        finally:
            conn.close()
    
    def get_sales_report(self, warehouse_id=None):
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            if warehouse_id:
                cursor.execute('''
                    SELECT s.id, p.name, s.quantity, s.total_price, s.sale_date, e.full_name, s.status, w.name
                    FROM sales s
                    JOIN products p ON s.product_id = p.id
                    JOIN employees e ON s.cashier_id = e.id
                    JOIN warehouses w ON s.warehouse_id = w.id
                    WHERE s.warehouse_id = %s
                    ORDER BY s.sale_date DESC
                ''', (warehouse_id,))
            else:
                cursor.execute('''
                    SELECT s.id, p.name, s.quantity, s.total_price, s.sale_date, e.full_name, s.status, w.name
                    FROM sales s
                    JOIN products p ON s.product_id = p.id
                    JOIN employees e ON s.cashier_id = e.id
                    JOIN warehouses w ON s.warehouse_id = w.id
                    ORDER BY s.sale_date DESC
                ''')
            
            sales = cursor.fetchall()
            
            result = []
            for sale in sales:
                result.append({
                    'id': sale[0],
                    'product_name': sale[1],
                    'quantity': sale[2],
                    'total_price': float(sale[3]),
                    'sale_date': sale[4].strftime("%Y-%m-%d %H:%M:%S"),
                    'cashier_name': sale[5],
                    'status': sale[6],
                    'warehouse_name': sale[7]
                })
            return result
        except Exception as e:
            print(f"Ошибка получения отчета: {e}")
            return []
        finally:
            conn.close()
    
    def cancel_sale(self, sale_id):
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            # Получаем информацию о продаже
            cursor.execute("SELECT product_id, quantity, warehouse_id FROM sales WHERE id = %s", (sale_id,))
            sale = cursor.fetchone()
            
            if sale:
                product_id, quantity, warehouse_id = sale
                # Возвращаем товар на склад
                cursor.execute(
                    "UPDATE product_warehouse SET quantity = quantity + %s WHERE product_id = %s AND warehouse_id = %s",
                    (quantity, product_id, warehouse_id)
                )
                # Помечаем продажу как отмененную
                cursor.execute(
                    "UPDATE sales SET status = 'cancelled' WHERE id = %s",
                    (sale_id,)
                )
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка отмены продажи: {e}")
            return False
        finally:
            conn.close()
    
    def get_all_employees(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT e.id, e.login, e.full_name, e.role, e.phone, e.email, w.name as warehouse_name
                FROM employees e
                LEFT JOIN warehouses w ON e.warehouse_id = w.id
            ''')
            employees = cursor.fetchall()
            
            result = []
            for emp in employees:
                result.append({
                    'id': emp[0],
                    'login': emp[1],
                    'full_name': emp[2],
                    'role': emp[3],
                    'phone': emp[4],
                    'email': emp[5],
                    'warehouse_name': emp[6]
                })
            return result
        except Exception as e:
            print(f"Ошибка получения сотрудников: {e}")
            return []
        finally:
            conn.close()
    
    def delete_employee(self, employee_id):
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM sales WHERE cashier_id = %s", (employee_id,))
            sales_count = cursor.fetchone()[0]
            
            if sales_count > 0:
                return False
            
            cursor.execute("DELETE FROM employees WHERE id = %s", (employee_id,))
            conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка удаления сотрудника: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
            
    def get_employee_by_id(self, employee_id):
        """Получает данные сотрудника по ID"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT e.id, e.login, e.full_name, e.role, e.phone, e.email, e.warehouse_id, w.name as warehouse_name
                FROM employees e
                LEFT JOIN warehouses w ON e.warehouse_id = w.id
                WHERE e.id = %s
            ''', (employee_id,))
            result = cursor.fetchone()
            
            if result:
                return {
                    'id': result[0],
                    'login': result[1],
                    'full_name': result[2],
                    'role': result[3],
                    'phone': result[4],
                    'email': result[5],
                    'warehouse_id': result[6],
                    'warehouse_name': result[7]
                }
            return None
        except Exception as e:
            print(f"Ошибка получения сотрудника: {e}")
            return None
        finally:
            conn.close()
    
    def update_employee(self, employee_id, login, password, full_name, role, warehouse_id, phone, email):
        """Обновляет данные сотрудника"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            if password:
                # Если пароль указан, обновляем его
                cursor.execute('''
                    UPDATE employees 
                    SET login = %s, password = %s, full_name = %s, role = %s, 
                        warehouse_id = %s, phone = %s, email = %s
                    WHERE id = %s
                ''', (login, password, full_name, role, warehouse_id, phone, email, employee_id))
            else:
                # Если пароль не указан, не меняем его
                cursor.execute('''
                    UPDATE employees 
                    SET login = %s, full_name = %s, role = %s, 
                        warehouse_id = %s, phone = %s, email = %s
                    WHERE id = %s
                ''', (login, full_name, role, warehouse_id, phone, email, employee_id))
            
            conn.commit()
            return True
        except psycopg2.IntegrityError:
            # Если логин уже существует
            return False
        except Exception as e:
            print(f"Ошибка обновления сотрудника: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def get_warehouse_by_id(self, warehouse_id):
        """Получает данные склада по ID"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT id, name, address FROM warehouses WHERE id = %s
            ''', (warehouse_id,))
            result = cursor.fetchone()
            
            if result:
                return {
                    'id': result[0],
                    'name': result[1],
                    'address': result[2]
                }
            return None
        except Exception as e:
            print(f"Ошибка получения склада: {e}")
            return None
        finally:
            conn.close()
    
    def update_warehouse(self, warehouse_id, name, address):
        """Обновляет данные склада"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                UPDATE warehouses 
                SET name = %s, address = %s
                WHERE id = %s
            ''', (name, address, warehouse_id))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка обновления склада: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def delete_warehouse(self, warehouse_id):
        """Удаляет склад"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM warehouses WHERE id = %s", (warehouse_id,))
            conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка удаления склада: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def get_employees_by_warehouse(self, warehouse_id):
        """Получает список сотрудников на указанном складе"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT id, login, full_name, role 
                FROM employees 
                WHERE warehouse_id = %s
            ''', (warehouse_id,))
            employees = cursor.fetchall()
            
            result = []
            for emp in employees:
                result.append({
                    'id': emp[0],
                    'login': emp[1],
                    'full_name': emp[2],
                    'role': emp[3]
                })
            return result
        except Exception as e:
            print(f"Ошибка получения сотрудников склада: {e}")
            return []
        finally:
            conn.close()