import discord
import OCRStuff
import asyncio
import time
import os
from dotenv import load_dotenv
from datetime import date
from discord.ext import commands
from AttendanceHelper import trimList
from AttendanceHelper import processGearBotData
from AttendanceHelper import findDiscordName
from ParseSheet import uploadAttendance
from ParseSheet import deleteUser
from ParseSheet import getPlayerAttPerc
from ParseSheet import uploadTwoWeekAtt

load_dotenv()
myTOKEN = os.getenv('TOKEN')
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='$', case_insensitive=True, intents = intents)
bot.remove_command("help")
deleteTime = 60.0

#myTOKEN = Discord Bot Token
#OCRKey = register API from https://ocr.space/
#500 calls/DAY limit
#File Size Limit 1MB

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
    myData = OCRStuff.ImageToAttendance(url)
    OCRStuff.generateFile(myData)
    myResult = "\nTotal count from this screenshot is: **" + str(len(myData)) + "**."
    await ctx.send(str(myData) + myResult, delete_after=deleteTime)

  except Exception as e:
    await ctx.send("Failed, try again. Exception: " + str(e), delete_after=deleteTime)

  finally:
    await asyncio.sleep(3.0)
    await ctx.message.delete()

@bot.command()
@commands.has_role('Officer')
async def setAttOn(ctx, date, url):
  try:
    myData = OCRStuff.ImageToAttendance(url)
    OCRStuff.generateFile(myData, date)
    myResult = "\nTotal count from this screenshot is: **" + str(len(myData)) + "**."
    await ctx.send(str(myData) + myResult, delete_after=deleteTime)

  except Exception as e:
    await ctx.send("Failed, try again. Exception: " + str(e), delete_after=deleteTime)

  finally:
    await asyncio.sleep(3.0)
    await ctx.message.delete()

@bot.command()
@commands.has_role('Officer')
async def getYesOn(ctx, date):
  try:
    myData = OCRStuff.filterData(date)
    myResult = "\nTotal count from this screenshot is: **" + str(len(myData)) + "**."
    await ctx.send(str(myData) + myResult)

  except Exception as e:
    await ctx.send("Failed, try again. Exception: " + str(e))

  finally:
    await asyncio.sleep(3.0)

@bot.command()
@commands.has_role('Officer')
async def getNoOn(ctx, date):
  try:
    myData = OCRStuff.filterData(date, 'No')
    myResult = "\nTotal count from this screenshot is: **" + str(len(myData)) + "**."
    await ctx.send(str(myData) + myResult, delete_after=deleteTime)

  except Exception as e:
    await ctx.send("Failed, try again. Exception: " + str(e), delete_after=deleteTime)

  finally:
    await asyncio.sleep(3.0)
    await ctx.message.delete()

@bot.command()
@commands.has_role('Officer')
async def setYesFor(ctx, name, myDate=None):
  try:
    myDict = {name : 'Yes'}
    OCRStuff.generateFile(myDict, myDate)
    if myDate is None:
      today = date.today()
      myDate = str(today.strftime("%m%d%y"))
    myStr = name + " has been added for " + myDate + "."
    await ctx.send(myStr, delete_after=deleteTime)

  except Exception as e:
    await ctx.send("Failed, try again. Exception: " + str(e), delete_after=deleteTime)

  finally:
    await asyncio.sleep(3.0)
    await ctx.message.delete()

@bot.command()
@commands.has_role('Officer')
async def setYesListForDate(ctx, myDate, *names):
  myDict = {}
  myStr = "" 
  try:
    for name in names:
      myDict[name] = "Yes"
      myStr += name + " "
    OCRStuff.generateFile(myDict, myDate)
    myStr += "have been added for " + myDate + "."
    await ctx.send(myStr, delete_after=deleteTime)

  except Exception as e:
    await ctx.send("Failed, try again. Exception: " + str(e), delete_after=deleteTime)

  finally:
    await asyncio.sleep(3.0)
    await ctx.message.delete()

