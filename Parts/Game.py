from Parts.Handlers import *
from Parts.Hand import Hand_Deck
from Parts.ConstsFuncsImports import *
from HS_Cards.AcrossPacks import Illidan, Anduin

SVClasses = ["Forestcraft", "Swordcraft", "Runecraft", "Dragoncraft", "Shadowcraft", "Bloodcraft", "Havencraft",
			 "Portalcraft"]

dict_GameEffects = {"Immune": "你的英雄免疫", "Immune2NextTurn": "你的英雄免疫直到你的下个回合", "ImmuneThisTurn": "你的英雄在本回合免疫",
					"Evasive": "你的英雄无法成为法术或英雄技能的目标", "Evasive2NextTurn": "直到下回合，你的英雄无法成为法术或英雄技能的目标",
					"Spell Damage": "你的英雄的法术伤害加成", "Spells Lifesteal": "你的法术具有吸血", "Spells x2": "你的法术会施放两次",
					"Spells Sweep": "你的法术也会对目标随从的相邻随从施放", "Spells Poisonous": "你的法术具有剧毒",
					"Fire Spell Damage": "你的英雄的火焰法术伤害加成",

					"Power Sweep": "你的英雄技能也会对目标随从的相邻随从生效", "Power Damage": "你的英雄技能伤害加成",
					"Power Can Target Minions": "你的英雄技能可以以随从为目标", "Power Freezes Target": "你的英雄技能会冻结目标",
					"Power Chance 2": "可以使用两次英雄技能", "Power Chance Inf": "可以使用任意次数的英雄技能",
					"Heal to Damage": "你的治疗改为造成伤害", "Lifesteal Damages Enemy": "你的吸血会对敌方英雄造成伤害，而非治疗你",
					"Choose Both": "你的抉择卡牌可以同时拥有两种效果",
					"Battlecry x2": "你的战吼会触发两次", "Combo x2": "你的连击会触发两次",
					"Deathrattle X": "你的亡语不会触发", "Minion Deathrattle x2": "你的随从的亡语触发两次", "Weapon Deathrattle x2": "你的武器的亡语触发两次",
					"Summon x2": "你的卡牌效果召唤的随从数量翻倍", "Secrets x2": "你的奥秘触发两次",
					"Minions Can't Be Frozen": "你的随从无法被冻结",  #Living Dragonbreath prevents minions from being Frozen
					"Ignore Taunt": "所有友方攻击无视嘲讽",  #Kayn Sunfury allows player to ignore Taunt
					"Hero Can't Be Attacked": "你的英雄不能被攻击",
					"Trade Discovers Instead": "交易时改为从牌库发现",
					}

statusDict = {key: 0 for key in dict_GameEffects.keys()}



