"""Draw selected dissertation figures from frozen output tables.

This module reads saved CSV/JSON and copies the original audit SVG. It imports
no simulation runner and does not write to any source directory.
"""

import argparse
import calendar
import csv
from datetime import datetime, timedelta
from decimal import Decimal
import json
from pathlib import Path
from shutil import copyfileobj
from statistics import fmean

import matplotlib

matplotlib.use("Agg")
from matplotlib import dates, pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import MaxNLocator

ROOT = Path(__file__).resolve().parents[2]
MONTHS = list(range(1, 13))
MONTH_NAMES = list(calendar.month_abbr)[1:]
C = {
    "PV": "#c98b1c", "Wind": "#217e71", "DG": "#ad543c", "BESS": "#4167a0",
    "Critical": "#424477", "Auxiliary": "#66845b", "EV": "#677686",
    "Original": "#26455c", "HDH": "#b05435", "Low": "#4167a0",
    "Central": "#217e71", "High": "#9a4866",
}
END_USES = {
    "C4ISR_and_command": ("Command and communications", C["Critical"]),
    "Medical_and_emergency_refrigeration": ("Medical and emergency refrigeration", "#8c6197"),
    "C4ISR_cooling": ("Dedicated ICT cooling", "#656da5"),
    "Perimeter_security_lighting": ("Perimeter security lighting", "#b389b5"),
    "Accommodation_ventilation": ("Accommodation ventilation", C["Auxiliary"]),
    "Accommodation_socket_loads": ("Accommodation sockets", "#83a16a"),
    "Accommodation_lighting": ("Accommodation lighting", "#b6c997"),
    "Catering_electric_cooking": ("Electric catering", "#756849"),
    "Workshops_and_maintenance": ("Workshops and maintenance", "#4b6a4b"),
    "Laundry": ("Laundry", "#a3aa57"),
    "Water_pumping_and_treatment": ("Water pumping and treatment", "#6e9f83"),
    "Common_area_lighting": ("Common-area lighting", "#d0dec0"),
    "Space_heating_electric": ("Space heating", "#bd7542"),
    "Summer_cooling_noncritical": ("Non-critical cooling", "#9fb8d0"),
    "fleet_AC_charging": ("EV charging (AC)", C["EV"]),
}

MONTHLY = "research_evidence/temperature_driven_load_calibration/monthly_baseline.csv"
HDH_MONTHLY = "research_evidence/hdh_heating_sensitivity/MONTHLY_ENERGY_COMPARISON.csv"
HDH_HOURLY = "research_evidence/hdh_heating_sensitivity/HDH_HOURLY_8760.csv"
PAIR = "research_evidence/hdh_heating_sensitivity/RESILIENCE_COMPARISON.csv"
PLANT = "week7/nextstage/outputs/winter_168h_original_equipment_plant_trace.csv"
COST = "week7/stage6/outputs/stage6_central_peacetime_outage_comparison.csv"
GRID = "week7/stage6/outputs/stage6_grid_limit_sweep_14.csv"
BESS = "week8/t17_bess_native_v1/BESS_VALIDATION_STATUS.json"
RE = "week8/t17_pv_wind_native_v1/PV_WIND_VALIDATION_STATUS.json"
D1 = "week8/t17_dg_bess_native_v1/D1_GATE_STATUS.json"
ARCH = "research_evidence/islanded_architecture_gate/figures/architecture_overview.svg"

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10.5, "axes.spines.top": False,
    "axes.spines.right": False, "axes.spines.left": False, "axes.spines.bottom": False,
    "text.color": "#18303e", "axes.labelcolor": "#18303e", "axes.axisbelow": True,
    "grid.color": "#dce5ea", "grid.linewidth": .75, "legend.frameon": False,
    "pdf.fonttype": 42, "figure.facecolor": "white",
})


def csv_rows(name):
    with (ROOT / name).open(encoding="utf-8-sig", newline="") as source:
        return list(csv.DictReader(source))


