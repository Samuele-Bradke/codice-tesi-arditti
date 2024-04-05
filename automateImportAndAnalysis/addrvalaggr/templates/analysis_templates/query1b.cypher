LOAD CSV WITH HEADERS FROM 'file:///randomAddresses_chunk_x.txt' AS line
MATCH (:Address)-[r:TRANSFERS_TO]->(dst:Address {addressId: toInteger(line.randomAddress)})
RETURN dst.addressId AS dstAddressId, MIN(r.firstTimestamp) AS FirstTransactionTimestamp