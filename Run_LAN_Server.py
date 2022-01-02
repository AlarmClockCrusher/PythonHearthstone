from Parts.Code2CardList import *

"""
selectors.EVENT_READ = 1; selectors.EVENT_WRITE = 2
So the bitwise or operation '|' and bitwise operation '&'
	can check if it's ready to read or write
"""

def socketAcceptswithTimeout(sock, timeout=1):
	sock.settimeout(timeout)
	try: conn, addr = sock.accept()
	except TimeoutError:
		print("The client failed to reconnect before timeout. Reset the sockets")
		conn = addr = None
	sock.settimeout(None)
	return conn, addr


class ScrollPanel(tk.Frame):
	def __init__(self, master, text, ls):
		super().__init__(master)
		self.text, self.lbl = text, tk.Label(self, text=text, font=("Yahei", 14))
		self.lbl.pack()
		scroll_bar = tk.Scrollbar(self)
		scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)
		self.listBox = tk.Listbox(self, yscrollcommand=scroll_bar.set, height=30)
		for line in ls:
			self.listBox.insert(tk.END, line)
		self.lbl["text"] = self.text + str(len(ls))
		self.listBox.pack(side=tk.LEFT, fill=tk.BOTH)
		scroll_bar.config(command=self.listBox.yview)

	def updateListDisplay(self, ls):
		self.listBox.delete(0, tk.END)
		for line in ls: self.listBox.insert(tk.END, line)
		self.lbl["text"] = self.text + str(len(ls))


class Table(tk.Frame):
	def __init__(self, innKeeper, tableDict):
		super().__init__(master=innKeeper.panel_Tables)
		self.innKeeper = innKeeper
		self.guestInfos = tableDict
		#Default is {"guest1ID": 'TestPlayerID', "guest2ID":'', "seeHands": False,
					#"deck1": deck1Code, "deck2": '', "class1": "Demon Hunter", "class2": ''}

		self.handsDecks = {1: b'', 2: b''}
		self.seed = datetime.now().microsecond
		self.mainPlayerID, self.ID_1st = numpyRandint(1, 3), numpyRandint(1, 3)
		self.boardID = numpyChoice(BoardIndex)
		self.keepRunning = True

		"""Put the hero image and address info in the frame"""
		size = (int(143/2), int(197/2))
		filepath_Hero1 = "Images\\HeroesandPowers\\%s.png"%Classes2HeroeNames[self.guestInfos["class1"]]
		self.lbl_Hero1Img = tk.Label(self, image=(ph := getPILPhotoImage(filePath=filepath_Hero1, size=size)))
		self.lbl_Hero1Img.image = ph
		self.lbl_Hero2Img = tk.Label(self, image=(ph := getPILPhotoImage(filePath=filePath_HeroBlank, size=size)))
		self.lbl_Hero2Img.image = ph
		self.lbl_Guest1 = tk.Label(self, text="玩家1: "+self.guestInfos["guest1ID"], font=("Yahei", 13))
		self.lbl_Guest2 = tk.Label(self, text="玩家2: ", font=("Yahei", 13))
		self.lbl_Guest1.grid(row=0, column=0, columnspan=3)
		self.lbl_Guest2.grid(row=1, column=0, columnspan=3)
		self.lbl_Hero1Img.grid(row=2, column=0, rowspan=4)
		self.lbl_Hero2Img.grid(row=2, column=2, rowspan=4)
		tk.Label(self, text="双方手牌互相可见" if self.guestInfos["seeHands"] else '',
				 font=("Yahei", 12)).grid(row=2, column=1)

	def updatePlayersInfo(self):
		self.innKeeper.lbl_NumTables["text"] = "运行中对战数：%d"%len(self.innKeeper.tables)
		size = (int(143/2), int(197/2))
		for ID, lbl_HeroImg, lbl_Guest in zip((1, 2), (self.lbl_Hero1Img, self.lbl_Hero2Img),
											 (self.lbl_Guest1, self.lbl_Guest2)):
			#Update Hero cardImage
			guestID = self.guestInfos["guest%dID"%ID]
			if heroClass := self.guestInfos["class%d"%ID]:
				filePath = "Images\\HeroesandPowers\\%s.png"%Classes2HeroeNames[heroClass]
			else: filePath = filePath_HeroBlank
			lbl_HeroImg.config(image=(ph := getPILPhotoImage(filePath=filePath, size=size)))
			lbl_HeroImg.image = ph
			#Update the Guest ID
			lbl_Guest["text"] = "玩家%d: "%ID+self.guestInfos["guest%dID"%ID]


