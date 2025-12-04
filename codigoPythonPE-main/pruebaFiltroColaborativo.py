import cornac
from cornac.datasets import movielens
from cornac.data import Reader
from cornac.models import ItemKNN
from cornac.eval_methods import RatioSplit
import random
import cargarDatos
from cornac.data import Dataset
from cornac.models import SVD  
import numpy as np
import random



# Cargamos el SVD
def cargar_inicializacion_SVD():
    data_user = cargarDatos.cargar_users_limpios()
    data_user = data_user.values.tolist()
    train_set = Dataset.from_uir(data=data_user)


    #Utilizo como modelon KNN iten-user con la similaridad del coseno
    modelSVD = SVD(k=20,  # número de factores latentes, puedes ajustar
                    learning_rate=0.01,
                    max_iter=50,
                    name="SVD")
    
    # Entreno SVD
    modelSVD.fit(train_set)
    print("cargadoSVD")
    return modelSVD

modelSVD = cargar_inicializacion_SVD()


# obtenemos la base de datos actual que se modifica constantemente
def obtener_la_base_datos_actual_usuario(id_usuario):
    data_user = cargarDatos.cargar_ratings()
    items = data_user[data_user["user"] == id_usuario]["item"].tolist()
    return items


# obtener los items que ya ha visto, se comprueba si existe una diferencia en el datasets (podemos o quitar el que ha visto o reentrenar el SVD)
def obtener_items_vistos(user_id, seen_items):
    global modelSVD
    items_actuales = obtener_la_base_datos_actual_usuario(user_id)
    if(len(items_actuales) == len(seen_items)):
        return seen_items
    else: 
        items_vistos = []
        for i in items_actuales:
            if i in modelSVD.train_set.iid_map:
                items_vistos.append(modelSVD.train_set.iid_map[i])
            else:
                nuevo_idx = anadir_nueva_pelicula(i)
                items_vistos.append(nuevo_idx)
        return items_vistos

# Obtenemos las 10 mejores recomendaciones
def obtener_las_10_mejores_recomendaciones(filtered_items):
    # obtenemos los datos basicos y ordenamos
    top_base = 50
    top_n = 10
    top10 = sorted(filtered_items, key=lambda x: x[1], reverse=True)

    if(top_base > len(top10)):
        top_base = len(top10)
    if(top_n > len(top10)):
        top_n = len(top10)
    
    top10 = top10[:top_base]
    top10 = random.sample(top10, top_n)
    return top10


# Hacemos las recomendaciones del SVD
def recomendaciones_SVD(user_id):
    global modelSVD

    user_idx = modelSVD.train_set.uid_map[user_id]
    seen_items = set(t for t in modelSVD.train_set.user_data[user_idx][0])


    # Obtengo los datos a trabajar y todas las configuraciones posibles
    seen_items = obtener_items_vistos(user_id, seen_items)


    # Obtengo el ranking completo para ese usuario
    ranked_items = modelSVD.rank(user_idx=user_idx)

    # Quito de la lista los items que ya ha visto el usuario
    filtered_items = []


    item_indices, scores = ranked_items
    for item_idx, score in zip(item_indices, scores):
        if item_idx not in seen_items:
            filtered_items.append((item_idx, score))


    #Ahora me quedo solo con el top 10
    top10 = obtener_las_10_mejores_recomendaciones(filtered_items)

    soluciones = []
    for item_idx, score in top10:
        item_idx = int(item_idx)  # convertir a entero
        item_id = modelSVD.train_set.item_ids[item_idx]  # Vuelvo a cambiar el id al del conjunto. 
        soluciones.append((item_id,score))
    return soluciones



# Introducimos una nueva pelicula
def anadir_nueva_pelicula(item_id):
    global modelSVD

    # Item nuevo: añadir al modelo
    new_item_idx = len(modelSVD.i_factors)
    modelSVD.train_set.iid_map[item_id] = new_item_idx
    modelSVD.train_set.item_ids[new_item_idx] = item_id

    # Vector latente promedio
    new_vector = np.mean(modelSVD.i_factors, axis=0).reshape(1, -1)
    modelSVD.i_factors = np.vstack([modelSVD.i_factors, new_vector])

    # Sesgo
    if modelSVD.use_bias:
        new_bias_item = np.mean(modelSVD.i_biases)
        modelSVD.i_biases = np.append(modelSVD.i_biases, new_bias_item)

    print(f"Añadiso item {item_id}. ")

    return new_item_idx







# Preparamos al nuevo usuario
def creacion_nuevo_usuario(id_usuario, new_ratings):
    global modelSVD
    # Creamos el nuevo usuario
    new_idx = modelSVD.num_users
    
    # Agregar al mapeo de IDs
    modelSVD.train_set.uid_map[id_usuario] = new_idx
    
    # Inicializar el perfil: promedio de perfiles existentes (o np.zeros(svd.k) para ceros)
    new_profile = np.mean(modelSVD.u_factors, axis=0).reshape(1, -1)
    
    # Extender la matriz de factores latentes
    modelSVD.u_factors = np.vstack([modelSVD.u_factors, new_profile])
    
    # Actualizar número de usuarios
    modelSVD.num_users += 1
    
    # Si usas sesgos (por defecto sí), extender u_biases (promedio o 0)
    if modelSVD.use_bias:
        new_bias = np.mean(modelSVD.u_biases) if len(modelSVD.u_biases) > 0 else 0.0
        modelSVD.u_biases = np.append(modelSVD.u_biases, new_bias)
    
    items_idx = []
    ratings = []
    if new_ratings:
        for item_id, rating in new_ratings:
            if item_id in modelSVD.train_set.iid_map:
                # lo introducimos en la lista
                items_idx.append(modelSVD.train_set.iid_map[item_id])
                ratings.append(rating)
            else:
                new_item_idx = anadir_nueva_pelicula(item_id)
                items_idx.append(new_item_idx)
                ratings.append(rating)

    
    modelSVD.train_set.user_data[new_idx] = (items_idx, ratings)
    
    print(f"Perfil creado para {id_usuario}. Índice: {new_idx}")


# Hacemos recomendacion exclusiva para nuevos usuarios
def recomendaciones_usuario_nuevo(id_usuario, top_n=10):
    global modelSVD

    # cargamos los datos y nos quedamos con las 20 filas del usuario
    data_user = cargarDatos.cargar_users_limpios()
    data_user = data_user[data_user["user"] == id_usuario]

    # Convertir a lista de tuplas (user_id, item_id, rating)
    new_ratings = [(row["item"], row["label"]) for _, row in data_user.iterrows()]

    # Creamos el nuevo usuario
    creacion_nuevo_usuario(id_usuario, new_ratings)

    return recomendaciones_SVD(id_usuario)










# Aqui hacemos el filtro colaborativo
def filtro_colaborativo(id_usuario):
    global modelSVD

    if id_usuario not in modelSVD.train_set.uid_map:
        return recomendaciones_usuario_nuevo(id_usuario)
    else:
        return recomendaciones_SVD(id_usuario)


filtro_colaborativo("6041")