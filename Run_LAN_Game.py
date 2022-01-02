from Panda.UICommonPart import *
import platform, subprocess

"""tableInfo/guestInfo的格式应该是"""
#{"guest1ID": str_Guest1ID, "guest2ID": str_Guest1ID,
	#"seeHands": False, "deck1": deck1Code, "deck2": deck2Code,
	#"class1": "Demon Hunter", "class2": "Warlock"}

pos_ConnInfoStandy, pos_ConnInfoConnected, pos_JoinedTable = (-14, 5, 0.1), (-14, 11, 0.1), (0, 5.3, 0)

class DeckBuilderHandler_Online(DeckBuilderHandler):
	x_offset_Deck2, pos_Start = -33.5, (1.4, 0, 2.2)
	def __init__(self, GUI):
		self.serverIPAddr, self.serverPort4Query, self.guestID = "127.0.0.1", 65432, platform.uname().node
		self.ownTable, self.joinedTable, self.tableInfos = None, None, []
		self.otherTablePages, self.otherTablesShown = {}, []
		self.connInfoRoot = self.btn_StartGame = None
		self.connected = False
		self.state = "" #"Reserved", "Joined", ''
		super().__init__(GUI, for1P=False)

	"""Total tree structure"""
	#render/Model2Keep_DeckBuilder
		#Conn Info Root
			#ConnInfo_TextNode
			#Btn_EditInfo
				#Text_TextNode|cNode|Options
			#Btn_Conn
				#Text_TextNode|cNode|Options
		#NP_OwnTable
			#PanelFrame|HeroFrame|cardImage|HeroFrame_2|cardImage_2
			#Text_TextNode|guest1ID_TextNode|guest2ID_TextNode
			#Panel
				#NurbsCurve|cNode
			#See Each Other'sHand
				#Check|Plane|Text_TextNode|cNode
			#Btn_Action
				#Options|Text_TextNode|cNode
		#NP_OthersTable

	def load(self):
		super().load()
		"""需要在套牌界面上进入服务器地址和端口等信息的输入"""
		self.connInfoRoot = self.root.attachNewNode("Conn Info Root")
		self.connInfoRoot.setPos(pos_ConnInfoStandy)
		s = self.GUI.txt("Server IP Address: {}\nServer Query Port: {}\nPlayer ID: {}")
		makeText(self.connInfoRoot, "ConnInfo", s.format(self.serverIPAddr, self.serverPort4Query, self.guestID),
				 pos=(2, 1, 0), scale=0.6, font=self.GUI.getFont(self.GUI.lang), color=black)[1].setAlign(TextNode.ALeft)
		#Place the btns and texts for guest info input
		self.GUI.addaButton("Button_Option", "Btn_EditInfo", parent=self.connInfoRoot, pos=(0, 1, 0), text="Edit", func=self.startConnInfoInput)
			#Later this "Connect" nodepath will accessed from tree in order to change its text and btn function
		self.GUI.addaButton("Button_Option", "Btn_Conn", parent=self.connInfoRoot, pos=(0, 0, 0), func=self.conn2Server, text="Connect")

	"""更新并显示当前酒馆里面的TableInfo"""
	def decideOwnTableGuestInfos(self, resetSeeHands=False):
		seeHands = False
		if not resetSeeHands and "seeHands" in self.ownTable.guestInfos:
			seeHands = self.ownTable.guestInfos["seeHands"]
		deckCode = "names"
		for card in self.decks[1]: deckCode += "||" + card.__name__
		self.ownTable.guestInfos["deck1"], self.ownTable.guestInfos["class1"] = deckCode, self.heroes[1].Class

		self.ownTable.guestInfos = {"guest1ID": self.guestID, "guest2ID": '',
							"seeHands": seeHands, "deck1": deckCode, "deck2": "",
							"class1": self.heroes[1].Class, "class2": ""}
		self.ownTable.refreshDisplay()

	#info_InnStatus b"InnStatus---".后面跟的是一个dict的列表，每个dict都是桌子的信息
	def updateInnStatus(self, info_InnStatus):
		self.tableInfos = unpickleBytes2Obj(info_InnStatus.split(b'---')[1])
		self.showTables()

	def getInvolvedTableInfo(self):
		return next((tableInfo for tableInfo in self.tableInfos
					 		if self.guestID in (tableInfo["guest1ID"], tableInfo["guest2ID"])), None)

	def lastPage(self):
		self.pageNum -= 1
		if self.collectionRoot.isStashed(): self.showTables(recalcPages=False)
		else: self.showCollection(recalcPages=False)

	def nextPage(self):
		self.pageNum += 1
		if self.collectionRoot.isStashed(): self.showTables(recalcPages=False)
		else: self.showCollection(recalcPages=False)

	def showTables(self, recalcPages=True):
		for table in self.otherTablesShown: table.np.removeNode()
		self.otherTablesShown = []
		#Always refresh own table display
		if info := next((info for info in self.tableInfos if info["guest1ID"] == self.guestID), None):
			self.ownTable.guestInfos = info
			self.ownTable.refreshDisplay()

		if recalcPages:
			self.otherTablePages, self.pageNum, i = {}, 0, 0
			for tableInfo in self.tableInfos:
				if tableInfo["guest1ID"] == self.guestID:
					self.ownTable.guestInfos = info
					self.ownTable.refreshDisplay()
				elif tableInfo["guest2ID"] == self.guestID:
					self.otherTablesShown.append(Table(self.GUI, tableInfo, pos_JoinedTable))
				if tableInfo["guest1ID"] != self.guestID:
					add2ListinDict(tableInfo, self.otherTablePages, int(i / 6))
					i += 1

		print("Showing tables:", [(info["guest1ID"], info["guest2ID"]) for info in self.tableInfos])
		if self.otherTablePages:
			self.pageNum = min(len(self.cardPages) - 1, self.pageNum)
			for i, tableInfo in enumerate(self.otherTablePages[self.pageNum]):
				# ownTable & joined table display is refreshed aboved
				if tableInfo["guest1ID"] != self.guestID and tableInfo["guest2ID"] != self.guestID:
					pos = (0 if i < 3 else 10.2, -5.3 * (i % 3), 0)
					self.otherTablesShown.append(Table(self.GUI, tableInfo, pos))
			if self.pageNum < 1: self.leftArrow.stash()
			else: self.leftArrow.unstash()
			if self.pageNum >= len(self.cardPages) - 1: self.rightArrow.stash()
			else: self.rightArrow.unstash()

	"""The input/update button needs to be able to switch func and text every time they are clicked"""
	#startConnInfoInput and getConnInfoInput are coupled together and reference each other
	def startConnInfoInput(self, btn):
		if self.connected: Btn_NotificationPanel(self.GUI, text=self.GUI.txt("Change your ID while not connected"))
		else:
			self.GUI.changeBtnDisplay(btn.np, newText="Update", newTextColor=white,
									  newTexture=self.GUI.textures["Button_Concede"])
			btn.func = self.getConnInfoInput

			text = self.GUI.txt("Server IP Address: {}\nServer Query Port: {}\nPlayer ID: {}").format('', '', '')
			with open("Input.txt", 'w', encoding="utf-8") as outputFile:
				outputFile.write(text)
			os.startfile("Input.txt")

	def getConnInfoInput(self, btn):
		GUI = self.GUI
		if self.connected: Btn_NotificationPanel(self.GUI, text=GUI.txt("Change your ID while not connected"))
		else:
			GUI.changeBtnDisplay(btn.np, newText="Edit", newTextColor=black, newTexture=GUI.textures["Button_Option"])
			btn.func = self.startConnInfoInput
			with open("Input.txt", 'r', encoding="utf-8") as inputFile:
				try:
					if ipAddr := inputFile.readline().split(':')[1].strip():
						if ipAddr.replace('.', '').isnumeric() and ipAddr.count('.') != 3:
							raise IndexError
						else: self.serverIPAddr = ipAddr
				except IndexError: #Error: No ':' in line or the input is purely numeric but not 'xxx.xxx.xxx.xxx'
					Btn_NotificationPanel(self.GUI, text="ServerIPAddr Unreadable")
					return
				try:
					if portInfo := inputFile.readline().split(':')[1].strip():
						self.serverPort4Query = int(portInfo)
				except (IndexError, ValueError): #Error: No ':' in line or the input isn't an integer
					Btn_NotificationPanel(self.GUI, text="serverPort4Query Must be integer number")
					return
				try:
					words = inputFile.readline().split(':')
					if len(words) == 2 and '---' not in (guestID := words[1].strip()):
						self.guestID = guestID
						self.ownTable.np.find("guest1ID_TextNode").node().setText(guestID)
					else: raise IndexError
				except IndexError: #Error: No or too many ':' in line, '---' in line
					Btn_NotificationPanel(self.GUI, text=GUI.txt("GuestID CANNOT have ':' or '---'"))
					return
			text = GUI.txt("Server IP Address: {}\nServer Query Port: {}\nPlayer ID: {}").format(
								self.serverIPAddr, self.serverPort4Query, self.guestID)
			self.root.find("Conn Info Root").find("ConnInfo_TextNode").node().setText(text)

	def getGuestID_DeckCode_Class(self):
		deck1Code = deck2Code = "names"
		for card in self.decks[1]: deck1Code += "||" + card.__name__
		for card in self.decks[2]: deck2Code += "||" + card.__name__
		return self.guestID, deck1Code, self.heroes[1].Class if self.heroes[1] else ''

	def conn2Server(self, btn):
		GUI = self.GUI
		GUI.restartSockets()
		serverIP, port = self.serverIPAddr, self.serverPort4Query
		param = '-n' if platform.system().lower() == 'windows' else '-c'
		command = ["ping", param, '1', serverIP]
		if subprocess.call(command) != 0:
			Btn_NotificationPanel(GUI, text=GUI.txt("Can't ping the address ")+serverIP)
			return
		try: # Connect to server and check available ports
			GUI.sock_Send.connect((serverIP, port)) # Blocks. If the server port rejects this attempt, it raises error
		except ConnectionRefusedError:
			Btn_NotificationPanel(GUI, text=GUI.txt("Can't connect to the query port")+str(port))
			return
		#到达这一些说明已经连接上服务器的询问端口
		GUI.sock_Send.sendall(b"Port Availabiltiy Query---"+self.guestID.encode())
		#3 Responses: b"This ID is taken"  b"No Ports Left"  b"Port available,65433,65434"
		self.decideOwnTableGuestInfos(resetSeeHands=True)
		if info_AvailablePort := recv_PossibleLongData(GUI.sock_Send):
			print("Info availability", info_AvailablePort)
			if info_AvailablePort.startswith(b"This ID is taken"):
				Btn_NotificationPanel(self.GUI, text=self.GUI.txt("This ID is taken"))
			elif info_AvailablePort.startswith(b"No Ports Left"):
				Btn_NotificationPanel(self.GUI, text=self.GUI.txt("No room for more guests for now"))
			elif info_AvailablePort.startswith(b"Ports available"):
				print("Start Reconnecting to the two ports given by query port")
				# Server receives to 1st port, client receives to 2nd port
				header, port_Send, port_Recv = info_AvailablePort.split(b'---')
				GUI.restartSockets()
				# The sock_Recv has remained unused so far
				GUI.sock_Send.connect((serverIP, int(port_Send)))
				GUI.sock_Recv.connect((serverIP, int(port_Recv)))
				print("Successfully connected. Now wait for inn status")
				# Will receive the Inn Status from InnKeeper, and update the panel accordingly
				threading.Thread(target=GUI.start_sock_Recv, name="Running Sock Receive", daemon=True).start()
				return
		else:
			Btn_NotificationPanel(self.GUI, text=self.GUI.txt("Connection is lost"))
			self.handleConnected(connected=False)

		GUI.restartSockets() #只有成功连接的情况下不会重启sockets

	def handleConnected(self, connected):
		self.connected = connected
		self.connInfoRoot.find("ConnInfo_TextNode").node().setTextColor(collectionTrayColor if connected else black)
		# Change text of btn for connection to "Connect"
		textNode = (np_Btn := self.connInfoRoot.find("Btn_Conn")).find("Text_TextNode").node()
		textNode.setText(self.GUI.txt("Disconnect" if connected else "Connect"))
		textNode.setTextColor(white if connected else black)
		np_Btn.setTexture(np_Btn.findTextureStage("*"), self.GUI.textures["Button_Concede" if connected else "Button_Option"], 1)
		np_Btn.getPythonTag("btn").func = self.disconnect if connected else self.conn2Server
		self.connInfoRoot.setPos(pos_ConnInfoConnected if connected else pos_ConnInfoStandy)

	#info_InnStatus b"InnStatus---"+pickled [table.guestInfos]
	#Invoked by GUI.start_sock_Recv
	def enterInn(self, info_InnStatus):
		print("Inn status acquired. Update display:", info_InnStatus)
		self.manaTrayRoot.stash()
		self.expansionIconRoot.stash()
		self.collectionRoot.stash()
		self.classTray.stash()
		#Unstash ownTable and the root of other tables
		self.innStatusRoot.unstash()
		self.ownTable.np.unstash()
		self.handleConnected(connected=True)
		# 把自己的桌子update。此时用的dictTable是没有bytes的。update可以自己分辨是dict还是pickle
		self.updateInnStatus(info_InnStatus)

	def updateTable(self, infoTable):
		#拿着这个infoTable，在画出的桌子里面寻找符合的桌子，并显示其对应的卡组
		tableInfo = unpickleBytes2Obj(infoTable.split(b"---")[1])
		print("Table Info", infoTable)
		for table in [self.ownTable, self.joinedTable, *self.otherTablesShown]:
			if table and table.guestInfos["guest1ID"] == tableInfo["guest1ID"]:
				table.guestInfos = tableInfo
				table.showDetails(table.np.find("Panel").getPythonTag("btn"))
				break

	"""从酒馆中断开连接"""
	def disconnect(self, btn):
		self.GUI.sock_Send.sendall("End Connection---{}".format(self.guestID).encode())

	def leaveInn(self):
		self.tableInfos = {}
		self.showTables()
		self.manaTrayRoot.unstash()
		self.expansionIconRoot.unstash()
		self.collectionRoot.unstash()
		self.classTray.unstash()
		#Stash ownTable and the root of other tables
		self.innStatusRoot.stash()
		self.ownTable.np.stash()
		self.state = ''
		self.handleConnected(connected=False)


