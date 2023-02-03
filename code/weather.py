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

    def __init__(self,t):
        self.t = t
        self.temp = None
        self.wind = None
        self.sunshine = None
        
    
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


    #_définition_de_la_température_quotidienne_---------------------------------------------------
    "Température en °C"
    def tempJour(self,sharedMemory,waitData):
        coefSaison = -sin(2*pi*self.t/365-250)*15 + 14.5 
        bruit = random.random()*5*random.randint(-1,1)
        sharedMemory[0]= coefSaison + bruit
        self.temp = sharedMemory[0]
        waitData.release()


    # Définition de l'ensoleillement moyen en 24h
    "Taux d'ensoleillement entre 0 et 1"
    def ensJour(self,sharedMemory,waitData):
        (heuresEnsAnnee,heureAnnee) = (2001.9, 8760)
        fmoy = heuresEnsAnnee/heureAnnee
        coefsaison = fmoy - 0.1*sin(2*pi*self.t/365-250)
        bruit = random.random()*0.075*random.randint(-1,1)
        sharedMemory[2] = coefsaison + bruit
        self.sunshine = sharedMemory[2]
        waitData.release()

    
    # Définition du vent moyen en 24h
    "Indice entre 0 et 10"
    def ventJour(self,sharedMemory,waitData):
        coefSaison = 5 + 2*sin(2*pi*self.t/365-250)
        bruit = random.random()*3*random.randint(-1,1)
        sharedMemory[1]=  coefSaison + bruit
        self.wind = sharedMemory[1]
        waitData.release()