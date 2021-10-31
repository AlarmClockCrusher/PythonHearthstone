from Parts_ConstsFuncsImports import *
from Parts_CardTypes import *
from Parts_TrigsAuras import *

from HS_AcrossPacks import Bananas, IllidariInitiate, Huffer, Leokk, Misha, SilverHandRecruit, Pyroblast
from HS_Outlands import Minion_Dormantfor2turns, MsshifnPrime, ZixorPrime, SolarianPrime, MurgurglePrime, ReliquaryPrime, \
					AkamaPrime, VashjPrime, KanrethadPrime, KargathPrime
from HS_Academy import Trig_Corrupt, Spellburst, SoulFragment



"""Auras"""
class Aura_DarkmoonStatue(Aura_AlwaysOn):
	attGain = 1

class ManaAura_LineHopper(ManaAura):
	by = -1
	def applicable(self, target): return "~Outcast" in target.index and target.ID == self.keeper.ID

#Even if hero is full health, the Lifesteal will still deal damage
class GameRuleAura_Ilgynoth(GameRuleAura):
	def auraAppears(self): self.keeper.Game.effects[self.keeper.ID]["Lifesteal Damages Enemy"] += 1
	def auraDisappears(self): self.keeper.Game.effects[self.keeper.ID]["Lifesteal Damages Enemy"] -= 1

class ManaAura_GameMaster(ManaAura_1UsageEachTurn):
	def auraAppears(self):
		game, ID = self.keeper.Game, self.keeper.ID
		if game.turn == ID and not any(issubclass(card, Secret) for card in game.Counters.cardsPlayedEachTurn[ID][-1]):
			self.aura = GameManaAura_GameMaster(game, ID)
			game.Manas.CardAuras.append(self.aura)
			self.aura.auraAppears()
		add2ListinDict(self, game.trigsBoard[ID], "TurnStarts")

class GameRuleAura_Deathwarden(GameRuleAura):
	def auraAppears(self):
		self.keeper.Game.effects[1]["Deathrattles X"] += 1
		self.keeper.Game.effects[2]["Deathrattles X"] += 1

	def auraDisappears(self):
		self.keeper.Game.effects[1]["Deathrattles X"] -= 1
		self.keeper.Game.effects[2]["Deathrattles X"] -= 1

class ManaAura_FelfireDeadeye(ManaAura):
	by, targets = -1, "Power"
	def applicable(self, target): return target.ID == self.keeper.ID


"""Trigs"""
class Trig_EndlessCorrupt(Trig_Corrupt):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if signal == "ManaPaid": self.on = number > self.keeper.mana
		else:
			card, self.on = self.keeper, False
			stat = int(type(card).__name__.split('_')[-1]) + 1
			newIndex = "DARKMOON_FAIRE~Neutral~2~%d~%d~Minion~~Horrendous Growth~Corrupted~Uncollectible" % (stat, stat)
			subclass = type("HorrendousGrowthCorrupt__" + str(stat), (HorrendousGrowthCorrupt,),
							{"attack": stat, "health": stat, "index": newIndex}
							)
			newCard = subclass(card.Game, card.ID)
			newCard.inheritEnchantmentsfrom(card)
			card.Game.Hand_Deck.replaceCardinHand(card, newCard, calcMana=True)

		
