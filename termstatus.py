from __future__ import division
import sys

class statusTxt:
    def __init__(self,initTxt):
        self.txtlen = len(initTxt)
        self.txt = initTxt
        # TODO: Check where this print command actually ends, previous ended with comma
        print(initTxt,
        sys.stdout.flush())

    def update(self, updateTxt):
        # TODO: make this print command python3 friendly
        print "\010"+"\010"*self.txtlen+updateTxt,
        sys.stdout.flush()
        self.txtlen = len(updateTxt)
        self.txt = updateTxt

    def end(self,updateTxt=""):
        if updateTxt == "":
            print("")
        else:
            # TODO: make this print command python3 friendly
            print "\010"+"\010"*self.txtlen+updateTxt

        sys.stdout.flush()

class progressBar:
    def __init__(self, width, nTot):
        self.width=width
        self.nTot=nTot
        self.stepped=0
        print('['+' '*width+']')
        # TODO: Check if following line was supposed to include comma to next line
        print('\b'*(width+2))
        sys.stdout.flush() 
        self.done=False

    def update(self, val):
        steps = int(round(val/self.nTot*self.width))
        if steps > self.stepped:
            for ii in range(steps-self.stepped):
                print '\b'+'*',
            sys.stdout.flush()
            self.stepped=steps

        if val == self.nTot:
            self.end()

    def end(self):
        if self.done is False:
            # TODO: make this print command python3 friendly
            print '\b] Done!'
            sys.stdout.flush()
            self.done=True
