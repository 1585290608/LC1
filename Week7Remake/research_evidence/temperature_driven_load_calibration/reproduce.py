"""Audit LC1's frozen load and T2M files and redraw the baseline figures."""

import argparse
import calendar
import csv
from datetime import datetime, timedelta
from decimal import Decimal
import hashlib
import json
from pathlib import Path

from week7.load_model import SCENARIOS, scheduled_hours

ROOT = Path(__file__).resolve().parents[2]
START = datetime(2025, 1, 1)
TIMES = tuple(START + timedelta(hours=hour) for hour in range(8760))
LABEL = "MODELLED_BASELINE"
ENERGY_CATEGORIES = {
    "C4ISR_and_command": ("Command & communications", "#25355f"),
    "Medical_and_emergency_refrigeration": ("Emergency refrigeration", "#845881"),
    "C4ISR_cooling": ("Dedicated ICT cooling", "#6984b3"),
    "Perimeter_security_lighting": ("Perimeter lighting", "#c8a2c4"),
    "Accommodation_ventilation": ("Accommodation ventilation", "#348880"),
    "Accommodation_socket_loads": ("Accommodation sockets", "#55aaa0"),
    "Accommodation_lighting": ("Accommodation lighting", "#a4d1cb"),
    "Catering_electric_cooking": ("Electric catering", "#a7674d"),
    "Workshops_and_maintenance": ("Workshop and maintenance", "#829049"),
    "Laundry": ("Laundry", "#acc079"),
    "Water_pumping_and_treatment": ("Water pumping and treatment", "#8c9ba8"),
    "Common_area_lighting": ("Common-area lighting", "#ccd5dd"),
    "Space_heating_electric": ("Space heating", "#d18539"),
    "Summer_cooling_noncritical": ("Non-critical summer cooling", "#7dacd2"),
    "fleet_AC_charging": ("EV charging (AC)", "#514d4c"),
}


def checked_number(value):
    number = Decimal(value)
    if not number.is_finite() or number == -999:
        raise ValueError(f"Missing or nonfinite value: {value}")
    return number


