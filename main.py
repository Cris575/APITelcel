from typing import Union
from fastapi import FastAPI, HTTPException, UploadFile, File
from datetime import datetime
from models import GenerarCita
from database import ConexionMongoDB
from typing import Optional
from bson import ObjectId


app = FastAPI()

conexion = ConexionMongoDB()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/citas/{item_id}", response_model=dict, name="Obtener Cita por ID")
def read_item(item_id: int):
    cita = conexion.coleccion.find_one({"_id": item_id})
    if cita:
        return cita
    else:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    
@app.post("/citas")
async def registrar_cita(cita: GenerarCita):
    # Verificar si el usuario está registrado por su nombre
    usuario = conexion.bd.usuarios.find_one({"nombre": cita.nombreCliente})
    if usuario is None:
        raise HTTPException(status_code=404, detail="El usuario no está registrado")
    
    # Obtener el ID del usuario y su nombre
    id_usuario = usuario["_id"]
    nombre_cliente = usuario["nombre"]

    # Generar automáticamente el ID de la cita
    ultima_cita = conexion.coleccion.find_one(sort=[("_id", -1)])
    nuevo_id_cita = 1 if ultima_cita is None else ultima_cita["_id"] + 1

    # Agregar el campo estatus y el nombre del cliente
    cita.estatus = "pendiente"
    cita.nombreCliente = nombre_cliente

    # Guardar la cita en la base de datos con el ID del usuario y el nombre del cliente
    cita_data = cita.dict()
    cita_data["_id"] = nuevo_id_cita
    cita_data["idUsuario"] = id_usuario
    conexion.coleccion.insert_one(cita_data)

    # Devolver respuesta con estatus
    respuesta = {
        "estatus": "pendiente"
    }
    return respuesta


    
@app.get("/citas/", name="Obtener Todas las Citas")
def read_all_items():
    citas = list(conexion.coleccion.find())
    if citas:
        return citas
    else:
        raise HTTPException(status_code=404, detail="No se encontraron citas")
    

@app.put("/citas/{idCita}/confirmar", name="Confirmar Cita por ID")
def confirmar_cita(idCita: int):
    # Verificar si la cita ya ha sido confirmada
    cita = conexion.coleccion.find_one({"_id": idCita})
    if cita is None:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    elif cita["estatus"] == "confirmado":
        return {"estatus": False, "mensaje": "La cita ya ha sido confirmada anteriormente."}

    updated_cita = {
        "estatus": "confirmado"
    }

    result = conexion.coleccion.update_one({"_id": idCita}, {"$set": updated_cita})

    # Verificar si la cita se actualizó correctamente
    if result.modified_count == 1:
        return {"estatus": True, "mensaje": "La cita ha sido confirmada exitosamente."}
    else:
        raise HTTPException(status_code=500, detail="Error al confirmar la cita")
    

@app.delete("/citas/{idCita}", name="Borrar Cita por ID")
def borrar_cita(idCita: int):
    # Buscar la cita por su ID
    cita = conexion.coleccion.find_one({"_id": idCita})
    if cita is None:
        raise HTTPException(status_code=404, detail="Cita no encontrada")

    # Eliminar la cita de la base de datos
    result = conexion.coleccion.delete_one({"_id": idCita})

    # Verificar si la cita se eliminó correctamente
    if result.deleted_count == 1:
        return {"mensaje": "La cita ha sido eliminada exitosamente."}
    else:
        raise HTTPException(status_code=500, detail="Error al intentar eliminar la cita")
    
@app.get("/reparaciones/{idReparacion}", name="Obtener Detalles de Reparación por ID")
def obtener_detalles_reparacion(idReparacion: int):
    reparacion = conexion.reparacion.find_one({"_id": idReparacion})
    if reparacion is None:
        raise HTTPException(status_code=404, detail="Reparación no encontrada")

    detalles_reparacion = {
        "_id": reparacion["_id"],
        "idCita": reparacion["idCita"],
        "fechaInicio": reparacion["fechaInicio"],
        "fechaFin": reparacion["fechaFin"],
        "estado": reparacion["estado"],
        "descripcion": reparacion["descripcion"],
        "costo": reparacion["costo"],
        "refaccionesUtilizadas": reparacion["refaccionesUtilizadas"]
    }

    return detalles_reparacion

from fastapi import HTTPException

