from Parts.ConstsFuncsImports import *
#对卡牌的费用机制的改变
#主要参考贴（冰封王座BB还在的时候）：https://www.diyiyou.com/lscs/news/194867.html
#
#费用的计算方式是对于一张牌，不考虑基础费用而是把费用光环和费用赋值一视同仁，根据其执行顺序来决定倒数第二步的费用，最终如果一张牌有自己赋值或者费用修改的能力，则这个能力在最后处理。
#
#BB给出的机制例子中：AV娜上场之后，热情的探险者抽一张牌，抽到融核巨人之后的结算顺序是：
#	AV的变1光环首先生效，然后探险者的费用赋值把那张牌的费用拉回5，然后融核巨人再根据自己的血量进行减费用。
#确实可以解释当前娜迦沙漠女巫与费用光环和大帝减费的问题。
#1：对方场上一个木乃伊，我方一个沙漠女巫，对方一个木乃伊，然后分别是-1光环，赋值为5，-1光环，法术的费用变成4费
#2：对方场上一个木乃伊，我方一个沙漠女巫，对方一个木乃伊，然后大帝。结算结果是-1光环，赋值为5，-1光环，-1赋值。结果是3费
#3.对方场上一个木乃伊，我方一个沙漠女巫，对方一个木乃伊，然后大帝，然后第一个木乃伊被连续杀死，光环消失。结算是赋值为5，-1光环，-1费用变化。最终那张法术的费用为3.
#4.对方场上一个木乃伊，我方一个沙漠女巫，对方一个木乃伊，然后大帝，第二个木乃伊被连续杀死，则那个法术-1光环，赋值为5，-1费用变化，最终费用为4.（已经验证是确实如此）
#5。对方场上一个木乃伊，我方一个沙漠女巫，对方一个木乃伊，然后大帝，第一个木乃伊被连续杀死，则那个法术会经历赋值为5，-1光环，-1费用变化，变为3费（注意第一个木乃伊第一次死亡的时候会复生出一个新的带光环的木乃伊，然后把费用变成2费，但是再杀死那个复生出来的木乃伊之后，费用就是正确的3费。）
class Manas:
	def __init__(self, Game):
		self.Game = Game
		self.manas = {1:1, 2: 0}
		self.manasUpper = {1:1, 2: 0}
		self.manasLocked = {1: 0, 2: 0}
		self.manasOverloaded = {1: 0, 2: 0}
		self.manas_UpperLimit = {1:10, 2:10}
		self.manas_withheld = {1: 0, 2: 0}
		#CardAuras只存放临时光环，永久光环不再注册于此
		#对于卡牌的费用修改效果，每张卡牌自己处理。
		self.CardAuras, self.CardAuras_Backup = [], []
		self.PowerAuras, self.PowerAuras_Backup = [], []
		
	def updateManaAni(self, ID):
		if GUI := self.Game.GUI:
			GUI.seqHolder[-1].append(GUI.FUNC(GUI.heroZones[ID].drawMana, self.manas[ID], self.manasUpper[ID],
												self.manasLocked[ID], self.manasOverloaded[ID]))

	#If there is no setting mana aura, the mana is simply adding/subtracting.
	#If there is setting mana aura
		#The temp mana change aura works in the same way as ordinary mana change aura.

	'''When the setting mana aura disappears, the calcMana function
	must be cited again for every card in its registered list.'''
	def overloadMana(self, num, ID):
		self.manasOverloaded[ID] += num
		self.updateManaAni(ID)
		self.Game.sendSignal("ManaOverloaded", ID)
		self.Game.sendSignal("OverloadCheck", ID)
		
	def unlockOverloadedMana(self, ID):
		self.manas[ID] += self.manasLocked[ID]
		self.manas[ID] = min(self.manas_UpperLimit[ID], self.manas[ID])
		self.manasLocked[ID] = self.manasOverloaded[ID] = 0
		self.updateManaAni(ID)
		self.Game.sendSignal("OverloadCheck", ID)
		
	def setManaCrystal(self, num, ID):
		self.manasUpper[ID] = num
		if self.manas[ID] > num: self.manas[ID] = num
		self.updateManaAni(ID)
		self.Game.sendSignal("ManaXtlsCheck", ID)
		
	def gainTempManaCrystal(self, num, ID):
		self.manas[ID] += num
		self.manas[ID] = min(self.manas_UpperLimit[ID], self.manas[ID])
		self.updateManaAni(ID)
		
	def gainManaCrystal(self, num, ID):
		self.manas[ID] += num
		self.manas[ID] = min(self.manas_UpperLimit[ID], self.manas[ID])
		self.manasUpper[ID] += num
		self.manasUpper[ID] = min(self.manas_UpperLimit[ID], self.manasUpper[ID])
		self.updateManaAni(ID)
		self.Game.sendSignal("ManaXtlsCheck", ID)
		
	def gainEmptyManaCrystal(self, num, ID):
		before = self.manasUpper[ID]
		if self.manasUpper[ID] + num <= self.manas_UpperLimit[ID]:
			self.manasUpper[ID] += num
			self.updateManaAni(ID)
			self.Game.sendSignal("ManaXtlsCheck", ID)
			return True
		else: #只要获得的空水晶量高于目前缺少的空水晶量，即返回False
			self.manasUpper[ID] = self.manas_UpperLimit[ID]
			self.updateManaAni(ID)
			self.Game.sendSignal("ManaXtlsCheck", ID)
			return before < self.manas_UpperLimit[ID]

	def restoreManaCrystal(self, num, ID, restoreAll=False):
		before = self.manas[ID]
		if restoreAll:
			self.manas[ID] = self.manasUpper[ID] - self.manasLocked[ID]
		else:
			self.manas[ID] += num
			self.manas[ID] = min(self.manas[ID], self.manasUpper[ID] - self.manasLocked[ID])
		after = self.manas[ID]
		self.updateManaAni(ID)
		if after > before: self.Game.sendSignal("ManaXtlsRestore", ID, None, None, after-before)

	def destroyManaCrystal(self, num, ID):
		self.manasUpper[ID] = max(0, self.manasUpper[ID] - num)
		self.manas[ID] = min(self.manas[ID], self.manasUpper[ID])
		self.updateManaAni(ID)
		self.Game.sendSignal("ManaXtlsCheck", ID)

	def checkTradeable(self, subject):
		return "~Tradeable" in subject.index and self.manas[subject.ID] > 0 and self.Game.Hand_Deck.decks[subject.ID]

	def affordable(self, subject):
		ID, mana = subject.ID, subject.getMana()
		if self.cardCostsHealth(subject):
			return mana < self.Game.heroes[ID].health + self.Game.heroes[ID].armor or self.Game.rules[ID]["Immune"] > 0
		else: return mana <= self.manas[ID]
		
	def cardCostsHealth(self, subject):
		return subject.effects["Cost Health Instead"] > 0

	def spendAllMana(self, ID):
		mana = self.manas[ID]
		if mana > 0:
			self.manas[ID] = 0
			self.updateManaAni(ID)
		return mana

	def payManaCost(self, subject, mana): #只有打出手牌和使用英雄技能时会调用，交易手牌时不触发
		#只在需要支付非0的水晶值才会进行下面的处理
		ID, mana = subject.ID, max(0, mana)
		if mana > 0:
			if self.cardCostsHealth(subject): self.Game.heroTakesDamage(ID, mana)
			else: self.manas[ID] -= mana
			if GUI := self.Game.GUI: GUI.seqHolder[-1].append(GUI.FUNC(GUI.heroZones[ID].drawMana, self.manas[ID], self.manasUpper[ID],
													  					self.manasLocked[ID], self.manasOverloaded[ID]))

		self.Game.sendSignal("ManaPaid", ID, subject, None, mana)
		subject.losesEffect("Cost Health Instead", -1)

	#At the start of turn, player's locked mana crystals are removed.
	#Overloaded manas will becomes the newly locked mana.
	def turnStarts(self):
		ID = self.Game.turn
		self.gainEmptyManaCrystal(1, ID)
		self.manasLocked[ID] = self.manasOverloaded[ID]
		self.manasOverloaded[ID] = 0
		self.manas[ID] = max(0, self.manasUpper[ID] - self.manasLocked[ID] - self.manas_withheld[ID])
		GUI = self.Game.GUI
		if GUI: GUI.seqHolder[-1].append(GUI.FUNC(GUI.heroZones[ID].drawMana, self.manas[ID], self.manasUpper[ID],
												  self.manasLocked[ID], self.manasOverloaded[ID]))
		self.Game.sendSignal("OverloadCheck", ID)
		#卡牌的费用光环加载
		i = 0
		while i < len(self.CardAuras_Backup):
			if self.CardAuras_Backup[i].ID == self.Game.turn:
				tempAura = self.CardAuras_Backup.pop(i)
				self.CardAuras.append(tempAura)
				tempAura.auraAppears()
			else: i += 1 #只有在当前aura无法启动时才会去到下一个位置继续检测，否则在pop之后可以在原位置检测
		self.calcMana_All()
		#英雄技能的费用光环加载
		i = 0
		while i < len(self.PowerAuras_Backup):
			if self.PowerAuras_Backup[i].ID == self.Game.turn:
				tempAura = self.PowerAuras_Backup.pop(i)
				self.PowerAuras.append(tempAura)
				tempAura.auraAppears()
			else: i += 1
		self.calcMana_Powers()

	#Manas locked at this turn doesn't disappear when turn ends. It goes away at the start of next turn.
	def turnEnds(self):
		for aura in self.CardAuras + self.PowerAuras:
			if aura.temporary: aura.auraDisappears()
		self.calcMana_All()
		self.calcMana_Powers()

	def calcMana_All(self, comment="HandOnly"):
		#卡牌的法力值计算：从卡牌的的基础法力值开始，优先计算非光环的法力值效果，然后处理光环的法力值效果。最后处理卡牌自身的法力值效果
		cards = self.Game.Hand_Deck.hands[1] + self.Game.Hand_Deck.hands[2]
		if comment == "IncludingDeck":
			cards += self.Game.Hand_Deck.decks[1] + self.Game.Hand_Deck.decks[2]
		for card in cards: self.calcMana_Single(card)
		
	def calcMana_Single(self, card):
		mana_0, card.mana = card.mana, card.mana_0
		auraMods = []
		for manaMod in card.manaMods:
			print(card, manaMod, manaMod.by, manaMod.to, manaMod.source)
			if manaMod.source: auraMods.append(manaMod)
			else: manaMod.handleMana()
		for manaMod in auraMods: manaMod.handleMana()
		#随从的改变自己法力值的效果在此结算。
		if card.inHand: card.selfManaChange()
		if card.mana < 0: card.mana = 0 #费用修改不能把卡的费用降为0
		if card.mana < 1 and ((card.category == "Minion" and card.effects["Echo"] > 0) or (card.category == "Spell" and "Echo" in card.index)):
			card.mana = 1 #如果卡牌有回响，则其法力值不能减少至0
		if card.btn and card.mana != mana_0: card.btn.manaChangeAni(card.mana)
		
	def calcMana_Powers(self):
		for ID in (1, 2):
			power = self.Game.powers[ID]
			mana_0, power.mana = power.mana, power.mana_0
			auraMods = []
			for manaMod in power.manaMods:
				if manaMod.source: auraMods.append(manaMod)
				else: manaMod.handleMana()
			for manaMod in auraMods: manaMod.handleMana()
			if power.mana < 0: power.mana = 0
			if power.btn and mana_0 != power.mana: power.btn.manaChangeAni(power.mana)

	def createCopy(self, game):
		Copy = type(self)(game)
		for key, value in self.__dict__.items():
			if key == "Game" or callable(value):
				pass
			elif "Auras" not in key: #不承载光环的列表都是数值，直接复制即可
				Copy.__dict__[key] = copy.deepcopy(value)
			else: #承载光环和即将加载的光环的列表
				for aura in value:
					Copy.__dict__[key].append(aura.createCopy(game))
		return Copy


