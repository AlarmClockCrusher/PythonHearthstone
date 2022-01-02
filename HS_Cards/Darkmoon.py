from Parts.CardTypes import *
from Parts.TrigsAuras import *
from HS_Cards.AcrossPacks import Bananas, IllidariInitiate, Huffer, Leokk, Misha, SilverHandRecruit, Pyroblast
from HS_Cards.Outlands import Minion_Dormantfor2turns, MsshifnPrime, ZixorPrime, SolarianPrime, MurgurglePrime, ReliquaryPrime, \
					AkamaPrime, VashjPrime, KanrethadPrime, KargathPrime
from HS_Cards.Academy import Trig_Corrupt, Spellburst, SoulFragment


class GameRuleAura_Deathwarden(GameRuleAura):
	def auraAppears(self):
		self.keeper.Game.rules[1]["Deathrattles X"] += 1
		self.keeper.Game.rules[2]["Deathrattles X"] += 1
		
	def auraDisappears(self):
		self.keeper.Game.rules[1]["Deathrattles X"] -= 1
		self.keeper.Game.rules[2]["Deathrattles X"] -= 1
		
	
class Aura_DarkmoonStatue(Aura_AlwaysOn):
	attGain = 1
	
	
class ManaAura_LineHopper(ManaAura):
	by = -1
	def applicable(self, target): return "~Outcast" in target.index and target.ID == self.keeper.ID
		
	
class GameRuleAura_Ilgynoth(GameRuleAura):
	def auraAppears(self): #Even if hero is full health, the Lifesteal will still deal damage
		self.keeper.Game.rules[self.keeper.ID]["Lifesteal Damages Enemy"] += 1
		
	def auraDisappears(self): self.keeper.Game.rules[self.keeper.ID]["Lifesteal Damages Enemy"] -= 1
		
	
class ManaAura_GameMaster(ManaAura_1UsageEachTurn):
	def auraAppears(self):
		game, ID = self.keeper.Game, self.keeper.ID
		if game.turn == ID and not game.Counters.examCardPlays(ID, turnInd=game.turnInd, cond=lambda tup: tup[0].race == "Secret"):
			self.aura = GameManaAura_GameMaster(game, ID)
			game.Manas.CardAuras.append(self.aura)
			self.aura.auraAppears()
		add2ListinDict(self, game.trigsBoard[ID], "TurnStarts")
		
	
class ManaAura_FelfireDeadeye(ManaAura):
	by, targets = -1, "Power"
	def applicable(self, target): return target.ID == self.keeper.ID
		
	
class Aura_InaraStormcrash:
	def __init__(self, keeper):
		self.keeper, self.receivers = keeper, []
		self.signals = ("HeroAppears", "TurnStarts", "TurnEnds")
		
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return self.keeper.onBoard and (signal[0] == "T" or target.ID == self.keeper.ID)
		
	def trig(self, signal, ID, subject, target, num, comment, choice):
		if self.canTrig(signal, ID, subject, target, num, comment, choice):
			kpr = self.keeper
			if signal[0] == "T":  #
				if "E" in signal:  # At the end of either player's turn, clear the affected list
					for receiver in self.receivers[:]: receiver.effectClear()
					self.receivers = []
				elif ID == kpr.ID:  # Only start the effect at the start of your turn
					Aura_Receiver(kpr.Game.heroes[ID], self, attGain=2, effGain="Windfury").effectStart()
			elif ID == kpr.ID == kpr.Game.turn:  # New hero is on board during your turn
				Aura_Receiver(target, self, attGain=2, effGain="Windfury").effectStart()
		
	def auraAppears(self):
		game, ID = self.keeper.Game, self.keeper.ID
		if game.turn == ID: Aura_Receiver(game.heroes[ID], self, attGain=2, effGain="Windfury").effectStart()
		trigsBoard = game.trigsBoard[ID]
		for sig in self.signals: add2ListinDict(self, trigsBoard, sig)
		
	def auraDisappears(self):
		for receiver in self.receivers[:]: receiver.effectClear()
		self.receivers = []
		trigsBoard = self.keeper.Game.trigsBoard[self.keeper.ID]
		for sig in self.signals: removefromListinDict(self, trigsBoard, sig)
		
	def selfCopy(self, recipient):
		return type(self)(recipient)
		
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
		
	
class Trig_EndlessCorrupt(Trig_Corrupt):
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		if signal == "ManaPaid": self.on = num[0] > self.keeper.mana
		else:
			card, self.on = self.keeper, False
			minion = HorrendousGrowthCorrupt(card.Game, card.ID)
			minion.attack_0 = minion.attack = card.attack_0 + 1
			minion.health_0 = minion.health = card.health_0 + 1
			minion.inheritEnchantmentsfrom(card)
			card.Game.Hand_Deck.replace1CardinHand(card, minion)
		
	
