"""Prepare the archived, deterministic EV regression fixtures in a public checkout."""

import csv
import hashlib
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory

from week7.load_model import produce

HERE = Path(__file__).resolve().parent
TRACE_HASHES = HERE / "audit/ev_regression_fixture_sha256.csv"
OUTPUTS = HERE / "outputs"


def sha256_file(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def prepare():
    with TRACE_HASHES.open(newline="", encoding="utf-8") as stream:
        fixtures = list(csv.DictReader(stream))
    if {f["scenario"] for f in fixtures} != {"low", "central", "high"} or len(fixtures) != 3:
        raise ValueError("The EV regression fixture manifest must specify all three scenarios.")

    for fixture in fixtures:
        scenario = fixture["scenario"]
        name = f"{scenario}_ev_trace_61320.csv"
        target = OUTPUTS / name
        expected = fixture["sha256"]
        if target.is_file():
            if sha256_file(target) != expected:
                raise ValueError(f"{name} differs from the archive. Preserve the existing file for inspection.")
            print(f"PASS {name} (existing fixture)")
            continue

        with TemporaryDirectory(prefix="lc1-ev-fixture-") as temp:
            scratch = Path(temp)
            produce(scenario, scratch)
            generated = scratch / name
            if sha256_file(generated) != expected:
                raise ValueError(f"{name} did not reproduce the archived SHA-256.")
            with generated.open("rb") as source, target.open("xb") as output:
                shutil.copyfileobj(source, output)
        print(f"PASS {name} (regenerated fixture)")


if __name__ == "__main__":
    prepare()
