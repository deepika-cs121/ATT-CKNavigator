import argparse
import os
import json
import sqlite3
import datetime
import uuid
import hashlib
import hmac
import logging
from logging.handlers import RotatingFileHandler
from typing import Optional, Dict, Any, List
import csv
import getpass
import smtplib
from email.message import EmailMessage

APP_NAME = "compromise_account"
DEFAULT_LOG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "incident_logs"))
os.makedirs(DEFAULT_LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(DEFAULT_LOG_DIR, "events.jsonl")
DB_FILE = os.path.join(DEFAULT_LOG_DIR, "events.db")
MAX_LOG_BYTES = 10 * 1024 * 1024
BACKUP_COUNT = 5

SECRET_KEY = os.getenv("COMP_ACCT_SECRET", None)

CONFIG = {
    "smtp": {
        "enabled": False,
        "host": "smtp.example.com",
        "port": 587,
        "username": "alert@example.com",
        "password": None,
        "from_addr": "alert@example.com",
        "to_addrs": ["you@example.com"]
    }
}
logger = logging.getLogger(APP_NAME)
logger.setLevel(logging.INFO)
json_handler = RotatingFileHandler(LOG_FILE, maxBytes=MAX_LOG_BYTES, backupCount=BACKUP_COUNT, encoding="utf-8")
json_handler.setFormatter(logging.Formatter('%(message)s')) 
logger.addHandler(json_handler)
console = logging.StreamHandler()
console.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
logger.addHandler(console)

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id TEXT PRIMARY KEY,
            account_type TEXT,
            account_id TEXT,
            timestamp TEXT,
            activity TEXT,
            ip TEXT,
            metadata TEXT,
            notes TEXT,
            hmac TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def insert_event_db(event: Dict[str,Any]):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO events (id, account_type, account_id, timestamp, activity, ip, metadata, notes, hmac, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        event["id"], event["account_type"], event["account_id"], event["timestamp"],
        event["activity"], event.get("ip"), json.dumps(event.get("metadata", {})),
        event.get("notes", ""), event.get("hmac", ""), event["created_at"]
    ))
    conn.commit()
    conn.close()

def query_events(account_id: str) -> List[Dict[str,Any]]:
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT id, account_type, account_id, timestamp, activity, ip, metadata, notes, hmac, created_at FROM events WHERE account_id = ? ORDER BY timestamp", (account_id,))
    rows = cur.fetchall()
    conn.close()
    out = []
    for r in rows:
        out.append({
            "id": r[0], "account_type": r[1], "account_id": r[2], "timestamp": r[3],
            "activity": r[4], "ip": r[5], "metadata": json.loads(r[6]) if r[6] else {},
            "notes": r[7], "hmac": r[8], "created_at": r[9]
        })
    return out

def get_secret_key() -> bytes:
    global SECRET_KEY
    if SECRET_KEY:
        return SECRET_KEY.encode("utf-8")
    k = os.getenv("COMP_ACCT_SECRET") or os.getenv("COMPROMISE_ACCOUNT_SECRET")
    if k:
        SECRET_KEY = k
        return SECRET_KEY.encode("utf-8")
    tmp = hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()
    SECRET_KEY = tmp
    logger.warning("No persistent secret key set. Using ephemeral key for this session only. "
                   "Set COMP_ACCT_SECRET env var to enable persistent tamper-evidence.")
    return SECRET_KEY.encode("utf-8")

def compute_hmac_event(event: Dict[str,Any]) -> str:
    payload = "|".join([
        event["id"],
        event["account_type"],
        event["account_id"],
        event["timestamp"],
        event["activity"],
        event.get("ip") or "",
        json.dumps(event.get("metadata", {}), sort_keys=True, separators=(",", ":"))
    ])
    key = get_secret_key()
    mac = hmac.new(key, payload.encode("utf-8"), hashlib.sha256).hexdigest()
    return mac

def make_event(account_type: str, account_id: str, activity: str, timestamp: Optional[str]=None,
               ip: Optional[str]=None, metadata: Optional[Dict[str,Any]]=None, notes: Optional[str]=None) -> Dict[str,Any]:
    if timestamp is None:
        timestamp = datetime.datetime.utcnow().isoformat() + "Z"
    event = {
        "id": str(uuid.uuid4()),
        "account_type": account_type,
        "account_id": account_id,
        "timestamp": timestamp,
        "activity": activity,
        "ip": ip,
        "metadata": metadata or {},
        "notes": notes or "",
        "created_at": datetime.datetime.utcnow().isoformat() + "Z"
    }
    event["hmac"] = compute_hmac_event(event)
    return event

