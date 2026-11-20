# Reproduce the frozen Initial Draft

This directory preserves all 158 files at the original public commit `228c005aa47bdee720524d152e56c10c5d4a7cd3`. All original file contents, including the [README](README.md) and research reports, remain byte-for-byte intact. The original commit provides a standalone reference.

Use Python 3.12 from this directory.

```powershell
python -m venv .venv
$env:PYTHONDONTWRITEBYTECODE='1'
& ./.venv/Scripts/python.exe -B -m pip install -r requirements-test.txt
& ./.venv/Scripts/python.exe -B -m pytest -q
```

The frozen implementation estimates energy and cost under its documented assumptions. Consult the [historical validation](validation/README.md) and [archive replay notes](validation/archive-replay.md) for scope and inputs requiring the local research archive. Track future changes in Week7Remake once the migration is merged.
