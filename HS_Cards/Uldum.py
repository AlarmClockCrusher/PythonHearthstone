from Parts.CardTypes import *
from Parts.TrigsAuras import *
from HS_Cards.Shadows import EVILCableRat


class ManaAura_GenerousMummy(ManaAura):
	by = -1
	def applicable(self, target): return target.ID != self.keeper.ID
		
	
class Aura_PhalanxCommander(Aura_AlwaysOn):
	signals, attGain, targets = ("MinionAppears", "CharEffectCheck"), 2, "All"
	def applicable(self, target): return target.effects["Taunt"] > 0
		
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return self.keeper.onBoard and target.category == "Minion" and target.ID == self.keeper.ID
		
	def trig(self, signal, ID, subject, target, num, comment, choice):
		if self.canTrig(signal, ID, subject, target, num, comment, choice):
			if signal.startswith("Char"):
				if target.effects["Taunt"] > 0 and all(receiver.recipient is not target for receiver in self.receivers):
					Aura_Receiver(target, self, 2, 0).effectStart()
				elif target.effects["Taunt"] < 1 and \
					(receiver := next((receiver for receiver in self.receivers if receiver.recipient is target), None)):
					receiver.effectClear()
			elif target.effects["Taunt"] > 0: Aura_Receiver(target, self, 2, 0).effectStart()
		
	
class Aura_Vessina(Aura_Conditional):
	signals, attGain, targets = ("MinionAppears", "OverloadCheck"), 2, "Others"
	def whichWay(self):
		keeper = self.keeper
		isOverloaded = keeper.Game.Manas.manasOverloaded[keeper.ID] > 0 or keeper.Game.Manas.manasLocked[keeper.ID] > 0
		if not isOverloaded and self.on: return -1
		elif isOverloaded and not self.on: return 1
		else: return 0
		
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		if signal[0] == 'M': return self.keeper.onBoard and ID == self.keeper.ID and self.on
		else: return self.keeper.onBoard and ID == self.keeper.ID
		
	
class Death_JarDealer(Deathrattle):
	description = "Deathrattle: Add a random 1-cost minion to your hand"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.addCardtoHand(numpyChoice(self.rngPool("1-Cost Minions")), self.keeper.ID)
		
	
class Death_KoboldSandtrooper(Deathrattle):
	description = "Deathrattle: Deal 3 damage to the enemy hero"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).dealsDamage(kpr.Game.heroes[3 - kpr.ID], 3)
		
	
class Death_SerpentEgg(Deathrattle):
	description = "Deathrattle: Summon a 3/4 Sea Serpent"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).summon(SeaSerpent(kpr.Game, kpr.ID))
		
	
class Death_InfestedGoblin(Deathrattle):
	description = "Deathrattle: Add two 1/1 Scarabs with Taunt to your hand"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.addCardtoHand([Scarab_Uldum, Scarab_Uldum], self.keeper.ID)
		
	
class Death_BlatantDecoy(Deathrattle):
	description = "Deathrattle: Each player summons the lowest Cost minion from their hand"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr, game = self.keeper, self.keeper.Game
		for ID in (1, 2):
			if game.space(ID) and (indices := pickInds_LowestAttr(game.Hand_Deck.hands[ID], cond=lambda card: card.category == "Minion")):
				game.summonfrom(numpyChoice(indices), ID, -1, summoner=kpr, hand_deck=0)
		
	
class Death_KhartutDefender(Deathrattle):
	description = "Deathrattle: Restore 4 Health to your hero"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).heals(kpr.Game.heroes[kpr.ID], kpr.calcHeal(4))
		
	
class Death_Octosari(Deathrattle):
	description = "Deathrattle: Draw 8 cards"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		for _ in range(8): self.keeper.Game.Hand_Deck.drawCard(self.keeper.ID)
		
	
class Death_AnubisathWarbringer(Deathrattle):
	description = "Deathrattle: Give all minions in your hand +3/+3"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).giveEnchant([card for card in kpr.Game.Hand_Deck.hands[kpr.ID] if card.category == "Minion"],
								3, 3, source=AnubisathWarbringer, add2EventinGUI=False)
		
	
class Death_SalhetsPride(Deathrattle):
	description = "Deathrattle: Draw two 1-Health minions from your deck"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		for _ in (0, 1):
			if not self.keeper.drawCertainCard(lambda card: card.category == "Minion" and card.health == 1)[0]: break
		
	
class Death_Grandmummy(Deathrattle):
	description = "Deathrattle: Give a random friendly minion +1/+1"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		if minions := (kpr := self.keeper).Game.minionsonBoard(kpr.ID): kpr.giveEnchant(numpyChoice(minions), 1, 1, source=Grandmummy)
		
	
class Death_SahketSapper(Deathrattle):
	description = "Deathrattle: Return a random enemy minion to your opponent's hand"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		if minions := (kpr := self.keeper).Game.minionsonBoard(3 - kpr.ID):
			kpr.Game.returnObj2Hand(kpr, numpyChoice(minions))
		
	
class Death_ExpiredMerchant(Deathrattle):
	description = "Deathrattle: Add 2 copies of discarded cards to your hand"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		game, ID = (kpr := self.keeper).Game, kpr.ID
		for tup in self.memory: kpr.addCardtoHand([game.fabCard(tup, ID, kpr) for _ in (0, 1)], ID)
		
	
class Trig_HighkeeperRa(TrigBoard):
	signals = ("TurnEnds",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).dealsDamage(kpr.Game.charsonBoard(3-kpr.ID), 20)
		
	
