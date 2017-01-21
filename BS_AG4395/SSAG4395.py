#!/usr/bin/env python

import subprocess, os
import argparse
import sys

# python script for stepping through SR785 readings at various spans using SRmeasure script and netpibdata group of scripts

# Author: Andrew Wade - awade@ligo.caltech.edu
# Created: ~ Jan 8, 2017
# Change log:
#
# Issues:


def main():
    print(sys.argv)
    if len(sys.argv) != 2:
        basefilename = 'defaultName'
        print(basefilename)
        #Generate defult filename if none given
    else:
        basefilename = str(sys.argv[1])
        print(basefilename)

    print("-----------------------------------------------")
    print("Starting script")
    print(basefilename)

    numSpans = 5
    for i in range(1,numSpans+1):
        print("Batch number " + str(i) + ".")
        processExc = 'AGmeasure BS' + str(i) + '_SPAG4395A' + '.yml -f ' + basefilename
        pn = subprocess.Popen(processExc, shell=True)
        pn.wait()

if __name__=="__main__":
    main()
