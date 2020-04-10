from tkinter import Tk, Frame, Button, Entry, Text, Listbox, Scrollbar
from tkinter import RIGHT, LEFT, BOTH, TOP, BOTTOM, END, DISABLED, NORMAL

from threading import Thread, Event

from socket import socket
from socket import AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR

from pickle import loads

from classe_utilisateur import Utilisateur


class Texte_input(Frame):
    largeur_bouton = 5
    largeur_input = 30
    indication_pseudo = 'Entrez votre pseudo: '
    indication_message = 'Message: '

    def __init__(self, parent, mere):
        Frame.__init__(self, parent)
        self.mere = mere

        self.Texte = ""
        self.indication = Texte_input.indication_pseudo

        self.Bouton = Button(self, text='Envoyer', command = self.envoyer, width = Texte_input.largeur_bouton)
        self.Entree = Entry(self, textvariable=self.Texte, width=Texte_input.largeur_input)

        self.afficher_indications()

        self.Entree.focus()

        self.Bouton.pack(side=RIGHT, fill=BOTH)
        self.Entree.pack(side=LEFT, fill=BOTH)

        self.Entree.bind("<Return>", self.envoyer)
        self.Entree.bind("<Key>", self.effacer_indications)

        self.pack(side=BOTTOM, fill=BOTH)
    
    def effacer_indications(self, key=None):
        self.Entree.config(bg='lightgrey')
        if self.Entree.get() == self.indication:
            self.Entree.delete(0, END)

    def afficher_indications(self):
        self.Entree.insert(0, self.indication)
        self.Entree.config(bg='darkgrey')

    def envoyer(self, key=None):
        contenu = self.Entree.get()

        if contenu == 'deconnexion()': self.mere.deconnexion()
        elif contenu != "":
            if self.indication == Texte_input.indication_pseudo:
               self.indication = Texte_input.indication_message 

               self.mere.pseudo = contenu
               self.mere.FListe.maj_liste(self.mere.pseudo)
               self.mere.envoyer_pseudo()
            else:
                self.mere.Foutput.afficher('Vous: ' + contenu)
                self.mere.envoyer_message(contenu)
        
        self.Entree.delete(0, END)   
        self.afficher_indications()

class Texte_output(Frame):
    largeur_contenu = Texte_input.largeur_bouton + Texte_input.largeur_input
    hauteur_contenu = 12

    def __init__(self, parent):
        Frame.__init__(self, parent)

        self.contenu =  ""
        self.Affichage = Text(self, height = Texte_output.hauteur_contenu, width = Texte_output.largeur_contenu, state=DISABLED)
        self.Scroll = Scrollbar(self, command=self.Affichage.yview)

        self.Affichage['yscrollcommand'] = self.Scroll.set

        self.Affichage.pack(side=LEFT, expand=1, fill=BOTH)
        self.Scroll.pack(side=RIGHT, fill=BOTH)

        self.pack(side=TOP, fill=BOTH)
    
    def afficher(self, texte):
        self.Affichage.config(state=NORMAL)

        nouv_contenu = texte + '\n'
        self.contenu += nouv_contenu
 
        self.Affichage.delete('1.0', END)
        self.Affichage.insert(END, self.contenu)

        self.Affichage.see(END)
        self.Affichage.config(state=DISABLED)

class Liste(Frame):

    def __init__(self, parent, utilisateurs):
        Frame.__init__(self, parent)
        self.parent = parent

        self.Liste_users = utilisateurs

        self.Liste = Listbox(self.parent, relief='sunken', bg='lightgrey')

        self.afficher_liste()
        
        self.Liste.pack(expand=1,fill=BOTH)
        self.pack(side=RIGHT, fill=BOTH, expand=1)

    def afficher_liste(self):
        self.Liste.delete(0, END)

        for user in self.Liste_users:
            self.Liste.insert('end', user.pseudo)
            self.Liste.itemconfig('end', foreground=user.couleur)

    def maj_liste(self, user, commande='ajouter'):
        if commande == 'ajouter':   
            self.Liste_users.append(Utilisateur(user))
            self.Liste_users.sort(key=lambda x:x.pseudo)
        elif commande == 'enlever':
            try:
                for k in self.Liste_users:
                    if user == k.pseudo:
                        self.Liste_users.remove(k)
                        break
            except KeyError:
                print("L'utilisateur {} n'est pas dans la liste.".format(user))

        self.afficher_liste()


class Mere(Frame):
    entete_message = 'MESSA'
    entete_deconnexion = 'DECON'
    entete_liste = 'LISTE'
    len_entete = len(entete_deconnexion)

    def __init__(self, parent, serveur):
        Frame.__init__(self, parent)

        self.pseudo = ""

        self.parent = parent

        self.serveur = serveur

        self.Frame_Texte = Frame(self, relief='raised')
        self.Finput = Texte_input(self.Frame_Texte, self)
        self.Foutput = Texte_output(self.Frame_Texte)
        self.Frame_Texte.pack(side=LEFT, fill=BOTH)

        self.FListe = Liste(self, [])

        self.ecoute_thread = Ecoute(self, self.serveur)
        self.ecoute_thread.start()

        self.bind("<Destroy>", self.deconnexion)

        self.pack()
        
    def deconnexion(self, key=None):
        self.envoyer_deconnexion()
        self.parent.destroy()

    def envoyer_message(self, contenu):
        contenu = Mere.entete_message + self.pseudo + '|' + contenu
        self.serveur.send(contenu.encode())
    def envoyer_pseudo(self):
        contenu = self.pseudo
        self.serveur.send(contenu.encode())
    def envoyer_deconnexion(self):
        contenu = Mere.entete_deconnexion + self.pseudo
        self.serveur.send(contenu.encode())

class Ecoute(Thread):

    def __init__(self, mere, serveur):
        Thread.__init__(self)

        self.serveur = serveur
        self.mere = mere


    def run(self):
        
        liste_users = loads(self.serveur.recv(8192))
        for user in liste_users:
            self.mere.FListe.maj_liste(user)

        while True:
            r = self.serveur.recv(2048).decode()
            r_entete = r[:Mere.len_entete]
            r = r[Mere.len_entete:]
            
            if r_entete == Mere.entete_deconnexion:
                self.mere.FListe.maj_liste(r, 'enlever')
                self.mere.Foutput.afficher(r + " s'est déconnecté.")

            elif r_entete == Mere.entete_liste:
                self.mere.FListe.maj_liste(r)
                self.mere.Foutput.afficher(r + " s'est connecté.")
            elif r != '':
                indice = 0
                for k in range(len(r)):
                    if r[k] == '|': 
                        indice = k
                        break
                
                pseudo = r[:indice]
                message = r[indice+1:]

                self.mere.Foutput.afficher(pseudo + ': ' + message)
            else:
                self.mere.Foutput.afficher("Le serveur a rencontré un problème.")
                return None

        
