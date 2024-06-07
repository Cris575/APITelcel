from fastapi import FastAPI
from models import NuevaCita, ConfirmacionCita, Usuario, DatosActualizados, CredencialesUsuario, Reparacion, NuevaRefaccion, ActualizarRefaccion
from database import ConexionMongoDB
from bson import json_util, ObjectId
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

@app.post("/usuarios")
async def crear_usuario(usuario: Usuario):
    # Verificar si el usuario ya existe
    if conexion_mongo.usuarios.find_one({"idUsuario": usuario.idUsuario}):
        raise HTTPException(status_code=400, detail="El usuario ya existe")

    # Generar la fecha de registro actual
    fecha_registro = datetime.now().strftime("%d/%m/%Y")

    # Convertir el usuario a un diccionario y agregar la fecha de registro
    usuario_dict = usuario.dict()
    usuario_dict["fechaRegistro"] = fecha_registro

    # Insertar el usuario en la base de datos
    usuario_id = conexion_mongo.usuarios.insert_one(usuario_dict).inserted_id

    # Devolver una respuesta exitosa con el ID del nuevo usuario
    return {"mensaje": "Usuario creado y guardado en MongoDB con éxito", "usuario_id": str(usuario_id)}

@app.get("/usuarios")
async def obtener_usuarios():
    # Recuperar todos los usuarios de la base de datos
    usuarios = list(conexion_mongo.usuarios.find({}, {
        "_id": 0,
        "idUsuario": 1,
        "nombre": 1,
        "apellidos": 1,
        "telefono": 1,
        "email": 1,
        "password": 1,
        "rolUsuario": 1
    }))

    # Construir la respuesta en el formato especificado
    usuarios_formateados = [
        {
            "idUsuario": usuario["idUsuario"],
            "nombre": usuario["nombre"],
            "apellidos": usuario["apellidos"],
            "telefono": usuario["telefono"],
            "correoElectronico": usuario["email"],
            "contraseña": usuario["password"],
            "rol": usuario["rolUsuario"]
        }
        for usuario in usuarios
    ]

    respuesta = {"usuarios": usuarios_formateados}

    return respuesta

@app.get("/usuarios/{idUsuario}")
async def obtener_usuario_por_id(idUsuario: int):
    # Buscar el usuario por idUsuario en la base de datos
    usuario = conexion_mongo.usuarios.find_one({"idUsuario": idUsuario}, {
        "_id": 0,
        "idUsuario": 1,
        "nombre": 1,
        "apellidos": 1,
        "telefono": 1,
        "email": 1,
        "password": 1,
        "rolUsuario": 1
    })

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Construir la respuesta en el formato especificado
    respuesta = {
        "idUsuario": usuario["idUsuario"],
        "nombre": usuario["nombre"],
        "apellidos": usuario["apellidos"],
        "telefono": usuario["telefono"],
        "correoElectronico": usuario["email"],
        "contraseña": usuario["password"],
        "rol": usuario["rolUsuario"]
    }

    return respuesta

@app.put("/usuarios/{idUsuario}")
async def actualizar_perfil_usuario(idUsuario: int, datos_actualizados: DatosActualizados):
    # Verificar si el usuario existe en la base de datos
    usuario_existente = conexion_mongo.usuarios.find_one({"idUsuario": idUsuario})
    if not usuario_existente:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Actualizar los detalles del perfil del usuario
    cambios_realizados = False
    for campo, valor in datos_actualizados.dict().items():
        if campo in usuario_existente and usuario_existente[campo] != valor:
            conexion_mongo.usuarios.update_one(
                {"idUsuario": idUsuario},
                {"$set": {campo: valor}}
            )
            cambios_realizados = True

    if cambios_realizados:
        return {"estatus": True, "mensaje": "Perfil de usuario actualizado correctamente."}
    else:
        return {"estatus": False, "mensaje": "No se realizaron cambios en el perfil del usuario."}

