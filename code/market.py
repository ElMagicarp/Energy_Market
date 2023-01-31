#symbole triangle rempli
import os
from multiprocessing import Process, Manager, Pipe, Semaphore
import signal
import threading 
import socket
import select
import concurrent.futures
import time
import csv
from external import External
from weather import Weather
from genHome import runGenHome

global externalEvent
serve = True

def handler (sig,frame):
        if sig == signal.SIGUSR1:
            print("\n#EVENT#\n")
            event = (pipe["parentConn"].recv())
            externalGenerator.listCoef = event
            print(externalGenerator.listCoef)
            externalEvent["warEvent"].value=externalGenerator.listCoef['warEvent']
            externalEvent["petrolCrisisEvent"].value=externalGenerator.listCoef['petrolCrisisEvent']


class Factor():

    def __init__(self, type ,weight, value = 0):
        self.type = type
        self.weight = weight
        self.value = value


class Market():

    def __init__(self, currentEnergyPrice = 1, longtermeAttenuation = 1 , amoutEnergyBought = 0, amoutEnergySold = 0, internalFactors = {}, externalFactors = {}, connPipe = {}):
        self.connPipe = connPipe
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
            print (self.externalFactors[event].type)
            print (str(self.externalFactors[event].value) + "\n")
            if self.externalFactors[event].value == 1:
                res.append(self.externalFactors[event].type)
        return res


def computeContribution(factor):
    result=0
    for event in factor:
        result+=(factor[event]).weight*(factor[event]).value
    return result

def socketConnect(HOST, PORT):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setblocking(False)
        server_socket.bind((HOST, PORT))
        server_socket.listen(10)
        with concurrent.futures.ThreadPoolExecutor(max_workers = 10) as executor:
            while serve:
                readable, writable, error = select.select([server_socket], [], [], 1)
                if server_socket in readable:
                    client_socket, address = server_socket.accept()
                    executor.submit(socket_handler, client_socket, address)
                    
def socket_handler(s, a):

    '''
    msg == 1 -> requête d'énergie
    msg == 2 -> requête de paiement
    msg == 3 -> ack paiement
    msg == 4 -> requête de prix de vente de float kWh
    msg == 5 -> réponse à 4 avec float €
    msg == "stop" -> requête de fermeture

    '''
    global serve
    with s:
        print("Connected to client: ", a)
        try:
            data = s.recv(4096)
            data = data.decode('utf-8')
            msg=eval(str(data))
            print("SERVER RECEIVED "+str(msg))

            if msg[0] == 1:
                invoice = [msg[1],energyMarket.currentEnergyPrice*msg[1]]
                s.send(str([2,invoice]).encode())
                time.sleep(0.00001)

            elif msg[0] == 2:
                payment = msg[1][1]
                energyMarket.energyBought += msg[1][0]
                s.send(str([3,payment]).encode())
                time.sleep(0.00001)

            elif msg[0] == 3:
                print("\033[92m"+"Energie sold avant "+str(energyMarket.amoutEnergySold )+"\033[0m")
                energyMarket.amoutEnergySold += msg[1]/energyMarket.currentEnergyPrice
                print("\033[92m"+"Energie sold apres "+str(energyMarket.amoutEnergySold )+"\033[0m")

            elif msg[0] == 4:
                s.send(str([5,energyMarket.currentEnergyPrice*msg[1]]).encode())
                time.sleep(0.00001)

            elif msg[0] == "stop":
                print("Terminating time server!")
                serve = False
                print("Disconnecting from client: ", a)

        except:
            print("\033[91m"+"ERROR MESSAGE UNRECEIVABLE"+"\033[0m")


def loopbackKill(HOST, PORT):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((HOST, PORT))
        client_socket.send(str(["stop"]).encode())


