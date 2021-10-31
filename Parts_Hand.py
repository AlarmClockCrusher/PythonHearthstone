from HS_AcrossPacks import TheCoin


class Game_PlaceHolder:
	name, mana, category, race, school  = "Game", -1, "Spell", "", ""
	name_CN = "游戏进程"
	def __init__(self, Game, ID):
		self.Game, self.ID = Game, ID
		self.name, self.category, self.race, self.school = "Game", "Spell", "", ""
		self.mana, self.creator = -1, None
		self.onBoard = self.inHand = self.inDeck = False
		self.index = "CORE~~Spell~1~Holy~Game_PlaceHolder"
		self.enchantments = self.trigsBoard = self.trigsHand = self.trigsDeck = self.deathrattles = []
		self.btn = None

	def text(self): return ''


class Hand_Deck:
	def __init__(self, Game, deck1=None, deck2=None):  # 通过卡组列表加载卡组
		self.Game = Game
		self.hands = {1: [], 2: []}
		self.decks = {1: [], 2: []}
		self.noCards = {1: 0, 2: 0}
		self.handUpperLimit = {1: 10, 2: 10}
		if self.Game.heroes[1].Class in SVClasses:
			self.handUpperLimit[1] = 9
		if self.Game.heroes[2].Class in SVClasses:
			self.handUpperLimit[2] = 9
		self.category = ''
		self.initialDecks = {1: deck1 if deck1 else Default1, 2: deck2 if deck2 else Default2}
		#self.cards_1Possi = {1:[], 2:[]} #可以明确知道是哪一张的全部资源牌
		#self.cards_XPossi = {1:[], 2:[]} #只知道这张牌可能是什么的资源牌
		#self.trackedHands = {1:[], 2:[]} #可以追踪的手牌，但是它们可能明确知道是哪一张，也可能是只知道可能是什么的手牌
		
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
				if "Galakrond, " in card.name:
					# 检测过程中，如果目前没有主迦拉克隆或者与之前检测到的迦拉克隆与玩家的职业不符合，则把检测到的迦拉克隆定为主迦拉克隆
					if self.Game.Counters.primaryGalakronds[ID] is None or (
							self.Game.Counters.primaryGalakronds[ID].Class != Class and card.Class == Class):
						self.Game.Counters.primaryGalakronds[ID] = card
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
	
	#Mulligan for 1P GUIs, where a single player controls all the plays.
	def mulliganBoth(self, indices1, indices2):
		#不涉及GUI的部分
		indices = {1: indices1, 2: indices2}  # indicesCards是要替换的手牌的列表序号，如[1, 3]
		GUI = self.Game.GUI
		for ID in (1, 2):
			cardstoReplace = []
			# self.Game.mulligans is the cards currently in players' hands.
			if indices[ID]:
				for num in range(1, len(indices[ID]) + 1):
					# 起手换牌的列表mulligans中根据要换掉的牌的序号从大到小摘掉，然后在原处补充新手牌
					cardstoReplace.append(self.Game.mulligans[ID].pop(indices[ID][-num]))
					self.Game.mulligans[ID].insert(indices[ID][-num], self.decks[ID].pop())
			self.decks[ID] += cardstoReplace
			for card in self.decks[ID]: card.entersDeck()  # Cards in deck arm their possible trigDeck
			numpyShuffle(self.decks[ID])  # Shuffle the deck after mulligan
			# 手牌和牌库中的牌调用entersHand和entersDeck,注册手牌和牌库扳机
		
		#决定是否将硬币置入玩家手牌，同时如果手牌中有进入时会变形的牌，则需要改变
		addCoin = False
		if not self.Game.heroes[2].Class in SVClasses:
			self.Game.mulligans[2].append((coin := TheCoin(self.Game, 2)))
			coin.creator = Game_PlaceHolder
			addCoin = True
		if GUI:
			#在这里生成Sequence，然后存储在seqHolder[-1]里面
			GUI.mulligan_NewCardsfromDeckAni(addCoin)
			#The cards are added into hands and the sequence is further extended
			GUI.mulligan_MoveCards2Hand()
			self.Game.Manas.calcMana_All() #Mana change will be animated
			for ID in (1, 2):
				for card in self.hands[ID] + self.decks[ID]:
					if "Start of Game" in card.index:
						GUI.seqHolder[-1].append(GUI.FUNC(GUI.showOffBoardTrig, card, "Appear"))
						card.startofGame()
			
			GUI.turnStartAni()
			self.drawCard(1)
			GUI.decideCardColors()
			GUI.seqReady = True
		else:
			self.Game.Manas.calcMana_All()  #Mana change will be animated
			for ID in (1, 2):
				for card in self.hands[ID] + self.decks[ID]:
					if "Start of Game" in card.index:
						card.startofGame()
			self.drawCard(1)
		
	# 双人游戏中一方很多控制自己的换牌，之后两个游戏中复制对方的手牌和牌库信息
	def mulligan1Side(self, ID, indices):
		GUI = self.Game.GUI
		cardstoReplace = []
		if indices:
			for num in range(1, len(indices) + 1):
				cardstoReplace.append(self.Game.mulligans[ID].pop(indices[-num]))
				self.Game.mulligans[ID].insert(indices[-num], self.decks[ID].pop())
		#self.hands[ID] = self.Game.mulligans[ID]
		self.decks[ID] += cardstoReplace
		numpyShuffle(self.decks[ID])

		addCoin = False
		#如果玩家操纵的是2号的话，则把硬币置入手牌中
		if ID == 2 and not self.Game.heroes[2].Class in SVClasses:
			self.Game.mulligans[2].append((coin := TheCoin(self.Game, 2)))
			coin.creator = Game_PlaceHolder
			addCoin = True
		if GUI:
			GUI.mulligan_NewCardsfromDeckAni(ID, addCoin)
			#调度得到的牌已经被 移入手牌Hand_Deck.hands里面，mulligans也被清空
		else: pass
		
	# 在双方给予了自己的手牌和牌库信息之后把它们注册同时触发游戏开始时的效果
	def finalizeHandDeck_StartGame(self):  # This ID is the opponent's ID
		for ID in (1, 2):  # 直接拿着mulligans开始
			self.hands[ID] = [card.entersHand() for card in self.hands[ID]]
			for card in self.decks[ID]: card.entersDeck()
			self.Game.mulligans[ID] = []
		
		GUI = self.Game.GUI
		if GUI:
			GUI.seqReady = False
			GUI.seqHolder = [GUI.SEQUENCE(GUI.FUNC(GUI.deckZones[1].draw, len(self.decks[1]), len(self.hands[1])),
										  GUI.FUNC(GUI.deckZones[2].draw, len(self.decks[2]), len(self.hands[2])),
										  )]
			GUI.seqHolder[-1].append(GUI.PARALLEL(GUI.handZones[1].placeCards(False), GUI.handZones[2].placeCards(False))
									 )
			GUI.turnEndButtonAni_Flip2RightPitch()
			
		self.Game.Manas.calcMana_All()
		for ID in (1, 2):
			for card in self.hands[ID] + self.decks[ID]:
				if "Start of Game" in card.index:
					if GUI: GUI.seqHolder[-1].append(GUI.FUNC(GUI.showOffBoardTrig, card, "Appear"))
					card.startofGame()
		if GUI and GUI.ID == 1: GUI.turnStartAni()
		self.drawCard(1)
		if GUI:
			GUI.decideCardColors()
			GUI.seqReady = True

	def handNotFull(self, ID):
		return len(self.hands[ID]) < self.handUpperLimit[ID]

	def spaceinHand(self, ID):
		return self.handUpperLimit[ID] - len(self.hands[ID])

	def outcastcanTrig(self, card):
		posinHand = self.hands[card.ID].index(card)
		return posinHand == 0 or posinHand == len(self.hands[card.ID]) - 1

	def noDuplicatesinDeck(self, ID):
		record = []
		for card in self.decks[ID]:
			if type(card) not in record: record.append(type(card))
			else: return False
		return True

	def noMinionsinDeck(self, ID):
		return not any(card.category == "Minion" for card in self.decks[ID])
		
	def noMinionsinHand(self, ID, minion=None):
		return not any(card.category == "Minion" and card is not minion for card in self.hands[ID])
		
	def holdingDragon(self, ID, minion=None):
		return any(card.category == "Minion" and "Dragon" in card.race and card is not minion \
				for card in self.hands[ID])
				
	def holdingSpellwith5CostorMore(self, ID):
		return any(card.category == "Spell" and card.mana >= 5 for card in self.hands[ID])
		
	def holdingCardfromAnotherClass(self, ID, exclude=None):
		Class = self.Game.heroes[ID].Class
		return any(Class not in card.Class and card.Class != "Neutral" and card != exclude for card in self.hands[ID])
						
	# 抽牌一次只能一张，需要废除一次抽多张牌的功能，因为这个功能都是用于抽效果指定的牌。但是这些牌中如果有抽到时触发的技能，可能会导致马上抽牌把列表后面的牌提前抽上来
	# 如果这个规则是正确的，则在牌库只有一张夺灵者哈卡的堕落之血时，抽到这个法术之后会立即额外抽牌，然后再塞进去两张堕落之血，那么第二次抽法术可能会抽到新洗进去的堕落之血。
	# Damage taken due to running out of card will keep increasing. Refilling the deck won't reset the damage you take next time you draw from empty deck
	#Returns a tuple (cardDrawn, card's mana, cardEntersHand)
	def drawCard(self, ID, card=None):
		game, GUI = self.Game, self.Game.GUI
		if card is None:  # Draw from top of the deck.
			if self.decks[ID]:  # Still have cards left in deck.
				card = self.decks[ID].pop()
				mana = card.mana
			else:
				if game.heroes[ID].Class in SVClasses:
					whoDies = ID if game.heroes[ID].effects["Draw to Win"] < 1 else 3 - ID
					game.heroes[whoDies].dead = True
					game.gathertheDead(True)
				else:
					self.noCards[ID] += 1
					damage = self.noCards[ID]
					if GUI: GUI.deckZones[ID].fatigueAni(damage)
					game.heroTakesDamage(ID, damage)
				return None, -1, False #假设疲劳时返回的数值是负数，从而可以区分爆牌（爆牌时仍然返回那个牌的法力值）和疲劳
		else:
			if isinstance(card, (int, numpy.int32, numpy.int64)): card = self.decks[ID].pop(card)
			else: removefrom(card, self.decks[ID])
			mana = card.mana
		card.leavesDeck()
		game.sendSignal("DeckCheck", ID, None, None, 0, "")
		if self.handNotFull(ID):
			#Draw a card at the deckZone and move it to the pausePos
			if GUI: GUI.drawCardAni_LeaveDeck(card)
			cardTracker = [card]  # 把这张卡放入一个列表，然后抽牌扳机可以对这个列表进行处理同时传递给其他抽牌扳机
			self.Game.Counters.numCardsDrawnThisTurn[ID] += 1
			game.sendSignal("CardDrawn", ID, None, cardTracker, mana, "")
			if cardTracker[0].category == "Spell" and "Casts When Drawn" in cardTracker[0].index:
				card2Cast = cardTracker[0]
				if GUI: GUI.seqHolder[-1].append(GUI.FUNC(card2Cast.btn.np.removeNode))
				card2Cast.whenEffective()
				game.sendSignal("SpellCastWhenDrawn", ID, None, card2Cast, mana, "")
				#抽到之后施放的法术如果检测到玩家处于濒死状态，则不会再抽一张。如果玩家有连续抽牌的过程，则执行下次抽牌
				if game.heroes[ID].health > 0 and not game.heroes[ID].dead:
					self.drawCard(ID)
				cardTracker[0].afterDrawingCard()
				return cardTracker[0], mana, False
			else:  # 抽到的牌可以加入手牌。
				if cardTracker[0].category == "Minion" or cardTracker[0].category == "Amulet":
					cardTracker[0].whenDrawn()
				card_Final = cardTracker[0].entersHand()
				self.hands[ID].append(cardTracker[0])
				if GUI: GUI.drawCardAni_IntoHand(card, cardTracker[0])
				game.sendSignal("CardEntersHand", ID, None, cardTracker, mana, "byDrawing")
				if cardTracker[0] != card_Final:
					card_Final.inheritEnchantmentsfrom(cardTracker[0])
					self.replaceCardinHand(cardTracker[0], card_Final, cardTracker[0].creator, calcMana=False)
				game.Manas.calcMana_All()
				return cardTracker[0], mana, True
		else:
			if GUI: GUI.millCardAni(card)
			return card, mana, False #假设即使爆牌也可以得到要抽的那个牌的费用，用于神圣愤怒
			
	# def createCard(self, obj, ID, comment)
	# Will force the ID of the card to change. obj can be an empty list/tuple
	#Creator是这张/些牌的创建者，creator=None，则它们的creator继承原来的。
	#possi是这张/些牌的可能性，possi=()说明它们都是确定的牌
	def addCardtoHand(self, obj, ID, byDiscover=False, pos=-1, ani="fromCenter", creator=None):
		game, GUI = self.Game, self.Game.GUI
		if not isinstance(obj, (list, numpy.ndarray, tuple)):  # if the obj is not a list, turn it into a single-element list
			obj = [obj]
		for card in obj:
			if self.handNotFull(ID):
				if inspect.isclass(card): card = card(game, ID)
				card.ID, card.creator = ID, creator
				self.hands[ID].insert(pos + 100 * (pos < 0), card)
				if GUI:
					if ani == "fromCenter":
						if card.btn: GUI.seqHolder[-1].append(GUI.handZones[card.ID].placeCards(add2Queue=False))
						else: GUI.putaNewCardinHandAni(card)
					elif ani == "Twinspell":
						if GUI: GUI.cardReplacedinHand_Refresh(card)
				card_Final = card.entersHand()
				game.sendSignal("CardEntersHand", ID, None, [card], 0, "")
				if byDiscover: game.sendSignal("PutinHandbyDiscover", ID, None, obj, 0, '')
				if card != card_Final:
					card_Final.inheritEnchantmentsfrom(card)
					self.replaceCardinHand(card, card_Final, creator, calcMana=False)
			else:
				self.Game.Counters.shadows[ID] += 1
		game.Manas.calcMana_All()
		
	def replaceCardDrawn(self, targetHolder, newCard, creator=None):
		ID = targetHolder[0].ID
		isPrimaryGalakrond = targetHolder[0] == self.Game.Counters.primaryGalakronds[ID]
		newCard.creator = creator
		targetHolder[0] = newCard
		if isPrimaryGalakrond: self.Game.Counters.primaryGalakronds[ID] = newCard
		
	#newCard must be an instance
	def replaceCardinHand(self, card, newCard, creator=None, calcMana=True): #替换单张卡牌，用于在手牌中发生变形时
		ID = card.ID
		card.leavesHand()
		self.hands[ID][self.hands[ID].index(card)] = newCard
		newCard.ID, newCard.creator = ID, creator
		#加入手牌的牌可能会变化
		newCard_Final = newCard.entersHand()
		
		if self.Game.GUI: self.Game.GUI.transformAni_inHand(card, newCard)
		
		self.Game.sendSignal("CardLeavesHand", ID, None, card, 0, '')
		self.Game.sendSignal("CardEntersHand", ID, None, [newCard], 0, "")
		
		if newCard != newCard_Final:
			newCard_Final.inheritEnchantmentsfrom(newCard)
			self.replaceCardinHand(newCard, newCard_Final, creator=newCard.creator)
		if calcMana: self.Game.Manas.calcMana_All()
		
	#目前只有牌库中的迦拉克隆升级时会调用，对方是可以知道的
	def replaceCardinDeck(self, card, newCard, creator=None):
		if card in (deck := self.decks[card.ID]):
			card.leavesDeck()
			deck[deck.index(card)] = newCard
			newCard.creator = creator
			self.Game.sendSignal("DeckCheck", card.ID, None, None, 0, "")
		
	def replaceWholeDeck(self, ID, newCards, creator=None):
		self.extractfromDeck(0, ID, getAll=True)
		self.decks[ID] = newCards
		for card in newCards:
			card.entersDeck()
			card.creator = creator
		self.Game.sendSignal("DeckCheck", ID, None, None, 0, "")
		
	def replacePartofDeck(self, ID, indices, newCards, creator=None):
		for card in newCards: card.leavesDeck()
		deck = self.decks[ID]
		for i, oldCard, newCard in zip(indices, deck, newCards):
			oldCard.leavesDeck()
			deck[i] = newCard
			newCard.creator = creator
			newCard.entersDeck()
		self.Game.sendSignal("DeckCheck", ID, None, None, 0, "")
		
	#Given the index in hand. Can't shuffle multiple cards except for whole hand
	#ID here is the target deck ID, it can be initiated by cards from a different side
	def shuffle_Hand2Deck(self, i, ID, initiatorID, shuffleAll=True):
		if shuffleAll:
			hand = self.extractfromHand(None, ID, shuffleAll, enemyCanSee=False, linger=True)[0]
			for card in hand:
				card.reset(ID, isKnown=False)
				self.shuffleintoDeck(card, initiatorID=initiatorID, enemyCanSee=False, sendSig=True)
		else:
			card = self.extractfromHand(i, ID, shuffleAll, enemyCanSee=False, linger=True)[0]
			card.reset(ID, isKnown=False)
			self.shuffleintoDeck(card, initiatorID=initiatorID, enemyCanSee=False, sendSig=True)

	# All the cards shuffled will be into the same deck. If necessary, invoke this function for each deck.
	# PlotTwist把手牌洗入牌库的时候，手牌中buff的随从两次被抽上来时buff没有了。
	# 假设洗入牌库这个动作会把一张牌初始化
	def shuffleintoDeck(self, obj, initiatorID=0, enemyCanSee=True, sendSig=True, creator=None):
		if obj:
			#如果obj不是一个Iterable，则将其变成一个列表
			if not isinstance(obj, (list, tuple, numpy.ndarray)):
				obj = [obj]
			ID = obj[0].ID
			self.decks[ID] += obj
			for card in obj:
				card.entersDeck()
				card.creator = creator
			if self.Game.GUI: self.Game.GUI.shuffleintoDeckAni(obj, enemyCanSee)
			numpyShuffle(self.decks[ID])
			if sendSig: self.Game.sendSignal("CardShuffled", initiatorID, None, obj, 0, "")
			self.Game.sendSignal("DeckCheck", ID, None, None, 0, "")
	
	def burialRite(self, ID, minions, noSignal=False):
		if not isinstance(minions, list):
			minions = [minions]
		for minion in minions:
			self.Game.summonfrom(minion, ID, -1, None, source='H')
			minion.loseAbilityInhand()
		for minion in minions:
			self.Game.killMinion(minion, minion)
		self.Game.gathertheDead()
		if not noSignal:
			for minion in minions:
				self.Game.Counters.numBurialRiteThisGame[ID] += 1
				self.Game.sendSignal("BurialRite", ID, None, minion, 0, "")

	#card can be a list(for discarding multiple cards), or can be a single int or card keeper
	def discard(self, ID, card, getAll=False):
		if getAll or isinstance(card, (list, tuple, numpy.ndarray)):
			if self.hands[ID]:
				if getAll: cards = self.extractfromHand(None, ID=ID, getAll=True, enemyCanSee=True, linger=False)[0]
				else: cards = [self.extractfromHand(i, ID=ID, enemyCanSee=True, linger=False)[0] for i in card]
				for card in cards:
					self.Game.sendSignal("CardDiscarded", card.ID, None, card, 1, "")
					card.whenDiscarded()
					self.Game.Counters.cardsDiscardedThisGame[ID].append(type(card))
					self.Game.Counters.cardsDiscardedThisTurn[ID].append(type(card))
					self.Game.Counters.shadows[card.ID] += 1
					self.Game.sendSignal("CardLeavesHand", card.ID, None, card, 0, "")
				self.Game.sendSignal("HandDiscarded", ID, None, None, len(cards), "")
				self.Game.Manas.calcMana_All()
			return None
		else:  # Discard a chosen card.
			i = card if isinstance(card, (int, numpy.int32, numpy.int64)) else self.hands[ID].index(card)
			card = self.hands[ID].pop(i)
			card.leavesHand()
			if self.Game.GUI: self.Game.GUI.cardsLeaveHandAni([card], ID=ID, enemyCanSee=True, linger=False)
			self.Game.sendSignal("CardDiscarded", card.ID, None, card, 1, "")
			card.whenDiscarded()
			self.Game.Counters.cardsDiscardedThisGame[ID].append(type(card))
			self.Game.Counters.cardsDiscardedThisTurn[ID].append(type(card))
			self.Game.Counters.shadows[card.ID] += 1
			self.Game.sendSignal("CardLeavesHand", card.ID, None, card, 0, "")
			self.Game.Manas.calcMana_All()
			return card
			
	# 只能全部拿出手牌中的所有牌或者拿出一个张，不能一次拿出多张指定的牌
	#丢弃手牌要用discardAll
	def extractfromHand(self, card, ID=0, getAll=False, enemyCanSee=False, linger=False, animate=True):
		if getAll:  # Extract the entire hand.
			cardsOut = self.hands[ID][:]
			if cardsOut:
				#一般全部取出手牌的时候都是直接洗入牌库，一般都不可见
				if animate and self.Game.GUI:
					self.Game.GUI.cardsLeaveHandAni(cardsOut, ID=ID, enemyCanSee=True, linger=linger)
				self.hands[ID] = []
				for card in cardsOut:
					card.leavesHand()
					self.Game.sendSignal("CardLeavesHand", card.ID, None, card, 0, '')
			return cardsOut, 0, -2  # -2 means the posinHand doesn't have real meaning.
		else:
			if not isinstance(card, (int, numpy.int32, numpy.int64)):
				# Need to keep track of the card's location in hand.
				index, cost = self.hands[card.ID].index(card), card.getMana()
				posinHand = index if index < len(self.hands[card.ID]) - 1 else -1
				card = self.hands[card.ID].pop(index)
			else:  # card is a number
				posinHand = card if card < len(self.hands[ID]) - 1 else -1
				card = self.hands[ID].pop(card)
				cost = card.getMana()
			card.leavesHand()
			if animate and self.Game.GUI:
				self.Game.GUI.cardsLeaveHandAni([card], card.ID, enemyCanSee, linger=linger)
			self.Game.sendSignal("CardLeavesHand", card.ID, None, card, 0, '')
			return card, cost, posinHand

	# 只能全部拿牌库中的所有牌或者拿出一个张，不能一次拿出多张指定的牌
	def extractfromDeck(self, card, ID=0, getAll=False, enemyCanSee=True, linger=False, animate=True):
		if getAll:  # For replacing the entire deck or throwing it away.
			cardsOut = self.decks[ID]
			self.decks[ID] = []
			for card in cardsOut: card.leavesDeck()
			#self.cards_1Possi, self.cards_XPossi = [], []
			self.Game.sendSignal("DeckCheck", ID, None, None, 0, "")
			return cardsOut, 0, False
		else:
			if not isinstance(card, (int, numpy.int32, numpy.int64)):
				removefrom(card, self.decks[card.ID])
			else:
				if not self.decks[ID]: return None, 0, False
				card = self.decks[ID].pop(card)
			card.leavesDeck()
			if animate and self.Game.GUI: self.Game.GUI.milledfromDeckAni(card, enemyCanSee=enemyCanSee, linger=linger)
			self.Game.sendSignal("DeckCheck", ID, None, None, 0, "")
			return card, 0, False
			
	#所有被移除的卡牌都会被展示
	def removeDeckTopCard(self, ID, num=1):
		cards = []
		for i in range(num):
			card = self.extractfromDeck(-1, ID)[0] #The cards removed from deck top can always be seen by opponent
			if card: cards.append(card)
		return cards
		
	def createCopy(self, game):
		if self not in game.copiedObjs:
			Copy = type(self)(game)
			game.copiedObjs[self] = Copy
			Copy.initialDecks = self.initialDecks
			Copy.hands, Copy.decks = {1: [], 2: []}, {1: [], 2: []}
			Copy.noCards, Copy.handUpperLimit = copy.deepcopy(self.noCards), copy.deepcopy(self.handUpperLimit)
			Copy.decks = {1: [card.createCopy(game) for card in self.decks[1]],
						  2: [card.createCopy(game) for card in self.decks[2]]}
			Copy.hands = {1: [card.createCopy(game) for card in self.hands[1]],
						  2: [card.createCopy(game) for card in self.hands[2]]}
			return Copy
		else: return game.copiedObjs[self]

