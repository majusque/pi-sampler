import pygame as pg
import time
import RPi.GPIO as GPIO
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306, ssd1325, ssd1331, sh1106

def sync_trigger(Pin):
    """
    Function triggered by sync-in voltage
    """
    global sync_count
    sync_count += 1
    
def increment_seq_count(sync_count, rate, seq_count, sequence):
    """
    Increment the sequence position counter based on the rate.
    When the number of sunc signals equals a multiple of the rate,
    increment the sequence position index
    """
    if sync_count % rate == 0:
        seq_count += 1
        if seq_count >= len(sequence):
            seq_count = 0
        
            
    return seq_count

def set_play(sync_count, rate, play):
    play = False
    if sync_count % rate == 0:
        play = True
    return play    
    
            
def play_sample(play, channel, sequence, seq_count, vol):
            
    if play:
        if sequence[seq_count] != "":
            pg.mixer.Channel(channel).set_volume(vol)
            pg.mixer.Channel(channel).play(sequence[seq_count])
        play = False
    
#some initialisation
pg.mixer.init()
#display
serial = i2c(port=1, address=0x3C)
device = ssd1306(serial, rotate=0)

with canvas(device) as draw:
    draw.text((10, 0), "SpAmpLer", fill="white")
    draw.text((10, 30), "EgJam Ind. 2025", fill="white")
time.sleep(3)


#samples and sequences
sample_1 = pg.mixer.Sound("wi-piano-1.wav")
sample_2 = pg.mixer.Sound("wi-piano-2.wav")
sample_3 = pg.mixer.Sound("ac-guitar-new-1.wav")
sample_4 = pg.mixer.Sound("ac-guitar-new-2.wav")

sequence_1  = []
sequence_1.append(sample_1)
sequence_1.append(sample_2)

sequence_2  = []
sequence_2.append(sample_3)
#sequence_2.append(sample_4)
sequence_2.append("")


#choose an external sync signal (true) or use the internal one (false)
sync_in = False
internal_rate = 0.125

sync_count = 0 #the current value of the sync trigger counter
last_sync_count = 0
#read the incoming sync trigger voltage and increment the sync counter
sync_in_pin = 21
GPIO.setmode(GPIO.BCM)
GPIO.setup(sync_in_pin, GPIO.IN)
if sync_in:
    GPIO.add_event_detect(sync_in_pin, GPIO.FALLING, callback=sync_trigger)


sequences = [sequence_1,sequence_2] #the list of sequences (max 8)
rates = [25,25] #length of each sequence to play
plays = [True,True] #triggers for whether to play the sequence on the nexst step or not
seq_counts = [0,0] #a counter to keep track of which sample to play in each sequence
play_seqs = [True,True] #whether to play the sequence or not
vols = [1.0,0.8]

while True: # main program loop
    
    #update sync count
    if sync_count != last_sync_count:
        last_sync_count = sync_count
        
        for i in range(0,len(sequences)):
            if play_seqs[i]:
                seq_counts[i] = increment_seq_count(sync_count, rates[i], seq_counts[i], sequences[i]) #increment each sequences sample counter
                plays[i] = set_play(sync_count, rates[i], plays[i]) # set whether to play the sequence at this loop step or not
                play_sample(plays[i], i, sequences[i], seq_counts[i], vols[i]) # play the sample (or not) at this loop step
                

    if sync_in == False:#internal clock
        sync_count += 1
        time.sleep(internal_rate)


