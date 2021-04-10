import discord
import os
import ocrspace
from dotenv import load_dotenv
from datetime import date


load_dotenv()
myTOKEN = os.getenv('TOKEN')
OCRKey = os.getenv('OCRKEY')

#myTOKEN = Discord Bot Token
#OCRKey = register API from https://ocr.space/
#500 calls/DAY limit
#File Size Limit 1MB

client = discord.Client()

def ImageToAttendance(url):
  myDict = dataProcessing(url)
  for key, value in myDict.items():
    print(key, '->', value)
  return myDict

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
  print(ParticipateIndex)

  myFamily = rawData[FamilyNameIndex + 1:ActivityIndex]
  myFamilyNamesOnly = []

  for i in myFamily:
    myStr = i.split('(')[0].replace("(","")
    myStr = myStr.rstrip()
    myFamilyNamesOnly.append(myStr.replace(" ","_"))

    myParticipation = rawData[ParticipateIndex + 1:-1]
  
    result = dict(zip(myFamilyNamesOnly, myParticipation))

  return result

def filterData(myDate, option='Yes', myData=None):
  myDict = {}
  if myData is None:
    myFile = "NW" + str(myDate) + '.txt'
    with open(myFile, 'r') as mainFile:
      for line in mainFile:
        (key, val) = line.split()
        if val == option:
          myDict[key] = val
    mainFile.close()

  else:
    for a in myData.keys():
      if myData[a] == option:
        myDict[a] = myData[a]

  return myDict


@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
  if message.author == client.user:
    return

  if message.content.startswith('Attendance:'):
    try:
      myData = ImageToAttendance(message.content[11:])
      generateFile(myData)
      myResult = "\nTotal count from this screenshot is: **" + str(len(myData)) + "**."
      await message.channel.send(str(myData) + myResult)
    except Exception as e:
      await message.channel.send("Failed, try again.")
      await message.channel.send(e)

  if message.content.startswith('AttendanceOn:'):
    try:
      myData = ImageToAttendance(message.content[19:])
      generateFile(myData, message.content[13:19])
      myResult = "\nTotal count from this screenshot is: **" + str(len(myData)) + "**."
      await message.channel.send(str(myData) + myResult)
    except Exception as e:
      await message.channel.send("Failed, try again.")
      await message.channel.send(e)

  if message.content.startswith('getYesAttOn:'):
    try:
      myDate = str(message.content[12:18])
      myData = filterData(myDate)
      myResult = "\nTotal count from this screenshot is: **" + str(len(myData)) + "**."
      await message.channel.send(str(myData) + myResult)
    except Exception as e:
      await message.channel.send("Failed, try again.")
      await message.channel.send(e)

  if message.content.startswith('getNoAttOn:'):
    try:
      myDate = str(message.content[11:17])
      myData = filterData(myDate, 'No')
      myResult = "\nTotal count from this screenshot is: **" + str(len(myData)) + "**."
      await message.channel.send(str(myData) + myResult)
    except Exception as e:
      await message.channel.send("Failed, try again.")
      await message.channel.send(e)


  # if message.content.startswith('Warscore:'):
  #   myURL = message.content[9:].strip()
  #   await message.channel.send(ocr_core(myURL))

client.run(myTOKEN)
#Attendance = 'https://cdn.discordapp.com/attachments/411788991353061389/830278096049537024/unknown.png'
#S = ImageToAttendance(Attendance)
#generateFile(S)
# myUrl = input("Enter link: ")
# ImageToAttendance(myUrl)