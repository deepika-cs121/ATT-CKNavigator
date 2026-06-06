#!/usr/bin/env python3
"""
WiFi Evil Twin Simulator & Detection Log
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
    interface: str
    ssid: str
    passphrase: str
    channel: int
    max_clients: int
    worker_threads: int
    max_duration_sec: int
    log_dir: str
    responsible_party: str
    emergency_stop_file: str

class WiFiEvilTwinSimulator:
    def __init__(self):
        self.config = None
        self.run_id = f"run{int(time.time())}"
        self.start_time = None
        self.stop_flag = False
        self.client_count = 0
        self.connected_clients = []
        self.attempts_log = []

    def get_user_input(self) -> RunConfig:
        print("=== WIFI EVIL TWIN SIMULATOR ===")
        print("Authorized Use Only – Requires Written Permission")
        print("=" * 45)

        interface = input("Enter WiFi interface (e.g., wlan0): ").strip()
        ssid = input("Enter SSID to mimic: ").strip()
        passphrase = input("Enter WPA passphrase: ").strip()
        try:
            channel = int(input("Channel [default 6]: ").strip() or "6")
            max_clients = int(input("Max clients [default 10]: ").strip() or "10")
            worker_threads = int(input("Worker threads [default 2]: ").strip() or "2")
            max_duration_sec = int(input("Max duration sec [default 300]: ").strip() or "300")
        except ValueError:
            print("Invalid numeric input.")
            sys.exit(1)

        log_dir = input("Log directory [default ./logs]: ").strip() or "./logs"
        os.makedirs(log_dir, exist_ok=True)

        responsible_party = input("Tester name & contact: ").strip()
        emergency_stop_file = input("Emergency stop file [default ./STOP]: ").strip() or "./STOP"

        return RunConfig(
            interface=interface, ssid=ssid, passphrase=passphrase, channel=channel,
            max_clients=max_clients, worker_threads=worker_threads,
            max_duration_sec=max_duration_sec, log_dir=log_dir,
            responsible_party=responsible_party, emergency_stop_file=emergency_stop_file
        )

    def simulate_client_connection(self):
        client_mac = ":".join(f"{random.randint(0,255):02x}" for _ in range(6))
        result = random.choice(['connected', 'connected', 'failed'])
        time.sleep(random.uniform(1, 5))
        return {
            "timestamp": datetime.now().isoformat(),
            "client_mac": client_mac,
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
        print(f"\nStarting Evil Twin Simulation on {self.config.interface} with SSID {self.config.ssid}")
        self.start_time = datetime.now()
        signal.signal(signal.SIGINT, self.signal_handler)

        with ThreadPoolExecutor(max_workers=self.config.worker_threads) as executor:
            futures = []
            while self.client_count < self.config.max_clients:
                if self.check_stop_conditions() or self.stop_flag:
                    break
                future = executor.submit(self.simulate_client_connection)
                futures.append(future)
                self.client_count += 1

            for future in as_completed(futures):
                result = future.result()
                self.attempts_log.append(result)
                if result['result'] == 'connected':
                    self.connected_clients.append({"client_mac": result["client_mac"]})

        self.cleanup()

    def cleanup(self):
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        summary = {
            "run_id": self.run_id,
            "interface": self.config.interface,
            "ssid": self.config.ssid,
            "start_time": self.start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_sec": duration,
            "total_clients": self.client_count,
            "connected_clients": len(self.connected_clients),
        }

        summary_path = os.path.join(self.config.log_dir, f"{self.run_id}_summary.json")
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)

        log_path = os.path.join(self.config.log_dir, f"{self.run_id}_attempts.jsonl")
        with open(log_path, 'w') as f:
            for entry in self.attempts_log:
                f.write(json.dumps(entry) + "\n")

        print("\nSimulation Completed")
        print(f"Total Client Attempts: {self.client_count}")
        print(f"Connected Clients: {len(self.connected_clients)}")
        print(f"Logs saved to: {os.path.abspath(self.config.log_dir)}")

        if self.connected_clients:
            print("\n=== CONNECTED CLIENTS ===")
            for client in self.connected_clients:
                print(f"[+] MAC: {client['client_mac']}")
            print("=======================================")
        else:
            print("No clients connected during this run.")

    def run(self):
        self.config = self.get_user_input()
        self.run_attack()

if __name__ == "__main__":
    simulator = WiFiEvilTwinSimulator()
    simulator.run()