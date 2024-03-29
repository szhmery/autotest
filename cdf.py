#! /usr/bin/python
"""
###############################################################################
##
## Confidential Information Access Agreement (NDA).                          ##
## For internal use only; do not distribute.                                 ##
##                                                                           ##
###############################################################################
"""
import gc
import sys
import time
import matplotlib
from scipy.interpolate import make_interp_spline, BSpline
from matplotlib.ticker import FormatStrFormatter

# C++ antigrain rendering engine backend for nice PNGs
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import math
import os.path

import numpy as np
from numpy import ma
from matplotlib import scale as mscale
from matplotlib import transforms as mtransforms
from matplotlib.ticker import FixedFormatter, FixedLocator

from matplotlib import rcParams

# BUG: this example fails with any other setting of axisbelow
# This makes sure the ylabel could be shown
rcParams['axes.axisbelow'] = False


class CloseToOne(mscale.ScaleBase):
    name = 'close_to_one'

    def __init__(self, axis, **kwargs):
        mscale.ScaleBase.__init__(self)
        self.nines = kwargs.get('nines', 3)

    def get_transform(self):
        return self.Transform(self.nines)

    def set_default_locators_and_formatters(self, axis):
        axis.set_major_locator(FixedLocator(
            np.array([1 - 10 ** (-k) for k in range(1 + self.nines)])))
        axis.set_major_formatter(FixedFormatter(
            [str(1 - 10 ** (-k)) for k in range(1 + self.nines)]))

    def limit_range_for_scale(self, vmin, vmax, minpos):
        return vmin, min(1 - 10 ** (-self.nines), vmax)

    class Transform(mtransforms.Transform):
        input_dims = 1
        output_dims = 1
        is_separable = True

        def __init__(self, nines):
            mtransforms.Transform.__init__(self)
            self.nines = nines

        def transform_non_affine(self, a):
            masked = ma.masked_where(a > 1 - 10 ** (-1 - self.nines), a)
            if masked.mask.any():
                return -ma.log10(1 - a)
            else:
                return -np.log10(1 - a)

        def inverted(self):
            return CloseToOne.InvertedTransform(self.nines)

    class InvertedTransform(mtransforms.Transform):
        input_dims = 1
        output_dims = 1
        is_separable = True

        def __init__(self, nines):
            mtransforms.Transform.__init__(self)
            self.nines = nines

        def transform_non_affine(self, a):
            return 1. - 10 ** (-a)

        def inverted(self):
            return CloseToOne.Transform(self.nines)


mscale.register_scale(CloseToOne)


# Argument checking
# Expected arguments are

