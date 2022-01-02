from Parts.ConstsFuncsImports import *
from Parts.TrigsAuras import ManaMod

#一个Enchantment中不能同时定义身材变化和效果变化。类型有buffDebuff/statReset/effectGain
#source记录的是什么样的卡牌效果给予了这个Enchantment
class Enchantment:
	def __init__(self, source, attGain=0, healthGain=0, attSet=None, healthSet=None, effGain='', effNum=1,
				 until=-1):
		if not source or not issubclass(source, Card):
			print("Enchantment doesn't have valid source", source)
			raise ValueError
		self.source = source
		self.attGain, self.healthGain = attGain, healthGain
		self.attSet, self.healthSet = attSet, healthSet
		self.effGain, self.effNum = effGain, effNum
		self.until = until # -1是持续效果, 0是直到本回合结束, 1/2 (3/4)是直到玩家1/2的回合开始(结束)。目前没有跨数个回合的enchantment

	def addto(self, keeper): keeper.enchantments.append(self)

	def text(self):
		s = self.source.name_CN + '\n'
		if self.effGain: s += self.effGain + ' ' + str(self.effNum)
		else:
			if a := self.attGain: s += ('+%d'%a if a > 0 else str(a))
			if a := self.attSet is not None: s += "=>%d"%a
			s += '/'
			if a := self.healthGain: s += ('+%d'%a if a > 0 else str(a))
			if a := self.healthSet is not None: s += "=>%d"%a
		return s

	#只负责处理身材数值的上限，对于随从的实际当前生命值不做处理
	#healthGain都是正值，以目前的结算机制不可能有负值
	def handleStatMax(self, keeper):
		keeper.attack += self.attGain
		keeper.health_max += self.healthGain
		if self.attSet is not None: keeper.attack = self.attSet
		if self.healthSet is not None: keeper.health_max = self.healthSet
		keeper.health_max = max(0, keeper.health_max)

	def handleEffect(self, keeper): #只有在随从复制时使用
		if self.effGain: keeper.effects[self.effGain] += self.effNum

	#如果Enchantment要失效了，则需要它自行
	def handleExpiring(self, keeper):
		if self.effGain: keeper.losesEffect(self.effGain, self.effNum)

	def selfCopy(self, recipient):
		return type(self)(self.source, self.attGain, self.healthGain, self.attSet, self.healthSet, self.effGain, self.effNum, self.until)

class Enchantment_Exclusive(Enchantment): #
	def addto(self, keeper):
		if enchant := next((enchant for enchant in keeper.enchantments \
							if enchant.source is self.source and enchant.effGain == self.effGain), None):
			enchant.attGain += self.attGain
			enchant.healthGain += self.healthGain
			enchant.effNum = self.effNum
		else: keeper.enchantments.append(self)


effectsDict = {"Taunt": "嘲讽", "Divine Shield": "圣盾", "Stealth": "潜行",
				"Lifesteal": "吸血", "Spell Damage": "法术伤害", "Poisonous": "剧毒",
				"Windfury": "风怒", "Mega Windfury": "超级风怒", "Charge": "冲锋", "Rush": "突袭",
				"Echo": "回响", "Reborn": "复生", "Bane": "毁灭", "Drain": "虹吸",

				"Cost Health Instead": "消耗生命值，而非法力值",
				"Sweep": "对攻击目标的相邻随从造成同样伤害",
				"Evasive": "无法成为法术或英雄技能的目标", "Enemy Evasive": "只有成为你的法术或英雄技能的目标",
				"Can't Attack": "无法攻击", "Can't Attack Hero": "无法攻击英雄",
				"Heal x2": "你的治疗效果翻倍",  # Crystalsmith Kangor
				"Power Heal&Dmg x2": "你的英雄技能的治疗或伤害翻倍",  # Prophet Velen, Clockwork Automation
				"Spell Heal&Dmg x2": "你的法术的治疗或伤害翻倍",
				"Enemy Effect Evasive": "敌方的能力无法指定此卡牌", "Enemy Effect Damage Immune": "因能力所受到的伤害皆转变为0",
				"Can't Break": "无法被能力破坏", "Can't Disappear": "无法被能力消失", "Can't Be Attacked": "无法对这个随从进行攻击", "Disappear When Die": "离场时消失",
				"Next Damage 0": "下一次受到的伤害转变为0", "Ignore Taunt": "可无视守护效果进行攻击", "Can't Evolve": "无法使用进化点进化", "Free Evolve": "不消费进化点即可进化",
				"Can Attack 3 times" : "一回合中可以进行3次攻击",

				"Immune": "免疫", "Frozen": "被冻结", "Temp Stealth": "潜行直到你的下个回合开始", "Borrowed": "被暂时控制",
				"Evolved": "已进化",
				}