class Secrets:
	def __init__(self, Game):
		self.Game = Game
		self.secrets = {1:[], 2:[]}
		self.mainQuests = {1: [], 2: []}
		self.sideQuests = {1:[], 2:[]}

	def areaNotFull(self, ID):
		return len(self.mainQuests[ID]) + len(self.sideQuests[ID]) + len(self.secrets[ID]) < 5

	def spaceinArea(self, ID):
		return 5 - (len(self.mainQuests[ID]) + len(self.sideQuests[ID]) + len(self.secrets[ID]))
		
	#def initSecretHint(self, secret):
	#	game, ID = self.Game, secret.ID
	#	secretCreator, Class = secret.creator, secret.Class
	#	deckSecrets = []
	#	if secret.tracked: #如果一张奥秘在手牌中且可以追踪，则需要做一些操作
	#		game.Hand_Deck.ruleOut(secret, fromHD=2)
	#		deckSecrets = list(secret.possi)
	#	else:
	#		if len(secret.possi) == 1:
	#			for creator, possi in self.Game.Hand_Deck.cards_1Possi[secret.ID]:
	#				if creator is secretCreator:
	#					deckSecrets += [T for T in possi if T.race == "Secret" and T.Class == Class]
	#		else: #如果一张奥秘有多种可能，则它肯定可以匹配到一个
	#			game.Hand_Deck.ruleOut(secret, fromHD=2)
	#			deckSecrets = list(secret.possi)
	#	secret.possi = list(set(deckSecrets))
	#	#需要根据一个奥秘的可能性，把所有可能的奥秘的伪扳机先都注册上
	#	for possi in secret.possi:
	#		if not isinstance(secret, possi): #把那些虚假的可能性都注册一份伪扳机
	#			dummyTrig = possi(game, ID).trigsBoard[0]
	#			#伪扳机和真奥秘之间需要建立双向联系
	#			dummyTrig.dummy, dummyTrig.realSecret = True, secret
	#			dummyTrig.connect()
	#			#game.trigAuras[ID].append(dummyTrig)
	#			secret.dummyTrigs.append(dummyTrig)
	#	for trig in secret.trigsBoard: trig.connect()
		
	def deploySecretsfromDeck(self, ID, initiator, num=1):
		for _ in range(num):
			if self.areaNotFull(ID) and (indices := [i for i, card in enumerate(self.Game.Hand_Deck.decks[ID])
													 if card.race == "Secret" and not self.sameSecretExists(card, ID)]):
				secret = self.Game.Hand_Deck.extractfromDeck(numpyChoice(indices), ID, enemyCanSee=False, animate=False)
				secret.playedEffect()
				self.Game.add2EventinGUI(initiator, secret)
			else: break
		if self.Game.GUI: self.Game.GUI.heroZones[ID].placeCards()
		
	#奥秘被强行移出奥秘区的时候，都是直接展示出来的，需要排除出已知牌
	def extractSecrets(self, ID, index=0, getAll=False, enemyCanSee=True, initiator=None):
		if getAll:
			secrets = []
			while self.secrets[ID]:
				secrets.append((secret := self.secrets[ID].pop()))
				for trig in secret.trigsBoard: trig.disconnect()
			if secrets and self.Game.GUI:
				self.Game.GUI.secretDestroyAni(secrets, enemyCanSee=enemyCanSee)
				self.Game.add2EventinGUI(initiator, secrets)
			return None
		else:
			secret = self.secrets[ID].pop(index)
			for trig in secret.trigsBoard: trig.disconnect()
			if self.Game.GUI:
				self.Game.GUI.secretDestroyAni((secret,), enemyCanSee=enemyCanSee)
				self.Game.add2EventinGUI(initiator, secret)
			return secret
			
	def sameSecretExists(self, secret, ID): #secret can be class or object
		return any(obj.name == secret.name for obj in self.secrets[ID])
			
	#只有Game自己会引用Secrets
	def createCopy(self, game):
		Copy = type(self)(game)
		for ID in (1, 2):
			for secret in self.secrets[ID]:
				Copy.secrets[ID].append(secret.createCopy(game))
			for quest in self.mainQuests[ID]:
				Copy.mainQuests[ID].append(quest.createCopy(game))
			for quest in self.sideQuests[ID]:
				Copy.sideQuests[ID].append(quest.createCopy(game))
		return Copy


