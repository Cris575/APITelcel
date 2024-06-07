from pymongo import MongoClient

class ConexionMongoDB:
    def __init__(self):
        self.cliente = MongoClient()
        self.bd = self.cliente.TelcelAPI
        self.coleccion = self.bd.citas
        self.reparacion = self.bd.reparacion
        self.usuarios = self.bd.usuarios
    def cerrar(self):
        self.cliente.close()

        