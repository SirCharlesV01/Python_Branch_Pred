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

    def get_jumps(self): #will return the predicted jumps **WIP
        print('Predicting jumps...')
        return

class global_history_pred:

    def __init__(self, reg_size):
        print('Initializing global history predictor...')
        self.reg_size = reg_size
        return

    def get_jumps(self): #will return the predicted jumps **WIP
        print('Predicting jumps...')
        return

class private_history_pred:

    def __init__(self, reg_size):
        print('Initializing private history predictor...')
        self.reg_size = reg_size
        return

    def get_jumps(self): #will return the predicted jumps **WIP
        print('Predicting jumps...')
        return

class tournament_pred:
    
    def __init__(self):
        print('Initializing tournament predictor...')
        return

    def get_jumps(self): #will return the predicted jumps **WIP
        print('Predicting jumps...')
        return





#-----SIMULATOR CLASS-----#

class simulator:

    predicted_jump_list = []    #list of predicted jump values, filled by the predict_jump_values() function.

    def __init__(self, cache):
        print('Initializing simulation...')

        self.cache = cache

        self.instruction_dir_list = []   #instruction directions list, to be read from trace file
        self.actual_jump_list = []        #jump taken (T) or not taken (N) list, to be read from trace file

        print('Loading trace file...')
        for line in sys.stdin:      #Reading the decompressed trace file from pipe, saving columns into corresponding lists
            line = line.partition(' ')
            self.instruction_dir_list.append(str.strip(line[0]))   #direction list appended
            self.actual_jump_list.append(str.strip(line[-1]))      #actual jumps taken list appended
        return

    def predict_jump_values(self):
        self.predicted_jump_list = self.cache.predictor.get_jumps() #will return the predicted jump values (Taken or Not Taken) from the chosen predictor **WIP
        return

    def get_stats(self): #returns a dictionary with: correctly predicted taken branches, incorrectly predicted taken branches, correctly predicted not taken branches, incorrectly predicted not taken branches
        stats = {
            'CP_TB': 0,
            'IP_TB': 0,
            'CP_NB': 0,
            'IP_NB': 0,
            'CP_percentage': 0
        }
        print('Calculating stats...')
        for (aj, pj) in zip(self.actual_jump_list, self.predicted_jump_list):
            if aj == pj and pj == 'T':
                stats['CP_TB'] += 1
            elif aj != pj and pj == 'T':
                stats['IP_TB'] += 1
            elif aj == pj and pj == 'N':
                stats['CP_NB'] += 1
            elif aj == pj and pj == 'N':
                stats['IP_NB'] += 1
            else:
                break

        stats['CP_percentage'] = (len(self.actual_jump_list))*100/(stats['CP_TB'] + stats['CP_NB'])

        return stats
        





#-----MAIN FUNCTION-----#
def main():
    #Initialize cache
    cache_instance = cache(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])

    #Initialize simulation
    sim = simulator(cache_instance)

    #Predict jumps
    sim.predict_jump_values()

    #Print results
    sim.get_stats()

if __name__ == "__main__":
        main()