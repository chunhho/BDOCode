import discord
import OCRStuff
import asyncio
import os
from dotenv import load_dotenv
from datetime import date
from discord.ext import commands
from AttendanceHelper import getMissingNames
from ParseSheet import uploadAttendance
from ParseSheet import deleteUser
from ParseSheet import getPlayerAttPerc

load_dotenv()
myTOKEN = os.getenv('TOKEN')
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='$', intents = intents)
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
      await ctx.message.delete()

@bot.command()
@commands.has_role('Officer')
async def demolish(ctx, familyName, master=False):
  await ctx.message.delete()
  await ctx.send(deleteUser(familyName, master), delete_after=deleteTime)

@bot.command()
@commands.has_role('Officer')
async def getPlayerAtt(ctx, familyName, window='All'):
  await ctx.message.delete()
  await ctx.send(getPlayerAttPerc(familyName, window), delete_after=deleteTime)

@bot.command()
@commands.has_role('Officer')
async def getMissing(ctx):
  role = discord.utils.get(ctx.guild.roles,name="Guild Member")
  guildList = [member.display_name for member in role.members]
  missingNames = getMissingNames(guildList)

  myStr = "```\nMissing People:\n"
  myStr += ", ".join([str(name) for name in missingNames])
  myStr += "\nTotal Count: " + str(len(missingNames)) + "```"

  await ctx.message.delete()
  await ctx.send(myStr, delete_after=deleteTime)

@bot.command()
@commands.has_role('Officer')
async def updateGuildFile(ctx):
  role = discord.utils.get(ctx.guild.roles,name="Guild Member")
  with open('Guildies.txt', 'w', encoding="utf-8") as mainFile:
    for member in role.members:
      mainFile.write(member.display_name + "\n")
    mainFile.close()

  await ctx.send("Guild List File updated.", delete_after=deleteTime)

@bot.command()
@commands.is_owner()
async def shutdown(ctx):
  await ctx.message.delete()
  await ctx.send("We're closing. The Tomato Bisque is sold out for the night!", delete_after=2.0)
  await asyncio.sleep(5)
  await ctx.bot.logout()

bot.run(myTOKEN)

#Attendance = 'https://cdn.discordapp.com/attachments/411788991353061389/830276999066288188/unknown.png'
#S = ImageToAttendance(Attendance)
#generateFile(S)
# myUrl = input("Enter link: ")
# ImageToAttendance(myUrl)