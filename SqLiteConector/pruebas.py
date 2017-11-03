from SqLiteConnection import SqLiteConnection
import pandas as pd
from sklearn.neighbors import NearestNeighbors
import pickle
import numpy as np

#funciones auxiliares
#funcion auxiliar para restar dos listas coordenada a coordenada
def restar(a,b):
    lon = len(a)
    sol = [0]*lon
    for i in range(lon):
        sol[i] = a[i]-b[i]
    return sol

def suma(a,b):
    lon = len(a)
    sol = [0]*lon
    for i in range(lon):
        sol[i] = a[i]+b[i]
    return sol

def dar_destino(listaCandidatos,pesos,distances,predecir):
    destinos = []
    for i in listaCandidatos:
        aux = restar(i,predecir)
        destinos.append(aux) 
    destinoPesos = []
    for i in range(len(pesos)):
        distancia = distances[i]
        peso = pesos[i]
        destino = destinos[i]
        destinoPesos.append(map(lambda x: x*peso,destino))
    sol = reduce(lambda x,y:suma(x,y),destinoPesos,[0]*len(destinoPesos[0]))
    destino = sol.index(max(sol))
    return destino


def main():
	#creamos las conexiones con la base de datos
    	path = '/home/vic/Repositorios/MyDestiny/MyDestinyAPP/MyDestiny/app.db'
	sql = SqLiteConnection(path)
	con = sql.connector()
	query = 'select * from datosmodelo'
	#cargamos los datos para el modelo
 	datos = pd.read_sql(query,con,index_col='id')
	#agrupamos todos los vectores iguales
	destinos = datos.columns[2:].tolist()
	agrupados = datos.groupby(destinos)['full_name'].count().reset_index()
	#preparamos los datos para entrenar el modelo
	X= agrupados[destinos].values
	#entrenamos el modelo
	vecinos  = NearestNeighbors(n_neighbors=5,metric='cosine',algorithm='brute')
	vecinos = vecinos.fit(X)
	#guardamos el modelo
	filename = 'train_model.pkl'
	pickle.dump(vecinos, open(filename, 'wb'))

	return agrupados,datos,destinos

if __name__ == '__main__':
	filename = 'train_model.pkl'
	agrupados,datos,destinos = main()
	# load the model from disk
	loaded_model = pickle.load(open(filename, 'rb'))
	predecir = np.array([datos[destinos].values[25]])

	#sacamos las prediciones, o vectores que mas se asemejen al original
	distances, indices = loaded_model.kneighbors(predecir)

	#definimos las variables para sacar resultado
	candidatos = agrupados.iloc[indices[0],:][destinos].values
	pesos = agrupados.iloc[indices[0],:]['full_name'].values

	#obtenemos el resultado
	destino = dar_destino(candidatos,pesos,distances[0],predecir[0])
	nombreisodestino = destinos[destino]

	#codigos alfa-2
	tables = pd.read_html('https://es.wikipedia.org/wiki/ISO_3166-1')
	tabla = tables[1]
	columnas = tabla.iloc[0,:]
	tabla.columns = ['nombre_comun','nombre_oficial','alfa-2','alfa-3','cod_numerico','obervaciones']
	codigosPaises = tabla[1:]

	#devolvemos el destino
	destinoFinal = codigosPaises[codigosPaises['alfa-2']==nombreisodestino]
	print destinoFinal
