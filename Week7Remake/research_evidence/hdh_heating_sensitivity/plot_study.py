"""Dissertation plots for the LC1 timing-only heating experiment."""

import calendar
from datetime import timedelta

import matplotlib

matplotlib.use("Agg")
from matplotlib import dates, pyplot as plt
from matplotlib.ticker import MaxNLocator

from research_evidence.temperature_driven_load_calibration.reproduce import ENERGY_CATEGORIES, TIMES


ORIGINAL = "#31577a"
ALTERNATIVE = "#b25536"
TEMPERATURE = "#417b76"
TEXT = "#1c2c38"

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10, "font.weight": "normal",
    "text.color": TEXT, "axes.labelcolor": TEXT, "axes.titleweight": "bold",
    "axes.spines.left": False, "axes.spines.right": False, "axes.spines.top": False, "axes.spines.bottom": False,
    "axes.axisbelow": True, "grid.color": "#dce4e9", "grid.linewidth": 0.75,
    "xtick.color": "#3f5663", "ytick.color": "#3f5663", "legend.frameon": False,
    "pdf.fonttype": 42, "figure.facecolor": "white",
})

MONTHS = list(range(1, 13))
MONTH_NAMES = list(calendar.month_abbr)[1:]
HEAT = "Space_heating_electric"


