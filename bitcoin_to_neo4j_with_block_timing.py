import time
from neo4j import GraphDatabase
import subprocess
import json
import csv

# Neo4j connection details
URI = "neo4j+s://6ae77e28.databases.neo4j.io"
AUTH = ("neo4j", "xSxHoQTyuj1xth3aSwbseqrl04p7R-uYv_WvwxwEepo")

# CSV file for logging timings
TIMING_CSV_FILE = "block_timing_log.csv"

# Neo4j queries
GET_LAST_BLOCK_QUERY = """
MATCH (t:Transaction)
RETURN max(t.blockId) AS lastBlock
"""

CHECK_TRANSACTION_EXISTS_QUERY = """
MATCH (t:Transaction {txId: $txId})
RETURN t IS NOT NULL AS exists
"""

CREATE_TRANSACTIONS_QUERY = """
WITH $infos AS infos, $inputs AS inputs, $outputs AS outputs
MERGE (t:Transaction {txId: infos[2]})
SET t.timestamp = toInteger(infos[0]),
    t.blockId = toInteger(infos[1]),
    t.isCoinbase = infos[3] = '1',
    t.fee = toInteger(infos[4])
RETURN t
"""

CREATE_OUTPUTS_QUERY = """
MATCH (t:Transaction {txId: $txId})
WITH t, $outputs AS outputs
UNWIND range(0, size(outputs) - 1) AS outputIndex
WITH t, split(outputs[outputIndex], ',') AS output, outputIndex
MERGE (a:Address {addressId: output[0]})
CREATE (t)-[:OUTPUT {amount: toFloat(output[1]), position: outputIndex}]->(a)
"""

CREATE_INPUTS_QUERY = """
MATCH (t:Transaction {txId: $txId})
WITH t, $inputs AS inputs
UNWIND inputs AS inputString
WITH t, split(inputString, ',') AS input
MERGE (a:Address {addressId: input[0]})
CREATE (a)-[:INPUT {amount: toFloat(input[1]), prevTxId: input[2], prevTxPos: toInteger(input[3])}]->(t)
"""

def start_bitcoind():
    """Start the Bitcoin Core daemon."""
    print("Starting Bitcoin Core daemon...")
    subprocess.Popen(["bitcoind"])
    time.sleep(5)  # Give the daemon some time to start

def wait_for_rpc():
    """Wait for the Bitcoin Core RPC server to be ready."""
    while True:
        try:
            result = subprocess.run(["bitcoin-cli", "getblockchaininfo"], capture_output=True, text=True)
            if result.returncode == 0:
                print("Bitcoin Core RPC server is ready.")
                return
            elif "error code: -28" in result.stderr:
                print("Bitcoin Core is starting up... Waiting...")
            elif "error: timeout on transient error: Could not connect to the server" in result.stderr:
                start_bitcoind()
                print("Bitcoin Core is starting up... Waiting...")
            else:
                print(f"Unexpected error: {result.stderr.strip()}")
        except FileNotFoundError:
            print("Bitcoin Core is not running. Attempting to start it...")
            start_bitcoind()
        time.sleep(10)