@app.put("/reparaciones/{idReparacion}/confirmar", name="Finalizar Reparación por ID")
def confirmar_reparacion(idReparacion: int):
   
    updated_estado = {
        "estado": "En proceso"
    }

    result = conexion.reparacion.update_one({"_id": idReparacion}, {"$set": updated_estado})

    # Verificar si la reparación se actualizó correctamente.
    if result.modified_count == 1:
        return {"estado": "Finalizado", "mensaje": "La reparación ha sido finalizada."}
    else:
        raise HTTPException(status_code=404, detail="Reparación no encontrada")
    

@app.put("/reparaciones/{idReparacion}", response_model=dict, name="Actualizar Datos de Reparación y Agregar Refacción por ID")
def actualizar_reparacion(idReparacion: int, descripcion: Optional[str] = None, costoTotal: Optional[float] = None, idRefaccion: Optional[int] = None, cantidad: Optional[int] = None):
    # Obtener los detalles de la reparación actual en la base de datos.
    reparacion_actual = conexion.reparacion.find_one({"_id": idReparacion})
    if reparacion_actual is None:
        raise HTTPException(status_code=404, detail="Reparación no encontrada")

    # Actualizar los detalles de la reparación solo si los nuevos valores son diferentes a los existentes.
    updated_data = {}
    if descripcion is not None and descripcion != reparacion_actual.get("descripcion"):
        updated_data["descripcion"] = descripcion
    if costoTotal is not None and costoTotal != reparacion_actual.get("costo"):
        updated_data["costo"] = costoTotal

    if updated_data:
        # Ejemplo de cómo se actualizarían los datos en la base de datos (reemplazar con tu lógica real).
        result_reparacion = conexion.reparacion.update_one({"_id": idReparacion}, {"$set": updated_data})

        # Verificar si la reparación se actualizó correctamente.
        if result_reparacion.modified_count != 1:
            raise HTTPException(status_code=500, detail="Error al actualizar la reparación")

    # Verificar si se proporcionó la información de la refacción y si la refacción existe en la colección de refacciones.
    if idRefaccion is not None and cantidad is not None:
        refaccion = conexion.refacciones.find_one({"_id": idRefaccion})
        if refaccion:
            # Actualizar el arreglo de refacciones de la reparación.
            result_refaccion = conexion.reparacion.update_one(
                {"_id": idReparacion},
                {"$addToSet": {"refaccionesUtilizadas": {"idRefaccion": idRefaccion, "cantidad": cantidad}}}
            )

            # Verificar si la refacción se agregó correctamente.
            if result_refaccion.modified_count != 1:
                raise HTTPException(status_code=500, detail="Error al agregar la refacción a la reparación")

    return {"mensaje": "Cambios realizados"}


@app.post("/usuarios/", name="Registrar Nuevo Usuario")
def create_user(idUsuario: int, nombre: str, apellidos: str, telefono: str, correoElectronico: str, contraseña: str, rol: str):
    # Verificar si el usuario ya existe
    if conexion.usuarios.find_one({"_id": idUsuario}):
        raise HTTPException(status_code=400, detail="El usuario con este ID ya existe")

    # Crear el documento del nuevo usuario con el _id especificado
    nuevo_usuario = {
        "_id": idUsuario,
        "nombre": nombre,
        "apellidos": apellidos,
        "telefono": telefono,
        "correoElectronico": correoElectronico,
        "contraseña": contraseña,
        "rol": rol
    }

    # Insertar el nuevo usuario en la colección de usuarios
    result = conexion.usuarios.insert_one(nuevo_usuario)

    # Verificar si la inserción fue exitosa
    if result.inserted_id:
        return {"estatus": True, "mensaje": "Usuario registrado exitosamente"}
    else:
        raise HTTPException(status_code=500, detail="Error al registrar usuario")
    
@app.put("/usuarios/{idUsuario}", name="Actualizar Detalles del Perfil de Usuario por ID")
def update_user_by_id(idUsuario: int, nombre: str = None, apellidos: str = None, telefono: str = None, correoElectronico: str = None, contraseña: str = None):
    # Comprobar si el usuario existe
    usuario_existente = conexion.usuarios.find_one({"_id": idUsuario})
    if not usuario_existente:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Construir el diccionario con los campos a actualizar
    updated_data = {}
    if nombre is not None:
        updated_data["nombre"] = nombre
    if apellidos is not None:
        updated_data["apellidos"] = apellidos
    if telefono is not None:
        updated_data["telefono"] = telefono
    if correoElectronico is not None:
        updated_data["correoElectronico"] = correoElectronico
    if contraseña is not None:
        updated_data["contraseña"] = contraseña

    # Actualizar el usuario en la base de datos
    result = conexion.usuarios.update_one({"_id": idUsuario}, {"$set": updated_data})

    # Comprobar si se actualizó correctamente
    if result.modified_count == 1:
        return {"estatus": True, "mensaje": "Detalles del perfil actualizados exitosamente"}
    else:
        raise HTTPException(status_code=500, detail="Error al actualizar los detalles del perfil de usuario")
    
