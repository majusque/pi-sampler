import pygame as pg
import time
import RPi.GPIO as GPIO
import threading
import board
import busio
import socket
import json
from tkinter import * 
from tkinter import font, ttk

from adafruit_ads1x15 import ADS1115, AnalogIn, ads1x15

pg.mixer.init()

global sequences
sequences = []
global samples
samples = []
global current_samples
current_samples = [""]*8

def sync_trigger(Pin):
    """
    Function triggered by sync-in voltage,
    increments the sync counter
    """
    sync()
    
def sync():
    global sync_count
    global current_samples
    sync_count += 1
    #play sequences
    for i in range(0,len(sequences)):
        s = sequences[i].play(sync_count, i)
        if s != None:
            current_samples[i] = s.sample
    
class Sequence():
    
    def __init__(self):
        self._slots = []
        self._slot_idx = 0
        self._called = False
        self._last_sync_count = 1
        self._volume = 1.0
        self._slot = None
        
    def play(self, sync_count, channel):

        if play_all:
            if self._called == False:
                self._last_sync_count = sync_count
                self._called = True
                self._slot = self._slots[self._slot_idx]

            if sync_count - (self._last_sync_count + self._slot.delay) == self._slot.length or sync_count - (self._last_sync_count + self._slot.delay) == 0:
                
                if self._slot.sample != "":
                    sound = pg.mixer.Sound(self._slot.sample)
                    sound.set_volume(self._slot.volume)
                    if mutes[channel]:
                        pg.mixer.Channel(channel).set_volume(0.0)
                    else:
                        pg.mixer.Channel(channel).set_volume(self._volume)
                    pg.mixer.Channel(channel).play(sound)
                
            if sync_count - self._last_sync_count == self._slot.length - 1:
                    if self._slot_idx >= len(self._slots) - 1:
                        self._slot_idx = 0
                    else:
                        self._slot_idx += 1
                            
                    self._slot = self._slots[self._slot_idx]
                    
                    self._last_sync_count = sync_count + 1
                    
        return self._slot


        
    @property
    def slots(self):
        return self._slots  # Getter

    @slots.setter
    def slots(self, value):
        self._slots = value  # Setter
        
    def set_slot(self, index, value):
        self._slots[index] = value
        
    @property
    def slot_idx(self):
        return self._slot_idx
    
    @slot_idx.setter
    def slot_idx(self, value):
        self._slot_idx = value
        
    @property
    def called(self):
        return self._called
    
    @slot_idx.setter
    def called(self, value):
        self._called = value
        
    @property
    def volume(self):
        return self._volume
    
    @volume.setter
    def volume(self, value):
        self._volume = value
    
        
class Slot():
    
    def __init__(self, sample, length, delay, volume):
        self._sample = sample
        self._delay = delay
        self._volume = volume
        self._length = length
        
    @property
    def sample(self):
        return self._sample
    
    @sample.setter
    def sample(self, value):
        self._sample = value
        
    @property
    def delay(self):
        return self._delay
    
    @delay.setter
    def delay(self, value):
        self._delay = value
        
    @property
    def volume(self):
        return self._volume
    
    @volume.setter
    def volume(self, value):
        self._volume = value
        
    @property
    def length(self):
        return self._length
    
    @length.setter
    def length(self, value):
        self._length = value


def play_all_button_callback(channel):
    global sync_count
    sync_count = 0
    for sequence in sequences:
        sequence.slot_idx = 0
        sequence.called = False
    global play_all
    play_all = not play_all
    print("play_all: " + str(play_all))
    
#rotary encoder functions
def PIN_A_callback(channel):
    global dirstr
    dirstr += "A"
    
def PIN_B_callback(channel):
    global dirstr
    dirstr += "B"


def rotary_count(dirstr):
    if dirstr == "AB":
        return 1
    elif dirstr == "BA":
        return -1
    else:
        return 0
    
def select_button_callback(channel):
    global select
    select = True
    print("select")



def mute_button_0_callback(channel):
    mute_channel(0)
    
def mute_button_1_callback(channel):
    mute_channel(1)

def mute_button_2_callback(channel):
    mute_channel(2)
    
def mute_button_3_callback(channel):
    mute_channel(3)
    
def mute_button_4_callback(channel):
    mute_channel(4)
    
def mute_button_5_callback(channel):
    mute_channel(5)

def mute_button_6_callback(channel):
    mute_channel(6)
    
def mute_button_7_callback(channel):
    mute_channel(7)
    

