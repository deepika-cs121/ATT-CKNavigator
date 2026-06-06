import os
import argparse
from datetime import datetime
import sys

OUTBOX_DIR = "outbox"
LOG_FILE = "Spearphishing_log.txt"

TEMPLATES = {
    "basic": {
        "subject": "Important: Update Your Account",
        "body": """
            <h2>Account update required</h2>
            <p>Dear {name},</p>
            <p>We noticed unusual activity on your account. Please <a href="#">review your account</a> immediately.</p>
            <p>Regards,<br/>Security Team</p>
        """
    },
    "delivery": {
        "subject": "Delivery Notice: Action Needed",
        "body": """
            <h2>Delivery problem</h2>
            <p>Dear {name},</p>
            <p>Our courier was unable to deliver a package. Please <a href="#">confirm your address</a>.</p>
            <p>Thanks,<br/>Delivery Support</p>
        """
    }
}

os.makedirs(OUTBOX_DIR, exist_ok=True)

def now_ts():
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"

def write_log(event_type, recipient, template, filename, notes=""):
    line = f"[{now_ts()}] event={event_type} recipient={recipient} template={template} file={filename} notes=\"{notes}\"\n"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line)

def generate_email(recipient, template_name, name_hint=None, extra_tag=""):
    template = TEMPLATES.get(template_name)
    if not template:
        raise ValueError("Unknown template: " + template_name)
    local_name = name_hint or recipient.split("@")[0].replace(".", " ").title()
    html_body = template["body"].format(name=local_name)
    subject = template["subject"]
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
    safe_recipient = recipient.split("@")[0]
    filename = f"{safe_recipient}_{timestamp}.html"
    path = os.path.join(OUTBOX_DIR, filename)
    html = f"""<!doctype html>
<html>
<head><meta charset="utf-8"><title>{subject}</title></head>
<body>
<p><strong>Subject:</strong> {subject}</p>
{html_body}
<hr/>
<p style="font-size:small;color:gray;">This is a training copy. Do not consider this a real email.</p>
</body>
</html>
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    write_log("generated", recipient, template_name, path, notes=extra_tag)
    print(f"[+] Generated: {path}")
    return path

def simulate_open(file_path, actor="trainee@example.com", note="simulated open"):
    if not os.path.exists(file_path):
        raise FileNotFoundError(file_path)
    write_log("opened", actor, os.path.basename(file_path), file_path, notes=note)
    print(f"[+] Simulated open recorded for {file_path}")

def list_outbox():
    files = sorted(os.listdir(OUTBOX_DIR))
    if not files:
        print("[*] Outbox empty")
    for f in files:
        print(f)

def interactive_menu():
    while True:
        print("\nSAFE Spearphishing")
        print("1) Generate mock email")
        print("2) Simulate open")
        print("3) List outbox")
        print("4) Show latest log lines")
        print("5) Exit")
        choice = input("Choose (1-5): ").strip()
        if choice == "1":
            recipient = input("Recipient (email): ").strip()
            print("Templates:", ", ".join(TEMPLATES.keys()))
            template = input("Template (default: basic): ").strip() or "basic"
            name = input("Display name (optional): ").strip() or None
            tag = input("Tag/notes (optional): ").strip() or ""
            try:
                generate_email(recipient, template, name, tag)
            except Exception as e:
                print("Error:", e)
        elif choice == "2":
            filep = input("Path to HTML file (e.g. outbox/xxx.html): ").strip()
            actor = input("Actor who 'opened' it (default trainee@example.com): ").strip() or "trainee@example.com"
            note = input("Note (optional): ").strip() or "simulated open"
            try:
                simulate_open(filep, actor, note)
            except Exception as e:
                print("Error:", e)
        elif choice == "3":
            list_outbox()
        elif choice == "4":
            try:
                with open(LOG_FILE, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    for ln in lines[-20:]:
                        print(ln.rstrip())
            except FileNotFoundError:
                print("[*] No log found yet.")
        elif choice == "5":
            print("Bye.")
            break
        else:
            print("Invalid choice.")

def parse_args():
    p = argparse.ArgumentParser(add_help=True)
    sub = p.add_subparsers(dest="cmd")

    g = sub.add_parser("generate")
    g.add_argument("--recipient", required=True)
    g.add_argument("--template", choices=list(TEMPLATES.keys()), default="basic")
    g.add_argument("--name", help="Display name to use in template")
    g.add_argument("--tag", default="", help="Optional tag to add to log")

    o = sub.add_parser("simulate-open")
    o.add_argument("--file", required=True, help="Path to local HTML file from outbox")
    o.add_argument("--actor", default="trainee@example.com", help="Who 'opened' it")
    o.add_argument("--note", default="simulated open")

    l = sub.add_parser("list")
    return p.parse_args()

def main():
    args = parse_args()
    if not args.cmd:
        interactive_menu()
        return

    if args.cmd == "generate":
        generate_email(args.recipient, args.template, name_hint=args.name, extra_tag=args.tag)
    elif args.cmd == "simulate-open":
        simulate_open(args.file, actor=args.actor, note=args.note)
    elif args.cmd == "list":
        list_outbox()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted by user. Exiting.")
        sys.exit(0)
