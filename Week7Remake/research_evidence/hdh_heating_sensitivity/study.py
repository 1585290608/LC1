"""Reproduce frozen demand and test an energy-neutral, capped winter heating reshaping."""

import argparse
from calendar import monthrange
import csv
from dataclasses import dataclass
from datetime import timedelta
from decimal import Decimal
from math import fsum, isclose, isfinite
from pathlib import Path
from types import FunctionType

from models.core.components import Loads
from research_evidence.temperature_driven_load_calibration.reproduce import (
    ENERGY_CATEGORIES,
    ROOT,
    TIMES,
    check,
    checked_number,
    csv_rows,
    read_temperature,
)
from week7.load_model import SCENARIOS, scheduled_hours
from week7.nextstage import screen

HEAT = "Space_heating_electric"
COOL = "Summer_cooling_noncritical"
EV = "fleet_AC_charging"
BASELINE = "MODELLED_BASELINE"
HDH = "TEMPERATURE_INFORMED_SYNTHETIC"
WEATHER = "NASA_POWER_METEOROLOGICAL_INPUT"
TEMPERATURE_BASES = tuple(map(Decimal, ("14.5", "15.5", "16.5")))
PRIMARY = Decimal("15.5")
ZERO = Decimal(0)
TOL = Decimal("0.0000001")
OUTAGE_TOL = 1e-7
DURATIONS = (24, 72, 168)
CATEGORIES = tuple(ENERGY_CATEGORIES)


class InfeasibleHeating(ValueError):
    """The eligible positive-weight hours cannot hold the annual heating target."""


@dataclass(frozen=True)
class Demand:
    name: str
    evidence: str
    groups: dict
    total: tuple
    critical: tuple
    auxiliary: tuple
    month_metrics: list
    base_c: Decimal | None = None
    power_cap_kw: Decimal | None = None
    scale_kw_per_degree: Decimal | None = None
    headroom_kwh: Decimal | None = None
    positive_hours: int | None = None


def by_month():
    for month in range(1, 13):
        hours = tuple(i for i, at in enumerate(TIMES) if at.month == month)
        yield month, monthrange(2025, month)[1], hours


def months_for(groups, totals):
    monthly = []
    for month, days, hours in by_month():
        group_energy = {key: sum(series[i] for i in hours) for key, series in groups.items()}
        values = [totals[i] for i in hours]
        kwh = sum(values)
        check(kwh == sum(group_energy.values()), f"Monthly end-use ledger failed in {month}")
        peak_hour = max(hours, key=totals.__getitem__)
        monthly.append({
            "month": month, "days": days, "total_kwh_e": kwh, "mean_kwh_e_per_day": kwh / days,
            "min_kw": min(values), "max_kw": totals[peak_hour], "first_peak_timestamp_LST": TIMES[peak_hour].isoformat(),
            "mean_kw": kwh / len(hours), "energy": group_energy,
        })
    for key in groups:
        check(sum(row["energy"][key] for row in monthly) == sum(groups[key]), f"Annual ledger {key}")
    check(sum(row["total_kwh_e"] for row in monthly) == sum(totals), "Annual total ledger")
    return monthly


def baseline(case, equipment):
    path = ROOT / f"week7/outputs/{case}_load_8760.csv"
    groups = {key: [] for key in CATEGORIES}
    total, critical, aux = [], [], []
    utilization = Decimal(str(SCENARIOS[case]["aux_utilisation"]))
    for hour, (at, row) in enumerate(zip(TIMES, csv_rows(path), strict=True)):
        check(int(row["hour_index"]) == hour and at.isoformat() == row["timestamp_LST"], f"{case}: timestamp {hour}")
        for category, (rated, tier) in equipment.items():
            expected = rated * (1 if tier == "c4isr" else utilization) if scheduled_hours(category, at) else ZERO
            value = checked_number(row[f"load_{category}_kw"])
            check(value == expected and value >= 0, f"{case}: frozen end-use mismatch at {at}: {category}")
            groups[category].append(value)
        groups[EV].append(checked_number(row["ev_kw"]))
        total.append(checked_number(row["total_kw"]))
        critical.append(checked_number(row["c4isr_kw"]))
        aux.append(checked_number(row["aux_kw"]))
        c4 = sum(groups[key][-1] for key, (_, tier) in equipment.items() if tier == "c4isr")
        other = sum(groups[key][-1] for key, (_, tier) in equipment.items() if tier == "aux")
        check(c4 == critical[-1] and other == aux[-1], f"{case}: baseline tier mismatch at {at}")
        check(ZERO <= groups[EV][-1] <= 70 and c4 + other + groups[EV][-1] == total[-1], f"{case}: EV or total ledger at {at}")
    groups = {key: tuple(values) for key, values in groups.items()}
    return Demand(f"A_{case.upper()}", BASELINE, groups, tuple(total), tuple(critical), tuple(aux), months_for(groups, total))


