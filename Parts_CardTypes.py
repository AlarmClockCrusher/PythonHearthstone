from Parts_ConstsFuncsImports import *
from Parts_TrigsAuras import ManaMod

#不能同时定义身材变化和效果变化。类型有buffDebuff/statReset/effectGain
#creator remembers what type card gave the enchantment,
class Enchantment:
	def __init__(self, attGain=0, healthGain=0, attSet=-1, healthSet=-1, effGain='', effNum=1,
				 until=-1, source=None, name=None):
		self.source, self.name = source, name
		self.attGain, self.healthGain = attGain, healthGain
		self.attSet, self.healthSet = attSet, healthSet
		self.effGain, self.effNum = effGain, effNum
		self.until = until # -1 is permanent, 0 is until the end of turn, 1/2 (3/4) is until start (end) of player 1/2's turn

	def addto(self, keeper): keeper.enchantments.append(self)

	def text(self):
		s = self.name.name + '\n' #self.name is actually the class object that gives this effect
		if self.effGain: s += self.effGain + ' ' + str(self.effNum)
		else:
			if self.attGain: s += ('+%d'%self.attGain if self.attGain > 0 else str(self.attGain)) + ''
			if self.attSet: s += ("=>%d"%self.attSet if self.attSet > -1 else '')
			s += '/'
			if self.healthGain: s += ('+%d'%self.healthGain if self.healthGain > 0 else str(self.healthGain)) + ' '
			if self.healthSet: s += ("=>%d"%self.healthSet if self.healthSet > -1 else '')
		return s

	#只负责处理身材数值的上限，对于随从的实际当前生命值不做处理
	#healthGain都是正值，以目前的结算机制不可能有负值
	def handleStatMax(self, keeper):
		keeper.attack += self.attGain
		keeper.health_max += self.healthGain
		if self.attSet > -1: keeper.attack = self.attSet
		if self.healthSet > -1: keeper.health_max = self.healthSet
		keeper.health_max = max(0, keeper.health_max)

	def handleEffect(self, keeper): #只有在随从复制时使用
		if self.effGain: keeper.effects[self.effGain] += self.effNum

	#如果Enchantment要失效了，则需要它自行
	def handleExpiring(self, keeper):
		if self.effGain: keeper.losesEffect(self.effGain, self.effNum)

	def selfCopy(self, recipient):
		return type(self)(self.attGain, self.healthGain, self.attSet, self.healthSet, self.effGain, self.effNum,
						  self.until, self.source, self.name)

