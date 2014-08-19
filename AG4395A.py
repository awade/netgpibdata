# This module provides data access to Agilent 4395 network analyzer

import re
#import sys
#import math
import time
#import netgpib
import numpy as np

def setParamters(gpibObj, params): 
    # Spectrum only so far!
    gpibObj.command('PRES')
    time.sleep(0.1)
    gpibObj.command('SA')
    time.sleep(0.1)

    # Spectrum or noise?

    if params['specType'].lower() == 'noise':
        gpibObj.command('FMT '+params['specType'][0:5].upper())
    elif params['specType'].lower() != 'spectrum':
        raise ValueError('specType not parsing!')

    # Set up channel inputs
    if params['dualChan'].lower() == 'dual' and len(params['channels'])==2: 
        gpibObj.command('DUAC ON')
        time.sleep(0.1)
    else:
        gpibObj.command('MEAS '+params['channels'][0])

    for jj in range(len(params['channels'])): 

        gpibObj.command('CHAN'+str(jj+1))
        gpibObj.command('MEAS '+params['channels'][jj])
        time.sleep(0.1)
        
        # For now, default noise to V^2/Hz and spectrum to dBm
        if params['specType'].lower() =='noise':
            gpibObj.command('SAUNIT V')
        else:
            gpibObj.command('SAUNIT DBM')

        gpibObj.command('AVERFACT '+params['averages'])
        time.sleep(0.1)
        # Stops measurement from proceeding for now?
        gpibObj.command('AVER OFF')
        gpibObj.command('STAR '+params['startFreq'])
        time.sleep(0.1)
        gpibObj.command('STOP '+params['stopFreq'])
        time.sleep(0.1)
        gpibObj.command('BW '+params['ifBW'])
        time.sleep(0.1)
        gpibObj.command('ATTAUTO OFF')
        time.sleep(0.1)
        gpibObj.command('ATT' +str(jj+1) +' ' +params['attentuation']+'DB')
        time.sleep(0.1)

    print('Parameters set!')

def measure(gpibObj, params):
    nDisp = int(gpibObj.query('DUAC?')[0])+1
    tim = gpibObj.query("SWET?")
    tot_time = float(tim)*(int(params['averages'])+1)

    for disp in range(nDisp):
        gpibObj.command('CHAN'+str(disp+1))
        time.sleep(0.1)
        gpibObj.command('AVER ON')
        time.sleep(0.1)
        gpibObj.command("AVERREST") #Start measurement

    print('Running...')
    # Is this really the best way? Can't I query the number of averages, like sr785?
    # Yes! Read page 5-14 in programming manual, need to figure out how to implement.
    time.sleep(tot_time)
    print('Done!')

def downloadData(gpibObj, params):
    # Put the analyzer on hold
    gpibObj.command('HOLD')
    time.sleep(0.1)


    #Set the output format to ASCII
    gpibObj.command('FORM4')
    
    #Check for the analyzer mode
    analyzerMode = int(gpibObj.query('NA?'))

    if analyzerMode == 1:
        # Not sure what the different channels return in each case...
        # Need to verify that this works when I make NWAG upgrade
        # It is the network analyzer mode    
        # In this mode, the data format is real,imag for each frequency point
        raise ValueError('I cannot do TFs yet!')
    else: # Spectrum mode!

        print('Reading frequency points...')            
        freqList = gpibObj.query('OUTPSWPRM?',1024)
        freqs = np.array(map(float,re.findall(r'[-+.E0-9]+', freqList)))

        dataList=[]

        if bool(gpibObj.query('DUAC?')):
            for ii in range(2):
                gpibObj.command('CHAN'+str(ii+1))
                time.sleep(0.5)
                print('Reading data from channel '+str(ii+1))
                dataStrings = gpibObj.query('OUTPDTRC?',1024)
                dataList.append(np.array(map(float,re.findall(r'[-+.E0-9]+', dataStrings))))
        else:
            print('Reading data from current display...')
            dataStrings = gpibObj.query('OUTPDTRC?',1024)
            dataList.append(np.array(map(float,re.findall(r'[-+.E0-9]+', dataStrings))))
        
        data = np.transpose(np.vstack(([column for column in dataList])))

    return(freqs,data)        


