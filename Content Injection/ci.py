#!/usr/bin/env python3
"""
Content Injection Simulator & Detection Log
For Authorized Security Testing Only
"""

import json
import os
import sys
import time
import random
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass

@dataclass
class RunConfig:
    url: str
    payload_file: str
    max_attempts_per_sec: int
    worker_threads: int
    max_total_attempts: int
    log_dir: str
    responsible_party: str
    emergency_stop_file: str

class ContentInjectionSimulator:
    def __init__(self):
        self.config = None
        self.run_id = f"run{int(time.time())}"
        self.start_time = None
        self.stop_flag = False
        self.attempt_count = 0
        self.success_count = 0
        self.successful_injections = []
        self.attempts_log = []

    def get_user_input(self) -> RunConfig:
        print("=== CONTENT INJECTION SIMULATOR ===")
        print("Authorized Use Only – Requires Written Permission")
        print("=" * 45)

        url = input("Enter target URL (e.g., http://localhost:5000/login): ").strip()
        payload_file = input("Path to payload list: ").strip()

        if not os.path.exists(payload_file):
            print("Payload file not found!")
            sys.exit(1)

        try:
            max_attempts_per_sec = int(input("Max attempts/sec [default 1]: ").strip() or "1")
            worker_threads = int(input("Worker threads [default 2]: ").strip() or "2")
            max_total_attempts = int(input("Max total attempts [default 100]: ").strip() or "100")
        except ValueError:
            print("Invalid numeric input.")
            sys.exit(1)

        log_dir = input("Log directory [default ./logs]: ").strip() or "./logs"
        os.makedirs(log_dir, exist_ok=True)

        responsible_party = input("Tester name & contact: ").strip()
        emergency_stop_file = input("Emergency stop file [default ./STOP]: ").strip() or "./STOP"

        return RunConfig(
            url=url, payload_file=payload_file,
            max_attempts_per_sec=max_attempts_per_sec, worker_threads=worker_threads,
            max_total_attempts=max_total_attempts, log_dir=log_dir,
            responsible_party=responsible_party, emergency_stop_file=emergency_stop_file
        )

    def simulate_injection_attempt(self, payload: str):
        data = {"username": payload, "password": ""}
        try:
            response = requests.post(self.config.url, data=data, timeout=5)
            result = "success" if "admin" in response.text.lower() else "failure"
        except Exception:
            result = "error"
        time.sleep(random.uniform(0.05, 0.3))
        return {
            "timestamp": datetime.now().isoformat(),
            "payload": payload,
            "result": result,
            "response_snippet": response.text[:100] if 'response' in locals() else ""
        }

    def check_stop_conditions(self):
        if os.path.exists(self.config.emergency_stop_file):
            print(f"Emergency stop file detected: {self.config.emergency_stop_file}")
            return True
        if self.attempt_count >= self.config.max_total_attempts:
            print("Max attempts reached.")
            return True
        return False

    def run_attack(self):
        print(f"\nStarting Content Injection Simulation on {self.config.url}")
        self.start_time = datetime.now()

        payloads = [p.strip() for p in open(self.config.payload_file)]

        with ThreadPoolExecutor(max_workers=self.config.worker_threads) as executor:
            futures = []
            for payload in payloads:
                if self.check_stop_conditions() or self.stop_flag:
                    break
                time.sleep(1 / self.config.max_attempts_per_sec)
                future = executor.submit(self.simulate_injection_attempt, payload)
                futures.append(future)
                self.attempt_count += 1

            for future in as_completed(futures):
                result = future.result()
                self.attempts_log.append(result)
                if result['result'] == 'success':
                    self.success_count += 1
                    self.successful_injections.append({"payload": result["payload"]})

        self.cleanup()

    def cleanup(self):
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        summary = {
            "run_id": self.run_id,
            "url": self.config.url,
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
        print(f"Successful Attempts: {self.success_count}")
        print(f"Logs saved to: {os.path.abspath(self.config.log_dir)}")

        if self.successful_injections:
            print("\n=== SUCCESSFUL INJECTIONS FOUND ===")
            for inj in self.successful_injections:
                print(f"[+] Payload: {inj['payload']}")
            print("=======================================")
        else:
            print("No successful injections found during this run.")

    def run(self):
        self.config = self.get_user_input()
        self.run_attack()

if __name__ == "__main__":
    simulator = ContentInjectionSimulator()
    simulator.run()