import numpy as np
import pandas as pd
import math
import cargarDatos
from transformers import AutoTokenizer, AutoModel
import torch
import re

# Cargamos el modelo BERT
def cargar_inicializacion_BERT():
    model_name = "bert-base-uncased"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    modelBC = AutoModel.from_pretrained(model_name)
    modelBC.eval()
    print("bert cargado")
    return modelBC, tokenizer



# Esta funcion genera un embedding promedio, mediante vector, del texto usando BERT
def get_bert_embedding(text, tokenizer, model):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=128)
    with torch.no_grad():
        outputs = model(**inputs)
    emb = outputs.last_hidden_state.mean(dim=1)
    return emb.squeeze().numpy()


# Cargaremos las peliculas de la cartelera
def cargar_Inicializacion_peliculas_cartelera():
    global modelBC, tokenizer
    # Cargamos los datos
    movies = cargarDatos.cargar_peliculas_para_embeding_limpios()
    # Crear columna combinada
    movies["desc"] = movies["title"] + ':' + movies["genres"]

    # Creamos el  embeddings de todas las películas
    print("\n🧠 Generando embeddings... (esto puede tardar un poco)")
    # Pasamos tokenizer y model usando lambda
    movies["embedding"] = movies["desc"].apply(lambda x: get_bert_embedding(x, tokenizer, modelBC))

    return movies

modelBC, tokenizer = cargar_inicializacion_BERT()
moviesBC = cargar_Inicializacion_peliculas_cartelera()








# calculamos la similitud del coseno entre dos vectores, usamos numpy
def cosine_similarity_manual(vec1, vec2):
    dot = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)


# Esta funcion se encarga de hacer una recomendacion, dado un texto, en este caso nombre: tags, hace una recomendacion de peliculas
def recomendar(movies, query, tokenizer, model, top_n):
    query_emb = get_bert_embedding(query, tokenizer, model)
    
    # Calcular similitudes manualmente
    similitudes = []
    for _, row in movies.iterrows():
        sim = cosine_similarity_manual(query_emb, row["embedding"])
        similitudes.append(sim)
    
    movies["similarity"] = similitudes
    recomendaciones = movies.sort_values(by="similarity", ascending=False)#.head(top_n)
    
    # usamos item, pero por si se usa otra base de datos o hay algun problema, que nunca esta de mas
    if "item" in recomendaciones.columns:  # por si usas 'item' en lugar de 'movieId'
        return recomendaciones[["item", "title", "similarity", "explicacion"]]
    else:
        # por si hay problema con el nombre de la columna
        return recomendaciones[["title", "similarity", "explicacion"]]



# A partir de las peliculas que el usuario anteriormente ha visto, sacamos los tags que le gustan al usuario
def obtener_gustos_de_usuario(user_id):
    pelis = cargarDatos.cargar_peliculas_para_embeding_originales_limpios()
    ratings = cargarDatos.cargar_ratings_limpios()

    print("user_id que buscas:", user_id)
    print("Usuarios en ratings:")
    for u in ratings["user"].unique():
        print(u)
    print("Coincidencias:", ratings[ratings["user"] == user_id])

    items_vistos = ratings[ratings["user"] == user_id]["item"]
    peliculas_vistas = pelis[pelis["item"].isin(items_vistos)]
    print("items vistos")
    print(items_vistos)
    print("peliculas vistas")
    print(peliculas_vistas)

    generos = set()
    for g in peliculas_vistas["genres"]:
        generos.update(g.split(','))
    
    todos_generos = ' '.join(generos)
    return todos_generos

# queremos tener una explicabilidad de porque a un usuario le puede gustar o no una pelicula, creamos una pelicula explicacion
def generar_explicabilidad(movies, user_query):
    query_genres = set(user_query.lower().split())  # ya vienen los géneros que le gustan
    
    def palabras_en_comun(desc):
        # Extraemos géneros de la descripción
        if ':' in desc:
            _, genres_str = desc.split(':', 1)
        else:
            genres_str = desc
        
        # Limpiar signos de puntuación y separar por comas o espacios
        genres_list = re.split('[, ]+', genres_str.lower())
        genres_list = [g.strip() for g in genres_list if g.strip()]
        
        comunes = query_genres.intersection(genres_list)
        return ', '.join(comunes) if comunes else 'Ninguna coincidencia'
    
    movies['explicacion'] = movies['desc'].apply(palabras_en_comun)
    return movies





# El algoritmo basado en contenidos
def basado_en_contenido(user_id):
    global modelBC, tokenizer, moviesBC

    # Hacemos las recomendaciones
    consulta = obtener_gustos_de_usuario(int(user_id))
    movies = generar_explicabilidad(moviesBC, consulta)
    solucion = recomendar(moviesBC, consulta, tokenizer, modelBC, top_n=10)
    print(solucion)
    return solucion

basado_en_contenido("6041")