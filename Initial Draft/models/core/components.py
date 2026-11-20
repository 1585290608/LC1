"""Draft2 AC components. All powers kW, energy kWh, time h, fuel L.
Diesel returns mean generated power plus an exact ON/OFF interval profile.
These are numerical research assumptions, not manufacturer specifications.
"""
from dataclasses import dataclass,field
import math
EPS=1e-10
def duration(dt):
    if not math.isfinite(dt) or dt<=0:raise ValueError('Positive finite timestep required')
    return float(dt)
@dataclass
class PV:
    capacity_kw:float=50.;pu:list|None=None
    def available(self,h):return self.capacity_kw*float(self.pu[h])
@dataclass
class Wind:
    capacity_kw:float=50.;pu:list|None=None
    def available(self,h):return self.capacity_kw*float(self.pu[h])
@dataclass
class Loads:
    c4isr:list|None=None;aux:list|None=None;ev:list|None=None
    def required(self,h):return {'c4isr':float(self.c4isr[h]),'aux':float(self.aux[h]),'ev':float(self.ev[h])}
@dataclass
class Diesel:
    rated_kw:float=100.;min_load_fraction:float=.25;fuel_l_per_kwh:float=.25;tank_l:float=2000.;startup_delay_h:float=1.;enabled:bool=True
    fuel_l:float=field(init=False);running:bool=field(default=False,init=False);state:str=field(default='OFF',init=False)
    start_remaining_h:float=field(default=0.,init=False);profile:list=field(default_factory=list,init=False)
    output_on_kw:float=field(default=0.,init=False);operating_duration_h:float=field(default=0.,init=False);fuel_used_l:float=field(default=0.,init=False)
    def __post_init__(self):
        if not(self.rated_kw>0 and 0<=self.min_load_fraction<=1 and self.fuel_l_per_kwh>0 and self.tank_l>=0 and self.startup_delay_h>=0):raise ValueError('Invalid diesel configuration')
        self.fuel_l=float(self.tank_l)
    @property
    def min_kw(self):return self.rated_kw*self.min_load_fraction
    def fuel_rate_lph(self,power_kw):return power_kw*self.fuel_l_per_kwh
    def stop(self):self.running=False;self.start_remaining_h=0.;self.state='OFF'
    def dispatch(self,request_kw,dt_h=1.):
        dt=duration(dt_h)
        if not math.isfinite(request_kw) or request_kw<0:raise ValueError('Invalid diesel request')
        self.profile=[];self.output_on_kw=0.;self.operating_duration_h=0.;self.fuel_used_l=0.
        if not self.enabled or self.fuel_l<=EPS:
            self.running=False;self.start_remaining_h=0.;self.state='DISABLED' if not self.enabled else 'NO_FUEL';self.profile=[(0.,dt,0.)];return 0.
        if request_kw<=EPS:
            self.stop();self.profile=[(0.,dt,0.)];return 0.
        if not self.running and self.state!='STARTING':self.start_remaining_h=self.startup_delay_h
        delay=min(dt,self.start_remaining_h);self.start_remaining_h=max(0.,self.start_remaining_h-delay)
        if delay>0:self.profile.append((0.,delay,0.))
        available=dt-delay
        if self.start_remaining_h>EPS or available<=EPS:
            self.running=self.start_remaining_h<=EPS;self.state='READY' if self.running else 'STARTING'
            if not self.profile:self.profile=[(0.,dt,0.)]
            return 0.
        self.running=True;on_power=min(self.rated_kw,max(request_kw,self.min_kw));rate=self.fuel_rate_lph(on_power)
        if rate<=0:raise ValueError('Positive output requires positive fuel rate')
        on_time=min(available,self.fuel_l/rate);used=rate*on_time
        self.fuel_l=max(0.,self.fuel_l-used);self.fuel_used_l=used;self.output_on_kw=on_power;self.operating_duration_h=on_time
        if on_time>EPS:self.profile.append((delay,delay+on_time,on_power))
        if delay+on_time<dt-EPS:self.profile.append((delay+on_time,dt,0.))
        self.state='NO_FUEL' if self.fuel_l<=EPS else 'RUNNING';self.running=self.fuel_l>EPS
        return on_power*on_time/dt
@dataclass
class Battery:
    energy_kwh:float=300.;pcs_kw:float=90.;eta_charge:float=.8944;eta_discharge:float=.8944;soc_min:float=.1;soc_max:float=.9;soc_reserve:float=.3;soc:float=.7
    charge_kw:float=field(default=0.,init=False);discharge_kw:float=field(default=0.,init=False);loss_kwh:float=field(default=0.,init=False)
    def __post_init__(self):
        if not(0<=self.soc_min<=self.soc_reserve<=self.soc_max<=1 and self.soc_min<=self.soc<=self.soc_max and self.energy_kwh>0 and self.pcs_kw>=0 and 0<self.eta_charge<=1 and 0<self.eta_discharge<=1):raise ValueError('Invalid battery configuration')
    def begin_step(self):self.charge_kw=self.discharge_kw=self.loss_kwh=0.
    def energy(self):return self.soc*self.energy_kwh
    def charge(self,ac_kw,allow_reserve=False,dt_h=1.):
        dt=duration(dt_h)
        if self.discharge_kw>EPS:raise ValueError('Cannot charge/discharge within same outer interval')
        accepted=max(0.,min(ac_kw,self.pcs_kw,(self.soc_max-self.soc)*self.energy_kwh/self.eta_charge/dt))
        self.soc+=accepted*dt*self.eta_charge/self.energy_kwh;self.charge_kw=accepted;self.loss_kwh+=accepted*dt*(1-self.eta_charge)
        return accepted
    def discharge(self,ac_kw,allow_reserve=False,dt_h=1.):
        dt=duration(dt_h)
        if self.charge_kw>EPS:raise ValueError('Cannot charge/discharge within same outer interval')
        floor=self.soc_min if allow_reserve else self.soc_reserve
        power=max(0.,min(ac_kw,self.pcs_kw,max(0.,self.soc-floor)*self.energy_kwh*self.eta_discharge/dt))
        self.soc-=power*dt/self.eta_discharge/self.energy_kwh;self.discharge_kw=power;self.loss_kwh+=power*dt*(1/self.eta_discharge-1)
        return power
@dataclass
class UPS:
    power_kw:float=30.;backup_min:float=15.;energy_kwh:float=field(init=False)
    def __post_init__(self):
        if self.power_kw<0 or self.backup_min<0:raise ValueError('Invalid UPS')
        self.energy_kwh=self.power_kw*self.backup_min/60.
