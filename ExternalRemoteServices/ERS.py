#!/usr/bin/env python3
"""
External Remote Services Simulator & Detection Log
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
    listener_port: int
    beacon_interval_sec: int
    max_beacons: int
    worker_threads: int
    max_duration_sec: int
    log_dir: str
    responsible_party: str
    emergency_stop_file: str

class ExternalRemoteSimulator:
    def __init__(self):
        self.config = None
        self.run_id = f"run{int(time.time())}"
        self.start_time = None
        self.stop_flag = False
        self.beacon_count = 0
        self.successful_beacons = []
        self.attempts_log = []

    def get_user_input(self) -> RunConfig:
        print("=== EXTERNAL REMOTE SERVICES SIMULATOR ===")
        print("Authorized Use Only – Requires Written Permission")
        print("=" * 45)

        try:
            listener_port = int(input("Listener port [default 4444]: ").strip() or "4444")
            beacon_interval_sec = int(input("Beacon interval sec [default 60]: ").strip() or "60")
            max_beacons = int(input("Max beacons [default 10]: ").strip() or "10")
            worker_threads = int(input("Worker threads [default 1]: ").strip() or "1")
            max_duration_sec = int(input("Max duration sec [default 300]: ").strip() or "300")
        except ValueError:
            print("Invalid numeric input.")
            sys.exit(1)

        log_dir = input("Log directory [default ./logs]: ").strip() or "./logs"
        os.makedirs(log_dir, exist_ok=True)

        responsible_party = input("Tester name & contact: ").strip()
        emergency_stop_file = input("Emergency stop file [default ./STOP]: ").strip() or "./STOP"

        return RunConfig(
            listener_port=listener_port, beacon_interval_sec=beacon_interval_sec,
            max_beacons=max_beacons, worker_threads=worker_threads,
            max_duration_sec=max_duration_sec, log_dir=log_dir,
            responsible_party=responsible_party, emergency_stop_file=emergency_stop_file
        )

    def simulate_beacon_attempt(self):
        result = random.choice(['success', 'failure', 'failure'])
        time.sleep(random.uniform(0.5, 2))
        return {
            "timestamp": datetime.now().isoformat(),
            "result": result
        }

    def signal_handler(self, signum, frame):
        print("\nReceived termination signal, stopping gracefully...")
        self.stop_flag = True

    def check_stop_conditions(self):
        if os.path.exists(self.config.emergency_stop_file):
            print(f"Emergency stop file detected: {self.config.emergency_stop_file}")
            return True
        if (datetime.now() - self.start_time).total_seconds() >= self.config.max_duration_sec:
            print("Max duration reached.")
            return True
        return False

    def run_attack(self):
        print(f"\nStarting External Remote Simulation on port {self.config.listener_port}")
        self.start_time = datetime.now()
        signal.signal(signal.SIGINT, self.signal_handler)

        with ThreadPoolExecutor(max_workers=self.config.worker_threads) as executor:
            futures = []
            while self.beacon_count < self.config.max_beacons:
                if self.check_stop_conditions() or self.stop_flag:
                    break
                time.sleep(self.config.beacon_interval_sec)
                future = executor.submit(self.simulate_beacon_attempt)
                futures.append(future)
                self.beacon_count += 1

            for future in as_completed(futures):
                result = future.result()
                self.attempts_log.append(result)
                if result['result'] == 'success':
                    self.successful_beacons.append(result["timestamp"])

        self.cleanup()

    def cleanup(self):
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        summary = {
            "run_id": self.run_id,
            "listener_port": self.config.listener_port,
            "start_time": self.start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_sec": duration,
            "total_beacons": self.beacon_count,
            "successful_beacons": len(self.successful_beacons),
        }

        summary_path = os.path.join(self.config.log_dir, f"{self.run_id}_summary.json")
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)

        log_path = os.path.join(self.config.log_dir, f"{self.run_id}_attempts.jsonl")
        with open(log_path, 'w') as f:
            for entry in self.attempts_log:
                f.write(json.dumps(entry) + "\n")

        print("\nSimulation Completed")
        print(f"Total Beacons: {self.beacon_count}")
        print(f"Successful Beacons: {len(self.successful_beacons)}")
        print(f"Logs saved to: {os.path.abspath(self.config.log_dir)}")

        if self.successful_beacons:
            print("\n=== SUCCESSFUL BEACONS ===")
            for ts in self.successful_beacons:
                print(f"[+] Timestamp: {ts}")
            print("=======================================")
        else:
            print("No successful beacons during this run.")

    def run(self):
        self.config = self.get_user_input()
        self.run_attack()

if __name__ == "__main__":
    simulator = ExternalRemoteSimulator()
    simulator.run()