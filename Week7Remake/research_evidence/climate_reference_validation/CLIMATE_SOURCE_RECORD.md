# Sennybridge No 2 — Met Office climate reference for LC1

**Saved:** 21 November 2026. **Project:** LC1 / EN3400 Hybrid Microgrids for Defence Applications. **Purpose:** source registration, baseline climate context and input-uncertainty assessment; not replacement of frozen model inputs.

## 1. Verified primary source and link correction

- **Primary Met Office station climatology (1991–2020):** https://www.metoffice.gov.uk/research/climate/maps-and-data/location-specific-long-term-averages/gcm2jvb2g
- **Station catalogue:** https://www.metoffice.gov.uk/research/climate/maps-and-data/uk-synoptic-and-climate-stations
- Met Office station catalogue identifies **Sennybridge No 2** at approximately **52.0629° N, −3.61341° W**.
- The link provided by the user ended in `/gcm2jvc0f` and could not be retrieved. The page actually verified to display **Sennybridge No 2, 1991–2020** ends in **`/gcm2jvb2g`**. The distinction matters when citing the thesis.
- The table provides monthly mean **daily maximum**, mean **daily minimum**, days of **air frost**, **rainfall**, rainy days (≥1 mm), and mean **10 m wind speed in knots**. Station **sunshine hours are shown as unavailable (dash)** for this period; do not substitute regional sunshine data and label it station-measured.

The file `SENNYBRIDGE_MET_OFFICE_1991_2020_MONTHLY.csv` transcribes the primary station table. The `station_derived_mean_C` column is **calculated here as (monthly mean daily max + monthly mean daily min)/2**, not a separately reported observed mean-temperature column. The m/s wind column is a unit conversion, **1 knot = 0.5144444444 m/s**.

### Verified 1991–2020 station annual summary

| Variable | Official station climatology |
|---|---:|
| Annual mean daily maximum temperature | **12.19°C** |
| Annual mean daily minimum temperature | **4.79°C** |
| Derived annual mean temperature, (12.19 + 4.79)/2 | **8.49°C** |
| Annual air frost days | **63.64 days** |
| Total annual rainfall | **1,565.62 mm** |
| Rain days ≥1 mm | **185.27 days** |
| Mean 10 m wind speed | **6.83 knots**, about **3.51 m/s** |
| Station sunshine hours | **Not available** in published station table |

### LC1 NASA POWER input versus long-term station climatology