def routine(NOMBRE_JOUR):
    Yprice = []
    #_routine_--------------------------------------------------------------------------------
    Yprice = []
    weatherFactor[3]=0

    for i in range(NOMBRE_JOUR):
        print("JOUR "+ str(i)+"\n")
        print("PID "+str(os.getpid()))

        #_initialisation_pipe_weatherFactor_---------------------------------------------------
        parentConn, childConn = Pipe()

        global pipe
        pipe = {"parentConn": parentConn
                ,"childConn": childConn}
        energyMarket.connPipe = pipe

        #_initialisation_Process_updateFacteurCalcul-------------------------------------------
        externalProcess = Process(target= externalGenerator.run, args=(externalGenerator,energyMarket.connPipe["childConn"],))
        weatherProcess = Process(target= weatherGenerator.dataJour, args=(weatherFactor,weatherSem,))

        #_lunch_Process_updateFacteurCalcul---------------------------------------------------
        externalProcess.start()
        weatherProcess.start()

        #_wait_Process_updateFacteurCalcul----------------------------------------------------
        externalProcess.join()
        print("\033[91m"+"Current Event war {}, petrol {}".format(str(energyMarket.externalFactors["warEvent"].value),str(energyMarket.externalFactors["petrolCrisisEvent"].value))+"\033[00m")
        weatherProcess.join()

        #_wait_update_weatherFactor------------------------------------------------------------
        energyMarket.externalFactors = externalEvent
        weatherSem.acquire()

        #_update_weatherFactor----------------------------------------------------------------
        tempFactor.value = weatherFactor[0]
        print("\033[94m "+"Current temperature {}".format(str(tempFactor.value))+"\033[00m")

        windSpeedFactor.value = weatherFactor[1]
        print("\033[94m "+"Current wind {}".format(str(windSpeedFactor.value))+"\033[00m")

        sunBeamFactor.value = weatherFactor[2]
        print("\033[94m "+"Current sunBeam {}".format(str(sunBeamFactor.value))+"\033[00m")

        #_calcul_currentEnergyPrice-----------------------------------------------------------
        energyMarket.computeCurrentEnergyPrice()
        Yprice.append(energyMarket.currentEnergyPrice)

        print("\033[94m "+"Current energy price {}\n".format(str(energyMarket.currentEnergyPrice))+"\033[00m")

        weatherFactor[3]+=1

    header = ['prixJour']
    with open('price.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for prixJour in Yprice:
            writer.writerow([prixJour])
    


if __name__ == '__main__':

    #_initialisation_SignalHandler_---------------------------------------------------------------
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
        petrolCrisisEvent = Factor("petrolCrisisEvent",0.1, 0)

        #_initialisation_Objets_parent/child_-----------------------------------------------------
        externalEvent = {"warEvent":warEvent
                        ,"petrolCrisisEvent":petrolCrisisEvent}

        global energyMarket
        global externalGenerator
        global weatherGenerator
        energyMarket = Market(  currentEnergyPrice = 0.145, 
                                longtermeAttenuation = 0.99, 
                                internalFactors = {"bought":energyBought
                                                ,"sold":energySold
                                                ,"temperature":tempFactor
                                                ,"wind":windSpeedFactor
                                                ,"sunbeam":sunBeamFactor},
                                externalFactors = externalEvent)
        event=[0,0]
        externalGenerator = External()
        weatherGenerator = Weather(0)

        #_initialisation_sharedMemory_weatherFactor_----------------------------------------------
        global weatherFactor
        weatherFactor = manager.list([-1,0,0,0]) #["temperature", "wind", "sunbeam", "jour"]

        #_initialisation_semaphore_---------------------------------------------------------------
        global weatherSem
        global endSimulation
        weatherSem = Semaphore(0) #wait update weatherFactor
        endSimulation = Semaphore(0) #wait end simulation
        genHomeFinished = Semaphore(0) 

        #_initialisation_Server_Socket_-----------------------------------------------------------
        HOST = "localhost"
        PORT = 1789
        socketGestioner = threading.Thread (target =socketConnect,args=(HOST, PORT,))
        socketGestioner.start()

        #_creation_maisons_-----------------------------------------------------------------------
        NOMBRE_JOUR = 3
        NOMBRE_HOME = 1
        KEY = 666
        genHomeProcess = Process(target= runGenHome, args=(HOST,PORT,NOMBRE_HOME,weatherFactor,KEY,genHomeFinished,NOMBRE_JOUR,))
        genHomeProcess.start()
        

        #_initialisation_durée_simulation---------------------------------------------------------
        routine(NOMBRE_JOUR)

        #_Socket_closure_-------------------------------------------------------------------------
        loopbackKill(HOST, PORT)
        socketGestioner.join()
        genHomeProcess.join()
        print("End of Simulation")
        
