import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors

class box_graph:
  """
  Graficar el mapa de cuadrícula, con las líneas que separan a cada
  individuo tomando un color en escala de grises dependiendo de cuanto 
  tengan en comun. 

  fig = plot donde se va a representar
  ax = subplot donde se va a representar 
  matrix = sociedad que se esté tratando 
  """

  def __init__(self, fig, ax, matrix = np.zeros((3,3))):
    self.fig = fig
    self.ax = ax
    self.matrix = matrix
    self.cmap = colors.LinearSegmentedColormap.from_list('grayscale', [(0, 'black'), (1, 'white')]) #mapa de color
    self.similarity_matrix = np.zeros((2*self.matrix.shape[0]-1, 2*self.matrix.shape[1]-1))


  def map_similarity_to_color(self, similarity_value, array_len): #asignar color al número de traits en común
    return self.cmap(similarity_value / array_len)


  def similarity(self, a, b):
    return np.sum(a == b)


  def sim_matrix_calc(self): 
    for i in range(self.matrix.shape[0]):
      for j in range(self.matrix.shape[1]):
        if j == self.matrix.shape[1]-1 and i != self.matrix.shape[0]-1: #ultima columna no hay nadie a la derecha
          similarity_value_down = self.similarity(self.matrix[i,j], self.matrix[i+1, j])
          self.similarity_matrix[2*i+1, 2*j] = similarity_value_down
        elif i == self.matrix.shape[0]-1 and j != self.matrix.shape[1]-1: #ultima fila no hay nadie debajo
          similarity_value_right = self.similarity(self.matrix[i,j], self.matrix[i, j+1])
          self.similarity_matrix[2*i, 2*j+1] = similarity_value_right
        elif i == self.matrix.shape[0]-1 and j == self.matrix.shape[1]-1: #esquina inferior derecha, todo pintado ya
          break
        else: #cualquier otro caso (hay línea a la derecha y debajo)
          similarity_value_right = self.similarity(self.matrix[i,j], self.matrix[i, j+1])
          similarity_value_down = self.similarity(self.matrix[i,j], self.matrix[i+1, j])

          self.similarity_matrix[2*i, 2*j+1] = similarity_value_right
          self.similarity_matrix[2*i+1, 2*j] = similarity_value_down
    return self.similarity_matrix




  def ploteo(self):

    #ploteo de las líneas
    for i in range(2*self.matrix.shape[0]-1):
      for j in range(self.matrix.shape[0]):
        if i%2 == 0 and 2*j+1 < self.similarity_matrix.shape[0]: #filas pares, se pinta línea vertical a la derecha
          line_color = self.map_similarity_to_color(self.sim_matrix_calc()[i, 2*j+1], len(self.matrix[0,0]))
          self.ax.axvline(j+1, ymin=(self.matrix.shape[0]-1-i/2)/self.matrix.shape[0], ymax=(self.matrix.shape[0]-i/2)/self.matrix.shape[0], color=line_color)
        
        elif i%2 != 0 and 2*j < 2*self.similarity_matrix.shape[0]-1: #filas impares, se pinta línea horizontal debajo
          line_color = self.map_similarity_to_color(self.sim_matrix_calc()[i, 2*j], len(self.matrix[0,0]))
          self.ax.axhline(self.matrix.shape[0] - (i+1)/2, xmin=j/self.matrix.shape[0], xmax=(j+1)/self.matrix.shape[0], color=line_color)
        
        else: #paramos justo en el elemento de la esquina inferior derecha, todo pintado ya
          break
      
    # Ajustar los límites de los ejes y maquillar un poco las graficas
    self.ax.set_xlim([0, self.matrix.shape[0]])
    self.ax.set_ylim([0, self.matrix.shape[0]])
    self.ax.minorticks_on()
    self.ax.get_xaxis().set_visible(False)
    self.ax.get_yaxis().set_visible(False)

    
  def ploteo2(self):

    #ploteo de las líneas
    for i in range(2*self.matrix.shape[0]-1):
      for j in range(self.matrix.shape[0]):
        if i%2 == 0 and 2*j+1 < self.similarity_matrix.shape[0]: #filas pares, se pinta línea vertical a la derecha
          line_color = self.map_similarity_to_color(self.sim_matrix_calc()[i, 2*j+1], len(self.matrix[0,0]))
          self.ax.axvline(j+1, ymin=(self.matrix.shape[0]-1-i/2)/self.matrix.shape[0], ymax=(self.matrix.shape[0]-i/2)/self.matrix.shape[0], color=line_color)
        
        elif i%2 != 0 and 2*j < 2*self.similarity_matrix.shape[0]-1: #filas impares, se pinta línea horizontal debajo
          line_color = self.map_similarity_to_color(self.sim_matrix_calc()[i, 2*j], len(self.matrix[0,0]))
          self.ax.axhline(self.matrix.shape[0] - (i+1)/2, xmin=j/self.matrix.shape[0], xmax=(j+1)/self.matrix.shape[0], color=line_color)
        
        else: #paramos justo en el elemento de la esquina inferior derecha, todo pintado ya
          break
      
    # Ajustar los límites de los ejes y maquillar un poco las graficas
    self.ax.set_xlim([0, self.matrix.shape[0]])
    self.ax.set_ylim([0, self.matrix.shape[0]])
    self.ax.minorticks_on()
    self.ax.get_xaxis().set_visible(False)
    self.ax.get_yaxis().set_visible(False)

    # Crear el colorbar
    norm = plt.Normalize(vmin=0, vmax=len(self.matrix[0,0]))
    sm = plt.cm.ScalarMappable(cmap=self.cmap, norm=norm)
    sm.set_array([])
    cbar = self.fig.colorbar(sm, ax=self.ax, fraction=0.046, pad=0.04)
    cbar.set_label('Similar traits between neighbors', rotation=270, labelpad=15)
    
    
        