- Existing **LC1 simulation point**: latitude 51.95° N, longitude −3.57° W. Source: NASA POWER 2025 Local Solar Time, `T2M` and `WS10M`, 8,760 hourly records.
- Archived file: `LC1-main/data/nasa-power-sennybridge-2025.csv`, in `LC1-main Github 10_11_2026 time1515.zip`; corresponding public model input: https://github.com/1585290608/LC1/blob/main/Week7Remake/data/nasa-power-sennybridge-2025.csv
- **NASA POWER 2025 annual T2M mean:** **9.707916°C** (calculated from all 8,760 saved hourly entries).
- **Sennybridge No 2 1991–2020 station proxy mean:** **8.49°C** (from Met Office's annual mean max/min). **Difference: +1.22°C**.
- Day-weighting station monthly max/min means for the 2025 calendar gives **8.492356°C**; this is an independent monthly-to-year aggregation and not an observed 2025 station mean.
- **NASA POWER 2025 WS10M annual mean:** **4.977205 m/s** versus station long-term **3.513656 m/s**. This is cross-location, cross-period and differently represented wind exposure; it is **NOT** a wind-model error statistic or turbine production validation.

**Important:** Station and NASA fields represent different locations and temporal scopes; NASA/MERRA-2 spatial cell average elevation in the saved file is 245.39 m. The station altitude of ~307 m quoted in secondary material was **not independently verified from the official station record here**. Do not label these differences a measured 2025 anomaly at one location. For location-specific climate mapping use HadUK-Grid 1 km as a subsequent task.

See `SENNYBRIDGE_MET_OFFICE_VS_NASA_2025_MONTHLY.csv` for monthly 2025 NASA vs long-term station comparisons. The 2025 NASA values were calculated from the **archived actual hourly input**, not a temperature curve fitted to the station reference.

## 2. User-provided Fourier model — checked but not recommended as hourly input

User-supplied first-harmonic approximation for month index m=1,...,12:

```text
Tmean = 8.462 - 4.467 cos(pi*m/6) - 3.586 sin(pi*m/6)
Tmax  = 12.157 - 5.419 cos(pi*m/6) - 3.698 sin(pi*m/6)
Tmin  = 4.768 - 3.515 cos(pi*m/6) - 3.473 sin(pi*m/6)
```

Independent R² values against the monthly station table, using the rounded coefficients:

- Mean: **0.992929** (user's claimed ~0.9929 confirmed).
- Mean daily max: **0.995891** (~0.9959 confirmed).
- Mean daily min: **0.983868** (~0.9839 confirmed).

Although these approximate the **monthly seasonal cycle**, they do not reproduce every month's actual station mean and cannot capture hourly variation, frost events, heat waves or extreme wind events. Retain as optional explanatory methodology only; **do not overwrite the 2025 T2M timeseries or rerun HDH based on these 12 monthly points**.

The proposed elevation lapse rate 0.0055–0.0065°C/m and winter valley inversion shift 1.5–3.0°C remain **UNVERIFIED PARAMETRIC ASSUMPTIONS**, not measured Sennybridge site corrections. Do not apply without source-specific evidence and a separate declared scenario. Humidity/precipitation alone does not determine a site's hourly lapse rate or thermal electricity consumption.

## 3. Three user-supplied Met Office links — evidence classification

| Link | What it is | Appropriate LC1 use | Not valid for |
|---|---|---|---|
| [1991–2020 averages](https://www.metoffice.gov.uk/research/climate/maps-and-data/location-specific-long-term-averages/gcm2jvb2g) | Station-level long-term monthly climate normals | Literature/background, monthly seasonality and NASA context | Replacing the 2025 hourly weather or calibrating building heat use |
| [Sennybridge forecast](https://weather.metoffice.gov.uk/forecast/gcm2jvb2g) | **Forecast** of future weather, changes daily | Practical site planning; possible future scenario checks if forecast data archived and timestamped | Historical 2025 validation or a climate-normal reference |
| [Sennybridge last 24 hours](https://weather.metoffice.gov.uk/observations/gcm2jvb2g) | Rolling **recent observations** window, dynamic | Potential later independent short-horizon comparison after timestamped acquisition | Complete 2025 observations, annual energy calibration or direct long-term normals |

Do not scrape these dynamic pages later and mistake their contents for observations valid on this note's creation date. If observational data are needed, use a documented downloadable station archive with known coordinates, timestamps, QC and licensing.

## 4. Authoritative supporting climate resources

- **HadUK-Grid 1 km datasets (official Met Office):** https://www.metoffice.gov.uk/research/climate/maps-and-data/data/haduk-grid/datasets
- **HadUK-Grid methods:** https://www.metoffice.gov.uk/research/climate/maps-and-data/data/haduk-grid/methods
- **HadUK-Grid CEDA catalogue:** https://catalogue.ceda.ac.uk/uuid/4dc8450d889a491ebb20e724debe2dfb/
- **NASA POWER hourly documentation:** https://power.larc.nasa.gov/docs/services/api/temporal/hourly/

## 5. Dissertation applicability and strict scope protection

1. Use verified Met Office monthly long-term values in **Study Area / Climate Context**, properly cited.
2. Use **Met Office station climatology versus NASA POWER 2025** as a cross-context check, with station-location and year-mismatch limitations explicitly stated.
3. Potentially use monthly station 10 m mean wind as a **qualitative plausibility** check of wind exposure, but not to regenerate the PV/Wind power-output series. The site-specific wind hub height and input source differ.
4. Station sunshine observations are missing; therefore these data **do not independently validate** the LC1 model's PV irradiance profile or energy yield.
5. **Do not change** the frozen Original Low/Central/High load series, HDH 15.5°C energy-neutral heating scenario, 72,768 kWh/year heating assumption, 763,901.095464 kWh/year Central demand, or 24/72/168h outage simulations merely because climate normals differ.
6. No empirical space-heating electricity, site building thermal coefficient, military meter, or true grid-forming/UPS transfer evidence was obtained.
7. When integrating into `Week7Remake/Dissertation/`, add a new weather source record to the Evidence Register and one source-limited paragraph under Methodology Section 2.1 or 2.11; do not alter previously supported simulation claims.
8. Preserve the academic distinction: **STATION_CLIMATE_NORMAL**, **MODELLED_2025_REANALYSIS**, **FORECAST**, **ROLLING_OBSERVATION**, and **ASSUMPTION**.

## Reproducibility and source integrity

- User-provided station climatology link was corrected to the page inspected, and **station table numbers were manually transcribed from the rendered Met Office page** on the stated date.
- NASA hourly figures were independently recomputed from the unmodified archived 8,760-line input file. Archived NASA input SHA-256: `2a59fbfd46bdb9b2cb24b67436dacd43ec8e42108ce4269e8506f8158b52e120`.
- The monthly comparison is a **descriptive cross-location, cross-period** tabulation; it is not bias correction, empirical site calibration or a weather-data accuracy verdict.
- Source webpage HTML was not copied or redistributed. Primary source URLs are retained for citation and audit.
