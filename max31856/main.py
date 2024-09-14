import max31856
csPin = 5
misoPin = 19
mosiPin = 23
clkPin = 18
max = max31856.max31856(csPin,misoPin,mosiPin,clkPin)
thermoTempC = max.readThermocoupleTemp()
print ("Thermocouple Temp: %f degC" % thermoTempC)
juncTempC = max.readJunctionTemp()
print ("Cold Junction Temp: %f degC" % juncTempC)
