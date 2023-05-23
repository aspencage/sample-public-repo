# SalesHandy seperator

'''
purpose:
after running the SalesHandy appender
    separates send and reply to new lines for viz

for time series visualization
    need to do this with the way time series is done in Google Data Studio

'''

import pandas as pd
import time

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

def SalesHandy_seperator(csvPath, salesHandy_appended_csv):
    df = pd.read_csv(csvPath + "\\" + salesHandy_appended_csv + ".csv")

    df["Email date general"] = df["Sent At"]
    df["Email type"] = "Send (Climate Cabinet)"

    reply_df = df[df["Replied At"] != "-"]

    reply_df["Email date general"] = df["Replied At"]
    reply_df["Email type"] = "Reply (Campaign)"

    datetime_string = time.strftime("%d%b%y_%H%M")

    df = df.append(reply_df)

    df = df.sort_index()

    print(df[["Recipient Name", "Email date general", "Email type"]].head(5))

    SH_separate_csv = "SalesHandy_seperated email types_" + datetime_string 
    df.to_csv(csvPath + "\\" + SH_separate_csv + ".csv",
              index = False)
    print(f"Successfully saved the combined SH dataframe as SalesHandy_seperated email types_{datetime_string}.csv")
    return SH_separate_csv

if __name__ == "__main__":
    print('Make sure you have downloaded the correct SalesHandy sheets and appended them using the SH appender code.')
    print('Make sure the path is set correctly.')
    print()

    csvPath = r"REPLACE_WITH_DESIRED_FILEPATH"

    salesHandy_appended_csv = input("What is the name of the appended SalesHandy CSV? (no ext) ")
    SalesHandy_seperator(csvPath, salesHandy_appended_csv)
