# Shared inputs

The load and renewable profile CSVs use their original file names, values,
units and ordering. The model reads the five `v6_*_index_value.csv` inputs
for C4ISR, auxiliary load, EV charging, solar and wind. The remaining files
provide supporting weather or load context. The 2025 clock is source local
solar time (LST).

- [Archived NASA POWER weather input](nasa-power-sennybridge-2025.csv)
- [Saved load checks](hourly-load-checks.json)
- [Source paths and hashes](../docs/source-map.csv)
