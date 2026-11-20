"""Generated observations only; original physics/control equations retained.
Fuel-charge safeguard and equipment outages live in emergency.py, not these frozen-derived equations.
"""
import math
from ..core.components import EPS,duration
from ..core.simulate import Settings,TIERS,serve,InfeasibleOperatingPoint
def log_service(records,h,start,end,req,served,ups_power,active_duration,dg_power):
    cuts=[(start,start+active_duration,ups_power),(start+active_duration,end,0.)] if active_duration>EPS else [(start,end,0.)]
    for a,b,p in cuts:
        if b-a<=EPS:continue
        r={'hour_index':h,'offset_start_h':a,'offset_end_h':b,'duration_h':b-a,'dg_on_kw':dg_power,'UPS_kw':p,'ledger_basis':'INSTRUMENTED_PIECEWISE_ENERGY_MODEL_NOT_TRANSIENTS'}
        for tier in TIERS:
            value=served[tier]+(p if tier=='c4isr' else 0.)
            r.update({tier+'_required_kw':req[tier],tier+'_served_kw':value,tier+'_unserved_kw':max(0.,req[tier]-value)})
        records.append(r)
def instrumented_s0(pv,wind,loads,battery,diesel,ups_energy,h,islanded,dt_h=1.,settings=None,segment_log=None):
    s=settings or Settings();dt=duration(dt_h);battery.begin_step()
    initial_soc=battery.soc;initial_fuel=diesel.fuel_l;initial_ups=ups_energy
    if not -EPS<=initial_fuel<=diesel.tank_l+EPS:raise ValueError('Fuel inventory exceeds configured capacity')
    req=loads.required(h)
    if any(not math.isfinite(v) or v<0 for v in req.values()):raise ValueError('Invalid demand')
    pv_av,wind_av=pv.available(h),wind.available(h)
    if min(pv_av,wind_av)<0 or not math.isfinite(pv_av+wind_av):raise ValueError('Invalid renewable profile')
    renewable=pv_av+wind_av;usable=renewable if not islanded or s.ac_reference_assumed else 0.
    base={t:0. for t in TIERS};re_to_load=serve(req,base,usable);gap=sum(req.values())-sum(base.values())
    batt_dis=battery.discharge(gap,allow_reserve=islanded,dt_h=dt);serve(req,base,batt_dis);gap=max(0.,sum(req.values())-sum(base.values()))
    if islanded and diesel.enabled and diesel.fuel_l>EPS and gap>EPS and gap<diesel.min_kw-EPS and not s.dump_load_assumed and not(s.allow_dg_to_bess and s.dg_bess_connection_assumed):raise InfeasibleOperatingPoint('DG request below minimum, no permitted charge/dump sink')
    if islanded:generated=diesel.dispatch(gap,dt)
    else:diesel.stop();diesel.profile=[(0.,dt,0.)];diesel.output_on_kw=0.;diesel.operating_duration_h=0.;diesel.fuel_used_l=0.;generated=0.
    delivered={t:base[t]*dt for t in TIERS};dg_delivered_e=dg_bess_e=dg_dump_e=ups_e=ups_on_h=0.;grid_import_to_load=0.
    if not islanded:
        extra=dict(base);grid_import_to_load=serve(req,extra,gap);delivered={t:extra[t]*dt for t in TIERS}
    else:
        for start,end,on_power in diesel.profile:
            span=end-start
            if span<=EPS:continue
            instant=dict(base);dg_to_load=serve(req,instant,on_power);dg_delivered_e+=dg_to_load*span
            for t in TIERS:delivered[t]+=(instant[t]-base[t])*span
            critical_gap=max(0.,req['c4isr']-instant['c4isr']);ups_power=min(critical_gap,s.ups_kw);ups_active_duration=0.
            if ups_power>EPS and ups_energy>EPS:
                on_time=min(span,ups_energy/ups_power);e=ups_power*on_time;ups_energy-=e;ups_e+=e;ups_on_h+=on_time;delivered['c4isr']+=e;ups_active_duration=on_time
            if segment_log is not None:log_service(segment_log,h,start,end,req,instant,ups_power,ups_active_duration,on_power)
            surplus=max(0.,on_power-dg_to_load)
            if surplus>EPS and s.allow_dg_to_bess and s.dg_bess_connection_assumed and batt_dis<=EPS:
                charge=battery.charge(surplus,dt_h=span);dg_bess_e+=charge*span;surplus-=charge
            if surplus>EPS:
                if not s.dump_load_assumed or surplus>s.dump_rating_kw+EPS:raise InfeasibleOperatingPoint(f'DG surplus {surplus}kW exceeds supported sink')
                dg_dump_e+=surplus*span
    re_remaining=max(0.,usable-re_to_load);re_bess=0.
    if re_remaining>EPS and batt_dis<=EPS:re_bess=battery.charge(re_remaining,dt_h=dt);re_remaining-=re_bess
    ups_charge=grid_ups=re_ups=0.
    if not islanded:
        capacity=s.ups_kw*s.ups_minutes/60.;ups_charge=max(0.,min(s.ups_kw,(capacity-ups_energy)/dt));re_ups=min(re_remaining,ups_charge);re_remaining-=re_ups;grid_ups=ups_charge-re_ups;ups_energy+=ups_charge*dt
    export=re_remaining if not islanded else 0.;curtail=renewable-usable+(re_remaining if islanded else 0.)
    pv_curt=curtail*pv_av/renewable if renewable else 0.;wind_curt=curtail-pv_curt;pv_actual=pv_av-pv_curt;wind_actual=wind_av-wind_curt
    charge_e=re_bess*dt+dg_bess_e;grid_import=grid_import_to_load+grid_ups;served_total=sum(delivered.values())/dt
    dg_to_load=dg_delivered_e/dt;dg_to_bess=dg_bess_e/dt;dumped=dg_dump_e/dt
    ac_res=(pv_actual+wind_actual+generated+grid_import+batt_dis+ups_e/dt-served_total-charge_e/dt-ups_charge-export-dumped)*dt
    dc_delta=(battery.soc-initial_soc)*battery.energy_kwh;dc_expected=charge_e*battery.eta_charge-batt_dis*dt/battery.eta_discharge
    expected_fuel=sum(diesel.fuel_rate_lph(power)*(end-start) for start,end,power in diesel.profile if power>0)
    fuel_used=initial_fuel-diesel.fuel_l;fuel_res=fuel_used-expected_fuel;dg_res=generated*dt-dg_delivered_e-dg_bess_e-dg_dump_e;ups_res=ups_energy-initial_ups-ups_charge*dt+ups_e
    if max(abs(ac_res),abs(dc_delta-dc_expected),abs(fuel_res),abs(dg_res),abs(ups_res))>1e-7:raise AssertionError('Full-system accounting fails')
    if battery.soc<s.soc_min-1e-9 or battery.soc>s.soc_max+1e-9:raise AssertionError('SOC outside bounds')
    if charge_e>EPS and batt_dis>EPS:raise AssertionError('Simultaneous battery charge/discharge')
    r={'hour_index':h,'dt_h':dt,'islanded':bool(islanded),'pv_available_kw':pv_av,'wind_available_kw':wind_av,'pv_actual_kw':pv_actual,'wind_actual_kw':wind_actual,'renewable_curtailed_kw':curtail,
       're_to_load_kw':re_to_load,'re_to_bess_kw':re_bess,'re_to_ups_kw':re_ups,'dg_generated_kw':generated,'dg_delivered_kw':dg_to_load,'dg_to_bess_kw':dg_to_bess,'dg_to_ups_kw':0.,'dg_dumped_kw':dumped,
       'dg_on_power_kw':diesel.output_on_kw,'dg_operating_duration_h':diesel.operating_duration_h,'dg_state':diesel.state,'dg_fuel_consumed_l':fuel_used,'dg_fuel_remaining_l':diesel.fuel_l,
       'bess_discharge_kw':batt_dis,'bess_charge_kw':charge_e/dt,'battery_loss_kwh':charge_e*(1-battery.eta_charge)+batt_dis*dt*(1/battery.eta_discharge-1),'soc_initial':initial_soc,'soc_final':battery.soc,'battery_delta_stored_kwh':dc_delta,
       'fuel_initial_l':initial_fuel,'fuel_final_l':diesel.fuel_l,'configured_fuel_capacity_l':diesel.tank_l,'ups_initial_kwh':initial_ups,'ups_final_kwh':ups_energy,'ups_output_kw':ups_e/dt,'ups_operating_duration_h':ups_on_h,'ups_charge_kw':ups_charge,
       'grid_import_kw':grid_import,'grid_export_kw':export,'AC_residual_kwh':ac_res,'battery_residual_kwh':dc_delta-dc_expected,'fuel_residual_l':fuel_res,'DG_destination_residual_kwh':dg_res,'UPS_residual_kwh':ups_res}
    for tier in TIERS:
        served=delivered[tier]/dt;unserved=max(0.,req[tier]-served)
        if served>req[tier]+1e-9:raise AssertionError('Served demand exceeded')
        for key,value in [('required_kw',req[tier]),('served_kw',served),('unserved_kw',unserved)]:r[tier+'_'+key]=value
    return r,ups_energy