def log_event(event: Dict[str,Any]):
    logger.info(json.dumps(event, ensure_ascii=False))
    insert_event_db(event)

def ingest_cloudtrail_json(path: str):
    """
    Ingest CloudTrail JSON (list of events or newline JSON) and extract useful fields.
    This is an example: adapt per your export format.
    """
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()
    try:
        data = json.loads(raw)
    except Exception:
        data = []
        for ln in raw.splitlines():
            ln = ln.strip()
            if not ln: continue
            try:
                data.append(json.loads(ln))
            except Exception:
                pass
    count = 0
    for rec in data:
        at = rec.get("eventTime") or rec.get("eventTimestamp")
        ip = rec.get("sourceIPAddress") or rec.get("callerIpAddress")
        activity = rec.get("eventName") or rec.get("eventType") or "cloudtrail-event"
        acct = rec.get("userIdentity", {}).get("arn") or rec.get("recipientAccountId") or "unknown"
        metadata = {k: rec.get(k) for k in ("eventSource", "requestParameters", "userAgent") if k in rec}
        e = make_event(account_type="cloud", account_id=str(acct), activity=activity, timestamp=at, ip=ip, metadata=metadata, notes="Ingested from CloudTrail export")
        log_event(e)
        count += 1
    print(f"Ingested {count} CloudTrail events from {path}")

