import sys #para lectura de stdin (el archivo comprimido)


#-----CLASE SIMULADOR-----#
class simulator:
    #CONSTRUCTOR   
    def __init__(self, s, bp, gh, ph):

        #Significado de los parametros:
            #s  =  bth_size
            #bp =  pred_type
            #gh =  global_bp_size
            #ph =  private_bp_size

        #Se asignan los parametros
        self.params = [s, bp, gh, ph]
        #-----CONSTRUCCION DEL PREDICTOR CORRESPONDIENTE-----#    
        if self.params[1] == 0:
            self.predictor = bimodal_pred(self.params[0])
        elif self.params[1] == 1:
            self.predictor = private_history_pred(self.params[0], self.params[3])
        elif self.params[1] == 2:
            self.predictor = global_history_pred(self.params[0], self.params[2])
        elif self.params[1] == 3:
            self.predictor = tournament_pred(self.params[0], self.params[3], self.params[2])
        return
    #Hace el llamado al predictor escogido
    def predict_jump_values(self):
        self.predicted_jump_list = self.predictor.get_jumps() 
    #Retorna el diccionario de estadísticas correspondiente al predictor escogido
    def get_stats(self):
        return self.predictor.stats

#-----PREDICTORES-----#

class bimodal_pred: #-----BIMODAL-----#
    #CONSTRUCTOR
    def __init__(self,s):
        #Se calcula el tamaño de la tabla de historio (BHT)
        bht_size = 2 ** s
        #Se inicializa el diccionario de estadísticas (Utilizado para recaudar datos del funcionamiento del predictor, no forma parte de la funcionalidad del mismo)
        self.stats = {
            'Total': 0, #Para el total de instrucciones
            'CP_TB': 0, #Correctly predicted taken branches
            'IP_TB': 0, #Incorrectly predicted taken branches
            'CP_NB': 0, #Correctly predicted not taken branches
            'IP_NB': 0, #Incorrectly predicted not taken branches
            'CP_percentage': 0  #Porcentaje de predicciones correctas
        }
        self.s = s
        #Se inicializa la BHT en ceros, con el tamaño dado por bht_size
        self.bht = [0] * bht_size
        return
    #Hace llamados a las demas funciones de la clase para obtener las predicciones y estadísticas, retorna una lista con dichas predicciones
    def get_jumps(self):
        #Para almacenar el valor de los saltos predecidos: 'T' o 'N'
        predicted_jumps = [] 
        #Se itera sobre cada linea del archivo trace
        for line in sys.stdin:
            #Se cuentan las líneas (instrucciones)
            self.stats['Total'] += 1
            #Se separa la linea en los whitespaces
            line = line.partition(' ')
            #Se obtiene el PC correspondiente a la linea (instruccion)
            self.PC = int(str.strip(line[0]))
            #Se recorta el PC para obtener los ultimos "s" bits
            self.pc_bits = bin(self.PC)[-self.s:]
            #Se obtiene el valor real del salto (T o N)
            self.actual_jump = str.strip(line[-1])
            #Se realiza la predicción en base a los ultimos "s" bits del PC actual
            self.prediction = self.predict(self.pc_bits)
            #Se actualiza el valor indexado por los ultimos "s" bits de la bht
            self.update_bht(self.pc_bits) 
            #Se actualiza el diccionario con las estadisticas del predictor
            self.update_stats()
        #Una vez iteradas todas las lineas, se calcula el porcentaje de predicciones correctas
        self.stats['CP_percentage'] = 100*(self.stats['CP_TB'] + self.stats['CP_NB'])/self.stats['Total']
        #Se retornan los saltos predecidos (en caso de que se desee realizar una verificación más exaustiva, más allá de las estadisticas calculadas)
        return predicted_jumps
    #Actualizan los valores del diccionario según el valor de la predicción y el salto real
    def update_stats(self):
        if self.actual_jump == self.prediction and self.prediction == 'T':
            self.stats['CP_TB'] += 1
        elif self.actual_jump != self.prediction and self.prediction == 'T':
            self.stats['IP_NB'] += 1
        elif self.actual_jump == self.prediction and self.prediction == 'N':
            self.stats['CP_NB'] += 1
        elif self.actual_jump != self.prediction and self.prediction == 'N':
            self.stats['IP_TB'] += 1
    #Actualiza la entrada indexada por los ultmos "s" bits del PC dados, segun el valor del salto real
    def update_bht(self, bits):
        if self.bht[int(bits,2)] >= 0 and self.bht[int(bits,2)] < 3 and self.actual_jump == 'T':
            self.bht[int(bits,2)] += 1
        elif self.bht[int(bits,2)] > 0 and self.bht[int(bits,2)] <= 3 and self.actual_jump == 'N':
            self.bht[int(bits,2)] -= 1
        else:
            return
    #Realiza la prediccion segun el valor de la entrada indexada por los ultimos "s" del PC dados
    def predict(self, bits):
        if self.bht[int(bits,2)] < 2:
            return 'N'
        elif self.bht[int(bits,2)] > 1:
            return 'T'