@bot.command()
@commands.has_role('Officer')
async def updateSheet(ctx, date):
  try:
    myData = OCRStuff.filterData(date)
    await ctx.send("Updating google sheet, one moment please...", delete_after=deleteTime)
    addToMasterNames = uploadAttendance(myData, date)
    await ctx.send("Update complete. Google Sheet Updated.")
    if len(addToMasterNames) > 0:
      await ctx.send("ATTENTION NEED TO ADD THESE MEMBERS TO THE MASTER LIST")
      for name in addToMasterNames:
        await ctx.send(name)

  except Exception as e:
    await ctx.send("Failed, try again. Exception: " + str(e), delete_after=deleteTime)

  finally:
    await asyncio.sleep(3.0)
    await ctx.message.delete()

@bot.command()
@commands.has_role('Officer')
async def demolish(ctx, familyName):
  await ctx.send(deleteUser(familyName))
  await asyncio.sleep(3.0)
  await ctx.message.delete()

@bot.command()
@commands.has_role('Officer')
async def getPlayerAtt(ctx, familyName, window='All'):
  await ctx.send(getPlayerAttPerc(familyName, window), delete_after=deleteTime)
  await asyncio.sleep(3.0)
  await ctx.message.delete()

@bot.command()
@commands.has_role('Officer')
async def updateGuildFile(ctx):
  role = discord.utils.get(ctx.guild.roles,name="Guild Member")
  with open('Guildies.txt', 'w', encoding="utf-8") as mainFile:
    for member in role.members:
      mainFile.write(member.display_name + "\n")
    mainFile.close()

  await ctx.send("Guild List File updated.", delete_after=deleteTime)
  await asyncio.sleep(3.0)
  await ctx.message.delete()

@bot.command()
@commands.has_role('Officer')
async def getRole(ctx, roleName):
  role = discord.utils.get(ctx.guild.roles,name=roleName)
  roleList = [member.display_name for member in role.members]
  return roleList

@bot.command()
@commands.has_role('Officer')
async def getVacation(ctx):
  #ignoreRole = discord.utils.get(ctx.guild.roles,name="Vacation")
  ignoreList = await getRole(ctx, "Vacation")
  myStr = "```\nDead, I mean on Vacation People:\n"
  myStr += ", ".join([str(name) for name in ignoreList])
  myStr += "\nDead, I mean on Vacation Count: " + str(len(ignoreList)) + "```"
  await ctx.send(myStr, delete_after=deleteTime)
  await asyncio.sleep(3.0)
  await ctx.message.delete()

@bot.command()
@commands.has_role('Officer')
async def clearRole(ctx, roleName):
  theRole = discord.utils.get(ctx.guild.roles,name=roleName)
  guildList = await getRole(ctx, roleName)
  roleList = []
  for member in theRole.members:
    await member.remove_roles(theRole)
    roleList.append(member.display_name)
  roleList.sort()
  myStr = "```\nRemoved the following list of people with the role " + roleName + ":\n"
  myStr += ", ".join([str(name) for name in roleList])
  myStr += "\nCount: " + str(len(roleList)) + "```"
  await ctx.send(myStr, delete_after=deleteTime)
  await asyncio.sleep(3.0)

