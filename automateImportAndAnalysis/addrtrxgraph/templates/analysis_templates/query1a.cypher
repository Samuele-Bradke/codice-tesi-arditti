LOAD CSV WITH HEADERS FROM 'file:///randomAddresses_chunk_x.txt' AS line
MATCH (a:Address {addressId: toInteger(line.randomAddress)})-[:INPUT]->(t:Transaction)
RETURN a.addressId AS srcAddressId, MIN(t.timestamp) AS FirstTransactionTimestamp