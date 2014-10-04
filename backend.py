
#	Copyright (C) 2014 Ryosuke Fukatani All Rights Reserved
#	
#    This file is part of pylink.
#
#    pylink is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 2 of the License, or
#    (at your option) any later version.
#
#    pylink is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with pylink.  If not, see <http://www.gnu.org/licenses/>.


import numpy as np
import os
from scipy import signal
from matplotlib.pyplot import plot, legend, show, hold, grid, figure, savefig, xlim

def display_graph(standardization = 0):
    signal_names = []
    for dpath, dnames, fnames in os.walk("./data/"):
        for fname in fnames:
            if fname.endswith(".log"):
                signal_names.append(fname.replace(".log",""))

    print(signal_names)

    colors = ('r','b','g','r','b','g','r','b','g')

    i=0
    figure()
    for sn in signal_names:
        t,y = get_data_from_logfile("data/"+sn+".log",standardization)
        plot(t, y, 'k',color = colors[i], linewidth=1.75)
        i+=1
    legend((signal_names), loc='best')
    hold(False)
    grid(True)


def get_data_from_logfile(log_file,standardization = 0):
    t=[]
    y=[]
    log_file = open(log_file,"r")

    for line in log_file:
        new_t,new_y = line.rstrip().split(',')

        t.append(float(new_t))
        y.append(float(new_y))

    log_file.close()
    if standardization:
        if np.max(y) != 0:
            y = y/np.max(y)
    return t,y

def main():
    display_graph(1)
    get_corr()
    pass

def get_corr():
    t,out_t = get_data_from_logfile("data/in.log",1)
    _,sinc_t = get_data_from_logfile("data/rtl_sinc.log",1)

    t2 = np.linspace(-np.max(t),np.max(t),len(t) * 2 - 1)
    cor = signal.correlate(out_t,sinc_t)

    log_file = open("data/cor.txt","w")
    i=0
    for c in cor:
        log_file.write(str(t2[i])+","+str(c)+"\n")
        i+=1

    #peakind = signal.find_peaks_cwt(cor,np.arange(1,2))

    figure()
    plot(t2, cor, 'k',color = 'b', linewidth=1.75)
    xlim(-4,4)
    legend("cross correlation", loc='best')
    hold(False)
    grid(True)
    show()

if __name__ == '__main__':
    main()
