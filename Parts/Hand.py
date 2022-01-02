from Parts.ConstsFuncsImports import *
from HS_Cards.AcrossPacks import TheCoin


class Hand_Deck:
	def __init__(self, Game, deck1=None, deck2=None):  # 通过卡组列表加载卡组
		self.Game = Game
		self.hands, self.decks, self.fatigues = {1: [], 2: []}, {1: [], 2: []}, {1: 0, 2: 0}
		self.handUpperLimits = {ID: (9 if hero.Class in SVClasses else 10)
									for ID, hero in self.Game.heroes.items()}
		self.initialDecks = {1: deck1 if deck1 else DefaultDeckCode1, 2: deck2 if deck2 else DefaultDeckCode2}

	"""处理游戏开始和起手换牌"""
	def initialize(self):
		self.initializeDecks()
		self.initializeHands()
		
	#InitializeDecks需要处理很多特殊的卡牌，比如转校生和迦拉克隆等。
	def initializeDecks(self):
		for ID in (1, 2):
			Class = self.Game.heroes[ID].Class  # Hero's class
			for obj in self.initialDecks[ID]:
				if obj.name == "Transfer Student" and hasattr(obj, "transferStudentPool"): obj = obj.transferStudentPool[self.Game.boardID]
				card = obj(self.Game, ID)
				card.mana_0 = card.mana = 0
				if "Galakrond, " in card.name:
					# 检测过程中，如果目前没有主迦拉克隆或者与之前检测到的迦拉克隆与玩家的职业不符合，则把检测到的迦拉克隆定为主迦拉克隆
					if not (gala := self.Game.Counters.primGala[ID]) or (gala.Class != Class and card.Class == Class):
						self.Game.Counters.primGala[ID] = card
				self.decks[ID].append(card)
			numpyShuffle(self.decks[ID])
			for i, card in enumerate(self.decks[ID]): #克苏恩一定不会出现在起始手牌中，只会沉在牌库底，然后等待效果触发后的洗牌
				if card.name == "C'Thun, the Shattered":
					self.decks[ID].insert(0, self.decks[ID].pop(i))
					break
					
	def initializeHands(self):  # 起手要换的牌都已经从牌库中移出到mulligan列表中，
		# 如果卡组有双传说任务，则起手时都会上手
		mainQuests = {1: [], 2: []}
		mulliganSize = {1: 3, 2: 4}
		if self.Game.heroes[2].Class in SVClasses:
			mulliganSize[2] = 3
		for ID in (1, 2):
			#The legendary Quests and Questlines both have description starting with Quest
			mainQuests[ID] = [card for card in self.decks[ID] if "Quest" in card.race]
			numQueststoDraw = min(len(mainQuests[ID]), mulliganSize[ID])
			if numQueststoDraw > 0:
				queststoDraw = numpyChoice(mainQuests[ID], numQueststoDraw, replace=False)
				for quest in queststoDraw:
					removefrom(quest, self.decks[ID])
					self.Game.mulligans[ID].append(quest)
			for i in range(mulliganSize[ID] - numQueststoDraw):
				self.Game.mulligans[ID].append(self.decks[ID].pop())

	"""1P mode. Mulligan and start game immediately"""
	#根据要换掉的牌在起手列表Game.mulligans[ID]中的序号indices决定替换
	def updateMulliganDeck(self, ID, indices): #In self.Game.mulligans are cards that will stay in player's hand
		mulligans = self.Game.mulligans[ID]
		cardstoReplace = [mulligans[i] for i in indices]
		for i in indices: mulligans[i] = self.decks[ID].pop()
		self.decks[ID] += cardstoReplace
		for card in self.decks[ID]: card.entersDeck()  # Cards in deck arm their possible trigDeck
		numpyShuffle(self.decks[ID])  # Shuffle the deck after mulligan

	# 决定是否将硬币置入P2手牌
	def checkifAddCoin2Hand(self, ID):
		if ID == 2 and not self.Game.heroes[2].Class in SVClasses: #影之诗的2号玩家没有硬币
			self.Game.mulligans[2].append((coin := TheCoin(self.Game, 2)))
			coin.creator = Game_PlaceHolder
			return True
		return False

	#Cards finally enters the hand from mulligan
	def moveMulligans2Hand(self, ID):
		cardsChanged, cardsNew = [], []
		ls_Hands = self.Game.Hand_Deck.hands[ID] = []
		for i, card in enumerate(self.Game.mulligans[ID]):
			ls_Hands.append((newCard := card.entersHand(isGameEvent=False)))
			if newCard is not card:
				cardsChanged.append(card)
				cardsNew.append(newCard)
		self.Game.mulligans[ID] = []

		return cardsChanged, cardsNew

	#Both 1P and 2P will share this. Calc manas of cards in hand, Start of Game effects and P1 draws card
	def startofGameEffects_Draw(self, GUI, seq):
		self.Game.Manas.calcMana_All() #Mana change will be animated
		for ID in (1, 2):
			for card in self.hands[ID] + self.decks[ID]:
				if "Start of Game" in card.index:
					if GUI: seq.append(GUI.FUNC(GUI.showOffBoardTrig, card, "Appear"))
					card.startofGame()
		if GUI and GUI.ID == 1: GUI.turnStartAni()
		self.drawCard(1)
		if GUI:
			GUI.decideCardColors()
			GUI.seqReady = True

	# Mulligan for 1P GUIs, where a single player controls all the plays.
	def mulliganBoth(self, indices1, indices2):  # indicesCards是要替换掉的手牌的列表序号，如[0, 2]
		self.updateMulliganDeck(1, indices1)
		self.updateMulliganDeck(2, indices2)
		addCoin = self.checkifAddCoin2Hand(2)

		if GUI := self.Game.GUI:  # 此时hands为空，需要把mulligans移到hands中
			GUI.replaceMulligan_PrepSeqHolder(addCoin=addCoin, for1P=True, ID=1)
			cardsChanged_1, cardsNew_1 = self.moveMulligans2Hand(1)
			cardsChanged_2, cardsNew_2 = self.moveMulligans2Hand(2)
			GUI.mulligan_TransformandMoveCards2Hand(cardsChanged_1 + cardsChanged_2, cardsNew_1 + cardsNew_2)
		self.startofGameEffects_Draw(GUI, GUI.seqHolder[-1] if GUI else None)

	# 双人游戏中一方只控制自己的换牌，之后通过Server进行双方的信息交换
	def mulligan1Side(self, ID, indices):
		self.updateMulliganDeck(ID, indices)
		addCoin = self.checkifAddCoin2Hand(ID)
		
		if GUI := self.Game.GUI: GUI.replaceMulligan_PrepSeqHolder(addCoin=addCoin, for1P=False, ID=ID)
		#2P GUI会调用sendMulliganedDeckHand2Server

	# 在双方给予了自己的手牌和牌库信息之后把它们注册同时触发游戏开始时的效果
	def finalizeHandDeck_StartGame(self):  # This ID is the opponent's ID
		if GUI := self.Game.GUI:
			GUI.seqHolder, GUI.seqReady = [GUI.SEQUENCE()], False
		for ID in (1, 2):  # 直接拿着mulligans开始
			for card in self.decks[ID]: card.entersDeck()
		cardsChanged_1, cardsNew_1 = self.moveMulligans2Hand(1)
		cardsChanged_2, cardsNew_2 = self.moveMulligans2Hand(2)
		if GUI:
			GUI.mulligan_TransformandMoveCards2Hand(cardsChanged_1 + cardsChanged_2, cardsNew_1 + cardsNew_2)
			GUI.turnEndButtonAni_Flip2RightPitch()

		self.startofGameEffects_Draw(GUI, GUI.seqHolder[-1] if GUI else None)

	"""Common methods"""
	def handNotFull(self, ID):
		return len(self.hands[ID]) < self.handUpperLimits[ID]

	def spaceinHand(self, ID):
		return self.handUpperLimits[ID] - len(self.hands[ID])

	def outcastcanTrig(self, card):
		return not (i := self.hands[card.ID].index(card)) or i == len(self.hands[card.ID]) - 1

	def noDuplicatesinDeck(self, ID):
		return len(types := tuple(type(card) for card in self.decks[ID])) == len(set(types))

	def noMinionsinDeck(self, ID):
		return not any(card.category == "Minion" for card in self.decks[ID])
		
	def holdingDragon(self, ID, minion=None, cond=lambda card: True):
		return any("Dragon" in card.race and card is not minion for card in self.hands[ID])

	def holdingBigSpell(self, ID):
		return any(card.category == "Spell" and card.mana >= 5 for card in self.hands[ID])
		
	def holdingCardfromAnotherClass(self, ID, exclude=None):
		Class = self.Game.heroes[ID].Class
		return any(Class not in card.Class and card.Class != "Neutral" and card is not exclude for card in self.hands[ID])


	"""Methods for handling actions regarding cards"""
	#"HandCheck"--COMMENT: "Enter", "Enter_Draw", "Enter_Discover", "Enter_Replace", "Leave"

	# 抽牌一次只能一张，抽到的牌中如果有“抽到时触发”，会马上再抽牌。夺灵者哈卡的堕落之血只会在一次抽牌彻底结束之后才会触发
	# 疲劳伤害不会因为牌库重新出现牌而被清零。下次疲劳时还是相同伤害
	#有加基森拍卖师时，使用神圣愤怒，即使手牌满了被爆掉，仍然可以造成伤害。可能是先检测牌堆顶的卡牌费用。
	#initiator目前只有因抽到时施放的法术或英雄技能抽牌时才会赋予
	#Returns a tuple (cardDrawn, card's original mana, cardEntersHand)
	def drawCard(self, ID, i=-1, initiator=None, cardsDrawn=None):
		game, GUI = self.Game, self.Game.GUI
		if not cardsDrawn: cardsDrawn = []
		#Draw form top of deck, by default
		if deck := self.decks[ID]: mana = (card := deck.pop(i)).mana
		else: #No card in deck
			if game.heroes[ID].Class in SVClasses:
				whoDies = ID if game.heroes[ID].effects["Draw to Win"] < 1 else 3 - ID
				game.heroes[whoDies].dead = True
				game.gathertheDead(True)
			else:
				self.fatigues[ID] += 1
				damage = self.fatigues[ID]
				if GUI: GUI.deckZones[ID].fatigueAni(damage)
				game.heroTakesDamage(ID, damage)
			game.sendSignal("DrawingStops", ID, None, [])
			return None, -1, False #假设疲劳时返回的数值是负数，从而可以区分爆牌（爆牌时仍然返回那个牌的法力值）和疲劳
		#When there is a card drawn from deck
		card.leavesDeck()
		game.sendSignal("DeckCheck", ID, comment="DrawFrom")
		"""尝试把抽到的牌加入手牌"""
		if self.handNotFull(ID):
			if GUI: GUI.drawCardAni_LeaveDeck(card)
			"""目前仅有Dragons的幻化师可以把抽到的牌进行更改。其他的则只作响应"""
			cardHolder = [card]  # 把这张卡放入一个列表，然后抽牌扳机可以对这个列表进行处理同时传递给其他抽牌扳机
			self.Game.Counters.handleGameEvent("DrawCard", ID)
			game.sendSignal("CardDrawn", ID, initiator, cardHolder)
			cardsDrawn.append(card := cardHolder[0])
			#幻化师把手牌中随从变形后才会处理法术和随从的抽到时触发效果。不知道变形出抽到时效果的卡时会如何结算，先假设正常结算。但是担心扳机预检测问题
			if card.category == "Spell" and "Casts When Drawn" in card.index:
				card.playedEffect()
				if GUI: GUI.seqHolder[-1].append(GUI.FUNC(card.btn.np.removeNode))
				#抽到之后施放的法术如果检测到玩家处于濒死状态，则不会再抽一张。如果玩家有连续抽牌的过程，则执行下次抽牌
				if game.heroes[ID].health > 0 and not game.heroes[ID].dead:
					self.drawCard(ID, initiator=card, cardsDrawn=cardsDrawn)
				card.afterDrawingCard()
				game.sendSignal("SpellCastWhenDrawn", ID, None, card)
				return card, mana, False
			else:  # 抽到的牌可以加入手牌。
				if card.category == "Minion" or card.category == "Amulet":
					card.whenDrawn()
				self.hands[ID].append(card)
				if GUI: GUI.drawCardAni_IntoHand(card, card)
				card = self.finalizeCardintoHand(card, ID, comment="Enter_Draw")
				game.Manas.calcMana_Single(card)
				game.sendSignal("DrawingStops", ID, cardsDrawn)
				return card, mana, True
		else:
			if GUI: GUI.millCardAni(card)
			game.sendSignal("DrawingStops", ID, None, cardsDrawn)
			return card, mana, False #假设即使爆牌也可以得到要抽的那个牌的费用，用于神圣愤怒
			
	# Will force the ID of the card to change. obj can be an empty list/tuple
	def addCardtoHand(self, obj, ID, byDiscover=False, pos=-1, ani="fromCenter", creator=None):
		game, GUI = self.Game, self.Game.GUI
		if not isinstance(obj, (list, tuple)): obj = [obj] # if the obj is not a list, turn it into a single-element list
		cards_Final = []
		for card in obj:
			if self.handNotFull(ID):
				if inspect.isclass(card): card = card(game, ID)
				card.ID = ID
				if creator: card.creator = creator
				self.hands[ID].insert(pos + 100 * (pos < 0), card)
				if GUI:
					if ani == "fromCenter":
						if card.btn: GUI.seqHolder[-1].append(GUI.handZones[card.ID].placeCards(add2Queue=False))
						else: GUI.putaNewCardinHandAni(card)
					elif ani == "Twinspell":
						if GUI: GUI.cardReplacedinHand_Refresh(card)
				cards_Final.append(self.finalizeCardintoHand(card, ID, sendSignal=False))
		if cards_Final:
			self.Game.sendSignal("HandCheck", ID, None, cards_Final, 0, "Enter_Discover" if byDiscover else 'Enter')
			game.Manas.calcMana_All()

	#此时card已经进入了hands列表。可以进行index检索
	#Replacing/Adding multiple cards in hand send signal after the all cards have entered.
	def finalizeCardintoHand(self, card, ID, sendSignal=True, comment='Enter'):
		game, card_Final = self.Game, card.entersHand() #卡牌不会连续两次变形
		if card is not card_Final:
			card_Final.inheritEnchantmentsfrom(card)
			self.hands[ID][self.hands[ID].index(card)] = card_Final
			if game.GUI: game.GUI.transformAni(card, card_Final, onBoard=False)

		#在替换手牌的时候旧手牌离开的时候不会发出"CardLeavesHand"信号，只会最后发出"CardinHandReplaced"
		if sendSignal: game.sendSignal("HandCheck", ID, None, [card_Final], 0, comment)
		return card
	
	def replaceCardDrawn(self, targetHolder, newCard, creator=None):
		ID = targetHolder[0].ID
		isPrimaryGalakrond = targetHolder[0] == self.Game.Counters.primGala[ID]
		newCard.creator = creator
		targetHolder[0] = newCard
		if isPrimaryGalakrond: self.Game.Counters.primGala[ID] = newCard

	#newCard must be an instance
	def replace1CardinHand(self, card, newCard, creator=None): #替换单张卡牌，用于在手牌中发生变形时
		ID = card.ID
		card.leavesHand()
		self.hands[ID][self.hands[ID].index(card)] = newCard
		if creator: newCard.creator = creator
		if self.Game.GUI: self.Game.GUI.transformAni(card, newCard, onBoard=False)
		card_Final = self.finalizeCardintoHand(newCard, ID, comment="Enter_Replace")
		self.Game.Manas.calcMana_All()
		return card_Final

	def replaceCardsinHand(self, ID, indices, newCards, creator=None):
		if not indices: return
		hand, cards_Final = self.hands[ID], []
		for i, newCard in zip(indices, newCards):
			hand[i].leavesHand()
			hand[i] = newCard
			if creator: newCard.creator = creator
			cards_Final.append(self.finalizeCardintoHand(newCard, ID, sendSignal=False))
		self.Game.sendSignal("HandCheck", ID, None, cards_Final, 0, "Enter_Replace")
		self.Game.Manas.calcMana_All()
		return cards_Final

	#indices and newCards must be lists or tuples
	def replaceCardsinDeck(self, ID, indices, newCards, creator=None):
		if not indices: return
		deck = self.decks[ID]
		for i, newCard in zip(indices, newCards):
			deck[i].leavesDeck()
			deck[i] = newCard.entersDeck() #加入牌库的牌也可能发生变形，但是可以简化
			if creator: newCard.creator = creator
		self.Game.sendSignal("DeckCheck", ID, None, newCards, comment="Replace")
		
	#Given the index in hand. Can't shuffle multiple cards except for whole hand
	#ID here is the target deck ID, it can be initiated by cards from a different side
	def shuffle_Hand2Deck(self, i, ID, initiatorID, getAll=True):
		if getAll:
			hand = self.extractfromHand(None, ID, getAll, enemyCanSee=False, linger=True)[0]
			for card in hand:
				card.reset(ID)
				self.shuffleintoDeck(card, initiatorID=initiatorID, enemyCanSee=False, sendSig=True)
		else:
			card = self.extractfromHand(i, ID, getAll, enemyCanSee=False, linger=True)[0]
			card.reset(ID)
			self.shuffleintoDeck(card, initiatorID=initiatorID, enemyCanSee=False, sendSig=True)

	# All the cards shuffled will be into the same deck. If necessary, invoke this function for each deck.
	def shuffleintoDeck(self, target, initiatorID=0, enemyCanSee=True, sendSig=True, creator=None):
		if target:
			if not isinstance(target, (list, tuple)): target = (target,) #保证obj是iterable
			ID = target[0].ID
			if self.Game.GUI: self.Game.GUI.shuffleintoDeckAni(target, enemyCanSee)
			#卡牌进入牌库的时候可以发生变形。目前只有Barrens的可升级法术会如此。其entersDeck自行处理creator继承
			objs = []
			for card in target:
				objs.append(newCard := card.entersDeck())
				if creator: newCard.creator = creator
			self.decks[ID] += objs
			numpyShuffle(self.decks[ID])
			if sendSig: self.Game.sendSignal("CardShuffled", initiatorID, None, target)
			self.Game.sendSignal("DeckCheck", ID, None, objs, comment="ShuffleInto")
	
	#def burialRite(self, ID, minions, noSignal=False):
	#	if not isinstance(minions, list):
	#		minions = [minions]
	#	for minion in minions:
	#		self.Game.summonfrom(minion, ID, -1, None, hand_deck=0)
	#		minion.loseAbilityInhand()
	#	for minion in minions:
	#		self.Game.kill(minion, minion)
	#	self.Game.gathertheDead()
	#	if not noSignal:
	#		for minion in minions:
	#			self.Game.Counters.numBurialRiteThisGame[ID] += 1
	#			self.Game.sendSignal("BurialRite", ID, None, minion)

	#card can be a list/tuple(for discarding multiple cards), or can be a single int or card object
	#When discarding multiple cards (not all), the cards must a list/tuple of indices
	def discard(self, ID, cardorInd, getAll=False):
		if getAll or isinstance(cardorInd, (list, tuple)):
			if self.hands[ID]:
				if getAll: cards = self.extractfromHand(None, ID=ID, getAll=True, enemyCanSee=True, linger=False)[0]
				else: cards = [self.extractfromHand(i, ID=ID, enemyCanSee=True, linger=False)[0] for i in reversed(sorted(cardorInd))]
				for card in cards:
					self.Game.Counters.handleGameEvent("DiscardCard", type(card), card.ID)
					card.whenDiscarded()
				self.Game.sendSignal("Discard", ID, None, cards)
				self.Game.Manas.calcMana_All()
				return cards
			return []
		else:  # Discard a chosen card.
			i = cardorInd if isinstance(cardorInd, (int, numpy.int32, numpy.int64)) else self.hands[ID].index(cardorInd)
			(card := self.hands[ID].pop(i)).leavesHand()
			if self.Game.GUI: self.Game.GUI.cardsLeaveHandAni([card], ID=ID, enemyCanSee=True, linger=False)
			self.Game.Counters.handleGameEvent("DiscardCard", type(card), card.ID)
			card.whenDiscarded()
			self.Game.sendSignal("Discard", card.ID, None, [card])
			self.Game.Manas.calcMana_All()
			return [card]
			
	# 只能全部拿出手牌中的所有牌或者拿出一个张，不能一次拿出多张指定的牌
	#cardorInd可以是单个的card object，或者单个序号。也可以是多个序号，需要从左到右
	def extractfromHand(self, cardorInd, ID=0, getAll=False, enemyCanSee=False, linger=False, animate=True):
		if not getAll and not isinstance(cardorInd, (list, tuple)):
			if isinstance(cardorInd, (int, numpy.int32, numpy.int64)): # cardorInd is index
				posinHand = cardorInd if cardorInd < len(self.hands[ID]) - 1 else -1
				card = self.hands[ID].pop(cardorInd)
			else: #ID can be 0 if cardorInd is card Object
				index, cost = self.hands[cardorInd.ID].index(cardorInd), cardorInd.getMana()
				posinHand = index if index < len(self.hands[cardorInd.ID]) - 1 else -1
				card = self.hands[cardorInd.ID].pop(index)
			cost = card.getMana()
			card.leavesHand()
			if animate and self.Game.GUI:
				self.Game.GUI.cardsLeaveHandAni([card], card.ID, enemyCanSee, linger=linger)
			self.Game.sendSignal("HandCheck", card.ID, None, [card], 0, "Leave")
			return card, cost, posinHand
		elif hand := self.hands[ID]:
			if getAll: cards, self.hands[ID] = hand, [] # Extract the entire hand.
			else: cards = [hand.pop(i) for i in reversed(sorted(cardorInd))][::-1] #保证移出的卡牌从左到右排序
			#全部移出手牌和移出指定序号的可以一起处理
			if animate and self.Game.GUI: self.Game.GUI.cardsLeaveHandAni(cards, ID=ID, enemyCanSee=enemyCanSee, linger=linger)
			for card in cards:
				card.leavesHand()
			self.Game.sendSignal("HandCheck", ID, None, cards, 0, "Leave")
				#if sendSignal: self.Game.sendSignal("CardLeavesHand", card.ID, None, card)
			return cards, 0, -2  # -2 means the posinHand doesn't have real meaning.

	# 只能全部拿牌库中的所有牌或者拿出一个张，不能一次拿出多张指定的牌
	def extractfromDeck(self, i=-1, ID=0, getAll=False, enemyCanSee=True, linger=False, animate=True):
		if getAll:  # For replacing the entire deck or throwing it away.
			obj, self.decks[ID] = self.decks[ID], []
			for card in obj: card.leavesDeck()
		else:
			(obj := self.decks[ID].pop(i)).leavesDeck()
			if animate and self.Game.GUI: self.Game.GUI.cardLeavesDeckAni(obj, enemyCanSee=enemyCanSee, linger=linger)
		self.Game.sendSignal("DeckCheck", ID, comment='Leave')
		return obj

	#所有被移除的卡牌都会被展示
	def removeDeckTopCard(self, ID, num=1):
		cards, deck = [], self.decks[ID]
		for _ in range(num):
			if deck: cards.append(self.extractfromDeck(-1, ID)) #Cards removed are always seen by opponent
			else: break
		return cards
		
	def createCopy(self, game):
		if self not in game.copiedObjs:
			game.copiedObjs[self] = Copy = type(self)(game)
			Copy.initialDecks = self.initialDecks
			Copy.fatigues, Copy.handUpperLimits = copy.deepcopy(self.fatigues), copy.deepcopy(self.handUpperLimits)
			Copy.hands = {1: [card.createCopy(game) for card in self.hands[1]],
						  2: [card.createCopy(game) for card in self.hands[2]]}
			Copy.decks = {1: [card.createCopy(game) for card in self.decks[1]],
						  2: [card.createCopy(game) for card in self.decks[2]]}
			return Copy
		else: return game.copiedObjs[self]