import pygame as pg
import time
import RPi.GPIO as GPIO


pg.mixer.init()

global sequences
sequences = []
global samples
samples = []

def sync_trigger(Pin):
    """
    Function triggered by sync-in voltage,
    increments the sync counter
    """
    global sync_count
    sync_count += 1
    
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
                
                if self._slot.sample is not "":
                    print("play", sync_count, self._last_sync_count, self._slot.length, self._slot.delay, self._slot_idx, self._slot.sample)
                    
                    sound = pg.mixer.Sound(self._slot.sample)
                    sound.set_volume(self._slot.volume)
                    pg.mixer.Channel(channel).set_volume(self._volume)
                    pg.mixer.Channel(channel).play(sound)
                
            if sync_count - self._last_sync_count == self._slot.length - 1:
                    if self._slot_idx >= len(self._slots) - 1:
                        self._slot_idx = 0
                    else:
                        self._slot_idx += 1
                            
                    self._slot = self._slots[self._slot_idx]
                    
                    self._last_sync_count = sync_count + 1


        
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
sync_in_pin = 21
GPIO.setmode(GPIO.BCM)
GPIO.setup(sync_in_pin, GPIO.IN)

#play all button
play_all_pin = 26
GPIO.setup(play_all_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.add_event_detect(play_all_pin,GPIO.RISING,callback=play_all_button_callback, bouncetime=500)

if sync_in:
    GPIO.add_event_detect(sync_in_pin, GPIO.FALLING, callback=sync_trigger)
    


    
    
while True: # main program loop
    
    #update sync count
    if sync_count != last_sync_count:
        last_sync_count = sync_count
        
        for i in range(0,len(sequences)):
            sequences[i].play(sync_count, i)
            
    if sync_in == False:#internal clock
        sync_count += 1
        time.sleep(internal_rate)