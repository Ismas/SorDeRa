#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#	SorDeRa (c) Ismas 2016
#	A sensible SDR radio
#
import os
import sys
import subprocess
import pygame as pg
from pygame import gfxdraw as pgd
import struct as st
import math as m
import random
import pickle
import datetime
import numpy as np
import butonify

REAL = True

if REAL: import SorDeRa_sdr as logic

# AUTOMATISMOS FFT
linecancel_enable	= True
maxpts_enable 	= False
maxdecay_enable = False
azoom_enable 	= True
fftfill_enable	= False
detect_enable	= False
stronger_enable	= False


# Automatismos waterfall
autorange_enable = True
dostronger		= False

# Main Window
ANCHO		= 1280
ALTO		= 850
MAIN_SIZE	= (ANCHO,ALTO)
CAPTION     = "SorDeRa SDR  fps: "
FPS 		= 30

# Cabecera
TOPANCHO	= 1280
TOPALTO		= 50
TOP_SIZE	= (TOPANCHO,TOPALTO)

# FFT (upper) Window
FFTANCHO    = 1280
FFTALTO     = 500
FFT_SIZE 	= (FFTANCHO, FFTALTO)

# Waterfall (down) Windows
DWNANCHO	= 1280
DWNALTO		= 300
DWN_SIZE	= (DWNANCHO,DWNALTO)

#Colrs
BGCOLOR     = (10, 10, 50)
FGCOLOR     = (200, 200, 50)
FILLCOLOR   = (50, 50, 12)
MAXCOLOR    = (100, 50, 0)
DETECTCOLOR = (150, 250, 0)
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
top_sf 	= ""
frame 	= 0
tframe 	= 0
count 	= 0

# GFX
MENUIMG 	= "gfx/menu.png"
STEREOIMG 	= "gfx/stereo.png"

# Network
ADDR_FFT = ('127.0.0.1',42421)
URL_RPC  = 'http://localhost:42423'
VEC_SZ   = FFTANCHO

# FFT
POSY = 300
BWY  = 100
pts = [(0,0),(0,0),(0,0),(0,0)]
#apts = pts

# FQ and DEV
xdev 	= float(FFTANCHO/2 - (20000/FFTANCHO))
dev 	= -20000
fqc 		= 126220000		# SDR params in Khz
#fq = fqc 	= 145800000		# SDR params in Khz
audrate 	= 11025
SAMPLERATE 	= 192000
decimation  = SAMPLERATE/audrate
decirate	= SAMPLERATE/decimation
MINBW		= 150
MAXF 		= 1999999999
MINF		= 150000
fqlabel1    = fqlabel2 = ""

# BW
xbw 	= 23
bw 		= 3150
maxbw	= audrate/2
minipaso = 0.5/(float(SAMPLERATE/FFTANCHO)/25.0)
xmaxbw	= 60			# <- TODO calcular esto
bwlabel = 0		#surface

#SQ
sq 		= -70
xsq		= FFTALTO/2 
asq		= 0.0
possq	= (0,0)

# Mode
mode = 0
tmode = "AM"
modex = 0
modelabel = ""

# FFT
py 		= []	# valores puntos en pantalla este fane
pm		= []	# Media de puntos
numx	= []
maxpts  = []	# maximos
mpts 	= []	# maximos en pantalla
pydx 	= 0		# indice matriz para media
fft_media = 10     # cantidad de media

# Waterfall
contraste	= -100
wfrango		= 100
wfframe		= 0

# DETECT
dtc 	 = []	# Detect
DTCTHRES = 1.15 # Threshold

#smeter	
smval 		= 0.0
smvaladj 	= 10.0
smbot		= 6.0
sml 		= 200
smx			= 0

# BASE & AUTOZOOM
FFTK   = 9*(FFTALTO/120) 
azoom  = 1
MAXZOOM = 3
base  = 0
tope  = FFTALTO
YTOP  = 100

# LINECANCEL
testi =	True
testj = False
lci = 0.0
lcj = 0.0
lcs = -1
alc = 0.0

# rec
rec 	= False

mn 		= None
retf 	= None
SALIDA 	= False

ma = -100
mi = 100

stereosf = None
menusf = None

ch = None