@app.post("/usuarios/validar")
async def validar_credenciales(credenciales: CredencialesUsuario):
    # Buscar el usuario por nombreUsuario en la base de datos
    usuario = conexion_mongo.usuarios.find_one({"email": credenciales.email})
    
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Verificar la contraseña
    if usuario["password"] != credenciales.contraseña:
        raise HTTPException(status_code=400, detail="Credenciales incorrectas")
    
    # Si las credenciales son válidas, devolver un mensaje de éxito
    return {"estatus": True, "mensaje": "Credenciales validadas correctamente"}

@app.post("/reparaciones")
async def agregar_reparacion(reparacion: Reparacion):
    # Generar un idReparacion único y autoincremental
    ultimo_reparacion = conexion_mongo.reparacion.find_one(
        sort=[("idReparacion", -1)]
    )
    nuevo_id_reparacion = 1 if ultimo_reparacion is None else ultimo_reparacion["idReparacion"] + 1

    # Convertir la reparación a un diccionario
    reparacion_dict = reparacion.dict()
    reparacion_dict["idReparacion"] = nuevo_id_reparacion

    # Convertir fechas a string para que sean compatibles con BSON
    if "fechaInicio" in reparacion_dict:
        reparacion_dict["fechaInicio"] = reparacion_dict["fechaInicio"].strftime("%Y-%m-%d")
    if "fechaFin" in reparacion_dict:
        reparacion_dict["fechaFin"] = reparacion_dict["fechaFin"].strftime("%Y-%m-%d")

    # Verificar si la cita existe en la base de datos
    cita = conexion_mongo.coleccion.find_one({"idCita": reparacion_dict["idCita"]})
    if not cita:
        raise HTTPException(status_code=404, detail="Cita no encontrada")

    # Guardar la reparación en la base de datos
    conexion_mongo.reparacion.insert_one(reparacion_dict)

    # Devolver una respuesta exitosa
    return {"estatus": True, "mensaje": "Reparación agregada exitosamente"}

@app.get("/reparaciones")
async def consultar_reparaciones():
    # Consulta para recuperar las reparaciones
    reparaciones_cursor = conexion_mongo.reparacion.find(
        {"refacciones": {"$exists": True}},
        {
            "_id": 0,
            "tipoReparacion": 1,
            "detalles": 1,
            "estatus": 1,
            "costoServicio": 1,
            "total": 1,
            "idCita": 1,
            "idUsuarioC": 1,
            "idUsuarioT": 1,
            "idDispositivo": 1,
            "refacciones.idReparacion": 1,
            "refacciones.idRefaccion": 1,
            "refacciones.nombreRefaccion": 1,
            "refacciones.precio": 1,
            "refacciones.cantidad": 1,
            "refacciones.descripcion": 1,
            "refacciones.estatus": 1
        }
    )

    # Convertir el cursor en una lista de reparaciones
    reparaciones = list(reparaciones_cursor)

    # Verificar si hay reparaciones
    if not reparaciones:
        return {"reparaciones": []}

    return {"reparaciones": reparaciones}

@app.get("/reparaciones/{idReparacion}")
async def consultar_reparacion_por_id(idReparacion: int):
    # Consulta para recuperar la reparación por su ID
    reparacion = conexion_mongo.reparacion.find_one({"idReparacion": idReparacion})

    # Verificar si la reparación existe
    if not reparacion:
        return {"mensaje": "Reparación no encontrada"}

    # Convertir el ObjectId a str para que sea JSON serializable
    reparacion["_id"] = str(reparacion["_id"])

    # Devolver los datos de la reparación en un diccionario
    return reparacion

@app.put("/reparaciones/{idReparacion}")
async def actualizar_reparacion(idReparacion: int, reparacion_data: dict):
    # Verificar si la reparación existe en la base de datos
    existing_reparacion = conexion_mongo.reparacion.find_one({"idReparacion": idReparacion})
    if existing_reparacion is None:
        raise HTTPException(status_code=404, detail="Reparación no encontrada")

    # Crear un diccionario de actualización con los datos proporcionados en el cuerpo
    update_data = {key: value for key, value in reparacion_data.items() if value is not None}

    # Actualizar la reparación en la base de datos con los nuevos datos
    conexion_mongo.reparacion.update_one({"idReparacion": idReparacion}, {"$set": update_data})

    return {"mensaje": "Reparación actualizada exitosamente"}


