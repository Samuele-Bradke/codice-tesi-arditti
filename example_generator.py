import random
import csv

def generate_bitcoin_transactions(file_path, num_transactions):
    with open(file_path, mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=':')
        for _ in range(num_transactions):
            # Generate random transaction data
            timestamp = random.randint(1609459200, 1640995200)  # Random timestamp (2021-2022)
            block_id = random.randint(1, 700000)  # Random block ID
            tx_id = random.randint(1, 1000000)  # Random transaction ID
            is_coinbase = random.choice(['0', '1'])  # Random coinbase flag
            fee = random.randint(100, 10000)  # Random fee in satoshis

            # Generate random inputs and outputs
            num_inputs = random.randint(1, 5)
            num_outputs = random.randint(1, 5)
            inputs = ';'.join([f"{random.randint(1, 100000)},{random.randint(1000, 100000)},{random.randint(1, 100000)},{random.randint(0, 10)}" for _ in range(num_inputs)])
            outputs = ';'.join([f"{random.randint(1, 100000)},{random.randint(1000, 100000)}" for _ in range(num_outputs)])

            # Write the transaction to the CSV file
            writer.writerow([f"{timestamp},{block_id},{tx_id},{is_coinbase},{fee}", inputs, outputs])

# Generate 100 Bitcoin transactions and save to example.csv
generate_bitcoin_transactions("example.csv", 1000)
print("Synthetic Bitcoin transactions generated successfully.")