#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: RX logic
# Author: Ismas
# Description: A sensible SDR receiver
# Generated: Sun Feb 21 03:30:26 2016
##################################################

from gnuradio import analog
from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import fft
from gnuradio import filter
from gnuradio import gr
from gnuradio.eng_option import eng_option
from gnuradio.fft import window
from gnuradio.filter import firdes
from gnuradio.wxgui import forms
from grc_gnuradio import blks2 as grc_blks2
from grc_gnuradio import wxgui as grc_wxgui
from optparse import OptionParser
import fcdproplus
import math
import wx

class SorDeRa_sdr(grc_wxgui.top_block_gui):

    def __init__(self):
        grc_wxgui.top_block_gui.__init__(self, title="RX logic")
        _icon_path = "/usr/share/icons/hicolor/32x32/apps/gnuradio-grc.png"
        self.SetIcon(wx.Icon(_icon_path, wx.BITMAP_TYPE_ANY))

        ##################################################
        # Variables
        ##################################################
        self.sq = sq = -70
        self.samp_rate = samp_rate = 192000
        self.rec = rec = 1
        self.freq = freq = 130850000+20000
        self.dev = dev = 19000
        self.decimation = decimation = 20
        self.bw = bw = 3200
        self.batido = batido = 0
        self.amfm = amfm = 0
        self.VEC = VEC = 1280

        ##################################################
        # Blocks
        ##################################################
        _sq_sizer = wx.BoxSizer(wx.VERTICAL)
        self._sq_text_box = forms.text_box(
        	parent=self.GetWin(),
        	sizer=_sq_sizer,
        	value=self.sq,
        	callback=self.set_sq,
        	label="sq",
        	converter=forms.float_converter(),
        	proportion=0,
        )
        self._sq_slider = forms.slider(
        	parent=self.GetWin(),
        	sizer=_sq_sizer,
        	value=self.sq,
        	callback=self.set_sq,
        	minimum=-100,
        	maximum=0,
        	num_steps=100,
        	style=wx.SL_HORIZONTAL,
        	cast=float,
        	proportion=1,
        )
        self.Add(_sq_sizer)
        self.low_pass_filter_0 = filter.fir_filter_ccf(decimation, firdes.low_pass(
        	1, samp_rate, bw, 1000, firdes.WIN_HAMMING, 6.76))
        self.fft_vxx_0 = fft.fft_vcc(VEC, True, (window.blackmanharris(1024)), True, 1)
        self.fcdproplus_fcdproplus_0 = fcdproplus.fcdproplus("",1)
        self.fcdproplus_fcdproplus_0.set_lna(1)
        self.fcdproplus_fcdproplus_0.set_mixer_gain(1)
        self.fcdproplus_fcdproplus_0.set_if_gain(2)
        self.fcdproplus_fcdproplus_0.set_freq_corr(7)
        self.fcdproplus_fcdproplus_0.set_freq(freq)
          
        self.dc_blocker_xx_0 = filter.dc_blocker_ff(64, True)
        self.blocks_wavfile_sink_0 = blocks.wavfile_sink("/tmp/CAPTURE.WAV", 1, samp_rate/decimation, 16)
        self.blocks_vector_to_stream_0 = blocks.vector_to_stream(gr.sizeof_float*1, VEC)
        self.blocks_udp_sink_0_0 = blocks.udp_sink(gr.sizeof_float*1, "127.0.0.1", 42421, VEC*4, False)
        self.blocks_udp_sink_0 = blocks.udp_sink(gr.sizeof_float*1, "127.0.0.1", 42420, 1472, True)
        self.blocks_stream_to_vector_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, VEC)
        self.blocks_rms_xx_0 = blocks.rms_cf(1)
        self.blocks_multiply_xx_0_0 = blocks.multiply_vff(1)
        self.blocks_multiply_xx_0 = blocks.multiply_vcc(1)
        self.blocks_complex_to_mag_squared_0 = blocks.complex_to_mag_squared(VEC)
        self.blks2_valve_0 = grc_blks2.valve(item_size=gr.sizeof_float*1, open=bool(rec))
        self.blks2_selector_0_0 = grc_blks2.selector(
        	item_size=gr.sizeof_float*1,
        	num_inputs=2,
        	num_outputs=1,
        	input_index=amfm,
        	output_index=0,
        )
        self.blks2_selector_0 = grc_blks2.selector(
        	item_size=gr.sizeof_gr_complex*1,
        	num_inputs=1,
        	num_outputs=2,
        	input_index=0,
        	output_index=amfm,
        )
        self.band_pass_filter_0 = filter.fir_filter_fff(1, firdes.band_pass(
        	4, samp_rate/decimation, 50, bw, bw+1000, firdes.WIN_HAMMING, 6.76))
        self.analog_sig_source_x_0_0 = analog.sig_source_f(samp_rate/decimation, analog.GR_COS_WAVE, batido, 0.5, 0)
        self.analog_sig_source_x_0 = analog.sig_source_c(samp_rate, analog.GR_COS_WAVE, dev, 1, 0)
        self.analog_quadrature_demod_cf_0 = analog.quadrature_demod_cf(0.25)
        self.analog_pwr_squelch_xx_0 = analog.pwr_squelch_cc(sq, 0.05, 0, True)
        self.analog_feedforward_agc_cc_0 = analog.feedforward_agc_cc(64, 1)

        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_sig_source_x_0, 0), (self.blocks_multiply_xx_0, 1))
        self.connect((self.blocks_multiply_xx_0, 0), (self.low_pass_filter_0, 0))
        self.connect((self.blocks_multiply_xx_0_0, 0), (self.dc_blocker_xx_0, 0))
        self.connect((self.analog_feedforward_agc_cc_0, 0), (self.blks2_selector_0, 0))
        self.connect((self.analog_sig_source_x_0_0, 0), (self.blocks_multiply_xx_0_0, 1))
        self.connect((self.dc_blocker_xx_0, 0), (self.band_pass_filter_0, 0))
        self.connect((self.blks2_selector_0_0, 0), (self.blocks_multiply_xx_0_0, 0))
        self.connect((self.low_pass_filter_0, 0), (self.analog_pwr_squelch_xx_0, 0))
        self.connect((self.analog_pwr_squelch_xx_0, 0), (self.analog_feedforward_agc_cc_0, 0))
        self.connect((self.band_pass_filter_0, 0), (self.blks2_valve_0, 0))
        self.connect((self.blks2_valve_0, 0), (self.blocks_wavfile_sink_0, 0))
        self.connect((self.blks2_selector_0, 0), (self.analog_quadrature_demod_cf_0, 0))
        self.connect((self.analog_quadrature_demod_cf_0, 0), (self.blks2_selector_0_0, 0))
        self.connect((self.blks2_selector_0, 1), (self.blocks_rms_xx_0, 0))
        self.connect((self.blocks_rms_xx_0, 0), (self.blks2_selector_0_0, 1))
        self.connect((self.blocks_stream_to_vector_0, 0), (self.fft_vxx_0, 0))
        self.connect((self.fft_vxx_0, 0), (self.blocks_complex_to_mag_squared_0, 0))
        self.connect((self.band_pass_filter_0, 0), (self.blocks_udp_sink_0, 0))
        self.connect((self.blocks_complex_to_mag_squared_0, 0), (self.blocks_vector_to_stream_0, 0))
        self.connect((self.blocks_vector_to_stream_0, 0), (self.blocks_udp_sink_0_0, 0))
        self.connect((self.fcdproplus_fcdproplus_0, 0), (self.blocks_multiply_xx_0, 0))
        self.connect((self.fcdproplus_fcdproplus_0, 0), (self.blocks_stream_to_vector_0, 0))


