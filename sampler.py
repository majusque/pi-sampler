import pygame as pg
import time
import RPi.GPIO as GPIO

def sync_trigger(Pin):
    """
    Function triggered by sync-in voltage
    """
    global sync_count
    sync_count += 1

#some initialisation
pg.mixer.init()

sample_1 = pg.mixer.Sound("wi-piano-1.wav")
sample_2 = pg.mixer.Sound("wi-piano-2.wav")

sequence_1  = []
sequence_1.append(sample_1)
#sequence_1.append(sample_1)
sequence_1.append(sample_2)

rate = 9 #the number of sync triggers to wait before playing the next sample in the sequence

seq_count = 0 #where we are in the sequence
sync_count = 0 #the current value of the sync trigger counter
last_sync_count = 0
#read the incoming sync trigger voltage and increment the sync counter
sync_in_pin = 2
GPIO.setmode(GPIO.BCM)
GPIO.setup(sync_in_pin, GPIO.IN)
GPIO.add_event_detect(sync_in_pin, GPIO.FALLING, callback=sync_trigger)

sync_watcher = ValueWatcher()

play = True

while True:
    
    if sync_count != last_sync_count:
        last_sync_count = sync_count
        print(sync_count, seq_count)
        if sync_count == rate - 1:
            sync_count = 0
            seq_count += 1
            play = True
        if seq_count >= len(sequence_1):
            seq_count = 0
            
        if play:
            pg.mixer.Channel(1).play(sequence_1[seq_count])
            play = False


