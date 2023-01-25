# ------------------------ #
# ** WHEATER SIMULATION ** #
# ------------------------ #

import random
import matplotlib.pyplot as plt
from math import *

# -------------------------------------------
# NOTES
"On suppose à t=0 on est le 1er janvier et que à t=365 on est le 31 décembre"
"Certaine données sont imspirées des valeurs métérologiques de la ville de LYON :"
"https://fr.wikipedia.org/wiki/Lyon"

# -------------------------------------------
# CLASSES METEO
class Meteo():
    '''
    Arguments: t (int) : jour de l'année
    Méthodes: jourAnnee() : renvoie le jour de l'année
            tempJour() : renvoie la température du jour 
            ensJour() : renvoie le taux d'ensoleillement du jour
            ventJour() : renvoie l'indice de vent du jour
            afficheStatJour() : affiche les statistiques du jour
    '''

    def __init__(self,t):
        self.t = t
    
    # Définition du jour de l'année en fonction de t
    def jourAnnee(self):
        mois = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
        nbJoursMois = [31,28,31,30,31,30,31,31,30,31,30,31]
        jour = self.t
        for k in range(len(nbJoursMois)):
            if jour > nbJoursMois[k]:
                jour -= nbJoursMois[k]
            else:
                return (jour, mois[k])

    # Définition de la température quotidienne
    "Température en °C"
    def tempJour(self):
        coefSaison = -sin(2*pi*self.t/365-250)*15 + 14.5 
        bruit = random.random()*5*random.randint(-1,1)
        return coefSaison + bruit

    # Définition de l'ensoleillement moyen en 24h
    "Taux d'ensoleillement entre 0 et 1"
    def ensJour(self):
        (heuresEnsAnnee,heureAnnee) = (2001.9, 8760)
        fmoy = heuresEnsAnnee/heureAnnee
        coefsaison = fmoy - 0.1*sin(2*pi*self.t/365-250)
        bruit = random.random()*0.075*random.randint(-1,1)
        return coefsaison + bruit
    
    # Définition du vent moyen en 24h
    "Indice entre 0 et 10"
    def ventJour(self):
        coefSaison = 5 + 2*sin(2*pi*self.t/365-250)
        bruit = random.random()*3*random.randint(-1,1)
        return coefSaison + bruit
    
    # Affichage des statistiques du jour
    def afficheStatJour(self):
        print("\nNous sommes le ", self.jourAnnee()[0], " ", self.jourAnnee()[1])
        print("Température : ", round(self.tempJour(),1),"°C")
        print("Taux d'Ensoleillement : ", self.ensJour())
        print("Indice de Vent : ", self.ventJour(), "\n")
        return None


# -------------------------------------------
# Quelles Stats aujourd'hui ?
Meteo(23).afficheStatJour()

# Graphique vent
X = [k for k in range(365)]
Y=[]
for k in range(365):
    Y.append(Meteo(k).tempJour())
plt.plot(X,Y)
plt.show()









