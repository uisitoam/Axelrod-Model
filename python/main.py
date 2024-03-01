import numpy as np
import matplotlib.pyplot as plt
import pylab as py
from scipy.interpolate import make_interp_spline
from sociedad import sociedad_Axelrod 
from boxgraph import box_graph
import time
from bs4 import BeautifulSoup  
import requests
import io
import base64

colores = ['#FF0000', '#FF9B00', '#F5DE00', '#51FF53', '#00A902', '#00FF8F', 
           '#00F5E6', '#00B2FF', '#0032FF', '#B900FF', '#8700FF', '#FF86F6', 
           '#EA00D9', '#B00070', '#A4A4A4']


"""
First of all, we're defining some helpful functions, but not neccesary for the 
execution of the simulation or to obtain results
"""

inicio = time.time() #get initial time

#obtain the execution time (in a fancy way look)
def timer(segundos):
    if segundos < 60:
        text = f'{int(segundos)} segundos'
    elif segundos < 3600:
        minutos = int(segundos/60)
        segundos -= minutos*60
        text = f'{minutos} minutos y {int(segundos)} segundos'
    else:
        horas = int(segundos/3600)
        segundos -= horas*3600
        minutos = int(segundos/60)
        segundos -= minutos*60
        text = f'{horas} horas, {minutos} minutos y {int(segundos)} segundos'
    return text


#telegram bot that update about how's the run going
def bot_texter(bot_message, file_data=None, file_name=None):
    
    bot_token = '6284133570:AAEAT9T74vaNFiJrY-wPdXgZD3Js3smMOI0'
    bot_chatID = '1018886244'
    
    if file_data is not None and file_name is not None: #send a picture
        send_file = 'https://api.telegram.org/bot' + bot_token + '/sendDocument?chat_id=' + bot_chatID
        file_bytes = io.BytesIO(file_data)
        response = requests.post(send_file, files={'document': (file_name, file_bytes)})
    else: #send a text message
        send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message
        response = requests.get(send_text)

    return response



"""
Where the program of interest really begins
"""


#positions of possible neighbors

