# Importation des modules
import sys 
import socket
import random
import threading
from multiprocessing import Semaphore
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
    - quantiteEnergie : quantité d'énergie de la maison (None)
    - haveSolarPanel : retourne Vrai si la maison possède des panneaux solaires (Bool)
    - haveWindTurbine : retounre Faux si la maison possède une éoliène (Bool)
    - nombrePersonnes : Nombre de personne dans une maison (int)
    - listeVoisins : Liste des maisons dans notre système (list)
    - listBesoinListe : liste qui énumère pour chaque jour la consommation énergétique nécessaire (float)
    -
    ## Méthodes
    - besoinEnergie : Retourne le besoin d'énergie journalier de la maison en fonction de la température et du nombre de personne (float)
    - demandePrix : Demande le prix du kwh jounalier (float)
    - productionEnergie : Retourne la quantité d'énergie quotidienne fournie par la maison et l'ajoute à quantiteEnergie (float)
    - faireUneSocket : process de socket entre genHome et market
    - run : actions quotidiennes d'une maison
    '''

    def __init__(self, quantiteEnergie, haveSolarPanel, haveWindTurbine, havePikachu, weatherSharedMemory, listeVoisins = [], coutEnergie =0, key = 666, id = None, jour = -1, nombreJour=0):
        self.id = id
        self.key = key
        self.client_socket = None
        self.weatherSharedMemory = weatherSharedMemory
        self.coutEnergie = coutEnergie
        self.quantiteEnergie = quantiteEnergie
        self.haveSolarPanel = haveSolarPanel
        self.haveWindTurbine = haveWindTurbine
        self.havePikachu = havePikachu
        self.nombrePersonnes =  random.choice([1,2,2,3,3,3,4,4,4,5,5,6])
        self.listeVoisins = listeVoisins
        self.listBesoinJour = [( -4/30 * weatherSharedMemory[0] + 7 ) * self.nombrePersonnes]
        self.jour = jour
        self.nombreJour = nombreJour
        
    def besionEnergie(self):
        besoin = ( -4/30 * self.weatherSharedMemory[0] + 7 ) * self.nombrePersonnes
        self.listBesoinJour.append(besoin)
        return besoin
    
    def demandePrix(self):
        pass
        #return Market.currentEnergyPrice  " donner par msg socket, on n'a jamais accée a l'objet market"

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

        '''
        "Vérifie si les voisins on des surplus d'énergie"
        for voisin in self.listeVoisins:
            if voisin.quantiteEnergie > 0:
                if self.quantiteEnergie + voisin.quantiteEnergie >0:
                    voisin.quantiteEnergie -= self.quantiteEnergie
                    # TODO : faut faire un send( ? ) pour récup le prix du kWh imposé par le market
                    voisin.coutEnergie -= energyMarket.currentEnergyPrice * self.quantiteEnergie
                    self.quantiteEnergie = 0
                    break
                else:
                    self.quantiteEnergie += voisin.quantiteEnergie
                    voisin.quantiteEnergie = 0
        '''

    def routineEchangeEnergie(self):
        pass
    
def creatSocket(HOST,PORT):
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    clientSocket.connect((HOST, PORT))
    return clientSocket

def setSocketConnection(HOST, PORT):
    #_initialisation_socket_--------------------------------------------------------------------------------7
    clientSocket = creatSocket(HOST, PORT)
    print("\033[96m"+"Global socket verif maison "+str(maison.id)+" "+str(clientSocket)+"\033[0m")
    socketHandler = threading.Thread(target = socket_handler, args = (clientSocket,HOST,PORT,))
    socketHandler.start()
    print("\033[96m"+"socket verif maison "+str(maison.id)+" "+str(maison.client_socket)+"\033[0m")
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
    
    print("\033[96m"+"Connected to server "+"\033[0m")
    try:
        data = s.recv(4096)
        data = data.decode('utf-8')
        msg=eval(str(data))
        print("\033[96m"+"maison "+str(maison.id)+" RECEIVED "+str(msg)+"\033[0m")
        if msg[0] == 2:
            payment = msg[1][1]
            energieAchete = msg[1][0]

            print("\033[96m"+"normalement je met a jour le cout"+"\033[0m")
            print("\033[96m"+"avant € "+str(maison.coutEnergie)+"\033[0m")

            maison.coutEnergie -= payment
            maison.quantiteEnergie += energieAchete

            print("\033[96m"+"apres € "+str(maison.coutEnergie)+"\033[0m")
            print("\033[96m"+"Energie dispo "+str(maison.quantiteEnergie)+"\033[0m")
        
            newS = setSocketConnection(HOST, PORT)
            newS.send(str([3,payment]).encode())
            time.sleep(0.00001)

        elif msg[0] == 3:
            print("\033[96m"+"normalement je suis payé"+"\033[0m")
            print("\033[96m"+"normalement je met a jour le cout"+"\033[0m")
            print("\033[96m"+"avant € "+str(maison.coutEnergie)+"\033[0m")
            maison.coutEnergie += msg[1]
            print("\033[96m"+"apres € "+str(maison.coutEnergie)+"\033[0m")

        elif msg[0] == 5:
            invoice = [maison.quantiteEnergie,msg[1]]
            newS = setSocketConnection(HOST, PORT)
            s.send(str([2,invoice]).encode())
            time.sleep(0.00001)

        s.close()

    except:
        print("\033[91m"+"ERROR MESSAGE UNRECEIVABLE"+"\033[0m")



def runHome( HOST, PORT, homeObj):
    #_mise_maison_varGlobale_-------------------------------------------------------------------------------
    global maison
    maison = homeObj

    print("\033[96m"+"run maison "+str(maison.id)+"\033[0m")

    #_initialisation_messageQueue_-----------------------------------------------------------------------
    try:
        global mq
        mq = sysv_ipc.MessageQueue(maison.key)
        print("\033[96m"+"hello messageQueue "+str(maison.key)+" I am "+str(maison.id)+"\033[0m")
    except:
        print("\033[96m"+"Cannot connect to message queue", maison.key, ", terminating."+"\033[0m")
        sys.exit(1) 

    #_routine_-------------------------------------------------------------------------------------------
    while maison.jour < maison.nombreJour:
        
        try:
            if int(maison.jour) < int(maison.weatherSharedMemory[3]):
                #_Calcul_énergie_maison_disponible_----------------------------------------------------------
                maison.quantiteEnergie =  maison.productionEnregie() - maison.besionEnergie()

                #_résolution_énergie_équilibre_--------------------------------------------------------------
                if maison.quantiteEnergie > 0 :
                    maison.vendreEnergie(HOST,PORT)
                elif maison.quantiteEnergie < 0 :
                    maison.acheterEnergie(HOST,PORT)

                maison.jour = maison.weatherSharedMemory[3]
                print ("\033[96m"+"jour "+str(maison.jour)+" quantité energie maison "+str(maison.id)+" : "+str(maison.quantiteEnergie)+"\033[0m")

            else :
                maison.jour = maison.weatherSharedMemory[3]

        except:
               print("\033[96m"+"fin maison "+str(maison.id)+"\033[0m")
               os.kill(os.getpid(), signal.SIGKILL)

    print("\033[96m"+"fin maison "+str(maison.id)+"\033[0m")
    os.kill(os.getpid(), signal.SIGKILL)
    
