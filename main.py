import sys
import os
import psycopg2
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt

# Добавляем путь к текущей директории для импортов
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from edb.config import DatabaseConfig
from window.connection_window import ConnectionWindow
from edb.database import Database

start = 0

def get_config_path():
    """Возвращает путь к файлу конфигурации в папке приложения"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, 'database_config.json')

def test_database_connection(config):
    """Проверка подключения к базе данных"""
    try:
        db_params = config.get_connection_params()
        # Проверяем базовое подключение к PostgreSQL
        test_conn = psycopg2.connect(
            host=db_params['host'],
            port=db_params['port'],
            user=db_params['user'],
            password=db_params['password'],
            database='postgres'  # Пробуем подключиться к стандартной базе
        )
        test_conn.close()
        return True
    except psycopg2.OperationalError as e:
        # Если база данных не существует, создаем ее
        if "database" in str(e) and "does not exist" in str(e):
            try:
                # Подключаемся к postgres базе для создания новой БД
                conn = psycopg2.connect(
                    host=db_params['host'],
                    port=db_params['port'],
                    user=db_params['user'],
                    password=db_params['password'],
                    database='postgres'
                )
                conn.autocommit = True
                cursor = conn.cursor()
                
                # Создаем базу данных если она не существует
                cursor.execute(f"CREATE DATABASE {db_params['database']}")
                print(f"База данных {db_params['database']} создана")
                
                cursor.close()
                conn.close()
                return True
            except Exception as create_error:
                print(f"Ошибка при создании базы данных: {create_error}")
                return False
        else:
            print(f"Ошибка подключения: {e}")
            return False
    except Exception as e:
        print(f"Общая ошибка подключения: {e}")
        return False

def main():
    # Создаем приложение
    app = QApplication(sys.argv)
    
    # Устанавливаем стиль
    app.setStyle('Fusion')
    
    # Загружаем конфигурацию (файл будет создан в папке приложения)
    config_path = get_config_path()
    config = DatabaseConfig(config_path)
    
    try:
        # Проверяем подключение к базе данных
        db_params = config.get_connection_params()
        
        # Если есть все необходимые параметры, пробуем подключиться
        if all([db_params['host'], db_params['user'], db_params['database']]):
            if test_database_connection(config):
                # Подключаемся к нашей базе данных
                db = Database(**db_params)
                start = 1
                # Показываем окно авторизации
                from window.login_window import LoginWindow
                login_window = LoginWindow(db)
                login_window.show()
                
                # Запускаем приложение
                sys.exit(app.exec())
            else:
                # Если подключение не удалось, показываем окно настройки подключения
                raise ConnectionError("Не удалось подключиться к базе данных")
        else:
            # Если параметры не заполнены, показываем окно подключения
            raise ConnectionError("Параметры подключения не заполнены")
            
    except (ConnectionError, psycopg2.Error, Exception) as e:
        print(f"Ошибка: {e}")
        
        # Показываем окно подключения к БД
        connection_window = ConnectionWindow(config)
        connection_window.show()
        
        # Запускаем приложение
        sys.exit(app.exec())

if __name__ == '__main__':
    main()