shifts1d = np.array([1, -1]) #unidimensional
shifts = np.array([(0, 1), (1, 0), (0, -1), (-1, 0)]) #bidimensional case 1
shifts_more = np.array([(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]) #bidimensional case 2



"""
Let's take a look at the society. We'll plot the two subjects in the same color if their arrays 
are equal (they have the same culture). Also for small dimension society it's useful to plot it 
like a grid, where the line between two subjects is in grayscale color, based on how similar 
the subjects are (black for them being completely different and white for completely equal)
"""

"""
sociedad1 = sociedad_Axelrod(rows = 40, cols = 40, f = 4, q = 5, shifts = shifts_more) #monocultural
sociedad2 = sociedad_Axelrod(rows = 40, cols = 40, f = 4, q = 23, shifts = shifts_more) #phase transition
sociedad3 = sociedad_Axelrod(rows = 40, cols = 40, f = 4, q = 50, shifts = shifts_more) #multicultural


fig1, ax1 = plt.subplots(2, 3, figsize=(12, 18))

final_society1 = sociedad1.run_simulation()
final_society2 = sociedad2.run_simulation()
final_society3 = sociedad3.run_simulation()


#grid

sociedad_final1 = box_graph(fig1, ax1[1,0], final_society1)
sociedad_final1.ploteo()
sociedad_final2 = box_graph(fig1, ax1[1,1], final_society2)
sociedad_final2.ploteo()
sociedad_final3 = box_graph(fig1, ax1[1,2], final_society3)
sociedad_final3.ploteo2()


#colormap

ax1[0,0].imshow(final_society1, cmap=sociedad1.moda(final_society1)[3])
ax1[0,0].get_xaxis().set_visible(False)
ax1[0,0].get_yaxis().set_visible(False)

ax1[0,1].imshow(final_society2, cmap=sociedad2.moda(final_society2)[3])
ax1[0,1].get_xaxis().set_visible(False)
ax1[0,1].get_yaxis().set_visible(False)

ax1[0,2].imshow(final_society3, cmap=sociedad3.moda(final_society3)[3])
ax1[0,2].get_xaxis().set_visible(False)
ax1[0,2].get_yaxis().set_visible(False)

fig1.savefig('colormap_40x40_extra.pdf', dpi=300)

"""


"""
In order to analize the model, we'll have to look at the transition phase
of the system. We will define some functions to obtain the results 
(it can be done better!!!!!!!, probabably just one function could contain all the
cases we are splitting here in different functions)
"""


#unidimensional graph

def graphics1d(tamaño, fs, qs, repeats, ax):
    if type(fs) == int:
        fs = [fs]
        
    size = tamaño
        
    for k, efe in enumerate(fs):
        #matrix to save values to be plot; columns will be for different repetitions
        scale_factor = np.zeros(repeats, dtype=object) 
        
        for reps in range(repeats):
            big_region = np.zeros(len(qs))
            
            for i, qu in enumerate(qs):
                
            
                if qu == 0:
                    big_region[i] = 1
                    
                else:
                    def cmd(num_elements):
                        i = int(np.sqrt(num_elements))
                        while num_elements % i != 0:
                            i -= 1
                        if i == 1:
                            return 'Prime number, try again'
                        return i, int(num_elements/i)
                    
                    n_rows, n_cols = cmd(size)
                    new_society = sociedad_Axelrod(rows = n_rows, cols = n_cols, q = qu, f = efe, shifts = shifts1d, dimension = 1) 
                    sociedad = new_society.run_simulation()
                    big_region[i] = new_society.moda(sociedad)[1]/size

            scale_factor[reps] = big_region
        
        
        # stack 1D arrays vertically
        stacked_scale_factor = np.vstack(scale_factor)
        reshaped_scale_factor = stacked_scale_factor.reshape(repeats, len(qs))
        
        #minimun, mean and maximum values for each q value
        scale_factor_min = reshaped_scale_factor.min(axis=0)
        scale_factor_mean = np.mean(reshaped_scale_factor, axis=0, dtype=np.float64)
        scale_factor_max = reshaped_scale_factor.max(axis=0)
        
        #bounds for the error 
        lower_bound = scale_factor_mean - scale_factor_min
        upper_bound = scale_factor_max - scale_factor_mean
        error_y = np.array(list(zip(lower_bound, upper_bound))).T
        
        #phase transition
        color_index = k 
        ax.errorbar(qs, scale_factor_mean, yerr = error_y, markersize=10, 
                     fmt='.', color=colores[color_index], ecolor=colores[color_index], 
                     capsize=3)
        ax.plot(qs, scale_factor_mean, color=colores[color_index], linewidth=1.2, 
                linestyle='dashed', label=f'N = {size}, F = {efe}')
        ax.set_xlabel(r'$q$')
        ax.set_ylabel(r'$\langle S_{max} \rangle / N$')
        ax.set_title("Phase transition in society's cultures")
        ax.grid(visible=True)
        ax.legend(loc='upper right')
        ax.minorticks_on()
            
    return 



#bidimensional graph (different F's)

def graphics(tamaño, fs, qs, repeats, fig, ax, mx, vs=None, alpha=None, tol=None): 
    
    if not vs:
        vs = 0
    if not alpha:
        alpha = 0
    if not tol:
        tol = 0
    #ensure fs es a list
    if type(fs) == int:
        fs = [fs]

    size = tamaño
    
    
    culturas_f2 = [0]
    culturas_f3 = [0]
    culturas_f4 = [0]
    culturas_f5 = [0]
    
    for k, efe in enumerate(fs):
        #matrix to save values to be plot; columns will be for different repetitions
        #bot_texter(f'va por F = {efe}')
        scale_factor = np.zeros(repeats, dtype=object) 
        color_index = k 
        
        for reps in range(repeats):
            big_region = np.zeros(len(qs[k]))
            
            for i, qu in enumerate(qs[k]):
                
            
                if qu == 0:
                    big_region[i] = 1
                    
                else:
                    def cmd(num_elements):
                        i = int(np.sqrt(num_elements))
                        while num_elements % i != 0:
                            i -= 1
                        if i == 1:
                            return 'Prime number, try again'
                        return i, int(num_elements/i)
                    
                    n_rows, n_cols = cmd(size)
                    max_nodes = (n_rows*(n_cols - 1) + n_cols*(n_rows - 1))
                    new_society = sociedad_Axelrod(rows = n_rows, cols = n_cols, q = qu, f = efe, version = vs, alpha = alpha) 
                    sociedad = new_society.run_simulation()
                    big_region[i] = new_society.moda(sociedad)[1]/size
                    
                    if reps == 0 and efe == 2 and 1 < qu < 11: 
                        num_nodes_f2 = new_society.nods
                        
                        #time evolution of nodes density
                        ejex = np.array([num for num in range(len(num_nodes_f2))])
                        ejey = np.array(num_nodes_f2)/max_nodes

                        spline = make_interp_spline(ejex, ejey)
 
                        # Returns evenly spaced numbers
                        # over a specified interval.
                        x_splines = np.linspace(ejex.min(), ejex.max(), 500)
                        y_splines = spline(x_splines)
                        
                        ax[1,0].plot(x_splines, y_splines, color=colores[qu - 1],  
                                     markersize=2, linewidth=0.9, linestyle='dashed', 
                                     label=f'q = {qu}')

                        ax[1,0].set_xlabel('Time')
                        ax[1,0].set_ylabel(r'$n_{nodos}$')
                        ax[1,0].set_title('Node density (N = 1600, F = 2)')
                        ax[1,0].legend(loc='upper right', fontsize='7')
                        ax[1,0].minorticks_on()
                        ax[1,0].grid(visible=True)
                    
                    if reps == 0 and efe == 4 and 14 < qu < 30:
                        num_nodes_f4 = new_society.nods
                        
                        #time evolution of nodes density
                        ejex = np.array([num for num in range(len(num_nodes_f4))])
                        ejey = np.array(num_nodes_f4)/max_nodes
                        
                        spline = make_interp_spline(ejex, ejey)
 
                        # Returns evenly spaced numbers
                        # over a specified interval.
                        x_splines = np.linspace(ejex.min(), ejex.max(), 500)
                        y_splines = spline(x_splines)
                        
                        ax[1,1].plot(x_splines, y_splines, color=colores[qu - 15],  
                                     markersize=2, linewidth=0.9, linestyle='dashed', 
                                     label=f'q = {qu}')
                        
                        
                        ax[1,1].set_xlabel('Time')
                        ax[1,1].set_ylabel(r'$n_{nodos}$')
                        ax[1,1].set_title('Node density (N = 1600, F = 4)')
                        ax[1,1].legend(loc='upper right', fontsize='7')
                        ax[1,1].minorticks_on()
                        ax[1,1].grid(visible=True)
                        
                    if efe == 2 and qu == 4 and len(new_society.moda(sociedad)[2]) > len(culturas_f2):
                        culturas_f2 = new_society.moda(sociedad)[2]
                        
                    if efe == 3 and qu == 9 and len(new_society.moda(sociedad)[2]) > len(culturas_f3): #15
                        culturas_f3 = new_society.moda(sociedad)[2]
                    
                    if efe == 4 and qu == 13 and len(new_society.moda(sociedad)[2]) > len(culturas_f4): #21
                        culturas_f4 = new_society.moda(sociedad)[2]
                    
                    if efe == 5 and qu == 16 and len(new_society.moda(sociedad)[2]) > len(culturas_f5): #28
                        culturas_f5 = new_society.moda(sociedad)[2]
                        

            scale_factor[reps] = big_region
        
        
        # stack 1D arrays vertically
        stacked_scale_factor = np.vstack(scale_factor)
        reshaped_scale_factor = stacked_scale_factor.reshape(repeats, len(qs[k]))
        
        #minimun, mean and maximum values for each q value
        scale_factor_min = reshaped_scale_factor.min(axis=0)
        scale_factor_mean = np.mean(reshaped_scale_factor, axis=0, dtype=np.float64)
        scale_factor_max = reshaped_scale_factor.max(axis=0)
        
        #bounds for the error 
        lower_bound = scale_factor_mean - scale_factor_min
        upper_bound = scale_factor_max - scale_factor_mean
        error_y = np.array(list(zip(lower_bound, upper_bound))).T
        
        #phase transition
        mx.errorbar(qs[k], scale_factor_mean, yerr = abs(error_y), markersize=10, 
                     fmt='.', color=colores[color_index], ecolor=colores[color_index], 
                     capsize=3)
        mx.plot(qs[k], scale_factor_mean, color=colores[color_index], linewidth=1.2, 
                linestyle='dashed', label=f'N = {size}, F = {efe}')
        mx.set_xlabel(r'$q$')
        mx.set_ylabel(r'$\langle S_{max} \rangle / N$')
        mx.set_title("Phase transition in society's cultures")
        mx.legend(loc='upper right')
        mx.minorticks_on()
        mx.grid(visible=True) 
        
    return culturas_f2, culturas_f3, culturas_f4, culturas_f5



#bidimensional graph (different N's)

def graphics2n(tamaño, fs, qs, repeats, ax, mx, vs=None, alpha=None): 
    if not vs:
        vs = 0
    if not alpha:
        alpha = 0
    #ensure tamaño is a list
    if type(tamaño) == int:
        tamaño = [tamaño]

    efe = fs
        
    for j, size in enumerate(tamaño):
        #bot_texter(f'va por N = {size}')
        scale_factor = np.zeros(repeats, dtype=object) 
        color_index = j 

            
        for reps in range(repeats):
            big_region = np.zeros(len(qs))
            
            for i, qu in enumerate(qs):
                if qu == 0:
                    big_region[i] = 1
                    
                else:
                    def cmd(num_elements):
                        i = int(np.sqrt(num_elements))
                        while num_elements % i != 0:
                            i -= 1
                        if i == 1:
                            return 'Prime number, try again'
                        return i, int(num_elements/i)
                    
                    n_rows, n_cols = cmd(size)
                    max_nodes = (n_rows*(n_cols - 1) + n_cols*(n_rows - 1))
                    new_society = sociedad_Axelrod(rows = n_rows, cols = n_cols, q = qu, f = efe, version = vs, alpha = alpha) 
                    sociedad = new_society.run_simulation()
                    big_region[i] = new_society.moda(sociedad)[1]/size

                    if reps == 0 and size == tamaño[0] and 1 < qu < 11: 
                        num_nodes_f2 = new_society.nods
                        
                        #time evolution of nodes density
                        ejex = np.array([num for num in range(len(num_nodes_f2))])
                        ejey = np.array(num_nodes_f2)/max_nodes

                        spline = make_interp_spline(ejex, ejey)
 
                        # Returns evenly spaced numbers
                        # over a specified interval.
                        x_splines = np.linspace(ejex.min(), ejex.max(), 500)
                        y_splines = spline(x_splines)
                        
                        ax[1,0].plot(x_splines, y_splines, color=colores[qu - 1],  
                                     markersize=2, linewidth=0.9, linestyle='dashed', 
                                     label=f'q = {qu}')

                        ax[1,0].set_xlabel('Time')
                        ax[1,0].set_ylabel(r'$n_{nodos}$')
                        ax[1,0].set_title(f'Node density (N = {tamaño[0]}, F = {efe})')
                        ax[1,0].legend(loc='upper right', fontsize='7')
                        ax[1,0].minorticks_on()
                        ax[1,0].grid(visible=True)
                    
                    if reps == 0 and size == tamaño[-1] and 1 < qu < 11 and efe == 2:
                        num_nodes_f4 = new_society.nods
                        
                        #time evolution of nodes density
                        ejex = np.array([num for num in range(len(num_nodes_f4))])
                        ejey = np.array(num_nodes_f4)/max_nodes
                        
                        spline = make_interp_spline(ejex, ejey)
 
                        # Returns evenly spaced numbers
                        # over a specified interval.
                        x_splines = np.linspace(ejex.min(), ejex.max(), 500)
                        y_splines = spline(x_splines)
                        
                        ax[1,1].plot(x_splines, y_splines, color=colores[qu - 1],  
                                     markersize=2, linewidth=0.9, linestyle='dashed', 
                                     label=f'q = {qu}')
                        
                        
                        ax[1,1].set_xlabel('Time')
                        ax[1,1].set_ylabel(r'$n_{nodos}$')
                        ax[1,1].set_title(f'Node density (N = {tamaño[-1]}, F = {efe})')
                        ax[1,1].legend(loc='upper right', fontsize='7')
                        ax[1,1].minorticks_on()
                        ax[1,1].grid(visible=True)
                        
                    if reps == 0 and size == tamaño[-1] and 10 < qu < 26 and efe == 4:
                        num_nodes_f4 = new_society.nods
                        
                        #time evolution of nodes density
                        ejex = np.array([num for num in range(len(num_nodes_f4))])
                        ejey = np.array(num_nodes_f4)/max_nodes
                        
                        spline = make_interp_spline(ejex, ejey)
 
                        # Returns evenly spaced numbers
                        # over a specified interval.
                        x_splines = np.linspace(ejex.min(), ejex.max(), 500)
                        y_splines = spline(x_splines)
                        
                        ax[1,1].plot(x_splines, y_splines, color=colores[qu - 11],  
                                     markersize=2, linewidth=0.9, linestyle='dashed', 
                                     label=f'q = {qu}')
                        
                        
                        ax[1,1].set_xlabel('Time')
                        ax[1,1].set_ylabel(r'$n_{nodos}$')
                        ax[1,1].set_title(f'Node density (N = {tamaño[-1]}, F = {efe})')
                        ax[1,1].legend(loc='upper right', fontsize='7')
                        ax[1,1].minorticks_on()
                        ax[1,1].grid(visible=True)
        
            scale_factor[reps] = big_region
            
                
                
        # stack 1D arrays vertically
        stacked_scale_factor = np.vstack(scale_factor)
        reshaped_scale_factor = stacked_scale_factor.reshape(repeats, len(qs))
        
        #minimun, mean and maximum values for each q value
        scale_factor_min = reshaped_scale_factor.min(axis=0)
        scale_factor_mean = np.mean(reshaped_scale_factor, axis=0, dtype=np.float64)
        scale_factor_max = reshaped_scale_factor.max(axis=0)
        
        #bounds for the error 
        lower_bound = scale_factor_mean - scale_factor_min
        upper_bound = scale_factor_max - scale_factor_mean
        error_y = np.array(list(zip(lower_bound, upper_bound))).T
        
        #phase transition
        mx.errorbar(qs, scale_factor_mean, yerr = abs(error_y), markersize=10, 
                     fmt='.', color=colores[color_index], ecolor=colores[color_index], 
                     capsize=3)
        mx.plot(qs, scale_factor_mean, color=colores[color_index], linewidth=1.2, 
                linestyle='dashed', label=f'N = {size}, F = {efe}')
        mx.set_xlabel(r'$q$')
        mx.set_ylabel(r'$\langle S_{max} \rangle / N$')
        mx.set_title("Phase transition in society's cultures")
        mx.legend(loc='upper right')
        mx.minorticks_on()
        mx.grid(visible=True) 
    
    return



#bidimensional different versions

def graphics_distv(tamaño, fs, qs, repeats, ax, vs, alpha=None, tol=None): 
    
    efe = fs
    size = tamaño
    culturas = [0]
    
    
    for j in range(len(vs)):
        for l in range(len(alpha)):
            #matrix to save values to be plot; columns will be for different repetitions
            scale_factor = np.zeros(repeats, dtype=object) 
            num_nodes = [0]
            
            for reps in range(repeats):
                big_region = np.zeros(len(qs))
                
                for i, qu in enumerate(qs):
                    
                
                    if qu == 0:
                        big_region[i] = 1
                        
                    else:
                        def cmd(num_elements):
                            i = int(np.sqrt(num_elements))
                            while num_elements % i != 0:
                                i -= 1
                            if i == 1:
                                return 'Prime number, try again'
                            return i, int(num_elements/i)
                        
                        n_rows, n_cols = cmd(size)
                        max_nodes = (n_rows*(n_cols - 1) + n_cols*(n_rows - 1))
                        new_society = sociedad_Axelrod(rows = n_rows, cols = n_cols, q = qu, f = efe, version = vs[j], alpha = alpha[l], tolerance = tol) 
                        sociedad = new_society.run_simulation()
                        big_region[i] = new_society.moda(sociedad)[1]/size
                        
                        if vs[j] == 2:
                        
                            if alpha[l] == 0.6 and reps == 0 and efe == 2 and 1 < qu < 10:
                                
                                num_nodes = new_society.nods
                                
                                #time evolution of nodes density
                                ejex = np.array([num for num in range(len(num_nodes))])
                                ejey = np.array(num_nodes)/max_nodes
                                ax[1].plot(ejex, ejey, color=colores[qu - 1],  
                                             markersize=2, linewidth=1.2, linestyle='dashed', label=f'q = {qu}')
                                
                                ax[1].set_xlabel('Time')
                                ax[1].set_ylabel(r'$n_{nodos}$')
                                ax[1].set_title('Node density (N = 400, F = 2)')
                                ax[1].legend(loc='upper right', fontsize='8')
                                ax[1].minorticks_on()
                                ax[1].grid(visible=True)
                                
                            if alpha[l] == 0.6 and reps == 0 and efe == 4 and 17 < qu < 31:
                                
                                num_nodes = new_society.nods
                                
                                #time evolution of nodes density
                                ejex = np.array([num for num in range(len(num_nodes))])
                                ejey = np.array(num_nodes)/max_nodes
                                ax[1].plot(ejex, ejey, color=colores[qu - 18],  
                                             markersize=2, linewidth=1.2, linestyle='dashed', label=f'q = {qu}')
                                    
                                ax[1].set_xlabel('Time')
                                ax[1].set_ylabel(r'$n_{nodos}$')
                                ax[1].set_title('Node density (N = 400, F = 4)')
                                ax[1].legend(loc='upper right', fontsize='8')
                                ax[1].minorticks_on()
                                ax[1].grid(visible=True)
                        else:
                            if vs[j] != 0 and reps == 0 and efe == 2 and 1 < qu < 10: 
                                num_nodes = new_society.nods
                                
                                #time evolution of nodes density
                                ejex = np.array([num for num in range(len(num_nodes))])
                                ejey = np.array(num_nodes)/max_nodes
                                if vs[j] != 4 and vs[j] != 6:
                                    try:
                                        spline = make_interp_spline(ejex, ejey)
                 
                                        # Returns evenly spaced numbers
                                        # over a specified interval.
                                        x_splines = np.linspace(ejex.min(), ejex.max(), 500)
                                        y_splines = spline(x_splines)
                                        
                                        ax[1].plot(x_splines, y_splines, color=colores[qu - 1],  
                                                     markersize=2, linewidth=1.2, linestyle='dashed', label=f'q = {qu}')
                                    
                                    except ValueError:
                                        ax[1].plot(ejex, ejey, color=colores[qu - 1],  
                                                     markersize=2, linewidth=1.2, linestyle='dashed', label=f'q = {qu}')
                                        
                                    ax[1].set_xlabel('Time')
                                    ax[1].set_ylabel(r'$n_{nodos}$')
                                    ax[1].set_title('Node density (N = 400, F = 2)')
                                    ax[1].legend(loc='upper right', fontsize='8')
                                    ax[1].minorticks_on()
                                    ax[1].grid(visible=True)
                                    
                                else:
                                    ax[1].plot(ejex, ejey, color=colores[qu - 6],  
                                                 markersize=2, linewidth=1.2, linestyle='dashed', label=f'q = {qu}')
                                    
                                    ax[1].set_xlabel('Time')
                                    ax[1].set_ylabel(r'$n_{nodos}$')
                                    ax[1].set_title('Node density (N = 400, F = 2)')
                                    ax[1].legend(loc='upper right', fontsize='8')
                                    ax[1].minorticks_on()
                                    ax[1].grid(visible=True)
                            
                            if vs[j] != 0 and reps == 0 and efe == 4 and 17 < qu < 31:
                                num_nodes = new_society.nods
                                
                                #time evolution of nodes density
                                ejex = np.array([num for num in range(len(num_nodes))])
                                ejey = np.array(num_nodes)/max_nodes
                                
                                if vs[j] != 4 and vs[j] != 6:
                                    try:
                                        spline = make_interp_spline(ejex, ejey)
                 
                                        # Returns evenly spaced numbers
                                        # over a specified interval.
                                        x_splines = np.linspace(ejex.min(), ejex.max(), 500)
                                        y_splines = spline(x_splines)
                                        
                                        ax[1].plot(x_splines, y_splines, color=colores[qu - 18],  
                                                     markersize=2, linewidth=1.2, linestyle='dashed', label=f'q = {qu}')
                                    
                                    except ValueError:
                                        ax[1].plot(ejex, ejey, color=colores[qu - 18],  
                                                     markersize=2, linewidth=1.2, linestyle='dashed', label=f'q = {qu}')
                                    
                                    
                                    ax[1].set_xlabel('Time')
                                    ax[1].set_ylabel(r'$n_{nodos}$')
                                    ax[1].set_title('Node density (N = 400, F = 4)')
                                    ax[1].legend(loc='upper right', fontsize='8')
                                    ax[1].minorticks_on()
                                    ax[1].grid(visible=True)
                                    
                                else:
                                    ax[1].plot(ejex, ejey, color=colores[qu - 18],  
                                                 markersize=2, linewidth=1.2, linestyle='dashed', label=f'q = {qu}')
                                    
                                    ax[1].set_xlabel('Time')
                                    ax[1].set_ylabel(r'$n_{nodos}$')
                                    ax[1].set_title('Node density (N = 400, F = 4)')
                                    ax[1].legend(loc='upper right', fontsize='8')
                                    ax[1].minorticks_on()
                                    ax[1].grid(visible=True)
                                    
                        if efe == 2 and qu == 2 and len(culturas) < len(new_society.moda(sociedad)[2]):
                            culturas = new_society.moda(sociedad)[2]
                        
                        if efe == 4 and qu == 14 and len(culturas) < len(new_society.moda(sociedad)[2]):
                            culturas = new_society.moda(sociedad)[2]                                 
    
                scale_factor[reps] = big_region
                
                
            # stack 1D arrays vertically
            stacked_scale_factor = np.vstack(scale_factor)
            reshaped_scale_factor = stacked_scale_factor.reshape(repeats, len(qs))
            
            #minimun, mean and maximum values for each q value
            scale_factor_min = reshaped_scale_factor.min(axis=0)
            scale_factor_mean = np.mean(reshaped_scale_factor, axis=0, dtype=np.float64)
            scale_factor_max = reshaped_scale_factor.max(axis=0)
            
            #bounds for the error 
            lower_bound = scale_factor_mean - scale_factor_min
            upper_bound = scale_factor_max - scale_factor_mean
            error_y = np.array(list(zip(lower_bound, upper_bound))).T
            
            #phase transition
            color_index = j + l 
            ax[0].errorbar(qs, scale_factor_mean, yerr = abs(error_y), markersize=10, 
                         fmt='.', color=colores[color_index], ecolor=colores[color_index], 
                         capsize=3)
            if vs[j] == 1:
                ax[0].plot(qs, scale_factor_mean, color=colores[color_index], linewidth=1.2, 
                        linestyle='dashed', label=f'F = {efe}, v = {vs[j]}, \u03B1 = {alpha[l]}, \u03BE = 1%')
            else:
                ax[0].plot(qs, scale_factor_mean, color=colores[color_index], linewidth=1.2, 
                        linestyle='dashed', label=f'F = {efe}, v = {vs[j]}, \u03B1 = {alpha[l]}')
            ax[0].set_xlabel(r'$q$')
            ax[0].set_ylabel(r'$\langle S_{max} \rangle / N$')
            ax[0].set_title("Phase transition in society's cultures")
            ax[0].legend(loc='upper right')
            ax[0].minorticks_on()
            ax[0].grid(visible=True) 

    return culturas



"""
Now let's take a look to the results we want to obtain from this model.
"""

#unidimensional


tamaño = 1600
f = [2, 3, 4]
qus = [i for i in np.arange(1, 9)] + [j for j in np.arange(9, 56, 3)]
repeats = 10

fig_1d_efes, ax_1d_efes = plt.subplots(figsize=(18, 12))

graphics1d(tamaño, f, qus, repeats, ax_1d_efes)

fig_1d_efes.savefig('uni_n1600.pdf', dpi=300)


tamaño = [100, 400, 900, 1600, 2500]
f = 2
qus = [i for i in np.arange(1, 9)] + [j for j in np.arange(9, 56, 3)]
repeats = 10

fig_1d_enes, ax_1d_enes = plt.subplots(figsize=(18, 12))

graphics1d(tamaño, f, qus, repeats, ax_1d_enes)

fig_1d_enes.savefig('uni_f2.pdf', dpi=300)



#From now on all the results will be on the bidimensional model 

#Same N, different F's


tamaño = 1600
f = [2, 3, 4, 5]
repeats = 3

qus_f2 = [i for i in np.arange(1, 9)] + [j for j in np.arange(9, 56, 3)]
qus_f3 = [1, 3] + [j for j in np.arange(4, 15)] + [i for i in np.arange(15, 56, 3)]
qus_f4 = [i for i in np.arange(1, 18, 3)] + [j for j in np.arange(18, 30)] + [k for k in np.arange(30, 56, 3)]
qus_f5 = [i for i in np.arange(1, 22, 3)] + [j for j in np.arange(22, 37)] + [k for k in np.arange(37, 56, 3)]

qus = []
qus.append(qus_f2)
qus.append(qus_f3)
qus.append(qus_f4)
qus.append(qus_f5)

fig2, ax2 = plt.subplots(2, 2, figsize=(18, 12))
merged_ax = fig2.add_subplot(2, 1, 1)
ax2[0,0].remove()
ax2[0,1].remove()

culturas_f2, culturas_f3, culturas_f4, culturas_f5 = graphics(tamaño, f, qus, repeats, fig2, ax2, merged_ax)


plt.subplots_adjust(top=0.95, bottom=0.06, left=0.11, 
                         right=0.89, hspace=0.286, wspace=0.163)

fig2.savefig('efes_try.pdf', dpi=300)



#critical exponents

def critical_exponent(culturas, name=None):
    #logaritmic fit to find the exponent as the slope 
    ejex = list(set(int(value) for value in culturas.values()))
    
    #dictionary with the frequency of each value
    dict_freq = {}
    for value in ejex:
        freq = 1
        for key in culturas:
            if culturas[key] == value:
                freq += 1
        dict_freq[value] = freq
        
    ejey = np.log10(np.array([dict_freq[value] for value in ejex])/len(culturas)) #normalize to find the probability
    ejex = np.log10(np.array(ejex))
    
    fig_ce, ax_ce = plt.subplots(figsize=(18,12))

    ajuste = py.polyfit(ejex, ejey, 1) 
    ax_ce.plot(ejex, py.polyval(ajuste, ejex), "r-", label=f'$\ln (P(s))$ = {np.round(ajuste[0], 3)} $\ln (s)$ + {np.round(ajuste[1], 3)}')
    ax_ce.plot(ejex, ejey, 'ko')
    ax_ce.set_xlabel(r'$\ln (s)$')
    ax_ce.set_ylabel('$\ln (P(s))$')
    ax_ce.legend()
    ax_ce.grid(visible=True)
    ax_ce.minorticks_on()
    
    if name:
        fig_ce.savefig(name, dpi=300)
        
    return ejex, ejey
    


ejex2, ejey2 = critical_exponent(culturas_f2, 'critical_f2.pdf')
ejex3, ejey3 = critical_exponent(culturas_f3, 'critical_f3.pdf')
ejex4, ejey4 = critical_exponent(culturas_f4, 'critical_f4.pdf')
ejex5, ejey5 = critical_exponent(culturas_f5, 'critical_f5.pdf')



#same F, different N's

repeats = 4
tamaño_fs= [100, 400, 900, 1600]
f_f2 = 2

qus_ndif_f2 = [i for i in np.arange(1, 10)] + [k for k in np.arange(10, 56, 3)]

fig3, ax3 = plt.subplots(2, 2, figsize=(18, 12))
merged_ax3 = fig3.add_subplot(2, 1, 1)
ax3[0,0].remove()
ax3[0,1].remove()

graphics2n(tamaño_fs, f_f2, qus_ndif_f2, repeats, ax3, merged_ax3)

plt.subplots_adjust(top=0.95, bottom=0.06, left=0.11, 
                         right=0.89, hspace=0.286, wspace=0.163)

fig3.savefig('enesf2.pdf', dpi=300)


f_f4 = 4

qus_ndif_f4 = [i for i in np.arange(1, 10, 3)] + [j for j in np.arange(10, 27)] + [k for k in np.arange(27, 56, 3)]

fig4, ax4 = plt.subplots(2, 2, figsize=(18, 12))
merged_ax4 = fig4.add_subplot(2, 1, 1)
ax4[0,0].remove()
ax4[0,1].remove()

graphics2n(tamaño_fs, f_f4, qus_ndif_f4, repeats, ax4, merged_ax4)

plt.subplots_adjust(top=0.95, bottom=0.06, left=0.11, 
                         right=0.89, hspace=0.286, wspace=0.163)

fig4.savefig('enesf4.pdf', dpi=300)



def grafica(size, f, qus, reps, version, alpha=None, tolerance=None, name=None):
    if type(alpha) == int:
        alpha = [alpha]
    if not alpha:
        alpha = [0]
    if not tolerance:
        tolerance = 0
    
    fig, ax = plt.subplots(2, 1, figsize=(18, 12))
    
    culturas = graphics_distv(size, f, qus, reps, ax, version, alpha, tolerance)
    plt.subplots_adjust(top=0.94, bottom=0.07, left=0.125, right=0.9, 
                        hspace=0.255, wspace=0.2)
    
    if name:
        fig.savefig(name, dpi=300)
        
    return culturas



tamaño_extras = 400
f2 = 2
f4 = 4
quses_f2 = [i for i in np.arange(1, 9)] + [j for j in np.arange(9, 56, 3)]
quses_f4 = [i for i in np.arange(1, 12, 3)] + [j for j in np.arange(12, 30)] + [k for k in np.arange(30, 56, 3)]
alphas = [0, 0.075, 0.6]


#how to socialize

culturas_alpha_f2 = grafica(tamaño_extras, f2, quses_f2, 3, [2], alphas, 0, 'alpha_f2.pdf')
culturas_alpha_f4 = grafica(tamaño_extras, f4, quses_f4, 3, [2], alphas, 0, 'alpha_f4.pdf') 


#reasonable likenesses

culturas_pr_f2_tol1 = grafica(tamaño_extras, f2, quses_f2, 3, [0, 3], 0, 0.15, 'pr_f2(0.15).pdf') 
culturas_pr_f4_tol1 = grafica(tamaño_extras, f4, quses_f4, 3, [0, 3], 0, 0.15, 'pr_f4(0.15).pdf') 

culturas_pr_f2_tol2 = grafica(tamaño_extras, f2, quses_f2, 3, [0, 3], 0, 0.05, 'pr_f2(0.05).pdf') 
culturas_pr_f4_tol2 = grafica(tamaño_extras, f4, quses_f4, 3, [0, 3], 0, 0.05, 'pr_f4(0.05).pdf') 


#gradual exchange

culturas_cg_f2_tol1 = grafica(tamaño_extras, f2, quses_f2, 3, [0, 4], 0, 0.15, 'cg_f2(0.15).pdf') 
culturas_cg_f4_tol1 = grafica(tamaño_extras, f4, quses_f4, 3, [0, 4], 0, 0.15, 'cg_f4(0.15).pdf') 

culturas_cg_f2_tol2 = grafica(tamaño_extras, f2, quses_f2, 3, [0, 4], 0, 0.05, 'cg_f2(0.05).pdf') 
culturas_cg_f4_tol2 = grafica(tamaño_extras, f4, quses_f4, 3, [0, 4], 0, 0.05, 'cg_f4(0.05).pdf')  


#freethinker

culturas_lp_f2 = grafica(tamaño_extras, f2, quses_f2, 3, [0, 1], 0, 0, 'lp_f2.pdf') 
culturas_lp_f4 = grafica(tamaño_extras, f4, quses_f4, 3, [0, 1], 0, 0, 'lp_f4.pdf')


#superagent

culturas_sa_f2 = grafica(tamaño_extras, f2, quses_f2, 3, [0, 5], 0, 0, 'sa_f2.pdf') 
culturas_sa_f4 = grafica(tamaño_extras, f4, quses_f4, 3, [0, 5], 0, 0, 'sa_f4.pdf') 


#superagent with relaxed cultural exchange

culturas_sa_cg_f2 = grafica(tamaño_extras, f2, quses_f2, 3, [0, 6], 0, 0.05, 'sa_cg_f2.pdf') 
culturas_sa_cg_f4 = grafica(tamaño_extras, f4, quses_f4, 3, [0, 6], 0, 0.05, 'sa_cg_f4.pdf') 



fin = time.time()



#save image/s for the bot to send it/them

"""
#save the plot as a PNG image to a memory buffer
buffer1 = io.BytesIO()
fig1.savefig(buffer1, format='png')
buffer1.seek(0)

#encode the image data as a base64 string
image_base64_1 = base64.b64encode(buffer1.getvalue()).decode() 
"""


#bot_texter(f'ya acabó !!! Tardó {timer(fin-inicio)}')
#bot_texter('mira', file_data=buffer1.getvalue(), file_name='box_plot.png')


print(f'Tiempo ejecución: {timer(fin-inicio)}')