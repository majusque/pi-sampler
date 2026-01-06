import pygame as pg
import time
import RPi.GPIO as GPIO

def sync_trigger(Pin):
    """
    Function triggered by sync-in voltage
    """
    global sync_count
    sync_count += 1
    
def increment_seq_count(sync_count, rate, seq_count, sequence):
    """
    """
    if sync_count % rate == 0:
        #sync_count = 0
        seq_count += 1
        if seq_count >= len(sequence):
            seq_count = 0
        
            
    return seq_count

def set_play(sync_count, rate, play):
    play = False
    if sync_count % rate == 0:
        play = True
    return play    
    
            
def play_sample(play, channel, sequence, seq_count):
            
    if play:
        pg.mixer.Channel(channel).play(sequence[seq_count])
        play = False
    
#some initialisation
pg.mixer.init()

sync_count = 0 #the current value of the sync trigger counter
last_sync_count = 0
#read the incoming sync trigger voltage and increment the sync counter
sync_in_pin = 2
GPIO.setmode(GPIO.BCM)
GPIO.setup(sync_in_pin, GPIO.IN)
GPIO.add_event_detect(sync_in_pin, GPIO.FALLING, callback=sync_trigger)

#samples and sequences
sample_1 = pg.mixer.Sound("wi-piano-1.wav")
sample_2 = pg.mixer.Sound("wi-piano-2.wav")
sample_3 = pg.mixer.Sound("ac-guitar-new-1.wav")
sample_4 = pg.mixer.Sound("ac-guitar-new-2.wav")

rate_1 = 8
seq_count_1 = 0
play_1 = True
sequence_1  = []
sequence_1.append(sample_1)
sequence_1.append(sample_2)

rate_2 = 8 
seq_count_2 = 0 
play_2 = True

sequence_2  = []
sequence_2.append(sample_3)
sequence_2.append(sample_4)

while True:
    
    if sync_count != last_sync_count:
        last_sync_count = sync_count
        
        print(sync_count, seq_count_1)
        
        seq_count_1 = increment_seq_count(sync_count, rate_1, seq_count_1, sequence_1)
        play_1 = set_play(sync_count, rate_1, play_1)
        play_sample(play_1, 1, sequence_1, seq_count_1)
        
        seq_count_2 = increment_seq_count(sync_count, rate_2, seq_count_2, sequence_2)
        play_2 = set_play(sync_count, rate_2, play_2)
        play_sample(play_2, 2, sequence_2, seq_count_2)
# 
#         if sync_count % rate_1 == 0:
#             #sync_count = 0
#             seq_count_1 += 1
#             play_1 = True
#             
#             if seq_count_1 >= len(sequence_1):
#                 seq_count_1 = 0
#                 
#         if play_1:
#             pg.mixer.Channel(1).play(sequence_1[seq_count_1])
#             play_1 = False



