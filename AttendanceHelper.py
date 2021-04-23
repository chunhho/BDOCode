import os

def getMissingNames(guildList=None):
  if guildList is None:
    guildFile = open('Guildies.txt', 'r', encoding="utf-8")
    guildList = guildFile.readlines()
    guildFile.close()

  respondFile = "responder.txt"
  respondList = []
  if os.path.exists(respondFile):
  	with open(respondFile, 'r', encoding="utf-8") as f:
  		for line in f:
  			name = line.split('>')
  			respondList.append(name[2].strip())
  		f.close()
  
  # Iterate through the list of people who responded
  for i in respondList:
  	# Iterate through the guild list
  	for j in guildList:
  		# if a part of name from the respond List exist in guildList
  		if i in j:
  			guildList.remove(j)

  return guildList
