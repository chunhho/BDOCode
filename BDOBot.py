import discord
import os
import ocrspace
from dotenv import load_dotenv
from datetime import date
from discord.ext import commands
from ParseSheet import uploadAttendance


load_dotenv()
myTOKEN = os.getenv('TOKEN')
OCRKey = os.getenv('OCRKEY')

#myTOKEN = Discord Bot Token
#OCRKey = register API from https://ocr.space/
#500 calls/DAY limit
#File Size Limit 1MB

bot = commands.Bot(command_prefix='$')

def ImageToAttendance(url):
  myDict = dataProcessing(url)
  #for key, value in myDict.items():
  #  print(key, '->', value)
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


#################################################################################################
#
#           Bot Command Sections
#
#################################################################################################


@bot.event
async def on_ready():
  print('The Tomato Bisque is ready!')

@bot.command()
@commands.has_role('Officer')
async def setAtt(ctx, url):
  try:
      myData = ImageToAttendance(url)
      generateFile(myData)
      myResult = "\nTotal count from this screenshot is: **" + str(len(myData)) + "**."
      await ctx.send(str(myData) + myResult)
  except Exception as e:
      await ctx.send("Failed, try again. Exception: " + str(e))

@bot.command()
@commands.has_role('Officer')
async def setAttOn(ctx, date, url):
  try:
      myData = ImageToAttendance(url)
      generateFile(myData, date)
      myResult = "\nTotal count from this screenshot is: **" + str(len(myData)) + "**."
      await ctx.send(str(myData) + myResult)
  except Exception as e:
      await ctx.send("Failed, try again. Exception: " + str(e))

@bot.command()
@commands.has_role('Officer')
async def getYesAttOn(ctx, date):
  try:
      myData = filterData(date)
      myResult = "\nTotal count from this screenshot is: **" + str(len(myData)) + "**."
      await ctx.send(str(myData) + myResult)
  except Exception as e:
      await ctx.send("Failed, try again. Exception: " + str(e))

@bot.command()
@commands.has_role('Officer')
async def getNoAttOn(ctx, date):
  try:
      myData = filterData(date, 'No')
      myResult = "\nTotal count from this screenshot is: **" + str(len(myData)) + "**."
      await ctx.send(str(myData) + myResult)
  except Exception as e:
      await ctx.send("Failed, try again. Exception: " + str(e))

@bot.command()
@commands.has_role('Officer')
async def addYesFor(ctx, name, myDate=None):
  try:
    myDict = {name : 'Yes'}
    generateFile(myDict, myDate)
    if myDate is None:
      today = date.today()
      myDate = str(today.strftime("%m%d%y"))
    await ctx.send(name + " has been added for " + myDate + ".")

  except Exception as e:
      await ctx.send("Failed, try again. Exception: " + str(e))

@bot.command()
@commands.has_role('Officer')
async def updateSheet(ctx, date):
  try:
      myData = filterData(date)
      await ctx.send("Updating google sheet, one moment please...")
      uploadAttendance(myData, date)
      await ctx.send("update complete")
  except Exception as e:
      await ctx.send("Failed, try again. Exception: " + str(e))


bot.run(myTOKEN)

#Attendance = 'https://cdn.discordapp.com/attachments/411788991353061389/830276999066288188/unknown.png'
#S = ImageToAttendance(Attendance)
#generateFile(S)
# myUrl = input("Enter link: ")
# ImageToAttendance(myUrl)