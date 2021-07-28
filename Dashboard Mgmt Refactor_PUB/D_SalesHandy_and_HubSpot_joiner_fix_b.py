# SalesHandy and HubSpot joiner

# GDS blend does left join to SH data

'''
purpose
merges the SalesHandy and HubSpot files 
    left merge on SalesHandy
'''

import pandas as pd
import numpy as np
import time

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

def join_SH_combined_and_HS_contacts(csvPath, sh_file, hs_file):
    salesHandy_outreach_df = pd.read_csv(csvPath + "\\" + sh_file + ".csv")

    print("The length of salesHandy_outreach_df is:", len(salesHandy_outreach_df))

    hubSpot_contacts_df = pd.read_csv(csvPath + "\\" + hs_file + ".csv")

    print("The length of hubSpot_contacts_df with all contacts is:", len(hubSpot_contacts_df))

    # remove all non candidates from the hubSpot df
    hubSpot_contacts_df = hubSpot_contacts_df[hubSpot_contacts_df["Campaign role"] == "Candidate"]

    print("The length of hubSpot_contacts_df with only candidate contacts is:", len(hubSpot_contacts_df))

    # used for merge later
    hubSpot_contacts_df["Full Name"] = hubSpot_contacts_df["First Name"] + " " + hubSpot_contacts_df["Last Name"]

    # lower emails before beginning merges, otherwise will not qualify as duplicates 
    salesHandy_outreach_df["Recipient Email"] = salesHandy_outreach_df["Recipient Email"].str.lower()
    hubSpot_contacts_df["Email"] = hubSpot_contacts_df["Email"].str.lower()

    # capitalize only the first letter of each name 
    salesHandy_outreach_df["Recipient Name"] = np.where(
        salesHandy_outreach_df["Recipient Name"].str.contains("Mc|Mac"),
        salesHandy_outreach_df["Recipient Name"],
        salesHandy_outreach_df["Recipient Name"].str.title()
        )
        
    hubSpot_contacts_df["Full Name"] = np.where(
        hubSpot_contacts_df["Full Name"].str.contains("Mc|Mac"),
        hubSpot_contacts_df["Full Name"],
        hubSpot_contacts_df["Full Name"].str.title()
        )

    # merge on email domain, excepting common domains
    generic_domains_list = [
        "gmail.com",
        "outlook.com",
        "yahoo.com",
        "aol.com",
        "earthlink.net",
        "comcast.net",
        "sent.com",
        "live.com",
        "hotmail.com",
        "att.net",
        "me.com",
        "sbcglobal.net",
        "flash.net",
        "icloud.com",
        "elections.facebook.com",
        "house.texas.gov"
        ]

    combined_df_domain = pd.merge(
        salesHandy_outreach_df[~salesHandy_outreach_df["Email Domain"].isin(generic_domains_list)],
        hubSpot_contacts_df,
        on="Email Domain",
        how="left"
        )
    print(f"Conducted a join between {sh_file} and {hs_file} at combined_df_domain based on email domain.")

    print("the length of combined_df_domain is:", len(combined_df_domain))
    print("combined_df_domain: \n", combined_df_domain)

    # recipient email as a (should be) unique identifier 
    already_merged = combined_df_domain["Recipient Email"]

    # merge on full email
    combined_df_full_emails = pd.merge(
        salesHandy_outreach_df[~salesHandy_outreach_df["Recipient Email"].isin(already_merged)],
        hubSpot_contacts_df,
        left_on="Recipient Email",
        right_on="Email",
        how="left"
        )

    print("the length of combined_df_full_emails is:", len(combined_df_full_emails))
    print("combined_df_full_emails: \n", combined_df_full_emails)

    combined_df_domain_and_full_email = combined_df_domain.append(combined_df_full_emails)

    print("the length of combined_df_domain_and_full_email is:", len(combined_df_domain_and_full_email))
    print("combined_df_domain_and_full_email: \n", combined_df_domain_and_full_email)

    already_merged = combined_df_domain_and_full_email["Recipient Email"]

    # merge on candidate name
    combined_df_candidate_name = pd.merge(
        salesHandy_outreach_df[~salesHandy_outreach_df["Recipient Email"].isin(already_merged)],
        hubSpot_contacts_df,
        left_on="Recipient Name",
        right_on="Full Name",
        how="left"
        )

    print("the length of combined_df_candidate_name is:", len(combined_df_candidate_name))
    print("combined_df_candidate_name: \n", combined_df_candidate_name)

    combined_df_ALL = combined_df_domain_and_full_email.append(combined_df_candidate_name)

    print("the length of combined_df_ALL is:", len(combined_df_ALL))
    print("combined_df_ALL: \n", combined_df_ALL)

    combined_df_ALL_dupeless = combined_df_ALL.drop_duplicates(subset=["Recipient Email"])

    print("the length of combined_df_ALL with dropped duplicates is:", len(combined_df_ALL_dupeless))
    print("combined_df_ALL: \n", combined_df_ALL_dupeless)

    datetime_string = time.strftime("%d%b%y_%H%M")

    final_merged_csv_name = "SH Combined_to_HS Contacts_left merge_" + datetime_string
    combined_df_ALL_dupeless.to_csv(csvPath + "\\" + final_merged_csv_name + ".csv",
                                    index = False)
    print("Saved SalesHandy / HubSpot Contacts left merge.")
    print("Saved as:", final_merged_csv_name + ".csv")

    return(final_merged_csv_name)

if __name__ == "__main__":
    print('Make sure the SalesHandy sheets have been combined.')
    print("Make sure both the SalesHandy and HubSpot Contacts sheets are located in the right file path.")
    print('Make sure that the "Email Domain" property is successfully in HubSpot Contacts sheet.')
    print()

    csvPath = r"REPLACE_WITH_DESIRED_FILEPATH"

    sh_file = input("What is the name of the SalesHandy combined file you want to import? (no extension) ")

    hs_file = input("What is the name of the HubSpot contacts file you want to import? (no extension) ")
