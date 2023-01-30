# ----------------- #
# ** Les Maisons ** #
# ----------------- #

# Importation des modules

import socket
import random

#-----------------------------------------------
# Définition de la classe "Maison"

class Maison:
    '''
    classe représentant une maison
    ## Attribut
    - quantiteEnergie : quantité d'énergie de la maison (None)
    - haveSolarPanel : retourne Vrai si la maison possède des panneaux solaires (Bool)
    - haveWindTurbine : retounre Faux si la maison possède une éoliène (Bool)
    - nombrePersonnes : Nombre de personne dans une maison (int)
    - listeVoisins : Liste des maisons dans notre système (list)
    _ listBesoinListe : liste qui énumère pour chaque jour la consommation énergétique nécessaire (float)
    ## Méthodes
    - besoinEnergie : Retourne le besoin d'énergie journalier de la maison en fonction de la température et du nombre de personne (float)
    - demandePrix : Demande le prix du kwh jounalier (float)
    - productionEnergie : Retourne la quantité d'énergie quotidienne fournie par la maison et l'ajoute à quantiteEnergie (float)
    - faireUneSocket : process de socket entre genHome et market
    - run : actions quotidiennes d'une maison
    '''
    def __init__(self, quantiteEnergie, haveSolarPanel, haveWindTurbine, havePikachu, weatherSharedMemory, listeVoisins = [], coutEnergie =0, prixEnergie = 0):
        self.prixEnergie = prixEnergie
        self.weatherSharedMemory = weatherSharedMemory
        self.coutEnergie = coutEnergie
        self.quantiteEnergie = quantiteEnergie
        self.haveSolarPanel = haveSolarPanel
        self.haveWindTurbine = haveWindTurbine
        self.havePikachu = havePikachu
        self.nombrePersonnes =  random.choice([1,2,2,3,3,3,4,4,4,5,5,6])
        self.listeVoisins = listeVoisins
        self.listBesoinJour = [( -4/30 * weatherSharedMemory[0] + 7 ) * self.nombrePersonnes]
        
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
        
    
    
    def faireUneSocket(self):
        "Créer une socket pour se connecter au serveur"

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:

            "Se connecter au serveur"
            client_socket.connect(("localhost", 2000))

            "Envoyer un message au serveur"
            client_socket.sendall(str(self.quantiteEnergie).encode())

            "Recevoir un message du serveur"
            data = client_socket.recv(1024)
            print("echo> ", data.decode())

            "Fermer la connexion"
            client_socket.close()
    
    def socket_handler(self, s, a):
        global client
        with s:
            print("Connected to client: ", a)
            data = s.recv(1024)
            msg = data.decode()[0]
            if msg[0] == 2:
                payment = msg[1][1]
                self.coutEnergie -= payment
                s.send([3,payment].encode)

            elif msg[0] == 3:
                self.coutEnergie += msg[1]

            elif msg[0] == 5:
                invoice = [msg[1],self.prixEnergie*msg[1]]
                s.send([2,invoice].encode)

            elif msg[0] == "stop":
                print("Terminating time server!")
                serve = False
            print("Disconnecting from client: ", a)

    def routineMaison(self):
        '''routine de la maison avec comm avec market et autres maisons'''
        pass
            
            
    def run(self):
        '''Fonction Principal pour faire les opérations sur une maison'''
        self.quantiteEnergie -=  self.besionEnergie()
        if self.quantiteEnergie < 0 :
            energieManquante = abs(self.quantiteEnergie)
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
            "Si les voisins n'ont pas assez d'energie, la maison achète de l'énerge au Market"
            if self.quantiteEnergie < 0:
                self.quantiteEnergie = 0 
            "Processus de payement de l'énergie quotidienne manquante"
            # TODO : faut faire un send( ? ) pour récup le prix du kWh imposé par le market
            self.coutEnergie += energyMarket.currentEnergyPrice * energieManquante
            
                
                    

#-----------------------------------------------
# Création de la liste des maisons de notre système

def listeMaison(nombreMaison, weatherSharedMemory):

    '''génère la liste des maisons'''
    listeVoisins = [Maison(0,random.choice([True,False]),
                    random.choice([True,False]),
                    random.choices([True, False], weights=[0.1, 0.9])[0],
                    weatherSharedMemory=weatherSharedMemory) for i in range(nombreMaison)]
    for maison in listeVoisins:        maison.listeVoisins=listeVoisins


def run(nombreMaison, weatherSharedMemory):

    '''Fonction Principal initialisation des maisons et lancement des routines'''
    pass
    '''
    for maison in listeVoisins:
        process = multiprocessing.Process(target=maison.routineMaison, args=(,))
    '''


