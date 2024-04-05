LOAD CSV WITH HEADERS FROM 'file:///randomAddresses_chunk_x.txt' AS line
MATCH (src:Address {addressId: toInteger(line.randomAddress)})-[r:TRANSFERS_TO]->(:Address)
RETURN src.addressId AS srcAddressId, MIN(r.firstTimestamp) AS FirstTransactionTimestamp