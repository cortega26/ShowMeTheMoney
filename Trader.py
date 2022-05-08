# En este ejercicio se nos solicitó:
# El retorno y anualizado de tres stock, a saber: SPY, VWO y QQQ entre 2015 y 2021 (ambos inclusive)
# Graficar el retorno acumulado de los stocks indicados durante ese mismo período

import requests
import pandas as pd
import numpy as np
import math


# URL genérica = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={SYMBOL}&outputsize=full&apikey=7M2JKVOWY1ZE0IFW&datatype=csv'
# Sustituir {SYMBOL} por el ticker correspondiente

tickers = ['SPY', 'VWO', 'QQQ']


print('\n','*' * 110, "\n", '*', ' ' * 106, '*')
print(' *   \033[1mNOTA BENE.\033[0m A efectos de una comparación sin sesgos deberíamos incluir los eventuales divivendos de       *')
print(' *   cada acción/activo, sin embargo a efectos de calcular la volatilidad y riesgo/beneficio se utiliza el    *')
print(' *   indicador "Close" y no "Adjusted Close" que además es un indicador Premium en la API de AlphaVantage.    *')
print(' *   Por lo anterior, toda conclusión derivada de estos cálculos debe ser contrastada con el dato mencionado  *')
print(' *', ' ' * 106, '*', '\n','*' * 110, '\n')


def constructor_URL(ticker):
    #print("Indica el código (ticker) del activo:")
    #ticker = input()
    URL = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=' + ticker + '&outputsize=full&apikey=7M2JKVOWY1ZE0IFW&datatype=csv'
    return URL

riesgo_beneficio = {} # Creamos un diccionario vacío para almacenar los nombres de activos y su respectivo riesgo-beneficio
df_retorno_diario = pd.DataFrame() # Creamos un dataframe vacío al que luego insertaremos columnas

for ticker in tickers:
    # Proceso de carga y manipulación de datos
    df = pd.read_csv(constructor_URL(ticker)) # Cargamos el CSV en un Dataframe en Pandas
    df = df.iloc[::-1] # Invertimos el orden del Dataframe para poder trabajarlo correctamente (de la fecha más antigua a la más reciente)
    df['Ret_Log'] = np.log(df['close'] / df['close'].shift(1)).dropna() # Calculamos el retorno logarítmico usando el precio de cierre
    df.drop(['high', 'low', 'volume'], axis = 1, inplace = True) # Eliminamos las columnas que no utilizaremos
    df.drop(df[df['timestamp'] < '2015-01-01'].index, inplace = True) # Eliminamos todas las fechas anteriores al 1 de enero de 2015
    df.drop(df[df['timestamp'] > '2021-12-31'].index, inplace = True) # Eliminamos todas las fechas posteriores al 31 de diciembre de 2021
    
    # Cálculos para obtener la información requerida
    df['Volatilidad'] = df['Ret_Log'].rolling(window=252).std() * np.sqrt(252) * 100 # Calculamos la volatilidad usando la desviación estándar y pandas rolling   
    volat_promedio = round(df['Volatilidad'].mean(), 2) # Cálculo de la volatilidad promedio durante el período
    retorno_total = round((df['close'].iloc[-1] - df['open'].iloc[0]) / df['open'].iloc[0], 4) # Cálculo del retorno total durante el período
    retorno_porcentual = round(retorno_total * 100, 2) # Retorno total del período en términos porcentuales (pregunta 1, parte 1)
    retorno_anualizado = round((((1 + retorno_total)**(1/7)) - 1) * 100, 2) # Cálculo del retorno anualizado = ((1 + retorno_total)^(1/años) - 1)
    df_retorno_diario[ticker] = df['close'].pct_change()[1:] #El retorno acumulado se calcula mediante la variación porcentual diaria
    riesgo_beneficio[ticker] = retorno_anualizado / volat_promedio

    print("El retorno total de {} entre 2015-01-01 y 2021-12-31 es: {}%".format(ticker, retorno_porcentual))
    print("La volatilidad anual promedio de {} es: {}%".format(ticker, volat_promedio))
    print("El retorno anualizado de {} es: {}%\n".format(ticker, retorno_anualizado))


    if ticker == tickers[-1]: #En la última iteración, ya con todos los datos, indicamos la probable mejor opción y se genera el gráfico
        for llave, valor in riesgo_beneficio.items():
            print("El cociente beneficio/volatilidad de {} es {}".format(llave, round(valor, 2)))
        print("La mejor relación beneficio vs. volatilidad (retorno vs. riesgo) la tiene la tiene:", max(riesgo_beneficio, key=riesgo_beneficio.get),"\n")
        df2 = df['timestamp'].iloc[1:]
        df_retorno_diario.set_index(df2, inplace = True) #Reemplazamos el índice del DataFrame retorno diario con las fechas
        df3 = df_retorno_diario.add(1).cumprod().sub(1) # Aplicación de la fórmula de Retornos Acumulados
        df3.plot(title = "Serie Temporal de Retornos Acumulados", ylabel = "Retorno Acumulado (ganancia por cada US$ invertido)", xlabel = "Fecha", rot = 45, figsize=(12,8))
