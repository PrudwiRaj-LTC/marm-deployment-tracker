
import json
import os
from pathlib import Path

with open(os.environ["GITHUB_EVENT_PATH"]) as f:
    event = json.load(f)

payload = event["client_payload"]

service = payload["service"]
environment = payload["environment"]

tracker_file = Path(f"{environment}/{service}.json")

new_current = {
    "version": payload["version"],
    "commitId": payload["commitId"],
    "deploymentId": payload["deploymentId"],
    "deployedAt": payload["deployedAt"]
}

if tracker_file.exists():

    with open(tracker_file) as f:
        existing = json.load(f)

    previous = existing.get("current")

else:
    previous = None

compare_url = ""

if previous:
    compare_url = (
        f"https://github.com/my-org/{service}"
        f"/compare/{previous['commitId']}...{new_current['commitId']}"
    )

updated = {
    "service": service,
    "environment": environment,
    "current": new_current,
    "previous": previous,
    "compareUrl": compare_url
}

tracker_file.parent.mkdir(parents=True, exist_ok=True)

with open(tracker_file, "w") as f:
    json.dump(updated, f, indent=2)

print(f"Updated {tracker_file}")
