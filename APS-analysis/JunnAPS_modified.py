# -*- coding: utf-8 -*-
"""
Created on Thu Nov 22 17:57:04 2018

@author: cp2515
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os, glob
import sys
#from Module_auto import auto
#from Module_manual import manual
np.set_printoptions(threshold=np.nan)




#prompt user to choose mode of program
Quick = False
Auto = False
Manual = False

while True:
    mode = input('Enter: \n 1 for Manual \n 2 for Auto \n 3 for Quick \n 4 to Exit \n -->')
    if mode == '1':
        Quick = False
        Auto = False
        Manual = True
        break
    elif mode == '2':
        Quick = False
        Auto = True
        Manual = False
        break
    elif mode == '3':
        Quick = True
        Auto = False
        Manual = False
        break
    elif mode == '4':
        sys.exit('Programme ended')
    else:
        continue
  
#execute quick mode
if Quick == True:
    
    #Prompt user for directory input
    folder = input('Please enter directory of the folder containing the dat files:')
    os.chdir(folder)
    filenumber=0
    folderDF = pd.DataFrame()
    baselineList = []
    colors = ['r-','b-','g-','c-','m-','y-']
    
    #looping through all dat files in folder
    for file in glob.glob('*.dat'):
        txt = ""
        
    
        #reads csv file for data points which smooth data gives a real value
        df = pd.read_csv(file)
        df = df[pd.notnull(df[' Smooth'])]
        df = df.sort_values(by=[' Energy (eV)'], ascending=True)
        df.reset_index(drop=True, inplace=True)
        
        #prints header for all data contained in csv file
        #print (list(df.columns.values))
                
        #extract normalized smooth data and energy from csv file
        #smooth = df[' Smooth']
        smooth = df[' CUBE RT(PE)']
        energies = df[' Energy (eV)'] 
        #smooth = smooth/max(smooth)    
                      
        #create new file to store analyzed data
        folderDF = pd.concat((folderDF, energies.rename('%s_ENERGY'%(file.rstrip('.dat')) )), axis=1)
        folderDF['%s_DATA'%(file.rstrip('.dat'))] = pd.Series(smooth)
        
        
        
        #calculating derivatives, median and mean from extracted data
        firstderivatives = np.gradient(smooth)
        secondderivatives = np.gradient(firstderivatives)
        datamean = np.mean(smooth) 
        energymean = np.mean(energies)
        datamedian = (max(smooth) + min(smooth))/2
        energymedian = (max(energies) + min(energies))/2
        datarange = (max(smooth) - min(smooth))
        energyrange = (max(energies) - min(energies))
        
        
        '''
        Chenfeng
        '''
        #check oscillation to find signal rise point
        oscillation = np.sign(np.diff(smooth))
        for i in range(len(smooth)):
            if int( sum(oscillation[i:i+20]) ) == 20:
                RiseIdx = i
                break
            else: 
                continue
        #find baseline 
        baseline = np.mean(smooth[:RiseIdx])
        baselineList.append(baseline)
        #search linear segement
        linearMat = np.array([[0,0,0]])
        for i in np.arange(RiseIdx,len(smooth)-20):
            for d in np.arange(10,21):
                x = np.nanstd(firstderivatives[i:i+d])
                linearMat = np.concatenate( (linearMat,[[i,i+d,x]]) )
        linearMat = linearMat[1:,:]
        linearMat = linearMat[linearMat[:,2].argsort()]
        
        idx = np.argmax(linearMat[:10,0])
        fitStartIdx = int(linearMat[idx,0])
        fitEndIdx = int(linearMat[idx,1])
        
        fitenergy = np.array(energies)[fitStartIdx:fitEndIdx]
        fitdata = np.array(smooth)[fitStartIdx:fitEndIdx]

                                
        #linear fitting based on region with most 2nd diff=0
        z = np.polyfit(x=fitenergy, y=fitdata, deg=1)
        p = np.poly1d(z)
        txtp = str(p).strip()
        df['trendline'] = p(energies)
        trendline = df['trendline'] 
        txt += ('\n Trendline: y= %s' %(txtp))
        txt += ('\n Baseline = %.3g' %(baseline))
    
        
        #define range of integration for larger area
        baseintersect = np.argwhere(np.diff(np.sign(smooth - baseline)) != 0).reshape(-1)
        trendintersect = np.argwhere(np.diff(np.sign(smooth - trendline)) != 0).reshape(-1)
        integratebegin = max(baseintersect)
        integrateend = min(trendintersect)
        integratebase = np.maximum(baseline,trendline)
        integratedata = smooth[(energies[integratebegin]<=energies) & (energies<=energies[integrateend])]
        integrateenergy = energies[(energies[integratebegin]<=energies) & (energies<=energies[integrateend])]
        
        #for smaller area
        basetrendintersect = np.argwhere(np.diff(np.sign(trendline - baseline)) != 0).reshape(-1)
        #subdata = smooth[(energies[basetrendintersect].squeeze()<=energies) & (energies<=energies[integrateend])]
        subdata = trendline[(energies[basetrendintersect].squeeze()<=energies) & (energies<=energies[integrateend])]
        subenergy = energies[(energies[basetrendintersect].squeeze()<=energies) & (energies<=energies[integrateend])]
        
        #integrating area
        #areabig = np.trapz(integratedata,integrateenergy)
        areabig = np.trapz(integratedata-baseline,integrateenergy)
        #areasmall = np.trapz(subdata,subenergy)
        areasmall = np.trapz(subdata-baseline,subenergy)
        area = areabig - areasmall
        
        if area > 0:
#            txt += ("\n total area = %s" %(areabig))
#            txt += ("\n subtracted area = %s" %(areasmall))
#            txt += ("\n useful area =%s" %(area))
            txt += ("\n Area = %.3g" %(area))
        else:
            txt += ("\n NO AREA FORMED")
        
        #finding WF
        txt += ('\n WF/HOMO/VBE = %.4g'%(energies[basetrendintersect].squeeze()))
        
        #plotting data with baseline and linear fit
        plt.figure(filenumber)
        plt.figure(filenumber).canvas.set_window_title(file.rstrip('.dat'))
        plt.title(file.rstrip('.dat'))
        plt.text(min(energies), max(smooth), txt, ha='left', va='top')
        plt.xlabel('Energy /eV')
        plt.ylabel('Smooth')
        plt.grid(True)
        plt.plot(energies,smooth,colors[filenumber])
        plt.plot(energies,trendline)
        plt.hlines(y=baseline, xmin=min(energies), xmax=max(energies), color='black')
    #    plt.hlines(y=cap, xmin=min(energies), xmax=max(energies), color='black')
        plt.xlim((min(energies)-(energyrange/20),max(energies)+(energyrange/20)))
        plt.ylim((min(smooth)-(datarange/20),max(smooth)+(datarange/20)))
        plt.fill_between(energies, smooth, integratebase, where=((energies[integratebegin]<=energies) & (energies<=energies[integrateend])), alpha = 0.5)
        plt.plot(energies[integratebegin], smooth[integratebegin], 'ro', markersize=5)
        plt.plot(energies[integrateend], smooth[integrateend], 'ro', markersize=5)
        plt.plot(energies[basetrendintersect], baseline, 'yo', markersize=5)
        plt.savefig('%s.png' %(file.rstrip('.dat')),dpi=300)
        
        #save file storing analyzed data
        folderDF['%s_Trendline' %(file.rstrip('.dat'))] = pd.Series(trendline)
        folderDF['%s_Parameters' %(file.rstrip('.dat'))] = pd.Series(['Baseline = %.3g' %(baseline), 'Tendline: y = %s Data' %(txtp), 'Area = %s' %(area), 'WF/HOMO/VBE = %s' %(energies[basetrendintersect].squeeze())])
        
        filenumber = filenumber + 1

    #plot all APS data in one graph
    plt.figure(filenumber + 1)
    plt.figure(filenumber + 1).canvas.set_window_title('%s_plot' %(os.path.basename(folder)))
    plt.title(os.path.basename(folder))
    plt.xlabel('Energy/eV')
    plt.ylabel('APS data baselined')
    for i in range(filenumber):
        plt.plot(folderDF.iloc[:,i*4], folderDF.iloc[:,i*4+1]-baselineList[i], colors[i], label = list(folderDF)[i*4+1])
        plt.legend(loc = 'upper left')
    plt.savefig('%s_Plot' %(os.path.basename(folder)), dpi=300)
        
        
    
    
    
    folderDF.to_csv('%s_analyzed_data.csv' %(os.path.basename(folder)), sep=',')
    #signalling the end of the program
    print('Programme ended')    

#executing auto mode    
elif Auto == True:
    
    #Prompt user for directory input
    folder = input('Please enter folder directory:')
    while True:
        setting = input('Enter 1 to analyze one file or 2 to analyze all:')
        if setting == '2':
            os.chdir(folder)
            #looping through all dat files in folder
            for file in glob.glob('*.dat'):
                auto(file)
            break
        elif setting == '1':
            os.chdir(folder)
            file = input('Enter name of file:')
            auto(file)
            break
        else:
            continue
        
    #signalling the end of the program
    print('Programme ended')  
    
#executing manual mode        
elif Manual == True:
    
    #Prompt user for directory input
    folder = input('Please enter folder directory:')
    while True:
        setting = input('Enter 1 to analyze one file or 2 to analyze all:')
        if setting == '2':
            os.chdir(folder)
            #looping through all dat files in folder
            for file in glob.glob('*.dat'):
                manual(file)
            break
        elif setting == '1':
            os.chdir(folder)
            file = input('Enter name of file:')
            manual(file)
            break
        else:
            continue
    
    #signalling the end of the program
    print('Programme ended')     
