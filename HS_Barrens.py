from Parts_ConstsFuncsImports import *
from Parts_CardTypes import *
from Parts_TrigsAuras import *

from HS_AcrossPacks import Frog, SilverHandRecruit, WaterElemental_Basic, DreamCards, Adventurers

def panda_Show2TransformReturn(game, GUI, initiator, cards, newCards):
	para = GUI.PARALLEL()
	for card in cards:
		para.append(GUI.LERP_PosHpr(card.btn.np, pos=(3, -5 if GUI.heroeZones[card.ID].y < 0 else 5, 20),
									duration=0.3, startHpr=(0, 0, 0), hpr=(0, 0, 0)))
	GUI.seqHolder[-1].append(para)
	GUI.seqHolder[-1].append(GUI.WAIT(0.4))
	for card, newCard in zip(cards, newCards):
		game.transform(card, newCard, summoner=type(initiator))
	GUI.seqHolder[-1].append(GUI.WAIT(1.3))
	GUI.handZones[1].placeCards()
	GUI.handZones[2].placeCards()


"""Auras"""
class ManaAura_BarrensTrapper(ManaAura):
	by = -1
	def applicable(self, target): return target.ID == self.keeper.ID and target.deathrattles

class ManaAura_TaintheartTormenter(ManaAura):
	by = +2
	def applicable(self, target): return target.ID != self.keeper.ID and target.category == "Spell"

class ManaAura_ArcaneLuminary(ManaAura):
	by, lowerbound = -2, 1
	def applicable(self, target): return target.ID == self.keeper.ID and target.card

class ManaAura_RazormaneBattleguard(ManaAura_1UsageEachTurn):
	def auraAppears(self):
		game, ID = self.keeper.Game, self.keeper.ID
		if game.turn == ID and not any(card.index.endswith("~Taunt") for card in game.Counters.cardsPlayedEachTurn[ID][-1]):
			self.aura = GameManaAura_RazormaneBattleguard(game, ID)
			self.aura.auraAppears()
		add2ListinDict(self, game.trigsBoard[ID], "TurnStarts")


class ManaAura_LadyAnacondra(ManaAura):
	by = -2
	def applicable(self, target): return target.ID == self.keeper.ID and target.school == "Nature"


class Aura_WaterMoccasin(Aura_Conditional):
	signals, effGain, targets = ("MinionAppears", "MinionDisappears"), "Poisonous", "Self"
	def whichWay(self): #Decide the aura turns on(1) or off(-1), or does nothing(0)
		otherMinions = self.keeper.Game.minionsonBoard(self.keeper.ID, self.keeper)
		if otherMinions and self.on: return -1
		elif not otherMinions and not self.on: return 1
		else: return 0

	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject.ID == self.keeper.ID and subject != self


"""Trigs"""
#假设是随从受伤时触发，不是受伤之后触发
class Frenzy(TrigBoard):
	signals, oneTime = ("MinionTakesDmg", ), True
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and target == self.keeper and target.health > 0 and not target.dead
		
	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrig(signal, ID, subject, target, number, comment):
			btn, GUI = self.keeper.btn, self.keeper.Game.GUI
			if btn and "SpecTrig" in btn.icons:
				btn.icons["SpecTrig"].trigAni()
			self.keeper.losesTrig(self)
			self.effect(signal, ID, subject, target, number, comment)
			

