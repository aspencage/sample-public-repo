# reformat HubSpot notes for candidate join

import pandas as pd

'''
purpose:
take downloaded hubspot notes (from dashboard/report function) and modify them
    so they are ready for a name join with candidate
'''

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

def format_HS_notes(csvPath):
    personnel = set() # NOTE - add any names of team personnel here

    csvFile = input("What is the name of the HubSpot Notes CSV file you want to import? (no extension) ")
    df = pd.read_csv(csvPath + "\\" + csvFile + ".csv")

    campaignContact_metaList = [] 

    # iterate through each cell in specific column
    for contactString in df["Associated Contacts"]:
        contactSet = set(contactString.split(sep=", "))
        campaignContact_List = list(contactSet - personnel)
        campaignContact_metaList.append(campaignContact_List)

    df.insert(3, "Associated Campaign Contacts", campaignContact_metaList)

    camp_cont_names_ordered = []

    for contactList in df["Associated Campaign Contacts"]:
        for contact in contactList:
            camp_cont_names_ordered.append(contact)

    # apply instead of crude looping to get number in the list
    df["Number Campaign Contacts"] = df.apply(lambda row : len(row["Associated Campaign Contacts"]), axis=1)

    df = df.loc[df.index.repeat(df["Number Campaign Contacts"])]

    df = df.sort_index()
    df.insert(0, "Campaign Contact Single", camp_cont_names_ordered)

    HS_Notes_formatted_csv = csvFile + " _merge ready"
    df.to_csv(csvPath + "\\" + HS_Notes_formatted_csv + ".csv",
              index = False)

    return HS_Notes_formatted_csv

if __name__ == "__main__":
    print('Make sure the file is saved in the proper data sheets folder set under csvPath.')

    csvPath = r"REPLACE_WITH_DESIRED_FILEPATH"