def getdata(gpibObj, dataFile, paramFile):
    #Put the analyzer on hold
    gpibObj.command('HOLD')
    time.sleep(0.1)

    #Get the number of data points
    #numPoints = int(gpibObj.query('POIN?'))

    #Set the output format to ASCII
    gpibObj.command('FORM4')
    
    #Check for the analyzer mode
    analyzerMode = int(gpibObj.query('NA?'))

    if analyzerMode == 1:
        # It is the network analyzer mode    
        # In this mode, the data format is real,imag for each frequency point

        #Get the frequency points
        print('Reading frequency points.')
        receivedData=gpibObj.query('OUTPSWPRM?',1024)

        # Parse data
        # Matching to the second column of dumpedData
        freqList=re.findall(r'[-+.E0-9]+', receivedData, re.M)

        # Get the data
        print('Reading data.')
        receivedData=gpibObj.query('OUTPDATA?',1024)

        # Break the data into lists
        dataList = re.findall(r'[-+.E0-9]+',receivedData)
        
        # Output data
        print('Writing the data into a file.')
        
        j=0;
        for i in range(len(freqList)):
            dataFile.write(freqList[i]+', '+dataList[j]+', '+ dataList[j+1]+'\n')
            j=j+2;
    else:
        # It is spectrum analyzer mode
            
        #Check if it is the dual channel mode or not
        numOfChan = int(gpibObj.query('DUAC?')) +1

        # Get the current channel number
        ans = int(gpibObj.query('CHAN1?'))
        if ans ==1:
            currentChannel = 1
        else:
            currentChannel = 2

        #Get the data

        dataList=[]
        freqList=[]
        # Loop for each channel
        for i in range(1,numOfChan+1):
            #ch stores the current channel number
            if numOfChan == 1:
                ch=currentChannel
            else:
                ch=i
                
            # Change the active channel to ch
            gpibObj.command( 'CHAN'+str(ch))
            time.sleep(0.5)

            # Get the frequency points
            print('Reading frequency points for channel '+str(i))            
            receivedData = gpibObj.query('OUTPSWPRM?',1024)

            # Break into elements
            freqList = re.findall(r'[-+.E0-9]+', receivedData)
            
            print('Reading data from channel '+str(i))
            receivedData = gpibObj.query('OUTPDATA?',1024)
                        
            # Break into elements
            dataList = re.findall(r'[-+.E0-9]+',receivedData)
                
            # Output data
            print('Writing channel '+str(ch)+' data into a file.')
            dataFile.write('# Channel '+str(ch)+'\n')
            for j in range(len(freqList)):
                dataFile.write(freqList[j]+', '+dataList[j])
                dataFile.write('\n')
                
    # Continue the measurement
    gpibObj.command( 'CONT\n')                            

def getparam(gpibObj, filename, dataFile, paramFile):
    #Get measurement parameters
    
    print('Reading measurement parameters')
    
    #pdb.set_trace()
    #Check the analyzer mode
    analyzerMode = int(gpibObj.query('NA?'))
    analyzerType={1: 'Network Analyzer', 0: 'Spectrum Analyzer'}[analyzerMode]

    #Determine labels and units
    Label=[]
    Unit=[]
    if analyzerMode == 1: # Network analyzer mode
        Label.append('Real Part')
        Label.append('Imaginary Part')
        Unit.append('')
        Unit.append('')
        numOfChan = 2
    else:  # Spectrum analyzer mode
        numOfChan = int(gpibObj.query('DUAC?')) +1
        for i in range(numOfChan):
            Label.append('Spectrum')
            Unit.append('W')

    #Get the current channel number
    ans=int(gpibObj.query('CHAN1?'))
    if ans ==1:
        currentChannel=1
    else:
        currentChannel=2

    BW=[]
    BWAuto=[]
    MEAS=[]
    for i in range(numOfChan):

        #ch stores the current channel number
        if numOfChan == 1:
            ch=currentChannel
        else:
            ch=i+1
                
        #Change the active channel to ch
        print('Change channel to '+str(ch))
        gpibObj.command( 'CHAN'+str(ch))
        time.sleep(1)

    # Get bandwidth information
                  
        buf=gpibObj.query('BW?')
        BW.append(buf[:-1])

        j=int(gpibObj.query('BWAUTO?'))
        BWAuto.append({0: 'Off', 1: 'On'}[j])

    # Measurement Type
        gpibObj.command('CHAN'+str(i+1))
        buf=gpibObj.query('MEAS?')
        MEAS.append(buf[:-1])

    # Get attenuator information
    AttnR = str(int(gpibObj.query('ATTR?')))+'dB'
    AttnA = str(int(gpibObj.query('ATTA?')))+'dB'
    AttnB = str(int(gpibObj.query('ATTB?')))+'dB'
    
    # Source power
    buf = gpibObj.query('POWE?')
    SPW = buf[:-1]+'dBm'
        
    # Write to the parameter file
    # Header
    paramFile.write('Agilent 4395A parameter file\nThis file contains measurement parameters for the data saved in '
                    +filename+'.dat\n')
    # For the ease of getting necessary information for plotting the data, several numbers 
    # and strings are put first.
    # The format is the number of channels comes first, then the title of the channels and 
    # the units follow, one per line.
    #     paramFile.write('#The following lines are for a matlab plotting function\n')
    #     paramFile.write(str(numOfChan)+'\n')

    paramFile.write('Data format: Freq')
    for i in range(numOfChan):
         paramFile.write(', '+Label[i])
         paramFile.write('('+Unit[i]+')')

    paramFile.write('\n')

    paramFile.write('##################### Measurement Parameters #############################\n')
    paramFile.write('Analyzer Type: '+analyzerType+'\n')
    for i in range(numOfChan):
        #ch stores the current channel number
        if numOfChan == 1:
            ch=currentChannel
        else:
            ch=i+1

        paramFile.write('CH'+str(ch)+' measurement: '+MEAS[i]+'\n')
    
    for i in range(numOfChan):
        paramFile.write('CH'+str(ch)+' bandwidth: '+BW[i]+'\n')
        paramFile.write('CH'+str(ch)+' auto bandwidth: '+BWAuto[i]+'\n')
    
    paramFile.write('R attenuator: '+AttnR+'\n')
    paramFile.write('A attenuator: '+AttnA+'\n')
    paramFile.write('B attenuator: '+AttnB+'\n')

    paramFile.write('Source power: '+SPW+'\n')
