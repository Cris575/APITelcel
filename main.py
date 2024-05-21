from fastapi import FastAPI
from models import NuevaCita, ConfirmacionCita
from database import ConexionMongoDB
from bson import json_util
import json
from fastapi import HTTPException, status
from datetime import datetime, timedelta



app = FastAPI()

# Instancia de la conexión a MongoDB
conexion_mongo = ConexionMongoDB()

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/citas")
async def crear_cita(cita: NuevaCita):
    # Obtener el nombre del usuario cliente
    usuario_cliente = conexion_mongo.usuarios.find_one({"idUsuario": cita.idUsuarioC})
    if not usuario_cliente:
        raise HTTPException(status_code=404, detail="Usuario cliente no encontrado")

    # Generar la fecha de registro actual
    fecha_registro = datetime.now().strftime("%d/%m/%Y")

    # Generar la fecha de entrega tres días después de la fecha de registro
    fecha_entrega = (datetime.now() + timedelta(days=3)).strftime("%d/%m/%Y")

    # Guardar la cita en MongoDB
    cita_dict = cita.dict()
    dispositivos_dict = [disp.dict() for disp in cita.dispositivos]
    cita_dispositivos = {
        "idCita": cita_dict["id"],
        "fechaRegistro": fecha_registro,
        "fechaEntrega": fecha_entrega,
        "motivoCita": cita_dict["motivoCita"],
        "horaCita": cita_dict["horaCita"],
        "estatusCita": cita_dict["estatusCita"],
        "idUsuarioC": cita_dict["idUsuarioC"],
        "idUsuarioT": cita_dict["idUsuarioT"],
        "dispositivos": dispositivos_dict,
    }
    cita_id = conexion_mongo.coleccion.insert_one(cita_dispositivos).inserted_id

    # Devolver un mensaje de confirmación y el nombre del usuario
    return {"mensaje": "Cita creada exitosamente", "nombreUsuario": usuario_cliente["nombre"]}

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

@app.put("/citas/{idCita}/finalizar")
async def finalizar_cita(idCita: int):
    # Verificar si la cita existe en la base de datos
    cita = conexion_mongo.coleccion.find_one({"idCita": idCita})
    if not cita:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="La cita no existe")

    # Verificar si la cita ya está cancelada
    if cita.get("estatusCita") == "Cancelada":
        return {"mensaje": f"La cita con ID {idCita} fue cancelada."}
    
    if cita.get("estatusCita") == "Atendida":
        return {"mensaje": f"La cita con ID {idCita} fue atendida."}

    # Actualizar el estado de la cita a "Cancelada"
    conexion_mongo.coleccion.update_one({"idCita": idCita}, {"$set": {"estatusCita": "Atendida"}})

    # Devolver una respuesta exitosa
    return {"mensaje": f"Cita con ID {idCita} fue atendida exitosamente."}

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