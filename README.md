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
  * $getYesAttOn:MMDDYY
  * (ie. $getYesAttOn 010121)
  * $getNoAttOn MMDDYY 
  * (ie. $getNoAttOn 010121)

* Get Missing Responding People:
  * $getMissing

* Add Person
  * $addYesFor FamilyName Date(Optional)
  * (ie. $addYesFor TomatoBisque) FOR TODAY
  * (ie. $addYesFor TomatoBisque 010121) FOR SPECIFC DATE 

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
  * Gets the player attendnace for the previous <integer> nw's
* Query From Google Sheet
  * TODO