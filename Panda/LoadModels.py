from direct.interval.FunctionInterval import Func, Wait
from direct.interval.LerpInterval import *
from direct.interval.MetaInterval import Sequence, Parallel
from direct.directutil import Mopath
from direct.interval.MopathInterval import *
from panda3d.core import *
from Parts.ConstsFuncsImports import *

from panda3d.physics import PhysicalNode, PhysicsManager, ParticleSystem, ParticleSystemManager
from panda3d.physics import PointParticleFactory, ZSpinParticleFactory
from panda3d.physics import BaseParticleRenderer, PointParticleRenderer, LineParticleRenderer, \
							GeomParticleRenderer, SparkleParticleRenderer, SpriteParticleRenderer
from panda3d.physics import BaseParticleEmitter, ArcEmitter, BoxEmitter, DiscEmitter, LineEmitter, \
							PointEmitter, RectangleEmitter, RingEmitter, SphereSurfaceEmitter, \
							SphereVolumeEmitter, TangentRingEmitter
from panda3d.physics import SpriteAnim
from panda3d.physics import LinearVectorForce, AngularVectorForce
from direct.particles import ParticleEffect, Particles, ForceGroup

from direct.particles import SpriteParticleRendererExt

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.directtools import DirectSelection

#nodepath.removeNode()&nodepath.detachNode() both remove the nodes and subnodes from the current tree structure
#The node still exists in the memory and will be later garbage collected if no longer referenced
#But removeNode NULLIFIES nodepath itself, nodepath will be None/**removed** after this. Any reference to it will be illegal
#detachNode will leave the nodepath STILL USABLE. Although it will lose all parent infomation

def traverseTree(GUI, nodePath, depth=4, curDepth=1):
	if curDepth == 1:
		x, y, z = nodePath.getPos(GUI.render)
		print('\nALL CHILDREN OF NODEPATH, UP TO DEPTH {}:\n{}   {}, {}, {}'.format(
					depth, nodePath, round(x, 2), round(y, 2), round(z, 2)))
	if depth > 0:
		for child in nodePath.getChildren():
			x, y, z = nodePath.getPos(GUI.render)
			print(('\t'*curDepth+"{}   {}, {}, {}".format(
				child, round(x, 2), round(y, 2), round(z, 2))).replace("{}".format(nodePath), ''))
			traverseTree(GUI, child, depth=depth-1, curDepth=curDepth+1)

#If poseFrame is negative, then the texCard keeps playing
def makeTexCard(GUI, filePath, pos=(0, 0, 0), scale=1.0, aspectRatio=1.0,
				name='', getSeqNode=True, poseFrame=0, parent=None):
	texCard = GUI.loader.loadModel(filePath)
	texCard.name = name + "_TexCard" if name else "TexCard"
	if aspectRatio == 1: texCard.setScale(scale)
	else: texCard.setScale(scale, 1, scale*aspectRatio)
	texCard.setPosHpr(pos, (0, -90, 0))
	texCard.reparentTo(parent if parent else GUI.render)
	if getSeqNode and (a := texCard.find("+SequenceNode")):
		seqNode = texCard.find("+SequenceNode").node()
		if poseFrame > -1: seqNode.pose(poseFrame)
	else: seqNode = None
	return texCard, seqNode

#Can only set the color of the textNode itself to transparent. No point in setting the nodePath transparency
def makeText(np_Parent, textName, valueText, pos, scale, color, font, wordWrap=0, cardColor=None):
	textNode = TextNode(textName + "_TextNode")
	textNode.setText(valueText)
	textNode.setAlign(TextNode.ACenter)
	textNode.setFont(font)
	textNode.setTextColor(color)
	if wordWrap > 0: textNode.setWordwrap(wordWrap)
	if cardColor:
		textNode.setCardColor(cardColor)
		textNode.setCardAsMargin(0, 0.1, 0, -0.10)
		textNode.setCardDecal(True)
	textNodePath = np_Parent.attachNewNode(textNode)
	textNodePath.setScale(scale)
	textNodePath.setPosHpr(pos, Point3(0, -90, 0))
	return textNodePath, textNode

def textNode_SetExpandShrink(textNodePath, textNode, scale_0, scale_1, s, color, duration=0.15):
	return Sequence(Func(textNode.setText, s), Func(textNode.setTextColor, color),
					textNodePath.scaleInterval(duration=duration, scale=scale_1),
					textNodePath.scaleInterval(duration=duration, scale=scale_0)
					)

def textNode_setTextandColor(textNode, text, color):
	textNode.setText(text)
	textNode.setTextColor(color)
	
def reassignBtn2Card(btn, card):
	card.btn = btn
	
