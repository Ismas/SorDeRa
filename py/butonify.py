#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import time
import pygame as pg
import math
from pygame import gfxdraw as pgd

VERSION = "0.2"


class buton():
	# Crea y pinta un boton
	# Parametros: texto y color

	dpi = 1.5

	sff = None
	sft = None
	font = u'droidsans'
	width = 200
	posx = 10
	posy = 10
	aposy = posy
	BTNFONDO 	= (220,220,220)
	BTNFONDO2	= (200,200,200)
	BTNSEP 		= (180,180,180)
	tipo	= "Boton"
	value 	= None
	estado 	= False
	texto2 	= ""
	# Constantes MATERIAL
	margenizq 		= math.trunc(16 / dpi)
	txtizq 			= math.trunc(72 / dpi)
	margender 		= math.trunc(64 / dpi)
	tituloheight 	= math.trunc(64 / dpi)
	btnheight		= math.trunc(72 / dpi)
	fsize			= math.trunc(24 / dpi) # 12, 14, 16, 20, 24, 34, 45, etc

	#########
	# TIPOS #
	#########
		# Boton
		# Switch

	def init(s,sf,btn):
		s.sf = sf 									# Recoge surface
		s.sff = pg.font.SysFont(s.font,s.fsize)		# Crea fuente
		s.aposy = s.posy							# Almacena pos
		for b in btn.items():
			if b[0] == "text": 	s.texto = b[1]		# Extrae los campos del dict
			if b[0] == "text2": s.texto2 = b[1]
			if b[0] == "type": 	s.tipo = b[1]
			if b[0] == "posx": 	s.posx = b[1]
			if b[0] == "posy": 	s.posy = b[1]
			if b[0] == "value":	s.value = b[1]
			if b[0] == "color": s.BTNFONDO = b[1]
			if b[0] == "hight": s.estado = b[1]


	def create(self):
		return {
				"type":"Boton",
				"text":"Click",
				"text2":"No",
				"posx": 10,
				"posy": 10,
				"value":0,
				"color":(200,200,200),
				"hight":False
		}

	def pinta(s,sel):	# Sel: seleccionado o no
						# NOS PASAMOS A MATERIAL DESIGN
		if sel:	col = (255,255,255)
		else: 	col = s.BTNFONDO
		s.sf.fill(col,(s.posx,s.posy,s.width,s.btnheight),0)				# Pinta caja
		pgd.hline(s.sf,s.posx,s.posx+s.width,math.trunc(s.posy)-1,s.BTNSEP)			# Pinta separador
																				# Pinta icono
		s.sft = s.sff.render(s.texto, 1, (0,0,0), col)							# Pinta texto
		s.sf.blit(s.sft, (s.posx+s.txtizq, s.posy+s.btnheight/2-s.sft.get_size()[1]/2))	# Render texto
		if s.tipo == "Switch":
			s.sft = s.sff.render(s.texto2, 1, (0,0,0), col)											# Pinta texto2
			s.sf.blit(s.sft,(s.posx+s.width-s.txtizq, math.trunc(s.posy+s.btnheight/2-s.sft.get_size()[1]/2)))	# Render texto2
			#pgd.vline(s.sf, s.posx+s.width-s.txtizq-s.margenizq, math.trunc(s.posy)+5, math.trunc(s.posy+s.btnheight-1)-5,s.BTNSEP)				# Pinta separador


	def refresca(s,sel):
		s.pinta(sel)	# Igual en el futuro nos pasamos a surface


	def borra(s,bgcol):
		s.sf.fill(bgcol,(s.posx,s.posy,s.width,s.btnheight),0)