def check(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def csv_rows(path):
    with path.open(encoding="utf-8-sig", newline="") as source:
        yield from csv.DictReader(source)


def read_temperature(clean_path, raw_path):
    with raw_path.open(encoding="utf-8-sig", newline="") as source:
        for line in source:
            if line.strip() == "-END HEADER-":
                break
        raw = list(csv.DictReader(source))
    temperature = {}
    for at, clean, original in zip(TIMES, csv_rows(clean_path), raw, strict=True):
        raw_time = datetime(*(int(original[col]) for col in ("YEAR", "MO", "DY", "HR")))
        value = checked_number(clean["temp_c"])
        check(
            clean["datetime"] == at.isoformat() and raw_time == at and value == checked_number(original["T2M"]),
            f"T2M timestamp or value mismatch at {at}",
        )
        temperature[at] = value
    return temperature


def monthly_load(path, case, equipment, temperature):
    utilization = Decimal(str(SCENARIOS[case]["aux_utilisation"]))
    results = []
    source_total = Decimal(0)
    source_peak = Decimal(0)
    for hour, (at, row) in enumerate(zip(TIMES, csv_rows(path), strict=True)):
        check(int(row["hour_index"]) == hour and row["timestamp_LST"] == at.isoformat(), f"{case} timestamp {at}")
        if at.day == 1 and at.hour == 0:
            month = {
                "days": calendar.monthrange(2025, at.month)[1],
                "total": Decimal(0),
                "critical": Decimal(0),
                "auxiliary": Decimal(0),
                "peak": Decimal(0),
                "peak_time": "",
                "temperatures": [],
                "end_groups": dict.fromkeys(ENERGY_CATEGORIES, Decimal(0)),
            }
            results.append(month)
        tier_power = {"c4isr": Decimal(0), "aux": Decimal(0)}
        for name, (rated, tier) in equipment.items():
            active_power = rated if tier == "c4isr" else rated * utilization
            expected = active_power if scheduled_hours(name, at) else Decimal(0)
            power = checked_number(row[f"load_{name}_kw"])
            check(power == expected, f"{case} {at}: {name} differs from the baseline schedule")
            tier_power[tier] += power
            month["end_groups"][name] += power
        ev = checked_number(row["ev_kw"])
        total = checked_number(row["total_kw"])
        critical = checked_number(row["c4isr_kw"])
        aux = checked_number(row["aux_kw"])
        check(tier_power == {"c4isr": critical, "aux": aux}, f"{case} {at}: load tiers")
        check(Decimal(0) <= ev <= Decimal(70) and critical + aux + ev == total, f"{case} {at}: electricity balance")
        month["end_groups"]["fleet_AC_charging"] += ev
        month["total"] += total
        month["critical"] += critical
        month["auxiliary"] += aux
        month["temperatures"].append(temperature[at])
        if not month["peak_time"] or total > month["peak"]:
            month["peak"], month["peak_time"] = total, at.isoformat()
        source_total += total
        source_peak = max(source_peak, total)

    check(all(len(month["temperatures"]) == 24 * month["days"] for month in results), f"{case} month coverage")
    check(all(sum(month["end_groups"].values()) == month["total"] for month in results), f"{case} category reconciliation")
    check(sum(month["total"] for month in results) == source_total, f"{case} annual reconciliation")
    check(max(month["peak"] for month in results) == source_peak, f"{case} annual peak")
    return results


def formatted(value):
    return f"{value:.6f}"


def write_monthly(path, scenarios):
    fields = [
        "evidence_class", "case", "month_2025_LST", "days", "hours",
        "outdoor_t2m_mean_c", "outdoor_t2m_min_c", "outdoor_t2m_max_c",
        "total_kwh_e", "mean_kwh_e_per_day", "peak_kw", "first_peak_timestamp_LST",
        "critical_subtotal_kwh_e", "auxiliary_subtotal_kwh_e", "space_heating_kwh_e_per_day",
        "summer_cooling_kwh_e_per_day",
    ] + [f"{name}_kwh_e" for name in ENERGY_CATEGORIES]
    with path.open("x", encoding="utf-8", newline="") as out:
        writer = csv.writer(out, lineterminator="\n")
        writer.writerow(fields)
        for case, results in scenarios.items():
            for index, month in enumerate(results, 1):
                temps = month["temperatures"]
                parts = month["end_groups"]
                days = month["days"]
                writer.writerow([
                    LABEL, case, f"2025-{index:02}", days, len(temps),
                    formatted(sum(temps) / len(temps)), min(temps), max(temps),
                    formatted(month["total"]), formatted(month["total"] / days), formatted(month["peak"]),
                    month["peak_time"], formatted(month["critical"]), formatted(month["auxiliary"]),
                    formatted(parts["Space_heating_electric"] / days),
                    formatted(parts["Summer_cooling_noncritical"] / days),
                    *[formatted(parts[name]) for name in ENERGY_CATEGORIES],
                ])


def write_summary(path, scenarios, temperature, inputs):
    verified = {
        "evidence_class": LABEL,
        "clock": "2025 NASA POWER fixed LST, UTC+0 index band, no DST",
        "hourly_matches_per_case": len(temperature),
        "offset_hours": 0,
        "missing_duplicate_nonfinite_or_shifted_hours": 0,
        "raw_processed_T2M_mismatches": 0,
        "max_hourly_tier_or_site_residual_kw": "0",
        "baseline_input_sha256": {str(p.relative_to(ROOT).as_posix()): digest(p) for p in inputs},
        "scenarios": {},
    }
    for case, results in scenarios.items():
        peak = max(results, key=lambda month: month["peak"])
        measures = {
            "annual_kwh_e": formatted(sum(m["total"] for m in results)),
            "monthly_to_annual_residual_kwh_e": "0.000000",
            "peak_kw": formatted(peak["peak"]),
            "first_peak_timestamp_LST": peak["peak_time"],
            "annual_heating_kwh_e": formatted(sum(m["end_groups"]["Space_heating_electric"] for m in results)),
            "annual_noncritical_cooling_kwh_e": formatted(sum(m["end_groups"]["Summer_cooling_noncritical"] for m in results)),
        }
        for season, indices in {"DJF": (11, 0, 1), "JJA": (5, 6, 7)}.items():
            months = [results[index] for index in indices]
            times = [t for entry in months for t in entry["temperatures"]]
            days = sum(m["days"] for m in months)
            measures[season] = {
                "days": days,
                "mean_t2m_c": formatted(sum(times) / len(times)),
                "mean_kwh_e_per_day": formatted(sum(m["total"] for m in months) / days),
                "heating_kwh_e": formatted(sum(m["end_groups"]["Space_heating_electric"] for m in months)),
                "noncritical_cooling_kwh_e": formatted(sum(m["end_groups"]["Summer_cooling_noncritical"] for m in months)),
            }
        verified["scenarios"][case] = measures
    with path.open("x", encoding="utf-8", newline="\n") as out:
        json.dump(verified, out, indent=2)
        out.write("\n")


def draw_figures(destination, scenarios):
    import matplotlib

    matplotlib.use("Agg")
    from matplotlib import pyplot as plt
    from matplotlib.ticker import MaxNLocator

    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 10,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.spines.left": False,
        "axes.spines.bottom": False,
        "axes.titleweight": "bold",
        "axes.titlepad": 12,
        "axes.labelcolor": "#263743",
        "text.color": "#1d2d37",
        "xtick.color": "#344752",
        "ytick.color": "#344752",
        "grid.color": "#dce5ea",
        "grid.linewidth": 0.8,
        "legend.frameon": False,
        "figure.facecolor": "white",
    })
    months = range(1, 13)
    abbreviations = list(calendar.month_abbr)[1:]
    central = scenarios["central"]
    colours = {"low": "#3867a6", "central": "#2c7e74", "high": "#a04c38"}

    def monthly_axes(ax, ylabel):
        ax.set_xticks(months, abbreviations)
        ax.set_xlim(0.45, 12.55)
        ax.set_ylabel(ylabel)
        ax.set_axisbelow(True)
        ax.grid(axis="y")
        ax.tick_params(length=0)
        ax.yaxis.set_major_locator(MaxNLocator(7))

    def save(fig, filename, footer):
        fig.text(0.10, 0.023, footer, fontsize=8, color="#516771")
        with (destination / filename).open("xb") as out:
            fig.savefig(out, format="png", dpi=300, metadata={"Description": footer})
        plt.close(fig)

    fig, ax = plt.subplots(figsize=(11, 6.6))
    fig.subplots_adjust(left=0.10, right=0.975, bottom=0.31, top=0.89)
    bottom = [0.0] * 12
    for name, (label, colour) in ENERGY_CATEGORIES.items():
        height = [float(m["end_groups"][name] / 1000) for m in central]
        ax.bar(months, height, width=0.72, bottom=bottom, label=label, color=colour, edgecolor="white", linewidth=0.4)
        bottom = [a + b for a, b in zip(bottom, height)]
    ax.set_title("Central demand by electrical end use", loc="left", fontsize=17)
    monthly_axes(ax, "Monthly electricity (MWh)")
    ax.legend(ncol=3, loc="upper left", bbox_to_anchor=(-0.015, -0.115), fontsize=9, handlelength=1.35)
    save(fig, "01_monthly_stacked_end_uses.png", f"{LABEL}   |   Frozen Central load, fixed 2025 LST   |   Electricity at the camp AC load boundary")

    fig, ax = plt.subplots(figsize=(9, 5.3))
    fig.subplots_adjust(left=0.12, right=0.95, bottom=0.17, top=0.87)
    temps = [float(sum(m["temperatures"]) / len(m["temperatures"])) for m in central]
    energy = [float(m["total"] / m["days"]) for m in central]
    ax.scatter(temps, energy, color=colours["central"], s=52, edgecolor="white", linewidth=0.7, zorder=3)
    label_offsets = [(2, -14), (-16, 9), (3, -15), (3, 8), (-29, -14), (-9, 9), (6, -3), (0, -15), (8, 7), (4, 7), (-16, 9), (4, 9)]
    for temperature, demand, name, offset in zip(temps, energy, abbreviations, label_offsets):
        ax.annotate(name, (temperature, demand), xytext=offset, textcoords="offset points", fontsize=8.5)
    ax.set_ylim(min(energy) - 35, max(energy) + 38)
    ax.set_xlim(min(temps) - 1, max(temps) + 1)
    ax.set_xlabel("Monthly mean outdoor temperature (°C)")
    ax.set_ylabel("Mean daily electricity (kWh/day)")
    ax.set_title("Calendar demand and outdoor temperature", loc="left", fontsize=16)
    ax.grid()
    save(fig, "02_daily_electricity_vs_t2m.png", f"{LABEL}   |   Central load + NASA POWER T2M, 2025   |   Points are monthly aggregates")

    fig, (ax_heat, ax_temp) = plt.subplots(2, 1, figsize=(9, 6.4), sharex=True, gridspec_kw={"height_ratios": [1.7, 1]})
    fig.subplots_adjust(left=0.12, right=0.96, bottom=0.14, top=0.88, hspace=0.22)
    ax_heat.bar(months, [float(m["end_groups"]["Space_heating_electric"] / m["days"]) for m in central],
                width=0.65, color="#d18539", label="Space heating")
    ax_heat.bar(months, [float(m["end_groups"]["Summer_cooling_noncritical"] / m["days"]) for m in central],
                width=0.65, color="#7dacd2", label="Non-critical summer cooling")
    ax_heat.set_title("Scheduled HVAC electricity and outdoor temperature", loc="left", fontsize=15)
    ax_heat.legend(loc="upper center", bbox_to_anchor=(0.5, 0.99), ncol=2)
    ax_heat.set_ylim(0, 360)
    ax_heat.tick_params(labelbottom=False)
    monthly_axes(ax_heat, "Mean electricity (kWh/day)")
    ax_temp.plot(months, temps, color="#3c677b", linewidth=2.2, marker="o", markersize=4)
    monthly_axes(ax_temp, "Mean NASA T2M (°C)")
    save(fig, "03_scheduled_hvac_and_t2m.png", f"{LABEL}   |   Central calendar HVAC   |   Temperature-adjusted series pending calibration")

    fig, ax = plt.subplots(figsize=(9, 5.3))
    fig.subplots_adjust(left=0.115, right=0.96, bottom=0.17, top=0.86)
    for case, results in scenarios.items():
        ax.plot(months, [float(m["total"] / m["days"]) for m in results], color=colours[case],
                linewidth=2.15, marker={"low": "o", "central": "s", "high": "D"}[case],
                markersize=4.4, label=case.title())
    monthly_axes(ax, "Mean daily electricity (kWh/day)")
    ax.set_title("Low, Central and High monthly demand", loc="left", fontsize=16)
    ax.set_ylim(1500, 2650)
    ax.legend(loc="lower center", bbox_to_anchor=(0.52, 0.015), ncol=3)
    save(fig, "04_low_central_high_monthly.png", f"{LABEL}   |   Frozen 2025 demand envelopes   |   Daily averages use each calendar month's length")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--figure-dir", type=Path, required=True)
    args = parser.parse_args()
    equipment_path = ROOT / "week7/config/equipment.csv"
    equipment = {row["category"]: (checked_number(row["rated_kw"]), row["tier"]) for row in csv_rows(equipment_path)}
    check(set(equipment) | {"fleet_AC_charging"} == set(ENERGY_CATEGORIES), "Category inventory mismatch")
    load_paths = {case: ROOT / f"week7/outputs/{case}_load_8760.csv" for case in SCENARIOS}
    raw_path = ROOT / "data/nasa-power-sennybridge-2025.csv"
    clean_path = ROOT / "data/temp.csv"
    temperature = read_temperature(clean_path, raw_path)
    scenarios = {case: monthly_load(path, case, equipment, temperature) for case, path in load_paths.items()}

    args.output_dir.mkdir(parents=True, exist_ok=True)
    args.figure_dir.mkdir(parents=True, exist_ok=True)
    write_monthly(args.output_dir / "monthly_baseline.csv", scenarios)
    write_summary(args.output_dir / "baseline_reconciliation.json", scenarios, temperature,
                  [equipment_path, raw_path, clean_path, *load_paths.values()])
    draw_figures(args.figure_dir, scenarios)


if __name__ == "__main__":
    main()
