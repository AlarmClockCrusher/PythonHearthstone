from math import ceil
from Panda_LoadModels import *


"""Hand Zone infos"""
Separation_Hands = 5
OpeningAngle = 40
radius = 12.9
HandZone_Z, ZoomInCard_Z = 2.5, 20
HandZone1_Y, HandZone2_Y = -25, 26.2
DrawnCard1_PausePos, DrawnCard2_PausePos = (6.5, -0.8, 25), (6.5, 4.2, 25)
DiscardedCard1_Y, DiscardedCard2_Y = -2, 5.5
ZoomInCard_X, ZoomInCard1_Y, ZoomInCard2_Y = -11.1, -1.5, 4.25
scale_Hand = 0.9

def calc_PosHprHands(num, x, y, z):
	if num < 1: return [], []
	d_angle = min(12, int(OpeningAngle / num))
	posHands, hprHands = [], []
	if y < 0:
		leftAngle = -d_angle * (num - 1) / 2
		for i in range(num):
			angleAboutZ = leftAngle+i*d_angle
			hprHands.append(Point3(-angleAboutZ, 0, 0))
			posHands.append(Point3(x+radius*numpy.sin(numpy.pi*angleAboutZ/180), y+radius*numpy.cos(numpy.pi*angleAboutZ/180),
								z+i*0.15))
	else:
		leftAngle = d_angle * (num - 1) / 2
		for i in range(num):
			angleAboutZ = leftAngle-i*d_angle
			hprHands.append(Point3(-angleAboutZ+180, 0, 0))
			posHands.append(Point3(x-radius*numpy.sin(numpy.pi*angleAboutZ/180), y-radius*numpy.cos(numpy.pi*angleAboutZ/180),
								z-i*0.15))
	return posHands, hprHands

posHandsTable = {HandZone1_Y: {i: calc_PosHprHands(i, 0, HandZone1_Y, HandZone_Z)[0] for i in range(13)},
				HandZone2_Y: {i: calc_PosHprHands(i, 0, HandZone2_Y, HandZone_Z)[0] for i in range(13)}
				}
				
hprHandsTable = {HandZone1_Y: {i: calc_PosHprHands(i, 0, HandZone1_Y, HandZone_Z)[1] for i in range(13)},
				HandZone2_Y: {i: calc_PosHprHands(i, 0, HandZone2_Y, HandZone_Z)[1] for i in range(13)}
				}


class HandZone:
	def __init__(self, GUI, ID):
		self.GUI, self.ID = GUI, ID
		lowerPlayerID = max(1, self.GUI.ID) #GUI_1P has UI = 0
		self.x, self.y, self.z = 0, HandZone1_Y if self.ID == lowerPlayerID else HandZone2_Y, HandZone_Z
		
	#transform hand card into arbitrary category. Minion could become spell
	def transformHands(self, btns, newCards):
		para = Parallel()
		for btn, newCard in zip(btns, newCards):
			isPlayed = btn.isPlayed
			pos, hpr, scale = btn.np.getPos(), btn.np.getHpr(), btn.np.getScale()
			nodePath, btn_NewCard = genCard(self.GUI, newCard, isPlayed=isPlayed, pos=pos, hpr=hpr, scale=scale,
											onlyShowCardBack=self.GUI.sock and newCard.ID != self.GUI.ID and not self.GUI.showEnemyHand)
			para.append(Func(btn.np.removeNode)) #Transformed cards won't ever show up again
			para.append(Func(nodePath.setPosHprScale, pos, hpr, scale))
		self.GUI.seqHolder[-1].append(para)
		
	def placeCards(self, add2Queue=True): #Sometimes, CardModelTest.py wants to use this without the seqHolder
		GUI = self.GUI
		ownHand = GUI.Game.Hand_Deck.hands[self.ID]
		posHands, hprHands = posHandsTable[self.y][len(ownHand)], hprHandsTable[self.y][len(ownHand)]
		for i, card in enumerate(ownHand):
			genCard(GUI, card, isPlayed=False, scale=scale_Hand, onlyShowCardBack=GUI.need2beHidden(card))
		para = Parallel(Func(GUI.deckZones[self.ID].draw, len(GUI.Game.Hand_Deck.decks[self.ID]), len(ownHand)) )
		for i, card in enumerate(ownHand):
			if card.btn != GUI.btnBeingDragged:
				para.append(Func(card.btn.np.reparentTo, GUI.render))
				para.append(LerpPosHprScaleInterval(card.btn.np, duration=0.25, pos=posHands[i], hpr=hprHands[i], scale=scale_Hand))
		
		if GUI.seqHolder:
			if add2Queue: GUI.seqHolder[-1].append(para)
			else: return para
		else: para.start()
		
