import pygame as pg
import time

pg.mixer.init()

sample_1 = pg.mixer.Sound("/home/matt/samples/wimm/wi-piano-1.wav")
sample_2 = pg.mixer.Sound("/home/matt/samples/wimm/wi-piano-2.wav")

sequence  = []
sequence.append(sample_1)
sequence.append(sample_2)

t = 3.122

while True:
    for sample in sequence:
        pg.mixer.Channel(1).play(sample)
        time.sleep(t)

