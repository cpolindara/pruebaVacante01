import numpy as np
from numpy.linalg import norm
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as colors
import copy as copy
import random
import pickle

class Mesh():

    def __init__(self, vertices, elements, nsets={}, elsets={}):
        self.__vertices = np.array(vertices)
        self.__elements = copy.deepcopy(elements)
        self.__nsets = copy.deepcopy(nsets)
        self.__elsets = copy.deepcopy(elsets)
        self.__nelements = len(self.__elements)
        self.__nvertices = len(self.__vertices)

    @property
    def vertices(self):
        return self.__vertices

    @property
    def elements(self):
        return self.__elements

    @property
    def nvertices(self):
        return  self.__nvertices

    @property
    def nelements(self):
        return self.__nelements

    @property
    def x_min(self):
        return np.min(self.__vertices[:,0])

    @property
    def x_max(self):
        return np.max(self.__vertices[:,0])

    @property
    def y_min(self):
        return np.min(self.__vertices[:,1])

    @property
    def y_max(self):
        return np.max(self.__vertices[:,1])

    @property
    def center(self):
        x = 0.5*(self.x_min + self.x_max)
        y = 0.5*(self.y_min + self.y_max)
        return np.array([x,y])

    @property
    def elsets(self):
        return self.__elsets

    @property
    def nsets(self):
        return self.__nsets

    def shuffle(self):
        # Get indices and shuffle elements
        indices = [ii for ii in range(self.__nelements)]
        random.shuffle(indices)

        elements = [self.__elements[ii] for ii in indices]
        self.__elements = elements
        for key,value in self.__elsets.items():
            self.__elsets[key] = [indices.index(ii) for ii in value]

        self.__elsets['all'] = [ii for ii in range(self.__nelements)]   # special hardcoded set!!!

        # Get indices for half the elements and flip elements
        indices = random.sample(range(len(self.__elements)), k=self.__nelements // 2)
        for ii in indices:
            self.__elements[ii].reverse()

    def split(self):
        # n = int(self.__nelements / 2)
        # all_elems = [ii for ii in range(self.__nelements)]
        # elems_to_remove = [all_elems[-1], all_elems[-n-1]]

        elems_to_remove = []
        indices = [(0,1), (self.__nvertices//2, self.__nvertices//2 + 1)]
        for ii,jj in indices:
            for el_indx, el in enumerate(self.__elements):
                if ii in el and jj in el:
                    elems_to_remove.append(el_indx)
        elems_to_remove.sort()

        for ii in elems_to_remove[::-1]:
            self.__elements.pop(ii)

        old2new = {}
        nelements = 0
        for ii in range(self.__nelements):
            if ii in elems_to_remove:
                old2new[ii] = None
            else:
                old2new[ii] = nelements
                nelements += 1

        for key,elset in self.__elsets.items():
            elset = [old2new[ii] for ii in elset]
            elset = [ii for ii in elset if ii is not None]
            self.__elsets[key] = elset

        self.__nelements -= 2
        self.__elsets['all'] = [ii for ii in range(self.__nelements)]   # special hardcoded set!!!

    def sort(self):
        # ###################################################################################### #
        # # solution

        # ###################################################################################### #
        
        self.__elsets['all'] = [ii for ii in range(self.__nelements)]   # special hardcoded set!!!

    def save(self, filename='pickle.pkl'):
        save_object_to_pickle((self.__vertices, self.__elements, self.__elsets), filename)



def set_axes_equal(ax, my_mesh:Mesh):

    x_range = my_mesh.x_max - my_mesh.x_min
    y_range = my_mesh.y_max - my_mesh.y_min
    r = max(x_range, y_range)

    x_left = my_mesh.center[0] - r
    x_right = my_mesh.center[0] + r
    y_bottom = my_mesh.center[1] - r
    y_upper = my_mesh.center[1] + r
    ax.set_xlim([x_left, x_right])
    ax.set_ylim([y_bottom, y_upper])
    return (x_left, x_right, y_bottom, y_upper)


def draw(my_mesh:Mesh, elset=[], colormap ='cividis', title='', annotate=False):

    color_elements = False
    cmap = cm.get_cmap(colormap, my_mesh.nelements)  # Get cyclic color map
    norm = colors.Normalize(vmin=0, vmax=my_mesh.nelements - 1)  # Normalize to the range of data
    if elset != []:
        # cmap = cm.get_cmap(colormap, len(elset))  # Get cyclic color map
        # norm = colors.Normalize(vmin=0, vmax=len(elset) - 1)  # Normalize to the range of data
        color_elements = True

    # draw 2D Mesh
    fig, ax = plt.subplots()

    for indx, el in enumerate(my_mesh.elements):
        nel = len(el)
        offset = 1
        if nel == 2:
            offset = 0

        x = []
        y = []
        for jj in range(nel-1+offset):
            el_1 = el[jj%nel]
            v_1 = np.array(my_mesh.vertices[el_1])
            x.append(v_1[0])
            y.append(v_1[1])
            el_2 = el[(jj+1)%nel]
            v_2 = np.array(my_mesh.vertices[el_2])
            x.append(v_2[0])
            y.append(v_2[1])

            dv = v_2 - v_1

            ax.plot(x, y, '-k', linewidth=1, zorder=1)

            if color_elements and indx in elset:
                # aux_indx = elset.index(indx)
                # color = cmap(norm(aux_indx))  # Get color from color map
                color = cmap(norm(indx))  # Get color from color map
                # ax.plot(x, y, color=color, linewidth=4.0)
                ax.quiver(v_1[0], v_1[1], dv[0], dv[1], zorder=2,
                          angles='xy', scale_units='xy', scale=1, width=0.0075, color=color, label='%2d: (%d, %d)'%(indx,el_1,el_2))

    x_left, x_right, y_bottom, y_upper = set_axes_equal(ax, my_mesh)
    ax.set_xlim()
    ax.set_aspect('equal','box')
    # ax.set_axis_off()
    ax.set_title(title)

    if annotate:
        for ii,v in enumerate(my_mesh.vertices):
            ax.plot(v[0], v[1], 'ok', markersize=3)
            ax.annotate('%d'%ii, xy=(v[0], v[1]))

        ax.legend(loc='upper left', bbox_to_anchor=(1., 1.))
        # ax.legend()

    plt.show()
    return fig, ax


def save_object_to_pickle(obj, file_path):
    with open(file_path, 'wb') as f:
        pickle.dump(obj, f)

def load_from_pickle(file_path):
    with open(file_path, 'rb') as f:
        data = pickle.load(f)
    return data


def create_circle(center=(0., 0.), radius=1.0, nelements=24):

    # create vertices
    vertices = []
    center = np.array(center)
    for a in np.linspace(0., 2*np.pi, nelements+1)[:-1]:
        p = center + radius*np.array((np.cos(a), np.sin(a)))
        vertices.append(p)

    # create elements
    elements = [[ii,(ii+1)%nelements] for ii in range(nelements)]

    # create sets
    nsets = {'all': [ii for ii in range(nelements)]}
    elsets = {
        'all': [ii for ii in range(nelements)],
        'upper-right': [ii for ii in range(nelements//4)],
        'upper-left': [ii for ii in range(nelements//4, nelements//2)],
        'bottom-left': [ii for ii in range(nelements//2, 3*nelements//4)],
        'bottom-right': [ii for ii in range(3*nelements//4, nelements)],
    }

    return Mesh(vertices, elements, nsets, elsets)


# #################################################################################################################### #

def problema01():
    msh = create_circle(nelements=12)
    ii = 1
    for key,elset in msh.elsets.items():
        annotate = False
        if key == 'all':
            annotate = True
        # fig,_ = draw(msh, elset=elset, title='Elementos ordenados: %s'%key, annotate=annotate)
        # fig.savefig('sorted%02d.svg'%ii)
        ii += 1

    msh.shuffle()
    ii = 1
    for key,elset in msh.elsets.items():
        annotate = False
        if key == 'all':
            annotate = True
        # fig,_ = draw(msh, elset=elset, title='Elementos desordenados: %s'%key, annotate=annotate)
        # fig.savefig('shuffled%02d.svg'%ii)
        ii += 1


    # ###################################################################################### #
    # Test solution
    # msh.sort()
    # for key,elset in msh.elsets.items():
    #     annotate = False
    #     if key == 'all':
    #         annotate = True
    #     draw(msh, elset=elset, title='Elementos reordenados: %s'%key, annotate=annotate)
    # ###################################################################################### #

def problema02():
    msh = create_circle(nelements=12)
    ii = 1
    for key,elset in msh.elsets.items():
        annotate = False
        if key == 'all':
            annotate = True
        # fig,_ = draw(msh, elset=elset, title='Elementos ordenados: %s'%key, annotate=annotate)
        # fig.savefig('sorted%02d.svg'%ii)
        ii += 1

    msh.shuffle()
    msh.split()
    ii = 1
    for key,elset in msh.elsets.items():
        annotate = False
        if key == 'all':
            annotate = True
        fig,_ = draw(msh, elset=elset, title='Elementos desordenados: %s'%key, annotate=annotate)
        # fig.savefig('split%02d.svg'%ii)
        ii += 1


    # ###################################################################################### #
    # Test solution
    # msh.sort()
    # for key,elset in msh.elsets.items():
    #     annotate = False
    #     if key == 'all':
    #         annotate = True
    #     draw(msh, elset=elset, title='Elementos reordenados: %s'%key, annotate=annotate)
    # ###################################################################################### #


# problema01()
problema02()

print('\nAll good!')