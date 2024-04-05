#!/bin/bash

inputFile="updateMe.txt" # File di input da processare, sostituire con il proprio file
indexFile="chunk_index.txt"  # File indice generato precedentemente in generateDataIndexes.sh
outputDir="$NEO4J_HOME/import/chunks" # Directory dove salvare i chunk (creata se non esiste) 
# NB: viene usata la directory import di Neo4j in modo che le operazioni di lettura con LOAD CSV non richiedano permessi aggiuntivi per la lettura da directory diverse 

# Crea la directory di output se non esiste
mkdir -p "$outputDir"

# Leggi il file indice e processa ciascuna riga
while IFS=' ' read -r fileCounter startLine endLine startBlock endBlock; do
    chunkName="${outputDir}/file_${fileCounter}_chunk_${startBlock}_${endBlock}.txt"
    
    # Usa sed per estrarre le righe specificate dall'indice e salvale nel chunk corrispondente
    sed -n "${startLine},${endLine}p" "$inputFile" > "$chunkName"
    
    echo "Creato chunk: $chunkName"
done < "$indexFile"