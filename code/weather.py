# ------------------------ #
# ** WHEATER SIMULATION ** #
# ------------------------ #
from multiprocessing import Semaphore, Manager, Process
import random
#import matplotlib.pyplot as plt
import threading
from math import *

# ----------------------------------------------------------------------------------------------
# NOTES
"On suppose à t=0 on est le 1er janvier et que à t=365 on est le 31 décembre"
"Certaine données sont imspirées des valeurs métérologiques de la ville de LYON :"
"https://fr.wikipedia.org/wiki/Lyon"

# ----------------------------------------------------------------------------------------------
#_CLASSE_METEO_---------------------------------------------------------------------------------
class Weather():
    '''
    ## Arguments:
    - t : jour de l'année (int)
    ## Méthodes: 
    - dataJour(self, sharedMemory, sem) : met à jour les paramétres de meteo (None)
    - jourAnnee(self) : renvoie le jour de l'année (list)
    - tempJour(self,sharedMemory,waitData) : calcule la température du jour (None)
    - ensJour() : calcule l'ensoleillement du jour (None)
    - ventJour() : calcule le vent du jour (None)
    - afficheStatJour() : affiche les statistiques du jour (str)
    '''

    def __init__(self,t):
        self.t = t
    
    #_mise_à_jour_paramètres_de_météo_--------------------------------------------------------- 
    def dataJour(self, sharedMemory, sem):
        
        self.t=sharedMemory[3]

        waitTemp = Semaphore(0)
        waitWind = Semaphore(0)
        waitSunBeam = Semaphore(0)

        temperature = threading.Thread(target=self.tempJour, args=(sharedMemory,waitTemp,))
        windSpeed = threading.Thread(target=self.ventJour, args=(sharedMemory,waitWind,))
        sunbeam = threading.Thread(target=self.ensJour, args=(sharedMemory,waitSunBeam,))

        temperature.start()
        windSpeed.start()
        sunbeam.start()

        temperature.join()
        windSpeed.join()
        sunbeam.join()

        waitTemp.acquire()
        waitWind.acquire()
        waitSunBeam.acquire()
        sem.release()

        print("Ending process dataJour\n")

    #_définition_du_jour_de_l'année_en_fonction_de_t_--------------------------------------------
    def jourAnnee(self):
        mois = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
        nbJoursMois = [31,28,31,30,31,30,31,31,30,31,30,31]
        jour = self.t
        for k in range(len(nbJoursMois)):
            if jour > nbJoursMois[k]:
                jour -= nbJoursMois[k]
            else:
                return (jour, mois[k])

    #_définition_de_la_température_quotidienne_---------------------------------------------------
    "Température en °C"
    def tempJour(self,sharedMemory,waitData):
        #print("Starting thread:", threading.current_thread().name)
        coefSaison = -sin(2*pi*self.t/365-250)*15 + 14.5 
        bruit = random.random()*5*random.randint(-1,1)
        sharedMemory[0]= coefSaison + bruit
        waitData.release()
        #print("Ending thread:", threading.current_thread().name)

    # Définition de l'ensoleillement moyen en 24h
    "Taux d'ensoleillement entre 0 et 1"
    def ensJour(self,sharedMemory,waitData):
        #print("Starting thread:", threading.current_thread().name)
        (heuresEnsAnnee,heureAnnee) = (2001.9, 8760)
        fmoy = heuresEnsAnnee/heureAnnee
        coefsaison = fmoy - 0.1*sin(2*pi*self.t/365-250)
        bruit = random.random()*0.075*random.randint(-1,1)
        sharedMemory[2] = coefsaison + bruit
        waitData.release()
        #print("Ending thread:", threading.current_thread().name)
    
    # Définition du vent moyen en 24h
    "Indice entre 0 et 10"
    def ventJour(self,sharedMemory,waitData):
        #print("Starting thread:", threading.current_thread().name)
        coefSaison = 5 + 2*sin(2*pi*self.t/365-250)
        bruit = random.random()*3*random.randint(-1,1)
        sharedMemory[1]=  coefSaison + bruit
        waitData.release()
        #print("Ending thread:", threading.current_thread().name)
    
    '''
    # Affichage des statistiques du jour
    def afficheStatJour(self):
        print("\nNous sommes le ", self.jourAnnee()[0], " ", self.jourAnnee()[1])
        print("Température : ", round(self.tempJour(),1),"°C")
        print("Taux d'Ensoleillement : ", self.ensJour())
        print("Indice de Vent : ", self.ventJour(), "\n")
        return None
    '''


# -------------------------------------------
'''
# Quelles Stats aujourd'hui ?
Meteo(23).afficheStatJour()

# Graphique vent
X = [k for k in range(365)]
Y=[]
for k in range(365):
    Y.append(Meteo(k).tempJour())
plt.plot(X,Y)
plt.show()
'''