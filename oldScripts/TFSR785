#! /usr/bin/env python
#
# TFSR785.py [-f filename] [-i ip_address] [-a gpib_address] [{-s|--startfreq} start_freq]
#                 [{-e|--stopfreq} stop_freq] [-n|--numpoints num_of_points] [--sweep Linear|Log] 
#                 [{-x|--excamp} excitation_amplitude] [{-c|--settlecycle} settle_cycle]
#                 [{-t|--intcycle} integration_cycle] [--ic1 AC|DC ] [--ic2 AC|DC ]
#                 [--ig1 GND|Float ] [--ig2 GND|Float ] [--armode UpOnly|Tracking ] [--title Title]
#                 [--memo Memo]
#                 
#                 
# Command a SR785 to execute a transfer function measurement.
#
# Yoichi Aso  Sep 22 2008

import re
import sys
import math
import optparse
import time
import pdb
import netgpib
import SR785
import termstatus


#Parse options
usage = """usage: %prog [options]

This program executes a transfer function measurement using SR785.
Various measurement conditions can be set using options.
The measurement result will be saved in FILENAME.dat and the measurement parameters in FILENAME.par.
Optionally, it can plot the retrieved data. You need matplotlib and numpy modules to plot the data.
"""

parser = optparse.OptionParser(usage=usage)
parser.add_option("-f", "--file", dest="filename",
                  help="Output file name without an extension", default="TF")
parser.add_option("-i", "--ip",
                  dest="ipAddress", default="teofila",
                  help="IP address/Host name")
parser.add_option("-a", "--address",
                  dest="gpibAddress", type="int", default=10,
                  help="GPIB device address")
parser.add_option("-s", "--startfreq",
                  dest="startFreq", default="100kHz",
                  help="Start frequency. Units can be mHz, Hz or kHz.")
parser.add_option("-e", "--stopfreq",
                  dest="stopFreq", default="10kHz",
                  help="Stop frequency. Units can be mHz, Hz or kHz.")
parser.add_option("-n", "--numpoints",
                  dest="numOfPoints", type="int", default="50",
                  help="Number of frequency points")
parser.add_option("--sweep",
                  dest="sweepType", type="string", default="Log",
                  help="Sweep type: Log or Linear (default: Log)")
parser.add_option("-x", "--excamp",
                  dest="excAmp", default="1mV",
                  help="Excitation amplitude")
parser.add_option("-c", "--settlecycle",
                  dest="settleCycles", type="int", default="10",
                  help="Settle cycles")
parser.add_option("-t", "--intcycle",
                  dest="intCycles", type="int",default="20",
                  help="Integration cycles")
parser.add_option("--ic1",
                  dest="inputCoupling1", type="string",default="DC",
                  help="CH1 input coupling. DC or AC (default:DC)")
parser.add_option("--ic2",
                  dest="inputCoupling2", type="string",default="DC",
                  help="CH2 input coupling. DC or AC (default:DC)")
parser.add_option("--ig1",
                  dest="inputGND1", type="string",default="Float",
                  help="CH1 input grounding. Float or Ground (default:Float)")
parser.add_option("--ig2",
                  dest="inputGND2", type="string",default="Float",
                  help="CH2 input grounding. Float or Ground (default:Float)")
parser.add_option("--armode",
                  dest="arMode", type="string",default="UpOnly",
                  help="Auto range mode: UpOnly or Tracking (default: UpOnly)")
parser.add_option("--plot",
                  dest="plotData", default=False,
                  action="store_true",
                  help="Plot the downloaded data.")
parser.add_option("--title",
                  dest="title", type="string",default="",
                  help="Title of the measurement. The given string will be written into the parameter file.")
parser.add_option("--memo",
                  dest="memo", type="string",default="",
                  help="Use this option to note miscellaneous things.")


(options, args) = parser.parse_args()
# Create a netGPIB class object
print('Connecting to '+str(options.ipAddress)+' ...'),
gpibObj=netgpib.netGPIB(options.ipAddress, options.gpibAddress, '\004',0)
print('done.')

#File names
dataFileName=options.filename+'.dat'
paramFileName=options.filename+'.par'

print('Data will be written into '+dataFileName)
print('Parameters will be written into '+paramFileName)
print('Setting up parameters for the measurement') 

#pdb.set_trace()
#
#Prepare for the TF measurement

#Set output to GPIB
gpibObj.command("OUTX0")
time.sleep(0.1)

#Input setup
if options.inputCoupling1 == "AC":
    icp1="1"
else:
    icp1="0"
gpibObj.command('I1CP'+icp1) #CH1 Input Coupling
time.sleep(0.1)

if options.inputCoupling2 == "AC":
    icp2="1"
else:
    icp2="0"
gpibObj.command('I2CP'+icp2) #CH2 Input Coupling
time.sleep(0.1)

if options.inputGND1 == "Float":
    igd1="0"
else:
    igd1="1"
gpibObj.command('I1GD'+igd1) #CH1 Input GND
time.sleep(0.1)

if options.inputGND2 == "Float":
    igd2="0"
else:
    igd2="1"
gpibObj.command('I2GD'+igd2) #CH2 Input GND
time.sleep(0.1)

gpibObj.command('A1RG0') #AutoRange Off
time.sleep(0.1)
gpibObj.command('A2RG0') #AutoRange Off
time.sleep(0.1)
if options.arMode == "Tracking":
    arModeID='1'
else:
    arModeID='0'
gpibObj.command('I1AR'+arModeID) #Auto Range Mode 
time.sleep(0.1)
gpibObj.command('I2AR'+arModeID) #Auto Range Mode 
time.sleep(0.1)
gpibObj.command('A1RG1') #AutoRange On
time.sleep(0.1)
gpibObj.command('A2RG1') #AutoRange On
time.sleep(0.1)

