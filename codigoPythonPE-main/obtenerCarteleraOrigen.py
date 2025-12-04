import cargarDatos
import os
import requests
from pathlib import Path
import pandas as pd

import gestionUsuario

import spacy
nlp = spacy.load("es_core_news_sm")  # modelo en español


# recuerda que hay que hacer pip freeze > requirements.txt


# Obtenemos todos los generos de peliculas 
def sacar_todos_tags_peliculas_tmdb(descripcion, generos):
    lista_generos = generos.copy()
    if not descripcion or not descripcion.strip():
        lista_generos = list(dict.fromkeys(lista_generos))
        return ','.join(lista_generos)
    
    doc = nlp(descripcion)
    palabras = [token.lemma_.lower() for token in doc if token.pos_ in ["NOUN", "PROPN", "ADJ"] and not token.is_stop]
    palabras_unicas = list(dict.fromkeys(palabras))

    lista_generos.extend(palabras_unicas)
    return ','.join(lista_generos)



# creamos la nueva pelicula que hemos descargado y la añadimos a los datos que ya tenemos
def crear_formato_pelicula_nueva(titulo, generos, descripcion):
    generos_completo = sacar_todos_tags_peliculas_tmdb(descripcion, generos)
    ultimo_item_id = cargarDatos.csv_peliculas["item"].max()
    nuevo_item_id = ultimo_item_id + 1

    pelicula_nueva = {"item": nuevo_item_id, 
                  "title": titulo, 
                  "genres": generos_completo}
    
    cargarDatos.csv_peliculas.loc[len(cargarDatos.csv_peliculas)] = pelicula_nueva
    cargarDatos.csv_peliculas_embeding_originales.loc[len(cargarDatos.csv_peliculas)] = pelicula_nueva

    return pelicula_nueva

# miramos si existe la pelicula anteriormente
def existe_pelicula_previamente(titulo):

    mask = (cargarDatos.csv_peliculas_embeding_originales["title"] == titulo)
    return mask


# guardamos la nueva cartelera y los datos de peliculas y peliculas con tags actualizado
def guardar_nueva_cartelera(nueva_cartelera):
    cargarDatos.csv_peliculas_embeding = nueva_cartelera
    cargarDatos.guardar_nueva_pelicula()
    cargarDatos.guardar_peliculas_para_emmbeding()
    cargarDatos.guardar_peliculas_para_emmbeding_originales()




# Funcion para descargar la imagen
def descargar_imagen(poster_path, pelicula_nueva):
    if poster_path:
        imagen_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
        nombre_archivo = f"{pelicula_nueva["item"]}"

        base_dir_img = os.path.dirname(os.path.abspath(__file__))
        data_dir_img = os.path.join(base_dir_img, "ml-1m")
        img_dir = os.path.join(data_dir_img, "images")
        ruta_archivo = os.path.join(img_dir, f"{nombre_archivo}.jpg")

        # Descargar la imagen
        img_data = requests.get(imagen_url).content
        with open(ruta_archivo, "wb") as f:
            f.write(img_data)

        print(f"  Imagen guardada en: {ruta_archivo}")
    else:
        print(" No hay imagen disponible.")






headers = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIyOTU1OGE0YmQxYmNlYWU5NTUwMmFlNjgzMDEwMzhlYiIsIm5iZiI6MTcxOTQzMDQxNS42NDc5NTIsInN1YiI6IjY2MjFhZTRjYmIxMDU3MDE4OWQyNGY4MiIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.NlNxso6YVdLFXXOZXZK9ZzEDXYuDD2HUuTz0P67eKXY",
}


# Crear carpeta 'data' si no existe
output_folder = Path("ml-1m")
output_folder.mkdir(exist_ok=True)

# Endpoint de películas en cartelera
url = "https://api.themoviedb.org/3/movie/now_playing"

# Parámetros de la consulta
params = {
    "language": "es-ES",
    "page": 1,
    "region": "ES"
}

# Solicitud principal
response = requests.get(url, headers=headers, params=params)
if response.status_code != 200:
    print("Error al conectar con TMDb:", response.status_code, response.text)
    exit()

data = response.json()
peliculas = data.get("results", [])[:10]

# Obtener géneros
genres_url = "https://api.themoviedb.org/3/genre/movie/list"
genres_response = requests.get(genres_url, headers=headers, params=params)
genre_map = {g["id"]: g["name"] for g in genres_response.json()["genres"]}

# Iterar sobre las películas
nueva_cartelera = pd.DataFrame(columns=["item", "title", "genres"])
for i, peli in enumerate(peliculas, 1):
    titulo = peli["title"]
    descripcion = peli.get("overview", "Sin descripción disponible.")
    generos = [genre_map.get(gid, "Desconocido") for gid in peli.get("genre_ids", [])]
    poster_path = peli.get("poster_path")

    print(f"\n {i}. {titulo}")
    print(f"  Géneros: {', '.join(generos)}")
    print(f" Descripción: {descripcion}")


    mask = existe_pelicula_previamente(titulo)
    if mask.any():
        pelicula_nueva = cargarDatos.csv_peliculas_embeding_originales[mask]
        print()
    else:
        pelicula_nueva = crear_formato_pelicula_nueva(titulo, generos, descripcion)
        descargar_imagen(poster_path, pelicula_nueva)
        pelicula_nueva = pd.DataFrame([pelicula_nueva])  # 🔹 lo convertimos a DataFrame de una fila
    nueva_cartelera = pd.concat([nueva_cartelera, pelicula_nueva], ignore_index=True)
guardar_nueva_cartelera(nueva_cartelera)


# Aprovechamos y hacemos la gestion de invitados
gestionUsuario.formateo_de_invitados()

