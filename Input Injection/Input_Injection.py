import argparse
import base64
import binascii
import json
import logging
import os
import random
import sqlite3
import string
import sys
import time
from datetime import datetime
from logging.handlers import RotatingFileHandler
from typing import Any, Dict, List, Optional

try:
    import requests
except Exception:
    requests = None

LOG_DIR = "logs"
DB_FILE = os.path.join(LOG_DIR, "injection_logs.db")
LOG_FILE = os.path.join(LOG_DIR, "injection.log")
os.makedirs(LOG_DIR, exist_ok=True)

logger = logging.getLogger("input_injector")
logger.setLevel(logging.DEBUG)
handler = RotatingFileHandler(LOG_FILE, maxBytes=2_000_000, backupCount=5, encoding="utf-8")
formatter = logging.Formatter("[%(asctime)s] %(levelname)s %(message)s", "%Y-%m-%d %H:%M:%S")
handler.setFormatter(formatter)
logger.addHandler(handler)

sh = logging.StreamHandler(sys.stdout)
sh.setLevel(logging.INFO)
sh.setFormatter(formatter)
logger.addHandler(sh)

def init_db(db_path: str = DB_FILE):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        """CREATE TABLE IF NOT EXISTS attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            payload_type TEXT,
            encoder TEXT,
            payload TEXT,
            target_url TEXT,
            http_status INTEGER,
            http_reason TEXT,
            response_body TEXT
        )"""
    )
    conn.commit()
    return conn


def save_attempt(
    conn: sqlite3.Connection,
    payload_type: str,
    encoder: str,
    payload: str,
    target_url: Optional[str],
    http_status: Optional[int],
    http_reason: Optional[str],
    response_body: Optional[str],
):
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO attempts (timestamp, payload_type, encoder, payload, target_url, http_status, http_reason, response_body) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (datetime.utcnow().isoformat(), payload_type, encoder, payload, target_url, http_status, http_reason, response_body),
    )
    conn.commit()


def random_string(length: int = 16):
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_payloads(mode: str = "mixed") -> List[Dict[str, Any]]:
    payloads = []

    standard_examples = [
        ("plain_text", "Hello, this is a normal message."),
        ("username", "alice"),
        ("email", "user@example.com"),
        ("number", "12345"),
        ("script_like", "<script>alert('x')</script>"),
        ("sql_like", "SELECT * FROM users WHERE id = 1;"),
    ]

    nonstandard_examples = [
        ("long_string", "A" * 5000),
        ("null_bytes", "abc\x00\x00\x00def"),
        ("unicode_emoji", "😊🚀 Привет こんにちは"),
        ("unicode_combining", "e\u0301 (e with acute combining)"),
        ("non_printables", "".join(chr(i) for i in range(0, 32))),  
        ("hex_binary", binascii.hexlify(b"\x00\xff\x10\x80").decode()),
    ]

    generated = [
        ("rand_short", random_string(12)),
        ("rand_long", random_string(300)),
    ]

    if mode == "standard":
        pool = standard_examples + generated[:1]
    elif mode == "nonstandard":
        pool = nonstandard_examples + generated[1:]
    else:
        pool = standard_examples + nonstandard_examples + generated

    for t, raw in pool:
        payloads.append({"type": t, "raw": raw})
    return payloads


def encode_payload(raw: str, encoder: str) -> str:
    if encoder == "identity":
        return raw
    if encoder == "base64":
        return base64.b64encode(raw.encode("utf-8", errors="surrogateescape")).decode("ascii")
    if encoder == "hex":
        return binascii.hexlify(raw.encode("utf-8", errors="surrogateescape")).decode()
    if encoder == "url":
        try:
            from urllib.parse import quote

            return quote(raw, safe="")
        except Exception:
            return raw
    if encoder == "unicode_escape":
        return raw.encode("unicode_escape").decode()
    return raw


def send_payload(url: str, payload: str, headers: Dict[str, str] = None, timeout: float = 5.0):
    if requests is None:
        raise RuntimeError("requests library not installed. Install with: pip install requests")
    headers = headers or {"Content-Type": "application/json"}
    try:
        resp = requests.post(url, json={"input": payload}, headers=headers, timeout=timeout)
        return resp.status_code, resp.reason, (resp.text[:5000] if resp.text else "")
    except Exception as e:
        logger.debug("HTTP error: %s", e)
        return None, None, f"ERROR: {e}"


def main():
    p = argparse.ArgumentParser(description="Input injector (testing) with logging")
    p.add_argument("--count", type=int, default=20, help="How many attempts to make (will cycle payloads)")
    p.add_argument("--mode", choices=["standard", "nonstandard", "mixed"], default="mixed")
    p.add_argument("--encoders", nargs="+", default=["identity", "base64", "hex", "url", "unicode_escape"])
    p.add_argument("--target", type=str, default=None, help="Target URL to POST to (e.g. http://127.0.0.1:5000/process)")
    p.add_argument("--send", action="store_true", help="Actually send requests. If omitted, runs in dry-run mode.")
    p.add_argument("--delay", type=float, default=0.1, help="Delay between attempts (seconds)")
    p.add_argument("--quiet", action="store_true", help="Reduce console output")
    args = p.parse_args()

    if args.send and not args.target:
        logger.error("You requested --send but did not supply --target. Exiting.")
        sys.exit(1)

    if args.send and requests is None:
        logger.error("requests library missing. Install with: pip install requests")
        sys.exit(1)

    conn = init_db()

    payload_templates = generate_payloads(mode=args.mode)
    if not args.quiet:
        logger.info("Generated %d payload templates (mode=%s)", len(payload_templates), args.mode)

    total = args.count
    attempts = 0
    while attempts < total:
        template = random.choice(payload_templates)
        encoder = random.choice(args.encoders)
        raw = template["raw"]

        if random.random() < 0.25:
            raw = f"{random_string(6)}-{raw}-{random_string(4)}"

        encoded = encode_payload(raw, encoder)

        record = {
            "attempt_no": attempts + 1,
            "payload_type": template["type"],
            "encoder": encoder,
            "raw_preview": (raw[:200] + "..." if len(raw) > 200 else raw),
            "encoded_preview": (encoded[:200] + "..." if len(encoded) > 200 else encoded),
            "target": args.target,
        }

        if not args.quiet:
            logger.info("Attempt %d/%d: type=%s encoder=%s target=%s",
                        attempts + 1, total, template["type"], encoder, args.target or "DRY-RUN")

        logger.debug("Raw payload (first 300 chars): %s", record["raw_preview"])
        logger.debug("Encoded payload (first 300 chars): %s", record["encoded_preview"])

        http_status = None
        http_reason = None
        response_body = None
        if args.send:
            status, reason, resp_text = send_payload(args.target, encoded)
            http_status, http_reason, response_body = status, reason, resp_text
            if status is not None:
                logger.info("HTTP %s %s", status, reason)
            else:
                logger.warning("Request failed: %s", resp_text)

        try:
            save_attempt(conn, template["type"], encoder, encoded, args.target, http_status, http_reason, response_body)
        except Exception as e:
            logger.exception("Failed to write to DB: %s", e)

        attempts += 1
        time.sleep(max(0.0, args.delay))

    logger.info("Completed %d attempts. Logfile: %s  DB: %s", total, LOG_FILE, DB_FILE)


if __name__ == "__main__":
    main()

