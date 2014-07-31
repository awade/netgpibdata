# This module provides data access to SR785 analyzer

import re
import sys
import math
import time
import pdb
import netgpib
import termstatus

def getdata(gpibObj, dataFile, paramFile):
    """
    Get data from SR785 and save it to a file.
    """
    # Get number of displays
    gpibObj.command("OUTX0")
    time.sleep(0.1)
    numOfDisp=int(gpibObj.query("DFMT?",100))
    if numOfDisp == 3:
       numOfDisp=1        
    numOfDisp = numOfDisp + 1
    
    data=[]
    freq=[]
    for disp in range(numOfDisp): #Loop for displays
        print('Downloading data from display #'+str(disp))

        (f,d)=downloadData(gpibObj, disp)
        freq.append(f)
        data.append(d)
            
    #Check the measurement group
    isSpectra=not int(gpibObj.query('MGRP?'+str(disp),100)) #True if it is FFT measurement
    
    if isSpectra:  #If FFT group
        for disp in range(numOfDisp):
            dataFile.write('#Display #'+str(disp+1)+' length= '+str(len(freq[disp]))+'\n')

            for j in range(len(freq[disp])):
                dataFile.write(freq[disp][j])
                dataFile.write(' '+data[disp][j]+'\n')
        
    else:  #Else
    #Write to the data file
        print('Writing data into the data file ...\n')
    
        for i in range(len(freq[0])):
            dataFile.write(freq[0][i])
            for disp in range(numOfDisp):
                dataFile.write(' '+data[disp][i])
            dataFile.write('\n')

def downloadData(gpibObj, disp):
    #Get the number of points on the Display 
    numPoint = int(gpibObj.query('DSPN?'+str(disp),100))

    freq=[]
    data=[]
    accomplished=0
    print 'Reading data'
    progressInfo=termstatus.statusTxt('0%')
    for bin in range(numPoint): #Loop for frequency bins
        percent = int(math.floor(100*bin/numPoint))
        if (percent - accomplished) >= 1 and percent < 100:
            progressInfo.update(str(percent)+'%')
            accomplished = percent
            pass

        f=gpibObj.query("DBIN?"+str(disp)+","+str(bin),100)
        f=f[:-1] #Chop new line character
        d=gpibObj.query("DSPY?"+str(disp)+","+str(bin),100)
        d=d[:-1] #Chop new line character
        freq.append(f)
        data.append(d)
        
    progressInfo.end('100%')
    time.sleep(1)

    #print 'Getting data values'
    #gpibObj.setDebugMode(1)
    #d=gpibObj.query("DSPY?"+str(disp),1024,0.1)
    #data=re.findall(r'[-+.eE0-9]+',d)
    #gpibObj.setDebugMode(0)

    return (freq,data)

