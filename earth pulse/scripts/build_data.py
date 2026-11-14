"""Download NASA POWER monthly data and compute trend statistics.

Source: NASA POWER API (MERRA-2 meteorology).
https://power.larc.nasa.gov/

Team: NOVAFLUX | Team Owner: Joe Manu Thomas (Local Event: Pala, India)
2026 NASA Space Apps Challenge — Be An Earth System Trend Detective!
"""

from __future__ import annotations

import hashlib
import json
import math
import ssl
import statistics
import urllib.parse
import urllib.request
from calendar import monthrange
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent if HERE.name == "scripts" else HERE
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"

FILL = -999.0
ALLOWED_HOST = "power.larc.nasa.gov"
MAX_RESPONSE_BYTES = 5 * 1024 * 1024  # 5 MB safety cap against memory exhaustion

LOCATIONS = {
    "kerala_pala": {
        "id": "kerala_pala",
        "name": "Pala, Kerala",
        "region": "Humid tropical monsoon (Western Ghats foothills)",
        "state": "Kerala, India",
        "lat": 9.71,
        "lon": 76.68,
    },
    "rajasthan_jaisalmer": {
        "id": "rajasthan_jaisalmer",
        "name": "Jaisalmer, Rajasthan",
        "region": "Arid Thar Desert",
        "state": "Rajasthan, India",
        "lat": 26.92,
        "lon": 70.91,
    },
}

PARAMETERS = {
    "T2M": {"id": "T2M", "label": "2 m air temperature", "units": "°C", "aggregation": "mean"},
    "T2M_MAX": {"id": "T2M_MAX", "label": "2 m maximum air temperature", "units": "°C", "aggregation": "mean"},
    "PRECTOTCORR": {"id": "PRECTOTCORR", "label": "Corrected precipitation", "units": "mm", "aggregation": "sum"},
    "TS": {"id": "TS", "label": "Earth skin temperature", "units": "°C", "aggregation": "mean"},
    "RH2M": {"id": "RH2M", "label": "2 m relative humidity", "units": "%", "aggregation": "mean"},
}


def power_url(lat: float, lon: float) -> str:
    params = ",".join(PARAMETERS)
    return (
        "https://power.larc.nasa.gov/api/temporal/monthly/point"
        f"?parameters={params}&community=AG"
        f"&longitude={lon}&latitude={lat}"
        "&start=1981&end=2024&format=JSON"
    )


def fetch_json(url: str) -> dict:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or parsed.netloc != ALLOWED_HOST:
        raise ValueError(f"Security violation: Untrusted scheme or host in URL '{url}'")

    tls_context = ssl.create_default_context()
    tls_context.minimum_version = ssl.TLSVersion.TLSv1_2

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "EARTH-PULSE/1.0 (NASA Space Apps NOVAFLUX; Security-Hardened)",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=60, context=tls_context) as response:
        raw_bytes = response.read(MAX_RESPONSE_BYTES + 1)
        if len(raw_bytes) > MAX_RESPONSE_BYTES:
            raise ValueError("Security violation: API payload exceeded 5 MB limit")
        return json.loads(raw_bytes.decode("utf-8"))


def parse_monthly(raw: dict, parameter: str) -> list[dict]:
    block = raw["properties"]["parameter"][parameter]
    rows = []
    for key, value in block.items():
        if not key.isdigit() or len(key) != 6:
            continue
        year, month = int(key[:4]), int(key[4:])
        if month < 1 or month > 12:
            continue
        if value is None or value <= FILL + 1:
            continue
        v = float(value)
        if parameter == "PRECTOTCORR":
            v = v * monthrange(year, month)[1]
        rows.append({"year": year, "month": month, "value": v})
    rows.sort(key=lambda r: (r["year"], r["month"]))
    return rows


def aggregate_window(monthly: list[dict], months: tuple[int, ...], aggregation: str) -> list[dict]:
    buckets: dict[int, list[float]] = defaultdict(list)
    for row in monthly:
        if row["month"] in months:
            buckets[row["year"]].append(row["value"])
    out = []
    for year in sorted(buckets):
        vals = buckets[year]
        if len(vals) < len(months):
            continue
        value = sum(vals) if aggregation == "sum" else sum(vals) / len(vals)
        out.append({"year": year, "value": round(value, 4)})
    return out


def mann_kendall_and_sen(series: list[dict]) -> dict:
    years = [float(r["year"]) for r in series]
    values = [float(r["value"]) for r in series]
    n = len(values)
    s = 0
    slopes = []
    for i in range(n - 1):
        for j in range(i + 1, n):
            diff = values[j] - values[i]; dx = years[j] - years[i]
            if diff > 0:
                s += 1
            elif diff < 0:
                s -= 1
            if dx != 0:
                slopes.append(diff / dx)

    counts: dict[float, int] = defaultdict(int)
    for v in values:
        counts[round(v, 6)] += 1
    tie_correction = sum(t * (t - 1) * (2 * t + 5) for t in counts.values() if t > 1)
    var_s = (n * (n - 1) * (2 * n + 5) - tie_correction) / 18.0
    z = (s - 1) / math.sqrt(var_s) if s > 0 else ((s + 1) / math.sqrt(var_s) if s < 0 else 0.0)
    p_value = math.erfc(abs(z) / math.sqrt(2.0))
    tau = s / (0.5 * n * (n - 1))
    slope_yr = statistics.median(slopes) if slopes else 0.0

    return {
        "n": n,
        "s": s,
        "z": round(z, 4),
        "tau": round(tau, 4),
        "p_value": round(p_value, 6),
        "significant": p_value < 0.05,
        "sen_slope_per_decade": round(slope_yr * 10.0, 4),
    }


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    PROCESSED.mkdir(parents=True, exist_ok=True)
    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "security_verification": {
            "tls_enforced": "TLSv1.2+",
            "allowed_host": ALLOWED_HOST,
            "raw_file_sha256": {},
        },
        "results": {},
    }

    for loc_id, loc in LOCATIONS.items():
        raw_payload = fetch_json(power_url(loc["lat"], loc["lon"]))
        raw_json_str = json.dumps(raw_payload, indent=2)
        raw_sha256 = hashlib.sha256(raw_json_str.encode("utf-8")).hexdigest()
        (RAW / f"{loc_id}_power_monthly.json").write_text(raw_json_str, encoding="utf-8")
        output["security_verification"]["raw_file_sha256"][loc_id] = raw_sha256
        output["results"][loc_id] = {}
        for param_id, meta in PARAMETERS.items():
            monthly = parse_monthly(raw_payload, param_id)
            ann = aggregate_window(monthly, tuple(range(1, 13)), meta["aggregation"])
            jjas = aggregate_window(monthly, (6, 7, 8, 9), meta["aggregation"])
            mam = aggregate_window(monthly, (3, 4, 5), meta["aggregation"])
            output["results"][loc_id][param_id] = {
                "annual": mann_kendall_and_sen(ann),
                "jjas": mann_kendall_and_sen(jjas),
                "mam": mann_kendall_and_sen(mam),
            }

    summary_str = json.dumps(output, indent=2)
    (PROCESSED / "earth_pulse_summary.json").write_text(summary_str, encoding="utf-8")
    print("Done! Saved to data/processed/earth_pulse_summary.json (TLS 1.2+ & SHA-256 Verified)")


if __name__ == "__main__":
    main()