class Enchantment_Cumulative(Enchantment):
	def addto(self, keeper):
		if enchant := next((enchant for enchant in keeper.enchantments \
							if enchant.name == self.name and enchant.effGain == self.effGain), None):
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
	Class = name = index = description = ''
	category = race = school = effects = ''
	mana = attack = health = durability = armor = 0
	requireTarget = False
	aura = trigBoard = trigHand = trigDeck = None
	options, overload = (), 0
	def __init__(self, Game, ID):
		cardType = type(self)
		self.Game, self.ID = Game, ID
		self.Class, self.name, self.category = cardType.Class, cardType.name, cardType.category
		self.mana, self.school, self.race = cardType.mana, cardType.school, cardType.race
		self.description, self.index = cardType.description, cardType.index
		self.options = [option(self) for option in cardType.options]

		self.onBoard = self.inHand = self.inDeck = self.dead = False
		self.enterBoardTurn = self.enterHandTurn = 0
		self.seq, self.pos = -1, -2
		self.usageCount, self.attChances_base, self.attChances_extra = 0, 1, 0
		self.progress = 0
		
		self.attack_0 = self.attack = cardType.attack
		self.health_0 = self.health = self.health_max = (cardType.health if cardType.health > 0 else cardType.durability)
		self.armor, self.dmgTaken = cardType.armor, 0 #Real health is health_max-dmgTaken
		#会改变dmgTaken的过程只有takesDamage, getsHealed, statReset, losesDurability, getsSilenced, replaceHero
		#会调用dmgTaken的过程只有calcStat, selfCopy, createCopy

		self.auras, self.auraReceivers, self.manaMods, self.deathrattles, self.enchantments = [], [], [], [], []
		self.trigsBoard = [cardType.trigBoard(self)] if cardType.trigBoard else []
		self.trigsHand = [cardType.trigHand(self)] if cardType.trigHand else []
		self.trigsDeck = [cardType.trigDeck(self)] if cardType.trigDeck else []

		self.effects = {}
		self.effectViable = self.evanescent = False
		#用于跟踪卡牌的可能性
		self.creator, self.tracked, self.possi = None, False, (cardType,)
		self.btn = None

	def getMana(self): return self.mana
	def becomeswhenPlayed(self, choice=0): return self, self.mana
	def getTypewhenPlayed(self): return self.category
	def needTarget(self, choice=0): return type(self).requireTarget
	def selfManaChange(self): pass
	#This is for battlecries with specific target requirement.
	def effCanTrig(self): pass
	def checkEvanescent(self): self.evanescent = any(type(trig).changesCard for trig in self.trigsBoard + self.trigsHand)
	def text(self): return ''

	def func(self, target, func, text='', color=white):
		if self == target: self.Game.add2EventinGUI(self, target, textSubject=text, colorSubject=color)
		else: self.Game.add2EventinGUI(self, target, textTarget=text, colorTarget=color)
		func(target)

	#处理卡牌进入/离开 手牌/牌库时的扳机和各个onBoard/inHand/inDeck标签
	def entersHand(self):
		self.inHand = True
		self.onBoard = self.inDeck = False
		self.enterHandTurn = self.Game.numTurn
		for trig in self.trigsHand: trig.connect()
		self.calcStat()
		return self

	def leavesHand(self, intoDeck=False):
		#将注册了的场上、手牌和牌库扳机全部注销。
		for trig in self.trigsBoard[:]:
			trig.disconnect()
			#If the trig is temporary, it will be removed once it leaves hand, whether being discarded, played or shuffled into deck
			if not trig.inherent: self.trigsBoard.remove(trig)
		for trig in self.trigsHand[:]:
			trig.disconnect()
			if not trig.inherent: self.trigsHand.remove(trig)
		self.onBoard = self.inHand = self.inDeck = False
		#无论如果离开手牌，被移出还是洗回牌库，费用修改效果（如大帝-1）都会消失
		for manaMod in self.manaMods[:]: manaMod.getsRemoved()
		self.manaMods = []

	def entersDeck(self):
		self.inDeck = True
		self.onBoard = self.inHand = False
		#Hand_Deck.shuffleintoDeck won't track the mana change.
		self.Game.Manas.calcMana_Single(self)
		for trig in self.trigsDeck: trig.connect()

	def leavesDeck(self, intoHand=True):
		#将注册了的场上、手牌和牌库扳机全部注销。
		for trig in self.trigsDeck[:]: trig.disconnect() #没有给卡牌施加外来扳机的机制
		self.onBoard = self.inHand = self.inDeck = False
		if not intoHand: #离开牌库时，只有去往手牌中时费用修改效果不会丢失。
			for manaMod in self.manaMods[:]: manaMod.getsRemoved()
			self.manaMods = []

	def whenDrawn(self): pass
	def whenDiscarded(self): pass
	#def returnResponse(self): For SV cards

	def turnStarts(self, turn2Start):
		for enchant in self.enchantments:
			if enchant.until == turn2Start: enchant.handleExpiring(self)
		self.enchantments = [enchant for enchant in self.enchantments if enchant.until != turn2Start]

	def turnEnds(self, turn2End):
		for manaMod in self.manaMods[:]: manaMod.turnEnds(turn2End)
		for enchant in self.enchantments:  # 直到回合结束的对攻击力改变效果不论是否是该随从的当前回合，都会消失
			if enchant.until == 0 or enchant.until - 2 == turn2End: enchant.handleExpiring(self)
		self.enchantments = [enchant for enchant in self.enchantments if enchant.until and enchant.until != turn2End]

	"""Handle the target selection. All methods belong to minions. Other types will define their own methods."""
	def available(self): return True

	def targetCorrect(self, target, choice=0):
		return (target.category == "Minion" or target.category == "Hero") and target.onBoard

	def selectablebyBattle(self, subject):
				#攻击目标必须是在场上的没有潜行的敌方随从或英雄
				#被攻击目标必须能够被选择(没有免疫，潜行和“不能被攻击”)的随从或者英雄
				#攻击方如果有无视嘲讽，则不用判定嘲讽问题
		if self.onBoard and self.ID != subject.ID and self.effects["Temp Stealth"] < 1:
			if self.category == "Minion":
				return self.effects["Immune"] + self.effects["Stealth"] + self.effects["Can't Be Attacked"] < 1 \
						and (self.effects["Taunt"] > 0
							or not any(minion.effects["Taunt"] > 0 and minion.effects["Temp Stealth"] + minion.effects["Immune"] + minion.effects["Stealth"] < 1 for minion in self.Game.minionsonBoard(self.ID))
							or self.Game.effects[subject.ID]["Ignore Taunt"] > 0 or (subject.category == "Minion" and subject.effects["Ignore Taunt"]))
			elif self.category == "Hero":
				return self.Game.effects[self.ID]["Immune"] + self.Game.effects[self.ID]["Hero Can't Be Attacked"] < 1 \
						and not (subject.category == "Hero" and any(weapon.effects["Can't Attack Heroes"] > 0 for weapon in self.Game.weapons[subject.ID])) \
						and (not any(minion.effects["Taunt"] > 0 and minion.effects["Temp Stealth"] + minion.effects["Immune"] + minion.effects["Stealth"] < 1 for minion in self.Game.minionsonBoard(self.ID))
							or self.Game.effects[subject.ID]["Ignore Taunt"] > 0 or (subject.category == "Minion" and subject.effects["Ignore Taunt"]))
						#The last 2 lines handle the case of blockage by Taunt minions
		return False

	def canSelect(self, target):
		targets = target if isinstance(target, list) else [target]
		for target in targets:
			targetType = target.category
			selectable = False
			if target.onBoard and targetType in ("Hero", "Minion", "Amulet"):
				if targetType == "Hero":
					#如果英雄是敌方英雄且目前有潜行，免疫，且“不可被敌方效果指定”，则无论什么指向性效果都无法进行选择
					if target.ID != self.ID and self.Game.effects[target.ID]["Immune"] + target.effects["Temp Stealth"] + target.effects["Enemy Effect Evasive"] > 0:
						pass
					#如果subject是法术或者英雄技能，则如果英雄有魔免，或者对方英雄有对对方的魔免，则无法进行选择
					elif (self.category == "Power" or self.category == "Spell") and self.Game.effects[target.ID]["Evasive"] > 0:
						pass
					else: selectable = True #其余情况下可以选择一个英雄
				elif targetType == "Minion":
					#如果目标随从是敌方的，且目前拥有免疫，潜行或者临时潜行，则无法进行选择
					if target.ID != self.ID and target.effects["Immune"] + target.effects["Stealth"] + target.effects["Temp Stealth"] + target.effects["Enemy Effect Evasive"] > 0:
						pass
					#如果subject是法术或者英雄技能，且目标随从有魔免，或者是一个有“对对方魔免”的对方随从，则无法进行选择
					elif (self.category == "Power" or self.category == "Spell") \
						and (target.effects["Evasive"] > 0 or (target.ID != self.ID and target.effects["Enemy Evasive"] > 0)):
						pass
					else: selectable = True
				elif targetType == "Amulet":
					if target.ID != self.ID and target.effects["Enemy Effect Evasive"] > 0:
						pass
					elif self.category == "Spell" and target.effects["Evasive"] > 0:
						pass
					else: selectable = True

			if not selectable: return False
		return True

	def selectableEnemyMinionExists(self, choice=0):
		return any(minion.category == "Minion" and minion.onBoard and self.canSelect(minion) and self.targetCorrect(minion, choice) \
					for minion in self.Game.minions[3-self.ID])

	def selectableFriendlyMinionExists(self, choice=0):
		return any(minion.category == "Minion" and minion.onBoard and self.canSelect(minion) and self.targetCorrect(minion, choice) \
					for minion in self.Game.minions[self.ID])

	def selectableEnemyAmuletExists(self, choice=0):
		return any(minion.category == "Amulet" and minion.onBoard and self.canSelect(minion) and self.targetCorrect(minion, choice) \
					for minion in self.Game.minions[3-self.ID])

	def selectableFriendlyAmuletExists(self, choice=0):
		return any(minion.category == "Amulet" and minion.onBoard and self.canSelect(minion) and self.targetCorrect(minion, choice) \
					for minion in self.Game.minions[self.ID])

	def selectableMinionExists(self, choice=0):
		return self.selectableFriendlyMinionExists(choice) or self.selectableEnemyMinionExists(choice)

	def selectableEnemyExists(self, choice=0):
		hero = self.Game.heroes[3-self.ID]
		return (self.canSelect(hero) and self.targetCorrect(hero, choice)) or self.selectableEnemyMinionExists(choice)

	#There is always a selectable friendly character -- hero.
	def selectableFriendlyExists(self, choice=0): #For minion battlecries, the friendly hero is always selectable
		hero = self.Game.heroes[self.ID]
		return (self.category != "Spell" or self.category != "Power") \
				or (self.canSelect(hero) and self.targetCorrect(hero, choice) or self.selectableFriendlyMinionExists(choice))

	def selectableCharacterExists(self, choice=0):
		return self.selectableFriendlyExists(choice) or self.selectableEnemyExists(choice)

	#For targeting battlecries(Minions/Weapons)
	def targetExists(self, choice=0): return True

	def selectionLegit(self, target, choice=0):
		#抉择牌在有全选光环时，选项自动更正为一个负数。
		if self.Game.effects[self.ID]["Choose Both"] > 0 and type(self).options: choice = -1
		if target: #指明了目标
			#在指明目标的情况下，只有抉择牌的选项是合理的，选项需要目标，目标对于这个选项正确，且目标可选时，才能返回正确。
			return self.needTarget(choice) and self.targetCorrect(target, choice) and self.canSelect(target)
		else: #打出随从如果没有指定目标，则必须是其不要求目标或没有目标。
			return not self.needTarget(choice) or ((self.category == "Minion" or self.category == "Amulet") and not (self.needTarget(choice) and self.targetExists(choice)))

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		return target

	def countSpellDamage(self): #Counting spell damage is independent of card category
		return self.Game.effects[self.ID]["Spell Damage"] + (self.school == "Fire" and self.Game.effects[self.ID]["Fire Spell Damage"])\
				+ sum(minion.effects["Spell Damage"] or (minion.effects["Nature Spell Damage"] and self.school == "Nature")
					  for minion in self.Game.minions[self.ID])

	def dmgtoDeal(self, dmg, role="att"):
		return dmg

	def dmgtoRec(self, dmg, role="def"):
		return dmg

	"""Handle the card doing battle(Minion and Hero)"""
	def decideAttChances_base(self):
		if self.category == "Minion":
			if self.effects["Mega Windfury"] > 0: self.attChances_base = 4
			elif self.effects["Can Attack 3 times"] > 0: self.attChances_base = 3
			elif self.effects["Windfury"] > 0: self.attChances_base = 2
			else: self.attChances_base = 1
			if self.btn: self.btn.effectChangeAni("Exhausted")
		elif self.category == "Hero":
			weapon = self.Game.availableWeapon(self.ID)
			self.attChances_base = 2 if self.effects["Windfury"] > 0 or (weapon and weapon.effects["Windfury"] > 0) else 1
		
	def actionable(self):
		# 不考虑冻结、零攻和自身有不能攻击的debuff的情况。
		if self.category == "Minion":
			# 判定随从是否处于刚在我方场上登场，以及暂时控制、冲锋、突袭等。
			# 如果随从是刚到我方场上，则需要分析是否是暂时控制或者是有冲锋或者突袭。
			# 随从已经在我方场上存在一个回合。则肯定可以行动。
			return self.onBoard and self.ID == self.Game.turn and \
				   (self.enterBoardTurn != self.Game.numTurn or (self.effects["Borrowed"] > 0 or self.effects["Charge"] > 0 or self.effects["Rush"] > 0))
		elif self.category == "Hero": return self.ID == self.Game.turn
		else: return False
		
	#Game.battle() invokes this function.
	#我方有扫荡打击的狂暴者攻击对方相邻的两个狂暴者之一，然后扫荡打击在所有受伤开始之前触发，
	#然后被攻击的那个狂暴者先受伤加攻，然后我方的狂暴者受伤加攻，最后是被AOE波及的那个狂暴者加攻。
	#说明扫荡打击是把相邻的随从列入伤害处理列表 ，主要涉及的两个随从是最先结算的两个，
	#被扫荡打击涉及的两个随从从左到右依次结算。
	def attacks(self, target, useAttChance=True, duetoCardEffects=False):
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
		game.sendSignal("BattleDmg" + target.category, 0, dmgDealer_att, target, subjectAtt, "") #不能把这个东西写入和伤害承受目标判定同时进行的结算，因为存在互相干扰的情况
		if dmgActual := dmgTaker.takesDamage(dmgDealer_att, subjectAtt[0], sendDmgSignal=False, damageType="Battle"):
			dmgList.append((dmgDealer_att, dmgTaker, dmgActual))

		#寻找受到攻击目标的伤害的角色。同理，此时受伤的角色不会发出受伤信号，这些受伤信号会在之后统一发出。
		dmgTaker = game.scapegoat4(self, dmgDealer_def)
		game.sendSignal("BattleDmg" + target.category, 0, target, dmgDealer_def, targetAtt, "") #不能把这个东西写入和伤害承受目标判定同时进行的结算，因为存在互相干扰的情况
		if dmgActual := dmgTaker.takesDamage(dmgDealer_def, targetAtt[0], sendDmgSignal=False, damageType="Battle"):
			dmgList.append((dmgDealer_def, dmgTaker, dmgActual))
		dmg_byDef = dmgActual #The damage dealt by the character under attack
		#如果攻击者的伤害来源（随从或者武器）有对相邻随从也造成伤害的扳机，则将相邻的随从录入处理列表。
		neighbors = []
		if dmgDealer_att.category != "Hero" and dmgDealer_att.effects["Sweep"] > 0 and target.category == "Minion":
			neighbors = game.neighbors2(target)[0] #此时被攻击的随从一定是在场的，已经由Game.battleRequest保证。
			for minion in neighbors:
				dmgTaker = game.scapegoat4(minion, dmgDealer_att)
				#目前假设横扫时造成的战斗伤害都一样，不会改变。毕竟炉石里面没有相似的效果
				if dmgActual := dmgTaker.takesDamage(dmgDealer_att, subjectAtt[0], sendDmgSignal=False, damageType="Ability"):
					dmgList.append((dmgDealer_att, dmgTaker, dmgActual))

		if game.GUI:
			sSubject, sTarget = "-%d"%targetAtt[0] if targetAtt[0] else '', "-%d"%subjectAtt[0] if subjectAtt[0] else ''
			game.eventinGUI(self, eventType="Battle", target=[target]+neighbors, textSubject=sSubject, colorSubject=red,
							textTarget=[sTarget]*(1+len(neighbors)), colorTarget=red, level=1 if duetoCardEffects else 0)
		if dmgDealer_att.category == "Weapon": dmgDealer_att.losesDurability()
		dmg_byAtt = 0 #The damage dealt by the character that attacks
		for dmgDealer, dmgTaker, damage in dmgList:
			#参与战斗的各方在战斗过程中只减少血量，受伤的信号在血量和受伤名单登记完毕之后按被攻击者，攻击者，被涉及者顺序发出。
			game.sendSignal(dmgTaker.category+"TakesDmg", 0, dmgDealer, dmgTaker, damage, "")
			game.sendSignal(dmgTaker.category+"TookDmg", 0, dmgDealer, dmgTaker, damage, "")
			#吸血扳机始终在队列结算的末尾。
			dmgDealer.tryLifesteal(damage, damageType="Battle")
			dmg_byAtt += damage
		#有需要一次性检测伤害总量的扳机，如骑士奥秘“清算”
		if dmg_byAtt: game.sendSignal("DealtDmg", 0, dmgDealer_att, None, dmg_byAtt, "")
		if dmg_byDef: game.sendSignal("DealtDmg", 0, dmgDealer_def, None, dmg_byDef, "")

	def freeze(self, target, add2EventinGUI=True):
		if (target.onBoard or target.inHand) and "Frozen" in target.effects:
			if self.Game.GUI and add2EventinGUI: self.Game.add2EventinGUI(self, target)
			target.effects["Frozen"] = 1
			if target.onBoard and (target.category == "Minion" or target.category == "Hero"):
				target.decideAttChances_base()
				target.Game.sendSignal("CharEffectCheck", target.Game.turn, target, None, 0, "")  # 用于部分光环，如方阵指挥官
			if (target.onBoard or target.inHand) and target.btn: target.btn.effectChangeAni("Frozen")

	def AOE_Freeze(self, targets):
		if targets:
			if self.Game.GUI: self.Game.add2EventinGUI(self, targets)
			for target in targets: self.freeze(target, add2EventinGUI=False)

	# 当随从失去关键字的时候不可能有解冻情况发生。
	#角色失去光环效果时是不涉及移除enchant的。目前会让角色失去effect的情况有:
		#只会失去所有的： 沉默 | 随从的临时免疫和潜行 | 受伤失去圣盾 | 冰冻解除
		#会按数值减少的： 光环效果移除 | 英雄的法强伤害等增益移除
	#amount设为负数或0时表示要移除该特效的全部值，仅限 圣盾|潜行|临时潜行|免疫 使用
	#loseAllEffects=True只在随从被沉默时出现
	def losesEffect(self, name, amount=1, removeEnchant=False, loseAllEffects=False): #当角色失去所有keyWords时，amount需要小于0
		if not self.inDeck:
			hadDivineShield = self.category == "Minion" and self.effects["Divine Shield"] > 0
			if loseAllEffects: #只会在随从被沉默时调用。随从不会与Game.efffects产生关联
				for key in self.effects.keys(): self.effects[key] = 0 #getsSilenced会自行清理enchantments
			else:
				if name in self.effects:
					self.effects[name] = max(0, self.effects[name] - amount) if amount > 0 else 0
				elif name in (effects := self.Game.effects[self.ID]):
					effects[name] = max(0, effects[name] - amount) if amount > 0 else 0
				if removeEnchant: #调用removeEnchant的时候一般都是潜行等只有0/1状态的效果，所以只能进行
					for enchant in self.enchantments[:]:
						if enchant.effGain == name:
							enchant.effGain = ''
							if enchant.attGain == enchant.healthGain == 0 and enchant.attSet == enchant.healthSet == -1:
								removefrom(enchant, self.enchantments)
			if self.onBoard:
				self.decideAttChances_base()
				if hadDivineShield: self.Game.sendSignal("CharLoses_"+name, self.Game.turn, self, None, 0, "")
				self.Game.sendSignal("CharEffectCheck", self.Game.turn, self, None, 0, "")
			if (self.onBoard or self.inHand) and self.btn: #Lifesteal, Poisonous, Deathrattle and Trig show up at the bottom of the minion icon
				if name not in ("Lifesteal", "Poisonous"): self.btn.effectChangeAni(name)
				else: self.btn.placeIcons()
	
	#Can acquire trigBoard, deathrattle
	def getsTrig(self, trig, trigType="TrigBoard", connect=True):
		trig.inherent = False
		{"TrigBoard": self.trigsBoard, "Deathrattle": self.deathrattles, "TrigHand": self.trigsHand}[trigType].append(trig)
		if connect:
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
	
	"""Handle cards dealing targeting/AOE damage/heal to target(s)."""
	#Handle Lifesteal of a card. Currently Minion/Weapon/Spell classs have this method.
	##法术因为有因为外界因素获得吸血的能力，所以有自己的tryLifesteal方法。
	def tryLifesteal(self, damage, damageType="None"):
		game = self.Game
		if self.effects["Lifesteal"] > 0 or (self.category == "Spell" and game.effects[self.ID]["Spells Lifesteal"] > 0)\
				or (damageType == "Battle" and "Drain" in self.effects and self.effects["Drain"] > 0):
			heal = self.calcHeal(damage)
			if game.effects[self.ID]["Heal to Damage"] > 0:
				#If the Lifesteal heal is converted to damage, then the obj to take the final
				#damage will not cause Lifesteal cycle.
				dmgTaker = self.Game.scapegoat4(game.heroes[self.ID])
				dmgTaker.takesDamage(self, heal, damageType="Ability")
			elif game.effects[self.ID]["Lifesteal Damages Enemy"] > 0:
				dmgTaker = self.Game.scapegoat4(game.heroes[3-self.ID])
				dmgTaker.takesDamage(self, heal, damageType="Ability")
			else: #Heal is heal.
				if self.btn and hasattr(self.btn, "icons") and "Lifesteal" in self.btn.icons:
					GUI, icon = self.Game.GUI, self.btn.icons["Lifesteal"]
					GUI.seqHolder[-1].append(GUI.PARALLEL(GUI.FUNC(icon.trigAni), GUI.WAIT(0.25)))
				game.heroes[self.ID].getsHealed(self, heal)

	#可以对在场上以及手牌中的随从造成伤害，同时触发应有的响应，比如暴乱狂战士和+1攻击力和死亡缠绕的抽牌。
	#牌库中的和已经死亡的随从免疫伤害，但是死亡缠绕可以触发抽牌。
	#吸血同样可以对于手牌中的随从生效并为英雄恢复生命值。如果手牌中的随从有圣盾，那个圣盾可以抵挡伤害，那个随从在打出后没有圣盾（已经消耗）。
	#暂时可以考虑不把吸血做成场上扳机，因为几乎没有战吼随从可以获得吸血，直接将吸血视为随从的dealsDamage自带属性也可以。
	def dealsDamage(self, target, damage, animationType=''):
		damage, game = [damage], self.Game
		if target.onBoard or target.inHand:
			if game.GUI and animationType: game.GUI.targetingEffectAni(self, target)
			elif game.GUI: game.GUI.resetSubTarColor(self, target)
			if self == target: game.add2EventinGUI(self, target, textSubject="-%d"%damage[0], colorSubject=red)
			else: game.add2EventinGUI(self, target, textTarget="-%d"%damage[0], colorTarget=red)
			dmgTaker = game.scapegoat4(target, self)
			#超杀和造成伤害触发的效果为场上扳机.吸血始终会在队列的末尾结算。
			#战斗时不会调用这个函数，血量减少时也不立即发生伤害信号，但是这里是可以立即发生信号触发扳机的。
			#如果随从或者英雄处于可以修改伤害的效果之下，如命令怒吼或者复活的铠甲，伤害量会发生变化
			game.sendSignal("AbilityDmg" + target.category, 0, self, target, damage, "")  # 不能把这个东西写入和伤害承受目标判定同时进行的结算，因为存在互相干扰的情况
			dmgActual = dmgTaker.takesDamage(self, damage[0], damageType="Ability")
			self.tryLifesteal(dmgActual, "Ability")
			if dmgActual:
				game.sendSignal("DealtDmg", 0, self, None, dmgActual, "")
				if self.category == "Power": game.Counters.damageDealtbyHeroPower[self.ID] += dmgActual
			return dmgTaker, dmgActual
		else: return target, 0 #The target is neither on board or in hand. Either removed already or shuffled into deck.

	#The targets can be [], [subject], [subject1, subject2, ...]
	#For now, AOE will only affect targets that are on board. No need to check if the target is dead, in hand or in deck.
	#当场上有血量为2的奥金尼和因为欧米茄灵能者获得的法术吸血时，神圣新星杀死奥金尼仍然会保留治疗转伤害的效果。
	#有的扳机随从默认随从需要在非濒死情况下才能触发扳机，如北郡牧师。
	def AOE_Damage(self, targets, damages):
		game = self.Game
		targets, damages = targets[:], damages[:]
		self.Game.add2EventinGUI(self, targets, textTarget=["-%d"%dmg for dmg in damages], colorTarget=red)
		dmgTakers, dmgsActual, totalDmg = [], [], 0
		if targets and game.GUI:
			game.GUI.AOEAni(self, targets, damages)
		for target, damage in zip(targets, damages):
			dmg = [damage]
			dmgTaker = game.scapegoat4(target, self)
			#Handle the Divine Shield and Commanding Shout here.
			self.Game.sendSignal("AbilityDmg" + target.category, 0, self, target, dmg, "")  # 不能把这个东西写入和伤害承受目标判定同时进行的结算，因为存在互相干扰的情况
			dmgActual = dmgTaker.takesDamage(self, dmg[0], sendDmgSignal=False, damageType="Ability")
			if dmgActual > 0:
				dmgTakers.append(dmgTaker)
				dmgsActual.append(dmgActual)
				totalDmg += dmgActual
		#AOE首先计算血量变化，之后才发出伤害信号。
		for target, dmgActual in zip(dmgTakers, dmgsActual):
			game.sendSignal(target.category+"TakesDmg", self.ID, self, target, dmgActual, "")
			game.sendSignal(target.category+"TookDmg", self.ID, self, target, dmgActual, "")
		self.tryLifesteal(totalDmg, "Ability")
		if totalDmg: game.sendSignal("DealtDmg", 0, self, None, totalDmg, "")
		return dmgTakers, dmgsActual, totalDmg

	def countHealDouble(self):
		if self.category in ("Minion", "Weapon"): return sum(minion.effects["Heal x2"] > 0 for minion in self.Game.minions[self.ID])
		elif self.category in ("Spell", "Power"):
			return sum(minion.effects["Heal x2"] > 0 or minion.effects["Spell Heal&Dmg x2"] > 0 for minion in self.Game.minions[self.ID])
		else: return 0

	def calcHeal(self, base): return base * (2 ** self.countHealDouble())

	def AOE_Heal(self, targets, heals):
		game = self.Game
		targets_Heal, heals = targets[:], heals[:]
		if game.effects[self.ID]["Heal to Damage"] > 0:
			dmgTakers, dmgsActual, totalDmgDone = self.AOE_Damage(targets_Heal, heals)
			healsActual = [-damage for damage in dmgsActual]
			return dmgTakers, healsActual, -totalDmgDone #对于AOE回复，如果反而造成伤害，则返回数值为负数
		else:
			targets_healed, healsActual, totalHealDone = [], [], 0
			if targets and game.GUI:
				self.Game.add2EventinGUI(self, targets, textTarget=["+%d"%heal for heal in heals], colorTarget=yellow)
				#game.GUI.AOEAni(self, targets, heals, color="green3")
			for target, heal in zip(targets, heals):
				healActual = target.getsHealed(self, heal, sendHealSignal=False)
				if healActual > 0:
					targets_healed.append(target)
					healsActual.append(healActual)
					totalHealDone += healActual
			containHero = False
			for target, healActual in zip(targets_healed, healsActual):
				game.sendSignal(target.category+"GetsHealed", game.turn, self, target, healActual, "")
				game.sendSignal(target.category+"GotHealed", game.turn, self, target, healActual, "")
				if target.category == "Hero":
					containHero = target.ID
			if containHero:
				game.sendSignal("AllCured", containHero, self, None, 0, "")
			else:
				game.sendSignal("MinionsCured", game.turn, self, None, 0, "")
		return targets_healed, healsActual, totalHealDone

	def restoresHealth(self, target, heal):
		if self.Game.effects[self.ID]["Heal to Damage"] > 0:
			dmgTaker, dmgActual = self.dealsDamage(target, heal)
			return dmgTaker, -dmgActual
		else:
			if self == target: self.Game.add2EventinGUI(self, target, textSubject="+%d"%heal, colorSubject=yellow)
			else: self.Game.add2EventinGUI(self, target, textTarget="+%d"%heal, colorTarget=yellow)
			healActual = target.getsHealed(self, heal)
			return target, healActual

	#Lifesteal will only calc once with Aukenai,  for a lifesteal damage spell,
	#the damage output is first enhanced by spell damage, then the lifesteal is doubled by Kangor, then the doubled healing is converted by the Aukenai.
	#Heal is heal at this poin. The Auchenai effect has been resolved before this function
	def getsHealed(self, subject, heal, sendHealSignal=True):
		game, healActual = self.Game, 0
		if self.inHand or self.onBoard:#If the character is dead and removed already or in deck. Nothing happens.
			#This doesn't check if the heal actually changes anything.
			game.sendSignal(self.category + "ReceivesHeal", game.turn, subject, self, 0, "")
			if self.health < self.health_max:
				healActual = heal if self.health + heal < self.health_max else self.health_max - self.health
				self.dmgTaken -= healActual
				self.calcStat("heal")
				if sendHealSignal: #During AOE healing, the signals are delayed.
					game.sendSignal(self.category+"GetsHealed", game.turn, subject, self, healActual, "")
				game.Counters.healthRestoredThisGame[subject.ID] += healActual
				game.Counters.healthRestoredThisTurn[subject.ID] += healActual
				if self.category == "Minion":
					game.sendSignal("MinionStatCheck", self.ID, None, self, 0, "")
				elif game.turn == self.ID: #Hero getting healed
					game.Counters.timesHeroChangedHealth_inOwnTurn[self.ID] += 1
					game.Counters.heroChangedHealthThisTurn[self.ID] = True
					game.sendSignal("HeroChangedHealthinTurn", self.ID, None, None, 0, "")
				if sendHealSignal: #During AOE healing, the signals are delayed.
					game.sendSignal(self.category+"GotHealed", game.turn, subject, self, healActual, "")
		return healActual

	def rngPool(self, identifier):
		cardType = type(self)
		return [card for card in self.Game.RNGPools[identifier] if card != cardType]

	def newEvolved(self, cost, by=0, ID=0, s="-Cost Minions to Summon"):
		cost, gameRNGPool = cost + by, self.Game.RNGPools
		if by > 0:
			while str(cost) + s not in gameRNGPool: cost -= 1
		elif by < 0:
			while str(cost) + s not in gameRNGPool: cost += 1
		return numpyChoice(self.rngPool(str(cost)+s))(self.Game, ID)

	"""Common statChange/buffDebuff"""
	#buffDebuff和getsEffect很少单独被调用，一般由giveEnchant统一处理。只有在光环影响下可能会单独调用getsEffect
	def buffDebuff(self, target, attackGain=0, healthGain=0, source=None, name=None, enchant=None, add2EventinGUI=True):
		if not enchant: enchant = Enchantment(attackGain, healthGain, name=name)
		enchant.source, enchant.keeper = source, target
		enchant.addto(target)
		target.calcStat("buffDebuff")
		if target.category == "Minion" and (enchant.attGain > 0 or enchant.healthGain > 0):
			self.Game.sendSignal("MinionBuffed", target.ID, target, None, 0, "")

	# 卡牌获得一些效果，如圣盾，嘲讽等。冰冻效果单独由freeze&AOE_Freeze处理
	# 一些特殊的enchantment需要卡片效果自行定义，普通的enchantment只定义来源卡片各类，然后自行定义
	# 如果效果来源是光环，则enchantment和creator皆为None。普通的赋予特效需要source，然后自行定义Enchantment；特殊的特效需要卡牌效果自行定义一个Enchantment_xxx
	#name是产生这个效果的卡牌效果名称。如WarsongCommander
	def getsEffect(self, effect='', amount=1, source=None, name=None, enchant=None):
		if not self.inDeck:
			if enchant:
				effect, amount = enchant.effGain, enchant.effNum
				enchant.addto(self) #The Enchantment_Cumulative can pile on the same enchantment
			elif source: Enchantment(effGain=effect, effNum=amount, source=source, name=name).addto(self)
			# 首先检视卡牌自身的effects，如果特效/不在其中，则交由Game.effects处理。
			if effect in self.effects: self.effects[effect] += amount
			elif effect in (effects := self.Game.effects[self.ID]): effects[effect] += amount
			else:
				print("GetsEffect got something unresolvable", effect)
				raise
			if self.onBoard and (self.category == "Minion" or self.category == "Hero"):
				self.decideAttChances_base()
				self.Game.sendSignal("CharEffectCheck", self.Game.turn, self, None, 0, "")  # 用于部分光环，如方阵指挥官
			if (self.onBoard or self.inHand) and self.btn:
				if effect in ("Lifesteal", "Poisonous"): self.btn.placeIcons()
				else: self.btn.effectChangeAni(effect)

	#Combine the stat buffDebuff and effect gain.
	#If only give one effect, effGain should be defined; elif multipleEffGains isn't empty, then multiple effects would be given
	#enchant only need to define its values and card effect that generates it, the source and keeper will be handled by
	#The trigger to give to cards can't store in-game information. It is a simple type
	def giveEnchant(self, target, attackGain=0, healthGain=0, statEnchant=None,
					effGain=None, effNum=1, effectEnchant=None, multipleEffGains=(),
					trig=None, trigType="TrigBoard", connect=True, trigs=(),
					name=None, add2EventinGUI=True):
		if target.inDeck or target.dead: return

		if self.Game.GUI and add2EventinGUI:
			if statEnchant: attackGain, healthGain = statEnchant.attGain, statEnchant.healthGain
			if attackGain or healthGain:
				s = "%d/%d"%(attackGain, healthGain)
				color = green if attackGain > -1 and healthGain > -1 else red
			else: s, color = '', white
			if self == target: self.Game.add2EventinGUI(self, None, textSubject=s, colorSubject=color)
			else: self.Game.add2EventinGUI(self, target, textTarget=s, colorTarget=color)

		if attackGain or healthGain or statEnchant: self.buffDebuff(target, attackGain, healthGain, source=type(self), name=name,
													 				enchant=statEnchant, add2EventinGUI=add2EventinGUI)
		if effGain: target.getsEffect(effGain, effNum, source=type(self), name=name, enchant=effectEnchant)
		else: #Use the (effGain, amount, effectEnchant) given in the multipleEffGains container
			for effect, num, enchant in multipleEffGains: target.getsEffect(effect, num, source=type(self), name=name, enchant=enchant)
		if trig: target.getsTrig(trig(target), trigType, connect)
		elif trigs:
			for trigger, triggerType, conn in trigs: target.getsTrig(trigger(target), triggerType, conn)

	#For multiple targets, the enchants and multipleEffGains will be in the same way as single target above. The function takes care of
	def AOE_GiveEnchant(self, targets, attackGain=0, healthGain=0, statEnchant=None,
						effGain=None, effNum=1, effectEnchant=None, multipleEffGains=(),
						trig=None, trigType="TrigBoard", connect=True, trigs=(),
						name=None, add2EventinGUI=True):
		if len(targets) > 0: return
		if self.Game.GUI and add2EventinGUI:
			if statEnchant: attackGain, healthGain = statEnchant.attGain, statEnchant.healthGain
			if attackGain or healthGain:
				s = "%d/%d"%(attackGain, healthGain)
				color = green if attackGain > -1 and healthGain > -1 else red
			else: s, color = '', white
			self.Game.add2EventinGUI(self, targets, textTarget=s, colorTarget=color)
		for target in targets:
			self.giveEnchant(target, attackGain, healthGain, statEnchant,
							effGain, effNum, effectEnchant, multipleEffGains,
							trig, trigType, connect, trigs,
							name, add2EventinGUI=False)

	def getsBuffDebuff_inDeck(self, attackGain, healthGain, source=None, name=None):
		self.enchantments.append(Enchantment(attackGain, healthGain, source=source, name=name))
		self.attack, self.health_max = self.attack_0, self.health_0
		for enchant in self.enchantments: enchant.handleStatMax(self)
		self.health = self.health_max

	def giveHeroAttackArmor(self, ID, attGain=0, statEnchant=None, armor=0, name=None):
		hero = self.Game.heroes[ID]
		if statEnchant or attGain:
			if not statEnchant: statEnchant = Enchantment(attGain=attGain, until=0, source=type(self), name=name)
			statEnchant.addto(hero)
		s = "%d|%d"%(statEnchant.attGain if statEnchant else attGain, armor)
		if self.Game.GUI: self.Game.add2EventinGUI(self, hero, textTarget=s, colorTarget=white)

		if statEnchant: hero.calcStat("buffDebuff")
		self.Game.sendSignal("HeroAttGained", ID, hero, None, attGain, "")
		if armor:
			hero.armor += armor
			if hero.btn: hero.btn.statChangeAni(action="armorChange")
			self.Game.sendSignal("ArmorGained", ID, hero, None, armor, "")

	# Either newAttack or newHealth must be a positive number
	def setStat(self, target, newAttack=-1, newHealth=-1, enchant=None, name=None, add2EventinGUI=True):
		if not target.inDeck and not target.dead:
			if not enchant: enchant = Enchantment(attSet=newAttack, healthSet=newHealth, name=name)
			newAttack, newHealth = enchant.attSet, enchant.healthSet
			enchant.source, enchant.keeper = type(self), target
			if self.Game.GUI and add2EventinGUI:
				s = (str(newAttack) if newAttack > -1 else '') + '/' + (str(newHealth) if newHealth > -1 else '')
				if self == target: self.Game.add2EventinGUI(self, None, textSubject=s, colorSubject=white)
				else: self.Game.add2EventinGUI(self, target, textTarget=s, colorTarget=white)

			if newHealth > 0: target.dmgTaken = 0
			target.enchantments.append(enchant)
			target.calcStat()

	def AOE_SetStat(self, targets, newAttack=-1, newHealth=-1, enchant=None, name=None, add2EventinGUI=True):
		if len(targets) > 0: return
		if self.Game.GUI and add2EventinGUI:
			if enchant: newAttack, newHealth = enchant.attSet, enchant.healthSet
			s = (str(newAttack) if newAttack > -1 else '') + '/' + (str(newHealth) if newHealth > -1 else '')
			self.Game.add2EventinGUI(self, targets, textTarget=s, colorTarget=white)
		for target in targets:
			self.setStat(target, newAttack, newHealth, enchant, name, add2EventinGUI=False)

	def statCheckResponse(self): pass
	#Some special card need their own calcStat, like Lightspawn
	def calcStat(self, action="set", num2=0): #During damage on hero, the damage reduction due to armor requires num2.
		if self.category in ("Minion", "Weapon", "Hero"):
			attOrig, healthOrig = self.attack, self.health
			self.attack, self.health_max = self.attack_0, self.health_0
			for enchant in self.enchantments: enchant.handleStatMax(self)
			for receiver in self.auraReceivers: receiver.handleStatMax()
			self.health = self.health_max - self.dmgTaken
			self.statCheckResponse()

			if self.category == "Hero" and self.Game.turn == self.ID and (weapon := self.Game.availableWeapon(self.ID)):
				self.attack += max(0, weapon.attack)
			if self.btn: self.btn.statChangeAni(num1=self.attack-attOrig, num2=num2 if num2 else self.health-healthOrig, action=action)
			self.Game.sendSignal("%sStatCheck"%self.category, self.ID, None, self, 0, "")
			if self.category == "Weapon" and self.ID == self.Game.turn: self.Game.heroes[self.ID].calcStat()

	"""Common discover handlers"""
	#因为所有发现界面的东西都会进行picks的读取，所以随机发现和引导下的发现都需要和手动发现一样的。
	#即使这一个发现可能没有问题，也可能会有连续发现的情况，导致出现问题
	
	#默认的discoverDecided是把一张生成的卡牌加入手牌中
	#info_GUISync可以是list/tuple/整数。但是当手动发现时需要向它里面添加数据，此时必须是列表，所以info_GUISync最终录入picks_Backup的时候需要再次用tuple转换为tuple
	#手动发现过程后会把一般的info_GUISync补完为[numOption, indexOption]
	def discoverDecided(self, option, case, info_RNGSync=None, info_GUISync=None):
		self.handleDiscoverGeneratedCard(option, case, info_RNGSync, info_GUISync)
	
	#Most basic Discovers, such as "Discover a spell". Choose 3(max) out of a single pool
	def discoverandGenerate(self, effectType, comment, poolFunc):
		game, ID = self.Game, self.ID
		if self.category == "Minion" and ID != game.turn:
			return
		if game.mode == 0:
			if game.picks:
				info_RNGSync, info_GUISync, isRandom, cardType = game.picks.pop(0) #, info_GUISync is (numOption, indexOption)
				if not cardType: return
				#For discoverandGenerate, info_RNGSync is simply poolSize
				numpyChoice(range(info_RNGSync), info_GUISync[0], replace=False)
				card = cardType(game, ID)
				if game.GUI: game.GUI.discoverDecideAni(isRandom=isRandom, numOption=info_GUISync[0], indexOption=info_GUISync[1], options=card)
				effectType.discoverDecided(self, card, case="Guided", info_RNGSync=info_RNGSync, info_GUISync=info_GUISync)
			else:
				pool = poolFunc()
				if not pool: game.picks_Backup.append((None, None, None, None))
				else:
					numOption = min(3, len(pool))
					options = numpyChoice(pool, numOption, replace=False)
					if ID != game.turn or "byOthers" in comment:
						i = datetime.now().microsecond % numOption
						#info_RNGSync=poolSize, info_GUISync = [numOption, i]
						card = options[i](game, ID)
						if game.GUI: game.GUI.discoverDecideAni(isRandom=True, numOption=numOption, indexOption=i, options=card)
						effectType.discoverDecided(self, card, case="Random", info_RNGSync=len(pool), info_GUISync=(numOption, i))
					else:
						game.options = [card(game, ID) for card in options]
						#info_RNGSync=poolSize, info_GUISync = [numOption] #discover will addto the indexOption to info_GUISync
						game.Discover.startDiscover(self, effectType=effectType, info_RNGSync=len(pool), info_GUISync=[numOption])

	#Such as "Discover a Hunter secret, Hunter weapon and a weapon". Choose one from each different pool
	def discoverandGenerate_MultiplePools(self, effectType, comment, poolsFunc):
		game, ID = self.Game, self.ID
		if self.category == "Minion" and ID != game.turn:
			return
		if game.mode == 0:
			if game.picks:
				info_RNGSync, info_GUISync, isRandom, card = game.picks.pop(0)
				for poolSize in info_RNGSync: numpyChoice(range(poolSize))
				card = card(game, ID)
				if game.GUI: game.GUI.discoverDecideAni(isRandom=isRandom, numOption=info_GUISync[0], indexOption=info_GUISync[1], options=card)
				effectType.discoverDecided(self, card, case="Guided", info_RNGSync=info_RNGSync, info_GUISync=info_GUISync)
			else:
				pools = poolsFunc()
				#Such pools is definitely non-empty
				if ID != game.turn or "byOthers" in comment:
					i = datetime.now().microsecond % len(pools)
					card = numpyChoice(pools[i])(game, ID)
					if game.GUI: game.GUI.discoverDecideAni(isRandom=True, numOption=len(pools), indexOption=i, options=card)
					effectType.discoverDecided(self, card, case="Random", info_RNGSync=(len(pools[i]), ), info_GUISync=(len(pools), i))
				else:
					info_RNGSync, game.options = [], []
					for pool in pools:
						game.options.append(numpyChoice(pool)(game, ID))
						info_RNGSync.append(len(pool))
					game.Discover.startDiscover(self, effectType=effectType, info_RNGSync=tuple(info_RNGSync), info_GUISync=[len(pools)])

	#Discover from a list of types, such as "Discover a friendly minion that died this game"
	#Most numerous type have a higher probability to be in the discover options
	def discoverandGenerate_Types(self, effectType, comment, typePoolFunc):
		game, ID = self.Game, self.ID
		if self.category == "Minion" and ID != game.turn:
			return
		if game.mode == 0:
			if game.picks:
				info_RNGSync, info_GUISync, isRandom, card = game.picks.pop(0)
				if not card: return
				numOption, indexOption = info_GUISync
				if info_RNGSync: numpyChoice(range(info_RNGSync[0]), numOption, p=info_RNGSync[1], replace=False)
				card = card(game, ID)
				if game.GUI: game.GUI.discoverDecideAni(isRandom=isRandom, numOption=numOption, indexOption=indexOption, options=card)
				effectType.discoverDecided(self, card, case="Guided", info_RNGSync=info_RNGSync, info_GUISync=info_GUISync)
			else:
				cardTypes, p = discoverProb(typePoolFunc())
				if not cardTypes: game.picks_Backup.append((None, None, None, None))
				else:
					numOption = min(3, len(cardTypes))
					types = numpyChoice(cardTypes, numOption, p=p, replace=False)
					if numOption == 1 or ID != game.turn or "byOthers" in comment:
						i = datetime.now().microsecond % numOption
						card = types[i](game, ID)
						if game.GUI: game.GUI.discoverDecideAni(isRandom=True, numOption=numOption, indexOption=i, options=card)
						effectType.discoverDecided(self, card, case="Random", info_RNGSync=(len(cardTypes), p), info_GUISync=(numOption, i))
					else:
						game.options = [card(game, ID) for card in types]
						game.Discover.startDiscover(self, effectType=effectType, info_RNGSync=(len(cardTypes), p), info_GUISync=[numOption])
	
	#For selections like Totemic Slam. The options are totally determined
	#options are types. Such as (HealingTotem, SearingTotem, StoneclawTotem, StrengthTotem)
	def chooseFixedOptions(self, effectType, comment, options):
		game, ID = self.Game, self.ID
		if self.category == "Minion" and ID != game.turn:
			return
		if game.mode == 0:
			if game.picks:
				info_RNGSync, info_GUISync, isRandom, optionType = game.picks.pop(0)  #, info_GUISync is (numOption, indexOption)
				numOption, indexOption = info_GUISync
				option = options[indexOption]
				if game.GUI: game.GUI.discoverDecideAni(isRandom=isRandom, numOption=numOption, indexOption=indexOption, options=option)
				effectType.discoverDecided(self, option, case="Guided", info_RNGSync=info_RNGSync, info_GUISync=info_GUISync)
			else:
				numOption = len(options)
				if ID != game.turn or "byOthers" in comment:
					i = datetime.now().microsecond % numOption
					card = options[i]
					if game.GUI: game.GUI.discoverDecideAni(isRandom=True, indexOption=i, options=card)
					effectType.discoverDecided(self, card, case="Random", info_RNGSync=None, info_GUISync=(numOption, i))
				else:
					game.options = options
					game.Discover.startDiscover(self, effectType=effectType, info_RNGSync=None, info_GUISync=[numOption])
	
	#case can be "Discovered", "Guided" or "Random"
	def handleDiscoverGeneratedCard(self, option, case, info_RNGSync, info_GUISync, func=None):
		cardType, card = type(option), option
		if case != "Guided": self.Game.picks_Backup.append((info_RNGSync, tuple(info_GUISync), case == "Random", cardType))
		
		if func: func(cardType, card)
		else: self.addCardtoHand(card, self.ID, byDiscover=True)

	#By default, discover any card from your own deck. ls must a list of card objects
	def discoverfromCardList(self, effectType, comment, conditional=lambda card: True, ls=None):
		game, ID = self.Game, self.ID
		if ls is None: ls = self.Game.Hand_Deck.decks[self.ID]
		if not ls or (self.category == "Minion" and ID != game.turn): return
		if game.mode == 0:
			if game.picks:
				#选哪2/3张牌的序号记录在info_GUISync里面，indexPicked就是被选中的那张牌在ls中的序号
				info_RNGSync, info_GUISync, isRandom, indexPicked = game.picks.pop(0)
				if not indexPicked: #indices here are the indices of the 2/3 cards to show from ls
					return		#info_GUISync[1] is the indexOption
				indices_from_ls, numOption, indexOption = info_GUISync
				if info_RNGSync: #If no card to discover, then no RNG was involved
					numPools, p = info_RNGSync[0]
					numpyChoice(range(numPools), min(3, numPools), p=p, replace=False)
					for poolSize in info_RNGSync[1:]: numpyRandint(poolSize) #nprandint和npchoice效果完全相同
				if game.GUI: game.GUI.discoverDecideAni(isRandom=isRandom, numOption=numOption, indexOption=indexOption,
														options=[ls[i] for i in indices_from_ls])
				effectType.discoverDecided(self, indexPicked, case="Guided", info_RNGSync=info_RNGSync, info_GUISync=info_GUISync)
			else:
				cardTypes, p = discoverProb([type(card) for card in ls if conditional(card)])
				if not cardTypes:
					self.Game.picks_Backup.append((None, None, None, None))
				else:
					numOption = min(3, len(cardTypes))
					types = numpyChoice(cardTypes, numOption, p=p, replace=False)
					#2/3 different cards have their own indices make up indices_2Pickfrom
					#(len(cardTypes), p) + 2/3 different cards have their own poolSizes make up info_RNGSync
					info_RNGSync, indices_from_ls, options = [(len(cardTypes), p)], [], []
					for cardType in types:
						indices = [i for i, card in enumerate(ls) if isinstance(card, cardType)]
						index = numpyChoice(indices) #indices is of the same-typed cards in ls
						options.append(ls[index]) #a random card from the category is picked
						info_RNGSync.append(len(indices)) #len(indices) is the poolSize to pick a certain category from
						indices_from_ls.append(index)
					if numOption == 1 or ID != game.turn or "byOthers" in comment: #如果只有一个选项则跳过手动发现过程
						i = datetime.now().microsecond % numOption
						if game.GUI: game.GUI.discoverDecideAni(isRandom=True, numOption=numOption, indexOption=i, options=options)
						effectType.discoverDecided(self, indices_from_ls[i], case="Random", info_RNGSync=tuple(info_RNGSync),
												   info_GUISync=(tuple(indices_from_ls), numOption, i))
					else:
						game.options = options
						game.Discover.startDiscover(self, effectType=effectType, info_RNGSync=tuple(info_RNGSync),
													info_GUISync=[tuple(indices_from_ls), numOption])
						
	def handleDiscoveredCardfromList(self, option, case, ls, func, info_RNGSync, info_GUISync):
		if case == "Random":  #option here the index from ls
			card, index = ls[option], option
			self.Game.picks_Backup.append((info_RNGSync, tuple(info_GUISync), True, index))
		elif case == "Guided": #option here is index from ls
			card, index = ls[option], option
		else: #case == "Discovered" #option here is a real card selected
			card, index = option, ls.index(option)
			self.Game.picks_Backup.append((info_RNGSync, tuple(info_GUISync), False, index) )
		func(index, card)

	#Choose a target that is onBoard/inHand during effect resolution. Now only applicable to GoliathSneedsMasterpiece
	#ls会在调用函数时直接选好
	#因为没有随机生成选项
	def choosefromBoard(self, effectType, comment, ls): #ls可以根据index找到选择的目标
		game, ID = self.Game, self.ID
		if not ls or (self.category == "Minion" and ID != game.turn):
			return
		if game.mode == 0:
			if game.picks: #在场上的选择是没有随机产生的。info_RNGSync总是None
				isRandom, indexPicked = game.picks.pop(0)
				option = ls[indexPicked]
				if game.GUI: game.GUI.chooseDecideAni(isRandom=isRandom, indexOption=indexPicked, options=ls)
				effectType.chooseDecided(self, option, case="Guided", ls=ls)
			else:
				if (numOption := len(ls))== 1 or ID != game.turn or "byOthers" in comment:  # 如果只有一个选项则跳过手动发现过程
					i = datetime.now().microsecond % numOption
					if game.GUI: game.GUI.chooseDecideAni(isRandom=True, indexOption=i, options=ls)
					effectType.chooseDecided(self, ls[i], case="Random", ls=ls)
				else:
					game.options = ls
					game.Discover.startChoose(self, effectType=effectType, ls=ls)

	def chooseDecided(self, option, case, ls):
		self.handleChooseDecision(option, case, ls)

	def handleChooseDecision(self, option, case, ls, func=None):
		cardType, card = type(option), option
		if case != "Guided": self.Game.picks_Backup.append((case=="Random", ls.index(option)))

		if func: func(cardType, card)

	"""Common card generation handlers"""
	def addCardtoHand(self, card, ID, byDiscover=False, pos=-1, ani="fromCenter"):
		self.Game.Hand_Deck.addCardtoHand(card, ID, byDiscover=byDiscover, pos=pos,
										  ani=ani, creator=type(self))
		
	def shuffleintoDeck(self, obj, enemyCanSee=True):
		self.Game.Hand_Deck.shuffleintoDeck(obj, initiatorID=self.ID, enemyCanSee=enemyCanSee, creator=type(self))

	def summon(self, subject, relative=">", position=None):
		print("Doing summoning, summoner pos:", self.pos)
		return self.Game.summon(subject, self, relative=relative, position=position)

	def try_SummonfromDeck(self, position=None, func=lambda card: card.category == "Minion"):
		if self.Game.space(self.ID) and (indices := [i for i, card in enumerate(self.Game.Hand_Deck.decks[self.ID]) if func(card)]):
			return self.Game.summonfrom(numpyChoice(indices), self.ID, self.pos+1 if position is None else position, summoner=self, source="D")
		return None

	def try_SummonfromHand(self, position=None, func=lambda card: card.category == "Minion"):
		if self.Game.space(self.ID) and (indices := [i for i, card in enumerate(self.Game.Hand_Deck.hands[self.ID]) if func(card)]):
			return self.Game.summonfrom(numpyChoice(indices), self.ID, self.pos+1 if position is None else position, summoner=self, source="H")
		return None

	def transform(self, target, newTarget):
		self.Game.transform(target, newTarget, firstTime=True, summoner=self)
		
	def equipWeapon(self, weapon):
		self.Game.equipWeapon(weapon, creator=type(self))

	#1st param is None when empty/no match. When there is milling, returns (card, x, False)
	def drawCertainCard(self, conditional=lambda card: True):
		if indices := [i for i, card in enumerate(self.Game.Hand_Deck.decks[self.ID]) if conditional(card)]:
			return self.Game.Hand_Deck.drawCard(self.ID, numpyChoice(indices))
		return None, -1, False #When no card meets requirement, then no card would enter hand

	#If not specified, all cards in owner's hand will be legal target. Assuming cards costing >0 will be prioritized.
	def findCards4ManaReduction(self, conditional=lambda card: True, ID=0):
		hand = self.Game.Hand_Deck.hands[ID if ID else self.ID]
		if cards := [card for card in hand if conditional(card) and card.mana > 0]:
			return cards
		else: return [card for card in hand if conditional(card)]

	"""Handle the battle options for minions and heroes."""
	def canAttack(self):
		return False

	def canAttackTarget(self, target):
		return False

	#Will only be used to find a selectable attack target
	def findBattleTargets(self):
		if self.canAttack():
			targets = [minion for minion in self.Game.minionsonBoard(3-self.ID) if self.canAttackTarget(minion)]
			if self.canAttackTarget((hero := self.Game.heroes[3-self.ID])): targets.append(hero)
			return targets
		else: return []

	#所有打出效果的目标寻找，包括战吼，法术等
	def findTargets(self, choice=0): #comment="" is for random choosing, ignoring Stealth, etc. Non-empty comment will require target to be selectable
		targets = [minion for minion in self.Game.minionsonBoard(1) if self.targetCorrect(minion, choice) and self.canSelect(minion)] \
					+ [minion for minion in self.Game.minionsonBoard(2) if self.targetCorrect(minion, choice) and self.canSelect(minion)]
		for ID in (1, 2):
			if self.targetCorrect((hero := self.Game.heroes[ID]), choice) and self.canSelect(hero):
				targets.append(hero)
		return targets

	#继承一张卡的所有附魔时一定是那张卡要消失的时候。一般用于一张牌的升级/腐蚀变形
	def inheritEnchantmentsfrom(self, card):
		for receiver in card.auraReceivers: receiver.effectClear()
		#Buff and mana effects, etc, will be preserved
		#Buff to cards in hand will always be permanent or temporary, not from Auras
		if self.category in ("Minion", "Weapon"):
			self.enchantments += card.enchantments
			for trig in card.deathrattles:
				if not trig.inherent:
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

	#在原始的游戏中生成一个Copy，即复制一张手牌/随从等。Dormant不会selfCopy
	def selfCopy(self, ID, creator, attack=-1, health=-1, mana=-1):
		Copy = type(self)(self.Game, ID)
		Copy.creator = creator = type(creator)
		Copy.progress = self.progress
		Copy.manaMods = [manaMod.selfCopy(Copy) for manaMod in self.manaMods if not manaMod.source]
		Copy.enchantments = [enchant.selfCopy(Copy) for enchant in self.enchantments]
		if self.category in ("Minion", "Weapon"): Copy.dmgTaken = self.dmgTaken
		if self.category == "Minion":
			Copy.attack_0, Copy.health_0 = self.attack_0, self.health_0
			Copy.silenced = self.silenced
			# 如果要生成一个x/x/x的复制
			if attack > -1 or health > -1: Copy.enchantments.append(Enchantment(attSet=attack, healthSet=health, source=creator))
			if mana: Copy.manaMods.append(ManaMod(Copy, to=mana))
		self.assistSelfCopy(Copy)
		return Copy

	def assistSelfCopy(self, Copy): pass

	def createCopy(self, game):
		if self in game.copiedObjs: return game.copiedObjs[self]
		else:
			game.copiedObjs[self] = Copy = type(self)(game, self.ID)
			Copy.enterHandTurn, Copy.enterBoardTurn = self.enterHandTurn, self.enterBoardTurn
			Copy.progress = self.progress
			Copy.effects = copy.deepcopy(self.effects)
			if self.category in ("Dormant", "Minion", "Weapon", "Hero"):
				Copy.onBoard, Copy.seq, Copy.pos = self.onBoard, self.seq, self.pos
				if self.category != "Dormant":
					Copy.dmgTaken = self.dmgTaken
					Copy.attack, Copy.health, Copy.health_max = self.attack, self.health, self.health_max
					Copy.inHand, Copy.inDeck, Copy.dead = self.inHand, self.inDeck, self.dead
				if self.category == "Minion":
					Copy.silenced = self.silenced
					Copy.attack_0, Copy.health_0 = self.attack_0, self.health_0
					#Copy.history = copy.deepcopy(self.history)
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
			Copy.auras = [aura.createCopy(game) for aura in self.auras]
			Copy.auraReceivers = [receiver.selfCopy(Copy) for receiver in self.auraReceivers]
			if self.category != "Dormant":
				Copy.usageCount = self.usageCount
				Copy.mana, Copy.manaMods = self.mana, [manaMod.selfCopy(Copy) for manaMod in self.manaMods]

			Copy.enchantments = [enchant.selfCopy(Copy) for enchant in self.enchantments]
			Copy.deathrattles = [trig.createCopy(game) for trig in self.deathrattles]
			Copy.trigsBoard = [trig.createCopy(game) for trig in self.trigsBoard]
			Copy.trigsHand = [trig.createCopy(game) for trig in self.trigsHand]
			Copy.trigsDeck = [trig.createCopy(game) for trig in self.trigsDeck]
			Copy.tracked, Copy.creator, Copy.possi = self.tracked, self.creator, self.possi

			self.assistCreateCopy(Copy)
			return Copy

	def assistCreateCopy(self, Copy): pass



