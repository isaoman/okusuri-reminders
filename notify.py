"""Run once per minute on Render to dispatch scheduled web push reminders."""

import json
import os
import urllib.request


def main():
    url = os.environ["REMINDER_URL"].rstrip("/") + "/api/cron"
    key = os.environ["REMINDER_KEY"]
    if not url.startswith("https://") or not key:
        raise ValueError("Reminder URL and key must be configured")

    request = urllib.request.Request(
        url,
        data=b"{}",
        headers={
            "X-Reminder-Key": key,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "okusuri-reminders/1.0",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=50) as response:
        result = json.load(response)

    if not result.get("ok"):
        raise RuntimeError("Reminder dispatch failed")
    print(json.dumps({"ok": True, "sent": result.get("sent", 0), "failed": result.get("failed", 0)}))


if __name__ == "__main__":
    main()

