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
MAXCOLOR    = (50, 50, 0)
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

# GFX
MENUIMG = "gfx/menu.png"

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
xdev 	= FFTANCHO/2 - (20000/FFTANCHO)
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
bwlabel = 0		#surface

#SQ
sq 		= -70
xsq		= FFTALTO/2 
asq		= 0.0

# Mode
mode = 0
tmode = "AM"
modex = 0
modelabel = ""

# FFT
numx	= []
py 		= []	# valores puntos
pydx 	= 0		# indice matriz para media
maxpts  = []	# maximos
mpts 	= []
fft_media = 10     # cantidad de media

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
MAXZOOM = 10
base  = 0
tope  = FFTALTO
YTOP  = 100

# rec
rec 	= False

mn 		= None
retf 	= None
SALIDA 	= False

ma = -100
mi = 100

def FFT_frame(sock,sf):
	global py,pydx,fft_media
	global pts,maxpts,mpts
	global mindB,maxdB
	global azoom,azoom_enable,MAXZOOM,base,tope,YTOP
	global dtc,detect_enable
	global refreshfq
	global tframe
	global smval,xdev
	global sdr

	# ADQUISICION DE DATOS
	y 	= []	
	if (REAL):
		y = sdr.fft_probe.level() 
	else:
		for x in range(VEC_SZ):	y += [ random.random() /1000]

	#for x in range(VEC_SZ):
		#t = 20*m.log10(y[x])

	# RANGO [-10,5] -> +10 -> [0,15]
	# 120/15 = 8 -> dBs
	# FFTALTO/120 = 
	#if t > ma: ma = t
	#if t < mi: mi = t

	# BUCLE PRINCIPAL CALCULOS
	t 		= 0.0
	t2 		= FFTALTO
	t3 		= 0
	pts 	= []
	mpts 	= []
	smval 	= 0
	dtc 	= []
	tope 	= 0
	dtcm	= 0
	smval 	= -10.0
	for x in range(VEC_SZ):
		py[pydx][x] = m.log10(y[x]) 					# Almaceno dBs
		for x2 in range(fft_media):	t += py[x2][x]		# media de los fft_media valores
		t /= fft_media

		# SMETER
		# Media de lo que hay dentro de bw
		if m.fabs(x-xdev) < xbw:  
			if t > smval : smval = t			# Cojo señal maxima dentro del bw para el smeter

		posy = FFTALTO-(t*FFTK*azoom)-(6*FFTK*azoom)+base # Altura en el FFT
		dtcm +=  posy / VEC_SZ 							# media para el detect (grafico)

		if posy>FFTALTO : base += 1						# AUTOBASE cuando se sale por debajo
		#if posy > t3 : t3 = posy						# AUTOBASE cuando no llega abajo

		if posy < t2  : t2 = posy 						# tope superior para calcular zoom
		pts += [(x,m.trunc( posy ))]					# compone vector draw

		# MAXPTS
		if maxpts_enable and tframe > fft_media:
			if m.trunc(posy) < maxpts[x] :	
				maxpts[x] = m.trunc(posy)					# Calcula max
			else :
				if maxdecay_enable: maxpts[x] += 1
			mpts += [(x,maxpts[x]+1)]


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
				azoom -= 0.01
				calc_sq(xsq+TOPALTO)

	# Calculos finales
	smval 	= (smval + 5) * 1.55 		# Ajuste final smeter
	tframe	+= 1
	pts 	+= [(FFTANCHO+1,FFTALTO+1),(0,FFTALTO+1)]						#cierro para fill
	if maxpts_enable: 	mpts 	+= [(FFTANCHO+1,FFTALTO+1),(0,FFTALTO+1)]	#cierro para fill
	pydx 	= (pydx+1) % fft_media
	#print(azoom)

def calc_dev():
	global	xdev,dev
	global	fqc,afq
	global  fqlabel1,fqlabel2
	global 	refreshfq

	a = FFTANCHO/2											# media pantalla
	dev = (xdev-a) * (SAMPLERATE/FFTANCHO)
	fq = m.trunc(fqc + dev)
	sfq = format(fq,'010d')
	sfq = sfq[:-9]+'.'+sfq[-9:-6]+'.'+sfq[-6:-3]+','+sfq[-3:]
	sfq = sfq.lstrip('0.')
	fqlabel1 = ftdev1.render(sfq[:len(sfq)-4], 0, DEVCOLORMHZ,BGCOLOR) # pinta dev text
	fqlabel2 = ftdev2.render(sfq[len(sfq)-3:], 0, DEVCOLORHZ,BGCOLOR)
	if REAL: sdr.set_dev(m.trunc(-dev))	# set dev


