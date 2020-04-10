from random import choice

class Utilisateur:
    Couleurs = ['black', 'yellow', 'green', 'darkgreen', 'blue',\
         'darkblue', 'red', 'darkred', 'pink', 'orange', 'brown']

    def __init__(self, nom):
        self.pseudo = nom
        self.couleur = choice(Utilisateur.Couleurs)

