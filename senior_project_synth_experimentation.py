# -*- coding: utf-8 -*-
"""Senior project synth experimentation.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1WkX1bCA8DIA04mORhQAEk-rQ9wN4YSP6
"""

# Commented out IPython magic to ensure Python compatibility.

#%% libraries
import numpy as np
import math
from itertools import repeat
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, CheckButtons
import sounddevice as sd
#from matplotlib import rc

#%% bitreverse and fft
def bitreverse(bitsize, num):
  num = bin(num) #convert to binary
  rev = num[-1:1:-1] #reverse
  rev += (bitsize-len(rev))*'0' #add zeros to make it the right length
  return (int(rev,2))

def fft(x): 
  n = len(x)
  bit = int(math.log(n, 2))
 # if (math.log(n,2)).is_integer() == False:  #Check if length of sample is a power of 2
 #   print('Using first ', 2**bit, ' samples...') #if not, round down to a power of 2
  length = 2**bit
  order = np.arange(length)
  order = np.array(list(map(bitreverse,repeat(bit),order))) #reverse bits in the order
  xhat = np.zeros(length)
  for i in np.arange(length):
    xhat[i] = x[order[i]] #rearrange x to match bit reversed order
 
  omega = np.exp(-1j*2*np.pi/n) #calculate each omega

  for i in np.arange(bit): #LOGBASE(2, N)
    xp = np.full(length, 0j) #fill with 0j so it doesnt cast new values to int from imaginary 
    inc = 2**i #distance between p and q
    oinc = int(length/2/inc) #increment for exponent of omega
    for j in np.arange(oinc):
      start = 2*j*(inc) #each group of butterflies
      o = 0 #always starts with 0
      for k in np.arange(inc):
        p = xhat[start + k]
        q = xhat[start + k + inc]
        xp[start + k] = p + q*(omega**o) #butterfly p+alpha*q
        xp[start + k + inc] = p - q*(omega**o) #butterfly p-alpha*q
        o += oinc
    xhat = xp
  return xhat

#%% tone
def tone(t, base, rats, baseampl, decay = 0):
  y = 0
  for i in np.arange(len(rats)):
     if rats[i] != 0:
        y += rats[i]*np.sin((t+i/(base+1))*(i+1)*base*2*np.pi)*baseampl #add harmonics
  if decay:
    y=y*(np.log(t + 0.02) - 1) #add logarithmic decay
  return y

#%% plot fft
def plotfft(ys, n):
  N = 2**n
  xhat = fft(ys[:N])
  magxhat = np.abs(xhat)
  n= np.arange(N)
  freq = n*44100/N
  plt.xlim((0,3000))
  plt.stem(freq, magxhat, use_line_collection=True)
  plt.show()
  return n, magxhat
  
def plotffta(ys, ax):
  xhat = fft(ys)
  magxhat = np.abs(xhat)
  N = len(magxhat)
  n = np.arange(N)
  freq = n*44100/N
  ax.set_xlim((0,3000))
  ax.scatter(freq, magxhat)#, use_line_collection=True)

  # ax.set_xlim(0,5000)
  # #return 
  # ax.stem(freq, magxhat, use_line_collection=True)

#%%
seconds = 2
rats = np.array((1, .8, .75, .45, .5, .2))
#rats = np.array((1, 0.0000001))
xs = np.linspace(0, seconds, int(seconds*44100))
ys = tone(xs, 880, rats, 50)
y2s = tone(xs, 220, rats, 50)


#%% Audio test
#plt.xlim(0,.16)
plt.plot(xs,ys)


plt.xlim(0,.02)
plt.plot(xs,y2s)

n = 7
N = 2**n
xhat = fft(ys[:N])

magxhat = np.abs(xhat)

n= np.arange(N)
freq = n*(seconds*44100)/N

yp = ys-y2s

print(yp[:7])

#%% fft test
#plotfft(y2s, 10)
plotfft(ys, 10)

#plotfft(y2s, 9)
#plotfft(ys, 9)

#plotfft(ys, 5)
#plotfft(ys, 10)
#plotfft(ys,15)
#plotfft(ys, 20)


#%% Dynamic Sound Class
"""# Animated plot"""

