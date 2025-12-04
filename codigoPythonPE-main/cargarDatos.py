import pandas as pd
import requests

# las peliculas son id,title,genre_ids

# cargamos la base de datos de las peliculas de movilens
def cargar_peliculas_movilens():
    movies = pd.read_csv( "ml-1m/movies.dat", sep="::",
        names=["item", "title", "genres"],
        engine='python',
        encoding="latin-1"
    )
    return movies

# cargamos la base de datos de los usuarios de movilens
def cargar_usuarios():
    data = pd.read_csv("ml-1m/users.dat", sep="::",
                    names=["user", "sex", "age", "ocupation", "zipcode"], engine='python') 
    return data  

# cargamos la base de datos de los ratings de movilens
def cargar_ratings():
    data = pd.read_csv("ml-1m/ratings.dat", sep="::",
                    names=["user", "item", "label", "timestamp"], engine='python')
    return data

# cargamos la base de datos interna de subscripciones 
def cargar_datos_privados_usuarios():
    data = pd.read_csv("ml-1m/privados.dat", sep="::",
                    names=["user", "nombre", "contrasena"], engine='python')
    return data

# cargamos la base de datos interna con todos los posibles tags para usuarios. En este caso la cartelera de 10 peliculas
def cargar_peliculas_para_embeding():
    movies = pd.read_csv( "ml-1m/movies_tags.txt", sep="::",
        names=["item", "title", "genres"],
        engine='python',
        encoding="utf-8"
    )
    return movies

# cargamos la base de datos interna con todos los posibles tags para usuarios. En este caso todos los tags
def cargar_peliculas_para_embeding_originales():
    movies = pd.read_csv( "ml-1m/movies_tags_original.txt", sep="::",
        names=["item", "title", "genres"],
        engine='python',
        encoding="utf-8"
    )
    return movies

def guardar_nuevo_usuario_privado():
    global csv_datos_privados_usuarios
    with open("ml-1m/privados.dat", "w", encoding="utf-8") as f:
        for row in csv_datos_privados_usuarios.itertuples(index=False):
            line = "::".join(str(x) for x in row)
            f.write(line + "\n")

def guardar_nuevo_user():
    global csv_usuarios
    with open("ml-1m/users.dat", "w", encoding="utf-8") as f:
        for row in csv_usuarios.itertuples(index=False):
            line = "::".join(str(x) for x in row)
            f.write(line + "\n")

def guardar_valoracion_rating():
    global csv_ratings, csv_ratings_limpios
    csv_ratings_limpios = cargar_ratings_limpios()
    with open("ml-1m/ratings.dat", "w", encoding="utf-8") as f:
        for row in csv_ratings.itertuples(index=False):
            line = "::".join(str(x) for x in row)
            f.write(line + "\n")

def guardar_nueva_pelicula():
    global csv_peliculas
    with open("ml-1m/movies.dat", "w", encoding="utf-8") as f:
        for row in csv_peliculas.itertuples(index=False):
            line = "::".join(str(x) for x in row)
            f.write(line + "\n")

def guardar_peliculas_para_emmbeding():
    global csv_peliculas_embeding
    with open("ml-1m/movies_tags.txt", "w", encoding="utf-8") as f:
        for row in csv_peliculas_embeding.itertuples(index=False):
            line = "::".join(str(x) for x in row)
            f.write(line + "\n")

def guardar_peliculas_para_emmbeding_originales():
    global csv_peliculas_embeding_originales, csv_peliculas_embeding_originales_limpios
    csv_peliculas_embeding_originales_limpios = cargar_peliculas_para_embeding_originales_limpios()
    with open("ml-1m/movies_tags_original.txt", "w", encoding="utf-8") as f:
        for row in csv_peliculas_embeding_originales.itertuples(index=False):
            line = "::".join(str(x) for x in row)
            f.write(line + "\n")
    

def cargar_ratings_limpios():
    global csv_ratings
    data_user = csv_ratings.copy()
    data_user = data_user[["user", "item", "label"]]

    # Función para limpiar caracteres invisibles
    def clean_string(val):
        if isinstance(val, str):
            # Elimina caracteres no imprimibles
            return ''.join(c for c in val if c.isprintable())
        return val

    # Limpiamos las columnas 'user' y 'item'
    data_user["user"] = data_user["user"].apply(clean_string)
    data_user["item"] = data_user["item"].apply(clean_string)

    data_user["user"] = data_user["user"].astype(int)
    data_user["item"] = data_user["item"].astype(int)
    data_user["label"] = data_user["label"].astype(int)

    return data_user

def cargar_peliculas_para_embeding_originales_limpios():
    global csv_peliculas_embeding_originales
    pelis = csv_peliculas_embeding_originales.copy()

    def clean_string(val):
        if isinstance(val, str):
            # Elimina caracteres no imprimibles
            return ''.join(c for c in val if c.isprintable())
        return val
    
    pelis["item"] = pelis["item"].apply(clean_string)
    pelis["item"] = pelis["item"].astype(int)

    return pelis

def cargar_peliculas_para_embeding_limpios():
    global csv_peliculas_embeding
    pelis = csv_peliculas_embeding.copy()

    def clean_string(val):
        if isinstance(val, str):
            # Elimina caracteres no imprimibles
            return ''.join(c for c in val if c.isprintable())
        return val
    
    pelis["item"] = pelis["item"].apply(clean_string)
    pelis["item"] = pelis["item"].astype(int)

    return pelis  



csv_peliculas = cargar_peliculas_movilens()
csv_usuarios = cargar_usuarios()
csv_ratings = cargar_ratings()
csv_datos_privados_usuarios = cargar_datos_privados_usuarios()
csv_peliculas_embeding = cargar_peliculas_para_embeding()
csv_peliculas_embeding_originales = cargar_peliculas_para_embeding_originales()

csv_ratings_limpios = cargar_ratings_limpios()
csv_peliculas_embeding_originales_limpios = cargar_peliculas_para_embeding_originales_limpios()
print("cargada todas las bases de datos")