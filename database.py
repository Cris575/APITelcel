from pymongo import MongoClient

class ConexionMongoDB:
    def __init__(self):
        self.cliente = MongoClient()
        self.bd = self.cliente.TelcelAPI
        self.coleccion = self.bd.citas
        self.reparacion = self.bd.reparaciones
        self.refacciones = self.bd.refacciones
        self.usuarios = self.bd.usuarios
        self.dispositivos = self.bd.dispositivos 
    def cerrar(self):
        self.cliente.close()

        