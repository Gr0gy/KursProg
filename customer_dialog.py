from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QDialogButtonBox, 
                             QFormLayout, QMessageBox)
from PyQt6.QtCore import Qt

class CustomerDialog(QDialog):
    def __init__(self, db, customer_id=None, parent=None):
        super().__init__(parent)
        self.db = db
        self.customer_id = customer_id
        self.init_ui()
        if customer_id:
            self.load_customer_data()
    
    def init_ui(self):
        self.setWindowTitle('Редактирование клиента' if self.customer_id else 'Создание клиента')
        self.setFixedSize(400, 300)
        
        layout = QFormLayout()
        
        self.full_name_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.email_input = QLineEdit()
        self.address_input = QLineEdit()
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.save_customer)
        buttons.rejected.connect(self.reject)
        
        layout.addRow('ФИО:', self.full_name_input)
        layout.addRow('Телефон:', self.phone_input)
        layout.addRow('Email:', self.email_input)
        layout.addRow('Адрес:', self.address_input)
        layout.addRow(buttons)
        
        self.setLayout(layout)
    
    def load_customer_data(self):
        customer = self.db.get_customer_by_id(self.customer_id)
        if customer:
            self.full_name_input.setText(customer['full_name'])
            self.phone_input.setText(customer['phone'])
            self.email_input.setText(customer['email'])
            self.address_input.setText(customer['address'])
    
    def save_customer(self):
        full_name = self.full_name_input.text()
        phone = self.phone_input.text()
        email = self.email_input.text()
        address = self.address_input.text()
        
        if not full_name or not phone:
            QMessageBox.warning(self, 'Ошибка', 'Заполните ФИО и телефон')
            return
        
        if self.customer_id:
            # Редактирование существующего клиента
            if self.db.update_customer(self.customer_id, full_name, phone, email, address):
                self.accept()
            else:
                QMessageBox.warning(self, 'Ошибка', 'Ошибка при обновлении данных клиента')
        else:
            # Создание нового клиента
            if self.db.create_customer(full_name, phone, email, address):
                self.accept()
            else:
                QMessageBox.warning(self, 'Ошибка', 'Ошибка при создании клиента')
# [file content end]