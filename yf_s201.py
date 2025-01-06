import uasyncio as asyncio
from machine import Pin
import time

class WaterFlowMeter:
    def __init__(self, pulsPin=4, calibration_factor=450):
        self.pulsPin = pulsPin
        self.calibration_factor = calibration_factor
        self.pulse_count = 0

        # Настроить GPIO пин
        self.p = Pin(self.pulsPin, Pin.IN, Pin.PULL_DOWN)
        self.p.irq(trigger=Pin.IRQ_RISING, handler=self.pulse_callback)
    
    def pulse_callback(self, pin):
        self.pulse_count += 1

    async def measure_flow(self):
        self.pulse_count = 0
        await asyncio.sleep(1)  # Период измерения, 1 секунда

        # Рассчитываем поток в литрах за последний интервал
        liters_per_second = self.pulse_count / self.calibration_factor

        return liters_per_second