"""Hero Zone infos"""
Hero1_Pos, Hero2_Pos = (0, -7.35, 1.05), (0.05, 8.54, 1.05)
Weapon1_Pos, Weapon2_Pos = (-4.75, -7.4, 1.05), (-4.75, 8.4, 1.05)
Power1_Pos, Power2_Pos = (4.67, -7.9, 1.05), (4.67, 8, 1.05)
Hero2_X = Hero2_Pos[0]
posSecretsTable = {Hero1_Pos: [( +0,	-4.82-0.2, 1.15),
								(-1.14, -5.43-0.2, 1.15),
								(+1.14, -5.43-0.2, 1.15),
								(-1.83, -6.51-0.2, 1.15),
								(+1.83, -6.51-0.2, 1.15)],
					Hero2_Pos: [(Hero2_X+0,	11.05-0.2, 1.15),
								(Hero2_X-1.14, 10.44-0.2, 1.15),
								(Hero2_X+1.14, 10.44-0.2, 1.15),
								(Hero2_X-1.83,  9.36-0.2, 1.15),
								(Hero2_X+1.83,  9.36-0.2, 1.15)]
			  		}

Seperation_Trigs = 1.2
def calc_posTrigs(num, x, y, z): #Input the x, y, z of the heroPos
	if num < 3:
		leftPos = x - Seperation_Trigs * (num - 1) / 2
		return [(leftPos + Seperation_Trigs * i, y, z) for i in range(num)]
	else: #num >= 3
		if num % 2 == 0: numLeft = numRight = int(num / 2) - 1 #8: 3 + 2 + 3
		else: numLeft, numRight = int((num - 1) / 2), int((num - 3) / 2) #5 : 2 + 2 + 1
		return [(x - 3.2 - i * Seperation_Trigs, y, z) for i in range(numLeft)] \
				+ calc_posTrigs(2, x, y, z) + [(x + 3.2 + i * Seperation_Trigs, y, z) for i in range(numRight)]
	

ManaText1_Pos, ManaText2_Pos = Point3(7.87, -11.9, 1.01), Point3(6.92, 11.65, 1.01)

