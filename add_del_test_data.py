# test_data_manager.py
import sys
import os

# Добавляем путь к текущей директории для импорта модулей
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from edb.config import DatabaseConfig
from edb.database import Database

class TestDataManager:
    def __init__(self):
        self.config = DatabaseConfig()
        self.db = None
        
    def connect_to_database(self):
        """Подключается к базе данных"""
        try:
            connection_params = self.config.get_connection_params()
            self.db = Database(**connection_params)
            print("Успешно подключено к базе данных")
            return True
        except Exception as e:
            print(f"Ошибка подключения к базе данных: {e}")
            return False
    
    def add_test_data(self):
        """Добавляет тестовые данные в базу"""
        if not self.db:
            print("Нет подключения к базе данных")
            return False
        
        try:
            print("Добавление тестовых данных...")
            
            # Сначала удаляем старые тестовые данные
            print("Очистка старых тестовых данных...")
            self._clean_test_data()
            
            # 1. Добавляем дополнительные склады (пропускаем если уже есть)
            print("Добавляем склады...")
            warehouses = [
                ('Склад на Ленина', 'ул. Ленина, д. 25, г. Москва'),
                ('Склад на Пушкина', 'ул. Пушкина, д. 10, г. Санкт-Петербург'),
                ('Южный склад', 'ул. Южная, д. 5, г. Ростов-на-Дону')
            ]
            
            warehouse_ids = [1]  # Основной склад уже есть
            for name, address in warehouses:
                # Проверяем, существует ли уже склад с таким именем
                existing_warehouse = self._get_warehouse_by_name(name)
                if not existing_warehouse:
                    if self.db.add_warehouse(name, address):
                        new_warehouse = self._get_warehouse_by_name(name)
                        if new_warehouse:
                            warehouse_ids.append(new_warehouse['id'])
                            print(f"   Добавлен склад: {name}")
                else:
                    warehouse_ids.append(existing_warehouse['id'])
                    print(f"   Склад уже существует: {name}")
            
            print(f"Доступно складов: {len(warehouse_ids)}")
            
            print("Добавляем сотрудников...")
            employees = [
                ('manager1', 'manager123', 'Иванов Петр Сергеевич', 'manager', '7(531)056-27-44', 'ivanov@mail.ru', 1),
                ('cashier2', 'cashier123', 'Сидорова Анна Владимировна', 'cashier', '7(2863)000-84-25', 'sidorova@mail.ru', 1),
                ('storekeeper2', 'store123', 'Кузнецов Дмитрий Иванович', 'storekeeper', '7(71)839-10-46', 'kuznetsov@mail.ru', 1),
                ('manager2', 'manager123', 'Петрова Ольга Николаевна', 'manager', '7(71)839-10-46', 'petrova@mail.ru', 2),
                ('cashier3', 'cashier123', 'Смирнов Алексей Викторович', 'cashier', '7(2655)370-09-86', 'smirnov@mail.ru', 2)
            ]
            
            employee_ids = []
            for emp in employees:
                # Проверяем, существует ли уже сотрудник с таким логином
                existing_emp = self._get_employee_by_login(emp[0])
                if not existing_emp:
                    if self.db.register_employee(*emp):
                        new_emp = self.db.authenticate_user(emp[0], emp[1])
                        if new_emp:
                            employee_ids.append(new_emp['id'])
                            print(f"   Добавлен сотрудник: {emp[2]}")
                else:
                    employee_ids.append(existing_emp['id'])
                    print(f"   Сотрудник уже существует: {emp[2]}")
            
            print(f"Доступно сотрудников: {len(employee_ids)}")
            
            # 3. Добавляем товары
            print("Добавляем товары...")
            products = [
                # Холодильники
                ('Холодильник Samsung RB37', 'Холодильники', 'Samsung', 45999.00, 2),
                ('Холодильник LG GA-B459', 'Холодильники', 'LG', 38999.00, 2),
                ('Холодильник Bosch KGN36', 'Холодильники', 'Bosch', 52999.00, 1),
                
                # Стиральные машины
                ('Стиральная машина Indesit IWSC 5105', 'Стиральные машины', 'Indesit', 21999.00, 3),
                ('Стиральная машина Samsung WW65', 'Стиральные машины', 'Samsung', 32999.00, 2),
                ('Стиральная машина LG F2J3', 'Стиральные машины', 'LG', 41999.00, 2),
                
                # Телевизоры
                ('Телевизор LG 55NANO766', 'Телевизоры', 'LG', 54999.00, 2),
                ('Телевизор Samsung QE55Q60', 'Телевизоры', 'Samsung', 68999.00, 1),
                ('Телевизор Sony KD-55X80', 'Телевизоры', 'Sony', 72999.00, 1),
                
                # Микроволновые печи
                ('Микроволновая печь Samsung MG23', 'Микроволновые печи', 'Samsung', 8999.00, 5),
                ('Микроволновая печь LG MS23', 'Микроволновые печи', 'LG', 10999.00, 4),
                
                # Пылесосы
                ('Пылесос Thomas TWIN X10', 'Пылесосы', 'Thomas', 15999.00, 3),
                ('Пылесос Samsung VS15', 'Пылесосы', 'Samsung', 12999.00, 4),
                
                # Кофемашины
                ('Кофемашина DeLonghi ECAM350', 'Кофемашины', 'DeLonghi', 34999.00, 2),
                ('Кофемашина Philips EP2220', 'Кофемашины', 'Philips', 28999.00, 2)
            ]
            
            product_ids = []
            for product in products:
                # Проверяем, существует ли уже товар с таким именем
                existing_product = self._get_product_by_name(product[0])
                if not existing_product:
                    if self.db.add_product(*product):
                        new_product = self._get_product_by_name(product[0])
                        if new_product:
                            product_ids.append(new_product['id'])
                            print(f"   Добавлен товар: {product[0]}")
                else:
                    product_ids.append(existing_product['id'])
                    print(f"   Товар уже существует: {product[0]}")
            
            print(f"Доступно товаров: {len(product_ids)}")
            
            # 4. Добавляем наличие товаров на складах
            print("Добавляем наличие товаров...")
            stock_data = [
                # Склад 1
                (1, 1, 5), (2, 1, 3), (3, 1, 2),
                (4, 1, 8), (5, 1, 4), (6, 1, 3),
                (7, 1, 6), (8, 1, 2), (9, 1, 1),
                (10, 1, 10), (11, 1, 7),
                (12, 1, 5), (13, 1, 4),
                (14, 1, 3), (15, 1, 4),
                
                # Склад 2
                (1, 2, 3), (2, 2, 4), (4, 2, 6),
                (5, 2, 3), (7, 2, 4), (10, 2, 8),
                (12, 2, 4), (14, 2, 2),
                
                # Склад 3
                (3, 3, 1), (6, 3, 2), (8, 3, 1),
                (9, 3, 1), (11, 3, 5), (13, 3, 3),
                (15, 3, 2)
            ]
            
            stock_count = 0
            for product_id, warehouse_id, quantity in stock_data:
                if product_id <= len(product_ids) and warehouse_id in warehouse_ids:
                    if self.db.update_product_quantity(product_id, warehouse_id, quantity):
                        stock_count += 1
            
            print(f"Добавлено записей наличия: {stock_count}")
            
            # 5. Добавляем клиентов
            print("Добавляем клиентов...")
            customers = [
                ('Семенов Андрей Игоревич', "79167778899", 'semenov@mail.ru', 'ул. Мира, д. 15, кв. 34, г. Москва'),
                ('Ковалева Мария Сергеевна', "79168889900", 'kovaleva@yandex.ru', 'пр. Ленинградский, д. 45, кв. 12, г. Москва'),
                ('Николаев Денис Петрович', "79169990011", 'nikolaev@gmail.com', 'ул. Садовая, д. 23, кв. 67, г. Санкт-Петербург'),
                ('Орлова Екатерина Викторовна', "79161112233", 'orlova@mail.ru', 'ул. Центральная, д. 8, кв. 89, г. Ростов-на-Дону'),
                ('Федоров Сергей Александрович', "79162223344", 'fedorov@yandex.ru', 'пр. Победы, д. 33, кв. 45, г. Москва'),
                ('Григорьева Анна Дмитриевна', "79163334455", 'grigorieva@gmail.com', 'ул. Зеленая, д. 12, кв. 23, г. Санкт-Петербург')
            ]
            
            customer_ids = []
            for customer in customers:
                # Проверяем, существует ли уже клиент с таким телефоном
                existing_customer = self.db.get_customer_by_phone(customer[1])
                if not existing_customer:
                    if self.db.create_customer(*customer):
                        new_customer = self.db.get_customer_by_phone(customer[1])
                        if new_customer:
                            customer_ids.append(new_customer['id'])
                            print(f"   Добавлен клиент: {customer[0]}")
                else:
                    customer_ids.append(existing_customer['id'])
                    print(f"   Клиент уже существует: {customer[0]}")
            
            print(f"Доступно клиентов: {len(customer_ids)}")
            
            # 6. Добавляем продажи
            print("Добавляем продажи...")
            
            # Получаем ID существующих кассиров
            all_employees = self.db.get_all_employees()
            cashiers = [emp for emp in all_employees if emp['role'] == 'cashier']
            if not cashiers:
                print("Ошибка: нет кассиров в базе данных")
                return False
            
            # Используем первого доступного кассира для всех продаж
            cashier_id = cashiers[0]['id']
            
            sales = [
                (1, 1, 45999.00, cashier_id, 1),
                (4, 1, 21999.00, cashier_id, 1),
                (7, 1, 54999.00, cashier_id, 1),
                (10, 1, 8999.00, cashier_id, 1),
                (2, 1, 38999.00, cashier_id, 2),
                (5, 1, 32999.00, cashier_id, 2),
                (14, 1, 34999.00, cashier_id, 1),
                (12, 1, 15999.00, cashier_id, 2),
                (3, 1, 52999.00, cashier_id, 1),
                (8, 1, 68999.00, cashier_id, 1)
            ]
            
            sale_ids = []
            for i, sale in enumerate(sales):
                product_id, quantity, total_price, cashier_id, warehouse_id = sale
                if product_id <= len(product_ids) and warehouse_id in warehouse_ids:
                    if self.db.add_sale(product_id, quantity, total_price, cashier_id, warehouse_id):
                        last_sale_id = self._get_last_sale_id()
                        if last_sale_id:
                            sale_ids.append(last_sale_id)
                            print(f"   Добавлена продажа #{i+1}")
            
            print(f"Добавлено продаж: {len(sale_ids)}")
            
            # 7. Добавляем доставки
            print("Добавляем доставки...")
            
            if len(sale_ids) >= 7 and len(customer_ids) >= 6:
                deliveries = [
                    (sale_ids[0], customer_ids[0], 'ул. Мира, д. 15, кв. 34, г. Москва', ''),
                    (sale_ids[1], customer_ids[1], 'пр. Ленинградский, д. 45, кв. 12, г. Москва', ''),
                    (sale_ids[2], customer_ids[2], 'ул. Садовая, д. 23, кв. 67, г. Санкт-Петербург', ''),
                    (sale_ids[3], customer_ids[3], 'ул. Центральная, д. 8, кв. 89, г. Ростов-на-Дону', ''),
                    (sale_ids[4], customer_ids[4], 'пр. Победы, д. 33, кв. 45, г. Москва', ''),
                    (sale_ids[5], customer_ids[5], 'ул. Зеленая, д. 12, кв. 23, г. Санкт-Петербург', ''),
                    (sale_ids[6], customer_ids[0], 'ул. Мира, д. 15, кв. 34, г. Москва', '')
                ]
                
                delivery_ids = []
                for i, delivery in enumerate(deliveries):
                    if self.db.create_delivery(*delivery):
                        last_delivery_id = self._get_last_delivery_id()
                        if last_delivery_id:
                            delivery_ids.append(last_delivery_id)
                            print(f"   Добавлена доставка #{i+1}")
                
                print(f"Добавлено доставок: {len(delivery_ids)}")
                
                # 8. Обновляем статусы доставок
                print("Обновляем статусы доставок...")
                
                # Получаем кладовщиков
                storekeepers = [emp for emp in all_employees if emp['role'] == 'storekeeper']
                if storekeepers and len(delivery_ids) >= 3:
                    storekeeper_id = storekeepers[0]['id']
                    
                    self.db.assign_delivery_to_storekeeper(delivery_ids[0], storekeeper_id)
                    self.db.assign_delivery_to_storekeeper(delivery_ids[1], storekeeper_id)
                    self.db.assign_delivery_to_storekeeper(delivery_ids[2], storekeeper_id)
                    print("   Назначены кладовщики для доставок")
                
                # Создаем группы доставки
                print("Создаем группы доставки...")
                if storekeepers and len(delivery_ids) >= 3:
                    group1_id = self.db.create_delivery_group(storekeeper_id, 'Газель A123BC777')
                    group2_id = self.db.create_delivery_group(storekeeper_id, 'Газель B456DE777')
                    
                    if group1_id and len(delivery_ids) >= 2:
                        self.db.add_delivery_to_group(group1_id, delivery_ids[0])
                        self.db.add_delivery_to_group(group1_id, delivery_ids[1])
                        self.db.complete_delivery_group(group1_id)
                        self.db.complete_delivery(delivery_ids[0])
                        self.db.complete_delivery(delivery_ids[1])
                        print("   Создана и завершена группа доставки 1")
                    
                    if group2_id and len(delivery_ids) >= 3:
                        self.db.add_delivery_to_group(group2_id, delivery_ids[2])
                        print("   Создана группа доставки 2")
            else:
                print("   Недостаточно данных для создания доставок")
            
            print("Тестовые данные успешно добавлены!")
            return True
            
        except Exception as e:
            print(f"Ошибка при добавлении тестовых данных: {e}")
            return False
    
    def _clean_test_data(self):
        """Очищает только тестовые данные, сохраняя стандартных пользователей"""
        try:
            # Удаляем в правильном порядке с учетом внешних ключей
            self._execute_sql("DELETE FROM delivery_group_items")
            self._execute_sql("DELETE FROM delivery_groups")
            self._execute_sql("DELETE FROM deliveries")
            self._execute_sql("DELETE FROM sales")
            self._execute_sql("DELETE FROM customers")
            self._execute_sql("DELETE FROM product_warehouse")
            self._execute_sql("DELETE FROM products")
            
            # Удаляем только тестовых сотрудников (кроме стандартных)
            self._execute_sql("DELETE FROM employees WHERE login NOT IN ('admin', 'cashier', 'storekeeper')")
            
            # Удаляем только тестовые склады (кроме основного)
            self._execute_sql("DELETE FROM warehouses WHERE name != 'Основной склад'")
            
            # Сбрасываем последовательности
            self._reset_sequences()
            
        except Exception as e:
            print(f"Ошибка при очистке тестовых данных: {e}")
    
    def remove_test_data(self):
        """Удаляет тестовые данные из базы"""
        if not self.db:
            print("Нет подключения к базе данных")
            return False
        
        try:
            print("Удаление тестовых данных...")
            self._clean_test_data()
            print("Тестовые данные успешно удалены!")
            return True
            
        except Exception as e:
            print(f"Ошибка при удалении тестовых данных: {e}")
            return False
    
    def show_database_info(self):
        """Показывает информацию о текущих данных в базе"""
        if not self.db:
            print("Нет подключения к базе данных")
            return
        
        try:
            print("\nИНФОРМАЦИЯ О БАЗЕ ДАННЫХ:")
            print("=" * 50)
            
            # Склады
            warehouses = self.db.get_all_warehouses()
            print(f"Склады: {len(warehouses)}")
            for wh in warehouses:
                print(f"   - {wh['name']} (ID: {wh['id']})")
            
            # Сотрудники
            employees = self.db.get_all_employees()
            print(f"\nСотрудники: {len(employees)}")
            for emp in employees:
                print(f"   - {emp['full_name']} ({emp['role']})")
            
            # Товары
            products = self.db.get_products_with_quantity()
            print(f"\nТовары: {len(products)}")
            
            # Клиенты
            customers = self.db.get_all_customers()
            print(f"\nКлиенты: {len(customers)}")
            
            # Продажи
            sales = self.db.get_sales_report()
            print(f"\nПродажи: {len(sales)}")
            
            # Доставки
            deliveries = self.db.get_all_deliveries()
            print(f"\nДоставки: {len(deliveries)}")
            
            print("=" * 50)
            
        except Exception as e:
            print(f"Ошибка при получении информации: {e}")
    
    def _execute_sql(self, sql):
        """Выполняет SQL запрос напрямую"""
        conn = self.db._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(sql)
            conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка выполнения SQL: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def _reset_sequences(self):
        """Сбрасывает последовательности ID"""
        sequences = [
            'warehouses_id_seq',
            'employees_id_seq',
            'products_id_seq',
            'product_warehouse_id_seq',
            'sales_id_seq',
            'customers_id_seq',
            'deliveries_id_seq',
            'delivery_groups_id_seq',
            'delivery_group_items_id_seq'
        ]
        
        for seq in sequences:
            try:
                self._execute_sql(f"ALTER SEQUENCE {seq} RESTART WITH 1")
            except:
                # Игнорируем ошибки, если последовательности не существует
                pass
    
    def _get_warehouse_by_name(self, name):
        """Находит склад по имени"""
        warehouses = self.db.get_all_warehouses()
        for wh in warehouses:
            if wh['name'] == name:
                return wh
        return None
    
    def _get_employee_by_login(self, login):
        """Находит сотрудника по логину"""
        try:
            # Пробуем аутентифицироваться с пустым паролем, чтобы получить данные сотрудника
            all_employees = self.db.get_all_employees()
            for emp in all_employees:
                if emp['login'] == login:
                    return emp
            return None
        except:
            return None
    
    def _get_product_by_name(self, name):
        """Находит товар по имени"""
        products = self.db.get_products_with_quantity()
        for product in products:
            if product['name'] == name:
                return product
        return None
    
    def _get_last_sale_id(self):
        """Получает ID последней добавленной продажи"""
        conn = self.db._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT MAX(id) FROM sales")
            result = cursor.fetchone()[0]
            return result if result else None
        finally:
            conn.close()
    
    def _get_last_delivery_id(self):
        """Получает ID последней добавленной доставки"""
        conn = self.db._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT MAX(id) FROM deliveries")
            result = cursor.fetchone()[0]
            return result if result else None
        finally:
            conn.close()

