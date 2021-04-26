import os

def processGearBotData(rawData):
  processedData = []
  for item in rawData:
    if "> <" in item:
      temp = item.split(">")
      FamName = temp[-1].replace("`", "").lstrip()
      processedData.append(FamName)
  return list(set(processedData))


def trimList(guildList=None, namesToDelete=None):
  if guildList is None:
    guildFile = open('Guildies.txt', 'r', encoding="utf-8")
    guildList = guildFile.readlines()
    guildFile.close()

  if namesToDelete is None:
    respondFile = "responder.txt"
    namesToDelete = []
    if os.path.exists(respondFile):
    	with open(respondFile, 'r', encoding="utf-8") as f:
    		for line in f:
    			name = line.split('>')
    			namesToDelete.append(name[2].strip())
    		f.close()
  
  # Iterate through the list of people who responded/or ignored
  for i in namesToDelete:
  	# Iterate through the guild list
  	for j in guildList:
  		# if a part of name from the respond List exist in guildList
  		if i in j:
  			guildList.remove(j)

  return guildList
