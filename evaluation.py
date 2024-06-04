import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys

# Função para ler o arquivo CSV e criar o gráfico
def compare1Ex(df, coluna1, coluna2, medida):

    coluna_tempo = 'time'

    if (medida == 'Milliseconds'):
        df[coluna1] = df[coluna1] / 1000
        df[coluna2] = df[coluna2] / 1000

    #Infos relevantes
    print(f"Average {medida} of {coluna1}: {df[coluna1].mean():.2f}")
    print(f"Average {medida} of {coluna2}: {df[coluna2].mean():.2f}")

    print(f"Maximum value of {medida} in {coluna1}: {df[coluna1].max():.2f}")
    print(f"Maximum value of {medida} in {coluna2}: {df[coluna2].max():.2f}")

    print(f"Minimum value of {medida} in {coluna1}: {df[coluna1].min():.2f}")
    print(f"Minimum value of {medida} in {coluna2}: {df[coluna2].min():.2f}")

    print()

    # Cria o gráfico
    plt.figure(figsize=(15, 8))
    plt.plot(df[coluna_tempo], df[coluna1], label=coluna1)
    plt.plot(df[coluna_tempo], df[coluna2], label=coluna2)

    # Adiciona rótulos e título
    plt.xlabel("Time")
    plt.ylabel(medida)
    plt.title(f"{sys.argv[1]} - Comparison between {coluna1} and {coluna2}")
    
    # Adiciona a legenda
    plt.legend()

    # Exibe o gráfico
    plt.show()


def compare2Ex(df1, df2, coluna, medida):
    
    coluna_tempo = 'time'

    ex1 = 'Fortnite 2P (LERIS)'
    ex2 = 'Fortnite 2P (FACENS 5G)'

    if (medida == 'Milliseconds'):
        df1[coluna] = df1[coluna] / 1000
        df2[coluna] = df2[coluna] / 1000
    
    max_df1 = df1[coluna].max()
    max_df2 = df2[coluna].max()
    max1 = max(max_df1, max_df2)
    media_df1 = df1[coluna].mean()
    media_df2 = df2[coluna].mean()
    desvio_df1 = np.std(df1[coluna])
    desvio_df2 = np.std(df2[coluna])


    plt.figure(figsize=(15, 8))
    plt.plot(df1[coluna_tempo], df1[coluna], label=f'{ex1}')
    plt.plot(df2[coluna_tempo], df2[coluna], label=f'{ex2}')

    plt.axhline(media_df1, color='b', linestyle='--', label=f'Average {ex1}: {media_df1:.2f}', alpha=0.7)
    plt.axhline(media_df2, color='r', linestyle='--', label=f'Average {ex2}: {media_df2:.2f}', alpha=0.7) 

    plt.text(10, max1, f'Std Dev {ex1}: {desvio_df1:.2f}', color='b')
    plt.text(900, max1, f'Std Dev {ex2}: {desvio_df2:.2f}', color='r')


    # Adiciona rótulos e título
    plt.xlabel("Time")
    plt.ylabel(medida)
    plt.title(f"{coluna} - Comparison between {ex1} and {ex2}")
    
    # Adiciona a legenda
    plt.legend(loc='upper right')

    # Exibe o gráfico
    plt.show()



def main():

    if len(sys.argv) == 2:
        df = pd.read_csv(f'INT_data/{sys.argv[1]}.csv')
        compare1Ex(df, 'downlink deq_qdepth', 'uplink deq_qdepth', 'Packets')
        compare1Ex(df, 'downlink enq_qdepth', 'uplink enq_qdepth', 'Packets')
        compare1Ex(df, 'downlink deq_timedelta', 'uplink deq_timedelta', 'Milliseconds')
    elif len(sys.argv) == 3:
        df1 = pd.read_csv(f'INT_data/{sys.argv[1]}.csv')
        df2 = pd.read_csv(f'INT_tests/{sys.argv[2]}.csv')
        compare2Ex(df1, df2, 'downlink deq_qdepth', 'Packets')
        compare2Ex(df1, df2, 'downlink enq_qdepth', 'Packets')
        compare2Ex(df1, df2, 'uplink enq_qdepth', 'Packets')
        compare2Ex(df1, df2, 'downlink deq_timedelta', 'Milliseconds')
        compare2Ex(df1, df2, 'uplink deq_timedelta', 'Milliseconds')
    else:
        print("Espera-se 1 ou 2 argumentos: ID(s) do(s) experimento(s)...")

    
main()