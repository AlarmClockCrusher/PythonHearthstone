from Parts_Handlers import *
from Parts_Hand import Hand_Deck
from Parts_ConstsFuncsImports import *

from HS_AcrossPacks import Illidan, Anduin
from HS_Stormwind import AuctioneerJaxon

SVClasses = ["Forestcraft", "Swordcraft", "Runecraft", "Dragoncraft", "Shadowcraft", "Bloodcraft", "Havencraft",
			 "Portalcraft"]

dict_GameEffects = {"Immune": "你的英雄免疫", "Immune2NextTurn": "你的英雄免疫直到你的下个回合", "ImmuneThisTurn": "你的英雄在本回合免疫",
					"Evasive": "你的英雄无法成为法术或英雄技能的目标", "Evasive2NextTurn": "直到下回合，你的英雄无法成为法术或英雄技能的目标",
					"Spell Damage": "你的英雄的法术伤害加成", "Spells Lifesteal": "你的法术具有吸血", "Spells x2": "你的法术会施放两次",
					"Spells Sweep": "你的法术也会对目标随从的相邻随从施放", "Spells Poisonous": "你的法术具有剧毒",
					"Fire Spell Damage": "你的英雄的火焰法术伤害加成",

					"Power Sweep": "你的英雄技能也会对目标随从的相邻随从生效", "Power Damage": "你的英雄技能伤害加成",  #Power Damage.
					"Power Can Target Minions": "你的英雄技能可以以随从为目标",
					"Power Chance 2": "可以使用两次英雄技能", "Power Chance Inf": "可以使用任意次数的英雄技能",
					"Heal to Damage": "你的治疗改为造成伤害", "Lifesteal Damages Enemy": "你的吸血会对敌方英雄造成伤害，而非治疗你",
					"Choose Both": "你的抉择卡牌可以同时拥有两种效果",
					"Battlecry x2": "你的战吼会触发两次", "Combo x2": "你的连击会触发两次",
					"Deathrattle X": "你的亡语不会触发", "Deathrattle x2": "你的随从的亡语触发两次", "Weapon Deathrattle x2": "你的武器的亡语触发两次",
					"Summon x2": "你的卡牌效果召唤的随从数量翻倍", "Secrets x2": "你的奥秘触发两次",
					"Minions Can't Be Frozen": "你的随从无法被冻结",  #Living Dragonbreath prevents minions from being Frozen
					"Ignore Taunt": "所有友方攻击无视嘲讽",  #Kayn Sunfury allows player to ignore Taunt
					"Hero Can't Be Attacked": "你的英雄不能被攻击",
					"Trade Discovers Instead": "交易时改为从牌库发现",
					}

statusDict = {key: 0 for key in dict_GameEffects.keys()}