class Card:
	Class = name = index = description = name_CN = ''
	category = race = school = Effects = ''
	mana = attack = health = durability = armor = 0
	numTargets = cardID = 0
	aura = trigBoard = trigHand = trigDeck = deathrattle = trigEffect = None
	options, overload = (), 0
	info1 = info2 = None
	def __init__(self, Game, ID):
		cardType = type(self)
		self.Game, self.ID = Game, ID
		self.Class, self.name, self.category = cardType.Class, cardType.name, cardType.category
		self.school, self.race, self.index = cardType.school, cardType.race, cardType.index
		self.options = [option(self) for option in cardType.options]

		self.effects = {}
		self.onBoard = self.inHand = self.inDeck = self.dead = self.silenced = False
		self.enterBoardTurn = self.enterHandTurn = 0
		self.seq, self.pos = -1, -2
		self.usageCount, self.attChances_base, self.attChances_extra = 0, 1, 0
		self.progress = 0

		self.mana_0 = self.mana = cardType.mana
		self.info1, self.info2 = cardType.info1, cardType.info2
		self.attack_0 = self.attack = cardType.attack
		self.health_0 = self.health = self.health_max = (cardType.health if cardType.health > 0 else cardType.durability)
		self.armor, self.dmgTaken = cardType.armor, 0 #Real health is health_max-dmgTaken
		#会改变dmgTaken的过程只有takesDamage, getsHealed, statReset, losesDurability, getsSilenced, replaceHero
		#会调用dmgTaken的过程只有calcStat, selfCopy, createCopy

		#目前只有随从有光环，只有随从和武器有亡语
		self.auras, self.auraReceivers, self.manaMods, self.deathrattles, self.enchantments = [], [], [], [], []
		self.trigsBoard = [cardType.trigBoard(self)] if cardType.trigBoard else []
		self.trigsHand = [cardType.trigHand(self)] if cardType.trigHand else []
		self.trigsDeck = [cardType.trigDeck(self)] if cardType.trigDeck else []

		self.effectViable = self.evanescent = False
		self.btn = self.creator = None

	# 如果一个随从被返回手牌或者死亡然后进入墓地，其上面的身材改变(buff/statReset)会被消除，但是保留其白字变化
	def reset(self, ID):
		btn, creator = self.btn, self.creator
		mana_0, att_0, health_0 = self.mana_0, self.attack_0, self.health_0
		info1, info2 = self.info1, self.info2
		self.__init__(self.Game, ID)
		self.mana_0, self.attack_0, self.health_0 = mana_0, att_0, health_0
		self.info1, self.info2 = info1, info2
		self.btn, self.creator = btn, creator

	def setEffects_fromStr(self):
		for key in self.Effects.split(","):
			if '_' in key:
				keyWord, s = key.strip().split('_')
				self.effects[keyWord] = int(s)
			else: self.effects[key.strip()] = 1

	def getBareInfo(self):
		s = ''
		for key, value in self.effects.items():
			if value > 1: s += "%s_%d," % (key, value)
			elif value == 1: s += "%s," % key
		return type(self), (self.mana_0, self.attack_0, self.health_0, self.info1, self.info2, s)

	def getMana(self): return self.mana
	def becomeswhenPlayed(self, choice=0): return self, self.mana
	def categorywhenPlayed(self): return self.category #SV minions might change category when played
	def willAccelerate(self): return False
	def selfManaChange(self): pass
	def effCanTrig(self): pass #For cards that have special activation condition
	def checkEvanescent(self): self.evanescent = any(type(trig).changesCard for trig in self.trigsBoard + self.trigsHand)
	def text(self): return ''
	def pickRandomChoice(self):
		if (numOptions := len(self.options)) < 1: return 0
		else: return -1 if self.Game.rules[self.ID]["Choose Both"] > 0 else numpyRandint(numOptions)

	#处理卡牌进入/离开 手牌/牌库时的扳机和各个onBoard/inHand/inDeck标签
	def entersHand(self, isGameEvent=True):
		self.inHand = True
		self.onBoard = self.inDeck = False
		self.enterHandTurn = self.Game.turnInd
		for trig in self.trigsHand: trig.connect()
		self.calcStat()
		if isGameEvent: self.Game.Counters.handleGameEvent("AddCard2Hand", type(self), self.ID)
		return self

	def leavesHand(self, intoDeck=False):
		#将注册了的场上、手牌和牌库扳机全部注销。
		for trig in self.trigsBoard[:]:
			trig.disconnect() #特殊的扳机，如手牌变形，被回合结束弃牌等扳机的disconnect需要自己把自己从列表中摘掉
		for trig in self.trigsHand[:]:
			trig.disconnect()
		self.onBoard = self.inHand = self.inDeck = False
		#离开手牌时把因为光环产生的费用效果清除。固定的费用效果在交易之外的方法洗入牌库或者随从/武器/英雄入场时会清空
		for i in range(len(self.manaMods)-1, -1, -1):
			if (manaMod := self.manaMods[i]).source: manaMod.getsRemoved()

	def entersDeck(self):
		self.inDeck = True
		self.onBoard = self.inHand = False
		self.Game.Manas.calcMana_Single(self)
		for trig in self.trigsDeck: trig.connect()
		return self

	def leavesDeck(self):
		for trig in self.trigsDeck[:]: trig.disconnect() #没有赋予卡牌牌库扳机的效果
		self.onBoard = self.inHand = self.inDeck = False

	def whenDrawn(self): pass
	def whenDiscarded(self): pass
	#def returnResponse(self): For SV cards

	def turnStarts(self, turn2Start): #处理卡牌上携带的直到某方回合开始时的附魔效果
		for enchant in self.enchantments:
			if enchant.until == turn2Start: enchant.handleExpiring(self)
		self.enchantments = [enchant for enchant in self.enchantments if enchant.until != turn2Start]

	def turnEnds(self, turn2End): #处理卡牌上携带的直到某方回合结束时的费用效果和附魔效果
		for manaMod in self.manaMods[:]: manaMod.turnEnds(turn2End) #存在部分费用效果只持续一个回合，如亚煞极拿到的被腐蚀的卡牌
		for enchant in self.enchantments:  # 直到回合结束的对攻击力改变效果不论是否是该随从的当前回合，都会消失
			# -1 is permanent, 0 is until the end of turn, 1/2 (3/4) is until start (end) of player 1/2's turn
			if not enchant.until or enchant.until - 2 == turn2End: enchant.handleExpiring(self)
		self.enchantments = [enchant for enchant in self.enchantments if enchant.until and enchant.until != turn2End]

	"""Handle the effect target selection"""
	def available(self): return True
	#检测目标是否正确。target必须是iterable，同时所有包含在其中的obj必须是场上的角色。
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category in ("Minion", "Hero") and obj.onBoard and obj is not self

	#检测目标是否可以被卡牌效果取对象。如果选择了场上的卡牌，则其必须是英雄/随从/护符
	def canSelect(self, obj):
		if obj.onBoard and (category := obj.category) in ("Hero", "Minion", "Amulet"):
			effects, fromPowerSpell = obj.effects, self.category in ("Power", "Spell")
			if category == "Minion":# 休眠中的随从是无法被选取的。休眠的随从的category会被 更改为"Dormant"
				# 如果目标随从是敌方的，且目前拥有免疫，潜行或者临时潜行，则无法进行选择
				# 如果subject是法术或者英雄技能，且目标随从有魔免，或者是一个有“对对方魔免”的对方随从，则无法进行选择
				if (fromPowerSpell and (effects["Evasive"] > 0 or (obj.ID != self.ID and effects["Enemy Evasive"] > 0))) or \
						(obj.ID != self.ID and effects["Immune"] + effects["Stealth"] + effects["Temp Stealth"] + effects["Enemy Effect Evasive"] > 0):
					return False
			elif category == "Hero":
				rules = self.Game.rules[obj.ID]
				# 如果subject是法术或者英雄技能，则如果英雄有魔免，或者对方英雄有对对方的魔免，则无法进行选择
				#如果英雄是敌方英雄且目前有潜行，免疫，且“不可被敌方效果指定”，则无论什么指向性效果都无法进行选择
				if (fromPowerSpell and rules["Evasive"]) or (obj.ID != self.ID and rules["Immune"] + effects["Temp Stealth"] + effects["Enemy Effect Evasive"] > 0):
					return False
			elif category == "Amulet": #只有护符既不敌方效果魔免，也不是对敌方法术魔免时，才算作是可选
				if (obj.ID != self.ID and effects["Enemy Effect Evasive"] > 0) or (fromPowerSpell and effects["Evasive"] > 0):
					return False
		return True

	#如果打出效果只需要取单目标时，则只需判断场上是否有可以被选择的角色。目标是多选的情况下需要写自己的targetExists方法。
	def selectableMinionExists(self, ID=0, choice=0, ith=0): #canSelect can take in both single card object and iterable
		it = (ID,) if ID else (1, 2)
		return any(obj.category == "Minion" and obj.onBoard and self.canSelect(obj) and self.targetCorrect(obj, choice, ith) for ID in it for obj in self.Game.minions[ID])

	def selectableAmuletExists(self, ID=0, choice=0, ith=0):
		it = (ID,) if ID else (1, 2)
		return any(obj.category == "Amulet" and obj.onBoard and self.canSelect(obj) and self.targetCorrect(obj, choice, ith) for ID in it for obj in self.Game.minions[ID])

	def selectableCharExists(self, ID=0, choice=0, ith=0):
		it = (ID,) if ID else (1, 2)
		if any(self.canSelect(hero := self.Game.heroes[ID]) and self.targetCorrect(hero, choice, ith) for ID in it):
			return True
		else: return any(obj.category == "Minion" and obj.onBoard and self.canSelect(obj) and self.targetCorrect(obj, choice, ith) for ID in it for obj in self.Game.minions[ID])

	#只用于战吼等非法术/英雄技能的效果。法术的合法目标是否存在判定由available处理
	def numTargetsNeeded(self, choice=0): return self.numTargets
	def targetExists(self, choice=0, ith=0): return True #如果没有选择目标的限制一般随从从手牌中的打出效果总是可以选择己方英雄
	def effectNeedsAllTargets(self, choice=0): return True
	def canFindTargetsNeeded(self, choice=0):
		target = []
		for ith in range(self.numTargetsNeeded(choice)):
			if allTargets := self.findTargets(choice, ith, exclude=target):
				target.append(allTargets[0])
			elif self.effectNeedsAllTargets(): return False
			else: target.append(None)
		return any(target)

	# 所有打出效果的目标寻找，包括战吼，法术等。需要可以选择多个目标。返回多层列表
	def findTargets(self, choice=0, ith=0, exclude=()):
		return [obj for obj in self.Game.charsonBoard() if obj not in exclude and self.targetCorrect(obj, choice, ith) and self.canSelect(obj)]

	def randomTargets(self, numTargetsNeeded, preSelected=(), choice=0, prefered=None):
		target = preSelected if preSelected else []
		for ith in range(len(target), numTargetsNeeded):  # 目前的多目标选择不能有重复。
			if allTargets := self.findTargets(choice, ith, exclude=target):
				if prefered and (objs := [obj for obj in allTargets if prefered(obj)]):
					target.append(numpyChoice(objs))
				else: target.append(numpyChoice(allTargets))
			elif self.effectNeedsAllTargets(choice):  # 没有合法目标时且效果需要所有目标才能结算的话，则直接停止并把target清空
				target = ()
				break
			else: target.append(None)  # 没有合法目标，但是效果不需要所有目标都被选择，则直接添加一个None。由后续效果处理时进行分析
		if not any(target): target = ()  # 如果所有目标都是None，则还是清空target
		return target

	def selectionLegit(self, target, choice=0): #target可以是单个卡牌object或者list
		#抉择牌在有全选光环时，选项自动更正为一个负数。
		if self.Game.rules[self.ID]["Choose Both"] > 0 and self.options: choice = -1
		if target: #如果指定了目标，则需要选定的目标数与效果需要的目标数一致，且选定的目标不能全部是None，同时所有目标要么是None，要么是可选的正确目标
			return len(target) == self.numTargetsNeeded(choice) and any(target) \
				   		and all(obj is None or (self.canSelect(obj) and self.targetCorrect(obj, choice, i)) for i, obj in enumerate(target))
		else: #如果没有指定目标，则需要卡牌要么不需要目标，要么是指向性效果的武器/随从/护符，且它们没有合法目标。
			return self.numTargetsNeeded(choice) < 1 or (self.category in ("Minion", "Amulet", "Weapon") and not self.canFindTargetsNeeded(choice))

	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		pass

	def countSpellDamage(self): #Counting spell damage is independent of card category
		return self.Game.rules[self.ID]["Spell Damage"] + (self.school == "Fire" and self.Game.rules[self.ID]["Fire Spell Damage"])\
				+ sum(obj.effects["Spell Damage"] or (self.school == "Nature" and obj.effects["Nature Spell Damage"])
					  for obj in self.Game.minions[self.ID])

	"""Handle the battle options for minions and heroes."""
	def canAttack(self): return False
	def canAttackTarget(self, target): return False
	def aliveonBoard(self): return self.category in ("Hero", "Minion") and self.onBoard and self.health > 0 and not self.dead
	def canBattle(self, mustbeAlive=True): return self.category in ("Minion", "Hero") and self.onBoard and (not mustbeAlive or (self.health > 0 and not self.dead))
	def findBattleTargets(self): return [char for char in self.Game.charsonBoard(3-self.ID) if self.canAttackTarget(char)] if self.canAttack() else []
	def notHiddenfromAttack(self):  # 效果选取时因为没有嘲讽的存在，所以不用重复检测其他角色的可选择性。
		if self.category == "Minion":
			return self.effects["Temp Stealth"] + self.effects["Immune"] + self.effects["Stealth"] + self.effects["Can't Be Attacked"] < 1
		elif self.category == "Hero":
			return self.Game.rules[self.ID]["Immune"] + self.Game.rules[self.ID]["Hero Can't Be Attacked"] < 1
		return False

	def decideAttChances_base(self):
		if self.category == "Minion":
			if self.effects["Mega Windfury"] > 0: self.attChances_base = 4
			elif self.effects["Can Attack 3 times"] > 0: self.attChances_base = 3
			elif self.effects["Windfury"] > 0: self.attChances_base = 2
			else: self.attChances_base = 1
			if self.btn: self.btn.effectChangeAni("Exhausted")
		elif self.category == "Hero":
			self.attChances_base = 2 if self.effects["Windfury"] > 0 or ((weapon := self.Game.availableWeapon(self.ID)) and weapon.effects["Windfury"] > 0) else 1

	def actionable(self): # 不考虑冻结、零攻和自身有不能攻击的debuff的情况。
		if self.category == "Minion": # 判定随从是否处于刚在我方场上登场，以及暂时控制、冲锋、突袭等。
			return self.onBoard and self.ID == self.Game.turn \
				   and (self.enterBoardTurn < self.Game.turnInd or (self.effects["Borrowed"] > 0 or self.effects["Charge"] > 0 or self.effects["Rush"] > 0))
		elif self.category == "Hero": return self.ID == self.Game.turn
		return False

	#Game.battle() invokes this function.
	#我方有扫荡打击的狂暴者攻击对方相邻的两个狂暴者之一，然后扫荡打击在所有受伤开始之前触发，
	#然后被攻击的那个狂暴者先受伤加攻，然后我方的狂暴者受伤加攻，最后是被AOE波及的那个狂暴者加攻。
	#说明扫荡打击是把相邻的随从列入伤害处理列表 ，主要涉及的两个随从是最先结算的两个，
	#被扫荡打击涉及的两个随从从左到右依次结算。
	def landsAtk(self, target, useAttChance=True, duetoCardEffects=False):
		game = self.Game
		subjectAtt, targetAtt = [max(0, self.attack)], [max(0, target.attack)]
		self.losesEffect("Stealth", 0, removeEnchant=True)
		self.losesEffect("Temp Stealth", 0, removeEnchant=True)
		if useAttChance: self.usageCount += 1

		dmgList = []
		#如果攻击者是英雄且装备着当前回合打开着的武器，则将攻击的伤害来源视为那把武器。
		weapon = game.availableWeapon(self.ID)
		dmgDealer_att = weapon if self.category == "Hero" and weapon and self.ID == game.turn else self
		#如果被攻击者是英雄，且装备着当前回合打开着的武器，则将攻击目标造成的伤害来源视为那把武器。
		weapon = game.availableWeapon(target.ID)
		dmgDealer_def = weapon if target.category == "Hero" and weapon and target.ID == game.turn else target
		# Manipulate the health of the subject/target's health.
		#Only send out "MinionTakesDmg" signal at this point.
		#首先结算攻击者对于攻击目标的伤害，如果攻击力小于1，则攻击目标不会被记入伤害处理列表。
		#注意这个伤害承受目标不一定是攻击目标，因为有博尔夫碎盾以及钳嘴龟持盾者的存在
		#承受伤害者的血量减少，结算剧毒，但是此时不会发出受伤信号。
		dmgTaker = game.scapegoat4(target, dmgDealer_att)
		game.sendSignal("BattleDmg" + target.category, 0, dmgDealer_att, target, subjectAtt) #不能把这个东西写入和伤害承受目标判定同时进行的结算，因为存在互相干扰的情况
		if dmgActual := dmgTaker.takesDamage(dmgDealer_att, subjectAtt[0], "Battle"):
			dmgList.append((dmgDealer_att, dmgTaker, dmgActual))

		#寻找受到攻击目标的伤害的角色。同理，此时受伤的角色不会发出受伤信号，这些受伤信号会在之后统一发出。
		dmgTaker = game.scapegoat4(self, dmgDealer_def)
		game.sendSignal("BattleDmg" + target.category, 0, target, dmgDealer_def, targetAtt) #不能把这个东西写入和伤害承受目标判定同时进行的结算，因为存在互相干扰的情况
		if dmgActual := dmgTaker.takesDamage(dmgDealer_def, targetAtt[0], "Battle"):
			dmgList.append((dmgDealer_def, dmgTaker, dmgActual))
		dmg_byDef = dmgActual #The damage dealt by the character under attack
		#如果攻击者的伤害来源（随从或者武器）有对相邻随从也造成伤害的扳机，则将相邻的随从录入处理列表。
		neighbors = []
		if dmgDealer_att.category != "Hero" and dmgDealer_att.effects["Sweep"] > 0 and target.category == "Minion":
			neighbors = game.neighbors2(target)[0]
			for minion in neighbors:
				dmgTaker = game.scapegoat4(minion, dmgDealer_att)
				#目前假设横扫时造成的战斗伤害都一样，不会改变。毕竟炉石里面没有相似的效果
				if dmgActual := dmgTaker.takesDamage(dmgDealer_att, subjectAtt[0], "Ability"):
					dmgList.append((dmgDealer_att, dmgTaker, dmgActual))

		if game.GUI:
			sSubject, sTarget = "-%d"%targetAtt[0] if targetAtt[0] else '', "-%d"%subjectAtt[0] if subjectAtt[0] else ''
			game.eventinGUI(self, eventType="Battle", target=[target]+neighbors, textSubject=sSubject, colorSubject=red,
							textTarget=[sTarget]*(1+len(neighbors)), colorTarget=red, level=1 if duetoCardEffects else 0)

		if dmgDealer_att.category == "Weapon": dmgDealer_att.losesDurability()
		dmg_byAtt = 0 #The damage dealt by the character that attacks
		for dmgDealer, dmgTaker, damage in dmgList:
			#参与战斗的各方在战斗过程中只减少血量，受伤的信号在血量和受伤名单登记完毕之后按被攻击者，攻击者，被涉及者顺序发出。
			game.sendSignal(dmgTaker.category+"TakesDmg", dmgTaker.ID, dmgDealer, dmgTaker, damage)
			game.sendSignal(dmgTaker.category+"TookDmg", dmgTaker.ID, dmgDealer, dmgTaker, damage)
			#吸血扳机始终在队列结算的末尾。
			dmgDealer.tryLifesteal(damage, damageType="Battle")
			dmg_byAtt += damage

		#有需要一次性检测伤害总量的扳机，如骑士奥秘“清算”
		if dmg_byAtt: game.sendSignal("DealtDmg", dmgDealer_att.ID, dmgDealer_att, None, dmg_byAtt)
		if dmg_byDef: game.sendSignal("DealtDmg", dmgDealer_def.ID, dmgDealer_def, None, dmg_byDef)

	"""Handle cards dealing targeting/AOE damage/heal to target(s)."""
	def dmgtoDeal(self, dmg, role="att"): return dmg
	def dmgtoRec(self, dmg, role="def"): return dmg

	#Handle Lifesteal of a card. Currently Minion/Weapon/Spell classs have this method.
	##法术因为有因为外界因素获得吸血的能力，所以有自己的tryLifesteal方法。
	def tryLifesteal(self, damage, damageType="None"):
		game = self.Game
		if self.effects["Lifesteal"] > 0 or (self.category == "Spell" and game.rules[self.ID]["Spells Lifesteal"] > 0)\
				or (damageType == "Battle" and "Drain" in self.effects and self.effects["Drain"] > 0):
			heal = self.calcHeal(damage)
			if game.rules[self.ID]["Heal to Damage"] > 0:
				#If the Lifesteal heal is converted to damage, then the obj to take the final
				#damage will not cause Lifesteal cycle.
				dmgTaker = game.scapegoat4(game.heroes[self.ID])
				dmgTaker.takesDamage(self, heal, damageType="Ability")
			elif game.rules[self.ID]["Lifesteal Damages Enemy"] > 0:
				dmgTaker = game.scapegoat4(game.heroes[3-self.ID])
				dmgTaker.takesDamage(self, heal, damageType="Ability")
			else: #Heal is heal.
				if self.btn and hasattr(self.btn, "icons") and "Lifesteal" in self.btn.icons:
					GUI, icon = game.GUI, self.btn.icons["Lifesteal"]
					GUI.seqHolder[-1].append(GUI.PARALLEL(GUI.FUNC(icon.trigAni), GUI.WAIT(0.25)))
				if healActual := (hero := game.heroes[self.ID]).getsHealed(self, heal):
					game.sendSignal(self.category + "GetsHealed", self.ID, self, hero, healActual)
					game.sendSignal(self.category + "GotHealed", self.ID, self, hero, healActual)

	#可以对在场上以及手牌中的随从造成伤害，同时触发应有的响应，比如暴乱狂战士和+1攻击力和死亡缠绕的抽牌。
	#牌库中的和已经死亡的随从免疫伤害。死亡缠绕只是检测那个随从是否满足死亡的条件
	#吸血同样可以对于手牌中的随从生效并为英雄恢复生命值。如果手牌中的随从有圣盾，那个圣盾可以抵挡伤害，那个随从在打出后没有圣盾（已经消耗）。
	#暂时可以考虑不把吸血做成场上扳机，因为几乎没有战吼随从可以获得吸血同时弹回手牌
	#该函数是效果伤害。战斗伤害由landsAtk处理
	def dealsDamage(self, target, damage, animationType=''):
		#target可以是单个卡牌obj，可以是一个空列表/数组或者正常的列表/数组
		if not isinstance(target, (list, tuple)): target = (target,)
		if len(target) < 1: return (), (), 0

		if not isinstance(damage, (list, tuple)): damage = [damage] * len(target)
		game = self.Game
		self.Game.add2EventinGUI(self, target, textTarget=["-%d" % dmg for dmg in damage], colorTarget=red)
		if len(target) == 1 and game.GUI: game.GUI.resetSubTarColor(self, target)
		dmgTakers, dmgsActual, totalDmg = [], [], 0
		for obj, dmg in zip(target, damage):
			dmgTaker = game.scapegoat4(obj, self)
			# Handle the Divine Shield and Commanding Shout here.
			if (dmgActual := dmgTaker.takesDamage(self, dmg, "Ability")) > 0:
				dmgTakers.append(dmgTaker)
				dmgsActual.append(dmgActual)
				totalDmg += dmgActual
		# AOE时首先计算血量变化，之后才发出伤害信号。
		handleGameEvent, subLocator = game.Counters.handleGameEvent, game.genLocator(self)
		for dmgTaker, dmgActual in zip(dmgTakers, dmgsActual):
			game.sendSignal(dmgTaker.category+"TakesDmg", self.ID, self, dmgTaker, dmgActual)
			game.sendSignal(dmgTaker.category+"TookDmg", self.ID, self, dmgTaker, dmgActual)
		self.tryLifesteal(totalDmg, "Ability")
		if totalDmg > 0:
			game.sendSignal("DealtDmg", self.ID, self, None, totalDmg)
		return dmgTakers, dmgsActual, totalDmg

	def countHealDouble(self):
		if self.category in ("Minion", "Weapon"): return sum(minion.effects["Heal x2"] > 0 for minion in self.Game.minions[self.ID])
		elif self.category in ("Spell", "Power"):
			return sum(minion.effects["Heal x2"] > 0 or minion.effects["Spell Heal&Dmg x2"] > 0 for minion in self.Game.minions[self.ID])
		else: return 0

	def calcHeal(self, base): return base * (2 ** self.countHealDouble())

	def heals(self, target, heal):
		# target可以是单个卡牌obj，可以是一个空列表/数组或者正常的列表/数组
		if not isinstance(target, (list, tuple)): target = (target,)
		if not isinstance(heal, (list, tuple)): heal = [heal] * len(target)
		if len(target) < 1:
			return
		game = self.Game
		if game.rules[self.ID]["Heal to Damage"] > 0:
			self.dealsDamage(target, heal)
		else:
			objsHealed, healsActual, totalHeal = [], [], 0
			if target and game.GUI:
				self.Game.add2EventinGUI(self, target, textTarget=["+%d"%hl for hl in heal], colorTarget=yellow)
			for target, heal in zip(target, heal):
				if (healActual := target.getsHealed(self, heal)) > 0:
					objsHealed.append(target)
					healsActual.append(healActual)
					totalHeal += healActual
			handleGameEvent, subLocator = game.Counters.handleGameEvent, game.genLocator(self)
			for target, healActual in zip(objsHealed, healsActual): #假设是对同一个随从先后进行受到治疗时和受到治疗后的扳机触发
				game.sendSignal(target.category+"GetsHealed", self.ID, self, target, healActual)
				game.sendSignal(target.category+"GotHealed", self.ID, self, target, healActual)
			for target, healActual in zip(objsHealed, healsActual):
				handleGameEvent("Heal", self.ID, healActual, game.genLocator(target))

	#Lifesteal will only calc once with Aukenai,  for a lifesteal damage spell,
	#the damage output is first enhanced by spell damage, then the lifesteal is doubled by Kangor, then the doubled healing is converted by the Aukenai.
	#Heal is heal at this poin. The Auchenai effect has been resolved before this function
	def getsHealed(self, subject, heal):
		game, healActual = self.Game, 0
		if self.category in ("Minion", "Hero") and (self.inHand or self.onBoard):#If the character is dead and removed already or in deck. Nothing happens.
			#This doesn't check if the heal actually changes anything.
			game.sendSignal(self.category + "ReceivesHeal", self.ID, subject, self)
			if self.health < self.health_max:
				healActual = heal if self.health + heal < self.health_max else self.health_max - self.health
				self.dmgTaken -= healActual
				self.calcStat("heal")
		return healActual

	def rngPool(self, identifier):
		cardType = type(self)
		return [card for card in self.Game.RNGPools[identifier] if card is not cardType]

	def newEvolved(self, cost, by=0, ID=0, s="Minions to Summon"):
		#卡牌在生成"x-Cost Minions to Summon"的时候会同时生成"Minions to Summon Costs"
		cost, gameRNGPool = cost + by, self.Game.RNGPools
		if by > 0: #从cost+by往下降至发现一个存在的cost
			cost = next(i for i in reversed(gameRNGPool[s+" Costs"]) if i <= cost)
		elif by < 0: #从cost+by往上升至发现一个存在的cost
			cost = next(i for i in gameRNGPool[s+" Costs"] if i >= cost)
		return numpyChoice(self.rngPool(str(cost)+"-Cost "+s))(self.Game, ID)

	"""卡牌的给予/获得效果，buff等处理"""
	def freeze(self, target, add2EventinGUI=True):  # target可以是列表，数组，单个卡牌obj和None（无事发生）
		if isinstance(target, (list, tuple)): target = [obj for obj in target if obj.onBoard or obj.inHand]
		elif target and (target.onBoard or target.inHand): target = (target,)
		else: return

		if self.Game.GUI and add2EventinGUI: self.Game.add2EventinGUI(self, target)
		for obj in target:
			obj.effects["Frozen"] = 1
			if obj.onBoard and (obj.category == "Minion" or obj.category == "Hero"):
				obj.decideAttChances_base()
				obj.Game.sendSignal("CharFrozen", obj.ID, self, obj)
			if obj.onBoard and obj.btn: obj.btn.effectChangeAni("Frozen")

	"""Common statChange/buffDebuff"""
	#buffDebuff和getsEffect很少单独被调用，一般由giveEnchant统一处理。只有在光环影响下可能会单独调用getsEffect
	def getsBuffDebuff(self, attackGain=0, healthGain=0, source=None, enchant=None, add2EventinGUI=True):
		if not enchant: enchant = Enchantment(source, attackGain, healthGain)
		enchant.addto(self)
		self.calcStat("buffDebuff")

	# 卡牌获得一些效果，如圣盾，嘲讽等。冰冻效果单独由freeze&freeze处理
	# 一些特殊的enchantment需要卡片效果自行定义，普通的enchantment只定义来源卡片各类，然后自行定义
	# 如果效果来源是光环，则enchantment和creator皆为None。普通的赋予特效需要source，然后自行定义Enchantment；特殊的特效需要卡牌效果自行定义一个Enchantment_xxx
	#name是产生这个效果的卡牌效果名称。如WarsongCommander
	def getsEffect(self, effect='', amount=1, source=None, enchant=None):
		if not self.inDeck:
			if enchant:
				effect, amount = enchant.effGain, enchant.effNum
				enchant.addto(self) #The Enchantment_Exclusive can pile on the same enchantment
			elif source: Enchantment(source, effGain=effect, effNum=amount).addto(self)
			# 首先检视卡牌自身的effects，如果特效/不在其中，则交由game.rules处理。
			if effect in self.effects: self.effects[effect] += amount
			elif effect in (effects := self.Game.rules[self.ID]): effects[effect] += amount
			else:
				print("GetsEffect got something unresolvable", effect)
				raise
			if self.onBoard and (self.category == "Minion" or self.category == "Hero"):
				self.decideAttChances_base()
				self.Game.sendSignal("CharEffectCheck", self.Game.turn, None, self)  # 用于部分光环，如方阵指挥官
			if (self.onBoard or self.inHand) and self.btn:
				if effect in ("Lifesteal", "Poisonous"): self.btn.placeIcons()
				else: self.btn.effectChangeAni(effect)

	# 当随从失去关键字的时候不可能有解冻情况发生。
	# 角色失去光环效果时是不涉及移除enchant的。目前会让角色失去effect的情况有:
	# 只会失去所有的： 沉默 | 随从的临时免疫和潜行 | 受伤失去圣盾 | 冰冻解除
	# 会按数值减少的： 光环效果移除 | 英雄的法强伤害等增益移除
	# amount设为负数或0时表示要移除该特效的全部值，仅限 圣盾|潜行|临时潜行|免疫 使用
	# loseAllEffects=True只在随从被沉默时出现
	def losesEffect(self, effect, amount=1, removeEnchant=False, loseAllEffects=False):  # 当角色失去所有keyWords时，amount需要小于0
		if not self.inDeck:
			hadDivineShield = self.category == "Minion" and self.effects["Divine Shield"] > 0
			if loseAllEffects:  # 只会在随从被沉默时调用。随从不会与Game.efffects产生关联
				for key in self.effects.keys(): self.effects[key] = 0  # getsSilenced会自行清理enchantments
			else:
				if effect in self.effects: self.effects[effect] = max(0, self.effects[effect] - amount) if amount > 0 else 0
				elif effect in (effects := self.Game.rules[self.ID]): effects[effect] = max(0, effects[effect] - amount) if amount > 0 else 0
				if removeEnchant:  # 调用removeEnchant的时候一般都是潜行等只有0/1状态的效果，所以只能进行
					for enchant in self.enchantments[:]:
						if enchant.effGain == effect: removefrom(enchant, self.enchantments)
			if self.onBoard:
				self.decideAttChances_base()
				if hadDivineShield: self.Game.sendSignal("CharLoses_" + effect, self.ID, self)
				self.Game.sendSignal("CharEffectCheck", self.Game.turn, None, self)
			if (self.onBoard or self.inHand) and self.btn:  # Lifesteal, Poisonous, Deathrattle and Trig show up at the bottom of the minion icon
				if effect not in ("Lifesteal", "Poisonous"): self.btn.effectChangeAni(effect)
				else: self.btn.placeIcons()

	# Can acquire trigBoard, deathrattle
	def getsTrig(self, trig, trigType="TrigBoard"):
		trig.inherent = False
		{"TrigBoard": self.trigsBoard, "Deathrattle": self.deathrattles, "TrigHand": self.trigsHand}[trigType].append(trig)
		if (trigType in ("TrigBoard", "Deathrattle") and self.onBoard) or (trigType == "TrigHand" and self.inHand):
			trig.connect()
			if self.btn: self.btn.placeIcons()

	def losesTrig(self, trig, trigType="TrigBoard", allTrigs=False):
		if allTrigs:
			for trig in self.trigsBoard + self.deathrattles + self.trigsHand + self.trigsDeck:
				trig.disconnect()
			self.trigsBoard, self.deathrattles, self.trigsHand, self.trigsDeck = [], [], [], []
		else:
			removefrom(trig, {"TrigBoard": self.trigsBoard, "Deathrattle": self.deathrattles, "TrigHand": self.trigsHand}[trigType])
			trig.disconnect()
		if self.btn: self.btn.placeIcons()

	#Combine the stat buffDebuff and effect gain.
	#If only give one effect, effGain should be defined; elif multipleEffGains isn't empty, then multiple effects would be given
	#enchant only need to define its values and card effect that generates it, the source and keeper will be handled by
	#The trigger to give to cards can't store in-game information. It is a simple type
	def giveEnchant(self, target, attackGain=0, healthGain=0, statEnchant=None,
					effGain=None, effNum=1, effectEnchant=None, multipleEffGains=(), source=None,
					trig=None, trigType="TrigBoard", trigs=(), add2EventinGUI=True):
		if not isinstance(target, (list, tuple)): target = (target,)
		target = [obj for obj in target if not (obj.inDeck or obj.dead)]
		if len(target) < 1: return

		if self.Game.GUI and add2EventinGUI:
			if statEnchant: attackGain, healthGain = statEnchant.attGain, statEnchant.healthGain
			if attackGain or healthGain:
				s = "%d/%d"%(attackGain, healthGain)
				color = green if attackGain > -1 and healthGain > -1 else red
			else: s, color = '', white
			self.Game.add2EventinGUI(self, target, textTarget=s, colorTarget=color)

		for obj in target:
			#Enchantment是通用的，可以诸多卡牌共享一个Enchantment实例
			if statEnchant or attackGain or healthGain:
				obj.getsBuffDebuff(attackGain, healthGain, source=source, enchant=statEnchant, add2EventinGUI=add2EventinGUI)
			if effGain: obj.getsEffect(effGain, effNum, source=source, enchant=effectEnchant)
			elif multipleEffGains: #Use the (effGain, amount, effectEnchant) given in the multipleEffGains container
				for effect, num, enchant in multipleEffGains: obj.getsEffect(effect, num, source=source, enchant=enchant)
			#trig不能是携带有除keeper以外信息的。只能是类。如果需要让卡牌带上特殊的扳机，则让卡牌直接引用getsTrig
			if trig: obj.getsTrig(trig(obj), trigType)
			elif trigs:
				for trigger, triggerType in trigs: obj.getsTrig(trigger(obj), triggerType)

	def getsBuffDebuff_inDeck(self, attackGain, healthGain, source=None):
		self.enchantments.append(Enchantment(source, attackGain, healthGain))
		self.attack, self.health_max = self.attack_0, self.health_0
		for enchant in self.enchantments: enchant.handleStatMax(self)
		self.health = self.health_max

	def giveHeroAttackArmor(self, ID, attGain=0, statEnchant=None, armor=0, source=None):
		hero = (game := self.Game).heroes[ID]
		if statEnchant or attGain:
			if not statEnchant: statEnchant = Enchantment(source, attGain=attGain, until=0)
			statEnchant.addto(hero)
		s = "%d|%d"%(statEnchant.attGain if statEnchant else attGain, armor)
		if game.GUI: game.add2EventinGUI(self, hero, textTarget=s, colorTarget=white)

		if statEnchant: hero.calcStat("buffDebuff")
		game.sendSignal("HeroAttGained", ID, hero, None, attGain)
		if armor:
			hero.armor += armor
			if hero.btn: hero.btn.statChangeAni(action="armorChange")
			game.Counters.handleGameEvent("GainArmor", ID, armor)
			game.sendSignal("ArmorGained", ID, hero, None, armor)

	# Either newAttack or newHealth must be a non-negative number
	#Can handle multi-target with different Attack/Health
	#newStat must be a single tuple or a list of tuples
	def setStat(self, target, newStat=(None, None), source=None, add2EventinGUI=True):
		if not isinstance(target, (list, tuple)): target = (target,)
		target = [obj for obj in target if not (obj.inDeck or obj.dead)]
		if len(target) < 1: return

		if isinstance(newStat, list): #Different tups for each minion
			if self.Game.GUI and add2EventinGUI:
				self.Game.add2EventinGUI(self, target, textTarget="=>/<=", colorTarget=white)
			for obj, stat in zip(target, newStat):
				newAttack, newHealth = stat
				if newHealth: obj.dmgTaken = 0
				obj.enchantments.append(Enchantment(source, attSet=newAttack, healthSet=newHealth))
				obj.calcStat()
		else: #A single tup will apply to all minions
			newAttack, newHealth = newStat
			enchant = Enchantment(source, attSet=newAttack, healthSet=newHealth)
			if self.Game.GUI and add2EventinGUI:
				s = (str(newAttack) if newAttack is not None else '') + '/' + (str(newHealth) if newHealth is not None else '')
				self.Game.add2EventinGUI(self, target, textTarget=s, colorTarget=white)
			for obj in target:
				if newHealth: obj.dmgTaken = 0
				obj.enchantments.append(enchant)
				obj.calcStat()

	#Only applicable to Wave of Apathy at the moment. enchant is a single obj shared by all minions
	def setStat_Enchant(self, target, enchant, add2EventinGUI=True):
		if not isinstance(target, (list, tuple)): target = (target,)
		target = [obj for obj in target if not (obj.inDeck or obj.dead)]
		if len(target) < 1: return

		newAttack, newHealth = enchant.attSet, enchant.healthSet
		if self.Game.GUI and add2EventinGUI:
			s = (str(newAttack) if newAttack is not None else '') + '/' + (str(newHealth) if newHealth is not None else '')
			self.Game.add2EventinGUI(self, target, textTarget=s, colorTarget=white)
		for obj in target:
			if newHealth: obj.dmgTaken = 0
			obj.enchantments.append(enchant)
			obj.calcStat()

	def getsStatSet_inDeck(self, newAttack=None, newHealth=None, source=None):
		self.enchantments.append(Enchantment(source, attSet=newAttack, healthSet=newHealth))
		if newAttack is not None: self.attack = newAttack
		if newHealth is not None: self.health = self.health_max = newHealth

	def statCheckResponse(self): pass
	#Some special card need their own calcStat, like Lightspawn
	#prevHealth >=0 only when minion getting silenced, since minion tries to stay at the same health
	def calcStat(self, action="set", num2=0, prevHealth=-1): #During damage on hero, the damage reduction due to armor requires num2.
		if self.category in ("Minion", "Weapon", "Hero"):
			attOrig, healthOrig = self.attack, self.health
			self.attack, self.health_max = self.attack_0, self.health_0
			for enchant in self.enchantments: enchant.handleStatMax(self)
			for receiver in self.auraReceivers: receiver.handleStatMax()
			if prevHealth < 0: self.health = self.health_max - self.dmgTaken
			else:
				self.health = min(self.health_max, prevHealth)
				self.dmgTaken = self.health_max - self.health
			self.statCheckResponse()

			if self.category == "Hero" and self.Game.turn == self.ID:
				if weapon := self.Game.availableWeapon(self.ID): self.attack += max(0, weapon.attack)
				if healthOrig != self.health: self.Game.Counters.handleGameEvent("HeroHealthChange", self.ID)
			if self.btn: self.btn.statChangeAni(num1=self.attack-attOrig, num2=num2 if num2 else self.health-healthOrig, action=action)
			self.Game.sendSignal("%sStatCheck"%self.category, self.ID, None, self)
			if self.category == "Weapon" and self.ID == self.Game.turn: self.Game.heroes[self.ID].calcStat()

	"""
	目前的发现种类
	一个随机池里面挑3个发现并生成，3个随机池里面各挑一个发现并生成---可以有随机选项存在
	固定选项里面挑一个生成
	从卡牌列表里挑一个现有的，从历史记录里面挑一个生成
	"""
	#因为所有发现界面的东西都会进行picks的读取，所以随机发现和引导下的发现都需要和手动发现一样的。
	#即使这一个发现可能没有问题，也可能会有连续发现的情况，导致出现问题
	def randomorDiscover(self, game, comment, options):
		if self.ID != game.turn or "byOthers" in comment:
			i = datetime.now().microsecond % len(options)
			if game.GUI: game.GUI.discoverDecideAni(isRandom=True, indPick=i, options=options)
			return options[i], i, True
		else: return *game.Discover.startDiscover(options), False

	#Most basic Discovers, such as "Discover a spell". Choose 3(max) out of a single pool
	#只有这个最基础的发现会有加入自己手牌的选项，其他的发现要执行的效果一般都比较复杂，没有必要设立这个选项。
	#如果算作严格的发现并加入手牌（如描述为检视一张牌），则不能使用add2Hand的默认选项
	#第一个返回值是选择的选项，而所有卡牌都会在第二个返回值里面
	def discoverNew(self, comment, poolFunc, add2Hand=True, sideOption=None): #可以有额外选项，如狐人恶棍和Guide
		game, ID = self.Game, self.ID
		if not game.mode:
			if game.picks:
				i, *(poolSize, numChoice, choices), isRandom = game.picks.pop(0)
				if not poolSize:
					return None, ()
				numpyChoice(range(poolSize), numChoice, replace=False)
				options = [card(game, ID) for card in choices]
				finalOptions = (options + [sideOption]) if sideOption else options
				if game.GUI: game.GUI.discoverDecideAni(isRandom=isRandom, indPick=i, options=finalOptions)
				if add2Hand: self.addCardtoHand(options[i], ID, byDiscover=True)
				return options[i], options
			else:
				poolSize = len(pool := poolFunc())
				if not pool: return game.picks_Backup.append((None, (None, None, None), None)), ()
				else:
					choices = numpyChoice(pool, (numChoice := min(3, poolSize)), replace=False)
					options = [choice(game, ID) for choice in choices]
					finalOptions = (options + [sideOption]) if sideOption else options
					card, i, isRandom = self.randomorDiscover(game, comment, finalOptions)
					self.Game.picks_Backup.append((i, (poolSize, numChoice, choices), isRandom))
					if add2Hand: self.addCardtoHand(card, ID, byDiscover=True)
					return card, options

	#Such as "Discover a Hunter secret, Hunter weapon and a Beast". Choose one from each different pool
	def discoverNew_MultiPools(self, comment, poolsFunc, add2Hand=True):
		game, ID = self.Game, self.ID
		if not game.mode:
			if game.picks:
				i, *(poolSizes, choices), isRandom = game.picks.pop(0)
				for poolSize in poolSizes: numpyChoice(range(poolSize))
				options = [choice(game, ID) for choice in choices]
				if game.GUI: game.GUI.discoverDecideAni(isRandom=isRandom, indPick=i, options=options)
				if add2Hand: self.addCardtoHand(options[i], self.ID, byDiscover=True)
				return options[i]
			else:
				pools = poolsFunc()
				choices, poolSizes = tuple(numpyChoice(pool) for pool in pools), tuple(len(pool) for pool in pools)
				card, i, isRandom = self.randomorDiscover(game, comment, [choice(game, ID) for choice in choices])
				self.Game.picks_Backup.append((i, (poolSizes, choices), isRandom))
				if add2Hand: self.addCardtoHand(card, self.ID, byDiscover=True)
				return card

	#完全确定的选项，类似Totemic Slam。options are objects. Such as [HealingTotem(game, 1) ...]
	def chooseFixedOptions(self, comment, options):
		game = self.Game
		if not game.mode:
			if game.picks:
				i, _, isRandom = game.picks.pop(0)
				if game.GUI: game.GUI.discoverDecideAni(isRandom=isRandom, indPick=i, options=options)
				return options[i]
			else:
				card, i, isRandom = self.randomorDiscover(game, comment, options)
				self.Game.picks_Backup.append((i, None, isRandom))
				return card

	#如果tupsFunc不为None，则根据历史信息生成新的卡牌。
	#如果tupsFunc是None，则如果ls为None时默认为从自己的牌库中发现。不然从ls中挑选满足cond的卡牌。
	def discoverfrom(self, comment, tupsFunc=None, cond=lambda card: True, ls=None):
		game, ID = self.Game, self.ID
		if not game.mode:
			if game.picks:
				i, *(numTypes, numChoice, poolSizes, inds_tups), isRandom = game.picks.pop(0)
				if not numTypes: return None, -1
				numpyChoice(numTypes, numChoice, replace=False)
				for poolSize in poolSizes: numpyChoice(range(poolSize))
				#如果没有tupsFunc，则说明是从现有的列表中进行寻找
				if tupsFunc: options = [game.fabCard(tup, ID, self) for tup in inds_tups]
				else:
					if not ls: ls = game.Hand_Deck.decks[ID]
					options = [ls[ind] for ind in inds_tups]
				if game.GUI: game.GUI.discoverDecideAni(isRandom=isRandom, indPick=i, options=options)
				return options[i], inds_tups[i] #从现有列表发现时，第二个参数是序号；否则是一个没有用的tup
			else:
				if tupsFunc: types, probs, typs2TupsInds = discoverProb_fromTups(tups := tupsFunc())
				else: types, probs, typs2TupsInds = discoverProb(ls := ls if ls else game.Hand_Deck.decks[ID], cond)
				if not types: return self.Game.picks_Backup.append((None, (None, None, None, None), None)), -1
				else:
					numChoice = min(3, numTypes := len(types))
					types = numpyChoice(types, numChoice, p=probs, replace=False)
					poolSizes = tuple(len(typs2TupsInds[typ]) for typ in types)
					tups_Inds = [numpyChoice(typs2TupsInds[typ]) for typ in types]
					#如果有ls则采用从ls中选取序号，否则再用fabCard创造新的卡
					options = [ls[i] for i in tups_Inds] if ls else [game.fabCard(tup, self.ID, self) for tup in tups_Inds]
					card, i, isRandom = self.randomorDiscover(game, comment, options)
					# 只需要向对方发送自己选了第几，和哪几个序号
					self.Game.picks_Backup.append((i, (numTypes, numChoice, poolSizes, tups_Inds), isRandom))
					return card, tups_Inds[i]

	#Choose a target that is onBoard/inHand during effect resolution. Now only applicable to GoliathSneedsMasterpiece
	#ls会在调用函数时直接选好。只有在不为空的时候才会调用这个函数
	def choosefromBoard(self, comment, ls): #ls可以根据index找到选择的目标
		game = self.Game
		if not game.mode:
			if game.picks: #在场上的选择是没有随机产生的。info_RNGSync总是None
				i, _, isRandom = game.picks.pop(0)
				option = ls[i]
				if game.GUI: game.GUI.chooseDecideAni(isRandom=isRandom, indexOption=i, options=ls)
				return option
			else:
				if isRandom := ((numOption := len(ls)) == 1 or self.ID != game.turn or "byOthers" in comment):  # 如果只有一个选项则跳过手动发现过程
					card = ls[(i := datetime.now().microsecond % numOption)]
					if game.GUI: game.GUI.chooseDecideAni(isRandom=True, indexOption=i, options=ls)
				else: card, i = game.Discover.startChoose(self, ls=ls)
				game.picks_Backup.append((i, None, isRandom))
				return card

	"""Common card generation handlers"""
	def copyCard(self, card, ID, attack=None, health=None, mana=None, bareCopy=False):
		if bareCopy or (card.category == "Minion" and not (card.onBoard or card.inHand)):
			Copy = self.Game.fabCard(card.getBareTup(), ID, type(self))
			if Copy.category == "Minion" and (attack or health): # 如果要生成一个x/x/x的复制
				Copy.enchantments.append(Enchantment(Copy.creator, attSet=attack, healthSet=health))
			if mana: Copy.manaMods.append(ManaMod(Copy, to=mana))
			return Copy
		else: return card.selfCopy(ID, self, attack, health, mana)

	def addCardtoHand(self, card, ID, byDiscover=False, pos=-1, ani="fromCenter"):
		self.Game.Hand_Deck.addCardtoHand(card, ID, byDiscover=byDiscover, pos=pos, ani=ani, creator=type(self))
		
	def shuffleintoDeck(self, target, enemyCanSee=True):
		self.Game.Hand_Deck.shuffleintoDeck(target, initiatorID=self.ID, enemyCanSee=enemyCanSee, creator=type(self))

	def summon(self, subject, relative=">", position=None):
		return self.Game.summon(subject, self, relative=relative, position=position)

	def try_SummonfromOwn(self, position=None, hand_deck=1, cond=lambda card: card.category == "Minion"):
		ls_Cards = self.Game.Hand_Deck.decks[self.ID] if hand_deck else self.Game.Hand_Deck.hands[self.ID]
		if self.Game.space(self.ID) and (indices := [i for i, card in enumerate(ls_Cards) if cond(card)]):
			return self.Game.summonfrom(numpyChoice(indices), self.ID, self.pos+1 if position is None else position,
										summoner=self, hand_deck=hand_deck)
		return None

	#target可以是list或object
	def transform(self, target, newTarget):
		self.Game.transform(target, newTarget, summoner=self)

	def replayCard_fromTup(self, tup):
		card = self.Game.fabCard(tup, self.ID, self)
		if card.category == "Minion": self.summon(card)
		elif card.category == "Spell": card.cast()
		elif card.category == "Weapon": self.equipWeapon(card)
		elif card.category == "Hero": card.replaceHero(fromHeroCard=True)
		else: return
		self.Game.gathertheDead(decideWinner=True)

	def killandSummon(self, target, newTarget):
		#newTarget can be a single obj, or a list/tuple
		pos = target.pos
		self.Game.kill(self, target)
		self.Game.gathertheDead()
		if newTarget: self.summon(newTarget, position=pos)

	def equipWeapon(self, weapon):
		self.Game.equipWeapon(weapon, creator=type(self))

	#1st param is None when empty/no match. When there is milling, returns (card, x, False)
	def drawCertainCard(self, cond=lambda card: True):
		if indices := [i for i, card in enumerate(self.Game.Hand_Deck.decks[self.ID]) if cond(card)]:
			return self.Game.Hand_Deck.drawCard(self.ID, numpyChoice(indices))
		return None, -1, False #When no card meets requirement, then no card would enter hand

	#If not specified, all cards in owner's hand will be legal target. Assuming cards costing >0 will be prioritized.
	def findCards2ReduceMana(self, conditional=lambda card: True, ID=0):
		hand = self.Game.Hand_Deck.hands[ID if ID else self.ID]
		if cards := [card for card in hand if conditional(card) and card.mana > 0]:
			return cards
		else: return [card for card in hand if conditional(card)]

	def deathResolution(self, armedTrigs_WhenDies, armedTrigs_AfterDied):
		if self.category in ("Minion", "Weapon", "Amulet"):
			self.Game.sendSignal("ObjDies", self.Game.turn, None, self, 0, '', trigPool=armedTrigs_WhenDies)
			#亡语和“每当你的一个随从死亡”的扳机是同时点触发。一个随从的多个亡语会连续触发。
			#随从在结算死亡的情况下，disappears()不会直接取消亡语这些扳机，而是等到deathResolution的时候触发这些扳机
			#如果是提前离场，如改变控制权或者是返回手牌，则需要取消这些扳机。
			#区域移动类扳机一般不能触发两次。游戏中的很多区域移动扳机实际上只是生成一个卡牌的复制。而我们严格进行移动
			#随从只有在场上结算亡语完毕之后才会进行初始化。一般情况下扳机将随从返回手牌或者牌库，随从也会被初始化，而永恒祭司自己的亡语会保存附魔效果。
			for trig in self.deathrattles: trig.disconnect()
			self.Game.Counters.handleObjDeath(self)
			self.Game.sendSignal("ObjDied", self.Game.turn, None, self, 0, "", trigPool=armedTrigs_AfterDied)

	"""Copy card effects"""
	#继承一张卡的所有附魔时一定是那张卡要消失的时候。一般用于一张牌的升级/腐蚀变形
	def inheritEnchantmentsfrom(self, card):
		for receiver in card.auraReceivers: receiver.effectClear()
		#Buff and mana effects, etc, will be preserved
		#Buff to cards in hand will always be permanent or temporary, not from Auras
		if self.category in ("Minion", "Weapon"):
			self.enchantments += card.enchantments
			for trig in card.deathrattles:
				trig.keeper = self
				self.deathrattles.append(trig)
			for enchant in card.enchantments: enchant.handleEffect(card)
			self.calcStat()
		#Inhand triggers and mana modifications
		for trig in card.trigsBoard:
			if not trig.inherent:
				trig.keeper = self
				self.trigsBoard.append(trig)
		for trig in card.trigsHand: #Some cards can get trigs that discard them.
			if not trig.inherent:
				trig.keeper = self
				self.trigsHand.append(trig)
		self.manaMods = [manaMod.selfCopy(self) for manaMod in card.manaMods if not manaMod.source]

	#在一个游戏内生成一个Copy，即复制一张手牌/随从等。Dormant不会selfCopy
	def selfCopy(self, ID, creator, attack=None, health=None, mana=None):
		Copy = type(self)(self.Game, ID)
		Copy.creator, Copy.progress = type(creator) if creator else None, self.progress
		#没有改变一张牌库扳机的效果，所以不需要复制
		#复制一张牌受伤以及各种效果和扳机.目前没有复制场上的英雄的效果
		Copy.mana_0, Copy.info1, Copy.info2 = self.mana_0, self.info1, self.info2
		Copy.effects = copy.deepcopy(self.effects)
		Copy.manaMods = [manaMod.selfCopy(Copy) for manaMod in self.manaMods if not manaMod.source]
		Copy.enchantments = [enchant.selfCopy(Copy) for enchant in self.enchantments]
		Copy.trigsBoard = [trig.selfCopy(Copy) for trig in self.trigsBoard]
		Copy.trigsHand = [trig.selfCopy(Copy) for trig in self.trigsHand]
			#只有随从和武器有亡语
		if self.category in ("Minion", "Weapon"):
			Copy.attack_0, Copy.health_0, Copy.dmgTaken = self.attack_0, self.health_0, self.dmgTaken
			Copy.deathrattles = [trig.selfCopy(Copy) for trig in self.deathrattles]
		if self.category == "Minion": #只有随从有光环和沉默
			Copy.silenced = self.silenced
			Copy.auras = [aura.selfCopy(Copy) for aura in self.auras]
			# 如果要生成一个x/x/x的复制
			if attack or health:
				Copy.enchantments.append(Enchantment(Copy.creator, attSet=attack, healthSet=health))
		if mana: Copy.manaMods.append(ManaMod(Copy, to=mana))
		self.assistSelfCopy(Copy)
		return Copy

	def createCopy(self, game):
		if self in game.copiedObjs: return game.copiedObjs[self]
		else:
			game.copiedObjs[self] = Copy = type(self)(game, self.ID)
			Copy.enterHandTurn, Copy.enterBoardTurn = self.enterHandTurn, self.enterBoardTurn
			Copy.creator, Copy.progress, Copy.usageCount = self.creator, self.progress, self.usageCount
			#效果和扳机
			Copy.info1, Copy.info2 = self.info1, self.info2
			Copy.effects = copy.deepcopy(self.effects)
			Copy.enchantments = [enchant.selfCopy(Copy) for enchant in self.enchantments] #附魔没有createCopy
			Copy.deathrattles = [trig.createCopy(game) for trig in self.deathrattles]
			Copy.trigsBoard = [trig.createCopy(game) for trig in self.trigsBoard]
			Copy.trigsHand = [trig.createCopy(game) for trig in self.trigsHand]
				#光环和受到的光环效果
			Copy.mana_0, Copy.mana, Copy.manaMods = self.mana_0, self.mana, [manaMod.createCopy(Copy) for manaMod in self.manaMods]
			Copy.auras = [aura.createCopy(game) for aura in self.auras]
			Copy.auraReceivers = [receiver.selfCopy(Copy) for receiver in self.auraReceivers]

			#没有更改一张牌牌库扳机的效果，不需要处理
			if self.category in ("Minion", "Weapon", "Hero"):
				Copy.onBoard, Copy.seq, Copy.pos = self.onBoard, self.seq, self.pos
				Copy.dmgTaken = self.dmgTaken
				Copy.attack, Copy.health, Copy.health_max = self.attack, self.health, self.health_max
				Copy.inHand, Copy.inDeck, Copy.dead = self.inHand, self.inDeck, self.dead
				if self.category == "Minion":
					Copy.silenced = self.silenced
					Copy.attack_0, Copy.health_0 = self.attack_0, self.health_0
					Copy.attChances_base, Copy.attChances_extra = self.attChances_base, self.attChances_extra
				elif self.category == "Hero":
					Copy.armor = self.armor
					Copy.attChances_base, Copy.attChances_extra = self.attChances_base, self.attChances_extra

			#随从等接受的光环效果与产生这些效果的光环之间的复制：
				#首先复制这些随从接受的光环效果，复制得到的效果仍然引用原游戏中光环。
				#凡是可能产生光环的随从，在最终开始复制其产生的光环之前，它们接受到的光环效果保证已经全部复制完毕了
				#此时状态为，光环接受者的复制已成功带上了相应的光环效果的复制，但是这些效果错误的指向原游戏中的光环发生者的光环
					#所以在光环发生者的光环的复制过程中，需要原光环检查自己的每个(光环接受者, 光环效果)对，然后找到光环效果在这个接受者的auraReceivers中的序号。
						#然后光环接受者的复制就可以凭借这个序号找到正确的对应某个光环效果的光环
				#在光环发生者的光环复制时，这个光环会检查接收到自己光环的所有aura_Receiver，找到它们的序号，然后就看光环接受者的复制中
			self.assistCreateCopy(Copy)
			return Copy

	def assistSelfCopy(self, Copy): pass
	def assistCreateCopy(self, Copy): pass



