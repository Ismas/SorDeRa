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
	#fsize = width/7
	#border = height/10
	posx = 10
	posy = 10
	#size = (width,height)
	color = (100,100,100)
	value = None
	estado = False

	#def __init__(s):

	def init(s,sf,t,c):
		s.sf = sf
		s.texto = t
		s.color = c
		s.height = float(s.width) / s.aur
		s.size = (s.width,s.height)
		s.fsize = s.width/7
		s.border = s.height/10
		s.sff = pg.font.SysFont(s.font,s.fsize)						
	

	def pinta(s,sel):	# Sel: seleccionado o no
		if sel:	
			col = ( 255,255,255)
		else: 
			col = s.color
		s.sf.fill((s.color[0]/2,s.color[1]/2,s.color[2]/2),(s.posx,s.posy,s.width,s.height),0)		# Pinta borde
		s.sf.fill(col,(s.posx+s.border/2,s.posy+s.border/2,s.width-s.border,s.height-s.border),0)	# Pinta centro
		s.sft = s.sff.render(s.texto, 0, (0,0,0), col)												# Pinta texto
		s.sf.blit(s.sft,(s.posx+s.width/2-s.sft.get_size()[0]/2,s.posy+s.height/2-s.sft.get_size()[1]/2))	# Render texto


	def refresca(s,sel):
		s.pinta(sel)
		#if sel:	
		#	col = ( 255,255,255)
		#else: 
		#	col = s.color
		#s.sf.fill(col,(s.posx+s.border/2,s.posy+s.border/2,s.width-s.border,s.height-s.border),0)
		#s.sft = s.sff.render(s.texto, 0, (0,0,0), col)
		#s.sf.blit(s.sft,(s.posx+s.width/2-s.sft.get_size()[0]/2,s.posy+s.height/2-s.sft.get_size()[1]/2))


	def borra(s,bgcol):
		s.sf.fill(bgcol,(s.posx,s.posy,s.width,s.height),0)


class menu():
	# Pinta un menu centrado con todos los botonoes bien puestecitos
	# Los botones vienen en una lista de tuplas nombre/valor
	# params: surface, lista, color

	bts = []
	but = []
	esp = 5 			# Pixels entre botones
	col = (100,100,100)
	colhead = (200,200,100)
	sel = 0
	last = None
	width = None
	height = 10
	horborder = 5
	verborder = 5
	sff = None
	font = "droidsans"
	fsize = 16
	header = "MENU"
	cx = cy = 0
	a = b = c = d = 0


	#def __init__(s):

	def init(s,sf,bts,c,header="MENU"):
		s.sf = sf 					
		s.bts = bts
		s.col = c

		i = 0
		if not s.cx: s.cx = s.sf.get_size()[0]/2 						# Calcula posición centrito X
		if not s.cy: s.cy = s.sf.get_size()[1]/2 - len(s.bts)*s.esp		
		if s.cx < 0 : s.cx = 0
		if s.cy < 0 : s.cy = 0

		s.sff = pg.font.SysFont(s.font,s.fsize)					# Crea fuente
	
		s.but=[]
		for bt in s.bts:
			q = buton()
			if s.width: 
				q.width = s.width
			if len(bt)>2: q.estado = bt[2]
			q.value  = bt[1]
			q.init(s.sf,bt[0],s.col)							# Crea el boton con el texto y color del menu
			q.posx = s.cx - q.width/2
			q.posy = s.cy - (q.height*len(s.bts))/2 + (i*q.height) + i*s.esp  
			s.but += [q]										# Guarda boton
			s.height += q.height
			i += 1

		s.a = s.cx-s.width/2-s.horborder					# posx
		s.b = s.cy-s.height/2-s.verborder*2-s.fsize			# posy
		s.c = s.width+(s.horborder*2)						# anchura
		s.d = s.height+(s.verborder*2)+ s.fsize	+20			# altura


	def pinta(s):
		s.sf.fill( (s.col[0]/3,s.col[1]/3,s.col[2]/3), (s.a,s.b,s.c,s.d),0)				# Pinta fondo
		s.sf.fill(s.colhead,(s.a+s.horborder,s.b+s.verborder,s.width,s.fsize+4),0)		# pinta header
		sft = s.sff.render(s.header ,0 ,(0,0,0) ,s.colhead)								# Pinta texto
		s.sf.blit(sft,(s.cx-sft.get_size()[0]/2,s.b+s.verborder))						# Render texto
		for bt in s.but:
			bt.pinta(bt.estado)

	def selecciona(s):
		for evt in pg.event.get():
			if (evt.type == pg.MOUSEBUTTONDOWN and evt.button == 1) or (evt.type == pg.MOUSEMOTION and evt.buttons[0] == 1):
				for bt in s.but:
					if evt.pos[0] >= bt.posx and evt.pos[0] <= bt.posx+bt.width and evt.pos[1] >= bt.posy and evt.pos[1] <= bt.posy+bt.height:				
						if s.last:
							s.last.estado = False
							s.last.refresca(s.last.estado)
						bt.estado = True		
						bt.refresca(bt.estado)
						s.last = bt

			if evt.type == pg.MOUSEBUTTONUP and evt.button == 1 :
				for bt in s.but:
					if evt.pos[0] >= bt.posx and evt.pos[0] <= bt.posx+bt.width and evt.pos[1] >= bt.posy and evt.pos[1] <= bt.posy+bt.height and bt.estado: 
						return bt

	def refresca(s):
		s.pinta()
		#for bt in s.but: bt.pinta(bt.estado)

	def borra(s,bgcolor):
		for bt in s.but: bt.borra(bgcolor)

if __name__ == "__main__":
	exit()

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