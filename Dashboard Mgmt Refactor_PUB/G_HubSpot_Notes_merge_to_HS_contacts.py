# HubSpot notes merge

'''
purpose:
following the SalesHandy and HubSpot joiner,
    and the processing of the HubSpot notes
    join the HubSpot notes
'''

import pandas as pd
import time

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

def HS_Notes_merge_HS_Contacts(csvPath, hs_notes_csv, sh_hs_contacts_combined_csv):
    hs_notes_df = pd.read_csv(csvPath + "\\" + hs_notes_csv + ".csv")

    unique_notes = hs_notes_df["Engagement ID"].nunique()
    print("The number of distinct notes is:", unique_notes)

    sh_hs_contacts_combined_df = pd.read_csv(csvPath + "\\" + sh_hs_contacts_combined_csv + ".csv")

    full_combined_df = pd.merge(
        sh_hs_contacts_combined_df,
        hs_notes_df,
        left_on="Full Name",
        right_on="Campaign Contact Single",
        how="left"
        )
    full_combined_df.drop(["Email Domain_x", "Email Domain_y"], axis=1, inplace=True)
    print(f"Conducted a join between {sh_hs_contacts_combined_csv}.csv and {hs_notes_csv}.csv at full_combined_df based on HubSpot full name.")

    merged_notes = full_combined_df["Campaign Contact Single"].notna().sum()

    # feedback on merge success
    percent_notes_merged = round(merged_notes / unique_notes * 100,1)
    print("The number of joined records is:", merged_notes)
    print("The percentage of unique notes merged is:", str(percent_notes_merged) + "%")

    datetime_string = time.strftime("%d%b%y-%H%M%S")
    csvName = "SH_HS_Contacts-and-Notes_triple-merge_" + datetime_string
    full_combined_df.to_csv(csvPath + "\\" + csvName + ".csv",
                            index = False)
    print("Saved combined file as:", csvPath + "\\" + csvName + ".csv")   

    # df to determine which calls are scheduled without replies
    df_no_reply_with_call = full_combined_df[(full_combined_df["Replied Bool"] == False)
                                             & (full_combined_df["Engagement ID"].notna())]

    return csvName

if __name__ == "__main__":
    print("Make sure that there has already been a left join between the SalesHandy and the HubSpot.")
    print()
    print("Make sure the HubSpot Notes CSV has already been processed.")
    print()

    csvPath = r"REPLACE_WITH_DESIRED_FILEPATH"

    print(f"Make sure files are stored in {csvPath}")
    print()

    hs_notes_csv = input("What is the name of the HubSpot notes CSV you want to add? (no extension) ")
    sh_hs_contacts_combined_csv = input("What is the name of the SalesHandy/HubSpot Contacts left join CSV you want to import as the base? (no extension) ")