class Minion(Card):
	category = "Minion"
	aura = deathrattle = None
	def __init__(self, Game, ID, statsEffects=''):
		super().__init__(Game, ID)
		cardType = type(self)
		if statsEffects: #"3,2,4|Spell Damage_3,Poisonous"
			mana_0, attack_0, health_0, *_ = statsEffects.split(",")
			self.mana_0, self.attack_0, self.health_0 = int(mana_0), int(attack_0), int(health_0)
		# 卡牌的费用和对于费用修改的效果列表在此处定义
		self.effects = {"Taunt": 0, "Divine Shield": 0,
						"Stealth": 0, "Temp Stealth": 0, "Evasive": 0, "Enemy Evasive": 0, "Immune": 0,
						"Spell Damage": 0, "Nature Spell Damage": 0, "Heal x2": 0, "Power Heal&Dmg x2": 0, "Spell Heal&Dmg x2": 0,
						"Sweep": 0, "Lifesteal": 0, "Poisonous": 0,
						"Charge": 0, "Rush": 0, "Frozen": 0, "Borrowed": 0, "Windfury": 0, "Mega Windfury": 0,
						"Can't Attack": 0, "Can't Attack Hero": 0, "Unplayable": 0,
						"Cost Health Instead": 0,
						"Reborn": 0, "Echo": 0,
						#SV effects
						"Enemy Effect Damage Immune": 0, "Next Damage 0": 0,
						"Bane": 0, "Drain": 0,
						"Can't Break": 0, "Can't Disappear": 0, "Can't Be Attacked": 0, "Disappear When Die": 0,
						"Ignore Taunt": 0, "Can't Evolve": 0, "Free Evolve": 0,
						"Can Attack 3 times": 0, "Deal Damage 0": 0,
						"Enemy Effect Evasive": 0,
						"Evolved": 0,
						 }
		self.setEffects_fromStr()
		self.silenced = False  # This mark is for minion state change, such as enrage.
		# self.seq records the number of the minion's appearance. The first minion on board has a sequence of 0
		self.usageCount = self.attChances_base = self.attChances_extra = 0
		if cardType.aura: self.auras = [cardType.aura(self)]
		if cardType.deathrattle: self.deathrattles = [cardType.deathrattle(self)]

	def available(self): return self.Game.space(self.ID) > 0
	"""Handle the trigsBoard/inHand/inDeck of minions based on its move"""
	#可以休眠的随从会有自己的appears方法，但是其中会引用这个方法，并传入dormantTrig
	def appears(self, firstTime=True, dormantTrig=None):
		self.onBoard, self.enterBoardTurn = True, self.Game.turnInd
		self.inHand = self.inDeck = self.dead = False
		self.mana = self.mana_0  # Restore the minion's mana to original value.
		for manaMod in self.manaMods[:]: manaMod.getsRemoved()
		self.manaMods = []
		if dormantTrig:
			self.category = "Dormant"
			self.trigsBoard.append(dormantTrig)
			dormantTrig.connect()
		else:
			self.category = "Minion"
			for aura in self.auras: aura.auraAppears()
			for trig in self.trigsBoard + self.deathrattles: trig.connect()
			self.decideAttChances_base()  # Decide base att chances, given Windfury and Mega Windfury
		if self.btn:
			self.btn.isPlayed, self.btn.card = True, self
			self.btn.placeIcons()
			self.btn.effectChangeAni()
		if not dormantTrig:
			# auras will react to this signal.
			self.Game.sendSignal("MinionAppears", self.ID, None, self, 0, comment=firstTime)
			self.calcStat()
		return self

	def appears_fromPlay(self, choice):
		return self.appears(firstTime=True)

	def disappears(self, deathrattlesStayArmed=False):  # The minion is about to leave board.
		self.onBoard = self.inHand = self.inDeck = False
		for aura in self.auras: aura.auraDisappears()
		for trig in self.trigsBoard: trig.disconnect()
		# 随从因离场方式不同，对于亡语扳机的注册是否保留也有不同
		# 死亡时触发的区域移动扳机导致的返回手牌或者牌库--保留其他死亡扳机的注册
		# 存活状态下因为亡语触发效果而触发的区域移动扳机--保留其他死亡扳机
		# 存活状态下因为闷棍等效果导致的返回手牌--注销全部死亡扳机
		# 存活状态下因为控制权变更，会取消全部死亡扳机的注册，在随从移动到另一侧的时候重新注册死亡扳机
		# 总之，区域移动扳机的触发不会取消其他注册了的死亡扳机,这些死亡扳机会在它们触发之后移除。
		# 如果那些死亡扳机是因为其他效果而触发（非死亡），除非随从在扳机触发后已经离场（返回手牌或者牌库），否则可以保留
		if not deathrattlesStayArmed:
			for trig in self.deathrattles: trig.disconnect()
		# Let Stat_Receivers and hasreceivers remove themselves
		while self.auraReceivers: self.auraReceivers[0].effectClear()
		self.Game.sendSignal("MinionDisappears", self.ID, None, self)

	#从在场上存在到变成休眠体
	def goDormant(self, trig):
		self.disappears()
		self.onBoard, self.category = True, "Dormant"
		self.trigsBoard.append(trig)
		trig.connect()
		if self.btn:
			self.btn.effectChangeAni()
			self.btn.placeIcons()
		self.Game.sendSignal("MinionDisappears", self.ID, None, self)

	def awaken(self):
		self.category = "Minion"
		self.appears(firstTime=False)
		if hasattr(self, "awakenEffect"):
			self.awakenEffect()

	"""Attack chances handle"""
	# The game will directly invoke the turnStarts/turnEnds methods.
	def turnStarts(self, turn2Start):
		if self.category != "Minion":
			return
		super().turnStarts(turn2Start)
		if turn2Start == self.ID:
			if self.onBoard: self.losesEffect("Temp Stealth", 0, removeEnchant=True)
			self.usageCount = self.attChances_extra = 0
			self.decideAttChances_base()
		self.calcStat()
		if self.btn: self.btn.effectChangeAni()
		## 影之诗中的融合随从每个回合只能进行一次融合，需要在每个回合开始时重置
		#if self.index.startswith("SV_") and hasattr(self, "fusion"):
		#	self.fusion = 1

	# Violet teacher is frozen in hand. When played right after being frozen or a turn after that, it can't defrost.
	# The minion is still frozen when played. And since it's not actionable, it won't defrost at the end of turn either.
	# 随从不能因为有多次攻击机会而自行解冻。只能等回合结束。
	def turnEnds(self, turn2End):
		if self.category != "Minion":
			return
		super().turnEnds(turn2End)
		self.losesEffect("Immune", 0, removeEnchant=True)
		if turn2End == self.ID: # The minion can only thaw itself at the end of its turn. Not during or outside its turn
			if self.onBoard and self.effects["Frozen"] > 0:  # The minion can't defrost in hand.
				if self.actionable() and self.attChances_base + self.attChances_extra > self.usageCount:
					self.losesEffect("Frozen", 0)

		self.usageCount = self.attChances_extra = 0
		self.calcStat()
		if self.btn: self.btn.effectChangeAni()

	# Whether the minion can select the attack target or not.
	def canAttack(self):
		# THE CHARGE/RUSH MINIONS WILL GAIN ATTACKCHANCES WHEN THEY APPEAR
		return self.actionable() and self.attack > 0 and self.effects["Frozen"] < 1 \
			   and self.attChances_base + self.attChances_extra > self.usageCount \
			   and self.attackAllowedbyEffect()

	def attackAllowedbyEffect(self):
		return self.effects["Can't Attack"] < 1

	def canAttackTarget(self, target):
		#自己可以攻击，目标是场上的敌方角色，那个角色不能有潜行/免疫/不能被攻击等效果
		#目标是随从，或者是英雄的场合需要自己没有“不能攻击英雄”的效果，同时是之前回合进场或者被暂时控制或者有冲锋
		#目标是有嘲讽的随从，或者对方场上没有那个目标迟延的有嘲讽且没有潜行/免疫/不能被攻击等效果
		return self.canAttack() and target.onBoard and target.ID != self.ID and target.notHiddenfromAttack() \
			   and (target.category == "Minion" or (target.category == "Hero" and self.effects["Can't Attack Hero"] < 1 and
													(self.enterBoardTurn < self.Game.turnInd or self.effects["Borrowed"] + self.effects["Charge"] > 0))) \
			   and ((target.category == "Minion" and target.effects["Taunt"] > 0)
					or not any(obj is not target and obj.effects["Taunt"] > 0 and obj.notHiddenfromAttack() for obj in target.Game.minions[target.ID])
					or self.Game.rules[self.ID]["Ignore Taunt"] > 0 or self.effects["Ignore Taunt"] > 0)

	"""Healing, damage, takeDamage, AOE, lifesteal and dealing damage response"""
	# Stealth Dreadscale actually stays in stealth.
	def takesDamage(self, subject, damage, damageType="None"):
		if not (self.onBoard or self.inHand) or self.category != "Minion":
			return 0
		game = self.Game
		if self.effects["Immune"] < 1:  # 随从首先结算免疫和圣盾对于伤害的作用，然后进行预检测判定
			if "Next Damage 0" in self.effects and self.effects["Next Damage 0"] > 0:
				if not subject.category == "Hero" or damage:
					damage = 0
					self.effects["Next Damage 0"] = 0
			if damageType == "Ability" and "Enemy Effect Damage Immune" in self.effects \
					and self.effects["Enemy Effect Damage Immune"] > 0:
				damage = 0
			if "Deal Damage 0" in subject.effects and subject.effects["Deal Damage 0"] > 0:
				damage = 0
			if "Bane" in subject.effects and subject.effects["Bane"] > 0 and damageType == "Battle" and self.onBoard:
				self.dead = True
			if damage > 0:
				if self.effects["Divine Shield"] > 0:
					damage = 0
					self.losesEffect("Divine Shield", removeEnchant=True)
				else:
					# 伤害量预检测。如果随从有圣盾则伤害预检测实际上是没有意义的。
					damageHolder = [damage]  # 这个列表用于盛装伤害数值，会经由伤害扳机判定
					game.sendSignal("FinalDmgonMinion?", 0, subject, self, damageHolder)
					damage = damageHolder[0]
					deadbyPoisonous = self.onBoard and ((subject.category == "Spell" and game.rules[subject.ID]["Spells Poisonous"] > 0) or
									   					("Poisonous" in subject.effects and subject.effects["Poisonous"] > 0))
					self.dmgTaken += damage
					game.Counters.handleGameEvent("Damage", game.genLocator(subject), game.genLocator(self), damage)
					self.calcStat("poisonousDamage" if deadbyPoisonous else "damage", num2=-damage)
					# 经过检测，被伏击者返回手牌中的紫罗兰老师不会因为毒药贩子加精灵弓箭手而直接丢弃。会减1血，并在打出时复原。
					if deadbyPoisonous:
						if (GUI := self.Game.GUI) and "Poisonous" in subject.btn.icons:
							GUI.seqHolder[-1].append(GUI.PARALLEL(GUI.FUNC(subject.btn.icons["Poisonous"].trigAni), GUI.WAIT(0.2)))
						self.dead = True
			else:
				game.sendSignal("MinionTakes0Dmg", game.turn, subject, self)
				game.sendSignal("MinionTook0Dmg", game.turn, subject, self)
		else: damage = 0
		return damage

	def magnetCombine(self, target):
		pass

	def invokeBattlecry(self, effOwnerType):
		target = self.randomTargets(numTargetsNeeded := self.numTargetsNeeded())

		if self.Game.GUI:
			effOwnerObj = effOwnerType(self.Game, self.ID)
			self.Game.GUI.showOffBoardTrig(effOwnerObj)
			self.Game.eventinGUI(effOwnerObj, "Battlecry", target=target)
		if not numTargetsNeeded or target:
			effOwnerType.playedEffect(self, target, comment="byOthers")

	# 破法者因为阿努巴尔潜伏者的亡语被返回手牌，之后被沉默，但是仍然可以触发其战吼
	#需要首先记住随从的原始生命值。然后去除身上的所有光环效果以及它们各自对应的光环。然后清空随从身上的所有effects&enchantments&effects
	#之前的光环视情况返回随从身上
	#即使随从带有enchantment和加血光环带来的血量变化，沉默也尽量不会改变当前血量，除非新的血量上限会比当前血量更低。然后重新计算dmgTaken
	def getsSilenced(self, keepStatEnchant=False):
		if self.category != "Minion": return
		self.postSilence(*self.removeEffectsTrigsAuras(keepStatEnchant))

	def removeEffectsTrigsAuras(self, keepStatEnchant=False):
		self.silenced, prevHealth = True, self.health
		self.losesTrig(None, allTrigs=True)  # 清除所有场上扳机,亡语扳机，手牌扳机和牌库扳机。然后将这些扳机全部清除
		for aura in self.auras: aura.auraDisappears()  # Clear the minion's auras
		self.auras = []
		auras_Receivers = [(receiver.source, receiver) for receiver in self.auraReceivers]
		self.auraReceivers = []
		if not keepStatEnchant: self.enchantments = []  # 效果和身材的enchant都除去
		else:  # 保存身材的enchantment，移除只有effGain。enchant不会同时有身材变化和effGain
			for i in reversed(range(len(self.enchantments))):
				if self.enchantments[i].effGain: self.enchantments.pop(i)

		returnBorrowed = self.effects["Borrowed"] > 0 and self.onBoard
		for key in self.effects: self.effects[key] = 0
		return returnBorrowed, prevHealth, auras_Receivers

	def postSilence(self, returnBorrowed, prevHealth, auras_Receivers):
		if returnBorrowed: #被归还的随从是一定会失去所有光环效果的
			for aura, receiver in auras_Receivers: removefrom(receiver, aura.receivers)
			self.Game.minionSwitchSide(self, activity="Return")
		else:
			for aura, receiver in auras_Receivers:
				if aura.on and aura.applicable(self): receiver.effectBack2List()
				else: removefrom(receiver, aura.receivers)

		self.calcStat(prevHealth=prevHealth)
		if self.btn: self.btn.effectChangeAni()
		self.decideAttChances_base()

	"""target在不包含目标时为一个空tuple，而有目标时则是列表"""
	#打出不同种类随从的扳机响应总结：抉择类，休眠随从进场时都会直接变化。但是它们都可以正常触发使用牌和召唤随从扳机。
	#但是休眠物在触发扳机时，涉及到改变召唤物的扳机不会对其生效，如buff召唤物的效果
	#随从进场后得到的随从会被记录入打出的牌里面。打出抉择变形类随从，剽窃得到变形后的随从；剽窃得到的休眠随从也是原随从。
	#这是因为游戏中休眠随从实际上也没有变成新的object，而是随从类型不变，加上了一个休眠的标签而已。所以打出和召唤休眠随从只在接受其他效果影响时与正常随从不同。
	#打出和复活被禁锢的阳鳃鱼人甚至都可以触发鱼人招潮者的buff扳机。
	#打出的抉择变形类随从和战吼把自己变形的随从都由变形后的随从触发狙击。说明”使用一张牌后“扳机跟踪的是cardinPlay.无论各效果如何对其变形，都可以保证跟踪。
	#综上所述，抉择变形类随从和休眠随从只是在入场时进行变形，其他结算与正常随从的打出基本一致。打出牌的记录会记录随从入场时是什么牌。
	def played(self, target=(), choice=0, mana=0, posinHand=-2, comment=""):
		game, ID, GUI, numTargetsNeeded = self.Game, self.ID, self.Game.GUI, self.numTargetsNeeded(choice)
		self.dmgTaken = 0 # 即使该随从在手牌中有受伤，打出时仍会重置为无伤状态。
		# 此时，随从可以开始建立光环，建立侦听，同时接受其他光环。例如： 打出暴风城勇士之后，光环在Illidan的召唤之前给随从加buff，同时之后打出的随从也是先接受光环再触发Illidan。
		#德鲁伊的抉择变形随从已经变形为其他随从。
		#然后触发“每当你使用一张xx牌”的扳机,如伊利丹，任务达人，无羁元素和魔能机甲等。伊利丹召唤的随从可以插入召唤和飞刀的结算
		#然后触发“每当你召唤一个xx随从”的扳机.如鱼人招潮者等。
		#目前没有打出和召唤扳机对随从进行变形的机制
		obj2Appear = self.appears_fromPlay(choice) #只有休眠随从的outside和inside不一致。
		game.sendSignal("CardPlayed", ID, obj2Appear, target, mana, "Minion", choice)
		game.sendSignal("ObjSummoned", ID, obj2Appear, target, mana, "Minion")
		# 过载结算
		if overload := self.overload: game.Manas.overloadMana(overload, ID)
		silenced = self.silenced
		game.gathertheDead() #战吼前的死亡结算，暂不处理胜负问题。可以插入亡语结算，达到女王抢走这个随从等效果。
		"""随从战吼、连击、抉择、流放的结算"""
		# 目标发射扳机只在战吼触发前检测一次，之后的第二次战吼会重复对此目标施放。同时战吼是否两次的检测也在战吼之前检测
		# 如果战吼之前市长和铜须等已经离场，则没有事发生。市长只影响初始目标的选择。玩家的其他选择，如发现和抉择都不会受影响
		#target的形式有[target1, target2, ...], (target,), ()
		target = game.try_RedirectEffectTarget("EffectTarget?", self, target, choice)
		# 随从在打出过程的第一次死亡结算之前检测自己是否被沉默。只有没有被沉默的时候才会结算打出效果
		if not silenced and not (numTargetsNeeded and not target):
			num, rules = 1, game.rules[ID]
			if ("~Battlecry" in self.index and rules["Battlecry x2"] > 0) or ("~Combo" in self.index and rules["Combo x2"] > 0):
				num = 2
			for _ in range(num):
				if GUI and "~Battlecry" in self.index: GUI.battlecryAni(obj2Appear)
				#在这里检测随从是否在战吼之间发生了变形，实际上只有战吼把自己变形的随从会调用到break。
				#休眠随从在进场时即变形为休眠体，game.cardinPlay和form2Appear都是Dormant。
				if obj2Appear is game.cardinPlay: self.playedEffect(target, "", choice, posinHand)
				else: break #当一个随从在战吼之前不再是正在打出的卡牌，则只能是因为自己的上一次战吼将自己变形为其他随从。战吼会中断
			game.gathertheDead()
		"""随从召唤后和打出后的结算"""
		#假设打出的随从被对面控制的话仍然会计为我方使用的随从。
		#抉择变形随从触发剽窃时得到变形后的随从，但是无面操纵者打出并变形后，剽窃依然得到无面。
		if game.cardinPlay.onBoard:
			game.Counters.handleGameEvent("Summon", game.cardinPlay, game.cardinPlay.ID)
			game.sendSignal("ObjBeenSummoned", game.cardinPlay.ID, game.cardinPlay, None, 0, "Minion")
		#使用后步骤需要处理预检测扳机，所以在Game.playMinion中继续结算
		return obj2Appear


