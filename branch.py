#!/usr/bin/env python

#-----IMPORTS-----#

#for reading the decompressed trace file
import fileinput
#for help and usage messages from cmd line
import argparse
#for cmd line args
import sys


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

        # print('Loading trace file...')
        # for line in sys.stdin:      #Reading the decompressed trace file from pipe, saving columns into corresponding lists
        #     line = line.partition(' ')
        #     self.instruction_dir_list.append(int(str.strip(line[0])))   #direction list appended
        #     self.pc_bits.append(  bin(self.instruction_dir_list[-1])[-int(self.params[0]):]  ) #Last "s" bits of PC appended
        #     self.actual_jump_list.append(str.strip(line[-1]))      #actual jumps taken list appended

        #-----BUILD THE CORRESPONDING PREDICTOR-----#    
        if self.params[1] == 0:
            self.predictor = bimodal_pred(self.params[0])
        elif self.params[1] == 1:
            self.predictor = private_history_pred(self.params[0], self.params[3])
        elif self.params[1] == 2:
            self.predictor = global_history_pred(self.params[0], self.params[2])
        elif self.params[1] == 3:
            self.predictor = tournament_pred(self.params[0], self.params[3], self.params[2])
        return


    def predict_jump_values(self): #gets the predicted jump values (Taken or Not Taken) from the chosen predictor
        self.predicted_jump_list = self.predictor.get_jumps() 
        print(self.predicted_jump_list[0:20]) #for debbuging
        print(self.actual_jump_list[0:20])
        return

    def get_stats(self): #returns a dictionary with: correctly predicted taken branches, incorrectly predicted taken branches, correctly predicted not taken branches, incorrectly predicted not taken branches
        return self.predictor.stats


#-----PREDICTOR CLASSES-----#

#Bi-modal predictor:

