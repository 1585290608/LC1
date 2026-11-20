"""Independent, immutable fuel models. Never infer fuel from delivered-to-load power."""
from pathlib import Path
import json,math
from ..core.components import Diesel,EPS
CONFIG=Path(__file__).resolve().parent / "config"
class UnsupportedFuelDomain(ValueError):pass
class FixedFuel:
    name='FIXED_025'
    def rate_lph(self,power_kw,rated_kw=100.):
        if not math.isfinite(power_kw) or not 0<=power_kw<=rated_kw+EPS:raise ValueError('Invalid generated ONpower')
        return .25*power_kw
class NativeFuel:
    name='MDT_DERIVED'
    def __init__(self):self.definition=json.loads((CONFIG/'fuel-models.json').read_text(encoding='utf-8'))
    def rate_lph(self,power_kw,rated_kw=100.):
        if not math.isfinite(power_kw) or power_kw<0 or power_kw>rated_kw+EPS:raise ValueError('Invalid generated ONpower')
        if power_kw<=EPS:return 0. # OFF, not a verified running-idle model.
        f=power_kw/rated_kw
        if f<.25-1e-10:raise UnsupportedFuelDomain('MDT0%is a mixed-unit idle point; positive<25%not modelled/validated')
        xs=self.definition['fractions'][1:];ys=self.definition['stored_values'][1:]
        i=min(2,max(0,int((f-.25)*4)));w=(f-xs[i])/(xs[i+1]-xs[i]);sfc=ys[i]+w*(ys[i+1]-ys[i])
        return power_kw*sfc*self.definition['USgal_to_L']
def model(name):return FixedFuel() if name=='FIXED_025' else NativeFuel() if name=='MDT_DERIVED' else (_ for _ in ()).throw(ValueError(name))
class ResearchDiesel(Diesel):
    def set_fuel_model(self,name):self.selected_fuel_model=model(name);self.start_commands=0;self.last_start_command=0;return self
    def fuel_rate_lph(self,power_kw):return self.selected_fuel_model.rate_lph(power_kw,self.rated_kw)
    def dispatch(self,request_kw,dt_h=1.):
        self.last_start_command=int(request_kw>EPS and self.enabled and self.fuel_l>EPS and not self.running and self.state!='STARTING')
        self.start_commands+=self.last_start_command
        return super().dispatch(request_kw,dt_h)
