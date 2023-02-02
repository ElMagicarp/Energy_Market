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
    '''
    classe représentant une maison
    ## Attribut
    - id : identifiant de la maison (int)
    - key : clé de la maison (int)
    - client_socket : socket de la maison (socket)
    - weatherSharedMemory : mémoire partagée de la météo (list)
    - coutEnergie : cout de l'énergie de la maison consommé par le market (float)
    - quantiteEnergie : quantité d'énergie de la maison (None)
    - haveSolarPanel : retourne Vrai si la maison possède des panneaux solaires (Bool)
    - haveWindTurbine : retounre Faux si la maison possède une éoliène (Bool)
    - havePikachu : retourne Vrai si la maison possède un pikachu (Bool)
    - nombrePersonnes : Nombre de personne dans une maison (int)
    - listeVoisins : Liste des maisons dans notre système (list)
    - besoinJour : Besoin d'énergie journalier de la maison (float)
    - jour : jour de l'année (int)
    - nombreJour : nombre de jour dans l'année (int)
    ## Méthodes
    - besoinEnergie : Retourne le besoin d'énergie journalier de la maison en fonction de la température et du nombre de personne (float)
    - productionEnergie : Retourne la quantité d'énergie quotidienne fournie par la maison et l'ajoute à quantiteEnergie (float)
    - vendreEnergie : envoie de socket la quantité d'énergie vendue à la maison (None)
    - acheterEnergie : envoie de socket la quantité d'énergie achetée à la maison (None)
    - isHomeAlive : envoie de socket un message de vie à la maison (None)
    - miseSurMarcher : protocole message queue pour mettre la maison sur le marché (None)
    - creatSocket : création de socket entre la maison et le marché (None)
    - setSocketConnection : création de socket entre la maison et le marché (None)
    - socket_handler : envoie des messages de socket entre la maison et le marché (None)
    - runHome : fonction principale de la maison (None)
    '''

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

    
    def isHomeAlive(self,HOST,PORT):

        self.client_socket = setSocketConnection(HOST, PORT)
        self.client_socket.send(str(["alive"]).encode())
        time.sleep(1)


    def miseSurMarcher(self,HOST,PORT,msgQ):

        msgQ.send(float(maison.quantiteEnergie).encode(),type  = maison.id)
        try:
            msg, t = msgQ.receive(False, type  = maison.id)
        #    print("message reçu/"+str(t))
            maison.vendreEnergie(HOST,PORT)
        except:
            msgQ.send(float(maison.quantiteEnergie).encode(),type  = maison.id)
            maison.quantiteEnergie = 0
     


    
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
    
  #  print("\033[96m"+"Connected to server "+"\033[0m")
    try:
        data = s.recv(4096)
        data = data.decode('utf-8')
        msg=eval(str(data))
       # print("\033[96m"+"maison "+str(maison.id)+" RECEIVED "+str(msg)+"\033[0m")
        if msg[0] == 2:
            payment = msg[1][1]
            energieAchete = msg[1][0]

          #  print("\033[96m"+"normalement je mets à jour le coût"+"\033[0m")
          #  print("\033[96m"+"avant € "+str(maison.coutEnergie)+"\033[0m")

            maison.coutEnergie -= payment
            maison.quantiteEnergie += energieAchete

          #  print("\033[96m"+"apres € "+str(maison.coutEnergie)+"\033[0m")
          #  print("\033[96m"+"Energie dispo "+str(maison.quantiteEnergie)+"\033[0m")
        
            newS = setSocketConnection(HOST, PORT)
            newS.send(str([3,payment]).encode())
            time.sleep(0.00001)

        elif msg[0] == 3:
          #  print("\033[96m"+"normalement je suis payé"+"\033[0m")
           # print("\033[96m"+"normalement je met a jour le cout"+"\033[0m")
          # print("\033[96m"+"avant € "+str(maison.coutEnergie)+"\033[0m")
            maison.coutEnergie += msg[1]
            maison.quantiteEnergie = 0
           # print("\033[96m"+"apres € "+str(maison.coutEnergie)+"\033[0m")

        elif msg[0] == 5:
            invoice = [maison.quantiteEnergie,msg[1]]
            newS = setSocketConnection(HOST, PORT)
            s.send(str([2,invoice]).encode())
            time.sleep(0.00001)

        s.close()

    except:
        pass
       # print("\033[91m"+"ERROR MESSAGE UNRECEIVABLE"+"\033[0m")



