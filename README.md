# SorDeRa
A light, sensible, powerfull but practical SDR receiver that makes use of computer power to automatize and enhanced reception and use. 
Eembedable. GNURADIO based.

This is IN DEVELOPMENT - PRE PRE ALFA state. Asume this not works. Nothing.

Requirements:
	* Gnuradio >= 3.7.x
	* Gnuradio gr-funcube
	* Python >= 2.7.3
	* Pygame >= 1.9

Supoorts:
	* FUNCube Dongle Pro+ 
	* TODO more

Usage:
 $ pulseaudio -k
 $ cd py
 $ ./SorDeRa_hmi.py

Features:
	* Basic demodulations: AM, USB, LSB, FMN
	* FM W, FM Stereo
	* FFT				* Waterfall
	* FFT Autorange			* Waterfall Autorange
	* FFT Autocenter bottom		* FFT maximums
	* Point-and-click tune		* Zero IQ cancelation
	* Point-and-click bandwith	* Autogain, no AGC needed
	* Point-and-click squelch	* S-Meter
	* Squelch recorder		* Carrier detector

	* No window manager.
	* "Material Design"-like unfolding animated menus

 TO-DO
	* Thousillions of bugs killing
	* Support other radios (osmocomm)
	* Frontend parameters	
	* Auto tune
	* Channels, set, record, ranges.
	* Bands, ranges
	* Scanning, several types
	* Multi demodulators
	* HAM modes: CW with decoder, packet, rtty, etc
	* Digital modes.
	* Pluggable demodulators
	* Advanced features
