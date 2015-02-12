# This module provides data access to Agilent 4395 network analyzer

import re
import sys
import math
from optparse import OptionParser
from socket import *
import time
import gpib
import pdb

def getdata(netSock, gpibAddr, dataFile, paramFile):
    # Initialization of the GPIB-Ethernet converter box
    print('Initializing the GPIB-Ethernet converter \n')
    
    netSock.setblocking(0)
    netSock.send("++addr "+str(gpibAddr)+"\n")
    time.sleep(0.1)
    netSock.send("++eos 3\n")
    time.sleep(0.1)
    netSock.send("++mode 1\n")
    time.sleep(0.1)
    netSock.send("++auto 0\n")
    time.sleep(0.1)
    netSock.send("++read_tmo_ms 4000\n")
    time.sleep(0.1)
    netSock.send("++eot_char 4\n")
    netSock.send("++eot_enable 1\n")
    netSock.send("++addr "+str(gpibAddr)+"\n")

    #Put the analyzer on hold
    netSock.send("HOLD\n")
    time.sleep(0.1)

    #Get the number of data points
    netSock.send("POIN?\n")
    time.sleep(0.1)
    netSock.send("++read eoi\n")
    numPoints = gpib.gpibGetData(netSock,30,'\004')
    numPoints = int(numPoints)

    #Set the output format to ASCII
    netSock.send("++auto 0\n")
    netSock.send("FORM4\n")

    
    #Check for the analyzer mode
    netSock.send("NA?\n") 
    netSock.send("++read eoi\n")
    analyzerMode = int(gpib.gpibGetData(netSock,30,'\004'))

    if analyzerMode == 1:
        # It is the network analyzer mode    
        # In this mode, the data format is real,imag for each frequency point


        #Get the frequency points
        print('Reading frequency points. \n')
        
        netSock.send("OUTPSWPRM?\n")
        netSock.send("++read eoi\n")
    
        time.sleep(0.2)
        receivedData=""
        while 1:  #Receive data from network until the end of data.
            time.sleep(0.1)
            tmp = gpib.gpibGetData(netSock,1024,'\004')
            if not len(tmp) == 1024:
                receivedData=receivedData+tmp
                break
            receivedData=receivedData+tmp

        #Parse data
        #Matching to the second column of dumpedData
        freqList=re.findall(r'[-+.E0-9]+', receivedData, re.M)

        #Get the data
        print('Reading data. \n')
        
        netSock.send("OUTPDATA?\n")
        netSock.send("++read eoi\n")
        time.sleep(0.2)
        receivedData=""
        while 1:  #Receive data from network until the end of data.
            time.sleep(0.1)
            tmp = gpib.gpibGetData(netSock,1024,'\004')
            if not len(tmp) == 1024:
                receivedData=receivedData+tmp
                break
            receivedData=receivedData+tmp

        #Break the data into lists
        dataList = re.findall(r'[-+.E0-9]+',receivedData)
        
    # Output data
        print('Writing the data into a file. \n')
        
        j=0;
        for i in range(len(freqList)):
            dataFile.write(freqList[i]+', '+dataList[j]+', '+ dataList[j+1]+'\n')
            j=j+2;
    else:
        #It is spectrum analyzer mode
            
        #Check if it is the dual channel mode or not
        netSock.send('DUAC?\n')
        netSock.send("++read eoi\n")
        numOfChan = int(gpib.gpibGetData(netSock,30,'\004')) +1

        #Get the current channel number
        netSock.send('CHAN1?\n')
        netSock.send("++read eoi\n")
        ans=int(gpib.gpibGetData(netSock,30,'\004'))
        if ans ==1:
            currentChannel=1
        else:
            currentChannel=2

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
                
            #Change the active channel to ch
            netSock.send( "CHAN"+str(ch)+'\n')
            time.sleep(1)

            #Get the frequency points
            print('Reading frequency points for channel '+str(i)+'\n')
            
            netSock.send("OUTPSWPRM?\n")
            netSock.send("++read eoi\n")

            receivedData = gpib.gpibGetData(netSock,1024,'\004', 1)

            #Break into elements
            freqList=re.findall(r'[-+.E0-9]+', receivedData)
            
            print('Reading data from channel '+str(i)+'\n')
            
            netSock.send("OUTPDATA?\n")
            netSock.send("++read eoi\n")

            time.sleep(0.1)
            receivedData = gpib.gpibGetData(netSock,1024,'\004', 1)
                        
            #Break into elements
            dataList=re.findall(r'[-+.E0-9]+',receivedData)
                
            # Output data
            print('Writing channel '+str(ch)+' data into a file. \n')
            dataFile.write('Channel '+str(ch)+'\n')
            for j in range(len(freqList)):
                dataFile.write(freqList[j]+', '+dataList[j])
                dataFile.write('\n')
                
    #Continue the measurement
    #netSock.send( "CONT\n")                            
    netSock.send("++eot_enable 0\n")

