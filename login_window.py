from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QMessageBox,
                             QTabWidget, QComboBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import json
import os

class LoginWindow(QMainWindow):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.current_user = None
        self.theme_settings_file = self.get_theme_settings_path()
        self.load_theme_settings()
        self.init_ui()
        self.apply_theme()
    
    def get_theme_settings_path(self):
        """Возвращает путь к файлу настроек темы"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(current_dir, 'theme_settings.json')
    
    def load_theme_settings(self):
        """Загружает настройки темы из файла"""
        default_settings = {
            'theme': 'light',
            'color': '#2196F3'
        }
        
        try:
            if os.path.exists(self.theme_settings_file):
                with open(self.theme_settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.current_theme = settings.get('theme', 'light')
                    self.theme_color = settings.get('color', '#2196F3')
            else:
                self.current_theme = default_settings['theme']
                self.theme_color = default_settings['color']
                self.save_theme_settings()
        except Exception as e:
            print(f"Ошибка загрузки настроек темы: {e}")
            self.current_theme = default_settings['theme']
            self.theme_color = default_settings['color']
    
    def save_theme_settings(self):
        """Сохраняет настройки темы в файл"""
        try:
            settings = {
                'theme': self.current_theme,
                'color': self.theme_color
            }
            with open(self.theme_settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Ошибка сохранения настроек темы: {e}")
    
    def init_ui(self):
        self.setWindowTitle('Авторизация - Магазин бытовой техники')
        self.setFixedSize(500, 400)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        
        # Вкладки
        self.tabs = QTabWidget()
        
        # Вкладка авторизации
        self.login_tab = QWidget()
        self.init_login_tab()
        
        # Вкладка настроек
        self.settings_tab = QWidget()
        self.init_settings_tab()
        
        self.tabs.addTab(self.login_tab, "Авторизация")
        self.tabs.addTab(self.settings_tab, "Настройки")
        
        layout.addWidget(self.tabs)
        central_widget.setLayout(layout)
    
    def init_login_tab(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title = QLabel('Магазин бытовой техники')
        title.setFont(QFont('Arial', 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('Логин')
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('Пароль')
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        login_btn = QPushButton('Войти')
        login_btn.clicked.connect(self.login)
        
        layout.addWidget(title)
        layout.addSpacing(30)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)
        layout.addWidget(login_btn)
        
        self.login_tab.setLayout(layout)
    
    def init_settings_tab(self):
        layout = QVBoxLayout()
        
        # Настройки темы
        theme_group = QWidget()
        theme_layout = QVBoxLayout()
        
        theme_title = QLabel('Настройки темы')
        theme_title.setFont(QFont('Arial', 12, QFont.Weight.Bold))
        
        # Текущие настройки
        current_settings = QLabel(f'Текущая тема: {"Светлая" if self.current_theme == "light" else "Темная"}')
        
        # Кнопка смены темы
        change_theme_btn = QPushButton('Сменить тему')
        change_theme_btn.clicked.connect(self.open_theme_dialog)
        
        theme_layout.addWidget(theme_title)
        theme_layout.addWidget(current_settings)
        theme_layout.addWidget(change_theme_btn)
        theme_group.setLayout(theme_layout)
        
        # Настройки подключения
        connection_group = QWidget()
        connection_layout = QVBoxLayout()
        
        connection_title = QLabel('Настройки подключения')
        connection_title.setFont(QFont('Arial', 12, QFont.Weight.Bold))
        
        connection_btn = QPushButton('Настройки подключения к БД')
        connection_btn.clicked.connect(self.open_connection_settings)
        
        connection_layout.addWidget(connection_title)
        connection_layout.addWidget(connection_btn)
        connection_group.setLayout(connection_layout)
        
        layout.addWidget(theme_group)
        layout.addWidget(connection_group)
        layout.addStretch()
        
        self.settings_tab.setLayout(layout)
    
    def open_theme_dialog(self):
        """Открывает диалог смены темы"""
        from theme_dialog import ThemeDialog
        dialog = ThemeDialog(self, self)
        dialog.exec()
    
    def change_theme(self, theme):
        self.current_theme = theme
        self.save_theme_settings()
        self.apply_theme()
        QMessageBox.information(self, 'Успех', f'Тема изменена на {"светлую" if theme == "light" else "темную"}')
    
    def change_theme_color(self, color_name):
        colors = {
            'Синий': '#2196F3',
            'Зеленый': '#4CAF50',
            'Красный': '#F44336',
            'Фиолетовый': '#9C27B0',
            'Оранжевый': '#FF9800',
            'Серый': '#757575'
        }
        self.theme_color = colors.get(color_name, '#2196F3')
        self.save_theme_settings()
        self.apply_theme()
    
    def apply_theme(self):
        """Применяет тему ко всему приложению"""
        if self.current_theme == 'light':
            self.apply_light_theme()
        else:
            self.apply_dark_theme()
        
        # Обновляем дочерние окна, если они открыты
        self.update_child_windows_theme()
    
    def update_child_windows_theme(self):
        """Обновляет тему всех открытых дочерних окон"""
        child_windows = [
            getattr(self, 'admin_window', None),
            getattr(self, 'cashier_window', None),
            getattr(self, 'storekeeper_window', None)
        ]
        
        for window in child_windows:
            if window and hasattr(window, 'apply_theme'):
                window.apply_theme()
    
    def apply_light_theme(self):
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
            background-color: {self.theme_color};
            color: white;
        }}
        QPushButton {{
            background-color: {self.theme_color};
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: {self.darken_color(self.theme_color)};
        }}
        QLineEdit {{
            padding: 8px;
            border: 2px solid #cccccc;
            border-radius: 4px;
            background-color: white;
            color: #333333;
        }}
        QLineEdit:focus {{
            border-color: {self.theme_color};
        }}
        QComboBox {{
            padding: 8px;
            border: 2px solid #cccccc;
            border-radius: 4px;
            background-color: white;
            color: #333333;
        }}
        QComboBox:focus {{
            border-color: {self.theme_color};
        }}
        QLabel {{
            color: #333333;
        }}
        """
        self.setStyleSheet(light_style)
    
    def apply_dark_theme(self):
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
            background-color: {self.theme_color};
            color: white;
        }}
        QPushButton {{
            background-color: {self.theme_color};
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: {self.darken_color(self.theme_color)};
        }}
        QLineEdit {{
            padding: 8px;
            border: 2px solid #555555;
            border-radius: 4px;
            background-color: #404040;
            color: #ffffff;
        }}
        QLineEdit:focus {{
            border-color: {self.theme_color};
        }}
        QComboBox {{
            padding: 8px;
            border: 2px solid #555555;
            border-radius: 4px;
            background-color: #404040;
            color: #ffffff;
        }}
        QComboBox:focus {{
            border-color: {self.theme_color};
        }}
        QLabel {{
            color: #ffffff;
        }}
        """
        self.setStyleSheet(dark_style)
    
    def darken_color(self, color):
        # Упрощенное затемнение цвета
        color_map = {
            '#2196F3': '#1976D2',  # Синий
            '#4CAF50': '#388E3C',  # Зеленый
            '#F44336': '#D32F2F',  # Красный
            '#9C27B0': '#7B1FA2',  # Фиолетовый
            '#FF9800': '#F57C00',  # Оранжевый
            '#757575': '#616161'   # Серый
        }
        return color_map.get(color, color)
    
    def open_connection_settings(self):
        from connection_window import ConnectionWindow
        # Создаем временный config если его нет
        if hasattr(self.db, 'config'):
            config = self.db.config
        else:
            from config import DatabaseConfig
            config = DatabaseConfig()
            
        self.connection_window = ConnectionWindow(config)
        self.connection_window.show()
    
    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, 'Ошибка', 'Заполните все поля')
            return
        
        user = self.db.authenticate_user(username, password)
        
        if user:
            self.current_user = user
            self.hide()
            
            # Применяем тему к открываемому окну
            if user['role'] == 'storekeeper':
                from storekeeper_window import StorekeeperWindow
                self.storekeeper_window = StorekeeperWindow(self.db, user, self)
                self.apply_theme_to_window(self.storekeeper_window)
                self.storekeeper_window.show()
            elif user['role'] == 'cashier':
                from cashier_window import CashierWindow
                self.cashier_window = CashierWindow(self.db, user, self)
                self.apply_theme_to_window(self.cashier_window)
                self.cashier_window.show()
            elif user['role'] == 'admin':
                from admin_window import AdminWindow
                self.admin_window = AdminWindow(self.db, user, self)
                self.apply_theme_to_window(self.admin_window)
                self.admin_window.show()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Неверный логин или пароль')
    
    def apply_theme_to_window(self, window):
        """Применяет текущую тему к переданному окну"""
        if hasattr(window, 'apply_theme'):
            window.apply_theme()
    
    def logout(self):
        self.current_user = None
        self.username_input.clear()
        self.password_input.clear()
        self.show()

    def get_theme_settings(self):
        return {
            'theme': self.current_theme,
            'color': self.theme_color
        }