class Game:
	def __init__(self, GUI=None, boardID="", mainPlayerID=0, orig=None):
		self.GUI = GUI
		self.options, self.mulligans = [], {1: [], 2: []}
		self.players = {1: None, 2: None}
		self.Discover = Discover(self)
		self.cardinPlay = self.target = None  # Used for target change induced by triggers such Mayor Noggenfogger and Spell Bender.
		self.deads = []  # 1st list records dead objects, 2nd records object attacks when they die.
		self.resolvingDeath = False
		self.mode = 0
		self.picks, self.picks_Backup, self.moves = [], [], []
		#复制基础的数值
		if orig:
			self.copiedObjs = {}
			self.mainPlayerID = orig.mainPlayerID
			self.initialClasses, self.boardID = orig.initialClasses, orig.boardID
			self.RNGPools = orig.RNGPools
			self.rules = copy.copy(self.rules)
			self.gameEnds, self.turn, self.turnInd = orig.gameEnds, orig.turn, orig.turnInd
		else:
			self.mainPlayerID = mainPlayerID if mainPlayerID else numpyRandint(2) + 1 #To be replaced in LAN_Games
			self.rules = {1: statusDict, 2: copy.deepcopy(statusDict)}
			self.gameEnds, self.turn, self.turnInd = 0, 1, 0
		#复制卡牌和handlers
		self.trigsBoard, self.trigsHand, self.trigsDeck = {1: {}, 2: {}}, {1: {}, 2: {}}, {1: {}, 2: {}}
		if orig:
			self.heroes = {1: orig.heroes[1].createCopy(self), 2: self.heroes[2].createCopy(self)}
			self.powers = {1: self.powers[1].createCopy(self), 2: self.powers[2].createCopy(self)}
			self.weapons = {1: [weapon.createCopy(self) for weapon in self.weapons[1]],
							2: [weapon.createCopy(self) for weapon in self.weapons[2]]}
			self.Hand_Deck = self.Hand_Deck.createCopy(self)
			self.minions = {1: [minion.createCopy(self) for minion in self.minions[1]],
							2: [minion.createCopy(self) for minion in self.minions[2]]}
			self.Counters, self.Manas, self.Secrets = Counters(self), Manas(self), Secrets(self)
			# self.turnstoTake = {1:1, 2:1} #For Temporus & Open the Waygate
			self.turnStartTrigger, self.turnEndTrigger = [], []  # 用于一个回合的光环的取消
			self.trigAuras = {1: [], 2: []}  # 用于一些永久光环，如砰砰博士的机械获得突袭。
			# 登记了的扳机，这些扳机的触发依次遵循主玩家的场上、手牌和牌库。然后是副玩家的场上、手牌和牌库。
			self.trigAuras = {ID: [aura.createCopy(self) for aura in self.trigAuras[ID]] for ID in (1, 2)}
			self.Counters, self.Manas = self.Counters.createCopy(self), self.Manas.createCopy(self)
			self.Secrets = self.Secrets.createCopy(self)
			for trigs1, trigs2 in zip((self.trigsBoard, self.trigsHand, self.trigsDeck),
									  (self.trigsBoard, self.trigsHand, self.trigsDeck)):
				for ID in (1, 2):
					for sig in trigs2[ID].keys(): trigs1[ID][sig] = [trig.createCopy(self) for trig in trigs2[ID][sig]]
			self.turnStartTrigger = [trig.createCopy(self) for trig in self.turnStartTrigger]
			self.turnEndTrigger = [trig.createCopy(self) for trig in self.turnEndTrigger]
			#完成之后把copiesObjs这个存储单元删除
			del self.copiedObjs
		else:
			self.heroes = {1: Illidan(self, 1), 2: Anduin(self, 2)}
			self.powers = {1: self.heroes[1].heroPower(self, 1), 2: self.heroes[2].heroPower(self, 2)}
			self.heroes[1].onBoard = self.heroes[2].onBoard = True
			# Multipole weapons can coexitst at minions in lists. The newly equipped weapons are added to the lists
			self.minions, self.weapons = {1: [], 2: []}, {1: [], 2: []}
			self.Counters, self.Manas, self.Secrets = Counters(self), Manas(self), Secrets(self)
			#self.Hand_Deck 会在之后的initialize_Details里面定义
			self.turnStartTrigger, self.turnEndTrigger = [], []  # 用于一个回合的光环的取消
			self.trigAuras = {1: [], 2: []}  # 用于一些永久光环，如砰砰博士的机械获得突袭。

	def initialize_Details(self, boardID, seed, RNGPools, hero1, hero2, deck1=None, deck2=None):
		hero1, hero2 = hero1(self, 1), hero2(self, 2)
		hero1.onBoard = hero2.onBoard = True
		self.initialClasses = {1: hero1.Class, 2: hero2.Class}
		self.heroes = {1: hero1, 2: hero2}
		self.powers = {1: hero1.heroPower(self, 1), 2: hero2.heroPower(self, 2)}
		
		self.boardID, self.RNGPools = boardID, RNGPools
		numpy.random.seed(seed)
		self.Hand_Deck = Hand_Deck(self, deck1, deck2)
		self.Hand_Deck.initialize()
		
	def minionsAlive(self, ID=0, exclude=None): #if exclude is not None, return all living minions except the exclude
		it = (ID,) if ID else (1, 2)
		return [o for ID in it for o in self.minions[ID] if o.category == "Minion" and o is not exclude \
				and o.onBoard and not o.dead and o.health > 0]

	def charsAlive(self, ID=0, exclude=None):
		it = (ID,) if ID else (1, 2)
		return [o for ID in it for o in self.minions[ID] if o.category == "Minion" and o is not exclude \
				and o.onBoard and not o.dead and o.health > 0] \
				+ [o for ID in it if (o := self.heroes[ID]) is not exclude and not o.dead and o.health > 0]

	#exclude is the minion that won't counted in. With non-empty race, only count minions with certain race
	def minionsonBoard(self, ID=0, exclude=None, race=""): #if exclude is not None, return all onBoard minions except the target
		it = (ID,) if ID else (1, 2)
		return [o for ID in it for o in self.minions[ID] if o.category == "Minion" and o.onBoard and o is not exclude and race in o.race]

	def charsonBoard(self, ID=0, exclude=None):
		it = (ID,) if ID else (1, 2)
		return [o for ID in it for o in self.minions[ID] if o.category == "Minion" and o is not exclude and o.onBoard] \
				+ [o for ID in it if (o := self.heroes[ID]) is not exclude]

	def amuletsonBoard(self, ID, exclude=None):
		return [o for o in self.minions[ID] if o.category == "Amulet" and o.onBoard and o is not exclude]

	def minionsandAmuletsonBoard(self, ID, exclude=None):
		return [o for o in self.minions[ID] if o.onBoard and o is not exclude]

	def earthsonBoard(self, ID, exclude=None):
		return [o for o in self.minions[ID] if o.category == "Amulet" and o.onBoard and "Earth Sigil" in o.race and o is not exclude]
		
	def neighbors2(self, target, countDormants=False):
		targets, ID, pos, i = [], target.ID, target.pos, 0
		if target not in self.minions[ID]: return [], 0
		while pos > 0:
			pos -= 1
			obj_onLeft = self.minions[ID][pos]
			if not countDormants and obj_onLeft.category != "Minion": break #If Dormants aren't considered as adjacent entities, they block the search
			elif obj_onLeft.onBoard: #If the minion is not onBoard, skip it; if on board, count it.
				targets.append(obj_onLeft)
				i -= 1
				break
		pos = target.pos
		boardSize = len(self.minions[ID])
		while pos < boardSize - 1:
			pos += 1
			obj_onRight = self.minions[ID][pos]
			if not countDormants and obj_onRight.category != "Minion": break
			elif obj_onRight.onBoard:
				targets.append(obj_onRight)
				i += 2
				break
		#i = 0 if no adjacent; -1 if only left; 1 if both; 2 if only right
		return targets, i

	"""Handle playing cards"""
	def prepGUI4Ani(self, GUI, newSequence=True):
		if GUI:
			GUI.seqReady = False
			if newSequence: GUI.seqHolder.append(GUI.SEQUENCE())
			
	def wrapUpPlay(self, GUI, sendthruServer, endingTurn=False):
		if GUI:
			GUI.decideCardColors()
			GUI.seqReady = True #当seqHolder中最后一个sequence的准备完毕时，重置seqReady，告知GUI.mouseMove可以调用
			if GUI.sock_Send and sendthruServer: GUI.sendOwnMovethruServer(endingTurn=endingTurn)
		self.moves, self.picks_Backup, self.picks = [], [], []

	def check_playAmulet(self, amulet, target, position, choice):
		return self.Manas.affordable(amulet) and self.space(amulet.ID) and amulet.selectionLegit(target, choice)
	
	def playAmulet(self, amulet, target, position, choice=0, comment="", sendthruServer=True):
		self.playMinion(amulet, target, position, choice, comment, sendthruServer)

	#There probably won't be board size limit changing effects.
	#Minions to die will still count as a placeholder on board. Only minions that have entered the tempDeads don't occupy space.
	def space(self, ID):
		#Minions and Dormants both occupy space as long as they are on board.
		return 7 - 2 * (self.heroes[ID].Class in SVClasses) - sum(minion.onBoard for minion in self.minions[ID])

	def check_playMinion(self, minion, target, position, choice=0):
		return self.Manas.affordable(minion) and minion.selectionLegit(target, choice) \
			   and (self.space(minion.ID) > 0 or (minion.willAccelerate()))

	def getSubTarLocators(self, subject, target):
		subLocator = self.genLocator(subject)
		if target:
			if isinstance(target, (list, tuple)): tarLocator = [self.genLocator(obj) for obj in target]
			else: tarLocator = self.genLocator(target)  # 非列表状态的target一定是炉石卡指定的
		else: tarLocator = 0
		return subLocator, tarLocator

	def fabCard(self, tup, ID, creator):
		card = tup[0](self, ID, tup[1])
		card.creator = type(creator)
		return card

	def playMinion(self, minion, target, position, choice=0, comment="", sendthruServer=True):
		#当场上没有空位且打出的随从不是一个有Accelerate的Shadowverse随从时，不能打出
		if not self.check_playMinion(minion, target, position, choice):
			return False
			#打出随从到所有结算完结为一个序列，序列完成之前不会进行胜负裁定。
			#打出随从产生的序列分为
				#1）使用阶段： 支付费用，随从进入战场（处理位置和刚刚召唤等），抉择变形类随从立刻提前变形，黑暗之主也在此时变形。
					#如果随从有回响，在此时决定其将在完成阶段结算回响
					#使用时阶段：使用时扳机，如伊利丹，任务达人和魔能机甲等
					#召唤时阶段：召唤时扳机，如鱼人招潮者，饥饿的秃鹫等
					#得到过载
					###开始结算死亡事件。此时序列还没有结束，不用处理胜负问题。
				#2）结算阶段： 根据随从的死亡，在手牌、牌库和场上等位置来决定战吼，战吼双次的扳机等。
					#开始时判定是否需要触发多次战吼，连击
					#指向型战吼连击和抉择随机选取目标。如果此时场上没有目标，则不会触发 对应指向部分效果和它引起的效果。
					#抉择和磁力也在此时结算，不过抉择变形类随从已经提前结算，此时略过。
					###开始结算死亡事件，不必处理胜负问题。
				#3）完成阶段
					#召唤后步骤：召唤后扳机触发：如飞刀杂耍者，船载火炮等
					#将回响牌加入打出者的手牌
					#使用后步骤：使用后扳机：如镜像实体，狙击，顽石元素。低语元素的状态移除结算和dk的技能刷新等。
					###结算死亡，此时因为序列结束可以处理胜负问题。

		#Get locators for event recording and online gaming
		subLocator, tarLocator = self.getSubTarLocators(minion, target)
		GUI = self.GUI
		self.prepGUI4Ani(GUI) #开始准备游戏操作对应的动画
		category_Orig = minion.category #记录记录从手牌中打出的原始category
		#支付法力值，结算血色绽放等状态
		minion, mana, posinHand = self.Hand_Deck.extractfromHand(minion, enemyCanSee=True, animate=False)
		#如果打出的随从是SV中的爆能强化，激奏和结晶随从，则它们会返回自己的真正要打出的牌以及对应的费用
		minion, mana = minion.becomeswhenPlayed(choice) #如果随从没有爆能强化等，则无事发生。
		self.Manas.payManaCost(minion, mana) #海魔钉刺者，古加尔和血色绽放的伤害生效。
		self.cardinPlay = minion
		if GUI:
			GUI.seqHolder[-1].append(GUI.FUNC(removefrom, minion, GUI.playedCards))
			GUI.showOffBoardTrig(minion, animationType='')
			self.eventinGUI(minion, eventType="Play%s"%minion.category, target=target, level=0)
		#需要根据变形成的随从来进行不同的执行
		if minion.category == "Spell": #Shadowverse Accelerate minion might become spell when played
			self.resolveSpellBeingPlayed(minion, target, subLocator, tarLocator, choice, mana, posinHand, comment,
										 sendthruServer)
		else: #Normal or Enhance X or Crystallize X minion played
			minion.seq = len(self.minions[1]) + len(self.minions[2]) + len(self.weapons[1]) + len(self.weapons[2])
			self.minions[minion.ID].insert(position+100*(position < 0), minion)
			self.sortPos()
			armedTrigs = self.armedTrigs("CardBeenPlayed")
			if GUI: GUI.hand2BoardAni(minion)
			obj2Appear = minion.played(target, choice, mana, posinHand, comment)
			# 使用后步骤，触发镜像实体，狙击，顽石元素等“每当你使用一张xx牌”之后的扳机。
			if self.cardinPlay.onBoard and self.cardinPlay.ID == self.turn: #打出无面操纵者时，剽窃复制得到的还是无面，所以关注的是进场时的牌是什么。
				self.Counters.handleCardPlayed(obj2Appear, target, mana, choice, posinHand)
				#目前只有很少的扳机会涉及连续对一个确定个体进行变形。只有”在使用一个随从牌后“和”抽到一张牌时“.两者均有相对特殊的处理方法
				#在打出一个随从，被变形药水变形为绵羊之后，触发寒冰克隆的时候会返回绵羊。打出被禁锢的随从，触发寒冰克隆会得到原始的随从。休眠的随从不会触发变形药水。
				self.sendSignal("CardBeenPlayed", self.turn, None, target, (mana, posinHand), "Minion", choice, armedTrigs)
			else: self.Counters.comboCounters[self.turn] += 1
			#............完成阶段结束，开始处理死亡情况，此时可以处理胜负问题。
			self.gathertheDead(True)
			if isinstance(tarLocator, (list, tuple)): self.moves.append(("play"+category_Orig, subLocator, tuple(tarLocator), position, choice))
			else: self.moves.append(("play"+category_Orig, subLocator, tarLocator, position, choice))
			self.wrapUpPlay(GUI, sendthruServer)

	#不考虑卡德加带来的召唤数量翻倍。用于被summon引用。
	#returns the single minion summoned. Used for anchoring the position of the original minion summoned during doubling
	#position MUST be a NUMBER. If non-negative, insert; otherwise, append
	def summonSingle(self, subject, position, summoner, hand_deck=-1, changeCreator=True):
		ID = subject.ID
		if self.space(ID) > 0:
			if changeCreator: subject.creator = type(summoner) if summoner else None
			subject.seq = len(self.minions[1]) + len(self.minions[2]) + len(self.weapons[1]) + len(self.weapons[2])
			self.minions[subject.ID].insert(position+100*(position<0), subject)  #If position is too large, the insert() simply puts it at the end.
			self.sortPos()
			self.sortSeq()
			if self.GUI:
				if hand_deck > 0: self.GUI.deck2BoardAni(subject)
				elif not hand_deck: self.GUI.hand2BoardAni(subject)
				else: self.GUI.summonAni(subject)
			self.add2EventinGUI(summoner, subject)
			category_Orig = subject.category
			subject.appears(firstTime=True) #休眠的出现实际上不会发出任何信号，但是之后仍要进行召唤随从的扳机触发
			#发出信号仍然按照目标召唤的obj类型计算，如复活禁锢的阳鳃鱼人仍然可以触发鱼人招潮者的buff扳机。
			#召唤的是一般的随从时，subject.category和comment都是"Minion"
			#召唤的是休眠的随从时，subject.category是"Dormant"，comment是"Minion“
			#召唤的是本来就休眠的随从时，如无敌巨舰和休眠的鼠王时，subject.category和comment都是"Dormant"
			self.sendSignal("ObjSummoned", subject.ID, subject, None, 0, category_Orig)
			self.Counters.handleGameEvent("Summon", type(subject), subject.ID)
			self.sendSignal("ObjBeenSummoned", subject.ID, subject, None, 0, category_Orig)
			return subject
		return None

	#只能为同一方召唤随从，如有需要，则多次引用这个函数即可。subject不能是空的
	#注意，卡德加的机制是2 ** n倍。每次翻倍会出现多召唤1个，2个，4个的情况。
	#relative只有"<>"（召唤到其右侧）和">"（召唤到其左右两侧）。如果定义了position则优先使用position给出的位置，否则按summoner和relative计算位置
	def summon(self, subject, summoner, relative='>', position=None): #只有召唤多个随从的时候会需要使用position，其需要是一个具体的int
		#如果subject是多个随从，则需要对列表/tuple/数组循环召唤单独的随从
		if not isinstance(subject, (list, tuple)): #Summon a single minion
			pos0 = summoner.pos+1 if position is None else position #除非直接定义了position，否则召唤的首个随从位置由summoner.pos+1决定
			#如果是英雄技能进行的召唤，则不会翻倍。
			if timesofx2 := self.rules[summoner.ID]["Summon x2"] if summoner and summoner.category == "Power" else 0:
				ID, numCopies = subject.ID, 2 ** timesofx2 - 1
				copies = [summoner.copyCard(subject, ID) for _ in range(numCopies)]
				if minionSummoned := self.summonSingle(subject, pos0, summoner): #只有最初本体召唤成功时才会召唤随从的复制
					if self.summonSingle(copies[0], subject.pos + 1, summoner): #复制的第一个随从是紧跟本体随从的右边
						for i in range(1, numCopies): #复制的随从列表中剩余的随从，如果没有剩余随从了，直接跳过
							if not self.summonSingle(copies[i], copies[i - 1].pos + 1, summoner): break #翻倍出的复制始终在上一个复制随从的右边。
				return minionSummoned #只要第一次召唤出随从就视为召唤成功
			else: return self.summonSingle(subject, pos0, summoner)
		else: #Summoning multiple minions in a row. But the list can be of length 1
			if len(subject) == 1: #用列表形式但是只召唤一个随从的时候，relative一定是'>'
				return self.summon(subject[0], summoner, position=position) #如果没有定义position,则召唤至summoner的两侧
			else: #真正召唤多个随从的时候，会把它们划分为多次循环。每次循环后下次循环召唤的随从紧贴在这次循环召唤的随从的右边。
				if relative == "<>" and position is None and summoner.pos != -2: #召唤到summoner的左右。只有随从在场上的时候使用，也不能在为对方召唤随从时使用
					minionSummoned = subject[0]
					for i in range(len(subject)):
						if i < 2: pos = summoner.pos + 1 - i % 2 #召唤的首个随从在summoner右边，第二个随从则在左边（实际是要把summoner向右顶）
						else: pos = subject[i-2].pos + 1 - i % 2 #i > 1 向左侧召唤随从也是让新召唤的随从紧贴上一次在左边召唤出来的初始随从。
						if not self.summon(subject[i], summoner, position=pos):
							if not i: minionSummoned = None #如果首个随从召唤即失败则返回None
							break
				else: #'>' to the right of the card. Cards no on board will have pos=-2
					if minionSummoned := self.summon(subject[0], summoner, position=summoner.pos+1 if position is None else position):
						for i in range(1, len(subject)):
							if not self.summon(subject[i], summoner, position=subject[i-1].pos+1): break
				return minionSummoned

	#一次只从一方的手牌中召唤一个随从。没有列表，从手牌中召唤多个随从都是循环数次检索，然后单个召唤入场的。
	#首个召唤的随从不进行creator的修改，如果有召唤效果翻倍，则复制的creator为summoner
	def summonfrom(self, i, ID, position, summoner, hand_deck=0):
		if hand_deck: subject = self.Hand_Deck.extractfromDeck(i, ID, animate=False)
		else: subject = self.Hand_Deck.extractfromHand(i, ID, animate=False)[0]
		if timesofx2 := self.rules[summoner.ID]["Summon x2"] if summoner and summoner.category == "Power" else 0:
			ID, numCopies = subject.ID, 2 ** timesofx2 - 1
			copies = [summoner.copyCard(subject, ID) for _ in range(numCopies)]
			if subject := self.summonSingle(subject, position, summoner=None, hand_deck=hand_deck, changeCreator=False):
				if self.summonSingle(copies[0], subject.pos + 1, summoner):
					for i in range(1, numCopies): #复制的随从列表中剩余的随从，如果没有剩余随从了，直接跳过
						if not self.summonSingle(copies[i], copies[i - 1].pos, summoner): break #翻倍出来的复制会始终紧跟在初始随从的右边。
			return subject #只要第一次召唤出随从就视为召唤成功
		else: return self.summonSingle(subject, position, summoner=None, hand_deck=hand_deck, changeCreator=False)

	def silenceMinions(self, minions):
		ls = [minion.removeEffectsTrigsAuras() for minion in minions]
		for tup, minion in zip(ls, minions):
			minion.postSilence(*tup)

	def kill(self, subject, target):
		if isinstance(target, (list, tuple)):
			if len(target) > 0: #No need to check if objs are onBoard, as only killing minions on board effects pass multiple targets
				target = [obj for obj in target if not (obj.category == "Minion" and obj.effects["Can't Break"] > 0)]
				self.add2EventinGUI(subject, target, textTarget='X', colorTarget=red)
				for obj in target: obj.dead = True
				for obj in target: self.sendSignal("Kills", self.turn, subject, obj, 0, '')
		elif target:
			if self.GUI:
				self.GUI.resetSubTarColor(subject, target)
				if subject is target: self.add2EventinGUI(subject, target, textSubject='X', colorSubject=red)
				else: self.add2EventinGUI(subject, target, textTarget='X', colorTarget=red)
			if target.onBoard:
				if not (target.category == "Minion" and target.effects["Can't Break"] > 0):
					target.dead = True
					self.sendSignal("Kills", self.turn, subject, target, 0, '')
			elif target.inHand: self.Hand_Deck.discard(target.ID, target)  # 如果随从在手牌中则将其丢弃

	#可以变形单个卡牌object或多个目标的列表，但是需要保证newTarget和target的个数保证一致
	#需要跟踪目标的效果在引用transform的时候需要自己保证target是列表
	def transform(self, target, newTarget, summoner=None): #summoner是一个卡牌object
		if not isinstance(target, (list, tuple)): target = [target]
		if not isinstance(newTarget, (list, tuple)): newTarget = [newTarget]
		if self.cardinPlay in target: self.cardinPlay = newTarget[target.index(self.cardinPlay)]
		if not target: return

		newObjsBoard, newObjsHand, i = [], [], 0
		seq_Base = len(self.minions[1]) + len(self.minions[2]) + len(self.weapons[1]) + len(self.weapons[2])
		summoner = type(summoner) if summoner else None
		#同时处理手牌中场上的随从变形时，手牌中的牌会先进入。
		for obj, newObj in zip(target, newTarget):
			ID, i = obj.ID, i + 1
			newObj.creator = summoner
			if (isMinion := obj in self.minions[ID]) or obj in self.weapons[ID]:
				self.add2EventinGUI(summoner, (obj, newObj))
				newObj.pos, newObj.seq = obj.pos, seq_Base + i #连续处理时需要让新的obj有不同的seq
				obj.disappears()
				if isMinion: self.minions[ID][obj.pos] = newObj
				else: self.weapons[ID].append(newObj)
				newObjsBoard.append(newObj)
			elif obj in (hands := self.Hand_Deck.hands[ID]):
				obj.leavesHand()
				hands[hands.index(obj)] = newObj
				newObjsHand.append(newObj)

		if self.GUI: self.GUI.transformAni(target, newTarget, onBoard=True)
		if newObjsHand: #先进行手牌中的新卡进入结算。使用Hand_Deck.replaceCardsinHand
			hands_1, hands_2 = [], []
			for i, newObj in enumerate(newObjsHand):
				if newObj is not (card_Final := self.Hand_Deck.finalizeCardintoHand(newObj, newObj.ID, sendSignal=False)):
					newTarget[newTarget.index(newObj)] = card_Final
				(hands_1 if card_Final.ID == 1 else hands_2).append(card_Final)
			if hands_1: self.sendSignal("HandCheck", 1, None, hands_1, 0, "Enter_Replace")
			if hands_2: self.sendSignal("HandCheck", 2, None, hands_2, 0, "Enter_Replace")
			self.Manas.calcMana_All()
		if newObjsBoard:
			self.sortSeq()
			for newObj in newObjsBoard:
				newObj.appears()
				if newObj.category == "Weapon": newObj.setasNewWeapon()

		for i, newObj in enumerate(newTarget): #最后需要把target内部的所有object都变成新的，从而这个target的变化可以被外部看到
			target[i] = newObj

	#This method is always invoked after the minion.disappears() method.
	def removeMinionorWeapon(self, target, sortPos=True, animate=True):
		target.onBoard, target.pos = False, -2
		removefrom(target, self.weapons[target.ID] if target.category == "Weapon" else self.minions[target.ID])
		self.sortSeq()
		if target.category != "Weapon" and sortPos: self.sortPos()
		if self.GUI and animate: self.GUI.removeMinionorWeaponAni(target)

	def banishMinion(self, subject, target):
		if isinstance(target, (list, tuple)):
			if len(target) > 0:
				self.add2EventinGUI(subject, target)
				for obj in target: obj.disappears()
				for obj in target: self.removeMinionorWeapon(obj)
		elif target:
			if self.GUI:
				self.GUI.resetSubTarColor(subject, target)
				self.add2EventinGUI(subject, target)
			if target.onBoard:
				target.disappears()
				self.removeMinionorWeapon(target)
			elif target.inHand: self.Hand_Deck.extractfromHand(target.ID, target)  #如果随从在手牌中则将其丢弃

	#The leftmost minion has position 0. Consider Dormant
	def sortPos(self):
		for i, obj in enumerate(self.minions[1]): obj.pos = i
		for i, obj in enumerate(self.minions[2]): obj.pos = i

	#Rearrange all livng minions' sequences if change is true. Otherwise, just return the list of the sequences.
	#需要考虑Dormant的出场顺序
	def sortSeq(self):
		objs = self.weapons[1] + self.weapons[2] + self.minions[1] + self.minions[2]
		for i, obj in zip(numpy.asarray([obj.seq for obj in objs]).argsort().argsort(), objs): obj.seq = i
		
	#将一张随从返回手牌。目前没有必要让returnObj2Hand和swapMinionwith1Hand能够处理多个目标
	def returnObj2Hand(self, subject, obj, deathrattlesStayArmed=False, manaMod=None):
		ID = obj.ID
		if obj in self.minions[ID]: #如果随从仍在随从列表中
			self.add2EventinGUI(subject, obj)
			if self.Hand_Deck.handNotFull(ID):
				#如果onBoard仍为True，则其仍计为场上存活的随从，需调用disappears以注销各种扳机。
				if obj.onBoard: #随从存活状态下触发死亡扳机的区域移动效果时，不会注销其他扳机
					obj.disappears(deathrattlesStayArmed)
				#如onBoard为False,则disappears已被调用过了。主要适用于触发死亡扳机中的区域移动效果
				self.removeMinionorWeapon(obj, animate=False)
				obj.reset(ID)
				self.Hand_Deck.hands[ID].append(obj)
				if manaMod: obj.manaMods.append(manaMod)
				if self.GUI: self.GUI.board2HandAni(obj)
				self.Hand_Deck.finalizeCardintoHand(obj, ID, comment="Enter")
				self.Manas.calcMana_Single(obj)
				#for func in target.returnResponse: func()
				return obj
			else: #让还在场上的活着的随从返回一个满了的手牌只会让其死亡
				if obj.onBoard: obj.dead = True
				#for func in target.returnResponse: func()
		elif obj.inDeck: #如果目标阶段已经在牌库中了，将一个基础复制置入其手牌。
			Copy = type(obj)(self, ID)
			self.add2EventinGUI(subject, Copy)
			if manaMod: obj.manaMods.append(manaMod)
			self.Hand_Deck.addCardtoHand(Copy, ID)
		elif obj.inHand and manaMod: manaMod.applies()

	def swapMinionwith1Hand(self, subject, obj):
		hand = self.Hand_Deck.hands[obj.ID]
		if obj.onBoard and hand and (inds := [i for i, card in enumerate(hand) if card.category == "Minion"]):
			i, ID = numpyChoice(inds), obj.ID
			minion, pos = hand[i], obj.pos
			minion.disappears()
			self.removeMinionorWeapon(minion, animate=False)
			minion.reset(ID)
			hand.append(minion)
			self.Hand_Deck.finalizeCardintoHand(minion, ID, comment="Enter")
			# 假设先发送牌进入手牌的信号，然后召唤随从
			self.summonfrom(i, ID, pos, summoner=subject, hand_deck=0)

	#Shuffle a single minion to deck
	#targetDeckID decides the destination. initiatorID is for triggers, such as Trig_AugmentedElekk
	def returnMiniontoDeck(self, obj, targetDeckID, initiatorID, deathrattlesStayArmed=False):
		if obj in self.minions[obj.ID]:
			#如果onBoard仍为True，则其仍计为场上存活的随从，需调用disappears以注销各种扳机
			if obj.onBoard: #随从存活状态下触发死亡扳机的区域移动效果时，不会注销其他扳机
				obj.disappears(deathrattlesStayArmed)
			#如onBoard为False，则disappears已被调用过了。主要适用于触发死亡扳机中的区域移动效果
			self.removeMinionorWeapon(obj, animate=False)
			obj.reset(targetDeckID) #永恒祭司的亡语会备份一套enchantment，在调用该函数之后将初始化过的本体重新增益
			self.Hand_Deck.shuffleintoDeck(obj)
			return obj
		elif obj.inHand: #如果随从已进入手牌，仍会将其强行洗入牌库
			self.Hand_Deck.shuffleintoDeck(self.Hand_Deck.extractfromHand(obj)[0])
			return obj
		else: return None

	def minionSwitchSide(self, target, activity="Permanent"):
		#如果随从在手牌中，则该会在手牌中换边；如果随从在牌库中，则无事发生。
		if target.inHand and target in self.Hand_Deck.hands[target.ID]:
			card, mana, posinHand = self.Hand_Deck.extractfromHand(target, enemyCanSee=True)
			#addCardtoHand method will force the ID of the card to change to the target hand ID.
			#If the other side has full hand, then the card is extracted and thrown away.
			self.Hand_Deck.addCardtoHand(card, 3-card.ID)
		elif target.onBoard: #If the minion is on board.
			if self.space(3-target.ID) < 1: target.dead = True
			else:
				target.disappears() #随从控制权的变更会注销其死亡扳机，随从会在另一方重新注册其所有死亡扳机
				self.minions[target.ID].remove(target)
				target.ID = 3 - target.ID
				self.minions[target.ID].append(target)
				self.sortPos() #The appearance sequence stays intact.
				target.appears(firstTime=False) #控制权的变更不会触发水晶核心以及休眠随从的再次休眠等
				#Possible activities are "Permanent" "Borrow" "Return"
				#一个随从在被暂时控制的情况下会在回合结束时归还对方，但是不认它被连续几次暂时控制，都只进行一次控制权的切换
				#被暂时控制的随从如果被无面操纵者复制，复制者也可以攻击，回合时，连同复制者一并归还对面。
				if activity == "Borrow": target.effects["Borrowed"] = 1
				else: target.effects["Borrowed"] = 0 #Return or permanent
				target.decideAttChances_base()
				if GUI := self.GUI:
					GUI.seqHolder[-1].append(GUI.PARALLEL(GUI.minionZones[1].placeCards(add2Queue=False),
															GUI.minionZones[2].placeCards(add2Queue=False)))

	#For those that have more complicated pretest requirements, they have their own complicated canTrig/trig
	def armedTrigs(self, sig):
		trigs = []
		for ID in (self.mainPlayerID, 3 - self.mainPlayerID):
			if sig in (ls := self.trigsBoard[ID]): trigs += ls[sig]
			if sig in (ls := self.trigsHand[ID]): trigs += ls[sig]
			if sig in (ls := self.trigsDeck[ID]): trigs += ls[sig]
		return trigs

	#New signal processing can be interpolated during the processing of old signal
	def sendSignal(self, signal, ID, subject=None, target=None, num=None, comment='', choice=0, trigPool=None):
		hasResponder = False
		#即使trigPool传入的值是[]，也说明之前进行了扳机预检测，需要进入if的语句中
		if trigPool is not None: #主要用于打出xx牌和随从死亡时/后扳机，它们有预检测机制。
			if i := next((i for i, trig in enumerate(trigPool) if hasattr(trig, "lastinQ")), -1) > -1:
				trigPool.append(trigPool.pop(i))  # 目前一次信号的结算中只可能有一个扳机可以拥有top priority
			for trig in trigPool: #扳机只有仍被注册情况下才能触发，但是这个状态可以通过canTrigger来判断，而不必在所有扳机列表中再次检查。
				if trig.canTrig(signal, ID, subject, target, num, comment, choice): #扳机能触发通常需要扳机记录的实体还在场上等。
					hasResponder = True
					trig.trig(signal, ID, subject, target, num, comment, choice)
		else: #向所有注册的扳机请求触发。先后触发主副玩家的场上，手牌和牌库扳机
			mainPlayerID = self.mainPlayerID #假设主副玩家不会在一次扳机结算之中发生变化。先触发主玩家的各个位置的扳机。
			#Trigger the trigs on main player's side, in the following order board-> hand -> deck.
			for Id in [mainPlayerID, 3-mainPlayerID]:
				for gameTrigs in (self.trigsBoard[Id], self.trigsHand[Id], self.trigsDeck[Id]):
					if signal in gameTrigs and (trigs := [trig for trig in gameTrigs[signal] if trig.canTrig(
																signal, ID, subject, target, num, comment, choice)]):
						hasResponder = True
						#目前可以保证自己在扳机结算队列末尾的扳机有骑士奥秘救赎和伤害扳机明月之牙
						if i := next((i for i, trig in enumerate(trigs) if hasattr(trig, "lastinQ")), -1) > -1:
							trigs.append(trigs.pop(i)) #目前一次信号的结算中只可能有一个扳机可以拥有top priority
						for trig in trigs: trig.trig(signal, ID, subject, target, num, comment, choice)
		return hasResponder

	#Process the damage transfer. If no transfer happens, the original target is returned
	def scapegoat4(self, target, subject=None):
		holder = [target]
		#Each damage trigger only triggers once during a single resolution
		while self.sendSignal("DmgTaker?", 0, subject, holder):
			pass
		dmgTaker = holder[0]
		self.sendSignal("DmgTaker?", 0, None, None, 0, "Reset") #Reset all damage modification trigger.
		return dmgTaker

	# 不管target是否还在场上，此时只要市长还在，就要重新在场上寻找合法目标。
	# 如果找不到，就return None，不能触发战吼的指向性部分，以及其产生的后续操作
	def try_RedirectEffectTarget(self, signal, subject, target, choice):
		if target:
			if self.GUI: self.GUI.resetSubTarColor(subject, target)
			if not isinstance(target, list):
				holder = [target]
				self.sendSignal(signal, subject.ID, self, holder, 0, "", choice)
				target = holder[0]
			if self.GUI: self.GUI.resetSubTarColor(None, target)
		return target

	def heroTakesDamage(self, ID, dmg):
		self.scapegoat4(self.heroes[ID]).takesDamage(None, dmg, "Ability")

	#The weapon will also join the deathList and compare its own sequence against other minions.
	def gathertheDead(self, decideWinner=False):
		#Determine what characters are dead. The die() method hasn't been invoked yet.
		#序列内部不包含胜负裁定，即只有回合开始、结束产生的序列；
		#回合开始抽牌产生的序列；打出随从，法术，武器，英雄牌产生的序列；
		#以及战斗和使用英雄技能产生的序列以及包含的所有亡语等结算结束之后，胜负才会被结算。
		deads2Sort = []
		for ID in (1, 2):
			for obj in self.minions[ID] + self.weapons[ID]:
				if obj.health < 1 or obj.dead:
					if obj.category == "Minion" and obj.effects["Disappear When Die"] > 0:
						self.banishMinion(None, obj)
						continue
					obj.dead = True
					deads2Sort.append((obj, obj.attack, obj.health))
					obj.disappears(deathrattlesStayArmed=True) #随从死亡时不会注销其死亡扳机，这些扳机会在触发之后自行注销
			#无论是不在此时结算胜负，都要在英雄的生命值降为0时将其标记为dead
			if self.heroes[ID].health < 1: self.heroes[ID].dead = True

		if deads2Sort:
			#Rearrange the dead minions according to their sequences.
			deadObjs = [obj for obj, att, health in deads2Sort]
			if self.GUI: self.GUI.minionsDieAni(deadObjs)
			self.deads += [deads2Sort[i] for i in objs_SeqSorted(deadObjs)[1]]

		if not self.resolvingDeath: #如果游戏目前已经处于死亡结算过程中，不会再重复调用deathHandle
			#如果要执行胜负判定或者有要死亡/摧毁的随从/武器，则调用deathHandle
			if decideWinner or self.deads: self.deathHandle(decideWinner)

	#大法师施放的闷棍会打断被闷棍的随从的回合结束结算。可以视为提前离场。
	#死亡缠绕实际上只是对一个随从打1，然后如果随从的生命值在1以下，则会触发抽牌。它不涉及强制死亡导致的随从提前离场
	#当一个拥有多个亡语的随从死亡时，多个亡语触发完成之后才会开始结算其他随从死亡的结算。
	#每次gathertheDead找到要死亡的随从之后，会在它们这一轮的死亡事件全部处理之后，才再次收集死者，用于下次死亡处理。
		#复生随从也会在一轮死亡结算之后统一触发。
	#亡语实际上是随从死亡时触发的扳机，例如食腐土狼与亡语野兽的结算是先登场者先触发
	def deathHandle(self, decideWinner=False):
		while self.deads:
			rebornMinions = []
			if not self.deads: break #If no minions are dead, then stop the loop
			armedTrigs_WhenDies = self.armedTrigs("ObjDies")
			armedTrigs_AfterDied = self.armedTrigs("ObjDied")
			while self.deads:
				self.resolvingDeath = True
				obj2Die, obj2Die.attack, obj2Die.health = self.deads.pop(0)
				#For now, assume Tirion Fordring's deathrattle equipping Ashbringer won't trigger player's weapon's deathrattles right away.
				#weapons with regard to deathrattle triggering is handled the same way as minions.
				#同一卡牌有多个亡语时，它们会连续触发，然后结算下个卡牌的亡语。每个亡语触发时检测是否有"亡语触发两次"光环，提前决定触发次数。
				if obj2Die.category == "Minion" and obj2Die.effects["Reborn"] > 0: rebornMinions.append(obj2Die)
				obj2Die.deathResolution(armedTrigs_WhenDies, armedTrigs_AfterDied)
				self.removeMinionorWeapon(obj2Die) #结算完一个随从的亡语之后将其移除。
				obj2Die.reset(obj2Die.ID) #亡语结算之后把pos调回-2
				obj2Die.dead = True
			#当一轮死亡结算结束之后，召唤这次死亡结算中死亡的复生随从
			for rebornMinion in rebornMinions:
				miniontoSummon = type(rebornMinion)(self, rebornMinion.ID)
				miniontoSummon.effects["Reborn"], miniontoSummon.health = 0, 1 #不需要特殊的身材处理，激怒等直接在随从的appears()函数中处理。
				self.summon(miniontoSummon, rebornMinion.pos, rebornMinion)
			#死亡结算每轮结束之后才进行是否有新的死者的收集，然后进行下一轮的亡语结算。
			self.gathertheDead(decideWinner) #See if the deathrattle results in more death or destruction.

		self.resolvingDeath = False
		#The reborn effect take place after the deathrattles of minions have been triggered.
		if decideWinner: #游戏中选手的死亡状态
			#gameEnds = 0: No one dies; 1: Only Hero1 dies; 2: Only Hero2 dies, 3: Both heroes die
			self.gameEnds = (self.heroes[1].dead or self.heroes[1].health <= 0) + 2 * (self.heroes[2].dead or self.heroes[2].health <= 0)
			GUI = self.GUI
			if self.gameEnds and GUI:
				if self.gameEnds == 1: GUI.heroExplodeAni([self.heroes[1]])
				elif self.gameEnds == 2: GUI.heroExplodeAni([self.heroes[2]])
				else: GUI.heroExplodeAni([self.heroes[1], self.heroes[2]])
	"""
	At the start of turn, the AOE destroy/AOE damage/damage effect won't kill minions make them leave the board.
	As long as the minion is still on board, it can still trigger its turn start/end effects.
	Special things are Sap/Defile, which will force the minion to leave board early.
	#The Defile will cause the game to preemptively start death resolution.
	Archmage casting spell will be able to target minions with health <= 0, since they are not regarded as dead yet.
	The deaths of minions will be handled at the end of triggering, which is then followed by drawing card.
	"""
	
	"""
	自己和自己玩的情况下，因为没有GUI.sock_Recv/sock_Send，所以始终都会endTurn接startTurn
	双人对战的情况下
		玩家X结束回合的时候sendthruServer=True， intiatesChain=True，endTurn结尾时终止自己的动画sequence，
			向对方发送endTurn的move，并开始等待对方的回合结束、回合开始，从而补完自己的回合切换流程
	 	玩家Y接手玩家X的回合结束，sendthruServer=False，initiatesChain=False，endTurn结尾时接自己的回合开始
	 	玩家Y自己的回合开始使用finallyWrapUpSwitchTurn=False。完毕时sendThruServer为True，会向对方发送startTurn的move
	 	玩家X接到对方回传的回合开始消息，finallyWrapUpSwitchTurn=True。完毕时，sendThruServer为False，不再回传任何消息
	"""
	def endTurn(self, sendthruServer=True, initiatesChain=True):
		GUI = self.GUI
		self.prepGUI4Ani(GUI)
		if GUI: GUI.turnEndButtonAni_FlipRegardless()
		for ID in (1, 2):
			for card in self.minions[ID] + self.Hand_Deck.hands[ID]: #Include the Dormants.
				card.turnEnds(self.turn) #Handle minions' usageCount and attChances
			self.heroes[ID].turnEnds(self.turn)
			self.powers[ID].turnEnds(self.turn)
		self.sendSignal("TurnEnds", self.turn)
		self.gathertheDead(True)
		#The secrets and temp effects are cleared at the end of turn.
		for obj in self.turnEndTrigger[:]: obj.trig_TurnTrig() #所有一回合光环都是回合结束时消失，即使效果在自己回合外触发了也是如此

		self.Counters.turnEnds()
		self.Manas.turnEnds()
		"""目前没有必要考虑连续进行回合的情况，以后大概不会再出类似的牌"""
		self.turn = 3 - self.turn #Changes the turn to another hero.
		
		#If there is an opponent, they take over the rest, and later return a "startTurn" move
		theresOppo2TakeOver = GUI and GUI.sock_Send
		#initiatesChain和theresOppo2TakeOver一般会有至少一个是真的
		#自己和自己玩的时候总是initiatesChain，但是只有有对手并且自己在开始chain的时候才会停下来等对面走完回合结束和开始
		if initiatesChain: self.moves.append(("endTurn",)) #只有作为发起玩家时才会添加endTurn到move中。
		if initiatesChain and theresOppo2TakeOver:
			self.wrapUpPlay(GUI, sendthruServer, endingTurn=True)
		else: #自己和自己玩，或者，接到了对面的回合结束，自己这边需要先走完回合开始后，再传回给对面
			self.startTurn(finallyWrapUpSwitchTurn=False, sendthruServer=False)
		return True
	
	#自己和自己玩或者自己接收到对方的回合结束，需要补完的时候fromOppoMove都是False
	#只有自己的回合结束收到了对方的回合开始补完时fromOppoMove才会是True
	def startTurn(self, finallyWrapUpSwitchTurn, sendthruServer):
		GUI = self.GUI
		if GUI:
			#如果是自己和自己玩的话，则GUI.seqReady本来也应该还是False,没有影响。从对面接收来的操作需要重开一个Sequence
			self.prepGUI4Ani(GUI, newSequence=finallyWrapUpSwitchTurn)
			GUI.turnStartAni()
		self.turnInd += 1
		self.Counters.turnStarts()
		self.Manas.turnStarts()
		self.sendSignal("NewTurnStarts", self.turn, None, None, 0, '')
		for obj in self.turnStartTrigger[:]:
			if obj.ID == self.turn: obj.trig_TurnTrig()

		for ID in (1, 2):
			self.heroes[ID].turnStarts(self.turn)
			self.powers[ID].turnStarts(self.turn)
			if GUI:
				for secret in self.Secrets.secrets[ID]: secret.btn.checkHpr()
			for card in self.minions[ID] + self.Hand_Deck.hands[ID]: #Include the Dormants.
				card.turnStarts(self.turn) #Handle minions' usageCount and attChances

		self.sendSignal("TurnStarts", self.turn)
		self.gathertheDead(True)
		#抽牌阶段之后的死亡处理可以涉及胜负裁定。
		self.Hand_Deck.drawCard(self.turn)
		self.Hand_Deck.drawCard(self.turn)
		self.Hand_Deck.drawCard(self.turn)
		self.Hand_Deck.drawCard(self.turn)
		self.gathertheDead(True) #There might be death induced by drawing cards.
		
		#只有在不是自己
		if not finallyWrapUpSwitchTurn: self.moves.append(("startTurn",))
		#自己和自己玩的时候发送消息与否没有影响，而自己在补完对方的回合结束时需要发送消息
		#自己在回合结束后接收到对方发来的补完消息后，不再把己方的消息再次回传。只有此时fromOppoMove才会是True
		self.wrapUpPlay(GUI, sendthruServer=not finallyWrapUpSwitchTurn, endingTurn=False)
		return True

	def pastTurnInd(self, ID, backby=1): #进行过的回合里面最近的一个不是当前回合的回合数
		i = 0 #the most recent turn is backby=1, the past 3 turns will need backby=3
		for turnInd in reversed(self.Counters.playersTurnInds[ID]):
			if turnInd != self.turnInd:
				i += 1
				if i == backby: return turnInd
		return -2 #If can't find the turn wanted, then return -2. -1 is reserved for self.Counters.iter_AllTupsSoFar

	#有两种情况：玩家指挥随从和英雄攻击；卡牌效果使随从/英雄攻击。默认为卡牌效果发起攻击。
	#只有玩家指挥情况下verifySelectable&useAttChance为True，一般只有玩家指挥下的战斗结算resolveDeath
	#只有一个随从/英雄连续攻击时才会把resetRedirTrig设为False。重导向扳机和攻击时免疫在这个信号发出的时候才会重置/取消
	#疯狂巨龙死亡之翼和狂乱可以让一个随从连续攻击。它们在效果结算结束的时候会主动补充发送一个"BattleFinished"的信号。
	def battle(self, subject, target, verifySelectable=False, useAttChance=False, resolveDeath=False,
			   resetRedirTrig=True, evenifDead=False, sendthruServer=False):
		if verifySelectable and not subject.canAttackTarget(target):
			return False
		#战斗阶段：
			#攻击前步骤： 触发攻击前扳机，列队结算，如爆炸陷阱，冰冻陷阱，误导
				#如果扳机结算完毕后，被攻击者发生了变化，则再次进行攻击前步骤的扳机触发。重复此步骤直到被攻击者没有变化为止。
				#在这些额外的攻击前步骤中，之前已经触发过的攻击前扳机不能再能触发。主要是指市长和傻子
			#攻击时步骤：触发攻击时扳机，如真银圣剑，智慧祝福，血吼，收集者沙库尔等
			#如果攻击者，被攻击目标或者任意一方英雄离场或者濒死，则攻击取消，跳过伤害和攻击后步骤。
			#无论攻击是否取消，攻击者的attackedTimes都会增加。
			#伤害步骤：攻击者移除潜行，攻击者对被攻击者造成伤害，被攻击者对攻击者造成伤害。然后结算两者的伤害事件。
			#攻击后步骤：触发“当你的xx攻击之后”扳机。如捕熊陷阱，符文之矛。
				#蜡烛弓和角斗士的长弓给予的免疫被移除。
			#战斗阶段结束，处理死亡事件
		#如果有攻击之后的发现效果需要结算，则在此结算之后。


		#如果一个角色被迫发起攻击，如沼泽之王爵德，野兽之心，群体狂乱等，会经历上述的战斗阶段的所有步骤，之后没有发现效果结算。同时角色的attackedTimes不会增加。
		#之后没有阶段间步骤（因为这种强制攻击肯定是由其他序列引发的）
		#疯狂巨龙死亡之翼的连续攻击中，只有第一次目标选择被被市长改变，但之后的不会
		print("Handling battle", subject, target)
		subLocator = tarLocator = 0
		if verifySelectable: subLocator, tarLocator = self.genLocator(subject), self.genLocator(target)
		GUI = self.GUI
		self.prepGUI4Ani(GUI)
		if GUI:
			GUI.resetSubTarColor(subject, target)
			dy = 0.5 * (1 if GUI.heroZones[subject.ID].heroPos[1] < 0 else -1)
			GUI.offsetNodePath_Wait(subject.btn.np, duration=0.15, dy=dy, dz=5)
			GUI.seqHolder[-1].append(GUI.WAIT(0.3))

		#如果英雄的武器为蜡烛弓和角斗士的长弓，则优先给予攻击英雄免疫，防止一切攻击前步骤带来的伤害。
		self.sendSignal("BattleStarted", subject.ID, subject, target) #这里的target没有什么意义，可以留为target
		#在此，奥秘和健忘扳机会在此触发。需要记住初始的目标，然后可能会有诸多扳机可以对此初始信号响应。
		targetHolder = [target, target] #第一个target是每轮要触发的扳机会对应的原始随从，目标重导向扳机会改变第二个
		signal = subject.category + "Attacks" + targetHolder[0].category
		self.sendSignal(signal, subject.ID, subject, targetHolder, 0, "1stPre-attack")
		#第一轮攻击前步骤结束之后，Game的记录的target如果相对于初始目标发生了变化，则再来一轮攻击前步骤，直到目标不再改变为止。
		#例如，对手有游荡怪物、误导和毒蛇陷阱，则攻击英雄这个信号可以按扳机入场顺序触发误导和游荡怪物，改变了攻击目标。之后的额外攻击前步骤中毒蛇陷阱才会触发。
		#如果对手有崇高牺牲和自动防御矩阵，那么攻击随从这个信号会将两者都触发，此时攻击目标不会因为这两个奥秘改变。
		#健忘这个特性，如果满足触发条件，且错过了50%几率，之后再次满足条件时也不会再触发这个扳机。这个需要在每个食人魔随从上专门放上标记。
			#如果场上有多个食人魔勇士，则这些扳机都只会在第一次信号发出时触发。
		#如果一个攻击前步骤中，目标连续发生变化，如前面提到的游荡怪物和误导，则只会对最新的目标进行下一次攻击前步骤。
		#如果一个攻击前步骤中，目标连续发生变化，但最终又变回与初始目标相同，则不会产生新的攻击前步骤。
		#在之前的攻击前步骤中触发过的扳机不能再后续的额外攻击前步骤中再次触发，主要作用于傻子和市长，因为其他的攻击前扳机都是奥秘，触发之后即消失。
		#只有在攻击前步骤中可能有攻击目标的改变，之后的信号可以大胆的只传递目标本体，不用targetHolder
		while targetHolder[1] is not targetHolder[0]: #这里的target只是refrence传递进来的target，赋值过程不会更改函数外原来的target
			targetHolder[0] = targetHolder[1] #攻击前步骤改变了攻击目标，则再次进行攻击前步骤，与这个新的目标进行比对。
			if GUI: GUI.resetSubTarColor(subject, targetHolder[0])
			signal = subject.category+"Attacks"+targetHolder[0].category #产生新的触发信号。
			self.sendSignal(signal, subject.ID, subject, targetHolder, 0, "FollowingPre-attack")
		target = targetHolder[1] #攻击目标改向结束之后，把targetHolder里的第二个值赋给target(用于重导向扳机的那个),这个target不是函数外的target了
		#攻击前步骤结束，开始结算攻击时步骤
		#攻击时步骤：触发“当xx攻击时”的扳机，如真银圣剑，血吼，智慧祝福，血吼，收集者沙库尔等
		signal = subject.category+"Attacking"+target.category
		self.sendSignal(signal, subject.ID, subject, target)
		#如果此时攻击者，攻击目标或者任意英雄濒死或离场所，除非无视死亡情况，否则攻击取消，跳过伤害和攻击后步骤。
		battleContinues = True
		#如果攻击者和目标不再是场上的随从/英雄，则停止攻击。（可以要求两者不一定都是活的）
		if not (subject.canBattle(mustbeAlive=not evenifDead) and target.canBattle(mustbeAlive=not evenifDead)):
			battleContinues = False #如果不满足攻击者&目标均为场上的随从/英雄，则停止攻击
		elif not ((self.heroes[1].health > 0 and not self.heroes[1].dead) and (self.heroes[2].health > 0 and not self.heroes[2].dead)
				): #假设即使攻击无视死亡的情况下，如果双方英雄有死亡的时候仍然会停止攻击
			battleContinues = False

		if not battleContinues: #如果攻击者被冰冻陷阱弹回手牌，但是又因为其他卡牌效果被拉出来，则仍然会判定其攻击未遂而消耗一次攻击机会。
			if useAttChance and subject.onBoard: subject.usageCount += 1  # If this attack is canceled, the attack time still increases.
			if GUI: GUI.attackAni_Cancel(subject)
		else:
			#伤害步骤，攻击者移除潜行，攻击者对被攻击者造成伤害，被攻击者对攻击者造成伤害。然后结算两者的伤害事件。
			#攻击者和被攻击的血量都减少。但是此时尚不发出伤害判定。先发出攻击完成的信号，可以触发扫荡打击。
			if GUI: GUI.attackAni_HitandReturn(subject, target)
			self.Counters.handleGameEvent("Battle", subLocator, tarLocator)
			subject.landsAtk(target, useAttChance, duetoCardEffects=not verifySelectable)
			#获得额外攻击机会的触发在随从死亡之前结算。有隐藏的条件：自己不能处于濒死状态。
			self.sendSignal(subject.category+"Attacked"+target.category, subject.ID, subject, target)
		#"Immune while attacking" effect ends, reset attack redirection triggers, like Mogor the Ogre
		if resetRedirTrig: #这个选项目前只有让一个随从连续攻击其他目标时才会选择关闭，不会与角斗士的长弓冲突
			self.sendSignal("BattleFinished", subject.ID, subject)
		#战斗阶段结束，处理亡语，此时可以处理胜负问题。
		if resolveDeath:
			self.gathertheDead(True)
		if verifySelectable: #只有需要验证攻击目标的攻击才是玩家的游戏操作
			self.moves.append(("battle", subLocator, tarLocator))
			self.wrapUpPlay(GUI, sendthruServer)
		return True
	
	def check_playSpell(self, spell, target, choice):
		return self.Manas.affordable(spell) and spell.available() and spell.selectionLegit(target, choice)

	def check_UsePower(self, power, target, choice):
		return self.Manas.affordable(power) and power.available() and power.selectionLegit(target, choice)

	#comment = "InvokedbyAI", "Branching-i", ""(GUI by default)
	def playSpell(self, spell, target, choice=0, comment="", sendthruServer=True):
		#古加尔的费用光环需要玩家的血量加护甲大于法术的当前费用或者免疫状态下才能使用
		if not self.check_playSpell(spell, target, choice):
			return False
			#使用阶段：
				#支付费用，相关费用状态移除，包括血色绽放，墨水大师，卡雷苟斯以及暮陨者艾维娜。
				#奥秘和普通法术会进入不同的区域。法术反制触发的话会提前终止整个序列。
				#使用时步骤： 触发伊利丹，紫罗兰老师，法力浮龙等“每当你使用一张xx牌”的扳机
				#获得过载和双重法术。
			#结算阶段
				#目标随机化和修改：市长和扰咒术结算（有主副玩家和登场先后之分）
				#按牌面结算，泽蒂摩不算是扳机，所以只要法术开始结算时在场，那么后面即使提前离场也会使用第二次结算的法术对相信随从生效。
			#完成阶段：
				#如果该牌有回响，结算回响（没有其他牌可以让法术获得回响）
				#使用后步骤：触发“当你使用一张xx牌之后”的扳机，如狂野炎术士，西风灯神，星界密使和风潮的状态移除。

			#如果是施放的法术（非玩家亲自打出）
			#获得过载，与双生法术 -> 依照版面描述结算，如有星界密使或者风潮，这个法术也会被重复或者法强增益，但是不会触发泽蒂摩。 -> 星界密使和风潮的状态移除。
			#符文之矛和导演释放的法术也会使用风潮或者星界密使的效果。
			#西风灯神和沃拉斯的效果仅是获得过载和双生法术 ->结算法术牌面
			
		subLocator, tarLocator = self.getSubTarLocators(spell, target)
		self.prepGUI4Ani(GUI := self.GUI)
		if GUI: GUI.seqHolder[-1].append(GUI.FUNC(removefrom, spell, GUI.playedCards))
		#支付法力值，结算血色绽放等状态。
		isaSecret2Hide = GUI and spell.race == "Secret" and GUI.sock_Send and spell.ID != GUI.ID and not GUI.showEnemyHand
		spell, mana, posinHand = self.Hand_Deck.extractfromHand(spell, enemyCanSee=not isaSecret2Hide)
		spell, mana = spell.becomeswhenPlayed(choice) #如果随从没有爆能强化等，则无事发生。
		self.Manas.payManaCost(spell, mana)
		self.cardinPlay = spell
		#记录游戏事件的发生
		self.eventinGUI(spell, eventType="PlaySpell", target=target, level=0)
		#请求使用法术，如果此时对方场上有法术反制，则取消后续序列。
		#法术反制会阻挡使用时扳机，如伊利丹和任务达人等。但是法力值消耗扳机，如血色绽放，肯瑞托法师会触发，从而失去费用光环
		#被反制掉的法术会消耗“下一张法术减费”光环，但是卡雷苟斯除外（显然其是程序员自己后写的）
		#被反制掉的法术不会触发巨人的减费光环，不会进入你已经打出的法术列表，不计入法力飓风的计数
		#被反制的法术不会被导演们重复施放
		#很特殊的是，连击机制仍然可以通过被反制的法术触发。所以需要一个本回合打出过几张牌的计数器
		#https://www.bilibili.com/video/av51236298?zw
		self.resolveSpellBeingPlayed(spell, target, subLocator, tarLocator, choice, mana, posinHand, comment, sendthruServer)
		return True

	def resolveSpellBeingPlayed(self, spell, target, subLocator, tarLocator, choice, mana, posinHand, comment, sendthruServer):
		boolHolder = [0]
		self.sendSignal("SpellOK2Play?", self.turn, boolHolder, None, mana)
		#古神在上只会把打出法术变成一个打出一个随机的随机目标的法术。之后的一切结算照正常
		#正常过程打出: self.cardinPlay = spell, 		boolHolder = [0]
		#冰霜或法反后: self.cardinPlay = spell, 		boolHolder = [-1] #连续触发时需要self.cardinPlay
		#古神在上过后: self.cardinPlay = newSpell, 	boolHolder = [1]
		if boolHolder[0] < 0: self.Counters.comboCounters[self.turn] += 1 #被法反取消或被冰霜陷阱返回手牌
		else: #只有正常施放和被古神在上修改过的法术可以继续
			if boolHolder[0] > 0:
				spell = self.cardinPlay
				choice = spell.pickRandomChoice()
				if spell.numTargetsNeeded(choice) and (targets := spell.findTargets(choice)):
					target = numpyChoice(targets)
				else: target = None
			#处理完被古神修改成随机施放的法术之后，其他一切与正常打出法术的结算一致
			if self.GUI: self.GUI.resetSubTarColor(None, target)
			armedTrigs = self.armedTrigs("CardBeenPlayed")
			spell.played(target, choice, mana, posinHand, comment)  # choice用于抉择选项，comment用于区分是GUI环境下使用还是AI分叉
			# 使用后步骤，触发“每当使用一张xx牌之后”的扳机，如狂野炎术士，西风灯神，星界密使的状态移除和伊莱克特拉风潮的状态移除。
			self.Counters.handleCardPlayed(spell, target, mana, choice, posinHand)
			self.sendSignal("CardBeenPlayed", spell.ID, None, target, (mana, posinHand), "Spell", choice, armedTrigs)
			# 完成阶段结束，处理亡语，此时可以处理胜负问题。
			self.gathertheDead(True)  # 即使法术可以被古神在上变为随机施放的法术，也要进行死亡判定
			if isinstance(tarLocator, list):
				self.moves.append(("playSpell", subLocator, tuple(tarLocator), choice))
			else: self.moves.append(("playSpell", subLocator, tarLocator, choice))
		self.wrapUpPlay(self.GUI, sendthruServer)

	def usePower(self, power, target=(), choice=0, sendthruServer=True):
		if not self.check_UsePower(power, target, choice):
			return False
		print("Using hero power", power.name)
		# 支付费用，清除费用状态。
		subLocator, tarLocator = self.getSubTarLocators(power, target)
		# 准备游戏操作的动画
		GUI = self.GUI
		self.prepGUI4Ani(GUI)
		if GUI:
			GUI.showOffBoardTrig(power)
			self.eventinGUI(power, eventType="UsePower", target=target, level=0)

		self.Manas.payManaCost(power, (mana := power.mana))

		target = self.try_RedirectEffectTarget("EffectTarget?", power, target, choice)
		power.effect_wrapper(target, choice)
		# 结算阶段结束，处理死亡，此时尚不进行胜负判定。
		self.gathertheDead()

		power.usageCount += 1
		# 激励阶段，触发“每当你使用一次英雄技能”的扳机，如激励，虚空形态的技能刷新等。
		self.Counters.handleCardPlayed(power, target, mana, choice, -2) #-2 is placeholder for posinHand
		self.sendSignal("HeroUsedAbility", power.ID, power, target, power.mana, "", choice)
		if GUI: GUI.usePowerAni(power)
		# 激励阶段结束，处理死亡。此时可以进行胜负判定。
		self.gathertheDead(True)
		if GUI: GUI.decideCardColors()
		self.moves.append(("usePower", subLocator, tarLocator, choice))
		self.wrapUpPlay(GUI, sendthruServer)
		return True

	def availableWeapon(self, ID):
		return next((weapon for weapon in self.weapons[ID] if weapon.health > 0 and weapon.onBoard), None)

	"""Weapon with target will be handle later"""
	def check_playWeapon(self, weapon, target, choice):
		return self.Manas.affordable(weapon)
	
	def playWeapon(self, weapon, target, choice=0, sendthruServer=True):
		ID = weapon.ID
		if not self.check_playWeapon(weapon, target, choice):
			return False
		#使用阶段
			#卡牌从手中离开，支付费用，费用状态移除，但是目前没有根据武器费用支付而产生响应的效果。
			#武器进场，此时武器自身的扳机已经可以开始触发。如公正之剑可以通过触发的伊利丹召唤的元素来触发，并给予召唤的元素buff
			#使用时步骤，触发“每当你使用一张xx牌”的扳机”，如伊利丹，无羁元素等
			#结算过载。
			#结算死亡，尚不处理胜负问题。
		#结算阶段:
			#根据市长和铜须的存在情况决定战吼触发次数和目标（只有一个武器有指向性效果）
			#结算战吼、连击
			#消灭你的旧武器，将列表中前面的武器消灭，触发“每当你装备一把武器时”的扳机。
			#结算死亡（包括武器的亡语。）
		#完成阶段
			#使用后步骤，触发“每当你使用一张xx牌”之后的扳机。如捕鼠陷阱和瑟拉金之种等
			#死亡结算，可以处理胜负问题。
		subLocator, tarLocator = self.genLocator(weapon), self.genLocator(target)
		GUI = self.GUI
		self.prepGUI4Ani(GUI)
		#卡牌从手中离开，支付费用，费用状态移除，但是目前没有根据武器费用支付而产生响应的效果。
		weapon, mana, posinHand = self.Hand_Deck.extractfromHand(weapon, enemyCanSee=True, animate=False)
		self.Manas.payManaCost(weapon, mana)
		if GUI:
			GUI.seqHolder[-1].append(GUI.FUNC(removefrom, weapon, GUI.playedCards))
			GUI.showOffBoardTrig(weapon, animationType='')
			self.eventinGUI(weapon, eventType="PlayWeapon", target=target, level=0)
		#使用阶段，结算阶段。
		armedTrigs = self.armedTrigs("CardBeenPlayed")
		#武器进场
		self.weapons[ID].append(weapon)
		if GUI: GUI.weaponPlayedAni(weapon)
		weapon.played(target, 0, mana, posinHand, comment="") #There are no weapon with Choose One.
		#完成阶段，触发“每当你使用一张xx牌”的扳机，如捕鼠陷阱和瑟拉金之种等。
		self.Counters.handleCardPlayed(weapon, target, mana, choice, posinHand)
		self.sendSignal("CardBeenPlayed", weapon.ID, None, target, (mana, posinHand), "Weapon", choice, armedTrigs)
		#完成阶段结束，处理亡语，可以处理胜负问题。
		self.gathertheDead(True)
		self.moves.append(("playWeapon", subLocator, tarLocator, 0))
		self.wrapUpPlay(GUI, sendthruServer)
		return True
	
	#只是为英雄装备一把武器。结算相对简单
	#消灭你的旧武器，新武器进场，这把新武器设置为新武器，并触发扳机。
	def equipWeapon(self, weapon, creator=None):
		ID, weapon.creator = weapon.ID, creator
		for obj in self.weapons[ID]: obj.dead = True #角斗士的长弓仍然可以为攻击过程中的英雄提供免疫，因为它是依靠扳机进行判定的。
		self.weapons[ID].append(weapon)

		if self.GUI: self.GUI.weaponEquipAni(weapon)
		weapon.appears()
		weapon.setasNewWeapon()

	def check_playHero(self, heroCard, target, choice):
		return self.Manas.affordable(heroCard)
	
	def playHero(self, hero, target=None, choice=0, sendthruServer=True):
		ID = hero.ID
		if not self.check_playHero(hero, target, choice):
			return False
		#使用阶段
			#支付费用，费用状态移除
			#英雄牌进入战场
			#使用时步骤，触发“每当你使用一张xx牌”的扳机，如魔能机甲，伊利丹等。
			#新英雄的最大生命值，当前生命值以及护甲被设定为与旧英雄一致。获得英雄牌上标注的额外护甲。
			#使用阶段结束，结算死亡情况。
		#结算阶段
			#获得新的英雄技能
			#确定战吼触发的次数。
			#结算战吼和抉择。
			#结算阶段结束，处理死亡。
		#完成阶段
			#使用后步骤，触发“每当你使用一张xx牌之后”的扳机。如捕鼠陷阱和瑟拉金之种等
			#完成阶段结束，处理死亡，可以处理胜负问题。
		subLocator = self.genLocator(hero)
		#准备游戏操作的动画
		self.prepGUI4Ani(GUI := self.GUI)
		if GUI: GUI.seqHolder[-1].append(GUI.FUNC(removefrom, hero, GUI.playedCards))
		self.eventinGUI(hero, eventType="PlayHero", target=target, level=0) #从手牌中打出英雄牌的时候显示为整卡
		#支付费用，以及费用状态移除
		hero, mana, posinHand = self.Hand_Deck.extractfromHand(hero, enemyCanSee=True, linger=True)
		self.Manas.payManaCost(hero, mana)
		#使用阶段，结算阶段的处理。
		armedTrigs = self.armedTrigs("CardBeenPlayed")
		hero.played(None, choice, mana, posinHand, comment="")
		#完成阶段
		#使用后步骤，触发“每当你使用一张xx牌之后”的扳机，如捕鼠陷阱等。
		self.Counters.handleCardPlayed(hero, None, mana, choice, posinHand)
		self.sendSignal("CardBeenPlayed", ID, None, None, (mana, posinHand), "Hero", choice, armedTrigs)
		#完成阶段结束，处理亡语，可以处理胜负问题。
		self.gathertheDead(True)
		self.moves.append(("playHero", subLocator, 0, choice))
		self.wrapUpPlay(GUI, sendthruServer)
		return True
	
	def playCard_4Trade(self, subject, sendthruServer=True):
		HD, ID = self.Hand_Deck, subject.ID
		subLocator = self.genLocator(subject)
		GUI = self.GUI
		self.prepGUI4Ani(GUI)
		#先把手牌中的这些牌移出
		HD.hands[subject.ID].remove(subject)
		subject.leavesHand()
		self.Manas.manas[ID] -= 1 #不调用Manas.payManaCost
		if GUI:
			GUI.seqHolder[-1].append(GUI.FUNC(GUI.heroZones[ID].drawMana, self.Manas.manas[ID], self.Manas.manasUpper[ID],
											  self.Manas.manasLocked[ID], self.Manas.manasOverloaded[ID]))
			GUI.cardsLeaveHandAni([subject], ID, linger=True)
		if self.rules[ID]["Trade Discovers Instead"] > 0:
			_, i = subject.discoverfrom('')
			HD.drawCard(ID, i)
		else: HD.drawCard(ID)
		HD.shuffleintoDeck(subject, initiatorID=ID, enemyCanSee=False)
		self.eventinGUI(subject, eventType="Trade", level=0)
		if hasattr(subject, "tradeEffect"): subject.tradeEffect()
		self.moves.append(("playCard_4Trade", subLocator))
		self.wrapUpPlay(GUI, sendthruServer)
		return True
	
	def concede(self, ID, sendthruServer=True):
		GUI = self.GUI
		self.prepGUI4Ani(GUI)
		self.heroes[ID].dead = True
		if GUI:
			GUI.heroExplodeAni([self.heroes[ID]])
			GUI.stage = -2 #需要调成无响应状态
			GUI.seqHolder[-1].append(GUI.FUNC(GUI.setMsg, "Player %d Conceded!"%ID))
		self.moves.append(("concede", ID, 'Hero%d'%ID, 0))
		self.wrapUpPlay(GUI, sendthruServer)
		return True

	def genLocator(self, card=None):
		if not card: return 0
		ID = card.ID
		if card.onBoard:
			if card.category in ("Minion", "Amulet"): #X0Y: The Xth in minions[Y]
				return card.pos * 100 + ID #X doesn't matter here
			elif card.category == "Hero": #001Y: Hero Y
				return 10 + ID
			else: return 20 + ID #002Y: Power of player Y
		elif card.inHand: #X3Y: The Xth in self.Game.Hand_Deck.hands[Y]
			return self.Hand_Deck.hands[ID].index(card) * 100 + 30 + ID
		elif card.inDeck: #X4Y: The Xth in self.Game.Hand_Deck.decks[Y]
			return self.Hand_Deck.decks[ID].index(card) * 100 + 40 + ID
		else: return 50 + ID #5Y: From card with ID Y not in any of these zones

	#Find the card in the game using integer locator
	#index+zone+ID
	#Zone: Board--0, Hero--1, Power--2, Hand--3, Deck--4
	#2241: ID=1, Deck, index=22 --->self.Game.Hand_Deck.decks[1][22]
	#0002: ID=2, Board, index=0 -->self.Game.minions[2][0]
	def locate(self, locator): #ID last digit, zone 2nd last digit
		if not locator: return None
		ID, zone, i = locator % 10, int(locator % 100 / 10), int(locator / 100)
		if not zone: return self.minions[ID][i]
		elif zone == 1: return self.heroes[ID]
		elif zone == 2: return self.powers[ID]
		elif zone == 3: return self.Hand_Deck.hands[ID][i]
		elif zone == 4: return self.Hand_Deck.decks[ID][i]
		else: raise

	def isLocatoraFriendlyonBoardinHand(self, locator, ID):
		if locator and locator % 10 == ID and (zone := int(locator % 100 / 10)) in (0, 1, 3):
			return 1 if int(locator % 100 / 10) == 1 else 2
		else: return 0

	def evolvewithGuide(self, moves, picks):
		self.picks = picks[:]
		for move in moves: self.decodePlay(move)
		self.moves, self.picks = [], []

	def decodePlay(self, move):
		#接收并解读别人传来的信息时，需要把自己的回合开始先走完再说
		if move[0] == "endTurn": playCorrect = self.endTurn(sendthruServer=False, initiatesChain=False)
		#只会在自己发起的回合结束得到了对方的回合开始信息之后被调用
		elif move[0] == "startTurn": playCorrect = self.startTurn(finallyWrapUpSwitchTurn=True, sendthruServer=False)
		elif move[0] == "concede": playCorrect = self.concede(move[1], sendthruServer=False)
		else:
			sub = self.locate(move[1])
			if isinstance(move[2], tuple): tar = [self.locate(locator) for locator in move[2]]
			else: tar = self.locate(move[2])
			playCorrect = {"battle": lambda: self.battle(sub, tar, verifySelectable=True, useAttChance=True,
														 resolveDeath=True), #sendthruServer is False by default
							"usePower": lambda: self.usePower(sub, tar, move[3], sendthruServer=False),
							"playMinion": lambda: self.playMinion(sub, tar, move[3], move[4], sendthruServer=False),
							"playAmulet": lambda: self.playAmulet(sub, tar, move[3], move[4], sendthruServer=False),
							"playWeapon": lambda: self.playWeapon(sub, tar, move[3], sendthruServer=False),
							"playSpell": lambda: self.playSpell(sub, tar, move[3], sendthruServer=False),
							"playHero": lambda: self.playHero(sub, move[3], sendthruServer=False),
							"playCard_4Trade": lambda: self.playCard_4Trade(sub, sendthruServer=False),
							}[move[0]]()
			if self.GUI: self.GUI.subject, self.GUI.targets = None, None
		if not playCorrect: print("\n\n********DESYNCED!!!********\n\n")

	def eventinGUI(self, subject=None, eventType='', target=None, textSubject='', colorSubject=white,
				   textTarget='', colorTarget=white, level=1):
		if self.GUI: self.GUI.historyZone.eventinGUI(subject=subject, eventType=eventType, target=target,
													 textSubject=textSubject, colorSubject=colorSubject,
													 textTarget=textTarget, colorTarget=colorTarget, level=level)

	def add2EventinGUI(self, subject, target, textSubject='', textTarget='', colorSubject=white, colorTarget=white):
		if self.GUI: self.GUI.historyZone.add2Event(subject=subject, target=target, textSubject=textSubject, textTarget=textTarget,
													colorSubject=colorSubject, colorTarget=colorTarget)

	def usableObjs(self):
		plays, curTurn, affordable, checkTradeable = [], self.turn, self.Manas.affordable, self.Manas.checkTradeable
		hasSpaceonBoard = self.space(curTurn) > 0
		for card in self.Hand_Deck.hands[curTurn]:
			if checkTradeable(card) or \
					(affordable(card) and (card.category == "Minion" and hasSpaceonBoard) or
					 	(card.category == "Spell" and card.available()) or card.category in ("Hero", "Weapon")):
				plays.append(card)
		plays += [minion for minion in self.minionsonBoard(curTurn) if minion.canAttack() and minion.findBattleTargets()]
		hero = self.heroes[curTurn]
		if hero.canAttack() and hero.findBattleTargets(): plays.append(hero)
		if self.powers[curTurn].available(): plays.append(self.powers[curTurn])
		return plays
		
	def morePlaysPossible(self):
		curTurn, affordable, checkTradeable = self.turn, self.Manas.affordable, self.Manas.checkTradeable
		hasSpaceonBoard = self.space(curTurn) > 0
		for card in self.Hand_Deck.hands[curTurn]:
			if checkTradeable(card) or \
					(affordable(card) and (card.category == "Minion" and hasSpaceonBoard) or
					 (card.category == "Spell" and card.available()) or card.category in ("Hero", "Weapon")):
				return True
		if any(minion.canAttack() and minion.findBattleTargets() for minion in self.minionsonBoard(curTurn)):
			return True
		hero, power = self.heroes[curTurn], self.powers[curTurn]
		if hero.canAttack() and hero.findBattleTargets(): return True
		if affordable(power) and power.available(): return True
		return False