class Table: #dictTable in the declaration is a pickled object
	def __init__(self, GUI, guestInfos, pos, yourOwnTable=False):
		self.GUI, self.guestInfos, self.isOwnTable = GUI, guestInfos, yourOwnTable
		root = GUI.deckBuilder.root if yourOwnTable else GUI.deckBuilder.innStatusRoot
		self.np = GUI.modelTemplates["Own Table" if yourOwnTable else "Other's Table"].copyTo(root)
		self.np.setPos(pos)
		# 处理模型的显示。自己的桌子和别人的桌子会有略微不同
		(panel := self.np.find("Panel")).setPythonTag("btn", Btn_Button(GUI, self.np, func=self.showDetails))
		GUI.addaCheckBox(self.np, "See Each Other's Hand", text="See Each \nOther's Hand", pos=(1.35, 0.7, 0.1),
						 pickable=yourOwnTable)
		GUI.addaButton("Button_Option", "Btn_Action", parent=self.np, pos=(0, 1.5, 0.01),
					   text="Reserve" if yourOwnTable else "Join",
					   func=self.reserveorCancel if yourOwnTable else self.joinorExit)
		if yourOwnTable:
			self.np.name = "NP_OwnTable"
			panel.setColor(collectionTraySelectedColor)
			GUI.deckBuilder.btn_StartGame = np_Btn = GUI.addaButton("Button_Start", "Btn_Start", self.np, pos=(0.5, -1.2, 0.01),
						   											func=GUI.startGame)
			np_Btn.setScale(0.55)
			np_Btn.stash()
		else: self.refreshDisplay() #如果是自己的桌子，先不更新，到enterInn之后再更新

	#dicTable could be {"guest1ID", "guest2ID", "seeHands", "deck1", "deck2", "class1", "class2"}
		#or a pickle of this
	def refreshDisplay(self):
		if isinstance(self.guestInfos, bytes): self.guestInfos = unpickleBytes2Obj(self.guestInfos)
		print("Updating table based on guestInfos", self.guestInfos)
		self.np.find("guest1ID_TextNode").node().setText(self.guestInfos["guest1ID"])
		self.np.find("guest2ID_TextNode").node().setText(self.guestInfos["guest2ID"])
		for Class, name in zip((self.guestInfos["class1"], self.guestInfos["class2"]), ("cardImage", "cardImage_2")):
			cardImage = self.np.find(name)
			if Class in Classes2HeroeNames:
				cardImage.setTexture(cardImage.findTextureStage('*'), self.GUI.loader.loadTexture(
												"Images\\HeroesandPowers\\%s.png"%Classes2HeroeNames[Class]), 1)
				cardImage.show()
			else: cardImage.hide()
		if self.isOwnTable and self.guestInfos["guest1ID"] == self.GUI.deckBuilder.guestID and self.guestInfos["guest2ID"]:
			self.GUI.deckBuilder.btn_StartGame.unstash()
		else: self.GUI.deckBuilder.btn_StartGame.stash()

	def queryTable(self):
		self.GUI.sock_Send.sendall(b"Query a Table---"+self.guestInfos["guest1ID"].encode())

	def showDetails(self, btn):
		deckBuilder = self.GUI.deckBuilder
		deckBuilder.ownTable.np.find("Panel").setColor(collectionTrayColor)
		for table in deckBuilder.otherTablesShown: table.np.find("Panel").setColor(collectionTrayColor)
		self.np.find("Panel").setColor(collectionTraySelectedColor)

		if self.isOwnTable:
			deckBuilder.updateDeck(1, deckCode=self.guestInfos["deck1"])
			deckBuilder.updateDeck(2, deckCode=self.guestInfos["deck2"])
		else:
			deckBuilder.updateDeck(1, deckCode=self.guestInfos["deck2"])
			deckBuilder.updateDeck(2, deckCode=self.guestInfos["deck1"])

	def toggleseeHands(self):
		self.guestInfos["seeHands"] = not self.guestInfos["seeHands"]
		check = self.np.find("See Each Other's Hand").find("Check")
		check.setColor(green if self.guestInfos["seeHands"] else transparent)

	def reserveorCancel(self, btn):
		if (deckBuilder := self.GUI.deckBuilder).state:
			Btn_NotificationPanel(self.GUI, text="Exit the table you joined before proceeding")
			return
		deckBuilder.decideOwnTableGuestInfos(resetSeeHands=False)
		self.guestInfos["guest1ID"] = (deckBuilder := self.GUI.deckBuilder).guestID
		deckCode = "names" #Decide the deckCode to send to server
		for card in deckBuilder.decks[1]: deckCode += "||" + card.__name__
		self.guestInfos["deck1"], self.guestInfos["class1"] = deckCode, deckBuilder.heroes[1].Class
		if deckBuilder.state == "Reserved": s = b"Cancel a Table---" + self.guestInfos["guest1ID"].encode()
		else: s = b"Reserve a Table---" + pickleObj2Bytes(self.guestInfos)
		print("Sending reserve/cancel request to server", s)
		try: self.GUI.sock_Send.sendall(s)
		except ConnectionError: pass

	def joinorExit(self, btn):
		if (deckBuilder := self.GUI.deckBuilder).state == "Reserved":
			Btn_NotificationPanel(self.GUI, text="Cancel the table you reserved before proceeding")
			return
		if deckBuilder.state == "Joined": #Starts with the guestInfos of the table you want to join
			s = b"Exit a Table---" + pickleObj2Bytes(self.guestInfos)
		else: s = b"Join a Table---" + pickleObj2Bytes(self.guestInfos) + b"---" + pickleObj2Bytes(deckBuilder.ownTable.guestInfos)
		print("Sending join table request to server", s)
		send_PossiblePadding(self.GUI.sock_Send, s)