#德鲁伊的抉择变形随从和打出时自动休眠的随从的入场函数需要专门处理，由played中appears_fromPlay调用
def appears_fromPlay_Druid(self, choice, forms):
	if choice < 0: form = forms[-1]
	elif choice >= len(forms) - 2: form = forms[-2]
	else: form = forms[choice]
	self.Game.transform(self, newObj := form(self.Game, self.ID))
	return newObj



class Hero(Card):
	category, health, heroPower = "Hero", 30, None
	def __init__(self, Game, ID, statsEffects=''):
		super().__init__(Game, ID)
		self.attChances_base, self.attChances_extra = 1, 0
		self.pos = self.ID
		self.effects = {"Windfury": 0, "Frozen": 0, "Temp Stealth": 0,
						 "Enemy Effect Evasive": 0, "Cost Health Instead": 0, "Unplayable": 0,
						#SV effects
						 "Enemy Effect Damage Immune": 0, "Can't Be Attacked": 0, "Next Damage 0": 0,
						"Deal Damage 0": 0,  "Draw to Win": 0,
						 }

	"""Handle hero's attacks, attack chances, attack chances and frozen."""
	def turnStarts(self, turn2Start):
		super().turnStarts(turn2Start)
		if turn2Start == self.ID:
			self.losesEffect("Temp Stealth", 0, removeEnchant=True)
			effects = self.Game.rules[self.ID]
			if effects["Immune2NextTurn"] > 0:
				self.losesEffect("Immune", amount=effects["Immune2NextTurn"])
				effects["Immune2NextTurn"] = 0
			if effects["Evasive2NextTurn"] > 0:
				self.losesEffect("Evasive", amount=effects["Evasive2NextTurn"])
				effects["Evasive2NextTurn"] = 0

			self.usageCount = self.attChances_extra = 0
			self.decideAttChances_base()
		self.calcStat()

	def turnEnds(self, turn2End):
		super().turnEnds(turn2End)
		effects = self.Game.rules[self.ID]
		if effects["ImmuneThisTurn"] > 0:
			self.losesEffect("Immune", amount=effects["ImmuneThisTurn"])
			effects["ImmuneThisTurn"] = 0
		#一个角色只有在自己的回合结束时有剩余的攻击机会才能解冻
		if turn2End == self.ID and self.effects["Frozen"] > 0 and self.attChances_base + self.attChances_extra > self.usageCount:
			self.losesEffect("Frozen", 0)

		self.usageCount = self.attChances_extra = 0
		self.calcStat()
		if self.btn: self.btn.effectChangeAni()
		
	def losesArmor(self, armor, allArmor=False, dueToDamage=False):
		if allArmor:
			prevArmor, self.armor = self.armor, 0
			if prevArmor: self.Game.sendSignal("ArmorLost", self.ID, self, None, prevArmor)
		else:
			self.armor -= (armor := min(armor, self.armor))
			self.Game.sendSignal("ArmorLost", self.ID, self, None, armor)
		#英雄在没有受到伤害的情况下失去护甲时才会调用，不然直交由takesDamage函数处理
		if not dueToDamage and self.btn: self.btn.statChangeAni(action="armorChange")
	
	"""Handle hero's being selectable by subjects or not. And hero's availability for battle."""
	def canAttack(self):
		return self.actionable() and self.attack > 0 and self.effects["Frozen"] < 1 \
				and self.attChances_base + self.attChances_extra > self.usageCount

	def canAttackTarget(self, target):
		#如果携带有不能攻击敌方英雄的武器，则目标不可以是英雄
		return self.canAttack() and target.onBoard and target.ID != self.ID and target.notHiddenfromAttack() \
			   and not (target.category == "Hero" and any(weapon.effects["Can't Attack Heroes"] > 0 for weapon in self.Game.weapons[self.ID])) \
				and ((target.category == "Minion" and target.effects["Taunt"] > 0)
						or not any(obj is not target and obj.effects["Taunt"] > 0 and obj.notHiddenfromAttack() for obj in target.Game.minions[target.ID])
						or self.Game.rules[self.ID]["Ignore Taunt"] > 0)

	#Heroes don't have Lifesteal.
	def tryLifesteal(self, damage, damageType="None"):
		pass

	def takesDamage(self, subject, damage, damageType="None"): #正常情况下不会发生对不是场上英雄的英雄牌造成伤害的情况
		game = self.Game
		if game.rules[self.ID]["Immune"] < 1:  # 随从首先结算免疫和圣盾对于伤害的作用，然后进行预检测判定
			if "Next Damage 0" in self.effects and self.effects["Next Damage 0"] > 0:
				damage = self.effects["Next Damage 0"] = 0
			if damageType == "Ability" and "Enemy Effect Damage Immune" in self.effects \
				and self.effects["Enemy Effect Damage Immune"] > 0:
				damage = 0
			if subject and "Deal Damage 0" in subject.effects and subject.effects["Deal Damage 0"] > 0:
				damage = 0
			if damage > 0:
				damageHolder = [damage]
				game.sendSignal("FinalDmgonHero?", self.ID, subject, self, damageHolder)
				damage = damageHolder[0]
				if damage > 0:
					if self.armor > damage: self.losesArmor(damage, dueToDamage=True)
					else:
						self.dmgTaken += damage - self.armor
						self.losesArmor(0, allArmor=True, dueToDamage=True)
					game.Counters.handleGameEvent("Damage", game.genLocator(subject), game.genLocator(self), damage)
					self.calcStat("damage", num2=-damage)
			else: #是否应该把这个东西挪到与dealsDamage中的两个信号发出一致的地方
				game.sendSignal("HeroTakes0Dmg", game.turn, subject, self)
				game.sendSignal("HeroTook0Dmg", game.turn, subject, self)
		else: damage = 0
		return damage

	#def healthReset(self, health, zeroDmgTaken=False):
	#	healthChanged = health != self.health
	#	self.health = health
	#	if health_max: self.health_max = health_max
	#	self.dmgTaken = self.health_max - self.health
	#	self.calcStat("buffDebuff")

	#专门被英雄牌使用，加拉克苏斯大王和拉格纳罗斯都不会调用该方法。
	def played(self, target=(), choice=0, mana=0, posinHand=-2, comment=""): #英雄牌使用目前不存在触发发现的情况
	#使用阶段
		#英雄牌替换出的英雄的生命值，护甲和攻击机会等数值都会继承当前英雄的值。
		game, ID, GUI = self.Game, self.ID, self.Game.GUI
		# 新技能必须存放起来，之后英雄还有可能被其他英雄替换，但是这个技能要到最后才登场。
		oldHero, oldPower, newPower = game.heroes[ID], game.powers[ID], power(game, ID) if (power := self.heroPower) else None
		self.onBoard, oldHero.onBoard, self.pos, self.usageCount = True, False, ID, oldHero.usageCount #hero.pos方便定义(i, where)
		self.armor, self.dmgTaken = oldHero.armor, oldHero.dmgTaken
		#英雄牌进入战场。（本来是应该在使用阶段临近结束时移除旧英雄和旧技能，但是为了方便，在此时执行。）
		#继承旧英雄的生命状态和护甲值。此时英雄的被冻结和攻击次数以及攻击机会也继承旧英雄。
		if newPower: oldPower.disappears() #清除旧的英雄技能。
		while oldHero.auraReceivers: oldHero.auraReceivers[0].effectClear() #旧英雄在消失前需要归还其所有的光环buff效果
		# 英雄替换。如果后续有埃克索图斯再次替换英雄，则最后的英雄是拉格纳罗斯。
		game.heroes[ID], game.powers[ID] = self, None
		if GUI: GUI.showOffBoardTrig(self, animationType='')
		self.calcStat()
		#使用时步骤，触发“每当你使用一张xx牌时”的扳机。
		game.sendSignal("CardPlayed", ID, self, None, mana, "Hero", choice)
		#英雄牌的最大生命值和现有生命值以及护甲被设定继承旧英雄的数值。并获得英雄牌上标注的护甲值。
		self.giveHeroAttackArmor(ID, armor=type(self).armor)
		game.sendSignal("HeroAppears", ID, None, self)
		#使用阶段结束，进行死亡结算，此时尚不进行胜负判定。
		game.gathertheDead()
		#获得新的英雄技能。注意，在此之前英雄有可能被其他英雄代替，如伊利丹飞刀打死我方的管理者埃克索图斯。
			#埃克索图斯可以替换英雄和英雄技能，然后本英雄牌在此处开始结算，再次替换英雄技能为正确的英雄牌技能。
		game.powers[ID] = newPower
		if GUI: GUI.heroZones[ID].heroReplacedAni(oldHero, oldPower)
		newPower.appears()
		#视铜须等的存在而结算战吼次数以及具体战吼。目前的英雄卡一定是有战吼的
		#不用返回主体，但是当沙德沃克调用时playedEffect函数的时候需要。
		if game.rules[ID]["Battlecry x2"] > 0:
			self.playedEffect((), "", choice)
		self.playedEffect((), "", choice)
		self.decideAttChances_base()
		#结算阶段结束，处理死亡，此时尚不进行胜负判定。
		game.gathertheDead()

	#可以是英雄牌被其他牌打出时替换当前英雄，也可以是炎魔之王拉格纳罗斯替换英雄，此时没有战吼。
	#炎魔之王变身不会摧毁玩家的现有装备和奥秘。只会移除冰冻，免疫和潜行等状态，并清除玩家的护甲。
	def replaceHero(self, fromHeroCard=False):
		#假设直接替换的英雄不会继承之前英雄获得的回合内攻击力增加。
		game, ID, GUI = self.Game, self.ID, self.Game.GUI
		oldHero, oldPower, newPower = game.heroes[ID], game.powers[ID], power(game, ID) if (power := self.heroPower) else None
		oldHealth = oldHero.health
		self.onBoard, oldHero.onBoard, self.pos, self.usageCount = True, False, ID, oldHero.usageCount

		if newPower: oldPower.disappears()
		while oldHero.auraReceivers: oldHero.auraReceivers[0].effectClear()

		self.health = oldHero.health #让英雄直接继承当前的生命值。然后再检测这个值是否会变化
		if fromHeroCard: self.dmgTaken, self.armor = oldHero.health_max - oldHero.health, oldHero.armor
		else: #英雄牌被其他牌打出时不会取消当前玩家的免疫状态
			self.losesArmor(0, allArmor=True) #被英雄牌以外的方式替换时，护甲会被摧毁
			# Hero's immune state is gone, except that given by Mal'Ganis
			effects = game.rules[ID]
			effects["Immune"] -= effects["Immune2NextTurn"] + effects["ImmuneThisTurn"]
			effects["ImmuneThisTurn"] = effects["Immune2NextTurn"] = 0
		game.heroes[ID] = self
		if newPower: game.powers[ID] = newPower
		if GUI: GUI.heroZones[ID].heroReplacedAni(oldHero, oldPower)
		self.calcStat()
		if self.btn: self.btn.effectChangeAni()

		game.sendSignal("HeroAppears", ID, None, self)


