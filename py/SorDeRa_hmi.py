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
import struct as st
import math as m
import random
import SorDeRa_sdr as logic
import butonify

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
FQCCOLOR  	= (150, 150, 250)
BGFQCCOLOR 	= (60, 60, 60)
DEVCOLOR  	= (150, 0, 150)
DEVCOLORMHZ = (220, 0, 220)
DEVCOLORHZ  = (200, 80, 80)
ESCCOLOR	= (20, 20, 100)
SQCOLOR		= (80, 0, 0)
MODECOLOR	= (200, 200, 50)
FONT = "arial"
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
pts = [(0,0),(0,0),(0,0),(0,0)]
#apts = pts

# BW
xbw 	= 23
bw 		= 3150
bwlabel = 0		#surface

# FQ and DEV
xdev 	= FFTANCHO/2
dev 	= 0
sq 		= -70
xsq		= FFTALTO/2 
fq 			= 130870000		
fqc 		= 130870000		# SDR params in Khz
#fq = fqc 	= 145800000		# SDR params in Khz
SAMPLERATE 	= 192000
DECIRATE	= 9600
MINBW		= 150
MAXF 		= 1999999999
MINF		= 150000
fqlabel1    = fqlabel2 = ""

# Mode
mode = 1
tmode = "AM"
modex = 0
modelabel = ""

# FFT
numx	= []
py 		= []	# valores puntos
pydx 	= 0		# indice matriz para media
maxpts  = []	# maximos
fft_media = 10     # cantidad de media

dtc 	 = []	# Detect
DTCTHRES = 1.15 # Threshold

# BASE & AUTOZOOM
FFTK   = 8*(FFTALTO/120) 
azoom  = 1
MAXZOOM = 10
base  = 0
tope  = FFTALTO
YTOP  = 100

mn = None
retf = None
SALIDA = False

ma = -100
mi = 100

def FFT_frame(sock,sf):
	global py,pydx,fft_media
	global pts,maxpts
	global mindB,maxdB
	global azoom,azoom_enable,MAXZOOM,base,tope,YTOP
	global dtc,detect_enable
	global refrescar
	#global ma, mi
	global sdr

	pts 	= []
	y 		= []
	dtc 	= []
	tope 	= 0
	dtcm	= 0
	if (REAL):
		y = sdr.fft_probe.level()
	else:
		for x in range(VEC_SZ):	y += [ random.random() ]


	for x in range(VEC_SZ):
		#t = 20*m.log10(y[x])
		t = m.log10(y[x])
		py[pydx][x] =  t 	# Almaceno dBs	

		# RANGO [-10,5] -> +10 -> [0,15]
		# 120/15 = 8 -> dBs
		# FFTALTO/120 = 
		#if t > ma: ma = t
		#if t < mi: mi = t

	t = 0.0
	t2 = FFTALTO
	t3 = 0
	for x in range(VEC_SZ):
		for x2 in range(fft_media):	t += py[x2][x]		# media de los fft_media valores
		t /= fft_media

		#posy = FFTALTO-(t*azoom)-(base*azoom)			# Altura en el FFT
		posy = FFTALTO-(t*FFTK*azoom)-(6*FFTK*azoom)+base # Altura en el FFT
		dtcm +=  posy / VEC_SZ 							# media para el detect (grafico)

		if posy>FFTALTO : 
			base += 1 									# AUTOBASE cuando se sale por debajo
		#if posy > t3 : t3 = posy						# AUTOBASE cuando no llega abajo

		if posy < t2  : t2 = posy 						# tope superior para calcular zoom
		pts += [(x,m.trunc( posy ))]					# compone vector draw

		if m.trunc(posy) < maxpts[x] :	
			maxpts[x] = m.trunc(posy)					# Calcula max
		else :
			if maxdecay_enable: maxpts[x] += 1

	#base = t3
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
			if (azoom<MAXZOOM): 
				azoom += 0.01       # AUTOZOOM con 5% de histeresis
				calc_sq(xsq+TOPALTO)
		if t2<(YTOP*0.95) : 
			if azoom>1: 
				azoom -= 0.01
				calc_sq(xsq+TOPALTO)


	pts += [(FFTANCHO+1,FFTALTO+1),(0,FFTALTO+1)]			#cierro para fill
	pydx = (pydx+1) % fft_media
	#print(azoom)

