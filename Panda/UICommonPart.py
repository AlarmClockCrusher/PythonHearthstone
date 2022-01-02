from direct.gui.DirectGui import *
from direct.showbase.ShowBase import ShowBase
from direct.task import Task

from Panda.CustomWidgets import *
from Parts.Game import Game
from Parts.Code2CardList import *
from HS_Cards.AcrossPacks import TheCoin, SilverHandRecruit, Rexxar, SteadyShot
from HS_Cards.Core import FieryWarAxe, RampantGrowth_Option

w, h = 1440, 800
configVars = """
win-size 1440 800
window-title Hearthstone Simulator
clock-mode limited
clock-frame-rate 45
text-use-harfbuzz true
framebuffer-multisample 1
multisamples 1
"""

# the last two lines are for antialiasing to work with multisample
loadPrcFileData('', configVars)


CamPos_Z = 51.5
pos_OffBoardTrig_1, pos_OffBoardTrig_2 = (-10, -1.8, 10), (-10, 5, 10)
pos_ClassSelectionTray = (3.6, 9.8, 0.15)

#Class2HeroDict is {"Demon Hunter": Illidan}
cardPool, cardPool_All, RNGPools, ClassCards, NeutralCards, Class2HeroDict = makeCardPool()

"""Loading Interface and DeckBuilder"""
class Btn_Door:
	def __init__(self, GUI):
		self.GUI, self.i = GUI, 0
		self.np = GUI.loadaRetexturedModel(modelName="Models\\UIModels\\Door.glb", textureName="Models\\UIModels\\Door.png",
										   pos=(0, 0, 41.5))
		textNodePath, textNode = makeText(self.np, "Door", valueText='', pos=(-1.5, 0.6, 0.05),
				 scale=0.23, color=white, font=self.GUI.getFont(GUI.lang))

		self.textNodePaths = [textNodePath]
		for i in range(1, 8):
			self.textNodePaths.append((np := textNodePath.copyTo(self.np)))
			np.setPos(-1.5 if i < 4 else 1.5, 0.6-0.6*(i%4), 0.05)

	def addaText(self, text):
		self.textNodePaths[self.i].node().setText(text)
		self.i += 1

#The button can cycle through a list/tuple of funcs, and the texts will change accordingly
#funcs and texts can be empty lists/tuples, but they must have equal length
class Btn_Button: #removeAfter=True will only remove the btn nodepath. Other removeNode need to be in the func
	def __init__(self, GUI, np, removeAfter=False, func=None):
		self.GUI, self.np, self.removeAfter, self.func = GUI, np, removeAfter, func

	def rightClick(self): pass
	def leftClick(self):
		#print("Button clicked. NP: {}".format(self.np))
		if self.func: self.func(self)
		if self.removeAfter: self.np.removeNode()
		else:
			scale_0 = self.np.getScale()[0]
			Sequence(LerpScaleInterval(self.np, duration=0.15, scale=1.2*scale_0),
					   LerpScaleInterval(self.np, duration=0.15, scale=scale_0)).start()

class Btn_NotificationPanel:
	def __init__(self, GUI, text, acknowledge=True):
		self.GUI, np = GUI, GUI.modelTemplates["NotificationPanel"].copyTo(GUI.render)
		np.find("text_TextNode").node().setText(text)
		if GUI.np_Notification: GUI.np_Notification.removeNode()
		GUI.np_Notification = np
		if acknowledge:
			GUI.addaButton("Button_Yes", "Yes", parent=np, pos=(0, -2.3, 0), func=lambda btn: np.removeNode())
		else:
			GUI.addaButton("Button_Yes", "Yes", parent=np, pos=(-4.3, -2.3, 0), func=lambda btn: np.removeNode())
			GUI.addaButton("Button_No", "No", parent=np, pos=(4.3, -2.3, 0), func=lambda btn: np.removeNode())
		np.setPos(0, 0, 10)


class DeckBuilderHandler:
	x_offset_Deck2, pos_Start, pos_Standby = 8, (-1, 0, 2.2), (-1, 35, 2.2)
	def __init__(self, GUI, for1P):
		self.GUI, self.for1P, self.root = GUI, for1P, GUI.render.attachNewNode("Model2Keep_DeckBuilder")
		self.innStatusRoot = self.root.attachNewNode("Inn Status Root") #Only used in Online Game
		self.innStatusRoot.setPos(-9.9, 1.7, 0.1) #Top left corner. Top right corner is (3.7, 3.6, 0.1)
		self.collectionRoot = self.manaTrayRoot = self.classTray = self.expansionIconRoot = None
		self.cardPages, self.cardNPsShown, self.pageNum, self.Class2Display = {}, [], 0, "Demon Hunter"
		self.expansionsSelected, self.manasSelected = [], []
		self.y_offset_Collection, self.x0_Collection, self.y1_Collection, self.y2_Collection = -2, -12.7, 2.5, -6
		self.x0_Deck, self.y0_Deck = 11.9, 10.39
		self.leftArrow = self.rightArrow = self.root_DeckTray1 = self.root_DeckTray2 = None
		self.deckID, self.decks = 1, {1:[], 2:[]}
		self.heroes = {1: Rexxar, 2: Rexxar}
		self.deckMax = 30
		self.load()
	"""Tree structure after loading"""
	#render/Model2Keep_DeckBuilder
		#Collection Tray
			#Plane|cNode
		#Mana Tray Root
			#NP_ManaTray
			#mana_TextNode  x7
			#NP_Mana  x7
				#cNode|1~7+
		#ClassSelectionTray
			#PanelFrame|HeroFrame|cardImage|HeroFrame_2|cardImage_2|Panel
			#NP_ClassSelectIcon  x11
				#ClassIcon|cNode
			#Expansion Icons Root
				#NP_ExpansionSelectIcon  x7
					#Circile|cNode
		#DeckTray1&2
			#NP_DeckTray
				#Plane|ClassIcon
			#Btn_Select
	 			#Btn_Yes|cNode|Text_TextNode
			#Btn_Import
	 			#Btn_Small|cNode|Text_TextNode
			#Btn_Clear
	 			#Btn_Yes|cNode|Text_TextNode
			#NP_CardinDeck  x30
				#cNode|mana_TextNode|count_TextNode|cardName_TextNode|cardImage|Label|Legendary
		#Collection Root
			#NP_Card  x8
		#Left&RightArrow
			#Plane|cNode
		#Conn Info Root (Empty)
		#Inn Status Root (Empty)

	def load(self):
		GUI, root = self.GUI, self.root
		root.setPos(type(self).pos_Start)
		loadModel, loadTexture = GUI.loader.loadModel, GUI.loader.loadTexture
		collectionTexture = loadTexture("Models\\UIModels\\CollectionTray.png")

		collectionTray = loadModel("Models\\UIModels\\CollectionTray.glb")
		collectionTray.name = "Collection Tray"
		collectionTray.reparentTo(root)
		collectionTray.setTexture(collectionTray.findTextureStage('*'), collectionTexture, 1)
		(cNode := CollisionNode("cNode")).addSolid(CollisionBox((0, 0, -0.2), 30, 15, 0.1))
		collectionTray.attachNewNode(cNode)#.show()

		"""Mana selection tray and add the mana crystals to it"""
		self.manaTrayRoot = manaTrayRoot = root.attachNewNode("Mana Tray Root")
		manaTrayRoot.setPos(-15, 11, 0)
		(manaTray := loadModel("Models\\UIModels\\ManaSelectionTray.glb")).reparentTo(self.manaTrayRoot)
		manaTray.name = "NP_ManaTray"
		manaTray.setTexture(manaTray.findTextureStage('*'), collectionTexture, 1)

		manaModel = loadModel("Models\\UIModels\\Mana.glb")
		manaModel.name = "NP_Mana"
		makeText(manaModel, "mana", '', pos=(0, -0.25, 0.1), scale=0.9, color=white, font=self.GUI.getFont())
		manaModel.setTexture(manaModel.findTextureStage('*'), loadTexture("Models\\UIModels\\EmptyMana.png"), 1)
		(cNode := CollisionNode("cNode")).addSolid(CollisionSphere(0, 0, 0, 0.6))
		manaModel.attachNewNode(cNode)#.show()
		for mana in range(8):
			manaModel.setPos(1.40662*mana, 0, 0.1)
			(model := manaModel.copyTo(manaTrayRoot)).wrtReparentTo(self.manaTrayRoot)
			model.setPythonTag("btn", Btn_ManaSelection(GUI=GUI, np=model, deckBuilder=self, mana=mana))
			model.find("mana_TextNode").wrtReparentTo(self.manaTrayRoot)

		"""Class Selection Tray. Also add class selection icons to it"""
		self.classTray = classTray = GUI.modelTemplates["Own Table"].copyTo(root)
		classTray.name = "NP_ClassSelectionTray"
		classTray.find("Panel").setColor(collectionTrayColor)
		cardImage = classTray.find("cardImage")
		cardImage.setTexture(cardImage.findTextureStage("*"), loadTexture("Images\\HeroesandPowers\\Illidan.png"), 1)
		classTray.setPos(pos_ClassSelectionTray)
		x, y, z = -4.15, 1.2, 0
		(icon := loadModel("Models\\UIModels\\ClassIcon.glb")).setScale(1.1)
		icon.name = "NP_ClassSelectIcon"
		(cNode := CollisionNode("cNode")).addSolid(CollisionSphere(0, 0, 0, 0.45))
		icon.attachNewNode(cNode)#.show()
		for i, Class in enumerate(ClassesandNeutral):
			icon.setTexture(icon.findTextureStage('*'), loadTexture("Models\\UIModels\\Icon_%s.png" % Class), 1)
			(model := icon.copyTo(classTray)).setPos(x+1.2*(i%5), y-1.2*int(i/5), z)
			model.setPythonTag("btn", Btn_ClassSelection(GUI=GUI, np=model, deckBuilder=self, Class=Class))
		"""Expansion Selection Tray to it"""
		(expansionIconRoot := root.attachNewNode("Expansion Icons Root")).setPos(-14.8, 8.7, 0.05)

		(model := loadModel("Models\\UIModels\\ExpansionIcon.glb")).setScale(1.5)
		model.name = "NP_ExpansionSelectIcon"
		model.setTexture(model.findTextureStage('0'), self.GUI.textures["UIDesign"], 1)
		(cNode := CollisionNode("cNode")).addSolid(CollisionSphere(0, 0, 0, 0.55))
		model.attachNewNode(cNode)#.show()
		for i, expansion in enumerate(("CORE", "BLACK_TEMPLE", "SCHOLOMANCE", "DARKMOON_FAIRE",
									   "THE_BARRENS", "STORMWIND", "ALTERAC_VALLEY", "DIY_Cards")):
			(copyModel := model.copyTo(expansionIconRoot)).setPos(1.8 * (i % 7), -1.8 * int(i / 7), 0)
			(ts := TextureStage('Icon')).setTexcoordName('1')
			copyModel.setTexture(ts, loadTexture("Images\\%s\\Icon.png" % expansion), 1)
			copyModel.setPythonTag("btn", Btn_ExpansionSelection(np=copyModel, deckBuilder=self, expansion=expansion))
		self.expansionIconRoot = expansionIconRoot

		"""Place the deck trays right to the collection area"""
		self.root_DeckTray1, self.root_DeckTray2 = root.attachNewNode("DeckTray1"), root.attachNewNode("DeckTray2")
		self.root_DeckTray1.setPos(0, 0, 0.02)
		self.root_DeckTray2.setPos(type(self).x_offset_Deck2, 0, 0.02)
		plane = (deckTray := loadModel("Models\\UIModels\\DeckTray.glb")).find("Plane")
		plane.setTexture(plane.findTextureStage("*"), loadTexture("Models\\UIModels\\CollectionTray.png"), 1)
		deckTray.name = "NP_DeckTray"
		deckTray.reparentTo(self.root_DeckTray1)
		deckTray.copyTo(self.root_DeckTray2)
		self.root_DeckTray2.setColor(grey)  # Always set the 2nd tray to dark first

		root_DeckTray, deckID = self.root_DeckTray1, 1
		self.GUI.addaButton("Button_Yes", "Btn_Select", parent=root_DeckTray, pos=(12, 11.95, 0),
							func=lambda btn: self.toggleDeck2Edit(1)).setScale(0.7)
		self.GUI.addaButton("Button_Small", "Btn_Import", parent=root_DeckTray, pos=(15.6, 10.5, 0),
							text="Import", func=lambda btn: self.getDeckCodefromInput(1)).setScale(0.9)
		self.GUI.addaButton("Button_Small", "Btn_Clear", parent=root_DeckTray, pos=(15.6, 9.7, 0),
							text="Clear", func=lambda btn: self.clearDeck(1)).setScale(0.9)
		root_DeckTray, deckID = self.root_DeckTray2, 2
		self.GUI.addaButton("Button_Yes", "Btn_Select", parent=root_DeckTray, pos=(12, 11.95, 0),
							func=lambda btn: self.toggleDeck2Edit(2)).setScale(0.7)
		self.GUI.addaButton("Button_Small", "Btn_Import", parent=root_DeckTray, pos=(15.6, 10.5, 0),
							text="Import", func=lambda btn: self.getDeckCodefromInput(2)).setScale(0.9)
		self.GUI.addaButton("Button_Small", "Btn_Clear", parent=root_DeckTray, pos=(15.6, 9.7, 0),
							text="Clear", func=lambda btn: self.clearDeck(2)).setScale(0.9)

		"""Define the Start Game Button"""
		if self.for1P: self.GUI.addaButton("Button_Start", "StartGame", root, pos=(5.3, 5.1, 0), 
											func=self.GUI.startGame)
		"""Arrows to turn pages in the collection"""
		self.leftArrow = self.GUI.addaButton("Button_LeftArrow", "LeftArrow", root,
											 pos=(-15.2, -2.8+self.y_offset_Collection, 0), func=lambda btn: self.lastPage())
		self.rightArrow = self.GUI.addaButton("Button_LeftArrow", "RightArrow", root,
											 pos=(6.7, -2.8+self.y_offset_Collection, 0), func=lambda btn: self.nextPage())
		self.rightArrow.setHpr(180, 0, 0)
		self.updateDeck(ID=1, deckCode=DefaultDeckCode1)
		if self.for1P: self.updateDeck(ID=2, deckCode=DefaultDeckCode2)
		self.collectionRoot = self.root.attachNewNode("Collection Root")
		self.showCollection()

	def toggleDeck2Edit(self, deckID):
		self.deckID = deckID
		self.root_DeckTray1.setColor(white if deckID == 1 else grey)
		self.root_DeckTray2.setColor(grey if deckID == 1 else white)

	def clearDeck(self, deckID):
		if deckID == self.deckID:
			self.decks[deckID] = []
			root_DeckTray = self.root_DeckTray1 if deckID == 1 else self.root_DeckTray2
			for child in root_DeckTray.getChildren():
				if child.name == "NP_CardinDeck": child.removeNode()

	def getDeckCodefromInput(self, deckID):
		self.clearDeck(deckID)
		root_DeckTray = self.root_DeckTray1 if deckID == 1 else self.root_DeckTray2
		root_DeckTray.find("Btn_Import").find("Text_TextNode").node().setText(self.GUI.txt("Import"))
		with open("Deck Codes.txt", 'r', encoding="utf-8") as InputFile:
			try:
				InputFile.readline()
				if line := InputFile.readline(): deckCode1 = line
				else: raise IndexError
				InputFile.readline()
				InputFile.readline()
				if line := InputFile.readline(): deckCode2 = line
				else: raise IndexError
				if deckID == 1: self.updateDeck(ID=1, deckCode=deckCode1)
				else: self.updateDeck(ID=2, deckCode=deckCode2)
			except IndexError:
				resetDeckCodeFile(self.GUI.lang)
				msg = "Your deck code/input format is incorrect\n'Deck Codes.txt' has been reset with default deck"
				Btn_NotificationPanel(self.GUI, text=self.GUI.txt(msg))
				return

	def manaCorrect(self, card, manasSelected): #True if manasSelect is empty
		return not manasSelected or (card.mana in manasSelected) or (7 in manasSelected and card.mana >= 7)

	def expansionCorrect(self, index, expansionsSelected): #True if expansionsSelected is empty
		return not expansionsSelected or index.split('~')[0] in expansionsSelected

	def searchMatches(self, search, card): #card is a class, not object
		lower = search.lower()
		return (lower in card.name.lower() or lower in card.description.lower()) or search in card.name_CN

	def showCollection(self, recalcPages=True):
		GUI, root = self.GUI, self.collectionRoot
		if self.Class2Display == "Neutral": cards = NeutralCards
		else: cards = ClassCards[self.Class2Display]
		#Remove the current page of cardNPs shown and clear for next display
		for np in self.cardNPsShown: np.removeNode()
		self.cardNPsShown = []
		#Only Turning pages won't recalc card pages
		if recalcPages:
			self.cardPages, self.pageNum, i = {}, 0, 0
			for card in cards:
				if self.manaCorrect(card, self.manasSelected) and self.expansionCorrect(card.index, self.expansionsSelected):
					add2ListinDict(card, self.cardPages, int(i/8))
					i += 1
		if self.cardPages:
			self.pageNum = min(len(self.cardPages)-1, self.pageNum)
			for i, card in enumerate(self.cardPages[self.pageNum]):
				pos = (self.x0_Collection + 5.5 * (i % 4), (self.y2_Collection if i > 3 else self.y1_Collection) + self.y_offset_Collection, 0.05)
				(nodepath := genCard(GUI, card(GUI.Game, 1), isPlayed=False, pos=pos, scale=1.1)[0]).reparentTo(root)
				self.cardNPsShown.append(nodepath)
			if self.pageNum < 1: self.leftArrow.stash()
			else: self.leftArrow.unstash()
			if self.pageNum >= len(self.cardPages) - 1: self.rightArrow.stash()
			else: self.rightArrow.unstash()
		else: Btn_NotificationPanel(GUI, GUI.txt("No card match"), acknowledge=True)

	def lastPage(self):
		self.pageNum -= 1
		self.showCollection(recalcPages=False)

	def nextPage(self):
		self.pageNum += 1
		self.showCollection(recalcPages=False)

	def addaCard(self, card):
		deck = self.decks[self.deckID]
		numCopies = deck.count(card)
		if len(deck) >= self.deckMax: text = self.GUI.txt("Your deck is full")
		elif card.index.startswith("SV_") and numCopies >= 2:
			text = self.GUI.txt("Can't have >3 copies in the same deck")
		elif not card.index.startswith("SV_") and "~Legendary" in card.index and numCopies >= 1:
			text = self.GUI.txt("At most 1 copy of Legendary card in the deck")
		elif not card.index.startswith("SV_") and "~Legendary" not in card.index and numCopies > 1:
			text = self.GUI.txt("Can't have >2 copies in the same deck")
		else: text = ''
		if text: Btn_NotificationPanel(GUI=self.GUI, text=self.GUI.txt(text))
		else:
			deck.append(card)
			self.heroes[self.deckID] = Class2HeroDict[decideClassofaDeck(deck)]
			self.updateDeck(self.deckID)

	def updateDeck(self, ID, deckCode=''):
		GUI, model_CardInDeck = self.GUI, self.GUI.modelTemplates["CardinDeck"]

		if ID == 1: rt, offSet = self.root_DeckTray1, 0
		else: rt, offSet = self.root_DeckTray2, type(self).x_offset_Deck2
		if deckCode:
			deck, deckCorrect, self.heroes[ID] = parseDeckCode(deckCode, "Demon Hunter", Class2HeroDict,
															   cardPool_All=cardPool_All)
			if not deckCorrect: Btn_NotificationPanel(GUI=GUI, text=GUI.txt("Deck %d incorrect"%ID))
			else: self.decks[ID] = deck
		cardCounts, cards2Models = {card: self.decks[ID].count(card) for card in self.decks[ID]}, {}
		cards = numpy.array(list(cardCounts.keys())) #cards本身是不重复的
		cards_Sorted = cards[numpy.array([card.mana for card in cards]).argsort()] #Sort the cards based on cost
		inDeckDrawn = [] #Get all the card in deck models drawn
		for child in rt.getChildren():
			if child.name == "NP_CardinDeck": inDeckDrawn.append(child)
		#Establish mapping cardType --> model
		for model in inDeckDrawn[:]:
			if (card := model.getPythonTag("btn").card) in cards_Sorted: cards2Models[card] = model
			else:
				inDeckDrawn.remove(model)
				model.removeNode()
		for i, card in enumerate(cards_Sorted):
			pos = (self.x0_Deck, self.y0_Deck - i * 0.77, 0.05)
			if card in cards2Models: model = cards2Models[card]
			else:
				cards2Models[card] = (model := model_CardInDeck.copyTo(rt))
				model.setPythonTag("btn", Btn_CardinDeck(GUI=GUI, np=model, deckBuilder=self, ID=ID, card=card))
				inDeckDrawn.append(model)
			count = cardCounts[card]
			model.find("count_TextNode").node().setText(str(count) if count > 1 else '')
			model.setPos(pos)
		if self.heroes[ID]:
			icon = rt.find("NP_DeckTray").find("ClassIcon")
			icon.setTexture(icon.findTextureStage("*"),
							GUI.loader.loadTexture("Models\\UIModels\\Icon_%s.png"%self.heroes[ID].Class), 1)

