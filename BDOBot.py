import discord
import OCRStuff
import asyncio
import time
import os
from dotenv import load_dotenv
from datetime import date
from discord.ext import commands
from AttendanceHelper import getMissingNames
from AttendanceHelper import processGearBotData
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
async def addYesFor(ctx, name, myDate=None):
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

  # Get list of Discord Users with the role Guild Member
  role = discord.utils.get(ctx.guild.roles,name="Guild Member")
  guildList = [member.display_name for member in role.members]

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
    await botChannel.send("Data received... Processing names.", delete_after=deleteTime)

  results = processGearBotData(gearBotData)

  await botChannel.send("There are " + str(len(results)) + " responders.", delete_after=deleteTime/3)

  missingNames = sorted(getMissingNames(guildList,results))
  # Extra Wookie Account
  # No Dutchy (cuz he isn't @Guild Member)
  # Missing 2 People from discord: IrregularSlayer/Luphorian
  # This makes role.members = Actual - 2.
  #await botChannel.send("There are **" + str(len(role.members) - len(missingNames)) + "** guild members that responded.", delete_after=deleteTime)
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
  embed.add_field(name="$getYesAttOn MMDDYY", value="(Ex. $getYesAttOn 042021)", inline=False)
  embed.add_field(name="$getNoAttOn MMDDYY", value="(Ex. $getNoAttOn 042021)", inline=False)
  embed.add_field(name="$getMon", value="N/A", inline=False)
  embed.add_field(name="$getWed", value="N/A", inline=False)
  embed.add_field(name="$getFri", value="N/A", inline=False)
  embed.add_field(name="$addYesFor FamilyName", value="(Ex. $addYesFor TomatoBisque)", inline=False)
  embed.add_field(name="$addYesFor FamilyName Date", value="(Ex. $addYesFor TomatoBisque 042021)", inline=False)
  embed.add_field(name="$updateSheet Date", value="(Ex. $updateSheet 042021)", inline=False)
  embed.add_field(name="$demolish FamilyName ", value="(Ex. $demolish TomatoBisque)", inline=False)
  embed.add_field(name="$demolish FamilyName Master ", value="(Ex. $demolish TomatoBisque True)", inline=False)
  embed.add_field(name="$getPlayerAtt FamilyName", value="(Ex. $getPlayerAtt TomatoBisque)", inline=False)
  embed.add_field(name="$getPlayerAtt FamilyName Count", value="(Ex. $getPlayerAtt TomatoBisque 3)", inline=False)
  await ctx.send(embed=embed,delete_after=deleteTime*3)
  await ctx.message.delete()

bot.run(myTOKEN)

#Attendance = 'https://cdn.discordapp.com/attachments/411788991353061389/830276999066288188/unknown.png'
#S = ImageToAttendance(Attendance)
#generateFile(S)
# myUrl = input("Enter link: ")
# ImageToAttendance(myUrl)


