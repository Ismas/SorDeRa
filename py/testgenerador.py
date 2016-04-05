#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#	SorDeRa (c) Ismas 2016
#	A sensible SDR radio
#
import os
import time

if __name__ == "__main__":
	print("*** BUSCANDO GENERADOR RF **")

	t = "/dev/ttyUSB2"
	PORT = ""
	f = open(t,"rw+")
	f.write("A\n")
	time.sleep(1)
	q = f.readline()
	if q[:2] == "OK": 
		PORT = t;
		print(q)
	else:
		print"ooo NO "+t

	while True:
		for i in range(50):
			# SINTONIZA
			fq = int(10e6+(2000*i))
			s = "F"+str(fq)+'\n'
			f.write(s)
			print(fq,s)
			time.sleep(0.01)