def getparam(gpibObj, paramFile):
    #Get measurement parameters
    
    print('Reading instrument parameters')
        
    #Get the display format
    numOfDisp=int(gpibObj.query("DFMT?"))
    if numOfDisp == 3:
        numOfDisp=1
    numOfDisp = numOfDisp + 1

    #Get display parameters for each display
    measGrp=[]
    measurement=[]
    view=[]
    unit=[]

    time.sleep(0.1)

    for disp in range(numOfDisp):
        i=int(gpibObj.query("MGRP?"+str(disp)))
        measGrp.append({0: 'FFT' , 
                         1: 'Correlation', 
                         2: 'Octave', 
                         3: 'Swept Sine', 
                         4: 'Order', 
                         5: 'Time/Histogram'}[i])

    #Get measurement
        i=int(gpibObj.query("MEAS?"+str(disp)))
        measurement.append(
        {0: 'FFT 1',
         1: 'FFT 2',
         2: 'Power Spectrum 1',
         3: 'Power Spectrum 2',
         4: 'Time 1',
         5: 'Time 2',
         6: 'Windowed Time 1',
         7: 'Windowed Time 2',
         8: 'Orbit',
         9: 'Coherence',
         10: 'Cross Spectrum',
         11: 'Frequency Response',
         12: 'Capture Buffer 1',
         13: 'Capture Buffer 2',
         14: 'FFT User Function 1',
         15: 'FFT User Function 2',
         16: 'FFT User Function 3',
         17: 'FFT User Function 4',
         18: 'FFT User Function 5',
         19: 'Auto Correlation 1',
         20: 'Auto Correlation 2',
         21: 'Cross Correlation',
         22: 'Time 1',
         23: 'Time 2',
         24: 'Windowed Time 1',
         25: 'Windowed Time 2',
         26: 'Capture Buffer 1',
         27: 'Capture Buffer 2',
         28: 'Correlation Function 1',
         29: 'Correlation Function 2',
         30: 'Correlation Function 3',
         31: 'Correlation Function 4',
         32: 'Correlation Function 5',
         33: 'Octave 1',
         34: 'Octave 2',
         35: 'Capture 1',
         36: 'Capture 2',
         37: 'Octave User Function 1',
         38: 'Octave User Function 2',
         39: 'Octave User Function 3',
         40: 'Octave User Function 4',
         41: 'Octave User Function 5',
         42: 'Spectrum 1',
         43: 'Spectrum 2',
         44: 'Normalized Variance 1',
         45: 'Normalized Variance 2',
         46: 'Cross Spectrum',
         47: 'Frequency Response',
         48: 'Swept Sine User Function 1',
         49: 'Swept Sine User Function 2',
         50: 'Swept Sine User Function 3',
         51: 'Swept Sine User Function 4',
         52: 'Swept Sine User Function 5',
         53: 'Linear Spectrum 1',
         54: 'Linear Spectrum 2',
         55: 'Power Spectrum 1',
         56: 'Power Spectrum 2',
         57: 'Time 1',
         58: 'Time 2',
         59: 'Windowed Time 1',
         60: 'Windowed Time 2',
         61: 'RPM Profile',
         62: 'Orbit',
         63: 'Track 1',
         64: 'Track 2',
         65: 'Capture Buffer 1',
         66: 'Capture Buffer 2',
         67: 'Order User Function 1',
         68: 'Order User Function 2',
         69: 'Order User Function 3',
         70: 'Order User Function 4',
         71: 'Order User Function 5',
         72: 'Histogram 1',
         73: 'Histogram 2',
         74: 'PDF 1',
         75: 'PDF 2',
         76: 'CDF 1',
         77: 'CDF 2',
         78: 'Time 1',
         79: 'Time 2',
         80: 'Capture Buffer 1',
         81: 'Capture Buffer 2',
         82: 'Histogram User Function 1',
         83: 'Histogram User Function 2',
         84: 'Histogram User Function 3',
         85: 'Histogram User Function 4',
         86: 'Histogram User Function 5'
         }[i])

        #View information
        i=int(gpibObj.query("VIEW?"+str(disp)))
        view.append({0: 'Log Magnitude',
                     1: 'Linear Magnitude',
                     2: 'Magnitude Squared',
                     3: 'Real Part',
                     4: 'Imaginary Part',
                     5: 'Phase',
                     6: 'Unwrapped Phase',
                     7: 'Nyquist',
                     8: 'Nichols'}[i])

        #Units
        result=gpibObj.query('UNIT?'+str(disp))
        result=result[:-1]  # Chop a new line character
        unit.append(result)   


    #Input Source
    i=int(gpibObj.query("ISRC?"))
    time.sleep(0.1)
    inputSource={0: 'Analog',
                 1: 'Capture'}[i]

    #Input Mode
    i=int(gpibObj.query("I1MD?"))
    CH1inputMode={0: 'Single ended',
                 1: 'Differential'}[i]
         
    i=int(gpibObj.query("I2MD?"))
    CH2inputMode={0: 'Single ended',
                 1: 'Differential'}[i]

    #Grounding
    i=int(gpibObj.query("I1GD?"))
    CH1Grounding={0: 'Float',
                 1: 'Grounded'}[i]

    i=int(gpibObj.query("I2GD?"))
    CH2Grounding={0: 'Float',
                 1: 'Grounded'}[i]

    #Coupling
    i=int(gpibObj.query("I1CP?"))
    CH1Coupling={0: 'DC',
                 1: 'AC',
                  2:'ICP'}[i]

    i=int(gpibObj.query("I2CP?"))
    CH2Coupling={0: 'DC',
                 1: 'AC',
                  2:'ICP'}[i]

    #Input Range
    result=gpibObj.query("I1RG?")
    match=re.search(r'^\s*([-+\d]*),.*',result)
    CH1Range=str(float(match.group(1)))
    match=re.search(r'\d,(\d)',result)
    i=int(match.group(1))
    CH1Range=CH1Range+{0: 'dBVpk', 1: 'dBVpp', 2: 'dBVrms', 3: 'Vpk', 4: 'Vpp', 5: 'Vrms', 
                       6: 'dBEUpk', 7: 'dBEUpp', 8: 'dBEUrms', 9: 'EUpk', 10: 'EUpp', 11: 'EUrms'}[i]

    result=gpibObj.query("I2RG?")
    match=re.search(r'^\s*([-+\d]*),.*',result)
    CH2Range=str(float(match.group(1)))
    match=re.search(r'\d,(\d)',result)
    i=int(match.group(1))
    CH2Range=CH2Range+{0: 'dBVpk', 1: 'dBVpp', 2: 'dBVrms', 3: 'Vpk', 4: 'Vpp', 5: 'Vrms', 
                       6: 'dBEUpk', 7: 'dBEUpp', 8: 'dBEUrms', 9: 'EUpk', 10: 'EUpp', 11: 'EUrms'}[i]

    #Auto Range
    i=int(gpibObj.query("A1RG?"))
    CH1AutoRange={0: 'Off', 1: 'On'}[i]
    i=int(gpibObj.query("I1AR?"))
    CH1AutoRangeMode={0: 'Up Only', 1: 'Tracking'}[i]

    i=int(gpibObj.query("A2RG?"))
    CH2AutoRange={0: 'Off', 1: 'On'}[i]
    i=int(gpibObj.query("I2AR?"))
    CH2AutoRangeMode={0: 'Normal', 1: 'Tracking'}[i]

    #Anti-Aliasing Filter
    i=int(gpibObj.query("I1AF?"))
    CH1AAFilter={0: 'Off', 1: 'On'}[i]

    i=int(gpibObj.query("I1AF?"))
    CH2AAFilter={0: 'Off', 1: 'On'}[i]

    #Source type
    i=int(gpibObj.query("STYP?"))
    SrcType={0: "Sine", 1: "Chirp", 2: "Noise", 3: "Arbitrary"}[i]

    #Source amplitude
    if SrcType == "Sine":
        if measGrp[0] == "Swept Sine":
            result=gpibObj.query("SSAM?")
        else:
            result=gpibObj.query("S1AM?")

        match=re.search(r'^\s*([-+.\d]*),.*',result)
        SrcAmp=str(float(match.group(1)))
        match=re.search(r'\d,(\d)',result)
        i=int(match.group(1))
        SrcAmp=SrcAmp+{0: 'mVpk', 1: 'mVpp', 2: 'mVrms', 3: 'Vpk', 4: 'Vrms', 5: 'dBVpk', 
                           6: 'dBVpp', 7: 'dBVrms'}[i]
    elif SrcType == "Chirp":
        result=gpibObj.query("CAMP?")
        match=re.search(r'^\s*([-+.\d]*),.*',result)
        SrcAmp=str(float(match.group(1)))
        match=re.search(r'\d,(\d)',result)
        i=int(match.group(1))
        SrcAmp=SrcAmp+{0: 'mV', 1: 'V', 2: 'dBVpk'}[i]
    elif SrcType == "Noise":
        result=gpibObj.query("NAMP?")
        match=re.search(r'^\s*([-+.\d]*),.*',result)
        SrcAmp=str(float(match.group(1)))
        match=re.search(r'\d,(\d)',result)
        i=int(match.group(1))
        SrcAmp=SrcAmp+{0: 'mV', 1: 'V', 2: 'dBVpk'}[i]
    else:
        result=float(gpibObj.query("AAMP?"))
        SrcAmp=str(result/100)+"V"
        
    #Write to the parameter file

    print "Writing to the parameter file."
    #Header