def FFT_get():
	global py,pydx,pm
	global linecancel_enable,lci,lcj,testi,testj,lcs,alc
	global dostronger,tframe, xdev
	# RANGO [-10,5] -> +10 -> [0,15]
	# 120/15 = 8 -> dBs
	# FFTALTO/120 = 
	#if t > ma: ma = t
	#if t < mi: mi = t

		#print(m.fabs(tcancel+alc),testi,testj)
		#if testi:		
		#	if tcancel > alc : 
		#		lcs = -lcs		# vamos mal, invierto signo
		#		lci += 0.0001 * lcs 
		#	else:				# si no vamos mal
		#		if m.fabs(tcancel+alc) > 0.1:		# si 
		#		print("en testi")
		#		if tcancel > alc:  
		#			print("sumo")
		#			lci += 0.0001					# suma
		#		else:								# si no
		#			print("resto")
		#			lci -= 0.0001	# si es mayor que antes, resta
		#			alc = tcancel 					# lo guardamos como bueno
		#		sdr.set_lai(lci)
		#	else:
		#		testi = False 						# Si el pico no es chungo paso a siguiente fase
		#		testj = True
		#if testj:		
		#	if m.fabs(tcancel+alc) > 0.1:
		#		if tcancel > alc:  lcj -= 0.0001
		#		else:		
		#			lcj += 0.0001
		#			alc = tcancel
		#		sdr.set_laj(lcj)
		#	else:
		#		testi = False 	# Fin comprobacion
		#		testj = False

	#print(lcj)

	# LINECANCEL
	if REAL:
		if linecancel_enable:
			sdr.set_lai(-0.0032)
			sdr.set_laj(-0.0034)
		else:
			sdr.set_lai(0)
			sdr.set_laj(0)


	# ADQUISICION DE DATOS
	if (REAL):
		i = 0
		for x in sdr.fft_probe.level():
			py[pydx][i] = m.log10(x)
			t = 0											# Leo DBs y logaritmo y añado
			for x2 in range(fft_media):	t += py[x2][i]		# media de los fft_media valores
			pm[i] = (t / fft_media) 						# Media
			i += 1
	else:	
		for x in range(VEC_SZ):	py[pydx][x] = random.random() 
			
	if dostronger and tframe > fft_media:	# Sintoniza al punto más alto cuando el FFT se ha estabilizado
		tmax = -3.0 # Un nivel minimo para sintonizar, debería ser -infinito
		txd  = 0
		for i in range(VEC_SZ):
			if py[pydx][i] > tmax: 
				tmax = py[pydx][i]
				txd = i 
		if txd:
		 	xdev = txd
		 	dostronger = False
		 	calc_dev()

	pydx = (pydx+1) % fft_media					# Siguiente para media

def FFT_frame(sf):
	global py,pydx,pm,fft_media
	global pts,maxpts,mpts
	global mindB,maxdB
	global azoom,azoom_enable,MAXZOOM,base,tope,YTOP
	global dtc,detect_enable
	global refreshfq
	global tframe
	global smval,xdev
	global base,mi
	global sdr


	# BUCLE PRINCIPAL CALCULOS
	t 		= 0.0
	t2 		= FFTALTO
	t3 		= 0
	mi 		= 0
	pts 	= []
	mpts 	= []
	smval 	= 0
	dtc 	= []
	tope 	= 0
	dtcm	= 0
	smval 	= -10.0

	for x in range(VEC_SZ):
		t = pm[x]

		# Captura media de linecancel
		if linecancel_enable and x == VEC_SZ/2: tcancel = t

		# SMETER
		# Media de lo que hay dentro de bw
		if m.fabs(x-xdev) < xbw:  
			if t > smval : smval = t			# Cojo señal maxima dentro del bw para el smeter

		posy = FFTALTO-(t*FFTK*azoom)-(6*FFTK*azoom)+base # Altura en el FFT
		dtcm +=  posy / VEC_SZ 							# media para el detect (grafico)

		if posy < t2  : t2 = posy 						# tope superior para calcular zoom
		if int(posy)+base > mi: mi = int(posy)+base		# busco base

		pts += [(x,int(posy)+base)]					# compone vector draw

		# MAXPTS
		if maxpts_enable and tframe > fft_media:
			if int(posy) < maxpts[x] :	
				maxpts[x] = int(posy)					# Calcula max
			else :
				if maxdecay_enable: maxpts[x] += 1
			mpts += [(x,maxpts[x]+1+base)]

	# Caluclo base
	if mi < FFTALTO-30:	base += 1
	if mi > FFTALTO:	base -= 1


	# AUTODETECT
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

	# AUTOZOOM
	if azoom_enable :
		if t2>(YTOP*1.05) : 
			if (azoom<MAXZOOM): 
				azoom += 0.01       # AUTOZOOM con 5% de histeresis
				calc_sq(xsq+TOPALTO)
		if t2<(YTOP*0.95) : 
			if azoom>1: 
				azoom -= 0.03
				calc_sq(xsq+TOPALTO)

	# Calculos finales
	smval 	= (smval + 5) * 1.55 		# Ajuste final smeter
	tframe	+= 1
	pts 	+= [(FFTANCHO+1,FFTALTO+1),(0,FFTALTO+1)]						#cierro para fill
	if maxpts_enable: 	mpts 	+= [(FFTANCHO+1,FFTALTO+1),(0,FFTALTO+1)]	#cierro para fill
	#print(azoom)

