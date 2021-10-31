import socket
from Parts_ConstsFuncsImports import *
from Parts_Code2CardList import *

import tkinter as tk
import PIL.Image, PIL.ImageTk
from Panda_UICommonPart import unpickleBytes2Obj
from Run_OnlineGame import send_PossiblePadding, recv_PossibleLongData

"""
selectors.EVENT_READ = 1; selectors.EVENT_WRITE = 2
So the bitwise or operation '|' and bitwise operation '&'
	can check if it's ready to read or write
"""

				
class Table(tk.Frame):
	def __init__(self, innKeeper):
		super().__init__(master=innKeeper.panel_Tables)
		self.innKeeper = innKeeper
		self.socks2Players = {1: None, 2: None}
		self.conns2Players = {1: None, 2: None}
		self.boardID = numpyChoice(BoardIndex)
		self.decksHandsHeroes  = {1: b'', 2: b''}
		self.mainPlayerID = numpyChoice([1, 2])
		self.noResponseTime = 0 #如果超过2分钟则尝试断开连接，并保存当前进度
		self.heroes = {1: b'', 2: b''}
		self.buffers = {1: b'', 2: b''}
		self.handsDecks = {1: b'', 2: b''}
		#self.curTurn = 1
		self.seed = datetime.now().microsecond
		self.keepRunning = True
		self.infoSegmentHeader = b""
		
		"""Put the hero image and address info in the frame"""
		filepath_Blank = "Images\\HeroesandPowers\\Unknown.png"
		ph = PIL.ImageTk.PhotoImage(PIL.Image.open(filepath_Blank).resize((int(143/2), int(197/2))))
		self.lbl_Hero1Img = tk.Label(self, image=ph)
		self.lbl_Hero1Img.image = ph
		ph = PIL.ImageTk.PhotoImage(PIL.Image.open(filepath_Blank).resize((int(143/2), int(197/2))))
		self.lbl_Hero2Img = tk.Label(self, image=ph)
		self.lbl_Hero2Img.image = ph
		self.lbl_Player1 = tk.Label(self, text="玩家1:  ", font=("Yahei", 14))
		self.lbl_Player2 = tk.Label(self, text="  玩家2:", font=("Yahei", 14))
		self.lbl_Hero1Img.grid(row=0, column=0, rowspan=2)
		self.lbl_Hero2Img.grid(row=0, column=2, rowspan=2)
		self.lbl_Player1.grid(row=0, column=1)
		self.lbl_Player2.grid(row=1, column=1)
		
	def updatePlayersInfo(self):
		self.innKeeper.lbl_NumTables["text"] = "运行中对战数：%d"%len(self.innKeeper.tablesShown)
		for ID, lbl_HeroImg, lbl_Hero in zip((1, 2), (self.lbl_Hero1Img, self.lbl_Hero2Img),
											 (self.lbl_Player1, self.lbl_Player2)):
			sock = self.socks2Players[ID]
			byte_Hero = self.heroes[ID]
			print(byte_Hero)
			if byte_Hero: filePath = "Images\\HeroesandPowers\\%s.png"%unpickleBytes2Obj(self.heroes[ID]).__name__
			else: filePath = "Images\\HeroesandPowers\\Unknown.png"
			ph = PIL.ImageTk.PhotoImage(PIL.Image.open(filePath).resize((int(143/2), int(197/2))))
			lbl_HeroImg.config(image=ph)
			lbl_HeroImg.image = ph
			if ID == 1: lbl_Hero["text"] = "玩家1: "+ (sock.getsockname()[0] if sock else "")
			else: lbl_Hero["text"] = "  玩家2: "+ (sock.getsockname()[0] if sock else "")
			
	def portStart(self, ID):
		print("Table port {} starts accepting conns".format(ID))
		conn, addr = self.socks2Players[ID].accept()
		print("Table {} port {} has established conn to player port {}".format(self, ID, addr))
		self.conns2Players[ID] = conn
		#Send the connected player the player ID and RNG seed
		conn.sendall(b"PlayerID BoardID Seed||%d||%s||%d" % (ID, self.boardID.encode(), self.seed))
		
		while self.keepRunning:
			try:
				totalData = recv_PossibleLongData(self, self.conns2Players[ID])
				if not totalData:
					print("Table receives no data. Free a table")
					self.innKeeper.freeaTable(self)
				print("Table received data:", totalData)
				if totalData.startswith(b"Hero Picked"):
					header, self.heroes[ID] = totalData.split(b"||")
					self.updatePlayersInfo()
					#If both players have submitted their game info, then they can start mulligan
					#Give each player their opponent's info
					if self.heroes[1] and self.heroes[2]:
						print("Telling each player the opponent hero picked", self.heroes[1], self.heroes[2])
						send_PossiblePadding(self, self.conns2Players[1], b"Enemy Hero Picked||"+self.heroes[2])
						send_PossiblePadding(self, self.conns2Players[2], b"Enemy Hero Picked||"+self.heroes[1])
				#一个玩家自己的换牌结束，向这里递交自己的手牌和牌库情况
				elif totalData.startswith(b"Exchange Deck&Hand"):
					header, self.handsDecks[ID] = totalData.split(b"||")
					if self.handsDecks[1] and self.handsDecks[2]:
						print("Both finished mulligan. Tell each player the opponent hand deck")
						send_PossiblePadding(self, self.conns2Players[1], b"Start Game with Oppo Hand_Deck||"+self.handsDecks[2])
						send_PossiblePadding(self, self.conns2Players[2], b"Start Game with Oppo Hand_Deck||"+self.handsDecks[1])
				elif totalData.startswith(b"Game Move"):
					print("Game move from client {}. Pass it to oppo, and return b'Move Received'".format(ID))
					send_PossiblePadding(self, self.conns2Players[ID], b"Info Received")
					send_PossiblePadding(self, self.conns2Players[3-ID], totalData)
					if b"concede" in totalData:
						self.innKeeper.freeaTable(self)
			except ConnectionResetError as e: #If the connection to client is lost
				print("Table {}'s connection to client {} is lost".format(self, ID))
				try: self.conns2Players[3-ID].sendall(b"Opponent Disconnected")
				except: pass
				self.innKeeper.freeaTable(self)
			except Exception as e:
				print("While port is running, exception is", e)
				
		print("Thread of port stopping")
	
	def handleConnectionLost(self, msg=''):
		raise ConnectionResetError
	
	