class Btn_ExpansionSelection:
	def __init__(self, np, deckBuilder, expansion):
		self.np, self.deckBuilder, self.expansion = np, deckBuilder, expansion
		self.selected = False

	def leftClick(self):
		self.selected = not self.selected
		self.np.setScale(1.8 if self.selected else 1.5)
		expansions = self.deckBuilder.expansionsSelected
		if not self.selected: removefrom(self.expansion, expansions)
		elif self.expansion not in expansions: expansions.append(self.expansion)
		self.deckBuilder.showCollection()

class Btn_ClassSelection:
	def __init__(self, GUI, np, deckBuilder, Class):
		self.GUI, self.np, self.deckBuilder, self.Class = GUI, np, deckBuilder, Class

	def rightClick(self): pass
	def leftClick(self):
		cardImage = self.np.getParent().find("cardImage")
		if self.Class != "Neutral":
			cardImage.setTexture(cardImage.findTextureStage('*'),
								 self.GUI.loader.loadTexture("Images\\HeroesandPowers\\%s.png"%Classes2HeroeNames[self.Class]), 1)

		self.deckBuilder.Class2Display = self.Class
		if self.Class in Class2HeroDict: #"Neutral doesn't have a Hero name
			self.deckBuilder.heroes[self.deckBuilder.deckID] = Class2HeroDict[self.Class]
		self.deckBuilder.showCollection()

class Btn_ManaSelection:
	def __init__(self, GUI, np, deckBuilder, mana):
		self.GUI, self.np, self.deckBuilder, self.mana = GUI, np, deckBuilder, mana
		self.selected = False
		np.find("mana_TextNode").node().setText(str(mana))

	def rightClick(self): pass
	def leftClick(self):
		self.selected = not self.selected
		texture = self.GUI.loader.loadTexture("Models\\UIModels\\%s.png" % ("Mana" if self.selected else "EmptyMana"))
		self.np.setTexture(self.np.findTextureStage("*"), texture, 1)

		manas = self.deckBuilder.manasSelected
		if not self.selected: removefrom(self.mana, manas)
		elif self.mana not in manas: manas.append(self.mana)
		self.deckBuilder.showCollection()


class Btn_CardinDeck:
	def __init__(self, GUI, np, deckBuilder, ID, card):
		self.GUI, self.np, self.deckBuilder, self.ID, self.card = GUI, np, deckBuilder, ID, card
		self.cardEntity = card(GUI.Game, 1)
		if "~Legendary" not in card.index: self.np.find("Legendary").hide()
		self.np.find("mana_TextNode").node().setText(str(card.mana))
		self.np.find("cardName_TextNode").node().setText(card.name_CN if GUI.lang == "CN" else card.name)
		cardImage = self.np.find("cardImage")
		cardImage.setTexture(cardImage.findTextureStage('*'),
							 GUI.loader.loadTexture(findFilepath(card(None, 1))), 1)

	def rightClick(self): pass
	def leftClick(self):
		self.deckBuilder.decks[self.ID].remove(self.card)
		self.deckBuilder.updateDeck(self.ID)



