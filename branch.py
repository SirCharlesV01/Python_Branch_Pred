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
parser.add_argument('s', type = int, help = 'BHT size')
parser.add_argument('bp', type = int, help = 'Predictor type')
parser.add_argument('gh', type = int, help = 'Global history predictor registry size')
parser.add_argument('ph', type = int, help = 'Private history predictor registry size')
args = parser.parse_args()


#-----SIMULATOR CLASS-----#

class simulator:

    def __init__(self, s, bp, gh, ph):
        print('Initializing simulation...')

        #s  =  bth_size
        #bp =  pred_type
        #gh =  global_bp_size
        #ph =  private_bp_size

        self.params = [s, bp, gh, ph] #params are assigned
        self.instruction_dir_list = []   #instruction directions list, to be read from trace file
        self.actual_jump_list = []        #jump taken (T) or not taken (N) list, to be read from trace file
        self.pc_bits = []               #binary values of PC

        print('Loading trace file...')
        for line in sys.stdin:      #Reading the decompressed trace file from pipe, saving columns into corresponding lists
            line = line.partition(' ')
            self.instruction_dir_list.append(int(str.strip(line[0])))   #direction list appended
            self.pc_bits.append(  bin(self.instruction_dir_list[-1])[-int(self.params[0]):]  ) #Last "s" bits of PC appended
            self.actual_jump_list.append(str.strip(line[-1]))      #actual jumps taken list appended

        #-----BUILD THE CORRESPONDING PREDICTOR-----#    
        if self.params[1] == 0:
            self.predictor = bimodal_pred(self.params[0], self.pc_bits, self.actual_jump_list)
        elif self.params[1] == 1:
            self.predictor = private_history_pred(self.params[0], self.params[3], self.pc_bits, self.actual_jump_list)
        elif self.params[1] == 2:
            self.predictor = global_history_pred(gh)
        elif self.params[1] == 3:
            self.predictor = tournament_pred()
        return


    def predict_jump_values(self): #gets the predicted jump values (Taken or Not Taken) from the chosen predictor
        self.predicted_jump_list = self.predictor.get_jumps() 
        print(self.predicted_jump_list[0:20]) #for debbuging
        print(self.actual_jump_list[0:20])
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
            elif aj != pj and pj == 'N':
                stats['IP_NB'] += 1
            else:
                break

        stats['CP_percentage'] = 100*(stats['CP_TB'] + stats['CP_NB'])/(len(self.actual_jump_list))
        return stats


#-----PREDICTOR CLASSES-----#

#Bi-modal predictor:

class bimodal_pred:

    def __init__(self,s,pc_bits,actual_jump_list):
        print('Initializing bimodal predictor...')
        bht_size = 2 ** s #bth size is given by 2^s
        self.pc_bits = pc_bits
        self.actual_jump_list = actual_jump_list
        self.bht = [0] * bht_size #bht initialized with zero vals, (0 = strongly not taken, **defined arbitrarily for simplicity)
        return
    
    def get_jumps(self): #will return the predicted jumps
        print('Predicting jumps...')

        predicted_jumps = []    #predicted jumps list to be returned by function

        for i in range(len(self.actual_jump_list)): #iterates over instructions, predicts jumps and updates BHT according to the actual jumps made
            predicted_jumps.append(self.predict(self.pc_bits[i]))   #computes the i-th prediction
            self.update_bht(i)                                      #updates BHT on i-th jump value

        print('Done!')
        return predicted_jumps
        
    #For the following functions, it is not necesary to check individual bit values, so we will work with int values

    def update_bht(self, i):  #updates the BHT according to the jump value of the i-th instruction
        bits = self.pc_bits[i]
        if self.bht[int(bits,2)] >= 0 and self.bht[int(bits,2)] < 3 and self.actual_jump_list[i] == 'T':
            self.bht[int(bits,2)] += 1
        elif self.bht[int(bits,2)] > 0 and self.bht[int(bits,2)] <= 3 and self.actual_jump_list[i] == 'N':
            self.bht[int(bits,2)] -= 1
        else:
            return

    def predict(self, bits): #returns 'N' or 'T' char, depending on prediction for jump on given PC bits value
        if self.bht[int(bits,2)] < 2: #if value in bht is 0 (strongly NT) or 1 (weakly NT) prediction is NT
            return 'N'
        elif self.bht[int(bits,2)] > 1: #if value in bht is 2 (weakly T) or 3 (strongly T) prediction is T
            return 'T'


