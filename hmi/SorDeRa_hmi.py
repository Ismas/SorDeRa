#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#	REALRADIO (c) Ismas 2016
#
import os
import sys
import pygame as pg
from pygame import gfxdraw as pgd
import socket as sk
import struct as st
import math as m
import xmlrpclib as xml
import random
#from realradio import params as V

REAL = True

# Window
ANCHO       = 1280
ALTO        = 600
SCREEN_SIZE = (ANCHO, ALTO)
CAPTION     = "PyFFT "

#Colrs
BGCOLOR     = (10, 10, 50)
FGCOLOR     = (200, 200, 50)
MAXCOLOR    = (50, 50, 12)
BWCOLOR     = (200, 0, 0)
BWCOLOR2    = (50, 0, 0)
FQCCOLOR  	= (50, 150, 50)
DEVCOLOR  	= (150, 0, 150)
DEVCOLORMHZ = (220, 0, 220)
DEVCOLORHZ  = (200, 80, 80)
ESCCOLOR	= (20, 20, 100)
FONT = "Arial"
FFT_RELLENO	= False
ftbw = ftdev1 = ftdev2 = ftqc = ""

# Network
ADDR_FFT = ('127.0.0.1',42421)
URL_RPC  = 'http://localhost:42423'
VEC_SZ   = 1280

# FFT
POSY = 300
BWY  = 100
apts = pts = [(0,0),(0,0),(0,0),(0,0)]

# BW
xbw 	= 23
bw 		= 3150
bwlabel = 0		#surface

# FQ and DEV
xdev 	= ANCHO/2
dev 	= 0
fq 			= 130870000		
fqc 		= 130870000		# SDR params in Khz
#fq = fqc 	= 145800000		# SDR params in Khz
SAMPLERATE 	= 192000
DECIRATE	= 9600
MINBW		= 150
fqlabel1    = fqlabel2 = ""

py 		= []	# valores puntos
MAX     = []
pydx 	= 0		# indice matriz para media
fft_media = 10     # cantidad de media

AZOOM  = 10
MAXAZOOM = 30
menor = 0
mayor = 0
mindB = 1000.0
maxdB = -1000.0

#pulsado = False
SALIDA = False

def FFT_frame(sock,sf):
	global py,pydx,fft_media
	y = []
	global pts,apts
	global MAX
	global mindB,maxdB
	global AZOOM,MAXAZOOM
	#global VEC_SZ

	pts = []
	tope = 0
	if (REAL):
		fft = sock.recv(4*VEC_SZ)
		#while (len(fft)<4*VEC_SZ):
		#	fft += sock.recv(4*VEC_SZ-len(fft))		# 4 = sizeof(float)
		y   = st.unpack_from('f'*VEC_SZ, fft)		# convierte stream a vector de floats
	else:
		for x in range(VEC_SZ):	y += [ random.random() ]

	for x in range(VEC_SZ):
		#py[pydx][x] =  m.trunc( -20*m.log( y[x] ) ) 	# Almaceno dBs	
		#if (y[x]<mindB): mindB = m.sqrt(y[x])							# calcula el suelo
		#if (y[x]>maxdB): maxdB = m.sqrt(y[x])							# calcula el techo

		py[pydx][x] =  m.log(4294967296L/y[x]) 	# Almaceno dBs	

	t = 0.0
	for x in range(VEC_SZ):
		for x2 in range(fft_media):	t += py[x2][x]		# media de los fft_media valores
		t /= fft_media

		if (t<mindB): mindB = t							# calcula el suelo
		if (t>maxdB): maxdB = t							# calcula el techo

		#AZOOM = 100.0 / (100.0 - t)
		AZOOM = 1

		pts += [(x,m.trunc( ALTO/2+(t*AZOOM) ))]						# compone vector draw

		#if (pts[x][1] < MAX[x][1]):
		#	MAX[x] = [(x,pts[x][1])]		# compone vector max

	pts += [(ANCHO+1,ALTO+1),(0,ALTO+1)]			#cierro para fill
	pydx = (pydx+1) % fft_media
	print(mindB,maxdB)


