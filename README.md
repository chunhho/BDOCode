# BDOCode
For BDO Stuff

Commands:

* Set Attendance:
  * Set Attendance for TODAY:
  * $setAtt <<URL>>
  * (ie. $setAtt https://cdn.discordapp.com/attachments/411788991353061389/827714272887832606/unknown.png)
    
* Set Attendance on SPECIFIC DATE:
  * $setAttOn MMDDYY <<URL>>
  * (ie. $setAttOn 010121 https://cdn.discordapp.com/attachments/411788991353061389/827714272887832606/unknown.png)

* Get Attendance
  * $getYesOn:MMDDYY
  * (ie. $getYesOn 010121)
  * $getNoOn MMDDYY 
  * (ie. $getNoOn 010121)

* Update Guild File (Looks for 'Guild Member' Role and put their info into file)
  * $updateGuildFile

* Set Attending Role to People:
  * $setMon
  * $setWed
  * $setFri

* Clear Attending Role from People:
  * $clearAtt

* Get Missing Responding People:
  * $getMon
  * $getWed
  * $getFri

* Add Person
  * $setYesFor FamilyName Date(Optional)
  * (ie. $setYesFor TomatoBisque) FOR TODAY
  * (ie. $setYesFor TomatoBisque 010121) FOR SPECIFC DATE
  * $setYesListForDate Date Name1 Name2 Name3 ...
  * (ie. $setYesListForDate 010101 Alpha Beta Charlie Delta)

* Add to Google Sheet
  * $updateSheet Date
  * (ie. $updateSheet 010121)
  * Prints new member names to be added to the master list

* Delete From Google Sheet
  * $demolish FamilyName Master(Optional)
  * Master is if you want to remove from Master List
  * (ie. $demolish ExGuildie)
  * (ie. $demolish ExGuildie True
  
* Get a players attendance % from Google Sheet
  * $getPlayerAtt <username>
  * Gets the total player attendance (all attendable nw's)
  * $getPlayerAtt <username> <integer>
  * Gets the player attendance for the previous <integer> nw's
* Query From Google Sheet
  * TODO
  
* Set Player 2 week attendance on Members List
  * $uploadTwoWeekAttendance