def json_record(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8-sig"))


def open_figure(caption):
    fig = plt.figure(figsize=(9.2, 5.8))
    fig.text(.115, .937, caption, fontsize=17, fontweight="bold", va="top")
    return fig


def axis(ax, unit, months=False):
    ax.set_ylabel(unit)
    ax.yaxis.set_major_locator(MaxNLocator(6))
    ax.grid(axis="y")
    ax.tick_params(length=0)
    if months:
        ax.set_xticks(MONTHS, MONTH_NAMES)
        ax.set_xlim(.4, 12.6)


def monthly_values(rows, col, factor=1):
    return [float(row[col]) * factor for row in rows]


def save(fig, directory, stem, caption):
    fig.text(.115, .022, caption, color="#3e5866", fontsize=8.6)
    directory.mkdir(parents=True, exist_ok=True)
    for fmt in ("png", "pdf"):
        meta = ({"Title": stem, "Subject": caption, "CreationDate": None, "ModDate": None}
                if fmt == "pdf" else {"Title": stem, "Description": caption})
        with (directory / f"{stem}.{fmt}").open("xb") as file:
            fig.savefig(file, format=fmt, dpi=300, metadata=meta)
    plt.close(fig)


def load_figures(out):
    month = csv_rows(MONTHLY)
    central = [r for r in month if r["case"] == "central"]
    assert len(central) == 12
    total = sum(Decimal(row["total_kwh_e"]) for row in central)
    per_use = [sum(Decimal(row[key + "_kwh_e"]) for row in central) for key in END_USES]
    assert sum(per_use) == total == Decimal("763901.095464")
    assert all(sum(Decimal(row[key + "_kwh_e"]) for key in END_USES) == Decimal(row["total_kwh_e"]) for row in central)

    fig = open_figure("Annual electricity by end use")
    ax = fig.add_axes([.060, .12, .53, .72])
    wedges, _ = ax.pie([float(value) for value in per_use], colors=[v[1] for v in END_USES.values()], startangle=95, counterclock=False,
                       wedgeprops={"width": .33, "edgecolor": "white", "linewidth": 1})
    ax.text(0, .06, "763.90", ha="center", va="center", fontsize=23, weight="bold")
    ax.text(0, -.17, "MWh electricity", ha="center", va="center", fontsize=10)
    labels = [f"{v[0]}  ·  {100*x/total:.1f}%" for v, x in zip(END_USES.values(), per_use, strict=True)]
    ax.legend(wedges, labels, loc="center left", bbox_to_anchor=(1.01, .50), fontsize=8.7, labelspacing=.69)
    save(fig, out, "02_annual_electricity", "Central baseline · 2025 LST · Modelled electricity at the AC load boundary.")

    fig = open_figure("Monthly electricity by end use")
    ax = fig.add_axes([.115, .30, .86, .54])
    bottom = [0.] * 12
    for key, (label, colour) in END_USES.items():
        y = monthly_values(central, key + "_kwh_e", .001)
        ax.bar(MONTHS, y, bottom=bottom, color=colour, label=label, width=.72, edgecolor="white", linewidth=.38)
        bottom = [a + b for a, b in zip(bottom, y)]
    axis(ax, "Electricity (MWh/month)", months=True)
    ax.legend(ncol=3, loc="upper left", bbox_to_anchor=(-.025, -.14), fontsize=7.9, handlelength=1.3)
    save(fig, out, "03_monthly_electricity", "Central baseline · 2025 LST · All 14 infrastructure categories and EV charging.")

    fig = open_figure("Low, Central and High monthly demand")
    ax = fig.add_axes([.115, .16, .86, .66])
    for case, marker in (("Low", "o"), ("Central", "s"), ("High", "D")):
        subset = [r for r in month if r["case"] == case.lower()]
        ax.plot(MONTHS, monthly_values(subset, "mean_kwh_e_per_day"), color=C[case], marker=marker,
                markersize=4.5, linewidth=2, label=case)
    axis(ax, "Mean electricity (kWh/day)", months=True)
    ax.legend(loc="lower center", ncol=3)
    ax.set_ylim(1600, 2600)
    save(fig, out, "04_low_central_high", "Frozen 2025 LST demand bounds · Daily means account for month length.")


def resource_figure(out):
    def profile(name):
        with (ROOT / f"data/v6_{name}_pu_index_value.csv").open(encoding="utf-8-sig", newline="") as handle:
            return [(int(i), float(pu)) for i, pu in csv.reader(handle)]

    pv, wind = profile("solar"), profile("wind")
    assert [i for i, _ in pv] == [i for i, _ in wind] == list(range(1, 8761))
    fig = open_figure("2025 available PV and wind resources")
    ax = fig.add_axes([.115, .16, .86, .65])
    for records, name, marker in ((pv, "PV", "o"), (wind, "Wind", "s")):
        offset, means = 0, []
        for month in MONTHS:
            count = 24 * calendar.monthrange(2025, month)[1]
            means.append(fmean(pu for _, pu in records[offset:offset + count]))
            offset += count
        ax.plot(MONTHS, means, color=C[name], marker=marker, linewidth=2.1, markersize=4.5, label=name)
    axis(ax, "Monthly mean available power (p.u.)", months=True)
    ax.set_ylim(0, .67)
    ax.legend(loc="upper center", ncol=2)
    save(fig, out, "05_available_pv_wind_2025", "2025 fixed LST · PV AC per kW DC nameplate; wind AC per kW rated · Before dispatch.")


def dispatch_figure(out):
    rows = csv_rows(PLANT)[:48]
    assert [int(r["hour_index"]) for r in rows] == list(range(48))
    hours = list(range(49))
    fig = open_figure("Diesel and battery dispatch during islanding")
    ax, state = fig.subplots(2, 1, sharex=True, gridspec_kw={"height_ratios": [1.55, 1]})
    fig.subplots_adjust(left=.115, right=.97, bottom=.145, top=.75, hspace=.22)
    dg = [float(r["dg_generated_kw"]) for r in rows]
    net = [float(r["bess_discharge_kw"])-float(r["bess_charge_kw"]) for r in rows]
    ax.stairs(dg, hours, baseline=None, color=C["DG"], linewidth=1.7, label="DG generation")
    ax.stairs(net, hours, baseline=None, color=C["BESS"], linewidth=1.7, label="BESS net discharge")
    ax.axhline(0, color="#bac7cf", linewidth=.7)
    fig.legend(*ax.get_legend_handles_labels(), loc="upper right", bbox_to_anchor=(.97, .87), ncol=2, fontsize=9)
    axis(ax, "Mean AC power (kW)")
    state.plot(hours, [100*float(rows[0]["soc_initial"]), *[100*float(r["soc_final"]) for r in rows]],
               color=C["BESS"], linewidth=2)
    state.axhline(30, color="#8398b3", linewidth=1, linestyle="--", label="Operating reserve")
    state.axhline(10, color="#525d68", linewidth=1, linestyle=":", label="Physical floor")
    axis(state, "BESS SOC (%)")
    state.set_xlabel("Elapsed outage time (h)")
    state.set_xlim(0, 48)
    state.set_ylim(0, 91)
    state.legend(loc="upper right", fontsize=8.6)
    save(fig, out, "06_dg_bess_dispatch", "1–2 January 2025 LST · Original Central S3-v2 · Negative BESS power denotes charge.")


def outage_figure(out):
    rows = csv_rows(PAIR)
    durations = [int(r["hours"]) for r in rows]
    assert durations == [24, 72, 168]
    x = [0, 1, 2]
    fig = open_figure("Winter outage sensitivity to heating timing")
    axes = fig.subplots(2, 2).flat
    fig.subplots_adjust(left=.115, right=.97, bottom=.15, top=.76, hspace=.40, wspace=.38)
    metrics = (("critical_ENS_kwh", "Critical ENS (kWh)"), ("critical_EA_pct", "Critical EA (%)"),
               ("total_ENS_kwh", "Total ENS (kWh)"), ("diesel_fuel_used_l", "Diesel consumed (L)"))
    for panel, (key, label) in zip(axes, metrics, strict=True):
        a, b = ([float(r[f"{name}_{key}"]) for r in rows] for name in ("original", "hdh"))
        if key == "critical_EA_pct":
            panel.plot(x, a, color=C["Original"], marker="o", linewidth=1.7)
            panel.plot(x, b, color=C["HDH"], marker="s", linewidth=1.7, linestyle="--")
            panel.set_ylim(94.5, 100.5)
        else:
            panel.bar([j-.18 for j in x], a, width=.35, color=C["Original"])
            panel.bar([j+.18 for j in x], b, width=.35, color=C["HDH"])
        axis(panel, label)
        panel.set_xticks(x, [f"{d} h" for d in durations])
    fig.legend(handles=[Line2D([], [], color=C[name], lw=7, label=("Original" if name=="Original" else "HDH 15.5 °C"))
                        for name in ("Original", "HDH")], loc="upper right", bbox_to_anchor=(.97, .88), ncol=2)
    save(fig, out, "07_winter_outage_energy_service", "1 January 2025 LST · Same hardware and dynamic EV feedback · Three deterministic, nested windows.")


def cost_figure(out):
    rows = [r for r in csv_rows(COST) if float(r["assumed_grid_import_limit_kw"]) == 250
            and abs(float(r["annual_hourly_requested_service_shortfall_kwh_NOT_EENS"])) < 1e-6]
    assert len(rows) == 9
    fig = open_figure("Normal-year cost and outage energy shortfall")
    ax = fig.add_axes([.145, .18, .81, .55])
    styles = {50: "o", 75: "s", 100: "D"}
    storage = {300: "#7395c4", 450: C["BESS"], 600: "#233f68"}
    for r in rows:
        renewable = int(float(r["pv_kw"]))
        battery = int(float(r["bess_kwh"]))
        ax.scatter(float(r["normal_year_cash_PV_PROXY_NOT_NPC_gbp"])/1e6,
                   float(r["52start_mean_168h_islanded_total_ENS_kwh"])/1000,
                   marker=styles[renewable], s=64, color=storage[battery], edgecolor="white", linewidth=.55)
    marker_notes = [Line2D([], [], marker=m, linestyle="", color="#34485a", label=f"{k} kW PV + wind each")
                    for k, m in styles.items()]
    colour_notes = [Line2D([], [], marker="o", linestyle="", color=v, label=f"{u} kWh BESS") for u, v in storage.items()]
    fig.legend(handles=marker_notes + colour_notes, loc="upper right", bbox_to_anchor=(.96, .87), ncol=2, fontsize=8.8)
    axis(ax, "Mean 168 h total ENS (MWh)")
    ax.set_xlabel("Normal-year 20-year discounted cash proxy (£m)")
    save(fig, out, "08_cost_resilience_screen", "Stage 6 · Central, 250 kW grid assumption · 52 deterministic starts · Cash proxy excludes outage costs.")


def hdh_figures(out):
    rows = csv_rows(HDH_MONTHLY)
    fig = open_figure("Annual heating energy redistributed within 2025")
    ax = fig.add_axes([.115, .16, .86, .65])
    key = "Space_heating_electric_kwh_e"
    series = [[r for r in rows if r["scenario"] == tag] for tag in ("A_CENTRAL", "B_HDH_15.5")]
    sums = [sum(Decimal(r[key]) for r in s) for s in series]
    assert all(abs(value-72768) <= Decimal("1e-7") for value in sums)
    for sub, colour, label, offset in zip(series, (C["Original"], C["HDH"]), ("Original", "HDH 15.5 °C"), (-.19, .19), strict=True):
        ax.bar([m+offset for m in MONTHS], monthly_values(sub, key, .001), width=.37, color=colour, label=label)
    axis(ax, "Space-heating electricity (MWh/month)", months=True)
    ax.legend(loc="upper center", ncol=2)
    ax.set_ylim(0, 13.7)
    save(fig, out, "09_hdh_heating_sensitivity", "Synthetic HDH case · Assumed 15.5 °C balance point · 72.768 MWh annual electric heating in each case.")

    rows = csv_rows(HDH_HOURLY)[:168]
    assert len(rows) == 168
    fig = open_figure("Original and HDH demand in the winter week")
    ax = fig.add_axes([.115, .165, .855, .64])
    times = [datetime.fromisoformat(r["timestamp_2025_LST"]) for r in rows]
    edges = dates.date2num([*times, times[-1]+timedelta(hours=1)])
    for col, series, style in (("original_total_kw", "Original", "-"), ("hdh_total_kw", "HDH", "--")):
        ax.stairs([float(r[col]) for r in rows], edges, baseline=None, color=C[series],
                  linestyle=style, linewidth=1.5, label=series if series=="Original" else "HDH 15.5 °C")
    ax.set_xlim(edges[0], edges[-1])
    ax.xaxis.set_major_locator(dates.DayLocator())
    ax.xaxis.set_major_formatter(dates.DateFormatter("%d %b"))
    axis(ax, "Total mean hourly demand (kW)")
    ax.legend(loc="upper right", ncol=2, fontsize=9)
    save(fig, out, "A01_hdh_winter_week", "1–7 January 2025 fixed LST · Synthetic annual-energy-neutral HDH · Before islanded EV feedback.")


def native_figure(out):
    bess = json_record(BESS)
    renewable = json_record(RE)["benchmarks"]
    dg = bess["DG_only_record"]
    gate = json_record(D1)
    assert gate["controller_feasibility"] == "NO-GO" and gate["native_runs"] == 0
    benchmark = {
        "DG 24 h": [dg["DG_24h_aggregate_energy_and_fuel"], dg["DG_24h_event_timing"], dg["DG_native_fixed_1h_steps_24h"]],
        **{f"BESS {label}": [status[key] for key in "ABC"] for label, status in bess["benchmarks"].items()},
        **{label: [renewable[key][cell] for cell in "ABC"] for label, key in (("PV P2", "P2"), ("Wind W2", "W2"))},
        "DG + BESS D1": [gate[key] for key in ("A_aggregate", "C_event_timing", "D_native_fixed_1h_visible_clock")],
    }
    fig = open_figure("Native MDT component evidence and D1 gate")
    ax = fig.add_axes([.115, .15, .86, .68])
    ax.axis("off")
    grid = ax.table(cellText=[[name, *values] for name, values in benchmark.items()],
                    colLabels=["Benchmark", "Aggregate", "Event / state*", "Visible fixed 1 h"],
                    cellLoc="left", colLoc="left", loc="upper left", bbox=[0, .01, 1, .98], colWidths=[.24, .21, .27, .28])
    grid.auto_set_font_size(False)
    grid.set_fontsize(10.1)
    background = {"PASS": "#e7f1ea", "FAIL": "#f7e4dd", "STRICT FAIL": "#f7e4dd",
                  "INCONCLUSIVE": "#f8efd8", "NOT RUN": "#e9eef2"}
    for (i, j), cell in grid.get_celld().items():
        label = cell.get_text().get_text()
        cell.set_edgecolor("#ffffff")
        cell.set_facecolor(background.get(label, "#f1f5f7"))
        if i == 0 or j == 0:
            cell.get_text().set_weight("bold")
    save(fig, out, "10_native_validation_scope", "*DG 24 h PASS is event timing only; direct tank state inconclusive. D1 joint run remains NO-GO / NOT RUN.")


def grid_figure(out):
    rows = csv_rows(GRID)
    fig = open_figure("Dependence on the assumed grid import limit")
    ax = fig.add_axes([.14, .17, .82, .66])
    for case in ("Central", "High"):
        items = sorted([r for r in rows if r["scenario"] == case.lower()], key=lambda r:float(r["grid_import_limit_kw"]))
        assert len(items) == 7
        ax.plot(monthly_values(items, "grid_import_limit_kw"),
                monthly_values(items, "hourly_requested_service_shortfall_kwh_NOT_EENS", .001),
                marker="o" if case=="Central" else "D", color=C[case], linewidth=2, label=case)
    axis(ax, "Annual requested shortfall (MWh)")
    ax.set_xlabel("Assumed grid import limit (kW)")
    ax.legend(loc="upper right")
    save(fig, out, "A02_grid_import_sensitivity", "Stage 6 · Dynamic EV requests can recur · This shortfall does not represent probability-weighted EENS.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    out = parser.parse_args().output_dir
    arch = out / "01_System_Architecture"
    arch.mkdir(parents=True, exist_ok=True)
    with (ROOT / ARCH).open("rb") as source, (arch / "01_islanded_energy_architecture.svg").open("xb") as file:
        copyfileobj(source, file)
    load_figures(out / "02_Load_Modelling")
    resource_figure(out / "03_PV_Wind_Resources")
    dispatch_figure(out / "04_BESS_Diesel_Dispatch")
    outage_figure(out / "05_Outage_Resilience")
    cost_figure(out / "06_Economic_Analysis")
    hdh_figures(out / "07_Sensitivity_Analysis")
    native_figure(out / "08_Model_Validation")
    grid_figure(out / "07_Sensitivity_Analysis")


if __name__ == "__main__":
    main()