class Weapon(Card):
	category, deathrattle = "Weapon", None
	def __init__(self, Game, ID, statsEffects=''):
		super().__init__(Game, ID)
		self.effects = {"Lifesteal": 0, "Poisonous": 0, "Windfury": 0, "Immune": 0,
						 "Sweep": 0, "Cost Health Instead": 0, "Can't Attack Heroes": 0, "Unplayable": 0,
						 }
		cardType = type(self)
		self.setEffects_fromStr()
		if cardType.deathrattle: self.deathrattles = [cardType.deathrattle(self)]
		if cardType.aura: self.auras = [cardType.aura(self)]

	"""Handle weapon entering/leaving board/hand/deck"""
	#武器与随从的区别在于武器在打出过程中入场时appears和setasNewWeapon是会开的，尽管变形出现和装备时一起结算
	#只有最终设为setasNewWeapon时onBoard才会变为True
	def appears(self, firstTime=False):
		# 注意，此时武器还不能设为onBoard,因为之后可能会涉及亡语随从为英雄装备武器。
		# 尚不能因为武器标记为onBoard而调用其destroyed。
		self.inHand = self.inDeck = self.dead = False
		self.mana = self.mana_0
		if self.btn: #需要变形过程中前后携带的btn和btn.card正确
			self.btn.isPlayed, self.btn.card = True, self
		for trig in self.trigsBoard + self.deathrattles: trig.connect()

	def setasNewWeapon(self):
		game, self.onBoard = self.Game, True
		# 武器被设置为英雄的新武器，触发“每当你装备一把武器时”的扳机。
		# 因为武器在之前已经被添加到武器列表，所以sequence需要-1，不然会导致错位
		self.seq = len(game.minions[1]) + len(game.minions[2]) + len(game.weapons[1]) + len(game.weapons[2]) - 1
		self.calcStat()
		if self.btn:
			self.btn.placeIcons()
			self.btn.effectChangeAni()
		if self.effects["Windfury"] > 0: game.heroes[self.ID].decideAttChances_base()
		game.sendSignal("WeaponAppears", self.ID, None, self)

	def disappears(self, deathrattlesStayArmed=False, disappearResponse=True):
		if self.onBoard:  # 只有装备着的武器才会触发，以防连续触发。
			self.onBoard = False
			if self.effects["Windfury"] > 0: self.Game.heroes[self.ID].decideAttChances_base()
			self.Game.heroes[self.ID].calcStat()
			for trig in self.trigsBoard: trig.disconnect()
			if not deathrattlesStayArmed:
				for trig in self.deathrattles: trig.disconnect()
			self.Game.sendSignal("WeaponDisappears", self.ID, None, self)

	"""Handle the mana, durability and stat of weapon."""
	# This method is invoked by Hero class, not a listner.
	def losesDurability(self):
		if self.effects["Immune"] < 1:
			self.health -= 1
			self.dmgTaken += 1 #可以省掉calcStat
			if self.btn: self.btn.statChangeAni(action="damage")

	"""Handle the weapon being played/equipped."""
	def played(self, target=(), choice=0, mana=0, posinHand=-2, comment=""):
		game, numTargetsNeeded = self.Game, self.numTargetsNeeded(choice)
		# 连接扳机。比如公正之剑可以触发伊利丹的召唤，这个召唤又反过来触发公正之剑
		self.appears()  #武器已进入Game.weapons列表，但是此时onBoard还是False
		# 注意，暂时不取消已经装备的武器的侦听，比如两把公正之剑可能同时为伊利丹召唤的元素buff。
		# 使用时步骤，触发“每当你使用一张xx牌”的扳机，如伊利丹和无羁元素。
		game.sendSignal("CardPlayed", self.ID, self, target, 0, "Weapon", choice)
		# 结算过载。
		if overload := self.overload: game.Manas.overloadMana(overload, self.ID)
		# 使用阶段结束，处理亡语，暂不处理胜负问题。
		# 打出武器牌时，如伊利丹飞刀造成了我方佛丁的死亡，则其装备的灰烬使者会先于该武器加入Game.weapons[ID]。
		# 之后在结算阶段的武器正式替换阶段，打出的该武器顶掉灰烬使者。最终装备的武器依然是打出的这把武器。
		game.gathertheDead()  # 此时被替换的武器先不视为死亡，除非被亡语引起的死亡结算先行替换（如佛丁）。
		# 结算阶段
		target = game.try_RedirectEffectTarget("EffectTarget?", self, target, choice)
		if not numTargetsNeeded or target:
			# 根据铜须的存在情况来决定战吼的触发次数。不同于随从，武器的连击目前不会触发
			if game.rules[self.ID]["Battlecry x2"] > 0:
				self.playedEffect(target, "", choice, posinHand)
			self.playedEffect(target, "", choice, posinHand)
		# 消灭旧武器，并将列表前方的武器全部移除。
		for weapon in game.weapons[self.ID]:
			if weapon is not self: weapon.disappears(deathrattlesStayArmed=True)  # 触发“每当你的一把武器被摧毁时”和“每当你的一把武器离场时”的扳机，如南海船工。
		# 打出的这把武器会成为最后唯一还装备着的武器。触发“每当你装备一把武器时”的扳机，如锈水海盗。
		self.setasNewWeapon()  # 此时打出的武器的onBoard才会正式标记为True
		# 结算阶段结束，处理亡语。（此时的亡语结算会包括武器的亡语结算。）
		game.gathertheDead()