class Test_OnlineGame(Panda_UICommon):
	def addaCheckBox(self, parent, name, pos, text, color=black, pickable=True, func=None):
		checkBox = self.modelTemplates["CheckBox"].copyTo(parent)
		checkBox.name = name  # 有时候需要在定义之后重新找到这个checkBox在tree里面的位置
		checkBox.setPos(pos)
		textNode = checkBox.find("Text_TextNode").node()
		textNode.setText(self.txt(text))
		textNode.setTextColor(color)
		if pickable:
			checkBox.setPythonTag("btn", Btn_Button(self, np=checkBox, func=func))
		else: checkBox.find("cNode").removeNode()

	#本函数在Panda_UICommon的prepareTexturesandModels里面调用
	"""新增"Own Table", "Other's Table"和"CheckBox"新的modelTemplate"""
	"""把modelTemplates["ClassSelectionTray"]复制给modelTemplates["Own Table"]，并在其基础上补全"""
	def prepareDeckBuilderPanel(self):
		texture_HeroFrame = self.loader.loadTexture("Models\\HeroModels\\Stats.png")
		self.modelTemplates["Other's Table"] = othersTable = self.loader.loadModel("Models\\UIModels\\OthersTable.glb")
		othersTable.name = "NP_OthersTable"
		trayFrame, heroFrame, heroFrame_2 = othersTable.find("PanelFrame"), othersTable.find("HeroFrame"), othersTable.find("HeroFrame_2")
		trayFrame.setTexture(trayFrame.findTextureStage('*'),
							self.loader.loadTexture("Models\\UIModels\\CollectionTray.png"), 1)
		heroFrame.setTexture(heroFrame.findTextureStage('*'), texture_HeroFrame, 1)
		heroFrame_2.setTexture(heroFrame_2.findTextureStage('*'), texture_HeroFrame, 1)
			#Click the panel to view the its details
		(panel := othersTable.find("Panel")).setColor(collectionTrayColor)
		(cNode := CollisionNode("cNode")).addSolid(CollisionBox((0, 0, 0), 5, 2.5, 0.02))
		panel.attachNewNode(cNode)#.show()
			#Used to indicate the status, playerIDs of a table.
		for tray, isOwnTable in zip((self.modelTemplates["Own Table"], othersTable), (True, False)):
			makeText(tray, "Text", '', pos=(1, 0.3, 0.1), scale=0.5, color=black,
					font=self.getFont(self.lang))[1].setAlign(TextNode.A_boxed_left)
			makeText(tray, "guest1ID", "", pos=(4.3 if isOwnTable else -4.3, -2, 0.1), scale=0.4, color=black,
					font=self.getFont(self.lang))[1].setAlign(TextNode.A_boxed_right if isOwnTable else TextNode.A_boxed_left)
			makeText(tray, "guest2ID", "", pos=(-4.3 if isOwnTable else 4.3, -2, 0.1), scale=0.4, color=black,
				 	font=self.getFont(self.lang))[1].setAlign(TextNode.A_boxed_left if isOwnTable else TextNode.A_boxed_right)

		# Add a check box template
		self.modelTemplates["CheckBox"] = checkBox = self.loader.loadModel("Models\\UIModels\\CheckBox.glb")
		plane, check = checkBox.find("Plane"), checkBox.find("Check")
		check.setTransparency(True)
		check.setColor(transparent)
		plane.setTexture(plane.findTextureStage("*"), self.textures["UIDesign"], 1)
		makeText(checkBox, "Text", "", pos=(-0.22, -0.1, 0.05), scale=0.35, color=black,
				 font=self.getFont(self.lang))[1].setAlign(TextNode.A_right)
		(cNode := CollisionNode("cNode")).addSolid(CollisionBox((0, 0, 0.03), 0.17, 0.17, 0.01))
		checkBox.attachNewNode(cNode)#.show()

		"""Finally handle the DeckBuilder"""
		self.deckBuilder = DeckBuilderHandler_Online(self)
		self.deckBuilder.ownTable = table = Table(self, guestInfos={}, pos=pos_ClassSelectionTray, yourOwnTable=True)
		table.np.stash()
		self.deckBuilder.decideOwnTableGuestInfos(resetSeeHands=True)
		
	def restartSockets(self):
		if self.sock_Send: self.sock_Send.close()
		if self.sock_Recv: self.sock_Recv.close()
		self.sock_Send = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock_Recv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	def changeBtnDisplay(self, np_Btn, newText, newTextColor, newTexture):
		textNode = np_Btn.find("Text_TextNode").node()
		textNode.setText(self.txt(newText))
		textNode.setTextColor(newTextColor)
		np_Btn.setTexture(np_Btn.findTextureStage("*"), newTexture, 1)

	def startGame(self, btn):
		s = b"Table start game---"+self.deckBuilder.guestID.encode()
		print("Trying to start game. Info", s)
		self.sock_Send.sendall(s)

	def initMulligan(self, btn):
		#In 1P mode, this starts game immediately; in Online mode, you need to wait for opponent to finish mulligan, too
		ID, self.stage, game = self.ID, 0, self.Game
		for btn in self.btns2Remove: btn.destroy()

		indices = [i for i, status in enumerate(self.mulliganStatus[self.ID]) if status]
		for i in indices: game.mulligans[ID][i].btn.np.removeNode()
		# 直到目前为止不用创建需要等待的sequence
		game.Hand_Deck.mulligan1Side(ID, indices)
		# 2P需要通过Server沟通。需要将我方手牌和牌库信息上传Server，然后等待对方的信息回传
		mulliganDeck = [[type(card) for card in game.mulligans[self.ID]],
						[type(card) for card in game.Hand_Deck.decks[self.ID]]]
		s = b"Exchange Mulligan&Deck---%s---%s"%(self.deckBuilder.guestID.encode(), pickleObj2Bytes(mulliganDeck))
		print("Sending to server the mulligan info", self.deckBuilder.guestID.encode())
		send_PossiblePadding(self.sock_Send, s)

	def sendOwnMovethruServer(self, endingTurn=False):
		game = self.Game
		moves, picks = game.moves, game.picks_Backup
		game.moves, game.picks, game.picks_Backup = [], [], []
		if moves:
			s = b"Game Move---%s---%s---%s"%(self.deckBuilder.guestID.encode(), pickleObj2Bytes(moves), pickleObj2Bytes(picks))
			print("Sending plays thru server", self.deckBuilder.guestID.encode(), moves, picks)
			send_PossiblePadding(self.sock_Send, s)

	def concede(self, btn):
		if self.stage != -1:
			self.stage = -2
			print("Concede! Going back to layer 1")
			self.gamePlayQueue.append(lambda: self.Game.concede(self.ID))

	def setMsg(self, msg):
		self.msg_Exit = msg

	def decodePlayfromServer(self, data):
		game = self.Game
		header, moves, picks = data.split(b"---")
		moves, picks = unpickleBytes2Obj(moves), unpickleBytes2Obj(picks)
		print("Decoding move", moves, picks)
		if isinstance(moves, (list, tuple)):
			game.evolvewithGuide(moves, picks)
		self.stage = -2 if game.turn != self.ID else 0
		gameEnds = game.gameEnds
		if gameEnds:
			self.stage = -2
			if gameEnds == 1: self.heroExplodeAni([game.heroes[1]])
			elif gameEnds == 2: self.heroExplodeAni([game.heroes[2]])
			else: self.heroExplodeAni([game.heroes[1], game.heroes[2]])
			for btn in self.btns2Remove: btn.destroy()
			self.msg_Exit = "Player dead"

	def start_sock_Recv(self):
		print("Start constantly getting data from server")
		while True:
			if not (data := recv_PossibleLongData(self.sock_Recv)):
				Btn_NotificationPanel(self, text=self.txt("Reception from Server has faults"))
				self.restartSockets()
				self.back2Layer1()
				break
			else:
				print("Got data from server", data)
				#从服务器得到了目前在酒馆中的所有桌子情况，包括自己的那个桌子。然后更新显示
				if data.startswith(b"InnStatus---"):
					if self.deckBuilder.state != "In Game": self.deckBuilder.enterInn(data)
				#从服务器处查询被点击的桌子的所有信息，然后进行显示。
				elif data.startswith(b"Table Info---"): #b"Table Info---"+pickleObj2Bytes(tableInfo)
					self.deckBuilder.updateTable(data)
				#当你在连接到服务器的状态下尝试改变自己的ID
				elif data.startswith(b"Disconnect and change your ID"):
					Btn_NotificationPanel(self, text=self.txt("You have the same player ID as someone else.\nDisconnect and change your ID"))
				#当你申请从服务器断开连接的操作成功后会收到这个断开连接的信号。重置自己的sock
				elif data.startswith(b"Connection terminated"):
					Btn_NotificationPanel(self, text=self.txt("You have disconnected from the server"))
					self.restartSockets()
					self.deckBuilder.leaveInn()
				#自己的桌子成功预约或者取消。需要把自己的state设置为"Reserved"或""
				elif data.startswith(b"Table successfully"): #Reserved or cancelled
					if isReserved := b"reserved" in data:
						self.deckBuilder.state, newText = "Reserved", "Cancel"
						newTextColor, newTexture = white, self.textures["Button_Concede"]
					else:
						self.deckBuilder.state, newText = '', "Reserve"
						newTextColor, newTexture = black, self.textures["Button_Option"]
					self.changeBtnDisplay(self.deckBuilder.ownTable.np.find("Btn_Action"),
											newText, newTextColor, newTexture)
				#成功加入了一个牌桌或者退出了一个自己加入了的桌子
				elif data in (b"Joined Table", b"Exited Table"):
					deckBuilder = self.deckBuilder
					if b"Joined" in data:
						deckBuilder.state, newText = "Joined", "Exit"
						newTextColor, newTexture = white, self.textures["Button_Concede"]
						Btn_NotificationPanel(self, text=self.txt(data.decode()))
					else:
						deckBuilder.state, newText = "", "Join"
						newTextColor, newTexture = black, self.textures["Button_Option"]
					np_Btn = next(table for table in deckBuilder.otherTablesShown
						 			if table.guestInfos["guest2ID"] == deckBuilder.guestID).np.find("Btn_Action")
					self.changeBtnDisplay(np_Btn, newText, newTextColor, newTexture)
				#一些其他的情况下，只显示通知
				elif data in (b"Your ID doesn't match the record",
								b"You must exit the current table before joining another",
								b"Table owner ID doesn't match an owned table",
								b"Someone joined your table",
								b"Trying to exit a table you are not",
							  ):
					Btn_NotificationPanel(self, text=self.txt(data.decode()))
				#加入牌桌之后，从服务器拿到牌桌棋盘，种子，双方初始牌库等信息，然后开始起手调度。
				elif data.startswith(b"Game Init Info---"):
					print("Trying to initiate game based on info", data)
					self.deckBuilder.state = "In Game"
					_, ID, boardID, seed, mainPlayerID, int_SeeHands, bytes_Class1, bytes_Class2, deckCode = data.split(b"---")
					self.ID, self.boardID, self.Game.mainPlayerID = int(ID), boardID.decode(), int(mainPlayerID)
					numpy.random.seed(int(seed))
					self.showEnemyHand = int(int_SeeHands) != 0
					if tableInfo := self.deckBuilder.getInvolvedTableInfo():
						hero1 = Class2HeroDict[tableInfo["class1"]]
						hero2 = Class2HeroDict[tableInfo["class2"]]
						print("Trying to init game using deckCode:", deckCode.decode())
						deck, deckCorrect, hero = parseDeckCode(deckCode.decode(), "Demon Hunter",
																Class2HeroDict, cardPool_All=cardPool_All)
						heroes = (hero1, hero2) if self.ID == 1 else (hero2, hero1)
						self.Game.initialize_Details(self.boardID, int(seed), RNGPools, *heroes, deck1=deck, deck2=deck)
						if self.np_CardZoomIn: self.np_CardZoomIn.removeNode()
						self.clearDrawnCards()
						self.deckBuilder.root.stash()
						self.initMulliganDisplay(for1P=False)
					else:
						print("Didn't find table involved.", self.deckBuilder.guestID,
							  [(tableInfo["guest1ID"], tableInfo["guest2ID"]) for tableInfo in self.deckBuilder.tableInfos])
				# 自己在加入了一个牌桌时，双方手牌调度完成之后，根据对方的手牌和牌库信息进行自己的游戏的初始化
				elif data.startswith(b"Start Game with Oppo Hand_Deck---"):
					header, handDeck_Oppo = data.split(b"---")
					mulligan, deck = unpickleBytes2Obj(handDeck_Oppo)
					game, ID_Oppo = self.Game, 3 - self.ID
					game.mulligans[ID_Oppo] = [card(game, ID_Oppo) for card in mulligan]
					game.Hand_Deck.initialDecks[ID_Oppo] = deck
					game.Hand_Deck.decks[ID_Oppo] = [card(game, ID_Oppo) for card in deck]
					# 此时双方手牌中的牌都还没有进行entersHand、entersDeck处理。留给game.Hand_Deck.finalizeHandDeck_StartGame处理
					self.stage = 0
					print("\n-----------------\nStart the game as PLAYER %d\n----------------" % self.ID)
					game.Hand_Deck.finalizeHandDeck_StartGame()
					self.addaButton("Button_Concede", "Concede", self.render, pos=(20.5, -8, 1.1),
									text="Concede", textColor=white, removeAfter=True, func=self.concede)
					tableInfo = self.deckBuilder.getInvolvedTableInfo()
					makeText(self.render, "PlayerID", tableInfo["guest%dID"%self.ID], pos=(22.5, -10, 1.1), scale=0.7,
							 color=white, font=self.getFont(self.lang))[1].setAlign(TextNode.A_boxed_right)
					makeText(self.render, "PlayerID", tableInfo["guest%dID"%(3-self.ID)], pos=(22.5, 10, 1.1), scale=0.7,
							 color=white, font=self.getFont(self.lang))[1].setAlign(TextNode.A_boxed_right)
				#在游戏对局中得到了对手的游戏操作。
				elif data.startswith(b"Game Move---"):
					self.decodePlayfromServer(data)
				elif data.startswith(b"End Game---"):
					pass


if __name__ == "__main__":
	Test_OnlineGame().run()