class global_history_pred:  #-----GSHARE-----#
    #CONSTRUCTOR
    def __init__(self, s, gh):
        self.reg_size = 2 ** s
        self.s = s
        self.gh = gh
        #El historial es simplemente un entero, inicializado en cero. (se trataran los LSbs en las funciones del predictor, segun corresponda)
        self.hist = 0
        #Igual que para el predictore bimodal, se inicializa la BHT en ceros, con el tamaño dado por reg_size
        self.bht = [0] * self.reg_size
        #El diccionario de estadisticas
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
        for line in sys.stdin: 
            self.stats['Total'] += 1
            line = line.partition(' ')
            self.PC = int(str.strip(line[0]))
            self.pc_bits = bin(self.PC)[-self.s:]
            #Por medio de la función XOR se indexa la BHT
            self.bht_index = self.xor()
            self.actual_jump = str.strip(line[-1])
            self.prediction = self.predict(self.bht_index)
            self.update_bht(self.bht_index) 
            #A diferencia del predictor bimodal, en este caso debemos actualizar tambien el registro de historia
            self.update_hist()
            self.update_stats()
        self.stats['CP_percentage'] = 100*(self.stats['CP_TB'] + self.stats['CP_NB'])/self.stats['Total']
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
    #Se crea define la función XOR para indexar la BHT
    def xor (self):
        #Se realiza la función XOR entre el historial y los últos "s" bits del PC (se trata con ints para evitar el uso de mascaras)
        xor =  self.hist ^ int(self.pc_bits,2)
        return xor

    def update_bht (self, bht_index):
        bht_index = self.xor()
        if self.actual_jump == 'T' and self.bht[bht_index] >= 0 and self.bht[bht_index] < 3:
            self.bht[bht_index] += 1
        elif self.actual_jump == 'N' and self.bht[bht_index] > 0 and self.bht[bht_index] <= 3:
            self.bht[bht_index] -= 1
    #Actualiza el valor del historial, según la predicción realizada
    def update_hist(self):
        if self.actual_jump == 'T':
            #En caso de tomar el salto, se realiza el shift a la izquierda insertando un 1 en el LSb
            shifted_val = self.hist << 1
            if shifted_val < 2**self.gh: #En caso de que no haya rebase
                self.hist = shifted_val + 1
            else:   #Sí hay rebase
                self.hist = shifted_val - 2**self.gh + 1 #Se resta el rebase
        else:
            #En caso de no tomar el salto, se realiza el shift insertando un 0 en el LSb
            shifted_val = self.hist << 1
            if shifted_val < 2**self.gh: #En caso de que no haya rebase
                self.hist = shifted_val
            else:   #Si hay rebase
                self.hist = shifted_val - 2**self.gh    #se resta el rebase

    def predict(self, bht_index):
        prediction = self.bht[bht_index]
        if prediction > 1:
            return 'T'
        else:
            return 'N'

class private_history_pred: #-----PSHARE-----#
    #CONSTRUCTOR
    def __init__(self, s, ph):
        self.reg_size = 2 ** s
        self.s = s
        self.ph = ph
        #Esta vez tenemos una tabla de historia, del mismo tamaño que la BHT
        self.pht = [0] * self.reg_size
        self.bht = [0] * self.reg_size
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
        for line in sys.stdin:
            self.stats['Total'] += 1
            line = line.partition(' ')
            self.PC = int(str.strip(line[0]))
            self.pc_bits = bin(self.PC)[-self.s:]
            #En este caso también utilizamos la operación XOR para indexar la BHT
            self.bht_index = self.xor()
            self.actual_jump = str.strip(line[-1])
            self.prediction = self.predict(self.bht_index)
            self.update_bht(self.bht_index)
            #Se actualiza la PHT
            self.update_pht(int(self.pc_bits,2))
            self.update_stats()
        self.stats['CP_percentage'] = 100*(self.stats['CP_TB'] + self.stats['CP_NB'])/self.stats['Total']
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
        #En este caso a diferencia del predictor GHSARE, se debe realizar el XOR entre la entrada de la PHT dada por el PC y el mismo PC
        xor =  self.pht[int(self.pc_bits,2)] ^ int(self.pc_bits,2)
        return xor

    def update_bht (self, bht_index):
        bht_index = self.xor()
        if self.actual_jump == 'T' and self.bht[bht_index] >= 0 and self.bht[bht_index] < 3:
            self.bht[bht_index] += 1
        elif self.actual_jump == 'N' and self.bht[bht_index] > 0 and self.bht[bht_index] <= 3:
            self.bht[bht_index] -= 1

    #Funciona de la misma forma que se actualiza el historial en GSHARE, solo que esta vez se generaliza para cualquier entrada de la tabla PHT
    def update_pht(self, pht_index):
        if self.actual_jump == 'T':
            shifted_val = self.pht[pht_index] << 1
            if shifted_val < 2**self.ph:
                self.pht[pht_index] = shifted_val + 1
            else:
                self.pht[pht_index] = shifted_val - 2**self.ph + 1
        else:
            shifted_val = self.pht[pht_index] << 1
            if shifted_val < 2**self.ph:
                self.pht[pht_index] = shifted_val
            else:
                self.pht[pht_index] = shifted_val - 2**self.ph

    def predict(self, bht_index):
        prediction = self.bht[bht_index]
        if prediction > 1:
            return 'T'
        else:
            return 'N'

