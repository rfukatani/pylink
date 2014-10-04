#!C:\Python27\python.exe

#from numpy import sin, cos, pi, linspace, real
#from math import sin, cos, pi
import numpy as np
from numpy.random import randn
from scipy import signal
from matplotlib.pyplot import plot, legend, show, hold, grid, figure, savefig
import os.path

## TODO:
##    WRITE LOG

debug = False

class time_depend_func:
    def __init__(self,init_val):
        self.current_val = init_val
    def val_t(self,t):
        print("!!!This method should be overridden!!!")
        exit(1)


class sig(time_depend_func):
    def val_t(self,t):
        return np.sin(t)*100
        #return (sin(2 * pi * 0.75 * t*(1-t) + 2.1) + 0.1*sin(2 * pi * 1.25 * t + 1) + 0.18*cos(2 * pi * 3.85 * t))

class sig_sawtooth(time_depend_func):
    def val_t(self,t):
        return signal.sawtooth(t)*100

class noise(time_depend_func):
    def val_t(self,t):
        #return randn(len(t)) * 0.1
        return np.sin(200*t) * 10

class delta_sigma_modulator:
    def __init__(self):
        self.integ1 = 0
        self.integ2 = 0
        self.out = 0
    def get_next_state(self,input_ad):
        temp1 = input_ad + self.integ1 - self.out
        temp2 = temp1 + self.integ2 - self.out
        self.integ1 = temp1
        self.integ2 = temp2

        if temp2 > 0:
            self.out = 1
        else:
            self.out = -1

        return self.out

class sinc_filter:
    def __init__(self):
        self.integ1 = 0
        self.integ2 = 0
        self.integ3 = 0
        self.dif1 = 0
        self.dif2 = 0
        self.dif3 = 0
        self.decim = 0
        self.count = 0

    def get_next_state(self,output_ad):
        if output_ad == 1:
            self.integ1 = 1
        else:
            self.integ1 = -1
        self.integ2 += self.integ1
        self.integ3 += self.integ2

        if self.count == 15:
            self.dif3 = self.integ3 - self.dif1 - self.dif2
            self.dif2 = self.integ3 - self.dif1
            self.dif1 = self.integ3
            self.count = 0
        else:
            self.count += 1

class time_driven_simulator:

    def __init__(self, time_step=1, divide_num=1):

#initialize internal variable
        self.time_step = time_step
        self.divide_num = divide_num
        self.dt = float(time_step) / divide_num
        self.current_time = 0
        self.sig = 0.0
        self.noise = 0.0

        if time_step <= 0:
            print("time step should be larger than zero.")
            exit(1)
        elif divide_num <= 0:
            print("time step should be larger than zero.")
            exit(1)

#initialize system elements
        self.sig_h = sig(0)
        self.noise_h = noise(0)
        self.filter1_b,self.filter1_a = signal.butter(1, 1, 'low', analog=True)
        self.dsm = delta_sigma_modulator()
        self.sinc = sinc_filter()

#initialize monitor
        self.inmonitor = data_monitor("in")
        self.monitor = data_monitor("out",False)
        self.dsmonitor = data_monitor("dsout",False)
        self.sincmonitor = data_monitor("sinc")
        self.rtlsincmonitor = data_monitor("rtl_sinc")

    def set_condition(self,time_step,divide_num):
        self.time_step = time_step
        self.divide_num = divide_num
        self.dt = float(time_step) / divide_num
        if debug:
            print("time_step:"+str(self.time_step))
            print("diveide_num:"+str(self.time_step))

    def get_next_state(self,rtl_result):
        #ex. divide_num=2 and time_step = 1
        #    t_in = [0,0.5,1]
        t_in = np.linspace(self.current_time, self.current_time + self.time_step, self.divide_num + 1)
        if debug:
            print(t_in)

        sig_t = self.sig_h.val_t(t_in)
        noise_t = self.noise_h.val_t(t_in)

#need initial condition(last_result)
        _, out_t = signal.dlsim5((self.filter1_b,self.filter1_a,self.dt),\
                    sig_t+noise_t,t_in,self.sig_h.current_val)

        self.dsm.get_next_state(out_t[-1])
        self.sinc.get_next_state(self.dsm.out)

#log data
        self.inmonitor.add_new_data(self.current_time+self.time_step,sig_t[-1]+noise_t[-1])
        self.monitor.add_new_data(self.current_time+self.time_step,out_t[-1])
        self.dsmonitor.add_new_data(self.current_time+self.time_step,self.dsm.out)
        self.sincmonitor.add_new_data(self.current_time+self.time_step,self.sinc.dif3)

        #cation! time = current_time
        self.rtlsincmonitor.add_new_data(self.current_time,rtl_result)

#step end process
        self.current_time += self.time_step

        if debug:
            print("sig: "+str(sig_t[-1])+"@python")
            print("noise: "+str(sig_t[-1])+"@python")
            print("dt: "+str(self.dt)+"@python")
            print("filter_b: "+str(self.filter1_b)+"@python")
            print("return to: "+str(out_t[-1])+"@python")
        return self.dsm.out

    def sim_end(self):
        self.monitor.display_graph()


class data_monitor:
    def __init__(self,signal_name,log_enable = True):
        self.log_enable = log_enable
        if log_enable:
            if not os.path.isdir("data"):
                os.mkdir("data")
                print("data directory is maded @python.")

            self.signal_name = signal_name
            self.log_file = open("data/"+self.signal_name+".log","w")
        else:
            pass

    def add_new_data(self,time,data):
        if self.log_enable:
            self.log_file.write(str(time)+","+str(np.real(data)).strip(" []")+"\n")
    def display_graph(self):
        if not self.log_enable:
            return
        if not self.log_file.closed:
            self.log_file.close()

        t,y = get_data_from_logfile("data/"+self.signal_name+".log")


        plot(t, y, 'k',color = 'r', linewidth=1.75)
        legend((self.signal_name),
            loc='best')
        hold(False)
        grid(True)
	if debug:
            print("display graph")
        show()
    pass

def get_data_from_logfile(log_file):
    t=[]
    y=[]
    log_file = open(log_file,"r")

    for line in log_file:
        new_t,new_y = line.rstrip().split(',')

        t.append(float(new_t))
        y.append(float(new_y))

    log_file.close()
    return t,y


#should be execute by c++
def main():
    simulator = time_driven_simulator(time_step=0.002,divide_num=8)
    simulator.set_condition(0.002,8)
    for step in range(5000):
        simulator.get_next_state(0)
    #simulator.sim_end()


if __name__ == '__main__':
    main()