def calc_dev():
	global	xdev,dev
	global	fq,fqc,afq
	global  fqlabel1,fqlabel2
	global 	refrescar

	a = FFTANCHO/2											# media pantalla
	dev = (xdev-a) * (SAMPLERATE/FFTANCHO)
	fq = m.trunc(fqc + dev)
	sfq = format(fq,'010d')
	sfq = sfq[:-9]+'.'+sfq[-9:-6]+'.'+sfq[-6:-3]+','+sfq[-3:]
	sfq = sfq.lstrip('0.')
	fqlabel1 = ftdev1.render(sfq[:len(sfq)-4], 0, DEVCOLORMHZ,BGCOLOR) # pinta dev text
	fqlabel2 = ftdev2.render(sfq[len(sfq)-3:], 0, DEVCOLORHZ,BGCOLOR)
	sdr.set_dev(m.trunc(-dev))	# set dev


def calc_bw():
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
	sdr.set_bw(bw)									# set bw


def calc_freq(posx,posy):
	global fqc
	global numx
	global sdr
	global refrescar
	global mediac

	sp 	 = 4
	size = 24
	inc  = 1
	if posy > TOPALTO/2: inc = -1 	# Calcula incremento o decremento

	i = 9;
	for x in numx:
		if (posx >= x) and (posx <= x+size) : fqc += inc * (10**i) # Click sobre los numeros			
		i -= 1

	if fqc > MAXF : fqc = MAXF 	# Limites
	if fqc < MINF : fqc = MINF
	sdr.set_freq(fqc)

	calc_dev()			# Esto afecta al indicador de desviacion
	mediac = 0 			# reinicia suavizado

	refrescar = True


def calc_sq(posy):
	global xsq,sq
	global sdr

	xsq = posy - TOPALTO
	#sq =  m.trunc( (-120*xsq/FFTALTO) )
	sq =  m.trunc( ((-120/azoom)*(float(xsq)/FFTALTO)) - (120.0-120.0/azoom)*(1.0-(xsq/FFTALTO)  ) )
	if sq < -120 : sq = 120
	if sq > 0 	 : sq = 0
	sdr.set_sq(sq)


def calc_demod_ask():
	global mn,opt

	opt = None
	bus = [("AUTO",10),("FM N",0),("AM",1),("FM W",2),("USB",4),("LSB",5)]
	mn = ""
	k = butonify
	k.width = 100
	mn = k.menu(sf,bus,(50,130,220))


def calc_demod_set():
	global mn,opt
	global modelabel
	global sdr

	print("SET MODE ",opt.texto,opt.value)
	modelabel = ftbw.render(opt.texto, 0, MODECOLOR,BGCOLOR)
	sdr.set_amfm(opt.value)
	mn = None
	opt = None


