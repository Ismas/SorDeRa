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
import math as m
import time
import numpy as np

import SorDeRa_sdr as logic

PORT		= "/dev/ttyUSB2"
BAUD 		= 19200

RES			= 5
VEC_SZ		= 1280
FFTALTO		= 500
MAIN_SIZE	= (1280,600)
BGCOLOR		= (25,25,100)
FGCOLOR		= (200,200,25)
FONDO		= (25,100,100)
FONDO2		= (100,100,100)
FONT 		= "arial"

FFTK   		= 9*(FFTALTO/120) 
azoom  		= 1.5
py			= []

#FMIN		= 10e6
#FMAX		= 200e6
FMIN		= 70e6
FMAX		= 130e6
STEP		= (FMAX-FMIN)/VEC_SZ
FPS			= 0

t 			= 0.0
SALIDA 		= False

cal 		= [ 0.0 for y in range(VEC_SZ)]
elmax		= 0

def doit(calibrar):
	global SALIDA
	global cal,elmax
	# CLS
	#sf.fill(BGCOLOR)

	# Pinta grafica
	for i in range(10):
		pgd.hline(sf,0,VEC_SZ,i*50,FONDO)
	elpaso = (FMAX-FMIN)/(int(VEC_SZ)/50)
	for i in range(int(VEC_SZ/50)+1):
		pgd.vline(sf,i*50,0,500,FONDO)
		#if (i % 3 ) == 0:
		fs = ft.render(str((FMIN+(elpaso*i))/1e6), 1,FGCOLOR, BGCOLOR)
		sf.blit(fs, (i*50,505))
		#print(str((FMIN+(elpaso*i))/1e6))

	for i in np.arange(0,VEC_SZ,RES):
		# SINTONIZA
		fq = FMIN+(STEP*i)
		sdr.set_freq(fq)

		f2 = int(fq)
		if fq>50e6: f2 = 125e6-int(fq)
		if fq>125e6: f2 = int(fq)-125e6
		f.write("F"+str(int(f2))+"\n")

		# ESPERA
		time.sleep(0.04)
		~clk.tick(30)

		#BORRA EL DATO ANTERIOR
		#pg.gfxdraw.pixel(sf,i,FFTALTO-int(py[i]),BGCOLOR);
		pg.draw.rect(sf,BGCOLOR,(i-RES,0,RES,10));
		pg.draw.line(sf,BGCOLOR,(i,FFTALTO-int(py[i])),(i+RES,FFTALTO-int(py[i])));

		# COJE DATO. EL MAYOR DEL FFT
		ma = -10000000;
		for x in sdr.fft_probe.level():
				if x > ma: ma = x;
		#print(ma)
		t = 5+m.log10(ma)

		# Usa calibración
		if cal[i] != 0.0: t = t+ (elmax-cal[i])

		if calibrar: 
			cal[i] = t
		 	if t > elmax: elmax=t

		# GUARDA PA LUEGO
		py[i] = t*FFTK;

		# PINTA
		#pg.gfxdraw.pixel(sf,i,FFTALTO-int(py[i]),FGCOLOR);
		pg.draw.rect(sf,FGCOLOR,(i,0,RES,10));
		pg.draw.line(sf,FGCOLOR,(i,FFTALTO-int(py[i])),(i+RES,FFTALTO-int(py[i])));

		# Muestra
		pg.display.flip()		

		for evt in pg.event.get():			
			if (evt.type == pg.QUIT):
				SALIDA = True

		if SALIDA: quit()


if __name__ == "__main__":

	print("*** BUSCANDO GENERADOR RF **")

	t = PORT

	# Puerto a 19200: stty -F /dev/ttyUSB2 speed 19200
	#os.execvp("stty",  ("-F "+t ," speed "+str(BAUD)))

	PORT = ""
	f = open(t,"rw+")
	f.write("A\n")
	time.sleep(1)
	q = f.readline()
	if q[:2] == "OK": PORT = t;
	else:
		print"ooo NO "+t

	if PORT != "": print("+++ ENCONTRADO EN "+PORT)
	else:
		print("--- NO ENCONTRADO")
		quit()

	print("[+] Init")

	pg.init()
	os.environ["SDL_VIDEO_CENTERED"] = "TRUE"
	pg.display.set_mode(MAIN_SIZE)
	#print(pg.display.Info())
	sf = pg.display.get_surface()
	sf.fill(BGCOLOR)
	ft = pg.font.SysFont(FONT,12)						

	sdr = logic.SorDeRa_sdr()
	sdr.start()
	sdr.set_mode(1)
	sdr.set_VEC(VEC_SZ)
	sdr.set_aud_rate(11200)
	sdr.set_samp_rate(192000)
	sdr.set_freq(FMIN)
	sdr.set_bw(1000)
	sdr.set_dev(-10000)
	sdr.set_sq(-100)
	sdr.set_lai(-0.0032)
	sdr.set_laj(-0.0034)

	py	= [ 0.0 for y in range(VEC_SZ)]

	clk = pg.time.Clock()

	sf.fill(BGCOLOR)

	######### CALIBRACIÓN
	pg.display.set_caption("ANALIZADOR DE ESPECTRO                    ******* CALIBRANDO *********")
	pg.display.flip()		
	doit(True)

	######### EJECUCIÓN
	pg.display.set_caption("ANALIZADOR DE ESPECTRO                    ** RUN **")
	pg.display.flip()		
	while not SALIDA:
		doit(False)


