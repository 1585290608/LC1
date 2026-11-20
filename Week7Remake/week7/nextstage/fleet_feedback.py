"""Independent *unidirectional* EV fleet feedback for simulated outages.
Vehicle archetypes and route timetables are PROVISIONAL assumptions; not OEM or MOD data.
Under-served EV charging changes future SOC and can cause missed missions.
No V2B, V2G, or vehicle discharge for stationary loads is modelled.
"""
from __future__ import annotations
from datetime import timedelta,datetime
from week7.load_model import initialise_fleet,SCENARIOS,DATE0,next_departure

class EVFleetFeedback:
    def __init__(self,case='central'):
        self.case=case
        self.opt=SCENARIOS[case]
        self.vehicles=initialise_fleet()
        self.eta=0.92
        self.target_soc=0.90
        self.opportunities=0
        self.completed=0
        self.missed=0
        self.traction_kwh=0.0
        self.served_ac_kwh=0.0
        self.unserved_ac_kwh=0.0
        self.rows=[]
        self._pending=None
        self._last_index=-1

    def before_hour(self,h:int)->float:
        if self._pending is not None or h!=self._last_index+1:
            raise ValueError('Fleet must update once per consecutive hour')
        dt=DATE0+timedelta(hours=h)
        activities={}
        for v in self.vehicles:
            a={'hour_index':h,'timestamp_LST':dt.isoformat(),'vehicle_id':v.id,
               'mission_opportunity':0,'mission_departure':0,'mission_missed':0,
               'mission_return':0,'traction_kwh':0.,'charging_requested_ac_kwh':0.,
               'charging_served_ac_kwh':0.,'charging_unserved_ac_kwh':0.}
            if not v.connected and dt.hour==v.arr and v.mission_today(dt):
                v.soc-=v.away_energy_kwh/v.cap
                if v.soc<v.reserve-1e-9:raise AssertionError('Propulsion reserve depleted')
                self.traction_kwh+=v.away_energy_kwh
                a['traction_kwh']=v.away_energy_kwh
                v.away_energy_kwh=0.
                v.connected=True
                a['mission_return']=1
            if v.connected and dt.hour==v.dep and v.mission_today(dt):
                a['mission_opportunity']=1
                self.opportunities+=1
                need=v.km*self.opt['mission_distance_factor']*v.consumption
                if v.soc*v.cap+1e-8>=need+v.reserve*v.cap:
                    v.connected=False
                    v.away_energy_kwh=need
                    a['mission_departure']=1
                    self.completed+=1
                else:
                    # A failed deployment is not silently allowed or discounted as propulsion.
                    a['mission_missed']=1
                    self.missed+=1
            a['soc_before_charge']=v.soc
            a['connected']=int(v.connected)
            a['mission_reserve_soc']=v.reserve
            activities[v.id]=a
        connected=sorted([v for v in self.vehicles if v.connected],key=lambda v:(next_departure(v,dt) or datetime.max,v.id))
        remaining=self.opt['shared_charger_kw']
        order=[]
        for v in connected:
            requested=min(v.rate,remaining,max(0.,(self.target_soc-v.soc)*v.cap/self.eta))
            remaining-=requested
            activities[v.id]['charging_requested_ac_kwh']=requested
            order.append((v,requested))
        self._pending=(h,order,activities)
        self._last_index=h
        return sum(x for _,x in order)

    def after_hour(self,served_ac_kwh:float)->None:
        if self._pending is None:raise ValueError('before_hour required')
        h,order,activities=self._pending
        requested=sum(x for _,x in order)
        if served_ac_kwh<-1e-7 or served_ac_kwh>requested+1e-6:
            raise AssertionError(f'Invalid EV dispatch: served {served_ac_kwh}, requested {requested}')
        left=min(requested,max(0.,served_ac_kwh))
        for v,demand in order:
            served=min(left,demand)
            left-=served
            v.soc+=served*self.eta/v.cap
            if v.soc>self.target_soc+1e-7:raise AssertionError('EV target SOC exceeded')
            a=activities[v.id]
            a['charging_served_ac_kwh']=served
            a['charging_unserved_ac_kwh']=demand-served
        if left>1e-7:raise AssertionError('EV service not allocated')
        self.served_ac_kwh+=min(served_ac_kwh,requested)
        self.unserved_ac_kwh+=requested-min(served_ac_kwh,requested)
        for v in self.vehicles:
            a=activities[v.id]
            a['soc_end']=v.soc
            if v.soc<v.reserve-1e-8:raise AssertionError('EV mission reserve not respected')
            if a['connected']==0 and a['charging_served_ac_kwh']>1e-9:raise AssertionError('Charged away vehicle')
            self.rows.append(a)
        self._pending=None

    def precondition(self,end_hour:int):
        """Reproduce fully supplied normal-grid EV charging before an outage window.
        This is a vehicle state warm-up, not a grid-connected microgrid model.
        """
        for h in range(end_hour):
            demand=self.before_hour(h)
            self.after_hour(demand)
        self.rows=[]
        self.opportunities=self.completed=self.missed=0
        self.traction_kwh=self.served_ac_kwh=self.unserved_ac_kwh=0.

    def summary(self):
        return {'vehicle_opportunities':self.opportunities,
                'vehicle_departures_completed':self.completed,
                'vehicle_departures_missed':self.missed,
                'mission_readiness_fraction':self.completed/self.opportunities if self.opportunities else None,
                'ev_actual_charging_ac_kwh':self.served_ac_kwh,
                'ev_charging_ENS_ac_kwh':self.unserved_ac_kwh,
                'ev_mission_traction_kwh':self.traction_kwh,
                'minimum_vehicle_end_soc':min(v.soc for v in self.vehicles),
                'end_soc_by_vehicle':{v.id:v.soc for v in self.vehicles},
                'fleet_soc_boundary':'Only EV propulsion uses battery energy; no V2G supported'}