def waterfall(sf):
	global pm
	global wfrango,wfframe
	global ftbw

	sf.scroll(0,1)				# Empuja parriba a un pixer por frame, de momento
	if autorange_enable:
		mi = 1000
		ma = -1000
		for x in range(VEC_SZ):		# Calcula rango
			if pm[x] < mi: mi = pm[x]
			if pm[x] > ma: ma = pm[x]
		# Ampliacion es diferencia de rangos
		k = (255.0 -contraste) / (ma - mi)
	else:
		k = wfrango
		mi = -3.5
	for x in range(VEC_SZ):		# Pinta los puntos
		t = contraste + ((pm[x]-mi) * k) 	# sumo mi para dejar el limite inferior en 0	
		if t<0: 	t = 0
		if t>255: 	t = 255
		pg.gfxdraw.pixel(sf,x,0,(0,t,t))

	if not (wfframe % (FPS*5)):
		t = datetime.datetime.now().timetuple()
		fts = ftbw.render('{0:02d}:{1:02d}:{2:02d}'.format(t[3],t[4],t[5]),1, (200,100,0),(0,0,0))
		sf.blit(fts, (0,0))												
 
	wfframe += 1

def calc_dev():
	global	xdev,dev
	global	fqc,afq
	global  fqlabel1,fqlabel2
	global 	refreshfq

	a = FFTANCHO/2								# media pantalla
	dev = (xdev-a) * (SAMPLERATE/FFTANCHO)
	fq = int(fqc + dev)
	sfq = format(fq,'010d')
	sfq = sfq[:-9]+'.'+sfq[-9:-6]+'.'+sfq[-6:-3]+','+sfq[-3:]
	sfq = sfq.lstrip('0.')
	if stronger_enable: sfq = "[] " + sfq  		# Pinta una "A" de automático si está en autosint
	fqlabel1 = ftdev1.render(sfq[:len(sfq)-4], 0, DEVCOLORMHZ,BGCOLOR) # pinta dev text
	fqlabel2 = ftdev2.render(sfq[len(sfq)-3:], 0, DEVCOLORHZ,BGCOLOR)
	t = 0 											# AÑADO DESFASE A LA DESVIACION SOLO PARA USB y LSB
	if tmode=="USB" or tmode=="LSB": t = bw;		# APLICA SOLO A LA LOGICA; NO A LOS VALORES
	if REAL: sdr.set_dev(int(-dev+t))	# set dev

def calc_bw():
	global xbw,bw,maxbw
	global bwlabel
	global decirate,decimation,MINBW
	global ftbw
	global refreshfq

	a = FFTANCHO/2 											# media pantalla
	decirate= SAMPLERATE/decimation
	bw = int((SAMPLERATE*xbw)/FFTANCHO)
	if (bw >= maxbw):
		bw = maxbw
	if (bw < MINBW):
		bw = MINBW
	xbw = bw / (SAMPLERATE/FFTANCHO)
	txt = str(bw)
	bwlabel = ftbw.render(txt, 0, BWCOLOR,BWCOLOR2)
	calc_dev()												# calcula dev para USB y LSB
	if REAL: sdr.set_bw(bw)									# set bw

