"""Reconcile the published LC1 native evidence using the Python standard library."""

from collections import defaultdict
import csv
import hashlib
import math
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent


def rows(file):
    with (ROOT / file).open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def near(actual, expected, context):
    if not math.isclose(float(actual), float(expected), abs_tol=1e-6, rel_tol=0):
        raise ValueError(f"{context} differs: {actual} vs {expected}")


def unique(records, key):
    indexed = {row[key]: row for row in records}
    if len(indexed) != len(records):
        raise ValueError(f"Duplicate {key}")
    return indexed


def verify_hashes():
    expected = {path.name for path in ROOT.glob("*.csv") if path.name != "data-manifest.csv"}
    manifest = unique(rows("data-manifest.csv"), "file")
    if set(manifest) != expected:
        raise ValueError("CSV inventory differs from the data manifest")
    for file, row in manifest.items():
        actual = hashlib.sha256((ROOT / file).read_bytes()).hexdigest()
        if actual != row["sha256"]:
            raise ValueError(f"SHA-256 mismatch: {file}")


def verify_events(metadata):
    events = unique(rows("event-results.csv"), "case")
    feeders = defaultdict(list)
    for row in rows("section-service.csv"):
        feeders[row["case"]].append(row)
    if set(events) != set(metadata) or set(feeders) != set(metadata):
        raise ValueError("Event, model and feeder identifiers differ")
    for case, event in events.items():
        near(event["event_h"], metadata[case]["event_h"], case)
        sections = unique(feeders[case], "section")
        section_fields = {"C4ISR": "C4ISR_served_kwh", "Auxiliary essential": "essential_aux_served_kwh",
                          "Auxiliary interruptible": "interruptible_aux_served_kwh", "EV": "EV_served_kwh"}
        if set(sections) != set(section_fields):
            raise ValueError(f"Unexpected feeder names: {case}")
        for section, field in section_fields.items():
            stats = sections[section]
            near(stats["served_kwh"], event[field], f"{case} {section} service")
            near(float(stats["served_kwh"]) + float(stats["unserved_kwh"]),
                 stats["required_kwh"], f"{case} {section} demand")
        near(sections["C4ISR"]["unserved_kwh"], event["C4ISR_ens_kwh"], case)
        near(sections["EV"]["unserved_kwh"], event["EV_ens_kwh"], case)
        near(sum(float(row["unserved_kwh"]) for row in sections.values()), event["total_ens_kwh"], case)
        ac_supply = sum(float(event[key]) for key in ("dg_kwh", "pv_kwh", "wind_kwh", "bess_discharge_kwh"))
        ac_use = sum(float(row["served_kwh"]) for row in sections.values()) + float(event["bess_charge_kwh"])
        near(ac_supply - ac_use, event["balance_residual_kwh"], case)
        near(ac_supply, ac_use, f"{case} AC balance")
    return events