class Dormant(Card):
	category = "Dormant"
	def __init__(self, Game, ID, minionInside=None):
		super().__init__(Game, ID)
		self.minionInside = minionInside
		self.effects = {"Taunt": 0, "Divine Shield": 0,
						"Temp Stealth": 0, "Stealth": 0, "Immune": 0, "Evasive": 0, "Enemy Evasive": 0,
						"Spell Damage": 0, "Nature Spell Damage": 0,
						"Lifesteal": 0, "Poisonous": 0, "Sweep": 0,
						"Frozen": 0, "Borrowed": 0, "Charge": 0, "Rush": 0, "Windfury": 0, "Mega Windfury": 0,
						"Can't Attack": 0, "Can't Attack Hero": 0, "Unplayable": 0,
						"Heal x2": 0, "Spell Heal&Dmg x2": 0, "Power Heal&Dmg x2": 0,  # Crystalsmith Kangor, Prophet Velen, Clockwork Automation
						"Echo": 0,
						#SV effects
						"Deal Damage 0": 0,
						 }

	def appears(self, firstTime=True):
		self.onBoard = True
		self.enterBoardTurn = self.Game.numTurn
		for aura in self.auras: aura.auraAppears() # 目前没有Dormant有光环
		for trig in self.trigsBoard: trig.connect()
		if self.btn:
			self.btn.isPlayed, self.btn.card = True, self
			self.btn.placeIcons()

	# Dormant本身是没有死亡扳机的，所以这个deathrattlesStayArmed无论真假都无影响
	def disappears(self, deathrattlesStayArmed=False, disappearResponse=True):
		self.onBoard = False
		for aura in self.auras: aura.auraDisappears()
		for trig in self.trigsBoard: trig.disconnect()

	def takesDamage(self, subject, damage, sendDmgSignal=True, damageType="None"):
		return 0

	def assistCreateCopy(self, Copy):
		Copy.minionInside = self.minionInside.createCopy(Copy.Game)