"""Subclass the NodePath, since it can be assigned attributes directly"""
class Btn_Card:
	def __init__(self, GUI, card, nodePath):
		self.GUI, self.card = GUI, card
		self.selected = self.isPlayed = False
		self.onlyCardBackShown = False
		
		self.np = nodePath #Load the templates, who won't carry btn and then btn will be assigned after copyTo()
		self.cNode = self.cNode_Backup = self.cNode_Backup_Played = None  #cNode holds the return value of attachNewNode
		self.box = None
		self.models, self.icons, self.texts, self.texCards = {}, {}, {}, {}
		self.texCards_Dyna = []

	#如果需要其在seq/para中，则需要使用Func(btn.changeCard)
	def changeCard(self, card, isPlayed, pickable=True, onlyShowCardBack=False, isUnknownSecret=False):
		self.card, self.isPlayed = card, isPlayed
		self.np.name = "NP_{}_{}".format(type(card).__name__, datetime.now().microsecond)
		loader = self.GUI.loader
		if pickable: card.btn = self
		while self.texCards_Dyna:
			self.texCards_Dyna.pop().removeNode()
		self.reloadModels(loader, findFilepath(card), pickable, onlyShowCardBack)

		if secretTexCard := self.np.find("SecretCard_TexCard"): secretTexCard.removeNode()
		if isUnknownSecret and card.race == "Secret":
			makeTexCard(self.GUI, "TexCards\\ForGame\\%sSecretCard.egg"%card.Class, pos=(0.15, -0.95, 0.09), scale=5.4,
						aspectRatio=518/375, name="SecretCard", getSeqNode=False, parent=self.np)
		self.np.reparentTo(self.GUI.render)
		self.onlyCardBackShown = onlyShowCardBack
	
	def reassignBox(self):
		card = self.card
		for name in ("box", "box_Played", "box_Legendary", "box_Normal", "box_Legendary_Played", "box_Normal_Played"):
			if name in self.models: self.models[name].hide()
		#Power不参与box的重新赋值
		isLegendary, category = "~Legendary" in card.index, card.category
		if category == "Minion":
			if isLegendary: self.box = self.models["box_Legendary_Played" if self.isPlayed else "box_Legendary"]
			else: self.box = self.models["box_Normal_Played" if self.isPlayed else "box_Normal"]
		elif category == "Dormant": self.box = None
		elif category == "Weapon":
			self.box = None if self.isPlayed else self.models["box_Legendary" if isLegendary else "box_Normal"]
		elif category == "Hero": self.box = self.models["box_Played" if self.isPlayed else "box"]
		elif category == "Spell": self.box = self.models["box_Legendary" if isLegendary else "box_Normal"]
		elif category == "Power": self.box = self.models["box"] if self.isPlayed else None

	#For Minion/Dormant/Weapon/Hero.  Spell and Power will need to override this
	def reloadModels(self, loader, imgPath, pickable, onlyShowCardBack):
		card, category = self.card, self.card.category
		if self.cNode:
			self.cNode.removeNode()
			self.cNode = None
		if pickable:
			if category == "Spell": self.cNode = self.np.attachNewNode(self.cNode_Backup)
			else: self.cNode = self.np.attachNewNode(self.cNode_Backup_Played if self.isPlayed else self.cNode_Backup)

		self.reassignBox()
		#If the card is tradeable, then load the Trade model
		np_Trade = self.np.find("Trade")
		if "~Tradeable" in card.index and not self.isPlayed:
			if not np_Trade:
				if card.category == "Minion": pos = (-1.75, 1.05, 0.055)
				elif card.category == "Spell": pos = (-1.7, 1.05, 0.055)
				else: pos = (-1.7, 1.05, 0.077) #card.category == "Weapon"
				(np_Trade := self.GUI.modelTemplates["Trade"].copyTo(self.np)).setPos(pos)
				np_Trade.find("box").hide()
		elif np_Trade: np_Trade.removeNode()

		isLegendary = "~Legendary" in card.index
		if "legendaryIcon" in self.models:
			if isLegendary: self.models["legendaryIcon"].show()
			else: self.models["legendaryIcon"].hide()

		cardTexture = loader.loadTexture(imgPath)
		for name in ("card", "cardImage", "nameTag", "description"):
			if name in self.models: self.models[name].setTexture(self.models[name].findTextureStage('*'), cardTexture, 1)
		#一定会显示的。不过Hero没有nameTag
		for name in ("frame", "cardImage", "nameTag"):
			if name in self.models: self.models[name].show()
		for name in ("card", "cardBack", "mana"):
			if name in self.models:
				if self.isPlayed: self.models[name].hide()
				else: self.models[name].show()
		if "stats_Played" in self.models:
			if self.isPlayed and category != "Dormant": self.models["stats_Played"].show()
			else: self.models["stats_Played"].hide()
		if "stats" in self.models:
			if not self.isPlayed and category != "Dormant": self.models["stats"].show()
			else: self.models["stats"].hide()
		# Those models that require special treatment
		if category not in ("Spell", "Hero"):
			for name in ("Hourglass", "Trigger", "Lifesteal", "Deathrattle", "Poisonous", "SpecTrig"):
				if name in self.icons: self.icons[name].np.hide()

		if category == "Hero":
			if not self.isPlayed:
				self.models["frame"].hide()
				self.models["cardImage"].hide()
			else:
				self.models["cardImage"].setTexture(self.models["cardImage"].findTextureStage('*'),
													loader.loadTexture("Images\\HeroesandPowers\\%s.png" % type(card).__name__), 1)
		elif category == "Power":
			self.models["mana"].show()
			self.models["cardBack"].hide()
			if self.isPlayed: self.models["nameTag"].hide()
		elif category == "Weapon":
			self.models["card"].setTexture(self.models["card"].findTextureStage('*'), self.GUI.textures["weapon_"+card.Class], 1)
			if self.isPlayed: self.models["description"].hide()
		# Change the card textNodes no matter what (non-mutable texts are empty anyways)
		if "description" in self.texts: self.texts["description"].node().setText('' if self.isPlayed else str(card.text()))

		if category == "Dormant": # 休眠物不进行数值显示
			for text in self.texts.values(): text.node().setText('')
		else:
			hideMana = card.mana < 0 or (self.isPlayed and not category == "Power")
			(textNode_Mana := self.texts["mana"].node()).setText('' if hideMana else str(card.mana))
			if not hideMana: textNode_Mana.setTextColor(white if card.mana == card.mana_0 else (green if card.mana < card.mana_0 else red))

			if category in ("Minion", "Weapon", "Hero"):
				color_Attack = white if card.attack <= card.attack_0 else green
				color_Health = red if card.health < card.health_max else (green if card.health_max > card.health_0 else white)
				if "attack" in self.texts:
					(textNode_Attack := self.texts["attack"].node()).setText(str(card.attack) if not self.isPlayed else '')
					textNode_Attack.setTextColor(color_Attack)
				if "attack_Played" in self.texts:
					s = '' if not self.isPlayed or (category == "Hero" and card.attack < 1) else str(card.attack)
					(textNode_Attack_Played := self.texts["attack_Played"].node()).setText(s)
					textNode_Attack_Played.setTextColor(color_Attack)
				if "health" in self.texts:
					(textNode_Health := self.texts["health"].node()).setText(str(card.health) if not self.isPlayed else '')
					textNode_Health.setTextColor(color_Health)
				if "health_Played" in self.texts:
					(textNode_Health_Played := self.texts["health_Played"].node()).setText(str(card.health) if self.isPlayed else '')
					textNode_Health_Played.setTextColor(color_Health)
			if category == "Hero": #Hero没有名为stats_played的model，因为攻击和护甲需要单独显示
				if self.isPlayed and card.attack > 0: self.models["attack_Played"].show()
				else: self.models["attack_Played"].hide()
				if self.isPlayed: self.models["health_Played"].show()
				else: self.models["health_Played"].hide()
				if self.isPlayed and card.armor > 0: self.models["armor_Played"].show()
				else: self.models["armor_Played"].hide()

				self.texts["armor"].node().setText(str(card.armor) if not self.isPlayed else '')
				self.texts["armor_Played"].node().setText(str(card.armor) if card.armor > 0 and self.isPlayed else '')

		if onlyShowCardBack:
			for model in self.models.values(): model.hide()
			if not self.isPlayed:
				for textNodePath in self.texts.values(): textNodePath.node().setText('')
			if np_Trade: np_Trade.removeNode()
			self.models["cardBack"].show()

	def effectChangeAni_Shared(self, name, para):
		card = self.card
		if not name or name == "Cost Health Instead":
			if effectOn := not self.isPlayed and card.inHand and card.effects["Cost Health Instead"] > 0:
				if not (model_Blood := self.np.find("BloodBloomHealth")):
					model_Blood = self.GUI.loader.loadModel("Models\\BloodBloomHealth.glb")
					model_Blood.name = "BloodBloomHealth"
					model_Blood.setTexture(model_Blood.findTextureStage("*"),
										   self.GUI.loader.loadTexture("Models\\MinionModels\\Stats.png"), 1)
					model_Blood.reparentTo(self.np)
					model_Blood.hide()
				para.append(Func(model_Blood.show))
			elif model_Blood := self.np.find("BloodBloomHealth"):
				para.append(Func(model_Blood.removeNode))
			
			if effectOn: self.checkTexCard("Cost Health Instead")
			para.append(Func(self.texCardAni_LoopPose, "Cost Health Instead", effectOn))
		if not name or name == "Unplayable":
			if on := not self.isPlayed and card.inHand and card.effects["Unplayable"] > 0:
				self.checkTexCard("Unplayable")
			para.append(Func(self.texCardAni_OnOff, "Unplayable", on))

	def texCardAni_LoopPose(self, name, start=True):
		if name in self.texCards:
			seqNode = self.texCards[name].find("+SequenceNode").node()
			if start: seqNode.loop(False, 1, seqNode.getNumFrames()-1)
			else: seqNode.pose(0)

	def texCardAni_OnOff(self, name, on=True): #The texture cards only has two frames, 0~On, 1~Off
		if name in self.texCards:
			self.texCards[name].find("+SequenceNode").node().pose(1 if on else 0)

	def texCardAni_PlayPlay(self, name, end_Gain, start_Lose, end_Lose, gain=True):
		if name in self.texCards:
			seqNode = self.texCards[name].find("+SequenceNode").node()
			if gain and 0 <= seqNode.getFrame() < end_Gain: seqNode.play(seqNode.getFrame(), end_Gain)
			elif not gain and 0 < seqNode.getFrame() <= end_Gain: seqNode.play(start_Lose, end_Lose)
	
	def texCardAni_LoopPlay(self, name, end_Gain, start_Lose, end_Lose, gain=True):
		if name in self.texCards:
			seqNode = self.texCards[name].find("+SequenceNode").node()
			if gain: seqNode.loop(False, 1, end_Gain)
			elif not gain and 0 < seqNode.getFrame() <= end_Gain: seqNode.play(start_Lose, end_Lose)
	
	def addaStatusTexCard2Top(self, texCard_New, seqNode_New, num_0, num_1, playnotLoop, x_New, y_New, textNodePath=None):
		i = 0
		for texCard in self.texCards_Dyna[:]:
			seqNode = texCard.find("+SequenceNode").node()
			if seqNode.isPlaying() or seqNode.getFrame() != seqNode.getNumFrames() - 1:
				x, y, z = texCard.getPos()
				texCard.setPos(x, y, 0.17+i*0.06)
				i += 1
		texCard_New.setPos(x_New, y_New, 0.17+i*0.06)
		texCard_New.reparentTo(self.np)
		if playnotLoop:
			if textNodePath: Sequence(Wait(33/24), Func(textNodePath.removeNode)).start()
			Sequence(Func(seqNode_New.play, num_0, num_1), Wait(seqNode_New.getNumFrames()/seqNode_New.getFrameRate()),
					 Func(removefrom, texCard_New, self.texCards_Dyna), Func(texCard_New.removeNode)).start()
		else: seqNode_New.loop(num_0, num_1)
		
	def dimDown(self):
		self.np.setColor(grey)

	#Cards sometimes disappear and show up again immediately. Need to make sure card.btn and self.np are nullified.
	#Otherwise, the card might not be correctly re-genereated and left with a removed nodepath, raising an error.
	def add2Queue_NullifyBtnNodepath(self, seqPara):
		if nodepath := self.np:
			self.np = None
			if self.card: self.card.btn = None
			seqPara.append(Func(nodepath.removeNode))

	def setBoxColor(self, color):
		if self.box:
			if color == transparent: self.box.hide()
			else:
				self.box.show()
				self.box.setColor(color)

	def showStatus(self):
		pass
	
	def rightClick(self):
		if self.GUI.stage in (1, 2): self.GUI.cancelSelection()
		else: self.GUI.drawCardZoomIn(self)
	
	def manaChangeAni(self, mana_1):  #mana_1 is the value the mana changes to
		btn = (card := self.card).btn
		if not btn or btn.onlyCardBackShown: return  #If the btn doesn't exist anymore, skip the rest
		nodePath, scale_0 = btn.texts["mana"], statTextScale if card.category != "Power" else 0.857 * statTextScale
		seq = textNode_SetExpandShrink(textNodePath=nodePath, textNode=nodePath.node(),
										scale_0=scale_0, scale_1=2*statTextScale, s=str(mana_1),
										color=white if card.mana == card.mana_0 else (red if card.mana > card.mana_0 else green))
		self.GUI.seqHolder[-1].append(Func(seq.start))
		self.GUI.seqHolder[-1].append(Wait(0.03))

	#Minion actions: "set"|"buffDebuff"|"damage"|"heal"
	#Weapon actions: "buffDebuff"|"damage"
	#Hero actions: "set"|"buffDebuff"|"damage"|"heal
		#无论什么时候都应该检测角色的身材。如果角色的攻击力有变化，则始终应该有其数值的大小变化；而生命值/耐久的变化则视action类型而定
	def statChangeAni(self, num1=0, num2=0, action="set"):
		category = (card := self.card).category
		#如果卡牌在手中且只显示卡背，则终止；另外若卡牌既不是不是场上的英雄/休眠物，也不是手牌/场上的随从/武器，则也会终止
		if (card.inHand and self.onlyCardBackShown) \
				or not ((category in ("Hero", "Dormant") and card.onBoard and self.isPlayed)
						or (category in ("Minion", "Weapon") and (card.inHand or card.onBoard))):
			return
		#决定卡牌的攻击/血量的文字显示和其颜色
		attack, health = card.attack, card.health
		color_Attack = white if card.attack <= card.attack_0 else green
		color_Health = red if health < card.health_max else (white if card.health_max <= card.health_0 else green)
		if category == "Hero": s_attack, s_health = '' if attack < 1 else str(attack), str(health)
		else: s_attack, s_health = '' if category == "Dormant" else str(attack), '' if category == "Dormant" else str(health)
		npText_Attack_Played, npText_Health_Played = self.texts["attack_Played"], self.texts["health_Played"]
		nodeText_Attack_Played, nodeText_Health_Played = self.texts["attack_Played"].node(), self.texts["health_Played"].node()

		self.GUI.seqHolder[-1].append((para := Parallel()))
		self.GUI.seqHolder[-1].append(Wait(0.05))
		scale_0 = {"Hero": 1.1, "Weapon": 0.9, "Minion": 0.8, "Dormant": 0.8}[category] if self.isPlayed else statTextScale

		#需要检测是否有模型的显示/隐藏。因为涉及到英雄的攻击/护甲值、和休眠物的攻击/生命值隐藏
		if category == "Hero":
			para.append(Func(self.models["attack_Played"].show if attack > 0 else self.models["attack_Played"].hide))
			para.append(Func(self.models["armor_Played"].hide if card.armor < 1 else self.models["armor_Played"].show))
		else: para.append( Func(self.models["stats_Played"].hide if category == "Dormant" else self.models["stats_Played"].show))
		#无论什么时候都要检测攻击力的变化，如果真的发生变化，则需要涉及textNode的大小变化
		if self.isPlayed: npText, nodeText = npText_Attack_Played, nodeText_Attack_Played
		else: npText, nodeText = self.texts["attack"], self.texts["attack"].node()
		s = '' if category == "Hero" and attack < 1 else str(attack)
		if num1: para.append(Func(textNode_SetExpandShrink(npText, nodeText, scale_0, 1.8 * scale_0, s, color_Attack).start))
		else: para.append(Func(textNode_setTextandColor, nodeText, s, color_Attack))
		"""根据卡牌category和action来决定对生命值和护甲值的显示、变动方法"""
		if action in ("set", "buffDebuff"):  #一般的攻击力和耐久度重置计算也可以用set，只是需要把num1和num2设为0
			if not self.isPlayed and action == "buffDebuff":
				scale = self.np.getScale()[0]
				para.append(Sequence(LerpScaleInterval(self.np, duration=0.17, scale=1.2*scale), LerpScaleInterval(self.np, duration=0.17, scale=scale)))
			if self.isPlayed: npText, nodeText = npText_Health_Played, nodeText_Health_Played
			else: npText, nodeText = self.texts["health"], self.texts["health"].node()
			if num2: para.append(Func(textNode_SetExpandShrink(npText, nodeText, scale_0, 1.8 * scale_0, str(health), color_Health).start))
			else: para.append(Func(textNode_setTextandColor, nodeText, str(health), color_Health))
		else: #damage|healing|armorChange
			if not self.isPlayed: return
			if category == "Hero": #英雄需要额外处理自己的护甲值显示
				armor, npText_Armor_Played, nodeText_Armor_Played = card.armor, self.texts["armor_Played"], self.texts["armor_Played"].node()
				s_Armor = '' if armor < 1 else str(armor)
				if action == "armorChange":
					para.append(Func(textNode_SetExpandShrink(npText_Armor_Played, nodeText_Armor_Played, 1.1, 1.8 * 1.1, s_Armor, white).start))
				else: para.append(Func(nodeText_Armor_Played.setText, s_Armor))

			if category == "Weapon": s, color, texCardName, num = '', white, '', 48
			elif action == "poisonousDamage": s, color, texCardName, num = '', white, "DamagePoisonous", 48 #Only for minions
			elif action == "damage": s, color, texCardName, num = str(num2), red, "Damage", 48
			elif action == "heal": s, color, texCardName, num = '+' + str(num2), black, "Healing", 32 #heal
			else: s, color, texCardName, num = '', white, '', 0
			#生命值的显示不会有大小的变化
			para.append(Func(textNode_setTextandColor, nodeText_Health_Played, str(health), color_Health))
			if texCardName:
				texCard, seqNode = makeTexCard(self.GUI, "TexCards\\Shared\\%s.egg" % texCardName, scale=3 if category == "Minion" else 4.5)
				textNodePath = None
				if s: (textNodePath := makeText(np_Parent=texCard, textName='', valueText=s, pos=(0, -0.01, -0.05), scale=0.25, color=color,
												font=self.GUI.getFont())[0]).setHpr(0, 0, 0)
				para.append(Func(self.addaStatusTexCard2Top, texCard, seqNode, 1, num, True, 0.15, 0.45 if category == "Minion" else 0.25, textNodePath))

	def checkTexCard(self, name):
		if name and name not in self.texCards:
			category = self.card.category
			if name in ("Cost Health Instead", "Unplayable"):
				category = "Common"

			if name in self.GUI.cardTex[category]:
				texCard = self.GUI.cardTex[category][name].copyTo(self.np)
			else: #GUI.cardTex还没有加载完毕，需要加载后给自己和GUI.cardTex和一份
				GUI, posScale = self.GUI, tableTexCards[category][name]
				if category == "Hero": filepath = "TexCards\\For%ses\\%s.egg"%(category, name)
				elif category == "Common": filepath = "TexCards\\Shared\\%s.egg"%name
				else: filepath = "TexCards\\For%ss\\%s.egg"%(category, name)
				self.GUI.cardTex[category][name] = texCard = makeTexCard(GUI, filepath, pos=posScale[1], scale=posScale[0], name=name)[0]
				texCard = texCard.copyTo(self.np)
			self.texCards[name] = texCard

	def placeIcons(self):
		card, category = self.card, self.card.category
		if not self.isPlayed and category in ("Hero", "Spell"): return
		card, para, icons = self.card, Parallel(name="Icon Placing Ani"), []
		#Minion/Weapon/Power
		if self.isPlayed and any(trig.connected and trig.counter > -1 for trig in card.trigsBoard):
			btn_Icon = self.icons["Hourglass"]
			para.append(btn_Icon.seqUpdateText(s='', animate=False))
			icons.append(btn_Icon)
		else: para.append(Func(self.icons["Hourglass"].np.hide))
		if self.isPlayed and any(trig.connected and trig.show and trig.counter < 0 and not trig.oneTime for trig in card.trigsBoard):
			icons.append(self.icons["Trigger"])
		else: para.append(Func(self.icons["Trigger"].np.hide))
		#视category决定是否显示吸血，亡语，剧毒和一次性扳机
		if "Lifesteal" in self.icons:
			if self.isPlayed and category in ("Minion", "Weapon", "Power") and card.effects["Lifesteal"] > 0:
				icons.append(self.icons["Lifesteal"])
			else: para.append(Func(self.icons["Lifesteal"].np.hide))
		if "Deathrattle" in self.icons:
			if self.isPlayed and category in ("Minion", "Weapon") and card.deathrattles:
				icons.append(self.icons["Deathrattle"])
			else: para.append(Func(self.icons["Deathrattle"].np.hide))
		if "Poisonous" in self.icons:
			if self.isPlayed and category in ("Minion", "Weapon") and card.effects["Poisonous"] > 0:
				icons.append(self.icons["Poisonous"])
			else: para.append(Func(self.icons["Poisonous"].np.hide))
		if "SpecTrig" in self.icons:
			if self.isPlayed and category in ("Minion", "Weapon") and any(trig.connected and trig.oneTime for trig in card.trigsBoard):
				para.append(Func(self.icons["SpecTrig"].np.find("SpecTrig").show))
				icons.append(self.icons["SpecTrig"])
			else: para.append(Func(self.icons["SpecTrig"].np.hide))
		#Place the icons beneath the cardImage
		nameTagModel = self.models["nameTag"] if category in ("Minion", "Weapon") else None
		if icons:
			if nameTagModel:
				darkNameTagImg = "Models\\%sModels\\DarkNameTag.png"%category
				para.append(Func(nameTagModel.setTexture, nameTagModel.findTextureStage('0'),
							 	self.GUI.loader.loadTexture(darkNameTagImg), 1))
			leftMostPos = 0.12 - 0.6 * (len(icons) - 1) / 2
			for i, model in enumerate(icons):
				para.append(Func(model.np.show))
				x = leftMostPos + i * 0.6
				if category == "Weapon": para.append(Func(model.np.setPos, x, -1.13, 0.125))
				elif category == "Power": para.append(Func(model.np.setPos, x, -1, 0.11))
				else: para.append(Func(model.np.setPos, x, x2y_MinionNameTagCurve(x, coeffs_Curve), 0.115))
		elif nameTagModel:
			para.append(Func(nameTagModel.setTexture, nameTagModel.findTextureStage('*'),
							self.GUI.loader.loadTexture(findFilepath(card)), 1))

		if self.GUI.seqHolder: self.GUI.seqHolder[-1].append(para)
		else: para.start()

	def makeMoPathIntervals(self, curveFileName, duration=0.3):
		moPath = Mopath.Mopath()
		moPath.loadFile(curveFileName)
		return MopathInterval(moPath, self.np, duration=duration)


