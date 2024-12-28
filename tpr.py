import time
import uasyncio as asyncio
from machine import Pin, time_pulse_us

class TPR:
    def __init__(self, pulsPin=5, dimNumber=10, timeout=55000):
        self.pulsPin = pulsPin
        self.dimNumber = dimNumber
        self.timeout = timeout
        self._setup_gpio()
        
    def _setup_gpio(self):
        self.p = Pin(self.pulsPin, Pin.IN, Pin.PULL_DOWN)

    async def _median_of_n(self):
        values = []
        for _ in range(self.dimNumber):
            pulse_high = await self._time_pulse_us_async(1)
            pulse_low = await self._time_pulse_us_async(0)
            if pulse_high < 0 or pulse_low < 0:
                continue  # пропускаем некорректные измерения
            values.append(pulse_high + pulse_low)
        if not values:
            return float('inf')  # вернуть бесконечность если все измерения некорректны
        return sum(values) / len(values)

    async def _time_pulse_us_async(self, state):
        # Асинхронный аналог функции time_pulse_us
        start = time.ticks_us()
        while True:
            if self.p.value() == state:
                break
            await asyncio.sleep_us(10)  # позволяет переключиться на другие задачли
            if time.ticks_diff(time.ticks_us(), start) > self.timeout:
                return -1
        start = time.ticks_us()
        while True:
            if self.p.value() != state:
                return time.ticks_diff(time.ticks_us(), start)
            await asyncio.sleep_us(10)
            if time.ticks_diff(time.ticks_us(), start) > self.timeout:
                return -1

    async def frequency_measurement(self):
        period = await self._median_of_n()
        if period == float('inf'):
            return 0  # вернуть 0 если частоту невозможно измерить
        return 1000000 / period
    
        