class InnKeeper:
	def __init__(self):
		#Attributes of the server
		self.address = ""
		self.socketsAvailable = []  #(port, sock)
		self.socketsOccupied = []  #(sock, conn)
		#Need to a special socket to respond to queries about what port can be connected for playing
		self.sock4PortQuery, self.conn4PortQuery = None, None
		self.tables = {}
		
		self.window = tk.Tk()
		"""Panel holding info for starting/stopping the server"""
		panel_Config = tk.Frame(self.window)
		panel_Config.grid(row=0, column=0)
		self.btn_Start = tk.Button(panel_Config, text="开始运行", bg="green3", font=("Yahei", 20, "bold"),
							  command=lambda : threading.Thread(target=self.openBusiness, daemon=True).start())
		btn_Stop = tk.Button(panel_Config, text="终止", bg="red",
							  font=("Yahei", 15, "bold"), command=self.stopRunning)
		self.entry_Address = tk.Entry(panel_Config, font=("Yahei", 20), width=10)
		self.entry_NumTables = tk.Entry(panel_Config, font=("Yahei", 20), width=5)
		self.entry_Address.insert(0, "0.0.0.0")
		self.entry_NumTables.insert(0, "20")
		self.lbl_SocketsAvailable = tk.Label(panel_Config, text="可用端口数", font=("Yahei", 15))
		self.lbl_NumTables = tk.Label(panel_Config, text="运行中对战数：0", font=("Yahei", 15))
		tk.Label(panel_Config, text="服务器地址", font=("Yahei", 20, "bold")).grid(row=0, column=0)
		self.entry_Address.grid(row=0, column=1)
		tk.Label(panel_Config, text="桌子数量", font=("Yahei", 20, "bold")).grid(row=0, column=2)
		self.entry_NumTables.grid(row=0, column=3)
		self.btn_Start.grid(row=0, column=4)
		btn_Stop.grid(row=0, column=5)
		self.lbl_SocketsAvailable.grid(row=0, column=6)
		self.lbl_NumTables.grid(row=0, column=7)
		
		self.tablesShown = []
		"""Visualization panel for tables"""
		self.panel_Tables = tk.Frame(self.window)
		self.panel_Tables.grid(row=1, column=0)
		self.window.mainloop()
		
	def prepare4Business(self, numTables=2):
		self.sock4PortQuery = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock4PortQuery.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock4PortQuery.bind((self.address, 65432))
		self.sock4PortQuery.listen()
	
		ports = [65433 + i for i in range(2 * numTables)]
		socks = [socket.socket(socket.AF_INET, socket.SOCK_STREAM) for i in range(2 * numTables)]
		for port, sock in zip(ports, socks):
			print("Port", port, "on IP address", self.address, "opened")
			sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			sock.bind((self.address, port))
			sock.listen()
			self.socketsAvailable.append((port, sock))
			
		print("*****Available ports:")
		for port, sock in self.socketsAvailable: print("\tPort {}  Socket ID {}".format(port, sock.fileno()))
		
	def placeTables(self):
		self.lbl_SocketsAvailable["text"] = "可用端口数：%d" % len(self.socketsAvailable)
		self.lbl_NumTables["text"] = "运行中对战数：%d" % len(self.tablesShown)
		for i, table in enumerate(self.tablesShown):
			table.grid(row=i%10, column=int(i/10))
			
	def tellGuestAvailableTables(self, conn):
		if self.socketsAvailable:
			port1, sock1 = self.socketsAvailable.pop()
			port2, sock2 = self.socketsAvailable.pop()
			print("Returns available tables to client", b"Port available,%d"%port1)
			conn.sendall(b"Port available,%d"%port1)
			
			#The guest return the table ID it wants to reserve. Need to reserve a table for the guest.
			tableID_Requested = conn.recv(1024) #Any byte string
			if tableID_Requested.startswith(b"Request to Reserver/Join Table ID"):
				print("Received table ID from guest", tableID_Requested)
				tableID_Requested = tableID_Requested.split(b',')[1]
				print("Guest wants tableID:", tableID_Requested)
				if tableID_Requested in self.tables:
					table = self.tables[tableID_Requested]
					conns2Players = table.conns2Players
					if conns2Players[1] and conns2Players[2]: #If the table has two connections, that means two players playing at that table
						conn.sendall(b"Use another Table ID")
						conn.close()
					#There is one guest waiting at the table. Do some modifications
					elif conns2Players[1] or conns2Players[2]:
						sockfor2ndGuest = table.socks2Players[2] if conns2Players[1] else table.socks2Players[1]
						addr, port = sockfor2ndGuest.getsockname()
						conn.sendall(b"Join Reserved Table via Port||%d"%port)
				#No one has reserved this table yet. Assign sockets to a table
				else:#The table ID reserved is available.
					self.tables[tableID_Requested] = table = Table(self)
					self.tablesShown.append(table)
					self.placeTables()
					#Assign two sockets for the table
					if numpy.random.randint(2):
						table.socks2Players, name1, name2 = {1: sock1, 2: sock2}, "Port %d Thread"%port1, "Port %d Thread"%port2
					else:
						table.socks2Players, name1, name2 = {1: sock2, 2: sock1}, "Port %d Thread"%port2, "Port %d Thread"%port1
					threading.Thread(target=table.portStart, args=(1,), name=name1, daemon=True).start()
					threading.Thread(target=table.portStart, args=(2,), name=name2, daemon=True).start()
					print("Table assigned with sockets 1: {}, 2: {}".format(table.socks2Players[1].fileno(), table.socks2Players[2].fileno()))
					conn.sendall(b"Table can be Reserved")
		else:
			print("Has no available tables left")
			conn.sendall(b"No Ports Left")
		
		conn.close()
		
	#Whenever a socket connects to this query port, server tells it the availability of table ports
	def openBusiness(self):
		self.prepare4Business(int(self.entry_NumTables.get()))
		self.lbl_SocketsAvailable["text"] = "可用端口数：%d" % len(self.socketsAvailable)
		self.btn_Start.config(bg="cyan", text="正在运行")
		while True:
			conn, addr = self.sock4PortQuery.accept()
			print("Got a request to connect", conn, addr)
			self.tellGuestAvailableTables(conn)
			
	def stopRunning(self):
		self.window.destroy()
		quit()
		
	def freeaTable(self, table):
		print("Freeing a table", table)
		for tableID, t in self.tables.items():
			if t == table:
				table.keepRunning = False
				for sock in table.socks2Players.values():
					if sock:
						port = sock.getsockname()[1]
						sock.close()
						sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
						sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
						sock.bind((self.address, port))
						sock.listen()
						self.socketsAvailable.append((port, sock))
				self.tablesShown.remove(table)
				table.destroy()
				del self.tables[tableID]
				self.placeTables()
				break
				
				
if __name__ == "__main__":
	InnKeeper()