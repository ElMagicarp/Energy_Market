#symbole triangle rempli
import sys
import os
from multiprocessing import Process, Manager, Pipe, Semaphore
import signal
import threading
import sysv_ipc
import socket
from external import External
from weather import Weather
from genHome import listeMaison, Maison

global event
global parentPipe

def handler (sig,frame):
        if sig == signal.SIGUSR1:
            event[0]= parentPipe.recv()
        if sig == signal.SIGUSR2:
            event[1] = parentPipe.recv()

class Factor():

    def __init__(self, type ,weight, value = 0):
        self.type = type
        self.weight = weight
        self.value = value


class Market():

    def __init__(self, currentEnergyPrice = 1, longtermeAttenuation = 1 , amoutEnergyBought = 0, amoutEnergySold = 0, internalFactors ={}, externalFactors ={}):
        self.connPipe = {"parentConn":None,"childConn":None}
        self.currentEnergyPrice = currentEnergyPrice
        self.longtermeAttenuation = longtermeAttenuation
        self.amoutEnergyBought = amoutEnergyBought
        self.amoutEnergySold = amoutEnergySold
        self.internalFactors = internalFactors
        self.externalFactors = externalFactors

    def computeCurrentEnergyPrice(self):
        newPrice = self.longtermeAttenuation*self.currentEnergyPrice + computeContribution(self.internalFactors) + computeContribution(self.externalFactors)
        self.currentEnergyPrice = newPrice
    
    def eventIsActive(self):
        res = []
        for event in self.externalFactors:
            if (self.externalFactors[event]).value == 1:
                res.append((self.externalFactors[event]).type)
        
        return res

def computeContribution(factor):
    
    result=0
    for event in factor:
        result+=(factor[event]).weight*(factor[event]).value
    return result


if __name__ == '__main__':

    signal.signal(signal.SIGUSR1, handler)
    signal.signal(signal.SIGUSR2, handler)

    #print("Starting process market\n")
    with Manager() as manager:

        #_initialisation_facteurCalcul_-----------------------------------------------------------
        tempFactor = Factor("temperature", 0.01, 0)
        windSpeedFactor = Factor("wind", 0.01, 0)
        sunBeamFactor = Factor("sunbeam", 0.01, 0)
        energyBought = Factor("bought", 0.01, 0)
        energySold = Factor("sold", 0.01, 0)
        warEvent = Factor("warEvent",0.2, 0)
        petrolCrisisEvent = Factor("petrolCrisisEvent",0.05, 0)

        #_initialisation_Objets_parent/child_-----------------------------------------------------
        energyMarket = Market(  currentEnergyPrice=0.145, 
                                longtermeAttenuation= 0.99, 
                                internalFactors={energyBought.type:energyBought,energySold.type:energySold,tempFactor.type:tempFactor,windSpeedFactor.type:windSpeedFactor,sunBeamFactor.type:sunBeamFactor}, 
                                externalFactors={warEvent.type:warEvent, petrolCrisisEvent.type:petrolCrisisEvent}
                            )
        event=[0,0]
        externalGenerator = External()
        weatherGenerator = Weather(0)

        #_initialisation_sharedMemory_weatherFactor_----------------------------------------------
        weatherFactor = manager.list([0,0,0])

        #_creation_maisons_-----------------------------------------------------------------------
        NOMBRE_HOME = 0
        genHomeProcess = Process(target= listeMaison, args=(NOMBRE_HOME,weatherFactor,))
        genHomeProcess.start()
        genHomeProcess.join()

        #_initialisation_semaphore_weatherFactor_-------------------------------------------------
        weatherSem = Semaphore(0)

        #_initialisation_durée_simulation---------------------------------------------------------
        NOMBRE_JOUR = 10

        #_routine_--------------------------------------------------------------------------------
        for i in range(NOMBRE_JOUR):
            print("JOUR "+ str(i)+"\n")
            print("PID "+str(os.getpid()))

            #_initialisation_pipe_weatherFactor_---------------------------------------------------
            parentPipe,childConn = Pipe()
            energyMarket.connPipe["parentConn"] = parentPipe
            energyMarket.connPipe["childConn"] = childConn

            #_initialisation_Process_updateFacteurCalcul-------------------------------------------
            externalProcess = Process(target= externalGenerator.run, args=((energyMarket.connPipe)["childConn"],))
            weatherProcess = Process(target= weatherGenerator.dataJour, args=(weatherFactor,weatherSem,))

            #_lunch_Process_updateFacteurCalcul---------------------------------------------------
            externalProcess.start()
            weatherProcess.start()

            #_wait_Process_updateFacteurCalcul----------------------------------------------------
            externalProcess.join()
            print("Current Event {}".format(str(energyMarket.eventIsActive())))
            weatherProcess.join()

            #_wait_update_weatherFactor------------------------------------------------------------
            weatherSem.acquire()

             #_update_weatherFactor----------------------------------------------------------------
            tempFactor.value = weatherFactor[0]
            print("Current temperature {}".format(str(tempFactor.value)))

            windSpeedFactor.value = weatherFactor[1]
            print("Current wind {}".format(str(windSpeedFactor.value)))

            sunBeamFactor.value = weatherFactor[2]
            print("Current sunBeam {}".format(str(sunBeamFactor.value)))


            #_calcul_currentEnergyPrice-----------------------------------------------------------
            energyMarket.computeCurrentEnergyPrice()

            print("Current energy price {}\n".format(str(energyMarket.currentEnergyPrice)))
            
            weatherGenerator.t+=1

#print("Ending process market\n")


    

        