@app.post("/refacciones")
async def agregar_refaccion(refaccion: NuevaRefaccion):
    # Verificar si la reparación existe en la base de datos
    reparacion = conexion_mongo.reparacion.find_one({"idReparacion": refaccion.idReparacion})
    if not reparacion:
        raise HTTPException(status_code=404, detail="La reparación no existe")

    # Verificar si la refacción ya existe en el arreglo 'refacciones' de la reparación
    refacciones_existentes = reparacion.get("refacciones", [])
    for ref in refacciones_existentes:
        if ref["idRefaccion"] == refaccion.idRefaccion:
            raise HTTPException(status_code=400, detail="La refacción ya existe en la reparación")

    # Agregar la nueva refacción al arreglo 'refacciones' del documento de reparación
    conexion_mongo.reparacion.update_one(
        {"idReparacion": refaccion.idReparacion},
        {"$push": {"refacciones": refaccion.dict()}}
    )

    return {"estatus": True, "mensaje": "Refacción agregada exitosamente"}

@app.get("/refacciones")
async def consultar_refacciones():
    # Consultar todas las reparaciones en la base de datos
    reparaciones = list(conexion_mongo.reparacion.find({}, {"_id": 0}))

    # Extraer las refacciones de cada reparación y agregarlas a una lista independiente
    refacciones = []
    for reparacion in reparaciones:
        refacciones.extend(reparacion.get("refacciones", []))

    return {"refacciones": refacciones}

@app.get("/refacciones/{idReparacion}/{idRefaccion}")
async def consultar_refaccion_por_id(idReparacion: int, idRefaccion: int):
    # Consultar la reparación por su ID
    reparacion = conexion_mongo.reparacion.find_one({"idReparacion": idReparacion}, {"_id": 0, "refacciones": 1})

    # Verificar si la reparación existe
    if not reparacion:
        return {"mensaje": "Reparación no encontrada"}

    # Obtener las refacciones de la reparación
    refacciones = reparacion.get("refacciones", [])

    # Buscar la refacción por su idRefaccion
    refaccion_encontrada = next((refaccion for refaccion in refacciones if refaccion.get("idRefaccion") == idRefaccion), None)

    if not refaccion_encontrada:
        return {"mensaje": "Refacción no encontrada"}

    return {"refaccion": refaccion_encontrada}

@app.put("/refacciones/{idReparacion}/{idRefaccion}")
async def actualizar_refaccion(idReparacion: int, idRefaccion: int, refaccion_actualizada: ActualizarRefaccion):
    # Consultar la reparación que contiene la refacción
    reparacion = conexion_mongo.reparacion.find_one({"idReparacion": idReparacion, "refacciones.idRefaccion": idRefaccion})

    # Verificar si la reparación existe
    if not reparacion:
        raise HTTPException(status_code=404, detail="La reparación que contiene la refacción no fue encontrada")

    # Buscar la refacción por su idRefaccion dentro de la lista de refacciones de la reparación
    refaccion_index = next((index for index, refaccion in enumerate(reparacion["refacciones"]) if refaccion["idRefaccion"] == idRefaccion), None)

    if refaccion_index is None:
        raise HTTPException(status_code=404, detail="La refacción no fue encontrada en la reparación")

    # Actualizar los datos de la refacción
    conexion_mongo.reparacion.update_one(
        {"idReparacion": idReparacion, "refacciones.idRefaccion": idRefaccion},
        {"$set": {
            f"refacciones.{refaccion_index}.nombreRefaccion": refaccion_actualizada.nombre,
            f"refacciones.{refaccion_index}.cantidad": refaccion_actualizada.cantidad,
            f"refacciones.{refaccion_index}.precio": refaccion_actualizada.precioUnitario
        }}
    )

    return {"estatus": True, "mensaje": "Detalles de refacción actualizados correctamente"}



if __name__ == '__main__':
    app.run(debug=True)