def attend_mouse(sf):
	global xbw,xdev
	global retf
	global SALIDA

	for evt in pg.event.get():
		if (evt.type == pg.QUIT):
			print("[+] Evento de salida")
			SALIDA = True
			continue
		if ( ((evt.type == pg.MOUSEBUTTONDOWN or evt.type == pg.MOUSEBUTTONUP) and  evt.button == 1) or 
			(evt.type == pg.MOUSEMOTION and evt.buttons[0] == 1) ) :
			if m.fabs(evt.pos[0]-xdev) < 20 and m.fabs(evt.pos[1]-BWY-40) < 20 :		# Demodulator mode
				calc_demod_ask()
				retf = calc_demod_set
				continue
			if m.fabs(evt.pos[0] - FFTANCHO) < 50  and m.fabs(evt.pos[1]-xsq-TOPALTO) < 50 :	# Si xestá en los ´ultimos 20 pixels y a la altura del
				calc_sq(evt.pos[1])																# squelch
				continue
			if evt.pos[1] > TOPALTO+BWY :	# ancho de banda
				xbw = m.fabs(evt.pos[0]-xdev)									# distancia al dev
				calc_bw()
				continue
			if (evt.pos[1] > TOPALTO):											# desviacion
				xdev = evt.pos[0]
				calc_dev()
				continue
			# Va a ser freq
			if evt.type == pg.MOUSEBUTTONDOWN and evt.button == 1:				# Digitos de frecuencia
				calc_freq(evt.pos[0],evt.pos[1])
				continue


def pantalla_init():
	global bw, fq
	global bwlabel, fqlabel
	global ftbw,ftdev1,ftdev2,ftqc
	global fft_sf, top_sf

	pg.init()
	os.environ["SDL_VIDEO_CENTERED"] = "TRUE"
	pg.display.set_mode(MAIN_SIZE)
	#print(pg.display.Info())
	sf = pg.display.get_surface()
	sf.fill(BGCOLOR)

	# Surfaces TOP & FFT (subsurfaces del main)
	top_sf= sf.subsurface((0,0,TOPANCHO,TOPALTO))		
	fft_sf= sf.subsurface((0,TOPALTO,FFTANCHO,FFTALTO))

	#print(pg.font.get_fonts())

	ftdev1 = pg.font.SysFont(FONT,18)						
	ftdev2 = pg.font.SysFont(FONT,16)						
	ftbw   = pg.font.SysFont(FONT,16)						
	ftqc   = pg.font.SysFont('ubuntumono',48)						

	return sf


