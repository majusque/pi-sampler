import pygame as pg
import time

pg.mixer.init()

sample_1 = pg.mixer.Sound("/home/matt/samples/wimm/wi-piano-1.wav")
sample_2 = pg.mixer.Sound("/home/matt/samples/wimm/wi-piano-2.wav")

sequence_1  = []
sequence_1.append(sample_1)
sequence_1.append(sample_1)
sequence_1.append(sample_2)

rate = 3
t = 0
count = 0

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