def mute_channel(idx):
    global sequences
    global mutes
    mutes[idx] = not mutes[idx]
    if mutes[idx]:
        pg.mixer.Channel(idx).set_volume(0.0)
    else:
        pg.mixer.Channel(idx).set_volume(sequences[idx].volume)
        
        
def play_loop():
    count = 0
    last_count = 0
    while True: # main program loop
        global dirstr
        dirstr = ""
        global select 
        select = False
        
        if sync_in == False:#internal clock
            sync()
            time.sleep(internal_rate)
        else:
            time.sleep(0.1)

        for i in range(0,7):
            if mutes[i] == False:
                pg.mixer.Channel(i).set_volume(vols[i])
                sequences[i].volume = vols[i]

        count += rotary_count(dirstr)
        if count != last_count:
            print(count)
            last_count = count
 

def read_vols():
    global vols
    while True:
        for i in range(0,4):
            v = int(round(x[i].voltage, 1)*30.3)
            vols[i] = float(v/100)
        for j in range(0,4):
            v = int(round(y[j].voltage, 1)*30.3)
            vols[j+4] = float(v/100)
        #print(vols)
        time.sleep(0.5)
        
def display_loop():
    global TFT
    while True:
        play_display(TFT)
        time.sleep(1)
        
############################################################################################################################        
############################################################################################################################        

def gui():
    root=Tk()
    root.configure(bg='black')
    root.attributes('-fullscreen', False)
    root.bind("<F11>", lambda event: root.attributes("-fullscreen",
                                        not root.attributes("-fullscreen")))
    root.bind("<Escape>", lambda event: root.attributes("-fullscreen", False))
    fontname = "Courier"
    font_size = 16
    main_title_font_size = 18
    sub_title_font_size = 18
    pad = 6
    xpad = 5
    default_font = font.nametofont("TkDefaultFont")
    default_font.configure(family=fontname, size=font_size)
    wrap = 1500
    title  = "SpAmPLeR"

    root.title(title)

    s = StringVar()
    s.set("SpAmPLeR")
    banner_label = Label(root, textvariable = s, foreground="white", background="black", font=(fontname, sub_title_font_size, "bold"), wraplength=wrap)
    banner_label.pack(pady=pad)
    separator = ttk.Separator(root, orient='horizontal')
    separator.pack(fill='x')

    global play_string
    play_string = StringVar()

    global chnls
    chnls = []
    for i in range(0,8):
        c = StringVar()
        chnls.append(c)

    def update_variables():
        global vols
        global mutes
        global play_all
        global sequences
        global current_samples
        while True:
            
            for i in range(0,len(chnls)):
                cs = current_samples[i]
                v = str(vols[i])
                if len(v) == 3:
                    v += "0"
                if current_samples[i] == "":
                    cs = "-"
                chnls[i].set(str(i+1) + " " + v + ", " + str(int(not mutes[i])) + ", " + cs)
            
            if play_all:
                play_string.set("1")
            else:
                play_string.set("0")


            time.sleep(0.25)
            root.update()

    def show_channels():
        global chnls
        for i in range(0,8):
            c_label = Label(root, textvariable = chnls[i], justify="left", foreground="white", background="black", font=(fontname, sub_title_font_size, "bold"), wraplength=wrap)
            c_label.pack(pady=pad, padx=xpad, anchor="w")
            
    def show_playing():
        global play_string
        play_label = Label(root, textvariable = play_string, foreground="white", background="black", font=(fontname, sub_title_font_size, "bold"), wraplength=wrap)
        play_label.pack(pady=pad)
    
    top_label = Label(root, textvariable = "", foreground="white", background="black")
    top_label.pack(pady=1)
    
    show_playing()
    show_channels()
    update_variables()


    separator = ttk.Separator(root, orient='horizontal')
    separator.pack(fill='x')

    root.mainloop()
    
##############################################################################################################################################
##############################################################################################################################################           

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

slot_1_1 = Slot("drums.wav", 50, 0, 1.0)
sequence_1 = Sequence()
sequence_1.slots = [slot_1_1]
sequences.append(sequence_1)

slot_2_1 = Slot("wi-piano-1.wav", 25, 0, 1.0)
slot_2_2 = Slot("wi-piano-2.wav", 25, 0, 1.0)
sequence_2 = Sequence()
sequence_2.slots = [slot_2_1, slot_2_2]
sequences.append(sequence_2)

