from fastapi import FastAPI
from models import NuevaCita, ConfirmacionCita
from database import ConexionMongoDB
from bson import json_util
import json
from fastapi import HTTPException, status



app = FastAPI()

# Instancia de la conexión a MongoDB
conexion_mongo = ConexionMongoDB()

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/citas")
async def crear_cita(cita: NuevaCita):
    # Convertir la cita y los dispositivos a diccionarios
    cita_dict = cita.dict()
    dispositivos_dict = [disp.dict() for disp in cita.dispositivos]

    # Construir el objeto para la estructura deseada
    cita_dispositivos = {
        "idCita": cita_dict["id"],
        "fechaRegistro": cita_dict["fechaRegistro"],
        "fechaEntrega": cita_dict["fechaEntrega"],
        "motivoCita": cita_dict["motivoCita"],
        "horaCita": cita_dict["horaCita"],
        "estatusCita": cita.estatusCita,  # Utilizar el valor predeterminado
        "idUsuarioC": cita_dict["idUsuarioC"],
        "idUsuarioT": cita_dict["idUsuarioT"],
        "dispositivos": dispositivos_dict
    }

    # Guardar la cita y la información del dispositivo en MongoDB
    cita_id = conexion_mongo.coleccion.insert_one(cita_dispositivos).inserted_id

    # Devolver una respuesta exitosa con el ID de la nueva cita
    return {"mensaje": "Cita creada y guardada en MongoDB con éxito", "cita_id": str(cita_id)}

@app.get("/citas")
async def obtener_citas():
    # Obtener todas las citas de la colección en MongoDB
    citas = list(conexion_mongo.coleccion.find({}))

    # Convertir ObjectId a cadenas y formatear los datos como se requiere
    citas_formateadas = []
    for cita in citas:
        cita["_id"] = str(cita["_id"])
        citas_formateadas.append(cita)

    # Devolver las citas como respuesta
    return {"citas": citas_formateadas}

@app.put("/citas/{idCita}/confirmar")
async def confirmar_cita(idCita: int):
    # Verificar si la cita existe en la base de datos
    cita = conexion_mongo.coleccion.find_one({"idCita": idCita})
    if not cita:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="La cita no existe")

    # Verificar si la cita ya está confirmada
    if cita.get("estatusCita") == "Confirmada":
        return {"mensaje": f"La cita con ID {idCita} ya está confirmada."}

    # Actualizar el estado de la cita a "Confirmada"
    conexion_mongo.coleccion.update_one({"idCita": idCita}, {"$set": {"estatusCita": "Confirmada"}})

    # Devolver una respuesta exitosa
    return {"mensaje": f"Cita con ID {idCita} confirmada exitosamente."}

@app.put("/citas/{idCita}/cancelar")
async def cancelar_cita(idCita: int):
    # Verificar si la cita existe en la base de datos
    cita = conexion_mongo.coleccion.find_one({"idCita": idCita})
    if not cita:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="La cita no existe")

    # Verificar si la cita ya está cancelada
    if cita.get("estatusCita") == "Cancelada":
        return {"mensaje": f"La cita con ID {idCita} ya está cancelada."}

    # Actualizar el estado de la cita a "Cancelada"
    conexion_mongo.coleccion.update_one({"idCita": idCita}, {"$set": {"estatusCita": "Cancelada"}})

    # Devolver una respuesta exitosa
    return {"mensaje": f"Cita con ID {idCita} cancelada exitosamente."}

@app.get("/citas/{idCita}")
async def obtener_cita(idCita: int):
    # Buscar la cita en la base de datos
    cita = conexion_mongo.coleccion.find_one({"idCita": idCita})
    
    # Verificar si la cita existe
    if not cita:
        raise HTTPException(status_code=404, detail="Cita no encontrada")

    # Convertir el _id de ObjectId a string
    cita["_id"] = str(cita["_id"])

    # Devolver los detalles completos de la cita
    return cita

if __name__ == '__main__':
    app.run(debug=True)