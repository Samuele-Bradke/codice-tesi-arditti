# Informazioni

In questa directory sono presenti i file che consentono di poter generare a partire da un dataset di transazioni Bitcoin tanti dataset più piccoli, ciascuno contenente le transazioni corrispondenti a intervalli di 6 mesi. Questo è necessario per poter effettuare l'importazione e l'analisi dei dati in Neo4j in maniera incrementale, così da poter registrare l'evoluzione delle dimensioni del grafo e delle prestazioni delle query all'aumentare del numero di chunk di dati importati.

In particolare, i file presenti in questa directory sono:

* `generateDataIndexes.sh`: script bash che specificato un file `inputFile`, contente per ogni riga una transazione Bitcoin nel formato riportato dal capitolo 5 della tesi, genera un file `indexFile` contenente gli intervalli (in termini di righe di `inputFile`) che rappresentano 6 mesi di transazioni Bitcoin. Ciascuna riga del file `indexFile` generato è nel formato:

file_counter startLine endLine startBlock endBlock

e.g.

```
1 1 26085 0 25919
2 26086 56039 25920 51839
...
```
Ovvero: il primo chunk di dati è composto dalle righe 1-26085 del file `inputFile` e rappresenta transazioni che vanno dal blocco 0 al blocco 25919. Il secondo chunk di dati è composto dalle righe 26086-56039 del file `inputFile` e rappresenta transazioni che vanno dal blocco 25920 al blocco 51839. E così via. Se il file `inputFile` presenta un chunk di dati che non copre esattamente 6 mesi di transazioni allora viene considerato come `endBlock` il blocco massimo presente nel chunk (corrispondente al blocco contenuto nell'ultima riga del dataset, dato che i dati sono ordinati temporalmente).

Questo approccio di generazione degli indici (cioè degli intervalli di righe del file `inputFile` da considerare per ciascun chunk) e poi divisione dei dati di `inputFile` in chunks usando `indexAnalyzer.sh` si rivela essere molto più efficiente rispetto a quello di andare a leggere ogni singola riga del file `inputFile`, determinate se il blocco è nell'intervallo corretto e poi scrivere la riga nel file di output. 

* `indexAnalyzer.sh`: script bash che specificato un file `indexFile` contenente gli intervalli (in termini di righe di `inputFile`) che rappresentano 6 mesi di transazioni Bitcoin, copia le righe di `inputFile` corrispondenti a ciascun intervallo nel file `chunkName` dove `chunkName="${outputDir}/file_${fileCounter}_chunk_${startBlock}_${endBlock}.txt"`, ad esempio `chunkName="chunks/file_1_chunk_0_25919.txt"` per le prime 26085 righe del file `inputFile`.