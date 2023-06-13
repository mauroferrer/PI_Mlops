
    ####Importamos librerias 
from fastapi import FastAPI, HTTPException #Para crear la api
import pandas as pd # Manejo de dataframes 
from typing import Optional
import uvicorn  # Para correr nuestra API
from sklearn.metrics.pairwise import cosine_similarity #Utilizamos para obtener la similitud del coseno 
from sklearn.utils.extmath import randomized_svd # Utilizamos SVD para desponer nuestra matriz 
from sklearn.feature_extraction.text import  TfidfVectorizer #Utilizamos para vectorizar datos tipo texto y convertirlos en una representacion numerica
import numpy as np # Manejo de matrices, array, etc
import locale
import datetime




app = FastAPI()

@app.get('/')
def presentacion():
    return 'Mauro_Ferrera'

data = pd.read_csv('data_terminada.csv')

####CONSULTA 1
# Esta consulta nos retorna el mes indicado con la cantidad de peliculas producidas en el mismo
@app.get('/cantidad_filmaciones_mes/{mes}')
def cantidad_filmaciones_mes(mes:str):
    locale.setlocale(locale.LC_TIME,"es_ES")
    data['release_date'] = pd.to_datetime(data['release_date'], format='%Y-%m-%d', errors='coerce')
    mes_indicado = datetime.datetime.strptime(mes, '%B').month
    mes_filtrado = data[data['release_date'].dt.month == mes_indicado].shape[0]
    return{'CANTIDAD DE PELICULAS PRODUCIDAS:':mes_filtrado, 'MES:':mes}



####CONSULTA 2
# Esta consulta nos retorna la cantidad de filmaciones producidas en los dias pasado como parametro
@app.get('/cantidad_filmacion_dia/{dia}')
def cantidad_filmacion_dia(dia:str):
    locale.setlocale(locale.LC_TIME,'es_ES')
    data['release_date'] = pd.to_datetime(data['release_date'],format='%Y-%m-%d', errors='coerce')
    dia_indicado = datetime.datetime.strptime(dia, '%A').day
    dia_filtrado = data[data['release_date'].dt.day == dia_indicado].shape[0]
    return {dia_filtrado,':Cantidad de peliculas producidas en los dias',dia}



####CONSULTA 3
# Esta consulta nos retorna el año de estreno y el score de la pelicula que le pasemos como parametro
@app.get('/score_titulo/{titulo}')
def score_titulo(titulo:str):
    titulo_filtrado = data[data['title'] == titulo]
    año = titulo_filtrado['release_year']
    data['popularity'] = pd.to_numeric(data['popularity'], errors='coerce')
    score = titulo_filtrado['popularity']
    return {'La plicula':titulo, 'se estreno en':año, 'Y su score es de':score}



####CONULTA 4
#Esta cosulta nos retorna la cantidad de votos y el valor promedio de las votaciones de una pelicula
@app.get('/votos_titulo/{titulo}')
def votos_titulo(titulo:str):
    pelicula_filtrada = data[data['title']==titulo]
    votos = pelicula_filtrada['vote_count']
    voto_promedio = pelicula_filtrada['vote_average']
    año = pelicula_filtrada['release_year'] 
    if (votos >= 2000).all():
        return votos,'Es la cantidad de votos y',voto_promedio,'Es el promedio de votaciones', 'de la pelicula',titulo,'estrenada en',año
    else: return 'La pelicula cuenta con menos de 2000 votos'



####CONSULTA 5 
#Esta consulta devuelve el retorno de exito del actor pasado como parametro, ademas de la cantidad de peliculas que ha realizado y el promedio de retorno 
@app.get('/get_actor/{actor}')
def get_actor(actor:str):
    data = pd.read_csv('data_terminada.csv')
    actor_filter = data[data['name'].apply(lambda x: actor in x if isinstance(x, (list, str)) else False)]
    cantidad = actor_filter.shape[0] 
    retorno = actor_filter['return'].sum()
    promedio = actor_filter['return'].mean()
    return actor,'tiene un retorno de:',retorno,'y un retorno promedio de',promedio,'con una cantidad de peliculas actuadas',cantidad



####CONSULTA 6 
# Se coloca el nombre de un director y retorna el retorno del mismo debera devolver el nombre de cada pelicula con su fecha de lanzamiento
@app.get('/get_director/{director}')
def get_director(director:str):
   data = pd.read_csv('data_terminada.csv')
   director_data = data[data['name_director'].apply(lambda x: director in x if isinstance(x, (list, str)) else False)].head(5)
   ganancias_totales = director_data['revenue'].sum()
   peliculas = []
   for _, row in director_data.iterrows():
        titulo = row['title']
        fecha_estreno = row['release_date']
        retorno = row['return']
        peliculas.append({'titulo': titulo, 'fecha_estreno': fecha_estreno, 'retorno':retorno})
    
   return {'nombre del director': director, 'retorno total': ganancias_totales, 'peliculas': peliculas}
   
   
   #### CREACION DEL MODELO DE RECOMENDACIONES ####

user_item = data[['title','vote_count','name_genres']] #Utilizamos solo estas 4 columnas
user_item.reset_index(drop=True) #Reseteamos el indice
user_item = user_item.head(10000) # Cortamos los datos a 10000

#### Creamos la matriz de similitud del coseno ####

# Vectorizador TfidfVectorizer con parámetros de reduccion procesamiento
vectorizer = TfidfVectorizer(min_df=10, max_df=0.5, ngram_range=(1,2))

# Vectorizar, ajustar y transformar el texto de la columna "title" del DataFrame
X = vectorizer.fit_transform(user_item['title'])

# Calcular la matriz de similitud de coseno con una matriz reducida de 7000
similarity_matrix = cosine_similarity(X[:1250,:])

# Obtener la descomposición en valores singulares aleatoria de la matriz de similitud de coseno con 10 componentes
n_components = 10
U, Sigma, VT = randomized_svd(similarity_matrix, n_components=n_components)

# Construir la matriz reducida de similitud de coseno
reduced_similarity_matrix = U.dot(np.diag(Sigma)).dot(VT)



####Creamo la funcion utilizando la matriz 'reduce_similarity_matrix'
#Consulta 7 
@app.get('/get_recomendation/{titulo}')
def get_recommendation(titulo: str):
    try:
        #Ubicamos el indice del titulo pasado como parametro en la columna 'title' del dts user_item
        indice = np.where(user_item['title'] == titulo)[0][0]
        #Encontramos los indices de las puntuaciones y caracteristicas similares del titulo 
        puntuaciones_similitud = reduced_similarity_matrix[indice,:]
        #Ordenamos los indices de menor a mayor
        puntuacion_ordenada = np.argsort(puntuaciones_similitud)[::-1]
        #seleccionamos solo 5 
        top_indices = puntuacion_ordenada[:5]
        #retornamos los 5 items con sus titulos como una lista
        return user_item.loc[top_indices, 'title'].tolist()
        #Si el titulo dado no se encuentra damos un aviso
    except IndexError:
        print(f"El título '{titulo}' no se encuentra en la base de datos. Intente con otro título.")
 


if __name__ == "_main_":

    uvicorn.run(app, host="0.0.0.0", port=8000)