def loadCard(base, card):
	return {"Minion": loadMinion, "Spell": loadSpell, "Weapon": loadWeapon, "Hero": loadHero,
			"Power": loadPower, "Option": loadOption,
			}[card.category](base)

tableTexCards = {"Minion": {"Aura": (5.8, (0, 0.3, -0.03)),
							"Taunt": (5.5, (0.05, -0.05, 0)),
							"Frozen": (5.2, (0, 0.55, 0.07)),
							"Immune": (4.5, (0.05, 0.5, 0.08)),
							"Stealth": (4.2, (0.1, 0.5, 0.09)),
							"Divine Shield": (7.3, (0.05, 0.2, 0.10)),
							"Silenced": (4, (0, 0, 0.11)),
							"Exhausted": (5, (0.1, 0.5, 0.12)),
							"Spell Damage": (4, (0, 1, 0.13)),

							"SilencedText": (2.4, (0.08, -2.85, 0.11)),
							},
				 "Weapon": {"Immune": (3.7, (0.1, 0.3, 0.12)),
							},
				 "Spell": {},
				 "Power": {"Power Damage": (3.5, (0, 0.25, 0.13)),
							"Can Target Minions": (2, (0, 0.25, 0.11)),
							},
				 "Hero": {"Breaking": (4.3, Point3(0, 0.27, 0.01)),
						  "Frozen": (8, Point3(-0.1, 0.2, 0.06)),
						  "Immune": (5.2, Point3(0, 0.3, 0.07)),
						  "Stealth": (5.5, Point3(0, 0.15, 0.08)),
						  "Spell Damage": (4.8, Point3(0, 0.2, 0.09)),
						  },
				 "Common": {"Cost Health Instead": (2.6, (-1.77, 1.75, 0.09)),
							"Unplayable": (3.7, (0, -0.5, 0.09)), }
				 }
