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

load_dotenv()
myTOKEN = os.getenv('TOKEN')
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='$', intents = intents)
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
async def getYesAttOn(ctx, date):
  try:
    myData = OCRStuff.filterData(date)
    myResult = "\nTotal count from this screenshot is: **" + str(len(myData)) + "**."
    await ctx.send(str(myData) + myResult, delete_after=deleteTime)

  except Exception as e:
    await ctx.send("Failed, try again. Exception: " + str(e), delete_after=deleteTime)

  finally:
    await asyncio.sleep(3.0)
    await ctx.message.delete()

@bot.command()
@commands.has_role('Officer')
async def getNoAttOn(ctx, date):
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
async def demolish(ctx, familyName, master=False):
  await ctx.send(deleteUser(familyName, master), delete_after=deleteTime)
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
async def getMissing(ctx, channel):

  # Process: Call getGearBotMsgFriday in #attendance-bot
  # Bisque Bot sends message (!list) to #attendance-friday
  # Gear Bot replies with guildies' info
  # Bisque Bot captures replies
  # Bisque Bot sends message (!list not attending)
  # Gear Bot replies with guildies' info
  # Bisque Bot captures replies
  # Bisque Bot process and post results

  # Set #Attendance-[Day] to attChn
  attChn = discord.utils.get(ctx.guild.channels, name=channel)
  # Set #attendance-bot to botChannel
  botChannel = discord.utils.get(ctx.guild.channels, name="attendance-bot")

  # Get list of Discord Users with the role Guild Member/Leader
  guildList = await getRole(ctx, "Guild Member")
  guildList += await getRole(ctx, "Guild Leader")

  # Remove duplicates Users
  guildList = list(set(guildList))

  # Missing 2 People from discord: IrregularSlayer/Luphorian
  guildSize = len(guildList)

  # Add people that may come back? :kekW:
  # Some of these people should just be kicked tbh.
  ignoreList = await getRole(ctx, "Vacation")
  guildList = sorted(trimList(guildList,ignoreList))

  await botChannel.send("Attempting to get " + channel + "'s attendance.", delete_after=deleteTime/3)

  # Retrieve Sign-ups from the #Attendance-[Day]
  await attChn.send("!list")
  await asyncio.sleep(3.0)
  await attChn.send("!list not attending")

  # Wait for 5 seconds for the messages to load
  await asyncio.sleep(5.0)

  gearBotData = []
  
  # Get the last 8 messages
  botMsgs = await attChn.history(limit=8).flatten()
  for msg in botMsgs:
    for embeddedmsg in msg.embeds:
      [gearBotData.append(x) for x in embeddedmsg.to_dict()['description'].splitlines() if x not in gearBotData]

  if len(gearBotData) > 0: 
    await botChannel.send("Data received... Processing names.", delete_after=deleteTime/3)

  # Get Family Names from the !list and !list not attending
  results = processGearBotData(gearBotData)
  resultMsg = "There are **" + str(len(results)) + "** responders and **" + str(len(ignoreList)) + "** vacation members."
  await botChannel.send(resultMsg, delete_after=deleteTime/3)

  missingNames = sorted(trimList(guildList,results))

  myStr = "```\nMissing People for " + channel + ":\n"
  myStr += ", ".join([str(name) for name in missingNames])
  myStr += "\nMissing Total Count: " + str(len(missingNames)) + "```"

  await botChannel.send(myStr, delete_after=deleteTime)

@bot.command()
@commands.has_role('Officer')
async def getMon(ctx):
  await getMissing(ctx, "attendance-monday")
  await asyncio.sleep(3.0)
  await ctx.message.delete()

@bot.command()
@commands.has_role('Officer')
async def getWed(ctx):
  await getMissing(ctx, "attendance-wednesday")
  await asyncio.sleep(3.0)
  await ctx.message.delete()

@bot.command()
@commands.has_role('Officer')
async def getFri(ctx):
  await getMissing(ctx, "attendance-friday")  
  await asyncio.sleep(3.0)
  await ctx.message.delete()

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
async def getAttending(ctx, channel):

  guildMem = discord.utils.get(ctx.guild.roles,name="Guild Member")
  guildLeader = discord.utils.get(ctx.guild.roles,name="Guild Leader")
  guildList = [member for member in guildMem.members]
  guildList += [member for member in guildLeader.members]
  guildList = list(set(guildList))

  #Get List of People that Yes up
  attChn = discord.utils.get(ctx.guild.channels, name=channel)
  await attChn.send("!list")
  botMsgs = await attChn.history(limit=4).flatten()

  gearBotData = []
  for msg in botMsgs:
    for embeddedmsg in msg.embeds:
      [gearBotData.append(x) for x in embeddedmsg.to_dict()['description'].splitlines() if x not in gearBotData]

  famNames = processGearBotData(gearBotData)

  attending = discord.utils.get(ctx.guild.roles, name="Attending")
  attendingList = []
  # Not sure how to deal with bullshit same names for now
  for name in famNames:
    for member in guildList:
      if name in member.display_name:
        await member.add_roles(attending)
        attendingList.append(member.display_name)
  return attendingList