class InnKeeper:
	def __init__(self):
		self.address, self.sock4PortQuery, self.socksAvailable = "", None, []
		#Need to a special socket to respond to queries about what port can be connected for playing
		self.guests = {}  # {bytes_GuestID: {"sock_Recv": None, "sock_Send": None, "conn_Recv": None, "conn_Send": None,}}
		self.tables = [] #list of tableDicts[{"guest1ID": "TestPlayerID", "guest2ID": '', "seeHands": False,
											#"deck1": "weiofhweoigwef", "deck2": "weiofhweoigwef",
											#"class1": "Hunter", "class2": "Mage"}]
		"""Initiate the tkinter UI"""
		#Top panel that holds server info & start/stop buttons & ports availability
		self.window = tk.Tk()
		self.btn_Start = tk.Button(self.window, text="开始运行", bg="green3", font=("Yahei", 20, "bold"),
								   command=lambda : threading.Thread(target=self.openBusiness, daemon=True).start())
		btn_Stop = tk.Button(self.window, text="终止", bg="red",
							 font=("Yahei", 15, "bold"), command=self.stopRunning)
		self.entry_Address = tk.Entry(self.window, font=("Yahei", 20), width=10)
		self.entry_NumGuests = tk.Entry(self.window, font=("Yahei", 20), width=5)
		self.entry_Address.insert(0, "0.0.0.0")
		self.entry_NumGuests.insert(0, "20")
		self.lbl_NumTables = tk.Label(self.window, text="运行中对战数：0", font=("Yahei", 15))
		tk.Label(self.window, text="服务器地址", font=("Yahei", 20, "bold")).grid(row=0, column=0)
		self.entry_Address.grid(row=0, column=1)
		tk.Label(self.window, text="桌子数量", font=("Yahei", 20, "bold")).grid(row=1, column=0)
		self.entry_NumGuests.grid(row=1, column=1)
		self.btn_Start.grid(row=2, column=0)
		btn_Stop.grid(row=2, column=1)
		self.lbl_NumTables.grid(row=3, column=0, columnspan=2)
		#Visualization panel for tables
		self.panel_Ports = ScrollPanel(self.window, text="可用端口数:", ls=[])
		self.panel_GuestIDs = ScrollPanel(self.window, text="已连接的用户:", ls=[])
		self.panel_Tables = tk.Frame(self.window, width=300, height=300)
		self.panel_Ports.grid(row=4, column=0)
		self.panel_GuestIDs.grid(row=4, column=1)
		self.panel_Tables.grid(row=1, column=2, rowspan=5, columnspan=3)

		ph = getPILPhotoImage(self.window, "Models\\UIModels\\Arrow.png")
		self.arrow_Left = tk.Label(self.window, image=ph)#, size=(32, 32))
		self.arrow_Left.ph = ph
		ph = getPILPhotoImage(self.window, "Models\\UIModels\\Arrow_Right.png")
		self.arrow_Right = tk.Label(self.window, image=ph)#, size=(32, 32))
		self.arrow_Right.ph = ph
		self.arrow_Left.grid(row=0, column=2)
		self.arrow_Right.grid(row=0, column=3)
		self.window.mainloop()

	#老板开放一系列port，其中首个port为咨询port,用来返回其他ports
	#client接入port后，老板向client发送所有目前server上的对局的英雄，牌组信息
	#随后如果有client改变了预约桌子的状态，（可以是取消连接或者是为了修改带的牌桌）则其需要重新连接
	#client接入老板返回的port时候也可以是观战和加入桌子
	def prepare4Business(self, numTables=2):
		self.sock4PortQuery = self.prepSocket(socket.socket(socket.AF_INET, socket.SOCK_STREAM), 65432)

		ports = [65433 + i for i in range(2 * numTables)]
		socks = [socket.socket(socket.AF_INET, socket.SOCK_STREAM) for i in range(2 * numTables)]
		for port, sock in zip(ports, socks):
			self.socksAvailable.append(self.prepSocket(sock, port, timeout=1, closeFirst=False))

	def prepSocket(self, sock, port, timeout=0, closeFirst=False):
		if closeFirst: sock.close()
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		if timeout: sock.settimeout(1)
		sock.bind((self.address, port))
		sock.listen()
		return sock

	def updateInnStatusDisplay(self):
		self.panel_Ports.updateListDisplay(ls := [sock.getsockname()[1] for sock in self.socksAvailable])
		print("socks available num", len(ls))
		self.panel_GuestIDs.updateListDisplay(
			ls := [str(guestID) + str(dic["sock_Recv"].getsockname()[1]) + str(dic["sock_Send"].getsockname()[1])
			 for guestID, dic in self.guests.items()])
		print("guest IDs num", ls)
		self.lbl_NumTables["text"] = "桌子数%d"%len(self.tables)
		for i, table in enumerate(self.tables):
			table.updatePlayersInfo()
			table.grid(row=1+i%3, column=int(i/3))

	#每张桌子应该有自己的ID，就是每个用户连接时自己的ID
	def genInnStatus(self):
		return b'InnStatus---' + pickleObj2Bytes([table.guestInfos for table in self.tables])

	# Whenever a socket connects to this query port, server tells it the availability of table ports
	def openBusiness(self):
		self.prepare4Business(int(self.entry_NumGuests.get()))
		self.updateInnStatusDisplay()
		self.btn_Start.config(bg="cyan", text="正在运行")
		while True:
			conn, addr = self.sock4PortQuery.accept()
			if (data := conn.recv(1024)) and data.startswith(b"Port Availabiltiy Query---"):
				_, bytes_GuestID = data.split(b"---") #b"Port Availabiltiy Query---TestPlayerID"
				print("\nGot a request to connect for guest", conn, addr, bytes_GuestID)
				self.tellGuestInnStatus(conn, bytes_GuestID)
			else: #是否应该把未知的IP addr禁止再次访问
				print("\nGot an unknown connection from IP adress", addr)
				conn.close()

	#从self.sock4PortQuery给予guest信息，b"No Ports Left"  b"This ID is taken"  b"Ports available---65433---65434"
	#给予信息后立刻关闭这个conn，但是因为self.sock4PortQuery没有关闭，所以其可以直接重新接收连接请求
	#如果给予了guest两个新的port，则开个线程，让这两个port接收guest的端口连接
	def tellGuestInnStatus(self, conn, bytes_GuestID):
		if len(self.socksAvailable) < 2: conn.sendall(b"No Ports Left")
		elif bytes_GuestID in self.guests: conn.sendall(b"This ID is taken")
		else:
			port_Recv = (sock_Recv := self.socksAvailable.pop()).getsockname()[1]
			port_Send = (sock_Send := self.socksAvailable.pop()).getsockname()[1]
			print("\nReturns available tables to client", b"Ports available---%d---%d"%(port_Recv, port_Send))
			conn.sendall(b"Ports available---%d---%d"%(port_Recv, port_Send))
			#告诉guest两个个可用的port，然后guest会从这两个新的port连接，然后对新的连接输出InnStatus
			threading.Thread(target=lambda : self.ports4GuestKeepRunning(bytes_GuestID, sock_Recv, sock_Send),
							 name="Port %d, %d Starts Waiting"%(port_Recv, port_Send), daemon=True).start()
		conn.close()

	#guestID will be saved in self.guestInfos. guestID is bytes.
	def ports4GuestKeepRunning(self, bytes_GuestID, sock_Recv, sock_Send):
		#如果client不能在规定时间内成功连接，则取消其连接权。成功连接之后把sock的timeout调回None
		if not (conn_Recv := socketAcceptswithTimeout(sock_Recv)[0]): return
		if not (conn_Send := socketAcceptswithTimeout(sock_Send)[0]): return
		try: #genInnStatus得到把当前的所有桌子和桌子旁的玩家ID。tableInfo {"guest1ID": '', "guest2ID": ''}
			self.guests[bytes_GuestID] = {"sock_Recv": sock_Recv, "sock_Send": sock_Send,
											"conn_Recv": conn_Recv, "conn_Send": conn_Send}
			print("\nGuest reconnected to the 2 ports given. Send inn status:", (s := self.genInnStatus()))
			conn_Send.sendall(s)
			self.updateInnStatusDisplay()
			#After acquiring the inn status, the guest can choose to reserve/join/spectate a table
			while True:
				if guestAction := recv_PossibleLongData(conn_Recv):
					self.handleGuestActions(guestAction, sock_Recv, sock_Send, conn_Recv, conn_Send)
					if guestAction.startswith(b"End Connection"):
						conn_Recv.close()
						conn_Send.close() #No need to close and restart the sock.
						print("Guest {} ends connection to server".format(bytes_GuestID))
						ataTable = self.getInvolvedTable_with_GuestID(bytes_GuestID.decode()) is not None
						self.clearTableof(bytes_GuestID, notifyEveryGuest=ataTable, deleteGuest=True)
						break
				else: raise ConnectionError
		#如果在连接状态下有错误出现，则把玩家在的桌子清空
		except ConnectionError:
			print("\nConnection to guest is lost")
			ataTable = self.getInvolvedTable_with_GuestID(bytes_GuestID.decode()) is not None
			self.clearTableof(bytes_GuestID, notifyEveryGuest=ataTable, deleteGuest=True)

	def clearTableof(self, bytes_GuestID, notifyEveryGuest, deleteGuest):
		print("Clearing the table of guestID:", bytes_GuestID, [table.guestInfos["guest1ID"] for table in self.tables])
		guestID = bytes_GuestID.decode()
		if table := next((table for table in self.tables if table.guestInfos["guest1ID"] == guestID), None):
			print("\nFound a table that has the guest1ID", bytes_GuestID, table.guestInfos)
			removefrom(table, self.tables)
			table.destroy()
			if notifyEveryGuest: self.publishInnStatus()
		else: print("\nClear Table func didn't find a table that matches the guestID")
		if table := next((table for table in self.tables if table.guestInfos["guest2ID"] == guestID), None):
			print("Found a table having guest2ID")
		if deleteGuest and bytes_GuestID in self.guests:
			sock_Recv = (guest := self.guests[bytes_GuestID])["sock_Recv"]
			sock_Send, portsAvailable = guest["sock_Send"], [sock.getsockname()[1] for sock in self.socksAvailable]
			portsAvailable.sort()
			print("Clearing table. Ports available right now", portsAvailable)
			print(sock_Recv.getsockname()[1], sock_Send.getsockname()[1])
			if sock_Recv.getsockname()[1] not in portsAvailable: self.socksAvailable.append(sock_Recv)
			if sock_Send.getsockname()[1] not in portsAvailable: self.socksAvailable.append(sock_Send)
			del self.guests[bytes_GuestID]
		self.updateInnStatusDisplay()

	#需要保证不同的线程之间不会发生冲突。需要在执行期间把这个函数锁起来
	def publishInnStatus(self):
		innStatus = self.genInnStatus()
		for bytes_GuestID, socksandConns in self.guests.items():
			try: socksandConns["conn_Send"].sendall(innStatus)
			except ConnectionError: print("Connection Error to ", bytes_GuestID) 

	def bytes_GuestID_matches_SocksConns(self, bytes_GuestID, sock_Recv, sock_Send, conn_Recv, conn_Send):
		return bytes_GuestID in self.guests and \
			   self.guests[bytes_GuestID] == {"sock_Recv": sock_Recv, "sock_Send": sock_Send,
										   			"conn_Recv": conn_Recv, "conn_Send": conn_Send}

	def checkGuestInfoFormat(self, info):
		try:
			if isinstance(info["guest1ID"], str) and isinstance(info["guest2ID"], str) and \
					isinstance(info["deck1"], str) and isinstance(info["deck2"], str) and \
					isinstance(info["class1"], str) and isinstance(info["class2"], str) and \
					isinstance(info["seeHands"], bool):
				return True
			else:
				print("Format error in Table GuestInfo received")
				return False
		except KeyError as e:
			print("KeyError in the Table GuestInfo received:", e)
			return False

	def getInvolvedTable_with_GuestID(self, guestID, verbose=True):
		if not (table := next((table for table in self.tables if table.guestInfos["guest1ID"] == guestID or
					table.guestInfos["guest2ID"] == guestID), None)) and verbose:
			print("Can't find a table guestID {} is involved with".format(guestID))
		return table

	def getOwnedTable_with_GuestID(self, guestID, verbose=True):
		if not (table := next((table for table in self.tables if table.guestInfos["guest1ID"] == guestID), None)) \
				and verbose:
			print("Can't find a table guestID {} owns".format(guestID))
		return table

	# Start waiting for guest's decision: Reserve/Join/Spectate at a table
	#如果guest预约、加入或者旁观牌桌，则会设立专门的table。然后停止这个ports4GuestKeepRunning
	def handleGuestActions(self, guestAction, sock_Recv, sock_Send, conn_Recv, conn_Send):
		print("\n\nReceived guestAction info from guest", guestAction)
		if guestAction.startswith(b"Query a Table---"):
			guest1ID = guestAction.split(b"---")[1].decode()
			if tableInfo := next((tableInfo for tableInfo in self.tables if tableInfo["guest1ID"] == guest1ID), None):
				conn_Send.sendall(b"Table Info---"+pickleObj2Bytes(tableInfo))
			else: conn_Send.sendall(b"Table owner ID doesn't match an owned table")
		elif guestAction.startswith(b"Reserve a Table---"):
			guestInfos = unpickleBytes2Obj(guestAction.split(b"---")[1])
			#guest1ID in the tableDict from client is the guestID
			bytes_GuestID = (guest1ID := guestInfos["guest1ID"]).encode()
			if self.getOwnedTable_with_GuestID(guest1ID, verbose=False):
				print("Found an indentical guestID owning a table:", guest1ID)
				conn_Send.sendall(b"Disconnect and change your ID")
			else: #Player ID doesn't conflict with other peoples. Can reserve successfully
				print("Successfully reserve a table for guestID", bytes_GuestID)
				self.tables.append(table := Table(self, guestInfos))
				self.publishInnStatus()
				conn_Send.sendall(b"Table successfully reserved")
			self.updateInnStatusDisplay()
		elif (isEndConn := guestAction.startswith(b"End Connection---")) or guestAction.startswith(b"Cancel a Table---"):
			_, bytes_GuestID = guestAction.split(b"---") #self.guestInfos keys are bytes
			print("Received a request to disconnect", bytes_GuestID)
			if self.bytes_GuestID_matches_SocksConns(bytes_GuestID, sock_Recv, sock_Send, conn_Recv, conn_Send):
				if isEndConn: conn_Send.sendall(b"Connection terminated")
				else: conn_Send.sendall(b"Table successfully cancelled")
				self.clearTableof(bytes_GuestID, notifyEveryGuest=True, deleteGuest=isEndConn)
				self.publishInnStatus()
			else: conn_Send.sendall(b"Your ID doesn't match the record")
		elif guestAction.startswith(b"Join a Table---"):
			#pickledInfo_Table2Join is the table info that someone wants to join
			#pickledInfo_Applicant is the info of the person who wants to join a table
			_, pickledInfo_Table2Join, pickledInfo_Applicant = guestAction.split(b"---")
			print("Trying to join table info:", _, pickledInfo_Table2Join, pickledInfo_Applicant)
			info_Table2Join = unpickleBytes2Obj(pickledInfo_Table2Join)
			info_Applicant = unpickleBytes2Obj(pickledInfo_Applicant)
			applicantID, tableOwnerID = info_Applicant["guest1ID"], info_Table2Join["guest1ID"]
			print("Processing join table request using infos", info_Applicant, info_Table2Join)
			if self.bytes_GuestID_matches_SocksConns(applicantID.encode(), sock_Recv, sock_Send, conn_Recv, conn_Send):
				if not self.getInvolvedTable_with_GuestID(applicantID):
					if table := self.getOwnedTable_with_GuestID(tableOwnerID):
						if table.guestInfos["guest2ID"]: conn_Send.sendall(b"Another player at this table")
						else:
							"""info_Applicant has info about applicant under 1. Need to flip"""
							table.guestInfos["guest2ID"] = info_Applicant["guest1ID"]
							table.guestInfos["deck2"] = info_Applicant["deck1"]
							table.guestInfos["class2"] = info_Applicant["class1"]
							self.publishInnStatus()
							conn_Send.sendall(b"Joined table")
							self.guests[tableOwnerID.encode()]["conn_Send"].sendall(b"Someone joined your table")
					else: conn_Send.sendall(b"Table owner ID doesn't match an owned table")
				else: conn_Send.sendall(b"You must exit the current table before joining another")
			else: conn_Send.sendall(b"Your ID doesn't match the record")
		elif guestAction.startswith(b"Exit a Table---"):
			_, pickledInfo_Table2Exit = guestAction.split(b"---")
			info_Table2Exit = unpickleBytes2Obj(pickledInfo_Table2Exit)
			leaverID, tableOwnerID = info_Table2Exit["guest2ID"], info_Table2Exit["guest1ID"]
			if table := self.getInvolvedTable_with_GuestID(leaverID.encode()):
				if table.guestInfos["guest2ID"] == leaverID:
					table.guestInfos["guest2ID"] = table.guestInfos["deck2"] = table.guestInfos["class2"] = ''
					self.publishInnStatus()
					conn_Send.sendall(b"Exited Table")
				else: pass
			else: conn_Send.sendall(b"Trying to exit a table you are not")
		elif guestAction.startswith(b"Table start game---"): #b"Table start game---"+bytes_GuestID
			bytes_OwnerID = guestAction.split(b"---")[1]
			if self.bytes_GuestID_matches_SocksConns(bytes_OwnerID, sock_Recv, sock_Send, conn_Recv, conn_Send):
				print("Found ownerID in Inn", bytes_OwnerID)
				if table := self.getOwnedTable_with_GuestID(bytes_OwnerID.decode()):
					bytes_BoardID = table.boardID.encode()
					int_SeeHands = 1 if table.guestInfos["seeHands"] else 0
					guest1ID, guest2ID = table.guestInfos["guest1ID"], table.guestInfos["guest2ID"]
					bytes_Class1, bytes_Class2 = table.guestInfos["class1"].encode(), table.guestInfos["class2"].encode()
					ID_1st = table.ID_1st
					s0 = b"%s---%d---%d---%d---%s---%s"%(bytes_BoardID, table.seed, table.mainPlayerID,
															  int_SeeHands, bytes_Class1, bytes_Class2)
					for guestID, Id in zip((guest1ID, guest2ID), (ID_1st, 3-ID_1st)):
						s = b"Game Init Info---%d---"%Id + s0 + b"---%s"%table.guestInfos["deck%d"%Id].encode()
						print("Sending Game initiate info to ", guestID.encode(), s)
						self.guests[guestID.encode()]["conn_Send"].sendall(s)
				else: print("Didn't find table owned by ", bytes_OwnerID)
			else: print("GuestID requesting table start game is not found", bytes_OwnerID)
		elif guestAction.startswith(b"Exchange Mulligan&Deck---"):
			_, bytes_GuestID, pickled_MulliganDeck = guestAction.split(b"---")
			guestID = bytes_GuestID.decode()
			if table := self.getInvolvedTable_with_GuestID(bytes_GuestID.decode()):
				table.handsDecks[1 if table.guestInfos["guest1ID"] == guestID else 2] = pickled_MulliganDeck
				if table.handsDecks[1] and table.handsDecks[2]:
					for ID in (1, 2):
						conn_Send = self.guests[table.guestInfos["guest%dID"%ID].encode()]["conn_Send"]
						s = b"Start Game with Oppo Hand_Deck---" + table.handsDecks[3-ID]
						print("Sending start game info to players")
						send_PossiblePadding(conn_Send, s)
			else: conn_Send.sendall(b"You are not at a table")
		elif guestAction.startswith(b"Game Move---"):
			_, bytes_GuestID, pickled_Moves, pickled_Picks = guestAction.split(b"---")
			print("Handling Game Move", bytes_GuestID, pickled_Moves, pickled_Picks)
			if table := self.getInvolvedTable_with_GuestID(bytes_GuestID.decode()):
				if table.guestInfos["guest1ID"] == bytes_GuestID.decode():
					oppoID = table.guestInfos["guest2ID"] #Send info to opponent
				else: oppoID = table.guestInfos["guest1ID"]
				s = b"Game Move---%s---%s"%(pickled_Moves, pickled_Picks)
				print("Sending game move to the other")
				self.guests[oppoID.encode()]["conn_Send"].sendall(s)
			else:
				print("Failed to send game mv to oppon")
				conn_Send.sendall(b"You are not at a table")
		elif guestAction.startswith(b"Spectate at a Table---"):
			pass

	def stopRunning(self):
		self.window.destroy()
		quit()
				
				
if __name__ == "__main__":
	InnKeeper()