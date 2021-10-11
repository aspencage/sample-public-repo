# SalesHandy appender

'''
purpose:
code to append a bunch of saleshandy sheets into one CSV
    so we don't have to do this every time we update the data
    also, creates an "email domain" column for best join the HS
'''

import pandas as pd
import glob
import time
import re

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

def SalesHandy_appender(csvPath):
    directory = input("What is the name of the folder of SalesHandy files you want to import?")

    csv_files_in_folder = glob.glob(csvPath + "\\" + directory + "\*.csv")

    # update manually for each go
    print("The number expected from candidate SH campaigns is:", 10)
    print("This is assuming that strategic partnerships is not for candidates.")

    # announce the files as readout to prevent future errors
    print(f"There are {len(csv_files_in_folder)} CSV files in this directory.")
    print("Files are:")
    i = 0

    # + 2 bc of \
    csv_path_remove = len(csvPath + directory) + 2

    for csv_file in csv_files_in_folder:
        i += 1
        print(str(i) + ".", csv_file[csv_path_remove:] + "\n")

    df = pd.read_csv(csv_files_in_folder[0])
    print("Defined dataframe.")
    print("Included information from file:", csv_files_in_folder[0])
    print(df.head())

    for sh_csv in csv_files_in_folder[1:]: # skip the first one
        print(sh_csv)
        print("Included information from file:", sh_csv)
        df_new = pd.read_csv(sh_csv)
        df = df.append(df_new)

    email_domain_List = []

    for email_string in df["Recipient Email"]:
        domain = re.search("@[\w.]+", email_string).group()
        domain = domain.lower()
        # .group() converts from reMatch object to string
        email_domain_List.append(domain[1:])

    df["Email Domain"] = email_domain_List

    print(df.head())

    date_string = time.strftime("%d%b%y-%H%M%S")

    csvName = "SalesHandy appended_" + date_string
    df.to_csv(csvPath + "\\" + csvName + ".csv",
                      index = False)
    print("Saved combined file as:", csvPath + "\\" + csvName + ".csv")

    return csvName

if __name__ == "__main__":
   # stuff only to run when not called via 'import' here
    print('Make sure the directory with only SalesHandy files is saved in the folder set under csvPath.')
    print("Make sure the SalesHandy directory is unzipped.")

    csvPath = r"REPLACE_WITH_DESIRED_FILEPATH"
    SalesHandy_appender(csvPath)