def calc_freq(posx,posy):
	global fqc
	global numx
	global sdr
	global refreshfq
	global tframe
	global maxpts
	global stronger_enable, dostronger

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
	if REAL: sdr.set_freq(fqc)

	calc_dev()			# Esto afecta al indicador de desviacion
	tframe = 0 			# reinicia suavizado
	if stronger_enable: dostronger = True;	# REsintoniza automaticamente

	maxpts  = [ FFTALTO for y in range(VEC_SZ)]
	refreshfq = True

def calc_sq(posy):
	global xsq,sq,base
	global sdr

	xsq = posy - TOPALTO 
	sq =  int( ((-120/azoom)*(float(xsq)/FFTALTO)) - (120.0-120.0/azoom)*(1.0-(xsq/FFTALTO)  ) )

	if sq < -120 : sq = 120
	if sq > 0 	 : sq = 0

	if REAL: sdr.set_sq(sq+(9*azoom))	# 15 for que si

def demod_mode():
	global mn,opt,xdev
	global tmode

	b = [ 	{"text":"AUTO","value":10},
			{"text":"AM","value":0},
			{"text":"FM N","value":1},
			{"text":"USB","value":2},
			{"text":"LSB","value":3},
			{"text":"FM W","value":4},
			{"text":"FM ST","value":5}
	]
	for t in b:	
		if tmode == t["text"]: t["hight"] = True

	mn = butonify.menu()
	mn.width = 150
	mn.cx = xdev
	mn.cy = 300
	mn.init(sf,b,(0,0,0),"Demod mode")

def demod_mode_response():
	global mn,opt
	global modelabel,tmode,mode
	global sdr,decimation,decirate
	global maxbw,audrate

	tmode 	= opt.texto
	mode 	= opt.value
	modelabel = ftbw.render(tmode, 0, MODECOLOR,BGCOLOR)	# Pinta el label del modo

	if opt.value != "FM ST": pgd.box(top_sf,(250,0,40,TOPALTO),BGCOLOR) # Borra preventivamente el icono de stereo

	calc_bw()
	if REAL: 
		#sdr.set_decimation(decimation)
		calc_dev()			# Calcula deviation para USB y LSB
		sdr.set_mode(mode)
	mn = None
	opt = None

def demod_menu():
	global mn,tmode
	global rec

	bus = []
	bus += [ {"type":"Switch","text":"Mode","text2":tmode,"value":1}]
	bus += [ {"type":"Switch","text":"AutoSINT","text2":tmode,"value":2}]
	bus += [ {"type":"Switch","text":"Rec","value":3} ]
	if stronger_enable:	bus[1]["text2"]="ON"
	else:				bus[1]["text2"]="OFF"
	if rec:	bus[2]["text2"]="ON"
	else:	bus[2]["text2"]="OFF"
	bus += [{"text":"Back","value":0}]

	mn = butonify.menu()
	mn.cx = xdev
	mn.cy = 250
	mn.width = 200
	mn.init(sf,bus,(0,0,0),"Demodulator")

def demod_menu_response():
	global mn,opt,retf
	global dostronger, stronger_enable
	global top_sf
	global top_sf
	global rec

	if opt.value == 1:				# llamar menu node
		retf = demod_mode_response
		demod_mode()
		return
	if opt.value == 3:				# grabar
		rec = not rec 				# pinta el punto en fft_frame
		if not rec: pgd.filled_circle(top_sf, smx+sml+TOPALTO/2, TOPALTO/2, TOPALTO/4, BGCOLOR)	#Borra botón rojo izquierda smeter
		if REAL: sdr.set_rec(not rec)	#Activa REC. como es una valvula va al reves
	if opt.value == 2:				# AutoSINT
		stronger_enable = not stronger_enable
		if stronger_enable: dostronger = True

	mn = None

