LOAD CSV WITH HEADERS FROM 'file:///randomAddresses_chunk_x.txt' AS line
MATCH (startTXO:TXO {addressId: toInteger(line.randomAddress)})
OPTIONAL MATCH (startTXO)-[:CONTRIBUTES]->(endTXO:TXO)
WHERE startTXO.addressId <> endTXO.addressId
RETURN startTXO.addressId AS srcAddressId, COUNT(DISTINCT endTXO.addressId) AS EgoNetworkSize