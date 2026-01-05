import pygame as pg
import time
import RPi.GPIO as GPIO

def sync_trigger(Pin):
    """
    Function triggered by sync in voltage
    """
    global sync_count
    sync_count += 1
    print(sync_count)

pg.mixer.init()

sample_1 = pg.mixer.Sound("wi-piano-1.wav")
sample_2 = pg.mixer.Sound("wi-piano-2.wav")

sequence_1  = []
sequence_1.append(sample_1)
sequence_1.append(sample_1)
sequence_1.append(sample_2)

rate = 3
t = 0
count = 0

sync_count = 0

sync_in_pin = 2
GPIO.setmode(GPIO.BCM)
GPIO.setup(sync_in_pin, GPIO.IN)
GPIO.add_event_detect(sync_in_pin, GPIO.FALLING, callback=sync_trigger)

while True:
    
    if t == 0:
        pg.mixer.Channel(1).play(sequence_1[count])
        count += 1
    time.sleep(1)
    t += 1
    if t == rate:
        t = 0
    if count >= len(sequence_1):
        count = 0