def allocate_heat(weights, cap, target):
    """Solve sum(min(cap, scale*weight))=target by removing saturated weights."""
    positive = sorted((w for w in weights if w > ZERO), reverse=True)
    capacity = cap * len(positive)
    if target < ZERO or target > capacity:
        raise InfeasibleHeating(f"{target} kWh target exceeds {capacity} kWh assigned capacity")
    if target == ZERO:
        return tuple(ZERO for _ in weights), ZERO, capacity

    remaining, weight_sum = target, sum(positive)
    saturated = 0
    for weight in positive:
        scale = remaining / weight_sum
        if scale * weight <= cap:
            break
        remaining -= cap
        weight_sum -= weight
        saturated += 1
    scale = cap / positive[-1] if saturated == len(positive) else remaining / weight_sum
    # Twelve decimals keep text round-trip error below the stated annual tolerance.
    load = tuple(min(cap, scale * weight).quantize(Decimal("0.000000000001")) for weight in weights)
    check(abs(sum(load) - target) <= TOL, "Annual heating allocation did not conserve energy")
    return load, scale, capacity


def reshape(original, temperature, cap, base):
    heating, cooling = original.groups[HEAT], original.groups[COOL]
    eligible = tuple(scheduled_hours(HEAT, at) and cool == ZERO for at, cool in zip(TIMES, cooling, strict=True))
    weights = tuple(max(base - temp, ZERO) if allowed else ZERO for temp, allowed in zip(temperature, eligible, strict=True))
    reshaped, scale, capacity = allocate_heat(weights, cap, sum(heating))
    changed = {**original.groups, HEAT: reshaped}
    check(all(changed[key] == original.groups[key] for key in CATEGORIES if key != HEAT), "Non-heating profile changed")
    total = tuple(old - old_heat + heat for old, old_heat, heat in zip(original.total, heating, reshaped, strict=True))
    aux = tuple(old - old_heat + heat for old, old_heat, heat in zip(original.auxiliary, heating, reshaped, strict=True))
    for i, (assigned, allowed) in enumerate(zip(reshaped, eligible, strict=True)):
        check(ZERO <= assigned <= cap and (weights[i] > ZERO or assigned == ZERO), f"Heating cap or HDH support at {TIMES[i]}")
        check(assigned == ZERO or (allowed and cooling[i] == ZERO), f"Forbidden heating at {TIMES[i]}")
        check(total[i] >= ZERO and sum(seq[i] for seq in changed.values()) == total[i], f"End-use ledger {TIMES[i]}")
        check(original.critical[i] + aux[i] + changed[EV][i] == total[i], f"Tier ledger {TIMES[i]}")
    check(abs(sum(total) - sum(original.total)) <= TOL, "Annual total not conserved")
    return Demand(f"B_HDH_{base}", HDH, changed, total, original.critical, aux, months_for(changed, total),
                  base, cap, scale, capacity - sum(heating), sum(w > 0 for w in weights))


