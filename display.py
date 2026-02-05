import time
import RPi.GPIO as GPIO
from lib_tft144 import TFT144
import spidev
import json

def splash_load(TFT):
    TFT.clear_display(TFT.BLACK)
    TFT.put_string("SpAmpLer",28,28,TFT.WHITE,TFT.BLACK)  # std font 3 (default)
    TFT.put_string("EgJam Ind. 2025", 24,80,TFT.WHITE, TFT.BLACK)     # doubled font 4
    time.sleep(3)
    TFT.clear_display(TFT.BLACK)
    TFT.put_string("Menu",28,28,TFT.WHITE,TFT.BLACK)  # std font 3 (default)
    
GPIO.setmode(GPIO.BCM)

#display
RST = 18
CE =   0    # 0 or 1 for CE0 / CE1 number (NOT the pin#)
DC =  22    # Labeled on board as "A0"
LED = 23    # LED backlight sinks 10-14 mA @ 3V
#these pins defult value:
#SCK = 11
#MOSI (SDA) = 10 # Don't forget the other 2 SPI pins SCK and MOSI (SDA)
TFT = TFT144(GPIO, spidev.SpiDev(), CE, DC, RST, LED, isRedBoard=False)
TFT.clear_display(TFT.BLACK)
splash_load(TFT)

while True:
    x = 4
    time.sleep(3)