# QT sink close method reimplementation

    def get_sq(self):
        return self.sq

    def set_sq(self, sq):
        self.sq = sq
        self.analog_pwr_squelch_xx_0.set_threshold(self.sq)
        self._sq_slider.set_value(self.sq)
        self._sq_text_box.set_value(self.sq)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.analog_sig_source_x_0.set_sampling_freq(self.samp_rate)
        self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.samp_rate, self.bw, 1000, firdes.WIN_HAMMING, 6.76))
        self.analog_sig_source_x_0_0.set_sampling_freq(self.samp_rate/self.decimation)
        self.band_pass_filter_0.set_taps(firdes.band_pass(4, self.samp_rate/self.decimation, 50, self.bw, self.bw+1000, firdes.WIN_HAMMING, 6.76))

    def get_rec(self):
        return self.rec

    def set_rec(self, rec):
        self.rec = rec
        self.blks2_valve_0.set_open(bool(self.rec))

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
        self.band_pass_filter_0.set_taps(firdes.band_pass(4, self.samp_rate/self.decimation, 50, self.bw, self.bw+1000, firdes.WIN_HAMMING, 6.76))

    def get_bw(self):
        return self.bw

    def set_bw(self, bw):
        self.bw = bw
        self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.samp_rate, self.bw, 1000, firdes.WIN_HAMMING, 6.76))
        self.band_pass_filter_0.set_taps(firdes.band_pass(4, self.samp_rate/self.decimation, 50, self.bw, self.bw+1000, firdes.WIN_HAMMING, 6.76))

    def get_batido(self):
        return self.batido

    def set_batido(self, batido):
        self.batido = batido
        self.analog_sig_source_x_0_0.set_frequency(self.batido)

    def get_amfm(self):
        return self.amfm

    def set_amfm(self, amfm):
        self.amfm = amfm
        self.blks2_selector_0.set_output_index(int(self.amfm))
        self.blks2_selector_0_0.set_input_index(int(self.amfm))

    def get_VEC(self):
        return self.VEC

    def set_VEC(self, VEC):
        self.VEC = VEC

if __name__ == '__main__':
    parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
    (options, args) = parser.parse_args()
    tb = SorDeRa_sdr()
    tb.Start(True)
    tb.Wait()