#Minion: cardImage y limit -0.06; nameTag -0.07; stats_Played -0.12
#Weapon: cardImage y limit -0.09; nameTag -0.095; stats_Played -0.13


#Need to calculate the curve in order to align the trig icons with the name tag
arr_x = numpy.array([-1, -0.44, 0.12, 1.24])
arr_y = numpy.array([-1.37, -1.26, -1.17, -1.12])
arr = numpy.array([[x**3, x**2, x**1, 1] for x in arr_x])
coeffs_Curve = numpy.linalg.solve(arr, arr_y)

def x2y_MinionNameTagCurve(x, coeffs):
	return coeffs[0] * x ** 3 + coeffs[1] * x ** 2 + coeffs[2] * x + coeffs[3]

class Btn_Minion(Btn_Card):
	def __init__(self, GUI, card, nodePath):
		super().__init__(GUI, card, nodePath)
		
		self.cNode_Backup = CollisionNode("cNode")
		self.cNode_Backup.addSolid(CollisionBox((0.05, -1.1, 0), 2.2, 3.1, 0.1))
		self.cNode_Backup_Played = CollisionNode("cNode_Played")
		self.cNode_Backup_Played.addSolid(CollisionBox((0.07, 0.35, 0), 1.5, 1.9, 0.1))
		#self.cNode = self.attachNewNode(self.cNode_Backup)

	def leftClick(self):
		if self.card.category != "Minion": return
		self.selected = not self.selected
		GUI, card = self.GUI, self.card
		stage, game = GUI.stage, GUI.Game
		if self.isPlayed: #When the minion is on board
			if stage == 0 or stage == 2: self.GUI.resolveMove(self.card, self, "MiniononBoard")
			elif stage == 3 and card in game.options: GUI.resolveMove(card, None, "DiscoverOption")
		else: #When the minion is in hand
			if stage == -2:  # 组建套牌中
				GUI.deckBuilder.addaCard(type(card))
			elif stage == -1:
				self.setBoxColor(red if self.selected else green)
				GUI.mulliganStatus[card.ID][game.mulligans[card.ID].index(card)] = 1 if self.selected else 0
			elif stage == 0: GUI.resolveMove(card, self, "MinioninHand")
			elif stage == 3 and card in game.options: GUI.resolveMove(card, None, "DiscoverOption")

	#需要用inverval.start
	def effectChangeAni(self, name=''):
		if self.card.category != "Minion": return
		card, para = self.card, Parallel(name="Status Change Ani")
		self.effectChangeAni_Shared(name, para) #Cost Health Instead and Unplayable
		#Handle the loop(False)/pose(0) category of texCards: Aura, Immune, Stealth, Exhausted, Silenced
		if not name or name == "Aura":  #Check the Aura animation
			if on := self.isPlayed and card.onBoard and card.auras:
				self.checkTexCard("Aura")
			para.append(Func(self.texCardAni_LoopPose, "Aura", on))
		if not name or name == "Immune":
			if on := self.isPlayed and card.onBoard and card.effects["Immune"] > 0:
				self.checkTexCard("Immune")
			para.append(Func(self.texCardAni_LoopPose, "Immune", on))
		if not name or name == "Spell Damage":
			if on := self.isPlayed and card.onBoard and card.effects["Spell Damage"] + card.effects["Nature Spell Damage"] > 0:
				self.checkTexCard("Spell Damage")
			para.append(Func(self.texCardAni_LoopPose, "Spell Damage", on))
		if not name or name == "Stealth":
			if on := self.isPlayed and card.onBoard and (card.effects["Stealth"] > 0 or card.effects["Temp Stealth"] > 0):
				self.checkTexCard("Stealth")
			para.append(Func(self.texCardAni_LoopPose, "Stealth", on))
		if not name or name in ("Exhausted", "Rush", "Charge"):
			if on := self.isPlayed and card.onBoard and card.enterBoardTurn >= card.Game.turnInd and not card.actionable():
				self.checkTexCard("Exhausted")
			para.append(Func(self.texCardAni_LoopPose, "Exhausted", on))
		if not name or name == "Silenced":
			if on := self.isPlayed and card.onBoard and card.silenced:
				self.checkTexCard("Silenced")
			para.append(Func(self.texCardAni_LoopPose, "Silenced", on))
			if on := not self.isPlayed and card.silenced:
				self.checkTexCard("SilencedText")
			para.append(Func(self.texCardAni_OnOff, "SilencedText", on))

		#Handle the play(num1, num2)/play(num1, num2) category of texCards: Divine Shield, Taunt
		if not name or name == "Divine Shield":
			if card.onBoard and self.isPlayed and card.effects["Divine Shield"] > 0:
				self.checkTexCard("Divine Shield")
				para.append(Func(self.texCardAni_PlayPlay, "Divine Shield", 23, 24, 29, True))
			else: para.append(Func(self.texCardAni_LoopPose, "Divine Shield", False))
		if not name or name == "Taunt":
			if card.onBoard and self.isPlayed and card.effects["Taunt"] > 0:
				self.checkTexCard("Taunt")
				para.append(Func(self.texCardAni_PlayPlay, "Taunt", 13, 14, 28, True))
			else: para.append(Func(self.texCardAni_LoopPose, "Taunt", False))
		#Handle the loop(False, num1, num2)/play(num1, num2) category of texCards: Frozen
		if not name or name == "Frozen":
			if card.onBoard and self.isPlayed and card.effects["Frozen"] > 0:
				self.checkTexCard("Frozen")
				para.append(Func(self.texCardAni_LoopPlay, "Frozen", 96, 97, 105, True))
			else: para.append(Func(self.texCardAni_LoopPose, "Frozen", False))
			
		if self.GUI.seqHolder: self.GUI.seqHolder[-1].append(para)
		else: para.start()
	
	def decideColor(self):
		color, card = transparent, self.card
		if card.category != "Minion": return color
		game = card.Game
		if card.ID == game.turn:
			if card.inHand:
				if game.Manas.affordable(card) and game.space(card.ID) > 0:
					color = yellow if card.effectViable else green
			elif card.canAttack():
				if card.effects["Can't Attack Hero"] > 0 or (card.enterBoardTurn >= game.turnInd and card.effects["Rush"] > 0 and
															 card.effects["Borrowed"] + card.effects["Charge"] < 1):
					color = darkGreen #如果随从可以攻击但是不能攻击对方英雄，即有“不能直接攻击英雄”或者是没有冲锋或暗影狂乱的突袭随从
				else: color = green #If this is a minion that is on board
		return color

		
