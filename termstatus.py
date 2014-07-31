import sys
import pdb

class statusTxt:
    def __init__(self,initTxt):
        self.txtlen = len(initTxt)
        self.txt = initTxt
        print initTxt,
        sys.stdout.flush()

    def update(self, updateTxt):
        print "\010"+"\010"*self.txtlen+updateTxt,
        sys.stdout.flush()
        self.txtlen = len(updateTxt)
        self.txt = updateTxt

    def end(self,updateTxt=""):
        if updateTxt == "":
            print ""
        else:
            print "\010"+"\010"*self.txtlen+updateTxt

        sys.stdout.flush()

