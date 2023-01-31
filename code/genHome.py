# ----------------- #
# ** Les Maisons ** #
# ----------------- #

#_importation_modules_--------------------------------------------------------------

import csv
import random
import sys 
import sysv_ipc
import os
import signal
from multiprocessing import Process , Semaphore

from home import Maison, runHome

#-----------------------------------------------------------------------------------
# Création de la liste des maisons de notre système

def runGenHome(HOST,PORT,nombreMaison,weatherSharedMemory,key,semGet,nombreJour):
    #_creer_messageQueue_-----------------------------------------------------------
    try:
        mq = sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREX)
    except:
        print("Message queue", key, "already exsits, terminating.")
        sys.exit(1)

    #_creer_listeMaison_------------------------------------------------------------
    listeMaisons = [Maison(0,random.choice([True,False]),
                    random.choice([True,False]),
                    random.choices([True, False], weights=[0.1, 0.9])[0],
                    weatherSharedMemory=weatherSharedMemory,
                    key = key, id = i, nombreJour=nombreJour) for i in range(nombreMaison)]
    
    #_creer_data.csv_---------------------------------------------------------------
    header = ['id', 'haveSolarPanel', 'haveWindTurbine', 'havePikachu', 'nombrePersonnes']
    with open('data.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for maison in listeMaisons:
            writer.writerow([maison.id, maison.haveSolarPanel, maison.haveWindTurbine,
                            maison.havePikachu, maison.nombrePersonnes])

    #_attribut_listeMaisons_à_chaque_maison_----------------------------------------
    for maison in listeMaisons:
        semHome = Semaphore(0)
        maison.listeVoisins=listeMaisons
        home = Process(target=runHome, args=(HOST,PORT,maison,))
        home.start()

    semGet.release()

    print("Ending process genhome\n")
    os.kill(os.getpid(), signal.SIGKILL) 
    
if "__main__" == __name__:
    runGenHome(0,0,5,[0,0,0,0],666)