def calc_bw():
	global xbw,bw,maxbw
	global bwlabel
	global decirate,decimation,MINBW
	global ftbw
	global refreshfq

	a = FFTANCHO/2 											# media pantalla
	decirate= SAMPLERATE/decimation
	bw = m.trunc((SAMPLERATE*xbw)/FFTANCHO)
	if (bw >= maxbw):
		bw = maxbw
	if (bw < MINBW):
		bw = MINBW
	xbw = bw / (SAMPLERATE/FFTANCHO)
	txt = str(bw)
	bwlabel = ftbw.render(txt, 0, BWCOLOR,BWCOLOR2)
	if REAL: sdr.set_bw(bw)									# set bw


def calc_freq(posx,posy):
	global fqc
	global numx
	global sdr
	global refreshfq
	global tframe
	global maxpts

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

	maxpts  = [ FFTALTO for y in range(VEC_SZ)]
	refreshfq = True


def calc_sq(posy):
	global xsq,sq
	global sdr

	xsq = posy - TOPALTO
	#sq =  m.trunc( (-120*xsq/FFTALTO) )
	sq =  m.trunc( ((-120/azoom)*(float(xsq)/FFTALTO)) - (120.0-120.0/azoom)*(1.0-(xsq/FFTALTO)  ) )
	if sq < -120 : sq = 120
	if sq > 0 	 : sq = 0
	if REAL: sdr.set_sq(sq+15.25)	# 15 for que si


def demod_mode():
	global mn,opt,xdev
	global tmode

	b = [("AUTO",10),("AM",0),("FM N",1),("FM W",3),("USB",2),("LSB",2)]
	bus = []
	for t in b:	
		k = False
		if tmode == t[1]: k = True
		bus.append((t[0],t[1],k))
	mn = butonify.menu()
	mn.width = 100
	mn.header = "MODE"
	mn.cx = xdev
	mn.init(sf,bus,(200,130,0))


def demod_mode_response():
	global mn,opt
	global modelabel,tmode,mode
	global sdr,decimation,decirate
	global maxbw,audrate

	tmode 	= opt.texto
	mode 	= opt.value
	modelabel = ftbw.render(tmode, 0, MODECOLOR,BGCOLOR)	# Pinta el label del modo

	#if tmode == "FM W":
	#	sdr.set_aud_rate(48000)
	#	maxbw = SAMPLERATE/2
	#else:
	#	sdr.set_aud_rate(audrate)
	#	maxbw = audrate/2
	calc_bw()
	if REAL: 
		sdr.set_decimation(decimation)
		sdr.set_mode(mode)
	mn = None
	opt = None


def demod_menu():
	global mn,tmode
	global rec

	bus = []
	bus += [("MODE:"+tmode,1)]
	if rec:
		bus += [("REC:ON",2)]
	else:
		bus += [("REC",2)]
	bus += [("EXIT",0)]

	mn = butonify.menu()
	mn.cx = xdev
	mn.width = 100
	mn.header = "DEMOD"
	mn.init(sf,bus,(100,100,100))