def getparam(netSock, gpibAddr, filename, dataFile, paramFile):
    #Get measurement parameters
    
    print('Reading measurement parameters\n')
    
    
    netSock.send("++addr "+str(gpibAddr)+"\n")
    time.sleep(0.1)
    netSock.send("++eos 3\n")
    time.sleep(0.1)
    netSock.send("++mode 1\n")
    time.sleep(0.1)
    netSock.send("++auto 0\n")
    time.sleep(0.1)
    netSock.send("++read_tmo_ms 4000\n")
    time.sleep(0.1)
    netSock.send("++eot_char 4\n")
    netSock.send("++eot_enable 1\n")
    netSock.send("++addr "+str(gpibAddr)+"\n")

    time.sleep(0.1)
    #pdb.set_trace()
    #Check the analyzer mode
    netSock.send("NA?\n") 
    netSock.send("++read eoi\n")
    time.sleep(0.1)
    analyzerMode = int(gpib.gpibGetData(netSock,30,'\004'))
    analyzerType={1: 'Network Analyzer', 0: 'Spectrum Analyzer'}[analyzerMode]

    #Determine labels and units
    Label=[]
    Unit=[]
    if analyzerMode == 1: #Network analyzer mode
        Label.append('Real Part')
        Label.append('Imaginary Part')
        Unit.append('')
        Unit.append('')
        numOfChan = 2
    else:  #Spectrum analyzer mode
        netSock.send('DUAC?\n')
        netSock.send("++read eoi\n")
        numOfChan = int(gpib.gpibGetData(netSock,30,'\004')) +1
        for i in range(numOfChan):
            Label.append('Spectrum')
            Unit.append('W')

    #Get the current channel number
    netSock.send('CHAN1?\n')
    netSock.send("++read eoi\n")
    ans=int(gpib.gpibGetData(netSock,30,'\004'))
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
        print("Change channel to "+str(ch))
        netSock.send( "CHAN"+str(ch)+'\n')
        time.sleep(1)

    # Get bandwidth information
                  
        netSock.send('BW?\n')
        netSock.send('++read eoi\n')
        buf=gpib.gpibGetData(netSock,100,'\004')
        BW.append(buf[0:len(buf)-1])
        netSock.send('BWAUTO?\n')
        netSock.send('++read eoi\n')
        j=int(gpib.gpibGetData(netSock,100,'\004'))
        BWAuto.append({0: 'Off', 1: 'On'}[j])

    #Measurement Type
        netSock.send('CHAN'+str(i+1)+'\n')
        netSock.send('MEAS?\n')
        netSock.send('++read eoi\n')
        buf=gpib.gpibGetData(netSock,100,'\004')
        MEAS.append(buf[0:len(buf)-1])

    # Get attenuator information
    netSock.send('ATTR?\n')
    netSock.send('++read eoi\n')
    AttnR=str(int(gpib.gpibGetData(netSock,100,'\004')))+'dB'
    netSock.send('ATTA?\n')
    netSock.send('++read eoi\n')
    AttnA=str(int(gpib.gpibGetData(netSock,100,'\004')))+'dB'
    netSock.send('ATTB?\n')
    netSock.send('++read eoi\n')
    AttnB=str(int(gpib.gpibGetData(netSock,100,'\004')))+'dB'
    
    #Source power
    netSock.send('POWE?\n')
    netSock.send('++read eoi\n')
    buf=gpib.gpibGetData(netSock,100,'\004')
    SPW=buf[0:len(buf)-1]+'dBm'

    
    
        
    #Write to the parameter file
    #Header
    paramFile.write('#Agilent 4395A parameter file\n#This file contains measurement parameters for the data saved in '
                    +filename+'.dat\n')
    #For the ease of getting necessary information for plotting the data, several numbers and strings are put first
    #The format is the number of channels comes first, then the title of the channels and the units follow, 
    #one per line.
    paramFile.write('#The following lines are for a matlab plotting function\n')
    paramFile.write(str(numOfChan)+'\n')
    for i in range(numOfChan):
        paramFile.write(Label[i]+'\n')
        paramFile.write(Unit[i]+'\n')

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
    
    paramFile.write('R attanuator: '+AttnR+'\n')
    paramFile.write('A attanuator: '+AttnA+'\n')
    paramFile.write('B attanuator: '+AttnB+'\n')

    paramFile.write('Source power: '+SPW+'\n')
