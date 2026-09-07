"""Script tạo dữ liệu mô phỏng cho bài toán phát hiện bất thường thanh toán."""

from __future__ import annotations

import pandas as pd
import numpy as np
import uuid
import random
import hashlib
from datetime import datetime, timedelta
import os
from pathlib import Path


def main() -> None:
    # Set seed for reproducibility
    np.random.seed(42)
    random.seed(42)

    TOTAL_ROWS = 100000
    LABEL_0_ROWS = 70000
    LABEL_1_ROWS = 15000
    LABEL_2_ROWS = 15000

    # Select a random, less obvious date in 2025 (e.g. somewhere in August)
    base_time = datetime(2025, 8, random.randint(1, 28), random.randint(6, 18), random.randint(0, 59), 0)

    print("Generating Label 0 (Normal) data...")
    # Label 0: Normal
    normal_users = [f"USR_{str(i).zfill(5)}" for i in range(1, 5001)]
    normal_devices = {u: [f"DEV_{str(random.randint(10000, 99999))}" for _ in range(random.randint(1, 2))] for u in normal_users}
    normal_ips = {u: f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}" for u in normal_users}
    endpoints = ['/balance', '/transfer', '/transaction/history', '/login', '/logout']
    user_agents = ["Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)", "MyBankApp/1.0.0 (Android 11)", "MyBankApp/1.0.0 (iOS 15.0)"]

    data_0 = []
    
    # Generate requests per normal user to maintain realistic intervals
    requests_per_normal = LABEL_0_ROWS // len(normal_users)
    for u in normal_users:
        # Each user starts at a random time within the first hour to interleave them
        user_time = base_time + timedelta(seconds=random.randint(0, 3600))
        for _ in range(requests_per_normal):
            dev = random.choice(normal_devices[u])
            ip = normal_ips[u]
            if random.random() < 0.05: # 5% IP change
                ip = f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}"
            
            endpoint = random.choice(endpoints)
            method = 'POST' if endpoint in ['/transfer', '/login', '/logout'] else 'GET'
            amt = random.randint(50, 10000) * 1000 if endpoint == '/transfer' else None
            receiver = f"ACC_{str(random.randint(10000, 99999))}" if endpoint == '/transfer' else None
            tx_type = 'TRANSFER' if endpoint == '/transfer' else ('INQUIRY' if endpoint in ['/balance', '/transaction/history'] else None)
            
            # jwt hash (normal users don't change often)
            jwt = hashlib.md5(f"{u}_{random.randint(1,2)}".encode()).hexdigest()
            
            data_0.append([
                user_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                str(uuid.uuid4()),
                str(uuid.uuid4()),
                u,
                jwt,
                dev,
                ip,
                random.choice(user_agents),
                endpoint,
                method,
                random.randint(200, 2000),
                f"ACC_{u[-5:]}",
                receiver,
                amt,
                tx_type,
                200 if random.random() < 0.95 else random.choice([401, 403, 500]),
                "00" if random.random() < 0.95 else random.choice(["05", "06", "99"]),
                random.randint(50, 500),
                random.randint(100, 5000),
                0
            ])
            # interval: 30s to a few hours
            user_time += timedelta(seconds=random.randint(30, 10800))

    print("Generating Label 1 (Token Abuse) data...")
    # Label 1: Token abuse
    straw_users = [f"USR_{str(i).zfill(5)}" for i in range(5001, 5051)]
    data_1 = []
    requests_per_abuser = LABEL_1_ROWS // len(straw_users)
    for u in straw_users:
        user_time = base_time + timedelta(seconds=random.randint(0, 3600))
        for _ in range(requests_per_abuser):
            dev = f"DEV_{str(random.randint(10000, 99999))}"
            ip = f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}"
            jwt = hashlib.md5(str(random.random()).encode()).hexdigest()
            
            data_1.append([
                user_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                str(uuid.uuid4()),
                str(uuid.uuid4()),
                u,
                jwt,
                dev,
                ip,
                "python-requests/2.28.1", # usually a script
                "/transaction/history",
                "GET",
                random.randint(100, 300),
                f"ACC_{u[-5:]}",
                None,
                None,
                "INQUIRY",
                200,
                "00",
                random.randint(10, 100),
                random.randint(500, 2000),
                1
            ])
            user_time += timedelta(seconds=random.randint(2, 10))

    print("Generating Label 2 (Straw Account) data...")
    # Label 2: Straw account receiving transfers
    straw_receivers = [f"ACC_{u[-5:]}" for u in straw_users]
    data_2 = []
    requests_per_receiver = LABEL_2_ROWS // len(straw_receivers)
    for receiver in straw_receivers:
        receiver_time = base_time + timedelta(seconds=random.randint(0, 3600))
        for _ in range(requests_per_receiver):
            sender_u = f"USR_{str(random.randint(10000, 99999))}" # diverse senders
            sender_acc = f"ACC_{sender_u[-5:]}"
            dev = f"DEV_{str(random.randint(10000, 99999))}"
            ip = f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}"
            jwt = hashlib.md5(f"{sender_u}".encode()).hexdigest()
            amt = random.choice([1000, 2000, 5000, 10000])
            
            data_2.append([
                receiver_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                str(uuid.uuid4()),
                str(uuid.uuid4()),
                sender_u,
                jwt,
                dev,
                ip,
                random.choice(user_agents),
                "/transfer",
                "POST",
                random.randint(500, 1500),
                sender_acc,
                receiver,
                amt,
                "TRANSFER",
                200,
                "00",
                random.randint(100, 500),
                random.randint(200, 1000),
                2
            ])
            receiver_time += timedelta(seconds=random.randint(5, 30))

    print("Combining, sorting, and shuffling data...")
    columns = [
        'timestamp', 'request_id', 'trace_id', 'user_id', 'jwt_token_hash', 
        'device_id', 'ip_address', 'user_agent', 'endpoint', 'method', 
        'request_size_bytes', 'sender_id', 'receiver_id', 'amount', 
        'transaction_type', 'response_code', 'business_code', 'response_time_ms', 
        'response_size_bytes', 'label'
    ]

    df_0 = pd.DataFrame(data_0, columns=columns)
    df_1 = pd.DataFrame(data_1, columns=columns)
    df_2 = pd.DataFrame(data_2, columns=columns)

    # Combine and sort by timestamp to simulate interleaved high traffic log stream
    df_full = pd.concat([df_0, df_1, df_2])
    # Convert timestamp to datetime for sorting
    df_full['timestamp_dt'] = pd.to_datetime(df_full['timestamp'])
    df_full = df_full.sort_values('timestamp_dt')
    # Drop the temporary datetime column
    df_full = df_full.drop(columns=['timestamp_dt'])

    # Now shuffle the full dataset for splitting
    df_full_shuffled = df_full.sample(frac=1, random_state=42).reset_index(drop=True)

    # Generate Train, Val, Test split
    train_size = int(0.7 * TOTAL_ROWS)
    val_size = int(0.15 * TOTAL_ROWS)
    
    df_train = df_full_shuffled.iloc[:train_size]
    df_val = df_full_shuffled.iloc[train_size:train_size+val_size]
    df_test = df_full_shuffled.iloc[train_size+val_size:]

    # determine the output directory relative to the script
    script_dir = Path(__file__).resolve().parent
    output_dir = script_dir / 'raw'
    os.makedirs(output_dir, exist_ok=True)

    print("Saving to CSV...")
    # Save the time-sorted full data to full_data_sorted.csv (good for time-series analysis)
    df_full.to_csv(f'{output_dir}/full_data_sorted.csv', index=False)
    # Save the shuffled data as requested
    df_full_shuffled.to_csv(f'{output_dir}/full_data.csv', index=False)
    df_train.to_csv(f'{output_dir}/train.csv', index=False)
    df_val.to_csv(f'{output_dir}/validation.csv', index=False)
    df_test.to_csv(f'{output_dir}/test.csv', index=False)

    print("\n=== Dataset Statistics ===")
    print("Full Data Label Distribution:")
    print(df_full_shuffled['label'].value_counts().sort_index())
    print("\nTrain Data Label Distribution:")
    print(df_train['label'].value_counts().sort_index())
    print("\nValidation Data Label Distribution:")
    print(df_val['label'].value_counts().sort_index())
    print("\nTest Data Label Distribution:")
    print(df_test['label'].value_counts().sort_index())
    
    # Optional: Print time range
    print(f"\nTime range: {df_full['timestamp'].iloc[0]} to {df_full['timestamp'].iloc[-1]}")
    print("==========================")
    print(f"Data saved successfully to {output_dir}/")


if __name__ == "__main__":
    main()
