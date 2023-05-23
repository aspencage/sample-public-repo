# atax_parts 

import random, string
from gen_part_lib import gen_parts_library

''' 
purpose: script to house all part objects
in order to avoid circular dependencies  

NOTE - a few working example parts are provided here to demonstrate basic OOP familiarity 
'''

class _Part():
    def __init__(self, part_dict, scaling_input:dict=None): 
        # part basics 
        self.diagram_part = part_dict["diagram_part"]
        self.scaling_type = part_dict["scaling_type"] # basis of scaling e.g., water flow 
        self.part_function = part_dict["part_function"] 
        self.emissions_category = part_dict.get("emissions_category")
        
        self.scaling_setting = part_dict["scaling_setting"] 
        if scaling_input is not None:
            self.scaling_input = scaling_input
        
        # a single part_model will not be available if a scaling model specified 
        try: 
            self.part_model = part_dict["part_model"] 
            self.price = part_dict["price"]
            self.useful_life = part_dict["useful_life"]

        except KeyError: # for scaling models 
            self.scaling_dict = part_dict["scaling_dict"]
            self.useful_life = part_dict["scaling_dict"]["useful_life"]
        
        if part_dict.get("normalized_quantity") is not None:
            if isinstance(part_dict["normalized_quantity"], float) or isinstance(part_dict["normalized_quantity"], int):
                self.normalized_quantity = part_dict["normalized_quantity"] # normalized quantity is # per scaling_input (of scaling_type) I believe
            else:
                print(f"Invalid entry for normalized_quantity in part {self.diagram_part}. Setting normalized_quantity to 1.")
                self.normalized_quantity = 1
        else:
            print(f"No value for normalized_quantity in part {self.diagram_part}. Setting normalized_quantity to 1.")
            self.normalized_quantity = 1

        self.quantity_per_cycle = None 
        self.cost_per_cycle = None


    def _get_model_index(self, data, scaling_col):
        for k, v in data[scaling_col].items():
            part_sufficient = False
            if self.scaling_input["value"] > v: # if system req more than part can handle 
                model_i = k
            elif self.scaling_input["value"] < v: # if system req less than part can handle 
                model_i = k
                part_sufficient = True
                break
        if part_sufficient == False:
            print("No model in the data is sufficient for the provided scaling input. \
Scaling the number of devices to fit the scenario...")   
        return model_i, part_sufficient
            

    def _scale_model_continuous(self):
        # scale a part model continuously based on functions in the data.
        ## creates a new hypothetical part based on curve fit to real data, 
        ## prevents stepwise phenomena from biasing results

        self.quantity_per_cycle = 1 # simple placeholder, not range controlled 

        for fn in self.scaling_dict["continuous fns"]:

            fn_type = fn["type"]
            fn_params = fn["parameters"]

            if fn_type == "linear":
                m = fn_params["m"]
                b = fn_params["b"]
                x = self.scaling_input["value"]
                y_projected = m*x + b

            else:
                pass

            # other response variables included here
            if fn["response variable"] == "cost":
                self.cost_per_cycle = y_projected

            elif fn["response variable"] == "electricity":
                self.watts = y_projected

            else:
                pass


    def _scale_model_discrete(self, num_finalUnit = None):
        # select a real part based on the data  

        self.quantity_per_cycle = 1

        data = self.scaling_dict["discrete steps"]["data"]
        scaling_col = self.scaling_dict["discrete steps"]["scaling_param_col"]

        model_i, part_sufficient = self._get_model_index(data, scaling_col)

        # for both part_sufficient == True or False 
        if self.scaling_dict["discrete steps"]["col_map"]:
            # flexible and standardized naming
            ### eg if col_map["watts"] rather than current structure 
            col_map = self.scaling_dict["discrete steps"]["col_map"]
            name_col, cost_col, watts_col = col_map["model_name"], col_map["model_cost"], col_map["watts"]

            self.part_model = data[name_col][model_i]
            self.cost_per_cycle = data[cost_col][model_i]
            self.watts = data[watts_col][model_i]
            if self.scaling_type.lower() == "water flow":
                self.gpm = data[scaling_col][model_i]

        else:
            self.part_model = data["model_name"][model_i]
            self.cost_per_cycle = data["model_cost"][model_i]
            self.watts = data["watts"][model_i]
            if self.scaling_type.lower() == "water flow":
                self.gpm = data["gpm"][model_i]

        if part_sufficient == False:
            # move to _scale_quantity 
            ## this will require num_finalUnit and h2o_flow to be passed from the Cultivation instance
            self.normalized_quantity = 1
            self.price = self.cost_per_cycle
            if self.scaling_type.lower() == "number final unit":
                self._scale_quantity(num_finalUnit=self.scaling_input["value"]) 
            elif self.scaling_type.lower() == "water flow":
                self._scale_quantity(part_flow=self.gpm) 
            elif self.scaling_type.lower() == "is final unit":
                self._scale_quantity(num_finalUnit=num_finalUnit) 
        

    def _scale_quantity(self, num_finalUnit = None, part_flow = None):
        # normalized quantity is # per scaling_input
        if self.scaling_type.lower() == "number final unit": 
            self.quantity_per_cycle = self.normalized_quantity * self.scaling_input["value"] 

        elif self.scaling_type.lower() == "is final unit":
            self.normalized_quantity = num_finalUnit 
            # this should already be set from number commercial units required 
            self.quantity_per_cycle = self.normalized_quantity
        
        # normalized quantity here is calibrated to a certain GPM which is stored in scaling_input
        elif self.scaling_type.lower() == "water flow":
            # part_flow is the max GPM the part can handle 
            system_flow = self.scaling_input["value"] # the max GPM the system needs to be designed for )
            self.quantity_per_cycle = self.normalized_quantity * system_flow / part_flow 

        self.cost_per_cycle = self.quantity_per_cycle * self.price


