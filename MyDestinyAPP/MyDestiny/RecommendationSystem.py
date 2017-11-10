# -*- coding: UTF8 -*-

from SqLiteConnection import SqLiteConnection
import pandas as pd
import pickle
from sklearn.neighbors import NearestNeighbors
from constants import *


# funciones auxiliares

# funcion auxiliar para restar dos listas coordenada a coordenada
def restar(a, b):
    lon = len(a)
    sol = [0] * lon
    for i in range(lon):
        sol[i] = a[i] - b[i]
    return sol


def suma(a, b):
    lon = len(a)
    sol = [0] * lon
    for i in range(lon):
        sol[i] = a[i] + b[i]
    return sol

# TODO Review distancia var and top 5 get AU by default when has few cases
def dar_destino(listaCandidatos, pesos, distances, predecir):
    destinos = []
    for i in listaCandidatos:
        aux = restar(i, predecir)
        destinos.append(aux)
    destinoPesos = []
    for i in range(len(pesos)):
        distancia = distances[i]
        peso = pesos[i]
        destino = destinos[i]
        destinoPesos.append(map(lambda x: x * peso, destino))
    sol = reduce(lambda x, y: suma(x, y), destinoPesos, [0] * len(destinoPesos[0]))
    destino = sol.index(max(sol))
    return destino


# TODO Review distancia var and top 5 get AU by default when has few cases
def dar_destino_top5(listaCandidatos, pesos, distances, predecir):
    destinos = []
    for i in listaCandidatos:
        aux = restar(i, predecir)
        destinos.append(aux)
    destinoPesos = []
    for i in range(len(pesos)):
        distancia = distances[i]
        peso = pesos[i]
        destino = destinos[i]
        destinoPesos.append(map(lambda x: x * peso, destino))
    sol = reduce(lambda x, y: suma(x, y), destinoPesos, [0] * len(destinoPesos[0]))
    orden = sorted(sol)
    orden.reverse()
    top_5 = orden[0:5]
    destino = [sol.index(i) for i in top_5]
    return destino


def predict(input):
    # creamos las conexiones con la base de datos
    sql = SqLiteConnection(PATH_DB)
    con = sql.connector()
    query = 'select * from agrupados_modelo'
    # cargamos los datos para el modelo
    agrupados = pd.read_sql(query, con, index_col='id')
    model = pickle.load(open(PATH_MODEL, 'rb'))
    # sacamos las prediciones, o vectores que mas se asemejen al original
    distances, indexes = model.kneighbors(input)
    # definimos las variables para sacar resultado
    candidatos = agrupados.iloc[indexes[0], :][COUNTRY_LIST].values
    pesos = agrupados.iloc[indexes[0], :]['full_name'].values
    # obtenemos el resultado
    # destino = dar_destino(candidatos, pesos, distances[0], input[0])  #
    destino_top5 = dar_destino_top5(candidatos, pesos, distances[0], input[0])
    # return list of top5 country ISO code
    return [COUNTRY_LIST[destino] for destino in destino_top5]
    # Return country ISO code
    # return COUNTRY_LIST[destino]
