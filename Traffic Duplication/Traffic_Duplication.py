from http.server import BaseHTTPRequestHandler, HTTPServer, SimpleHTTPRequestHandler
import socketserver
import argparse
import threading
import socket
import time
import json
import os
import sys
import signal
from urllib.parse import urljoin, urlparse
from datetime import datetime

try:
    import requests
except Exception as e:
    print("[!] This script requires the 'requests' library. Install with: pip install requests", file=sys.stderr)
    raise

PRIMARY_BASE = os.environ.get("PRIMARY_BASE", "http://localhost:9000")
SECONDARY_BASE = os.environ.get("SECONDARY_BASE", "http://localhost:9001")
REQUEST_TIMEOUT = float(os.environ.get("DUP_REQ_TIMEOUT", "6.0"))
LOGFILE = os.environ.get("DUP_LOGFILE", "dup_logs.jsonl")

def ensure_log_dir(path):
    d = os.path.dirname(os.path.abspath(path))
    if d and not os.path.exists(d):
        os.makedirs(d, exist_ok=True)

def write_jsonl_line(path, obj):
    line = json.dumps(obj, separators=(",", ":"), default=str)
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(line + "\n")
            f.flush()
            try:
                os.fsync(f.fileno())
            except Exception:
                pass
    except Exception as e:
        print(f"[!] Failed writing log to {path}: {e}", file=sys.stderr)
    print(line, flush=True)

def now_ts():
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

def parse_base(base_url):
    p = urlparse(base_url)
    host = p.hostname or "localhost"
    port = p.port or (80 if p.scheme == "http" else 443)
    return host, port

def is_port_open(host, port, timeout=0.5):
    try:
        with socket.create_connection((host, port), timeout):
            return True
    except Exception:
        return False

class TinyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = f"dummy upstream on {self.server.server_address[0]}:{self.server.server_address[1]}\n".encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        try:
            self.wfile.write(body)
        except BrokenPipeError:
            pass

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0) or 0)
        except Exception:
            length = 0
        if length:
            try:
                _ = self.rfile.read(length)
            except Exception:
                pass
        body = b"OK\n"
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        try:
            self.wfile.write(body)
        except BrokenPipeError:
            pass

def start_dummy_server(bind_host, bind_port):
    class ThreadingHTTP(socketserver.ThreadingMixIn, HTTPServer):
        daemon_threads = True
    try:
        srv = ThreadingHTTP((bind_host, bind_port), TinyHandler)
    except Exception as e:
        print(f"[!] Could not start dummy server on {bind_host}:{bind_port}: {e}", file=sys.stderr)
        return None
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    print(f"[+] Tiny dummy upstream started on {bind_host}:{bind_port}")
    return srv

class ThreadingHTTP(socketserver.ThreadingMixIn, HTTPServer):
    daemon_threads = True

class DupHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _read_body(self):
        try:
            length = int(self.headers.get("Content-Length", 0) or 0)
        except Exception:
            length = 0
        return self.rfile.read(length) if length else b""

    def _filter_headers(self):
        hop = {"connection","keep-alive","proxy-authenticate","proxy-authorization","te","trailers","transfer-encoding","upgrade"}
        return {k:v for k,v in self.headers.items() if k.lower() not in hop}

    def _forward_request(self, base, method, path, headers, body):
        url = urljoin(base, path)
        start = time.time()
        try:
            r = requests.request(method=method, url=url, headers=headers, data=body, timeout=REQUEST_TIMEOUT, allow_redirects=False)
            return {"ok": True, "status": r.status_code, "elapsed_s": round(time.time()-start, 4), "body_snippet": (r.text or "")[:200]}
        except Exception as e:
            err = str(e)
            print(f"[!] Forward error to {base}: {err}", file=sys.stderr)
            return {"ok": False, "status": 0, "elapsed_s": round(time.time()-start, 4), "error": err, "body_snippet": ""}

    def _reply_to_client(self, primary_res):
        if primary_res.get("ok"):
            status = primary_res.get("status", 200)
            body = primary_res.get("body_snippet","").encode("utf-8")
        else:
            status = 502
            body = ("Upstream error: " + primary_res.get("error","")).encode("utf-8")
        try:
            self.send_response(status)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(body)
        except Exception as e:
            print(f"[!] Failed writing to client: {e}", file=sys.stderr)

    def _handle_common(self):
        method = self.command
        path = self.path
        client_ip = self.client_address[0]
        body = self._read_body()
        headers = self._filter_headers()
        ts = now_ts()

        print(f"[>] {client_ip} {method} {path}", flush=True)

        primary_res = self._forward_request(PRIMARY_BASE, method, path, headers, body)
        primary_entry = {
            "timestamp": ts,
            "role": "primary",
            "method": method,
            "path": path,
            "client": client_ip,
            "upstream": PRIMARY_BASE,
            "status": primary_res.get("status", 0),
            "error": primary_res.get("error", ""),
            "elapsed_ms": int(primary_res.get("elapsed_s", 0)*1000),
            "body_snippet": primary_res.get("body_snippet","")
        }
        write_jsonl_line(LOGFILE, primary_entry)

        def do_duplicate():
            sec_res = self._forward_request(SECONDARY_BASE, method, path, headers, body)
            sec_entry = {
                "timestamp": now_ts(),
                "role": "secondary",
                "method": method,
                "path": path,
                "client": client_ip,
                "upstream": SECONDARY_BASE,
                "status": sec_res.get("status", 0),
                "error": sec_res.get("error",""),
                "elapsed_ms": int(sec_res.get("elapsed_s",0)*1000),
                "body_snippet": sec_res.get("body_snippet","")
            }
            write_jsonl_line(LOGFILE, sec_entry)
        threading.Thread(target=do_duplicate, daemon=True).start()

        self._reply_to_client(primary_res)

    def do_GET(self): self._handle_common()
    def do_POST(self): self._handle_common()
    def do_PUT(self): self._handle_common()
    def do_DELETE(self): self._handle_common()
    def do_PATCH(self): self._handle_common()
    def log_message(self, fmt, *args):
        print(f"{self.client_address[0]} - {fmt%args}", flush=True)

def run(listen="127.0.0.1", port=8080, logfile="dup_logs.jsonl", auto_dummy=True, selftest=True):
    global LOGFILE, PRIMARY_BASE, SECONDARY_BASE
    LOGFILE = logfile
    ensure_log_dir(LOGFILE)

    print(f"[+] Duplicator starting on http://{listen}:{port}")
    print(f"[+] Primary: {PRIMARY_BASE}")
    print(f"[+] Secondary: {SECONDARY_BASE}")
    print(f"[+] Logging to: {os.path.abspath(LOGFILE)}")

    if auto_dummy:
        for label, base in (("primary", PRIMARY_BASE), ("secondary", SECONDARY_BASE)):
            host, prt = parse_base = (lambda u: (urlparse(u).hostname or "localhost", urlparse(u).port or (80 if urlparse(u).scheme=="http" else 443)))(base)
            if host in ("localhost", "127.0.0.1", "::1"):
                if not is_port_open(host, prt, timeout=0.5):
                    try:
                        start_dummy_server(host, prt)
                    except Exception as e:
                        print(f"[!] Failed to start dummy {label}: {e}", file=sys.stderr)

    try:
        srv = ThreadingHTTP((listen, port), DupHandler)
    except Exception as e:
        print(f"[!] Failed to bind duplicator to {listen}:{port}: {e}", file=sys.stderr)
        sys.exit(1)

    def _sigint(signum, frame):
        print("\n[+] Shutting down...", flush=True)
        try:
            srv.shutdown()
        except Exception:
            pass
        sys.exit(0)
    signal.signal(signal.SIGINT, _sigint)

    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()

    if selftest:
        time.sleep(0.2)
        test_url = f"http://{listen}:{port}/"
        try:
            print(f"[+] Performing self-test request to {test_url}")
            import requests as _req
            r = _req.get(test_url, timeout=3)
            print(f"[+] Self-test response: {r.status_code}")
        except Exception as e:
            print(f"[!] Self-test failed: {e}", file=sys.stderr)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        _sigint(None, None)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HTTP traffic duplicator (lab-only).")
    parser.add_argument("--listen", default="127.0.0.1", help="IP to bind (default 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind (default 8080)")
    parser.add_argument("--logfile", default=None, help="Path to JSONL logfile (default dup_logs.jsonl)")
    parser.add_argument("--no-auto-dummy", action="store_true", help="Don't auto-start dummy upstreams on localhost")
    parser.add_argument("--no-selftest", action="store_true", help="Disable self-test request at startup")
    args = parser.parse_args()

    logfile = args.logfile if args.logfile else LOGFILE
    run(args.listen, args.port, logfile, auto_dummy=not args.no_auto_dummy, selftest=not args.no_selftest)
