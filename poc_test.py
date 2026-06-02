#!/usr/bin/env python3
"""AutoPoC Test Script for TradingAgents-Studio"""
import json, os, sys, time, urllib.request, urllib.error

SERVICE_URL = os.environ.get("SERVICE_URL", sys.argv[1] if len(sys.argv) > 1 else "")
MAX_RETRIES = 5
RETRY_DELAY = 10
results = []


def test_scenario(name, description, method, path, body=None,
                  expected_status=200, expected_content=None, timeout=30):
    url = f"{SERVICE_URL.rstrip('/')}{path}"
    start = time.time()
    for attempt in range(MAX_RETRIES):
        try:
            if body:
                data = json.dumps(body).encode() if isinstance(body, dict) else body.encode()
                req = urllib.request.Request(url, data=data, method=method)
                req.add_header("Content-Type", "application/json")
            else:
                req = urllib.request.Request(url, method=method)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                status = resp.status
                response_body = resp.read().decode()
                if status == expected_status:
                    if expected_content and expected_content not in response_body:
                        r = {"scenario_name": name, "status": "fail",
                             "output": response_body[:2000],
                             "error_message": f"Expected '{expected_content}' not in response",
                             "duration_seconds": round(time.time()-start, 2)}
                    else:
                        r = {"scenario_name": name, "status": "pass",
                             "output": response_body[:2000], "error_message": None,
                             "duration_seconds": round(time.time()-start, 2)}
                    results.append(r); return r
                elif attempt < MAX_RETRIES - 1:
                    print(f"  [{name}] Got status {status}, retrying ({attempt+1}/{MAX_RETRIES})...", file=sys.stderr)
                    time.sleep(RETRY_DELAY); continue
                else:
                    r = {"scenario_name": name, "status": "fail",
                         "output": response_body[:2000],
                         "error_message": f"Expected {expected_status}, got {status}",
                         "duration_seconds": round(time.time()-start, 2)}
                    results.append(r); return r
        except urllib.error.HTTPError as e:
            response_body = ""
            try:
                response_body = e.read().decode()[:2000]
            except Exception:
                pass
            if e.code == expected_status:
                r = {"scenario_name": name, "status": "pass",
                     "output": response_body, "error_message": None,
                     "duration_seconds": round(time.time()-start, 2)}
                results.append(r); return r
            elif attempt < MAX_RETRIES - 1:
                print(f"  [{name}] HTTP {e.code}, retrying ({attempt+1}/{MAX_RETRIES})...", file=sys.stderr)
                time.sleep(RETRY_DELAY)
            else:
                r = {"scenario_name": name, "status": "fail",
                     "output": response_body,
                     "error_message": f"Expected {expected_status}, got HTTP {e.code}",
                     "duration_seconds": round(time.time()-start, 2)}
                results.append(r); return r
        except urllib.error.URLError as e:
            if attempt < MAX_RETRIES - 1:
                print(f"  [{name}] Retry {attempt+1}/{MAX_RETRIES}: {e}", file=sys.stderr)
                time.sleep(RETRY_DELAY)
            else:
                r = {"scenario_name": name, "status": "error", "output": "",
                     "error_message": f"Unreachable after {MAX_RETRIES} attempts: {e}",
                     "duration_seconds": round(time.time()-start, 2)}
                results.append(r); return r
        except Exception as e:
            r = {"scenario_name": name, "status": "error", "output": "",
                 "error_message": str(e),
                 "duration_seconds": round(time.time()-start, 2)}
            results.append(r); return r


# === SCENARIOS ===

print("Running PoC tests for TradingAgents-Studio...", file=sys.stderr)
print(f"Service URL: {SERVICE_URL}", file=sys.stderr)

# Scenario 1: Health Check
print("\n[1/4] Testing health check endpoint...", file=sys.stderr)
test_scenario(
    name="health-check",
    description="Verify FastAPI health endpoint",
    method="GET",
    path="/api/health",
    expected_status=200,
    expected_content="ok",
    timeout=60
)

# Scenario 2: Root Access (SPA frontend)
print("[2/4] Testing root path (frontend SPA)...", file=sys.stderr)
test_scenario(
    name="root-access",
    description="Verify root path serves frontend or API response",
    method="GET",
    path="/",
    expected_status=200,
    timeout=30
)

# Scenario 3: History API
print("[3/4] Testing history API...", file=sys.stderr)
test_scenario(
    name="history-api",
    description="Verify history API endpoint",
    method="GET",
    path="/api/history",
    expected_status=200,
    timeout=30
)

# Scenario 4: Settings API
print("[4/4] Testing settings API...", file=sys.stderr)
test_scenario(
    name="settings-api",
    description="Verify settings API endpoint",
    method="GET",
    path="/api/settings",
    expected_status=200,
    timeout=30
)

# === END SCENARIOS ===

print(json.dumps({"results": results}, indent=2))
sys.exit(1 if any(r["status"] in ("fail", "error") for r in results) else 0)
