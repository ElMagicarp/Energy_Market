# ----------------- #
# ** Les Maisons ** #
# ----------------- #

# Importation des modules

import socket
import random

# Définition de la classe "Maison"

class Maison:
    '''
    classe représentant une maison
    ## Attribut
    - quantiteEnergie : quantité d'énergie de la maison (None)
    ## Méthodes
    - ajoutEnergie : ajoute de l'énergie à la maison (None)
    - utiliseEnergie : utilise de l'energie (None)
    - besoinEnergie : Retourne le besoin d'énergie journalier de la maison en fonction de la température et du nombre de personne
    - demandePrix : Demande le prix du kwh jounalier
    '''
    def __init__(self, quantiteEnergie, haveSolarPanel, haveWindTurbine, weatherSharedMemory, listeVoisins = []):

        self.weatherSharedMemory = weatherSharedMemory

        self.quantiteEnergie = quantiteEnergie
        self.haveSolarPanel = haveSolarPanel
        self.haveWindTurbine = haveWindTurbine
        self.nombrePersonnes =  random.choice([1,2,2,3,3,3,4,4,4,5,5,6])
        self.listeVoisins = listeVoisins
        self.listBesoinJour = [( -4/30 * weatherSharedMemory[0] + 7 ) * self.nombrePersonnes]
    
    def ajoutEnergie(self, energie):
        self.quantitieEnregie += energie
    
    def utiliseEnergie(self, energie):
        self.quantiteEnergie -= energie * self.nombrePersonnes
        
    def besionEnergie(self):
        besoin = ( -4/30 * self.weatherSharedMemory[0] + 7 ) * self.nombrePersonnes
        self.listBesoinJour.append(besoin)
        return besoin
    
    def demandePrix(self):
        pass
        #return Market.currentEnergyPrice  " donner par msg socket, on n'a jamais accée a l'objet market"

    def productionEnregie(self):
        energie = 0
        if self.haveSolarPanel == True:
            energie += self.weatherSharedMemory[2] * 2
        if self.haveWindTurbine == True:
            energie += self.weatherSharedMemory[1] * 2/10
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



def listeMaison(nombreMaison, weatherSharedMemory):

    '''génère la liste des maisons'''
    listeVoisins = [Maison(0,random.choice([True,False]),random.choice([True,False]),weatherSharedMemory=weatherSharedMemory) for i in range(nombreMaison)]
    for maison in listeVoisins:
        maison.listeVoisins=listeVoisins


def run(nombreMaison, weatherSharedMemory):

    '''Fonction Principal initialisation des maisons et lancement des routines'''
    pass

def routineMaison(maison):

    '''routine de la maison avec comm avec market et autres maisons'''
    pass