class Power(Card):
	category = "Power"
	def __init__(self, Game, ID, powerReplaced=None):
		super().__init__(Game, ID)
		# 额外的英雄技能技能只有考达拉幼龙和要塞指挥官可以更改。
		# 技能能否使用，需要根据已使用次数和基础机会和额外机会的和相比较。
		self.onBoard = True
		self.effects = {"Lifesteal": 0, "Poisonous": 0,

						"Damage Boost": 0, "Can Target Minions": 0,
						"Cost Health Instead": 0, "Unplayable": 0,
						}
		self.setEffects_fromStr()
		self.powerReplaced = powerReplaced

	def dealsDmg(self): return False
	def likeSteadyShot(self): return False
	def countDamageDouble(self):
		return sum(minion.effects["Power Heal&Dmg x2"] > 0 for minion in self.Game.minions[self.ID])

	def calcDamage(self, base):
		return (base + self.effects["Damage Boost"] + self.Game.rules[self.ID]["Power Damage"]) * (2 ** self.countDamageDouble())

	def turnStarts(self, turn2Start):
		super().turnStarts(turn2Start)
		if turn2Start == self.ID:
			self.usageCount = 0
			if self.btn: self.btn.checkHpr()

	def turnEnds(self, turn2End):
		super().turnEnds(turn2End)
		if turn2End == self.ID: self.usageCount = 0

	def appears(self):
		self.usageCount = 0
		for trig in self.trigsBoard: trig.connect()
		if self.btn:
			self.btn.isPlayed, self.btn.card = True, self
			self.btn.placeIcons()
			self.btn.effectChangeAni()
		self.Game.sendSignal("PowerAppears", self.ID, None, self)
		self.Game.Manas.calcMana_Powers()

	def disappears(self):
		for trig in self.trigsBoard: trig.disconnect()
		for manaMod in self.manaMods: manaMod.getsRemoved()
		self.manaMods = []

	def replacePower(self):
		powers, ID = self.Game.powers, self.ID
		GUI = self.Game.GUI
		if powers[ID]:
			oldPower = powers[ID]
			if GUI and oldPower.btn and oldPower.btn.np: GUI.seqHolder[-1].append(GUI.FUNC(oldPower.btn.np.detachNode))
			powers[ID].disappears()
		powers[ID] = self
		if GUI: GUI.heroZones[ID].placeCards()
		self.appears()

	def chancesUsedUp(self):
		return self.Game.rules[self.ID]["Power Chance Inf"] < 1 \
			   and self.usageCount >= (1 + (self.Game.rules[self.ID]["Power Chance 2"] > 0))

	def available(self):  # 只考虑没有抉择的技能，抉择技能需要自己定义
		return not self.chancesUsedUp() and (not self.numTargetsNeeded() or self.findTargets())

	def effect_wrapper(self, target=(), choice=0):
		if target: #英雄杀死随从在死亡结算之前。应该只是检测受到伤害和消灭的扳机
			freeze = (rules := self.Game.rules[self.ID])["Power Freezes Target"]
			if sweep := rules["Power Sweep"] and len(target) == 1 and target[0].catgory == "Minion":
				if neighbors := self.Game.neighbors2(obj := target[0])[0]:
					target = [obj] + neighbors
			self.effect(target, choice)
			if freeze: self.freeze(target)
		else: self.effect((), choice)

	def effect(self, target, choice=0): pass #

	def assistCreateCopy(self, Copy):
		Copy.powerReplaced = self.powerReplaced.createCopy(Copy.Game)


