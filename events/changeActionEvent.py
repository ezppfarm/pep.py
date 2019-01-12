from common.log import logUtils as log
from constants import clientPackets
from constants import serverPackets
from objects import glob
from common.constants import mods

def handle(userToken, packetData):
	# Get usertoken data
	userID = userToken.userID
	username = userToken.username

	# Make sure we are not banned
	#if userUtils.isBanned(userID):
	#	userToken.enqueue(serverPackets.loginBanned())
	#	return

	# Send restricted message if needed
	#if userToken.restricted:
	#	userToken.checkRestricted(True)

	# Change action packet
	packetData = clientPackets.userActionChange(packetData)

	# If we are not in spectate status but we're spectating someone, stop spectating
	'''
if userToken.spectating != 0 and userToken.actionID != actions.WATCHING and userToken.actionID != actions.IDLE and userToken.actionID != actions.AFK:
	userToken.stopSpectating()

# If we are not in multiplayer but we are in a match, part match
if userToken.matchID != -1 and userToken.actionID != actions.MULTIPLAYING and userToken.actionID != actions.MULTIPLAYER and userToken.actionID != actions.AFK:
	userToken.partMatch()
		'''

	# Update cached stats if our pp changed if we've just submitted a score or we've changed gameMode
	#if (userToken.actionID == actions.PLAYING or userToken.actionID == actions.MULTIPLAYING) or (userToken.pp != userUtils.getPP(userID, userToken.gameMode)) or (userToken.gameMode != packetData["gameMode"]):

	# Update cached stats if we've changed gamemode
	if userToken.gameMode != packetData["gameMode"]:
		userToken.gameMode = packetData["gameMode"]
		userToken.updateCachedStats()

	# Always update action id, text, md5 and beatmapID
	userToken.actionID = packetData["actionID"]
	
	userToken.actionMd5 = packetData["actionMd5"]
	userToken.actionMods = packetData["actionMods"]
	userToken.beatmapID = packetData["beatmapID"]

	
	if bool(packetData["actionMods"] & 128) == True:
		userToken.relaxing = True
		UserText = packetData["actionText"] + " Playing Relax"
		userToken.actionText = UserText
		userToken.updateCachedStats()
		if userToken.apAnnounce == True:
			userToken.apAnnounce = False
		if userToken.autobotting == True:
			userToken.autobotting = False
		if userToken.relaxAnnounce == False:
			userToken.relaxAnnounce = True
			userToken.enqueue(serverPackets.notification("Hey, you're playing with Relax, we've changed the leaderboards to Relax."))
	elif bool(packetData["actionMods"] & 8192) == True:
		userToken.autobotting = True
		UserText = packetData["actionText"] + " Playing AutoPilot"
		userToken.actionText = UserText
		if userToken.relaxAnnounce == True:
			userToken.relaxAnnounce = False
		if userToken.relaxing == True:
			userToken.relaxing = False
		userToken.updateCachedStats()
		if userToken.apAnnounce == False:
			userToken.apAnnounce = True
			userToken.enqueue(serverPackets.notification("Hey, you're playing with AutoPilot, We've chaned the learboards to AutoPilot."))
	else:
		UserText = packetData["actionText"]
		userToken.actionText = UserText
		userToken.relaxing = False
		userToken.autobotting = False
		userToken.updateCachedStats()
		if userToken.relaxAnnounce == True:
			userToken.relaxAnnounce = False
		elif userToken.apAnnounce == True:
			userToken.apAnnounce = False
			userToken.enqueue(serverPackets.notification("Hey, you've disabled relax/autopilot. We've changed back to the Regular leaderboards."))
	glob.db.execute("UPDATE users_stats SET current_status = %s WHERE id = %s", [UserText, userID])
	# Enqueue our new user panel and stats to us and our spectators
	recipients = [userToken]
	if len(userToken.spectators) > 0:
		for i in userToken.spectators:
			if i in glob.tokens.tokens:
				recipients.append(glob.tokens.tokens[i])

	for i in recipients:
		if i is not None:
			# Force our own packet
			force = True if i == userToken else False
			i.enqueue(serverPackets.userPanel(userID, force))
			i.enqueue(serverPackets.userStats(userID, force))

	# Console output
	log.info("{} changed action: {} [{}][{}][{}]".format(username, str(userToken.actionID), userToken.actionText, userToken.actionMd5, userToken.beatmapID))
