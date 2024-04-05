LOAD CSV WITH HEADERS FROM 'file:///randomAddresses_chunk_x.txt' AS line
MATCH (startTXO:TXO {addressId: toInteger(line.randomAddress)})-[:CONTRIBUTES]->(endTXO:TXO)
RETURN startTXO.addressId AS srcAddressId, MIN(endTXO.timestamp) AS FirstTransactionTimestamp