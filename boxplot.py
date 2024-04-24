import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

'''
    criar boxplots dos dados INT
        - 1 plotar um grafico só
        - plotar varios
        - salvar valores relevantes (media, mediana, max, min, Q1, Q3, percentil 95, limites superior e inferior)
'''

def oneBoxplot():
    folder = 'INT_tests'
    experimento = 'teste8000MK' # Inserir ID experimento
    coluna = 'downlink deq_qdepth'

    df = pd.read_csv(f'{folder}/{experimento}.csv')
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


def NBoxplot():
    folder = 'INT_tests'
    coluna = 'downlink deq_qdepth'
    experimentos = ['teste2000MK', 'teste4000MK', 'teste6000MK', 'x']

    data = []

    for experimento in experimentos:
        if experimento != 'x':
            df = pd.read_csv(f'{folder}/{experimento}.csv')
            data.append(df[coluna])
    

    plt.figure(figsize =(11, 6))
    plt.boxplot(data,  vert = 1, patch_artist = False)
    plt.ylabel("Packets")

    plt.show()


def saveStatistics():
    in_folder = 'INT_data'
    out_folder = 'Stats_INT'
    int_columns = ['downlink deq_qdepth', 
                    'downlink deq_timedelta', 
                    'downlink enq_qdepth', 
                    'uplink deq_qdepth', 
                    'uplink deq_timedelta', 
                    'uplink enq_qdepth']
    
    stat_columns = ['min',
                    'max',
                    'avg',
                    'mid',
                    'std_dev',
                    'first_quartile',
                    'third_quartile',
                    'percentile_95',
                    'lower_limit',
                    'upper_limit']
    
    filesList = os.listdir(in_folder)
    
    for file in filesList:
        filePath = os.path.join(in_folder, file)
        if os.path.isfile(filePath):
            df = pd.read_csv(filePath)
            statistics = pd.DataFrame(columns=stat_columns, index=int_columns)

            for column in int_columns:
                data = df[column]
                min = data.min()
                max = data.max()
                avg = data.mean()  
                mid = data.median()
                std_dev = np.std(data)
                first_quartile = data.quantile(0.25)
                third_quartile = data.quantile(0.75)
                percentile_95 = data.quantile(0.95)
                lower_limit = first_quartile - 1.5 * (third_quartile - first_quartile)
                upper_limit = third_quartile + 1.5 * (third_quartile - first_quartile)
                data_line = {   'min': min, 
                                'max': max, 
                                'avg': avg, 
                                'mid': mid, 
                                'std_dev': std_dev,
                                'first_quartile': first_quartile, 
                                'third_quartile': third_quartile, 
                                'percentile_95': percentile_95, 
                                'lower_limit': lower_limit,
                                'upper_limit': upper_limit
                            } 
                
                statistics.loc[column] = data_line

            statistics.to_csv(f"{out_folder}/{file}")
            print(f'{file} criado')












def main():
    #oneBoxplot()
    #NBoxplot()
    saveStatistics()
    


    
main()    
