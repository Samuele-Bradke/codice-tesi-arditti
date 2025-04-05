import os
import csv
import subprocess
import json

CSV_FILE = "example.csv"
TRANSACTION_BATCH_SIZE = 1000  # Stop after processing this many transactions

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

def get_last_transaction_id(csv_file):
    """Get the last transaction ID from the CSV file."""
    if not os.path.exists(csv_file):
        return None
    with open(csv_file, mode="r") as file:
        reader = csv.reader(file, delimiter=":")
        rows = list(reader)
        if rows:
            last_row = rows[-1]
            return last_row[0].split(",")[2]  # Extract TxID as a string from the last row
    return None

def write_transactions_to_csv(block, csv_file):
    """Write transactions from a block to the CSV file in the correct format."""
    with open(csv_file, mode="a", newline="") as file:
        writer = csv.writer(file, delimiter=":")
        for tx in block["tx"]:
            tx_id = tx["txid"]  # TxID is a string (hash)
            is_coinbase = "1" if len(tx["vin"]) == 1 and "coinbase" in tx["vin"][0] else "0"
            fee = 0  # Fee calculation requires additional logic
            approx_size = tx.get("size", 0)
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
                # Extract address or fallback to "unknown"
                if "scriptPubKey" in vout and "hex" in vout["scriptPubKey"]:
                    address = vout["scriptPubKey"]["hex"]  # Handle multiple addresses
                else:
                    address = "unknown"

                amount = vout["value"]
                script_type = vout["scriptPubKey"].get("type", "unknown") if "scriptPubKey" in vout else "unknown"
                outputs.append(f"{address},{amount},{script_type}")

            # Combine inputs and outputs
            inputs_str = ";".join(inputs)
            outputs_str = ";".join(outputs)

            # Write the transaction to the CSV file
            writer.writerow([
                f"{block['time']},{block['height']},{tx_id},{is_coinbase},{fee},{approx_size}",
                inputs_str,
                outputs_str
            ])

def generate_csv_from_bitcoin_core(csv_file):
    """Generate a CSV file of Bitcoin transactions starting from the genesis block."""
    # Determine the last processed block height
    last_block_height = None
    next_block_hash = None
    transaction_count = 0
    if os.path.exists(csv_file):
        with open(csv_file, mode="r") as file:
            reader = csv.reader(file, delimiter=":")
            rows = list(reader)
            if rows:
                transaction_count = len(rows)
                last_row = rows[-1]
                last_block_height = int(last_row[0].split(",")[1])  # Extract block height from the last row

    start_block = 0 if last_block_height is None else last_block_height + 1

    print(f"Starting from block {start_block}...")
    block_height = start_block
    

    try:
        while True:
            if next_block_hash:
                block_hash = next_block_hash
            else:
                block_hash = get_block_hash(block_height)
            block = get_block(block_hash)
            next_block_hash = block["nextblockhash"] if "nextblockhash" in block else None
            write_transactions_to_csv(block, csv_file)
            transaction_count += int(block["nTx"])
            print(f"Processed block {block_height} with {len(block['tx'])} transactions. Total transactions: {transaction_count}.")
            block_height += 1
    except KeyboardInterrupt:
        print("Program interrupted by user. Exiting gracefully...")
    except Exception as e:
        print(f"Error processing block {block_height}: {e}")

# Generate the CSV file
generate_csv_from_bitcoin_core(CSV_FILE)