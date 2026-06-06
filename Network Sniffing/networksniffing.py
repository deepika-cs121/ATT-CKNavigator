#!/usr/bin/env python3
"""
Network Sniffing Simulator & Detection Log
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
    packet_count: int
    max_duration_sec: int
    worker_threads: int
    log_dir: str
    responsible_party: str
    emergency_stop_file: str

class NetworkSniffingSimulator:
    def __init__(self):
        self.config = None
        self.run_id = f"run{int(time.time())}"
        self.start_time = None
        self.stop_flag = False
        self.packet_count = 0
        self.captured_packets = []
        self.attempts_log = []

    def get_user_input(self) -> RunConfig:
        print("=== NETWORK SNIFFING SIMULATOR ===")
        print("Authorized Use Only – Requires Written Permission")
        print("=" * 45)

        interface = input("Enter interface (e.g., eth0): ").strip()
        try:
            packet_count = int(input("Packet count [default 100]: ").strip() or "100")
            max_duration_sec = int(input("Max duration sec [default 60]: ").strip() or "60")
            worker_threads = int(input("Worker threads [default 1]: ").strip() or "1")
        except ValueError:
            print("Invalid numeric input.")
            sys.exit(1)

        log_dir = input("Log directory [default ./logs]: ").strip() or "./logs"
        os.makedirs(log_dir, exist_ok=True)

        responsible_party = input("Tester name & contact: ").strip()
        emergency_stop_file = input("Emergency stop file [default ./STOP]: ").strip() or "./STOP"

        return RunConfig(
            interface=interface, packet_count=packet_count,
            max_duration_sec=max_duration_sec, worker_threads=worker_threads,
            log_dir=log_dir, responsible_party=responsible_party,
            emergency_stop_file=emergency_stop_file
        )

    def simulate_sniff_packet(self):
        pkt = {
            "src": f"192.168.1.{random.randint(1,254)}",
            "dst": f"192.168.1.{random.randint(1,254)}",
            "payload": "".join(random.choices("abcdef0123456789", k=50))
        }
        time.sleep(random.uniform(0.1, 0.5))
        return {
            "timestamp": datetime.now().isoformat(),
            "packet": pkt
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
        print(f"\nStarting Network Sniffing Simulation on {self.config.interface}")
        self.start_time = datetime.now()
        signal.signal(signal.SIGINT, self.signal_handler)

        with ThreadPoolExecutor(max_workers=self.config.worker_threads) as executor:
            futures = []
            while self.packet_count < self.config.packet_count:
                if self.check_stop_conditions() or self.stop_flag:
                    break
                future = executor.submit(self.simulate_sniff_packet)
                futures.append(future)
                self.packet_count += 1

            for future in as_completed(futures):
                result = future.result()
                self.attempts_log.append(result)
                self.captured_packets.append(result["packet"])

        self.cleanup()

    def cleanup(self):
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        summary = {
            "run_id": self.run_id,
            "interface": self.config.interface,
            "start_time": self.start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_sec": duration,
            "total_packets": self.packet_count,
        }

        summary_path = os.path.join(self.config.log_dir, f"{self.run_id}_summary.json")
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)

        log_path = os.path.join(self.config.log_dir, f"{self.run_id}_attempts.jsonl")
        with open(log_path, 'w') as f:
            for entry in self.attempts_log:
                f.write(json.dumps(entry) + "\n")

        print("\nSimulation Completed")
        print(f"Total Packets Captured: {self.packet_count}")
        print(f"Logs saved to: {os.path.abspath(self.config.log_dir)}")

        if self.captured_packets:
            print("\n=== CAPTURED PACKETS SAMPLE ===")
            for pkt in self.captured_packets[:5]:
                print(f"[+] Src: {pkt['src']} | Dst: {pkt['dst']}")
            print("=======================================")
        else:
            print("No packets captured during this run.")

    def run(self):
        self.config = self.get_user_input()
        self.run_attack()

if __name__ == "__main__":
    simulator = NetworkSniffingSimulator()
    simulator.run()