from DB_CardPools import *

Default1 = []

Default2 = []

[EnchantedRaven, PoweroftheWild, WildGrowth, NordrassilDruid, SouloftheForest,
			DruidoftheClaw, ForceofNature, MenagerieWarden, Nourish, ArchsporeMsshifn,
			ImprisonedSatyr, Germination, YsielWindsinger,
			RunicCarvings, AdorableInfestation, ShandoWildclaw,
			KiriChosenofElune, CenarionWard,
			Guidance, LivingSeedRank1, MarkoftheSpikeshell,
			PridesFury, DeviateDreadfang, BestinShell, SheldrasMoontree, 			]


[ArcaneShot, Tracking, Webspinner, ExplosiveTrap, FreezingTrap, HeadhuntersHatchet, QuickShot, ScavengingHyena, SelectiveBreeder, SnakeTrap,
				Bearshark, DeadlyShot, DireFrenzy, SavannahHighmane, Helboar, ImprisonedFelmaw, PackTactics, ScavengersIngenuity, AugmentedPorcupine,
				ZixorApexPredator, MokNathalLion, ScrapShot, BeastmasterLeoroxx, NagrandSlam, TrueaimCrescent, BloodHerald, AdorableInfestation,
				CarrionStudies, Overwhelm, Wolpertinger, BloatedPython, ProfessorSlate, ShandoWildclaw, KroluskBarkstripper, MysteryWinner,
				DancingCobra, DontFeedtheAnimals, OpentheCages, PettingZoo, RinlingsRifle, TramplingRhino, MaximaBlastenheimer, DarkmoonTonk, JewelofNZoth, FelfireDeadeye,
				ResizingPouch, BolaShot, Saddlemaster, SunscaleRaptor, WoundPrey, KolkarPackRunner, ProspectorsCaravan, TameBeastRank1, PackKodo, TavishStormpike,
				PiercingShot, WarsongWrangler, BarakKodobane, Serpentbloom, SindoreiScentfinder, VenomstrikeBow, DevouringSwarm, LeatherworkingKit, AimedShot, RammingMount,
				StormwindPiper, RodentNest, ImportedTarantula, TheRatKing, RatsofExtraordinarySize, 			]

