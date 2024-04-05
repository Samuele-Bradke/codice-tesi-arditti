LOAD CSV WITH HEADERS FROM 'file:///randomAddresses_chunk_x.txt' AS line
MATCH (t:Transaction)-[:OUTPUT]->(a:Address {addressId: toInteger(line.randomAddress)})
RETURN a.addressId AS dstAddressId, MIN(t.timestamp) AS FirstTransactionTimestamp