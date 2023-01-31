# -------------------------- #
# ** STATISTICS INTERFACE ** #
# -------------------------- #

# -------------------------------------
# Importation des modules locales

from home import Maison
from weather import Weather

# Importation des packages

from rich.console import Console
from rich.table import Table
from rich import box

import matplotlib.pyplot as plt
from math import *
import random

# -------------------------------------
# Affichage des Statistiques Weather

# Définition des lambda
temp = lambda t : -sin(2*pi*t/365-250)*15 + 14.5 + random.random()*5*random.randint(-1,1)
ens = lambda t : 2001.9/ 8760 - 0.1*sin(2*pi*t/365-250) + random.random()*0.075*random.randint(-1,1)
vent = lambda t : 5 + 2*sin(2*pi*t/365-250) + random.random()*3*random.randint(-1,1)

# Création des listes
X = [k for k in range(365)]
Ytemp = [temp(t) for t in X]
Yens = [ens(t) for t in X]
Yvent = [vent(t) for t in X]

# Affichages des graphiques
plt.plot(X, Ytemp)
plt.plot(X, Yens)
plt.plot(X, Yvent)

plt.subplot(221)
plt.plot(X, Ytemp,color='red')
plt.xlabel('Jour')
plt.ylabel("°C")
plt.title("Température en fonction du jour de l'année (en °C)")
plt.legend()

plt.subplot(222)
plt.plot(X, Yens,color='green')
plt.xlabel('Jour')
plt.ylabel('Taux')
plt.title("Taux d'ensoleillement en fonction du jour de l'année")
plt.legend()

plt.subplot(223)
plt.plot(X, Yvent,color='darkblue')
plt.xlabel('Jour')
plt.ylabel('indice')
plt.title("Indice de vent en fonction du jour de l'année")
plt.legend()

plt.tight_layout()
# plt.show()

# -------------------------------------
# Utilisation d'une interface terminal avec "rich"

# Afficher un tableau avec les statistiques des maisons

"Création tableau"
tableMaison = Table(title="[red]Les Maisons")

"Création des colonnes"
tableMaison.add_column("ID", justify="center", style="cyan")
tableMaison.add_column("Cout Energie", justify="center", style="magenta")
tableMaison.add_column("Quantité Energie", justify="center", style="#45dc81")
tableMaison.add_column("Panneaux Solaires", justify="center", style="red")
tableMaison.add_column("Eolienne", justify="center", style="#0b2b8a")
tableMaison.add_column("Pikachu", justify="center", style="yellow")
tableMaison.add_column("Nombre Personnes", justify="center", style="#eeeeee")


"Création des lignes"

tableMaison.add_row("1", "2", "3", "4", "5", "6", "7")


"Affichage du tableau"
console = Console()
console.print(tableMaison)
