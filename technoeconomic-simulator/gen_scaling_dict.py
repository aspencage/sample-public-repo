# generate scaling dictionary

# create the scaling_dict that fits inside the part_dict
## from either a part-scaling-data file or json

import pandas as pd 
import numpy as np
import os
import json 

# from scipy.sparse import data 

from curve_fit_linear import get_linear_fn

def gen_scaling_dict(part_dict, fp, 
    return_part_dict = False):

    # can make conditional for dict import option later 
    df = pd.read_excel(fp)
    df_meta = pd.read_excel(fp, sheet_name="metadata", header=None, usecols = [0,1])

    # for later option to import a dict obj/file directly  
    if df is not None: 
        data_dict = df.to_dict()

    # metadata sxn
    df_meta.set_index(0, inplace=True)
    sr_meta = pd.Series(df_meta[1])

    # generates col map
    col_map_cols = ["scaling_parameter", "model_name", "model_cost", "watts", "Column mapping"]
    col_map = sr_meta[col_map_cols].dropna().to_dict()

    scaling_param_col = col_map["scaling_parameter"]
    col_map.pop("scaling_parameter") # beware pop edits global object 

    x_col = sr_meta["scaling_parameter"]
    x = df[x_col]

    if sr_meta["scaling_type"].lower() == "water flow":
        x_units = "gallons minute-1"
    elif sr_meta["scaling_type"].lower() == "number final unit":
        x_units = "final_unit-1" 

    # fn_list part here
    try:
        cost_data = df[col_map["model_cost"]] 
    except KeyError:
        cost_data = df["model_cost"] 
    fn_list = [(cost_data, "cost", "usd")]

    if sr_meta["Emissions category"].lower() == "electricity":
        try:
            watts_data = df[col_map["watts"]] 
        except KeyError:
            watts_data = df["watts"] 
    else: 
        raise KeyError(f"not operationalized for value: {sr_meta['Emissions category']}")
    fn_list.append((watts_data, "electricity", "watts"))

    fn_dict_list = []
    for fn_tuple in fn_list:
        y = fn_tuple[0]
        y_name = fn_tuple[1]
        y_units = fn_tuple[2]
        fn_dict = get_linear_fn(x, y, y_name, y_units, plot = False)
        fn_dict_list.append(fn_dict)

    scaling_dict = {
        "scaling_input_unit": x_units,
        "continuous fns": fn_dict_list,
        "discrete steps": {
            "scaling_param_col": scaling_param_col,
            "col_map": col_map,
            "data": data_dict
            },
        "data source": str(fp),
        "useful_life" : sr_meta["useful_life"]
        }
    # useful_life in scaling_dict for now

    if return_part_dict == False:
        return scaling_dict 

    elif return_part_dict == True:
        part_dict["scaling_dict"] = scaling_dict
        return part_dict


# add a scaling dictionary if one already exists in JSON / dict form
def add_scaling_dict(part_dict: dict, 
    scaling_json: str = None, scaling_dict: dict = None):
    if scaling_dict is not None:
        part_dict["scaling_dict"] = scaling_dict
    elif scaling_json is not None:
        with open(scaling_json, "r") as file:
            scaling_dict = json.load(file) 
            part_dict["scaling_dict"] = scaling_dict
    else:
        raise ValueError("provide value for either scaling_json or scaling_dict")

    return part_dict


# used for _scale_quantity 
def _update_part_dict(
    part_dict: dict, 
    update_json: str = None, 
    update_dict: dict = None):

    if update_json is not None:
        with open(update_json, "r") as file:
            update_dict = json.load(file) 

    for k,v in update_dict.items():
        try:
            part_dict[k]
        except KeyError:
            part_dict[k] = v

    return part_dict


# simple wrapper fn to generate and dump part_dict or scaling_dict json file 
def dump_component_json(part_dict, 
    part_datapath, fn_export,
    fd_export = None,
    component_type="part"):

    if component_type == "part":
        gen_scaling_dict(part_dict, part_datapath, 
            return_part_dict = True)

    elif component_type == "scaling":
        gen_scaling_dict(part_dict, part_datapath, 
            return_part_dict = False)

    else:
        raise KeyError("Acceptable values are 'part' or 'scaling'")

    if fd_export is not None:
        os.chdir(fd_export)
    with open(fn_export,"w") as file:
        json.dump(scaling_dict, file) 


if __name__ == "__main__":

    # example list of part_dict (here with only one)
    parts_dicts = [
        { 
            "diagram_part" : "EXAMPLE-PART-TYPE",
            "scaling_type" : "maximum flow rate",
            "part_function" : "decontamination",
            "scaling_dict" : "undefined",
            "scaling_setting" : "continuous"
        }
        ]
    
    part_dict = parts_dicts[0]

    fp = r"PATH/TO/DIRECTORY"
    fn = "PART-OBJECT-IN-STRUCTURED-TEMPLATE"
    ext = "xlsx"
    part_datapath = fp + "\\" + fn + "." + ext

    os.chdir(fp)
    df = pd.read_excel(fn + "." + ext)

    scaling_dict = gen_scaling_dict(part_dict, part_datapath, return_part_dict = False)

    part_dict_populated = gen_scaling_dict(part_dict, part_datapath, 
        return_part_dict = True)