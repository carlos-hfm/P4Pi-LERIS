import os



diretorio = 'pcap_features'

for filename in os.listdir(diretorio):
    original_path = os.path.join(diretorio, filename)
    #print("encontrou arquivo " + original_path)

    if os.path.isfile(original_path):
        
        if ".pcap.csv" in filename:
            new_filename = filename.replace(".pcap.csv", "")
        else:
            new_filename = filename

        if new_filename != filename:
            new_path = os.path.join(diretorio, new_filename)
            os.rename(original_path, new_path)
            print(f"renomeado: {filename} para {new_filename}")