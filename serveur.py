import socket
import threading

from classes_serveur import Serveur, ClientThread

host, port = 'localhost', 1111


serveur = Serveur(host, port)