class Trig_DwarvenArchaeologist(TrigBoard):
	signals = ("HandCheck",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return comment == "Enter_Discover" and ID == kpr.ID and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		ManaMod(target, by=-1).applies()
		
	
class Trig_SpittingCamel(TrigBoard):
	signals = ("TurnEnds",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		minions = kpr.Game.minionsAlive(kpr.ID, exclude=kpr)
		if minions: self.keeper.dealsDamage(numpyChoice(minions), 1)
		
	
class Trig_HistoryBuff(TrigBoard):
	signals = ("CardPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return comment == "Minion" and ID == kpr.ID and kpr != kpr.Game.cardinPlay and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		if minions := [card for card in kpr.Game.Hand_Deck.hands[kpr.ID] if card.category == "Minion"]:
			kpr.giveEnchant(numpyChoice(minions), statEnchant=Enchantment_Exclusive(HistoryBuff, 1, 1), add2EventinGUI=False)
		
	
class Trig_ConjuredMirage(TrigBoard):
	signals = ("TurnStarts",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		#随从在可以触发回合开始扳机的时机一定是不结算其亡语的。可以安全地注销其死亡扳机
		kpr.Game.returnMiniontoDeck(kpr, kpr.ID, kpr.ID, deathrattlesStayArmed=False)
		
	
class Trig_SunstruckHenchman(TrigBoard):
	signals = ("TurnStarts", "TurnEnds",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		if signal == "TurnStarts":
			if numpyRandint(2): self.keeper.effects["Can't Attack"] += 1
		else: self.keeper.effects["Can't Attack"] -= 1 #signal == "TurnEnds"
		
	
class Trig_DesertObelisk(TrigBoard):
	signals = ("TurnEnds",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID and len([o for o in kpr.Game.minionsonBoard(kpr.ID) if o.name == "Desert Obelisk"]) > 2
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		if objs := (kpr := self.keeper).Game.charsAlive(3-kpr.ID): kpr.dealsDamage(numpyChoice(objs), 5)
		
	
class Trig_MortuaryMachine(TrigBoard):
	signals = ("CardBeenPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.Game.cardinPlay.category == "Minion" and kpr.onBoard and ID != kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).giveEnchant(kpr.Game.cardinPlay, effGain="Reborn", source=MortuaryMachine)
		
	
class Trig_WrappedGolem(TrigBoard):
	signals = ("TurnEnds",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).summon(Scarab_Uldum(kpr.Game, kpr.ID))
		
	
class Trig_UntappedPotential(Trig_Quest):
	signals = ("TurnEnds",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return ID == kpr.ID and kpr.Game.Manas.manas[kpr.ID] > 0
		
	
class Trig_CrystalMerchant(TrigBoard):
	signals = ("TurnEnds",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		if kpr.Game.Manas.manas[kpr.ID] > 0:
			kpr.Game.Hand_Deck.drawCard(kpr.ID)
		
	
class Trig_AnubisathDefender(TrigHand):
	signals = ("CardBeenPlayed", "TurnStarts", "TurnEnds",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.inHand and (signal[0] == 'T' or (comment == "Spell" and num[0] > 4 and ID == kpr.ID))
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).Game.Manas.calcMana_Single(kpr)
		
	
class Trig_UnsealtheVault(Trig_Quest):
	signals = ("ObjBeenSummoned",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return comment == "Minion" and ID == self.keeper.ID
		
	
class Trig_PressurePlate(Trig_Secret):
	signals = ("CardBeenPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return comment == "Spell" and kpr.ID != kpr.Game.turn == ID and kpr.Game.minionsAlive(ID)
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		if objs := (game := kpr.Game).minionsAlive(3-kpr.ID): kpr.Game.kill(kpr, numpyChoice(objs))
		
	
class Trig_DesertSpear(TrigBoard):
	signals = ("HeroAttackedMinion", "HeroAttackedHero",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		#The target can't be dying to trigger this
		return subject is kpr.Game.heroes[kpr.ID] and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).summon(Locust(kpr.Game, kpr.ID))
		
	
class Trig_RaidtheSkyTemple(Trig_Quest):
	signals = ("CardBeenPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return comment == "Spell" and ID == self.keeper.ID
		
	
class Trig_FlameWard(Trig_Secret):
	signals = ("MinionAttackedHero",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.ID != kpr.Game.turn and target is kpr.Game.heroes[kpr.ID]
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).dealsDamage(kpr.Game.minionsonBoard(3-kpr.ID), kpr.calcDamage(3))
		
	
class Trig_ArcaneFlakmage(TrigBoard):
	signals = ("CardBeenPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.race == "Secret" and kpr.onBoard and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).dealsDamage(kpr.Game.minionsonBoard(3-kpr.ID), 2)
		
	
class Trig_DuneSculptor(TrigBoard):
	signals = ("CardPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return comment == "Spell" and ID == kpr.ID and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).addCardtoHand(numpyChoice(self.rngPool("Mage Minions")), kpr.ID)
		
	
class Trig_MakingMummies(Trig_Quest):
	signals = ("CardBeenPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		#假设扳机的判定条件是打出的随从在检测时有复生就可以，如果在打出过程中获得复生，则依然算作任务进度
		return comment == "Minion" and ID == kpr.ID and kpr.effects["Reborn"] > 0
		
	
class Trig_BrazenZealot(TrigBoard):
	signals = ("ObjSummoned",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return comment == "Minion" and ID == kpr.ID and subject is not kpr and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).giveEnchant(kpr, statEnchant=Enchantment_Exclusive(BrazenZealot, 1, 0))
		
	
class Trig_MicroMummy(TrigBoard):
	signals = ("TurnEnds",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		if minions := kpr.Game.minionsonBoard(kpr.ID, exclude=kpr):
			kpr.giveEnchant(numpyChoice(minions), statEnchant=Enchantment_Exclusive(MicroMummy, 1, 0))
		
	
class Trig_ActivatetheObelisk(Trig_Quest):
	signals = ("MinionGetsHealed", "HeroGetsHealed",)
	def handleCounter(self, signal, ID, subject, target, num, comment, choice):
		self.counter += num
		
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return ID == self.keeper.ID
		
	
class Trig_SandhoofWaterbearer(TrigBoard):
	signals = ("TurnEnds",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		chars = [char for char in kpr.Game.charsAlive(kpr.ID) if char.health < char.health_max]
		if chars: kpr.heals(numpyChoice(chars), kpr.calcHeal(5))
		
	
class Trig_HighPriestAmet(TrigBoard):
	signals = ("ObjSummoned",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return subject.category == "Minion" and ID == kpr.ID and subject is not kpr and kpr.health > 0 and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).setStat(subject, (None, kpr.health), source=HighPriestAmet)
		
	
class Trig_BazaarBurglary(Trig_Quest):
	signals = ("HandCheck", "DrawingStops")
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		HeroClass = (kpr := self.keeper).Game.heroes[kpr.ID].Class
		if ID == kpr.ID and (signal[0] == "D" or (comment.startswith("Enter") and not comment != "Enter_Draw")):
			return any(HeroClass not in card.Class for card in target)
		return False
		
	def handleCounter(self, signal, ID, subject, target, num, comment, choice):
		self.counter += len(target)
		
	
class Trig_MirageBlade(TrigBoard):
	signals = ("BattleStarted", "BattleFinished",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return subject is kpr.Game.heroes[kpr.ID] and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		if signal == "BattleStarted": subject.getsEffect("Immune")
		else: subject.losesEffect("Immune")
		
	
class Trig_WhirlkickMaster(TrigBoard):
	signals = ("CardPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		#这个随从本身是没有连击的。同时目前没有名字中带有Combo的牌。
		return kpr.onBoard and ID == kpr.ID and "~Combo" in kpr.Game.cardinPlay.index
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).addCardtoHand(numpyChoice(self.rngPool("Combo Cards")), kpr.ID)
		
	
class Trig_CorrupttheWaters(Trig_Quest):
	signals = ("CardBeenPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return ID == kpr.ID and "~Battlecry" in kpr.Game.cardinPlay.index
		
	
class Trig_EVILTotem(TrigBoard):
	signals = ("TurnEnds",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).addCardtoHand(numpyChoice(EVILCableRat.lackeys), kpr.ID)
		
	
class Trig_MoguFleshshaper(TrigHand):
	signals = ("MinionAppears", "MinionDisappears",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return self.keeper.inHand
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).Game.Manas.calcMana_Single(kpr)
		
	
class Trig_SupremeArchaeology(Trig_Quest):
	signals = ("CardDrawn",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return ID == self.keeper.ID
		
	
class Trig_NefersetThrasher(TrigBoard):
	signals = ("MinionAttackingMinion", "MinionAttackingHero",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return subject is kpr and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).dealsDamage(kpr.Game.heroes[kpr.ID], 3)
		
	
class Trig_DiseasedVulture(TrigBoard):
	signals = ("HeroTookDmg",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return ID == kpr.ID == kpr.Game.turn
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).summon(numpyChoice(self.rngPool("3-Cost Minions to Summon"))(kpr.Game, kpr.ID))
		
	
class Trig_HacktheSystem(Trig_Quest):
	signals = ("HeroAttackedHero", "HeroAttackedMinion",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return subject is kpr.Game.heroes[kpr.ID]
		
	
class Trig_AnraphetsCore(TrigBoard):
	signals = ("HeroAttackedHero", "HeroAttackedMinion",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return subject is kpr.Game.heroes[kpr.ID] and kpr.chancesUsedUp()
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.usageCount -= 1
		
	
class Trig_LivewireLance(TrigBoard):
	signals = ("HeroAttackedMinion", "HeroAttackedHero",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		#The target can't be dying to trigger this
		return subject is kpr.Game.heroes[kpr.ID] and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).addCardtoHand(numpyChoice(EVILCableRat.lackeys), kpr.ID)
		
	
class Trig_Armagedillo(TrigBoard):
	signals = ("TurnEnds",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		kpr.giveEnchant([card for card in kpr.Game.Hand_Deck.hands[kpr.ID] \
							if card.category == "Minion" and card.effects["Taunt"] > 0],
						statEnchant=Enchantment(Armagedillo, 2, 2), add2EventinGUI=False)
		
	
class Trig_ArmoredGoon(TrigBoard):
	signals = ("HeroAttackingHero", "HeroAttackingMinion",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and subject is kpr.Game.heroes[kpr.ID]
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).giveHeroAttackArmor(kpr.ID, armor=5)
		
	
class HeartofVirnaal_Effect(TrigEffect):
	trigType = "TurnEnd&OnlyKeepOne"
	def trigEffect(self): self.Game.rules[self.ID]["Battlecry x2"] -= 1
		
	
class DarkPharaohTekahn_Effect(TrigEffect):
	signals, trigType = ("HandCheck", "DeckCheck", "MinionAppears",), "Conn&TrigAura&OnlyKeepOne"
	def connect(self):
		#当本扳机在场上的时候发现之前死亡的还是11的跟班时，跟班加入手牌之后会变成44。所以应该写成牌在进入场上，手牌和牌库时对其白字进行修改的扳机。
		#这个扳机也应该在连接的时候对场上，手牌和牌库的随从进行修改。被修改的随从得到一个修改过了的标签，避免重复生效。
		#标签存放在effects里面，不参与平时的效果结算。但是随从在被沉默的时候这个标签会失去。
		#变成44的效果生效过一次之后就。
		#以此法变成44的跟班被对面得到后如果其死亡，也可以让对面复活出44。这样的44被对面获得基础复制时，也是44。
		#这个样的44被对面发现死亡的随从时（裹尸匠），也是44
		trigAuras = self.Game.trigAuras[self.ID]
		if any(isinstance(trig, DarkPharaohTekahn_Effect) for trig in trigAuras):
			for sig in type(self).signals:
				trigs = self.Game.trigsBoard[self.ID][sig]
				i = next(i for i, trig in enumerate(trigs) if isinstance(trig, DarkPharaohTekahn_Effect))
				trigs.append(trigs.pop(i))  #只是移动扳机的位置
		else:
			trigAuras.append(self)
			for sig in type(self).signals: add2ListinDict(self, self.Game.trigsBoard[self.ID], sig)
			if self.Game.GUI: self.Game.GUI.heroZones[self.ID].addaTrig(self.card)
		#对场上、手牌和牌库中的所有满足条件的随从进行修改
		for card in self.Game.minionsonBoard(self.ID) + self.Game.Hand_Deck.hands[self.ID] + self.Game.Hand_Deck.decks[self.ID]:
			self.applies(card)
		
	def applicable(self, target):
		return target.ID == self.ID and "Lackey" in target.name and not (target.attack_0 == target.health_0 == 4)
		
	def applies(self, target):
		if "Lackey" in target.name and "Tekahn" not in target.effects:
			if target.onBoard or target.inHand:
				target.attack_0 = target.health_0 = 4
				target.dmgTaken = 0
				target.enchantments = [enchant for enchant in target.enchantments if enchant.effGain]
				target.calcStat()
			else:
				target.attack = target.health = target.health_max = target.attack_0 = target.health_0 = 4
				target.enchantments = [enchant for enchant in target.enchantments if enchant.effGain]
		
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		if signal[0] == "M": return self.applicable(target)
		elif signal[0] == "D": return ID == self.ID and comment in ("Replace", "ShuffleInto")
		else: return ID == self.ID and comment.startswith("Enter") and any(self.applicable(obj) for obj in target)
		
	def trig(self, signal, ID, subject, target, num, comment, choice):
		if self.canTrig(signal, ID, subject, target, num, comment, choice):
			if signal[0] == "M": self.applies(target)
			else:
				for obj in target: self.applies(obj)
		
	
class BeamingSidekick(Minion):
	Class, race, name = "Neutral", "", "Beaming Sidekick"
	mana, attack, health = 1, 1, 2
	name_CN = "欢快的同伴"
	numTargets, Effects, description = 1, "", "Battlecry: Give a friendly minion +2 Health"
	index = "Battlecry"
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists(self.ID, choice)
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.ID == self.ID and obj is not self and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(target, 0, 2, source=BeamingSidekick)
		
	
class JarDealer(Minion):
	Class, race, name = "Neutral", "", "Jar Dealer"
	mana, attack, health = 1, 1, 1
	numTargets, Effects, description = 0, "", "Deathrattle: Add a random 1-cost minion to your hand"
	name_CN = "陶罐商人"
	deathrattle = Death_JarDealer
	poolIdentifier = "1-Cost Minions"
	@classmethod
	def generatePool(cls, pools):
		return "1-Cost Minions", pools.MinionsofCost[1]
		
	
class MoguCultist(Minion):
	Class, race, name = "Neutral", "", "Mogu Cultist"
	mana, attack, health = 1, 1, 1
	name_CN = "魔古信徒"
	numTargets, Effects, description = 0, "", "Battlecry: If your board is full of Mogu Cultists, sacrifice them all and summon Highkeeper Ra"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		#强制要求场上有总共有7个魔古信徒，休眠物会让其效果无法触发
		minions = self.Game.minionsonBoard(self.ID)
		if len(minions) == 7 and all(minion.name == "Mogu Cultist" for minion in minions):
			self.Game.kill(None, minions)
			self.Game.gathertheDead()
			self.summon(HighkeeperRa(self.Game, self.ID))
		
	
class HighkeeperRa(Minion):
	Class, race, name = "Neutral", "", "Highkeeper Ra"
	mana, attack, health = 10, 20, 20
	name_CN = "莱，至高守护者"
	numTargets, Effects, description = 0, "", "At the end of your turn, deal 20 damage to all enemies"
	index = "Legendary~Uncollectible"
	trigBoard = Trig_HighkeeperRa		
	
	
class Murmy(Minion):
	Class, race, name = "Neutral", "Murloc", "Murmy"
	mana, attack, health = 1, 1, 1
	name_CN = "鱼人木乃伊"
	numTargets, Effects, description = 0, "Reborn", "Reborn"
	
	
class BugCollector(Minion):
	Class, race, name = "Neutral", "", "Bug Collector"
	mana, attack, health = 2, 2, 1
	name_CN = "昆虫收藏家"
	numTargets, Effects, description = 0, "", "Battlecry: Summon a 1/1 Locust with Rush"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon(Locust(self.Game, self.ID))
		
	
class Locust(Minion):
	Class, race, name = "Neutral", "Beast", "Locust"
	mana, attack, health = 1, 1, 1
	name_CN = "蝗虫"
	numTargets, Effects, description = 0, "Rush", "Rush"
	index = "Uncollectible"
	
	
class DwarvenArchaeologist(Minion):
	Class, race, name = "Neutral", "", "Dwarven Archaeologist"
	mana, attack, health = 2, 2, 3
	numTargets, Effects, description = 0, "", "After you Discover a card, reduce its cost by (1)"
	name_CN = "矮人历史学家"
	trigBoard = Trig_DwarvenArchaeologist		
	
	
class Fishflinger(Minion):
	Class, race, name = "Neutral", "Murloc", "Fishflinger"
	mana, attack, health = 2, 3, 2
	name_CN = "鱼人投手"
	numTargets, Effects, description = 0, "", "Battlecry: Add a random Murloc to each player's hand"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		murloc1, murloc2 = numpyChoice(self.rngPool("Murlocs"), 2, replace=False)
		self.addCardtoHand(murloc1, self.ID)
		self.addCardtoHand(murloc2, 3-self.ID)
		
	
class InjuredTolvir(Minion):
	Class, race, name = "Neutral", "", "Injured Tol'vir"
	mana, attack, health = 2, 2, 6
	name_CN = "受伤的托维尔人"
	numTargets, Effects, description = 0, "Taunt", "Taunt. Battlecry: Deal 3 damage to this minion"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(self, 3)
		
	
class KoboldSandtrooper(Minion):
	Class, race, name = "Neutral", "", "Kobold Sandtrooper"
	mana, attack, health = 2, 2, 1
	numTargets, Effects, description = 0, "", "Deathrattle: Deal 3 damage to the enemy hero"
	name_CN = "狗头人沙漠步兵"
	deathrattle = Death_KoboldSandtrooper
	
	
class NefersetRitualist(Minion):
	Class, race, name = "Neutral", "", "Neferset Ritualist"
	mana, attack, health = 2, 2, 3
	name_CN = "尼斐塞特仪祭师"
	numTargets, Effects, description = 0, "", "Battlecry: Restore adjacent minions to full Health"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.onBoard:
			for minion in self.Game.neighbors2(self)[0]:
				heal = self.calcHeal(minion.health_max)
				self.heals(minion, heal)
		
	
class QuestingExplorer(Minion):
	Class, race, name = "Neutral", "", "Questing Explorer"
	mana, attack, health = 2, 2, 3
	name_CN = "奋进的探险者"
	numTargets, Effects, description = 0, "", "Battlecry: If you control a Quest, draw a card"
	index = "Battlecry"
	def effCanTrig(self):
		self.effectViable = self.Game.Secrets.mainQuests[self.ID] or self.Game.Secrets.sideQuests[self.ID]
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.Game.Secrets.mainQuests[self.ID] or self.Game.Secrets.sideQuests[self.ID]:
			self.Game.Hand_Deck.drawCard(self.ID)
		
	
class QuicksandElemental(Minion):
	Class, race, name = "Neutral", "Elemental", "Quicksand Elemental"
	mana, attack, health = 2, 3, 2
	name_CN = "流沙元素"
	numTargets, Effects, description = 0, "", "Battlecry: Give all enemy minions -2 Attack this turn"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(self.Game.minionsonBoard(3 - self.ID), statEnchant=Enchantment(QuicksandElemental, -2, 0, until=0))
		
	
class SerpentEgg(Minion):
	Class, race, name = "Neutral", "", "Serpent Egg"
	mana, attack, health = 2, 0, 3
	numTargets, Effects, description = 0, "", "Deathrattle: Summon a 3/4 Sea Serpent"
	name_CN = "海蛇蛋"
	deathrattle = Death_SerpentEgg
	
	
class SeaSerpent(Minion):
	Class, race, name = "Neutral", "Beast", "Sea Serpent"
	mana, attack, health = 3, 3, 4
	name_CN = "海蛇"
	numTargets, Effects, description = 0, "", ""
	index = "Uncollectible"
	
	
class SpittingCamel(Minion):
	Class, race, name = "Neutral", "Beast", "Spitting Camel"
	mana, attack, health = 2, 2, 4
	numTargets, Effects, description = 0, "", "At the end of your turn, deal 1 damage to another random friendly minion"
	name_CN = "乱喷的骆驼"
	trigBoard = Trig_SpittingCamel		
	
	
class TempleBerserker(Minion):
	Class, race, name = "Neutral", "", "Temple Berserker"
	mana, attack, health = 2, 1, 2
	name_CN = "神殿狂战士"
	numTargets, Effects, description = 0, "Reborn", "Reborn. Has +2 Attack while damaged"
	def statCheckResponse(self):
		if self.onBoard and not self.silenced and self.dmgTaken > 0: self.attack += 2
		
	
class Vilefiend(Minion):
	Class, race, name = "Neutral", "Demon", "Vilefiend"
	mana, attack, health = 2, 2, 2
	numTargets, Effects, description = 0, "Lifesteal", "Lifesteal"
	name_CN = "邪犬"
	
	
class ZephrystheGreat(Minion):
	Class, race, name = "Neutral", "Elemental", "Zephrys the Great"
	mana, attack, health = 2, 3, 2
	name_CN = "了不起的杰弗里斯"
	numTargets, Effects, description = 0, "", "Battlecry: If your deck has no duplicates, wish for the perfect card"
	index = "Battlecry~Legendary"
	
	
class Candletaker(Minion):
	Class, race, name = "Neutral", "", "Candletaker"
	mana, attack, health = 3, 3, 2
	name_CN = "夺烛木乃伊"
	numTargets, Effects, description = 0, "Reborn", "Reborn"
	
	
class DesertHare(Minion):
	Class, race, name = "Neutral", "Beast", "Desert Hare"
	mana, attack, health = 3, 1, 1
	name_CN = "沙漠野兔"
	numTargets, Effects, description = 0, "", "Battlecry: Summon two 1/1 Desert Hares"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon([DesertHare(self.Game, self.ID) for _ in (0, 1)], relative="<>")
		
	
class GenerousMummy(Minion):
	Class, race, name = "Neutral", "", "Generous Mummy"
	mana, attack, health = 3, 5, 4
	name_CN = "慷慨的木乃伊"
	numTargets, Effects, description = 0, "Reborn", "Reborn. Your opponent's cards cost (1) less"
	aura = ManaAura_GenerousMummy
	
	
class GoldenScarab(Minion):
	Class, race, name = "Neutral", "Beast", "Golden Scarab"
	mana, attack, health = 3, 2, 2
	name_CN = "金甲虫"
	numTargets, Effects, description = 0, "", "Battlecry: Discover a 4-cost card"
	index = "Battlecry"
	poolIdentifier = "4-Cost Cards as Druid"
	@classmethod
	def generatePool(cls, pools):
		return genPool_CertainCardsasClass(pools, "4-Cost", cond=lambda card: card.mana == 4)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.discoverNew(comment, lambda : self.rngPool("4-Cost Cards as "+class4Discover(self)))
		
	
class HistoryBuff(Minion):
	Class, race, name = "Neutral", "", "History Buff"
	mana, attack, health = 3, 3, 4
	numTargets, Effects, description = 0, "", "Whenever you play a minion, give a random minion in your hand +1/+1"
	name_CN = "历史爱好者"
	trigBoard = Trig_HistoryBuff		
	
	
class InfestedGoblin(Minion):
	Class, race, name = "Neutral", "", "Infested Goblin"
	mana, attack, health = 3, 2, 3
	numTargets, Effects, description = 0, "Taunt", "Taunt. Deathrattle: Add two 1/1 Scarabs with Taunt to your hand"
	name_CN = "招虫的地精"
	deathrattle = Death_InfestedGoblin
	
	
class Scarab_Uldum(Minion):
	Class, race, name = "Neutral", "Beast", "Scarab"
	mana, attack, health = 1, 1, 1
	name_CN = "甲虫"
	numTargets, Effects, description = 0, "Taunt", "Taunt"
	index = "Uncollectible"
	
	
class MischiefMaker(Minion):
	Class, race, name = "Neutral", "", "Mischief Maker"
	mana, attack, health = 3, 3, 3
	name_CN = "捣蛋鬼"
	numTargets, Effects, description = 0, "", "Battlecry: Swap the top deck of your deck with your opponent's"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		#不知道如果一方牌库为空时会如何,假设一方牌库为空时不触发效果
		if self.Game.Hand_Deck.decks[1] and self.Game.Hand_Deck.decks[2]:
			card1 = self.Game.Hand_Deck.removeDeckTopCard(1)
			card2 = self.Game.Hand_Deck.removeDeckTopCard(2)
			card1.ID, card2.ID = 2, 1
			self.Game.Hand_Deck.decks[1].append(card2)
			self.Game.Hand_Deck.decks[2].append(card1)
			card1.entersDeck()
			card2.entersDeck()
		
	
class VulperaScoundrel(Minion):
	Class, race, name = "Neutral", "", "Vulpera Scoundrel"
	mana, attack, health = 3, 2, 3
	name_CN = "狐人恶棍"
	numTargets, Effects, description = 0, "", "Battlecry: Discover a spell or pick a mystery choice"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		poolFunc = lambda : self.rngPool(class4Discover(self)+" Spells")
		option, _ = self.discoverNew(comment, poolFunc=poolFunc, add2Hand=False, sideOption=MysteryChoice())
		if isinstance(option, MysteryChoice): self.addCardtoHand(numpyChoice(poolFunc()), self.ID, byDiscover=True)
		else: self.addCardtoHand(option, self.ID, byDiscover=True)
		
	
class MysteryChoice(Option):
	name, description = "Mystery Choice!", "Add a random spell to your hand"
	mana, attack, health = -1, -1, -1
	
	
class BoneWraith(Minion):
	Class, race, name = "Neutral", "", "Bone Wraith"
	mana, attack, health = 4, 2, 5
	name_CN = "白骨怨灵"
	numTargets, Effects, description = 0, "Reborn,Taunt", "Reborn, Taunt"
	
	
class BodyWrapper(Minion):
	Class, race, name = "Neutral", "", "Body Wrapper"
	mana, attack, health = 4, 4, 4
	name_CN = "裹尸匠"
	numTargets, Effects, description = 0, "", "Battlecry: Discover a friendly minion that died this game. Shuffle it into your deck"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		card, _ = self.discoverfrom(comment, tupsFunc=lambda : self.Game.Counters.examDeads(self.ID, veri_sum_ls=2))
		if card: self.shuffleintoDeck(card, enemyCanSee=False)
		
	
class ConjuredMirage(Minion):
	Class, race, name = "Neutral", "", "Conjured Mirage"
	mana, attack, health = 4, 3, 10
	numTargets, Effects, description = 0, "Taunt", "Taunt. At the start of your turn, shuffle this minion into your deck"
	name_CN = "魔法幻象"
	trigBoard = Trig_ConjuredMirage		
	
	
class SunstruckHenchman(Minion):
	Class, race, name = "Neutral", "", "Sunstruck Henchman"
	mana, attack, health = 4, 6, 5
	numTargets, Effects, description = 0, "", "At the start of your turn, this has a 50% chance to fall asleep"
	name_CN = "中暑的匪徒"
	trigBoard = Trig_SunstruckHenchman		
	
	
class FacelessLurker(Minion):
	Class, race, name = "Neutral", "", "Faceless Lurker"
	mana, attack, health = 5, 3, 3
	name_CN = "无面潜伏者"
	numTargets, Effects, description = 0, "Taunt", "Taunt. Battlecry: Double this minion's Health"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.setStat(self, (None, self.health*2), source=FacelessLurker)
		
	
class DesertObelisk(Minion):
	Class, race, name = "Neutral", "", "Desert Obelisk"
	mana, attack, health = 5, 0, 5
	numTargets, Effects, description = 0, "", "If your control 3 of these at the end of your turn, deal 5 damage to a random enemy"
	name_CN = "沙漠方尖碑"
	trigBoard = Trig_DesertObelisk		
	
	
class MortuaryMachine(Minion):
	Class, race, name = "Neutral", "Mech", "Mortuary Machine"
	mana, attack, health = 5, 8, 8
	numTargets, Effects, description = 0, "", "After your opponent plays a minion, give it Reborn"
	name_CN = "机械法医"
	trigBoard = Trig_MortuaryMachine		
	
	
class PhalanxCommander(Minion):
	Class, race, name = "Neutral", "", "Phalanx Commander"
	mana, attack, health = 5, 4, 5
	numTargets, Effects, description = 0, "", "Your Taunt minions have +2 Attack"
	name_CN = "方阵指挥官"
	aura = Aura_PhalanxCommander
	
	
class WastelandAssassin(Minion):
	Class, race, name = "Neutral", "", "Wasteland Assassin"
	mana, attack, health = 5, 4, 2
	name_CN = "废土刺客"
	numTargets, Effects, description = 0, "Stealth,Reborn", "Stealth, Reborn"
	
	
class BlatantDecoy(Minion):
	Class, race, name = "Neutral", "", "Blatant Decoy"
	mana, attack, health = 6, 5, 5
	numTargets, Effects, description = 0, "", "Deathrattle: Each player summons the lowest Cost minion from their hand"
	name_CN = "显眼的诱饵"
	deathrattle = Death_BlatantDecoy
	
	
class KhartutDefender(Minion):
	Class, race, name = "Neutral", "", "Khartut Defender"
	mana, attack, health = 6, 3, 4
	name_CN = "卡塔图防御者"
	numTargets, Effects, description = 0, "Taunt,Reborn", "Taunt, Reborn. Deathrattle: Restore 4 Health to your hero"
	deathrattle = Death_KhartutDefender
	
	
class Siamat(Minion):
	Class, race, name = "Neutral", "Elemental", "Siamat"
	mana, attack, health = 7, 6, 6
	name_CN = "希亚玛特"
	numTargets, Effects, description = 0, "", "Battlecry: Gain 2 of Rush, Taunt, Divine Shield, or Windfury (your choice)"
	index = "Battlecry~Legendary"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		options = [option() for option in (SiamatsHeart, SiamatsShield, SiamatsSpeed, SiamatsWind)]
		for _ in (0, 1):
			options.remove(chosen := self.chooseFixedOptions(comment, options))
			self.giveEnchant(self, effGain=type(chosen).effect, source=Siamat)
		
	
class SiamatsHeart(Option):
	name, effect, description = "Siamat's Heart", "Taunt", "Give Siamat Taunt"
	mana, attack, health = 0, -1, -1
	
	
class SiamatsShield(Option):
	name, effect, description = "Siamat's Shield", "Divined Shield", "Give Siamat Divined Shield"
	mana, attack, health = 0, -1, -1
	
	
class SiamatsSpeed(Option):
	name, effect, description = "Siamat's Speed", "Rush", "Give Siamat Rush"
	mana, attack, health = 0, -1, -1
	
	
class SiamatsWind(Option):
	name, effect, description = "Siamat's Wind", "Windfury", "Give Siamat Windfury"
	mana, attack, health = 0, -1, -1
	
	
class WastelandScorpid(Minion):
	Class, race, name = "Neutral", "Beast", "Wasteland Scorpid"
	mana, attack, health = 7, 3, 9
	numTargets, Effects, description = 0, "Poisonous", "Poisonous"
	name_CN = "废土巨蝎"
	
	
class WrappedGolem(Minion):
	Class, race, name = "Neutral", "", "Wrapped Golem"
	mana, attack, health = 7, 7, 5
	name_CN = "被缚的魔像"
	numTargets, Effects, description = 0, "Reborn", "Reborn. At the end of your turn, summon a 1/1 Scarab with Taunt"
	trigBoard = Trig_WrappedGolem		
	
	
class Octosari(Minion):
	Class, race, name = "Neutral", "Beast", "Octosari"
	mana, attack, health = 8, 8, 8
	name_CN = "八爪巨怪"
	numTargets, Effects, description = 0, "", "Deathrattle: Draw 8 cards"
	index = "Legendary"
	deathrattle = Death_Octosari
	
	
class PitCrocolisk(Minion):
	Class, race, name = "Neutral", "Beast", "Pit Crocolisk"
	mana, attack, health = 8, 5, 6
	name_CN = "深坑鳄鱼"
	numTargets, Effects, description = 1, "", "Battlecry: Deal 5 damage"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(target, 5)
		
	
class AnubisathWarbringer(Minion):
	Class, race, name = "Neutral", "", "Anubisath Warbringer"
	mana, attack, health = 9, 9, 6
	numTargets, Effects, description = 0, "", "Deathrattle: Give all minions in your hand +3/+3"
	name_CN = "阿努比萨斯战争使者"
	deathrattle = Death_AnubisathWarbringer
	
	
class ColossusoftheMoon(Minion):
	Class, race, name = "Neutral", "", "Colossus of the Moon"
	mana, attack, health = 10, 10, 10
	name_CN = "月亮巨人"
	numTargets, Effects, description = 0, "Divine Shield,Reborn", "Divine Shield, Reborn"
	index = "Legendary"
	
	
class KingPhaoris(Minion):
	Class, race, name = "Neutral", "", "King Phaoris"
	mana, attack, health = 10, 5, 5
	name_CN = "法奥瑞斯国王"
	numTargets, Effects, description = 0, "", "Battlecry: For each spell in your hand, summon a minion of the same Cost"
	index = "Battlecry~Legendary"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		#根据莱登之拳的效果，假设如果手牌中的法术费用过高，无法对应卡池中的随从，则不会召唤
		game, minions = self.Game, []
		for card in self.Game.Hand_Deck.hands[self.ID]:
			if card.category == "Spell" and (key := card.mana+"-Cost Minions to Summon") in game.RNGPools:
				minions.append(numpyChoice(self.rngPool(key))(card.mana-1, by=1, ID=self.ID))
		if minions: self.summon(minions)
		
	
class LivingMonument(Minion):
	Class, race, name = "Neutral", "", "Living Monument"
	mana, attack, health = 10, 10, 10
	numTargets, Effects, description = 0, "Taunt", "Taunt"
	name_CN = "活化方尖碑"
	
	
class UntappedPotential(Quest):
	Class, school, name = "Druid", "", "Untapped Potential"
	numTargets, mana, Effects = 0, 1, ""
	name_CN = "发掘潜力"
	description = "Quest: End 4 turns with any unspent Mana. Reward: Orissian Tear"
	index = "Legendary"
	numNeeded = 4
	trigBoard = Trig_UntappedPotential
	def questEffect(self, game, ID):
		OssirianTear(game, ID).replacePower()
		
	
class OssirianTear(Power):
	mana, name, numTargets = 0, "Ossirian Tear", 0
	description = "Passive Hero Power. Your Choose One cards have both effects combined"
	name_CN = "奥斯里安之泪"
	def available(self, choice=0): return False
		
	def use(self, target=None, choice=0, sendthruServer=True): pass
		
	def appears(self): self.Game.rules[self.ID]["Choose Both"] += 1
		
	def disappears(self): self.Game.rules[self.ID]["Choose Both"] -= 1
		
	
class WorthyExpedition(Spell):
	Class, school, name = "Druid", "", "Worthy Expedition"
	numTargets, mana, Effects = 0, 1, ""
	description = "Discover a Choose One card"
	name_CN = "不虚此行"
	poolIdentifier = "Choose One Cards"
	@classmethod
	def generatePool(cls, pools):
		return "Choose One Cards", [card for card in pools.ClassCards["Druid"] if card.options]
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.discoverNew(comment, lambda : self.rngPool("Choose One Cards"))
		
	
class CrystalMerchant(Minion):
	Class, race, name = "Druid", "", "Crystal Merchant"
	mana, attack, health = 2, 1, 4
	numTargets, Effects, description = 0, "", "If you have any unspent Mana at the end of your turn, draw a card"
	name_CN = "水晶商人"
	trigBoard = Trig_CrystalMerchant		
	
	
class BEEEES(Spell):
	Class, school, name = "Druid", "", "BEEEES!!!"
	numTargets, mana, Effects = 1, 3, ""
	description = "Choose a minion. Summon four 1/1 Bees that attack it"
	name_CN = "蜜蜂"
	def available(self):
		return self.selectableMinionExists() and self.Game.space(self.ID) > 0
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for obj in target:
			self.summon(bees := [Bee_Uldum(self.Game, self.ID) for i in (0, 1, 2, 3)])
			for bee in bees: #召唤的蜜蜂需要在场上且存活，同时目标也需要在场且存活
				if obj.canBattle():
					if bee.canBattle(): self.Game.battle(bee, obj)
				else: break
		
	
class Bee_Uldum(Minion):
	Class, race, name = "Druid", "Beast", "Bee"
	mana, attack, health = 1, 1, 1
	name_CN = "蜜蜂"
	numTargets, Effects, description = 0, "", ""
	index = "Uncollectible"
	
	
class GardenGnome(Minion):
	Class, race, name = "Druid", "", "Garden Gnome"
	mana, attack, health = 4, 2, 3
	name_CN = "园艺侏儒"
	numTargets, Effects, description = 0, "", "Battlecry: If you're holding a spell that costs (5) or more, summon two 2/2 Treants"
	index = "Battlecry"
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.holdingBigSpell(self.ID)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.Game.Hand_Deck.holdingBigSpell(self.ID):
			self.summon([Treant_Uldum(self.Game, self.ID) for _ in (0, 1)], relative="<>")
		
	
class Treant_Uldum(Minion):
	Class, race, name = "Druid", "", "Treant"
	mana, attack, health = 2, 2, 2
	name_CN = "树人"
	numTargets, Effects, description = 0, "", ""
	index = "Uncollectible"
	
	
class AnubisathDefender(Minion):
	Class, race, name = "Druid", "", "Anubisath Defender"
	mana, attack, health = 5, 3, 5
	numTargets, Effects, description = 0, "Taunt", "Taunt. Costs (0) if you've cast a spell this turn that costs (5) or more"
	name_CN = "阿努比萨斯防御者"
	trigHand = Trig_AnubisathDefender
	def selfManaChange(self):
		if self.Game.Counters.examCardPlays(self.ID, turnInd=self.Game.turnInd, cond=self.Game.Counters.checkTup_BigSpell):
			self.mana = 0
		
	
class ElisetheEnlightened(Minion):
	Class, race, name = "Druid", "", "Elise the Enlightened"
	mana, attack, health = 5, 5, 5
	name_CN = "启迪者伊莉斯"
	numTargets, Effects, description = 0, "", "Battlecry: If your deck has no duplicates, duplicate your hand"
	index = "Battlecry~Legendary"
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.noDuplicatesinDeck(self.ID)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		HD = self.Game.Hand_Deck
		if HD.noDuplicatesinDeck(self.ID):
			self.addCardtoHand([self.copyCard(card, self.ID) for card in HD.hands[self.ID]], self.ID)
		
	
class FocusedBurst_Option(Option):
	name, description = "Focused Burst", "Gain +2/+2"
	mana, attack, health = 5, -1, -1
	
	
class DivideandConquer_Option(Option):
	name, description = "Divide and Conquer", "Summon a copy of this minion"
	mana, attack, health = 5, -1, -1
	def available(self):
		return self.keeper.Game.space(self.keeper.ID) > 0
		
	
class OasisSurger(Minion):
	Class, race, name = "Druid", "Elemental", "Oasis Surger"
	mana, attack, health = 5, 3, 3
	name_CN = "绿洲涌动者"
	numTargets, Effects, description = 0, "Rush", "Rush. Choose One: Gain +2/+2; or Summon a copy of this minion"
	options = (FocusedBurst_Option, DivideandConquer_Option)
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if choice < 1: self.giveEnchant(self, 2, 2, source=OasisSurger)
		if choice and not self.dead: self.summon(self.copyCard(self, self.ID))
		
	
class BefriendtheAncient(Spell):
	Class, school, name = "Druid", "", "Befriend the Ancient"
	numTargets, mana, Effects = 0, 6, ""
	name_CN = "结识古树"
	description = "Summon a 6/6 Ancient with Taunt"
	index = "Uncollectible"
	def available(self):
		return self.Game.space(self.ID)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon(VirnaalAncient(self.Game, self.ID))
		
	
class DrinktheWater(Spell):
	Class, school, name = "Druid", "", "Drink the Water"
	numTargets, mana, Effects = 1, 6, ""
	name_CN = "饮用泉水"
	description = "Restore 12 Health"
	index = "Uncollectible"
	def text(self): return self.calcHeal(12)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.heals(target, self.calcHeal(12))
		
	
class BefriendtheAncient_Option(Option):
	name, description = "Befriend the Ancient", "Summon a 6/6 Ancient with Taunt"
	mana, attack, health = 6, -1, -1
	spell = BefriendtheAncient
	def available(self):
		return self.keeper.Game.space(self.keeper.ID) > 0
		
	
class DrinktheWater_Option(Option):
	name, description = "Drink the Water", "Restore 12 Health"
	mana, attack, health = 6, -1, -1
	spell = DrinktheWater
	def available(self):
		return self.keeper.selectableCharExists(1)
		
	
class HiddenOasis(Spell):
	Class, school, name = "Druid", "Nature", "Hidden Oasis"
	numTargets, mana, Effects = 1, 6, ""
	name_CN = "隐秘绿洲"
	description = "Choose One: Summon a 6/6 Ancient with Taunt; or Restore 12 Health"
	options = (BefriendtheAncient_Option, DrinktheWater_Option)
	def numTargetsNeeded(self, choice=0):
		return 1 if choice else 0
		
	def available(self):
		#当场上有全选光环时，变成了一个指向性法术，必须要有一个目标可以施放。
		if self.Game.rules[self.ID]["Choose Both"] > 0:
			return self.selectableCharExists(1)
		else: return self.Game.space(self.ID) > 0 or self.selectableCharExists(1)
		
	def text(self): return self.calcHeal(12)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if choice and target: self.heals(target, self.calcHeal(12))
		if choice < 1: self.summon(VirnaalAncient(self.Game, self.ID))
		
	
class VirnaalAncient(Minion):
	Class, race, name = "Druid", "", "Vir'naal Ancient"
	mana, attack, health = 6, 6, 6
	name_CN = "维尔纳尔古树"
	numTargets, Effects, description = 0, "Taunt", "Taunt"
	index = "Uncollectible"
	
	
class Overflow(Spell):
	Class, school, name = "Druid", "Nature", "Overflow"
	numTargets, mana, Effects = 0, 7, ""
	description = "Restore 5 Health to all characters. Draw 5 cards"
	name_CN = "溢流"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.heals(self.Game.charsonBoard(self.ID), self.calcHeal(5))
		for _ in range(5): self.Game.Hand_Deck.drawCard(self.ID)
		
	
class UnsealtheVault(Quest):
	Class, school, name = "Hunter", "", "Unseal the Vault"
	numTargets, mana, Effects = 0, 1, ""
	name_CN = "打开宝库"
	description = "Quest: Summon 20 minions. Reward: Ramkahen Roar"
	index = "Legendary"
	numNeeded = 20
	trigBoard = Trig_UnsealtheVault
	def questEffect(self, game, ID):
		PharaohsWarmask(game, ID).replacePower()
		
	
class PharaohsWarmask(Power):
	mana, name, numTargets = 2, "Pharaoh's Warmask", 0
	description = "Give your minions +2 Attack"
	name_CN = "法老的面盔"
	def effect(self, target=(), choice=0, comment=''):
		self.giveEnchant(self.Game.minionsonBoard(self.ID), 2, 0, source=PharaohsWarmask)
		
	
class PressurePlate(Secret):
	Class, school, name = "Hunter", "", "Pressure Plate"
	numTargets, mana, Effects = 0, 2, ""
	description = "Secret: After your opponent casts a spell, destroy a random enemy minion"
	name_CN = "压感陷阱"
	trigBoard = Trig_PressurePlate		
	
	
class DesertSpear(Weapon):
	Class, name, description = "Hunter", "Desert Spear", "After your hero Attacks, summon a 1/1 Locust with Rush"
	mana, attack, durability, Effects = 3, 1, 3, ""
	name_CN = "沙漠之矛"
	trigBoard = Trig_DesertSpear		
	
	
class HuntersPack(Spell):
	Class, school, name = "Hunter", "", "Hunter's Pack"
	numTargets, mana, Effects = 0, 3, ""
	description = "Add a random Hunter Beast, Secret, and Weapon to your hand"
	name_CN = "猎人工具包"
	poolIdentifier = "Hunter Beasts"
	@classmethod
	def generatePool(cls, pools):
		return ["Hunter Beasts", "Hunter Weapons"], [[card for card in pools.ClassCards["Hunter"] if "Beast" in card.race],
													[card for card in pools.ClassCards["Hunter"] if card.category == "Weapon"]]
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.addCardtoHand(numpyChoice(self.rngPool("Hunter Beasts")),
							 numpyChoice(self.rngPool("Hunter Secrets")),
							 numpyChoice(self.rngPool("Hunter Weapons")), self.ID)
		
	
class HyenaAlpha(Minion):
	Class, race, name = "Hunter", "Beast", "Hyena Alpha"
	mana, attack, health = 4, 3, 3
	name_CN = "土狼头领"
	numTargets, Effects, description = 0, "", "Battlecry: If you control a Secret, summon two 2/2 Hyenas"
	index = "Battlecry"
	def effCanTrig(self):
		self.effectViable = self.Game.Secrets.secrets[self.ID]
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.Game.Secrets.secrets[self.ID]: self.summon([Hyena_Uldum(self.Game, self.ID) for _ in (0, 1)], relative="<>")
		
	
class Hyena_Uldum(Minion):
	Class, race, name = "Hunter", "Beast", "Hyena"
	mana, attack, health = 2, 2, 2
	name_CN = "土狼"
	numTargets, Effects, description = 0, "", ""
	index = "Uncollectible"
	
	
class RamkahenWildtamer(Minion):
	Class, race, name = "Hunter", "", "Ramkahen Wildtamer"
	mana, attack, health = 3, 4, 3
	name_CN = "拉穆卡恒驯兽师"
	numTargets, Effects, description = 0, "", "Battlecry: Copy a random Beast in your hand"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if beasts := [card for card in self.Game.Hand_Deck.hands[self.ID] if "Beast" in card.race]:
			self.addCardtoHand(self.copyCard(numpyChoice(beasts), self.ID), self.ID)
		
	
class SwarmofLocusts(Spell):
	Class, school, name = "Hunter", "", "Swarm of Locusts"
	numTargets, mana, Effects = 0, 6, ""
	description = "Summon seven 1/1 Locusts with Rush"
	name_CN = "飞蝗虫群"
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon([Locust(self.Game, self.ID) for i in range(7)])
		
	
class ScarletWebweaver(Minion):
	Class, race, name = "Hunter", "Beast", "Scarlet Webweaver"
	mana, attack, health = 6, 5, 5
	name_CN = "猩红织网蛛"
	numTargets, Effects, description = 0, "", "Battlecry: Reduce the Cost of a random Beast in your hand by (5)"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if cards := self.findCards2ReduceMana(lambda card: "Beast" in card.race):
			ManaMod(numpyChoice(cards), by=-5).applies()
		
	
class WildBloodstinger(Minion):
	Class, race, name = "Hunter", "Beast", "Wild Bloodstinger"
	mana, attack, health = 6, 6, 9
	name_CN = "刺血狂蝎"
	numTargets, Effects, description = 0, "", "Battlecry: Summon a minion from your opponent's hand. Attack it"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.Game.space(3-self.ID) and \
			(indices := [i for i, card in enumerate(self.Game.Hand_Deck.hands[3-self.ID] ) if card.category == "Minion"]):
			minion = self.Game.summonfrom(numpyChoice(indices), 3-self.ID, -1, summoner=self, hand_deck=0)
			if self.canBattle() and minion.canBattle(): self.Game.battle(self, minion)
		
	
class DinotamerBrann(Minion):
	Class, race, name = "Hunter", "", "Dinotamer Brann"
	mana, attack, health = 7, 2, 4
	name_CN = "恐龙大师布莱恩"
	numTargets, Effects, description = 0, "", "Battlecry: If your deck has no duplicates, summon King Krush"
	index = "Battlecry~Legendary"
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.noDuplicatesinDeck(self.ID)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.Game.Hand_Deck.noDuplicatesinDeck(self.ID): self.summon(KingKrush_Uldum(self.Game, self.ID))
		
	
class KingKrush_Uldum(Minion):
	Class, race, name = "Hunter", "Beast", "King Krush"
	mana, attack, health = 9, 8, 8
	name_CN = "暴龙王克鲁什"
	numTargets, Effects, description = 0, "Charge", "Charge"
	index = "Legendary~Uncollectible"
	
	
class RaidtheSkyTemple(Quest):
	Class, school, name = "Mage", "", "Raid the Sky Temple"
	numTargets, mana, Effects = 0, 1, ""
	name_CN = "洗劫天空殿"
	description = "Quest: Cast 10 spell. Reward: Ascendant Scroll"
	index = "Legendary"
	numNeeded = 10
	trigBoard = Trig_RaidtheSkyTemple
	def questEffect(self, game, ID):
		AscendantScroll(game, ID).replacePower()
		
	
class AscendantScroll(Power):
	mana, name, numTargets = 2, "Ascendant Scroll", 0
	description = "Add a random Mage spell to your hand. It costs (2) less"
	name_CN = "升腾卷轴"
	def effect(self, target=(), choice=0, comment=''):
		spell = numpyChoice(self.rngPool("Mage Spells"))(self.Game, self.ID)
		spell.manaMods.append(ManaMod(spell, by=-2))
		self.addCardtoHand(spell, self.ID)
		
	
class AncientMysteries(Spell):
	Class, school, name = "Mage", "Arcane", "Ancient Mysteries"
	numTargets, mana, Effects = 0, 2, ""
	description = "Draw a Secret from your deck. It costs (0)"
	name_CN = "远古谜团"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		secret, mana, entersHand = self.drawCertainCard(lambda card: card.race == "Secret")
		if entersHand: ManaMod(secret, to=0).applies()
		
	
class FlameWard(Secret):
	Class, school, name = "Mage", "Fire", "Flame Ward"
	numTargets, mana, Effects = 0, 3, ""
	description = "Secret: After a minion attacks your hero, deal 3 damage to all enemy minions"
	name_CN = "火焰结界"
	trigBoard = Trig_FlameWard		
	
	
class CloudPrince(Minion):
	Class, race, name = "Mage", "Elemental", "Cloud Prince"
	mana, attack, health = 5, 4, 4
	name_CN = "云雾王子"
	numTargets, Effects, description = 1, "", "Battlecry: If you control a Secret, deal 6 damage"
	index = "Battlecry"
	def numTargetsNeeded(self, choice=0):
		return 1 if self.Game.Secrets.secrets[self.ID] else 0
		
	def effCanTrig(self):
		self.effectViable = self.Game.Secrets.secrets[self.ID]
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.Game.Secrets.secrets[self.ID]: self.dealsDamage(target, 6)
		
	
class ArcaneFlakmage(Minion):
	Class, race, name = "Mage", "", "Arcane Flakmage"
	mana, attack, health = 2, 3, 2
	numTargets, Effects, description = 0, "", "After you play a Secret, deal 2 damage to all enemy minions"
	name_CN = "对空奥术法师"
	trigBoard = Trig_ArcaneFlakmage		
	
	
class DuneSculptor(Minion):
	Class, race, name = "Mage", "", "Dune Sculptor"
	mana, attack, health = 3, 3, 3
	numTargets, Effects, description = 0, "", "After you cast a spell, add a random Mage minion to your hand"
	name_CN = "沙丘塑形者"
	trigBoard = Trig_DuneSculptor
	
	
class NagaSandWitch(Minion):
	Class, race, name = "Mage", "", "Naga Sand Witch"
	mana, attack, health = 5, 5, 5
	name_CN = "纳迦沙漠女巫"
	numTargets, Effects, description = 0, "", "Battlecry: Change the Cost of spells in your hand to (5)"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for spell in [card for card in self.Game.Hand_Deck.hands[self.ID] if card.category == "Spell"]:
			ManaMod(spell, to=5).applies()
		self.Game.Manas.calcMana_All()
		
	
class TortollanPilgrim(Minion):
	Class, race, name = "Mage", "", "Tortollan Pilgrim"
	mana, attack, health = 8, 5, 5
	name_CN = "始祖龟朝圣者"
	numTargets, Effects, description = 0, "", "Battlecry: Discover a spell in your deck and cast it with random targets"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		_, i = self.discoverfrom(comment, cond=lambda card: card.category == "Spell")
		if i > -1: self.Game.Hand_Deck.extractfromHand(i, self.ID, enemyCanSee=True)[0].cast()
		
	
class RenotheRelicologist(Minion):
	Class, race, name = "Mage", "", "Reno the Relicologist"
	mana, attack, health = 6, 4, 6
	name_CN = "考古学家 雷诺"
	numTargets, Effects, description = 0, "", "Battlecry: If your deck has no duplicates, deal 10 damage randomly split among all enemy minions"
	index = "Battlecry~Legendary"
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.noDuplicatesinDeck(self.ID)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		game, side = self.Game, 3 - self.ID
		if game.Hand_Deck.noDuplicatesinDeck(self.ID):
			for _ in range(10):
				if minions := game.minionsAlive(side): self.dealsDamage(numpyChoice(minions), 1)
				else: break
		
	
class PuzzleBoxofYoggSaron(Spell):
	Class, school, name = "Mage", "", "Puzzle Box of Yogg-Saron"
	numTargets, mana, Effects = 0, 10, ""
	description = "Cast 10 random spells (targets chosen randomly)"
	name_CN = "尤格-萨隆的谜之匣"
	poolIdentifier = "Spells"
	@classmethod
	def generatePool(cls, pools):
		return "Spells", [card for cards in pools.ClassSpells.values() for card in cards]
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		game = self.Game
		game.sendSignal("SpellBeenCast", self.ID, self, None, 0, "", choice)
		for _ in range(10):
			numpyChoice(self.rngPool("Spells"))(game, self.ID).cast()
			game.gathertheDead(decideWinner=True)
		
	
class MakingMummies(Quest):
	Class, school, name = "Paladin", "", "Making Mummies"
	numTargets, mana, Effects = 0, 1, ""
	name_CN = "制作木乃伊"
	description = "Quest: Play 5 Reborn minions. Reward: Emperor Wraps"
	index = "Legendary"
	numNeeded = 5
	trigBoard = Trig_MakingMummies
	def questEffect(self, game, ID):
		EmperorWraps(game, ID).replacePower()
		
	
class EmperorWraps(Power):
	mana, name, numTargets = 2, "Emperor Wraps", 1
	description = "Summon a 2/2 copy of a friendly minion"
	name_CN = "帝王裹布"
	def available(self, choice=0):
		return not self.chancesUsedUp() and self.Game.space(self.ID) > 0 and self.selectableMinionExists(self.ID)
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard and obj.ID == self.ID
		
	def effect(self, target=(), choice=0, comment=''):
		for obj in target: self.summon(self.copyCard(obj, self.ID, 2, 2))
		
	
class BrazenZealot(Minion):
	Class, race, name = "Paladin", "", "Brazen Zealot"
	mana, attack, health = 1, 2, 1
	numTargets, Effects, description = 0, "", "Whenever you summon a minion, gain +1 Attack"
	name_CN = "英勇狂热者"
	trigBoard = Trig_BrazenZealot
	
	
class MicroMummy(Minion):
	Class, race, name = "Paladin", "Mech", "Micro Mummy"
	mana, attack, health = 2, 1, 2
	name_CN = "微型木乃伊"
	numTargets, Effects, description = 0, "Reborn", "Reborn. At the end of your turn, give another random friendly minion +1 Attack"
	trigBoard = Trig_MicroMummy
	
	
class SandwaspQueen(Minion):
	Class, race, name = "Paladin", "Beast", "Sandwasp Queen"
	mana, attack, health = 2, 3, 1
	name_CN = "沙漠蜂后"
	numTargets, Effects, description = 0, "", "Battlecry: Add two 2/1 Sandwasps to your hand"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.addCardtoHand([Sandwasp, Sandwasp], self.ID)
		
	
class Sandwasp(Minion):
	Class, race, name = "Paladin", "Beast", "Sandwasp"
	mana, attack, health = 1, 2, 1
	name_CN = "沙漠胡蜂"
	numTargets, Effects, description = 0, "", ""
	index = "Uncollectible"
	
	
class SirFinleyoftheSands(Minion):
	Class, race, name = "Paladin", "Murloc", "Sir Finley of the Sands"
	mana, attack, health = 2, 2, 3
	name_CN = "沙漠爵士芬利"
	numTargets, Effects, description = 0, "", "Battlecry: If your deck has no duplicates, Discover an upgraded Hero Power"
	index = "Battlecry~Legendary"
	poolIdentifier = "Upgraded Powers"
	@classmethod
	def generatePool(cls, pools):
		return "Upgraded Powers", pools.upgradedPowers
		
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.noDuplicatesinDeck(self.ID)
		
	def decideUpgradedPowerPool(self):
		powerType = type(self.Game.powers[self.ID])
		return [power for power in self.rngPool("Upgraded Powers") if power is not powerType]
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		power, _ = self.discoverNew(comment, lambda : SirFinleyoftheSands.decideUpgradedPowerPool(self), add2Hand=False)
		power.replacePower()
		
	
class Subdue(Spell):
	Class, school, name = "Paladin", "", "Subdue"
	numTargets, mana, Effects = 1, 2, ""
	description = "Change a minion's Attack and Health to 1"
	name_CN = "制伏"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.setStat(target, (1, 1), source=Subdue)
		
	
class SalhetsPride(Minion):
	Class, race, name = "Paladin", "Beast", "Salhet's Pride"
	mana, attack, health = 3, 3, 1
	numTargets, Effects, description = 0, "", "Deathrattle: Draw two 1-Health minions from your deck"
	name_CN = "萨赫特的傲狮"
	deathrattle = Death_SalhetsPride
	
	
class AncestralGuardian(Minion):
	Class, race, name = "Paladin", "", "Ancestral Guardian"
	mana, attack, health = 4, 4, 2
	name_CN = "先祖守护者"
	numTargets, Effects, description = 0, "Lifesteal,Reborn", "Lifesteal, Reborn"
	
	
class PharaohsBlessing(Spell):
	Class, school, name = "Paladin", "Holy", "Pharaoh's Blessing"
	numTargets, mana, Effects = 1, 6, ""
	description = "Give a minion +4/+4, Divine Shield, and Taunt"
	name_CN = "法老祝福"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(target, 4, 4, multipleEffGains=(("Divine Shield", 1, None), ("Taunt", 1, None)), source=PharaohsBlessing)
		
	
class TiptheScales(Spell):
	Class, school, name = "Paladin", "", "Tip the Scales"
	numTargets, mana, Effects = 0, 8, ""
	description = "Summon 7 Murlocs from your deck"
	name_CN = "鱼人为王"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for _ in range(7):
			if not self.try_SummonfromOwn(cond=lambda card: "Murloc" in card.race): break
		
	
class ActivatetheObelisk(Quest):
	Class, school, name = "Priest", "", "Activate the Obelisk"
	numTargets, mana, Effects = 0, 1, ""
	name_CN = "激活方尖碑"
	description = "Quest: Restore 15 Health. Reward: Obelisk's Eye"
	index = "Legendary"
	numNeeded = 15
	trigBoard = Trig_ActivatetheObelisk
	def questEffect(self, game, ID):
		ObelisksEye(game, ID).replacePower()
		
	
class ObelisksEye(Power):
	mana, name, numTargets = 2, "Obelisk's Eye", 1
	description = "Restore 3 Health. If you target a minion, also give it +3/+3"
	name_CN = "方尖碑之眼"
	def text(self): return self.calcHeal(3)
		
	def effect(self, target=(), choice=0, comment=''):
		for obj in target:
			self.heals(obj, self.calcHeal(3))
			self.giveEnchant(obj, 3, 3, source=ObelisksEye)
		
	
class EmbalmingRitual(Spell):
	Class, school, name = "Priest", "", "Embalming Ritual"
	numTargets, mana, Effects = 1, 1, ""
	description = "Give a minion Reborn"
	name_CN = "防腐仪式"
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(target, effGain="Reborn", source=EmbalmingRitual)
		
	
class Penance(Spell):
	Class, school, name = "Priest", "Holy", "Penance"
	numTargets, mana, Effects = 1, 2, "Lifesteal"
	description = "Lifesteal. Deal 3 damage to a minion"
	name_CN = "苦修"
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def text(self): return self.calcDamage(3)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(target, self.calcDamage(3))
		
	
class SandhoofWaterbearer(Minion):
	Class, race, name = "Priest", "", "Sandhoof Waterbearer"
	mana, attack, health = 5, 5, 5
	numTargets, Effects, description = 0, "", "At the end of your turn, restore 5 Health to a damaged friendly character"
	name_CN = "沙蹄搬水工"
	trigBoard = Trig_SandhoofWaterbearer		
	
	
class Grandmummy(Minion):
	Class, race, name = "Priest", "", "Grandmummy"
	mana, attack, health = 2, 1, 2
	name_CN = "木奶伊"
	numTargets, Effects, description = 0, "Reborn", "Reborn. Deathrattle: Give a random friendly minion +1/+1"
	deathrattle = Death_Grandmummy
	
	
class HolyRipple(Spell):
	Class, school, name = "Priest", "Holy", "Holy Ripple"
	numTargets, mana, Effects = 0, 2, ""
	description = "Deal 1 damage to all enemies. Restore 1 Health to all friendly characters"
	name_CN = "神圣涟漪"
	def text(self): return "%d, %d"%(self.calcDamage(1), self.calcHeal(1))
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(self.Game.charsonBoard(3-self.ID), self.calcDamage(1))
		self.heals(self.Game.charsonBoard(self.ID), self.calcHeal(1))
		
	
class WretchedReclaimer(Minion):
	Class, race, name = "Priest", "", "Wretched Reclaimer"
	mana, attack, health = 3, 3, 3
	name_CN = "卑劣的回收者"
	numTargets, Effects, description = 1, "", "Battlecry: Destroy a friendly minion, then return it to life with full Health"
	index = "Battlecry"
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists(self.ID, choice)
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj is not self and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for obj in target: self.killandSummon(obj, self.copyCard(obj, self.ID, bareCopy=True))
		
	
class Psychopomp(Minion):
	Class, race, name = "Priest", "", "Psychopomp"
	mana, attack, health = 4, 3, 1
	name_CN = "接引冥神"
	numTargets, Effects, description = 0, "", "Battlecry: Summon a random friendly minion that died this game. Give it Reborn"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if tups := self.Game.Counters.examDeads(self.ID, veri_sum_ls=2):
			minion = self.Game.fabCard(numpyChoice(tups), self.ID, self)
			self.giveEnchant(minion, effGain="Reborn", source=Psychopomp)
			self.summon(minion)
		
	
class HighPriestAmet(Minion):
	Class, race, name = "Priest", "", "High Priest Amet"
	mana, attack, health = 4, 2, 7
	name_CN = "高阶祭司阿门特"
	numTargets, Effects, description = 0, "", "Whenever you summon a minion, set its Health equal to this minion's"
	index = "Legendary"
	trigBoard = Trig_HighPriestAmet		
	
	
class PlagueofDeath(Spell):
	Class, school, name = "Priest", "Shadow", "Plague of Death"
	numTargets, mana, Effects = 0, 9, ""
	description = "Silence and destroy all minions"
	name_CN = "死亡之灾祸"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		minions = self.Game.minionsonBoard()
		for minion in minions:
			minion.getsSilenced()
		self.Game.kill(self, minions)
		
	
class BazaarBurglary(Quest):
	Class, school, name = "Rogue", "", "Bazaar Burglary"
	numTargets, mana, Effects = 0, 1, ""
	name_CN = "劫掠集市"
	description = "Quest: Add 4 cards from other classes to your hand. Reward: Ancient Blades"
	index = "Legendary"
	numNeeded = 4
	trigBoard = Trig_BazaarBurglary
	def questEffect(self, game, ID):
		AncientBlades(game, ID).replacePower()
		
	
class AncientBlades(Power):
	mana, name, numTargets = 2, "Ancient Blades", 0
	description = "Equip a 3/2 Blade with Immune while attacking"
	name_CN = "远古刀锋"
	def effect(self, target=(), choice=0, comment=''):
		self.equipWeapon(MirageBlade(self.Game, self.ID))
		
	
class MirageBlade(Weapon):
	Class, name, description = "Rogue", "Mirage Blade", "Your hero is Immune while attacking"
	mana, attack, durability, Effects = 2, 3, 2, ""
	name_CN = "幻象之刃"
	index = "Uncollectible"
	trigBoard = Trig_MirageBlade		
	
	
class PharaohCat(Minion):
	Class, race, name = "Rogue", "Beast", "Pharaoh Cat"
	mana, attack, health = 1, 1, 2
	name_CN = "法老御猫"
	numTargets, Effects, description = 0, "", "Battlecry: Add a random Reborn minion to your hand"
	index = "Battlecry"
	poolIdentifier = "Reborn Minions"
	@classmethod
	def generatePool(cls, pools):
		return "Reborn Minions", [card for cards in pools.MinionsofCost.values() for card in cards if "Reborn" in card.Effects]
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.addCardtoHand(numpyChoice(self.rngPool("Reborn Minions")), self.ID)
		
	
class PlagueofMadness(Spell):
	Class, school, name = "Rogue", "Shadow", "Plague of Madness"
	numTargets, mana, Effects = 0, 1, ""
	description = "Each player equips a 2/2 Knife with Poisonous"
	name_CN = "疯狂之灾祸"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.equipWeapon(PlaguedKnife(self.Game, self.ID))
		self.equipWeapon(PlaguedKnife(self.Game, 3-self.ID))
		
	
class PlaguedKnife(Weapon):
	Class, name, description = "Rogue", "Plagued Knife", "Poisonous"
	mana, attack, durability, Effects = 1, 2, 2, "Poisonous"
	name_CN = "灾祸狂刀"
	index = "Uncollectible"
	
	
class CleverDisguise(Spell):
	Class, school, name = "Rogue", "", "Clever Disguise"
	numTargets, mana, Effects = 0, 2, ""
	description = "Add 2 random spells from another Class to your hand"
	name_CN = "聪明的伪装"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		classes = self.rngPool("Classes")[:]
		removefrom(self.Game.heroes[self.ID].Class, classes)
		self.addCardtoHand(numpyChoice(self.rngPool("%s Spells"%numpyChoice(classes)), 2, replace=True), self.ID)
		
	
class WhirlkickMaster(Minion):
	Class, race, name = "Rogue", "", "Whirlkick Master"
	mana, attack, health = 2, 1, 2
	numTargets, Effects, description = 0, "", "Whenever you play a Combo card, add a random Combo card to your hand"
	name_CN = "连环腿大师"
	trigBoard = Trig_WhirlkickMaster		
	poolIdentifier = "Combo Cards"
	@classmethod
	def generatePool(cls, pools):
		return "Combo Cards", [card for card in pools.ClassCards["Rogue"] if "~Combo" in card.index]
		
	
class HookedScimitar(Weapon):
	Class, name, description = "Rogue", "Hooked Scimitar", "Combo: Gain +2 Attack"
	mana, attack, durability, Effects = 3, 2, 2, ""
	name_CN = "钩镰弯刀"
	index = "Combo"
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.comboCounters[self.ID] > 0
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.Game.Counters.comboCounters[self.ID] > 0: self.giveEnchant(self, 2, 0, source=HookedScimitar)
		
	
class SahketSapper(Minion):
	Class, race, name = "Rogue", "Pirate", "Sahket Sapper"
	mana, attack, health = 4, 4, 4
	numTargets, Effects, description = 0, "", "Deathrattle: Return a random enemy minion to your opponent's hand"
	name_CN = "萨赫柯特工兵"
	deathrattle = Death_SahketSapper
	
	
class BazaarMugger(Minion):
	Class, race, name = "Rogue", "", "Bazaar Mugger"
	mana, attack, health = 5, 3, 5
	name_CN = "集市恶痞"
	numTargets, Effects, description = 0, "Rush", "Rush. Battlecry: Add a random minion from another class to your hand"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		heroClass = self.Game.heroes[self.ID].Class
		classes = [Class for Class in self.rngPool("Classes") if Class != heroClass]
		self.addCardtoHand(numpyChoice(self.rngPool(numpyChoice(classes)+" Minions")), self.ID)
		
	
class ShadowofDeath(Spell):
	Class, school, name = "Rogue", "Shadow", "Shadow of Death"
	numTargets, mana, Effects = 1, 4, ""
	description = "Choose a minion. Shuffle 3 'Shadows' into your deck that summon a copy when drawn"
	name_CN = "死亡之影"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for obj in target:
			typTarget = type(obj)
			subclass = type("Shadow__"+typTarget.__name__, (Shadow,),
							{"info1": typTarget}
							)
			self.shuffleintoDeck([subclass(self.Game, self.ID) for _ in (0, 1, 2)])
		
	
class Shadow(Spell):
	Class, school, name = "Rogue", "", "Shadow"
	numTargets, mana, Effects = 0, 4, ""
	name_CN = "阴影"
	description = "Casts When Drawn. Summon a (0)"
	index = "Uncollectible"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if minion := type(self).info1: self.summon(minion(self.Game, self.ID))
		
	
class AnkatheBuried(Minion):
	Class, race, name = "Rogue", "", "Anka, the Buried"
	mana, attack, health = 5, 5, 5
	name_CN = "被埋葬的安卡"
	numTargets, Effects, description = 0, "", "Battlecry: Change each Deathrattle minion in your hand into a 1/1 that costs (1)"
	index = "Battlecry~Legendary"
	def effCanTrig(self):
		return any(card.category == "Minion" and card.deathrattles and card is not self for card in self.Game.Hand_Deck.hands[self.ID])
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for card in self.Game.Hand_Deck.hands[self.ID][:]:
			if card.category == "Minion" and card.deathrattles:
				self.setStat(card, (1, 1), source=AnkatheBuried, add2EventinGUI=False)
				ManaMod(card, to=1).applies()
		
	
class CorrupttheWaters(Quest):
	Class, school, name = "Shaman", "", "Corrupt the Waters"
	numTargets, mana, Effects = 0, 1, ""
	name_CN = "腐化水源"
	description = "Quest: Play 6 Battlecry cards. Reward: Heart of Vir'naal"
	index = "Legendary"
	numNeeded = 6
	trigBoard = Trig_CorrupttheWaters
	def questEffect(self, game, ID):
		HeartofVirnaal(game, ID).replacePower()
		
	
class HeartofVirnaal(Power):
	mana, name, numTargets = 2, "Heart of Vir'naal", 0
	description = "Your Battlecries trigger twice this turn"
	name_CN = "维尔纳尔之心"
	trigEffect = HeartofVirnaal_Effect
	def effect(self, target=(), choice=0, comment=''):
		self.Game.rules[self.ID]["Battlecry x2"] += 1
		HeartofVirnaal_Effect(self.Game, self.ID).connect()
		
	
class TotemicSurge(Spell):
	Class, school, name = "Shaman", "Nature", "Totemic Surge"
	numTargets, mana, Effects = 0, 0, ""
	description = "Give your Totems +2 Attack"
	name_CN = "图腾潮涌"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(self.Game.minionsonBoard(self.ID, race="Totem"), 2, 2, source=TotemicSurge)
		
	
class EVILTotem(Minion):
	Class, race, name = "Shaman", "Totem", "EVIL Totem"
	mana, attack, health = 2, 0, 2
	numTargets, Effects, description = 0, "", "At the end of your turn, add a Lackey to your hand"
	name_CN = "怪盗图腾"
	trigBoard = Trig_EVILTotem		
	
	
class SandstormElemental(Minion):
	Class, race, name = "Shaman", "Elemental", "Sandstorm Elemental"
	mana, attack, health = 2, 2, 2
	name_CN = "沙暴元素"
	numTargets, Effects, description = 0, "", "Battlecry: Deal 1 damage to all enemy minions. Overload: (1)"
	index = "Battlecry"
	overload = 1
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(self.Game.minionsonBoard(3-self.ID), 1)
		
	
class PlagueofMurlocs(Spell):
	Class, school, name = "Shaman", "", "Plague of Murlocs"
	numTargets, mana, Effects = 0, 3, ""
	description = "Transform all minions into random Murlocs"
	name_CN = "鱼人之灾祸"
	poolIdentifier = "Murlocs to Summon"
	@classmethod
	def generatePool(cls, pools):
		return "Murlocs to Summon", pools.MinionswithRace["Murloc"]
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		game = self.Game
		if minions := self.Game.minionsonBoard():
			cards = numpyChoice(self.rngPool("Murlocs"), len(minions), replace=True)
			self.transform(minions, [card(game, obj.ID) for card, obj in zip(cards, minions)])
		
	
class WeaponizedWasp(Minion):
	Class, race, name = "Shaman", "Beast", "Weaponized Wasp"
	mana, attack, health = 3, 3, 3
	name_CN = "武装黄蜂"
	numTargets, Effects, description = 1, "", "Battlecry: If you control a Lackey, deal 3 damage"
	index = "Battlecry"
	def numTargetsNeeded(self, choice=0):
		return 1 if any(minion.name.endswith("Lackey") for minion in self.Game.minionsonBoard(self.ID)) else 0
		
	def effCanTrig(self):
		self.effectViable = self.targetExists() and any(minion.name.endswith("Lackey") for minion in self.Game.minionsonBoard(self.ID))
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if any(minion.name.endswith("Lackey") for minion in self.Game.minionsonBoard(self.ID)):
			self.dealsDamage(target, 3)
		
	
class SplittingAxe(Weapon):
	Class, name, description = "Shaman", "Splitting Axe", "Battlecry: Summon copies of your Totems"
	mana, attack, durability, Effects = 4, 3, 2, ""
	name_CN = "分裂战斧"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for minion in self.Game.minionsonBoard(self.ID, race="Totem"):
			self.summon(self.copyCard(minion, self.ID), position=minion.pos+1)
		
	
class Vessina(Minion):
	Class, race, name = "Shaman", "", "Vessina"
	mana, attack, health = 4, 2, 6
	name_CN = "维西纳"
	numTargets, Effects, description = 0, "", "While you're Overloaded, your other minions have +2 Attack"
	index = "Legendary"
	aura = Aura_Vessina
	
	
class Earthquake(Spell):
	Class, school, name = "Shaman", "Nature", "Earthquake"
	numTargets, mana, Effects = 0, 7, ""
	description = "Deal 5 damage to all minions, then deal 2 damage to all minions"
	name_CN = "地震术"
	def text(self): return "%d, %d"%(self.calcDamage(5), self.calcDamage(2))
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(self.Game.minionsonBoard(), self.calcDamage(5))
		self.Game.gathertheDead() #地震术在第一次AOE后会让所有随从结算死亡事件，然后再次对全场随从打2.
		self.dealsDamage(self.Game.minionsonBoard(), self.calcDamage(2))
		
	
class MoguFleshshaper(Minion):
	Class, race, name = "Shaman", "", "Mogu Fleshshaper"
	mana, attack, health = 9, 3, 4
	numTargets, Effects, description = 0, "Rush", "Rush. Costs (1) less for each minion on the battlefield"
	name_CN = "魔古血肉塑造者"
	trigHand = Trig_MoguFleshshaper
	def selfManaChange(self):
		self.mana -= len(self.Game.minionsonBoard())
		
	
class PlagueofFlames(Spell):
	Class, school, name = "Warlock", "Fire", "Plague of Flames"
	numTargets, mana, Effects = 0, 1, ""
	description = "Destroy all your minions. For each one, destroy a random enemy minion"
	name_CN = "火焰之灾祸"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		num = len((ownMinions := self.Game.minionsonBoard(self.ID)))
		self.Game.kill(self, ownMinions)
		if num > 0 and (enemyMinions := self.Game.minionsonBoard(3-self.ID)):
			minions = numpyChoice(enemyMinions, min(num, len(enemyMinions)), replace=False)
			self.Game.kill(self, minions)
		
	
class SinisterDeal(Spell):
	Class, school, name = "Warlock", "", "Sinister Deal"
	numTargets, mana, Effects = 0, 1, ""
	description = "Discover a Lackey"
	name_CN = "邪恶交易"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.discoverNew(comment, lambda: EVILCableRat.lackeys)
		
	
class SupremeArchaeology(Quest):
	Class, school, name = "Warlock", "", "Supreme Archaeology"
	numTargets, mana, Effects = 0, 1, ""
	name_CN = "最最伟大的考古学"
	description = "Quest: Draw 20 cards. Reward: Tome of Origination"
	index = "Legendary"
	numNeeded = 20
	trigBoard = Trig_SupremeArchaeology
	def questEffect(self, game, ID):
		TomeofOrigination(game, ID).replacePower()
		
	
class TomeofOrigination(Power):
	mana, name, numTargets = 2, "Tome of Origination", 0
	description = "Draw a card. It costs (0)"
	name_CN = "源生魔典"
	def effect(self, target=(), choice=0, comment=''):
		card, mana, entersHand = self.Game.Hand_Deck.drawCard(self.ID, initiator=self)
		if entersHand: ManaMod(card, to=0).applies()
		
	
class ExpiredMerchant(Minion):
	Class, race, name = "Warlock", "", "Expired Merchant"
	mana, attack, health = 2, 2, 1
	name_CN = "过期货物专卖商"
	numTargets, Effects, description = 0, "", "Battlecry: Discard your highest Cost card. Deathrattle: Add 2 copies of it to your hand"
	index = "Battlecry"
	deathrattle = Death_ExpiredMerchant
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if indices := pickInds_HighestAttr(self.Game.Hand_Deck.hands[self.ID]):
			card = self.Game.Hand_Deck.discard(self.ID, numpyChoice(indices))[0]
			for trig in self.deathrattles:
				if isinstance(trig, Death_ExpiredMerchant): trig.memory.append(card.getBareInfo())
		
	
class EVILRecruiter(Minion):
	Class, race, name = "Warlock", "", "EVIL Recruiter"
	mana, attack, health = 3, 3, 3
	name_CN = "怪盗征募官"
	numTargets, Effects, description = 1, "", "Battlecry: Destroy a friendly Lackey to summon a 5/5 Demon"
	index = "Battlecry"
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists(self.ID)
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.ID == self.ID and "Lackey" in obj.name and "~Uncollectible" in obj.index and obj.onBoard
		
	def effCanTrig(self): #Friendly minions are always selectable.
		self.effectViable = False
		for minion in self.Game.minionsonBoard(self.ID):
			if minion.name.endswith("Lackey"):
				self.effectViable = True
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for obj in target:
			#假设消灭跟班之后会进行强制死亡结算，把跟班移除之后才召唤
			#假设召唤的恶魔是在EVIL Recruiter的右边，而非死亡的跟班的原有位置
			self.Game.kill(self, obj)
			self.Game.gathertheDead()
			self.summon(EVILDemon(self.Game, self.ID))
		
	
class EVILDemon(Minion):
	Class, race, name = "Warlock", "Demon", "EVIL Demon"
	mana, attack, health = 5, 5, 5
	name_CN = "怪盗恶魔"
	numTargets, Effects, description = 0, "", ""
	index = "Uncollectible"
	
	
class NefersetThrasher(Minion):
	Class, race, name = "Warlock", "", "Neferset Thrasher"
	mana, attack, health = 3, 4, 5
	numTargets, Effects, description = 0, "", "Whenever this attacks, deal 3 damage to your hero"
	name_CN = "尼斐塞特鞭笞者"
	trigBoard = Trig_NefersetThrasher		
	
	
class Impbalming(Spell):
	Class, school, name = "Warlock", "Fel", "Impbalming"
	numTargets, mana, Effects = 1, 4, ""
	description = "Destroy a minion. Shuffle 3 Worthless Imps into your deck"
	name_CN = "小鬼油膏"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.Game.kill(self, target)
		self.shuffleintoDeck([WorthlessImp_Uldum(self.Game, self.ID) for _ in (0, 1, 2)])
		
	
class WorthlessImp_Uldum(Minion):
	Class, race, name = "Warlock", "Demon", "Worthless Imp"
	mana, attack, health = 1, 1, 1
	name_CN = "游荡小鬼"
	numTargets, Effects, description = 0, "", ""
	index = "Uncollectible"
	
	
class DiseasedVulture(Minion):
	Class, race, name = "Warlock", "Beast", "Diseased Vulture"
	mana, attack, health = 4, 3, 5
	numTargets, Effects, description = 0, "", "After your hero takes damage on your turn, summon a random 3-Cost minion"
	name_CN = "染病的兀鹫"
	trigBoard = Trig_DiseasedVulture
	
	
class Riftcleaver(Minion):
	Class, race, name = "Warlock", "Demon", "Riftcleaver"
	mana, attack, health = 6, 7, 5
	name_CN = "裂隙屠夫"
	numTargets, Effects, description = 1, "", "Battlecry: Destroy a minion. Your hero takes damage equal to its health"
	index = "Battlecry"
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj is not self and obj.onBoard
		#不知道连续触发战吼时，第二次是否还会让玩家受到伤害
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for obj in target:
			if not obj.dead:
				damage, game = max(0, obj.health), self.Game
				game.kill(self, obj)
				#不知道这个对于英雄的伤害有无伤害来源。假设没有，和抽牌疲劳伤害类似
				game.scapegoat4(game.heroes[self.ID]).takesDamage(None, damage, "Ability")
		
	
class DarkPharaohTekahn(Minion):
	Class, race, name = "Warlock", "", "Dark Pharaoh Tekahn"
	mana, attack, health = 5, 4, 4
	name_CN = "黑暗法老塔卡恒"
	numTargets, Effects, description = 0, "", "Battlecry: For the rest of the game, your Lackeys are 4/4"
	index = "Battlecry~Legendary"
	trigEffect = DarkPharaohTekahn_Effect
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		DarkPharaohTekahn_Effect(self.Game, self.ID).connect()
		
	
class HacktheSystem(Quest):
	Class, school, name = "Warrior", "", "Hack the System"
	numTargets, mana, Effects = 0, 1, ""
	name_CN = "侵入系统"
	description = "Quest: Attack 5 times with your hero. Reward: Anraphet's Core"
	index = "Legendary"
	numNeeded = 5
	trigBoard = Trig_HacktheSystem
	def questEffect(self, game, ID):
		AnraphetsCore(game, ID).replacePower()
		
	
class AnraphetsCore(Power):
	mana, name, numTargets = 2, "Anraphet's Core", 0
	description = "Summon a 4/3 Golem. After your hero attacks, refresh this"
	name_CN = "安拉斐特之核"
	trigBoard = Trig_AnraphetsCore		
	def available(self, choice=0):
		return not self.chancesUsedUp() and self.Game.space(self.ID) > 0
		
	def effect(self, target=(), choice=0, comment=''):
		self.summon(StoneGolem(self.Game, self.ID))
		
	
class StoneGolem(Minion):
	Class, race, name = "Warrior", "", "Stone Golem"
	mana, attack, health = 3, 4, 3
	name_CN = "石头魔像"
	numTargets, Effects, description = 0, "", ""
	index = "Uncollectible"
	
	
class IntotheFray(Spell):
	Class, school, name = "Warrior", "", "Into the Fray"
	numTargets, mana, Effects = 0, 1, ""
	description = "Give all Taunt minions in your hand +2/+2"
	name_CN = "投入战斗"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant([card for card in self.Game.Hand_Deck.hands[self.ID] if card.category == "Minion" and card.effects["Taunt"] > 0],
						 2, 2, source=IntotheFray, add2EventinGUI=False)
		
	
class FrightenedFlunky(Minion):
	Class, race, name = "Warrior", "", "Frightened Flunky"
	mana, attack, health = 2, 2, 2
	name_CN = "惊恐的仆从"
	numTargets, Effects, description = 0, "Taunt", "Taunt. Battlecry: Discover a Taunt minion"
	index = "Battlecry"
	poolIdentifier = "Taunt Minions as Warrior"
	@classmethod
	def generatePool(cls, pools):
		return genPool_CertainMinionsasClass(pools, "Taunt", cond=lambda card: "Taunt" in card.Effects)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.discoverNew(comment, lambda : self.rngPool("Taunt Minions as "+class4Discover(self)))
		
	
class BloodswornMercenary(Minion):
	Class, race, name = "Warrior", "", "Bloodsworn Mercenary"
	mana, attack, health = 3, 2, 2
	name_CN = "血誓雇佣兵"
	numTargets, Effects, description = 1, "", "Battlecry: Choose a damaged friendly minion. Summon a copy of it"
	index = "Battlecry"
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists(self.ID)
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.ID == self.ID and obj is not self and obj.onBoard and obj.health < obj.health_max
		
	def effCanTrig(self):
		self.effectViable = any(minion.dmgTaken > 0 for minion in self.Game.minionsonBoard(self.ID))
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for obj in target: self.summon(self.copyCard(obj, self.ID))
		
	
class LivewireLance(Weapon):
	Class, name, description = "Warrior", "Livewire Lance", "After your hero attacks, add a Lackey to your hand"
	mana, attack, durability, Effects = 3, 2, 2, ""
	name_CN = "电缆长枪"
	trigBoard = Trig_LivewireLance		
	
	
class RestlessMummy(Minion):
	Class, race, name = "Warrior", "", "Restless Mummy"
	mana, attack, health = 4, 3, 2
	name_CN = "焦躁的木乃伊"
	numTargets, Effects, description = 0, "Rush,Reborn", "Rush, Reborn"
	
	
class PlagueofWrath(Spell):
	Class, school, name = "Warrior", "", "Plague of Wrath"
	numTargets, mana, Effects = 0, 5, ""
	description = "Destroy all damaged minions"
	name_CN = "愤怒之灾祸"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.Game.kill(self, [minion for minion in self.Game.minionsonBoard() if minion.health < minion.health_max])
		
	
class Armagedillo(Minion):
	Class, race, name = "Warrior", "Beast", "Armagedillo"
	mana, attack, health = 6, 4, 7
	name_CN = "铠硕鼠"
	numTargets, Effects, description = 0, "Taunt", "Taunt. At the end of your turn, give all Taunt minions in your hand +2/+2"
	index = "Legendary"
	trigBoard = Trig_Armagedillo		
	
	
class ArmoredGoon(Minion):
	Class, race, name = "Warrior", "", "Armored Goon"
	mana, attack, health = 6, 6, 7
	numTargets, Effects, description = 0, "", "Whenever your hero attacks, gain 5 Armor"
	name_CN = "重甲暴徒"
	trigBoard = Trig_ArmoredGoon		
	
	
class TombWarden(Minion):
	Class, race, name = "Warrior", "Mech", "Tomb Warden"
	mana, attack, health = 8, 3, 6
	name_CN = "陵墓守望者"
	numTargets, Effects, description = 0, "Taunt", "Taunt. Battlecry: Summon a copy of this minion"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if not self.dead: self.summon(self.copyCard(self, self.ID))
		
	


AllClasses_Uldum = [
	ManaAura_GenerousMummy, Aura_PhalanxCommander, Aura_Vessina, Death_JarDealer, Death_KoboldSandtrooper, Death_SerpentEgg,
	Death_InfestedGoblin, Death_BlatantDecoy, Death_KhartutDefender, Death_Octosari, Death_AnubisathWarbringer, Death_SalhetsPride,
	Death_Grandmummy, Death_SahketSapper, Death_ExpiredMerchant, Trig_HighkeeperRa, Trig_DwarvenArchaeologist, Trig_SpittingCamel,
	Trig_HistoryBuff, Trig_ConjuredMirage, Trig_SunstruckHenchman, Trig_DesertObelisk, Trig_MortuaryMachine, Trig_WrappedGolem,
	Trig_UntappedPotential, Trig_CrystalMerchant, Trig_AnubisathDefender, Trig_UnsealtheVault, Trig_PressurePlate,
	Trig_DesertSpear, Trig_RaidtheSkyTemple, Trig_FlameWard, Trig_ArcaneFlakmage, Trig_DuneSculptor, Trig_MakingMummies,
	Trig_BrazenZealot, Trig_MicroMummy, Trig_ActivatetheObelisk, Trig_SandhoofWaterbearer, Trig_HighPriestAmet, Trig_BazaarBurglary,
	Trig_MirageBlade, Trig_WhirlkickMaster, Trig_CorrupttheWaters, Trig_EVILTotem, Trig_MoguFleshshaper, Trig_SupremeArchaeology,
	Trig_NefersetThrasher, Trig_DiseasedVulture, Trig_HacktheSystem, Trig_AnraphetsCore, Trig_LivewireLance, Trig_Armagedillo,
	Trig_ArmoredGoon, HeartofVirnaal_Effect, DarkPharaohTekahn_Effect, BeamingSidekick, JarDealer, MoguCultist, HighkeeperRa,
	Murmy, BugCollector, Locust, DwarvenArchaeologist, Fishflinger, InjuredTolvir, KoboldSandtrooper, NefersetRitualist,
	QuestingExplorer, QuicksandElemental, SerpentEgg, SeaSerpent, SpittingCamel, TempleBerserker, Vilefiend, ZephrystheGreat,
	Candletaker, DesertHare, GenerousMummy, GoldenScarab, HistoryBuff, InfestedGoblin, Scarab_Uldum, MischiefMaker,
	VulperaScoundrel, MysteryChoice, BoneWraith, BodyWrapper, ConjuredMirage, SunstruckHenchman, FacelessLurker, DesertObelisk,
	MortuaryMachine, PhalanxCommander, WastelandAssassin, BlatantDecoy, KhartutDefender, Siamat, SiamatsHeart, SiamatsShield,
	SiamatsSpeed, SiamatsWind, WastelandScorpid, WrappedGolem, Octosari, PitCrocolisk, AnubisathWarbringer, ColossusoftheMoon,
	KingPhaoris, LivingMonument, UntappedPotential, OssirianTear, WorthyExpedition, CrystalMerchant, BEEEES, Bee_Uldum,
	GardenGnome, Treant_Uldum, AnubisathDefender, ElisetheEnlightened, FocusedBurst_Option, DivideandConquer_Option,
	OasisSurger, BefriendtheAncient, DrinktheWater, BefriendtheAncient_Option, DrinktheWater_Option, HiddenOasis,
	VirnaalAncient, Overflow, UnsealtheVault, PharaohsWarmask, PressurePlate, DesertSpear, HuntersPack, HyenaAlpha,
	Hyena_Uldum, RamkahenWildtamer, SwarmofLocusts, ScarletWebweaver, WildBloodstinger, DinotamerBrann, KingKrush_Uldum,
	RaidtheSkyTemple, AscendantScroll, AncientMysteries, FlameWard, CloudPrince, ArcaneFlakmage, DuneSculptor, NagaSandWitch,
	TortollanPilgrim, RenotheRelicologist, PuzzleBoxofYoggSaron, MakingMummies, EmperorWraps, BrazenZealot, MicroMummy,
	SandwaspQueen, Sandwasp, SirFinleyoftheSands, Subdue, SalhetsPride, AncestralGuardian, PharaohsBlessing, TiptheScales,
	ActivatetheObelisk, ObelisksEye, EmbalmingRitual, Penance, SandhoofWaterbearer, Grandmummy, HolyRipple, WretchedReclaimer,
	Psychopomp, HighPriestAmet, PlagueofDeath, BazaarBurglary, AncientBlades, MirageBlade, PharaohCat, PlagueofMadness,
	PlaguedKnife, CleverDisguise, WhirlkickMaster, HookedScimitar, SahketSapper, BazaarMugger, ShadowofDeath, Shadow,
	AnkatheBuried, CorrupttheWaters, HeartofVirnaal, TotemicSurge, EVILTotem, SandstormElemental, PlagueofMurlocs,
	WeaponizedWasp, SplittingAxe, Vessina, Earthquake, MoguFleshshaper, PlagueofFlames, SinisterDeal, SupremeArchaeology,
	TomeofOrigination, ExpiredMerchant, EVILRecruiter, EVILDemon, NefersetThrasher, Impbalming, WorthlessImp_Uldum,
	DiseasedVulture, Riftcleaver, DarkPharaohTekahn, HacktheSystem, AnraphetsCore, StoneGolem, IntotheFray, FrightenedFlunky,
	BloodswornMercenary, LivewireLance, RestlessMummy, PlagueofWrath, Armagedillo, ArmoredGoon, TombWarden, 
]

for class_ in AllClasses_Uldum:
	if issubclass(class_, Card):
		class_.index = "ULDUM" + ("~" if class_.index else '') + class_.index