def attend_mouse(sf):
	global xbw,xdev,minipaso
	global possq
	global retf
	global SALIDA

	for evt in pg.event.get():
		if (evt.type == pg.QUIT):
			print("[+] Evento de salida")
			SALIDA = True
			continue
		if ( ((evt.type == pg.MOUSEBUTTONDOWN or evt.type == pg.MOUSEBUTTONUP) and  evt.button == 1) or 
			(evt.type == pg.MOUSEMOTION and evt.buttons[0] == 1) ) :										# boton izquierdo
			if TOPANCHO-evt.pos[0] < 48  and evt.pos[1] < 24 :		# MENU PRINCIPAL
				main_menu()
				retf = main_menu_response														
				continue
			if m.fabs(evt.pos[0] - possq[0]) < 50  and m.fabs(evt.pos[1]-possq[1]-50) < 50 :	# Si xestá en los ´ultimos 20 pixels y a la altura del
				calc_sq(evt.pos[1]-base)															# squelch. 
				continue
			# Va a ser freq
			if evt.type == pg.MOUSEBUTTONDOWN and evt.button == 1 and evt.pos[1]<TOPALTO :	# Digitos de frecuencia
				calc_freq(evt.pos[0],evt.pos[1])
				continue
			if (evt.pos[1] > TOPALTO):														# desviacion
				xdev = evt.pos[0]
				calc_dev()
				continue
		if ( ((evt.type == pg.MOUSEBUTTONDOWN or evt.type == pg.MOUSEBUTTONUP) and  evt.button == 3) or 
			(evt.type == pg.MOUSEMOTION and evt.buttons[2] == 1) ) :					# boton derecho
			#print(m.fabs(evt.pos[0]-xdev-xbw),evt.pos[1]) 				# ancho de banda

			if m.fabs(evt.pos[0]-xdev) < 20 and m.fabs(evt.pos[1]-BWY-40) < 20 :		# Menu demodulacion
				demod_menu()
				retf = demod_menu_response
				continue
			if m.fabs(evt.pos[0]-xdev) < xmaxbw and evt.pos[1] > TOPALTO+BWY :				# ancho de banda
				xbw = m.fabs(evt.pos[0]-xdev)			
				calc_bw()
				continue
			if evt.pos[1] > TOPALTO+FFTALTO:
				retf = waterfall_response				# Sino, menu del waterfall
				waterfall_menu()
				continue
			if evt.pos[1] < TOPALTO+BWY:
				retf = fft_menu_response					# Sino, menu del FFT
				fft_menu()
				continue
		if  ((evt.type == pg.MOUSEBUTTONDOWN or evt.type == pg.MOUSEBUTTONUP) and  evt.button == 4): # boton rueda de enmedio
			xdev += minipaso
			calc_dev()
			continue
		if  ((evt.type == pg.MOUSEBUTTONDOWN or evt.type == pg.MOUSEBUTTONUP) and  evt.button == 5): # boton rueda de enmedio
			xdev -= minipaso
			calc_dev()
			continue

def fft_menu(refresh = False):
	global mn

	b = []
	b += [ {"text":"Cancelation", "value":1 }]
	b += [ {"text":"Fill", "value":2 }]
	b += [ {"text":"Peak", "value":3 }]
	b += [ {"text":"Decay", "value":4 }]
	b += [ {"text":"Detect", "value":5}]
	b += [ {"text":"AutoZOOM", "value":6 }]
	for i in b:
		i["type"]	= "Switch"
		i["text2"]	= "OFF"
	if linecancel_enable: 	b[0]["text2"] = "ON"
	if fftfill_enable: 		b[1]["text2"] = "ON"
	if maxpts_enable: 		b[2]["text2"] = "ON"
	if maxdecay_enable: 	b[3]["text2"] = "ON"
	if detect_enable: 		b[4]["text2"] = "ON"
	if azoom_enable: 		b[5]["text2"] = "ON"
	b += [ {"text":"Back", "value":0}]

	mn = butonify.menu()
	mn.width 	= 200
	mn.cx 		= pg.mouse.get_pos()[0]
	mn.cy 		= TOPALTO+250
	if refresh: mn.frame = 48 # no scroll
	mn.init(sf,b,(0,0,0),"FFT Menu")

def fft_menu_response():
	global mn,opt
	global linecancel_enable,fftfill_enable, maxpts_enable, maxdecay_enable, detect_enable, azoom_enable

	if opt.value == 1:	linecancel_enable = not linecancel_enable
	if opt.value == 2:	fftfill_enable 	= not fftfill_enable
	if opt.value == 3:	maxpts_enable  	= not maxpts_enable
	if opt.value == 4:	maxdecay_enable = not maxdecay_enable
	if opt.value == 5:	detect_enable 	= not detect_enable
	if opt.value == 6:	azoom_enable 	= not azoom_enable

	if opt.value == 0:	
		mn = opt = None
	else:
		mn = None
		fft_menu(True)

