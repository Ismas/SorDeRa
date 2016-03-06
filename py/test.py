#!/usr/bin/python

import pygame as pg
import numpy as np
import math as m
import time as t
import signal as sg

def next_sample(a,b):
	ch.queue(snd)
	ch.set_endevent(sg.SIGALRM)

print("mmixer")
pg.mixer.init(11025,-16, 1, 40960)

print("seno")
sin = []
for i in range(360*10):
	sin += [m.trunc(m.sin(i % 360)*32000)]

sn = np.array(sin)

print("sound")
snd = pg.sndarray.make_sound(sn)
snd.set_volume(1)
print("play")
#snd.play()

ch = pg.mixer.Channel(1)
ch.set_volume(0.5)
ch.play(snd)
ch.set_endevent(sg.SIGALRM)
sg.signal(sg.SIGALRM, next_sample)

pg.init()
while(True):
	for evt in pg.event.get():
		if evt.type == 14: next_sample(10,20)



pg.mixer.quit()