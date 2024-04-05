LOAD CSV WITH HEADERS FROM 'file:///randomAddresses_chunk_x.txt' AS line
MATCH (src:Address {addressId: toInteger(line.randomAddress)})
OPTIONAL MATCH (src)-[:TRANSFERS_TO]->(dst:Address)
WHERE src.addressId <> dst.addressId
RETURN src.addressId AS srcAddressId, COUNT(dst) AS EgoNetworkSize