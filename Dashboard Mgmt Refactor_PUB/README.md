# Sample Data Processing README

### Description
This series of Python scripts was developed as a practical approach to clean and merge data for periodic data upload to Google Sheets as part of a fast-paced 2020 election-cycle collaboration. These processed data are uploaded as two datasets to automatically update visualizations in a linked Google Data Studio dashboard, used to assess campaign progress and impact. 

The seven data cleaning and merging scripts and the one Google Sheets upload script can be run properly through the single script `0_dashboarding interactions single run_PUB.py`. 



### Configuration
**Data**: Data should be downloaded as CSVs from the three data sources: HubSpot CRM, HubSpot Notes, and SalesHandy. These should all be stored in the same directory, with SalesHandy emails placed in a unique folder within that directory. 

**Google Sheets**: If the user wishes to push dataframes to Google Sheets with `google_sheets_upload_18sep20.py`, the user will have to save credentials through the Google Sheets API before running the code.  Guidance and template code for generating these credentials is available in the [Google Sheets for Developers documentation]( https://developers.google.com/sheets/api/quickstart/python?authuser=4). As a workaround for those unable to configure the Google Sheets API, users can also copy and paste the datasets into the appropriate Google Sheets manually or upload the data as new Google Sheet and then upload this data in Google Data Studio.

*Notes:* As of Fall 2020, HubSpot CRM and Notes must be accessed separately. As of Fall 2020, SalesHandy has no free public API and allows users to manually download separate CSVs with data for each email campaign. 


### Running the Script 
To run all data processing and upload at once, simply run `0_dashboarding interactions single run_PUB.py`. 

The user will be asked to input the following:
- Filepath to directory where downloaded data is stored.
- The name of the folder within this directory containing SalesHandy datafiles.
- The csv of HubSpot CRM (Contacts) data.
- The csv of HubSpot Notes data (meetings).

### Rationale and Mofidications
These scripts are written to provide consistently high-quality data in the absence of centralized data management infrastructure during a fast-paced electoral campaign. Note these scripts are practically designed to be interactive and "talkative" (significant use of `print`) for: 
- execution and troubleshooting by multiple teammates who have limited comfort in Python
- changing filenames and structures between periodic updates.

For less interactivity, the user may adjust the filepaths and filenames (four in total) away from inputs in the script `dashboarding interactions single run_PUB.py` A rapid refactor could make this script less talkative. 

### Scripts
This repo contains 9 scripts for data preparation and delivery. The function of each script is summarized below:
- `0_dashboarding interactions single run_PUB.py`: runs the other 8 scripts in appropriate order.
- `A_SalesHandy_appender.py`: appends SalesHandy CSVs together and creates an "email domain" field for the most effective join to HubSpot CRM data.
- `B_SalesHandy_combiner_add_email_stage_number.py`: transforms the appended SalesHandy data into one row per political candidate, retaining relevant data fields.
- `C_SalesHandy_separator_send_and_reply_lines.py`: creates new dataset that transforms email send and email reply to separate rows for GDS time series visualizations.
- `D_SalesHandy_and_HubSpot_joiner_fix_b.py`: merges SalesHandy and HubSpot CRM data (left merge), for maximum coverage and accuracy in the absence of a shared ID field.
- `E_SH_separated_and_HS_contacts_joiner.py`: merges the *separated* SalesHandy and HubSpot CRM data from C.
- `F_Reformat_HubSpot_notes_for_Contacts_join_cleaned.py`: prepares data from HubSpot Notes (meetings) for a clean merge with dataset.
- `G_HubSpot_Notes_merge_to_HS_contacts.py`: merge HubSpot notes to dataset with summary information provided. 
- `google_sheets_upload_18sep20.py`: pushes datasets to designated Google Sheets (requires credentials configuration),