class bimodal_pred:

    def __init__(self,s):
        print('Initializing bimodal predictor...')
        bht_size = 2 ** s #bth size is given by 2^s
        self.stats = {
            'Total': 0,
            'CP_TB': 0,
            'IP_TB': 0,
            'CP_NB': 0,
            'IP_NB': 0,
            'CP_percentage': 0
        }
        self.s = s
        self.bht = [0] * bht_size #bht initialized with zero vals, (0 = strongly not taken, **defined arbitrarily for simplicity)
        return
    
    def get_jumps(self): #will return the predicted jumps

        predicted_jumps = [] 
        print('Predicting jumps...')

        for line in sys.stdin:      #Reading the decompressed trace file from pipe, saving columns into corresponding lists
            self.stats['Total'] += 1
            line = line.partition(' ')
            self.PC = int(str.strip(line[0]))   #direction list appended
            self.pc_bits = bin(self.PC)[-self.s:] #Last "s" bits of PC appended
            self.actual_jump = str.strip(line[-1])      #actual jumps taken list appended
            self.prediction = self.predict(self.pc_bits)
            self.update_bht(self.pc_bits) 
            self.update_stats()             #updates BHT on i-th jump value
            self.stats['CP_percentage'] = 100*(self.stats['CP_TB'] + self.stats['CP_NB'])/self.stats['Total']

        print('Done!')
        return predicted_jumps
        
    #For the following functions, it is not necesary to check individual bit values, so we will work with int values

    def update_stats(self):
        if self.actual_jump == self.prediction and self.prediction == 'T':
            self.stats['CP_TB'] += 1
        elif self.actual_jump != self.prediction and self.prediction == 'T':
            self.stats['IP_NB'] += 1
        elif self.actual_jump == self.prediction and self.prediction == 'N':
            self.stats['CP_NB'] += 1
        elif self.actual_jump != self.prediction and self.prediction == 'N':
            self.stats['IP_TB'] += 1



    def update_bht(self, bits):  #updates the BHT according to the jump value of the i-th instruction
        if self.bht[int(bits,2)] >= 0 and self.bht[int(bits,2)] < 3 and self.actual_jump == 'T':
            self.bht[int(bits,2)] += 1
        elif self.bht[int(bits,2)] > 0 and self.bht[int(bits,2)] <= 3 and self.actual_jump == 'N':
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

    def __init__(self, s, gh):
        print("Initializing GShare predictor...")
        self.reg_size = 2 ** s
        self.s = s
        self.gh = gh
        self.hist = 0 #global history reg initialized with zero val
        self.bht = [0] * self.reg_size #0 being Strongly not taken
        self.stats = {
            'Total': 0,
            'CP_TB': 0,
            'IP_TB': 0,
            'CP_NB': 0,
            'IP_NB': 0,
            'CP_percentage': 0
        }
        return

    def get_jumps(self):


        predicted_jumps = [] 
        print('Predicting jumps...')

        for line in sys.stdin:      #Reading the decompressed trace file from pipe, saving columns into corresponding lists
            self.stats['Total'] += 1
            line = line.partition(' ')
            self.PC = int(str.strip(line[0]))   #direction list appended
            self.pc_bits = bin(self.PC)[-self.s:] #Last "s" bits of PC appended
            self.bht_index = self.xor()
            self.actual_jump = str.strip(line[-1])      #actual jumps taken list appended
            self.prediction = self.predict(self.bht_index)
            self.update_bht(self.bht_index) 
            self.update_hist()
            self.update_stats()             #updates BHT on i-th jump value
            self.stats['CP_percentage'] = 100*(self.stats['CP_TB'] + self.stats['CP_NB'])/self.stats['Total']

        print('Done!')
        return predicted_jumps


    def update_stats(self):
        if self.actual_jump == self.prediction and self.prediction == 'T':
            self.stats['CP_TB'] += 1
        elif self.actual_jump != self.prediction and self.prediction == 'T':
            self.stats['IP_NB'] += 1
        elif self.actual_jump == self.prediction and self.prediction == 'N':
            self.stats['CP_NB'] += 1
        elif self.actual_jump != self.prediction and self.prediction == 'N':
            self.stats['IP_TB'] += 1

    def xor (self):
        #self.pht[int(self.pc_bits[i],2)] = self.pht[int(self.pc_bits[i],2)] & (2**self.ph -1)
        xor =  self.hist ^ int(self.pc_bits,2)
        return xor

    def update_bht (self, bht_index):
        bht_index = self.xor()
        if self.actual_jump == 'T' and self.bht[bht_index] >= 0 and self.bht[bht_index] < 3:
            self.bht[bht_index] += 1
        elif self.actual_jump == 'N' and self.bht[bht_index] > 0 and self.bht[bht_index] <= 3:
            self.bht[bht_index] -= 1

    def update_hist(self):

        if self.actual_jump == 'T':

            #PHT entry is shifted to the left, inserting a '1' in LSb:
            shifted_val = self.hist << 1
            if shifted_val < 2**self.gh: #if no 1s "drop" from MSb
                self.hist = shifted_val + 1
            else:   #if a 1 "drops" from MSb
                self.hist = shifted_val - 2**self.gh + 1

        else:

            #PHT entry is shifted to the left, inserting a '0' in LSb:
            shifted_val = self.hist << 1
            if shifted_val < 2**self.gh: #if no 1s "drop" from MSb
                self.hist = shifted_val
            else:   #if a 1 "drops" from MSb
                self.hist = shifted_val - 2**self.gh

    def predict(self, bht_index):
        prediction = self.bht[bht_index]
        if prediction > 1:
            return 'T'
        else:
            return 'N'



#Private history predictor (Pshare):

