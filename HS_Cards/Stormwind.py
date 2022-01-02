from Parts.CardTypes import *
from Parts.TrigsAuras import *
from HS_Cards.AcrossPacks import TheCoin, Voidwalker, LightsJustice, SpiritWolf, DamagedGolem
from HS_Cards.Core import MindSpike, Fireball, Imp
from HS_Cards.Barrens import Spell_Sigil, PartyUp


class GameRuleAura_AuctioneerJaxon(GameRuleAura):
	def auraAppears(self): self.keeper.Game.rules[self.keeper.ID]["Trade Discovers Instead"] += 1
		
	def auraDisappears(self): self.keeper.Game.rules[self.keeper.ID]["Trade Discovers Instead"] -= 1
		
	
class Aura_BattlegroundBattlemaster(Aura_AlwaysOn):
	effGain, targets = "Windfury", "Neighbors"
	
	
class Aura_MrSmite(Aura_AlwaysOn):
	effGain, targets = "Charge", "All"
	def applicable(self, target): return "Pirate" in target.race
		
	
class Trig_SwordofaThousandTruth(TrigBoard):
	signals = ("HeroAttackedMinion", "HeroAttackedHero",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return subject is kpr.Game.heroes[kpr.ID] and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).Game.Manas.destroyManaCrystal(10, 3-kpr.ID)
		
	
class Trig_Peasant(TrigBoard):
	signals = ("TurnStarts",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return ID == kpr.ID and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).Game.Hand_Deck.drawCard(kpr.ID)
		
	
