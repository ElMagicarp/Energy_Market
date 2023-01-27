# ----------------- #
# ** Les Maisons ** #
# ----------------- #

# Importation des modules

import socket
import random
from .market import Market, weatherFactor, NOMBRE_MAISON

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
    def __init__(self, quantiteEnergie, haveSolarPanel, haveWindTurbine):
        self.quantiteEnergie = quantiteEnergie
        self.haveSolarPanel = haveSolarPanel
        self.haveWindTurbine = haveWindTurbine
        self.nombrePersonnes =  random.choice([1,2,2,3,3,3,4,4,4,5,5,6])
        self.listeVoisins = listeMaison(NOMBRE_MAISON)
        self.listBesoinJour = [( -4/30 * weatherFactor[0] + 7 ) * self.nombrePersonnes]
    
    def ajoutEnergie(self, energie):
        self.quantitieEnregie += energie
    
    def utiliseEnergie(self, energie):
        self.quantiteEnergie -= energie * self.nombrePersonnes
        
    def besionEnergie(self):
        besoin = ( -4/30 * weatherFactor[0] + 7 ) * self.nombrePersonnes
        self.listBesoinJour.append(besoin)
        return besoin
    
    def demandePrix(self):
        return Market.currentEnergyPrice

    def productionEnregie(self):
        energie = 0
        if self.haveSolarPanel == True:
            energie += weatherFactor[2] * 2
        if self.haveWindTurbine == True:
            energie += weatherFactor[1] * 2/10
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



def listeMaison(nombreMaison):
    '''génère la liste des maisons'''
    return [Maison(0,random.choice([True,False]),random.choice([True,False])) for i in range(nombreMaison)]


def run(maison : Maison()):
    '''Fonction Principal pour faire les opérations sur une maison'''
    pass