class Trig_ParadeLeader(TrigBoard):
	signals = ("MinionBeenSummoned", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject.ID == self.keeper.ID and subject != self.keeper and subject.effects["Rush"] > 0

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.giveEnchant(subject, 2, 0, name=ParadeLeader)
		

class Trig_OptimisticOgre(TrigBoard):
	signals = ("MinionAttacksMinion", "MinionAttacksHero", "BattleFinished", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		#The trigger can be reset any time by "BattleFinished".
		#Otherwise, can only trigger if there are enemies other than the target.
		#游荡怪物配合误导可能会将对英雄的攻击目标先改成对召唤的随从，然后再发回敌方英雄，说明攻击一个错误的敌人应该也是游戏现记录的目标之外的角色。
		return not signal.startswith("Minion") or (subject == self.keeper and self.keeper.onBoard and target[1] and not self.on
													and self.keeper.Game.charsAlive(3-subject.ID, target[1])
													)
													
	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		if self.keeper.onBoard:
			if signal == "BattleFinished": #Reset the Forgetful for next battle event.
				self.on = False
			elif target: #Attack signal
				game = self.keeper.Game
				char, redirect = None, 0
				otherEnemies = game.charsAlive(3- self.keeper.ID, target[1])
				if otherEnemies:
					char, redirect = numpyChoice(otherEnemies), numpyRandint(2)
					if char and redirect: #Redirect is 0/1, indicating whether the attack will redirect or not
						#玩家命令的一次攻击中只能有一次触发机会。只要满足进入50%判定的条件，即使没有最终生效，也不能再次触发。
						if game.GUI: game.GUI.trigBlink(self.keeper)
						target[1], self.on = char, True


class Trig_RedeemedPariah(TrigBoard):
	signals = ("MinionBeenPlayed", "SpellBeenPlayed", "WeaponBeenPlayed", "HeroCardBeenPlayed", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject.ID == self.keeper.ID and "~Outcast" in subject.index

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.giveEnchant(self.keeper, Enchantment_Cumulative(1, 1, name=RedeemedPariah))


class Trig_BladedLady(TrigHand):
	signals = ("HeroStatCheck", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.inHand and ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.Game.Manas.calcMana_Single(self.keeper)
		

class Trig_UmbralOwl(TrigHand):
	signals = ("SpellBeenPlayed", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.inHand and subject.ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.Game.Manas.calcMana_Single(self.keeper)
		
		
class Trig_OpentheCages(Trig_Secret):
	signals = ("TurnStarts", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0): #target here holds the actual target object
		secret = self.keeper
		return secret.ID == ID and secret.Game.minionsonBoard(secret.ID) and secret.Game.space(secret.ID) > 0
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.summon(numpyChoice((Huffer, Leokk, Misha))(self.keeper.Game, self.keeper.ID))
			
			
class Trig_RinlingsRifle(TrigBoard):
	signals = ("HeroAttackedMinion", "HeroAttackedHero", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.keeper.Game.heroes[self.keeper.ID] and self.keeper.onBoard

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.discoverandGenerate(RinlingsRifle, '', lambda : RinlingsRifle.decideSecretPool(self.keeper))
		

class Trig_TramplingRhino(TrigBoard):
	signals = ("MinionAttackedMinion", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject == self.keeper and target.health < 0

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		excessDmg = -target.health
		self.keeper.dealsDamage(self.keeper.Game.heroes[3-self.keeper.ID], excessDmg)


class Trig_RiggedFaireGame(Trig_Secret):
	signals = ("TurnEnds", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0): #target here holds the actual target object
		return self.keeper.ID != ID and self.keeper.Game.Counters.dmgHeroTookThisTurn[self.keeper.ID] == 0
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.Game.Hand_Deck.drawCard(self.keeper.ID)
		self.keeper.Game.Hand_Deck.drawCard(self.keeper.ID)
		self.keeper.Game.Hand_Deck.drawCard(self.keeper.ID)

		
class Trig_OhMyYogg(Trig_Secret):
	signals = ("SpellOKtoCast?", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject[0].ID != self.keeper.ID and subject is not None
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		subject[0] = numpyChoice(self.rngPool("%d-Cost Spells"%number))(self.keeper.Game, 3-self.keeper.ID)
		

class Trig_CarnivalBarker(TrigBoard):
	signals = ("MinionSummoned", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject.ID == self.keeper.ID and subject.health == 1 and subject != self.keeper

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.giveEnchant(subject, 1, 2, name=CarnivalBarker)


class Trig_NazmaniBloodweaver(TrigBoard):
	signals = ("SpellBeenPlayed", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject.ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if cards := self.keeper.findCards4ManaReduction(): ManaMod(numpyChoice(cards), by=-1).applies()
		
		
class Trig_BloodofGhuun(TrigBoard):
	signals = ("TurnEnds", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.keeper
		minions = [card for card in minion.Game.Hand_Deck.decks[minion.ID] if card.category == "Minion"]
		if minions and minion.Game.space(self.keeper.ID) > 0:
			minion.summon(numpyChoice(minions).selfCopy(minion.ID, minion, 5, 5))


class Trig_ShadowClone(Trig_Secret):
	signals = ("MinionAttackedHero", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.ID != self.keeper.Game.turn and target == self.keeper.Game.heroes[self.keeper.ID]
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		Copy = subject.selfCopy(self.keeper.ID, self.keeper)
		self.keeper.summon(Copy)


class Trig_MalevolentStrike(TrigHand):
	signals = ("DeckCheck", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.inHand and ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.Game.Manas.calcMana_Single(self.keeper)
		
		
class Trig_GrandTotemEysor(TrigBoard):
	signals = ("TurnEnds", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		keeper, typeSelf = self.keeper, type(self.keeper)
		keeper.AOE_GiveEnchant(keeper.Game.minionsonBoard(keeper.ID, keeper, race="Totem"), 1, 1, name=GrandTotemEysor)
		self.keeper.AOE_GiveEnchant([card for card in self.keeper.Game.Hand_Deck.hands[self.keeper.ID] if "Totem" in card.race],
									1, 1, name=GrandTotemEysor, add2EventinGUI=False)
		for card in self.keeper.Game.Hand_Deck.decks[self.keeper.ID]:
			if "Totem" in card.race: card.getsBuffDebuff_inDeck(1, 1, source=typeSelf, name=GrandTotemEysor)
			
class Trig_Magicfin(TrigBoard):
	signals = ("MinionDies", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and target != self.keeper and target.ID == self.keeper.ID and "Murloc" in target.race

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.addCardtoHand(numpyChoice(self.rngPool("Legendary Minions")), self.keeper.ID)


class Trig_WhackAGnollHammer(TrigBoard):
	signals = ("HeroAttackedMinion", "HeroAttackedHero", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.keeper.Game.heroes[self.keeper.ID] and self.keeper.onBoard

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if minions := self.keeper.Game.minionsonBoard(self.keeper.ID): 
			self.keeper.giveEnchant(numpyChoice(minions), 1, 1, name=WhackAGnollHammer)


class Aura_InaraStormcrash:
	def __init__(self, keeper):
		self.keeper, self.receivers = keeper, []
		self.signals = ("HeroAppears", "TurnStarts", "TurnEnds")

	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and (signal[0] == "T" or subject.ID == self.keeper.ID)

	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrig(signal, ID, subject, target, number, comment):
			minion = self.keeper
			if signal[0] == "T":  #
				if "E" in signal:  # At the end of either player's turn, clear the affected list
					for hero, receiver in self.receivers[:]: receiver.effectClear()
					self.receivers = []
				elif ID == minion.ID:  # Only start the effect at the start of your turn
					Aura_Receiver(minion.Game.heroes[ID], self, attGain=2, effGain="Windfury").effectStart()
			elif ID == minion.ID == minion.Game.turn:  # New hero is on board during your turn
				Aura_Receiver(subject, self, attGain=2, effGain="Windfury").effectStart()

	def auraAppears(self):
		game, ID = self.keeper.Game, self.keeper.ID
		if game.turn == ID: Aura_Receiver(game.heroes[ID], self, attGain=2, effGain="Windfury").effectStart()
		trigsBoard = game.trigsBoard[ID]
		for sig in self.signals: add2ListinDict(self, trigsBoard, sig)

	def auraDisappears(self):
		for hero, receiver in self.receivers[:]:
			receiver.effectClear()
		self.receivers = []
		trigsBoard = self.keeper.Game.trigsBoard[self.keeper.ID]
		for sig in self.signals: removefromListinDict(self, trigsBoard, sig)

	def selfCopy(self, recipient):
		return type(self)(recipient)

	# 这个函数会在复制场上扳机列表的时候被调用。
	def createCopy(self, game):
		# 一个光环的注册可能需要注册多个扳机
		if self not in game.copiedObjs:  # 这个光环没有被复制过
			game.copiedObjs[self] = Copy = self.selfCopy(self.keeper.createCopy(game))
			for hero, receiver in self.receivers:
				heroCopy = hero.createCopy(game)
				index = hero.auraReceivers.index(receiver)
				receiverCopy = heroCopy.auraReceivers[index]
				receiverCopy.source = Copy  # 补上这个receiver的source
				Copy.receivers.append((heroCopy, receiverCopy))
			return Copy
		else: return game.copiedObjs[self]


class Trig_ETCGodofMetal(TrigBoard):
	signals = ("MinionAttackedMinion", "MinionAttackedHero", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.keeper.ID and subject.effects["Rush"] > 0 and self.keeper.onBoard

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.dealsDamage(self.keeper.Game.heroes[3-self.keeper.ID], 2)
		
		
class Trig_RingmastersBaton(TrigBoard):
	signals = ("HeroAttackedMinion", "HeroAttackedHero", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.keeper.Game.heroes[self.keeper.ID] and self.keeper.onBoard

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		ownHand = self.keeper.Game.Hand_Deck.hands[self.keeper.ID]
		for race in ("Mech", "Dragon", "Pirate"):
			if minions := [card for card in ownHand if card.category == "Minion" and race in card.race]:
				self.keeper.giveEnchant(numpyChoice(minions), 1, 1, name=RingmastersBaton, add2EventinGUI=False)
			
			
class Trig_TentTrasher(TrigHand):
	signals = ("MinionAppears", "MinionDisappears", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		if 'A' in signal: return self.keeper.inHand and ID == self.keeper.ID and subject.race
		else: return self.keeper.inHand and ID == self.keeper.ID and target.race

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Tent trasher calcs")
		self.keeper.Game.Manas.calcMana_Single(self.keeper)
		

class Trig_MoonFang(TrigBoard):
	signals = ("FinalDmgonMinion?", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		#Can only prevent damage if there is still durability left
		return target == self.keeper and self.keeper.onBoard

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		number[0] = min(number[0], 1)
		
		
class Trig_RunawayBlackwing(TrigBoard):
	signals = ("TurnEnds", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		targets = self.keeper.Game.minionsAlive(3-self.keeper.ID)
		if targets: self.keeper.dealsDamage(numpyChoice(targets), 9)
		

class Trig_Saddlemaster(TrigBoard):
	signals = ("MinionBeenPlayed", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject.ID == self.keeper.ID and "Beast" in subject.race

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.addCardtoHand(numpyChoice(self.rngPool("Beasts")), self.keeper.ID)
			

class Trig_GlacierRacer(Spellburst):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		targets = [obj for obj in self.keeper.Game.minionsonBoard(self.keeper.ID) if obj.effects["Frozen"]]
		if (hero := self.keeper.Game.heroes[3-self.keeper.ID]).effects["Frozen"] > 0: targets.append(hero)
		if targets: self.keeper.AOE_Damage(targets, [3] * len(targets))


class Trig_KeywardenIvory(Spellburst):
	def __init__(self, keeper, card=None):
		super().__init__(keeper)
		self.savedObj = card

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.addCardtoHand(self.savedObj, self.keeper.ID)

	def selfCopy(self, recipient):
		return type(self)(recipient, self.savedObj)

	def assistCreateCopy(self, Copy):
		Copy.savedObj = self.savedObj


class Trig_ImprisonedCelestial(Spellburst):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.giveEnchant(self.keeper.Game.minionsonBoard(self.keeper.ID), effGain="Divine Shield", name=ImprisonedCelestial)

			
class Trig_Lightsteed(TrigBoard):
	signals = ("MinionReceivesHeal", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject.ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.giveEnchant(target, 0, 2, name=Lightsteed)
		
		
class Trig_Shenanigans(Trig_Secret):
	signals = ("CardDrawn", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		#假设即使第二张被爆牌也会触发
		secret = self.keeper
		return self.keeper.ID != self.keeper.Game.turn and self.keeper.ID != ID and self.keeper.Game.Counters.numCardsDrawnThisTurn[ID] == 1
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		card = Bananas(self.keeper.Game, target.ID)
		self.keeper.Game.Hand_Deck.replaceCardDrawn(target, card)
		

class Trig_SpikedWheel(Trig_SelfAura):
	signals = ("ArmorGained", "ArmorLost")
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.calcStat()

"""Deathrattles"""
class Death_Showstopper(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.keeper.Game
		for minion in curGame.minionsonBoard(1) + curGame.minionsonBoard(2):
			minion.getsSilenced()

class Death_ClawMachine(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		card, mana, entersHand = self.keeper.drawCertainCard(lambda card: card.category == "Minion")
		if entersHand: self.keeper.giveEnchant(card, 3, 3, name=ClawMachine)

class Death_RenownedPerformer(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.summon([PerformersAssistant(self.keeper.Game, self.keeper.ID) for _ in (0, 1)], relative="<>")
		
class Death_Greybough(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if minions := self.keeper.Game.minionsonBoard(self.keeper.ID):
			self.keeper.giveEnchant(numpyChoice(minions), trig=Death_SummonGreybough, trigType="Deathrattle", connect=True)

class Death_SummonGreybough(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.summon(Greybough(self.keeper.Game, self.keeper.ID))

class Death_DarkmoonTonk(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.keeper
		for num in (0, 1, 2, 3):
			if enemies := minion.Game.charsAlive(3 - minion.ID): minion.dealsDamage(numpyChoice(enemies), 2)
			else: break

class Death_TicketMaster(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		keeper = self.keeper
		keeper.shuffleintoDeck([Tickets(keeper.Game, keeper.ID) for _ in (0, 1, 2)])
		
class Death_RedscaleDragontamer(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.drawCertainCard(lambda card: "Dragon" in card.race)
		
class Death_RingMatron(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.summon([FieryImp(self.keeper.Game, self.keeper.ID) for _ in (0, 1)], relative="<>")
		
class Death_BumperCar(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.addCardtoHand([DarkmoonRider, DarkmoonRider], self.keeper.ID)

PrimeMinions = (MsshifnPrime, ZixorPrime, SolarianPrime, MurgurglePrime, ReliquaryPrime,
				AkamaPrime, VashjPrime, KanrethadPrime, KargathPrime)

class Death_EnvoyRustwix(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.keeper
		minion.shuffleintoDeck([prime(minion.Game, minion.ID) for prime in numpyChoice(PrimeMinions, 3, replace=True)])


"""Neutral Cards"""
class SafetyInspector(Minion):
	Class, race, name = "Neutral", "", "Safety Inspector"
	mana, attack, health = 1, 1, 3
	index = "DARKMOON_FAIRE~Neutral~Minion~1~1~3~~Safety Inspector~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Shuffle the lowest-Cost card from your hand into your deck. Draw a card"
	name_CN = "安全检查员"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if indices := pickLowestCostIndices(self.Game.Hand_Deck.hands[self.ID]):
			self.Game.Hand_Deck.shuffle_Hand2Deck(numpyChoice(indices), ID=self.ID, initiatorID=self.ID, shuffleAll=False)
		self.Game.Hand_Deck.drawCard(self.ID)
		
		
class CostumedEntertainer(Minion):
	Class, race, name = "Neutral", "", "Costumed Entertainer"
	mana, attack, health = 2, 1, 2
	index = "DARKMOON_FAIRE~Neutral~Minion~2~1~2~~Costumed Entertainer~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Give a random minion in your hand +2/+2"
	name_CN = "盛装演员"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if minions := [card for card in self.Game.Hand_Deck.hands[self.ID] if card.category == "Minion"]:
			self.giveEnchant(numpyChoice(minions), 2, 2, name=CostumedEntertainer, add2EventinGUI=False)
		
		
class HorrendousGrowthCorrupt(Minion):
	Class, race, name = "Neutral", "", "Horrendous Growth"
	mana, attack, health = 2, 3, 3
	index = "DARKMOON_FAIRE~Neutral~Minion~2~3~3~~Horrendous Growth~ToCorrupt~Corrupted~Uncollectible"
	requireTarget, effects, description = False, "", "Corrupt: Gain +1/+1. Can be Corrupted endlessly"
	name_CN = "恐怖增生体"
	trigHand = Trig_EndlessCorrupt

class HorrendousGrowth(Minion):
	Class, race, name = "Neutral", "", "Horrendous Growth"
	mana, attack, health = 2, 2, 2
	index = "DARKMOON_FAIRE~Neutral~Minion~2~2~2~~Horrendous Growth~ToCorrupt"
	requireTarget, effects, description = False, "", "Corrupt: Gain +1/+1. Can be Corrupted endlessly"
	name_CN = "恐怖增生体"
	trigHand, corruptedType = Trig_Corrupt, HorrendousGrowthCorrupt


class ParadeLeader(Minion):
	Class, race, name = "Neutral", "", "Parade Leader"
	mana, attack, health = 2, 2, 3
	index = "DARKMOON_FAIRE~Neutral~Minion~2~2~3~~Parade Leader"
	requireTarget, effects, description = False, "", "After you summon a Rush minion, give it +2 Attack"
	name_CN = "巡游领队"
	trigBoard = Trig_ParadeLeader		


class PrizeVendor(Minion):
	Class, race, name = "Neutral", "Murloc", "Prize Vendor"
	mana, attack, health = 2, 2, 3
	index = "DARKMOON_FAIRE~Neutral~Minion~2~2~3~Murloc~Prize Vendor~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Both players draw a card"
	name_CN = "奖品商贩"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.Hand_Deck.drawCard(self.ID)
		self.Game.Hand_Deck.drawCard(3-self.ID)
		
		
class RockRager(Minion):
	Class, race, name = "Neutral", "Elemental", "Rock Rager"
	mana, attack, health = 2, 5, 1
	index = "DARKMOON_FAIRE~Neutral~Minion~2~5~1~Elemental~Rock Rager~Taunt"
	requireTarget, effects, description = False, "Taunt", "Taunt"
	name_CN = "岩石暴怒者"
	
	
class Showstopper(Minion):
	Class, race, name = "Neutral", "", "Showstopper"
	mana, attack, health = 2, 3, 2
	index = "DARKMOON_FAIRE~Neutral~Minion~2~3~2~~Showstopper~Deathrattle"
	requireTarget, effects, description = False, "", "Deathrattle: Silence all minions"
	name_CN = "砸场游客"
	deathrattle = Death_Showstopper


class WrigglingHorror(Minion):
	Class, race, name = "Neutral", "", "Wriggling Horror"
	mana, attack, health = 2, 2, 1
	index = "DARKMOON_FAIRE~Neutral~Minion~2~2~1~~Wriggling Horror~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Give adjacent minions +1/+1"
	name_CN = "蠕动的恐魔"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.onBoard and (neighbors := self.Game.neighbors2(self)[0]):
			self.AOE_GiveEnchant(neighbors, 1, 1, name=WrigglingHorror)
		
		
class BananaVendor(Minion):
	Class, race, name = "Neutral", "", "Banana Vendor"
	mana, attack, health = 3, 2, 4
	index = "DARKMOON_FAIRE~Neutral~Minion~3~2~4~~Banana Vendor~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Add 2 Bananas to each player's hand"
	name_CN = "香蕉商贩"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.addCardtoHand([Bananas, Bananas], self.ID)
		self.addCardtoHand([Bananas, Bananas], 3-self.ID)


class DarkmoonDirigible_Corrupt(Minion):
	Class, race, name = "Neutral", "Mech", "Darkmoon Dirigible"
	mana, attack, health = 3, 3, 2
	index = "DARKMOON_FAIRE~Neutral~Minion~3~3~2~Mech~Darkmoon Dirigible~Divine Shield~Rush~Corrupted~Uncollectible"
	requireTarget, effects, description = False, "Divine Shield,Rush", "Corrupted. Divine Shield, Rush"
	name_CN = "暗月飞艇"


class DarkmoonDirigible(Minion):
	Class, race, name = "Neutral", "Mech", "Darkmoon Dirigible"
	mana, attack, health = 3, 3, 2
	index = "DARKMOON_FAIRE~Neutral~Minion~3~3~2~Mech~Darkmoon Dirigible~Divine Shield~ToCorrupt"
	requireTarget, effects, description = False, "Divine Shield", "Divine Shield. Corrupt: Gain Rush"
	name_CN = "暗月飞艇"
	trigHand, corruptedType = Trig_Corrupt, DarkmoonDirigible_Corrupt


class DarkmoonStatue_Corrupt(Minion):
	Class, race, name = "Neutral", "", "Darkmoon Statue"
	mana, attack, health = 3, 4, 5
	index = "DARKMOON_FAIRE~Neutral~Minion~3~4~5~~Darkmoon Statue~Corrupted~Uncollectible"
	requireTarget, effects, description = False, "", "Corrupted. Your other minions have +1 Attack"
	name_CN = "暗月雕像"
	aura = Aura_DarkmoonStatue

class DarkmoonStatue(Minion):
	Class, race, name = "Neutral", "", "Darkmoon Statue"
	mana, attack, health = 3, 0, 5
	index = "DARKMOON_FAIRE~Neutral~Minion~3~0~5~~Darkmoon Statue~ToCorrupt"
	requireTarget, effects, description = False, "", "Your other minions have +1 Attack. Corrupt: This gains +4 Attack"
	name_CN = "暗月雕像"
	aura, trigHand, corruptedType = Aura_DarkmoonStatue, Trig_Corrupt, DarkmoonStatue_Corrupt

		
class Gyreworm(Minion):
	Class, race, name = "Neutral", "Elemental", "Gyreworm"
	mana, attack, health = 3, 3, 2
	index = "DARKMOON_FAIRE~Neutral~Minion~3~3~2~Elemental~Gyreworm~Battlecry"
	requireTarget, effects, description = True, "", "Battlecry: If you played an Elemental last turn, deal 3 damage"
	name_CN = "旋岩虫"
	def needTarget(self, choice=0):
		return self.Game.Counters.numElementalsPlayedLastTurn[self.ID] > 0
		
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.numElementalsPlayedLastTurn[self.ID] > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and self.Game.Counters.numElementalsPlayedLastTurn[self.ID] > 0:
			self.dealsDamage(target, 3)
		return target
		
		
class InconspicuousRider(Minion):
	Class, race, name = "Neutral", "", "Inconspicuous Rider"
	mana, attack, health = 3, 2, 2
	index = "DARKMOON_FAIRE~Neutral~Minion~3~2~2~~Inconspicuous Rider~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Cast a Secret from your deck"
	name_CN = "低调的游客"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.Secrets.deploySecretsfromDeck(self.ID, initiator=self)
		
		
class KthirRitualist(Minion):
	Class, race, name = "Neutral", "", "K'thir Ritualist"
	mana, attack, health = 3, 4, 4
	index = "DARKMOON_FAIRE~Neutral~Minion~3~4~4~~K'thir Ritualist~Taunt~Battlecry"
	requireTarget, effects, description = False, "Taunt", "Taunt. Battlecry: Add a random 4-Cost minion to your opponent's hand"
	name_CN = "克熙尔祭师"
	poolIdentifier = "4-Cost Minions"
	@classmethod
	def generatePool(cls, pools):
		return "4-Cost Minions", pools.MinionsofCost[4]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.addCardtoHand(numpyChoice(self.rngPool("4-Cost Minions")), 3-self.ID)
		

class CircusAmalgam(Minion):
	Class, race, name = "Neutral", "Elemental,Mech,Demon,Murloc,Dragon,Beast,Pirate,Quilboar,Totem", "Circus Amalgam"
	mana, attack, health = 4, 4, 5
	index = "DARKMOON_FAIRE~Neutral~Minion~4~4~5~Elemental,Mech,Demon,Murloc,Dragon,Beast,Pirate,Quilboar,Totem~Circus Amalgam~Taunt"
	requireTarget, effects, description = False, "Taunt", "Taunt. This has all minion types"
	name_CN = "马戏团融合怪"
	
	
class CircusMedic_Corrupt(Minion):
	Class, race, name = "Neutral", "", "Circus Medic"
	mana, attack, health = 4, 3, 4
	index = "DARKMOON_FAIRE~Neutral~Minion~4~3~4~~Circus Medic~Battlecry~Corrupted~Uncollectible"
	requireTarget, effects, description = True, "", "Corrupted. Battlecry: Deal 4 damage"
	name_CN = "马戏团医师"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.dealsDamage(target, 4)
		return target


class CircusMedic(Minion):
	Class, race, name = "Neutral", "", "Circus Medic"
	mana, attack, health = 4, 3, 4
	index = "DARKMOON_FAIRE~Neutral~Minion~4~3~4~~Circus Medic~Battlecry~ToCorrupt"
	requireTarget, effects, description = True, "", "Battlecry: Restore 4 Health. Corrupt: Deal 4 damage instead"
	name_CN = "马戏团医师"
	trigHand, corruptedType = Trig_Corrupt, CircusMedic_Corrupt

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.restoresHealth(target, self.calcHeal(4))
		return target


class FantasticFirebird(Minion):
	Class, race, name = "Neutral", "Elemental", "Fantastic Firebird"
	mana, attack, health = 4, 3, 5
	index = "DARKMOON_FAIRE~Neutral~Minion~4~3~5~Elemental~Fantastic Firebird~Windfury"
	requireTarget, effects, description = False, "Windfury", "Windfury"
	name_CN = "炫目火鸟"
	
	
class KnifeVendor(Minion):
	Class, race, name = "Neutral", "", "Knife Vendor"
	mana, attack, health = 4, 3, 4
	index = "DARKMOON_FAIRE~Neutral~Minion~4~3~4~~Knife Vendor~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Deal 4 damage to each hero"
	name_CN = "小刀商贩"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.AOE_Damage([self.Game.heroes[1], self.Game.heroes[2]], [4, 4])
		

class DerailedCoaster(Minion):
	Class, race, name = "Neutral", "", "Derailed Coaster"
	mana, attack, health = 5, 3, 2
	index = "DARKMOON_FAIRE~Neutral~Minion~5~3~2~~Derailed Coaster~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Summon a 1/1 Rider with Rush for each minion in your hand"
	name_CN = "脱轨过山车"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if num := sum(card.category == "Minion" for card in self.Game.Hand_Deck.hands[self.ID]):
			self.summon([DarkmoonRider(self.Game, self.ID) for i in range(num)])
		

class DarkmoonRider(Minion):
	Class, race, name = "Neutral", "", "Darkmoon Rider"
	mana, attack, health = 1, 1, 1
	index = "DARKMOON_FAIRE~Neutral~Minion~1~1~1~~Darkmoon Rider~Rush~Uncollectible"
	requireTarget, effects, description = False, "Rush", "Rush"
	name_CN = "暗月乘客"


class FleethoofPearltusk_Corrupt(Minion):
	Class, race, name = "Neutral", "Beast", "Fleethoof Pearltusk"
	mana, attack, health = 5, 8, 8
	index = "DARKMOON_FAIRE~Neutral~Minion~5~8~8~Beast~Fleethoof Pearltusk~Rush~Corrupted~Uncollectible"
	requireTarget, effects, description = False, "Rush", "Rush"
	name_CN = "迅蹄珠齿象"

class FleethoofPearltusk(Minion):
	Class, race, name = "Neutral", "Beast", "Fleethoof Pearltusk"
	mana, attack, health = 5, 4, 4
	index = "DARKMOON_FAIRE~Neutral~Minion~5~4~4~Beast~Fleethoof Pearltusk~Rush~ToCorrupt"
	requireTarget, effects, description = False, "Rush", "Rush. Corrupt: Gain +4/+4"
	name_CN = "迅蹄珠齿象"
	trigHand, corruptedType = Trig_Corrupt, FleethoofPearltusk_Corrupt

	
class OptimisticOgre(Minion):
	Class, race, name = "Neutral", "", "Optimistic Ogre"
	mana, attack, health = 5, 6, 7
	index = "DARKMOON_FAIRE~Neutral~Minion~5~6~7~~Optimistic Ogre"
	requireTarget, effects, description = False, "", "50% chance to attack the correct enemy"
	name_CN = "乐观的食人魔"
	trigBoard = Trig_OptimisticOgre		


class ClawMachine(Minion):
	Class, race, name = "Neutral", "Mech", "Claw Machine"
	mana, attack, health = 6, 6, 3
	index = "DARKMOON_FAIRE~Neutral~Minion~6~6~3~Mech~Claw Machine~Rush~Deathrattle"
	requireTarget, effects, description = False, "Rush", "Rush. Deathrattle: Draw a minion and give it +3/+3"
	name_CN = "娃娃机"
	deathrattle = Death_ClawMachine


class SilasDarkmoon(Minion):
	Class, race, name = "Neutral", "", "Silas Darkmoon"
	mana, attack, health = 7, 4, 4
	index = "DARKMOON_FAIRE~Neutral~Minion~7~4~4~~Silas Darkmoon~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: Choose a direction to rotate all minions"
	name_CN = "希拉斯暗月"
	
	def prepMinionstoSwap(self, minions):
		for minion in minions:
			if minion:
				minion.disappears()
				self.Game.minions[minion.ID].remove(minion)
				minion.ID = 3 - minion.ID
				
	def swappedMinionsAppear(self, minions):
		self.Game.sortPos()
		#假设归还或者是控制对方随从的时候会清空所有暂时控制的标志，并取消回合结束归还随从的扳机
		for minion in minions:
			if minion:
				minion.appears(firstTime=False) #Swapped Imprisoned minions won't go Dormant
				minion.effects["Borrowed"] = 0
				for trig in reversed(minion.trigsBoard):
					if isinstance(trig, Trig_Borrow):
						trig.disconnect()
						minion.trigsBoard.remove(trig)
				#minion.afterSwitchSide(activity="Permanent")
				
	def rotateAllMinions(self, perspectiveID=1, giveOwnLeft=True):
		miniontoGive, miniontoTake = None, None
		ownMinions = self.Game.minionsonBoard(perspectiveID)
		enemyMinions = self.Game.minionsonBoard(3-perspectiveID)
		if giveOwnLeft: ownIndex, enemyIndex = 0, -1  #Give your leftmost and take enemy's rightmost
		else: ownIndex, enemyIndex = -1, 0 #Give your rightmost and take enemy's leftmost
		if ownMinions: miniontoGive = self.Game.minions[perspectiveID][ownMinions[ownIndex].pos]
		if enemyMinions: miniontoTake = self.Game.minions[3-perspectiveID][enemyMinions[enemyIndex].pos]
		
		self.prepMinionstoSwap([miniontoGive, miniontoTake])
		if giveOwnLeft: #Add minions to your rightmost and enemy's leftmost
			self.Game.minions[perspectiveID].append(miniontoTake)
			self.Game.minions[3-perspectiveID].insert(0, miniontoGive)
		else: #Add minions to your leftmost and enemy's rightmost
			self.Game.minions[perspectiveID].insert(0, miniontoTake)
			self.Game.minions[3-perspectiveID].append(miniontoGive)
		self.swappedMinionsAppear([miniontoGive, miniontoTake])
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.chooseFixedOptions(SilasDarkmoon, comment,
								options=[RotateThisWay(ID=self.ID), RotateThatWay(ID=self.ID)])
	
	#RotateThisWay give your leftmost minion
	def discoverDecided(self, option, case, info_RNGSync=None, info_GUISync=None):
		optionType = type(option)
		if case != "Guided":
			self.Game.picks_Backup.append((info_RNGSync, info_GUISync, case == "Random", optionType) )
		SilasDarkmoon.rotateAllMinions(self, perspectiveID=self.ID, giveOwnLeft=optionType == RotateThisWay)

class RotateThisWay(Option):
	name, description = "Rotate This Way", "Give your LEFTMOST minion"
	index = ""
	mana, attack, health = -1, -1, -1

class RotateThatWay(Option):
	name, description = "Rotate That Way", "Give your RIGHTMOST minion"
	index = ""
	mana, attack, health = 0, -1, -1


class Strongman_Corrupt(Minion):
	Class, race, name = "Neutral", "", "Strongman"
	mana, attack, health = 0, 6, 6
	index = "DARKMOON_FAIRE~Neutral~Minion~0~6~6~~Strongman~Taunt~Corrupted~Uncollectible"
	requireTarget, effects, description = False, "Taunt", "Corrupted. Taunt"
	name_CN = "大力士"


class Strongman(Minion):
	Class, race, name = "Neutral", "", "Strongman"
	mana, attack, health = 7, 6, 6
	index = "DARKMOON_FAIRE~Neutral~Minion~7~6~6~~Strongman~Taunt~ToCorrupt"
	requireTarget, effects, description = False, "Taunt", "Taunt. Corrupt: This costs (0)"
	name_CN = "大力士"
	trigHand, corruptedType = Trig_Corrupt, Strongman_Corrupt

	
class CarnivalClown_Corrupt(Minion):
	Class, race, name = "Neutral", "", "Carnival Clown"
	mana, attack, health = 9, 4, 4
	index = "DARKMOON_FAIRE~Neutral~Minion~9~4~4~~Carnival Clown~Taunt~Battlecry~Corrupted~Uncollectible"
	requireTarget, effects, description = False, "Taunt", "Corrupted. Taunt. Battlecry: Fill your board with copies of this"
	name_CN = "狂欢小丑"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		#假设已经死亡时不会召唤复制
		if not self.dead: self.summon([self.selfCopy(self.ID, self) for i in range(7)], relative="<>")


class CarnivalClown(Minion):
	Class, race, name = "Neutral", "", "Carnival Clown"
	mana, attack, health = 9, 4, 4
	index = "DARKMOON_FAIRE~Neutral~Minion~9~4~4~~Carnival Clown~Taunt~Battlecry~ToCorrupt"
	requireTarget, effects, description = False, "Taunt", "Taunt. Battlecry: Summon 2 copies of this. Corrupted: Fill your board with copies"
	name_CN = "狂欢小丑"
	trigHand, corruptedType = Trig_Corrupt, CarnivalClown_Corrupt
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		# 假设已经死亡时不会召唤复制
		if self.onBoard or self.inDeck: self.summon([self.selfCopy(self.ID, self) for _ in (0, 1)], relative="<>")

#Assume one can get CThun as long as pieces are played, even if it didn't start in their deck
class BodyofCThun(Spell):
	Class, school, name = "Neutral", "", "Body of C'Thun"
	requireTarget, mana, effects = False, 5, ""
	index = "DARKMOON_FAIRE~Neutral~Spell~5~~Body of C'Thun~Uncollectible"
	description = "Piece of C'Thun(0/4). Summon a 6/6 C'Thun's body with Taunt"
	name_CN = "克苏恩之躯"
	def available(self):
		return self.Game.space(self.ID) > 0
	
	def text(self):
		trigsBoard = self.Game.trigsBoard[self.ID]
		trig = next((trig for trig in trigsBoard if isinstance(trig, CThuntheShattered_Effect)), None) if "CThunPiece" in trigsBoard else None
		return "%d/4"%(len(trig.pieces) if trig else 0)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon(CThunsBody(self.Game, self.ID))
		#Assume the spell effect will increase the counter
		if "CThunPiece" not in self.Game.trigsBoard[self.ID]:
			CThuntheShattered_Effect(self.Game, self.ID).connect()
		self.Game.sendSignal("CThunPiece", self.ID, None, None, 0, "Body")

class CThunsBody(Minion):
	Class, race, name = "Neutral", "", "C'Thun's Body"
	mana, attack, health = 6, 6, 6
	index = "DARKMOON_FAIRE~Neutral~Minion~6~6~6~~C'Thun's Body~Taunt~Uncollectible"
	requireTarget, effects, description = False, "Taunt", "Taunt"
	name_CN = "克苏恩之躯"

class EyeofCThun(Spell):
	Class, school, name = "Neutral", "", "Eye of C'Thun"
	requireTarget, mana, effects = False, 5, ""
	index = "DARKMOON_FAIRE~Neutral~Spell~5~~Eye of C'Thun~Uncollectible"
	description = "Deal 7 damage randomly split among all enemies"
	name_CN = "克苏恩之眼"
	def text(self):
		trigsBoard = self.Game.trigsBoard[self.ID]
		trig = next((trig for trig in trigsBoard if isinstance(trig, CThuntheShattered_Effect)), None) if "CThunPiece" in trigsBoard else None
		return "%d/4, %d"%(len(trig.pieces) if trig else 0, self.calcDamage(7))

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		side, game = 3 - self.ID, self.Game
		for _ in range(self.calcDamage(7)):
			if objs := game.charsAlive(side): self.dealsDamage(numpyChoice(objs), 1)
			else: break
		if "CThunPiece" not in self.Game.trigsBoard[self.ID]:
			CThuntheShattered_Effect(self.Game, self.ID).connect()
		self.Game.sendSignal("CThunPiece", self.ID, None, None, 0, "Eye")

class HeartofCThun(Spell):
	Class, school, name = "Neutral", "", "Heart of C'Thun"
	requireTarget, mana, effects = False, 5, ""
	index = "DARKMOON_FAIRE~Neutral~Spell~5~~Heart of C'Thun~Uncollectible"
	description = "Deal 3 damage to all minions"
	name_CN = "克苏恩之心"
	def text(self):
		trigsBoard = self.Game.trigsBoard[self.ID]
		trig = next((trig for trig in trigsBoard if isinstance(trig, CThuntheShattered_Effect)), None) if "CThunPiece" in trigsBoard else None
		damage = self.calcDamage(3)
		return "%d/4, %d"%(len(trig.pieces) if trig else 0, damage)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = self.calcDamage(3)
		targets = self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)
		self.AOE_Damage(targets, [damage] * len(targets))
		if "CThunPiece" not in self.Game.trigsBoard[self.ID]:
			CThuntheShattered_Effect(self.Game, self.ID).connect()
		self.Game.sendSignal("CThunPiece", self.ID, None, None, 0, "Heart")

class MawofCThun(Spell):
	Class, school, name = "Neutral", "", "Maw of C'Thun"
	requireTarget, mana, effects = True, 5, ""
	index = "DARKMOON_FAIRE~Neutral~Spell~5~~Maw of C'Thun~Uncollectible"
	description = "Destroy a minion"
	name_CN = "克苏恩之口"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard
	
	def text(self):
		trigsBoard = self.Game.trigsBoard[self.ID]
		trig = next((trig for trig in trigsBoard if isinstance(trig, CThuntheShattered_Effect)), None) if "CThunPiece" in trigsBoard else None
		return len(trig.pieces) if trig else 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.Game.kill(self, target)
		#Assume the counter still works even if there is no target designated
		if "CThunPiece" not in self.Game.trigsBoard[self.ID]:
			CThuntheShattered_Effect(self.Game, self.ID).connect()
		self.Game.sendSignal("CThunPiece", self.ID, None, None, 0, "Maw")

#https://www.iyingdi.com/web/article/search/108538
#克苏恩不会出现在起手手牌中，只能在之后抽到碎片
#不在衍生池中，不能被随机发生和召唤等
#碎片是可以在第一次抽牌中抽到的，计入“开始时不在牌库中的牌”
#带克苏恩会影响巴库的触发，不影响狼王
#四张不同的碎片被打出后才会触发洗入克苏恩的效果，可以被法术反制
class CThuntheShattered(Minion):
	Class, race, name = "Neutral", "", "C'Thun, the Shattered"
	mana, attack, health = 10, 6, 6
	index = "DARKMOON_FAIRE~Neutral~Minion~10~6~6~~C'Thun, the Shattered~Battlecry~Start of Game~Legendary"
	requireTarget, effects, description = False, "", "Start of Game: Break into pieces. Battlecry: Deal 30 damage randomly split among all enemies"
	name_CN = "克苏恩，破碎之劫"
	#WON't show up in the starting hand
	def startofGame(self):
		#Remove the card from deck. Assume the final card WON't count as deck original card
		game, ID = self.Game, self.ID
		game.Hand_Deck.extractfromDeck(self, ID=0, getAll=False, enemyCanSee=True)
		self.shuffleintoDeck([BodyofCThun(game, ID), EyeofCThun(game, ID), HeartofCThun(game, ID), MawofCThun(game, ID)])
		CThuntheShattered_Effect(game, ID).connect()

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		side, game = 3-self.ID, self.Game
		for _ in range(30):
			if objs := game.charsAlive(side): self.dealsDamage(numpyChoice(objs), 1)
			else: break
		

class DarkmoonRabbit(Minion):
	Class, race, name = "Neutral", "Beast", "Darkmoon Rabbit"
	mana, attack, health = 10, 1, 1
	index = "DARKMOON_FAIRE~Neutral~Minion~10~1~1~Beast~Darkmoon Rabbit~Rush~Poisonous"
	requireTarget, effects, description = False, "Rush,Poisonous,Sweep", "Rush, Poisonous. Also damages the minions next to whomever this attacks"
	name_CN = "暗月兔子"
	
	
class NZothGodoftheDeep(Minion):
	Class, race, name = "Neutral", "", "N'Zoth, God of the Deep"
	mana, attack, health = 9, 5, 7
	index = "DARKMOON_FAIRE~Neutral~Minion~9~5~7~~N'Zoth, God of the Deep~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: Resurrect a friendly minion of each minion type"
	name_CN = "恩佐斯，深渊之神"
	#A single Amalgam minion won't be resurrected multiple times
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		game, ID = self.Game, self.ID
		#First, categorize. Second, from each type, select one.
		minions, pool = [], game.Counters.minionsDiedThisGame[ID]
		types = {"Beast": [], "Pirate": [], "Elemental": [], "Mech": [], "Dragon": [], "Quilboar": [], "Totem": [], "Demon": [], "Murloc": [], "All": []}
		#假设机制如下 ，在依次决定几个种族召唤随从，融合怪的随从池和单一种族的随从池合并计算随机。这个种族下如果没有召唤出一个融合怪，则它可以继续等待，如果召唤出来了，则将其移出随从池
		for card in pool:
			race = card.race
			if race: types[race if len(race) < 10 else "All"].append(card)
		for race in ["Elemental", "Mech", "Demon", "Murloc", "Dragon", "Beast", "Pirate", "Quilboar", "Totem"]: #假设种族顺序是与融合怪的牌面描述 一致的
			a, b = len(types[race]), len(types["All"])
			if a or b:
				p1 = a / (a + b)
				isAmalgam = numpyChoice([0, 1], p=[p1, 1-p1])
				minions.append(types["All"].pop(numpyRandint(b)) if isAmalgam else types[race][numpyRandint(a)])
		if minions: self.summon([minion(game, ID) for minion in minions])
		
		
class CurseofFlesh(Spell):
	Class, school, name = "Neutral", "", "Curse of Flesh"
	requireTarget, mana, effects = False, 0, ""
	index = "DARKMOON_FAIRE~Neutral~Spell~0~~Curse of Flesh~Uncollectible"
	description = "Fill the board with random minions, then give yours Rush"
	name_CN = "血肉诅咒"
	poolIdentifier = "Minions to Summon"
	@classmethod
	def generatePool(cls, pools):
		pool = []
		for minions in pools.MinionsofCost.values(): #value is still a dict: {index: type}
			pool += minions
		return "Minions to Summon", pool
		
	def __init__(self, Game, ID, yogg):
		super().__init__(Game, ID)
		self.yogg = yogg
		
	def cast(self, target=None, func=None):
		game = self.Game
		minions1 = numpyChoice(self.rngPool("Minions to Summon"), game.space(1), replace=True)
		minions2 = numpyChoice(self.rngPool("Minions to Summon"), game.space(2), replace=True)
		if self.ID == 1: ownMinions, enemyMinions = minions1, minions2
		else: ownMinions, enemyMinions = minions2, minions1
		if game.GUI: game.GUI.showOffBoardTrig(self)
		if len(ownMinions):
			ownMinions = [minion(game, self.ID) for minion in ownMinions]
			self.yogg.summon(ownMinions)
		if len(enemyMinions):
			enemyMinions = [minion(game, 3-self.ID) for minion in enemyMinions]
			self.yogg.summon(enemyMinions)
		self.yogg.AOE_GiveEnchant([minion for minion in ownMinions if minion.onBoard], effGain="Rush", name=CurseofFlesh)


class DevouringHunger(Spell):
	Class, school, name = "Neutral", "", "Devouring Hunger"
	requireTarget, mana, effects = False, 0, ""
	index = "DARKMOON_FAIRE~Neutral~Spell~0~~Devouring Hunger~Uncollectible"
	description = "Destroy all other minions. Gain their Attack and Health"
	name_CN = "吞噬之饥"
	def __init__(self, Game, ID, yogg):
		super().__init__(Game, ID)
		self.yogg = yogg
		
	def cast(self, target=None, func=None):
		game = self.Game
		if game.GUI: game.GUI.showOffBoardTrig(self)
		attGain, healthGain = 0, 0
		for minion in game.minionsonBoard(1) + game.minionsonBoard(2):
			if minion != self.yogg:
				attGain += max(0, minion.attack)
				healthGain += max(0, minion.health)
				game.kill(self.yogg, minion)
		if self.yogg.onBoard or self.yogg.inHand: self.giveEnchant(self.yogg, attGain, healthGain, name=DevouringHunger)
		

class HandofFate(Spell):
	Class, school, name = "Neutral", "", "Hand of Fate"
	requireTarget, mana, effects = False, 0, ""
	index = "DARKMOON_FAIRE~Neutral~Spell~0~~Hand of Fate~Uncollectible"
	description = "Fill your hand with random spells. They cost (0) this turn"
	name_CN = "命运之手"
	poolIdentifier = "Spells"
	@classmethod
	def generatePool(cls, pools):
		spells = []
		for cards in pools.ClassCards.values():
			spells += [card for card in cards if card.category == "Spell"]
		return "Spells", spells
	
	def __init__(self, Game, ID, yogg):
		super().__init__(Game, ID)
		self.yogg = yogg
		
	def cast(self, target=None, func=None):
		game = self.Game
		if game.GUI: game.GUI.showOffBoardTrig(self)
		spells = [spell(game, self.ID) for spell in numpyChoice(self.rngPool("Spells"), game.Hand_Deck.spaceinHand(self.ID), replace=True)]
		self.yogg.addCardtoHand(spells, self.ID)
		for spell in spells:
			if spell.inHand: ManaMod_YShaarjtheDefiler(spell).applies()
			

class MindflayerGoggles(Spell):
	Class, school, name = "Neutral", "", "Mindflayer Goggles"
	requireTarget, mana, effects = False, 0, ""
	index = "DARKMOON_FAIRE~Neutral~Spell~0~~Mindflayer Goggles~Uncollectible"
	description = "Take control of three random enemy minions"
	name_CN = "夺心护目镜"
	def __init__(self, Game, ID, yogg):
		super().__init__(Game, ID)
		self.yogg = yogg
		
	def cast(self, target=None, func=None):
		game, side = self.Game, 3 - self.ID
		if game.GUI: game.GUI.showOffBoardTrig(self)
		for _ in range(3):
			minions = game.minionsAlive(side)
			if minions: game.minionSwitchSide(numpyChoice(minions))
		

class Mysterybox(Spell):
	Class, school, name = "Neutral", "", "Mysterybox"
	requireTarget, mana, effects = False, 0, ""
	index = "DARKMOON_FAIRE~Neutral~Spell~0~~Mysterybox~Uncollectible"
	description = "Cast a random spell for each spell you've cast this game(targets chosen randomly)"
	name_CN = "神秘魔盒"
	#pool already generated by the other effect
	def __init__(self, Game, ID, yogg):
		super().__init__(Game, ID)
		self.yogg = yogg
		
	def cast(self, target=None, func=None):
		game = self.Game
		if game.GUI: game.GUI.showOffBoardTrig(self)
		num = sum(issubclass(card, Spell) for card in game.Counters.cardsPlayedThisGame[self.ID])
		spells = [spell(game, self.ID) for spell in  numpyChoice(self.rngPool("Spells"), num, replace=True)]
		for spell in spells:
			spell.cast()
			game.gathertheDead(decideWinner=True)
			
#每次释放炎爆之后会进行设计胜负判定的死亡结算
class RodofRoasting(Spell):
	Class, school, name = "Neutral", "", "Rod of Roasting"
	requireTarget, mana, effects = False, 0, ""
	index = "DARKMOON_FAIRE~Neutral~Spell~0~~Rod of Roasting~Uncollectible"
	description = "Cast 'Pyroblast' randomly until a player dies"
	name_CN = "燃烧权杖"
	def __init__(self, Game, ID, yogg):
		super().__init__(Game, ID)
		self.yogg = yogg
		
	def cast(self, target=None, func=None):
		game = self.Game
		if game.GUI: game.GUI.showOffBoardTrig(self)
		i = 0
		while i < 30 and game.heroes[1].health > 0 and not game.heroes[1].dead and game.heroes[2].health > 0 and not game.heroes[2].dead:
			if Pyroblast(game, self.ID).cast(func=lambda obj: obj.health > 0 and not obj.dead):
				i += 1
				game.gathertheDead(decideWinner=True)
			else: break
		if i: game.heroes[3-self.ID].dead = True #假设在30次循环后如果还没有人死亡的话，则直接杀死对方英雄
		

class YoggSaronMasterofFate(Minion):
	Class, race, name = "Neutral", "", "Yogg-Saron, Master of Fate"
	mana, attack, health = 10, 7, 5
	index = "DARKMOON_FAIRE~Neutral~Minion~10~7~5~~Yogg-Saron, Master of Fate~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: If you've cast 10 spells this game, spin the Wheel of Yogg-Saron"
	name_CN = "尤格-萨隆，命运主宰"
	def effCanTrig(self):
		self.effectViable = sum(issubclass(card, Spell) for card in self.Game.Counters.cardsPlayedThisGame[self.ID]) > 10

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if sum(issubclass(card, Spell) for card in self.Game.Counters.cardsPlayedThisGame[self.ID]) > 10:
			#CurseofFlesh "Fill the board with random minions, then give your Rush"
			#DevouringHunger "Destroy all other minions. Gain their Attack and Health"
			#HandofFate "Fill your hand with random spells. They cost (0) this turn"
			#MindflayerGoggles "Take control of three random enemy minions"
			#Mysterybox "Cast a random spell for each spell you've cast this game(targets chosen randomly)"
			#RodofRoasting "Cast 'Pyroblast' randomly until a player dies"
			wheel = numpyChoice([CurseofFlesh, DevouringHunger, HandofFate, MindflayerGoggles, Mysterybox, RodofRoasting],
								p=[0.19, 0.19, 0.19, 0.19, 0.19, 0.05])
			wheel(self.Game, self.ID, self).cast()
		
		
class YShaarjtheDefiler(Minion):
	Class, race, name = "Neutral", "", "Y'Shaarj, the Defiler"
	mana, attack, health = 10, 10, 10
	index = "DARKMOON_FAIRE~Neutral~Minion~10~10~10~~Y'Shaarj, the Defiler~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: Add a copy of each Corrupted card you've played this game to your hand. They cost (0) this turn"
	name_CN = "亚煞极，污染之源"
	#The mana effect should be carried by each card, since card copied to opponent should also cost (0).
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		game, ID = self.Game, self.ID
		pool = [card for card in game.Counters.cardsPlayedThisGame[ID] if "_Corrupt" in card.__name__]
		#numpy.random.choice can apply to [], as long as num=0
		cards = numpyChoice(pool, min(game.Hand_Deck.spaceinHand(ID), len(pool)), replace=False)
		if cards:
			cards = [card(game, ID) for card in cards]
			self.addCardtoHand(cards, ID)
			for card in cards:
				if card.inHand: ManaMod_YShaarjtheDefiler(card).applies()

class ManaMod_YShaarjtheDefiler(ManaMod):
	def __init__(self, recipient):
		super().__init__(recipient, to=0)

	def turnEnds(self, turn2End): removefrom(self, self.recipient.manaMods)


"""Demon Hunter Cards"""
class FelscreamBlast(Spell):
	Class, school, name = "Demon Hunter", "Fel", "Felscream Blast"
	requireTarget, mana, effects = True, 1, "Lifesteal"
	index = "DARKMOON_FAIRE~Demon Hunter~Spell~1~Fel~Felscream Blast~Lifesteal"
	description = "Lifesteal. Deal 1 damage to a minion and its neighbors"
	name_CN = "邪吼冲击"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = self.calcDamage(1)
			if target.onBoard and (neighbors := self.Game.neighbors2(target)[0]):
				self.AOE_Damage([target] + neighbors, [damage] * (1 + len(neighbors)))
			else: self.dealsDamage(target, damage)
		return target
		
		
class ThrowGlaive(Spell):
	Class, school, name = "Demon Hunter", "", "Throw Glaive"
	requireTarget, mana, effects = True, 1, ""
	index = "DARKMOON_FAIRE~Demon Hunter~Spell~1~~Throw Glaive"
	description = "Deal 2 damage to a minion. If it dies, add a temporary copy of this to your hand"
	name_CN = "投掷利刃"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard
		
	def text(self): return self.calcDamage(2)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			dmgTaker, damageActual = self.dealsDamage(target, self.calcDamage(2))
			if dmgTaker.health < 1 or dmgTaker.dead:
				card = ThrowGlaive(self.Game, self.ID)
				card.trigsHand = [Trig_Echo(card)]
				self.addCardtoHand(card, self.ID)
		return target
		
		
class RedeemedPariah(Minion):
	Class, race, name = "Demon Hunter", "", "Redeemed Pariah"
	mana, attack, health = 2, 2, 3
	index = "DARKMOON_FAIRE~Demon Hunter~Minion~2~2~3~~Redeemed Pariah"
	requireTarget, effects, description = False, "", "After you play an Outcast card, gain +1/+1"
	name_CN = "获救的流民"
	trigBoard = Trig_RedeemedPariah		


class Acrobatics(Spell):
	Class, school, name = "Demon Hunter", "", "Acrobatics"
	requireTarget, mana, effects = False, 3, ""
	index = "DARKMOON_FAIRE~Demon Hunter~Spell~3~~Acrobatics"
	description = "Draw 2 cards. If you play both this turn, draw 2 more"
	name_CN = "空翻杂技"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		card1, mana, entersHand = self.Game.Hand_Deck.drawCard(self.ID)
		if entersHand:
			card2, mana, entersHand = self.Game.Hand_Deck.drawCard(self.ID)
			if entersHand: Acrobatics_Effect(self.Game, self.ID, [card1, card2]).connect()


class DreadlordsBite(Weapon):
	Class, name, description = "Demon Hunter", "Dreadlord's Bite", "Outcast: Deal 1 damage to all enemies"
	mana, attack, durability, effects = 3, 2, 2, ""
	index = "DARKMOON_FAIRE~Demon Hunter~Weapon~3~2~2~Dreadlord's Bite~Outcast"
	name_CN = "恐惧魔王之咬"
	
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.outcastcanTrig(self)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if posinHand == 0 or posinHand == -1:
			enemies = [self.Game.heroes[3-self.ID]] + self.Game.minionsonBoard(3-self.ID)
			self.AOE_Damage(enemies, [1] * len(enemies))
		
		
class FelsteelExecutioner_Corrupt(Weapon):
	Class, name, description = "Demon Hunter", "Felsteel Executioner", "Corrupted"
	mana, attack, durability, effects = 3, 4, 3, ""
	index = "DARKMOON_FAIRE~Demon Hunter~Weapon~3~4~3~Felsteel Executioner~Corrupted~Uncollectible"
	name_CN = "魔钢处决者"
	
class FelsteelExecutioner(Minion):
	Class, race, name = "Demon Hunter", "Elemental", "Felsteel Executioner"
	mana, attack, health = 3, 4, 3
	index = "DARKMOON_FAIRE~Demon Hunter~Minion~3~4~3~Elemental~Felsteel Executioner~ToCorrupt"
	requireTarget, effects, description = False, "", "Corrupt: Become a weapon"
	name_CN = "魔钢处决者"
	trigHand, corruptedType = Trig_Corrupt, FelsteelExecutioner_Corrupt


class LineHopper(Minion):
	Class, race, name = "Demon Hunter", "", "Line Hopper"
	mana, attack, health = 3, 3, 4
	index = "DARKMOON_FAIRE~Demon Hunter~Minion~3~3~4~~Line Hopper"
	requireTarget, effects, description = False, "", "Your Outcast cards cost (1) less"
	name_CN = "越线的游客"
	aura = ManaAura_LineHopper


class InsatiableFelhound_Corrupt(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Insatiable Felhound"
	mana, attack, health = 3, 3, 6
	index = "DARKMOON_FAIRE~Demon Hunter~Minion~3~3~6~Demon~Insatiable Felhound~Taunt~Lifesteal~Corrupt~Uncollectible"
	requireTarget, effects, description = False, "Taunt,Lifesteal", "Taunt, Lifesteal"
	name_CN = "贪食地狱犬"


class InsatiableFelhound(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Insatiable Felhound"
	mana, attack, health = 3, 2, 5
	index = "DARKMOON_FAIRE~Demon Hunter~Minion~3~2~5~Demon~Insatiable Felhound~Taunt~ToCorrupt"
	requireTarget, effects, description = False, "Taunt", "Taunt. Corrupt: Gain +1/+1 and Lifesteal"
	name_CN = "贪食地狱犬"
	trigHand, corruptedType = Trig_Corrupt, InsatiableFelhound_Corrupt


class RelentlessPursuit(Spell):
	Class, school, name = "Demon Hunter", "", "Relentless Pursuit"
	requireTarget, mana, effects = False, 3, ""
	index = "DARKMOON_FAIRE~Demon Hunter~Spell~3~~Relentless Pursuit"
	description = "Give your hero +4 Attack and Immune this turn"
	name_CN = "冷酷追杀"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.giveHeroAttackArmor(self.ID, attGain=4, name=RelentlessPursuit)
		self.giveEnchant(self.Game.heroes[self.ID], effGain="Immune", name=RelentlessPursuit)
		self.Game.effects[self.ID]["ImmuneThisTurn"] += 1
		
		
class Stiltstepper(Minion):
	Class, race, name = "Demon Hunter", "", "Stiltstepper"
	mana, attack, health = 3, 4, 1
	index = "DARKMOON_FAIRE~Demon Hunter~Minion~3~4~1~~Stiltstepper~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Draw a card. If you play it this turn, give your hero +4 Attack this turn"
	name_CN = "高跷艺人"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		card, mana, entersHand = self.Game.Hand_Deck.drawCard(self.ID)
		if entersHand: Stiltstepper_Effect(self.Game, self.ID, card).connect()
		

#Even if hero is full health, the Lifesteal will still deal damage
class Ilgynoth(Minion):
	Class, race, name = "Demon Hunter", "", "Il'gynoth"
	mana, attack, health = 6, 4, 8
	index = "DARKMOON_FAIRE~Demon Hunter~Minion~6~4~8~~Il'gynoth~Lifesteal~Legendary"
	requireTarget, effects, description = False, "Lifesteal", "Lifesteal. Your Lifesteal damages the enemy hero instead of healing you"
	name_CN = "伊格诺斯"
	aura = GameRuleAura_Ilgynoth

		
class RenownedPerformer(Minion):
	Class, race, name = "Demon Hunter", "", "Renowned Performer"
	mana, attack, health = 4, 3, 3
	index = "DARKMOON_FAIRE~Demon Hunter~Minion~4~3~3~~Renowned Performer~Rush~Deathrattle"
	requireTarget, effects, description = False, "Rush", "Rush. Deathrattle: Summon two 1/1 Assistants with Rush"
	name_CN = "知名表演者"
	deathrattle = Death_RenownedPerformer


class PerformersAssistant(Minion):
	Class, race, name = "Demon Hunter", "", "Performer's Assistant"
	mana, attack, health = 1, 1, 1
	index = "DARKMOON_FAIRE~Demon Hunter~Minion~1~1~1~~Performer's Assistant~Taunt~Uncollectible"
	requireTarget, effects, description = False, "Taunt", "Taunt"
	name_CN = "演出助手"
	
	
class ZaitheIncredible(Minion):
	Class, race, name = "Demon Hunter", "", "Zai, the Incredible"
	mana, attack, health = 5, 5, 3
	index = "DARKMOON_FAIRE~Demon Hunter~Minion~5~5~3~~Zai, the Incredible~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: Copy the left- and right-most cards in your hand"
	name_CN = "扎依，出彩艺人"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		ownHand = self.Game.Hand_Deck.hands[self.ID]
		if ownHand:
			#需要更多考虑
			cards = [ownHand[0].selfCopy(self.ID, self), ownHand[-1].selfCopy(self.ID, self)]
			#Assume the copied cards BOTH occupy the right most position
			self.addCardtoHand(cards, self.ID)
		
		
class BladedLady(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Bladed Lady"
	mana, attack, health = 6, 6, 6
	index = "DARKMOON_FAIRE~Demon Hunter~Minion~6~6~6~Demon~Bladed Lady~Rush"
	requireTarget, effects, description = False, "Rush", "Rush. Costs (1) if your hero has 6 or more Attack"
	name_CN = "刀锋舞娘"
	trigHand = Trig_BladedLady
	def selfManaChange(self):
		if self.inHand and self.Game.heroes[self.ID].attack > 5:
			self.mana = 1
			

class ExpendablePerformers(Spell):
	Class, school, name = "Demon Hunter", "", "Expendable Performers"
	requireTarget, mana, effects = False, 7, ""
	index = "DARKMOON_FAIRE~Demon Hunter~Spell~7~~Expendable Performers"
	description = "Summon seven 1/1 Illidari with Rush. If they all die this turn, summon seven more"
	name_CN = "演员大接力"
	def available(self):
		return self.Game.space(self.ID) > 0
	#Don't need to all 7 Illidari to be summoned and die
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		minions = [IllidariInitiate(self.Game, self.ID) for i in range(7)]
		self.summon(minions)
		if minions := [minion for minion in minions if minion.onBoard]:
			ExpendablePerformers_Effect(self.Game, self.ID, minions).connect()


"""Druid Cards"""
class GuesstheWeight(Spell):
	Class, school, name = "Druid", "", "Guess the Weight"
	requireTarget, mana, effects = False, 2, ""
	index = "DARKMOON_FAIRE~Druid~Spell~2~~Guess the Weight"
	description = "Draw a card. Guess if your next card costs more or less to draw it"
	name_CN = "猜重量"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		game = self.Game
		card, firstCost = game.Hand_Deck.drawCard(self.ID)
		ownDeck = game.Hand_Deck.decks[self.ID]
		if card and ownDeck:
			secondCost = ownDeck[-1].mana
			self.chooseFixedOptions(GuesstheWeight, comment,
									options=[NextCostsMore(self.ID, firstCost, secondCost), 
											NextCostsLess(self.ID, firstCost, secondCost)])
			
	def discoverDecided(self, option, case, info_RNGSync=None, info_GUISync=None):
		if case != "Guided": self.Game.picks_Backup.append((info_RNGSync, info_GUISync, case == "Random", type(option)) )
		bingo = (isinstance(option, NextCostsLess) and option.firstCost > option.secondCost) \
				or (isinstance(option, NextCostsMore) and option.firstCost < option.secondCost)
		if self.Game.GUI: self.Game.GUI.revealaCardfromDeckAni(self.ID, -1, bingo)
		if bingo: self.Game.Hand_Deck.drawCard(self.ID)
		

class NextCostsMore(Option):
	name = "Costs More"
	index = ""
	mana, attack, health = 0, -1, -1
	def __init__(self, ID, firstCost=0, secondCost=0):
		super().__init__(ID=ID)
		self.description = "The next card costs more than %d"%firstCost
		self.firstCost, self.secondCost = firstCost, secondCost
		

class NextCostsLess(Option):
	name = "Costs Less"
	index = ""
	mana, attack, health = 0, -1, -1
	def __init__(self, ID, firstCost=0, secondCost=0):
		super().__init__()
		self.description = "The next card costs less than %d"%firstCost
		self.firstCost, self.secondCost = firstCost, secondCost
		
		
class LunarEclipse(Spell):
	Class, school, name = "Druid", "Arcane", "Lunar Eclipse"
	requireTarget, mana, effects = True, 2, ""
	index = "DARKMOON_FAIRE~Druid~Spell~2~Arcane~Lunar Eclipse"
	description = "Deal 3 damage to a minion. Your next spell this turn costs (2) less"
	name_CN = "月蚀"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard
		
	def text(self): return self.calcDamage(3)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.dealsDamage(target, self.calcDamage(3))
			GameManaAura_LunarEclipse(self.Game, self.ID).auraAppears()
		return target


class SolarEclipse(Spell):
	Class, school, name = "Druid", "Nature", "Solar Eclipse"
	requireTarget, mana, effects = False, 2, ""
	index = "DARKMOON_FAIRE~Druid~Spell~2~Nature~Solar Eclipse"
	description = "Your next spell this turn casts twice"
	name_CN = "日蚀"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.effects[self.ID]["Spells x2"] += 1
		SolarEclipse_Effect(self.Game, self.ID, self).connect()


#The card actually summons a treant that belongs in the darkmoonk pack. But the json id for this card somehow doesn't exist in HS's index
class FaireArborist_Corrupt(Minion):
	Class, race, name = "Druid", "", "Faire Arborist"
	mana, attack, health = 3, 2, 2
	index = "DARKMOON_FAIRE~Druid~Minion~3~2~2~~Faire Arborist~Corrupted~Uncollectible"
	requireTarget, effects, description = False, "", "Corrupted. Summon a 2/2 Treant. Draw a card"
	name_CN = "马戏团树艺师"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon(Treant_Darkmoon(self.Game, self.ID))
		self.Game.Hand_Deck.drawCard(self.ID)

class PrunetheFruit_Option(Option):
	name, description = "Prune the Fruit", "Draw a card"
	mana, attack, health = 3, -1, -1
	
class DigItUp_Option(Option):
	name, description = "Dig It Up", "Summon a 2/2 Treant"
	mana, attack, health = 3, -1, -1
	def available(self):
		return self.keeper.Game.space(self.keeper.ID) > 0

class FaireArborist(Minion):
	Class, race, name = "Druid", "", "Faire Arborist"
	mana, attack, health = 3, 2, 2
	index = "DARKMOON_FAIRE~Druid~Minion~3~2~2~~Faire Arborist~Choose One~ToCorrupt"
	requireTarget, effects, description = False, "", "Choose One- Draw a card; or Summon a 2/2 Treant. Corrupt: Do both"
	name_CN = "马戏团树艺师"
	trigHand, corruptedType = Trig_Corrupt, FaireArborist_Corrupt
	options = (PrunetheFruit_Option, DigItUp_Option)
	#对于抉择随从而言，应以与战吼类似的方式处理，打出时抉择可以保持到最终结算。但是打出时，如果因为鹿盔和发掘潜力而没有选择抉择，视为到对方场上之后仍然可以而没有如果没有
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if choice != 0: #"ChooseBoth" aura gives choice of -1
			self.summon(Treant_Darkmoon(self.Game, self.ID))
		if choice < 1:
			self.Game.Hand_Deck.drawCard(self.ID)

class Treant_Darkmoon(Minion):
	Class, race, name = "Druid", "", "Treant"
	mana, attack, health = 2, 2, 2
	index = "DARKMOON_FAIRE~Druid~Minion~2~2~2~~Treant~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "树人"


class MoontouchedAmulet_Corrupt(Spell):
	Class, school, name = "Druid", "", "Moontouched Amulet"
	requireTarget, mana, effects = False, 3, ""
	index = "DARKMOON_FAIRE~Druid~Spell~3~~Moontouched Amulet~Corrupted~Uncollectible"
	description = "Corrupted. Give your hero +4 Attack this turn. And gain 6 Armor"
	name_CN = "月触项链"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.giveHeroAttackArmor(self.ID, attGain=4, armor=6, name=MoontouchedAmulet_Corrupt)

class MoontouchedAmulet(Spell):
	Class, school, name = "Druid", "", "Moontouched Amulet"
	requireTarget, mana, effects = False, 3, ""
	index = "DARKMOON_FAIRE~Druid~Spell~3~~Moontouched Amulet~ToCorrupt"
	description = "Give your hero +4 Attack this turn. Corrupt: And gain 6 Armor"
	name_CN = "月触项链"
	trigHand, corruptedType = Trig_Corrupt, MoontouchedAmulet_Corrupt
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.giveHeroAttackArmor(self.ID, attGain=4, name=MoontouchedAmulet)
		
		
class KiriChosenofElune(Minion):
	Class, race, name = "Druid", "", "Kiri, Chosen of Elune"
	mana, attack, health = 4, 2, 2
	index = "DARKMOON_FAIRE~Druid~Minion~4~2~2~~Kiri, Chosen of Elune~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: Add a Solar Eclipse and Lunar Eclipse to your hand"
	name_CN = "基利，艾露恩之眷"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.addCardtoHand([SolarEclipse, LunarEclipse], self.ID)
		
		
class Greybough(Minion):
	Class, race, name = "Druid", "", "Greybough"
	mana, attack, health = 5, 4, 6
	index = "DARKMOON_FAIRE~Druid~Minion~5~4~6~~Greybough~Taunt~Deathrattle~Legendary"
	requireTarget, effects, description = False, "Taunt", "Taunt. Deathrattle: Give a random friendly minion 'Deathrattle: Summon Greybough'"
	name_CN = "格雷布"
	deathrattle = Death_Greybough


class UmbralOwl(Minion):
	Class, race, name = "Druid", "Beast", "Umbral Owl"
	mana, attack, health = 7, 4, 4
	index = "DARKMOON_FAIRE~Druid~Minion~7~4~4~Beast~Umbral Owl~Rush"
	requireTarget, effects, description = False, "Rush", "Rush. Costs (1) less for each spell you've cast this game"
	name_CN = "幽影猫头鹰"
	trigHand = Trig_UmbralOwl		
	def selfManaChange(self):
		if self.inHand:
			self.mana -= sum(issubclass(card, Spell) for card in self.Game.Counters.cardsPlayedThisGame[self.ID])
			self.mana = max(self.mana, 0)


class CenarionWard(Spell):
	Class, school, name = "Druid", "Nature", "Cenarion Ward"
	requireTarget, mana, effects = False, 8, ""
	index = "DARKMOON_FAIRE~Druid~Spell~8~Nature~Cenarion Ward"
	description = "Gain 8 Armor. Summon a random 8-Cost minion"
	name_CN = "塞纳里奥结界"
	poolIdentifier = "8-Cost Minions to Summon"
	@classmethod
	def generatePool(cls, pools):
		return "8-Cost Minions to Summon", pools.MinionsofCost[8]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.giveHeroAttackArmor(self.ID, armor=8)
		self.summon(numpyChoice(self.rngPool("8-Cost Minions to Summon"))(self.Game, self.ID))
		
		
class FizzyElemental(Minion):
	Class, race, name = "Druid", "Elemental", "Fizzy Elemental"
	mana, attack, health = 9, 10, 10
	index = "DARKMOON_FAIRE~Druid~Minion~9~10~10~Elemental~Fizzy Elemental~Rush~Taunt"
	requireTarget, effects, description = False, "Rush,Taunt", "Rush, Taunt"
	name_CN = "泡沫元素"
	

"""Hunter Cards"""
class MysteryWinner(Minion):
	Class, race, name = "Hunter", "", "Mystery Winner"
	mana, attack, health = 1, 1, 1
	index = "DARKMOON_FAIRE~Hunter~Minion~1~1~1~~Mystery Winner~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Discover a Secret"
	name_CN = "神秘获奖者"
	poolIdentifier = "Hunter Secrets"
	@classmethod
	def generatePool(cls, pools):
		classes, lists = [], []
		for Class in pools.Classes:
			secrets = [card for card in pools.ClassCards[Class] if card.race == "Secret"]
			if secrets:
				classes.append(Class + " Secrets")
				lists.append(secrets)
		return classes, lists

	def decideSecretPool(self):
		HeroClass = self.Game.heroes[self.ID].Class
		key = HeroClass + " Secrets" if HeroClass in ["Hunter", "Mage", "Paladin", "Rogue"] else "Hunter Secrets"
		return self.rngPool(key)
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverandGenerate(MysteryWinner, comment, lambda : MysteryWinner.decideSecretPool(self))


class DancingCobra_Corrupt(Minion):
	Class, race, name = "Hunter", "Beast", "Dancing Cobra"
	mana, attack, health = 2, 1, 5
	index = "DARKMOON_FAIRE~Hunter~Minion~2~1~5~Beast~Dancing Cobra~Poisonous~Corrupted~Uncollectible"
	requireTarget, effects, description = False, "Poisonous", "Poisonous"
	name_CN = "舞动的眼镜蛇"


class DancingCobra(Minion):
	Class, race, name = "Hunter", "Beast", "Dancing Cobra"
	mana, attack, health = 2, 1, 5
	index = "DARKMOON_FAIRE~Hunter~Minion~2~1~5~Beast~Dancing Cobra~ToCorrupt"
	requireTarget, effects, description = False, "", "Corrupt: Gain Poisonous"
	name_CN = "舞动的眼镜蛇"
	trigHand, corruptedType = Trig_Corrupt, DancingCobra_Corrupt


class DontFeedtheAnimals_Corrupt(Spell):
	Class, school, name = "Hunter", "", "Don't Feed the Animals"
	requireTarget, mana, effects = False, 2, ""
	index = "DARKMOON_FAIRE~Hunter~Spell~2~~Don't Feed the Animals~Corrupted~Uncollectible"
	description = "Corrupted. Give all Beasts in your hand +2/+2"
	name_CN = "请勿投食"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.AOE_GiveEnchant([card for card in self.Game.Hand_Deck.hands[self.ID] if "Beast" in card.race],
							2, 2, name=DontFeedtheAnimals_Corrupt, add2EventinGUI=False)

class DontFeedtheAnimals(Spell):
	Class, school, name = "Hunter", "", "Don't Feed the Animals"
	requireTarget, mana, effects = False, 2, ""
	index = "DARKMOON_FAIRE~Hunter~Spell~2~~Don't Feed the Animals~ToCorrupt"
	description = "Give all Beasts in your hand +1/+1. Corrupt: Give them +2/+2 instead"
	name_CN = "请勿投食"
	trigHand, corruptedType = Trig_Corrupt, DontFeedtheAnimals_Corrupt
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.AOE_GiveEnchant([card for card in self.Game.Hand_Deck.hands[self.ID] if "Beast" in card.race], 
							1, 1, name=DontFeedtheAnimals, add2EventinGUI=False)

		
class OpentheCages(Secret):
	Class, school, name = "Hunter", "", "Open the Cages"
	requireTarget, mana, effects = False, 2, ""
	index = "DARKMOON_FAIRE~Hunter~Spell~2~~Open the Cages~~Secret"
	description = "Secret: When your turn starts, if you control two minions, summon an Animal Companion"
	name_CN = "打开兽笼"
	trigBoard = Trig_OpentheCages		


class PettingZoo(Spell):
	Class, school, name = "Hunter", "", "Petting Zoo"
	requireTarget, mana, effects = False, 3, ""
	index = "DARKMOON_FAIRE~Hunter~Spell~3~~Petting Zoo"
	description = "Summon a 3/3 Strider. Repeat for each Secret you control"
	name_CN = "宠物乐园"
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def effCanTrig(self):
		self.effectViable = self.Game.Secrets.secrets[self.ID] != []
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon(DarkmoonStrider(self.Game, self.ID))
		for i in range(len(self.Game.Secrets.secrets[self.ID])):
			self.summon(DarkmoonStrider(self.Game, self.ID))
		

class DarkmoonStrider(Minion):
	Class, race, name = "Hunter", "Beast", "Darkmoon Strider"
	mana, attack, health = 3, 3, 3
	index = "DARKMOON_FAIRE~Hunter~Minion~3~3~3~Beast~Darkmoon Strider~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "暗月陆行鸟"
	
	
class RinlingsRifle(Weapon):
	Class, name, description = "Hunter", "Rinling's Rifle", "After your hero attacks, Discover a Secret and cast it"
	mana, attack, durability, effects = 4, 2, 2, ""
	index = "DARKMOON_FAIRE~Hunter~Weapon~4~2~2~Rinling's Rifle~Legendary"
	name_CN = "瑞林的步枪"
	poolIdentifier = "Hunter Secrets"
	@classmethod
	def generatePool(cls, pools):
		classes, lists = [], []
		for Class in pools.Classes:
			secrets = [card for card in pools.ClassCards[Class] if card.race == "Secret"]
			if secrets:
				classes.append(Class + " Secrets")
				lists.append(secrets)
		return classes, lists

	trigBoard = Trig_RinlingsRifle	
	def decideSecretPool(self):
		HeroClass = self.Game.heroes[self.ID].Class
		key = HeroClass + " Secrets" if HeroClass in ["Hunter", "Mage", "Paladin", "Rogue"] else "Hunter Secrets"
		pool = self.rngPool(key)[:]
		for secret in self.Game.Secrets.secrets[self.ID]:
			removefrom(type(secret), pool)  #Deployed Secrets won't show up in the options
		return pool
	
	#case here must be "Discovered" or "Guided"
	def discoverDecided(self, option, case, info_RNGSync=None, info_GUISync=None):
		if case != "Guided": self.Game.picks_Backup.append((info_RNGSync, info_GUISync, case == "Random", type(option)))
		option.creator = RinlingsRifle
		option.cast()
		

class TramplingRhino(Minion):
	Class, race, name = "Hunter", "Beast", "Trampling Rhino"
	mana, attack, health = 5, 5, 5
	index = "DARKMOON_FAIRE~Hunter~Minion~5~5~5~Beast~Trampling Rhino~Rush"
	requireTarget, effects, description = False, "Rush", "Rush. Afte this attacks and kills a minion, excess damage hits the enemy hero"
	name_CN = "狂踏的犀牛"
	trigBoard = Trig_TramplingRhino		


#Even minions with "Can't attack heroes" still attack hero under her command
#The battlecry alone will not kill the minion summoned.
class MaximaBlastenheimer(Minion):
	Class, race, name = "Hunter", "", "Maxima Blastenheimer"
	mana, attack, health = 6, 4, 4
	index = "DARKMOON_FAIRE~Hunter~Minion~6~4~4~~Maxima Blastenheimer~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: Summon a random minion from your deck. It attacks the enemy hero, then dies"
	name_CN = "玛克希玛·雷管"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if minion := self.try_SummonfromDeck(self.pos + 1):
			#verifySelectable is exclusively for player ordering chars to attack
			self.Game.battle(minion, self.Game.heroes[3-self.ID], verifySelectable=False, useAttChance=True, resolveDeath=False, resetRedirTrig=True)
			if minion.onBoard: self.Game.kill(self, minion)
		
		
class DarkmoonTonk(Minion):
	Class, race, name = "Hunter", "Mech", "Darkmoon Tonk"
	mana, attack, health = 7, 8, 5
	index = "DARKMOON_FAIRE~Hunter~Minion~7~8~5~Mech~Darkmoon Tonk~Deathrattle"
	requireTarget, effects, description = False, "", "Deathrattle: Fire four missiles at random enemies that deal 2 damage each"
	name_CN = "暗月坦克"
	deathrattle = Death_DarkmoonTonk


class JewelofNZoth(Spell):
	Class, school, name = "Hunter", "", "Jewel of N'Zoth"
	requireTarget, mana, effects = False, 8, ""
	index = "DARKMOON_FAIRE~Hunter~Spell~8~~Jewel of N'Zoth"
	description = "Summon three friendly Deathrattle minions that died this game"
	name_CN = "恩佐斯宝石"
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		game = self.Game
		minions = [card for card in game.Counters.minionsDiedThisGame[self.ID] if "~Deathrattle" in card.index]
		if minions:
			minions = numpyChoice(minions, min(3, len(minions)), replace=False)
			self.summon([minion(game, self.ID) for minion in minions])
		

"""Mage Cards"""
class ConfectionCyclone(Minion):
	Class, race, name = "Mage", "Elemental", "Confection Cyclone"
	mana, attack, health = 2, 3, 2
	index = "DARKMOON_FAIRE~Mage~Minion~2~3~2~Elemental~Confection Cyclone~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Add two 1/2 Sugar Elementals to your hand"
	name_CN = "甜点飓风"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.addCardtoHand([SugarElemental] * 2, self.ID)

class SugarElemental(Minion):
	Class, race, name = "Mage", "Elemental", "Sugar Elemental"
	mana, attack, health = 1, 1, 2
	index = "DARKMOON_FAIRE~Mage~Minion~1~1~2~Elemental~Sugar Elemental~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "甜蜜元素"
	
	
class DeckofLunacy(Spell):
	Class, school, name = "Mage", "", "Deck of Lunacy"
	requireTarget, mana, effects = False, 4, ""
	index = "DARKMOON_FAIRE~Mage~Spell~4~~Deck of Lunacy~Legendary"
	description = "Transform spells in your deck into ones that cost (3) more. (They keep their original Cost.)"
	name_CN = "愚人套牌"
	poolIdentifier = "3-Cost Spells"
	@classmethod
	def generatePool(cls, pools):
		spells = {mana: [] for mana in range(3, 11)}
		for cards in pools.ClassCards.values():
			for card in cards:
				if card.category == "Spell" and 2 < card.mana < 11:
					spells[card.mana].append(card)
		return ["%d-Cost Spells"%cost for cost in spells.keys()], spells.values()
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame, ID = self.Game, self.ID
		indices, newCards, costs = [], [], []
		for i, card in enumerate(curGame.Hand_Deck.decks[ID]):
			if card.category == "Spell":
				indices.append(i)
				newCards.append(numpyChoice(self.rngPool("%d-Cost Spells"%min(10, card.mana+3))))
				costs.append(card.mana)
		if indices:
			newCards = [card(curGame, ID) for card in newCards]
			for card, cost in zip(newCards, costs): card.manaMods.append(ManaMod(card, to=cost))
			curGame.Hand_Deck.replacePartofDeck(ID, indices, newCards)


class GameMaster(Minion):
	Class, race, name = "Mage", "", "Game Master"
	mana, attack, health = 2, 2, 3
	index = "DARKMOON_FAIRE~Mage~Minion~2~2~3~~Game Master"
	requireTarget, effects, description = False, "", "The first Secret you play each turn costs (1)"
	name_CN = "游戏管理员"
	aura = ManaAura_GameMaster

		
class RiggedFaireGame(Secret):
	Class, school, name = "Mage", "", "Rigged Faire Game"
	requireTarget, mana, effects = False, 3, ""
	index = "DARKMOON_FAIRE~Mage~Spell~3~~Rigged Faire Game~~Secret"
	description = "Secret: If you didn't take any damage during your opponent's turn, draw 3 cards"
	name_CN = "非公平游戏"
	trigBoard = Trig_RiggedFaireGame		


class OccultConjurer(Minion):
	Class, race, name = "Mage", "", "Occult Conjurer"
	mana, attack, health = 4, 4, 4
	index = "DARKMOON_FAIRE~Mage~Minion~4~4~4~~Occult Conjurer~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: If you control a Secret, summon a copy of this"
	name_CN = "隐秘咒术师"
	
	def effCanTrig(self):
		self.effectViable = self.Game.Secrets.secrets[self.ID] != []
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Secrets.secrets[self.ID]:
			Copy = self.selfCopy(self.ID, self) if self.onBoard else type(self)(self.Game, self.ID)
			self.summon(Copy)
		

class RingToss_Corrupt(Spell):
	Class, school, name = "Mage", "", "Ring Toss"
	requireTarget, mana, effects = False, 4, ""
	index = "DARKMOON_FAIRE~Mage~Spell~4~~Ring Toss~Corrupted~Uncollectible"
	description = "Corrupted. Discover 2 Secrets and cast them"
	name_CN = "套圈圈"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for num in range(2):
			self.discoverandGenerate(RingToss, comment, lambda: RingToss.decideSecretPool(self))


class RingToss(Spell):
	Class, school, name = "Mage", "", "Ring Toss"
	requireTarget, mana, effects = False, 4, ""
	index = "DARKMOON_FAIRE~Mage~Spell~4~~Ring Toss~ToCorrupt"
	description = "Discover a Secret and cast it. Corrupt: Discover 2 instead"
	name_CN = "套圈圈"
	trigHand, corruptedType = Trig_Corrupt, RingToss_Corrupt
	poolIdentifier = "Mage Secrets"
	@classmethod
	def generatePool(cls, pools):
		classes, lists = [], []
		for Class in pools.Classes:
			secrets = [card for card in pools.ClassCards[Class] if card.race == "Secret"]
			if secrets:
				classes.append(Class + " Secrets")
				lists.append(secrets)
		return classes, lists
	
	def decideSecretPool(self):
		HeroClass = self.Game.heroes[self.ID].Class
		key = HeroClass + " Secrets" if HeroClass in ["Hunter", "Mage", "Paladin", "Rogue"] else "Mage Secrets"
		pool = self.rngPool(key)[:]
		for secret in self.Game.Secrets.secrets[self.ID]:
			removefrom(type(secret), pool)
		return pool
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverandGenerate(RingToss, comment, lambda : RingToss.decideSecretPool(self))
		
	def discoverDecided(self, option, case, info_RNGSync=None, info_GUISync=None):
		if case != "Guided": self.Game.picks_Backup.append((info_RNGSync, info_GUISync, case == "Random", type(option)))
		option.creator = RingToss
		option.cast()


class FireworkElemental_Corrupt(Minion):
	Class, race, name = "Mage", "Elemental", "Firework Elemental"
	mana, attack, health = 5, 3, 5
	index = "DARKMOON_FAIRE~Mage~Minion~5~3~5~Elemental~Firework Elemental~Battlecry~Corrupted~Uncollectible"
	requireTarget, effects, description = True, "", "Corrupted. Battlecry: Deal 12 damage to a minion"
	name_CN = "焰火元素"
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.dealsDamage(target, 12)
		return target


class FireworkElemental(Minion):
	Class, race, name = "Mage", "Elemental", "Firework Elemental"
	mana, attack, health = 5, 3, 5
	index = "DARKMOON_FAIRE~Mage~Minion~5~3~5~Elemental~Firework Elemental~Battlecry~ToCorrupt"
	requireTarget, effects, description = True, "", "Battlecry: Deal 3 damage to a minion. Corrupt: Deal 12 damage instead"
	name_CN = "焰火元素"
	trigHand, corruptedType = Trig_Corrupt, FireworkElemental_Corrupt
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.dealsDamage(target, 3)
		return target

		
class SaygeSeerofDarkmoon(Minion):
	Class, race, name = "Mage", "", "Sayge, Seer of Darkmoon"
	mana, attack, health = 6, 5, 5
	index = "DARKMOON_FAIRE~Mage~Minion~6~5~5~~Sayge, Seer of Darkmoon~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: Draw 1 card(Upgraded for each friendly Secret that has triggered this game!)"
	name_CN = "暗月先知赛格"
	def text(self): return self.Game.Counters.numSecretsTriggeredThisGame[self.ID] + 1

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for _ in range(self.Game.Counters.numSecretsTriggeredThisGame[self.ID] + 1):
			self.Game.Hand_Deck.drawCard(self.ID)
		
		
class MaskofCThun(Spell):
	Class, school, name = "Mage", "", "Mask of C'Thun"
	requireTarget, mana, effects = False, 7, ""
	index = "DARKMOON_FAIRE~Mage~Spell~7~~Mask of C'Thun"
	description = "Deal 10 damage randomly split among all enemies"
	name_CN = "克苏恩面具"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		side, game = 3-self.ID, self.Game
		for _ in range(self.calcDamage(10)):
			if objs := game.charsAlive(side): self.dealsDamage(numpyChoice(objs), 1)
			else: break
		
		
class GrandFinale(Spell):
	Class, school, name = "Mage", "Fire", "Grand Finale"
	requireTarget, mana, effects = False, 8, ""
	index = "DARKMOON_FAIRE~Mage~Spell~8~Fire~Grand Finale"
	description = "Summon an 8/8 Elemental. Repeat for each Elemental you played last turn"
	name_CN = "华丽谢幕"
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.numElementalsPlayedLastTurn[self.ID] > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		game = self.Game
		self.summon(ExplodingSparkler(game, self.ID))
		for i in range(game.Counters.numElementalsPlayedLastTurn[self.ID]):
			self.summon(ExplodingSparkler(game, self.ID))
		
class ExplodingSparkler(Minion):
	Class, race, name = "Mage", "Elemental", "Exploding Sparkler"
	mana, attack, health = 8, 8, 8
	index = "DARKMOON_FAIRE~Mage~Minion~8~8~8~Elemental~Exploding Sparkler~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "爆破烟火"
	

"""Paladin Cards"""
class OhMyYogg(Secret):
	Class, school, name = "Paladin", "Shadow", "Oh My Yogg!"
	requireTarget, mana, effects = False, 1, ""
	index = "DARKMOON_FAIRE~Paladin~Spell~1~Shadow~Oh My Yogg!~~Secret"
	description = "Secret: When your opponent casts a spell, they instead cast a random one of the same Cost"
	name_CN = "古神在上"
	poolIdentifier = "0-Cost Spells"
	@classmethod
	def generatePool(cls, pools):
		spells = {mana: [] for mana in range(3, 11)}
		for cards in pools.ClassCards.values():
			for card in cards:
				if card.category == "Spell" and 2 < card.mana < 11:
					spells[card.mana].append(card)
		return ["%d-Cost Spells" % cost for cost in spells.keys()], spells.values()
	
	trigBoard = Trig_OhMyYogg		


class RedscaleDragontamer(Minion):
	Class, race, name = "Paladin", "Murloc", "Redscale Dragontamer"
	mana, attack, health = 2, 2, 3
	index = "DARKMOON_FAIRE~Paladin~Minion~2~2~3~Murloc~Redscale Dragontamer~Deathrattle"
	requireTarget, effects, description = False, "", "Deathrattle: Draw a Dragon"
	name_CN = "赤鳞驯龙者"
	deathrattle = Death_RedscaleDragontamer


class SnackRun(Spell):
	Class, school, name = "Paladin", "", "Snack Run"
	requireTarget, mana, effects = False, 2, ""
	index = "DARKMOON_FAIRE~Paladin~Spell~2~~Snack Run"
	description = "Discover a spell. Restore Health to your hero equal to its Cost"
	name_CN = "零食大冲关"
	poolIdentifier = "Paladin Spells"
	@classmethod
	def generatePool(cls, pools):
		return [Class+" Spells" for Class in pools.Classes], \
				[[card for card in cards if card.category == "Spell"] for cards in pools.ClassCards.values()]

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverandGenerate(SnackRun, comment, lambda : self.rngPool(classforDiscover(self) + " Spells"))
		
	def discoverDecided(self, option, case, info_RNGSync=None, info_GUISync=None):
		heal = self.calcHeal(option.mana )
		self.handleDiscoverGeneratedCard(option, case, info_RNGSync, info_GUISync)
		self.restoresHealth(self.Game.heroes[self.ID], heal)
		
		
class CarnivalBarker(Minion):
	Class, race, name = "Paladin", "", "Carnival Barker"
	mana, attack, health = 3, 3, 2
	index = "DARKMOON_FAIRE~Paladin~Minion~3~3~2~~Carnival Barker"
	requireTarget, effects, description = False, "", "Whenever you summon a 1-Health minion, give +1/+2"
	name_CN = "狂欢报幕员"
	trigBoard = Trig_CarnivalBarker		


class DayattheFaire_Corrupt(Spell):
	Class, school, name = "Paladin", "", "Day at the Faire"
	requireTarget, mana, effects = False, 3, ""
	index = "DARKMOON_FAIRE~Paladin~Spell~3~~Day at the Faire~Corrupted~Uncollectible"
	description = "Corrupted: Summon 5 Silver Hand Recruits"
	name_CN = "游园日"
	def available(self):
		return self.Game.space(self.ID) > 0

	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		self.summon([SilverHandRecruit(self.Game, self.ID)  for _ in (0, 1, 2, 3, 4)])


class DayattheFaire(Spell):
	Class, school, name = "Paladin", "", "Day at the Faire"
	requireTarget, mana, effects = False, 3, ""
	index = "DARKMOON_FAIRE~Paladin~Spell~3~~Day at the Faire~ToCorrupt"
	description = "Summon 3 Silver Hand Recruits. Corrupt: Summon 5"
	name_CN = "游园日"
	trigHand, corruptedType = Trig_Corrupt, DayattheFaire_Corrupt
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		self.summon([SilverHandRecruit(self.Game, self.ID) for _ in (0, 1, 2)])

		
class BalloonMerchant(Minion):
	Class, race, name = "Paladin", "", "Balloon Merchant"
	mana, attack, health = 4, 3, 5
	index = "DARKMOON_FAIRE~Paladin~Minion~4~3~5~~Balloon Merchant~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Give your Silver Hand Recruits +1 Attack and Divine Shield"
	name_CN = "气球商人"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.AOE_GiveEnchant([minion for minion in self.Game.minionsonBoard(self.ID) if minion.name == "Silver Hand Recruit"],
							 1, 0, effGain="Divine Shield", name=BalloonMerchant)


class CarouselGryphon_Corrupt(Minion):
	Class, race, name = "Paladin", "Mech", "Carousel Gryphon"
	mana, attack, health = 5, 8, 8
	index = "DARKMOON_FAIRE~Paladin~Minion~5~8~8~Mech~Carousel Gryphon~Divine Shield~Taunt~Corrupted~Uncollectible"
	requireTarget, effects, description = False, "Divine Shield,Taunt", "Divine Shield, Taunt"
	name_CN = "旋转木马"

class CarouselGryphon(Minion):
	Class, race, name = "Paladin", "Mech", "Carousel Gryphon"
	mana, attack, health = 5, 5, 5
	index = "DARKMOON_FAIRE~Paladin~Minion~5~5~5~Mech~Carousel Gryphon~Divine Shield~ToCorrupt"
	requireTarget, effects, description = False, "Divine Shield", "Divine Shield. Corrupt: Gain +3/+3 and Taunt"
	name_CN = "旋转木马"
	trigHand, corruptedType = Trig_Corrupt, CarouselGryphon_Corrupt

	
class LothraxiontheRedeemed(Minion):
	Class, race, name = "Paladin", "Demon", "Lothraxion the Redeemed"
	mana, attack, health = 5, 5, 5
	index = "DARKMOON_FAIRE~Paladin~Minion~5~5~5~Demon~Lothraxion the Redeemed~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: For the rest of the game, after you summon a Silver Hand Recruit, give it Divine Shield"
	name_CN = "救赎者洛萨克森"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		LothraxiontheRedeemed_Effect(self.Game, self.ID).connect()
		

class HammeroftheNaaru(Weapon):
	Class, name, description = "Paladin", "Hammer of the Naaru", "Battlecry: Summon a 6/6 Holy Elemental with Taunt"
	mana, attack, durability, effects = 6, 3, 3, ""
	index = "DARKMOON_FAIRE~Paladin~Weapon~6~3~3~Hammer of the Naaru~Battlecry"
	name_CN = "纳鲁之锤"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon(HolyElemental(self.Game, self.ID))

class HolyElemental(Minion):
	Class, race, name = "Paladin", "Elemental", "Holy Elemental"
	mana, attack, health = 6, 6, 6
	index = "DARKMOON_FAIRE~Paladin~Minion~6~6~6~Elemental~Holy Elemental~Taunt~Uncollectible"
	requireTarget, effects, description = False, "Taunt", "Taunt"
	name_CN = "神圣元素"
	
	
class HighExarchYrel(Minion):
	Class, race, name = "Paladin", "", "High Exarch Yrel"
	mana, attack, health = 8, 7, 5
	index = "DARKMOON_FAIRE~Paladin~Minion~8~7~5~~High Exarch Yrel~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: If your deck has no Neutral cards, gain Rush, Lifesteal, Taunt, and Divine Shield"
	name_CN = "大主教伊瑞尔"
	
	def effCanTrig(self):
		self.effectViable = all(card.Class != "Neutral" for card in self.Game.Hand_Deck.decks[self.ID])
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if all(card.Class != "Neutral" for card in self.Game.Hand_Deck.decks[self.ID]):
			self.giveEnchant(self, multipleEffGains=(("Rush", 1, None), ("Lifesteal", 1, None),
													 ("Taunt", 1, None), ("Divine Shield", 1, None)),
							 name=HighExarchYrel)
		

"""Priest Cards"""
class Insight_Corrupt(Spell):
	Class, school, name = "Priest", "Shadow", "Insight"
	requireTarget, mana, effects = False, 2, ""
	index = "DARKMOON_FAIRE~Priest~Spell~2~Shadow~Insight~Corrupted~Uncollectible"
	description = "Corrupted. Draw a minion. Reduce its Cost by (2)"
	name_CN = "洞察"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		card, mana, entersHand = self.drawCertainCard(lambda card: card.category == "Minion")
		if entersHand: ManaMod(card, by=-2).applies()

class Insight(Spell):
	Class, school, name = "Priest", "Shadow", "Insight"
	requireTarget, mana, effects = False, 2, ""
	index = "DARKMOON_FAIRE~Priest~Spell~2~Shadow~Insight~ToCorrupt"
	description = "Draw a minion. Corrupt: Reduce its Cost by (2)"
	name_CN = "洞察"
	trigHand, corruptedType = Trig_Corrupt, Insight_Corrupt
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.drawCertainCard(lambda card: card.category == "Minion")


class FairgroundFool_Corrupt(Minion):
	Class, race, name = "Priest", "", "Fairground Fool"
	mana, attack, health = 3, 4, 7
	index = "DARKMOON_FAIRE~Priest~Minion~3~4~7~~Fairground Fool~Taunt~Corrupted~Uncollectible"
	requireTarget, effects, description = False, "Taunt", "Corrupted. Taunt"
	name_CN = "游乐园小丑"


class FairgroundFool(Minion):
	Class, race, name = "Priest", "", "Fairground Fool"
	mana, attack, health = 3, 4, 3
	index = "DARKMOON_FAIRE~Priest~Minion~3~4~3~~Fairground Fool~Taunt~ToCorrupt"
	requireTarget, effects, description = False, "Taunt", "Taunt. Corrupt: Gain +4 Health"
	name_CN = "游乐园小丑"
	trigHand, corruptedType = Trig_Corrupt, FairgroundFool_Corrupt
	
	
class NazmaniBloodweaver(Minion):
	Class, race, name = "Priest", "", "Nazmani Bloodweaver"
	mana, attack, health = 3, 2, 5
	index = "DARKMOON_FAIRE~Priest~Minion~3~2~5~~Nazmani Bloodweaver"
	requireTarget, effects, description = False, "", "After you cast a spell, reduce the Cost of a random card in your hand by (1)"
	name_CN = "纳兹曼尼织血者"
	trigBoard = Trig_NazmaniBloodweaver		


class PalmReading(Spell):
	Class, school, name = "Priest", "Shadow", "Palm Reading"
	requireTarget, mana, effects = False, 3, ""
	index = "DARKMOON_FAIRE~Priest~Spell~3~Shadow~Palm Reading"
	description = "Discover a spell. Reduce the Cost of spells in your hand by (1)"
	name_CN = "解读手相"
	poolIdentifier = "Priest Spells"
	@classmethod
	def generatePool(cls, pools):
		return [Class+" Spells" for Class in pools.Classes], \
				[[card for card in cards if card.category == "Spell"] for cards in pools.ClassCards.values()]

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverandGenerate(PalmReading, comment, lambda : self.rngPool(classforDiscover(self)+" Spells"))
		for card in self.Game.Hand_Deck.hands[self.ID]:
			if card.category == "Spell": ManaMod(card, by=-1).applies()


class AuspiciousSpirits_Corrupt(Spell):
	Class, school, name = "Priest", "Shadow", "Auspicious Spirits"
	requireTarget, mana, effects = False, 4, ""
	index = "DARKMOON_FAIRE~Priest~Spell~4~Shadow~Auspicious Spirits~Corrupted~Uncollectible"
	description = "Corrupted. Summon a 7-Cost minion"
	name_CN = "吉兆"
	poolIdentifier = "7-Cost Minions to Summon"
	@classmethod
	def generatePool(cls, pools):
		return "7-Cost Minions to Summon", pools.MinionsofCost[7]

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon(numpyChoice(self.rngPool("7-Cost Minions to Summon"))(self.Game, self.ID))


class AuspiciousSpirits(Spell):
	Class, school, name = "Priest", "Shadow", "Auspicious Spirits"
	requireTarget, mana, effects = False, 4, ""
	index = "DARKMOON_FAIRE~Priest~Spell~4~Shadow~Auspicious Spirits~ToCorrupt"
	description = "Summon a random 4-Cost minion. Corrupt: Summon a 7-Cost minion instead"
	name_CN = "吉兆"
	trigHand, corruptedType = Trig_Corrupt, AuspiciousSpirits_Corrupt
	poolIdentifier = "4-Cost Minions to Summon"
	@classmethod
	def generatePool(cls, pools):
		return "4-Cost Minions to Summon", pools.MinionsofCost[4]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon(numpyChoice(self.rngPool("4-Cost Minions to Summon"))(self.Game, self.ID))
		

class TheNamelessOne(Minion):
	Class, race, name = "Priest", "", "The Nameless One"
	mana, attack, health = 4, 4, 4
	index = "DARKMOON_FAIRE~Priest~Minion~4~4~4~~The Nameless One~Battlecry~Legendary"
	requireTarget, effects, description = True, "", "Battlecry: Choose a minion. Become a 4/4 copy of it, then Silence it"
	name_CN = "无名者"
	
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			if not self.dead and self.Game.minionPlayed == self and (self.onBoard or self.inHand): #战吼触发时自己不能死亡。
				Copy = target.selfCopy(self.ID, self, 4, 4) if target.onBoard or target.inHand else type(target)(self.Game, self.ID)
				self.transform(self, Copy)
			target.getsSilenced()
		return target
		
		
class FortuneTeller(Minion):
	Class, race, name = "Priest", "Mech", "Fortune Teller"
	mana, attack, health = 5, 3, 3
	index = "DARKMOON_FAIRE~Priest~Minion~5~3~3~Mech~Fortune Teller~Taunt~Battlecry"
	requireTarget, effects, description = False, "Taunt", "Taunt. Battlecry: Gain +1/+1 for each spell in your hand"
	name_CN = "占卜机"
	#For self buffing effects, being dead and removed before battlecry will prevent the battlecry resolution.
	#If this minion is returned hand before battlecry, it can still buff it self according to living friendly minions.
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.onBoard or self.inHand: #For now, no battlecry resolution shuffles this into deck.
			num = sum(card.category == "Spell" for card in self.Game.Hand_Deck.hands[self.ID])
			self.giveEnchant(self, num, num, name=FortuneTeller)
		
		
class IdolofYShaarj(Spell):
	Class, school, name = "Priest", "", "Idol of Y'Shaarj"
	requireTarget, mana, effects = False, 8, ""
	index = "DARKMOON_FAIRE~Priest~Spell~8~~Idol of Y'Shaarj"
	description = "Summon a 10/10 copy of a minion in your deck"
	name_CN = "亚煞极神像"
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		minions = [card for card in self.Game.Hand_Deck.decks[self.ID] if card.category == "Minion"]
		if minions: self.summon(numpyChoice(minions).selfCopy(self.ID, self, attack=10, health=10))
		
		
class GhuuntheBloodGod(Minion):
	Class, race, name = "Priest", "", "G'huun the Blood God"
	mana, attack, health = 8, 8, 8
	index = "DARKMOON_FAIRE~Priest~Minion~8~8~8~~G'huun the Blood God~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Draw 2 cards. They cost Health instead of Mana"
	name_CN = "戈霍恩，鲜血之神"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for _ in (0, 1):
			card, mana, entersHand = self.Game.Hand_Deck.drawCard(self.ID)
			if entersHand: self.giveEnchant(card, effGain="Cost Health Instead", name=GhuuntheBloodGod)
			
			
class BloodofGhuun(Minion):
	Class, race, name = "Priest", "Elemental", "Blood of G'huun"
	mana, attack, health = 9, 8, 8
	index = "DARKMOON_FAIRE~Priest~Minion~9~8~8~Elemental~Blood of G'huun~Taunt"
	requireTarget, effects, description = False, "Taunt", "Taunt. At the end of your turn, summon a 5/5 copy of a minion in your deck"
	name_CN = "戈霍恩之血"
	trigBoard = Trig_BloodofGhuun


"""Rogue Cards"""
class PrizePlunderer(Minion):
	Class, race, name = "Rogue", "Pirate", "Prize Plunderer"
	mana, attack, health = 1, 2, 1
	index = "DARKMOON_FAIRE~Rogue~Minion~1~2~1~Pirate~Prize Plunderer~Combo"
	requireTarget, effects, description = True, "", "Combo: Deal 1 damage to a minion for each other card you've played this turn"
	name_CN = "奖品掠夺者"
	def needTarget(self, choice=0):
		return self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target != self and target.onBoard
		
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and (dmg := self.Game.Counters.numCardsPlayedThisTurn[self.ID]):
			self.dealsDamage(target, dmg)
		return target
		
		
class FoxyFraud(Minion):
	Class, race, name = "Rogue", "", "Foxy Fraud"
	mana, attack, health = 2, 3, 2
	index = "DARKMOON_FAIRE~Rogue~Minion~2~3~2~~Foxy Fraud~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Your next Combo this turn costs (2) less"
	name_CN = "狐人老千"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		GameManaAura_FoxyFraud(self.Game, self.ID).auraAppears()
		

class ShadowClone(Secret):
	Class, school, name = "Rogue", "Shadow", "Shadow Clone"
	requireTarget, mana, effects = False, 2, ""
	index = "DARKMOON_FAIRE~Rogue~Spell~2~Shadow~Shadow Clone~~Secret"
	description = "Secret: After a minion attacks your hero, summon a copy of it with Stealth"
	name_CN = "暗影克隆"
	trigBoard = Trig_ShadowClone		


class SweetTooth_Corrupt(Minion):
	Class, race, name = "Rogue", "", "Sweet Tooth"
	mana, attack, health = 2, 5, 2
	index = "DARKMOON_FAIRE~Priest~Minion~2~5~2~~Sweet Tooth~Stealth~Corrupted~Uncollectible"
	requireTarget, effects, description = False, "Stealth", "Corrupted. Stealth"
	name_CN = "甜食狂"


class SweetTooth(Minion):
	Class, race, name = "Rogue", "", "Sweet Tooth"
	mana, attack, health = 2, 3, 2
	index = "DARKMOON_FAIRE~Rogue~Minion~2~3~2~~Sweet Tooth~ToCorrupt"
	requireTarget, effects, description = False, "", "Corrupt: Gain +2 Attack and Stealth"
	name_CN = "甜食狂"
	trigHand, corruptedType = Trig_Corrupt, SweetTooth_Corrupt

	
class Swindle(Spell):
	Class, school, name = "Rogue", "", "Swindle"
	requireTarget, mana, effects = False, 2, ""
	index = "DARKMOON_FAIRE~Rogue~Spell~2~~Swindle~Combo"
	description = "Draw a spell. Combo: And a minion"
	name_CN = "行骗"
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.drawCertainCard(lambda card: card.category == "Spell")
		if self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0:
			self.drawCertainCard(lambda card: card.category == "Minion")
		
		
class TenwuoftheRedSmoke(Minion):
	Class, race, name = "Rogue", "", "Tenwu of the Red Smoke"
	mana, attack, health = 2, 3, 2
	index = "DARKMOON_FAIRE~Rogue~Minion~2~3~2~~Tenwu of the Red Smoke~Battlecry~Legendary"
	requireTarget, effects, description = True, "", "Battlecry: Return a friendly minion to you hand. It costs (1) less this turn"
	name_CN = "'赤烟'腾武"
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.ID == self.ID and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and target.onBoard:
			self.Game.returnObj2Hand(target)
			if target.inHand: ManaMod_TenwuoftheRedSmoke(target).applies()
		return target
		

class ManaMod_TenwuoftheRedSmoke(ManaMod):
	def __init__(self, recipient):
		super().__init__(recipient, by=-1)

	def turnEnds(self, turn2End): removefrom(self, self.recipient.manaMods)


class CloakofShadows(Spell):
	Class, school, name = "Rogue", "Shadow", "Cloak of Shadows"
	requireTarget, mana, effects = False, 3, ""
	index = "DARKMOON_FAIRE~Rogue~Spell~3~Shadow~Cloak of Shadows"
	description = "Give your hero Stealth for 1 turn"
	name_CN = "暗影斗篷"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.giveEnchant(self.Game.heroes[self.ID], effGain="Temp Stealth", name=CloakofShadows)
		
		
class TicketMaster(Minion):
	Class, race, name = "Rogue", "", "Ticket Master"
	mana, attack, health = 3, 4, 3
	index = "DARKMOON_FAIRE~Rogue~Minion~3~4~3~~Ticket Master~Deathrattle"
	requireTarget, effects, description = False, "", "Deathrattle: Shuffle 3 Tickets into your deck. When drawn, summon a 3/3 Plush Bear"
	name_CN = "奖券老板"
	deathrattle = Death_TicketMaster


class Tickets(Spell):
	Class, school, name = "Rogue", "", "Tickets"
	requireTarget, mana, effects = False, 3, ""
	index = "DARKMOON_FAIRE~Rogue~Spell~3~~Tickets~Casts When Drawn~Uncollectible"
	description = "Casts When Drawn. Summon a 3/3 Plush Bear"
	name_CN = "奖券"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon(PlushBear(self.Game, self.ID))
		

class PlushBear(Minion):
	Class, race, name = "Rogue", "", "Plush Bear"
	mana, attack, health = 3, 3, 3
	index = "DARKMOON_FAIRE~Rogue~Minion~3~3~3~~Plush Bear~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "玩具熊"
	
	
class MalevolentStrike(Spell):
	Class, school, name = "Rogue", "", "Malevolent Strike"
	requireTarget, mana, effects = True, 5, ""
	index = "DARKMOON_FAIRE~Rogue~Spell~5~~Malevolent Strike"
	description = "Destroy a minion. Costs (1) less for each card in your deck that didn't start there"
	name_CN = "致伤打击"
	trigHand = Trig_MalevolentStrike
	def selfManaChange(self):
		if self.inHand:
			self.mana -= sum(card.creator for card in self.Game.Hand_Deck.decks[self.ID])
			self.mana = max(0, self.mana)
			
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.Game.kill(self, target)
		return target
		

class GrandEmpressShekzara(Minion):
	Class, race, name = "Rogue", "", "Grand Empress Shek'zara"
	mana, attack, health = 6, 5, 7
	index = "DARKMOON_FAIRE~Rogue~Minion~6~5~7~~Grand Empress Shek'zara~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: Discover a card in your deck and draw all copies of it"
	name_CN = "大女皇夏柯扎拉"
	
	def drawCopiesofType(self, cardType): #info is the index of the card in player's deck
		Hand_Deck, ID = self.Game.Hand_Deck, self.ID
		while True:
			i = next((i for i, card in enumerate(Hand_Deck.decks[ID]) if isinstance(card, cardType)), -1)
			if i > -1: Hand_Deck.drawCard(ID, i)
			
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverfromList(GrandEmpressShekzara, comment)
		
	def discoverDecided(self, option, case, info_RNGSync=None, info_GUISync=None):
		self.handleDiscoveredCardfromList(option, case, self.Game.Hand_Deck.decks[self.ID],
										  lambda index, card: GrandEmpressShekzara.drawCopiesofType(self, type(card)),
										  info_RNGSync, info_GUISync)
		

"""Shaman Cards"""
class Revolve(Spell):
	Class, school, name = "Shaman", "", "Revolve"
	requireTarget, mana, effects = False, 1, ""
	index = "DARKMOON_FAIRE~Shaman~Spell~1~~Revolve"
	description = "Transform all minions into random ones with the same Cost"
	name_CN = "异变轮转"
	poolIdentifier = "1-Cost Minions to Summon"
	@classmethod
	def generatePool(cls, pools):
		return ["%d-Cost Minions to Summon"%cost for cost in pools.MinionsofCost.keys()], \
				list(pools.MinionsofCost.values())
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		game = self.Game
		minions = game.minionsonBoard(1) + game.minionsonBoard(2)
		newMinions = [numpyChoice(self.rngPool("%d-Cost Minions to Summon"%minion.mana)) for minion in minions]
		for minion, newMinion in zip(minions, newMinions):
			self.transform(minion, newMinion(game, minion.ID))
		
		
class CagematchCustodian(Minion):
	Class, race, name = "Shaman", "Elemental", "Cagematch Custodian"
	mana, attack, health = 2, 2, 2
	index = "DARKMOON_FAIRE~Shaman~Minion~2~2~2~Elemental~Cagematch Custodian~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Draw a weapon"
	name_CN = "笼斗管理员"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.drawCertainCard(lambda card: card.category == "Weapon")
		
		
class DeathmatchPavilion(Spell):
	Class, school, name = "Shaman", "", "Deathmatch Pavilion"
	requireTarget, mana, effects = False, 2, ""
	index = "DARKMOON_FAIRE~Shaman~Spell~2~~Deathmatch Pavilion"
	description = "Summon a 3/2 Duelist. If your hero attacked this turn, summon another"
	name_CN = "死斗场帐篷"
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.heroAtkTimesThisTurn[self.ID] > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon(PavilionDuelist(self.Game, self.ID))
		if self.Game.Counters.heroAtkTimesThisTurn[self.ID] > 0:
			self.summon(PavilionDuelist(self.Game, self.ID))
		

class PavilionDuelist(Minion):
	Class, race, name = "Shaman", "", "Pavilion Duelist"
	mana, attack, health = 2, 3, 2
	index = "DARKMOON_FAIRE~Shaman~Minion~2~3~2~~Pavilion Duelist~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "大帐决斗者"
	
	
class GrandTotemEysor(Minion):
	Class, race, name = "Shaman", "Totem", "Grand Totem Eys'or"
	mana, attack, health = 3, 0, 4
	index = "DARKMOON_FAIRE~Shaman~Minion~3~0~4~Totem~Grand Totem Eys'or~Legendary"
	requireTarget, effects, description = False, "", "At the end of your turn, give +1/+1 to all other Totems in your hand, deck and battlefield"
	name_CN = "巨型图腾埃索尔"
	trigBoard = Trig_GrandTotemEysor		


class Magicfin(Minion):
	Class, race, name = "Shaman", "Murloc", "Magicfin"
	mana, attack, health = 3, 3, 4
	index = "DARKMOON_FAIRE~Shaman~Minion~3~3~4~Murloc~Magicfin"
	requireTarget, effects, description = False, "", "After a friendly Murloc dies, add a random Legendary minion to your hand"
	name_CN = "鱼人魔术师"
	poolIdentifier = "Legendary Minions"
	@classmethod
	def generatePool(cls, pools):
		return "Legendary Minions", pools.LegendaryMinions
		
	trigBoard = Trig_Magicfin		


class PitMaster_Corrupt(Minion):
	Class, race, name = "Shaman", "", "Pit Master"
	mana, attack, health = 3, 1, 2
	index = "DARKMOON_FAIRE~Shaman~Minion~3~1~2~~Pit Master~Battlecry~Corrupted~Uncollectible"
	requireTarget, effects, description = False, "", "Corrupted. Battlecry: Summon two 3/2 Duelists"
	name_CN = "死斗场管理者"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon([PavilionDuelist(self.Game, self.ID) for _ in (0, 1)], relative="<>")


class PitMaster(Minion):
	Class, race, name = "Shaman", "", "Pit Master"
	mana, attack, health = 3, 1, 2
	index = "DARKMOON_FAIRE~Shaman~Minion~3~1~2~~Pit Master~Battlecry~ToCorrupt"
	requireTarget, effects, description = False, "", "Battlecry: Summon a 3/2 Duelist. Corrupt: Summon two"
	name_CN = "死斗场管理者"
	trigHand, corruptedType = Trig_Corrupt, PitMaster_Corrupt
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon(PavilionDuelist(self.Game, self.ID))
		

class Stormstrike(Spell):
	Class, school, name = "Shaman", "Nature", "Stormstrike"
	requireTarget, mana, effects = True, 3, ""
	index = "DARKMOON_FAIRE~Shaman~Spell~3~Nature~Stormstrike"
	description = "Deal 3 damage to a minion. Give your hero +3 Attack this turn"
	name_CN = "风暴打击"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.dealsDamage(target, self.calcDamage(3))
			self.giveHeroAttackArmor(self.ID, attGain=3, name=Stormstrike)
		return target
		
		
class WhackAGnollHammer(Weapon):
	Class, name, description = "Shaman", "Whack-A-Gnoll Hammer", "After your hero attacks, give a random friendly minion +1/+1"
	mana, attack, durability, effects = 3, 3, 2, ""
	index = "DARKMOON_FAIRE~Shaman~Weapon~3~3~2~Whack-A-Gnoll Hammer"
	name_CN = "敲狼锤"
	trigBoard = Trig_WhackAGnollHammer		


class DunkTank_Corrupt(Spell):
	Class, school, name = "Shaman", "Nature", "Dunk Tank"
	requireTarget, mana, effects = True, 4, ""
	index = "DARKMOON_FAIRE~Shaman~Spell~4~Nature~Dunk Tank~Corrupted~Uncollectible"
	description = "Corrupted. Deal 4 damage. Then deal 2 damage to all enemy minions"
	name_CN = "深水炸弹"
	def text(self): return "%d, %d"%(self.calcDamage(4), self.calcDamage(2))

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.dealsDamage(target, self.calcDamage(4))
			damage = self.calcDamage(2)
			minions = self.Game.minionsonBoard(3 - self.ID)
			self.AOE_Damage(minions, [damage] * len(minions))
		return target


class DunkTank(Spell):
	Class, school, name = "Shaman", "Nature", "Dunk Tank"
	requireTarget, mana, effects = True, 4, ""
	index = "DARKMOON_FAIRE~Shaman~Spell~4~Nature~Dunk Tank~ToCorrupt"
	description = "Deal 4 damage. Corrupt: Then deal 2 damage to all enemy minions"
	name_CN = "深水炸弹"
	trigHand, corruptedType = Trig_Corrupt, DunkTank_Corrupt
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.dealsDamage(target, self.calcDamage(4))
		return target


class InaraStormcrash(Minion):
	Class, race, name = "Shaman", "", "Inara Stormcrash"
	mana, attack, health = 5, 4, 5
	index = "DARKMOON_FAIRE~Shaman~Minion~5~4~5~~Inara Stormcrash~Legendary"
	requireTarget, effects, description = False, "", "On your turn, your hero has +2 Attack and Windfury"
	name_CN = "伊纳拉·碎雷"
	ara = Aura_InaraStormcrash


"""Warlock Cards"""
class WickedWhispers(Spell):
	Class, school, name = "Warlock", "Shadow", "Wicked Whispers"
	requireTarget, mana, effects = False, 1, ""
	index = "DARKMOON_FAIRE~Warlock~Spell~1~Shadow~Wicked Whispers"
	description = "Discard your lowest Cost card. Give your minions +1/+1"
	name_CN = "邪恶低语"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if indices := pickLowestCostIndices(self.Game.Hand_Deck.hands[self.ID]):
			self.Game.Hand_Deck.discard(self.ID, numpyChoice(indices))
		self.AOE_GiveEnchant(self.Game.minionsonBoard(self.ID), 1, 1, name=WickedWhispers)
		
		
class MidwayManiac(Minion):
	Class, race, name = "Warlock", "Demon", "Midway Maniac"
	mana, attack, health = 2, 1, 5
	index = "DARKMOON_FAIRE~Warlock~Minion~2~1~5~Demon~Midway Maniac~Taunt"
	requireTarget, effects, description = False, "Taunt", "Taunt"
	name_CN = "癫狂的游客"
	
	
class FreeAdmission(Spell):
	Class, school, name = "Warlock", "", "Free Admission"
	requireTarget, mana, effects = False, 3, ""
	index = "DARKMOON_FAIRE~Warlock~Spell~3~~Free Admission"
	description = "Draw 2 minions. If they're both Demons, reduce their Cost by (2)"
	name_CN = "免票入场"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		minion1, mana, entersHand1 = self.drawCertainCard(lambda card: card.category == "Minion")
		minion2, mana, entersHand2 = self.drawCertainCard(lambda card: card.category == "Minion")
		if entersHand1 and entersHand2 and "Demon" in minion1.race and "Demon" in minion2.race:
			ManaMod(minion1, by=-2).applies()
			ManaMod(minion2, by=-2).applies()
			

class ManariMosher(Minion):
	Class, race, name = "Warlock", "Demon", "Man'ari Mosher"
	mana, attack, health = 3, 3, 4
	index = "DARKMOON_FAIRE~Warlock~Minion~3~3~4~Demon~Man'ari Mosher~Battlecry"
	requireTarget, effects, description = True, "", "Battlecry: Give a friendly Demon +3 Attack and Lifesteal this turn"
	name_CN = "摇滚堕落者"
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return "Demon" in target.race and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and (target.onBoard or target.inHand):
			self.giveEnchant(target, statEnchant=Enchantment(3, 0, until=0, name=ManariMosher),
							effectEnchant=Enchantment(effGain="Lifesteal", until=0, name=ManariMosher))
		return target


class CascadingDisaster_Corrupt2(Spell):
	Class, school, name = "Warlock", "", "Cascading Disaster"
	requireTarget, mana, effects = False, 4, ""
	index = "DARKMOON_FAIRE~Warlock~Spell~4~~Cascading Disaster~Corrupted~Uncollectible"
	description = "Corrupted. Destroy 3 random enemy minions"
	name_CN = "连环灾难"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if minions := self.Game.minionsAlive(3-self.ID):
			for minion in numpyChoice(minions, min(3, len(minions)), replace=False):
				self.Game.kill(self, minion)

class CascadingDisaster_Corrupt(Spell):
	Class, school, name = "Warlock", "", "Cascading Disaster"
	requireTarget, mana, effects = False, 4, ""
	index = "DARKMOON_FAIRE~Warlock~Spell~4~~Cascading Disaster~ToCorrupt~Corrupted~Uncollectible"
	description = "Corrupted. Destroy 2 random enemy minions. Corrupt: Destroy 3"
	name_CN = "连环灾难"
	trigHand, corruptedType = Trig_Corrupt, CascadingDisaster_Corrupt2
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if minions := self.Game.minionsAlive(3-self.ID):
			for minion in numpyChoice(minions, min(2, len(minions)), replace=False):
				self.Game.kill(self, minion)

class CascadingDisaster(Spell):
	Class, school, name = "Warlock", "", "Cascading Disaster"
	requireTarget, mana, effects = False, 4, ""
	index = "DARKMOON_FAIRE~Warlock~Spell~4~~Cascading Disaster~ToCorrupt"
	description = "Destroy a random enemy minion. Corrupt: Destroy 2. Corrupt Again: Destroy 3"
	name_CN = "连环灾难"
	trigHand, corruptedType = Trig_Corrupt, CascadingDisaster_Corrupt
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if minions:= self.Game.minionsAlive(3 - self.ID): self.Game.kill(self, numpyChoice(minions))


class RevenantRascal(Minion):
	Class, race, name = "Warlock", "", "Revenant Rascal"
	mana, attack, health = 3, 3, 3
	index = "DARKMOON_FAIRE~Warlock~Minion~3~3~3~~Revenant Rascal~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Destroy a Mana Crystal for both players"
	name_CN = "怨灵捣蛋鬼"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.Manas.destroyManaCrystal(1, self.ID)
		self.Game.Manas.destroyManaCrystal(1, 3-self.ID)
		
		
class FireBreather(Minion):
	Class, race, name = "Warlock", "Demon", "Fire Breather"
	mana, attack, health = 4, 4, 3
	index = "DARKMOON_FAIRE~Warlock~Minion~4~4~3~Demon~Fire Breather~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Deal 2 damage to all minions except Demons"
	name_CN = "吐火艺人"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		minions = [minion for minion in self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2) if "Demon" not in minion.race]
		self.AOE_Damage(minions, [2] * len(minions))
		
		
class DeckofChaos(Spell):
	Class, school, name = "Warlock", "Shadow", "Deck of Chaos"
	requireTarget, mana, effects = False, 5, ""
	index = "DARKMOON_FAIRE~Warlock~Spell~5~Shadow~Deck of Chaos~Legendary"
	description = "Swap the Cost and Attack of all minions in your deck"
	name_CN = "混乱套牌"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if card.category == "Minion":
				for enchant in card.enchantments: enchant.handleStatMax(card)
				att, cost = max(0, card.attack), max(0, card.mana)
				card.manaMods.clear()
				card.enchantments.append(Enchantment(card, source=type(self), attSet=cost))
				card.attack = cost
				ManaMod(card, to=att).applies()
		
		
class RingMatron(Minion):
	Class, race, name = "Warlock", "Demon", "Ring Matron"
	mana, attack, health = 6, 6, 4
	index = "DARKMOON_FAIRE~Warlock~Minion~6~6~4~Demon~Ring Matron~Taunt~Deathrattle"
	requireTarget, effects, description = False, "Taunt", "Taunt. Deathrattle: Summon two 3/2 Imps"
	name_CN = "火圈鬼母"
	deathrattle = Death_RingMatron


class FieryImp(Minion):
	Class, race, name = "Warlock", "Demon", "Fiery Imp"
	mana, attack, health = 2, 3, 2
	index = "DARKMOON_FAIRE~Warlock~Minion~2~3~2~Demon~Fiery Imp~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "火焰小鬼"


class Tickatus_Corrupt(Minion):
	Class, race, name = "Warlock", "Demon", "Tickatus"
	mana, attack, health = 6, 8, 8
	index = "DARKMOON_FAIRE~Warlock~Minion~6~8~8~Demon~Tickatus~Battlecry~Corrupted~Legendary~Uncollectible"
	requireTarget, effects, description = False, "", "Corrupted. Battlecry: Remove the top 5 cards from your opponent's deck"
	name_CN = "提克特斯"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		self.Game.Hand_Deck.removeDeckTopCard(3-self.ID, num=5)

class Tickatus(Minion):
	Class, race, name = "Warlock", "Demon", "Tickatus"
	mana, attack, health = 6, 8, 8
	index = "DARKMOON_FAIRE~Warlock~Minion~6~8~8~Demon~Tickatus~Battlecry~ToCorrupt~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: Remove the top 5 cards from your deck. Corrupt: Your opponent's instead"
	name_CN = "提克特斯"
	trigHand, corruptedType = Trig_Corrupt, Tickatus_Corrupt
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		self.Game.Hand_Deck.removeDeckTopCard(self.ID, num=5)


"""Warrior Cards"""
class StageDive_Corrupt(Spell):
	Class, school, name = "Warrior", "", "Stage Dive"
	requireTarget, mana, effects = False, 1, ""
	index = "DARKMOON_FAIRE~Warrior~Spell~1~~Stage Dive~Corrupted~Uncollectible"
	description = "Corrupted. Draw a Rush minion and give it +2/+1"
	name_CN = "舞台跳水"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		card, mana, entersHand = self.drawCertainCard(lambda card: card.category == "Minion" and card.effects["Rush"] > 0)
		if entersHand: self.giveEnchant(card, 2, 1, name=StageDive_Corrupt, add2EventinGUI=False)

class StageDive(Spell):
	Class, school, name = "Warrior", "", "Stage Dive"
	requireTarget, mana, effects = False, 1, ""
	index = "DARKMOON_FAIRE~Warrior~Spell~1~~Stage Dive~ToCorrupt"
	description = "Draw a Rush minion. Corrupt: Give it +2/+1"
	name_CN = "舞台跳水"
	trigHand, corruptedType = Trig_Corrupt, StageDive_Corrupt
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.drawCertainCard(lambda card: card.category == "Minion" and card.effects["Rush"] > 0)
		

class BumperCar(Minion):
	Class, race, name = "Warrior", "Mech", "Bumper Car"
	mana, attack, health = 2, 1, 3
	index = "DARKMOON_FAIRE~Warrior~Minion~2~1~3~Mech~Bumper Car~Rush~Deathrattle"
	requireTarget, effects, description = False, "Rush", "Rush. Deathrattle: Add two 1/1 Riders with Rush to your hand"
	name_CN = "碰碰车"
	deathrattle = Death_BumperCar


class ETCGodofMetal(Minion):
	Class, race, name = "Warrior", "", "E.T.C., God of Metal"
	mana, attack, health = 2, 1, 4
	index = "DARKMOON_FAIRE~Warrior~Minion~2~1~4~~E.T.C., God of Metal~Legendary"
	requireTarget, effects, description = False, "", "After a friendly Rush minion attack, deal 2 damage to the enemy hero"
	name_CN = "精英牛头人酋长，金属之神"
	trigBoard = Trig_ETCGodofMetal		


class Minefield(Spell):
	Class, school, name = "Warrior", "", "Minefield"
	requireTarget, mana, effects = False, 2, ""
	index = "DARKMOON_FAIRE~Warrior~Spell~2~~Minefield"
	description = "Deal 5 damage randomly split among all minions"
	name_CN = "雷区挑战"
	def text(self): return self.calcDamage(5)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for _ in range(self.calcDamage(5)):
			if objs := self.Game.minionsAlive(1) + self.Game.minionsAlive(2): self.dealsDamage(numpyChoice(objs), 1)
			else: break
		
		
class RingmastersBaton(Weapon):
	Class, name, description = "Warrior", "Ringmaster's Baton", "After your hero attacks, give a Mech, Dragon, and Pirate in your hand +1/+1"
	mana, attack, durability, effects = 2, 1, 3, ""
	index = "DARKMOON_FAIRE~Warrior~Weapon~2~1~3~Ringmaster's Baton"
	name_CN = "马戏领班的节杖"
	trigBoard = Trig_RingmastersBaton		


class StageHand(Minion):
	Class, race, name = "Warrior", "Mech", "Stage Hand"
	mana, attack, health = 2, 3, 2
	index = "DARKMOON_FAIRE~Warrior~Minion~2~3~2~Mech~Stage Hand~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Give a random minion in your hand +1/+1"
	name_CN = "置景工"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if minions := [card for card in self.Game.Hand_Deck.hands[self.ID] if card.category == "Minion"]:
			self.giveEnchant(numpyChoice(minions), 1, 1, name=StageHand, add2EventinGUI=False)
		
		
class FeatofStrength(Spell):
	Class, school, name = "Warrior", "", "Feat of Strength"
	requireTarget, mana, effects = False, 3, ""
	index = "DARKMOON_FAIRE~Warrior~Spell~3~~Feat of Strength"
	description = "Give a random Taunt minion in your hand +5/+5"
	name_CN = "实力担当"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if minions := [card for card in self.Game.Hand_Deck.hands[self.ID] if card.category == "Minion" and card.effects["Taunt"] > 0]:
			self.giveEnchant(numpyChoice(minions), 5, 5, name=FeatofStrength, add2EventinGUI=False)
		
		
class SwordEater(Minion):
	Class, race, name = "Warrior", "Pirate", "Sword Eater"
	mana, attack, health = 4, 2, 5
	index = "DARKMOON_FAIRE~Warrior~Minion~4~2~5~Pirate~Sword Eater~Taunt~Battlecry"
	requireTarget, effects, description = False, "Taunt", "Taunt. Battlecry: Equip a 3/2 Sword"
	name_CN = "吞剑艺人"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.equipWeapon(Jawbreaker(self.Game, self.ID))
		

class Jawbreaker(Weapon):
	Class, name, description = "Warrior", "Jawbreaker", ""
	mana, attack, durability, effects = 3, 3, 2, ""
	index = "DARKMOON_FAIRE~Warrior~Weapon~3~3~2~Jawbreaker~Uncollectible"
	name_CN = "断颚之刃"
	
	
class RingmasterWhatley(Minion):
	Class, race, name = "Warrior", "", "Ringmaster Whatley"
	mana, attack, health = 5, 3, 5
	index = "DARKMOON_FAIRE~Warrior~Minion~5~3~5~~Ringmaster Whatley~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: Draw a Mech, Dragon, and Pirate"
	name_CN = "马戏领班威特利"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		for race in ("Mech", "Dragon", "Pirate"): self.drawCertainCard(lambda card: race in card.race)
		
#All type can only count as one of the 8 races.


#All type can only count as one of the 8 races.
class TentTrasher(Minion):
	Class, race, name = "Warrior", "Dragon", "Tent Trasher"
	mana, attack, health = 5, 5, 5
	index = "DARKMOON_FAIRE~Warrior~Minion~5~5~5~Dragon~Tent Trasher~Rush"
	requireTarget, effects, description = False, "Rush", "Rush. Costs (1) less for each friendly minion with a unique minion type"
	name_CN = "帐篷摧毁者"
	trigHand = Trig_TentTrasher
	def selfManaChange(self):
		if self.inHand:
			races = countTypes([minion.race for minion in self.Game.minionsonBoard(self.ID)])
			del races[""] #There are at most 7 minions on board. The "All" type can always reduce the cost by 1
			#del races["Elemental,Mech,Demon,Murloc,Dragon,Beast,Pirate,Totem"]
			num = sum(value > 0 for value in races.values())
			print("Tent trasher reduces bty", num)
			self.mana -= num
			self.mana = max(0, self.mana)
			

class ArmorVendor(Minion):
	Class, race, name = "Neutral", "", "Armor Vendor"
	mana, attack, health = 1, 1, 3
	index = "DARKMOON_FAIRE~Neutral~Minion~1~1~3~~Armor Vendor~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Give 4 Armor to each hero"
	name_CN = "护甲商贩"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.giveHeroAttackArmor(1, armor=4)
		self.giveHeroAttackArmor(2, armor=4)
		
		
class Crabrider(Minion):
	Class, race, name = "Neutral", "Murloc", "Crabrider"
	mana, attack, health = 2, 1, 4
	index = "DARKMOON_FAIRE~Neutral~Minion~2~1~4~Murloc~Crabrider~Rush~Windfury"
	requireTarget, effects, description = False, "Rush,Windfury", "Rush, Windfury"
	name_CN = "螃蟹骑士"


class Deathwarden(Minion):
	Class, race, name = "Neutral", "", "Deathwarden"
	mana, attack, health = 3, 2, 5
	index = "DARKMOON_FAIRE~Neutral~Minion~3~2~5~~Deathwarden"
	requireTarget, effects, description = False, "", "Deathrattles can't trigger"
	name_CN = "死亡守望者"
	aura = GameRuleAura_Deathwarden

		
class Moonfang(Minion):
	Class, race, name = "Neutral", "Beast", "Moonfang"
	mana, attack, health = 5, 6, 3
	index = "DARKMOON_FAIRE~Neutral~Minion~5~6~3~Beast~Moonfang~Legendary"
	requireTarget, effects, description = False, "", "Can only take 1 damage at a time"
	name_CN = "明月之牙"
	trigBoard = Trig_MoonFang		


class RunawayBlackwing(Minion):
	Class, race, name = "Neutral", "Dragon", "Runaway Blackwing"
	mana, attack, health = 9, 9, 9
	index = "DARKMOON_FAIRE~Neutral~Minion~9~9~9~Dragon~Runaway Blackwing"
	requireTarget, effects, description = False, "", "At the end of your turn, deal 9 damage to a random enemy minion"
	name_CN = "窜逃的黑翼龙"
	trigBoard = Trig_RunawayBlackwing		


class IllidariStudies(Spell):
	Class, school, name = "Demon Hunter", "", "Illidari Studies"
	requireTarget, mana, effects = False, 1, ""
	index = "DARKMOON_FAIRE~Demon Hunter~Spell~1~~Illidari Studies"
	description = "Discover an Outcast card. Your next one costs (1) less"
	name_CN = "伊利达雷研习"
	poolIdentifier = "Outcast Cards"
	@classmethod
	def generatePool(cls, pools):
		return "Outcast Cards", [card for card in pools.ClassCards["Demon Hunter"] if "~Outcast" in card.index]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverandGenerate(IllidariStudies, comment, lambda : self.rngPool("Outcast Cards"))
		GameManaAura_IllidariStudies(self.Game, self.ID).auraAppears()
		

class FelfireDeadeye(Minion):
	Class, race, name = "Demon Hunter,Hunter", "", "Felfire Deadeye"
	mana, attack, health = 2, 2, 3
	index = "DARKMOON_FAIRE~Demon Hunter,Hunter~Minion~2~2~3~~Felfire Deadeye"
	requireTarget, effects, description = False, "", "Your Hero Power costs (1) less"
	name_CN = "邪火神射手"
	aura = ManaAura_FelfireDeadeye

		
class Felsaber(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Felsaber"
	mana, attack, health = 4, 5, 6
	index = "DARKMOON_FAIRE~Demon Hunter~Minion~4~5~6~Demon~Felsaber"
	requireTarget, effects, description = False, "Can't Attack", "Can only attack if your hero attacked this turn"
	name_CN = "邪刃豹"
	def attackAllowedbyEffect(self):
		return self.effects["Can't Attack"] < 1 or \
			   (self.effects["Can't Attack"] == 1 and not self.silenced and self.Game.Counters.heroAtkTimesThisTurn[self.ID] > 0)


class Guidance(Spell):
	Class, school, name = "Druid,Shaman", "", "Guidance"
	requireTarget, mana, effects = False, 1, ""
	index = "DARKMOON_FAIRE~Druid,Shaman~Spell~1~~Guidance"
	description = "Look at two spells. Add one to your hand or Overload: (1) to get both"
	name_CN = "灵魂指引"
	poolIdentifier = "Druid Spells"
	@classmethod
	def generatePool(cls, pools):
		return [Class + " Spells" for Class in pools.Classes], \
			   [[card for card in pools.ClassCards[Class] if card.category == "Spell"] for Class in pools.Classes]
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		game = self.Game
		if game.mode == 0:
			if game.picks:
				info_RNGSync, info_GUISync, isRandom, option = game.picks.pop(0)
				numpyChoice(range(info_RNGSync), 2, replace=False)
				#option is (card1, card2, choice=0/1/2)
				card1, card2, i = option
				cards_Real = [card1(game, self.ID), card2(game, self.ID)]
				if game.GUI: game.GUI.discoverDecideAni(isRandom=isRandom, numOption=info_GUISync[0], indexOption=info_GUISync[1],
														options=cards_Real + [SpiritPath(ID=self.ID)])
				Guidance.discoverDecided(self, cards_Real+[i],
									 	case="Guided", info_RNGSync=info_RNGSync, info_GUISync=info_GUISync)
			else:
				pool = self.rngPool(classforDiscover(self) + " Spells")
				options = [option(game, self.ID) for option in numpyChoice(pool, 2, replace=False)] + [SpiritPath(ID=self.ID)]
				if self.ID != game.turn or "byOthers" in comment:
					i = datetime.now().microsecond % 3
					if game.GUI: game.UI.discoverDecideAni(isRandom=True, numOption=3, indexOption=i, options=options)
					Guidance.discoverDecided(self, options[0:2]+[i], case="Random", info_RNGSync=len(pool), info_GUISync=(3, i))
				else:
					game.options = options
					game.Discover.startDiscover(self, effectType=Guidance, info_RNGSync=len(pool), info_GUISync=[3])
		
	def discoverDecided(self, option, case, info_RNGSync=None, info_GUISync=None):
		if case == "Discovered": #option is one of the cards or SpiritPath(self.Game, self.ID)
			card1, card2 = self.Game.options[0:2]
			i = self.Game.options.index(option)
			self.Game.picks_Backup.append((info_RNGSync, info_GUISync, False, (type(card1), type(card2), i)))
		else: #option is (card1, card2, i)
			card1, card2, i = option
			if case == "Random": self.Game.picks_Backup.append((info_RNGSync, info_GUISync, True, (type(card1), type(card2), i)) )
			
		if i == 2:
			self.addCardtoHand((card1, card2), self.ID, byDiscover=True)
			self.Game.Manas.overloadMana(1, self.ID)
		else:
			self.addCardtoHand(card2 if i else card1, self.ID, byDiscover=True)
			

class SpiritPath(Option):
	name, description = "Spirit Path", "Add both spells to your hand. Overload: (1)"
	index = ""
	mana, attack, health = 0, -1, -1


class DreamingDrake_Corrupt(Minion):
	Class, race, name = "Druid", "Dragon", "Dreaming Drake"
	mana, attack, health = 3, 5, 6
	index = "DARKMOON_FAIRE~Druid~Minion~3~5~6~Dragon~Dreaming Drake~Taunt~Corrupted~Uncollectible"
	requireTarget, effects, description = False, "Taunt", "Corrupted. Taunt"
	name_CN = "迷梦幼龙"


class DreamingDrake(Minion):
	Class, race, name = "Druid", "Dragon", "Dreaming Drake"
	mana, attack, health = 3, 3, 4
	index = "DARKMOON_FAIRE~Druid~Minion~3~3~4~Dragon~Dreaming Drake~Taunt~ToCorrupt"
	requireTarget, effects, description = False, "Taunt", "Taunt. Corrupt: Gain +2/+2"
	name_CN = "迷梦幼龙"
	trigHand, corruptedType = Trig_Corrupt, DreamingDrake_Corrupt

	
class ArborUp(Spell):
	Class, school, name = "Druid", "Nature", "Arbor Up"
	requireTarget, mana, effects = False, 5, ""
	index = "DARKMOON_FAIRE~Druid~Spell~5~Nature~Arbor Up"
	description = "Summon two 2/2 Treants. Give your minions +2/+1"
	name_CN = "树木生长"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon([Treant_Darkmoon(self.Game, self.ID) for _ in (0, 1)])
		self.AOE_GiveEnchant(self.Game.minionsonBoard(self.ID), 2, 1, name=ArborUp)
		
		
class ResizingPouch(Spell):
	Class, school, name = "Hunter,Druid", "", "Resizing Pouch"
	requireTarget, mana, effects = False, 1, ""
	index = "DARKMOON_FAIRE~Hunter,Druid~Spell~1~~Resizing Pouch"
	description = "Discover a card with Cost equal to your remaining Mana Crystals"
	name_CN = "随心口袋"
	poolIdentifier = "Cards as Hunter"
	@classmethod
	def generatePool(cls, pools):
		return ["Cards as "+Class for Class in pools.Classes], [pools.ClassCards[Class]+pools.NeutralCards for Class in pools.Classes]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverandGenerate(ResizingPouch, comment, lambda : [card for card in self.rngPool("Cards as %s" % classforDiscover(self))
														if card.mana == self.Game.Manas.manas[self.ID]])
		
		
class BolaShot(Spell):
	Class, school, name = "Hunter", "", "Bola Shot"
	requireTarget, mana, effects = True, 2, ""
	index = "DARKMOON_FAIRE~Hunter~Spell~2~~Bola Shot"
	description = "Deal 1 damage to a minion and 2 damage to its neighbors"
	name_CN = "套索射击"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard
		
	def text(self): return "%d, %d"%(self.calcDamage(1), self.calcDamage(2))

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage_target, damage_adjacent = self.calcDamage(1), self.calcDamage(2)
			if target.onBoard and (neighbors := self.Game.neighbors2(target)[0]):
				targets = [target] + neighbors
				damages = [damage_target] + [damage_adjacent for minion in targets]
				self.AOE_Damage(targets, damages)
			else: self.dealsDamage(target, damage_target)
		return target
		
		
class Saddlemaster(Minion):
	Class, race, name = "Hunter", "", "Saddlemaster"
	mana, attack, health = 3, 3, 4
	index = "DARKMOON_FAIRE~Hunter~Minion~3~3~4~~Saddlemaster"
	requireTarget, effects, description = False, "", "After you play a Beast, add a random Beast to your hand"
	name_CN = "鞍座大师"
	trigBoard = Trig_Saddlemaster		
	poolIdentifier = "Beasts"
	@classmethod
	def generatePool(cls, pools):
		return "Beasts", pools.MinionswithRace["Beast"]
		

class GlacierRacer(Minion):
	Class, race, name = "Mage", "", "Glacier Racer"
	mana, attack, health = 1, 1, 3
	index = "DARKMOON_FAIRE~Mage~Minion~1~1~3~~Glacier Racer"
	requireTarget, effects, description = False, "", "Spellburst: Deal 3 damage to all Frozen enemies"
	name_CN = "冰川竞速者"
	trigBoard = Trig_GlacierRacer		


class ConjureManaBiscuit(Spell):
	Class, school, name = "Mage", "Arcane", "Conjure Mana Biscuit"
	requireTarget, mana, effects = False, 2, ""
	index = "DARKMOON_FAIRE~Mage~Spell~2~Arcane~Conjure Mana Biscuit"
	description = "Add a Biscuit to your hand that refreshes 2 Mana Crystals"
	name_CN = "制造法力饼干"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.addCardtoHand(ManaBiscuit, self.ID)
		

class ManaBiscuit(Spell):
	Class, school, name = "Mage", "", "Mana Biscuit"
	requireTarget, mana, effects = False, 0, ""
	index = "DARKMOON_FAIRE~Mage~Spell~0~~Mana Biscuit~Uncollectible"
	description = "Refresh 2 Mana Crystals"
	name_CN = "法力饼干"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.Manas.restoreManaCrystal(2, self.ID, restoreAll=False)
		
		
class KeywardenIvory(Minion):
	Class, race, name = "Mage,Rogue", "", "Keywarden Ivory"
	mana, attack, health = 5, 4, 5
	index = "DARKMOON_FAIRE~Mage,Rogue~Minion~5~4~5~~Keywarden Ivory~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: Discover a dual-class spell from any class. Spellburst: Get another copy"
	name_CN = "钥匙守护者艾芙瑞"
	poolIdentifier = "Dual Class Spells"
	@classmethod
	def generatePool(cls, pools):
		spells = []
		for cards in pools.ClassCards.values():
			spells += [card for card in cards if "," in card.Class and card.category == "Spell"]
		return "Dual Class Spells", spells
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverandGenerate(KeywardenIvory, comment, lambda : self.rngPool("Dual Class Spells"))
		
	def discoverDecided(self, option, case, info_RNGSync=None, info_GUISync=None):
		self.handleDiscoverGeneratedCard(option, case, info_RNGSync, info_GUISync)
		if (self.onBoard or self.inHand) and option.inHand: #Because the Trig here carries special info, can't use giveEnchant
			self.getsTrig(Trig_KeywardenIvory(self, type(option)), trigType="TrigBoard", connect=self.onBoard)
			

class ImprisonedCelestial(Minion_Dormantfor2turns):
	Class, race, name = "Paladin", "", "Imprisoned Celestial"
	mana, attack, health = 3, 4, 5
	index = "DARKMOON_FAIRE~Paladin~Minion~3~4~5~~Imprisoned Celestial"
	requireTarget, effects, description = False, "", "Dormant for 2 turns. Spellburst: Give your minions Divine Shield"
	name_CN = "被禁锢的星骓"
	trigBoard = Trig_ImprisonedCelestial		


class Rally(Spell):
	Class, school, name = "Paladin,Priest", "Holy", "Rally!"
	requireTarget, mana, effects = False, 4, ""
	index = "DARKMOON_FAIRE~Paladin,Priest~Spell~4~Holy~Rally!"
	description = "Resurrect a friendly 1-Cost, 2-Cost, and 3-Cost minion"
	name_CN = "开赛集结！"
	def available(self):
		return self.selectableMinionExists()
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		minionsDied = self.Game.Counters.minionsDiedThisTurn[self.ID]
		minions = []
		for i in (1, 2, 3):
			if ls := [card for card in minionsDied if card.mana == i]: minions.append(numpyChoice(ls))
		if minions: self.summon([minion(self.Game, self.ID) for minion in minions])
		
		
class LibramofJudgment_Corrupt(Weapon):
	Class, name, description = "Paladin", "Libram of Judgment", "Corrupted. Lifesteal"
	mana, attack, durability, effects = 7, 5, 3, "Lifesteal"
	index = "DARKMOON_FAIRE~Paladin~Weapon~7~5~3~Libram of Judgment~Lifesteal~Corrupted~Uncollectible"
	name_CN = "审判圣契"
		
class LibramofJudgment(Weapon):
	Class, name, description = "Paladin", "Libram of Judgment", "Corrupt: Gain Lifesteal"
	mana, attack, durability, effects = 7, 5, 3, ""
	index = "DARKMOON_FAIRE~Paladin~Weapon~7~5~3~Libram of Judgment~ToCorrupt"
	name_CN = "审判圣契"
	trigHand, corruptedType = Trig_Corrupt, LibramofJudgment_Corrupt


class Hysteria(Spell):
	Class, school, name = "Priest,Warlock", "Shadow", "Hysteria"
	requireTarget, mana, effects = True, 4, ""
	index = "DARKMOON_FAIRE~Priest,Warlock~Spell~4~Shadow~Hysteria"
	description = "Choose a minion. It attacks random minions until it dies"
	name_CN = "狂乱"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and target.onBoard:
			#The minion must still be onBoard and alive in order to continue the loop
			i = 0 #Assume the loop can only last 14 times
			while target.onBoard and target.health > 0 and not target.dead and i < 14:
				minions = self.Game.minionsAlive(target.ID, target) + self.Game.minionsAlive(3-target.ID)
				if minions:
					self.Game.battle(target, numpyChoice(minions), verifySelectable=False, useAttChance=True, resolveDeath=False, resetRedirTrig=False)
				else: break
				i += 1
		return target
		
		
class Lightsteed(Minion):
	Class, race, name = "Priest", "Elemental", "Lightsteed"
	mana, attack, health = 4, 3, 6
	index = "DARKMOON_FAIRE~Priest~Minion~4~3~6~Elemental~Lightsteed"
	requireTarget, effects, description = False, "", "Your healing effects also give affected minions +2 Health"
	name_CN = "圣光战马"
	trigBoard = Trig_Lightsteed		


class DarkInquisitorXanesh(Minion):
	Class, race, name = "Priest", "", "Dark Inquisitor Xanesh"
	mana, attack, health = 5, 3, 5
	index = "DARKMOON_FAIRE~Priest~Minion~5~3~5~~Dark Inquisitor Xanesh~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Your healing effects also give affected minions +2 Health"
	name_CN = "黑暗审判官夏奈什"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for card in self.Game.Hand_Deck.hands[self.ID]:
			if "~ToCorrupt" in card.index:
				ManaMod(card, by=-2).applies()
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if "~ToCorrupt" in card.index:
				ManaMod(card, by=-2).applies()
		

class NitroboostPoison_Corrupt(Spell):
	Class, school, name = "Rogue,Warrior", "Nature", "Nitroboost Poison"
	requireTarget, mana, effects = True, 2, ""
	index = "DARKMOON_FAIRE~Rogue,Warrior~Spell~2~Nature~Nitroboost Poison~Corrupted~Uncollectible"
	description = "Corrupted: Give a minion and your weapon +2 Attack"
	name_CN = "氮素药膏"
	def available(self):
		return self.selectableMinionExists()

	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.giveEnchant(target, 2, 0, name=NitroboostPoison_Corrupt)
			if weapon:= self.Game.availableWeapon(self.ID): self.giveEnchant(weapon, 2, 0, name=NitroboostPoison_Corrupt)
		return target


class NitroboostPoison(Spell):
	Class, school, name = "Rogue,Warrior", "Nature", "Nitroboost Poison"
	requireTarget, mana, effects = True, 2, ""
	index = "DARKMOON_FAIRE~Rogue,Warrior~Spell~2~Nature~Nitroboost Poison~ToCorrupt"
	description = "Give a minion +2 Attack. Corrupt: And your weapon"
	name_CN = "氮素药膏"
	trigHand, corruptedType = Trig_Corrupt, NitroboostPoison_Corrupt
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.giveEnchant(target, 2, 0, name=NitroboostPoison)
		return target


class Shenanigans(Secret):
	Class, school, name = "Rogue", "", "Shenanigans"
	requireTarget, mana, effects = False, 2, ""
	index = "DARKMOON_FAIRE~Rogue~Spell~2~~Shenanigans~~Secret"
	description = "Secret: When your opponent draws their second card in a turn, transform it into a Banana"
	name_CN = "蕉猾诡计"
	trigBoard = Trig_Shenanigans		


class SparkjoyCheat(Minion):
	Class, race, name = "Rogue", "", "Sparkjoy Cheat"
	mana, attack, health = 3, 3, 3
	index = "DARKMOON_FAIRE~Rogue~Minion~3~3~3~~Sparkjoy Cheat~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: If you're holding a Secret, cast it and draw a card"
	name_CN = "欢脱的作弊选手"
	def effCanTrig(self):
		self.effectViable = any(card.race == "Secret" and not self.Game.Secrets.sameSecretExists(card, self.ID) \
									for card in self.Game.Hand_Deck.hands[self.ID])
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if indices := [i for i, card in enumerate(self.Game.Hand_Deck.hands[self.ID]) \
				   if card.race == "Secret" and not self.Game.Secrets.sameSecretExists(card, self.ID)]:
			self.Game.Hand_Deck.extractfromHand(numpyChoice(indices), self.ID, enemyCanSee=False)[0].whenEffective()
			self.Game.Hand_Deck.drawCard(self.ID)
		
		
class ImprisonedPhoenix(Minion_Dormantfor2turns):
	Class, race, name = "Shaman,Mage", "Elemental", "Imprisoned Phoenix"
	mana, attack, health = 2, 2, 3
	index = "DARKMOON_FAIRE~Shaman,Mage~Minion~2~2~3~Elemental~Imprisoned Phoenix~Spell Damge"
	requireTarget, effects, description = False, "Spell Damage_2", "Dormant for 2 turns. Spell Damage +2"
	name_CN = "被禁锢的凤凰"
		
		
class Landslide(Spell):
	Class, school, name = "Shaman", "Nature", "Landslide"
	requireTarget, mana, effects = False, 2, ""
	index = "DARKMOON_FAIRE~Shaman~Spell~2~Nature~Landslide"
	description = "Deal 1 damage to all enemy minions. If you're Overloaded, deal 1 damage again"
	name_CN = "大地崩陷"
	def text(self): return self.calcDamage(1)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = self.calcDamage(1)
		targets = self.Game.minionsonBoard(3-self.ID)
		if targets:
			self.AOE_Damage(targets, [damage]*len(targets))
			#假设插入随从的死亡结算
			self.Game.gathertheDead()
			damage = self.calcDamage(1)
			targets = self.Game.minionsonBoard(3-self.ID)
			self.AOE_Damage(targets, [damage]*len(targets))
		
		
class Mistrunner(Minion):
	Class, race, name = "Shaman", "", "Mistrunner"
	mana, attack, health = 5, 4, 4
	index = "DARKMOON_FAIRE~Shaman~Minion~5~4~4~~Mistrunner~Battlecry~Overload"
	requireTarget, effects, description = True, "", "Battlecry: Give a friendly minion +3/+3. Overload: (1)"
	name_CN = "迷雾行者"
	overload = 1
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.ID == self.ID and target.onBoard and target != self
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.giveEnchant(target, 3, 3, name=Mistrunner)
		return target
		

class Backfire(Spell):
	Class, school, name = "Warlock", "Fire", "Backfire"
	requireTarget, mana, effects = False, 3, ""
	index = "DARKMOON_FAIRE~Warlock~Spell~3~Fire~Backfire"
	description = "Draw 3 cards. Deal 3 damage to your hero"
	name_CN = "赛车回火"
	def text(self): return self.calcDamage(3)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for _ in range(3): self.Game.Hand_Deck.drawCard(self.ID)
		self.dealsDamage(self.Game.heroes[self.ID], self.calcDamage(3))


class LuckysoulHoarder_Corrupt(Minion):
	Class, race, name = "Warlock,Demon Hunter", "", "Luckysoul Hoarder"
	mana, attack, health = 3, 3, 4
	index = "DARKMOON_FAIRE~Warlock,Demon Hunter~Minion~3~3~4~~Luckysoul Hoarder~Battlecry~Corrupted~Uncollectible"
	requireTarget, effects, description = False, "", "Corrupted. Battlecry: Shuffle 2 Soul Fragments into your deck. Draw a card"
	name_CN = "幸运之魂囤积者"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.shuffleintoDeck([SoulFragment(self.Game, self.ID) for _ in (0, 1)])
		self.Game.Hand_Deck.drawCard(self.ID)

class LuckysoulHoarder(Minion):
	Class, race, name = "Warlock,Demon Hunter", "", "Luckysoul Hoarder"
	mana, attack, health = 3, 3, 4
	index = "DARKMOON_FAIRE~Warlock,Demon Hunter~Minion~3~3~4~~Luckysoul Hoarder~Battlecry~ToCorrupt"
	requireTarget, effects, description = False, "", "Battlecry: Shuffle 2 Soul Fragments into your deck. Corrupt: Draw a card"
	name_CN = "幸运之魂囤积者"
	trigHand, corruptedType = Trig_Corrupt, LuckysoulHoarder_Corrupt
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.shuffleintoDeck([SoulFragment(self.Game, self.ID) for _ in (0, 1)])
		
		
class EnvoyRustwix(Minion):
	Class, race, name = "Warlock", "Demon", "Envoy Rustwix"
	mana, attack, health = 5, 5, 4
	index = "DARKMOON_FAIRE~Warlock~Minion~5~5~4~Demon~Envoy Rustwix~Deathrattle~Legendary"
	requireTarget, effects, description = False, "", "Deathrattle: Shuffle 3 random Prime Legendary minions into your deck"
	name_CN = "铁锈特使拉斯维克斯"
	deathrattle = Death_EnvoyRustwix


class SpikedWheel(Weapon):
	Class, name, description = "Warrior", "Spiked Wheel", "Has +3 Attack when your hero has Armor"
	mana, attack, durability, effects = 1, 0, 2, ""
	index = "DARKMOON_FAIRE~Warrior~Weapon~1~0~2~Spiked Wheel"
	name_CN = "尖刺轮盘"
	trigBoard = Trig_SpikedWheel
	def statCheckResponse(self):
		if self.onBoard and self.Game.heroes[self.ID].armor > 0: self.attack += 3


class Ironclad(Minion):
	Class, race, name = "Warrior", "Mech", "Ironclad"
	mana, attack, health = 3, 2, 4
	index = "DARKMOON_FAIRE~Warrior~Minion~3~2~4~Mech~Ironclad~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: If your hero has Armor, gain +2/+2"
	name_CN = "铁甲战车"
	
	def effCanTrig(self):
		self.effectViable = self.Game.heroes[self.ID].armor > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.heroes[self.ID].armor > 0: self.giveEnchant(self, 2, 2, name=Ironclad)
		
		
class Barricade(Spell):
	Class, school, name = "Warrior,Paladin", "", "Barricade"
	requireTarget, mana, effects = False, 4, ""
	index = "DARKMOON_FAIRE~Warrior,Paladin~Spell~4~~Barricade"
	description = "Summon a 2/4 Guard with Taunt. If it's your only minion, summon another"
	name_CN = "路障"
	def available(self):
		return self.Game.space(self.ID) > 0

	def effCanTrig(self):
		self.effectViable = not self.Game.minionsonBoard(self.ID)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon(RaceGuard(self.Game, self.ID))
		#Note that at this stage, there won't be deaths/deathrattles resolved.
		if len(self.Game.minionsonBoard(self.ID)) == 1: self.summon(RaceGuard(self.Game, self.ID))
		

class RaceGuard(Minion):
	Class, race, name = "Warrior,Paladin", "", "Race Guard"
	mana, attack, health = 3, 2, 4
	index = "DARKMOON_FAIRE~Warrior,Paladin~Minion~3~2~4~~Race Guard~Taunt~Uncollectible"
	requireTarget, effects, description = False, "Taunt", "Taunt"
	name_CN = "赛道护卫"
	

"""Game TrigEffects & Game Auras"""
#Assume one can get CThun as long as pieces are played, even if it didn't start in their deck
class CThuntheShattered_Effect(TrigEffect):
	card, signals, counter, trigType = CThuntheShattered, ("CThunPiece",), 4, "Conn&TrigAura"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.pieces = ["Body", "Eye", "Heart", "Maw"]

	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return ID == self.ID and comment in self.pieces

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.pieces.remove(comment)
		self.counter -= 1
		if self.counter < 1:
			self.card.shuffleintoDeck(self.card)
			self.card.creator = None
			self.disconnect()
			del self.Game.trigsBoard[self.ID]["CThunPiece"]

	def assistCreateCopy(self, Copy):
		Copy.pieces = self.pieces[:]


class GameManaAura_IllidariStudies(GameManaAura_OneTime):
	card, by, temporary = IllidariStudies, -1, False
	def applicable(self, target): return target.ID == self.ID and "~Outcast" in target.index


class Stiltstepper_Effect(TrigEffect):
	card, signals, trigType = Stiltstepper, ("MinionBeenPlayed", "SpellBeenPlayed", "WeaponBeenPlayed", "HeroCardBeenPlayed"), "Conn&TurnEnd"
	def __init__(self, Game, ID, cardDrawn=None):
		super().__init__(Game, ID)
		self.savedObj = cardDrawn

	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.ID and subject == self.savedObj

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.card.giveHeroAttackArmor(self.ID, attGain=4, name=Stiltstepper)
		self.disconnect()

	def assistCreateCopy(self, Copy):
		Copy.cardMarked = self.savedObj.createCopy(Copy.Game)


class Acrobatics_Effect(TrigEffect):
	card, signals, counter, trigType = Acrobatics, ("MinionBeenPlayed", "SpellBeenPlayed", "WeaponBeenPlayed", "HeroCardBeenPlayed"), 2, "Conn&TurnEnd"
	def __init__(self, Game, ID, cardsDrawn=()):
		super().__init__(Game, ID)
		self.savedObjs = cardsDrawn
		self.animate = False

	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.ID and subject in self.savedObjs

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.savedObjs.remove(subject)
		self.counter -= 1
		if self.card.btn: self.card.btn.trigAni(self.counter)
		if self.counter < 1:
			if self.Game.GUI: self.Game.GUI.showOffBoardTrig(self.card)
			self.Game.Hand_Deck.drawCard(self.ID)
			self.Game.Hand_Deck.drawCard(self.ID)
			self.disconnect()

	def assistCreateCopy(self, Copy):
		Copy.cardsDrawn = [card.createCopy(Copy.Game) for card in self.savedObjs]


class ExpendablePerformers_Effect(TrigEffect):
	card, signals, trigType, animate = ExpendablePerformers, ("MinionDies",), "Conn&TurnEnd", False
	def __init__(self, Game, ID, minions=()):
		super().__init__(Game, ID)
		self.savedObjs = minions

	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return target.ID == self.ID and target in self.savedObjs

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.savedObjs.remove(target)
		if not self.savedObjs:
			self.disconnect()
			if self.Game.GUI: self.Game.GUI.showOffBoardTrig(self.card)
			self.card.summon([IllidariInitiate(self.Game, self.ID) for _ in range(7)])

	def assistCreateCopy(self, Copy):
		Copy.minions = [minion.createCopy(Copy.Game) for minion in self.savedObjs]


class GameManaAura_LunarEclipse(GameManaAura_OneTime):
	card, by = LunarEclipse, -2
	def applicable(self, target): return target.ID == self.ID and target.category == "Spell"

class SolarEclipse_Effect(TrigEffect):
	card, signals, trigType = SolarEclipse, ("SpellBeenCast",), "Conn&TurnEnd&OnlyKeepOne"
	def __init__(self, Game, ID, card=None):
		super().__init__(Game, ID)
		self.savedObj = card #The Solar Eclipse card that casts this is restored.

	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.ID and subject != self.savedObj  # This won't respond to the Solar Eclipse that sends the signal

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.Game.effects[self.ID]["Spells x2"] -= 1
		self.disconnect()

	def trigEffect(self):
		self.Game.effects[self.ID]["Spells x2"] -= 1
		self.disconnect()

	def assistCreateCopy(self, Copy):
		Copy.savedObj = self.savedObj.createCopy(Copy.Game)


class GameManaAura_GameMaster(GameManaAura_OneTime):
	card, to = GameMaster, 1
	def applicable(self, target): return target.ID == self.ID and target.race == "Secret"


class GameManaAura_FoxyFraud(GameManaAura_OneTime):
	card, by = FoxyFraud, -2
	def applicable(self, target): return target.ID == self.ID and "~Combo" in target.index


class LothraxiontheRedeemed_Effect(TrigEffect):
	card, signals, trigType = LothraxiontheRedeemed, ("MinionBeenSummoned",), "Conn&TrigAura&OnlyKeepOne"
	def connect(self):
		trigs = getListinDict(self.Game.trigsBoard[self.ID], "MinionBeenSummoned")
		if (i := next((i for i, trig in enumerate(trigs) if isinstance(trig, LothraxiontheRedeemed_Effect)), -1)) > -1:
			trigs.append(trigs.pop(i)) #把给予圣盾的扳机移到最新的位置
		else:
			self.Game.trigAuras[self.ID].append(self)
			trigs.append(self)
			if self.Game.GUI: self.Game.GUI.heroZones[self.ID].addaTrig(self.card)

	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.ID and subject.name == "Silver Hand Recruit"

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.card.giveEnchant(subject, effGain="Divine Shield", name=LothraxiontheRedeemed)


TrigsDeaths_Darkmoon = {Death_Showstopper: (Showstopper, "Deathrattle: Silence all minions"),
						Death_ClawMachine: (ClawMachine, "Deathrattle: Draw a minion and give it +3/+3"),
						Death_RenownedPerformer: (RenownedPerformer, "Deathrattle: Summon two 1/1 Assistants with Rush"),
						Death_Greybough: (Greybough, "Deathrattle: Give a random friendly minion 'Deathrattle: Summon Greybough'"),
						Death_SummonGreybough: (Greybough, "Deathrattle: Summon Greybough"),
						Death_DarkmoonTonk: (DarkmoonTonk, "Deathrattle: Fire four missiles at random enemies that deal 2 damage each"),
						Death_TicketMaster: (TicketMaster, "Deathrattle: Shuffle 3 Tickets into your deck"),
						Death_RedscaleDragontamer: (RedscaleDragontamer, "Deathrattle: Draw a Dragon"),
						Death_RingMatron: (RingMatron, "Deathrattle: Summon two 3/2 Imps"),
						Death_BumperCar: (BumperCar, "Deathrattle: Add two 1/1 Riders with Rush to your hand"),
						Death_EnvoyRustwix: (EnvoyRustwix, "Deathrattle: Shuffle 3 random Prime Legendary minions into your deck"),
						Trig_KeywardenIvory: (KeywardenIvory, "Spellburst: Add the discover card to your hand"),
						}

Darkmoon_Cards = [
		#Neutral
		SafetyInspector, CostumedEntertainer, HorrendousGrowth, HorrendousGrowthCorrupt, ParadeLeader, PrizeVendor,
		RockRager, Showstopper, WrigglingHorror, BananaVendor, DarkmoonDirigible, DarkmoonDirigible_Corrupt, DarkmoonStatue,
		DarkmoonStatue_Corrupt, Gyreworm, InconspicuousRider, KthirRitualist, CircusAmalgam, CircusMedic,
		CircusMedic_Corrupt, FantasticFirebird, KnifeVendor, DerailedCoaster, DarkmoonRider, FleethoofPearltusk,
		FleethoofPearltusk_Corrupt, OptimisticOgre, ClawMachine, SilasDarkmoon, Strongman, Strongman_Corrupt, CarnivalClown,
		CarnivalClown_Corrupt, BodyofCThun, CThunsBody, EyeofCThun, HeartofCThun, MawofCThun, CThuntheShattered,
		DarkmoonRabbit, NZothGodoftheDeep, YoggSaronMasterofFate, CurseofFlesh, HandofFate, YShaarjtheDefiler,
		#Demon Hunter
		FelscreamBlast, ThrowGlaive, RedeemedPariah, Acrobatics, DreadlordsBite, FelsteelExecutioner,
		FelsteelExecutioner_Corrupt, LineHopper, InsatiableFelhound, InsatiableFelhound_Corrupt, RelentlessPursuit,
		Stiltstepper, Ilgynoth, RenownedPerformer, PerformersAssistant, ZaitheIncredible, BladedLady, ExpendablePerformers,
		#Druid
		GuesstheWeight, LunarEclipse, SolarEclipse, FaireArborist, FaireArborist_Corrupt, Treant_Darkmoon, MoontouchedAmulet,
		MoontouchedAmulet_Corrupt, KiriChosenofElune, Greybough, UmbralOwl, CenarionWard, FizzyElemental,
		#Hunter
		MysteryWinner, DancingCobra, DancingCobra_Corrupt, DontFeedtheAnimals, DontFeedtheAnimals_Corrupt, OpentheCages,
		PettingZoo, DarkmoonStrider, RinlingsRifle, TramplingRhino, MaximaBlastenheimer, DarkmoonTonk, JewelofNZoth,
		#Mage
		ConfectionCyclone, SugarElemental, DeckofLunacy, GameMaster, RiggedFaireGame, OccultConjurer, RingToss,
		RingToss_Corrupt, FireworkElemental, FireworkElemental_Corrupt, SaygeSeerofDarkmoon, MaskofCThun, GrandFinale,
		ExplodingSparkler,
		#Paladin
		OhMyYogg, RedscaleDragontamer, SnackRun, CarnivalBarker, DayattheFaire, DayattheFaire_Corrupt, BalloonMerchant,
		CarouselGryphon, CarouselGryphon_Corrupt, LothraxiontheRedeemed, HammeroftheNaaru, HolyElemental, HighExarchYrel,
		#Priest
		Insight, Insight_Corrupt, FairgroundFool, FairgroundFool_Corrupt, NazmaniBloodweaver, PalmReading, AuspiciousSpirits,
		AuspiciousSpirits_Corrupt, TheNamelessOne, FortuneTeller, IdolofYShaarj, GhuuntheBloodGod, BloodofGhuun,
		#Rogue
		PrizePlunderer, FoxyFraud, ShadowClone, SweetTooth, SweetTooth_Corrupt, Swindle, TenwuoftheRedSmoke, CloakofShadows,
		TicketMaster, Tickets, PlushBear, MalevolentStrike, GrandEmpressShekzara,
		#Shaman
		Revolve, CagematchCustodian, DeathmatchPavilion, PavilionDuelist, GrandTotemEysor, Magicfin, PitMaster,
		PitMaster_Corrupt, Stormstrike, WhackAGnollHammer, DunkTank, DunkTank_Corrupt, InaraStormcrash,
		#Warlock
		WickedWhispers, MidwayManiac, FreeAdmission, ManariMosher, CascadingDisaster, CascadingDisaster_Corrupt,
		CascadingDisaster_Corrupt2, RevenantRascal, FireBreather, DeckofChaos, RingMatron, FieryImp, Tickatus,
		Tickatus_Corrupt,
		#Warrior
		StageDive, StageDive_Corrupt, BumperCar, ETCGodofMetal, Minefield, RingmastersBaton, StageHand, FeatofStrength,
		SwordEater, Jawbreaker, RingmasterWhatley, TentTrasher,
		#Neutral
		ArmorVendor, Crabrider, Deathwarden, Moonfang, RunawayBlackwing,
		#Demon Hunter
		IllidariStudies, FelfireDeadeye, Felsaber,
		#Druid
		Guidance, DreamingDrake, DreamingDrake_Corrupt, ArborUp,
		#Hunter
		ResizingPouch, BolaShot, Saddlemaster,
		#Mage
		GlacierRacer, ConjureManaBiscuit, ManaBiscuit, KeywardenIvory,
		#Paladin
		ImprisonedCelestial, Rally, LibramofJudgment, LibramofJudgment_Corrupt,
		#Priest
		Hysteria, Lightsteed, DarkInquisitorXanesh,
		#Rogue
		NitroboostPoison, NitroboostPoison_Corrupt, Shenanigans, SparkjoyCheat,
		#Shaman
		ImprisonedPhoenix, Landslide, Mistrunner,
		#Warlock
		Backfire, LuckysoulHoarder, LuckysoulHoarder_Corrupt, EnvoyRustwix,
		#Warrior
		SpikedWheel, Ironclad, Barricade, RaceGuard,
]

Darkmoon_Cards_Collectible = [
		#Neutral
		SafetyInspector, CostumedEntertainer, HorrendousGrowth, ParadeLeader, PrizeVendor, RockRager, Showstopper,
		WrigglingHorror, BananaVendor, DarkmoonDirigible, DarkmoonStatue, Gyreworm, InconspicuousRider, KthirRitualist,
		CircusAmalgam, CircusMedic, FantasticFirebird, KnifeVendor, DerailedCoaster, FleethoofPearltusk, OptimisticOgre,
		ClawMachine, SilasDarkmoon, Strongman, CarnivalClown, CThuntheShattered, DarkmoonRabbit, NZothGodoftheDeep,
		YoggSaronMasterofFate, YShaarjtheDefiler,
		#Demon Hunter
		FelscreamBlast, ThrowGlaive, RedeemedPariah, Acrobatics, DreadlordsBite, FelsteelExecutioner, LineHopper,
		InsatiableFelhound, RelentlessPursuit, Stiltstepper, Ilgynoth, RenownedPerformer, ZaitheIncredible, BladedLady,
		ExpendablePerformers,
		#Druid
		GuesstheWeight, LunarEclipse, SolarEclipse, FaireArborist, MoontouchedAmulet, KiriChosenofElune, Greybough,
		UmbralOwl, CenarionWard, FizzyElemental,
		#Hunter
		MysteryWinner, DancingCobra, DontFeedtheAnimals, OpentheCages, PettingZoo, RinlingsRifle, TramplingRhino,
		MaximaBlastenheimer, DarkmoonTonk, JewelofNZoth,
		#Mage
		ConfectionCyclone, DeckofLunacy, GameMaster, RiggedFaireGame, OccultConjurer, RingToss, FireworkElemental,
		SaygeSeerofDarkmoon, MaskofCThun, GrandFinale,
		#Paladin
		OhMyYogg, RedscaleDragontamer, SnackRun, CarnivalBarker, DayattheFaire, BalloonMerchant, CarouselGryphon,
		LothraxiontheRedeemed, HammeroftheNaaru, HighExarchYrel,
		#Priest
		Insight, FairgroundFool, NazmaniBloodweaver, PalmReading, AuspiciousSpirits, TheNamelessOne, FortuneTeller,
		IdolofYShaarj, GhuuntheBloodGod, BloodofGhuun,
		#Rogue
		PrizePlunderer, FoxyFraud, ShadowClone, SweetTooth, Swindle, TenwuoftheRedSmoke, CloakofShadows, TicketMaster,
		MalevolentStrike, GrandEmpressShekzara,
		#Shaman
		Revolve, CagematchCustodian, DeathmatchPavilion, GrandTotemEysor, Magicfin, PitMaster, Stormstrike,
		WhackAGnollHammer, DunkTank, InaraStormcrash,
		#Warlock
		WickedWhispers, MidwayManiac, FreeAdmission, ManariMosher, CascadingDisaster, RevenantRascal, FireBreather,
		DeckofChaos, RingMatron, Tickatus,
		#Warrior
		StageDive, BumperCar, ETCGodofMetal, Minefield, RingmastersBaton, StageHand, FeatofStrength, SwordEater,
		RingmasterWhatley, TentTrasher,
		#Neutral
		ArmorVendor, Crabrider, Deathwarden, Moonfang, RunawayBlackwing,
		#Demon Hunter
		IllidariStudies, FelfireDeadeye, Felsaber,
		#Druid
		Guidance, DreamingDrake, ArborUp,
		#Hunter
		ResizingPouch, BolaShot, Saddlemaster,
		#Mage
		GlacierRacer, ConjureManaBiscuit, KeywardenIvory,
		#Paladin
		ImprisonedCelestial, Rally, LibramofJudgment,
		#Priest
		Hysteria, Lightsteed, DarkInquisitorXanesh,
		#Rogue
		NitroboostPoison, Shenanigans, SparkjoyCheat,
		#Shaman
		ImprisonedPhoenix, Landslide, Mistrunner,
		#Warlock
		Backfire, LuckysoulHoarder, EnvoyRustwix,
		#Warrior
		SpikedWheel, Ironclad, Barricade,
]