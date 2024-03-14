import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


# Função para ler o arquivo CSV e criar o gráfico
def compare1Ex(ex, coluna1, coluna2, medida):

    coluna_tempo = 'time'

    df = pd.read_csv(f'INT_data/{ex}.csv')

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

    print(f"Standard deviation of {coluna1}: {np.std(df[coluna1])}")
    print(f"Standard deviation of {coluna2}: {np.std(df[coluna1])}")

    print()

    # Cria o gráfico
    plt.figure(figsize=(10, 6))
    plt.plot(df[coluna_tempo], df[coluna1], label=coluna1)
    plt.plot(df[coluna_tempo], df[coluna2], label=coluna2)

    # Adiciona rótulos e título
    plt.xlabel("Time")
    plt.ylabel(medida)
    plt.title(f"{ex} - Comparison between {coluna1} and {coluna2}")
    
    # Adiciona a legenda
    plt.legend()

    # Exibe o gráfico
    plt.show()


def compare2Ex(ex1, ex2, coluna, medida):
    
    coluna_tempo = 'time'

    df1 = pd.read_csv(f'INT_data/{ex1}.csv')
    df2 = pd.read_csv(f'INT_data/{ex2}.csv')

    if (medida == 'Milliseconds'):
        df1[coluna] = df1[coluna] / 1000
        df2[coluna] = df2[coluna] / 1000

    #Infos relevantes
    print(f"{ex1} - Average {medida} of {coluna}: {df1[coluna].mean():.2f}")
    print(f"{ex2} - Average {medida} of {coluna}: {df2[coluna].mean():.2f}")

    print(f"{ex1} - Maximum value in {medida} of {coluna}: {df1[coluna].max():.2f}")
    print(f"{ex2} - Maximum value in {medida} of {coluna}: {df2[coluna].max():.2f}")

    print(f"{ex1} - Minimum value in {medida} of {coluna}: {df1[coluna].min():.2f}")
    print(f"{ex2} - Minimum value in {medida} of {coluna}: {df2[coluna].min():.2f}")

    print(f"{ex1} - Standard deviation of {coluna}: {np.std(df1[coluna])}")
    print(f"{ex2} - Standard deviation of {coluna}: {np.std(df2[coluna])}")

    print()

    plt.figure(figsize=(10, 6))
    plt.plot(df1[coluna_tempo].iloc[2:740], df1[coluna].iloc[2:740], label=f'{ex1} - {coluna}')
    plt.plot(df2[coluna_tempo].iloc[2:740], df2[coluna].iloc[2:740], label=f'{ex2} - {coluna}')

    # Adiciona rótulos e título
    plt.xlabel("Time")
    plt.ylabel(medida)
    plt.title(f"{coluna} - Comparison between {ex1} and {ex2}")
    
    # Adiciona a legenda
    plt.legend()

    # Exibe o gráfico
    plt.show()


def compare1Game(game, coluna, medida):

    coluna_tempo = 'time'

    df1 = pd.read_csv(f'INT_data/{game} - Ex1.csv') 
    df2 = pd.read_csv(f'INT_data/{game} - Ex2.csv')
    df3 = pd.read_csv(f'INT_data/{game} - Ex3.csv') 

    if (medida == 'Milliseconds'):
        df1[coluna] = df1[coluna] / 1000
        df2[coluna] = df2[coluna] / 1000
        df3[coluna] = df3[coluna] / 1000
    

    dataframes = [df1, df2, df3]
    df = pd.concat(dataframes)
    soma = sum(df[coluna])
    lenght = len(df)
    maxValor = max(df[coluna])
    media_total = soma / lenght
    desvio = np.std(df[coluna])

    print(f"{game} - Total Average {medida} of {coluna}: {media_total:.2f}")
    print(f"{game} - Maximium Value in {medida} of {coluna}: {maxValor}")
    print(f"{game} - Standard deviation of {coluna}: {desvio:.2f}")

    
    plt.figure(figsize=(10, 6))
    plt.plot(df1[coluna_tempo].iloc[2:800], df1[coluna].iloc[2:800], label=f'Ex1')
    plt.plot(df2[coluna_tempo].iloc[2:800], df2[coluna].iloc[2:800], label=f'Ex2')
    plt.plot(df3[coluna_tempo].iloc[2:800], df3[coluna].iloc[2:800], label=f'Ex3')

    # Adiciona rótulos e título
    plt.xlabel("Time")
    plt.ylabel(medida)
    plt.title(f"{coluna} - {game} Comparison")
    plt.legend()

    plt.show()

def compare2Game(coluna, medida):
    game1 = 'Forza'
    game2 = 'Forza 2P'

    forza1 = pd.read_csv(f'INT_data/{game1} - Ex1.csv')
    forza2 = pd.read_csv(f'INT_data/{game1} - Ex2.csv')
    forza3 = pd.read_csv(f'INT_data/{game1} - Ex3.csv')
    forzaP1 = pd.read_csv(f'INT_data/{game2} - Ex1.csv') 
    forzaP2 = pd.read_csv(f'INT_data/{game2} - Ex2.csv') 
    forzaP3 = pd.read_csv(f'INT_data/{game2} - Ex3.csv') 

    forza = pd.concat([forza1, forza2, forza3])
    forzaP = pd.concat([forzaP1, forzaP2, forzaP3])

    medias = [forza[coluna].mean(), forzaP[coluna].mean()]
    desvios = [np.std(forza[coluna]), np.std(forzaP[coluna])]

    fig, ax = plt.subplots()
    games = ['Forza 1 Player', 'Forza 2 Player']
    bar_colors = ['tab:blue', 'tab:red']
    ax.bar(games, medias, color=bar_colors)
    ax.set_ylabel(medida)
    ax.set_title(f'Average {coluna} game comparison')
    plt.show()

    fig, ax = plt.subplots()
    games = ['Forza 1 Player', 'Forza 2 Player']
    bar_colors = ['tab:blue', 'tab:red']
    ax.bar(games, desvios, color=bar_colors)
    ax.set_ylabel(medida)
    ax.set_title(f'Standard deviation {coluna} game comparison')
    plt.show()