class Trig_Florist(TrigBoard):
	signals = ("TurnEnds",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		if spells := self.keeper.findCards2ReduceMana(lambda card: card.school == "Nature"):
			ManaMod(numpyChoice(spells), by=-1).applies()
		
	
class Trig_StockadesPrisoner(Trig_Countdown):
	signals, counter = ("CardBeenPlayed",), 2
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID  #会在我方回合开始时进行苏醒
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		if self.counter < 1: self.keeper.awaken()
		
	
class Trig_EnthusiasticBanker(TrigBoard):
	signals = ("TurnEnds",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		game, ID = (kpr := self.keeper).Game, kpr.ID
		if deckSize := len(game.Hand_Deck.decks[ID]):
			card = game.Hand_Deck.extractfromDeck(numpyRandint(deckSize), ID)
			for trig in self.keeper.deathrattles:
				if isinstance(trig, Death_EnthusiasticBanker): trig.memory.append(card)
		
	
class Trig_TwoFacedInvestor(TrigBoard):
	signals = ("TurnEnds",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		if (by := 2*numpyRandint(2)-1) < 0:
			if cards := self.keeper.findCards2ReduceMana(): ManaMod(numpyChoice(cards), by=by).applies()
		elif cards := kpr.Game.Hand_Deck.hands[kpr.ID]: ManaMod(numpyChoice(cards), by=by).applies()
		
	
class Trig_FlightmasterDungar_Westfall(Trig_Countdown):
	signals, counter = ("TurnStarts",), 1
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID  #会在我方回合开始时进行苏醒
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		if self.counter < 1:
			self.keeper.awaken()
			kpr.summon(numpyChoice(PartyUp.adventurers)(kpr.Game, kpr.ID))
		
	
class Trig_FlightmasterDungar_Ironforge(Trig_Countdown):
	signals, counter = ("TurnStarts",), 3
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID  #会在我方回合开始时进行苏醒
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		if self.counter < 1:
			self.keeper.awaken()
			kpr.heals(kpr.Game.heroes[kpr.ID], kpr.calcHeal(10))
		
	
class Trig_FlightmasterDungar_EasternPlaguelands(Trig_Countdown):
	signals, counter = ("TurnStarts",), 5
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID  #会在我方回合开始时进行苏醒
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		if self.counter < 1:
			self.keeper.awaken()
			side, game = 3 - kpr.ID, kpr.Game
			for _ in range(12):
				if objs := game.charsAlive(side): self.keeper.dealsDamage(numpyChoice(objs), 1)
				else: break
		
	
class Trig_Cheesemonger(TrigBoard):
	signals = ("CardPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return comment == "Spell" and ID != kpr.ID and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		if spells := self.rngPool("%d-Cost Spells"%num[0]):
			kpr.addCardtoHand(numpyChoice(spells), kpr.ID)
		
	
class Trig_CorneliusRoame(TrigBoard):
	signals = ("TurnStarts", "TurnEnds",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return self.keeper.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).Game.Hand_Deck.drawCard(kpr.ID)
		
	
class Trig_GoldshireGnoll(TrigHand):
	signals = ("HandCheck",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.inHand and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).Game.ManaHandler.calcMana_Single(kpr)
		
	
class Trig_FinalShowdown(Trig_Quest):
	signals = ("DrawingStops", "NewTurnStarts",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return signal[0] == 'N' or ID == self.keeper.ID
		
	def handleCounter(self, signal, ID, subject, target, num, comment, choice):
		if signal[0] == 'N': self.counter = 0
		else:
			self.memory += target
			self.counter += len(target)
		
	
class Trig_LionsFrenzy(Trig_SelfAura):
	signals = ("NewTurnStarts", "CardDrawn")
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and (signal == "NewTurnStarts" or ID == kpr.ID)
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.calcStat()
		
	
class Trig_IreboundBrute(TrigHand):
	signals = ("CardDrawn",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.inHand and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).Game.Manas.calcMana_Single(kpr)
		
	
class Trig_LostinthePark(Trig_Quest):
	signals = ("HeroAttGained",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return ID == self.keeper.ID
		
	def handleCounter(self, signal, ID, subject, target, num, comment, choice):
		self.counter += num
		
	
class Trig_Wickerclaw(TrigBoard):
	signals = ("HeroAttGained",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).giveEnchant(kpr, statEnchant=Enchantment_Exclusive(Wickerclaw, 2, 0))
		
	
class Trig_OracleofElune(TrigBoard):
	signals = ("CardBeenPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		#Assume can only copy a minion while it is still alive onBoard
		return kpr.Game.cardinPlay.category == "Minion" and kpr.onBoard and ID == kpr.ID and num[0] < 3 and kpr.aliveonBoard()
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).summon(kpr.copyCard(kpr.Game.cardinPlay, kpr.ID))
		
	
class Trig_ParkPanther(TrigBoard):
	signals = ("MinionAttackingMinion", "MinionAttackingHero",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and subject is kpr
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).giveHeroAttackArmor(kpr.ID, attGain=3, source=ParkPanther)
		
	
class Trig_DefendtheDwarvenDistrict(Trig_Quest):
	signals = ("MinionTookDmg", "HeroTookDmg",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return subject and subject.ID == self.keeper.ID and subject.category == "Spell" and subject not in self.memory
		
	def handleCounter(self, signal, ID, subject, target, num, comment, choice):
		self.memory.append(subject)
		self.counter += 1
		
	def assistCreateCopy(self, Copy):
		Copy.memory = [spell.createCopy(Copy.Game) for spell in self.memory]
		
	
class Trig_LeatherworkingKit(Trig_Countdown):
	signals, counter = ("ObjDied",), 3
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return "Beast" in target.race and target.ID == kpr.ID and kpr.onBoard and kpr.health > 0
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		if self.counter < 1:
			self.resetCount()
			beast, mana, entersHand = self.keeper.drawCertainCard(lambda card: "Beast" in card.race)
			if entersHand: self.keeper.giveEnchant(beast, 1, 1, source=LeatherworkingKit, add2EventinGUI=False)
			self.keeper.losesDurability() #Assuming weapon always loses Durability
		
	
class Trig_TavishsRam(TrigBoard):
	signals, description = ("BattleStarted", "BattleFinished",), "Immune while attacking"
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return subject is kpr and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		if signal == "BattleStarted": subject.getsEffect("Immune")
		else: subject.losesEffect("Immune")
		
	
class Trig_StormwindPiper(TrigBoard):
	signals = ("MinionAttackedMinion", "MinionAttackedHero",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return subject is kpr and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).giveEnchant(kpr.Game.minionsonBoard(kpr.ID, race="Beast"), statEnchant=Enchantment(StormwindPiper, 1, 1))
		
	
class Trig_DormantRatKing(Trig_Countdown):
	signals, counter = ("ObjDied",), 5
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return target.category == "Minion" and kpr.onBoard and target.ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		if self.counter < 1:
			self.keeper.losesTrig(self, "TrigBoard")
			self.keeper.awaken()
		
	
class Trig_SorcerersGambit(Trig_Quest):
	signals = ("CardBeenPlayed",)
	def __init__(self, keeper):
		super().__init__(keeper)
		self.memory = ["Fire", "Frost", "Arcane"]
		
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return ID == kpr.ID and kpr.Game.cardinPlay.school in self.memory
		
	def handleCounter(self, signal, ID, subject, target, num, comment, choice):
		self.memory.remove(subject.school)
		self.counter += 1
		
	
class Trig_CelestialInkSet(Trig_Countdown):
	signals, counter = ("CardBeenPlayed",), 5
	def increment(self, signal, ID, subject, target, num, comment, choice):
		return num[0]
		
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return num[0] > 0 and ID == kpr.ID and kpr.onBoard and kpr.health > 0
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		if self.counter < 1:
			self.resetCount()
			if cards := self.keeper.findCards2ReduceMana(lambda card: card.category == "Spell"):
				ManaMod(numpyChoice(cards), by=-5).applies()
			self.keeper.losesDurability()
		
	
class Trig_SanctumChandler(TrigBoard):
	signals = ("CardBeenPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return ID == kpr.ID and kpr.onBoard and kpr.Game.cardinPlay.school == "Fire"
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.drawCertainCard(lambda card: card.category == "Spell")
		
	
class Trig_PrismaticJewelKit(TrigBoard):
	signals = ("CharLoses_Divine Shield",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return ID == kpr.ID and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		kpr.giveEnchant([card for card in kpr.Game.Hand_Deck.hands[kpr.ID] if card.category == "Minion"],
						statEnchant=Enchantment(PrismaticJewelKit, 1, 1), add2EventinGUI=False)
		self.keeper.losesDurability()
		
	
class Trig_RisetotheOccasion(Trig_Quest):
	signals = ("CardBeenPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return ID == kpr.ID and num[0] == 1 and type(kpr) not in self.memory
		
	def handleCounter(self, signal, ID, subject, target, num, comment, choice):
		self.memory.append(type(subject))
		self.counter += 1
		
	
class Trig_HighlordFordragon(TrigBoard):
	signals = ("CharLoses_Divine Shield",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return ID == self.keeper.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		if minions := [card for card in kpr.Game.Hand_Deck.hands[kpr.ID] if card.category == "Minion"]:
			self.keeper.giveEnchant(numpyChoice(minions), 5, 5, source=HighlordFordragon, add2EventinGUI=False)
		
	
class Trig_SeekGuidance(Trig_Quest):
	signals = ("CardBeenPlayed",)
	def __init__(self, keeper):
		super().__init__(keeper)
		self.memory = [2, 3, 4]
		
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return ID == self.keeper.ID and num[0] in self.memory
		
	def handleCounter(self, signal, ID, subject, target, num, comment, choice):
		self.memory.remove(num[0])
		self.counter += 1
		
	
class Trig_DiscovertheVoidShard(Trig_SeekGuidance):
	def __init__(self, keeper):
		super().__init__(keeper)
		self.memory = [5, 6]
		
	
class Trig_IlluminatetheVoid(Trig_SeekGuidance):
	def __init__(self, keeper):
		super().__init__(keeper)
		self.memory = [7, 8]
		
	
class Trig_VoidtouchedAttendant(TrigBoard):
	signals = ("FinalDmgonHero?",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return self.keeper.onBoard and target.category == "Hero"
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		num[0] += 1
		
	
class Trig_ShadowclothNeedle(TrigBoard):
	signals = ("CardBeenPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return ID == kpr.ID and kpr.health > 0 and kpr.onBoard and kpr.Game.cardinPlay.school == "Shadow"
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		kpr.dealsDamage(kpr.Game.charsonBoard(3-kpr.ID), 1)
		self.keeper.losesDurability()
		
	
class Trig_Psyfiend(TrigBoard):
	signals = ("CardBeenPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID and kpr.Game.cardinPlay.school == "Shadow"
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).dealsDamage(list(kpr.Game.heroes.values()), [2, 2])
		
	
class Trig_UndercoverMole(TrigBoard):
	signals = ("MinionAttackedMinion", "MinionAttackedHero",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return subject is kpr and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).addCardtoHand(numpyChoice(self.rngPool(kpr.Game.heroes[3-kpr.ID].Class+" Cards"), kpr.ID))
		
	
class Trig_FindtheImposter(Trig_Quest):
	signals = ("CardBeenPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return ID == kpr.ID and "SI:7" in kpr.Game.cardinPlay.name
		
	
class Trig_SI7Operative(TrigBoard):
	signals = ("MinionAttackedMinion",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return subject is kpr and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).giveEnchant(kpr, effectEnchant=Enchantment_Exclusive(SI7Operative, effGain="Stealth"))
		
	
class Trig_SI7Assassin(TrigHand):
	signals = ("CardBeenPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.inHand and ID == kpr.ID and kpr.Game.cardinPlay.name.startswith("SI:7")
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).Game.Manas.calcMana_Single(kpr)
		
	
class Trig_CommandtheElements(Trig_Quest):
	signals = ("CardBeenPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return ID == kpr.ID and kpr.overload > 0
		
	
class Trig_BolnerHammerbeak(TrigBoard):
	signals = ("CardBeenPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		#打出的第一个战吼随从也可以享受这个重复。重复时的战吼发出者为这个随从。战吼目标随机
		return comment == "Minion" and ID == kpr.ID and "~Battlecry" in kpr.Game.cardinPlay.index and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		plays = kpr.Game.Counters.cardPlays[kpr.ID][kpr.Game.turnInd]
		if card := next((tup[0] for tup in plays if tup[0].category == "Minion" and "~Battlecry" in tup[0].index), None):
			self.keeper.invokeBattlecry(card)
		
	
class Trig_AuctionhouseGavel(TrigBoard):
	signals = ("HeroAttackedMinion", "HeroAttackedHero",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return subject is kpr.Game.heroes[kpr.ID] and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		if cards := self.keeper.findCards2ReduceMana(lambda card: card.category == "Minion" and "~Battlecry" in card.index):
			ManaMod(numpyChoice(cards), by=-1).applies()
		
	
class Trig_SpiritAlpha(TrigBoard):
	signals = ("CardBeenPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return ID == kpr.ID and kpr.onBoard and type(kpr.Game.cardinPlay).overload
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).summon(SpiritWolf(kpr.Game, kpr.ID))
		
	
class Trig_TheDemonSeed(Trig_Quest):
	signals = ("HeroTookDmg",)
	def handleCounter(self, signal, ID, subject, target, num, comment, choice):
		self.counter += num
		
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return ID == self.keeper.ID == subject.Game.turn
		
	
class Trig_BloodboundImp(TrigBoard):
	signals = ("MinionAttackingMinion", "MinionAttackingHero",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return subject is kpr and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).dealsDamage(kpr.Game.heroes[kpr.ID], 2)
		
	
class Trig_RunedMithrilRod(Trig_Countdown):
	signals, counter = ("DrawingStops",), 4
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return ID == kpr.ID and kpr.onBoard and len(target) > 0
		
	def increment(self, signal, ID, subject, target, num, comment, choice):
		return len(target)
		
	def trig(self, signal, ID, subject, target, num, comment, choice):
		# 在计数时，如果有抽数张牌的效果时，每抽一张牌之后进行一次扳机计数/减费效果。然后结算抽下一张牌
		# 在因为抽到时施放的法术而持续抽牌时，只有最终停止（最终抽到不施放的牌或疲劳）时才会让计数开始。因为此法使计数超过4时，则额外的计数会储存。
		# 如果因为抽到时施放的法术使计数积累得很高，则可以连续触发多次。
		if self.canTrig(signal, ID, subject, target, num, comment, choice):
			counter_0 = self.counter
			self.counter -= self.increment(signal, ID, subject, target, num, comment, choice)
			if (btn := self.keeper.btn) and self.counter != counter_0:
				btn.GUI.seqHolder[-1].append(btn.icons["Hourglass"].seqUpdateText())
			while self.counter < 1 and self.keeper.health > 0:
				self.counter += type(self).counter
				for card in self.keeper.Game.Hand_Deck.hands[self.keeper.ID]:
					ManaMod(card, by=-1).applies()
				self.keeper.losesDurability()
				if btn: btn.GUI.seqHolder[-1].append(btn.icons["Hourglass"].seqUpdateText())
		
	
class Trig_Anetheron(TrigHand):
	signals = ("HandCheck", "HandUpperLimitChange",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.inHand and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).Game.Manas.calcMana_Single(kpr)
		
	
class Trig_RaidtheDocks(Trig_Quest):
	signals = ("CardBeenPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return ID == kpr.ID and "Pirate" in kpr.Game.cardinPlay.race
		
	
class Trig_TheJuggernaut(TrigBoard):
	signals = ("TurnStarts",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		dormant = self.keeper
		dormant.summon(numpyChoice(self.rngPool("Pirates"))(dormant.Game, dormant.ID))
		dormant.equipWeapon(numpyChoice(self.rngPool("Warrior Weapons"))(dormant.Game, dormant.ID))
		for _ in range(2):
			if objs := dormant.Game.charsAlive(3-dormant.ID): dormant.dealsDamage(numpyChoice(objs), 2)
			else: break
		
	
class Trig_CargoGuard(TrigBoard):
	signals = ("TurnEnds",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).giveHeroAttackArmor(kpr.ID, armor=3)
		
	
class Trig_RemoteControlledGolem(TrigBoard):
	signals = ("MinionTookDmg",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and target is kpr
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		game, ID = (kpr := self.keeper).Game, kpr.ID
		kpr.shuffleintoDeck([GolemParts(game, ID) for _ in (0, 1)])
		
	
class Trig_Lothar(TrigBoard):
	signals = ("TurnEnds",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return ID == kpr.ID and kpr.canBattle()
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		if minions := kpr.Game.minionsAlive(3 - kpr.ID):
			minion = numpyChoice(minions)
			kpr.Game.battle(kpr, minion)
			if minion.health < 1 or minion.dead: kpr.giveEnchant(kpr, 3, 3, source=Lothar)
		
	
class Trig_EdwinDefiasKingpin(TrigBoard):
	signals = ("NewTurnStarts", "CardBeenPlayed",)
	description = "Play the card drawn to gain +2/+2 and repeat this effect"
	def __init__(self, keeper, memory=None):
		super().__init__(keeper)
		self.memory = memory
		
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and (signal[0] == "N" or (ID == kpr.ID and kpr.Game.cardinPlay is self.memory))
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		if signal.startswith("New"): kpr.losesTrig(self)
		else:
			card, mana, entersHand = kpr.Game.Hand_Deck.drawCard(kpr.ID)
			if entersHand and card.inHand and kpr.onBoard:
				self.memory = card
				kpr.giveEnchant(kpr, statEnchant=Enchantment_Exclusive(EdwinDefiasKingpin, 2, 2))
			
	
class Trig_Suckerhook(TrigBoard):
	signals = ("TurnEnds",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return ID == kpr.ID and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		keeper = self.keeper
		if weapon := keeper.Game.availableWeapon(keeper.ID):
			keeper.transform(weapon, keeper.newEvolved(weapon.mana_0, by=1, ID=keeper.ID, s="Weapons"))
		
	
class Trig_DefiasCannoneer(TrigBoard):
	signals = ("HeroAttackedMinion", "HeroAttackedHero",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return ID == kpr.ID and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		if objs := kpr.Game.charsAlive(3-kpr.ID):
			self.keeper.dealsDamage(numpyChoice(objs), 2)
			if objs := kpr.Game.charsAlive(3 - kpr.ID):
				self.keeper.dealsDamage(numpyChoice(objs), 2)
		
	
class Death_ElwynnBoar(Deathrattle):
	description = "Deathrattle: If you had 7 Elwynn Boars die this game, equip a 15/3 Sword of a Thousand Truth"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		if (kpr := self.keeper).Game.Counters.examDeads(kpr.ID, veri_sum_ls=1, cond=lambda card: card is ElwynnBoar) > 6:
			kpr.equipWeapon(SwordofaThousandTruth(kpr.Game, kpr.ID))
		
	
class Death_MailboxDancer(Deathrattle):
	description = "Deathrattle: Add a Coin to your opponent's hand"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.addCardtoHand(TheCoin, 3 - self.keeper.ID)
		
	
class Death_EnthusiasticBanker(Deathrattle):
	description = "Deathrattle: Add the stored cards to your hand"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		if self.memory: self.keeper.addCardtoHand(self.memory, self.keeper.ID)
		
	def selfCopy(self, recipient):
		trig = type(self)(recipient)
		trig.memory = [recipient.copyCard(card, recipient.ID) for card in self.memory]
		return trig
		
	def assistCreateCopy(self, Copy):
		Copy.memory = [card.createCopy(Copy.Game) for card in self.memory]
		
	
class Death_StubbornSuspect(Deathrattle):
	description = "Deathrattle: Summon a random 3-Cost minion"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).summon(numpyChoice(self.rngPool("3-Cost Minions to Summon"))(kpr.Game, kpr.ID))
		
	
class Death_MoargForgefiend(Deathrattle):
	description = "Deathrattle: Gain 8 Armor"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.giveHeroAttackArmor(self.keeper.ID, armor=8)
		
	
class Death_PersistentPeddler(Deathrattle):
	description = "Deathrattle: Summon a Persistent Peddler from your deck"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.try_SummonfromOwn(cond=lambda card: card.name == "Persistent Peddler")
		
	
class Death_VibrantSquirrel(Deathrattle):
	description = "Deathrattle: Shuffle 4 Acorns into your deck"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		game, ID = (kpr := self.keeper).Game, kpr.ID
		kpr.shuffleintoDeck([Acorn(game, ID) for _ in (0, 1, 2, 3)])
		
	
class Death_Composting(Deathrattle):
	description = "Deathrattle: Draw a card"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.Game.Hand_Deck.drawCard(self.keeper.ID)
		
	
class Death_KodoMount(Deathrattle):
	description = "Deathrattle: Summon a 4/2 Kodo"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).summon(GuffsKodo(kpr.Game, kpr.ID))
		
	
class Death_RammingMount(Deathrattle):
	description = "Deathrattle: Summon a 2/2 Ram"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).summon(TavishsRam(kpr.Game, kpr.ID))
		
	
class Death_RodentNest(Deathrattle):
	description = "Deathrattle: Summon five 1/1 Rats"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		game, ID = (kpr := self.keeper).Game, kpr.ID
		kpr.summon([Rat(game, ID) for _ in range(5)])
		
	
class Death_ImportedTarantula(Deathrattle):
	description = "Deathrattle: Summon two 1/1 Spiders with Poisonous and Rush"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		game, ID = (kpr := self.keeper).Game, kpr.ID
		kpr.summon([InvasiveSpiderling(game, ID) for _ in (0, 1)], relative="<>")
		
	
class Death_TheRatKing(Deathrattle):
	description, forceLeave = "Deathrattle: Go dormant. Revive after 5 friendly minions die", True
	def effect(self, signal, ID, subject, target, num, comment, choice):
		game, ID = self.keeper.Game, self.keeper.ID
		if self.keeper.category == "Minion" and self.keeper in game.minions[ID]:
			if self.keeper.onBoard: self.keeper.goDormant(Trig_DormantRatKing(self.keeper))
			elif game.space(ID) > 0:
				dormant = TheRatKing(game, ID)
				dormant.category = "Dormant"
				dormant.trigsBoard.append(Trig_DormantRatKing(dormant))
				game.summonSingle(dormant)
		
	
class Death_NobleMount(Deathrattle):
	description = "Deathrattle: Summon a 1/1 Warhorse"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).summon(CarielsWarhorse(kpr.Game, kpr.ID))
		
	
class Death_ElekkMount(Deathrattle):
	description = "Deathrattle: Summon a 4/7 Elekk"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).summon(XyrellasElekk(kpr.Game, kpr.ID))
		
	
class Death_HiddenGyroblade(Deathrattle):
	description = "Deathrattle: Throw this at a random enemy minion"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		if (kpr := self.keeper).attack > 0 and (minions := kpr.Game.minionsAlive(3 - kpr.ID)):
			kpr.dealsDamage(numpyChoice(minions), kpr.attack)
		
	
class Death_LoanShark(Deathrattle):
	description = "Deathrattle: Add two Coins to your hand"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.addCardtoHand([TheCoin, TheCoin], self.keeper.ID)
		
	
class Death_TamsinsDreadsteed(Deathrattle):
	description = "Deathrattle: At the end of the turn, summon Tamsin's Dreadsteed"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		TamsinsDreadsteed_Effect(self.keeper.Game, self.keeper.ID).connect()
		
	
class Death_CowardlyGrunt(Deathrattle):
	description = "Deathrattle: Summon a minion from your deck"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.try_SummonfromOwn()
		
	
class Death_CookietheCook(Deathrattle):
	description = "Deathrattle: Equip a 2/3 Stirring Rod with Lifesteal"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).equipWeapon(CookiesStirringRod(kpr.Game, kpr.ID))
		
	
class Death_Hullbreaker(Deathrattle):
	description = "Deathrattle: Draw a spell. Your hero takes damage equal to its Cost"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		if (mana := (kpr := self.keeper).drawCertainCard(lambda card: card.category == "Spell")[1]) > 0:
			kpr.Game.heroTakesDamage(kpr.ID, mana)
		
	
class SigilofAlacrity_Effect(TrigEffect):
	trigType = "TurnStart&OnlyKeepOne"
	def trigEffect(self):
		card, mana, entersHand = self.Game.Hand_Deck.drawCard(self.ID)
		if entersHand: ManaMod(card, by=-1).applies()
		
	
class DemonslayerKurtrus_Effect(TrigEffect):
	signals, counter, trigType = ("HandCheck",), 2, "Conn&TrigAura"
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return comment == "Enter_Draw" and ID == self.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		ManaMod(target, by=-self.counter).applies()
		
	
class SheldrasMoontree_Effect(TrigEffect):
	signals, counter, trigType = ("CardDrawn",), 3, "Conn&TrigAura&OnlyKeepOne"
	def connect(self):
		trigs = getListinDict(self.Game.trigsBoard[self.ID], "CardDrawn")
		trig = next((trig for trig in trigs if isinstance(trig, SheldrasMoontree_Effect)), None)
		if trig:
			trig.counter = 3
			if trig.card.btn: trig.card.btn.trigAni(trig.counter)
		else:
			trigs.append(self)
			self.Game.trigAuras[self.ID].append(self)
			if self.Game.GUI: self.Game.GUI.heroZones[self.ID].addaTrig(self.card, text='3')
		
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return target[0].ID == self.ID
		
	def trig(self, signal, ID, subject, target, num, comment, choice):
		if self.canTrig(signal, ID, subject, target, num, comment, choice):
			if self.Game.GUI: self.Game.GUI.showOffBoardTrig(self.card)
			self.effect(signal, ID, subject, target, num, comment, choice)
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.counter -= 1
		if self.card.btn: self.card.btn.trigAni(self.counter)
		target[0].index += "Casts When Drawn"
		if self.counter < 1: self.disconnect()
		
	
class TavishMasterMarksman_Effect(TrigEffect):
	signals, trigType = ("CardBeenPlayed",), "Conn&TrigAura&OnlyKeepOne"
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return comment == "Spell" and ID == self.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.Game.powers[self.ID].usageCount = 0
		self.Game.powers[self.ID].btn.checkHpr()
		
	
class AimedShot_Effect(TrigEffect):
	signals, counter, trigType = ("HeroUsedAbility",), 2, "Conn&TrigAura&OnlyKeepOne"
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return ID == self.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.Game.powers[self.ID].losesEffect("Power Damage", amount=self.counter)
		self.disconnect()
		
	
class GameManaAura_HotStreak(GameManaAura_OneTime):
	by = -2
	def applicable(self, target): return target.ID == self.ID and target.school == "Fire"
		
	
class PrestorsPyromancer_Effect(TrigEffect):
	signals, counter, trigType = ("SpellBeenCast",), 2, "Conn&TrigAura&OnlyKeepOne"
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return ID == self.ID and subject.school == "Fire"
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.Game.heroes[self.ID].losesEffect("Fire Spell Damage", amount=self.counter)
		self.disconnect()
		
	
class ArcanistDawngrasp_Effect(TrigEffect):
	counter, trigType = 3, "OnlyKeepOne" #For this effect, it is simply an indicator, no need for "Conn&TrigAura"
	
	
class GameAura_LightbornCariel(GameAura_AlwaysOn):
	attGain, healthGame, counter = 2, 2, 2
	def applicable(self, target): return target.name == "Silver Hand Recruit"
		
	def upgrade(self):
		self.attGain = self.healthGain = self.counter = self.counter + 2
		for receiver in self.receivers:
			receiver.attGain, receiver.healthGain = self.attGain, self.healthGain
			receiver.recipient.calcStat()
		if self.counter and self.card.btn: self.card.btn.trigAni(self.counter)
		
	
class SI7Skulker_Effect(TrigEffect):
	signals, counter, trigType = ("HandCheck",), 1, "Conn"
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return comment == "Enter_Draw" and ID == self.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		ManaMod(target, by=-self.counter).applies()
		self.disconnect()
		
	
class StormcallerBrukan_Effect(TrigEffect):
	trigType = "OnlyKeepOne" #For this effect, it is simply an indicator, no need for "Conn&TrigAura"
	
	
class BlightbornTamsin_Effect(TrigEffect):
	signals, trigType = ("DmgTaker?",), "Conn&TrigAura&OnlyKeepOne"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.on = True
		
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		#target is a list that holds the target object. It can be modified by triggers
		if comment == "Reset":  # Assume this can't trigger multiple times in a chain
			self.on = True
			return False
		else: return target[0] == self.Game.heroes[self.ID] and target[0].onBoard and self.Game.turn == self.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		target[0] = self.Game.heroes[3 - self.ID]
		self.on = False
		
	def assistCreateCopy(self, Copy):
		Copy.on = self.on
		
	
class TamsinsDreadsteed_Effect(TrigEffect):
	counter, trigType = 1, "TurnEnd&OnlyKeepOne"
	def trigEffect(self):
		self.card.summon([TamsinsDreadsteed(self.Game, self.ID) for _ in range(self.counter)])
		
	
class MoonlitGuidance_Effect(TrigEffect):
	signals, trigType = ("CardBeenPlayed",), "Conn&TurnEnd"
	def __init__(self, Game, ID, memory=()):
		super().__init__(Game, ID)
		self.memory = memory  #tuple (Original card, copy)
		
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return self.memory and subject is self.memory[1]
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		if (card := self.memory[0]) in (deck := self.Game.Hand_Deck.decks[self.ID]):
			if card in deck: self.Game.Hand_Deck.drawCard(self.ID, deck.index(card))
		self.disconnect()
		
	def assistCreateCopy(self, Copy):
		Copy.memory = tuple(card.createCopy(Copy.Game) for card in self.memory)
		
	
class Copycat_Effect(TrigEffect):
	signals, trigType = ("CardBeenPlayed",), "Conn&TrigAura"
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return ID != self.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.card.addCardtoHand(type(self.Game.cardinPlay), self.ID)
		self.disconnect()
		
	
class ElwynnBoar(Minion):
	Class, race, name = "Neutral", "Beast", "Elwynn Boar"
	mana, attack, health = 1, 1, 1
	numTargets, Effects, description = 0, "", "Deathrattle: If you had 7 Elwynn Boars die this game, equip a 15/3 Sword of Thousand Truth"
	name_CN = "埃尔文野猪"
	deathrattle = Death_ElwynnBoar
	def text(self): return self.Game.Counters.examDeads(self.ID, veri_sum_ls=1, cond=lambda card: card is ElwynnBoar)
		
	
class SwordofaThousandTruth(Weapon):
	Class, name, description = "Neutral", "Sword of a Thousand Truths", "After your hero attacks, destroy your opponent's Mana Crystals"
	mana, attack, durability, Effects = 10, 15, 3, ""
	name_CN = "万千箴言之剑"
	index = "Legendary~Uncollectible"
	trigBoard = Trig_SwordofaThousandTruth
	
	
class Peasant(Minion):
	Class, race, name = "Neutral", "", "Peasant"
	mana, attack, health = 1, 2, 1
	numTargets, Effects, description = 0, "", "At the start of your turn, draw a card"
	name_CN = "农夫"
	trigBoard = Trig_Peasant
	
	
class StockadesGuard(Minion):
	Class, race, name = "Neutral", "", "Stockades Guard"
	mana, attack, health = 1, 1, 3
	name_CN = "监狱守卫"
	numTargets, Effects, description = 1, "", "Battlecry: Give a friendly minion Taunt"
	index = "Battlecry"
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists(self.ID, choice)
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.ID == self.ID and obj is not self and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(target, effGain="Taunt", source=StockadesGuard)
		
	
class AuctioneerJaxon(Minion):
	Class, race, name = "Neutral", "", "Auctioneer Jaxon"
	mana, attack, health = 2, 2, 3
	name_CN = "拍卖师亚克森"
	numTargets, Effects, description = 0, "", "Whenever you Trade, Discover a card from your deck to draw instead"
	index = "Legendary"
	aura = GameRuleAura_AuctioneerJaxon
	
	
class DeeprunEngineer(Minion):
	Class, race, name = "Neutral", "", "Deeprun Engineer"
	mana, attack, health = 2, 1, 2
	name_CN = "矿道工程师"
	numTargets, Effects, description = 0, "", "Battlecry: Discover a Mech. It costs (1) less"
	index = "Battlecry"
	poolIdentifier = "Mechs as Druid"
	@classmethod
	def generatePool(cls, pools):
		return genPool_MinionsofRaceasClass(pools, "Mech")
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		card, _ = self.discoverNew(comment, lambda : self.rngPool("Mechs as " + class4Discover(self)))
		if card and card.inHand: ManaMod(card, by=-1).applies()
		
	
class EncumberedPackMule(Minion):
	Class, race, name = "Neutral", "Beast", "Encumbered Pack Mule"
	mana, attack, health = 2, 2, 3
	numTargets, Effects, description = 0, "Taunt", "Taunt. When you draw this, add a copy of it to your hand"
	name_CN = "劳累的驮骡"
	def whenDrawn(self):
		self.addCardtoHand(self.copyCard(self, self.ID), self.ID)
		
	
class Florist(Minion):
	Class, race, name = "Neutral", "", "Florist"
	mana, attack, health = 2, 2, 3
	numTargets, Effects, description = 0, "", "At the end of your turn, reduce the Cost of a Nature spell in your hand by (1)"
	name_CN = "卖花女郎"
	trigBoard = Trig_Florist
	
	
class PandarenImporter(Minion):
	Class, race, name = "Neutral", "", "Pandaren Importer"
	mana, attack, health = 2, 1, 3
	name_CN = "熊猫人进口商"
	numTargets, Effects, description = 0, "", "Battlecry: Discover a spell that didn't start in your deck"
	index = "Battlecry"
	def decideSpellPool(self):
		pool = self.rngPool(class4Discover(self)+" Spells")
		origDeck = self.Game.Hand_Deck.initialDecks[self.ID]
		return [card for card in pool if card not in origDeck]
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.discoverNew(comment, lambda : PandarenImporter.decideSpellPool(self))
		
	
class MailboxDancer(Minion):
	Class, race, name = "Neutral", "", "Mailbox Dancer"
	mana, attack, health = 2, 3, 2
	name_CN = "邮箱舞者"
	numTargets, Effects, description = 0, "", "Battlecry: Add a Coin to your hand. Deathrattle: Give your opponent one"
	index = "Battlecry"
	deathrattle = Death_MailboxDancer
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.addCardtoHand(TheCoin, self.ID)
		
	
class SI7Skulker(Minion):
	Class, race, name = "Neutral", "", "SI:7 Skulker"
	mana, attack, health = 2, 2, 2
	name_CN = "军情七处潜伏者"
	numTargets, Effects, description = 0, "Stealth", "Stealth. Battlecry: The next card you draw costs (1) less"
	index = "Battlecry"
	trigEffect = SI7Skulker_Effect
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		#假设只有最终进入手牌的卡会享受减费
		SI7Skulker_Effect(self.Game, self.ID).connect()
		
	
class StockadesPrisoner(Minion):
	Class, race, name = "Neutral", "", "Stockades Prisoner"
	mana, attack, health = 2, 5, 4
	numTargets, Effects, description = 0, "", "Starts Dormant. After you play 3 cards, this awakens"
	name_CN = "监狱囚徒"
	def appears_fromPlay(self, choice):
		return super().appears(True, Trig_StockadesPrisoner(self))
		
	def appears(self, firstTime=True, dormantTrig=None):
		return super().appears(firstTime, Trig_StockadesPrisoner(self) if firstTime else None)
		
	
class EntrappedSorceress(Minion):
	Class, race, name = "Neutral", "", "Entrapped Sorceress"
	mana, attack, health = 3, 3, 4
	name_CN = "被困的女巫"
	numTargets, Effects, description = 0, "", "Battlecry: If you control a Quest, Discover a spell"
	index = "Battlecry"
	def effCanTrig(self):
		self.effectViable = self.Game.Secrets.mainQuests[self.ID]
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.Game.Secrets.mainQuests[self.ID] or self.Game.Secrets.sideQuests[self.ID]:
			self.discoverNew(comment, lambda : self.rngPool(class4Discover(self) + " Spells"))
		
	
class EnthusiasticBanker(Minion):
	Class, race, name = "Neutral", "", "Enthusiastic Banker"
	mana, attack, health = 3, 2, 3
	numTargets, Effects, description = 0, "", "At the end of your turn, store a card from your deck. Deathrattle: Add the stored cards to your hand"
	name_CN = "热情的柜员"
	trigBoard, deathrattle = Trig_EnthusiasticBanker, Death_EnthusiasticBanker
	
	
class ImpatientShopkeep(Minion):
	Class, race, name = "Neutral", "", "Impatient Shopkeep"
	mana, attack, health = 3, 3, 3
	numTargets, Effects, description = 0, "Rush", "Tradeable, Rush"
	name_CN = "不耐烦的店长"
	
	
class NorthshireFarmer(Minion):
	Class, race, name = "Neutral", "", "Northshire Farmer"
	mana, attack, health = 3, 3, 3
	name_CN = "北郡农民"
	numTargets, Effects, description = 1, "", "Battlecry: Choose a friendly Beast. Shuffle three 3/3 copies into your deck"
	index = "Battlecry"
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists(self.ID)
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard and obj.ID == self.ID and "Beast" in obj.race
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for obj in target:
			self.shuffleintoDeck([self.copyCard(obj, self.ID, 3, 3, bareCopy=True) for _ in (0, 1, 2)])
		
	
class PackageRunner(Minion):
	Class, race, name = "Neutral", "", "Package Runner"
	mana, attack, health = 3, 5, 6
	numTargets, Effects, description = 0, "Can't Attack", "Can only attack if you have at least 8 cards in hand"
	name_CN = "包裹速递员"
	def attackAllowedbyEffect(self):
		return self.effects["Can't Attack"] < 1 or \
			   (self.effects["Can't Attack"] == 1 and not self.silenced and len(self.Game.Hand_Deck.hands[self.ID]) > 7)
		
	
class RustrotViper(Minion):
	Class, race, name = "Neutral", "Beast", "Rustrot Viper"
	mana, attack, health = 3, 3, 4
	name_CN = "锈烂蝰蛇"
	numTargets, Effects, description = 0, "", "Tradeable. Battlecry: Destroy your opponent's weapon"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.Game.kill(self, self.Game.weapons[3 - self.ID])
		
	
class TravelingMerchant(Minion):
	Class, race, name = "Neutral", "", "Traveling Merchant"
	mana, attack, health = 3, 2, 3
	name_CN = "旅行商人"
	numTargets, Effects, description = 0, "", "Tradeable. Battlecry: Gain +1/+1 for each other friendly minion you control"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if not self.dead and (self.onBoard or self.inHand):
			num = len(self.Game.minionsonBoard(self.ID, exclude=self))
			if num: self.giveEnchant(self, num, num, source=TravelingMerchant)
		
	
class TwoFacedInvestor(Minion):
	Class, race, name = "Neutral", "", "Two-Faced Investor"
	mana, attack, health = 3, 2, 4
	numTargets, Effects, description = 0, "", "At the end of your turn, reduce the Cost of a card in your hand by (1). (50% chance to increase)"
	name_CN = "双面投资者"
	trigBoard = Trig_TwoFacedInvestor
	
	
class FlightmasterDungar(Minion):
	Class, race, name = "Neutral", "", "Flightmaster Dungar"
	mana, attack, health = 3, 3, 3
	name_CN = "飞行管理员杜加尔"
	numTargets, Effects, description = 0, "", "Battlecry: Choose a flightpath and go Dormant. Awaken with a bonus when you complete it!"
	index = "Battlecry~Legendary"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.category == "Minion" and self.aliveonBoard():
			option = self.chooseFixedOptions(comment, options=[Westfall(), Ironforge(), EasternPlaguelands()])
			self.goDormant(type(option).flightPath(self))
		
	
class Westfall(Option):
	name, category = "Westfall", "Option_Spell"
	mana, attack, health = 0, -1, -1
	flightPath = Trig_FlightmasterDungar_Westfall
	
	
class Ironforge(Option):
	name, category = "Ironforge", "Option_Spell"
	mana, attack, health = 0, -1, -1
	flightPath = Trig_FlightmasterDungar_Ironforge
	
	
class EasternPlaguelands(Option):
	name, category = "Eastern Plaguelands", "Option_Spell"
	mana, attack, health = 0, -1, -1
	flightPath = Trig_FlightmasterDungar_EasternPlaguelands
	
	
class Nobleman(Minion):
	Class, race, name = "Neutral", "", "Nobleman"
	mana, attack, health = 3, 2, 3
	name_CN = "贵族"
	numTargets, Effects, description = 0, "", "Battlecry: Create a Golden copy of a random card in your hand"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if ownHand := self.Game.Hand_Deck.hands[self.ID]:
			self.addCardtoHand(self.copyCard(numpyChoice(ownHand), self.ID), self.ID)
		
	
class Cheesemonger(Minion):
	Class, race, name = "Neutral", "", "Cheesemonger"
	mana, attack, health = 4, 3, 6
	numTargets, Effects, description = 0, "", "Whenever your opponent casts a spell, add a spell with the same Cost to your hand"
	name_CN = "奶酪商贩"
	trigBoard = Trig_Cheesemonger
	
	
class GuildTrader(Minion):
	Class, race, name = "Neutral", "", "Guild Trader"
	mana, attack, health = 4, 3, 4
	numTargets, Effects, description = 0, "Spell Damage_2", "Tradeable, Spell Damage +2"
	name_CN = "工会商人"
	
	
class RoyalLibrarian(Minion):
	Class, race, name = "Neutral", "", "Royal Librarian"
	mana, attack, health = 4, 3, 4
	name_CN = "王室图书管理员"
	numTargets, Effects, description = 1, "", "Tradeable. Battlecry: Silence a minion"
	index = "Battlecry"
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard and obj is not self
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.Game.silenceMinions(target)
		
	
class SpiceBreadBaker(Minion):
	Class, race, name = "Neutral", "", "Spice Bread Baker"
	mana, attack, health = 4, 3, 2
	name_CN = "香料面包师"
	numTargets, Effects, description = 0, "", "Battlecry: Restore Health to your hero equal to your hand size"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if handSize := len(self.Game.Hand_Deck.hands[self.ID]):
			self.heals(self.Game.heroes[self.ID], self.calcHeal(handSize))
		
	
class StubbornSuspect(Minion):
	Class, race, name = "Neutral", "", "Stubborn Suspect"
	mana, attack, health = 4, 3, 3
	numTargets, Effects, description = 0, "", "Deathrattle: Summon a random 3-Cost minion"
	name_CN = "顽固的嫌疑人"
	deathrattle = Death_StubbornSuspect
	
	
class LionsGuard(Minion):
	Class, race, name = "Neutral", "", "Lion's Guard"
	mana, attack, health = 5, 4, 6
	name_CN = "暴风城卫兵"
	numTargets, Effects, description = 0, "", "Battlecry: If you have 15 or less Health, gain +2/+4 and Taunt"
	index = "Battlecry"
	def effCanTrig(self):
		self.effectViable = self.Game.heroes[self.ID].health < 16
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.onBoard and self.Game.heroes[self.ID].health < 16:
			self.giveEnchant(self, 2, 4, effGain="Taunt", source=LionsGuard)
		
	
class StormwindGuard(Minion):
	Class, race, name = "Neutral", "", "Stormwind Guard"
	mana, attack, health = 5, 4, 5
	name_CN = "暴风城卫兵"
	numTargets, Effects, description = 0, "Taunt", "Taunt. Battlecry: Give adjacent minions +1/+1"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.onBoard and (neighbors := self.Game.neighbors2(self)[0]):
			self.giveEnchant(neighbors, 1, 1, source=StormwindGuard)
		
	
class BattlegroundBattlemaster(Minion):
	Class, race, name = "Neutral", "", "Battleground Battlemaster"
	mana, attack, health = 6, 5, 5
	numTargets, Effects, description = 0, "", "Adjacent minions have Windfury"
	name_CN = "战场军官"
	aura = Aura_BattlegroundBattlemaster
	
	
class CityArchitect(Minion):
	Class, race, name = "Neutral", "", "City Architect"
	mana, attack, health = 6, 4, 4
	name_CN = "城市建筑师"
	numTargets, Effects, description = 0, "", "Battlecry: Summon two 0/5 Castle Walls with Taunt"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon([CastleWall(self.Game, self.ID) for _ in (0, 1)], relative="<>")
		
	
class CastleWall(Minion):
	Class, race, name = "Neutral", "", "Castle Wall"
	mana, attack, health = 2, 0, 5
	name_CN = "城堡石墙"
	numTargets, Effects, description = 0, "Taunt", "Taunt"
	index = "Uncollectible"
	
	
class CorneliusRoame(Minion):
	Class, race, name = "Neutral", "", "Cornelius Roame"
	mana, attack, health = 6, 4, 5
	name_CN = "考内留斯·罗姆"
	numTargets, Effects, description = 0, "", "At the start and end of each player's turn, draw a card"
	index = "Legendary"
	trigBoard = Trig_CorneliusRoame
	
	
class LadyPrestor(Minion):
	Class, race, name = "Neutral", "", "Lady Prestor"
	mana, attack, health = 6, 6, 7
	name_CN = "普瑞斯托女士"
	numTargets, Effects, description = 0, "", "Battlecry: Transform minions in your deck into random Dragons. (They keep their original stats and Cost)"
	index = "Battlecry~Legendary"
	poolIdentifier = "Dragons"
	@classmethod
	def generatePool(cls, pools):
		return "Dragons", pools.MinionswithRace["Dragon"]
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		game = self.Game
		ownDeck = game.Hand_Deck.decks[self.ID]
		minions = [i for i, card in enumerate(ownDeck) if card.category == "Minion"]
		if minions:
			dragons = numpyChoice(self.rngPool("Dragons"), len(minions), replace=True)
			for i, newCard in zip(minions, dragons):
				game.Hand_Deck.extractfromDeck(i, self.ID)
				card = newCard(game, self.ID)
				ownDeck.insert(i, card)
				card.entersDeck()
		
	
class MoargForgefiend(Minion):
	Class, race, name = "Neutral", "Demon", "Mo'arg Forgefiend"
	mana, attack, health = 8, 8, 8
	numTargets, Effects, description = 0, "Taunt", "Taunt. Deathrattle: Gain 8 Armor"
	name_CN = "莫尔葛熔魔"
	deathrattle = Death_MoargForgefiend
	
	
class VarianKingofStormwind(Minion):
	Class, race, name = "Neutral", "", "Varian, King of Stormwind"
	mana, attack, health = 8, 7, 7
	name_CN = "瓦里安，暴风城国王"
	numTargets, Effects, description = 0, "", "Battlecry: Draw a Rush minion to gain Rush. Repeat for Taunt and Divine Shield"
	index = "Battlecry~Legendary"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		curGame = self.Game
		#在挑选Rush的时候需要先把有Rush，Taunt和Divine Shield的都找到（三个列表可以有交集）
		#挑Rush的时候随意，但是需要把挑出来的这个随从从三个列表之路移除。之后挑Taunt的时候，如果列表里还有Taunt，则直接挑；否则检测Rush的那个随从是否有Taunt
		#如果这个Rush随从有Taunt，则说明该随从是唯一拥有Taunt的，只是先一步被Rush挑走了。如果Rush还有的选，则Rush可以重新挑选（同样在3个列表之中移除），并把这个既有Rush也有Taunt的随从让给Taunt
		#在前面两个都挑完之后，看Divine是否存在，如果有，则在Divine中挑选；如果Divine没有，则检测Rush和Taunt选中的随从是否有Divine（它们是唯二可能有Divine的随从了）
		#如果Rush和Taunt的随从都有Divine，则随机一个给Divine，然后自己再选。如果只有一个有，则给Divine之后自己再重新选。如果都没有再随意。
		#然后就可以确定第一个Rush的挑选序号
		ownDeck = curGame.Hand_Deck.decks[self.ID]
		pool_Rush = [card for card in ownDeck if card.category == "Minion" and card.effects["Rush"] > 0]
		pool_Taunt = [card for card in ownDeck if card.category == "Minion" and card.effects["Taunt"] > 0]
		pool_Divine = [card for card in ownDeck if card.category == "Minion" and card.effects["Divine Shield"] > 0]
		#When first picking a Rush minion, the choice is not restricted
		minion_Rush = numpyChoice(pool_Rush) if pool_Rush else None
		if minion_Rush: #The Rush minion picked must be excluded from the the remaining Rush, Taunt and Divine pool
			pool_Rush.remove(minion_Rush)
			if minion_Rush in pool_Taunt: pool_Taunt.remove(minion_Rush)
			if minion_Rush in pool_Divine: pool_Divine.remove(minion_Rush)
		#When picking the Taunt minion, if there is still a pool of Taunt minion, nothing happens; if the remain pool is empty,
		# and the Rush minion has Taunt and there is a remaining pool of Rush, then the Taunt will take the chosen Rush minion.
		# The Rush minion will need to pick another from the remaining Rush pool
		minion_Taunt = numpyChoice(pool_Taunt) if pool_Taunt else None
		if minion_Taunt:
			pool_Taunt.remove(minion_Taunt)
			if minion_Taunt in pool_Rush: pool_Rush.remove(minion_Taunt)
			if minion_Taunt in pool_Divine: pool_Divine.remove(minion_Taunt)
		elif minion_Rush and minion_Rush.effects["Taunt"] > 0 and pool_Rush:
			minion_Taunt = minion_Rush
			minion_Rush = numpyChoice(pool_Rush)
			pool_Rush.remove(minion_Rush)
			if minion_Rush in pool_Taunt: pool_Taunt.remove(minion_Rush)
			if minion_Rush in pool_Divine: pool_Divine.remove(minion_Rush)
		#If there isn't a remaining pool of Divine minions, and the picked Rush minion has Divine Shield,
		# and the picked Taunt minion could also have Taunt.
		if not pool_Divine:
			divineCanTakeRush = minion_Rush and minion_Rush.effects["Divine Shield"] > 0 and pool_Rush
			divineCanTakeTaunt = minion_Taunt and minion_Taunt.effects["Divine Shield"] > 0 and pool_Taunt
			if divineCanTakeRush and (not divineCanTakeTaunt or numpyRandint(2)):
				pool_Divine.append(minion_Rush)
				minion_Rush = numpyChoice(pool_Rush)
		if minion_Rush:
			self.Game.Hand_Deck.drawCard(self.ID, ownDeck.index(minion_Rush))
			self.giveEnchant(self, "Rush", source=VarianKingofStormwind)
		#在挑选Taunt的时候把有Taunt和Divine Shield的都找到（两份个列表可以有交集）
		#挑Taunt的时候随意，但是需要把挑出来的这个随从从三个列表之路移除。之后挑Divine的时候，如果列表里还有Divine，则直接挑；否则检测Taunt的那个随从是否有Divine
		#如果这个Taunt随从有Divine，则说明该随从是唯一拥有Divine的，只是先一步被Taunt挑走了。如果Rush还有的选，则Rush可以重新挑选（同样在3个列表之中移除），并把这个既有Rush也有Taunt的随从让给Taunt
		pool_Taunt = [card for card in ownDeck if card.category == "Minion" and card.effects["Taunt"] > 0]
		pool_Divine = [card for card in ownDeck if card.category == "Minion" and card.effects["Divine Shield"] > 0]
		#When first picking a Rush minion, the choice is not restricted
		minion_Taunt = numpyChoice(pool_Taunt) if pool_Taunt else None
		if minion_Taunt:  #The Rush minion picked must be excluded from the the remaining Rush, Taunt and Divine pool
			pool_Taunt.remove(minion_Taunt)
			if minion_Taunt in pool_Divine: pool_Divine.remove(minion_Taunt)
		minion_Divine = numpyChoice(pool_Divine) if pool_Divine else None
		if not minion_Divine and minion_Taunt and minion_Taunt.effects["Divine Shield"] > 0 and pool_Taunt:
			minion_Taunt = numpyChoice(pool_Taunt)
		if minion_Taunt:
			self.Game.Hand_Deck.drawCard(self.ID, ownDeck.index(minion_Taunt))
			self.giveEnchant(self, effGain="Taunt", source=VarianKingofStormwind)
		if self.drawCertainCard(lambda card: card.category == "Minion" and card.effects["Divine Shield"] > 0)[0]:
			self.giveEnchant(self, effGain="Divine Shield", source=VarianKingofStormwind)
		
	
class GoldshireGnoll(Minion):
	Class, race, name = "Neutral", "", "Goldshire Gnoll"
	mana, attack, health = 10, 5, 4
	numTargets, Effects, description = 0, "Rush", "Rush. Costs (1) less for each other card in your hand"
	name_CN = "闪金镇豺狼人"
	trigHand = Trig_GoldshireGnoll
	def selfManaChange(self):
		self.mana -= len(self.Game.Hand_Deck.hands[self.ID]) - 1
		
	
class DemonslayerKurtrus(Minion):
	Class, race, name = "Demon Hunter", "", "Demonslayer Kurtrus"
	mana, attack, health = 5, 7, 7
	name_CN = "屠魔者库尔特鲁斯"
	numTargets, Effects, description = 0, "", "Battlecry: For the rest of the game, cards you draw cost (2) less"
	index = "Battlecry~Legendary~Uncollectible"
	trigEffect = DemonslayerKurtrus_Effect
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		DemonslayerKurtrus_Effect(self.Game, self.ID).connect()
		
	
class ClosethePortal(Quest):
	Class, name = "Demon Hunter", "Close the Portal"
	numTargets, mana, Effects = 0, -1, ""
	name_CN = "关闭传送门"
	description = "Questline: Draw 5 cards in one turn. Reward: Demonslayer Kurtrus"
	index = "Legendary~Uncollectible"
	numNeeded, newQuest, reward = 5, None, DemonslayerKurtrus
	race, trigBoard = "Questline", Trig_FinalShowdown
	
	
class GainMomentum(Quest):
	Class, name = "Demon Hunter", "Gain Momentum"
	numTargets, mana, Effects = 0, -1, ""
	name_CN = "汲取动力"
	description = "Questline: Draw 5 cards in one turn. Reward: Reduce the Cost of the cards in your hand by (1)"
	index = "Legendary~Uncollectible"
	numNeeded, newQuest, reward = 5, ClosethePortal, None
	race, trigBoard = "Questline", Trig_FinalShowdown
	def questEffect(self, game, ID):
		trig = next(trig for trig in self.trigsBoard if isinstance(trig, Trig_FinalShowdown))
		for card in trig.memory:
			if card.inHand: ManaMod(card, by=-1).applies()
		
	
class FinalShowdown(Quest):
	Class, name = "Demon Hunter", "Final Showdown"
	numTargets, mana, Effects = 0, 1, ""
	name_CN = "一决胜负"
	description = "Questline: Draw 4 cards in one turn. Reward: Reduce the Cost of the cards drawn by (1)"
	index = "Legendary"
	numNeeded, newQuest, reward = 4, GainMomentum, None
	race, trigBoard = "Questline", Trig_FinalShowdown
	def questEffect(self, game, ID):
		trig = next(trig for trig in self.trigsBoard if isinstance(trig, Trig_FinalShowdown))
		for card in trig.memory:
			if card.inHand: ManaMod(card, by=-1).applies()
		
	
class Metamorfin(Minion):
	Class, race, name = "Demon Hunter", "Murloc", "Metamorfin"
	mana, attack, health = 1, 1, 2
	name_CN = "魔变鱼人"
	numTargets, Effects, description = 0, "Taunt", "Taunt. Battlecry: If you've cast a Fel spell this turn, gain +2/+2"
	index = "Battlecry"
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.examCardPlays(self.ID, turnInd=self.Game.turnInd, cond=lambda tup: tup[0].school == "Fel")
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.Game.Counters.examCardPlays(self.ID, turnInd=self.Game.turnInd, cond=lambda tup: tup[0].school == "Fel"):
			self.giveEnchant(self, 2, 2, source=Metamorfin)
		
	
class SigilofAlacrity(Spell_Sigil):
	Class, school, name = "Demon Hunter", "Shadow", "Sigil of Alacrity"
	numTargets, mana, Effects = 0, 1, ""
	description = "At the start of your next turn, draw a card and reduce its Cost by (1)"
	name_CN = "敏捷咒符"
	trigEffect = SigilofAlacrity_Effect
	
	
class FelBarrage(Spell):
	Class, school, name = "Demon Hunter", "Fel", "Fel Barrage"
	numTargets, mana, Effects = 0, 2, ""
	description = "Deal 2 damage to the low Health enemy, twice"
	name_CN = "邪能弹幕"
	def text(self): return self.calcDamage(2)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		damage = self.calcDamage(2)
		for _ in (1, 2):
			chars, lowestHealth = [], numpy.inf
			for obj in self.Game.charsAlive(3-self.ID):
				if obj.health < lowestHealth: chars, lowestHealth = [obj], obj.health
				elif obj.health == lowestHealth: chars.append(obj)
			if chars: self.dealsDamage(numpyChoice(chars), damage)
			else: break
		
	
class ChaosLeech(Spell):
	Class, school, name = "Demon Hunter", "Fel", "Chaos Leech"
	numTargets, mana, Effects = 1, 3, "Lifesteal"
	description = "Lifesteal. Deal 3 damage to a minion. Outcast: Deal 5 instead"
	name_CN = "混乱吸取"
	index = "Outcast"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.outcastcanTrig(self)
		
	def text(self): return "%d, %d"%(self.calcDamage(3), self.calcDamage(5))
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(target, self.calcDamage(5 if posinHand in (-1, 0) else 3))
		
	
class LionsFrenzy(Weapon):
	Class, name, description = "Demon Hunter", "Lion's Frenzy", "Has Attack equal to the number of cards you've drawn this turn"
	mana, attack, durability, Effects = 3, 0, 2, ""
	name_CN = "雄狮之怒"
	trigBoard = Trig_LionsFrenzy
	def statCheckResponse(self):
		if self.onBoard: self.attack = sum(tup[0] == "DrawCard" and tup[1] == self.ID for tup in self.Game.Counters.events[self.Game.turnInd])
		
	
class Felgorger(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Felgorger"
	mana, attack, health = 4, 4, 3
	name_CN = "邪能吞食者"
	numTargets, Effects, description = 0, "", "Battlecry: Draw a Fel spell. Reduce its Cost by (2)"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		spell, mana, entersHand = self.drawCertainCard(lambda card: card.school == "Fel")
		if entersHand: ManaMod(spell, by=-2).applies()
		
	
class PersistentPeddler(Minion):
	Class, race, name = "Demon Hunter", "", "Persistent Peddler"
	mana, attack, health = 4, 4, 3
	numTargets, Effects, description = 0, "", "Tradeable. Deathrattle: Summon a Persistent Peddler from your deck"
	name_CN = "固执的商贩"
	deathrattle = Death_PersistentPeddler
	
	
class IreboundBrute(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Irebound Brute"
	mana, attack, health = 8, 6, 7
	numTargets, Effects, description = 0, "Taunt", "Taunt. Costs (1) less for each card drawn this turn"
	name_CN = "怒缚蛮兵"
	trigHand = Trig_IreboundBrute
	def selfManaChange(self):
		self.mana -= sum(tup[0] == "DrawCard" and tup[1] == self.ID for tup in self.Game.Counters.events[self.Game.turnInd])
		
	
class JaceDarkweaver(Minion):
	Class, race, name = "Demon Hunter", "", "Jace Darkweaver"
	mana, attack, health = 8, 7, 5
	name_CN = "杰斯·织暗"
	numTargets, Effects, description = 0, "", "Battlecry: Cast all Fel spells you've played this game(targets enemies if possible)"
	index = "Battlecry~Legendary"
	def text(self): return self.Game.Counters.examCardPlays(self.ID, veri_sum_ls=1, cond=lambda tup: tup[0].school == "Fel")
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		game = self.Game
		if tups := game.Counters.examCardPlays(self.ID, veri_sum_ls=2, cond=lambda tup: tup[0].school == "Fel"):
			numpyShuffle(tups)
			for tup in tups:
				game.fabCard(tup, self.ID, self).cast(prefered=lambda obj: obj.ID != self.ID)
				game.gathertheDead(decideWinner=True)
		
	
class GufftheTough(Minion):
	Class, race, name = "Druid", "Beast", "Guff the Tough"
	mana, attack, health = 5, 8, 8
	name_CN = "铁肤古夫"
	numTargets, Effects, description = 0, "", "Taunt. Battlecry: Give your hero +8 Attack this turn. Gain 8 Armor"
	index = "Battlecry~Legendary~Uncollectible"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveHeroAttackArmor(self.ID, attGain=8, armor=8, source=GufftheTough)
		
	
class FeralFriendsy(Quest):
	Class, name = "Druid", "Feral Friendsy"
	numTargets, mana, Effects = 0, -1, ""
	name_CN = "野性暴朋"
	description = "Questline: Gain 6 Attack with your hero. Reward: Guff the Tough"
	index = "Legendary~Uncollectible"
	numNeeded, newQuest, reward = 6, None, GufftheTough
	race, trigBoard = "Questline", Trig_LostinthePark
	
	
class DefendtheSquirrels(Quest):
	Class, name = "Druid", "Defend the Squirrels"
	numTargets, mana, Effects = 0, -1, ""
	name_CN = "保护松鼠"
	description = "Questline: Gain 5 Attack with your hero. Reward: Gain 5 Armor and draw a card"
	numNeeded, newQuest, reward = 5, FeralFriendsy, None
	index = "Legendary~Uncollectible"
	race, trigBoard = "Questline", Trig_LostinthePark
	def questEffect(self, game, ID):
		self.giveHeroAttackArmor(ID, armor=5)
		game.Hand_Deck.drawCard(ID)
		
	
class LostinthePark(Quest):
	Class, name = "Druid", "Lost in the Park"
	numTargets, mana, Effects = 0, 1, ""
	name_CN = "游园迷梦"
	description = "Questline: Gain 4 Attack with your hero. Reward: Gain 5 Armor"
	numNeeded, newQuest, reward = 4, DefendtheSquirrels, None
	index = "Legendary"
	race, trigBoard = "Questline", Trig_LostinthePark
	def questEffect(self, game, ID):
		self.giveHeroAttackArmor(ID, armor=5)
		
	
class Fertilizer(Spell):
	Class, school, name = "Druid", "Nature", "Fertilizer"
	numTargets, mana, Effects = 0, 1, ""
	name_CN = "肥料滋养"
	description = "Give your minions +1 Attack"
	index = "Uncollectible"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(self.Game.minionsonBoard(self.ID), 1, 0, source=Fertilizer)
		
	
class NewGrowth(Spell):
	Class, school, name = "Druid", "Nature", "New Growth"
	numTargets, mana, Effects = 0, 1, ""
	name_CN = "新生细苗"
	description = "Summon a 2/2 Treant"
	index = "Uncollectible"
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon(Treant_Stormwind(self.Game, self.ID))
		
	
class Fertilizer_Option(Option):
	name, description = "Fertilizer", "Give your minions +1 Attack"
	mana, attack, health = 1, -1, -1
	spell = Fertilizer
	
	
class NewGrowth_Option(Option):
	name, description = "New Growth", "Summon a 2/2 Treant"
	mana, attack, health = 1, -1, -1
	spell = NewGrowth
	def available(self):
		return self.keeper.Game.space(self.keeper.ID)
		
	
class SowtheSoil(Spell):
	Class, school, name = "Druid", "Nature", "Sow the Soil"
	numTargets, mana, Effects = 0, 1, ""
	name_CN = "播种施肥"
	description = "Choose One - Give your minions +1 Attack; or Summon a 2/2 Treant"
	options = (Fertilizer_Option, NewGrowth_Option)
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if choice: self.summon(Treant_Stormwind(self.Game, self.ID))
		if choice < 1: self.giveEnchant(self.Game.minionsonBoard(self.ID), 1, 0, source=SowtheSoil)
		
	
class Treant_Stormwind(Minion):
	Class, race, name = "Neutral", "", "Treant"
	mana, attack, health = 2, 2, 2
	name_CN = "树人"
	numTargets, Effects, description = 0, "", ""
	index = "Uncollectible"
	
	
class VibrantSquirrel(Minion):
	Class, race, name = "Druid", "Beast", "Vibrant Squirrel"
	mana, attack, health = 1, 2, 1
	numTargets, Effects, description = 0, "", "Deathrattle: Shuffle 4 Acorns into your deck. When drawn, summon a 2/1 Squirrel"
	name_CN = "活泼的松鼠"
	deathrattle = Death_VibrantSquirrel
	
	
class Acorn(Spell):
	Class, school, name = "Druid", "", "Acorn"
	numTargets, mana, Effects = 0, 1, ""
	name_CN = "橡果"
	description = "Casts When Drawn. Summon a 2/1 Squirrel"
	index = "Uncollectible"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon(SatisfiedSquirrel(self.Game, self.ID))
		
	
class SatisfiedSquirrel(Minion):
	Class, race, name = "Druid", "Beast", "Satisfied Squirrel"
	mana, attack, health = 1, 2, 1
	name_CN = "满足的松鼠"
	numTargets, Effects, description = 0, "", ""
	index = "Uncollectible"
	
	
class Composting(Spell):
	Class, school, name = "Druid", "Nature", "Composting"
	numTargets, mana, Effects = 0, 2, ""
	description = "Give your minions 'Deathrattle: Draw a card'"
	name_CN = "施肥"
	trigEffect = Death_Composting
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(self.Game.minionsonBoard(self.ID), trig=Death_Composting, trigType="Deathrattle")
		
	
class Wickerclaw(Minion):
	Class, race, name = "Druid", "Beast", "Wickerclaw"
	mana, attack, health = 2, 1, 4
	numTargets, Effects, description = 0, "", "After your hero gains Attack, this minion gain +2 Attack"
	name_CN = "柳魔锐爪兽"
	trigBoard = Trig_Wickerclaw
	
	
class OracleofElune(Minion):
	Class, race, name = "Druid", "", "Oracle of Elune"
	mana, attack, health = 3, 2, 4
	numTargets, Effects, description = 0, "", "After you play a minion that costs (2) or less, summon a copy of it"
	name_CN = "艾露恩神谕者"
	trigBoard = Trig_OracleofElune
	
	
class KodoMount(Spell):
	Class, school, name = "Druid", "", "Kodo Mount"
	numTargets, mana, Effects = 1, 4, ""
	description = "Give a minion +4/+2 and Rush. When it dies, summon a Kodo"
	name_CN = "科多兽坐骑"
	trigEffect = Death_KodoMount
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(target, 4, 2, effGain="Rush", source=KodoMount, trig=Death_KodoMount, trigType="Deathrattle")
		
	
class GuffsKodo(Minion):
	Class, race, name = "Druid", "Beast", "Guff's Kodo"
	mana, attack, health = 3, 4, 2
	name_CN = "古夫的科多兽"
	numTargets, Effects, description = 0, "Rush", "Rush"
	index = "Uncollectible"
	
	
class ParkPanther(Minion):
	Class, race, name = "Druid", "Beast", "Park Panther"
	mana, attack, health = 4, 4, 4
	numTargets, Effects, description = 0, "Rush", "Rush. Whenever this minion attacks, give your hero +3 Attack this turn"
	name_CN = "花园猎豹"
	trigBoard = Trig_ParkPanther
	
	
class BestinShell(Spell):
	Class, school, name = "Druid", "", "Best in Shell"
	numTargets, mana, Effects = 0, 6, ""
	description = "Tradeable. Summon two 2/7 Turtles with Taunt"
	name_CN = "紧壳商品"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon([GoldshellTurtle(self.Game, self.ID) for _ in (0, 1)])
		
	
class GoldshellTurtle(Minion):
	Class, race, name = "Druid", "Beast", "Goldshell Turtle"
	mana, attack, health = 4, 2, 7
	name_CN = "金壳龟"
	numTargets, Effects, description = 0, "Taunt", "Taunt"
	index = "Uncollectible"
	
	
class SheldrasMoontree(Minion):
	Class, race, name = "Druid", "", "Sheldras Moontree"
	mana, attack, health = 8, 5, 5
	name_CN = "沙德拉斯·月树"
	numTargets, Effects, description = 0, "", "Battlecry: The next 3 spells you draw are Cast When Drawn"
	index = "Battlecry~Legendary"
	trigEffect = SheldrasMoontree_Effect
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		SheldrasMoontree_Effect(self.Game, self.ID).connect()
		
	
class DevouringSwarm(Spell):
	Class, school, name = "Hunter", "", "Devouring Swarm"
	numTargets, mana, Effects = 1, 0, ""
	description = "Choose an enemy minion. Your minions attack it, then return any that die to your hand"
	name_CN = "集群撕咬"
	def available(self):
		return self.selectableMinionExists(3 - self.ID)
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard and obj.ID != self.ID
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		game, deads = self.Game, []
		for obj in target:
			if minions := game.minionsAlive(self.ID):
				minions = objs_SeqSorted(minions)[0]
				for o in minions:
					if obj.canBattle():
						if o.canBattle(): game.battle(o, obj)
					else: break
					if (o.dead or o.health < 1) and o not in deads: deads.append(o)
			else: break
		if deads: self.addCardtoHand([self.copyCard(o, self.ID, bareCopy=True) for o in deads], self.ID)
		
	
class TavishMasterMarksman(Minion):
	Class, race, name = "Hunter", "", "Tavish, Master Marksman"
	mana, attack, health = 5, 7, 7
	name_CN = "射击大师塔维什"
	numTargets, Effects, description = 0, "", "Battlecry: For the rest of the game, spells you cast refresh your Hero Power"
	index = "Battlecry~Legendary~Uncollectible"
	trigEffect = TavishMasterMarksman_Effect
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		TavishMasterMarksman_Effect(self.Game, self.ID).connect()
		
	
class KnockEmDown(Quest):
	Class, name = "Hunter", "Knock 'Em Down"
	numTargets, mana, Effects = 0, -1, ""
	name_CN = "干掉他们"
	description = "Questline: Deal damage with 2 spells. Reward: Tavish, Master Marksman"
	index = "Legendary~Uncollectible"
	numNeeded, newQuest, reward = 2, None, TavishMasterMarksman
	race, trigBoard = "Questline", Trig_DefendtheDwarvenDistrict
	
	
class TaketheHighGround(Quest):
	Class, name = "Hunter", "Take the High Ground"
	numTargets, mana, Effects = 0, -1, ""
	name_CN = "占据高地"
	description = "Questline: Deal damage with 2 spells. Reward: Set the Cost of your Hero Power to (0)"
	index = "Legendary~Uncollectible"
	numNeeded, newQuest, reward = 2, KnockEmDown, None
	race, trigBoard = "Questline", Trig_DefendtheDwarvenDistrict
	def questEffect(self, game, ID):
		ManaMod(game.powers[ID], to=0).applies()
		
	
class DefendtheDwarvenDistrict(Quest):
	Class, name = "Hunter", "Defend the Dwarven District"
	numTargets, mana, Effects = 0, 1, ""
	name_CN = "保卫矮人区"
	description = "Questline: Deal damage with 2 spells. Reward: Your Hero Power can target minions"
	index = "Legendary"
	numNeeded, newQuest, reward = 2, TaketheHighGround, None
	race, trigBoard = "Questline", Trig_DefendtheDwarvenDistrict
	def questEffect(self, game, ID):
		self.giveEnchant(game.powers[ID], effGain="Can Target Minions", source=DefendtheDwarvenDistrict)
		
	
class LeatherworkingKit(Weapon):
	Class, name, description = "Hunter", "Leatherworking Kit", "After three friendly Beasts die, draw a Beast and give it +1/+1. Lose 1 Durability"
	mana, attack, durability, Effects = 1, 0, 3, ""
	name_CN = "制皮工具"
	trigBoard = Trig_LeatherworkingKit
	
	
class AimedShot(Spell):
	Class, school, name = "Hunter", "", "Aimed Shot"
	numTargets, mana, Effects = 1, 3, ""
	description = "Deal 3 damage. Your next Hero Power deals two more damage"
	name_CN = "瞄准射击"
	trigEffect = AimedShot_Effect
	def text(self): return self.calcDamage(3)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(target, self.calcDamage(3))
		self.Game.powers[self.ID].getsEffect("Power Damage", amount=2)
		AimedShot_Effect(self.Game, self.ID).connect()
		
	
class RammingMount(Spell):
	Class, school, name = "Hunter", "", "Ramming Mount"
	numTargets, mana, Effects = 1, 3, ""
	description = "Give a minion +2/+2 and Immune while attacking. When it dies, summon a Ram"
	name_CN = "山羊坐骑"
	trigEffect = Death_RammingMount
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(target, 2, 2, source=RammingMount, trigs=((Trig_TavishsRam, "TrigBoard"), (Death_RammingMount, "Deathrattle")))
		
	
class TavishsRam(Minion):
	Class, race, name = "Hunter", "Beast", "Tavish's Ram"
	mana, attack, health = 2, 2, 2
	name_CN = "塔维什的山羊"
	numTargets, Effects, description = 0, "", "Immune while attacking"
	index = "Uncollectible"
	trigBoard = Trig_TavishsRam
	
	
class StormwindPiper(Minion):
	Class, race, name = "Hunter", "Demon", "Stormwind Piper"
	mana, attack, health = 3, 1, 6
	numTargets, Effects, description = 0, "", "After this minion attacks, give your Beasts +1/+1"
	name_CN = "暴风城吹笛人"
	trigBoard = Trig_StormwindPiper
	
	
class RodentNest(Minion):
	Class, race, name = "Hunter", "", "Rodent Nest"
	mana, attack, health = 4, 2, 2
	numTargets, Effects, description = 0, "", "Deathrattle: Summon five 1/1 Rats"
	name_CN = "老鼠窝"
	deathrattle = Death_RodentNest
	
	
class ImportedTarantula(Minion):
	Class, race, name = "Hunter", "Beast", "Imported Tarantula"
	mana, attack, health = 5, 4, 5
	numTargets, Effects, description = 0, "", "Tradeable. Deathrattle: Summon two 1/1 Spiders with Poisonous and Rush"
	name_CN = "进口狼蛛"
	deathrattle = Death_ImportedTarantula
	
	
class InvasiveSpiderling(Minion):
	Class, race, name = "Hunter", "Beast", "Invasive Spiderling"
	mana, attack, health = 2, 1, 1
	name_CN = "入侵的蜘蛛"
	numTargets, Effects, description = 0, "Poisonous,Rush", "Poisonous, Rush"
	index = "Uncollectible"
	
	
class TheRatKing(Minion):
	Class, race, name = "Hunter", "Beast", "The Rat King"
	mana, attack, health = 5, 5, 5
	name_CN = "鼠王"
	numTargets, Effects, description = 0, "Rush", "Rush. Deathrattle: Go Dormant. Revive after 5 friendly minions die"
	index = "Legendary"
	deathrattle = Death_TheRatKing
	
	
class RatsofExtraordinarySize(Spell):
	Class, school, name = "Hunter", "", "Rats of Extraordinary Size"
	numTargets, mana, Effects = 0, 6, ""
	description = "Summon seven 1/1 Rats. Any that can't fit on the battlefield go to your hand with +4/+4"
	name_CN = "硕鼠成群"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		size = self.Game.space(self.ID)
		if minions2Board := [Rat(self.Game, self.ID) for i in range(size)]: self.summon(minions2Board)
		if minions2Hand := [Rat(self.Game, self.ID) for i in range(7-size)]:
			self.giveEnchant(minions2Hand, 4, 4, source=RatsofExtraordinarySize)
			self.addCardtoHand(minions2Hand, self.ID)
		
	
class Rat(Minion):
	Class, race, name = "Hunter", "Beast", "Rat"
	mana, attack, health = 1, 1, 1
	name_CN = "老鼠"
	numTargets, Effects, description = 0, "", ""
	index = "Uncollectible"
	
	
class HotStreak(Spell):
	Class, school, name = "Mage", "Fire", "Hot Streak"
	numTargets, mana, Effects = 0, 0, ""
	description = "Your next Fire spell costs (2) less"
	name_CN = "炽热连击"
	trigEffect = GameManaAura_HotStreak
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		GameManaAura_HotStreak(self.Game, self.ID).auraAppears()
		
	
class FirstFlame(Spell):
	Class, school, name = "Mage", "Fire", "First Flame"
	numTargets, mana, Effects = 1, 1, ""
	description = "Deal 2 damage to a minion. Add a Second Flame to your hand"
	name_CN = "初始之火"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def text(self): return self.calcDamage(2)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(target, self.calcDamage(2))
		self.addCardtoHand(SecondFlame, self.ID)
		
	
class SecondFlame(Spell):
	Class, school, name = "Mage", "Fire", "Second Flame"
	numTargets, mana, Effects = 1, 1, ""
	name_CN = "传承之火"
	description = "Deal 2 damage to a minion"
	index = "Uncollectible"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def text(self): return self.calcDamage(2)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(target, self.calcDamage(2))
		
	
class ArcanistDawngrasp(Minion):
	Class, race, name = "Mage", "", "Arcanist Dawngrasp"
	mana, attack, health = 5, 7, 7
	name_CN = "奥术师晨拥"
	numTargets, Effects, description = 0, "", "Battlecry: For the rest of the game, you have Spell Damage +3"
	index = "Battlecry~Legendary~Uncollectible"
	trigEffect = ArcanistDawngrasp_Effect
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.Game.heroes[self.ID].getsEffect("Spell Damage", amount=3)
		ArcanistDawngrasp_Effect(self.Game, self.ID).connect()
		
	
class ReachthePortalRoom(Quest):
	Class, name = "Mage", "Reach the Portal Room"
	numTargets, mana, Effects = 0, -1, ""
	name_CN = "抵达传送大厅"
	description = "Questline: Cast a Fire, Frost and Arcane spell. Reward: Arcanist Dawngrasp"
	index = "Legendary~Uncollectible"
	numNeeded, newQuest, reward = 3, None, ArcanistDawngrasp
	race, trigBoard = "Questline", Trig_SorcerersGambit
	@classmethod
	def getProgress(cls, card):
		if not card.inHand and "CardBeenPlayed" in (trigs := card.Game.trigsBoard[card.ID]):
			if trig := next((trig for trig in trigs if isinstance(trig, Trig_SorcerersGambit)), None):
				return "Fire: %d\nFrost: %d\nArcane: %d"%(("Fire" in trig.memory)+0, ("Frost" in trig.memory)+0, ("Arcane" in trig.memory)+0)
		return ""
		
	def text(self): return ReachthePortalRoom.getProgress(self)
		
	
class StallforTime(Quest):
	Class, name = "Mage", "Stall for Time"
	numTargets, mana, Effects = 0, -1, ""
	name_CN = "拖延时间"
	description = "Questline: Cast a Fire, Frost and Arcane spell. Reward: Discover one"
	index = "Legendary~Uncollectible"
	numNeeded, newQuest, reward = 3, ReachthePortalRoom, None
	race, trigBoard = "Questline", Trig_SorcerersGambit
	def questEffect(self, game, ID):
		self.discoverNew_MultiPools('', lambda: SorcerersGambit.decidePools(self))
		
	def text(self): return ReachthePortalRoom.getProgress(self)
		
	
class SorcerersGambit(Quest):
	Class, school, name = "Mage", "", "Sorcerer's Gambit"
	numTargets, mana, Effects = 0, 1, ""
	name_CN = "巫师的计策"
	description = "Questline: Cast a Fire, Frost and Arcane spell. Reward: Draw a spell"
	index = "Legendary"
	race, trigBoard = "Questline", Trig_SorcerersGambit
	numNeeded, newQuest, reward = 3, StallforTime, None
	poolIdentifier = "Fire Spells as Mage"
	@classmethod
	def generatePool(cls, pools):
		classes, lists = [], []
		for Class in pools.Classes:
			fire, frost, arcane = [], [], []
			for card in pools.ClassCards[Class]:
				if card.category == "Spell":
					if card.school == "Fire": fire.append(card)
					elif card.school == "Frost": frost.append(card)
					elif card.school == "Arcane": arcane.append(card)
			classes += ["Fire Spells as %s" % Class, "Frost Spells as %s" % Class, "Arcane Spells as %s" % Class]
			lists += [fire, frost, arcane]
		return classes, lists
		
	@classmethod
	def decidePools(cls, self):
		Class = class4Discover(self)
		return [self.rngPool("Fire Spells as " + Class),
		 		self.rngPool("Frost Spells as " + Class),
		 		self.rngPool("Arcane Spells as " + Class)]
		
	def questEffect(self, game, ID):
		self.drawCertainCard(lambda card: card.category == "Spell")
		
	def text(self): return ReachthePortalRoom.getProgress(self)
		
	
class CelestialInkSet(Weapon):
	Class, name, description = "Mage", "Celestial Ink Set", "After you spend 5 Mana on spells, reduce the Cost of a spell in your hand by (5)"
	mana, attack, durability, Effects = 2, 0, 2, ""
	name_CN = "星空墨水套装"
	trigBoard = Trig_CelestialInkSet		
	
	
class Ignite(Spell):
	Class, school, name = "Mage", "Fire", "Ignite"
	numTargets, mana, Effects = 1, 2, ""
	description = "Deal 2 damgae. Shuffle an Ignite into your deck that deals one more damage"
	name_CN = "点燃"
	info1 = 2
	def text(self): return self.calcDamage(self.info1)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(target, self.calcDamage(self.info1))
		spell = Ignite(self.Game, self.ID)
		spell.info1 = self.info1 + 1
		self.shuffleintoDeck(spell)
		
	
class PrestorsPyromancer(Minion):
	Class, race, name = "Mage", "", "Prestor's Pyromancer"
	mana, attack, health = 2, 2, 3
	name_CN = "普瑞斯托的炎术师"
	numTargets, Effects, description = 0, "", "Battlecry: Your next Fire spell has Spell Damage +2"
	index = "Battlecry"
	trigEffect = PrestorsPyromancer_Effect
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.Game.heroes[self.ID].getsEffect("Fire Spell Damage", amount=2)
		PrestorsPyromancer_Effect(self.Game, self.ID).connect()
		
	
class FireSale(Spell):
	Class, school, name = "Mage", "Fire", "Fire Sale"
	numTargets, mana, Effects = 0, 4, ""
	description = "Tradeable. Deal 3 damage to all minions"
	name_CN = "火热促销"
	def text(self): return self.calcDamage(3)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(self.Game.minionsonBoard(), self.calcDamage(3))
		
	
class SanctumChandler(Minion):
	Class, race, name = "Mage", "Elemental", "Sanctum Chandler"
	mana, attack, health = 5, 4, 5
	numTargets, Effects, description = 0, "", "After you cast a Fire spell, draw a spell"
	name_CN = "圣殿蜡烛商"
	trigBoard = Trig_SanctumChandler
	
	
class ClumsyCourier(Minion):
	Class, race, name = "Mage", "", "Clumsy Courier"
	mana, attack, health = 7, 4, 5
	name_CN = "笨拙的信使"
	numTargets, Effects, description = 0, "", "Battlecry: Cast the highest Cost spell from your hand"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if indices := pickInds_HighestAttr(self.Game.Hand_Deck.hands[self.ID],
										   cond=lambda card: card.category == "Spell"):
			self.Game.Hand_Deck.extractfromHand(numpyChoice(indices), self.ID)[0].cast()
		
	
class GrandMagusAntonidas(Minion):
	Class, race, name = "Mage", "", "Grand Magus Antonidas"
	mana, attack, health = 8, 6, 6
	name_CN = "大魔导师安东尼达斯"
	numTargets, Effects, description = 0, "", "Battlecry: If you've cast a Fire spell on each of your last three turns, cast 3 Fireballs at random enemies. (0/3)"
	index = "Battlecry~Legendary"
	def numPastTurnwithFireSpells(self):
		i, pastTurnInd, examCardPlays = 0, self.Game.pastTurnInd, self.Game.Counters.examCardPlays
		for backby in (1, 2, 3):
			if (turnInd := pastTurnInd(self.ID, backby=backby) ) >= 0 \
					and examCardPlays(self.ID, turnInd=turnInd, cond=lambda tup: tup[0].school == "Fire"):
				i += 1
			else: break
		return i
		
	def effCanTrig(self):
		self.effectViable = self.numPastTurnwithFireSpells() >= 3
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if GrandMagusAntonidas.numPastTurnwithFireSpells(self) >= 3:
			for _ in (0, 1, 2):
				if objs := self.Game.charsAlive(3-self.ID):
					Fireball(self.Game, self.ID).cast(prefered=lambda obj: obj.ID != self.ID)
				else: break
		
	
class BlessedGoods(Spell):
	Class, school, name = "Paladin", "Holy", "Blessed Goods"
	numTargets, mana, Effects = 0, 1, ""
	description = "Discover a Secret, Weapon, or Divine Shield minion"
	name_CN = "受祝福的货物"
	poolIdentifier = "Divine Shield Minions as Paladin"
	@classmethod
	def generatePool(cls, pools):
		neutralWeapons = [card for card in pools.NeutralCards if card.category == "Weapon"]
		classWeapons = {Class: [card for card in cards if card.category == "Weapon"]
						for Class, cards in pools.ClassCards.items()}
		ls, weaponsasClass = ["Weapons as "+Class for Class in classWeapons], [cards+neutralWeapons for cards in classWeapons.values()]
		ls_Minions, minionsasClass = genPool_CertainMinionsasClass(pools, "Divine Shield", cond=lambda card: "Divine Shield" in card.Effects)
		return ls + ls_Minions, weaponsasClass + minionsasClass
		
	def decidePool(self):
		Class = class4Discover(self)
		return [secrets2Discover(self), self.rngPool("Weapons as "+Class), self.rngPool("Divine Shield as "+Class)]
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.discoverNew_MultiPools(comment, lambda : BlessedGoods.decidePool(self))
		
	
class PrismaticJewelKit(Weapon):
	Class, name, description = "Paladin", "Prismatic Jewel Kit", "After a friendly minion loses Divine Shield, give minions in your hand +1/+1. Lose 1 Durability"
	mana, attack, durability, Effects = 1, 0, 3, ""
	name_CN = "棱彩珠宝工具"
	trigBoard = Trig_PrismaticJewelKit
	
	
class LightbornCariel(Minion):
	Class, race, name = "Paladin", "", "Lightborn Cariel"
	mana, attack, health = 5, 7, 7
	name_CN = "圣光化身凯瑞尔"
	numTargets, Effects, description = 0, "", "Battlecry: For the rest of the game, your Silver Hand Recruits have +2/+2"
	index = "Battlecry~Legendary~Uncollectible"
	trigEffect = GameAura_LightbornCariel
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		GameAura_LightbornCariel(self.Game, self.ID).auraAppears()
		
	
class AvengetheFallen(Quest):
	Class, name = "Paladin", "Pave the Way"
	numTargets, mana, Effects = 0, -1, ""
	name_CN = "为逝者复仇"
	description = "Questline: Play 3 different 1-Cost cards. Reward: Lightborn Cariel"
	index = "Legendary~Uncollectible"
	numNeeded, newQuest, reward = 3, None, LightbornCariel
	race, trigBoard = "Questline", Trig_RisetotheOccasion
	@classmethod
	def getProgress(cls, card):
		s = ''
		if not card.inHand and "CardBeenPlayed" in (trigs := card.Game.trigsBoard[card.ID]):
			if trig := next((trig for trig in trigs if isinstance(trig, Trig_RisetotheOccasion)), None):
				for obj in trig.memory: s += obj.__name__ + '\n'
		return s
		
	def text(self): return AvengetheFallen.getProgress(self)
		
	
class PavetheWay(Quest):
	Class, name = "Paladin", "Pave the Way"
	numTargets, mana, Effects = 0, -1, ""
	name_CN = "荡平道路"
	description = "Questline: Play 3 different 1-Cost cards. Reward: Upgrade your Hero Power"
	index = "Legendary~Uncollectible"
	numNeeded, newQuest, reward = 3, AvengetheFallen, None
	race, trigBoard = "Questline", Trig_RisetotheOccasion
	def questEffect(self, game, ID):
		if hasattr(typePower := type(game.powers[ID]), "upgrade"):
			typePower.upgrade(game, ID).replacePower()
		
	def text(self): return AvengetheFallen.getProgress(self)
		
	
class RisetotheOccasion(Quest):
	Class, name = "Paladin", "Rise to the Occasion"
	numTargets, mana, Effects = 0, 1, ""
	name_CN = "挺身而出"
	description = "Questline: Play 3 different 1-Cost cards. Reward: Equip a 1/4 Light's Justice"
	index = "Legendary"
	numNeeded, newQuest, reward = 3, PavetheWay, None
	race, trigBoard = "Questline", Trig_RisetotheOccasion
	def questEffect(self, game, ID):
		self.equipWeapon(LightsJustice(game, ID))
		
	def text(self): return AvengetheFallen.getProgress(self)
		
	
class NobleMount(Spell):
	Class, school, name = "Paladin", "", "Noble Mount"
	numTargets, mana, Effects = 1, 2, ""
	description = "Give a minion +1/+1 and Divine Shield. When it dies, summon a Warhorse"
	name_CN = "神圣坐骑"
	trigEffect = Death_NobleMount
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(target, 1, 1, effGain="Divine Shield", source=NobleMount, trig=Death_NobleMount, trigType="Deathrattle")
		
	
class CarielsWarhorse(Minion):
	Class, race, name = "Paladin", "Beast", "Cariel's Warhorse"
	mana, attack, health = 1, 1, 1
	name_CN = "卡瑞尔的战马"
	numTargets, Effects, description = 0, "Divine Shield", "Divine Shield"
	index = "Uncollectible"
	
	
class CityTax(Spell):
	Class, school, name = "Paladin", "", "City Tax"
	numTargets, mana, Effects = 0, 2, "Lifesteal"
	description = "Tradeable. Lifesteal. Deal 1 damage to all enemy minions"
	name_CN = "城建税"
	def text(self): return self.calcDamage(1)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(self.Game.minionsonBoard(3-self.ID), self.calcDamage(1))
		
	
class AllianceBannerman(Minion):
	Class, race, name = "Paladin", "", "Alliance Bannerman"
	mana, attack, health = 3, 2, 2
	name_CN = "联盟旗手"
	numTargets, Effects, description = 0, "", "Battlecry: Draw a minion. Give minions in your hand +1/+1"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.drawCertainCard(lambda card: card.category == "Minion")
		self.giveEnchant([card for card in self.Game.Hand_Deck.hands[self.ID] if card.category == "Minion"], 1, 1,
						 source=AllianceBannerman, add2EventinGUI=False)
		
	
class CatacombGuard(Minion):
	Class, race, name = "Paladin", "", "Catacomb Guard"
	mana, attack, health = 3, 1, 4
	name_CN = "古墓卫士"
	numTargets, Effects, description = 1, "Lifesteal", "Lifesteal. Battlecry: Deal damage equal to this minin's Attack to an enemy minion"
	index = "Battlecry"
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists(3 - self.ID)
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.ID != self.ID and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.attack > 0: self.dealsDamage(target, self.attack)
		
	
class LightbringersHammer(Weapon):
	Class, name, description = "Paladin", "Lightbringer's Hammer", "Lifesteal. Can't attack heroes"
	mana, attack, durability, Effects = 3, 3, 2, "Lifesteal,Can't Attack Heroes"
	name_CN = "光明使者之锤"
	
	
class FirstBladeofWrynn(Minion):
	Class, race, name = "Paladin", "", "First Blade of Wrynn"
	mana, attack, health = 4, 3, 5
	name_CN = "乌瑞恩首席剑士"
	numTargets, Effects, description = 0, "Divine Shield", "Divine Shield. Battlecry: Gain Rush if this has at least 4 Attack"
	index = "Battlecry"
	def effCanTrig(self):
		self.effectViable = self.attack > 3
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.attack > 3: self.giveEnchant(self, "Rush", source=FirstBladeofWrynn)
		
	
class HighlordFordragon(Minion):
	Class, race, name = "Paladin", "", "Highlord Fordragon"
	mana, attack, health = 6, 5, 5
	name_CN = "大领主弗塔根"
	numTargets, Effects, description = 0, "Divine Shield", "Divine Shield. After a friendly minion loses Divine Shield, give a minion in your hand +5/+5"
	index = "Legendary"
	trigBoard = Trig_HighlordFordragon
	
	
class CalloftheGrave(Spell):
	Class, school, name = "Priest", "Shadow", "Call of the Grave"
	numTargets, mana, Effects = 0, 1, ""
	description = "Discover a Deathrattle minion. If you have enough Mana to play it, trigger its Deathrattle"
	name_CN = "墓园召唤"
	poolIdentifier = "Deathrattle Minions as Priest"
	@classmethod
	def generatePool(cls, pools):
		return genPool_CertainMinionsasClass(pools, "Deathrattle", cond=lambda card: card.deathrattle)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		card, _ = self.discoverNew(comment, lambda : self.rngPool("Deathrattle Minions as " + class4Discover(self)))
		if card and type(card).mana <= self.Game.Manas.manas[self.ID]:
			for trig in card.deathrattles: trig.trig("TrigDeathrattle", self.ID, None, card)
		
	
class XyrellatheSanctified(Minion):
	Class, race, name = "Priest", "", "Xyrella, the Sanctified"
	mana, attack, health = 5, 7, 7
	name_CN = "圣徒泽瑞拉"
	numTargets, Effects, description = 0, "", "Battlecry: Shuffle the Purifid Shard into your deck"
	index = "Battlecry~Legendary~Uncollectible"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.shuffleintoDeck(PurifiedShard(self.Game, self.ID))
		
	
class IlluminatetheVoid(Quest):
	Class, name = "Priest", "Illuminate the Void"
	numTargets, mana, Effects = 0, -1, ""
	name_CN = "照亮虚空"
	description = "Questline: Play a 7, and 8-Cost card. Reward: Xyrella, the Sanctified"
	index = "Legendary~Uncollectible"
	numNeeded, newQuest, reward = 2, None, XyrellatheSanctified
	race, trigBoard = "Questline", Trig_IlluminatetheVoid
	def text(self): return SeekGuidance.getProgress(self, Trig_IlluminatetheVoid, (7, 8))

	
class DiscovertheVoidShard(Quest):
	Class, name = "Priest", "Discover the Void Shard"
	numTargets, mana, Effects = 0, -1, ""
	name_CN = "发现虚空碎片"
	description = "Questline: Play a 5, and 6-Cost card. Reward: Discover a card from your deck"
	index = "Legendary~Uncollectible"
	numNeeded, newQuest, reward = 2, IlluminatetheVoid, None
	race, trigBoard = "Questline", Trig_DiscovertheVoidShard
	def questEffect(self, game, ID):
		card, i = self.discoverfrom('')
		if i > -1: self.Game.Hand_Deck.drawCard(self.ID, i)
		
	def text(self): return SeekGuidance.getProgress(self, Trig_DiscovertheVoidShard, (5, 6))
		
	
class SeekGuidance(Quest):
	Class, name = "Priest", "Seek Guidance"
	numTargets, mana, Effects = 0, 1, ""
	name_CN = "寻求指引"
	description = "Questline: Play a 2, 3, and 4-Cost card. Reward: Discover a card from your deck"
	index = "Legendary"
	numNeeded, newQuest, reward = 3, DiscovertheVoidShard, None
	race, trigBoard = "Questline", Trig_SeekGuidance
	@classmethod
	def getProgress(cls, quest, typTrig, costs):
		if not quest.inHand and "CardBeenPlayed" in (trigs := quest.Game.trigsBoard[quest.ID]):
			if trig := next((trig for trig in trigs if isinstance(trig, typTrig)), None):
				s = ""
				for cost in costs: s += "\n%d: %d"%(cost, cost in trig.memory + 0)
				return s.strip("\n")
		return ""

	def questEffect(self, game, ID):
		_, i = self.discoverfrom('')
		if i > -1: self.Game.Hand_Deck.drawCard(self.ID, i)
		
	def text(self): return SeekGuidance.getProgress(self, Trig_SeekGuidance, (2, 3, 4))
		
	
class PurifiedShard(Spell):
	Class, school, name = "Priest", "Holy", "Purified Shard"
	numTargets, mana, Effects = 0, 1, ""
	name_CN = "净化的碎片"
	description = "Destroy the enemy hero"
	index = "Legendary~Uncollectible"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.Game.kill(self, self.Game.heroes[3 - self.ID])
		
	
class ShardoftheNaaru(Spell):
	Class, school, name = "Priest", "Holy", "Shard of the Naaru"
	numTargets, mana, Effects = 0, 1, ""
	description = "Tradeable. Silence all enemy minions"
	name_CN = "纳鲁碎片"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for minion in self.Game.minionsonBoard(3-self.ID):
			minion.getsSilenced()
		
	
class VoidtouchedAttendant(Minion):
	Class, race, name = "Priest", "", "Voidtouched Attendant"
	mana, attack, health = 1, 1, 3
	numTargets, Effects, description = 0, "", "Both heroes take one extra damage from all source"
	name_CN = "虚触侍从"
	trigBoard = Trig_VoidtouchedAttendant
	
	
class ShadowclothNeedle(Weapon):
	Class, name, description = "Priest", "Shadowcloth Needle", "After you cast a Shadow spell, deal 1 damage to all enemies. Lose 1 Durability"
	mana, attack, durability, Effects = 2, 0, 3, ""
	name_CN = "暗影布缝针"
	trigBoard = Trig_ShadowclothNeedle
	
	
class TwilightDeceptor(Minion):
	Class, race, name = "Priest", "", "Twilight Deceptor"
	mana, attack, health = 2, 2, 3
	name_CN = "暮光欺诈者"
	numTargets, Effects, description = 0, "", "Battlecry: If any hero took damage this turn, draw a Shadow spell"
	index = "Battlecry"
	def effCanTrig(self):
		turnInd = self.Game.turnInd
		self.effectViable = self.Game.Counters.examDmgonHero(1, turnInd=turnInd) or self.Game.Counters.examDmgonHero(2, turnInd=turnInd)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		turnInd = self.Game.turnInd
		if self.Game.Counters.examDmgonHero(1, turnInd=turnInd) or self.Game.Counters.examDmgonHero(2, turnInd=turnInd):
			self.drawCertainCard(lambda card: card.school == "Shadow")
		
	
class Psyfiend(Minion):
	Class, race, name = "Priest", "", "Psyfiend"
	mana, attack, health = 3, 3, 4
	numTargets, Effects, description = 0, "", "After you cast a Shadow spell, dead 2 damage to each hero"
	name_CN = "灵能魔"
	trigBoard = Trig_Psyfiend
	
	
class VoidShard(Spell):
	Class, school, name = "Priest", "Shadow", "Void Shard"
	numTargets, mana, Effects = 1, 4, "Lifesteal"
	description = "Lifesteal. Deal 4 damage"
	name_CN = "虚空碎片"
	def text(self): return self.calcDamage(4)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(target, self.calcDamage(4))
		
	
class DarkbishopBenedictus(Minion):
	Class, race, name = "Priest", "", "Darkbishop Benedictus"
	mana, attack, health = 5, 5, 6
	name_CN = "黑暗主教本尼迪塔斯"
	numTargets, Effects, description = 0, "", "Start of Game: If the spells in your deck are all Shadow, enter Shadowform"
	index = "Legendary"
	def startofGame(self):
		#all([]) returns True
		print("Darkbishop test", all(card.school == "Shadow" for card in self.Game.Hand_Deck.initialDecks[self.ID] if card.category == "Spell"))
		if all(card.school == "Shadow" for card in self.Game.Hand_Deck.initialDecks[self.ID] if card.category == "Spell"):
			MindSpike(self.Game, self.ID).replacePower()
		
	
class ElekkMount(Spell):
	Class, school, name = "Priest", "", "Elekk Mount"
	numTargets, mana, Effects = 1, 7, ""
	description = "Give a minion +4/+7 and Taunt. When it dies, summon an Elekk"
	name_CN = "雷象坐骑"
	trigEffect = Death_ElekkMount
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(target, 4, 7, effGain="Taunt", source=ElekkMount, trig=Death_ElekkMount, trigType="Deathrattle")
		
	
class XyrellasElekk(Minion):
	Class, race, name = "Priest", "Beast", "Xyrella's Elekk"
	mana, attack, health = 6, 4, 7
	name_CN = "泽瑞拉的雷象"
	numTargets, Effects, description = 0, "Taunt", "Taunt"
	index = "Uncollectible"
	
	
class FizzflashDistractor(Spell):
	Class, school, name = "Rogue", "", "Fizzflash Distractor"
	numTargets, mana, Effects = 1, 1, ""
	name_CN = "声光干扰器"
	description = "Return a minion to its owner's hand. They can't play it next turn"
	index = "Uncollectible"
	def available(self):
		return self.selectableMinionExists(3 - self.ID)
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard and obj.ID != self.ID
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for obj in target: self.Game.returnObj2Hand(self, obj)
		self.giveEnchant(target, effectEnchant=Enchantment(FizzflashDistractor, effGain="Unplayable", until=3-self.ID+2))
		
	
class Spyomatic(Minion):
	Class, race, name = "Rogue", "Mech", "Spy-o-matic"
	mana, attack, health = 1, 3, 2
	name_CN = "间谍机器人"
	numTargets, Effects, description = 0, "", "Battlecry: Look at 3 cards in your opponent's deck. Choose one to put on top"
	index = "Battlecry~Uncollectible"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		deck = self.Game.Hand_Deck.decks[3-self.ID]
		_, i = self.discoverfrom(comment, ls=deck)
		if i > -1: deck.append(deck.pop(i))
		
	
class NoggenFogGenerator(Spell):
	Class, school, name = "Rogue", "", "Noggen-Fog Generator"
	numTargets, mana, Effects = 1, 1, ""
	name_CN = "迷雾发生器"
	description = "Give a minion +2 Attack and Stealth"
	index = "Uncollectible"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(target, 2, 0, effGain="Stealth", source=NoggenFogGenerator)
		
	
class HiddenGyroblade(Weapon):
	Class, name, description = "Rogue", "Hidden Gyroblade", "Deathrattle: Throw this at a random enemy minion"
	mana, attack, durability, Effects = 1, 3, 2, ""
	name_CN = "隐蔽式旋刃"
	index = "Uncollectible"
	deathrattle = Death_HiddenGyroblade
	
	
class UndercoverMole(Minion):
	Class, race, name = "Rogue", "Beast", "Undercover Mole"
	mana, attack, health = 1, 2, 3
	name_CN = "潜藏的鼹鼠"
	numTargets, Effects, description = 0, "Stealth", "Stealth. After this attacks, add a random card to your hand. (From your opponent's class)"
	index = "Uncollectible"
	trigBoard = Trig_UndercoverMole
	
	
class SpymasterScabbs(Minion):
	Class, race, name = "Rogue", "", "Spymaster Scabbs"
	mana, attack, health = 1, 7, 7
	name_CN = "间谍大师卡布斯"
	numTargets, Effects, description = 0, "", "Battlecry: Add one of each Spy Gizmo to your hand"
	index = "Battlecry~Legendary~Uncollectible"
	spyGizmos = (FizzflashDistractor, Spyomatic, NoggenFogGenerator, HiddenGyroblade, UndercoverMole)
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.addCardtoHand(SpymasterScabbs.spyGizmos, self.ID)
		
	
class MarkedaTraitor(Quest):
	Class, name = "Rogue", "Marked a Traitor"
	numTargets, mana, Effects = 0, -1, ""
	name_CN = "标出叛徒"
	description = "Questline: Play 2 SI:7 cards. Reward: Spymaster Scabbs"
	index = "Legendary~Uncollectible"
	numNeeded, newQuest, reward = 2, None, SpymasterScabbs
	race, trigBoard = "Questline", Trig_FindtheImposter
	
	
class LearntheTruth(Quest):
	Class, name = "Rogue", "Learn the Truth"
	numTargets, mana, Effects = 0, -1, ""
	name_CN = "了解真相"
	description = "Questline: Play 2 SI:7 cards. Reward: Add a Spy Gizmo to your hand"
	index = "Legendary~Uncollectible"
	numNeeded, newQuest, reward = 2, MarkedaTraitor, None
	race, trigBoard = "Questline", Trig_FindtheImposter
	def questEffect(self, game, ID):
		self.addCardtoHand(numpyChoice(SpymasterScabbs.spyGizmos), ID)
		
	
class FindtheImposter(Quest):
	Class, name = "Rogue", "Find the Imposter"
	numTargets, mana, Effects = 0, 1, ""
	name_CN = "探查内鬼"
	description = "Questline: Play 2 SI:7 cards. Reward: Add a Spy Gizmo to your hand"
	index = "Legendary"
	numNeeded, newQuest, reward = 2, LearntheTruth, None
	race, trigBoard = "Questline", Trig_FindtheImposter
	def questEffect(self, game, ID):
		self.addCardtoHand(numpyChoice(SpymasterScabbs.spyGizmos), ID)
		
	
class SI7Extortion(Spell):
	Class, school, name = "Rogue", "", "SI:7 Extortion"
	numTargets, mana, Effects = 1, 1, ""
	description = "Tradeable. Deal 3 damage to an undamage character"
	name_CN = "军情七处的要挟"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category in ("Minion", "Hero") and not obj.dmgTaken and obj.onBoard
		
	def text(self): return self.calcDamage(3)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(target, self.calcDamage(3))
		
	
class Garrote(Spell):
	Class, school, name = "Rogue", "", "Garrote"
	numTargets, mana, Effects = 0, 2, ""
	description = "Deal 2 damage to the enemy hero. Shuffle 3 Bleeds into your deck that deal 2 more when drawn"
	name_CN = "锁喉"
	def text(self): return self.calcDamage(2)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(self.Game.heroes[3-self.ID], self.calcDamage(2))
		self.shuffleintoDeck([Bleed(self.Game, self.ID) for _ in (0, 1, 2)])
		
	
class Bleed(Spell):
	Class, school, name = "Rogue", "", "Bleed"
	numTargets, mana, Effects = 0, 1, ""
	name_CN = "流血"
	description = "Casts When Drawn. Deal 2 damage to the enemy hero"
	index = "Uncollectible"
	def text(self): return self.calcDamage(2)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(self.Game.heroes[3-self.ID], self.calcDamage(2))
		
	
class MaestraoftheMasquerade(Minion):
	Class, race, name = "Rogue", "", "Maestra of the Masquerade"
	mana, attack, health = 2, 3, 2
	name_CN = "变装大师"
	numTargets, Effects, description = 0, "", "You start the game as different class until you play a Rogue card"
	index = "Legendary"
	
	
class CounterfeitBlade(Weapon):
	Class, name, description = "Rogue", "Counterfeit Blade", "Gain a random friendly Deathrattle that triggered this game"
	mana, attack, durability, Effects = 4, 4, 2, ""
	name_CN = "伪造的匕首"
	index = "Battlecry"
	def effCanTrig(self):
		self.effectViable = any(tup[1] == 'Deathrattle' and tup[2] == self.ID for tup in self.Game.Counters.iter_TupsSoFar("trigs"))
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if deathrattles := [tup[0] for tup in self.Game.Counters.iter_TupsSoFar("trigs") if tup[1] == 'Deathrattle' and tup[2] == self.ID]:
			self.giveEnchant(self, trig=numpyChoice(deathrattles), trigType="Deathrattle")
		
	
class LoanShark(Minion):
	Class, race, name = "Rogue", "Beast", "Loan Shark"
	mana, attack, health = 3, 3, 4
	name_CN = "放贷的鲨鱼"
	numTargets, Effects, description = 0, "", "Battlecry: Give your opponent a Coin. Deathrattle: You get two"
	index = "Battlecry"
	deathrattle = Death_LoanShark
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.addCardtoHand(TheCoin, 3-self.ID)
		
	
class SI7Operative(Minion):
	Class, race, name = "Rogue", "", "SI:7 Operative"
	mana, attack, health = 3, 2, 4
	numTargets, Effects, description = 0, "Rush", "Rush. After this minion attacks a minion, gain Stealth"
	name_CN = "军情七处探员"
	trigBoard = Trig_SI7Operative
	
	
class SketchyInformation(Spell):
	Class, school, name = "Rogue", "", "Sketchy Information"
	numTargets, mana, Effects = 0, 3, ""
	description = "Draw a Deathrattle card that costs (4) or less. Trigger its effect"
	name_CN = "简略情报"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if drawnCard := self.drawCertainCard(lambda card: hasattr(card, "deathrattles") and card.deathrattles and card.mana < 5)[0]:
			for trig in drawnCard.deathrattles: trig.trig("TrigDeathrattle", self.ID, None, drawnCard, 0, "", 0)
		
	
class SI7Informant(Minion):
	Class, race, name = "Rogue", "", "SI:7 Informant"
	mana, attack, health = 4, 3, 3
	name_CN = "军情七处线人"
	numTargets, Effects, description = 0, "", "Battlecry: Gain +1/+1 for each SI:7 card you've played this game"
	index = "Battlecry"
	@classmethod
	def examSI7Played(cls, card, veri_sum=0):
		return card.Game.Counters.examCardPlays(card.ID, veri_sum_ls=veri_sum, cond=lambda tup: "SI:7" in tup[0].name)

	def effCanTrig(self):
		self.effectViable = SI7Informant.examSI7Played(self)
		
	def text(self): return SI7Informant.examSI7Played(self)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if n := SI7Informant.examSI7Played(self): self.giveEnchant(self, n, n, source=SI7Informant)
		
	
class SI7Assassin(Minion):
	Class, race, name = "Rogue", "", "SI:7 Assassin"
	mana, attack, health = 7, 4, 4
	name_CN = "军情七处刺客"
	numTargets, Effects, description = 1, "", "Costs (1) less for each SI:7 card you've played this game. Combo: Destroy an enemy minion"
	index = "Combo"
	trigHand = Trig_SI7Assassin
	def selfManaChange(self):
		self.mana -= SI7Informant.examSI7Played(self, veri_sum=1)
		
	def numTargetsNeeded(self, choice=0):
		return 0 + self.Game.Counters.comboCounters[self.ID] > 0
		
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists(3 - self.ID)
		
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.comboCounters[self.ID] > 0
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.Game.Counters.comboCounters[self.ID]: self.Game.kill(self, target)
		
	
class StormcallerBrukan(Minion):
	Class, race, name = "Shaman", "", "Stormcaller Bru'kan"
	mana, attack, health = 5, 7, 7
	name_CN = "风暴召唤者布鲁坎"
	numTargets, Effects, description = 0, "", "Battlecry: For the rest of the game, your spells cast twice"
	index = "Battlecry~Legendary~Uncollectible"
	trigEffect = StormcallerBrukan_Effect
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.Game.rules[self.ID]["Spells x2"] += 1
		StormcallerBrukan_Effect(self.Game, self.ID).connect()
		
	
class TametheFlames(Quest):
	Class, name = "Shaman", "Tame the Flames"
	numTargets, mana, Effects = 0, -1, ""
	name_CN = "驯服火焰"
	description = "Questline: Play 3 cards with Overload. Reward: Stormcaller Bru'kan"
	index = "Legendary~Uncollectible"
	numNeeded, newQuest, reward = 3, None, StormcallerBrukan
	race, trigBoard = "Questline", Trig_CommandtheElements
	
	
class StirtheStones(Quest):
	Class, name = "Shaman", "Stir the Stones"
	numTargets, mana, Effects = 0, -1, ""
	name_CN = "搬移磐石"
	description = "Questline: Play 3 cards with Overload. Reward: Summon a 3/3 Elemental with Taunt"
	index = "Legendary~Uncollectible"
	numNeeded, newQuest, reward = 3, TametheFlames, None
	race, trigBoard = "Questline", Trig_CommandtheElements
	def questEffect(self, game, ID):
		self.summon(LivingEarth(game, ID))
		
	
class CommandtheElements(Quest):
	Class, name = "Shaman", "Command the Elements"
	numTargets, mana, Effects = 0, 1, ""
	name_CN = "号令元素"
	description = "Questline: Play 3 cards with Overload. Reward: Unlock your Overloaded Mana Crystals"
	index = "Legendary"
	numNeeded, newQuest, reward = 3, StirtheStones, None
	race, trigBoard = "Questline", Trig_CommandtheElements
	def questEffect(self, game, ID):
		game.Manas.unlockOverloadedMana(ID)
		
	
class LivingEarth(Minion):
	Class, race, name = "Shaman", "Elemental", "Living Earth"
	mana, attack, health = 3, 3, 3
	name_CN = "活体土石"
	numTargets, Effects, description = 0, "Taunt", "Taunt"
	index = "Uncollectible"
	
	
class InvestmentOpportunity(Spell):
	Class, school, name = "Shaman", "", "Investment Opportunity"
	numTargets, mana, Effects = 0, 1, ""
	description = "Draw an Overload card"
	name_CN = "投资良机"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.drawCertainCard(lambda card: type(card).overload)
		
	
class Overdraft(Spell):
	Class, school, name = "Shaman", "", "Overdraft"
	numTargets, mana, Effects = 1, 1, ""
	description = "Tradeable. Unlock your Overloaded Mana Crystals to deal that much damage"
	name_CN = "强行透支"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		damage = self.calcDamage(self.Game.Manas.manasOverloaded[self.ID] + self.Game.Manas.manasLocked[self.ID])
		self.Game.Manas.unlockOverloadedMana(self.ID)
		self.dealsDamage(target, damage)
		
	
class BolnerHammerbeak(Minion):
	Class, race, name = "Shaman", "", "Bolner Hammerbeak"
	mana, attack, health = 2, 1, 4
	name_CN = "伯纳尔·锤喙"
	numTargets, Effects, description = 0, "", "After you play a Battlecry minion, repeat the first Battlecry played this turn"
	index = "Legendary"
	trigBoard = Trig_BolnerHammerbeak	
	
	
class AuctionhouseGavel(Weapon):
	Class, name, description = "Shaman", "Auctionhouse Gavel", "After your hero attacks, reduce the Cost of a Battlecry minion in your hand by (1)"
	mana, attack, durability, Effects = 2, 2, 2, ""
	name_CN = "拍卖行木槌"
	trigBoard = Trig_AuctionhouseGavel
	
	
class ChargedCall(Spell):
	Class, school, name = "Shaman", "Nature", "Charged Call"
	numTargets, mana, Effects = 0, 3, ""
	description = "Discover a 1-Cost minion and summon it. (Upgrade it for each Overload card you played this game)"
	name_CN = "充能召唤"
	poolIdentifier = "Minions as Mage to Summon"
	@classmethod
	def generatePool(cls, pools):
		return genPool_MinionsasClasstoSummon(pools)
		
	def text(self):
		return 1 + self.Game.Counters.examCardPlays(self.ID, veri_sum_ls=1, cond=lambda tup: tup[0].overload)
		
	def decideMinionPool(self, num):
		pool = self.rngPool("Minions as %s to Summon"%class4Discover(self))
		return pickObjs_HighestAttr(pool, cond=lambda card: card.mana <= num, attr="mana")
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		num = 1 + min(10, self.Game.Counters.examCardPlays(self.ID, veri_sum_ls=1, cond=lambda tup: tup[0].overload))
		minion, _ = self.discoverNew(comment, lambda : ChargedCall.decideMinionPool(self, num), add2Hand=False)
		self.summon(minion)
		
	
class SpiritAlpha(Minion):
	Class, race, name = "Shaman", "", "Spirit Alpha"
	mana, attack, health = 4, 2, 5
	numTargets, Effects, description = 0, "", "After you play a card with Overload, summon a 2/3 Spirit Wolf with Taunt"
	name_CN = "幽灵狼前锋"
	trigBoard = Trig_SpiritAlpha
	
	
class GraniteForgeborn(Minion):
	Class, race, name = "Shaman", "Elemental", "Granite Forgeborn"
	mana, attack, health = 4, 4, 4
	name_CN = "花岗岩熔铸体"
	numTargets, Effects, description = 0, "", "Battlecry: Reduce the Cost of Elementals in your hand and deck by (1)"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for card in self.Game.Hand_Deck.hands[self.ID]:
			if card.category == "Minion" and "Elemental" in card.race:
				ManaMod(card, by=-1).applies()
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if card.category == "Minion" and "Elemental" in card.race:
				ManaMod(card, by=-1).applies()
		
	
class CanalSlogger(Minion):
	Class, race, name = "Shaman", "Elemental", "Canal Slogger"
	mana, attack, health = 4, 6, 4
	numTargets, Effects, description = 0, "Rush,Lifesteal", "Rush, Lifesteal, Overload: (1)"
	name_CN = "运河慢步者"
	overload = 1
	
	
class TinyToys(Spell):
	Class, school, name = "Shaman", "", "Tiny Toys"
	numTargets, mana, Effects = 0, 6, ""
	description = "Summon four random 5-Cost minions. Make them 2/2"
	name_CN = "小巧玩具"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		minions = [minion(self.Game, self.ID) for minion in numpyChoice(self.rngPool("5-Cost Minions to Summon"), 4, replace=True)]
		self.summon(minions)
		self.setStat([minion for minion in minions if minion.onBoard], (2, 2), source=TinyToys)
		
	
class BlightbornTamsin(Minion):
	Class, race, name = "Warlock", "", "Blightborn Tamsin"
	mana, attack, health = 5, 7, 7
	name_CN = "枯萎化身塔姆辛"
	numTargets, Effects, description = 0, "", "Battlecry: For the rest of the game, damage you take on your turns damages your opponent instead"
	index = "Battlecry~Legendary~Uncollectible"
	trigEffect = BlightbornTamsin_Effect
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		BlightbornTamsin_Effect(self.Game, self.ID).connect()
		
	
class CompletetheRitual(Quest):
	Class, name = "Warlock", "Complete the Ritual"
	numTargets, mana, Effects = 0, -1, ""
	name_CN = "完成仪式"
	description = "Questline: Take 8 damage on your turns. Reward: Blightborn Tamsin"
	index = "Legendary~Uncollectible"
	numNeeded, newQuest, reward = 8, None, BlightbornTamsin
	race, trigBoard = "Questline", Trig_TheDemonSeed
	
	
class EstablishtheLink(Quest):
	Class, name = "Warlock", "Establish the Link"
	numTargets, mana, Effects = 0, -1, "Lifesteal"
	name_CN = "建立连接"
	description = "Questline: Take 8 damage on your turns. Reward: Lifesteal. Deal 3 damage to the enemy hero"
	index = "Legendary~Uncollectible"
	numNeeded, newQuest, reward = 8, CompletetheRitual, None
	race, trigBoard = "Questline", Trig_TheDemonSeed
	def questEffect(self, game, ID):
		damage = self.calcDamage(3)
		self.dealsDamage(game.heroes[3-ID], damage)
		
	
class TheDemonSeed(Quest):
	Class, name = "Warlock", "The Demon Seed"
	numTargets, mana, Effects = 0, 1, "Lifesteal"
	name_CN = "恶魔之种"
	description = "Questline: Take 8 damage on your turns. Reward: Lifesteal. Deal 3 damage to the enemy hero"
	index = "Legendary"
	numNeeded, newQuest, reward = 8, EstablishtheLink, None
	race, trigBoard = "Questline", Trig_TheDemonSeed
	def questEffect(self, game, ID):
		damage = self.calcDamage(3)
		self.dealsDamage(game.heroes[3-ID], damage)
		
	
class TouchoftheNathrezim(Spell):
	Class, school, name = "Warlock", "Shadow", "Touch of the Nathrezim"
	numTargets, mana, Effects = 1, 1, ""
	description = "Deal 2 damage to a minion. If it dies, restore 4 Health to your hero"
	name_CN = "纳斯雷兹姆之触"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def text(self): return "%d, %d"%(self.calcDamage(2), self.calcHeal(4))
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		damage, heal = self.calcDamage(2), self.calcHeal(4)
		for obj in target:
			self.dealsDamage(obj, damage)
			if obj.health < 1 or obj.dead: self.heals(self.Game.heroes[self.ID], heal)
		
	
class BloodboundImp(Minion):
	Class, race, name = "Warlock", "Demon", "Bloodbound Imp"
	mana, attack, health = 2, 2, 5
	numTargets, Effects, description = 0, "", "Whenever this attacks, deal 2 damage to your hero"
	name_CN = "血缚小鬼"
	trigBoard = Trig_BloodboundImp
	
	
class DreadedMount(Spell):
	Class, school, name = "Warlock", "", "Dreaded Mount"
	numTargets, mana, Effects = 1, 3, ""
	description = "Give a minion +1/+1. When it dies, summon an endless Dreadsteed"
	name_CN = "恐惧坐骑"
	trigEffect = Death_TamsinsDreadsteed
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(target, 1, 1, source=DreadedMount, trig=Death_TamsinsDreadsteed, trigType="Deathrattle")
		
	
class TamsinsDreadsteed(Minion):
	Class, race, name = "Warlock", "Demon", "Tamsin's Dreadsteed"
	mana, attack, health = 4, 1, 1
	name_CN = "塔姆辛的恐惧战马"
	numTargets, Effects, description = 0, "", "Deathrattle: At the end of the turn, summon Tamsin's Dreadsteed"
	index = "Uncollectible"
	deathrattle, trigEffect = Death_TamsinsDreadsteed, TamsinsDreadsteed_Effect
	
	
class RunedMithrilRod(Weapon):
	Class, name, description = "Warlock", "Runed Mithril Rod", "After you draw 4 cards, reduce the Cost of cards in your hand by (1). Lose 1 Durability"
	mana, attack, durability, Effects = 4, 0, 2, ""
	name_CN = "符文秘银杖"
	trigBoard = Trig_RunedMithrilRod
	
	
class DarkAlleyPact(Spell):
	Class, school, name = "Warlock", "Shadow", "Dark Alley Pact"
	numTargets, mana, Effects = 0, 4, ""
	description = "Summon a Fiend with stat equal to your hand size"
	name_CN = "暗巷交易"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if size := len(self.Game.Hand_Deck.hands[self.ID]):
			minion = Fiend(self.Game, self.ID)
			minion.mana_0 = min(10, size)
			minion.attack_0 = minion.health_0 = minion.attack = minion.health = size
			self.summon(minion)
		
	
class Fiend(Minion):
	Class, race, name = "Warlock", "Demon", "Fiend"
	mana, attack, health = 1, 1, 1
	name_CN = "邪魔"
	numTargets, Effects, description = 0, "", ""
	index = "Uncollectible"
	
	
class DemonicAssault(Spell):
	Class, school, name = "Warlock", "Fel", "Demonic Assault"
	numTargets, mana, Effects = 1, 4, ""
	description = "Deal 3 damage. Summon two 1/3 Voidwalkers with Taunt"
	name_CN = "恶魔来袭"
	def text(self): return self.calcDamage(3)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(target, self.calcDamage(3))
		self.summon([Voidwalker(self.Game, self.ID) for _ in (0, 1)])
		
	
class ShadyBartender(Minion):
	Class, race, name = "Warlock", "", "Shady Bartender"
	mana, attack, health = 5, 4, 4
	name_CN = "阴暗的酒保"
	numTargets, Effects, description = 0, "", "Tradeable. Battlecry: Give your Demons +2/+2"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(self.Game.minionsonBoard(self.ID, race="Demon"), 2, 2, source=ShadyBartender)
		
	
class Anetheron(Minion):
	Class, race, name = "Warlock", "Demon", "Anetheron"
	mana, attack, health = 6, 8, 6
	name_CN = "安纳塞隆"
	numTargets, Effects, description = 0, "", "Costs (1) if your hand is full"
	index = "Legendary"
	trigHand = Trig_Anetheron
	def selfManaChange(self):
		if self.Game.Hand_Deck.spaceinHand(self.ID) < 1: self.mana = 1
		
	
class EntitledCustomer(Minion):
	Class, race, name = "Warlock", "", "Entitled Customer"
	mana, attack, health = 6, 3, 2
	name_CN = "资深顾客"
	numTargets, Effects, description = 0, "", "Battlecry: Deal damage equal to your hand size to all other minions"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if num := len(self.Game.Hand_Deck.hands[self.ID]):
			self.dealsDamage(self.Game.minionsonBoard(exclude=self), num)
		
	
class Provoke(Spell):
	Class, school, name = "Warrior", "", "Provoke"
	numTargets, mana, Effects = 1, 0, ""
	description = "Tradeable. Choose a friendly minion. Enemy minions attack it"
	name_CN = "挑衅"
	def available(self):
		return self.selectableMinionExists(self.ID)
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.ID == self.ID and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		game = self.Game
		for obj in target:
			if obj.onBoard and obj.health > 0 and not obj.dead and (minions := game.minionsAlive(3-self.ID)):
				for minion in objs_SeqSorted(minions)[0]:
					if minion.canBattle() and obj.canBattle(): game.battle(minion, obj)
		
	
class CapnRokara(Minion):
	Class, race, name = "Warrior", "Pirate", "Cap'n Rokara"
	mana, attack, health = 5, 7, 7
	name_CN = "船长洛卡拉"
	numTargets, Effects, description = 0, "", "Battlecry: Summon The Juggernaut"
	index = "Battlecry~Legendary~Uncollectible"
	poolIdentifier = "Warrior Weapons"
	@classmethod
	def generatePool(cls, pools):
		return "Warrior Weapons", [card for card in pools.ClassCards["Warrior"] if card.category == "Weapon"]
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.Game.summonSingle(TheJuggernaut(self.Game, self.ID), self.pos + 1, self)
		
	
class SecuretheSupplies(Quest):
	Class, name = "Warrior", "Secure the Supplies"
	numTargets, mana, Effects = 0, -1, ""
	name_CN = "保证补给"
	description = "Questline: Play 2 Pirates. Reward: Cap'n Rokara"
	index = "Legendary~Uncollectible"
	numNeeded, newQuest, reward = 2, None, CapnRokara
	race, trigBoard = "Questline", Trig_RaidtheDocks
	
	
class CreateaDistraction(Quest):
	Class, name = "Warrior", "Create a Distraction"
	numTargets, mana, Effects = 0, -1, ""
	name_CN = "制造混乱"
	description = "Questline: Play 2 Pirates. Reward: Deal 2 damage to a random enemy twice"
	index = "Legendary~Uncollectible"
	numNeeded, newQuest, reward = 2, SecuretheSupplies, None
	race, trigBoard = "Questline", Trig_RaidtheDocks
	def questEffect(self, game, ID):
		damage = self.calcDamage(2)
		for _ in (0, 1):
			if objs := game.charsAlive(3-ID): self.dealsDamage(numpyChoice(objs), damage)
			else: break
		
	
class RaidtheDocks(Quest):
	Class, name = "Warrior", "Raid the Docks"
	numTargets, mana, Effects = 0, 1, ""
	name_CN = "开进码头"
	description = "Questline: Play 3 Pirates. Reward: Draw a weapon"
	index = "Legendary"
	numNeeded, newQuest, reward = 3, CreateaDistraction, None
	race, trigBoard = "Questline", Trig_RaidtheDocks
	def questEffect(self, game, ID):
		self.drawCertainCard(lambda card: card.category == "Weapon")
		
	
class TheJuggernaut(Minion):
	Class, name = "Warrior", "The Juggernaut"
	description = "At the start of your turn, summon a Pirate, equip a Warrior weapon and fire two cannons that deal 2 damage!"
	index = "Legendary~Uncollectible"
	trigBoard = Trig_TheJuggernaut
	category = "Dormant"
	
	
class ShiverTheirTimbers(Spell):
	Class, school, name = "Warrior", "", "Shiver Their Timbers!"
	numTargets, mana, Effects = 1, 1, ""
	description = "Deal 2 damage to a minion. If you control a Pirate, deal 5 instead"
	name_CN = "海上威胁"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def effCanTrig(self): return 1 and self.Game.minionsonBoard(self.ID, race="Pirate")
		
	def text(self): return "%d, %d"%(self.calcDamage(2), self.calcDamage(5))
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(target, self.calcDamage(5 if self.Game.minionsonBoard(self.ID, race="Pirate") else 2))
		
	
class HarborScamp(Minion):
	Class, race, name = "Warrior", "Pirate", "Harbor Scamp"
	mana, attack, health = 2, 2, 2
	name_CN = "港口匪徒"
	numTargets, Effects, description = 0, "", "Battlecry: Draw a Pirate"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.drawCertainCard(lambda card: "Pirate" in card.race)
		
	
class CargoGuard(Minion):
	Class, race, name = "Warrior", "Pirate", "Cargo Guard"
	mana, attack, health = 3, 2, 4
	numTargets, Effects, description = 0, "", "At the end of your turn, gain 3 Armor"
	name_CN = "货物保镖"
	trigBoard = Trig_CargoGuard
	
	
class HeavyPlate(Spell):
	Class, school, name = "Warrior", "", "Heavy Plate"
	numTargets, mana, Effects = 0, 3, ""
	description = "Tredeable. Gain 8 Armor"
	name_CN = "厚重板甲"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveHeroAttackArmor(self.ID, armor=8)
		
	
class StormwindFreebooter(Minion):
	Class, race, name = "Warrior", "Pirate", "Stormwind Freebooter"
	mana, attack, health = 3, 3, 4
	name_CN = "暴风城海盗"
	numTargets, Effects, description = 0, "", "Battlecry: Give your hero +2 Attack this turn"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveHeroAttackArmor(self.ID, attGain=2, source=StormwindFreebooter)
		
	
class RemoteControlledGolem(Minion):
	Class, race, name = "Warrior", "Mech", "Remote-Controlled Golem"
	mana, attack, health = 4, 3, 6
	numTargets, Effects, description = 0, "", "After this minion takes damage, shuffle two Golem Parts into your deck. When drawn, summon a 2/1 Mech"
	name_CN = "遥控傀儡"
	trigBoard = Trig_RemoteControlledGolem
	
	
class GolemParts(Spell):
	Class, school, name = "Warrior", "", "Golem Parts"
	numTargets, mana, Effects = 0, 1, ""
	name_CN = "傀儡部件"
	description = "Casts When Drawn. Summon a 2/1 Mech"
	index = "Uncollectible"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon(DamagedGolem(self.Game, self.ID))
		
	
class CowardlyGrunt(Minion):
	Class, race, name = "Warrior", "", "Cowardly Grunt"
	mana, attack, health = 6, 6, 2
	numTargets, Effects, description = 0, "", "Deathrattle: Summon a minion from your deck"
	name_CN = "怯懦的步兵"
	deathrattle = Death_CowardlyGrunt
	
	
class Lothar(Minion):
	Class, race, name = "Warrior", "", "Lothar"
	mana, attack, health = 7, 7, 7
	name_CN = "洛萨"
	numTargets, Effects, description = 0, "", "At the end of your turn, attack a random enemy minion. If it dies, gain +3/+3"
	index = "Legendary"
	trigBoard = Trig_Lothar
	
	
class GolakkaGlutton(Minion):
	Class, race, name = "Neutral", "Pirate", "Golakka Glutton"
	mana, attack, health = 3, 2, 3
	name_CN = "葛拉卡蟹杀手"
	numTargets, Effects, description = 1, "", "Battlecry: Destroy a Beast and gain +1/+1"
	index = "Battlecry"
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def effCanTrig(self):
		self.effectViable = self.targetExists()
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.Game.kill(self, target)
		self.giveEnchant(self, n := len(target), n, source=GolakkaGlutton)
		
	
class Multicaster(Minion):
	Class, race, name = "Neutral", "Pirate", "Multicaster"
	mana, attack, health = 4, 3, 4
	name_CN = "多系施法者"
	numTargets, Effects, description = 0, "", "Battlecry: Draw a card for each different spell school you've cast this game"
	index = "Battlecry"
	def text(self): return len(set(school for tup in self.Game.Counters.iter_CardPlaysSoFar(self.ID) if (school := tup[0].school)))
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for _ in set(school for tup in self.Game.Counters.iter_CardPlaysSoFar(self.ID) if (school := tup[0].school)):
			self.Game.Hand_Deck.drawCard(self.ID)
		
	
class MrSmite(Minion):
	Class, race, name = "Neutral", "Pirate", "Mr. Smite"
	mana, attack, health = 6, 6, 5
	name_CN = "重拳先生"
	numTargets, Effects, description = 0, "", "Your Pirates have Charge"
	index = "Legendary"
	aura = Aura_MrSmite
	
	
class GoliathSneedsMasterpiece(Minion):
	Class, race, name = "Neutral", "Mech", "Goliath, Sneed's Masterpiece"
	mana, attack, health = 8, 8, 8
	name_CN = "哥利亚，斯德尼的杰作"
	numTargets, Effects, description = 0, "", "Battlecry: Fire five rockets at enemy minions that deal 2 damage each. (You pick the targets!)"
	index = "Battlecry~Legendary"
	def targetCorrect(self, obj, choice=0, ith=0):
		#尽管随从自身不需要指向目标，但是需要targetCorrect，从而正确地选择场上的随从
		return obj.ID != self.ID and obj.category == "Minion" and obj.onBoard and obj.health > 0 and not obj.dead
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for _ in (0, 1, 2, 3, 4):
			if minions := GoliathSneedsMasterpiece.findTargets(self):
				card = self.choosefromBoard(comment, ls=minions)
				self.dealsDamage(card, 2)
			else: break
		
	
class MaddestBomber(Minion):
	Class, race, name = "Neutral", "", "Maddest Bomber"
	mana, attack, health = 8, 9, 8
	name_CN = "最疯狂的爆破者"
	numTargets, Effects, description = 0, "", "Battlecry: Deal 12 damage randomly split among all other characters"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for _ in range(12):
			if chars := self.Game.charsAlive(exclude=self): self.dealsDamage(numpyChoice(chars), 1)
			else: break
		
	
class CrowsNestLookout(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Crow's Nest Lookout"
	mana, attack, health = 3, 2, 2
	name_CN = "鸦巢观察员"
	numTargets, Effects, description = 0, "", "Battlecry: Deal 2 damage to the left and right-most enemy minions"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if minions := self.Game.minionsonBoard(3-self.ID): self.dealsDamage([minions[0], minions[-1]], [2, 2])
		
	
class NeedforGreed(Spell):
	Class, school, name = "Demon Hunter", "", "Need for Greed"
	numTargets, mana, Effects = 0, 5, ""
	description = "Tradeable. Draw 3 cards. If drawn this turn, this costs (3)"
	name_CN = "贪婪需求"
	def effCanTrig(self):
		self.effectViable = self.enterHandTurn >= self.Game.turnInd
		
	def selfManaChange(self):
		if self.enterHandTurn >= self.Game.turnInd:
			self.mana = 3
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for _ in (0, 1, 2): self.Game.Hand_Deck.drawCard(self.ID)
		
	
class ProvingGrounds(Spell):
	Class, school, name = "Demon Hunter", "", "Proving Grounds"
	numTargets, mana, Effects = 0, 6, ""
	description = "Summon two minions from your deck. They fight"
	name_CN = "试炼场"
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if (minion1 := self.try_SummonfromOwn()) and (minion2 := self.try_SummonfromOwn()):
			if minion1.canBattle() and minion2.canBattle():
				self.Game.battle(minion1, minion2)
		
	
class SharkForm_Option(Option):
	name, category, description = "Shark Form", "Option_Minion", "Rush"
	mana, attack, health = 1, 3, 1
	
	
class SeaTurtleForm_Option(Option):
	name, category, description = "Sea Turtle Form", "Option_Minion", "Taunt"
	mana, attack, health = 1, 1, 3
	
	
class DruidoftheReef(Minion):
	Class, race, name = "Druid", "", "Druid of the Reef"
	mana, attack, health = 1, 1, 1
	numTargets, Effects, description = 0, "", "Choose One - Transform into a 3/1 Shark with Rush; or a 1/3 Turtle with Taunt"
	name_CN = "暗礁德鲁伊"
	options = (SharkForm_Option, SeaTurtleForm_Option)
	def appears_fromPlay(self, choice):
		return appears_fromPlay_Druid(self, choice, (DruidoftheReef_Rush, DruidoftheReef_Taunt, DruidoftheReef_Both))
		
	
class DruidoftheReef_Rush(Minion):
	Class, race, name = "Druid", "Beast", "Druid of the Reef"
	mana, attack, health = 1, 3, 1
	name_CN = "暗礁德鲁伊"
	numTargets, Effects, description = 0, "Rush", "Rush"
	index = "Uncollectible"
	
	
class DruidoftheReef_Taunt(Minion):
	Class, race, name = "Druid", "Beast", "Druid of the Reef"
	mana, attack, health = 1, 1, 3
	name_CN = "暗礁德鲁伊"
	numTargets, Effects, description = 0, "Taunt", "Taunt"
	index = "Uncollectible"
	
	
class DruidoftheReef_Both(Minion):
	Class, race, name = "Druid", "Beast", "Druid of the Reef"
	mana, attack, health = 1, 3, 3
	name_CN = "暗礁德鲁伊"
	numTargets, Effects, description = 0, "Rush,Taunt", "Rush, Taunt"
	index = "Uncollectible"
	
	
class JerryRigCarpenter(Minion):
	Class, race, name = "Druid", "Pirate", "Jerry Rig Carpenter"
	mana, attack, health = 2, 2, 1
	name_CN = "应急木工"
	numTargets, Effects, description = 0, "", "Battlecry: Draw a Choose One spell and split it"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		#不知道是否会保留这个初始法术的费用效果，假设不保留
		spell, mana, entersHand = self.drawCertainCard(lambda card: card.category == "Spell" and card.options)
		if entersHand:
			self.Game.Hand_Deck.extractfromHand(spell, self.ID)
			self.Game.Hand_Deck.addCardtoHand([option.spell for option in type(spell).options], self.ID)
		
	
class MoonlitGuidance(Spell):
	Class, school, name = "Druid", "Arcane", "Moonlit Guidance"
	numTargets, mana, Effects = 0, 2, ""
	description = "Discover a copy of a card in your deck. If you play it this turn, draw the original"
	name_CN = "月光指引"
	trigEffect = MoonlitGuidance_Effect
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		card, i = self.discoverfrom(comment)
		if i > -1:
			self.addCardtoHand(Copy := self.copyCard(card, self.ID), self.ID, byDiscover=True)
			if Copy.inHand and card.inDeck: MoonlitGuidance_Effect(self.Game, self.ID, (card, Copy)).connect()
		
	
class DoggieBiscuit(Spell):
	Class, school, name = "Hunter", "", "Doggie Biscuit"
	numTargets, mana, Effects = 1, 2, ""
	description = "Tradeable. Give a minion +2/+3. After you Trade this, give a friendly minion Rush"
	name_CN = "狗狗饼干"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(target, 2, 3, source=DoggieBiscuit)
		
	def tradeEffect(self):
		if minions:= self.Game.minionsonBoard(self.ID):
			self.giveEnchant(numpyChoice(minions), effGain="Rush", source=DoggieBiscuit)
		
	
class MonstrousParrot(Minion):
	Class, race, name = "Hunter", "Beast", "Monstrous Parrot"
	mana, attack, health = 4, 3, 4
	name_CN = "巨型鹦鹉"
	numTargets, Effects, description = 0, "", "Battlecry: Repeat the last friendly Deathrattle that triggered"
	index = "Battlecry"
	def effCanTrig(self):
		self.effectViable = any(tup[1] == "Deathrattle" and tup[2] == self.ID for tup in self.Game.Counters.iter_TupsSoFar("trigs"))
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if deathrattle := next((tup[0] for tup in self.Game.Counters.iter_TupsSoFar("trigs", backwards=True)
								if tup[1] == "Deathrattle" and tup[2] == self.ID), None):
			deathrattle(self).trig("TrigDeathrattle", self.ID, None, self, 0, "", 0)
		
	
class DefiasBlastfisher(Minion):
	Class, race, name = "Hunter", "Pirate", "Defias Blastfisher"
	mana, attack, health = 5, 3, 2
	name_CN = "迪菲亚炸鱼手"
	numTargets, Effects, description = 0, "", "Battlecry: Deal 2 damage to a random enemy. Repeat for each of your Beasts"
	index = "Battlecry"
	def effCanTrig(self):
		self.effectViable = 1 and self.Game.minionsonBoard(self.ID, race="Beast")
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if objs := self.Game.charsAlive(3-self.ID):
			self.dealsDamage(numpyChoice(objs), 2)
			for _ in range(len(self.Game.minionsonBoard(self.ID, race="Beast"))):
				if objs := self.Game.charsAlive(3-self.ID): self.dealsDamage(numpyChoice(objs), 2)
				else: break
		
	
class DeepwaterEvoker(Minion):
	Class, race, name = "Mage", "Pirate", "Deepwater Evoker"
	mana, attack, health = 4, 3, 4
	name_CN = "深水唤醒师"
	numTargets, Effects, description = 0, "", "Battlecry: Draw a spell. Gain Armor equal to its Cost"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if (mana := self.drawCertainCard(lambda card: card.category == "Spell")[1]) > 0:
			self.giveHeroAttackArmor(self.ID, armor=mana)
		
	
class ArcaneOverflow(Spell):
	Class, school, name = "Mage", "Arcane", "Arcane Overflow"
	numTargets, mana, Effects = 1, 5, ""
	description = "Deal 8 damage to an enemy minion. Summon a Remnant with stats equal to the excess damage"
	name_CN = "奥术溢爆"
	def available(self):
		return self.selectableMinionExists(3 - self.ID)
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.ID != self.ID and obj.onBoard
		
	def text(self): return self.calcDamage(8)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		damage = self.calcDamage(8)
		for obj in target:
			dmgExcess = damage - (dmgReal := min(damage, max(0, obj.health)))
			self.dealsDamage(obj, dmgReal)
			if dmgExcess:
				minion = ArcaneRemnant(self.Game, self.ID)
				minion.mana_0 = min(10, dmgExcess)
				minion.attack_0 = minion.health_0 = minion.attack = minion.health = dmgExcess
				self.summon(minion)
		
	
class ArcaneRemnant(Minion):
	Class, race, name = "Mage", "Elemental", "Arcane Remnant"
	mana, attack, health = 1, 1, 1
	name_CN = "奥术残渣"
	numTargets, Effects, description = 0, "", ""
	index = "Uncollectible"
	
	
class GreySageParrot(Minion):
	Class, race, name = "Mage", "Beast", "Grey Sage Parrot"
	mana, attack, health = 8, 6, 6
	name_CN = "灰贤鹦鹉"
	numTargets, Effects, description = 0, "", "Battlecry: Repeat the last spell you've cast that costs (5) or more"
	index = "Battlecry"
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.examCardPlays(self.ID, cond=self.Game.Counters.checkTup_BigSpell)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		checkTup = self.Game.Counters.checkTup_BigSpell
		if bareInfo := next(self.Game.Counters.iter_CardPlays(self.ID, backwards=True, cond=checkTup), None):
			self.Game.fabCard(bareInfo, self.ID, self).cast()
		
	
class RighteousDefense(Spell):
	Class, school, name = "Paladin", "Holy", "Righteous Defense"
	numTargets, mana, Effects = 1, 3, ""
	description = "Set a minion's Attack and Health to 1. Give the stats it lost to a minion in your hand"
	name_CN = "正义防御"
	def available(self):
		return self.selectableMinionExists(3 - self.ID)
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for obj in target:
			attLost, healthLost = max(obj.attack - 1, 0), max(obj.health - 1, 0)
			self.setStat(obj, (1, 1), source=RighteousDefense)
			if (attLost or healthLost) and (minions := [card for card in self.Game.Hand_Deck.hands[self.ID] if card.category == "Minion"]):
				self.giveEnchant(numpyChoice(minions), attLost, healthLost, source=RighteousDefense)
		
	
class SunwingSquawker(Minion):
	Class, race, name = "Paladin", "Beast", "Sunwing Squawker"
	mana, attack, health = 4, 3, 4
	name_CN = "金翼鹦鹉"
	numTargets, Effects, description = 0, "", "Battlecry: Repeat the last spell you've cast on a friendly minion on this"
	index = "Battlecry"
	def effCanTrig(self):
		self.effectViable = any(self.Game.Counters.iter_SpellsonFriendly(self.ID, minionsOnly=True))

	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if tup := next(self.Game.Counters.iter_SpellsonFriendly(self.ID, backwards=True, minionsOnly=True), None):
			self.Game.fabCard(tup[:2], self.ID, self).cast(target=self)
		
	
class WealthRedistributor(Minion):
	Class, race, name = "Paladin", "Pirate", "Wealth Redistributor"
	mana, attack, health = 5, 2, 8
	name_CN = "分赃专员"
	numTargets, Effects, description = 0, "Taunt", "Taunt. Battlecry: Swap the Attack of the highest and losest Attack minion"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if minions := self.Game.minionsonBoard():
			minions_Highest, minions_Lowest, highest, lowest = [], [], -numpy.inf, numpy.inf
			for minion in minions:
				att = minion.attack
				if att > highest: minions_Highest, highest = [minion], att
				elif att == highest: minions_Highest.append(minion)
				if att < lowest: minions_Lowest, lowest = [minion], att
				elif att == lowest: minions_Lowest.append(minion)
			self.setStat(numpyChoice(minions_Highest), (lowest, None), source=WealthRedistributor)
			self.setStat(numpyChoice(minions_Lowest), (highest, None), source=WealthRedistributor)
		
	
class DefiasLeper(Minion):
	Class, race, name = "Priest", "Pirate", "Defias Leper"
	mana, attack, health = 2, 3, 2
	name_CN = "迪菲亚麻风侏儒"
	numTargets, Effects, description = 1, "", "Battlecry: If you're holding a Shadow spell, deal 2 damage"
	index = "Battlecry"
	def numTargetsNeeded(self, choice=0):
		return 1 if any(card.school == "Shadow" for card in self.Game.Hand_Deck.hands[self.ID]) else 0
		
	def effCanTrig(self):
		self.effectViable = any(card.school == "Shadow" for card in self.Game.Hand_Deck.hands[self.ID])
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if any(card.school == "Shadow" for card in self.Game.Hand_Deck.hands[self.ID]):
			self.dealsDamage(target, 2)
		
	
class AmuletofUndying(Spell):
	Class, school, name = "Priest", "Shadow", "Amulet of Undying"
	numTargets, mana, Effects = 0, 3, ""
	description = "Tradeable. Resurrect 1 friendly Deathrattle minion. (Upgrades when Traded!)"
	name_CN = "不朽护符"
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def text(self): return self.progress + 1
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if tups := self.Game.Counters.examDeads(self.ID, veri_sum_ls=2, cond=lambda card: card.deathrattle):
			tups = numpyChoice(tups, min(len(tups), self.progress+1), replace=False)
			self.summon([self.Game.fabCard(tup, self.ID, self) for tup in tups])
		
	def tradeEffect(self):
		self.progress += 1
		
	
class Copycat(Minion):
	Class, race, name = "Priest", "Beast", "Copycat"
	mana, attack, health = 3, 3, 4
	name_CN = "仿冒猫猫"
	numTargets, Effects, description = 0, "", "Battlecry: Add a copy of the next card your opponent plays to your hand"
	index = "Battlecry"
	trigEffect = Copycat_Effect
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		Copycat_Effect(self.Game, self.ID).connect()
		
	
class BlackwaterCutlass(Weapon):
	Class, name, description = "Rogue", "Blackwater Cutlass", "Tradeable. After you Trade this, reduce the cost of a spell in your hand by (1)"
	mana, attack, durability, Effects = 1, 2, 2, ""
	name_CN = "黑水弯刀"
	def tradeEffect(self):
		if cards := self.findCards2ReduceMana(lambda card: card.category == "Spell"):
			ManaMod(numpyChoice(cards), by=-1).applies()
		
	
class Parrrley(Spell):
	Class, school, name = "Rogue", "", "Parrrley"
	numTargets, mana, Effects = 0, 1, ""
	description = "Swap this for a card in your opponent's deck"
	name_CN = "海盗谈判"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if enemyDeck := self.Game.Hand_Deck.decks[3-self.ID]:
			#Enemy can see what card is taken away
			card = self.Game.Hand_Deck.extractfromDeck((i := numpyRandint(len(enemyDeck))), 3 - self.ID, linger=True)
			self.Game.Hand_Deck.addCardtoHand(card, self.ID)
			self.reset(3 - self.ID)
			enemyDeck[i] = self
			self.entersDeck()
		
	
class EdwinDefiasKingpin(Minion):
	Class, race, name = "Rogue", "Pirate", "Edwin, Defias Kingpin"
	mana, attack, health = 4, 4, 4
	name_CN = "艾德温，迪菲亚首脑"
	numTargets, Effects, description = 0, "", "Battlecry: Draw a card. If you play it this turn, gain +2/+2 and repeat this effect"
	index = "Battlecry~Legendary"
	trigEffect = Trig_EdwinDefiasKingpin
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		card, mana, entersHand = self.Game.Hand_Deck.drawCard(self.ID)
		if entersHand and card.inHand and self.onBoard:
			self.getsTrig(Trig_EdwinDefiasKingpin(self, card))
		
	
class BrilliantMacaw(Minion):
	Class, race, name = "Shaman", "Beast", "Brilliant Macaw"
	mana, attack, health = 3, 3, 3
	name_CN = "艳丽的金刚鹦鹉"
	numTargets, Effects, description = 0, "", "Battlecry: Repeat the last Battlecry you played"
	index = "Battlecry"
	@classmethod
	def checkTup_Battlecry(cls, tup):
		return "~Battlecry" in (card := tup[0]).index and card is not BrilliantMacaw

	def effCanTrig(self):
		self.effectViable = self.Game.Counters.examCardPlays(self.ID, cond=BrilliantMacaw.checkTup_Battlecry)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		#鹦鹉的战吼在寻找时，会跳过鹦鹉的战吼而寻找上一个战吼。
		if tup := next(self.Game.Counters.iter_CardPlays(self.ID, backwards=True, cond=BrilliantMacaw.checkTup_Battlecry), None):
			self.invokeBattlecry(tup[0])
		
	
class CookietheCook(Minion):
	Class, race, name = "Shaman", "Murloc", "Cookie the Cook"
	mana, attack, health = 3, 2, 3
	name_CN = "厨师曲奇"
	numTargets, Effects, description = 0, "Lifesteal", "Lifesteal. Deathrattle: Equip a 2/3 Stirring Rod with Lifesteal"
	index = "Legendary"
	deathrattle = Death_CookietheCook
	
	
class CookiesStirringRod(Weapon):
	Class, name, description = "Shaman", "Cookie's Stirring Rod", "Lifesteal"
	mana, attack, durability, Effects = 3, 2, 3, "Lifesteal"
	name_CN = "曲奇的搅汤棒"
	index = "Legendary~Uncollectible"
	
	
class Suckerhook(Minion):
	Class, race, name = "Shaman", "Pirate", "Suckerhook"
	mana, attack, health = 4, 3, 6
	numTargets, Effects, description = 0, "", "At the end of your turn, transform your weapon into one that costs (1) more"
	name_CN = "吸盘钩手"
	trigBoard = Trig_Suckerhook
	
	
class ShadowbladeSlinger(Minion):
	Class, race, name = "Warlock", "Pirate", "Shadowblade Slinger"
	mana, attack, health = 1, 2, 1
	name_CN = "暗影之刃飞刀手"
	numTargets, Effects, description = 1, "", "Battlecry: If you've taken damage this turn, deal that much to an enemy minion"
	index = "Battlecry"
	def numTargetsNeeded(self, choice=0):
		return 1 if self.Game.Counters.examDmgonHero(self.ID, turnInd=self.Game.turnInd) else 0
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.ID != self.ID and obj.onBoard
		
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.examDmgonHero(self.ID, turnInd=self.Game.turnInd)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if dmg := self.Game.Counters.examDmgonHero(self.ID, turnInd=self.Game.turnInd, veri_sum=1):
			self.dealsDamage(target, dmg)
		
	
class WickedShipment(Spell):
	Class, school, name = "Warlock", "", "Wicked Shipment"
	numTargets, mana, Effects = 0, 1, ""
	description = "Tradeable. Summon 2 1/1 Imps. (Upgrades by 2 when Traded!)"
	name_CN = "邪恶船运"
	def text(self): return 2 + self.progress
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon([Imp(self.Game, self.ID) for _ in range(2 + self.progress)])
		
	def tradeEffect(self):
		self.progress += 2
		
	
class Hullbreaker(Minion):
	Class, race, name = "Warlock", "Demon", "Hullbreaker"
	mana, attack, health = 4, 4, 3
	name_CN = "碎舰恶魔"
	numTargets, Effects, description = 0, "", "Battlecry and Deathrattle: Draw a spell. Your hero takes damage equal to its Cost"
	index = "Battlecry"
	deathrattle = Death_Hullbreaker
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if (mana := self.drawCertainCard(lambda card: card.category == "Spell")[1]) > 0:
			self.Game.heroTakesDamage(self.ID, mana)
		
	
class MantheCannons(Spell):
	Class, school, name = "Warrior", "", "Man the Cannons"
	numTargets, mana, Effects = 1, 2, ""
	description = "Deal 3 damage to a minion and 1 damage to all other minions"
	name_CN = "操纵火炮"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def text(self): return "%d, %d"%(self.calcDamage(3), self.calcDamage(1))
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		dmg_3, dmg_1 = self.calcDamage(3), self.calcDamage(1)
		for obj in target:
			minions = [obj] + self.Game.minionsonBoard(exclude=obj)
			self.dealsDamage(minions, [self.calcDamage(3)]+[self.calcDamage(1)]*(len(minions)-1))
		
	
class DefiasCannoneer(Minion):
	Class, race, name = "Warrior", "Pirate", "Defias Cannoneer"
	mana, attack, health = 3, 3, 3
	numTargets, Effects, description = 0, "", "After your hero attacks, deal 2 damage to a random enemy twice"
	name_CN = "迪菲亚炮手"
	trigBoard = Trig_DefiasCannoneer
	
	
class BlacksmithingHammer(Weapon):
	Class, name, description = "Warrior", "Blacksmithing Hammer", "Tradeable. After you Trade this, gain +2 Durability"
	mana, attack, durability, Effects = 4, 5, 1, ""
	name_CN = "铁匠锤"
	def tradeEffect(self):
		self.getsBuffDebuff_inDeck(0, 2, source=BlacksmithingHammer)
		
	


AllClasses_Stormwind = [
	GameRuleAura_AuctioneerJaxon, Aura_BattlegroundBattlemaster, Aura_MrSmite, Trig_SwordofaThousandTruth, Trig_Peasant,
	Trig_Florist, Trig_StockadesPrisoner, Trig_EnthusiasticBanker, Trig_TwoFacedInvestor, Trig_FlightmasterDungar_Westfall,
	Trig_FlightmasterDungar_Ironforge, Trig_FlightmasterDungar_EasternPlaguelands, Trig_Cheesemonger, Trig_CorneliusRoame,
	Trig_GoldshireGnoll, Trig_FinalShowdown, Trig_LionsFrenzy, Trig_IreboundBrute, Trig_LostinthePark, Trig_Wickerclaw,
	Trig_OracleofElune, Trig_ParkPanther, Trig_DefendtheDwarvenDistrict, Trig_LeatherworkingKit, Trig_TavishsRam,
	Trig_StormwindPiper, Trig_DormantRatKing, Trig_SorcerersGambit, Trig_CelestialInkSet, Trig_SanctumChandler, Trig_PrismaticJewelKit,
	Trig_RisetotheOccasion, Trig_HighlordFordragon, Trig_SeekGuidance, Trig_DiscovertheVoidShard, Trig_IlluminatetheVoid,
	Trig_VoidtouchedAttendant, Trig_ShadowclothNeedle, Trig_Psyfiend, Trig_UndercoverMole, Trig_FindtheImposter, Trig_SI7Operative,
	Trig_SI7Assassin, Trig_CommandtheElements, Trig_BolnerHammerbeak, Trig_AuctionhouseGavel, Trig_SpiritAlpha, Trig_TheDemonSeed,
	Trig_BloodboundImp, Trig_RunedMithrilRod, Trig_Anetheron, Trig_RaidtheDocks, Trig_TheJuggernaut, Trig_CargoGuard,
	Trig_RemoteControlledGolem, Trig_Lothar, Trig_EdwinDefiasKingpin, Trig_Suckerhook, Trig_DefiasCannoneer, Death_ElwynnBoar,
	Death_MailboxDancer, Death_EnthusiasticBanker, Death_StubbornSuspect, Death_MoargForgefiend, Death_PersistentPeddler,
	Death_VibrantSquirrel, Death_Composting, Death_KodoMount, Death_RammingMount, Death_RodentNest, Death_ImportedTarantula,
	Death_TheRatKing, Death_NobleMount, Death_ElekkMount, Death_HiddenGyroblade, Death_LoanShark, Death_TamsinsDreadsteed,
	Death_CowardlyGrunt, Death_CookietheCook, Death_Hullbreaker, SigilofAlacrity_Effect, DemonslayerKurtrus_Effect,
	SheldrasMoontree_Effect, TavishMasterMarksman_Effect, AimedShot_Effect, GameManaAura_HotStreak, PrestorsPyromancer_Effect,
	ArcanistDawngrasp_Effect, GameAura_LightbornCariel, SI7Skulker_Effect, StormcallerBrukan_Effect, BlightbornTamsin_Effect,
	TamsinsDreadsteed_Effect, MoonlitGuidance_Effect, Copycat_Effect, ElwynnBoar, SwordofaThousandTruth, Peasant,
	StockadesGuard, AuctioneerJaxon, DeeprunEngineer, EncumberedPackMule, Florist, PandarenImporter, MailboxDancer,
	SI7Skulker, StockadesPrisoner, EntrappedSorceress, EnthusiasticBanker, ImpatientShopkeep, NorthshireFarmer, PackageRunner,
	RustrotViper, TravelingMerchant, TwoFacedInvestor, FlightmasterDungar, Westfall, Ironforge, EasternPlaguelands,
	Nobleman, Cheesemonger, GuildTrader, RoyalLibrarian, SpiceBreadBaker, StubbornSuspect, LionsGuard, StormwindGuard,
	BattlegroundBattlemaster, CityArchitect, CastleWall, CorneliusRoame, LadyPrestor, MoargForgefiend, VarianKingofStormwind,
	GoldshireGnoll, DemonslayerKurtrus, ClosethePortal, GainMomentum, FinalShowdown, Metamorfin, SigilofAlacrity,
	FelBarrage, ChaosLeech, LionsFrenzy, Felgorger, PersistentPeddler, IreboundBrute, JaceDarkweaver, GufftheTough,
	FeralFriendsy, DefendtheSquirrels, LostinthePark, Fertilizer, NewGrowth, Fertilizer_Option, NewGrowth_Option,
	SowtheSoil, Treant_Stormwind, VibrantSquirrel, Acorn, SatisfiedSquirrel, Composting, Wickerclaw, OracleofElune,
	KodoMount, GuffsKodo, ParkPanther, BestinShell, GoldshellTurtle, SheldrasMoontree, DevouringSwarm, TavishMasterMarksman,
	KnockEmDown, TaketheHighGround, DefendtheDwarvenDistrict, LeatherworkingKit, AimedShot, RammingMount, TavishsRam,
	StormwindPiper, RodentNest, ImportedTarantula, InvasiveSpiderling, TheRatKing, RatsofExtraordinarySize, Rat, HotStreak,
	FirstFlame, SecondFlame, ArcanistDawngrasp, ReachthePortalRoom, StallforTime, SorcerersGambit, CelestialInkSet,
	Ignite, PrestorsPyromancer, FireSale, SanctumChandler, ClumsyCourier, GrandMagusAntonidas, BlessedGoods, PrismaticJewelKit,
	LightbornCariel, AvengetheFallen, PavetheWay, RisetotheOccasion, NobleMount, CarielsWarhorse, CityTax, AllianceBannerman,
	CatacombGuard, LightbringersHammer, FirstBladeofWrynn, HighlordFordragon, CalloftheGrave, XyrellatheSanctified,
	IlluminatetheVoid, DiscovertheVoidShard, SeekGuidance, PurifiedShard, ShardoftheNaaru, VoidtouchedAttendant, ShadowclothNeedle,
	TwilightDeceptor, Psyfiend, VoidShard, DarkbishopBenedictus, ElekkMount, XyrellasElekk, FizzflashDistractor, Spyomatic,
	NoggenFogGenerator, HiddenGyroblade, UndercoverMole, SpymasterScabbs, MarkedaTraitor, LearntheTruth, FindtheImposter,
	SI7Extortion, Garrote, Bleed, MaestraoftheMasquerade, CounterfeitBlade, LoanShark, SI7Operative, SketchyInformation,
	SI7Informant, SI7Assassin, StormcallerBrukan, TametheFlames, StirtheStones, CommandtheElements, LivingEarth, InvestmentOpportunity,
	Overdraft, BolnerHammerbeak, AuctionhouseGavel, ChargedCall, SpiritAlpha, GraniteForgeborn, CanalSlogger, TinyToys,
	BlightbornTamsin, CompletetheRitual, EstablishtheLink, TheDemonSeed, TouchoftheNathrezim, BloodboundImp, DreadedMount,
	TamsinsDreadsteed, RunedMithrilRod, DarkAlleyPact, Fiend, DemonicAssault, ShadyBartender, Anetheron, EntitledCustomer,
	Provoke, CapnRokara, SecuretheSupplies, CreateaDistraction, RaidtheDocks, TheJuggernaut, ShiverTheirTimbers, HarborScamp,
	CargoGuard, HeavyPlate, StormwindFreebooter, RemoteControlledGolem, GolemParts, CowardlyGrunt, Lothar, GolakkaGlutton,
	Multicaster, MrSmite, GoliathSneedsMasterpiece, MaddestBomber, CrowsNestLookout, NeedforGreed, ProvingGrounds,
	SharkForm_Option, SeaTurtleForm_Option, DruidoftheReef, DruidoftheReef_Rush, DruidoftheReef_Taunt, DruidoftheReef_Both,
	JerryRigCarpenter, MoonlitGuidance, DoggieBiscuit, MonstrousParrot, DefiasBlastfisher, DeepwaterEvoker, ArcaneOverflow,
	ArcaneRemnant, GreySageParrot, RighteousDefense, SunwingSquawker, WealthRedistributor, DefiasLeper, AmuletofUndying,
	Copycat, BlackwaterCutlass, Parrrley, EdwinDefiasKingpin, BrilliantMacaw, CookietheCook, CookiesStirringRod, Suckerhook,
	ShadowbladeSlinger, WickedShipment, Hullbreaker, MantheCannons, DefiasCannoneer, BlacksmithingHammer, 
]

for class_ in AllClasses_Stormwind:
	if issubclass(class_, Card):
		class_.index = "STORMWIND" + ("~" if class_.index else '') + class_.index