#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#	SorDeRa (c) Ismas 2016
#	A sensible SDR radio
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
import SorDeRa_sdr as logic

REAL = True

maxpts_enable 	= False
maxdecay_enable = False
azoom_enable 	= True
fftfill_enable	= False
detect_enable	= False

# Cabecera
TOPANCHO	= 1280
TOPALTO		= 50
TOP_SIZE	= (TOPANCHO,TOPALTO)

# Main Window
ANCHO		= 1280
ALTO		= 600
MAIN_SIZE	= (ANCHO,ALTO)

# FFT Window
FFTANCHO    = 1280
FFTALTO     = 500
FFT_SIZE 	= (FFTANCHO, FFTALTO)
CAPTION     = "SorDeRa SDR  fps: "
FPS 		= 30

#Colrs
BGCOLOR     = (10, 10, 50)
FGCOLOR     = (200, 200, 50)
FILLCOLOR   = (50, 50, 12)
MAXCOLOR    = (255, 150, 150)
BWCOLOR     = (200, 0, 0)
BWCOLOR2    = (50, 0, 0)
FQCCOLOR  	= (50, 150, 50)
DEVCOLOR  	= (150, 0, 150)
DEVCOLORMHZ = (220, 0, 220)
DEVCOLORHZ  = (200, 80, 80)
ESCCOLOR	= (20, 20, 100)
FONT = "Arial"
ftbw = ftdev1 = ftdev2 = ftqc = ""
fft_sf	= ""
top_sf = ""

# Network
ADDR_FFT = ('127.0.0.1',42421)
URL_RPC  = 'http://localhost:42423'
VEC_SZ   = FFTANCHO

# FFT
POSY = 300
BWY  = 100
apts = pts = [(0,0),(0,0),(0,0),(0,0)]

# BW
xbw 	= 23
bw 		= 3150
bwlabel = 0		#surface

# FQ and DEV
xdev 	= FFTANCHO/2
dev 	= 0
fq 			= 130870000		
fqc 		= 130870000		# SDR params in Khz
#fq = fqc 	= 145800000		# SDR params in Khz
SAMPLERATE 	= 192000
DECIRATE	= 9600
MINBW		= 150
fqlabel1    = fqlabel2 = ""

py 		= []	# valores puntos
pydx 	= 0		# indice matriz para media
maxpts  = []	# maximos
fft_media = 10     # cantidad de media

dtc 	 = []	# Detect
DTCTHRES = 1.15 # Threshold

# BASE & AUTOZOOM
azoom  = 3
MAXZOOM = 30
base  = 0
tope  = FFTALTO
YTOP  = 100

SALIDA = False

def FFT_frame(sock,sf):
	global py,pydx,fft_media
	global pts,maxpts
	global mindB,maxdB
	global azoom,azoom_enable,MAXZOOM,base,tope,YTOP
	global dtc,detect_enable

	pts 	= []
	y 		= []
	dtc 	= []
	tope 	= 0
	dtcm	= 0
	if (REAL):
		fft = sock.recv(4*VEC_SZ)
		#while (len(fft)<4*VEC_SZ):
		#	fft += sock.recv(4*VEC_SZ-len(fft))		# 4 = sizeof(float)
		y   = st.unpack_from('f'*VEC_SZ, fft)		# convierte stream a vector de floats
	else:
		for x in range(VEC_SZ):	y += [ random.random() ]

	for x in range(VEC_SZ):
		t = 20*m.log10(y[x])
		py[pydx][x] =  t 	# Almaceno dBs	

	t = 0.0
	t2 = FFTALTO
	for x in range(VEC_SZ):
		for x2 in range(fft_media):	t += py[x2][x]		# media de los fft_media valores
		t /= fft_media

		posy = FFTALTO-(t*azoom)-(base*azoom)

		dtcm +=  posy / VEC_SZ 							# media para el detect (grafico)

		if posy>FFTALTO : base += 1 						# AUTOBASE
		if posy<t2   : t2 = posy 						# tope superior para calcular zoom
		pts += [(x,m.trunc( posy ))]					# compone vector draw

		if m.trunc(posy) < maxpts[x] :	
			maxpts[x] = m.trunc(posy)		# Calcula max
		else :
			if maxdecay_enable: maxpts[x] += 1

	if detect_enable :	# Detect (grafico):
		# TIPO A media movil. Si tres valores mayores que la media
		#x = 0
		#while x < VEC_SZ-3:
		#	if pts[x][1] >= (dtcm / DTCTHRES) and pts[x+1][1] < (dtcm / DTCTHRES) and pts[x+2][1] >= (dtcm / DTCTHRES)	: dtc += [pts[x+1]]
		#	x += 1
		# TIPO B
		#for x in pts :
		#	if x[1] < (dtcm / DTCTHRES): dtc += [x]
		# TIPO C: Simplemente que los puntos de alrededor sean 10% más bajos
		for x in  range(VEC_SZ-4) :
			k = pts[x+1][1] 
			if (pts[x][1] >= k*1.10) and (pts[x+2][1] >= k*1.10) and (pts[x+3][1] >= k*1.15) : 
				dtc += [pts[x+1]]

	if azoom_enable :
		if t2>(YTOP*1.05) : 
			if (azoom<MAXZOOM): azoom += 0.05       # AUTOZOOM con 5% de histeresis
		if t2<(YTOP*0.95) : 
			if azoom>1: azoom -= 0.05

	pts += [(FFTANCHO+1,FFTALTO+1),(0,FFTALTO+1)]			#cierro para fill
	pydx = (pydx+1) % fft_media