"""Common UI components for 1P and Online"""
class Panda_UICommon(ShowBase):
	def __init__(self, disableMouse=True):
		super().__init__()
		# simplepbr.init(max_lights=4)
		self.render.setAntialias(AntialiasAttrib.MAuto)  # All nodepaths under render to have antialiasing
		# nodePath.setAntialias(AntialiasAttrib.MMultisample) #If you only want one nodepath to have antialiasing
		self.cam.name, self.camera.name = "Model2Keep_Cam", "Model2Keep_Camera"
		if disableMouse: self.disableMouse()
		self.WAIT, self.FUNC = Wait, Func
		self.SEQUENCE, self.PARALLEL = Sequence, Parallel
		self.LERP_Pos, self.LERP_PosHpr, self.LERP_PosHprScale = LerpPosInterval, LerpPosHprInterval, LerpPosHprScaleInterval
		self.genCard = genCard

		"""Attributes to store info"""
		self.ID, self.boardID, self.showEnemyHand = 1, True, ''
		self.btnBeingDragged = self.arrow = self.crosshair = self.np_Fatigue = self.np_YourTurnBanner = self.btnBoard = self.btnTurnEnd = None
		self.playedCards = [] #当手牌中的卡牌被打出后录入此列表，在clearDrawnCards和打出手牌时处理。
		self.np_CardZoomIn = self.np_Notification = None
		# Game play info related
		self.posMulligans = None
		self.mulliganStatus = {1: [0, 0, 0], 2: [0, 0, 0, 0]}
		self.step = ""
		self.subject = self.discover = None
		self.target = []
		self.pos = self.choice = -1
		self.stage = -2
		# self.stage defines how cards respond to clicking.
		# -2:尚未进入游戏，还在组建套牌，-1:起手调试中，0:游戏中的闲置状态，还未选取任何目标，1:抉择中，2:选择了subject，3:发现选择中
		self.btns2Remove = []

		# Animation related
		self.gamePlayQueue = []
		self.seqHolder, self.seq2Play, self.seqReady = [], None, False

		self.Game = Game(self)

		# Online Pvp related
		self.sock_Recv = self.sock_Send = None
		self.waiting4Server, self.msg_Exit, self.timer = False, '', 60

		# Models, textures and fonts
		self.textures, self.modelTemplates, self.manaModels, self.forGameTex = {}, {}, {}, {}
		self.cardTex = {category: {} for category in ("Minion", "Weapon", "Spell", "Power", "Hero", "Common")}
		self.lang = "CN"
		self.fonts = {"EN": self.loader.loadFont("Models\\OpenSans-Bold.ttf"),
					"CN": self.loader.loadFont("Models\\NotoSansSC-Regular.otf"), }
		self.minionZones, self.heroZones, self.handZones, self.deckZones = {}, {}, {}, {}
		self.deckBuilder = self.historyZone = None

		self.cTrav = self.collHandler = self.raySolid = None
		self.loadingUI = Btn_Door(self)
		self.relocateCamera()

		threading.Thread(target=self.prepareTexturesandModels, daemon=True).start()
		threading.Thread(target=self.keepExecutingGamePlays, name="GameThread", daemon=True).start()

	def getFont(self, lang='EN'):
		if lang not in self.fonts: return self.fonts["EN"]
		else: return self.fonts[lang]

	def txt(self, s):
		if self.lang == "EN": return s
		try: return translateTable[s][self.lang]
		except KeyError: return s

	def loadaRetexturedModel(self, modelName, textureName, pos=(0, 0, 0), hpr=(0, 0, 0), scale=1, parent=None):
		(model := self.loader.loadModel(modelName)).reparentTo(parent if parent else self.render)
		model.setTexture(model.findTextureStage('*'), self.loader.loadTexture(textureName), 1)
		model.setPosHpr(pos, hpr)
		model.setScale(scale)
		return model

	def addaButton(self, buttonName, name, parent, pos, text='', textColor=black, removeAfter=False, func=None):
		(np := self.modelTemplates[buttonName].copyTo(parent)).setPos(pos)
		np.name = name
		if textnp := np.find("Text_TextNode"):
			textnp.node().setText(self.txt(text))
			textnp.node().setTextColor(textColor)
		np.setPythonTag("btn", Btn_Button(self, np, removeAfter=removeAfter, func=func))
		return np

	def prepareTexturesandModels(self):
		loadModel, loadTexture = self.loader.loadModel, self.loader.loadTexture
		t1 = datetime.now()
		#Load the textures
		self.textures = {"cardBack": loadTexture("Models\\CardBack.png"),
						 "UIDesign": loadTexture("Models\\UIModels\\UIDesign.png"),
						 "Button_Concede": loadTexture("Models\\UIModels\\Button_Concede.png"),
						 "Button_Option": loadTexture("Models\\UIModels\\Button_Option.png"),
						 }
		for category in ("Minion", "Spell", "Weapon", "Hero", "Power"):
			self.textures["stats_" + category] = loadTexture("Models\\%sModels\\Stats.png"%category)
		for Class in ("Hunter", "Mage", "Paladin", "Rogue"):
			self.textures["Secret_" + Class] = loadTexture("Models\\HeroModels\\Secret_%s.png" % Class)
		for Class in ("Demon Hunter,Hunter", "Demon Hunter", "Druid", "Hunter", "Mage", "Paladin",
					  "Priest", "Rogue", "Shaman", "Warlock", "Warrior", "Warrior,Paladin", "Neutral"):
			self.textures["weapon_" + Class] = loadTexture("Models\\WeaponModels\\WeaponCards\\%s.png" % Class)
		self.loadingUI.addaText("基础贴图加载完成")
		#Load texCards for Game
		#self.forGameTex["TurnStart_Banner"] = makeTexCard(self, filePath="TexCards\\ForGame\\TurnStartBanner.egg",
		#												  pos=(0, 0, -0.3), scale=15, aspectRatio=332 / 768,
		#												  name="Tex2Keep_TurnStart_Banner")[0]
		#self.forGameTex["TurnStart_Particles"] = makeTexCard(self, filePath="TexCards\\ForGame\\TurnStartParticles.egg",
		#													 pos=(0, 0, -1), scale=18,
		#													 name="Tex2Keep_TurnStart_Particles")[0]
		for name in ("SecretHunter", "SecretMage", "SecretPaladin", "SecretRogue"):
			self.forGameTex[name] = makeTexCard(self, filePath="TexCards\\ForGame\\%s.egg"%name,
												name="Tex2Keep_"+name, getSeqNode=False)[0]
		self.loadingUI.addaText("基础特效加载完成")
		#Load models for triggers, and then various category of cards
		for iconName, scale in zip(("Trigger", "Deathrattle", "Lifesteal", "Poisonous", "SpecTrig", "Hourglass"),
									(1.1, 3, 1.2, 1.3, 0.63, None)):
			np_Icon = loadModel("Models\\%s.glb" % iconName)
			np_Icon.setTexture(np_Icon.findTextureStage('0'),
							   loadTexture("Models\\%s.png"%iconName), 1)
			self.modelTemplates[iconName] = np_Icon
			np_Icon.name = iconName + "_Icon"
			if iconName == "Hourglass":
				makeText(np_Icon, "Trig Counter", '', pos=(-0.02, -0.18, 0.04), scale=0.6, font=self.getFont(), color=white)
			else: makeTexCard(self, "TexCards\\Shared\\%s.egg" % iconName, pos=(0, 0, 0), scale=scale, parent=np_Icon)
		# np_Icon is now: Trigger_Icon
		# Trigger|TexCard
		# Trigger|Trigger
		# Hourglass_Icon
		# Hourglass|Trig Counter_TextNode
		# Hourglass|Hourglass
		# Get the templates for the cards, they will load the trig icons and status tex cards
		self.modelTemplates["Dormant"] = self.modelTemplates["Minion"] = loadCard(self, SilverHandRecruit(self.Game, 1))
		self.loadingUI.addaText("随从模型加载完成")
		self.modelTemplates["Spell"] = loadCard(self, TheCoin(self.Game, 1))
		self.loadingUI.addaText("法术模型加载完成")
		self.modelTemplates["Weapon"] = loadCard(self, FieryWarAxe(self.Game, 1))
		self.loadingUI.addaText("武器模型加载完成")
		self.modelTemplates["Hero"] = loadCard(self, Rexxar(self.Game, 1))
		self.loadingUI.addaText("英雄模型加载完成")
		self.modelTemplates["Power"] = loadCard(self, SteadyShot(self.Game, 1))
		self.loadingUI.addaText("英雄技能模型加载完成")
		#Load models for various purposes
		self.modelTemplates["Option"] = loadCard(self, RampantGrowth_Option(None))
		self.modelTemplates["HeroZoneTrig"] = loadHeroZoneTrig(self)
		self.modelTemplates["Trade"] = model = loadModel("Models\\Trade.glb")
		model.name = "Trade"
		model.find("Trade").setTexture(model.findTextureStage("*"), loadTexture("Models\\Trade.png"), 1)
		#Button templates
		for name, colBoxSize in zip(("Button_Small", "Button_InGame", "Button_Option", "Button_Concede",
									 "Button_Yes", "Button_No"),
									((0.7, 0.4, 0.1), (1, 0.6, 0.1), (1.7, 0.45, 0.1), (1.7, 0.45, 0.1),
									 (3.3, 0.9, 0.1), (3.3, 0.9, 0.1))):
			self.modelTemplates[name] = btn = loadModel("Models\\UIModels\\%s.glb"%name)
			texture = self.textures[name if name in ("Button_Concede", "Button_Option") else "UIDesign"]
			btn.setTexture(btn.findTextureStage("*"), texture, 1)
			x, y, z = colBoxSize
			(cNode := CollisionNode("cNode")).addSolid(CollisionBox((0, 0, 0), x, y, z))
			btn.attachNewNode(cNode)#.show()
			makeText(btn, 'Text', "", pos=(0, -0.15, 0.06), scale=0.45, color=black, font=self.getFont(self.lang))
		self.modelTemplates["Button_Start"] = btn = loadModel("Models\\UIModels\\Button_Start.glb")
		btn.setTexture(btn.findTextureStage("*"), loadTexture("Models\\UIModels\\StartGame.png"), 1)
		(cNode := CollisionNode("cNode")).addSolid(CollisionSphere((0, 0, 0), 1.6))
		btn.attachNewNode(cNode)#.show()
		self.modelTemplates["Button_LeftArrow"] = btn = loadModel("Models\\UIModels\\Button_Arrow.glb")
		btn.setTexture(btn.findTextureStage("*"), loadTexture("Models\\UIModels\\Arrow.png"), 1)
		(cNode := CollisionNode("cNode")).addSolid(CollisionSphere(0, 0, 0, 0.7))
		btn.attachNewNode(cNode)#.show()

		# Card in deck label template when building decks
		self.modelTemplates["CardinDeck"] = model = loadModel("Models\\UIModels\\CardinDeck.glb")
		model.name = "NP_CardinDeck"
		makeText(model, "mana", valueText='', pos=(-2.26, -0.23, 0.1), scale=0.7, color=white, font=self.getFont())
		makeText(model, "count", valueText='', pos=(2.6, -0.16, 0.12), scale=0.5, color=white, font=self.getFont())
		makeText(model, "cardName", valueText='', pos=(-1.85, -0.1, 0.05), scale=0.4, color=white,
				 font=self.getFont(self.lang))[1].setAlign(TextNode.ABoxedLeft)
		model.setTexture(model.findTextureStage('*'), self.textures["UIDesign"], 1)
		(cNode := CollisionNode("cNode")).addSolid(CollisionBox((0.2, 0, 0), 2.6, 0.3, 0.1))
		model.attachNewNode(cNode)#.show()
		# Notification panel template
		self.modelTemplates["NotificationPanel"] = model = loadModel("Models\\UIModels\\NotificationPanel.glb")
		makeText(model, "text", valueText='', pos=(0, 0, 0.05),
				 scale=0.5, color=white, font=self.getFont(self.lang))
		model.setTexture(model.findTextureStage('*'), self.textures["UIDesign"], 1)
		#ClassSelectionTray。更多的模型需要在双人模式的prepareDeckBuilderPanel中补全
		self.modelTemplates["Own Table"] = tray = loadModel("Models\\UIModels\\OwnTable.glb")
		tray.name = "NP_OwnTable"
		texture_HeroFrame = loadTexture("Models\\HeroModels\\Stats.png")
		trayFrame, heroFrame, heroFrame_2 = tray.find("PanelFrame"), tray.find("HeroFrame"), tray.find("HeroFrame_2")
		trayFrame.setTexture(trayFrame.findTextureStage('*'),
							 loadTexture("Models\\UIModels\\CollectionTray.png"), 1)
		heroFrame.setTexture(heroFrame.findTextureStage('*'), texture_HeroFrame, 1)
		heroFrame_2.setTexture(heroFrame_2.findTextureStage('*'), texture_HeroFrame, 1)
		# Only show the hero1 icon at the beginning
		for child in tray.getChildren():
			if child.name not in ("PanelFrame", "HeroFrame", "cardImage", "Panel"): child.hide()

		self.loadingUI.addaText("其他模型加载完成")
		#After load card models, load deck panel, game board, cancel the loading UI
		self.loadBackground()
		self.prepareDeckBuilderPanel()
		self.loadingUI.np.removeNode()
		self.init_CollisionSetup()
		threading.Thread(target=self.startLoadingTexCard, daemon=True).start()
		self.taskMgr.add(self.mainTaskLoop, "Task_MainLoop")
		self.accept("mouse1", self.mouse1_Down)
		self.accept("mouse1-up", self.mouse1_Up)
		self.accept("mouse3", self.mouse3_Down)
		self.accept("mouse3-up", self.mouse3_Up)

		t2 = datetime.now()
		print("Time needed to load", datetime.timestamp(t2) - datetime.timestamp(t1))

	def startLoadingTexCard(self):
		for category in ("Minion", "Weapon", "Spell", "Power", "Hero"):
			for name, posScale in tableTexCards[category].items():
				if name not in self.cardTex[category]:
					if category == "Hero": filepath = "TexCards\\ForHeroes\\%s.egg" % name
					else: filepath = "TexCards\\For%ss\\%s.egg" % (category, name)
					self.cardTex[category][name] = makeTexCard(self, filepath, pos=posScale[1], scale=posScale[0], name=name)[0]
		for name, posScale in tableTexCards["Common"].items():
			if name not in self.cardTex["Common"]:
				self.cardTex[category][name] = makeTexCard(self, "TexCards\\Shared\\%s.egg"%name,
														   pos=posScale[1], scale=posScale[0], name=name)[0]

	def prepareDeckBuilderPanel(self): pass

	# Load the board, turnEndButton, manaModels and arrow
	def loadBackground(self):
		if not self.btnBoard:  # Loaded models can be reused
			plane = self.loader.loadModel("Models\\BoardModels\\Background.glb")
			#plane.setTexture(plane.findTextureStage('*'),
			#				 self.loader.loadTexture("Models\\BoardModels\\%s.png" % self.boardID), 1)
			plane.name = "Model2Keep_Board"
			plane.reparentTo(self.render)
			plane.setPos(0, 0, 1)
			(cNode := CollisionNode("cNode")).addSolid(CollisionBox((0, 0.4, -0.2), 14.5, 7.5, 0.2))
			plane.attachNewNode(cNode)#.show()
			self.btnBoard = Btn_Board(self, plane)
			plane.setPythonTag("btn", self.btnBoard)
		else:
			self.btnBoard.np.setTexture(self.btnBoard.np.findTextureStage('*'),
										self.loader.loadTexture("Models\\BoardModels\\%s.png" % self.boardID), 1)
		# Load the turn end button
		if not self.btnTurnEnd:
			turnEnd = self.loader.loadModel("Models\\BoardModels\\TurnEndButton.glb")
			turnEnd.reparentTo(self.render)
			turnEnd.name = "Model2Keep_TurnEndBtn"
			turnEnd.setPos(TurnEndBtn_Pos)
			(cNode := CollisionNode("cNode")).addSolid(CollisionBox((0, 0, 0), 2, 1, 0.2))
			turnEnd.attachNewNode(cNode)#.show()
			self.btnTurnEnd = Btn_TurnEnd(self, turnEnd)
			turnEnd.setPythonTag("btn", self.btnTurnEnd)

		# The fatigue model to show when no more card to draw
		if not self.np_Fatigue:
			self.np_Fatigue = self.loader.loadModel("Models\\BoardModels\\Fatigue.glb")
			self.np_Fatigue.setTexture(self.np_Fatigue.findTextureStage('0'),
									   self.loader.loadTexture("Models\\BoardModels\\Fatigue.png"), 1)
			self.np_Fatigue.name = "Model2Keep_Fatigue"
			self.np_Fatigue.reparentTo(self.render)
			self.np_Fatigue.setPos(4, 0, 0)
			makeText(self.np_Fatigue, "Fatigue", valueText='1', pos=(-0.03, -1.3, 0.1),
					 scale=1, color=red, font=self.getFont())

		if not self.np_YourTurnBanner:
			self.np_YourTurnBanner = self.loader.loadModel("Models\\BoardModels\\YourTurnBanner.glb")
			self.np_YourTurnBanner.name = "Model2Keep_YourTurnBanner"
			self.np_YourTurnBanner.setTexture(self.np_YourTurnBanner.findTextureStage("*"),
											  self.loader.loadTexture("Models\\BoardModels\\ForBanner.png"), 1)
			self.np_YourTurnBanner.reparentTo(self.render)

		if not self.arrow:
			self.arrow = model = self.loader.loadModel("Models\\Arrow.glb")
			model.setTexture(model.findTextureStage('0'), self.loader.loadTexture("Models\\Arrow.png"), 1)
			model.reparentTo(self.render)
			model.name = "Model2Keep_Arrow"
			model.hide()

		if not self.crosshair:
			self.crosshair = model = self.loader.loadModel("Models\\Crosshair.glb")
			model.setTexture(model.findTextureStage('0'), self.loader.loadTexture("Models\\Arrow.png"), 1)
			model.reparentTo(self.render)
			model.name = "Model2Keep_Crosshair"
			model.hide()

		if not self.manaModels:
			for name in ("Mana", "EmptyMana", "LockedMana", "OverloadedMana"):
				model = self.loader.loadModel("Models\\BoardModels\\Mana.glb")
				model.name = "Model2Keep_" + name
				model.reparentTo(self.render)
				model.setTexture(model.findTextureStage('*'),
								 self.loader.loadTexture("Models\\BoardModels\\%s.png" % name), 1)
				self.manaModels[name] = [model]
				for i in range(9):
					self.manaModels[name].append(model.copyTo(self.render))

	def relocateCamera(self):
		self.camLens.setFov(51.1, 27.5)
		self.cam.setPosHpr(0, 0, CamPos_Z, 0, -90, 0)
		props = WindowProperties()
		props.setSize(w, h)
		self.win.requestProperties(props)

	def getDegreeDistance_fromCoors(self, x_0, y_0, x_1, y_1):
		distance = numpy.sqrt((x_1 - x_0) ** 2 + (y_1 - y_0) ** 2)
		degree = 180 * numpy.arccos((x_1 - x_0) / distance) / numpy.pi
		if y_1 < y_0: degree = 360 - degree
		return degree - 90, distance

	"""Handle animation of game display and mulligan. To be invoked by both Run_1PGame and Run_OnlineGame"""
	def initGameDisplay(self):
		for ID in (1, 2):
			self.deckZones[ID].draw(len(self.Game.Hand_Deck.decks[ID]), len(self.Game.Hand_Deck.hands[ID]))
			self.heroZones[ID].drawMana(self.Game.Manas.manas[ID], self.Game.Manas.manasUpper[ID],
										self.Game.Manas.manasLocked[ID], self.Game.Manas.manasOverloaded[ID])
			self.heroZones[ID].placeCards()

	def initMulliganDisplay(self, for1P):
		self.handZones = {1: HandZone(self, 1), 2: HandZone(self, 2)}
		self.minionZones = {1: MinionZone(self, 1), 2: MinionZone(self, 2)}
		self.heroZones = {1: HeroZone(self, 1), 2: HeroZone(self, 2)}
		self.historyZone = HistoryZone(self)
		if not self.deckZones:
			self.deckZones = {1: DeckZone(self, 1), 2: DeckZone(self, 2)}
		elif not for1P:
			self.deckZones[self.ID].changeSide(self.ID)
			self.deckZones[3 - self.ID].changeSide(3 - self.ID)

		self.mulliganStatus = {1: [0, 0, 0], 2: [0, 0, 0, 0]}  # 需要在每次退出和重新进入时刷新
		self.stage = -1
		self.initGameDisplay()
		self.addaButton("Button_InGame", "StartMulligan", self.render, pos=(0, 0, 10) if for1P else (0, -4, 10),
						removeAfter=True, func=self.initMulligan)

		# Draw the animation of mulligan cards coming out of the deck
		if for1P: sides, Y_1, Y_2 = (1, 2), -3.3, 6
		else: sides, Y_1, Y_2 = (self.ID,), 1.5, 1.5
		self.posMulligans = {1: [(-7, Y_1, 10), (0, Y_1, 10), (7, Y_1, 10)],
							 2: [(-8.25, Y_2, 10), (-2.75, Y_2, 10), (2.75, Y_2, 10), (8.25, Y_2, 10)]}
		for ID in sides: self.initMulligan_OutofDeck(ID)

		for child in self.render.getChildren():
			if "2Keep" not in child.name: print("After initGame, left in render:", child.name, type(child))

		print("Own sock_Recv&sock_Send is", self.sock_Recv, self.sock_Send)

	def initMulligan(self, btn): pass

	def initMulligan_OutofDeck(self, ID):
		deckZone, handZone, i = self.deckZones[ID], self.handZones[ID], 0
		pos_0, hpr_0 = deckZone.pos, (90, 90, 0)
		cards2Mulligan = self.Game.mulligans[ID]
		mulliganBtns = []
		for card, pos, hpr, scale in zip(cards2Mulligan, [pos_0]*len(cards2Mulligan), [hpr_0]*len(cards2Mulligan),
										 [1]*len(cards2Mulligan)):
			mulliganBtns.append(genCard(self, card, isPlayed=False, pos=pos, hpr=hpr, scale=scale)[1])
		for btn, pos in zip(mulliganBtns, self.posMulligans[ID]):
			Sequence(Wait(0.4 + i * 0.4),
					 LerpPosHprScaleInterval(btn.np, duration=0.5, pos=pos, hpr=(0, 0, 0), scale=1)).start()
			i += 1

	def replaceMulligan_PrepSeqHolder(self, addCoin, for1P, ID):
		# At this point, the Coin is added to the Game.mulligans[2]
		if addCoin: genCard(self, card=self.Game.mulligans[2][-1], isPlayed=False, pos=(13.75, 6 if for1P else 1.5, 10))

		para = Parallel()
		for ID in (1, 2) if for1P else (ID,):
			posMulligans = self.posMulligans[ID]
			pos_DeckZone, hpr_0 = self.deckZones[ID].pos, (90, 90, 0)
			for i, card in enumerate(self.Game.mulligans[ID]):
				if not card.btn:  # 把替换后新摸到的牌画在牌库位置并添加运动到调度位置的动画
					np, btn = genCard(self, card, isPlayed=False, pos=pos_DeckZone, hpr=hpr_0, scale=1)
					para.append(LerpPosHprScaleInterval(np, duration=0.5, pos=posMulligans[i], hpr=(0, 0, 0), scale=1))
		if for1P:
			self.seqHolder = [Sequence(para, Wait(1))]
			self.seqReady = False
		else: para.start()

	# 在决定完手牌中的牌以及它们的可能变形之后，添加它们的变形动画和移入手牌区动画
	def mulligan_TransformandMoveCards2Hand(self, cardsChanged, cardsNew):
		handZone_1, handZone_2, HD = self.handZones[1], self.handZones[2], self.Game.Hand_Deck
		seq = self.seqHolder[-1]

		seq.append(Func(self.deckZones[1].draw, len(HD.decks[1]), len(HD.hands[1])))
		seq.append(Func(self.deckZones[2].draw, len(HD.decks[2]), len(HD.hands[2])))
		seq.append(Wait(0.4))
		seq.append(Parallel(handZone_1.placeCards(False), handZone_2.placeCards(False)))
		if cardsChanged: seq.append(Func(handZone_1.transformHands([card.btn for card in cardsChanged], cardsNew)))

	"""Animation control setup"""
	def keepExecutingGamePlays(self):
		while True:
			if self.gamePlayQueue:
				self.gamePlayQueue.pop(0)()
				self.cancelSelection()
			time.sleep(0.02)

	def highlightTargets(self, legalTargets):
		game = self.Game
		for ID in (1, 2):
			for card in game.minions[ID] + game.Hand_Deck.hands[ID] + [game.heroes[ID]]:
				card.btn.np.setColor(white if card in legalTargets else grey)

	def resetCardColors(self):
		game = self.Game
		for ID in (1, 2):
			for card in game.minions[ID] + game.Hand_Deck.hands[ID] + [game.heroes[ID]]:
				if card and card.btn and card.btn.np:
					card.btn.np.setColor(white)
				else: print("Reset color fail", card, card.btn)

	def resetSubTarColor(self, subject=None, target=None):
		seq = self.seqHolder[-1]
		if subject:  # If subject not given, leave self.subject and its color unchanged
			if self.subject and self.subject.btn: seq.append(Func(self.subject.btn.setBoxColor, transparent))
			self.subject = subject
			if subject.btn: seq.append(Func(subject.btn.setBoxColor, yellow))
		if self.target:  # 先取消当前的所有target颜色显示，之后重新根据target显示
			for obj in self.target:
				if obj.btn: seq.append(Func(obj.btn.setBoxColor, transparent))
			self.target = []
		if target:
			self.target = target = list(target) if isinstance(target, (list, tuple)) else [target]
			for obj in target:
				if obj.btn: seq.append(Func(obj.btn.setBoxColor, pink))
		if subject or target: seq.append(Wait(0.15))

	# 游戏在逻辑结算完毕之后会直接先进行一次各卡牌的颜色处理，从而让玩家在打出一张牌之后马上知道场上已有的卡牌的状态
	# 在一些目标指向过程中可以改变subject和target的颜色，从而指示目标的变化
	# GUI在一次操作的动画流程即将结束时也会进行一次处理，从而让玩家知道所有新出现的卡牌的状态
	def decideCardColors(self):
		game = self.Game
		for card in game.Hand_Deck.hands[1] + game.Hand_Deck.hands[2]:
			card.effCanTrig()
			card.checkEvanescent()
		curTurn = game.turn
		for ID in (1, 2):
			# 双人对战过程中对方的牌不展示的情况下不显示可选框，其他情况下均显示
			if self.sock_Send:
				showCardColor = ID == curTurn and (ID == self.ID or self.showEnemyHand)
			else:
				showCardColor = ID == curTurn
			canTrade = game.Manas.manas[ID] > 0 and game.Hand_Deck.decks[ID]
			for card in game.Hand_Deck.hands[ID]:
				if card.btn:
					card.btn.setBoxColor(card.btn.decideColor() if showCardColor else transparent)
					if "~Tradeable" in card.index and (np_Trade := card.btn.np.find("Trade")):
						box = np_Trade.find("box")
						if showCardColor and canTrade:
							box.show()
							box.setColor(green)
						else: box.hide()
			for card in game.minions[ID]:
				if card.btn: card.btn.setBoxColor(card.btn.decideColor() if showCardColor else transparent)
			hero, power = game.heroes[ID], game.powers[ID]
			if hero.btn: hero.btn.setBoxColor(hero.btn.decideColor() if showCardColor else transparent)
			if power.btn: power.btn.setBoxColor(power.btn.decideColor() if showCardColor else transparent)
		self.btnTurnEnd.changeDisplay(jobDone=curTurn == self.ID and not game.morePlaysPossible())

	"""Animation details"""
	# Card/Hand animation
	def putaNewCardinHandAni(self, card):
		genCard(self, card, isPlayed=False, onlyShowCardBack=self.need2Hide(card))
		self.handZones[card.ID].placeCards()

	def cardReplacedinHand_Refresh(self, card):
		genCard(self, card, isPlayed=False, onlyShowCardBack=self.need2Hide(card))
		self.handZones[card.ID].placeCards()

	def transformAni(self, target, newCard, onBoard):
		if not isinstance(target, (list, tuple)): target, newCard = (target,), (newCard,)
		self.seqHolder[-1].append(para := Parallel())
		for obj, newObj in zip(target, newCard):
			if obj.btn and obj.btn.np:
				np_New, btn_New = genCard(self, newObj, isPlayed=onBoard, pickable=True, onlyShowCardBack=obj.btn.onlyCardBackShown)
				para.append(Func(self.replaceaNPwithNewCard, obj.btn.np, btn_New, not self.need2Hide(obj), 1.9 if onBoard else 2.3))

	def replaceaNPwithNewCard(self, npOld, btnNew, mist=True, mistScale=1.9):
		nodePathNew = btnNew.np
		texCard, seqNode = makeTexCard(self, filePath="TexCards\\Shared\\TransformMist.egg",
									   pos=(0, 0, 0.2), scale=mistScale, parent=nodePathNew)
		Sequence(Func(seqNode.play), Wait(0.75), Func(texCard.removeNode)).start()
		nodeOld, nodeNew = npOld.node(), nodePathNew.node()
		oldChildren = npOld.getChildren()
		nodeNew.replaceNode(nodeOld)
		for child in oldChildren:
			child.removeNode()
		btnNew.np = npOld
		npOld.setPythonTag("btn", btnNew)

	def transformAni_inHand(self, target, newCard):
		texCard = seqNode = None
		if not self.need2Hide(target):
			texCard, seqNode = makeTexCard(self, filePath="TexCards\\Shared\\TransformMist.egg",
										   pos=(0, 0, 0.2), scale=2.3)
		seq_Holder = self.seqHolder[-1]
		if target.category == newCard.category:
			newCard.btn = target.btn
			if texCard:
				seq_Holder.append(Sequence(Func(texCard.reparentTo, target.btn.np), Func(seqNode.play), Wait(0.05),
										   Func(target.btn.changeCard, newCard, False)))
				seq_Holder.append(Func(Sequence(Wait(0.75), Func(texCard.removeNode)).start))
			else:
				seq_Holder.append(Func(target.btn.changeCard, newCard, False))
			target.btn = None
		else:
			np_New, btn_New = genCard(self, newCard, isPlayed=False, pickable=True,
									  onlyShowCardBack=target.btn.onlyCardBackShown)
			np_Old = target.btn.np
			if texCard:
				seq_Holder.append(Sequence(Func(texCard.reparentTo, np_Old), Func(seqNode.play), Wait(0.05),
										   Func(np_New.reparentTo, np_Old), Wait(0.75),
										   Func(np_New.wrtReparentTo, self.render),
										   Func(np_Old.removeNode))
								  )
			else:
				seq_Holder.append(Func(np_New.reparentTo, np_Old), Func(np_New.wrtReparentTo, self.render),
								  Func(np_Old.removeNode))

	def transformAni_onBoard(self, target, newCard):
		newCard.btn = target.btn
		texCard = seqNode = None
		if target.category == newCard.category and target.category in ("Minion", "Weapon"):
			texCard, seqNode = makeTexCard(self, filePath="TexCards\\Shared\\TransformMist.egg",
										   pos=(0, 0, 0.2), scale=1.9)
		seq_Holder = self.seqHolder[-1]
		if not texCard:
			seq_Holder.append(Func(target.btn.changeCard, newCard, True))
		else:
			seq_Holder.append(Sequence(Func(texCard.reparentTo, target.btn.np), Func(seqNode.play), Wait(0.05),
									   Func(target.btn.changeCard, newCard, True)))
			seq_Holder.append(Func(Sequence(Wait(0.65), Func(texCard.removeNode)).start))
		target.btn = None

	# 因为可以结算的时候一般都是手牌已经发生了变化，所以只能用序号来标记每个btn了
	# linger is for when you would like to see the card longer before it vanishes
	def cardsLeaveHandAni(self, cards, ID=0, enemyCanSee=True, linger=False):
		handZone, para, btns2Destroy = self.handZones[ID], Parallel(), [card.btn for card in cards]
		# 此时需要离开手牌的牌已经从Game.Hand_Deck.hands里面移除,手牌列表中剩余的就是真实存在还在手牌中的
		for btn, card in zip(btns2Destroy, cards):
			seq, nodePath = Sequence(), btn.np
			if enemyCanSee and btn.onlyCardBackShown:
				seq.append(Func(btn.changeCard, card, False, False))
			x, y, z = nodePath.getPos()
			if not -9 < y < 9:
				y = DiscardedCard1_Y if self.ID == btn.card.ID else DiscardedCard2_Y
				seq.append(LerpPosHprInterval(nodePath, duration=0.3, pos=(x, y, z), startHpr=(0, 0, 0), hpr=(0, 0, 0)))
				seq.append(Wait(0.6))
			# 如果linger为True就留着这张牌的显示，到之后再处理
			if not linger: seq.append(Func(nodePath.detachNode))
			para.append(seq)
		handZone.placeCards()
		self.seqHolder[-1].append(para)

	def hand2BoardAni(self, card):
		ID = card.ID
		handZone, minionZone = self.handZones[ID], self.minionZones[ID]
		# At this point, minion has been inserted into the minions list. The btn on the minion won't change. It will simply change "isPlayed"
		ownMinions = self.Game.minions[ID]
		x, y, z = posMinionsTable[minionZone.y][len(ownMinions)][ownMinions.index(card)]
		# Must be first set to isPlayed=True, so that ensuing statChangeAni can correctly respond
		if card.btn.onlyCardBackShown:
			self.seqHolder[-1].append(Func(card.btn.changeCard, card, False, True))
		card.btn.isPlayed = True  # Must be first set to isPlayed=True, so that ensuing statChangeAni can correctly respond
		card.btn.reassignBox()
		seq = Sequence(LerpPosHprScaleInterval(card.btn.np, duration=0.25, pos=(x, y, z + 5), hpr=(0, 0, 0), startHpr=(0, 0, 0),
									scale=scale_Minion),
						Func(card.btn.changeCard, card, True),
						Parallel(minionZone.placeCards(False), handZone.placeCards(False)), name="Hand2Board Ani")
		self.seqHolder[-1].append(seq)

	def board2HandAni(self, card):
		handZone, minionZone = self.handZones[card.ID], self.minionZones[card.ID]
		# At this point, minion has been extracted from the minion lists
		ownMinions, ownHands = self.Game.minions[card.ID], self.Game.Hand_Deck.hands[card.ID]
		x, y, z = card.btn.np.getPos()
		onlyShowCardBack = self.need2Hide(card)
		card.btn.isPlayed = True  # Must be first set to isPlayed=True, so that ensuing statChangeAni can correctly respond
		card.btn.reassignBox()
		seq = Sequence(LerpPosInterval(card.btn.np, duration=0.25, pos=Point3(x, y, z + 5)),
					   Wait(0.15), Func(card.btn.changeCard, card, False, True, onlyShowCardBack), Wait(0.2),
					   Func(self.deckZones[self.ID].draw, len(self.Game.Hand_Deck.decks[self.ID]), len(ownHands)),
					   Parallel(handZone.placeCards(False), minionZone.placeCards(False)),
					   name="Board 2 hand ani")
		self.seqHolder[-1].append(seq)

	def deck2BoardAni(self, card):
		ID = card.ID
		nodePath, btn = genCard(self, card,
								isPlayed=False)  # place these cards at pos(0, 0, 0), to be move into proper position later
		# At this point, minion has been inserted into the minions list. The btn on the minion won't change. It will simply change "isPlayed"
		deckZone, minionZone = self.deckZones[ID], self.minionZones[ID]
		ownMinions = self.Game.minions[ID]
		x, y, z = posMinionsTable[minionZone.y][len(ownMinions)][ownMinions.index(card)]
		deckPos = Deck1_Pos if ID == self.ID else Deck2_Pos
		# The minion must be first set to isPlayed=True, so that the later statChangeAni can correctly respond
		btn.isPlayed = True
		card.btn.reassignBox()
		sequence = Sequence(Func(deckZone.draw, len(card.Game.Hand_Deck.decks[ID]), len(self.Game.Hand_Deck.hands[ID])),
							LerpPosHprScaleInterval(nodePath, duration=0.3, startPos=deckPos, startHpr=hpr_Deck,
													startScale=deckScale,
													pos=(x, y, z + 5), hpr=(0, 0, 0), scale=scale_Minion),
							Wait(0.2), Func(btn.changeCard, card, True),
							minionZone.placeCards(False),
							name="Deck to board Ani")
		self.seqHolder[-1].append(sequence)

	def revealaCardfromDeckAni(self, ID, index, bingo):
		card = self.Game.Hand_Deck.decks[ID][index]
		deckZone = self.deckZones[card.ID]
		pos_Pause = DrawnCard1_PausePos if self.ID == card.ID else DrawnCard2_PausePos
		nodePath, btn = genCard(self, card, isPlayed=False)  # the card is preloaded and positioned at (0, 0, 0)
		sequence = Sequence(Func(nodePath.setPosHpr, deckZone.pos, (90, 90, 0)),
							Func(deckZone.draw, len(self.Game.Hand_Deck.decks[card.ID]),
								 len(self.Game.Hand_Deck.hands[card.ID])),
							LerpPosHprScaleInterval(btn.np, duration=0.4, pos=pos_Pause, hpr=(0, 0, 0), scale=1,
													blendType="easeOut"),
							Wait(0.6)
							)
		if bingo:
			sequence.append(LerpScaleInterval(nodePath, duration=0.2, scale=1.15))
			sequence.append(LerpScaleInterval(nodePath, duration=0.2, scale=1))
		sequence.append(
			LerpPosHprInterval(nodePath, duration=0.4, pos=deckZone.pos, hpr=(90, 90, 0), blendType="easeOut"))
		btn.add2Queue_NullifyBtnNodepath(sequence)  # 一般只有把卡牌洗回牌库时会有nodepath消失再出现的可能性
		sequence.append(Wait(0.2))
		self.seqHolder[-1].append(sequence)

	# Amulets and dormants also count as minions
	def removeMinionorWeaponAni(self, card):
		if not (card.btn and card.btn.np): return
		# At this point, minion/dormant/weapon has left the containing list
		self.seqHolder[-1].append(Func(card.btn.np.detachNode))
		if card.category in ("Minion", "Dormant", "Amulet"):
			self.minionZones[card.ID].placeCards()

	# 直接出现，而不是从手牌或者牌库中召唤出来
	def summonAni(self, card):
		# At this point, minion has been inserted into the minions list
		genCard(self, card, isPlayed=True)
		self.minionZones[card.ID].placeCards()
		self.seqHolder[-1].append(Wait(0.1))

	def weaponEquipAni(self, card):
		nodePath, btn = genCard(self, card, isPlayed=True)
		x, y, z = self.heroZones[card.ID].weaponPos
		self.seqHolder[-1].append(
			LerpPosHprInterval(nodePath, duration=0.3, startPos=(x, y + 0.2, z + 5), pos=(x, y, z), hpr=(0, 0, 0)))

	# 需要把secret原本的icon移除，然后加入卡牌
	def secretDestroyAni(self, secrets, enemyCanSee=True):
		if secrets:
			heroZone = self.heroZones[secrets[0].ID]
			heroPos = heroZone.heroPos
			para_Remove = Parallel()
			for nodePath in [secret.btn.np for secret in secrets]: para_Remove.append(Func(nodePath.removeNode))
			self.seqHolder[-1].append(para_Remove)

			if enemyCanSee:
				para_Show, para_RemoveCards, nps2Emerge, interval = Parallel(), Parallel(), [], 8
				for secret in secrets:
					nps2Emerge.append(self.addCard(secret, pos=(heroPos[0], heroPos[1], 0), pickable=False)[0])
				leftMostX = interval * (len(secrets) - 1) / 2
				for i, nodePath in enumerate(nps2Emerge):
					para_Show.append(
						LerpPosHprScaleInterval(nodePath, duration=0.3, hpr=(0, 0, 0), startScale=0.1, scale=1,
												startPos=heroPos, pos=(leftMostX + interval * i, 1, ZoomInCard_Z)))
				for nodePath in nps2Emerge: para_RemoveCards.append(Func(nodePath.removeNode))
				self.seqHolder[-1].append(para_Show)
				self.seqHolder[-1].append(para_RemoveCards)
			heroZone.placeSecrets()

	def drawCardAni_LeaveDeck(self, card):
		deckZone = self.deckZones[card.ID]
		pos_Pause = DrawnCard1_PausePos if self.ID == card.ID else DrawnCard2_PausePos
		nodePath, btn = genCard(self, card, isPlayed=False, onlyShowCardBack=self.need2Hide(card))
		self.seqHolder[-1].append(Sequence(
			Func(deckZone.draw, len(self.Game.Hand_Deck.decks[card.ID]), len(self.Game.Hand_Deck.hands[card.ID])),
			Func(nodePath.setPosHpr, deckZone.pos, (90, 90, 0)),
			LerpPosHprScaleInterval(nodePath, duration=0.4, pos=pos_Pause, hpr=(0, 0, 0), scale=1, blendType="easeOut"),
			Wait(0.8))
								  )

	def drawCardAni_IntoHand(self, oldCard, newCard):
		btn = oldCard.btn
		handZone = self.handZones[oldCard.ID]
		if btn.card != newCard:
			print("Drawn card is changed", newCard)
			handZone.transformHands([btn], [newCard])
		handZone.placeCards()
		self.seqHolder[-1].append(Func(self.deckZones[oldCard.ID].draw, len(self.Game.Hand_Deck.decks[newCard.ID]),
									   len(self.Game.Hand_Deck.hands[newCard.ID])))

	def millCardAni(self, card):
		deckZone = self.deckZones[card.ID]

		pos_Pause = DrawnCard1_PausePos if self.ID == card.ID else DrawnCard2_PausePos
		nodePath, btn = genCard(self, card, isPlayed=False)
		interval = LerpPosHprScaleInterval(nodePath, duration=0.4, startPos=deckZone.pos, pos=pos_Pause,
										   startHpr=(90, 90, 0), hpr=(0, 0, 0), scale=1, blendType="easeOut")
		texCard, seqNode = makeTexCard(self, "TexCards\\ForGame\\Mill.egg", scale=27)
		self.seqHolder[-1].append(
			Sequence(interval, Func(texCard.setPos, pos_Pause[0], pos_Pause[1] - 1, pos_Pause[2] + 0.4),
					 Func(seqNode.play), Wait(0.5), Func(nodePath.removeNode), Wait(0.5), Func(texCard.removeNode)))

	def cardLeavesDeckAni(self, card, enemyCanSee=True, linger=False):
		deckZone = self.deckZones[card.ID]
		pos_Pause = DrawnCard1_PausePos if self.ID == card.ID else DrawnCard2_PausePos
		nodePath, btn = genCard(self, card, isPlayed=False)  # the card is preloaded and positioned at (0, 0, 0)
		sequence = Sequence(Func(nodePath.setPosHpr, deckZone.pos, (90, 90, 0)),
							Func(deckZone.draw, len(self.Game.Hand_Deck.decks[card.ID]),
								 len(self.Game.Hand_Deck.hands[card.ID])),
							LerpPosHprScaleInterval(btn.np, duration=0.4, pos=pos_Pause, hpr=(0, 0, 0), scale=1,
													blendType="easeOut"),
							Wait(0.6))
		if not linger: sequence.append(Func(nodePath.removeNode))
		self.seqHolder[-1].append(sequence)

	def shuffleintoDeckAni(self, cards, enemyCanSee=True):
		ID = cards[0].ID
		deckZone = self.deckZones[ID]
		para, btns = Parallel(), []
		leftMostPos = -(len(cards) - 1) / 2 * 5
		for i, card in enumerate(cards):
			num = len(cards) - i
			if (btn := card.btn) and (nodePath := card.btn.np):  # For cards that already have btns and nodepaths.
				seq = Sequence(Wait(0.15 * num + 0.3),
							   LerpPosHprInterval(nodePath, duration=0.25, pos=deckZone.pos, hpr=(90, 90, 0)))
			else:  # For cards that are newly created
				nodePath, btn = genCard(self, card, isPlayed=False, pickable=False,
										onlyShowCardBack=not enemyCanSee and self.need2Hide(card))
				seq = Sequence(Func(nodePath.setPos, leftMostPos + 5 * i, 1.5, 8), Wait(0.15 * num + 0.3),
							   LerpPosHprInterval(nodePath, duration=0.2, pos=deckZone.pos, hpr=(90, 90, 0)))
			btn.add2Queue_NullifyBtnNodepath(seq)
			para.append(seq)

		self.seqHolder[-1].append(para)
		self.seqHolder[-1].append(
			Func(deckZone.draw, len(self.Game.Hand_Deck.decks[ID]), len(self.Game.Hand_Deck.hands[ID])))

	def wait(self, duration=0, showLine=False):
		pass

	def offsetNodePath_Wait(self, nodePath, duration=0.3, dx=0, dy=0, dz=0, dh=0, dp=0, dr=0, add2Queue=True):
		if add2Queue:
			self.seqHolder[-1].append(Func(self.offsetNodePath, nodePath, duration, dx, dy, dz, dh, dp, dr))
			self.seqHolder[-1].append(Wait(duration))
		else: return self.offsetNodePath(nodePath, duration, dx, dy, dz, dh, dp, dr)

	def offsetNodePath(self, np, duration=0.3, dx=0, dy=0, dz=0, dh=0, dp=0, dr=0):
		x, y, z = np.getPos()
		h, p, r = np.getHpr()
		Sequence(LerpPosHprInterval(np, duration=duration, pos=(x+dx, y+dy, z+dz), hpr=(h+dh, p+dp, r+dr))).start()

	def moveNodePath2_wrt_Wait(self, np_2Move, np_Ref, duration=0.3, dx=0, dy=0, dz=0, add2Queue=True):
		if add2Queue:
			self.seqHolder[-1].append(Func(self.moveNodePath2_wrt, np_2Move, np_Ref, duration, dx, dy, dz))
			self.seqHolder[-1].append(Wait(duration))
		else: return Sequence(Func(self.moveNodePath2_wrt, np_2Move, np_Ref, duration, dx, dy, dz), Wait(duration))

	def moveNodePath2_wrt(self, np_2Move, nodePath_Ref, duration, dx, dy, dz):
		x, y, z = nodePath_Ref.getPos()
		Sequence(LerpPosInterval(np_2Move, duration=duration, pos=(x+dx, y+dy, z+dz))).start()

	def attackAni_HitandReturn(self, subject, target):
		np_Subject, np_Target = subject.btn.np, target.btn.np
		if subject.category == "Minion":
			ownMinions = self.Game.minions[subject.ID]
			x_0, y_0, z_0 = posMinionsTable[self.minionZones[subject.ID].y][len(ownMinions)][ownMinions.index(subject)]
		else:
			x_0, y_0, z_0 = self.heroZones[subject.ID].heroPos
		seq = Sequence(self.moveNodePath2_wrt_Wait(np_Subject, np_Target, duration=0.17, add2Queue=False),
					   LerpPosInterval(np_Subject, duration=0.17, pos=(x_0, y_0, z_0 + 3)),
					   LerpPosInterval(np_Subject, duration=0.15, pos=(x_0, y_0, z_0)),
					   )
		self.seqHolder[-1].append(seq)

	def attackAni_Cancel(self, subject):
		if subject.category == "Minion":
			minionZone, ownMinions = self.minionZones[subject.ID], self.Game.minions[subject.ID]
			if subject not in ownMinions: return
			pos_Orig = posMinionsTable[minionZone.y][len(ownMinions)][ownMinions.index(subject)]
		else:
			pos_Orig = self.heroZones[subject.ID].heroPos

		self.seqHolder[-1].append(LerpPosInterval(subject.btn.np, duration=0.15, pos=pos_Orig))

	def battlecryAni(self, card):
		if card.btn:
			texCard, seqNode = makeTexCard(self, "TexCards\\For%ss\\Battlecry.egg" % card.category, pos=(0, 0.5, 0.03),
										   scale=6)
			texCard.reparentTo(card.btn.np)
			self.seqHolder[-1].append(
				Func(Sequence(Func(seqNode.play, 0, 32), Wait(32 / 24), Func(texCard.removeNode)).start))
			self.seqHolder[-1].append(Wait(20 / 24))

	def heroExplodeAni(self, entities):
		for keeper in entities:
			if keeper.btn:
				texCard, seqNode = makeTexCard(self, "TexCards\\ForHeroes\\Breaking.egg",
											   pos=(0, 0.2, 0.3), scale=5)
				texCard.reparentTo(keeper.btn.np)
				headPieces = self.loader.loadModel("Models\\HeroModels\\HeadPieces.glb")
				headPieces.reparentTo(self.render)
				headPieces.setTexture(headPieces.findTextureStage('*'),
									  self.loader.loadTexture(
										  "Images\\HeroesandPowers\\%s.png" % type(keeper).__name__), 1)
				x_0, y_0, z_0 = self.heroZones[keeper.ID].heroPos
				headPieces.setPos(x_0, y_0, z_0)
				para = Parallel()
				for child in headPieces.getChildren():
					x, y, z = child.getPos()
					vec = numpy.array([x, y + 3 * (-1 if y_0 > 0 else 1), z_0 + 5])
					x_pos, y_pos, z_pos = numpy.array([x_0, y_0, -5]) + vec * 60 / numpy.linalg.norm(vec)
					para.append(LerpPosInterval(child, duration=0.8, pos=(x_pos, y_pos, z_pos)))

				self.seqHolder[-1].append(Sequence(Func(seqNode.play, 0, 17), Wait(17 / 24),
												   Func(texCard.removeNode), Func(keeper.btn.np.removeNode),
												   Func(headPieces.setPos, x_0, y_0, z_0), para)
										  )

	def minionsDieAni(self, entities):
		para = Parallel()
		for keeper in entities:
			if keeper.btn: para.append(Func(keeper.btn.dimDown))
		self.seqHolder[-1].append(para)
		self.seqHolder[-1].append(Wait(0.3))

	def deathrattleAni(self, keeper):
		if keeper.btn:
			x, y, z = keeper.btn.np.getPos()
			texCard, seqNode = makeTexCard(self, "TexCards\\Shared\\Deathrattle.egg", pos=(x, y + 0.4, z + 0.3), scale=3.3)
			self.seqHolder[-1].append(Sequence(Func(seqNode.play), Wait(1.2), Func(texCard.removeNode)))

	def weaponPlayedAni(self, card):
		ID = card.ID
		handZone = self.handZones[ID]
		x, y, z = self.heroZones[ID].weaponPos
		card.btn.isPlayed = True  # The minion must be first set to isPlayed=True, so that the later statChangeAni can correctly respond
		sequence = Sequence(LerpPosHprScaleInterval(card.btn.np, duration=0.25, pos=(x, y + 0.2, z + 5), hpr=(0, 0, 0), scale=1),
							Func(card.btn.changeCard, card, True),
							Parallel(handZone.placeCards(False), LerpPosInterval(card.btn.np, duration=0.25, pos=(x, y, z)))
							)
		self.seqHolder[-1].append(sequence)

	def secretTrigAni(self, card): #Secret trigger twice will show the animation twice.
		if not (nodepath := card.btn.np): seq = Sequence()
		else: seq = Sequence(Func(self.offsetNodePath_Wait, nodepath, duration=0.15, dx=0.1, add2Queue=False),
							Func(self.offsetNodePath_Wait, nodepath, duration=0.15, dx=-0.2, add2Queue=False),
							Func(self.offsetNodePath_Wait, nodepath, duration=0.15, dx=0.1, add2Queue=False),
							Wait(0.3), Func(nodepath.removeNode)
							)
		scale_Max, scale_Min = (25, 1, 25 * 600 / 800), (1, 1, 1 * 600 / 800)
		texCard = self.forGameTex["Secret%s" % card.Class]
		seq.append(LerpPosHprScaleInterval(texCard, duration=0.3, pos=(0, 1, 9), hpr=(0, -90, 0), scale=scale_Max))
		seq.append(Wait(0.8))
		seq.append(LerpPosHprScaleInterval(texCard, duration=0.3, pos=(0, 0, 0), hpr=(0, -90, 0), scale=scale_Min))
		self.seqHolder[-1].append(seq)
		self.showOffBoardTrig(card)
		self.heroZones[card.ID].placeSecrets()

	def need2Hide(self, card):  # options don't have ID, so they are always hidden if the PvP doesn't show enemy hand
		return not self.showEnemyHand and self.sock_Send and (not hasattr(card, "ID") or card.ID != self.ID)

	def showOffBoardTrig(self, card, animationType="Curve", text2Show='', textY=-3, isSecret=False):
		if card:
			y = self.heroZones[card.ID].heroPos[1]
			# if card.btn and isinstance(card.btn, Btn_Card) and card.btn.np: nodePath, btn_Card = card.btn.np, card.btn
			nodePath, btn_Card = self.addCard(card, pos=(0, 0, 0), pickable=False, isUnknownSecret=isSecret and self.need2Hide(card))
			if text2Show:
				textNode = TextNode("Text Disp")
				textNode.setText(text2Show)
				textNode.setAlign(TextNode.ACenter)
				textNodePath = nodePath.attachNewNode(textNode)
				textNodePath.setPosHpr(0, textY, 1, 0, -90, 0)
			seq = self.seqHolder[-1] if self.seqHolder else Sequence()
			if animationType == "Curve":
				moPath = Mopath.Mopath()
				moPath.loadFile("Models\\BoardModels\\DisplayCurve_%s.egg" % ("Lower" if y < 0 else "Upper"))
				seq.append(MopathInterval(moPath, nodePath, duration=0.3))
				seq.append(Wait(1))
			elif animationType == "Appear":
				pos = pos_OffBoardTrig_1 if y < 0 else pos_OffBoardTrig_2
				seq.append(Func(nodePath.setPos, pos[0], pos[1], 0))
				seq.append(LerpPosHprScaleInterval(nodePath, duration=0.4, pos=pos, hpr=(0, 0, 0), startScale=0.3, scale=1))
				seq.append(Wait(0.7))
				seq.append(LerpScaleInterval(nodePath, duration=0.2, scale=0.2))
			else:  # typically should be ''
				seq.append(Func(nodePath.setPos, pos_OffBoardTrig_1 if y < 0 else pos_OffBoardTrig_2))
				seq.append(Wait(1))
			seq.append(Func(nodePath.removeNode))
			if not self.seqHolder: seq.start()

	def addCard(self, card, pos, pickable, isUnknownSecret=False, onlyShowCardBack=False, isPlayed=False):
		if card.category == "Option":
			nodePath, btn_Card = genOption(self, card, pos=pos, onlyShowCardBack=onlyShowCardBack)  # Option cards are always pickable
		else:
			btn_Orig = card.btn if card.btn and card.btn.np else None
			nodePath, btn_Card = genCard(self, card, pos=pos, isPlayed=isPlayed, pickable=pickable,
										 onlyShowCardBack=onlyShowCardBack, makeNewRegardless=True, isUnknownSecret=isUnknownSecret)
			if btn_Orig: card.btn = btn_Orig  # 一张牌只允许存有其创建伊始指定的btn，不能在有一个btn的情况下再新加其他的btn
		return nodePath, btn_Card

	# Targeting/AOE animations
	def targetingEffectAni(self, subject, target):
		return

	# Miscellaneous animations
	def turnEndButtonAni_FlipRegardless(self):
		interval = self.btnTurnEnd.np.hprInterval(0.4, (0, 180 - self.btnTurnEnd.np.get_p(), 0))
		self.seqHolder[-1].append(Func(self.btnTurnEnd.changeDisplay, False))
		self.seqHolder[-1].append(Func(interval.start))

	def turnEndButtonAni_Flip2RightPitch(self):
		p = 0 if self.ID == self.Game.turn else 180
		if self.btnTurnEnd.np.get_p() != p:
			interval = self.btnTurnEnd.np.hprInterval(0.4, (0, p, 0))
			self.seqHolder[-1].append(Func(interval.start))

	def turnStartAni(self):
		self.turnEndButtonAni_Flip2RightPitch()
		if self.ID != self.Game.turn: return
		#tex_Parts = self.forGameTex["TurnStart_Particles"]
		#tex_Banner = self.forGameTex["TurnStart_Banner"]
		#seqNode_Parts = tex_Parts.find("+SequenceNode").node()
		#seqNode_Banner = tex_Banner.find("+SequenceNode").node()
		#seqNode_Parts.pose(0)
		#seqNode_Banner.pose(0)
		#sequence_Particles = Sequence(Func(tex_Parts.setPos, 0, 1, 5), Func(seqNode_Parts.play, 0, 27), Wait(0.9),
		#							  Func(tex_Parts.setPos, 0, 0, 0))  # #27 returns to the begin
		#sequence_Banner = Sequence(
		#	LerpPosHprScaleInterval(tex_Banner, duration=0.2, pos=(0, 1, 6), hpr=(0, -90, 0), startScale=1,
		#							scale=(23, 1, 23 * 332 / 768)),
		#	Func(seqNode_Banner.play), Wait(1.2),
		#	LerpPosHprScaleInterval(tex_Banner, duration=0.2, pos=(0, 0, 0), hpr=(0, 0, 0), scale=(0.15, 0.15, 0.15))
		#	)
		#self.seqHolder[-1].append(Parallel(sequence_Particles, sequence_Banner))
		self.seqHolder[-1].append(Sequence(LerpPosHprScaleInterval(self.np_YourTurnBanner, duration=0.3, pos=(0, 0, 4), hpr=(0, 0, 0), startScale=0.3, scale=1),
											Wait(0.7),
											LerpPosHprScaleInterval(self.np_YourTurnBanner, duration=0.3, pos=(0, 0, 0), hpr=(0, 0, 0), scale=0.3))
								  )

	def usePowerAni(self, card):
		x, y, z = self.heroZones[card.ID].powerPos
		np = card.btn.np
		sequence = Sequence(LerpPosHprInterval(np, duration=0.2, pos=(x, y, z + 3), hpr=Point3(0, 0, 90)),
							LerpPosHprInterval(np, duration=0.2, pos=(x, y, z), hpr=Point3(0, 0, 180)))
		if card.ID == self.Game.turn and not card.chancesUsedUp():
			sequence.append(LerpPosHprInterval(np, duration=0.17, pos=(x, y, z + 3), hpr=(0, 0, 90)))
			sequence.append(LerpPosHprInterval(np, duration=0.17, pos=(x, y, z), hpr=(0, 0, 0)))
		self.seqHolder[-1].append(Func(sequence.start))

	"""Mouse click setup"""
	#The camera carries a CollisionNode that has a solid collision volume. Its nodepath is added to the CollisionTraverser.
	#When invoked, CollisionTraverser checks for collision added (Only between Collision Ray and other volumes)
	def init_CollisionSetup(self):
		self.cTrav, self.collHandler, self.raySolid = CollisionTraverser(), CollisionHandlerQueue(), CollisionRay()
		(cNode := CollisionNode("cNode")).addSolid(self.raySolid)
		(cNodePath_Picker := self.camera.attachNewNode(cNode))#.show()
		self.cTrav.addCollider(cNodePath_Picker, self.collHandler)
		self.raySolid.setOrigin(0, 0, CamPos_Z)

	def setRaySolidDirection(self):
		mpos = self.mouseWatcherNode.getMouse()
		#self.crosshair.show()
		# Reset the Collision Ray orientation, based on the mouse position
		self.raySolid.setDirection(24 * mpos.getX(), 13.3 * mpos.getY(), -50.5)

	def mouse1_Down(self):
		if self.mouseWatcherNode.hasMouse():
			self.setRaySolidDirection()

	def mouse1_Up(self):
		if self.mouseWatcherNode.hasMouse():
			self.setRaySolidDirection()
			if self.collHandler.getNumEntries() > 0:
				self.collHandler.sortEntries()
				#Scene graph tree is written in C. To store/read python objects, use NodePath.setPythonTag/getPythonTag('attrName')
				if btn := self.collHandler.getEntry(0).getIntoNodePath().getParent().getPythonTag("btn"):
					btn.leftClick()

	def mouse3_Down(self):
		if self.mouseWatcherNode.hasMouse():
			self.setRaySolidDirection()

	def mouse3_Up(self):
		if self.mouseWatcherNode.hasMouse():
			self.setRaySolidDirection()
			if self.collHandler.getNumEntries() > 0:
				self.collHandler.sortEntries()
				cNode_Picked = self.collHandler.getEntry(0).getIntoNodePath()
				if self.stage != 0: self.cancelSelection()
				elif btn := cNode_Picked.getParent().getPythonTag("btn"):
					btn.rightClick()
			else: self.cancelSelection()

	def clearDrawnCards(self):
		self.playedCards = []
		for child in self.render.getChildren():
			if not (child.name.startswith("Model2Keep")
					or child.name.startswith("Tex2Keep")
					or child.name.startswith("Text2Keep")):
				print("Remove", child.name, type(child))
				child.removeNode()
		for child in self.render.getChildren():
			if "2Keep" not in child.name:
				print("Kept under render (those that shouldn't):", child.name, type(child))
		print(self.cam.getPos(), self.cam.getHpr(), self.camLens.getFov())
		self.arrow.hide()
		self.deckZones = {}

	def mainTaskLoop(self, task):
		# seqReady默认是True，只在游戏结算和准备动画过程中把seqReady设为False，保证尚未完成的seq不被误读
		# 完成sequence的准备工作时会把seqReady再次设为True
		# 只有把当前正在进行的seq走完之后才会读取下一个seq
		if self.seqReady and self.seqHolder and not (self.seq2Play and self.seq2Play.isPlaying()):
			self.seq2Play = self.seqHolder.pop(0)
			self.seq2Play.append(Func(self.decideCardColors))
			self.seq2Play.start()
		# tkinter window必须在主线程中运行，所以必须在ShowBase的main loop中被执行
		# self.msg_Exit随时可以被设为非空值。但是一定要等到GUI中的所有seq都排空并且没有正在播放的seq了之后才会退出当前游戏
		# 实际上就是只有当GUI处于空闲状态时才会执行
		elif self.msg_Exit and self.seqReady and not self.seqHolder and not (self.seq2Play and self.seq2Play.isPlaying()):
			# print("\n\n----------\nCheck restart layer 1 window:", self.msg_Exit, self.seqReady, self.seqHolder, self.seq2Play, self.seq2Play and self.seq2Play.isPlaying())
			self.seqReady, self.seq2Play, self.msg_Exit = True, None, ''
			self.clearDrawnCards()
			self.deckBuilder.root.unstash()
			return Task.cont

		if self.mouseWatcherNode.hasMouse(): #如果鼠标在窗口内
			self.setRaySolidDirection() #不断地把RaySolid重置
			#只要self.arrow和self.crosshair有一个正在显示，就取消卡牌的放大
			if not (self.arrow.isHidden() and self.crosshair.isHidden()):
				self.stopCardZoomIn()
				self.replotArrowCrosshair()
			elif self.btnBeingDragged: #如果有被拖动的卡牌，则取消卡牌的放大
				self.stopCardZoomIn()
				self.dragCard() #拖动卡牌
			#如果RaySolid有碰撞发生
			elif self.collHandler.getNumEntries() > 0:
				self.collHandler.sortEntries()
				cNode_Picked = self.collHandler.getEntry(0).getIntoNodePath()
				btn_Picked = cNode_Picked.getParent().getPythonTag("btn")
				#在组建套牌期间，只要鼠标移到了套牌中卡牌之外的地方就会取消。卡牌收藏区域的卡牌不设置放大功能
				if self.stage < 0:
					if isinstance(btn_Picked, Btn_CardinDeck): self.drawCardZoomIn(btn_Picked)
					else: self.stopCardZoomIn()
				else: #游戏过程中，指向了一个对应手牌的btn时才会响应。drawCardZoomIn自行判断指着的这张牌是否已经放大
					if hasattr(btn_Picked, "card") and btn_Picked.card and hasattr(btn_Picked.card, "inHand") \
							and btn_Picked.card.inHand and abs(btn_Picked.np.getY()) > 11.5: #如果手牌中的牌远离手牌区域，则不进行显示
						self.drawCardZoomIn(btn_Picked)
			#RaySolid没有碰撞时，如果此时不是游戏中或者有一个手牌在被放大，则取消放大
			#实际上很少会有需要调用此处的需要，因为背景也有较大的碰撞体积，所以在部分时候都会有RaySolid的碰撞
			elif self.np_CardZoomIn and (self.stage < 0 or self.np_CardZoomIn.getPythonTag("btn").card.inHand):
				self.stopCardZoomIn()
		return Task.cont

	def drawCardZoomIn(self, btn):
		# Stop showing for btns without card and hero and cards not allowed to show to enemy(hand and secret).
		if self.stage == -2:  # 在组建套牌时调用这个函数时一定是要放大一张牌
			card, drawNew = btn.cardEntity, True
			if self.np_CardZoomIn:  # 如果当前有放大的卡牌且不是指向的卡牌时，重新画一个；如果是相同的卡牌则无事发生
				if card != self.np_CardZoomIn.getPythonTag("btn").card:
					self.np_CardZoomIn.removeNode()
				else: drawNew = False  # 只有目前有放大卡牌且就是指向的卡牌时，才不会重新画一个
			if drawNew:
				x, y, z = btn.np.getPos()
				self.np_CardZoomIn = self.addCard(card, pos=(x-10, 0.75*y, z+3), pickable=False)[0]
				self.np_CardZoomIn.setScale(2)
		# 在游戏过程中放大一张牌时
		elif self.stage > -1:
			card = btn.card
			# 想要放大场上的英雄，或者一个对方手牌中应该只显示了卡背的牌时会失败，并取消当前的放大。
			if (card.category == "Hero" and card is self.Game.heroes[card.ID]) or \
					(card.inHand and btn.onlyCardBackShown):
				self.stopCardZoomIn()
			else:  # 在游戏中放大一张牌的时候需要判断其是否是一张要隐瞒的奥秘，并显示一张牌的扳机和附魔效果
				if self.np_CardZoomIn and self.np_CardZoomIn.getPythonTag("btn").card == card:
					return  # 如果正在放大的牌就是当前指着的牌的话，则直接返回
				if self.np_CardZoomIn: self.np_CardZoomIn.removeNode()
				# 手牌中的牌放大时在其上下方；而其他卡牌的放大会在屏幕左侧显示
				pos = (btn.np.getX() if hasattr(card, "inHand") and card.inHand else ZoomInCard_X,
						ZoomInCard1_Y if self.ID == card.ID else ZoomInCard2_Y, ZoomInCard_Z)
				#需要隐瞒的奥秘需要在卡面上盖未知奥秘的卡图；只有场上英雄在放大时是不显示完整卡图
				self.np_CardZoomIn, btn = self.addCard(card, pos, pickable=False,
													   isUnknownSecret=card.race == "Secret" and self.need2Hide(card),
													   isPlayed=card.category == "Hero" and card.onBoard)
				if btn: btn.effectChangeAni()
				# Display the creator of the card at the bottom
				if card.creator:
					genHeroZoneTrigIcon(self, card.creator(self.Game, card.ID), pos=(-1.4, -4.88, 0),
										scale=1)[0].reparentTo(self.np_CardZoomIn)
					valueText = self.txt("Created by:\n") + card.creator.name_CN if self.lang == "CN" else card.creator.name
					makeText(self.np_CardZoomIn, "Text", valueText=valueText, pos=(-0.8, -4.7, 0),
							scale=0.45, color=white, font=self.getFont(self.lang))[1].setAlign(TextNode.ALeft)
				# Add the tray of enchantments onto the card
				i = 0
				for enchant in card.enchantments:
					self.showEnchantTrigDeath(enchant.source, enchant.text(), i)
					i += 1
				for trig in card.trigsBoard + card.trigsHand + card.deathrattles:
					if not trig.inherent:
						typeTrig = type(trig)
						name = typeTrig.cardType.name_CN if self.lang == "CN" else typeTrig.cardType.name
						self.showEnchantTrigDeath(typeTrig.cardType, name+"\n"+typeTrig.description, i)
						i += 1

	def showEnchantTrigDeath(self, creator, text, i):
		nodepath = genHeroZoneTrigIcon(self, creator(self.Game, 1), pos=(3.15, -i, 0.1), scale=0.9)[0]
		nodepath.reparentTo(self.np_CardZoomIn)
		makeText(self.np_CardZoomIn, "Text", valueText=text, pos=(3.7, -i + 0.06, 0.1), scale=0.3,
				 color=black, font=self.getFont(self.lang), wordWrap=20, cardColor=yellow)[1].setAlign(TextNode.ALeft)

	def stopCardZoomIn(self):
		if self.np_CardZoomIn:
			self.np_CardZoomIn.removeNode()
			self.np_CardZoomIn = None

	def calcMousePos(self, z):
		vec_X, vec_Y, vec_Z = self.raySolid.getDirection()
		delta_Z = abs(CamPos_Z - z)
		x, y = vec_X * delta_Z / (-vec_Z), vec_Y * delta_Z / (-vec_Z)
		return x, y

	def dragCard(self):
		if self.btnBeingDragged.cNode:
			self.btnBeingDragged.cNode.removeNode()  # The collision nodes are kept by the cards.
			self.btnBeingDragged.cNode = None

		# Decide the new position of the btn being dragged
		z = self.btnBeingDragged.np.getZ()
		x, y = self.calcMousePos(z)
		self.btnBeingDragged.np.setPosHpr(x, y, z, 0, 0, 0)
		# No need to change the x, y, z of the card being dragged(Will return anyway)
		card = self.btnBeingDragged.card
		if card.category == "Minion":
			minionZone = self.minionZones[card.ID]
			ownMinions = self.Game.minions[card.ID]
			boardSize = len(ownMinions)
			if not ownMinions: self.pos = -1
			elif len(ownMinions) < 7:
				ls_np_temp = [minion.btn.np for minion in ownMinions]
				posMinions_Orig = posMinionsTable[minionZone.y][boardSize]
				posMinions_Plus1 = posMinionsTable[minionZone.y][boardSize + 1]
				if -6 > y or y > 6:  # Minion away from the center board, the minions won't shift
					dict_MinionNp_Pos = {ls_np_temp[i]: posMinions_Orig[i] for i in range(boardSize)}
					self.pos = -1
				elif minionZone.y - 3.8 < y < minionZone.y + 3.8:
					# Recalculate the positions and rearrange the minion btns
					if x < ls_np_temp[0].get_x():  # If placed leftmost, all current minion shift right
						dict_MinionNp_Pos = {ls_np_temp[i]: posMinions_Plus1[i + 1] for i in range(boardSize)}
						self.pos = 0
					elif x < ls_np_temp[-1].get_x():
						ind = next((i + 1 for i, nodePath in enumerate(ls_np_temp[:-1]) if nodePath.get_x() < x < ls_np_temp[i+1].get_x()), -1)
						if ind > -1:
							dict_MinionNp_Pos = {ls_np_temp[i]: posMinions_Plus1[i + (i >= ind)] for i in range(boardSize)}
							self.pos = ind
						else: return  # If failed to find
					else:  # All minions shift left
						dict_MinionNp_Pos = {ls_np_temp[i]: posMinions_Plus1[i] for i in range(boardSize)}
						self.pos = -1
				else:  # The minion is dragged to the opponent's board, all minions shift left
					dict_MinionNp_Pos = {ls_np_temp[i]: posMinions_Plus1[i] for i in range(boardSize)}
					self.pos = -1
				for nodePath, pos in dict_MinionNp_Pos.items(): nodePath.setPos(pos)

	def stopDraggingCard(self, returnDraggedCard=True):
		btn = self.btnBeingDragged
		if btn:
			btn.cNode = btn.np.attachNewNode(btn.cNode_Backup)
			self.btnBeingDragged = None
			if not returnDraggedCard:
				self.playedCards.append(self.subject)
				return
			ID = btn.card.ID
			# Put the card back in the right pos_hpr in hand
			handZone_Y, ownHand = self.handZones[ID].y, self.Game.Hand_Deck.hands[ID]
			if btn.card in ownHand:
				i = ownHand.index(btn.card)
				pos, hpr = posHandsTable[handZone_Y][len(ownHand)][i], hprHandsTable[handZone_Y][len(ownHand)][i]
				btn.np.setPosHpr(pos, hpr)
			# Put the minions back to right positions on board
			ownMinions = self.Game.minions[ID]
			posMinions = posMinionsTable[self.minionZones[ID].y][len(ownMinions)]
			for i, minion in enumerate(ownMinions):
				minion.btn.np.setPos(posMinions[i])

	def replotArrowCrosshair(self):
		# Decide the new orientation and scale of the arrow
		if self.subject and self.subject.btn and self.subject.btn.np:
			x_0, y_0, z_0 = self.subject.btn.np.getPos()
		else: x_0, y_0, z_0 = 0, 0, 1.4
		x, y = self.calcMousePos(z_0)
		if not self.arrow.isHidden():
			degree, distance = self.getDegreeDistance_fromCoors(x_0, y_0, x, y)
			self.arrow.setPosHprScale(x_0, y_0, z_0, degree, 0, 0, 1, distance / 7.75, 1)
		if not self.crosshair.isHidden():
			self.crosshair.setPos(x, y, 1.4)

	"""Game resolution setup"""
	def cancelSelection(self, returnDraggedCard=True, keepSubject=False, keepTarget=False, keepChoice=False, keepPos=False):
		self.stopDraggingCard(returnDraggedCard)
		self.arrow.hide()

		if 3 > self.stage > -1:  # 只有非发现状态,且游戏不在结算过程中时下才能取消选择
			if self.subject:
				for option in self.subject.options:
					if option.btn:
						if option.btn.np: option.btn.np.removeNode()
						option.btn = None
			for card in self.target: #self.target can be empty
				if card.btn and card.btn.np and (np := card.btn.np.find("ithTarget_TextNode")):
					np.removeNode()
			subject, target, choice, pos = self.subject, self.target, self.choice, self.pos
			self.subject, self.target = None, []
			self.stage, self.step, self.pos, self.choice = 0, "", -1, -1
			self.resetCardColors()

			curTurn = self.Game.turn
			for card in self.Game.Hand_Deck.hands[curTurn] + self.Game.minions[curTurn] \
						+ [self.Game.heroes[curTurn], self.Game.powers[curTurn]]:
				if card.btn and not (card.inHand and card.btn.onlyCardBackShown): card.btn.setBoxColor(
					card.btn.decideColor())

			for card in self.Game.Hand_Deck.hands[1] + self.Game.Hand_Deck.hands[2] + [self.Game.powers[1]] + [
				self.Game.powers[2]]:
				if hasattr(card, "targets"): card.targets = []

			if keepSubject: self.subject = subject
			if keepTarget: self.target = target
			if keepChoice: self.choice = choice
			if keepPos: self.pos = pos

	#专门用于卡牌效果的目标选取。对于所有需要的序号判断是否有合法目标。如果某个序号没有合法目标，则当前的目标为None，跳到下一个选择。
	#如果剩余的选择中有合法目标，则返回2
	#如果剩余的所有选择中均没有合法目标的话，但之前已经有选择了的目标，则返回1；如果所有的序号都没有合法目标，则返回0
	def findTargetsandHighlight(self):
		target = ()
		for ith in range(len(self.target), self.subject.numTargetsNeeded(self.choice)):
			if target := self.subject.findTargets(self.choice, ith, exclude=self.target):
				break
			else: self.target.append(None)
		if target: #剩余的选择中有合法目标。可以高亮合法目标，并显示箭头。
			self.highlightTargets(target)
			self.arrow.show()
			self.arrow.setPos(self.subject.btn.np.getPos())
			return 2
		else: return 0 + any(obj for obj in self.target) #如果已选的目标中的合法目标，则返回1，否则返回0

	def resolveMove(self, card, button, step):
		print("Resolve move", card, button, step)
		game = self.Game
		if self.stage < 0 or self.stage > 3: pass
		elif self.stage == 0:
			self.cancelSelection()
			self.resetCardColors()
			#在需要选择subject的时候点击棋盘，回合结束按键和敌方的角色都会取消当前的所有选择；回合结束按钮还会另外取消所有的选择。
			if step == "TurnEnds": self.gamePlayQueue.append(lambda: game.endTurn())
			elif step != "Board" and card.ID == game.turn and not (1 < self.ID != card.ID):
				self.subject, self.step = card, step
				self.stage, self.choice = 2, 0  # 选择了主体目标，则准备进入选择打出位置或目标界面。抉择法术可能会将界面导入抉择界面。
				if step.endswith("inHand"): #选择一张手牌作为subject
					canBeTraded, affordable = game.Manas.checkTradeable(card), game.Manas.affordable(card) #checkTradeable是能否交易，affordable是能否正常从手牌打出
					if not affordable:
						if canBeTraded: self.btnBeingDragged = button #不够费用正常打出但是可以交易的话，则只可以把卡牌拖动到牌库处
						else: self.cancelSelection()
					else: #有费用正常打出卡牌或者可以交易卡牌时，需要目标的法术留在手中，显示指向箭头（可以指向牌库来交易），其他的可以拖动。
						if card.becomeswhenPlayed()[0].available():
							if self.checkifStartChooseOne(card): return #如果一张牌是可以打出的，函数自己处理选项的显示和stage的改变
							#如果是一个手牌中的没有抉择，且需要指定目标的法术，且有足够的费用正常打出时，那张牌不会从手牌中离开，直接显示指向箭头
							#如果是抉择法术但是因为光环而无需选择，则上述的函数只是修改self.choice，其余部分和正常卡牌一样执行。
							if affordable and self.subject.categorywhenPlayed() == "Spell" and card.numTargetsNeeded(self.choice):
								self.findTargetsandHighlight() #card.available()保证指向性法术一定有合法目标。
							else: self.btnBeingDragged = button
						elif canBeTraded: self.btnBeingDragged = button #不能正常打出，但是可以交易的卡牌，只能拖动到牌库处
						else: self.cancelSelection()
				elif step == "Power": #需要技能的费用足够且能使用。需要抉择的技能进入抉择阶段；不需要抉择的不需目标的技能当即使用，需要目标的进入目标选择。
					if game.Manas.affordable(card) and card.available():
						if self.checkifStartChooseOne(card): return
						self.selectedPowerasSubject(card, button)
					else: self.cancelSelection()
				elif step.endswith("onBoard"): #不能攻击的随从不能被选择。
					if card.canAttack() and (targets := card.findBattleTargets()):
						self.highlightTargets(targets)
						self.arrow.show()
						self.arrow.setPos(card.btn.np.getPos())
					else: self.cancelSelection()
		elif self.stage == 1:  # 在抉择界面下点击了抉择选项会进入此结算流程
			self.arrow.hide()
			if step == "ChooseOneOption" and card.available(): #目标必须是一个available的选项
				self.stage, self.choice = 2, self.subject.options.index(card)
				for option in self.subject.options: option.btn.np.removeNode()
				#抉择确定后有数种可能：不需要指向的技能（直接改动），需要指向的技能，手牌中的指向性法术，需要拖动的随从、非指向性法术和英雄牌等
				if self.subject.category == "Power": self.selectedPowerasSubject(self.subject, self.subject.btn)
				else: #如果之前选定的subject是一个需要目标的法术，则显示其指向箭头
					if self.subject.numTargetsNeeded(self.choice) and self.subject.category == "Spell":
						self.findTargetsandHighlight() #Available保证法术的抉择选项有合法目标。
					else: self.btnBeingDragged = self.subject.btn
			elif step == "TurnEnds":
				self.cancelSelection()
				self.gamePlayQueue.append(lambda: game.endTurn())
		# 炉石的目标选择在此处进行，可以对场上随从，英雄以及牌库（限于可交易卡牌）进行选择
		elif self.stage == 2: #选择的subject在stage=0的界面中已经确定一定是友方角色。
			#目标选择时，无论之前选择如何，点击回合结束时一定会终止所有选择
			if step == "TurnEnds":
				self.cancelSelection()
				self.gamePlayQueue.append(lambda: game.endTurn())
			#战斗只能存在于都在场上的随从或英雄之间
			elif self.step in ("MiniononBoard", "HeroonBoard") and step in ("MiniononBoard", "HeroonBoard"):
				if self.subject.canAttackTarget(card): #要想结算攻击，self.subject必须能够攻击
					self.cancelSelection(keepSubject=True, keepTarget=True)
					self.gamePlayQueue.append(lambda: game.battle(self.subject, card, verifySelectable=True, useAttChance=True, resolveDeath=True, sendthruServer=True))
			#subject是手牌中的卡牌时，此时正在拖动卡牌。随从的打出需要先选择位置，其他的卡牌如果需要目标，则直接留在手牌中改为拖动箭头，不需要目标的为拖动后打出。
			elif "inHand" in self.step:
				if step == "Deck" and game.Manas.checkTradeable(self.subject):  # 在选择牌库的时候只有是手中的可交易卡牌并且当前费用大于0时会有反应
					self.cancelSelection(keepSubject=True)
					self.gamePlayQueue.append(lambda: game.playCard_4Trade(self.subject))
				elif self.subject.effects["Unplayable"] > 0 or not game.Manas.affordable(self.subject):  # 手牌中的牌希望以正常方式找出时,只要费用不足以支付，就放弃之前的所有选择
					self.cancelSelection()
				#手中选中的随从在这里结算打出位置，如果不需要目标，则直接打出。
				elif self.step in ("MinioninHand", "AmuletinHand"):  # 选中场上的友方随从，我休眠物和护符时会把随从打出在其左侧
					#如果点击的是棋盘，或者是一个非英雄的我方场上随从/休眠物/护符，则直接确定随从等的打出位置
					if step == "Board" or (card.ID == self.subject.ID and (step.endswith("onBoard") and not step.startswith("Hero"))):
						self.step = "MinionPosDecided"  # 将主体记录为标记了打出位置的手中随从。
						if self.subject.numTargetsNeeded(self.choice) and self.subject.canFindTargetsNeeded(self.choice):
							self.findTargetsandHighlight()  # 随从打出后需要目标
						#随从牌不需要目标或没有合法目标时
						elif self.Game.check_playMinion(self.subject, (), self.pos, self.choice):
							self.cancelSelection(returnDraggedCard=False, keepSubject=True, keepTarget=True, keepChoice=True, keepPos=True)
							self.gamePlayQueue.append(lambda: game.playMinion(self.subject, (), self.pos, self.choice))
						else: self.cancelSelection()
				#选择手牌中的法术/武器/英雄牌的目标选择和打出
				elif self.step in ("SpellinHand", "WeaponinHand", "HeroinHand"): #尝试打出手牌中的一张牌（无目标），或者给手牌中的一张牌选择目标
					playFunc = {"Spell": game.playSpell, "Weapon": game.playWeapon, "Hero": game.playHero}[self.subject.category]
					checkFunc = {"Spell": game.check_playSpell, "Weapon": game.check_playWeapon, "Hero": game.check_playHero}[self.subject.category]
					if self.subject.numTargetsNeeded(self.choice):
						#如果目标不合法，没有反应；如果目标合法，则subject已经选择了所有目标后，可以判断是否打出。
						if step in ("MiniononBoard", "HeroonBoard") and self.isLegalTarget_canFinishSelection(card):
							if checkFunc(self.subject, self.target, self.choice):
								self.cancelSelection(returnDraggedCard=False, keepSubject=True, keepTarget=True, keepChoice=True)
								self.gamePlayQueue.append(lambda: playFunc(self.subject, self.target, self.choice))
							else: self.cancelSelection()
					# 打出非指向性法术/武器/英雄牌时，可以把卡牌拖动到随从，英雄或者桌面上
					elif checkFunc(self.subject, self.target, self.choice):
						self.cancelSelection(returnDraggedCard=False, keepSubject=True, keepTarget=True, keepChoice=True)
						self.gamePlayQueue.append(lambda: playFunc(self.subject, self.target, self.choice))
					else: self.cancelSelection()
			# 随从的打出位置和抉择选项已经在上一步选择，这里一定是处理目标选择。
			elif self.step == "MinionPosDecided":
				if step in ("MiniononBoard", "HeroonBoard") and self.isLegalTarget_canFinishSelection(card):
					if self.Game.check_playMinion(self.subject, self.target, self.pos, self.choice):
						self.cancelSelection(returnDraggedCard=False, keepSubject=True, keepTarget=True, keepChoice=True, keepPos=True)
						self.gamePlayQueue.append(lambda: game.playMinion(self.subject, self.target, self.pos, self.choice))
					else: self.cancelSelection()
			# 在此选择的一定是指向性的英雄技能。
			elif self.step == "Power":  # 如果需要指向的英雄技能对None使用，HeroPower的合法性检测会阻止使用。
				if step in ("MiniononBoard", "HeroonBoard") and self.isLegalTarget_canFinishSelection(card):
					if self.Game.check_UsePower(self.subject, self.target, self.choice):
						self.cancelSelection(keepSubject=True, keepTarget=True, keepChoice=True)
						self.gamePlayQueue.append(lambda: game.usePower(self.subject, self.target, self.choice))
					else: self.cancelSelection()
		else:  # self.stage == 3
			if step == "DiscoverOption": self.discover = card
			elif step == "Fusion":
				self.stage = 0
				game.Discover.initiator.fusionDecided(card)

	#能够被选择的目标必须是目前不在卡池里面的，是可以被效果选择到的，且是效果的合法目标。
	#是合法目标的前提下，向self.target中添加。如果卡牌效果得到了所有需要的目标，则返回True，然后开始打出操作。
	def isLegalTarget_canFinishSelection(self, card):
		if card not in self.target and self.subject.canSelect(card) \
				and self.subject.targetCorrect(card, self.choice, ith=len(self.target)):
			self.target.append(card)
			if len(self.target) >= self.subject.numTargetsNeeded(self.choice): return True
			else: #需要给被选择的卡牌标其现在是第几号被选择的目标。
				makeText(card.btn.np, "ithTarget", str(len(self.target)), pos=(0, 0, 1), scale=1.5, color=red, font=self.getFont())
				return self.findTargetsandHighlight() < 2
		return False

	def checkifStartChooseOne(self, card):
		if card.options and self.Game.rules[card.ID]["Choose Both"] < 1:
			self.stage = 1
			leftMost_X = -5 * (len(card.options) - 1) / 2
			for i, option in enumerate(card.options):
				available = option.available()
				nodePath, _ = self.addCard(option, pos=(leftMost_X + i * 5, 1.5, 10), pickable=available)
				if not available: nodePath.setColor(grey)
			return True
		else:
			self.choice = -1
			return False

	def selectedPowerasSubject(self, card, button):
		# 英雄技能会自己判定是否可以使用。
		if card.numTargetsNeeded(self.choice):  # selectedSubject之前是"Hero Power 1"或者"Hero Power 2"
			self.step = "Power"
			self.findTargetsandHighlight()
		else:
			self.cancelSelection(keepSubject=True, keepChoice=True)
			self.gamePlayQueue.append(lambda: self.Game.usePower(self.subject, (), self.choice))

	# Can only be invoked by the game thread
	def waitforDiscover(self):
		self.stage, self.discover = 3, None
		para = Parallel()
		btns = []
		leftMost_x = -5 * (len(self.Game.options) - 1) / 2
		for i, card in enumerate(self.Game.options):
			# self.addCard creates a btn for the card, but the card's original button(if any) is kept.
			# There will be two btns referencing the same card
			nodePath_New, btn_New = self.addCard(card, Point3(0, 0, 0), pickable=True)
			btns.append(btn_New)
			para.append(LerpPosHprScaleInterval(nodePath_New, duration=0.2, pos=(leftMost_x + 5 * i, 1.5, 13),
												hpr=(0, 0, 0), startScale=0.2, scale=1))
		self.seqHolder[-1].append(para)
		btn_HideOptions = DirectButton(text=("Hide", "Hide", "Hide", "Continue"), scale=.1,
									   pos=(2, 0, 2), command=self.toggleDiscoverHide)
		btn_HideOptions["extraArgs"] = [btn_HideOptions]
		self.btns2Remove.append(btn_HideOptions)
		self.seqHolder[-1].append(Func(btn_HideOptions.setPos, -0.5, 0, -0.5))
		self.seqReady = True
		while self.discover is None:
			time.sleep(0.1)
		self.stage = 0
		# Restart the sequence
		self.seqReady = False
		self.seqHolder.append(Sequence())
		for btn in btns: btn.np.detachNode()
		for btn in self.btns2Remove: btn.destroy()
		return self.discover  # No need to reset the self.discover. Need to reset each time anyways

	def toggleDiscoverHide(self, btn):
		print("Toggle hide button", btn["text"])
		if btn["text"] == ("Hide", "Hide", "Hide", "Continue"):
			btn["text"] = ("Show", "Show", "Show", "Continue")
			for card in self.Game.options: card.btn.np.hide()
		else:  # btn["text"] == ("Show", "Show", "Show", "Continue")
			btn["text"] = ("Hide", "Hide", "Hide", "Continue")
			for card in self.Game.options: card.btn.np.show()

	# To be invoked for animation of opponent's discover decision (if PvP) or own random decisions
	def discoverDecideAni(self, isRandom, indPick, options):
		seq, para = self.seqHolder[-1], Parallel()
		btn_Chosen, btns = None, []
		leftMost_x = -5 * (len(options) - 1) / 2
		if isinstance(options, (list, tuple)):
			for i, card in enumerate(options):
				nodePath, btn = self.addCard(card, Point3(0, 0, 0), pickable=True,
											 onlyShowCardBack=self.need2Hide(card))
				btns.append(btn)
				if i == indPick: btn_Chosen = btn
				para.append(LerpPosHprScaleInterval(nodePath, duration=0.2, pos=(leftMost_x + 5 * i, 1.5, 13),
													hpr=(0, 0, 0), startScale=0.2, scale=1))
		seq.append(para)
		seq.append(Wait(0.5) if isRandom else Wait(1.2))
		sequence = Sequence(LerpScaleInterval(btn_Chosen.np, duration=0.2, scale=1.13),
							LerpScaleInterval(btn_Chosen.np, duration=0.2, scale=1.0))
		for btn in btns: sequence.append(Func(btn.np.detachNode))  # The card might need to be added to hand
		seq.append(sequence)

	# For choosing a target onBoard during effect resolution
	def waitforChoose(self, ls):
		self.stage, self.discover = 3, None
		self.seqHolder[-1].append(Func(self.highlightTargets, ls))
		self.seqReady = True
		self.crosshair.show()

		while self.discover not in ls:
			time.sleep(0.1)
		self.stage = 0
		# Restart the sequence
		self.crosshair.hide()
		self.resetCardColors()
		self.seqReady = False
		self.seqHolder.append(Sequence())
		return self.discover  # No need to reset the self.discover. Need to reset each time anyways

	# options should be real card objs
	def chooseDecideAni(self, isRandom, indexOption, options):
		nodePath = (option := options[indexOption]).btn.np
		seq = Sequence(Func(self.highlightTargets, options), Func(self.crosshair.setPos, 0, 0, 1.4),
					   # The crosshair wrtReparentTo the target it will point to, then moves onto it, then reparentTo render
					   Func(self.crosshair.wrtReparentTo, nodePath), Func(self.crosshair.show),
					   LerpPosInterval(self.crosshair, duration=0.2 if isRandom else 0.5, pos=(0, 0.5, 0.3)),
					   Wait(0.4), Func(self.crosshair.hide), Func(self.crosshair.reparentTo, self.render),
					   Func(self.resetCardColors)
					   )
		self.seqHolder[-1].append(seq)

	def checkCardsDisplays(self, side=0, checkHand=False, checkBoard=False):
		sides = (side,) if side else (1, 2)
		if checkHand:
			print("   Check cards in hands:")
			for ID in sides:
				for card in self.Game.Hand_Deck.hands[ID]:
					if not card.btn.np.getParent():
						print("	  ", ID, card.name, card.btn.np, card.btn.np.getParent(), card.btn.np.getPos())
		if checkBoard:
			print("   Check cards on Board:")
			for ID in sides:
				for card in self.Game.minions[ID]:
					if not card.btn.np.getParent():
						print("	  ", ID, card.name, card.btn.np, card.btn.np.getParent(), card.btn.np.getPos())

	def sendOwnMovethruServer(self, endingTurn=True):
		pass

	def back2Layer1(self, btn=None):
		self.stage = -2
		self.msg_Exit = "Go Back to Layer 1"
		self.seqReady = True