class Trig_ParadeLeader(TrigBoard):
	signals = ("ObjBeenSummoned",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return subject.category == "Minion" and ID == kpr.ID and subject is not kpr and subject.effects["Rush"] > 0 and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.giveEnchant(subject, 2, 0, source=ParadeLeader)
		
	
class Trig_OptimisticOgre(TrigBoard):
	signals = ("MinionAttacksMinion", "MinionAttacksHero", "BattleFinished",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		#The trigger can be reset any time by "BattleFinished".
		#Otherwise, can only trigger if there are enemies other than the target.
		#游荡怪物配合误导可能会将对英雄的攻击目标先改成对召唤的随从，然后再发回敌方英雄，说明攻击一个错误的敌人应该也是游戏现记录的目标之外的角色。
		return not signal.startswith("Minion") \
					or (subject is kpr and kpr.onBoard and target[1] and not self.on and kpr.Game.charsAlive(3-ID, exclude=target[1]))
		
	def trig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		if kpr.onBoard:
			if signal == "BattleFinished": #Reset the Forgetful for next battle event.
				self.on = False
			elif target: #Attack signal
				game, char, redirect = kpr.Game, None, 0
				otherEnemies = game.charsAlive(3-kpr.ID, exclude=target[1])
				if otherEnemies:
					char, redirect = numpyChoice(otherEnemies), numpyRandint(2)
					if char and redirect: #Redirect is 0/1, indicating whether the attack will redirect or not
						#玩家命令的一次攻击中只能有一次触发机会。只要满足进入50%判定的条件，即使没有最终生效，也不能再次触发。
						if game.GUI: game.GUI.trigBlink(kpr)
						target[1], self.on = char, True
		
	
class Trig_RedeemedPariah(TrigBoard):
	signals = ("CardBeenPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID and "~Outcast" in kpr.Game.cardinPlay.index
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).giveEnchant(kpr, statEnchant=Enchantment_Exclusive(RedeemedPariah, 1, 1))
		
	
class Trig_BladedLady(TrigHand):
	signals = ("HeroStatCheck",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.inHand and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).Game.Manas.calcMana_Single(kpr)
		
	
class Trig_UmbralOwl(TrigHand):
	signals = ("CardBeenPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return comment == "Spell" and ID == kpr.ID and kpr.inHand
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).Game.Manas.calcMana_Single(kpr)
		
	
class Trig_OpentheCages(Trig_Secret):
	signals = ("TurnStarts",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice): #target here holds the actual target object
		secret = self.keeper
		return secret.ID == ID and secret.Game.minionsonBoard(secret.ID) and secret.Game.space(secret.ID) > 0
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		game, ID = (kpr := self.keeper).Game, kpr.ID
		kpr.summon([numpyChoice((Huffer, Leokk, Misha))(game, ID) for _ in range(type(kpr).num)])
		
	
class Trig_RinlingsRifle(TrigBoard):
	signals = ("HeroAttackedMinion", "HeroAttackedHero",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return subject is kpr.Game.heroes[kpr.ID] and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		secret = kpr.discoverNew('', lambda : secrets2Discover(kpr, toPutonBoard=True), add2Hand=False)
		secret.creator = RinlingsRifle
		secret.playedEffect()
		
	
class Trig_TramplingRhino(TrigBoard):
	signals = ("MinionAttackedMinion",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and subject is kpr and target.health < 0
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).dealsDamage(kpr.Game.heroes[3-kpr.ID], -target.health)
		
	
class Trig_RiggedFaireGame(Trig_Secret):
	signals = ("TurnEnds",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice): #target here holds the actual target object
		kpr = self.keeper
		return kpr.ID != ID and not kpr.Game.Counters.examDmgonHero(kpr.ID, turnInd=kpr.Game.turnInd)
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		for _ in (0, 1, 2): (kpr := self.keeper).Game.Hand_Deck.drawCard(kpr.ID)
		
	
class Trig_OhMyYogg(Trig_Secret):
	signals = ("SpellOK2Play?",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.Game.cardinPlay.ID != kpr.ID and subject[0] > -1 #-1: Counterspell&Ice Trap; 0: Normally played
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		if subject[0] > -1:
			key = "%d-Cost Spells"%num[0]
			if key in self.keeper.Game.RNGPools:
				kpr.Game.cardinPlay = numpyChoice(kpr.rngPool(key))(kpr.Game, 3-kpr.ID)
				subject[0] = 1
			else: subject[0] = -1 #如果没有对应费用的法术，则取消。采用和法反一样的机制
		
	
class Trig_CarnivalBarker(TrigBoard):
	signals = ("ObjSummoned",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return subject.category == "Minion" and ID == kpr.ID and subject.health == 1 and subject is not kpr and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.giveEnchant(subject, 1, 2, source=CarnivalBarker)
		
	
class Trig_NazmaniBloodweaver(TrigBoard):
	signals = ("CardBeenPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return comment == "Spell" and ID == kpr.ID and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		if cards := self.keeper.findCards2ReduceMana(): ManaMod(numpyChoice(cards), by=-1).applies()
		
	
class Trig_BloodofGhuun(TrigBoard):
	signals = ("TurnEnds",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID and kpr.Game.space(kpr.ID) > 0
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		keeper = self.keeper
		if minions := [card for card in keeper.Game.Hand_Deck.decks[keeper.ID] if card.category == "Minion"]:
			keeper.summon(keeper.copyCard(numpyChoice(minions), keeper.ID, 5, 5))
		
	
class Trig_ShadowClone(Trig_Secret):
	signals = ("MinionAttackedHero",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.ID != kpr.Game.turn and target is kpr.Game.heroes[kpr.ID]
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).summon(kpr.copyCard(subject, kpr.ID))
		
	
class Trig_MalevolentStrike(TrigHand):
	signals = ("DeckCheck",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.inHand and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).Game.Manas.calcMana_Single(kpr)
		
	
class Trig_GrandTotemEysor(TrigBoard):
	signals = ("TurnEnds",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		keeper, typeSelf = kpr, type(kpr)
		keeper.giveEnchant(keeper.Game.minionsonBoard(keeper.ID, keeper, race="Totem"), 1, 1, source=GrandTotemEysor)
		kpr.giveEnchant([card for card in kpr.Game.Hand_Deck.hands[kpr.ID] if "Totem" in card.race], 1, 1,
								source=GrandTotemEysor, add2EventinGUI=False)
		for card in kpr.Game.Hand_Deck.decks[kpr.ID]:
			if "Totem" in card.race: card.getsBuffDebuff_inDeck(1, 1, source=GrandTotemEysor)
		
	
class Trig_Magicfin(TrigBoard):
	signals = ("ObjDies",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and target != kpr and target.ID == kpr.ID and "Murloc" in target.race
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).addCardtoHand(numpyChoice(self.rngPool("Legendary Minions")), kpr.ID)
		
	
class Trig_WhackAGnollHammer(TrigBoard):
	signals = ("HeroAttackedMinion", "HeroAttackedHero",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return subject is kpr.Game.heroes[kpr.ID] and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		if minions := kpr.Game.minionsonBoard(kpr.ID):
			self.keeper.giveEnchant(numpyChoice(minions), 1, 1, source=WhackAGnollHammer)
		
	
class Trig_ETCGodofMetal(TrigBoard):
	signals = ("MinionAttackedMinion", "MinionAttackedHero",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return ID == kpr.ID and subject.effects["Rush"] > 0 and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).dealsDamage(kpr.Game.heroes[3-kpr.ID], 2)
		
	
class Trig_RingmastersBaton(TrigBoard):
	signals = ("HeroAttackedMinion", "HeroAttackedHero",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return subject is kpr.Game.heroes[kpr.ID] and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		ownHand = kpr.Game.Hand_Deck.hands[kpr.ID]
		for race in ("Mech", "Dragon", "Pirate"):
			if minions := [card for card in ownHand if card.category == "Minion" and race in card.race]:
				self.keeper.giveEnchant(numpyChoice(minions), 1, 1, source=RingmastersBaton, add2EventinGUI=False)
		
	
class Trig_TentTrasher(TrigHand):
	signals = ("MinionAppears", "MinionDisappears",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.inHand and ID == kpr.ID and target.race
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).Game.Manas.calcMana_Single(kpr)
		
	
class Trig_Moonfang(TrigBoard):
	signals = ("FinalDmgonMinion?",)
	def __init__(self, keeper):
		super().__init__(keeper)
		self.lastinQ = True
		
	def canTrig(self, signal, ID, subject, target, num, comment, choice=0):
		kpr = self.keeper
		return target is kpr and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice=0):
		num[0] = min(num[0], 1)
		
	
class Trig_RunawayBlackwing(TrigBoard):
	signals = ("TurnEnds",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		if objs := (kpr := self.keeper).Game.minionsAlive(3-kpr.ID): kpr.dealsDamage(numpyChoice(objs), 9)
		
	
class Trig_Saddlemaster(TrigBoard):
	signals = ("CardBeenPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID and "Beast" in kpr.Game.cardinPlay.race
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).addCardtoHand(numpyChoice(self.rngPool("Beasts")), kpr.ID)
		
	
class Trig_GlacierRacer(Spellburst):
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		objs = [obj for obj in kpr.Game.charsonBoard(3-kpr.ID) if obj.effects["Frozen"] > 0]
		self.keeper.dealsDamage(objs, 3)
		
	
class Trig_KeywardenIvory(Spellburst):
	description = "Spellburst: Add the discover card to your hand"
	def __init__(self, keeper, card=None):
		super().__init__(keeper)
		self.memory = card
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).addCardtoHand(self.memory, kpr.ID)
		
	def selfCopy(self, recipient):
		return type(self)(recipient, self.memory)
		
	
class Trig_ImprisonedCelestial(Spellburst):
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).giveEnchant(kpr.Game.minionsonBoard(kpr.ID), effGain="Divine Shield", source=ImprisonedCelestial)
		
	
class Trig_Lightsteed(TrigBoard):
	signals = ("MinionReceivesHeal",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.giveEnchant(target, 0, 2, source=Lightsteed)
		
	
class Trig_Shenanigans(Trig_Secret):
	signals = ("CardDrawn",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.ID != kpr.Game.turn == ID \
			   and kpr.Game.Counters.examCardsDrawnThisTurn(kpr.ID, veri_sum=1) == 2
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		if not (isinstance(target[0], Bananas) and target[0].creator is Shenanigans):
			kpr.Game.Hand_Deck.replaceCardDrawn(target, Bananas(kpr.Game, target[0].ID), kpr)
		
	
class Trig_SpikedWheel(Trig_SelfAura):
	signals = ("ArmorGained", "ArmorLost")
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.calcStat()
		
	
class Death_Showstopper(Deathrattle):
	description = "Deathrattle: Silence all minions"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.Game.silenceMinions(self.keeper.Game.minionsonBoard())
		
	
class Death_ClawMachine(Deathrattle):
	description = "Deathrattle: Draw a minion and give it +3/+3"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		minion, mana, entersHand = self.keeper.drawCertainCard(lambda card: card.category == "Minion")
		if entersHand: self.keeper.giveEnchant(minion, 3, 3, source=ClawMachine)
		
	
class Death_RenownedPerformer(Deathrattle):
	description = "Deathrattle: Summon two 1/1 Assistants with Rush"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		game, ID = (kpr := self.keeper).Game, kpr.ID
		kpr.summon([PerformersAssistant(game, ID) for _ in (0, 1)], relative="<>")
		
	
class Death_Greybough(Deathrattle):
	description = "Deathrattle: Give a random friendly minion 'Deathrattle: Summon Greybough'"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		if minions := (kpr := self.keeper).Game.minionsonBoard(kpr.ID):
			kpr.giveEnchant(numpyChoice(minions), trig=Death_SummonGreybough, trigType="Deathrattle")
		
	
class Death_SummonGreybough(Deathrattle):
	description = "Deathrattle: Summon Greybough"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).summon(Greybough(kpr.Game, kpr.ID))
		
	
class Death_DarkmoonTonk(Deathrattle):
	description = "Deathrattle: Fire four missiles at random enemies that deal 2 damage each"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		for _ in (0, 1, 2, 3):
			if enemies := self.keeper.Game.charsAlive(3-self.keeper.ID): self.keeper.dealsDamage(numpyChoice(enemies), 2)
			else: break
		
	
class Death_TicketMaster(Deathrattle):
	description = "Deathrattle: Shuffle 3 Tickets into your deck"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		keeper = self.keeper
		keeper.shuffleintoDeck([Tickets(keeper.Game, keeper.ID) for _ in (0, 1, 2)])
		
	
class Death_RedscaleDragontamer(Deathrattle):
	description = "Deathrattle: Draw a Dragon"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.drawCertainCard(lambda card: "Dragon" in card.race)
		
	
class Death_RingMatron(Deathrattle):
	description = "Deathrattle: Summon two 3/2 Imps"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		game, ID = (kpr := self.keeper).Game, kpr.ID
		kpr.summon([FieryImp(game, ID) for _ in (0, 1)], relative="<>")
		
	
class Death_BumperCar(Deathrattle):
	description = "Deathrattle: Add two 1/1 Riders with Rush to your hand"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.addCardtoHand([DarkmoonRider, DarkmoonRider], self.keeper.ID)
		
	
class Death_EnvoyRustwix(Deathrattle):
	description = "Deathrattle: Shuffle 3 random Prime Legendary minions into your deck"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		game, ID = (kpr := self.keeper).Game, kpr.ID
		kpr.shuffleintoDeck([prime(game, ID) for prime in numpyChoice(EnvoyRustwix.primeMinions, 3, replace=True)])
		
	
class CThuntheShattered_Effect(TrigEffect):
	signals, counter, trigType = ("CThunPiece",), 4, "Conn&TrigAura"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		#One can start piecing together CThun even if CThun isn't in their original deck
		self.memory = ["Body", "Eye", "Heart", "Maw"]
		
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return ID == self.ID and comment in self.memory
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.memory.remove(comment)
		self.counter -= 1
		if self.counter < 1:
			self.card.shuffleintoDeck(self.card)
			self.card.creator = None
			self.disconnect()
			del self.Game.trigsBoard[self.ID]["CThunPiece"]
		
	
class GameManaAura_IllidariStudies(GameManaAura_OneTime):
	by, temporary = -1, False
	def applicable(self, target): return target.ID == self.ID and "~Outcast" in target.index
		
	
class Stiltstepper_Effect(TrigEffect):
	signals, trigType = ("CardBeenPlayed",), "Conn&TurnEnd"
	def __init__(self, Game, ID, memory=None):
		super().__init__(Game, ID)
		self.memory = memory
		
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return ID == self.ID and subject is self.memory
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.card.giveHeroAttackArmor(self.ID, attGain=4, source=Stiltstepper)
		self.disconnect()
		
	
class Acrobatics_Effect(TrigEffect):
	signals, counter, trigType = ("CardBeenPlayed",), 2, "Conn&TurnEnd"
	def __init__(self, Game, ID, memory=()):
		super().__init__(Game, ID)
		self.memory = memory
		self.animate = False
		
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return ID == self.ID and subject in self.memory
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.memory.remove(subject)
		self.counter -= 1
		if self.card.btn: self.card.btn.trigAni(self.counter)
		if self.counter < 1:
			if self.Game.GUI: self.Game.GUI.showOffBoardTrig(self.card)
			self.Game.Hand_Deck.drawCard(self.ID)
			self.Game.Hand_Deck.drawCard(self.ID)
			self.disconnect()
		
	def assistCreateCopy(self, Copy):
		Copy.memory = [card.createCopy(Copy.Game) for card in self.memory]
		
	
class ExpendablePerformers_Effect(TrigEffect):
	signals, trigType, animate = ("ObjDied",), "Conn&TurnEnd", False
	def __init__(self, Game, ID, memory=()):
		super().__init__(Game, ID)
		self.memory = memory
		
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return target.ID == self.ID and target in self.memory
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.memory.remove(target)
		if not self.memory:
			self.disconnect()
			if self.Game.GUI: self.Game.GUI.showOffBoardTrig(self.card)
			self.card.summon([IllidariInitiate(self.Game, self.ID) for _ in range(7)])
		
	def assistCreateCopy(self, Copy):
		Copy.memory = [minion.createCopy(Copy.Game) for minion in self.memory]
		
	
class GameManaAura_LunarEclipse(GameManaAura_OneTime):
	by = -2
	def applicable(self, target): return target.ID == self.ID and target.category == "Spell"
		
	
class SolarEclipse_Effect(TrigEffect):
	signals, trigType = ("SpellBeenCast",), "Conn&TurnEnd&OnlyKeepOne"
	def __init__(self, Game, ID, memory=None):
		super().__init__(Game, ID)
		self.memory = memory #The Solar Eclipse card that casts this is restored.
		
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return ID == self.ID and subject is not self.memory  # This won't respond to the Solar Eclipse that sends the signal
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.Game.rules[self.ID]["Spells x2"] -= 1
		self.disconnect()
		
	def trigEffect(self):
		self.Game.rules[self.ID]["Spells x2"] -= 1
		self.disconnect()
		
	
class GameManaAura_GameMaster(GameManaAura_OneTime):
	to = 1
	def applicable(self, target): return target.ID == self.ID and target.race == "Secret"
		
	
class GameManaAura_FoxyFraud(GameManaAura_OneTime):
	by = -2
	def applicable(self, target): return target.ID == self.ID and "~Combo" in target.index
		
	
class LothraxiontheRedeemed_Effect(TrigEffect):
	signals, trigType = ("ObjBeenSummoned",), "Conn&TrigAura&OnlyKeepOne"
	def connect(self):
		trigs = getListinDict(self.Game.trigsBoard[self.ID], "ObjBeenSummoned")
		if (i := next((i for i, trig in enumerate(trigs) if isinstance(trig, LothraxiontheRedeemed_Effect)), -1)) > -1:
			trigs.append(trigs.pop(i)) #把给予圣盾的扳机移到最新的位置
		else:
			self.Game.trigAuras[self.ID].append(self)
			trigs.append(self)
			if self.Game.GUI: self.Game.GUI.heroZones[self.ID].addaTrig(self.card)
		
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return ID == self.ID and subject.name == "Silver Hand Recruit" and subject.category == "Minion"
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.card.giveEnchant(subject, effGain="Divine Shield", source=LothraxiontheRedeemed)
		
	
class SafetyInspector(Minion):
	Class, race, name = "Neutral", "", "Safety Inspector"
	mana, attack, health = 1, 1, 3
	name_CN = "安全检查员"
	numTargets, Effects, description = 0, "", "Battlecry: Shuffle the lowest-Cost card from your hand into your deck. Draw a card"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if indices := pickInds_LowestAttr(self.Game.Hand_Deck.hands[self.ID]):
			self.Game.Hand_Deck.shuffle_Hand2Deck(numpyChoice(indices), ID=self.ID, initiatorID=self.ID, getAll=False)
		self.Game.Hand_Deck.drawCard(self.ID)
		
	
class CostumedEntertainer(Minion):
	Class, race, name = "Neutral", "", "Costumed Entertainer"
	mana, attack, health = 2, 1, 2
	name_CN = "盛装演员"
	numTargets, Effects, description = 0, "", "Battlecry: Give a random minion in your hand +2/+2"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if minions := [card for card in self.Game.Hand_Deck.hands[self.ID] if card.category == "Minion"]:
			self.giveEnchant(numpyChoice(minions), 2, 2, source=CostumedEntertainer, add2EventinGUI=False)
		
	
class HorrendousGrowthCorrupt(Minion):
	Class, race, name = "Neutral", "", "Horrendous Growth"
	mana, attack, health = 2, 3, 3
	name_CN = "恐怖增生体"
	numTargets, Effects, description = 0, "", "Corrupt: Gain +1/+1. Can be Corrupted endlessly"
	index = "ToCorrupt~Uncollectible"
	trigHand = Trig_EndlessCorrupt
	
	
class HorrendousGrowth(Minion):
	Class, race, name = "Neutral", "", "Horrendous Growth"
	mana, attack, health = 2, 2, 2
	numTargets, Effects, description = 0, "", "Corrupt: Gain +1/+1. Can be Corrupted endlessly"
	name_CN = "恐怖增生体"
	trigHand, corruptedType = Trig_Corrupt, HorrendousGrowthCorrupt
	
	
class ParadeLeader(Minion):
	Class, race, name = "Neutral", "", "Parade Leader"
	mana, attack, health = 2, 2, 3
	numTargets, Effects, description = 0, "", "After you summon a Rush minion, give it +2 Attack"
	name_CN = "巡游领队"
	trigBoard = Trig_ParadeLeader		
	
	
class PrizeVendor(Minion):
	Class, race, name = "Neutral", "Murloc", "Prize Vendor"
	mana, attack, health = 2, 2, 3
	name_CN = "奖品商贩"
	numTargets, Effects, description = 0, "", "Battlecry: Both players draw a card"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.Game.Hand_Deck.drawCard(self.ID)
		self.Game.Hand_Deck.drawCard(3-self.ID)
		
	
class RockRager(Minion):
	Class, race, name = "Neutral", "Elemental", "Rock Rager"
	mana, attack, health = 2, 5, 1
	numTargets, Effects, description = 0, "Taunt", "Taunt"
	name_CN = "岩石暴怒者"
	
	
class Showstopper(Minion):
	Class, race, name = "Neutral", "", "Showstopper"
	mana, attack, health = 2, 3, 2
	numTargets, Effects, description = 0, "", "Deathrattle: Silence all minions"
	name_CN = "砸场游客"
	deathrattle = Death_Showstopper
	
	
class WrigglingHorror(Minion):
	Class, race, name = "Neutral", "", "Wriggling Horror"
	mana, attack, health = 2, 2, 1
	name_CN = "蠕动的恐魔"
	numTargets, Effects, description = 0, "", "Battlecry: Give adjacent minions +1/+1"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.onBoard and (neighbors := self.Game.neighbors2(self)[0]):
			self.giveEnchant(neighbors, 1, 1, source=WrigglingHorror)
		
	
class BananaVendor(Minion):
	Class, race, name = "Neutral", "", "Banana Vendor"
	mana, attack, health = 3, 2, 4
	name_CN = "香蕉商贩"
	numTargets, Effects, description = 0, "", "Battlecry: Add 2 Bananas to each player's hand"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.addCardtoHand([Bananas, Bananas], self.ID)
		self.addCardtoHand([Bananas, Bananas], 3-self.ID)
		
	
class DarkmoonDirigible_Corrupt(Minion):
	Class, race, name = "Neutral", "Mech", "Darkmoon Dirigible"
	mana, attack, health = 3, 3, 2
	name_CN = "暗月飞艇"
	numTargets, Effects, description = 0, "Divine Shield,Rush", "Corrupted. Divine Shield, Rush"
	index = "Uncollectible"
	
	
class DarkmoonDirigible(Minion):
	Class, race, name = "Neutral", "Mech", "Darkmoon Dirigible"
	mana, attack, health = 3, 3, 2
	numTargets, Effects, description = 0, "Divine Shield", "Divine Shield. Corrupt: Gain Rush"
	name_CN = "暗月飞艇"
	trigHand, corruptedType = Trig_Corrupt, DarkmoonDirigible_Corrupt
	
	
class DarkmoonStatue_Corrupt(Minion):
	Class, race, name = "Neutral", "", "Darkmoon Statue"
	mana, attack, health = 3, 4, 5
	name_CN = "暗月雕像"
	numTargets, Effects, description = 0, "", "Corrupted. Your other minions have +1 Attack"
	index = "Uncollectible"
	aura = Aura_DarkmoonStatue
	
	
class DarkmoonStatue(Minion):
	Class, race, name = "Neutral", "", "Darkmoon Statue"
	mana, attack, health = 3, 0, 5
	numTargets, Effects, description = 0, "", "Your other minions have +1 Attack. Corrupt: This gains +4 Attack"
	name_CN = "暗月雕像"
	aura, trigHand, corruptedType = Aura_DarkmoonStatue, Trig_Corrupt, DarkmoonStatue_Corrupt
	
	
class Gyreworm(Minion):
	Class, race, name = "Neutral", "Elemental", "Gyreworm"
	mana, attack, health = 3, 3, 2
	name_CN = "旋岩虫"
	numTargets, Effects, description = 1, "", "Battlecry: If you played an Elemental last turn, deal 3 damage"
	index = "Battlecry"
	def numTargetsNeeded(self, choice=0):
		return 1 if self.Game.Counters.examElementalsLastTurn(self.ID) else 0
		
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.examElementalsLastTurn(self.ID)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.Game.Counters.examElementalsLastTurn(self.ID): self.dealsDamage(target, 3)
		
	
class InconspicuousRider(Minion):
	Class, race, name = "Neutral", "", "Inconspicuous Rider"
	mana, attack, health = 3, 2, 2
	name_CN = "低调的游客"
	numTargets, Effects, description = 0, "", "Battlecry: Cast a Secret from your deck"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.Game.Secrets.deploySecretsfromDeck(self.ID, initiator=self)
		
	
class KthirRitualist(Minion):
	Class, race, name = "Neutral", "", "K'thir Ritualist"
	mana, attack, health = 3, 4, 4
	name_CN = "克熙尔祭师"
	numTargets, Effects, description = 0, "Taunt", "Taunt. Battlecry: Add a random 4-Cost minion to your opponent's hand"
	index = "Battlecry"
	poolIdentifier = "4-Cost Minions"
	@classmethod
	def generatePool(cls, pools):
		return "4-Cost Minions", pools.MinionsofCost[4]
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.addCardtoHand(numpyChoice(self.rngPool("4-Cost Minions")), 3-self.ID)
		
	
class CircusAmalgam(Minion):
	Class, race, name = "Neutral", "Elemental,Mech,Demon,Murloc,Dragon,Beast,Pirate,Quilboar,Totem", "Circus Amalgam"
	mana, attack, health = 4, 4, 5
	numTargets, Effects, description = 0, "Taunt", "Taunt. This has all minion types"
	name_CN = "马戏团融合怪"
	
	
class CircusMedic_Corrupt(Minion):
	Class, race, name = "Neutral", "", "Circus Medic"
	mana, attack, health = 4, 3, 4
	name_CN = "马戏团医师"
	numTargets, Effects, description = 1, "", "Corrupted. Battlecry: Deal 4 damage"
	index = "Battlecry~Uncollectible"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(target, 4)
		
	
class CircusMedic(Minion):
	Class, race, name = "Neutral", "", "Circus Medic"
	mana, attack, health = 4, 3, 4
	name_CN = "马戏团医师"
	numTargets, Effects, description = 1, "", "Battlecry: Restore 4 Health. Corrupt: Deal 4 damage instead"
	index = "Battlecry~ToCorrupt"
	trigHand, corruptedType = Trig_Corrupt, CircusMedic_Corrupt
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.heals(target, self.calcHeal(4))
		
	
class FantasticFirebird(Minion):
	Class, race, name = "Neutral", "Elemental", "Fantastic Firebird"
	mana, attack, health = 4, 3, 5
	numTargets, Effects, description = 0, "Windfury", "Windfury"
	name_CN = "炫目火鸟"
	
	
class KnifeVendor(Minion):
	Class, race, name = "Neutral", "", "Knife Vendor"
	mana, attack, health = 4, 3, 4
	name_CN = "小刀商贩"
	numTargets, Effects, description = 0, "", "Battlecry: Deal 4 damage to each hero"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage([self.Game.heroes[1], self.Game.heroes[2]], [4, 4])
		
	
class DerailedCoaster(Minion):
	Class, race, name = "Neutral", "", "Derailed Coaster"
	mana, attack, health = 5, 3, 2
	name_CN = "脱轨过山车"
	numTargets, Effects, description = 0, "", "Battlecry: Summon a 1/1 Rider with Rush for each minion in your hand"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if num := sum(card.category == "Minion" for card in self.Game.Hand_Deck.hands[self.ID]):
			self.summon([DarkmoonRider(self.Game, self.ID) for i in range(num)])
		
	
class DarkmoonRider(Minion):
	Class, race, name = "Neutral", "", "Darkmoon Rider"
	mana, attack, health = 1, 1, 1
	name_CN = "暗月乘客"
	numTargets, Effects, description = 0, "Rush", "Rush"
	index = "Uncollectible"
	
	
class FleethoofPearltusk_Corrupt(Minion):
	Class, race, name = "Neutral", "Beast", "Fleethoof Pearltusk"
	mana, attack, health = 5, 8, 8
	name_CN = "迅蹄珠齿象"
	numTargets, Effects, description = 0, "Rush", "Rush"
	index = "Uncollectible"
	
	
class FleethoofPearltusk(Minion):
	Class, race, name = "Neutral", "Beast", "Fleethoof Pearltusk"
	mana, attack, health = 5, 4, 4
	numTargets, Effects, description = 0, "Rush", "Rush. Corrupt: Gain +4/+4"
	name_CN = "迅蹄珠齿象"
	trigHand, corruptedType = Trig_Corrupt, FleethoofPearltusk_Corrupt
	
	
class OptimisticOgre(Minion):
	Class, race, name = "Neutral", "", "Optimistic Ogre"
	mana, attack, health = 5, 6, 7
	numTargets, Effects, description = 0, "", "50% chance to attack the correct enemy"
	name_CN = "乐观的食人魔"
	trigBoard = Trig_OptimisticOgre		
	
	
class ClawMachine(Minion):
	Class, race, name = "Neutral", "Mech", "Claw Machine"
	mana, attack, health = 6, 6, 3
	numTargets, Effects, description = 0, "Rush", "Rush. Deathrattle: Draw a minion and give it +3/+3"
	name_CN = "娃娃机"
	deathrattle = Death_ClawMachine
	
	
class SilasDarkmoon(Minion):
	Class, race, name = "Neutral", "", "Silas Darkmoon"
	mana, attack, health = 7, 4, 4
	name_CN = "希拉斯暗月"
	numTargets, Effects, description = 0, "", "Battlecry: Choose a direction to rotate all minions"
	index = "Battlecry~Legendary"
	def rotateMinions(self, giveLeftmost=True):
		miniontoGive, miniontoTake, ownID = None, None, self.ID
		ownBoard, enemyBoard = self.Game.minions[ownID], self.Game.minions[3-ownID]
		ownMinions, enemyMinions = self.Game.minionsonBoard(ownID), self.Game.minionsonBoard(3-ownID)
		if ownMinions or enemyMinions: #give left most = take right most
			if ownMinions:
				(miniontoGive := ownMinions[0] if giveLeftmost else ownMinions[-1]).disappears()
				miniontoGive.ID = 3 - ownID
				miniontoGive.effects["Borrowed"] = 0
				ownBoard.remove(miniontoGive)
				if giveLeftmost: enemyBoard.insert(0, miniontoGive)
				else: enemyBoard.append(miniontoGive)
			if enemyMinions:
				(miniontoTake := enemyMinions[-1] if giveLeftmost else enemyMinions[0]).disappears()
				miniontoTake.ID = ownID
				miniontoTake.effects["Borrowed"] = 0
				enemyBoard.remove(miniontoTake)
				if giveLeftmost: ownBoard.append(miniontoTake)
				else: ownBoard.insert(0, miniontoTake)
			self.Game.sortPos()
			if miniontoGive:
				miniontoGive.appears(firstTime=False)
				miniontoGive.decideAttChances_base()
			if miniontoTake:
				miniontoTake.appears(firstTime=False)
				miniontoTake.decideAttChances_base()
			if GUI := self.Game.GUI:
				GUI.seqHolder[-1].append(GUI.PARALLEL(GUI.minionZones[1].placeCards(add2Queue=False),
													  GUI.minionZones[2].placeCards(add2Queue=False)))
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		option = self.chooseFixedOptions(comment, options=[RotateThisWay(), RotateThatWay()])
		SilasDarkmoon.rotateMinions(self, giveLeftmost=isinstance(option, RotateThisWay))
		
	
class RotateThisWay(Option):
	name, description = "Rotate This Way", "Give your LEFTMOST minion"
	mana, attack, health = -1, -1, -1
	
	
class RotateThatWay(Option):
	name, description = "Rotate That Way", "Give your RIGHTMOST minion"
	mana, attack, health = -1, -1, -1
	
	
class Strongman_Corrupt(Minion):
	Class, race, name = "Neutral", "", "Strongman"
	mana, attack, health = 0, 6, 6
	name_CN = "大力士"
	numTargets, Effects, description = 0, "Taunt", "Corrupted. Taunt"
	index = "Uncollectible"
	
	
class Strongman(Minion):
	Class, race, name = "Neutral", "", "Strongman"
	mana, attack, health = 7, 6, 6
	numTargets, Effects, description = 0, "Taunt", "Taunt. Corrupt: This costs (0)"
	name_CN = "大力士"
	trigHand, corruptedType = Trig_Corrupt, Strongman_Corrupt
	
	
class CarnivalClown_Corrupt(Minion):
	Class, race, name = "Neutral", "", "Carnival Clown"
	mana, attack, health = 9, 4, 4
	name_CN = "狂欢小丑"
	numTargets, Effects, description = 0, "Taunt", "Corrupted. Taunt. Battlecry: Fill your board with copies of this"
	index = "Battlecry~Uncollectible"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if not self.dead: self.summon([self.copyCard(self, self.ID) for _ in range(7)], relative="<>")
		
	
class CarnivalClown(Minion):
	Class, race, name = "Neutral", "", "Carnival Clown"
	mana, attack, health = 9, 4, 4
	name_CN = "狂欢小丑"
	numTargets, Effects, description = 0, "Taunt", "Taunt. Battlecry: Summon 2 copies of this. Corrupted: Fill your board with copies"
	index = "Battlecry~ToCorrupt"
	trigHand, corruptedType = Trig_Corrupt, CarnivalClown_Corrupt
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if not self.dead: self.summon([self.copyCard(self, self.ID) for _ in (0, 1)], relative="<>")
		
	
class BodyofCThun(Spell):
	Class, school, name = "Neutral", "", "Body of C'Thun"
	numTargets, mana, Effects = 0, 5, ""
	name_CN = "克苏恩之躯"
	description = "Piece of C'Thun(0/4). Summon a 6/6 C'Thun's body with Taunt"
	index = "Uncollectible"
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def text(self): return CThuntheShattered.getProgress(self)

	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon(CThunsBody(self.Game, self.ID))
		#Assume the spell effect will increase the counter
		if "CThunPiece" not in self.Game.trigsBoard[self.ID]:
			CThuntheShattered_Effect(self.Game, self.ID).connect()
		self.Game.sendSignal("CThunPiece", self.ID, None, None, 0, "Body")
		
	
class CThunsBody(Minion):
	Class, race, name = "Neutral", "", "C'Thun's Body"
	mana, attack, health = 6, 6, 6
	name_CN = "克苏恩之躯"
	numTargets, Effects, description = 0, "Taunt", "Taunt"
	index = "Uncollectible"
	
	
class EyeofCThun(Spell):
	Class, school, name = "Neutral", "", "Eye of C'Thun"
	numTargets, mana, Effects = 0, 5, ""
	name_CN = "克苏恩之眼"
	description = "Deal 7 damage randomly split among all enemies"
	index = "Uncollectible"
	def text(self): return CThuntheShattered.getProgress(self) + ", %d"%self.calcDamage(7)

	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		side, game = 3 - self.ID, self.Game
		for _ in range(self.calcDamage(7)):
			if objs := game.charsAlive(side): self.dealsDamage(numpyChoice(objs), 1)
			else: break
		if "CThunPiece" not in self.Game.trigsBoard[self.ID]:
			CThuntheShattered_Effect(self.Game, self.ID).connect()
		self.Game.sendSignal("CThunPiece", self.ID, None, None, 0, "Eye")
		
	
class HeartofCThun(Spell):
	Class, school, name = "Neutral", "", "Heart of C'Thun"
	numTargets, mana, Effects = 0, 5, ""
	name_CN = "克苏恩之心"
	description = "Deal 3 damage to all minions"
	index = "Uncollectible"
	def text(self): return CThuntheShattered.getProgress(self) + ", %d"%self.calcDamage(3)

	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(self.Game.minionsonBoard(), self.calcDamage(3))
		if "CThunPiece" not in self.Game.trigsBoard[self.ID]:
			CThuntheShattered_Effect(self.Game, self.ID).connect()
		self.Game.sendSignal("CThunPiece", self.ID, None, None, 0, "Heart")
		
	
class MawofCThun(Spell):
	Class, school, name = "Neutral", "", "Maw of C'Thun"
	numTargets, mana, Effects = 1, 5, ""
	name_CN = "克苏恩之口"
	description = "Destroy a minion"
	index = "Uncollectible"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def text(self): return CThuntheShattered.getProgress(self)

	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.Game.kill(self, target)
		#Assume the counter still works even if there is no target[0] designated
		if "CThunPiece" not in self.Game.trigsBoard[self.ID]:
			CThuntheShattered_Effect(self.Game, self.ID).connect()
		self.Game.sendSignal("CThunPiece", self.ID, None, None, 0, "Maw")
		
	
class CThuntheShattered(Minion):
	Class, race, name = "Neutral", "", "C'Thun, the Shattered"
	mana, attack, health = 10, 6, 6
	name_CN = "克苏恩，破碎之劫"
	numTargets, Effects, description = 0, "", "Start of Game: Break into pieces. Battlecry: Deal 30 damage randomly split among all enemies"
	index = "Battlecry~Legendary"
	trigEffect = CThuntheShattered_Effect
	@classmethod
	def getProgress(cls, card):
		trigsBoard = card.Game.trigsBoard[card.ID]
		trig = next((trig for trig in trigsBoard if isinstance(trig, CThuntheShattered_Effect)), None) if "CThunPiece" in trigsBoard else None
		return "%d/4" % (len(trig.memory) if trig else 0)

	def startofGame(self):
		#WON't show up in the starting hand
		#Remove the card from deck. Assume the final card WON't count as deck original card
		#https://www.iyingdi.com/web/article/search/108538
		#克苏恩不会出现在起手手牌中，只能在之后抽到碎片
		#不在衍生池中，不能被随机发生和召唤等
		#碎片是可以在第一次抽牌中抽到的，计入“开始时不在牌库中的牌”
		#带克苏恩会影响巴库的触发，不影响狼王
		#四张不同的碎片被打出后才会触发洗入克苏恩的效果，可以被法术反制
		game, ID = self.Game, self.ID
		game.Hand_Deck.extractfromDeck(game.Hand_Deck.decks[self.ID].index(self), ID=self.ID)
		self.shuffleintoDeck([BodyofCThun(game, ID), EyeofCThun(game, ID), HeartofCThun(game, ID), MawofCThun(game, ID)])
		CThuntheShattered_Effect(game, ID).connect()
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		side, game = 3-self.ID, self.Game
		for _ in range(30):
			if objs := game.charsAlive(side): self.dealsDamage(numpyChoice(objs), 1)
			else: break
		
	
class DarkmoonRabbit(Minion):
	Class, race, name = "Neutral", "Beast", "Darkmoon Rabbit"
	mana, attack, health = 10, 1, 1
	numTargets, Effects, description = 0, "Rush,Poisonous,Sweep", "Rush, Poisonous. Also damages the minions next to whomever this attacks"
	name_CN = "暗月兔子"
	
	
class NZothGodoftheDeep(Minion):
	Class, race, name = "Neutral", "", "N'Zoth, God of the Deep"
	mana, attack, health = 9, 5, 7
	name_CN = "恩佐斯，深渊之神"
	numTargets, Effects, description = 0, "", "Battlecry: Resurrect a friendly minion of each minion type"
	index = "Battlecry~Legendary"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		#A single Amalgam minion won't be resurrected multiple times
		game, ID = self.Game, self.ID
		#First, categorize. Second, from each type, select one.
		tups, pool = [], game.Counters.examDeads(self.ID, veri_sum_ls=2, cond=lambda card: card.race)
		races = {"Beast": [], "Pirate": [], "Elemental": [], "Mech": [], "Dragon": [], "Quilboar": [], "Totem": [], "Demon": [], "Murloc": [], "All": []}
		#假设机制如下 ，在依次决定几个种族召唤随从，融合怪的随从池和单一种族的随从池合并计算随机。这个种族下如果没有召唤出一个融合怪，则它可以继续等待，如果召唤出来了，则将其移出随从池
		for tup in pool:
			if race := tup[0].race: races[race if len(race) < 10 else "All"].append(tup)
		for race in ["Elemental", "Mech", "Demon", "Murloc", "Dragon", "Beast", "Pirate", "Quilboar", "Totem"]: #假设种族顺序是与融合怪的牌面描述 一致的
			a, b = len(races[race]), len(races["All"])
			if a or b:
				p1 = a / (a + b)
				isAmalgam = numpyChoice([0, 1], p=[p1, 1-p1])
				tups.append(races["All"].pop(numpyRandint(b)) if isAmalgam else races[race][numpyRandint(a)])
		if tups: self.summon([game.fabCard(tup, ID, self) for tup in tups])
		
	
class CurseofFlesh(Spell):
	Class, school, name = "Neutral", "", "Curse of Flesh"
	numTargets, mana, Effects = 0, 0, ""
	name_CN = "血肉诅咒"
	description = "Fill the board with random minions, then give yours Rush"
	index = "Uncollectible"
	poolIdentifier = "Minions to Summon"
	@classmethod
	def generatePool(cls, pools):
		return "Minions to Summon", [card for cards in pools.MinionsofCost.values() for card in cards]
		
	def __init__(self, Game, ID, yogg=None):
		super().__init__(Game, ID)
		self.yogg = yogg
		
	def cast(self, prefered=None, target=()):
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
		self.yogg.giveEnchant([minion for minion in ownMinions if minion.onBoard], effGain="Rush", source=CurseofFlesh)
		
	
class DevouringHunger(Spell):
	Class, school, name = "Neutral", "", "Devouring Hunger"
	numTargets, mana, Effects = 0, 0, ""
	name_CN = "吞噬之饥"
	description = "Destroy all other minions. Gain their Attack and Health"
	index = "Uncollectible"
	def __init__(self, Game, ID, yogg=None):
		super().__init__(Game, ID)
		self.yogg = yogg
		
	def cast(self, prefered=None, target=()):
		game = self.Game
		if game.GUI: game.GUI.showOffBoardTrig(self)
		attGain, healthGain = 0, 0
		for minion in game.minionsonBoard():
			if minion is not self.yogg:
				attGain += max(0, minion.attack)
				healthGain += max(0, minion.health)
				game.kill(self.yogg, minion)
		if self.yogg.onBoard or self.yogg.inHand: self.giveEnchant(self.yogg, attGain, healthGain, source=DevouringHunger)
		
	
class HandofFate(Spell):
	Class, school, name = "Neutral", "", "Hand of Fate"
	numTargets, mana, Effects = 0, 0, ""
	name_CN = "命运之手"
	description = "Fill your hand with random spells. They cost (0) this turn"
	index = "Uncollectible"
	poolIdentifier = "Spells"
	@classmethod
	def generatePool(cls, pools):
		return "Spells", [card for cards in pools.ClassSpells.values() for card in cards]

	def __init__(self, Game, ID, yogg=None):
		super().__init__(Game, ID)
		self.yogg = yogg

	def cast(self, prefered=None, target=()):
		game = self.Game
		if game.GUI: game.GUI.showOffBoardTrig(self)
		spells = [spell(game, self.ID) for spell in numpyChoice(self.rngPool("Spells"), game.Hand_Deck.spaceinHand(self.ID), replace=True)]
		self.yogg.addCardtoHand(spells, self.ID)
		for spell in spells:
			if spell.inHand: ManaMod(spell, to=0, until=0).applies()
		
	
class MindflayerGoggles(Spell):
	Class, school, name = "Neutral", "", "Mindflayer Goggles"
	numTargets, mana, Effects = 0, 0, ""
	name_CN = "夺心护目镜"
	description = "Take control of three random enemy minions"
	index = "Uncollectible"
	def __init__(self, Game, ID, yogg=None):
		super().__init__(Game, ID)
		self.yogg = yogg

	def cast(self, prefered=None, target=()):
		game, side = self.Game, 3 - self.ID
		if game.GUI: game.GUI.showOffBoardTrig(self)
		for _ in range(3):
			minions = game.minionsAlive(side)
			if minions: game.minionSwitchSide(numpyChoice(minions))
		
	
class Mysterybox(Spell):
	Class, school, name = "Neutral", "", "Mysterybox"
	numTargets, mana, Effects = 0, 0, ""
	name_CN = "神秘魔盒"
	description = "Cast a random spell for each spell you've cast this game(targets chosen randomly)"
	index = "Uncollectible"
	def __init__(self, Game, ID, yogg=None):
		super().__init__(Game, ID)
		self.yogg = yogg

	def cast(self, prefered=None, target=()):
		game = self.Game
		if game.GUI: game.GUI.showOffBoardTrig(self)
		num = game.Counters.examCardPlays(self.ID, veri_sum_ls=1, cond=lambda tup: tup[0].category == "Spell")
		spells = [spell(game, self.ID) for spell in numpyChoice(self.rngPool("Spells"), num, replace=True)]
		for spell in spells:
			spell.cast()
			game.gathertheDead(decideWinner=True)
		
	
class RodofRoasting(Spell):
	Class, school, name = "Neutral", "", "Rod of Roasting"
	numTargets, mana, Effects = 0, 0, ""
	name_CN = "燃烧权杖"
	description = "Cast 'Pyroblast' randomly until a player dies"
	index = "Uncollectible"
	def __init__(self, Game, ID, yogg=None):
		super().__init__(Game, ID)
		self.yogg = yogg

	def cast(self, prefered=None, target=()):
		game = self.Game
		if game.GUI: game.GUI.showOffBoardTrig(self)
		i = 0
		while i < 30 and game.heroes[1].health > 0 and not game.heroes[1].dead and game.heroes[2].health > 0 and not game.heroes[2].dead:
			if Pyroblast(game, self.ID).cast(prefered=lambda obj: obj.health > 0 and not obj.dead):
				i += 1
				game.gathertheDead(decideWinner=True)
			else: break
		if i: game.heroes[3-self.ID].dead = True #假设在30次循环后如果还没有人死亡的话，则直接杀死对方英雄
		
	
class YoggSaronMasterofFate(Minion):
	Class, race, name = "Neutral", "", "Yogg-Saron, Master of Fate"
	mana, attack, health = 10, 7, 5
	name_CN = "尤格-萨隆，命运主宰"
	numTargets, Effects, description = 0, "", "Battlecry: If you've cast 10 spells this game, spin the Wheel of Yogg-Saron"
	index = "Battlecry~Legendary"
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.examCardPlays(self.ID, veri_sum_ls=1, cond=lambda tup: tup[0].category == "Spell") >= 10
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.Game.Counters.examCardPlays(self.ID, veri_sum_ls=1, cond=lambda tup: tup[0].category == "Spell") >= 10:
			#CurseofFlesh "Fill the board with random minions, then give your Rush"
			#DevouringHunger "Destroy all other minions. Gain their Attack and Health"
			#HandofFate "Fill your hand with random spells. They cost (0) this turn"
			#MindflayerGoggles "Take control of three random enemy minions"
			#Mysterybox "Cast a random spell for each spell you've cast this game(objs chosen randomly)"
			#RodofRoasting "Cast 'Pyroblast' randomly until a player dies"
			wheel = numpyChoice([CurseofFlesh, DevouringHunger, HandofFate, MindflayerGoggles, Mysterybox, RodofRoasting],
								p=[0.19, 0.19, 0.19, 0.19, 0.19, 0.05])
			wheel(self.Game, self.ID, self).cast()
		
	
class YShaarjtheDefiler(Minion):
	Class, race, name = "Neutral", "", "Y'Shaarj, the Defiler"
	mana, attack, health = 10, 10, 10
	name_CN = "亚煞极，污染之源"
	numTargets, Effects, description = 0, "", "Battlecry: Add a copy of each Corrupted card you've played this game to your hand. They cost (0) this turn"
	index = "Battlecry~Legendary"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		game, ID = self.Game, self.ID
		if (n := game.Hand_Deck.spaceinHand(ID)) > 0 and \
				(tups := game.Counters.examCardPlays(self.ID, veri_sum_ls=2, cond=lambda tup: "_Corrupt" in tup[0].__name__)):
			tups = numpyChoice(tups, min(len(tups), n), replace=False)
			self.addCardtoHand((cards := [game.fabCard(tup, ID, self) for tup in tups]), ID)
			for card in cards:
				if card.inHand: ManaMod(card, to=0, until=0).applies()
		
	
class FelscreamBlast(Spell):
	Class, school, name = "Demon Hunter", "Fel", "Felscream Blast"
	numTargets, mana, Effects = 1, 1, "Lifesteal"
	description = "Lifesteal. Deal 1 damage to a minion and its neighbors"
	name_CN = "邪吼冲击"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		damage = self.calcDamage(1)
		for obj in target:
			self.dealsDamage([obj]+self.Game.neighbors2(obj)[0], damage)
		
	
class ThrowGlaive(Spell):
	Class, school, name = "Demon Hunter", "", "Throw Glaive"
	numTargets, mana, Effects = 1, 1, ""
	description = "Deal 2 damage to a minion. If it dies, add a temporary copy of this to your hand"
	name_CN = "投掷利刃"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def text(self): return self.calcDamage(2)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for obj in self.dealsDamage(target, self.calcDamage(2))[0]:
			if obj.health < 1 or obj.dead:
				card = ThrowGlaive(self.Game, self.ID)
				card.trigsHand = [Trig_Echo(card)]
				self.addCardtoHand(card, self.ID)
		
	
class RedeemedPariah(Minion):
	Class, race, name = "Demon Hunter", "", "Redeemed Pariah"
	mana, attack, health = 2, 2, 3
	numTargets, Effects, description = 0, "", "After you play an Outcast card, gain +1/+1"
	name_CN = "获救的流民"
	trigBoard = Trig_RedeemedPariah		
	
	
class Acrobatics(Spell):
	Class, school, name = "Demon Hunter", "", "Acrobatics"
	numTargets, mana, Effects = 0, 3, ""
	description = "Draw 2 cards. If you play both this turn, draw 2 more"
	name_CN = "空翻杂技"
	trigEffect = Acrobatics_Effect
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		card1, mana, entersHand = self.Game.Hand_Deck.drawCard(self.ID)
		if entersHand:
			card2, mana, entersHand = self.Game.Hand_Deck.drawCard(self.ID)
			if entersHand: Acrobatics_Effect(self.Game, self.ID, [card1, card2]).connect()
		
	
class DreadlordsBite(Weapon):
	Class, name, description = "Demon Hunter", "Dreadlord's Bite", "Outcast: Deal 1 damage to all enemies"
	mana, attack, durability, Effects = 3, 2, 2, ""
	name_CN = "恐惧魔王之咬"
	index = "Outcast"
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.outcastcanTrig(self)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if posinHand in (-1, 0):
			self.dealsDamage(self.Game.charsonBoard(3-self.ID), 1)
		
	
class FelsteelExecutioner_Corrupt(Weapon):
	Class, name, description = "Demon Hunter", "Felsteel Executioner", "Corrupted"
	mana, attack, durability, Effects = 3, 4, 3, ""
	name_CN = "魔钢处决者"
	index = "Uncollectible"
	
	
class FelsteelExecutioner(Minion):
	Class, race, name = "Demon Hunter", "Elemental", "Felsteel Executioner"
	mana, attack, health = 3, 4, 3
	numTargets, Effects, description = 0, "", "Corrupt: Become a weapon"
	name_CN = "魔钢处决者"
	trigHand, corruptedType = Trig_Corrupt, FelsteelExecutioner_Corrupt
	
	
class LineHopper(Minion):
	Class, race, name = "Demon Hunter", "", "Line Hopper"
	mana, attack, health = 3, 3, 4
	numTargets, Effects, description = 0, "", "Your Outcast cards cost (1) less"
	name_CN = "越线的游客"
	aura = ManaAura_LineHopper
	
	
class InsatiableFelhound_Corrupt(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Insatiable Felhound"
	mana, attack, health = 3, 3, 6
	name_CN = "贪食地狱犬"
	numTargets, Effects, description = 0, "Taunt,Lifesteal", "Taunt, Lifesteal"
	index = "Uncollectible"
	
	
class InsatiableFelhound(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Insatiable Felhound"
	mana, attack, health = 3, 2, 5
	numTargets, Effects, description = 0, "Taunt", "Taunt. Corrupt: Gain +1/+1 and Lifesteal"
	name_CN = "贪食地狱犬"
	trigHand, corruptedType = Trig_Corrupt, InsatiableFelhound_Corrupt
	
	
class RelentlessPursuit(Spell):
	Class, school, name = "Demon Hunter", "", "Relentless Pursuit"
	numTargets, mana, Effects = 0, 3, ""
	description = "Give your hero +4 Attack and Immune this turn"
	name_CN = "冷酷追杀"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveHeroAttackArmor(self.ID, attGain=4, source=RelentlessPursuit)
		self.giveEnchant(self.Game.heroes[self.ID], effGain="Immune", source=RelentlessPursuit)
		self.Game.rules[self.ID]["ImmuneThisTurn"] += 1
		
	
class Stiltstepper(Minion):
	Class, race, name = "Demon Hunter", "", "Stiltstepper"
	mana, attack, health = 3, 4, 1
	name_CN = "高跷艺人"
	numTargets, Effects, description = 0, "", "Battlecry: Draw a card. If you play it this turn, give your hero +4 Attack this turn"
	index = "Battlecry"
	trigEffect = Stiltstepper_Effect
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		card, mana, entersHand = self.Game.Hand_Deck.drawCard(self.ID)
		if entersHand: Stiltstepper_Effect(self.Game, self.ID, card).connect()
		
	
class Ilgynoth(Minion):
	Class, race, name = "Demon Hunter", "", "Il'gynoth"
	mana, attack, health = 6, 4, 8
	name_CN = "伊格诺斯"
	numTargets, Effects, description = 0, "Lifesteal", "Lifesteal. Your Lifesteal damages the enemy hero instead of healing you"
	index = "Legendary"
	aura = GameRuleAura_Ilgynoth
	
	
class RenownedPerformer(Minion):
	Class, race, name = "Demon Hunter", "", "Renowned Performer"
	mana, attack, health = 4, 3, 3
	numTargets, Effects, description = 0, "Rush", "Rush. Deathrattle: Summon two 1/1 Assistants with Rush"
	name_CN = "知名表演者"
	deathrattle = Death_RenownedPerformer
	
	
class PerformersAssistant(Minion):
	Class, race, name = "Demon Hunter", "", "Performer's Assistant"
	mana, attack, health = 1, 1, 1
	name_CN = "演出助手"
	numTargets, Effects, description = 0, "Taunt", "Taunt"
	index = "Uncollectible"
	
	
class ZaitheIncredible(Minion):
	Class, race, name = "Demon Hunter", "", "Zai, the Incredible"
	mana, attack, health = 5, 5, 3
	name_CN = "扎依，出彩艺人"
	numTargets, Effects, description = 0, "", "Battlecry: Copy the left- and right-most cards in your hand"
	index = "Battlecry~Legendary"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if hand := (HD := self.Game.Hand_Deck).hands[self.ID]:
			for i in (0, -1):
				if HD.spaceinHand(self.ID): self.addCardtoHand(self.copyCard(hand[i], self.ID), self.ID, pos=i)
		
	
class BladedLady(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Bladed Lady"
	mana, attack, health = 6, 6, 6
	numTargets, Effects, description = 0, "Rush", "Rush. Costs (1) if your hero has 6 or more Attack"
	name_CN = "刀锋舞娘"
	trigHand = Trig_BladedLady
	def selfManaChange(self):
		if self.Game.heroes[self.ID].attack > 5: self.mana = 1
		
	
class ExpendablePerformers(Spell):
	Class, school, name = "Demon Hunter", "", "Expendable Performers"
	numTargets, mana, Effects = 0, 7, ""
	description = "Summon seven 1/1 Illidari with Rush. If they all die this turn, summon seven more"
	name_CN = "演员大接力"
	trigEffect = ExpendablePerformers_Effect
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		#只要召唤到场上的全部死亡即可，不用7个都在场上
		self.summon(minions := [IllidariInitiate(self.Game, self.ID) for i in range(7)])
		if minions := [minion for minion in minions if minion.onBoard]:
			ExpendablePerformers_Effect(self.Game, self.ID, minions).connect()
		
	
class GuesstheWeight(Spell):
	Class, school, name = "Druid", "", "Guess the Weight"
	numTargets, mana, Effects = 0, 2, ""
	description = "Draw a card. Guess if your next card costs more or less to draw it"
	name_CN = "猜重量"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		card, firstCost, entersHand = self.Game.Hand_Deck.drawCard(self.ID)
		if entersHand and (deck := self.Game.Hand_Deck.decks[self.ID]):
			secondCost = deck[-1].mana
			option = self.chooseFixedOptions(comment, options=[NextCostsMore(firstCost, secondCost),
																NextCostsLess(firstCost, secondCost)])
			bingo = (isinstance(option, NextCostsLess) and option.firstCost > option.secondCost) \
					or (isinstance(option, NextCostsMore) and option.firstCost < option.secondCost)
			if self.Game.GUI: self.Game.GUI.revealaCardfromDeckAni(self.ID, -1, bingo)
			if bingo: self.Game.Hand_Deck.drawCard(self.ID)
		
	
class NextCostsMore(Option):
	name = "Costs More"
	mana, attack, health = 0, -1, -1
	def __init__(self, firstCost=0, secondCost=0):
		super().__init__()
		self.firstCost, self.secondCost = firstCost, secondCost
		
	
class NextCostsLess(Option):
	name = "Costs Less"
	mana, attack, health = 0, -1, -1
	def __init__(self, firstCost=0, secondCost=0):
		super().__init__()
		self.firstCost, self.secondCost = firstCost, secondCost
		
	
class LunarEclipse(Spell):
	Class, school, name = "Druid", "Arcane", "Lunar Eclipse"
	numTargets, mana, Effects = 1, 2, ""
	description = "Deal 3 damage to a minion. Your next spell this turn costs (2) less"
	name_CN = "月蚀"
	trigEffect = GameManaAura_LunarEclipse
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def text(self): return self.calcDamage(3)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(target, self.calcDamage(3))
		GameManaAura_LunarEclipse(self.Game, self.ID).auraAppears()
		
	
class SolarEclipse(Spell):
	Class, school, name = "Druid", "Nature", "Solar Eclipse"
	numTargets, mana, Effects = 0, 2, ""
	description = "Your next spell this turn casts twice"
	name_CN = "日蚀"
	trigEffect = SolarEclipse_Effect
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.Game.rules[self.ID]["Spells x2"] += 1
		SolarEclipse_Effect(self.Game, self.ID, self).connect()
		
	
class FaireArborist_Corrupt(Minion):
	Class, race, name = "Druid", "", "Faire Arborist"
	mana, attack, health = 3, 2, 2
	name_CN = "马戏团树艺师"
	numTargets, Effects, description = 0, "", "Corrupted. Summon a 2/2 Treant. Draw a card"
	index = "Uncollectible"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
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
	name_CN = "马戏团树艺师"
	numTargets, Effects, description = 0, "", "Choose One- Draw a card; or Summon a 2/2 Treant. Corrupt: Do both"
	index = "ToCorrupt"
	trigHand, corruptedType = Trig_Corrupt, FaireArborist_Corrupt
	options = (PrunetheFruit_Option, DigItUp_Option)
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		#对于抉择随从而言，应以与战吼类似的方式处理，打出时抉择可以保持到最终结算。但是打出时，如果因为鹿盔和发掘潜力而没有选择抉择，视为到对方场上之后仍然可以而没有如果没有
		if choice: #"ChooseBoth" aura gives choice of -1
			self.summon(Treant_Darkmoon(self.Game, self.ID))
		if choice < 1:
			self.Game.Hand_Deck.drawCard(self.ID)
		
	
class Treant_Darkmoon(Minion):
	Class, race, name = "Druid", "", "Treant"
	mana, attack, health = 2, 2, 2
	name_CN = "树人"
	numTargets, Effects, description = 0, "", ""
	index = "Uncollectible"
	
	
class MoontouchedAmulet_Corrupt(Spell):
	Class, school, name = "Druid", "", "Moontouched Amulet"
	numTargets, mana, Effects = 0, 3, ""
	name_CN = "月触项链"
	description = "Corrupted. Give your hero +4 Attack this turn. And gain 6 Armor"
	index = "Uncollectible"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveHeroAttackArmor(self.ID, attGain=4, armor=6, source=MoontouchedAmulet_Corrupt)
		
	
class MoontouchedAmulet(Spell):
	Class, school, name = "Druid", "", "Moontouched Amulet"
	numTargets, mana, Effects = 0, 3, ""
	description = "Give your hero +4 Attack this turn. Corrupt: And gain 6 Armor"
	name_CN = "月触项链"
	trigHand, corruptedType = Trig_Corrupt, MoontouchedAmulet_Corrupt
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveHeroAttackArmor(self.ID, attGain=4, source=MoontouchedAmulet)
		
	
class KiriChosenofElune(Minion):
	Class, race, name = "Druid", "", "Kiri, Chosen of Elune"
	mana, attack, health = 4, 2, 2
	name_CN = "基利，艾露恩之眷"
	numTargets, Effects, description = 0, "", "Battlecry: Add a Solar Eclipse and Lunar Eclipse to your hand"
	index = "Battlecry~Legendary"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.addCardtoHand([SolarEclipse, LunarEclipse], self.ID)
		
	
class Greybough(Minion):
	Class, race, name = "Druid", "", "Greybough"
	mana, attack, health = 5, 4, 6
	name_CN = "格雷布"
	numTargets, Effects, description = 0, "Taunt", "Taunt. Deathrattle: Give a random friendly minion 'Deathrattle: Summon Greybough'"
	index = "Legendary"
	deathrattle = Death_Greybough
	
	
class UmbralOwl(Minion):
	Class, race, name = "Druid", "Beast", "Umbral Owl"
	mana, attack, health = 7, 4, 4
	numTargets, Effects, description = 0, "Rush", "Rush. Costs (1) less for each spell you've cast this game"
	name_CN = "幽影猫头鹰"
	trigHand = Trig_UmbralOwl		
	def selfManaChange(self):
		self.mana -= self.Game.Counters.examCardPlays(self.ID, veri_sum_ls=1, cond=lambda tup: tup[0].category == "Spell")
		
	
class CenarionWard(Spell):
	Class, school, name = "Druid", "Nature", "Cenarion Ward"
	numTargets, mana, Effects = 0, 8, ""
	description = "Gain 8 Armor. Summon a random 8-Cost minion"
	name_CN = "塞纳里奥结界"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveHeroAttackArmor(self.ID, armor=8)
		self.summon(numpyChoice(self.rngPool("8-Cost Minions to Summon"))(self.Game, self.ID))
		
	
class FizzyElemental(Minion):
	Class, race, name = "Druid", "Elemental", "Fizzy Elemental"
	mana, attack, health = 9, 10, 10
	numTargets, Effects, description = 0, "Rush,Taunt", "Rush, Taunt"
	name_CN = "泡沫元素"
	
	
class MysteryWinner(Minion):
	Class, race, name = "Hunter", "", "Mystery Winner"
	mana, attack, health = 1, 1, 1
	name_CN = "神秘获奖者"
	numTargets, Effects, description = 0, "", "Battlecry: Discover a Secret"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.discoverNew(comment, lambda : secrets2Discover(self))
		
	
class DancingCobra_Corrupt(Minion):
	Class, race, name = "Hunter", "Beast", "Dancing Cobra"
	mana, attack, health = 2, 1, 5
	name_CN = "舞动的眼镜蛇"
	numTargets, Effects, description = 0, "Poisonous", "Poisonous"
	index = "Uncollectible"
	
	
class DancingCobra(Minion):
	Class, race, name = "Hunter", "Beast", "Dancing Cobra"
	mana, attack, health = 2, 1, 5
	numTargets, Effects, description = 0, "", "Corrupt: Gain Poisonous"
	name_CN = "舞动的眼镜蛇"
	trigHand, corruptedType = Trig_Corrupt, DancingCobra_Corrupt
	
	
class DontFeedtheAnimals_Corrupt(Spell):
	Class, school, name = "Hunter", "", "Don't Feed the Animals"
	numTargets, mana, Effects = 0, 2, ""
	name_CN = "请勿投食"
	description = "Corrupted. Give all Beasts in your hand +2/+2"
	index = "Uncollectible"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant([card for card in self.Game.Hand_Deck.hands[self.ID] if "Beast" in card.race], 2, 2,
						 source=DontFeedtheAnimals_Corrupt, add2EventinGUI=False)
		
	
class DontFeedtheAnimals(Spell):
	Class, school, name = "Hunter", "", "Don't Feed the Animals"
	numTargets, mana, Effects = 0, 2, ""
	description = "Give all Beasts in your hand +1/+1. Corrupt: Give them +2/+2 instead"
	name_CN = "请勿投食"
	trigHand, corruptedType = Trig_Corrupt, DontFeedtheAnimals_Corrupt
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant([card for card in self.Game.Hand_Deck.hands[self.ID] if "Beast" in card.race], 1, 1,
						 source=DontFeedtheAnimals, add2EventinGUI=False)
		
	
class OpentheCages(Secret):
	Class, school, name = "Hunter", "", "Open the Cages"
	numTargets, mana, Effects = 0, 2, ""
	description = "Secret: When your turn starts, if you control two minions, summon an Animal Companion"
	name_CN = "打开兽笼"
	trigBoard = Trig_OpentheCages		
	num = 1
	
	
class PettingZoo(Spell):
	Class, school, name = "Hunter", "", "Petting Zoo"
	numTargets, mana, Effects = 0, 3, ""
	description = "Summon a 3/3 Strider. Repeat for each Secret you control"
	name_CN = "宠物乐园"
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def effCanTrig(self):
		self.effectViable = self.Game.Secrets.secrets[self.ID]
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon(DarkmoonStrider(self.Game, self.ID))
		for i in range(len(self.Game.Secrets.secrets[self.ID])):
			self.summon(DarkmoonStrider(self.Game, self.ID))
		
	
class DarkmoonStrider(Minion):
	Class, race, name = "Hunter", "Beast", "Darkmoon Strider"
	mana, attack, health = 3, 3, 3
	name_CN = "暗月陆行鸟"
	numTargets, Effects, description = 0, "", ""
	index = "Uncollectible"
	
	
class RinlingsRifle(Weapon):
	Class, name, description = "Hunter", "Rinling's Rifle", "After your hero attacks, Discover a Secret and cast it"
	mana, attack, durability, Effects = 4, 2, 2, ""
	name_CN = "瑞林的步枪"
	index = "Legendary"
	trigBoard = Trig_RinlingsRifle
	
	
class TramplingRhino(Minion):
	Class, race, name = "Hunter", "Beast", "Trampling Rhino"
	mana, attack, health = 5, 5, 5
	numTargets, Effects, description = 0, "Rush", "Rush. Afte this attacks and kills a minion, excess damage hits the enemy hero"
	name_CN = "狂踏的犀牛"
	trigBoard = Trig_TramplingRhino		
	
	
class MaximaBlastenheimer(Minion):
	Class, race, name = "Hunter", "", "Maxima Blastenheimer"
	mana, attack, health = 6, 4, 4
	name_CN = "玛克希玛·雷管"
	numTargets, Effects, description = 0, "", "Battlecry: Summon a random minion from your deck. It attacks the enemy hero, then dies"
	index = "Battlecry~Legendary"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		#Even minions with "Can't attack heroes" still attack hero under her command
		if minion := self.try_SummonfromOwn(self.pos + 1):
			if minion.canBattle and (hero := self.Game.heroes[3-self.ID]).canBattle():
				self.Game.battle(minion, hero)
			if minion.onBoard: self.Game.kill(self, minion)
		
	
class DarkmoonTonk(Minion):
	Class, race, name = "Hunter", "Mech", "Darkmoon Tonk"
	mana, attack, health = 7, 8, 5
	numTargets, Effects, description = 0, "", "Deathrattle: Fire four missiles at random enemies that deal 2 damage each"
	name_CN = "暗月坦克"
	deathrattle = Death_DarkmoonTonk
	
	
class JewelofNZoth(Spell):
	Class, school, name = "Hunter", "", "Jewel of N'Zoth"
	numTargets, mana, Effects = 0, 8, ""
	description = "Summon three friendly Deathrattle minions that died this game"
	name_CN = "恩佐斯宝石"
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def text(self): return self.Game.Counters.examDeads(self.ID, veri_sum_ls=1, cond=lambda card: card.deathrattle)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if tups := self.Game.Counters.examDeads(self.ID, veri_sum_ls=2, cond=lambda card: card.deathrattle):
			tups = numpyChoice(tups, min(3, len(tups)), replace=False)
			self.summon([self.Game.fabCard(tup, self.ID, self) for tup in tups])
		
	
class ConfectionCyclone(Minion):
	Class, race, name = "Mage", "Elemental", "Confection Cyclone"
	mana, attack, health = 2, 3, 2
	name_CN = "甜点飓风"
	numTargets, Effects, description = 0, "", "Battlecry: Add two 1/2 Sugar Elementals to your hand"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.addCardtoHand([SugarElemental] * 2, self.ID)
		
	
class SugarElemental(Minion):
	Class, race, name = "Mage", "Elemental", "Sugar Elemental"
	mana, attack, health = 1, 1, 2
	name_CN = "甜蜜元素"
	numTargets, Effects, description = 0, "", ""
	index = "Uncollectible"
	
	
class DeckofLunacy(Spell):
	Class, school, name = "Mage", "", "Deck of Lunacy"
	numTargets, mana, Effects = 0, 4, ""
	name_CN = "愚人套牌"
	description = "Transform spells in your deck into ones that cost (3) more. (They keep their original Cost.)"
	index = "Legendary"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		curGame, ID = self.Game, self.ID
		indices, newCards, costs = [], [], []
		for i, card in enumerate(curGame.Hand_Deck.decks[ID]):
			if card.category == "Spell":
				indices.append(i)
				newCards.append(numpyChoice(self.rngPool("%d-Cost Spells"%min(10, card.mana+3))))
				costs.append(card.mana)
		if indices:
			newCards, typeSelf = [card(curGame, ID) for card in newCards], type(self)
			for card, cost in zip(newCards, costs): card.manaMods.append(ManaMod(card, to=cost))
			curGame.Hand_Deck.replaceCardsinDeck(ID, indices, newCards, creator=typeSelf)
		
	
class GameMaster(Minion):
	Class, race, name = "Mage", "", "Game Master"
	mana, attack, health = 2, 2, 3
	numTargets, Effects, description = 0, "", "The first Secret you play each turn costs (1)"
	name_CN = "游戏管理员"
	aura, trigEffect = ManaAura_GameMaster, GameManaAura_GameMaster
	
	
class RiggedFaireGame(Secret):
	Class, school, name = "Mage", "", "Rigged Faire Game"
	numTargets, mana, Effects = 0, 3, ""
	description = "Secret: If you didn't take any damage during your opponent's turn, draw 3 cards"
	name_CN = "非公平游戏"
	trigBoard = Trig_RiggedFaireGame		
	
	
class OccultConjurer(Minion):
	Class, race, name = "Mage", "", "Occult Conjurer"
	mana, attack, health = 4, 4, 4
	name_CN = "隐秘咒术师"
	numTargets, Effects, description = 0, "", "Battlecry: If you control a Secret, summon a copy of this"
	index = "Battlecry"
	def effCanTrig(self):
		self.effectViable = self.Game.Secrets.secrets[self.ID]
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if not self.dead and self.Game.Secrets.secrets[self.ID]: self.summon(self.copyCard(self, self.ID))
		
	
class RingToss_Corrupt(Spell):
	Class, school, name = "Mage", "", "Ring Toss"
	numTargets, mana, Effects = 0, 4, ""
	name_CN = "套圈圈"
	description = "Corrupted. Discover 2 Secrets and cast them"
	index = "Uncollectible"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for _ in range(2):
			secret, _ = self.discoverNew(comment, lambda: secrets2Discover(self, toPutonBoard=True), add2Hand=False)
			secret.creator = type(self)
			secret.playedEffect()
		
	
class RingToss(Spell):
	Class, school, name = "Mage", "", "Ring Toss"
	numTargets, mana, Effects = 0, 4, ""
	description = "Discover a Secret and cast it. Corrupt: Discover 2 instead"
	name_CN = "套圈圈"
	trigHand, corruptedType = Trig_Corrupt, RingToss_Corrupt
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		secret, _ = self.discoverNew(comment, lambda: secrets2Discover(self, toPutonBoard=True), add2Hand=False)
		secret.creator = type(self)
		secret.playedEffect()
		
	
class FireworkElemental_Corrupt(Minion):
	Class, race, name = "Mage", "Elemental", "Firework Elemental"
	mana, attack, health = 5, 3, 5
	name_CN = "焰火元素"
	numTargets, Effects, description = 1, "", "Corrupted. Battlecry: Deal 12 damage to a minion"
	index = "Battlecry~Uncollectible"
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(target, 12)
		
	
class FireworkElemental(Minion):
	Class, race, name = "Mage", "Elemental", "Firework Elemental"
	mana, attack, health = 5, 3, 5
	name_CN = "焰火元素"
	numTargets, Effects, description = 1, "", "Battlecry: Deal 3 damage to a minion. Corrupt: Deal 12 damage instead"
	index = "Battlecry~ToCorrupt"
	trigHand, corruptedType = Trig_Corrupt, FireworkElemental_Corrupt
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(target, 3)
		
	
class SaygeSeerofDarkmoon(Minion):
	Class, race, name = "Mage", "", "Sayge, Seer of Darkmoon"
	mana, attack, health = 6, 5, 5
	name_CN = "暗月先知赛格"
	numTargets, Effects, description = 0, "", "Battlecry: Draw 1 card(Upgraded for each friendly Secret that has triggered this game!)"
	index = "Battlecry~Legendary"
	def text(self): return 1 + sum(tup[1] == "Secret" and tup[2] == self.ID for tup in self.Game.Counters.iter_TupsSoFar("trigs"))
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for _ in range(1 + sum(tup[1] == "Secret" and tup[2] == self.ID for tup in self.Game.Counters.iter_TupsSoFar("trigs"))):
			self.Game.Hand_Deck.drawCard(self.ID)
		
	
class MaskofCThun(Spell):
	Class, school, name = "Mage", "Shadow", "Mask of C'Thun"
	numTargets, mana, Effects = 0, 7, ""
	description = "Deal 10 damage randomly split among all enemies"
	name_CN = "克苏恩面具"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		side, game = 3-self.ID, self.Game
		for _ in range(self.calcDamage(10)):
			if objs := game.charsAlive(side): self.dealsDamage(numpyChoice(objs), 1)
			else: break
		
	
class GrandFinale(Spell):
	Class, school, name = "Mage", "Fire", "Grand Finale"
	numTargets, mana, Effects = 0, 8, ""
	description = "Summon an 8/8 Elemental. Repeat for each Elemental you played last turn"
	name_CN = "华丽谢幕"
	def effCanTrig(self):
		self.effectViable = 1 + self.Game.Counters.examElementalsLastTurn(self.ID, veri_sum=1)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		game = self.Game
		self.summon(ExplodingSparkler(game, self.ID))
		for _ in range(game.Counters.examElementalsLastTurn(self.ID, veri_sum=1)):
			self.summon(ExplodingSparkler(game, self.ID))
		
	
class ExplodingSparkler(Minion):
	Class, race, name = "Mage", "Elemental", "Exploding Sparkler"
	mana, attack, health = 8, 8, 8
	name_CN = "爆破烟火"
	numTargets, Effects, description = 0, "", ""
	index = "Uncollectible"
	
	
class OhMyYogg(Secret):
	Class, school, name = "Paladin", "Shadow", "Oh My Yogg!"
	numTargets, mana, Effects = 0, 1, ""
	description = "Secret: When your opponent casts a spell, they instead cast a random one of the same Cost"
	name_CN = "古神在上"
	trigBoard = Trig_OhMyYogg
	
	
class RedscaleDragontamer(Minion):
	Class, race, name = "Paladin", "Murloc", "Redscale Dragontamer"
	mana, attack, health = 2, 2, 3
	numTargets, Effects, description = 0, "", "Deathrattle: Draw a Dragon"
	name_CN = "赤鳞驯龙者"
	deathrattle = Death_RedscaleDragontamer
	
	
class SnackRun(Spell):
	Class, school, name = "Paladin", "", "Snack Run"
	numTargets, mana, Effects = 0, 2, ""
	description = "Discover a spell. Restore Health to your hero equal to its Cost"
	name_CN = "零食大冲关"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		card, _ = self.discoverNew(comment, lambda : self.rngPool(class4Discover(self) + " Spells"))
		self.heals(self.Game.heroes[self.ID], type(card).mana)
		
	
class CarnivalBarker(Minion):
	Class, race, name = "Paladin", "", "Carnival Barker"
	mana, attack, health = 3, 3, 2
	numTargets, Effects, description = 0, "", "Whenever you summon a 1-Health minion, give +1/+2"
	name_CN = "狂欢报幕员"
	trigBoard = Trig_CarnivalBarker		
	
	
class DayattheFaire_Corrupt(Spell):
	Class, school, name = "Paladin", "", "Day at the Faire"
	numTargets, mana, Effects = 0, 3, ""
	name_CN = "游园日"
	description = "Corrupted: Summon 5 Silver Hand Recruits"
	index = "Uncollectible"
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon([SilverHandRecruit(self.Game, self.ID)  for _ in (0, 1, 2, 3, 4)])
		
	
class DayattheFaire(Spell):
	Class, school, name = "Paladin", "", "Day at the Faire"
	numTargets, mana, Effects = 0, 3, ""
	description = "Summon 3 Silver Hand Recruits. Corrupt: Summon 5"
	name_CN = "游园日"
	trigHand, corruptedType = Trig_Corrupt, DayattheFaire_Corrupt
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon([SilverHandRecruit(self.Game, self.ID) for _ in (0, 1, 2)])
		
	
class BalloonMerchant(Minion):
	Class, race, name = "Paladin", "", "Balloon Merchant"
	mana, attack, health = 4, 3, 5
	name_CN = "气球商人"
	numTargets, Effects, description = 0, "", "Battlecry: Give your Silver Hand Recruits +1 Attack and Divine Shield"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant([minion for minion in self.Game.minionsonBoard(self.ID) if minion.name == "Silver Hand Recruit"],
						1, 0, effGain="Divine Shield", source=BalloonMerchant)
		
	
class CarouselGryphon_Corrupt(Minion):
	Class, race, name = "Paladin", "Mech", "Carousel Gryphon"
	mana, attack, health = 5, 8, 8
	name_CN = "旋转木马"
	numTargets, Effects, description = 0, "Divine Shield,Taunt", "Divine Shield, Taunt"
	index = "Uncollectible"
	
	
class CarouselGryphon(Minion):
	Class, race, name = "Paladin", "Mech", "Carousel Gryphon"
	mana, attack, health = 5, 5, 5
	numTargets, Effects, description = 0, "Divine Shield", "Divine Shield. Corrupt: Gain +3/+3 and Taunt"
	name_CN = "旋转木马"
	trigHand, corruptedType = Trig_Corrupt, CarouselGryphon_Corrupt
	
	
class LothraxiontheRedeemed(Minion):
	Class, race, name = "Paladin", "Demon", "Lothraxion the Redeemed"
	mana, attack, health = 5, 5, 5
	name_CN = "救赎者洛萨克森"
	numTargets, Effects, description = 0, "", "Battlecry: For the rest of the game, after you summon a Silver Hand Recruit, give it Divine Shield"
	index = "Battlecry~Legendary"
	trigEffect = LothraxiontheRedeemed_Effect
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		LothraxiontheRedeemed_Effect(self.Game, self.ID).connect()
		
	
class HammeroftheNaaru(Weapon):
	Class, name, description = "Paladin", "Hammer of the Naaru", "Battlecry: Summon a 6/6 Holy Elemental with Taunt"
	mana, attack, durability, Effects = 6, 3, 3, ""
	name_CN = "纳鲁之锤"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon(HolyElemental(self.Game, self.ID))
		
	
class HolyElemental(Minion):
	Class, race, name = "Paladin", "Elemental", "Holy Elemental"
	mana, attack, health = 6, 6, 6
	name_CN = "神圣元素"
	numTargets, Effects, description = 0, "Taunt", "Taunt"
	index = "Uncollectible"
	
	
class HighExarchYrel(Minion):
	Class, race, name = "Paladin", "", "High Exarch Yrel"
	mana, attack, health = 8, 7, 5
	name_CN = "大主教伊瑞尔"
	numTargets, Effects, description = 0, "", "Battlecry: If your deck has no Neutral cards, gain Rush, Lifesteal, Taunt, and Divine Shield"
	index = "Battlecry~Legendary"
	def effCanTrig(self):
		self.effectViable = all(card.Class != "Neutral" for card in self.Game.Hand_Deck.decks[self.ID])
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if all(card.Class != "Neutral" for card in self.Game.Hand_Deck.decks[self.ID]):
			self.giveEnchant(self, multipleEffGains=(("Rush", 1, None), ("Lifesteal", 1, None), ("Taunt", 1, None), ("Divine Shield", 1, None)),
							 source=HighExarchYrel)
		
	
class Insight_Corrupt(Spell):
	Class, school, name = "Priest", "Shadow", "Insight"
	numTargets, mana, Effects = 0, 2, ""
	name_CN = "洞察"
	description = "Corrupted. Draw a minion. Reduce its Cost by (2)"
	index = "Uncollectible"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		minion, mana, entersHand = self.drawCertainCard(lambda card: card.category == "Minion")
		if entersHand: ManaMod(minion, by=-2).applies()
		
	
class Insight(Spell):
	Class, school, name = "Priest", "Shadow", "Insight"
	numTargets, mana, Effects = 0, 2, ""
	description = "Draw a minion. Corrupt: Reduce its Cost by (2)"
	name_CN = "洞察"
	trigHand, corruptedType = Trig_Corrupt, Insight_Corrupt
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.drawCertainCard(lambda card: card.category == "Minion")
		
	
class FairgroundFool_Corrupt(Minion):
	Class, race, name = "Priest", "", "Fairground Fool"
	mana, attack, health = 3, 4, 7
	name_CN = "游乐园小丑"
	numTargets, Effects, description = 0, "Taunt", "Corrupted. Taunt"
	index = "Uncollectible"
	
	
class FairgroundFool(Minion):
	Class, race, name = "Priest", "", "Fairground Fool"
	mana, attack, health = 3, 4, 3
	numTargets, Effects, description = 0, "Taunt", "Taunt. Corrupt: Gain +4 Health"
	name_CN = "游乐园小丑"
	trigHand, corruptedType = Trig_Corrupt, FairgroundFool_Corrupt
	
	
class NazmaniBloodweaver(Minion):
	Class, race, name = "Priest", "", "Nazmani Bloodweaver"
	mana, attack, health = 3, 2, 5
	numTargets, Effects, description = 0, "", "After you cast a spell, reduce the Cost of a random card in your hand by (1)"
	name_CN = "纳兹曼尼织血者"
	trigBoard = Trig_NazmaniBloodweaver		
	
	
class PalmReading(Spell):
	Class, school, name = "Priest", "Shadow", "Palm Reading"
	numTargets, mana, Effects = 0, 3, ""
	description = "Discover a spell. Reduce the Cost of spells in your hand by (1)"
	name_CN = "解读手相"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.discoverNew(comment, lambda : self.rngPool(class4Discover(self)+" Spells"))
		for card in self.Game.Hand_Deck.hands[self.ID]:
			if card.category == "Spell": ManaMod(card, by=-1).applies()
		
	
class AuspiciousSpirits_Corrupt(Spell):
	Class, school, name = "Priest", "Shadow", "Auspicious Spirits"
	numTargets, mana, Effects = 0, 4, ""
	name_CN = "吉兆"
	description = "Corrupted. Summon a 7-Cost minion"
	index = "Uncollectible"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon(numpyChoice(self.rngPool("7-Cost Minions to Summon"))(self.Game, self.ID))
		
	
class AuspiciousSpirits(Spell):
	Class, school, name = "Priest", "Shadow", "Auspicious Spirits"
	numTargets, mana, Effects = 0, 4, ""
	description = "Summon a random 4-Cost minion. Corrupt: Summon a 7-Cost minion instead"
	name_CN = "吉兆"
	trigHand, corruptedType = Trig_Corrupt, AuspiciousSpirits_Corrupt
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon(numpyChoice(self.rngPool("4-Cost Minions to Summon"))(self.Game, self.ID))
		
	
class TheNamelessOne(Minion):
	Class, race, name = "Priest", "", "The Nameless One"
	mana, attack, health = 4, 4, 4
	name_CN = "无名者"
	numTargets, Effects, description = 1, "", "Battlecry: Choose a minion. Become a 4/4 copy of it, then Silence it"
	index = "Battlecry~Legendary"
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj is not self and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if not self.dead and self.Game.cardinPlay is self: #战吼触发时自己不能死亡。
			self.transform(self, self.copyCard(target[0], self.ID, 4, 4))
		target[0].getsSilenced()
		
	
class FortuneTeller(Minion):
	Class, race, name = "Priest", "Mech", "Fortune Teller"
	mana, attack, health = 5, 3, 3
	name_CN = "占卜机"
	numTargets, Effects, description = 0, "Taunt", "Taunt. Battlecry: Gain +1/+1 for each spell in your hand"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.onBoard or self.inHand: #For now, no battlecry resolution shuffles this into deck.
			num = sum(card.category == "Spell" for card in self.Game.Hand_Deck.hands[self.ID])
			self.giveEnchant(self, num, num, source=FortuneTeller)
		
	
class IdolofYShaarj(Spell):
	Class, school, name = "Priest", "Shadow", "Idol of Y'Shaarj"
	numTargets, mana, Effects = 0, 8, ""
	description = "Summon a 10/10 copy of a minion in your deck"
	name_CN = "亚煞极神像"
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if minions := [card for card in self.Game.Hand_Deck.decks[self.ID] if card.category == "Minion"]:
			self.summon(self.copyCard(numpyChoice(minions), self.ID, 10, 10))
		
	
class GhuuntheBloodGod(Minion):
	Class, race, name = "Priest", "", "G'huun the Blood God"
	mana, attack, health = 8, 8, 8
	name_CN = "戈霍恩，鲜血之神"
	numTargets, Effects, description = 0, "", "Draw 2 cards. They cost Health instead of Mana"
	index = "Battlecry~Legendary"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for _ in (0, 1):
			card, mana, entersHand = self.Game.Hand_Deck.drawCard(self.ID)
			if entersHand: self.giveEnchant(card, effGain="Cost Health Instead", source=GhuuntheBloodGod)
		
	
class BloodofGhuun(Minion):
	Class, race, name = "Priest", "Elemental", "Blood of G'huun"
	mana, attack, health = 9, 8, 8
	numTargets, Effects, description = 0, "Taunt", "Taunt. At the end of your turn, summon a 5/5 copy of a minion in your deck"
	name_CN = "戈霍恩之血"
	trigBoard = Trig_BloodofGhuun
	
	
class PrizePlunderer(Minion):
	Class, race, name = "Rogue", "Pirate", "Prize Plunderer"
	mana, attack, health = 1, 2, 1
	name_CN = "奖品掠夺者"
	numTargets, Effects, description = 1, "", "Combo: Deal 1 damage to a minion for each other card you've played this turn"
	index = "Combo"
	def numTargetsNeeded(self, choice=0):
		return 1 if self.Game.Counters.comboCounters[self.ID] > 0 else 0
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj is not self and obj.onBoard
		
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.comboCounters[self.ID] > 0
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if dmg := self.Game.Counters.comboCounters[self.ID]:
			self.dealsDamage(target, dmg)
		
	
class FoxyFraud(Minion):
	Class, race, name = "Rogue", "", "Foxy Fraud"
	mana, attack, health = 2, 3, 2
	name_CN = "狐人老千"
	numTargets, Effects, description = 0, "", "Battlecry: Your next Combo this turn costs (2) less"
	index = "Battlecry"
	trigEffect = GameManaAura_FoxyFraud
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		GameManaAura_FoxyFraud(self.Game, self.ID).auraAppears()
		
	
class ShadowClone(Secret):
	Class, school, name = "Rogue", "Shadow", "Shadow Clone"
	numTargets, mana, Effects = 0, 2, ""
	description = "Secret: After a minion attacks your hero, summon a copy of it with Stealth"
	name_CN = "暗影克隆"
	trigBoard = Trig_ShadowClone		
	
	
class SweetTooth_Corrupt(Minion):
	Class, race, name = "Rogue", "", "Sweet Tooth"
	mana, attack, health = 2, 5, 2
	name_CN = "甜食狂"
	numTargets, Effects, description = 0, "Stealth", "Corrupted. Stealth"
	index = "Uncollectible"
	
	
class SweetTooth(Minion):
	Class, race, name = "Rogue", "", "Sweet Tooth"
	mana, attack, health = 2, 3, 2
	numTargets, Effects, description = 0, "", "Corrupt: Gain +2 Attack and Stealth"
	name_CN = "甜食狂"
	trigHand, corruptedType = Trig_Corrupt, SweetTooth_Corrupt
	
	
class Swindle(Spell):
	Class, school, name = "Rogue", "", "Swindle"
	numTargets, mana, Effects = 0, 2, ""
	name_CN = "行骗"
	description = "Draw a spell. Combo: And a minion"
	index = "Combo"
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.comboCounters[self.ID] > 0
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.drawCertainCard(lambda card: card.category == "Spell")
		if self.Game.Counters.comboCounters[self.ID] > 0:
			self.drawCertainCard(lambda card: card.category == "Minion")
		
	
class TenwuoftheRedSmoke(Minion):
	Class, race, name = "Rogue", "", "Tenwu of the Red Smoke"
	mana, attack, health = 2, 3, 2
	name_CN = "'赤烟'腾武"
	numTargets, Effects, description = 1, "", "Battlecry: Return a friendly minion to you hand. It costs (1) this turn"
	index = "Battlecry~Legendary"
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists(self.ID)
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.ID == self.ID and obj is not self and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for obj in target: self.Game.returnObj2Hand(self, obj, manaMod=ManaMod(obj, to=1, until=0))
		
	
class CloakofShadows(Spell):
	Class, school, name = "Rogue", "Shadow", "Cloak of Shadows"
	numTargets, mana, Effects = 0, 3, ""
	description = "Give your hero Stealth for 1 turn"
	name_CN = "暗影斗篷"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(self.Game.heroes[self.ID], effGain="Temp Stealth", source=CloakofShadows)
		
	
class TicketMaster(Minion):
	Class, race, name = "Rogue", "", "Ticket Master"
	mana, attack, health = 3, 4, 3
	numTargets, Effects, description = 0, "", "Deathrattle: Shuffle 3 Tickets into your deck. When drawn, summon a 3/3 Plush Bear"
	name_CN = "奖券老板"
	deathrattle = Death_TicketMaster
	
	
class Tickets(Spell):
	Class, school, name = "Rogue", "", "Tickets"
	numTargets, mana, Effects = 0, 3, ""
	name_CN = "奖券"
	description = "Casts When Drawn. Summon a 3/3 Plush Bear"
	index = "Uncollectible"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon(PlushBear(self.Game, self.ID))
		
	
class PlushBear(Minion):
	Class, race, name = "Rogue", "", "Plush Bear"
	mana, attack, health = 3, 3, 3
	name_CN = "玩具熊"
	numTargets, Effects, description = 0, "", ""
	index = "Uncollectible"
	
	
class MalevolentStrike(Spell):
	Class, school, name = "Rogue", "", "Malevolent Strike"
	numTargets, mana, Effects = 1, 5, ""
	description = "Destroy a minion. Costs (1) less for each card in your deck that didn't start there"
	name_CN = "致伤打击"
	trigHand = Trig_MalevolentStrike
	def selfManaChange(self):
		self.mana -= sum(card.creator is not None for card in self.Game.Hand_Deck.decks[self.ID])
		
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.Game.kill(self, target)
		
	
class GrandEmpressShekzara(Minion):
	Class, race, name = "Rogue", "", "Grand Empress Shek'zara"
	mana, attack, health = 6, 5, 7
	name_CN = "大女皇夏柯扎拉"
	numTargets, Effects, description = 0, "", "Battlecry: Discover a card in your deck and draw all copies of it"
	index = "Battlecry~Legendary"
	def drawCopiesofType(self, name):
		#经测试，检索过程中只看名字是否相同。
		HD, ID = self.Game.Hand_Deck, self.ID
		while (i := next((i for i, card in enumerate(HD.decks[ID]) if card.name == name), -1)) > -1:
			HD.drawCard(ID, i)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		card, i = self.discoverfrom(comment)
		if i > -1: GrandEmpressShekzara.drawCopiesofType(self, card.name)
		
	
class Revolve(Spell):
	Class, school, name = "Shaman", "", "Revolve"
	numTargets, mana, Effects = 0, 1, ""
	description = "Transform all minions into random ones with the same Cost"
	name_CN = "异变轮转"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		game = self.Game
		if minions := game.minionsonBoard():
			self.transform(minions, [numpyChoice(self.rngPool("%d-Cost Minions to Summon"%obj.mana))(game, obj.ID) for obj in minions])
		
	
class CagematchCustodian(Minion):
	Class, race, name = "Shaman", "Elemental", "Cagematch Custodian"
	mana, attack, health = 2, 2, 2
	name_CN = "笼斗管理员"
	numTargets, Effects, description = 0, "", "Battlecry: Draw a weapon"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.drawCertainCard(lambda card: card.category == "Weapon")
		
	
class DeathmatchPavilion(Spell):
	Class, school, name = "Shaman", "", "Deathmatch Pavilion"
	numTargets, mana, Effects = 0, 2, ""
	description = "Summon a 3/2 Duelist. If your hero attacked this turn, summon another"
	name_CN = "死斗场帐篷"
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.examHeroAtks(self.ID, turnInd=self.Game.turnInd)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon(PavilionDuelist(self.Game, self.ID))
		if self.Game.Counters.examHeroAtks(self.ID, turnInd=self.Game.turnInd):
			self.summon(PavilionDuelist(self.Game, self.ID))
		
	
class PavilionDuelist(Minion):
	Class, race, name = "Shaman", "", "Pavilion Duelist"
	mana, attack, health = 2, 3, 2
	name_CN = "大帐决斗者"
	numTargets, Effects, description = 0, "", ""
	index = "Uncollectible"
	
	
class GrandTotemEysor(Minion):
	Class, race, name = "Shaman", "Totem", "Grand Totem Eys'or"
	mana, attack, health = 3, 0, 4
	name_CN = "巨型图腾埃索尔"
	numTargets, Effects, description = 0, "", "At the end of your turn, give +1/+1 to all other Totems in your hand, deck and battlefield"
	index = "Legendary"
	trigBoard = Trig_GrandTotemEysor		
	
	
class Magicfin(Minion):
	Class, race, name = "Shaman", "Murloc", "Magicfin"
	mana, attack, health = 3, 3, 4
	numTargets, Effects, description = 0, "", "After a friendly Murloc dies, add a random Legendary minion to your hand"
	name_CN = "鱼人魔术师"
	trigBoard = Trig_Magicfin		
	poolIdentifier = "Legendary Minions"
	@classmethod
	def generatePool(cls, pools):
		return "Legendary Minions", pools.LegendaryMinions
		
	
class PitMaster_Corrupt(Minion):
	Class, race, name = "Shaman", "", "Pit Master"
	mana, attack, health = 3, 1, 2
	name_CN = "死斗场管理者"
	numTargets, Effects, description = 0, "", "Corrupted. Battlecry: Summon two 3/2 Duelists"
	index = "Battlecry~Uncollectible"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon([PavilionDuelist(self.Game, self.ID) for _ in (0, 1)], relative="<>")
		
	
class PitMaster(Minion):
	Class, race, name = "Shaman", "", "Pit Master"
	mana, attack, health = 3, 1, 2
	name_CN = "死斗场管理者"
	numTargets, Effects, description = 0, "", "Battlecry: Summon a 3/2 Duelist. Corrupt: Summon two"
	index = "Battlecry~ToCorrupt"
	trigHand, corruptedType = Trig_Corrupt, PitMaster_Corrupt
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon(PavilionDuelist(self.Game, self.ID))
		
	
class Stormstrike(Spell):
	Class, school, name = "Shaman", "Nature", "Stormstrike"
	numTargets, mana, Effects = 1, 3, ""
	description = "Deal 3 damage to a minion. Give your hero +3 Attack this turn"
	name_CN = "风暴打击"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(target, self.calcDamage(3))
		self.giveHeroAttackArmor(self.ID, attGain=3, source=Stormstrike)
		
	
class WhackAGnollHammer(Weapon):
	Class, name, description = "Shaman", "Whack-A-Gnoll Hammer", "After your hero attacks, give a random friendly minion +1/+1"
	mana, attack, durability, Effects = 3, 3, 2, ""
	name_CN = "敲狼锤"
	trigBoard = Trig_WhackAGnollHammer
	
	
class DunkTank_Corrupt(Spell):
	Class, school, name = "Shaman", "Nature", "Dunk Tank"
	numTargets, mana, Effects = 1, 4, ""
	name_CN = "深水炸弹"
	description = "Corrupted. Deal 4 damage. Then deal 2 damage to all enemy minions"
	index = "Uncollectible"
	def text(self): return "%d, %d"%(self.calcDamage(4), self.calcDamage(2))
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(target, self.calcDamage(4))
		self.dealsDamage(self.Game.minionsonBoard(3-self.ID), self.calcDamage(2))
		
	
class DunkTank(Spell):
	Class, school, name = "Shaman", "Nature", "Dunk Tank"
	numTargets, mana, Effects = 1, 4, ""
	description = "Deal 4 damage. Corrupt: Then deal 2 damage to all enemy minions"
	name_CN = "深水炸弹"
	trigHand, corruptedType = Trig_Corrupt, DunkTank_Corrupt
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(target, self.calcDamage(4))
		
	
class InaraStormcrash(Minion):
	Class, race, name = "Shaman", "", "Inara Stormcrash"
	mana, attack, health = 5, 4, 5
	name_CN = "伊纳拉·碎雷"
	numTargets, Effects, description = 0, "", "On your turn, your hero has +2 Attack and Windfury"
	index = "Legendary"
	ara = Aura_InaraStormcrash
	
	
class WickedWhispers(Spell):
	Class, school, name = "Warlock", "Shadow", "Wicked Whispers"
	numTargets, mana, Effects = 0, 1, ""
	description = "Discard your lowest Cost card. Give your minions +1/+1"
	name_CN = "邪恶低语"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if indices := pickInds_LowestAttr(self.Game.Hand_Deck.hands[self.ID]):
			self.Game.Hand_Deck.discard(self.ID, numpyChoice(indices))
		self.giveEnchant(self.Game.minionsonBoard(self.ID), 1, 1, source=WickedWhispers)
		
	
class MidwayManiac(Minion):
	Class, race, name = "Warlock", "Demon", "Midway Maniac"
	mana, attack, health = 2, 1, 5
	numTargets, Effects, description = 0, "Taunt", "Taunt"
	name_CN = "癫狂的游客"
	
	
class FreeAdmission(Spell):
	Class, school, name = "Warlock", "", "Free Admission"
	numTargets, mana, Effects = 0, 3, ""
	description = "Draw 2 minions. If they're both Demons, reduce their Cost by (2)"
	name_CN = "免票入场"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		minion1, mana, entersHand1 = self.drawCertainCard(lambda card: card.category == "Minion")
		minion2, mana, entersHand2 = self.drawCertainCard(lambda card: card.category == "Minion")
		if entersHand1 and entersHand2 and "Demon" in minion1.race and "Demon" in minion2.race:
			ManaMod(minion1, by=-2).applies()
			ManaMod(minion2, by=-2).applies()
		
	
class ManariMosher(Minion):
	Class, race, name = "Warlock", "Demon", "Man'ari Mosher"
	mana, attack, health = 3, 3, 4
	name_CN = "摇滚堕落者"
	numTargets, Effects, description = 1, "", "Battlecry: Give a friendly Demon +3 Attack and Lifesteal this turn"
	index = "Battlecry"
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return "Demon" in obj.race and obj is not self and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(target, statEnchant=Enchantment(ManariMosher, 3, 0, until=0),
								 effectEnchant=Enchantment(ManariMosher, effGain="Lifesteal", until=0))
		
	
class CascadingDisaster_Corrupt2(Spell):
	Class, school, name = "Warlock", "", "Cascading Disaster"
	numTargets, mana, Effects = 0, 4, ""
	name_CN = "连环灾难"
	description = "Corrupted. Destroy 3 random enemy minions"
	index = "Uncollectible"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if minions := self.Game.minionsAlive(3-self.ID):
			for minion in numpyChoice(minions, min(3, len(minions)), replace=False):
				self.Game.kill(self, minion)
		
	
class CascadingDisaster_Corrupt(Spell):
	Class, school, name = "Warlock", "", "Cascading Disaster"
	numTargets, mana, Effects = 0, 4, ""
	name_CN = "连环灾难"
	description = "Corrupted. Destroy 2 random enemy minions. Corrupt: Destroy 3"
	index = "ToCorrupt~Uncollectible"
	trigHand, corruptedType = Trig_Corrupt, CascadingDisaster_Corrupt2
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if minions := self.Game.minionsAlive(3-self.ID):
			for minion in numpyChoice(minions, min(2, len(minions)), replace=False):
				self.Game.kill(self, minion)
		
	
class CascadingDisaster(Spell):
	Class, school, name = "Warlock", "", "Cascading Disaster"
	numTargets, mana, Effects = 0, 4, ""
	description = "Destroy a random enemy minion. Corrupt: Destroy 2. Corrupt Again: Destroy 3"
	name_CN = "连环灾难"
	trigHand, corruptedType = Trig_Corrupt, CascadingDisaster_Corrupt
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if minions:= self.Game.minionsAlive(3-self.ID): self.Game.kill(self, numpyChoice(minions))
		
	
class RevenantRascal(Minion):
	Class, race, name = "Warlock", "", "Revenant Rascal"
	mana, attack, health = 3, 3, 3
	name_CN = "怨灵捣蛋鬼"
	numTargets, Effects, description = 0, "", "Battlecry: Destroy a Mana Crystal for both players"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.Game.Manas.destroyManaCrystal(1, self.ID)
		self.Game.Manas.destroyManaCrystal(1, 3-self.ID)
		
	
class FireBreather(Minion):
	Class, race, name = "Warlock", "Demon", "Fire Breather"
	mana, attack, health = 4, 4, 3
	name_CN = "吐火艺人"
	numTargets, Effects, description = 0, "", "Battlecry: Deal 2 damage to all minions except Demons"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage([obj for obj in self.Game.minionsonBoard() if "Demon" not in obj.race], 2)
		
	
class DeckofChaos(Spell):
	Class, school, name = "Warlock", "Shadow", "Deck of Chaos"
	numTargets, mana, Effects = 0, 5, ""
	name_CN = "混乱套牌"
	description = "Swap the Cost and Attack of all minions in your deck"
	index = "Legendary"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if card.category == "Minion":
				for enchant in card.enchantments: enchant.handleStatMax(card)
				att, cost = max(0, card.attack), max(0, card.mana)
				card.manaMods.clear()
				card.getsStatSet_inDeck(cost, source=DeckofChaos)
				ManaMod(card, to=att).applies()
		
	
class RingMatron(Minion):
	Class, race, name = "Warlock", "Demon", "Ring Matron"
	mana, attack, health = 6, 6, 4
	numTargets, Effects, description = 0, "Taunt", "Taunt. Deathrattle: Summon two 3/2 Imps"
	name_CN = "火圈鬼母"
	deathrattle = Death_RingMatron
	
	
class FieryImp(Minion):
	Class, race, name = "Warlock", "Demon", "Fiery Imp"
	mana, attack, health = 2, 3, 2
	name_CN = "火焰小鬼"
	numTargets, Effects, description = 0, "", ""
	index = "Uncollectible"
	
	
class Tickatus_Corrupt(Minion):
	Class, race, name = "Warlock", "Demon", "Tickatus"
	mana, attack, health = 6, 8, 8
	name_CN = "提克特斯"
	numTargets, Effects, description = 0, "", "Corrupted. Battlecry: Remove the top 5 cards from your opponent's deck"
	index = "Battlecry~Legendary~Uncollectible"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.Game.Hand_Deck.removeDeckTopCard(3-self.ID, num=5)
		
	
class Tickatus(Minion):
	Class, race, name = "Warlock", "Demon", "Tickatus"
	mana, attack, health = 6, 8, 8
	name_CN = "提克特斯"
	numTargets, Effects, description = 0, "", "Battlecry: Remove the top 5 cards from your deck. Corrupt: Your opponent's instead"
	index = "Battlecry~ToCorrupt~Legendary"
	trigHand, corruptedType = Trig_Corrupt, Tickatus_Corrupt
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.Game.Hand_Deck.removeDeckTopCard(self.ID, num=5)
		
	
class StageDive_Corrupt(Spell):
	Class, school, name = "Warrior", "", "Stage Dive"
	numTargets, mana, Effects = 0, 1, ""
	name_CN = "舞台跳水"
	description = "Corrupted. Draw a Rush minion and give it +2/+1"
	index = "Uncollectible"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		minion, mana, entersHand = self.drawCertainCard(lambda card: card.category == "Minion" and card.effects["Rush"] > 0)
		if entersHand: self.giveEnchant(minion, 2, 1, source=StageDive_Corrupt, add2EventinGUI=False)
		
	
class StageDive(Spell):
	Class, school, name = "Warrior", "", "Stage Dive"
	numTargets, mana, Effects = 0, 1, ""
	description = "Draw a Rush minion. Corrupt: Give it +2/+1"
	name_CN = "舞台跳水"
	trigHand, corruptedType = Trig_Corrupt, StageDive_Corrupt
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.drawCertainCard(lambda card: card.category == "Minion" and card.effects["Rush"] > 0)
		
	
class BumperCar(Minion):
	Class, race, name = "Warrior", "Mech", "Bumper Car"
	mana, attack, health = 2, 1, 3
	numTargets, Effects, description = 0, "Rush", "Rush. Deathrattle: Add two 1/1 Riders with Rush to your hand"
	name_CN = "碰碰车"
	deathrattle = Death_BumperCar
	
	
class ETCGodofMetal(Minion):
	Class, race, name = "Warrior", "", "E.T.C., God of Metal"
	mana, attack, health = 2, 1, 4
	name_CN = "精英牛头人酋长，金属之神"
	numTargets, Effects, description = 0, "", "After a friendly Rush minion attack, deal 2 damage to the enemy hero"
	index = "Legendary"
	trigBoard = Trig_ETCGodofMetal		
	
	
class Minefield(Spell):
	Class, school, name = "Warrior", "", "Minefield"
	numTargets, mana, Effects = 0, 2, ""
	description = "Deal 5 damage randomly split among all minions"
	name_CN = "雷区挑战"
	def text(self): return self.calcDamage(5)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for _ in range(self.calcDamage(5)):
			if objs := self.Game.minionsAlive(): self.dealsDamage(numpyChoice(objs), 1)
			else: break
		
	
class RingmastersBaton(Weapon):
	Class, name, description = "Warrior", "Ringmaster's Baton", "After your hero attacks, give a Mech, Dragon, and Pirate in your hand +1/+1"
	mana, attack, durability, Effects = 2, 1, 3, ""
	name_CN = "马戏领班的节杖"
	trigBoard = Trig_RingmastersBaton		
	
	
class StageHand(Minion):
	Class, race, name = "Warrior", "Mech", "Stage Hand"
	mana, attack, health = 2, 3, 2
	name_CN = "置景工"
	numTargets, Effects, description = 0, "", "Battlecry: Give a random minion in your hand +1/+1"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if minions := [card for card in self.Game.Hand_Deck.hands[self.ID] if card.category == "Minion"]:
			self.giveEnchant(numpyChoice(minions), 1, 1, source=StageHand, add2EventinGUI=False)
		
	
class FeatofStrength(Spell):
	Class, school, name = "Warrior", "", "Feat of Strength"
	numTargets, mana, Effects = 0, 3, ""
	description = "Give a random Taunt minion in your hand +5/+5"
	name_CN = "实力担当"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if minions := [card for card in self.Game.Hand_Deck.hands[self.ID] if card.category == "Minion" and card.effects["Taunt"] > 0]:
			self.giveEnchant(numpyChoice(minions), 5, 5, source=FeatofStrength, add2EventinGUI=False)
		
	
class SwordEater(Minion):
	Class, race, name = "Warrior", "Pirate", "Sword Eater"
	mana, attack, health = 4, 2, 5
	name_CN = "吞剑艺人"
	numTargets, Effects, description = 0, "Taunt", "Taunt. Battlecry: Equip a 3/2 Sword"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.equipWeapon(Jawbreaker(self.Game, self.ID))
		
	
class Jawbreaker(Weapon):
	Class, name, description = "Warrior", "Jawbreaker", ""
	mana, attack, durability, Effects = 3, 3, 2, ""
	name_CN = "断颚之刃"
	index = "Uncollectible"
	
	
class RingmasterWhatley(Minion):
	Class, race, name = "Warrior", "", "Ringmaster Whatley"
	mana, attack, health = 5, 3, 5
	name_CN = "马戏领班威特利"
	numTargets, Effects, description = 0, "", "Battlecry: Draw a Mech, Dragon, and Pirate"
	index = "Battlecry~Legendary"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for race in ("Mech", "Dragon", "Pirate"): self.drawCertainCard(lambda card: race in card.race)
		
	
class TentTrasher(Minion):
	Class, race, name = "Warrior", "Dragon", "Tent Trasher"
	mana, attack, health = 5, 5, 5
	numTargets, Effects, description = 0, "Rush", "Rush. Costs (1) less for each friendly minion with a unique minion type"
	name_CN = "帐篷摧毁者"
	trigHand = Trig_TentTrasher
	def selfManaChange(self):
		#All type can only count as one of the 8 races.
		self.mana -= len(set(minion.race for minion in self.Game.minionsonBoard(self.ID) if minion.race))
		
	
class ArmorVendor(Minion):
	Class, race, name = "Neutral", "", "Armor Vendor"
	mana, attack, health = 1, 1, 3
	name_CN = "护甲商贩"
	numTargets, Effects, description = 0, "", "Battlecry: Give 4 Armor to each hero"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveHeroAttackArmor(1, armor=4)
		self.giveHeroAttackArmor(2, armor=4)
		
	
class Crabrider(Minion):
	Class, race, name = "Neutral", "Murloc", "Crabrider"
	mana, attack, health = 2, 1, 4
	numTargets, Effects, description = 0, "Rush,Windfury", "Rush, Windfury"
	name_CN = "螃蟹骑士"
	
	
class Deathwarden(Minion):
	Class, race, name = "Neutral", "", "Deathwarden"
	mana, attack, health = 3, 2, 5
	numTargets, Effects, description = 0, "", "Deathrattles can't trigger"
	name_CN = "死亡守望者"
	aura = GameRuleAura_Deathwarden
	
	
class Moonfang(Minion):
	Class, race, name = "Neutral", "Beast", "Moonfang"
	mana, attack, health = 5, 6, 3
	name_CN = "明月之牙"
	numTargets, Effects, description = 0, "", "Can only take 1 damage at a time"
	index = "Legendary"
	trigBoard = Trig_Moonfang
	
	
class RunawayBlackwing(Minion):
	Class, race, name = "Neutral", "Dragon", "Runaway Blackwing"
	mana, attack, health = 9, 9, 9
	numTargets, Effects, description = 0, "", "At the end of your turn, deal 9 damage to a random enemy minion"
	name_CN = "窜逃的黑翼龙"
	trigBoard = Trig_RunawayBlackwing		
	
	
class IllidariStudies(Spell):
	Class, school, name = "Demon Hunter", "", "Illidari Studies"
	numTargets, mana, Effects = 0, 1, ""
	description = "Discover an Outcast card. Your next one costs (1) less"
	name_CN = "伊利达雷研习"
	trigEffect = GameManaAura_IllidariStudies
	poolIdentifier = "Outcast Cards"
	@classmethod
	def generatePool(cls, pools):
		return "Outcast Cards", [card for card in pools.ClassCards["Demon Hunter"] if "~Outcast" in card.index]
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.discoverNew(comment, lambda : self.rngPool("Outcast Cards"))
		GameManaAura_IllidariStudies(self.Game, self.ID).auraAppears()
		
	
class FelfireDeadeye(Minion):
	Class, race, name = "Demon Hunter,Hunter", "", "Felfire Deadeye"
	mana, attack, health = 2, 2, 3
	numTargets, Effects, description = 0, "", "Your Hero Power costs (1) less"
	name_CN = "邪火神射手"
	aura = ManaAura_FelfireDeadeye
	
	
class Felsaber(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Felsaber"
	mana, attack, health = 4, 5, 6
	numTargets, Effects, description = 0, "Can't Attack", "Can only attack if your hero attacked this turn"
	name_CN = "邪刃豹"
	def attackAllowedbyEffect(self):
		return self.effects["Can't Attack"] < 1 or (self.effects["Can't Attack"] == 1 and not self.silenced
													and self.Game.Counters.examHeroAtks(self.ID, turnInd=self.Game.turnInd))
		
	
class Guidance(Spell):
	Class, school, name = "Druid,Shaman", "", "Guidance"
	numTargets, mana, Effects = 0, 1, ""
	description = "Look at two spells. Add one to your hand or Overload: (1) to get both"
	name_CN = "灵魂指引"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		pick, options = self.discoverNew(comment, lambda : self.rngPool(class4Discover(self) + " Spells"),
										 add2Hand=False, sideOption=SpiritPath())
		if isinstance(pick, SpiritPath):
			self.addCardtoHand(options, self.ID, byDiscover=True)
			self.Game.Manas.overloadMana(1, self.ID)
		else: self.addCardtoHand(pick, self.ID, byDiscover=True)
		
	
class SpiritPath(Option):
	name, description = "Spirit Path", "Add both spells to your hand. Overload: (1)"
	mana, attack, health = -1, -1, -1
	
	
class DreamingDrake_Corrupt(Minion):
	Class, race, name = "Druid", "Dragon", "Dreaming Drake"
	mana, attack, health = 3, 5, 6
	name_CN = "迷梦幼龙"
	numTargets, Effects, description = 0, "Taunt", "Corrupted. Taunt"
	index = "Uncollectible"
	
	
class DreamingDrake(Minion):
	Class, race, name = "Druid", "Dragon", "Dreaming Drake"
	mana, attack, health = 3, 3, 4
	numTargets, Effects, description = 0, "Taunt", "Taunt. Corrupt: Gain +2/+2"
	name_CN = "迷梦幼龙"
	trigHand, corruptedType = Trig_Corrupt, DreamingDrake_Corrupt
	
	
class ArborUp(Spell):
	Class, school, name = "Druid", "Nature", "Arbor Up"
	numTargets, mana, Effects = 0, 5, ""
	description = "Summon two 2/2 Treants. Give your minions +2/+1"
	name_CN = "树木生长"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon([Treant_Darkmoon(self.Game, self.ID) for _ in (0, 1)])
		self.giveEnchant(self.Game.minionsonBoard(self.ID), 2, 1, source=ArborUp)
		
	
class ResizingPouch(Spell):
	Class, school, name = "Hunter,Druid", "", "Resizing Pouch"
	numTargets, mana, Effects = 0, 1, ""
	description = "Discover a card with Cost equal to your remaining Mana Crystals"
	name_CN = "随心口袋"
	poolIdentifier = "Cards as Hunter"
	@classmethod
	def generatePool(cls, pools):
		return ["Cards as "+Class for Class in pools.Classes], [pools.ClassCards[Class]+pools.NeutralCards for Class in pools.Classes]
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		mana = self.Game.Manas.manas[self.ID]
		self.discoverNew(comment, lambda : [card for card in self.rngPool("Cards as %s"%class4Discover(self)) if card.mana == mana])
		
	
class BolaShot(Spell):
	Class, school, name = "Hunter", "", "Bola Shot"
	numTargets, mana, Effects = 1, 2, ""
	description = "Deal 1 damage to a minion and 2 damage to its neighbors"
	name_CN = "套索射击"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def text(self): return "%d, %d"%(self.calcDamage(1), self.calcDamage(2))
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		dmg_1, dmg_2 = self.calcDamage(1), self.calcDamage(2)
		for obj in target:
			if obj.onBoard and (neighbors := self.Game.neighbors2(obj)[0]):
				self.dealsDamage(objs := target+neighbors, [dmg_1]+[dmg_2]*len(neighbors))
			else: self.dealsDamage(target, dmg_1)
		
	
class Saddlemaster(Minion):
	Class, race, name = "Hunter", "", "Saddlemaster"
	mana, attack, health = 3, 3, 4
	numTargets, Effects, description = 0, "", "After you play a Beast, add a random Beast to your hand"
	name_CN = "鞍座大师"
	trigBoard = Trig_Saddlemaster		
	
	
class GlacierRacer(Minion):
	Class, race, name = "Mage", "", "Glacier Racer"
	mana, attack, health = 1, 1, 3
	numTargets, Effects, description = 0, "", "Spellburst: Deal 3 damage to all Frozen enemies"
	name_CN = "冰川竞速者"
	trigBoard = Trig_GlacierRacer		
	
	
class ConjureManaBiscuit(Spell):
	Class, school, name = "Mage", "Arcane", "Conjure Mana Biscuit"
	numTargets, mana, Effects = 0, 2, ""
	description = "Add a Biscuit to your hand that refreshes 2 Mana Crystals"
	name_CN = "制造法力饼干"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.addCardtoHand(ManaBiscuit, self.ID)
		
	
class ManaBiscuit(Spell):
	Class, school, name = "Mage", "", "Mana Biscuit"
	numTargets, mana, Effects = 0, 0, ""
	name_CN = "法力饼干"
	description = "Refresh 2 Mana Crystals"
	index = "Uncollectible"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.Game.Manas.restoreManaCrystal(2, self.ID, restoreAll=False)
		
	
class KeywardenIvory(Minion):
	Class, race, name = "Mage,Rogue", "", "Keywarden Ivory"
	mana, attack, health = 5, 4, 5
	name_CN = "钥匙守护者艾芙瑞"
	numTargets, Effects, description = 0, "", "Battlecry: Discover a dual-class spell from any class. Spellburst: Get another copy"
	index = "Battlecry~Legendary"
	trigEffect = Trig_KeywardenIvory
	poolIdentifier = "Dual Class Spells"
	@classmethod
	def generatePool(cls, pools):
		return "Dual Class Spells", list(set(card for cards in pools.ClassCards.values()
									for card in cards if "," in card.Class and card.category == "Spell"))
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		card, _ = self.discoverNew(comment, lambda : self.rngPool("Dual Class Spells"))
		if (self.onBoard or self.inHand) and card.inHand:  # Because the Trig here carries special info, can't use giveEnchant
			self.getsTrig(Trig_KeywardenIvory(self, type(card)))
		
	
class ImprisonedCelestial(Minion_Dormantfor2turns):
	Class, race, name = "Paladin", "", "Imprisoned Celestial"
	mana, attack, health = 3, 4, 5
	numTargets, Effects, description = 0, "", "Dormant for 2 turns. Spellburst: Give your minions Divine Shield"
	name_CN = "被禁锢的星骓"
	trigBoard = Trig_ImprisonedCelestial		
	
	
class Rally(Spell):
	Class, school, name = "Paladin,Priest", "Holy", "Rally!"
	numTargets, mana, Effects = 0, 4, ""
	description = "Resurrect a friendly 1-Cost, 2-Cost, and 3-Cost minion"
	name_CN = "开赛集结！"
	def available(self):
		return self.selectableMinionExists()
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		deads, tups = self.Game.Counters.examDeads(self.ID, veri_sum_ls=2), []
		for i in (1, 2, 3): #tup: (HonorStudent, (5, 5, 5, None, None, "Taunt"))
			if ls := [tup for tup in deads if tup[1][0] == i]: tups.append(numpyChoice(ls))
		if tups: self.summon([self.Game.fabCard(tup, self.ID, self) for tup in tups])
		
	
class LibramofJudgment_Corrupt(Weapon):
	Class, name, description = "Paladin", "Libram of Judgment", "Corrupted. Lifesteal"
	mana, attack, durability, Effects = 7, 5, 3, "Lifesteal"
	name_CN = "审判圣契"
	index = "Uncollectible"
	
	
class LibramofJudgment(Weapon):
	Class, name, description = "Paladin", "Libram of Judgment", "Corrupt: Gain Lifesteal"
	mana, attack, durability, Effects = 7, 5, 3, ""
	name_CN = "审判圣契"
	trigHand, corruptedType = Trig_Corrupt, LibramofJudgment_Corrupt
	
	
class Hysteria(Spell):
	Class, school, name = "Priest,Warlock", "Shadow", "Hysteria"
	numTargets, mana, Effects = 1, 4, ""
	description = "Choose a minion. It attacks random minions until it dies"
	name_CN = "狂乱"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for obj in target:
			#The minion must still be onBoard and alive in order to continue the loop
			i = 0 #Assume the loop can only last 14 times
			while obj.canBattle() and i < 14:
				if minions := self.Game.minionsAlive(exclude=obj):
					self.Game.battle(obj, numpyChoice(minions), resetRedirTrig=False)
				else: break
				i += 1
		
	
class Lightsteed(Minion):
	Class, race, name = "Priest", "Elemental", "Lightsteed"
	mana, attack, health = 4, 3, 6
	numTargets, Effects, description = 0, "", "Your healing effects also give affected minions +2 Health"
	name_CN = "圣光战马"
	trigBoard = Trig_Lightsteed		
	
	
class DarkInquisitorXanesh(Minion):
	Class, race, name = "Priest", "", "Dark Inquisitor Xanesh"
	mana, attack, health = 5, 3, 5
	name_CN = "黑暗审判官夏奈什"
	numTargets, Effects, description = 0, "", ""
	index = "Battlecry~Legendary"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for card in self.Game.Hand_Deck.hands[self.ID]:
			if "~ToCorrupt" in card.index:
				ManaMod(card, by=-2).applies()
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if "~ToCorrupt" in card.index:
				ManaMod(card, by=-2).applies()
		
	
class NitroboostPoison_Corrupt(Spell):
	Class, school, name = "Rogue,Warrior", "Nature", "Nitroboost Poison"
	numTargets, mana, Effects = 1, 2, ""
	name_CN = "氮素药膏"
	description = "Corrupted: Give a minion and your weapon +2 Attack"
	index = "Uncollectible"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(target, 2, 0, source=NitroboostPoison_Corrupt)
		if weapon:= self.Game.availableWeapon(self.ID): self.giveEnchant(weapon, 2, 0, source=NitroboostPoison_Corrupt)
		
	
class NitroboostPoison(Spell):
	Class, school, name = "Rogue,Warrior", "Nature", "Nitroboost Poison"
	numTargets, mana, Effects = 1, 2, ""
	description = "Give a minion +2 Attack. Corrupt: And your weapon"
	name_CN = "氮素药膏"
	trigHand, corruptedType = Trig_Corrupt, NitroboostPoison_Corrupt
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(target, 2, 0, source=NitroboostPoison)
		
	
class Shenanigans(Secret):
	Class, school, name = "Rogue", "", "Shenanigans"
	numTargets, mana, Effects = 0, 2, ""
	description = "Secret: When your opponent draws their second card in a turn, transform it into a Banana"
	name_CN = "蕉猾诡计"
	trigBoard = Trig_Shenanigans		
	
	
class SparkjoyCheat(Minion):
	Class, race, name = "Rogue", "", "Sparkjoy Cheat"
	mana, attack, health = 3, 3, 3
	name_CN = "欢脱的作弊选手"
	numTargets, Effects, description = 0, "", "Battlecry: If you're holding a Secret, cast it and draw a card"
	index = "Battlecry"
	def effCanTrig(self):
		self.effectViable = any(card.race == "Secret" and not self.Game.Secrets.sameSecretExists(card, self.ID) \
									for card in self.Game.Hand_Deck.hands[self.ID])
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if indices := [i for i, card in enumerate(self.Game.Hand_Deck.hands[self.ID]) \
				   if card.race == "Secret" and not self.Game.Secrets.sameSecretExists(card, self.ID)]:
			self.Game.Hand_Deck.extractfromHand(numpyChoice(indices), self.ID, enemyCanSee=False)[0].playedEffect()
			self.Game.Hand_Deck.drawCard(self.ID)
		
	
class ImprisonedPhoenix(Minion_Dormantfor2turns):
	Class, race, name = "Shaman,Mage", "Elemental", "Imprisoned Phoenix"
	mana, attack, health = 2, 2, 3
	numTargets, Effects, description = 0, "Spell Damage_2", "Dormant for 2 turns. Spell Damage +2"
	name_CN = "被禁锢的凤凰"
	
	
class Landslide(Spell):
	Class, school, name = "Shaman", "Nature", "Landslide"
	numTargets, mana, Effects = 0, 2, ""
	description = "Deal 1 damage to all enemy minions. If you're Overloaded, deal 1 damage again"
	name_CN = "大地崩陷"
	def text(self): return self.calcDamage(1)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(self.Game.minionsonBoard(3-self.ID), self.calcDamage(1))
		if self.Game.Manas.manasLocked[self.ID] > 0 or self.Game.Manas.manasOverloaded[self.ID] > 0:
			self.Game.gathertheDead()
			self.dealsDamage(self.Game.minionsonBoard(3-self.ID), self.calcDamage(1))
		
	
class Mistrunner(Minion):
	Class, race, name = "Shaman", "", "Mistrunner"
	mana, attack, health = 5, 4, 4
	name_CN = "迷雾行者"
	numTargets, Effects, description = 1, "", "Battlecry: Give a friendly minion +3/+3. Overload: (1)"
	index = "Battlecry"
	overload = 1
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists(self.ID)
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.ID == self.ID and obj.onBoard and obj is not self
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(target, 3, 3, source=Mistrunner)
		
	
class Backfire(Spell):
	Class, school, name = "Warlock", "Fire", "Backfire"
	numTargets, mana, Effects = 0, 3, ""
	description = "Draw 3 cards. Deal 3 damage to your hero"
	name_CN = "赛车回火"
	def text(self): return self.calcDamage(3)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for _ in range(3): self.Game.Hand_Deck.drawCard(self.ID)
		self.dealsDamage(self.Game.heroes[self.ID], self.calcDamage(3))
		
	
class LuckysoulHoarder_Corrupt(Minion):
	Class, race, name = "Warlock,Demon Hunter", "", "Luckysoul Hoarder"
	mana, attack, health = 3, 3, 4
	name_CN = "幸运之魂囤积者"
	numTargets, Effects, description = 0, "", "Corrupted. Battlecry: Shuffle 2 Soul Fragments into your deck. Draw a card"
	index = "Battlecry~Uncollectible"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.shuffleintoDeck([SoulFragment(self.Game, self.ID) for _ in (0, 1)])
		self.Game.Hand_Deck.drawCard(self.ID)
		
	
class LuckysoulHoarder(Minion):
	Class, race, name = "Warlock,Demon Hunter", "", "Luckysoul Hoarder"
	mana, attack, health = 3, 3, 4
	name_CN = "幸运之魂囤积者"
	numTargets, Effects, description = 0, "", "Battlecry: Shuffle 2 Soul Fragments into your deck. Corrupt: Draw a card"
	index = "Battlecry~ToCorrupt"
	trigHand, corruptedType = Trig_Corrupt, LuckysoulHoarder_Corrupt
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.shuffleintoDeck([SoulFragment(self.Game, self.ID) for _ in (0, 1)])
		
	
class EnvoyRustwix(Minion):
	Class, race, name = "Warlock", "Demon", "Envoy Rustwix"
	mana, attack, health = 5, 5, 4
	name_CN = "铁锈特使拉斯维克斯"
	numTargets, Effects, description = 0, "", "Deathrattle: Shuffle 3 random Prime Legendary minions into your deck"
	index = "Legendary"
	primeMinions = (MsshifnPrime, ZixorPrime, SolarianPrime, MurgurglePrime, ReliquaryPrime, AkamaPrime, VashjPrime, KanrethadPrime, KargathPrime)
	deathrattle = Death_EnvoyRustwix
	
	
class SpikedWheel(Weapon):
	Class, name, description = "Warrior", "Spiked Wheel", "Has +3 Attack when your hero has Armor"
	mana, attack, durability, Effects = 1, 0, 2, ""
	name_CN = "尖刺轮盘"
	trigBoard = Trig_SpikedWheel
	def statCheckResponse(self):
		if self.onBoard and self.Game.heroes[self.ID].armor > 0: self.attack += 3
		
	
class Ironclad(Minion):
	Class, race, name = "Warrior", "Mech", "Ironclad"
	mana, attack, health = 3, 2, 4
	name_CN = "铁甲战车"
	numTargets, Effects, description = 0, "", "Battlecry: If your hero has Armor, gain +2/+2"
	index = "Battlecry"
	def effCanTrig(self):
		self.effectViable = self.Game.heroes[self.ID].armor > 0
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.Game.heroes[self.ID].armor > 0: self.giveEnchant(self, 2, 2, source=Ironclad)
		
	
class Barricade(Spell):
	Class, school, name = "Warrior,Paladin", "", "Barricade"
	numTargets, mana, Effects = 0, 4, ""
	description = "Summon a 2/4 Guard with Taunt. If it's your only minion, summon another"
	name_CN = "路障"
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def effCanTrig(self):
		self.effectViable = not self.Game.minionsonBoard(self.ID)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon(RaceGuard(self.Game, self.ID))
		#Note that at this stage, there won't be deaths/deathrattles resolved.
		if len(self.Game.minionsonBoard(self.ID)) == 1: self.summon(RaceGuard(self.Game, self.ID))
		
	
class RaceGuard(Minion):
	Class, race, name = "Warrior,Paladin", "", "Race Guard"
	mana, attack, health = 3, 2, 4
	name_CN = "赛道护卫"
	numTargets, Effects, description = 0, "Taunt", "Taunt"
	index = "Uncollectible"
	
	


AllClasses_Darkmoon = [
	GameRuleAura_Deathwarden, Aura_DarkmoonStatue, ManaAura_LineHopper, GameRuleAura_Ilgynoth, ManaAura_GameMaster,
	ManaAura_FelfireDeadeye, Aura_InaraStormcrash, Trig_EndlessCorrupt, Trig_ParadeLeader, Trig_OptimisticOgre, Trig_RedeemedPariah,
	Trig_BladedLady, Trig_UmbralOwl, Trig_OpentheCages, Trig_RinlingsRifle, Trig_TramplingRhino, Trig_RiggedFaireGame,
	Trig_OhMyYogg, Trig_CarnivalBarker, Trig_NazmaniBloodweaver, Trig_BloodofGhuun, Trig_ShadowClone, Trig_MalevolentStrike,
	Trig_GrandTotemEysor, Trig_Magicfin, Trig_WhackAGnollHammer, Trig_ETCGodofMetal, Trig_RingmastersBaton, Trig_TentTrasher,
	Trig_Moonfang, Trig_RunawayBlackwing, Trig_Saddlemaster, Trig_GlacierRacer, Trig_KeywardenIvory, Trig_ImprisonedCelestial,
	Trig_Lightsteed, Trig_Shenanigans, Trig_SpikedWheel, Death_Showstopper, Death_ClawMachine, Death_RenownedPerformer,
	Death_Greybough, Death_SummonGreybough, Death_DarkmoonTonk, Death_TicketMaster, Death_RedscaleDragontamer, Death_RingMatron,
	Death_BumperCar, Death_EnvoyRustwix, CThuntheShattered_Effect, GameManaAura_IllidariStudies, Stiltstepper_Effect,
	Acrobatics_Effect, ExpendablePerformers_Effect, GameManaAura_LunarEclipse, SolarEclipse_Effect, GameManaAura_GameMaster,
	GameManaAura_FoxyFraud, LothraxiontheRedeemed_Effect, SafetyInspector, CostumedEntertainer, HorrendousGrowthCorrupt,
	HorrendousGrowth, ParadeLeader, PrizeVendor, RockRager, Showstopper, WrigglingHorror, BananaVendor, DarkmoonDirigible_Corrupt,
	DarkmoonDirigible, DarkmoonStatue_Corrupt, DarkmoonStatue, Gyreworm, InconspicuousRider, KthirRitualist, CircusAmalgam,
	CircusMedic_Corrupt, CircusMedic, FantasticFirebird, KnifeVendor, DerailedCoaster, DarkmoonRider, FleethoofPearltusk_Corrupt,
	FleethoofPearltusk, OptimisticOgre, ClawMachine, SilasDarkmoon, RotateThisWay, RotateThatWay, Strongman_Corrupt,
	Strongman, CarnivalClown_Corrupt, CarnivalClown, BodyofCThun, CThunsBody, EyeofCThun, HeartofCThun, MawofCThun,
	CThuntheShattered, DarkmoonRabbit, NZothGodoftheDeep, CurseofFlesh, DevouringHunger, HandofFate, MindflayerGoggles,
	Mysterybox, RodofRoasting, YoggSaronMasterofFate, YShaarjtheDefiler, FelscreamBlast, ThrowGlaive, RedeemedPariah,
	Acrobatics, DreadlordsBite, FelsteelExecutioner_Corrupt, FelsteelExecutioner, LineHopper, InsatiableFelhound_Corrupt,
	InsatiableFelhound, RelentlessPursuit, Stiltstepper, Ilgynoth, RenownedPerformer, PerformersAssistant, ZaitheIncredible,
	BladedLady, ExpendablePerformers, GuesstheWeight, NextCostsMore, NextCostsLess, LunarEclipse, SolarEclipse, FaireArborist_Corrupt,
	PrunetheFruit_Option, DigItUp_Option, FaireArborist, Treant_Darkmoon, MoontouchedAmulet_Corrupt, MoontouchedAmulet,
	KiriChosenofElune, Greybough, UmbralOwl, CenarionWard, FizzyElemental, MysteryWinner, DancingCobra_Corrupt, DancingCobra,
	DontFeedtheAnimals_Corrupt, DontFeedtheAnimals, OpentheCages, PettingZoo, DarkmoonStrider, RinlingsRifle, TramplingRhino,
	MaximaBlastenheimer, DarkmoonTonk, JewelofNZoth, ConfectionCyclone, SugarElemental, DeckofLunacy, GameMaster,
	RiggedFaireGame, OccultConjurer, RingToss_Corrupt, RingToss, FireworkElemental_Corrupt, FireworkElemental, SaygeSeerofDarkmoon,
	MaskofCThun, GrandFinale, ExplodingSparkler, OhMyYogg, RedscaleDragontamer, SnackRun, CarnivalBarker, DayattheFaire_Corrupt,
	DayattheFaire, BalloonMerchant, CarouselGryphon_Corrupt, CarouselGryphon, LothraxiontheRedeemed, HammeroftheNaaru,
	HolyElemental, HighExarchYrel, Insight_Corrupt, Insight, FairgroundFool_Corrupt, FairgroundFool, NazmaniBloodweaver,
	PalmReading, AuspiciousSpirits_Corrupt, AuspiciousSpirits, TheNamelessOne, FortuneTeller, IdolofYShaarj, GhuuntheBloodGod,
	BloodofGhuun, PrizePlunderer, FoxyFraud, ShadowClone, SweetTooth_Corrupt, SweetTooth, Swindle, TenwuoftheRedSmoke,
	CloakofShadows, TicketMaster, Tickets, PlushBear, MalevolentStrike, GrandEmpressShekzara, Revolve, CagematchCustodian,
	DeathmatchPavilion, PavilionDuelist, GrandTotemEysor, Magicfin, PitMaster_Corrupt, PitMaster, Stormstrike, WhackAGnollHammer,
	DunkTank_Corrupt, DunkTank, InaraStormcrash, WickedWhispers, MidwayManiac, FreeAdmission, ManariMosher, CascadingDisaster_Corrupt2,
	CascadingDisaster_Corrupt, CascadingDisaster, RevenantRascal, FireBreather, DeckofChaos, RingMatron, FieryImp,
	Tickatus_Corrupt, Tickatus, StageDive_Corrupt, StageDive, BumperCar, ETCGodofMetal, Minefield, RingmastersBaton,
	StageHand, FeatofStrength, SwordEater, Jawbreaker, RingmasterWhatley, TentTrasher, ArmorVendor, Crabrider, Deathwarden,
	Moonfang, RunawayBlackwing, IllidariStudies, FelfireDeadeye, Felsaber, Guidance, SpiritPath, DreamingDrake_Corrupt,
	DreamingDrake, ArborUp, ResizingPouch, BolaShot, Saddlemaster, GlacierRacer, ConjureManaBiscuit, ManaBiscuit,
	KeywardenIvory, ImprisonedCelestial, Rally, LibramofJudgment_Corrupt, LibramofJudgment, Hysteria, Lightsteed,
	DarkInquisitorXanesh, NitroboostPoison_Corrupt, NitroboostPoison, Shenanigans, SparkjoyCheat, ImprisonedPhoenix,
	Landslide, Mistrunner, Backfire, LuckysoulHoarder_Corrupt, LuckysoulHoarder, EnvoyRustwix, SpikedWheel, Ironclad,
	Barricade, RaceGuard, 
]

for class_ in AllClasses_Darkmoon:
	if issubclass(class_, Card):
		class_.index = "DARKMOON_FAIRE" + ("~" if class_.index else '') + class_.index