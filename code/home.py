# Importation des modules
import sys 
import socket
import random
import threading
import sysv_ipc

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

    def __init__(self, quantiteEnergie, haveSolarPanel, haveWindTurbine, havePikachu, weatherSharedMemory, listeVoisins = [], coutEnergie =0, key = 666, id = None, jour = -1):
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

    def vendreEnergie(self):
        self.client_socket.send(str([4,self.quantiteEnergie]).encode())

    def acheterEnergie(self):
        self.client_socket.send(str([1,abs(self.quantiteEnergie)]).encode())

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
    


def socket_handler(s):
    global client
    while client:

        '''
        msg == 1 -> requête d'éntergie
        msg == 2 -> requête de paiement
        msg == 3 -> ack paiement
        msg == 4 -> requête de prix de vente de float kWh
        msg == 5 -> réponse à 4 avec float €
        msg == "stop" -> requête de fermeture

        '''
        print("Connected to server ")
        data = s.recv(4096)
        data = data.decode('utf-8')
        msg=eval(data)
        if msg[0] == 2:
            payment = msg[1][1]
            energieAchete = msg[1][0]
            maison.coutEnergie -= payment
            maison.quantiteEnergie += energieAchete
            s.send(str([3,payment]).encode())

        elif msg[0] == 3:
            maison.coutEnergie += msg[1]

        elif msg[0] == 5:
            invoice = [maison.quantiteEnergie,msg[1]] 
            s.send(str([2,invoice]).encode())

        elif msg[0] == "stop":
            print("Terminating client")
            client = False
            print("Disconnecting from server")



def runHome( HOST, PORT, homeObj):

    #_mise_maison_varGlobale_-------------------------------------------------------------------------------
    global maison
    maison = homeObj

    print("run maison "+str(maison.id))

    #_initialisation_socket_--------------------------------------------------------------------------------
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as clientSocket:
        clientSocket.connect((HOST, PORT))
        print("Global socket verif maison "+str(maison.id)+" "+str(clientSocket))

        socketHandler = threading.Thread(target = socket_handler, args = (clientSocket,))
        socketHandler.start()

        maison.client_socket = clientSocket

        #_initialisation_messageQueue_-----------------------------------------------------------------------
        try:
            global mq
            mq = sysv_ipc.MessageQueue(maison.key)
            print("hello messageQueue "+str(maison.key)+" I am "+str(maison.id))
        except:
            print("Cannot connect to message queue", maison.key, ", terminating.")
            sys.exit(1) 
        
        print("socket verif maison "+str(maison.id)+" "+str(clientSocket))

        #_routine_-------------------------------------------------------------------------------------------
        while client:
            
            print("maison "+str(maison.id)+" jour "+str(maison.jour))
            print("maison "+str(maison.id)+" sharedMemory "+str(maison.weatherSharedMemory))

            if int(maison.jour) < int(maison.weatherSharedMemory[3]):
                #_Calcul_énergie_maison_disponible_----------------------------------------------------------
                maison.quantiteEnergie =  maison.productionEnregie() - maison.besionEnergie()

                #_résolution_énergie_équilibre_--------------------------------------------------------------
                if maison.quantiteEnergie > 0 :
                    maison.vendreEnergie()
                else :
                    maison.acheterEnergie()

                maison.jour = maison.weatherSharedMemory[3] 
                print ("jour "+str(maison.jour)+" quantité energie maison "+str(maison.id)+" : "+str(maison.quantiteEnergie))
    
     
    print("fin maison "+str(maison.id))
