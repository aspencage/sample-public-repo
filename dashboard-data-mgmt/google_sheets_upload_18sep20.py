# google sheets upload code

import pickle
from googleapiclient.discovery import build

credentialsPath = r"REPLACE_WITH_PATH_TO_GOOGLE_SHEETS_CREDENTIALS"
credentialsFile = credentialsPath + '\\' + 'token.pickle'

def push_csv_to_gsheet(importPath, importCsv, spreadsheet_id):
    with open(importPath + "\\" + importCsv + ".csv", 'r', encoding = "utf-8") as csv_file:
        csvContents = csv_file.read()
        type(csvContents)
    body = {
        'requests': [{
            'pasteData' : {
                "data": csvContents,
                "type": 'PASTE_NORMAL',
                "delimiter": ',',
                }
            }]
    }
    request = API.spreadsheets().batchUpdate(spreadsheetId = spreadsheet_id, body=body)
    response = request.execute()
    return response

def g_cred(credentialsFile):
    with open(credentialsFile, 'rb') as token:
        credentials = pickle.load(token)

    API = build('sheets', 'v4', credentials = credentials)
    return API

def push_multi_csvs_to_gsheet(importPath, importCsv_spreadsheet_dict):
    # create lists with importCsv_List and spread_id_List
    for (spreadsheet_id, importCsv) in importCsv_spreadsheet_dict.items(): 
        push_csv_to_gsheet(
        importPath,
        importCsv,
        spreadsheet_id
        )
        print(f"Successfully uploaded {importCsv} to {spreadsheet_id}.")

API = g_cred(credentialsFile)

if __name__ == "__main__":
    spreadsheet_id = input("What is the ID of the spreadsheet you want to update? (get this from URL) ") 

    importPath = input("What is the CSV path to the file you want to update from? ")
    importCsv = input("What is the CSV file you want to update from? (no extension) ")

    push_csv_to_gsheet(
        importPath,
        importCsv,
        spreadsheet_id
    )