[BabblingBook, ShootingStar, SnapFreeze, Arcanologist, FallenHero, ArcaneIntellect, ConeofCold, Counterspell, IceBarrier, MirrorEntity,
				Fireball, WaterElemental_Core, AegwynntheGuardian, EtherealConjurer, ColdarraDrake, Flamestrike, Evocation, FontofPower, ApexisSmuggler, AstromancerSolarian,
				IncantersFlow, Starscryer, ImprisonedObserver, NetherwindPortal, ApexisBlast, DeepFreeze, BrainFreeze, LabPartner, WandThief, CramSession,
				Combustion, Firebrand, PotionofIllusion, JandiceBarov, MozakiMasterDuelist, WyrmWeaver, DevolvingMissiles, PrimordialStudies, TrickTotem, RasFrostwhisper,
				ConfectionCyclone, DeckofLunacy, GameMaster, RiggedFaireGame, OccultConjurer, RingToss, FireworkElemental, SaygeSeerofDarkmoon, MaskofCThun, GrandFinale,
				GlacierRacer, ConjureManaBiscuit, KeywardenIvory, ImprisonedPhoenix, FlurryRank1, RunedOrb, Wildfire, ArcaneLuminary, OasisAlly, Rimetongue,
				RecklessApprentice, RefreshingSpringWater, VardenDawngrasp, MordreshFireEye, FrostweaveDungeoneer, ShatteringBlast, Floecaster, HotStreak, FirstFlame, CelestialInkSet,
				Ignite, PrestorsPyromancer, FireSale, SanctumChandler, ClumsyCourier, GrandMagusAntonidas, 			],