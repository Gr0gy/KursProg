from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QTableWidget,
                             QTableWidgetItem, QSpinBox, QMessageBox, QHeaderView,
                             QDialog, QDialogButtonBox, QFormLayout, QCheckBox,
                             QGroupBox, QTextEdit)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class CashierWindow(QMainWindow):
    def __init__(self, db, user, login_window):
        super().__init__()
        self.db = db
        self.user = user
        self.login_window = login_window
        self.cart = []
        self.delivery_customer = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle(f'Касса - Магазин бытовой техники ({self.user["full_name"]})')
        self.setMinimumSize(1100, 900)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        
        # Верхняя панель
        top_panel = QHBoxLayout()
        user_info = QLabel(f'Кассир: {self.user["full_name"]} | Склад: {self.user["warehouse_name"]}')
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
        
        # Заголовок
        title = QLabel('Оформление продаж')
        title.setFont(QFont('Arial', 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Таблица товаров
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(6)
        self.products_table.setHorizontalHeaderLabels([
            'ID', 'Название', 'Категория', 'Бренд', 'Цена', 'В наличии'
        ])
        self.products_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Поля для добавления в корзину
        sale_layout = QHBoxLayout()
        self.product_id_input = QSpinBox()
        self.product_id_input.setMinimum(1)
        
        self.quantity_input = QSpinBox()
        self.quantity_input.setMinimum(1)
        self.quantity_input.setMaximum(100)
        
        add_to_cart_btn = QPushButton('Добавить в корзину')
        add_to_cart_btn.clicked.connect(self.add_to_cart)
        
        sale_layout.addWidget(QLabel('ID товара:'))
        sale_layout.addWidget(self.product_id_input)
        sale_layout.addWidget(QLabel('Количество:'))
        sale_layout.addWidget(self.quantity_input)
        sale_layout.addWidget(add_to_cart_btn)
        
        # Корзина
        cart_label = QLabel('Корзина:')
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(6)
        self.cart_table.setHorizontalHeaderLabels(['ID', 'Название', 'Количество', 'Цена за шт.', 'Сумма', 'Действие'])
        self.cart_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Кнопки корзины
        cart_buttons_layout = QHBoxLayout()
        complete_sale_btn = QPushButton('Оформить продажу')
        complete_sale_btn.clicked.connect(self.complete_sale)
        clear_cart_btn = QPushButton('Очистить корзину')
        clear_cart_btn.clicked.connect(self.clear_cart)
        
        cart_buttons_layout.addWidget(complete_sale_btn)
        cart_buttons_layout.addWidget(clear_cart_btn)
        
        # Общая сумма
        self.total_label = QLabel('Общая сумма: 0 руб.')
        self.total_label.setFont(QFont('Arial', 12, QFont.Weight.Bold))
        
        # НОВЫЙ БЛОК: Доставка
        delivery_group = QGroupBox("Доставка")
        delivery_layout = QVBoxLayout()
        
        self.delivery_checkbox = QCheckBox('Оформить доставку')
        self.delivery_checkbox.stateChanged.connect(self.toggle_delivery_fields)
        
        delivery_fields_layout = QHBoxLayout()
        
        self.customer_phone_input = QLineEdit()
        self.customer_phone_input.setPlaceholderText('Телефон клиента')
        
        find_customer_btn = QPushButton('Найти клиента')
        find_customer_btn.clicked.connect(self.find_customer)
        
        create_customer_btn = QPushButton('Создать клиента')
        create_customer_btn.clicked.connect(self.create_customer)
        
        delivery_fields_layout.addWidget(QLabel('Телефон:'))
        delivery_fields_layout.addWidget(self.customer_phone_input)
        delivery_fields_layout.addWidget(find_customer_btn)
        delivery_fields_layout.addWidget(create_customer_btn)
        
        self.customer_info_label = QLabel('Клиент не выбран')
        
        self.delivery_address_input = QTextEdit()
        self.delivery_address_input.setPlaceholderText('Адрес доставки')
        self.delivery_address_input.setMaximumHeight(60)
        
        self.delivery_notes_input = QLineEdit()
        self.delivery_notes_input.setPlaceholderText('Примечания к доставке')
        
        delivery_layout.addWidget(self.delivery_checkbox)
        delivery_layout.addLayout(delivery_fields_layout)
        delivery_layout.addWidget(self.customer_info_label)
        delivery_layout.addWidget(QLabel('Адрес доставки:'))
        delivery_layout.addWidget(self.delivery_address_input)
        delivery_layout.addWidget(QLabel('Примечания:'))
        delivery_layout.addWidget(self.delivery_notes_input)
        
        delivery_group.setLayout(delivery_layout)
        
        layout.addLayout(top_panel)
        layout.addWidget(title)
        layout.addWidget(QLabel('Доступные товары:'))
        layout.addWidget(self.products_table)
        layout.addLayout(sale_layout)
        layout.addWidget(cart_label)
        layout.addWidget(self.cart_table)
        layout.addLayout(cart_buttons_layout)
        layout.addWidget(self.total_label)
        layout.addWidget(delivery_group)  # Добавляем блок доставки
        
        central_widget.setLayout(layout)
        
        self.load_products()
        self.toggle_delivery_fields()  # Инициализируем видимость полей доставки
    
    def toggle_delivery_fields(self):
        """Включает/выключает поля доставки"""
        enabled = self.delivery_checkbox.isChecked()
        self.customer_phone_input.setEnabled(enabled)
        self.delivery_address_input.setEnabled(enabled)
        self.delivery_notes_input.setEnabled(enabled)
    
    def find_customer(self):
        """Поиск клиента по телефону"""
        phone = self.customer_phone_input.text()
        if not phone:
            QMessageBox.warning(self, 'Ошибка', 'Введите телефон для поиска')
            return
        
        customer = self.db.get_customer_by_phone(phone)
        if customer:
            self.delivery_customer = customer
            self.customer_info_label.setText(f"Клиент: {customer['full_name']}, {customer['phone']}")
            self.delivery_address_input.setPlainText(customer['address'])
        else:
            QMessageBox.information(self, 'Информация', 'Клиент не найден. Создайте нового клиента.')
    
    def create_customer(self):
        """Создание нового клиента"""
        from customer_dialog import CustomerDialog
        dialog = CustomerDialog(self.db, None, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Обновляем поле телефона после создания клиента
            phone = self.customer_phone_input.text()
            if phone:
                self.find_customer()
    
    def load_products(self):
        products = self.db.get_products_with_quantity(self.user['warehouse_id'])
        self.products_table.setRowCount(len(products))
        
        for row, product in enumerate(products):
            self.products_table.setItem(row, 0, QTableWidgetItem(str(product['id'])))
            self.products_table.setItem(row, 1, QTableWidgetItem(product['name']))
            self.products_table.setItem(row, 2, QTableWidgetItem(product['category']))
            self.products_table.setItem(row, 3, QTableWidgetItem(product['brand']))
            self.products_table.setItem(row, 4, QTableWidgetItem(f"{product['price']:.2f}"))
            self.products_table.setItem(row, 5, QTableWidgetItem(str(product['quantity'])))
    
    def add_to_cart(self):
        product_id = self.product_id_input.value()
        quantity = self.quantity_input.value()
        
        products = self.db.get_products_with_quantity(self.user['warehouse_id'])
        product = next((p for p in products if p['id'] == product_id), None)
        
        if not product:
            QMessageBox.warning(self, 'Ошибка', 'Товар не найден')
            return
        
        if product['quantity'] < quantity:
            QMessageBox.warning(self, 'Ошибка', f'Недостаточно товара в наличии. Доступно: {product["quantity"]}')
            return
        
        # Проверяем, есть ли товар уже в корзине
        for item in self.cart:
            if item['id'] == product_id:
                item['quantity'] += quantity
                break
        else:
            self.cart.append({
                'id': product_id,
                'name': product['name'],
                'quantity': quantity,
                'price': product['price']
            })
        
        self.update_cart_display()
    
    def update_cart_display(self):
        self.cart_table.setRowCount(len(self.cart))
        total = 0
        
        for row, item in enumerate(self.cart):
            item_total = item['quantity'] * item['price']
            total += item_total
            
            self.cart_table.setItem(row, 0, QTableWidgetItem(str(item['id'])))
            self.cart_table.setItem(row, 1, QTableWidgetItem(item['name']))
            self.cart_table.setItem(row, 2, QTableWidgetItem(str(item['quantity'])))
            self.cart_table.setItem(row, 3, QTableWidgetItem(f"{item['price']:.2f}"))
            self.cart_table.setItem(row, 4, QTableWidgetItem(f"{item_total:.2f}"))
            
            remove_btn = QPushButton('Удалить')
            remove_btn.clicked.connect(lambda checked, r=row: self.remove_from_cart(r))
            self.cart_table.setCellWidget(row, 5, remove_btn)
        
        self.total_label.setText(f'Общая сумма: {total:.2f} руб.')
    
    def remove_from_cart(self, row):
        self.cart.pop(row)
        self.update_cart_display()
    
    def clear_cart(self):
        self.cart.clear()
        self.update_cart_display()
    
    def complete_sale(self):
        if not self.cart:
            QMessageBox.warning(self, 'Ошибка', 'Корзина пуста')
            return
        
        # Проверяем наличие товара
        for item in self.cart:
            products = self.db.get_products_with_quantity(self.user['warehouse_id'])
            product = next((p for p in products if p['id'] == item['id']), None)
            if not product or product['quantity'] < item['quantity']:
                QMessageBox.warning(self, 'Ошибка', f'Недостаточно товара "{item["name"]}" в наличии')
                return
        
        # Оформляем продажу
        for item in self.cart:
            success = self.db.add_sale(
                item['id'],
                item['quantity'],
                item['quantity'] * item['price'],
                self.user['id'],
                self.user['warehouse_id']
            )
            
            if not success:
                QMessageBox.critical(self, 'Ошибка', f'Ошибка при оформлении продажи товара "{item["name"]}"')
                return
        
        # Если выбрана доставка
        if self.delivery_checkbox.isChecked():
            if not self.delivery_customer and not self.customer_phone_input.text():
                QMessageBox.warning(self, 'Ошибка', 'Для доставки необходимо указать клиента')
                return
            
            if not self.delivery_address_input.toPlainText():
                QMessageBox.warning(self, 'Ошибка', 'Для доставки необходимо указать адрес')
                return
            
            # Если клиент не найден, создаем нового
            if not self.delivery_customer:
                phone = self.customer_phone_input.text()
                if not phone:
                    QMessageBox.warning(self, 'Ошибка', 'Введите телефон клиента')
                    return
                
                # В реальном приложении здесь нужно запросить остальные данные клиента
                # Для упрощения создаем клиента с минимальными данными
                address = self.delivery_address_input.toPlainText()
                success = self.db.create_customer(
                    f"Клиент {phone}",  # Временное имя
                    phone,
                    "",  # email
                    address
                )
                
                if not success:
                    QMessageBox.warning(self, 'Ошибка', 'Ошибка при создании клиента')
                    return
                
                # Получаем созданного клиента
                self.delivery_customer = self.db.get_customer_by_phone(phone)
            
            # Получаем последнюю продажу (предполагаем, что это продажа только что добавленного товара)
            # В реальном приложении нужно получить ID конкретной продажи
            sales = self.db.get_sales_report(self.user['warehouse_id'])
            if sales:
                last_sale_id = sales[0]['id']
                
                # Создаем доставку
                success = self.db.create_delivery(
                    last_sale_id,
                    self.delivery_customer['id'],
                    self.delivery_address_input.toPlainText(),
                    self.delivery_notes_input.text()
                )
                
                if not success:
                    QMessageBox.warning(self, 'Ошибка', 'Ошибка при создании доставки')
        
        QMessageBox.information(self, 'Успех', 'Продажа успешно оформлена!')
        self.clear_cart()
        self.load_products()
        
        # Сбрасываем данные доставки
        self.delivery_checkbox.setChecked(False)
        self.customer_phone_input.clear()
        self.delivery_address_input.clear()
        self.delivery_notes_input.clear()
        self.customer_info_label.setText('Клиент не выбран')
        self.delivery_customer = None
    
    def logout(self):
        self.login_window.show()
        self.close()
    
    def change_theme(self):
        from theme_dialog import ThemeDialog
        dialog = ThemeDialog(self.login_window, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.apply_theme()
            
    def apply_theme(self):
        """Применяет тему от login_window"""
        theme_settings = self.login_window.get_theme_settings()
        if theme_settings['theme'] == 'light':
            self.apply_light_theme(theme_settings['color'])
        else:
            self.apply_dark_theme(theme_settings['color'])
            
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