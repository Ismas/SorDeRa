#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: RX logic
# Author: Ismas
# Description: A sensible SDR receiver
# Generated: Sun Mar  6 21:37:29 2016
##################################################

from gnuradio import analog
from gnuradio import audio
from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import fft
from gnuradio import filter
from gnuradio import gr
from gnuradio.eng_option import eng_option
from gnuradio.fft import window
from gnuradio.filter import firdes
from grc_gnuradio import blks2 as grc_blks2
from optparse import OptionParser
import fcdproplus
import math

class SorDeRa_sdr(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "RX logic")

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 192000
        self.aud_rate = aud_rate = 11025
        self.st = st = 1
        self.sq = sq = -700
        self.rec = rec = 1
        self.mode = mode = 4
        self.laj_0 = laj_0 = -0.0034
        self.laj = laj = 0
        self.lai_0 = lai_0 = -0.0032
        self.lai = lai = 0
        self.freq = freq = 99500000
        self.dev = dev = 19000
        self.decimation = decimation = samp_rate/aud_rate
        self.bw = bw = 3200
        self.batswitch = batswitch = 0
        self.batido = batido = 2950
        self.VEC = VEC = 1280

        ##################################################
        # Blocks
        ##################################################
        self.probe_sq = blocks.probe_signal_f()
        self.low_pass_filter_0_1_0_0_0 = filter.fir_filter_fff(samp_rate/48000, firdes.low_pass(
        	1, samp_rate, 15000, 1000, firdes.WIN_HAMMING, 6.76))
        self.low_pass_filter_0_1 = filter.fir_filter_fff(samp_rate/48000, firdes.low_pass(
        	30, samp_rate, 15000, 1000, firdes.WIN_HAMMING, 6.76))
        self.low_pass_filter_0 = filter.fir_filter_ccf(decimation, firdes.low_pass(
        	1, samp_rate, bw, 1000, firdes.WIN_HAMMING, 6.76))
        self.fractional_resampler_xx_0 = filter.fractional_resampler_ff(0, (samp_rate/decimation)/48000.0)
        self.fft_vxx_0 = fft.fft_vcc(VEC, True, (window.blackmanharris(1024)), True, 1)
        self.fft_probe = blocks.probe_signal_vf(VEC)
        self.fcdproplus_fcdproplus_0 = fcdproplus.fcdproplus("",1)
        self.fcdproplus_fcdproplus_0.set_lna(1)
        self.fcdproplus_fcdproplus_0.set_mixer_gain(1)
        self.fcdproplus_fcdproplus_0.set_if_gain(2)
        self.fcdproplus_fcdproplus_0.set_freq_corr(7)
        self.fcdproplus_fcdproplus_0.set_freq(freq)
          
        self.dc_blocker_xx_0 = filter.dc_blocker_ff(64, True)
        self.blocks_wavfile_sink_0 = blocks.wavfile_sink("/tmp/CAPTURE.WAV", 1, aud_rate, 16)
        self.blocks_sub_xx_0 = blocks.sub_ff(1)
        self.blocks_stream_to_vector_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, VEC)
        self.blocks_multiply_xx_0_1_0 = blocks.multiply_vff(1)
        self.blocks_multiply_xx_0_0 = blocks.multiply_vff(1)
        self.blocks_multiply_xx_0 = blocks.multiply_vcc(1)
        self.blocks_multiply_const_vxx_0_0_0_0 = blocks.multiply_const_vff((1, ))
        self.blocks_multiply_const_vxx_0_0_0 = blocks.multiply_const_vff((1, ))
        self.blocks_multiply_const_vxx_0_0 = blocks.multiply_const_vcc((0.4, ))
        self.blocks_complex_to_real_0_0 = blocks.complex_to_real(1)
        self.blocks_complex_to_mag_squared_0 = blocks.complex_to_mag_squared(VEC)
        self.blocks_add_xx_0 = blocks.add_vff(1)
        self.blocks_add_const_vxx_0 = blocks.add_const_vcc((-complex(lai,laj), ))
        self.blks2_valve_0_0_1 = grc_blks2.valve(item_size=gr.sizeof_gr_complex*1, open=bool(mode!=4 and mode!=3))
        self.blks2_valve_0_0_0 = grc_blks2.valve(item_size=gr.sizeof_gr_complex*1, open=bool(0))
        self.blks2_valve_0 = grc_blks2.valve(item_size=gr.sizeof_float*1, open=bool(rec))
        self.blks2_selector_0_0_0 = grc_blks2.selector(
        	item_size=gr.sizeof_float*1,
        	num_inputs=2,
        	num_outputs=1,
        	input_index=batswitch,
        	output_index=0,
        )
        self.blks2_selector_0_0 = grc_blks2.selector(
        	item_size=gr.sizeof_float*1,
        	num_inputs=3,
        	num_outputs=1,
        	input_index=mode,
        	output_index=0,
        )
        self.blks2_selector_0 = grc_blks2.selector(
        	item_size=gr.sizeof_gr_complex*1,
        	num_inputs=1,
        	num_outputs=3,
        	input_index=0,
        	output_index=mode,
        )
        self.band_pass_filter_0_0_0 = filter.fir_filter_fff(1, firdes.band_pass(
        	100*(mode==4), samp_rate, 18500, 19500, 500, firdes.WIN_HAMMING, 6.76))
        self.band_pass_filter_0_0 = filter.fir_filter_fff(1, firdes.band_pass(
        	30, samp_rate, 23000, 53000, 1000, firdes.WIN_HAMMING, 6.76))
        self.audio_sink_0_0_0 = audio.sink(48000, "dmix:CARD=Pro,DEV=0", False)
        self.audio_sink_0 = audio.sink(48000, "dmix:CARD=Pro,DEV=0", False)
        self.analog_wfm_rcv_1 = analog.wfm_rcv(
        	quad_rate=samp_rate,
        	audio_decimation=1,
        )
        self.analog_sig_source_x_0_0 = analog.sig_source_f(samp_rate/decimation, analog.GR_COS_WAVE, 0, 1, 0)
        self.analog_sig_source_x_0 = analog.sig_source_c(samp_rate, analog.GR_COS_WAVE, dev, 1, 0)
        self.analog_quadrature_demod_cf_0 = analog.quadrature_demod_cf(0.25)
        self.analog_pwr_squelch_xx_0 = analog.pwr_squelch_cc(sq, 0.001, 0, False)
        self.analog_fm_deemph_0_0 = analog.fm_deemph(fs=48000, tau=50e-6)
        self.analog_fm_deemph_0 = analog.fm_deemph(fs=48000, tau=50e-6)
        self.analog_feedforward_agc_cc_0 = analog.feedforward_agc_cc(64, 0.9)
        self.analog_am_demod_cf_0 = analog.am_demod_cf(
        	channel_rate=samp_rate/decimation,
        	audio_decim=samp_rate/decimation/aud_rate,
        	audio_pass=bw,
        	audio_stop=bw+500,
        )
        self.analog_agc3_xx_0 = analog.agc3_cc(0.0001, 0.0001, 0.9, 0.1)
        self.analog_agc3_xx_0.set_max_gain(200)

        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_complex_to_mag_squared_0, 0), (self.fft_probe, 0))
        self.connect((self.fcdproplus_fcdproplus_0, 0), (self.blocks_add_const_vxx_0, 0))
        self.connect((self.blocks_add_const_vxx_0, 0), (self.blocks_stream_to_vector_0, 0))
        self.connect((self.blocks_complex_to_real_0_0, 0), (self.blks2_selector_0_0, 2))
        self.connect((self.blks2_selector_0, 2), (self.blocks_multiply_const_vxx_0_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0_0, 0), (self.blocks_complex_to_real_0_0, 0))
        self.connect((self.blks2_selector_0, 1), (self.analog_quadrature_demod_cf_0, 0))
        self.connect((self.analog_quadrature_demod_cf_0, 0), (self.blks2_selector_0_0, 1))
        self.connect((self.blks2_selector_0, 0), (self.analog_am_demod_cf_0, 0))
        self.connect((self.analog_am_demod_cf_0, 0), (self.blks2_selector_0_0, 0))
        self.connect((self.analog_sig_source_x_0_0, 0), (self.blocks_multiply_xx_0_0, 1))
        self.connect((self.blks2_selector_0_0, 0), (self.blocks_multiply_xx_0_0, 0))
        self.connect((self.blocks_multiply_xx_0_0, 0), (self.dc_blocker_xx_0, 0))
        self.connect((self.dc_blocker_xx_0, 0), (self.blks2_selector_0_0_0, 1))
        self.connect((self.blks2_selector_0_0, 0), (self.blks2_selector_0_0_0, 0))
        self.connect((self.analog_feedforward_agc_cc_0, 0), (self.blks2_selector_0, 0))
        self.connect((self.blks2_selector_0_0_0, 0), (self.blks2_valve_0, 0))
        self.connect((self.blks2_selector_0_0_0, 0), (self.probe_sq, 0))
        self.connect((self.analog_pwr_squelch_xx_0, 0), (self.analog_feedforward_agc_cc_0, 0))
        self.connect((self.low_pass_filter_0, 0), (self.analog_pwr_squelch_xx_0, 0))
        self.connect((self.analog_sig_source_x_0, 0), (self.blocks_multiply_xx_0, 1))
        self.connect((self.blks2_valve_0_0_0, 0), (self.blocks_multiply_xx_0, 0))
        self.connect((self.blocks_multiply_xx_0, 0), (self.low_pass_filter_0, 0))
        self.connect((self.blocks_stream_to_vector_0, 0), (self.fft_vxx_0, 0))
        self.connect((self.fft_vxx_0, 0), (self.blocks_complex_to_mag_squared_0, 0))
        self.connect((self.blks2_valve_0, 0), (self.blocks_wavfile_sink_0, 0))
        self.connect((self.fractional_resampler_xx_0, 0), (self.audio_sink_0, 0))
        self.connect((self.blks2_selector_0_0_0, 0), (self.fractional_resampler_xx_0, 0))
        self.connect((self.band_pass_filter_0_0, 0), (self.blocks_multiply_xx_0_1_0, 0))
        self.connect((self.band_pass_filter_0_0_0, 0), (self.blocks_multiply_xx_0_1_0, 1))
        self.connect((self.blocks_multiply_xx_0_1_0, 0), (self.low_pass_filter_0_1_0_0_0, 0))
        self.connect((self.band_pass_filter_0_0_0, 0), (self.blocks_multiply_xx_0_1_0, 2))
        self.connect((self.low_pass_filter_0_1, 0), (self.analog_fm_deemph_0, 0))
        self.connect((self.analog_fm_deemph_0, 0), (self.blocks_add_xx_0, 0))
        self.connect((self.analog_fm_deemph_0, 0), (self.blocks_sub_xx_0, 1))
        self.connect((self.analog_wfm_rcv_1, 0), (self.low_pass_filter_0_1, 0))
        self.connect((self.analog_wfm_rcv_1, 0), (self.band_pass_filter_0_0, 0))
        self.connect((self.analog_wfm_rcv_1, 0), (self.band_pass_filter_0_0_0, 0))
        self.connect((self.blocks_sub_xx_0, 0), (self.blocks_multiply_const_vxx_0_0_0_0, 0))
        self.connect((self.blocks_add_xx_0, 0), (self.blocks_multiply_const_vxx_0_0_0, 0))
        self.connect((self.analog_fm_deemph_0_0, 0), (self.blocks_sub_xx_0, 0))
        self.connect((self.analog_fm_deemph_0_0, 0), (self.blocks_add_xx_0, 1))
        self.connect((self.low_pass_filter_0_1_0_0_0, 0), (self.analog_fm_deemph_0_0, 0))
        self.connect((self.analog_agc3_xx_0, 0), (self.analog_wfm_rcv_1, 0))
        self.connect((self.blks2_valve_0_0_1, 0), (self.analog_agc3_xx_0, 0))
        self.connect((self.blocks_add_const_vxx_0, 0), (self.blks2_valve_0_0_1, 0))
        self.connect((self.blocks_add_const_vxx_0, 0), (self.blks2_valve_0_0_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0_0_0, 0), (self.audio_sink_0_0_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0_0_0_0, 0), (self.audio_sink_0_0_0, 1))


