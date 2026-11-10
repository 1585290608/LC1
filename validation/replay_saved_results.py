"""Read-only regression against sealed Draft 3A, 3B and 3C Python outputs."""

import argparse
import csv
import io
from pathlib import Path

from models.core.simulate import Settings
from models.grid_connected import dispatch, economics
from models.islanded import contingencies, strategies
from validation.trace_io import load, read, sha


class FrozenStudy:
    def __init__(self, root):
        self.root = root
        self.hashes = {row["path"]: row["sha256"] for row in read(root / "SHA256_MANIFEST.csv")}

    def checked(self, rel):
        path = self.root / rel
        if sha(path) != self.hashes[rel]:
            raise ValueError(f"Frozen source hash mismatch: {path}")
        return path

    def compare_csv(self, rel, rows):
        path = self.checked(rel)
        buffer = io.StringIO(newline="")
        writer = csv.DictWriter(buffer, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
        if buffer.getvalue().encode("utf-8-sig") != path.read_bytes():
            raise ValueError(f"Replay differs: {path}")


def replay_strategies(study):
    rows_checked = 0
    winter = None
    for strategy in ("S0", "S1", "S2", "S3"):
        for fuel in ("FIXED_025", "MDT_DERIVED"):
            for hours in (24, 72, 168):
                case = f"Results/PRIMARY/{strategy}_{fuel}_H{hours}"
                config = load(study.checked(case + "/CONFIG.json"))
                rows, _ = strategies.run_case(
                    strategy, fuel, hours, settings=Settings(**config["settings"]),
                    initial_fuel=config["initial_fuel_l"]
                )
                study.compare_csv(case + "/DISPATCH.csv", rows)
                rows_checked += len(rows)
                if (strategy, fuel, hours) == ("S3", "MDT_DERIVED", 168):
                    winter = rows
    print(f"Islanded strategies: 24 traces, {rows_checked:,} hourly rows identical.")
    return winter


def replay_outages(study, winter):
    rows_checked = 0
    count = 0
    for case in contingencies.scenarios():
        folder = f"Results/Scenarios/{case.id}"
        if case.reused:
            study.compare_csv("Raw_Data/Existing_Draft3A_Winter_S3/DISPATCH.csv", winter)
            # Draft 3C read the reused CSV with its numeric columns parsed as floats.
            imported = [
                {key: float(value) if type(value) is int else value for key, value in row.items()}
                for row in winter
            ]
            segments = contingencies.imported_ledger(imported)
        else:
            rows, segments, _ = contingencies.run(case)
            study.compare_csv(folder + "/DISPATCH.csv", rows)
            rows_checked += len(rows)
            count += 1
        study.compare_csv(folder + "/SERVICE_LEDGER.csv", segments)
    print(f"Outages: {count} traces, {rows_checked:,} hourly rows identical. "
          "Reused winter trace and all 18 service ledgers identical.")


def replay_grid_and_finance(study):
    grid = {}
    rows_checked = 0
    for case in dispatch.cases():
        rows, metrics, _ = dispatch.run(case)
        folder = f"Results/Annual/{case.name}"
        study.compare_csv(folder + "/DISPATCH.csv", rows)
        frozen = load(study.checked(folder + "/METRICS.json"))
        if metrics | {"status": frozen["status"]} != frozen:
            raise ValueError(f"Annual metrics differ: {case.name}")
        grid[case.name] = frozen
        rows_checked += len(rows)
    print(f"Grid connected: {len(grid)} traces, {rows_checked:,} hourly rows identical.")

    finance_root = study.root / "Results/Financial"
    case_ids = sorted({Path(rel).parent.name for rel in study.hashes
                       if rel.startswith("Results/Financial/") and rel.endswith("/RESULT.json")})
    if len(case_ids) != 16:
        raise ValueError(f"Expected 16 saved financial cases under {finance_root}")
    for case_id in case_ids:
        folder = f"Results/Financial/{case_id}"
        config = load(study.checked(folder + "/CONFIG.json"))
        metrics = grid[config["physical_case"]]
        result, flows, incremental = economics.evaluate(
            metrics, price=config["import_gbp_kwh"],
            comparator_metrics=grid["P0R_GRID_DG_UPS"],
        )
        result["financial_id"] = case_id
        if result != load(study.checked(folder + "/RESULT.json")):
            raise ValueError(f"Financial metrics differ: {case_id}")
        study.compare_csv(folder + "/CASHFLOWS.csv", flows)
        if incremental:
            study.compare_csv(folder + "/INCREMENTAL_VS_P0R.csv", incremental)
    print(f"Finance: {len(case_ids)} cashflows and corresponding results identical.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path, help="Path to the original LC1 Remake Validation folder")
    args = parser.parse_args()
    winter = replay_strategies(FrozenStudy(args.archive / "Draft3A"))
    replay_outages(FrozenStudy(args.archive / "Draft3C"), winter)
    replay_grid_and_finance(FrozenStudy(args.archive / "Draft3B"))


if __name__ == "__main__":
    main()
