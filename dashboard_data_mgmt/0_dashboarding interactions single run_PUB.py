# dashboarding interactions single run_PUB

'''
purpose:
single script to run the data processing operations and push the merged datasets to Google Sheets  
'''

print('Make sure all relevant files and folders are downloaded and saved in the same directory.')
print(''' Relevant files and folders to download are:
1. HubSpot Contacts 
2. SalesHandy raw data (saved into a specific folder)
3. HubSpot Notes
''')
print("Make sure the SalesHandy directory is unzipped.")

import pandas as pd

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

print()
csvPath = r"REPLACE_WITH_DESIRED_FILEPATH"
pathCheck = input(f"The current path for all CSVs is {csvPath}. Is this path acceptable? ")

if (pathCheck.lower().strip() == "no"):
    csvPath = input("What would you like to set as the new path? ")
    # potentially need to add r to the beginning?
elif (pathCheck.lower().strip() == "yes"):
    print(f"Continuing with {csvPath}.")
else:
    print(f"Okay, we're going to take that to mean you are okay with {csvPath}.") 

from A_SalesHandy_appender import SalesHandy_appender

SH_appended_csvName = SalesHandy_appender(csvPath)
print("SalesHandy Appender completed.")

from B_SalesHandy_combiner_add_email_stage_number import SalesHandy_combiner

SH_combo = SalesHandy_combiner(csvPath, SH_appended_csvName)
print("SalesHandy Combiner completed.")

from C_SalesHandy_separator_send_and_reply_lines import SalesHandy_seperator

SH_seperate = SalesHandy_seperator(csvPath, SH_appended_csvName)
print("SalesHandy Seperator completed.")

from D_SalesHandy_and_HubSpot_joiner_fix_b import join_SH_combined_and_HS_contacts

print('Make sure that the "Email Domain" property is successfully in HubSpot Contacts sheet.')

hs_file = input("What is the name of the HubSpot Contacts file you want to import? (no extension) ")

SH_combo_HS_contacts = join_SH_combined_and_HS_contacts(csvPath, SH_combo, hs_file)
print("Join between the Combined SalesHandy and the HubSpot Contacts completed.")

from E_SH_separated_and_HS_contacts_joiner import join_SH_seperated_and_HS_contacts

SH_contact_time_series = join_SH_seperated_and_HS_contacts(csvPath, SH_seperate, hs_file)
print("Join between the Seperated SalesHandy and the HubSpot Contacts completed.")
print("SH_contact_time_series", SH_contact_time_series)

from F_Reformat_HubSpot_notes_for_Contacts_join_cleaned import format_HS_notes

HS_Notes_formatted_csv = format_HS_notes(csvPath)
print("Reformatting of HubSpot Notes completed.")

from G_HubSpot_Notes_merge_to_HS_contacts import HS_Notes_merge_HS_Contacts

triple_merge_csv = HS_Notes_merge_HS_Contacts(csvPath, HS_Notes_formatted_csv, SH_combo_HS_contacts)
print("Addition of the HubSpot Notes completed to create the triple merge file.")
print("triple_merge_csv", triple_merge_csv)

from google_sheets_upload_18sep20 import *

# NameError: name 'credentialsPath' is not defined

# both values are the returned csv names without the .csv
importCsv_spreadsheet_dict = {
    "REPLACE_WITH_GSHEETS_ID_1" : triple_merge_csv,
    "REPLACE_WITH_GSHEETS_ID_2" : SH_contact_time_series
    }

push_multi_csvs_to_gsheet(csvPath, importCsv_spreadsheet_dict)
