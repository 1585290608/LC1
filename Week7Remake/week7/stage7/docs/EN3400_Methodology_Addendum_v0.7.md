# EN3400 LC1 — Methodology v0.7 Addendum: Transparent Verification and External Benchmarks

**Draft for supervisor review, 19 November 2026. Not an approved change to the study scope.**
This is an **addendum to Stage 5 v0.5 and Stage 6 v0.6**, not a replacement for those chapters.

## Verification hierarchy

Five distinct levels are used in this dissertation:

1. **Source-preservation and regression testing.** The A/B/S3 original files are retained, original hashes are checked, and existing Python tests are re-run. This establishes repeatability rather than correctness.
2. **Analytical component benchmarks.** Hand-derived, dimensionally consistent test cases are compared with the Python implementation for the DG start-up/fuel constraint, renewable curtailment, load-priority allocation, battery charge/discharge and grid import limit. The fixture's constant 0.25 L/kWh is intentionally distinct from the production piecewise `MDT_DERIVED` fuel curve.
3. **Independent hourly ledger reconciliation.** Output traces are read as raw CSV and independently assessed using conservation equations and operational bounds without accepting the dispatcher's reported residuals as proof. Five archived traces representing 18,024 one-hour samples have been inspected in Stage 7.
4. **External simulation comparison.** Native Microgrid Design Toolkit or HOMER Pro inputs, scenarios, dispatch controller semantics and output fields must be matched to the Python model. The historically retained 24-hour DG-only MDT check does not satisfy this requirement for the hybrid or revised site.
5. **Physical/site validation.** Real-site demand measurement, engineering approvals, equipment specifications and vehicle charge/discharge tests would be required for a deployment claim. None is claimed.

## Reconciliation equations

For one-hour AC dispatch, with powers expressed as average kW over the hour,

\[
E_{\mathrm{RE,used}} + E_{\mathrm{DG,generated}}-E_{\mathrm{DG,dumped}} + E_{\mathrm{grid,import}} + E_{\mathrm{BESS,dis}}+E_{\mathrm{UPS,dis}}
=E_{\mathrm{served}}+E_{\mathrm{BESS,ch}}+E_{\mathrm{UPS,ch}}+E_{\mathrm{grid,export}}.
\]

Battery DC energy obeys

\[
C_{\mathrm{BESS}}(SOC_{t+1}-SOC_t)=\eta_{\mathrm{ch}}E_{\mathrm{BESS,ch,AC}} - E_{\mathrm{BESS,dis,AC}}/\eta_{\mathrm{dis}}.
\]

The hour-start replenishment convention is

\[
F_{\mathrm{initial},t}=F_{\mathrm{final},t-1}+F_{\mathrm{accepted},t},\quad
F_{\mathrm{final},t}=F_{\mathrm{initial},t}-F_{\mathrm{consumed},t}.
\]

## Economic reproducibility and double-counting boundary

The selected normal-year 20-year discounted cash-flow calculation is reconstructed line by line for 27 fully serviced 250 kW *hypothetical* grid import cases, resulting in 567 yearly records. Year 0 includes initial CAPEX and initial fuel working-stock purchase; years 1–20 include fixed O&M, normal grid energy/standing charges, and previously scheduled replacement expenditures; Year 20 credits working-stock recovery. Every row is discounted at the inherited illustrative real discount rate of 3% per annum. Neither stochastic outage incidence nor physical fuel resupply is incorporated in this replay; therefore no event is counted twice, but this **is not a full NPC or HOMER output**.

No direct summation of the isolated 168-hour ENS and the 8,760h normal-year electricity cost is undertaken. A future integrated NPC would require time-matched outage event sampling, explicit nonoverlap with normal grid purchases, fuel/restoration costs, reliability data, service-equivalence, realistic component lifetime and economic input verification.

## Native data export notes

The fixed 2025 time series are written as plain ASCII text, one numeric kW load per line and no header, with 8,760 rows each. This meets the file-layout requirement described in HOMER Pro documentation for primary load import; it does **not** ensure equivalent DER, storage, EV or operational model fidelity. For the project, PV and wind are archived as output capacity factors and must not be presented as weather resource measurements unless converted and justified.

## Research limitations

Site and 7-EV fleet data remain representative assumptions rather than commissioned operational data; constraints are energy adequacy only, not AC voltage/stability/protection compliance; HOMER/MDT native versions and licences have not been exercised in Stage 7; acceptance of the site design basis and dissertation scope awaits supervisor review.
