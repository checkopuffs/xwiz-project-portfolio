import json
import os
import re
import socket
import sqlite3
import threading
import time
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from pathlib import Path
from urllib.request import Request, urlopen

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
ALLOWED_ID = int(os.environ["TELEGRAM_ALLOWED_USER_ID"])
MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:1b")
API = f"https://api.telegram.org/bot{TOKEN}/"
DB_FILE = os.getenv("XWIZ_DB_FILE", "/data/xwiz-memory.db")
TIMEZONE = os.getenv("XWIZ_TIMEZONE", "America/Los_Angeles")
LOCAL_ZONE = ZoneInfo(TIMEZONE)

# Optional, fixed, read-only TCP targets supplied by the operator.
# Each item: [key, display name, host/IP, TCP port, service].
# Avoid checking unknown or third-party systems.
def load_monitor_targets():
    targets = json.loads(os.getenv("XWIZ_MONITOR_TARGETS", "[]"))
    if not isinstance(targets, list):
        raise ValueError("XWIZ_MONITOR_TARGETS must be a JSON list")
    clean = []
    for entry in targets:
        if (not isinstance(entry, list) or len(entry) != 5
                or not isinstance(entry[3], int) or not 1 <= entry[3] <= 65535
                or any(not isinstance(v, str) or not v.strip() for i, v in enumerate(entry) if i != 3)):
            raise ValueError("Each monitor target must be [key, label, host, port, service]")
        clean.append(tuple(entry))
    return tuple(clean)

MONITOR_ENDPOINTS = load_monitor_targets()
MONITOR_INTERVAL_SECONDS = 60
MONITOR_DOWN_FAILURES = 3
MONITOR_RECOVERY_SUCCESSES = 2

SYSTEM = """You are XWiz AI, a friendly and practical homelab assistant.
Never invent live system state or claim to have performed actions.
This assistant cannot control servers, read private infrastructure, or message
other people unless a specifically authorized integration implements it.
For TCP connectivity checks the user can send /status.
For automatic outage notifications use /monitor on.
For reminders use /remind tomorrow 6pm followed by the task.
Never claim a reminder was saved unless the Telegram bot confirms it.
"""


def request_json(url, payload, timeout=45):
    req = Request(url, data=json.dumps(payload).encode(),
                  headers={"Content-Type": "application/json"})
    with urlopen(req, timeout=timeout) as response:
        return json.load(response)


def telegram(method, payload):
    result = request_json(API + method, payload, timeout=45)
    if not result.get("ok"):
        raise RuntimeError("Telegram API error")
    return result["result"]


def send(text):
    telegram("sendMessage", {"chat_id": ALLOWED_ID, "text": text[:3900]})


