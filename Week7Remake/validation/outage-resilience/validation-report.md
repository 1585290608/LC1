# Draft3C validation

Status: PASS_SCOPED_NUMERICAL_ENERGY_SERVICE; engineering/nativeHybrid validation remains NOT_VERIFIED.

- 40tests passed; originalcore/regression and newavailability/startup/fuelguard/priority tests included.
- 18uniqueconfigurations,17newmainruns/3528h plus1reused168h; total3696h. No newDraft3A/B campaign or financial rerun.
- Source2025LST windows map Python0/2160/4344/6552 to inputrow1/2161/4345/6553. These are fileindices, not newnativeoutagetimestamps.
- Strict sourcehash, initialfuel500/1000/2000L in2000Ltank, initialSOC30/50/70%, UPS7.5kWhAC and coldDG1h checks. Same loads acrosscomparisonwindows; no phantomfuel/refill.
- Independently recomputed maximumhourlyAC 1.066e-14kWh,DC 1.776e-14kWh,fuel 1.137e-13L; serviceledger/hourlyintegral 0.000e+00kWh. Cumulative residuals, DGdestinations, statecontinuity and limits alsochecked; eachcolumn hasitsownunits inrawandvalidationrecords.
- Everyservicepiece obeys C4ISR→Aux→EV priority. Hourlybatteryallocation/idealUPS/DGenergysegments are not actualsubhour switchingobservations.
- DGavailabilityfalse inexact24h interval48-72; generation/fuel0there; restoredDGnotinstantaneous. StartupcommandhourDGoutput0. No gridimport/export or UPScharge inislandedcases.
- ActiveBESS300kWh/PCS90 forHybrid only. P0RinternalPCS0object inactive; SOC metricsN/A. C4nominalPV/Wind50/50 remainfixed; computational30/30 coefficients onlyencode0.6availability.
- Coldstartup plusfinitefuel explains P0Rfailure; no universalconventionalbackup conclusion. Hybrid1000Lwintercase has3.031L remaining, not safeinventoryvalidation.
- No invalidmainresult admitted. Initialaggregationbooleanparserfailure preserved, savedaggregation resumed withoutchanging18rawtracehashes.
- 17newcases reproduced byte-identically forhourly/service ledgers; oldbaseline notrerun. Priorresearch/figure preservation proof inEvidence/FINAL_PRESERVATION.json. Archive/extractedoffline reproduction recordedbesidefinalZIP.
- GenuineexistingnativeDGcontrol selected through originalversionedadmissiongate. No newnativeexecution or wholeHybridparity claim.

Phase1carbon supplement independently checks8existing8760h annualCSV at0.13096 and0.17700; original310sealedDraft3Bfiles andfinancialZIPunchanged. Scope2only; noScope3/avoidedexport/embodiedorScope1mixing.

Limitations are explicit in ENGINEERING_LIMITATIONS.csv. Mathematicalbalance is not protection/GFM/UPS/OEM/real reliability certification. Firstshortfall isprimarily an hourlybracket, no precisionbeyond thedeclared energy model. Deterministicweeks/stress are not combatvalidation, MonteCarlo or probabilityestimates.
