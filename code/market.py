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

class Factor():

    def __init__(self, type ,weight, value = 0):
        self.type = type
        self.weight = weight
        self.value = value


class Market():

    def __init__(self, currentEnergyPrice = 1, longtermeAttenuation = 1 , amoutEnergyBought = 0, amoutEnergySold = 0, internalFactors ={}, externalFactors ={}):
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
    
    def eventIsActive(self):
        res = []
        for event in self.externalFactors:
            if (self.externalFactors[event]).value == 1:
                res.append((self.externalFactors[event]).type)
        
        return res


def handler (self,sig,frame):
        if sig == signal.SIGUSR1:
            self.externalFactors[warEvent.type].value = self.connPipe["parentConn"].recv()
        if sig == signal.SIGUSR2:
            self.externalFactors[petrolCrisisEvent.type].value = self.connPipe["parentConn"].recv()

    
def computeContribution(factor):
    
    result=0
    for event in factor:
        result+=(factor[event]).weight*(factor[event]).value
    return result


if __name__ == '__main__':

    print("Starting process market")
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
        signal.signal(signal.SIGUSR1, handler)
        externalGenerator = External()
        weatherGenerator = Weather(0)

        #_initialisation_sharedMemory_weatherFactor_----------------------------------------------
        weatherFactor = manager.list([0,0,0])
        print(weatherFactor)

        #_initialisation_semaphore_weatherFactor_-------------------------------------------------
        weatherSem = Semaphore(0)

        #_initialisation_Process_updateFacteurCalcul----------------------------------------------
        nbHome = 0
        externalProcess = Process(target= externalGenerator.run, args=((energyMarket.connPipe)["childConn"],))
        weatherProcess = Process(target= weatherGenerator.dataJour, args=(weatherFactor,weatherSem,))
        genHomeProcess = Process(target= listeMaison, args=(nbHome,weatherFactor,))

        #_routine_--------------------------------------------------------------------------------
        while True:

            #_lunch_Process_updateFacteurCalcul---------------------------------------------------
            try:
                externalProcess.start()
            except:
                print("event unchanged")

            weatherProcess.start()

            #_wait_Process_updateFacteurCalcul----------------------------------------------------
            externalProcess.join()
            print("Current Event {}\n".format(str(energyMarket.eventIsActive())))
            weatherProcess.join()

            #_wait_update_weatherFactor------------------------------------------------------------
            weatherSem.acquire()

             #_update_weatherFactor----------------------------------------------------------------
            tempFactor.value = weatherFactor[0]
            print("Current temperature {}\n".format(str(tempFactor.value)))

            windSpeedFactor.value = weatherFactor[1]
            print("Current wind {}\n".format(str(windSpeedFactor.value)))

            sunBeamFactor.value = weatherFactor[2]
            print("Current sunBeam {}\n".format(str(sunBeamFactor.value)))


            #_calcul_currentEnergyPrice-----------------------------------------------------------
            energyMarket.computeCurrentEnergyPrice()

            print("Current energy price {}\n".format(str(energyMarket.currentEnergyPrice)))

            weatherGenerator.t+=1

print("Ending process market")


    

        

