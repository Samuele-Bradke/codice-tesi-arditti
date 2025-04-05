from neo4j import GraphDatabase
import csv

# URI examples: "neo4j://localhost", "neo4j+s://xxx.databases.neo4j.io"
URI = "neo4j://localhost:7687"
AUTH = ("neo4j", "k*e%TZ2er4dBb^LV!B&o")

file = "example.csv"

# Individual queries
CREATE_TRANSACTIONS_QUERY = """
WITH $infos AS infos, $inputs AS inputs, $outputs AS outputs
MERGE (t:Transaction {txId: infos[2]})
SET t.timestamp = toInteger(infos[0]),
    t.blockId = toInteger(infos[1]),
    t.isCoinbase = infos[3] = '1',
    t.fee = toInteger(infos[4])
RETURN t, inputs, outputs
"""

CREATE_OUTPUTS_QUERY = """
MATCH (t:Transaction {txId: $txId})
WITH t, $outputs AS outputs
UNWIND range(0, size(outputs) - 1) AS outputIndex
WITH t, split(outputs[outputIndex], ',') AS output, outputIndex
MERGE (a:Address {addressId: output[0]})
CREATE (t)-[:OUTPUT {amount: toInteger(output[1]), position: outputIndex}]->(a)
"""

CREATE_INPUTS_QUERY = """
MATCH (t:Transaction {txId: $txId})
WITH t, $inputs AS inputs
UNWIND inputs AS inputString
WITH t, split(inputString, ',') AS input
MERGE (a:Address {addressId: input[0]})
CREATE (a)-[:INPUT {amount: toInteger(input[1]), prevTxId: input[2], prevTxPos: toInteger(input[3])}]->(t)
"""

CHECK_TRANSACTION_EXISTS_QUERY = """
MATCH (t:Transaction {txId: $txId})
RETURN t IS NOT NULL AS exists
"""

def process_csv(file_path):
    with open(file_path, mode='r') as csv_file:
        reader = csv.reader(csv_file, delimiter=':')
        for row in reader:
            yield row

with GraphDatabase.driver(URI, auth=AUTH) as driver:
    driver.verify_connectivity()
    print("Connected to Neo4j database.")

    # Execute the queries sequentially
    with driver.session() as session:
        for row in process_csv(file):
            line = row
            infos = line[0].split(',')
            inputs = line[1].split(';') if line[1] else []
            outputs = line[2].split(';')

            # Check if the transaction already exists
            tx_id = infos[2]
            exists_result = session.run(CHECK_TRANSACTION_EXISTS_QUERY, txId=tx_id)
            if exists_result.single():
                print(f"Transaction {tx_id} already exists. Skipping...")
                continue

            # Create transactions
            result = session.run(CREATE_TRANSACTIONS_QUERY, infos=infos, inputs=inputs, outputs=outputs)
            for tx in result:
                tx_id = tx["t"]["txId"]  # Extract the txId property

                # Create outputs
                session.run(CREATE_OUTPUTS_QUERY, txId=tx_id, outputs=outputs)

                # Create inputs
                session.run(CREATE_INPUTS_QUERY, txId=tx_id, inputs=inputs)

    print("All queries executed successfully.")