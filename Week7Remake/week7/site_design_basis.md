# Week 7 T03 - Proposed Site Design Basis (Working Design Envelope)

**Status:** PROVISIONAL and ACADEMIC ONLY. This is a representative design case for the LC1 project, not an actual MOD Sennybridge asset or approved 120-person occupancy plan.

## Modelling boundary

The research examines a hypothetical **120-person Operational Support Camp in the Sennybridge area**. The 120 is a design choice under review, **not** a measured population of a particular training camp. The original LC1 2025 NASA POWER weather and 8,760-hour source LST time base are reused for reproducibility. No real site-level electric meter profiles, building inventory, floor plans, accommodation schedules, EV fleet logs, or restricted defence infrastructure details were supplied.

| Representative facility unit | Quantity in design envelope | Occupancy / model role | Real-site verification |
| --- | ---: | --- | --- |
| Accommodation blocks | 4 hypothetical blocks | 30 residents each; general socket loads, indoor lighting and ventilation | Not surveyed |
| C4ISR / command and IT hut | 1 | Aggregate C4ISR demand and dedicated IT cooling | Not surveyed |
| Catering / communal dining | 1 | Catering electric cooking only; no duplication with accommodation sockets | Not surveyed |
| Medical and emergency-services module | 1 | Independent critical refrigeration / medical base load | Not surveyed |
| Maintenance workshop / laundry | 1 combined service area | Weekday workshop and separately scheduled laundry load | Not surveyed |
| Water-pumping / treatment utility | 1 conceptual plant | Water utility demand; not counted elsewhere | Not surveyed |
| Security / common lighting | Assumed distributed systems | Perimeter critical lighting separate from noncritical common lighting | Not surveyed |
| Fleet charging point group | 7 vehicle-specific AC connections | Four light, two medium logistics, one mobile emergency EV; shared AC 70 kW cap | Charger specification not verified |

## Load tier boundary

- **Critical (C4ISR):** command/communications electronics, dedicated C4ISR cooling, medical and emergency refrigeration, perimeter security lighting. The chosen critical category is a **research priority assignment**; essential-service doctrine and mission owners have not approved it.
- **Auxiliary:** accommodation, ventilation, sockets, lighting, catering, laundry, water utilities, workshops, seasonal electric heating or cooling.
- **Flexible EV:** charging power required to replace propulsion energy. This is treated as priority three for *microgrid load serving*, but the independent EV scheduler always protects vehicle mission reserve before departure. Microgrid ENS in EV charging is **not yet coupled back** to vehicle departure feasibility after outages; this feedback needs implementation before interpreting mission readiness in islanded operations.

**Important coupling gap:** The 8,760-hour EV load is scheduled as if requested charging were fully supplied. In a microgrid outage, `ev_unserved_kw` represents charging energy not delivered but the input load generator does not yet update future individual vehicle SOC. The EV readiness checks therefore validate *planned normal charging*, not guaranteed deployment readiness during a 168-hour outage. This is a high-priority next-stage modelling dependency.

## Explicit electrical assumptions

1. Every equipment rating in `config/equipment.csv` is a proposed aggregate operating kW rating; duty cycles are assigned by one-hour schedules.
2. Critical devices use 100% of their assumed rating when scheduled. Auxiliary demand uses 65%, 80%, or 100% of the stated site-group aggregate rating for low, central and high cases. These are deterministic occupancy/use factors, not probability-based estimates.
3. Winter heating and summer cooling are mutually exclusive modelled end uses. Accommodation ventilation is separately counted only as fan/air movement power.
4. All EVs charge AC to 90% initial/target SOC, with hypothetical charger efficiency 0.92 and a shared 70 kW charging constraint. Mission-distance multipliers are 0.80 / 1.00 / 1.25.
5. Weekly mission timing is specified in `config/fleet.csv` and follows fixed **source LST**, not BST civil time or a realistic dispatch log. No battery ageing or route-temperature correction is modelled.
6. Inherited original LC1 100 kW grid import bound is **hypothetical**, not a verified electrical connection. The revised peak 172–225 kW means peacetime grid connection adequacy cannot be assumed.
7. The model does not represent individual distribution feeders, kVA/power factor, voltage drops, fault coordination, protected communications, physical access, or operational security.

## Site study limitations and decisions for supervisor

1. Approve a representative **120-person** design envelope, or change the population and facility inventory.
2. Agree whether the research target is only 24/72/168-hour **islanded resilience**, or also normal grid-connected NPC and EV fleet charging economics.
3. Obtain a public / permissible reference load basis for accommodation, kitchen, heat load, water utility, critical operations and actual EV sizes; use ranges if authentic data are unavailable.
4. Decide whether EV charging service under outages must feed back into actual vehicle SOC and readiness before vehicle-supported emergency power is investigated.
5. Authorise prioritisation of C4ISR versus medical/security services as a conceptual demand-tier model. Avoid asserting these are official MOD priorities.