def waterfall_menu(refresh=False):
	global mn

	b = []
	b += [ {"text":"Autorange", "value":1 }]
	for i in b:
		i["type"]	= "Switch"
		i["text2"]	= "OFF"
	if autorange_enable: 	b[0]["text2"] = "ON"
	b += [ {"text":"Back", "value":0}]

	mn = butonify.menu()
	mn.width 	= 200
	mn.cx 		= pg.mouse.get_pos()[0]
	mn.cy 		= 150
	if refresh: mn.frame = 48 # no scroll
	mn.init(sf,b,(0,0,0),"WF Menu")

def waterfall_response():
	global mn,opt
	global autorange_enable

	if opt.value == 1:	autorange_enable = not autorange_enable

	if opt.value == 0:	
		mn = opt = None
	else:
		mn = None
		waterfall_menu(True)

def main_menu():
	global mn
	global tupper,tdown

	b = [ 	{"type":"Switch","text":"Upper window","text2":tupper,"value":1},
			{"type":"Switch","text":"Lower window","text2":tdown,"value":2},
			{"text":"Frontend config","value":3},
			{"text":"Back","value":4}
	]
	mn = butonify.menu()
	mn.width = 300
	mn.cx = FFTANCHO - 150
	mn.header = "Main"
	mn.init(sf,b,(0,0,0),"Menu")

def main_menu_response():
	global mn,opt,retf
	global tupper,tdown

	if opt.value == 1: 	# FFT MENU
		#retf = fft_menu_response
		#fft_menu()
		return

	if opt.value == 4: 	# EXIT
		mn = None
		opt = None

def pantalla_init():
	global bw, fq
	global bwlabel, fqlabel
	global ftbw,ftdev1,ftdev2,ftqc
	global fft_sf, top_sf, dwn_sf
	global menusf,stereosf

	pg.init()
	os.environ["SDL_VIDEO_CENTERED"] = "TRUE"
	pg.display.set_mode(MAIN_SIZE)
	#print(pg.display.Info())
	sf = pg.display.get_surface()
	sf.fill(BGCOLOR)

	# Surfaces TOP & FFT (subsurfaces del main)
	top_sf= sf.subsurface((0,0,TOPANCHO,TOPALTO))		
	fft_sf= sf.subsurface((0,TOPALTO,FFTANCHO,FFTALTO))
	dwn_sf= sf.subsurface((0,TOPALTO+FFTALTO,FFTANCHO,DWNALTO))

	#print(pg.font.get_fonts())

	ftdev1 = pg.font.SysFont(FONT,18)						
	ftdev2 = pg.font.SysFont(FONT,16)						
	ftbw   = pg.font.SysFont(FONT,16)						
	ftqc   = pg.font.SysFont('ubuntumono',48)						

	# pinta smeter
	pgd.box(top_sf,(smx,0,sml,TOPALTO),(0,0,0))
	fsm = pg.font.SysFont('ubuntumono',14)						
	fsq = fsm.render(' S 1  3  5  7  9 +20 +40 +60', 1, (200,200,200),(0,0,0))
	top_sf.blit(fsq, (smx,5))													# Pinta smeter label
	fsq = fsm.render(' ||||||||||||||||||||||||||', 1, (200,200,200),(0,0,0))
	top_sf.blit(fsq, (smx,19))													# Pinta smeter guia
	pgd.box(top_sf,(smx+10,23,sml-25,2),(200,200,200))

	# pinta boton menu
	menusf = pg.image.load(MENUIMG)
	top_sf.blit(menusf,(TOPANCHO-50,0))

	# icono stereo
	stereosf = pg.image.load(STEREOIMG)

	# Icono aplicación
	pg.display.set_icon(stereosf)

	return sf