#So far the cards that upgrade when Mana Crystals are enough are all spells
class Trig_ForgeUpgrade(TrigHand):
	signals = ("ManaXtlsCheck", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.inHand and ID == self.keeper.ID \
			   and self.keeper.Game.Manas.manasUpper[self.keeper.ID] >= type(self.keeper).upgradeMana

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		card = self.keeper
		newCard = type(card).upgradedVersion(card.Game, card.ID)
		newCard.inheritEnchantmentsfrom(card)
		card.Game.Hand_Deck.replaceCardinHand(card, newCard, calcMana=True)


class Trig_FarWatchPost(TrigBoard):
	signals = ("CardEntersHand", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject.ID != self.keeper.ID and comment == "byDrawing"

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if target[0].mana < 10: ManaMod(target[0], by=+1).applies()
		
		
class Trig_LushwaterScout(TrigBoard):
	signals = ("MinionSummoned", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject.ID == self.keeper.ID and subject != self.keeper and "Murloc" in subject.race

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.giveEnchant(subject, 1, 0, effGain="Rush", name=LushwaterScout)


class Trig_OasisThrasher(Frenzy):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.dealsDamage(self.keeper.heroes[3-self.keeper.ID], 3)
		

class Trig_Peon(Frenzy):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.addCardtoHand(numpyChoice(self.rngPool(self.keeper.Game.heroes[self.keeper.ID].Class + " Spells")), self.keeper.ID)
			

class Trig_CrossroadsGossiper(TrigBoard):
	signals = ("SecretRevealed", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.keeper.ID and self.keeper.onBoard

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.giveEnchant(self.keeper, statEnchant=Enchantment_Cumulative(2, 2, name=CrossroadsGossiper))


class Trig_MorshanWatchPost(TrigBoard):
	signals = ("MinionBeenPlayed", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject.ID != self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.summon(WatchfulGrunt(self.keeper.Game, self.keeper.ID))


class Trig_SunwellInitiate(Frenzy):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.giveEnchant(self.keeper, effGain="Divine Shield", name=SunwellInitiate)


class Trig_BlademasterSamuro(Frenzy):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if (damage := self.keeper.attack) > 0:
			targets = self.keeper.Game.minionsonBoard(3-self.keeper.ID)
			self.keeper.AOE_Damage(targets, [damage]*len(targets))


class Trig_CrossroadsWatchPost(TrigBoard):
	signals = ("SpellPlayed", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject.ID != self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.AOE_GiveEnchant(self.keeper.Game.minionsonBoard(self.keeper.ID),
									statEnchant=Enchantment_Cumulative(1, 1, CrossroadsWatchPost))
		

class Trig_GruntledPatron(Frenzy):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.summon(GruntledPatron(self.keeper.Game, self.keeper.ID))


class Trig_SpiritHealer(TrigBoard):
	signals = ("SpellBeenPlayed", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if minions := self.keeper.Game.minionsonBoard[ID]:
			self.keeper.giveEnchant(numpyChoice(minions), statEnchant=Enchantment_Cumulative(0, 2, name=SpiritHealer))


class Trig_BarrensBlacksmith(Frenzy):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.AOE_GiveEnchant(self.keeper.Game.minionsonBoard(self.keeper.ID, self.keeper), 2, 2, name=BarrensBlacksmith)


class Trig_GoldRoadGrunt(Frenzy):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.giveHeroAttackArmor(self.keeper.ID, armor=number)


class Trig_RazormaneRaider(Frenzy):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if objs := self.keeper.Game.charsAlive(3-self.keeper.ID):
			self.keeper.Game.battle(self.keeper, numpyChoice(objs), verifySelectable=False, useAttChance=False, resolveDeath=False)


class Trig_TaurajoBrave(Frenzy):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if minions := self.keeper.Game.minionsAlive(3 - self.keeper.ID):
			self.keeper.Game.killMinion(self.keeper, numpyChoice(minions))


class Trig_GuffRunetotem(TrigBoard):
	signals = ("SpellBeenPlayed", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject.ID == self.keeper.ID and subject.school == "Nature"

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if minions := self.keeper.Game.minionsonBoard(self.keeper.ID, self.keeper):
			self.keeper.giveEnchant(numpyChoice(minions), statEnchant=Enchantment_Cumulative(2, 2, name=GuffRunetotem))


class Trig_PlaguemawtheRotting(TrigBoard):
	signals = ("MinionDied", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and target != self.keeper and target.ID == self.keeper.ID and target.effects["Taunt"] > 0#Technically, minion has to disappear before dies. But just in case.

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		Copy = type(target)(self.keeper.Game, self.keeper.ID)
		Copy.effects["Taunt"] = 0
		self.keeper.summon(Copy)


class Trig_DruidofthePlains(Frenzy):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.transform(self.keeper, DruidofthePlains_Taunt(self.keeper.Game, self.keeper.ID))


class Trig_SunscaleRaptor(Frenzy):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		game = self.keeper.Game
		if self.keeper.onBoard: newAtt, newHealth = self.keeper.attack + 2, self.keeper.health + 1
		else: newAtt, newHealth = self.keeper.attack_0 + 2, self.keeper.health_0 + 1
		newIndex = "THE_BARRENS~Hunter~Minion~1~%d~%d~Beast~Sunscale Raptor~Uncollectible"%(newAtt, newHealth)
		subclass = type("SunscaleRaptor__%d_%d"%(newAtt, newHealth), (SunscaleRaptor, ),
						{"attack": newAtt, "health": newHealth, "index": newIndex}
						)
		self.keeper.shuffleintoDeck(subclass(game, self.keeper.ID))


class Trig_KolkarPackRunner(TrigBoard):
	signals = ("SpellBeenPlayed", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject.ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.summon(SwiftHyena(self.keeper.Game, self.keeper.ID))


class Trig_ProspectorsCaravan(TrigBoard):
	signals = ("TurnStarts", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.AOE_GiveEnchant([card for card in self.keeper.Game.Hand_Deck.hands[self.keeper.ID] if card.category == "Minion"], 
									statEnchant=Enchantment_Cumulative(1, 1, name=ProspectorsCaravan), add2EventinGUI=False)
		

class Trig_TavishStormpike(TrigBoard):
	signals = ("MinionAttackedHero", "MinionAttackedMinion", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject.ID == self.keeper.ID and "Beast" in subject.race

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.try_SummonfromDeck(func=lambda card: "Beast" in card.race and card.mana == subject.mana - 1)
		

class Trig_OasisAlly(Trig_Secret):
	signals = ("MinionAttacksMinion", "HeroAttacksMinion", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):  #target here holds the actual target object
		#The target has to a friendly minion and there is space on board to summon minions.
		return self.keeper.ID != self.keeper.Game.turn and target[0].category == "Minion" and target[0].ID == self.keeper.ID and self.keeper.Game.space(self.keeper.ID) > 0

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.summon(WaterElemental_Basic(self.keeper.Game, self.keeper.ID))


class Trig_Rimetongue(TrigBoard):
	signals = ("SpellBeenPlayed", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject.ID == self.keeper.ID and subject.school == "Frost"

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.summon(FrostedElemental(self.keeper.Game, self.keeper.ID))


class Trig_FrostedElemental(TrigBoard):
	signals = ("MinionTakesDmg", "HeroTakesDmg", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.keeper

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.freeze(target)


class Trig_GallopingSavior(Trig_Secret):
	signals = ("MinionBeenPlayed", "SpellBeenPlayed", "WeaponBeenPlayed", "HeroBeenPlayed", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		secret = self.keeper
		return secret.ID != secret.Game.turn and subject.ID != secret.ID \
			   and len(secret.Game.Counters.cardsPlayedEachTurn[subject.ID][-1]) > 2 \
				and secret.Game.space(secret.ID)

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.summon(HolySteed(self.keeper.Game, self.keeper.ID))


class Trig_SoldiersCaravan(TrigBoard):
	signals = ("TurnStarts", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.summon([SilverHandRecruit(self.keeper.Game, self.keeper.ID) for _ in (0, 1)], relative="<>")


class Trig_SwordoftheFallen(TrigBoard):
	signals = ("HeroAttackedMinion", "HeroAttackedHero", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.keeper.Game.heroes[self.keeper.ID] and self.keeper.onBoard

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.Game.Secrets.deploySecretsfromDeck(self.keeper.ID, initiator=self.keeper)


class Trig_CarielRoame(TrigBoard):
	signals = ("MinionAttackingMinion", "MinionAttackingHero", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.keeper and self.keeper.onBoard

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		for card in self.keeper.Game.Hand_Deck.hands[self.keeper.ID]:
			if card.school == "Holy": ManaMod(card, by=-1).applies()


class Trig_VeteranWarmedic(TrigBoard):
	signals = ("SpellBeenPlayed", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject.ID == self.keeper.ID and subject.school == "Holy"

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.summon(BattlefieldMedic(self.keeper.Game, self.keeper.ID))


class Trig_SoothsayersCaravan(TrigBoard):
	signals = ("TurnStarts", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.keeper
		if spells := [card for card in minion.Game.Hand_Deck.decks[3-minion.ID] if card.category == "Spell"]:
			minion.addCardtoHand(numpyChoice(spells).selfCopy(minion.ID, minion), minion.ID)


class Trigger_PowerWordFortitude(TrigHand):
	signals = ("CardLeavesHand", "CardEntersHand")
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.inHand and ((target[0] if signal == "CardEntersHand" else target).ID == self.keeper.ID)

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.Game.Manas.calcMana_Single(self.keeper)


class Trig_ParalyticPoison(TrigBoard):
	signals = ("BattleStarted", "BattleFinished", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.keeper.Game.heroes[self.keeper.ID] and self.keeper.onBoard

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if signal == "BattleStarted": subject.getsEffect("Immune")
		else: subject.losesEffect("Immune")


class Trig_SwapBackPowerAfter2Uses(Trig_Countdown):
	signals, counter = ("HeroUsedAbility", ), 2
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.keeper

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if self.counter < 1:
			self.keeper.powerReplaced.ID = self.keeper.ID
			self.keeper.powerReplaced.replacePower()


class Trig_EfficientOctobot(Frenzy):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		for card in self.keeper.Game.Hand_Deck.hands[self.keeper.ID]:
			ManaMod(card, by=-1).applies()


class Trig_SilverleafPoison(TrigBoard):
	signals = ("HeroAttackedMinion", "HeroAttackedHero", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject.ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.Game.Hand_Deck.drawCard(self.keeper.ID)


class Trig_FieldContact(TrigBoard):
	signals = ("MinionBeenPlayed", "SpellBeenPlayed", "WeaponBeenPlayed", "HeroBeenPlayed", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject.ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.Game.Hand_Deck.drawCard(self.keeper.ID)


class Trig_SwinetuskShank(TrigBoard):
	signals = ("SpellBeenPlayed", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.keeper.ID and self.keeper.onBoard and "Poison" in subject.name

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.giveEnchant(self.keeper, statEnchant=Enchantment_Cumulative(0, 1, name=SwinetuskShank))


class Trig_FiremancerFlurgl(TrigBoard):
	signals = ("MinionBeenPlayed", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject.ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		targets = self.keeper.Game.minionsonBoard(3-self.keeper.ID) + [self.keeper.Game.heroes[3-self.keeper.ID]]
		self.keeper.AOE_Damage(targets, [1]*len(targets))


class Trig_TinyfinsCaravan(TrigBoard):
	signals = ("TurnStarts", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.drawCertainCard(lambda card: "Murloc" in card.race)


class Trig_ApothecarysCaravan(TrigBoard):
	signals = ("TurnStarts", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.try_SummonfromDeck(func=lambda card: card.category == "Minion" and card.mana == 1)
		

class Trig_TamsinRoame(TrigBoard):
	signals = ("SpellPlayed", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject.ID == self.keeper.ID and subject.school == "Shadow" and number > 0

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		Copy = subject.selfCopy(self.keeper.ID, self.keeper)
		self.keeper.addCardtoHand(Copy, self.keeper.ID)
		if Copy.inHand: ManaMod(Copy, to=0).applies()


class Trig_BurningBladePortal(TrigBoard):
	signals = ("TurnEnds", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.keeper
		minion.summon([ImpFamiliar(minion.Game, minion.ID) for i in range(6)], relative="<>")


class Trig_BarrensScavenger(TrigHand):
	signals = ("", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.inHand and ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.Game.Manas.calcMana_Single(self.keeper)


class Trig_WarsongEnvoy(Frenzy):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		num = 1 if self.keeper.Game.heroes[self.keeper.ID].dmgTaken > 0 else 0
		num += sum(minion.health < minion.health_max for minion in self.keeper.Game.minionsonBoard(self.keeper.ID))
		self.keeper.giveEnchant(self.keeper, num, 0, name=WarsongEnvoy)


class Trig_Rokara(TrigBoard):
	signals = ("MinionAttackedHero", "MinionAttackedMinion", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject.ID == self.keeper.ID and subject.health > 0 and not subject.dead

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.giveEnchant(subject, statEnchant=Enchantment_Cumulative(1, 1, name=Rokara))


class Trig_OutridersAxe(TrigBoard):
	signals = ("HeroAttackedMinion", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.keeper.Game.heroes[self.keeper.ID] and self.keeper.onBoard and target.category == "Minion" and (target.health < 1 or target.dead)

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.Game.Hand_Deck.drawCard(self.keeper.ID)


class Trig_WhirlingCombatant(Frenzy):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		targets = self.keeper.Game.minionsonBoard(self.keeper.ID, self.keeper) + self.keeper.Game.minionsonBoard(3 - self.keeper.ID)
		self.keeper.AOE_Damage(targets, [1] * len(targets))


class Trig_StonemaulAnchorman(Frenzy):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.Game.Hand_Deck.drawCard(self.keeper.ID)


class Trig_MeetingStone(TrigBoard):
	signals = ("TurnEnds", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.addCardtoHand(numpyChoice(Adventurers), self.keeper.ID)


class Trig_SleepingNaralex(TrigBoard):
	signals = ("TurnEnds", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and ID == self.keeper.ID  #会在我方回合开始时进行苏醒

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.addCardtoHand(numpyChoice(DreamCards), self.keeper.ID)

class Trig_SleepingNaralex_Countdown(Trig_Countdown):
	signals = ("TurnStarts", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and ID == self.keeper.ID  #会在我方回合开始时进行苏醒

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if self.counter < 1:
			self.keeper.Game.transform(self.keeper, self.keeper.minionInside, firstTime=False)
			self.keeper.minionInside.awakenEffect()


class Trig_DeviateDreadfang(TrigBoard):
	signals = ("SpellBeenPlayed", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject.ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.summon(DeviateViper(self.keeper.Game, self.keeper.ID))


class Trig_SindoreiScentfinder(Frenzy):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.summon([SwiftHyena(self.keeper.Game, self.keeper.ID) for i in (0, 1, 2, 3)], relative="<>")


class Trig_Floecaster(TrigHand): #"HeroAppears" only is sent when hero is replaced. It's equivalent to "HeroDisappars" (Although don't have this)
	signals = ("MinionAppears", "MinionDisappears", "HeroAppears", "CharEffectCheck", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.inHand and (target if "Disappears" in signal else subject).ID != self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.Game.Manas.calcMana_Single(self.keeper)


class Trig_JudgmentofJustice(Trig_Secret):
	signals = ("MinionAttackingMinion", "MinionAttackingHero", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.ID != self.keeper.Game.turn and subject.ID != self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		subject.statReset(1, 1, source=type(self))


class Trig_WailingVapor(TrigBoard):
	signals = ("MinionBeenPlayed", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject.ID == self.keeper.ID and subject != self.keeper

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.giveEnchant(self.keeper, statEnchant=Enchantment_Cumulative(1, 0, name=WailingVapor))


class Trig_StealerofSouls(TrigBoard):
	signals = ("CardEntersHand", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and target[0].ID == self.keeper.ID and comment == "byDrawing"

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.giveEnchant(target[0], effGain="Cost Health Instead", name=StealerofSouls)


class Trig_WhetstoneHatchet(TrigBoard):
	signals = ("HeroAttackedMinion", "HeroAttackedHero", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.keeper.Game.heroes[self.keeper.ID] and self.keeper.onBoard

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if minions := [card for card in self.keeper.Game.Hand_Deck.hands[self.keeper.ID] if card.category == "Minion"]:
			self.keeper.giveEnchant(numpyChoice(minions), 1, 0, name=WhetstoneHatchet, add2EventinGUI=False)


class Trig_KreshLordofTurtling(Frenzy):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.giveHeroAttackArmor(self.keeper.ID, armor=8)


class Spell_Forge(Spell):
	upgradeMana, upgradedVersion = 5, None
	trigHand = Trig_ForgeUpgrade
	def entersHand(self):
		if upgrade := self.Game.Manas.manasUpper[self.ID] >= type(self).upgradeMana:
			card = type(self).upgradedVersion(self.Game, self.ID)
		else: card = self
		card.inHand = True
		card.onBoard = card.inDeck = False
		card.enterHandTurn = card.Game.numTurn
		if not upgrade:
			for trig in card.trigsHand: trig.connect()
		return card

#So far the cards that upgrade when Mana Crystals are enough are all spells


"""Deathrattles"""
class Death_DeathsHeadCultist(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.restoresHealth(self.keeper.heroes[self.keeper.ID], self.keeper.calcHeal(4))

class Death_DarkspearBerserker(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.dealsDamage(self.keeper.heroes[3-self.keeper.ID], 5)

class Death_BurningBladeAcolyte(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.summon(Demonspawn(self.keeper.Game, self.keeper.ID))

class Death_Tuskpiercer(Deathrattle_Weapon):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.drawCertainCard(lambda card: card.category == "Minion" and card.deathrattles)

class Death_Razorboar(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.try_SummonfromHand(func=lambda card: card.category == "Minion" and card.deathrattles and card.mana < 4)
		
class Death_RazorfenBeastmaster(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.try_SummonfromHand(func=lambda card: card.category == "Minion" and card.deathrattles and card.mana < 5)
		
class Death_ThickhideKodo(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.giveHeroAttackArmor(self.keeper.ID, armor=5)

class Death_NorthwatchSoldier(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if self.savedObj:
			self.savedObj.ID = self.keeper.ID
			self.savedObj.whenEffective()

	def selfCopy(self, recipient):
		trig = type(self)(recipient)
		trig.secret = self.savedObj.selfCopy(self.keeper.ID, None)
		return trig

	def assistCreateCopy(self, Copy):
		Copy.savedObj = self.savedObj.createCopy(Copy.Game)


class Death_LightshowerElemental(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		keeper = self.keeper
		targets, heal = keeper.Game.minionsonBoard(keeper.ID) + [keeper.Game.heroes[keeper.ID]], keeper.calcHeal(8)
		keeper.AOE_Heal(targets, [heal]*len(targets))

class Death_ApothecaryHelbrim(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.addCardtoHand(numpyChoice(self.rngPool("Poisons")), self.keeper.ID)

class Death_SpawnpoolForager(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.summon(DiremuckTinyfin(self.keeper.Game, self.keeper.ID))

class Death_KabalOutfitter(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if minions := self.keeper.Game.minionsonBoard(self.keeper.ID, self.keeper):
			self.keeper.giveEnchant(numpyChoice(minions), 1, 1, name=KabalOutfitter)

class Death_DevouringEctoplasm(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.summon(numpyChoice(Adventurers)(self.keeper.Game, self.keeper.ID))

class Death_Felrattler(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		targets = self.keeper.Game.minionsonBoard(1) + self.keeper.Game.minionsonBoard(2)
		self.keeper.AOE_Damage(targets, [1]*len(targets))

class Death_FangboundDruid(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if cards := self.keeper.findCards4ManaReduction(lambda card: "Beast" in card.race):
			ManaMod(numpyChoice(cards), by=-2).applies()

class Death_SeedcloudBuckler(Deathrattle_Weapon):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.AOE_GiveEnchant(self.keeper.Game.minionsonBoard(self.keeper.ID), effGain="Divine Shield", name=SeedcloudBuckler)
		
class Death_KreshLordofTurtling(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.equipWeapon(TurtleSpike(self.keeper.Game, self.keeper.ID))


"""Neutral Cards"""
class KindlingElemental(Minion):
	Class, race, name = "Neutral", "Elemental", "Kindling Elemental"
	mana, attack, health = 1, 1, 2
	index = "THE_BARRENS~Neutral~Minion~1~1~2~Elemental~Kindling Elemental~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Your next Elemental costs (1) less"
	name_CN = "火光元素"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		GameManaAura_KindlingElemental(self.Game, self.ID).auraAppears()


class FarWatchPost(Minion):
	Class, race, name = "Neutral", "", "Far Watch Post"
	mana, attack, health = 2, 2, 3
	index = "THE_BARRENS~Neutral~Minion~2~2~3~~Far Watch Post"
	requireTarget, effects, description = False, "Can't Attack", "Can't attack. After your opponent draws a card, it costs (1) more (up to 10)"
	name_CN = "前沿哨所"
	trigBoard = Trig_FarWatchPost


class HecklefangHyena(Minion):
	Class, race, name = "Neutral", "Beast", "Hecklefang Hyena"
	mana, attack, health = 2, 2, 4
	index = "THE_BARRENS~Neutral~Minion~2~2~4~Beast~Hecklefang Hyena~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Deal 3 damage to your hero"
	name_CN = "乱齿土狼"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.dealsDamage(self.Game.heroes[self.ID], 3)


class LushwaterMurcenary(Minion):
	Class, race, name = "Neutral", "Murloc", "Lushwater Murcenary"
	mana, attack, health = 2, 3, 2
	index = "THE_BARRENS~Neutral~Minion~2~3~2~Murloc~Lushwater Murcenary~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: If you control a Murloc, gain +1/+1"
	name_CN = "甜水鱼人斥侯"
	
	def effCanTrig(self):
		self.effectViable = any("Murloc" in minion.race for minion in self.Game.minionsonBoard(self.ID))

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if any("Murloc" in minion.race and minion != self for minion in self.Game.minionsonBoard(self.ID)):
			self.giveEnchant(self, 1, 1, name=LushwaterMurcenary)
	
	
class LushwaterScout(Minion):
	Class, race, name = "Neutral", "Murloc", "Lushwater Scout"
	mana, attack, health = 2, 1, 3
	index = "THE_BARRENS~Neutral~Minion~2~1~3~Murloc~Lushwater Scout"
	requireTarget, effects, description = False, "", "After you summon a Murloc, give it +1 Attack and Rush"
	name_CN = "甜水鱼人斥侯"
	trigBoard = Trig_LushwaterScout


class OasisThrasher(Minion):
	Class, race, name = "Neutral", "Beast", "Oasis Thrasher"
	mana, attack, health = 2, 2, 3
	index = "THE_BARRENS~Neutral~Minion~2~2~3~Beast~Oasis Thrasher~Frenzy"
	requireTarget, effects, description = False, "", "Frenzy: Deal 3 damage to the enemy hero"
	name_CN = "绿洲长尾鳄"
	trigBoard = Trig_OasisThrasher


class Peon(Minion):
	Class, race, name = "Neutral", "", "Peon"
	mana, attack, health = 2, 2, 3
	index = "THE_BARRENS~Neutral~Minion~2~2~3~~Peon~Frenzy"
	requireTarget, effects, description = False, "", "Frenzy: Add a random spell from your class to your hand"
	name_CN = "苦工"
	trigBoard = Trig_Peon
	poolIdentifier = "Druid Spells"
	@classmethod
	def generatePool(cls, pools):
		return [Class + " Spells" for Class in pools.Classes], \
			   [[card for card in cards if card.category == "Spell"] for cards in pools.ClassCards.values()]
	


class TalentedArcanist(Minion):
	Class, race, name = "Neutral", "", "Talented Arcanist"
	mana, attack, health = 2, 1, 3
	index = "THE_BARRENS~Neutral~Minion~2~1~3~~Talented Arcanist~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Your next spell this turn has Spell Damage +2"
	name_CN = "精明的奥术师"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.heroes[self.ID].getsEffect("Spell Damage", 2)
		TalentedArcanist_Effect(self.Game, self.ID).connect()


class ToadoftheWilds(Minion):
	Class, race, name = "Neutral", "Beast", "Toad of the Wilds"
	mana, attack, health = 2, 2, 2
	index = "THE_BARRENS~Neutral~Minion~2~2~2~Beast~Toad of the Wilds~Taunt~Battlecry"
	requireTarget, effects, description = False, "Taunt", "Taunt. Battlecry: If you're holding a Nature spell, gain +2 Health"
	name_CN = "狂野蟾蜍"
	
	def effCanTrig(self):
		self.effectViable = any(card.category == "Spell" and card.school == "Nature" for card in self.Game.Hand_Deck.hands[self.ID])
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if any(card.category == "Spell" and card.school == "Nature" for card in self.Game.Hand_Deck.hands[self.ID]):
			self.giveEnchant(self, 0, 2, name=ToadoftheWilds)


class BarrensTrapper(Minion):
	Class, race, name = "Neutral", "", "Barrens Trapper"
	mana, attack, health = 3, 2, 4
	index = "THE_BARRENS~Neutral~Minion~3~2~4~~Barrens Trapper"
	requireTarget, effects, description = False, "", "Your Deathrattle cards cost (1) less"
	name_CN = "贫瘠之地诱捕者"
	aura = ManaAura_BarrensTrapper


class CrossroadsGossiper(Minion):
	Class, race, name = "Neutral", "", "Crossroads Gossiper"
	mana, attack, health = 3, 4, 3
	index = "THE_BARRENS~Neutral~Minion~3~4~3~~Crossroads Gossiper~Battlecry"
	requireTarget, effects, description = False, "", "After a friendly Secret is revealed, gain +2/+2"
	name_CN = "十字路口大嘴巴"
	trigBoard = Trig_CrossroadsGossiper


class DeathsHeadCultist(Minion):
	Class, race, name = "Neutral", "Quilboar", "Death's Head Cultist"
	mana, attack, health = 3, 2, 4
	index = "THE_BARRENS~Neutral~Minion~3~2~4~Quilboar~Death's Head Cultist~Taunt~Deathrattle"
	requireTarget, effects, description = False, "Taunt", "Deathrattle: Restore 4 Health to your hero"
	name_CN = "亡首教徒"
	deathrattle = Death_DeathsHeadCultist


class HogRancher(Minion):
	Class, race, name = "Neutral", "", "Hog Rancher"
	mana, attack, health = 3, 3, 2
	index = "THE_BARRENS~Neutral~Minion~3~3~2~~Hog Rancher~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Summon a 2/1 Hog with Rush"
	name_CN = "放猪牧人"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon(Hog(self.Game, self.ID))


class Hog(Minion):
	Class, race, name = "Neutral", "Beast", "Hog"
	mana, attack, health = 1, 2, 1
	index = "THE_BARRENS~Neutral~Minion~1~2~1~Beast~Hog~Rush~Uncollectible"
	requireTarget, effects, description = False, "Rush", "Rush"
	name_CN = "小猪"


class HordeOperative(Minion):
	Class, race, name = "Neutral", "", "Horde Operative"
	mana, attack, health = 3, 3, 4
	index = "THE_BARRENS~Neutral~Minion~3~3~4~~Horde Operative~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Copy your opponent's secrets and put them into play"
	name_CN = "部落特工"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		#假设先复制最早入场的奥秘
		secretHD = self.Game.Secrets
		for secret in secretHD.secrets[3-self.ID]:
			if secretHD.areaNotFull(self.ID):
				if not secretHD.sameSecretExists(secret, self.ID):
					secret.selfCopy(self.ID, self).whenEffective()
			else: break


class Mankrik(Minion):
	Class, race, name = "Neutral", "", "Mankrik"
	mana, attack, health = 3, 3, 4
	index = "THE_BARRENS~Neutral~Minion~3~3~4~~Mankrik~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: Help Mankrik find his wife! She was last seen somewhere in your deck"
	name_CN = "曼克里克"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.shuffleintoDeck(OlgraMankriksWife(self.Game, self.ID))


class OlgraMankriksWife(Spell):
	Class, school, name = "Neutral", "", "Olgra, Mankrik's Wife"
	requireTarget, mana, effects = False, 3, ""
	index = "THE_BARRENS~Neutral~Spell~3~~Olgra, Mankrik's Wife~Uncollectible~Casts When Drawn"
	description = "Casts When Drawn. Summon a 3/10 Mankrik, who immediately attaks the enemy hero"
	name_CN = "奥格拉，曼克里克的妻子"
	def available(self):
		return self.Game.space(self.ID) > 0

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		minion = MankrikConsumedbyHatred(self.Game, self.ID)
		self.summon(minion)
		if minion.onBoard and minion.health > 0 and not minion.dead:
			self.Game.battle(minion, self.Game.heroes[3-self.ID], verifySelectable=False, useAttChance=False)


class MankrikConsumedbyHatred(Minion):
	Class, race, name = "Neutral", "", "Mankrik, Consumed by Hatred"
	mana, attack, health = 5, 3, 7
	index = "THE_BARRENS~Neutral~Minion~5~3~7~~Mankrik, Consumed by Hatred~Legendary~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "曼克里克"


class MorshanWatchPost(Minion):
	Class, race, name = "Neutral", "", "Mor'shan Watch Post"
	mana, attack, health = 3, 3, 4
	index = "THE_BARRENS~Neutral~Minion~3~3~4~~Mor'shan Watch Post"
	requireTarget, effects, description = False, "Can't Attack", "Can't attack. After your opponent plays a minion, summon a 2/2 Grunt"
	name_CN = "莫尔杉哨所"
	trigBoard = Trig_MorshanWatchPost


class WatchfulGrunt(Minion):
	Class, race, name = "Neutral", "", "Watchful Grunt"
	mana, attack, health = 2, 2, 2
	index = "THE_BARRENS~Neutral~Minion~2~2~2~~Watchful Grunt~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "警觉的步兵"


class RatchetPrivateer(Minion):
	Class, race, name = "Neutral", "Pirate", "Ratchet Privateer"
	mana, attack, health = 3, 4, 3
	index = "THE_BARRENS~Neutral~Minion~3~4~3~Pirate~Ratchet Privateer~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Give your weapon +1 Attack"
	name_CN = "棘齿城私掠者"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if weapon := self.Game.availableWeapon(self.ID): self.giveEnchant(weapon, 1, 0, RatchetPrivateer)


class SunwellInitiate(Minion):
	Class, race, name = "Neutral", "", "Sunwell Initiate"
	mana, attack, health = 3, 3, 4
	index = "THE_BARRENS~Neutral~Minion~3~3~4~~Sunwell Initiate~Frenzy"
	requireTarget, effects, description = False, "", "Frenzy: Gain Divine Shield"
	name_CN = "太阳之井新兵"
	trigBoard = Trig_SunwellInitiate


class VenomousScorpid(Minion):
	Class, race, name = "Neutral", "Beast", "Venomous Scorpid"
	mana, attack, health = 3, 1, 3
	index = "THE_BARRENS~Neutral~Minion~3~1~3~Beast~Venomous Scorpid~Poisonous~Battlecry"
	requireTarget, effects, description = False, "Poisonous", "Poisonous. Battlecry: Discover a spell"
	name_CN = "剧毒魔蝎"
	poolIdentifier = "Druid Spells"
	@classmethod
	def generatePool(cls, pools):
		return [Class + " Spells" for Class in pools.Classes], \
			   [[card for card in cards if card.category == "Spell"] for cards in pools.ClassCards.values()]

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverandGenerate(VenomousScorpid, comment, lambda : self.rngPool(classforDiscover(self) + " Spells"))


class BlademasterSamuro(Minion):
	Class, race, name = "Neutral", "", "Blademaster Samuro"
	mana, attack, health = 4, 1, 6
	index = "THE_BARRENS~Neutral~Minion~4~1~6~~Blademaster Samuro~Rush~Frenzy~Legendary"
	requireTarget, effects, description = False, "Rush", "Rush. Frenzy: Deal damage equal to this minion's Attack equal to all enemy minions"
	name_CN = "剑圣萨穆罗"
	trigBoard = Trig_BlademasterSamuro


class CrossroadsWatchPost(Minion):
	Class, race, name = "Neutral", "", "Crossroads Watch Post"
	mana, attack, health = 4, 4, 6
	index = "THE_BARRENS~Neutral~Minion~4~4~6~~Crossroads Watch Post"
	requireTarget, effects, description = False, "Can't Attack", "Can't attack. Whenever you opponent casts a spell, give your minions +1/+1"
	name_CN = "十字路口哨所"
	trigBoard = Trig_CrossroadsWatchPost


class DarkspearBerserker(Minion):
	Class, race, name = "Neutral", "", "Darkspear Berserker"
	mana, attack, health = 4, 5, 7
	index = "THE_BARRENS~Neutral~Minion~4~5~7~~Darkspear Berserker~Deathrattle"
	requireTarget, effects, description = False, "", "Deathrattle: Deal 5 damage to your hero"
	name_CN = "暗矛狂战士"
	deathrattle = Death_DarkspearBerserker


class GruntledPatron(Minion):
	Class, race, name = "Neutral", "", "Gruntled Patron"
	mana, attack, health = 4, 3, 3
	index = "THE_BARRENS~Neutral~Minion~4~3~3~~Gruntled Patron~Frenzy"
	requireTarget, effects, description = False, "", "Frenzy: Summon another Gruntled Patron"
	name_CN = "满意的奴隶主"
	trigBoard = Trig_GruntledPatron


class InjuredMarauder(Minion):
	Class, race, name = "Neutral", "", "Injured Marauder"
	mana, attack, health = 4, 5, 10
	index = "THE_BARRENS~Neutral~Minion~4~5~10~~Injured Marauder~Taunt~Battlecry"
	requireTarget, effects, description = False, "Taunt", "Taunt. Battlecry: Deal 6 damage to this minion"
	name_CN = "受伤的掠夺者"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.dealsDamage(self, 6)


class KazakusGolemShaper(Minion):
	Class, race, name = "Neutral", "", "Kazakus, Golem Shaper"
	mana, attack, health = 4, 3, 3
	index = "THE_BARRENS~Neutral~Minion~4~3~3~~Kazakus, Golem Shaper~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: If your deck has no 4-Cost cards, build a custom Golem"
	name_CN = "魔像师卡扎库斯"

	def effCanTrig(self):
		self.effectViable = all(card.mana != 4 for card in self.Game.Hand_Deck.decks[self.ID])

	def createGolem(self, mana, effect, golem):
		name = golem.name
		words = golem.index.split('~')
		for i, word in enumerate(words):
			if word == name: words.insert(i+2, effect)
		newIndex = '~'.join(words)
		#Example: "SuperiorGolem__Mageroyal"
		subclass = type(golem.__name__+'__'+effect, (golem,),
						{"index": newIndex, "effects": effect, "description": effect + ". " + golem.description}
						)
		return subclass

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		game, ID = self.Game, self.ID
		if ID == game.turn and all(card.mana != 4 for card in game.Hand_Deck.decks[ID]):
			if game.mode == 0:
				manas, keyWords = (1, 5, 10), ("Rush", "Taunt", "Divine Shield", "Lifesteal", "Stealth", "Poisonouus")
				if game.picks:
					info_RNGSync, info_GUISync, isRandom, golemInfo = game.picks.pop(0)
					mana, effect, golem = golemInfo
					numpyChoice(range(6), 3, replace=False)
					numpyChoice(range(6), 3, replace=False)
					if game.GUI:
						i_mana, i_keyWord, i_golem = info_GUISync
						option_mana = (LesserGolem, GreaterGolem, SuperiorGolem)[i_mana](ID=ID)
						option_keyWord = GolemKeywordOptions[mana][keyWords.index(effect)](ID=ID)
						for indexOption, option in zip((i_mana, i_keyWord, i_golem), (option_mana, option_keyWord, golem(ID=ID))):
							game.GUI.discoverDecideAni(isRandom=isRandom, numOption=3, indexOption=indexOption, options=option)
					KazakusGolemShaper.discoverDecided(self, (mana, effect, golem), case="Guided")
				else:
					keyWords = numpyChoice(keyWords, 3, replace=False)
					if "byOthers" in comment:
						microsecond = datetime.now().microsecond
						i_mana, i_keyWord, i_golem = microsecond % 3, int(microsecond/10) % 3, int(microsecond/100) % 3
						mana, effect = manas[i_mana], keyWords[i_keyWord]
						if mana == 1: golems = (LesserGolem__Wildvine, LesserGolem__Gromsblood, LesserGolem__Icecap, LesserGolem__Firebloom, LesserGolem__Mageroyal, LesserGolem__Kingsblood)
						elif mana == 5: golems = (GreaterGolem__Wildvine, GreaterGolem__Gromsblood, GreaterGolem__Icecap, GreaterGolem__Firebloom, GreaterGolem__Mageroyal, GreaterGolem__Kingsblood)
						else: golems = (SuperiorGolem__Wildvine, SuperiorGolem__Gromsblood, SuperiorGolem__Icecap, SuperiorGolem__Firebloom, SuperiorGolem__Mageroyal, SuperiorGolem__Kingsblood)
						#Another n_choose_3
						golems = numpyChoice(golems, 3, replace=False)
						golem = golems[i_golem]
						if game.GUI:
							option_mana = (LesserGolem, GreaterGolem, SuperiorGolem)[i_mana](ID=ID)
							option_keyWord = GolemKeywordOptions[mana][keyWords.index(effect)](ID=ID)
							for indexOption, option in zip((i_mana, i_keyWord, i_golem), (option_mana, option_keyWord, golem(ID=ID))):
								game.GUI.discoverDecideAni(isRandom=True, numOption=3, indexOption=indexOption, options=option)
						KazakusGolemShaper.discoverDecided(self, (mana, effect, golem),
											 				case="Random", info_RNGSync=(6, 6), info_GUISync=(i_mana, i_keyWord, i_golem))
					else:
						info = [] #3次选择中积累出2+2+1个元素 (indexOption_mana, mana, indexOption_keyWord, effect, indexOption_effect)
						game.options = [LesserGolem(ID=ID), GreaterGolem(ID=ID), SuperiorGolem(ID=ID)]
						game.Discover.startDiscover(self, effectType=KazakusGolemShaper, info_RNGSync=(6, 6), info_GUISync=info)
						#The first discover changes the choices and leave a mana in there
						mana = info[0]
						#Whatever mana is, the effect poolSize is always 6
						game.options = [choice(ID=ID) for choice in numpyChoice(GolemKeywordOptions[mana], 3, replace=False)]
						game.Discover.startDiscover(self, effectType=KazakusGolemShaper, info_RNGSync=(6, 6), info_GUISync=info)
						#Whatever mana is, the effect poolSize is always 6
						game.options = [choice(ID=ID) for choice in numpyChoice(GolemEffectOptions[mana], 3, replace=False)]
						game.Discover.startDiscover(self, effectType=KazakusGolemShaper, info_RNGSync=(6, 6), info_GUISync=info)

	def discoverDecided(self, option, case, info_RNGSync=None, info_GUISync=None):
		if case == "Discovered": #The mana option and effect options have names
			if not option.name: #effect options。此时info_GUISync为[indexOption_mana, mana, indexOption_keyWord]
				info_GUISync.append(option.effect)
			else: #费用和效果选择
				#先选择费用，发现一次之后info_GUISync变为[indexOption_mana]
				if option.name == "Lesser Golem": info_GUISync.append(1)
				elif option.name == "Greater Golem": info_GUISync.append(5)
				elif option.name == "Superior Golem": info_GUISync.append(10)
				else: #effect option。此时info_GUISync为[indexOption_mana, mana, indexOption_keyWord, effect, indexOption_effect]
					#3次发现完成
					golem = GolemTable[option.name]
					indexOption_mana, mana, indexOption_keyWord, effect, indexOption_effect = info_GUISync
					self.Game.picks_Backup.append(((6, 6), (indexOption_mana, indexOption_keyWord, indexOption_effect),
											False, (mana, effect, golem)))
					self.addCardtoHand(KazakusGolemShaper.createGolem(self, mana, effect, golem), self.ID)
		else:
			mana, effect, golem = option
			if case == "Random": self.Game.picks_Backup.append((info_RNGSync, info_GUISync, True, option))
			self.addCardtoHand(KazakusGolemShaper.createGolem(self, mana, effect, golem), self.ID)


class LesserGolem(Option):
	name, category = "Lesser Golem", "Option_Minion"
	mana, attack, health = 1, -1, -1


class GreaterGolem(Option):
	name, category = "Greater Golem", "Option_Minion"
	mana, attack, health = 5, -1, -1


class SuperiorGolem(Option):
	name, category = "Superior Golem", "Option_Minion"
	mana, attack, health = 10, -1, -1


class Swiftthistle_1(Option):
	category, effect = "Option_Minion", "Rush"
	mana, attack, health = 1, -1, -1


class Swiftthistle_5(Option):
	category, effect = "Option_Minion", "Rush"
	mana, attack, health = 5, -1, -1


class Swiftthistle_10(Option):
	category, effect = "Option_Minion", "Rush"
	mana, attack, health = 10, -1, -1


class Earthroot_1(Option):
	category, effect = "Option_Minion", "Taunt"
	mana, attack, health = 1, -1, -1


class Earthroot_5(Option):
	category, effect = "Option_Minion", "Taunt"
	mana, attack, health = 5, -1, -1


class Earthroot_10(Option):
	category, effect = "Option_Minion", "Taunt"
	mana, attack, health = 10, -1, -1


class Sungrass_1(Option):
	category, effect = "Option_Minion", "Divine Shield"
	mana, attack, health = 1, -1, -1


class Sungrass_5(Option):
	category, effect = "Option_Minion", "Divine Shield"
	mana, attack, health = 5, -1, -1


class Sungrass_10(Option):
	category, effect = "Option_Minion", "Divine Shield"
	mana, attack, health = 10, -1, -1


class Liferoot_1(Option):
	category, effect = "Option_Minion", "Lifesteal"
	mana, attack, health = 1, -1, -1


class Liferoot_5(Option):
	category, effect = "Option_Minion", "Lifesteal"
	mana, attack, health = 5, -1, -1


class Liferoot_10(Option):
	category, effect = "Option_Minion", "Lifesteal"
	mana, attack, health = 10, -1, -1


class Fadeleaf_1(Option):
	category, effect = "Option_Minion", "Stealth"
	mana, attack, health = 1, -1, -1


class Fadeleaf_5(Option):
	category, effect = "Option_Minion", "Stealth"
	mana, attack, health = 5, -1, -1


class Fadeleaf_10(Option):
	category, effect = "Option_Minion", "Stealth"
	mana, attack, health = 10, -1, -1


class GraveMoss_1(Option):
	category, effect = "Option_Minion", "Poisonous"
	mana, attack, health = 1, -1, -1


class GraveMoss_5(Option):
	category, effect = "Option_Minion", "Poisonous"
	mana, attack, health = 5, -1, -1


class GraveMoss_10(Option):
	category, effect = "Option_Minion", "Poisonous"
	mana, attack, health = 10, -1, -1


#Battlecries
class Wildvine_1(Option):
	name, category, description = "Wildvine_1", "Option_Minion", "Battlecry: Give your other minions +1/+1"
	mana, attack, health = 1, -1, -1


class Wildvine_5(Option):
	name, category, description = "Wildvine_5", "Option_Minion", "Battlecry: Give your other minions +2/+2"
	mana, attack, health = 5, -1, -1


class Wildvine_10(Option):
	name, category, description = "Wildvine_10", "Option_Minion", "Battlecry: Give your other minions +4/+4"
	mana, attack, health = 10, -1, -1


class Gromsblood_1(Option):
	name, category, description = "Gromsblood_1", "Option_Minion", "Battlecry: Summon a copy of this"
	mana, attack, health = 1, -1, -1


class Gromsblood_5(Option):
	name, category, description = "Gromsblood_5", "Option_Minion", "Battlecry: Summon a copy of this"
	mana, attack, health = 5, -1, -1


class Gromsblood_10(Option):
	name, category, description = "Gromsblood_10", "Option_Minion", "Battlecry: Summon a copy of this"
	mana, attack, health = 10, -1, -1


class Icecap_1(Option):
	name, category, description = "Icecap_1", "Option_Minion", "Battlecry: Freeze a random enemy minion"
	mana, attack, health = 1, -1, -1


class Icecap_5(Option):
	name, category, description = "Icecap_5", "Option_Minion", "Battlecry: Freeze two random enemy minions"
	mana, attack, health = 5, -1, -1


class Icecap_10(Option):
	name, category, description = "Icecap_10", "Option_Minion", "Battlecry: Freeze all enemy minions"
	mana, attack, health = 10, -1, -1


class Firebloom_1(Option):
	name, category, description = "Firebloom_1", "Option_Minion", "Battlecry: Deal 3 damage to a random enemy minion"
	mana, attack, health = 1, -1, -1


class Firebloom_5(Option):
	name, category, description = "Firebloom_5", "Option_Minion", "Battlecry: Deal 3 damage to two random enemy minions"
	mana, attack, health = 5, -1, -1


class Firebloom_10:
	name, category, description = "Firebloom_10", "Option_Minion", "Battlecry: Deal 3 damage to all enemy minions"
	mana, attack, health = 10, -1, -1


class Mageroyal_1:
	name, category, description = "Mageroyal_1", "Option_Minion", "Spell Damage +1"
	mana, attack, health = 1, -1, -1


class Mageroyal_5:
	name, category, description = "Mageroyal_5", "Option_Minion", "Spell Damage +2"
	mana, attack, health = 5, -1, -1


class Mageroyal_10:
	name, category, description = "Mageroyal_10", "Option_Minion", "Spell Damage +4"
	mana, attack, health = 10, -1, -1


class Kingsblood_1:
	name, category, description = "Kingsblood_1", "Option_Minion", "Battlecry: Draw a card"
	mana, attack, health = 1, -1, -1


class Kingsblood_5:
	name, category, description = "Kingsblood_5", "Option_Minion", "Battlecry: Draw 2 cards"
	mana, attack, health = 5, -1, -1


class Kingsblood_10:
	name, category, description = "Kingsblood_10", "Option_Minion", "Battlecry: Draw 4 cards"
	mana, attack, health = 10, -1, -1


#Mana 1 Golems
class LesserGolem__Wildvine(Minion):
	Class, race, name = "Neutral", "", "Lesser Golem"
	mana, attack, health = 1, 1, 1
	index = "THE_BARRENS~Neutral~Minion~1~1~1~~Lesser Golem~Wildvine~Battlecry~Uncollectible"
	requireTarget, effects, description = False, "", "Battlecry: Give your other minions +1/+1"
	name_CN = "小型魔像"
	def text(self): return effectsDict[type(self).effects]

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.AOE_GiveEnchant(self.Game.minionsonBoard(self.ID, self), 1, 1, name=LesserGolem__Wildvine)


class LesserGolem__Gromsblood(Minion):
	Class, race, name = "Neutral", "", "Lesser Golem"
	mana, attack, health = 1, 1, 1
	index = "THE_BARRENS~Neutral~Minion~1~1~1~~Lesser Golem~Gromsblood~Battlecry~Uncollectible"
	requireTarget, effects, description = False, "", "Battlecry: Summon a copy of this"
	name_CN = "小型魔像"
	def text(self): return effectsDict[type(self).effects]

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon(self.selfCopy(self.ID, self))


class LesserGolem__Icecap(Minion):
	Class, race, name = "Neutral", "", "Lesser Golem"
	mana, attack, health = 1, 1, 1
	index = "THE_BARRENS~Neutral~Minion~1~1~1~~Lesser Golem~Icecap~Battlecry~Uncollectible"
	requireTarget, effects, description = False, "", "Battlecry: Freeze a random enemy minion"
	name_CN = "小型魔像"
	def text(self): return effectsDict[type(self).effects]

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if targets := self.Game.minionsAlive(3 - self.ID): self.freeze(numpyChoice(targets))


class LesserGolem__Firebloom(Minion):
	Class, race, name = "Neutral", "", "Lesser Golem"
	mana, attack, health = 1, 1, 1
	index = "THE_BARRENS~Neutral~Minion~1~1~1~~Lesser Golem~Firebloom~Battlecry~Uncollectible"
	requireTarget, effects, description = False, "", "Battlecry: Deal 3 damage to a random enemy minion"
	name_CN = "小型魔像"

	def text(self):
		return effectsDict[type(self).effects]

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		targets = self.Game.minionsAlive(3 - self.ID)
		if targets: self.dealsDamage(numpyChoice(targets), 3)


class LesserGolem__Mageroyal(Minion):
	Class, race, name = "Neutral", "", "Lesser Golem"
	mana, attack, health = 1, 1, 1
	index = "THE_BARRENS~Neutral~Minion~1~1~1~~Lesser Golem~Mageroyal~Spell Damage~Uncollectible"
	requireTarget, effects, description = False, "Spell Damage", "Spell Damage +1"
	name_CN = "小型魔像"

	def text(self):
		return effectsDict[type(self).effects]


class LesserGolem__Kingsblood(Minion):
	Class, race, name = "Neutral", "", "Lesser Golem"
	mana, attack, health = 1, 1, 1
	index = "THE_BARRENS~Neutral~Minion~1~1~1~~Lesser Golem~Kingsblood~Battlecry~Uncollectible"
	requireTarget, effects, description = False, "", "Battlecry: Draw a card"
	name_CN = "小型魔像"

	def text(self):
		return effectsDict[type(self).effects]

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.Hand_Deck.drawCard(self.ID)

#Mana 5 Golems


#Mana 5 Golems
class GreaterGolem__Wildvine(Minion):
	Class, race, name = "Neutral", "", "Greater Golem"
	mana, attack, health = 5, 5, 5
	index = "THE_BARRENS~Neutral~Minion~5~5~5~~Greater Golem~Wildvine~Battlecry~Uncollectible"
	requireTarget, effects, description = False, "", "Battlecry: Give your other minions +2/+2"
	name_CN = "大型魔像"

	def text(self):
		return effectsDict[type(self).effects]

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.AOE_GiveEnchant(self.Game.minionsonBoard(self.ID), 2, 2, name=GreaterGolem__Wildvine)


class GreaterGolem__Gromsblood(Minion):
	Class, race, name = "Neutral", "", "Greater Golem"
	mana, attack, health = 5, 5, 5
	index = "THE_BARRENS~Neutral~Minion~5~5~5~~Greater Golem~Gromsblood~Battlecry~Uncollectible"
	requireTarget, effects, description = False, "", "Battlecry: Summon a copy of this"
	name_CN = "大型魔像"

	def text(self):
		return effectsDict[type(self).effects]

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon(self.selfCopy(self.ID, self))


class GreaterGolem__Icecap(Minion):
	Class, race, name = "Neutral", "", "Greater Golem"
	mana, attack, health = 5, 5, 5
	index = "THE_BARRENS~Neutral~Minion~5~5~5~~Greater Golem~Icecap~Battlecry~Uncollectible"
	requireTarget, effects, description = False, "", "Battlecry: Freeze two random enemy minions"
	name_CN = "大型魔像"

	def text(self):
		return effectsDict[type(self).effects]

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		minions = self.Game.minionsAlive(3 - self.ID)
		self.AOE_Freeze(numpyChoice(minions, min(2, len(minions)), replace=False))


class GreaterGolem__Firebloom(Minion):
	Class, race, name = "Neutral", "", "Greater Golem"
	mana, attack, health = 5, 5, 5
	index = "THE_BARRENS~Neutral~Minion~5~5~5~~Greater Golem~Firebloom~Battlecry~Uncollectible"
	requireTarget, effects, description = False, "", "Battlecry: Deal 3 damage to two random enemy minions"
	name_CN = "大型魔像"

	def text(self):
		return effectsDict[type(self).effects]

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		minions = self.Game.minionsAlive(3 - self.ID)
		if minions:
			minions = numpyChoice(minions, min(2, len(minions)), replace=False)
			self.AOE_Damage(minions, [3] * len(minions))


class GreaterGolem__Mageroyal(Minion):
	Class, race, name = "Neutral", "", "Greater Golem"
	mana, attack, health = 5, 5, 5
	index = "THE_BARRENS~Neutral~Minion~5~5~5~~Greater Golem~Mageroyal~Spell Damage~Uncollectible"
	requireTarget, effects, description = False, "Spell Damage_2", "Spell Damage +2"
	name_CN = "大型魔像"

	def text(self):
		return effectsDict[type(self).effects]


class GreaterGolem__Kingsblood(Minion):
	Class, race, name = "Neutral", "", "Greater Golem"
	mana, attack, health = 5, 5, 5
	index = "THE_BARRENS~Neutral~Minion~5~5~5~~Greater Golem~Kingsblood~Battlecry~Uncollectible"
	requireTarget, effects, description = False, "", "Battlecry: Draw 2 cards"
	name_CN = "大型魔像"

	def text(self):
		return effectsDict[type(self).effects]

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.Hand_Deck.drawCard(self.ID)
		self.Game.Hand_Deck.drawCard(self.ID)

#Mana 10 Golems


#Mana 10 Golems
class SuperiorGolem__Wildvine(Minion):
	Class, race, name = "Neutral", "", "Superior Golem"
	mana, attack, health = 10, 10, 10
	index = "THE_BARRENS~Neutral~Minion~10~10~10~~Superior Golem~Wildvine~Battlecry~Uncollectible"
	requireTarget, effects, description = False, "", "Battlecry: Give your other minions +4/+4"
	name_CN = "超级魔像"
	def text(self): return effectsDict[type(self).effects]

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.AOE_GiveEnchant(self.Game.minionsonBoard(self.ID), 4, 4, name=SuperiorGolem__Wildvine)


class SuperiorGolem__Gromsblood(Minion):
	Class, race, name = "Neutral", "", "Superior Golem"
	mana, attack, health = 10, 10, 10
	index = "THE_BARRENS~Neutral~Minion~10~10~10~~Superior Golem~Gromsblood~Battlecry~Uncollectible"
	requireTarget, effects, description = False, "", "Battlecry: Summon a copy of this"
	name_CN = "超级魔像"

	def text(self):
		return effectsDict[type(self).effects]

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon(self.selfCopy(self.ID, self))


class SuperiorGolem__Icecap(Minion):
	Class, race, name = "Neutral", "", "Superior Golem"
	mana, attack, health = 10, 10, 10
	index = "THE_BARRENS~Neutral~Minion~10~10~10~~Superior Golem~Icecap~Battlecry~Uncollectible"
	requireTarget, effects, description = False, "", "Battlecry: Freeze all enemy minions"
	name_CN = "超级魔像"

	def text(self):
		return effectsDict[type(self).effects]

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.AOE_Freeze(self.Game.minionsonBoard(3-self.ID))


class SuperiorGolem__Firebloom(Minion):
	Class, race, name = "Neutral", "", "Superior Golem"
	mana, attack, health = 10, 10, 10
	index = "THE_BARRENS~Neutral~Minion~10~10~10~~Superior Golem~Firebloom~Battlecry~Uncollectible"
	requireTarget, effects, description = False, "", "Battlecry: Deal 3 damage to all enemy minions"
	name_CN = "超级魔像"

	def text(self):
		return effectsDict[type(self).effects]

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		targets = self.Game.minionsonBoard(3-self.ID)
		self.AOE_Damage(targets, [3]*len(targets))


class SuperiorGolem__Mageroyal(Minion):
	Class, race, name = "Neutral", "", "Superior Golem"
	mana, attack, health = 10, 10, 10
	index = "THE_BARRENS~Neutral~Minion~10~10~10~~Superior Golem~Mageroyal~Spell Damage~Uncollectible"
	requireTarget, effects, description = False, "Spell Damage_4", "Spell Damage +4"
	name_CN = "超级魔像"

	def text(self):
		return effectsDict[type(self).effects]


class SuperiorGolem__Kingsblood(Minion):
	Class, race, name = "Neutral", "", "Superior Golem"
	mana, attack, health = 10, 10, 10
	index = "THE_BARRENS~Neutral~Minion~10~10~10~~Superior Golem~Kingsblood~Battlecry~Uncollectible"
	requireTarget, effects, description = False, "", "Battlecry: Draw 4 cards"
	name_CN = "超级魔像"

	def text(self):
		return effectsDict[type(self).effects]

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for i in (0, 1, 2, 3):
			self.Game.Hand_Deck.drawCard(self.ID)


GolemKeywordOptions = {1: (Swiftthistle_1, Earthroot_1, Sungrass_1, Liferoot_1, Fadeleaf_1, GraveMoss_1),
						5: (Swiftthistle_5, Earthroot_5, Sungrass_5, Liferoot_5, Fadeleaf_5, GraveMoss_5),
						10: (Swiftthistle_10, Earthroot_10, Sungrass_10, Liferoot_10, Fadeleaf_10, GraveMoss_10)
					   }
#Battlecries
GolemEffectOptions = {1: (Wildvine_1, Gromsblood_1, Icecap_1, Firebloom_1, Mageroyal_1, Kingsblood_1),
						5: (Wildvine_5, Gromsblood_5, Icecap_5, Firebloom_5, Mageroyal_5, Kingsblood_5),
						10: (Wildvine_10, Gromsblood_10, Icecap_10, Firebloom_10, Mageroyal_10, Kingsblood_10),
					  }
#Mana 1 Golems
GolemTable = {"Wildvine_1": LesserGolem__Wildvine, "Wildvine_5": GreaterGolem__Wildvine, "Wildvine_10": SuperiorGolem__Wildvine,
				"Gromsblood_1": LesserGolem__Gromsblood, "Gromsblood_5": GreaterGolem__Gromsblood, "Gromsblood_10": SuperiorGolem__Gromsblood,
				"Icecap_1": LesserGolem__Icecap, "Icecap_5": GreaterGolem__Icecap, "Icecap_10": SuperiorGolem__Icecap,
				"Firebloom_1": LesserGolem__Firebloom, "Firebloom_5": GreaterGolem__Firebloom, "Firebloom_10": SuperiorGolem__Firebloom,
				"Mageroyal_1": LesserGolem__Mageroyal,  "Mageroyal_5": GreaterGolem__Mageroyal,  "Mageroyal_10": SuperiorGolem__Mageroyal,
				"Kingsblood_1": LesserGolem__Kingsblood, "Kingsblood_5": GreaterGolem__Kingsblood, "Kingsblood_10": SuperiorGolem__Kingsblood,
			  }

class SouthseaScoundrel(Minion):
	Class, race, name = "Neutral", "Pirate", "Southsea Scoundrel"
	mana, attack, health = 4, 5, 5
	index = "THE_BARRENS~Neutral~Minion~4~5~5~Pirate~Southsea Scoundrel~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Discover a card from your opponent's deck. They draw theirs as well"
	name_CN = "南海恶徒"

	def getCopyfromOppoDeck_TheyDrawTheirs(self, index, card):
		self.addCardtoHand(card.selfCopy(self.ID, self), self.ID, byDiscover=True)
		self.Game.Hand_Deck.drawCard(3 - self.ID, index)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverfromList(SouthseaScoundrel, comment, ls=self.Game.Hand_Deck.decks[3-self.ID])

	def discoverDecided(self, option, case, info_RNGSync=None, info_GUISync=None):
		self.handleDiscoveredCardfromList(option, case, ls=self.Game.Hand_Deck.decks[3 - self.ID],
										  func=lambda index, card: SouthseaScoundrel.getCopyfromOppoDeck_TheyDrawTheirs(self, index, card),
										  info_RNGSync=info_RNGSync, info_GUISync=info_GUISync)


class SpiritHealer(Minion):
	Class, race, name = "Neutral", "", "Spirit Healer"
	mana, attack, health = 4, 3, 6
	index = "THE_BARRENS~Neutral~Minion~4~3~6~~Spirit Healer"
	requireTarget, effects, description = False, "", "After you cast Holy spell, give a friendly minion +2 Health"
	name_CN = "灵魂医者"
	trigBoard = Trig_SpiritHealer


class BarrensBlacksmith(Minion):
	Class, race, name = "Neutral", "", "Barrens Blacksmith"
	mana, attack, health = 5, 3, 5
	index = "THE_BARRENS~Neutral~Minion~5~3~5~~Barrens Blacksmith~Frenzy"
	requireTarget, effects, description = False, "", "Frenzy: Give your other minions +2/+2"
	name_CN = "贫瘠之地铁匠"
	trigBoard = Trig_BarrensBlacksmith


class BurningBladeAcolyte(Minion):
	Class, race, name = "Neutral", "", "Burning Blade Acolyte"
	mana, attack, health = 5, 1, 1
	index = "THE_BARRENS~Neutral~Minion~5~1~1~~Burning Blade Acolyte~Deathrattle"
	requireTarget, effects, description = False, "", "Deathrattle: Summon a 5/8 Demonspawn with Taunt"
	name_CN = "火刃侍僧"
	deathrattle = Death_BurningBladeAcolyte

class Demonspawn(Minion):
	Class, race, name = "Neutral", "Demon", "Demonspawn"
	mana, attack, health = 6, 5, 8
	index = "THE_BARRENS~Neutral~Minion~6~5~8~Demon~Demonspawn~Taunt~Uncollectible"
	requireTarget, effects, description = False, "Taunt", "Taunt"
	name_CN = "恶魔生物"


class GoldRoadGrunt(Minion):
	Class, race, name = "Neutral", "", "Gold Road Grunt"
	mana, attack, health = 5, 3, 7
	index = "THE_BARRENS~Neutral~Minion~5~3~7~~Gold Road Grunt~Taunt~Frenzy"
	requireTarget, effects, description = False, "Taunt", "Taunt. Frenzy: Gain Armor equal to the damage taken"
	name_CN = "黄金之路步兵"
	trigBoard = Trig_GoldRoadGrunt


class RazormaneRaider(Minion):
	Class, race, name = "Neutral", "Quilboar", "Razormane Raider"
	mana, attack, health = 5, 5, 6
	index = "THE_BARRENS~Neutral~Minion~5~5~6~Quilboar~Razormane Raider~Frenzy"
	requireTarget, effects, description = False, "", "Frenzy: Attack a random enemy"
	name_CN = "钢鬃掠夺者"
	trigBoard = Trig_RazormaneRaider


class ShadowHunterVoljin(Minion):
	Class, race, name = "Neutral", "", "Shadow Hunter Vol'jin"
	mana, attack, health = 5, 3, 6
	index = "THE_BARRENS~Neutral~Minion~5~3~6~~Shadow Hunter Vol'jin~Battlecry~Legendary"
	requireTarget, effects, description = True, "", "Battlecry: Choose a minion. Swap it with a random one in its owners hand"
	name_CN = "暗影猎手沃金"

	def targetExists(self, choice=0):
		return self.selectableMinionExists()

	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target != self and target.onBoard

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and not target.dead and target.onBoard: #战吼触发时自己不能死亡。
			#假设对方手牌中没有随从时不能交换
			curGame, ID = self.Game, target.ID
			hand = curGame.Hand_Deck.hands[ID]
			if indices := [i for i, card in enumerate(hand) if card.category == "Minion"]:
				i = numpyChoice(indices)
				minion, pos = curGame.Hand_Deck.hands[ID][i], target.pos
				minion.disappears(deathrattlesStayArmed=False)
				curGame.removeMinionorWeapon(minion)
				minion.reset(ID)
				#下面节选自Hand.py的addCardtoHand方法，但是要跳过手牌已满的检测
				hand.append(minion)
				minion.entersHand()
				curGame.sendSignal("CardEntersHand", minion, None, [minion], 0, "")
				#假设先发送牌进入手牌的信号，然后召唤随从
				curGame.summonfrom(i, ID, pos, summoner=self, source='H')
		return target


class TaurajoBrave(Minion):
	Class, race, name = "Neutral", "", "Taurajo Brave"
	mana, attack, health = 6, 4, 8
	index = "THE_BARRENS~Neutral~Minion~6~4~8~~Taurajo Brave~Frenzy"
	requireTarget, effects, description = False, "", "Frenzy: Destroy a random enemy minion"
	name_CN = "陶拉祖武士"
	trigBoard = Trig_TaurajoBrave


class KargalBattlescar(Minion):
	Class, race, name = "Neutral", "", "Kargal Battlescar"
	mana, attack, health = 7, 5, 5
	index = "THE_BARRENS~Neutral~Minion~7~5~5~~Kargal Battlescar~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: Summon a 5/5 Lookout for each Watch Post you've summoned this game"
	name_CN = "卡加尔·战痕"

	def effCanTrig(self):
		self.effectViable = self.Game.Counters.numWatchPostSummoned[self.ID] > 0

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if minions := [Lookout(self.Game, self.ID) for i in range(len(self.Game.Counters.numWatchPostSummoned))]:
			self.summon(minions, relative="<>")


class Lookout(Minion):
	Class, race, name = "Neutral", "", "Lookout"
	mana, attack, health = 5, 5, 5
	index = "THE_BARRENS~Neutral~Minion~5~5~5~~Lookout~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "哨兵"


class PrimordialProtector(Minion):
	Class, race, name = "Neutral", "Elemental", "Primordial Protector"
	mana, attack, health = 8, 6, 6
	index = "THE_BARRENS~Neutral~Minion~8~6~6~Elemental~Primordial Protector~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Draw your highest Cost spell. Summon a random minion with the same Cost"
	name_CN = "始生保护者"
	poolIdentifier = "0-Cost Minions to Summon"
	@classmethod
	def generatePool(cls, pools):
		return ["%d-Cost Minions to Summon" % cost for cost in pools.MinionsofCost.keys()], \
			   list(pools.MinionsofCost.values())

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if indices := pickHighestCostIndices(self.Game.Hand_Deck.decks[self.ID], func=lambda card: card.category == "Spell"):
			cost = self.Game.Hand_Deck.drawCard(self.ID, numpyChoice(indices))[1]
			self.summon(numpyChoice(self.rngPool("%d-Cost Minions to Summon"%cost))(self.Game, self.ID))


"""Demon Hunter Cards"""
class FuryRank3(Spell):
	Class, school, name = "Demon Hunter", "Fel", "Fury (Rank 3)"
	requireTarget, mana, effects = False, 1, ""
	index = "THE_BARRENS~Demon Hunter~Spell~1~Fel~Fury (Rank 3)~Uncollectible"
	description = "Give your hero +4 Attack this turn"
	name_CN = "怒火（等级3）"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		self.giveHeroAttackArmor(self.ID, attGain=4, name=FuryRank3)


class FuryRank2(Spell_Forge):
	Class, school, name = "Demon Hunter", "Fel", "Fury (Rank 2)"
	requireTarget, mana, effects = False, 1, ""
	index = "THE_BARRENS~Demon Hunter~Spell~1~Fel~Fury (Rank 2)~Uncollectible"
	description = "Give your hero +3 Attack this turn. (Upgrades when you have 10 mana.)"
	upgradeMana, upgradedVersion = 10, FuryRank3
	name_CN = "怒火（等级2）"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		self.giveHeroAttackArmor(self.ID, attGain=3, name=FuryRank2)


class FuryRank1(Spell_Forge):
	Class, school, name = "Demon Hunter", "Fel", "Fury (Rank 1)"
	requireTarget, mana, effects = False, 1, ""
	index = "THE_BARRENS~Demon Hunter~Spell~1~Fel~Fury (Rank 1)"
	description = "Give your hero +2 Attack this turn. (Upgrades when you have 5 mana.)"
	upgradeMana, upgradedVersion = 5, FuryRank2
	name_CN = "怒火（等级1）"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		self.giveHeroAttackArmor(self.ID, attGain=2, name=FuryRank1)


class Tuskpiercer(Weapon):
	Class, name, description = "Demon Hunter", "Tuskpiercer", "Deathrattle: Draw a Deathrattle minion"
	mana, attack, durability, effects = 1, 1, 2, ""
	index = "THE_BARRENS~Demon Hunter~Weapon~1~1~2~Tuskpiercer~Deathrattle"
	name_CN = "獠牙锥刃"
	deathrattle = Death_Tuskpiercer


class Razorboar(Minion):
	Class, race, name = "Demon Hunter", "Beast", "Razorboar"
	mana, attack, health = 2, 3, 2
	index = "THE_BARRENS~Demon Hunter~Minion~2~3~2~Beast~Razorboar~Deathrattle"
	requireTarget, effects, description = False, "", "Deathrattle: Summon a Deathrattle minion that costs (3) or less from your hand"
	name_CN = "剃刀野猪"
	deathrattle = Death_Razorboar


class SigilofFlame(Spell):
	Class, school, name = "Demon Hunter", "Fel", "Sigil of Flame"
	requireTarget, mana, effects = False, 2, ""
	index = "THE_BARRENS~Demon Hunter~Spell~2~Fel~Sigil of Flame"
	description = "At the start of your next turn, deal 3 damage to all enemy minions"
	name_CN = "烈焰咒符"
	def text(self): return self.calcDamage(3)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		SigilofFlame_Effect(self.Game, self.ID).connect()


class SigilofSilence(Spell):
	Class, school, name = "Demon Hunter", "Shadow", "Sigil of Silence"
	requireTarget, mana, effects = False, 0, ""
	index = "THE_BARRENS~Demon Hunter~Spell~0~Shadow~Sigil of Silence"
	description = "At the start of your next turn, Silence all enemy minions"
	name_CN = "沉默咒符"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		SigilofSilence_Effect(self.Game, self.ID).connect()


class VileCall(Spell):
	Class, school, name = "Demon Hunter", "", "Vile Call"
	requireTarget, mana, effects = False, 3, ""
	index = "THE_BARRENS~Demon Hunter~Spell~3~~Vile Call"
	description = "Summon two 2/2 Demons with Lifesteal"
	name_CN = "邪恶召唤"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon([RavenousVilefiend(self.Game, self.ID) for _ in (0, 1)])


class RavenousVilefiend(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Ravenous Vilefiend"
	mana, attack, health = 2, 2, 2
	index = "THE_BARRENS~Demon Hunter~Minion~2~2~2~Demon~Ravenous Vilefiend~Lifesteal~Uncollectible"
	requireTarget, effects, description = False, "Lifesteal", "Lifesteal"
	name_CN = "贪食邪犬"


class RazorfenBeastmaster(Minion):
	Class, race, name = "Demon Hunter", "Quilboar", "Razorfen Beastmaster"
	mana, attack, health = 3, 3, 3
	index = "THE_BARRENS~Demon Hunter~Minion~3~3~3~Quilboar~Razorfen Beastmaster~Deathrattle"
	requireTarget, effects, description = False, "", "Deathrattle: Summon a Deathrattle minion that costs (4) or less from your hand"
	name_CN = "剃刀沼泽兽王"
	deathrattle = Death_RazorfenBeastmaster


class KurtrusAshfallen(Minion):
	Class, race, name = "Demon Hunter", "", "Kurtrus Ashfallen"
	mana, attack, health = 4, 3, 4
	index = "THE_BARRENS~Demon Hunter~Minion~4~3~4~~Kurtrus Ashfallen~Battlecry~Outcast~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: Attack the left and right-most enemy minions. Outcast: Immune this turn"
	name_CN = "库尔特鲁斯·陨烬"

	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.outcastcanTrig(self)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if posinHand == 0 or posinHand == -1:
			self.getsEffect("Immune", )
		minions = self.Game.minionsonBoard(3-self.ID)
		if minions and self.onBoard and self.health > 0 and not self.dead and minions[0].health > 0 and not minions[0].dead:
			self.Game.battle(self, minions[0], verifySelectable=False, useAttChance=False, resolveDeath=False)
		if minions and self.onBoard and self.health > 0 and not self.dead and minions[-1].health > 0 and not minions[-1].dead:
			self.Game.battle(self, minions[-1], verifySelectable=False, useAttChance=False, resolveDeath=False)


class VengefulSpirit(Minion):
	Class, race, name = "Demon Hunter", "", "Vengeful Spirit"
	mana, attack, health = 4, 4, 4
	index = "THE_BARRENS~Demon Hunter~Minion~4~4~4~~Vengeful Spirit~Outcast"
	requireTarget, effects, description = False, "", "Outcast: Draw two Deathrattle minions"
	name_CN = "复仇之魂"

	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.outcastcanTrig(self)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if posinHand == 0 or posinHand == -1:
			for _ in (0, 1):
				if not self.drawCertainCard(lambda card: card.category == "Minion" and card.deathrattles)[0]: break


class DeathSpeakerBlackthorn(Minion):
	Class, race, name = "Demon Hunter", "Quilboar", "Death Speaker Blackthorn"
	mana, attack, health = 7, 3, 6
	index = "THE_BARRENS~Demon Hunter~Minion~7~3~6~Quilboar~Death Speaker Blackthorn~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: Summon 3 Deathrattle minions that cost (5) or less from your deck"
	name_CN = "亡语者布莱克松"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		refMinion = self
		for _ in (0, 1, 2):
			if not (refMinion := self.try_SummonfromDeck(refMinion.pos + 1, func=lambda card: card.category == "Minion" and card.deathrattles)):
				break


class LivingSeedRank3(Spell):
	Class, school, name = "Druid", "Nature", "Living Seed (Rank 3)"
	requireTarget, mana, effects = False, 2, ""
	index = "THE_BARRENS~Druid~Spell~2~Nature~Living Seed (Rank 3)~Uncollectible"
	description = "Draw a Beast. Reduce its Cost by (3)"
	name_CN = "生命之种（等级3）"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		card, mana, entersHand = self.drawCertainCard(lambda card: "Beast" in card.race)
		if card and entersHand: ManaMod(card, by=-3).applies()

class LivingSeedRank2(Spell_Forge):
	Class, school, name = "Druid", "Nature", "Living Seed (Rank 2)"
	requireTarget, mana, effects = False, 2, ""
	index = "THE_BARRENS~Druid~Spell~2~Nature~Living Seed (Rank 2)~Uncollectible"
	description = "Draw a Beast. Reduce its Cost by (2). (Upgrades when you have 10 mana.)"
	upgradeMana, upgradedVersion = 10, LivingSeedRank3
	name_CN = "生命之种（等级2）"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		card, mana, entersHand = self.drawCertainCard(lambda card: "Beast" in card.race)
		if card and entersHand: ManaMod(card, by=-2).applies()

class LivingSeedRank1(Spell_Forge):
	Class, school, name = "Druid", "Nature", "Living Seed (Rank 1)"
	requireTarget, mana, effects = False, 2, ""
	index = "THE_BARRENS~Druid~Spell~2~Nature~Living Seed (Rank 1)"
	description = "Draw a Beast. Reduce its Cost by (1). (Upgrades when you have 5 mana.)"
	upgradeMana, upgradedVersion = 5, LivingSeedRank2
	name_CN = "生命之种（等级1）"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		card, mana, entersHand = self.drawCertainCard(lambda card: "Beast" in card.race)
		if card and entersHand: ManaMod(card, by=-1).applies()


class MarkoftheSpikeshell(Spell):
	Class, school, name = "Druid", "Nature", "Mark of the Spikeshell"
	requireTarget, mana, effects = True, 2, ""
	index = "THE_BARRENS~Druid~Spell~2~Nature~Mark of the Spikeshell"
	description = "Give a minion +2/+2. If it has Taunt, add a copy of it to your hand"
	name_CN = "尖壳印记"
	def available(self):
		return self.selectableMinionExists()

	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.giveEnchant(target, 2, 2, name=MarkoftheSpikeshell)
			if target.effects["Taunt"] > 0: self.addCardtoHand(target.selfCopy(self.ID, self), self.ID)
		return target


class RazormaneBattleguard(Minion):
	Class, race, name = "Druid", "Quilboar", "Razormane Battleguard"
	mana, attack, health = 2, 2, 3
	index = "THE_BARRENS~Druid~Minion~2~2~3~Quilboar~Razormane Battleguard"
	requireTarget, effects, description = False, "", "The first Taunt minion your play each turn costs (2) less"
	name_CN = "钢鬃卫兵"
	aura = ManaAura_RazormaneBattleguard


class ThorngrowthSentries(Spell):
	Class, school, name = "Druid", "Nature", "Thorngrowth Sentries"
	requireTarget, mana, effects = False, 2, ""
	index = "THE_BARRENS~Druid~Spell~2~Nature~Thorngrowth Sentries"
	description = "Summon two 1/2 Turtles with Taunt"
	name_CN = "荆棘护卫"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon([ThornguardTurtle(self.Game, self.ID) for _ in (0, 1)])


class ThornguardTurtle(Minion):
	Class, race, name = "Druid", "Beast", "Thornguard Turtle"
	mana, attack, health = 1, 1, 2
	index = "THE_BARRENS~Druid~Minion~1~1~2~Beast~Thornguard Turtle~Taunt~Uncollectible"
	requireTarget, effects, description = False, "Taunt", "Taunt"
	name_CN = "棘甲龟"


class GuffRunetotem(Minion):
	Class, race, name = "Druid", "", "Guff Runetotem"
	mana, attack, health = 3, 2, 4
	index = "THE_BARRENS~Druid~Minion~3~2~4~~Guff Runetotem~Legendary"
	requireTarget, effects, description = False, "", "After you cast a Nature spell, give another friendly minion +2/+2"
	name_CN = "古夫·符文图腾"
	trigBoard = Trig_GuffRunetotem


class PlaguemawtheRotting(Minion):
	Class, race, name = "Druid", "Quilboar", "Plaguemaw the Rotting"
	mana, attack, health = 4, 3, 4
	index = "THE_BARRENS~Druid~Minion~4~3~4~Quilboar~Plaguemaw the Rotting~Legendary"
	requireTarget, effects, description = False, "", "After a friendly Taunt minion dies, summon a new copy of it with Taunt"
	name_CN = "腐烂的普雷莫尔"
	trigBoard = Trig_PlaguemawtheRotting


class PridesFury(Spell):
	Class, school, name = "Druid", "", "Pride's Fury"
	requireTarget, mana, effects = False, 4, ""
	index = "THE_BARRENS~Druid~Spell~4~~Pride's Fury"
	description = "Give your minions +1/+3"
	name_CN = "狮群之怒"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.AOE_GiveEnchant(self.Game.minionsonBoard(self.ID), 1, 3, name=PridesFury)


class ThickhideKodo(Minion):
	Class, race, name = "Druid", "Beast", "Thickhide Kodo"
	mana, attack, health = 4, 3, 5
	index = "THE_BARRENS~Druid~Minion~4~3~5~Beast~Thickhide Kodo~Taunt~Deathrattle"
	requireTarget, effects, description = False, "Taunt", "Taunt. Deathrattle: Gain 5 Armor"
	name_CN = "厚皮科多兽"
	deathrattle = Death_ThickhideKodo


class CelestialAlignment(Spell):
	Class, school, name = "Druid", "Arcane", "Celestial Alignment"
	requireTarget, mana, effects = False, 7, ""
	index = "THE_BARRENS~Druid~Spell~7~Arcane~Celestial Alignment"
	description = "Set each player to 0 Mana Crystals. Set the Cost of cards in all hands and decks to (1)"
	name_CN = "超凡之盟"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for ID in (1, 2):
			self.Game.Manas.setManaCrystal(0, ID)
			for card in self.Game.Hand_Deck.hands[ID]:
				ManaMod(card, to=1).applies()
			for card in self.Game.Hand_Deck.decks[ID]:
				ManaMod(card, to=1).applies()


class DruidofthePlains(Minion):
	Class, race, name = "Druid", "Beast", "Druid of the Plains"
	mana, attack, health = 7, 7, 6
	index = "THE_BARRENS~Druid~Minion~7~7~6~Beast~Druid of the Plains~Rush~Frenzy"
	requireTarget, effects, description = False, "Rush", "Rush. Frenzy: Transform into a 6/7 Kodo with Taunt"
	name_CN = "平原德鲁伊"
	trigBoard = Trig_DruidofthePlains


class DruidofthePlains_Taunt(Minion):
	Class, race, name = "Druid", "Beast", "Druid of the Plains"
	mana, attack, health = 7, 6, 7
	index = "THE_BARRENS~Druid~Minion~7~6~7~Beast~Druid of the Plains~Taunt~Uncollectible"
	requireTarget, effects, description = False, "Taunt", "Taunt"
	name_CN = "平原德鲁伊"


"""Hunter Cards"""
class SunscaleRaptor(Minion):
	Class, race, name = "Hunter", "Beast", "Sunscale Raptor"
	mana, attack, health = 1, 1, 3
	index = "THE_BARRENS~Hunter~Minion~1~1~3~Beast~Sunscale Raptor~Frenzy"
	requireTarget, effects, description = False, "", "Frenzy: Shuffle a Sunscale Raptor into your deck with permanent +2/+1"
	name_CN = "赤鳞迅猛龙"
	trigBoard = Trig_SunscaleRaptor


class WoundPrey(Spell):
	Class, school, name = "Hunter", "", "Wound Prey"
	requireTarget, mana, effects = True, 1, ""
	index = "THE_BARRENS~Hunter~Spell~1~~Wound Prey"
	description = "Deal 1 damage. Summon a 1/1 Hyena with Rush"
	name_CN = "击伤猎物"
	def text(self): return self.calcDamage(1)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.dealsDamage(target, self.calcDamage(1))
			self.summon(SwiftHyena(self.Game, self.ID))
		return target

class SwiftHyena(Minion):
	Class, race, name = "Hunter", "Beast", "Swift Hyena"
	mana, attack, health = 1, 1, 1
	index = "THE_BARRENS~Hunter~Minion~1~1~1~Beast~Swift Hyena~Rush~Uncollectible"
	requireTarget, effects, description = False, "Rush", "Rush"
	name_CN = "迅捷土狼"


class KolkarPackRunner(Minion):
	Class, race, name = "Hunter", "", "Kolkar Pack Runner"
	mana, attack, health = 3, 3, 4
	index = "THE_BARRENS~Hunter~Minion~3~3~4~~Kolkar Pack Runner"
	requireTarget, effects, description = False, "", "After you cast a spell, summon a 1/1 Hyena with Rush"
	name_CN = "科卡尔驯犬者"
	trigBoard = Trig_KolkarPackRunner


class ProspectorsCaravan(Minion):
	Class, race, name = "Hunter", "", "Prospector's Caravan"
	mana, attack, health = 2, 1, 3
	index = "THE_BARRENS~Hunter~Minion~2~1~3~~Prospector's Caravan"
	requireTarget, effects, description = False, "", "At the start of your turn, give all minions in your hand +1/+1"
	name_CN = "勘探者车队"
	trigBoard = Trig_ProspectorsCaravan


class TameBeastRank3(Spell):
	Class, school, name = "Hunter", "", "Tame Beast (Rank 3)"
	requireTarget, mana, effects = False, 2, ""
	index = "THE_BARRENS~Hunter~Spell~2~~Tame Beast (Rank 3)~Uncollectible"
	description = "Summon a 6/6 Beast with Rush"
	name_CN = "驯服野兽（等级3）"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		self.summon(TamedThunderLizard(self.Game, self.ID))


class TameBeastRank2(Spell_Forge):
	Class, school, name = "Hunter", "", "Tame Beast (Rank 2)"
	requireTarget, mana, effects = False, 2, ""
	index = "THE_BARRENS~Hunter~Spell~2~~Tame Beast (Rank 2)~Uncollectible"
	description = "Summon a 4/4 Beast with Rush. (Upgrades when you have 10 mana.)"
	upgradeMana, upgradedVersion = 10, TameBeastRank3
	name_CN = "驯服野兽（等级2）"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		self.summon(TamedScorpid(self.Game, self.ID))


class TameBeastRank1(Spell_Forge):
	Class, school, name = "Hunter", "", "Tame Beast (Rank 1)"
	requireTarget, mana, effects = False, 2, ""
	index = "THE_BARRENS~Hunter~Spell~2~~Tame Beast (Rank 1)"
	description = "Summon a 2/2 Beast with Rush. (Upgrades when you have 5 mana.)"
	upgradeMana, upgradedVersion = 5, TameBeastRank2
	name_CN = "驯服野兽（等级1）"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		self.summon(TamedCrab(self.Game, self.ID))


class TamedCrab(Minion):
	Class, race, name = "Hunter", "Beast", "Tamed Crab"
	mana, attack, health = 2, 2, 2
	index = "THE_BARRENS~Hunter~Minion~2~2~2~Beast~Tamed Crab~Rush~Uncollectible"
	requireTarget, effects, description = False, "Rush", "Rush"
	name_CN = "驯服的螃蟹"


class TamedScorpid(Minion):
	Class, race, name = "Hunter", "Beast", "Tamed Scorpid"
	mana, attack, health = 4, 4, 4
	index = "THE_BARRENS~Hunter~Minion~4~4~4~Beast~Tamed Scorpid~Rush~Uncollectible"
	requireTarget, effects, description = False, "Rush", "Rush"
	name_CN = "驯服的蝎子"


class TamedThunderLizard(Minion):
	Class, race, name = "Hunter", "Beast", "Tamed Thunder Lizard"
	mana, attack, health = 6, 6, 6
	index = "THE_BARRENS~Hunter~Minion~6~6~6~Beast~Tamed Thunder Lizard~Rush~Uncollectible"
	requireTarget, effects, description = False, "Rush", "Rush"
	name_CN = "驯服的雷霆蜥蜴"


class PackKodo(Minion):
	Class, race, name = "Hunter", "Beast", "Pack Kodo"
	mana, attack, health = 3, 3, 3
	index = "THE_BARRENS~Hunter~Minion~3~3~3~Beast~Pack Kodo~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Discove a Beast, Secret, or weapon"
	name_CN = "载货科多兽"
	poolIdentifier = "Beasts as Druid"
	@classmethod
	def generatePool(cls, pools):
		Classes, ls_Pools = [], []
		neutralBeasts, neutralWeapons = [], []
		for card in pools.NeutralCards:
			if card.category == "Weapon": neutralWeapons.append(card)
			elif "Beast" in card.race: neutralBeasts.append(card)
		for Class in pools.Classes:
			beasts, secrets, weapons = [], [], []
			for card in pools.ClassCards[Class]:
				if "Beast" in card.race: beasts.append(card)
				elif card.race == "Secret": secrets.append(card)
				elif card.category == "Weapon": weapons.append(card)
			beasts.extend(neutralBeasts)
			weapons.extend(neutralWeapons)
			Classes.append("Beasts as "+Class)
			Classes.append(Class+" Secrets")
			Classes.append("Weapons as "+Class)
			ls_Pools.append(beasts)
			ls_Pools.append(secrets)
			ls_Pools.append(weapons)
		return Classes, ls_Pools

	def decidePools(self):
		Class = classforDiscover(self)
		HeroClass = self.Game.heroes[self.ID].Class
		key = HeroClass + " Secrets" if HeroClass in ["Hunter", "Mage", "Paladin", "Rogue"] else "Hunter Secrets"
		return [self.rngPool("Beasts as " + Class), self.rngPool(key), self.rngPool("Weapons as " + Class)]

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverandGenerate_MultiplePools(PackKodo, comment,
											   poolsFunc=lambda : PackKodo.decidePools(self))


class TavishStormpike(Minion):
	Class, race, name = "Hunter", "", "Tavish Stormpike"
	mana, attack, health = 3, 2, 5
	index = "THE_BARRENS~Hunter~Minion~3~2~5~~Tavish Stormpike~Legendary"
	requireTarget, effects, description = False, "", "After a friendly Beast attacks, summon a Beast from your deck that costs (1) less"
	name_CN = "塔维什·雷矛"
	trigBoard = Trig_TavishStormpike


class PiercingShot(Spell):
	Class, school, name = "Hunter", "", "Piercing Shot"
	requireTarget, mana, effects = True, 4, ""
	index = "THE_BARRENS~Hunter~Spell~4~~Piercing Shot"
	description = "Deal 6 damage to a minion. Excess damage hits the enemy hero"
	name_CN = "穿刺射击"
	def available(self):
		return self.selectableMinionExists()

	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard

	def text(self): return self.calcDamage(6)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target:
			totalDamage, realDamage = self.calcDamage(6), max(target.health, 0)
			excessDamage = totalDamage - realDamage
			self.dealsDamage(target, realDamage)
			if excessDamage > 0: self.dealsDamage(self.Game.heroes[3-self.ID], excessDamage)
		return target


class WarsongWrangler(Minion):
	Class, race, name = "Hunter", "", "Warsong Wrangler"
	mana, attack, health = 4, 3, 4
	index = "THE_BARRENS~Hunter~Minion~4~3~4~~Warsong Wrangler~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Discover a Beast in your deck. Give all copies of it +2/+1 (wherever they are)"
	name_CN = "战歌驯兽师"

	def drawBeastandBuffAllCopies(self, i, beast):
		cardType = type(self.Game.Hand_Deck.decks[self.ID][i])
		self.Game.Hand_Deck.drawCard(self.ID, i)
		self.AOE_GiveEnchant([minion for minion in self.Game.minionsonBoard(self.ID) if isinstance(minion, cardType)], 
							2, 1, name=WarsongWrangler)
		self.AOE_GiveEnchant([card for card in self.Game.Hand_Deck.hands[self.ID] if isinstance(card, cardType)], 
							2, 1, name=WarsongWrangler, add2EventinGUI=False)
		typeSelf = type(self)
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if isinstance(card, cardType): card.getsBuffDebuff_inDeck(2, 1, source=typeSelf, name=WarsongWrangler)
			
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverfromList(WarsongWrangler, comment, conditional=lambda card: "Beast" in card.race)

	def discoverDecided(self, option, case, info_RNGSync=None, info_GUISync=None):
		self.handleDiscoveredCardfromList(option, case, ls=self.Game.Hand_Deck.decks[self.ID],
										  func=lambda index, card: WarsongWrangler.drawBeastandBuffAllCopies(self, index, card),
										  info_RNGSync=info_RNGSync, info_GUISync=info_GUISync)


class BarakKodobane(Minion):
	Class, race, name = "Hunter", "", "Barak Kodobane"
	mana, attack, health = 5, 3, 5
	index = "THE_BARRENS~Hunter~Minion~5~3~5~~Barak Kodobane~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: Draw a 1, 2, and 3-Cost spell"
	name_CN = "巴拉克·科多班恩"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for cost in (1, 2, 3): self.drawCertainCard(lambda card: card.category == "Spell" and card.mana == cost)


"""Mage Cards"""
class FlurryRank3(Spell):
	Class, school, name = "Mage", "Frost", "Flurry (Rank 3)"
	requireTarget, mana, effects = False, 0, ""
	index = "THE_BARRENS~Mage~Spell~0~Frost~Flurry (Rank 3)~Uncollectible"
	description = "Freeze three random enemy minions"
	name_CN = "冰风暴（等级3）"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		minions = self.Game.minionsonBoard(3 - self.ID)
		self.AOE_Freeze(numpyChoice(minions, min(3, len(minions)), replace=False))


class FlurryRank2(Spell_Forge):
	Class, school, name = "Mage", "Frost", "Flurry (Rank 2)"
	requireTarget, mana, effects = False, 0, ""
	index = "THE_BARRENS~Mage~Spell~0~Frost~Flurry (Rank 2)~Uncollectible"
	description = "Freeze two random enemy minions. (Upgrades when you have 10 mana.)"
	upgradeMana, upgradedVersion = 10, FlurryRank3
	name_CN = "冰风暴（等级2）"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		minions = self.Game.minionsonBoard(3-self.ID)
		self.AOE_Freeze(numpyChoice(minions, min(2, len(minions)), replace=False))


class FlurryRank1(Spell_Forge):
	Class, school, name = "Mage", "Frost", "Flurry (Rank 1)"
	requireTarget, mana, effects = False, 0, ""
	index = "THE_BARRENS~Mage~Spell~0~Frost~Flurry (Rank 1)"
	description = "Freeze a random enemy minion. (Upgrades when you have 5 mana.)"
	upgradeMana, upgradedVersion = 5, FlurryRank2
	name_CN = "冰风暴（等级1）"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if minions := self.Game.minionsonBoard(3-self.ID): self.freeze(numpyChoice(minions))


class RunedOrb(Spell):
	Class, school, name = "Mage", "Arcane", "Runed Orb"
	requireTarget, mana, effects = True, 2, ""
	index = "THE_BARRENS~Mage~Spell~2~Arcane~Runed Orb"
	description = "Deal 2 damage. Discover a Spell"
	name_CN = "符文宝珠"
	poolIdentifier = "Mage Spells"
	@classmethod
	def generatePool(cls, pools):
		return [Class + " Spells" for Class in pools.Classes], \
			   [[card for card in cards if card.category == "Spell"] for cards in pools.ClassCards.values()]

	def text(self): return self.calcDamage(2)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.dealsDamage(target, self.calcDamage(2))
			self.discoverandGenerate(RunedOrb, comment, lambda : self.rngPool(classforDiscover(self) + " Spells"))
		return target


class Wildfire(Spell):
	Class, school, name = "Mage", "Fire", "Wildfire"
	requireTarget, mana, effects = False, 1, ""
	index = "THE_BARRENS~Mage~Spell~1~Fire~Wildfire"
	description = "Increase the damage of your Hero Power by 1"
	name_CN = "野火"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.powers[self.ID].getsEffect("Damage Boost")


class ArcaneLuminary(Minion):
	Class, race, name = "Mage", "Elemental", "Arcane Luminary"
	mana, attack, health = 3, 4, 3
	index = "THE_BARRENS~Mage~Minion~3~4~3~Elemental~Arcane Luminary"
	requireTarget, effects, description = False, "", "Cards that didn't start in your deck cost (2) less, but not less than (1)"
	name_CN = "奥术发光体"
	aura = ManaAura_ArcaneLuminary


class OasisAlly(Secret):
	Class, school, name = "Mage", "Frost", "Oasis Ally"
	requireTarget, mana, effects = False, 3, ""
	index = "THE_BARRENS~Mage~Spell~3~Frost~Oasis Ally~~Secret"
	description = "Secret: When a friendly minion is attacked, summon a 3/6 Water Elemental"
	name_CN = "绿洲盟军"
	trigBoard = Trig_OasisAlly


class Rimetongue(Minion):
	Class, race, name = "Mage", "", "Rimetongue"
	mana, attack, health = 3, 3, 4
	index = "THE_BARRENS~Mage~Minion~3~3~4~~Rimetongue"
	requireTarget, effects, description = False, "", "After you cast a Frost spell, summon a 1/1 Elemental that Freezes"
	name_CN = "霜舌半人马"
	trigBoard = Trig_Rimetongue


class FrostedElemental(Minion):
	Class, race, name = "Mage", "Elemental", "Frosted Elemental"
	mana, attack, health = 1, 1, 1
	index = "THE_BARRENS~Mage~Minion~1~1~1~Elemental~Frosted Elemental~Uncollectible"
	requireTarget, effects, description = False, "", "Freeze any character damaged by this minion"
	name_CN = "霜冻元素"
	trigBoard = Trig_FrostedElemental


class RecklessApprentice(Minion):
	Class, race, name = "Mage", "", "Reckless Apprentice"
	mana, attack, health = 4, 3, 5
	index = "THE_BARRENS~Mage~Minion~4~3~5~~Reckless Apprentice~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Fire your Hero Power at all enemies"
	name_CN = "鲁莽的学徒"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		#假设只有指向性的英雄技能才能触发，同时目标需要符合条件
		power = self.Game.powers[self.ID]
		if power.needTarget():
			for char in self.Game.minionsonBoard(3 - self.ID) + [self.Game.heroes[3 - self.ID]]:
				power.effect(char)
		else:
			for char in self.Game.minionsonBoard(3 - self.ID) + [self.Game.heroes[3 - self.ID]]:
				power.effect()


class RefreshingSpringWater(Spell):
	Class, school, name = "Mage", "", "Refreshing Spring Water"
	requireTarget, mana, effects = False, 5, ""
	index = "THE_BARRENS~Mage~Spell~5~~Refreshing Spring Water"
	description = "Draw 2 cards. Refresh 2 Mana Crystals for each spell drawn"
	name_CN = "清凉的泉水"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		card1 = self.Game.Hand_Deck.drawCard(self.ID)[0]
		card2 = self.Game.Hand_Deck.drawCard(self.ID)[0]
		num = 0 #假设即使爆牌也能回复费用
		if card1 and card1.category == "Spell": num += 2
		if card2 and card2.category == "Spell": num += 2
		if num > 0: self.Game.Manas.restoreManaCrystal(num, self.ID)


class VardenDawngrasp(Minion):
	Class, race, name = "Mage", "", "Varden Dawngrasp"
	mana, attack, health = 4, 3, 3
	index = "THE_BARRENS~Mage~Minion~4~3~3~~Varden Dawngrasp~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: Freeze all enemy minions. If any are already Frozen, deal 4 damage to them instead"
	name_CN = "瓦尔登·晨拥"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		targets_Freeze, targets_Damage = [], []
		for minion in self.Game.minionsonBoard(3-self.ID):
			if minion.effects["Frozen"] < 1: targets_Freeze.append(minion)
			else: targets_Damage.append(minion)
		self.AOE_Freeze(targets_Freeze)
		self.AOE_Damage(targets_Damage, [4]*len(targets_Damage))


class MordreshFireEye(Minion):
	Class, race, name = "Mage", "", "Mordresh Fire Eye"
	mana, attack, health = 8, 8, 8
	index = "THE_BARRENS~Mage~Minion~8~8~8~~Mordresh Fire Eye~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: If you've dealt 10 damage with your hero power this game, deal 10 damage to all enemies"
	name_CN = "火眼莫德雷斯"

	def effCanTrig(self):
		self.effectViable = self.Game.Counters.damageDealtbyHeroPower[self.ID] > 9

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Counters.damageDealtbyHeroPower[self.ID] > 9:
			targets = self.Game.minionsonBoard(3-self.ID) + [self.Game.heroes[3-self.ID]]
			self.AOE_Damage(targets, [10] * len(targets))


"""Paladin Cards"""
class ConvictionRank3(Spell):
	Class, school, name = "Paladin", "Holy", "Conviction (Rank 3)"
	requireTarget, mana, effects = False, 2, ""
	index = "THE_BARRENS~Paladin~Spell~2~Holy~Conviction (Rank 3)~Uncollectible"
	description = "Give three random friendly minions +3 Attack"
	name_CN = "定罪（等级3）"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if minions := self.Game.minionsonBoard(self.ID):
			self.AOE_GiveEnchant(numpyChoice(minions, min(2, len(minions)), replace=False), 3, 0, name=ConvictionRank3)

class ConvictionRank2(Spell_Forge):
	Class, school, name = "Paladin", "Holy", "Conviction (Rank 2)"
	requireTarget, mana, effects = False, 2, ""
	index = "THE_BARRENS~Paladin~Spell~2~Holy~Conviction (Rank 2)~Uncollectible"
	description = "Give two random friendly minions +3 Attack. (Upgrades when you have 10 mana.)"
	upgradeMana, upgradedVersion = 10, ConvictionRank3
	name_CN = "定罪（等级2）"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if minions := self.Game.minionsonBoard(self.ID):
			self.AOE_GiveEnchant(numpyChoice(minions, min(2, len(minions)), replace=False), 3, 0, name=ConvictionRank2)

class ConvictionRank1(Spell_Forge):
	Class, school, name = "Paladin", "Holy", "Conviction (Rank 1)"
	requireTarget, mana, effects = False, 2, ""
	index = "THE_BARRENS~Paladin~Spell~2~Holy~Conviction (Rank 1)"
	description = "Give a random friendly minion +3 Attack. (Upgrades when you have 5 mana.)"
	upgradeMana, upgradedVersion = 5, ConvictionRank2
	name_CN = "定罪（等级1）"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if minions := self.Game.minionsonBoard(self.ID): self.giveEnchant(numpyChoice(minions), 3, 0, name=ConvictionRank1)


class GallopingSavior(Secret):
	Class, school, name = "Paladin", "", "Galloping Savior"
	requireTarget, mana, effects = False, 1, ""
	index = "THE_BARRENS~Paladin~Spell~1~~Galloping Savior~~Secret"
	description = "Secret: After your opponent plays three cards in a turn, summon a 3/4 Steed with Taunt"
	name_CN = "迅疾救兵"
	trigBoard = Trig_GallopingSavior


class HolySteed(Minion):
	Class, race, name = "Paladin", "Beast", "Holy Steed"
	mana, attack, health = 3, 3, 4
	index = "THE_BARRENS~Paladin~Minion~3~3~4~Beast~Holy Steed~Taunt~Uncollectible"
	requireTarget, effects, description = False, "Taunt", "Taunt"
	name_CN = "神圣战马"


class KnightofAnointment(Minion):
	Class, race, name = "Paladin", "", "Knight of Anointment"
	mana, attack, health = 1, 1, 1
	index = "THE_BARRENS~Paladin~Minion~1~1~1~~Knight of Anointment~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Draw a Holy spell"
	name_CN = "圣礼骑士"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.drawCertainCard(lambda card: card.school == "Holy")


class SoldiersCaravan(Minion):
	Class, race, name = "Paladin", "", "Soldier's Caravan"
	mana, attack, health = 2, 1, 3
	index = "THE_BARRENS~Paladin~Minion~2~1~3~~Soldier's Caravan"
	requireTarget, effects, description = False, "", "At the start of your turn, summon two 1/1 Silver Hand Recruits"
	name_CN = "士兵车队"
	trigBoard = Trig_SoldiersCaravan


class SwordoftheFallen(Weapon):
	Class, name, description = "Paladin", "Sword of the Fallen", "After your hero attack, cast a Secret from your deck"
	mana, attack, durability, effects = 2, 1, 2, ""
	index = "THE_BARRENS~Paladin~Weapon~2~1~2~Sword of the Fallen"
	name_CN = "逝者之剑"
	trigBoard = Trig_SwordoftheFallen


class NorthwatchCommander(Minion):
	Class, race, name = "Paladin", "", "Northwatch Commander"
	mana, attack, health = 3, 3, 4
	index = "THE_BARRENS~Paladin~Minion~3~3~4~~Northwatch Commander~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: If you control a Secret, draw a minion"
	name_CN = "北卫军指挥官"
	def effCanTrig(self):
		self.effectViable = self.Game.Secrets.secrets[self.ID] != []

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Secrets.secrets[self.ID]: self.drawCertainCard(lambda card: card.category == "Minion")


class CarielRoame(Minion):
	Class, race, name = "Paladin", "", "Cariel Roame"
	mana, attack, health = 4, 4, 3
	index = "THE_BARRENS~Paladin~Minion~4~4~3~~Cariel Roame~Rush~Divine Shield~Legendary"
	requireTarget, effects, description = False, "Rush,Divine Shield", "Rush, Divine Shield. Whenever this attacks, reduce the Cost of Holy Spells in your hand by (1)"
	name_CN = "凯瑞尔·罗姆"
	trigBoard = Trig_CarielRoame


class VeteranWarmedic(Minion):
	Class, race, name = "Paladin", "", "Veteran Warmedic"
	mana, attack, health = 4, 3, 5
	index = "THE_BARRENS~Paladin~Minion~4~3~5~~Veteran Warmedic"
	requireTarget, effects, description = False, "", "After you cast a Holy spell, summon a 2/2 Medic with Lifesteal"
	name_CN = "战地医师老兵"
	trigBoard = Trig_VeteranWarmedic

class BattlefieldMedic(Minion):
	Class, race, name = "Paladin", "", "Battlefield Medic"
	mana, attack, health = 2, 2, 2
	index = "THE_BARRENS~Paladin~Minion~2~2~2~~Battlefield Medic~Lifesteal~Uncollectible"
	requireTarget, effects, description = False, "Lifesteal", "Lifesteal"
	name_CN = "战地医师"


class InvigoratingSermon(Spell):
	Class, school, name = "Paladin", "Holy", "Invigorating Sermon"
	requireTarget, mana, effects = False, 4, ""
	index = "THE_BARRENS~Paladin~Spell~4~Holy~Invigorating Sermon"
	description = "Give +1/+1 to all minions in your hand, deck and battlefield"
	name_CN = "动员布道"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		typeSelf = type(self)
		self.AOE_GiveEnchant([card for card in self.Game.Hand_Deck.hands[self.ID] if card.category == "Minion"], 
							1, 1, name=InvigoratingSermon, add2EventinGUI=False)
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if card.category == "Minion": card.getsBuffDebuff_inDeck(1, 1, source=typeSelf, name=InvigoratingSermon)
		self.AOE_GiveEnchant(self.Game.minionsonBoard(self.ID), 1, 1, name=InvigoratingSermon)


class CannonmasterSmythe(Minion):
	Class, race, name = "Paladin", "", "Cannonmaster Smythe"
	mana, attack, health = 5, 4, 4
	index = "THE_BARRENS~Paladin~Minion~5~4~4~~Cannonmaster Smythe~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: Transform your secrets into 3/3 Soldiers. They transform back when they die"
	name_CN = "火炮长斯密瑟"
	def effCanTrig(self):
		self.effectViable = self.Game.Secrets.secrets[self.ID] != []

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		secretsHD = self.Game.Secrets
		while secretsHD.secrets[self.ID] and self.Game.space(self.ID):
			secret = secretsHD.extractSecrets(self.ID, 0, enemyCanSee=False)
			minion = NorthwatchSoldier(self.Game, self.ID)
			minion.deathrattles[0].savedObj = secret
			self.summon(minion)

class NorthwatchSoldier(Minion):
	Class, race, name = "Paladin", "", "Northwatch Soldier"
	mana, attack, health = 3, 3, 3
	index = "THE_BARRENS~Paladin~Minion~3~3~3~~Northwatch Soldier~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "北卫军士兵"
	deathrattle = Death_NorthwatchSoldier


"""Priest Cards"""
class DesperatePrayer(Spell):
	Class, school, name = "Priest", "Holy", "Desperate Prayer"
	requireTarget, mana, effects = False, 0, ""
	index = "THE_BARRENS~Priest~Spell~0~Holy~Desperate Prayer"
	description = "Restore 5 Health to each hero"
	name_CN = "绝望祷言"
	def text(self): return self.calcHeal(5)
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		heal = self.calcHeal(5)
		self.AOE_Heal(list(self.Game.heroes.values()), [heal]*2)


class CondemnRank3(Spell):
	Class, school, name = "Priest", "Holy", "Condemn (Rank 3)"
	requireTarget, mana, effects = False, 2, ""
	index = "THE_BARRENS~Priest~Spell~2~Holy~Condemn (Rank 3)~Uncollectible"
	description = "Deal 3 damage to all enemy minions"
	name_CN = "罪罚（等级3）"
	def text(self): return self.calcDamage(3)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		damage = self.calcDamage(3)
		targets = self.Game.minionsonBoard(3 - self.ID)
		self.AOE_Damage(targets, [damage] * len(targets))


class CondemnRank2(Spell_Forge):
	Class, school, name = "Priest", "Holy", "Condemn (Rank 2)"
	requireTarget, mana, effects = False, 2, ""
	index = "THE_BARRENS~Priest~Spell~2~Holy~Condemn (Rank 2)~Uncollectible"
	description = "Deal 2 damage to all enemy minions. (Upgrades when you have 10 mana.)"
	upgradeMana, upgradedVersion = 10, CondemnRank3
	name_CN = "罪罚（等级2）"
	def text(self): self.calcDamage(2)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		damage = self.calcDamage(2)
		targets = self.Game.minionsonBoard(3 - self.ID)
		self.AOE_Damage(targets, [damage] * len(targets))


class CondemnRank1(Spell_Forge):
	Class, school, name = "Priest", "Holy", "Condemn (Rank 1)"
	requireTarget, mana, effects = False, 2, ""
	index = "THE_BARRENS~Priest~Spell~2~Holy~Condemn (Rank 1)"
	description = "Deal 1 damage to all enemy minions. (Upgrades when you have 5 mana.)"
	upgradeMana, upgradedVersion = 5, CondemnRank2
	name_CN = "罪罚（等级1）"
	def text(self): self.calcDamage(1)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		damage = self.calcDamage(1)
		targets = self.Game.minionsonBoard(3 - self.ID)
		self.AOE_Damage(targets, [damage] * len(targets))


class SerenaBloodfeather(Minion):
	Class, race, name = "Priest", "", "Serena Bloodfeather"
	mana, attack, health = 2, 1, 1
	index = "THE_BARRENS~Priest~Minion~2~1~1~~Serena Bloodfeather~Battlecry~Legendary"
	requireTarget, effects, description = True, "", "Battlecry: Choose an enemy minion. Steal Attack and Health from it until this has more"
	name_CN = "塞瑞娜·血羽"

	def targetExists(self, choice=0):
		return self.selectableEnemyMinionExists(choice)

	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.ID != self.ID and target.onBoard

	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target and (self.onBoard or self.inHand) and (target.attack > 0 or target.health > 0):
			attackStolen = max(0, int((target.attack - self.attack) / 2) + 1)
			healthStolen = max(0, int((target.health - self.health) / 2) + 1)
			self.giveEnchant(target, -attackStolen, -healthStolen, name=SerenaBloodfeather)
			self.giveEnchant(self, attackStolen, healthStolen, name=SerenaBloodfeather)


class SoothsayersCaravan(Minion):
	Class, race, name = "Priest", "", "Soothsayer's Caravan"
	mana, attack, health = 2, 1, 3
	index = "THE_BARRENS~Priest~Minion~2~1~3~~Soothsayer's Caravan"
	requireTarget, effects, description = False, "", "At the start of your turn, copy a spell from your opponent's deck to your hand"
	name_CN = "占卜者车队"
	trigBoard = Trig_SoothsayersCaravan


class DevouringPlague(Spell):
	Class, school, name = "Priest", "Shadow", "Devouring Plague"
	requireTarget, mana, effects = False, 3, "Lifesteal"
	index = "THE_BARRENS~Priest~Spell~3~Shadow~Devouring Plague~Lifesteal"
	description = "Lifesteal. Deal 4 damage randomly split among all enemies"
	name_CN = "噬灵疫病"
	def text(self): return self.calcDamage(4)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for num in range(self.calcDamage(4)):
			if objs := self.Game.charsAlive(3 - self.ID): self.dealsDamage(numpyChoice(objs), 1)
			else: break


class VoidFlayer(Minion):
	Class, race, name = "Priest", "", "Void Flayer"
	mana, attack, health = 4, 3, 4
	index = "THE_BARRENS~Priest~Minion~4~3~4~~Void Flayer~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: For each spell in your hand, deal 1 damage to a random enemy minion"
	name_CN = "剥灵者"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		damage = sum(card.category == "Spell" for card in self.Game.Hand_Deck.hands[self.ID])
		for _ in range(damage):
			if objs := self.Game.charsAlive(3-self.ID): self.dealsDamage(numpyChoice(objs), 1)
			else: break


class Xyrella(Minion):
	Class, race, name = "Priest", "", "Xyrella"
	mana, attack, health = 4, 4, 4
	index = "THE_BARRENS~Priest~Minion~4~4~4~~Xyrella~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: If you've restored Health this turn, deal that much damage to all enemy minions"
	name_CN = "泽瑞拉"
	def text(self): return self.Game.Counters.healthRestoredThisTurn[self.ID]

	def effCanTrig(self):
		self.effectViable = self.Game.Counters.healthRestoredThisTurn[self.ID] > 0

	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if (damage := self.Game.Counters.healthRestoredThisTurn[self.ID]) > 0:
			targets = self.Game.minionsonBoard(3-self.ID)
			self.AOE_Damage(targets, [damage]*len(targets))


class PriestofAnshe(Minion):
	Class, race, name = "Priest", "", "Priest of An'she"
	mana, attack, health = 5, 5, 5
	index = "THE_BARRENS~Priest~Minion~5~5~5~~Priest of An'she~Taunt~Battlecry"
	requireTarget, effects, description = False, "Taunt", "Taunt. Battlecry: If you've restored Health this turn, gain +3/+3"
	name_CN = "安瑟祭司"

	def effCanTrig(self):
		self.effectViable = self.Game.Counters.healthRestoredThisTurn[self.ID] > 0

	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if self.Game.Counters.healthRestoredThisTurn[self.ID] > 0: self.giveEnchant(self, 3, 3, name=PriestofAnshe)


class LightshowerElemental(Minion):
	Class, race, name = "Priest", "Elemental", "Lightshower Elemental"
	mana, attack, health = 6, 6, 6
	index = "THE_BARRENS~Priest~Minion~6~6~6~Elemental~Lightshower Elemental~Taunt~Deathrattle"
	requireTarget, effects, description = False, "Taunt", "Taunt. Deathrattle: Restore 8 Health to all friendly characters"
	name_CN = "光沐元素"
	deathrattle = Death_LightshowerElemental


class PowerWordFortitude(Spell):
	Class, school, name = "Priest", "Holy", "Power Word: Fortitude"
	requireTarget, mana, effects = True, 8, ""
	index = "THE_BARRENS~Priest~Spell~8~Holy~Power Word: Fortitude"
	description = "Give a minion +3/+5. Costs (1) less for each spell in your hand"
	name_CN = "真言术：韧"
	trigHand = Trigger_PowerWordFortitude
	def selfManaChange(self):
		if self.inHand:
			self.mana -= sum(card.category == "Spell" for card in self.Game.Hand_Deck.hands[self.ID])
			self.mana = max(0, self.mana)

	def targetExists(self, choice=0):
		return self.selectableMinionExists()

	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.giveEnchant(target, 3, 5, name=PowerWordFortitude)
		return target


"""Rogue Cards"""
class ParalyticPoison(Spell):
	Class, school, name = "Rogue", "Nature", "Paralytic Poison"
	requireTarget, mana, effects = False, 1, ""
	index = "THE_BARRENS~Rogue~Spell~1~Nature~Paralytic Poison"
	description = "Give your weapon +1 Attack and 'Your hero is Immune while attacking'"
	name_CN = "麻痹药膏"
	def available(self):
		return self.Game.availableWeapon(self.ID) is not None

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if weapon := self.Game.availableWeapon(self.ID): self.giveEnchant(weapon, 1, 0, trig=Trig_ParalyticPoison, name=ParalyticPoison)


class Yoink(Spell):
	Class, school, name = "Rogue", "", "Yoink!"
	requireTarget, mana, effects = False, 1, ""
	index = "THE_BARRENS~Rogue~Spell~1~~Yoink!"
	description = "Discover a Hero Power and set its Cost to (0). Swap back after 2 uses"
	name_CN = "偷师学艺"
	poolIdentifier = "Basic Powers"
	@classmethod
	def generatePool(cls, pools):
		return "Basic Powers", pools.basicPowers

	def decidePowerPool(self):
		powerType = type(self.Game.powers[self.ID])
		return [power for power in self.rngPool("Basic Powers") if power != powerType]

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverandGenerate(Yoink, comment, lambda : Yoink.decidePowerPool(self))

	def discoverDecided(self, option, case, info_RNGSync=None, info_GUISync=None):
		if case == "Discovered" or case == "Random":
			self.Game.picks_Backup.append((info_RNGSync, info_GUISync, case == "Random", type(option)) )
		ManaMod(option, to=0).applies()
		option.powerReplaced = self.Game.powers[self.ID]
		self.giveEnchant(option, trig=Trig_SwapBackPowerAfter2Uses, connect=False)
		option.replacePower()


class EfficientOctobot(Minion):
	Class, race, name = "Rogue", "Mech", "Efficient Octo-bot"
	mana, attack, health = 2, 1, 4
	index = "THE_BARRENS~Rogue~Minion~2~1~4~Mech~Efficient Octo-bot~Frenzy"
	requireTarget, effects, description = False, "", "Frenzy: Reduce the cost of cards in your hand by (1)"
	name_CN = "高效八爪机器人"
	trigBoard = Trig_EfficientOctobot


class SilverleafPoison(Spell):
	Class, school, name = "Rogue", "Nature", "Silverleaf Poison"
	requireTarget, mana, effects = False, 2, ""
	index = "THE_BARRENS~Rogue~Spell~2~Nature~Silverleaf Poison"
	description = "Give your weapon 'After your hero attacks draw a card'"
	name_CN = "银叶草药膏"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if weapon := self.Game.availableWeapon(self.ID): self.giveEnchant(weapon, trig=Trig_SilverleafPoison)


class WickedStabRank3(Spell):
	Class, school, name = "Rogue", "", "Wicked Stab (Rank 3)"
	requireTarget, mana, effects = True, 2, ""
	index = "THE_BARRENS~Rogue~Spell~2~~Wicked Stab (Rank 3)~Uncollectible"
	description = "Deal 6 damage"
	name_CN = "邪恶挥刺（等级3）"
	def text(self): return self.calcDamage(6)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target: self.dealsDamage(target, self.calcDamage(6))
		return target

class WickedStabRank2(Spell_Forge):
	Class, school, name = "Rogue", "", "Wicked Stab (Rank 2)"
	requireTarget, mana, effects = True, 2, ""
	index = "THE_BARRENS~Rogue~Spell~2~~Wicked Stab (Rank 2)~Uncollectible"
	description = "Deal 4 damage. (Upgrades when you have 10 mana.)"
	upgradeMana, upgradedVersion = 10, WickedStabRank3
	name_CN = "邪恶挥刺（等级2）"
	def text(self): return self.calcDamage(4)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target: self.dealsDamage(target, self.calcDamage(4))
		return target

class WickedStabRank1(Spell_Forge):
	Class, school, name = "Rogue", "", "Wicked Stab (Rank 1)"
	requireTarget, mana, effects = True, 2, ""
	index = "THE_BARRENS~Rogue~Spell~2~~Wicked Stab (Rank 1)"
	description = "Deal 2 damage. (Upgrades when you have 5 mana.)"
	upgradeMana, upgradedVersion = 5, WickedStabRank2
	name_CN = "邪恶挥刺（等级1）"
	def text(self): return self.calcDamage(2)
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target: self.dealsDamage(target, self.calcDamage(2))
		return target


class FieldContact(Minion):
	Class, race, name = "Rogue", "", "Field Contact"
	mana, attack, health = 3, 3, 2
	index = "THE_BARRENS~Rogue~Minion~3~3~2~~Field Contact"
	requireTarget, effects, description = False, "", "After you play a Battlecry or Combo card, draw a card"
	name_CN = "原野联络人"
	trigBoard = Trig_FieldContact


class SwinetuskShank(Weapon):
	Class, name, description = "Rogue", "Swinetusk Shank", "After you play a Poison gain +1 Durability"
	mana, attack, durability, effects = 3, 2, 2, ""
	index = "THE_BARRENS~Rogue~Weapon~3~2~2~Swinetusk Shank"
	name_CN = "猪牙匕首"
	trigBoard = Trig_SwinetuskShank


class ApothecaryHelbrim(Minion):
	Class, race, name = "Rogue", "", "Apothecary Helbrim"
	mana, attack, health = 4, 3, 2
	index = "THE_BARRENS~Rogue~Minion~4~3~2~~Apothecary Helbrim~Battlecry~Deathrattle~Legendary"
	requireTarget, effects, description = False, "", "Battlecry and Deathrattle: Add a random Poison to your hand"
	name_CN = "药剂师赫布拉姆"
	deathrattle = Death_ApothecaryHelbrim
	poolIdentifier = "Poisons"
	@classmethod
	def generatePool(cls, pools):
		return "Poisons", [card for card in pools.ClassCards["Rogue"] if card.category == "Spell" and "Poison" in card.name]

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.addCardtoHand(numpyChoice(self.rngPool("Poisons")), self.ID)


class OilRigAmbusher(Minion):
	Class, race, name = "Rogue", "", "Oil Rig Ambusher"
	mana, attack, health = 4, 4, 4
	index = "THE_BARRENS~Rogue~Minion~4~4~4~~Oil Rig Ambusher~Battlecry"
	requireTarget, effects, description = True, "", "Battlecry: Deal 2 damamge. If this entered your hand this turn, deal 4 damage instead"
	name_CN = "油田伏击者"

	def effCanTrig(self):
		self.effectViable = self.enterHandTurn == self.Game.numTurn

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.dealsDamage(target, 4 if self.enterHandTurn == self.Game.numTurn else 2)
		return target


class ScabbsCutterbutter(Minion):
	Class, race, name = "Rogue", "", "Scabbs Cutterbutter"
	mana, attack, health = 4, 3, 3
	index = "THE_BARRENS~Rogue~Minion~4~3~3~~Scabbs Cutterbutter~Combo~Legendary"
	requireTarget, effects, description = False, "", "Combo: The next two cards you play this turn cost (3) less"
	name_CN = "斯卡布斯·刀油"

	def effCanTrig(self):
		self.effectViable = self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0:
			GameManaAura_ScabbsCutterbutter(self.Game, self.ID).auraAppears()


"""Shaman Cards"""
class SpawnpoolForager(Minion):
	Class, race, name = "Shaman", "Murloc", "Spawnpool Forager"
	mana, attack, health = 1, 1, 2
	index = "THE_BARRENS~Shaman~Minion~1~1~2~Murloc~Spawnpool Forager~Deathrattle"
	requireTarget, effects, description = False, "", "Deathrattle: Summon a 1/1 Tinyfin"
	name_CN = "孵化池觅食者"
	deathrattle = Death_SpawnpoolForager

class DiremuckTinyfin(Minion):
	Class, race, name = "Shaman", "Murloc", "Diremuck Tinyfin"
	mana, attack, health = 1, 1, 1
	index = "THE_BARRENS~Shaman~Minion~1~1~1~Murloc~Diremuck Tinyfin~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "凶饿的鱼人宝宝"


class ChainLightningRank3(Spell):
	Class, school, name = "Shaman", "Nature", "Chain Lightning (Rank 3)"
	requireTarget, mana, effects = True, 2, ""
	index = "THE_BARRENS~Shaman~Spell~2~Nature~Chain Lightning (Rank 3)~Uncollectible"
	description = "Deal 4 damage to a minion and a random adjacent one"
	name_CN = "闪电链（等级3）"
	def available(self):
		return self.selectableMinionExists()

	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard

	def text(self): return self.calcDamage(4)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target:
			damage = self.calcDamage(4)
			if neighbors := self.Game.neighbors2(target)[0]: self.AOE_Damage([target, numpyChoice(neighbors)], [damage] * 2)
			else: self.dealsDamage(target, damage)
		return target


class ChainLightningRank2(Spell_Forge):
	Class, school, name = "Shaman", "Nature", "Chain Lightning (Rank 2)"
	requireTarget, mana, effects = True, 2, ""
	index = "THE_BARRENS~Shaman~Spell~2~Nature~Chain Lightning (Rank 2)~Uncollectible"
	description = "Deal 3 damage to a minion and a random adjacent one. (Upgrades when you have 10 mana.)"
	upgradeMana, upgradedVersion = 10, ChainLightningRank3
	name_CN = "闪电链（等级2）"
	def available(self):
		return self.selectableMinionExists()

	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard

	def text(self): return self.calcDamage(3)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target:
			damage = self.calcDamage(3)
			if neighbors := self.Game.neighbors2(target)[0]: self.AOE_Damage([target, numpyChoice(neighbors)], [damage] * 2)
			else: self.dealsDamage(target, damage)
		return target


class ChainLightningRank1(Spell_Forge):
	Class, school, name = "Shaman", "Nature", "Chain Lightning (Rank 1)"
	requireTarget, mana, effects = True, 2, ""
	index = "THE_BARRENS~Shaman~Spell~2~Nature~Chain Lightning (Rank 1)"
	description = "Deal 2 damage to a minion and a random adjacent one. (Upgrades when you have 5 mana.)"
	upgradeMana, upgradedVersion = 5, ChainLightningRank2
	name_CN = "闪电链（等级1）"
	def available(self):
		return self.selectableMinionExists()

	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard

	def text(self): return self.calcDamage(2)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target:
			damage = self.calcDamage(2)
			if neighbors := self.Game.neighbors2(target)[0]: self.AOE_Damage([target, numpyChoice(neighbors)], [damage] * 2)
			else: self.dealsDamage(target, damage)
		return target


class FiremancerFlurgl(Minion):
	Class, race, name = "Shaman", "Murloc", "Firemancer Flurgl"
	mana, attack, health = 2, 2, 3
	index = "THE_BARRENS~Shaman~Minion~2~2~3~Murloc~Firemancer Flurgl~Legendary"
	requireTarget, effects, description = False, "", "After you play a Murloc, deal 1 damage to all enemies"
	name_CN = "火焰术士弗洛格尔"
	trigBoard = Trig_FiremancerFlurgl


class SouthCoastChieftain(Minion):
	Class, race, name = "Shaman", "Murloc", "South Coast Chieftain"
	mana, attack, health = 2, 3, 2
	index = "THE_BARRENS~Shaman~Minion~2~3~2~Murloc~South Coast Chieftain~Battlecry"
	requireTarget, effects, description = True, "", "Battlecry: If you control another Murloc, deal 2 damage"
	name_CN = "南海岸酋长"

	def effCanTrig(self):
		self.effectViable = any("Murloc" in minion.race for minion in self.Game.minionsonBoard(self.ID))

	def needTarget(self, choice=0):
		return any("Murloc" in minion.race for minion in self.Game.minionsonBoard(self.ID))

	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target != self and target.onBoard

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and any("Murloc" in minion.race for minion in self.Game.minionsonBoard(self.ID)):
			self.dealsDamage(target, 2)
		return target


class TinyfinsCaravan(Minion):
	Class, race, name = "Shaman", "", "Tinyfin's Caravan"
	mana, attack, health = 2, 1, 3
	index = "THE_BARRENS~Shaman~Minion~2~1~3~~Tinyfin's Caravan"
	requireTarget, effects, description = False, "", "At the start of your turn, draw a Murloc"
	name_CN = "鱼人宝宝车队"
	trigBoard = Trig_TinyfinsCaravan


class AridStormer(Minion):
	Class, race, name = "Shaman", "Elemental", "Arid Stormer"
	mana, attack, health = 3, 2, 5
	index = "THE_BARRENS~Shaman~Minion~3~2~5~Elemental~Arid Stormer~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: If you played an Elemental last turn, gain Rush and Windfury"
	name_CN = "旱地风暴"

	def effCanTrig(self):
		self.effectViable = self.Game.Counters.numElementalsPlayedLastTurn[self.ID] > 0

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Counters.numElementalsPlayedLastTurn[self.ID] > 0:
			self.getsEffect("Rush", source=type(self))
			self.getsEffect("Windfury", source=type(self))


class NofinCanStopUs(Spell):
	Class, school, name = "Shaman", "", "Nofin Can Stop Us"
	requireTarget, mana, effects = False, 3, ""
	index = "THE_BARRENS~Shaman~Spell~3~~Nofin Can Stop Us"
	description = "Give your minions +1/+1. Give your Murlocs an extra +1/+1"
	name_CN = "鱼勇可贾"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.AOE_GiveEnchant([minion for minion in self.Game.minionsonBoard(self.ID) if "Murloc" not in minion.race], 
							1, 1, name=NofinCanStopUs)
		self.AOE_GiveEnchant(self.Game.minionsonBoard(self.ID, race="Murloc"), 2, 2, name=NofinCanStopUs)


class Brukan(Minion):
	Class, race, name = "Shaman", "", "Bru'kan"
	mana, attack, health = 4, 5, 4
	index = "THE_BARRENS~Shaman~Minion~4~5~4~~Bru'kan~Legendary"
	requireTarget, effects, description = False, "Nature Spell Damage_3", "Nature Spell Damage +3"
	name_CN = "布鲁坎"


class EarthRevenant(Minion):
	Class, race, name = "Shaman", "Elemental", "Earth Revenant"
	mana, attack, health = 4, 2, 6
	index = "THE_BARRENS~Shaman~Minion~4~2~6~Elemental~Earth Revenant~Taunt~Battlecry"
	requireTarget, effects, description = False, "Taunt", "Taunt. Battlecry: Deal 1 damage to all enemy minions"
	name_CN = "大地亡魂"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		targets = self.Game.minionsonBoard(3-self.ID)
		self.AOE_Damage(targets, [1]*len(targets))


class LilypadLurker(Minion):
	Class, race, name = "Shaman", "Elemental", "Lilypad Lurker"
	mana, attack, health = 5, 5, 6
	index = "THE_BARRENS~Shaman~Minion~5~5~6~Elemental~Lilypad Lurker~Battlecry"
	requireTarget, effects, description = True, "", "Battlecry: If you played an Elemental last turn, transform an enemy minion into a 0/1 Frog with Taunt"
	name_CN = "荷塘潜伏者"
	def needTarget(self, choice=0):
		return self.Game.Counters.numElementalsPlayedLastTurn[self.ID] > 0

	def effCanTrig(self):
		self.effectViable = self.Game.Counters.numElementalsPlayedLastTurn[self.ID] > 0

	def targetExists(self, choice=0):
		return self.selectableMinionExists(choice)

	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target != self and target.onBoard

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and self.Game.Counters.numElementalsPlayedLastTurn[self.ID] > 0:
			target = self.transform(target, Frog(self.Game, self.ID))
		return target


"""Warlock Cards"""
class AltarofFire(Spell):
	Class, school, name = "Warlock", "Fire", "Altar of Fire"
	requireTarget, mana, effects = False, 1, ""
	index = "THE_BARRENS~Warlock~Spell~1~Fire~Altar of Fire"
	description = "Destroy a friendly minion. Deal 2 damage to all enemy minions"
	name_CN = "火焰祭坛"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		self.Game.Hand_Deck.removeDeckTopCard(self.ID, num=3)
		self.Game.Hand_Deck.removeDeckTopCard(3-self.ID, num=3)


class GrimoireofSacrifice(Spell):
	Class, school, name = "Warlock", "Shadow", "Grimoire of Sacrifice"
	requireTarget, mana, effects = True, 1, ""
	index = "THE_BARRENS~Warlock~Spell~1~Shadow~Grimoire of Sacrifice"
	description = "Destroy a friendly minion. Deal 2 damage to all enemy minions"
	name_CN = "牺牲魔典"
	def available(self):
		return self.selectableFriendlyMinionExists()

	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard and target.ID == self.ID

	def text(self): return self.calcDamage(2)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.Game.killMinion(self, target)
			damage = self.calcDamage(2)
			targets = self.Game.minionsonBoard(3-self.ID)
			self.AOE_Damage(targets, [damage]*len(targets))
		return target


class ApothecarysCaravan(Minion):
	Class, race, name = "Warlock", "", "Apothecary's Caravan"
	mana, attack, health = 2, 1, 3
	index = "THE_BARRENS~Warlock~Minion~2~1~3~~Apothecary's Caravan"
	requireTarget, effects, description = False, "", "At the start of your turn, summon a 1-Cost minion from your deck"
	name_CN = "药剂师车队"
	trigBoard = Trig_ApothecarysCaravan


class ImpSwarmRank3(Spell):
	Class, school, name = "Warlock", "Fel", "Imp Swarm (Rank 3)"
	requireTarget, mana, effects = False, 2, ""
	index = "THE_BARRENS~Warlock~Spell~2~Fel~Imp Swarm (Rank 3)~Uncollectible"
	description = "Summon three 3/2 Imps"
	name_CN = "小鬼集群（等级3）"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		self.summon([ImpFamiliar(self.Game, self.ID) for _ in (0, 1, 2)])


class ImpSwarmRank2(Spell_Forge):
	Class, school, name = "Warlock", "Fel", "Imp Swarm (Rank 2)"
	requireTarget, mana, effects = False, 2, ""
	index = "THE_BARRENS~Warlock~Spell~2~Fel~Imp Swarm (Rank 2)~Uncollectible"
	description = "Summon two 3/2 Imps. (Upgrades when you have 10 Mana.)"
	upgradeMana, upgradedVersion = 10, ImpSwarmRank3
	name_CN = "小鬼集群（等级2）"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		self.summon([ImpFamiliar(self.Game, self.ID) for _ in (0, 1)])


class ImpSwarmRank1(Spell_Forge):
	Class, school, name = "Warlock", "Fel", "Imp Swarm (Rank 1)"
	requireTarget, mana, effects = False, 2, ""
	index = "THE_BARRENS~Warlock~Spell~2~Fel~Imp Swarm (Rank 1)"
	description = "Summon a 3/2 Imp. (Upgrades when you have 5 mana.)"
	upgradeMana, upgradedVersion = 5, ImpSwarmRank2
	name_CN = "小鬼集群（等级1）"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		self.summon(ImpFamiliar(self.Game, self.ID))


class ImpFamiliar(Minion):
	Class, race, name = "Warlock", "Demon", "Imp Familiar"
	mana, attack, health = 2, 3, 2
	index = "THE_BARRENS~Warlock~Minion~2~3~2~Demon~Imp Familiar~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "小鬼魔仆"


class BloodShardBristleback(Minion):
	Class, race, name = "Warlock", "Quilboar", "Blood Shard Bristleback"
	mana, attack, health = 3, 3, 3
	index = "THE_BARRENS~Warlock~Minion~3~3~3~Quilboar~Blood Shard Bristleback~Lifesteal~Battlecry"
	requireTarget, effects, description = True, "Lifesteal", "Lifesteal. Battlecry: If your deck contains 10 or fewer cards, deal 6 damage to a minion"
	name_CN = " 血之碎片刺背野猪人"
	def needTarget(self, choice=0):
		return len(self.Game.Hand_Deck.decks[self.ID]) < 11

	def targetExists(self, choice=0):
		return self.selectableMinionExists()

	def targetCorrect(self, target, choice=0):
		return target.onBoard and target.category == "Minion" and target != self

	def effCanTrig(self):
		self.effectViable = len(self.Game.Hand_Deck.decks[self.ID]) < 11

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and len(self.Game.Hand_Deck.decks[self.ID]) < 11:
			self.dealsDamage(target, 6)
		return target


class KabalOutfitter(Minion):
	Class, race, name = "Warlock", "", "Kabal Outfitter"
	mana, attack, health = 3, 3, 3
	index = "THE_BARRENS~Warlock~Minion~3~3~3~~Kabal Outfitter~Battlecry~Deathrattle"
	requireTarget, effects, description = False, "", "Battlecry and Deathrattle: Give another random friendly minion +1/+1"
	name_CN = "暗金教物资官"
	deathrattle = Death_KabalOutfitter
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if minions := self.Game.minionsonBoard(self.ID, self): self.giveEnchant(numpyChoice(minions), 1, 1, name=KabalOutfitter)


class TamsinRoame(Minion):
	Class, race, name = "Warlock", "", "Tamsin Roame"
	mana, attack, health = 3, 1, 3
	index = "THE_BARRENS~Warlock~Minion~3~1~3~~Tamsin Roame~Legendary"
	requireTarget, effects, description = False, "", "Whenever you cast a Shadow spell that costs (1) or more, add a copy to your hand that costs (0)"
	name_CN = "塔姆辛·罗姆"
	trigBoard = Trig_TamsinRoame


class SoulRend(Spell):
	Class, school, name = "Warlock", "Shadow", "Soul Rend"
	requireTarget, mana, effects = False, 4, ""
	index = "THE_BARRENS~Warlock~Spell~4~Shadow~Soul Rend"
	description = "Deal 5 damage to all minions. Destroy a card in your deck for each killed"
	name_CN = "灵魂撕裂"
	def text(self): return self.calcDamage(5)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = self.calcDamage(5)
		targets = self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)
		self.AOE_Damage(targets, [damage]*len(targets))
		if numKilled := sum(minion.health < 1 or minion.dead for minion in targets):
			self.Game.Hand_Deck.removeDeckTopCard(self.ID, numKilled)


class NeeruFireblade(Minion):
	Class, race, name = "Warlock", "", "Neeru Fireblade"
	mana, attack, health = 5, 5, 5
	index = "THE_BARRENS~Warlock~Minion~5~5~5~~Neeru Fireblade~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: If your deck is empty, open a portal that fills your board with 3/2 Imps each turn"
	name_CN = "尼尔鲁·火刃"

	def effCanTrig(self):
		self.effectViable = not self.Game.Hand_Deck.decks[self.ID]

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if not self.Game.Hand_Deck.decks[self.ID]:
			self.Game.summonSingle(BurningBladePortal(self.Game, self.ID), self.pos+1, self)

class BurningBladePortal(Dormant):
	Class, name = "Warlock", "Burning Blade Portal"
	description = "At the end of your turn, fill your board with 3/2 Imps"
	index = "THE_BARRENS~Dormant~Burning Blade Portal~Legendary"
	trigBoard = Trig_BurningBladePortal


class BarrensScavenger(Minion):
	Class, race, name = "Warlock", "", "Barrens Scavenger"
	mana, attack, health = 6, 6, 6
	index = "THE_BARRENS~Warlock~Minion~6~6~6~~Barrens Scavenger~Taunt"
	requireTarget, effects, description = False, "Taunt", "Taunt。 Costs(1) while your deck has 10 or fewer cards"
	name_CN = "贫瘠之地拾荒者"
	trigHand = Trig_BarrensScavenger
	def selfManaChange(self):
		if self.inHand and len(self.Game.Hand_Deck.decks[self.ID]) < 11:
			self.mana = 1


"""Warrior Cards"""
class WarsongEnvoy(Minion):
	Class, race, name = "Warrior", "", "Warsong Envoy"
	mana, attack, health = 1, 1, 3
	index = "THE_BARRENS~Warrior~Minion~1~1~3~~Warsong Envoy~Frenzy"
	requireTarget, effects, description = False, "", "Frenzy: Gain +1 Attack for each damaged character"
	name_CN = "战歌大使"
	trigBoard = Trig_WarsongEnvoy


class BulkUp(Spell):
	Class, school, name = "Warrior", "", "Bulk Up"
	requireTarget, mana, effects = False, 2, ""
	index = "THE_BARRENS~Warrior~Spell~2~~Bulk Up"
	description = "Give a random Taunt minion in your hand +1/+1 and copy it"
	name_CN = "重装上阵"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if minions := [card for card in self.Game.Hand_Deck.hands[self.ID] if card.category == "Minion" and card.effects["Taunt"] > 0]:
			self.giveEnchant((minion := numpyChoice(minions)), 1, 1, name=BulkUp, add2EventinGUI=False)
			self.addCardtoHand(minion.selfCopy(self.ID, self), self.ID)


class ConditioningRank3(Spell):
	Class, school, name = "Warrior", "", "Conditioning (Rank 3)"
	requireTarget, mana, effects = False, 2, ""
	index = "THE_BARRENS~Warrior~Spell~2~~Conditioning (Rank 3)~Uncollectible"
	description = "Give minions in your hand +3/+3"
	name_CN = "体格训练（等级3）"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		self.AOE_GiveEnchant([card for card in self.Game.Hand_Deck.hands[self.ID] if card.category == "Minion"],
							3, 3, name=ConditioningRank3, add2EventinGUI=False)

class ConditioningRank2(Spell_Forge):
	Class, school, name = "Warrior", "", "Conditioning (Rank 2)"
	requireTarget, mana, effects = False, 2, ""
	index = "THE_BARRENS~Warrior~Spell~2~~Conditioning (Rank 2)~Uncollectible"
	description = "Give minions in your hand +2/+2. (Upgrades when you have 10 mana.)"
	upgradeMana, upgradedVersion = 10, ConditioningRank3
	name_CN = "体格训练（等级2）"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		self.AOE_GiveEnchant([card for card in self.Game.Hand_Deck.hands[self.ID] if card.category == "Minion"],
							2, 2, name=ConditioningRank2, add2EventinGUI=False)

class ConditioningRank1(Spell_Forge):
	Class, school, name = "Warrior", "", "Conditioning (Rank 1)"
	requireTarget, mana, effects = False, 2, ""
	index = "THE_BARRENS~Warrior~Spell~2~~Conditioning (Rank 1)"
	description = "Give minions in your hand +1/+1. (Upgrades when you have 5 mana.)"
	upgradeMana, upgradedVersion = 5, ConditioningRank2
	name_CN = "体格训练（等级1）"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		self.AOE_GiveEnchant([card for card in self.Game.Hand_Deck.hands[self.ID] if card.category == "Minion"], 
							1, 1, name=ConditioningRank1, add2EventinGUI=False)


class Rokara(Minion):
	Class, race, name = "Warrior", "", "Rokara"
	mana, attack, health = 3, 2, 3
	index = "THE_BARRENS~Warrior~Minion~3~2~3~~Rokara~Rush~Legendary"
	requireTarget, effects, description = False, "Rush", "Rush. After a friendly minion attacks and survives, give it +1/+1"
	name_CN = "洛卡拉"
	trigBoard = Trig_Rokara


class OutridersAxe(Weapon):
	Class, name, description = "Warrior", "Outrider's Axe", "After your hero attacks and kills a minion, draw a card"
	mana, attack, durability, effects = 4, 3, 3, ""
	index = "THE_BARRENS~Warrior~Weapon~4~3~3~Outrider's Axe"
	name_CN = "先锋战斧"
	trigBoard = Trig_OutridersAxe


class Rancor(Spell):
	Class, school, name = "Warrior", "", "Rancor"
	requireTarget, mana, effects = False, 4, ""
	index = "THE_BARRENS~Warrior~Spell~4~~Rancor"
	description = "Deal 2 damage to all minions. Gain 2 Armor for each destroyed"
	name_CN = "仇怨累积"
	def text(self): return self.calcDamage(2)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = self.calcDamage(2)
		targets = self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)
		self.AOE_Damage(targets, [damage] * len(targets))
		if num := sum(minion.health < 1 or minion.dead for minion in targets):
			self.giveHeroAttackArmor(self.ID, num * 2)

class WhirlingCombatant(Minion):
	Class, race, name = "Warrior", "", "Whirling Combatant"
	mana, attack, health = 4, 3, 6
	index = "THE_BARRENS~Warrior~Minion~4~3~6~~Whirling Combatant~Frenzy~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry and Frenzy: Deal 1 damage to all other minions"
	name_CN = "旋风争斗者"
	trigBoard = Trig_WhirlingCombatant
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		targets = self.Game.minionsonBoard(self.ID, self) + self.Game.minionsonBoard(3-self.ID)
		self.AOE_Damage(targets, [1]*len(targets))


class MorshanElite(Minion):
	Class, race, name = "Warrior", "", "Mor'shan Elite"
	mana, attack, health = 5, 4, 4
	index = "THE_BARRENS~Warrior~Minion~5~4~4~~Mor'shan Elite~Taunt~Battlecry"
	requireTarget, effects, description = False, "Taunt", "Taunt. Battlecry: If your hero attacked this turn, summon a copy of this"
	name_CN = "莫尔杉精锐"

	def effCanTrig(self):
		self.effectViable = self.Game.Counters.heroAtkTimesThisTurn[self.ID] > 0

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Counters.heroAtkTimesThisTurn[self.ID] > 0:
			minion = self.selfCopy(self.ID, self) if self.onBoard else type(self)(self.Game, self.ID)
			self.summon(minion)


class StonemaulAnchorman(Minion):
	Class, race, name = "Warrior", "Pirate", "Stonemaul Anchorman"
	mana, attack, health = 5, 4, 6
	index = "THE_BARRENS~Warrior~Minion~5~4~6~Pirate~Stonemaul Anchorman~Rush~Frenzy"
	requireTarget, effects, description = False, "Rush", "Rush. Frenzy: Draw a card"
	name_CN = "石槌掌锚者"
	trigBoard = Trig_StonemaulAnchorman


class OverlordSaurfang(Minion):
	Class, race, name = "Warrior", "", "Overlord Saurfang"
	mana, attack, health = 7, 5, 4
	index = "THE_BARRENS~Warrior~Minion~7~5~4~~Overlord Saurfang~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: Resurrect two friendly Frenzy minions. Deal 1 damage to all other minions"
	name_CN = "萨鲁法尔大王"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		game = self.Game
		if minions := [card for card in game.Counters.minionsDiedThisGame[self.ID] if "~Frenzy" in card.index]:
			minions = numpyChoice(minions, min(2, len(minions)), replace=False)
			self.summon([minion(game, self.ID) for minion in minions], relative="<>")
		targets = game.minionsonBoard(self.ID, self) + game.minionsonBoard(3-self.ID)
		self.AOE_Damage(targets, [1]*len(targets))


#Neutral cards
class MeetingStone(Minion):
	Class, race, name = "Neutral", "", "Meeting Stone"
	mana, attack, health = 1, 0, 2
	index = "THE_BARRENS~Neutral~Minion~1~0~2~~Meeting Stone"
	requireTarget, effects, description = False, "", "At the end of your turn, add a 2/2 Adventurer with random bonus effect to your hand"
	name_CN = "集合石"
	trigBoard = Trig_MeetingStone


class DevouringEctoplasm(Minion):
	Class, race, name = "Neutral", "", "Devouring Ectoplasm"
	mana, attack, health = 3, 3, 2
	index = "THE_BARRENS~Neutral~Minion~3~3~2~~Devouring Ectoplasm~Deathrattle"
	requireTarget, effects, description = False, "", "Deathrattle: Summon a 2/2 Adventurer with random bonus effect"
	name_CN = "吞噬软浆怪"
	deathrattle = Death_DevouringEctoplasm


class ArchdruidNaralex(Minion):
	Class, race, name = "Neutral", "", "Archdruid Naralex"
	mana, attack, health = 3, 3, 3
	index = "THE_BARRENS~Neutral~Minion~3~3~3~~Archdruid Naralex~Legendary"
	requireTarget, effects, description = False, "", "Dormant for 2 turns. While Dormant, add a Dream card to your hand at the end of your turn"
	name_CN = "大德鲁伊纳拉雷克斯"
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
			self.Game.transform(self, SleepingNaralex(self.Game, self.ID, self), firstTime=True)
		else:  #只有不是第一次出现在场上时才会执行这些函数
			if self.btn:
				self.btn.isPlayed, self.btn.card = True, self
				self.btn.placeIcons()
				self.btn.statChangeAni()
				self.btn.effectChangeAni()
			for aura in self.auras: aura.auraAppears()
			for trig in self.trigsBoard + self.deathrattles: trig.connect()
			self.Game.sendSignal("MinionAppears", self.ID, self, None, 0, comment=firstTime)

class SleepingNaralex(Dormant):
	Class, school, name = "Neutral", "", "Sleeping Naralex"
	description = "Dormant for 2 turns. While Dormant, add a Dream card to your hand at the end of your turn"
	def __init__(self, Game, ID, minionInside=None):
		super().__init__(Game, ID, minionInside)
		self.trigsBoard = [Trig_SleepingNaralex(self), Trig_SleepingNaralex_Countdown(self)]


class MutanustheDevourer(Minion):
	Class, race, name = "Neutral", "Murloc", "Mutanus the Devourer"
	mana, attack, health = 7, 4, 4
	index = "THE_BARRENS~Neutral~Minion~7~4~4~Murloc~Mutanus the Devourer~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: Eat a minion in your opponent's hand. Gain its effect"
	name_CN = "吞噬者穆坦努斯"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if indices := [i for i, card in enumerate(self.Game.Hand_Deck.hands[3-self.ID]) if card.category == "Minion"]:
			minion = self.Game.Hand_Deck.extractfromHand(numpyChoice(indices), self.ID)[0]
			self.giveEnchant(self, minion.attack, minion.health, name=MutanustheDevourer)


class SelflessSidekick(Minion):
	Class, race, name = "Neutral", "", "Selfless Sidekick"
	mana, attack, health = 7, 6, 6
	index = "THE_BARRENS~Neutral~Minion~7~6~6~~Selfless Sidekick~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Equip a random weapon from your deck"
	name_CN = "无私的同伴"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if indices := [i for i, card in enumerate(self.Game.Hand_Deck.decks[self.ID]) if card.category == "Weapon"]:
			self.Game.equipWeapon(self.Game.Hand_Deck.extractfromDeck(numpyChoice(indices), self.ID, animate=False)[0])


#Demon Hunter
class SigilofSummoning(Spell):
	Class, school, name = "Demon Hunter", "Shadow", "Sigil of Summoning"
	requireTarget, mana, effects = False, 2, ""
	index = "THE_BARRENS~Demon Hunter~Spell~2~Shadow~Sigil of Summoning"
	description = "At the start of your next turn, summmon two 2/2 Demons with Taunt"
	name_CN = "召唤咒符"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		SigilofSummoning_Effect(self.Game, self.ID).connect()


class WailingDemon(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Wailing Demon"
	mana, attack, health = 2, 2, 2
	index = "THE_BARRENS~Demon Hunter~Minion~2~2~2~Demon~Wailing Demon~Taunt~Uncollectible"
	requireTarget, effects, description = False, "Taunt", "Taunt"
	name_CN = "哀嚎恶魔"


class Felrattler(Minion):
	Class, race, name = "Demon Hunter", "Beast", "Felrattler"
	mana, attack, health = 3, 3, 2
	index = "THE_BARRENS~Demon Hunter~Minion~3~3~2~Beast~Felrattler~Rush~Deathrattle"
	requireTarget, effects, description = False, "Rush", "Rush. Deathrattle: Deal 1 damage to all enemy minions"
	name_CN = "邪能响尾蛇"
	deathrattle = Death_Felrattler


class TaintheartTormenter(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Taintheart Tormenter"
	mana, attack, health = 8, 8, 8
	index = "THE_BARRENS~Demon Hunter~Minion~8~8~8~Demon~Taintheart Tormenter~Taunt"
	requireTarget, effects, description = False, "Taunt", "Taunt. Your opponent's spells cost (2) more"
	name_CN = "污心拷问者"
	aura = ManaAura_TaintheartTormenter


class FangboundDruid(Minion):
	Class, race, name = "Druid", "", "Fangbound Druid"
	mana, attack, health = 3, 4, 3
	index = "THE_BARRENS~Druid~Minion~3~4~3~~Fangbound Druid~Taunt~Deathrattle"
	requireTarget, effects, description = False, "Taunt", "Taunt. Deathrattle: Reduce the cost of a random Beast in your hand by (2)"
	name_CN = "牙缚德鲁伊"
	deathrattle = Death_FangboundDruid


class LadyAnacondra(Minion):
	Class, race, name = "Druid", "", "Lady Anacondra"
	mana, attack, health = 6, 3, 7
	index = "THE_BARRENS~Druid~Minion~6~3~7~~Lady Anacondra~Legendary"
	requireTarget, effects, description = False, "", "Your Nature spells cost (2) less"
	name_CN = "安娜康德拉"
	aura = ManaAura_LadyAnacondra


class DeviateDreadfang(Minion):
	Class, race, name = "Druid", "Beast", "Deviate Dreadfang"
	mana, attack, health = 8, 4, 9
	index = "THE_BARRENS~Druid~Minion~8~4~9~Beast~Deviate Dreadfang"
	requireTarget, effects, description = False, "", "After you cast a Nature spell, summon a 4/2 Viper with Rush"
	name_CN = "变异尖牙风蛇"
	trigBoard = Trig_DeviateDreadfang


class DeviateViper(Minion):
	Class, race, name = "Druid", "Beast", "Deviate Viper"
	mana, attack, health = 3, 4, 2
	index = "THE_BARRENS~Druid~Minion~3~4~2~Beast~Deviate Viper~Rush~Uncollectible"
	requireTarget, effects, description = False, "Rush", "Rush"
	name_CN = "变异飞蛇"


class Serpentbloom(Spell):
	Class, school, name = "Hunter", "", "Serpentbloom"
	requireTarget, mana, effects = True, 0, ""
	index = "THE_BARRENS~Hunter~Spell~0~~Serpentbloom"
	description = "Give a friendly Beast Poisonous"
	name_CN = "毒蛇花"
	def available(self):
		return self.selectableFriendlyMinionExists()

	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.ID == self.ID and target.onBoard and "Beast" in target.race

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: target.getsEffect("Poisonous", source=type(self))
		return target


class SindoreiScentfinder(Minion):
	Class, race, name = "Hunter", "", "Sin'dorei Scentfinder"
	mana, attack, health = 4, 1, 6
	index = "THE_BARRENS~Hunter~Minion~4~1~6~~Sin'dorei Scentfinder~Frenzy"
	requireTarget, effects, description = False, "", "Frenzy: Summon four 1/1 Hyenas with Rush"
	name_CN = "辛多雷气味猎手"
	trigBoard = Trig_SindoreiScentfinder


class VenomstrikeBow(Weapon):
	Class, name, description = "Hunter", "Venomstrike Bow", "Poisonous"
	mana, attack, durability, effects = 4, 1, 2, "Poisonous"
	index = "THE_BARRENS~Hunter~Weapon~4~1~2~Venomstrike Bow~Poisonous"
	name_CN = "毒袭之弓"


class FrostweaveDungeoneer(Minion):
	Class, race, name = "Mage", "", "Frostweave Dungeoneer"
	mana, attack, health = 3, 2, 3
	index = "THE_BARRENS~Mage~Minion~3~2~3~~Frostweave Dungeoneer~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Draw a spell. If it's a Frost spell, summon two 1/1 Elementals that Freeze"
	name_CN = "织霜地下城历险家"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if (card := self.drawCertainCard(lambda card: card.category == "Spell")[0]) and card.school == "Frost":
			self.summon([FrostedElemental(self.Game, self.ID) for _ in (0, 1)], relative="<>")


class ShatteringBlast(Spell):
	Class, school, name = "Mage", "Frost", "Shattering Blast"
	requireTarget, mana, effects = False, 3, ""
	index = "THE_BARRENS~Mage~Spell~3~Frost~Shattering Blast"
	description = "Destroy all Frozen minions"
	name_CN = "冰爆冲击"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		targets = [minion for minion in self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2) if minion.effects["Frozen"] > 0]
		self.Game.killMinion(self, targets)


class Floecaster(Minion):
	Class, race, name = "Mage", "", "Floecaster"
	mana, attack, health = 6, 5, 5
	index = "THE_BARRENS~Mage~Minion~6~5~5~~Floecaster"
	requireTarget, effects, description = False, "", "Costs (2) less for each Frozen enemy"
	name_CN = "浮冰施法者"
	trigHand = Trig_Floecaster
	def selfManaChange(self):
		if self.inHand:
			num = sum(char.effects["Frozen"] > 0 for char in self.Game.minionsonBoard(3-self.ID))
			if self.Game.heroes[3-self.ID].effects["Frozen"] > 0: num += 1
			self.mana -= 2 * num
			self.mana = max(0, self.mana)


class JudgmentofJustice(Secret):
	Class, school, name = "Paladin", "Holy", "Judgment of Justice"
	requireTarget, mana, effects = False, 1, ""
	index = "THE_BARRENS~Paladin~Spell~1~Holy~Judgment of Justice~~Secret"
	description = "Secret: When an enemy minion attacks, set its Attack and Health to 1"
	name_CN = "公正审判"
	trigBoard = Trig_JudgmentofJustice


class SeedcloudBuckler(Weapon):
	Class, name, description = "Paladin", "Seedcloud Buckler", "Deathrattle: Give your minions Divine Shield"
	mana, attack, durability, effects = 3, 2, 3, ""
	index = "THE_BARRENS~Paladin~Weapon~3~2~3~Seedcloud Buckler~Deathrattle"
	name_CN = "淡云圆盾"
	deathrattle = Death_SeedcloudBuckler


class PartyUp(Spell):
	Class, school, name = "Paladin", "", "Party Up!"
	requireTarget, mana, effects = False, 7, ""
	index = "THE_BARRENS~Paladin~Spell~7~~Party Up!"
	description = "Summon five 2/2 Adventurers with random bonus effects"
	name_CN = "小队集合"
	def available(self):
		return self.Game.space(self.ID) > 0

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon([minion(self.Game, self.ID) for minion in numpyChoice(Adventurers, 5, replace=True)])


#Priest cards


#Priest cards
class ClericofAnshe(Minion):
	Class, race, name = "Priest", "", "Cleric of An'she"
	mana, attack, health = 1, 1, 2
	index = "THE_BARRENS~Priest~Minion~1~1~2~~Cleric of An'she~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: If you've restored Health this turn, Discover a spell from your deck"
	name_CN = "安瑟教士"
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.healthRestoredThisTurn[self.ID] > 0

	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if self.Game.Counters.healthRestoredThisTurn[self.ID] > 0:
			self.discoverfromList(ClericofAnshe, comment, conditional=lambda card: card.category == "Spell")

	def discoverDecided(self, option, case, info_RNGSync=None, info_GUISync=None):
		self.handleDiscoveredCardfromList(option, case, ls=self.Game.Hand_Deck.decks[self.ID],
										  func=lambda index, card: self.Game.Hand_Deck.drawCard(self.ID, index),
										  info_RNGSync=info_RNGSync, info_GUISync=info_GUISync)


class DevoutDungeoneer(Minion):
	Class, race, name = "Priest", "", "Devout Dungeoneer"
	mana, attack, health = 3, 2, 3
	index = "THE_BARRENS~Priest~Minion~3~2~3~~Devout Dungeoneer~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Draw a spell. If it's a Holy spell, reduce its Cost by (2)"
	name_CN = "虔诚地下城历险家"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		card, mana, entersHand = self.drawCertainCard(lambda card: card.category == "Spell")
		if entersHand and card.school == "Holy": ManaMod(card, by=-2).applies()


class AgainstAllOdds(Spell):
	Class, school, name = "Priest", "Holy", "Against All Odds"
	requireTarget, mana, effects = False, 5, ""
	index = "THE_BARRENS~Priest~Spell~5~Holy~Against All Odds"
	description = "Destroy ALL odd-Attack minions"
	name_CN = "除奇致胜"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		targets = [minion for minion in self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2) if minion.attack % 2 == 1]
		if targets: self.Game.killMinion(self, targets)


#Rogue cards


#Rogue cards
class SavoryDeviateDelight(Spell):
	Class, school, name = "Rogue", "", "Savory Deviate Delight"
	requireTarget, mana, effects = False, 1, ""
	index = "THE_BARRENS~Rogue~Spell~1~~Savory Deviate Delight"
	description = "Transform a minion in both players' hands into a Pirate or Stealth minion"
	name_CN = "美味风蛇"
	poolIdentifier = "Pirates"
	@classmethod
	def generatePool(cls, pools):
		pirates = pools.MinionswithRace["Pirate"]
		stealthMinions = []
		for minions in pools.MinionsofCost.values(): #pool here is still a dict 1: {index: cls}
			stealthMinions += [minion for minion in minions if "Stealth" in minion.effects]
		return ["Pirates", "Stealth Minions"], [pirates, stealthMinions]

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		pool = self.rngPool("Pirates") + self.rngPool("Stealth Minions")
		minion1 = minion2 = newMinion1 = newMinion2 = None
		if minions := [card for card in self.Game.Hand_Deck.hands[1] if card.category == "Minion"]:
			minion1, newMinion1 = numpyChoice(minions), numpyChoice(pool)
		if minions := [card for card in self.Game.Hand_Deck.hands[2] if card.category == "Minion"]:
			minion2, newMinion2 = numpyChoice(minions), numpyChoice(pool)
		if minion1: self.transform(minion1, newMinion1(self.Game, 1))
		if minion2: self.transform(minion2, newMinion2(self.Game, 2))


class WaterMoccasin(Minion):
	Class, race, name = "Rogue", "Beast", "Water Moccasin"
	mana, attack, health = 3, 2, 5
	index = "THE_BARRENS~Rogue~Minion~3~2~5~Beast~Water Moccasin~Stealth"
	requireTarget, effects, description = False, "Stealth", "Stealth. Has Poisonous while you have no other minions"
	name_CN = "水栖蝮蛇"
	aura = Aura_WaterMoccasin


class ShroudofConcealment(Spell):
	Class, school, name = "Rogue", "Shadow", "Shroud of Concealment"
	requireTarget, mana, effects = False, 3, ""
	index = "THE_BARRENS~Rogue~Spell~3~Shadow~Shroud of Concealment"
	description = "Draw 2 minions. Any played this turn gain Stealth for 1 turn"
	name_CN = "潜行帷幕"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		minion1, mana, entersHand1 = self.drawCertainCard(lambda card: card.category == "Minion")
		if minion1:
			minion2, mana, entersHand2 = self.drawCertainCard(lambda card: card.category == "Minion")
			if minion1 and entersHand1 and entersHand2: ShroudofConcealment_Effect(self.Game, self.ID, [minion1, minion2]).connect()


#Shaman cards
class PerpetualFlame(Spell):
	Class, school, name = "Shaman", "Fire", "Perpetual Flame"
	requireTarget, mana, effects = False, 2, ""
	index = "THE_BARRENS~Shaman~Spell~2~Fire~Perpetual Flame~Overload"
	description = "Deal 3 damage to a random enemy minion. If it dies, recast this. Overload: (1)"
	name_CN = "永恒之火"
	overload = 1
	def text(self): return self.calcDamage(3)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if targets := self.Game.minionsAlive(3 - self.ID):
			self.dealsDamage((minion := numpyChoice(targets)), self.calcDamage(3))
			if minion.dead or minion.health < 1: PerpetualFlame(self.Game, self.ID).cast()


class WailingVapor(Minion):
	Class, race, name = "Shaman", "Elemental", "Wailing Vapor"
	mana, attack, health = 1, 1, 3
	index = "THE_BARRENS~Shaman~Minion~1~1~3~Elemental~Wailing Vapor"
	requireTarget, effects, description = False, "", "After you play an Elemental, gain +1 Attack"
	name_CN = "哀嚎蒸汽"
	trigBoard = Trig_WailingVapor


class PrimalDungeoneer(Minion):
	Class, race, name = "Shaman", "", "Primal Dungeoneer"
	mana, attack, health = 3, 2, 3
	index = "THE_BARRENS~Shaman~Minion~3~2~3~~Primal Dungeoneer~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Draw a spell. If it's a Nature spell, draw an Elemental"
	name_CN = "原初地下城历险家"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if (card := self.drawCertainCard(lambda card: card.category == "Spell")[0]) and card.school == "Nature":
			self.drawCertainCard(lambda card: "Elemental" in card.race)


#Warlock cards
class FinalGasp(Spell):
	Class, school, name = "Warlock", "Shadow", "Final Gasp"
	requireTarget, mana, effects = True, 1, ""
	index = "THE_BARRENS~Warlock~Spell~1~Shadow~Final Gasp"
	description = "Deal 1 damage to a minion. If it dies, summon a 2/2 Adventurer with random bonus effect"
	name_CN = "临终之息"
	def available(self):
		return self.selectableMinionExists()

	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard

	def text(self): return self.calcDamage(1)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target:
			self.dealsDamage(target, self.calcDamage(1))
			if target.dead or target.health < 1: self.summon(numpyChoice(Adventurers)(self.Game, self.ID))
		return target


class UnstableShadowBlast(Spell):
	Class, school, name = "Warlock", "Shadow", "Unstable Shadow Blast"
	requireTarget, mana, effects = True, 2, ""
	index = "THE_BARRENS~Warlock~Spell~2~Shadow~Unstable Shadow Blast"
	description = "Deal 6 damage to a minion. Excess damage hits your hero"
	name_CN = "不稳定的暗影震爆"
	def available(self):
		return self.selectableMinionExists()

	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard

	def text(self): return self.calcDamage(6)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target:
			totalDamage, realDamage = self.calcDamage(6), max(target.health, 0)
			excessDamage = totalDamage - realDamage
			self.dealsDamage(target, realDamage)
			if excessDamage > 0: self.dealsDamage(self.Game.heroes[self.ID], excessDamage)
		return target


class StealerofSouls(Minion):
	Class, race, name = "Warlock", "Demon", "Stealer of Souls"
	mana, attack, health = 6, 4, 6
	index = "THE_BARRENS~Warlock~Minion~6~4~6~Demon~Stealer of Souls"
	requireTarget, effects, description = False, "", "After you draw a card, change its Cost to Health instead of Mana"
	name_CN = "灵魂窃者"
	trigBoard = Trig_StealerofSouls


#Warrior cards
class ManatArms(Minion):
	Class, race, name = "Warrior", "", "Man-at-Arms"
	mana, attack, health = 2, 2, 3
	index = "THE_BARRENS~Warrior~Minion~2~2~3~~Man-at-Arms~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: If you have a weapon equipped, gain +1/+1"
	name_CN = "武装战士"
	def effCanTrig(self):
		self.effectViable = self.Game.availableWeapon(self.ID) is not None

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.availableWeapon(self.ID): self.giveEnchant(self, 1, 1, name=ManatArms)


class WhetstoneHatchet(Weapon):
	Class, name, description = "Warrior", "Whetstone Hatchet", "After your hero attack, give a minion in your hand +1 Attack"
	mana, attack, durability, effects = 1, 1, 4, ""
	index = "THE_BARRENS~Warrior~Weapon~1~1~4~Whetstone Hatchet"
	name_CN = "砥石战斧"
	trigBoard = Trig_WhetstoneHatchet


class KreshLordofTurtling(Minion):
	Class, race, name = "Warrior", "Beast", "Kresh, Lord of Turtling"
	mana, attack, health = 6, 3, 9
	index = "THE_BARRENS~Warrior~Minion~6~3~9~Beast~Kresh, Lord of Turtling~Frenzy~Deathrattle~Legendary"
	requireTarget, effects, description = False, "", "Frenzy: Gain 8 Armor. Deathrattle: Equip a 2/5 Turtle Spike"
	name_CN = "克雷什，群龟之王"
	trigBoard, deathrattle = Trig_KreshLordofTurtling, Death_KreshLordofTurtling

class TurtleSpike(Weapon):
	Class, name, description = "Warrior", "Turtle Spike", ""
	mana, attack, durability, effects = 4, 2, 5, ""
	index = "THE_BARRENS~Warrior~Weapon~4~2~5~Turtle Spike~Uncollectible"
	name_CN = "龟甲尖刺"


"""Game TrigEffects and game Auras"""
class GameManaAura_KindlingElemental(GameManaAura_OneTime):
	card, by, temporary = KindlingElemental, -1, False
	def applicable(self, target): return target.ID == self.ID and "Elemental" in target.race

class TalentedArcanist_Effect(TrigEffect):
	card, signals, counter, trigType = TalentedArcanist, ("SpellBeenCast",), 2, "Conn&TurnEnd&OnlyKeepOne"
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.Game.heroes[self.ID].losesEffect("Spell Damage", amount=2)
		self.disconnect()

	def trigEffect(self):
		self.Game.heroes[self.ID].losesEffect("Spell Damage", amount=2)


class SigilofSilence_Effect(TrigEffect):
	card, trigType = SigilofSilence, "TurnStart&OnlyKeepOne"
	def trigEffect(self):
		self.Game.silenceMinions(self.Game.minionsonBoard(3 - self.ID))

class SigilofFlame_Effect(TrigEffect):
	card, trigType = SigilofFlame, "TurnStart&OnlyKeepOne"
	def trigEffect(self):
		damage = self.card.calcDamage(3)
		targets = self.Game.minionsonBoard(3 - self.ID)
		self.card.AOE_Damage(targets, [damage] * len(targets))

class SigilofSummoning_Effect(TrigEffect):
	card, trigType = SigilofSummoning, "TurnStart&OnlyKeepOne"
	def trigEffect(self):
		self.card.summon([WailingDemon(self.Game, self.ID) for _ in (0, 1)])


class ShroudofConcealment_Effect(TrigEffect):
	card, signals, counter, trigtype = ShroudofConcealment, ("MinionBeenPlayed",), 2, "Conn&TurnEnd"
	def __init__(self, Game, ID, cardsDrawn=()):
		super().__init__(Game, ID)
		self.savedObjs = cardsDrawn

	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.ID and subject in self.savedObjs

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		subject.getsEffect("Temp Stealth", source=type(self))
		self.savedObjs.remove(subject)
		if not self.savedObjs: self.disconnect()

	def assistCreateCopy(self, Copy):
		Copy.cardsDrawn = [card.createCopy(Copy.Game) for card in self.savedObjs]


class GameManaAura_ScabbsCutterbutter(GameManaAura_OneTime):
	card, by = ScabbsCutterbutter, -2
	def applicable(self, target): return target.ID == self.ID

class GameManaAura_RazormaneBattleguard(GameManaAura_OneTime):
	card, by = RazormaneBattleguard, -2
	def applicable(self, target): return target.ID == self.ID and target.category == "Minion" and target.effects["Taunt"] > 0


TrigsDeaths_Barrens = {Death_DeathsHeadCultist: (DeathsHeadCultist, "Deathrattle: Restore 4 Health to your hero"),
						Death_DarkspearBerserker: (DarkspearBerserker, "Deathrattle: Deal 5 damage to your hero"),
						Death_BurningBladeAcolyte: (BurningBladeAcolyte, "Deathrattle: Summon a 5/8 Demonspawn with Taunt"),
						Death_Tuskpiercer: (Tuskpiercer, "Deathrattle: Draw a Deathrattle minion"),
						Death_Razorboar: (Razorboar, "Deathrattle: Summon a Deathrattle minion that costs (3) or less from your hand"),
						Death_RazorfenBeastmaster: (RazorfenBeastmaster, "Deathrattle: Summon a Deathrattle minion that costs (4) or less from your hand"),
						Death_ThickhideKodo: (ThickhideKodo, "Deathrattle: Gain 5 Armor"),
						Death_NorthwatchSoldier: (NorthwatchSoldier, "Deathrattle: Transform back into secret"),
						Death_LightshowerElemental: (LightshowerElemental, "Deathrattle: Restore 8 Health to all friendly characters"),
						Trig_SwapBackPowerAfter2Uses: (Yoink, "Deathrattle: Swap back after 2 uses"),
						Trig_ParalyticPoison: (ParalyticPoison, "Deathrattle: Your hero is Immune while attacking"),
						Trig_SilverleafPoison: (SilverleafPoison, "Deathrattle: After your hero attacks draw a card"),
						Death_ApothecaryHelbrim: (ApothecaryHelbrim, "Deathrattle: Add a random Poison to your hand"),
						Death_SpawnpoolForager: (SpawnpoolForager, "Deathrattle: Summon a 1/1 Tinyfin"),
						Death_KabalOutfitter: (KabalOutfitter, "Deathrattle: Give another random friendly minion +1/+1"),
						Death_DevouringEctoplasm: (DevouringEctoplasm, "Deathrattle: Summon a 2/2 Adventurer with random bonus effect"),
						Death_Felrattler: (Felrattler, "Deathrattle: Deal 1 damage to all enemy minions"),
						Death_FangboundDruid: (FangboundDruid, "Deathrattle: Reduce the cost of a random Beast in your hand by (2)"),
						Death_SeedcloudBuckler: (SeedcloudBuckler, "Deathrattle: Give your minions Divine Shield"),
						Death_KreshLordofTurtling: (KreshLordofTurtling, "Deathrattle: Equip a 2/5 Turtle Spike"),
						}

RankedSpells = [FuryRank1, LivingSeedRank1, TameBeastRank1, FlurryRank1, ConvictionRank1, CondemnRank1, \
				WickedStabRank1, ChainLightningRank1, ImpSwarmRank1, ConditioningRank1]

Barrens_Cards = [
		#Neutral
		KindlingElemental, FarWatchPost, HecklefangHyena, LushwaterMurcenary, LushwaterScout, OasisThrasher, Peon,
		TalentedArcanist, ToadoftheWilds, BarrensTrapper, CrossroadsGossiper, DeathsHeadCultist, HogRancher, Hog,
		HordeOperative, Mankrik, OlgraMankriksWife, MankrikConsumedbyHatred, MorshanWatchPost, WatchfulGrunt,
		RatchetPrivateer, SunwellInitiate, VenomousScorpid, BlademasterSamuro, CrossroadsWatchPost, DarkspearBerserker,
		GruntledPatron, InjuredMarauder, KazakusGolemShaper, SouthseaScoundrel, SpiritHealer, BarrensBlacksmith,
		BurningBladeAcolyte, Demonspawn, GoldRoadGrunt, RazormaneRaider, ShadowHunterVoljin, TaurajoBrave, KargalBattlescar,
		Lookout, PrimordialProtector,
		#Demon Hunter
		FuryRank1, FuryRank2, FuryRank3, Tuskpiercer, Razorboar, SigilofFlame, SigilofSilence, VileCall, RavenousVilefiend,
		RazorfenBeastmaster, KurtrusAshfallen, VengefulSpirit, DeathSpeakerBlackthorn,
		#Druid
		LivingSeedRank1, LivingSeedRank2, LivingSeedRank3, MarkoftheSpikeshell, RazormaneBattleguard, ThorngrowthSentries,
		ThornguardTurtle, GuffRunetotem, PlaguemawtheRotting, PridesFury, ThickhideKodo, CelestialAlignment,
		DruidofthePlains, DruidofthePlains_Taunt,
		#Hunter
		SunscaleRaptor, WoundPrey, SwiftHyena, KolkarPackRunner, ProspectorsCaravan, TameBeastRank1, TameBeastRank2,
		TameBeastRank3, TamedCrab, TamedScorpid, TamedThunderLizard, PackKodo, TavishStormpike, PiercingShot,
		WarsongWrangler, BarakKodobane,
		#Mage
		FlurryRank1, FlurryRank2, FlurryRank3, RunedOrb, Wildfire, ArcaneLuminary, OasisAlly, Rimetongue, FrostedElemental,
		RecklessApprentice, RefreshingSpringWater, VardenDawngrasp, MordreshFireEye,
		#Paladin
		ConvictionRank1, ConvictionRank2, ConvictionRank3, GallopingSavior, HolySteed, KnightofAnointment, SoldiersCaravan,
		SwordoftheFallen, NorthwatchCommander, CarielRoame, VeteranWarmedic, BattlefieldMedic, InvigoratingSermon,
		CannonmasterSmythe, NorthwatchSoldier,
		#Priest
		DesperatePrayer, CondemnRank1, CondemnRank2, CondemnRank3, SerenaBloodfeather, SoothsayersCaravan, DevouringPlague,
		VoidFlayer, Xyrella, PriestofAnshe, LightshowerElemental, PowerWordFortitude,
		#Rogue
		ParalyticPoison, Yoink, EfficientOctobot, SilverleafPoison, WickedStabRank1, WickedStabRank2, WickedStabRank3,
		FieldContact, SwinetuskShank, ApothecaryHelbrim, OilRigAmbusher, ScabbsCutterbutter,
		#Shaman
		SpawnpoolForager, DiremuckTinyfin, ChainLightningRank1, ChainLightningRank2, ChainLightningRank3, FiremancerFlurgl,
		SouthCoastChieftain, TinyfinsCaravan, AridStormer, NofinCanStopUs, Brukan, EarthRevenant, LilypadLurker,
		#Warlock
		AltarofFire, GrimoireofSacrifice, ApothecarysCaravan, ImpSwarmRank1, ImpFamiliar, ImpSwarmRank2, ImpSwarmRank3,
		BloodShardBristleback, KabalOutfitter, TamsinRoame, SoulRend, NeeruFireblade, BarrensScavenger,
		#Warrior
		WarsongEnvoy, BulkUp, ConditioningRank1, ConditioningRank2, ConditioningRank3, Rokara, OutridersAxe, Rancor,
		WhirlingCombatant, MorshanElite, StonemaulAnchorman, OverlordSaurfang,
		#Neutral
		MeetingStone, DevouringEctoplasm, ArchdruidNaralex, MutanustheDevourer, SelflessSidekick,
		#Demon Hunter
		SigilofSummoning, WailingDemon, Felrattler, TaintheartTormenter,
		#Druid
		FangboundDruid, LadyAnacondra, DeviateDreadfang, DeviateViper,
		#Hunter
		Serpentbloom, SindoreiScentfinder, VenomstrikeBow,
		#Mage
		FrostweaveDungeoneer, ShatteringBlast, Floecaster,
		#Paladin
		JudgmentofJustice, SeedcloudBuckler, PartyUp,
		#Priest
		ClericofAnshe, DevoutDungeoneer, AgainstAllOdds,
		#Rogue
		SavoryDeviateDelight, WaterMoccasin, ShroudofConcealment,
		#Shaman
		PerpetualFlame, WailingVapor, PrimalDungeoneer,
		#Warlock
		FinalGasp, UnstableShadowBlast, StealerofSouls,
		#Warrior
		ManatArms, WhetstoneHatchet, KreshLordofTurtling, TurtleSpike,
]

Barrens_Cards_Collectible = [
		#Neutral
		KindlingElemental, FarWatchPost, HecklefangHyena, LushwaterMurcenary, LushwaterScout, OasisThrasher, Peon,
		TalentedArcanist, ToadoftheWilds, BarrensTrapper, CrossroadsGossiper, DeathsHeadCultist, HogRancher, HordeOperative,
		Mankrik, MorshanWatchPost, RatchetPrivateer, SunwellInitiate, VenomousScorpid, BlademasterSamuro,
		CrossroadsWatchPost, DarkspearBerserker, GruntledPatron, InjuredMarauder, KazakusGolemShaper, SouthseaScoundrel,
		SpiritHealer, BarrensBlacksmith, BurningBladeAcolyte, GoldRoadGrunt, RazormaneRaider, ShadowHunterVoljin,
		TaurajoBrave, KargalBattlescar, PrimordialProtector,
		#Demon Hunter
		FuryRank1, Tuskpiercer, Razorboar, SigilofFlame, SigilofSilence, VileCall, RazorfenBeastmaster, KurtrusAshfallen,
		VengefulSpirit, DeathSpeakerBlackthorn,
		#Druid
		LivingSeedRank1, MarkoftheSpikeshell, RazormaneBattleguard, ThorngrowthSentries, GuffRunetotem, PlaguemawtheRotting,
		PridesFury, ThickhideKodo, CelestialAlignment, DruidofthePlains,
		#Hunter
		SunscaleRaptor, WoundPrey, KolkarPackRunner, ProspectorsCaravan, TameBeastRank1, PackKodo, TavishStormpike,
		PiercingShot, WarsongWrangler, BarakKodobane,
		#Mage
		FlurryRank1, RunedOrb, Wildfire, ArcaneLuminary, OasisAlly, Rimetongue, RecklessApprentice, RefreshingSpringWater,
		VardenDawngrasp, MordreshFireEye,
		#Paladin
		ConvictionRank1, GallopingSavior, KnightofAnointment, SoldiersCaravan, SwordoftheFallen, NorthwatchCommander,
		CarielRoame, VeteranWarmedic, InvigoratingSermon, CannonmasterSmythe,
		#Priest
		DesperatePrayer, CondemnRank1, SerenaBloodfeather, SoothsayersCaravan, DevouringPlague, VoidFlayer, Xyrella,
		PriestofAnshe, LightshowerElemental, PowerWordFortitude,
		#Rogue
		ParalyticPoison, Yoink, EfficientOctobot, SilverleafPoison, WickedStabRank1, FieldContact, SwinetuskShank,
		ApothecaryHelbrim, OilRigAmbusher, ScabbsCutterbutter,
		#Shaman
		SpawnpoolForager, ChainLightningRank1, FiremancerFlurgl, SouthCoastChieftain, TinyfinsCaravan, AridStormer,
		NofinCanStopUs, Brukan, EarthRevenant, LilypadLurker,
		#Warlock
		AltarofFire, GrimoireofSacrifice, ApothecarysCaravan, ImpSwarmRank1, BloodShardBristleback, KabalOutfitter,
		TamsinRoame, SoulRend, NeeruFireblade, BarrensScavenger,
		#Warrior
		WarsongEnvoy, BulkUp, ConditioningRank1, Rokara, OutridersAxe, Rancor, WhirlingCombatant, MorshanElite,
		StonemaulAnchorman, OverlordSaurfang,
		#Neutral
		MeetingStone, DevouringEctoplasm, ArchdruidNaralex, MutanustheDevourer, SelflessSidekick,
		#Demon Hunter
		SigilofSummoning, Felrattler, TaintheartTormenter,
		#Druid
		FangboundDruid, LadyAnacondra, DeviateDreadfang,
		#Hunter
		Serpentbloom, SindoreiScentfinder, VenomstrikeBow,
		#Mage
		FrostweaveDungeoneer, ShatteringBlast, Floecaster,
		#Paladin
		JudgmentofJustice, SeedcloudBuckler, PartyUp,
		#Priest
		ClericofAnshe, DevoutDungeoneer, AgainstAllOdds,
		#Rogue
		SavoryDeviateDelight, WaterMoccasin, ShroudofConcealment,
		#Shaman
		PerpetualFlame, WailingVapor, PrimalDungeoneer,
		#Warlock
		FinalGasp, UnstableShadowBlast, StealerofSouls,
		#Warrior
		ManatArms, WhetstoneHatchet, KreshLordofTurtling,
]