class tournament_pred:  #-----PREDICTOR DE TORNEO-----#

    '''
    En este caso, se reutilizo gran cantidad del código para los predictores GSHARE y PSHARE (previamente comentado)
    por lo que habra comentarios solo en las secciones donde se introduzca nueva funcionalidad
    correspondiente al predictor de torneo como tal.
    '''
    #CONSTRUCTOR
    def __init__(self, s, ph, gh):
        self.reg_size = 2 ** s
        self.s = s
        #Para el predictor global (GShare):
        self.gh = gh
        self.G_hist = 0
        self.G_bht = [0] * self.reg_size
        #Para el predictor privado (PShare):
        self.ph = ph
        self.P_pht = [0] * self.reg_size
        self.P_bht = [0] * self.reg_size
        #La tabla de metapredictores, del mismo tamaño que BHT y PHT para los predictores GSHARE Y PSHARE
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
        for line in sys.stdin:
            self.stats['Total'] += 1
            line = line.partition(' ')
            self.PC = int(str.strip(line[0]))
            self.pc_bits = bin(self.PC)[-self.s:]
            self.actual_jump = str.strip(line[-1])
            #Se obtiene la indexacion para las tablas BHT de PSHARE y GSHARE por separado
            P_bht_index = self.P_xor()
            G_bht_index = self.G_xor()
            #Solo hay una tabla PHT (correspondiente a PSHARE)
            pht_index = int(self.pc_bits,2)
            #Se obtienen ambas predicciones por separado
            P_pred = self.P_predict(P_bht_index)
            G_pred = self.G_predict(G_bht_index)
            #Se escoge la prediccón final, según la preferencia del metapredictor
            if self.MP_result() == 'P':
                self.prediction = P_pred
            else:
                self.prediction = G_pred
            #Se actualiza el metapredictor, segun ambas predicciones realizadas
            self.update_mp(P_pred, G_pred)
            #Se actualizan las tablas BHT e historiales de los predictores PSHARE y GSHARE
            self.update_G_bht(G_bht_index)
            self.update_G_hist()
            self.update_P_bht(P_bht_index)
            self.update_P_pht(pht_index)
            #Se actualizan las estadisticas
            self.update_stats()
        self.stats['CP_percentage'] = 100*(self.stats['CP_TB'] + self.stats['CP_NB'])/self.stats['Total']
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
    #Obtiene el resultado de la preferencia almacenada en el metapredictor
    def MP_result(self):
        mp_index = int(self.pc_bits,2)
        if self.mp[mp_index] < 2:
            return 'P'
        else:
            return 'G'
    #Actualiza el metapredictor
    def update_mp(self, P_pred, G_pred):
        mp_index = int(self.pc_bits,2)
        #El metapredictor es actualizado solo si las predicciones de GSHARE y PSHARE difieren entre si
        if P_pred != G_pred:
            if P_pred == self.actual_jump and self.mp[mp_index] > 0: #si la prediccion del PSHARE fue acertada
                self.mp[mp_index] -= 1
            elif G_pred == self.actual_jump and self.mp[mp_index] < 3:  #Si la prediccion del GHSARE fue acertada
                self.mp[mp_index] += 1
            else:
                return

    #-----FUNCIONES REUTIlIZADAS-----#
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
        xor =  self.P_pht[int(self.pc_bits,2)] ^ int(self.pc_bits,2)
        return xor

    def G_xor (self):
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
            shifted_val = self.P_pht[pht_index] << 1
            if shifted_val < 2**self.ph:
                self.P_pht[pht_index] = shifted_val + 1
            else: 
                self.P_pht[pht_index] = shifted_val - 2**self.ph + 1
        else:
            shifted_val = self.P_pht[pht_index] << 1
            if shifted_val < 2**self.ph:
                self.P_pht[pht_index] = shifted_val
            else:
                self.P_pht[pht_index] = shifted_val - 2**self.ph

    def update_G_hist(self):
        if self.actual_jump == 'T':
            shifted_val = self.G_hist << 1
            if shifted_val < 2**self.gh:
                self.G_hist = shifted_val + 1
            else:
                self.G_hist = shifted_val - 2**self.gh + 1
        else:
            shifted_val = self.G_hist << 1
            if shifted_val < 2**self.gh:
                self.G_hist = shifted_val
            else:
                self.G_hist = shifted_val - 2**self.gh