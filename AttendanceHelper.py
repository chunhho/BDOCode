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
			if i.lower().strip() in j.lower().strip():
				guildList.remove(j)

	return guildList

def findDiscordName(guildList, discordName):
	#guildList = in-game family names
	myDict = {}
	myFam = []
	myDis = []
	myFkdUpNames = {'BavoI': 'Bavol', 'Lieng' : '˥ᴉǝuƃ', 'Waffle' : 'ᗆጠ⊣', 'LarsaMadsen' : 'Larsa Madsen (MadsenFamily)' }
	found = False
	for a in guildList:

		if a.strip() in myFkdUpNames.keys():
			myDict[a.strip()] = myFkdUpNames[a.strip()]
			found = True

		# elif a.strip() == 'Lieng':
		# 	myDict[a] = '˥ᴉǝuƃ'
		# 	found = True

		# elif a.strip() == 'Waffle':
		# 	myDict[a] = 'ᗆጠ⊣'
		# 	found = True

		else:
			for b in discordName:
				if (a.lower().strip() in b.lower().strip()) or (b.lower().strip() in a.lower().strip()):
					if b == "fro" and len(a) > 6:
						continue
					else:
						found = True
						myDict[a] = b
						break

		if found == False:
			myFam.append(a)
			myDis.append(b)
		else:
			found = False
	return myDict, myFam, myDis