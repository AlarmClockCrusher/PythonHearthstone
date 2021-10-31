from Parts_ConstsFuncsImports import *
from Parts_CardTypes import *
from Parts_TrigsAuras import *

from HS_AcrossPacks import TheCoin, Adventurers, Voidwalker, LightsJustice, Basicpowers, Upgradedpowers, SpiritWolf, DamagedGolem
from HS_Core import MindSpike, Fireball, Imp


"""Auras"""
class GameRuleAura_AuctioneerJaxon(GameRuleAura):
	def auraAppears(self): self.keeper.Game.effects[self.keeper.ID]["Trade Discovers Instead"] += 1
	def auraDisappears(self): self.keeper.Game.effects[self.keeper.ID]["Trade Discovers Instead"] -= 1

class Aura_BattlegroundBattlemaster(Aura_AlwaysOn):
	effGain, targets = "Windfury", "Neighbors"


"""Trigs"""
class Trig_SwordofaThousandTruth(TrigBoard):
	signals = ("HeroAttackedMinion", "HeroAttackedHero", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.keeper.Game.heroes[self.keeper.ID] and self.keeper.onBoard

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.Game.Manas.destroyManaCrystal(10, 3-self.keeper.ID)


class Trig_Peasant(TrigBoard):
	signals = ("TurnStarts", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return ID == self.keeper.ID and self.keeper.onBoard

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.Game.Hand_Deck.drawCard(self.keeper.ID)


class Trig_Florist(TrigBoard):
	signals = ("TurnEnds", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if spells := self.keeper.findCards4ManaReduction(lambda card: card.school == "Nature"):
			ManaMod(numpyChoice(spells), by=-1).applies()


class Trig_ImprisonedStockadesPrisoner(Trig_Countdown):
	signals, counter = ("MinionBeenPlayed", "SpellBeenPlayed", "WeaponBeenPlayed", "HeroBeenPlayed", ), 2
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject.ID == self.keeper.ID  #会在我方回合开始时进行苏醒
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if self.counter < 1: self.keeper.Game.transform(self.keeper, self.keeper.minionInside, firstTime=False)


class Trig_EnthusiasticBanker(TrigBoard):
	signals = ("TurnEnds", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if deckSize := len(self.keeper.Game.Hand_Deck.decks[self.keeper.ID]):
			card = self.keeper.Game.Hand_Deck.extractfromDeck(numpyRandint(deckSize), self.keeper.ID)[0]
			for trig in self.keeper.deathrattles:
				if isinstance(trig, Death_EnthusiasticBanker): trig.savedObjs.append(card)
					

class Trig_TwoFacedInvestor(TrigBoard):
	signals = ("TurnEnds", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if (by := 2*numpyRandint(2)-1) < 0:
			if cards := self.keeper.findCards4ManaReduction(): ManaMod(numpyChoice(cards), by=by).applies()
		elif cards := self.keeper.Game.Hand_Deck.hands[self.keeper.ID]: ManaMod(numpyChoice(cards), by=by).applies()
		
		
class Trig_FlightmasterDungar_Westfall(Trig_Countdown):
	signals, counter = ("TurnStarts", ), 1
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and ID == self.keeper.ID  #会在我方回合开始时进行苏醒
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if self.counter < 1:
			self.keeper.Game.transform(self.keeper, self.keeper.minionInside)
			self.keeper.summon(numpyChoice(Adventurers)(self.keeper.Game, self.keeper.ID))


class Trig_FlightmasterDungar_Ironforge(Trig_Countdown):
	signals, counter = ("TurnStarts", ), 3
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and ID == self.keeper.ID  #会在我方回合开始时进行苏醒
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if self.counter < 1:
			self.keeper.Game.transform(self.keeper, self.keeper.minionInside)
			self.keeper.restoresHealth(self.keeper.Game.heroes[self.keeper.ID], self.keeper.calcHeal(10))
		

class Trig_FlightmasterDungar_EasternPlaguelands(Trig_Countdown):
	signals, counter = ("TurnStarts", ), 5
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and ID == self.keeper.ID  #会在我方回合开始时进行苏醒
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if self.counter < 1:
			self.keeper.Game.transform(self.keeper, self.keeper.minionInside)
			side, game = 3 - self.keeper.ID, self.keeper.Game
			for num in range(12):
				if objs := game.charsAlive(side): self.keeper.dealsDamage(numpyChoice(objs), 1)
				else: break


class Trig_Cheesemonger(TrigBoard):
	signals = ("SpellBeenPlayed", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and ID != self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if spells := self.rngPool("%d-Cost Spells" % number):
			self.keeper.addCardtoHand(numpyChoice(spells), self.keeper.ID)


class Trig_CorneliusRoame(TrigBoard):
	signals = ("TurnStarts", "TurnEnds", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.Game.Hand_Deck.drawCard(self.keeper.ID)
		

class Trig_GoldshireGnoll(TrigHand):
	signals = ("CardLeavesHand", "CardEntersHand", )
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.inHand and ID == self.keeper.ID
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.Game.ManaHandler.calcMana_Single(self.keeper)


class Trig_FinalShowdown(Trig_Quest):
	signals = ("CardDrawn", "CardEntersHand", "NewTurnStarts",)
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return signal.startswith('N') or (ID == self.keeper.ID and
										  ((signal == "CardDrawn" and "Casts When Drawn" in target[0].index)
										   or (signal == "CardEntersHand" and comment == "byDrawing")))

	def handleCounter(self, signal, ID, subject, target, number, comment, choice=0):
		if signal.startswith('N'): self.counter = 0
		else: self.counter += 1


class Trig_LionsFrenzy(Trig_SelfAura):
	signals = ("NewTurnStarts", "CardDrawn")
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and (signal == "NewTurnStarts" or ID == self.keeper.ID)

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.calcStat()


class Trig_IreboundBrute(TrigHand):
	signals = ("CardDrawn", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.inHand and ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.Game.Manas.calcMana_Single(self.keeper)


class Trig_LostinthePark(Trig_Quest):
	signals = ("HeroAttGained",)
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return ID == self.keeper.ID

	def handleCounter(self, signal, ID, subject, target, number, comment, choice=0):
		self.counter += number


class Trig_Wickerclaw(TrigBoard):
	signals = ("HeroAttGained", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.giveEnchant(self.keeper, statEnchant=Enchantment_Cumulative(2, 0, name=Wickerclaw))


class Trig_OracleofElune(TrigBoard):
	signals = ("MinionBeenPlayed", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject.ID == self.keeper.ID and number < 3

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.summon(subject.selfCopy(self.keeper.ID, self.keeper))


class Trig_ParkPanther(TrigBoard):
	signals = ("MinionAttackingMinion", "MinionAttackingHero", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject.ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.giveHeroAttackArmor(self.keeper.ID, attGain=3, name=ParkPanther)
		

class Trig_DefendtheDwarvenDistrict(Trig_Quest):
	signals = ("MinionTookDmg", "HeroTookDmg", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject and subject.ID == self.keeper.ID and subject.category == "Spell" and subject not in self.savedObjs
	
	def handleCounter(self, signal, ID, subject, target, number, comment, choice=0):
		self.savedObjs.append(subject)
		self.counter += 1

	def assistCreateCopy(self, Copy):
		Copy.spells = [spell.createCopy(Copy.Game) for spell in self.savedObjs]
		

class Trig_LeatherworkingKit(Trig_Countdown):
	signals, counter = ("MinionDied", ), 3
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return target.ID == self.keeper.ID and self.keeper.onBoard and self.keeper.health > 0 and "Beast" in target.race
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if self.counter < 1:
			self.resetCount()
			card, mana, entersHand = self.keeper.drawCertainCard(lambda card: "Beast" in card.race)
			if entersHand: self.keeper.giveEnchant(card, 1, 1, name=LeatherworkingKit, add2EventinGUI=False)
			self.keeper.losesDurability() #Assuming weapon always loses Durability


class Trig_TavishsRam(TrigBoard):
	signals = ("BattleStarted", "BattleFinished", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.keeper and self.keeper.onBoard

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if signal == "BattleStarted": subject.getsEffect("Immune")
		else: subject.losesEffect("Immune")


class Trig_StormwindPiper(TrigBoard):
	signals = ("MinionAttackedMinion", "MinionAttackedHero", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.keeper and self.keeper.onBoard

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.AOE_GiveEnchant(self.keeper.Game.minionsonBoard(self.keeper.ID, race="Beast"), 
									statEnchant=Enchantment_Cumulative(1, 1, name=StormwindPiper))
		

class Trig_DormantRatKing(Trig_Countdown):
	signals, counter = ("MinionDied", ), 5
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and target.ID == self.keeper.ID
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if self.counter < 1: self.keeper.Game.transform(self.keeper, self.keeper.minionInside)


class Trig_SorcerersGambit(Trig_Quest):
	signals = ("SpellBeenPlayed", )
	def __init__(self, keeper):
		super().__init__(keeper)
		self.savedObjs = ["Fire", "Frost", "Arcane"]

	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.keeper.ID and subject.school in self.savedObjs
	
	def handleCounter(self, signal, ID, subject, target, number, comment, choice=0):
		self.savedObjs.remove(subject.school)
		self.counter += 1

	def assistCreateCopy(self, Copy):
		Copy.spellsLeft = self.savedObjs[:]


class Trig_CelestialInkSet(Trig_Countdown):
	signals, counter = ("SpellBeenPlayed", ), 5
	def increment(self, number):
		return number
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return number > 0 and ID == self.keeper.ID and self.keeper.onBoard and self.keeper.health > 0

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if self.counter < 1:
			self.resetCount()
			if cards := self.keeper.findCards4ManaReduction(lambda card: card.category == "Spell"):
				ManaMod(numpyChoice(cards), by=-5).applies()
			self.keeper.losesDurability()
			

class Trig_SanctumChandler(TrigBoard):
	signals = ("SpellBeenPlayed", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.keeper.ID and self.keeper.onBoard and subject.school == "Fire"

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.drawCertainCard(lambda card: card.category == "Spell")
		

class Trig_PrismaticJewelKit(TrigBoard):
	signals = ("CharLoses_Divine Shield", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.keeper.ID and self.keeper.onBoard

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.AOE_GiveEnchant([card for card in self.keeper.Game.Hand_Deck.hands[self.keeper.ID] if card.category == "Minion"], 
									statEnchant=Enchantment_Cumulative(1, 1, name=PrismaticJewelKit), add2EventinGUI=False)
		self.keeper.losesDurability()


class Trig_RisetotheOccasion(Trig_Quest):
	signals = ("MinionBeenPlayed", "SpellBeenPlayed", "WeaponBeenPlayed", "HeroBeenPlayed", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.keeper.ID and number == 1 and type(subject) not in self.savedObjs
	
	def handleCounter(self, signal, ID, subject, target, number, comment, choice=0):
		self.savedObjs.append(type(subject))
		self.counter += 1

	def assistCreateCopy(self, Copy):
		Copy.cardsPlayed = self.savedObjs[:]
		

class Trig_HighlordFordragon(TrigBoard):
	signals = ("CharLoses_Divine Shield", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if minions := [card for card in self.keeper.Game.Hand_Deck.hands[self.keeper.ID] if card.category == "Minion"]:
			self.keeper.giveEnchant(numpyChoice(minions), 5, 5, add2EventinGUI=False)
		
		
class Trig_SeekGuidance(Trig_Quest):
	signals = ("MinionBeenPlayed", "SpellBeenPlayed", "WeaponBeenPlayed", "HeroBeenPlayed", )
	def __init__(self, keeper):
		super().__init__(keeper)
		self.savedObjs = [2, 3, 4]

	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.keeper.ID and number in self.savedObjs
	
	def handleCounter(self, signal, ID, subject, target, number, comment, choice=0):
		self.savedObjs.remove(number)
		self.counter += 1

	def assistCreateCopy(self, Copy):
		Copy.costs = self.savedObjs[:]

class Trig_DiscovertheVoidShard(Trig_SeekGuidance):
	def __init__(self, keeper):
		super().__init__(keeper)
		self.savedObjs = [5, 6]

class Trig_IlluminatetheVoid(Trig_SeekGuidance):
	def __init__(self, keeper):
		super().__init__(keeper)
		self.savedObjs = [7, 8]


class Trig_VoidtouchedAttendant(TrigBoard):
	signals = ("FinalDmgonHero?", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and target.category == "Hero"

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		number[0] += 1


class Trig_ShadowclothNeedle(TrigBoard):
	signals = ("SpellBeenPlayed", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.keeper.ID and self.keeper.health > 0 and self.keeper.onBoard and subject.school == "Shadow"

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		weapon = self.keeper
		targets = weapon.Game.minionsonBoard(3-weapon.ID) + [weapon.Game.heroes[3-weapon.ID]]
		weapon.AOE_Damage(targets, [1] * len(targets))
		weapon.losesDurability()


class Trig_Psyfiend(TrigBoard):
	signals = ("SpellBeenPlayed", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject.ID == self.keeper.ID and subject.school == "Shadow"

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.AOE_Damage(list(self.keeper.Game.heroes.values()), [2, 2])


class Trig_UndercoverMole(TrigBoard):
	signals = ("MinionAttackedMinion", "MinionAttackedHero", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.keeper and self.keeper.onBoard

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.addCardtoHand(numpyChoice(self.rngPool(self.keeper.Game.heroes[3-self.keeper.ID].Class+" Cards"), self.keeper.ID))


class Trig_FindtheImposter(Trig_Quest):
	signals = ("MinionBeenPlayed", "SpellBeenPlayed", "WeaponBeenPlayed", "HeroBeenPlayed", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.keeper.ID and "SI:7" in subject.name
	

class Trig_SI7Operative(TrigBoard):
	signals = ("MinionAttackedMinion", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.keeper and self.keeper.onBoard

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.giveEnchant(self.keeper, effectEnchant=Enchantment_Cumulative(effGain="Stealth", name=SI7Operative))
		

class Trig_SI7Assassin(TrigHand):
	signals = ("MinionBeenPlayed", "SpellBeenPlayed", "WeaponBeenPlayed", "HeroBeenPlayed", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.inHand and subject.ID == self.keeper.ID and subject.name.startswith("SI:7")

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.Game.Manas.calcMana_Single(self.keeper)


class Trig_CommandtheElements(Trig_Quest):
	signals = ("MinionBeenPlayed", "SpellBeenPlayed", "WeaponBeenPlayed", "HeroBeenPlayed", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.keeper.ID and subject.overload > 0


class Trig_BolnerHammerbeak(TrigBoard):
	signals = ("MinionBeenPlayed", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.keeper.ID and self.keeper.onBoard and "~Battlecry" in subject.index
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if card := next((card for card in self.keeper.Game.Counters.cardsPlayedEachTurn[self.keeper.ID][-1] \
			  							if card.category == "Minion" and "~Battlecry" in card.index), None):
			self.keeper.invokeBattlecry(card)


class Trig_AuctionhouseGavel(TrigBoard):
	signals = ("HeroAttackedMinion", "HeroAttackedHero", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.keeper.Game.heroes[self.keeper.ID] and self.keeper.onBoard

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if cards := self.keeper.findCards4ManaReduction(lambda card: card.category == "Minion" and "~Battlecry" in card.index):
			ManaMod(numpyChoice(cards), by=-1).applies()


class Trig_SpiritAlpha(TrigBoard):
	signals = ("MinionBeenPlayed", "SpellBeenPlayed", "WeaponBeenPlayed", "HeroBeenPlayed", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.keeper.ID and self.keeper.onBoard and "~Overload" in subject.index
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.summon(SpiritWolf(self.keeper.Game, self.keeper.ID))


class Trig_TheDemonSeed(Trig_Quest):
	signals = ("HeroTookDmg", )
	def handleCounter(self, signal, ID, subject, target, number, comment, choice=0):
		self.counter += number
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return target.ID == self.keeper.ID == subject.Game.turn


class Trig_BloodboundImp(TrigBoard):
	signals = ("MinionAttackingMinion", "MinionAttackingHero", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.keeper and self.keeper.onBoard

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.dealsDamage(self.keeper.Game.heroes[self.keeper.ID], 2)


class Trig_RunedMithrilRod(Trig_Countdown):
	signals, counter = ("CardEntersHand", ), 4
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return target[0].ID == self.keeper.ID and self.keeper.onBoard and comment == "byDrawing"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if self.counter < 1:
			self.resetCount()
			for card in self.keeper.Game.Hand_Deck.hands[self.keeper.ID]:
				ManaMod(card, by=-1).applies()
			self.keeper.losesDurability()
		
		
class Trig_Anetheron(TrigHand):
	signals = ("CardEntersHand", "CardLeavesHand", "HandUpperLimitChange", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.inHand and ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.Game.Manas.calcMana_Single(self.keeper)


class Trig_RaidtheDocks(Trig_Quest):
	signals = ("MinionBeenPlayed", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.keeper.ID and "Pirate" in subject.race


class Trig_TheJuggernaut(TrigBoard):
	signals = ("TurnStarts", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		dormant = self.keeper
		dormant.summon(numpyChoice(self.rngPool("Pirates"))(dormant.Game, dormant.ID))
		dormant.equipWeapon(numpyChoice(self.rngPool("Warrior Weapons"))(dormant.Game, dormant.ID))
		for num in range(2):
			if objs := dormant.Game.charsAlive(3-dormant.ID): dormant.dealsDamage(numpyChoice(objs), 2)
			else: break


class Trig_CargoGuard(TrigBoard):
	signals = ("TurnEnds", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.giveHeroAttackArmor(self.keeper.ID, armor=3)


class Trig_RemoteControlledGolem(TrigBoard):
	signals = ("MinionTookDmg", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and target == self.keeper

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.shuffleintoDeck([GolemParts(self.keeper.Game, self.keeper.ID) for _ in range(2)])


class Trig_Lothar(TrigBoard):
	signals = ("TurnEnds", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return ID == self.keeper.ID and self.keeper.onBoard and self.keeper.health > 0 and not self.keeper.dead

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if minions := self.keeper.Game.minionsAlive(3 - self.keeper.ID):
			minion = numpyChoice(minions)
			self.keeper.Game.battle(self.keeper, minion, verifySelectable=False, resolveDeath=False)
			if minion.health < 1 or minion.dead: self.keeper.giveEnchant(self.keeper, 3, 3, name=Lothar)
			

class Trig_Suckerhook(TrigBoard):
	signals = ("TurnEnds",)
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return ID == self.keeper.ID and self.keeper.onBoard

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		keeper = self.keeper
		if weapon := keeper.Game.availableWeapon(keeper.ID):
			keeper.transform(weapon, keeper.newEvolved(type(weapon).mana, by=1, ID=keeper.ID, s="-Cost Weapons"))


class Trig_DefiasCannoneer(TrigBoard):
	signals = ("HeroAttackedMinion", "HeroAttackedHero",)
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.keeper.ID and self.keeper.onBoard

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if objs := self.keeper.Game.charsAlive(3-self.keeper.ID):
			self.keeper.dealsDamage(numpyChoice(objs), 2)
			if objs := self.keeper.Game.charsAlive(3 - self.keeper.ID):
				self.keeper.dealsDamage(numpyChoice(objs), 2)


"""Deathrattles"""
class Death_ElwynnBoar(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.keeper
		if minion.Game.Counters.minionsDiedThisGame[minion.ID].count(ElwynnBoar) > 6:
			minion.equipWeapon(SwordofaThousandTruth(minion.Game, minion.ID))

class Death_MailboxDancer(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.addCardtoHand(TheCoin, 3 - self.keeper.ID)

class Death_EnthusiasticBanker(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if self.savedObjs: self.keeper.addCardtoHand(self.savedObjs, self.keeper.ID)

	def selfCopy(self, recipient):
		trig = type(self)(recipient)
		trig.cardsStored = [card.selfCopy(recipient.ID, recipient) for card in self.savedObjs]
		return trig

	def assistCreateCopy(self, Copy):
		Copy.cardsStored = [card.createCopy(Copy.Game) for card in self.savedObjs]


class Death_StubbornSuspect(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.summon(numpyChoice(self.rngPool("3-Cost Minions to Summon"))(self.keeper.Game, self.keeper.ID))

class Death_MoargForgefiend(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.giveHeroAttackArmor(self.keeper.ID, armor=8)

class Death_PersistentPeddler(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.try_SummonfromDeck(func=lambda card: card.name == "Persistent Peddler")
		
class Death_VibrantSquirrel(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.keeper
		minion.shuffleintoDeck([Acorn(minion.Game, minion.ID) for _ in (0, 1, 2, 3)])

class Death_Composting(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.Game.Hand_Deck.drawCard(self.keeper.ID)

class Death_KodoMount(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.summon(GuffsKodo(self.keeper.Game, self.keeper.ID))

class Death_RammingMount(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.summon(TavishsRam(self.keeper.Game, self.keeper.ID))

class Death_RodentNest(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.keeper
		minion.summon([Rat(minion.Game, minion.ID) for i in range(5)])

class Death_ImportedTarantula(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.summon([InvasiveSpiderling(self.keeper.Game, self.keeper.ID) for _ in (0, 1)], relative="<>")

class Death_TheRatKing(Deathrattle_Minion):
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return target == self.keeper and self.keeper.Game.space(self.keeper.ID) > 0

	# 这个变形亡语只能触发一次。
	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrig(signal, ID, subject, target, number, comment):
			minion = self.keeper
			if minion.Game.GUI: minion.Game.GUI.deathrattleAni(minion)
			minion.Game.Counters.deathrattlesTriggered[minion.ID].append(Death_TheRatKing)
			dormant = DormantRatKing(minion.Game, minion.ID, TheRatKing(minion.Game, minion.ID))
			minion.Game.transform(minion, dormant)

class Death_NobleMount(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.summon(CarielsWarhorse(self.keeper.Game, self.keeper.ID))

class Death_ElekkMount(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.summon(XyrellasElekk(self.keeper.Game, self.keeper.ID))

class Death_HiddenGyroblade(Deathrattle_Weapon):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minions = self.keeper.Game.minionsAlive(3 - self.keeper.ID)
		if minions:
			self.keeper.dealsDamage(numpyChoice(minions), number)

class Death_LoanShark(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.addCardtoHand([TheCoin, TheCoin], self.keeper.ID)

class Death_TamsinsDreadsteed(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		TamsinsDreadsteed_Effect(self.keeper.Game, self.keeper.ID).connect()

class Death_CowardlyGrunt(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.try_SummonfromDeck()
		
class Death_Hullbreaker(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if (mana := self.keeper.drawCertainCard(lambda card: card.category == "Spell")[1]) > 0:
			self.keeper.Game.heroTakesDamage(self.keeper.ID, mana)
		

"""Cards"""
"""Neutral Cards"""
class ElwynnBoar(Minion):
	Class, race, name = "Neutral", "Beast", "Elwynn Boar"
	mana, attack, health = 1, 1, 1
	index = "STORMWIND~Neutral~Minion~1~1~1~Beast~Elwynn Boar~Deathrattle"
	requireTarget, effects, description = False, "", "Deathrattle: If you had 7 Elwynn Boars die this game, equip a 15/3 Sword of Thousand Truth"
	name_CN = "埃尔文野猪"
	deathrattle = Death_ElwynnBoar
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.minionsDiedThisGame[self.ID].count(ElwynnBoar) > 5
		

class SwordofaThousandTruth(Weapon):
	Class, name, description = "Neutral", "Sword of a Thousand Truths", "After your hero attacks, destroy your opponent's Mana Crystals"
	mana, attack, durability, effects = 10, 15, 3, ""
	index = "STORMWIND~Neutral~Weapon~10~15~3~Sword of a Thousand Truths~Legendary~Uncollectible"
	name_CN = "万千箴言之剑"
	trigBoard = Trig_SwordofaThousandTruth


class Peasant(Minion):
	Class, race, name = "Neutral", "", "Peasant"
	mana, attack, health = 1, 2, 1
	index = "STORMWIND~Neutral~Minion~1~2~1~~Peasant"
	requireTarget, effects, description = False, "", "At the start of your turn, draw a card"
	name_CN = "农夫"
	trigBoard = Trig_Peasant


class StockadesGuard(Minion):
	Class, race, name = "Neutral", "", "Stockades Guard"
	mana, attack, health = 1, 1, 3
	index = "STORMWIND~Neutral~Minion~1~1~3~~Stockades Guard~Battlecry"
	requireTarget, effects, description = True, "", "Battlecry: Give a friendly minion Taunt"
	name_CN = "监狱守卫"
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists(choice)
	
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.ID == self.ID and target != self and target.onBoard
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.giveEnchant(target, effGain="Taunt", name=StockadesGuard)
		return target
	

class AuctioneerJaxon(Minion):
	Class, race, name = "Neutral", "", "Auctioneer Jaxon"
	mana, attack, health = 2, 2, 3
	index = "STORMWIND~Neutral~Minion~2~2~3~~Auctioneer Jaxon~Legendary"
	requireTarget, effects, description = False, "", "Whenever you Trade, Discover a card from your deck to draw instead"
	name_CN = "拍卖师亚克森"
	aura = GameRuleAura_AuctioneerJaxon

	def discoverDecided(self, option, case, info_RNGSync=None, info_GUISync=None):
		self.handleDiscoveredCardfromList(option, case, ls=self.Game.Hand_Deck.decks[self.ID],
										  func=lambda index, card: self.Game.Hand_Deck.drawCard(self.ID, index),
										  info_RNGSync=info_RNGSync, info_GUISync=info_GUISync)
		

class DeeprunEngineer(Minion):
	Class, race, name = "Neutral", "", "Deeprun Engineer"
	mana, attack, health = 2, 1, 2
	index = "STORMWIND~Neutral~Minion~2~1~2~~Deeprun Engineer~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Discover a Mech. It costs (1) less"
	name_CN = "矿道工程师"
	poolIdentifier = "Mechs as Druid"
	@classmethod
	def generatePool(cls, pools):
		classCards = {s: [card for card in pools.ClassCards[s] if card.category == "Minion" and "Mech" in card.race] for s in pools.Classes}
		classCards["Neutral"] = [card for card in pools.NeutralCards if card.category == "Minion" and "Mech" in card.race]
		return ["Mechs as " + Class for Class in pools.Classes], \
			   [classCards[Class] + classCards["Neutral"] for Class in pools.Classes]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverandGenerate(DeeprunEngineer, comment, lambda : self.rngPool("Mechs as " + classforDiscover(self)))
		
	def discoverDecided(self, option, case, info_RNGSync=None, info_GUISync=None):
		self.handleDiscoverGeneratedCard(option, case, info_RNGSync, info_GUISync)
		ManaMod(option, by=-1).applies()


class EncumberedPackMule(Minion):
	Class, race, name = "Neutral", "Beast", "Encumbered Pack Mule"
	mana, attack, health = 2, 2, 3
	index = "STORMWIND~Neutral~Minion~2~2~3~Beast~Encumbered Pack Mule~Taunt"
	requireTarget, effects, description = False, "Taunt", "Taunt. When you draw this, add a copy of it to your hand"
	name_CN = "劳累的驮骡"
	
	def whenDrawn(self):
		self.addCardtoHand(self.selfCopy(self.ID, self), self.ID)


class Florist(Minion):
	Class, race, name = "Neutral", "", "Florist"
	mana, attack, health = 2, 2, 3
	index = "STORMWIND~Neutral~Minion~2~2~3~~Florist"
	requireTarget, effects, description = False, "", "At the end of your turn, reduce the Cost of a Nature spell in your hand by (1)"
	name_CN = "卖花女郎"
	trigBoard = Trig_Florist


class PandarenImporter(Minion):
	Class, race, name = "Neutral", "", "Pandaren Importer"
	mana, attack, health = 2, 1, 3
	index = "STORMWIND~Neutral~Minion~2~1~3~~Pandaren Importer~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Discover a spell that didn't start in your deck"
	name_CN = "熊猫人进口商"
	poolIdentifier = "Druid Spells"
	@classmethod
	def generatePool(cls, pools):
		return [Class + " Spells" for Class in pools.Classes], \
			   [[card for card in pools.ClassCards[Class] if card.category == "Spell"] for Class in pools.Classes]

	def decideSpellPool(self):
		pool = self.rngPool("Spells as " + classforDiscover(self))
		origDeck = self.Game.Hand_Deck.initialDecks[self.ID]
		return [card for card in pool if card not in origDeck]

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverandGenerate(PandarenImporter, comment, lambda : PandarenImporter.decideSpellPool(self))
		
	
class MailboxDancer(Minion):
	Class, race, name = "Neutral", "", "Mailbox Dancer"
	mana, attack, health = 2, 3, 2
	index = "STORMWIND~Neutral~Minion~2~3~2~~Mailbox Dancer~Battlecry~Deathrattle"
	requireTarget, effects, description = False, "", "Battlecry: Add a Coin to your hand. Deathrattle: Give your opponent one"
	name_CN = "邮箱舞者"
	deathrattle = Death_MailboxDancer
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.addCardtoHand(TheCoin, self.ID)


class SI7Skulker(Minion):
	Class, race, name = "Neutral", "", "SI:7 Skulker"
	mana, attack, health = 2, 2, 2
	index = "STORMWIND~Neutral~Minion~2~2~2~~SI:7 Skulker~Stealth~Battlecry"
	requireTarget, effects, description = False, "Stealth", "Stealth. Battlecry: The next card you draw costs (1) less"
	name_CN = "军情七处潜伏者"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		#假设只有最终进入手牌的卡会享受减费
		SI7Skulker_Effect(self.Game, self.ID).connect()
	

class StockadesPrisoner(Minion):
	Class, race, name = "Neutral", "", "Stockades Prisoner"
	mana, attack, health = 2, 5, 4
	index = "STORMWIND~Neutral~Minion~2~5~4~~Stockades Prisoner"
	requireTarget, effects, description = False, "", "Starts Dormant. After you play 3 cards, this awakens"
	name_CN = "监狱囚徒"
	#出现即休眠的随从的played过程非常简单
	def played(self, target=None, choice=0, mana=0, posinHand=-2, comment=""):
		self.health = self.health_max
		self.appears(firstTime=True)  #打出时一定会休眠，同时会把Game.minionPlayed变为None
		
	def appears(self, firstTime=True):
		self.onBoard = True
		self.inHand = self.inDeck = self.dead = False
		self.enterBoardTurn = self.Game.numTurn
		self.mana = type(self).mana  #Restore the minion's mana to original value.
		self.decideAttChances_base()  #Decide base att chances, given Windfury and Mega Windfury
		#没有光环，目前炉石没有给随从人为添加光环的效果, 不可能在把手牌中获得的扳机带入场上，因为会在变形中丢失
		#The buffAuras/hasAuras will react to this signal.
		if firstTime:  #首次出场时会进行休眠，而且休眠状态会保持之前的随从buff
			self.Game.transform(self, ImprisonedStockadesPrisoner(self.Game, self.ID, self), firstTime=True)
		else:  #只有不是第一次出现在场上时才会执行这些函数
			if self.btn:
				self.btn.isPlayed, self.btn.card = True, self
				self.btn.placeIcons()
				self.btn.statChangeAni()
				self.btn.effectChangeAni()
			for aura in self.auras: aura.auraAppears()
			for trig in self.trigsBoard + self.deathrattles: trig.connect()
			self.Game.sendSignal("MinionAppears", self.ID, self, None, 0, comment=firstTime)
	
	def awakenEffect(self):
		pass


class ImprisonedStockadesPrisoner(Dormant):
	Class, school, name = "Neutral", "", "Imprisoned Stockades Prisoner"
	description = "Awakens after you play 3 cards"
	trigBoard = Trig_ImprisonedStockadesPrisoner


class EntrappedSorceress(Minion):
	Class, race, name = "Neutral", "", "Entrapped Sorceress"
	mana, attack, health = 3, 3, 4
	index = "STORMWIND~Neutral~Minion~3~3~4~~Entrapped Sorceress~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: If you control a Quest, Discover a spell"
	name_CN = "被困的女巫"
	poolIdentifier = "Druid Spells"
	@classmethod
	def generatePool(cls, pools):
		return [Class + " Spells" for Class in pools.Classes], \
			   [[card for card in cards if card.category == "Spell"] for cards in pools.ClassCards.values()]
	
	def effCanTrig(self):
		self.effectViable = self.Game.Secrets.mainQuests[self.ID] != []
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Secrets.mainQuests[self.ID] or self.Game.Secrets.sideQuests[self.ID]:
			self.discoverandGenerate(EntrappedSorceress, comment, lambda : self.rngPool(classforDiscover(self) + " Spells"))
	

class EnthusiasticBanker(Minion):
	Class, race, name = "Neutral", "", "Enthusiastic Banker"
	mana, attack, health = 3, 2, 3
	index = "STORMWIND~Neutral~Minion~3~2~3~~Enthusiastic Banker"
	requireTarget, effects, description = False, "", "At the end of your turn, store a card from your deck. Deathrattle: Add the stored cards to your hand"
	name_CN = "热情的柜员"
	trigBoard, deathrattle = Trig_EnthusiasticBanker, Death_EnthusiasticBanker


class ImpatientShopkeep(Minion):
	Class, race, name = "Neutral", "", "Impatient Shopkeep"
	mana, attack, health = 3, 3, 3
	index = "STORMWIND~Neutral~Minion~3~3~3~~Impatient Shopkeep~Rush~Tradeable"
	requireTarget, effects, description = False, "Rush", "Tradeable, Rush"
	name_CN = "不耐烦的店长"


class NorthshireFarmer(Minion):
	Class, race, name = "Neutral", "", "Northshire Farmer"
	mana, attack, health = 3, 3, 3
	index = "STORMWIND~Neutral~Minion~3~3~3~~Northshire Farmer~Battlecry"
	requireTarget, effects, description = True, "", "Battlecry: Choose a friendly Beast. Shuffle three 3/3 copies into your deck"
	name_CN = "北郡农民"
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
	
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard and target.ID == self.ID and "Beast" in target.race
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.shuffleintoDeck([target.selfCopy(self.ID, self, attack=3, health=3) for _ in range(3)])
		return target


class PackageRunner(Minion):
	Class, race, name = "Neutral", "", "Package Runner"
	mana, attack, health = 3, 5, 6
	index = "STORMWIND~Neutral~Minion~3~5~6~~Package Runner"
	requireTarget, effects, description = False, "Can't Attack", "Can only attack if you have at least 8 cards in hand"
	name_CN = "包裹速递员"

	def attackAllowedbyEffect(self):
		return self.effects["Can't Attack"] < 1 or \
			   (self.effects["Can't Attack"] == 1 and not self.silenced and len(self.Game.Hand_Deck.hands[self.ID]) > 7)


class RustrotViper(Minion):
	Class, race, name = "Neutral", "Beast", "Rustrot Viper"
	mana, attack, health = 3, 3, 4
	index = "STORMWIND~Neutral~Minion~3~3~4~Beast~Rustrot Viper~Battlecry~Tradeable"
	requireTarget, effects, description = False, "", "Tradeable. Battlecry: Destroy your opponent's weapon"
	name_CN = "锈烂蝰蛇"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for weapon in self.Game.weapons[3 - self.ID]:
			weapon.destroyed()


class TravelingMerchant(Minion):
	Class, race, name = "Neutral", "", "Traveling Merchant"
	mana, attack, health = 3, 2, 3
	index = "STORMWIND~Neutral~Minion~3~2~3~~Traveling Merchant~Battlecry~Tradeable"
	requireTarget, effects, description = False, "", "Tradeable. Battlecry: Gain +1/+1 for each other friendly minion you control"
	name_CN = "旅行商人"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if not self.dead and (self.onBoard or self.inHand):
			num = len(self.Game.minionsonBoard(self.ID, exclude=self))
			if num: self.giveEnchant(self, num, num, name=TravelingMerchant)


class TwoFacedInvestor(Minion):
	Class, race, name = "Neutral", "", "Two-Faced Investor"
	mana, attack, health = 3, 2, 4
	index = "STORMWIND~Neutral~Minion~3~2~4~~Two-Faced Investor"
	requireTarget, effects, description = False, "", "At the end of your turn, reduce the Cost of a card in your hand by (1). (50% chance to increase)"
	name_CN = "双面投资者"
	trigBoard = Trig_TwoFacedInvestor


class FlightmasterDungar(Minion):
	Class, race, name = "Neutral", "", "Flightmaster Dungar"
	mana, attack, health = 3, 3, 3
	index = "STORMWIND~Neutral~Minion~3~3~3~~Flightmaster Dungar~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: Choose a flightpath and go Dormant. Awaken with a bonus when you complete it!"
	name_CN = "飞行管理员杜加尔"
	
	def goDormant(self, flightpath):
		newMinion = FlightmasterDungar_Dormant(self.Game, self.ID, self) if flightpath else None
		if newMinion:
			if flightpath == Westfall:
				newMinion.trigsBoard.append(Trig_FlightmasterDungar_Westfall(newMinion))
			elif flightpath == Ironforge:
				newMinion.trigsBoard.append(Trig_FlightmasterDungar_Ironforge(newMinion))
			elif flightpath == EasternPlaguelands:
				newMinion.trigsBoard.append(Trig_FlightmasterDungar_EasternPlaguelands(newMinion))
			self.Game.transform(self, newMinion)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		self.chooseFixedOptions(FlightmasterDungar, comment,
								options=[Westfall(ID=self.ID), Ironforge(ID=self.ID), EasternPlaguelands(ID=self.ID)])
	
	def discoverDecided(self, option, case, info_RNGSync=None, info_GUISync=None):
		optionType = type(option)
		if case != "Guided": self.Game.picks_Backup.append((info_RNGSync, info_GUISync, case == "Random", optionType))
		FlightmasterDungar.goDormant(self, optionType)

class Westfall(Option):
	name, category = "Westfall", "Option_Spell"
	mana, attack, health = 0, -1, -1

class Ironforge(Option):
	name, category = "Ironforge", "Option_Spell"
	mana, attack, health = 0, -1, -1

class EasternPlaguelands(Option):
	name, category = "Eastern Plaguelands", "Option_Spell"
	mana, attack, health = 0, -1, -1

class FlightmasterDungar_Dormant(Dormant):
	Class, school, name = "Neutral", "", "Sleeping Naralex"
	description = "Dormant. Awaken with bonus!"
	trigBoard = Trig_FlightmasterDungar_Westfall
	def assistCreateCopy(self, Copy):
		Copy.minionInside = self.minionInside.createCopy(Copy.Game)
		Copy.name, Copy.Class, Copy.description = self.name, self.Class, self.description


class Nobleman(Minion):
	Class, race, name = "Neutral", "", "Nobleman"
	mana, attack, health = 3, 2, 3
	index = "STORMWIND~Neutral~Minion~3~2~3~~Nobleman~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Create a Golden copy of a random card in your hand"
	name_CN = "贵族"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if ownHand := self.Game.Hand_Deck.hands[self.ID]:
			self.addCardtoHand(numpyChoice(ownHand).selfCopy(self.ID, self), self.ID)
	
	
class Cheesemonger(Minion):
	Class, race, name = "Neutral", "", "Cheesemonger"
	mana, attack, health = 4, 3, 6
	index = "STORMWIND~Neutral~Minion~4~3~6~~Cheesemonger"
	requireTarget, effects, description = False, "", "Whenever your opponent casts a spell, add a spell with the same Cost to your hand"
	name_CN = "奶酪商贩"
	trigBoard = Trig_Cheesemonger
	poolIdentifier = "0-Cost Spells"
	@classmethod
	def generatePool(cls, pools):
		spells = {}
		for Class in pools.Classes:
			for card in pools.ClassCards[Class]:
				if card.category == "Spell": add2ListinDict(card, spells, card.mana)
		return ["%d-Cost Spells" % cost for cost in spells.keys()], list(spells.values())
	

class GuildTrader(Minion):
	Class, race, name = "Neutral", "", "Guild Trader"
	mana, attack, health = 4, 3, 4
	index = "STORMWIND~Neutral~Minion~4~3~4~~Guild Trader~Spell Damage~Tradeable"
	requireTarget, effects, description = False, "Spell Damage_2", "Tradeable, Spell Damage +2"
	name_CN = "工会商人"
		

class RoyalLibrarian(Minion):
	Class, race, name = "Neutral", "", "Royal Librarian"
	mana, attack, health = 4, 3, 4
	index = "STORMWIND~Neutral~Minion~4~3~4~~Royal Librarian~Battlecry~Tradeable"
	requireTarget, effects, description = True, "", "Tradeable. Battlecry: Silence a minion"
	name_CN = "王室图书管理员"

	def targetExists(self, choice=0):
		return self.selectableMinionExists()
	
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard and target != self
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: target.getsSilenced()
		return target
	
	
class SpiceBreadBaker(Minion):
	Class, race, name = "Neutral", "", "Spice Bread Baker"
	mana, attack, health = 4, 3, 2
	index = "STORMWIND~Neutral~Minion~4~3~2~~Spice Bread Baker~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Restore Health to your hero equal to your hand size"
	name_CN = "香料面包师"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if handSize := len(self.Game.Hand_Deck.hands[self.ID]):
			self.restoresHealth(self.Game.heroes[self.ID], self.calcHeal(handSize))


class StubbornSuspect(Minion):
	Class, race, name = "Neutral", "", "Stubborn Suspect"
	mana, attack, health = 4, 3, 3
	index = "STORMWIND~Neutral~Minion~4~3~3~~Stubborn Suspect~Deathrattle"
	requireTarget, effects, description = False, "", "Deathrattle: Summon a random 3-Cost minion"
	name_CN = "顽固的嫌疑人"
	deathrattle = Death_StubbornSuspect
	poolIdentifier = "3-Cost Minions to Summon"
	@classmethod
	def generatePool(cls, pools):
		return "3-Cost Minions to Summon", pools.MinionsofCost[3]


class LionsGuard(Minion):
	Class, race, name = "Neutral", "", "Lion's Guard"
	mana, attack, health = 5, 4, 6
	index = "STORMWIND~Neutral~Minion~5~4~6~~Lion's Guard~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: If you have 15 or less Health, gain +2/+4 and Taunt"
	name_CN = "暴风城卫兵"
	
	def effCanTrig(self):
		self.effectViable = self.Game.heroes[self.ID].health < 16
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.onBoard and self.Game.heroes[self.ID].health < 16:
			self.giveEnchant(self, 2, 4, effGain="Taunt", name=LionsGuard)


class StormwindGuard(Minion):
	Class, race, name = "Neutral", "", "Stormwind Guard"
	mana, attack, health = 5, 4, 5
	index = "STORMWIND~Neutral~Minion~5~4~5~~Stormwind Guard~Taunt~Battlecry"
	requireTarget, effects, description = False, "Taunt", "Taunt. Battlecry: Give adjacent minions +1/+1"
	name_CN = "暴风城卫兵"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.onBoard and (neighbors := self.Game.neighbors2(self)[0]):
			self.AOE_GiveEnchant(neighbors, 1, 1, name=StormwindGuard)


class BattlegroundBattlemaster(Minion):
	Class, race, name = "Neutral", "", "Battleground Battlemaster"
	mana, attack, health = 6, 5, 5
	index = "STORMWIND~Neutral~Minion~6~5~5~~Battleground Battlemaster"
	requireTarget, effects, description = False, "", "Adjacent minions have Windfury"
	name_CN = "战场军官"
	aura = Aura_BattlegroundBattlemaster


class CityArchitect(Minion):
	Class, race, name = "Neutral", "", "City Architect"
	mana, attack, health = 6, 4, 4
	index = "STORMWIND~Neutral~Minion~6~4~4~~City Architect~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Summon two 0/5 Castle Walls with Taunt"
	name_CN = "城市建筑师"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon([CastleWall(self.Game, self.ID) for _ in (0, 1)], relative="<>")

class CastleWall(Minion):
	Class, race, name = "Neutral", "", "Castle Wall"
	mana, attack, health = 2, 0, 5
	index = "STORMWIND~Neutral~Minion~2~0~5~~Castle Wall~Taunt~Uncollectible"
	requireTarget, effects, description = False, "Taunt", "Taunt"
	name_CN = "城堡石墙"


class CorneliusRoame(Minion):
	Class, race, name = "Neutral", "", "Cornelius Roame"
	mana, attack, health = 6, 4, 5
	index = "STORMWIND~Neutral~Minion~6~4~5~~Cornelius Roame~Legendary"
	requireTarget, effects, description = False, "", "At the start and end of each player's turn, draw a card"
	name_CN = "考内留斯·罗姆"
	trigBoard = Trig_CorneliusRoame


class LadyPrestor(Minion):
	Class, race, name = "Neutral", "", "Lady Prestor"
	mana, attack, health = 6, 6, 7
	index = "STORMWIND~Neutral~Minion~6~6~7~~Lady Prestor~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: Transform minions in your deck into random Dragons. (They keep their original stats and Cost)"
	name_CN = "普瑞斯托女士"
	poolIdentifier = "Dragons"
	@classmethod
	def generatePool(cls, pools):
		return "Dragons", pools.MinionswithRace["Dragon"]
	
	#不知道拉法姆的替换手牌、牌库和迦拉克隆会有什么互动。假设不影响主迦拉克隆。
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
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
	index = "STORMWIND~Neutral~Minion~8~8~8~Demon~Mo'arg Forgefiend~Taunt~Deatthrattle"
	requireTarget, effects, description = False, "Taunt", "Taunt. Deathrattle: Gain 8 Armor"
	name_CN = "莫尔葛熔魔"
	deathrattle = Death_MoargForgefiend


class VarianKingofStormwind(Minion):
	Class, race, name = "Neutral", "", "Varian, King of Stormwind"
	mana, attack, health = 8, 7, 7
	index = "STORMWIND~Neutral~Minion~8~7~7~~Varian, King of Stormwind~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: Draw a Rush minion to gain Rush. Repeat for Taunt and Divine Shield"
	name_CN = "瓦里安，暴风城国王"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
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
			self.giveEnchant(self, "Rush", name=VarianKingofStormwind)
			
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
			self.giveEnchant(self, effGain="Taunt", name=VarianKingofStormwind)
		
		if self.drawCertainCard(lambda card: card.category == "Minion" and card.effects["Divine Shield"] > 0)[0]:
			self.giveEnchant(self, effGain="Divine Shield", name=VarianKingofStormwind)


class GoldshireGnoll(Minion):
	Class, race, name = "Neutral", "", "Goldshire Gnoll"
	mana, attack, health = 10, 5, 4
	index = "STORMWIND~Neutral~Minion~10~5~4~~Goldshire Gnoll~Rush"
	requireTarget, effects, description = False, "Rush", "Rush. Costs (1) less for each other card in your hand"
	name_CN = "闪金镇豺狼人"
	trigHand = Trig_GoldshireGnoll
	def selfManaChange(self):
		if self.inHand:
			self.mana -= len(self.Game.Hand_Deck.hands[self.ID]) - 1
			self.mana = max(0, self.mana)


"""Demon Hunter Cards"""
class DemonslayerKurtrus(Minion):
	Class, race, name = "Demon Hunter", "", "Demonslayer Kurtrus"
	mana, attack, health = 5, 7, 7
	index = "STORMWIND~Demon Hunter~Minion~5~7~7~~Demonslayer Kurtrus~Battlecry~Legendary~Uncollectible"
	requireTarget, effects, description = False, "", "Battlecry: For the rest of the game, cards you draw cost (2) less"
	name_CN = "屠魔者库尔特鲁斯"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		DemonslayerKurtrus_Effect(self.Game, self.ID).connect()

class ClosethePortal(Quest):
	Class, name = "Demon Hunter", "Close the Portal"
	requireTarget, mana, effects = False, -1, ""
	index = "STORMWIND~Demon Hunter~Spell~0~~Close the Portal~~Questline~Legendary~Uncollectible"
	description = "Questline: Draw 5 cards in one turn. Reward: Demonslayer Kurtrus"
	name_CN = "关闭传送门"
	numNeeded, newQuest, reward = 5, None, DemonslayerKurtrus
	race, trigBoard = "Questline", Trig_FinalShowdown

class GainMomentum(Quest):
	Class, name = "Demon Hunter", "Gain Momentum"
	requireTarget, mana, effects = False, -1, ""
	index = "STORMWIND~Demon Hunter~Spell~0~~Gain Momentum~~Questline~Legendary~Uncollectible"
	description = "Questline: Draw 5 cards in one turn. Reward: Reduce the Cost of the cards in your hand by (1)"
	name_CN = "汲取动力"
	numNeeded, newQuest, reward = 5, ClosethePortal, None
	race, trigBoard = "Questline", Trig_FinalShowdown
	def questEffect(self, game, ID):
		for card in game.Hand_Deck.hands[ID]: ManaMod(card, by=-1).applies()

class FinalShowdown(Quest):
	Class, name = "Demon Hunter", "Final Showdown"
	requireTarget, mana, effects = False, 1, ""
	index = "STORMWIND~Demon Hunter~Spell~1~~Final Showdown~~Questline~Legendary"
	description = "Questline: Draw 4 cards in one turn. Reward: Reduce the Cost of the cards in your hand by (1)"
	name_CN = "一决胜负"
	numNeeded, newQuest, reward = 4, GainMomentum, None
	race, trigBoard = "Questline", Trig_FinalShowdown
	def questEffect(self, game, ID):
		for card in game.Hand_Deck.hands[ID]: ManaMod(card, by=-1).applies()


class Metamorfin(Minion):
	Class, race, name = "Demon Hunter", "Murloc", "Metamorfin"
	mana, attack, health = 1, 1, 2
	index = "STORMWIND~Demon Hunter~Minion~1~1~2~Murloc~Metamorfin~Taunt~Battlecry"
	requireTarget, effects, description = False, "Taunt", "Taunt. Battlecry: If you've cast a Fel spell this turn, gain +2/+2"
	name_CN = "魔变鱼人"

	def effCanTrig(self):
		self.effectViable = any(card.school == "Fel" for card in self.Game.Counters.cardsPlayedEachTurn[self.ID][-1])
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if any(card.school == "Fel" for card in self.Game.Counters.cardsPlayedEachTurn[self.ID][-1]):
			self.giveEnchant(self, 2, 2, name=Metamorfin)
		
		
class SigilofAlacrity(Spell):
	Class, school, name = "Demon Hunter", "Shadow", "Sigil of Alacrity"
	requireTarget, mana, effects = False, 1, ""
	index = "STORMWIND~Demon Hunter~Spell~1~Shadow~Sigil of Alacrity"
	description = "At the start of your next turn, draw a card and reduce its Cost by (1)"
	name_CN = "敏捷咒符"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		SigilofAlacrity_Effect(self.Game, self.ID).connect()


class FelBarrage(Spell):
	Class, school, name = "Demon Hunter", "Fel", "Fel Barrage"
	requireTarget, mana, effects = False, 2, ""
	index = "STORMWIND~Demon Hunter~Spell~2~Fel~Fel Barrage"
	description = "Deal 2 damage to the low Health enemy, twice"
	name_CN = "邪能弹幕"
	def text(self): return self.calcDamage(2)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
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
	requireTarget, mana, effects = True, 3, "Lifesteal"
	index = "STORMWIND~Demon Hunter~Spell~3~Fel~Chaos Leech~Lifesteal~Outcast"
	description = "Lifesteal. Deal 3 damage to a minion. Outcast: Deal 5 instead"
	name_CN = "混乱吸取"
	def available(self):
		return self.selectableMinionExists()
	
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard
	
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.outcastcanTrig(self)
	
	def text(self): return "%d, %d"%(self.calcDamage(3), self.calcDamage(5))
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.dealsDamage(target, self.calcDamage(5 if posinHand == 0 or posinHand == -1 else 3))
		return target


class LionsFrenzy(Weapon):
	Class, name, description = "Demon Hunter", "Lion's Frenzy", "Has Attack equal to the number of cards you've drawn this turn"
	mana, attack, durability, effects = 3, 0, 2, ""
	index = "STORMWIND~Demon Hunter~Weapon~3~0~2~Lion's Frenzy"
	name_CN = "雄狮之怒"
	trigBoard = Trig_LionsFrenzy
	def statCheckResponse(self):
		if self.onBoard: self.attack = self.Game.Counters.numCardsDrawnThisTurn[self.ID]


class Felgorger(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Felgorger"
	mana, attack, health = 4, 4, 3
	index = "STORMWIND~Demon Hunter~Minion~4~4~3~Demon~Felgorger~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Draw a Fel spell. Reduce its Cost by (2)"
	name_CN = "邪能吞食者"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		card, mana, entersHand = self.drawCertainCard(lambda card: card.school == "Fel")
		if entersHand: ManaMod(card, by=-2).applies()
	

class PersistentPeddler(Minion):
	Class, race, name = "Demon Hunter", "", "Persistent Peddler"
	mana, attack, health = 4, 4, 3
	index = "STORMWIND~Demon Hunter~Minion~4~4~3~~Persistent Peddler~Deathrattle~Tradeable"
	requireTarget, effects, description = False, "", "Tradeable. Deathrattle: Summon a Persistent Peddler from your deck"
	name_CN = "固执的商贩"
	deathrattle = Death_PersistentPeddler


class IreboundBrute(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Irebound Brute"
	mana, attack, health = 8, 6, 7
	index = "STORMWIND~Demon Hunter~Minion~8~6~7~Demon~Irebound Brute~Taunt"
	requireTarget, effects, description = False, "Taunt", "Taunt. Costs (1) less for each card drawn this turn"
	name_CN = "怒缚蛮兵"
	trigHand = Trig_IreboundBrute
	def selfManaChange(self):
		if self.inHand:
			self.mana -= self.Game.Counters.numCardsDrawnThisTurn[self.ID]
			self.mana = max(self.mana, 0)


class JaceDarkweaver(Minion):
	Class, race, name = "Demon Hunter", "", "Jace Darkweaver"
	mana, attack, health = 8, 7, 5
	index = "STORMWIND~Demon Hunter~Minion~8~7~5~~Jace Darkweaver~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: Cast all Fel spells you've played this game(targets enemies if possible)"
	name_CN = "杰斯·织暗"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		game = self.Game
		spells = [card for card in game.Counters.cardsPlayedThisGame[self.ID] \
						  								if "~Fel~" in card.index]
		numpyShuffle(spells)
		if spells:
			for spell in spells:
				spell(game, self.ID).cast(func=lambda obj: obj.ID != self.ID)
				game.gathertheDead(decideWinner=True)


"""Druid Cards"""
class GufftheTough(Minion):
	Class, race, name = "Druid", "Beast", "Guff the Tough"
	mana, attack, health = 5, 8, 8
	index = "STORMWIND~Druid~Minion~5~8~8~Beast~Guff the Tough~Battlecry~Legendary~Uncollectible"
	requireTarget, effects, description = False, "", "Taunt. Battlecry: Give your hero +8 Attack this turn. Gain 8 Armor"
	name_CN = "铁肤古夫"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.giveHeroAttackArmor(self.ID, attGain=8, armor=8, name=GufftheTough)

class FeralFriendsy(Quest):
	Class, name = "Druid", "Feral Friendsy"
	requireTarget, mana, effects = False, -1, ""
	index = "STORMWIND~Druid~Spell~0~~Feral Friendsy~~Questline~Legendary~Uncollectible"
	description = "Questline: Gain 6 Attack with your hero. Reward: Guff the Tough"
	name_CN = "野性暴朋"
	numNeeded, newQuest, reward = 6, None, GufftheTough
	race, trigBoard = "Questline", Trig_LostinthePark

class DefendtheSquirrels(Quest):
	Class, name = "Druid", "Defend the Squirrels"
	requireTarget, mana, effects = False, -1, ""
	index = "STORMWIND~Druid~Spell~0~~Defend the Squirrels~~Questline~Legendary~Uncollectible"
	description = "Questline: Gain 5 Attack with your hero. Reward: Gain 5 Armor and draw a card"
	numNeeded, newQuest, reward = 5, FeralFriendsy, None
	name_CN = "保护松鼠"
	race, trigBoard = "Questline", Trig_LostinthePark
	def questEffect(self, game, ID):
		self.giveHeroAttackArmor(ID, armor=5)
		game.Hand_Deck.drawCard(ID)

class LostinthePark(Quest):
	Class, name = "Druid", "Lost in the Park"
	requireTarget, mana, effects = False, 1, ""
	index = "STORMWIND~Druid~Spell~1~~Lost in the Park~~Questline~Legendary"
	description = "Questline: Gain 4 Attack with your hero. Reward: Gain 5 Armor"
	numNeeded, newQuest, reward = 4, DefendtheSquirrels, None
	name_CN = "游园迷梦"
	race, trigBoard = "Questline", Trig_LostinthePark
	def questEffect(self, game, ID):
		self.giveHeroAttackArmor(ID, armor=5)


class Fertilizer(Spell):
	Class, school, name = "Druid", "Nature", "Fertilizer"
	requireTarget, mana, effects = False, 1, ""
	index = "STORMWIND~Druid~Spell~1~Nature~Fertilizer~Uncollectible"
	description = "Give your minions +1 Attack"
	name_CN = "肥料滋养"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.AOE_GiveEnchant(self.Game.minionsonBoard(self.ID), 1, 0, name=Fertilizer)

class NewGrowth(Spell):
	Class, school, name = "Druid", "Nature", "New Growth"
	requireTarget, mana, effects = False, 1, ""
	index = "STORMWIND~Druid~Spell~1~Nature~New Growth~Uncollectible"
	description = "Summon a 2/2 Treant"
	name_CN = "新生细苗"
	def available(self):
		return self.Game.space(self.ID) > 0
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
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
	requireTarget, mana, effects = False, 1, ""
	index = "STORMWIND~Druid~Spell~1~Nature~Sow the Soil~Choose One"
	description = "Choose One - Give your minions +1 Attack; or Summon a 2/2 Treant"
	name_CN = "播种施肥"
	options = (Fertilizer_Option, NewGrowth_Option)
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if choice != 0: self.summon(Treant_Stormwind(self.Game, self.ID))
		if choice < 1: self.AOE_GiveEnchant(self.Game.minionsonBoard(self.ID), 1, 0, name=SowtheSoil)
		
class Treant_Stormwind(Minion):
	Class, race, name = "Neutral", "", "Treant"
	mana, attack, health = 2, 2, 2
	index = "STORMWIND~Neutral~Minion~2~2~2~~Treant~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "树人"
	
	
class VibrantSquirrel(Minion):
	Class, race, name = "Druid", "Beast", "Vibrant Squirrel"
	mana, attack, health = 1, 2, 1
	index = "STORMWIND~Druid~Minion~1~2~1~Beast~Vibrant Squirrel"
	requireTarget, effects, description = False, "", "Deathrattle: Shuffle 4 Acorns into your deck. When drawn, summon a 2/1 Squirrel"
	name_CN = "活泼的松鼠"
	deathrattle = Death_VibrantSquirrel


class Acorn(Spell):
	Class, school, name = "Druid", "", "Acorn"
	requireTarget, mana, effects = False, 1, ""
	index = "STORMWIND~Druid~Spell~1~~Acorn~Casts When Drawn~Uncollectible"
	description = "Casts When Drawn. Summon a 2/1 Squirrel"
	name_CN = "橡果"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon(SatisfiedSquirrel(self.Game, self.ID))


class SatisfiedSquirrel(Minion):
	Class, race, name = "Druid", "Beast", "Satisfied Squirrel"
	mana, attack, health = 1, 2, 1
	index = "STORMWIND~Druid~Minion~1~2~1~Beast~Satisfied Squirrel~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "满足的松鼠"


class Composting(Spell):
	Class, school, name = "Druid", "Nature", "Composting"
	requireTarget, mana, effects = False, 2, ""
	index = "STORMWIND~Druid~Spell~2~Nature~Composting"
	description = "Give your minions 'Deathrattle: Draw a card'"
	name_CN = "施肥"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.AOE_GiveEnchant(self.Game.minionsonBoard(self.ID), trig=Death_Composting, trigType="Deathrattle")
		return target


class Wickerclaw(Minion):
	Class, race, name = "Druid", "Beast", "Wickerclaw"
	mana, attack, health = 2, 1, 4
	index = "STORMWIND~Druid~Minion~2~1~4~Beast~Wickerclaw"
	requireTarget, effects, description = False, "", "After your hero gains Attack, this minion gain +2 Attack"
	name_CN = "柳魔锐爪兽"
	trigBoard = Trig_Wickerclaw


class OracleofElune(Minion):
	Class, race, name = "Druid", "", "Oracle of Elune"
	mana, attack, health = 3, 2, 4
	index = "STORMWIND~Druid~Minion~3~2~4~~Oracle of Elune"
	requireTarget, effects, description = False, "", "After you play a minion that costs (2) or less, summon a copy of it"
	name_CN = "艾露恩神谕者"
	trigBoard = Trig_OracleofElune


class KodoMount(Spell):
	Class, school, name = "Druid", "", "Kodo Mount"
	requireTarget, mana, effects = True, 4, ""
	index = "STORMWIND~Druid~Spell~4~~Kodo Mount"
	description = "Give a minion +4/+2 and Rush. When it dies, summon a Kodo"
	name_CN = "科多兽坐骑"
	def available(self):
		return self.selectableMinionExists()
	
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.giveEnchant(target, 4, 2, effGain="Rush", trig=Death_KodoMount, trigType="Deathrattle", connect=target.onBoard, name=KodoMount)
		return target

class GuffsKodo(Minion):
	Class, race, name = "Druid", "Beast", "Guff's Kodo"
	mana, attack, health = 3, 4, 2
	index = "STORMWIND~Druid~Minion~3~4~2~Beast~Guff's Kodo~Rush~Uncollectible"
	requireTarget, effects, description = False, "Rush", "Rush"
	name_CN = "古夫的科多兽"
	

class ParkPanther(Minion):
	Class, race, name = "Druid", "Beast", "Park Panther"
	mana, attack, health = 4, 4, 4
	index = "STORMWIND~Druid~Minion~4~4~4~Beast~Park Panther~Rush"
	requireTarget, effects, description = False, "Rush", "Rush. Whenever this minion attacks, give your hero +3 Attack this turn"
	name_CN = "花园猎豹"
	trigBoard = Trig_ParkPanther


class BestinShell(Spell):
	Class, school, name = "Druid", "", "Best in Shell"
	requireTarget, mana, effects = False, 6, ""
	index = "STORMWIND~Druid~Spell~6~~Best in Shell~Tradeable"
	description = "Tradeable. Summon two 2/7 Turtles with Taunt"
	name_CN = "紧壳商品"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon([GoldshellTurtle(self.Game, self.ID) for _ in (0, 1)])


class GoldshellTurtle(Minion):
	Class, race, name = "Druid", "Beast", "Goldshell Turtle"
	mana, attack, health = 4, 2, 7
	index = "STORMWIND~Druid~Minion~4~2~7~Beast~Goldshell Turtle~Taunt~Uncollectible"
	requireTarget, effects, description = False, "Taunt", "Taunt"
	name_CN = "金壳龟"


class SheldrasMoontree(Minion):
	Class, race, name = "Druid", "", "Sheldras Moontree"
	mana, attack, health = 8, 5, 5
	index = "STORMWIND~Druid~Minion~8~5~5~~Sheldras Moontree~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: The next 3 spells you draw are Cast When Drawn"
	name_CN = "沙德拉斯·月树"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		SheldrasMoontree_Effect(self.Game, self.ID).connect()


"""Hunter cards"""
class DevouringSwarm(Spell):
	Class, school, name = "Hunter", "", "Devouring Swarm"
	requireTarget, mana, effects = True, 0, ""
	index = "STORMWIND~Hunter~Spell~0~~Devouring Swarm"
	description = "Choose an enemy minion. Your minions attack it, then return any that die to your hand"
	name_CN = "集群撕咬"
	def available(self):
		return self.selectableEnemyMinionExists()
	
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard and target.ID != self.ID

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		game = self.Game
		if target and (minions := game.minionsAlive(self.ID)):
			minions = game.objs_SeqSorted(minions)[0]
			for minion in minions:
				if target.onBoard and target.health > 0 and not target.dead:
					game.battle(minion, target, verifySelectable=False, useAttChance=False, resolveDeath=False, resetRedirTrig=True)
			for minion in minions:
				if minion.dead or minion.health < 1: self.addCardtoHand(type(minion), self.ID)
		return target


class TavishMasterMarksman(Minion):
	Class, race, name = "Hunter", "", "Tavish, Master Marksman"
	mana, attack, health = 5, 7, 7
	index = "STORMWIND~Hunter~Minion~5~7~7~~Tavish, Master Marksman~Battlecry~Legendary~Uncollectible"
	requireTarget, effects, description = False, "", "Battlecry: For the rest of the game, spells you cast refresh your Hero Power"
	name_CN = "射击大师塔维什"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		TavishMasterMarksman_Effect(self.Game, self.ID).connect()

class KnockEmDown(Quest):
	Class, name = "Hunter", "Knock 'Em Down"
	requireTarget, mana, effects = False, -1, ""
	index = "STORMWIND~Hunter~Spell~0~~Knock 'Em Down~~Questline~Legendary~Uncollectible"
	description = "Questline: Deal damage with 2 spells. Reward: Tavish, Master Marksman"
	name_CN = "干掉他们"
	numNeeded, newQuest, reward = 2, None, TavishMasterMarksman
	race, trigBoard = "Questline", Trig_DefendtheDwarvenDistrict

class TaketheHighGround(Quest):
	Class, name = "Hunter", "Take the High Ground"
	requireTarget, mana, effects = False, -1, ""
	index = "STORMWIND~Hunter~Spell~0~~Take the High Ground~~Questline~Legendary"
	description = "Questline: Deal damage with 2 spells. Reward: Set the Cost of your Hero Power to (0)"
	name_CN = "占据高地"
	numNeeded, newQuest, reward = 2, KnockEmDown, None
	race, trigBoard = "Questline", Trig_DefendtheDwarvenDistrict
	def questEffect(self, game, ID):
		ManaMod(game.powers[ID], to=0).applies()

class DefendtheDwarvenDistrict(Quest):
	Class, name = "Hunter", "Defend the Dwarven District"
	requireTarget, mana, effects = False, 1, ""
	index = "STORMWIND~Hunter~Spell~1~~Defend the Dwarven District~~Questline~Legendary"
	description = "Questline: Deal damage with 2 spells. Reward: Your Hero Power can target minions"
	name_CN = "保卫矮人区"
	numNeeded, newQuest, reward = 2, TaketheHighGround, None
	race, trigBoard = "Questline", Trig_DefendtheDwarvenDistrict
	def questEffect(self, game, ID):
		self.giveEnchant(game.powers[ID], effGain="Can Target Minions", name=DefendtheDwarvenDistrict)


class LeatherworkingKit(Weapon):
	Class, name, description = "Hunter", "Leatherworking Kit", "After three friendly Beasts die, draw a Beast and give it +1/+1. Lose 1 Durability"
	mana, attack, durability, effects = 1, 0, 3, ""
	index = "STORMWIND~Hunter~Weapon~1~0~3~Leatherworking Kit"
	name_CN = "制皮工具"
	trigBoard = Trig_LeatherworkingKit


class AimedShot(Spell):
	Class, school, name = "Hunter", "", "Aimed Shot"
	requireTarget, mana, effects = True, 3, ""
	index = "STORMWIND~Hunter~Spell~3~~Aimed Shot"
	description = "Deal 3 damage. Your next Hero Power deals two more damage"
	name_CN = "瞄准射击"
	def text(self): return self.calcDamage(3)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.dealsDamage(target, self.calcDamage(3))
			self.Game.powers[self.ID].getsEffect("Power Damage", amount=2)
			AimedShot_Effect(self.Game, self.ID).connect()
		return target


class RammingMount(Spell):
	Class, school, name = "Hunter", "", "Ramming Mount"
	requireTarget, mana, effects = True, 3, ""
	index = "STORMWIND~Hunter~Spell~3~~Ramming Mount"
	description = "Give a minion +2/+2 and Immune while attacking. When it dies, summon a Ram"
	name_CN = "山羊坐骑"
	def available(self):
		return self.selectableMinionExists()
	
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.giveEnchant(target, 2, 2, trigs=((Trig_TavishsRam, "TrigBoard", target.onBoard), 
													(Death_RammingMount, "Deathrattle", target.onBoard)), name=RammingMount)
		return target

class TavishsRam(Minion):
	Class, race, name = "Hunter", "Beast", "Tavish's Ram"
	mana, attack, health = 2, 2, 2
	index = "STORMWIND~Hunter~Minion~2~2~2~Beast~Tavish's Ram~Uncollectible"
	requireTarget, effects, description = False, "", "Immune while attacking"
	name_CN = "塔维什的山羊"
	trigBoard = Trig_TavishsRam


class StormwindPiper(Minion):
	Class, race, name = "Hunter", "Demon", "Stormwind Piper"
	mana, attack, health = 3, 1, 6
	index = "STORMWIND~Hunter~Minion~3~1~6~Demon~Stormwind Piper"
	requireTarget, effects, description = False, "", "After this minion attacks, give your Beasts +1/+1"
	name_CN = "暴风城吹笛人"
	trigBoard = Trig_StormwindPiper


class RodentNest(Minion):
	Class, race, name = "Hunter", "", "Rodent Nest"
	mana, attack, health = 4, 2, 2
	index = "STORMWIND~Hunter~Minion~4~2~2~~Rodent Nest~Deathrattle"
	requireTarget, effects, description = False, "", "Deathrattle: Summon five 1/1 Rats"
	name_CN = "老鼠窝"
	deathrattle = Death_RodentNest


class ImportedTarantula(Minion):
	Class, race, name = "Hunter", "Beast", "Imported Tarantula"
	mana, attack, health = 5, 4, 5
	index = "STORMWIND~Hunter~Minion~5~4~5~Beast~Imported Tarantula~Deathrattle~Tradeable"
	requireTarget, effects, description = False, "", "Tradeable. Deathrattle: Summon two 1/1 Spiders with Poisonous and Rush"
	name_CN = "进口狼蛛"
	deathrattle = Death_ImportedTarantula


class InvasiveSpiderling(Minion):
	Class, race, name = "Hunter", "Beast", "Invasive Spiderling"
	mana, attack, health = 2, 1, 1
	index = "STORMWIND~Hunter~Minion~2~1~1~Beast~Invasive Spiderling~Poisonous~Rush~Uncollectible"
	requireTarget, effects, description = False, "Poisonous,Rush", "Poisonous, Rush"
	name_CN = "入侵的蜘蛛"


class TheRatKing(Minion):
	Class, race, name = "Hunter", "Beast", "The Rat King"
	mana, attack, health = 5, 5, 5
	index = "STORMWIND~Hunter~Minion~5~5~5~Beast~The Rat King~Rush~Deathrattle~Legendary"
	requireTarget, effects, description = False, "Rush", "Rush. Deathrattle: Go Dormant. Revive after 5 friendly minions die"
	name_CN = "鼠王"
	deathrattle = Death_TheRatKing

class DormantRatKing(Dormant):
	Class, school, name = "Hunter", "", "Dormant Rat King"
	description = "Restore 5 Health to awaken"
	name_CN = "沉睡的鼠王"
	trigBoard = Trig_DormantRatKing


class RatsofExtraordinarySize(Spell):
	Class, school, name = "Hunter", "", "Rats of Extraordinary Size"
	requireTarget, mana, effects = False, 6, ""
	index = "STORMWIND~Hunter~Spell~6~~Rats of Extraordinary Size"
	description = "Summon seven 1/1 Rats. Any that can't fit on the battlefield go to your hand with +4/+4"
	name_CN = "硕鼠成群"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		size = self.Game.space(self.ID)
		if minions2Board := [Rat(self.Game, self.ID) for i in range(size)]: self.summon(minions2Board)
		if minions2Hand := [Rat(self.Game, self.ID) for i in range(7-size)]:
			self.AOE_GiveEnchant(minions2Hand, 4, 4, name=RatsofExtraordinarySize)
			self.addCardtoHand(minions2Hand, self.ID)


class Rat(Minion):
	Class, race, name = "Hunter", "Beast", "Rat"
	mana, attack, health = 1, 1, 1
	index = "STORMWIND~Hunter~Minion~1~1~1~Beast~Rat~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "老鼠"


"""Mage Cards"""
class HotStreak(Spell):
	Class, school, name = "Mage", "Fire", "Hot Streak"
	requireTarget, mana, effects = False, 0, ""
	index = "STORMWIND~Mage~Spell~0~Fire~Hot Streak"
	description = "Your next Fire spell costs (2) less"
	name_CN = "炽热连击"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		GameManaAura_HotStreak(self.Game, self.ID).auraAppears()


class FirstFlame(Spell):
	Class, school, name = "Mage", "Fire", "First Flame"
	requireTarget, mana, effects = True, 1, ""
	index = "STORMWIND~Mage~Spell~1~Fire~First Flame"
	description = "Deal 2 damage to a minion. Add a Second Flame to your hand"
	name_CN = "初始之火"
	def available(self):
		return self.selectableMinionExists()
	
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard
	
	def text(self): return self.calcDamage(2)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.dealsDamage(target, self.calcDamage(2))
			self.addCardtoHand(SecondFlame, self.ID)
		return target


class SecondFlame(Spell):
	Class, school, name = "Mage", "Fire", "Second Flame"
	requireTarget, mana, effects = True, 1, ""
	index = "STORMWIND~Mage~Spell~1~Fire~Second Flame~Uncollectible"
	description = "Deal 2 damage to a minion"
	name_CN = "传承之火"
	def available(self):
		return self.selectableMinionExists()
	
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard
	
	def text(self): return self.calcDamage(2)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.dealsDamage(target, self.calcDamage(2))
		return target


class ArcanistDawngrasp(Minion):
	Class, race, name = "Mage", "", "Arcanist Dawngrasp"
	mana, attack, health = 5, 7, 7
	index = "STORMWIND~Mage~Minion~5~7~7~~Arcanist Dawngrasp~Battlecry~Legendary~Uncollectible"
	requireTarget, effects, description = False, "", "Battlecry: For the rest of the game, you have Spell Damage +3"
	name_CN = "奥术师晨拥"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.heroes[self.ID].getsEffect("Spell Damage", amount=3)
		ArcanistDawngrasp_Effect(self.Game, self.ID).connect()

class ReachthePortalRoom(Quest):
	Class, name = "Mage", "Reach the Portal Room"
	requireTarget, mana, effects = False, -1, ""
	index = "STORMWIND~Mage~Spell~0~~Reach the Portal Room~~Questline~Legendary~Uncollectible"
	description = "Questline: Cast a Fire, Frost and Arcane spell. Reward: Arcanist Dawngrasp"
	name_CN = "抵达传送大厅"
	numNeeded, newQuest, reward = 3, None, ArcanistDawngrasp
	race, trigBoard = "Questline", Trig_SorcerersGambit

class StallforTime(Quest):
	Class, name = "Mage", "Stall for Time"
	requireTarget, mana, effects = False, -1, ""
	index = "STORMWIND~Mage~Spell~0~~Stall for Time~~Questline~Legendary~Uncollectible"
	description = "Questline: Cast a Fire, Frost and Arcane spell. Reward: Discover one"
	name_CN = "拖延时间"
	numNeeded, newQuest, reward = 3, ReachthePortalRoom, None
	race, trigBoard = "Questline", Trig_SorcerersGambit
	def questEffect(self, game, ID):
		self.discoverandGenerate_MultiplePools(StallforTime, '', poolsFunc=lambda: SorcerersGambit.decidePools(self))

class SorcerersGambit(Quest):
	Class, school, name = "Mage", "", "Sorcerer's Gambit"
	requireTarget, mana, effects = False, 1, ""
	index = "STORMWIND~Mage~Spell~1~~Sorcerer's Gambit~~Questline~Legendary"
	description = "Questline: Cast a Fire, Frost and Arcane spell. Reward: Draw a spell"
	name_CN = "巫师的计策"
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

	def questEffect(self, game, ID):
		self.drawCertainCard(lambda card: card.category == "Spell")
		
	def decidePools(self):
		Class = classforDiscover(self)
		return [self.rngPool("Fire Spells as " + Class),
		 		self.rngPool("Frost Spells as " + Class),
		 		self.rngPool("Arcane Spells as " + Class)]


class CelestialInkSet(Weapon):
	Class, name, description = "Mage", "Celestial Ink Set", "After you spend 5 Mana on spells, reduce the Cost of a spell in your hand by (5)"
	mana, attack, durability, effects = 2, 0, 2, ""
	index = "STORMWIND~Mage~Weapon~2~0~2~Celestial Ink Set"
	name_CN = "星空墨水套装"
	trigBoard = Trig_CelestialInkSet		


class Ignite(Spell):
	Class, school, name = "Mage", "Fire", "Ignite"
	requireTarget, mana, effects = True, 2, ""
	index = "STORMWIND~Mage~Spell~2~Fire~Ignite~2"
	description = "Deal 2 damgae. Shuffle an Ignite into your deck that deals one more damage"
	name_CN = "点燃"
	baseDamage = 2
	def text(self): return self.calcDamage(type(self).baseDamage)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			base = type(self).baseDamage
			self.dealsDamage(target, self.calcDamage(base))
			newBaseDamage = base + 1
			newIndex = "STORMWIND~Mage~2~Spell~Fire~Ignite~%d~Uncollectible"%newBaseDamage
			subclass = type("Ignite__%d"%newBaseDamage, (Ignite, ),
							{"index": newIndex, "description": "Deal %d damage. Shuffle an Ignite into your deck that deals one more damage"%newBaseDamage,
							"baseDamage": newBaseDamage}
							)
			self.shuffleintoDeck(subclass(self.Game, self.ID))
		return target
	
	
class PrestorsPyromancer(Minion):
	Class, race, name = "Mage", "", "Prestor's Pyromancer"
	mana, attack, health = 2, 2, 3
	index = "STORMWIND~Paladin~Minion~2~2~3~~Prestor's Pyromancer~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Your next Fire spell has Spell Damage +2"
	name_CN = "普瑞斯托的炎术师"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.heroes[self.ID].getsEffect("Fire Spell Damage", amount=2)
		PrestorsPyromancer_Effect(self.Game, self.ID).connect()


class FireSale(Spell):
	Class, school, name = "Mage", "Fire", "Fire Sale"
	requireTarget, mana, effects = False, 4, ""
	index = "STORMWIND~Mage~Spell~4~Fire~Fire Sale~Tradeable"
	description = "Tradeable. Deal 3 damage to all minions"
	name_CN = "火热促销"
	def text(self): return self.calcDamage(3)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = self.calcDamage(3)
		targets = self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)
		self.AOE_Damage(targets, [damage] * len(targets))


class SanctumChandler(Minion):
	Class, race, name = "Mage", "Elemental", "Sanctum Chandler"
	mana, attack, health = 5, 4, 5
	index = "STORMWIND~Mage~Minion~5~4~5~Elemental~Sanctum Chandler"
	requireTarget, effects, description = False, "", "After you cast a Fire spell, draw a spell"
	name_CN = "圣殿蜡烛商"
	trigBoard = Trig_SanctumChandler


class ClumsyCourier(Minion):
	Class, race, name = "Mage", "", "Clumsy Courier"
	mana, attack, health = 7, 4, 5
	index = "STORMWIND~Mage~Minion~7~4~5~~Clumsy Courier~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Cast the highest Cost spell from your hand"
	name_CN = "笨拙的信使"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if indices := pickHighestCostIndices(self.Game.Hand_Deck.hands[self.ID], func=lambda card: card.category == "Spell"):
			self.Game.Hand_Deck.extractfromHand(numpyChoice(indices), self.ID)[0].cast()


class GrandMagusAntonidas(Minion):
	Class, race, name = "Mage", "", "Grand Magus Antonidas"
	mana, attack, health = 8, 6, 6
	index = "STORMWIND~Mage~Minion~8~6~6~~Grand Magus Antonidas~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: If you've cast a Fire spell on each of your last three turns, cast 3 Fireballs at random enemies. (0/3)"
	name_CN = "大魔导师安东尼达斯"
	
	def effCanTrig(self):
		cardsEachTurn = self.Game.Counters.cardsPlayedEachTurn[self.ID]
		self.effectViable = len(cardsEachTurn) > 3 and all(any(card.school == "Fire" for card in cardsEachTurn[i]) for i in (-2, -3, -4))
	
	def	text(self):
		cardsEachTurn = self.Game.Counters.cardsPlayedEachTurn[self.ID]
		turns_Indices = [-i for i in range(2, min(4, len(cardsEachTurn)))]
		return "%d/3"%sum(any(card.school == "Fire" for card in cardsEachTurn[i]) for i in turns_Indices)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		cardsEachTurn = self.Game.Counters.cardsPlayedEachTurn[self.ID]
		if len(cardsEachTurn) > 3 and all(any(card.school == "Fire" for card in cardsEachTurn[i]) for i in (-2, -3, -4)):
			for num in range(3):
				objs = self.Game.charsAlive(3-self.ID)
				if objs: Fireball(self.Game, self.ID).cast(func=lambda obj: obj.ID != self.ID)
				else: break
	

"""Paladin Cards"""
class BlessedGoods(Spell):
	Class, school, name = "Paladin", "Holy", "Blessed Goods"
	requireTarget, mana, effects = False, 1, ""
	index = "STORMWIND~Paladin~Spell~1~Holy~Blessed Goods"
	description = "Discover a Secret, Weapon, or Divine Shield minion"
	name_CN = "受祝福的货物"
	poolIdentifier = "Divine Shield Minions as Paladin"
	@classmethod
	def generatePool(cls, pools):
		classes, lists = [], []
		for Class in pools.Classes:
			secrets = [card for card in pools.ClassCards[Class] if card.race == "Secret"]
			if secrets:
				classes.append(Class + " Secrets")
				lists.append(secrets)
		neutralWeapons = [card for card in pools.NeutralCards if card.category == "Weapon"]
		for Class in pools.Classes:
			weapons = neutralWeapons + [card for card in pools.ClassCards[Class] if card.category == "Weapon"]
			classes.append("Weapons as "+Class)
			lists.append(weapons)
		neutralDivineShields = [card for card in pools.NeutralCards if "~Divine Shield~" in card.index]
		for Class in pools.Classes:
			minions = neutralDivineShields + [card for card in pools.ClassCards[Class] if "~Divine Shield~" in card.index]
			classes.append("Divine Shield as " + Class)
			lists.append(minions)
		return classes, lists
	
	def decidePool(self):
		Class = classforDiscover(self)
		HeroClass = self.Game.heroes[self.ID].Class
		key = HeroClass + " Secrets" if HeroClass in ["Hunter", "Mage", "Paladin", "Rogue"] else "Paladin Secrets"
		return [self.rngPool(key), self.rngPool("Weapons as " + Class), self.rngPool("Divine Shield as " + Class)]
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverandGenerate_MultiplePools(BlessedGoods, comment, poolsFunc=lambda : BlessedGoods.decidePool(self))
	

class PrismaticJewelKit(Weapon):
	Class, name, description = "Paladin", "Prismatic Jewel Kit", "After a friendly minion loses Divine Shield, give minions in your hand +1/+1. Lose 1 Durability"
	mana, attack, durability, effects = 1, 0, 3, ""
	index = "STORMWIND~Paladin~Weapon~1~0~3~Prismatic Jewel Kit"
	name_CN = "棱彩珠宝工具"
	trigBoard = Trig_PrismaticJewelKit


class LightbornCariel(Minion):
	Class, race, name = "Paladin", "", "Lightborn Cariel"
	mana, attack, health = 5, 7, 7
	index = "STORMWIND~Paladin~Minion~5~7~7~~Lightborn Cariel~Battlecry~Legendary~Uncollectible"
	requireTarget, effects, description = False, "", "Battlecry: For the rest of the game, your Silver Hand Recruits have +2/+2"
	name_CN = "圣光化身凯瑞尔"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		GameAura_LightbornCariel(self.Game, self.ID).auraAppears()

class AvengetheFallen(Quest):
	Class, name = "Paladin", "Pave the Way"
	requireTarget, mana, effects = False, -1, ""
	index = "STORMWIND~Paladin~Spell~0~~Pave the Way~~Questline~Legendary~Uncollectible"
	description = "Questline: Play 3 different 1-Cost cards. Reward: Lightborn Cariel"
	name_CN = "为逝者复仇"
	numNeeded, newQuest, reward = 3, None, LightbornCariel
	race, trigBoard = "Questline", Trig_RisetotheOccasion

class PavetheWay(Quest):
	Class, name = "Paladin", "Pave the Way"
	requireTarget, mana, effects = False, -1, ""
	index = "STORMWIND~Paladin~Spell~0~~Pave the Way~~Questline~Legendary~Uncollectible"
	description = "Questline: Play 3 different 1-Cost cards. Reward: Upgrade your Hero Power"
	name_CN = "荡平道路"
	numNeeded, newQuest, reward = 3, AvengetheFallen, None
	race, trigBoard = "Questline", Trig_RisetotheOccasion
	def questEffect(self, game, ID):
		power = game.powers[ID]
		if type(power) in Basicpowers:
			Upgradedpowers[Basicpowers.index(type(power))](game, ID).replacePower()

class RisetotheOccasion(Quest):
	Class, name = "Paladin", "Rise to the Occasion"
	requireTarget, mana, effects = False, 1, ""
	index = "STORMWIND~Paladin~Spell~1~~Rise to the Occasion~~Questline~Legendary"
	description = "Questline: Play 3 different 1-Cost cards. Reward: Equip a 1/4 Light's Justice"
	name_CN = "挺身而出"
	numNeeded, newQuest, reward = 3, PavetheWay, None
	race, trigBoard = "Questline", Trig_RisetotheOccasion
	def questEffect(self, game, ID):
		self.equipWeapon(LightsJustice(game, ID))


class NobleMount(Spell):
	Class, school, name = "Paladin", "", "Noble Mount"
	requireTarget, mana, effects = True, 2, ""
	index = "STORMWIND~Paladin~Spell~2~~Noble Mount"
	description = "Give a minion +1/+1 and Divine Shield. When it dies, summon a Warhorse"
	name_CN = "神圣坐骑"
	
	def available(self):
		return self.selectableMinionExists()
	
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.giveEnchant(target, 1, 1, effGain="Divine Shield", trig=Death_NobleMount, trigType="Deathrattle", connect=target.onBoard, name=NobleMount)
		return target

class CarielsWarhorse(Minion):
	Class, race, name = "Paladin", "Beast", "Cariel's Warhorse"
	mana, attack, health = 1, 1, 1
	index = "STORMWIND~Paladin~Minion~1~1~1~Beast~Cariel's Warhorse~Divine Shield~Uncollectible"
	requireTarget, effects, description = False, "Divine Shield", "Divine Shield"
	name_CN = "卡瑞尔的战马"
	
	
class CityTax(Spell):
	Class, school, name = "Paladin", "", "City Tax"
	requireTarget, mana, effects = False, 2, "Lifesteal"
	index = "STORMWIND~Paladin~Spell~2~~City Tax~Lifesteal~Tradeable"
	description = "Tradeable. Lifesteal. Deal 1 damage to all enemy minions"
	name_CN = "城建税"
	def text(self): return self.calcDamage(1)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = self.calcDamage(1)
		targets = self.Game.minionsonBoard(3-self.ID)
		self.AOE_Damage(targets, [damage] * len(targets))
	
	
class AllianceBannerman(Minion):
	Class, race, name = "Paladin", "", "Alliance Bannerman"
	mana, attack, health = 3, 2, 2
	index = "STORMWIND~Paladin~Minion~3~2~2~~Alliance Bannerman~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Draw a minion. Give minions in your hand +1/+1"
	name_CN = "联盟旗手"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.drawCertainCard(lambda card: card.category == "Minion")
		self.AOE_GiveEnchant([card for card in self.Game.Hand_Deck.hands[self.ID] if card.category == "Minion"],
							1, 1, name=AllianceBannerman, add2EventinGUI=False)


class CatacombGuard(Minion):
	Class, race, name = "Paladin", "", "Catacomb Guard"
	mana, attack, health = 3, 1, 4
	index = "STORMWIND~Paladin~Minion~3~1~4~~Catacomb Guard~Lifesteal~Battlecry"
	requireTarget, effects, description = True, "Lifesteal", "Lifesteal. Battlecry: Deal damage equal to this minin's Attack to an enemy minion"
	name_CN = "古墓卫士"
	
	def targetExists(self, choice=0):
		return self.selectableEnemyMinionExists()
	
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.ID != self.ID and target.onBoard
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and self.attack > 0:
			self.dealsDamage(target, self.attack)


class LightbringersHammer(Weapon):
	Class, name, description = "Paladin", "Lightbringer's Hammer", "Lifesteal. Can't attack heroes"
	mana, attack, durability, effects = 3, 3, 2, "Lifesteal,Can't Attack Heroes"
	index = "STORMWIND~Paladin~Weapon~3~3~2~Lightbringer's Hammer~Lifesteal"
	name_CN = "光明使者之锤"
	
	
class FirstBladeofWrynn(Minion):
	Class, race, name = "Paladin", "", "First Blade of Wrynn"
	mana, attack, health = 4, 3, 5
	index = "STORMWIND~Paladin~Minion~4~3~5~~First Blade of Wrynn~Divine Shield~Battlecry"
	requireTarget, effects, description = False, "Divine Shield", "Divine Shield. Battlecry: Gain Rush if this has at least 4 Attack"
	name_CN = "乌瑞恩首席剑士"
	def effCanTrig(self):
		self.effectViable = self.attack > 3
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.attack > 3: self.giveEnchant(self, "Rush", name=FirstBladeofWrynn)


class HighlordFordragon(Minion):
	Class, race, name = "Paladin", "", "Highlord Fordragon"
	mana, attack, health = 6, 5, 5
	index = "STORMWIND~Paladin~Minion~6~5~5~~Highlord Fordragon~Divine Shield~Legendary"
	requireTarget, effects, description = False, "Divine Shield", "Divine Shield. After a friendly minion loses Divine Shield, give a minion in your hand +5/+5"
	name_CN = "大领主弗塔根"
	trigBoard = Trig_HighlordFordragon


"""Priest Cards"""
class CalloftheGrave(Spell):
	Class, school, name = "Priest", "Shadow", "Call of the Grave"
	requireTarget, mana, effects = False, 1, ""
	index = "STORMWIND~Priest~Spell~1~Shadow~Call of the Grave"
	description = "Discover a Deathrattle minion. If you have enough Mana to play it, trigger its Deathrattle"
	name_CN = "墓园召唤"
	poolIdentifier = "Deathrattle Minions as Priest"
	@classmethod
	def generatePool(cls, pools):
		classCards = {s: [card for card in pools.ClassCards[s] if card.category == "Minion" and "~Deathrattle" in card.index] for s in pools.Classes}
		classCards["Neutral"] = [card for card in pools.NeutralCards if card.category == "Minion" and "~Deathrattle" in card.index]
		return ["Deathrattle Minions as " + Class for Class in pools.Classes], \
			   [classCards[Class] + classCards["Neutral"] for Class in pools.Classes]
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverandGenerate(CalloftheGrave, comment, lambda : self.rngPool("Deathrattle Minions as " + classforDiscover(self)))
	
	def discoverDecided(self, option, case, info_RNGSync=None, info_GUISync=None):
		self.handleDiscoverGeneratedCard(option, case, info_RNGSync, info_GUISync)
		if option.mana <= self.Game.Manas.manas[self.ID]:
			for trig in option.deathrattles: trig.trig("TrigDeathrattle", self.ID, None, option, option.attack, "")


class XyrellatheSanctified(Minion):
	Class, race, name = "Priest", "", "Xyrella, the Sanctified"
	mana, attack, health = 5, 7, 7
	index = "STORMWIND~Priest~Minion~5~7~7~~Xyrella, the Sanctified~Battlecry~Legendary~Uncollectible"
	requireTarget, effects, description = False, "", "Battlecry: Shuffle the Purifid Shard into your deck"
	name_CN = "圣徒泽瑞拉"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.shuffleintoDeck(PurifiedShard(self.Game, self.ID))


class IlluminatetheVoid(Quest):
	Class, name = "Priest", "Illuminate the Void"
	requireTarget, mana, effects = False, -1, ""
	index = "STORMWIND~Priest~Spell~0~~Illuminate the Void~~Questline~Legendary~Uncollectible"
	description = "Questline: Play a 7, and 8-Cost card. Reward: Xyrella, the Sanctified"
	name_CN = "照亮虚空"
	numNeeded, newQuest, reward = 2, None, XyrellatheSanctified
	race, trigBoard = "Questline", Trig_IlluminatetheVoid

class DiscovertheVoidShard(Quest):
	Class, name = "Priest", "Discover the Void Shard"
	requireTarget, mana, effects = False, -1, ""
	index = "STORMWIND~Priest~Spell~0~~Discover the Void Shard~~Questline~Legendary~Uncollectible"
	description = "Questline: Play a 5, and 6-Cost card. Reward: Discover a card from your deck"
	name_CN = "发现虚空碎片"
	numNeeded, newQuest, reward = 2, IlluminatetheVoid, None
	race, trigBoard = "Questline", Trig_DiscovertheVoidShard
	def questEffect(self, game, ID):
		self.discoverfromList(SeekGuidance, '')

class SeekGuidance(Quest):
	Class, name = "Priest", "Seek Guidance"
	requireTarget, mana, effects = False, 1, ""
	index = "STORMWIND~Priest~Spell~1~~Seek Guidance~~Questline~Legendary"
	description = "Questline: Play a 2, 3, and 4-Cost card. Reward: Discover a card from your deck"
	name_CN = "寻求指引"
	numNeeded, newQuest, reward = 3, DiscovertheVoidShard, None
	race, trigBoard = "Questline", Trig_SeekGuidance
	def questEffect(self, game, ID):
		self.discoverfromList(SeekGuidance, '')

	def discoverDecided(self, option, case, info_RNGSync=None, info_GUISync=None):
		self.handleDiscoveredCardfromList(option, case, ls=self.Game.Hand_Deck.decks[self.ID],
										  func=lambda index, card: self.Game.Hand_Deck.drawCard(self.ID, index),
										  info_RNGSync=info_RNGSync, info_GUISync=info_GUISync)


class PurifiedShard(Spell):
	Class, school, name = "Priest", "Holy", "Purified Shard"
	requireTarget, mana, effects = False, 1, ""
	index = "STORMWIND~Priest~Spell~10~Holy~Purified Shard~Legendary~Uncollectible"
	description = "Destroy the enemy hero"
	name_CN = "净化的碎片"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.killMinion(self, self.Game.heroes[3-self.ID])


class ShardoftheNaaru(Spell):
	Class, school, name = "Priest", "Holy", "Shard of the Naaru"
	requireTarget, mana, effects = False, 1, ""
	index = "STORMWIND~Priest~Spell~1~Holy~Shard of the Naaru~Tradeable"
	description = "Tradeable. Silence all enemy minions"
	name_CN = "纳鲁碎片"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for minion in self.Game.minionsonBoard(3-self.ID):
			minion.getsSilenced()


class VoidtouchedAttendant(Minion):
	Class, race, name = "Priest", "", "Voidtouched Attendant"
	mana, attack, health = 1, 1, 3
	index = "STORMWIND~Priest~Minion~1~1~3~~Voidtouched Attendant"
	requireTarget, effects, description = False, "", "Both heroes take one extra damage from all source"
	name_CN = "虚触侍从"
	trigBoard = Trig_VoidtouchedAttendant


class ShadowclothNeedle(Weapon):
	Class, name, description = "Priest", "Shadowcloth Needle", "After you cast a Shadow spell, deal 1 damage to all enemies. Lose 1 Durability"
	mana, attack, durability, effects = 2, 0, 3, ""
	index = "STORMWIND~Priest~Weapon~2~0~3~Shadowcloth Needle"
	name_CN = "暗影布缝针"
	trigBoard = Trig_ShadowclothNeedle


class TwilightDeceptor(Minion):
	Class, race, name = "Priest", "", "Twilight Deceptor"
	mana, attack, health = 2, 2, 3
	index = "STORMWIND~Priest~Minion~2~2~3~~Twilight Deceptor~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: If any hero took damage this turn, draw a Shadow spell"
	name_CN = "暮光欺诈者"
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.dmgHeroTookThisTurn[1] + self.Game.Counters.dmgHeroTookThisTurn[2] > 0
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Counters.dmgHeroTookThisTurn[1] + self.Game.Counters.dmgHeroTookThisTurn[2] > 0:
			self.drawCertainCard(lambda card: card.school == "Shadow")


class Psyfiend(Minion):
	Class, race, name = "Priest", "", "Psyfiend"
	mana, attack, health = 3, 3, 4
	index = "STORMWIND~Priest~Minion~3~3~4~~Psyfiend"
	requireTarget, effects, description = False, "", "After you cast a Shadow spell, dead 2 damage to each hero"
	name_CN = "灵能魔"
	trigBoard = Trig_Psyfiend


class VoidShard(Spell):
	Class, school, name = "Priest", "Shadow", "Void Shard"
	requireTarget, mana, effects = True, 4, "Lifesteal"
	index = "STORMWIND~Priest~Spell~4~Shadow~Void Shard~Lifesteal"
	description = "Lifesteal. Deal 4 damage"
	name_CN = "虚空碎片"
	def text(self): return self.calcDamage(4)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.dealsDamage(target, self.calcDamage(4))
		return target
	
	
class DarkbishopBenedictus(Minion):
	Class, race, name = "Priest", "", "Darkbishop Benedictus"
	mana, attack, health = 5, 5, 6
	index = "STORMWIND~Druid~Minion~5~5~6~~Darkbishop Benedictus~Legendary~Start of Game"
	requireTarget, effects, description = False, "", "Start of Game: If the spells in your deck are all Shadow, enter Shadowform"
	name_CN = "黑暗主教本尼迪塔斯"
	def startofGame(self):
		#all([]) returns True
		print("Darkbishop test", all(card.school == "Shadow" for card in self.Game.Hand_Deck.initialDecks[self.ID] if card.category == "Spell"))
		if all(card.school == "Shadow" for card in self.Game.Hand_Deck.initialDecks[self.ID] if card.category == "Spell"):
			MindSpike(self.Game, self.ID).replacePower()
			
			
class ElekkMount(Spell):
	Class, school, name = "Priest", "", "Elekk Mount"
	requireTarget, mana, effects = True, 7, ""
	index = "STORMWIND~Priest~Spell~7~~Elekk Mount"
	description = "Give a minion +4/+7 and Taunt. When it dies, summon an Elekk"
	name_CN = "雷象坐骑"
	def available(self):
		return self.selectableMinionExists()
	
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.giveEnchant(target, 4, 7, effGain="Taunt", trig=Death_ElekkMount, trigType="Deathrattle", connect=target.onBoard, name=ElekkMount)
		return target

class XyrellasElekk(Minion):
	Class, race, name = "Priest", "Beast", "Xyrella's Elekk"
	mana, attack, health = 6, 4, 7
	index = "STORMWIND~Priest~Minion~6~4~7~Beast~Xyrella's Elekk~Taunt~Uncollectible"
	requireTarget, effects, description = False, "Taunt", "Taunt"
	name_CN = "泽瑞拉的雷象"


"""Rogue Cards"""
class FizzflashDistractor(Spell):
	Class, school, name = "Rogue", "", "Fizzflash Distractor"
	requireTarget, mana, effects = True, 1, ""
	index = "STORMWIND~Rogue~Spell~1~~Fizzflash Distractor~Uncollectible"
	description = "Return a minion to its owner's hand. They can't play it next turn"
	name_CN = "声光干扰器"
	
	def available(self):
		return self.selectableEnemyMinionExists()
	
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard and target.ID != self.ID
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and target.onBoard:
			self.Game.returnObj2Hand(target)
			self.giveEnchant(target, effectEnchant=Enchantment(effGain="Unplayable", until=3-self.ID+2, name=FizzflashDistractor))
		return target

class Spyomatic(Minion):
	Class, race, name = "Rogue", "Mech", "Spy-o-matic"
	mana, attack, health = 1, 3, 2
	index = "STORMWIND~Rogue~Minion~1~3~2~Mech~Spy-o-matic~Battlecry~Uncollectible"
	requireTarget, effects, description = False, "", "Battlecry: Look at 3 cards in your opponent's deck. Choose one to put on top"
	name_CN = "间谍机器人"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverfromList(Spyomatic, comment, ls=self.Game.Hand_Deck.decks[3-self.ID])
	
	def discoverDecided(self, option, case, info_RNGSync=None, info_GUISync=None):
		deck = self.Game.Hand_Deck.decks[3-self.ID]
		self.handleDiscoveredCardfromList(option, case, ls=deck,
										  func=lambda index, card: deck.append(deck.pop(index)),
										  info_RNGSync=info_RNGSync, info_GUISync=info_GUISync)
		

class NoggenFogGenerator(Spell):
	Class, school, name = "Rogue", "", "Noggen-Fog Generator"
	requireTarget, mana, effects = True, 1, ""
	index = "STORMWIND~Rogue~Spell~1~~Noggen-Fog Generator~Uncollectible"
	description = "Give a minion +2 Attack and Stealth"
	name_CN = "迷雾发生器"
	
	def available(self):
		return self.selectableMinionExists()
	
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.giveEnchant(target, 2, 0, effGain="Stealth", name=NoggenFogGenerator)
		return target
	
	
class HiddenGyroblade(Weapon):
	Class, name, description = "Rogue", "Hidden Gyroblade", "Deathrattle: Throw this at a random enemy minion"
	mana, attack, durability, effects = 1, 3, 2, ""
	index = "STORMWIND~Rogue~Weapon~1~3~2~Hidden Gyroblade~Deathrattle~Uncollectible"
	name_CN = "隐蔽式旋刃"
	deathrattle = Death_HiddenGyroblade


class UndercoverMole(Minion):
	Class, race, name = "Rogue", "Beast", "Undercover Mole"
	mana, attack, health = 1, 2, 3
	index = "STORMWIND~Rogue~Minion~1~2~3~Beast~Undercover Mole~Stealth~Uncollectible"
	requireTarget, effects, description = False, "Stealth", "Stealth. After this attacks, add a random card to your hand. (From your opponent's class)"
	name_CN = "潜藏的鼹鼠"
	poolIdentifier = "Rogue Cards"
	@classmethod
	def generatePool(cls, pools):
		return ["%s Cards" % Class for Class in pools.Classes], \
			   [pools.ClassCards[Class] for Class in pools.Classes]
	
	trigBoard = Trig_UndercoverMole


SpyGizmos = [FizzflashDistractor, Spyomatic, NoggenFogGenerator, HiddenGyroblade, UndercoverMole]


class SpymasterScabbs(Minion):
	Class, race, name = "Rogue", "", "Spymaster Scabbs"
	mana, attack, health = 1, 7, 7
	index = "STORMWIND~Rogue~Minion~5~7~7~~Spymaster Scabbs~Battlecry~Legendary~Uncollectible"
	requireTarget, effects, description = False, "", "Battlecry: Add one of each Spy Gizmo to your hand"
	name_CN = "间谍大师卡布斯"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.addCardtoHand(SpyGizmos, self.ID)

class MarkedaTraitor(Quest):
	Class, name = "Rogue", "Marked a Traitor"
	requireTarget, mana, effects = False, -1, ""
	index = "STORMWIND~Rogue~Spell~0~~Marked a Traitor~~Questline~Legendary~Uncollectible"
	description = "Questline: Play 2 SI:7 cards. Reward: Spymaster Scabbs"
	name_CN = "标出叛徒"
	numNeeded, newQuest, reward = 2, None, SpymasterScabbs
	race, trigBoard = "Questline", Trig_FindtheImposter

class LearntheTruth(Quest):
	Class, name = "Rogue", "Learn the Truth"
	requireTarget, mana, effects = False, -1, ""
	index = "STORMWIND~Rogue~Spell~0~~Learn the Truth~~Questline~Legendary~Uncollectible"
	description = "Questline: Play 2 SI:7 cards. Reward: Add a Spy Gizmo to your hand"
	name_CN = "了解真相"
	numNeeded, newQuest, reward = 2, MarkedaTraitor, None
	race, trigBoard = "Questline", Trig_FindtheImposter
	def questEffect(self, game, ID):
		self.addCardtoHand(numpyChoice(SpyGizmos), ID)

class FindtheImposter(Quest):
	Class, name = "Rogue", "Find the Imposter"
	requireTarget, mana, effects = False, 1, ""
	index = "STORMWIND~Rogue~Spell~1~~Find the Imposter~~Questline~Legendary"
	description = "Questline: Play 2 SI:7 cards. Reward: Add a Spy Gizmo to your hand"
	name_CN = "探查内鬼"
	numNeeded, newQuest, reward = 2, LearntheTruth, None
	race, trigBoard = "Questline", Trig_FindtheImposter
	def questEffect(self, game, ID):
		self.addCardtoHand(numpyChoice(SpyGizmos), ID)


class SI7Extortion(Spell):
	Class, school, name = "Rogue", "", "SI:7 Extortion"
	requireTarget, mana, effects = True, 1, ""
	index = "STORMWIND~Rogue~Spell~1~~SI:7 Extortion~Tradeable"
	description = "Tradeable. Deal 3 damage to an undamage character"
	name_CN = "军情七处的要挟"
	
	def available(self):
		return self.selectableMinionExists()
	
	def targetCorrect(self, target, choice=0):
		return (target.category == "Minion" or target.category == "Hero") and target.health == target.health_max and target.onBoard
	
	def text(self): return self.calcDamage(3)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.dealsDamage(target, self.calcDamage(3))
		return target


class Garrote(Spell):
	Class, school, name = "Rogue", "", "Garrote"
	requireTarget, mana, effects = False, 2, ""
	index = "STORMWIND~Rogue~Spell~2~~Garrote"
	description = "Deal 2 damage to the enemy hero. Shuffle 3 Bleeds into your deck that deal 2 more when drawn"
	name_CN = "锁喉"
	def text(self): return self.calcDamage(2)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.dealsDamage(self.Game.heroes[3-self.ID], self.calcDamage(2))
		self.shuffleintoDeck([Bleed(self.Game, self.ID) for _ in (0, 1, 2)])


class Bleed(Spell):
	Class, school, name = "Rogue", "", "Bleed"
	requireTarget, mana, effects = False, 1, ""
	index = "STORMWIND~Rogue~Spell~1~~Bleed~Casts When Drawn~Uncollectible"
	description = "Casts When Drawn. Deal 2 damage to the enemy hero"
	name_CN = "流血"
	def text(self): return self.calcDamage(2)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.dealsDamage(self.Game.heroes[3 - self.ID], self.calcDamage(2))


class MaestraoftheMasquerade(Minion):
	Class, race, name = "Rogue", "", "Maestra of the Masquerade"
	mana, attack, health = 2, 3, 2
	index = "STORMWIND~Rogue~Minion~2~3~2~~Maestra of the Masquerade~Legendary"
	requireTarget, effects, description = False, "", "You start the game as different class until you play a Rogue card"
	name_CN = "变装大师"


class CounterfeitBlade(Weapon):
	Class, name, description = "Rogue", "Counterfeit Blade", "Gain a random friendly Deathrattle that triggered this game"
	mana, attack, durability, effects = 4, 4, 2, ""
	index = "STORMWIND~Rogue~Weapon~4~4~2~Counterfeit Blade~Battlecry"
	name_CN = "伪造的匕首"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if deathrattles := self.Game.Counters.deathrattlesTriggered[self.ID]:
			self.giveEnchant(self, trig=numpyChoice(deathrattles), trigType="Deathrattle", connect=self.onBoard)
	

class LoanShark(Minion):
	Class, race, name = "Rogue", "Beast", "Loan Shark"
	mana, attack, health = 3, 3, 4
	index = "STORMWIND~Rogue~Minion~3~3~4~Beast~Loan Shark~Battlecry~Deathrattle"
	requireTarget, effects, description = False, "", "Battlecry: Give your opponent a Coin. Deathrattle: You get two"
	name_CN = "放贷的鲨鱼"
	deathrattle = Death_LoanShark
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.addCardtoHand(TheCoin, 3-self.ID)
	

class SI7Operative(Minion):
	Class, race, name = "Rogue", "", "SI:7 Operative"
	mana, attack, health = 3, 2, 4
	index = "STORMWIND~Rogue~Minion~3~2~4~~SI:7 Operative~Rush"
	requireTarget, effects, description = False, "Rush", "Rush. After this minion attacks a minion, gain Stealth"
	name_CN = "军情七处探员"
	trigBoard = Trig_SI7Operative


class SketchyInformation(Spell):
	Class, school, name = "Rogue", "", "Sketchy Information"
	requireTarget, mana, effects = False, 3, ""
	index = "STORMWIND~Rogue~Spell~3~~Sketchy Information"
	description = "Draw a Deathrattle card that costs (4) or less. Trigger its effect"
	name_CN = "简略情报"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if card := self.drawCertainCard(lambda card: hasattr(card, "deathrattles") and card.deathrattles and card.mana < 5)[0]:
			for trig in card.deathrattles: trig.trig("TrigDeathrattle", self.ID, None, card, card.attack, "")


class SI7Informant(Minion):
	Class, race, name = "Rogue", "", "SI:7 Informant"
	mana, attack, health = 4, 3, 3
	index = "STORMWIND~Rogue~Minion~4~3~3~~SI:7 Informant~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Gain +1/+1 for each SI:7 card you've played this game"
	name_CN = "军情七处线人"
	
	def effCanTrig(self):
		self.effectViable = any("SI:7" in card.index for card in self.Game.Counters.cardsPlayedThisGame[self.ID])
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		num = sum("SI:7" in card.index for card in self.Game.Counters.cardsPlayedThisGame[self.ID])
		if num > 0: self.giveEnchant(self, num, num, name=SI7Informant)


class SI7Assassin(Minion):
	Class, race, name = "Rogue", "", "SI:7 Assassin"
	mana, attack, health = 7, 4, 4
	index = "STORMWIND~Rogue~Minion~7~4~4~~SI:7 Assassin~Combo"
	requireTarget, effects, description = True, "", "Costs (1) less for each SI:7 card you've played this game. Combo: Destroy an enemy minion"
	name_CN = "军情七处刺客"
	trigHand = Trig_SI7Assassin
	def selfManaChange(self):
		if self.inHand:
			self.mana -= sum("SI:7" in card.index for card in self.Game.Counters.cardsPlayedThisGame[self.ID])
			self.mana = max(self.mana, 0)
	
	def needTarget(self, choice=0):
		return self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0
	
	def targetExists(self, choice=0):
		return self.selectableEnemyMinionExists()
	
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0:
			self.Game.killMinion(self, target)
		return target


"""Shaman Cards"""
class StormcallerBrukan(Minion):
	Class, race, name = "Shaman", "", "Stormcaller Bru'kan"
	mana, attack, health = 5, 7, 7
	index = "STORMWIND~Shaman~Minion~5~7~7~~Stormcaller Bru'kan~Battlecry~Legendary~Uncollectible"
	requireTarget, effects, description = False, "", "Battlecry: For the rest of the game, your spells cast twice"
	name_CN = "风暴召唤者布鲁坎"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.effects[self.ID]["Spells x2"] += 1
		StormcallerBrukan_Effect(self.Game, self.ID).connect()

class TametheFlames(Quest):
	Class, name = "Shaman", "Tame the Flames"
	requireTarget, mana, effects = False, -1, ""
	index = "STORMWIND~Shaman~Spell~0~~Tame the Flames~~Questline~Legendary~Uncollectible"
	description = "Questline: Play 3 cards with Overload. Reward: Stormcaller Bru'kan"
	name_CN = "驯服火焰"
	numNeeded, newQuest, reward = 3, None, StormcallerBrukan
	race, trigBoard = "Questline", Trig_CommandtheElements

class StirtheStones(Quest):
	Class, name = "Shaman", "Stir the Stones"
	requireTarget, mana, effects = False, -1, ""
	index = "STORMWIND~Shaman~Spell~0~~Stir the Stones~~Questline~Legendary~Uncollectible"
	description = "Questline: Play 3 cards with Overload. Reward: Summon a 3/3 Elemental with Taunt"
	name_CN = "搬移磐石"
	numNeeded, newQuest, reward = 3, TametheFlames, None
	race, trigBoard = "Questline", Trig_CommandtheElements
	def questEffect(self, game, ID):
		self.summon(LivingEarth(game, ID))

class CommandtheElements(Quest):
	Class, name = "Shaman", "Command the Elements"
	requireTarget, mana, effects = False, 1, ""
	index = "STORMWIND~Shaman~Spell~1~~Command the Elements~~Questline~Legendary"
	description = "Questline: Play 3 cards with Overload. Reward: Unlock your Overloaded Mana Crystals"
	name_CN = "号令元素"
	numNeeded, newQuest, reward = 3, StirtheStones, None
	race, trigBoard = "Questline", Trig_CommandtheElements
	def questEffect(self, game, ID):
		game.Manas.unlockOverloadedMana(ID)

class LivingEarth(Minion):
	Class, race, name = "Shaman", "Elemental", "Living Earth"
	mana, attack, health = 3, 3, 3
	index = "STORMWIND~Shaman~Minion~3~3~3~Elemental~Living Earth~Taunt~Uncollectible"
	requireTarget, effects, description = False, "Taunt", "Taunt"
	name_CN = "活体土石"


class InvestmentOpportunity(Spell):
	Class, school, name = "Shaman", "", "Investment Opportunity"
	requireTarget, mana, effects = False, 1, ""
	index = "STORMWIND~Shaman~Spell~1~~Investment Opportunity"
	description = "Draw an Overload card"
	name_CN = "投资良机"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.drawCertainCard(lambda card: "~Overload" in card.index)


class Overdraft(Spell):
	Class, school, name = "Shaman", "", "Overdraft"
	requireTarget, mana, effects = True, 1, ""
	index = "STORMWIND~Shaman~Spell~1~~Overdraft~Tradeable"
	description = "Tradeable. Unlock your Overloaded Mana Crystals to deal that much damage"
	name_CN = "强行透支"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = self.calcDamage(self.Game.Manas.manasOverloaded[self.ID] + self.Game.Manas.manasLocked[self.ID])
			self.Game.Manas.unlockOverloadedMana(self.ID)
			self.dealsDamage(target, damage)
		return target


class BolnerHammerbeak(Minion):
	Class, race, name = "Shaman", "", "Bolner Hammerbeak"
	mana, attack, health = 2, 1, 4
	index = "STORMWIND~Shaman~Minion~2~1~4~~Bolner Hammerbeak~Legendary"
	requireTarget, effects, description = False, "", "After you play a Battlecry minion, repeat the first Battlecry played this turn"
	name_CN = "伯纳尔·锤喙"
	#打出的第一个战吼随从也可以享受这个重复。重复时的战吼发出者为这个随从。战吼目标随机
	trigBoard = Trig_BolnerHammerbeak	


class AuctionhouseGavel(Weapon):
	Class, name, description = "Shaman", "Auctionhouse Gavel", "After your hero attacks, reduce the Cost of a Battlecry minion in your hand by (1)"
	mana, attack, durability, effects = 2, 2, 2, ""
	index = "STORMWIND~Shaman~Weapon~2~2~2~Auctionhouse Gavel"
	name_CN = "拍卖行木槌"
	trigBoard = Trig_AuctionhouseGavel


class ChargedCall(Spell):
	Class, school, name = "Shaman", "Nature", "Charged Call"
	requireTarget, mana, effects = False, 3, ""
	index = "STORMWIND~Shaman~Spell~3~Nature~Charged Call"
	description = "Discover a 1-Cost minion and summon it. (Upgrade it for each Overload card you played this game)"
	name_CN = "充能召唤"
	poolIdentifier = "Minions as Mage to Summon"
	@classmethod
	def generatePool(cls, pools):
		neutralMinions = [card for card in pools.NeutralCards if card.category == "Minion"]
		classCards = {}
		for Class, cards in pools.ClassCards.items():
			classCards[Class] = [card for card in cards if card.category == "Minion"]
		return ["Minions as %s to Summon"%Class for Class in classCards], \
			   [minions+neutralMinions for minions in classCards.values()]

	def text(self):
		return 1 + min(10, sum("~Overload" in card.index for card in self.Game.Counters.cardsPlayedThisGame[self.ID]))
		
	def decideMinionPool(self, num):
		return self.rngPool("%d-Cost Minions as %s to Summon"%(min(0, num), classforDiscover(self)))
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		num = 1 + sum("~Overload" in card.index for card in self.Game.Counters.cardsPlayedThisGame[self.ID])
		self.discoverandGenerate(ChargedCall, comment, lambda : ChargedCall.decideMinionPool(self, num))
		
	def discoverDecided(self, option, case, info_RNGSync=None, info_GUISync=None):
		self.handleDiscoverGeneratedCard(option, case, info_RNGSync, info_GUISync,
										 func=lambda cardType, card: self.summon(cardType(self.Game, self.ID)))
		

class SpiritAlpha(Minion):
	Class, race, name = "Shaman", "", "Spirit Alpha"
	mana, attack, health = 4, 2, 5
	index = "STORMWIND~Shaman~Minion~4~2~5~~Spirit Alpha"
	requireTarget, effects, description = False, "", "After you play a card with Overload, summon a 2/3 Spirit Wolf with Taunt"
	name_CN = "幽灵狼前锋"
	trigBoard = Trig_SpiritAlpha


class GraniteForgeborn(Minion):
	Class, race, name = "Shaman", "Elemental", "Granite Forgeborn"
	mana, attack, health = 4, 4, 4
	index = "STORMWIND~Shaman~Minion~4~4~4~Elemental~Granite Forgeborn~Rush~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Reduce the Cost of Elementals in your hand and deck by (1)"
	name_CN = "花岗岩熔铸体"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for card in self.Game.Hand_Deck.hands[self.ID]:
			if card.category == "Minion" and "Elemental" in card.race:
				ManaMod(card, by=-1).applies()
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if card.category == "Minion" and "Elemental" in card.race:
				ManaMod(card, by=-1).applies()


class CanalSlogger(Minion):
	Class, race, name = "Shaman", "Elemental", "Canal Slogger"
	mana, attack, health = 4, 6, 4
	index = "STORMWIND~Shaman~Minion~4~6~4~Elemental~Canal Slogger~Rush~Lifesteal~Overload"
	requireTarget, effects, description = False, "Rush,Lifesteal", "Rush, Lifesteal, Overload: (1)"
	name_CN = "运河慢步者"
	overload = 1


class TinyToys(Spell):
	Class, school, name = "Shaman", "", "Tiny Toys"
	requireTarget, mana, effects = False, 6, ""
	index = "STORMWIND~Shaman~Spell~6~~Tiny Toys"
	description = "Summon four random 5-Cost minions. Make them 2/2"
	name_CN = "小巧玩具"
	poolIdentifier = "5-Cost Minions to Summon"
	@classmethod
	def generatePool(cls, pools):
		return "5-Cost Minions to Summon", pools.MinionsofCost[5]
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		minions = [minion(self.Game, self.ID) for minion in numpyChoice(self.rngPool("5-Cost Minions to Summon"), 4, replace=True)]
		self.summon(minions)
		for minion in minions:
			if minion.onBoard: minion.statReset(2, 2, source=type(self))


"""Warlock Cards"""
class BlightbornTamsin(Minion):
	Class, race, name = "Warlock", "", "Blightborn Tamsin"
	mana, attack, health = 5, 7, 7
	index = "STORMWIND~Warlock~Minion~5~7~7~~Blightborn Tamsin~Battlecry~Legendary~Uncollectible"
	requireTarget, effects, description = False, "", "Battlecry: For the rest of the game, damage you take on your turns damages your opponent instead"
	name_CN = "枯萎化身塔姆辛"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		BlightbornTamsin_Effect(self.Game, self.ID).connect()

class CompletetheRitual(Quest):
	Class, name = "Warlock", "Complete the Ritual"
	requireTarget, mana, effects = False, -1, ""
	index = "STORMWIND~Warlock~Spell~0~~Complete the Ritual~~Questline~Legendary~Uncollectible"
	description = "Questline: Take 8 damage on your turns. Reward: Blightborn Tamsin"
	name_CN = "完成仪式"
	numNeeded, newQuest, reward = 8, None, BlightbornTamsin
	race, trigBoard = "Questline", Trig_TheDemonSeed

class EstablishtheLink(Quest):
	Class, name = "Warlock", "Establish the Link"
	requireTarget, mana, effects = False, -1, "Lifesteal"
	index = "STORMWIND~Warlock~Spell~0~~Establish the Link~~Questline~Legendary~Uncollectible"
	description = "Questline: Take 8 damage on your turns. Reward: Lifesteal. Deal 3 damage to the enemy hero"
	name_CN = "建立连接"
	numNeeded, newQuest, reward = 8, CompletetheRitual, None
	race, trigBoard = "Questline", Trig_TheDemonSeed
	def questEffect(self, game, ID):
		damage = self.calcDamage(3)
		self.dealsDamage(game.heroes[3-ID], damage)

class TheDemonSeed(Quest):
	Class, name = "Warlock", "The Demon Seed"
	requireTarget, mana, effects = False, 1, "Lifesteal"
	index = "STORMWIND~Warlock~Spell~1~~The Demon Seed~~Questline~Legendary"
	description = "Questline: Take 8 damage on your turns. Reward: Lifesteal. Deal 3 damage to the enemy hero"
	name_CN = "恶魔之种"
	numNeeded, newQuest, reward = 8, EstablishtheLink, None
	race, trigBoard = "Questline", Trig_TheDemonSeed
	def questEffect(self, game, ID):
		damage = self.calcDamage(3)
		self.dealsDamage(game.heroes[3-ID], damage)


class TouchoftheNathrezim(Spell):
	Class, school, name = "Warlock", "Shadow", "Touch of the Nathrezim"
	requireTarget, mana, effects = True, 1, ""
	index = "STORMWIND~Warlock~Spell~1~Shadow~Touch of the Nathrezim"
	description = "Deal 2 damage to a minion. If it dies, restore 4 Health to your hero"
	name_CN = "纳斯雷兹姆之触"
	
	def available(self):
		return self.selectableMinionExists()
	
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard
	
	def text(self):
		return "%d, %d"%(self.calcDamage(2), self.calcHeal(4))
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.dealsDamage(target, self.calcDamage(2))
			if target.health < 1 or target.dead: self.restoresHealth(self.Game.heroes[self.ID], self.calcHeal(4))
		return target
	
	
class BloodboundImp(Minion):
	Class, race, name = "Warlock", "Demon", "Bloodbound Imp"
	mana, attack, health = 2, 2, 5
	index = "STORMWIND~Warlock~Minion~2~2~5~Demon~Bloodbound Imp"
	requireTarget, effects, description = False, "", "Whenever this attacks, deal 2 damage to your hero"
	name_CN = "血缚小鬼"
	trigBoard = Trig_BloodboundImp


class DreadedMount(Spell):
	Class, school, name = "Warlock", "", "Dreaded Mount"
	requireTarget, mana, effects = True, 3, ""
	index = "STORMWIND~Warlock~Spell~3~~Dreaded Mount"
	description = "Give a minion +1/+1. When it dies, summon an endless Dreadsteed"
	name_CN = "恐惧坐骑"
	def available(self):
		return self.selectableMinionExists()
	
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.giveEnchant(target, 1, 1, trig=Death_TamsinsDreadsteed, trigType="Deathrattle", connect=target.onBoard, name=DreadedMount)
		return target


class TamsinsDreadsteed(Minion):
	Class, race, name = "Warlock", "Demon", "Tamsin's Dreadsteed"
	mana, attack, health = 4, 1, 1
	index = "STORMWIND~Warlock~Minion~4~1~1~Demon~Tamsin's Dreadsteed~Deathrattle~Uncollectible"
	requireTarget, effects, description = False, "", "Deathrattle: At the end of the turn, summon Tamsin's Dreadsteed"
	name_CN = "塔姆辛的恐惧战马"
	deathrattle = Death_TamsinsDreadsteed

class RunedMithrilRod(Weapon):
	Class, name, description = "Warlock", "Runed Mithril Rod", "After you draw 4 cards, reduce the Cost of cards in your hand by (1). Lose 1 Durability"
	mana, attack, durability, effects = 4, 0, 2, ""
	index = "STORMWIND~Warlock~Weapon~4~0~2~Runed Mithril Rod"
	name_CN = "符文秘银杖"
	trigBoard = Trig_RunedMithrilRod


class DarkAlleyPact(Spell):
	Class, school, name = "Warlock", "Shadow", "Dark Alley Pact"
	requireTarget, mana, effects = False, 4, ""
	index = "STORMWIND~Warlock~Spell~4~Shadow~Dark Alley Pact"
	description = "Summon a Fiend with stat equal to your hand size"
	name_CN = "暗巷交易"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		handSize = len(self.Game.Hand_Deck.hands[self.ID])
		if handSize == 1: self.summon(Fiend(self.Game, self.ID))
		elif handSize > 1:
			cost = min(handSize, 10)
			newIndex = "STORMWIND~Warlock~Minion~%d~%d~%d~Demon~Fiend~Uncollectible" % (cost, handSize, handSize)
			subclass = type("Fiend__" + str(handSize), (Fiend,),
							{"mana": cost, "attack": handSize, "health": handSize,
							 "index": newIndex}
							)
			self.summon(subclass(self.Game, self.ID))


class Fiend(Minion):
	Class, race, name = "Warlock", "Demon", "Fiend"
	mana, attack, health = 1, 1, 1
	index = "STORMWIND~Warlock~Minion~1~1~1~Demon~Fiend~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "邪魔"


class DemonicAssault(Spell):
	Class, school, name = "Warlock", "Fel", "Demonic Assault"
	requireTarget, mana, effects = True, 4, ""
	index = "STORMWIND~Warlock~Spell~4~Fel~Demonic Assault"
	description = "Deal 3 damage. Summon two 1/3 Voidwalkers with Taunt"
	name_CN = "恶魔来袭"
	def text(self): return self.calcDamage(3)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.dealsDamage(target, self.calcDamage(3))
			self.summon([Voidwalker(self.Game, self.ID) for _ in (0, 1)])
		return target


class ShadyBartender(Minion):
	Class, race, name = "Warlock", "", "Shady Bartender"
	mana, attack, health = 5, 4, 4
	index = "STORMWIND~Warlock~Minion~5~4~4~~Shady Bartender~Battlecry~Tradeable"
	requireTarget, effects, description = False, "", "Tradeable. Battlecry: Give your Demons +2/+2"
	name_CN = "阴暗的酒保"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.AOE_GiveEnchant(self.Game.minionsonBoard(self.ID, race="Demon"), 2, 2, name=ShadyBartender)
	
	
class Anetheron(Minion):
	Class, race, name = "Warlock", "Demon", "Anetheron"
	mana, attack, health = 6, 8, 6
	index = "STORMWIND~Warlock~Minion~6~8~6~Demon~Anetheron~Legendary"
	requireTarget, effects, description = False, "", "Costs (1) if your hand is full"
	name_CN = "安纳塞隆"
	trigHand = Trig_Anetheron
	def selfManaChange(self):
		if self.inHand and len(self.Game.Hand_Deck.hands[self.ID]) == self.Game.Hand_Deck.handUpperLimit[self.ID]:
			self.mana = 1


class EntitledCustomer(Minion):
	Class, race, name = "Warlock", "", "Entitled Customer"
	mana, attack, health = 6, 3, 2
	index = "STORMWIND~Warlock~Minion~6~3~2~~Entitled Customer~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Deal damage equal to your hand size to all other minions"
	name_CN = "资深顾客"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = len(self.Game.Hand_Deck.hands[self.ID])
		targets = self.Game.minionsonBoard(1, exclude=self) + self.Game.minionsonBoard(2, exclude=self)
		if targets: self.AOE_Damage(targets, [damage] * len(targets))


"""Warrior Cards"""
class Provoke(Spell):
	Class, school, name = "Warrior", "", "Provoke"
	requireTarget, mana, effects = True, 0, ""
	index = "STORMWIND~Warrior~Spell~0~~Provoke~Tradeable"
	description = "Tradeable. Choose a friendly minion. Enemy minions attack it"
	name_CN = "挑衅"
	def available(self):
		return self.selectableFriendlyMinionExists()
	
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.ID == self.ID and target.onBoard
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		game = self.Game
		if target and target.onBoard and target.health > 0 and not target.dead \
			and (minions := game.minionsAlive(3-self.ID)):
			#假设依登场顺序来进行攻击
			for minion in game.objs_SeqSorted(minions)[0]:
				if minion.onBoard and minion.health > 0 and not minion.dead and target.onBoard and target.health > 0 and not target.dead:
					game.battle(minion, target, verifySelectable=False, useAttChance=False, resolveDeath=False, resetRedirTrig=True)
		return target


class CapnRokara(Minion):
	Class, race, name = "Warrior", "Pirate", "Cap'n Rokara"
	mana, attack, health = 5, 7, 7
	index = "STORMWIND~Warrior~Minion~5~7~7~Pirate~Cap'n Rokara~Battlecry~Legendary~Uncollectible"
	requireTarget, effects, description = False, "", "Battlecry: Summon The Juggernaut"
	name_CN = "船长洛卡拉"
	poolIdentifier = "Pirates"
	@classmethod
	def generatePool(cls, pools):
		return ["Pirates", "Warrior Weapons"], [pools.MinionswithRace["Pirate"],
												[card for card in pools.ClassCards["Warrior"] if card.category == "Weapon"]]

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.summonSingle(TheJuggernaut(self.Game, self.ID), self.pos + 1, self)

class SecuretheSupplies(Quest):
	Class, name = "Warrior", "Secure the Supplies"
	requireTarget, mana, effects = False, -1, ""
	index = "STORMWIND~Warrior~Spell~0~~Secure the Supplies~~Questline~Legendary~Uncollectible"
	description = "Questline: Play 2 Pirates. Reward: Cap'n Rokara"
	name_CN = "保证补给"
	numNeeded, newQuest, reward = 2, None, CapnRokara
	race, trigBoard = "Questline", Trig_RaidtheDocks

class CreateaDistraction(Quest):
	Class, name = "Warrior", "Create a Distraction"
	requireTarget, mana, effects = False, -1, ""
	index = "STORMWIND~Warrior~Spell~0~~Create a Distraction~~Questline~Legendary"
	description = "Questline: Play 2 Pirates. Reward: Deal 2 damage to a random enemy twice"
	name_CN = "制造混乱"
	numNeeded, newQuest, reward = 2, SecuretheSupplies, None
	race, trigBoard = "Questline", Trig_RaidtheDocks
	def questEffect(self, game, ID):
		damage = self.calcDamage(2)
		for num in range(2):
			if objs := game.charsAlive(3-ID): self.dealsDamage(numpyChoice(objs), damage)
			else: break

class RaidtheDocks(Quest):
	Class, name = "Warrior", "Raid the Docks"
	requireTarget, mana, effects = False, 1, ""
	index = "STORMWIND~Warrior~Spell~1~~Raid the Docks~~Questline~Legendary"
	description = "Questline: Play 3 Pirates. Reward: Draw a weapon"
	name_CN = "开进码头"
	numNeeded, newQuest, reward = 3, CreateaDistraction, None
	race, trigBoard = "Questline", Trig_RaidtheDocks
	def questEffect(self, game, ID):
		self.drawCertainCard(lambda card: card.category == "Weapon")
		
class TheJuggernaut(Dormant):
	Class, name = "Warlock", "The Juggernaut"
	description = "At the start of your turn, summon a Pirate, equip a Warrior weapon and fire two cannons that deal 2 damage!"
	index = "STORMWIND~Dormant~The Juggernaut~Legendary"
	trigBoard = Trig_TheJuggernaut


class ShiverTheirTimbers(Spell):
	Class, school, name = "Warrior", "", "Shiver Their Timbers!"
	requireTarget, mana, effects = True, 1, ""
	index = "STORMWIND~Warrior~Spell~1~~Shiver Their Timbers!"
	description = "Deal 2 damage to a minion. If you control a Pirate, deal 5 instead"
	name_CN = "海上威胁"
	def available(self):
		return self.selectableMinionExists()
	
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard

	def effCanTrig(self): return any("Pirate" in minion.race for minion in self.Game.minionsonBoard(self.ID))
	def text(self): return "%d, %d"%(self.calcDamage(2), self.calcDamage(5))
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.dealsDamage(target, self.calcDamage(5 if any("Pirate" in minion.race for minion in self.Game.minionsonBoard(self.ID)) else 2))
		return target


class HarborScamp(Minion):
	Class, race, name = "Warrior", "Pirate", "Harbor Scamp"
	mana, attack, health = 2, 2, 2
	index = "STORMWIND~Warrior~Minion~2~2~2~Pirate~Harbor Scamp~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Draw a Pirate"
	name_CN = "港口匪徒"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.drawCertainCard(lambda card: "Pirate" in card.race)


class CargoGuard(Minion):
	Class, race, name = "Warrior", "Pirate", "Cargo Guard"
	mana, attack, health = 3, 2, 4
	index = "STORMWIND~Warrior~Minion~3~2~4~Pirate~Cargo Guard"
	requireTarget, effects, description = False, "", "At the end of your turn, gain 3 Armor"
	name_CN = "货物保镖"
	trigBoard = Trig_CargoGuard


class HeavyPlate(Spell):
	Class, school, name = "Warrior", "", "Heavy Plate"
	requireTarget, mana, effects = False, 3, ""
	index = "STORMWIND~Warrior~Spell~3~~Heavy Plate~Tradeable"
	description = "Tredeable. Gain 8 Armor"
	name_CN = "厚重板甲"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.giveHeroAttackArmor(self.ID, armor=8)


class StormwindFreebooter(Minion):
	Class, race, name = "Warrior", "Pirate", "Stormwind Freebooter"
	mana, attack, health = 3, 3, 4
	index = "STORMWIND~Warrior~Minion~3~3~4~Pirate~Stormwind Freebooter~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Give your hero +2 Attack this turn"
	name_CN = "暴风城海盗"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.giveHeroAttackArmor(self.ID, attGain=2, name=StormwindFreebooter)
	
	
class RemoteControlledGolem(Minion):
	Class, race, name = "Warrior", "Mech", "Remote-Controlled Golem"
	mana, attack, health = 4, 3, 6
	index = "STORMWIND~Warrior~Minion~4~3~6~Mech~Remote-Controlled Golem"
	requireTarget, effects, description = False, "", "After this minion takes damage, shuffle two Golem Parts into your deck. When drawn, summon a 2/1 Mech"
	name_CN = "遥控傀儡"
	trigBoard = Trig_RemoteControlledGolem

class GolemParts(Spell):
	Class, school, name = "Warrior", "", "Golem Parts"
	requireTarget, mana, effects = False, 1, ""
	index = "STORMWIND~Warrior~Spell~1~~Golem Parts~Casts When Drawn~Uncollectible"
	description = "Casts When Drawn. Summon a 2/1 Mech"
	name_CN = "傀儡部件"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon(DamagedGolem(self.Game, self.ID))


class CowardlyGrunt(Minion):
	Class, race, name = "Warrior", "", "Cowardly Grunt"
	mana, attack, health = 6, 6, 2
	index = "STORMWIND~Warrior~Minion~6~6~2~~Cowardly Grunt~Deathrattle"
	requireTarget, effects, description = False, "", "Deathrattle: Summon a minion from your deck"
	name_CN = "怯懦的步兵"
	deathrattle = Death_CowardlyGrunt


class Lothar(Minion):
	Class, race, name = "Warrior", "", "Lothar"
	mana, attack, health = 7, 7, 7
	index = "STORMWIND~Warrior~Minion~7~7~7~~Lothar~Legendary"
	requireTarget, effects, description = False, "", "At the end of your turn, attack a random enemy minion. If it dies, gain +3/+3"
	name_CN = "洛萨"
	trigBoard = Trig_Lothar


"""Miniset"""
#Neutral
class GolakkaGlutton(Minion):
	Class, race, name = "Neutral", "Pirate", "Golakka Glutton"
	mana, attack, health = 3, 2, 3
	index = "STORMWIND~Neutral~Minion~3~2~3~Pirate~Golakka Glutton~Battlecry"
	requireTarget, effects, description = True, "", "Battlecry: Destroy a Beast and gain +1/+1"
	name_CN = "葛拉卡蟹杀手"
	def targetExists(self, choice=0):
		return self.selectableMinionExists()

	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard

	def effCanTrig(self):
		self.effectViable = self.targetExists()

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.Game.killMinion(self, target)
			self.giveEnchant(self, 1, 1, name=GolakkaGlutton)
		return target


class Multicaster(Minion):
	Class, race, name = "Neutral", "", "Multicaster"
	mana, attack, health = 4, 3, 4
	index = "STORMWIND~Neutral~Minion~4~3~4~~Multicaster~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Draw a card for each different spell school you've cast this game"
	name_CN = "多系施法者"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		schools = []
		for card in self.Game.Counters.cardsPlayedThisGame[self.ID]:
			if card.school and card.school not in schools:
				schools.append(card.school)
		for _ in range(len(schools)): self.Game.Hand_Deck.drawCard(self.ID)


class MaddestBomber(Minion):
	Class, race, name = "Neutral", "", "Maddest Bomber"
	mana, attack, health = 8, 9, 8
	index = "STORMWIND~Neutral~Minion~8~9~8~~Maddest Bomber~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Deal 12 damage randomly split among all other characters"
	name_CN = "最疯狂的爆破者"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for _ in range(12):
			if chars := self.Game.charsAlive(self.ID, self) + self.Game.charsAlive(3-self.ID):
				self.dealsDamage(numpyChoice(chars), 1)
			else: break


#Demon Hunter Cards
class CrowsNestLookout(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Crow's Nest Lookout"
	mana, attack, health = 3, 2, 2
	index = "STORMWIND~Demon Hunter~Minion~3~2~2~Demon~Crow's Nest Lookout~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Deal 2 damage to the left and right-most enemy minions"
	name_CN = "鸦巢观察员"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if minions := self.Game.minionsonBoard(3-self.ID): self.AOE_Damage([minions[0], minions[-1]], [2, 2])


class NeedforGreed(Spell):
	Class, school, name = "Demon Hunter", "", "Need for Greed"
	requireTarget, mana, effects = False, 5, ""
	index = "STORMWIND~Demon Hunter~Spell~5~~Need for Greed~Tradeable"
	description = "Tradeable. Draw 3 cards. If drawn this turn, this costs (3)"
	name_CN = "贪婪需求"
	def effCanTrig(self):
		self.effectViable = self.enterHandTurn >= self.Game.numTurn

	def selfManaChange(self):
		if self.inHand and self.enterHandTurn >= self.Game.numTurn:
			self.mana = 3

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for _ in (0, 1, 2): self.Game.Hand_Deck.drawCard(self.ID)
		

class ProvingGrounds(Spell):
	Class, school, name = "Demon Hunter", "", "Proving Grounds"
	requireTarget, mana, effects = False, 6, ""
	index = "STORMWIND~Demon Hunter~Spell~6~~Proving Grounds"
	description = "Summon two minions from your deck. They fight"
	name_CN = "试炼场"
	def available(self):
		return self.Game.space(self.ID) > 0

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if (minion1 := self.try_SummonfromDeck()) and (minion2 := self.try_SummonfromDeck()):
			self.Game.battle(minion1, minion2, verifySelectable=False, useAttChance=False, resolveDeath=False, resetRedirTrig=True)
		

#Druid cards
class SharkForm_Option(Option):
	name, category, description = "Shark Form", "Option_Minion", "Rush"
	mana, attack, health = 1, 3, 1

class SeaTurtleForm_Option(Option):
	name, category, description = "Sea Turtle Form", "Option_Minion", "Taunt"
	mana, attack, health = 1, 1, 3

class DruidoftheReef(Minion):
	Class, race, name = "Druid", "", "Druid of the Reef"
	mana, attack, health = 1, 1, 1
	index = "STORMWIND~Druid~Minion~1~1~1~~Druid of the Reef~ChooseOne"
	requireTarget, effects, description = False, "", "Choose One - Transform into a 3/1 Shark with Rush; or a 1/3 Turtle with Taunt"
	name_CN = "暗礁德鲁伊"
	options = (SharkForm_Option, SeaTurtleForm_Option)

	def played(self, target=None, choice=0, mana=0, posinHand=0, comment=""):
		self.health = self.health_max
		self.appears(firstTime=True)
		if choice < 0: minion = DruidoftheReef_Both(self.Game, self.ID)
		elif choice == 0: minion = DruidoftheReef_Rush(self.Game, self.ID)
		else: minion = DruidoftheReef_Taunt(self.Game, self.ID)
		#抉择变形类随从的入场后立刻变形。
		self.Game.transform(self, minion)
		#在此之后就要引用self.Game.minionPlayed
		self.Game.sendSignal("MinionPlayed", self.ID, self.Game.minionPlayed, None, mana, "", choice)
		self.Game.sendSignal("MinionSummoned", self.ID, self.Game.minionPlayed, None, mana, "")
		self.Game.gathertheDead()
		
class DruidoftheReef_Rush(Minion):
	Class, race, name = "Druid", "Beast", "Druid of the Reef"
	mana, attack, health = 1, 3, 1
	index = "STORMWIND~Druid~Minion~1~3~1~Beast~Druid of the Reef~Rush~Uncollectible"
	requireTarget, effects, description = False, "Rush", "Rush"
	name_CN = "暗礁德鲁伊"

class DruidoftheReef_Taunt(Minion):
	Class, race, name = "Druid", "Beast", "Druid of the Reef"
	mana, attack, health = 1, 1, 3
	index = "STORMWIND~Druid~Minion~1~1~3~Beast~Druid of the Reef~~Taunt~Uncollectible"
	requireTarget, effects, description = False, "Taunt", "Taunt"
	name_CN = "暗礁德鲁伊"

class DruidoftheReef_Both(Minion):
	Class, race, name = "Druid", "Beast", "Druid of the Reef"
	mana, attack, health = 1, 3, 3
	index = "STORMWIND~Druid~Minion~1~3~3~Beast~Druid of the Reef~Rush~Taunt~Uncollectible"
	requireTarget, effects, description = False, "Rush,Taunt", "Rush, Taunt"
	name_CN = "暗礁德鲁伊"


class JerryRigCarpenter(Minion):
	Class, race, name = "Druid", "Pirate", "Jerry Rig Carpenter"
	mana, attack, health = 2, 2, 1
	index = "STORMWIND~Druid~Minion~2~2~1~Pirate~Jerry Rig Carpenter~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Draw a Choose One spell and split it"
	name_CN = "应急木工"
	#不知道是否会保留这个初始法术的费用效果，假设不保留
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		card, mana, entersHand = self.drawCertainCard(lambda card: card.category == "Spell" and type(card).options)
		if entersHand:
			self.Game.Hand_Deck.extractfromHand(card, self.ID)
			self.Game.Hand_Deck.addCardtoHand([option.spell for option in type(card).options], self.ID)


class MoonlitGuidance(Spell):
	Class, school, name = "Druid", "Arcane", "Moonlit Guidance"
	requireTarget, mana, effects = False, 2, ""
	index = "STORMWIND~Druid~Spell~2~Arcane~Moonlit Guidance"
	description = "Discover a copy of a card in your deck. If you play it this turn, draw the original"
	name_CN = "月光指引"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverfromList(MoonlitGuidance, comment)

	def discoverDecided(self, option, case, info_RNGSync=None, info_GUISync=None):
		self.handleDiscoveredCardfromList(option, case, ls=self.Game.Hand_Deck.decks[self.ID],
										  func=lambda index, card: MoonlitGuidance.addCopyandStartTrigEffect(self, card),
										  info_RNGSync=info_RNGSync, info_GUISync=info_GUISync)

	def addCopyandStartTrigEffect(self, card):
		self.addCardtoHand((Copy := card.selfCopy(self.ID, self)), self.ID, byDiscover=True)
		if Copy.inHand and card.inDeck: MoonlitGuidance_Effect(self.Game, self.ID, (card, Copy)).connect()


#Hunter cards
class DoggieBiscuit(Spell):
	Class, school, name = "Hunter", "", "Doggie Biscuit"
	requireTarget, mana, effects = True, 2, ""
	index = "STORMWIND~Hunter~Spell~2~~Doggie Biscuit~Tradeable"
	description = "Tradeable. Give a minion +2/+3. After you Trade this, give a friendly minion Rush"
	name_CN = "狗狗饼干"
	def available(self):
		return self.selectableMinionExists()

	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.giveEnchant(target, 2, 3, name=DoggieBiscuit)
		return target

	def tradeEffect(self):
		if minions:= self.Game.minionsonBoard(self.ID):
			self.giveEnchant(numpyChoice(minions), effGain="Rush", name=DoggieBiscuit)


class MonstrousParrot(Minion):
	Class, race, name = "Hunter", "Beast", "Monstrous Parrot"
	mana, attack, health = 4, 3, 4
	index = "STORMWIND~Hunter~Minion~4~3~4~Beast~Monstrous Parrot~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Repeat the last friendly Deathrattle that triggered"
	name_CN = "应急木工"
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.deathrattlesTriggered[self.ID] != []

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if deathrattles := self.Game.Counters.deathrattlesTriggered[self.ID]:
			deathrattles[-1](self).trig("TrigDeathrattle", self.ID, None, self, self.attack, "")


class DefiasBlastfisher(Minion):
	Class, race, name = "Hunter", "Pirate", "Defias Blastfisher"
	mana, attack, health = 5, 3, 2
	index = "STORMWIND~Hunter~Minion~5~3~2~Pirate~Defias Blastfisher~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Deal 2 damage to a random enemy. Repeat for each of your Beasts"
	name_CN = "迪菲亚炸鱼手"
	def effCanTrig(self):
		self.effectViable = self.Game.minionsonBoard(self.ID, race="Beast") != []

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if objs := self.Game.charsAlive(3-self.ID):
			self.dealsDamage(numpyChoice(objs), 2)
			for _ in range(len(self.Game.minionsonBoard(self.ID, race="Beast"))):
				if objs := self.Game.charsAlive(3-self.ID): self.dealsDamage(numpyChoice(objs), 2)
				else: break


#Mage Cards
class DeepwaterEvoker(Minion):
	Class, race, name = "Mage", "Pirate", "Deepwater Evoker"
	mana, attack, health = 4, 3, 4
	index = "STORMWIND~Mage~Minion~4~3~4~Pirate~Deepwater Evoker~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Draw a spell. Gain Armor equal to its Cost"
	name_CN = "深水唤醒师"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if (mana := self.drawCertainCard(lambda card: card.category == "Spell")[1]) > 0:
			self.giveHeroAttackArmor(self.ID, armor=mana)


class ArcaneOverflow(Spell):
	Class, school, name = "Mage", "Arcane", "Arcane Overflow"
	requireTarget, mana, effects = True, 5, ""
	index = "STORMWIND~Mage~Spell~5~Arcane~Arcane Overflow"
	description = "Deal 8 damage to an enemy minion. Summon a Remnant with stats equal to the excess damage"
	name_CN = "奥术溢爆"
	def available(self):
		return self.selectableEnemyMinionExists()

	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.ID != self.ID and target.onBoard

	def text(self): return self.calcDamage(8)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			excess = (damage := self.calcDamage(8)) - max(0, target.health)
			self.dealsDamage(target, damage)
			if excess:
				if excess == 1: minion = ArcaneRemnant
				else:
					cost = min(excess, 10)
					newIndex = "STORMWIND~Mage~Minion~%d~%d~%d~Elemental~Arcane Remnant~Uncollectible"%(cost, excess, excess)
					minion = type("ArcaneRemnant__" + str(excess), (ArcaneRemnant,),
									{"mana": cost, "attack": excess, "health": excess, "index": newIndex}
									)
				self.summon(minion(self.Game, self.ID))
		return target

class ArcaneRemnant(Minion):
	Class, race, name = "Mage", "Elemental", "Arcane Remnant"
	mana, attack, health = 1, 1, 1
	index = "STORMWIND~Mage~Minion~1~1~1~Elemental~Arcane Remnant~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "奥术残渣"


class GreySageParrot(Minion):
	Class, race, name = "Mage", "Beast", "Grey Sage Parrot"
	mana, attack, health = 8, 6, 6
	index = "STORMWIND~Mage~Minion~8~6~6~Beast~Grey Sage Parrot~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Repeat the last spell you've cast that costs (5) or more"
	name_CN = "灰贤鹦鹉"
	def effCanTrig(self):
		self.effectViable = any(card.category == "Spell" and card.mana > 4 for card in self.Game.Counters.cardsPlayedThisGame[self.ID])

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if spells := [card for card in self.Game.Counters.cardsPlayedThisGame[self.ID] if card.category == "Spell" and card.mana > 4]:
			numpyChoice(spells)(self.Game, self.ID).cast()


#Paladin Cards
class RighteousDefense(Spell):
	Class, school, name = "Paladin", "Holy", "Righteous Defense"
	requireTarget, mana, effects = True, 3, ""
	index = "STORMWIND~Paladin~Spell~3~Holy~Righteous Defense"
	description = "Set a minion's Attack and Health to 1. Give the stats it lost to a minion in your hand"
	name_CN = "正义防御"
	def available(self):
		return self.selectableEnemyMinionExists()

	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			attLost, healthLost = max(target.attack - 1, 0), max(target.health - 1, 0)
			target.statReset(1, 1, source=type(self), name=RighteousDefense)
			if (attLost or healthLost) and (minions := [card for card in self.Game.Hand_Deck.hands[self.ID] if card.category == "Minion"]):
				self.giveEnchant(numpyChoice(minions), attLost, healthLost, name=RighteousDefense, add2EventinGUI=False)
		return target


class SunwingSquawker(Minion):
	Class, race, name = "Paladin", "Beast", "Sunwing Squawker"
	mana, attack, health = 4, 3, 4
	index = "STORMWIND~Paladin~Minion~4~3~4~Beast~Sunwing Parrot~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Repeat the last spell you've cast on a friendly minion on this"
	name_CN = "金翼鹦鹉"
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.spellsonFriendlyMinionsThisGame[self.ID] != []

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if spells := self.Game.Counters.spellsonFriendlyMinionsThisGame[self.ID]:
			numpyChoice(spells)(self.Game, self.ID).cast(target=self)


class WealthRedistributor(Minion):
	Class, race, name = "Paladin", "Pirate", "Wealth Redistributor"
	mana, attack, health = 5, 2, 8
	index = "STORMWIND~Paladin~Minion~5~2~8~Pirate~Wealth Redistributor~Taunt~Battlecry"
	requireTarget, effects, description = False, "Taunt", "Taunt. Battlecry: Swap the Attack of the highest and losest Attack minion"
	name_CN = "分赃专员"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if minions := self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2):
			minions_Highest, minions_Lowest, highest, lowest = [], [], -numpy.inf, numpy.inf
			for minion in minions:
				att = minion.attack
				if att > highest: minions_Highest, highest = [minion], att
				elif att == highest: minions_Highest.append(minion)
				if att < lowest: minions_Lowest, lowest = [minion], att
				elif att == lowest: minions_Lowest.append(minion)
			numpyChoice(minions_Highest).statReset(lowest, source=type(self), name=WealthRedistributor)
			numpyChoice(minions_Lowest).statReset(highest, source=type(self), name=WealthRedistributor)


#Priest Cards
class DefiasLeper(Minion):
	Class, race, name = "Priest", "Pirate", "Defias Leper"
	mana, attack, health = 2, 3, 2
	index = "STORMWIND~Priest~Minion~2~3~2~Pirate~Defias Leper~Battlecry"
	requireTarget, effects, description = True, "", "Battlecry: If you're holding a Shadow spell, deal 2 damage"
	name_CN = "迪菲亚麻风侏儒"
	def needTarget(self, choice=0):
		return any(card.school == "Shadow" for card in self.Game.Hand_Deck.hands[self.ID])

	def effCanTrig(self):
		self.effectViable = any(card.school == "Shadow" for card in self.Game.Hand_Deck.hands[self.ID])

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and any(card.school == "Shadow" for card in self.Game.Hand_Deck.hands[self.ID]):
			self.dealsDamage(target, 2)
		return target


class AmuletofUndying(Spell):
	Class, school, name = "Priest", "Shadow", "Amulet of Undying"
	requireTarget, mana, effects = False, 3, ""
	index = "STORMWIND~Priest~Spell~3~Shadow~Amulet of Undying~Tradeable"
	description = "Tradeable. Resurrect 1 friendly Deathrattle minion. (Upgrades when Traded!)"
	name_CN = "不朽护符"
	def available(self):
		return self.Game.space(self.ID)

	def text(self): return self.progress + 1

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if minions := [minion for minion in self.Game.Counters.minionsDiedThisGame[self.ID] if "~Deathrattle" in minion.index]:
			minions = numpyChoice(minions, min(len(minions), self.progress+1), replace=False)
			self.summon([minion(self.Game, self.ID) for minion in minions])

	def tradeEffect(self):
		self.progress += 1


class Copycat(Minion):
	Class, race, name = "Priest", "Beast", "Copycat"
	mana, attack, health = 3, 3, 4
	index = "STORMWIND~Priest~Minion~3~3~4~Beast~Copycat~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Add a copy of the next card your opponent plays to your hand"
	name_CN = "仿冒猫猫"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		Copycat_Effect(self.Game, self.ID).connect()


#Rogue cards
class BlackwaterCutlass(Weapon):
	Class, name, description = "Rogue", "Blackwater Cutlass", "Tradeable. After you Trade this, reduce the cost of a spell in your hand by (1)"
	mana, attack, durability, effects = 1, 2, 2, ""
	index = "STORMWIND~Rogue~Weapon~1~2~2~Blackwater Cutlass~Tradeable"
	name_CN = "黑水弯刀"
	def tradeEffect(self):
		if cards := self.findCards4ManaReduction(lambda card: card.category == "Spell"):
			ManaMod(numpyChoice(cards), by=-1).applies()


class Parrrley(Spell):
	Class, school, name = "Rogue", "", "Parrrley"
	requireTarget, mana, effects = False, 1, ""
	index = "STORMWIND~Rogue~Spell~1~~Parrrley"
	description = "Swap this for a card in your opponent's deck"
	name_CN = "海盗谈判"
	#Assuming the opponent can see what card you get
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if enemyDeck := self.Game.Hand_Deck.decks[3-self.ID]:
			card = self.Game.Hand_Deck.extractfromDeck((i := numpyRandint(len(enemyDeck))), 3-self.ID, linger=True)[0]
			self.Game.Hand_Deck.addCardtoHand(card, self.ID)
			self.reset(3 - self.ID)
			enemyDeck[i] = self
			self.entersDeck()


#Shaman cards
class BrilliantMacaw(Minion):
	Class, race, name = "Shaman", "Beast", "Brilliant Macaw"
	mana, attack, health = 3, 3, 3
	index = "STORMWIND~Shaman~Minion~3~3~3~Shaman~Brilliant Macaw~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Repeat the last Battlecry you played"
	name_CN = "艳丽的金刚鹦鹉"
	def effCanTrig(self):
		self.effectViable = any("~Battlecry" in card.index for card in self.Game.Counters.cardsPlayedThisGame[self.ID])

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if cards := [card for card in self.Game.Counters.cardsPlayedThisGame[self.ID] if "~Battlecry" in card.index]:
			self.invokeBattlecry(cards[-1])


class Suckerhook(Minion):
	Class, race, name = "Shaman", "Pirate", "Suckerhook"
	mana, attack, health = 4, 3, 6
	index = "STORMWIND~Shaman~Minion~4~3~6~Pirate~Suckerhook"
	requireTarget, effects, description = False, "", "At the end of your turn, transform your weapon into one that costs (1) more"
	name_CN = "吸盘钩手"
	trigBoard = Trig_Suckerhook
	poolIdentifier = "1-Cost Weapons"
	@classmethod
	def generatePool(cls, pools):
		weapons = {}
		for card in pools.cardPool:
			if card.category == "Weapon": add2ListinDict(card, weapons, card.mana)
		return ["%d-Cost Weapons"%cost for cost in weapons.keys()], list(weapons.values())


#Warlock Cards
class ShadowbladeSlinger(Minion):
	Class, race, name = "Warlock", "Pirate", "Shadowblade Slinger"
	mana, attack, health = 1, 2, 1
	index = "STORMWIND~Warlock~Minion~1~2~1~Pirate~Shadowblade Slinger~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: If you've taken damage this turn, deal that much to an enemy minion"
	name_CN = "暗影之刃飞刀手"
	def needTarget(self, choice=0):
		return self.Game.Counters.dmgHeroTookThisTurn[self.ID] > 0

	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.ID != self.ID and target.onBoard

	def effCanTrig(self):
		self.effectViable = self.Game.Counters.dmgHeroTookThisTurn[self.ID] > 0

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and (dmg := self.Game.Counters.dmgHeroTookThisTurn[self.ID]):
			self.dealsDamage(target, dmg)
		return target


class WickedShipment(Spell):
	Class, school, name = "Warlock", "", "Wicked Shipment"
	requireTarget, mana, effects = False, 1, ""
	index = "STORMWIND~Warlock~Spell~1~~Wicked Shipment~Tradeable"
	description = "Tradeable. Summon 2 1/1 Imps. (Upgrades by 2 when Traded!)"
	name_CN = "邪恶船运"
	def text(self): return 2 + self.progress

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon([Imp(self.Game, self.ID) for _ in range(2 + self.progress)])

	def tradeEffect(self):
		self.progress += 2


class Hullbreaker(Minion):
	Class, race, name = "Warlock", "Demon", "Hullbreaker"
	mana, attack, health = 4, 4, 3
	index = "STORMWIND~Warlock~Minion~4~4~3~Demon~Hullbreaker~Battlecry~Deathrattle"
	requireTarget, effects, description = False, "", "Battlecry and Deathrattle: Draw a spell. Your hero takes damage equal to its Cost"
	name_CN = "碎舰恶魔"
	deathrattle = Death_Hullbreaker
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if (mana := self.drawCertainCard(lambda card: card.category == "Spell")[1]) > 0:
			self.Game.heroTakesDamage(self.ID, mana)


#Warrior cards
class MantheCannons(Spell):
	Class, school, name = "Warrior", "", "Man the Cannons"
	requireTarget, mana, effects = True, 2, ""
	index = "STORMWIND~Warrior~Spell~2~~Man the Cannons"
	description = "Deal 3 damage to a minion and 1 damage to all other minions"
	name_CN = "操纵火炮"
	def available(self):
		return self.selectableMinionExists()

	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard

	def text(self): return "%d, %d"%(self.calcDamage(3), self.calcDamage(1))

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			minions = [target] + self.Game.minionsonBoard(target.ID, target) + self.Game.minionsonBoard(3-target.ID)
			damages = [self.calcDamage(3)] + [self.calcDamage(1)] * (len(minions) - 1)
			self.AOE_Damage(minions, damages)


class DefiasCannoneer(Minion):
	Class, race, name = "Warrior", "Pirate", "Defias Cannoneer"
	mana, attack, health = 3, 3, 3
	index = "STORMWIND~Warrior~Minion~3~3~3~Pirate~Defias Cannoneer"
	requireTarget, effects, description = False, "", "After your hero attacks, deal 2 damage to a random enemy twice"
	name_CN = "迪菲亚炮手"
	trigBoard = Trig_DefiasCannoneer


class BlacksmithHammer(Weapon):
	Class, name, description = "Warrior", "Blacksmithing Hammer", "Tradeable. After you Trade this, gain +2 Durability"
	mana, attack, durability, effects = 4, 5, 1, ""
	index = "STORMWIND~Warrior~Weapon~4~5~1~Blacksmithing Hammer~Tradeable"
	name_CN = "铁匠锤"
	def tradeEffect(self):
		self.getsBuffDebuff_inDeck(0, 2, source=type(self), name=BlacksmithHammer)


"""Game TrigEffects and game auras"""
class SigilofAlacrity_Effect(TrigEffect):
	card, trigType = SigilofAlacrity, "TurnStart&OnlyKeepOne"
	def trigEffect(self):
		card, mana, entersHand = self.Game.Hand_Deck.drawCard(self.ID)
		if entersHand: ManaMod(card, by=-1).applies()

class DemonslayerKurtrus_Effect(TrigEffect):
	card, signals, counter, trigType = DemonslayerKurtrus, ("CardEntersHand",), 2, "Conn&TrigAura"
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return target[0].ID == self.ID and comment == "byDrawing"

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		ManaMod(target[0], by=-self.counter).applies()


class SheldrasMoontree_Effect(TrigEffect):
	card, signals, counter, trigType = SheldrasMoontree, ("CardDrawn",), 3, "Conn&TrigAura&OnlyKeepOne"
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

	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return target[0].ID == self.ID

	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrig(signal, ID, subject, target, number, comment):
			if self.Game.GUI: self.Game.GUI.showOffBoardTrig(self.card)
			self.effect(signal, ID, subject, target, number, comment)

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.counter -= 1
		if self.card.btn: self.card.btn.trigAni(self.counter)
		target[0].index += "Casts When Drawn"
		if self.counter < 1: self.disconnect()


class TavishMasterMarksman_Effect(TrigEffect):
	card, signals, trigType = TavishMasterMarksman, ("SpellBeenPlayed",), "Conn&TrigAura&OnlyKeepOne"
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.Game.powers[self.ID].usageCount = 0
		self.Game.powers[self.ID].btn.checkHpr()


class AimedShot_Effect(TrigEffect):
	card, signals, counter, trigType = AimedShot, ("HeroUsedAbility",), 2, "Conn&TrigAura&OnlyKeepOne"
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.Game.powers[self.ID].losesEffect("Power Damage", amount=self.counter)
		self.disconnect()


class GameManaAura_HotStreak(GameManaAura_OneTime):
	card, by = HotStreak, -2
	def applicable(self, target): return target.ID == self.ID and target.school == "Fire"

class PrestorsPyromancer_Effect(TrigEffect):
	card, signals, counter, trigType = PrestorsPyromancer, ("SpellBeenCast",), 2, "Conn&TrigAura&OnlyKeepOne"
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.ID and subject.school == "Fire"

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.Game.heroes[self.ID].losesEffect("Fire Spell Damage", amount=self.counter)
		self.disconnect()

class ArcanistDawngrasp_Effect(TrigEffect):
	card, counter, trigType = ArcanistDawngrasp, 3, "OnlyKeepOne" #For this effect, it is simply an indicator, no need for "Conn&TrigAura"

class GameAura_LightbornCariel(GameAura_AlwaysOn):
	card, attGain, healthGame, counter = LightbornCariel, 2, 2, 2
	def applicable(self, target): return target.name == "Silver Hand Recruit"
	def upgrade(self):
		self.attGain = self.healthGain = self.counter = self.counter + 2
		for receiver in self.receivers:
			receiver.attGain, receiver.healthGain = self.attGain, self.healthGain
			receiver.recipient.calcStat()
		if self.counter and self.card.btn: self.card.btn.trigAni(self.counter)


class SI7Skulker_Effect(TrigEffect):
	card, signals, counter, trigType = SI7Skulker, ("CardEntersHand",), 1, "Conn"
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return target[0].ID == self.ID and comment == "byDrawing"

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		ManaMod(target[0], by=-self.counter).applies()
		self.disconnect()

class StormcallerBrukan_Effect(TrigEffect):
	card, trigType = StormcallerBrukan, "OnlyKeepOne" #For this effect, it is simply an indicator, no need for "Conn&TrigAura"

class BlightbornTamsin_Effect(TrigEffect):
	card, signals, trigType = BlightbornTamsin, ("DmgTaker?",), "Conn&TrigAura&OnlyKeepOne"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.on = True

	# number here is a list that holds the damage to be processed
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		if comment == "Reset":  # Assume this can't trigger multiple times in a chain
			self.on = True
			return False
		else: return target[0] == self.Game.heroes[self.ID] and target[0].onBoard and self.Game.turn == self.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		target[0] = self.Game.heroes[3 - self.ID]
		self.on = False

	def assistCreateCopy(self, Copy):
		Copy.on = self.on


class TamsinsDreadsteed_Effect(TrigEffect):
	card, counter, trigType = TamsinsDreadsteed, 1, "TurnEnd&OnlyKeepOne"
	def trigEffect(self):
		self.card.summon([TamsinsDreadsteed(self.Game, self.ID) for i in range(self.counter)])


class MoonlitGuidance_Effect(TrigEffect):
	card, signals, trigType = MoonlitGuidance, ("MinionBeenPlayed", "SpellBeenPlayed", "WeaponBeenPlayed", "HeroBeenPlayed"), "Conn&TurnEnd"
	def __init__(self, Game, ID, cards=()):
		super().__init__(Game, ID)
		self.savedObjs = cards  #tuple (Original card, copy)

	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.savedObjs and subject.ID == self.ID and subject == self.savedObjs[1]

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if self.savedObjs[0] in (deck := self.Game.Hand_Deck.decks[self.ID]):
			self.Game.Hand_Deck.drawCard(self.ID, deck.index(self.savedObjs[0]))
		self.disconnect()

	def assistCreateCopy(self, Copy):
		Copy.savedObjs = tuple(card.createCopy(Copy.Game) for card in self.savedObjs)


class Copycat_Effect(TrigEffect):
	card, signals, trigType = Copycat, ("MinionBeenPlayed", "SpellBeenPlayed", "WeaponBeenPlayed", "HeroBeenPlayed", ), "Conn&TrigAura"
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID != self.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.card.addCardtoHand(type(subject), self.ID)
		self.disconnect()


TrigsDeaths_Stormwind = {Death_ElwynnBoar: (ElwynnBoar, "Deathrattle: If you had 7 Elwynn Boars die this game, equip a 15/3 Sword of a Thousand Truth"),
						Death_MailboxDancer: (MailboxDancer, "Deathrattle: Add a Coin to your opponent's hand"),
						Death_EnthusiasticBanker: (EnthusiasticBanker, "Deathrattle: Add the stored cards to your hand"),
						Death_StubbornSuspect: (StubbornSuspect, "Deathrattle: Summon a random 3-Cost minion"),
						Death_MoargForgefiend: (MoargForgefiend, "Deathrattle: Gain 8 Armor"),
						Death_PersistentPeddler: (PersistentPeddler, "Deathrattle: Summon a Persistent Peddler from your deck"),
						Death_VibrantSquirrel: (VibrantSquirrel, "Deathrattle: Shuffle 4 Acorns into your deck"),
						Death_Composting: (Composting, "Deathrattle: Draw a card"),
						Death_KodoMount: (KodoMount, "Deathrattle: Summon a 4/2 Kodo"),
						Trig_TavishsRam: (TavishsRam, "Immune while attacking"),
						Death_RammingMount: (RammingMount, "Deathrattle: Summon a 2/2 Ram"),
						Death_ImportedTarantula: (ImportedTarantula, "Deathrattle: Summon two 1/1 Spiders with Poisonous and Rush"),
						Death_TheRatKing: (TheRatKing, "Deathrattle: Go dormant. Revive after 5 friendly minions die"),
						Death_RodentNest: (RodentNest, "Deathrattle: Summon five 1/1 Rats"),
						Death_NobleMount: (NobleMount, "Deathrattle: Summon a 1/1 Warhorse"),
						Death_ElekkMount: (ElekkMount, "Deathrattle: Summon a 4/7 Elekk"),
						Death_HiddenGyroblade: (HiddenGyroblade, "Deathrattle: Throw this at a random enemy minion"),
						Death_LoanShark: (LoanShark, "Deathrattle: Add two Coins to your hand"),
						Death_TamsinsDreadsteed: (TamsinsDreadsteed, "Deathrattle: At the end of the turn, summon Tamsin's Dreadsteed"),
						Death_CowardlyGrunt: (CowardlyGrunt, "Deathrattle: Summon a minion from your deck"),
						}

Stormwind_Cards = [
		#Neutral
		ElwynnBoar, SwordofaThousandTruth, Peasant, StockadesGuard, AuctioneerJaxon, DeeprunEngineer, EncumberedPackMule,
		Florist, MailboxDancer, PandarenImporter, SI7Skulker, StockadesPrisoner, EnthusiasticBanker, ImpatientShopkeep,
		NorthshireFarmer, PackageRunner, RustrotViper, TravelingMerchant, TwoFacedInvestor, EntrappedSorceress,
		FlightmasterDungar, Nobleman, Cheesemonger, GuildTrader, RoyalLibrarian, SpiceBreadBaker, StubbornSuspect,
		LionsGuard, StormwindGuard, BattlegroundBattlemaster, CityArchitect, CastleWall, CorneliusRoame, LadyPrestor,
		MoargForgefiend, VarianKingofStormwind, GoldshireGnoll, Treant_Stormwind,
		#Demon Hunter
		FinalShowdown, DemonslayerKurtrus, Metamorfin, SigilofAlacrity, FelBarrage, ChaosLeech, LionsFrenzy, Felgorger,
		PersistentPeddler, IreboundBrute, JaceDarkweaver,
		#Druid
		LostinthePark, GufftheTough, SowtheSoil, Fertilizer, NewGrowth, VibrantSquirrel, Acorn, SatisfiedSquirrel,
		Composting, Wickerclaw, OracleofElune, KodoMount, GuffsKodo, ParkPanther, BestinShell, GoldshellTurtle,
		SheldrasMoontree,
		#Hunter
		DevouringSwarm, DefendtheDwarvenDistrict, TavishMasterMarksman, LeatherworkingKit, AimedShot, RammingMount,
		TavishsRam, StormwindPiper, RodentNest, ImportedTarantula, InvasiveSpiderling, TheRatKing, RatsofExtraordinarySize,
		Rat,
		#Mage
		HotStreak, FirstFlame, SecondFlame, SorcerersGambit, ArcanistDawngrasp, CelestialInkSet, Ignite, PrestorsPyromancer,
		FireSale, SanctumChandler, ClumsyCourier, GrandMagusAntonidas,
		#Paladin
		BlessedGoods, PrismaticJewelKit, RisetotheOccasion, LightbornCariel, NobleMount, CarielsWarhorse, CityTax,
		AllianceBannerman, CatacombGuard, LightbringersHammer, FirstBladeofWrynn, HighlordFordragon,
		#Priest
		CalloftheGrave, SeekGuidance, XyrellatheSanctified, PurifiedShard, ShardoftheNaaru, VoidtouchedAttendant,
		ShadowclothNeedle, TwilightDeceptor, Psyfiend, VoidShard, DarkbishopBenedictus, ElekkMount, XyrellasElekk,
		#Rogue
		FizzflashDistractor, Spyomatic, NoggenFogGenerator, HiddenGyroblade, UndercoverMole, FindtheImposter,
		SpymasterScabbs, SI7Extortion, Garrote, Bleed, MaestraoftheMasquerade, CounterfeitBlade, LoanShark, SI7Operative,
		SketchyInformation, SI7Informant, SI7Assassin,
		#Shaman
		CommandtheElements, LivingEarth, StormcallerBrukan, InvestmentOpportunity, Overdraft, BolnerHammerbeak,
		AuctionhouseGavel, ChargedCall, SpiritAlpha, GraniteForgeborn, CanalSlogger, TinyToys,
		#Warlock
		TheDemonSeed, BlightbornTamsin, TouchoftheNathrezim, BloodboundImp, DreadedMount, TamsinsDreadsteed, RunedMithrilRod,
		DarkAlleyPact, Fiend, DemonicAssault, ShadyBartender, Anetheron, EntitledCustomer,
		#Warrior
		Provoke, RaidtheDocks, CapnRokara, ShiverTheirTimbers, HarborScamp, CargoGuard, HeavyPlate, StormwindFreebooter,
		RemoteControlledGolem, GolemParts, CowardlyGrunt, Lothar,
		#Neutral
		GolakkaGlutton, Multicaster, MaddestBomber,
		#Demon Hunter
		CrowsNestLookout, NeedforGreed, ProvingGrounds,
		#Druid
		DruidoftheReef, DruidoftheReef_Rush, DruidoftheReef_Taunt, DruidoftheReef_Both, JerryRigCarpenter, MoonlitGuidance,
		#Hunter
		DoggieBiscuit, MonstrousParrot, DefiasBlastfisher,
		#Mage
		DeepwaterEvoker, ArcaneOverflow, ArcaneRemnant, GreySageParrot,
		#Paladin
		RighteousDefense, SunwingSquawker, WealthRedistributor,
		#Priest
		DefiasLeper, AmuletofUndying, Copycat,
		#Rogue
		BlackwaterCutlass, Parrrley,
		#Shaman
		BrilliantMacaw, Suckerhook,
		#Warlock
		ShadowbladeSlinger, WickedShipment, Hullbreaker,
		#Warrior
		MantheCannons, DefiasCannoneer, BlacksmithHammer,
]

Stormwind_Cards_Collectible = [
		#Neutral
		ElwynnBoar, Peasant, StockadesGuard, AuctioneerJaxon, DeeprunEngineer, EncumberedPackMule, Florist, MailboxDancer,
		PandarenImporter, SI7Skulker, StockadesPrisoner, EnthusiasticBanker, ImpatientShopkeep, NorthshireFarmer,
		PackageRunner, RustrotViper, TravelingMerchant, TwoFacedInvestor, EntrappedSorceress, FlightmasterDungar, Nobleman,
		Cheesemonger, GuildTrader, RoyalLibrarian, SpiceBreadBaker, StubbornSuspect, LionsGuard, StormwindGuard,
		BattlegroundBattlemaster, CityArchitect, CorneliusRoame, LadyPrestor, MoargForgefiend, VarianKingofStormwind,
		GoldshireGnoll,
		#Demon Hunter
		FinalShowdown, Metamorfin, SigilofAlacrity, FelBarrage, ChaosLeech, LionsFrenzy, Felgorger, PersistentPeddler,
		IreboundBrute, JaceDarkweaver,
		#Druid
		LostinthePark, SowtheSoil, VibrantSquirrel, Composting, Wickerclaw, OracleofElune, KodoMount, ParkPanther,
		BestinShell, SheldrasMoontree,
		#Hunter
		DevouringSwarm, DefendtheDwarvenDistrict, LeatherworkingKit, AimedShot, RammingMount, StormwindPiper, RodentNest,
		ImportedTarantula, TheRatKing, RatsofExtraordinarySize,
		#Mage
		HotStreak, FirstFlame, SorcerersGambit, CelestialInkSet, Ignite, PrestorsPyromancer, FireSale, SanctumChandler,
		ClumsyCourier, GrandMagusAntonidas,
		#Paladin
		BlessedGoods, PrismaticJewelKit, RisetotheOccasion, NobleMount, CityTax, AllianceBannerman, CatacombGuard,
		LightbringersHammer, FirstBladeofWrynn, HighlordFordragon,
		#Priest
		CalloftheGrave, SeekGuidance, ShardoftheNaaru, VoidtouchedAttendant, ShadowclothNeedle, TwilightDeceptor, Psyfiend,
		VoidShard, DarkbishopBenedictus, ElekkMount,
		#Rogue
		FindtheImposter, SI7Extortion, Garrote, MaestraoftheMasquerade, CounterfeitBlade, LoanShark, SI7Operative,
		SketchyInformation, SI7Informant, SI7Assassin,
		#Shaman
		CommandtheElements, InvestmentOpportunity, Overdraft, BolnerHammerbeak, AuctionhouseGavel, ChargedCall, SpiritAlpha,
		GraniteForgeborn, CanalSlogger, TinyToys,
		#Warlock
		TheDemonSeed, TouchoftheNathrezim, BloodboundImp, DreadedMount, RunedMithrilRod, DarkAlleyPact, DemonicAssault,
		ShadyBartender, Anetheron, EntitledCustomer,
		#Warrior
		Provoke, RaidtheDocks, ShiverTheirTimbers, HarborScamp, CargoGuard, HeavyPlate, StormwindFreebooter,
		RemoteControlledGolem, CowardlyGrunt, Lothar,
		#Neutral
		GolakkaGlutton, Multicaster, MaddestBomber,
		#Demon Hunter
		CrowsNestLookout, NeedforGreed, ProvingGrounds,
		#Druid
		DruidoftheReef, JerryRigCarpenter, MoonlitGuidance,
		#Hunter
		DoggieBiscuit, MonstrousParrot, DefiasBlastfisher,
		#Mage
		DeepwaterEvoker, ArcaneOverflow, GreySageParrot,
		#Paladin
		RighteousDefense, SunwingSquawker, WealthRedistributor,
		#Priest
		DefiasLeper, AmuletofUndying, Copycat,
		#Rogue
		BlackwaterCutlass, Parrrley,
		#Shaman
		BrilliantMacaw, Suckerhook,
		#Warlock
		ShadowbladeSlinger, Hullbreaker, WickedShipment,
		#Warrior
		MantheCannons, DefiasCannoneer, BlacksmithHammer,
]