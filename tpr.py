import time
from machine import Pin, time_pulse_us

class TPR:
    def __init__(self, pulsPin=5, dimNumber=10, timeout=55000):
        self.pulsPin = pulsPin
        self.dimNumber = dimNumber
        self.timeout = timeout
        self._setup_gpio()
        
    def _setup_gpio(self):
        self.p = Pin(self.pulsPin, Pin.IN, Pin.PULL_DOWN)

    def _median_of_n(self):
        values = []
        for _ in range(self.dimNumber):
            pulse_high = time_pulse_us(self.p, 1, self.timeout)
            pulse_low = time_pulse_us(self.p, 0, self.timeout)
            if pulse_high < 0 or pulse_low < 0:
                continue  # пропускаем некорректные измерения
            values.append(pulse_high + pulse_low)
        if not values:
            return float('inf')  # вернуть бесконечность если все измерения некорректны
        return sum(values) / len(values)
    
    def frequency_measurement(self):
        period = self._median_of_n()
        if period == float('inf'):
            return 0  # вернуть 0 если частоту невозможно измерить
        return 1000000 / period
        