def ingest_csv(path: str, mapping: Dict[str,str]=None, account_type: str="email"):
    mapping = mapping or {}
    with open(path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        count = 0
        for row in reader:
            acct = row.get(mapping.get("account_id","account_id")) or row.get(mapping.get("email","email")) or "unknown"
            ts = row.get(mapping.get("timestamp","timestamp")) or datetime.datetime.utcnow().isoformat()+"Z"
            act = row.get(mapping.get("activity","activity")) or "ingested-event"
            ip = row.get(mapping.get("ip","ip")) or None
            notes = row.get(mapping.get("notes","notes")) or "Ingested from CSV"
            meta = {k: row.get(k) for k in row.keys()}
            e = make_event(account_type=account_type, account_id=acct, activity=act, timestamp=ts, ip=ip, metadata=meta, notes=notes)
            log_event(e)
            count += 1
    print(f"Ingested {count} rows from {path}")

def export_report(account_id: str, out_path: str):
    evts = query_events(account_id)
    if not evts:
        raise ValueError("No events for account: " + account_id)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(f"Incident Report - account: {account_id}\n")
        f.write(f"Generated: {datetime.datetime.utcnow().isoformat()}Z\n")
        f.write("="*72 + "\n\n")
        for e in evts:
            f.write(f"Event ID: {e['id']}\n")
            f.write(f"Account Type: {e['account_type']}\n")
            f.write(f"Timestamp: {e['timestamp']}\n")
            f.write(f"Activity: {e['activity']}\n")
            f.write(f"IP: {e['ip']}\n")
            f.write(f"Notes: {e['notes']}\n")
            f.write(f"Metadata: {json.dumps(e.get('metadata',{}), ensure_ascii=False)}\n")
            f.write(f"HMAC: {e.get('hmac')}\n")
            f.write("-"*72 + "\n")
    print("Exported report to", out_path)


def send_alert(subject: str, body: str):
    if not CONFIG.get("smtp", {}).get("enabled"):
        logger.info("SMTP not enabled in CONFIG; skipping alert")
        return
    smtp = CONFIG["smtp"]
    passwd = smtp.get("password") or os.getenv("COMP_ACCT_SMTP_PASS")
    if not passwd:
        passwd = getpass.getpass("SMTP password: ")
    msg = EmailMessage()
    msg["From"] = smtp["from_addr"]
    msg["To"] = ", ".join(smtp["to_addrs"])
    msg["Subject"] = subject
    msg.set_content(body)
    with smtplib.SMTP(smtp["host"], smtp["port"]) as s:
        s.starttls()
        s.login(smtp["username"], passwd)
        s.send_message(msg)
    logger.info("Alert sent via SMTP")

def interactive_prompt():
    print("Interactive incident logger. Press Enter to cancel a prompt.")
    while True:
        acct_type = input("Account type (email/cloud/social/other) [email]: ").strip() or "email"
        acct = input("Account identifier (email or username): ").strip()
        if not acct:
            print("No account entered, exiting.")
            break
        activity = input("Activity (short): ").strip() or "suspicious-activity"
        ip = input("IP (optional): ").strip() or None
        ts = input("Timestamp (ISO, optional, Enter for now): ").strip() or None
        notes = input("Notes (optional): ").strip() or ""
        meta_input = input("Metadata as JSON (optional): ").strip()
        meta = {}
        if meta_input:
            try:
                meta = json.loads(meta_input)
            except Exception as e:
                print("Failed to parse metadata JSON:", e)
                meta = {}
        e = make_event(account_type=acct_type, account_id=acct, activity=activity, timestamp=ts, ip=ip, metadata=meta, notes=notes)
        log_event(e)
        print("Logged event id:", e["id"])
        alert = input("Send SMTP alert for this event? (y/N): ").strip().lower()
        if alert == "y":
            send_alert(subject=f"[Incident] {acct} {activity}", body=json.dumps(e, indent=2))
        cont = input("Add another? (Y/n): ").strip().lower()
        if cont == "n":
            break

def parse_args():
    p = argparse.ArgumentParser(prog="compromise_account", description="Defensive incident logger for suspected compromised accounts")
    sub = p.add_subparsers(dest="cmd")

    add = sub.add_parser("add", help="Add a single event")
    add.add_argument("--type", required=True, choices=["email","cloud","social","other"], help="Account type")
    add.add_argument("--id", required=True, help="Account identifier (email or username)")
    add.add_argument("--activity", required=True, help="Short activity description")
    add.add_argument("--ip", required=False, help="Observed IP address")
    add.add_argument("--timestamp", required=False, help="ISO timestamp")
    add.add_argument("--notes", required=False, help="Notes")
    add.add_argument("--meta", required=False, help="JSON string for metadata")
    add.add_argument("--alert", action="store_true", help="Send SMTP alert (if configured)")

    show = sub.add_parser("show", help="Show events for an account")
    show.add_argument("--id", required=True, help="Account identifier")

    export = sub.add_parser("export-report", help="Export report for an account")
    export.add_argument("--id", required=True, help="Account identifier")
    export.add_argument("--out", required=True, help="Output path")

    ingest = sub.add_parser("ingest", help="Ingest provider export")
    ingest.add_argument("--source", required=True, choices=["cloudtrail","csv","custom"], help="Source format")
    ingest.add_argument("--file", required=True, help="Path to file")
    ingest.add_argument("--mapping", required=False, help="If CSV, provide JSON mapping for columns")

    return p.parse_args()

def main():
    init_db()
    args = parse_args()
    if not args.cmd:
        interactive_prompt()
        return

    if args.cmd == "add":
        meta = {}
        if getattr(args, "meta", None):
            try:
                meta = json.loads(args.meta)
            except Exception as e:
                print("Failed to parse --meta JSON:", e)
                return
        event = make_event(account_type=args.type, account_id=args.id, activity=args.activity, timestamp=args.timestamp, ip=args.ip, metadata=meta, notes=args.notes)
        log_event(event)
        print("Logged event id:", event["id"])
        if getattr(args, "alert", False):
            send_alert(subject=f"[Incident] {event['account_id']} - {event['activity']}", body=json.dumps(event, indent=2))
    elif args.cmd == "show":
        evts = query_events(args.id)
        print(json.dumps(evts, indent=2, ensure_ascii=False))
    elif args.cmd == "export-report":
        try:
            export_report(args.id, args.out)
        except Exception as e:
            print("Error exporting report:", e)
    elif args.cmd == "ingest":
        if args.source == "cloudtrail":
            ingest_cloudtrail_json(args.file)
        elif args.source == "csv":
            mapping = {}
            if args.mapping:
                try:
                    mapping = json.loads(args.mapping)
                except Exception as e:
                    print("Failed to parse mapping JSON:", e)
                    return
            ingest_csv(args.file, mapping=mapping)
        else:
            print("Custom ingest not implemented; provide conversion logic.")

if __name__ == "__main__":
    main()
