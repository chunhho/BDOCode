import os
import ocrspace
from dotenv import load_dotenv
from datetime import date
from datetime import datetime

load_dotenv()
OCRKey = os.getenv('OCRKEY')

def ImageToAttendance(url):
  myDict = dataProcessing(url)
  #for key, value in myDict.items():
  #  print(key, '->', value)
  return myDict

def nameFixer(myData):
  # InvalidNames : CorrectNames
  failedFamilyNames = {"Donltalia" : "DonItalia",
                       "Shioweeb"  : "ShioWeeb",
                       "Pottl" : "Pott1"}
  for key, value in failedFamilyNames.items():
    if key in myData:
      myData[value] = myData.pop(key)
  return myData

def generateFile(myData, myDate=None):

  if myDate is None:
    today = date.today()
    myFile = "NW" + str(today.strftime("%m%d%y")) + ".txt"
  else:
    myFile = "NW" + str(myDate) + ".txt"

  overallList = {}
  sortedOverall = {}

  if os.path.exists(myFile):
    with open(myFile, 'r') as mainFile:
      for line in mainFile:
        (key, val) = line.split()
        overallList[key] = val

    overallList.update(myData)
    mainFile.close()
    os.remove(myFile)

  else:
    overallList = myData

  for i in sorted(overallList.keys()):
    sortedOverall[i] = overallList[i]

  with open(myFile, 'w') as mainFile:
    for i in sortedOverall.keys():
      mainFile.write(str(i + " " + sortedOverall[i] + "\n"))
  mainFile.close()

def dataProcessing(url):
  ocrStuff = ocrspace.API(OCRKey, ocrspace.Language.English)
  rawData = ocrStuff.ocr_url(url).split('\r\n')
  FamilyNameIndex = [i for i, s in enumerate(rawData) if 'Family (C' in s][0]
  ActivityIndex = [i for i, s in enumerate(rawData) if 'Activity (?' in s][0]
  ParticipateIndex = [i for i, s in enumerate(rawData) if 'Participate' in s][0]

  myFamily = rawData[FamilyNameIndex + 1:ActivityIndex]
  myFamilyNamesOnly = []

  for i in myFamily:
    myStr = i.split('(')[0].replace("(","")
    myStr = myStr.rstrip()
    myFamilyNamesOnly.append(myStr.replace(" ","_"))

    myParticipation = rawData[ParticipateIndex + 1:-1]
  
  result = dict(zip(myFamilyNamesOnly, myParticipation))
  result = nameFixer(result)
  return result

def filterData(myDate, option='Yes', myData=None):
  myDict = {}
  if myData is None:
    myFile = "NW" + str(myDate) + '.txt'
    if os.path.exists(myFile):
      with open(myFile, 'r') as mainFile:
        for line in mainFile:
          (key, val) = line.split()
          if val == option:
            myDict[key] = val
      mainFile.close()
    else:
      raise Exception("File does not exist.")

  else:
    for a in myData.keys():
      if myData[a] == option:
        myDict[a] = myData[a]

  return myDict