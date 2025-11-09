from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QMessageBox, 
                             QFormLayout, QGroupBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from edb.database import Database

class ConnectionWindow(QMainWindow):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.db = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle('Подключение к базе данных')
        self.setFixedSize(400, 350)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title = QLabel('Настройка подключения к БД')
        title.setFont(QFont('Arial', 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Информация о файле конфигурации
        config_info = QLabel(f'Файл конфигурации: {self.config.get_config_file_path()}')
        config_info.setFont(QFont('Arial', 8))
        config_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Группа настроек подключения
        connection_group = QGroupBox("Параметры подключения")
        form_layout = QFormLayout()
        
        self.host_input = QLineEdit()
        self.host_input.setText(self.config.get('host', 'localhost'))
        
        self.port_input = QLineEdit()
        self.port_input.setText(str(self.config.get('port', 5432)))
        
        self.user_input = QLineEdit()
        self.user_input.setText(self.config.get('user', 'postgres'))
        
        self.password_input = QLineEdit()
        self.password_input.setText(self.config.get('password', ''))
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.database_input = QLineEdit()
        self.database_input.setText(self.config.get('database', 'appliance_store'))
        
        form_layout.addRow('Хост:', self.host_input)
        form_layout.addRow('Порт:', self.port_input)
        form_layout.addRow('Пользователь:', self.user_input)
        form_layout.addRow('Пароль:', self.password_input)
        form_layout.addRow('База данных:', self.database_input)
        
        connection_group.setLayout(form_layout)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        test_btn = QPushButton('Тест подключения')
        test_btn.clicked.connect(self.test_connection)
        
        connect_btn = QPushButton('Подключиться')
        connect_btn.clicked.connect(self.connect_to_db)
        
        buttons_layout.addWidget(test_btn)
        buttons_layout.addWidget(connect_btn)
        
        layout.addWidget(title)
        layout.addWidget(config_info)
        layout.addSpacing(10)
        layout.addWidget(connection_group)
        layout.addLayout(buttons_layout)
        
        central_widget.setLayout(layout)
    
    def test_connection(self):
        try:
            db_params = self.get_connection_params()
            # Простая проверка подключения без создания таблиц
            import psycopg2
            conn = psycopg2.connect(**db_params)
            conn.close()
            QMessageBox.information(self, 'Успех', 'Подключение к базе данных успешно!')
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось подключиться к базе данных:\n{str(e)}')
    
    def connect_to_db(self):
        try:
            db_params = self.get_connection_params()
            self.db = Database(**db_params)
            
            # Сохраняем настройки
            self.config.update_config(db_params)
            
            # Закрываем окно подключения и открываем окно авторизации
            self.close()
            from window.login_window import LoginWindow
            self.login_window = LoginWindow(self.db)
            from main import start
            if(start):
                self.login_window.show()
            
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось подключиться к базе данных:\n{str(e)}')
    
    def get_connection_params(self):
        return {
            'host': self.host_input.text(),
            'port': int(self.port_input.text()),
            'user': self.user_input.text(),
            'password': self.password_input.text(),
            'database': self.database_input.text()
        }