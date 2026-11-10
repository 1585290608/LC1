import hashlib

import pytest

from validation.trace_io import ROOT, load


@pytest.fixture(scope="session")
def baseline_core_verified():
    baseline = load(ROOT / "validation/diesel-energy-accounting/baseline-core-hashes.json")
    for record in baseline["selected_sources"]:
        name = record["path"].split("/")[-1]
        content = (ROOT / "models/core" / name).read_bytes()
        if name == "simulate.py":
            # Reverse only the import and path changes allowed by the repository migration.
            content = content.replace(b"from .components import", b"from components import", 1)
            content = content.replace(b"ROOT=Path(__file__).resolve().parents[2]",
                                      b"ROOT=Path(__file__).resolve().parents[1]", 1)
        assert hashlib.sha256(content).hexdigest() == record["sha256"]
