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
    # Coef Externe
    Permet de savoir si un évènement extérieur s'est produit :
    - Evènements possibles : Guerre / Petrole
    - run : modifie la valeur d'un évènement de manière aléatoire
    '''

    def __init__(self):
        self.listCoef = {"warEvent" : 0, "petrolCrisisEvent" :0}

    def run(self, childPipe):
        
        #print("Starting process external\n")
        warChange = False
        petrolChange = False

        "Vérification changement War"
        xWar = random.random()
        if xWar< 0.05 :
            if self.listCoef["warEvent"]==0:
                self.listCoef["warEvent"]=1
            else:
                self.listCoef["warEvent"]=0
            print(os.getppid())
            os.kill(os.getppid(), signal.SIGUSR1)
            warChange= True

        "Vérification changement Petrol"
        xPetrol = random.random()
        if xPetrol < 0.10 :
            if self.listCoef["petrolCrisisEvent"]==0:
                self.listCoef["petrolCrisisEvent"]=1
            else:
                self.listCoef["petrolCrisisEvent"]=0
            print(os.getppid())
            os.kill(os.getppid(), signal.SIGUSR2)
            petrolChange= True
        
        if warChange or petrolChange:
            childPipe.send(self.listCoef)

        

        #print("Ending process external\n")