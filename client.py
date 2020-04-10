
import socket
from tkinter import Tk

from custom_widgets import Mere


host, port = 'localhost', 1111
serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serveur.connect((host, port))

fenetre = Tk()
Affichage = Mere(fenetre, serveur)
fenetre.mainloop()