def draw_figures(output, original, adjusted, air):
    output.mkdir(parents=True, exist_ok=True)

    def finish(fig, stem, title, caption):
        fig.text(.10, .026, caption, color="#3f5663", fontsize=8.4)
        for ext in ("png", "pdf"):
            metadata = ({"Title": title, "Subject": caption, "CreationDate": None, "ModDate": None}
                        if ext == "pdf" else {"Title": title, "Description": caption})
            with (output / f"{stem}.{ext}").open("xb") as file:
                fig.savefig(file, format=ext, dpi=300, metadata=metadata)
        plt.close(fig)

    def time_axis(ax, unit):
        ax.set_ylabel(unit)
        ax.grid(axis="y")
        ax.yaxis.set_major_locator(MaxNLocator(6))
        ax.tick_params(length=0)

    def monthly_axis(ax, unit):
        time_axis(ax, unit)
        ax.set_xticks(MONTHS, MONTH_NAMES)
        ax.set_xlim(.44, 12.56)

    def values(case, key):
        return [float(month[key]) for month in case.month_metrics]

    def end_use(case, category):
        return [float(month["energy"][category]) / 1000 for month in case.month_metrics]

    def pair(ax, original_values, hdh_values, unit):
        ax.plot(MONTHS, original_values, label="Original calendar", color=ORIGINAL, linewidth=2.1,
                marker="o", markersize=4.5)
        ax.plot(MONTHS, hdh_values, label="HDH 15.5 °C", color=ALTERNATIVE, linewidth=2.1, linestyle="--",
                marker="s", markersize=4.1)
        monthly_axis(ax, unit)

    title = "Monthly electricity by end use"
    fig, ax = plt.subplots(figsize=(11, 6.6))
    fig.subplots_adjust(left=.10, right=.98, bottom=.31, top=.87)
    ax.set_title(title, loc="left", fontsize=17, pad=17)
    bottom = [0] * 12
    for key, (label, colour) in ENERGY_CATEGORIES.items():
        heights = end_use(original, key)
        ax.bar(MONTHS, heights, width=.74, bottom=bottom, label=label, color=colour,
               edgecolor="white", linewidth=.42)
        bottom = [a + b for a, b in zip(bottom, heights)]
    monthly_axis(ax, "Electricity (MWh/month)")
    ax.legend(ncol=3, loc="upper left", bbox_to_anchor=(-.012, -.12), fontsize=9.1, handlelength=1.4)
    finish(fig, "01_monthly_electricity_by_end_use", title,
           "MODELLED_BASELINE · Central camp electricity demand · Fixed 2025 LST")

    title = "Annual electricity by end use"
    fig, ax = plt.subplots(figsize=(10.3, 6.2))
    fig.subplots_adjust(left=.07, right=.52, bottom=.13, top=.87)
    fig.text(.10, .90, title, fontweight="bold", fontsize=17)
    annual = [float(sum(original.groups[key])) for key in ENERGY_CATEGORIES]
    total = sum(annual)
    wedges, _ = ax.pie(annual, colors=[value[1] for value in ENERGY_CATEGORIES.values()], startangle=95,
                       counterclock=False, wedgeprops={"width": 0.34, "edgecolor": "white", "linewidth": 1.1})
    ax.text(0, .07, f"{total/1000:,.1f}", ha="center", va="center", fontsize=27, fontweight="bold")
    ax.text(0, -.17, "MWh electricity", ha="center", va="center", fontsize=10)
    ax.legend(wedges, [f"{v[0]}  ·  {100*x/total:.1f}%" for v, x in zip(ENERGY_CATEGORIES.values(), annual, strict=True)],
              loc="center left", bbox_to_anchor=(1.04, .50), fontsize=10, labelspacing=.75, handlelength=1.1)
    finish(fig, "02_annual_electricity_breakdown", title,
           "MODELLED_BASELINE · Central annual shares · Same categories and colour key as Figure 1")

    title = "Calendar demand and outdoor temperature"
    fig, (ax, temp_axis) = plt.subplots(2, 1, figsize=(9.1, 6.1), sharex=True)
    fig.subplots_adjust(left=.125, right=.96, bottom=.14, top=.87, hspace=.18)
    t_means = [sum(float(t) for t, at in zip(air, TIMES, strict=True) if at.month == month)
               / (original.month_metrics[month - 1]["days"] * 24) for month in MONTHS]
    ax.plot(MONTHS, values(original, "mean_kwh_e_per_day"), color=ORIGINAL, linewidth=2.2, marker="o", markersize=5)
    ax.set_title(title, loc="left", fontsize=16, pad=16)
    monthly_axis(ax, "Mean electricity (kWh/day)")
    temp_axis.plot(MONTHS, t_means, color=TEMPERATURE, linewidth=2.2, marker="o", markersize=5)
    monthly_axis(temp_axis, "Mean outdoor T2M (°C)")
    finish(fig, "03_daily_demand_and_temperature", title,
           "MODELLED_BASELINE · NASA_POWER_METEOROLOGICAL_INPUT · Monthly values paired on fixed 2025 LST")

    title = "Space heating under the same annual energy budget"
    fig, (ax, weight_ax) = plt.subplots(2, 1, figsize=(9.15, 6.3), sharex=True,
                                        gridspec_kw={"height_ratios": [1.75, 1]})
    fig.subplots_adjust(left=.115, right=.97, bottom=.13, top=.86, hspace=.25)
    offsets = [-.19, .19]
    for off, case, color, legend in zip(offsets, (original, adjusted), (ORIGINAL, ALTERNATIVE),
                                        ("Original calendar", "HDH 15.5 °C"), strict=True):
        ax.bar([m + off for m in MONTHS], end_use(case, HEAT), width=.36, color=color, label=legend)
    ax.set_title(title, loc="left", fontsize=15.5, pad=15)
    monthly_axis(ax, "Heating electricity (MWh)")
    ax.legend(loc="upper center", bbox_to_anchor=(.5, 1.00), ncol=2)
    ax.set_ylim(0, max(end_use(adjusted, HEAT) + end_use(original, HEAT)) * 1.25)
    weights = [0.] * 12
    for at, outdoor, initial_heat in zip(TIMES, air, original.groups[HEAT], strict=True):
        if initial_heat > 0:
            weights[at.month - 1] += max(float(adjusted.base_c - outdoor), 0)
    weight_ax.fill_between(MONTHS, weights, color=TEMPERATURE, alpha=.17)
    weight_ax.plot(MONTHS, weights, color=TEMPERATURE, linewidth=1.9, marker="o", markersize=3.7)
    monthly_axis(weight_ax, "Eligible HDH (°C·h)")
    finish(fig, "04_calendar_vs_hdh_heating", title,
           "MODELLED_BASELINE and TEMPERATURE_INFORMED_SYNTHETIC · Annual heating demand is 72.768 MWh in both cases")

    title = "Monthly demand and peak power"
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9.1, 6.2), sharex=True)
    fig.subplots_adjust(left=.135, right=.96, bottom=.14, top=.85, hspace=.25)
    pair(ax1, values(original, "mean_kwh_e_per_day"), values(adjusted, "mean_kwh_e_per_day"), "Mean electricity (kWh/day)")
    ax1.set_title(title, loc="left", fontsize=16, pad=21)
    ax1.legend(loc="lower center", bbox_to_anchor=(.47, -.12), ncol=2)
    pair(ax2, values(original, "max_kw"), values(adjusted, "max_kw"), "Peak hourly power (kW)")
    finish(fig, "05_calendar_vs_hdh_total_load", title,
           "MODELLED_BASELINE and TEMPERATURE_INFORMED_SYNTHETIC · Identical calendar, equipment and non-heating demand")

    title = "Hourly demand during the representative winter week"
    fig, (ax, heating_ax) = plt.subplots(2, 1, figsize=(10.7, 6.25), sharex=True,
                                         gridspec_kw={"height_ratios": [1.7, 1]})
    fig.subplots_adjust(left=.105, right=.97, bottom=.14, top=.85, hspace=.21)
    date_edges = dates.date2num([*TIMES[:168], TIMES[167] + timedelta(hours=1)])
    for case, colour, style, label in ((original, ORIGINAL, "-", "Original calendar"),
                                         (adjusted, ALTERNATIVE, "--", "HDH 15.5 °C")):
        ax.stairs([float(v) for v in case.total[:168]], date_edges, baseline=None,
                  color=colour, linewidth=1.5, linestyle=style, label=label)
        heating_ax.stairs([float(v) for v in case.groups[HEAT][:168]], date_edges, baseline=None,
                          color=colour, linewidth=1.5, linestyle=style)
    ax.set_title(title, loc="left", fontsize=16, pad=19)
    ax.legend(loc="upper center", bbox_to_anchor=(.52, 1.015), ncol=2)
    ax.set_ylim(top=max(float(max(original.total[:168])), float(max(adjusted.total[:168]))) * 1.15)
    time_axis(ax, "Total electrical demand (kW)")
    time_axis(heating_ax, "Space heating (kW)")
    heating_ax.set_ylim(-1, 33)
    heating_ax.set_xlim(date_edges[0], date_edges[-1])
    heating_ax.xaxis.set_major_locator(dates.DayLocator())
    heating_ax.xaxis.set_major_formatter(dates.DateFormatter("%d %b"))
    finish(fig, "06_representative_winter_week", title,
           "Fixed 2025 LST · 1–7 January, 168 hours · Camp load profiles before islanded EV state feedback")