def main():
    """Главная функция приложения"""
    manager = TestDataManager()
    
    print("МЕНЕДЖЕР ТЕСТОВЫХ ДАННЫХ ДЛЯ МАГАЗИНА БЫТОВОЙ ТЕХНИКИ")
    print("=" * 60)
    
    # Подключаемся к базе данных
    if not manager.connect_to_database():
        print("Не удалось подключиться к базе данных. Проверьте настройки в database_config.json")
        return
    
    while True:
        print("\nВЫБЕРИТЕ ДЕЙСТВИЕ:")
        print("1. Добавить тестовые данные")
        print("2. Удалить тестовые данные")
        print("3. Показать информацию о базе данных")
        print("4. Выйти")
        
        choice = input("\nВаш выбор (1-4): ").strip()
        
        if choice == '1':
            print("\nВНИМАНИЕ: Это добавит тестовые данные в базу.")
            confirm = input("Продолжить? (y/n): ").strip().lower()
            if confirm == 'y':
                manager.add_test_data()
            else:
                print("Операция отменена")
        
        elif choice == '2':
            print("\nВНИМАНИЕ: Это удалит ВСЕ тестовые данные из базы!")
            confirm = input("Продолжить? (y/n): ").strip().lower()
            if confirm == 'y':
                manager.remove_test_data()
            else:
                print("Операция отменена")
        
        elif choice == '3':
            manager.show_database_info()
        
        elif choice == '4':
            print("До свидания!")
            break
        
        else:
            print("Неверный выбор. Попробуйте снова.")

if __name__ == "__main__":
    main()