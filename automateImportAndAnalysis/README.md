# Informazioni

In questa directory sono presenti i file che consentono di poter automatizzare l'importazione e l'analisi in Neo4j dei chunk di dati della blockchain Bitcoin ottenuti con l'approccio descritto nella directory `generateDataset`.

In particolare, questa directory contiene 3 sotto-cartelle:

1. `addrtrxgraph`
2. `paymentgraph`
3. `addrvalaggr`

Ognuna di queste cartelle contiene uno script bash che consente di automatizzare la creazione e l'analisi di un grafo specifico in Neo4j, rispettivamente:

1. Address-transaction graph
2. Payment graph
3. Address graph con valori aggregati

Ciascuna delle 3 directory presenta la stessa struttura, con i seguenti file:

* `processing_<nome_rappresentazione>.sh`: script bash che consente di automatizzare l'importazione e l'analisi in Neo4j dei chunk di dati della blockchain Bitcoin per la rappresentazione specificata (sostituire `<nome_rappresentazione>` con `addrtrx`, `payment`, o `addrvalaggr`). Lo script: 
    
    * prende opzionalmente due input che indicano l'intervallo di chunk di dati che si vuole sottoporre ad importazione e analisi in Neo4j. Se nessun input è specificato, lo script importa e analizza tutti i chunk di dati presenti nella directory `$NEO4J_HOME/import/chunks` (che deve essere creata e popolata con i risultati dello script `indexAnalyzer.sh` presente nella directory `generateDataset`)
    
    * crea, per ciascun chunk importato e analizzato, una directory `chunk_${file_counter}_blockId_${last_block_id}` all'interno della directory `chunk_results` (a sua volta contenuta nella directory della rappresentazione specifica `<nome_rappresentazione>`). Questa directory creata contiene: 
    
        - risultati dell'importazione del chunk (`risultati_import_chunk_${file_counter}_blockId_${last_block_id}.txt`) con il tempo impiegato per l'importazione, il numero di nodi e relazioni creati, etc.

        - la memoria totale occupata del database dopo l'importazione del chunk (`memoriaTotaleDB_finoA_${file_counter}_blockId_${last_block_id}.txt`)

        - i risultati delle query di analisi eseguite sul database usando gli $n$ indirizzi scelti casualmente (vedi punto successivo) nell'intero grafo costruito fino all'ultimo chunk importato. I risultati sono memorizzati ciascuno in un file distinto `${analysis_basename}_up_to_chunk_${file_counter}_blockId_${last_block_id}.txt` con `$analysis_basename` che può essere `query1a`, `query1b` o `query2` a seconda della query di analisi eseguita

    
    * salva, solo nel caso di `processing_addrtrx.sh`, gli $n$ indirizzi scelti casualmente nell'intero grafo costruito fino all'ultimo chunk importato in un file `randomAddresses_up_to_chunk_${file_counter}_blockId_${last_block_id}.txt` all'interno della directory `$NEO4J_HOME/import/`. Questi indirizzi saranno poi utilizzati per eseguire le query di analisi presenti nella directory `analysis_templates` di ciascuna rappresentazione

* `templates`: directory contenente:

    - `<nome_rappresentazione>.cypher`: template della query Cypher che verrà modificato dinamicamente dallo script bash di ciascuna rappresentazione (`processing_addrtrx.sh`, `processing_payment.sh` e `processing_addrvalaggr.sh` rispettivamente)
    sostituendo il placeholder `{{CSV_PATH}}` con il path a un chunk specifico di dati della blockchain Bitcoin in `$NEO4J_HOME/import/chunks` 

    - solo nel caso della rappresentazione `addrtrx`, il template Cypher `selectRandomAddresses.cypher` con il placeholder `randomAddresses_chunk_x.txt` che verrà sostituito con `randomAddresses_up_to_chunk_{file_counter}_blockId_{last_block_id}.txt` per il salvataggio in `$NEO4J_HOME/import/` degli $n$ indirizzi scelti casualmente nell'intero grafo costruito

    - `analysis_templates`: directory contenente le query Cypher `query1a.cypher`, `query1b.cypher` e `query2.cypher` che vengono eseguite su Neo4j considerando gli $n$ indirizzi scelti casualmente nell'intero grafo costruito fino a quel chunk e memorizzati in `$NEO4J_HOME/import/` come `randomAddresses_up_to_chunk_${file_counter}_blockId_${last_block_id}.txt`. Queste query vengono eseguite per ogni chunk importato e i risultati sono salvati in un file all'interno della directory `chunk_results`, creata automaticamente dallo script bash di ciascuna rappresentazione nella directory `<nome_rappresentazione>`. Il placeholder `file:///randomAddresses_chunk_x.txt` dentro le query di analisi viene sostituito dinamicamente con il nome del file contenente gli $n$ indirizzi scelti casualmente da considerare per l'analisi