class Spell(Card):
	category = "Spell"
	def __init__(self, Game, ID, statsEffects=''):
		super().__init__(Game, ID)
		self.effects = {"Poisonous": 0, "Lifesteal": 0,
						"Cost Health Instead": 0, "Unplayable": 0,
						}
		self.setEffects_fromStr()
		if statsEffects:
			mana_0, attack_0, health_0, *_ = statsEffects.split(",")
			self.mana_0, self.attack_0, self.health_0 = int(mana_0), int(attack_0), int(health_0)
	def available(self):
		return not self.numTargetsNeeded() or self.selectableCharExists()

	def countDamageDouble(self):
		return sum(minion.effects["Spell Heal&Dmg x2"] > 0 for minion in self.Game.minions[self.ID])

	def calcDamage(self, base):
		return (base + self.countSpellDamage()) * (2 ** self.countDamageDouble())

	# 用于由其他卡牌释放法术。这个法术会受到风潮和星界密使的状态影响，同时在结算完成后移除两者的状态。
	# 这个由其他卡牌释放的法术不受泽蒂摩的光环影响。目标随机，也不触发目标扳机。
	# 随机施放的法术仍然需要检测目标的可选择性，如免疫，潜行和魔免等，同时如果没有目标，则指向性法术整体失效，没有任何效果会结算
	# 由其他卡牌释放的法术结算相对玩家打出要简单，只需要结算过载，双生法术， 重复释放和使用后的扳机步骤即可。
	def cast(self, prefered=None, target=()): #target is designated target, only applicable to Sunwing Swquaker so far
		game, GUI = self.Game, self.Game.GUI
		choice = self.pickRandomChoice()
		if (numTargets := self.numTargetsNeeded(choice)) and not target: #需要目标，同时又没有预先指定目标
			target = self.randomTargets(numTargets, choice=choice, prefered=prefered)

		if GUI:
			GUI.showOffBoardTrig(self)
			game.eventinGUI(self, eventType="CastSpell", target=target)
			GUI.resetSubTarColor(None, target)

		if not numTargets or target:
			# 在法术要施放两次的情况下，第二次的目标仍然是第一次时随机决定的
			for _ in range(2 if game.rules[self.ID]["Spells x2"] > 0 else 1):
				self.beforeSpellEffective()
				self.playedEffect(target, "byOthers", choice)
		# 使用后步骤，但是此时的扳机只会触发星界密使和风潮的状态移除。这个信号不是“使用一张xx牌之后”的扳机。
		game.sendSignal("SpellBeenCast", self.ID, self, None, 0, "byOthers")

	def beforeSpellEffective(self):
		if overload := self.overload: self.Game.Manas.overloadMana(overload, self.ID)

	# 泽蒂摩加风潮，当对泽蒂摩使用Mutate之后，Mutate会连续两次都进化3个随从
	# 泽蒂摩是在法术开始结算之前打上标记,而非在连续两次之间进行判定。
	# comment = "InvokedbyAI", "Branching-i", ""
	def played(self, target=(), choice=0, mana=0, posinHand=-2, comment=""):
		game, ID, GUI = self.Game, self.ID, self.Game.GUI
		numTargetsNeeded = self.numTargetsNeeded(choice)
		if GUI: GUI.showOffBoardTrig(self, isSecret=self.race == "Secret")
		#触发“每当你使用一张牌”的扳机，然后进行随从死亡的判定。可以出现飞刀/紫罗兰老师的combo
		game.sendSignal("CardPlayed", ID, self, target, mana, "Spell", choice)
		game.gathertheDead()

		# 进行目标的随机选择和扰咒术的目标改向判定。
		target = game.try_RedirectEffectTarget("EffectTarget?", self, target, choice)
		if not numTargetsNeeded or target:
			sweep = game.rules[ID]["Spells Sweep"] > 0 #只在法术生效之前检测泽蒂摩的光环是否存在。
			for _ in range(2 if game.rules[ID]["Spells x2"] > 0 else 1):
				self.beforeSpellEffective() #过载/法术双生在此处理
				if len(target) == 1 and target[0].category == "Minion" and target[0].onBoard \
						and sweep and (neighbors := game.neighbors2(target[0])[0]):
					self.playedEffect(target, comment, choice, posinHand)
					for minion in neighbors: self.playedEffect([minion], comment, choice, posinHand) # 对相邻的随从也释放该法术。
				else: self.playedEffect(target, comment, choice, posinHand)
		# 仅触发风潮，星界密使等的光环移除扳机。“使用一张xx牌之后”的扳机不在这里触发，而是在Game的playSpell函数中结算。
		game.sendSignal("SpellBeenCast", self.ID, self, target, 0, "", choice)
		game.gathertheDead()  # At this point, the minion might be removed/controlled by Illidan/Juggler combo.
		# 如果法术具有回响，则将回响牌置入手牌中。因为没有牌可以让法术获得回响，所以可以直接在法术played()方法中处理echo
		# if "~Echo" in self.index:
		#	echoCard = type(minion)(self, game.turn)
		#	trig = Trig_Echo(echoCard)
		#	echoCard.trigsHand.append(trig)
		#	game.Hand_Deck.addCardtoHand(echoCard, ID)

	def afterDrawingCard(self):
		pass