@bot.command()
@commands.has_role('Officer')
async def setMon(ctx):
  roleList = await getAttending(ctx, "attendance-monday")
  roleList.sort()
  myStr = "```\nAdded the following list of people with the role Attending:\n"
  myStr += ", ".join([str(name) for name in roleList])
  myStr += "\nAttending Count: " + str(len(roleList)) + "```"
  await ctx.send(myStr, delete_after=deleteTime)
  await asyncio.sleep(3.0)
  await ctx.message.delete()

@bot.command()
@commands.has_role('Officer')
async def setWed(ctx):
  roleList = await getAttending(ctx, "attendance-wednesday")
  roleList.sort()
  myStr = "```\nAdded the following list of people with the role Attending:\n"
  myStr += ", ".join([str(name) for name in roleList])
  myStr += "\nAttending Count: " + str(len(roleList)) + "```"
  await ctx.send(myStr, delete_after=deleteTime)
  await asyncio.sleep(3.0)
  await ctx.message.delete()


@bot.command()
@commands.has_role('Officer')
async def setFri(ctx):
  roleList = await getAttending(ctx, "attendance-friday")
  roleList.sort()
  myStr = "```\nAdded the following list of people with the role Attending:\n"
  myStr += ", ".join([str(name) for name in roleList])
  myStr += "\nAttending Count: " + str(len(roleList)) + "```"
  await ctx.send(myStr, delete_after=deleteTime)
  await asyncio.sleep(3.0)
  await ctx.message.delete()

@bot.command()
@commands.has_role('Officer')
async def clearAtt(ctx):
  attendingRole = discord.utils.get(ctx.guild.roles,name="Attending")
  guildList = await getRole(ctx, "Attending")
  roleList = []
  for member in attendingRole.members:
    await member.remove_roles(attendingRole)
    roleList.append(member.display_name)
  roleList.sort()
  myStr = "```\nRemoved the following list of people with the role Attending:\n"
  myStr += ", ".join([str(name) for name in roleList])
  myStr += "\nAttending Count: " + str(len(roleList)) + "```"
  await ctx.send(myStr, delete_after=deleteTime)
  await asyncio.sleep(3.0)
  await ctx.message.delete()

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

  guildList = [member for member in guildMem.members]
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
  embed.add_field(name="$updateSheet Date", value="(Ex. $updateSheet 042021)", inline=False)
  embed.add_field(name="$getYesAttOn MMDDYY", value="(Ex. $getYesAttOn 042021)", inline=False)
  embed.add_field(name="$getNoAttOn MMDDYY", value="(Ex. $getNoAttOn 042021)", inline=False)
  embed.add_field(name="$getPlayerAtt FamilyName", value="(Ex. $getPlayerAtt TomatoBisque)", inline=False)
  embed.add_field(name="$getPlayerAtt FamilyName Count", value="(Ex. $getPlayerAtt TomatoBisque 3)", inline=False)
  embed.add_field(name="$setMon", value="Add attending role for Monday's attendees", inline=False)
  embed.add_field(name="$setWed", value="Add attending role for Wednesday's attendees", inline=False)
  embed.add_field(name="$setFri", value="Add attending role for Friday's attendees", inline=False)
  embed.add_field(name="$clearAtt", value="Remove attending role from everyone who has it", inline=False)
  embed.add_field(name="$getMon", value="Returns list of Missing People for Monday", inline=False)
  embed.add_field(name="$getWed", value="Returns list of Missing People for Wednesday", inline=False)
  embed.add_field(name="$getFri", value="Returns list of Missing People for Friday", inline=False)
  embed.add_field(name="$getVacation", value="Returns list of People with Vacation Role", inline=False)
  embed.add_field(name="$demolish FamilyName ", value="(Ex. $demolish TomatoBisque)", inline=False)
  embed.add_field(name="$demolish FamilyName Master ", value="(Ex. $demolish TomatoBisque True)", inline=False)
  await ctx.send(embed=embed,delete_after=deleteTime*3)
  await ctx.message.delete()

bot.run(myTOKEN)

#Attendance = 'https://cdn.discordapp.com/attachments/411788991353061389/830276999066288188/unknown.png'
#S = ImageToAttendance(Attendance)
#generateFile(S)
# myUrl = input("Enter link: ")
# ImageToAttendance(myUrl)