statTextScale = 1.05
manaPos = Point3(-2.8, 3.85, -0.15)
healthPos = Point3(3.1, -4.95, -0.2)
attackPos = Point3(-2.85, -4.95, -0.15)


#loadMinion, etc will prepare all the textures and trigIcons to be ready.
def loadMinion(base):
	loader = base.loader
	font = base.getFont()
	root = loader.loadModel("Models\\MinionModels\\Minion.glb")
	root.name = "NP_Minion"
	
	#Model names: box_Legendary, box_Legendary_Played, box_Normal, box_Normal_Played
	# card, cardBack, cardImage, legendaryIcon, nameTag, stats, stats_Played
	for model in root.getChildren():
		#model.setTransparency(True)
		#Only retexture the cardBack, legendaryIcon, stats, stats_Played models.
		#These models will be shared by all minion cards.
		if model.name == "cardBack": texture = base.textures["cardBack"]
		elif model.name in ("legendaryIcon", "mana", "stats", "stats_Played", "frame"): texture = base.textures["stats_Minion"]
		else: continue
		model.setTexture(model.findTextureStage('*'), texture, 1)
	
	makeText(root, "mana", '0', pos=(-1.77, 1.15, 0.1), scale=statTextScale,
			 color=white, font=font)
	makeText(root, "attack", '0', pos=(-1.63, -4.05, 0.09), scale=statTextScale,
			 color=white, font=font)
	makeText(root, "health", '0', pos=(1.85, -4.05, 0.09), scale=statTextScale,
			 color=white, font=font)
	makeText(root, "attack_Played", '0', pos=(-1.2, -0.74, 0.122), scale=0.8,
			 color=white, font=font)
	makeText(root, "health_Played", '0', pos=(1.32, -0.74, 0.122), scale=0.8,
			 color=white, font=font)
	makeText(root, "description", "", pos=(0.7, -2, 0.1), scale=0.5,
			 color=black, font=font, wordWrap=12, cardColor=yellow)
	
	for name in ("Hourglass", "Trigger", "SpecTrig", "Deathrattle", "Lifesteal", "Poisonous"):
		base.modelTemplates[name].copyTo(root)

	#After the loading, the NP_Minion root tree structure is:
	#NP_Minion/card|stats|cardImage, etc
	#NP_Minion/mana_TextNode|attack_TextNode, etc
	#NP_Minion/Trigger_Icon|Deathrattle_Icon, etc
	#NP_Minion/Aura_TexCard, etc
	return root


"""Load Spell Cards"""
class Btn_Spell(Btn_Card):
	def __init__(self, GUI, card, nodePath):
		super().__init__(GUI, card, nodePath)
		
		self.cNode_Backup = CollisionNode("cNode")
		self.cNode_Backup.addSolid(CollisionBox((0.05, -1.1, 0), 2.2, 3.1, 0.1))

	def leftClick(self):
		self.selected = not self.selected
		GUI, card = self.GUI, self.card
		if GUI.stage == -2:  # 组建套牌中
			GUI.deckBuilder.addaCard(type(card))
		elif GUI.stage == -1:
			self.setBoxColor(red if self.selected else green)
			GUI.mulliganStatus[card.ID][GUI.Game.mulligans[card.ID].index(card)] = 1 if self.selected else 0
		elif GUI.stage == 0: GUI.resolveMove(card, self, "SpellinHand")
		elif GUI.stage == 3 and card in GUI.Game.options: GUI.resolveMove(card, None, "DiscoverOption")

	def effectChangeAni(self, name=''):
		card, para = self.card, Parallel(name="Status Change Ani")
		self.effectChangeAni_Shared(name, para)

		if self.GUI.seqHolder: self.GUI.seqHolder[-1].append(para)
		else: para.start()

	def decideColor(self):
		color, card = transparent, self.card
		if card.ID == card.Game.turn and card.inHand:
			if card.inHand and card.Game.Manas.affordable(card) and card.available():
				color = yellow if card.effectViable else green
		return color
		
		
def loadSpell(base):
	loader = base.loader
	font = base.getFont()
	root = loader.loadModel("Models\\SpellModels\\Spell.glb")
	root.name = "NP_Spell"
	
	#Model names: box_Legendary, box_Normal, card, cardBack, legendaryIcon, mana
	for model in root.getChildren():
		#model.setTransparency(True)
		if model.name == "cardBack": texture = base.textures["cardBack"]
		elif model.name in ("mana", "legendaryIcon"): texture = base.textures["stats_Spell"]
		else: continue
		model.setTexture(model.findTextureStage('*'), texture, 1)
	
	makeText(root, "mana", '0', pos=(-1.72, 1.2, 0.1), scale=statTextScale,
			 color=white, font=font, wordWrap=0)
	makeText(root, "description", '', pos=(0.7, -2, 0.1), scale=0.5,
			 color=black, font=font, cardColor=yellow)

	#After the loading, the NP_Spell root tree structure is:
	#NP_Spell/card|cardBack|legendaryIcon, etc
	#NP_Spell/mana_TextNode|description_TextNode
	return root



"""Load Weapon Cards"""
class Btn_Weapon(Btn_Card):
	def __init__(self, GUI, card, nodePath):
		super().__init__(GUI, card, nodePath)
		
		self.cNode_Backup = CollisionNode("cNode")
		self.cNode_Backup.addSolid(CollisionBox((0.05, -1.1, 0), 2.2, 3.1, 0.1))
		self.cNode_Backup_Played = CollisionNode("cNode_Played")
		self.cNode_Backup_Played.addSolid(CollisionBox((0.07, 0.33, 0), 1.8, 1.8, 0.1))

	def leftClick(self):
		if not self.isPlayed:
			self.selected = not self.selected
			GUI, card = self.GUI, self.card
			game = GUI.Game
			if GUI.stage == -2:  # 组建套牌中
				GUI.deckBuilder.addaCard(type(card))
			elif GUI.stage == -1:
				self.setBoxColor(red if self.selected else green)
				GUI.mulliganStatus[card.ID][game.mulligans[card.ID].index(card)] = 1 if self.selected else 0
			elif GUI.stage == 0: GUI.resolveMove(card, self, "WeaponinHand")
			elif GUI.stage == 3 and card in game.options: GUI.resolveMove(card, None, "DiscoverOption")

	#需要用inverval.start
	def effectChangeAni(self, name=''):
		card, para = self.card, Parallel(name="Status Change Ani")
		self.effectChangeAni_Shared(name, para)
		if not name or name == "Immune":
			if on := self.isPlayed and card.onBoard and card.effects["Immune"] > 0:
				self.checkTexCard("Immune")
			para.append(Func(self.texCardAni_LoopPose, "Immune", on))

		if self.GUI.seqHolder: self.GUI.seqHolder[-1].append(para)
		else: para.start()

	def decideColor(self):
		if self.isPlayed: return transparent
		color, card = transparent, self.card
		if card.inHand and card.ID == card.Game.turn and card.Game.Manas.affordable(card):
			color = yellow if card.effectViable else green
		return color
		
		
