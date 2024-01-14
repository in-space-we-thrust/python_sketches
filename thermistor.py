# Analog temperature sensor (NTC)
#Librerias importadas para el programa
from time import sleep
from machine import ADC
from math import log

# Uso de constantes
BETA = 3950 # es el coeficiente del beta del termistor
KELVIN_CONSTANT = 273.15
NOMINAL = 25

RESISTOR = 10000
THERMISTOR = 10000

#Funciones
def adc_to_celsius(x):
    return (1 / (log(1/(65535/x - 1))/BETA + 1/298.15) - KELVIN_CONSTANT)


def steinhart_temperature_C(r, Ro=10000.0, To=25.0, beta=3950.0):
    r = 10000 / (65535/r - 1)
    import math
    steinhart = math.log(r / Ro) / beta      # log(R/Ro) / beta
    steinhart += 1.0 / (To + 273.15)         # log(R/Ro) / beta + 1/To
    steinhart = (1.0 / steinhart) - 273.15   # Invert, convert to C
    return steinhart


thermistor_pin = ADC('PA3')

#Ciclo
while True:
    thermistor_value = thermistor_pin.read_u16()
    print("Resistance(ADC)","Celsius1(°C)", "Celsius2(°C)" )
    print(thermistor_value , " ", adc_to_celsius(thermistor_value), " ", steinhart_temperature_C(thermistor_value))
    sleep(0.5)
