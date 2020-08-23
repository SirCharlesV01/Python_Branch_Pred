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
parser = argparse.ArgumentParser(description='Simulates different jump predictors based on user defined cache parameters')
#arguments
parser.add_argument('s', type = int, help = 'BTH table size')
parser.add_argument('bp', type = int, help = 'Predictor type')
parser.add_argument('gh', type = int, help = 'Global history predictor registry size')
parser.add_argument('ph', type = int, help = 'Private history predictor registry size')
args = parser.parse_args()


#-----CACHE CLASS-----#

class cache:

    #-----CONSTRUCTOR-----#

    def __init__(self, s, bp, gh, ph):
        print('Initializing cache...')

        #s  =  bth_size
        #bp =  pred_type
        #gh =  global_bp_size
        #ph =  private_bp_size

        self.params = [s, bp, gh, ph] #params are assigned

        self.instruction_dir = []   #instruction directions list, to be read from trace file
        self.jump_taken = []        #jump taken (T) or not taken (N) list, to be read from trace file

        print('Reading trace file...')
        for line in sys.stdin:      #Reading the decompressed trace file from pipe, saving columns into corresponding lists
            line = line.partition(' ')
            self.instruction_dir.append(line[0])
            self.jump_taken.append(line[-1])
            

        return


    #-----PREDICTORS-----#

    def bimodal(self):
        print("Running bimodal predictor simulation...")
        return

    def history_global(self):
        print("Running global history predictor simulation...")
        return

    def history_private(self):
        print("Running private history predictor simulation...")
        return

    def tournament(self):
        print("Running tournament predictor simulation...")
        return


    #-----SIMULATION RELATED FUNCTIONS-----#

    def run_simulation(self):       #Switch to the correct predictor according to the user defined "bp" parameter
        if self.params[1] == '0':
            self.bimodal()
        elif self.params[1] == '1':
            self.history_global()
        elif self.params[1] == '2':
            self.history_private()
        elif self.params[1] == '3':
            self.tournament()
        else:
            return



#-----MAIN FUNCTION-----#
def main():
    #Initialize cache
    sim_cache = cache(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])

    #run simulation
    sim_cache.run_simulation()

if __name__ == "__main__":
        main()