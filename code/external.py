# --------------------------- #
# **  External Coefficient ** #
# --------------------------- #

import random
from math import exp

# ----------------------------
# Define External Class :
class External:
    '''
    Génère un coefficient €[0,1] par un modèle exponnentiel ( il y a plus de chance d'obtenir un nombre proche de 0 que de 1
    '''
    def __init__(self):
        self.externalCoef = exp(-random.choice([k for k in range(15)]))

# ----------------------------