@app.delete("/usuarios/{idUsuario}", name="Eliminar Perfil de Usuario por ID")
def delete_user_by_id(idUsuario: int):
    # Comprobar si el usuario existe
    usuario_existente = conexion.usuarios.find_one({"_id": idUsuario})
    if not usuario_existente:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Eliminar el usuario de la base de datos
    result = conexion.usuarios.delete_one({"_id": idUsuario})

    # Comprobar si se eliminó correctamente
    if result.deleted_count == 1:
        return {"estatus": True, "mensaje": "Perfil de usuario eliminado exitosamente"}
    else:
        raise HTTPException(status_code=500, detail="Error al eliminar el perfil de usuario")

@app.post("/usuarios/validar", name="Validar Credenciales de Usuario")
def validate_user_credentials(nombreUsuario: str, contraseña: str):
    # Buscar el usuario por nombre de usuario y contraseña en la base de datos
    usuario = conexion.usuarios.find_one({"nombre": nombreUsuario, "contraseña": contraseña})

    # Comprobar si se encontró el usuario
    if usuario:
        return {"estatus": True, "mensaje": "Credenciales de usuario válidas"}
    else:
        raise HTTPException(status_code=401, detail="Credenciales de usuario no válidas")
    
@app.post("/refacciones", name="Agregar Nueva Refacción al Inventario")
def add_new_spare_part(idRefaccion: int, nombre: str, cantidad: int, precioUnitario: float, descripcion: str):
    # Verificar si ya existe una refacción con el mismo ID
    existing_refaccion = conexion.refacciones.find_one({"idRefaccion": idRefaccion})
    if existing_refaccion:
        raise HTTPException(status_code=400, detail="Ya existe una refacción con este ID")

    # Crear un nuevo documento para la refacción
    nueva_refaccion = {
        "_id": idRefaccion,
        "nombre": nombre,
        "cantidad": cantidad,
        "precioUnitario": precioUnitario,
        "descripcion": descripcion
    }

    # Insertar la nueva refacción en la base de datos
    result = conexion.refacciones.insert_one(nueva_refaccion)

    # Verificar si la refacción se agregó correctamente
    if result.inserted_id:
        return {"estatus": True, "mensaje": "Nueva refacción agregada al inventario"}
    else:
        raise HTTPException(status_code=500, detail="Error al agregar la nueva refacción")
    
@app.get("/refacciones", name="Recuperar Todas las Refacciones")
def get_all_spare_parts():
    refacciones = list(conexion.refacciones.find({}, {"_id": 0}))  # Excluir el campo _id
    return {"refacciones": refacciones}


@app.put("/refacciones/{idRefaccion}", name="Actualizar Detalles de Refacción por ID")
def update_spare_part(idRefaccion: int, nombre: str = None, cantidad: int = None, precioUnitario: float = None):
    # Construir el diccionario de datos actualizados
    updated_data = {}
    if nombre is not None:
        updated_data["nombre"] = nombre
    if cantidad is not None:
        updated_data["cantidad"] = cantidad
    if precioUnitario is not None:
        updated_data["precioUnitario"] = precioUnitario

    # Verificar que al menos un campo sea proporcionado para actualizar
    if not updated_data:
        raise HTTPException(status_code=400, detail="No se proporcionaron datos para actualizar")

    # Actualizar la refacción en la base de datos
    result = conexion.refacciones.update_one({"_id": idRefaccion}, {"$set": updated_data})

    # Verificar si la refacción se actualizó correctamente
    if result.modified_count == 1:
        return {"estatus": True, "mensaje": "Los detalles de la refacción han sido actualizados exitosamente."}
    else:
        raise HTTPException(status_code=404, detail="Refacción no encontrada")