class DynamicSound:
    ##################
    # default values #
    ##################
    freq = 660
    sample_rate = 44100
    rats = [1,0,0,0] #single frequency tone
    state = False #false = off, true = on
    
    #create a stream
    def __init__(self):
       self.outs = sd.OutputStream(samplerate=self.sample_rate, blocksize = 44100, callback=self.streamup, latency = 'low')
       #self.outs.start()
       
    def set_freq(self, new):
        self.freq = new
    
    # set ratios
    def set_rats(self, new):
        self.rats = new
        
    def get_freq(self):
        return self.freq
    
    def get_samplerate(self):
        return self.sample_rate
    
    # update the stream
    def streamup(self, outdata, frames, time, status):
        for i in range(frames):
            outdata[i] = tone(i/self.sample_rate, self.freq, self.rats, 10)
        return 
    
    # set stream state to true
    def start(self):
        self.outs.start()
        self.state = True
    
    # set stream state to false
    def stop(self):
        self.outs.stop() 
        #self.outs.close()
        self.state = False
        return
    
    # start or stop stream. called by the button widget
    def toggle(self, label):
        if self.state:
            self.stop()
        else:
            self.start()
    
    pass
#%% Notes
#discrete values for slider

notes = [440,     # A4
         466.16,  # A#4
         493.88,  # B4
         523.25,  # C5
         554.37,  # C#5
         587.33,  # D5
         622.25,  # D#5
         659.25,  # E5
         698.46,  # F5
         739.99,  # F#5
         783.99,  # G5
         830.61,  # G#5
         880]     # A5


harmonics = [[  0,  0,  0,  0],
             [ .2,  0,  0,  0],
             [ .3, .1,  0,  0],
             [ .4, .2, .1,  0],
             [ .6, .4, .2, .1],
             [ .7, .5, .3, .2],
             [ .7, .6, .5, .5],
             [ .7, .7, .7, .6],
             [.7,.7,.7,.7,.6,.5,.4,.3,.2,.1]] # this line is specifically to demonstrate that
                                              # you can hear the fundamental even when it isn't
                                              # there

#%%

rows = 3
#rows = 2

# =============================================================================
# rc('animation', html = 'jshtml')
# plt.rcParams["figure.figsize"] = [7.50, 3.50]
# plt.rcParams["figure.autolayout"] = True
# =============================================================================
fig, ax = plt.subplots(rows,2, gridspec_kw={'height_ratios':[8,1,1]})

xsize = 0.02
xlen = int(.02*44100)

line1, = ax[0][0].plot(np.linspace(0,xsize,xlen),np.zeros(int(xlen)))
# print(int(xlen))

stemax = ax[0][1]
line2, = stemax.plot(np.linspace(0, 5000, 500), np.zeros(500))
#stemax.stem(np.linspace(0, 3000, 300), np.zeros(300))
stemax.set_ylim([0,20000])
    
ax[0][0].set_xlim([0, xsize])
ax[0][0].set_ylim([-3.5, 3.5])

freqax = ax[1][0]
freq = Slider(freqax, 'Freq', valmin = 440, valmax = 880, valinit = notes[1], 
              valstep = notes)

soundax = ax[1][1]
soundbutton = CheckButtons(soundax, ['Sound'], [True])
sound = DynamicSound()


harmonics1 = Slider(ax[2][0], 'Fundamental', valmin=0, valmax=1, valinit = 1)
harmonics2 = Slider(ax[2][1], 'First Harmonic', valmin=0, valmax=len(harmonics)-1, valinit = 0, valstep = np.arange(len(harmonics)))
# harmonics3 = Slider(ax[3][0], 'Second Harmonic', valmin=0, valmax=1, valinit = 0)
# harmonics4 = Slider(ax[3][1], 'Third Harmonic', valmin=0, valmax=1, valinit = 0)


# def init():
#   line1.set_data([],[])
#   sound.start()
#    return line1,

def update(i):
    h = harmonics2.val
    if h == 8:
        rats = np.array([harmonics1.val,  harmonics[h][0], 
                         harmonics[h][1], harmonics[h][2], 
                         harmonics[h][3], harmonics[h][4],
                         harmonics[h][5], harmonics[h][6],
                         harmonics[h][7], harmonics[h][8], 
                         harmonics[h][9]])
    else:
        rats = np.array([harmonics1.val,  harmonics[h][0], 
                     harmonics[h][1], harmonics[h][2], 
                     harmonics[h][3]])
    sound.set_rats(rats)
    
    x = np.linspace(0, 1, 44100)
    y = tone(x, freq.val, rats, baseampl=1, decay = 0)
    
    xhat = np.fft.fft(y)
    #xhat = fft(y)
    magxhat = np.abs(xhat)
    N = len(xhat)
    n = np.arange(N)
    frequ = n*44100/N
    line2.set_data(frequ, magxhat)
    
    line1.set_data(x[:xlen], y[:xlen])
    
    sound.set_freq(freq.val)
    return line1, line2,

soundbutton.on_clicked(sound.toggle)
freq.on_changed(update)
harmonics1.on_changed(update) # fundamental frequency
harmonics2.on_changed(update) # array of ratios for remaining harmonics

#animator = ani.FuncAnimation(fig, update, init_func = init, frames = 10, 
#                            interval = 50, blit = True)
                                                                        
plt.show()