class Minion(Card):
	category = "Minion"
	aura = deathrattle = None
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		cardType = type(self)
		self.race = cardType.race
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
		for key in cardType.effects.split(","):
			if '_' in key:
				keyWord, s = key.strip().split('_')
				self.effects[keyWord] = int(s)
			else: self.effects[key.strip()] = 1
		self.silenced = False  # This mark is for minion state change, such as enrage.
		# self.seq records the number of the minion's appearance. The first minion on board has a sequence of 0
		self.usageCount = self.attChances_base = self.attChances_extra = 0
		if cardType.aura: self.auras = [cardType.aura(self)]
		if cardType.deathrattle: self.deathrattles = [cardType.deathrattle(self)]
		self.history = {"Spells Cast on This": [],
						#"Magnetic Upgrades": {"AttackGain": 0, "HealthGain": 0,
						#					  "Keywords": {}, "Marks": {},
						#					  "Deathrattles": [], "Triggers": []
						#					  }
						}
		
	def reset(self, ID, isKnown=True): #如果一个随从被返回手牌或者死亡然后进入墓地，其上面的身材改变(buff/statReset)会被消除，但是保留其白字变化
		creator, possi = self.creator, type(self) if isKnown else self.possi
		att_0, health_0 = self.attack_0, self.health_0
		btn = self.btn
		self.__init__(self.Game, ID)
		self.attack_0 = self.attack = att_0
		self.health_0 = self.health = self.health_max = health_0
		self.creator, self.possi = creator, possi
		self.btn = btn
		
	def applicable(self, target):
		return target != self

	"""Handle the trigsBoard/inHand/inDeck of minions based on its move"""
	def appears(self, firstTime=True):
		self.onBoard = True
		self.inHand = self.inDeck = self.dead = False
		self.enterBoardTurn = self.Game.numTurn
		self.mana = type(self).mana  # Restore the minion's mana to original value.
		for aura in self.auras: aura.auraAppears()
		for trig in self.trigsBoard + self.deathrattles: trig.connect()
		self.decideAttChances_base()  # Decide base att chances, given Windfury and Mega Windfury
		if self.btn:
			self.btn.isPlayed, self.btn.card = True, self
			self.btn.placeIcons()
			self.btn.effectChangeAni()
		# auras will react to this signal.
		self.Game.sendSignal("MinionAppears", self.ID, self, None, 0, comment=firstTime)
		self.calcStat()

	def disappears(self, deathrattlesStayArmed=False, disappearResponse=True):  # The minion is about to leave board.
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
		self.Game.sendSignal("MinionDisappears", self.ID, None, self, 0, "")

	"""Attack chances handle"""
	# The game will directly invoke the turnStarts/turnEnds methods.
	def turnStarts(self, turn2Start):
		super().turnStarts(turn2Start)
		if turn2Start == self.ID:
			if self.onBoard: self.losesEffect("Temp Stealth", 0, removeEnchant=True) # Only minions on board lose Temp Stealth
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
		super().turnEnds(turn2End)
		self.losesEffect("Immune", 0, removeEnchant=True)
		if turn2End == self.ID: # The minion can only thaw itself at the end of its turn. Not during or outside its turn
			if self.onBoard and self.effects["Frozen"] > 0:  # The minion can't defrost in hand.
				if self.actionable() and self.attChances_base + self.attChances_extra > self.usageCount:
					self.losesEffect("Frozen", 0)

		self.usageCount = self.attChances_extra = 0
		self.calcStat()
		if self.btn: self.btn.effectChangeAni()
		
	# 判定随从是否处于刚在我方场上登场，以及暂时控制、冲锋、突袭等。
	def actionable(self):
		# 不考虑冻结、零攻和自身有不能攻击的debuff的情况。
		# 如果随从是刚到我方场上，则需要分析是否是暂时控制或者是有冲锋或者突袭。
		# 随从已经在我方场上存在一个回合。则肯定可以行动。
		return self.onBoard and self.ID == self.Game.turn and \
			   (self.enterBoardTurn != self.Game.numTurn or (self.effects["Borrowed"] > 0 or self.effects["Charge"] > 0 or self.effects["Rush"] > 0))

	# Whether the minion can select the attack target or not.
	def canAttack(self):
		# THE CHARGE/RUSH MINIONS WILL GAIN ATTACKCHANCES WHEN THEY APPEAR
		return self.actionable() and self.attack > 0 and self.effects["Frozen"] < 1 \
			   and self.attChances_base + self.attChances_extra > self.usageCount \
			   and self.attackAllowedbyEffect()

	def attackAllowedbyEffect(self):
		return self.effects["Can't Attack"] < 1

	def canAttackTarget(self, target):
		return self.canAttack() and target.selectablebyBattle(self) and \
			   (target.category == "Minion" or (target.category == "Hero" and
											(self.enterBoardTurn != self.Game.numTurn or self.effects["Borrowed"] > 0 or self.effects["Charge"] > 0)
											and self.effects["Can't Attack Hero"] < 1)
				)

	"""Healing, damage, takeDamage, AOE, lifesteal and dealing damage response"""
	# Stealth Dreadscale actually stays in stealth.
	def takesDamage(self, subject, damage, sendDmgSignal=True, damageType="None"):
		game = self.Game
		if self.effects["Immune"] < 1:  # 随从首先结算免疫和圣盾对于伤害的作用，然后进行预检测判定
			if "Next Damage 0" in self.effects and self.effects["Next Damage 0"] > 0:
				if not subject.category == "Hero" or not damage == 0:
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
					game.sendSignal("FinalDmgonMinion?", 0, subject, self, damageHolder, "")
					damage = damageHolder[0]
					deadbyPoisonous = self.onBoard and ((subject.category == "Spell" and game.effects[subject.ID]["Spells Poisonous"] > 0) or
									   					("Poisonous" in subject.effects and subject.effects["Poisonous"] > 0))
					self.dmgTaken += damage
					self.calcStat("poisonousDamage" if deadbyPoisonous else "damage", num2=-damage)
					# 经过检测，被伏击者返回手牌中的紫罗兰老师不会因为毒药贩子加精灵弓箭手而直接丢弃。会减1血，并在打出时复原。
					if deadbyPoisonous:
						if (GUI := self.Game.GUI) and "Poisonous" in subject.btn.icons:
							GUI.seqHolder[-1].append(GUI.PARALLEL(GUI.FUNC(subject.btn.icons["Poisonous"].trigAni), GUI.WAIT(0.2)))
						self.dead = True
					# 在同时涉及多个角色的伤害处理中，受到的伤害暂不发送信号而之后统一进行扳机触发。
					if sendDmgSignal:
						game.sendSignal("MinionTakesDmg", game.turn, subject, self, damage, "")
						game.sendSignal("MinionTookDmg", game.turn, subject, self, damage, "")
					# 随从的激怒，根据血量和攻击的状态改变都在这里触发。
					self.Game.sendSignal("MinionStatCheck", self.ID, None, self, 0, "")
			else:
				game.sendSignal("MinionTakes0Dmg", game.turn, subject, self, 0, "")
				game.sendSignal("MinionTook0Dmg", game.turn, subject, self, 0, "")
		else: damage = 0
		return damage

	def deathResolution(self, attackwhenDies, armedTrigs_WhenDies, armedTrigs_AfterDied):
		self.Game.sendSignal("MinionDies", self.Game.turn, None, self, attackwhenDies, '', 0,
							 armedTrigs_WhenDies)
		# 随从的亡语也需要扳机化，因为亡语和“每当你的一个xx随从死亡”的扳机的触发顺序也由其登场顺序决定
		# 如果一个随从有多个亡语（后来获得的，那么土狼会在两个亡语结算之间触发。所以说这些亡语是严格意义上的扳机）
		# 随从入场时注册亡语扳机，除非注明了是要结算死亡的情况下，disappears()的时候不会直接取消这些扳机，而是等到deathResolution的时候触发这些扳机
		# 如果是提前离场，如改变控制权或者是返回手牌，则需要取消这些扳机
		# 扳机应该注册为场上扳机，这个扳机应该写一个特殊的类，从而使其可以两次触发，同时这个类必须可存储一个attribute,复制效果可以复制食肉魔块等战吼提供的信息
		# 区域移动类扳机一般不能触发两次
		# 触发扳机如果随从已经不在场上，则说明它区域移动然后进入了牌库或者手牌。同类的区域移动扳机不会触发。
		# 区域移动的死亡扳机大多是伪区域移动，实际上是将原实体移除之后将一个复制置入相应区域。可以通过魔网操纵者来验证。只有莫里甘博士和阿努巴拉克的亡语是真的区域移动
		# 鼬鼠挖掘工的洗入对方牌库扳机十分特别，在此不予考虑，直接视为将自己移除，然后给对方牌库里洗入一个复制
		# If returned to hand/deck already due to deathrattle, the inHand/inDeck will be kept
		# 假设随从只有在场上结算亡语完毕之后才会进行初始化，而如果扳机已经提前将随从返回手牌或者牌库，则这些随从不会
		# 移除随从注册了的亡语扳机
		for trig in self.deathrattles: trig.disconnect()
		self.Game.sendSignal("MinionDied", self.Game.turn, None, self, 0, "", 0, armedTrigs_AfterDied)

	def magnetCombine(self, target):
		pass

	# Specifically for battlecry resolution. Doesn't care if the target is in Stealth.
	def targetCorrect(self, target, choice=0):
		return (target.category == "Minion" or target.category == "Hero") and target.onBoard and target != self

	# Minions that initiates discover or transforms self will be different.
	# For minion that transform before arriving on board, there's no need in setting its onBoard to be True.
	# By the time this triggers, death resolution caused by Illidan/Juggler has been finished.
	# If Brann Bronzebeard/ Mayor Noggenfogger has been killed at this point, they won't further affect the battlecry.
	# posinHand在played中主要用于记录一张牌是否是从手牌中最左边或者最右边打出（恶魔猎手职业关键字）
	def played(self, target=None, choice=0, mana=0, posinHand=-2, comment=""):
		game = self.Game
		# 即使该随从在手牌中的生命值为0或以下，打出时仍会重置为无伤状态。
		self.health = self.health_max
		# 此时，随从可以开始建立光环，建立侦听，同时接受其他光环。例如： 打出暴风城勇士之后，光环在Illidan的召唤之前给随从加buff，同时之后打出的随从也是先接受光环再触发Illidan。
		self.appears(firstTime=True)
		GUI = game.GUI
		# 使用阶段
		# 使用时步骤,触发“每当你使用一张xx牌”的扳机,如伊利丹，任务达人，无羁元素和魔能机甲等
		# 触发信号依次得到主玩家的场上，手牌和牌库的侦听器的响应，之后是副玩家的侦听器响应。
		# 伊利丹可以在此时插入召唤和飞刀的结算，之后在战吼结算开始前进行死亡的判定，同时subject和target的位置情况会影响战吼结果。
		game.sendSignal("MinionPlayed", self.ID, self, target, mana, "", choice)
		# 召唤时步骤，触发“每当你召唤一个xx随从”的扳机.如鱼人招潮者等。
		game.sendSignal("MinionSummoned", self.ID, self, target, mana, "")
		# 过载结算
		if overload := type(self).overload: game.Manas.overloadMana(overload, self.ID)

		magneticTarget = None
		#if self.magnetic > 0:
		#	if self.onBoard:
		#		neighbors, dist = game.neighbors2(self)
		#		if dist == 1 and "Mech" in neighbors[1].race:
		#			magneticTarget = neighbors[1]
		#		elif dist == 2 and "Mech" in neighbors[0].race:
		#			magneticTarget = neighbors[0]
		# 使用阶段结束，开始死亡结算。视随从的存活情况决定战吼的触发情况，此时暂不处理胜负问题。
		game.gathertheDead()  # At this point, the minion might be removed/controlled by Illidan/Juggler combo.
		# 结算阶段
		#if self.magnetic > 0:
		#	# 磁力相当于伪指向性战吼，一旦指定目标之后，不会被其他扳机改变
		#	# 磁力随从需要目标和自己都属于同一方,且磁力目标在场时才能触发。
		#	if magneticTarget and magneticTarget.onBoard and self.ID == magneticTarget.ID:
		#		# 磁力结算会让随从离场，不会触发后续的随从召唤后，打出后的扳机
		#		self.magnetCombine(magneticTarget)
		# 磁力随从没有战吼等入场特效，因而磁力结算不会引发死亡，不必进行死亡结算

		# 无磁力的随从
		# 市长会在战吼触发前检测目标，指向性战吼会被随机取向。一旦这个随机过程完成，之后的第二次战吼会重复对此目标施放。
		# 如果场上有随从可供战吼选择，但是因为免疫和潜行导致打出随从时没有目标，则不会触发随机选择，因为本来就没有目标。
		# 在战吼开始检测之前，如果铜须已经死亡，则其并不会让战吼触发两次。也就是扳机的机制。
		# 同理，如果此时市长已经死亡，则其让选择随机化的扳机也已经离场，所以不会触发随机目标。

		# 市长只影响初始目标的选择，玩家的其他选择，如发现和抉择都不会受影响
		target = game.try_RedirectEffectTarget("EffectTarget?", self, target, choice)

		# 在随从战吼/连击开始触发前，检测是否有战吼/连击翻倍的情况。如果有且战吼可以进行，则强行执行战吼至两次循环结束。无论那个随从是死亡，在手牌中还是牌库
		num, effects = 1, game.effects[self.ID]
		if ("~Battlecry" in self.index and effects["Battlecry x2"] > 0) or ("~Combo" in self.index and effects["Combo x2"] > 0):
			num = 2
		# 不同的随从会根据目标和自己的位置和状态来决定effectwhenPlayed()产生体积效果。
		# 可以变形的随从，如无面操纵者，会有自己的played 方法。 大王同理。
		# 战吼随从自己不会进入牌库，因为目前没有亡语等效果可以把随从返回牌库。
		# 发现随从如果在战吼触发前被对方控制，则不会引起发现，因为炉石没有对方回合外进行操作的可能。
		# 结算战吼，连击，抉择
		for i in range(num):
			if GUI and "~Battlecry" in self.index: GUI.battlecryAni(self)
			target = self.whenEffective(target, "", choice, posinHand)
		# 结算阶段结束，处理死亡情况，不处理胜负问题。
		game.gathertheDead()
		return target

	def invokeBattlecry(self, effOwnerType):
		target, effOwnerObj = None, effOwnerType(self.Game, self.ID)
		if effOwnerObj.needTarget() and (targets := effOwnerType.findTargets(self)):
			target = numpyChoice(targets)
		self.Game.eventinGUI(effOwnerObj, "Battlecry", target=target)
		effOwnerType.whenEffective(self, target, comment="byOthers")

	# 沉默时随从的身材的变化原则：
	# 即使随从带有enchantment和加血光环带来的血量变化，沉默也尽量不会改变当前血量，除非新的血量上限会比当前血量更低
	# 需要重新计算dmgTaken

	# 破法者因为阿努巴尔潜伏者的亡语被返回手牌，之后被沉默，但是仍然可以触发其战吼
	def getsSilenced(self, keepStatEnchant=False):
		# 处理方式应当是首先记住随从的原始生命值，身上的所有光环效果以及它们各自对应的光环。然后清空随从身上的所有enchantments&effects
		# 清空之后从attack_0和health_0重新计算本体的攻击力和生命值，然后让之前的所有光环重新检测是否符合条件，符合的重新启动，不符合的移除
		# 然后比较当前的生命值上限和原始生命值，然后是处理effect变化和失去圣盾
		self.silenced = True
		prevHealth = self.health
		self.losesTrig(None, allTrigs=True)  # 清除所有场上扳机,亡语扳机，手牌扳机和牌库扳机。然后将这些扳机全部清除
		for aura in self.auras: aura.auraDisappears() #Clear the minion's auras
		self.auras = []
		auras_Receivers = [(receiver.source, receiver) for receiver in self.auraReceivers]
		self.auraReceivers = []
		if not keepStatEnchant: self.enchantments = [] #效果和身材的enchant都除去
		else: #保存身材的enchantment，移除只有effGain的，并把所有剩余的enchantment的effGain设为''
			i = len(self.enchantments) - 1
			for enchant in reversed(self.enchantments):
				if enchant.attGain == enchant.healthGain == 0 and enchant.attSet == enchant.healthSet == -1:
					self.enchantments.pop(i)
				else: enchant.effGain = ''
				i -= 1

		returnBorrowed = self.effects["Borrowed"] > 0 and self.onBoard
		for key in self.effects: self.effects[key] = 0
		if returnBorrowed: #被归还的随从是一定会失去所有光环效果的
			for aura, receiver in auras_Receivers: removefrom(receiver, aura.receivers)
			self.Game.minionSwitchSide(self, activity="Return")
		else:
			for aura, receiver in auras_Receivers:
				if aura.on and aura.applicable(self): receiver.effectBack2List()
				else: removefrom(receiver, aura.receivers)

		self.attack, self.health_max = self.attack_0, self.health_0
		for enchant in self.enchantments: enchant.handleStatMax(self)
		for receiver in self.auraReceivers: receiver.handleStatMax()
		self.health = min(self.health_max, prevHealth)
		self.dmgTaken = self.health_max - self.health

		if self.btn: self.btn.statChangeAni(num1=-1, num2=-1)
		self.Game.sendSignal("%sStatCheck" % self.category, self.ID, None, self, 0, "")
		if self.btn:
			self.btn.placeIcons()
			self.btn.effectChangeAni()
		self.decideAttChances_base()