#Global history predictor (Gshare):

class global_history_pred:

    def __init__(self,reg_size):
        print('Initializing global history predictor...')
        self.reg_size = reg_size
        return

    def get_jumps(self): #will return the predicted jumps **WIP
        print('Predicting jumps...')
        return



#Private history predictor (Pshare):

class private_history_pred:

    def __init__(self, s, ph, pc_bits, actual_jump_list):
        print("Initializing PShare predictor...")
        self.reg_size = 2 ** s
        self.s = s
        self.ph = ph
        self.pc_bits = pc_bits
        self.actual_jump_list = actual_jump_list
        self.pht = [0] * self.reg_size
        self.bht = [[0] * 2** ph] * self.reg_size #0 being Strongly not taken
        return

    def get_jumps(self):
        print('Predicting jumps...')

        predicted_jumps = []    #predicted jumps list to be returned by function

        for i in range(len(self.actual_jump_list)):
            predicted_jumps.append(self.predict(i))   #computes the i-th prediction
            self.update_bht(i)                    #updates BHT on i-th jump value
            self.update_pht(i)

        print('Done!')
        return predicted_jumps


    def xor (self, i):
        #self.pht[int(self.pc_bits[i],2)] = self.pht[int(self.pc_bits[i],2)] & (2**self.ph -1)
        xor =  self.pht[int(self.pc_bits[i],2)] ^ int(self.pc_bits[i][-self.ph:],2)
        return xor

    def update_bht (self, i):
        pc_bits = self.pc_bits[i]
        pht_index = int(pc_bits,2)
        bht_index0 = self.xor(i)
        bht_index1 = self.pht[pht_index]
        if self.actual_jump_list[i] == 'T' and self.bht[bht_index0][bht_index1] >= 0 and self.bht[bht_index0][bht_index1] < 3:
            self.bht[bht_index0][bht_index1] += 1
        elif self.actual_jump_list[i] == 'N' and self.bht[bht_index0][bht_index1] > 0 and self.bht[bht_index0][bht_index1] <= 3:
            self.bht[bht_index0][bht_index1] -= 1

    def update_pht(self, i):
        pc_bits = self.pc_bits[i]
        pht_index = int(pc_bits,2)

        if self.actual_jump_list[i] == 'T':

            #PHT entry is shifted to the left, inserting a '1' in LSb:
            shifted_val = self.pht[pht_index] << 1
            if shifted_val < 2**self.ph: #if no 1s "drop" from MSb
                self.pht[pht_index] = shifted_val + 1
            else:   #if a 1 "drops" from MSb
                self.pht[pht_index] = shifted_val - 2**self.ph + 1

        else:

            #PHT entry is shiftet to the left, inserting a '0' in LSb:
            shifted_val = self.pht[pht_index] << 1
            if shifted_val < 2**self.ph: #if no 1s "drop" from MSb
                self.pht[pht_index] = shifted_val
            else:   #if a 1 "drops" from MSb
                self.pht[pht_index] = shifted_val - 2**self.ph

    def predict(self, i):
        pc_bits = self.pc_bits[i]
        pht_index = int(pc_bits,2)
        bht_index0 = self.xor(i)
        bht_index1 = self.pht[pht_index]
        prediction = self.bht[bht_index0][bht_index1]
        if prediction > 1:
            return 'T'
        else:
            return 'N'

#Tournament predictor:

class tournament_pred:
    
    def __init__(self):
        print('Initializing tournament predictor...')
        return

    def get_jumps(self): #will return the predicted jumps **WIP
        print('Predicting jumps...')
        return
            

#-----MAIN FUNCTION-----#
def main():

    #Initialize simulation
    sim = simulator(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]))

    #Predict jumps
    sim.predict_jump_values()

    #Print results
    print(sim.get_stats())

if __name__ == "__main__":
        main()