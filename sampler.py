import pygame as pg
import time

pg.mixer.init()

sample_1 = pg.mixer.Sound("/home/matt/samples/wimm/wi-piano-1.wav")
sample_2 = pg.mixer.Sound("/home/matt/samples/wimm/wi-piano-2.wav")

while True:
    pg.mixer.Channel(1).play(sample_1)
    time.sleep(3.122)
    pg.mixer.Channel(1).play(sample_2)
    time.sleep(3.122)