def instrumented_s3(pv,wind,loads,battery,diesel,ups_energy,h,islanded,dt_h=1.,settings=None,controller=None,segment_log=None):
    s=settings or Settings();dt=duration(dt_h);battery.begin_step()
    initial_soc=battery.soc;initial_fuel=diesel.fuel_l;initial_ups=ups_energy
    if not -EPS<=initial_fuel<=diesel.tank_l+EPS:raise ValueError('Fuel inventory exceeds configured capacity')
    req=loads.required(h)
    if any(not math.isfinite(v) or v<0 for v in req.values()):raise ValueError('Invalid demand')
    pv_av,wind_av=pv.available(h),wind.available(h)
    if min(pv_av,wind_av)<0 or not math.isfinite(pv_av+wind_av):raise ValueError('Invalid renewable profile')
    renewable=pv_av+wind_av;usable=renewable if not islanded or s.ac_reference_assumed else 0.
    base={t:0. for t in TIERS};re_to_load=serve(req,base,usable);gap=sum(req.values())-sum(base.values())
    if not islanded:raise ValueError('S2/S3 islanded-only research variant')
    reserve_power=max(0.,(battery.soc-s.soc_reserve)*battery.energy_kwh*battery.eta_discharge/dt)
    can_cover=gap<=min(battery.pcs_kw,reserve_power)+EPS
    if gap<=EPS:controller['committed']=False
    elif controller['committed']:
        if battery.soc>=controller['stop_soc']-EPS and can_cover:controller['committed']=False
    elif battery.soc<=s.soc_reserve+EPS or not can_cover:controller['committed']=True
    batt_dis=0. if controller['committed'] else battery.discharge(gap,allow_reserve=False,dt_h=dt)
    serve(req,base,batt_dis);batt_dis_e=batt_dis*dt;gap=max(0.,sum(req.values())-sum(base.values()))
    if islanded and diesel.enabled and diesel.fuel_l>EPS and gap>EPS and gap<diesel.min_kw-EPS and not s.dump_load_assumed and not(s.allow_dg_to_bess and s.dg_bess_connection_assumed):raise InfeasibleOperatingPoint('DG request below minimum, no permitted charge/dump sink')
    if islanded:generated=diesel.dispatch(gap,dt)
    else:diesel.stop();diesel.profile=[(0.,dt,0.)];diesel.output_on_kw=0.;diesel.operating_duration_h=0.;diesel.fuel_used_l=0.;generated=0.
    delivered={t:base[t]*dt for t in TIERS};dg_delivered_e=dg_bess_e=dg_dump_e=ups_e=ups_on_h=0.;grid_import_to_load=0.
    if not islanded:
        extra=dict(base);grid_import_to_load=serve(req,extra,gap);delivered={t:extra[t]*dt for t in TIERS}
    else:
        for start,end,on_power in diesel.profile:
            span=end-start
            if span<=EPS:continue
            instant=dict(base);dg_to_load=serve(req,instant,on_power);dg_delivered_e+=dg_to_load*span
            if controller['committed']:
                backup=battery.discharge(max(0.,sum(req.values())-sum(instant.values())),allow_reserve=True,dt_h=span)
                serve(req,instant,backup);batt_dis_e+=backup*span
            for t in TIERS:delivered[t]+=(instant[t]-base[t])*span
            critical_gap=max(0.,req['c4isr']-instant['c4isr']);ups_power=min(critical_gap,s.ups_kw);ups_active_duration=0.
            if ups_power>EPS and ups_energy>EPS:
                on_time=min(span,ups_energy/ups_power);e=ups_power*on_time;ups_energy-=e;ups_e+=e;ups_on_h+=on_time;delivered['c4isr']+=e;ups_active_duration=on_time
            if segment_log is not None:log_service(segment_log,h,start,end,req,instant,ups_power,ups_active_duration,on_power)
            surplus=max(0.,on_power-dg_to_load)
            if surplus>EPS and s.allow_dg_to_bess and s.dg_bess_connection_assumed and batt_dis_e<=EPS:
                charge=battery.charge(surplus,dt_h=span);dg_bess_e+=charge*span;surplus-=charge
            if surplus>EPS:
                if not s.dump_load_assumed or surplus>s.dump_rating_kw+EPS:raise InfeasibleOperatingPoint(f'DG surplus {surplus}kW exceeds supported sink')
                dg_dump_e+=surplus*span
    batt_dis=batt_dis_e/dt
    re_remaining=max(0.,usable-re_to_load);re_bess=0.
    if re_remaining>EPS and batt_dis_e<=EPS:re_bess=battery.charge(re_remaining,dt_h=dt);re_remaining-=re_bess
    ups_charge=grid_ups=re_ups=0.
    if not islanded:
        capacity=s.ups_kw*s.ups_minutes/60.;ups_charge=max(0.,min(s.ups_kw,(capacity-ups_energy)/dt));re_ups=min(re_remaining,ups_charge);re_remaining-=re_ups;grid_ups=ups_charge-re_ups;ups_energy+=ups_charge*dt
    export=re_remaining if not islanded else 0.;curtail=renewable-usable+(re_remaining if islanded else 0.)
    pv_curt=curtail*pv_av/renewable if renewable else 0.;wind_curt=curtail-pv_curt;pv_actual=pv_av-pv_curt;wind_actual=wind_av-wind_curt
    charge_e=re_bess*dt+dg_bess_e;grid_import=grid_import_to_load+grid_ups;served_total=sum(delivered.values())/dt
    dg_to_load=dg_delivered_e/dt;dg_to_bess=dg_bess_e/dt;dumped=dg_dump_e/dt
    ac_res=(pv_actual+wind_actual+generated+grid_import+batt_dis+ups_e/dt-served_total-charge_e/dt-ups_charge-export-dumped)*dt
    dc_delta=(battery.soc-initial_soc)*battery.energy_kwh;dc_expected=charge_e*battery.eta_charge-batt_dis*dt/battery.eta_discharge
    expected_fuel=sum(diesel.fuel_rate_lph(power)*(end-start) for start,end,power in diesel.profile if power>0)
    fuel_used=initial_fuel-diesel.fuel_l;fuel_res=fuel_used-expected_fuel;dg_res=generated*dt-dg_delivered_e-dg_bess_e-dg_dump_e;ups_res=ups_energy-initial_ups-ups_charge*dt+ups_e
    if max(abs(ac_res),abs(dc_delta-dc_expected),abs(fuel_res),abs(dg_res),abs(ups_res))>1e-7:raise AssertionError('Full-system accounting fails')
    if battery.soc<s.soc_min-1e-9 or battery.soc>s.soc_max+1e-9:raise AssertionError('SOC outside bounds')
    if charge_e>EPS and batt_dis>EPS:raise AssertionError('Simultaneous battery charge/discharge')
    r={'hour_index':h,'dt_h':dt,'islanded':bool(islanded),'pv_available_kw':pv_av,'wind_available_kw':wind_av,'pv_actual_kw':pv_actual,'wind_actual_kw':wind_actual,'renewable_curtailed_kw':curtail,
       're_to_load_kw':re_to_load,'re_to_bess_kw':re_bess,'re_to_ups_kw':re_ups,'dg_generated_kw':generated,'dg_delivered_kw':dg_to_load,'dg_to_bess_kw':dg_to_bess,'dg_to_ups_kw':0.,'dg_dumped_kw':dumped,
       'dg_on_power_kw':diesel.output_on_kw,'dg_operating_duration_h':diesel.operating_duration_h,'dg_state':diesel.state,'dg_fuel_consumed_l':fuel_used,'dg_fuel_remaining_l':diesel.fuel_l,
       'bess_discharge_kw':batt_dis,'bess_charge_kw':charge_e/dt,'battery_loss_kwh':charge_e*(1-battery.eta_charge)+batt_dis*dt*(1/battery.eta_discharge-1),'soc_initial':initial_soc,'soc_final':battery.soc,'battery_delta_stored_kwh':dc_delta,
       'fuel_initial_l':initial_fuel,'fuel_final_l':diesel.fuel_l,'configured_fuel_capacity_l':diesel.tank_l,'ups_initial_kwh':initial_ups,'ups_final_kwh':ups_energy,'ups_output_kw':ups_e/dt,'ups_operating_duration_h':ups_on_h,'ups_charge_kw':ups_charge,
       'grid_import_kw':grid_import,'grid_export_kw':export,'AC_residual_kwh':ac_res,'battery_residual_kwh':dc_delta-dc_expected,'fuel_residual_l':fuel_res,'DG_destination_residual_kwh':dg_res,'UPS_residual_kwh':ups_res}
    for tier in TIERS:
        served=delivered[tier]/dt;unserved=max(0.,req[tier]-served)
        if served>req[tier]+1e-9:raise AssertionError('Served demand exceeded')
        for key,value in [('required_kw',req[tier]),('served_kw',served),('unserved_kw',unserved)]:r[tier+'_'+key]=value
    return r,ups_energy