class private_history_pred:

    def __init__(self, s, ph):
        print("Initializing PShare predictor...")
        self.reg_size = 2 ** s
        self.s = s
        self.ph = ph
        self.pht = [0] * self.reg_size
        self.bht = [0] * self.reg_size #0 being Strongly not taken
        self.stats = {
            'Total': 0,
            'CP_TB': 0,
            'IP_TB': 0,
            'CP_NB': 0,
            'IP_NB': 0,
            'CP_percentage': 0
        }
        return

    def get_jumps(self):

        predicted_jumps = [] 
        print('Predicting jumps...')

        for line in sys.stdin:      #Reading the decompressed trace file from pipe, saving columns into corresponding lists
            self.stats['Total'] += 1
            line = line.partition(' ')
            self.PC = int(str.strip(line[0]))   #direction list appended
            self.pc_bits = bin(self.PC)[-self.s:] #Last "s" bits of PC appended
            self.bht_index = self.xor()
            self.actual_jump = str.strip(line[-1])      #actual jumps taken list appended
            self.prediction = self.predict(self.bht_index)
            self.update_bht(self.bht_index) 
            self.update_pht(int(self.pc_bits,2))
            self.update_stats()             #updates BHT on i-th jump value
            self.stats['CP_percentage'] = 100*(self.stats['CP_TB'] + self.stats['CP_NB'])/self.stats['Total']

        print('Done!')
        return predicted_jumps



    def update_stats(self):
        if self.actual_jump == self.prediction and self.prediction == 'T':
            self.stats['CP_TB'] += 1
        elif self.actual_jump != self.prediction and self.prediction == 'T':
            self.stats['IP_NB'] += 1
        elif self.actual_jump == self.prediction and self.prediction == 'N':
            self.stats['CP_NB'] += 1
        elif self.actual_jump != self.prediction and self.prediction == 'N':
            self.stats['IP_TB'] += 1



    def xor (self):
        #self.pht[int(self.pc_bits[i],2)] = self.pht[int(self.pc_bits[i],2)] & (2**self.ph -1)
        xor =  self.pht[int(self.pc_bits,2)] ^ int(self.pc_bits,2)
        return xor

    def update_bht (self, bht_index):
        bht_index = self.xor()
        if self.actual_jump == 'T' and self.bht[bht_index] >= 0 and self.bht[bht_index] < 3:
            self.bht[bht_index] += 1
        elif self.actual_jump == 'N' and self.bht[bht_index] > 0 and self.bht[bht_index] <= 3:
            self.bht[bht_index] -= 1

    def update_pht(self, pht_index):
        

        if self.actual_jump == 'T':

            #PHT entry is shifted to the left, inserting a '1' in LSb:
            shifted_val = self.pht[pht_index] << 1
            if shifted_val < 2**self.ph: #if no 1s "drop" from MSb
                self.pht[pht_index] = shifted_val + 1
            else:   #if a 1 "drops" from MSb
                self.pht[pht_index] = shifted_val - 2**self.ph + 1

        else:

            #PHT entry is shifted to the left, inserting a '0' in LSb:
            shifted_val = self.pht[pht_index] << 1
            if shifted_val < 2**self.ph: #if no 1s "drop" from MSb
                self.pht[pht_index] = shifted_val
            else:   #if a 1 "drops" from MSb
                self.pht[pht_index] = shifted_val - 2**self.ph

    def predict(self, bht_index):
        prediction = self.bht[bht_index]
        if prediction > 1:
            return 'T'
        else:
            return 'N'

#Tournament predictor:

