from machine import Pin, time_pulse_us
import utime
p_echo = Pin(36, Pin.IN)
while True:
    print(time_pulse_us(p_echo,0))
    utime.sleep_ms(1)