class Game:
	def __init__(self, GUI=None, boardID="", mainPlayerID=0):
		self.mainPlayerID = mainPlayerID if mainPlayerID else numpyRandint(2) + 1
		self.GUI, self.boardID = GUI, boardID

	def initialize(self):
		self.initialClasses = {1: '', 2: ''}
		self.heroes = {1:Illidan(self, 1), 2:Anduin(self, 2)}
		self.powers = {1:self.heroes[1].heroPower(self, 1), 2:self.heroes[2].heroPower(self, 2)}
		self.heroes[1].onBoard = self.heroes[2].onBoard = True
		#Multipole weapons can coexitst at minions in lists. The newly equipped weapons are added to the lists
		self.minions, self.weapons = {1:[], 2:[]}, {1:[], 2:[]}
		self.options, self.mulligans = [], {1:[], 2:[]}
		self.players = {1:None, 2:None}
		#handlers.
		self.Counters, self.Manas, self.Discover, self.Secrets = Counters(self), Manas(self), Discover(self), Secrets(self)

		self.minionPlayed = None #Used for target change induced by triggers such Mayor Noggenfogger and Spell Bender.
		self.gameEnds, self.turn, self.numTurn = 0, 1, 1
		#self.turnstoTake = {1:1, 2:1} #For Temporus & Open the Waygate
		self.tempDeads, self.deads = [[], []], [[], []] #1st list records dead objects, 2nd records object attacks when they die.
		self.resolvingDeath = False
		self.effects = {1:statusDict, 2:copy.deepcopy(statusDict)}
		self.turnStartTrigger, self.turnEndTrigger = [], [] #用于一个回合的光环的取消
		self.trigAuras = {1:[], 2:[]} #用于一些永久光环，如砰砰博士的机械获得突袭。
		#登记了的扳机，这些扳机的触发依次遵循主玩家的场上、手牌和牌库。然后是副玩家的场上、手牌和牌库。
		self.trigsBoard, self.trigsHand, self.trigsDeck = {1:{}, 2:{}}, {1:{}, 2:{}}, {1:{}, 2:{}}
		
		self.mode = 0
		self.picks, self.picks_Backup, self.moves = [], [], []
		
		self.possibleSecrets = {1: [], 2: []}

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
		
	def minionsAlive(self, ID, exclude=None): #if exclude is not None, return all living minions except the exclude
		return [minion for minion in self.minions[ID] if minion.category == "Minion" \
				and minion != exclude and minion.onBoard and (not minion.dead or minion.effects["Can't Break"] > 0) and minion.health > 0]

	#exclude is the minion that won't counted in. With non-empty race, only count minions with certain race
	def minionsonBoard(self, ID, exclude=None, race=""): #if target is not None, return all onBoard minions except the target
		return [minion for minion in self.minions[ID] if minion.category == "Minion" and minion.onBoard and minion != exclude and race in minion.race]
		
	def amuletsonBoard(self, ID, exclude=None):
		return [amulet for amulet in self.minions[ID] if amulet.category == "Amulet" and amulet.onBoard and amulet != exclude]
		
	def minionsandAmuletsonBoard(self, ID, exclude=None):
		return [amulet for amulet in self.minions[ID] if amulet.category != "Dormant" and amulet.onBoard and amulet != exclude]
		
	def earthsonBoard(self, ID, exclude=None):
		return [amulet for amulet in self.minions[ID] if amulet.category == "Amulet" and amulet.onBoard and "Earth Sigil" in amulet.race and amulet != exclude]
		
	def neighbors2(self, target, countDormants=False):
		targets, ID, pos, i = [], target.ID, target.pos, 0
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

	def charsAlive(self, ID, exclude=None):
		hero = self.heroes[ID]
		objs = [obj for obj in self.minions[ID] if obj.category == "Minion" and obj != exclude and obj.onBoard and not obj.dead and obj.health > 0]
		if hero.health > 0 and not hero.dead and hero != exclude: objs.append(hero)
		return objs

	"""Handle playing cards"""
	def prepGUI4Ani(self, GUI, newSequence=True):
		if GUI:
			GUI.seqReady = False
			if newSequence: GUI.seqHolder.append(GUI.SEQUENCE())
			
	def wrapUpPlay(self, GUI, sendthruServer, endingTurn=False):
		if GUI:
			GUI.decideCardColors()
			GUI.seqReady = True #当seqHolder中最后一个sequence的准备完毕时，重置seqReady，告知GUI.mouseMove可以调用
			if GUI.sock and sendthruServer: GUI.sendOwnMovethruServer(endingTurn=endingTurn)
		self.moves, self.picks_Backup, self.picks = [], [], []
		
	def check_playAmulet(self, amulet, target, position, choice):
		return self.Manas.affordable(amulet) and self.space(amulet.ID) and amulet.selectionLegit(target, choice)
	
	def playAmulet(self, amulet, target, position, choice=0, comment="", sendthruServer=True):
		if not self.check_playAmulet(amulet, target, position, choice):
			return False
		# 打出随从到所有结算完结为一个序列，序列完成之前不会进行胜负裁定。
		# 打出随从产生的序列分为
		# 1）使用阶段： 支付费用，随从进入战场（处理位置和刚刚召唤等），抉择变形类随从立刻提前变形，黑暗之主也在此时变形。
		# 如果随从有回响，在此时决定其将在完成阶段结算回响
		# 使用时阶段：使用时扳机，如伊利丹，任务达人和魔能机甲等
		# 召唤时阶段：召唤时扳机，如鱼人招潮者，饥饿的秃鹫等
		# 得到过载
		###开始结算死亡事件。此时序列还没有结束，不用处理胜负问题。
		# 2）结算阶段： 根据随从的死亡，在手牌、牌库和场上等位置来决定战吼，战吼双次的扳机等。
		# 开始时判定是否需要触发多次战吼，连击
		# 指向型战吼连击和抉择随机选取目标。如果此时场上没有目标，则不会触发 对应指向部分效果和它引起的效果。
		# 抉择和磁力也在此时结算，不过抉择变形类随从已经提前结算，此时略过。
		###开始结算死亡事件，不必处理胜负问题。
		# 3）完成阶段
		# 召唤后步骤：召唤后扳机触发：如飞刀杂耍者，船载火炮等
		# 将回响牌加入打出者的手牌
		# 使用后步骤：使用后扳机：如镜像实体，狙击，顽石元素。低语元素的状态移除结算和dk的技能刷新等。
		###结算死亡，此时因为序列结束可以处理胜负问题。
		# 在打出序列的开始阶段决定是否要产生一个回响copy
		subLocator = self.genLocator(amulet)
		if target: #因为护符是SV特有的卡牌类型，所以其目标选择一定是列表填充式的
			tarLocator = [self.genLocator(obj) for obj in target]
		else: tarLocator = 0
		#准备游戏操作的动画
		GUI = self.GUI
		self.prepGUI4Ani(GUI)
		
		amulet, mana, posinHand = self.Hand_Deck.extractfromHand(amulet, enemyCanSee=True)
		self.Manas.payManaCost(amulet, mana)  # 海魔钉刺者，古加尔和血色绽放的伤害生效。
		# The new minion played will have the largest sequence.
		# 处理随从的位置的登场顺序。
		amulet.seq = len(self.minions[1]) + len(self.minions[2]) + len(self.weapons[1]) + len(self.weapons[2])
		self.minions[amulet.ID].insert(position + 100 * (position < 0), amulet)
		self.sortPos()
		# 使用随从牌、召唤随从牌、召唤结束信号会触发
		# 把本回合召唤随从数的计数提前至打出随从之前，可以让小个子召唤师等“每回合第一张”光环在随从打出时正确结算。连击等结算仍依靠cardsPlayedThisTurn
		self.amuletPlayed = amulet
		armedTrigs = self.armedTrigs("AmuletBeenPlayed")
		if self.GUI: self.GUI.wait(400)
		target = amulet.played(target, choice, mana, posinHand, comment)
		# 完成阶段
		# 只有当打出的随从还在场上的时候，飞刀杂耍者等“在你召唤一个xx随从之后”才会触发。当大王因变形为英雄而返回None时也不会触发。
		# 召唤后步骤，触发“每当你召唤一个xx随从之后”的扳机，如飞刀杂耍者，公正之剑和船载火炮等
		if self.amuletPlayed and self.amuletPlayed.onBoard:
			self.sendSignal("AmuletBeenSummoned", self.turn, self.amuletPlayed, target, mana, "")
		self.Counters.numCardsPlayedThisTurn[self.turn] += 1
		# 假设打出的随从被对面控制的话仍然会计为我方使用的随从。被对方变形之后仍记录打出的初始随从
		self.Counters.cardsPlayedEachTurn[self.turn][-1].append(type(self.amuletPlayed))
		self.Counters.manas4CardsEachTurn[self.turn][-1].append(mana)
		self.Counters.cardsPlayedThisGame[self.turn].append(type(self.amuletPlayed))
		# 使用后步骤，触发镜像实体，狙击，顽石元素等“每当你使用一张xx牌”之后的扳机。
		if self.amuletPlayed and self.amuletPlayed.category == "Amulet":
			if self.amuletPlayed.creator: self.Counters.createdCardsPlayedThisGame[self.turn] += 1
			# The comment here is posinHand, which records the position a card is played from hand. -1 means the rightmost, 0 means the leftmost
			self.sendSignal("AmuletBeenPlayed", self.turn, self.amuletPlayed, target, mana, posinHand, choice,
							armedTrigs)
		# ............完成阶段结束，开始处理死亡情况，此时可以处理胜负问题。
		self.gathertheDead(True)
		if isinstance(tarLocator, list): self.moves.append(("playAmulet", subLocator, tuple(tarLocator), position, choice))
		else: self.moves.append(("playAmulet", subLocator, tarLocator, position, choice))
		self.wrapUpPlay(GUI, sendthruServer)
		return True
	
	#There probably won't be board size limit changing effects.
	#Minions to die will still count as a placeholder on board. Only minions that have entered the tempDeads don't occupy space.
	def space(self, ID):
		#Minions and Dormants both occupy space as long as they are on board.
		return 7 - 2 * (self.heroes[ID].Class in SVClasses) - sum(minion.onBoard for minion in self.minions[ID])

	def check_playMinion(self, minion, target, position, choice=0):
		return (self.Manas.affordable(minion) and (self.space(minion.ID) or (minion.index.startswith("SV_") and minion.willAccelerate()))
				and minion.selectionLegit(target, choice))
	
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

		subLocator = self.genLocator(minion)
		if target:
			if isinstance(target, list): tarLocator = [self.genLocator(obj) for obj in target]
			else: tarLocator = self.genLocator(target) #非列表状态的target一定是炉石卡指定的
		else: tarLocator = 0
		#开始准备游戏操作对应的动画
		GUI = self.GUI
		self.prepGUI4Ani(GUI)
		#支付法力值，结算血色绽放等状态
		minion, mana, posinHand = self.Hand_Deck.extractfromHand(minion, enemyCanSee=True, animate=False)
		#如果打出的随从是SV中的爆能强化，激奏和结晶随从，则它们会返回自己的真正要打出的牌以及对应的费用
		minion, mana = minion.becomeswhenPlayed(choice) #如果随从没有爆能强化等，则无事发生。
		self.Manas.payManaCost(minion, mana) #海魔钉刺者，古加尔和血色绽放的伤害生效。
		if GUI:
			GUI.showOffBoardTrig(minion, animationType='')
			self.eventinGUI(minion, eventType="Play%s"%minion.category, target=target, level=0)
		#需要根据变形成的随从来进行不同的执行
		if minion.category == "Spell": #Shadowverse Accelerate minion might become spell when played
			self.minionPlayed, spell = None, minion
			spellHolder, origSpell = [spell], spell
			self.sendSignal("SpellOKtoCast?", self.turn, spellHolder, None, mana, "")
			if not spellHolder:
				self.Counters.numCardsPlayedThisTurn[self.turn] += 1
			else:
				if origSpell != spellHolder[0]: spellHolder[0].cast()
				else:
					if GUI: GUI.resetSubTarColor(None, target)
					armedTrigs = self.armedTrigs("SpellBeenPlayed")
					self.Counters.cardsPlayedEachTurn[self.turn][-1].append(type(spell))
					self.Counters.manas4CardsEachTurn[self.turn][-1].append(mana)
					self.Counters.cardsPlayedThisGame[self.turn].append(type(spell))
					spell.played(target, choice, mana, posinHand, comment) #choice用于抉择选项，comment用于区分是GUI环境下使用还是AI分叉
					self.Counters.numCardsPlayedThisTurn[self.turn] += 1
					self.Counters.numSpellsPlayedThisTurn[self.turn] += 1
					if "~Accelerate" in spell.index:
						self.Counters.numAcceleratePlayedThisGame[self.turn] += 1
						self.Counters.numAcceleratePlayedThisTurn[self.turn] += 1
					if "~Corrupted~" in spell.index: self.Counters.corruptedCardsPlayed[self.turn].append(type(spell))
					#使用后步骤，触发“每当使用一张xx牌之后”的扳机，如狂野炎术士，西风灯神，星界密使的状态移除和伊莱克特拉风潮的状态移除。
					if spell.creator: self.Counters.createdCardsPlayedThisGame[self.turn] += 1
					self.sendSignal("SpellBeenPlayed", self.turn, spell, target, mana, posinHand, choice, armedTrigs)
					if "~Accelerate" in spell.index:
						self.sendSignal("AccelerateBeenPlayed", self.turn, spell, target, mana, posinHand, choice, armedTrigs)
					#完成阶段结束，处理亡语，此时可以处理胜负问题。
				self.gathertheDead(True) #即使随从以法术打出，并被古神在上变成随机施放的法术，也要进行死亡的判定
				if not isinstance(tarLocator, list):
					self.moves.append(("playSpell", subLocator, tarLocator, choice))
				else: self.moves.append(("playSpell", subLocator, tuple(tarLocator), choice))
				self.Counters.shadows[spell.ID] += 1
		else: #Normal or Enhance X or Crystallize X minion played
			typewhenPlayed = minion.category
			minion.seq = len(self.minions[1]) + len(self.minions[2]) + len(self.weapons[1]) + len(self.weapons[2])
			self.minions[minion.ID].insert(position+100*(position < 0), minion)
			self.sortPos()
			if typewhenPlayed == "Minion": self.Counters.numMinionsPlayedThisTurn[self.turn] += 1
			self.minionPlayed = minion
			armedTrigs = self.armedTrigs("%sBeenPlayed"%typewhenPlayed)
			if GUI: GUI.hand2BoardAni(minion)
			target = minion.played(target, choice, mana, posinHand, comment)
			if self.minionPlayed and self.minionPlayed.onBoard:
				self.sendSignal("%sBeenSummoned"%typewhenPlayed, self.turn, self.minionPlayed, target, mana, "")
				if typewhenPlayed == "Minion": self.Counters.numMinionsSummonedThisGame[self.minionPlayed.ID] += 1
			self.Counters.numCardsPlayedThisTurn[self.turn] += 1
			#假设打出的随从被对面控制的话仍然会计为我方使用的随从。被对方变形之后仍记录打出的初始随从
			if self.minionPlayed.category == "Minion": #有时候打出的随从可以变成休眠体，这种情况下不计入打出的牌的序列
				self.Counters.cardsPlayedEachTurn[self.turn][-1].append(type(self.minionPlayed))
				self.Counters.manas4CardsEachTurn[self.turn][-1].append(mana)
				self.Counters.cardsPlayedThisGame[self.turn].append(type(self.minionPlayed))
			if "~Corrupted~" in minion.index: self.Counters.corruptedCardsPlayed[self.turn].append(type(minion))
			if minion.name.endswith("Watch Post"): self.Counters.numWatchPostSummoned[self.turn] += 1
			#使用后步骤，触发镜像实体，狙击，顽石元素等“每当你使用一张xx牌”之后的扳机。
			if self.minionPlayed and self.minionPlayed.category != "Dormant":
				if self.minionPlayed.creator: self.Counters.createdCardsPlayedThisGame[self.turn] += 1
				#The comment here is posinHand, which records the position a card is played from hand. -1 means the rightmost, 0 means the leftmost
				self.sendSignal("%sBeenPlayed"%typewhenPlayed, self.turn, self.minionPlayed, target, mana, posinHand, choice, armedTrigs)
		#............完成阶段结束，开始处理死亡情况，此时可以处理胜负问题。
		self.gathertheDead(True)
		if isinstance(tarLocator, list): self.moves.append(("playMinion", subLocator, tuple(tarLocator), position, choice))
		else: self.moves.append(("playMinion", subLocator, tarLocator, position, choice))
		self.wrapUpPlay(GUI, sendthruServer)
		return True

	#不考虑卡德加带来的召唤数量翻倍。用于被summon引用。
	#returns the single minion summoned. Used for anchoring the position of the original minion summoned during doubling
	#position MUST be a NUMBER. If non-negative, insert; otherwise, append
	def summonSingle(self, subject, position, summoner, source='', changeCreator=True):
		ID = subject.ID
		if self.space(ID) > 0:
			if changeCreator: subject.creator = type(summoner)
			subject.seq = len(self.minions[1]) + len(self.minions[2]) + len(self.weapons[1]) + len(self.weapons[2])
			self.minions[subject.ID].insert(position+100*(position<0), subject)  #If position is too large, the insert() simply puts it at the end.
			self.sortPos()
			self.sortSeq()
			if self.GUI:
				if source == 'H': self.GUI.hand2BoardAni(subject)
				elif source == 'D': self.GUI.deck2BoardAni(subject)
				else: self.GUI.summonAni(subject)
			self.add2EventinGUI(summoner, subject)
			subject.appears()
			self.Counters.numWatchPostSummoned[ID] += 1
			if subject.category=="Minion":
				self.sendSignal("MinionSummoned", self.turn, subject, None, 0, "")
				self.sendSignal("MinionBeenSummoned", self.turn, subject, None, 0, "")
				self.Counters.numMinionsSummonedThisGame[subject.ID] += 1
			elif subject.category=="Amulet":
				self.sendSignal("AmuletSummoned", self.turn, subject, None, 0, "")
			return subject
		return None

	#只能为同一方召唤随从，如有需要，则多次引用这个函数即可。subject不能是空的
	#注意，卡德加的机制是2 ** n倍。每次翻倍会出现多召唤1个，2个，4个的情况。
	#relative只有"<>"（召唤到其右侧）和">"（召唤到其左右两侧）。如果定义了position则优先使用position给出的位置，否则按summoner和relative计算位置
	def summon(self, subject, summoner, relative='>', position=None): #只有召唤多个随从的时候会需要使用position，其需要是一个具体的int
		#如果subject是多个随从，则需要对列表/tuple/数组循环召唤单独的随从
		if not isinstance(subject, (list, tuple, numpy.ndarray)): #Summon a single minion
			pos0 = summoner.pos+1 if position is None else position #除非直接定义了position，否则召唤的首个随从位置由summoner.pos+1决定
			#如果是英雄技能进行的召唤，则不会翻倍。
			if timesofx2 := self.effects[summoner.ID]["Summon x2"] if summoner and summoner.category == "Power" else 0:
				ID, numCopies = subject.ID, 2 ** timesofx2 - 1
				copies = [subject.selfCopy(ID, creator=summoner) for _ in range(numCopies)]
				if minionSummoned := self.summonSingle(subject, pos0, summoner): #只有最初本体召唤成功时才会召唤随从的复制
					if self.summonSingle(copies[0], subject.pos+1, summoner): #复制的第一个随从是紧跟本体随从的右边
						for i in range(1, numCopies): #复制的随从列表中剩余的随从，如果没有剩余随从了，直接跳过
							if not self.summonSingle(copies[i], copies[i-1].pos+1, summoner): break #翻倍出的复制始终在上一个复制随从的右边。
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
	def summonfrom(self, i, ID, position, summoner, source='H'):
		if source == 'H': subject = self.Hand_Deck.extractfromHand(i, ID, getAll=False, enemyCanSee=True, animate=False)[0]
		else: subject = self.Hand_Deck.extractfromDeck(i, ID, getAll=False, enemyCanSee=True, animate=False)[0]
		if timesofx2 := self.effects[summoner.ID]["Summon x2"] if summoner and summoner.category == "Power" else 0:
			ID, numCopies = subject.ID, 2 ** timesofx2 - 1
			copies = [subject.selfCopy(ID, summoner) for _ in range(numCopies)]
			if subject := self.summonSingle(subject, position, summoner=None, source=source, changeCreator=False):
				if self.summonSingle(copies[0], subject.pos+1, summoner):
					for i in range(1, numCopies): #复制的随从列表中剩余的随从，如果没有剩余随从了，直接跳过
						if not self.summonSingle(copies[i], copies[i-1].pos, summoner): break #翻倍出来的复制会始终紧跟在初始随从的右边。
			return subject #只要第一次召唤出随从就视为召唤成功
		else: return self.summonSingle(subject, position, summoner=None, source=source, changeCreator=False)

	def silenceMinions(self, minions):
		prevHealths, ls_AurasReceivers, ls_returnBorrowed = [minion.health for minion in minions], [], []

		for minion in minions:
			minion.silenced = True
			minion.losesTrig(None, allTrigs=True)
			for aura in minion.auras: aura.auraDisappears()
			minion.auras, minion.enchantments = [], []
			ls_AurasReceivers.append([(receiver.source, receiver) for receiver in minion.auraReceivers])
			ls_returnBorrowed.append(minion.effects["Borrowed"] > 0 and minion.onBoard)
			for key in minion.effects: minion.effects[key] = 0
			minion.attack, minion.health_max = minion.attack_0, minion.health_0
		for prevHealth, AurasReceivers, returnBorrowed, minion in zip(prevHealths, ls_AurasReceivers, ls_returnBorrowed, minions):
			if returnBorrowed:
				for aura, receiver in AurasReceivers: removefrom(receiver, aura.receivers)
				self.minionSwitchSide(minion, activity="Return")
			else:
				for aura, receiver in AurasReceivers:
					if aura.on and aura.applicable(minion): receiver.effectBack2List()
					else: removefrom(receiver, aura.receivers)
			
			minion.attack, minion.health_max = minion.attack_0, minion.health_0
			for enchant in minion.enchantments: enchant.handleStatMax(minion)
			for receiver in minion.auraReceivers: receiver.handleStatMax()
			minion.health = min(minion.health_max, prevHealth)
			minion.dmgTaken = minion.health_max - minion.health

			if minion.btn: minion.btn.statChangeAni(num1=-1, num2=-1)
			self.sendSignal("MinionStatCheck", minion.ID, None, minion, 0, "")
			if minion.btn: minion.btn.effectChangeAni()
			minion.decideAttChances_base()

	def kill(self, subject, target):
		if isinstance(target, (list, tuple, numpy.ndarray)):
			if len(target) > 0:
				self.add2EventinGUI(subject, target, textTarget='X', colorTarget=red)
				for obj in target: obj.dead = True
		elif target:
			if self.GUI:
				self.GUI.resetSubTarColor(subject, target)
				if subject == target: self.add2EventinGUI(subject, target, textSubject='X', colorSubject=red)
				else: self.add2EventinGUI(subject, target, textTarget='X', colorTarget=red)
			if target.onBoard: target.dead = True
			elif target.inHand: self.Hand_Deck.discard(target.ID, target)  # 如果随从在手牌中则将其丢弃

	def necromancy(self, subject, ID, number):
		if self.Counters.shadows[ID] >= number:
			self.Counters.shadows[ID] -= number
			self.sendSignal("Necromancy", ID, subject, None, number, "")
			return True
		return False

	#summoner here is a real obj. Either a minion/Dormant on board, or a weapon equipped, or a card in hand
	def transform(self, target, newTarget, firstTime=True, summoner=None):
		ID = target.ID
		if self.minionPlayed == target: self.minionPlayed = newTarget
		if (isMinion := target in self.minions[ID]) or target in self.weapons[target.ID]:
			self.add2EventinGUI(summoner, (target, newTarget))
			newTarget.pos, newTarget.creator = target.pos, type(summoner) if summoner else None
			target.disappears(disappearResponse=False)
			#removeMinionorWeapon invokes sortSeq()
			newTarget.seq = len(self.minions[1]) + len(self.minions[2]) + len(self.weapons[1]) + len(self.weapons[2])
			self.removeMinionorWeapon(target, sortPos=False, animate=False) #No need to resort the pos of minions
			if isMinion: self.minions[ID].insert(newTarget.pos, newTarget)
			else: self.weapons[ID].append(newTarget)
			if self.GUI: self.GUI.transformAni_onBoard(target, newTarget)
			newTarget.appears(firstTime)
			if not isMinion: newTarget.setasNewWeapon()
		elif target in self.Hand_Deck.hands[target.ID]:
			self.Hand_Deck.replaceCardinHand(target, newTarget, creator=type(summoner))
		return newTarget

	#This method is always invoked after the minion.disappears() method.
	def removeMinionorWeapon(self, target, sortPos=True, animate=True):
		target.onBoard, target.pos = False, -2
		zone = self.weapons[target.ID] if target.category == "Weapon" else self.minions[target.ID]
		removefrom(target, zone)
		self.sortSeq()
		if target.category != "Weapon" and sortPos: self.sortPos()
		if self.GUI and animate: self.GUI.removeMinionorWeaponAni(target)

	def banishMinion(self, subject, target):
		if target:
			if isinstance(target, list):
				#if self.GUI and subject: self.GUI.AOEAni(subject, target, ['○']*len(target), color="grey46")
				for obj in target:
					obj.disappears()
					self.removeMinionorWeapon(obj)
			else:
				#if self.GUI and subject: self.GUI.targetingEffectAni(subject, target, '○', color="grey46")
				if target.onBoard:
					target.disappears()
					self.removeMinionorWeapon(target)
				elif target.inHand: self.Hand_Deck.extractfromHand(target.ID, target) #如果随从在手牌中则将其丢弃

	def isVengeance(self, ID):
		return self.heroes[ID].health <= 10 or self.Counters.tempVengeance[ID]

	def isAvarice(self, ID):
		return self.Counters.numCardsDrawnThisTurn[ID] >= 2

	def isWrath(self, ID):
		return self.Counters.timesHeroTookDamage_inOwnTurn[ID] >= 7

	def isResonance(self, ID):
		return len(self.Hand_Deck.decks[ID]) % 2 == 0

	def isOverflow(self, ID):
		return self.Manas.manasUpper[ID] >= 7

	def combCards(self, ID):
		return self.Counters.numCardsPlayedThisTurn[ID]

	def getEvolutionPoint(self, ID):
		point = 0
		if self.powers[ID].name == "Evolve" and self.Counters.turns[ID] >= \
				self.Counters.numEvolutionTurn[ID]:
			point = self.Counters.numEvolutionPoint[ID]
		return point

	def restoreEvolvePoint(self, ID, number=1):
		if self.heroes[ID].heroPower.name == "Evolve":
			self.Counters.numEvolutionPoint[ID] = min(1 + ID, self.Counters.numEvolutionPoint[ID] + number)

	def earthRite(self, subject, ID, number=1):
		earths = self.earthsonBoard(ID)
		if len(earths) >= number:
			for i in range(number):
				self.kill(subject, earths[i])
				self.gathertheDead()
			return True
		return False

	#def reanimate(self, ID, mana):
	#	if self.mode == 0:
	#		t = None
	#		if self.picks:
	#			t = self.cardPool[self.picks.pop(0)]
	#		else:
	#			cards = self.Counters.minionsDiedThisGame[ID]
	#			minions = {}
	#			for card in cards:
	#				try: minions[card.mana].append(card)
	#				except: minions[card.mana] = [card]
	#			for i in range(mana, -1, -1):
	#				if i in minions:
	#					t = numpy.random.choice(minions[i])
	#					break
	#			self.picks_Backup.append(t.index)
	#		if t:
	#			subject = t(self, ID)
	#			self.summon([subject], None)
	#			self.sendSignal("Reanimate", ID, subject, None, mana, "")
	#			return subject
	#	return None

	#The leftmost minion has position 0. Consider Dormant
	def sortPos(self):
		for i, obj in enumerate(self.minions[1]): obj.pos = i
		for i, obj in enumerate(self.minions[2]): obj.pos = i

	#Rearrange all livng minions' sequences if change is true. Otherwise, just return the list of the sequences.
	#需要考虑Dormant的出场顺序
	def sortSeq(self):
		objs = self.weapons[1] + self.weapons[2] + self.minions[1] + self.minions[2]
		for i, obj in zip(numpy.asarray([obj.seq for obj in objs]).argsort().argsort(), objs): obj.seq = i
		
	#Return a single minion to hand
	def returnObj2Hand(self, target, deathrattlesStayArmed=False, manaMod=None):
		ID = target.ID
		if target in self.minions[ID]: #如果随从仍在随从列表中
			if self.Hand_Deck.handNotFull(ID):
				#如果onBoard仍为True，则其仍计为场上存活的随从，需调用disappears以注销各种扳机。
				if target.onBoard: #随从存活状态下触发死亡扳机的区域移动效果时，不会注销其他扳机
					target.disappears(deathrattlesStayArmed)
				#如onBoard为False,则disappears已被调用过了。主要适用于触发死亡扳机中的区域移动效果
				self.removeMinionorWeapon(target, animate=False)
				target.reset(ID)
				self.Hand_Deck.hands[ID].append(target)
				if manaMod: manaMod.applies()
				
				GUI = self.GUI
				if GUI: self.GUI.board2HandAni(target)
				card_Final = target.entersHand()
				self.sendSignal("CardEntersHand", ID, None, [target], 0, "")
				if target != card_Final:
					card_Final.inheritEnchantmentsfrom(target)
					self.Hand_Deck.replaceCardinHand(target, card_Final, target.creator, calcMana=False)
				self.Manas.calcMana_All()
				#for func in target.returnResponse: func()
				return target
			else: #让还在场上的活着的随从返回一个满了的手牌只会让其死亡
				if target.onBoard: target.dead = True
				for func in target.returnResponse: func()
				return None #如果随从这时已死亡，则满手牌下不会有任何事情发生。
		elif target.inDeck: #如果目标阶段已经在牌库中了，将一个基础复制置入其手牌。
			Copy = type(target)(self, ID)
			self.Hand_Deck.addCardtoHand(Copy, ID)
			return Copy
		elif target.inHand: return target
		else: return None #The target is dead and removed already

	#Shuffle a single minion to deck
	#targetDeckID decides the destination. initiatorID is for triggers, such as Trig_AugmentedElekk
	def returnMiniontoDeck(self, target, targetDeckID, initiatorID, deathrattlesStayArmed=False):
		if target in self.minions[target.ID]:
			#如果onBoard仍为True，则其仍计为场上存活的随从，需调用disappears以注销各种扳机
			if target.onBoard: #随从存活状态下触发死亡扳机的区域移动效果时，不会注销其他扳机
				target.disappears(deathrattlesStayArmed)
			#如onBoard为False，则disappears已被调用过了。主要适用于触发死亡扳机中的区域移动效果
			self.removeMinionorWeapon(target)
			target.reset(targetDeckID) #永恒祭司的亡语会备份一套enchantment，在调用该函数之后将初始化过的本体重新增益
			self.Hand_Deck.shuffleintoDeck(target)
			return target
		elif target.inHand: #如果随从已进入手牌，仍会将其强行洗入牌库
			self.Hand_Deck.shuffleintoDeck(self.Hand_Deck.extractfromHand(target)[0])
			return target
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

	#Given a list of targets to sort, return the list that
	#contains the targets in the right order to trigger.
	def objs_SeqSorted(self, targets):
		order = numpy.array([target.seq for target in targets]).argsort()
		return [targets[i] for i in order], order

	#For those that have more complicated pretest requirements, they have their own complicated canTrig/trig
	def armedTrigs(self, sig):
		trigs = []
		for ID in (self.mainPlayerID, 3 - self.mainPlayerID):
			if sig in (ls := self.trigsBoard[ID]): trigs += ls[sig]
			if sig in (ls := self.trigsHand[ID]): trigs += ls[sig]
			if sig in (ls := self.trigsDeck[ID]): trigs += ls[sig]
		return trigs

	#New signal processing can be interpolated during the processing of old signal
	def sendSignal(self, signal, ID, subject, target, number, comment, choice=0, trigPool=None):
		hasResponder = False
		#即使trigPool传入的值是[]，也说明之前进行了扳机预检测，需要进入if的语句中
		if trigPool is not None: #主要用于打出xx牌和随从死亡时/后扳机，它们有预检测机制。
			for trig in trigPool: #扳机只有仍被注册情况下才能触发，但是这个状态可以通过canTrigger来判断，而不必在所有扳机列表中再次检查。
				if trig.canTrig(signal, ID, subject, target, number, comment, choice): #扳机能触发通常需要扳机记录的实体还在场上等。
					hasResponder = True
					trig.trig(signal, ID, subject, target, number, comment, choice)
		else: #向所有注册的扳机请求触发。
			mainPlayerID = self.mainPlayerID #假设主副玩家不会在一次扳机结算之中发生变化。先触发主玩家的各个位置的扳机。
			#Trigger the trigs on main player's side, in the following order board-> hand -> deck.
			for triggerID in [mainPlayerID, 3-mainPlayerID]:
				if signal in self.trigsBoard[triggerID]:
					trigs = [trig for trig in self.trigsBoard[triggerID][signal] if trig.canTrig(signal, ID, subject, target, number, comment, choice)]
					#某个随从死亡导致的队列中，作为场上扳机，救赎拥有最低优先级，其始终在最后结算
					if trigs: hasResponder = True
					#Redemption has been rotated out
					#if signal == "MinionDies" and self.Secrets.sameSecretExists(Redemption, 3-self.turn):
					#	for i in range(len(trigs)):
					#		if type(trigs[i]) == Trig_Redemption:
					#			trigs.append(trigs.pop(i)) #把救赎的扳机移到最后
					#			break
					for trig in trigs: trig.trig(signal, ID, subject, target, number, comment, choice)
				if signal in self.trigsHand[triggerID]:
					trigs = [trig for trig in self.trigsHand[triggerID][signal] if trig.canTrig(signal, ID, subject, target, number, comment, choice)]
					if trigs: hasResponder = True
					for trig in trigs: trig.trig(signal, ID, subject, target, number, comment, choice)
				if signal in self.trigsDeck[triggerID]:
					trigs = [trig for trig in self.trigsDeck[triggerID][signal] if trig.canTrig(signal, ID, subject, target, number, comment, choice)]
					if trigs: hasResponder = True
					invocation = []
					for trig in trigs:
						if "Invocation" in type(trig).__name__:
							if trig.keeper.name not in invocation:
								trig.trig(signal, ID, subject, target, number, comment, choice)
								invocation.append(trig.keeper.name)
						else: trig.trig(signal, ID, subject, target, number, comment, choice)
		return hasResponder

	#Process the damage transfer. If no transfer happens, the original target is returned
	def scapegoat4(self, target, subject=None):
		holder = [target]
		#Each damage trigger only triggers once during a single resolution
		while self.sendSignal("DmgTaker?", 0, subject, holder, 0, ""):
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
		self.scapegoat4(self.heroes[ID]).takesDamage(None, dmg, damageType="Ability")

	#The weapon will also join the deathList and compare its own sequence against other minions.
	def gathertheDead(self, decideWinner=False):
		#Determine what characters are dead. The die() method hasn't been invoked yet.
		#序列内部不包含胜负裁定，即只有回合开始、结束产生的序列；
		#回合开始抽牌产生的序列；打出随从，法术，武器，英雄牌产生的序列；
		#以及战斗和使用英雄技能产生的序列以及包含的所有亡语等结算结束之后，胜负才会被结算。
		for ID in (1, 2):
			#Register the weapons to destroy.(There might be multiple weapons in queue,
			#since you can trigger Tirion Fordring's deathrattle twice and equip two weapons in a row.)
			#Pop all the weapons until no weapon or the latest weapon equipped.
			for weapon in self.weapons[ID]:
				if weapon.health < 1 or weapon.dead:
					weapon.dead = True
					weapon.disappears(deathrattlesStayArmed=True)
					self.Counters.weaponsDestroyedThisGame[ID].append(type(weapon))
					self.tempDeads[0].append(weapon)
					self.tempDeads[1].append(weapon.attack)
				else: #If the weapon is the latest weapon to equip
					break
			for minion in self.minionsonBoard(ID) + self.amuletsonBoard(ID):
				if minion.effects["Can't Break"] > 0: minion.dead = False
				if minion.category == "Minion":
					if minion.health < 1 or minion.dead:
						if minion.effects["Disappear When Die"] > 0:
							self.banishMinion(None, minion)
							continue
						minion.dead = True
						self.tempDeads[0].append(minion)
						self.tempDeads[1].append(minion.attack)
						minion.disappears(deathrattlesStayArmed=True) #随从死亡时不会注销其死亡扳机，这些扳机会在触发之后自行注销
						self.Counters.minionsDiedThisTurn[minion.ID].append(type(minion))
						self.Counters.minionsDiedThisGame[minion.ID].append(type(minion))
						if "Artifact" in minion.race:
							if minion.index in self.Counters.artifactsDiedThisGame[minion.ID]:
								self.Counters.artifactsDiedThisGame[minion.ID][minion.index] += 1
							else: self.Counters.artifactsDiedThisGame[minion.ID][minion.index] = 1
						self.Counters.shadows[minion.ID] += 1
				elif minion.dead: #The obj is Amulet and it's been marked dead
					minion.dead = True
					self.tempDeads[0].append(minion)
					self.tempDeads[1].append(0)
					minion.disappears(deathrattlesStayArmed=True) #随从死亡时不会注销其死亡扳机，这些扳机会在触发之后自行注销
					self.Counters.amuletsDestroyedThisTurn[minion.ID].append(type(minion))
					self.Counters.amuletsDestroyedThisGame[minion.ID].append(type(minion))
					self.Counters.shadows[minion.ID] += 1
			#无论是不在此时结算胜负，都要在英雄的生命值降为0时将其标记为dead
			if self.heroes[ID].health < 1: self.heroes[ID].dead = True

		if self.tempDeads[0]: #self.tempDeads != [[], []]
			#Rearrange the dead minions and their attacks according to their sequences.
			self.tempDeads[0], order = self.objs_SeqSorted(self.tempDeads[0])
			temp = self.tempDeads[1]
			self.tempDeads[1] = []
			for i in range(len(order)):
				self.tempDeads[1].append(temp[order[i]])
			if self.GUI: self.GUI.minionsDieAni(self.tempDeads[0])
			#If there is no current deathrattles queued, start the deathrattle calc process.
			if not self.deads[0]: self.deads = self.tempDeads
			else:
				#If there is deathrattle in queue, simply add new deathrattles to the existing list.
				self.deads[0] += self.tempDeads[0]
				self.deads[1] += self.tempDeads[1]

			#The content stored in self.tempDeads must be released.
			#Clean the temp list to wait for new input.
			self.tempDeads = [[], []]
			
		if not self.resolvingDeath: #如果游戏目前已经处于死亡结算过程中，不会再重复调用deathHandle
			#如果要执行胜负判定或者有要死亡/摧毁的随从/武器，则调用deathHandle
			if decideWinner or self.deads[0]:  #self.deads != [[], []]
				self.deathHandle(decideWinner)

	#大法师施放的闷棍会打断被闷棍的随从的回合结束结算。可以视为提前离场。
	#死亡缠绕实际上只是对一个随从打1，然后如果随从的生命值在1以下，则会触发抽牌。它不涉及强制死亡导致的随从提前离场
	#当一个拥有多个亡语的随从死亡时，多个亡语触发完成之后才会开始结算其他随从死亡的结算。
	#每次gathertheDead找到要死亡的随从之后，会在它们这一轮的死亡事件全部处理之后，才再次收集死者，用于下次死亡处理。
		#复生随从也会在一轮死亡结算之后统一触发。
	#亡语实际上是随从死亡时触发的扳机，例如食腐土狼与亡语野兽的结算是先登场者先触发
	def deathHandle(self, decideWinner=False):
		while True:
			rebornMinions = []
			if not self.deads[0]: break #If no minions are dead, then stop the loop
			armedTrigs_WhenDies = self.armedTrigs("MinionDies") + self.armedTrigs("WeaponDestroys") + self.armedTrigs("AmuletDestroys")
			armedTrigs_AfterDied = self.armedTrigs("MinionDied") + self.armedTrigs("AmuletDestroyed")
			while self.deads != [[], []]:
				self.resolvingDeath = True
				objtoDie, attackwhenDies = self.deads[0][0], self.deads[1][0] #留着这个attackwhenDies是因为随从可能会因为光环的失去而产生攻击力的变化
				#For now, assume Tirion Fordring's deathrattle equipping Ashbringer won't trigger player's weapon's deathrattles right away.
				#weapons with regard to deathrattle triggering is handled the same way as minions.
				#一个亡语随从另附一个亡语时，两个亡语会连续触发，之后才会去结算其他随从的亡语。
				#当死灵机械师与其他 亡语随从一同死亡的时候， 不会让那些亡语触发两次，即死灵机械师、瑞文戴尔需要活着才能有光环
				#场上有憎恶时，憎恶如果死亡，触发的第一次AOE杀死死灵机械师，则第二次亡语照常触发。所以亡语会在第一次触发开始时判定是否会多次触发
				if objtoDie.category == "Minion" and objtoDie.effects["Reborn"] > 0: rebornMinions.append(objtoDie)
				objtoDie.deathResolution(attackwhenDies, armedTrigs_WhenDies, armedTrigs_AfterDied)
				self.removeMinionorWeapon(objtoDie) #结算完一个随从的亡语之后将其移除。
				objtoDie.reset(objtoDie.ID) #亡语结算之后把pos调回-2
				objtoDie.dead = True
				self.deads[0].pop(0)
				self.deads[1].pop(0)
			#当一轮死亡结算结束之后，召唤这次死亡结算中死亡的复生随从
			for rebornMinion in rebornMinions:
				miniontoSummon = type(rebornMinion)(self, rebornMinion.ID)
				miniontoSummon.effects["Reborn"], miniontoSummon.health = 0, 1 #不需要特殊的身材处理，激怒等直接在随从的appears()函数中处理。
				self.summon(miniontoSummon, rebornMinion.pos, rebornMinion)
			#死亡结算每轮结束之后才进行死亡随从的收集，然后进行下一轮的亡语结算。
			self.gathertheDead(decideWinner) #See if the deathrattle results in more death or destruction.
			if self.deads == [[], []]: break #只有没有死亡随从要结算了才会终结

		self.resolvingDeath = False
		#The reborn effect take place after the deathrattles of minions have been triggered.
		if decideWinner: #游戏中选手的死亡状态
			#gameEnds == 0: No one dies; 1: Only Hero1 dies; 2: Only Hero2 dies, 3: Both heroes die
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
	自己和自己玩的情况下，因为没有GUI.sock，所以始终都会endTurn接startTurn
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
		self.sendSignal("TurnEnds", self.turn, None, None, 0, "")
		self.gathertheDead(True)
		#The secrets and temp effects are cleared at the end of turn.
		for obj in self.turnEndTrigger[:]: obj.trig_TurnTrig() #所有一回合光环都是回合结束时消失，即使效果在自己回合外触发了也是如此

		self.Counters.turnEnds()
		self.Manas.turnEnds()
		"""目前没有必要考虑连续进行回合的情况，以后大概不会再出类似的牌"""
		self.turn = 3 - self.turn #Changes the turn to another hero.
		
		#If there is an opponent, they take over the rest, and later return a "startTurn" move
		theresOppo2TakeOver = GUI and GUI.sock
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
		self.numTurn += 1
		self.Counters.turns[self.turn] += 1
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

		self.sendSignal("TurnStarts", self.turn, None, None, 0, "")
		self.gathertheDead(True)
		#抽牌阶段之后的死亡处理可以涉及胜负裁定。
		self.Hand_Deck.drawCard(self.turn)
		if self.turn == 2 and self.Counters.turns[2] == 1 and self.heroes[2].Class in SVClasses:
			self.Hand_Deck.drawCard(self.turn)
		self.gathertheDead(True) #There might be death induced by drawing cards.
		
		#只有在不是自己
		if not finallyWrapUpSwitchTurn: self.moves.append(("startTurn", ))
		#自己和自己玩的时候发送消息与否没有影响，而自己在补完对方的回合结束时需要发送消息
		#自己在回合结束后接收到对方发来的补完消息后，不再把己方的消息再次回传。只有此时fromOppoMove才会是True
		self.wrapUpPlay(GUI, sendthruServer=not finallyWrapUpSwitchTurn, endingTurn=False)
		return True
	
	def battle(self, subject, target, verifySelectable=True, useAttChance=True, resolveDeath=True, resetRedirTrig=True, sendthruServer=True):
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
		GUI = self.GUI
		self.prepGUI4Ani(GUI)
		if GUI:
			GUI.resetSubTarColor(subject, target)
			dy = 0.5 * (1 if GUI.heroZones[subject.ID].heroPos[1] < 0 else -1)
			GUI.offsetNodePath_Wait(subject.btn.np, duration=0.15, dy=dy, dz=5)
			GUI.seqHolder[-1].append(GUI.WAIT(0.3))

		subLocator = tarLocator = 0
		if verifySelectable: subLocator, tarLocator = self.genLocator(subject), self.genLocator(target)
		#如果英雄的武器为蜡烛弓和角斗士的长弓，则优先给予攻击英雄免疫，防止一切攻击前步骤带来的伤害。
		self.sendSignal("BattleStarted", self.turn, subject, target, 0, "") #这里的target没有什么意义，可以留为target
		#在此，奥秘和健忘扳机会在此触发。需要记住初始的目标，然后可能会有诸多扳机可以对此初始信号响应。
		targetHolder = [target, target] #第一个target是每轮要触发的扳机会对应的原始随从，目标重导向扳机会改变第二个
		signal = subject.category + "Attacks" + targetHolder[0].category
		self.sendSignal(signal, self.turn, subject, targetHolder, 0, "1stPre-attack")
		#第一轮攻击前步骤结束之后，Game的记录的target如果相对于初始目标发生了变化，则再来一轮攻击前步骤，直到目标不再改变为止。
		#例如，对手有游荡怪物、误导和毒蛇陷阱，则攻击英雄这个信号可以按扳机入场顺序触发误导和游荡怪物，改变了攻击目标。之后的额外攻击前步骤中毒蛇陷阱才会触发。
		#如果对手有崇高牺牲和自动防御矩阵，那么攻击随从这个信号会将两者都触发，此时攻击目标不会因为这两个奥秘改变。
		#健忘这个特性，如果满足触发条件，且错过了50%几率，之后再次满足条件时也不会再触发这个扳机。这个需要在每个食人魔随从上专门放上标记。
			#如果场上有多个食人魔勇士，则这些扳机都只会在第一次信号发出时触发。
		#如果一个攻击前步骤中，目标连续发生变化，如前面提到的游荡怪物和误导，则只会对最新的目标进行下一次攻击前步骤。
		#如果一个攻击前步骤中，目标连续发生变化，但最终又变回与初始目标相同，则不会产生新的攻击前步骤。
		#在之前的攻击前步骤中触发过的扳机不能再后续的额外攻击前步骤中再次触发，主要作用于傻子和市长，因为其他的攻击前扳机都是奥秘，触发之后即消失。
		#只有在攻击前步骤中可能有攻击目标的改变，之后的信号可以大胆的只传递目标本体，不用targetHolder
		while targetHolder[1] != targetHolder[0]: #这里的target只是refrence传递进来的target，赋值过程不会更改函数外原来的target
			targetHolder[0] = targetHolder[1] #攻击前步骤改变了攻击目标，则再次进行攻击前步骤，与这个新的目标进行比对。
			if GUI: GUI.resetSubTarColor(subject, targetHolder[0])
			signal = subject.category+"Attacks"+targetHolder[0].category #产生新的触发信号。
			self.sendSignal(signal, self.turn, subject, targetHolder, 0, "FollowingPre-attack")
		target = targetHolder[1] #攻击目标改向结束之后，把targetHolder里的第二个值赋给target(用于重导向扳机的那个),这个target不是函数外的target了
		#攻击前步骤结束，开始结算攻击时步骤
		#攻击时步骤：触发“当xx攻击时”的扳机，如真银圣剑，血吼，智慧祝福，血吼，收集者沙库尔等
		signal = subject.category+"Attacking"+target.category
		self.sendSignal(signal, self.turn, subject, target, 0, "")
		#如果此时攻击者，攻击目标或者任意英雄濒死或离场所，则攻击取消，跳过伤害和攻击后步骤。
		battleContinues = True
		#如果目标随从变成了休眠物，则攻击会取消，但是不知道是否会浪费攻击机会。假设会浪费
		if ((subject.category != "Minion" and subject.category != "Hero") or not subject.onBoard or subject.health < 1 or subject.dead) \
			or ((target.category != "Minion" and target.category != "Hero") or not target.onBoard or target.health < 1 or target.dead) \
			or (self.heroes[1].health < 1 or self.heroes[1].dead or self.heroes[2].health < 1 or self.heroes[2].dead):
			battleContinues = False
			if useAttChance: subject.usageCount += 1 #If this attack is canceled, the attack time still increases.
		if battleContinues:
			#伤害步骤，攻击者移除潜行，攻击者对被攻击者造成伤害，被攻击者对攻击者造成伤害。然后结算两者的伤害事件。
			#攻击者和被攻击的血量都减少。但是此时尚不发出伤害判定。先发出攻击完成的信号，可以触发扫荡打击。
			if GUI: GUI.attackAni_HitandReturn(subject, target)
			subject.attacks(target, useAttChance, duetoCardEffects=not verifySelectable)
			#巨型沙虫的获得额外攻击机会的触发在随从死亡之前结算。同理达利乌斯克罗雷的触发也在死亡结算前，但是有隐藏的条件：自己不能处于濒死状态。
			if subject.category == "Hero": self.Counters.heroAtkTimesThisTurn[subject.ID] += 1
			self.sendSignal(subject.category+"Attacked"+target.category, self.turn, subject, target, 0, "")
		elif GUI: GUI.attackAni_Cancel(subject)
		#"Immune while attacking" effect ends, reset attack redirection triggers, like Mogor the Ogre
		if resetRedirTrig: #这个选项目前只有让一个随从连续攻击其他目标时才会选择关闭，不会与角斗士的长弓冲突
			self.sendSignal("BattleFinished", self.turn, subject, None, 0, "")
		#战斗阶段结束，处理亡语，此时可以处理胜负问题。
		if resolveDeath:
			self.gathertheDead(True)
		if verifySelectable: #只有需要验证攻击目标的攻击都是玩家的游戏操作
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
			
		subLocator = self.genLocator(spell)
		if target:
			if isinstance(target, list): tarLocator = [self.genLocator(obj) for obj in target]
			else: tarLocator = self.genLocator(target) #非列表状态的target一定是炉石卡指定的
		else: tarLocator = 0
		GUI = self.GUI
		self.prepGUI4Ani(GUI)
		#支付法力值，结算血色绽放等状态。
		isaSecret2Hide = GUI and spell.race == "Secret" and GUI.sock and spell.ID != GUI.ID and not GUI.showEnemyHand
		spell, mana, posinHand = self.Hand_Deck.extractfromHand(spell, enemyCanSee=not isaSecret2Hide)
		spell, mana = spell.becomeswhenPlayed(choice) #如果随从没有爆能强化等，则无事发生。
		self.Manas.payManaCost(spell, mana)
		#记录游戏事件的发生
		self.eventinGUI(spell, eventType="PlaySpell", target=target, level=0)
		#请求使用法术，如果此时对方场上有法术反制，则取消后续序列。
		#法术反制会阻挡使用时扳机，如伊利丹和任务达人等。但是法力值消耗扳机，如血色绽放，肯瑞托法师会触发，从而失去费用光环
		#被反制掉的法术会消耗“下一张法术减费”光环，但是卡雷苟斯除外（显然其是程序员自己后写的）
		#被反制掉的法术不会触发巨人的减费光环，不会进入你已经打出的法术列表，不计入法力飓风的计数
		#被反制的法术不会被导演们重复施放
		#很特殊的是，连击机制仍然可以通过被反制的法术触发。所以需要一个本回合打出过几张牌的计数器
		#https://www.bilibili.com/video/av51236298?zw
		spellHolder, origSpell = [spell], spell
		self.sendSignal("SpellOKtoCast?", self.turn, spellHolder, None, mana, "")
		if not spellHolder:
			self.Counters.numCardsPlayedThisTurn[self.turn] += 1
		else:
			if origSpell != spellHolder[0]: spellHolder[0].cast()
			else:
				if GUI: GUI.resetSubTarColor(None, target)
				armedTrigs = self.armedTrigs("SpellBeenPlayed")
				self.Counters.cardsPlayedEachTurn[self.turn][-1].append(type(spell))
				self.Counters.manas4CardsEachTurn[self.turn][-1].append(mana)
				self.Counters.cardsPlayedThisGame[self.turn].append(type(spell))
				spell.played(target, choice, mana, posinHand, comment) #choice用于抉择选项，comment用于区分是GUI环境下使用还是AI分叉
				self.Counters.numCardsPlayedThisTurn[self.turn] += 1
				self.Counters.numSpellsPlayedThisTurn[self.turn] += 1
				if "~Corrupted~" in spell.index: self.Counters.corruptedCardsPlayed[self.turn].append(type(spell))
				#使用后步骤，触发“每当使用一张xx牌之后”的扳机，如狂野炎术士，西风灯神，星界密使的状态移除和伊莱克特拉风潮的状态移除。
				if spell.creator: self.Counters.createdCardsPlayedThisGame[self.turn] += 1
				self.sendSignal("SpellBeenPlayed", self.turn, spell, target, mana, posinHand, choice, armedTrigs)
				#完成阶段结束，处理亡语，此时可以处理胜负问题。
			self.gathertheDead(True) #即使法术可以被古神在上变为随机施放的法术，也要进行死亡判定
			if isinstance(tarLocator, list): self.moves.append(("playSpell", subLocator, tuple(tarLocator), choice))
			else: self.moves.append(("playSpell", subLocator, tarLocator, choice))
			self.Counters.shadows[spell.ID] += 1
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
			GUI.showOffBoardTrig(weapon, animationType='')
			self.eventinGUI(weapon, eventType="PlayWeapon", target=target, level=0)
		#使用阶段，结算阶段。
		armedTrigs = self.armedTrigs("WeaponBeenPlayed")
		#武器进场
		self.weapons[ID].append(weapon)
		if GUI: GUI.weaponPlayedAni(weapon)
		weapon.played(target, 0, mana, posinHand, comment="") #There are no weapon with Choose One.
		self.Counters.numCardsPlayedThisTurn[ID] += 1
		self.Counters.cardsPlayedEachTurn[ID][-1].append(type(weapon))
		self.Counters.manas4CardsEachTurn[ID][-1].append(mana)
		self.Counters.cardsPlayedThisGame[ID].append(type(weapon))
		#if "~Corrupted~" in weaponIndex: self.Counters.corruptedCardsPlayed[self.turn].append(weaponIndex)
		#完成阶段，触发“每当你使用一张xx牌”的扳机，如捕鼠陷阱和瑟拉金之种等。
		if weapon.creator: self.Counters.createdCardsPlayedThisGame[ID] += 1
		self.sendSignal("WeaponBeenPlayed", self.turn, weapon, target, mana, posinHand, 0, armedTrigs)
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
	
	def playHero(self, heroCard, target=None, choice=0, sendthruServer=True):
		ID = heroCard.ID
		if not self.check_playHero(heroCard, target, choice):
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
		subLocator = self.genLocator(heroCard)
		#准备游戏操作的动画
		GUI = self.GUI
		self.prepGUI4Ani(GUI)

		self.eventinGUI(heroCard, eventType="PlayHero", target=target, level=0) #从手牌中打出英雄牌的时候显示为整卡
		#支付费用，以及费用状态移除
		heroCard, mana, posinHand = self.Hand_Deck.extractfromHand(heroCard, enemyCanSee=True)
		self.Manas.payManaCost(heroCard, mana)
		#使用阶段，结算阶段的处理。
		armedTrigs = self.armedTrigs("HeroCardBeenPlayed")
		heroCard.played(None, choice, mana, posinHand, comment="")
		self.Counters.numCardsPlayedThisTurn[ID] += 1
		self.Counters.cardsPlayedEachTurn[ID][-1].append(type(heroCard))
		self.Counters.manas4CardsEachTurn[ID][-1].append(mana)
		self.Counters.cardsPlayedThisGame[ID].append(type(heroCard))
		#完成阶段
		#使用后步骤，触发“每当你使用一张xx牌之后”的扳机，如捕鼠陷阱等。
		if heroCard.creator: self.Counters.createdCardsPlayedThisGame[self.turn] += 1
		self.sendSignal("HeroCardBeenPlayed", self.turn, heroCard, None, mana, posinHand, choice, armedTrigs)
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
		if self.effects[ID]["Trade Discovers Instead"] > 0:
			AuctioneerJaxon(self, ID).discoverfromCardList(AuctioneerJaxon, '')
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
			GUI.UI = -2 #需要调成无响应状态
			GUI.seqHolder[-1].append(GUI.FUNC(GUI.setMsg, "Player %d Conceded!"%ID))
		self.moves.append(("concede", ID, 'Hero%d'%ID, 0, ""))
		self.wrapUpPlay(GUI, sendthruServer)
		self.UI = -2
		return True
	
	def createCopy(self, game):
		return game

	def copyGame(self, num=1):
		#start = datetime.now()
		copies = [Game(None, self.boardID) for _ in range(num)]
		for Copy in copies:
			Copy.copiedObjs = {}
			Copy.mainPlayerID, Copy.GUI = self.mainPlayerID, None
			Copy.RNGPools = self.RNGPools
			#t1 = datetime.now()
			Copy.heroes = {1: self.heroes[1].createCopy(Copy), 2: self.heroes[2].createCopy(Copy)}
			Copy.powers = {1: self.powers[1].createCopy(Copy), 2: self.powers[2].createCopy(Copy)}
			Copy.weapons = {1: [weapon.createCopy(Copy) for weapon in self.weapons[1]], 2: [weapon.createCopy(Copy) for weapon in self.weapons[2]]}
			Copy.Hand_Deck = self.Hand_Deck.createCopy(Copy)
			Copy.minions = {1: [minion.createCopy(Copy) for minion in self.minions[1]],
							2: [minion.createCopy(Copy) for minion in self.minions[2]]}
			#t2 = datetime.now()
			#print("Time to copy characters onBoard", datetime.timestamp(t2)-datetime.timestamp(t1))
			#t1 = datetime.now()
			Copy.trigAuras = {ID: [aura.createCopy(Copy) for aura in self.trigAuras[ID]] for ID in (1, 2)}
			Copy.mulligans, Copy.options, Copy.tempDeads, Copy.deads = {1:[], 2:[]}, [], [[], []], [[], []]
			Copy.Counters, Copy.Manas = self.Counters.createCopy(Copy), self.Manas.createCopy(Copy)
			Copy.minionPlayed, Copy.gameEnds, Copy.turn, Copy.numTurn = None, self.gameEnds, self.turn, self.numTurn
			Copy.resolvingDeath = False
			Copy.effects = copy.copy(self.effects)
			Copy.players = self.players
			Copy.Discover = self.Discover.createCopy(Copy)
			Copy.Secrets = self.Secrets.createCopy(Copy)
			#t2 = datetime.now()
			#print("Time to copy various Handlers", datetime.timestamp(t2)-datetime.timestamp(t1))
			#t1 = datetime.now()
			#t2 = datetime.now()
			#print("Time to copy Hands/Decks", datetime.timestamp(t2)-datetime.timestamp(t1))
			#t1 = datetime.now()
			Copy.trigsBoard, Copy.trigsHand, Copy.trigsDeck = {1:{}, 2:{}}, {1:{}, 2:{}}, {1:{}, 2:{}}
			for trigs1, trigs2 in zip([Copy.trigsBoard, Copy.trigsHand, Copy.trigsDeck], [self.trigsBoard, self.trigsHand, self.trigsDeck]):
				for ID in (1, 2):
					for sig in trigs2[ID].keys(): trigs1[ID][sig] = [trig.createCopy(Copy) for trig in trigs2[ID][sig]]
			Copy.turnStartTrigger, Copy.turnEndTrigger = [trig.createCopy(Copy) for trig in self.turnStartTrigger], [trig.createCopy(Copy) for trig in self.turnEndTrigger]
			#t2 = datetime.now()
			#print("Time to copy triggers", datetime.timestamp(t2)-datetime.timestamp(t1))
			Copy.mode = self.mode
			Copy.moves, Copy.picks = copy.deepcopy(self.moves), copy.deepcopy(self.picks)
			del Copy.copiedObjs

		#finish = datetime.now()
		#print("Total time for copying %d games"%num, datetime.timestamp(finish)-datetime.timestamp(start))
		return copies

	def genLocator(self, card=None):
		if not card: return 0
		ID = card.ID
		if card.onBoard:
			if card.category in ("Minion", "Dormant", "Amulet"): #X0Y: The Xth in minions[Y]
				return card.pos * 100 + ID
			elif card.category == "Hero": #001Y: Hero Y
				return 10 + ID
			else: return 20 + ID #002Y: Power of player Y
		elif card.inHand: #X3Y: The Xth in self.Game.Hand_Deck.hands[Y]
			return self.Hand_Deck.hands[ID].index(card) * 100 + 30 + ID
		elif card.inDeck:
			return self.Hand_Deck.decks[ID].index(card) * 100 + 40 + ID
		else: raise

	#Find the card in the game using integert locator
	#Board: 0, Hero: 1, Power:2, Hand:3, Deck:4
	#2241: ID=1, Deck, index=22 --->self.Game.Hand_Deck.decks[1][22]
	#0002: ID=2, Board, index=0 -->self.Game.minions[2][0]
	def locate(self, locator): #ID last digit, zone 2nd last digit
		if not locator: return None
		ID, zone, i = locator % 10, int(locator % 100 / 10), int(locator / 100)
		if zone == 0: return self.minions[ID][i]
		elif zone == 1: return self.heroes[ID]
		elif zone == 2: return self.powers[ID]
		elif zone == 3: return self.Hand_Deck.hands[ID][i]
		elif zone == 4: return self.Hand_Deck.decks[ID][i]
		else: raise

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
			playCorrect = {"battle": lambda: self.battle(sub, tar, sendthruServer=False),
							"Power": lambda: sub.use(tar, move[3], sendthruServer=False),
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