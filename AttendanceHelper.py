import os

def processGearBotData(rawData):
  processedData = []
  for item in rawData:
    if "> <" in item:
      temp = item.split(">")
      FamName = temp[-1].replace("`", "").lstrip()
      processedData.append(FamName)
  return list(set(processedData))


def getMissingNames(guildList=None, attendanceList=None):
  if guildList is None:
    guildFile = open('Guildies.txt', 'r', encoding="utf-8")
    guildList = guildFile.readlines()
    guildFile.close()

  if attendanceList is None:
    respondFile = "responder.txt"
    attendanceList = []
    if os.path.exists(respondFile):
    	with open(respondFile, 'r', encoding="utf-8") as f:
    		for line in f:
    			name = line.split('>')
    			attendanceList.append(name[2].strip())
    		f.close()
  
  # Iterate through the list of people who responded
  for i in attendanceList:
  	# Iterate through the guild list
  	for j in guildList:
  		# if a part of name from the respond List exist in guildList
  		if i in j:
  			guildList.remove(j)

  return guildList
