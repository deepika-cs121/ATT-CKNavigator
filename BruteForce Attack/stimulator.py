#!/usr/bin/env python3
"""
Brute Force Attack Simulator & Detection Log
For Authorized Security Testing Only
"""

import json
import os
import sys
import time
import random
import getpass
import signal
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass

@dataclass
class RunConfig:
    target: str
    service: str
    mode: str
    attack_mode: str
    username_file: str
    password_file: str
    max_attempts_per_sec: int
    worker_threads: int
    max_total_attempts: int
    log_dir: str
    responsible_party: str
    emergency_stop_file: str

class BruteForceSimulator:
    def __init__(self):
        self.config = None
        self.run_id = f"run{int(time.time())}"
        self.start_time = None
        self.stop_flag = False
        self.attempt_count = 0
        self.success_count = 0
        self.unique_src_ips = set()
        self.successful_credentials = []
        self.attempts_log = []

    def get_user_input(self) -> RunConfig:
        print("=== BRUTE FORCE ATTACK SIMULATOR ===")
        print("⚠️ Authorized Use Only – Requires Written Permission")
        print("=" * 45)

        target = input("Enter target IP or hostname: ").strip()
        service = input("Enter service (ssh/http/ftp): ").strip().lower()
        mode = input("Run mode (dry-run/live-lab): ").strip().lower()
        attack_mode = input("Attack mode (guessing/spray/stuffing): ").strip().lower()

        username_file = input("Path to username list: ").strip()
        password_file = input("Path to password list: ").strip()

        if not os.path.exists(username_file) or not os.path.exists(password_file):
            print("❌ Username or password file not found!")
            sys.exit(1)

        try:
            max_attempts_per_sec = int(input("Max attempts/sec [default 1]: ").strip() or "1")
            worker_threads = int(input("Worker threads [default 2]: ").strip() or "2")
            max_total_attempts = int(input("Max total attempts [default 1000]: ").strip() or "1000")
        except ValueError:
            print("❌ Invalid numeric input.")
            sys.exit(1)

        log_dir = input("Log directory [default ./logs]: ").strip() or "./logs"
        os.makedirs(log_dir, exist_ok=True)

        responsible_party = input("Tester name & contact: ").strip()
        emergency_stop_file = input("Emergency stop file [default ./STOP]: ").strip() or "./STOP"

        return RunConfig(
            target=target, service=service, mode=mode, attack_mode=attack_mode,
            username_file=username_file, password_file=password_file,
            max_attempts_per_sec=max_attempts_per_sec, worker_threads=worker_threads,
            max_total_attempts=max_total_attempts, log_dir=log_dir,
            responsible_party=responsible_party, emergency_stop_file=emergency_stop_file
        )

    def simulate_auth_attempt(self, username: str, password: str, src_ip: str):
        """Simulate an authentication attempt (success/failure)"""
        result = random.choice(['failure'] * 4 + ['success'])  # 20% success rate
        time.sleep(random.uniform(0.05, 0.3))
        return {
            "timestamp": datetime.now().isoformat(),
            "username": username,
            "password": password,
            "src_ip": src_ip,
            "result": result
        }

    def signal_handler(self, signum, frame):
        print("\n🛑 Received termination signal, stopping gracefully...")
        self.stop_flag = True

    def check_stop_conditions(self):
        if os.path.exists(self.config.emergency_stop_file):
            print(f"🛑 Emergency stop file detected: {self.config.emergency_stop_file}")
            return True
        if self.attempt_count >= self.config.max_total_attempts:
            print("ℹ️ Max attempts reached.")
            return True
        return False

    def run_attack(self):
        print(f"\n🚀 Starting Brute Force Simulation on {self.config.target}")
        self.start_time = datetime.now()
        signal.signal(signal.SIGINT, self.signal_handler)

        usernames = [u.strip() for u in open(self.config.username_file)]
        passwords = [p.strip() for p in open(self.config.password_file)]

        with ThreadPoolExecutor(max_workers=self.config.worker_threads) as executor:
            futures = []
            for username in usernames:
                for password in passwords:
                    if self.check_stop_conditions() or self.stop_flag:
                        break
                    src_ip = f"192.168.1.{random.randint(1, 254)}"
                    time.sleep(1 / self.config.max_attempts_per_sec)
                    future = executor.submit(self.simulate_auth_attempt, username, password, src_ip)
                    futures.append(future)
                    self.attempt_count += 1

            for future in as_completed(futures):
                result = future.result()
                self.attempts_log.append(result)
                if result['result'] == 'success':
                    self.success_count += 1
                    self.successful_credentials.append(
                        {"username": result["username"], "password": result["password"]}
                    )

        self.cleanup()

    def cleanup(self):
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        summary = {
            "run_id": self.run_id,
            "target": self.config.target,
            "service": self.config.service,
            "mode": self.config.mode,
            "attack_mode": self.config.attack_mode,
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

        print("\n✅ Simulation Completed")
        print(f"📊 Total Attempts: {self.attempt_count}")
        print(f"✅ Successful Attempts: {self.success_count}")
        print(f"📁 Logs saved to: {os.path.abspath(self.config.log_dir)}")

        if self.successful_credentials:
            print("\n=== ✅ SUCCESSFUL CREDENTIALS FOUND ===")
            for cred in self.successful_credentials:
                print(f"[+] Username: {cred['username']} | Password: {cred['password']}")
            print("=======================================")
        else:
            print("❌ No valid credentials found during this run.")

    def run(self):
        self.config = self.get_user_input()
        self.run_attack()

if __name__ == "__main__":
    simulator = BruteForceSimulator()
    simulator.run()