def verify_telemetry(metadata):
    observer = unique(rows("telemetry-manifest.csv"), "case")
    intervals = defaultdict(list)
    histograms = defaultdict(lambda: defaultdict(dict))
    for row in rows("solver-intervals.csv"):
        intervals[row["case"]].append(row)
    for row in rows("soc-bins.csv"):
        case, hour = row["case"], int(row["hour_of_day_bucket_end"])
        edge, weight = float(row["soc_bin_upper_fraction"]), float(row["native_duration_weight_h"])
        if edge in histograms[case][hour] or not math.isfinite(weight) or weight < 0:
            raise ValueError(f"Invalid SOC bin for {case} hour {hour}")
        histograms[case][hour][edge] = weight
        near(row["event_h"], observer[case]["event_h"], case)
    if set(intervals) != set(observer) or set(histograms) != set(observer):
        raise ValueError("Telemetry tables reference different cases")
    for case, run in observer.items():
        origin = float(metadata[case]["source_start_index"])
        end = 0.0
        near(len(intervals[case]), run["step_boundaries_reconciled"], case)
        near(run["MOF_reopened_hour_buckets"], 0, f"{case} saved MOF")
        for row in intervals[case]:
            start = float(row["start_event_h"])
            near(start, end, f"{case} timeline continuity")
            end = float(row["end_event_h"])
            if end <= start:
                raise ValueError(f"Nonpositive solver interval for {case}")
            near(end - start, row["duration_h"], case)
            near(start + origin, row["start_model_clock_h"], case)
            near(end + origin, row["end_model_clock_h"], case)
        near(end, run["event_h"], case)
        near(end, metadata[case]["event_h"], case)
        if set(histograms[case]) != set(range(1, 25)):
            raise ValueError(f"Missing time-of-day buckets: {case}")
        for bins in histograms[case].values():
            if set(bins) != {i / 10 for i in range(11)}:
                raise ValueError(f"Missing SOC bin edges: {case}")
            near(sum(bins.values()), end / 24, f"{case} time-of-day weight")
    totals = defaultdict(lambda: [0.0, 0.0])
    seen = set()
    c2 = {24: "d0_hybrid_breakers", 72: "d0_hybrid72_breakers", 168: "d0_hybrid168_breakers"}
    for row in rows("soc-comparison.csv"):
        hours, hour = int(row["event_h"]), int(row["hour_of_day_bucket_end"])
        expected = sum(weight for edge, weight in histograms[c2[hours]][hour].items() if edge > 0.8)
        native = float(row["native_time_above_80_percent_h_bins"])
        python = float(row["python_time_above_80_percent_h_bins"])
        if (hours, hour) in seen or not 0 <= python <= hours / 24 + 1e-6:
            raise ValueError("Invalid comparison row")
        seen.add((hours, hour))
        near(native, expected, f"C2 {hours} h in hour bin {hour}")
        totals[hours][0] += native
        totals[hours][1] += python
    if seen != {(hours, hour) for hours in c2 for hour in range(1, 25)}:
        raise ValueError("C2 comparison does not cover all published hours")
    return observer, intervals, totals


def main():
    verify_hashes()
    metadata = unique(rows("case-manifest.csv"), "case")
    events = verify_events(metadata)
    observer, intervals, totals = verify_telemetry(metadata)
    overload = "battery_pcs120_overload"
    near(events[overload]["sampled_bess_peak_discharge_kw"],
         metadata[overload]["bess_max_discharge_kw"], "PCS overload limit")
    for file in ("case-manifest.csv", "telemetry-manifest.csv", "section-service.csv", "diesel-parity.csv",
                 "soc-comparison.csv", "data-manifest.csv"):
        for row in rows(file):
            for field, value in row.items():
                if "sha256" in field and re.fullmatch(r"[0-9a-f]{64}", value) is None:
                    raise ValueError(f"Invalid digest in {file}: {field}")
    parity = rows("diesel-parity.csv")
    if len(parity) != 25 or any(row["status"] != "VALIDATED" for row in parity):
        raise ValueError("Unexpected diesel parity evidence")
    for row in parity:
        near(row["native_value"], row["python_value"], f"{row['case']} {row['metric']}")
    snapshots = rows("electrical-snapshots.csv")
    if len(snapshots) != 11 or any(row["converged"] != "True" or row["accepted"] != "True" for row in snapshots):
        raise ValueError("Unexpected OpenDSS snapshot evidence")
    for row in snapshots:
        near(row["balance_residual_kw"], 0, row["case"])
    print(f"Verified {len(events)} native event ledgers, {len(observer)} telemetry runs, "
          f"{sum(map(len, intervals.values()))} intervals, {len(parity)} diesel metric pairs "
          f"and {len(snapshots)} OpenDSS snapshots.")
    for hours, (native, python) in sorted(totals.items()):
        print(f"C2 {hours} h: SOC bins above 80%: MDT {native:.2f} h, Python {python:.2f} h")


if __name__ == "__main__":
    main()