class Counters:
	def __init__(self, Game):
		self.Game, self.playersTurnInds = Game, {1: [0], 2: []}
		#Card played. (cardType, subLocator, tarLocator, mana, creator)
		self.cardPlays = {1: [[]], 2: [[]]}
		self.comboCounters = {1: 0, 2: 0}  # Specifically for Combo. Countered spells can trig Combos
		#Obj death. Minion/Weapon/Amulet
		self.deads = [[]]
		self.trigs = [[]] #(Death_BloodmageThalnos, "Deathrattle", ID)
		self.events = [[]] #dmgs/heals/armor/summoning/battle, etc
		"""Counter dedicated to specific cards"""
		#Descent of Dragons.
		self.primGala = {1: None, 2: None}

	"""Turn start and end handling"""
	def turnStarts(self):
		curTurn, turnInd = self.Game.turn, self.Game.turnInd
		self.playersTurnInds[curTurn].append(turnInd)
		self.cardPlays[curTurn].append([])
		self.cardPlays[3-curTurn].append([])

		self.deads.append([])
		self.trigs.append([])
		self.events.append([])

	def turnEnds(self):
		self.comboCounters = {1: 0, 2: 0}

	"""处理打出卡牌。打出卡牌与GameEvent和ObjDeath不同之处在于回合外不会打出卡牌"""
	#如果有多个目标被选择，则tarLocator是一个list，与各target合并并依次放置在tuple的最后
	#No target: 	(type(card), (mana_0, attack_0, health_0, info1, info2, s), subLocator, mana, choice, posinHand, creator)
	#Multi targets: 	上述数组末尾添加(target1, tar1Locator), (target2, tar2Locatr), ...
	def handleCardPlayed(self, card, target, mana, choice, posinHand): #不知道打出的卡牌跑到对面的时候会如果处理，假设不会计入对方打出的牌中
		self.comboCounters[self.Game.turn] += 1
		subLocator, tarLocator = self.Game.getSubTarLocators(card, target)
		tup = (*card.getBareInfo(), subLocator, mana, choice, posinHand, card.creator)
		if target: tup = (*tup, *( (type(o), locator) for o, locator in zip(target, tarLocator) ))
		self.cardPlays[self.Game.turn][-1].append(tup)

	#How to unpack a ET list: ls = [[1, 2], [3, 4], [5, 6], [7, 8], [9, 10], [11, 12]]
	#inds = [1, 3, 5]
	#[ele for l in ls for ele in l]								[1, 2, ~ 11, 12]
	#[ele for i in inds for ele in ls[i]]						[3, 4, 7, 8, 11, 12]
	#[ele for i in reversed(inds) for ele in reversed(ls[i])]	[12, 11, 8, 7, 4, 3]
	def iter_CardPlaysSoFar(self, ID, backwards=False):
		if backwards: return (tup for ls_Turn in reversed(self.cardPlays[ID]) for tup in reversed(ls_Turn))
		else: return (tup for ls_Turn in self.cardPlays[ID] for tup in ls_Turn)

	#turnIndex: -2(None), -1(so far), -1(this turn)
	#return: (type(card), (mana_0, attack_0, health_0, info1, info2, s))
	def examCardPlays(self, ID, turnInd=-1, veri_sum_ls=0, cond=lambda tup: True):
		it = self.cardPlays[ID][turnInd] if turnInd > -1 else (self.iter_CardPlaysSoFar(ID) if turnInd == -1 else ())
		if veri_sum_ls < 2: return (sum if veri_sum_ls else any)(cond(tup) for tup in it)
		else: return [tup[:2] for tup in it if cond(tup)]

	def iter_CardPlays(self, ID, turnInd=-1, backwards=False, cond=lambda tup: True):
		if turnInd > -1:
			it = self.cardPlays[ID][turnInd]
			if backwards: it = reversed(it)
		else: it = self.iter_CardPlaysSoFar(ID, backwards) if turnInd == -1 else ()
		return (tup[:2] for tup in it if cond(tup))

	def examElementalsLastTurn(self, ID, veri_sum=0):
		return self.examCardPlays(ID, turnInd=self.Game.pastTurnInd(ID), veri_sum_ls=veri_sum, cond=lambda tup: "Elemental" in tup[0].race)

	def examSpellsLastTurn(self, ID, veri_sum=0):
		return self.examCardPlays(ID, turnInd=self.Game.pastTurnInd(ID), veri_sum_ls=veri_sum, cond=lambda tup: tup[0].category == "Spell")

	def iter_SpellsonFriendly(self, ID, backwards=False, minionsOnly=False):
		return (tup[:2] for tup in self.Game.Counters.iter_CardPlaysSoFar(ID, backwards=backwards)
					if len(tup) == 8 and tup[0].category == "Spell" and tup[7][1] % 10 == ID and (not minionsOnly or tup[7][0].category == "Minion"))

	"""All card play tups cond will start with checkTup_ so it's easier to track all of them"""
	#(type(card), bareInfo, subLocator, mana, choice, posinHand, creator)
	def checkTup_SpellonFriendly(self, tup, ID, minionsOnly=False):
		#Only consider spells cast on single target. Ignore multiple-target cases. #7th would be (target, tarLocator)
		return len(tup) == 8 and tup[0].category == "Spell" and tup[7][1] % 10 == ID \
						   and (not minionsOnly or tup[7][0].category == "Minion")

	def checkTup_BigSpell(self, tup):
		return tup[0].category == "Spell" and tup[3] >= 5

	"""处理游戏中发生的事件。这些事件都是以回合为单位存储"""
	#("Damage", game.genLocator(dmgDealer), game.genLocator(dmgTaker), damage)
	#("Heal", self.ID, healActual, tarLocator)
	#("GainArmor", ID, armor)
	#("HeroHealthChange", self.ID)
	#("Summon", type(subject), subject.ID)
	#("Battle", subLocator, tarLocator)
	#("DrawCard", ID)
	#("DiscardCard", card, ID)
	#("AddCard2Hand", card, ID)
	def handleGameEvent(self, eventType, *args):  # sub/tar can be real objects or locators
		self.events[-1].append((eventType, *args))

	# deads: #(TeronGorefiend, (mana_0, attack_0, health_0, ....), ID)
	def handleObjDeath(self, obj):
		self.deads[-1].append((*obj.getBareInfo(), obj.ID))

	# trigs: (Death_BoomBot, "Deathrattle", self.keeper.ID)
	def handleTrig(self, trig, trigType):
		self.trigs[-1].append((type(trig), trigType, trig.keeper.ID))

	#ls should be like [[], [], []]
	def iter_TupsSoFar(self, lsName, backwards=False):
		ls = self.__dict__[lsName]
		if backwards: return (tup for ls_Turn in reversed(ls) for tup in reversed(ls_Turn))
		else: return (tup for ls_Turn in ls for tup in ls_Turn)

	#veri_sum_ls=0:check if certain dead obj exists; 1: count certain dead objs; others: [(card, info)]
	def examDeads(self, ID, turnInd=-1, category="Minion", veri_sum_ls=0, cond=lambda card: True):
		it = self.deads[turnInd] if turnInd > -1 else (self.iter_TupsSoFar("deads") if turnInd == -1 else ())
		if veri_sum_ls:
			ls = [(card, info) for card, info, Id in it if Id == ID and card.category == category and cond(card)]
			return len(ls) if veri_sum_ls == 1 else ls
		else: return any(Id == ID and card.category == category and cond(card) for card, _, Id in it)

	def examHeroAtks(self, ID, turnInd=-1, veri_sum=0):
		it = self.events[turnInd] if turnInd > -1 else (self.iter_TupsSoFar("events") if turnInd == -1 else ())
		return (sum if veri_sum else any)(tup[0] == "Battle" and tup[1] % 100 == 10 + ID for tup in it)

	def examHealThisTurn(self, ID, veri_sum=0):
		return (sum if veri_sum else any)(tup[2] for tup in self.Game.Counters.events[-1] if tup[0] == "Heal" and tup[1] == ID)

	def examDmgonHero(self, ID, turnInd=-1, veri_sum=0):
		it = self.events[turnInd] if turnInd > -1 else (self.iter_TupsSoFar("events") if turnInd == -1 else ())
		return (sum if veri_sum else any)(tup[3] for tup in it if tup[0] == "Damage" and tup[2] % 100 == 10 + ID)

	def examCardsDrawnThisTurn(self, ID, veri_sum=0):
		return (sum if veri_sum else any)(tup[0] == "DrawCard" and tup[1] == ID for tup in self.Game.Counters.events[-1])

	# 只有Game自己会引用Counters
	def createCopy(self, game):
		Copy = type(self)(game)
		Copy.cardPlays, Copy.comboCounter = copy.deepcopy(self.cardPlays), copy.deepcopy(self.comboCounters)
		Copy.deads, Copy.trigs, Copy.events = copy.deepcopy(self.deads), copy.deepcopy(self.trigs), copy.deepcopy(self.events)
		Copy.primGala = copy.deepcopy(self.primGala)
		return Copy


class Discover:
	def __init__(self, Game):
		self.Game = Game

	def startDiscover(self, options):
		if self.Game.GUI:
			self.Game.options = options
			i = options.index(card := self.Game.GUI.waitforDiscover())
			self.Game.options = []
			return card, i

	#For Hearthstone target selection during effect resolution
	def startChoose(self, initiator, effectType, ls):
		if self.Game.GUI:
			self.Game.options = []
			return (option := self.Game.GUI.waitforChoose(ls)), ls.index(option) #The GUI needs to know the legal targets

	def startFusion(self, initiator, validTargets):
		if self.Game.GUI:
			self.Game.GUI.waitforFusion(validTargets)

	def typeCardName(self, initiator):
		if self.Game.GUI:
			self.Game.GUI.wishforaCard(initiator)

	#除了Game本身，没有东西会在函数外引用Game.Discover
	def createCopy(self, game):
		return type(self)(game)
