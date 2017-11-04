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


def predict(input):
    # TODO Javi: Cambiar variables y metodos a ingles
    # TODO Javi: Crear tabla agrupados_modelo (tabla con pesos).
    # TODO Javi: Leer solo pesos necesarios
    # TODO Javi: Optimizar el codgio, revisarlo. (Por ejemplo, acabamos de cmabiar destinos por una constante de arriba)
    # TODO Javi: Insertar nuevos usuarios.
    # creamos las conexiones con la base de datos
    sql = SqLiteConnection(path_db)
    con = sql.connector()
    query = 'select * from datosmodelo'
    # cargamos los datos para el modelo
    datos = pd.read_sql(query, con, index_col='id')
    # agrupamos todos los vectores iguales
    agrupados = datos.groupby(destinos)['full_name'].count().reset_index()
    model = pickle.load(open(path_model, 'rb'))
    # sacamos las prediciones, o vectores que mas se asemejen al original
    distances, indexes = model.kneighbors(input)
    # definimos las variables para sacar resultado
    candidatos = agrupados.iloc[indexes[0], :][destinos].values
    pesos = agrupados.iloc[indexes[0], :]['full_name'].values
    # obtenemos el resultado
    destino = dar_destino(candidatos, pesos, distances[0], input[0])
    # Return country ISO code
    return destinos[destino]

