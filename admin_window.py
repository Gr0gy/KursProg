from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QTableWidget,
                             QTableWidgetItem, QMessageBox, QHeaderView,
                             QTabWidget, QDialog, QDialogButtonBox, QFormLayout,
                             QComboBox, QSpinBox, QTextEdit, QGroupBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from customer_dialog import CustomerDialog

class AdminWindow(QMainWindow):
    def __init__(self, db, user, login_window):
        super().__init__()
        self.db = db
        self.user = user
        self.login_window = login_window
        self.init_ui()
        # Применяем тему сразу после инициализации
        self.apply_theme()
    
    def init_ui(self):
        self.setWindowTitle(f'Админ панель - Магазин бытовой техники ({self.user["full_name"]})')
        self.setMinimumSize(1400, 900)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        
        # Верхняя панель
        top_panel = QHBoxLayout()
        user_info = QLabel(f'Администратор: {self.user["full_name"]}')
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

        
        # Вкладка регистрации сотрудников
        self.registration_tab = QWidget()
        self.init_registration_tab()
        
        # Вкладка управления складами
        self.warehouses_tab = QWidget()
        self.init_warehouses_tab()
        
        # Вкладка учета склада
        self.store_tab = QWidget()
        self.init_store_tab()
        
        # Вкладка продаж
        self.sales_tab = QWidget()
        self.init_sales_tab()
        
        # Вкладка клиентов
        self.customers_tab = QWidget()
        self.init_customers_tab()
        
        # Вкладка доставок
        self.deliveries_tab = QWidget()
        self.init_deliveries_tab()
        
        self.tabs.addTab(self.registration_tab, "Регистрация сотрудников")
        self.tabs.addTab(self.warehouses_tab, "Управление складами")
        self.tabs.addTab(self.store_tab, "Учет склада")
        self.tabs.addTab(self.sales_tab, "Продажи")
        self.tabs.addTab(self.customers_tab, "Клиенты")
        self.tabs.addTab(self.deliveries_tab, "Доставки")
        
        layout.addLayout(top_panel)
        layout.addWidget(self.tabs)
        
        central_widget.setLayout(layout)
        
        self.load_customers()
        self.load_all_deliveries()
    
    def init_customers_tab(self):
        layout = QVBoxLayout()
        
        title = QLabel('Управление клиентами')
        title.setFont(QFont('Arial', 12, QFont.Weight.Bold))
        
        # Панель управления
        control_panel = QHBoxLayout()
        
        self.customer_search_input = QLineEdit()
        self.customer_search_input.setPlaceholderText('Поиск по ФИО или телефону...')
        self.customer_search_input.textChanged.connect(self.search_customers)
        
        create_customer_btn = QPushButton('Создать клиента')
        create_customer_btn.clicked.connect(self.create_customer)
        
        refresh_btn = QPushButton('Обновить')
        refresh_btn.clicked.connect(self.load_customers)
        
        control_panel.addWidget(QLabel('Поиск:'))
        control_panel.addWidget(self.customer_search_input)
        control_panel.addWidget(create_customer_btn)
        control_panel.addWidget(refresh_btn)
        control_panel.addStretch()
        
        self.customers_table = QTableWidget()
        self.customers_table.setColumnCount(6)
        self.customers_table.setHorizontalHeaderLabels([
            'ID', 'ФИО', 'Телефон', 'Email', 'Адрес', 'Действия'
        ])
        self.customers_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(title)
        layout.addLayout(control_panel)
        layout.addWidget(self.customers_table)
        
        self.customers_tab.setLayout(layout)
    
    def init_deliveries_tab(self):
        layout = QVBoxLayout()
        
        title = QLabel('Управление доставками')
        title.setFont(QFont('Arial', 12, QFont.Weight.Bold))
        
        # Фильтры
        filter_layout = QHBoxLayout()
        
        self.status_filter_combo = QComboBox()
        self.status_filter_combo.addItem('Все статусы', 'all')
        self.status_filter_combo.addItem('Ожидает', 'pending')
        self.status_filter_combo.addItem('Назначена', 'assigned')
        self.status_filter_combo.addItem('В процессе', 'in_progress')
        self.status_filter_combo.addItem('Доставлена', 'delivered')
        self.status_filter_combo.currentIndexChanged.connect(self.load_all_deliveries)
        
        self.warehouse_filter_combo = QComboBox()
        self.warehouse_filter_combo.addItem('Все склады', 'all')
        warehouses = self.db.get_all_warehouses()
        for warehouse in warehouses:
            self.warehouse_filter_combo.addItem(warehouse['name'], warehouse['id'])
        self.warehouse_filter_combo.currentIndexChanged.connect(self.load_all_deliveries)
        
        refresh_btn = QPushButton('Обновить')
        refresh_btn.clicked.connect(self.load_all_deliveries)
        
        filter_layout.addWidget(QLabel('Статус:'))
        filter_layout.addWidget(self.status_filter_combo)
        filter_layout.addWidget(QLabel('Склад:'))
        filter_layout.addWidget(self.warehouse_filter_combo)
        filter_layout.addWidget(refresh_btn)
        filter_layout.addStretch()
        
        self.deliveries_table = QTableWidget()
        self.deliveries_table.setColumnCount(10)
        self.deliveries_table.setHorizontalHeaderLabels([
            'ID', 'Клиент', 'Телефон', 'Адрес', 'Товар', 'Количество', 'Статус', 'Кладовщик', 'Транспорт', 'Действия'
        ])
        self.deliveries_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(title)
        layout.addLayout(filter_layout)
        layout.addWidget(self.deliveries_table)
        
        self.deliveries_tab.setLayout(layout)
    
    def load_customers(self):
        customers = self.db.get_all_customers()
        self.customers_table.setRowCount(len(customers))
        
        for row, customer in enumerate(customers):
            self.customers_table.setItem(row, 0, QTableWidgetItem(str(customer['id'])))
            self.customers_table.setItem(row, 1, QTableWidgetItem(customer['full_name']))
            self.customers_table.setItem(row, 2, QTableWidgetItem(customer['phone']))
            self.customers_table.setItem(row, 3, QTableWidgetItem(customer['email'] or ''))
            self.customers_table.setItem(row, 4, QTableWidgetItem(customer['address']))
            
            action_widget = QWidget()
            action_layout = QHBoxLayout()
            action_layout.setContentsMargins(0, 0, 0, 0)
            
            edit_btn = QPushButton('Редактировать')
            edit_btn.clicked.connect(lambda checked, c_id=customer['id']: self.edit_customer(c_id))
            
            delete_btn = QPushButton('Удалить')
            delete_btn.clicked.connect(lambda checked, c_id=customer['id']: self.delete_customer(c_id))
            
            action_layout.addWidget(edit_btn)
            action_layout.addWidget(delete_btn)
            action_widget.setLayout(action_layout)
            
            self.customers_table.setCellWidget(row, 5, action_widget)
    
    def search_customers(self):
        search_text = self.customer_search_input.text().lower()
        if not search_text:
            self.load_customers()
            return
        
        customers = self.db.get_all_customers()
        filtered_customers = [
            c for c in customers 
            if search_text in c['full_name'].lower() or search_text in c['phone'].lower()
        ]
        
        self.customers_table.setRowCount(len(filtered_customers))
        
        for row, customer in enumerate(filtered_customers):
            self.customers_table.setItem(row, 0, QTableWidgetItem(str(customer['id'])))
            self.customers_table.setItem(row, 1, QTableWidgetItem(customer['full_name']))
            self.customers_table.setItem(row, 2, QTableWidgetItem(customer['phone']))
            self.customers_table.setItem(row, 3, QTableWidgetItem(customer['email'] or ''))
            self.customers_table.setItem(row, 4, QTableWidgetItem(customer['address']))
            
            action_widget = QWidget()
            action_layout = QHBoxLayout()
            action_layout.setContentsMargins(0, 0, 0, 0)
            
            edit_btn = QPushButton('Редактировать')
            edit_btn.clicked.connect(lambda checked, c_id=customer['id']: self.edit_customer(c_id))
            
            delete_btn = QPushButton('Удалить')
            delete_btn.clicked.connect(lambda checked, c_id=customer['id']: self.delete_customer(c_id))
            
            action_layout.addWidget(edit_btn)
            action_layout.addWidget(delete_btn)
            action_widget.setLayout(action_layout)
            
            self.customers_table.setCellWidget(row, 5, action_widget)
    
    def create_customer(self):
        dialog = CustomerDialog(self.db, None, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_customers()
    
    def edit_customer(self, customer_id):
        dialog = CustomerDialog(self.db, customer_id, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_customers()
    
    def delete_customer(self, customer_id):
        reply = QMessageBox.question(
            self, 'Подтверждение удаления',
            'Вы уверены, что хотите удалить этого клиента?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success = self.db.delete_customer(customer_id)
            if success:
                QMessageBox.information(self, 'Успех', 'Клиент удален')
                self.load_customers()
            else:
                QMessageBox.warning(self, 'Ошибка', 'Ошибка при удалении клиента')
    
    def load_all_deliveries(self):
        status_filter = self.status_filter_combo.currentData()
        warehouse_filter = self.warehouse_filter_combo.currentData()
        
        if warehouse_filter == 'all':
            deliveries = self.db.get_all_deliveries()
        else:
            deliveries = self.db.get_all_deliveries(warehouse_filter)
        
        # Применяем фильтр по статусу
        if status_filter != 'all':
            deliveries = [d for d in deliveries if d['status'] == status_filter]
        
        self.deliveries_table.setRowCount(len(deliveries))
        
        for row, delivery in enumerate(deliveries):
            self.deliveries_table.setItem(row, 0, QTableWidgetItem(str(delivery['id'])))
            self.deliveries_table.setItem(row, 1, QTableWidgetItem(delivery['customer_name']))
            self.deliveries_table.setItem(row, 2, QTableWidgetItem(delivery['customer_phone']))
            self.deliveries_table.setItem(row, 3, QTableWidgetItem(delivery['delivery_address']))
            self.deliveries_table.setItem(row, 4, QTableWidgetItem(delivery['product_name']))
            self.deliveries_table.setItem(row, 5, QTableWidgetItem(str(delivery['quantity'])))
            self.deliveries_table.setItem(row, 6, QTableWidgetItem(self.get_status_text(delivery['status'])))
            self.deliveries_table.setItem(row, 7, QTableWidgetItem(delivery['storekeeper_name']))
            self.deliveries_table.setItem(row, 8, QTableWidgetItem(delivery['vehicle_info']))
            
            action_widget = QWidget()
            action_layout = QHBoxLayout()
            action_layout.setContentsMargins(0, 0, 0, 0)
            
            if delivery['status'] in ['pending', 'assigned']:
                cancel_btn = QPushButton('Отменить')
                cancel_btn.clicked.connect(lambda checked, d_id=delivery['id']: self.cancel_delivery(d_id))
                action_layout.addWidget(cancel_btn)
            
            action_widget.setLayout(action_layout)
            
            self.deliveries_table.setCellWidget(row, 9, action_widget)
    
    def get_status_text(self, status):
        status_map = {
            'pending': 'Ожидает',
            'assigned': 'Назначена',
            'in_progress': 'В процессе',
            'delivered': 'Доставлена',
            'cancelled': 'Отменена'
        }
        return status_map.get(status, status)
    
    def cancel_delivery(self, delivery_id):
        reply = QMessageBox.question(
            self, 'Подтверждение отмены',
            'Вы уверены, что хотите отменить эту доставку?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Для отмены доставки обновляем статус
            conn = self.db._get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    UPDATE deliveries 
                    SET status = 'cancelled'
                    WHERE id = %s
                ''', (delivery_id,))
                conn.commit()
                QMessageBox.information(self, 'Успех', 'Доставка отменена')
                self.load_all_deliveries()
            except Exception as e:
                QMessageBox.warning(self, 'Ошибка', f'Ошибка при отмене доставки: {e}')
            finally:
                conn.close()
    
    def logout(self):
        self.login_window.show()
        self.close()
    
    # МЕТОДЫ ДЛЯ РАБОТЫ С ТЕМОЙ
    
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
    
    def init_registration_tab(self):
        layout = QVBoxLayout()
        
        # Форма регистрации
        form_group = QGroupBox("Регистрация нового сотрудника")
        form_layout = QFormLayout()
        
        self.emp_login_input = QLineEdit()
        self.emp_password_input = QLineEdit()
        self.emp_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.emp_full_name_input = QLineEdit()
        self.emp_role_combo = QComboBox()
        self.emp_role_combo.addItems(['admin', 'cashier', 'storekeeper'])
        
        self.emp_warehouse_combo = QComboBox()
        self.load_warehouses_combo()
        
        self.emp_phone_input = QLineEdit()
        self.emp_email_input = QLineEdit()
        
        register_btn = QPushButton('Зарегистрировать сотрудника')
        register_btn.clicked.connect(self.register_employee)
        
        form_layout.addRow('Логин:', self.emp_login_input)
        form_layout.addRow('Пароль:', self.emp_password_input)
        form_layout.addRow('ФИО:', self.emp_full_name_input)
        form_layout.addRow('Роль:', self.emp_role_combo)
        form_layout.addRow('Склад:', self.emp_warehouse_combo)
        form_layout.addRow('Телефон:', self.emp_phone_input)
        form_layout.addRow('Email:', self.emp_email_input)
        form_layout.addRow(register_btn)
        
        form_group.setLayout(form_layout)
        
        # Таблица сотрудников
        employees_label = QLabel('Зарегистрированные сотрудники:')
        
        # Кнопки управления сотрудниками
        employees_buttons_layout = QHBoxLayout()
        refresh_employees_btn = QPushButton('Обновить список')
        refresh_employees_btn.clicked.connect(self.load_employees)
        
        edit_employee_btn = QPushButton('Редактировать сотрудника')
        edit_employee_btn.clicked.connect(self.edit_employee)
        
        delete_employee_btn = QPushButton('Удалить выбранного сотрудника')
        delete_employee_btn.clicked.connect(self.delete_employee)
        
        employees_buttons_layout.addWidget(refresh_employees_btn)
        employees_buttons_layout.addWidget(edit_employee_btn)
        employees_buttons_layout.addWidget(delete_employee_btn)
        employees_buttons_layout.addStretch()
        
        self.employees_table = QTableWidget()
        self.employees_table.setColumnCount(7)
        self.employees_table.setHorizontalHeaderLabels(['ID', 'Логин', 'ФИО', 'Роль', 'Телефон', 'Email', 'Склад'])
        self.employees_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.employees_table.doubleClicked.connect(self.edit_employee)
        
        layout.addWidget(form_group)
        layout.addWidget(employees_label)
        layout.addLayout(employees_buttons_layout)
        layout.addWidget(self.employees_table)
        
        self.registration_tab.setLayout(layout)
        self.load_employees()
    
    def init_warehouses_tab(self):
        layout = QVBoxLayout()
        
        # Форма добавления склада
        form_group = QGroupBox("Добавление нового склада")
        form_layout = QFormLayout()
        
        self.warehouse_name_input = QLineEdit()
        self.warehouse_name_input.setPlaceholderText('Введите название склада')
        
        self.warehouse_address_input = QLineEdit()
        self.warehouse_address_input.setPlaceholderText('Введите адрес склада')
        
        add_warehouse_btn = QPushButton('Добавить склад')
        add_warehouse_btn.clicked.connect(self.add_warehouse)
        
        form_layout.addRow('Название склада:', self.warehouse_name_input)
        form_layout.addRow('Адрес склада:', self.warehouse_address_input)
        form_layout.addRow(add_warehouse_btn)
        
        form_group.setLayout(form_layout)
        
        # Таблица складов
        warehouses_label = QLabel('Существующие склады:')
        
        # Кнопки управления складами
        warehouses_buttons_layout = QHBoxLayout()
        refresh_warehouses_btn = QPushButton('Обновить список')
        refresh_warehouses_btn.clicked.connect(self.load_warehouses)
        
        edit_warehouse_btn = QPushButton('Редактировать склад')
        edit_warehouse_btn.clicked.connect(self.edit_warehouse)
        
        delete_warehouse_btn = QPushButton('Удалить склад')
        delete_warehouse_btn.clicked.connect(self.delete_warehouse)
        
        warehouses_buttons_layout.addWidget(refresh_warehouses_btn)
        warehouses_buttons_layout.addWidget(edit_warehouse_btn)
        warehouses_buttons_layout.addWidget(delete_warehouse_btn)
        warehouses_buttons_layout.addStretch()
        
        self.warehouses_table = QTableWidget()
        self.warehouses_table.setColumnCount(3)
        self.warehouses_table.setHorizontalHeaderLabels(['ID', 'Название', 'Адрес'])
        self.warehouses_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.warehouses_table.doubleClicked.connect(self.edit_warehouse)
        
        layout.addWidget(form_group)
        layout.addWidget(warehouses_label)
        layout.addLayout(warehouses_buttons_layout)
        layout.addWidget(self.warehouses_table)
        
        self.warehouses_tab.setLayout(layout)
        self.load_warehouses()
    
    def init_store_tab(self):
        layout = QVBoxLayout()
        
        # Фильтр отображения
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel('Отображение:'))
        
        self.view_combo = QComboBox()
        self.view_combo.addItems(['Текущий склад', 'Все склады'])
        self.view_combo.currentTextChanged.connect(self.load_products)
        
        filter_layout.addWidget(self.view_combo)
        filter_layout.addStretch()
        
        # Форма добавления товара
        form_group = QGroupBox("Добавление товара")
        form_layout = QHBoxLayout()
        
        self.product_name_input = QLineEdit()
        self.product_name_input.setPlaceholderText('Название')
        
        self.product_category_input = QLineEdit()
        self.product_category_input.setPlaceholderText('Категория')
        
        self.product_brand_input = QLineEdit()
        self.product_brand_input.setPlaceholderText('Бренд')
        
        self.product_price_input = QLineEdit()
        self.product_price_input.setPlaceholderText('Цена')
        
        self.product_min_quantity_input = QSpinBox()
        self.product_min_quantity_input.setMaximum(1000)
        self.product_min_quantity_input.setValue(0)
        
        add_product_btn = QPushButton('Добавить товар')
        add_product_btn.clicked.connect(self.add_product)
        
        delete_product_btn = QPushButton('Удалить товар')
        delete_product_btn.clicked.connect(self.delete_product)
        
        form_layout.addWidget(self.product_name_input)
        form_layout.addWidget(self.product_category_input)
        form_layout.addWidget(self.product_brand_input)
        form_layout.addWidget(self.product_price_input)
        form_layout.addWidget(QLabel('Мин.:'))
        form_layout.addWidget(self.product_min_quantity_input)
        form_layout.addWidget(add_product_btn)
        form_layout.addWidget(delete_product_btn)
        
        form_group.setLayout(form_layout)
        
        # Форма изменения количества
        quantity_group = QGroupBox("Изменение количества товара")
        quantity_layout = QHBoxLayout()
        
        self.quantity_product_id = QSpinBox()
        self.quantity_product_id.setMinimum(1)
        
        self.quantity_warehouse_combo = QComboBox()
        self.load_warehouses_combo_quantity()
        
        self.new_quantity_input = QSpinBox()
        self.new_quantity_input.setMaximum(10000)
        self.new_quantity_input.setValue(0)
        
        update_quantity_btn = QPushButton('Обновить количество')
        update_quantity_btn.clicked.connect(self.update_quantity)
        
        quantity_layout.addWidget(QLabel('ID товара:'))
        quantity_layout.addWidget(self.quantity_product_id)
        quantity_layout.addWidget(QLabel('Склад:'))
        quantity_layout.addWidget(self.quantity_warehouse_combo)
        quantity_layout.addWidget(QLabel('Новое количество:'))
        quantity_layout.addWidget(self.new_quantity_input)
        quantity_layout.addWidget(update_quantity_btn)
        
        quantity_group.setLayout(quantity_layout)
        
        # Таблица товаров
        products_label = QLabel('Товары:')
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(7)
        self.products_table.setHorizontalHeaderLabels(['ID', 'Название', 'Категория', 'Бренд', 'Цена', 'Количество', 'Мин. количество'])
        self.products_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        layout.addLayout(filter_layout)
        layout.addWidget(form_group)
        layout.addWidget(quantity_group)
        layout.addWidget(products_label)
        layout.addWidget(self.products_table)
        
        self.store_tab.setLayout(layout)
        self.load_products()
    
    def init_sales_tab(self):
        layout = QVBoxLayout()
        
        # Фильтр отображения
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel('Отображение:'))
        
        self.sales_view_combo = QComboBox()
        self.sales_view_combo.addItems(['Текущий склад', 'Все склады'])
        self.sales_view_combo.currentTextChanged.connect(self.load_sales)
        
        filter_layout.addWidget(self.sales_view_combo)
        filter_layout.addStretch()
        
        # Кнопка обновления
        refresh_btn = QPushButton('Обновить список продаж')
        refresh_btn.clicked.connect(self.load_sales)
        
        # Таблица продаж
        sales_label = QLabel('История продаж:')
        self.sales_table = QTableWidget()
        self.sales_table.setColumnCount(8)
        self.sales_table.setHorizontalHeaderLabels(['ID', 'Товар', 'Количество', 'Сумма', 'Дата', 'Кассир', 'Склад', 'Статус'])
        self.sales_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Кнопка отмены продажи
        cancel_sale_btn = QPushButton('Отменить выбранную продажу')
        cancel_sale_btn.clicked.connect(self.cancel_sale)
        
        layout.addLayout(filter_layout)
        layout.addWidget(refresh_btn)
        layout.addWidget(sales_label)
        layout.addWidget(self.sales_table)
        layout.addWidget(cancel_sale_btn)
        
        self.sales_tab.setLayout(layout)
        self.load_sales()
    
    def load_warehouses_combo(self):
        warehouses = self.db.get_all_warehouses()
        self.emp_warehouse_combo.clear()
        for warehouse in warehouses:
            self.emp_warehouse_combo.addItem(warehouse['name'], warehouse['id'])
    
    def load_warehouses_combo_quantity(self):
        warehouses = self.db.get_all_warehouses()
        self.quantity_warehouse_combo.clear()
        for warehouse in warehouses:
            self.quantity_warehouse_combo.addItem(warehouse['name'], warehouse['id'])
    
    def load_employees(self):
        employees = self.db.get_all_employees()
        self.employees_table.setRowCount(len(employees))
        
        for row, emp in enumerate(employees):
            self.employees_table.setItem(row, 0, QTableWidgetItem(str(emp['id'])))
            self.employees_table.setItem(row, 1, QTableWidgetItem(emp['login']))
            self.employees_table.setItem(row, 2, QTableWidgetItem(emp['full_name']))
            self.employees_table.setItem(row, 3, QTableWidgetItem(emp['role']))
            self.employees_table.setItem(row, 4, QTableWidgetItem(emp['phone']))
            self.employees_table.setItem(row, 5, QTableWidgetItem(emp['email']))
            self.employees_table.setItem(row, 6, QTableWidgetItem(emp['warehouse_name']))
    
    def load_warehouses(self):
        warehouses = self.db.get_all_warehouses()
        self.warehouses_table.setRowCount(len(warehouses))
        
        for row, warehouse in enumerate(warehouses):
            self.warehouses_table.setItem(row, 0, QTableWidgetItem(str(warehouse['id'])))
            self.warehouses_table.setItem(row, 1, QTableWidgetItem(warehouse['name']))
            self.warehouses_table.setItem(row, 2, QTableWidgetItem(warehouse['address']))
    
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
    
    def load_sales(self):
        view_type = self.sales_view_combo.currentText()
        
        if view_type == 'Текущий склад':
            sales = self.db.get_sales_report(self.user['warehouse_id'])
        else:
            sales = self.db.get_sales_report(None)
        
        self.sales_table.setRowCount(len(sales))
        
        for row, sale in enumerate(sales):
            self.sales_table.setItem(row, 0, QTableWidgetItem(str(sale['id'])))
            self.sales_table.setItem(row, 1, QTableWidgetItem(sale['product_name']))
            self.sales_table.setItem(row, 2, QTableWidgetItem(str(sale['quantity'])))
            self.sales_table.setItem(row, 3, QTableWidgetItem(str(sale['total_price'])))
            self.sales_table.setItem(row, 4, QTableWidgetItem(sale['sale_date']))
            self.sales_table.setItem(row, 5, QTableWidgetItem(sale['cashier_name']))
            self.sales_table.setItem(row, 6, QTableWidgetItem(sale['warehouse_name']))
            self.sales_table.setItem(row, 7, QTableWidgetItem(sale['status']))
    
    def register_employee(self):
        login = self.emp_login_input.text()
        password = self.emp_password_input.text()
        full_name = self.emp_full_name_input.text()
        role = self.emp_role_combo.currentText()
        warehouse_id = self.emp_warehouse_combo.currentData()
        phone = self.emp_phone_input.text()
        email = self.emp_email_input.text()
        
        if not login or not password or not full_name:
            QMessageBox.warning(self, 'Ошибка', 'Заполните логин, пароль и ФИО')
            return
        
        if not warehouse_id:
            QMessageBox.warning(self, 'Ошибка', 'Выберите склад для сотрудника')
            return
        
        if self.db.register_employee(login, password, full_name, role, warehouse_id, phone, email):
            QMessageBox.information(self, 'Успех', 'Сотрудник зарегистрирован')
            self.clear_employee_form()
            self.load_employees()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Логин уже существует')
    
    def edit_employee(self):
        selected = self.employees_table.selectedItems()
        if not selected:
            QMessageBox.warning(self, 'Ошибка', 'Выберите сотрудника для редактирования')
            return
        
        employee_id = int(self.employees_table.item(selected[0].row(), 0).text())
        employee_login = self.employees_table.item(selected[0].row(), 1).text()
        
        # Нельзя редактировать главного администратора
        if employee_login == 'admin':
            QMessageBox.warning(self, 'Ошибка', 'Нельзя редактировать главного администратора')
            return
        
        # Открываем диалог редактирования
        dialog = EditEmployeeDialog(self.db, employee_id, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_employees()
            QMessageBox.information(self, 'Успех', 'Данные сотрудника обновлены')
    
    def delete_employee(self):
        selected = self.employees_table.selectedItems()
        if not selected:
            QMessageBox.warning(self, 'Ошибка', 'Выберите сотрудника для удаления')
            return
        
        employee_id = int(self.employees_table.item(selected[0].row(), 0).text())
        employee_login = self.employees_table.item(selected[0].row(), 1).text()
        employee_name = self.employees_table.item(selected[0].row(), 2).text()
        
        # Нельзя удалить самого себя
        if employee_id == self.user['id']:
            QMessageBox.warning(self, 'Ошибка', 'Нельзя удалить свою учетную запись')
            return
        
        # Нельзя удалить администратора по умолчанию
        if employee_login == 'admin':
            QMessageBox.warning(self, 'Ошибка', 'Нельзя удалить главного администратора')
            return
        
        reply = QMessageBox.question(self, 'Подтверждение удаления', 
                                   f'Вы уверены, что хотите удалить сотрудника:\n'
                                   f'Логин: {employee_login}\n'
                                   f'ФИО: {employee_name}?',
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.db.delete_employee(employee_id):
                QMessageBox.information(self, 'Успех', 'Сотрудник удален')
                self.load_employees()
            else:
                QMessageBox.warning(self, 'Ошибка', 'Не удалось удалить сотрудника. Возможно, у сотрудника есть связанные продажи.')
    
    def add_warehouse(self):
        name = self.warehouse_name_input.text()
        address = self.warehouse_address_input.text()
        
        if not name or not address:
            QMessageBox.warning(self, 'Ошибка', 'Заполните название и адрес склада')
            return
        
        if self.db.add_warehouse(name, address):
            QMessageBox.information(self, 'Успех', 'Склад добавлен')
            self.clear_warehouse_form()
            self.load_warehouses()
            self.load_warehouses_combo()
            self.load_warehouses_combo_quantity()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Ошибка при добавлении склада')
    
    def edit_warehouse(self):
        selected = self.warehouses_table.selectedItems()
        if not selected:
            QMessageBox.warning(self, 'Ошибка', 'Выберите склад для редактирования')
            return
        
        warehouse_id = int(self.warehouses_table.item(selected[0].row(), 0).text())
        warehouse_name = self.warehouses_table.item(selected[0].row(), 1).text()
        
        # Открываем диалог редактирования
        dialog = EditWarehouseDialog(self.db, warehouse_id, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_warehouses()
            self.load_warehouses_combo()
            self.load_warehouses_combo_quantity()
            QMessageBox.information(self, 'Успех', 'Данные склада обновлены')
    
    def delete_warehouse(self):
        selected = self.warehouses_table.selectedItems()
        if not selected:
            QMessageBox.warning(self, 'Ошибка', 'Выберите склад для удаления')
            return
        
        warehouse_id = int(self.warehouses_table.item(selected[0].row(), 0).text())
        warehouse_name = self.warehouses_table.item(selected[0].row(), 1).text()
        
        # Проверяем, есть ли сотрудники на этом складе
        employees_on_warehouse = self.db.get_employees_by_warehouse(warehouse_id)
        if employees_on_warehouse:
            QMessageBox.warning(self, 'Ошибка', 
                              f'Нельзя удалить склад "{warehouse_name}". На складе зарегистрированы сотрудники.')
            return
        
        reply = QMessageBox.question(self, 'Подтверждение удаления', 
                                   f'Вы уверены, что хотите удалить склад:\n'
                                   f'Название: {warehouse_name}?',
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.db.delete_warehouse(warehouse_id):
                QMessageBox.information(self, 'Успех', 'Склад удален')
                self.load_warehouses()
                self.load_warehouses_combo()
                self.load_warehouses_combo_quantity()
            else:
                QMessageBox.warning(self, 'Ошибка', 'Не удалось удалить склад')
    
    def add_product(self):
        name = self.product_name_input.text()
        category = self.product_category_input.text()
        brand = self.product_brand_input.text()
        price_text = self.product_price_input.text()
        min_quantity = self.product_min_quantity_input.value()
        
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
    
    def delete_product(self):
        selected = self.products_table.selectedItems()
        if not selected:
            QMessageBox.warning(self, 'Ошибка', 'Выберите товар для удаления')
            return
        
        product_id = int(self.products_table.item(selected[0].row(), 0).text())
        product_name = self.products_table.item(selected[0].row(), 1).text()
        
        reply = QMessageBox.question(self, 'Подтверждение удаления', 
                                   f'Вы уверены, что хотите удалить товар "{product_name}"?',
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.db.delete_product(product_id):
                QMessageBox.information(self, 'Успех', 'Товар удален')
                self.load_products()
            else:
                QMessageBox.warning(self, 'Ошибка', 'Ошибка при удалении товара')
    
    def update_quantity(self):
        product_id = self.quantity_product_id.value()
        warehouse_id = self.quantity_warehouse_combo.currentData()
        new_quantity = self.new_quantity_input.value()
        
        if product_id <= 0:
            QMessageBox.warning(self, 'Ошибка', 'Введите корректный ID товара')
            return
        
        if not warehouse_id:
            QMessageBox.warning(self, 'Ошибка', 'Выберите склад')
            return
        
        if new_quantity < 0:
            QMessageBox.warning(self, 'Ошибка', 'Количество не может быть отрицательным')
            return
        
        if self.db.update_product_quantity(product_id, warehouse_id, new_quantity):
            QMessageBox.information(self, 'Успех', 'Количество товара обновлено')
            self.load_products()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Ошибка при обновлении количества')
    
    def cancel_sale(self):
        selected = self.sales_table.selectedItems()
        if not selected:
            QMessageBox.warning(self, 'Ошибка', 'Выберите продажу для отмены')
            return
        
        sale_id = int(self.sales_table.item(selected[0].row(), 0).text())
        product_name = self.sales_table.item(selected[0].row(), 1).text()
        status = self.sales_table.item(selected[0].row(), 7).text()
        
        if status == 'cancelled':
            QMessageBox.warning(self, 'Ошибка', 'Эта продажа уже отменена')
            return
        
        reply = QMessageBox.question(self, 'Подтверждение отмены', 
                                   f'Вы уверены, что хотите отменить продажу "{product_name}"?',
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.db.cancel_sale(sale_id):
                QMessageBox.information(self, 'Успех', 'Продажа отменена')
                self.load_sales()
            else:
                QMessageBox.warning(self, 'Ошибка', 'Ошибка при отмене продажи')
    
    def clear_employee_form(self):
        self.emp_login_input.clear()
        self.emp_password_input.clear()
        self.emp_full_name_input.clear()
        self.emp_phone_input.clear()
        self.emp_email_input.clear()
    
    def clear_warehouse_form(self):
        self.warehouse_name_input.clear()
        self.warehouse_address_input.clear()
    
    def clear_product_form(self):
        self.product_name_input.clear()
        self.product_category_input.clear()
        self.product_brand_input.clear()
        self.product_price_input.clear()
        self.product_min_quantity_input.setValue(0)
    
    def logout(self):
        reply = QMessageBox.question(self, 'Подтверждение выхода', 
                                   'Вы уверены, что хотите выйти из системы?',
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.close()
            self.login_window.logout()


class EditEmployeeDialog(QDialog):
    def __init__(self, db, employee_id, parent=None):
        super().__init__(parent)
        self.db = db
        self.employee_id = employee_id
        self.init_ui()
        self.load_employee_data()
    
    def init_ui(self):
        self.setWindowTitle('Редактирование сотрудника')
        self.setFixedSize(400, 350)
        
        layout = QFormLayout()
        
        self.login_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText('Оставьте пустым, чтобы не менять пароль')
        
        self.full_name_input = QLineEdit()
        self.role_combo = QComboBox()
        self.role_combo.addItems(['admin', 'cashier', 'storekeeper'])
        
        self.warehouse_combo = QComboBox()
        self.load_warehouses_combo()
        
        self.phone_input = QLineEdit()
        self.email_input = QLineEdit()
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.save_employee)
        buttons.rejected.connect(self.reject)
        
        layout.addRow('Логин:', self.login_input)
        layout.addRow('Пароль:', self.password_input)
        layout.addRow('ФИО:', self.full_name_input)
        layout.addRow('Роль:', self.role_combo)
        layout.addRow('Склад:', self.warehouse_combo)
        layout.addRow('Телефон:', self.phone_input)
        layout.addRow('Email:', self.email_input)
        layout.addRow(buttons)
        
        self.setLayout(layout)
    
    def load_warehouses_combo(self):
        warehouses = self.db.get_all_warehouses()
        self.warehouse_combo.clear()
        for warehouse in warehouses:
            self.warehouse_combo.addItem(warehouse['name'], warehouse['id'])
    
    def load_employee_data(self):
        employee = self.db.get_employee_by_id(self.employee_id)
        if employee:
            self.login_input.setText(employee['login'])
            self.full_name_input.setText(employee['full_name'])
            self.role_combo.setCurrentText(employee['role'])
            
            # Устанавливаем склад
            index = self.warehouse_combo.findData(employee['warehouse_id'])
            if index >= 0:
                self.warehouse_combo.setCurrentIndex(index)
            
            self.phone_input.setText(employee['phone'])
            self.email_input.setText(employee['email'])
    
    def save_employee(self):
        login = self.login_input.text()
        password = self.password_input.text()
        full_name = self.full_name_input.text()
        role = self.role_combo.currentText()
        warehouse_id = self.warehouse_combo.currentData()
        phone = self.phone_input.text()
        email = self.email_input.text()
        
        if not login or not full_name:
            QMessageBox.warning(self, 'Ошибка', 'Заполните логин и ФИО')
            return
        
        if self.db.update_employee(self.employee_id, login, password, full_name, role, warehouse_id, phone, email):
            self.accept()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Ошибка при обновлении данных сотрудника')


class EditWarehouseDialog(QDialog):
    def __init__(self, db, warehouse_id, parent=None):
        super().__init__(parent)
        self.db = db
        self.warehouse_id = warehouse_id
        self.init_ui()
        self.load_warehouse_data()
    
    def init_ui(self):
        self.setWindowTitle('Редактирование склада')
        self.setFixedSize(400, 200)
        
        layout = QFormLayout()
        
        self.name_input = QLineEdit()
        self.address_input = QLineEdit()
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.save_warehouse)
        buttons.rejected.connect(self.reject)
        
        layout.addRow('Название склада:', self.name_input)
        layout.addRow('Адрес склада:', self.address_input)
        layout.addRow(buttons)
        
        self.setLayout(layout)
    
    def load_warehouse_data(self):
        warehouse = self.db.get_warehouse_by_id(self.warehouse_id)
        if warehouse:
            self.name_input.setText(warehouse['name'])
            self.address_input.setText(warehouse['address'])
    
    def save_warehouse(self):
        name = self.name_input.text()
        address = self.address_input.text()
        
        if not name or not address:
            QMessageBox.warning(self, 'Ошибка', 'Заполните название и адрес склада')
            return
        
        if self.db.update_warehouse(self.warehouse_id, name, address):
            self.accept()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Ошибка при обновлении данных склада')
