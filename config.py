import json
import os

class DatabaseConfig:
    def __init__(self, config_file='database_config.json'):
        # Если передан относительный путь, создаем файл в папке приложения
        if not os.path.isabs(config_file):
            current_dir = os.path.dirname(os.path.abspath(__file__))
            config_file = os.path.join(current_dir, config_file)
        
        self.config_file = config_file
        self.config = self._load_config()
    
    def _load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    # Удаляем лишние параметры, которые могут быть в файле
                    valid_keys = ['host', 'port', 'user', 'password', 'database']
                    cleaned_config = {k: config_data.get(k) for k in valid_keys}
                    return cleaned_config
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                print(f"Ошибка чтения конфигурации: {e}")
                # Пробуем прочитать с другой кодировкой
                try:
                    with open(self.config_file, 'r', encoding='cp1251') as f:
                        config_data = json.load(f)
                        valid_keys = ['host', 'port', 'user', 'password', 'database']
                        cleaned_config = {k: config_data.get(k) for k in valid_keys}
                        return cleaned_config
                except:
                    # Если файл поврежден, создаем новый
                    print("Создаем новый файл конфигурации")
                    return self._create_default_config()
            except Exception as e:
                print(f"Неизвестная ошибка: {e}")
                return self._create_default_config()
        else:
            # Создаем файл с конфигурацией по умолчанию
            return self._create_default_config()
    
    def _create_default_config(self):
        """Создает конфигурацию по умолчанию и сохраняет в файл"""
        default_config = {
            "host": "localhost",
            "port": 5432,
            "user": "postgres",
            "password": "",
            "database": "appliance_store"
        }
        self._save_config(default_config)
        print(f"Создан файл конфигурации: {self.config_file}")
        return default_config
    
    def _save_config(self, config):
        """Сохраняет конфигурацию в файл"""
        try:
            # Создаем папку если она не существует
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Ошибка сохранения конфигурации: {e}")
    
    def update_config(self, new_config):
        """Обновляет конфигурацию и сохраняет в файл"""
        # Очищаем новые настройки от лишних параметров
        valid_keys = ['host', 'port', 'user', 'password', 'database']
        cleaned_config = {k: new_config.get(k) for k in valid_keys}
        
        self.config.update(cleaned_config)
        self._save_config(self.config)
    
    def get_connection_params(self):
        """Возвращает параметры подключения (очищенные от лишних параметров)"""
        valid_keys = ['host', 'port', 'user', 'password', 'database']
        return {k: self.config.get(k) for k in valid_keys}
    
    def get_config_file_path(self):
        """Возвращает путь к файлу конфигурации"""
        return self.config_file
    
    def get(self, key, default=None):
        """Метод get для доступа к конфигурации"""
        return self.config.get(key, default)