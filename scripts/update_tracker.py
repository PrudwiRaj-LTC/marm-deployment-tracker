import json
import os
from datetime import datetime, timezone
from pathlib import Path
 
with open(os.environ["GITHUB_EVENT_PATH"]) as f:
    event = json.load(f)
 
payload = event["client_payload"]
 
print(f"Received request payload: {json.dumps(payload, indent=2)}")
 
service = payload["service"]
environment = payload["environment"]
 
tracker_file = Path(f"{environment}/{service}.json")
 
 
def normalize_deployed_at(value):
    # Harness sometimes sends epoch millis instead of an ISO 8601 string.
    if value.isdigit():
        return datetime.fromtimestamp(int(value) / 1000, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return value
 
new_current = {
    "version": payload["version"],
    "commitId": payload["commitId"],
    "deploymentId": payload["deploymentId"],
    "deployedAt": normalize_deployed_at(payload["deployedAt"])
}
 
existing = None
if tracker_file.exists():
    with open(tracker_file) as f:
        existing = json.load(f)
 
previous = existing.get("previous") if existing else None
current = existing.get("current") if existing else None
 
if current and current.get("version") == new_current["version"]:
    current = {**current, "deployedAt": new_current["deployedAt"]}
else:
    previous = current
    current = new_current
 
compare_url = ""
if previous:
    compare_url = (
        f"https://github.com/lbg-gcp-foundation/{service}"
        f"/compare/{previous['commitId']}...{current['commitId']}"
    )
 
updated = {
    "service": service,
    "environment": environment,
    "current": current,
    "previous": previous,
    "compareUrl": compare_url
}
 
tracker_file.parent.mkdir(parents=True, exist_ok=True)
 
with open(tracker_file, "w") as f:
    json.dump(updated, f, indent=2)
 
print(f"Updated {tracker_file}")
