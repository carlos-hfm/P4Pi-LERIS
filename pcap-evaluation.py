import pyshark

def averagePacketSize(arquivo_pcap):
    cap = pyshark.FileCapture(arquivo_pcap)
    total_pacotes = 0
    tamanho_total = 0
    
    for pacote in cap:
        tamanho_total += int(pacote.length)
        total_pacotes += 1

    if total_pacotes > 0:
        tamanho_medio = tamanho_total / total_pacotes
        print(f"Tamanho médio dos pacotes: {tamanho_medio} bytes")
    else:
        print("Nenhum pacote encontrado.")
    
    cap.close()

# Substitua 'seu_arquivo.pcap' pelo caminho do seu arquivo
averagePacketSize('Captures/ex34.pcap')
