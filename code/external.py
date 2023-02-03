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

    def __init__(self):
        self.listEtatEvent = {"warEvent" : 0, "petrolCrisisEvent" :0}

    def run(self,event,childPipe,sem):
        
        warChange = False
        petrolChange = False

        "Vérification changement War"
        xWar = random.random()
        if xWar< 0.05 :
            print("#EVENT War previous "+str(self.listEtatEvent["warEvent"]))
            if event.listEtatEvent["warEvent"]==0:
                self.listEtatEvent["warEvent"]=1
            else:
                self.listEtatEvent["warEvent"]=0
            warChange= True

        "Vérification changement Petrol"
        xPetrol = random.random()
        if xPetrol < 0.10 :
            print("#EVENT Petrol previous "+str(self.listEtatEvent["petrolCrisisEvent"]))
            if event.listEtatEvent["petrolCrisisEvent"]==0:
                self.listEtatEvent["petrolCrisisEvent"]=1
            else:
                self.listEtatEvent["petrolCrisisEvent"]=0
            petrolChange= True
        
        if warChange or petrolChange:
            print("#SEND Event")
            childPipe.send(self.listEtatEvent)
        
        sem.release()