class tournament_pred:
    
    def __init__(self, s, ph, gh):
        print('Initializing tournament predictor...')
        self.reg_size = 2 ** s
        self.s = s
        #Para el predictor global (GShare):
        self.gh = gh
        self.G_hist = 0 #global history reg initialized with zero val
        self.G_bht = [0] * self.reg_size #0 being Strongly not taken

        #Para el predictor privado (PShare):
        self.ph = ph
        self.P_pht = [0] * self.reg_size
        self.P_bht = [0] * self.reg_size #0 being Strongly not taken

        #metapredictor
        self.mp = [0] * self.reg_size

        #para almacenar las estadisticas
        self.stats = {
            'Total': 0,
            'CP_TB': 0,
            'IP_TB': 0,
            'CP_NB': 0,
            'IP_NB': 0,
            'CP_percentage': 0
        }

        
        return

    def get_jumps(self):

        predicted_jumps = [] 
        print('Predicting jumps...')

        for line in sys.stdin:      #Reading the decompressed trace file from pipe, saving columns into corresponding lists
            self.stats['Total'] += 1
            line = line.partition(' ')
            self.PC = int(str.strip(line[0]))   #direction list appended
            self.pc_bits = bin(self.PC)[-self.s:] #Last "s" bits of PC appended
            self.actual_jump = str.strip(line[-1])
            P_bht_index = self.P_xor()
            G_bht_index = self.G_xor()
            pht_index = int(self.pc_bits,2)

            P_pred = self.P_predict(P_bht_index)   #computes the i-th prediction
            G_pred = self.G_predict(G_bht_index)

            if self.MP_result() == 'P':
                self.prediction = P_pred
            else:
                self.prediction = G_pred

            self.update_mp(P_pred, G_pred)
            self.update_G_bht(G_bht_index)                    #updates BHT on i-th jump value
            self.update_G_hist()
            self.update_P_bht(P_bht_index)                    #updates BHT on i-th jump value
            self.update_P_pht(pht_index)

            self.update_stats()             #updates BHT on i-th jump value
            self.stats['CP_percentage'] = 100*(self.stats['CP_TB'] + self.stats['CP_NB'])/self.stats['Total']

        print('Done!')
        return predicted_jumps


    def update_stats(self):
        if self.actual_jump == self.prediction and self.prediction == 'T':
            self.stats['CP_TB'] += 1
        elif self.actual_jump != self.prediction and self.prediction == 'T':
            self.stats['IP_NB'] += 1
        elif self.actual_jump == self.prediction and self.prediction == 'N':
            self.stats['CP_NB'] += 1
        elif self.actual_jump != self.prediction and self.prediction == 'N':
            self.stats['IP_TB'] += 1

    def MP_result(self):
        mp_index = int(self.pc_bits,2)
        if self.mp[mp_index] < 2:
            return 'P'
        else:
            return 'G'

    def update_mp(self, P_pred, G_pred):
        mp_index = int(self.pc_bits,2)
        if P_pred != G_pred:
            if P_pred == self.actual_jump and self.mp[mp_index] > 0:
                self.mp[mp_index] -= 1
            elif G_pred == self.actual_jump and self.mp[mp_index] < 3:
                self.mp[mp_index] += 1
            else:
                return

        
    def P_predict(self,bht_index):
        prediction = self.P_bht[bht_index]
        if prediction > 1:
            return 'T'
        else:
            return 'N'

    def G_predict(self, bht_index):
        prediction = self.G_bht[bht_index]
        if prediction > 1:
            return 'T'
        else:
            return 'N'

    def P_xor (self):
        #self.pht[int(self.pc_bits[i],2)] = self.pht[int(self.pc_bits[i],2)] & (2**self.ph -1)
        xor =  self.P_pht[int(self.pc_bits,2)] ^ int(self.pc_bits,2)
        return xor

    def G_xor (self):
        #self.pht[int(self.pc_bits[i],2)] = self.pht[int(self.pc_bits[i],2)] & (2**self.ph -1)
        xor =  self.G_hist ^ int(self.pc_bits,2)
        return xor

    def update_P_bht (self, bht_index):
        bht_index = self.P_xor()
        if self.actual_jump == 'T' and self.P_bht[bht_index] >= 0 and self.P_bht[bht_index] < 3:
            self.P_bht[bht_index] += 1
        elif self.actual_jump == 'N' and self.P_bht[bht_index] > 0 and self.P_bht[bht_index] <= 3:
            self.P_bht[bht_index] -= 1

    def update_G_bht (self, bht_index):
        bht_index = self.G_xor()
        if self.actual_jump == 'T' and self.G_bht[bht_index] >= 0 and self.G_bht[bht_index] < 3:
            self.G_bht[bht_index] += 1
        elif self.actual_jump == 'N' and self.G_bht[bht_index] > 0 and self.G_bht[bht_index] <= 3:
            self.G_bht[bht_index] -= 1

    def update_P_pht(self, pht_index):
        

        if self.actual_jump == 'T':

            #PHT entry is shifted to the left, inserting a '1' in LSb:
            shifted_val = self.P_pht[pht_index] << 1
            if shifted_val < 2**self.ph: #if no 1s "drop" from MSb
                self.P_pht[pht_index] = shifted_val + 1
            else:   #if a 1 "drops" from MSb
                self.P_pht[pht_index] = shifted_val - 2**self.ph + 1

        else:

            #PHT entry is shifted to the left, inserting a '0' in LSb:
            shifted_val = self.P_pht[pht_index] << 1
            if shifted_val < 2**self.ph: #if no 1s "drop" from MSb
                self.P_pht[pht_index] = shifted_val
            else:   #if a 1 "drops" from MSb
                self.P_pht[pht_index] = shifted_val - 2**self.ph

    def update_G_hist(self):

        if self.actual_jump == 'T':

            #PHT entry is shifted to the left, inserting a '1' in LSb:
            shifted_val = self.G_hist << 1
            if shifted_val < 2**self.gh: #if no 1s "drop" from MSb
                self.G_hist = shifted_val + 1
            else:   #if a 1 "drops" from MSb
                self.G_hist = shifted_val - 2**self.gh + 1

        else:

            #PHT entry is shifted to the left, inserting a '0' in LSb:
            shifted_val = self.G_hist << 1
            if shifted_val < 2**self.gh: #if no 1s "drop" from MSb
                self.G_hist = shifted_val
            else:   #if a 1 "drops" from MSb
                self.G_hist = shifted_val - 2**self.gh
    

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