class Hero(Card):
	category, health, heroPower = "Hero", 30, None
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.attChances_base, self.attChances_extra = 1, 0
		self.pos = self.ID
		self.effects = {"Windfury": 0, "Frozen": 0, "Temp Stealth": 0,
						 "Enemy Effect Evasive": 0, "Cost Health Instead": 0, "Unplayable": 0,
						#SV effects
						 "Enemy Effect Damage Immune": 0, "Can't Be Attacked": 0, "Next Damage 0": 0,
						"Deal Damage 0": 0,  "Draw to Win": 0,
						 }
		
	def reset(self, ID, isKnown=True):
		creator, possi = self.creator, type(self) if isKnown else self.possi
		btn = self.btn
		self.__init__(self.Game, ID)
		self.creator, self.possi = creator, possi
		self.btn = btn
	
	"""Handle hero's attacks, attack chances, attack chances and frozen."""
	def turnStarts(self, turn2Start):
		super().turnStarts(turn2Start)
		if turn2Start == self.ID:
			self.losesEffect("Temp Stealth", 0, removeEnchant=True)
			effects = self.Game.effects[self.ID]
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
		effects = self.Game.effects[self.ID]
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
			if prevArmor: self.Game.sendSignal("ArmorLost", self.ID, self, None, prevArmor, "")
		else:
			self.armor -= armor
			self.Game.sendSignal("ArmorLost", self.ID, self, None, armor, "")
		#英雄在没有受到伤害的情况下失去护甲时才会调用，不然直交由takesDamage函数处理
		if not dueToDamage and self.btn: self.btn.statChangeAni(action="armorChange")
	
	"""Handle hero's being selectable by subjects or not. And hero's availability for battle."""
	def canAttack(self):
		return self.actionable() and self.attack > 0 and self.effects["Frozen"] < 1 \
				and self.attChances_base + self.attChances_extra > self.usageCount

	def canAttackTarget(self, target):
		return self.canAttack() and target.selectablebyBattle(self)

	#Heroes don't have Lifesteal.
	def tryLifesteal(self, damage, damageType="None"):
		pass

	def takesDamage(self, subject, damage, sendDmgSignal=True, damageType="None"):
		game = self.Game
		if game.effects[self.ID]["Immune"] < 1:  # 随从首先结算免疫和圣盾对于伤害的作用，然后进行预检测判定
			if "Next Damage 0" in self.effects and self.effects["Next Damage 0"] > 0:
				damage = self.effects["Next Damage 0"] = 0
			if damageType == "Ability" and "Enemy Effect Damage Immune" in self.effects \
				and self.effects["Enemy Effect Damage Immune"] > 0:
				damage = 0
			if subject and "Deal Damage 0" in subject.effects and subject.effects["Deal Damage 0"] > 0:
				damage = 0
			if damage > 0:
				damageHolder = [damage]
				game.sendSignal("FinalDmgonHero?", self.ID, subject, self, damageHolder, "")
				damage = damageHolder[0]
				if damage > 0:
					if self.armor > damage: self.losesArmor(damage, dueToDamage=True)
					else:
						self.dmgTaken += damage - self.armor
						self.losesArmor(0, allArmor=True, dueToDamage=True)
					self.calcStat("damage", num2=-damage)
					game.Counters.dmgHeroTookThisTurn[self.ID] += damage
					if sendDmgSignal:
						game.sendSignal("HeroTakesDmg", game.turn, subject, self, damage, "")
						game.sendSignal("HeroTookDmg", game.turn, subject, self, damage, "")
					if game.turn == self.ID:
						game.Counters.timesHeroChangedHealth_inOwnTurn[self.ID] += 1
						game.Counters.timesHeroTookDamage_inOwnTurn[self.ID] += 1
						game.Counters.heroChangedHealthThisTurn[self.ID] = True
						game.sendSignal("HeroChangedHealthinTurn", self.ID, None, None, 0, "")
			else:
				game.sendSignal("HeroTakes0Dmg", game.turn, subject, self, 0, "")
				game.sendSignal("HeroTook0Dmg", game.turn, subject, self, 0, "")
		else:
			damage = 0
		return damage

	def healthReset(self, health, health_max=False):
		healthChanged = health != self.health
		self.health = health
		if health_max: self.health_max = health_max
		self.dmgTaken = self.health_max - self.health

		if self.btn: self.btn.statChangeAni(num2=0, action="buffDebuff")
		if healthChanged and self.Game.turn == self.ID:
			self.Game.Counters.timesHeroChangedHealth_inOwnTurn[self.ID] += 1
			self.Game.Counters.heroChangedHealthThisTurn[self.ID] = True
			self.Game.sendSignal("HeroChangedHealthinTurn", self.ID, None, None, 0, "")

	#专门被英雄牌使用，加拉克苏斯大王和拉格纳罗斯都不会调用该方法。
	def played(self, target=None, choice=0, mana=0, posinHand=-2, comment=""): #英雄牌使用目前不存在触发发现的情况
	#使用阶段
		#英雄牌替换出的英雄的生命值，护甲和攻击机会等数值都会继承当前英雄的值。
		game, ID, GUI = self.Game, self.ID, self.Game.GUI
		# 新技能必须存放起来，之后英雄还有可能被其他英雄替换，但是这个技能要到最后才登场。
		oldHero, oldPower, newPower = game.heroes[ID], game.powers[ID], type(self).heroPower(game, ID) if type(self).heroPower else None
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
		game.sendSignal("HeroCardPlayed", ID, self, None, mana, "", choice)
		#英雄牌的最大生命值和现有生命值以及护甲被设定继承旧英雄的数值。并获得英雄牌上标注的护甲值。
		self.giveHeroAttackArmor(self.ID, armor=type(self).armor)
		game.sendSignal("HeroAppears", ID, self, None, 0, "")
		#使用阶段结束，进行死亡结算，此时尚不进行胜负判定。
		game.gathertheDead()
	#结算阶段
		#获得新的英雄技能。注意，在此之前英雄有可能被其他英雄代替，如伊利丹飞刀打死我方的管理者埃克索图斯。
			#埃克索图斯可以替换英雄和英雄技能，然后本英雄牌在此处开始结算，再次替换英雄技能为正确的英雄牌技能。
		game.powers[ID] = newPower
		if GUI: GUI.heroZones[ID].heroReplacedAni(oldHero, oldPower)
		newPower.appears()
		#视铜须等的存在而结算战吼次数以及具体战吼。
		#不用返回主体，但是当沙德沃克调用时whenEffective函数的时候需要。
		if game.effects[ID]["Battlecry x2"] > 0: self.whenEffective(None, "", choice)
		self.whenEffective(None, "", choice)
		self.decideAttChances_base()
		#结算阶段结束，处理死亡，此时尚不进行胜负判定。
		game.gathertheDead()

	#可以是英雄牌被其他牌打出时替换当前英雄，也可以是炎魔之王拉格纳罗斯替换英雄，此时没有战吼。
	#炎魔之王变身不会摧毁玩家的现有装备和奥秘。只会移除冰冻，免疫和潜行等状态，并清除玩家的护甲。
	def replaceHero(self, fromHeroCard=False):
		#假设直接替换的英雄不会继承之前英雄获得的回合内攻击力增加。
		game, ID, GUI = self.Game, self.ID, self.Game.GUI
		oldHero, oldPower, newPower = game.heroes[ID], game.powers[ID], type(self).heroPower(game, ID) if type(self).heroPower else None
		oldHealth = oldHero.health
		self.onBoard, oldHero.onBoard, self.pos, self.usageCount = True, False, ID, oldHero.usageCount

		if newPower: oldPower.disappears()
		while oldHero.auraReceivers: oldHero.auraReceivers[0].effectClear()

		if fromHeroCard: self.dmgTaken, self.armor = oldHero.health_max - oldHero.health, oldHero.armor
		else: #英雄牌被其他牌打出时不会取消当前玩家的免疫状态
			self.losesArmor(0, allArmor=True) #被英雄牌以外的方式替换时，护甲会被摧毁
			# Hero's immune state is gone, except that given by Mal'Ganis
			effects = game.effects[ID]
			effects["Immune"] -= effects["Immune2NextTurn"] + effects["ImmuneThisTurn"]
			effects["ImmuneThisTurn"] = effects["Immune2NextTurn"] = 0
		game.heroes[ID] = self
		if newPower: game.powers[ID] = newPower
		if GUI: GUI.heroZones[ID].heroReplacedAni(oldHero, oldPower)
		self.calcStat()
		if self.btn: self.btn.effectChangeAni()

		game.sendSignal("HeroAppears", ID, self, None, 0, "")
		if self.health != oldHealth and game.turn == ID:
			game.Counters.timesHeroChangedHealth_inOwnTurn[ID] += 1
			game.Counters.heroChangedHealthThisTurn[ID] = True
			game.sendSignal("HeroChangedHealthinTurn", ID, None, None, 0, "")