class menu():
	# Pinta un menu centrado con todos los botonoes bien puestecitos
	# Los botones vienen en una lista de tuplas nombre/valor
	# params: surface, lista, color

	dpi = 1.5

	bts = []
	but = []
	#col = (100,100,100)
	sel = 0
	last 	= None
	width 	= None
	height 	= 10
	sff 	= None
	font 	= u'droidsans'
	header 		= "Menu"
	colhead 	= (0x00,0x96,0x88) # Gama Teil
	menuicon 	= "gfx/menu.png"
	menuicnsf 	= None
	# Constantes MATERIAL
	margenizq 		= math.trunc(16 / dpi)
	tituloheight 	= math.trunc(64 / dpi)
	btnheight		= math.trunc(72 / dpi)
	fsize 			= math.trunc(24 / dpi)
	frame	= 0

	cx = cy = 0
	a = b = c = d = 0


	def init(s,sf,bts,c,header="Menu"):
		s.sf = sf 					
		s.bts = bts
		s.col = c
		s.header = header

		if not s.cx: s.cx = s.sf.get_size()[0]/2 						# Calcula posición centrito X
		if not s.cy: s.cy = s.sf.get_size()[1]/2 - len(s.bts)*s.height/2 #- s.tituloheight/2	
		if s.cx < 0 : s.cx = 0
		if s.cy < 0 : s.cy = 0

		s.sff = pg.font.SysFont(s.font,s.fsize)					# Crea fuente
	
		# CARGA ICONOS
		s.menuicnsf = pg.image.load(s.menuicon)						

		s.but 	=	[]
		i 	  	=	-1
		for bt in s.bts:
			i += 1
			q = buton()
			if s.width: 
				q.width = s.width
			else:
				s.width = 300
			q.init(s.sf,bt)					# Crea el boton con sus variables
			q.posx = s.cx - q.width/2 		# Coloca el boton en X					
			q.posy = s.cy - (q.btnheight*len(s.bts))/2 + (i*q.btnheight) # Coloca el boton en Y
			s.but += [q]					# Guarda boton
			s.height += q.btnheight			# Calcula altura total

		s.a = s.cx-s.width/2					# posx
		s.b = s.cy-s.height/2  -(24 * s.dpi)	# posy WHY THAT 24
		s.c = s.width							# anchura
		s.d = s.height							# altura


	def pinta(s):
		# NOS PASAMOS A MATERIAL DESIGN
		# MATERIAL		
		i = 2
		for bt in s.but:
			bt.posy = s.cy - (bt.btnheight*len(s.but))/2 - ((bt.btnheight/2)-(s.frame*i)) - s.frame*1.5
			bt.pinta(bt.estado)
			i += 1
		s.sf.fill(s.colhead,(s.a,s.b,s.c,s.tituloheight),0)											# pinta fondo header
		s.sf.blit(s.menuicnsf,(s.a+s.margenizq,s.b+s.tituloheight/2-s.menuicnsf.get_size()[1]/2))	# Pinta ICONO MENU
		sft = s.sff.render( s.header ,1 ,(255,255,255) ,s.colhead)									# Pinta TEXTO HEADER
		s.sf.blit(sft,(s.a+s.btnheight,s.b+s.tituloheight/2-sft.get_size()[1]/2))					# Render texto
		if s.frame < s.btnheight: s.frame += 3 # ANIMA


	def selecciona(s):
		for evt in pg.event.get():
			if (evt.type == pg.MOUSEBUTTONDOWN and evt.button == 1) or (evt.type == pg.MOUSEMOTION and evt.buttons[0] == 1):
				for bt in s.but:
					if evt.pos[0] >= bt.posx and evt.pos[0] <= bt.posx+bt.width and evt.pos[1] >= bt.posy and evt.pos[1] <= bt.posy+bt.btnheight:				
						if s.last:
							s.last.estado = False
							s.last.refresca(s.last.estado)
						bt.estado = True		
						bt.refresca(bt.estado)
						s.last = bt

			if evt.type == pg.MOUSEBUTTONUP and evt.button == 1 :
				for bt in s.but:
					if evt.pos[0] >= bt.posx and evt.pos[0] <= bt.posx+bt.width and evt.pos[1] >= bt.posy and evt.pos[1] <= bt.posy+bt.btnheight and bt.estado: 
						return bt

	def refresca(s):
		s.pinta()			# Igual hacemos surface en el futuro

	def borra(s,bgcolor):
		for bt in s.but: bt.borra(bgcolor)

if __name__ == "__main__":
	#exit()

	pg.init()
	os.environ["SDL_VIDEO_CENTERED"] = "TRUE"
	pg.display.set_mode((800,600))

	sf = pg.display.get_surface()
	sf.fill((10,10,50))

	pg.display.set_caption("BUTONIFY V"+VERSION)
	pg.display.flip()


	bus = [	{ "text":"FM N","value":1,"hight":False},
			{ "text":"FM W","value":2,"hight":False},
			{ "text":"AM","value":3,"hight":False},
			{ "text":"USB","value":4,"hight":True},
			{ "text":"LSB","value":5,"hight":False}
	]

	m = menu()
	m.width = 300
	m.init(sf,bus,(100,100,200))
	m.pinta()
	pg.display.flip()

	print("PRESS USB TO EXIT")
	k = None
	clk = pg.time.Clock()
	while k == None or k.texto != "USB":
		clk.tick(30)
		k = m.selecciona()
		if k != None : print(k.texto)
		m.borra((10,10,50))
		m.refresca()
		pg.display.flip()

	print(k)

	#time.sleep(5)


	print("OUT")
	pg.quit()
