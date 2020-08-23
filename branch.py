#!/usr/bin/env python

#-----IMPORTS-----#

#for reading the decompressed trace file
import fileinput
#for help and usage messages from cmd line
import argparse
#for cmd line args
import sys
#numbers stuff we might need
import numpy
import scipy

#-----PARSER SETUP-----#

#program description
parser = argparse.ArgumentParser(description='Simulates different branch predictors based on user defined cache parameters')
#arguments
parser.add_argument('s', type = int, help = 'BTH table size')
parser.add_argument('bp', type = int, help = 'Predictor type')
parser.add_argument('gh', type = int, help = 'Global history predictor registry size')
parser.add_argument('ph', type = int, help = 'Private history predictor registry size')
args = parser.parse_args()


#-----CACHE CLASS-----#

class cache:

    def __init__(self, s, bp, gh, ph):
        print('Initializing cache...')

        #s  =  bth_size
        #bp =  pred_type
        #gh =  global_bp_size
        #ph =  private_bp_size

        self.params = [s, bp, gh, ph] #params are assigned

        #-----BUILD THE CORRESPONDING PREDICTOR-----#    
        if self.params[1] == '0':
            self.predictor = bimodal_pred()
        elif self.params[1] == '1':
            self.predictor = global_history_pred(gh)
        elif self.params[1] == '2':
            self.predictor = private_history_pred(ph)
        elif self.params[1] == '3':
            self.predictor = tournament_pred()
        else:
            return



#-----PREDICTOR CLASSES-----#

class bimodal_pred:

    def __init__(self):
        print('Initializing bimodal predictor...')
        return

class global_history_pred:

    def __init__(self, reg_size):
        print('Initializing global history predictor...')
        self.reg_size = reg_size
        return

class private_history_pred:

    def __init__(self, reg_size):
        print('Initializing private history predictor...')
        self.reg_size = reg_size
        return

class tournament_pred:
    
    def __init__(self):
        print('Initializing tournament predictor...')
        return

#-----SIMULATOR CLASS-----#

class simulator:
    def __init__(self):
        print('Initializing simulation...')

        self.instruction_dir = []   #instruction directions list, to be read from trace file
        self.jump_taken = []        #jump taken (T) or not taken (N) list, to be read from trace file

        print('Loading trace file...')
        for line in sys.stdin:      #Reading the decompressed trace file from pipe, saving columns into corresponding lists
            line = line.partition(' ')
            self.instruction_dir.append(line[0])
            self.jump_taken.append(line[-1])
        return





#-----MAIN FUNCTION-----#
def main():
    #Initialize cache
    cache_instance = cache(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])

    #Initialize simulation
    sim = simulator()

if __name__ == "__main__":
        main()