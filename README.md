# Energy_Market

PPC project 2022-2023


#_Exécution#_

Pour modifier le nombre de maisons et le nombre de jours de la simulation, modifiez dans le codes les paramétres affiliés dans le script market.py aux lignes 280 et 281.

Pour exécuter la simulation, il faut exécuter le script market.py.

Pour afficher les graphiques et les configurations des maisons aprés la simulation, il faut exécuter le script stats.py.


#_libraries externes  utilisées#_

sysv_ipc, csv,  rich, matplotlib.pyplot

---

#_ATTENTION#_

Après chaque exécution de la simulation, il faut clear la message queue à l'aide de la commande "ipcrm -Q `<key>`"

Lors de l'exécution de la simulation avec un grand nombre de maisons, il se peut que les sockets ne se ferment pas correctement et fassent crasher le programme avec une erreur 

'ADDRESS ALREADY USED', dans ces cas là il faut kill les processus encore vivant avant de relancer une simulation.
