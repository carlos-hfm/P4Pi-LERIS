import pandas as pd
import matplotlib.pyplot as plt

# Função para ler o arquivo CSV e criar o gráfico
def plotar_grafico(nome_arquivo, coluna_tempo, coluna1, coluna2, medida):
    # Lê o arquivo CSV usando o pandas
    df = pd.read_csv(nome_arquivo)

    #print(df.columns)

    #Infos relevantes
    print(f"Média de {medida} do {coluna1}: {df[coluna1].mean():.2f}")
    print(f"Média de {medida} do {coluna2}: {df[coluna2].mean():.2f}")

    print(f"Maior valor de {medida} do {coluna1}: {df[coluna1].max():.2f}")
    print(f"Maior valor de {medida} do {coluna2}: {df[coluna2].max():.2f}")

    print(f"Menor valor de {medida} do {coluna1}: {df[coluna1].min():.2f}")
    print(f"Menor valor de {medida} do {coluna2}: {df[coluna2].min():.2f}")

    print("\n")

    # Cria o gráfico
    plt.figure(figsize=(10, 6))
    plt.plot(df[coluna_tempo], df[coluna1], label=coluna1)
    plt.plot(df[coluna_tempo], df[coluna2], label=coluna2)

    # Adiciona rótulos e título
    plt.xlabel(coluna_tempo)
    plt.ylabel(medida)
    plt.title(f"Comparação entre {coluna1} e {coluna2}")
    
    # Adiciona a legenda
    plt.legend()

    # Exibe o gráfico
    plt.show()

# Substitua 'seu_arquivo.csv', 'coluna_tempo', 'coluna1' e 'coluna2' pelos nomes reais do seu arquivo e colunas.
plotar_grafico('../CG_data/Ex3.csv', 'time', 'downlink deq_qdepth', 'uplink deq_qdepth', 'Pacotes')
plotar_grafico('../CG_data/Ex3.csv', 'time', 'downlink enq_qdepth', 'uplink enq_qdepth', 'Pacotes')
plotar_grafico('../CG_data/Ex3.csv', 'time', 'downlink deq_timedelta', 'uplink deq_timedelta', 'Microsegundos')