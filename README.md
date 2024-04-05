# Informazioni

In questa repository sono presenti gli script di supporto alla tesi triennale in informatica @ UniPi "Modellazione a grafo dei dati Blockchain: rappresentazione e analisi della rete Bitcoin nel graph database Neo4j".  

Questi script hanno consentito di:

1. Dividere il dataset originale di transazioni Bitcoin in chunk contenti blocchi corrispondenti a 6 mesi di scambi di valore

2.  Automatizzare l'importazione e l'analisi dei chunk di dati della blockchain Bitcoin in Neo4j, registrando per ogni chunk importato:
    - statistiche su tempi impiegati, nodi, relazioni e proprietà introdotte/eliminate/aggiornate
    - l'evoluzione della dimensione del database sul disco  
    - i tempi di esecuzione delle query di analisi considerando $n$ indirizzi scelti casualmente nel database costruito fino all'ultimo chunk importato

## Struttura

Le cartelle presenti in questa repository che consentono di eseguire i task sopra descritti sono:

1. `generateDataset`, contenente:
    - `generateDataIndexes.sh`: script per individuare le righe del dataset originale da considerare per ogni singolo chunk della blockchain
    - `indexAnalyzer.sh`: script per analizzare i risultati ottenuti dallo script precedente e dividere il dataset originale in chunk
    - vedere il file [README.md](./generateDataset/README.md) per ulteriori dettagli

2. `automateImportAndAnalysis`: contiene 3 sotto-cartelle:
    - `addrtrxgraph` che contiene lo script `processing_addrtrx.sh` per automatizzare la creazione e analisi dell'Address-transaction graph in Neo4j
        - **NB**: la scelta degli indirizzi casuali viene fatta in questa rappresentazione della blockchain come grafo, gli indirizzi scelti sono indirizzi coinvolti come input in almeno una transazione. Questi indirizzi sono poi utilizzati per le analisi di tutte le rappresentazioni della blockchain come grafo
    - `paymentgraph` che contiene lo script `processing_payment.sh` per automatizzare la creazione e analisi del Payment graph in Neo4j 
    - `addrvalaggr` che contiene lo script `processing_addrvalaggr.sh` per automatizzare la creazione e analisi dell'Address graph con valori aggregati in Neo4j
    - vedere il file [README.md](./automateImportAndAnalysis/README.md) per ulteriori dettagli