def demod_menu_response():
	global mn,opt,retf
	global top_sf
	global top_sf
	global rec

	if opt.value == 1:				# llamar menu node
		retf = demod_mode_response
		demod_mode()
		return
	if opt.value == 2:				# grabar
		rec = not rec 				# pinta el punto en fft_frame
		if not rec: pgd.filled_circle(top_sf, smx+sml+TOPALTO/2, TOPALTO/2, TOPALTO/4, BGCOLOR)	#Borra botón rojo izquierda smeter
		sdr.set_rec(not rec)	#Activa REC. como es una valvula va al reves

	mn = None

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
			(evt.type == pg.MOUSEMOTION and evt.buttons[0] == 1) ) :										# boton izquierdo
			if m.fabs(evt.pos[0] - FFTANCHO) < 50  and m.fabs(evt.pos[1]-xsq-TOPALTO) < 50 :	# Si xestá en los ´ultimos 20 pixels y a la altura del
				calc_sq(evt.pos[1])																# squelch
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
			(evt.type == pg.MOUSEMOTION and evt.buttons[2] == 1) ) :										# boton derecho
			if m.fabs(evt.pos[0]-xdev) < 20 and m.fabs(evt.pos[1]-BWY-40) < 20 :		# Menu demodulacion
				demod_menu()
				retf = demod_menu_response
				continue
			if evt.pos[1] > TOPALTO+BWY :				# ancho de banda
				xbw = m.fabs(evt.pos[0]-xdev)			
				calc_bw()
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

	# pinta smeter
	pgd.box(top_sf,(smx,0,sml,TOPALTO),(0,0,0))
	fsm = pg.font.SysFont('ubuntumono',14)						
	fsq = fsm.render(' S 1  3  5  7  9 +20 +40 +60', 0, (200,200,200),(0,0,0))
	top_sf.blit(fsq, (smx,5))													# Pinta smeter label
	fsq = fsm.render(' ||||||||||||||||||||||||||', 0, (200,200,200),(0,0,0))
	top_sf.blit(fsq, (smx,19))													# Pinta smeter guia
	pgd.box(top_sf,(smx+10,23,sml-25,2),(200,200,200))

	# pinta boton menu
	menusf = pg.image.load(MENUIMG)
	top_sf.blit(menusf,(TOPANCHO-50,0))


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
	global sq,xsq,asq,smval,smvaladj
	global frame

	a = FFTANCHO/2 										# media pantalla
	pleft = fqlabel1.get_size()[0]/2 + fqlabel2.get_size()[0]/2 

	fft_sf.fill(BGCOLOR) 									# Borra BW Más rapido que reescribir.

	for x in range(12):										# Escala FFT
		y = m.trunc(FFTALTO - (x*(FFTALTO/12))*azoom) + base
		if y > 0 :
			pgd.hline(fft_sf,0,FFTANCHO,y,ESCCOLOR)
			lb = ftdev1.render(str((12-x)*-10), 0, FQCCOLOR,BGCOLOR) # pinta dev text
			fft_sf.blit(lb, (0,y-10))	# Pinta fq label

	# Pinta BW
	if 	tmode != "FM W" :
		if 		tmode == "USB":	tm = xdev
		elif 	tmode == "LSB":	tm = xdev-xbw*2	
		else:					tm = xdev-xbw
		fft_sf.fill(BWCOLOR2,(tm,BWY,xbw*2,FFTALTO-BWY),0) 			# Pinta BW
		pgd.rectangle(fft_sf,(tm,BWY,xbw*2,FFTALTO-BWY),BWCOLOR)
	pgd.vline(fft_sf,xdev,0,FFTALTO,DEVCOLOR)						# Pinta dev

	# PINTA FFT
	if maxpts_enable:												# Pintta puntos de max
		mpts += [(FFTANCHO,FFTALTO),(0,FFTALTO)]
		pgd.polygon(fft_sf,mpts,MAXCOLOR)
	if fftfill_enable:												# Pintta FFT relleno (Más rápido que el fill)
		for x in pts: pgd.vline(fft_sf,x[0],x[1],FFTALTO,FILLCOLOR)				
	pgd.polygon(fft_sf,pts,FGCOLOR)									# pinta FFT
	if detect_enable :												# Pinta detector picos
		for x in dtc :	pgd.circle(fft_sf,x[0],x[1],10,MAXCOLOR)

	# PINTA DEV
	if 	tmode != "FM W" :
		fft_sf.blit(bwlabel,  (xdev-bwlabel.get_size()[0]/2,BWY+2))		# Pinta bw label
		fft_sf.blit(fqlabel1, (xdev-pleft,BWY-22))						# Pinta dev label 
		fft_sf.blit(fqlabel2, (xdev-pleft+fqlabel1.get_size()[0]+4,BWY-20))	
	fft_sf.blit(modelabel,(xdev-modelabel.get_size()[0]/2,BWY-40))	# Pinta mode label

	# pinta Sqelch
	tc 	= SQCOLOR
	tsq = 0
	if REAL: tsq = sdr.probe_sq.level()				# Lee el nivel para ver si está levantado el squelch
	if 	tsq != asq: tc = (0,200,0)			# Si está levantado pinta verde
	pgd.hline(fft_sf,0,FFTANCHO,xsq, tc)
	fsq = ftdev2.render('SQ '+str(sq), 0, DEVCOLORHZ,BGCOLOR)
	fft_sf.blit(fsq, (FFTANCHO-fsq.get_size()[0],xsq-12))		# Pinta bw label
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
			fqclabel = ftqc.render(txt[x], 0, FQCCOLOR, col)		# pinta fqc text
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

	# Flipea/Vuelca la pantalla
	pg.display.flip()							
	refreshfq = False
	frame = (frame % FPS) +1	


if __name__ == "__main__":

	xm = 0
	soc = 0
	clk = pg.time.Clock()

	print("[+] ISMASRADIO (c) 2016")

	print("[+] Init")
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
		#os.spawnl(os.P_DETACH, "aplay -r 48000 -f FLOAT_LE /tmp/SOUNDOUT")
		sdr.start()

	print("[+] Generando ventana")
	sf = pantalla_init()

	calc_dev()
	calc_bw()
	calc_freq(0,0)
	calc_sq(FFTALTO/2)
	opt = butonify.buton()
	opt.value = mode
	opt.init(sf,tmode,(0,0,0))
	demod_mode_response()

	print("[+] Entrando a bucle principal")
	refreshfq = True
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