class Statistic():
    def draw_pdf_plot(self, latencyFileName, is_enable):
        xval, yval = [], []
        n_bins = 100
        i = 0
        if (os.path.isfile(str(latencyFileName))):
            with open(str(latencyFileName)) as f:
                for line in f:
                    delay_sample = line.split()[0:1]
                    # print delay_sample
                    latency = float(delay_sample[0]) / 1000
                    xval.append(i)
                    yval.append(latency)
                    i += 1
            if yval != []:
                latency_max = "Max:" + str(np.amax(yval)) + " ms\n"
                latency_ave = "Ave:" + str(round(np.average(yval), 3)) + " ms\n"
                latency_min = "Min:" + str(round(np.amin(yval), 3)) + " ms"
                if is_enable == 1:
                    labelString = "BWR Enabled \n" + latency_max + latency_ave + latency_min
                else:
                    labelString = "BWR Disabled \n" + latency_max + latency_ave + latency_min
                # Avoid visual effect of the CDF returning to y=0
                # histtype=step returns a single patch, open polygon
                n, bins, patches = plt.hist(yval, n_bins, normed=True, cumulative=False, label=labelString,
                                            histtype='bar')

            f.close()
        else:
            print("%s not found" % latencyFileName)

    def draw_pdf(self, enableLatencyFileName, disableLatencyFileName, title, latencyPlotName):

        self.draw_pdf_plot(disableLatencyFileName, 0)
        self.draw_pdf_plot(enableLatencyFileName, 1)

        plt.xlabel('Latency (ms) ')
        plt.ylabel('Count')
        plt.title(title, size=9)
        plt.legend(frameon=True, loc='center right', fontsize=9)

        print "save file : " + latencyPlotName
        plt.savefig(latencyPlotName, format='pdf')
        plt.close()

    def draw_cdf_plot(self, latencyFileName, is_enable):
        xval, yval = [], []
        n_bins = 1000
        xpercent, ypercent = [], []
        i = 0
        if (os.path.isfile(str(latencyFileName))):
            with open(str(latencyFileName)) as f:
                for line in f:
                    delay_sample = line.split()[0:1]
                    # print delay_sample
                    latency = float(delay_sample[0]) / 1000
                    xval.append(i)
                    yval.append(latency)
                    i += 1
            if yval != []:
                ###for more smooth
                xval_a = np.asarray(xval)
                yval_a = np.asarray(yval)
                xval_new = np.linspace(xval_a.min(), xval_a.max(), 10000)

                spl = make_interp_spline(xval_a, yval_a, k=3)  # BSpline object
                yval_new = spl(xval_new)

                latency_90 = "90%tile: " + str(round(np.percentile(yval_a, 90), 2)) + " ms\n"
                latency_50 = "50%tile: " + str(round(np.percentile(yval_a, 50), 2)) + " ms\n"
                latency_10 = "10%tile: " + str(round(np.percentile(yval_a, 10), 2)) + " ms"

                if is_enable == 1:
                    labelString = "BWR Enabled \n" + latency_90 + latency_50 + latency_10
                    print "BWR Enabled:"
                else:
                    labelString = "BWR Disabled \n" + latency_90 + latency_50 + latency_10
                    print "BWR Disabled:"
                print "10%:" + str(round(np.percentile(yval_a, 10), 2))
                print "20%:" + str(round(np.percentile(yval_a, 20), 2))
                print "50%:" + str(round(np.percentile(yval_a, 50), 2))
                print "70%:" + str(round(np.percentile(yval_a, 70), 2))
                print "90%:" + str(round(np.percentile(yval_a, 90), 2))
                print "95%:" + str(round(np.percentile(yval_a, 95), 2))
                print "99%:" + str(round(np.percentile(yval_a, 99), 2))

                # Avoid visual effect of the CDF returning to y=0
                # histtype=step returns a single patch, open polygon
                n, bins, patches = plt.hist(yval_new, n_bins, density=True, cumulative=True, label=labelString,
                                            histtype='step')
                # delete the last point
                patches[0].set_xy(patches[0].get_xy()[:-1])
            f.close()
        else:
            print("%s not found" % latencyFileName)

    def draw_cdf(self, enableLatencyFileName, disableLatencyFileName, title, latencyPlotName, type):
        # axis_name = fig.add_subplot(subplotNumber)
        self.draw_cdf_plot(disableLatencyFileName, 0)
        self.draw_cdf_plot(enableLatencyFileName, 1)

        plt.grid(True)
        plt.grid(b=True, which='minor', color='r', linestyle='-', alpha=0.2)

        ax = plt.gca()
        if type=="log":
            plt.yscale('close_to_one')

            # plt.yscale('log')

        # ax.grid(b=True, which='minor', linestyle='-',axis="y")
        plt.minorticks_on()
        minor_ticks = np.arange(0, 1, 0.05)
        ax.set_yticks(minor_ticks, minor=True)
        # ax.yaxis.get_ticklocs(minor=True)
        # plt.grid(which='minor', linestyle=':', linewidth='0.5', color='black')
        # plt.grid(b=True, which='minor', color='r', linestyle='--')
        plt.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)
        plt.xlabel('Latency (ms) ')
        plt.title(title, size=9)
        plt.ylabel("Percentile")

        plt.legend(frameon=True, loc='center right', fontsize=9)
        plt.show()

        print "save file : " + latencyPlotName
        plt.savefig(latencyPlotName, format='pdf')
        # plt.close()


    def draw_multiple_subplots(self,type):
        fig = plt.figure(figsize=(12, 10))
        plt.subplot(2, 2, 1)

        # case 1, 101_102
        disable_mbwr_file = '/root/zhaohsun/cdf/disable_mbwr_ping_500_005_0713_101_2.txt'
        enable_mbwr_file = '/root/zhaohsun/cdf/enable_mbwr_ping_500_005_0717_912_102.txt'
        # Statistic().draw_pdf(enable_mbwr_file, disable_mbwr_file,
        #                      "US Latency w/ and w/o BWR under no Traffic Load",
        #                      "/root/zhaohsun/autotest/pdf/mbwr_pdf_101_102.pdf")
        Statistic().draw_cdf(enable_mbwr_file, disable_mbwr_file,
                             "US Latency w/ and w/o BWR under no Traffic Load",
                             "/root/zhaohsun/autotest/"+type+"/"+type+"_mbwr_cdf_101_102.pdf",type)

        plt.subplot(2, 2, 2)
        # case 2, 201_202
        disable_mbwr_file = '/root/zhaohsun/cdf/disable_mbwr_ping_500_005_0714_927_201.txt'
        enable_mbwr_file = '/root/zhaohsun/cdf/enable_mbwr_ping_500_005_0714_927_202.txt'
        # Statistic().draw_pdf(enable_mbwr_file, disable_mbwr_file,
        #                      "US Latency w/ and w/o BWR under Low Traffic Load (20%)",
        #                      "/root/zhaohsun/autotest/pdf/mbwr_pdf_201_202.pdf")
        Statistic().draw_cdf(enable_mbwr_file, disable_mbwr_file,
                             "US Latency w/ and w/o BWR under Low Traffic Load (20%)",
                             "/root/zhaohsun/autotest/"+type+"/"+type+"_mbwr_cdf_201_202.pdf",type)
        plt.subplot(2, 2, 3)
        # case 3, 301_302
        disable_mbwr_file = '/root/zhaohsun/cdf/disable_mbwr_ping_500_005_0714_927_301.txt'
        enable_mbwr_file = '/root/zhaohsun/cdf/enable_mbwr_ping_500_005_0717_927_302_3.txt'
        # Statistic().draw_pdf(enable_mbwr_file, disable_mbwr_file,
        #                      "US Latency w/ and w/o BWR under Medium Traffic Load (40%) w/o REQ Contention",
        #                      "/root/zhaohsun/autotest/pdf/mbwr_pdf_301_302.pdf")
        Statistic().draw_cdf(enable_mbwr_file, disable_mbwr_file,
                             "US Latency w/ and w/o BWR under Medium Traffic Load (40%) w/o REQ Contention",
                             "/root/zhaohsun/autotest/"+type+"/"+type+"_mbwr_cdf_301_302.pdf",type)
        plt.subplot(2, 2, 4)

        # case 5, 401_402
        disable_mbwr_file = '/root/zhaohsun/cdf/disable_mbwr_ping_500_005_0714_927_401.txt'
        enable_mbwr_file = '/root/zhaohsun/cdf/enable_mbwr_ping_500_005_0714_927_402.txt'
        # Statistic().draw_pdf(enable_mbwr_file, disable_mbwr_file,
        #                      "US Latency under High Traffic Load (70%) w/o REQ Contention",
        #                      "/root/zhaohsun/autotest/pdf/mbwr_pdf_401_402.pdf")
        Statistic().draw_cdf(enable_mbwr_file, disable_mbwr_file,
                             "US Latency under High Traffic Load (70%) w/o REQ Contention",
                             "/root/zhaohsun/autotest/"+type+"/"+type+"_mbwr_cdf_401_402.pdf",type)
        fig.tight_layout()
        print "save all of plots to rate-multipleplots.pdf"
        fig.savefig("/root/zhaohsun/autotest/"+type+"/"+type+"_rate_multipleplots.pdf")

        fig2 = plt.figure(figsize=(12, 10))
        plt.subplot(2, 2, 1)
        # case 3, 301_302
        disable_mbwr_file = '/root/zhaohsun/cdf/disable_mbwr_ping_500_005_0714_927_301.txt'
        enable_mbwr_file = '/root/zhaohsun/cdf/enable_mbwr_ping_500_005_0717_927_302_3.txt'
        # Statistic().draw_pdf(enable_mbwr_file, disable_mbwr_file,
        #                      "US Latency w/ and w/o BWR under Medium Traffic Load (40%) w/o REQ Contention",
        #                      "/root/zhaohsun/autotest/pdf/mbwr_pdf_301_302.pdf")
        Statistic().draw_cdf(enable_mbwr_file, disable_mbwr_file,
                             "US Latency w/ and w/o BWR under Medium Traffic Load (40%) w/o REQ Contention",
                             "/root/zhaohsun/autotest/"+type+"/"+type+"_mbwr_cdf_301_302.pdf",type)

        plt.subplot(2, 2, 2)
        # case 4, 303_304
        disable_mbwr_file = '/root/zhaohsun/cdf/disable_mbwr_ping_500_005_0717_927_303.txt'
        enable_mbwr_file = '/root/zhaohsun/cdf/enable_mbwr_ping_500_005_0717_927_304_1.txt'
        # Statistic().draw_pdf(enable_mbwr_file, disable_mbwr_file,
        #                      "US Latency w/ and w/o BWR under Medium Traffic Load (40%) w/ REQ Contention",
        #                      "/root/zhaohsun/autotest/pdf/mbwr_pdf_303_304.pdf")
        Statistic().draw_cdf(enable_mbwr_file, disable_mbwr_file,
                             "US Latency w/ and w/o BWR under Medium Traffic Load (40%) w/ REQ Contention",
                             "/root/zhaohsun/autotest/"+type+"/"+type+"_mbwr_cdf_303_304.pdf",type)
        plt.subplot(2, 2, 3)
        # case 5, 401_402
        disable_mbwr_file = '/root/zhaohsun/cdf/disable_mbwr_ping_500_005_0714_927_401.txt'
        enable_mbwr_file = '/root/zhaohsun/cdf/enable_mbwr_ping_500_005_0714_927_402.txt'
        # Statistic().draw_pdf(enable_mbwr_file, disable_mbwr_file,
        #                      "US Latency under High Traffic Load (70%) w/o REQ Contention",
        #                      "/root/zhaohsun/autotest/pdf/mbwr_pdf_401_402.pdf")
        Statistic().draw_cdf(enable_mbwr_file, disable_mbwr_file,
                             "US Latency under High Traffic Load (70%) w/o REQ Contention",
                             "/root/zhaohsun/autotest/"+type+"/"+type+"_mbwr_cdf_401_402.pdf",type)
        plt.subplot(2, 2, 4)
        # case 6, 403_404
        disable_mbwr_file = '/root/zhaohsun/cdf/disable_mbwr_ping_500_005_0715_927_403.txt'
        enable_mbwr_file = '/root/zhaohsun/cdf/enable_mbwr_ping_500_005_0715_927_404.txt'
        # Statistic().draw_pdf(enable_mbwr_file, disable_mbwr_file,
        #                      "US Latency under High Traffic Load (70%) with REQ Contention",
        #                      "/root/zhaohsun/autotest/pdf/mbwr_pdf_403_404.pdf")
        Statistic().draw_cdf(enable_mbwr_file, disable_mbwr_file,
                             "US Latency under High Traffic Load (70%) with REQ Contention",
                             "/root/zhaohsun/autotest/"+type+"/"+type+"_mbwr_cdf_403_404.pdf",type)

        fig2.tight_layout()
        print "save all of plots to contetion-multipleplots.pdf"
        fig2.savefig("/root/zhaohsun/autotest/"+type+"/"+type+"_contetion_multipleplots.pdf")

        fig3 = plt.figure(figsize=(12, 10))
        plt.subplot(2, 2, 1)
        # case 5, 401_402
        disable_mbwr_file = '/root/zhaohsun/cdf/disable_mbwr_ping_500_005_0714_927_401.txt'
        enable_mbwr_file = '/root/zhaohsun/cdf/enable_mbwr_ping_500_005_0714_927_402.txt'
        # Statistic().draw_pdf(enable_mbwr_file, disable_mbwr_file,
        #                      "US Latency under High Traffic Load (70%) w/o REQ Contention",
        #                      "/root/zhaohsun/autotest/pdf/mbwr_pdf_401_402.pdf")
        Statistic().draw_cdf(enable_mbwr_file, disable_mbwr_file,
                             "US Latency under High Traffic Load (70%) w/o REQ Contention",
                             "/root/zhaohsun/autotest/"+type+"/"+type+"_mbwr_cdf_401_402.pdf",type)

        plt.subplot(2, 2, 2)
        # case 6, 403_404
        disable_mbwr_file = '/root/zhaohsun/cdf/disable_mbwr_ping_500_005_0715_927_403.txt'
        enable_mbwr_file = '/root/zhaohsun/cdf/enable_mbwr_ping_500_005_0715_927_404.txt'
        # Statistic().draw_pdf(enable_mbwr_file, disable_mbwr_file,
        #                      "US Latency under High Traffic Load (70%) with REQ Contention",
        #                      "/root/zhaohsun/autotest/pdf/mbwr_pdf_403_404.pdf")
        Statistic().draw_cdf(enable_mbwr_file, disable_mbwr_file,
                             "US Latency under High Traffic Load (70%) with REQ Contention",
                             "/root/zhaohsun/autotest/"+type+"/"+type+"_mbwr_cdf_403_404.pdf",type)

        plt.subplot(2, 2, 3)
        # case 7, 405_406
        disable_mbwr_file = '/root/zhaohsun/cdf/disable_mbwr_high_qos_ping_500_005_0718_927_405.txt'
        enable_mbwr_file = '/root/zhaohsun/cdf/enable_mbwr_high_qos_ping_500_005_0718_927_406.txt'
        # Statistic().draw_pdf(enable_mbwr_file, disable_mbwr_file,
        #                      "High Priority US Latency under High Traffic Load (70%) w/o REQ Contention",
        #                      "/root/zhaohsun/autotest/pdf/mbwr_pdf_405_406.pdf")
        Statistic().draw_cdf(enable_mbwr_file, disable_mbwr_file,
                             "High Priority US Latency under High Traffic Load (70%) w/o REQ Contention",
                             "/root/zhaohsun/autotest/"+type+"/"+type+"_mbwr_cdf_405_406.pdf",type)

        plt.subplot(2, 2, 4)
        # case 8, 407_408
        disable_mbwr_file = '/root/zhaohsun/cdf/disable_mbwr_high_qos_ping_500_005_0718_927_407.txt'
        enable_mbwr_file = '/root/zhaohsun/cdf/enable_mbwr_high_qos_ping_500_005_0718_927_408.txt'
        # Statistic().draw_pdf(enable_mbwr_file, disable_mbwr_file,
        #                      "High Priority US Latency under High Traffic Load (70%) with REQ Contention",
        #                      "/root/zhaohsun/autotest/pdf/mbwr_pdf_407_408.pdf")
        Statistic().draw_cdf(enable_mbwr_file, disable_mbwr_file,
                             "High Priority US Latency under High Traffic Load (70%) with REQ Contention",
                             "/root/zhaohsun/autotest/"+type+"/"+type+"_mbwr_cdf_407_408.pdf",type)
        fig3.tight_layout()
        print "save all of plots to priority-multipleplots.pdf"
        fig3.savefig("/root/zhaohsun/autotest/"+type+"/"+type+"_priority_multipleplots.pdf")

    def draw_seperate_plots(self,type):
        # case 1, 101_102
        disable_mbwr_file = '/root/zhaohsun/cdf/disable_mbwr_ping_500_005_0713_101_2.txt'
        enable_mbwr_file = '/root/zhaohsun/cdf/enable_mbwr_ping_500_005_0717_912_102.txt'
        Statistic().draw_pdf(enable_mbwr_file, disable_mbwr_file,
                             "US Latency w/ and w/o BWR under no Traffic Load",
                             "/root/zhaohsun/autotest/pdf/mbwr_pdf_101_102.pdf")
        Statistic().draw_cdf(enable_mbwr_file, disable_mbwr_file,
                             "US Latency w/ and w/o BWR under no Traffic Load",
                             "/root/zhaohsun/autotest/"+type+"/"+type+"_mbwr_cdf_101_102.pdf", type)

        # case 2, 201_202
        disable_mbwr_file = '/root/zhaohsun/cdf/disable_mbwr_ping_500_005_0714_927_201.txt'
        enable_mbwr_file = '/root/zhaohsun/cdf/enable_mbwr_ping_500_005_0714_927_202.txt'
        Statistic().draw_pdf(enable_mbwr_file, disable_mbwr_file,
                             "US Latency w/ and w/o BWR under Low Traffic Load (20%)",
                             "/root/zhaohsun/autotest/pdf/mbwr_pdf_201_202.pdf")
        Statistic().draw_cdf(enable_mbwr_file, disable_mbwr_file,
                             "US Latency w/ and w/o BWR under Low Traffic Load (20%)",
                             "/root/zhaohsun/autotest/"+type+"/"+type+"_mbwr_cdf_201_202.pdf", type)

        # case 3, 301_302
        disable_mbwr_file = '/root/zhaohsun/cdf/disable_mbwr_ping_500_005_0714_927_301.txt'
        enable_mbwr_file = '/root/zhaohsun/cdf/enable_mbwr_ping_500_005_0717_927_302_3.txt'
        Statistic().draw_pdf(enable_mbwr_file, disable_mbwr_file,
                             "US Latency w/ and w/o BWR under Medium Traffic Load (40%) w/o REQ Contention",
                             "/root/zhaohsun/autotest/pdf/mbwr_pdf_301_302.pdf")
        Statistic().draw_cdf(enable_mbwr_file, disable_mbwr_file,
                             "US Latency w/ and w/o BWR under Medium Traffic Load (40%) w/o REQ Contention",
                             "/root/zhaohsun/autotest/"+type+"/"+type+"_mbwr_cdf_301_302.pdf", type)

        # case 4, 303_304
        disable_mbwr_file = '/root/zhaohsun/cdf/disable_mbwr_ping_500_005_0717_927_303.txt'
        enable_mbwr_file = '/root/zhaohsun/cdf/enable_mbwr_ping_500_005_0717_927_304_1.txt'
        Statistic().draw_pdf(enable_mbwr_file, disable_mbwr_file,
                             "US Latency w/ and w/o BWR under Medium Traffic Load (40%) w/ REQ Contention",
                             "/root/zhaohsun/autotest/pdf/mbwr_pdf_303_304.pdf")
        Statistic().draw_cdf(enable_mbwr_file, disable_mbwr_file,
                             "US Latency w/ and w/o BWR under Medium Traffic Load (40%) w/ REQ Contention",
                             "/root/zhaohsun/autotest/"+type+"/"+type+"_mbwr_cdf_303_304.pdf", type)

        # case 5, 401_402
        disable_mbwr_file = '/root/zhaohsun/cdf/disable_mbwr_ping_500_005_0714_927_401.txt'
        enable_mbwr_file = '/root/zhaohsun/cdf/enable_mbwr_ping_500_005_0714_927_402.txt'
        Statistic().draw_pdf(enable_mbwr_file, disable_mbwr_file,
                             "US Latency under High Traffic Load (70%) w/o REQ Contention",
                             "/root/zhaohsun/autotest/pdf/mbwr_pdf_401_402.pdf")
        Statistic().draw_cdf(enable_mbwr_file, disable_mbwr_file,
                             "US Latency under High Traffic Load (70%) w/o REQ Contention",
                             "/root/zhaohsun/autotest/"+type+"/"+type+"_mbwr_cdf_401_402.pdf", type)

        # case 6, 403_404
        disable_mbwr_file = '/root/zhaohsun/cdf/disable_mbwr_ping_500_005_0715_927_403.txt'
        enable_mbwr_file = '/root/zhaohsun/cdf/enable_mbwr_ping_500_005_0715_927_404.txt'
        Statistic().draw_pdf(enable_mbwr_file, disable_mbwr_file,
                             "US Latency under High Traffic Load (70%) with REQ Contention",
                             "/root/zhaohsun/autotest/pdf/mbwr_pdf_403_404.pdf")
        Statistic().draw_cdf(enable_mbwr_file, disable_mbwr_file,
                             "US Latency under High Traffic Load (70%) with REQ Contention",
                             "/root/zhaohsun/autotest/"+type+"/"+type+"_mbwr_cdf_403_404.pdf", type)

        # case 7, 405_406
        disable_mbwr_file = '/root/zhaohsun/cdf/disable_mbwr_high_qos_ping_500_005_0718_927_405.txt'
        enable_mbwr_file = '/root/zhaohsun/cdf/enable_mbwr_high_qos_ping_500_005_0718_927_406.txt'
        Statistic().draw_pdf(enable_mbwr_file, disable_mbwr_file,
                             "High Priority US Latency under High Traffic Load (70%) w/o REQ Contention",
                             "/root/zhaohsun/autotest/pdf/mbwr_pdf_405_406.pdf")
        Statistic().draw_cdf(enable_mbwr_file, disable_mbwr_file,
                             "High Priority US Latency under High Traffic Load (70%) w/o REQ Contention",
                             "/root/zhaohsun/autotest/"+type+"/"+type+"_mbwr_cdf_405_406.pdf", type)

        # case 8, 407_408
        disable_mbwr_file = '/root/zhaohsun/cdf/disable_mbwr_high_qos_ping_500_005_0718_927_407.txt'
        enable_mbwr_file = '/root/zhaohsun/cdf/enable_mbwr_high_qos_ping_500_005_0718_927_408.txt'
        Statistic().draw_pdf(enable_mbwr_file, disable_mbwr_file,
                             "High Priority US Latency under High Traffic Load (70%) with REQ Contention",
                             "/root/zhaohsun/autotest/pdf/mbwr_pdf_407_408.pdf")
        Statistic().draw_cdf(enable_mbwr_file, disable_mbwr_file,
                             "High Priority US Latency under High Traffic Load (70%) with REQ Contention",
                             "/root/zhaohsun/autotest/"+type+"/"+type+"_mbwr_cdf_407_408.pdf", type)

        print "Draw seperate plots successfully!"
        
if __name__ == "__main__":

    Statistic().draw_seperate_plots("log")
    Statistic().draw_seperate_plots("linear")
    # Statistic().draw_multiple_subplots("log")
    # Statistic().draw_multiple_subplots("linear")