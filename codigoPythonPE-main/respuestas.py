# codigos
# 0 - filtro colaborativo       men:::id_usu                      se devuelve men:::id_us:::id_peli:nombre_peli
# 1 - basado en contenidos      men:::id_usu                      se devuelve men:::id_us:::id_peli:nombre_peli:::similaridad:::explicacion
# 2 - crear usuario             men:::nombre:::contraseña           se devuelve men:::id_us:::id_peli:nombre_peli
# 3 - loguear usuario           men:::nombre:::contraseña           se devuelve men:::id_us
# 4 - hacer el rating de una pelicula   men:::id_usu:::id_item:::valor      se devuelve men:::correcto
# 5 - enviar imagen de pelicula     men:id_item                 se devuelve la imagen

# mensaje 'codigo:::nombreUsuario:::-:::-:::'

import filtroColaborativo
import basadoEnContenido
import cargarDatos
import gestionUsuario
import os
from PIL import Image

# A partir de los ids de los items recomendados, buscamos los nombres de los mismos.
#  Verdaderamente esta funcion no es del todo necesaria, pero nos ayuda a poder manejar de forma mas efectiva los formatos
def obtener_nombre_pelicula_basado_contenidos(recomendaciones):
    return recomendaciones
    """
    pelis = cargarDatos.cargar_peliculas_movilens()
    nombre_peliculas = []
    item_to_title = {row['item']: row['title'] for _, row in pelis.iterrows()}

    for user_id, recs_array in recomendaciones.items():
        for rec in recs_array:
            for index, row in pelis.iterrows():
                print(rec)
                item_id = row['item']
                title = row['title']
                similaridad = rec['similarity']
                explicacion = rec['explicacion']
                if(item_id == rec):
                    nombre_peliculas.append({"item_id": item_id, "title": title, "similarity": similaridad, "explicacion": explicacion})
                    break
    return nombre_peliculas
    """

# A partir de los ids de los items recomendados, buscamos los nombres de los mismos
def obtener_nombre_pelicula_filtro_colaborativo(recomendaciones):
    pelis = cargarDatos.cargar_peliculas_movilens()
    nombre_peliculas = []
    for rec in recomendaciones:
        for index, row in pelis.iterrows():
            item_id = row['item']
            title = row['title']
            if(item_id == rec[0]):
                nombre_peliculas.append({"item_id": item_id, "title": title})
                break
    return nombre_peliculas



# dependiendo del mensaje y la accion, deberemos de preparar un formato concreto para la respuesta, son similares, pero hay que ceñirse a lo indicado arriba
def crear_respuesta_determinada(id_mensaje, respuesta):
    partes = [str(id_mensaje)]
    mensaje = 'nada'
    if(id_mensaje == '5'):
        base_dir_img = os.path.dirname(os.path.abspath(__file__))
        data_dir_img = os.path.join(base_dir_img, "ml-1m")
        img_dir = os.path.join(data_dir_img, "images")
        ruta_imagen = os.path.join(img_dir, f"{respuesta}.jpg")

        # si no existe la imagen usamos una por default
        if not os.path.exists(ruta_imagen):
            print(f" Imagen {respuesta}.jpg no encontrada, usando default.jpg")
            ruta_imagen = os.path.join(img_dir, "0.jpg")

        with open(ruta_imagen, "rb") as f:
            imagen_bytes = f.read()
        return imagen_bytes
    else:
        if(id_mensaje == '0'):
            for p in respuesta:
                partes.append(str(p['item_id']))
                partes.append(p['title'])
        if(id_mensaje == '1'):
            for index, p in respuesta.iterrows():
                partes.append(str(p['item']))
                partes.append(p['title'])
                partes.append(str(p['similarity']))
                partes.append(p['explicacion'])
        if(id_mensaje == '2'):
            todas_partes = respuesta.split(':::')
            for p in todas_partes:
                partes.append(p)
        if(id_mensaje == '3'):
            partes.append(str(respuesta))
        if(id_mensaje == '4'):
            partes.append(respuesta)
        mensaje = ":::".join(partes)
        print(mensaje)
    return mensaje




# A partir de un mensaje, creamos una respuesta determinada a dicho mensaje
def realizar_accion(mensaje):

    partes = mensaje.split(':::')
    id_mensaje = partes[0]

    if(id_mensaje == '0'):
        # Hacemos un filtro colaborativo
        id_usuario = int(partes[1])
        recomendacion = filtroColaborativo.filtro_colaborativo(id_usuario)
        respuesta = obtener_nombre_pelicula_filtro_colaborativo(recomendacion)
    if(id_mensaje == '1'):
        # hacemos una recomedacion basada en contenidos
        id_usuario = int(partes[1])
        recomendacion = basadoEnContenido.basado_en_contenido(id_usuario)
        respuesta = obtener_nombre_pelicula_basado_contenidos(recomendacion)
    if(id_mensaje == '2'):
        # creamos un usuario nuevo
        nombre = partes[1]
        contrasena = partes[2]
        respuesta = gestionUsuario.crearUsuario(nombre,contrasena)
    if(id_mensaje == '3'):
        #logeamos al usuario
        nombre = partes[1]
        contrasena = partes[2]
        respuesta = gestionUsuario.loguearUsuario(nombre,contrasena)
    if(id_mensaje == '4'):
        # Se evalua la pelicula
        id_usuario = int(partes[1])
        id_pelicula = int(partes[2])
        rating = int(partes[3])
        gestionUsuario.valorar_pelicula(id_usuario, id_pelicula, rating)
        respuesta = "Correcto"
    if(id_mensaje == '5'):
        # Enviamos la imagen de la pelicula
        respuesta = partes[1]
    respuesta = crear_respuesta_determinada(id_mensaje, respuesta)
    return respuesta