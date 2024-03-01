import numpy as np
import random
import math
from matplotlib.colors import ListedColormap


class sociedad_Axelrod:
    """
    Define completely the Axelrod model and implement some variations to be 
    more realistic 
    
    rows = rows of the society matrix
    cols = columns of the society matrix
    f = number of traits of each subject/individual
    q = number of values a trait can take
    tolerance = tolerance comparing values (must be between 0 and 1)
    alpha = sociability constant (between 0 and 1, with 0 the least sociable, i.e., original Axelrod model)
    shifts = relative positions of possible neighbors
    dimension = society's dimension (list or matrix)
    version = model's version to be considered (basic or with extras)
    """
    
    
    def __init__(self, rows = 3, cols = 3, f = 4, q = 10, tolerance = 0.15, alpha = 0, shifts = np.array([(0, 1), (1, 0), (0, -1), (-1, 0)]), dimension = 2, version = 0):
        
        self.rows = rows
        self.cols = cols
        self.f = f
        self.q = q
        self.tolerance = tolerance
        self.alpha = alpha
        self.shifts = shifts
        self.dimension = dimension
        self.version = version
        self.contador = 0
        self.nods = [] #to study de nodes density time evolution
        self.nods_max = self.cols*(self.rows - 1) + self.rows*(self.cols - 1)
        #determine number of bits required to generate later a random integer
        bits = math.ceil(math.log2(self.q+1)) 
        #generate a super agent (only for version 5)
        self.super_agent = np.zeros(self.f)
        if version >= 5:
            if self.q == 1:
                for i in range(self.f):
                    self.super_agent[i] = (random.getrandbits(bits) % (self.q))
            else:
                for i in range(self.f):
                    self.super_agent[i] = (random.getrandbits(bits) % (self.q))/(self.q-1)
        

        
        
        #creating societies of different dimension
        
        #unidimensional
        if self.dimension == 1:
            #society matrix (1D)
            if self.q == 1:
                self.matrix = np.zeros((self.rows*self.cols, self.f))
                for i in range(self.rows*self.cols):
                    for j in range(self.f):
                        self.matrix[i][j] = random.getrandbits(bits) % (self.q)
            else:
                self.matrix = np.zeros((self.rows*self.cols, self.f))
                for i in range(self.rows*self.cols):
                    for j in range(self.f):
                        self.matrix[i][j] = (random.getrandbits(bits) % (self.q))/(self.q-1)
                        
            #neighbors' matrix            
            if self.version < 7:
                
                self.neighbors = np.empty(self.rows*self.cols, dtype=object)
                
                for i in range(self.rows*self.cols):
                    indices = [i + shift for shift in self.shifts]
                    indices = [idx for idx in indices if idx >= 0 and idx < self.rows*self.cols]
                    self.neighbors[i] = indices

                
            else: #redes complejas
                print('Aun por implementar')
                
                
        #bidimensional 
        
        elif self.dimension == 2:
            #society matrix (2D)
            if self.q == 1:
                self.matrix = np.zeros((self.rows, self.cols, self.f))
                for i in range(self.matrix.shape[0]):
                    for j in range(self.matrix.shape[1]):
                        for k in range(len(self.matrix[0,0])):
                            self.matrix[i,j][k] = random.getrandbits(bits) % (self.q)
            else:
                self.matrix = np.zeros((self.rows, self.cols, self.f))
                for i in range(self.matrix.shape[0]):
                    for j in range(self.matrix.shape[1]):
                        for k in range(len(self.matrix[0,0])):
                            self.matrix[i,j][k] = (random.getrandbits(bits) % (self.q))/(self.q-1)
            
            #neighbors' matrix           
            if self.version < 7:
                
                self.neighbors = np.empty((self.rows, self.cols), dtype=object)
                
                for i in range(self.rows):
                    for j in range(self.cols):
                        indices = self.shifts + np.array([i, j])
                        indices = indices[np.all(indices >= 0, axis=1)]
                        indices = indices[np.all(indices < (self.rows, self.cols), axis=1)]
                        self.neighbors[i, j] = list(map(tuple, indices))
                
                
            else: #redes complejas
                print('Si venga')
                
        else: 
            print('Si venga')
        
            
    def random_num(self, top:int):
        bits = math.ceil(math.log2(top + 1)) 
        random_index = (random.getrandbits(bits) % (top))
        return random_index
      

    def elegir_vecino(self, activo:int):
        if self.dimension == 1:
            random_index : int = self.random_num(len(self.neighbors[activo]))
            vecino_index : int = self.neighbors[activo][random_index]
            
        elif self.dimension == 2:
            row, col = divmod(activo, self.cols) #tuple with row and col of the active individual
            random_index : int = self.random_num((len(self.neighbors[row][col])))
            vecino_index : tuple = self.neighbors[row][col][random_index] #random neighbor
    
        return vecino_index
    
    
    def exchange(self, active, rndidx, neighbor=None):
        
        if neighbor: #classical cultural exchange
            self.matrix[active][rndidx] = self.matrix[neighbor][rndidx]
            
        else: #relaxed cultural exchange
            cultural_exchange = (self.random_num(self.tolerance*200))/100
            
            if cultural_exchange > 0.15:
                cultural_exchange = self.tolerance - cultural_exchange 
                
            self.matrix[active][rndidx] += cultural_exchange 
            
            if self.matrix[active][rndidx] < 0:
                self.matrix[active][rndidx] = 0
                
            elif self.matrix[active][rndidx] > 1:
                self.matrix[active][rndidx] = 1
            
        return self.matrix[active][rndidx]
    
      
    def interaccion(self):
        if self.dimension == 1:
            for activo in range(self.rows*self.cols):
                vecino : tuple = self.elegir_vecino(activo)
                lista_indexes :list = [num for num in range(self.f) if self.matrix[activo][num] != self.matrix[vecino][num]]
                w : int = 0
                if lista_indexes:
                    random_index : int = lista_indexes[self.random_num(len(lista_indexes))]
                    w : int = np.sum(self.matrix[vecino] == self.matrix[activo])/self.f
                    if self.random_num(100)/100 < w:
                        self.exchange(activo, random_index, vecino)
                        
        
        elif self.dimension == 2:
            for activo in range(self.rows*self.cols): #avoid a double for loop
                vecino: tuple = self.elegir_vecino(activo)
                activo: tuple = divmod(activo, self.cols)
                #different traits between active and passive individuals
                lista_indexes : list = [num for num in range(self.f) if (self.matrix[activo][num] != self.matrix[vecino][num])] 
                w : int = 0 #probability of interaction
                
                if self.version == 0: #Axelrod model
                    if lista_indexes:
                        random_index : int = lista_indexes[self.random_num(len(lista_indexes))]
                        w : int = np.sum(self.matrix[vecino] == self.matrix[activo])/self.f
                        if self.random_num(100)/100 < w:
                            self.exchange(activo, random_index, vecino)
                          
                            
                #extras
                elif self.version > 0:
                    if lista_indexes:
                        random_index = lista_indexes[self.random_num(len(lista_indexes))]
                        w_ax = np.sum(self.matrix[vecino] == self.matrix[activo])/self.f
                        
                        if self.version == 1: #cultural drift
                            
                            w = w_ax
                            if self.random_num(100)/100 < w:
                                self.exchange(activo, random_index, vecino)
                                
                            if self.random_num(400)/400 < 1/100: 
                                random_index = self.random_num(self.f)
                                self.matrix[activo][random_index] = self.random_num(self.q)/(self.q - 1)
                        
                        #Add a sociability improve with time to a certain maximum, then returns to Axelrod basic model
                        if self.version == 2:
                            nods = self.active_nods(self.matrix) #active nodes in that time
                            w_extra = (nods/self.nods_max) # alpha*(1-n^3)
                            w = 1/(1-self.alpha)*(w_ax + self.alpha*w_extra)
                        
                            if self.random_num(100)/100 < w:
                                self.exchange(activo, random_index, vecino)
                        
                        
                        if 3 <= self.version <= 4: 
                            w_mod= np.sum(abs(self.matrix[vecino] - self.matrix[activo]) <= self.tolerance)/self.f
                            w = w_mod
                            if self.version == 3: #substitute the deltas on w for a more relaxed condition
                                if self.random_num(100)/100 < w:
                                    self.exchange(activo, random_index, vecino)
                                    
                            else: #cultural exchange relaxed
                                if self.random_num(100)/100 < w:
                                    self.exchange(activo, random_index) 
                                    
                                    
                        if self.version == 5: #superagent
                            w_sa = 0.80
                            
                            if self.random_num(100)/100 < w_sa:
                                lista_indexes = [num for num in range(self.f) if (self.matrix[activo][num] != self.super_agent[num])] 
                                
                                if lista_indexes:
                                    random_index = lista_indexes[self.random_num(len(lista_indexes))]
                                    self.matrix[activo][random_index] = self.super_agent[random_index]
                                    
                            else:
                                w = w_ax
                                if self.random_num(100)/100 < w:
                                    self.exchange(activo, random_index, vecino)
                        
                        
                        if self.version == 6: #superagent and cultural exchange relaxed
                            w_sa = 0.10
                            
                            if self.random_num(100)/100 < w_sa:
                                lista_indexes = [num for num in range(self.f) if (self.matrix[activo][num] != self.super_agent[num])] 
                                
                                if lista_indexes:
                                    random_index = lista_indexes[self.random_num(len(lista_indexes))]
                                    self.exchange(activo, random_index)
                                    
                            else:
                                w = w_ax
                                if self.random_num(100)/100 < w:
                                    self.exchange(activo, random_index) 
        return self.matrix
                            

    def moda(self, sociedad:np.ndarray): #generate a dictionary with all cultures and its frequencies in stationary society
        if self.dimension == 1:
            count_cults : dict = {}
            colors = {}
              
            for element in range(self.rows*self.cols):
                element_str = np.array2string(sociedad[element], separator=',')
                  
                if element_str in count_cults:
                    count_cults[element_str] += 1
              
                else:
                    count_cults[element_str] = 1
                    
              
            max_count = max(count_cults.values())
            mode_list = [element for element, count in count_cults.items() if count == max_count]
            mode_array = np.array([eval(element) for element in mode_list]) #con eval() convertimos el str a dato de numpy 
            
            return mode_array, max_count, count_cults
        
            
        if self.dimension == 2:
            count_cults : dict = {}
            colors = {}
              
            for element in range(self.rows*self.cols):
                row, col = divmod(element, self.cols)
                element_str = np.array2string(sociedad[row, col], separator=',')
                  
                if element_str in count_cults:
                    count_cults[element_str] += 1
              
                else:
                    count_cults[element_str] = 1
                    
                    # assign a random color to new elements
                    color = np.random.rand(3,)#tupla rgb
                    colors[element_str] = color
              
            max_count = max(count_cults.values())
            mode_list = [element for element, count in count_cults.items() if count == max_count]
            mode_array = np.array([eval(element) for element in mode_list]) #con eval() convertimos el str a dato de numpy 
            
            # create a colormap to be used in the plot
            colormap = ListedColormap(colors.values())

            return mode_array, max_count, count_cults, colormap
    
    
    def active_nods(self, sociedad): 
        
        nodos = 0
        
        if self.dimension == 1:
            
            for activo in range(self.rows*self.cols):
                red = self.neighbors[activo]
                for k in range(len(red)):
                    compare = sociedad[activo] - sociedad[red[k]]
                    
                    if 0 < np.count_nonzero(compare) < len(compare):
                        nodos += 1
        else:
            for activo in range(self.rows*self.cols):
                row, col = divmod(activo, self.cols) #optimizable, función un poco lenta en comparacion a otras !!!
                red = self.neighbors[row][col]
                
                for k in range(len(red)):
                    row_vecino, col_vecino = red[k]
                    if self.cols*row_vecino + col_vecino > activo: #avoid repeated agents
                        compare = sociedad[row, col] - sociedad[row_vecino, col_vecino]
                        
                        if 0 < np.count_nonzero(compare) < len(compare):
                            nodos += 1
                    
            self.nods.append(nodos)
        return nodos
    
    
    def run_simulation(self): #run the simulations til the stationary state it is reached. 
        flag = True
        self.contador = 0
        if self.version == 0:
            while flag:
                sociedad = self.interaccion()
                self.contador += 1
                verify = self.active_nods(sociedad)
                if verify == 0:
                    flag = False
        elif 0 < self.version < 8:
            while flag:
                sociedad = self.interaccion()
                self.contador += 1
                verify = self.active_nods(sociedad)/self.nods_max
                if verify < (10*self.nods_max)/(100*self.nods_max):
                    flag = False
            
        else: #redes complejas
            print('Por implementar')
        
        return sociedad