def loadWeapon(base):
	loader = base.loader
	font = base.getFont()
	root = loader.loadModel("Models\\WeaponModels\\Weapon.glb")
	root.name = "NP_Weapon"
	
	#Model names: border, box_Legendary, box_Normal, card, cardBack, cardImage, description,
	# legendaryIcon, nameTag, stats, stats_Played
	for model in root.getChildren():
		#model.setTransparency(True)
		if model.name == "cardBack": texture = base.textures["cardBack"]
		elif model.name in ("frame", "legendaryIcon", "stats", "stats_Played"): texture = base.textures["stats_Weapon"]
		else: continue
		model.setTexture(model.findTextureStage('*'), texture, 1)
		
	makeText(root, "mana", '0', pos=(-1.75, 1.23, 0.1), scale=statTextScale,
			  color=white, font=font)
	makeText(root, "attack", '0', pos=(-1.7, -4, 0.12), scale=statTextScale,
			  color=white, font=font)
	makeText(root, "health", '0', pos=(1.8, -4, 0.12), scale=statTextScale,
			  color=white, font=font)
	makeText(root, "attack_Played", '0', pos=(-1.28, -0.8, 0.132), scale=0.9,
			  color=white, font=font)
	makeText(root, "health_Played", '0', pos=(1.27, -0.8, 0.132), scale=0.9,
				  color=white, font=font)
	makeText(root, "description", '', pos=(0.7, -2, 0.1), scale=0.5,
				  color=black, font=font, cardColor=yellow)
	
	for name in ("Hourglass", "Trigger", "SpecTrig", "Deathrattle", "Lifesteal", "Poisonous"):
		base.modelTemplates[name].copyTo(root)

	#After the loading, the NP_Weapon root tree structure is:
	#NP_Weapon/card|stats|cardImage, etc
	#NP_Weapon/mana_TextNode|attack_TextNode, etc
	#NP_Weapon/Trigger_Icon|Deathrattle_Icon, etc
	return root


"""Load Hero Powers"""
class Btn_Power(Btn_Card):
	def __init__(self, GUI, card, nodePath):
		super().__init__(GUI, card, nodePath)
		
		self.cNode_Backup = CollisionNode("cNode")
		self.cNode_Backup.addSolid(CollisionBox((0, -1.6, 0), 2.3, 3, 0.1))
		self.cNode_Backup_Played = CollisionNode("cNode_Played")
		self.cNode_Backup_Played.addSolid(CollisionBox((0, 0.3, 0), 1.6, 1.6, 0.1))

	def checkHpr(self):
		hprFinal = None
		if self.card.ID == self.GUI.Game.turn:
			if self.card.chancesUsedUp() and self.np.get_r() < 180:
				hprFinal = (0, 0, 180)  #Flip to back, power unusable
			elif not self.card.chancesUsedUp() and self.np.get_r() > 0:
				hprFinal = (0, 0, 0) #Flip to front
		if hprFinal:
			x, y, z = self.GUI.heroZones[self.card.ID].powerPos
			interval = Sequence(LerpPosHprInterval(self.np, duration=0.17, pos=(x, y, z+3), hpr=(0, 0, 90)),
								LerpPosHprInterval(self.np, duration=0.17, pos=(x, y, z), hpr=hprFinal)
								)
			self.GUI.seqHolder[-1].append(Func(interval.start))

	def effectChangeAni(self, name=''):
		card, para = self.card, Parallel(name="Status Change Ani")
		#Handle the loop(False)/pose(0) category of texCards: Power Damage
		if not name or name in ("Damage Boost", "Power Damage"):
			if on := self.isPlayed and card.onBoard and card.dealsDmg() and \
					 	card.effects["Damage Boost"] + card.Game.rules[card.ID]["Power Damage"] > 0:
				self.checkTexCard("Power Damage")
			para.append(Func(self.texCardAni_LoopPose, "Power Damage", on))
		if not name or name in ("Can Target Minions", "Power Can Target Minions"):
			if on := self.isPlayed and card.onBoard and \
					 	card.effects["Can Target Minions"] + card.Game.rules[card.ID]["Power Can Target Minions"] > 0:
				self.checkTexCard("Can Target Minions")
			para.append(Func(self.texCardAni_LoopPose, "Can Target Minions", on))

		if self.GUI.seqHolder: self.GUI.seqHolder[-1].append(para)
		else: para.start()
		
	def leftClick(self):
		if self.isPlayed:
			if self.GUI.stage == 0: self.GUI.resolveMove(self.card, self, "Power")
		else: #Discover a power.
			if self.GUI.stage == 3 and self.card in self.GUI.Game.options:
				self.GUI.resolveMove(self.card, None, "DiscoverOption")
		
	def decideColor(self):
		color, card = transparent, self.card
		if self.isPlayed and card.ID == card.Game.turn and card.Game.Manas.affordable(card) and card.available():
			color = green
		return color

def loadPower(base):
	loader = base.loader
	font = base.getFont()
	root = loader.loadModel("Models\\PowerModels\\Power.glb")
	root.name = "NP_Power"
	
	#Model names: box, card, cardImage, description, nameTag, mana
	for model in root.getChildren():
		#model.setTransparency(True)
		if model.name in ("frame", "mana"): texture = base.textures["stats_Power"]
		elif model.name == "cardBack": texture = base.textures["cardBack"]
		else: continue
		model.setTexture(model.findTextureStage('*'), texture, 1)
	#y limit: mana -0.12, description -0.025
	makeText(root, "mana", '0', pos=(0, 1.36, 0.125), scale=0.857*statTextScale, #0.9,
			color=white, font=font)
	makeText(root, "description", '', pos=(1, -2.5, 0.027), scale=0.5,
			color=black, font=font, wordWrap=10, cardColor=yellow)

	for name in ("Hourglass", "Trigger", "Lifesteal"):
		base.modelTemplates[name].copyTo(root)

	#After the loading, the NP_Minion root tree structure is:
	#NP_Power/card|mana|cardImage, etc
	#NP_Power/mana_TextNode|description_TextNode
	#NP_Power/Trigger
	return root


"""Load Hero Cards"""
class Btn_Hero(Btn_Card):
	def __init__(self, GUI, card, nodePath):
		super().__init__(GUI, card, nodePath)
		
		self.cNode_Backup = CollisionNode("cNode")
		self.cNode_Backup.addSolid(CollisionBox((0.05, -1.1, 0), 2.2, 3.1, 0.1))
		self.cNode_Backup_Played = CollisionNode("cNode_Played")
		self.cNode_Backup_Played.addSolid(CollisionBox((0.05, 0.25, 0), 2, 2.2, 0.1))

	def leftClick(self):
		self.selected = not self.selected
		GUI, card = self.GUI, self.card
		stage, game = GUI.stage, GUI.Game
		if self.isPlayed:
			if stage == 0 or stage == 2: self.GUI.resolveMove(self.card, self, "HeroonBoard")
			elif stage == 3 and card in game.options: GUI.resolveMove(card, None, "DiscoverOption")
		else:
			if stage == -2: #组建套牌中
				GUI.deckBuilder.addaCard(type(card))
			elif stage == -1:
				self.setBoxColor(red if self.selected else green)
				GUI.mulliganStatus[card.ID][game.mulligans[card.ID].index(card)] = 1 if self.selected else 0
			elif stage == 0: GUI.resolveMove(card, self, "HeroinHand")
			elif GUI.stage == 3 and card in game.options: GUI.resolveMove(card, None, "DiscoverOption")
	
	def effectChangeAni(self, name=''):
		card, para = self.card, Parallel(name="Status Change Ani")
		self.effectChangeAni_Shared(name, para)
		#Handle the loop(False)/pose(0) category of texCards: Immune, Stealth, Spell Damage
		if not name or name == "Immune":
			if on := self.isPlayed and card.onBoard and card.Game.rules[card.ID]["Immune"] > 0:
				self.checkTexCard("Immune")
			para.append(Func(self.texCardAni_LoopPose, "Immune", on))
		if not name or name == "Spell Damage":
			if on := self.isPlayed and card.onBoard and card.Game.rules[card.ID]["Spell Damage"] > 0:
				self.checkTexCard("Spell Damage")
			para.append(Func(self.texCardAni_LoopPose, "Spell Damage", on))
		if not name or name == "Temp Stealth":
			if on := self.isPlayed and card.onBoard and card.effects["Temp Stealth"] > 0:
				self.checkTexCard("Stealth")
			para.append(Func(self.texCardAni_LoopPose, "Stealth", on))
		##Handle the loop(False, num1, num2)/play(num1, num2) category of texCards: Frozen
		if not name or name == "Frozen":
			if on := self.isPlayed and card.onBoard and card.effects["Frozen"] > 0:
				self.checkTexCard("Frozen")
			para.append(Func(self.texCardAni_LoopPlay, "Frozen", 96, 97, 105, on))
			
		if self.GUI.seqHolder: self.GUI.seqHolder[-1].append(para)
		else: para.start()

	def placeIcons(self):
		pass

	def decideColor(self):
		color, card = transparent, self.card
		if not self.isPlayed and card.inHand and card.ID == card.Game.turn and card.Game.Manas.affordable(card):
			color = green
		elif self.isPlayed and card.onBoard and card.canAttack(): color = green
		return color
		
		