def calc_dev(sf):
	global	xdev,dev
	global	fq,fqc,afq
	global  fqlabel1,fqlabel2
	global 	refrescar

	a = FFTANCHO/2											# media pantalla
	dev = (xdev-a) * (SAMPLERATE/FFTANCHO)
	fq = m.trunc(fqc + dev)
	sfq = str(fq)
	fqlabel1 = ftdev1.render(sfq[:3]+'.'+sfq[3:6], 0, DEVCOLORMHZ,BGCOLOR) # pinta dev text
	fqlabel2 = ftdev2.render(sfq[6:9], 0, DEVCOLORHZ,BGCOLOR)
	refrescar = True
	sdr.set_dev(m.trunc(-dev))	# set dev


def calc_bw(sf):
	global xbw,bw
	global bwlabel
	global DECIRATE,MINBW
	global ftbw
	global refrescar

	a = FFTANCHO/2 											# media pantalla
	bw = m.trunc((SAMPLERATE*xbw)/FFTANCHO)
	if (bw > DECIRATE/2):
		bw = DECIRATE/2
	if (bw < MINBW):
		bw = MINBW
	xbw = bw / (SAMPLERATE/FFTANCHO)
	txt = str(bw)
	bwlabel = ftbw.render(txt, 0, BWCOLOR,BWCOLOR2)
	refrescar = True
	sdr.set_bw(bw)									# set bw


def attend_mouse(sf):
	global xbw,xdev
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
				calc_bw(sf)
				continue
			if (evt.pos[1] < BWY):
				xdev = pg.mouse.get_pos()[0]
				calc_dev(sf)
				continue


def pantalla_init():
	global bw, fq
	global bwlabel, fqlabel
	global ftbw,ftdev1,ftdev2,ftqc
	global fft_sf, top_sf

	pg.init()
	os.environ["SDL_VIDEO_CENTERED"] = "TRUE"
	pg.display.set_mode(MAIN_SIZE,pg.DOUBLEBUF,8)
	sf = pg.display.get_surface()
	sf.fill(BGCOLOR)

	fft_sf= pg.Surface((FFT_SIZE),0,8)
	top_sf= pg.Surface((TOP_SIZE),0,8)

	ftdev1 = pg.font.SysFont(FONT,18)						
	ftdev2 = pg.font.SysFont(FONT,16)						
	ftbw   = pg.font.SysFont(FONT,16)						
	ftqc   = pg.font.SysFont(FONT,48)						

	calc_dev(sf)
	calc_bw(sf)

	return sf


