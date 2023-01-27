# ----------------- #
# ** Les Maisons ** #
# ----------------- #

# Importation des modules

import socket
import random
from market import weatherFactor


# Définition de la classe "Maison"

class Maison:
    '''
    classe représentant une maison
    ## Attribut
    - quantiteEnergie : quantité d'énergie de la maison (None)
    ## Méthodes
    - ajoutEnergie : ajoute de l'énergie à la maison (None)
    - utiliseEnergie : utilise de l'energie (None)
    - envoieEnergie : envoie de l'énergie au marché (None)
    '''
    def __init__(self, quantiteEnergie):
        self.quantiteEnergie = quantiteEnergie
        self.nombrePersonnes =  random.choice([1,2,2,3,3,3,4,4,4,5,5,6])
    
    def ajoutEnergie(self, energie):
        self.quantitieEnregie += energie
    
    def utiliseEnergie(self, energie):
        self.quantiteEnergie -= energie * self.nombrePersonnes
    
    def envoieEnergie(self):
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
