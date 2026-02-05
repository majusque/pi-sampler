import board
import busio
import time
import json
import socket

from adafruit_ads1x15 import ADS1115, AnalogIn, ads1x15

# Create the I2C bus
i2c2 = busio.I2C(3,2)
i2c = busio.I2C(1,0)

# Create the ADC object using the I2C bus
ads = ADS1115(i2c2)
ads2 = ADS1115(i2c)

x = []
x.append(AnalogIn(ads, ads1x15.Pin.A0))
x.append(AnalogIn(ads, ads1x15.Pin.A1))
x.append(AnalogIn(ads, ads1x15.Pin.A2))
x.append(AnalogIn(ads, ads1x15.Pin.A3))

y = []
y.append(AnalogIn(ads2, ads1x15.Pin.A0))
y.append(AnalogIn(ads2, ads1x15.Pin.A1))
y.append(AnalogIn(ads2, ads1x15.Pin.A2))
y.append(AnalogIn(ads2, ads1x15.Pin.A3))

vols = [1.0]*8



while True:
    for i in range(0,4):
        v = int(round(x[i].voltage, 1)*30.3)
        vols[i] = float(v/100)
    for j in range(0,4):
        v = int(round(y[j].voltage, 1)*30.3)
        vols[j+4] = float(v/100)
    print(vols)
    file = open("vols.json", "w")
    file.write(json.dumps(vols))
    file.close()
    time.sleep(0.5)