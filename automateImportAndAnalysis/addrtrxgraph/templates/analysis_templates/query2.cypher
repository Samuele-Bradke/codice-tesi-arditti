LOAD CSV WITH HEADERS FROM 'file:///randomAddresses_chunk_x.txt' AS line
MATCH (a:Address {addressId: toInteger(line.randomAddress)})
MATCH (a)-[:INPUT]->(:Transaction)-[:OUTPUT]->(dst:Address)
WHERE a.addressId <> dst.addressId
RETURN a.addressId AS srcAddressId, COUNT(DISTINCT dst) AS EgoNetworkSize