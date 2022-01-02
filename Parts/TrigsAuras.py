from Parts.ConstsFuncsImports import *

# 如果memory存了一张卡，复制它；如果只是single类，直接引用；如果是list/tuple，直接复制其内容。
# 存储多张卡或混合类型等复杂情况需要自行定义复制方法
def memory_selfCopy(trig, m, recipient):
	if m:
		if isinstance(m, (list, tuple)): trig.memory = m[:]
		else: trig.memory = recipient.copyCard(m, recipient.ID) if hasattr(m, "category") else m

def memory_createCopy(trig, m, game):
	if m:
		if isinstance(m, (list, tuple)): trig.memory = m[:]
		else: trig.memory = m.createCopy(game) if hasattr(m, "category") else m


#对于随从的场上扳机，其被复制的时候所有暂时和非暂时的扳机都会被复制。
#但是随从返回其额外效果的时候，只有其非暂时场上扳机才会被返回（永恒祭司），暂时扳机需要舍弃。
class TrigBoard:
	signals, inherent, counter = (), True, -1
	changesCard = oneTime = nextAniWaits = False
	def __init__(self, keeper):
		self.keeper, trig = keeper, type(self)
		self.inherent = trig.inherent
		self.counter = trig.counter
		self.memory = [] #默认为列表，卡牌效果可以把这个变成tuple或non-iterable
		self.connected, self.on, self.show = False, False, True

	def connect(self):
		self.connected = True
		trigs = self.keeper.Game.trigsBoard[self.keeper.ID]
		for sig in self.signals: add2ListinDict(self, trigs, sig)

	def disconnect(self):
		self.connected = False
		trigs = self.keeper.Game.trigsBoard[self.keeper.ID]
		for sig in self.signals: removefromListinDict(self, trigs, sig)

	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return True
		
	def trig(self, signal, ID, subject, target, num, comment, choice):
		if self.canTrig(signal, ID, subject, target, num, comment, choice):
			btn, GUI = self.keeper.btn, self.keeper.Game.GUI
			if GUI and (icon := btn.icons["Trigger"] if self.show and btn and "Trigger" in btn.icons else None):
				GUI.seqHolder[-1].append(GUI.FUNC(icon.trigAni))
			if GUI: self.keeper.Game.eventinGUI(self.keeper, "Trigger")
			self.effect(signal, ID, subject, target, num, comment, choice)
			if GUI and self.nextAniWaits: GUI.seqHolder[-1].append(GUI.WAIT(0.7))

	def effect(self, signal, ID, subject, target, num, comment, choice):
		pass

	#当以后effect的处理需要多次连续触发之间传递一些信息时可以用这个目前不需要
	#def effect_useMemo(self, signal, ID, subject, target, num, comment, choice, memory):
	#	pass

	def rngPool(self, identifier):
		typ = type(self.keeper)
		return [card for card in self.keeper.Game.RNGPools[identifier] if card is not typ]

	#一般有特殊的attribute的扳机需要有自己的selfCopy方法
	def selfCopy(self, recipient):
		memory_selfCopy(trig := type(self)(recipient), self.memory, recipient)
		return trig
		
	#这个扳机会在复制随从列表，手牌和牌库列表之前调用，扳机所涉及的随从，武器等会被复制
	#游戏会检查trigsBoard中的每个{signal: trigs},产生一个复制，并注册
	#这里负责处理产生一个trigCopy
	def createCopy(self, game):
		if self in game.copiedObjs: return game.copiedObjs[self] #一个扳机被复制过了，则其携带者也被复制过了
		else: #这个扳机没有被复制过
			game.copiedObjs[self] = trig = type(self)(self.keeper.createCopy(game))
			trig.connected = self.connected
			memory_createCopy(trig, self.memory, game)
			self.assistCreateCopy(trig)
			return trig

	def assistCreateCopy(self, Copy):
		pass

class Trig_Countdown(TrigBoard):
	def resetCount(self, useOrig=True):
		if useOrig: self.counter = type(self).counter

	def connect(self):
		self.connected = True
		trigs = self.keeper.Game.trigsBoard[self.keeper.ID]
		for sig in self.signals: add2ListinDict(self, trigs, sig)

		btn = self.keeper.btn
		changed = self.counter != type(self).counter and btn and "Hourglass" in btn.icons
		self.resetCount(useOrig=False)
		if changed: btn.GUI.seqHolder[-1].append(btn.icons["Hourglass"].seqUpdateText())

	def increment(self, signal, ID, subject, target, num, comment, choice):
		return 1
	
	def trig(self, signal, ID, subject, target, num, comment, choice):
		if self.canTrig(signal, ID, subject, target, num, comment, choice):
			counter_0 = self.counter
			self.counter -= self.increment(signal, ID, subject, target, num, comment, choice)
			self.counter = max(self.counter, 0)
			counter_1, btn = self.counter, self.keeper.btn
			animate = btn and "Hourglass" in btn.icons and counter_0 != self.counter
			if animate: btn.GUI.seqHolder[-1].append(btn.icons["Hourglass"].seqUpdateText())
			self.effect(signal, ID, subject, target, num, comment, choice)
			if animate: btn.GUI.seqHolder[-1].append(btn.icons["Hourglass"].seqUpdateText(animate=counter_1 != self.counter))

