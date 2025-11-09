from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QTableWidget,
                             QTableWidgetItem, QMessageBox, QHeaderView,
                             QTabWidget, QDialog, QDialogButtonBox, QFormLayout,
                             QComboBox, QGroupBox, QSpinBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class StorekeeperWindow(QMainWindow):
    def __init__(self, db, user, login_window):
        super().__init__()
        self.db = db
        self.user = user
        self.login_window = login_window
        self.init_ui()
        # Применяем тему сразу после инициализации
        self.apply_theme()
    
    def init_ui(self):
        self.setWindowTitle(f'Склад - Магазин бытовой техники ({self.user["full_name"]})')
        self.setMinimumSize(1200, 800)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        
        # Верхняя панель
        top_panel = QHBoxLayout()
        user_info = QLabel(f'Кладовщик: {self.user["full_name"]} | Склад: {self.user["warehouse_name"]}')
        user_info.setFont(QFont('Arial', 10))
        
        logout_btn = QPushButton('Выйти')
        logout_btn.setFixedSize(80, 30)
        logout_btn.clicked.connect(self.logout)
        
        theme_btn = QPushButton('Смена темы')
        theme_btn.setFixedSize(100, 30)
        theme_btn.clicked.connect(self.change_theme)

        top_panel.addWidget(theme_btn)
        top_panel.addWidget(user_info)
        top_panel.addStretch()
        top_panel.addWidget(logout_btn)
        
        # Вкладки
        self.tabs = QTabWidget()
        
        # Вкладка 1: Учет товаров
        self.products_tab = QWidget()
        self.init_products_tab()
        
        # Вкладка 2: Ожидающие доставки
        self.deliveries_tab = QWidget()
        self.init_deliveries_tab()
        
        # Вкладка 3: Мои доставки
        self.my_deliveries_tab = QWidget()
        self.init_my_deliveries_tab()
        
        # Вкладка 4: Группы доставки
        self.delivery_groups_tab = QWidget()
        self.init_delivery_groups_tab()
        
        self.tabs.addTab(self.products_tab, "Учет товаров")
        self.tabs.addTab(self.deliveries_tab, "Ожидающие доставки")
        self.tabs.addTab(self.my_deliveries_tab, "Мои доставки")
        self.tabs.addTab(self.delivery_groups_tab, "Группы доставки")
        
        layout.addLayout(top_panel)
        layout.addWidget(self.tabs)
        
        central_widget.setLayout(layout)
        
        self.load_products()
        self.load_pending_deliveries()
        self.load_my_deliveries()
        self.load_delivery_groups()
    
    def init_products_tab(self):
        """Вкладка для управления товарами на складе"""
        layout = QVBoxLayout()
        
        # Заголовок
        title = QLabel('Учет товаров на складе')
        title.setFont(QFont('Arial', 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Фильтр отображения
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel('Отображение:'))
        
        self.view_combo = QComboBox()
        self.view_combo.addItems(['Текущий склад', 'Все склады'])
        self.view_combo.currentTextChanged.connect(self.load_products)
        
        filter_layout.addWidget(self.view_combo)
        filter_layout.addStretch()
        
        # Таблица товаров
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(7)
        self.products_table.setHorizontalHeaderLabels([
            'ID', 'Название', 'Категория', 'Бренд', 'Цена', 'Количество', 'Мин. количество'
        ])
        self.products_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Форма добавления товара
        form_group = QGroupBox("Добавление товара")
        form_layout = QHBoxLayout()
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText('Название')
        
        self.category_input = QLineEdit()
        self.category_input.setPlaceholderText('Категория')
        
        self.brand_input = QLineEdit()
        self.brand_input.setPlaceholderText('Бренд')
        
        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText('Цена')
        
        self.min_quantity_input = QSpinBox()
        self.min_quantity_input.setMaximum(1000)
        self.min_quantity_input.setValue(0)
        
        add_btn = QPushButton('Добавить товар')
        add_btn.clicked.connect(self.add_product)
        
        form_layout.addWidget(self.name_input)
        form_layout.addWidget(self.category_input)
        form_layout.addWidget(self.brand_input)
        form_layout.addWidget(self.price_input)
        form_layout.addWidget(QLabel('Мин.:'))
        form_layout.addWidget(self.min_quantity_input)
        form_layout.addWidget(add_btn)
        
        form_group.setLayout(form_layout)
        
        # Форма изменения количества
        quantity_group = QGroupBox("Изменение количества товара")
        quantity_layout = QHBoxLayout()
        
        self.quantity_product_id = QSpinBox()
        self.quantity_product_id.setMinimum(1)
        
        self.new_quantity_input = QSpinBox()
        self.new_quantity_input.setMaximum(10000)
        self.new_quantity_input.setValue(0)
        
        update_quantity_btn = QPushButton('Обновить количество')
        update_quantity_btn.clicked.connect(self.update_quantity)
        
        quantity_layout.addWidget(QLabel('ID товара:'))
        quantity_layout.addWidget(self.quantity_product_id)
        quantity_layout.addWidget(QLabel('Новое количество:'))
        quantity_layout.addWidget(self.new_quantity_input)
        quantity_layout.addWidget(update_quantity_btn)
        
        quantity_group.setLayout(quantity_layout)
        
        # Кнопка проверки минимального количества
        check_min_btn = QPushButton('Проверить минимальные количества')
        check_min_btn.clicked.connect(self.check_minimum_quantities)
        
        layout.addWidget(title)
        layout.addLayout(filter_layout)
        layout.addWidget(QLabel('Товары:'))
        layout.addWidget(self.products_table)
        layout.addWidget(form_group)
        layout.addWidget(quantity_group)
        layout.addWidget(check_min_btn)
        
        self.products_tab.setLayout(layout)
    
    def init_deliveries_tab(self):
        layout = QVBoxLayout()
        
        title = QLabel('Ожидающие доставки')
        title.setFont(QFont('Arial', 12, QFont.Weight.Bold))
        
        self.pending_deliveries_table = QTableWidget()
        self.pending_deliveries_table.setColumnCount(8)
        self.pending_deliveries_table.setHorizontalHeaderLabels([
            'ID', 'Клиент', 'Телефон', 'Адрес доставки', 'Товар', 'Количество', 'Кассир', 'Действие'
        ])
        self.pending_deliveries_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(title)
        layout.addWidget(self.pending_deliveries_table)
        
        self.deliveries_tab.setLayout(layout)
    
    def init_my_deliveries_tab(self):
        layout = QVBoxLayout()
        
        title = QLabel('Мои доставки')
        title.setFont(QFont('Arial', 12, QFont.Weight.Bold))
        
        self.my_deliveries_table = QTableWidget()
        self.my_deliveries_table.setColumnCount(8)
        self.my_deliveries_table.setHorizontalHeaderLabels([
            'ID', 'Клиент', 'Телефон', 'Адрес доставки', 'Товар', 'Количество', 'Статус', 'Действие'
        ])
        self.my_deliveries_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(title)
        layout.addWidget(self.my_deliveries_table)
        
        self.my_deliveries_tab.setLayout(layout)
    
    def init_delivery_groups_tab(self):
        layout = QVBoxLayout()
        
        title = QLabel('Группы доставки')
        title.setFont(QFont('Arial', 12, QFont.Weight.Bold))
        
        # Панель создания новой группы
        create_group_layout = QHBoxLayout()
        
        self.vehicle_info_input = QLineEdit()
        self.vehicle_info_input.setPlaceholderText('Информация о транспорте (номер машины и т.д.)')
        
        create_group_btn = QPushButton('Создать группу доставки')
        create_group_btn.clicked.connect(self.create_delivery_group)
        
        create_group_layout.addWidget(QLabel('Транспорт:'))
        create_group_layout.addWidget(self.vehicle_info_input)
        create_group_layout.addWidget(create_group_btn)
        
        self.delivery_groups_table = QTableWidget()
        self.delivery_groups_table.setColumnCount(6)
        self.delivery_groups_table.setHorizontalHeaderLabels([
            'ID', 'Транспорт', 'Статус', 'Дата создания', 'Кол-во доставок', 'Действие'
        ])
        self.delivery_groups_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.delivery_groups_table.doubleClicked.connect(self.show_group_details)
        
        layout.addWidget(title)
        layout.addLayout(create_group_layout)
        layout.addWidget(self.delivery_groups_table)
        
        self.delivery_groups_tab.setLayout(layout)
    
    # ДОБАВЛЕННЫЙ МЕТОД
    def apply_theme(self):
        """Применяет текущую тему из login_window"""
        if hasattr(self.login_window, 'current_theme') and hasattr(self.login_window, 'current_color'):
            if self.login_window.current_theme == 'light':
                self.apply_light_theme(self.login_window.current_color)
            else:
                self.apply_dark_theme(self.login_window.current_color)
    
    # Методы для работы с товарами
    def load_products(self):
        view_type = self.view_combo.currentText()
        
        if view_type == 'Текущий склад':
            products = self.db.get_products_with_quantity(self.user['warehouse_id'])
        else:
            products = self.db.get_products_with_quantity(None)
        
        self.products_table.setRowCount(len(products))
        
        for row, product in enumerate(products):
            self.products_table.setItem(row, 0, QTableWidgetItem(str(product['id'])))
            self.products_table.setItem(row, 1, QTableWidgetItem(product['name']))
            self.products_table.setItem(row, 2, QTableWidgetItem(product['category']))
            self.products_table.setItem(row, 3, QTableWidgetItem(product['brand']))
            self.products_table.setItem(row, 4, QTableWidgetItem(str(product['price'])))
            self.products_table.setItem(row, 5, QTableWidgetItem(str(product['quantity'])))
            self.products_table.setItem(row, 6, QTableWidgetItem(str(product['min_quantity'])))
    
    def add_product(self):
        name = self.name_input.text()
        category = self.category_input.text()
        brand = self.brand_input.text()
        price_text = self.price_input.text()
        min_quantity = self.min_quantity_input.value()
        
        if not name or not category or not price_text:
            QMessageBox.warning(self, 'Ошибка', 'Заполните название, категорию и цену')
            return
        
        try:
            price = float(price_text)
            if price <= 0:
                QMessageBox.warning(self, 'Ошибка', 'Цена должна быть положительным числом')
                return
        except ValueError:
            QMessageBox.warning(self, 'Ошибка', 'Цена должна быть числом')
            return
        
        if self.db.add_product(name, category, brand, price, min_quantity):
            QMessageBox.information(self, 'Успех', 'Товар добавлен')
            self.clear_product_form()
            self.load_products()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Ошибка при добавлении товара')
    
    def update_quantity(self):
        product_id = self.quantity_product_id.value()
        warehouse_id = self.user['warehouse_id']
        new_quantity = self.new_quantity_input.value()
        
        if product_id <= 0:
            QMessageBox.warning(self, 'Ошибка', 'Введите корректный ID товара')
            return
        
        if new_quantity < 0:
            QMessageBox.warning(self, 'Ошибка', 'Количество не может быть отрицательным')
            return
        
        if self.db.update_product_quantity(product_id, warehouse_id, new_quantity):
            QMessageBox.information(self, 'Успех', 'Количество товара обновлено')
            self.load_products()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Ошибка при обновлении количества')
    
    def check_minimum_quantities(self):
        """Проверка товаров с количеством ниже минимального"""
        products = self.db.get_products_with_quantity(self.user['warehouse_id'])
        low_quantity_products = [p for p in products if p['quantity'] < p['min_quantity']]
        
        if not low_quantity_products:
            QMessageBox.information(self, 'Проверка', 'Все товары в достаточном количестве')
            return
        
        message = "Товары с низким количеством:\n\n"
        for product in low_quantity_products:
            message += f"{product['name']}: {product['quantity']} (мин.: {product['min_quantity']})\n"
        
        QMessageBox.warning(self, 'Внимание', message)
    
    def clear_product_form(self):
        self.name_input.clear()
        self.category_input.clear()
        self.brand_input.clear()
        self.price_input.clear()
        self.min_quantity_input.setValue(0)
    
    # Методы для работы с доставками (остаются без изменений)
    def load_pending_deliveries(self):
        deliveries = self.db.get_pending_deliveries(self.user['warehouse_id'])
        self.pending_deliveries_table.setRowCount(len(deliveries))
        
        for row, delivery in enumerate(deliveries):
            self.pending_deliveries_table.setItem(row, 0, QTableWidgetItem(str(delivery['id'])))
            self.pending_deliveries_table.setItem(row, 1, QTableWidgetItem(delivery['customer_name']))
            self.pending_deliveries_table.setItem(row, 2, QTableWidgetItem(delivery['customer_phone']))
            self.pending_deliveries_table.setItem(row, 3, QTableWidgetItem(delivery['delivery_address']))
            self.pending_deliveries_table.setItem(row, 4, QTableWidgetItem(delivery['product_name']))
            self.pending_deliveries_table.setItem(row, 5, QTableWidgetItem(str(delivery['quantity'])))
            self.pending_deliveries_table.setItem(row, 6, QTableWidgetItem(delivery['cashier_name']))
            
            action_widget = QWidget()
            action_layout = QHBoxLayout()
            action_layout.setContentsMargins(0, 0, 0, 0)
            
            take_delivery_btn = QPushButton('Взять в работу')
            take_delivery_btn.clicked.connect(lambda checked, d_id=delivery['id']: self.take_delivery(d_id))
            
            action_layout.addWidget(take_delivery_btn)
            action_widget.setLayout(action_layout)
            
            self.pending_deliveries_table.setCellWidget(row, 7, action_widget)
    
    def load_my_deliveries(self):
        all_deliveries = self.db.get_all_deliveries(self.user['warehouse_id'])
        my_deliveries = [d for d in all_deliveries if d['status'] in ['assigned', 'in_progress']]
        
        self.my_deliveries_table.setRowCount(len(my_deliveries))
        
        for row, delivery in enumerate(my_deliveries):
            self.my_deliveries_table.setItem(row, 0, QTableWidgetItem(str(delivery['id'])))
            self.my_deliveries_table.setItem(row, 1, QTableWidgetItem(delivery['customer_name']))
            self.my_deliveries_table.setItem(row, 2, QTableWidgetItem(delivery['customer_phone']))
            self.my_deliveries_table.setItem(row, 3, QTableWidgetItem(delivery['delivery_address']))
            self.my_deliveries_table.setItem(row, 4, QTableWidgetItem(delivery['product_name']))
            self.my_deliveries_table.setItem(row, 5, QTableWidgetItem(str(delivery['quantity'])))
            self.my_deliveries_table.setItem(row, 6, QTableWidgetItem(self.get_status_text(delivery['status'])))
            
            action_widget = QWidget()
            action_layout = QHBoxLayout()
            action_layout.setContentsMargins(0, 0, 0, 0)
            
            if delivery['status'] == 'assigned':
                add_to_group_btn = QPushButton('Добавить в группу')
                add_to_group_btn.clicked.connect(lambda checked, d_id=delivery['id']: self.add_to_delivery_group(d_id))
                action_layout.addWidget(add_to_group_btn)
            
            complete_btn = QPushButton('Завершить')
            complete_btn.clicked.connect(lambda checked, d_id=delivery['id']: self.complete_delivery(d_id))
            action_layout.addWidget(complete_btn)
            
            action_widget.setLayout(action_layout)
            
            self.my_deliveries_table.setCellWidget(row, 7, action_widget)
    
    def load_delivery_groups(self):
        groups = self.db.get_delivery_groups(self.user['id'])
        self.delivery_groups_table.setRowCount(len(groups))
        
        for row, group in enumerate(groups):
            self.delivery_groups_table.setItem(row, 0, QTableWidgetItem(str(group['id'])))
            self.delivery_groups_table.setItem(row, 1, QTableWidgetItem(group['vehicle_info']))
            self.delivery_groups_table.setItem(row, 2, QTableWidgetItem(self.get_status_text(group['status'])))
            self.delivery_groups_table.setItem(row, 3, QTableWidgetItem(group['created_date']))
            self.delivery_groups_table.setItem(row, 4, QTableWidgetItem(str(group['delivery_count'])))
            
            action_widget = QWidget()
            action_layout = QHBoxLayout()
            action_layout.setContentsMargins(0, 0, 0, 0)
            
            if group['status'] == 'preparing':
                complete_group_btn = QPushButton('Завершить группу')
                complete_group_btn.clicked.connect(lambda checked, g_id=group['id']: self.complete_delivery_group(g_id))
                action_layout.addWidget(complete_group_btn)
            
            details_btn = QPushButton('Детали')
            details_btn.clicked.connect(lambda checked, g_id=group['id']: self.show_group_details(g_id))
            action_layout.addWidget(details_btn)
            
            action_widget.setLayout(action_layout)
            
            self.delivery_groups_table.setCellWidget(row, 5, action_widget)
    
    def get_status_text(self, status):
        status_map = {
            'pending': 'Ожидает',
            'assigned': 'Назначена',
            'in_progress': 'В процессе',
            'delivered': 'Доставлена',
            'cancelled': 'Отменена',
            'preparing': 'Формируется',
            'completed': 'Завершена'
        }
        return status_map.get(status, status)
    
    def take_delivery(self, delivery_id):
        success = self.db.assign_delivery_to_storekeeper(delivery_id, self.user['id'])
        if success:
            QMessageBox.information(self, 'Успех', 'Доставка назначена вам')
            self.load_pending_deliveries()
            self.load_my_deliveries()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Ошибка при назначении доставки')
    
    def add_to_delivery_group(self, delivery_id):
        groups = self.db.get_delivery_groups(self.user['id'])
        active_groups = [g for g in groups if g['status'] == 'preparing']
        
        if not active_groups:
            QMessageBox.warning(self, 'Ошибка', 'Сначала создайте группу доставки')
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle('Выбор группы доставки')
        dialog.setFixedSize(300, 150)
        
        layout = QVBoxLayout()
        
        group_combo = QComboBox()
        for group in active_groups:
            group_combo.addItem(f"{group['vehicle_info']} (ID: {group['id']})", group['id'])
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        
        layout.addWidget(QLabel('Выберите группу доставки:'))
        layout.addWidget(group_combo)
        layout.addWidget(buttons)
        
        dialog.setLayout(layout)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            group_id = group_combo.currentData()
            success = self.db.add_delivery_to_group(group_id, delivery_id)
            if success:
                QMessageBox.information(self, 'Успех', 'Доставка добавлена в группу')
                self.load_my_deliveries()
                self.load_delivery_groups()
            else:
                QMessageBox.warning(self, 'Ошибка', 'Ошибка при добавлении доставки в группу')
    
    def create_delivery_group(self):
        vehicle_info = self.vehicle_info_input.text()
        if not vehicle_info:
            QMessageBox.warning(self, 'Ошибка', 'Введите информацию о транспорте')
            return
        
        group_id = self.db.create_delivery_group(self.user['id'], vehicle_info)
        if group_id:
            QMessageBox.information(self, 'Успех', 'Группа доставки создана')
            self.vehicle_info_input.clear()
            self.load_delivery_groups()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Ошибка при создании группы доставки')
    
    def complete_delivery(self, delivery_id):
        success = self.db.complete_delivery(delivery_id)
        if success:
            QMessageBox.information(self, 'Успех', 'Доставка завершена')
            self.load_my_deliveries()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Ошибка при завершении доставки')
    
    def complete_delivery_group(self, group_id):
        success = self.db.complete_delivery_group(group_id)
        if success:
            QMessageBox.information(self, 'Успех', 'Группа доставки завершена')
            self.load_delivery_groups()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Ошибка при завершении группы доставки')
    
    def show_group_details(self, group_id=None):
        if not group_id:
            current_row = self.delivery_groups_table.currentRow()
            if current_row >= 0:
                group_id = int(self.delivery_groups_table.item(current_row, 0).text())
            else:
                return
        
        deliveries = self.db.get_deliveries_in_group(group_id)
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f'Детали группы доставки #{group_id}')
        dialog.setFixedSize(600, 400)
        
        layout = QVBoxLayout()
        
        table = QTableWidget()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels(['ID', 'Клиент', 'Телефон', 'Адрес', 'Товар', 'Статус'])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        table.setRowCount(len(deliveries))
        for row, delivery in enumerate(deliveries):
            table.setItem(row, 0, QTableWidgetItem(str(delivery['id'])))
            table.setItem(row, 1, QTableWidgetItem(delivery['customer_name']))
            table.setItem(row, 2, QTableWidgetItem(delivery['customer_phone']))
            table.setItem(row, 3, QTableWidgetItem(delivery['delivery_address']))
            table.setItem(row, 4, QTableWidgetItem(delivery['product_name']))
            table.setItem(row, 5, QTableWidgetItem(self.get_status_text(delivery['status'])))
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(dialog.reject)
        
        layout.addWidget(QLabel(f'Доставки в группе #{group_id}:'))
        layout.addWidget(table)
        layout.addWidget(buttons)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def logout(self):
        self.login_window.show()
        self.close()  
        
    def apply_theme(self):
        """Применяет тему от login_window"""
        theme_settings = self.login_window.get_theme_settings()
        if theme_settings['theme'] == 'light':
            self.apply_light_theme(theme_settings['color'])
        else:
            self.apply_dark_theme(theme_settings['color'])            
            
    def change_theme(self):
        from window.theme_dialog import ThemeDialog
        dialog = ThemeDialog(self.login_window, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.apply_theme()
    
    def apply_light_theme(self, color):
        light_style = f"""
        QMainWindow, QWidget {{
            background-color: #f5f5f5;
            color: #333333;
        }}
        QTabWidget::pane {{
            border: 1px solid #cccccc;
            background-color: #ffffff;
        }}
        QTabBar::tab {{
            background-color: #e0e0e0;
            color: #333333;
            padding: 8px 16px;
            border: 1px solid #cccccc;
        }}
        QTabBar::tab:selected {{
            background-color: {color};
            color: white;
        }}
        QPushButton {{
            background-color: {color};
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: {self.darken_color(color)};
        }}
        QLineEdit, QSpinBox, QComboBox, QTextEdit {{
            padding: 8px;
            border: 2px solid #cccccc;
            border-radius: 4px;
            background-color: white;
            color: #333333;
            selection-background-color: {color};
        }}
        QLineEdit:focus, QSpinBox:focus, QComboBox:focus, QTextEdit:focus {{
            border-color: {color};
        }}
        QComboBox::drop-down {{
            border: 1px solid #cccccc;
            background-color: {color};
        }}
        QComboBox QAbstractItemView {{
            border: 2px solid #cccccc;
            background-color: white;
            color: #333333;
            selection-background-color: {color};
            selection-color: white;
        }}
        QTableWidget {{
            background-color: white;
            color: #333333;
            gridline-color: #cccccc;
            alternate-background-color: #f8f8f8;
        }}
        QHeaderView::section {{
            background-color: {color};
            color: white;
            padding: 8px;
            border: 1px solid #cccccc;
            font-weight: bold;
        }}
        QGroupBox {{
            font-weight: bold;
            border: 2px solid #cccccc;
            border-radius: 5px;
            margin-top: 1ex;
            padding-top: 10px;
            background-color: #fafafa;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
            color: {color};
            background-color: #fafafa;
        }}
        QCheckBox {{
            color: #333333;
            spacing: 5px;
        }}
        QCheckBox::indicator {{
            width: 16px;
            height: 16px;
            border: 2px solid #cccccc;
            border-radius: 3px;
            background-color: white;
        }}
        QCheckBox::indicator:checked {{
            background-color: {color};
            border-color: {color};
        }}
        QSpinBox::up-button, QSpinBox::down-button {{
            background-color: {color};
            border: 1px solid #cccccc;
            width: 16px;
            border-radius: 2px;
        }}
        QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
            background-color: {self.darken_color(color)};
        }}
        QSpinBox::up-arrow {{
            border-left: 4px solid {color};
            border-right: 4px solid {color};
            border-bottom: 8px solid white;
            width: 0px;
            height: 0px;
        }}
        QSpinBox::down-arrow {{
            border-left: 4px solid {color};
            border-right: 4px solid {color};
            border-top: 8px solid white;
            width: 0px;
            height: 0px;
        }}
        QComboBox::down-arrow {{
            border-left: 4px solid {color};
            border-right: 4px solid {color};
            border-top: 8px solid white;
            width: 0px;
            height: 0px;
        }}
        QComboBox::down-arrow:on {{
            border-top: {color};
            border-bottom: 8px solid white;
        }}
        QDialog {{
            background-color: #f5f5f5;
            color: #333333;
        }}
        QMessageBox {{
            background-color: #f5f5f5;
            color: #333333;
        }}
        """
        self.setStyleSheet(light_style)

    def apply_dark_theme(self, color):
        dark_style = f"""
        QMainWindow, QWidget {{
            background-color: #2b2b2b;
            color: #ffffff;
        }}
        QTabWidget::pane {{
            border: 1px solid #555555;
            background-color: #3c3c3c;
        }}
        QTabBar::tab {{
            background-color: #404040;
            color: #ffffff;
            padding: 8px 16px;
            border: 1px solid #555555;
        }}
        QTabBar::tab:selected {{
            background-color: {color};
            color: white;
        }}
        QPushButton {{
            background-color: {color};
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: {self.darken_color(color)};
        }}
        QLineEdit, QSpinBox, QComboBox, QTextEdit {{
            padding: 8px;
            border: 2px solid #555555;
            border-radius: 4px;
            background-color: #404040;
            color: #ffffff;
            selection-background-color: {color};
        }}
        QLineEdit:focus, QSpinBox:focus, QComboBox:focus, QTextEdit:focus {{
            border-color: {color};
        }}
        QComboBox::drop-down {{
            border: 1px solid #555555;
            background-color: {color};
        }}
        QComboBox QAbstractItemView {{
            border: 2px solid #555555;
            background-color: #404040;
            color: #ffffff;
            selection-background-color: {color};
            selection-color: white;
        }}
        QTableWidget {{
            background-color: #404040;
            color: #ffffff;
            gridline-color: #555555;
            alternate-background-color: #484848;
        }}
        QHeaderView::section {{
            background-color: {color};
            color: white;
            padding: 8px;
            border: 1px solid #555555;
            font-weight: bold;
        }}
        QGroupBox {{
            font-weight: bold;
            border: 2px solid #555555;
            border-radius: 5px;
            margin-top: 1ex;
            padding-top: 10px;
            background-color: #353535;
            color: #ffffff;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
            color: {color};
            background-color: #353535;
        }}
        QCheckBox {{
            color: #ffffff;
            spacing: 5px;
        }}
        QCheckBox::indicator {{
            width: 16px;
            height: 16px;
            border: 2px solid #555555;
            border-radius: 3px;
            background-color: #404040;
        }}
        QCheckBox::indicator:checked {{
            background-color: {color};
            border-color: {color};
        }}
        QSpinBox::up-button, QSpinBox::down-button {{
            background-color: {color};
            border: 1px solid #555555;
            width: 16px;
            border-radius: 2px;
        }}
        QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
            background-color: {self.darken_color(color)};
        }}
        QSpinBox::up-arrow {{
            border-left: 4px solid {color};
            border-right: 4px solid {color};
            border-bottom: 8px solid white;
            width: 0px;
            height: 0px;
        }}
        QSpinBox::down-arrow {{
            border-left: 4px solid {color};
            border-right: 4px solid {color};
            border-top: 8px solid white;
            width: 0px;
            height: 0px;
        }}
        QComboBox::down-arrow {{
            border-left: 4px solid {color};
            border-right: 4px solid {color};
            border-top: 8px solid white;
            width: 0px;
            height: 0px;
        }}
        QComboBox::down-arrow:on {{
            border-top: {color};
            border-bottom: 8px solid white;
        }}
        QDialog {{
            background-color: #2b2b2b;
            color: #ffffff;
        }}
        QMessageBox {{
            background-color: #2b2b2b;
            color: #ffffff;
        }}
        """
        self.setStyleSheet(dark_style)

    def darken_color(self, color):
        if color == '#2196F3': return '#1976D2'
        elif color == '#4CAF50': return '#388E3C'
        elif color == '#F44336': return '#D32F2F'
        elif color == '#9C27B0': return '#7B1FA2'
        elif color == '#FF9800': return '#F57C00'
        elif color == '#757575': return '#616161'  
        return color