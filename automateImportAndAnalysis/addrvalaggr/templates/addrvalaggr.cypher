CALL apoc.periodic.iterate(
  "LOAD CSV FROM '{{CSV_PATH}}' AS line FIELDTERMINATOR ':' RETURN line",
  "WITH line,
        split(line[0], ',') AS infos,
        (CASE WHEN line[1] IS NOT NULL THEN split(line[1], ';') ELSE [] END) AS inputs,
        split(line[2], ';') AS outputs
   WITH infos, inputs, outputs, toInteger(infos[2]) AS txId, toInteger(infos[0]) AS currentTimestamp, toInteger(infos[1]) AS blockId,
   // Calcolo la somma totale degli importi degli input una volta per transazione
   REDUCE(s = 0.0, i IN inputs | s + toInteger(split(i, ',')[1])) AS totalInputAmount
   CALL {
       WITH inputs, outputs, totalInputAmount
       UNWIND outputs AS output
       UNWIND inputs AS input
       WITH input, output, totalInputAmount,
            split(input, ',')[0] AS srcAddrId, toInteger(split(input, ',')[1]) AS inputAmount,
            split(output, ',')[0] AS dstAddrId, toInteger(split(output, ',')[1]) AS outputAmount
       MERGE (src:Address {addressId: toInteger(srcAddrId)})
       MERGE (dst:Address {addressId: toInteger(dstAddrId)})
       CREATE (src)-[tempTransfers:TEMP_TRANSFERS {amount: (outputAmount * (inputAmount / totalInputAmount))}]->(dst)
       RETURN src, dst, tempTransfers
       // restituisce ogni possibile coppia di indirizzi sorgente e destinazione insieme a tutti gli archi TEMP_TRANSFERS che li collegano
   }
   WITH src, dst, COLLECT(tempTransfers) AS tempTransfers, txId, currentTimestamp, blockId
   MERGE (src)-[transfers:TRANSFERS_TO]->(dst)
   ON CREATE SET transfers.sum = REDUCE(s = 0.0, t IN tempTransfers | s + t.amount),
   transfers.firstTxId = txId,
   transfers.firstTimestamp = currentTimestamp,
   transfers.firstBlockId = blockId,
   transfers.lastTxId = txId,
   transfers.lastTimestamp = currentTimestamp,
   transfers.lastBlockId = blockId
   ON MATCH SET transfers.sum = transfers.sum + REDUCE(s = 0.0, t IN tempTransfers | s + t.amount),
   // basta un assegnamento per le proprietà con prefisso "last" dato che le transazioni sono ordinate temporalmente in modo crescente
                transfers.lastTimestamp = currentTimestamp,
				transfers.lastTxId = txId,
				transfers.lastBlockId = blockId
   WITH tempTransfers
   UNWIND tempTransfers AS tempTransfer
   DELETE tempTransfer",
  {batchSize: 10000, batchMode: "BATCH"}
)