class _Container(_Part):
    def __init__(self, part_dict, volume: int, vessel_type="Undefined"):
        super().__init__(part_dict)
        self.volume = {"value": volume, "units": "liters"}
        self.vessel_type = vessel_type


# rename to CommercialUnit or similar? 
class CommercialUnit(_Container):
    def __init__(self, part_dict):
        super().__init__(
            part_dict,
            volume = {
                "value" : random.randint(1,1000),
                "units" : "gallons",
                "source" : "randomly generated"
                },
            vessel_type = "primary commercial unit for measurement")


class _ElectricalDevice(_Part):
    def __init__(self, part_dict, scaling_input, watts=None,
        num_finalUnit = None, h2o_flow = None):
        super().__init__(part_dict, scaling_input=scaling_input)
        if watts is not None:
            self.watts = watts 
        elif part_dict.get("watts") is not None:
            self.watts = part_dict["watts"]
        elif part_dict.get("scaling_dict") is not None:
            # will update watts as well as other fields
            if part_dict["scaling_setting"].lower() == "continuous":
                self._scale_model_continuous()  
            elif part_dict["scaling_setting"].lower() == "discrete":
                self._scale_model_discrete(
                        num_finalUnit = num_finalUnit)
            elif part_dict["scaling_setting"].lower() in ["quantity","constant","number"]:
                try :
                    if self.scaling_type.lower() == "water flow":
                        self._scale_quantity(
                                num_finalUnit = num_finalUnit,
                                part_flow = self.gpm)
                    else: 
                        self._scale_quantity(
                            num_finalUnit = num_finalUnit)
                except AttributeError:
                    print("Not in spec-model structure for initial _scale_quantity(). Assuming part-scaling-data structure. Applying _scale_model_discrete() first.")
                    self._scale_model_discrete(
                        num_finalUnit = num_finalUnit)
            else:
                raise KeyError("select a valid scaling_setting.")
        else: 
            self.watts = None 
    
    def calc_energy_use(self, hours_per_period, 
        period = "week", power_frac = 1, populate=True):
        # generalized energy use equation 

        energy_use = dict() 
        energy_use["value"] = self.watts * 10**(-6) * hours_per_period * power_frac * self.quantity_per_cycle
        energy_use["units"] = f"MWh {period}-1"
        if populate == True:
            self.energy_use = energy_use
        return energy_use["value"]


