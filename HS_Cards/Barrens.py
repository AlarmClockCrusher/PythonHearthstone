from Parts.CardTypes import *
from Parts.TrigsAuras import *
from HS_Cards.AcrossPacks import Frog, SilverHandRecruit, Dream, Nightmare, YseraAwakens, LaughingSister, EmeraldDrake
from HS_Cards.Core import WaterElemental
from HS_Cards.Outlands import Trig_Imprisoned


class KazakusGolem(Minion):
	Class = "Neutral"
	def text(self): return type(self).Effects
		
	
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
		if game.turn == ID and not game.Counters.examCardPlays(ID, turnInd=game.turnInd, cond=lambda tup: "Taunt" in tup[4]):
			self.aura = GameManaAura_RazormaneBattleguard(game, ID)
			self.aura.auraAppears()
		add2ListinDict(self, game.trigsBoard[ID], "TurnStarts")
		
	
class ManaAura_LadyAnacondra(ManaAura):
	by = -2
	def applicable(self, target): return target.ID == self.keeper.ID and target.school == "Nature"
		
	
class Aura_WaterMoccasin(Aura_Conditional):
	signals, effGain, targets = ("MinionAppears", "MinionDisappears"), "Poisonous", "Self"
	def whichWay(self): #Decide the aura turns on(1) or off(-1), or does nothing(0)
		otherMinions = self.keeper.Game.minionsonBoard(self.keeper.ID, exclude=self.keeper)
		if otherMinions and self.on: return -1
		elif not otherMinions and not self.on: return 1
		else: return 0
		
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return self.keeper.onBoard and target.ID == self.keeper.ID and target is not self
		
	
class Frenzy(TrigBoard):
	signals, oneTime = ("MinionTakesDmg",), True
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		#假设是随从受伤时触发，不是受伤之后触发
		return self.keeper.onBoard and target is self.keeper and target.health > 0 and not target.dead
		
	def trig(self, signal, ID, subject, target, num, comment, choice):
		if self.canTrig(signal, ID, subject, target, num, comment, choice):
			btn, GUI = self.keeper.btn, self.keeper.Game.GUI
			if btn and "SpecTrig" in btn.icons:
				btn.icons["SpecTrig"].trigAni()
			self.keeper.losesTrig(self)
			self.effect(signal, ID, subject, target, num, comment, 0)
		
	
