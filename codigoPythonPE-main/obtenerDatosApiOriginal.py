from fastapi import FastAPI # type: ignore
from pydantic import BaseModel # type: ignore
from typing import List
import logging
import requests
import pandas as pd # type: ignore
import ast
from fastapi.middleware.cors import CORSMiddleware # type: ignore
from typing import List
import random
import time
import os
from fastapi.staticfiles import StaticFiles # type: ignore

logging.basicConfig(level=logging.INFO) 
app = FastAPI()
# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todos los orígenes (puedes especificar dominios específicos si lo prefieres)
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permitir todos los encabezados
)

class MovieOnDB(BaseModel):
    idTmdb: int
    rating: int

genres_list = [
    {"id": 28, "name": "Acción"},
    {"id": 12, "name": "Aventura"},
    {"id": 16, "name": "Animación"},
    {"id": 35, "name": "Comedia"},
    {"id": 80, "name": "Crimen"},
    {"id": 99, "name": "Documental"},
    {"id": 18, "name": "Drama"},
    {"id": 10751, "name": "Familia"},
    {"id": 14, "name": "Fantasía"},
    {"id": 36, "name": "Historia"},
    {"id": 27, "name": "Terror"},
    {"id": 10402, "name": "Música"},
    {"id": 9648, "name": "Misterio"},
    {"id": 10749, "name": "Romance"},
    {"id": 878, "name": "Ciencia Ficción"},
    {"id": 10770, "name": "Película para TV"},
    {"id": 53, "name": "Suspenso"},
    {"id": 10752, "name": "Guerra"},
    {"id": 37, "name": "Western"}
]
genres_dict = {genre['id']: genre['name'] for genre in genres_list}
listOfAllMovies = []
dfMovies = None
page = 1
IMG_PATH = "https://image.tmdb.org/t/p/original"
imgDir = '/usr/src/app/data/img_movies'

# Función para convertir cadenas en listas
def convert_genre_ids(genre_ids_str):
    try:
        return ast.literal_eval(genre_ids_str)
    except (ValueError, SyntaxError):
        return []


def download_image_with_retries(url, retries=3, delay=5):
    """Descargar imagen con reintentos en caso de error de conexión."""
    for i in range(retries):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.content
            else:
                print(f"Error {response.status_code} al descargar la imagen.")
                return None
        except requests.exceptions.ConnectionError as e:
            print(f"Error de conexión al intentar descargar {url}: {e}")
            if i < retries - 1:
                print(f"Reintentando en {delay} segundos...")
                time.sleep(delay)
            else:
                print("Máximos intentos alcanzados. Imagen no descargada.")
                return None


def getMoviesFromTmdbApi():
    global page
    global listOfAllMovies
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIyOTU1OGE0YmQxYmNlYWU5NTUwMmFlNjgzMDEwMzhlYiIsIm5iZiI6MTcxOTQzMDQxNS42NDc5NTIsInN1YiI6IjY2MjFhZTRjYmIxMDU3MDE4OWQyNGY4MiIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.NlNxso6YVdLFXXOZXZK9ZzEDXYuDD2HUuTz0P67eKXY",
    }
    response = requests.get(f"https://api.themoviedb.org/3/discover/movie?with_genres=10751&language=es-ES&page={page}&sort_by=popularity.desc",headers=headers)
    if response.status_code == 200:
        if page <= 40:
            listOfAllMovies.extend(response.json()['results'])
            print(f"Page {page} success")
            page += 1
            return getMoviesFromTmdbApi()
        else:
            page = 1
            getCsv()
            return True
    else:
        print("Rejected connection")
        return False


def getCsv():
    dataset = []
    global listOfAllMovies
    global dfMovies
  
    if not os.path.exists(imgDir):
        os.makedirs(imgDir)
        print(f'Carpeta {imgDir} creada.')
    else:
        print(f'Carpeta {imgDir} ya existe. Las imágenes no se descargarán nuevamente.')

    for movie in listOfAllMovies:
        if movie['poster_path'] is None:
            continue
        
        imgUrl = IMG_PATH + movie['poster_path']
        imgPath = os.path.join(imgDir, imgUrl.split('/')[-1])

        # Verifica si la imagen ya existe
        if not os.path.exists(imgPath):
            imgData = download_image_with_retries(imgUrl, retries=3, delay=5)
            if imgData:
                with open(imgPath, 'wb') as f:
                    f.write(imgData)
                print(f'Imagen descargada y guardada en: {imgPath}')
            else:
                print(f'No se pudo descargar la imagen desde {imgUrl}.')
        else:
            print(f'La imagen ya existe en: {imgPath}')

        movieData = {
            'id': movie['id'],
            'title': movie['title'],
            'genre_ids': movie['genre_ids'],
            'poster_path': "img_movies/" + imgUrl.split('/')[-1],
        }
        
        dataset.append(movieData)
    
    dfMovies = pd.DataFrame(dataset)
    """ dfMovies.to_csv('./../data/movies_dataset.csv', index=False) """
    dfMovies.to_csv('/usr/src/app/data/movies_dataset.csv', index=False)



