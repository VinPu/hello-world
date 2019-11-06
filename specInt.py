# -*- coding: utf-8 -*-
"""
Created on Wed Sep 18 22:36:09 2019

@author: CPU
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os, glob
from matplotlib.ticker import AutoMinorLocator




#Prompt user for directory input
folder = input('Please enter directory of the folder containing the dat files:')
os.chdir(folder)
folderDF = pd.DataFrame()

ImAList = []
IntList = []


for file in glob.glob('*.txt'):
    
    I_mA = float(file[-7:-4])
    
    
    
    df = pd.read_csv(file, sep = '\t', skiprows = 12, header = None, names = ['Lambda', 'Irrad'])
    
    Lambda = np.array(df['Lambda'])
    Irrad = np.array(df['Irrad'])
    
    #Clean data
    Irrad[Lambda > 700] = 0
    Irrad[Irrad < 0] = 0
    
    
    #Trapezium
    trapBase = np.diff(Lambda)
    
    irradMovAv = np.convolve(Irrad,[1,1]) / 2.
    trapHeight = irradMovAv[1:-1]
    
    intensity = np.dot(trapBase,trapHeight)
    
    #Collect results
    ImAList.append(I_mA)
    IntList.append(intensity)

#Plot 
peakInt = max(IntList)
normIntList = [i / peakInt for i in IntList]

fig = plt.figure(1)
ax = fig.add_subplot(111)

ax.plot(ImAList,normIntList,'x')

ax.xaxis.set_minor_locator(AutoMinorLocator(5))
ax.yaxis.set_minor_locator(AutoMinorLocator(5))

ax.tick_params(which='both', direction='in')
ax.grid(b=True,which='both',linestyle='-.',linewidth=.5)
ax.set_title('Linearity test - Intensity v.s. Current')
ax.set_xlabel('Current/mA')
ax.set_ylabel('Normalized intensity')


fig.savefig('IntVsCurrent',dpi=300)





    
    
    
    
    
    
    