class Secret(Spell): #法术中有奥秘和任务两个子类，放在race中。Secret/Quest/Sidequest/Questline不会与随从的race发生混淆
	race = "Secret"
	def available(self):
		return self.Game.Secrets.areaNotFull(self.ID) and not self.Game.Secrets.sameSecretExists(self, self.ID)

	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		secretHD = self.Game.Secrets
		if secretHD.areaNotFull(self.ID) and not secretHD.sameSecretExists(self, self.ID):
			secretHD.secrets[self.ID].append(self)
			for trig in self.trigsBoard: trig.connect()
			if self.Game.GUI: self.Game.GUI.heroZones[self.ID].placeSecrets()
		# secretHD.initSecretHint(self) #Let the game know what possible secrets each player has
		return None

class Quest(Spell):
	race, numNeeded, newQuest, reward = "Quest", 1, None, None
	# Upper limit of secrets and quests is 5. There can only be one main quest/questline, but multiple different sidequests
	def available(self):
		secretZone = self.Game.Secrets
		if secretZone.areaNotFull(self.ID):
			if self.race == "Sidequest": return all(quest.name != self.name for quest in secretZone.sideQuests[self.ID])
			else: return not secretZone.mainQuests[self.ID] #Only available when there is no other Legendary quests/questlines
		return False

	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		secretZone = self.Game.Secrets
		if secretZone.areaNotFull(self.ID):
			if self.race == "Sidequest":
				if all(quest.name != self.name for quest in secretZone.sideQuests[self.ID]):
					secretZone.sideQuests[self.ID].append(self)
					for trig in self.trigsBoard: trig.connect()
			elif not secretZone.mainQuests[self.ID]: # The quest is a main Quest/Questline
				secretZone.mainQuests[self.ID].append(self)
				for trig in self.trigsBoard: trig.connect()
			if self.Game.GUI: self.Game.GUI.heroZones[self.ID].placeSecrets()
		return None


class Option:
	name = description = effect = ""
	mana = attack = health = -1
	isLegendary = False
	spell = None
	def __init__(self, keeper=None):
		self.keeper, self.category = keeper, "Option"
		self.btn = None
	
	def available(self): return True