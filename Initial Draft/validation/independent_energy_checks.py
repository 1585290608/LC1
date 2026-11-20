"""Recompute conservation/limits from saved CSV, without calling simulator residuals."""
import json,math,bisect
from validation.trace_io import read,load,ROOT

def fuel_rate(p,name,definition):
    if p==0:return 0.
    if name=='FIXED_025':return p*.25
    x=p/100.;xs=definition['fractions'][1:];ys=definition['stored_values'][1:]
    if x<.25-1e-9 or x>1+1e-9:raise AssertionError('Unsupported native positive-output domain')
    i=min(len(xs)-2,max(0,bisect.bisect_right(xs,x)-1))
    return p*(ys[i]+(ys[i+1]-ys[i])*(x-xs[i])/(xs[i+1]-xs[i]))*definition['USgal_to_L']

def check(path,settings,fuel_model,tag_path=None):
    raw=read(path);curve=load(ROOT/'models/islanded/config/fuel-models.json');s=settings
    maxima={k:0. for k in ['AC_kwh','DC_kwh','DG_destination_kwh','fuel_L','UPS_kwh','tier_kwh','profile_generation_kwh','profile_duration_h','state_continuity','DG_tag_kwh']}
    sums={k:0. for k in maxima};pools={'initial':s['initial_soc']*s['battery_kwh'],'DG':0.,'RE':0.};tags=[];previous=None;integral_fuel=0.;dg_redischarge=0.
    def bound(v,lo,hi):
        assert math.isfinite(v) and lo-1e-7<=v<=hi+1e-7,(v,lo,hi)
    for rr in raw:
        r={k:(float(v) if k not in ('dg_profile','dg_state','timestamp_LST','islanded','committed') else v) for k,v in rr.items()}
        dt=r['dt_h'];e=lambda k:r[k]*dt
        served=sum(e(t+'_served_kw') for t in ('c4isr','aux','ev'))
        ac=e('pv_actual_kw')+e('wind_actual_kw')+e('dg_generated_kw')+e('bess_discharge_kw')+e('ups_output_kw')+e('grid_import_kw')-served-e('bess_charge_kw')-e('ups_charge_kw')-e('grid_export_kw')-e('dg_dumped_kw')
        dc=(r['soc_final']-r['soc_initial'])*s['battery_kwh']-e('bess_charge_kw')*s['eta_charge']+e('bess_discharge_kw')/s['eta_discharge']
        dg=e('dg_generated_kw')-e('dg_delivered_kw')-e('dg_to_bess_kw')-e('dg_dumped_kw')-e('dg_to_ups_kw')
        profile=json.loads(r['dg_profile']);last=0.;gen=operating=fu=0.
        for a,b,p in profile:
            assert abs(a-last)<1e-8 and b>=a and 0<=a<=b<=dt+1e-8
            bound(p,0,s['dg_kw'])
            if p>1e-9:
                assert p>=s['dg_kw']*s['dg_min_fraction']-1e-8
                operating+=b-a;fu+=fuel_rate(p,fuel_model,curve)*(b-a)
            gen+=p*(b-a);last=b
        assert abs(last-dt)<1e-8
        fr=r['fuel_initial_l']-r['fuel_final_l']-fu;integral_fuel+=fu
        up=r['ups_final_kwh']-r['ups_initial_kwh']-e('ups_charge_kw')+e('ups_output_kw')
        vals={'AC_kwh':ac,'DC_kwh':dc,'DG_destination_kwh':dg,'fuel_L':fr,'UPS_kwh':up,'profile_generation_kwh':gen-e('dg_generated_kw'),'profile_duration_h':operating-r['dg_operating_duration_h']}
        for tier in ('c4isr','aux','ev'):
            bound(r[tier+'_served_kw'],0,r[tier+'_required_kw'])
            vals['tier_kwh']=max(vals.get('tier_kwh',0),abs(e(tier+'_required_kw')-e(tier+'_served_kw')-e(tier+'_unserved_kw')))
        for key in ('soc_initial','soc_final'):bound(r[key],s['soc_min'],s['soc_max'])
        for key in ('bess_charge_kw','bess_discharge_kw'):bound(r[key],0,s['pcs_kw'])
        assert not(r['bess_charge_kw']>1e-8 and r['bess_discharge_kw']>1e-8)
        bound(r['dg_dumped_kw'],0,s['dump_rating_kw'])
        assert e('grid_import_kw')==e('grid_export_kw')==0
        bound(r['fuel_final_l'],0,s['fuel_tank_l'])
        assert abs(e('pv_available_kw')+e('wind_available_kw')-e('pv_actual_kw')-e('wind_actual_kw')-e('renewable_curtailed_kw'))<1e-7
        if previous:
            vals['state_continuity']=max(abs(previous['soc_final']-r['soc_initial']),abs(previous['fuel_final_l']-r['fuel_initial_l']),abs(previous['ups_final_kwh']-r['ups_initial_kwh']),abs(previous['t_end_h']-r['t_start_h']))
        # Proportional mixing is attribution bookkeeping, not physical source metering.
        withdraw=e('bess_discharge_kw')/s['eta_discharge'];stock=sum(pools.values());dg_out=withdraw*pools['DG']/stock*s['eta_discharge'] if stock else 0.
        for k in pools:pools[k]-=withdraw*pools[k]/stock if stock else 0.
        pools['DG']+=e('dg_to_bess_kw')*s['eta_charge'];pools['RE']+=e('re_to_bess_kw')*s['eta_charge'];dg_redischarge+=dg_out
        vals['DG_tag_kwh']=sum(pools.values())-r['soc_final']*s['battery_kwh']
        for k,v in vals.items():maxima[k]=max(maxima[k],abs(v));sums[k]+=v
        tags.append({'hour_index':r['hour_index'],'DG_charge_ac_kwh':e('dg_to_bess_kw'),'DG_charge_dc_kwh':e('dg_to_bess_kw')*s['eta_charge'],'DG_origin_discharge_ac_kwh':dg_out,'DG_stored_final_dc_kwh':pools['DG'],'initial_stored_dc_kwh':pools['initial'],'RE_stored_dc_kwh':pools['RE']})
        previous=r
    assert max(maxima.values())<1e-6,maxima
    assert max(abs(v) for v in sums.values())<1e-6,sums
    dg_charge=sum(t['DG_charge_ac_kwh'] for t in tags)
    tag_res=dg_charge*s['eta_charge']-dg_redischarge/s['eta_discharge']-pools['DG'];assert abs(tag_res)<1e-7
    if tag_path:
        from common import write
        write(tag_path,tags)
    return {'status':'PASS','rows':len(raw),'max_independent_residual':max(maxima.values()),**{'max_'+k:v for k,v in maxima.items()},**{'sum_'+k:v for k,v in sums.items()},'profile_integrated_fuel_l':integral_fuel,'DG_charge_ac_kwh':dg_charge,'DG_stored_final_dc_kwh':pools['DG'],'DG_origin_discharge_ac_kwh':dg_redischarge,'DG_attributed_losses_kwh':dg_charge*(1-s['eta_charge'])+dg_redischarge*(1/s['eta_discharge']-1),'DG_attribution_residual_kwh':tag_res}
