LOAD CSV WITH HEADERS FROM 'file:///randomAddresses_chunk_x.txt' AS line
MATCH (endTXO:TXO {addressId: toInteger(line.randomAddress)})
RETURN endTXO.addressId AS dstAddressId, MIN(endTXO.timestamp) AS FirstTransactionTimestamp