class Weapon(Card):
	category = "Weapon"
	deathrattle = None
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.effects = {"Lifesteal": 0, "Poisonous": 0, "Windfury": 0,
						 "Immune": 0,
						 "Sweep": 0, "Cost Health Instead": 0, "Can't Attack Heroes": 0, "Unplayable": 0,
						 }
		cardType = type(self)
		for key in cardType.effects.split(","):
			self.effects[key.strip()] = 1
		if cardType.deathrattle: self.deathrattles = [cardType.deathrattle(self)]
		if cardType.aura: self.auras = [cardType.aura(self)]

	def reset(self, ID, isKnown=True):
		creator, possi = self.creator, type(self) if isKnown else self.possi
		btn = self.btn
		self.__init__(self.Game, ID)
		self.creator, self.possi = creator, possi
		self.btn = btn
	
	"""Handle weapon entering/leaving board/hand/deck"""
	#武器与随从的区别在于武器在打出过程中入场时appears和setasNewWeapon是会开的，尽管变形出现和装备时一起结算
	#只有最终设为setasNewWeapon时onBoard才会变为True
	def appears(self, firstTime=False):
		# 注意，此时武器还不能设为onBoard,因为之后可能会涉及亡语随从为英雄装备武器。
		# 尚不能因为武器标记为onBoard而调用其destroyed。
		self.inHand = self.inDeck = self.dead = False
		self.mana = type(self).mana
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
		game.sendSignal("WeaponAppears", self.ID, self, None, 0, "")

	def disappears(self, deathrattlesStayArmed=False, disappearResponse=True):
		if self.onBoard:  # 只有装备着的武器才会触发，以防连续触发。
			self.onBoard = False
			if self.effects["Windfury"] > 0: self.Game.heroes[self.ID].decideAttChances_base()
			self.Game.heroes[self.ID].calcStat()
			for trig in self.trigsBoard: trig.disconnect()
			if not deathrattlesStayArmed:
				for trig in self.deathrattles: trig.disconnect()
			self.Game.sendSignal("WeaponDisappears", self.ID, self, None, 0, "")

	def deathResolution(self, attackwhenDies, armedTrigs_WhenDies, armedTrigs_AfterDied):
		# 除了武器亡语以外，目前只有一个应对武器被摧毁的扳机，即冰封王座的Grave Shambler
		self.Game.sendSignal("WeaponDestroys", self.ID, None, self, attackwhenDies, "", armedTrigs_WhenDies)
		for trig in self.deathrattles: trig.disconnect()

	"""Handle the mana, durability and stat of weapon."""
	# This method is invoked by Hero class, not a listner.
	def losesDurability(self):
		self.health -= 1
		self.dmgTaken += 1 #可以省掉calcStat
		if self.btn: self.btn.statChangeAni(action="damage")

	"""Handle the weapon being played/equipped."""
	def played(self, target=None, choice=0, mana=0, posinHand=-2, comment=""):
		game = self.Game
		# 使用阶段
		# 连接扳机。比如公正之剑可以触发伊利丹的召唤，这个召唤又反过来触发公正之剑
		self.appears()  #武器已进入Game.weapons列表，但是此时onBoard还是False
		# 注意，暂时不取消已经装备的武器的侦听，比如两把公正之剑可能同时为伊利丹召唤的元素buff。
		# 使用时步骤，触发“每当你使用一张xx牌”的扳机，如伊利丹和无羁元素。
		game.sendSignal("WeaponPlayed", self.ID, self, target, 0, "", choice=0)
		# 结算过载。
		if overload := type(self).overload: game.Manas.overloadMana(overload, self.ID)
		# 使用阶段结束，处理亡语，暂不处理胜负问题。
		# 打出武器牌时，如伊利丹飞刀造成了我方佛丁的死亡，则其装备的灰烬使者会先于该武器加入Game.weapons[ID]。
		# 之后在结算阶段的武器正式替换阶段，打出的该武器顶掉灰烬使者。最终装备的武器依然是打出的这把武器。
		game.gathertheDead()  # 此时被替换的武器先不视为死亡，除非被亡语引起的死亡结算先行替换（如佛丁）。
		# 结算阶段
		target = game.try_RedirectEffectTarget("EffectTarget?", self, target, choice)
		# 根据铜须的存在情况来决定战吼的触发次数。不同于随从，武器的连击目前不会触发
		if game.effects[self.ID]["Battlecry x2"] > 0:
			target = self.whenEffective(target, "", choice, posinHand)
		target = self.whenEffective(target, "", choice, posinHand)
		# 消灭旧武器，并将列表前方的武器全部移除。
		for weapon in game.weapons[self.ID]:
			if weapon != self: weapon.disappears(deathrattlesStayArmed=True)  # 触发“每当你的一把武器被摧毁时”和“每当你的一把武器离场时”的扳机，如南海船工。
		# 打出的这把武器会成为最后唯一还装备着的武器。触发“每当你装备一把武器时”的扳机，如锈水海盗。
		self.setasNewWeapon()  # 此时打出的武器的onBoard才会正式标记为True
		# 结算阶段结束，处理亡语。（此时的亡语结算会包括武器的亡语结算。）
		game.gathertheDead()
	# 完成阶段在Game.playWeapon中处理。


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
		for key in type(self).effects.split(","):
			self.effects[key.strip()] = 1
		self.powerReplaced = powerReplaced

	def canDealDmg(self): return False
	def likeSteadyShot(self): return False
	def countDamageDouble(self):
		return sum(minion.effects["Power Heal&Dmg x2"] > 0 for minion in self.Game.minions[self.ID])

	def calcDamage(self, base):
		return (base + self.effects["Damage Boost"] + self.Game.effects[self.ID]["Power Damage"]) * (2 ** self.countDamageDouble())

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
		self.Game.sendSignal("PowerAppears", self.ID, self, None, 0, "")
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
			if GUI and oldPower.btn and oldPower.btn.np: GUI.seqHolder[-1].append(GUI.FUNC(oldPower.btn.np.removeNode))
			powers[ID].disappears()
		powers[ID] = self
		if GUI: GUI.heroZones[ID].placeCards()
		self.appears()

	def chancesUsedUp(self):
		return self.Game.effects[self.ID]["Power Chance Inf"] < 1 \
			   and self.usageCount >= (1 + (self.Game.effects[self.ID]["Power Chance 2"] > 0))

	def available(self):  # 只考虑没有抉择的技能，抉择技能需要自己定义
		return not self.chancesUsedUp() and (not self.needTarget() or self.findTargets())


	def use(self, target=None, choice=0, sendthruServer=True):
		game = self.Game
		if not game.check_UsePower(self, target, choice):
			return False
		print("Using hero power", self.name)
		# 支付费用，清除费用状态。
		subLocator, tarLocator = game.genLocator(self), game.genLocator(target)
		# 准备游戏操作的动画
		GUI = game.GUI
		game.prepGUI4Ani(GUI)
		if GUI:
			GUI.showOffBoardTrig(self)
			game.eventinGUI(self, eventType="UsePower", target=target, level=0)
		game.Manas.payManaCost(self, self.mana)

		target = game.try_RedirectEffectTarget("EffectTarget?", self, target, choice)
		minionsKilled = 0
		if target and target.category == "Minion" and game.effects[self.ID]["Power Sweep"] > 0:
			targets = game.neighbors2(target)[0]
			minionsKilled += self.effect(target, choice)
			if targets:
				for minion in targets: minionsKilled += self.effect(minion, choice)
		else: minionsKilled += self.effect(target, choice)
		# 结算阶段结束，处理死亡，此时尚不进行胜负判定。
		# 假设触发英雄技能消灭随从的扳机在死亡结算开始之前进行结算。（可能不对，但是相对比较符合逻辑。）
		if minionsKilled > 0:
			game.sendSignal("HeroPowerKilledMinion", game.turn, self, None, minionsKilled, "")
		game.gathertheDead()

		self.usageCount += 1
		# 激励阶段，触发“每当你使用一次英雄技能”的扳机，如激励，虚空形态的技能刷新等。
		game.Counters.powerUsagesThisTurn += 1
		game.sendSignal("HeroUsedAbility", self.ID, self, target, self.mana, "", choice)
		if GUI: GUI.usePowerAni(self)
		# 激励阶段结束，处理死亡。此时可以进行胜负判定。
		game.gathertheDead(True)
		if GUI: GUI.decideCardColors()
		game.moves.append(("Power", subLocator, tarLocator, choice))
		self.Game.wrapUpPlay(GUI, sendthruServer)
		return True

	def effect(self, target, choice=0):
		return 0

	def assistCreateCopy(self, Copy):
		Copy.powerReplaced = self.powerReplaced.createCopy(Copy.Game)


