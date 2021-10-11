# SalesHandy combiner

'''
purpose:
code to take the completed saleshandy sheets
    and combine into a single line per candidate

note:
see below code for info on conditional displaying 
'''

import pandas as pd
import numpy as np
import time

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

def SalesHandy_combiner(csvPath, salesHandy_appended_csv):
    salesHandy_appended_df = pd.read_csv(csvPath + "\\" + salesHandy_appended_csv + ".csv")

    # create a dictionary of blank lists
    # each candidate with append to each list
    # convert to df at end

    # remove the bounces
    salesHandy_appended_df = salesHandy_appended_df[salesHandy_appended_df["Status"] != "Bounced"]

    new_df_dict = {
        "Email Campaign Name" : [],
        "Email Stage Number when Replied" : [],
        "Recipient Email" : [],
        "Recipient Name" : [],
        "Status" : [],
        "First Email Sent At" : [],
        "First Reply Received At" : [],
        "Opened Bool" : [],
        "Clicked Bool" : [],
        "Replied Bool" : [],
        "Unsubscribed Bool" : [],
        "Email Domain" : []
        }

    candidate_email_Set = set(salesHandy_appended_df["Recipient Email"]) 

    for candidate_email in candidate_email_Set: 
        candidate_df = (salesHandy_appended_df[salesHandy_appended_df["Recipient Email"] == candidate_email])
        candidate_df = candidate_df.reset_index()

        new_df_dict["Email Campaign Name"].append(candidate_df["Campaign Name"][0])
        new_df_dict["Recipient Email"].append(candidate_df["Recipient Email"][0])
        new_df_dict["Recipient Name"].append(candidate_df["Recipient Name"][0])
        new_df_dict["Status"].append(candidate_df["Status"][0])
        new_df_dict["Email Domain"].append(candidate_df["Email Domain"][0])

        # calculated rows
        if any(candidate_df["Replied"] == "Yes"):
            stage_at_first_reply = candidate_df[candidate_df["Replied"] == "Yes"].iloc[0]["Stage Number"]
            new_df_dict["Email Stage Number when Replied"].append(stage_at_first_reply)
        else:
            new_df_dict["Email Stage Number when Replied"].append("")

        if any(candidate_df["Click Count"] > 0):
            new_df_dict["Clicked Bool"].append(True)
        else:
            new_df_dict["Clicked Bool"].append(False)
            
        if any(candidate_df["Open Count"] > 0):
            new_df_dict["Opened Bool"].append(True)
        else:
            new_df_dict["Opened Bool"].append(False)

        if any(candidate_df["Replied"] == "Yes"):
            new_df_dict["Replied Bool"].append(True)
        else:
            new_df_dict["Replied Bool"].append(False)

        if any(candidate_df["Unsubscribed"] == "Yes"):
            new_df_dict["Unsubscribed Bool"].append(True)
        else:
            new_df_dict["Unsubscribed Bool"].append(False)

        new_df_dict["First Email Sent At"].append(candidate_df["Sent At"].astype(str).min())

        candidate_df["Replied At"] = candidate_df["Replied At"].replace("-", np.NaN)

        if candidate_df["Replied At"].astype(str).min() and candidate_df["Replied At"].astype(str).min() != "nan":
            new_df_dict["First Reply Received At"].append(candidate_df["Replied At"].astype(str).min())
        else:
            new_df_dict["First Reply Received At"].append("")

    datetime_string = time.strftime("%d%b%y-%H%M%S")

    compiled_SalesHandy_df = pd.DataFrame.from_dict(new_df_dict)
    compiled_SalesHandy_csv = "SalesHandy_combined_email_" + datetime_string

    compiled_SalesHandy_df.to_csv(csvPath + "\\" + compiled_SalesHandy_csv + ".csv",
                                  index = False)
    print(f"Successfully saved the combined SH dataframe as SalesHandy_combined_email_{datetime_string}.csv")

    return compiled_SalesHandy_csv

if __name__ == "__main__":
    print('Make sure you have downloaded the correct SalesHandy sheets and appended them using the SH appender code.')

    csvPath = r"REPLACE_WITH_DESIRED_FILEPATH"

    salesHandy_appended_csv = input("What is the name of the appended SalesHandy CSV? (no ext) ")
    SalesHandy_combiner(csvPath, salesHandy_appended_csv)
