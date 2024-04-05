#!/bin/bash

inputFile="example.txt" # File di input da processare, sostituire con il proprio file
indexFile="chunk_index.txt"  # File dove salvare gli indici dei chunk
chunkSize=25920  # Numero di blockId per 6 mesi (= ipotizzando 6 blocchi/ora * 24 ore * 30 giorni * 6 mesi) 

# Resetta il file indice se già esiste
> "$indexFile"

# Processa il file di input per calcolare gli intervalli di blockId per ciascun chunk
awk -v chunkSize="$chunkSize" -v indexFile="$indexFile" -F, '
BEGIN { 
    startBlock = ""; 
    endBlock = ""; 
    startLine = 1; 
    file_counter = 1; 
}
{
    if (startBlock == "") {
        startBlock = $2;
        endBlock = startBlock + chunkSize - 1;
    }
    if ($2 > endBlock) {
        print file_counter " " startLine " " NR-1 " " startBlock " " endBlock >> indexFile;
		print "Chunk " file_counter ": Linee " startLine " - " NR-1 " per blockId " startBlock " - " endBlock > "/dev/stderr";
        startLine = NR;
        startBlock = $2;
        endBlock = startBlock + chunkSize - 1;
        file_counter++;
    }
}
END {
	
    print file_counter " " startLine " " NR " " startBlock " " $2 >> indexFile;
}' "$inputFile"

echo "File indice creato: $indexFile"