# --------------------------- #
# **  External Coefficient ** #
# --------------------------- #

import random

import os
import signal
import time
from multiprocessing import Process

# ----------------------------
# Define External Class :
class External:
    '''
    Génère le coefficient qui représente les facteurs extérieurs, 
    '''

    def __init__(self):
        self.listCoef = {"warEvent" : 0,
                         "petrolCrisisEvent" :0}
    
    def run(self):
        x = random.random()
        if self.listCoef["warEvent"] == 0:
            if x < 0.05 :
                self.listCoef["warEvent"] =1
        else:
            if x < 0.35:
                self.listCoef["petrolCrisisEvent"] =0
        if self.listCoef["petrolCrisisEvent"] == 0:
            if x < 0.05 :
                self.listCoef["petrolCrisisEvent"] =1
        else:
            if x < 0.35:
                self.listCoef["petrolCrisisEvent"] =0
        

# ----------------------------
# Multiprocessing

def child_external():
    os.kill(os.getpid(), signal.SIGUSR1)
    while True:
        monCoefExternal = External.run()