def getUserProfile(moviesRated):
    global dfMovies

    # Extraer los ids de las películas valoradas y sus ratings
    movieIds = [movie.idTmdb for movie in moviesRated]
    ratings = {movie.idTmdb: movie.rating for movie in moviesRated}

    # Filtrar el DataFrame de películas para incluir solo las películas valoradas por el usuario
    filteredMovies = dfMovies[dfMovies['id'].isin(movieIds)].copy()

    # Expandir las listas de géneros en filas separadas
    filteredMovies = filteredMovies.explode('genre_ids')

    # Añadir las calificaciones correspondientes a cada fila de película
    filteredMovies['rating'] = filteredMovies['id'].map(ratings)

    # Agrupar por género y sumar las calificaciones para crear el perfil del usuario
    genderCounts = filteredMovies.groupby('genre_ids')['rating'].sum().to_dict()

    return genderCounts


def getScores(userProfile):
    global dfMovies

    # Crear una Serie de pandas a partir del userProfile para facilitar la operación de mapeo
    userProfileSeries = pd.Series(userProfile)

    # Expandir las filas por géneros
    dfExploded = dfMovies.explode('genre_ids')

    # Mapear los géneros al perfil de usuario y llenar con 0 donde no haya coincidencias
    dfExploded['genre_score'] = dfExploded['genre_ids'].map(userProfileSeries).fillna(0)

    # Agrupar por id de película, sumar los scores de los géneros y convertir en diccionario
    movieScores = dfExploded.groupby('id')['genre_score'].sum().astype(int).to_dict()

    return movieScores


def getExplanation(movie_id, userProfile, dfMovies):
    # Obtener los géneros de la película como una lista de enteros
    genres_ids = dfMovies.loc[dfMovies['id'] == movie_id, 'genre_ids'].values[0]
    
    # Si genres_ids es una cadena, convertimos a lista
    if isinstance(genres_ids, str):
        genres_ids = eval(genres_ids)

    # Obtener nombres de géneros y puntajes, usando comprensión de listas
    genre_names_scores = [
        (genres_dict.get(genre_id, "Desconocido"), userProfile.get(genre_id, 0))
        for genre_id in genres_ids
    ]

    # Filtrar géneros con puntajes positivos
    genre_names, score_details = zip(*[(name, score) for name, score in genre_names_scores if score > 0]) if genre_names_scores else ([], [])

    # Excluir el género "Familiar" (con id 10751)
    filtered_genres = [(name, score) for name, score in zip(genre_names, score_details) if name != "Familia"]

    # Generar la explicación
    if filtered_genres:
        # Tomar los dos primeros géneros más relevantes (excluyendo "Familia")
        top_genres = ' y '.join([name for name, score in filtered_genres[:2]])
        explanation = f"Porque te gusta la {top_genres}"
    else:
        explanation = "Te recomendamos esta película debido a su popularidad."

    return explanation

@app.post("/recommender")
def index(moviesRated: List[MovieOnDB]):
    userProfile = getUserProfile(moviesRated)
    scores = getScores(userProfile)

    ratedMoviesIds = {movie.idTmdb for movie in moviesRated}

    # Obtener las top 40 películas sin contar las ya calificadas
    top_movies = [
        (movieId, score) for movieId, score in sorted(scores.items(), key=lambda x: x[1], reverse=True)
        if movieId not in ratedMoviesIds
    ][:60]

    # Seleccionar aleatoriamente 10 de esas 40
    selected_movies = random.sample(top_movies, min(10, len(top_movies)))

    # Crear la lista de recomendaciones
    recommendations = [
        {
            "id": id,
            "txt": getExplanation(id, userProfile, dfMovies),
            "img": dfMovies.loc[dfMovies['id'] == id, 'poster_path'].values[0]
        }
        for id, score in selected_movies
    ]

    return {"success": True, "recommendations": recommendations}

@app.get("/getAllMovies")
def allMovies():
    global dfMovies

    # Convertir el DataFrame en una lista de diccionarios
    movies_list = dfMovies.to_dict(orient="records")

    return {
        "success": True,
        "allMovies": movies_list
    }

          
# Cargar variable de entorno para decidir si actualizar o usar los datos locales
movies_source = os.getenv("MOVIES_SOURCE", "local").lower()
use_api = movies_source == "api" or not os.path.exists("/usr/src/app/data/img_movies/")

if use_api:
    print("Usando datos de la API..." if movies_source == "api" else "No hay suficientes datos locales, usando la API...")
    if getMoviesFromTmdbApi():
        print("Conexión a TMDB -> éxito")
    else:
        print("Error al obtener películas de la API de TMDB")
else:
    print("Usando datos locales...")
    dfMovies = pd.read_csv("/usr/src/app/data/movies_dataset.csv")
    dfMovies['genre_ids'] = dfMovies['genre_ids'].apply(convert_genre_ids)

# Este bloque es común para ambos casos
app.mount("/img_movies", StaticFiles(directory="/usr/src/app/data/img_movies/"), name="img_movies")