class Spell(Card):
	category = "Spell"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.effects = {"Poisonous": 0, "Lifesteal": 0,
						"Cost Health Instead": 0, "Unplayable": 0,
						}
		for key in type(self).effects.split(","):
			self.effects[key.strip()] = 1

	def reset(self, ID, isKnown=True):
		creator, possi = self.creator, type(self) if isKnown else self.possi
		btn = self.btn
		self.__init__(self.Game, ID)
		self.creator, self.possi = creator, possi
		self.btn = btn

	def available(self):
		return not self.needTarget() or self.selectableCharacterExists()

	def countDamageDouble(self):
		return sum(minion.effects["Spell Heal&Dmg x2"] > 0 for minion in self.Game.minions[self.ID])

	def calcDamage(self, base):
		return (base + self.countSpellDamage()) * (2 ** self.countDamageDouble())

	# 用于由其他卡牌释放法术。这个法术会受到风潮和星界密使的状态影响，同时在结算完成后移除两者的状态。
	# 这个由其他卡牌释放的法术不受泽蒂摩的光环影响。
	# 目标随机，也不触发目标扳机。
	def cast(self, target=None, func=None):
		game, GUI = self.Game, self.Game.GUI
		# 由其他卡牌释放的法术结算相对玩家打出要简单，只需要结算过载，双生法术， 重复释放和使用后的扳机步骤即可。
		# 因为这个法术是由其他序列产生的，所有结束时不会进行死亡处理。
		repeatTimes = 2 if game.effects[self.ID]["Spells x2"] > 0 else 1
		# 多次选择的法术，如分岔路口等会有自己专有的cast方法。
		if not type(self).options: choice = 0
		else: choice = -1 if game.effects[self.ID]["Choose Both"] else numpyRandint(len(self.options))
		if self.needTarget(choice):
			if target and self.targetCorrect(target, choice): pass
			else:  # 如果没有选择目标或者目标实际上不可符合法术的要求，则需要重新选取
				if targets := self.findTargets(choice): #抉择法术选项不同的目标合理性在这里执行
					if func and (preferedTargets := [obj for obj in targets if func(obj)]):
						target = numpyChoice(preferedTargets)
					else: target = numpyChoice(targets)
				else: target = None
		else: target = None

		if GUI:
			GUI.showOffBoardTrig(self)
			game.eventinGUI(self, eventType="CastSpell", target=target)
			GUI.resetSubTarColor(None, target)
		# 在法术要施放两次的情况下，第二次的目标仍然是第一次时随机决定的
		overload = type(self).overload
		for i in range(repeatTimes):
			if overload > 0: game.Manas.overloadMana(overload, self.ID)
			target = self.whenEffective(target, "byOthers", choice, posinHand=-2)
		# 使用后步骤，但是此时的扳机只会触发星界密使和风潮的状态移除。这个信号不是“使用一张xx牌之后”的扳机。
		game.sendSignal("SpellBeenCast", self.ID, self, target, 0, "byOthers", choice=0)
		return target

	# 泽蒂摩加风潮，当对泽蒂摩使用Mutate之后，Mutate会连续两次都进化3个随从
	# 泽蒂摩是在法术开始结算之前打上标记,而非在连续两次之间进行判定。
	# comment = "InvokedbyAI", "Branching-i", ""
	def played(self, target=None, choice=0, mana=0, posinHand=-2, comment=""):
		game, ID, GUI = self.Game, self.ID, self.Game.GUI
		# 使用阶段
		# 判定该法术是否会因为风潮的光环存在而释放两次。发现的子游戏中不会两次触发，直接跳过
		repeatTimes = 2 if game.effects[ID]["Spells x2"] > 0 else 1
		if GUI: GUI.showOffBoardTrig(self)
		# 使用时步骤，触发伊利丹和紫罗兰老师等“每当你使用一张xx牌”的扳机
		game.sendSignal("SpellPlayed", ID, self, target if not isinstance(target, list) else None, mana, "", choice)
		game.sendSignal("Spellboost", ID, self, None, mana, "", choice)
		# 使用阶段结束，进行死亡结算。不处理胜负裁定。
		game.gathertheDead()  # At this point, the minion might be removed/controlled by Illidan/Juggler combo.

		# 进行目标的随机选择和扰咒术的目标改向判定。
		target = game.try_RedirectEffectTarget("EffectTarget?", self, target, choice)
		if target and target.ID == ID:
			game.Counters.spellsonFriendliesThisGame[ID].append(type(self))
			if target.category == "Minion": game.Counters.spellsonFriendlyMinionsThisGame[ID].append(type(self))
		# Zentimo's effect actually an aura. As long as it's onBoard the moment the spell starts being resolved,
		# the effect will last even if Zentimo leaves board early.
		sweep, overload = game.effects[ID]["Spells Sweep"], type(self).overload
		# 没有法术目标，且法术本身是点了需要目标的选项的抉择法术或者需要目标的普通法术。
		for i in range(repeatTimes):
			#两次施放时都获得过载和双生法术牌。
			if overload > 0: game.Manas.overloadMana(overload, ID)
			# When the target is an onBoard minion, Zentimo is still onBoard and has adjacent minions next to it.
			if target and target.category == "Minion" and target.onBoard and sweep > 0 and game.neighbors2(target)[0]:
				neighbors = game.neighbors2(target)[0]
				# 只对中间的目标随从返回法术释放之后的新目标。
				# 用于变形等会让随从提前离场的法术。需要知道后面的再次生效目标。
				target.history["Spells Cast on This"].append(type(self))
				target = self.whenEffective(target, comment, choice, posinHand)
				for minion in neighbors:  # 对相邻的随从也释放该法术。
					minion.history["Spells Cast on This"].append(type(self))
					self.whenEffective(minion, comment, choice, posinHand)
			else:  # The target isn't minion or Zentimo can't apply to the situation. Be the target hero, minion onBoard or inDeck or None.
				# 如果目标不为空而且是在场上的随从，则这个随从的历史记录中会添加此法术的index。
				if target and (target.category == "Minion" or target.category == "Amulet") and target.onBoard:
					target.history["Spells Cast on This"].append(type(self))
				target = self.whenEffective(target, comment, choice, posinHand)

		# 仅触发风潮，星界密使等的光环移除扳机。“使用一张xx牌之后”的扳机不在这里触发，而是在Game的playSpell函数中结算。
		game.sendSignal("SpellBeenCast", game.turn, self, target, 0, "", choice)
		# 使用阶段结束，进行死亡结算，暂不处理胜负裁定。
		game.gathertheDead()  # At this point, the minion might be removed/controlled by Illidan/Juggler combo.
		# 完成阶段：
		# 如果法术具有回响，则将回响牌置入手牌中。因为没有牌可以让法术获得回响，所以可以直接在法术played()方法中处理echo
		# if "~Echo" in self.index:
		#	echoCard = type(minion)(self, game.turn)
		#	trig = Trig_Echo(echoCard)
		#	echoCard.trigsHand.append(trig)
		#	game.Hand_Deck.addCardtoHand(echoCard, ID)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		return target

	def afterDrawingCard(self):
		pass


