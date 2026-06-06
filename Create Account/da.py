#!/usr/bin/env python3
"""
Domain Account Creation Simulator & Detection Log
For Authorized Security Testing Only
"""

import json
import os
import sys
import time
import random
import signal
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass

@dataclass
class RunConfig:
    domain: str
    base_username: str
    max_attempts: int
    worker_threads: int
    log_dir: str
    responsible_party: str
    emergency_stop_file: str

class DomainAccountSimulator:
    def __init__(self):
        self.config = None
        self.run_id = f"run{int(time.time())}"
        self.start_time = None
        self.stop_flag = False
        self.attempt_count = 0
        self.success_count = 0
        self.created_accounts = []
        self.attempts_log = []

    def get_user_input(self) -> RunConfig:
        print("=== DOMAIN ACCOUNT CREATION SIMULATOR ===")
        print("Authorized Use Only – Requires Written Permission")
        print("=" * 45)

        domain = input("Enter domain (e.g., lab.local): ").strip()
        base_username = input("Enter base username: ").strip()
        try:
            max_attempts = int(input("Max attempts [default 5]: ").strip() or "5")
            worker_threads = int(input("Worker threads [default 1]: ").strip() or "1")
        except ValueError:
            print("Invalid numeric input.")
            sys.exit(1)

        log_dir = input("Log directory [default ./logs]: ").strip() or "./logs"
        os.makedirs(log_dir, exist_ok=True)

        responsible_party = input("Tester name & contact: ").strip()
        emergency_stop_file = input("Emergency stop file [default ./STOP]: ").strip() or "./STOP"

        return RunConfig(
            domain=domain, base_username=base_username, max_attempts=max_attempts,
            worker_threads=worker_threads, log_dir=log_dir,
            responsible_party=responsible_party, emergency_stop_file=emergency_stop_file
        )

    def simulate_create_account(self, suffix: str):
        full_username = f"{self.config.base_username}_{suffix}"
        result = random.choice(['success', 'failure'])
        time.sleep(random.uniform(0.3, 1.2))
        return {
            "timestamp": datetime.now().isoformat(),
            "username": full_username,
            "domain": self.config.domain,
            "result": result
        }

    def signal_handler(self, signum, frame):
        print("\nReceived termination signal, stopping gracefully...")
        self.stop_flag = True

    def check_stop_conditions(self):
        if os.path.exists(self.config.emergency_stop_file):
            print(f"Emergency stop file detected: {self.config.emergency_stop_file}")
            return True
        if self.attempt_count >= self.config.max_attempts:
            print("Max attempts reached.")
            return True
        return False

    def run_attack(self):
        print(f"\nStarting Domain Account Creation Simulation on {self.config.domain}")
        self.start_time = datetime.now()
        signal.signal(signal.SIGINT, self.signal_handler)

        with ThreadPoolExecutor(max_workers=self.config.worker_threads) as executor:
            futures = []
            for i in range(self.config.max_attempts):
                if self.check_stop_conditions() or self.stop_flag:
                    break
                future = executor.submit(self.simulate_create_account, str(i))
                futures.append(future)
                self.attempt_count += 1

            for future in as_completed(futures):
                result = future.result()
                self.attempts_log.append(result)
                if result['result'] == 'success':
                    self.success_count += 1
                    self.created_accounts.append({"username": result["username"]})

        self.cleanup()

    def cleanup(self):
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        summary = {
            "run_id": self.run_id,
            "domain": self.config.domain,
            "start_time": self.start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_sec": duration,
            "total_attempts": self.attempt_count,
            "total_successes": self.success_count,
        }

        summary_path = os.path.join(self.config.log_dir, f"{self.run_id}_summary.json")
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)

        log_path = os.path.join(self.config.log_dir, f"{self.run_id}_attempts.jsonl")
        with open(log_path, 'w') as f:
            for entry in self.attempts_log:
                f.write(json.dumps(entry) + "\n")

        print("\nSimulation Completed")
        print(f"Total Attempts: {self.attempt_count}")
        print(f"Successful Creations: {self.success_count}")
        print(f"Logs saved to: {os.path.abspath(self.config.log_dir)}")

        if self.created_accounts:
            print("\n=== CREATED DOMAIN ACCOUNTS ===")
            for acc in self.created_accounts:
                print(f"[+] Username: {acc['username']}@{self.config.domain}")
            print("=======================================")
        else:
            print("No domain accounts created during this run.")

    def run(self):
        self.config = self.get_user_input()
        self.run_attack()

if __name__ == "__main__":
    simulator = DomainAccountSimulator()
    simulator.run()