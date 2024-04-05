CALL apoc.periodic.iterate(
  "LOAD CSV FROM '{{CSV_PATH}}' AS line FIELDTERMINATOR ':' RETURN line",
  "WITH line, 
       split(line[0], ',') AS infos, 
       (CASE WHEN line[1] IS NOT NULL THEN split(line[1], ';') ELSE [] END) AS inputs, // per gestire le transazioni coinbase
       split(line[2], ';') AS outputs
   CREATE (t:Transaction {txId: toInteger(infos[2])})
   SET t.timestamp = toInteger(infos[0]), 
       t.blockId = toInteger(infos[1]),
       t.isCoinbase = infos[3] = '1',
       t.fee = toInteger(infos[4])
   WITH t, inputs, outputs
   // Gestione degli output
   CALL {
       WITH t, outputs
       UNWIND range(0, size(outputs) - 1) AS outputIndex
       WITH t, split(outputs[outputIndex], ',') AS output, outputIndex
       MERGE (a:Address {addressId: toInteger(output[0])})
       CREATE (t)-[:OUTPUT {amount: toInteger(output[1]), position: outputIndex}]->(a)
   }
   // Gestione degli input
   CALL {
       WITH t, inputs
       UNWIND inputs AS inputString
       WITH t, split(inputString, ',') AS input
       MERGE (a:Address {addressId: toInteger(input[0])})
       CREATE (a)-[:INPUT {amount: toInteger(input[1]), prevTxId: toInteger(input[2]), prevTxPos: toInteger(input[3])}]->(t)
   }",
  {batchSize: 10000, batchMode: "BATCH"}
)