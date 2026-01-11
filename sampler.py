import pygame as pg
import time
import RPi.GPIO as GPIO
import serial
import sys
import json

global mode_idx
mode_idx = 0
global samples_idx
samples_idx = 0
global sequence_idx
sequence_idx = 0
global play_mode_idx
play_mode_idx = 0


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


def set_play(sync_count, rate, play, sequence, seq_count):
    delay = sequence[seq_count]["delay"]
    play = False
    if (sync_count - delay) % rate == 0:
        play = True
    return play    
    
            
def play_sample(play, channel, sequence, seq_count, vol):
    if play_all:        
        if play:
            if sequence[seq_count]["file"] != "":
                sound = pg.mixer.Sound(sequence[seq_count]["file"])
                sound.set_volume(sequence[seq_count]["volume"])
                pg.mixer.Channel(channel).set_volume(vol)
                pg.mixer.Channel(channel).play(sound)
            play = False


def play_all_button_callback(channel):
    global sync_count
    sync_count = 0
    global seq_counts
    for i in range (0,len(seq_counts)):
        seq_counts[i] = 0
    global play_all
    play_all = not play_all
    print("play_all: " + str(play_all))
    
def mode_button_callback(channel):
    global mode_idx
    if mode_idx >= len(modes) - 1:
        mode_idx = 0
    else:
        mode_idx += 1
    print(modes[mode_idx])
    
def select_button_callback(channel):
    print("select")
    
def up_button_callback(channel):
    global samples_idx
    if mode_idx == 0:#play mode
        print("this thing +")
    elif mode_idx == 1:# edit sample mode
        if samples_idx >= len(samples) - 1:
            samples_idx = 0
        else:
            samples_idx += 1
        print(samples_idx)
    elif mode_idx == 2:# edit sequence mode
        print("the other thing +")

def down_button_callback(channel):
    global samples_idx
    if mode_idx == 0:#play mode
        print("this thing -")
    elif mode_idx == 1:# edit sample mode
        if samples_idx <= 0:
            samples_idx = 0
        else:
            samples_idx -= 1
        print(samples_idx)
    elif mode_idx == 2:# edit sequence mode
        print("the other thing -")
    
#some initialisation
pg.mixer.init()

global sequences
sequences = []
global samples
samples = []

#samples and sequences
sample_paths = []
sample_paths.append("wi-piano-1.wav")
sample_paths.append("wi-piano-2.wav")
sample_paths.append("ac-guitar-new-1.wav")
sample_paths.append("ac-guitar-new-2.wav")
sample_paths.append("drums.wav")
sample_paths.append("bass.wav")
sample_paths.append("hi-hats.wav")
sample_paths.append("ooh.wav")
sample_paths.append("wi-yeah.wav")
sample_paths.append("wi-fish.wav")
sample_paths.append("wi-2-guitar-1.wav")

for p in sample_paths:
    sample = {}
    sample["file"] = p
    sample["delay"] = 0
    sample["volume"] = 1.0
    samples.append(sample)


sequence_1 = []
sequence_1.append(samples[4])

sequences.append(sequence_1)


#choose an external sync signal (true) or use the internal one (false)
sync_in = False
internal_rate = 0.123

sync_count = 0 #the current value of the sync trigger counter
last_sync_count = 0
#read the incoming sync trigger voltage and increment the sync counter
sync_in_pin = 21
GPIO.setmode(GPIO.BCM)
GPIO.setup(sync_in_pin, GPIO.IN)
if sync_in:
    GPIO.add_event_detect(sync_in_pin, GPIO.FALLING, callback=sync_trigger)

#play all button
play_all_pin = 26
GPIO.setup(play_all_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.add_event_detect(play_all_pin,GPIO.RISING,callback=play_all_button_callback, bouncetime=500)
#select button
mode_pin = 19
GPIO.setup(mode_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.add_event_detect(mode_pin,GPIO.RISING,callback=mode_button_callback, bouncetime=500)
#up button
up_pin = 13
GPIO.setup(up_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.add_event_detect(up_pin,GPIO.RISING,callback=up_button_callback, bouncetime=500)
#down button
down_pin = 6
GPIO.setup(down_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.add_event_detect(down_pin,GPIO.RISING,callback=down_button_callback, bouncetime=500)
#select button
select_pin = 5
GPIO.setup(select_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.add_event_detect(select_pin,GPIO.RISING,callback=select_button_callback, bouncetime=500)

#the list of sequences (max 8)
global plays
plays = [True]*len(sequences)
global seq_counts
seq_counts = [0]*len(sequences)
global play_seqs
play_seqs = [True]*len(sequences)
vols = [0.8,0.8,1.0,0.0,0.8,1.0]
rates = [25,25,50,50,50,50] #length of each sequence to play

global play_all
play_all = False
play_refresh = int(1.0/0.123)

global modes
modes = ["play", "edit_sample", "edit_sequence"]

while True: # main program loop
    
    #update sync count
    if sync_count != last_sync_count:
        last_sync_count = sync_count
        
        for i in range(0,len(sequences)):
            if play_seqs[i]:
                seq_counts[i] = increment_seq_count(sync_count, rates[i], seq_counts[i], sequences[i]) #increment each sequences sample counter
                plays[i] = set_play(sync_count, rates[i], plays[i], sequences[i], seq_counts[i]) # set whether to play the sequence at this loop step or not
                play_sample(plays[i], i, sequences[i], seq_counts[i], vols[i]) # play the sample (or not) at this loop step
            

    if sync_in == False:#internal clock
        sync_count += 1
        time.sleep(internal_rate)
        



