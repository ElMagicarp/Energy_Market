# ----------------- #
# ** Les Maisons ** #
# ----------------- #

# Importation des modules

import socket
import random
from .market import Market, weatherFactor, NOMBRE_MAISON

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
    def __init__(self, quantiteEnergie, haveSolarPanel, haveWindTurbine):
        self.quantiteEnergie = quantiteEnergie
        self.haveSolarPanel = haveSolarPanel
        self.haveWindTurbine = haveWindTurbine
        self.nombrePersonnes =  random.choice([1,2,2,3,3,3,4,4,4,5,5,6])
        self.listeVoisins = listeMaison(NOMBRE_MAISON)
        self.listBesoinJour = [( -4/30 * weatherFactor[0] + 7 ) * self.nombrePersonnes]
        
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
        self.quantiteEnergie += energie
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
            
            
    def run(self):
    # TODO : ajouter un système de payement ?
        '''Fonction Principal pour faire les opérations sur une maison'''
        self.quantiteEnergie -=  self.besionEnergie()
        if self.quantiteEnergie < 0 :
            "Vérifie si les voisins on des surplus d'énergie"
            for voisin in self.listeVoisins:
                if voisin.quantiteEnergie > 0:
                    if self.quantiteEnergie + voisin.quantiteEnergie >0:
                        voisin.quantiteEnergie -= self.quantiteEnergie
                        self.quantiteEnergie = 0
                        break
                    else:
                        self.quantiteEnergie += voisin.quantiteEnergie
                        voisin.quantiteEnergie = 0
            "Si les voisins n'ont pas assez d'energie, la maison achète de l'énerge au Market"
            if self.quantiteEnergie < 0:
                # TODO : achter au market l'énregie manquante quotidienne  
                self.quantiteEnergie = 0 
            
                
                    

#-----------------------------------------------
# Création de la liste des maisons de notre système

def listeMaison(nombreMaison):
    '''génère la liste des maisons'''
    return [Maison(0,random.choice([True,False]),random.choice([True,False])) for i in range(nombreMaison)]
