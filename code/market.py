import sys
import os
from multiprocessing import Process, Pipe
import signal
import threading
import sysv_ipc
import socket
import external
import weather

class InternalFactor():

    def __init__(self, type ,weight, value = 0):
        self.type = type
        self.weight = weight
        self.value = value


class ExternalFactor():

    def __init__(self, weight, value):
        self.weight = weight
        self.value = value


class Market():

    def __init__(self, currentEnergyPrice = 1, longtermeAttenuation = 1 , amoutEnergyBought = 0, amoutEnergySold = 0, internalFactors =[], externalFactors =[]):
        signal.signal(signal.SIGUSR1, handler)
        parentConn,childConn = Pipe()
        self.connPipe = [parentConn,childConn]
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

    tempFactor = InternalFactor("weather", 0.001, None)
    warEvent = ExternalFactor(0.2, 0)
    petrolCrisisEvent = ExternalFactor(0.05, 0)

    energyMarket = Market(currentEnergyPrice=0.145, longtermeAttenuation= 0.99, internalFactors=[tempFactor], externalFactors=[warEvent,petrolCrisisEvent])
    externalGenerator = external(os.getpid(),(energyMarket.connPipe)[1])
    weatherGenerator = weather()

    externalProcess = Process(target= externalGenerator.run, args=())
    weatherProcess = Process(target= weatherGenerator.run, args=())

    while True:
        externalProcess.start()
        weatherProcess.start()
        externalProcess.join()
        weatherProcess.join()

        energyMarket.computeCurrentEnergyPrice()





def handler (self,sig,frame):
        if sig == signal.SIGUSR1:
            self.externalFactors[0].value = self.connPipe[0].recv()
        if sig == signal.SIGUSR2:
            self.externalFactors[1].value = self.connPipe[0].recv()

    
def computeContribution(factor):
    
    result=0
    for event in factor:
        result+=event.weight*event.value
    return result

    