class HeroZone:
	def __init__(self, GUI, ID):
		self.GUI, self.ID = GUI, ID
		lowerPlayerID = max(1, self.GUI.ID) #GUI_1P has UI = 0
		if self.ID == lowerPlayerID: self.heroPos, self.weaponPos, self.powerPos = Hero1_Pos, Weapon1_Pos, Power1_Pos
		else: self.heroPos, self.weaponPos, self.powerPos = Hero2_Pos, Weapon2_Pos, Power2_Pos
		
		self.manaHD = GUI.Game.Manas
		#Merge the ManaZone with HeroZone
		self.manaText = TextNode("Text_Mana")
		self.manaText.setText("0/0")
		self.manaText.setAlign(TextNode.ACenter)
		self.manaText.setFont(self.GUI.font)
		manaTextNode = self.GUI.render.attachNewNode(self.manaText)
		manaTextNode.setScale(0.8)
		if self.heroPos[1] < 0: manaTextNode.setPosHpr(ManaText1_Pos, Point3(0, -90, 0))
		else: manaTextNode.setPosHpr(ManaText2_Pos, Point3(0, -90, 0))

	def heroReplacedAni(self, oldHero, oldPower):
		seq_Holder = self.GUI.seqHolder[-1]
		heroNodePath = oldHero.btn.np if oldHero and oldHero.btn and oldHero.btn.np else None
		powerNodePath = oldPower.btn.np if oldPower and oldPower.btn and oldPower.btn.np else None
		x, y, z = self.heroPos
		if heroNodePath: seq_Holder.append(Func(heroNodePath.setPos, x, y, z - 0.01))
		x, y, z = self.powerPos
		if powerNodePath: seq_Holder.append(Func(powerNodePath.setPos, x, y, z - 0.02))
		self.placeCards()
		if heroNodePath: seq_Holder.append(Func(heroNodePath.removeNode))
		if powerNodePath: seq_Holder.append(Func(powerNodePath.removeNode))

	def placeCards(self, add2Queue=True, powerFlip=True, weaponDescends=True):
		#The whole func takes ~1ms
		GUI, para = self.GUI, Parallel()
		game = GUI.Game
		hero, power, weapon = game.heroes[self.ID], game.powers[self.ID], game.availableWeapon(self.ID)
		#Place the hero
		genCard(GUI, hero, isPlayed=True)
		para.append(Func(hero.btn.np.reparentTo, GUI.render))
		para.append(LerpPosHprScaleInterval(hero.btn.np, duration=0.3, pos=self.heroPos, hpr=(0, 0, 0), scale=1))

		#Place the power
		x, y, z = self.powerPos
		hpr = (0, 0, 180) if power.chancesUsedUp() else (0, 0, 0)
		genCard(GUI, power, isPlayed=True)
		#新技能出现的时候一定都是可以使用的正面向上状态
		if powerFlip:
			seq = Sequence(Func(power.btn.np.reparentTo, GUI.render),
							LerpPosHprInterval(power.btn.np, duration=0.17, startPos=(x, y, z), pos=(x, y, z + 3), hpr=(0, 0, 90)),
							LerpPosHprInterval(power.btn.np, duration=0.17, pos=(x, y, z), hpr=(0, 0, 180)),
						   LerpPosHprInterval(power.btn.np, duration=0.17, pos=(x, y, z), hpr=hpr))
			para.append(seq)
		else: para.append(LerpPosHprInterval(power.btn.np, duration=0.17, pos=(x, y, z), hpr=hpr))
		
		#Place the weapon
		x, y, z = self.weaponPos
		if weapon:
			genCard(GUI, weapon, isPlayed=True)
			para.append(Func(weapon.btn.np.reparentTo, GUI.render))
			if weaponDescends: para.append(Func(weapon.btn.np.setPos, x, y+0.2, z+5))
			para.append(LerpPosHprInterval(weapon.btn.np, duration=0.3, pos=self.weaponPos, hpr=(0, 0, 0)))
			
		if GUI.seqHolder:
			if add2Queue: GUI.seqHolder[-1].append(para)
			else: return para
		else: para.start()
		
	def drawMana(self, usable, upper, locked, overloaded):
		self.manaText.setText("%d/%d"%(usable, upper))
		manas = self.GUI.manaModels
		if self.heroPos[1] < 0:
			for i in range(usable): manas["Mana"][i].setPos(i * 0.82, 0, 1)
			for i in range(usable, 10): manas["Mana"][i].setPos(0, 0, 0)
			for j in range(upper - usable - locked): manas["EmptyMana"][j].setPos((usable+j) * 0.82, 0, 1)
			for j in range(upper - usable - locked, 10): manas["EmptyMana"][j].setPos(0, 0, 0)
			for k in range(locked): manas["LockedMana"][k].setPos((upper - locked + k)  * 0.82, 0, 1)
			for k in range(locked, 10): manas["LockedMana"][k].setPos(0, 0, 0)
			#过载了的水晶在水晶栏下方一行显示
			for m in range(overloaded): manas["OverloadedMana"][m].setPos(m * 0.82, -1.2, 1)
			for m in range(overloaded, 10): manas["OverloadedMana"][m].setPos(0, 0, 0)
			
	#Secrets and quests are treated in the same way
	def placeSecrets(self):
		secretHD = self.GUI.Game.Secrets
		ownSecrets = secretHD.mainQuests[self.ID] + secretHD.sideQuests[self.ID] + secretHD.secrets[self.ID]
		posSecrets = posSecretsTable[self.heroPos][:len(ownSecrets)]
		para, GUI = Parallel(), self.GUI
		print("Placing secret zone:", ownSecrets)
		for i, card in enumerate(ownSecrets):
			pos = posSecrets[i]
			if card.race == "Secret": genSecretIcon(GUI, card, pos=(pos[0], pos[1], 0))
			else: genHeroZoneTrigIcon(self.GUI, card, pos=(pos[0], pos[1], 0))
		for i, card in enumerate(ownSecrets):
			nodePath, btn = card.btn.np, card.btn
			para.append(Func(nodePath.reparentTo, GUI.render))
			if card.race == "Secret":
				hpr = (0, 0, 0) if self.ID != self.GUI.Game.turn else (0, 0, 180)
				para.append(Sequence(Func(nodePath.setZ, posSecrets[0][2]), Func(reassignBtn2Card, btn, card),
									 LerpPosHprInterval(nodePath, duration=0.25, pos=posSecrets[i], hpr=hpr))
							)
			else:
				print("setting non-secret thing", card, nodePath, btn)
				para.append(Func(nodePath.setPos, posSecrets[i]))
				para.append(Func(reassignBtn2Card, btn, card))

		if GUI.seqHolder: GUI.seqHolder[-1].append(para)
		else: para.start()
		
	def addaTrig(self, card, text=''):
		genHeroZoneTrigIcon(self.GUI, card, text=str(text)) #Add the trig to (0, 0, 0)
		self.GUI.seqHolder[-1].append(self.seq_PlaceTurnTrigs())
		
	def removeaTrig(self, card):
		self.GUI.seqHolder[-1].append(Func(card.btn.np.removeNode))
		self.GUI.seqHolder[-1].append(self.seq_PlaceTurnTrigs())
		
	def seq_PlaceTurnTrigs(self):
		cards = [trig.card for trig in self.GUI.Game.turnEndTrigger + self.GUI.Game.turnStartTrigger + self.GUI.Game.trigAuras[self.ID] if trig.ID == self.ID]
		posTrigs = calc_posTrigs(len(cards), self.heroPos[0], self.heroPos[1] - 2.2, self.heroPos[2]+0.1)
		para = Parallel()
		for i, card in enumerate(cards):
			if not card.btn: genHeroZoneTrigIcon(self.GUI, card, pos=posTrigs[i])
		for i, card in enumerate(cards):
			if card.btn: para.append(card.btn.np.posInterval(0.25, pos=posTrigs[i]))
		return para
	
				
