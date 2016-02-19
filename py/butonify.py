#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import time
import pygame as pg
from pygame import gfxdraw as pgd

VERSION = "0.1"

class buton():
	# Crea y pinta un boton
	# Parametros: texto y color

	aur = 1.618 * (16.0/9.0)
	sff = ""
	sft = ""
	font = "arialblack"
	width = 200
	height = float(width) / aur
	fsize = width/7
	border = height/10
	posx = 10
	posy = 10
	size = (width,height)
	color = (100,100,100)

	def __init__(s,sf,t,c):
		s.sf = sf
		s.texto = t
		s.color = c
		s.sff = pg.font.SysFont(s.font,s.fsize)						

	def pinta(s,sel):	# Sel: seleccionado o no
		if sel:	
			col = ( 255,255,255)
		else: 
			col = s.color
		s.sf.fill((s.color[0]/2,s.color[1]/2,s.color[2]/2),(s.posx,s.posy,s.width,s.height),0)
		s.sf.fill(col,(s.posx+s.border/2,s.posy+s.border/2,s.width-s.border,s.height-s.border),0)
		s.sft = s.sff.render(s.texto, 0, (0,0,0), col)
		s.sf.blit(s.sft,(s.posx+s.width/2-s.sft.get_size()[0]/2,s.posy+s.height/2-s.sft.get_size()[1]/2))

	def borra(s,bgcol):
		s.sf.fill(bgcol,(s.posx,s.posy,s.width,s.height),0)


class menu():
	# Pinta un menu centrado con todos los botonoes bien puestecitos
	# Los botones vienen en una lista de tuplas nombre/valor
	# params: surface, lista, color

	b = []
	but = []
	esp = 5 			# Pixels entre botones
	col = (100,100,100)

	def __init__(s,sf,b,c):
		s.sf = sf
		s.b = b
		s.col = c

		i = 0
		cx = s.sf.get_size()[0]/2  								# Calcula posición centrito X
		cy = s.sf.get_size()[1]/2 - len(s.b)*s.esp
																# Pinta ventanuco
		for bt in s.b:
			q = buton(s.sf,bt[0],s.col)							# Crea el boton con el texto y color del menu
			q.posx = cx - q.width/2
			q.posy = cy - (q.height*len(s.b))/2 + (i*q.height) + i*s.esp   
			s.but += [q]										# Guarda boton
			i += 1

	def pinta(s):
		for bt in s.but:
			bt.pinta(False)

	def selecciona(s):
		for evt in pg.event.get():
			if (evt.type == pg.MOUSEBUTTONDOWN and evt.button == 1) or (evt.type == pg.MOUSEMOTION and evt.buttons[0] == 1):
				for bt in s.but:
					if evt.pos[0] >= bt.posx and evt.pos[0] <= bt.posx+bt.width and evt.pos[1] >= bt.posy and evt.pos[1] <= bt.posy+bt.height:
						bt.pinta(True)
					else:
						bt.pinta(False)
					pg.display.flip()

			if evt.type == pg.MOUSEBUTTONUP and evt.button == 1 :
				for bt in s.but:
					if evt.pos[0] >= bt.posx and evt.pos[0] <= bt.posx+bt.width and evt.pos[1] >= bt.posy and evt.pos[1] <= bt.posy+bt.height:
						bt.pinta(False)
						pg.display.flip()

						return bt

	def borra(s,bgcolor):
		for bt in s.but: bt.borra(bgcolor)

if __name__ == "__main__":

	pg.init()
	os.environ["SDL_VIDEO_CENTERED"] = "TRUE"
	pg.display.set_mode((800,600))

	sf = pg.display.get_surface()
	sf.fill((10,10,50))

	pg.display.set_caption("BUTONIFY V"+VERSION)
	pg.display.flip()

	print("IN")

	#x = buton(sf,"BOTONN",(50,130,220))
	#x.posx = 300
	#x.posx = 200
	#x.pinta(False)

	bus = [("FM N",1),("FM W",2),("AM",3),("USB",4),("LSB",5)]
	m = menu(sf,bus,(50,130,220))
	m.pinta()
	pg.display.flip()

	print("PRESS USB TO EXIT")
	k = None
	while k == None or k.texto != "USB":
		k = m.selecciona()
		if k != None : print(k.texto)

	print(k)
	m.borra((10,10,50))
	pg.display.flip()

	#time.sleep(5)


	print("OUT")
	pg.quit()