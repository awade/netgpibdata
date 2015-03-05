# This module provides data access to Agilent 4395 network analyzer

# Standard Library imports
import time
# Third-party libraries
from numpy import linspace
# Required custom libraries
import netgpib


####################
# GPIB
####################


def connectGPIB(ipAddress,gpibAddress):
    print 'Connecting to '+str(ipAddress)+':'+str(gpibAddress)+'...',
    gpibObj=netgpib.netGPIB(ipAddress, gpibAddress)
    print 'Connected.'
    print "Instrument ID: ",
    idnString=gpibObj.query("ID?")
    print idnString.splitlines()[-1]
    return(gpibObj)


####################
# Settings helpers
####################

def reset(gpibObj):
    # Call reset command, manual states it takes 12 sec to finish
    print('Resetting HP8591E...')
    gpibObj.command("IP")
    time.sleep(2)
    print('Done!')


####################
# Compatibility with old netgpibdata script
####################


def getdata(gpibObj, dataFile, paramFile):
    # For compatibility with old netgpibdata
    timeStamp = time.strftime('%b %d %Y - %H:%M:%S', time.localtime())
    (freq,data)=download(gpibObj)
    writeHeader(dataFile, timeStamp)
    writeData(dataFile, freq, data, delimiter = ', ')


def getparam(gpibObj, fileRoot, dataFile, paramFile):
    # For compatibility with old netgpibdata
    timeStamp = time.strftime('%b %d %Y - %H:%M:%S', time.localtime())
    writeHeader(paramFile, timeStamp)
    writeParams(gpibObj, paramFile)


####################
# Fetching data
####################


def download(gpibObj):

    print('Downloading Data...')
    gpibObj.command('TDF P')
    data = [float(val) for val in gpibObj.query('TRA?')[:-2].split(',')]
    
    freqLo = float(gpibObj.query('FA?'))
    freqHi = float(gpibObj.query('FB?'))
    freqs = list(linspace(freqLo,freqHi,num=len(data)))

    return(freqs,data)


####################
# Output file writing
####################


def writeHeader(dataFile, timeStamp):
    dataFile.write('# HP8591E Measurement - Timestamp: ' + timeStamp+'\n')

def writeData(dataFile, freq, data, delimiter='    '):
    print('Writing measurement data to file...')
    #Write data vectors
    for i in range(len(freq)):
        dataFile.write(str(freq[i])+ delimiter +str(data[i])+'\n')

####################
# Run measurements
####################


def measure(gpibObj, params):
    print('Triggering measurement!')
    # Clear status bits, only ask for sweep end events
    gpibObj.command('RQS 4')
    gpibObj.command('CLS')
    gpibObj.command('CLRAVG') # Doesn't work?
    gpibObj.command('CONTS;SNGLS')
    gpibObj.command('TS')

    while not int(gpibObj.srq()):
        time.sleep(1)
    print('Done!')


####################
# Saving and setting measurement parameters
####################


def setParameters(gpibObj, params):
    gpibObj.command('IP')
    gpibObj.command('SNGLS')
    gpibObj.command('AUNITS '+str(params['dataMode']))
    gpibObj.command('VAVG '+str(params['averages']))
    gpibObj.command('VB AUTO')
    gpibObj.command('FA '+params['startFreq'])
    gpibObj.command('FB '+params['stopFreq'])
    gpibObj.command('RB '+str(params['resBW']))
    gpibObj.command('AT '+ str(params['attenuation']))

    print('Parameters set!')


def writeParams(gpibObj, paramFile):

    # Get bandwidth information
    bw = str(float(gpibObj.query('RB?')))
    unit = gpibObj.query('AUNITS?')[:-2]
    fStart = str(float(gpibObj.query('FA?')))
    fStop = str(float(gpibObj.query('FB?')))

    # Get attenuator information
    att = str(int(gpibObj.query('AT?'))) + 'dB '

    # Averages
    nAvg = str(int(gpibObj.query('VAVG?')))

    print "Writing to the parameter file."

    paramFile.write('#---------- Measurement Parameters ------------\n')
    paramFile.write('# Start Frequency (Hz): '+fStart+'\n')
    paramFile.write('# Stop Frequency (Hz): '+fStop+'\n')
    paramFile.write('# Measurement Units: '+unit+'\n')

    paramFile.write('#---------- Analyzer Settings ----------\n')
    paramFile.write('# Number of Averages: '+nAvg+'\n')
    paramFile.write('# Resolution Bandwidth: '+bw+'\n')
    paramFile.write('# Input Attenuator: '+att+'\n')

    paramFile.write('#---------- Measurement Data ----------\n')
    paramFile.write('# [Freq(Hz) Spectrum('+unit+')]\n')