def compare3Games(coluna, medida):
    game1 = 'Forza'
    game2 = 'Fortnite'
    game3 = 'Mortal Kombat'

    forza1 = pd.read_csv(f'INT_data/{game1} - Ex1.csv') 
    forza2 = pd.read_csv(f'INT_data/{game1} - Ex2.csv')
    forza3 = pd.read_csv(f'INT_data/{game1} - Ex3.csv')

    fortnite1 = pd.read_csv(f'INT_data/{game2} - Ex1.csv') 
    fortnite2 = pd.read_csv(f'INT_data/{game2} - Ex2.csv')
    fortnite3 = pd.read_csv(f'INT_data/{game2} - Ex3.csv')

    mortal1 = pd.read_csv(f'INT_data/{game3} - Ex1.csv') 
    mortal2 = pd.read_csv(f'INT_data/{game3} - Ex2.csv')
    mortal3 = pd.read_csv(f'INT_data/{game3} - Ex3.csv')

    forza = pd.concat([forza1, forza2, forza3])
    fortnite = pd.concat([fortnite1, fortnite2, fortnite3])
    mortal = pd.concat([mortal1, mortal2])

    medias = [forza[coluna].mean(), fortnite[coluna].mean(), mortal[coluna].mean()]
    desvios = [np.std(forza[coluna]), np.std(fortnite[coluna]), np.std(mortal[coluna])]


    fig, ax = plt.subplots()
    games = ['Forza Horizon 5', 'Fortnite (Zero Build)', 'Mortal Kombat 11']
    bar_colors = ['tab:blue', 'tab:red', 'tab:orange']
    ax.bar(games, medias, color=bar_colors)
    ax.set_ylabel(medida)
    ax.set_title(f'Average {coluna} game comparison')
    plt.show()

    fig, ax = plt.subplots()
    games = ['Forza Horizon 5', 'Fortnite (Zero Build)', 'Mortal Kombat 11']
    bar_colors = ['tab:blue', 'tab:red', 'tab:orange']
    ax.bar(games, desvios, color=bar_colors)
    ax.set_ylabel(medida)
    ax.set_title(f'Standard deviation {coluna} game comparison')
    plt.show()

    fig, ax = plt.subplots()
    games = ['Forza - Ex1',
             'Forza - Ex2', 
             'Forza - Ex3', 
             'Fortnite - Ex1', 
             'Fortnite - Ex2', 
             'Fortnite - Ex3', 
             'Mortal Kombat - Ex1', 
             'Mortal Kombat - Ex2', 
             'Mortal Kombat - Ex3']
    medias2 = [forza1[coluna].mean(), 
               forza2[coluna].mean(),
               forza3[coluna].mean(), 
               fortnite1[coluna].mean(), 
               fortnite2[coluna].mean(), 
               fortnite3[coluna].mean(), 
               mortal1[coluna].mean(), 
               mortal2[coluna].mean(), 
               mortal3[coluna].mean()]
    
    bar_colors = ['tab:blue', 'tab:blue', 'tab:blue', 'tab:red', 'tab:red', 'tab:red', 'tab:orange', 'tab:orange', 'tab:orange']
    ax.bar(games, medias2, color=bar_colors)
    ax.set_ylabel(medida)
    ax.set_title(f'Average {coluna} game comparison')
    plt.show()


def graficoDispersao(ex):
    df = pd.read_csv(f'INT_data/{ex}.csv')

    plt.figure(figsize=(8, 6))
    plt.scatter(df['downlink deq_qdepth'], df['downlink deq_timedelta']/ 1000, color='blue', alpha=0.5)
    plt.title('Scatter: downlink deq_qdepth vs deq_timedelta')
    plt.xlabel('downlink deq_qdepth')
    plt.ylabel('deq_timedelta')
    plt.grid(True)
    plt.show()



def main():

    # Forza
    ex = 'Forza - Ex1'
    #compare1Ex(ex, 'downlink deq_qdepth', 'uplink deq_qdepth', 'Packets')
    #compare1Ex(ex, 'downlink enq_qdepth', 'uplink enq_qdepth', 'Packets')
    #compare1Ex(ex, 'downlink deq_timedelta', 'uplink deq_timedelta', 'Milliseconds')


    #compare1Game('Forza', 'downlink deq_qdepth', 'Packets')
    #compare1Game('Fortnite', 'downlink deq_qdepth', 'Packets')
    #compare1Game('Mortal Kombat', 'downlink deq_qdepth', 'Packets')
    #compare1Game('Forza 2P', 'downlink deq_qdepth', 'Packets')

    #Compara forza 1 e 2 player
    #compare2Ex('Forza - Ex2', 'Forza 2P - Ex1', 'uplink deq_qdepth', 'Packets')

    #compare2Game('uplink deq_qdepth', 'Packets')

    compare3Games('downlink deq_qdepth', 'Packets')

    #graficoDispersao('Forza - Ex1')

main()