def loadHero(base):
	loader = base.loader
	font = base.getFont()
	root = loader.loadModel("Models\\HeroModels\\Hero.glb")
	root.name = "NP_Hero"
	
	#Model names: armor, attack, box, box_Played, card, cardBack, cardImage, frame, health, stats
	for model in root.getChildren():
		#model.setTransparency(True)
		if model.name == "cardBack": texture = base.textures["cardBack"]
		elif model.name in ("stats", "armor_Played", "attack_Played", "frame", "health_Played"):
			texture = base.textures["stats_Hero"]
		else: continue
		model.setTexture(model.findTextureStage('*'), texture, 1)
		
	makeText(root, "mana", '0', pos=(-1.73, 1.15, 0.1), scale=statTextScale,
				color=white, font=font)
	makeText(root, "armor", '0', pos=(1.81, -4.02, 0.09), scale=statTextScale,
				color=white, font=font)
	makeText(root, "attack_Played", '0', pos=(-2.15*0.88, -2.38*0.88, 0.122), scale=1.1,
				color=white, font=font)
	makeText(root, "health_Played", '0', pos=(2.2*0.88, -2.38*0.88, 0.122), scale=1.1,
				color=white, font=font)
	makeText(root, "armor_Played", '0', pos=(2.2*0.88, -0.8*0.88, 0.122), scale=1.1,
				color=white, font=font)
	makeText(root, "description", '', pos=(0.7, -2, 0.1), scale=0.5,
				color=black, font=font, cardColor=yellow)
	
	#After the loading, the NP_Minion root tree structure is:
	#NP_Hero/card|stats|cardImage, etc
	#NP_Hero/mana_TextNode|attack_TextNode, etc
	#NP_Hero/Frozen_TexCard, etc
	return root


class Btn_Trigger:
	def __init__(self, carrierBtn, nodePath):
		self.carrierBtn, self.np = carrierBtn, nodePath
		self.seqNode = nodePath.find("TexCard").find("+SequenceNode").node()
		
	def trigAni(self): #Index of last frame is 47
		if self.seqNode.isPlaying(): self.seqNode.play(self.seqNode.getFrame(), 48)
		else: self.seqNode.play(1, 48)
		
class Btn_SpecTrig:
	def __init__(self, carrierBtn, nodePath):
		self.carrierBtn, self.np = carrierBtn, nodePath
		self.seqNode = nodePath.find("TexCard").find("+SequenceNode").node()
	
	def trigAni(self):
		sequence = Sequence(Func(self.seqNode.play), Wait(0.4),
							#Func(self.np.find("SpecTrig").setColor, transparent),
							Func(self.np.find("SpecTrig").hide),
							Wait(0.7))
		self.carrierBtn.GUI.seqHolder[-1].append(sequence)
		
class Btn_Hourglass:
	#nodePath has following structure: Hourglass/Hourglass
											   #/Trig Counter
	def __init__(self, carrierBtn, nodePath):
		self.carrierBtn, self.np = carrierBtn, nodePath
		self.i = 0
		
	def seqUpdateText(self, s='', animate=True):
		model, counterText = self.np.find("Hourglass"), self.np.find("Trig Counter_TextNode")
		counterTextNode = counterText.node()
		if not s:
			s = ""
			for trig in self.carrierBtn.card.trigsBoard:
				if (animate and trig.counter > -1) or (not animate and trig.counter> 0):
					s += str(trig.counter) + ' '
		if animate:
			self.i += 1
			return Sequence(LerpHprInterval(model, duration=0.5, hpr=(self.i*360, 0, 0)),
							LerpScaleInterval(counterText, duration=0.25, scale=1.2),
					 		Func(counterTextNode.setText, s),
					 		LerpScaleInterval(counterText, duration=0.25, scale=0.6)
							)
		else: return Func(counterTextNode.setText, s)

class Btn_Deathrattle:
	def __init__(self, carrierBtn, nodePath):
		self.carrierBtn, self.np = carrierBtn, nodePath
		
class Btn_Lifesteal:
	def __init__(self, carrierBtn, nodePath):
		self.carrierBtn, self.np = carrierBtn, nodePath
		self.seqNode = nodePath.find("TexCard").find("+SequenceNode").node()
	
	def trigAni(self):
		if self.seqNode.isPlaying():
			self.seqNode.play(self.seqNode.getFrame(), self.seqNode.getNumFrames())
		else:
			self.seqNode.play(1, self.seqNode.getNumFrames())

class Btn_Poisonous:
	def __init__(self, carrierBtn, nodePath):
		self.carrierBtn, self.np = carrierBtn, nodePath
		self.seqNode = nodePath.find("TexCard").find("+SequenceNode").node()
		
	def trigAni(self):
		if self.seqNode.isPlaying():
			self.seqNode.play(self.seqNode.getFrame(), self.seqNode.getNumFrames())
		else:
			self.seqNode.play(1, self.seqNode.getNumFrames())


#Used for secrets and quests
class Btn_Secret:
	def __init__(self, GUI, card, nodePath):
		self.GUI, self.card = GUI, card
		self.onlyCardBackShown = self.selected = False
		self.np = nodePath
		
	def dimDown(self):
		self.np.setColor(grey)
	
	def setBoxColor(self, color):
		pass
	
	def checkHpr(self):
		hpr = None
		if self.card.ID == self.GUI.Game.turn and self.np.get_r() < 180:
			hpr = (0, 0, 180)  #Flip to back, unusable
		elif self.card.ID != self.GUI.Game.turn and self.np.get_r() > 0:
			hpr = (0, 0, 0)
		if hpr: self.GUI.seqHolder[-1].append(Func(LerpHprInterval(self.np, duration=0.3, hpr=hpr).start))
			
	def leftClick(self):
		pass
	
	def rightClick(self):
		if self.GUI.stage in (1, 2): self.GUI.cancelSelection()
		else: self.GUI.drawCardZoomIn(self)

pos_QuestFinish = (0, 1.5, 20)
scale_HeroZoneTrigCounter = 0.5

class Btn_HeroZoneTrig:
	def __init__(self, GUI, card, nodePath):
		self.GUI, self.card = GUI, card
		self.onlyCardBackShown = self.selected = False
		self.np = nodePath
		self.counterText = nodePath.find("Trig Counter_TextNode")
		
	def reassignCardBtn(self, card):
		card.btn = self
		
	def dimDown(self):
		self.np.setColor(grey)
		
	def setBoxColor(self, color):
		pass
	
	def trigAni(self, newValue):
		sequence = Sequence(LerpScaleInterval(self.counterText, duration=0.25, scale=1.2),
							Func(self.counterText.node().setText, '' if newValue == 0 else str(newValue)),
							LerpScaleInterval(self.counterText, duration=0.25, scale=scale_HeroZoneTrigCounter)
							)
		if self.GUI.seqHolder: self.GUI.seqHolder[-1].append(sequence)
		else: sequence.start()
		
	def finishAni(self, newQuest=None, reward=None):
		card, pos_0 = self.card, self.np.getPos()
		nodePath, btn = genCard(self.GUI, card, isPlayed=False, pickable=False, scale=0.1, makeNewRegardless=True)
		sequence = Sequence(Func(self.np.removeNode),
							LerpPosHprScaleInterval(nodePath, duration=0.5, startPos=pos_0, pos=pos_QuestFinish, hpr=(0, 0, 0), scale=(1, 1, 1)), Wait(0.5)
							)
		if newQuest:
			sequence.append(LerpHprInterval(nodePath, duration=0.3, hpr=(0, 0, 180)) )
			sequence.append(Func(btn.changeCard, newQuest, False, False))
			sequence.append(LerpHprInterval(nodePath, duration=0.3, hpr=(0, 0, 360)) )
			sequence.append(Wait(0.7))
			sequence.append(LerpPosHprScaleInterval(btn.np, duration=0.5, pos=pos_0, hpr=(0, 0, 360), scale=0.1))
			sequence.append(Func(nodePath.removeNode))
			nodePath_New, btn_New = genHeroZoneTrigIcon(self.GUI, newQuest)
			sequence.append(Func(nodePath_New.setPos, pos_0))
		elif reward:
			nodePath_Reward, btn_Reward = genCard(self.GUI, reward, isPlayed=False, pickable=True, pos=(0, 0, 0.2))
			sequence.append(LerpHprInterval(nodePath, duration=0.3, hpr=(0, 0, 180)))
			sequence.append(Func(nodePath_Reward.reparentTo, nodePath))
			sequence.append(LerpHprInterval(nodePath, duration=0.3, hpr=(0, 0, 360)))
			sequence.append(Wait(0.7))
			sequence.append(Func(nodePath_Reward.wrtReparentTo, self.GUI.render))
			sequence.append(Func(nodePath.removeNode))
		else: #No new quest or reward to add to hand.
			sequence.append(Func(nodePath.removeNode))
		sequence.append(Func(self.GUI.heroZones[card.ID].placeSecrets))
		
		self.GUI.seqHolder[-1].append(sequence)
		
	def leftClick(self):
		pass
	
	def rightClick(self):
		if self.GUI.stage: self.GUI.cancelSelection() #Only responds when UI is 0
		else: self.GUI.drawCardZoomIn(self)

	
class Btn_Option:
	def __init__(self, GUI, option, nodePath):
		self.GUI, self.card = GUI, option
		option.btn = self
		self.np = nodePath
		
	def leftClick(self):
		self.GUI.resolveMove(self.card, self, "ChooseOneOption" if self.GUI.stage == 1 else "DiscoverOption")
		
	def rightClick(self):
		pass
	
	