def open_db():
    Path(DB_FILE).parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB_FILE)
    db.execute("CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY, role TEXT NOT NULL, content TEXT NOT NULL)")
    db.execute("CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, content TEXT NOT NULL)")
    db.execute("CREATE TABLE IF NOT EXISTS state (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
    db.execute("""CREATE TABLE IF NOT EXISTS reminders (
        id INTEGER PRIMARY KEY, content TEXT NOT NULL,
        due_utc TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'pending',
        sent_utc TEXT
    )""")
    db.execute("""CREATE TABLE IF NOT EXISTS monitor_targets (
        target_key TEXT PRIMARY KEY,
        status TEXT NOT NULL DEFAULT 'unknown',
        failures INTEGER NOT NULL DEFAULT 0,
        successes INTEGER NOT NULL DEFAULT 0,
        checked_utc TEXT,
        changed_utc TEXT
    )""")
    db.execute("""CREATE TABLE IF NOT EXISTS monitor_alerts (
        id INTEGER PRIMARY KEY,
        message TEXT NOT NULL,
        created_utc TEXT NOT NULL,
        sent_utc TEXT
    )""")
    db.execute("INSERT OR IGNORE INTO state(key, value) VALUES ('monitor_enabled', '0')")
    db.commit()
    return db


def history(db):
    rows = db.execute("SELECT role, content FROM messages ORDER BY id DESC LIMIT 6").fetchall()
    return [{"role": role, "content": content} for role, content in reversed(rows)]


def saved_notes(db):
    rows = db.execute("SELECT content FROM notes ORDER BY id DESC LIMIT 12").fetchall()
    return "\n".join("- " + row[0] for row in reversed(rows))


def ask_ollama(db, question):
    extra = saved_notes(db)
    system = SYSTEM + ("\nNotes explicitly saved by the user:\n" + extra if extra else "")
    payload = {
        "model": MODEL, "stream": False, "keep_alive": "10m",
        "options": {"num_ctx": 4096, "num_predict": 200, "temperature": 0.1},
        "messages": ([{"role": "system", "content": system}]
                     + history(db)
                     + [{"role": "user", "content": question[:1800]}])
    }
    result = request_json(os.getenv("OLLAMA_API_URL", "http://ollama:11434/api/chat"), payload, timeout=240)
    return (result.get("message", {}).get("content") or "").strip()



def parse_clock(raw):
    match = re.fullmatch(r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", raw.strip(), re.I)
    if not match:
        raise ValueError("Enter a time such as 6pm or 18:00.")
    hour = int(match.group(1))
    minute = int(match.group(2) or 0)
    meridian = (match.group(3) or "").lower()
    if minute > 59 or (meridian and not 1 <= hour <= 12) or (not meridian and hour > 23):
        raise ValueError("Invalid time. Try 6pm or 18:00.")
    if meridian:
        hour = hour % 12 + (12 if meridian == "pm" else 0)
    return hour, minute


def parse_reminder(raw, now=None):
    """Deterministic input parsing; the AI model never decides the date or task."""
    now = now or datetime.now(LOCAL_ZONE)
    raw = re.sub(r"^remind\s+me\s+", "", raw.strip(), flags=re.I)
    raw = re.sub(r"^to\s+", "", raw, flags=re.I)

    delay = re.fullmatch(r"in\s+(\d{1,4})\s*(m|mins?|minutes?|h|hrs?|hours?)\s+(.+)", raw, re.I)
    if delay:
        count = int(delay.group(1))
        unit = delay.group(2).lower()
        seconds = count * (3600 if unit.startswith("h") else 60)
        if seconds < 60 or seconds > 86400:
            raise ValueError("Relative reminders must be between 1 minute and 24 hours.")
        due = (now.astimezone(timezone.utc) + timedelta(seconds=seconds)).astimezone(LOCAL_ZONE)
        content = delay.group(3).strip()
    else:
        m = re.fullmatch(
            r"(tomorrow|\d{4}-\d{2}-\d{2})\s+(?:at\s+)?"
            r"(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)\s+(.*)",
            raw, re.I
        )
        if not m:
            raise ValueError("Use /remind tomorrow 6pm Check backups, or /remind in 2m Test message.")
        daystr, timestr, content = m.groups()
        h, minute = parse_clock(timestr)
        if daystr.lower() == "tomorrow":
            local_date = now.date() + timedelta(days=1)
        else:
            try:
                local_date = datetime.strptime(daystr, "%Y-%m-%d").date()
            except ValueError as exc:
                raise ValueError("Use a valid date, e.g. 2027-02-28.") from exc
        due = datetime(local_date.year, local_date.month, local_date.day,
                       h, minute, tzinfo=LOCAL_ZONE)
        # If clocks move, reject nonexistent wall-times rather than silently shifting the reminder.
        roundtrip = due.astimezone(timezone.utc).astimezone(LOCAL_ZONE)
        if roundtrip.replace(tzinfo=None) != due.replace(tzinfo=None):
            raise ValueError("That time doesn't exist due to daylight saving. Choose another time.")
        content = content.strip()

    content = re.sub(r"^to\s+", "", content, flags=re.I).strip()
    if not content or len(content) > 400:
        raise ValueError("Use a reminder message between 1 and 400 characters.")
    if due <= now:
        raise ValueError("That time is in the past. Choose a future time.")
    return due.astimezone(timezone.utc), content


def reminder_worker():
    """Independent worker keeps reminders responsive during slow Ollama responses."""
    db = sqlite3.connect(DB_FILE, timeout=15)
    while True:
        try:
            now_utc = datetime.now(timezone.utc).isoformat()
            due = db.execute(
                "SELECT id, content, due_utc FROM reminders "
                "WHERE status='pending' AND due_utc <= ? ORDER BY due_utc LIMIT 5",
                (now_utc,)
            ).fetchall()
            for reminder_id, content, _ in due:
                # A failed send leaves the reminder pending for retry after the next check.
                send(f"⏰ XWiz reminder #{reminder_id}: {content}")
                with db:
                    db.execute("UPDATE reminders SET status='sent', sent_utc=? WHERE id=?",
                               (datetime.now(timezone.utc).isoformat(), reminder_id))
        except Exception as error:
            print("Reminder error:", type(error).__name__, str(error)[:160], flush=True)
        time.sleep(10)


def format_local(iso_utc):
    return datetime.fromisoformat(iso_utc).astimezone(LOCAL_ZONE).strftime("%a %b %d, %Y at %I:%M %p")

def tcp_reachable(ip, port):
    """Only attempts a TCP connection. No authentication or remote commands."""
    try:
        with socket.create_connection((ip, port), timeout=3):
            return True
    except OSError:
        return False


def live_status():
    """On-demand connectivity test, independent of automatic monitoring."""
    lines = ["🔎 XWiz live network checks:"]
    if not MONITOR_ENDPOINTS:
        return "No targets configured. Set XWIZ_MONITOR_TARGETS first."
    for _, name, ip, port, service in MONITOR_ENDPOINTS:
        if tcp_reachable(ip, port):
            lines.append(f"✅ {name} ({ip}): {service} TCP {port} reachable")
        else:
            lines.append(f"⚠️ {name} ({ip}): cannot connect to {service} TCP {port}")
    lines.append("Note: These test TCP connectivity only, not application health or VM status.")
    return "\n".join(lines)


def monitor_enabled(db):
    row = db.execute("SELECT value FROM state WHERE key='monitor_enabled'").fetchone()
    return bool(row and row[0] == '1')


def monitor_summary(db):
    enabled = monitor_enabled(db)
    lines = ["🔔 Automatic monitoring: " + ("ON" if enabled else "OFF")]
    if enabled:
        lines.append("Checks every 60 seconds. Alert after 3 failed checks; recovery after 2 successful checks.")
    for key, name, ip, port, service in MONITOR_ENDPOINTS:
        row = db.execute("SELECT status, checked_utc FROM monitor_targets WHERE target_key=?", (key,)).fetchone()
        state = row[0] if row else 'unknown'
        symbol = {"up": "✅", "down": "⚠️", "unknown": "◻️"}.get(state, "◻️")
        label = {"up": "reachable at last check", "down": "unreachable at last confirmed check", "unknown": "not checked yet"}.get(state, "unknown")
        lines.append(f"{symbol} {name} ({ip}): {service} TCP {port} — {label}")
    lines.append("Use /monitor on, /monitor off, or /status for an immediate check.")
    lines.append("TCP port monitoring is not an application health check.")
    return "\n".join(lines)


def set_monitoring(db, enabled):
    with db:
        db.execute("INSERT INTO state(key, value) VALUES ('monitor_enabled', ?) "
                   "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                   ('1' if enabled else '0',))
        if enabled:
            # Start a fresh baseline; do not treat old/stale readings as current.
            db.execute("UPDATE monitor_targets SET status='unknown', failures=0, successes=0")
        else:
            # Disabling monitoring also discards undelivered alerts.
            db.execute("DELETE FROM monitor_alerts WHERE sent_utc IS NULL")
    return monitor_summary(db)


def record_probe(db, target, reachable, now_utc=None):
    """Persist one sample and enqueue transition alerts; no duplicate periodic spam."""
    key, name, ip, port, service = target
    now_utc = now_utc or datetime.now(timezone.utc).isoformat()
    with db:
        row = db.execute("SELECT status, failures, successes FROM monitor_targets WHERE target_key=?", (key,)).fetchone()
        if row is None:
            db.execute("INSERT INTO monitor_targets(target_key) VALUES (?)", (key,))
            row = ('unknown', 0, 0)
        state, failures, successes = row
        next_state = state
        alert = None
        if reachable:
            failures = 0
            successes += 1
            if state == 'unknown':
                # Successful first check establishes an up baseline silently.
                next_state = 'up'
                successes = 0
            elif state == 'down' and successes >= MONITOR_RECOVERY_SUCCESSES:
                next_state = 'up'
                successes = 0
                alert = (f"✅ XWiz recovery ({now_utc}): {name} ({ip}) "
                         f"{service} TCP {port} reachable for {MONITOR_RECOVERY_SUCCESSES} consecutive checks. "
                         "This verifies the port, not complete service health.")
        else:
            successes = 0
            failures += 1
            if state != 'down' and failures >= MONITOR_DOWN_FAILURES:
                next_state = 'down'
                failures = 0
                alert = (f"⚠️ XWiz alert ({now_utc}): {name} ({ip}) "
                         f"{service} TCP {port} unreachable from Ubuntu for "
                         f"{MONITOR_DOWN_FAILURES} consecutive checks. "
                         "The host may still be powered on.")
        db.execute("UPDATE monitor_targets SET status=?, failures=?, successes=?, checked_utc=?, "
                   "changed_utc=CASE WHEN status!=? THEN ? ELSE changed_utc END "
                   "WHERE target_key=?",
                   (next_state, failures, successes, now_utc, next_state, now_utc, key))
        if alert:
            db.execute("INSERT INTO monitor_alerts(message, created_utc) VALUES (?, ?)",
                       (alert, now_utc))
    return alert


def deliver_monitor_alerts(db):
    """Retry unsent Telegram alerts after transient network/API failures."""
    pending = db.execute("SELECT id, message FROM monitor_alerts "
                         "WHERE sent_utc IS NULL ORDER BY id LIMIT 10").fetchall()
    for alert_id, message in pending:
        send(message)
        with db:
            db.execute("UPDATE monitor_alerts SET sent_utc=? WHERE id=? AND sent_utc IS NULL",
                       (datetime.now(timezone.utc).isoformat(), alert_id))


def monitor_worker():
    """Runs independently from the Telegram/LLM loop and reminder thread."""
    db = sqlite3.connect(DB_FILE, timeout=30)
    next_probe = 0.0
    while True:
        try:
            enabled = monitor_enabled(db)
            if enabled and time.monotonic() >= next_probe:
                for target in MONITOR_ENDPOINTS:
                    record_probe(db, target, tcp_reachable(target[2], target[3]))
                next_probe = time.monotonic() + MONITOR_INTERVAL_SECONDS
            elif not enabled:
                next_probe = 0.0
            if enabled:
                deliver_monitor_alerts(db)
        except Exception as error:
            print("Monitor error:", type(error).__name__, str(error)[:160], flush=True)
        time.sleep(5)


def handle(db, update):
    msg = update.get("message") or {}
    sender = msg.get("from") or {}
    chat = msg.get("chat") or {}
    if (chat.get("type") != "private" or sender.get("id") != ALLOWED_ID
            or chat.get("id") != ALLOWED_ID):
        return
    text = (msg.get("text") or "").strip()
    if not text:
        send("Text messages only for now.")
        return

    cmd, _, arg = text.partition(" ")
    cmd = cmd.split("@")[0].lower()
    arg = arg.strip()

    if cmd in ("/status", "/servers"):
        send(live_status())
    elif cmd == "/monitor":
        if arg.lower() == 'on':
            send(set_monitoring(db, True))
        elif arg.lower() == 'off':
            send(set_monitoring(db, False))
        elif not arg:
            send(monitor_summary(db))
        else:
            send("Use /monitor on, /monitor off, or /monitor to view status.")
    elif cmd in ("/start", "/help"):
        send("Hi, I'm XWiz! 🤖\n/remember text — save a note\n/memories — list notes\n/forget 3 — delete note #3\n/remind tomorrow 6pm Check backups — schedule reminder\n/remind in 2m Test reminder — quick test\n/reminders — list upcoming reminders\n/cancel 3 — cancel reminder #3\n/status — check server connectivity\n/monitor on — enable automatic alerts\n/monitor off — disable alerts\n/monitor — monitoring status\n/reset — clear chat history (keep notes and reminders)\n/help — show commands")
    elif cmd == "/remember":
        if not arg:
            send("Usage: /remember The spare SSDs are M.2 SATA")
        elif len(arg) > 400:
            send("Keep saved notes under 400 characters.")
        else:
            cur = db.execute("INSERT INTO notes(content) VALUES (?)", (arg,))
            db.commit()
            send(f"Saved note #{cur.lastrowid}. 🧠")
    elif cmd == "/memories":
        rows = db.execute("SELECT id, content FROM notes ORDER BY id DESC LIMIT 20").fetchall()
        send("Saved notes:\n" + "\n".join(f"#{i}: {v}" for i, v in rows)
             if rows else "No saved notes yet.")
    elif cmd == "/forget":
        if not arg.isdigit():
            send("Usage: /forget 3 (use /memories to see note numbers)")
        else:
            cur = db.execute("DELETE FROM notes WHERE id=?", (int(arg),))
            db.commit()
            send("Note deleted." if cur.rowcount else "No note with that number.")
    elif cmd == "/remind" or text.lower().startswith("remind me "):
        try:
            due, content = parse_reminder(arg if cmd == "/remind" else text)
        except ValueError as error:
            send(str(error))
        else:
            cur = db.execute("INSERT INTO reminders(content, due_utc) VALUES (?, ?)",
                             (content, due.isoformat()))
            db.commit()
            send(f"✅ Reminder #{cur.lastrowid} saved for {format_local(due.isoformat())} ({TIMEZONE}):\n{content}")
    elif cmd == "/reminders":
        reminders = db.execute("SELECT id, content, due_utc FROM reminders "
                               "WHERE status='pending' ORDER BY due_utc LIMIT 20").fetchall()
        send("Upcoming reminders (" + TIMEZONE + "):\n" +
             "\n".join(f"#{i} — {format_local(due)}: {content}" for i, content, due in reminders)
             if reminders else "No upcoming reminders.")
    elif cmd == "/cancel":
        if not arg.isdigit():
            send("Usage: /cancel 3 (use /reminders to find the number)")
        else:
            cur = db.execute("UPDATE reminders SET status='cancelled' "
                             "WHERE id=? AND status='pending'", (int(arg),))
            db.commit()
            send("Reminder cancelled." if cur.rowcount else "No pending reminder with that number.")
    elif cmd == "/reset":
        db.execute("DELETE FROM messages")
        db.commit()
        send("Recent chat history cleared; saved notes kept.")
    else:
        telegram("sendChatAction", {"chat_id": ALLOWED_ID, "action": "typing"})
        answer = ask_ollama(db, text) or "I couldn't generate a response."
        send(answer)
        db.executemany("INSERT INTO messages(role, content) VALUES (?, ?)",
                       [("user", text[:1800]), ("assistant", answer)])
        db.commit()


def main():
    db = open_db()
    row = db.execute("SELECT value FROM state WHERE key='offset'").fetchone()
    if row:
        offset = int(row[0])
    else:
        # On first startup, skip previously delivered Telegram messages.
        existing = telegram("getUpdates", {"offset": -1, "timeout": 0,
                                            "allowed_updates": ["message"]})
        offset = max((u["update_id"] for u in existing), default=-1) + 1
        db.execute("INSERT INTO state(key,value) VALUES ('offset',?)", (str(offset),))
        db.commit()
    threading.Thread(target=reminder_worker, name="reminders", daemon=True).start()
    threading.Thread(target=monitor_worker, name="monitor", daemon=True).start()
    print("XWiz bridge ready: SQLite memory, reminders, and opt-in monitoring available.", flush=True)
    while True:
        try:
            updates = telegram("getUpdates", {"offset": offset, "timeout": 25,
                                                "allowed_updates": ["message"]})
            for update in updates:
                handle(db, update)
                offset = update["update_id"] + 1
                db.execute("UPDATE state SET value=? WHERE key='offset'", (str(offset),))
                db.commit()
        except Exception as error:
            print("Bridge error:", type(error).__name__, str(error)[:160], flush=True)
            time.sleep(5)


if __name__ == "__main__":
    main()
