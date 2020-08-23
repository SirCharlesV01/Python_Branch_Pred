#for cmd line args
import sys

#numbers stuff we might need
import numpy
import scipy

#-----CACHE CLASS-----#
class cache:

    #Constructor
    def __init__(self, s, bp, gh, ph):

        #bth_size = s
        #pred_type = bp
        #global_bp_size = gh
        #private_bp_size = ph

        self.params = [s, bp, gh, ph]

    #-----PREDICTORS-----#
    def bimodal(self):
        print("bimodal predictor")
        return

    def history_global(self):
        print("global history predictor")
        return

    def history_private(self):
        print("private history predictor")
        return

    def tournament(self):
        print("tournament predictor")
        return

    def print_params(self):
        for p in self.params:
            print('\n' + str(p))



#-----MAIN FUNCTION-----#
def main():
    
    sim_cache = cache(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    sim_cache.print_params()
    

if __name__ == "__main__":
    main()