CALL apoc.periodic.iterate(
  "LOAD CSV FROM '{{CSV_PATH}}' AS line FIELDTERMINATOR ':' RETURN line",
  "WITH line, 
       split(line[0], ',') AS infos, 
       [i IN (CASE WHEN line[1] IS NOT NULL THEN split(line[1], ';') ELSE [] END) | split(i, ',')] AS inputs, 
       split(line[2], ';') AS outputs
   UNWIND range(0, size(outputs) - 1) AS outputIndex
   WITH outputs[outputIndex] AS outputString, outputIndex, inputs, infos
   WITH split(outputString, ',') AS output, outputIndex, inputs, infos
   CREATE (txo:TXO { 
      txId: toInteger(infos[2]), 
      timestamp: toInteger(infos[0]), 
      isCoinbase: infos[3] = '1', 
      addressId: toInteger(output[0]), 
      amount: toInteger(output[1]), 
      position: outputIndex,
      blockId: toInteger(infos[1])
   })
   WITH txo, inputs, infos
   UNWIND inputs AS input
   MATCH (txo_in:TXO {txId: toInteger(input[2]), position: toInteger(input[3])})
   CREATE (txo_in)-[:CONTRIBUTES]->(txo)",
  {batchSize: 10000, batchMode: "BATCH"}
)