class Trig_ForgeUpgrade_Hand(TrigHand):
	signals = ("ManaXtlsCheck",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		if kpr.inHand and ID == kpr.ID:
			xtls, typeSpell = kpr.Game.Manas.manasUpper[kpr.ID], type(kpr)
			return (xtls >= 10 and typeSpell.upgrade_10) or (xtls >= 5 and typeSpell.upgrade_5)
		return False
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		card = self.keeper
		xtls, typeSpell = card.Game.Manas.manasUpper[card.ID], type(card)
		upgrade = typeSpell.upgrade_10 if xtls >= 10 else typeSpell.upgrade_5
		(newCard := upgrade(card.Game, card.ID)).inheritEnchantmentsfrom(card)
		card.Game.Hand_Deck.replace1CardinHand(card, newCard)
		
	
class Trig_ForgeUpgrade_Deck(TrigDeck):
	signals = ("ManaXtlsCheck",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		if kpr.inDeck and ID == kpr.ID:
			xtls, typeSpell = kpr.Game.Manas.manasUpper[kpr.ID], type(kpr)
			return (xtls >= 10 and typeSpell.upgrade_10) or (xtls >= 5 and typeSpell.upgrade_5)
		return False
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		card = self.keeper
		xtls, typeSpell = card.Game.Manas.manasUpper[card.ID], type(card)
		upgrade = typeSpell.upgrade_10 if xtls >= 10 else typeSpell.upgrade_5
		(newCard := upgrade(card.Game, card.ID)).inheritEnchantmentsfrom(card)
		if (i := indin(card, card.Game.Hand_Deck.decks[card.ID])) > -1:
			card.Game.Hand_Deck.replaceCardsinDeck(card.ID, (i,), (newCard,))
		
	
class Trig_FarWatchPost(TrigBoard):
	signals = ("HandCheck",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return comment == "Enter_Draw" and ID != kpr.ID and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		if target.mana < 10: ManaMod(target, by=+1).applies()
		
	
class Trig_LushwaterScout(TrigBoard):
	signals = ("ObjSummoned",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return "Murloc" in subject.race and ID == kpr.ID and subject is not kpr and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.giveEnchant(subject, 1, 0, effGain="Rush", source=LushwaterScout)
		
	
class Trig_OasisThrasher(Frenzy):
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).dealsDamage(kpr.heroes[3-kpr.ID], 3)
		
	
class Trig_Peon(Frenzy):
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).addCardtoHand(numpyChoice(self.rngPool(kpr.Game.heroes[kpr.ID].Class + " Spells")), kpr.ID)
		
	
class Trig_CrossroadsGossiper(TrigBoard):
	signals = ("SecretRevealed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return ID == kpr.ID and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).giveEnchant(kpr, statEnchant=Enchantment_Exclusive(CrossroadsGossiper, 2, 2))
		
	
class Trig_MorshanWatchPost(TrigBoard):
	signals = ("CardBeenPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return comment == "Minion" and ID != kpr.ID and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).summon(WatchfulGrunt(kpr.Game, kpr.ID))
		
	
class Trig_SunwellInitiate(Frenzy):
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).giveEnchant(kpr, effGain="Divine Shield", source=SunwellInitiate)
		
	
class Trig_BlademasterSamuro(Frenzy):
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		if (atk := self.keeper.attack) > 0:
			kpr.dealsDamage(kpr.Game.minionsonBoard(3-kpr.ID), atk)
		
	
class Trig_CrossroadsWatchPost(TrigBoard):
	signals = ("CardPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return comment == "Spell" and ID != kpr.ID and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).giveEnchant(kpr.Game.minionsonBoard(kpr.ID), statEnchant=Enchantment(CrossroadsWatchPost, 1, 1))
		
	
class Trig_GruntledPatron(Frenzy):
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).summon(GruntledPatron(kpr.Game, kpr.ID))
		
	
class Trig_SpiritHealer(TrigBoard):
	signals = ("CardBeenPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return ID == kpr.ID and kpr.Game.cardinPlay.school == "Holy"
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		if minions := self.keeper.Game.minionsonBoard(ID):
			kpr.giveEnchant(numpyChoice(minions), statEnchant=Enchantment_Exclusive(SpiritHealer, 0, 2))
		
	
class Trig_BarrensBlacksmith(Frenzy):
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).giveEnchant(kpr.Game.minionsonBoard(kpr.ID, exclude=kpr), 2, 2, source=BarrensBlacksmith)
		
	
class Trig_GoldRoadGrunt(Frenzy):
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).giveHeroAttackArmor(kpr.ID, armor=num)
		
	
class Trig_RazormaneRaider(Frenzy):
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		if objs := kpr.Game.charsAlive(3-kpr.ID):
			kpr.Game.battle(kpr, numpyChoice(objs))
		
	
class Trig_TaurajoBrave(Frenzy):
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		if minions := kpr.Game.minionsAlive(3 - kpr.ID):
			kpr.Game.kill(kpr, numpyChoice(minions))
		
	
class Trig_GuffRunetotem(TrigBoard):
	signals = ("CardBeenPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID and kpr.Game.cardinPlay.school == "Nature"
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		if minions := kpr.Game.minionsonBoard(kpr.ID, exclude=kpr):
			kpr.giveEnchant(numpyChoice(minions), statEnchant=Enchantment_Exclusive(GuffRunetotem, 2, 2))
		
	
class Trig_PlaguemawtheRotting(TrigBoard):
	signals = ("ObjDied",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		#Technically, minion has to disappear before dies. But just in case.
		return target.category == "Minion" and kpr.onBoard and target is not kpr and target.ID == kpr.ID and target.effects["Taunt"] > 0
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		Copy = type(target)(kpr.Game, kpr.ID)
		Copy.effects["Taunt"] = 0
		kpr.summon(Copy)
		
	
class Trig_DruidofthePlains(Frenzy):
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).transform(kpr, DruidofthePlains_Taunt(kpr.Game, kpr.ID))
		
	
class Trig_SunscaleRaptor(Frenzy):
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		game = self.keeper.Game
		if kpr.onBoard: newAtt, newHealth = kpr.attack + 2, kpr.health + 1
		else: newAtt, newHealth = kpr.attack_0 + 2, kpr.health_0 + 1
		newIndex = "THE_BARRENS~Hunter~Minion~1~%d~%d~Beast~Sunscale Raptor~Uncollectible"%(newAtt, newHealth)
		subclass = type("SunscaleRaptor__%d_%d"%(newAtt, newHealth), (SunscaleRaptor,),
						{"attack": newAtt, "health": newHealth, "index": newIndex}
						)
		kpr.shuffleintoDeck(subclass(game, kpr.ID))
		
	
class Trig_KolkarPackRunner(TrigBoard):
	signals = ("CardBeenPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return comment == "Spell" and ID == kpr.ID and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).summon(SwiftHyena(kpr.Game, kpr.ID))
		
	
class Trig_ProspectorsCaravan(TrigBoard):
	signals = ("TurnStarts",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		kpr.giveEnchant([card for card in kpr.Game.Hand_Deck.hands[kpr.ID] if card.category == "Minion"],
						statEnchant=Enchantment(ProspectorsCaravan, 1, 1), add2EventinGUI=False)
		
	
class Trig_TavishStormpike(TrigBoard):
	signals = ("MinionAttackedHero", "MinionAttackedMinion",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID and "Beast" in subject.race
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.try_SummonfromOwn(cond=lambda card: "Beast" in card.race and card.mana == subject.mana - 1)
		
	
class Trig_OasisAlly(Trig_Secret):
	signals = ("MinionAttacksMinion", "HeroAttacksMinion",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):  #target here holds the actual target object
		kpr = self.keeper
		#The target has to a friendly minion and there is space on board to summon minions.
		return kpr.ID != kpr.Game.turn and target[0].category == "Minion" and target[0].ID == kpr.ID and kpr.Game.space(kpr.ID) > 0
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).summon(WaterElemental(kpr.Game, kpr.ID))
		
	
class Trig_Rimetongue(TrigBoard):
	signals = ("CardBeenPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID and kpr.Game.cardinPlay.school == "Frost"
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).summon(FrostedElemental(kpr.Game, kpr.ID))
		
	
class Trig_FrostedElemental(TrigBoard):
	signals = ("MinionTakesDmg", "HeroTakesDmg",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return subject is self.keeper
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.freeze(target)
		
	
class Trig_GallopingSavior(Trig_Secret):
	signals = ("CardBeenPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		secret = self.keeper
		return ID == secret.Game.turn != secret.ID and secret.Game.space(secret.ID) > 0 \
			   and secret.Game.Counter.examCardPlays(3 - secret.ID, turnInd=secret.Game.turnInd, veri_sum_ls=1) > 2
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).summon(HolySteed(kpr.Game, kpr.ID))
		
	
class Trig_SoldiersCaravan(TrigBoard):
	signals = ("TurnStarts",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		game, ID = (kpr := self.keeper).Game, kpr.ID
		kpr.summon([SilverHandRecruit(game, ID) for _ in (0, 1)], relative="<>")
		
	
class Trig_SwordoftheFallen(TrigBoard):
	signals = ("HeroAttackedMinion", "HeroAttackedHero",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return subject is kpr.Game.heroes[kpr.ID] and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).Game.Secrets.deploySecretsfromDeck(kpr.ID, initiator=kpr)
		
	
class Trig_CarielRoame(TrigBoard):
	signals = ("MinionAttackingMinion", "MinionAttackingHero",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return subject is kpr and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		for card in kpr.Game.Hand_Deck.hands[kpr.ID]:
			if card.school == "Holy": ManaMod(card, by=-1).applies()
		
	
class Trig_VeteranWarmedic(TrigBoard):
	signals = ("CardBeenPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID and kpr.Game.cardinPlay.school == "Holy"
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).summon(BattlefieldMedic(kpr.Game, kpr.ID))
		
	
class Trig_SoothsayersCaravan(TrigBoard):
	signals = ("TurnStarts",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		keeper = self.keeper
		if spells := [card for card in keeper.Game.Hand_Deck.decks[3-keeper.ID] if card.category == "Spell"]:
			keeper.addCardtoHand(keeper.copyCard(numpyChoice(spells), keeper.ID), keeper.ID)
		
	
class Trigger_PowerWordFortitude(TrigHand):
	signals = ("HandCheck",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return self.keeper.inHand and ID == self.keeper.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.Game.Manas.calcMana_Single(self.keeper)
		
	
class Trig_ParalyticPoison(TrigBoard):
	description = "Your hero is Immune while attacking"
	signals, nextAniWaits = ("BattleStarted", "BattleFinished",), True
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return subject is kpr.Game.heroes[kpr.ID] and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		if signal == "BattleStarted": subject.getsEffect("Immune")
		else: subject.losesEffect("Immune")
		
	
class Trig_SwapBackPowerAfter2Uses(Trig_Countdown):
	signals, counter, description = ("HeroUsedAbility",), 2, "Swap back after 2 uses"
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return subject is self.keeper
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		if self.counter < 1:
			kpr.powerReplaced.ID = kpr.ID
			self.keeper.powerReplaced.replacePower()
		
	
class Trig_EfficientOctobot(Frenzy):
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		for card in kpr.Game.Hand_Deck.hands[kpr.ID]:
			ManaMod(card, by=-1).applies()
		
	
class Trig_SilverleafPoison(TrigBoard):
	description = "After your hero attacks draw a card"
	signals = ("HeroAttackedMinion", "HeroAttackedHero",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).Game.Hand_Deck.drawCard(kpr.ID)
		
	
class Trig_FieldContact(TrigBoard):
	signals = ("CardBeenPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID and ("~Battlecry" in (index := kpr.Game.cardinPlay.index) or "~Combo" in index)
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).Game.Hand_Deck.drawCard(kpr.ID)
		
	
class Trig_SwinetuskShank(TrigBoard):
	signals = ("CardBeenPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return comment == "Spell" and "Poison" in kpr.Game.cardinPlay.name and ID == kpr.ID and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).giveEnchant(kpr, statEnchant=Enchantment_Exclusive(SwinetuskShank, 0, 1))
		
	
class Trig_FiremancerFlurgl(TrigBoard):
	signals = ("CardBeenPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID and "Murloc" in kpr.Game.cardinPlay.race
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).dealsDamage(kpr.Game.charsAlive(3-kpr.ID), 1)
		
	
class Trig_TinyfinsCaravan(TrigBoard):
	signals = ("TurnStarts",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.drawCertainCard(lambda card: "Murloc" in card.race)
		
	
class Trig_ApothecarysCaravan(TrigBoard):
	signals = ("TurnStarts",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.try_SummonfromOwn(cond=lambda card: card.category == "Minion" and card.mana == 1)
		
	
class Trig_TamsinRoame(TrigBoard):
	signals = ("CardPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID and kpr.Game.cardinPlay.school == "Shadow" and num[0] > 0
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).addCardtoHand(Copy := kpr.copyCard(kpr, kpr.ID), kpr.ID)
		if Copy.inHand: ManaMod(Copy, to=0).applies()
		
	
class Trig_BurningBladePortal(TrigBoard):
	signals = ("TurnEnds",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.summon([ImpFamiliar(self.keeper.Game, self.keeper.ID) for i in range(6)], relative="<>")
		
	
class Trig_BarrensScavenger(TrigHand):
	signals = ("",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.inHand and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).Game.Manas.calcMana_Single(kpr)
		
	
class Trig_WarsongEnvoy(Frenzy):
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		buff = 1 if kpr.Game.heroes[kpr.ID].dmgTaken > 0 else 0
		buff += sum(minion.health < minion.health_max for minion in kpr.Game.minionsonBoard(kpr.ID))
		kpr.giveEnchant(kpr, buff, 0, source=WarsongEnvoy)
		
	
class Trig_Rokara(TrigBoard):
	signals = ("MinionAttackedHero", "MinionAttackedMinion",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID and subject.health > 0 and not subject.dead
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.giveEnchant(subject, statEnchant=Enchantment_Exclusive(Rokara, 1, 1))
		
	
class Trig_OutridersAxe(TrigBoard):
	signals = ("HeroAttackedMinion",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return subject is kpr.Game.heroes[kpr.ID] and kpr.onBoard and target.category == "Minion" and (target.health < 1 or target.dead)
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).Game.Hand_Deck.drawCard(kpr.ID)
		
	
class Trig_WhirlingCombatant(Frenzy):
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).dealsDamage(kpr.Game.minionsonBoard(exclude=kpr), 1)
		
	
class Trig_StonemaulAnchorman(Frenzy):
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).Game.Hand_Deck.drawCard(kpr.ID)
		
	
class Trig_MeetingStone(TrigBoard):
	signals = ("TurnEnds",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).addCardtoHand(numpyChoice(PartyUp.adventurers), kpr.ID)
		
	
class Trig_SleepingNaralex(TrigBoard):
	signals = ("TurnEnds",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID  #会在我方回合开始时进行苏醒
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).addCardtoHand(numpyChoice((Dream, Nightmare, YseraAwakens, LaughingSister, EmeraldDrake)), kpr.ID)
		
	
class Trig_DeviateDreadfang(TrigBoard):
	signals = ("CardBeenPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID and kpr.Game.cardinPlay.school == "Nature"
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).summon(DeviateViper(kpr.Game, kpr.ID))
		
	
class Trig_SindoreiScentfinder(Frenzy):
	def effect(self, signal, ID, subject, target, num, comment, choice):
		game, ID = (kpr := self.keeper).Game, kpr.ID
		kpr.summon([SwiftHyena(game, ID) for i in (0, 1, 2, 3)], relative="<>")
		
	
class Trig_Floecaster(TrigHand): #"HeroAppears" only is sent when hero is replaced. It's equivalent to "HeroDisappars" (Although don't have this)
	signals = ("MinionAppears", "MinionDisappears", "HeroAppears", "CharEffectCheck",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.inHand and target.ID != kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).Game.Manas.calcMana_Single(kpr)
		
	
class Trig_JudgmentofJustice(Trig_Secret):
	signals = ("MinionAttackingMinion", "MinionAttackingHero",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.ID != kpr.Game.turn == ID and subject.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.setStat(subject, (1, 1), source=JudgmentofJustice)
		
	
class Trig_WailingVapor(TrigBoard):
	signals = ("CardBeenPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID and kpr != kpr.Game.cardinPlay and "Elemental" in kpr.Game.cardinPlay.race
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).giveEnchant(kpr, statEnchant=Enchantment_Exclusive(WailingVapor, 1, 0))
		
	
class Trig_StealerofSouls(TrigBoard):
	signals = ("HandCheck",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return comment == "Enter_Draw" and ID == kpr.ID and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.giveEnchant(target, effGain="Cost Health Instead", source=StealerofSouls)
		
	
class Trig_WhetstoneHatchet(TrigBoard):
	signals = ("HeroAttackedMinion", "HeroAttackedHero",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return subject is kpr.Game.heroes[kpr.ID] and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		if minions := [card for card in kpr.Game.Hand_Deck.hands[kpr.ID] if card.category == "Minion"]:
			self.keeper.giveEnchant(numpyChoice(minions), 1, 0, source=WhetstoneHatchet, add2EventinGUI=False)
		
	
class Trig_KreshLordofTurtling(Frenzy):
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).giveHeroAttackArmor(kpr.ID, armor=8)
		
	
class Death_DeathsHeadCultist(Deathrattle):
	description = "Deathrattle: Restore 4 Health to your hero"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).heals(kpr.heroes[kpr.ID], kpr.calcHeal(4))
		
	
class Death_DarkspearBerserker(Deathrattle):
	description = "Deathrattle: Deal 5 damage to your hero"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).dealsDamage(kpr.heroes[3-kpr.ID], 5)
		
	
class Death_BurningBladeAcolyte(Deathrattle):
	description = "Deathrattle: Summon a 5/8 Demonspawn with Taunt"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).summon(Demonspawn(kpr.Game, kpr.ID))
		
	
class Death_Tuskpiercer(Deathrattle):
	description = "Deathrattle: Draw a Deathrattle minion"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.drawCertainCard(lambda card: card.category == "Minion" and card.deathrattles)
		
	
class Death_Razorboar(Deathrattle):
	description = "Deathrattle: Summon a Deathrattle minion that costs (3) or less from your hand"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.try_SummonfromOwn(hand_deck=0,
			cond=lambda card: card.category == "Minion" and card.deathrattles and card.mana < 4)
		
	
class Death_RazorfenBeastmaster(Deathrattle):
	description = "Deathrattle: Summon a Deathrattle minion that costs (4) or less from your hand"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.try_SummonfromOwn(hand_deck=0,
			cond=lambda card: card.category == "Minion" and card.deathrattles and card.mana < 5)
		
	
class Death_ThickhideKodo(Deathrattle):
	description = "Deathrattle: Gain 5 Armor"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.giveHeroAttackArmor(self.keeper.ID, armor=5)
		
	
class Death_NorthwatchSoldier(Deathrattle):
	description = "Deathrattle: Transform back into secret"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		if self.memory:
			self.memory.ID = self.keeper.ID
			self.memory.playedEffect()
		
	
class Death_LightshowerElemental(Deathrattle):
	description = "Deathrattle: Restore 8 Health to all friendly characters"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).heals(kpr.Game.charsonBoard(kpr.ID), kpr.calcHeal(8))
		
	
class Death_ApothecaryHelbrim(Deathrattle):
	description = "Deathrattle: Add a random Poison to your hand"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.addCardtoHand(numpyChoice(self.rngPool("Poisons")), self.keeper.ID)
		
	
class Death_SpawnpoolForager(Deathrattle):
	description = "Deathrattle: Summon a 1/1 Tinyfin"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).summon(DiremuckTinyfin(kpr.Game, kpr.ID))
		
	
class Death_KabalOutfitter(Deathrattle):
	description = "Deathrattle: Give another random friendly minion +1/+1"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		if minions := (kpr := self.keeper).Game.minionsonBoard(kpr.ID, exclude=kpr):
			kpr.giveEnchant(numpyChoice(minions), 1, 1, source=KabalOutfitter)
		
	
class Death_DevouringEctoplasm(Deathrattle):
	description = "Deathrattle: Summon a 2/2 Adventurer with random bonus effect"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).summon(numpyChoice(PartyUp.adventurers)(kpr.Game, kpr.ID))
		
	
class Death_Felrattler(Deathrattle):
	description = "Deathrattle: Deal 1 damage to all enemy minions"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).dealsDamage(kpr.Game.minionsonBoard(3-kpr.ID), 1)
		
	
class Death_FangboundDruid(Deathrattle):
	description = "Deathrattle: Reduce the cost of a random Beast in your hand by (2)"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		if cards := self.keeper.findCards2ReduceMana(lambda card: "Beast" in card.race):
			ManaMod(numpyChoice(cards), by=-2).applies()
		
	
class Death_SeedcloudBuckler(Deathrattle):
	description = "Deathrattle: Give your minions Divine Shield"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).giveEnchant(kpr.Game.minionsonBoard(kpr.ID), effGain="Divine Shield",
								source=SeedcloudBuckler)
		
	
class Death_KreshLordofTurtling(Deathrattle):
	description = "Deathrattle: Equip a 2/5 Turtle Spike"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).equipWeapon(TurtleSpike(kpr.Game, kpr.ID))
		
	
class GameManaAura_KindlingElemental(GameManaAura_OneTime):
	by, temporary = -1, False
	def applicable(self, target): return target.ID == self.ID and "Elemental" in target.race
		
	
class TalentedArcanist_Effect(TrigEffect):
	signals, counter, trigType = ("SpellBeenCast",), 2, "Conn&TurnEnd&OnlyKeepOne"
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return ID == self.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.Game.heroes[self.ID].losesEffect("Spell Damage", amount=2)
		self.disconnect()
		
	def trigEffect(self):
		self.Game.heroes[self.ID].losesEffect("Spell Damage", amount=2)
		
	
class SigilofSilence_Effect(TrigEffect):
	trigType = "TurnStart&OnlyKeepOne"
	def trigEffect(self):
		self.Game.silenceMinions(self.Game.minionsonBoard(3 - self.ID))
		
	
class SigilofFlame_Effect(TrigEffect):
	trigType = "TurnStart&OnlyKeepOne"
	def trigEffect(self):
		self.card.dealsDamage(self.Game.minionsonBoard(3-self.ID), self.card.calcDamage(3))
		
	
class SigilofSummoning_Effect(TrigEffect):
	trigType = "TurnStart&OnlyKeepOne"
	def trigEffect(self):
		self.card.summon([WailingDemon(self.Game, self.ID) for _ in (0, 1)])
		
	
class ShroudofConcealment_Effect(TrigEffect):
	signals, counter, trigtype = ("CardBeenPlayed",), 2, "Conn&TurnEnd"
	def __init__(self, Game, ID, memory=()):
		super().__init__(Game, ID)
		self.memory = memory
		
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return ID == self.ID and subject in self.memory
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		subject.getsEffect("Temp Stealth", source=type(self))
		self.memory.remove(subject)
		if not self.memory: self.disconnect()
		
	def assistCreateCopy(self, Copy):
		Copy.memory = [card.createCopy(Copy.Game) for card in self.memory]
		
	
class GameManaAura_ScabbsCutterbutter(GameManaAura_OneTime):
	by = -2
	def applicable(self, target): return target.ID == self.ID
		
	
class GameManaAura_RazormaneBattleguard(GameManaAura_OneTime):
	by = -2
	def applicable(self, target): return target.ID == self.ID and target.category == "Minion" and target.effects["Taunt"] > 0
		
	
class Spell_Forge(Spell):
	upgrade_5 = upgrade_10 = None
	trigHand, trigDeck = Trig_ForgeUpgrade_Hand, Trig_ForgeUpgrade_Deck
	def entersHand(self, isGameEvent=True):
		#当你之前的未升级法术在之后满足升级条件的回合打出时也不会被升级。
		#会在手牌和牌库里面升级（在高费回合抽上手的时候直接就是升级过后的）
		#生成过程中直接随机加入手牌的时候也是已经升级完毕的。 （不能理解。就当这个不存在）
		#被发现时即使水晶数满足升级条件也要在加入手牌之后才升级。
		#综上所述，应该把升级法术写成在手牌和牌库中都可以升级。加入手牌时entersHand可以升级
		xtls, typeSelf = self.Game.Manas.manasUpper[self.ID], type(self)
		if xtls >= 10 and typeSelf.upgrade_10:
			card = typeSelf.upgrade_10(self.Game, self.ID)
			card.creator = self.creator
		elif xtls >= 5 and typeSelf.upgrade_5:
			card = typeSelf.upgrade_5(self.Game, self.ID)
			card.creator = self.creator
		else: card = self
		return Card.entersHand(card, isGameEvent=True)
		
	def entersDeck(self):
		xtls, typeSelf = self.Game.Manas.manasUpper[self.ID], type(self)
		if xtls >= 10 and typeSelf.upgrade_10:
			card = typeSelf.upgrade_10(self.Game, self.ID)
			card.creator = self.creator
		elif xtls >= 5 and typeSelf.upgrade_5:
			card = typeSelf.upgrade_5(self.Game, self.ID)
			card.creator = self.creator
		else: card = self
		return Card.entersDeck(card)
		
	
class Spell_Sigil(Spell):
	def available(self):
		typeSelf = type(self)
		return not any(isinstance(trig, typeSelf) for trig in self.Game.turnStartTrigger)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		type(self).trigEffect(self.Game, self.ID).connect()
		
	
class KindlingElemental(Minion):
	Class, race, name = "Neutral", "Elemental", "Kindling Elemental"
	mana, attack, health = 1, 1, 2
	name_CN = "火光元素"
	numTargets, Effects, description = 0, "", "Battlecry: Your next Elemental costs (1) less"
	index = "Battlecry"
	trigEffect = GameManaAura_KindlingElemental
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		GameManaAura_KindlingElemental(self.Game, self.ID).auraAppears()
		
	
class FarWatchPost(Minion):
	Class, race, name = "Neutral", "", "Far Watch Post"
	mana, attack, health = 2, 2, 3
	numTargets, Effects, description = 0, "Can't Attack", "Can't attack. After your opponent draws a card, it costs (1) more (up to 10)"
	name_CN = "前沿哨所"
	trigBoard = Trig_FarWatchPost
	
	
class HecklefangHyena(Minion):
	Class, race, name = "Neutral", "Beast", "Hecklefang Hyena"
	mana, attack, health = 2, 2, 4
	name_CN = "乱齿土狼"
	numTargets, Effects, description = 0, "", "Battlecry: Deal 3 damage to your hero"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(self.Game.heroes[self.ID], 3)
		
	
class LushwaterMurcenary(Minion):
	Class, race, name = "Neutral", "Murloc", "Lushwater Murcenary"
	mana, attack, health = 2, 3, 2
	name_CN = "甜水鱼人斥侯"
	numTargets, Effects, description = 0, "", "Battlecry: If you control a Murloc, gain +1/+1"
	index = "Battlecry"
	def effCanTrig(self):
		self.effectViable = any("Murloc" in minion.race for minion in self.Game.minionsonBoard(self.ID))
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if any("Murloc" in minion.race and minion is not self for minion in self.Game.minionsonBoard(self.ID)):
			self.giveEnchant(self, 1, 1, source=LushwaterMurcenary)
		
	
class LushwaterScout(Minion):
	Class, race, name = "Neutral", "Murloc", "Lushwater Scout"
	mana, attack, health = 2, 1, 3
	numTargets, Effects, description = 0, "", "After you summon a Murloc, give it +1 Attack and Rush"
	name_CN = "甜水鱼人斥侯"
	trigBoard = Trig_LushwaterScout
	
	
class OasisThrasher(Minion):
	Class, race, name = "Neutral", "Beast", "Oasis Thrasher"
	mana, attack, health = 2, 2, 3
	numTargets, Effects, description = 0, "", "Frenzy: Deal 3 damage to the enemy hero"
	name_CN = "绿洲长尾鳄"
	index = "Frenzy"
	trigBoard = Trig_OasisThrasher
	
	
class Peon(Minion):
	Class, race, name = "Neutral", "", "Peon"
	mana, attack, health = 2, 2, 3
	numTargets, Effects, description = 0, "", "Frenzy: Add a random spell from your class to your hand"
	name_CN = "苦工"
	index = "Frenzy"
	trigBoard = Trig_Peon
	
	
class TalentedArcanist(Minion):
	Class, race, name = "Neutral", "", "Talented Arcanist"
	mana, attack, health = 2, 1, 3
	name_CN = "精明的奥术师"
	numTargets, Effects, description = 0, "", "Battlecry: Your next spell this turn has Spell Damage +2"
	index = "Battlecry"
	trigEffect = TalentedArcanist_Effect
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.Game.heroes[self.ID].getsEffect("Spell Damage", 2)
		TalentedArcanist_Effect(self.Game, self.ID).connect()
		
	
class ToadoftheWilds(Minion):
	Class, race, name = "Neutral", "Beast", "Toad of the Wilds"
	mana, attack, health = 2, 2, 2
	name_CN = "狂野蟾蜍"
	numTargets, Effects, description = 0, "Taunt", "Taunt. Battlecry: If you're holding a Nature spell, gain +2 Health"
	index = "Battlecry"
	def effCanTrig(self):
		self.effectViable = any(card.school == "Nature" for card in self.Game.Hand_Deck.hands[self.ID])
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if any(card.school == "Nature" for card in self.Game.Hand_Deck.hands[self.ID]):
			self.giveEnchant(self, 0, 2, source=ToadoftheWilds)
		
	
class BarrensTrapper(Minion):
	Class, race, name = "Neutral", "", "Barrens Trapper"
	mana, attack, health = 3, 2, 4
	numTargets, Effects, description = 0, "", "Your Deathrattle cards cost (1) less"
	name_CN = "贫瘠之地诱捕者"
	aura = ManaAura_BarrensTrapper
	
	
class CrossroadsGossiper(Minion):
	Class, race, name = "Neutral", "", "Crossroads Gossiper"
	mana, attack, health = 3, 4, 3
	name_CN = "十字路口大嘴巴"
	numTargets, Effects, description = 0, "", "After a friendly Secret is revealed, gain +2/+2"
	index = "Battlecry"
	trigBoard = Trig_CrossroadsGossiper
	
	
class DeathsHeadCultist(Minion):
	Class, race, name = "Neutral", "Quilboar", "Death's Head Cultist"
	mana, attack, health = 3, 2, 4
	numTargets, Effects, description = 0, "Taunt", "Deathrattle: Restore 4 Health to your hero"
	name_CN = "亡首教徒"
	deathrattle = Death_DeathsHeadCultist
	
	
class HogRancher(Minion):
	Class, race, name = "Neutral", "", "Hog Rancher"
	mana, attack, health = 3, 3, 2
	name_CN = "放猪牧人"
	numTargets, Effects, description = 0, "", "Battlecry: Summon a 2/1 Hog with Rush"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon(Hog(self.Game, self.ID))
		
	
class Hog(Minion):
	Class, race, name = "Neutral", "Beast", "Hog"
	mana, attack, health = 1, 2, 1
	name_CN = "小猪"
	numTargets, Effects, description = 0, "Rush", "Rush"
	index = "Uncollectible"
	
	
class HordeOperative(Minion):
	Class, race, name = "Neutral", "", "Horde Operative"
	mana, attack, health = 3, 3, 4
	name_CN = "部落特工"
	numTargets, Effects, description = 0, "", "Battlecry: Copy your opponent's secrets and put them into play"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		#假设先复制最早入场的奥秘
		secretHD = self.Game.Secrets
		for secret in secretHD.secrets[3-self.ID][:]:
			if secretHD.areaNotFull(self.ID):
				if not secretHD.sameSecretExists(secret, self.ID):
					self.copyCard(secret, self.ID).playedEffect()
			else: break
		
	
class Mankrik(Minion):
	Class, race, name = "Neutral", "", "Mankrik"
	mana, attack, health = 3, 3, 4
	name_CN = "曼克里克"
	numTargets, Effects, description = 0, "", "Battlecry: Help Mankrik find his wife! She was last seen somewhere in your deck"
	index = "Battlecry~Legendary"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.shuffleintoDeck(OlgraMankriksWife(self.Game, self.ID))
		
	
class OlgraMankriksWife(Spell):
	Class, school, name = "Neutral", "", "Olgra, Mankrik's Wife"
	numTargets, mana, Effects = 0, 3, ""
	name_CN = "奥格拉，曼克里克的妻子"
	description = "Casts When Drawn. Summon a 3/10 Mankrik, who immediately attaks the enemy hero"
	index = "Uncollectible"
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		minion = MankrikConsumedbyHatred(self.Game, self.ID)
		self.summon(minion)
		if minion.canBattle() and (hero := self.Game.heroes[3-self.ID]).canBattle():
			self.Game.battle(minion, hero)
		
	
class MankrikConsumedbyHatred(Minion):
	Class, race, name = "Neutral", "", "Mankrik, Consumed by Hatred"
	mana, attack, health = 5, 3, 7
	name_CN = "曼克里克"
	numTargets, Effects, description = 0, "", ""
	index = "Legendary~Uncollectible"
	
	
class MorshanWatchPost(Minion):
	Class, race, name = "Neutral", "", "Mor'shan Watch Post"
	mana, attack, health = 3, 3, 4
	numTargets, Effects, description = 0, "Can't Attack", "Can't attack. After your opponent plays a minion, summon a 2/2 Grunt"
	name_CN = "莫尔杉哨所"
	trigBoard = Trig_MorshanWatchPost
	
	
class WatchfulGrunt(Minion):
	Class, race, name = "Neutral", "", "Watchful Grunt"
	mana, attack, health = 2, 2, 2
	name_CN = "警觉的步兵"
	numTargets, Effects, description = 0, "", ""
	index = "Uncollectible"
	
	
class RatchetPrivateer(Minion):
	Class, race, name = "Neutral", "Pirate", "Ratchet Privateer"
	mana, attack, health = 3, 4, 3
	name_CN = "棘齿城私掠者"
	numTargets, Effects, description = 0, "", "Battlecry: Give your weapon +1 Attack"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if weapon := self.Game.availableWeapon(self.ID): self.giveEnchant(weapon, 1, 0, source=RatchetPrivateer)
		
	
class SunwellInitiate(Minion):
	Class, race, name = "Neutral", "", "Sunwell Initiate"
	mana, attack, health = 3, 3, 4
	numTargets, Effects, description = 0, "", "Frenzy: Gain Divine Shield"
	name_CN = "太阳之井新兵"
	index = "Frenzy"
	trigBoard = Trig_SunwellInitiate
	
	
class VenomousScorpid(Minion):
	Class, race, name = "Neutral", "Beast", "Venomous Scorpid"
	mana, attack, health = 3, 1, 3
	name_CN = "剧毒魔蝎"
	numTargets, Effects, description = 0, "Poisonous", "Poisonous. Battlecry: Discover a spell"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.discoverNew(comment, lambda : self.rngPool(class4Discover(self) + " Spells"))
		
	
class BlademasterSamuro(Minion):
	Class, race, name = "Neutral", "", "Blademaster Samuro"
	mana, attack, health = 4, 1, 6
	name_CN = "剑圣萨穆罗"
	numTargets, Effects, description = 0, "Rush", "Rush. Frenzy: Deal damage equal to this minion's Attack equal to all enemy minions"
	index = "Frenzy~Legendary"
	trigBoard = Trig_BlademasterSamuro
	
	
class CrossroadsWatchPost(Minion):
	Class, race, name = "Neutral", "", "Crossroads Watch Post"
	mana, attack, health = 4, 4, 6
	numTargets, Effects, description = 0, "Can't Attack", "Can't attack. Whenever you opponent casts a spell, give your minions +1/+1"
	name_CN = "十字路口哨所"
	trigBoard = Trig_CrossroadsWatchPost
	
	
class DarkspearBerserker(Minion):
	Class, race, name = "Neutral", "", "Darkspear Berserker"
	mana, attack, health = 4, 5, 7
	numTargets, Effects, description = 0, "", "Deathrattle: Deal 5 damage to your hero"
	name_CN = "暗矛狂战士"
	deathrattle = Death_DarkspearBerserker
	
	
class GruntledPatron(Minion):
	Class, race, name = "Neutral", "", "Gruntled Patron"
	mana, attack, health = 4, 3, 3
	numTargets, Effects, description = 0, "", "Frenzy: Summon another Gruntled Patron"
	name_CN = "满意的奴隶主"
	index = "Frenzy"
	trigBoard = Trig_GruntledPatron
	
	
class InjuredMarauder(Minion):
	Class, race, name = "Neutral", "", "Injured Marauder"
	mana, attack, health = 4, 5, 10
	name_CN = "受伤的掠夺者"
	numTargets, Effects, description = 0, "Taunt", "Taunt. Battlecry: Deal 6 damage to this minion"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(self, 6)
		
	
class Golem_Lesser(KazakusGolem):
	name = "Lesser Golem"
	mana, attack, health = 1, 1, 1
	name_CN = "小型魔像"
	
	
class Golem_Greater(KazakusGolem):
	name = "Greater Golem"
	mana, attack, health = 5, 5, 5
	name_CN = "大型魔像"
	
	
class Golem_Superior(KazakusGolem):
	name = "Superior Golem"
	mana, attack, health = 10, 10, 10
	name_CN = "超级魔像"
	
	
class Swiftthistle_Option(Option):
	effect = "Rush"
	mana, attack, health = 0, -1, -1
	
	
class Earthroot_Option(Option):
	effect = "Taunt"
	mana, attack, health = 0, -1, -1
	
	
class Sungrass_Option(Option):
	effect = "Divine Shield"
	mana, attack, health = 0, -1, -1
	
	
class Liferoot_Option(Option):
	effect = "Lifesteal"
	mana, attack, health = 0, -1, -1
	
	
class Fadeleaf_Option(Option):
	effect = "Stealth"
	mana, attack, health = 0, -1, -1
	
	
class GraveMoss_Option(Option):
	effect = "Poisonous"
	mana, attack, health = 0, -1, -1
	
	
class LesserGolem_Wildvine(Golem_Lesser):
	index = "Battlecry~Uncollectible"
	description = "Battlecry: Give your other minions +1/+1"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(self.Game.minionsonBoard(self.ID, exclude=self), 1, 1, source=LesserGolem_Wildvine)
		
	
class GreaterGolem_Wildvine(Golem_Greater):
	index = "Battlecry~Uncollectible"
	description = "Battlecry: Give your other minions +2/+2"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(self.Game.minionsonBoard(self.ID), 2, 2, source=GreaterGolem_Wildvine)
		
	
class SuperiorGolem_Wildvine(Golem_Superior):
	index = "Battlecry~Uncollectible"
	description = "Battlecry: Give your other minions +4/+4"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(self.Game.minionsonBoard(self.ID), 4, 4, source=SuperiorGolem_Wildvine)
		
	
class LesserGolem_Gromsblood(Golem_Lesser):
	index = "Battlecry~Uncollectible"
	description = "Battlecry: Summon a copy of this"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if not self.dead: self.summon(self.copyCard(self, self.ID))
		
	
class GreaterGolem_Gromsblood(Golem_Greater):
	index = "Battlecry~Uncollectible"
	description = "Battlecry: Summon a copy of this"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if not self.dead: self.summon(self.copyCard(self, self.ID))
		
	
class SuperiorGolem_Gromsblood(Golem_Superior):
	index = "Battlecry~Uncollectible"
	description = "Battlecry: Summon a copy of this"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if not self.dead: self.summon(self.copyCard(self, self.ID))
		
	
class LesserGolem_Icecap(Golem_Lesser):
	index = "Battlecry~Uncollectible"
	description = "Battlecry: Freeze a random enemy minion"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if objs := self.Game.minionsAlive(3-self.ID): self.freeze(numpyChoice(objs))
		
	
class GreaterGolem_Icecap(Golem_Greater):
	index = "Battlecry~Uncollectible"
	description = "Battlecry: Freeze two random enemy minions"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		minions = self.Game.minionsAlive(3-self.ID)
		self.freeze(numpyChoice(minions, min(2, len(minions)), replace=False))
		
	
class SuperiorGolem_Icecap(Golem_Superior):
	index = "Battlecry~Uncollectible"
	description = "Battlecry: Freeze all enemy minions"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.freeze(self.Game.minionsonBoard(3-self.ID))
		
	
class LesserGolem_Firebloom(Golem_Lesser):
	index = "Battlecry~Uncollectible"
	description = "Battlecry: Deal 3 damage to a random enemy minion"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if objs := self.Game.minionsAlive(3-self.ID): self.dealsDamage(numpyChoice(objs), 3)
		
	
class GreaterGolem_Firebloom(Golem_Greater):
	index = "Battlecry~Uncollectible"
	description = "Battlecry: Deal 3 damage to two random enemy minions"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if minions := self.Game.minionsAlive(3-self.ID):
			self.dealsDamage(numpyChoice(minions, min(2, len(minions)), replace=False), 3)
		
	
class SuperiorGolem_Firebloom(Golem_Superior):
	index = "Battlecry~Uncollectible"
	description = "Battlecry: Deal 3 damage to all enemy minions"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(self.Game.minionsonBoard(3-self.ID), 3)
		
	
class LesserGolem_Mageroyal(Golem_Lesser):
	index = "Uncollectible"
	Effects, description = "Spell Damage", "Spell Damage +1"
	
	
class GreaterGolem_Mageroyal(Golem_Greater):
	index = "Uncollectible"
	Effects, description = "Spell Damage_2", "Spell Damage +2"
	
	
class SuperiorGolem_Mageroyal(Golem_Superior):
	index = "Uncollectible"
	Effects, description = "Spell Damage_4", "Spell Damage +4"
	
	
class LesserGolem_Kingsblood(Golem_Lesser):
	index = "Battlecry~Uncollectible"
	description = "Battlecry: Draw a card"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.Game.Hand_Deck.drawCard(self.ID)
		
	
class GreaterGolem_Kingsblood(Golem_Greater):
	index = "Battlecry~Uncollectible"
	description = "Battlecry: Draw 2 cards"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.Game.Hand_Deck.drawCard(self.ID)
		self.Game.Hand_Deck.drawCard(self.ID)
		
	
class SuperiorGolem_Kingsblood(Golem_Superior):
	index = "Battlecry~Uncollectible"
	description = "Battlecry: Draw 4 cards"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for i in (0, 1, 2, 3): self.Game.Hand_Deck.drawCard(self.ID)
		
	
class KazakusGolemShaper(Minion):
	Class, race, name = "Neutral", "", "Kazakus, Golem Shaper"
	mana, attack, health = 4, 3, 3
	name_CN = "魔像师卡扎库斯"
	numTargets, Effects, description = 0, "", "Battlecry: If your deck has no 4-Cost cards, build a custom Golem"
	index = "Battlecry~Legendary"
	bareGolems = (Golem_Lesser, Golem_Greater, Golem_Superior)
	keyWordsforGolems = (Swiftthistle_Option, Earthroot_Option, Sungrass_Option, Liferoot_Option, Fadeleaf_Option, GraveMoss_Option)
	golemTable = {1: [LesserGolem_Wildvine, LesserGolem_Gromsblood, LesserGolem_Icecap, LesserGolem_Firebloom, LesserGolem_Mageroyal, LesserGolem_Kingsblood],
			 	5: [GreaterGolem_Wildvine, GreaterGolem_Gromsblood, GreaterGolem_Icecap, GreaterGolem_Firebloom, GreaterGolem_Mageroyal, GreaterGolem_Kingsblood],
				10: [SuperiorGolem_Wildvine, SuperiorGolem_Gromsblood, SuperiorGolem_Icecap, SuperiorGolem_Firebloom, SuperiorGolem_Mageroyal, SuperiorGolem_Kingsblood]
				}
	def effCanTrig(self):
		self.effectViable = all(card.mana != 4 for card in self.Game.Hand_Deck.decks[self.ID])
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		game, ID = self.Game, self.ID
		if game.Hand_Deck.spaceinHand(self.ID) and all(card.mana != 4 for card in game.Hand_Deck.decks[ID]):
			option_mana = self.chooseFixedOptions(comment, [golem(game, ID) for golem in KazakusGolemShaper.bareGolems])
			mana = option_mana.mana
			option_effect, _ = self.discoverNew(comment, lambda : KazakusGolemShaper.keyWordsforGolems, add2Hand=False)
			option_playEffect, _ = self.discoverNew(comment, lambda: KazakusGolemShaper.golemTable[mana], add2Hand=False)
			effect, baseGolem = type(option_effect).effect, type(option_playEffect)
			# mana is 1, effect is "Taunt", golem is LesserGolem_Gromsblood. Result is LesserGolem_Gromsblood__Taunt
			subclass = type(baseGolem.__name__ + '__' + effect, (baseGolem,),
							{"effects": baseGolem.Effects+','+effect, }
							)
			self.addCardtoHand(subclass, self.ID)
		
	
class SouthseaScoundrel(Minion):
	Class, race, name = "Neutral", "Pirate", "Southsea Scoundrel"
	mana, attack, health = 4, 5, 5
	name_CN = "南海恶徒"
	numTargets, Effects, description = 0, "", "Battlecry: Discover a card from your opponent's deck. They draw theirs as well"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		card, i = self.discoverfrom(comment, ls=self.Game.Hand_Deck.decks[3 - self.ID])
		if card:
			self.addCardtoHand(self.copyCard(card, self.ID), self.ID, byDiscover=True)
			self.Game.Hand_Deck.drawCard(3-self.ID, i)
		
	
class SpiritHealer(Minion):
	Class, race, name = "Neutral", "", "Spirit Healer"
	mana, attack, health = 4, 3, 6
	numTargets, Effects, description = 0, "", "After you cast Holy spell, give a friendly minion +2 Health"
	name_CN = "灵魂医者"
	trigBoard = Trig_SpiritHealer
	
	
class BarrensBlacksmith(Minion):
	Class, race, name = "Neutral", "", "Barrens Blacksmith"
	mana, attack, health = 5, 3, 5
	numTargets, Effects, description = 0, "", "Frenzy: Give your other minions +2/+2"
	name_CN = "贫瘠之地铁匠"
	index = "Frenzy"
	trigBoard = Trig_BarrensBlacksmith
	
	
class BurningBladeAcolyte(Minion):
	Class, race, name = "Neutral", "", "Burning Blade Acolyte"
	mana, attack, health = 5, 1, 1
	numTargets, Effects, description = 0, "", "Deathrattle: Summon a 5/8 Demonspawn with Taunt"
	name_CN = "火刃侍僧"
	deathrattle = Death_BurningBladeAcolyte
	
	
class Demonspawn(Minion):
	Class, race, name = "Neutral", "Demon", "Demonspawn"
	mana, attack, health = 6, 5, 8
	name_CN = "恶魔生物"
	numTargets, Effects, description = 0, "Taunt", "Taunt"
	index = "Uncollectible"
	
	
class GoldRoadGrunt(Minion):
	Class, race, name = "Neutral", "", "Gold Road Grunt"
	mana, attack, health = 5, 3, 7
	numTargets, Effects, description = 0, "Taunt", "Taunt. Frenzy: Gain Armor equal to the damage taken"
	name_CN = "黄金之路步兵"
	index = "Frenzy"
	trigBoard = Trig_GoldRoadGrunt
	
	
class RazormaneRaider(Minion):
	Class, race, name = "Neutral", "Quilboar", "Razormane Raider"
	mana, attack, health = 5, 5, 6
	numTargets, Effects, description = 0, "", "Frenzy: Attack a random enemy"
	name_CN = "钢鬃掠夺者"
	index = "Frenzy"
	trigBoard = Trig_RazormaneRaider
	
	
class ShadowHunterVoljin(Minion):
	Class, race, name = "Neutral", "", "Shadow Hunter Vol'jin"
	mana, attack, health = 5, 3, 6
	name_CN = "暗影猎手沃金"
	numTargets, Effects, description = 1, "", "Battlecry: Choose a minion. Swap it with a random one in its owners hand"
	index = "Battlecry~Legendary"
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj is not self and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for obj in target: self.Game.swapMinionwith1Hand(self, obj)
		
	
class TaurajoBrave(Minion):
	Class, race, name = "Neutral", "", "Taurajo Brave"
	mana, attack, health = 6, 4, 8
	numTargets, Effects, description = 0, "", "Frenzy: Destroy a random enemy minion"
	name_CN = "陶拉祖武士"
	index = "Frenzy"
	trigBoard = Trig_TaurajoBrave
	
	
class KargalBattlescar(Minion):
	Class, race, name = "Neutral", "", "Kargal Battlescar"
	mana, attack, health = 7, 5, 5
	name_CN = "卡加尔·战痕"
	numTargets, Effects, description = 0, "", "Battlecry: Summon a 5/5 Lookout for each Watch Post you've summoned this game"
	index = "Battlecry~Legendary"
	def effCanTrig(self):
		self.effectViable = any(tup[0] == "Summon" and "WatchPost" in tup[1].__name__
								for tup in self.Game.Counters.iter_TupsSoFar("events"))
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if num := sum(tup[0] == "Summon" and "WatchPost" in tup[1].name for tup in self.Game.Counters.iter_TupsSoFar("events")):
			self.summon([Lookout(self.Game, self.ID) for _ in range(num)], relative="<>")
		
	
class Lookout(Minion):
	Class, race, name = "Neutral", "", "Lookout"
	mana, attack, health = 5, 5, 5
	name_CN = "哨兵"
	numTargets, Effects, description = 0, "", ""
	index = "Uncollectible"
	
	
class PrimordialProtector(Minion):
	Class, race, name = "Neutral", "Elemental", "Primordial Protector"
	mana, attack, health = 8, 6, 6
	name_CN = "始生保护者"
	numTargets, Effects, description = 0, "", "Battlecry: Draw your highest Cost spell. Summon a random minion with the same Cost"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if indices := pickInds_HighestAttr(self.Game.Hand_Deck.decks[self.ID],
										   cond=lambda card: card.category == "Spell"):
			cost = self.Game.Hand_Deck.drawCard(self.ID, numpyChoice(indices))[1]
			self.summon(self.newEvolved(cost-1, by=1, ID=self.ID))
		
	
class FuryRank3(Spell):
	Class, school, name = "Demon Hunter", "Fel", "Fury (Rank 3)"
	numTargets, mana, Effects = 0, 1, ""
	name_CN = "怒火（等级3）"
	description = "Give your hero +4 Attack this turn"
	index = "Uncollectible"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveHeroAttackArmor(self.ID, attGain=4, source=FuryRank3)
		
	
class FuryRank2(Spell_Forge):
	Class, school, name = "Demon Hunter", "Fel", "Fury (Rank 2)"
	numTargets, mana, Effects = 0, 1, ""
	name_CN = "怒火（等级2）"
	description = "Give your hero +3 Attack this turn. (Upgrades when you have 10 mana.)"
	upgrade_10 = FuryRank3
	index = "Uncollectible"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveHeroAttackArmor(self.ID, attGain=3, source=FuryRank2)
		
	
class FuryRank1(Spell_Forge):
	Class, school, name = "Demon Hunter", "Fel", "Fury (Rank 1)"
	numTargets, mana, Effects = 0, 1, ""
	description = "Give your hero +2 Attack this turn. (Upgrades when you have 5 mana.)"
	upgrade_5, upgrade_10 = FuryRank2, FuryRank3
	name_CN = "怒火（等级1）"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveHeroAttackArmor(self.ID, attGain=2, source=FuryRank1)
		
	
class Tuskpiercer(Weapon):
	Class, name, description = "Demon Hunter", "Tuskpiercer", "Deathrattle: Draw a Deathrattle minion"
	mana, attack, durability, Effects = 1, 1, 2, ""
	name_CN = "獠牙锥刃"
	deathrattle = Death_Tuskpiercer
	
	
class Razorboar(Minion):
	Class, race, name = "Demon Hunter", "Beast", "Razorboar"
	mana, attack, health = 2, 3, 2
	numTargets, Effects, description = 0, "", "Deathrattle: Summon a Deathrattle minion that costs (3) or less from your hand"
	name_CN = "剃刀野猪"
	deathrattle = Death_Razorboar
	
	
class SigilofFlame(Spell_Sigil):
	Class, school, name = "Demon Hunter", "Fel", "Sigil of Flame"
	numTargets, mana, Effects = 0, 2, ""
	description = "At the start of your next turn, deal 3 damage to all enemy minions"
	name_CN = "烈焰咒符"
	trigEffect = SigilofFlame_Effect
	def text(self): return self.calcDamage(3)
		
	
class SigilofSilence(Spell_Sigil):
	Class, school, name = "Demon Hunter", "Shadow", "Sigil of Silence"
	numTargets, mana, Effects = 0, 0, ""
	description = "At the start of your next turn, Silence all enemy minions"
	name_CN = "沉默咒符"
	trigEffect = SigilofSilence_Effect
	
	
class VileCall(Spell):
	Class, school, name = "Demon Hunter", "", "Vile Call"
	numTargets, mana, Effects = 0, 3, ""
	description = "Summon two 2/2 Demons with Lifesteal"
	name_CN = "邪恶召唤"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon([RavenousVilefiend(self.Game, self.ID) for _ in (0, 1)])
		
	
class RavenousVilefiend(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Ravenous Vilefiend"
	mana, attack, health = 2, 2, 2
	name_CN = "贪食邪犬"
	numTargets, Effects, description = 0, "Lifesteal", "Lifesteal"
	index = "Uncollectible"
	
	
class RazorfenBeastmaster(Minion):
	Class, race, name = "Demon Hunter", "Quilboar", "Razorfen Beastmaster"
	mana, attack, health = 3, 3, 3
	numTargets, Effects, description = 0, "", "Deathrattle: Summon a Deathrattle minion that costs (4) or less from your hand"
	name_CN = "剃刀沼泽兽王"
	deathrattle = Death_RazorfenBeastmaster
	
	
class KurtrusAshfallen(Minion):
	Class, race, name = "Demon Hunter", "", "Kurtrus Ashfallen"
	mana, attack, health = 4, 3, 4
	name_CN = "库尔特鲁斯·陨烬"
	numTargets, Effects, description = 0, "", "Battlecry: Attack the left and right-most enemy minions. Outcast: Immune this turn"
	index = "Battlecry~Outcast~Legendary"
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.outcastcanTrig(self)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if posinHand in (-1, 0):
			self.giveEnchant(self, effGain="Immune", source=KurtrusAshfallen)
		if minions := self.Game.minionsonBoard(3-self.ID):
			if self.canBattle() and minions[0].canBattle(): self.Game.battle(self, minions[0])
			if self.canBattle() and minions[-1].canBattle(): self.Game.battle(self, minions[-1])
		
	
class VengefulSpirit(Minion):
	Class, race, name = "Demon Hunter", "", "Vengeful Spirit"
	mana, attack, health = 4, 4, 4
	numTargets, Effects, description = 0, "", "Outcast: Draw two Deathrattle minions"
	name_CN = "复仇之魂"
	index = "Outcast"
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.outcastcanTrig(self)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if posinHand in (-1, 0):
			for _ in (0, 1):
				if not self.drawCertainCard(lambda card: card.category == "Minion" and card.deathrattles)[0]: break
		
	
class DeathSpeakerBlackthorn(Minion):
	Class, race, name = "Demon Hunter", "Quilboar", "Death Speaker Blackthorn"
	mana, attack, health = 7, 3, 6
	name_CN = "亡语者布莱克松"
	numTargets, Effects, description = 0, "", "Battlecry: Summon 3 Deathrattle minions that cost (5) or less from your deck"
	index = "Battlecry~Legendary"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		refMinion = self
		for _ in (0, 1, 2):
			if not (refMinion := self.try_SummonfromOwn(refMinion.pos + 1, cond=lambda card: card.category == "Minion" and card.deathrattles)):
				break
		
	
class LivingSeedRank3(Spell):
	Class, school, name = "Druid", "Nature", "Living Seed (Rank 3)"
	numTargets, mana, Effects = 0, 2, ""
	name_CN = "生命之种（等级3）"
	description = "Draw a Beast. Reduce its Cost by (3)"
	index = "Uncollectible"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		beast, mana, entersHand = self.drawCertainCard(lambda card: "Beast" in card.race)
		if beast and entersHand: ManaMod(beast, by=-3).applies()
		
	
class LivingSeedRank2(Spell_Forge):
	Class, school, name = "Druid", "Nature", "Living Seed (Rank 2)"
	numTargets, mana, Effects = 0, 2, ""
	name_CN = "生命之种（等级2）"
	description = "Draw a Beast. Reduce its Cost by (2). (Upgrades when you have 10 mana.)"
	upgrade_10 = LivingSeedRank3
	index = "Uncollectible"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		beast, mana, entersHand = self.drawCertainCard(lambda card: "Beast" in card.race)
		if beast and entersHand: ManaMod(beast, by=-2).applies()
		
	
class LivingSeedRank1(Spell_Forge):
	Class, school, name = "Druid", "Nature", "Living Seed (Rank 1)"
	numTargets, mana, Effects = 0, 2, ""
	description = "Draw a Beast. Reduce its Cost by (1). (Upgrades when you have 5 mana.)"
	upgrade_5, upgrade_10 = LivingSeedRank2, LivingSeedRank3
	name_CN = "生命之种（等级1）"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		beast, mana, entersHand = self.drawCertainCard(lambda card: "Beast" in card.race)
		if beast and entersHand: ManaMod(beast, by=-1).applies()
		
	
class MarkoftheSpikeshell(Spell):
	Class, school, name = "Druid", "Nature", "Mark of the Spikeshell"
	numTargets, mana, Effects = 1, 2, ""
	description = "Give a minion +2/+2. If it has Taunt, add a copy of it to your hand"
	name_CN = "尖壳印记"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for obj in target:
			self.giveEnchant(obj, 2, 2, source=MarkoftheSpikeshell)
			if obj.effects["Taunt"] > 0: self.addCardtoHand(self.copyCard(obj, self.ID), self.ID)
		
	
class RazormaneBattleguard(Minion):
	Class, race, name = "Druid", "Quilboar", "Razormane Battleguard"
	mana, attack, health = 2, 2, 2
	numTargets, Effects, description = 0, "", "The first Taunt minion your play each turn costs (2) less"
	name_CN = "钢鬃卫兵"
	aura, trigEffect = ManaAura_RazormaneBattleguard, GameManaAura_RazormaneBattleguard
	
	
class ThorngrowthSentries(Spell):
	Class, school, name = "Druid", "Nature", "Thorngrowth Sentries"
	numTargets, mana, Effects = 0, 2, ""
	description = "Summon two 1/2 Turtles with Taunt"
	name_CN = "荆棘护卫"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon([ThornguardTurtle(self.Game, self.ID) for _ in (0, 1)])
		
	
class ThornguardTurtle(Minion):
	Class, race, name = "Druid", "Beast", "Thornguard Turtle"
	mana, attack, health = 1, 1, 2
	name_CN = "棘甲龟"
	numTargets, Effects, description = 0, "Taunt", "Taunt"
	index = "Uncollectible"
	
	
class GuffRunetotem(Minion):
	Class, race, name = "Druid", "", "Guff Runetotem"
	mana, attack, health = 3, 2, 4
	name_CN = "古夫·符文图腾"
	numTargets, Effects, description = 0, "", "After you cast a Nature spell, give another friendly minion +2/+2"
	index = "Legendary"
	trigBoard = Trig_GuffRunetotem
	
	
class PlaguemawtheRotting(Minion):
	Class, race, name = "Druid", "Quilboar", "Plaguemaw the Rotting"
	mana, attack, health = 4, 3, 4
	name_CN = "腐烂的普雷莫尔"
	numTargets, Effects, description = 0, "", "After a friendly Taunt minion dies, summon a new copy of it with Taunt"
	index = "Legendary"
	trigBoard = Trig_PlaguemawtheRotting
	
	
class PridesFury(Spell):
	Class, school, name = "Druid", "", "Pride's Fury"
	numTargets, mana, Effects = 0, 4, ""
	description = "Give your minions +1/+3"
	name_CN = "狮群之怒"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(self.Game.minionsonBoard(self.ID), 1, 3, source=PridesFury)
		
	
class ThickhideKodo(Minion):
	Class, race, name = "Druid", "Beast", "Thickhide Kodo"
	mana, attack, health = 4, 3, 5
	numTargets, Effects, description = 0, "Taunt", "Taunt. Deathrattle: Gain 5 Armor"
	name_CN = "厚皮科多兽"
	deathrattle = Death_ThickhideKodo
	
	
class CelestialAlignment(Spell):
	Class, school, name = "Druid", "Arcane", "Celestial Alignment"
	numTargets, mana, Effects = 0, 7, ""
	description = "Set each player to 0 Mana Crystals. Set the Cost of cards in all hands and decks to (1)"
	name_CN = "超凡之盟"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for ID in (1, 2):
			self.Game.Manas.setManaCrystal(0, ID)
			for card in self.Game.Hand_Deck.hands[ID]:
				ManaMod(card, to=1).applies()
			for card in self.Game.Hand_Deck.decks[ID]:
				ManaMod(card, to=1).applies()
		
	
class DruidofthePlains(Minion):
	Class, race, name = "Druid", "Beast", "Druid of the Plains"
	mana, attack, health = 7, 7, 6
	numTargets, Effects, description = 0, "Rush", "Rush. Frenzy: Transform into a 6/7 Kodo with Taunt"
	name_CN = "平原德鲁伊"
	index = "Frenzy"
	trigBoard = Trig_DruidofthePlains
	
	
class DruidofthePlains_Taunt(Minion):
	Class, race, name = "Druid", "Beast", "Druid of the Plains"
	mana, attack, health = 7, 6, 7
	name_CN = "平原德鲁伊"
	numTargets, Effects, description = 0, "Taunt", "Taunt"
	index = "Uncollectible"
	
	
class SunscaleRaptor(Minion):
	Class, race, name = "Hunter", "Beast", "Sunscale Raptor"
	mana, attack, health = 1, 1, 3
	numTargets, Effects, description = 0, "", "Frenzy: Shuffle a Sunscale Raptor into your deck with permanent +2/+1"
	name_CN = "赤鳞迅猛龙"
	index = "Frenzy"
	trigBoard = Trig_SunscaleRaptor
	
	
class WoundPrey(Spell):
	Class, school, name = "Hunter", "", "Wound Prey"
	numTargets, mana, Effects = 1, 1, ""
	description = "Deal 1 damage. Summon a 1/1 Hyena with Rush"
	name_CN = "击伤猎物"
	def text(self): return self.calcDamage(1)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(target, self.calcDamage(1))
		self.summon(SwiftHyena(self.Game, self.ID))
		
	
class SwiftHyena(Minion):
	Class, race, name = "Hunter", "Beast", "Swift Hyena"
	mana, attack, health = 1, 1, 1
	name_CN = "迅捷土狼"
	numTargets, Effects, description = 0, "Rush", "Rush"
	index = "Uncollectible"
	
	
class KolkarPackRunner(Minion):
	Class, race, name = "Hunter", "", "Kolkar Pack Runner"
	mana, attack, health = 3, 3, 4
	numTargets, Effects, description = 0, "", "After you cast a spell, summon a 1/1 Hyena with Rush"
	name_CN = "科卡尔驯犬者"
	trigBoard = Trig_KolkarPackRunner
	
	
class ProspectorsCaravan(Minion):
	Class, race, name = "Hunter", "", "Prospector's Caravan"
	mana, attack, health = 2, 1, 3
	numTargets, Effects, description = 0, "", "At the start of your turn, give all minions in your hand +1/+1"
	name_CN = "勘探者车队"
	trigBoard = Trig_ProspectorsCaravan
	
	
class TameBeastRank3(Spell):
	Class, school, name = "Hunter", "", "Tame Beast (Rank 3)"
	numTargets, mana, Effects = 0, 2, ""
	name_CN = "驯服野兽（等级3）"
	description = "Summon a 6/6 Beast with Rush"
	index = "Uncollectible"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon(TamedThunderLizard(self.Game, self.ID))
		
	
class TameBeastRank2(Spell_Forge):
	Class, school, name = "Hunter", "", "Tame Beast (Rank 2)"
	numTargets, mana, Effects = 0, 2, ""
	name_CN = "驯服野兽（等级2）"
	description = "Summon a 4/4 Beast with Rush. (Upgrades when you have 10 mana.)"
	upgrade_10 = TameBeastRank3
	index = "Uncollectible"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon(TamedScorpid(self.Game, self.ID))
		
	
class TameBeastRank1(Spell_Forge):
	Class, school, name = "Hunter", "", "Tame Beast (Rank 1)"
	numTargets, mana, Effects = 0, 2, ""
	description = "Summon a 2/2 Beast with Rush. (Upgrades when you have 5 mana.)"
	upgrade_5, upgrade_10 = TameBeastRank2, TameBeastRank3
	name_CN = "驯服野兽（等级1）"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon(TamedCrab(self.Game, self.ID))
		
	
class TamedCrab(Minion):
	Class, race, name = "Hunter", "Beast", "Tamed Crab"
	mana, attack, health = 2, 2, 2
	name_CN = "驯服的螃蟹"
	numTargets, Effects, description = 0, "Rush", "Rush"
	index = "Uncollectible"
	
	
class TamedScorpid(Minion):
	Class, race, name = "Hunter", "Beast", "Tamed Scorpid"
	mana, attack, health = 4, 4, 4
	name_CN = "驯服的蝎子"
	numTargets, Effects, description = 0, "Rush", "Rush"
	index = "Uncollectible"
	
	
class TamedThunderLizard(Minion):
	Class, race, name = "Hunter", "Beast", "Tamed Thunder Lizard"
	mana, attack, health = 6, 6, 6
	name_CN = "驯服的雷霆蜥蜴"
	numTargets, Effects, description = 0, "Rush", "Rush"
	index = "Uncollectible"
	
	
class PackKodo(Minion):
	Class, race, name = "Hunter", "Beast", "Pack Kodo"
	mana, attack, health = 3, 3, 3
	name_CN = "载货科多兽"
	numTargets, Effects, description = 0, "", "Battlecry: Discove a Beast, Secret, or weapon"
	index = "Battlecry"
	poolIdentifier = "Beasts as Druid"
	@classmethod
	def generatePool(cls, pools):
		classes, ls_Pools = [], []
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
			classes.append("Beasts as "+Class)
			classes.append(Class+" Secrets")
			classes.append("Weapons as "+Class)
			ls_Pools.append(beasts)
			ls_Pools.append(secrets)
			ls_Pools.append(weapons)
		return classes, ls_Pools
		
	def decidePools(self):
		HeroClass, Class = self.Game.heroes[self.ID].Class, class4Discover(self)
		key = HeroClass + " Secrets" if HeroClass in ["Hunter", "Mage", "Paladin", "Rogue"] else "Hunter Secrets"
		return [self.rngPool("Beasts as " + Class), self.rngPool(key), self.rngPool("Weapons as " + Class)]
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.discoverNew_MultiPools(comment, lambda : PackKodo.decidePools(self))
		
	
class TavishStormpike(Minion):
	Class, race, name = "Hunter", "", "Tavish Stormpike"
	mana, attack, health = 3, 2, 5
	name_CN = "塔维什·雷矛"
	numTargets, Effects, description = 0, "", "After a friendly Beast attacks, summon a Beast from your deck that costs (1) less"
	index = "Legendary"
	trigBoard = Trig_TavishStormpike
	
	
class PiercingShot(Spell):
	Class, school, name = "Hunter", "", "Piercing Shot"
	numTargets, mana, Effects = 1, 4, ""
	description = "Deal 6 damage to a minion. Excess damage hits the enemy hero"
	name_CN = "穿刺射击"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def text(self): return self.calcDamage(6)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		damage = self.calcDamage(6)
		for obj in target:
			dmgExcess = damage - (dmgReal := min(damage, max(obj.health, 0)))
			self.dealsDamage(obj, dmgReal)
			if dmgExcess: self.dealsDamage(self.Game.heroes[3-self.ID], dmgExcess)
		
	
class WarsongWrangler(Minion):
	Class, race, name = "Hunter", "", "Warsong Wrangler"
	mana, attack, health = 4, 3, 4
	name_CN = "战歌驯兽师"
	numTargets, Effects, description = 0, "", "Battlecry: Discover a Beast in your deck. Give all copies of it +2/+1 (wherever they are)"
	index = "Battlecry"
	def drawBeastandBuffAllCopies(self, i, beast):
		self.Game.Hand_Deck.drawCard(self.ID, i)
		self.giveEnchant([minion for minion in self.Game.minionsonBoard(self.ID) if isinstance(minion, beast)],
						 2, 1, source=WarsongWrangler)
		self.giveEnchant([card for card in self.Game.Hand_Deck.hands[self.ID] if isinstance(card, beast)], 2, 1,
						 source=WarsongWrangler, add2EventinGUI=False)
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if isinstance(card, beast): card.getsBuffDebuff_inDeck(2, 1, source=WarsongWrangler)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		card, i = self.discoverfrom(comment, cond=lambda card: "Beast" in card.race)
		if card: WarsongWrangler.drawBeastandBuffAllCopies(self, i, type(card))
		
	
class BarakKodobane(Minion):
	Class, race, name = "Hunter", "", "Barak Kodobane"
	mana, attack, health = 5, 3, 5
	name_CN = "巴拉克·科多班恩"
	numTargets, Effects, description = 0, "", "Battlecry: Draw a 1, 2, and 3-Cost spell"
	index = "Battlecry~Legendary"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for cost in (1, 2, 3): self.drawCertainCard(lambda card: card.category == "Spell" and card.mana == cost)
		
	
class FlurryRank3(Spell):
	Class, school, name = "Mage", "Frost", "Flurry (Rank 3)"
	numTargets, mana, Effects = 0, 0, ""
	name_CN = "冰风暴（等级3）"
	description = "Freeze three random enemy minions"
	index = "Uncollectible"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		minions = self.Game.minionsonBoard(3 - self.ID)
		self.freeze(numpyChoice(minions, min(3, len(minions)), replace=False))
		
	
class FlurryRank2(Spell_Forge):
	Class, school, name = "Mage", "Frost", "Flurry (Rank 2)"
	numTargets, mana, Effects = 0, 0, ""
	name_CN = "冰风暴（等级2）"
	description = "Freeze two random enemy minions. (Upgrades when you have 10 mana.)"
	upgrade_10 = FlurryRank3
	index = "Uncollectible"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		minions = self.Game.minionsonBoard(3-self.ID)
		self.freeze(numpyChoice(minions, min(2, len(minions)), replace=False))
		
	
class FlurryRank1(Spell_Forge):
	Class, school, name = "Mage", "Frost", "Flurry (Rank 1)"
	numTargets, mana, Effects = 0, 0, ""
	description = "Freeze a random enemy minion. (Upgrades when you have 5 mana.)"
	upgrade_5, upgrade_10 = FlurryRank2, FlurryRank3
	name_CN = "冰风暴（等级1）"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if minions := self.Game.minionsonBoard(3-self.ID): self.freeze(numpyChoice(minions))
		
	
class RunedOrb(Spell):
	Class, school, name = "Mage", "Arcane", "Runed Orb"
	numTargets, mana, Effects = 1, 2, ""
	description = "Deal 2 damage. Discover a Spell"
	name_CN = "符文宝珠"
	def text(self): return self.calcDamage(2)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(target, self.calcDamage(2))
		self.discoverNew(comment, lambda : self.rngPool(class4Discover(self) + " Spells"))
		
	
class Wildfire(Spell):
	Class, school, name = "Mage", "Fire", "Wildfire"
	numTargets, mana, Effects = 0, 1, ""
	description = "Increase the damage of your Hero Power by 1"
	name_CN = "野火"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(self.Game.powers[self.ID], effGain="Damage Boost", source=Wildfire)
		#self.Game.powers[self.ID].getsEffect("Damage Boost")
		
	
class ArcaneLuminary(Minion):
	Class, race, name = "Mage", "Elemental", "Arcane Luminary"
	mana, attack, health = 3, 4, 3
	numTargets, Effects, description = 0, "", "Cards that didn't start in your deck cost (2) less, but not less than (1)"
	name_CN = "奥术发光体"
	aura = ManaAura_ArcaneLuminary
	
	
class OasisAlly(Secret):
	Class, school, name = "Mage", "Frost", "Oasis Ally"
	numTargets, mana, Effects = 0, 3, ""
	description = "Secret: When a friendly minion is attacked, summon a 3/6 Water Elemental"
	name_CN = "绿洲盟军"
	trigBoard = Trig_OasisAlly
	
	
class Rimetongue(Minion):
	Class, race, name = "Mage", "", "Rimetongue"
	mana, attack, health = 3, 3, 4
	numTargets, Effects, description = 0, "", "After you cast a Frost spell, summon a 1/1 Elemental that Freezes"
	name_CN = "霜舌半人马"
	trigBoard = Trig_Rimetongue
	
	
class FrostedElemental(Minion):
	Class, race, name = "Mage", "Elemental", "Frosted Elemental"
	mana, attack, health = 1, 1, 1
	name_CN = "霜冻元素"
	numTargets, Effects, description = 0, "", "Freeze any character damaged by this minion"
	index = "Uncollectible"
	trigBoard = Trig_FrostedElemental
	
	
class RecklessApprentice(Minion):
	Class, race, name = "Mage", "", "Reckless Apprentice"
	mana, attack, health = 4, 3, 5
	name_CN = "鲁莽的学徒"
	numTargets, Effects, description = 0, "", "Battlecry: Fire your Hero Power at all enemies"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		choice = (power := self.Game.powers[self.ID]).pickRandomChoice()
		numTargets = power.numTargetsNeeded(choice)
		for char in self.Game.charsonBoard(3-self.ID):
			if numTargets:
				if target := power.randomTargets(numTargets, preSelected=[char]):
					power.effect_wrapper(target, choice=choice, comment="byOhters")
				else: break
			else: power.effect_wrapper(choice=choice, comment="byOhters")
		
	
class RefreshingSpringWater(Spell):
	Class, school, name = "Mage", "", "Refreshing Spring Water"
	numTargets, mana, Effects = 0, 5, ""
	description = "Draw 2 cards. Refresh 2 Mana Crystals for each spell drawn"
	name_CN = "清凉的泉水"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		card1 = self.Game.Hand_Deck.drawCard(self.ID)[0]
		card2 = self.Game.Hand_Deck.drawCard(self.ID)[0]
		num = 0 #假设即使爆牌也能回复费用
		if card1 and card1.category == "Spell": num += 2
		if card2 and card2.category == "Spell": num += 2
		if num > 0: self.Game.Manas.restoreManaCrystal(num, self.ID)
		
	
class VardenDawngrasp(Minion):
	Class, race, name = "Mage", "", "Varden Dawngrasp"
	mana, attack, health = 4, 3, 3
	name_CN = "瓦尔登·晨拥"
	numTargets, Effects, description = 0, "", "Battlecry: Freeze all enemy minions. If any are already Frozen, deal 4 damage to them instead"
	index = "Battlecry~Legendary"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		objs_Freeze, objs_Damage = [], []
		for minion in self.Game.minionsonBoard(3-self.ID):
			if minion.effects["Frozen"] < 1: objs_Freeze.append(minion)
			else: objs_Damage.append(minion)
		self.freeze(objs_Freeze)
		self.dealsDamage(objs_Damage, 4)
		
	
class MordreshFireEye(Minion):
	Class, race, name = "Mage", "", "Mordresh Fire Eye"
	mana, attack, health = 8, 8, 8
	name_CN = "火眼莫德雷斯"
	numTargets, Effects, description = 0, "", "Battlecry: If you've dealt 10 damage with your hero power this game, deal 10 damage to all enemies"
	index = "Battlecry~Legendary"
	def effCanTrig(self):
		self.effectViable = 9 < sum(tup[3] for tup in self.Game.Counters.iter_TupsSoFar("events") if tup[0] == "Damage" and tup[1] % 100 == 20 + self.ID)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if 9 < sum(tup[3] for tup in self.Game.Counters.iter_TupsSoFar("events") if tup[0] == "Damage" and tup[1] % 100 == 20 + self.ID):
			self.dealsDamage(self.Game.charsonBoard(3-self.ID), 10)
		
	
class ConvictionRank3(Spell):
	Class, school, name = "Paladin", "Holy", "Conviction (Rank 3)"
	numTargets, mana, Effects = 0, 2, ""
	name_CN = "定罪（等级3）"
	description = "Give three random friendly minions +3 Attack"
	index = "Uncollectible"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if minions := self.Game.minionsonBoard(self.ID):
			self.giveEnchant(numpyChoice(minions, min(2, len(minions)), replace=False), 3, 0, source=ConvictionRank3)
		
	
class ConvictionRank2(Spell_Forge):
	Class, school, name = "Paladin", "Holy", "Conviction (Rank 2)"
	numTargets, mana, Effects = 0, 2, ""
	name_CN = "定罪（等级2）"
	description = "Give two random friendly minions +3 Attack. (Upgrades when you have 10 mana.)"
	upgrade_10 = ConvictionRank3
	index = "Uncollectible"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if minions := self.Game.minionsonBoard(self.ID):
			self.giveEnchant(numpyChoice(minions, min(2, len(minions)), replace=False), 3, 0, source=ConvictionRank2)
		
	
class ConvictionRank1(Spell_Forge):
	Class, school, name = "Paladin", "Holy", "Conviction (Rank 1)"
	numTargets, mana, Effects = 0, 2, ""
	description = "Give a random friendly minion +3 Attack. (Upgrades when you have 5 mana.)"
	upgrade_5, upgrade_10 = ConvictionRank2, ConvictionRank3
	name_CN = "定罪（等级1）"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if minions := self.Game.minionsonBoard(self.ID): self.giveEnchant(numpyChoice(minions), 3, 0, source=ConvictionRank1)
		
	
class GallopingSavior(Secret):
	Class, school, name = "Paladin", "", "Galloping Savior"
	numTargets, mana, Effects = 0, 1, ""
	description = "Secret: After your opponent plays three cards in a turn, summon a 3/4 Steed with Taunt"
	name_CN = "迅疾救兵"
	trigBoard = Trig_GallopingSavior
	
	
class HolySteed(Minion):
	Class, race, name = "Paladin", "Beast", "Holy Steed"
	mana, attack, health = 3, 3, 4
	name_CN = "神圣战马"
	numTargets, Effects, description = 0, "Taunt", "Taunt"
	index = "Uncollectible"
	
	
class KnightofAnointment(Minion):
	Class, race, name = "Paladin", "", "Knight of Anointment"
	mana, attack, health = 1, 1, 1
	name_CN = "圣礼骑士"
	numTargets, Effects, description = 0, "", "Battlecry: Draw a Holy spell"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.drawCertainCard(lambda card: card.school == "Holy")
		
	
class SoldiersCaravan(Minion):
	Class, race, name = "Paladin", "", "Soldier's Caravan"
	mana, attack, health = 2, 1, 3
	numTargets, Effects, description = 0, "", "At the start of your turn, summon two 1/1 Silver Hand Recruits"
	name_CN = "士兵车队"
	trigBoard = Trig_SoldiersCaravan
	
	
class SwordoftheFallen(Weapon):
	Class, name, description = "Paladin", "Sword of the Fallen", "After your hero attack, cast a Secret from your deck"
	mana, attack, durability, Effects = 2, 1, 2, ""
	name_CN = "逝者之剑"
	trigBoard = Trig_SwordoftheFallen
	
	
class NorthwatchCommander(Minion):
	Class, race, name = "Paladin", "", "Northwatch Commander"
	mana, attack, health = 3, 3, 4
	name_CN = "北卫军指挥官"
	numTargets, Effects, description = 0, "", "Battlecry: If you control a Secret, draw a minion"
	index = "Battlecry"
	def effCanTrig(self):
		self.effectViable = self.Game.Secrets.secrets[self.ID]
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.Game.Secrets.secrets[self.ID]: self.drawCertainCard(lambda card: card.category == "Minion")
		
	
class CarielRoame(Minion):
	Class, race, name = "Paladin", "", "Cariel Roame"
	mana, attack, health = 4, 4, 3
	name_CN = "凯瑞尔·罗姆"
	numTargets, Effects, description = 0, "Rush,Divine Shield", "Rush, Divine Shield. Whenever this attacks, reduce the Cost of Holy Spells in your hand by (1)"
	index = "Legendary"
	trigBoard = Trig_CarielRoame
	
	
class VeteranWarmedic(Minion):
	Class, race, name = "Paladin", "", "Veteran Warmedic"
	mana, attack, health = 4, 3, 5
	numTargets, Effects, description = 0, "", "After you cast a Holy spell, summon a 2/2 Medic with Lifesteal"
	name_CN = "战地医师老兵"
	trigBoard = Trig_VeteranWarmedic
	
	
class BattlefieldMedic(Minion):
	Class, race, name = "Paladin", "", "Battlefield Medic"
	mana, attack, health = 2, 2, 2
	name_CN = "战地医师"
	numTargets, Effects, description = 0, "Lifesteal", "Lifesteal"
	index = "Uncollectible"
	
	
class InvigoratingSermon(Spell):
	Class, school, name = "Paladin", "Holy", "Invigorating Sermon"
	numTargets, mana, Effects = 0, 4, ""
	description = "Give +1/+1 to all minions in your hand, deck and battlefield"
	name_CN = "动员布道"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		typeSelf = type(self)
		self.giveEnchant([card for card in self.Game.Hand_Deck.hands[self.ID] if card.category == "Minion"], 
						1, 1, source=InvigoratingSermon, add2EventinGUI=False)
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if card.category == "Minion": card.getsBuffDebuff_inDeck(1, 1, source=InvigoratingSermon)
		self.giveEnchant(self.Game.minionsonBoard(self.ID), 1, 1, source=InvigoratingSermon)
		
	
class CannonmasterSmythe(Minion):
	Class, race, name = "Paladin", "", "Cannonmaster Smythe"
	mana, attack, health = 5, 4, 4
	name_CN = "火炮长斯密瑟"
	numTargets, Effects, description = 0, "", "Battlecry: Transform your secrets into 3/3 Soldiers. They transform back when they die"
	index = "Battlecry~Legendary"
	def effCanTrig(self):
		self.effectViable = self.Game.Secrets.secrets[self.ID]
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		secretsHD = self.Game.Secrets
		while secretsHD.secrets[self.ID] and self.Game.space(self.ID):
			secret = secretsHD.extractSecrets(self.ID, 0, enemyCanSee=False)
			minion = NorthwatchSoldier(self.Game, self.ID)
			minion.deathrattles[0].memory = secret
			self.summon(minion)
		
	
class NorthwatchSoldier(Minion):
	Class, race, name = "Paladin", "", "Northwatch Soldier"
	mana, attack, health = 3, 3, 3
	name_CN = "北卫军士兵"
	numTargets, Effects, description = 0, "", ""
	index = "Uncollectible"
	deathrattle = Death_NorthwatchSoldier
	
	
class DesperatePrayer(Spell):
	Class, school, name = "Priest", "Holy", "Desperate Prayer"
	numTargets, mana, Effects = 0, 0, ""
	description = "Restore 5 Health to each hero"
	name_CN = "绝望祷言"
	def text(self): return self.calcHeal(5)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		heal = self.calcHeal(5)
		self.heals(list(self.Game.heroes.values()), [heal] * 2)
		
	
class CondemnRank3(Spell):
	Class, school, name = "Priest", "Holy", "Condemn (Rank 3)"
	numTargets, mana, Effects = 0, 2, ""
	name_CN = "罪罚（等级3）"
	description = "Deal 3 damage to all enemy minions"
	index = "Uncollectible"
	def text(self): return self.calcDamage(3)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(objs := self.Game.minionsonBoard(3-self.ID), [self.calcDamage(3)] * len(objs))
		
	
class CondemnRank2(Spell_Forge):
	Class, school, name = "Priest", "Holy", "Condemn (Rank 2)"
	numTargets, mana, Effects = 0, 2, ""
	name_CN = "罪罚（等级2）"
	description = "Deal 2 damage to all enemy minions. (Upgrades when you have 10 mana.)"
	upgrade_10 = CondemnRank3
	index = "Uncollectible"
	def text(self): return self.calcDamage(2)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(objs := self.Game.minionsonBoard(3-self.ID), [self.calcDamage(2)] * len(objs))
		
	
class CondemnRank1(Spell_Forge):
	Class, school, name = "Priest", "Holy", "Condemn (Rank 1)"
	numTargets, mana, Effects = 0, 2, ""
	description = "Deal 1 damage to all enemy minions. (Upgrades when you have 5 mana.)"
	upgrade_5, upgrade_10 = CondemnRank2, CondemnRank3
	name_CN = "罪罚（等级1）"
	def text(self): return self.calcDamage(1)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(self.Game.minionsonBoard(3-self.ID), self.calcDamage(1))
		
	
class SerenaBloodfeather(Minion):
	Class, race, name = "Priest", "", "Serena Bloodfeather"
	mana, attack, health = 2, 1, 1
	name_CN = "塞瑞娜·血羽"
	numTargets, Effects, description = 1, "", "Battlecry: Choose an enemy minion. Steal Attack and Health from it until this has more"
	index = "Battlecry~Legendary"
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists(3 - self.ID, choice)
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.ID != self.ID and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.onBoard or self.inHand:
			for obj in target:
				if obj.attack > 0 or obj.health > 0:
					attackStolen = max(0, int((obj.attack - self.attack) / 2) + 1)
					healthStolen = max(0, int((obj.health - self.health) / 2) + 1)
					self.giveEnchant(obj, -attackStolen, -healthStolen, source=SerenaBloodfeather)
					self.giveEnchant(self, attackStolen, healthStolen, source=SerenaBloodfeather)
		
	
class SoothsayersCaravan(Minion):
	Class, race, name = "Priest", "", "Soothsayer's Caravan"
	mana, attack, health = 2, 1, 3
	numTargets, Effects, description = 0, "", "At the start of your turn, copy a spell from your opponent's deck to your hand"
	name_CN = "占卜者车队"
	trigBoard = Trig_SoothsayersCaravan
	
	
class DevouringPlague(Spell):
	Class, school, name = "Priest", "Shadow", "Devouring Plague"
	numTargets, mana, Effects = 0, 3, "Lifesteal"
	description = "Lifesteal. Deal 4 damage randomly split among all enemies"
	name_CN = "噬灵疫病"
	def text(self): return self.calcDamage(4)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for _ in range(self.calcDamage(4)):
			if objs := self.Game.charsAlive(3-self.ID): self.dealsDamage(numpyChoice(objs), 1)
			else: break
		
	
class VoidFlayer(Minion):
	Class, race, name = "Priest", "", "Void Flayer"
	mana, attack, health = 4, 3, 4
	name_CN = "剥灵者"
	numTargets, Effects, description = 0, "", "Battlecry: For each spell in your hand, deal 1 damage to a random enemy minion"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		damage = sum(card.category == "Spell" for card in self.Game.Hand_Deck.hands[self.ID])
		for _ in range(damage):
			if objs := self.Game.charsAlive(3-self.ID): self.dealsDamage(numpyChoice(objs), 1)
			else: break
		
	
class Xyrella(Minion):
	Class, race, name = "Priest", "", "Xyrella"
	mana, attack, health = 4, 4, 4
	name_CN = "泽瑞拉"
	numTargets, Effects, description = 0, "", "Battlecry: If you've restored Health this turn, deal that much damage to all enemy minions"
	index = "Battlecry~Legendary"
	def text(self): return self.Game.Counters.examHealThisTurn(self.ID, veri_sum=1)
		
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.examHealThisTurn(self.ID)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if (heal := self.Game.Counters.examHealThisTurn(self.ID, veri_sum=1)) > 0:
			self.dealsDamage(self.Game.minionsonBoard(3-self.ID), heal)
		
	
class PriestofAnshe(Minion):
	Class, race, name = "Priest", "", "Priest of An'she"
	mana, attack, health = 5, 5, 5
	name_CN = "安瑟祭司"
	numTargets, Effects, description = 0, "Taunt", "Taunt. Battlecry: If you've restored Health this turn, gain +3/+3"
	index = "Battlecry"
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.examHealThisTurn(self.ID)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.Game.Counters.examHealThisTurn(self.ID): self.giveEnchant(self, 3, 3, source=PriestofAnshe)
		
	
class LightshowerElemental(Minion):
	Class, race, name = "Priest", "Elemental", "Lightshower Elemental"
	mana, attack, health = 6, 6, 6
	numTargets, Effects, description = 0, "Taunt", "Taunt. Deathrattle: Restore 8 Health to all friendly characters"
	name_CN = "光沐元素"
	deathrattle = Death_LightshowerElemental
	
	
class PowerWordFortitude(Spell):
	Class, school, name = "Priest", "Holy", "Power Word: Fortitude"
	numTargets, mana, Effects = 1, 8, ""
	description = "Give a minion +3/+5. Costs (1) less for each spell in your hand"
	name_CN = "真言术：韧"
	trigHand = Trigger_PowerWordFortitude
	def selfManaChange(self):
		self.mana -= sum(card.category == "Spell" for card in self.Game.Hand_Deck.hands[self.ID])
		
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(target, 3, 5, source=PowerWordFortitude)
		
	
class ParalyticPoison(Spell):
	Class, school, name = "Rogue", "Nature", "Paralytic Poison"
	numTargets, mana, Effects = 0, 1, ""
	description = "Give your weapon +1 Attack and 'Your hero is Immune while attacking'"
	name_CN = "麻痹药膏"
	trigEffect = Trig_ParalyticPoison
	def available(self):
		return self.Game.availableWeapon(self.ID) is not None
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if weapon := self.Game.availableWeapon(self.ID): self.giveEnchant(weapon, 1, 0, source=ParalyticPoison,
																		  trig=Trig_ParalyticPoison)
		
	
class Yoink(Spell):
	Class, school, name = "Rogue", "", "Yoink!"
	numTargets, mana, Effects = 0, 1, ""
	description = "Discover a Hero Power and set its Cost to (0). Swap back after 2 uses"
	name_CN = "偷师学艺"
	trigEffect = Trig_SwapBackPowerAfter2Uses
	poolIdentifier = "Basic Powers"
	@classmethod
	def generatePool(cls, pools):
		return "Basic Powers", pools.basicPowers
		
	def decidePowerPool(self):
		powerType = type(self.Game.powers[self.ID])
		return [power for power in self.rngPool("Basic Powers") if power is not powerType]
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		power, _ = self.discoverNew(comment, lambda : Yoink.decidePowerPool(self), add2Hand=False)
		ManaMod(power, to=0).applies()
		power.powerReplaced = self.Game.powers[self.ID]
		power.trigsBoard.append(Trig_SwapBackPowerAfter2Uses(power))
		power.replacePower()
		
	
class EfficientOctobot(Minion):
	Class, race, name = "Rogue", "Mech", "Efficient Octo-bot"
	mana, attack, health = 2, 1, 4
	numTargets, Effects, description = 0, "", "Frenzy: Reduce the cost of cards in your hand by (1)"
	name_CN = "高效八爪机器人"
	index = "Frenzy"
	trigBoard = Trig_EfficientOctobot
	
	
class SilverleafPoison(Spell):
	Class, school, name = "Rogue", "Nature", "Silverleaf Poison"
	numTargets, mana, Effects = 0, 2, ""
	description = "Give your weapon 'After your hero attacks draw a card'"
	name_CN = "银叶草药膏"
	trigEffect = Trig_SilverleafPoison
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if weapon := self.Game.availableWeapon(self.ID): self.giveEnchant(weapon, trig=Trig_SilverleafPoison)
		
	
class WickedStabRank3(Spell):
	Class, school, name = "Rogue", "", "Wicked Stab (Rank 3)"
	numTargets, mana, Effects = 1, 2, ""
	name_CN = "邪恶挥刺（等级3）"
	description = "Deal 6 damage"
	index = "Uncollectible"
	def text(self): return self.calcDamage(6)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(target, self.calcDamage(6))
		
	
class WickedStabRank2(Spell_Forge):
	Class, school, name = "Rogue", "", "Wicked Stab (Rank 2)"
	numTargets, mana, Effects = 1, 2, ""
	name_CN = "邪恶挥刺（等级2）"
	description = "Deal 4 damage. (Upgrades when you have 10 mana.)"
	upgrade_10 = WickedStabRank3
	index = "Uncollectible"
	def text(self): return self.calcDamage(4)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(target, self.calcDamage(4))
		
	
class WickedStabRank1(Spell_Forge):
	Class, school, name = "Rogue", "", "Wicked Stab (Rank 1)"
	numTargets, mana, Effects = 1, 2, ""
	description = "Deal 2 damage. (Upgrades when you have 5 mana.)"
	upgrade_5, upgrade_10 = WickedStabRank2, WickedStabRank3
	name_CN = "邪恶挥刺（等级1）"
	def text(self): return self.calcDamage(2)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(target, self.calcDamage(2))
		
	
class FieldContact(Minion):
	Class, race, name = "Rogue", "", "Field Contact"
	mana, attack, health = 3, 3, 2
	numTargets, Effects, description = 0, "", "After you play a Battlecry or Combo card, draw a card"
	name_CN = "原野联络人"
	trigBoard = Trig_FieldContact
	
	
class SwinetuskShank(Weapon):
	Class, name, description = "Rogue", "Swinetusk Shank", "After you play a Poison gain +1 Durability"
	mana, attack, durability, Effects = 3, 2, 2, ""
	name_CN = "猪牙匕首"
	trigBoard = Trig_SwinetuskShank
	
	
class ApothecaryHelbrim(Minion):
	Class, race, name = "Rogue", "", "Apothecary Helbrim"
	mana, attack, health = 4, 3, 2
	name_CN = "药剂师赫布拉姆"
	numTargets, Effects, description = 0, "", "Battlecry and Deathrattle: Add a random Poison to your hand"
	index = "Battlecry~Legendary"
	deathrattle = Death_ApothecaryHelbrim
	poolIdentifier = "Poisons"
	@classmethod
	def generatePool(cls, pools):
		return "Poisons", [card for card in pools.ClassCards["Rogue"] if card.category == "Spell" and "Poison" in card.name]
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.addCardtoHand(numpyChoice(self.rngPool("Poisons")), self.ID)
		
	
class OilRigAmbusher(Minion):
	Class, race, name = "Rogue", "", "Oil Rig Ambusher"
	mana, attack, health = 4, 4, 4
	name_CN = "油田伏击者"
	numTargets, Effects, description = 1, "", "Battlecry: Deal 2 damamge. If this entered your hand this turn, deal 4 damage instead"
	index = "Battlecry"
	def effCanTrig(self):
		self.effectViable = self.enterHandTurn == self.Game.turnInd
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(target, 4 if self.enterHandTurn == self.Game.turnInd else 2)
		
	
class ScabbsCutterbutter(Minion):
	Class, race, name = "Rogue", "", "Scabbs Cutterbutter"
	mana, attack, health = 4, 3, 3
	name_CN = "斯卡布斯·刀油"
	numTargets, Effects, description = 0, "", "Combo: The next two cards you play this turn cost (3) less"
	index = "Combo~Legendary"
	trigEffect = GameManaAura_ScabbsCutterbutter
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.comboCounters[self.ID] > 0
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.Game.Counters.comboCounters[self.ID] > 0:
			GameManaAura_ScabbsCutterbutter(self.Game, self.ID).auraAppears()
		
	
class SpawnpoolForager(Minion):
	Class, race, name = "Shaman", "Murloc", "Spawnpool Forager"
	mana, attack, health = 1, 1, 2
	numTargets, Effects, description = 0, "", "Deathrattle: Summon a 1/1 Tinyfin"
	name_CN = "孵化池觅食者"
	deathrattle = Death_SpawnpoolForager
	
	
class DiremuckTinyfin(Minion):
	Class, race, name = "Shaman", "Murloc", "Diremuck Tinyfin"
	mana, attack, health = 1, 1, 1
	name_CN = "凶饿的鱼人宝宝"
	numTargets, Effects, description = 0, "", ""
	index = "Uncollectible"
	
	
class ChainLightningRank3(Spell):
	Class, school, name = "Shaman", "Nature", "Chain Lightning (Rank 3)"
	numTargets, mana, Effects = 1, 2, ""
	name_CN = "闪电链（等级3）"
	description = "Deal 4 damage to a minion and a random adjacent one"
	index = "Uncollectible"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def text(self): return self.calcDamage(4)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		damage = self.calcDamage(4)
		for obj in target: self.dealsDamage((obj, numpyChoice(neighbors)) if (neighbors := self.Game.neighbors2(obj)[0]) else (obj,), damage)
		
	
class ChainLightningRank2(Spell_Forge):
	Class, school, name = "Shaman", "Nature", "Chain Lightning (Rank 2)"
	numTargets, mana, Effects = 1, 2, ""
	name_CN = "闪电链（等级2）"
	description = "Deal 3 damage to a minion and a random adjacent one. (Upgrades when you have 10 mana.)"
	upgrade_10 = ChainLightningRank3
	index = "Uncollectible"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def text(self): return self.calcDamage(3)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		damage = self.calcDamage(3)
		for obj in target: self.dealsDamage((obj, numpyChoice(neighbors)) if (neighbors := self.Game.neighbors2(obj)[0]) else (obj,), damage)
		
	
class ChainLightningRank1(Spell_Forge):
	Class, school, name = "Shaman", "Nature", "Chain Lightning (Rank 1)"
	numTargets, mana, Effects = 1, 2, ""
	description = "Deal 2 damage to a minion and a random adjacent one. (Upgrades when you have 5 mana.)"
	upgrade_5, upgrade_10 = ChainLightningRank2, ChainLightningRank3
	name_CN = "闪电链（等级1）"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def text(self): return self.calcDamage(2)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		damage = self.calcDamage(2)
		for obj in target: self.dealsDamage((obj, numpyChoice(neighbors)) if (neighbors := self.Game.neighbors2(obj)[0]) else (obj,), damage)
		
	
class FiremancerFlurgl(Minion):
	Class, race, name = "Shaman", "Murloc", "Firemancer Flurgl"
	mana, attack, health = 2, 2, 3
	name_CN = "火焰术士弗洛格尔"
	numTargets, Effects, description = 0, "", "After you play a Murloc, deal 1 damage to all enemies"
	index = "Legendary"
	trigBoard = Trig_FiremancerFlurgl
	
	
class SouthCoastChieftain(Minion):
	Class, race, name = "Shaman", "Murloc", "South Coast Chieftain"
	mana, attack, health = 2, 3, 2
	name_CN = "南海岸酋长"
	numTargets, Effects, description = 1, "", "Battlecry: If you control another Murloc, deal 2 damage"
	index = "Battlecry"
	def effCanTrig(self):
		self.effectViable = 1 and self.Game.minionsonBoard(self.ID, race="Murloc")
		
	def numTargetsNeeded(self, choice=0):
		return 1 if self.Game.minionsonBoard(self.ID, race="Murloc") else 0
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj is not self and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.Game.minionsonBoard(self.ID, race="Murloc"): self.dealsDamage(target, 2)
		
	
class TinyfinsCaravan(Minion):
	Class, race, name = "Shaman", "", "Tinyfin's Caravan"
	mana, attack, health = 2, 1, 3
	numTargets, Effects, description = 0, "", "At the start of your turn, draw a Murloc"
	name_CN = "鱼人宝宝车队"
	trigBoard = Trig_TinyfinsCaravan
	
	
class AridStormer(Minion):
	Class, race, name = "Shaman", "Elemental", "Arid Stormer"
	mana, attack, health = 3, 2, 5
	name_CN = "旱地风暴"
	numTargets, Effects, description = 0, "", "Battlecry: If you played an Elemental last turn, gain Rush and Windfury"
	index = "Battlecry"
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.examElementalsLastTurn(self.ID)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.Game.Counters.examElementalsLastTurn(self.ID):
			self.giveEnchant(self, multipleEffGains=(("Rush", 1, None), ("Windfury", 1, None)), source=AridStormer)
		
	
class NofinCanStopUs(Spell):
	Class, school, name = "Shaman", "", "Nofin Can Stop Us"
	numTargets, mana, Effects = 0, 3, ""
	description = "Give your minions +1/+1. Give your Murlocs an extra +1/+1"
	name_CN = "鱼勇可贾"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant([minion for minion in self.Game.minionsonBoard(self.ID) if "Murloc" not in minion.race],
						 1, 1, source=NofinCanStopUs)
		self.giveEnchant(self.Game.minionsonBoard(self.ID, race="Murloc"), 2, 2, source=NofinCanStopUs)
		
	
class Brukan(Minion):
	Class, race, name = "Shaman", "", "Bru'kan"
	mana, attack, health = 4, 5, 4
	name_CN = "布鲁坎"
	numTargets, Effects, description = 0, "Nature Spell Damage_3", "Nature Spell Damage +3"
	index = "Legendary"
	
	
class EarthRevenant(Minion):
	Class, race, name = "Shaman", "Elemental", "Earth Revenant"
	mana, attack, health = 4, 2, 6
	name_CN = "大地亡魂"
	numTargets, Effects, description = 0, "Taunt", "Taunt. Battlecry: Deal 1 damage to all enemy minions"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(self.Game.minionsonBoard(3-self.ID), 1)
		
	
class LilypadLurker(Minion):
	Class, race, name = "Shaman", "Elemental", "Lilypad Lurker"
	mana, attack, health = 5, 5, 6
	name_CN = "荷塘潜伏者"
	numTargets, Effects, description = 1, "", "Battlecry: If you played an Elemental last turn, transform an enemy minion into a 0/1 Frog with Taunt"
	index = "Battlecry"
	def numTargetsNeeded(self, choice=0):
		return 1 if self.Game.Counters.examElementalsLastTurn(self.ID) else 0
		
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.examElementalsLastTurn(self.ID)
		
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists(choice)
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj is not self and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.Game.Counters.examElementalsLastTurn(self.ID):
			self.transform(target, [Frog(self.Game, self.ID) for _ in target])
		
	
class AltarofFire(Spell):
	Class, school, name = "Warlock", "Fire", "Altar of Fire"
	numTargets, mana, Effects = 0, 1, ""
	description = "Destroy a friendly minion. Deal 2 damage to all enemy minions"
	name_CN = "火焰祭坛"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.Game.Hand_Deck.removeDeckTopCard(self.ID, num=3)
		self.Game.Hand_Deck.removeDeckTopCard(3-self.ID, num=3)
		
	
class GrimoireofSacrifice(Spell):
	Class, school, name = "Warlock", "Shadow", "Grimoire of Sacrifice"
	numTargets, mana, Effects = 1, 1, ""
	description = "Destroy a friendly minion. Deal 2 damage to all enemy minions"
	name_CN = "牺牲魔典"
	def available(self):
		return self.selectableMinionExists(self.ID)
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard and obj.ID == self.ID
		
	def text(self): return self.calcDamage(2)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.Game.kill(self, target)
		self.dealsDamage(self.Game.minionsonBoard(3-self.ID), self.calcDamage(2))
		
	
class ApothecarysCaravan(Minion):
	Class, race, name = "Warlock", "", "Apothecary's Caravan"
	mana, attack, health = 2, 1, 3
	numTargets, Effects, description = 0, "", "At the start of your turn, summon a 1-Cost minion from your deck"
	name_CN = "药剂师车队"
	trigBoard = Trig_ApothecarysCaravan
	
	
class ImpSwarmRank3(Spell):
	Class, school, name = "Warlock", "Fel", "Imp Swarm (Rank 3)"
	numTargets, mana, Effects = 0, 2, ""
	name_CN = "小鬼集群（等级3）"
	description = "Summon three 3/2 Imps"
	index = "Uncollectible"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon([ImpFamiliar(self.Game, self.ID) for _ in (0, 1, 2)])
		
	
class ImpSwarmRank2(Spell_Forge):
	Class, school, name = "Warlock", "Fel", "Imp Swarm (Rank 2)"
	numTargets, mana, Effects = 0, 2, ""
	name_CN = "小鬼集群（等级2）"
	description = "Summon two 3/2 Imps. (Upgrades when you have 10 Mana.)"
	upgrade_10 = ImpSwarmRank3
	index = "Uncollectible"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon([ImpFamiliar(self.Game, self.ID) for _ in (0, 1)])
		
	
class ImpSwarmRank1(Spell_Forge):
	Class, school, name = "Warlock", "Fel", "Imp Swarm (Rank 1)"
	numTargets, mana, Effects = 0, 2, ""
	description = "Summon a 3/2 Imp. (Upgrades when you have 5 mana.)"
	upgrade_5, upgrade_10 = ImpSwarmRank2, ImpSwarmRank3
	name_CN = "小鬼集群（等级1）"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon(ImpFamiliar(self.Game, self.ID))
		
	
class ImpFamiliar(Minion):
	Class, race, name = "Warlock", "Demon", "Imp Familiar"
	mana, attack, health = 2, 3, 2
	name_CN = "小鬼魔仆"
	numTargets, Effects, description = 0, "", ""
	index = "Uncollectible"
	
	
class BloodShardBristleback(Minion):
	Class, race, name = "Warlock", "Quilboar", "Blood Shard Bristleback"
	mana, attack, health = 3, 3, 3
	name_CN = " 血之碎片刺背野猪人"
	numTargets, Effects, description = 1, "Lifesteal", "Lifesteal. Battlecry: If your deck contains 10 or fewer cards, deal 6 damage to a minion"
	index = "Battlecry"
	def numTargetsNeeded(self, choice=0):
		return 1 if len(self.Game.Hand_Deck.decks[self.ID]) < 11 else 0
		
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.onBoard and obj.category == "Minion" and obj is not self
		
	def effCanTrig(self):
		self.effectViable = len(self.Game.Hand_Deck.decks[self.ID]) < 11
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if len(self.Game.Hand_Deck.decks[self.ID]) < 11: self.dealsDamage(target, 6)
		
	
class KabalOutfitter(Minion):
	Class, race, name = "Warlock", "", "Kabal Outfitter"
	mana, attack, health = 3, 3, 3
	name_CN = "暗金教物资官"
	numTargets, Effects, description = 0, "", "Battlecry and Deathrattle: Give another random friendly minion +1/+1"
	index = "Battlecry"
	deathrattle = Death_KabalOutfitter
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if minions := self.Game.minionsonBoard(self.ID, exclude=self): self.giveEnchant(numpyChoice(minions), 1, 1,
																						source=KabalOutfitter)
		
	
class TamsinRoame(Minion):
	Class, race, name = "Warlock", "", "Tamsin Roame"
	mana, attack, health = 3, 1, 3
	name_CN = "塔姆辛·罗姆"
	numTargets, Effects, description = 0, "", "Whenever you cast a Shadow spell that costs (1) or more, add a copy to your hand that costs (0)"
	index = "Legendary"
	trigBoard = Trig_TamsinRoame
	
	
class SoulRend(Spell):
	Class, school, name = "Warlock", "Shadow", "Soul Rend"
	numTargets, mana, Effects = 0, 4, ""
	description = "Deal 5 damage to all minions. Destroy a card in your deck for each killed"
	name_CN = "灵魂撕裂"
	def text(self): return self.calcDamage(5)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		dmgTakers = self.dealsDamage(self.Game.minionsonBoard(), self.calcDamage(5))
		if numKilled := sum(obj.health < 1 or obj.dead for obj in dmgTakers):
			self.Game.Hand_Deck.removeDeckTopCard(self.ID, numKilled)
		
	
class NeeruFireblade(Minion):
	Class, race, name = "Warlock", "", "Neeru Fireblade"
	mana, attack, health = 5, 5, 5
	name_CN = "尼尔鲁·火刃"
	numTargets, Effects, description = 0, "", "Battlecry: If your deck is empty, open a portal that fills your board with 3/2 Imps each turn"
	index = "Battlecry~Legendary"
	def effCanTrig(self):
		self.effectViable = not self.Game.Hand_Deck.decks[self.ID]
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if not self.Game.Hand_Deck.decks[self.ID]:
			self.Game.summonSingle(BurningBladePortal(self.Game, self.ID), self.pos + 1, self)
		
	
class BurningBladePortal(Minion):
	Class, name = "Warlock", "Burning Blade Portal"
	description = "At the end of your turn, fill your board with 3/2 Imps"
	index = "Legendary~Uncollectible"
	trigBoard = Trig_BurningBladePortal
	category = "Dormant"
	
	
class BarrensScavenger(Minion):
	Class, race, name = "Warlock", "", "Barrens Scavenger"
	mana, attack, health = 6, 6, 6
	numTargets, Effects, description = 0, "Taunt", "Taunt。 Costs(1) while your deck has 10 or fewer cards"
	name_CN = "贫瘠之地拾荒者"
	trigHand = Trig_BarrensScavenger
	def selfManaChange(self):
		if len(self.Game.Hand_Deck.decks[self.ID]) < 11: self.mana = 1
		
	
class WarsongEnvoy(Minion):
	Class, race, name = "Warrior", "", "Warsong Envoy"
	mana, attack, health = 1, 1, 3
	numTargets, Effects, description = 0, "", "Frenzy: Gain +1 Attack for each damaged character"
	name_CN = "战歌大使"
	index = "Frenzy"
	trigBoard = Trig_WarsongEnvoy
	
	
class BulkUp(Spell):
	Class, school, name = "Warrior", "", "Bulk Up"
	numTargets, mana, Effects = 0, 2, ""
	description = "Give a random Taunt minion in your hand +1/+1 and copy it"
	name_CN = "重装上阵"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if minions := [card for card in self.Game.Hand_Deck.hands[self.ID] if card.category == "Minion" and card.effects["Taunt"] > 0]:
			self.giveEnchant((minion := numpyChoice(minions)), 1, 1, source=BulkUp, add2EventinGUI=False)
			self.addCardtoHand(self.copyCard(minion, self.ID), self.ID)
		
	
class ConditioningRank3(Spell):
	Class, school, name = "Warrior", "", "Conditioning (Rank 3)"
	numTargets, mana, Effects = 0, 2, ""
	name_CN = "体格训练（等级3）"
	description = "Give minions in your hand +3/+3"
	index = "Uncollectible"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant([card for card in self.Game.Hand_Deck.hands[self.ID] if card.category == "Minion"], 3, 3,
						 source=ConditioningRank3, add2EventinGUI=False)
		
	
class ConditioningRank2(Spell_Forge):
	Class, school, name = "Warrior", "", "Conditioning (Rank 2)"
	numTargets, mana, Effects = 0, 2, ""
	name_CN = "体格训练（等级2）"
	description = "Give minions in your hand +2/+2. (Upgrades when you have 10 mana.)"
	upgrade_10 = ConditioningRank3
	index = "Uncollectible"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant([card for card in self.Game.Hand_Deck.hands[self.ID] if card.category == "Minion"], 2, 2,
						 source=ConditioningRank2, add2EventinGUI=False)
		
	
class ConditioningRank1(Spell_Forge):
	Class, school, name = "Warrior", "", "Conditioning (Rank 1)"
	numTargets, mana, Effects = 0, 2, ""
	description = "Give minions in your hand +1/+1. (Upgrades when you have 5 mana.)"
	upgrade_5, upgrade_10 = ConditioningRank2, ConditioningRank3
	name_CN = "体格训练（等级1）"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant([card for card in self.Game.Hand_Deck.hands[self.ID] if card.category == "Minion"], 1, 1,
						 source=ConditioningRank1, add2EventinGUI=False)
		
	
class Rokara(Minion):
	Class, race, name = "Warrior", "", "Rokara"
	mana, attack, health = 3, 2, 3
	name_CN = "洛卡拉"
	numTargets, Effects, description = 0, "Rush", "Rush. After a friendly minion attacks and survives, give it +1/+1"
	index = "Legendary"
	trigBoard = Trig_Rokara
	
	
class OutridersAxe(Weapon):
	Class, name, description = "Warrior", "Outrider's Axe", "After your hero attacks and kills a minion, draw a card"
	mana, attack, durability, Effects = 4, 3, 3, ""
	name_CN = "先锋战斧"
	trigBoard = Trig_OutridersAxe
	
	
class Rancor(Spell):
	Class, school, name = "Warrior", "", "Rancor"
	numTargets, mana, Effects = 0, 4, ""
	description = "Deal 2 damage to all minions. Gain 2 Armor for each destroyed"
	name_CN = "仇怨累积"
	def text(self): return self.calcDamage(2)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		dmgTakers = self.dealsDamage(self.Game.minionsonBoard(), self.calcDamage(2))
		if num := sum(minion.health < 1 or minion.dead for minion in dmgTakers):
			self.giveHeroAttackArmor(self.ID, armor=num*2)
		
	
class WhirlingCombatant(Minion):
	Class, race, name = "Warrior", "", "Whirling Combatant"
	mana, attack, health = 4, 3, 6
	numTargets, Effects, description = 0, "", "Battlecry and Frenzy: Deal 1 damage to all other minions"
	name_CN = "旋风争斗者"
	index = "Frenzy~Battlecry"
	trigBoard = Trig_WhirlingCombatant
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(self.Game.minionsonBoard(exclude=self), 1)
		
	
class MorshanElite(Minion):
	Class, race, name = "Warrior", "", "Mor'shan Elite"
	mana, attack, health = 5, 4, 4
	name_CN = "莫尔杉精锐"
	numTargets, Effects, description = 0, "Taunt", "Taunt. Battlecry: If your hero attacked this turn, summon a copy of this"
	index = "Battlecry"
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.examHeroAtks(self.ID, turnInd=self.Game.turnInd)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if not self.dead and self.Game.Counters.examHeroAtks(self.ID, turnInd=self.Game.turnInd):
			self.summon(self.copyCard(self, self.ID))
		
	
class StonemaulAnchorman(Minion):
	Class, race, name = "Warrior", "Pirate", "Stonemaul Anchorman"
	mana, attack, health = 5, 4, 6
	numTargets, Effects, description = 0, "Rush", "Rush. Frenzy: Draw a card"
	name_CN = "石槌掌锚者"
	index = "Frenzy"
	trigBoard = Trig_StonemaulAnchorman
	
	
class OverlordSaurfang(Minion):
	Class, race, name = "Warrior", "", "Overlord Saurfang"
	mana, attack, health = 7, 5, 4
	name_CN = "萨鲁法尔大王"
	numTargets, Effects, description = 0, "", "Battlecry: Resurrect two friendly Frenzy minions. Deal 1 damage to all other minions"
	index = "Battlecry~Legendary"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		game = self.Game
		if tups := game.Counters.examDeads(self.ID, veri_sum_ls=2, cond=lambda card: "~Frenzy" in card.index):
			tups = numpyChoice(tups, min(2, len(tups)), replace=False)
			self.summon([game.fabCard(tup, self.ID, self) for tup in tups], relative="<>")
		self.dealsDamage(game.minionsonBoard(exclude=self), 1)
		
	
class DeadlyAdventurer(Minion):
	Class, race, name = "Neutral", "", "Deadly Adventurer"
	mana, attack, health = 2, 2, 2
	name_CN = "致命的冒险者"
	numTargets, Effects, description = 0, "Poisonous", "Poisonous"
	index = "Uncollectible"
	
	
class BurlyAdventurer(Minion):
	Class, race, name = "Neutral", "", "Burly Adventurer"
	mana, attack, health = 2, 2, 2
	name_CN = "健壮的冒险者"
	numTargets, Effects, description = 0, "Taunt", "Taunt"
	index = "Uncollectible"
	
	
class DevoutAdventurer(Minion):
	Class, race, name = "Neutral", "", "Devout Adventurer"
	mana, attack, health = 2, 2, 2
	name_CN = "虔诚的冒险者"
	numTargets, Effects, description = 0, "Divine Shield", "Divine Shield"
	index = "Uncollectible"
	
	
class RelentlessAdventurer(Minion):
	Class, race, name = "Neutral", "", "Relentless Adventurer"
	mana, attack, health = 2, 2, 2
	name_CN = "无情的冒险者"
	numTargets, Effects, description = 0, "Windfury", "Windfury"
	index = "Uncollectible"
	
	
class ArcaneAdventurer(Minion):
	Class, race, name = "Neutral", "", "Arcane Adventurer"
	mana, attack, health = 2, 2, 2
	name_CN = "奥术冒险者"
	numTargets, Effects, description = 0, "Spell Damage", "Spell Damage+1"
	index = "Uncollectible"
	
	
class SneakyAdventurer(Minion):
	Class, race, name = "Neutral", "", "Sneaky Adventurer"
	mana, attack, health = 2, 2, 2
	name_CN = "鬼祟的冒险者"
	numTargets, Effects, description = 0, "Stealth", "Stealth"
	index = "Uncollectible"
	
	
class VitalAdventurer(Minion):
	Class, race, name = "Neutral", "", "Vital Adventurer"
	mana, attack, health = 2, 2, 2
	name_CN = "活跃的冒险者"
	numTargets, Effects, description = 0, "Lifesteal", "Lifesteal"
	index = "Uncollectible"
	
	
class SwiftAdventurer(Minion):
	Class, race, name = "Neutral", "", "Swift Adventurer"
	mana, attack, health = 2, 2, 2
	name_CN = "迅捷的冒险者"
	numTargets, Effects, description = 0, "Rush", "Rush"
	index = "Uncollectible"
	
	
class MeetingStone(Minion):
	Class, race, name = "Neutral", "", "Meeting Stone"
	mana, attack, health = 1, 0, 2
	numTargets, Effects, description = 0, "", "At the end of your turn, add a 2/2 Adventurer with random bonus effect to your hand"
	name_CN = "集合石"
	trigBoard = Trig_MeetingStone
	
	
class DevouringEctoplasm(Minion):
	Class, race, name = "Neutral", "", "Devouring Ectoplasm"
	mana, attack, health = 3, 3, 2
	numTargets, Effects, description = 0, "", "Deathrattle: Summon a 2/2 Adventurer with random bonus effect"
	name_CN = "吞噬软浆怪"
	deathrattle = Death_DevouringEctoplasm
	
	
class ArchdruidNaralex(Minion):
	Class, race, name = "Neutral", "", "Archdruid Naralex"
	mana, attack, health = 3, 3, 3
	name_CN = "大德鲁伊纳拉雷克斯"
	numTargets, Effects, description = 0, "", "Dormant for 2 turns. While Dormant, add a Dream card to your hand at the end of your turn"
	index = "Legendary"
	def appears_fromPlay(self, choice):
		obj = super().appears(True, Trig_Imprisoned(self))
		obj.trigsBoard.append(trig := Trig_SleepingNaralex(obj))
		trig.connect()
		return
		
	def appears(self, firstTime=True, dormantTrig=None):
		return super().appears(firstTime, Trig_Imprisoned(self) if firstTime else None)
		
	
class MutanustheDevourer(Minion):
	Class, race, name = "Neutral", "Murloc", "Mutanus the Devourer"
	mana, attack, health = 7, 4, 4
	name_CN = "吞噬者穆坦努斯"
	numTargets, Effects, description = 0, "", "Battlecry: Eat a minion in your opponent's hand. Gain its effect"
	index = "Battlecry~Legendary"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if indices := [i for i, card in enumerate(self.Game.Hand_Deck.hands[3-self.ID]) if card.category == "Minion"]:
			minion = self.Game.Hand_Deck.extractfromHand(numpyChoice(indices), self.ID)[0]
			self.giveEnchant(self, minion.attack, minion.health, source=MutanustheDevourer)
		
	
class SelflessSidekick(Minion):
	Class, race, name = "Neutral", "", "Selfless Sidekick"
	mana, attack, health = 7, 6, 6
	name_CN = "无私的同伴"
	numTargets, Effects, description = 0, "", "Battlecry: Equip a random weapon from your deck"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if indices := [i for i, card in enumerate(self.Game.Hand_Deck.decks[self.ID]) if card.category == "Weapon"]:
			self.Game.equipWeapon(self.Game.Hand_Deck.extractfromDeck(numpyChoice(indices), self.ID, animate=False))
		
	
class SigilofSummoning(Spell_Sigil):
	Class, school, name = "Demon Hunter", "Shadow", "Sigil of Summoning"
	numTargets, mana, Effects = 0, 2, ""
	description = "At the start of your next turn, summmon two 2/2 Demons with Taunt"
	name_CN = "召唤咒符"
	trigEffect = SigilofSummoning_Effect
	
	
class WailingDemon(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Wailing Demon"
	mana, attack, health = 2, 2, 2
	name_CN = "哀嚎恶魔"
	numTargets, Effects, description = 0, "Taunt", "Taunt"
	index = "Uncollectible"
	
	
class Felrattler(Minion):
	Class, race, name = "Demon Hunter", "Beast", "Felrattler"
	mana, attack, health = 3, 3, 2
	numTargets, Effects, description = 0, "Rush", "Rush. Deathrattle: Deal 1 damage to all enemy minions"
	name_CN = "邪能响尾蛇"
	deathrattle = Death_Felrattler
	
	
class TaintheartTormenter(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Taintheart Tormenter"
	mana, attack, health = 8, 8, 8
	numTargets, Effects, description = 0, "Taunt", "Taunt. Your opponent's spells cost (2) more"
	name_CN = "污心拷问者"
	aura = ManaAura_TaintheartTormenter
	
	
class FangboundDruid(Minion):
	Class, race, name = "Druid", "", "Fangbound Druid"
	mana, attack, health = 3, 4, 3
	numTargets, Effects, description = 0, "Taunt", "Taunt. Deathrattle: Reduce the cost of a random Beast in your hand by (2)"
	name_CN = "牙缚德鲁伊"
	deathrattle = Death_FangboundDruid
	
	
class LadyAnacondra(Minion):
	Class, race, name = "Druid", "", "Lady Anacondra"
	mana, attack, health = 6, 3, 7
	name_CN = "安娜康德拉"
	numTargets, Effects, description = 0, "", "Your Nature spells cost (2) less"
	index = "Legendary"
	aura = ManaAura_LadyAnacondra
	
	
class DeviateDreadfang(Minion):
	Class, race, name = "Druid", "Beast", "Deviate Dreadfang"
	mana, attack, health = 8, 4, 9
	numTargets, Effects, description = 0, "", "After you cast a Nature spell, summon a 4/2 Viper with Rush"
	name_CN = "变异尖牙风蛇"
	trigBoard = Trig_DeviateDreadfang
	
	
class DeviateViper(Minion):
	Class, race, name = "Druid", "Beast", "Deviate Viper"
	mana, attack, health = 3, 4, 2
	name_CN = "变异飞蛇"
	numTargets, Effects, description = 0, "Rush", "Rush"
	index = "Uncollectible"
	
	
class Serpentbloom(Spell):
	Class, school, name = "Hunter", "", "Serpentbloom"
	numTargets, mana, Effects = 1, 0, ""
	description = "Give a friendly Beast Poisonous"
	name_CN = "毒蛇花"
	def available(self):
		return self.selectableMinionExists(self.ID)
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.ID == self.ID and obj.onBoard and "Beast" in obj.race
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(target, effGain="Poisonous", source=Serpentbloom)
		
	
class SindoreiScentfinder(Minion):
	Class, race, name = "Hunter", "", "Sin'dorei Scentfinder"
	mana, attack, health = 4, 1, 6
	numTargets, Effects, description = 0, "", "Frenzy: Summon four 1/1 Hyenas with Rush"
	name_CN = "辛多雷气味猎手"
	index = "Frenzy"
	trigBoard = Trig_SindoreiScentfinder
	
	
class VenomstrikeBow(Weapon):
	Class, name, description = "Hunter", "Venomstrike Bow", "Poisonous"
	mana, attack, durability, Effects = 4, 1, 2, "Poisonous"
	name_CN = "毒袭之弓"
	
	
class FrostweaveDungeoneer(Minion):
	Class, race, name = "Mage", "", "Frostweave Dungeoneer"
	mana, attack, health = 3, 2, 3
	name_CN = "织霜地下城历险家"
	numTargets, Effects, description = 0, "", "Battlecry: Draw a spell. If it's a Frost spell, summon two 1/1 Elementals that Freeze"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if (spell := self.drawCertainCard(lambda card: card.category == "Spell")[0]) and spell.school == "Frost":
			self.summon([FrostedElemental(self.Game, self.ID) for _ in (0, 1)], relative="<>")
		
	
class ShatteringBlast(Spell):
	Class, school, name = "Mage", "Frost", "Shattering Blast"
	numTargets, mana, Effects = 0, 3, ""
	description = "Destroy all Frozen minions"
	name_CN = "冰爆冲击"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		objs = [minion for minion in self.Game.minionsonBoard() if minion.effects["Frozen"] > 0]
		self.Game.kill(self, objs)
		
	
class Floecaster(Minion):
	Class, race, name = "Mage", "", "Floecaster"
	mana, attack, health = 6, 5, 5
	numTargets, Effects, description = 0, "", "Costs (2) less for each Frozen enemy"
	name_CN = "浮冰施法者"
	trigHand = Trig_Floecaster
	def selfManaChange(self):
		num = sum(char.effects["Frozen"] > 0 for char in self.Game.minionsonBoard(3-self.ID))
		if self.Game.heroes[3-self.ID].effects["Frozen"] > 0: num += 1
		self.mana -= 2 * num
		
	
class JudgmentofJustice(Secret):
	Class, school, name = "Paladin", "Holy", "Judgment of Justice"
	numTargets, mana, Effects = 0, 1, ""
	description = "Secret: When an enemy minion attacks, set its Attack and Health to 1"
	name_CN = "公正审判"
	trigBoard = Trig_JudgmentofJustice
	
	
class SeedcloudBuckler(Weapon):
	Class, name, description = "Paladin", "Seedcloud Buckler", "Deathrattle: Give your minions Divine Shield"
	mana, attack, durability, Effects = 3, 2, 3, ""
	name_CN = "淡云圆盾"
	deathrattle = Death_SeedcloudBuckler
	
	
class PartyUp(Spell):
	Class, school, name = "Paladin", "", "Party Up!"
	numTargets, mana, Effects = 0, 7, ""
	description = "Summon five 2/2 Adventurers with random bonus effects"
	name_CN = "小队集合"
	adventurers = (DeadlyAdventurer, BurlyAdventurer, DevoutAdventurer, RelentlessAdventurer,
				   ArcaneAdventurer, SneakyAdventurer, VitalAdventurer, SwiftAdventurer)
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon([minion(self.Game, self.ID) for minion in numpyChoice(PartyUp.adventurers, 5, replace=True)])
		
	
class ClericofAnshe(Minion):
	Class, race, name = "Priest", "", "Cleric of An'she"
	mana, attack, health = 1, 1, 2
	name_CN = "安瑟教士"
	numTargets, Effects, description = 0, "", "Battlecry: If you've restored Health this turn, Discover a spell from your deck"
	index = "Battlecry"
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.examHealThisTurn(self.ID)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.Game.Counters.examHealThisTurn(self.ID):
			_, i = self.discoverfrom(comment, cond=lambda card: card.category == "Spell")
			if i > -1: self.Game.Hand_Deck.drawCard(self.ID, i)
		
	
class DevoutDungeoneer(Minion):
	Class, race, name = "Priest", "", "Devout Dungeoneer"
	mana, attack, health = 3, 2, 3
	name_CN = "虔诚地下城历险家"
	numTargets, Effects, description = 0, "", "Battlecry: Draw a spell. If it's a Holy spell, reduce its Cost by (2)"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		spell, mana, entersHand = self.drawCertainCard(lambda card: card.category == "Spell")
		if entersHand and spell.school == "Holy": ManaMod(spell, by=-2).applies()
		
	
class AgainstAllOdds(Spell):
	Class, school, name = "Priest", "Holy", "Against All Odds"
	numTargets, mana, Effects = 0, 5, ""
	description = "Destroy ALL odd-Attack minions"
	name_CN = "除奇致胜"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		objs = [minion for minion in self.Game.minionsonBoard() if minion.attack % 2 == 1]
		if objs: self.Game.kill(self, objs)
		
	
class SavoryDeviateDelight(Spell):
	Class, school, name = "Rogue", "", "Savory Deviate Delight"
	numTargets, mana, Effects = 0, 1, ""
	description = "Transform a minion in both players' hands into a Pirate or Stealth minion"
	name_CN = "美味风蛇"
	poolIdentifier = "Stealth Minions"
	@classmethod
	def generatePool(cls, pools):
		return "Stealth Minions", [card for cards in pools.MinionsofCost.values() for card in cards if "Stealth" in card.Effects]
		
	@classmethod
	def panda_MoveCardsfromHands(cls, game, GUI, cards):
		para = GUI.PARALLEL()
		for card in cards:
			para.append(GUI.LERP_PosHpr(card.btn.np, pos=(3, -5 if GUI.heroeZones[card.ID].y < 0 else 5, 20),
										duration=0.3, startHpr=(0, 0, 0), hpr=(0, 0, 0)))
		GUI.seqHolder[-1].append(para)
		GUI.seqHolder[-1].append(GUI.WAIT(0.4))
		
	@classmethod
	def panda_MoveCardsback2Hands(cls, GUI):
		GUI.seqHolder[-1].append(GUI.WAIT(1.3))
		GUI.handZones[1].placeCards()
		GUI.handZones[2].placeCards()
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		game = self.Game
		pool = self.rngPool("Pirates") + self.rngPool("Stealth Minions")
		minion1 = minion2 = newMinion1 = newMinion2 = None
		ls_Minions, ls_NewMinions = [], []
		if minions := [card for card in self.Game.Hand_Deck.hands[1] if card.category == "Minion"]:
			minion1, newMinion1 = numpyChoice(minions), numpyChoice(pool)(game, 1)
			ls_Minions.append(minion1)
			ls_NewMinions.append(newMinion1)
		if minions := [card for card in self.Game.Hand_Deck.hands[2] if card.category == "Minion"]:
			minion2, newMinion2 = numpyChoice(minions), numpyChoice(pool)(game, 1)
			ls_Minions.append(minion2)
			ls_NewMinions.append(newMinion2)
		if ls_Minions:
			if game.GUI: SavoryDeviateDelight.panda_MoveCardsfromHands(game, game.GUI, ls_Minions)
			game.transform(ls_Minions, ls_NewMinions, summoner=self)
			if game.GUI: SavoryDeviateDelight.panda_MoveCardsback2Hands(game.GUI)
		
	
class WaterMoccasin(Minion):
	Class, race, name = "Rogue", "Beast", "Water Moccasin"
	mana, attack, health = 3, 2, 5
	numTargets, Effects, description = 0, "Stealth", "Stealth. Has Poisonous while you have no other minions"
	name_CN = "水栖蝮蛇"
	aura = Aura_WaterMoccasin
	
	
class ShroudofConcealment(Spell):
	Class, school, name = "Rogue", "Shadow", "Shroud of Concealment"
	numTargets, mana, Effects = 0, 3, ""
	description = "Draw 2 minions. Any played this turn gain Stealth for 1 turn"
	name_CN = "潜行帷幕"
	trigEffect = ShroudofConcealment_Effect
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		minion1, mana, entersHand1 = self.drawCertainCard(lambda card: card.category == "Minion")
		if entersHand1:
			minion2, mana, entersHand2 = self.drawCertainCard(lambda card: card.category == "Minion")
			minions = [minion1, minion2] if entersHand2 else [minion1]
			ShroudofConcealment_Effect(self.Game, self.ID, minions).connect()
		
	
class PerpetualFlame(Spell):
	Class, school, name = "Shaman", "Fire", "Perpetual Flame"
	numTargets, mana, Effects = 0, 2, ""
	description = "Deal 3 damage to a random enemy minion. If it dies, recast this. Overload: (1)"
	name_CN = "永恒之火"
	overload = 1
	def text(self): return self.calcDamage(3)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if objs := self.Game.minionsAlive(3-self.ID):
			self.dealsDamage((minion := numpyChoice(objs)), self.calcDamage(3))
			if minion.dead or minion.health < 1: PerpetualFlame(self.Game, self.ID).cast()
		
	
class WailingVapor(Minion):
	Class, race, name = "Shaman", "Elemental", "Wailing Vapor"
	mana, attack, health = 1, 1, 3
	numTargets, Effects, description = 0, "", "After you play an Elemental, gain +1 Attack"
	name_CN = "哀嚎蒸汽"
	trigBoard = Trig_WailingVapor
	
	
class PrimalDungeoneer(Minion):
	Class, race, name = "Shaman", "", "Primal Dungeoneer"
	mana, attack, health = 3, 2, 3
	name_CN = "原初地下城历险家"
	numTargets, Effects, description = 0, "", "Battlecry: Draw a spell. If it's a Nature spell, draw an Elemental"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if (spell := self.drawCertainCard(lambda card: card.category == "Spell")[0]) and spell.school == "Nature":
			self.drawCertainCard(lambda card: "Elemental" in card.race)
		
	
class FinalGasp(Spell):
	Class, school, name = "Warlock", "Shadow", "Final Gasp"
	numTargets, mana, Effects = 1, 1, ""
	description = "Deal 1 damage to a minion. If it dies, summon a 2/2 Adventurer with random bonus effect"
	name_CN = "临终之息"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def text(self): return self.calcDamage(1)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for obj in target:
			self.dealsDamage(target, self.calcDamage(1))
			if obj.dead or obj.health < 1: self.summon(numpyChoice(PartyUp.adventurers)(self.Game, self.ID))
		
	
class UnstableShadowBlast(Spell):
	Class, school, name = "Warlock", "Shadow", "Unstable Shadow Blast"
	numTargets, mana, Effects = 1, 2, ""
	description = "Deal 6 damage to a minion. Excess damage hits your hero"
	name_CN = "不稳定的暗影震爆"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def text(self): return self.calcDamage(6)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		damage = self.calcDamage(6)
		for obj in target:
			dmgExcess = damage - (dmgReal := min(damage, max(obj.health, 0)))
			self.dealsDamage(obj, dmgReal)
			if dmgExcess: self.dealsDamage(self.Game.heroes[self.ID], dmgExcess)
		
	
class StealerofSouls(Minion):
	Class, race, name = "Warlock", "Demon", "Stealer of Souls"
	mana, attack, health = 6, 4, 6
	numTargets, Effects, description = 0, "", "After you draw a card, change its Cost to Health instead of Mana"
	name_CN = "灵魂窃者"
	trigBoard = Trig_StealerofSouls
	
	
class ManatArms(Minion):
	Class, race, name = "Warrior", "", "Man-at-Arms"
	mana, attack, health = 2, 2, 3
	name_CN = "武装战士"
	numTargets, Effects, description = 0, "", "Battlecry: If you have a weapon equipped, gain +1/+1"
	index = "Battlecry"
	def effCanTrig(self):
		self.effectViable = self.Game.availableWeapon(self.ID) is not None
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.Game.availableWeapon(self.ID): self.giveEnchant(self, 1, 1, source=ManatArms)
		
	
class WhetstoneHatchet(Weapon):
	Class, name, description = "Warrior", "Whetstone Hatchet", "After your hero attack, give a minion in your hand +1 Attack"
	mana, attack, durability, Effects = 1, 1, 4, ""
	name_CN = "砥石战斧"
	trigBoard = Trig_WhetstoneHatchet
	
	
class KreshLordofTurtling(Minion):
	Class, race, name = "Warrior", "Beast", "Kresh, Lord of Turtling"
	mana, attack, health = 6, 3, 9
	numTargets, Effects, description = 0, "", "Frenzy: Gain 8 Armor. Deathrattle: Equip a 2/5 Turtle Spike"
	name_CN = "克雷什，群龟之王"
	index = "Frenzy~Legendary"
	trigBoard, deathrattle = Trig_KreshLordofTurtling, Death_KreshLordofTurtling
	
	
class TurtleSpike(Weapon):
	Class, name, description = "Warrior", "Turtle Spike", ""
	mana, attack, durability, Effects = 4, 2, 5, ""
	name_CN = "龟甲尖刺"
	index = "Uncollectible"
	
	


AllClasses_Barrens = [
	KazakusGolem, ManaAura_BarrensTrapper, ManaAura_TaintheartTormenter, ManaAura_ArcaneLuminary, ManaAura_RazormaneBattleguard,
	ManaAura_LadyAnacondra, Aura_WaterMoccasin, Frenzy, Trig_ForgeUpgrade_Hand, Trig_ForgeUpgrade_Deck, Trig_FarWatchPost,
	Trig_LushwaterScout, Trig_OasisThrasher, Trig_Peon, Trig_CrossroadsGossiper, Trig_MorshanWatchPost, Trig_SunwellInitiate,
	Trig_BlademasterSamuro, Trig_CrossroadsWatchPost, Trig_GruntledPatron, Trig_SpiritHealer, Trig_BarrensBlacksmith,
	Trig_GoldRoadGrunt, Trig_RazormaneRaider, Trig_TaurajoBrave, Trig_GuffRunetotem, Trig_PlaguemawtheRotting, Trig_DruidofthePlains,
	Trig_SunscaleRaptor, Trig_KolkarPackRunner, Trig_ProspectorsCaravan, Trig_TavishStormpike, Trig_OasisAlly, Trig_Rimetongue,
	Trig_FrostedElemental, Trig_GallopingSavior, Trig_SoldiersCaravan, Trig_SwordoftheFallen, Trig_CarielRoame, Trig_VeteranWarmedic,
	Trig_SoothsayersCaravan, Trigger_PowerWordFortitude, Trig_ParalyticPoison, Trig_SwapBackPowerAfter2Uses, Trig_EfficientOctobot,
	Trig_SilverleafPoison, Trig_FieldContact, Trig_SwinetuskShank, Trig_FiremancerFlurgl, Trig_TinyfinsCaravan, Trig_ApothecarysCaravan,
	Trig_TamsinRoame, Trig_BurningBladePortal, Trig_BarrensScavenger, Trig_WarsongEnvoy, Trig_Rokara, Trig_OutridersAxe,
	Trig_WhirlingCombatant, Trig_StonemaulAnchorman, Trig_MeetingStone, Trig_SleepingNaralex, Trig_DeviateDreadfang,
	Trig_SindoreiScentfinder, Trig_Floecaster, Trig_JudgmentofJustice, Trig_WailingVapor, Trig_StealerofSouls, Trig_WhetstoneHatchet,
	Trig_KreshLordofTurtling, Death_DeathsHeadCultist, Death_DarkspearBerserker, Death_BurningBladeAcolyte, Death_Tuskpiercer,
	Death_Razorboar, Death_RazorfenBeastmaster, Death_ThickhideKodo, Death_NorthwatchSoldier, Death_LightshowerElemental,
	Death_ApothecaryHelbrim, Death_SpawnpoolForager, Death_KabalOutfitter, Death_DevouringEctoplasm, Death_Felrattler,
	Death_FangboundDruid, Death_SeedcloudBuckler, Death_KreshLordofTurtling, GameManaAura_KindlingElemental, TalentedArcanist_Effect,
	SigilofSilence_Effect, SigilofFlame_Effect, SigilofSummoning_Effect, ShroudofConcealment_Effect, GameManaAura_ScabbsCutterbutter,
	GameManaAura_RazormaneBattleguard, Spell_Forge, Spell_Sigil, KindlingElemental, FarWatchPost, HecklefangHyena,
	LushwaterMurcenary, LushwaterScout, OasisThrasher, Peon, TalentedArcanist, ToadoftheWilds, BarrensTrapper, CrossroadsGossiper,
	DeathsHeadCultist, HogRancher, Hog, HordeOperative, Mankrik, OlgraMankriksWife, MankrikConsumedbyHatred, MorshanWatchPost,
	WatchfulGrunt, RatchetPrivateer, SunwellInitiate, VenomousScorpid, BlademasterSamuro, CrossroadsWatchPost, DarkspearBerserker,
	GruntledPatron, InjuredMarauder, Golem_Lesser, Golem_Greater, Golem_Superior, Swiftthistle_Option, Earthroot_Option,
	Sungrass_Option, Liferoot_Option, Fadeleaf_Option, GraveMoss_Option, LesserGolem_Wildvine, GreaterGolem_Wildvine,
	SuperiorGolem_Wildvine, LesserGolem_Gromsblood, GreaterGolem_Gromsblood, SuperiorGolem_Gromsblood, LesserGolem_Icecap,
	GreaterGolem_Icecap, SuperiorGolem_Icecap, LesserGolem_Firebloom, GreaterGolem_Firebloom, SuperiorGolem_Firebloom,
	LesserGolem_Mageroyal, GreaterGolem_Mageroyal, SuperiorGolem_Mageroyal, LesserGolem_Kingsblood, GreaterGolem_Kingsblood,
	SuperiorGolem_Kingsblood, KazakusGolemShaper, SouthseaScoundrel, SpiritHealer, BarrensBlacksmith, BurningBladeAcolyte,
	Demonspawn, GoldRoadGrunt, RazormaneRaider, ShadowHunterVoljin, TaurajoBrave, KargalBattlescar, Lookout, PrimordialProtector,
	FuryRank3, FuryRank2, FuryRank1, Tuskpiercer, Razorboar, SigilofFlame, SigilofSilence, VileCall, RavenousVilefiend,
	RazorfenBeastmaster, KurtrusAshfallen, VengefulSpirit, DeathSpeakerBlackthorn, LivingSeedRank3, LivingSeedRank2,
	LivingSeedRank1, MarkoftheSpikeshell, RazormaneBattleguard, ThorngrowthSentries, ThornguardTurtle, GuffRunetotem,
	PlaguemawtheRotting, PridesFury, ThickhideKodo, CelestialAlignment, DruidofthePlains, DruidofthePlains_Taunt,
	SunscaleRaptor, WoundPrey, SwiftHyena, KolkarPackRunner, ProspectorsCaravan, TameBeastRank3, TameBeastRank2, TameBeastRank1,
	TamedCrab, TamedScorpid, TamedThunderLizard, PackKodo, TavishStormpike, PiercingShot, WarsongWrangler, BarakKodobane,
	FlurryRank3, FlurryRank2, FlurryRank1, RunedOrb, Wildfire, ArcaneLuminary, OasisAlly, Rimetongue, FrostedElemental,
	RecklessApprentice, RefreshingSpringWater, VardenDawngrasp, MordreshFireEye, ConvictionRank3, ConvictionRank2,
	ConvictionRank1, GallopingSavior, HolySteed, KnightofAnointment, SoldiersCaravan, SwordoftheFallen, NorthwatchCommander,
	CarielRoame, VeteranWarmedic, BattlefieldMedic, InvigoratingSermon, CannonmasterSmythe, NorthwatchSoldier, DesperatePrayer,
	CondemnRank3, CondemnRank2, CondemnRank1, SerenaBloodfeather, SoothsayersCaravan, DevouringPlague, VoidFlayer,
	Xyrella, PriestofAnshe, LightshowerElemental, PowerWordFortitude, ParalyticPoison, Yoink, EfficientOctobot, SilverleafPoison,
	WickedStabRank3, WickedStabRank2, WickedStabRank1, FieldContact, SwinetuskShank, ApothecaryHelbrim, OilRigAmbusher,
	ScabbsCutterbutter, SpawnpoolForager, DiremuckTinyfin, ChainLightningRank3, ChainLightningRank2, ChainLightningRank1,
	FiremancerFlurgl, SouthCoastChieftain, TinyfinsCaravan, AridStormer, NofinCanStopUs, Brukan, EarthRevenant, LilypadLurker,
	AltarofFire, GrimoireofSacrifice, ApothecarysCaravan, ImpSwarmRank3, ImpSwarmRank2, ImpSwarmRank1, ImpFamiliar,
	BloodShardBristleback, KabalOutfitter, TamsinRoame, SoulRend, NeeruFireblade, BurningBladePortal, BarrensScavenger,
	WarsongEnvoy, BulkUp, ConditioningRank3, ConditioningRank2, ConditioningRank1, Rokara, OutridersAxe, Rancor, WhirlingCombatant,
	MorshanElite, StonemaulAnchorman, OverlordSaurfang, DeadlyAdventurer, BurlyAdventurer, DevoutAdventurer, RelentlessAdventurer,
	ArcaneAdventurer, SneakyAdventurer, VitalAdventurer, SwiftAdventurer, MeetingStone, DevouringEctoplasm, ArchdruidNaralex,
	MutanustheDevourer, SelflessSidekick, SigilofSummoning, WailingDemon, Felrattler, TaintheartTormenter, FangboundDruid,
	LadyAnacondra, DeviateDreadfang, DeviateViper, Serpentbloom, SindoreiScentfinder, VenomstrikeBow, FrostweaveDungeoneer,
	ShatteringBlast, Floecaster, JudgmentofJustice, SeedcloudBuckler, PartyUp, ClericofAnshe, DevoutDungeoneer, AgainstAllOdds,
	SavoryDeviateDelight, WaterMoccasin, ShroudofConcealment, PerpetualFlame, WailingVapor, PrimalDungeoneer, FinalGasp,
	UnstableShadowBlast, StealerofSouls, ManatArms, WhetstoneHatchet, KreshLordofTurtling, TurtleSpike, 
]

for class_ in AllClasses_Barrens:
	if issubclass(class_, Card):
		class_.index = "THE_BARRENS" + ("~" if class_.index else '') + class_.index