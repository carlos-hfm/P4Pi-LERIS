import pandas as pd
import matplotlib.pyplot as plt
import sys

# Função para ler o arquivo CSV e criar o gráfico
def compare1Ex(df, coluna1, coluna2, medida):

    coluna_tempo = 'time'

    #Infos relevantes
    print(f"Média de {medida} do {coluna1}: {df[coluna1].mean():.2f}")
    print(f"Média de {medida} do {coluna2}: {df[coluna2].mean():.2f}")

    print(f"Maior valor de {medida} do {coluna1}: {df[coluna1].max():.2f}")
    print(f"Maior valor de {medida} do {coluna2}: {df[coluna2].max():.2f}")

    print(f"Menor valor de {medida} do {coluna1}: {df[coluna1].min():.2f}")
    print(f"Menor valor de {medida} do {coluna2}: {df[coluna2].min():.2f}")

    print()

    # Cria o gráfico
    plt.figure(figsize=(10, 6))
    plt.plot(df[coluna_tempo], df[coluna1], label=coluna1)
    plt.plot(df[coluna_tempo], df[coluna2], label=coluna2)

    # Adiciona rótulos e título
    plt.xlabel("Tempo")
    plt.ylabel(medida)
    plt.title(f"{sys.argv[1]} - Comparação entre {coluna1} e {coluna2}")
    
    # Adiciona a legenda
    plt.legend()

    # Exibe o gráfico
    plt.show()


def compare2Ex(df1, df2, coluna, medida):
    
    coluna_tempo = 'time'

    #Infos relevantes
    print(f"Média de {medida} do {coluna} do {sys.argv[1]}: {df1[coluna].mean():.2f}")
    print(f"Média de {medida} do {coluna} do {sys.argv[2]}: {df2[coluna].mean():.2f}")

    print(f"Valor máximo de {medida} do {coluna} do {sys.argv[1]}: {df1[coluna].max():.2f}")
    print(f"Valor máximo de {medida} do {coluna} do {sys.argv[2]}: {df2[coluna].max():.2f}")

    print(f"Valor mínimo de {medida} do {coluna} do {sys.argv[1]}: {df1[coluna].min():.2f}")
    print(f"Valor mínimo de {medida} do {coluna} do {sys.argv[2]}: {df2[coluna].min():.2f}")

    print()

    plt.figure(figsize=(10, 6))
    plt.plot(df1[coluna_tempo].iloc[2:740], df1[coluna].iloc[2:740], label=f'{sys.argv[1]} - {coluna}')
    plt.plot(df1[coluna_tempo].iloc[2:740], df2[coluna].iloc[2:740], label=f'{sys.argv[2]} - {coluna}')

    # Adiciona rótulos e título
    plt.xlabel("Tempo")
    plt.ylabel(medida)
    plt.title(f"{coluna} - Comparação entre {sys.argv[1]} e {sys.argv[2]}")
    
    # Adiciona a legenda
    plt.legend()

    # Exibe o gráfico
    plt.show()



def main():

    if len(sys.argv) == 2:
        df = pd.read_csv(f'CG_data/{sys.argv[1]}.csv')
        compare1Ex(df, 'downlink deq_qdepth', 'uplink deq_qdepth', 'Pacotes')
        compare1Ex(df, 'downlink enq_qdepth', 'uplink enq_qdepth', 'Pacotes')
        compare1Ex(df, 'downlink deq_timedelta', 'uplink deq_timedelta', 'Microsegundos')
    elif len(sys.argv) == 3:
        df1 = pd.read_csv(f'CG_data/{sys.argv[1]}.csv')
        df2 = pd.read_csv(f'CG_data/{sys.argv[2]}.csv')
        compare2Ex(df1, df2, 'downlink enq_qdepth', 'Pacotes')
        compare2Ex(df1, df2, 'uplink enq_qdepth', 'Pacotes')
        compare2Ex(df1, df2, 'downlink deq_timedelta', 'Microssegundos')
        compare2Ex(df1, df2, 'uplink deq_timedelta', 'Microssegundos')
    else:
        print("Espera-se 1 ou 2 argumentos: ID(s) do(s) experimento(s)...")

    
main()