def pantalla_refresh(sf):
	global pts,maxpts
	global xbw,xdev
	global fq,fqc,bw
	global modelabel,bwlabel,fqlabel1,fqlabel2
	global ftqc, numx
	global maxfill_enable, maxpts_enable, refrescar
	global azoom, base
	global fft_sf,top_sf
	global sq,xsq

	a = FFTANCHO/2 										# media pantalla
	pleft = fqlabel1.get_size()[0]/2 + fqlabel2.get_size()[0]/2 

	fft_sf.fill(BGCOLOR) 									# Borra BW Más rapido que reescribir.

	for x in range(12):										# Escala FFT
	#	y = FFTALTO - base - m.trunc( azoom*x*k1 )
		y = m.trunc(FFTALTO - (x*(FFTALTO/12))*azoom) + base
		if (y>0):
			pgd.hline(fft_sf,0,FFTANCHO,y,ESCCOLOR)
			lb = ftdev1.render(str((12-x)*-10), 0, FQCCOLOR,BGCOLOR) # pinta dev text
			fft_sf.blit(lb, (0,y-10))	# Pinta fq label

	fft_sf.fill(BWCOLOR2,(xdev-xbw,BWY,xbw*2,FFTALTO-BWY),0) 		# Pinta BW
	pgd.rectangle(fft_sf,(xdev-xbw,BWY,xbw*2,FFTALTO-BWY),BWCOLOR)
	pgd.vline(fft_sf,xdev,0,FFTALTO,DEVCOLOR)						# Pinta dev

	if fftfill_enable:												# Pintta FFT relleno (Más rápido que el fill)
		for x in pts: pgd.vline(fft_sf,x[0],x[1],FFTALTO,FILLCOLOR)				
	pgd.polygon(fft_sf,pts,FGCOLOR)									# pinta FFT
	if maxpts_enable:												# Pintta puntos de max
		for x in range(VEC_SZ) : pgd.pixel(fft_sf,x,maxpts[x],MAXCOLOR)				
	if detect_enable :												# Pinta detector picos
		for x in dtc :	pgd.circle(fft_sf,x[0],x[1],10,MAXCOLOR)

	fft_sf.blit(bwlabel,  (xdev-bwlabel.get_size()[0]/2,BWY+2))		# Pinta bw label
	fft_sf.blit(modelabel,(xdev-modelabel.get_size()[0]/2,BWY-40))	# Pinta mode label
	fft_sf.blit(fqlabel1, (xdev-pleft,BWY-22))						# Pinta dev label 
	fft_sf.blit(fqlabel2, (xdev-pleft+fqlabel1.get_size()[0]+4,BWY-20))	

	# pinta Sqelch
	pgd.hline(fft_sf,0,FFTANCHO,xsq,SQCOLOR)
	fsq = ftdev2.render('SQ '+str(sq), 0, DEVCOLORHZ,BGCOLOR)
	fft_sf.blit(fsq, (FFTANCHO-fsq.get_size()[0],xsq-12))		# Pinta bw label

	if refrescar:	
		sp 	 = 4
		size = 24
		numx = []	# Repinta el indicador de frecuencia
		txt = format(fqc,'010d')
		txt = txt[:-9]+'.'+txt[-9:-6]+'.'+txt[-6:-3]+','+txt[-3:]
		lon = len(txt)
		anc = 0
		for x in range(lon):
			if txt[x] in ['.',','] : 
				col = BGCOLOR
				anc = size / 2
			else :	
				col = BGFQCCOLOR
				anc = size
			px = (TOPANCHO/2) - (lon+sp)*size/2 + (x*(size+sp)) 	# Calcula posición
			fqclabel = ftqc.render(txt[x], 0, FQCCOLOR, col)		# pinta fqc text
			top_sf.blit(fqclabel,(px,0))							# blit
			if txt[x] not in ['.',','] : numx += [px]				# Almacena la coordenada del numero

	# PINTA MENU IF ANY
	if mn :
		mn.refresca()

	# Flipea/Vuelca la pantalla
	pg.display.flip()							
	refrescar = False



if __name__ == "__main__":

	xm = 0
	soc = 0
	clk = pg.time.Clock()

	print("[+] ISMASRADIO (c) 2016")

	print("[+] Init")
	py 		= [[0 for y in range(VEC_SZ)] for x in range(fft_media)]		# soften matrix
	maxpts  = [ FFTALTO for y in range(VEC_SZ)]

	if (REAL):

		print("[+] Estableciendo valores logica")
		sdr = logic.SorDeRa_sdr()
		sdr.set_VEC(VEC_SZ)
		sdr.set_freq(fq)
		sdr.set_bw(bw)
		sdr.set_dev(-dev)
		sdr.set_sq(sq)

		print("[+] Arrancando logica")
		sdr.start()

		#xdev = dev-(FFTANCHO/2) / (SAMPLERATE/FFTANCHO)
		xdev = (FFTANCHO/2)

	print("[+] Generando ventana")
	sf = pantalla_init()

	calc_dev()
	calc_bw()
	calc_freq(0,0)
	calc_sq(FFTALTO/2)
	opt = butonify.buton(sf,"AM",(0,0,0))
	opt.value = 1
	calc_demod_set()

	print("[+] Entrando a bucle principal")
	refrescar = True
	while not SALIDA:
		clk.tick(FPS)
		pg.display.set_caption(CAPTION + str(m.trunc(clk.get_fps())))
		FFT_frame(soc,fft_sf)
		pantalla_refresh(sf)
		if mn :							# Si existe un menu, gestiona menus
			opt = mn.selecciona()		# Lee botonera
			if opt: retf()				# Si se ha devuelto valor, salimos a la función de retorno
		else:
			attend_mouse(fft_sf)		# Si no hay menu, botones estandard.

	print("[+] Saliendo")
	sdr.stop()
	pg.quit()
	sys.exit()