def calc_dev(xm,sf):
	global	xdev,dev
	global	fq,fqc,afq
	global  fqlabel1,fqlabel2
	global 	refrescar

	a = ANCHO/2											# media pantalla
	dev = (xdev-a) * (SAMPLERATE/ANCHO)
	fq = m.trunc(fqc + dev)
	sfq = str(fq)
	fqlabel1 = ftdev1.render(sfq[:3]+'.'+sfq[3:6], 0, DEVCOLORMHZ,BGCOLOR) # pinta dev text
	fqlabel2 = ftdev2.render(sfq[6:9], 0, DEVCOLORHZ,BGCOLOR)
	refrescar = True
	xm.set_dev(m.trunc(-dev))	# set dev


def calc_bw(xm,sf):
	global xbw,bw
	global bwlabel
	global DECIRATE,MINBW
	global ftbw
	global refrescar

	a = ANCHO/2 											# media pantalla
	bw = m.trunc((SAMPLERATE*xbw)/ANCHO)
	if (bw > DECIRATE/2):
		bw = DECIRATE/2
	if (bw < MINBW):
		bw = MINBW
	xbw = bw / (SAMPLERATE/ANCHO)
	txt = str(bw)
	bwlabel = ftbw.render(txt, 0, BWCOLOR,BWCOLOR2)
	refrescar = True
	xm.set_bw(bw)									# set bw


def attend_mouse(xm,sf):
	global xbw,xdev
	global pulsado
	global SALIDA

	for evt in pg.event.get():
		if (evt.type == pg.QUIT):
			print("[+] Evento de salida")
			SALIDA = True
			continue
		if ( ((evt.type == pg.MOUSEBUTTONDOWN or evt.type == pg.MOUSEBUTTONUP) and  evt.button == 1) or 
			(evt.type == pg.MOUSEMOTION and evt.buttons[0] == 1) ) :
			if (evt.pos[1] > BWY):
				xbw = m.fabs(pg.mouse.get_pos()[0]-xdev)			# distancia al dev
				calc_bw(xm,sf)
				continue
			if (evt.pos[1] < BWY):
				xdev = pg.mouse.get_pos()[0]
				calc_dev(xm,sf)
				continue


def pantalla_init(xm):
	global bw, fq
	global bwlabel, fqlabel
	global ftbw,ftdev1,ftdev2,ftqc

	pg.init()
	os.environ["SDL_VIDEO_CENTERED"] = "TRUE"
	pg.display.set_mode(SCREEN_SIZE)
	sf = pg.display.get_surface()
	sf.fill(BGCOLOR)

	ftdev1 = pg.font.SysFont(FONT,18)						
	ftdev2 = pg.font.SysFont(FONT,16)						
	ftbw   = pg.font.SysFont(FONT,16)						
	ftqc   = pg.font.SysFont(FONT,24)						

	calc_dev(xm,sf)
	calc_bw(xm,sf)

	return sf


def pantalla_refresh(sf):
	global pts,apts
	global xbw,xdev
	global fq,fqc,bw
	global bwlabel,fqlabel1,fqlabel2
	global ftqc
	global FFT_RELLENO, refrescar
	global AZOOM, menor

	a = ANCHO/2 										# media pantalla
	pleft = fqlabel1.get_size()[0]/2 + fqlabel2.get_size()[0]/2 

	if refrescar:
		sf.fill(BGCOLOR) 										# Borra BW
	else:
		pgd.polygon(sf,apts,BGCOLOR)							# Borra FFT

	#k1=8
	#for x in range(12):										# Escala FFT
	#	y = m.trunc( float(AZOOM*x)*k1 + menor )
	#	pgd.hline(sf,0,ANCHO,y,ESCCOLOR)
	#	lb = ftdev1.render(str(x*10), 0, FQCCOLOR,BGCOLOR) # pinta dev text
	#	pg.Surface.blit(sf, lb, (0,y-10))	# Pinta fq label

	sf.fill(BWCOLOR2,(xdev-xbw,BWY,xbw*2,ALTO-BWY),0) 			# Pinta BW
	pgd.rectangle(sf,(xdev-xbw,BWY,xbw*2,ALTO-BWY),BWCOLOR)
	pgd.vline(sf,xdev,0,ALTO,DEVCOLOR)							# Pinta dev
	if FFT_RELLENO:												# Pintta FFT relleno (Más rápido que el fill)
		for x in pts: pgd.vline(sf,x[0],x[1],ALTO,MAXCOLOR)				
	pgd.polygon(sf,pts,FGCOLOR)									# pinta FFT
	#pg.draw.lines(sf,MAXCOLOR,False,MAX,1)					# pinta MAX
	pg.Surface.blit(sf, bwlabel, (xdev-bwlabel.get_size()[0]/2,BWY+2))		# Pinta bw label
	if refrescar:
		pg.Surface.blit(sf, fqlabel1, (xdev-pleft,BWY-22))					# Pinta dev label 
		pg.Surface.blit(sf, fqlabel2, (xdev-pleft+fqlabel1.get_size()[0]+4,BWY-20))	
		txt = str(fqc)
		fqclabel = ftqc.render(txt[:3]+'.'+txt[3:6]+','+txt[6:], 0, FQCCOLOR,BGCOLOR)	# pinta fqc text
		pleft = fqclabel.get_size()[0]/2
		pg.Surface.blit(sf, fqclabel, (ANCHO/2-pleft,2))	# Pinta fq label


	pg.display.flip()
	apts = pts

