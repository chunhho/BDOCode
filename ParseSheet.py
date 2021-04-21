import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time
from random import choice
from datetime import datetime

"""
Link to YT guide for Setup: https://www.youtube.com/watch?v=cnPlKLEGR7E&ab_channel=TechWithTim
"""

#Setup
scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("bghcreds.json", scope) #Name of your creds.json file goes here
client = gspread.authorize(creds)

#Access sheet
sheet = client.open("BGH Members List").worksheet("Attendance")
masterSheet = client.open("BGH Members List").sheet1

def findColIdx(date):
    """
    Helper function to find the index of the column by date or the next blank column
    :return: index of the column to written in
    """
    idx = 2
    while(sheet.cell(1, idx).value is not None):
        if(sheet.cell(1, idx).value == date):
            break
        idx += 1
    return idx

def generateLists(attended):
    """
    Helper function to populate lists required to run UploadAttendance
    :param attended: A dictionary of {Family Names : 'Yes'} for attending guild members
    :return: attendedNames: List of attended.keys()
             allNames: List of unique sorted names from attendedNames + sheetNames
             newMember: List of new members to be added to the google sheet, attendedNames - sheetNames
    """
    attendedNames = list(attended.keys())
    sheetNames = sheet.col_values(1)
    allNames = sheetNames + attendedNames
    allNames.pop(0)
    allNames = list(set(allNames))
    allNames.sort()
    newMember = [player for player in attendedNames if player not in sheetNames]
    return attendedNames, allNames, newMember

def uploadAttendance(attended, date):
    """
    Main function that uploads the guild attendance to the google sheet
    :param attended: A dictionary of {Family Names : 'Yes'} for attending guild members
    :param date: The date of the nodewar, used as a column header on the google sheet
    """
    myDate = datetime.strptime(date, "%m%d%y").date()
    myDate = str(myDate.strftime("%m/%d/%y"))
    #Find next blank row
    colIdx = findColIdx(myDate)
    sheet.update_cell(1, colIdx, myDate)
    #Populate required lists
    attendedNames, allNames, newMember = generateLists(attended)
    #Create a set of column values for new sheet members
    exemptBuffer = ['Exempt' for i in range(colIdx - 2)]
    exemptBuffer.append('Yes')
    #Set attendance for members
    rowIdx = 2
    for name in allNames:
        if name in newMember:
            newRow = [name] + exemptBuffer
            sheet.insert_row(newRow, rowIdx)
        elif name in attendedNames:
            sheet.update_cell(rowIdx, colIdx, 'Yes')
            attendedNames.pop(attendedNames.index(name))
        else:
            sheet.update_cell(rowIdx, colIdx, 'No')
        rowIdx += 1
        #This is here because of the google drive r/w quota
        if rowIdx % 20 == 0:
            print("Hit pause...")
            time.sleep(75)
    return newMember

def deleteUser(user, master=False):
    try:
        cell = sheet.find(user)
        sheet.delete_row(cell.row)

        if master:
            mastercell = masterSheet.find(user)
            masterSheet.delete_row(mastercell.row)

        return successQuips(user)

    except Exception as e:
        return failedQuips(str(e))


def successQuips(user):
    quips = ['Success! FamilyName: **' + user + '** has been banished into infernal bisque land.',
             'Success! Another one bites the dust~ FamilyName: **' + user + '** is removed.',
             'Success! <:gunpepe:408180927123030016> **' + user + '** has been removed!',
             'Success! FamilyName: **' + user + '** is gone. <a:PepeDance:587420384689782784> https://cdn.discordapp.com/attachments/554157458537447447/831392727412768818/unknown.png']
    return choice(quips)

def failedQuips(user):
    quips = ['Failed... FamilyName: **' + user + '** did not get banished to the infernal bisque land. Probably never existed in the first place!',
             'Failed... FamilyName: **' + user + '** is not found in the BGH archive.',
             'Failed... <:feelsweirdestman:719298173083844658> FamilyName: **' + user + '** is not real.']
    return choice(quips)

def getPlayerAttPerc(name, window):
    try:
        att_list = sheet.row_values(sheet.find(name).row)
        if window == 'All':
            return getPercent(att_list)
        else:
            window = int(window)
            return getPercent(att_list[-window:])
    except Exception as e:
        return ("You either attempted to search an invalid name or didnt enter 'All' or a integer value! " + str(e))


def getPercent(att_list):
    return (att_list.count('Yes') / (att_list.count('Yes') + att_list.count('No'))) * 100