Separation_Minions = 3.7
MinionZone1_Y, MinionZone2_Y = -1.72, 3.1
MinionZone_Z = Hero1_Pos[2]

def calc_posMinions(num, x, y, z):
	leftPos = x - Separation_Minions * (num - 1) / 2
	offset = 0.1 if y < 0 else 0
	posMinions = [Point3(leftPos + Separation_Minions * i, y, z+0.04*i+offset) for i in range(num)]
	return posMinions

#0~14 minions
posMinionsTable = {MinionZone1_Y: {i: calc_posMinions(i, 0, MinionZone1_Y, MinionZone_Z) for i in range(15)},
				MinionZone2_Y: {i: calc_posMinions(i, 0, MinionZone2_Y, MinionZone_Z) for i in range(15)}
				}
scale_Minion = 1.06

class MinionZone:
	def __init__(self, GUI, ID):
		self.GUI, self.ID = GUI, ID
		lowerPlayerID = max(1, self.GUI.ID) #GUI_1P has UI = 0
		self.y = MinionZone1_Y if self.ID == lowerPlayerID else MinionZone2_Y
		
	#It takes negligible time to finish calcing pos and actually start drawing
	def placeCards(self, add2Queue=True):
		GUI = self.GUI
		ownMinions = self.GUI.Game.minions[self.ID]
		posMinions = posMinionsTable[self.y][len(ownMinions)]
		for i, card in enumerate(ownMinions):
			genCard(GUI, card, isPlayed=True, scale=scale_Minion)
		para = Parallel()
		for i, card in enumerate(ownMinions):
			para.append(Func(card.btn.np.reparentTo, GUI.render))
			para.append(LerpPosHprScaleInterval(card.btn.np, duration=0.25, pos=posMinions[i], hpr=(0, 0, 0), scale=scale_Minion))
		
		if GUI.seqHolder:
			if add2Queue: GUI.seqHolder[-1].append(para)
			else: return para
		else: para.start()

