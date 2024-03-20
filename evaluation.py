import pandas as pd
import matplotlib.pyplot as plt
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
    plt.figure(figsize=(10, 6))
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

    if (medida == 'Milliseconds'):
        df1[coluna] = df1[coluna] / 1000
        df2[coluna] = df2[coluna] / 1000

    #Infos relevantes
    print(f"{sys.argv[1]} - Average {medida} of {coluna}: {df1[coluna].mean():.2f}")
    print(f"{sys.argv[2]} - Average {medida} of {coluna}: {df2[coluna].mean():.2f}")

    print(f"{sys.argv[1]} - Maximum value of {medida} in {coluna}: {df1[coluna].max():.2f}")
    print(f"{sys.argv[2]} - Maximum value of {medida} in {coluna}: {df2[coluna].max():.2f}")

    print(f"{sys.argv[1]} - Minimum value of {medida} in {coluna}: {df1[coluna].min():.2f}")
    print(f"{sys.argv[2]} - Minimum value of {medida} in {coluna}: {df2[coluna].min():.2f}")

    print()

    plt.figure(figsize=(10, 6))
    plt.plot(df1[coluna_tempo].iloc[2:740], df1[coluna].iloc[2:740], label=f'{sys.argv[1]} - {coluna}')
    plt.plot(df2[coluna_tempo].iloc[2:740], df2[coluna].iloc[2:740], label=f'{sys.argv[2]} - {coluna}')

    # Adiciona rótulos e título
    plt.xlabel("Time")
    plt.ylabel(medida)
    plt.title(f"{coluna} - Comparison between {sys.argv[1]} and {sys.argv[2]}")
    
    # Adiciona a legenda
    plt.legend()

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
        df2 = pd.read_csv(f'INT_data/{sys.argv[2]}.csv')
        compare2Ex(df1, df2, 'downlink enq_qdepth', 'Packets')
        compare2Ex(df1, df2, 'uplink enq_qdepth', 'Packets')
        compare2Ex(df1, df2, 'downlink deq_timedelta', 'Milliseconds')
        compare2Ex(df1, df2, 'uplink deq_timedelta', 'Milliseconds')
    else:
        print("Espera-se 1 ou 2 argumentos: ID(s) do(s) experimento(s)...")

    
main()