#!/usr/bin/env python

#-----IMPORTS-----#

#Archivo con los predictores
import predictors
#Para la lectura del archivo trace comprimido
import fileinput
#Para los argumentos de la linea de c
import sys

#Tipos de predictores (Para imprimir los resultados)
pred_type = [
    'Bimodal',
    'PShare',
    'GShare',
    'Tournament'
]

#-----FUNCIONES PARA MANEJO DE ARGUMENTOS-----#

#Para obtener los parametros de la linea de comandos, sin importar el orden en que sean ingresados
def get_params():
    s = 0
    bp = 0
    gh = 0
    ph = 0
    for i in range(1,len(sys.argv)-1):
        if sys.argv[i] == '-s':
            s = int(sys.argv[i+1])
        elif sys.argv[i] == '-bp':
            bp = int(sys.argv[i+1])
        elif sys.argv[i] == '-gh':
            gh = int(sys.argv[i+1])
        elif sys.argv[i] == '-ph':
            ph = int(sys.argv[i+1])
    return s, bp, gh, ph

#-----FUNCIONES PARA VERIFICACION DEL FUNCIONAMIENTO-----#

def print_results(s, bp, gh, ph, stats):
    print('------------------------------------------------------------------------\n')
    print('Prediction parameters:\n')
    print('------------------------------------------------------------------------\n')
    print('Branch prediction type: ' + pred_type[bp] + '\n')
    print('BHT size (entries): ' + str(2**s) + '\n')
    print('Global history register size: ' + str(gh) + '\n')
    print('Private history register size: ' + str(ph) + '\n')
    print('------------------------------------------------------------------------\n')
    print('------------------------------------------------------------------------\n')
    print('Simulation results:\n')
    print('------------------------------------------------------------------------\n')
    print('Number of branches: ' + str(stats['Total']) + '\n')
    print('Number of correct predictions of taken branches: ' + str(stats['CP_TB']) + '\n')
    print('Number of incorrect predictions of taken branches: ' + str(stats['IP_TB']) + '\n')
    print('Number of correct predictions of not-taken branches: ' + str(stats['CP_NB']) + '\n')
    print('Number of incorrect predictions of not-taken branches: ' + str(stats['IP_NB']) + '\n')
    print('Percentage of correct predictions: ' + str(round(stats['CP_percentage'],2)) + '\n')
    print('------------------------------------------------------------------------')


#-----MAIN-----#

def main():
    s, bp, gh, ph = get_params()
    #Se inicializa la clase simulador con los parametros dados
    sim = predictors.simulator(s,bp,gh,ph)
    #Se realiza la predicción
    sim.predict_jump_values()
    #Se obtienen las estadisticas
    stats = sim.get_stats()
    #Se imprimen los resultados para su verificacion
    print_results(s,bp,gh,ph,stats)

if __name__ == "__main__":
        main()