class Btn_Board:
	def __init__(self, GUI, nodePath):
		self.GUI = GUI
		self.selected = False
		self.np = nodePath
		self.np.name = "Model2Keep_Board"
		self.card = None #Just a placeholder
		
	def leftClick(self):
		#self.GUI.checkCardsDisplays(checkHand=True, checkBoard=True)
		if -1 < self.GUI.UI < 3:  #不在发现中和动画演示中才会响应
			self.GUI.resolveMove(None, self, "Board")
	
	def rightClick(self):
		self.GUI.cancelSelection()
		self.GUI.stopCardZoomIn()
		
	def dimDown(self):
		self.np.setColor(grey)
	
	def setBoxColor(self, color):
		pass
	
	def stopCardZoomIn(self):
		pass
		
		
TurnEndBtn_Pos = (15.5, 1.16, 1)

class Btn_TurnEnd:
	def __init__(self, GUI, nodePath):
		self.GUI = GUI
		self.np = nodePath
		#self.np_button and self.np_box are children of self.np
		self.np_button = nodePath.find("TurnEndButton")
		self.np_box = nodePath.find("box")
		self.np_box.setColor(green)
		self.changeDisplay(jobDone=False)
		self.card = None  #Just a placeholder
		self.jobDone = False
		
	def changeDisplay(self, jobDone=False):
		self.jobDone = jobDone
		if jobDone:
			self.np_button.setTexture(self.np_button.findTextureStage('*'),
									  self.GUI.loader.loadTexture("Models\\BoardModels\\TurnEndBtn_JobDone.png"), 1)
			self.np_box.show()
		else:
			self.np_button.setTexture(self.np_button.findTextureStage('*'),
									  self.GUI.loader.loadTexture("Models\\BoardModels\\TurnEndBtn.png"), 1)
			self.np_box.hide()
			
	def leftClick(self):
		if 3 > self.GUI.UI > -1:
			print("Turn End button clicked")
			self.GUI.resolveMove(None, self, "TurnEnds")
			
	def rightClick(self):
		self.GUI.cancelSelection()
	
	def dimDown(self):
		self.np.setColor(grey)
	
	def setBoxColor(self, color):
		pass
	
	def stopCardZoomIn(self):
		pass


deckScale = 0.9
Deck1_Pos, Deck2_Pos = (16.85, -2.44, 3), (16.75, 4.89, 3)
hpr_Deck = (90, 90, 0)