@bot.command()
@commands.has_role('Officer')
async def getMissingCanute(ctx):
  myMemList = await getRole(ctx, "Guild Member")
  mainFile = open('FamilyNamesWebsite.txt', 'r', encoding="utf-8")
  guildFile = open('canuteNames.txt', 'r', encoding="utf-8")
  guildList = mainFile.readlines()
  canuteList = guildFile.readlines()
  guildFile.close()
  mainFile.close()

  myDict, myFam, myDis = findDiscordName(guildList, myMemList)

  # Result A = List of Family names(with relevant Discord Name) missing from Canute
  resultA = trimList(list(myDict.keys()), canuteList)

  # Result B = List of Family names(without relevant Discord Name) missing from Canute
  resultB = trimList(myFam, canuteList)

  resultADict = {}

  for famNames in resultA:
    resultADict[famNames] = myDict[famNames] 
  
  sorted(resultADict)
  sorted(resultB)

  myStr = "```\nMissing Canute Names for findable Discord Names:\n"
  myStr += "\n".join(['FN:{0} DN:{1}'.format(k, v) for k,v in resultADict.items()])
  myStr += "\nMissing Count: " + str(len(resultADict)) + "```"

  await ctx.send(myStr)

  myStr = "```\nMissing Canute Names for not findable/difficult Discord Names:\n"
  myStr += "".join([str(name) for name in resultB])
  myStr += "\nMissing Count: " + str(len(resultB)) + "```"
  await ctx.send(myStr)


@bot.command()
@commands.has_role('Officer')
async def setDeadBeat(ctx):
  myMemList = await getRole(ctx, "Guild Member")
  famNamesFile = open('FamilyNamesWebsite.txt', 'r', encoding="utf-8")
  guildList = famNamesFile.readlines()

  canuteFile = open('canuteNames.txt', 'r', encoding="utf-8")
  canuteList = canuteFile.readlines()

  famNamesFile.close()
  canuteFile.close()

  myDict, myFam, myDis = findDiscordName(guildList, myMemList)

  # Result A = List of Family names(with relevant Discord Name) missing from Canute
  resultA = trimList(list(myDict.keys()), canuteList)
  resultADict = {}
  # Result B = List of Family names(without relevant Discord Name) missing from Canute
  resultB = trimList(myFam, canuteList)
  sorted(resultB)

  for famNames in resultA:
    resultADict[famNames] = myDict[famNames] 
  sorted(resultADict)

  guildMem = discord.utils.get(ctx.guild.roles,name="Guild Member")
  deadBeatMembers = discord.utils.get(ctx.guild.roles, name="NonResponder")
  vacationRole = discord.utils.get(ctx.guild.roles,name="Vacation")

  listOfDeadBeats = []

  for person in guildMem.members:
    for name in resultADict.values():
      if person.display_name == name and vacationRole not in person.roles:
        await person.add_roles(deadBeatMembers)
        listOfDeadBeats.append(person.display_name)
  sorted(listOfDeadBeats)
  
  myStr = "```\nGuild Members that can't XXXXing type a bot command:\n"
  #myStr += "\n".join(['FN:{0} DN:{1}'.format(k, v) for k,v in resultADict.items()])
  myStr += "\n".join([name for name in listOfDeadBeats])
  myStr += "\nCount: " + str(len(listOfDeadBeats)) + "```"
  await ctx.send(myStr)

  myStr = "```\nMissing Canute Names for not findable/difficult Discord Names:\n"
  myStr += "".join([str(name) for name in resultB])
  myStr += "\nCount: " + str(len(resultB)) + "```"
  await ctx.send(myStr)

@bot.command()
@commands.has_role('Officer')
async def resetDeadBeat(ctx):
  await clearRole(ctx, "NonResponder")
  await setDeadBeat(ctx)

@bot.command()
@commands.has_role('Officer')
async def listDeadBeat(ctx):
  guildList = await getRole(ctx, "NonResponder")
  guildList.sort()
  myStr = "```\nGuild Members that can't XXXXing type a bot command:\n"
  #myStr += "\n".join(['FN:{0} DN:{1}'.format(k, v) for k,v in resultADict.items()])
  myStr += "\n".join([name for name in guildList])
  myStr += "\nCount: " + str(len(guildList)) + "```"
  await ctx.send(myStr)

