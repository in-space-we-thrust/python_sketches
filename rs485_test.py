import serial
import time
import sys
import re

class PTMRSReader:
    def __init__(self, port='COM9', baudrate=9600, timeout=2):
        """
        Инициализация подключения к датчику PTM-RS
        
        Args:
            port (str): COM-порт (например, 'COM9' для Windows или '/dev/ttyUSB0' для Linux)
            baudrate (int): Скорость передачи данных (обычно 9600 для PTM-RS)
            timeout (float): Таймаут ожидания ответа в секундах
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.connection = None
        self.mac_address = None
        
    def connect(self):
        """Установка соединения с датчиком"""
        try:
            self.connection = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=self.timeout
            )
            print(f"Подключено к {self.port} со скоростью {self.baudrate} бод")
            
            # Получаем MAC адрес устройства
            self.get_mac_address()
            return True
            
        except serial.SerialException as e:
            print(f"Ошибка подключения: {e}")
            return False
    
    def disconnect(self):
        """Закрытие соединения"""
        if self.connection and self.connection.is_open:
            self.connection.close()
            print("Соединение закрыто")
    
    def send_command(self, command):
        """
        Отправка команды датчику
        
        Args:
            command (str): Команда для отправки
        """
        if not self.connection or not self.connection.is_open:
            print("Соединение не установлено")
            return None
            
        try:
            # Очищаем буфер приема перед отправкой
            self.connection.reset_input_buffer()
            
            # Отправляем команду
            self.connection.write(command.encode('ascii'))
            self.connection.flush()
            
            # Даем время на обработку
            time.sleep(0.1)
            return True
            
        except Exception as e:
            print(f"Ошибка отправки команды: {e}")
            return False
    
    def read_response(self, timeout=None):
        """
        Чтение ответа от датчика
        
        Args:
            timeout (float): Таймаут для конкретного чтения
        """
        if not self.connection or not self.connection.is_open:
            return None
            
        try:
            # Устанавливаем таймаут если передан
            if timeout:
                old_timeout = self.connection.timeout
                self.connection.timeout = timeout
            
            response = ""
            start_time = time.time()
            
            # Читаем до получения полного ответа
            while time.time() - start_time < (timeout or self.timeout):
                if self.connection.in_waiting > 0:
                    chunk = self.connection.read(self.connection.in_waiting).decode('ascii', errors='ignore')
                    response += chunk
                    
                    # Если получили символ новой строки, считаем ответ полным
                    if '\n' in response or ';' in response:
                        break
                        
                time.sleep(0.01)
            
            # Восстанавливаем исходный таймаут
            if timeout:
                self.connection.timeout = old_timeout
                
            return response.strip()
            
        except Exception as e:
            print(f"Ошибка чтения ответа: {e}")
            return None
    
    def get_mac_address(self):
        """Получение MAC адреса устройства"""
        print("Получение MAC адреса устройства...")
        if not self.send_command(":takemacadr;"):
            return None
        
        response = self.read_response()
        if response:
            # MAC адрес должен быть в формате 12 hex символов
            mac_match = re.search(r'[A-Fa-f0-9]{12}', response)
            if mac_match:
                self.mac_address = mac_match.group(0)
                print(f"MAC адрес устройства: {self.mac_address}")
                return self.mac_address
            else:
                print(f"Неожиданный формат ответа MAC: {response}")
        else:
            print("Не получен ответ на запрос MAC адреса")
        
        return None
    
    def get_pressure_and_status(self):
        """
        Получение текущего значения давления и состояния датчика
        
        Returns:
            dict: {'pressure': float, 'status': str} или None при ошибке
        """
        if not self.mac_address:
            print("MAC адрес не получен")
            return None
        
        if not self.send_command(self.mac_address):
            return None
        
        response = self.read_response()
        if response:
            try:
                # Парсим ответ - формат зависит от конкретной модели
                # Обычно в ответе содержится давление и статус
                print(f"Ответ датчика: {response}")
                
                # Попытка извлечь числовые значения из ответа
                numbers = re.findall(r'-?\d+\.?\d*', response)
                if numbers:
                    pressure = float(numbers[0]) if numbers else 0.0
                    return {
                        'pressure': pressure,
                        'status': response,
                        'raw_response': response
                    }
                else:
                    return {
                        'pressure': None,
                        'status': response,
                        'raw_response': response
                    }
                    
            except Exception as e:
                print(f"Ошибка парсинга ответа: {e}")
                return None
        else:
            print("Не получен ответ от датчика")
            return None
    
    def get_temperature(self):
        """
        Получение значения температуры
        
        Returns:
            float: Температура или None при ошибке
        """
        if not self.send_command(":0060000000;"):
            return None
        
        response = self.read_response()
        if response:
            try:
                # Извлекаем числовое значение температуры
                numbers = re.findall(r'-?\d+\.?\d*', response)
                if numbers:
                    temperature = float(numbers[0])
                    return temperature
                else:
                    print(f"Не удалось извлечь температуру из ответа: {response}")
                    return None
            except Exception as e:
                print(f"Ошибка парсинга температуры: {e}")
                return None
        else:
            print("Не получен ответ на запрос температуры")
            return None
    
    def set_zero(self):
        """Установка нуля датчика"""
        if not self.send_command(":0010000000;"):
            return False
        
        response = self.read_response()
        expected_response = "|0000000014"
        
        if response and expected_response in response:
            print("Ноль успешно установлен")
            return True
        else:
            print(f"Ошибка установки нуля. Ответ: {response}")
            return False
    
    def set_range(self, pressure_value):
        """
        Установка диапазона измерения
        
        Args:
            pressure_value (int): Значение давления для установки диапазона
        """
        command = f":002000{pressure_value:04d};"
        if not self.send_command(command):
            return False
        
        response = self.read_response()
        expected_response = "|0000000015"
        
        if response and expected_response in response:
            print(f"Диапазон успешно установлен: {pressure_value}")
            return True
        else:
            print(f"Ошибка установки диапазона. Ответ: {response}")
            return False
    
    def continuous_reading(self, interval=2):
        """
        Непрерывное чтение показаний датчика
        
        Args:
            interval (float): Интервал между чтениями в секундах
        """
        print("Начинаем непрерывное чтение данных. Нажмите Ctrl+C для остановки.")
        print("="*60)
        
        try:
            while True:
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                
                # Читаем давление и статус
                pressure_data = self.get_pressure_and_status()
                
                # Читаем температуру
                temperature = self.get_temperature()
                
                # Выводим результаты
                print(f"[{timestamp}]")
                if pressure_data:
                    if pressure_data['pressure'] is not None:
                        print(f"  Давление: {pressure_data['pressure']}")
                    print(f"  Статус: {pressure_data['status']}")
                else:
                    print("  Ошибка чтения давления")
                
                if temperature is not None:
                    print(f"  Температура: {temperature}")
                else:
                    print("  Ошибка чтения температуры")
                
                print("-" * 40)
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\nОстановка чтения данных")

def main():
    # Настройки подключения
    PORT = 'COM9'  # Измените на ваш COM-порт
    BAUDRATE = 9600
    
    # Создаем экземпляр ридера
    reader = PTMRSReader(port=PORT, baudrate=BAUDRATE)
    
    # Подключаемся к датчику
    if not reader.connect():
        print("Не удалось подключиться к датчику")
        return
    
    try:
        if not reader.mac_address:
            print("Не удалось получить MAC адрес. Проверьте подключение.")
            return
        
        print("\n" + "="*50)
        print("Тестирование команд датчика:")
        print("="*50)
        
        # Однократное чтение давления и статуса
        print("\n1. Чтение давления и статуса:")
        pressure_data = reader.get_pressure_and_status()
        if pressure_data:
            print(f"   Давление: {pressure_data.get('pressure', 'N/A')}")
            print(f"   Статус: {pressure_data.get('status', 'N/A')}")
        
        # Чтение температуры
        print("\n2. Чтение температуры:")
        temperature = reader.get_temperature()
        if temperature is not None:
            print(f"   Температура: {temperature}")
        
        print("\n" + "="*50)
        
        # Непрерывное чтение
        reader.continuous_reading(interval=3)
        
    finally:
        reader.disconnect()

if __name__ == "__main__":
    main()