class DeckZone:
	def __init__(self, GUI, ID):
		self.GUI, self.ID = GUI, ID
		lowerPlayerID = max(1, self.GUI.ID) #GUI_1P has UI = 0
		self.pos = Deck1_Pos if self.ID == lowerPlayerID else Deck2_Pos
		self.card = None #Only a placeholder
		
		np_Deck = GUI.loader.loadModel("Models\\BoardModels\\Deck.glb")
		np_Deck.name = "Model2Keep_Deck"
		np_Deck.setTexture(np_Deck.findTextureStage('*'), GUI.textures["cardBack"], 1)
		np_Deck.reparentTo(GUI.render)
		np_Deck.setPos(self.pos)
		np_Deck.setScale(0.9)
		self.np_Deck = np_Deck
		self.textNode = TextNode("Text2Keep_DeckHand")
		self.textNode.setText("Deck: {}\nHand: {}".format(0, 0))
		self.textNode.setFont(GUI.font)
		self.textNodePath = GUI.render.attachNewNode(self.textNode)
		self.textNodePath.setPosHpr(self.pos[0] + 1.5, self.pos[1], self.pos[2], 0, -90, 0)
		
		collision = CollisionNode("Deck_cNode")
		collision.addSolid(CollisionBox(Point3(0.2, 0, -1.1), 0.8, 2, 3))
		self.np_Deck.attachNewNode(collision)#.show()
		self.np_Deck.setPythonTag("btn", self)
		self.texCard_EmptyDeck = GUI.loader.loadModel("TexCards\\ForGame\\EmptyDeck.egg")
		self.texCard_EmptyDeck.reparentTo(GUI.render)
		self.texCard_EmptyDeck.setPosHprScale(0, 0, 0, 0, -90, 0, 4, 1, 4*384/256)
		
	def changeSide(self, ID):
		self.ID = ID
		lowerPlayerID = max(1, self.GUI.ID)  #GUI_1P has UI = 0
		self.pos = Deck1_Pos if self.ID == lowerPlayerID else Deck2_Pos
		self.np_Deck.setPos(self.pos)
		self.textNodePath.setPos(self.pos[0] + 1.5, self.pos[1], self.pos[2])
		
	def draw(self, deckSize, handSize):
		numPairs2Draw = min(10, ceil(deckSize / 3))
		for nodePath in self.np_Deck.getChildren():
			if nodePath.name != "Deck_cNode":
				if int(nodePath.name) <= numPairs2Draw: nodePath.show()
				else: nodePath.hide()
		self.textNode.setText("Deck: {}\nHand: {}".format(deckSize, handSize))
		x, y, z = self.pos
		if deckSize < 1: self.texCard_EmptyDeck.setPos(x+0.45, y, 1.1)
		else: self.texCard_EmptyDeck.setPos(0, 0, 0)
		
	def fatigueAni(self, numFatigue):
		self.GUI.np_Fatigue.find("Fatigue_TextNode").node().setText(str(numFatigue))
		moPath = Mopath.Mopath()
		moPath.loadFile("Models\\BoardModels\\FatigueCurve.egg")
		interval = MopathInterval(moPath, self.GUI.np_Fatigue, duration=0.6)
		if self.GUI.seqHolder: self.GUI.seqHolder[-1].append(Sequence(interval, Wait(1), Func(self.GUI.np_Fatigue.setPos, 0, 0, 0 ) ))
		else: Sequence(interval, Wait(1), Func(self.GUI.np_Fatigue.setPos, 4, 0, 0) ).start()
		
	def leftClick(self):
		if self.GUI.UI == 2:
			self.GUI.resolveMove(self.GUI.Game.Hand_Deck, None, "Deck")
			
	def rightClick(self):
		pass


iconsaRow = 4
offset_Icon = 1.1
x_Subject, y_Subject0, x_Target0 = -23, -8, 2.5