class Secret(Spell): #法术中有奥秘和任务两个子类，放在race中。Secret/Quest/Sidequest/Questline不会与随从的race发生混淆
	race = "Secret"
	def available(self):
		return self.Game.Secrets.areaNotFull(self.ID) and not self.Game.Secrets.sameSecretExists(self, self.ID)

	def selectionLegit(self, target, choice=0):
		return target is None

	def cast(self, target=None, func=None):
		if self.Game.GUI:
			self.Game.GUI.showOffBoardTrig(self, animationType='', isSecret=True)
			self.Game.eventinGUI(self, eventType="CastSpell")
		self.whenEffective(None, "byOthers", choice=0, posinHand=-2)
		self.Game.sendSignal("SpellBeenCast", self.ID, self, None, 0, "byOthers")

	def played(self, target=None, choice=0, mana=0, posinHand=-2, comment=""):
		if self.Game.GUI:
			self.Game.GUI.showOffBoardTrig(self, animationType='', isSecret=True)
		self.Game.sendSignal("SpellPlayed", self.ID, self, None, mana, "", choice)
		self.Game.sendSignal("Spellboost", self.ID, self, None, mana, "", choice)
		self.Game.gathertheDead()  # At this point, the minion might be removed/controlled by Illidan/Juggler combo.
		self.whenEffective(None, '', choice, posinHand)
		# There is no need for another round of death resolution.
		self.Game.sendSignal("SpellBeenCast", self.ID, self, None, 0, "")

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		secretHD = self.Game.Secrets
		if secretHD.areaNotFull(self.ID) and not secretHD.sameSecretExists(self, self.ID):
			secretHD.secrets[self.ID].append(self)
			for trig in self.trigsBoard: trig.connect()
			if self.Game.GUI: self.Game.GUI.heroZones[self.ID].placeSecrets()
		# secretHD.initSecretHint(self) #Let the game know what possible secrets each player has
		return None

class Quest(Spell):
	race = "Quest"
	# Upper limit of secrets and quests is 5. There can only be one main quest/questline, but multiple different sidequests
	def available(self):
		secretZone = self.Game.Secrets
		if secretZone.areaNotFull(self.ID):
			if self.race == "Sidequest": return all(quest.name != self.name for quest in secretZone.sideQuests[self.ID])
			else: return not secretZone.mainQuests[self.ID] #Only available when there is no other Legendary quests/questlines
		return False

	def selectionLegit(self, target, choice=0):
		return target is None

	def cast(self, target=None, func=None):
		if self.Game.GUI:
			self.Game.GUI.showOffBoardTrig(self)
			self.Game.eventinGUI(self, eventType="CastSpell")
		self.whenEffective(None, "byOthers", choice=0, posinHand=-2)
		self.Game.sendSignal("SpellBeenCast", self.ID, self, None, 0, "byOthers")

	def played(self, target=None, choice=0, mana=0, posinHand=-2, comment=""):
		if self.Game.GUI: self.Game.GUI.showOffBoardTrig(self)
		self.Game.sendSignal("SpellPlayed", self.ID, self, None, mana, "", choice)
		self.Game.sendSignal("Spellboost", self.ID, self, None, mana, "", choice)
		self.Game.gathertheDead()  # At this point, the minion might be removed/controlled by Illidan/Juggler combo.
		self.whenEffective(None, '', choice, posinHand)
		# There is no need for another round of death resolution.
		self.Game.sendSignal("SpellBeenCast", self.ID, self, None, 0, "")
		self.Game.Counters.hasPlayedQuestThisGame[self.ID] = True

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
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
	name, category, description = "", "", ""
	index, effect, isLegendary = '', '', False
	spell = None
	def __init__(self, keeper=None, ID=0): #ID is a placeholder.
		self.keeper, self.ID = keeper, keeper.ID if keeper else ID
		self.category = "Option"
		self.index, self.effect = type(self).index, type(self).effect
		self.isLegendary = type(self).isLegendary
		self.btn = None
	
	def available(self):
		return True


#用于处理卡牌的可能性
class PossiHolder:
	def __init__(self, card, real, possi, creator="", related=()):
		self.real = real #真实的牌类型
		self.possi = possi #可能的牌类型的列表
		self.creator = creator
		self.related = related #一张牌的可能性是可以与其他牌存在互斥关系的，这时盛放其他可能性容器
		self.card = card

	def confirm(self): #自己的可能性完全确定时
		self.possi = [self.real]
		for possiHolder in self.related:
			possiHolder.possi.remove(self.real)
			possiHolder.related.remove(self) #当一个可能性容器被完全确定时，其他的可能性容器就不再与这个可能性相关联

	def ruleOut(self, category): #从这个容器的可能性中移除一个。与此牌相关联的其他牌
		self.possi.remove(category)
		#当一个可能性容器被完全确定时，其他的可能性容器就不再与这个可能性相关联
		if len(self.possi) == 1:
			for possiHolder in self.related:
				possiHolder.possi.remove(self.real)
				possiHolder.related.remove(self)
