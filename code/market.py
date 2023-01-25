import sys
import os
from multiprocessing import Process, Manager, Pipe
import signal
import threading
import sysv_ipc
import socket
from external import External
from weather import Weather

class Factor():

    def __init__(self, type ,weight, value = 0):
        self.type = type
        self.weight = weight
        self.value = value


class Market():

    def __init__(self, currentEnergyPrice = 1, longtermeAttenuation = 1 , amoutEnergyBought = 0, amoutEnergySold = 0, internalFactors ={}, externalFactors ={}):
        signal.signal(signal.SIGUSR1, handler)
        parentConn,childConn = Pipe()
        self.connPipe = {"parentConn":parentConn,"childConn":childConn}
        self.currentEnergyPrice = currentEnergyPrice
        self.longtermeAttenuation = longtermeAttenuation
        self.amoutEnergyBought = amoutEnergyBought
        self.amoutEnergySold = amoutEnergySold
        self.internalFactors = internalFactors
        self.externalFactors = externalFactors

    def computeCurrentEnergyPrice(self):
        newPrice = self.longtermeAttenuation*self.currentEnergyPrice + computeContribution(self.internalFactors) + computeContribution(self.externalFactors)
        self.currentEnergyPrice = newPrice


if __name__ == '__main__':

    with Manager() as manager:

        #_initialisation_facteurCalcul_-----------------------------------------------------------
        tempFactor = Factor("temperature", 0.001, 0)
        windSpeedFactor = Factor("wind", 0.001, 0)
        sunBeamFactor = Factor("sunbeam", 0.001, 0)
        warEvent = Factor("warEvent",0.2, 0)
        petrolCrisisEvent = Factor("petrolCrisisEvent",0.05, 0)

        #_initialisation_Objets_parent/child_-----------------------------------------------------
        energyMarket = Market(currentEnergyPrice=0.145, longtermeAttenuation= 0.99, internalFactors={tempFactor.type:tempFactor,windSpeedFactor.type:windSpeedFactor,sunBeamFactor.type:sunBeamFactor}, externalFactors={warEvent.type:warEvent, petrolCrisisEvent.type:petrolCrisisEvent})
        externalGenerator = External()
        weatherGenerator = Weather(0)

        #_initialisation_sharedMemory_weatherFactor_----------------------------------------------
        weatherFactor = manager.dict("temperature","wind","sunBeam")

        #_initialisation_Process_updateFacteurCalcul----------------------------------------------
        externalProcess = Process(target= externalGenerator.run, args=((energyMarket.connPipe)["childConn"]))
        weatherProcess = Process(target= weatherGenerator.dataJour, args=(weatherFactor))

        #_routine_--------------------------------------------------------------------------------
        while True:

            #_lunch_Process_updateFacteurCalcul---------------------------------------------------
            externalProcess.start()
            weatherProcess.start()

            #_wait_Process_updateFacteurCalcul----------------------------------------------------
            externalProcess.join()
            weatherProcess.join()

            #_update_weatherFactor----------------------------------------------------------------
            tempFactor.value = weatherFactor["temperature"]
            windSpeedFactor.value = weatherFactor["wind"]
            sunBeamFactor.value = weatherFactor["sunBeam"]

            #_calcul_currentEnergyPrice-----------------------------------------------------------
            energyMarket.computeCurrentEnergyPrice()

            weatherGenerator.t+=1


def handler (self,sig,frame):
        if sig == signal.SIGUSR1:
            self.externalFactors[warEvent.type].value = self.connPipe["parentConn"].recv()
        if sig == signal.SIGUSR2:
            self.externalFactors[petrolCrisisEvent.type].value = self.connPipe["parentConn"].recv()

    
def computeContribution(factor):
    
    result=0
    for event in factor:
        result+=event.weight*event.value
    return result

        

