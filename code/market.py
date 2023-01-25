import sys
import multiprocessing as Process
import threading
import sysv_ipc
import socket

class internalFactors():

    def __init__(self, type ,weight, value = 0):

        self.type = type
        self.weight = weight
        self.value = value

class externalFactors():

    def __init__(self, weight, value):

        self.weight = weight
        self.value = value



class market():

    def __init__( self, currentEnergyPrice = 1, longtermeAttenuation = 1 , amoutEnergyBought = 0, amoutEnergySold = 0, internalFactors =[], externalFactors =[], ):

        self.currentEnergyPrice = currentEnergyPrice
        self.longtermeAttenuation = longtermeAttenuation
        self.amoutEnergyBought = amoutEnergyBought
        self.amoutEnergySold = amoutEnergySold
        self.internalFactors = internalFactors
        self.externalFactors = externalFactors

    def computeContribution(self, factor):
        
        result=0
        for event in factor:
            result+=event.weight*event.value
        return result

    def computeCurrentEnergyPrice(self):

        newPrice = self.longtermeAttenuation*self.currentEnergyPrice + computeContribute(self.internalFactors) + computeContribute(self.externalFactors)

    

