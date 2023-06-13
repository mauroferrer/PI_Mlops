import pandas as pd
import numpy as np 
from fastapi import FastAPI
import uvicorn 
import locale
import datetime

app = FastAPI()

@app.get('/')
def presentacion():
    return 'Mauro_Ferrera'

data = pd.read_csv('Csvs\\data_terminada.csv')

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
    data = pd.read_csv('Csvs\\data_terminada.csv')
    actor_filter = data[data['name'].apply(lambda x: actor in x if isinstance(x, (list, str)) else False)]
    cantidad = actor_filter.shape[0] 
    retorno = actor_filter['return'].sum()
    promedio = actor_filter['return'].mean()
    return actor,'tiene un retorno de:',retorno,'y un retorno promedio de',promedio,'con una cantidad de peliculas actuadas',cantidad



####CONSULTA 6 
# Se coloca el nombre de un director y retorna el retorno del mismo debera devolver el nombre de cada pelicula con su fecha de lanzamiento
@app.get('/get_director/{director}')
def get_director(director:str):
   data = pd.read_csv('Csvs\\data_terminada.csv')
   director_data = data[data['name_director'].apply(lambda x: director in x if isinstance(x, (list, str)) else False)].head(5)
   ganancias_totales = director_data['revenue'].sum()
   peliculas = []
   for _, row in director_data.iterrows():
        titulo = row['title']
        fecha_estreno = row['release_date']
        retorno = row['return']
        peliculas.append({'titulo': titulo, 'fecha_estreno': fecha_estreno, 'retorno':retorno})
    
   return {'nombre del director': director, 'retorno total': ganancias_totales, 'peliculas': peliculas}
   
   
   