@app.delete("/refacciones/{idRefaccion}", name="Eliminar Refacción por ID")
def delete_spare_part(idRefaccion: int):
    # Eliminar la refacción de la base de datos
    result = conexion.refacciones.delete_one({"_id": idRefaccion})

    # Verificar si la refacción se eliminó correctamente
    if result.deleted_count == 1:
        return {"estatus": True, "mensaje": "La refacción ha sido eliminada exitosamente."}
    else:
        raise HTTPException(status_code=404, detail="Refacción no encontrada")
    

@app.post("/dispositivos", name="Agregar Nuevo Dispositivo")
def agregar_dispositivo(
    idDispositivo: int,
    marca: str,
    modelo: str,
    caracteristicasHardware: str,
    fallas: str,
):
    # Verificar si el ID de dispositivo ya existe en la colección de dispositivos
    if conexion.dispositivos.find_one({"_id": idDispositivo}):
        raise HTTPException(status_code=400, detail="El ID de dispositivo ya existe")

    # Agregar el dispositivo a la colección de dispositivos
    conexion.dispositivos.insert_one({
        "_id": idDispositivo,
        "marca": marca,
        "modelo": modelo,
        "caracteristicasHardware": caracteristicasHardware,
        "fallas": fallas
    })

    # Actualizar el documento de cita con los campos idUsuario e idDispositivo
    cita = {"idUsuario": idDispositivo, "idDispositivo": idDispositivo}
    conexion.coleccion.update_one({"_id": idDispositivo}, {"$set": cita}, upsert=True)

    # Devolver una respuesta exitosa
    mensaje = "El dispositivo se ha agregado correctamente."
    return {"estatus": True, "mensaje": mensaje}

@app.get("/dispositivos", name="Obtener Todos los Dispositivos")
def obtener_dispositivos():
    # Obtener todos los dispositivos de la colección de dispositivos
    dispositivos = list(conexion.dispositivos.find())

    # Formatear la respuesta para incluir solo los campos requeridos
    dispositivos_formateados = []
    for dispositivo in dispositivos:
        dispositivo_formateado = {
            "_id": dispositivo["_id"],
            "marca": dispositivo["marca"],
            "modelo": dispositivo["modelo"],
            "caracteristicasHardware": dispositivo["caracteristicasHardware"],
            "fallas": dispositivo["fallas"],
        }
        dispositivos_formateados.append(dispositivo_formateado)

    # Devolver la lista de dispositivos formateada como respuesta
    return {"dispositivos": dispositivos_formateados}

from fastapi import HTTPException

@app.put("/dispositivos/{idDispositivo}", response_model=dict, name="Actualizar Detalles de Dispositivo por ID")
def actualizar_dispositivo(
    idDispositivo: int,
    marca: str = None,
    modelo: str = None,
    característicasHardware: str = None,
    fallas: str = None,
):
    # Verificar si el dispositivo existe en la base de datos
    dispositivo_existente = conexion.dispositivos.find_one({"_id": idDispositivo})
    if not dispositivo_existente:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")

    # Construir la actualización del dispositivo
    update_data = {}
    if marca is not None:
        update_data["marca"] = marca
    if modelo is not None:
        update_data["modelo"] = modelo
    if característicasHardware is not None:
        update_data["característicasHardware"] = característicasHardware
    if fallas is not None:
        update_data["fallas"] = fallas
    # Puedes agregar aquí la actualización de otros campos si es necesario

    # Actualizar los detalles del dispositivo
    result = conexion.dispositivos.update_one(
        {"_id": idDispositivo},
        {"$set": update_data}
    )

    # Verificar si se actualizó correctamente
    if result.modified_count == 1:
        return {"estatus": True, "mensaje": "Los detalles del dispositivo han sido actualizados exitosamente."}
    else:
        raise HTTPException(status_code=500, detail="No se pudo actualizar el dispositivo")

@app.delete("/dispositivos/{idDispositivo}", response_model=dict, name="Eliminar Dispositivo por ID")
def eliminar_dispositivo(idDispositivo: int):
    # Verificar si el dispositivo existe en la base de datos
    dispositivo_existente = conexion.dispositivos.find_one({"_id": idDispositivo})
    if not dispositivo_existente:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")

    # Eliminar el dispositivo de la base de datos
    result = conexion.dispositivos.delete_one({"_id": idDispositivo})

    # Verificar si se eliminó correctamente
    if result.deleted_count == 1:
        return {"estatus": True, "mensaje": "El dispositivo ha sido eliminado exitosamente."}
    else:
        raise HTTPException(status_code=500, detail="No se pudo eliminar el dispositivo")
 