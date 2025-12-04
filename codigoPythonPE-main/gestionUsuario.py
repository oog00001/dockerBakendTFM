import pandas as pd
import cargarDatos

# Esta funcion se encarga de ver si un usuario existe o no existe dentro de los usuarios suscritos
#modo = 0 = login
#modo = 1 = registro

# el codigo 0 representa a los invitados

def formateo_de_invitados():
    data_user_privados = cargarDatos.csv_datos_privados_usuarios.copy()

    # obtenemos los invitados
    user_privados_invitados = data_user_privados[data_user_privados["nombre"] == "invitado"]

    if(len(user_privados_invitados) > 0):
        #quitamos los invitados de los privados, los users y los ratings
        # Lista de usuarios
        usuarios_invitados = user_privados_invitados["user"].tolist()

        # Filtramos fuera los invitados de todos los csv
        cargarDatos.csv_datos_privados_usuarios = (
            cargarDatos.csv_datos_privados_usuarios[
                ~cargarDatos.csv_datos_privados_usuarios["user"].isin(usuarios_invitados)
            ]
        )

        cargarDatos.csv_usuarios = (
            cargarDatos.csv_usuarios[
                ~cargarDatos.csv_usuarios["user"].isin(usuarios_invitados)
            ]
        )

        cargarDatos.csv_ratings = (
            cargarDatos.csv_ratings[
                ~cargarDatos.csv_ratings["user"].isin(usuarios_invitados)
            ]
        )

        #guardarlo todo
        cargarDatos.guardar_nuevo_usuario_privado()
        cargarDatos.guardar_nuevo_user()
        cargarDatos.guardar_valoracion_rating()






def autentifica_usuario(nombre, contrasena, modo):
    data = cargarDatos.csv_datos_privados_usuarios.copy()


    # Normalizamos el nombre y contraseña que nos envian, es importante pues de no hacerlo da muchos problemas
    nombre = str(nombre).strip().lower()
    contrasena = str(contrasena).strip()

    data["nombre"] = data["nombre"].astype(str).str.strip().str.lower()
    data["contrasena"] = data["contrasena"].astype(str).str.strip()

    if(modo == 0):
        usuario = data.loc[
            (data["nombre"] == nombre) & (data["contrasena"] == contrasena), "user"
        ]
    else:
        usuario = data.loc[
            (data["nombre"] == nombre) , "user"
        ]

    return int(usuario.iloc[0]) if not usuario.empty else -1



# Creamos la suscripcion del usuario
def creacion_interna_credenciales_usuario(id_usuario, nombre, contrasena):
    nueva_fila = {"user": id_usuario, 
                  "nombre": nombre, 
                  "contrasena": contrasena}

    cargarDatos.csv_datos_privados_usuarios = pd.concat([cargarDatos.csv_datos_privados_usuarios, pd.DataFrame([nueva_fila])], ignore_index=True)




# Guardamos el nuevo usuario suscrito en la lista de users, esto verdaderamente no es tan necesario, pero es muy conveniente que lo hagamos
def creacion_interna_usuario(nombre, contrasena):

    ultimo_user_id = cargarDatos.csv_usuarios['user'].max()
    nuevo_user_id = ultimo_user_id + 1

    # Nueva fila
    nueva_fila = {"user": nuevo_user_id, 
                  "sex": "T", 
                  "age": 0,
                  "ocupation": 0, 
                  "zipcode": 48067}

    # Añadir fila
    cargarDatos.csv_usuarios = pd.concat([cargarDatos.csv_usuarios, pd.DataFrame([nueva_fila])], ignore_index=True)


    return nuevo_user_id


# Cogemos de la lista de peliculas 40 peliculas y se las enviamos al nuevo usuario para que las analice
def elegir_20_peliculas_al_azar():
    movies = cargarDatos.csv_peliculas.copy()
    muestra = movies.sample(n=40)
    muestra = muestra[["item", "title"]]
    return muestra








# Creamos un nuevo usuario
def crearUsuario(nombre, contrasena):
    # autentificar al usuario con la base de datos
    # Si el usuario ya existe error
    # Si el usuario no existe lo creamos
    # si es un usuario invitado cambiamos para que sea un usuario invitado
    id_usuario = autentifica_usuario(nombre,contrasena,1)
    if(id_usuario != -1 and id_usuario != 0):
        respuesta = 'error'
    else:
        if(id_usuario == 0):
            # creamos usuario invitado
            nombre = "invitado"
            contrasena = "invitado"
    # Como es nuevo, se seleccionaran 20 peliculas al hazar para que las evalue
        id_usuario = creacion_interna_usuario(nombre, contrasena)
        creacion_interna_credenciales_usuario(id_usuario, nombre, contrasena)
        peliculas_muestra = elegir_20_peliculas_al_azar()
        items_titles = [f"{row['item']}:::{row['title']}" for _, row in peliculas_muestra.iterrows()]
        respuesta = f"{id_usuario}:::" + ":::".join(items_titles)
    return respuesta








# logueamos a un usuario ya existe que se esta intentando conectar al servidor
def loguearUsuario(nombre, contrasena):
    # ver si usuario y contraseña es correcta
    # si es correcta devolvemos un true
    # si es falsa u vuelva a intentarlo
    id_usuario = autentifica_usuario(nombre,contrasena,0)
    if(id_usuario != -1):
        respuesta = id_usuario
    else:
        respuesta = 'error'
    return respuesta




# Un usuario hace una valoracion de las peliculas y eso lo guardamos
def valorar_pelicula(id_usuario, id_pelicula, rating):
    # Nueva fila
    nueva_fila = {"user": id_usuario, 
                  "item": id_pelicula, 
                  "label": rating,
                  "timestamp": 958417523}

    mask = (cargarDatos.csv_ratings["user"] == nueva_fila["user"]) & (cargarDatos.csv_ratings["item"] == nueva_fila["item"])
    
    if mask.any():
        cargarDatos.csv_ratings.loc[mask, "label"] = nueva_fila["label"]
    else:
        cargarDatos.csv_ratings.loc[len(cargarDatos.csv_ratings)] = nueva_fila  # Añadir directamente al final
    
    return 'correcto'

