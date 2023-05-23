# fluxes

import json 
import random 

class _FluxObj:
    def __init__(self, data):
        if type(data) == str:
            data_dict = json.load(open(data + '.json'))
        elif type(data) == dict:
            data_dict = data
        else:
            raise ValueError("Only string (filepath) and dict allowed.")
        self.value = data_dict['value']
        self.type = data_dict['type']
        self.units = data_dict['units']
        self.source = data_dict['source']
        self.data = data_dict

        if data_dict.get("phase") is not None:
            self.phase = data_dict["phase"]


class EmissionFactor(_FluxObj): 
    def __init__(self, data):
        super().__init__(data)

    def __str__(self):
        return f"{self.value} {self.units}"


class GHGConversion:
    gwp_reference = {
        2: {100: {"co2":1,"ch4":21,"n2o":310}}, 
        4: {100: {"co2":1,"ch4":25,"n2o":298}, 20: {"co2":1,"ch4":72,"n2o":289}},
        5: {100: {"co2":1,"ch4":28,"n2o":265}, 20: {"co2":1,"ch4":84,"n2o":264}},
        6: {100: {"co2":1,"ch4_f":29.8, "ch4_nf":27.2, "n2o":273}, 
            20: {"co2":1,"ch4_f":82.5, "ch4_nf":80.8, "n2o":273}}
        }

    def __init__(self, ar=6, time_horizon=100):
        gwp_d = self.gwp_reference[ar][time_horizon]
        self.ar = ar 
        self.time_horizon = time_horizon

        self.co2_gwp = gwp_d["co2"]
        if ar == 6:
            self.ch4_f_gwp = gwp_d["ch4_f"]  
            self.ch4_nf_gwp = gwp_d["ch4_nf"]  
        else: 
            self.ch4_gwp = gwp_d["ch4"] 
        self.n2o_gwp = gwp_d["n2o"] 

    def calc_co2e(self, co2=0, ch4=0, n2o=0, origin = None):
        if self.ar == 6: 
            if origin.lower() == "fossil" or origin.lower() == "f":
                co2e = co2*self.co2_gwp+ch4*self.ch4_f_gwp+n2o*self.n2o_gwp
            elif origin.lower() == "nonfossil" or origin.lower() == "non-fossil" or origin.lower() == "nf":
                co2e = co2*self.co2_gwp+ch4*self.ch4_nf_gwp+n2o*self.n2o_gwp
            else:
                raise KeyError("For AR6 GWPs, fossil or non-fossil origin must be designated. \
No value or an incorrect value was provided.")
        else:
            co2e = co2*self.co2_gwp+ch4*self.ch4_gwp+n2o*self.n2o_gwp

        return co2e


class GridElectricity():
    
    def __init__(self, mwh_ef, mwh_p: float, elec_units:str = "MWh"):
        """Object representing grid electricity used in a phase of Atax EF mitigation.

        Args:
            mwh_ef (str, dict, float): The GHG emission factor (mt CO2e/MWh). If string, it assumes a full filepath to a JSON dictionary. If a dictionary, it initializes the dictionary into an embedded class object. If a float or integer, it simply assumes this is the EF in mt CO2e/kWh. 
            mwh_p (float): The price of electricity (USD/MWh). This is currently operationalized for grid electricity.
        """
        self.elec_units = elec_units
       
        # emission factor 
        if type(mwh_ef) == str or type(mwh_ef) == dict:
            self.mwh_ef = EmissionFactor(mwh_ef)
        elif type(mwh_ef) == float or type(mwh_ef) == int: # if just enter number 
            mwh_ef_dict = {
                'value': mwh_ef,
                'type': 'user input',
                'units': 'mt CO2e MWh-1',
                'source': 'user input'
            }
            self.mwh_ef = EmissionFactor(mwh_ef_dict)
        else:
            raise TypeError("Only string (filepath), dict, and numeric (unitsS HERE)")
        # TODO future version could allow user to provide electrical grid zone 

        # electricity units price
        self.mwh_p = dict()
        self.mwh_p["value"] = mwh_p
        self.mwh_p["units"] = "USD MWh-1"

    def calc_elec_emissions(self, q_mwh):
        return q_mwh * self.mwh_ef.value

    def calc_elec_totalcost(self, q_mwh):
        return q_mwh * self.mwh_p["value"]

    def add_mwh(self, addl_mwh):
        try:
            self.q_mwh += addl_mwh
        except AttributeError:
            self.q_mwh = addl_mwh

    def populate(self):
        try:
            self.emissions_total = self.calc_elec_emissions(self.q_mwh)
            self.cost_total = self.calc_elec_totalcost(self.q_mwh)
            return self.emissions_total, self.cost_total
        except AttributeError:
            print("AttributeError raised. You may still have to populate the quantity of MWh (q_mwh) \
within the instance. These can be added manually or using the add_mwh(addl_mwh) method.")

    def summarize(self):
        c = f"""GRID ELECTRICITY SUMMARY INFORMATION:
units cost: {round(self.mwh_p["value"],2)} {self.mwh_p["units"]}
emission factor: {round(self.mwh_ef.value,4)} {self.mwh_ef.units}"""
        try:
            o = f"quantity consumed: {round(self.q_mwh,4)} {self.elec_units}"
            try:
                s = f"estimated emissions: {round(self.emissions_total,4)} {self.mwh_ef.units}\n\
estimated cost: {round(self.cost_total,2)} {self.mwh_p['units']}"
                o = o + "\n" + s
            except:
                pass
            c = c + "\n" + o
        except AttributeError:
            pass 
        print(c)


def _calc_h2o_flow(
    open_system: bool, v_system: int, hrs_replacement: float = None) -> dict:
    """Calculate the water flow for the system in gallons per minute, based on \
whether it is an open vs. closed system, the total volume of the system, and \
the number of hours dedicated to water replacement in the full system \
(i.e., with the taps running) if this is for a closed system. These default values \
are both approximations. 

    Args:
        open_system (bool): True if an open system, False if a closed system.
        v_system (int): The total volume of the cultivation system, in gallons. \
        hrs_replacement (float, optional): For closed systems, the number of \
hours dedicated to replacing all water in the system on average per week. \
This should be an estimate of the "taps on" time. Defaults to None.

    Returns:
        dict: A "value","units" dictionary for GPM.
    """

    gpm = {"value":None,"units":"gallons minute-1","open_system":open_system}
    RANDOM_VALUE = 1/random.randint(200,1000) # random value for example 
    if open_system:
        gpm["value"] = v_system * RANDOM_VALUE
    else:
        gpm["value"] = v_system * RANDOM_VALUE*100 / (hrs_replacement*60)
        gpm["hrs_replacement"] = {
            "value": hrs_replacement, 
            "units": 'average "taps-on"_hour_for_water_replacement week-1'
            }

    return gpm


if __name__ == "__main__":

    co2e = GHGConversion().calc_co2e(
        co2=0.0,
        ch4=0.118,
        n2o=0.000,
        origin="f"
    )
    print(co2e)