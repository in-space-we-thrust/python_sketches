# sensors/temperature_sensor.py
import uasyncio as asyncio
from base_sensor import Sensor
import max31856, tpr, yf_s201

from machine import I2C, Pin
from ads1115 import ADS1115

class PressureSensor(Sensor):

    def __init__(self, name):
        super().__init__(name)
        # Инициализируем необходимые ресурсы
        self.i2c = I2C(0, sda=Pin(21), scl=Pin(22))
        self.adc = ADS1115(self.i2c, address=0x48, gain=1)

    class SENSOR_IDS:
        # Объявляем ID датчиков
        PRESSURE_PP1 = 1
        PRESSURE_PP2 = 2
        PRESSURE_PP3 = 3       

    PERIOD = 1 / 10  # Период опроса, 10 раз в секунду

    def sense(self):
        # Чтение данных с каждого датчика давления и сохранение результатов
        for channel, sensor_id in enumerate([self.SENSOR_IDS.PRESSURE_PP1, self.SENSOR_IDS.PRESSURE_PP2, self.SENSOR_IDS.PRESSURE_PP3]):
            raw = self.adc.read(7, channel)
            voltage = self.adc.raw_to_v(raw)
            self.SENSE_RESULTS[sensor_id] = (voltage/222) * 3113.99116507371 - 12.6790689979901



class FlowSensor(Sensor):

    def __init__(self, name):
        super().__init__(name)
        # Инициализируем расходомеры
        self.tpr11 = tpr.TPR(pulsPin=5, dimNumber=10, timeout=55000)
        self.yf = yf_s201.YfS201(pulsPin=4, dimNumber=10, timeout=55000)

    class SENSOR_IDS:
        # Объявляем ID датчиков
        FLOW_METR1 = 4
        FLOW_METR2 = 5       

    PERIOD = 1 / 10  # Период опроса, 10 раз в секунду

    async def sense(self):
        # Чтение данных с каждого расходомера и сохранение результатов
        flowMetr1 = await self.tpr11.frequency_measurement()
        flowMetr2 = await self.yf.flow_measurement()
         
        self.SENSE_RESULTS[self.SENSOR_IDS.FLOW_METR1] = flowMetr1
        self.SENSE_RESULTS[self.SENSOR_IDS.FLOW_METR2] = flowMetr2
        
