# gen_part_dict

# purpose: read in a structured XLSX file to create the parts library [parts_dict_1, ... parts_dict_n] for the simulator program

import re 
import pandas as pd 
import numpy as np

from gen_scaling_dict import gen_scaling_dict, add_scaling_dict, _update_part_dict


# used when a scaling_dict is imported (w add_scaling_dict())
def gen_col_map(part_dict: dict) -> dict:
    col_map = {}

    # columns used in the current draft to name columns for the col_map
    col_cols = ["col_scaling_param", "col_model_name", "col_model_cost",
        "col_watts"]
    
    for col in col_cols:
        if col != "col_scaling_param":
            if part_dict[col] is not None:
                # names properly in scaling dict
                col_map[col[4:]] = part_dict[col]
        else:
            # deals with different naming convention for scaling_param_col
            if part_dict[col] is not None:
                col_map["scaling_param_col"] = part_dict[col]

    return col_map


def drop_flag_nan_parts(df):
    parts_mask = df.data_filepath.notna()
    df_partData = df.loc[parts_mask]
    df_no_partData = df.loc[~ parts_mask]
    if df_partData.shape[0] < df.shape[0]:
        print("NOTE: diagram parts (part types) missing data detected.")
        print(f"{df_partData.shape[0]} rows have data and \
{df_no_partData.shape[0]} are missing data of {df.shape[0]} rows total \
in this parts-typology.") 
        print()
        print("rows containing data:\n", list(df_partData[["part_index", "diagram_part"]].to_records(index=False)))
        print()
        print("rows lacking data:\n", list(df_no_partData[["part_index", "diagram_part"]].to_records(index=False)))
        print()
        print("dropping missing rows so analysis can proceed...")
        print("NOTE: be aware that any analysis of economics or GHGs proceeding without populating this data will UNDERESTIMATE costs and emissions")
        print()

    return df_partData


def gen_parts_library(fp: str) -> list:

    if re.search(".csv", fp):
        df = pd.read_csv(fp)
    elif re.search(".xls", fp):
        df = pd.read_excel(fp)
    else:
        raise KeyError("Select a valid extension")

    # for later option to import a dict, list of dict, json directly directly  
    if df is not None: 

        df = drop_flag_nan_parts(df)
        df = df.where(pd.notnull(df), None)

        parts_dicts = df.to_dict("records")

    parts_library = []

    for part_dict in parts_dicts:

        part_fp = part_dict["data_filepath"]

        if part_dict["scaling_setting"].lower() in ["continuous","discrete"]:
            if re.search(".json", part_fp):
                part_dict = add_scaling_dict(part_dict, scaling_json=part_fp) 

            else: 
                part_dict = gen_scaling_dict(part_dict, 
                    fp = part_fp,
                    return_part_dict = True)

        elif part_dict["scaling_setting"].lower() in ["constant","quantity","number"]:
            if re.search(".json", part_fp):
                part_dict = _update_part_dict(part_dict, update_json = part_fp, update_dict = None) 
            # add option for a simplified template like sr_meta 
            else: 
                ("currently operationalized for JSON dictionaries.")

        else:
            print(f"Improper scaling_setting provided for {part_dict['part_index']}: {part_dict['diagram_part']}. Assuming quantity scaling...")

        parts_library.append(part_dict)

    return parts_library