def old_pantalla_refresh(sf):
	global pts,apts
	global xbw,xdev
	global fq,fqc,bw
	global bwlabel,fqlabel1,fqlabel2
	global ftqc
	a = ANCHO/2 										# media pantalla
	pg.draw.lines(sf,BGCOLOR,False,apts,1)					# borra FFT
	pg.draw.rect(sf,BWCOLOR2,(xdev-xbw,BWY,xbw*2,ALTO-BWY))	# pinta BW
	pg.draw.rect(sf,BWCOLOR,(xdev-xbw,BWY,xbw*2,ALTO-BWY),2)
	pg.draw.line(sf,DEVCOLOR,[xdev,0],[xdev,ALTO],1)		# pinta dev
	#pts += [(ANCHO,ALTO),(0,ALTO),(0,600)]
	#pg.draw.polygon(sf,MAXCOLOR,pts,0)					# pinta FFT relleno
	pg.draw.lines(sf,FGCOLOR,False,pts,1)					# pinta FFT
	#pg.draw.lines(sf,MAXCOLOR,False,MAX,1)					# pinta MAX
	pg.Surface.blit(sf, bwlabel, (xdev-bwlabel.get_size()[0]/2,BWY+2))	# Pinta bw label
	pleft = fqlabel1.get_size()[0]/2 + fqlabel2.get_size()[0]/2 		# Pinta dev label
	pg.Surface.blit(sf, fqlabel1, (xdev-pleft,BWY-22))					# 
	pg.Surface.blit(sf, fqlabel2, (xdev-pleft+fqlabel1.get_size()[0]+4,BWY-20))	
	txt = str(fqc)
	fqclabel = ftqc.render(txt[:3]+'.'+txt[3:6]+','+txt[6:], 0, FQCCOLOR,BGCOLOR)	# pinta fqc text
	pleft = fqclabel.get_size()[0]/2
	pg.Surface.blit(sf, fqclabel, (ANCHO/2-pleft,2))	# Pinta fq label
	pg.display.flip()
	apts = pts


if __name__ == "__main__":

	xm = 0
	soc = 0
	clk = pg.time.Clock()

	print("[+] ISMASRADIO (c) 2016")

	print("[+] Init")
	py = [[0 for y in range(VEC_SZ)] for x in range(fft_media)]		# soften matrix
	for x in range(VEC_SZ):
		MAX += [(x,ALTO)]

	if (REAL):
		print("[+] Conectando a xmlrpc")
		xm = xml.Server(URL_RPC)

		print("[+] Estableciendo valores")
		xm.set_freq(fq)
		xm.set_bw(bw)
		xm.set_dev(-dev)
		#xdev = dev-(ANCHO/2) / (SAMPLERATE/ANCHO)
		#print(xm.get_bw(),xbw)
		#print(dev,xdev)

		print("[+] Abriendo socket fft")
		soc = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
		soc.bind(ADDR_FFT)

	print("[+] Generando ventana")
	sf = pantalla_init(xm)

	print("[+] Entrando a bucle principal")
	refrescar = True
	while not SALIDA:
		clk.tick(30)
		pg.display.set_caption(CAPTION + str(m.trunc(clk.get_fps())))
		attend_mouse(xm,sf)
		FFT_frame(soc,sf)
		pantalla_refresh(sf)

	print("[+] Saliendo")
	pg.quit()
	sys.exit()
