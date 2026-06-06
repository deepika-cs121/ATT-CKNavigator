import argparse
import csv
import logging
from datetime import datetime, timedelta
import random

from faker import Faker
import pandas as pd

try:
    import bcrypt
    BCRYPT_AVAILABLE = True
except Exception:
    BCRYPT_AVAILABLE = False

LOG_FILE = "generate_test_identities.log"

logger = logging.getLogger("gen_identities")
logger.setLevel(logging.INFO)
fh = logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8")
formatter = logging.Formatter("%(asctime)s\t%(levelname)s\t%(message)s")
fh.setFormatter(formatter)
logger.addHandler(fh)


def random_join_date(years_back=10, faker_obj=None):
    if faker_obj:
        start = datetime.now() - timedelta(days=365 * years_back)
        end = datetime.now()
        dt = faker_obj.date_between(start_date=start, end_date=end)
        return dt.isoformat()
    else:
        now = datetime.now()
        past = now - timedelta(days=365 * years_back)
        rand = past + timedelta(seconds=random.randint(0, int((now - past).total_seconds())))
        return rand.date().isoformat()


def hash_password(plain_text: str) -> str:
    if not BCRYPT_AVAILABLE:
        raise RuntimeError("bcrypt not available; install it with `pip install bcrypt`")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(plain_text.encode("utf-8"), salt).decode("utf-8")


def generate_rows(count=100, locale="en_US", include_hash=False, fake_password_pattern="TestPass{n}"):
    fake = Faker(locale)
    rows = []
    for i in range(1, count + 1):
        name = fake.name()
        company = fake.company()
        local_part = "".join([c.lower() for c in name if c.isalpha() or c == " "]).replace(" ", ".")
        domain = "".join([c.lower() for c in company if c.isalpha() or c == " "]).replace(" ", "") + ".test"
        email = f"{local_part}@{domain}"
        job = fake.job()
        phone = fake.phone_number()
        join_date = random_join_date(years_back=12, faker_obj=fake)
        entry = {
            "id": i,
            "full_name": name,
            "email": email,
            "job_title": job,
            "company": company,
            "phone": phone,
            "join_date": join_date
        }
        if include_hash:
            plain = fake_password_pattern.format(n=i)
            try:
                entry["password_hash"] = hash_password(plain)
            except RuntimeError:
                entry["password_hash"] = "" 
        rows.append(entry)
    return rows


def save_csv(rows, outpath):
    df = pd.DataFrame(rows)
    df.to_csv(outpath, index=False)
    return len(df)


def main():
    ap = argparse.ArgumentParser(description="Generate synthetic identity CSV for testing.")
    ap.add_argument("--count", "-n", type=int, default=200, help="Number of synthetic records to generate.")
    ap.add_argument("--out", "-o", default="fake_identities.csv", help="Output CSV path.")
    ap.add_argument("--locale", "-l", default="en_US", help="Faker locale (e.g. en_US, en_IN).")
    ap.add_argument("--hash-passwords", action="store_true",
                    help="Include bcrypt-hashed fake passwords in 'password_hash' column.")
    ap.add_argument("--password-pattern", default="TestPass{n}",
                    help="Pattern for generated plaintext (only used to derive the hash). Use {n} for index.")
    args = ap.parse_args()

    if args.hash_passwords and not BCRYPT_AVAILABLE:
        logger.warning("bcrypt not installed; continuing without password hashes.")
        print("Warning: bcrypt not installed. To enable password hashing, run: pip install bcrypt")

    logger.info(f"Run start: count={args.count} out={args.out} locale={args.locale} hash_passwords={args.hash_passwords}")

    rows = generate_rows(count=args.count, locale=args.locale,
                         include_hash=args.hash_passwords, fake_password_pattern=args.password_pattern)
    saved = save_csv(rows, args.out)

    logger.info(f"Run complete: saved={saved} rows to {args.out}")
    print(f"Saved {saved} synthetic records to {args.out}. Audit log: {LOG_FILE}")


if __name__ == "__main__":
    main()