def write_csv(path, rows):
    with path.open("x", encoding="utf-8", newline="") as out:
        writer = csv.DictWriter(out, list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def monthly_rows(cases, temperature, original):
    for demand in cases:
        base = demand.base_c or PRIMARY
        for (month, _, hours), metrics in zip(by_month(), demand.month_metrics, strict=True):
            days = metrics["days"]
            yield {
                "scenario": demand.name, "evidence_class": demand.evidence, "month_2025_LST": f"2025-{month:02}",
                "temperature_evidence_class": WEATHER, "T2M_mean_c": sum(temperature[i] for i in hours) / len(hours),
                "HDH_threshold_c": base, "monthly_HDH_all_hours_c_h": sum(max(base - temperature[i], ZERO) for i in hours),
                "monthly_HDH_eligible_c_h": sum(max(base - temperature[i], ZERO) for i in hours
                                               if scheduled_hours(HEAT, TIMES[i]) and not demand.groups[COOL][i]),
                **{key: value for key, value in metrics.items() if key not in ("month", "energy")},
                "delta_vs_original_central_kwh_e": metrics["total_kwh_e"] - original.month_metrics[month - 1]["total_kwh_e"],
                **{f"{key}_kwh_e": val for key, val in metrics["energy"].items()},
                **{f"{key}_kwh_e_per_day": val / days for key, val in metrics["energy"].items()},
            }


def hourly_rows(original, demand, temperature):
    for i, (at, outdoor) in enumerate(zip(TIMES, temperature, strict=True)):
        eligible = scheduled_hours(HEAT, at) and not demand.groups[COOL][i]
        hdh = max(demand.base_c - outdoor, ZERO)
        yield {
            "hour_index": i, "timestamp_2025_LST": at.isoformat(), "evidence_class": demand.evidence,
            "temperature_evidence_class": WEATHER, "outdoor_t2m_c": outdoor, "base_c": demand.base_c,
            "heating_eligible": int(eligible), "ambient_HDH_c_h": hdh, "effective_HDH_c_h": hdh if eligible else ZERO,
            "original_heating_kw": original.groups[HEAT][i], "original_total_kw": original.total[i],
            "hdh_heating_kw": demand.groups[HEAT][i], "hdh_total_kw": demand.total[i],
            "delta_total_kw": demand.total[i] - original.total[i],
            "critical_kw": demand.critical[i], "auxiliary_kw": demand.auxiliary[i], "ev_kw": demand.groups[EV][i],
            **{f"load_{key}_kw": demand.groups[key][i] for key in CATEGORIES if key != EV},
        }


def season_daily(demand, months):
    return sum(m["total_kwh_e"] for m in demand.month_metrics if m["month"] in months) / sum(
        m["days"] for m in demand.month_metrics if m["month"] in months)


def annual_row(demand, original, temperature, cap):
    delta = tuple(value - old for value, old in zip(demand.total, original.total, strict=True))
    month_delta = tuple(m["total_kwh_e"] - a["total_kwh_e"] for m, a in zip(demand.month_metrics, original.month_metrics, strict=True))
    peak_idx = demand.total.index(max(demand.total))
    max_idx = max(range(len(delta)), key=delta.__getitem__)
    min_idx = min(range(len(delta)), key=delta.__getitem__)
    increase_month = month_delta.index(max(month_delta)) + 1
    decrease_month = month_delta.index(min(month_delta)) + 1
    top = set(sorted(range(len(delta)), key=lambda i: (-demand.total[i], i))[:100])
    old_top = set(sorted(range(len(delta)), key=lambda i: (-original.total[i], i))[:100])
    base = demand.base_c or PRIMARY
    total = sum(demand.total)
    heating = sum(demand.groups[HEAT])
    winter = season_daily(demand, (12, 1, 2))
    summer = season_daily(demand, (6, 7, 8))
    return {
        "scenario": demand.name, "evidence_class": demand.evidence, "status": "PASS", "assumed_HDH_base_c": demand.base_c,
        "hours": len(TIMES), "annual_total_kwh_e": total, "annual_heating_kwh_e": heating,
        "annual_cooling_kwh_e": sum(demand.groups[COOL]), "annual_mean_kwh_e_per_day": total / 365,
        "annual_mean_kw": total / len(TIMES), "min_kw": min(demand.total), "peak_kw": demand.total[peak_idx],
        "first_peak_2025_LST": TIMES[peak_idx].isoformat(), "peak_delta_kw": max(demand.total) - max(original.total),
        "annual_total_delta_vs_central_kwh_e": total - sum(original.total),
        "annual_heating_delta_vs_central_kwh_e": heating - sum(original.groups[HEAT]),
        "winter_DJF_kwh_e_per_day": winter, "summer_JJA_kwh_e_per_day": summer,
        "winter_minus_summer_kwh_e_per_day": winter - summer, "heating_cap_kw": demand.power_cap_kw,
        "eligible_hours": sum(scheduled_hours(HEAT, at) and not cool for at, cool in zip(TIMES, demand.groups[COOL], strict=True)),
        "eligible_positive_HDH_hours": demand.positive_hours,
        "capped_hours": sum(value == cap for value in demand.groups[HEAT]),
        "feasible_capacity_headroom_kwh_e": demand.headroom_kwh,
        "scale_kw_per_degree": demand.scale_kw_per_degree,
        "annual_ambient_HDH_c_h": sum(max(base - v, ZERO) for v in temperature),
        "max_hourly_delta_vs_central_kw": delta[max_idx], "first_max_delta_2025_LST": TIMES[max_idx].isoformat(),
        "min_hourly_delta_vs_central_kw": delta[min_idx], "first_min_delta_2025_LST": TIMES[min_idx].isoformat(),
        "max_monthly_delta_vs_central_kwh_e": max(month_delta), "first_max_delta_month": increase_month,
        "min_monthly_delta_vs_central_kwh_e": min(month_delta), "first_min_delta_month": decrease_month,
        "top_100_hour_overlap_with_A_CENTRAL": len(top & old_top),
    }


def simulate_with_load(demand):
    """Give one invocation of the frozen solver its own input binding.

    The public runner has no load injection argument. Bind its unchanged code
    to a private namespace and avoid modifying screen.LOADS or dispatch code.
    """
    solver = screen.simulate
    profile = Loads(list(demand.critical), list(demand.auxiliary), list(demand.groups[EV]))
    namespace = {**solver.__globals__, "LOADS": {**screen.LOADS, "central": profile}}
    return FunctionType(solver.__code__, namespace, solver.__name__, solver.__defaults__, solver.__closure__)


def row_audit(trace, ev_trace, result, demand, hours):
    check(result["valid"] and len(trace) == hours and len(ev_trace) == hours * 7, f"Outage workflow rejected: {result['issues']}")
    check(result["feedback_model"] == "EV_DYNAMIC_MISSION_CONSTRAINED", "Unexpected EV denominator")
    check(result["bess_same_hour_both_directions"] == 0, "S3-v2 simultaneous BESS flows")
    residuals = (
        "AC_residual_kwh", "battery_residual_kwh", "fuel_residual_l", "DG_destination_residual_kwh", "UPS_residual_kwh",
    )
    max_residuals = {name: max(abs(row[name]) for row in trace) for name in residuals}
    check(all(isfinite(v) and v <= OUTAGE_TOL for v in max_residuals.values()), "Outage ledger residual exceeds tolerance")
    for i, row in enumerate(trace):
        check(row["hour_index"] == i and row["dt_h"] == 1, "Outage clock shifted")
        check(isclose(row["aux_required_kw"], float(demand.auxiliary[i]), rel_tol=0, abs_tol=OUTAGE_TOL), "Auxiliary injection absent")
        check(isclose(row["c4isr_required_kw"], float(demand.critical[i]), rel_tol=0, abs_tol=OUTAGE_TOL), "Critical input changed")
        check(row["fuel_final_l"] >= -OUTAGE_TOL, "Negative fuel inventory")
        if i:
            for final, initial in (("soc_final", "soc_initial"), ("fuel_final_l", "fuel_initial_l"), ("ups_final_kwh", "ups_initial_kwh")):
                check(isclose(trace[i - 1][final], row[initial], rel_tol=0, abs_tol=OUTAGE_TOL), f"Discontinuous {initial}")
    for prefix in ("c4isr", "aux", "ev"):
        ledger = max(abs(row[f"{prefix}_required_kw"] - row[f"{prefix}_served_kw"] - row[f"{prefix}_unserved_kw"]) for row in trace)
        check(ledger <= OUTAGE_TOL, f"Outage {prefix} energy ledger")
    check(isclose(fsum(row["ev_required_kw"] for row in trace), fsum(r["charging_requested_ac_kwh"] for r in ev_trace), rel_tol=0, abs_tol=OUTAGE_TOL),
          "EV demand denominator differs from fleet feedback")
    return max_residuals


def outage_comparison(original, adjusted):
    archived = {
        int(row["requested_h"]): row
        for row in csv_rows(ROOT / "week7/nextstage/outputs/mission_readiness_feedback_matrix.csv")
        if row["season"] == "winter" and row["pv_kw"] == "50.0" and row["wind_kw"] == "50.0" and row["bess_kwh"] == "300.0"
    }
    check(set(archived) == set(DURATIONS), "Saved winter case inputs not found")
    run_original, run_adjusted = simulate_with_load(original), simulate_with_load(adjusted)
    metric_fields = (
        "critical_required_kwh", "critical_ENS_kwh", "aux_ENS_kwh", "ev_ENS_kwh", "total_ENS_kwh",
        "critical_EA_fraction", "diesel_fuel_used_l", "fuel_end_l", "bess_end_soc",
        "vehicle_opportunities", "vehicle_departures_completed", "vehicle_departures_missed", "ev_actual_charging_ac_kwh",
    )
    for duration in DURATIONS:
        args = dict(start=0, hours=duration, pv_kw=50., wind_kw=50., bess_kwh=300.,
                    initial_soc=.7, fuel_l=2000., fleet_feedback=True, save_trace=True)
        untouched, _, _ = screen.simulate(**args)
        a, trace_a, ev_a = run_original(**args)
        b, trace_b, ev_b = run_adjusted(**args)
        residual_a = row_audit(trace_a, ev_a, a, original, duration)
        residual_b = row_audit(trace_b, ev_b, b, adjusted, duration)
        for key in metric_fields:
            saved = float(archived[duration][key])
            check(all(isclose(a[key], value, rel_tol=0, abs_tol=OUTAGE_TOL) for value in (untouched[key], saved)),
                  f"Historical parity failure for {duration} h: {key}")
        check(a["critical_required_kwh"] == b["critical_required_kwh"], "Critical service denominator differs")
        check(a["vehicle_opportunities"] == b["vehicle_opportunities"], "Mission opportunity denominator differs")
        results = {
            "hours": duration, "start_2025_LST": TIMES[0].isoformat(),
            "end_exclusive_2025_LST": (TIMES[0] + timedelta(hours=duration)).isoformat(),
            "status": "PYTHON_DETERMINISTIC_PAIRED", "original": BASELINE, "alternative": HDH,
            "PV_kw": 50, "wind_kw": 50, "DG_kw": 100, "BESS_kwh": 300, "PCS_kw": 90,
            "initial_SOC": .70, "initial_fuel_l": 2000, "fuel_curve": "MDT_DERIVED",
            "EV_mode_both": a["feedback_model"], "controller_both": a["controller"],
            "original_replay_parity": "PASS", "trace_energy_tolerance": OUTAGE_TOL,
        }
        both = {key: (a[key], b[key]) for key in metric_fields}
        both["critical_EA_pct"] = (100 * a["critical_EA_fraction"], 100 * b["critical_EA_fraction"])
        both["bess_min_soc"] = tuple(min(min(row["soc_initial"], row["soc_final"]) for row in trace) for trace in (trace_a, trace_b))
        both["total_required_kwh"] = tuple(fsum(fsum(row[f"{tier}_required_kw"] for tier in ("c4isr", "aux", "ev")) for row in trace)
                                           for trace in (trace_a, trace_b))
        both["space_heating_required_kwh"] = tuple(float(sum(d.groups[HEAT][:duration])) for d in (original, adjusted))
        both["ev_requested_ac_kwh"] = tuple(fsum(row["ev_required_kw"] for row in trace) for trace in (trace_a, trace_b))
        for label, values in both.items():
            results.update({f"original_{label}": values[0], f"hdh_{label}": values[1], f"delta_{label}": values[1] - values[0]})
        for label in residual_a:
            results[f"max_{label}"] = max(residual_a[label], residual_b[label])
        yield results


def main():
    from .plot_study import draw_figures

    options = argparse.ArgumentParser(description=__doc__)
    options.add_argument("--output-dir", required=True, type=Path)
    args = options.parse_args()
    output = args.output_dir
    equipment = {row["category"]: (checked_number(row["rated_kw"]), row["tier"])
                 for row in csv_rows(ROOT / "week7/config/equipment.csv")}
    check(set(equipment) | {EV} == set(CATEGORIES), "Equipment inventory differs")
    temperature = tuple(read_temperature(ROOT / "data/temp.csv", ROOT / "data/nasa-power-sennybridge-2025.csv").values())
    baselines = {case: baseline(case, equipment) for case in SCENARIOS}
    central = baselines["central"]
    check(sum(central.total) == Decimal("763901.095464") and max(central.total) == Decimal("195.091304"),
          "Central differs from the frozen reference")
    cap = equipment[HEAT][0]
    results, infeasible = {}, []
    for base in TEMPERATURE_BASES:
        try:
            results[base] = reshape(central, temperature, cap, base)
        except InfeasibleHeating as exc:
            infeasible.append((base, str(exc)))
    cases = [*baselines.values(), *results.values()]
    output.mkdir(parents=True, exist_ok=True)
    summary = [annual_row(case, central, temperature, cap) for case in cases]
    for base, why in infeasible:
        summary.append({"scenario": f"B_HDH_{base}", "evidence_class": HDH, "status": "INFEASIBLE",
                        "assumed_HDH_base_c": base, "heating_cap_kw": cap, "reason": why})
    write_csv(output / "HDH_SCENARIO_SUMMARY.csv", [{**row, "reason": row.get("reason", "")} for row in summary])
    write_csv(output / "MONTHLY_ENERGY_COMPARISON.csv", list(monthly_rows(cases, temperature, central)))
    if PRIMARY not in results:
        print("INFEASIBLE: primary HDH curve and outage comparison cannot be generated")
        return
    primary = results[PRIMARY]
    write_csv(output / "HDH_HOURLY_8760.csv", list(hourly_rows(central, primary, temperature)))
    draw_figures(output / "figures", central, primary, temperature)
    write_csv(output / "RESILIENCE_COMPARISON.csv", list(outage_comparison(central, primary)))
    print("Baseline, HDH checks, figures, and 3 paired outage windows completed.")


if __name__ == "__main__":
    main()