def get_block_hash(block_height):
    """Get the block hash for a given block height."""
    result = subprocess.run(["bitcoin-cli", "getblockhash", str(block_height)], capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Error getting block hash: {result.stderr.strip()}")
    return result.stdout.strip()

def get_block(block_hash):
    """Get the block details for a given block hash."""
    result = subprocess.run(["bitcoin-cli", "getblock", block_hash, "2"], capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Error getting block: {result.stderr.strip()}")
    return json.loads(result.stdout)

def log_block_timing(block_number, timings):
    """Log the timing of a block to the CSV file."""
    with open(TIMING_CSV_FILE, mode="a", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow([block_number] + timings)

# Initialize the CSV file with headers
with open(TIMING_CSV_FILE, mode="w", newline="") as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(["BlockNumber", "GetBlockHash", "GetBlock", "CheckTransactions", "CreateTransactions", "CreateOutputs", "CreateInputs"])

# Main function to process blocks and insert into Neo4j
def process_blocks_to_neo4j():
    next_hash = None
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        driver.verify_connectivity()
        print("Connected to Neo4j database.")

        while True:
            try:
                with driver.session() as session:
                    # Get the last processed block from the database
                    last_block_result = session.run(GET_LAST_BLOCK_QUERY)
                    last_block = last_block_result.single()["lastBlock"]
                    start_block = 0 if last_block is None else last_block + 1

                    print(f"Starting from block {start_block}...")
                    block_height = start_block

                    while True:
                        timings = []

                        # Step 1: Get block hash
                        start_time = time.time()
                        block_hash = next_hash if next_hash else get_block_hash(block_height)
                        timings.append(time.time() - start_time)

                        # Step 2: Get block details
                        start_time = time.time()
                        block = get_block(block_hash)
                        timings.append(time.time() - start_time)
                        next_hash = block.get("nextblockhash")

                        # Step 3: Process transactions
                        start_time = time.time()
                        for tx in block["tx"]:
                            tx_id = tx["txid"]

                            # Check if the transaction already exists in the database
                            exists_result = session.run(CHECK_TRANSACTION_EXISTS_QUERY, txId=tx_id)
                            if exists_result.single():
                                print(f"Transaction {tx_id} already exists. Skipping...")
                                continue

                            # Prepare transaction data
                            is_coinbase = "1" if len(tx["vin"]) == 1 and "coinbase" in tx["vin"][0] else "0"
                            fee = 0  # Fee calculation requires additional logic
                            size = tx.get("size", 0)
                            vsize = tx.get("vsize", 0)
                            weight = tx.get("weight", 0)

                            # Process inputs
                            inputs = []
                            for vin in tx["vin"]:
                                if "txid" in vin:  # Regular input
                                    inputs.append(f"{vin['txid']},{vin['vout']},{vin.get('sequence', '0')}")
                                else:  # Coinbase input
                                    inputs.append("coinbase,0,0")

                            # Process outputs
                            outputs = []
                            for vout in tx["vout"]:
                                if "scriptPubKey" in vout and "hex" in vout["scriptPubKey"]:
                                    address = vout["scriptPubKey"]["hex"]
                                else:
                                    address = "unknown"

                                amount = vout["value"]
                                script_type = vout["scriptPubKey"].get("type", "unknown") if "scriptPubKey" in vout else "unknown"
                                outputs.append(f"{address},{amount},{script_type}")

                            # Insert transaction into the database
                            infos = [block["time"], block["height"], tx_id, is_coinbase, fee, size, vsize, weight]

                            # Step 4: Create transactions
                            start_time_tx = time.time()
                            session.run(CREATE_TRANSACTIONS_QUERY, infos=infos, inputs=inputs, outputs=outputs)
                            timings.append(time.time() - start_time_tx)

                            # Step 5: Create outputs
                            start_time_outputs = time.time()
                            session.run(CREATE_OUTPUTS_QUERY, txId=tx_id, outputs=outputs)
                            timings.append(time.time() - start_time_outputs)

                            # Step 6: Create inputs
                            start_time_inputs = time.time()
                            session.run(CREATE_INPUTS_QUERY, txId=tx_id, inputs=inputs)
                            timings.append(time.time() - start_time_inputs)

                        timings.insert(2, time.time() - start_time)  # Total time for checking transactions
                        log_block_timing(block_height, timings)

                        print(f"Processed block {block_height} with {len(block['tx'])} transactions.")
                        block_height += 1

            except Exception as e:
                error_message = str(e)
                if "Unable to retrieve routing information" in error_message or "TimeoutError" in error_message:
                    print(f"Error encountered: {error_message}. Retrying in 10 seconds...")
                    time.sleep(10)
                else:
                    print(f"Unexpected error: {error_message}")
                    break

# Ensure Bitcoin Core RPC server is ready
wait_for_rpc()

# Run the script
process_blocks_to_neo4j()