gpibObj.command('I1AF1') #Anti-Aliasing filter On
time.sleep(0.1)
gpibObj.command('I2AF1') #Anti-Aliasing filter On
time.sleep(0.1)

#Set measurement parameters
gpibObj.command('DFMT1') # Dual display
time.sleep(0.1)
gpibObj.command('ACTD0') # Active display 0
time.sleep(0.1)

gpibObj.command('MGRP2,3') # Measurement Group = Swept Sine
time.sleep(0.1)
gpibObj.command('MEAS2,47') # Frequency Resp
time.sleep(0.1)
gpibObj.command('VIEW0,0') # Disp 0 = LogMag
time.sleep(0.1)
gpibObj.command('VIEW1,5') # Dsip 1 = Phase
time.sleep(0.1)
gpibObj.command('UNDB0,1') # dB ON
time.sleep(0.1)
gpibObj.command('UNPK0,0') # PK Unit Off
time.sleep(0.1)
gpibObj.command('UNDB1,0') # dB OFF
time.sleep(0.1)
gpibObj.command('UNPK1,0') # PK Unit Off
time.sleep(0.1)
gpibObj.command('UNPH1,0') # Phase Unit deg.
time.sleep(0.1)
gpibObj.command('DISP0,1') # Live display on
time.sleep(0.1)
gpibObj.command('DISP1,1') # Live display on
time.sleep(0.1)
gpibObj.command('SSCY2,'+str(options.settleCycles)) # Settle cycles
time.sleep(0.1)
gpibObj.command('SICY2,'+str(options.intCycles)) # Integration cycles
time.sleep(0.1)
gpibObj.command('SSTR2,'+options.startFreq) #Start frequency
time.sleep(0.1)
gpibObj.command('SSTP2,'+options.stopFreq) #Stop frequency
time.sleep(0.1)
gpibObj.command('SNPS2,'+str(options.numOfPoints)) #Number of points
time.sleep(0.1)
gpibObj.command('SRPT2,0') #Single shot moede
time.sleep(0.1)
if options.sweepType == 'Linear':
    sweepTypeID='0'
else:
    sweepTypeID='1'
gpibObj.command('SSTY2,'+sweepTypeID) # Sweep Type
time.sleep(0.1)
gpibObj.command('SSAM'+options.excAmp) #Source Amplitude
time.sleep(0.1)


#Start measurement
print 'Transfer function measurement started:',
sys.stdout.flush()
numPoints=int(gpibObj.query('SNPS?0')) #Number of points
time.sleep(0.1)
gpibObj.command('STRT') #Source Amplitude
time.sleep(0.5)

#Wait for the measurement to end
measuring = True
percentage=0
accomplished=0
progressInfo=termstatus.statusTxt('0%')
while measuring:
    #Get status 
    measuring = not int(gpibObj.query('DSPS?4'))
    a=int(gpibObj.query('SSFR?'))
    percentage=int(math.floor(100*a/numPoints))
    progressInfo.update(str(percentage)+'%')
    accomplished=percentage
    time.sleep(0.3)

        
progressInfo.end('100%')


#Download Data
#pdb.set_trace()
time.sleep(2)


data=[]
for disp in range(2):
    print('Downloading data from display #'+str(disp))
    (f,d)=SR785.downloadData(gpibObj, disp)        
    data.append(d)
    
freq=f
        
#Change the measurement to Norm Variance
print('Switching to normalized variance display')
gpibObj.command('MEAS0,44')  #Norm Variance Ch1
time.sleep(0.1)
gpibObj.command('UNDB0,0') # dB Off
time.sleep(0.1)
gpibObj.command('MEAS1,45')  #Norm Variance Ch2
time.sleep(0.1)
gpibObj.command('UNDB1,0') # dB Off
time.sleep(2)
# Download Normarized Variance
for disp in range(2):
    print('Downloading data from display #'+str(disp))
    (f,d)=SR785.downloadData(gpibObj, disp)        
    data.append(d)

#Open files
dataFile = open(dataFileName,'w')
paramFile = open(paramFileName,'w')

#Write to the data file
print('Writing data into the data file ...')
    
for i in range(len(freq)):
    dataFile.write(freq[i])
    for disp in range(4):
        dataFile.write(' '+data[disp][i])
    dataFile.write('\n')

#Deal with an empty title
if options.title == "":
    options.title = options.filename

#Write to parameter file
print('Writing measurement parameters into the parameter file ...')
paramFile.write('#SR785 Transfer function measurement\n')
paramFile.write('#Column format = [Freq  Mag(dB) Phase(deg) NormVar1  NormVar2]\n')
paramFile.write('Title: '+options.title+'\n')
paramFile.write('Memo: '+options.memo+'\n')
paramFile.write('#---------- Measurement Setup ------------\n')
paramFile.write('Start frequency = '+options.startFreq+'\n')
paramFile.write('Stop frequency = '+options.stopFreq+'\n')
paramFile.write('Number of frequency points = '+str(options.numOfPoints)+'\n')
paramFile.write('Excitation amplitude = '+options.excAmp+'\n')
paramFile.write('Settling cycles = '+str(options.settleCycles)+'\n')
paramFile.write('Integration cycles = '+str(options.intCycles)+'\n')
paramFile.write('\n')

SR785.getparam(gpibObj, options.filename, dataFile, paramFile)

dataFile.close()
paramFile.close()
gpibObj.close()

if options.plotData:
    import gpibplot
    gpibplot.plotTFSR785(options.filename)
    raw_input('Press enter to quit:')