def pantalla_refresh(sf):
	global pts,maxpts
	global xbw,xdev
	global fq,fqc,bw
	global bwlabel,fqlabel1,fqlabel2
	global ftqc
	global maxfill_enable, maxpts_enable, refrescar
	global azoom, base
	global fft_sf,top_sf

	a = FFTANCHO/2 										# media pantalla
	pleft = fqlabel1.get_size()[0]/2 + fqlabel2.get_size()[0]/2 

	if refrescar:
		fft_sf.fill(BGCOLOR) 										# Borra BW
	else:
		pgd.polygon(fft_sf,apts,BGCOLOR)							# Borra FFT

	k1=15	# Pixels por 10dB
	for x in range(12):										# Escala FFT
		y = FFTALTO - base - m.trunc( azoom*x*k1 )
		pgd.hline(fft_sf,0,FFTANCHO,y,ESCCOLOR)
		lb = ftdev1.render(str((12-x)*-10), 0, FQCCOLOR,BGCOLOR) # pinta dev text
		fft_sf.blit(lb, (0,y-10))	# Pinta fq label

	fft_sf.fill(BWCOLOR2,(xdev-xbw,BWY,xbw*2,FFTALTO-BWY),0) 			# Pinta BW
	pgd.rectangle(fft_sf,(xdev-xbw,BWY,xbw*2,FFTALTO-BWY),BWCOLOR)
	pgd.vline(fft_sf,xdev,0,FFTALTO,DEVCOLOR)							# Pinta dev
	if fftfill_enable:											# Pintta FFT relleno (Más rápido que el fill)
		for x in pts: pgd.vline(fft_sf,x[0],x[1],FFTALTO,FILLCOLOR)				

	pgd.polygon(fft_sf,pts,FGCOLOR)									# pinta FFT

	if maxpts_enable:											# Pintta puntos de max
		for x in range(VEC_SZ) : 
			pgd.pixel(fft_sf,x,maxpts[x],MAXCOLOR)				

	if detect_enable :
		for x in dtc :
			pgd.circle(fft_sf,x[0],x[1],10,MAXCOLOR)

	fft_sf.blit(bwlabel, (xdev-bwlabel.get_size()[0]/2,BWY+2))		# Pinta bw label
	if refrescar:
		fft_sf.blit(fqlabel1, (xdev-pleft,BWY-22))					# Pinta dev label 
		fft_sf.blit(fqlabel2, (xdev-pleft+fqlabel1.get_size()[0]+4,BWY-20))	

		txt = str(fqc)
		fqclabel = ftqc.render(txt[:3]+'.'+txt[3:6]+','+txt[6:], 0, FQCCOLOR,BGCOLOR)	# pinta fqc text
		pleft = fqclabel.get_size()[0]/2
		#pg.Surface.blit(sf, fqclabel, (FFTANCHO/2-pleft,2))	# Pinta fq label
		top_sf.blit(fqclabel,(TOPANCHO/2-pleft,TOPALTO/2-23))	# Pinta fq label

	pg.Surface.blit(sf,top_sf,(0,0))
	pg.Surface.blit(sf,fft_sf,(0,TOPALTO))
	pg.display.flip()
	apts = pts


if __name__ == "__main__":

	xm = 0
	soc = 0
	clk = pg.time.Clock()

	print("[+] ISMASRADIO (c) 2016")

	print("[+] Init")
	py 		= [[0 for y in range(VEC_SZ)] for x in range(fft_media)]		# soften matrix
	maxpts  = [ FFTALTO for y in range(VEC_SZ)]

	if (REAL):
		print("[+] Arrancando logica")
		sdr = logic.SorDeRa_sdr()
		sdr.set_VEC = VEC_SZ

		print("[+] Estableciendo valores")
		sdr.set_freq(fq)
		sdr.set_bw(bw)
		sdr.set_dev(-dev)
		sdr.Start(True)

		#xdev = dev-(FFTANCHO/2) / (SAMPLERATE/FFTANCHO)
		xdev = (FFTANCHO/2)

		print("[+] Abriendo socket fft")
		soc = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
		soc.bind(ADDR_FFT)

	print("[+] Generando ventana")
	sf = pantalla_init()

	print("[+] Entrando a bucle principal")
	refrescar = True
	while not SALIDA:
		clk.tick(FPS)
		pg.display.set_caption(CAPTION + str(m.trunc(clk.get_fps())))
		attend_mouse(fft_sf)
		FFT_frame(soc,fft_sf)
		pantalla_refresh(sf)

	print("[+] Saliendo")
	sdr.stop()
	pg.quit()
	sys.exit()
