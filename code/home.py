# Importation des modules
import sys 
import socket
import random
import threading
from multiprocessing import Semaphore, shared_memory
import sysv_ipc
import time
import os
import signal


# Définition de la classe "Maison"

client = True

class Maison:

    def __init__(self, quantiteEnergie, haveSolarPanel, haveWindTurbine, havePikachu, listeVoisins = [], coutEnergie =0, key = 666, id = None, jour = 0, nombreJour=0):
        self.id = id
        self.key = key
        self.client_socket = None
        self.weatherSharedMemory = []
        self.coutEnergie = coutEnergie
        self.quantiteEnergie = quantiteEnergie
        self.haveSolarPanel = haveSolarPanel
        self.haveWindTurbine = haveWindTurbine
        self.havePikachu = havePikachu
        self.nombrePersonnes =  random.choice([1,2,2,3,3,3,4,4,4,5,5,6])
        self.listeVoisins = listeVoisins
        self.besoinJour = 0
        self.jour = jour
        self.nombreJour = nombreJour
        
    def besionEnergie(self):
        besoin = ( -4/30 * self.weatherSharedMemory[0] + 7 ) * self.nombrePersonnes
        self.besoinJour = besoin
        return besoin

    def productionEnregie(self):
        '''Production d'énergie autonome quotidenne en kWh'''
        energie = 0
        if self.haveSolarPanel == True:
            energie += self.weatherSharedMemory[2] * 2
        if self.haveWindTurbine == True:
            energie += self.weatherSharedMemory[1] * 2/10
            self.quantiteEnergie += energie
        if self.havePikachu == True:
            energie += 2.5
        
        return energie

    def vendreEnergie(self,HOST,PORT):

        self.client_socket=setSocketConnection(HOST, PORT)
        self.client_socket.send(str([4,self.quantiteEnergie]).encode())


    def acheterEnergie(self,HOST,PORT):

        self.client_socket=setSocketConnection(HOST, PORT)
        self.client_socket.send(str([1,abs(self.quantiteEnergie)]).encode())

    def miseSurMarcher(self,HOST,PORT,msgQ):

        msgQ.send(float(self.quantiteEnergie).encode(),type  = self.id)
        try:
            msg, t = msgQ.receive(False, type  = self.id)
        #    print("message reçu/"+str(t))
            self.vendreEnergie(HOST,PORT)
        except:
            msgQ.send(float(self.quantiteEnergie).encode(),type  = self.id)
            self.quantiteEnergie = 0
     


    
def creatSocket(HOST,PORT):
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    clientSocket.connect((HOST, PORT))
    return clientSocket

def setSocketConnection(HOST, PORT):
    #_initialisation_socket_--------------------------------------------------------------------------------
    clientSocket = creatSocket(HOST, PORT)
   # print("\033[96m"+"Global socket verif maison "+str(maison.id)+" "+str(clientSocket)+"\033[0m")
    socketHandler = threading.Thread(target = socket_handler, args = (clientSocket,HOST,PORT,))
    socketHandler.start()
    return clientSocket


def socket_handler(s, HOST,PORT):
    '''
    msg == 1 -> requête d'éntergie
    msg == 2 -> requête de paiement
    msg == 3 -> ack paiement
    msg == 4 -> requête de prix de vente de float kWh
    msg == 5 -> réponse à 4 avec float €
    msg == "stop" -> requête de fermeture
    '''
    

    try:
        data = s.recv(4096)
        data = data.decode('utf-8')
        msg=eval(str(data))

        if msg[0] == 2:
            payment = msg[1][1]
            energieAchete = msg[1][0]
            maison.coutEnergie -= payment
            maison.quantiteEnergie += energieAchete
            newS = setSocketConnection(HOST, PORT)
            newS.send(str([3,payment]).encode())
            time.sleep(0.00001)

        elif msg[0] == 3:
            maison.coutEnergie += msg[1]
            maison.quantiteEnergie = 0

        elif msg[0] == 5:
            invoice = [maison.quantiteEnergie,msg[1]]
            newS = setSocketConnection(HOST, PORT)
            s.send(str([2,invoice]).encode())
            time.sleep(0.00001)

        s.close()

    except:
        pass



def runHome( HOST, PORT,home, list,sem,nouveauJour):
    #_mise_maison_varGlobale_-------------------------------------------------------------------------------
    global maison
    global weatherShared
    weatherShared = list
    maison = home
    maison.weatherSharedMemory = weatherShared
    print(maison.weatherSharedMemory)

    #_initialisation_messageQueue_-----------------------------------------------------------------------
    try:
        global mq
        mq = sysv_ipc.MessageQueue(maison.key)
    except:
        sys.exit(1) 

    #_routine_-------------------------------------------------------------------------------------------
    timeRef = time.monotonic_ns()
    timeOut = 0
    
    while maison.jour < maison.nombreJour and timeOut < 4000000000:

        if int(maison.jour) == int(list[3]):
            nouveauJour.acquire()
            #_Calcul_énergie_maison_disponible_----------------------------------------------------------
            maison.quantiteEnergie =  maison.productionEnregie() - maison.besionEnergie()

            #_résolution_énergie_équilibre_--------------------------------------------------------------
            if maison.quantiteEnergie > 0 :
                maison.miseSurMarcher(HOST,PORT,mq)
                
            elif maison.quantiteEnergie < 0 :
                try:
                    msg,t= mq.receive(False)
                    msg = msg.decode()
                    while maison.quantiteEnergie < 0 :
                        try:
                            msg,t  = mq.receive()
                            msg = msg.decode()
                            maison.quantiteEnergie += float(msg)
                        except:
                            maison.acheterEnergie(HOST,PORT)

                
                    if maison.quantiteEnergie > 0 :
                        maison.miseSurMarcher(HOST,PORT,mq)
                except: 
                    maison.acheterEnergie(HOST,PORT)

            maison.jour+= 1

            timeRef = time.monotonic_ns()
            nouveauJour.release()
            sem.release()

        else:
            timeOut = time.monotonic_ns() - timeRef
            time.sleep(0.005)

               
    print("\033[96m"+"fin maison regular "+str(maison.id)+"\033[0m")
    print("\033[96m"+"timeOut "+str(timeOut)+" jour "+str(maison.jour)+"/"+str(maison.nombreJour)+" id"+str(maison.id)+"\033[0m")