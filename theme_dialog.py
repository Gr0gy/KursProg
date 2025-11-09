from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QComboBox, QDialogButtonBox,
                             QColorDialog, QHBoxLayout, QLineEdit, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
import json
import os

class ThemeDialog(QDialog):
    def __init__(self, login_window, parent=None):
        super().__init__(parent)
        self.login_window = login_window
        self.init_ui()
        self.load_current_settings()
    
    def init_ui(self):
        self.setWindowTitle('Смена темы')
        self.setFixedSize(350, 280)
        
        layout = QVBoxLayout()
        
        # Выбор темы
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel('Тема:'))
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(['Светлая', 'Темная'])
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()
        
        # Выбор цвета
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel('Цвет:'))
        
        self.color_combo = QComboBox()
        self.color_combo.addItems(['Синий', 'Зеленый', 'Красный', 'Фиолетовый', 'Оранжевый', 'Серый', 'Пользовательский'])
        self.color_combo.currentTextChanged.connect(self.on_color_changed)
        color_layout.addWidget(self.color_combo)
        color_layout.addStretch()
        
        # Поле для пользовательского цвета
        custom_color_layout = QHBoxLayout()
        custom_color_layout.addWidget(QLabel('Пользовательский цвет:'))
        
        self.custom_color_input = QLineEdit()
        self.custom_color_input.setPlaceholderText('#RRGGBB')
        self.custom_color_input.setMaximumWidth(80)
        
        self.color_picker_btn = QPushButton('Выбрать')
        self.color_picker_btn.clicked.connect(self.pick_custom_color)
        self.color_picker_btn.setVisible(False)
        
        custom_color_layout.addWidget(self.custom_color_input)
        custom_color_layout.addWidget(self.color_picker_btn)
        custom_color_layout.addStretch()
        
        # Кнопки
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.apply_theme)
        buttons.rejected.connect(self.reject)
        
        layout.addLayout(theme_layout)
        layout.addLayout(color_layout)
        layout.addLayout(custom_color_layout)
        layout.addSpacing(20)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def on_color_changed(self, color_name):
        """Обработчик изменения выбора цвета"""
        is_custom = color_name == 'Пользовательский'
        self.custom_color_input.setVisible(is_custom)
        self.color_picker_btn.setVisible(is_custom)
    
    def pick_custom_color(self):
        """Открывает диалог выбора цвета"""
        color = QColorDialog.getColor()
        if color.isValid():
            hex_color = color.name()
            self.custom_color_input.setText(hex_color)
    
    def load_current_settings(self):
        """Загружает текущие настройки темы"""
        theme_settings = self.login_window.get_theme_settings()
        
        # Устанавливаем тему
        if theme_settings['theme'] == 'light':
            self.theme_combo.setCurrentText('Светлая')
        else:
            self.theme_combo.setCurrentText('Темная')
        
        # Устанавливаем цвет
        color_map = {
            '#2196F3': 'Синий',
            '#4CAF50': 'Зеленый', 
            '#F44336': 'Красный',
            '#9C27B0': 'Фиолетовый',
            '#FF9800': 'Оранжевый',
            '#757575': 'Серый'
        }
        
        current_color = theme_settings['color']
        if current_color in color_map:
            self.color_combo.setCurrentText(color_map[current_color])
        else:
            self.color_combo.setCurrentText('Пользовательский')
            self.custom_color_input.setText(current_color)
            self.custom_color_input.setVisible(True)
            self.color_picker_btn.setVisible(True)
    
    def apply_theme(self):
        """Применяет выбранную тему и сохраняет настройки"""
        theme = 'light' if self.theme_combo.currentText() == 'Светлая' else 'dark'
        
        colors = {
            'Синий': '#2196F3',
            'Зеленый': '#4CAF50',
            'Красный': '#F44336', 
            'Фиолетовый': '#9C27B0',
            'Оранжевый': '#FF9800',
            'Серый': '#757575'
        }
        
        selected_color = self.color_combo.currentText()
        if selected_color == 'Пользовательский':
            custom_color = self.custom_color_input.text().strip()
            if not custom_color or not self.is_valid_hex_color(custom_color):
                QMessageBox.warning(self, 'Ошибка', 'Введите корректный HEX-цвет (#RRGGBB)')
                return
            color = custom_color
        else:
            color = colors.get(selected_color, '#2196F3')
        
        # Обновляем настройки в login_window
        self.login_window.current_theme = theme
        self.login_window.theme_color = color
        
        # Сохраняем настройки
        self.login_window.save_theme_settings()
        
        # Применяем тему ко всем окнам
        self.login_window.apply_theme()
        
        # Обновляем тему родительского окна, если оно существует
        if self.parent():
            self.parent().apply_theme()
        
        self.accept()
    
    def is_valid_hex_color(self, color):
        """Проверяет валидность HEX-цвета"""
        import re
        pattern = r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$'
        return bool(re.match(pattern, color))
