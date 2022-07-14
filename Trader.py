# As a part of an application for a job in a fintech company I was tasked to do this exercise:
# 1.- Calculate total and annualized return for three stocks: SPY, VWO and QQQ between 2015 and 2021 (both included)
# 2.- Plot the accumulated return for the three stocks during the same period
# We were instructed to use the Alpha Vantage free API to complete the tasks

import requests
import pandas as pd
import numpy as np
import math


# URL genérica = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={SYMBOL}&outputsize=full&apikey={YOUR_API_KEY}&datatype=csv'
# Change {SYMBOL} and {YOUR_API_KEY} for their corresponding values

tickers = ['SPY', 'VWO', 'QQQ']

print('\n','*' * 110, "\n", '*', ' ' * 106, '*')
print(' *   \033[1mNOTA BENE.\033[0m A efectos de una comparación sin sesgos deberíamos incluir los eventuales divivendos de       *')
print(' *   cada acción/activo, sin embargo a efectos de calcular la volatilidad y riesgo/beneficio se utiliza el    *')
print(' *   indicador "Close" y no "Adjusted Close" que además es un indicador Premium en la API de AlphaVantage.    *')
print(' *   Por lo anterior, toda conclusión derivada de estos cálculos debe ser contrastada con el dato mencionado  *')
print(' *', ' ' * 106, '*', '\n','*' * 110, '\n')


def constructor_URL(ticker):
    URL = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=' + ticker + '&outputsize=full&apikey={YOUR_API_KEY}&datatype=csv'
    return URL

riesgo_beneficio = {}
df_retorno_diario = pd.DataFrame()

for ticker in tickers:
    # Data mining and manipulation
    df = pd.read_csv(constructor_URL(ticker))
    df = df.iloc[::-1]
    df['Ret_Log'] = np.log(df['close'] / df['close'].shift(1)).dropna()
    df.drop(['high', 'low', 'volume'], axis = 1, inplace = True)
    df.drop(df[df['timestamp'] < '2015-01-01'].index, inplace = True)
    df.drop(df[df['timestamp'] > '2021-12-31'].index, inplace = True)
    
    # Calculations for obtain the requested information
    df['Volatilidad'] = df['Ret_Log'].rolling(window=252).std() * np.sqrt(252) * 100   
    volat_promedio = round(df['Volatilidad'].mean(), 2)
    retorno_total = round((df['close'].iloc[-1] - df['open'].iloc[0]) / df['open'].iloc[0], 4)
    retorno_porcentual = round(retorno_total * 100, 2)
    retorno_anualizado = round((((1 + retorno_total)**(1/7)) - 1) * 100, 2)
    df_retorno_diario[ticker] = df['close'].pct_change()[1:]
    riesgo_beneficio[ticker] = retorno_anualizado / volat_promedio

    print("El retorno total de {} entre 2015-01-01 y 2021-12-31 es: {}%".format(ticker, retorno_porcentual))
    print("La volatilidad anual promedio de {} es: {}%".format(ticker, volat_promedio))
    print("El retorno anualizado de {} es: {}%\n".format(ticker, retorno_anualizado))


    if ticker == tickers[-1]:
        for llave, valor in riesgo_beneficio.items():
            print("El cociente beneficio/volatilidad de {} es {}".format(llave, round(valor, 2)))
        print("La mejor relación beneficio vs. volatilidad (retorno vs. riesgo) la tiene la tiene:", max(riesgo_beneficio, key=riesgo_beneficio.get),"\n")
        df2 = df['timestamp'].iloc[1:]
        df_retorno_diario.set_index(df2, inplace = True) #Reemplazamos el índice del DataFrame retorno diario con las fechas
        df3 = df_retorno_diario.add(1).cumprod().sub(1) # Aplicación de la fórmula de Retornos Acumulados
        df3.plot(title = "Serie Temporal de Retornos Acumulados", ylabel = "Retorno Acumulado (ganancia por cada US$ invertido)", xlabel = "Fecha", rot = 45, figsize=(12,8))