class GameEvent:
	def __init__(self, GUI, subject, eventType, target, textSubject, textTarget, colorSubject, colorTarget, level):
		self.GUI, self.np = GUI, None
		self.eventType, self.level = "Summary", 1
		self.subject = subject #self.subject is the original card obj.
		self.np_Subject = None
		if target:
			if isinstance(target, (tuple, numpy.ndarray)): self.targets = list(target)
			elif isinstance(target, list): self.targets = target
			else: self.targets = [target]
		else: self.targets = []
		self.indexTarget = 0 #Every time a new target nodepath is drawn, this increases by 1
		self.np = self.GUI.render.attachNewNode("Event_EmptyNP")
		if np_SubjectIcon := self.make_npSubject(subject, eventType, textSubject, colorSubject):
			self.np_Subject = np_SubjectIcon
			np_SubjectIcon.reparentTo(self.np)
		makeTexCard(self.GUI, filePath="TexCards\\ForGame\\%s.egg" % eventType, pos=(1, 0, 0), scale=1, aspectRatio=1,
					name='EventIcon', getSeqNode=False, poseFrame=0, parent=np_SubjectIcon)

		if textTarget:
			if isinstance(textTarget, (tuple, numpy.ndarray)): textTarget = list(textTarget)
			elif isinstance(textTarget, list): pass
			else: textTarget = [target]
		else: textTarget = ['']
		for obj, s in zip(self.targets, textTarget):
			self.make_npTarget(obj, parent=self.np, text=s, color=colorTarget)

	def make_npSubject(self, subject, eventType, textSubject, colorSubject):
		if subject:
			copy_Subject = subject.selfCopy(subject.ID, None)
			copy_Subject.creator, copy_Subject.attack, copy_Subject.health = subject.creator, subject.attack, subject.health
			copy_Subject.onBoard, copy_Subject.inHand = subject.onBoard, subject.inHand
			if subject.race == "Secret" and self.GUI.need2beHidden(subject):
				filePath = "TexCards\ForGame\\%sSecretCard.png" % subject.Class
			else: filePath = ""
			np_SubjectIcon = genHeroZoneTrigIcon(self.GUI, copy_Subject, pos=(0, 0, 0), text=textSubject, scale=1.2,
												 textColor=colorSubject, filePath=filePath)[0]
		else: np_SubjectIcon = None
		return np_SubjectIcon

	def make_npTarget(self, obj, parent, text='', color=white):
		copy_Target = obj.selfCopy(obj.ID, None)
		copy_Target.creator, copy_Target.attack, copy_Target.health = obj.creator, obj.attack, obj.health
		copy_Target.onBoard, copy_Target.inHand = obj.onBoard, obj.inHand
		if obj.race == "Secret" and self.GUI.need2beHidden(obj):
			filePath = "TexCards\ForGame\\%sSecretCard.png" % obj.Class
		else: filePath = ""
		pos = (x_Target0 + offset_Icon * (self.indexTarget % iconsaRow), -offset_Icon * int(self.indexTarget / iconsaRow), 0)
		self.indexTarget += 1
		genHeroZoneTrigIcon(self.GUI, copy_Target, pos=pos, text=text, scale=1.2, textColor=color, filePath=filePath)[0].reparentTo(parent)

	def reset_SubjectText(self, text, color):
		if self.np_Subject and (nodePath := self.np_Subject.find("Trig Counter_TextNode")):
			nodePath.node().setText(text)
			nodePath.node().setTextColor(color)


class HistoryZone:
	def __init__(self, GUI):
		self.GUI, self.events = GUI, []

	def placeIcons(self, events2Remove=()):  # 创建event和向event中添加target都会重新计算event.numRows
		para, indexRow, indexEvent = Parallel(), -1, 0
		for event in self.events:
			indexRow += max(1, ceil(len(event.targets) / iconsaRow))
			pos = (x_Subject + 0.5 * event.level, y_Subject0 + 1.3 * indexRow, 1.1)
			if indexEvent == 0: para.append(Func(event.np.setPos, pos))
			else: para.append(LerpPosInterval(event.np, duration=0.03, pos=pos))
			indexEvent += 1
		for event in events2Remove:
			if event.np: para.append(Func(event.np.removeNode))
		self.GUI.seqHolder[-1].append(para)

	def add2Event(self, subject, target, textSubject='', textTarget='', colorSubject=white, colorTarget=white):
		#在self.events列表里面寻找第一个subject是这个
		event = next((event for event in self.events if event.subject == subject), None)
		if event:
			if textSubject: event.reset_SubjectText(textSubject, colorSubject)
			if target:
				if isinstance(target, (tuple, numpy.ndarray)): target = list(target)
				elif isinstance(target, list): target = target
				else: target = [target]
				event.targets += target
				if not isinstance(textTarget, (list, tuple, numpy.ndarray)): textTarget = [textTarget]
				for obj, text in zip(target, textTarget):
					event.make_npTarget(obj, parent=event.np, text=text, color=colorTarget)

			self.placeIcons()

	#在添加一个事件icon的时候会
	def eventinGUI(self, subject=None, eventType='', target=None, textSubject='', textTarget='',
				   colorSubject=white, colorTarget=white, level=1):
		gameEvent = GameEvent(GUI=self.GUI, subject=subject, eventType=eventType, target=target, textSubject=textSubject,
							  textTarget=textTarget, colorSubject=colorSubject, colorTarget=colorTarget, level=level)
		self.events.insert(0, gameEvent)

		events2Remove = []
		if len(self.events) > 30:
			events2Remove = self.events[15:]
			self.events = self.events[:15]
		self.placeIcons(events2Remove)
