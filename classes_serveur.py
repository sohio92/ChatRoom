from threading import Thread, Event

from socket import socket
from socket import AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR

from pickle import dumps

class Serveur(socket):
    entete_message = 'MESSA'
    entete_deconnexion = 'DECON'
    entete_liste = 'LISTE'
    len_entete = len(entete_deconnexion)

    def __init__(self, host, port):
        socket.__init__(self, AF_INET, SOCK_STREAM)

        self.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.bind((host, port))

        self.Clients = {}

        self.run()

    def run(self):
        while True:
            self.listen(10)
            print( "En écoute...")
            (clientsocket, (ip, port)) = self.accept()

            nouveau_client = ClientThread(ip, port, self, clientsocket)
            nouveau_client.start()

class ClientThread(Thread):

    def __init__(self, ip, port, serveur, clientsocket):
        Thread.__init__(self)

        self.ip = ip
        self.port = port
        self.serveur = serveur

        self.clientsocket = clientsocket
        print("[+] Nouveau thread pour {} {}".format(self.ip, self.port))

    def run(self):
        self.pseudo = self.clientsocket.recv(2048).decode()

        data = dumps(list(self.serveur.Clients.keys()))
        self.clientsocket.send(data)

        self.serveur.Clients[self.pseudo] = self

        self.transmettre((Serveur.entete_liste + self.pseudo).encode())

        print("Connexion de {} avec IP:{} sur PORT:{}".format(self.pseudo, self.ip, self.port))
        while True:
            try:
                r = self.clientsocket.recv(2048)
            except OSError:
                self.serveur.Clients.pop(self.pseudo, None)
                self.clientsocket.close()
                return None

            if r != b'':
                self.transmettre(r)
                print(r)


            if r.decode()[:Serveur.len_entete] == Serveur.entete_deconnexion:
                self.deconnexion()
                
    def deconnexion(self):
        self.serveur.Clients.pop(self.pseudo, None)
        self.clientsocket.close()     
    
    def transmettre(self, message):
        for client in self.serveur.Clients.values():
            if self != client:
                client.clientsocket.send(message)