slot_3_1 = Slot("ooh.wav", 50, 6, 1.0)
slot_3_2 = Slot("", 50, 0, 1.0)
sequence_3 = Sequence()
sequence_3.slots = [slot_3_1, slot_3_2]
sequences.append(sequence_3)

slot_4_1 = Slot("bass.wav", 50, 0, 1.0)
sequence_4 = Sequence()
sequence_4.slots = [slot_4_1]
sequences.append(sequence_4)

slot_5_1 = Slot("hi-hats.wav", 50, 0, 0.5)
sequence_5 = Sequence()
sequence_5.slots = [slot_5_1]
sequences.append(sequence_5)

slot_6_1 = Slot("", 50, 0, 1.0)
slot_6_2 = Slot("wi-yeah.wav", 50, 34, 1.0)
sequence_6 = Sequence()
sequence_6.slots = [slot_6_1, slot_6_2]
sequences.append(sequence_6)

slot_7_1 = Slot("ac-guitar-new-1.wav", 25, 0, 1.0)
slot_7_2 = Slot("ac-guitar-new-2.wav", 25, 0, 1.0)
sequence_7 = Sequence()
sequence_7.slots = [slot_7_1, slot_7_2]
sequences.append(sequence_7)

#choose an external sync signal (true) or use the internal one (false)
sync_in = False
internal_rate = 0.123

global play_all
play_all = False

sync_count = 0 #the current value of the sync trigger counter
last_sync_count = 0
#read the incoming sync trigger voltage and increment the sync counter
sync_in_pin = 24
GPIO.setmode(GPIO.BCM)
GPIO.setup(sync_in_pin, GPIO.IN)

#play all button
play_all_pin = 26
GPIO.setup(play_all_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.add_event_detect(play_all_pin,GPIO.RISING,callback=play_all_button_callback, bouncetime=500)

if sync_in:
    GPIO.add_event_detect(sync_in_pin, GPIO.FALLING, callback=sync_trigger)

#rotary encoder inputs
PIN_A = 14 # Pin 8 
PIN_B = 15 # Pin 10
BUTTON = 4 # Pin 7


GPIO.setup(PIN_A, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.add_event_detect(PIN_A,GPIO.RISING,callback=PIN_A_callback, bouncetime=100)

GPIO.setup(PIN_B, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.add_event_detect(PIN_B,GPIO.RISING,callback=PIN_B_callback, bouncetime=100)

GPIO.setup(BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.add_event_detect(BUTTON,GPIO.RISING,callback=select_button_callback, bouncetime=500)


#button
mute_pin_0 = 17
GPIO.setup(mute_pin_0, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.add_event_detect(mute_pin_0,GPIO.RISING,callback=mute_button_0_callback, bouncetime=500)

mute_pin_1 = 16
GPIO.setup(mute_pin_1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.add_event_detect(mute_pin_1,GPIO.RISING,callback=mute_button_1_callback, bouncetime=500)

mute_pin_2 = 6
GPIO.setup(mute_pin_2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.add_event_detect(mute_pin_2,GPIO.RISING,callback=mute_button_2_callback, bouncetime=500)

mute_pin_3 = 5
GPIO.setup(mute_pin_3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.add_event_detect(mute_pin_3,GPIO.RISING,callback=mute_button_3_callback, bouncetime=500)

mute_pin_4 = 27
GPIO.setup(mute_pin_4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.add_event_detect(mute_pin_4,GPIO.RISING,callback=mute_button_4_callback, bouncetime=500)

mute_pin_5 = 25
GPIO.setup(mute_pin_5, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.add_event_detect(mute_pin_5,GPIO.RISING,callback=mute_button_5_callback, bouncetime=500)

mute_pin_6 = 12
GPIO.setup(mute_pin_6, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.add_event_detect(mute_pin_6,GPIO.RISING,callback=mute_button_6_callback, bouncetime=500)

mute_pin_7 = 13
GPIO.setup(mute_pin_7, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.add_event_detect(mute_pin_7,GPIO.RISING,callback=mute_button_7_callback, bouncetime=500)

global mutes
mutes = [False]*8

count = 0
last_count = 0
vol_count = 0

screen_refresh = 10
screen_refresh_count = 0

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

global vols
vols = [1.0]*8

vols_thread = threading.Thread(target=read_vols)
vols_thread.start()

play_thread = threading.Thread(target=play_loop)
play_thread.start()

gui_thread = threading.Thread(target=gui)
gui_thread.start()
