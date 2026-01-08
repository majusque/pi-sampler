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
    if play_all:        
        if play:
            if sequence[seq_count] != "":
                pg.mixer.Channel(channel).set_volume(vol)
                pg.mixer.Channel(channel).play(sequence[seq_count])
            play = False
        
def button_callback(channel):
    global sync_count
    sync_count = 0
    global seq_counts
    for i in range (0,len(seq_counts)):
        seq_counts[i] = 0
    global play_all
    play_all = not play_all
    print(play_all)
    

    
#some initialisation
pg.mixer.init()
#display
serial = i2c(port=1, address=0x3C)
device = ssd1306(serial, rotate=0)

with canvas(device) as draw:
    draw.text((10, 0), "SpAmpLer", fill="white")
    draw.text((10, 30), "EgJam Ind. 2025", fill="white")
time.sleep(3)

global sequences
sequences = []

#samples and sequences
sample_1 = pg.mixer.Sound("wi-piano-1.wav")
sample_2 = pg.mixer.Sound("wi-piano-2.wav")
sample_3 = pg.mixer.Sound("ac-guitar-new-1.wav")
sample_4 = pg.mixer.Sound("ac-guitar-new-2.wav")
sample_5 = pg.mixer.Sound("drums.wav")
sample_6 = pg.mixer.Sound("bass.wav")
sample_7 = pg.mixer.Sound("hi-hats.wav")
sample_8 = pg.mixer.Sound("ooh.wav")

sequence_1  = []
sequence_1.append(sample_2)
sequence_1.append(sample_1)
sequences.append(sequence_1)

sequence_2  = []
sequence_2.append(sample_4)
sequence_2.append(sample_3)
#sequence_2.append("")
sequences.append(sequence_2)

sequence_3 = []
sequence_3.append(sample_5)
sequences.append(sequence_3)


sequence_4 = []
sequence_4.append(sample_6)
sequences.append(sequence_4)


sequence_5 = []
sequence_5.append(sample_7)
sequences.append(sequence_5)


sequence_6 = []
sequence_6.append(sample_8)
sequences.append(sequence_6)


#choose an external sync signal (true) or use the internal one (false)
sync_in = False
internal_rate = 0.124

sync_count = 0 #the current value of the sync trigger counter
last_sync_count = 0
#read the incoming sync trigger voltage and increment the sync counter
sync_in_pin = 21
GPIO.setmode(GPIO.BCM)
GPIO.setup(sync_in_pin, GPIO.IN)
if sync_in:
    GPIO.add_event_detect(sync_in_pin, GPIO.FALLING, callback=sync_trigger)

#play all button
GPIO.setup(14, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.add_event_detect(14,GPIO.RISING,callback=button_callback, bouncetime=500)

#the list of sequences (max 8)
global plays
plays = [True]*len(sequences)
global seq_counts
seq_counts = [0]*len(sequences)
global play_seqs
play_seqs = [True]*len(sequences)
vols = [0.8,0.8,1.0,1.0,0.8,1.0]
rates = [25,25,50,50,50,100] #length of each sequence to play

global play_all
play_all = False

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