@bot.command
@commands.is_owner()
async def spamPeople(ctx):
  myMemList = await getRole(ctx, "Guild Member")
  mainFile = open('FamilyNamesWebsite.txt', 'r', encoding="utf-8")
  guildFile = open('canuteNames.txt', 'r', encoding="utf-8")
  guildList = mainFile.readlines()
  canuteList = guildFile.readlines()
  guildFile.close()
  mainFile.close()

  myDict, myFam, myDis = findDiscordName(guildList, myMemList)

  # Result A = List of Family names(with relevant Discord Name) missing from Canute
  resultA = trimList(list(myDict.keys()), canuteList)
  resultADict = {}

  for famNames in resultA:
    resultADict[famNames] = myDict[famNames] 
  sorted(resultADict)

  guildMem = discord.utils.get(ctx.guild.roles,name="Guild Member")
  attChn = discord.utils.get(ctx.guild.channels, name="canute-gear")
  spamChn = discord.utils.get(ctx.guild.channels, name="majorbotspam")

  for person in guildMem.members:
    for name in resultADict.values():
      if person.display_name == name:
        await spamChn.send(f"User {person.mention} is required to update your info in {attChn.mention}.")

@bot.command()
@commands.is_owner()
async def shutdown(ctx):
  await asyncio.sleep(3.0)
  await ctx.message.delete()
  await ctx.send("We're closing. The Tomato Bisque is sold out for the night!", delete_after=2.0)
  await asyncio.sleep(5)
  await ctx.bot.logout()

@bot.command()
async def help(ctx):
  embed=discord.Embed(title="Bisque Bot Help", description="List of commands for all your needs!")
  embed.add_field(name="$setAtt Url", value="(Ex. $setAtt http://picture4Attendance.com)", inline=False)
  embed.add_field(name="$setAttOn Date Url", value="(Ex. $setAttOn 042021 http://picture4Attendance.com)", inline=False)
  embed.add_field(name="$setYesFor FamilyName", value="(Ex. $setYesFor TomatoBisque)", inline=False)
  embed.add_field(name="$setYesFor FamilyName Date", value="(Ex. $setYesFor TomatoBisque 042021)", inline=False)
  embed.add_field(name="$setYesListForDate Date Name1 Name2 Name3 ...", value="(Ex. $setYesListForDate 010101 Alpha Beta Charlie Delta)", inline=False)
  embed.add_field(name="$updateSheet Date", value="(Ex. $updateSheet 042021)", inline=False)
  embed.add_field(name="$getYesOn MMDDYY", value="(Ex. $getYesOn 042021)", inline=False)
  embed.add_field(name="$getNoOn MMDDYY", value="(Ex. $getNoOn 042021)", inline=False)
  embed.add_field(name="$getPlayerAtt FamilyName", value="(Ex. $getPlayerAtt TomatoBisque)", inline=False)
  embed.add_field(name="$getPlayerAtt FamilyName Count", value="(Ex. $getPlayerAtt TomatoBisque 3)", inline=False)
  embed.add_field(name="$getVacation", value="Returns list of People with Vacation Role", inline=False)
  embed.add_field(name="$demolish FamilyName ", value="(Ex. $demolish TomatoBisque)", inline=False)
  embed.add_field(name="$uploadTwoWeekAttendance ", value="Updates the Member List Attendance % for the previous 2 weeks", inline=False)
  await ctx.send(embed=embed,delete_after=deleteTime*3)
  await ctx.message.delete()

@bot.command()
@commands.has_role('Officer')
async def uploadTwoWeekAttendance(ctx):
  await ctx.send("Updating all players 2 week attendance, this will take a few moments...")
  uploadTwoWeekAtt()
  await ctx.send("List update complete!")

bot.run(myTOKEN)

#Attendance = 'https://cdn.discordapp.com/attachments/411788991353061389/830276999066288188/unknown.png'
#S = ImageToAttendance(Attendance)
#generateFile(S)
# myUrl = input("Enter link: ")
# ImageToAttendance(myUrl)

