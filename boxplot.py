import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys

'''
    criar boxplots dos dados INT
        - 1 plotar um grafico só
        - plotar varios
        - salvar valores relevantes (media, mediana, max, min, Q1, Q3, percentil 95, limites superior e inferior)
'''

def oneBoxplot():
    experimento = 'Ex30' # Inserir ID experimento
    coluna = 'downlink deq_timedelta'

    df = pd.read_csv(f'INT_data/{experimento}.csv')
    data = df[coluna]

    minimo = data.min()
    maximo = data.max()
    media = data.mean()  
    mediana = data.median()
    primeiro_quartil = data.quantile(0.25)
    terceiro_quartil = data.quantile(0.75)
    percentil_95 = data.quantile(0.95)
    limite_inferior = primeiro_quartil - 1.5 * (terceiro_quartil - primeiro_quartil)
    limite_superior = terceiro_quartil + 1.5 * (terceiro_quartil - primeiro_quartil)
    
    print("min:", minimo)
    print("max:", maximo)
    print("avg:", media)
    print("mid:", mediana)
    print("1° quartile:", primeiro_quartil)
    print("3° quartile:", terceiro_quartil)
    print("percentile 95:", percentil_95)
    print("Limite Inferior:", limite_inferior)
    print("Limite Superior:", limite_superior)

    plt.figure(figsize =(11, 6))
    plt.boxplot(data,  vert = 1, patch_artist = False)
    plt.title(f"{experimento} - {coluna}", loc="center", fontsize=12)
    plt.ylabel("Packets")

    plt.show()






def main():

    oneBoxplot()
    


    
main()    
