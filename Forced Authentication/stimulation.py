#!/usr/bin/env python3
"""
SMB Relay / Forced Authentication Simulator (MITRE ATT&CK T1187)
Lab-only simulator for training and detection validation.
Do NOT run against systems you don't own or have explicit written permission to test.
"""

import json
import os
import sys
import time
import random
import getpass
import signal
from datetime import datetime, timedelta
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import ipaddress

@dataclass
class RelayConfig:
    target_network: str
    smb_ports: list
    relay_target: str
    mode: str
    capture_method: str
    listener_port: int
    max_attempts: int
    worker_threads: int
    log_dir: str
    responsible_party: str
    emergency_stop_file: str

class ForcedAuthSimulator:
    def __init__(self):
        self.config: RelayConfig = None
        self.run_id = f"relay{int(time.time())}"
        self.start_time = None
        self.stop_flag = False
        self.attempt_count = 0
        self.success_count = 0
        self.captured_hashes = []
        self.relay_attempts = []
        self.consent_log_path = "consent_log.json"

    def write_consent_log(self, result: str):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "user": getpass.getuser(),
            "responsible": (self.config.responsible_party if self.config else ""),
            "target_network": (self.config.target_network if self.config else ""),
            "relay_target": (self.config.relay_target if self.config else ""),
            "mode": (self.config.mode if self.config else ""),
            "capture_method": (self.config.capture_method if self.config else ""),
            "run_id": self.run_id,
            "result": result
        }
        with open(self.consent_log_path, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def write_run_metadata(self):
        metadata = {
            "run_id": self.run_id,
            "config": self.config.__dict__,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "user": getpass.getuser()
        }
        path = os.path.join(self.config.log_dir, "run_metadata.json")
        with open(path, "w") as f:
            json.dump(metadata, f, indent=2)

    def get_user_input(self) -> RelayConfig:
        print("=== SMB RELAY / FORCED AUTHENTICATION SIMULATOR ===")
        print("MITRE ATT&CK T1187 - Forced Authentication")
        print("⚠️ Authorized Use Only – Requires Written Permission")
        print("=" * 55)

        # Written permission confirmation
        permission = input("Type 'I_HAVE_WRITTEN_PERMISSION' to confirm: ").strip()
        if permission != "I_HAVE_WRITTEN_PERMISSION":
            print("❌ Written permission confirmation failed!")
            sys.exit(1)

        # Target configuration (accept single IP or CIDR)
        target_network = input("Enter target network (CIDR or single IP) [e.g., 192.168.1.0/24 or 192.168.1.10]: ").strip()
        try:
            # allow either an IP or network
            try:
                ipaddress.ip_network(target_network, strict=False)
            except Exception:
                # try to parse as a single IP
                ipaddress.ip_address(target_network)
        except ValueError:
            print("❌ Invalid network or IP provided!")
            sys.exit(1)

        relay_target = input("Enter relay target IP/hostname (the host you'd attempt to relay to): ").strip()
        if not relay_target:
            print("❌ Relay target required!")
            sys.exit(1)

        # Mode selection
        mode = input("Run mode (recon/live-capture/relay-attack) [default live-capture]: ").strip().lower() or "live-capture"
        if mode not in ['recon', 'live-capture', 'relay-attack']:
            print("❌ Invalid mode selected!")
            sys.exit(1)

        # Capture method
        capture_method = input("Capture method (llmnr-poisoning/wpad-spoofing/smb-listener) [default wpad-spoofing]: ").strip().lower() or "wpad-spoofing"
        if capture_method not in ['llmnr-poisoning', 'wpad-spoofing', 'smb-listener']:
            print("❌ Invalid capture method!")
            sys.exit(1)

        # Technical configuration (with safe defaults)
        try:
            listener_port = int(input("Listener port [default 445]: ").strip() or "445")
            max_attempts = int(input("Max capture attempts [default 100]: ").strip() or "100")
            worker_threads = int(input("Worker threads [default 3]: ").strip() or "3")
        except ValueError:
            print("❌ Invalid numeric input!")
            sys.exit(1)

        # Logging and safety
        log_dir = input("Log directory [default ./smb_relay_logs]: ").strip() or "./smb_relay_logs"
        os.makedirs(log_dir, exist_ok=True)

        responsible_party = input("Tester name & contact (optional): ").strip()
        emergency_stop_file = input("Emergency stop file [default ./STOP_RELAY]: ").strip() or "./STOP_RELAY"

        # Build config dataclass
        return RelayConfig(
            target_network=target_network,
            smb_ports=[445, 139],
            relay_target=relay_target,
            mode=mode,
            capture_method=capture_method,
            listener_port=listener_port,
            max_attempts=max_attempts,
            worker_threads=worker_threads,
            log_dir=log_dir,
            responsible_party=responsible_party,
            emergency_stop_file=emergency_stop_file
        )

    def simulate_llmnr_poisoning(self):
        """Simulate LLMNR/NBT-NS poisoning to capture authentication attempts (synthetic)"""
        print("[*] Simulating LLMNR/NBT-NS poisoning...")
        fake_responses = [
            {"query": "FILESERVER", "response": "192.168.1.100", "protocol": "LLMNR"},
            {"query": "SHARE01", "response": "192.168.1.101", "protocol": "NBT-NS"},
            {"query": "PRINTER02", "response": "192.168.1.102", "protocol": "LLMNR"}
        ]

        for response in fake_responses:
            if self.check_stop_conditions():
                break

            capture_event = {
                "timestamp": datetime.now().isoformat(),
                "event_type": "llmnr_poisoning",
                "query": response["query"],
                "spoofed_ip": response["response"],
                "protocol": response["protocol"],
                "result": "captured"
            }
            self.relay_attempts.append(capture_event)
            self.attempt_count += 1

            print(f"[+] LLMNR Poisoning: {response['query']} -> {response['response']}")
            time.sleep(random.uniform(0.5, 2.0))

    def simulate_smb_capture(self, client_ip: str):
        """Simulate SMB authentication capture (synthetic)"""
        hash_types = ["NTLMv1", "NTLMv2"]
        captured_hash = {
            "timestamp": datetime.now().isoformat(),
            "source_ip": client_ip,
            "target": f"\\\\{self.config.relay_target}\\IPC$",
            "hash_type": random.choice(hash_types),
            "username": f"DOMAIN\\user{random.randint(1, 50)}",
            "challenge": f"{random.getrandbits(64):016x}",
            "response": f"{random.getrandbits(128):032x}",
            "result": "captured"
        }

        self.captured_hashes.append(captured_hash)
        self.attempt_count += 1
        return captured_hash

    def simulate_hash_relay(self, captured_hash: dict):
        """Simulate relaying captured hash to target (synthetic)"""
        relay_results = ["success", "failure", "access_denied", "signing_required"]
        weights = [15, 60, 20, 5]  # simulated distribution
        result = random.choices(relay_results, weights=weights, k=1)[0]

        relay_event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "hash_relay",
            "source_hash": captured_hash,
            "relay_target": self.config.relay_target,
            "result": result,
            "session_established": result == "success",
            "privileges": "admin" if result == "success" else "none"
        }

        if result == "success":
            self.success_count += 1
            print(f"[!] SUCCESS: Hash relay successful to {self.config.relay_target}")

        self.relay_attempts.append(relay_event)
        return relay_event

    def simulate_smb_listener(self):
        """Simulate SMB listener capturing authentication attempts (synthetic)"""
        print(f"[*] Starting SMB listener simulation on port {self.config.listener_port}")

        # generate a handful of synthetic client IPs
        client_ips = [f"192.168.1.{random.randint(10, 200)}" for _ in range(random.randint(5, 15))]

        for client_ip in client_ips:
            if self.check_stop_conditions():
                break

            print(f"[*] Simulating connection from {client_ip}")

            # capture
            captured_hash = self.simulate_smb_capture(client_ip)
            print(f"[+] Captured {captured_hash['hash_type']} hash from {client_ip}")

            # optionally attempt relay (only in relay-attack mode)
            if self.config.mode == "relay-attack":
                _ = self.simulate_hash_relay(captured_hash)

            time.sleep(random.uniform(1.0, 3.0))

    def simulate_wpad_spoofing(self):
        """Simulate WPAD spoofing attacks (synthetic)"""
        print("[*] Simulating WPAD spoofing attack...")

        wpad_events = [
            {"client": "192.168.1.50", "wpad_url": "http://attacker.local/wpad.dat", "result": "captured"},
            {"client": "192.168.1.75", "wpad_url": "http://malicious.net/proxy.pac", "result": "captured"},
            {"client": "192.168.1.120", "wpad_url": "http://evil.corp/wpad.dat", "result": "failed"}
        ]

        for event in wpad_events:
            if self.check_stop_conditions():
                break

            wpad_capture = {
                "timestamp": datetime.now().isoformat(),
                "event_type": "wpad_spoofing",
                "client_ip": event["client"],
                "wpad_url": event["wpad_url"],
                "result": event["result"],
                "authentication_captured": event["result"] == "captured"
            }

            self.relay_attempts.append(wpad_capture)
            self.attempt_count += 1
            print(f"[+] WPAD Spoofing: {event['client']} -> {event['wpad_url']}")
            time.sleep(random.uniform(1.0, 2.0))

    def scan_network_for_smb(self):
        """Simulate network scanning for SMB services (synthetic)"""
        print(f"[*] Scanning network {self.config.target_network} for SMB services...")

        smb_hosts = [
            {"ip": "192.168.1.10", "port": 445, "hostname": "FILESERVER01", "signing": "disabled"},
            {"ip": "192.168.1.15", "port": 445, "hostname": "DC01", "signing": "required"},
            {"ip": "192.168.1.20", "port": 139, "hostname": "WORKSTATION05", "signing": "disabled"},
            {"ip": "192.168.1.25", "port": 445, "hostname": "SHARE02", "signing": "disabled"}
        ]

        for host in smb_hosts:
            if self.check_stop_conditions():
                break

            scan_result = {
                "timestamp": datetime.now().isoformat(),
                "event_type": "smb_scan",
                "target_ip": host["ip"],
                "port": host["port"],
                "hostname": host["hostname"],
                "signing_status": host["signing"],
                "vulnerable": host["signing"] == "disabled"
            }

            self.relay_attempts.append(scan_result)
            print(f"[+] Found SMB: {host['ip']}:{host['port']} ({host['hostname']}) - Signing: {host['signing']}")
            time.sleep(0.5)

        return smb_hosts

    def signal_handler(self, signum, frame):
        print("\n🛑 Received termination signal, stopping gracefully...")
        self.stop_flag = True

    def check_stop_conditions(self):
        if os.path.exists(self.config.emergency_stop_file):
            print(f"🛑 Emergency stop file detected: {self.config.emergency_stop_file}")
            return True
        if self.attempt_count >= self.config.max_attempts:
            print("ℹ️ Max attempts reached.")
            return True
        return self.stop_flag

    def display_attack_summary(self):
        print("\n" + "="*60)
        print("MITRE ATT&CK T1187 - FORCED AUTHENTICATION")
        print("="*60)
        print("Tactic: Credential Access")
        print("Platform: Windows")
        print("Description: Forced authentication attacks force a client to authenticate")
        print("to an attacker-controlled server, typically via SMB relay attacks.")
        print("\nCommon Techniques:")
        print("  • LLMNR/NBT-NS Poisoning")
        print("  • WPAD Spoofing") 
        print("  • SMB Relay Attacks")
        print("  • IPv6 DNS Spoofing")
        print("="*60)

    def run_attack(self):
        print(f"\n🚀 Starting Forced Authentication Simulation (T1187)")
        self.display_attack_summary()

        self.start_time = datetime.now()
        signal.signal(signal.SIGINT, self.signal_handler)

        print(f"\n[*] Configuration:")
        print(f"    Target Network: {self.config.target_network}")
        print(f"    Relay Target: {self.config.relay_target}")
        print(f"    Mode: {self.config.mode}")
        print(f"    Capture Method: {self.config.capture_method}")

        # Write metadata and consent entry
        self.write_consent_log("started")
        self.write_run_metadata()

        # Recon / scan
        if self.config.mode in ["recon", "live-capture", "relay-attack"]:
            vulnerable_hosts = self.scan_network_for_smb()
            print(f"[*] Found {len(vulnerable_hosts)} SMB hosts, {len([h for h in vulnerable_hosts if h['signing'] == 'disabled'])} vulnerable")

        # Attack execution based on chosen capture method
        tasks = []
        with ThreadPoolExecutor(max_workers=self.config.worker_threads) as executor:
            if self.config.capture_method == "llmnr-poisoning":
                tasks.append(executor.submit(self.simulate_llmnr_poisoning))
            elif self.config.capture_method == "wpad-spoofing":
                tasks.append(executor.submit(self.simulate_wpad_spoofing))
            elif self.config.capture_method == "smb-listener":
                tasks.append(executor.submit(self.simulate_smb_listener))

            # Wait for tasks (they are synthetic and will complete)
            try:
                for fut in as_completed(tasks):
                    if self.check_stop_conditions():
                        break
                    fut.result()
            except KeyboardInterrupt:
                self.stop_flag = True

        self.cleanup()

    def cleanup(self):
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds() if self.start_time else 0.0

        summary = {
            "run_id": self.run_id,
            "technique": "T1187 - Forced Authentication",
            "target_network": self.config.target_network,
            "relay_target": self.config.relay_target,
            "mode": self.config.mode,
            "capture_method": self.config.capture_method,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": end_time.isoformat(),
            "duration_sec": duration,
            "total_attempts": self.attempt_count,
            "hashes_captured": len(self.captured_hashes),
            "successful_relays": self.success_count,
            "success_rate": (self.success_count / max(self.attempt_count, 1)) * 100
        }

        # Save summary and logs
        os.makedirs(self.config.log_dir, exist_ok=True)
        summary_path = os.path.join(self.config.log_dir, f"{self.run_id}_summary.json")
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)

        log_path = os.path.join(self.config.log_dir, f"{self.run_id}_events.jsonl")
        with open(log_path, 'w') as f:
            for entry in self.relay_attempts:
                f.write(json.dumps(entry) + "\n")

        if self.captured_hashes:
            hashes_path = os.path.join(self.config.log_dir, f"{self.run_id}_hashes.json")
            with open(hashes_path, 'w') as f:
                json.dump(self.captured_hashes, f, indent=2)

        # finalize consent log
        self.write_consent_log("completed")

        print("\n✅ SMB Relay Simulation Completed")
        print(f"📊 Total Events: {self.attempt_count}")
        print(f"🔐 Hashes Captured: {len(self.captured_hashes)}")
        print(f"🔄 Successful Relays: {self.success_count}")
        print(f"📁 Logs saved to: {os.path.abspath(self.config.log_dir)}")

        if self.success_count > 0:
            print("\n🔴 CRITICAL FINDINGS:")
            print("   Successful SMB relay attacks detected!")
            print("   Recommendations:")
            print("   • Enable SMB signing on all hosts")
            print("   • Disable LLMNR and NBT-NS where possible")
            print("   • Implement network segmentation")
            print("   • Monitor for anomalous SMB traffic")

    def run(self):
        self.config = self.get_user_input()

        # Final confirmation token
        today = datetime.now().strftime("%Y-%m-%d")
        expected_token = f"START-{self.config.relay_target}-{today}"
        print(f"\n--- Final Consent Token ---")
        print(f"You MUST type exactly: {expected_token}")
        user_token = input("Type the token: ").strip()
        if user_token != expected_token:
            print("❌ Consent token mismatch! Aborting.")
            sys.exit(1)

        # Run simulation
        self.run_attack()

if __name__ == "__main__":
    sim = ForcedAuthSimulator()
    sim.run()
