# --------------------------- #
# **  External Coefficient ** #
# --------------------------- #

import random
import os
import signal
from multiprocessing import Process,Pipe

# ----------------------------
# Define External Class
class External:
    '''
    Classe qui permet de savoir si un évènement extérieur s'est produit
    ## Argument:
    - listCoef : liste des coefficients d'évènements possible : Guerre / Petrole
    ## Méthode:
    - run(self,event,childPipe) : modifie la valeur d'un évènement de manière aléatoire (None)
    '''

    def __init__(self):
        self.listCoef = {"warEvent" : 0, "petrolCrisisEvent" :0}

    def run(self,event,childPipe):
        
        
        #print("Starting process external\n")
        warChange = False
        petrolChange = False

        "Vérification changement War"
        xWar = random.random()
        if xWar< 0.05 :
            print("#EVENT War previous "+str(self.listCoef["warEvent"]))
            if event.listCoef["warEvent"]==0:
                self.listCoef["warEvent"]=1
            else:
                self.listCoef["warEvent"]=0
            warChange= True

        "Vérification changement Petrol"
        xPetrol = random.random()
        if xPetrol < 0.10 :
            print("#EVENT Petrol previous "+str(self.listCoef["petrolCrisisEvent"]))
            if event.listCoef["petrolCrisisEvent"]==0:
                self.listCoef["petrolCrisisEvent"]=1
            else:
                self.listCoef["petrolCrisisEvent"]=0
            petrolChange= True
        
        if warChange or petrolChange:
            print("#SEND Event")
            childPipe.send(self.listCoef)
            os.kill(os.getppid(), signal.SIGUSR1)
        
        print("Ending process external\n")