def pantalla_refresh(sf):
	global pts,mpts
	global xbw,xdev
	global fq,fqc,bw
	global modelabel,bwlabel,fqlabel1,fqlabel2
	global ftqc, numx
	global maxfill_enable, maxpts_enable, refreshfq
	global azoom, base
	global fft_sf,top_sf
	global sq,xsq,asq,smval,smvaladj,possq
	global frame, count
	global menusf,stereosf

	a = FFTANCHO/2 										# media pantalla
	pleft = fqlabel1.get_size()[0]/2 + fqlabel2.get_size()[0]/2 

	fft_sf.fill(BGCOLOR) 									# Borra BW Más rapido que reescribir.

	# PINTA ESCALA
	for x in range(12):										# Escala FFT
		y = int(FFTALTO - (x*(FFTALTO/12))*azoom) + base
		if y > 0 :
			pgd.hline(fft_sf,0,FFTANCHO,y,ESCCOLOR)
			lb = ftdev1.render(str((12-x)*-10), 0, ESCCOLOR,BGCOLOR) # pinta dev text
			fft_sf.blit(lb, (0,y-10))	# Pinta fq label

	# Pinta BW
	txbw 	= 2*xbw
	txdev   = xdev
	tcodo 	= txdev - txbw/2
	if 	tmode != "FM W" and tmode != "FM ST":	# WFM no tiene ancho de banda
		if 	tmode == "USB":						
			txbw /= 2	
			tcodo = txdev
		elif tmode == "LSB": 	
			txbw /= 2	
			tcodo = txdev - txbw
		fft_sf.fill(BWCOLOR2,(tcodo,BWY,txbw,FFTALTO-BWY),0) 		# Pinta BW
		pgd.rectangle(fft_sf,(tcodo,BWY,txbw,FFTALTO-BWY),BWCOLOR)
	pgd.vline(fft_sf,int(xdev),0,FFTALTO,DEVCOLOR)					# Pinta linea dev

	# PINTA MAX
	if maxpts_enable:												# Pintta puntos de max
		mpts += [(FFTANCHO,FFTALTO),(0,FFTALTO)]
		pgd.polygon(fft_sf,mpts,MAXCOLOR)

	# PINTA FILL
	if fftfill_enable:												# Pintta FFT relleno (Más rápido que el fill)
		for x in pts: pgd.vline(fft_sf,x[0],x[1],FFTALTO,FILLCOLOR)				

	# PINTA FFT
	pgd.polygon(fft_sf,pts,FGCOLOR)									# pinta FFT

	# PINTA DETECT
	if detect_enable :												# Pinta detector picos
		for x in dtc :	pgd.circle(fft_sf,x[0],x[1],10,DETECTCOLOR)

	# PINTA DEV
	if 	tmode != "FM W" and tmode != "FM ST":
		fft_sf.blit(bwlabel,  (txdev-bwlabel.get_size()[0]/2,BWY+2))	# Pinta bw label
		fft_sf.blit(fqlabel1, (txdev-pleft,BWY-22))						# Pinta dev label 
		fft_sf.blit(fqlabel2, (txdev-pleft+fqlabel1.get_size()[0]+4,BWY-20))	
	fft_sf.blit(modelabel,(txdev-modelabel.get_size()[0]/2,BWY-40))	# Pinta mode label

	# pinta Sqelch
	tc 	= SQCOLOR
	tsq = 0
	if REAL: tsq = sdr.probe_sq.level()				# Lee el nivel para ver si está levantado el squelch
	if 	tsq != asq: tc = (0,200,0)			# Si está levantado pinta verde
	pgd.hline(fft_sf,0,FFTANCHO,xsq+base, tc)
	fsq = ftdev2.render('SQ '+str(sq), 0, DEVCOLORHZ,BGCOLOR)
	fft_sf.blit(fsq, (FFTANCHO-fsq.get_size()[0],xsq-12+base))		# Pinta bw label

	possq = (FFTANCHO-fsq.get_size()[0]+25,xsq-12+base+12)	# Guardo posicion para el botón
	#pgd.circle(fft_sf,possq[0],possq[1],50,(200,200,200))
	asq = tsq

	# pinta smeter
	pgd.box(top_sf,(smx+13,25,sml-28,9),(0,0,0))
	pgd.box(top_sf,(smx+13,27,smval*smvaladj,6),(255,50,50))

	# PINTA CIFRAS DE FREQ SI HAN CAMBIADO
	if refreshfq:	
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
			fqclabel = ftqc.render(txt[x], 1, FQCCOLOR, col)		# pinta fqc text
			top_sf.blit(fqclabel,(px,0))							# blit
			if txt[x] not in ['.',','] : numx += [px]				# Almacena la coordenada del numero

	# PINTA MENU IF ANY
	if mn : mn.refresca()

	# PARPADEA BOTON ROJO IF REC
	if rec:
		if frame == FPS/2: 
			pgd.filled_circle(top_sf, smx+sml+TOPALTO/2, TOPALTO/2, TOPALTO/4, BGCOLOR)		#Borra botón rojo izquierda smeter
		if frame == 1:
			pgd.filled_circle(top_sf, smx+sml+TOPALTO/2, TOPALTO/2, TOPALTO/4, tc)			#Pinta botón del color del smeter

	# Pinta STEREO si STEREO
	if REAL and tmode == "FM ST":
		if (sdr.probe_st.level() > 0.5 ): 
			top_sf.blit(stereosf,(250,8))
		else:
			pgd.box(top_sf,(250,0,40,TOPALTO),BGCOLOR)

	# Flipea/Vuelca la pantalla
	pg.display.flip()							
	refreshfq = False
	frame = (frame % FPS) +1	
	count += 1