# QT sink close method reimplementation

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_decimation(self.samp_rate/self.aud_rate)
        self.analog_sig_source_x_0_0.set_sampling_freq(self.samp_rate/self.decimation)
        self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.samp_rate, self.bw, 1000, firdes.WIN_HAMMING, 6.76))
        self.analog_sig_source_x_0.set_sampling_freq(self.samp_rate)
        self.fractional_resampler_xx_0.set_resamp_ratio((self.samp_rate/self.decimation)/48000.0)
        self.band_pass_filter_0_0.set_taps(firdes.band_pass(30, self.samp_rate, 23000, 53000, 1000, firdes.WIN_HAMMING, 6.76))
        self.low_pass_filter_0_1_0_0_0.set_taps(firdes.low_pass(1, self.samp_rate, 15000, 1000, firdes.WIN_HAMMING, 6.76))
        self.low_pass_filter_0_1.set_taps(firdes.low_pass(30, self.samp_rate, 15000, 1000, firdes.WIN_HAMMING, 6.76))
        self.band_pass_filter_0_0_0.set_taps(firdes.band_pass(100*(self.mode==4), self.samp_rate, 18500, 19500, 500, firdes.WIN_HAMMING, 6.76))

    def get_aud_rate(self):
        return self.aud_rate

    def set_aud_rate(self, aud_rate):
        self.aud_rate = aud_rate
        self.set_decimation(self.samp_rate/self.aud_rate)

    def get_st(self):
        return self.st

    def set_st(self, st):
        self.st = st

    def get_sq(self):
        return self.sq

    def set_sq(self, sq):
        self.sq = sq
        self.analog_pwr_squelch_xx_0.set_threshold(self.sq)

    def get_rec(self):
        return self.rec

    def set_rec(self, rec):
        self.rec = rec
        self.blks2_valve_0.set_open(bool(self.rec))

    def get_mode(self):
        return self.mode

    def set_mode(self, mode):
        self.mode = mode
        self.blks2_selector_0_0.set_input_index(int(self.mode))
        self.blks2_selector_0.set_output_index(int(self.mode))
        self.blks2_valve_0_0_1.set_open(bool(self.mode!=4 and self.mode!=3))
        self.band_pass_filter_0_0_0.set_taps(firdes.band_pass(100*(self.mode==4), self.samp_rate, 18500, 19500, 500, firdes.WIN_HAMMING, 6.76))

    def get_laj_0(self):
        return self.laj_0

    def set_laj_0(self, laj_0):
        self.laj_0 = laj_0

    def get_laj(self):
        return self.laj

    def set_laj(self, laj):
        self.laj = laj
        self.blocks_add_const_vxx_0.set_k((-complex(self.lai,self.laj), ))

    def get_lai_0(self):
        return self.lai_0

    def set_lai_0(self, lai_0):
        self.lai_0 = lai_0

    def get_lai(self):
        return self.lai

    def set_lai(self, lai):
        self.lai = lai
        self.blocks_add_const_vxx_0.set_k((-complex(self.lai,self.laj), ))

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self.fcdproplus_fcdproplus_0.set_freq(self.freq)

    def get_dev(self):
        return self.dev

    def set_dev(self, dev):
        self.dev = dev
        self.analog_sig_source_x_0.set_frequency(self.dev)

    def get_decimation(self):
        return self.decimation

    def set_decimation(self, decimation):
        self.decimation = decimation
        self.analog_sig_source_x_0_0.set_sampling_freq(self.samp_rate/self.decimation)
        self.fractional_resampler_xx_0.set_resamp_ratio((self.samp_rate/self.decimation)/48000.0)

    def get_bw(self):
        return self.bw

    def set_bw(self, bw):
        self.bw = bw
        self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.samp_rate, self.bw, 1000, firdes.WIN_HAMMING, 6.76))

    def get_batswitch(self):
        return self.batswitch

    def set_batswitch(self, batswitch):
        self.batswitch = batswitch
        self.blks2_selector_0_0_0.set_input_index(int(self.batswitch))

    def get_batido(self):
        return self.batido

    def set_batido(self, batido):
        self.batido = batido

    def get_VEC(self):
        return self.VEC

    def set_VEC(self, VEC):
        self.VEC = VEC

if __name__ == '__main__':
    parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
    (options, args) = parser.parse_args()
    tb = SorDeRa_sdr()
    tb.start()
    tb.wait()