def loadOption(base):
	loader = base.loader
	texture = base.textures["stats_Minion"]
	font = base.getFont()
	root =  loader.loadModel("Models\\Option.glb")
	root.name = "NP_Option"
	
	#Model names: card, cardImage, mana, stats, cardBack
	nodePath = root.find("cardBack")
	nodePath.setTexture(nodePath.findTextureStage('0'), base.textures["cardBack"], 1)
	nodePath = root.find("mana")
	#nodePath.setTransparency(True)
	nodePath.setTexture(nodePath.findTextureStage('0'), texture, 1)
	nodePath = root.find("stats")
	#nodePath.setTransparency(True)
	nodePath.setTexture(nodePath.findTextureStage('0'), texture, 1)
	nodePath = root.find("legendaryIcon")
	#nodePath.setTransparency(True)
	nodePath.setTexture(nodePath.findTextureStage('0'), base.textures["stats_Spell"], 1)
	
	makeText(root, "mana", '', pos=(-1.75, 1.15, 0.1), scale=statTextScale,
			 color=white, font=font)
	makeText(root, "attack", '', pos=(-1.7, -4.05, 0.09), scale=statTextScale,
			 color=white, font=font)
	makeText(root, "health", '', pos=(1.8, -4.05, 0.09), scale=statTextScale,
			 color=white, font=font)
	
	(cNode := CollisionNode("cNode")).addSolid(CollisionBox((0.05, -1.1, 0), 2.2, 3.1, 0.1))
	root.attachNewNode(cNode)
	
	return root


def genOption(GUI, option, pos=None, onlyShowCardBack=False):
	nodePath = GUI.modelTemplates["Option"].copyTo(GUI.render)
	if pos: nodePath.setPos(pos)
	btn_Card = Btn_Option(GUI, option, nodePath)
	nodePath.setPythonTag("btn", btn_Card)
	
	if onlyShowCardBack:
		for child in nodePath.getChildren():
			if child.name != "cardBack" and child.name != "Option_cNode":
				child.hide()#child.setColor(transparent)
	else:
		typeOption = type(option)
		mana, attack, health = typeOption.mana, typeOption.attack, typeOption.health
		if mana > -1: nodePath.find("mana_TextNode").node().setText(str(mana))
		if attack > -1: nodePath.find("attack_TextNode").node().setText(str(attack))
		if health > -1: nodePath.find("health_TextNode").node().setText(str(health))
		if attack < 0 or health < 0:
			nodePath.find("cardImage").hide()#.setColor(transparent)
			nodePath.find("stats").hide()#.setColor(transparent)
		else:
			model = nodePath.find("cardImage")
			model.setTexture(model.findTextureStage('0'),
							 GUI.loader.loadTexture(findFilepath(option)), 1)
		model = nodePath.find("card")
		model.setTexture(model.findTextureStage('0'),
						 GUI.loader.loadTexture(findFilepath(option)), 1)
		if not typeOption.isLegendary: nodePath.find("legendaryIcon").hide()

	return nodePath, btn_Card



Table_Type2Btn = {"Minion": Btn_Minion, "Dormant": Btn_Minion, "Spell": Btn_Spell, "Weapon": Btn_Weapon,
				  "Hero": Btn_Hero, "Power": Btn_Power,
				  "Trigger_Icon": Btn_Trigger, "Deathrattle_Icon": Btn_Deathrattle,
				  "Lifesteal_Icon": Btn_Lifesteal, "Poisonous_Icon": Btn_Poisonous,
				  "SpecTrig_Icon": Btn_SpecTrig, "Hourglass_Icon": Btn_Hourglass,
				  }


#np_Template is of category NP_Minion, etc and is kept by the GUI.
#card: card object, which the copied nodePath needs to become
#isPlayed: boolean, whether the card is in played form or not
#Only "Trigger", etc reference btn, others reference nodePath

#There are situations where new cards must always be made, like questline being completed and popping from a Trig button
def genCard(GUI, card, isPlayed, pickable=True, pos=None, hpr=None, scale=None,
			onlyShowCardBack=False, makeNewRegardless=False, isUnknownSecret=False, seq=None):
	btn = card.btn
	if not makeNewRegardless and btn and (nodepath := btn.np):
		if pos: nodepath.setPos(pos)
		if hpr: nodepath.setHpr(hpr)
		if scale: nodepath.setScale(scale)
		btn.np.reparentTo(GUI.render)
		if btn.isPlayed != isPlayed or btn.onlyCardBackShown != onlyShowCardBack:
			if seq: seq.append(Func(btn.changeCard, card, isPlayed, pickable, onlyShowCardBack))
			else: btn.changeCard(card, isPlayed=isPlayed, pickable=pickable, onlyShowCardBack=onlyShowCardBack)
		return btn.np, btn

	nodepath = GUI.modelTemplates[card.category].copyTo(GUI.render)
	if pos: nodepath.setPos(pos)
	if hpr: nodepath.setHpr(hpr)
	if scale: nodepath.setScale(scale)
	#NP_Minion root tree structure is:
	#NP_Minion/card|stats|cardImage, etc
	#NP_Minion/mana_TextNode|attack_TextNode, etc
	btn_Card = Table_Type2Btn[card.category](GUI, None, nodepath)
	nodepath.setPythonTag("btn", btn_Card)
	for nodePath in nodepath.getChildren():
		name = nodePath.name
		if "TextNode" in name: btn_Card.texts[name.replace("_TextNode", '')] = nodePath
		elif "TexCard" in name: btn_Card.texCards[name.replace("_TexCard", '')] = nodePath
		#Collision Nodes are not inserted into the template tree yet
		elif "_Icon" in name: btn_Card.icons[name.replace("_Icon", '')] = Table_Type2Btn[name](btn_Card, nodePath)
		else: btn_Card.models[name] = nodePath
	
	btn_Card.changeCard(card, isPlayed=isPlayed, pickable=pickable, onlyShowCardBack=onlyShowCardBack,
						isUnknownSecret=isUnknownSecret)
	return nodepath, btn_Card


def genSecretIcon(GUI, card, pos=None, hpr=None):
	btn = card.btn
	if btn and isinstance(btn, Btn_Secret) and btn.np:
		btn.np.reparentTo(GUI.render)
		return btn.np, btn

	nodepath = GUI.loader.loadModel("Models\\HeroModels\\SecretIcon.glb")
	nodepath.setTexture(nodepath.findTextureStage('0'), GUI.textures["Secret_"+card.Class], 1)
	nodepath.reparentTo(GUI.render)
	if pos: nodepath.setPos(pos)
	if hpr: nodepath.setHpr(hpr)
	card.btn = btn_Icon = Btn_Secret(GUI, card, nodepath)
	nodepath.setPythonTag("btn", btn_Icon)
	(cNode := CollisionNode("cNode")).addSolid(CollisionSphere(0, 0, 0, 0.5))
	nodepath.attachNewNode(cNode)#.show()
	return nodepath, btn_Icon


def loadHeroZoneTrig(GUI):
	nodepath = GUI.loader.loadModel("Models\\HeroModels\\TurnTrig.glb")
	textNode = TextNode("Trig Counter_TextNode")
	textNode.setFont(GUI.getFont())
	textNode.setAlign(TextNode.ACenter)
	textNode.setTextColor(white)
	textNodePath = nodepath.attachNewNode(textNode)
	textNodePath.setPosHprScale(0, -0.4, 0.1, 0, -90, 0,
								scale_HeroZoneTrigCounter, scale_HeroZoneTrigCounter, scale_HeroZoneTrigCounter)
	(cNode := CollisionNode("cNode")).addSolid(CollisionSphere(0, 0, 0, 0.6))
	nodepath.attachNewNode(cNode)#.show()
	nodepath.setScale(1.2)
	return nodepath

def genHeroZoneTrigIcon(GUI, card, pos=None, text='', scale=1.2, textColor=white, filePath=''):
	btn = card.btn
	if btn and isinstance(btn, Btn_HeroZoneTrig) and btn.np:
		btn.np.reparentTo(GUI.render)
		return btn.np, btn

	nodepath = GUI.modelTemplates["HeroZoneTrig"].copyTo(GUI.render)
	icon, tex = nodepath.find("Icon"), GUI.loader.loadTexture(filePath if filePath else findFilepath(card))
	if card.category == "Power":
		(ts := TextureStage('ForPower')).setTexcoordName('1')
		icon.setTexture(ts, tex, 1)
	else: icon.setTexture(icon.findTextureStage('0'), tex, 1)
	textNode = nodepath.find("Trig Counter_TextNode").node()
	textNode.setText(text)
	textNode.setAlign(TextNode.ACenter)
	textNode.setTextColor(textColor)
	if pos: nodepath.setPos(pos)
	nodepath.setScale(scale)
	card.btn = btn_Icon = Btn_HeroZoneTrig(GUI, card, nodepath)
	nodepath.setPythonTag("btn", btn_Icon)
	return nodepath, btn_Icon