def runHome( HOST, PORT,home, list,sem):
    #_mise_maison_varGlobale_-------------------------------------------------------------------------------
    global maison
    global weatherShared
    weatherShared = list
    maison = home
    maison.weatherSharedMemory = weatherShared
    print(maison.weatherSharedMemory)

    #print("\033[96m"+"run maison "+str(maison.id)+"\033[0m")

    #_initialisation_messageQueue_-----------------------------------------------------------------------
    try:
        global mq
        mq = sysv_ipc.MessageQueue(maison.key)
        #print("\033[96m"+"hello messageQueue "+str(maison.key)+" I am "+str(maison.id)+"\033[0m")
    except:
        #print("\033[96m"+"Cannot connect to message queue", maison.key, ", terminating."+"\033[0m")
        sys.exit(1) 

    #_routine_-------------------------------------------------------------------------------------------
    timeRef = time.monotonic_ns()
    timeOut = 0
    
    while maison.jour < maison.nombreJour and timeOut < 4000000000:

        #print("\033[96m"+"timeOut "+str(timeOut)+" jour "+str(maison.jour)+" id "+str(maison.id)+"\033[0m")

        if int(maison.jour) == int(list[3]):
            #_Calcul_énergie_maison_disponible_----------------------------------------------------------
            maison.quantiteEnergie =  maison.productionEnregie() - maison.besionEnergie()

            #_résolution_énergie_équilibre_--------------------------------------------------------------
            if maison.quantiteEnergie > 0 :
               # print ("\033[96m"+"je vends"+"\033[0m")
                maison.miseSurMarcher(HOST,PORT,mq)
                
            elif maison.quantiteEnergie < 0 :
                try:
                    msg,t= mq.receive(False)
                    msg = msg.decode()
                   # print("message reçu"+str(msg)+"/"+str(t)) 
                    while maison.quantiteEnergie < 0 :
                        try:
                            msg,t  = mq.receive()
                            msg = msg.decode()
                           # print("message reçu"+str(msg)+"/"+str(t))
                            maison.quantiteEnergie += float(msg)
                        except:
                            #print ("\033[96m"+"j'achete"+"\033[0m")
                            maison.acheterEnergie(HOST,PORT)

                
                    if maison.quantiteEnergie > 0 :
                        #print ("\033[96m"+"je vends"+"\033[0m")
                        maison.miseSurMarcher(HOST,PORT,mq)
                except: 
                   # print ("\033[96m"+"j'achete"+"\033[0m")
                    maison.acheterEnergie(HOST,PORT)
                
            maison.jour+= 1
            #print ("\033[96m"+"jour "+str(maison.jour)+" quantité energie maison "+str(maison.id)+" : "+str(maison.quantiteEnergie)+"\033[0m")

            timeRef = time.monotonic_ns()
            sem.release()

        else:
            timeOut = time.monotonic_ns() - timeRef
            time.sleep(0.005)


    
            #print("\033[96m"+"ERROR COMPARE DATE"+"\033[0m")


               
    print("\033[96m"+"fin maison regular "+str(maison.id)+"\033[0m")
    print("\033[96m"+"timeOut "+str(timeOut)+" jour "+str(maison.jour)+"/"+str(maison.nombreJour)+" id"+str(maison.id)+"\033[0m")
    os.kill(os.getpid(), signal.SIGKILL)
    