#     #For the ease of getting necessary information for plotting the data, several numbers and strings are put first
#     #The format is the number of channels comes first, then the title of the channels and the units follow, 
#     #one per line.
#     paramFile.write('#The following lines are for a matlab plotting function\n')
#     paramFile.write(str(numOfDisp)+'\n')
#     for disp in range(numOfDisp):
#         paramFile.write(view[disp]+'\n')
#         paramFile.write('Frequency\n')
#     for disp in range(numOfDisp):
#         paramFile.write(unit[disp]+'\n')
#         paramFile.write('Hz\n')

    #Human readable section begin
    paramFile.write('##################### Measurement Parameters #############################\n')
    paramFile.write('Measurement Group: ')
    for disp in range(numOfDisp):
        paramFile.write(' "'+measGrp[disp]+'"')
    paramFile.write('\n')
    
    paramFile.write('Measurements: ')
    for disp in range(numOfDisp):
        paramFile.write(' "'+measurement[disp]+'"')
    paramFile.write('\n')
    
    paramFile.write('View: ')
    for disp in range(numOfDisp):
        paramFile.write(' "'+view[disp]+'"')
    paramFile.write('\n')
        
    paramFile.write('Unit: ')
    for disp in range(numOfDisp):
        paramFile.write(' "'+unit[disp]+'"')
    paramFile.write('\n\n')
    
    paramFile.write('##################### Input Parameters #############################\n')

    paramFile.write('Input Source: ')
    paramFile.write(inputSource+'\n')

    paramFile.write('Input Mode: ')
    paramFile.write(CH1inputMode+', '+CH2inputMode+'\n')
    
    paramFile.write('Input Grounding: ')
    paramFile.write(CH1Grounding+', '+CH2Grounding+'\n')
    
    paramFile.write('Input Coupling: ')
    paramFile.write(CH1Coupling+', '+CH2Coupling+'\n')

    paramFile.write('Input Range: ')
    paramFile.write(CH1Range+', '+CH2Range+'\n')

    paramFile.write('Auto Range: ')
    paramFile.write(CH1AutoRange+', '+CH2AutoRange+'\n')

    paramFile.write('Auto Range Mode: ')
    paramFile.write(CH1AutoRangeMode+', '+CH2AutoRangeMode+'\n')

    paramFile.write('Anti-Aliasing Filter: ')
    paramFile.write(CH1AAFilter+', '+CH2AAFilter+'\n')
    
    paramFile.write('##################### Source Parameters #############################\n')
    
    paramFile.write('Source Type: ')
    paramFile.write(SrcType+"\n")

    paramFile.write('Source Amplitude: ')
    paramFile.write(SrcAmp+"\n")

def reset(gpibObj):
    gpibObj.command("*RST")
    time.sleep(5)