if __name__ == "__main__":

	xm = 0
	soc = 0
	clk = pg.time.Clock()

	print("[+] ISMASRADIO (c) 2016")

	print("[+] Init")
	pm		= [ 0.0 for y in range(VEC_SZ)]
	py 		= [[0 for y in range(VEC_SZ)] for x in range(fft_media)]		# soften matrix
	maxpts  = [ FFTALTO for y in range(VEC_SZ)]

	print("[+] Recuperando estado")
	try:
		f = open('SorDeRa.stats','r')
		fqc 	= pickle.load(f)
		dev 	= pickle.load(f)
		xdev 	= pickle.load(f)
		mode 	= pickle.load(f)
		tmode 	= pickle.load(f)
		sq 		= pickle.load(f)
		xsq		= pickle.load(f)
		f.close()
	except:
		print("[-] ERROR LEYENDO FICHERO ESTADO")

	if (REAL):
		print("[+] Estableciendo valores logica")
		sdr = logic.SorDeRa_sdr()
		sdr.set_VEC(VEC_SZ)
		sdr.set_aud_rate(audrate)
		sdr.set_samp_rate(SAMPLERATE)
		sdr.set_freq(fqc)
		sdr.set_bw(bw)
		sdr.set_dev(-dev)
		sdr.set_sq(sq)

		print("[+] Arrancando logica")
		os.spawnl(None, "/usr/bin/pulseaudio -k")
		sdr.start()

	print("[+] Generando ventana")
	sf = pantalla_init()

	calc_dev()
	calc_bw()
	calc_freq(0,0)
	calc_sq(FFTALTO/2)
	opt = butonify.buton()
	opt.init(sf,{"text":tmode,"value":mode})
	demod_mode_response()

	print("[+] Entrando a bucle principal")
	refreshfq = True

	upperf 	= FFT_frame			# Funcion superior
	tupper	= "FFT"
	downerf	= waterfall			# Funcion inferior
	tdown	= "Waterfall"
	while not SALIDA:
		if mn :							# Si existe un menu, gestiona menus
			opt = mn.selecciona()		# Lee botonera
			if opt: retf()				# Si se ha devuelto valor, salimos a la función de retorno
		else:
			attend_mouse(fft_sf)		# Si no hay menu, botones estandard.
		clk.tick(FPS)
		pg.display.set_caption(CAPTION + str(int(clk.get_fps())))
		FFT_get()
		# UPPER
		upperf(fft_sf)
		# DOWNER
		downerf(dwn_sf)
		pantalla_refresh(sf)

	print("[+] Guardando estado")
	try:
		f = open('SorDeRa.stats','w')
		pickle.dump(fqc, f)
		pickle.dump(dev, f)
		pickle.dump(xdev, f)
		pickle.dump(mode, f)
		pickle.dump(tmode, f)
		pickle.dump(sq, f)
		pickle.dump(xsq, f)
		f.close()
	except:
		print("[-] ERROR CREADNO FICHERO ESTADO")

	print("[+] Saliendo")
	if REAL: sdr.stop()
	pg.quit()
	sys.exit()