class Trig_FreezeDamaged(TrigBoard):
	signals = ("MinionTakesDmg", "HeroTakesDmg",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return subject is self.keeper

	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.freeze(target)


class Trig_SelfAura(TrigBoard):
	def __init__(self, keeper):
		super().__init__(keeper)
		self.show = False

	def trig(self, signal, ID, subject, target, num, comment, choice):
		if self.canTrig(signal, ID, subject, target, num, comment, choice):
			self.effect(signal, ID, subject, target, num, comment, 0)


class TrigHand:
	signals, inherent, changesCard = (), True, True
	def __init__(self, keeper):
		self.keeper, self.inherent = keeper, type(self).inherent

	def connect(self):
		trigs = self.keeper.Game.trigsHand[self.keeper.ID]
		for sig in type(self).signals: add2ListinDict(self, trigs, sig)

	def disconnect(self):
		trigs = self.keeper.Game.trigsHand[self.keeper.ID]
		for sig in type(self).signals: removefromListinDict(self, trigs, sig)

	def trig(self, signal, ID, subject, target, num, comment, choice):
		if self.canTrig(signal, ID, subject, target, num, comment, choice):
			self.effect(signal, ID, subject, target, num, comment, choice)
			
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return True
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		pass

	def rngPool(self, identifier):
		typ = type(self.keeper)
		return [card for card in self.keeper.Game.RNGPools[identifier] if card is not typ]

	def selfCopy(self, recipient):
		return type(self)(recipient)
		
	def createCopy(self, game):
		if self in game.copiedObjs: return game.copiedObjs[self]#一个扳机被复制过了，则其携带者也被复制过了
		else: #这个扳机没有被复制过
			game.copiedObjs[self] = trigCopy = type(self)(self.keeper.createCopy(game))
			self.assistCreateCopy(trigCopy)
			return trigCopy

	def assistCreateCopy(self, Copy):
		pass

class TrigDeck:
	signals, inherent = (), True
	def __init__(self, keeper):
		self.keeper, self.inherent = keeper, type(self).inherent

	def connect(self):
		trigs = self.keeper.Game.trigsDeck[self.keeper.ID]
		for sig in type(self).signals: add2ListinDict(self, trigs, sig)

	def disconnect(self):
		trigs = self.keeper.Game.trigsDeck[self.keeper.ID]
		for sig in type(self).signals: removefromListinDict(self, trigs, sig)

	def trig(self, signal, ID, subject, target, num, comment, choice):
		if self.canTrig(signal, ID, subject, target, num, comment, choice):
			self.effect(signal, ID, subject, target, num, comment, choice)
			
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return True
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		pass

	def rngPool(self, identifier):
		typ = type(self.keeper)
		return [card for card in self.keeper.Game.RNGPools[identifier] if card is not typ]

	def selfCopy(self, recipient):
		return type(self)(recipient)
		
	def createCopy(self, game):
		if self in game.copiedObjs: return game.copiedObjs[self]
		else:
			game.copiedObjs[self] = trigCopy = type(self)(self.keeper.createCopy(game))
			return trigCopy


"""Variants of TrigBoard, TrigHand, TrigDeck"""
class Deathrattle(TrigBoard):
	signals, forceLeave = ("ObjDies", "TrigDeathrattle"), False
	def trig(self, signal, ID, subject, target, num, comment, choice):
		if self.canTrig(signal, ID, subject, target, num, comment, choice):
			game, ID = (kpr := self.keeper).Game, kpr.ID
			if game.GUI: game.GUI.deathrattleAni(kpr)
			for _ in (0, 1) if game.rules[ID][kpr.category+" Deathrattle x2"] > 0 and not self.forceLeave else (0,):
				game.eventinGUI(kpr, "Deathrattle")
				self.effect(signal, ID, subject, target, num, comment, 0)
				game.Counters.handleTrig(self, "Deathrattle")
			#death_Resolution和强制离场的亡语效果会自行处理亡语的取消注册问题
			
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return self.keeper.Game.rules[self.keeper.ID]["Deathrattle X"] < 1 and target is self.keeper

		
class Trig_Secret(TrigBoard):
	#当一个伪扳机可以被触发并开始结算的时候，它会把自己直接移除，同时去除掉这个可能性
	#例如：召唤了一个随从，有两个奥秘：第一个可能是狙击或者寒冰护体，但是实际上是爆炸符文；第二个可能是狙击，但是实际上是冰冻陷阱
		#在结算中，狙击的伪扳机被触发了，需要移除第一个奥秘是狙击的可能性，而寒冰护体的伪扳机无法触发，暂时还不能排除其可能性。
			#真实的爆炸符文触发了，把随从打到了负血
			#第二个奥秘的狙击伪扳机无法再发动了，因为随从已经是负血，所以我们无法得知那个奥秘是不是真的狙击，所以第二个奥秘的可能性是没有变化的
	def trig(self, signal, ID, subject, target, num, comment, choice):
		if self.canTrig(signal, ID, subject, target, num, comment, choice):
			game, ID = (kpr := self.keeper).Game, kpr.ID
			self.disconnect() #Handles removing dummy, too.
			game.Secrets.secrets[ID].remove(kpr)
			for _ in (0, 1) if game.rules[ID]["Secrets x2"] > 0 else (0,):
				if game.GUI:
					game.eventinGUI(kpr, kpr.Class+"SecretTrigger")
					game.GUI.secretTrigAni(kpr)
				self.effect(signal, ID, subject, target, num, comment, 0)
			game.Counters.handleTrig(self, "Secret")
			game.sendSignal("kprRevealed", ID, kpr)


#这个扳机的目标：当随从在回合结束时有多个同类扳机，只会触发第一个，这个可以通过回合ID和自身ID是否符合来决定
class Trig_Borrow(TrigBoard):
	signals = ("TurnEnds",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		#只有当前要结束的回合的ID与自身ID相同的时候可以触发，于是即使有多个同类扳机也只有一个会触发。
		return self.keeper.onBoard and ID == self.keeper.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		#Game的minionSwitchSide方法会自行移除所有的此类扳机。
		self.keeper.Game.minionSwitchSide(self.keeper, activity="Return")
		for trig in self.keeper.trigsBoard[:]:
			if isinstance(trig, Trig_Borrow): self.keeper.losesTrig(trig)


class Trig_Echo(TrigHand):
	card, description = Game_PlaceHolder, "Echo cards disappear at the end of turn"
	signals, changesCard = ("TurnEnds",), True
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return self.keeper.inHand #Echo disappearing should trigger at the end of any turn
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.Game.Hand_Deck.extractfromHand(self.keeper)


class Trig_DieatEndofTurn(TrigBoard):
	signals, inherent = ("TurnEnds",), False
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return self.keeper.onBoard #Even if the current turn is not the minion's owner's turn
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.Game.kill(None, self.keeper)
		
		
class Trig_Quest(TrigBoard):
	counter = 0
	def handleCounter(self, signal, ID, subject, target, num, comment, choice):
		self.counter += 1
	
	def trig(self, signal, ID, subject, target, num, comment, choice):
		if self.canTrig(signal, ID, subject, target, num, comment, choice):
			self.handleCounter(signal, ID, subject, target, num, comment, choice)
			quest, questType = self.keeper, type(self.keeper)
			if quest.btn: quest.btn.trigAni(self.counter)
			if self.counter >= questType.numNeeded:
				game, ID = quest.Game, quest.ID
				self.disconnect()
				removefrom(quest, game.Secrets.mainQuests[ID])
				removefrom(quest, game.Secrets.sideQuests[ID])
				if questType.newQuest: #Only for Questline so far
					newQuest = questType.newQuest(game, ID)
					if quest.btn: quest.btn.finishAni(newQuest=newQuest)
					newQuest.playedEffect()
					game.eventinGUI(quest, "Trigger")
					quest.questEffect(game, ID)
				elif questType.reward: #Only for Questline so far
					card = questType.reward(game, ID)
					if quest.btn: quest.btn.finishAni(reward=card)
					game.eventinGUI(quest, "Trigger")
					quest.addCardtoHand(card, ID)
				else:
					game.eventinGUI(quest, "Trigger")
					quest.questEffect(game, ID)
				
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return True
	
	def questEffect(self, quest, game, ID):
		pass
		
"""Aura receiver and mana receiver"""
class Aura_Receiver:
	# Source is the Aura, not the keeper that creates the aura.
	# Recipient is the minion/weapon/hero that receive the buff
	def __init__(self, recipient, source=None, attGain=0, healthGain=0, effGain=''):
		self.source, self.recipient = source, recipient
		self.attGain, self.healthGain = attGain, healthGain  # Positive by default.
		self.effGain = effGain

	def effectStart(self):
		self.recipient.auraReceivers.append(self)
		self.source.receivers.append(self)
		# Hero, Minion or Weapon
		if self.effGain: self.recipient.getsEffect(self.effGain)
		if self.attGain or self.healthGain: self.recipient.calcStat()

	# Cleanse the receiver from the receiver and delete the (receiver, receiver) from source aura's list.
	def effectClear(self):
		removefrom(self, self.recipient.auraReceivers)
		removefrom(self, self.source.receivers)
		# Hero, Minion or Weapon
		if self.effGain: self.recipient.losesEffect(self.effGain)
		if self.attGain or self.healthGain: self.recipient.calcStat()

	def handleStatMax(self):
		self.recipient.attack += self.attGain
		self.recipient.health_max += self.healthGain

	def effectBack2List(self): #Recipient gets silenced, the aura that still applies will resume
		self.recipient.auraReceivers.append(self)
		if self.effGain: self.recipient.effects[self.effGain] += 1

	def createCopy(self, game, auraCopy):
		if self in game.copiedObjs: return game.copiedObjs[self]
		else:
			game.copiedObjs[self] = Copy = Aura_Receiver(None, auraCopy, self.attGain, self.healthGain, self.effGain)
			return Copy


class ManaMod:
	def __init__(self, recipient, by=0, to=-1, source=None, lowerbound=0, until=-1):
		self.recipient, self.source = recipient, source
		self.by, self.to, self.lowerbound = by, to, lowerbound
		self.until = until

	def handleMana(self):
		if self.by:
			self.recipient.mana += self.by
			self.recipient.mana = max(self.lowerbound, self.recipient.mana)  # 用于召唤传送门的随从减费不小于1的限制。
		elif self.to >= 0:
			self.recipient.mana = self.to

	def applies(self):
		card = self.recipient
		card.manaMods.append(self)  # 需要让卡牌自己也带有一个检测的光环，离开手牌或者牌库中需要清除。
		if card.category == "Power" or card.inHand or card.inDeck:
			card.Game.Manas.calcMana_Single(card)

	def turnEnds(self, turn2End):
		if self.until > -1: removefrom(self, self.recipient.manaMods)

	def getsRemoved(self):
		removefrom(self, self.recipient.manaMods)
		if self.source: removefrom((self.recipient, self), self.source.receivers)

	def selfCopy(self, recipient):  # 只用于游戏内复制卡牌时复制没有光环来源的ManaMod
		return ManaMod(recipient, self.by, self.to, None, self.lowerbound, self.until)

	def createCopy(self, game, auraCopy):  # 跨游戏复制时先不给复制出的ManaMod赋予recipient，由aura自身负责
		if self in game.copiedObjs: return game.copiedObjs[self]
		else:
			game.copiedObjs[self] = Copy = ManaMod(None, self.by, self.to, auraCopy, self.lowerbound, self.until)
			return Copy


"""Aura and mana aura"""
# receiver一定是附属于一个随从的，在复制游戏的过程中，优先会createCopy光环本体，之后是光环影响的随从，
# 随从createCopy过程中会复制出没有source的receiver，所以receiver本身没有必要有createCopy
class Aura_AlwaysOn: #targets = "Others"/"All"/"Neighbors"/"Weapon" 一般的光环是不可能有"Self"的，只有有开启/关闭功能的光环会有"Self"
	signals, attGain, healthGain, effGain, targets = (), 0, 0, '', "Others"
	def __init__(self, keeper):
		self.keeper, self.receivers = keeper, []
		auraType = type(self)
		self.on = True
		self.attGain, self.healthGain, self.effGain = auraType.attGain, auraType.healthGain, auraType.effGain
		if auraType.targets == "Self" or auraType.signals: self.signals = auraType.signals
		elif auraType.targets == "Weapon": self.signals = ("WeaponAppears",)
		elif auraType.targets == "Neighbors": self.signals = ("MinionAppears", "MinionDisappears")
		else: self.signals = ("MinionAppears",) #"All"/"Others"

	def applicable(self, target): return True
	#By default, all other minions showing on the same side are subject to the aura.
	#不是只对相邻随从产生作用的光环的信号默认是("WeaponAppears",)或者是("MinionAppears", "MinionDisappears")
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		if "Appears" in signal: #一个随从上场时，他会先发送自己登场的消息，之后进行自己的光环和扳机检测
			return self.keeper.onBoard and target.ID == self.keeper.ID and target is not self.keeper and self.applicable(target)
		#在一个随从离开场上时，它会在发送信号前就把自己接受的光环清空
		else: return self.keeper.onBoard and target.ID == self.keeper.ID #signal=="MinionDisappears"只有相邻随从光环会设计这个处理

	def findTargets(self):
		keeper, targets = self.keeper, type(self).targets
		if targets == "Neighbors": return keeper.Game.neighbors2(keeper)[0]
		elif targets == "Self": return [keeper]
		elif targets == "Weapon": return keeper.Game.weapons[keeper.ID]
		else: return keeper.Game.minionsonBoard(keeper.ID, exclude=keeper if targets == "Others" else None) #"Others"/"All"

	def checkNeigbors(self): #只有相邻随从光环会设计这个处理
		neighbors = self.keeper.Game.neighbors2(self.keeper)[0]
		for receiver in self.receivers[:]: #先把被光环影响的随从中不再是相邻随从的receiver摘掉
			if receiver.recipient not in neighbors: receiver.effectClear()
		recipients = [receiver.recipient for receiver in self.receivers]
		for minion in neighbors:
			if minion not in recipients: Aura_Receiver(minion, self, self.attGain, self.healthGain, self.effGain).effectStart()

	def applies(self, target):
		if self.on: Aura_Receiver(target, self, self.attGain, self.healthGain, self.effGain).effectStart()

	def trig(self, signal, ID, subject, target, num, comment, choice):
		if self.canTrig(signal, ID, subject, target, num, comment, choice):
			if type(self).targets == "Neighbors": self.checkNeigbors() #只有相邻随从光环会设计这个处理
			elif "Appears" in signal and self.on:
				Aura_Receiver(target, self, self.attGain, self.healthGain, self.effGain).effectStart()

	def auraAppears(self):
		self.on, trigs = True, self.keeper.Game.trigsBoard[self.keeper.ID]
		# Only need to handle minions that appear. Them leaving/silenced will be handled by the Stat_Receiver object.
		for sig in self.signals: add2ListinDict(self, trigs, sig)
		for obj in self.findTargets():
			if self.applicable(obj): Aura_Receiver(obj, self, self.attGain, self.healthGain, self.effGain).effectStart()

	#光环在消失后需要把自己关掉。在群体沉默时可能涉及携带光环的随从也被沉默，所以光环需要知道自己被关闭了
	def auraDisappears(self):
		for receiver in self.receivers[:]: receiver.effectClear()
		self.on, self.receivers, trigs = False, [], self.keeper.Game.trigsBoard[self.keeper.ID]
		for sig in self.signals: removefrom(self, trigs[sig])

	def selfCopy(self, recipient):
		return type(self)(recipient)

	def createCopy(self, game):
		if self in game.copiedObjs: return game.copiedObjs[self]
		else:
			game.copiedObjs[self] = aura = type(self)(self.keeper.createCopy(game))
			for receiver in self.receivers:
				aura.receivers.append((receiverCopy := receiver.createCopy(game, aura)))
				receiverCopy.recipient = receiver.recipient.createCopy(game)
			return aura

	##这个函数会在复制场上扳机列表的时候被调用。
	#def createCopy(self, game):
	#	#一个光环的注册可能需要注册多个扳机
	#	if self in game.copiedObjs: return game.copiedObjs[self]
	#	else:
	#		game.copiedObjs[self] = Copy = self.selfCopy(self.keeper.createCopy(game))
	#		#复制一个随从的时候已经复制了其携带的光环buff状态receiver
	#		#这里只需要找到那个receiver的位置即可
	#		##注意一个随从在复制的时候需要把它的Stat_Receiver，keyWordAura_Reciever和manaMods一次性全部复制之后才能进行光环发出者的复制
	#		#相应地，这些光环receiver的来源全部被标为None，需要在之后处理它们的来源时一一补齐
	#		for minion, receiver in self.receivers:
	#			minionCopy = minion.createCopy(game)
	#			index = minion.auraReceivers.index(receiver)
	#			receiverCopy = minionCopy.auraReceivers[index]
	#			receiverCopy.source = Copy #补上这个receiver的source
	#			Copy.receivers.append((minionCopy, receiverCopy))
	#		return Copy

# 用于一定情况下可以开启光环，对自己/全体/其他随从产生作用。信号都是开启关闭检测和其他随从出现。
#目前没有任何条件光环是对相邻随从生效的，要么全体，要么其他有房随从，要么自己
class Aura_Conditional(Aura_AlwaysOn):
	def whichWay(self): #Decide the aura turns on(1) or off(-1), or does nothing(0)
		return 1

	def	auraAppears(self):
		kpr = self.keeper
		for sig in self.signals: add2ListinDict(self, kpr.Game.trigsBoard[kpr.ID], sig)
		if self.whichWay() > 0:
			self.on = True
			for target in self.findTargets(): Aura_Receiver(target, self, self.attGain, self.healthGain, self.effGain).effectStart()

	def trig(self, signal, ID, subject, target, num, comment, choice):
		if self.canTrig(signal, ID, subject, target, num, comment, choice):
			if "Appears" in signal:
				if self.on: Aura_Receiver(target, self, self.attGain, self.healthGain, self.effGain).effectStart()
			else: #开启关闭检测
				if self.whichWay() > 0:
					self.on = True
					for target in self.findTargets(): Aura_Receiver(target, self, self.attGain, self.healthGain, self.effGain).effectStart()
				elif self.whichWay() < 0:
					self.on = False
					for receiver in self.receivers[:]: receiver.effectClear()


#targets = "All" for now
class GameAura_AlwaysOn:
	cardType, attGain, healthGain, effGain, counter = None, 0, 0, '', 0
	def __init__(self, Game, ID, attGain=0, healthGain=0, effGain=''):
		self.Game, self.ID, self.receivers = Game, ID, []
		self.on, auraType = True, type(self)
		self.card, self.counter = auraType.cardType(Game, ID), auraType.counter
		self.attGain = attGain if attGain else auraType.attGain
		self.healthGain = healthGain if healthGain else auraType.healthGain
		self.effGain = effGain if effGain else auraType.effGain

	def applicable(self, target): return True
	def applies(self, target):
		Aura_Receiver(target, self, self.attGain, self.healthGain, self.effGain).effectStart()

	# By default, all other minions showing on the same side are subject to the aura.
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return target.ID == self.ID and self.applicable(target)

	def trig(self, signal, ID, subject, target, num, comment, choice):
		if self.canTrig(signal, ID, subject, target, num, comment, choice):
			Aura_Receiver(target, self, self.attGain, self.healthGain, self.effGain).effectStart()

	def auraAppears(self):
		trigs = getListinDict(self.Game.trigsBoard[self.ID], "MinionAppears")
		auraType = type(self)
		if aura := next((trig for trig in trigs if isinstance(trig, auraType)), None):
			aura.upgrade()
			if self.counter and aura.card.btn: aura.card.btn.trigAni(aura.counter)
		else:
			trigs.append(self)
			self.Game.trigAuras[self.ID].append(self)
			for minion in self.Game.minionsonBoard(self.ID):
				if self.applicable(minion):
					Aura_Receiver(minion, self, self.attGain, self.healthGain, self.effGain).effectStart()
			if self.Game.GUI: self.Game.GUI.heroZones[self.ID].addaTrig(self.card, text=str(self.counter) if self.counter else '')

	def upgrade(self): #To be overloaded by different auras
		if self.counter and self.card.btn: self.card.btn.trigAni(self.counter)

	# 这个函数会在复制场上扳机列表的时候被调用。
	def createCopy(self, game):
		if self in game.copiedObjs: return game.copiedObjs[self]
		else:
			game.copiedObjs[self] = auraCopy = type(self)(self.Game, self.ID, attGain=self.attGain,
														  healthGain=self.healthGain, effGain=self.effGain)
			auraCopy.counter = self.counter
			for receiver in self.receivers:
				auraCopy.receivers.append((receiverCopy := receiver.createCopy(game, auraCopy)))
				receiverCopy.recipient = receiver.recipient.createCopy(game)
			return auraCopy


class GameRuleAura:
	def __init__(self, keeper):
		self.keeper = keeper

	def auraAppears(self): pass
	def auraDisappears(self): pass

	def selfCopy(self, recipient): #The recipient is the keeper that deals the Aura.
		return type(self)(recipient)
		
	def createCopy(self, game):
		if self in game.copiedObjs: return game.copiedObjs[self]
		else:
			game.copiedObjs[self] = Copy = self.selfCopy(self.keeper.createCopy(game))
			return Copy


#有4种常用的：永久光环/扳机 "Conn&TrigAura", "Conn&TrigAura&OnlyKeepOne"
 			#不用connect的并加入回合开始的 "TurnStart" & "TurnStart&OnlyKeepOne"
 			#不用connect的并加入回合结束的 "TurnEnd"
			#需要connect并加入回合结束的 "Conn&TurnEnd"
			#需要connect但不加入回合开始或结束的 "Conn"
class TrigEffect:
	cardType, signals, counter, trigType, animate = None, (), 0, "Conn&TrigAura", True
	def __init__(self, Game, ID):
		self.Game, self.ID = Game, ID
		self.card, self.counter = type(self).cardType(Game, ID), type(self).counter
		self.memory = []

	def connect(self):
		typeSelf, trigType = type(self), type(self).trigType
		#规定在哪个列表里面寻找相同的可以合并的扳机。
		if "Conn" in trigType: trigs2Search = getListinDict(self.Game.trigsBoard[self.ID], typeSelf.signals[0])
		elif "TurnStart" in trigType: trigs2Search = self.Game.turnStartTrigger
		elif "TurnEnd" in trigType: trigs2Search = self.Game.turnEndTrigger
		else: trigs2Search = self.Game.trigAuras[self.ID]

		if "OnlyKeepOne" in trigType and (trig := next((trig for trig in trigs2Search
														if trig.ID == self.ID and isinstance(trig, typeSelf)), None)):
			trig.counter += self.counter
			if self.counter and trig.card.btn: trig.card.btn.trigAni(trig.counter)
		else: #"TrigAura"|"Conn&TurnEnd"|"TurnEnd"
			if "TurnStart" in trigType: self.Game.turnStartTrigger.append(self)
			elif "TurnEnd" in trigType: self.Game.turnEndTrigger.append(self)
			elif "TrigAura" in trigType: self.Game.trigAuras[self.ID].append(self)
			if "Conn" in trigType:
				for sig in typeSelf.signals: add2ListinDict(self, self.Game.trigsBoard[self.ID], sig)
			if self.Game.GUI: self.Game.GUI.heroZones[self.ID].addaTrig(self.card, text=str(self.counter) if self.counter else '')

	def disconnect(self):
		game, trigType = self.Game, type(self).trigType
		if "TurnStart" in trigType: removefrom(self, game.turnStartTrigger)
		if "TurnEnd" in trigType: removefrom(self, game.turnEndTrigger)
		if "Conn" in trigType:
			for sig in type(self).signals: removefrom(self, game.trigsBoard[self.ID][sig])
		if "TrigAura" in trigType: removefrom(self, game.trigAuras[self.ID])
		if game.GUI: game.GUI.heroZones[self.ID].removeaTrig(self.card)

	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return True

	def trig(self, signal, ID, subject, target, num, comment, choice):
		if self.canTrig(signal, ID, subject, target, num, comment, choice):
			if type(self).animate and self.Game.GUI: self.Game.GUI.showOffBoardTrig(self.card, animationType='')
			self.effect(signal, ID, subject, target, num, comment, choice)

	def effect(self, signal, ID, subject, target, num, comment, choice):
		pass

	def trig_TurnTrig(self):
		if self.Game.GUI: self.Game.GUI.showOffBoardTrig(self.card, animationType="Appear")
		self.trigEffect()
		self.disconnect()

	def trigEffect(self):
		pass

	def createCopy(self, game):  # 不是纯的只在回合结束时触发，需要完整的createCopy
		if self in game.copiedObjs: return game.copiedObjs[self]
		else: # 这个扳机没有被复制过
			game.copiedObjs[self] = trig = type(self)(game, self.ID)
			trig.counter = self.counter
			memory_createCopy(trig, self.memory, game)
			self.assistCreateCopy(trig)
			return trig

	def assistCreateCopy(self, Copy):
		pass


"""Mana Handle"""
#既可以用于随从发出的费用光环，也可用于不寄存在随从实体上的暂时费用光环，如伺机待发等。
#随从发出的光环由随从自己控制光环的开关。
#不寄存于随从身上的光环一般用于一次性的费用结算。而洛欧塞布等持续一个回合的光环没有任何扳机而已
#永久费用光环另行定义
class ManaAura:
	by, to, lowerbound, targets = 0, -1, 0, "Hand"
	def __init__(self, keeper):
		self.keeper, auraType = keeper, type(self)
		self.by, self.to, self.lowerbound = auraType.by, auraType.to, auraType.lowerbound
		self.receivers = []
		
	def applicable(self, target): return True
	#只要是有满足条件的卡牌进入手牌，就会触发这个光环。target是承载这个牌的列表。
	#applicable不需要询问一张牌是否在手牌中。光环只会处理在手牌中的卡牌
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		if signal[0] == "P": return self.keeper.onBoard and self.applicable(target)
		else: self.keeper.onBoard and comment.startswith("Enter") and ID == self.keeper.ID
		
	def trig(self, signal, ID, subject, target, num, comment, choice):
		if self.canTrig(signal, ID, subject, target, num, comment, choice):
			if isinstance(target, (list, tuple)):
				for obj in target: self.applies(obj)
			else: self.applies(target)

	def applies(self, target): #This target is NOT holder.
		if self.applicable(target):
			(manaMod := ManaMod(target, self.by, self.to, self, self.lowerbound)).applies()
			self.receivers.append((target, manaMod))
			
	def auraAppears(self):
		game = self.keeper.Game
		add2ListinDict(self, game.trigsBoard[self.keeper.ID], "HandCheck" if self.targets == "Hand" else "PowerAppears")
		if self.targets == "Hand":
			for card in game.Hand_Deck.hands[1]: self.applies(card)
			for card in game.Hand_Deck.hands[2]: self.applies(card)
			game.Manas.calcMana_All()
		else:
			self.applies(game.powers[1])
			self.applies(game.powers[2])
			game.Manas.calcMana_Powers()

	#When the aura object is no longer referenced, it vanishes automatically.
	def auraDisappears(self):
		for card, manaMod in self.receivers[:]: manaMod.getsRemoved()
		self.receivers = []
		removefrom(self, (kpr := self.keeper).Game.trigsBoard[kpr.ID]["HandCheck" if self.targets == "Hand" else "PowerAppears"])
		kpr.Game.Manas.calcMana_All()
		
	def selfCopy(self, recipient): #The recipient is the keeper that deals the Aura.
		return type(self)(recipient)

	def createCopy(self, game):
		if self in game.copiedObjs: return game.copiedObjs[self]
		else:
			game.copiedObjs[self] = aura = type(self)(self.keeper.createCopy(game))
			for receiver in self.receivers:
				aura.receivers.append((receiverCopy := receiver.createCopy(game, aura)))
				receiverCopy.recipient = receiver.recipient.createCopy(game)
			return aura


#TempManaEffects are supposed be single-usage. If self.temporary, then it expires at the end of turn.
class GameManaAura_OneTime:
	cardType, signals, by, to, lowerBound, targets = None, (), 0, -1, 0, "Hand"
	counter, temporary, nextTurn = 1, True, False
	def __init__(self, Game, ID):
		self.Game, self.ID, self.receivers = Game, ID, []
		self.card, self.counter = self.cardType(Game, ID), self.counter
		if not self.signals: self.signals = ("HandCheck", "ManaPaid") if self.targets == "Hand" else ("PowerAppears", "ManaPaid")
		
	def applicable(self, target): return True
	#"HandCheck"对应以”Enter"开头的comment时且是自己的手牌时就可以触发。卡牌在target中，可以是单体也可以是列表
	#"HandCheck"和"PowerAppears"的卡牌携带在target中，而ManaPaid则是subject中
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		if signal[0] == "H": return comment.startswith("Enter") and ID == self.ID
		else: return self.applicable(subject if signal.startswith("Mana") else target)
		
	def trig(self, signal, ID, subject, target, num, comment, choice):
		if signal[0] == "M":
			self.counter -= 1
			if self.counter < 1: self.auraDisappears()
		else:
			if isinstance(target, (list, tuple)):
				for obj in target: self.applies(obj)
			else: self.applies(target)

	def applies(self, target):
		if self.applicable(target):
			self.receivers.append((manaMod := ManaMod(target, self.by, self.to, self, lowerbound=self.lowerBound)))
			manaMod.applies()

	def text(self): return "=>%d"%self.to if self.to > -1 else ("+" if self.by > 0 else '') + str(self.by)

	def auraAppears(self): #因为费用光环与费用调整之间涉及有光环可能被覆盖的问题，所以光环之间不能合并
		game = self.Game
		game.trigAuras[self.ID].append(self)
		for sig in self.signals: add2ListinDict(self, game.trigsBoard[self.ID], sig)
		if game.GUI: game.GUI.heroZones[self.ID].addaTrig(self.card, text=self.text())

		if type(self).targets == "Hand":
			if type(self).nextTurn: game.Manas.CardAuras_Backup.append(self)
			else: game.Manas.CardAuras.append(self)
			for card in game.Hand_Deck.hands[1]: self.applies(card)
			for card in game.Hand_Deck.hands[2]: self.applies(card)
			game.Manas.calcMana_All()
		else:
			if type(self).nextTurn: game.Manas.PowerAuras_Backup.append(self)
			else: game.Manas.PowerAuras.append(self)
			self.applies(game.powers[1])
			self.applies(game.powers[2])
			game.Manas.calcMana_Powers()

	def auraDisappears(self):
		game = self.Game
		for manaMod in self.receivers[:]: manaMod.getsRemoved()
		self.receivers = []
		trigs = game.trigsBoard[self.ID]
		for sig in self.signals: removefrom(self, trigs[sig])
		removefrom(self, game.trigAuras[self.ID])
		if game.GUI: game.GUI.heroZones[self.ID].removeaTrig(self.card)
		if type(self).targets == "Hand":
			removefrom(self, game.Manas.CardAuras)
			game.Manas.calcMana_All()
		else:
			removefrom(self, game.Manas.PowerAuras)
			game.Manas.calcMana_Powers()

	def createCopy(self, game):
		if self in game.copiedObjs: return game.copiedObjs[self]
		else:
			game.copiedObjs[self] = aura = type(self)(game, self.ID)
			aura.counter = self.counter
			for receiver in self.receivers:
				aura.receivers.append((receiverCopy := receiver.createCopy(game, aura)))
				receiverCopy.recipient = receiver.recipient.createCopy(game)
			return aura


#不直接参与授与Aura_Receiver，而是间接控制临时的aura
class ManaAura_1UsageEachTurn: #For Pint-sized Summoner, Kalecgos, Gamemasteretc
	def __init__(self, keeper):
		self.keeper = keeper
		self.aura = None
	#只要是有满足条件的卡牌进入手牌，就会触发这个光环。target是承载这个牌的列表。
	#applicable不需要询问一张牌是否在手牌中。光环只会处理在手牌中的卡牌
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return self.keeper.onBoard and ID == self.keeper.ID
		
	def trig(self, signal, ID, subject, target, num, comment, choice):
		if self.canTrig(signal, ID, subject, target, num, comment, choice):
			self.aura.auraAppears()

	def auraAppears(self):
		#Typically will be overloaded by each card
		game, ID = self.keeper.Game, self.keeper.ID
		add2ListinDict(self, game.trigsBoard[ID], "TurnStarts")
		if game.turn == ID: #Usually needs a condition
			self.aura = GameManaAura_OneTime(game, ID)
			self.aura.auraAppears()
		#self.aura.auraAppears will handle the calcMana_All()
		#When the aura object is no longer referenced, it vanishes automatically.
	def auraDisappears(self):
		removefrom(self, self.keeper.Game.trigsBoard[self.keeper.ID]["TurnStarts"])
		if self.aura:
			self.aura.auraDisappears() #这个光环只负责（尝试）关掉它的TempManaEffect
			self.aura = None

	def selfCopy(self, recipient): #The recipient is the keeper that deals the Aura.
		return type(self)(recipient)
		
	def createCopy(self, game):
		if self in game.copiedObjs: return game.copiedObjs[self]
		else:
			game.copiedObjs[self] = trigCopy = type(self)(self.keeper.createCopy(game))
			if self.aura: trigCopy.aura = self.aura.createCopy(game)
			return trigCopy