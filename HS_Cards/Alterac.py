from Parts.CardTypes import *
from Parts.TrigsAuras import *
from HS_Cards.DemonHunterInitiate import Felwing
from HS_Cards.AcrossPacks import Huffer, Leokk, Misha, SteadyShot
from HS_Cards.Core import ExplosiveTrap, FreezingTrap, SnakeTrap
from HS_Cards.Outlands import PackTactics
from HS_Cards.Darkmoon import OpentheCages
from HS_Cards.Barrens import Spell_Sigil


class Death_Popsicooler(Deathrattle):
	description = "Deathrattle: Freeze two random enemy minions"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		if minions := (kpr := self.keeper).Game.minionsonBoard(3-kpr.ID):
			kpr.freeze(numpyChoice(minions, 2, replace=False))
		
	
class Death_DireFrostwolf(Deathrattle):
	description = "Deathrattle: Summon a 2/2 Wolf with Stealth"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).summon(FrostwolfCub(kpr.Game, kpr.ID))
		
	
class Death_PiggybackImp(Deathrattle):
	description = "Deathrattle: Summon a 4/1 Imp"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).summon(BackpiggyImp(kpr.Game, kpr.ID))
		
	
class Death_KorraktheBloodrager(Deathrattle):
	description = "Deathrattle: If this wasn't Honorably Killed, resummon Korrak the Bloodrage"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		if (kpr := self.keeper).health: kpr.summon(KorraktheBloodrager(kpr.Game, kpr.ID))
		
	
class Death_Legionnaire(Deathrattle):
	description = "Deathrattle: Give all minions in your hand +2/+2"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).giveEnchant([card for card in kpr.Game.Hand_Deck.hands[kpr.ID] if card.category == "Minion"],
								2, 2, source=Legionnaire, add2EventinGUI=False)
		
	
class Death_HumongousOwl(Deathrattle):
	description = "Deathrattle: Deal 8 damage to a random enemy"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		if objs := (kpr := self.keeper).Game.charsAlive(3-kpr.ID): kpr.dealsDamage(numpyChoice(objs), 8)
		
	
class Death_StormpikeBattleRam(Deathrattle):
	description = "Deathrattle: Your next Beast costs (2) less"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		GameManaAura_StormpikeBattleRam(self.keeper.Game, self.keeper.ID).auraAppears()
		
	
class Death_MountainBear(Deathrattle):
	description = "Deathrattle: Summon two 2/4 Cubs with Taunt"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		game, ID = (kpr := self.keeper).Game, kpr.ID
		kpr.summon([MountainCub(game, ID) for _ in (0, 1)], relative="<>")
		
	
class Death_CavalryHorn(Deathrattle):
	description = "Deathrattle: Summon the lowest Cost minion in your hand"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		keeper = self.keeper
		if keeper.Game.space(keeper.ID) > 0 and \
				(indices := pickInds_LowestAttr(keeper.Game.Hand_Deck.decks[keeper.ID], cond=lambda card: card.category == "Minion")):
			keeper.Game.summonfrom(numpyChoice(indices), keeper.ID, position=-1, summoner=keeper, hand_deck=0)
		
	
class Death_NajakHexxen(Deathrattle):
	description = "Deathrattle: Give the minion back"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		#Assume only onBoard minion will be returned
		if self.memory:
			for minion, prevOwnID, enterBoardTurn in self.memory:
				if minion.onBoard and minion.ID != prevOwnID and minion.enterBoardTurn == enterBoardTurn:
					self.keeper.Game.minionSwitchSide(minion)
		
	def assistCreateCopy(self, Copy):
		if self.memory: Copy.memory = [(minion.createCopy(Copy.Game), prevOwnID, turnID) for minion, prevOwnID, turnID in self.memory]
		
	
class Death_SpiritGuide(Deathrattle):
	description = "Deathrattle: Draw a Holy spell and a Shadow spell"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.drawCertainCard(cond=lambda card: card.school == "Holy")
		self.keeper.drawCertainCard(cond=lambda card: card.school == "Shadow")
		
	
class Death_UndyingDisciple(Deathrattle):
	description = "Deathrattle: Deal damage equal to this minion's Attack to all enemy minions"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		if (atk := (kpr := self.keeper).attack) > 0:
			kpr.dealsDamage(kpr.Game.minionsonBoard(3-kpr.ID), atk)
		
	
class HonorableKill(TrigBoard):
	signals = ("MinionTakesDmg",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		#伤害被转移到钳嘴龟盾卫而导致刚好杀死盾卫时也可以触发荣誉击杀。所以只与受到伤害的随从受到的扳机有关
		return subject is self.keeper and subject.onBoard and subject.ID == subject.Game.turn and not target.health
		
	
class Trig_GnomePrivate(HonorableKill):
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).giveEnchant(kpr, 2, 0, source=GnomePrivate)
		
	
class Trig_IrondeepTrogg(TrigBoard):
	signals = ("CardBeenPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return comment == "Spell" and ID != kpr.ID and kpr.canBattle()
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).summon(kpr.copyCard(kpr, kpr.ID))
		
	
class Trig_Gankster(TrigBoard):
	signals = ("CardBeenPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.Game.cardinPlay.category == "Minion" and ID != kpr.ID and kpr.canBattle() and kpr.canBattle()
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).Game.battle(kpr, kpr.Game.cardinPlay)
		
	
class Trig_Corporal(HonorableKill):
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		print("Triggering Coporal's Honorable Kill")
		kpr.giveEnchant(kpr.Game.minionsonBoard(kpr.ID, exclude=kpr),
								effGain="Divine Shield", source=Corporal)
		
	
class Trig_SneakyScout(HonorableKill):
	def effect(self, signal, ID, subject, target, num, comment, choice):
		GameManaAura_SneakyScout((kpr := self.keeper).Game, kpr.ID).auraAppears()
		
	
class Trig_StormpikeQuartermaster(TrigBoard):
	signals = ("CardBeenPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return comment == "Spell" and ID == kpr.ID and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		if minions := [card for card in kpr.Game.Hand_Deck.hands[kpr.ID] if card.category == "Minion"]:
			self.keeper.giveEnchant(numpyChoice(minions), 1, 1, source=StormpikeQuartermaster, add2EventinGUI=False)
		
	
class Trig_DirewolfCommander(HonorableKill):
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).summon(FrostwolfCub(kpr.Game, kpr.ID))
		
	
class Trig_FrostwolfWarmaster(TrigHand):
	signals = ("CardBeenPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.inHand and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).Game.Manas.calcMana_Single(kpr)
		
	
class Trig_FrozenMammoth(TrigBoard):
	signals = ("CardBeenPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID and kpr.Game.cardinPlay.school == "Fire"
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		#Assume even Frozen from external effects is also thawed.
		self.keeper.losesTrig(self)
		self.keeper.losesEffect("Frozen", 0)
		
	
class Trig_IceRevenant(TrigBoard):
	signals = ("CardBeenPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.Game.cardinPlay.school == "Frost" and kpr.onBoard and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).giveEnchant(kpr, statEnchant=Enchantment_Exclusive(IceRevenant, 2, 2))
		
	
class Trig_StormpikeMarshal(TrigHand):
	signals = ("HeroTookDmg",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.inHand and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).Game.Manas.calcMana_Single(kpr)
		
	
class Trig_BloodGuard(TrigBoard):
	signals = ("MinionTakesDmg",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and target is kpr
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).giveEnchant(kpr.Game.minionsonBoard(kpr.ID), statEnchant=Enchantment(BloodGuard, 1, 0))
		
	
class Trig_FranticHippogryph(HonorableKill):
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).giveEnchant(kpr, effGain="Windfury", source=FranticHippogryph)
		
	
class Trig_KnightCaptain(HonorableKill):
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).giveEnchant(kpr, 3, 3, source=KnightCaptain)
		
	
class Trig_AbominableLieutenant(TrigBoard):
	signals = ("TurnEnds",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		# Assume the minion eaten would be removed and won't trigger Deathrattle
		if minions := kpr.Game.minionsonBoard(3-kpr.ID):
			minion = numpyChoice(minions)
			att, health = max(0, minion.attack), max(0, minion.health)
			kpr.Game.banishMinion(kpr, minion)
			kpr.giveEnchant(kpr, statEnchant=Enchantment_Exclusive(AbominableLieutenant, att, health))
		
	
class Trig_TrollCenturion(HonorableKill):
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).dealsDamage(kpr.Game.heroes[3-kpr.ID], 8)
		
	
class Trig_LokholartheIceLord(TrigHand):
	signals = ("HeroStatCheck",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.inHand and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).Game.Manas.calcMana_Single(kpr)
		
	
class Trig_DreadprisonGlaive(HonorableKill):
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		if (attack := kpr.Game.heroes[kpr.ID].attack) > 0:
			kpr.dealsDamage(kpr.Game.heroes[3-kpr.ID], attack)
		
	
class Trig_BattlewornVanguard(TrigBoard):
	signals = ("HeroAttackedMinion", "HeroAttackedHero",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and subject is kpr.Game.heroes[kpr.ID]
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		game, ID = (kpr := self.keeper).Game, kpr.ID
		kpr.summon([Felwing(game, ID) for _ in (0, 1)], relative="<>")
		
	
class Trig_FlagRunner(TrigBoard):
	signals = ("ObjDies",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and target.ID == kpr.ID and target.category == "Minion"
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).giveEnchant(kpr, statEnchant=Enchantment_Exclusive(FlagRunner, 1, 0))
		
	
class Trig_AshfallensFury(TrigBoard):
	signals = ("MinionAttackedMinion", "MinionAttackedHero",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		kpr.Game.powers[kpr.ID].usageCount = 0
		kpr.Game.powers[kpr.ID].btn.checkHpr()
		
	
class Trig_UrzulGiant(TrigHand):
	signals = ("ObjDied",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return target.category == "Minion" and kpr.inHand and target.ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).Game.Manas.calcMana_Single(kpr)
		
	
class Trig_WingCommanderMulverick(TrigBoard):
	signals = ("MinionTakesDmg",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return subject.ID == kpr.ID == subject.Game.turn and subject.onBoard and kpr.onBoard and not target.health
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		subject.summon(StrikeWyvern(subject.Game, subject.ID))
		
	
class Trig_FrostsaberMatriarch(TrigHand):
	signals = ("ObjBeenSummoned",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return "Beast" in subject.race and ID == kpr.ID and kpr.inHand
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).Game.Manas.calcMana_Single(kpr)
		
	
class Trig_Bloodseeker(HonorableKill):
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).giveEnchant(kpr, 1, 1, source=Bloodseeker)
		
	
class Trig_IceTrap(Trig_Secret):
	signals = ("SpellOK2Play?",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return ID != self.keeper.ID and subject[0] > -1
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		spell, num = kpr.Game.cardinPlay, type(kpr).num
		if subject[0] > -1:
			kpr.Game.add2EventinGUI(kpr, spell, textTarget="X", colorTarget=red)
			subject[0] = -1
			spell.manaMods.append(ManaMod(spell, by=+num))
			self.keeper.Game.Hand_Deck.addCardtoHand(spell, spell.ID)
		else: ManaMod(spell, by=+num).applies() #一定是第二次触发，直接把其在手中的费用+1
		
	
class Trig_TheImmovableObject(TrigBoard):
	signals = ("FinalDmgonHero?",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and target.ID == kpr.ID and num[0] > 1
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		num[0] = math.ceil(num[0] / 2)
		
	
class Trig_Brasswing(TrigBoard):
	signals = ("MinionTakesDmg", "TurnEnds")
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		if signal[0] == "T": return ID == kpr.ID and kpr.onBoard
		else: return subject is kpr and kpr.onBoard and kpr.ID == kpr.Game.turn and not target.health
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		if signal[0] == "M": kpr.heals(kpr.Game.heroes[kpr.ID], kpr.calcHeal(4))
		else: kpr.dealsDamage(kpr.Game.minionsonBoard(3-kpr.ID), 2)
		
	
class Trig_TemplarCaptain(TrigBoard):
	signals = ("MinionAttackedMinion",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return subject is kpr and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).summon(StormpikeDefender(kpr.Game, kpr.ID))
		
	
class Trig_LuminousGeode(TrigBoard):
	signals = ("MinionGotHealed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return target.ID == kpr.ID and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.giveEnchant(target, statEnchant=Enchantment_Exclusive(LuminousGeode, 2, 0))
		
	
class Trig_HolyTouch(TrigBoard):
	signals = ("TurnEnds",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return ID == kpr.ID and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		VoidSpike((kpr := self.keeper).Game, kpr.ID).replacePower()
		
	
class Trig_VoidSpike(TrigBoard):
	signals = ("TurnEnds",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return ID == kpr.ID and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		HolyTouch((kpr := self.keeper).Game, kpr.ID).replacePower()
		
	
class Trig_ForsakenLieutenant(TrigBoard):
	signals = ("CardBeenPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return ID == kpr.ID and kpr.onBoard and kpr.Game.cardinPlay.category == "Minion"
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		Copy = kpr.copyCard(kpr.Game.cardinPlay, kpr.ID, 2, 2)
		self.keeper.giveEnchant(Copy, effGain="Rush", source=ForsakenLieutenant)
		kpr.transform(kpr, Copy)
		
	
class Trig_TheLobotomizer(HonorableKill):
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		if deck := kpr.Game.Hand_Deck.decks[3-kpr.ID]:
			kpr.addCardtoHand(kpr.copyCard(deck[-1], kpr.ID), kpr.ID)
		
	
class Trig_WildpawGnoll(TrigHand):
	signals = ("HandCheck", "HeroAppears",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return ID == kpr.ID and kpr.inHand and (signal == "HeroAppears" or comment.startswith("Enter"))
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).Game.Manas.calcMana_Single(kpr)
		
	
class Trig_CheatySnobold(TrigBoard):
	signals = ("CharFrozen",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return ID != kpr.ID and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.dealsDamage(target, 3)
		
	
class Trig_EarthInvocation(TrigBoard):
	signals = ("TurnEnds",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return ID == kpr.ID and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		powerType = type(self.keeper)
		newPower = numpyChoice([power for power in ElementalMastery.invocations if power is not powerType])
		newPower(kpr.Game, kpr.ID).replacePower()
		
	
class Trig_HollowAbomination(HonorableKill):
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).giveEnchant(kpr, statEnchant=Enchantment_Exclusive(HollowAbomination, max(0, target.attack), 0))
		
	
class Trig_GloryChaser(TrigBoard):
	signals = ("CardBeenPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return comment == "Minion" and ID == kpr.ID and kpr.onBoard and kpr.Game.cardinPlay.effects["Taunt"] > 0
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).Game.Hand_Deck.drawCard(kpr.ID)
		
	
class Trig_AxeBerserker(HonorableKill):
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.drawCertainCard(cond=lambda card: card.category == "Weapon")
		
	
class Trig_TheUnstoppableForce(TrigBoard):
	signals = ("HeroAttackedMinion",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID and target.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).Game.battle(target, kpr.Game.heroes[3-kpr.ID], evenifDead=True)
		
	
class Trig_ShieldShatter(TrigHand):
	signals = ("ArmorGained", "ArmorLost")
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return ID == kpr.ID and kpr.inHand
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).Game.Manas.calcMana_Single(kpr)
		
	
class GameManaAura_SneakyScout(GameManaAura_OneTime):
	to, temporary, targets = 0, False, "Power"
	def applicable(self, target): return target.ID == self.ID and target.category == "Power"
		
	
class GameAura_FieldofStrife(GameAura_AlwaysOn):
	attGain, counter = 1, 3
	def applies(self, target):
		Aura_Receiver(target, self, attGain=1).effectStart()
		
	def auraAppears(self):
		add2ListinDict(self, self.Game.trigsBoard[self.ID], "MinionAppears")
		self.Game.turnEndTrigger.append(self)
		for minion in self.Game.minionsonBoard(self.ID):
			self.applies(minion)
		if self.Game.GUI: self.Game.GUI.heroZones[self.ID].addaTrig(self.card, text=str(self.counter))
		
	def auraDisappears(self):
		for receiver in self.receivers[:]: receiver.effectClear()
		self.receivers = []
		removefrom(self, self.Game.trigsBoard[self.ID]["MinionAppears"])
		removefrom(self, self.Game.turnEndTrigger)
		if self.Game.GUI: self.Game.GUI.heroZones[self.ID].removeaTrig(self.card)
		
	def trig_TurnTrig(self):
		if self.Game.turn == self.ID: #Only counts down at then end of your own turn
			self.counter -= 1
			if self.card.btn: self.card.btn.trigAni(self.counter)
			if self.counter < 1:
				if self.Game.GUI: self.Game.GUI.showOffBoardTrig(self.card, animationType="Appear")
				self.auraDisappears()
		
	
class FlankingManeuver_Effect(TrigEffect):
	signals, trigType = ("ObjDied",), "Conn&TurnEnd"
	def __init__(self, Game, ID, memory=None):
		super().__init__(Game, ID)
		self.memory = memory
		
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return target is self.memory
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.card.summon(SnowySatyr(self.Game, self.ID))
		self.disconnect()
		
	def trig_TurnTrig(self):
		self.disconnect()
		
	
class SigilofReckoning_Effect(TrigEffect):
	trigType = "TurnStart&OnlyKeepOne"
	def trigEffect(self):
		self.card.try_SummonfromOwn(hand_deck=0, cond=lambda card: "Demon" in card.race)
		
	
class GameManaAura_PrideSeeker(GameManaAura_OneTime):
	by, temporary = -2, False
	def applicable(self, target): return target.ID == self.ID and target.options
		
	
class FrostwolfKennels_Effect(TrigEffect):
	signals, counter, trigType = ("TurnEnds",), 3, "Conn&TrigAura"
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return ID == self.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.card.summon(FrostwolfCub(self.Game, self.ID))
		self.counter -= 1
		if self.card.btn: self.card.btn.trigAni(self.counter)
		if self.counter < 1:
			if self.Game.GUI: self.Game.GUI.showOffBoardTrig(self.card, animationType="Appear")
			self.disconnect()
		
	
class DunBaldarBunker_Effect(TrigEffect):
	signals, counter, trigType = ("TurnEnds",), 3, "Conn&TrigAura"
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return ID == self.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		if indices := [i for i, card in enumerate(self.Game.Hand_Deck.decks[self.ID]) if card.race == "Secret"]:
			card, mana, entersHand = self.Game.Hand_Deck.drawCard(self.ID, numpyChoice(indices))
			if entersHand: ManaMod(card, to=1).applies()
		self.counter -= 1
		if self.card.btn: self.card.btn.trigAni(self.counter)
		if self.counter < 1:
			if self.Game.GUI: self.Game.GUI.showOffBoardTrig(self.card, animationType="Appear")
			self.disconnect()
		
	
class GameManaAura_StormpikeBattleRam(GameManaAura_OneTime):
	by, temporary = -2, False
	def applicable(self, target): return target.ID == self.ID and "Beast" in target.race
		
	
class WingCommanderIchman_Effect(TrigEffect):
	signals, trigType = ("MinionTakesDmg", "Kills"), "Conn&TurnEnd"
	def __init__(self, Game, ID, memory=None):
		super().__init__(Game, ID)
		self.memory = memory
		
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return subject.ID == self.ID and subject is self.memory and (signal[0] == "K" or target.health < 1 or target.dead)
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		if minion := self.card.try_SummonfromOwn(cond=lambda card: "Beast" in card.race):
			if self.Game.GUI: self.Game.GUI.showOffBoardTrig(self.card, animationType="Appear")
			self.card.giveEnchant(minion, effGain="Rush", source=WingCommanderIchman)
			self.memory = minion
		else: self.disconnect()
		
	def trig_TurnTrig(self):
		self.disconnect()
		
	
class GameManaAura_AmplifiedSnowflurry(GameManaAura_OneTime):
	signals, to, temporary, targets = ("PowerAppears", "HeroUsedAbility"), 0, False, "Power"
	def applicable(self, target): return target.ID == self.ID and target.category == "Power"
		
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return self.applicable(subject if signal[0] == "H" else target)
		
	def trig(self, signal, ID, subject, target, num, comment, choice):
		if signal[0] == "H": self.auraDisappears() #玩家手动使用一次技能后该光环才消失，因为需要保证技能可以吃到冻结目标的效果
		elif self.applicable(target): self.applies(target)
		
	def auraAppears(self):
		super().auraAppears()
		self.Game.rules[self.ID]["Power Freezes Target"] += 1
		
	def auraDisappears(self):
		super().auraDisappears()
		self.Game.rules[self.ID]["Power Freezes Target"] -= 1
		
	
class IcebloodTower_Effect(TrigEffect):
	signals, counter, trigType = ("TurnEnds",), 3, "Conn&TrigAura"
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return ID == self.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		if indices := [i for i, card in enumerate(self.Game.Hand_Deck.decks[self.ID])
					   if card.category == "Spell" and card.name != "Iceblood Tower"]:
			self.Game.Hand_Deck.extractfromDeck(numpyChoice(indices), self.ID).cast()
		self.counter -= 1
		if self.card.btn: self.card.btn.trigAni(self.counter)
		if self.counter < 1:
			if self.Game.GUI: self.Game.GUI.showOffBoardTrig(self.card, animationType="Appear")
			self.disconnect()
		
	
class DunBaldarBridge_Effect(TrigEffect):
	signals, counter, trigtype = ("ObjBeenSummoned",), 3, "Conn&TurnEnd"
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return subject.category == "Minion" and ID == self.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.card.giveEnchant(subject, 2, 2, source=DunBaldarBridge)
		
	def trig_TurnTrig(self):
		if self.Game.turn == self.ID: #Only counts down at then end of your own turn
			self.counter -= 1
			if self.card.btn: self.card.btn.trigAni(self.counter)
			if self.counter < 1:
				if self.Game.GUI: self.Game.GUI.showOffBoardTrig(self.card, animationType="Appear")
				self.disconnect()
		
	
class StormpikeAidStation_Effect(TrigEffect):
	signals, counter, trigType = ("TurnEnds",), 3, "Conn&TrigAura"
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return ID == self.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.card.giveEnchant(self.Game.minionsonBoard(self.ID), 0, 2, source=StormpikeAidStation)
		self.counter -= 1
		if self.card.btn: self.card.btn.trigAni(self.counter)
		if self.counter < 1:
			if self.Game.GUI: self.Game.GUI.showOffBoardTrig(self.card, animationType="Appear")
			self.disconnect()
		
	
class SnowfallGraveyard_Effect(TrigEffect):
	counter, trigType = 3, "TurnEnd"
	def connect(self):
		super().connect()
		self.Game.rules[self.ID]["Minion Deathrattle x2"] += 1
		self.Game.rules[self.ID]["Weapon Deathrattle x2"] += 1
		
	def trig_TurnTrig(self):
		self.counter -= 1
		if self.card.btn: self.card.btn.trigAni(self.counter)
		if self.counter < 1:
			self.Game.rules[self.ID]["Minion Deathrattle x2"] -= 1
			self.Game.rules[self.ID]["Weapon Deathrattle x2"] -= 1
			if self.Game.GUI: self.Game.GUI.showOffBoardTrig(self.card, animationType="Appear")
			self.disconnect()
		
	
class GameManaAura_SleightofHand(GameManaAura_OneTime):
	by = -2
	def applicable(self, target): return target.ID == self.ID
		
	
class GameManaAura_Frostbite(GameManaAura_OneTime):
	by = +2
	def applicable(self, target): return target.ID == self.ID and target.category == "Spell"
		
	
class WildpawCavern_Effect(TrigEffect):
	signals, counter, trigType = ("TurnEnds",), 3, "Conn&TrigAura"
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return ID == self.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.card.summon(FrozenStagguard(self.Game, self.ID))
		self.counter -= 1
		if self.card.btn: self.card.btn.trigAni(self.counter)
		if self.counter < 1:
			if self.Game.GUI: self.Game.GUI.showOffBoardTrig(self.card, animationType="Appear")
			self.disconnect()
		
	
class DesecratedGraveyard_Effect(TrigEffect):
	signals, counter, trigType = ("TurnEnds",), 3, "Conn&TrigAura"
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return ID == self.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		if minions := pickObjs_LowestAttr(self.Game.minionsonBoard(self.ID), attr="attack"):
			self.card.killandSummon(numpyChoice(minions), DesecratedShade(self.Game, self.ID))
		self.counter -= 1
		if self.card.btn: self.card.btn.trigAni(self.counter)
		if self.counter < 1:
			if self.Game.GUI: self.Game.GUI.showOffBoardTrig(self.card, animationType="Appear")
			self.disconnect()
		
	
class FrozenBuckler_Effect(TrigEffect):
	counter, trigType = 5, "TurnStart&OnlyKeepOne"
	def trigEffect(self):
		self.Game.heroes[self.ID].losesArmor(self.counter)
		
	
class GameManaAura_TotheFront(GameManaAura_OneTime):
	signals, by, lowerBound = ("HandCheck",), -1, 1 #temporary is True and is removed at the end of the turn
	def applicable(self, target): return target.ID == self.ID and target.category == "Minion"
		
	
class IcebloodGarrison_Effect(TrigEffect):
	signals, counter, trigType = ("TurnEnds",), 3, "Conn&TrigAura"
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return ID == self.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.card.dealsDamage(self.Game.minionsonBoard(3-self.ID), self.card.calcDamage(1))
		self.counter -= 1
		if self.card.btn: self.card.btn.trigAni(self.counter)
		if self.counter < 1:
			if self.Game.GUI: self.Game.GUI.showOffBoardTrig(self.card, animationType="Appear")
			self.disconnect()
		
	
class GnomePrivate(Minion):
	Class, race, name = "Neutral", "", "Gnome Private"
	mana, attack, health = 1, 1, 3
	numTargets, Effects, description = 0, "", "Honorable Kill: Gain +2 Attack"
	name_CN = "侏儒列兵"
	trigBoard = Trig_GnomePrivate
	
	
class IrondeepTrogg(Minion):
	Class, race, name = "Neutral", "", "Irondeep Trogg"
	mana, attack, health = 1, 1, 2
	numTargets, Effects, description = 0, "", "After your opponent casts a spell, summon a copy of this"
	name_CN = "深铁穴居人"
	trigBoard = Trig_IrondeepTrogg
	
	
class IvustheForestLord(Minion):
	Class, race, name = "Neutral", "", "Ivus, the Forest Lord"
	mana, attack, health = 1, 1, 1
	numTargets, Effects, description = 0, "", "Battlecry: Spend the rest of your Mana and gain +2/+2, Rush, Divine Shield, or Taunt at random for each"
	name_CN = "森林之王伊弗斯"
	index = "Battlecry~Legendary"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if num := self.Game.Manas.spendAllMana(self.ID):
			gains = ['b', "Rush", "Divine Shield", "Taunt"]
			for _ in range(num):
				if (gain := gains.pop(numpyRandint(len(gains)))) == 'b':
					gains.insert(0, gain)
					self.giveEnchant(self, 2, 2, source=IvustheForestLord)
				else:
					self.giveEnchant(self, effGain=gain, source=IvustheForestLord)
		
	
class Gankster(Minion):
	Class, race, name = "Neutral", "", "Gankster"
	mana, attack, health = 2, 4, 2
	numTargets, Effects, description = 0, "Stealth", "Stealth. After your opponent plays a minion, attack it"
	name_CN = "伏兵"
	trigBoard = Trig_Gankster
	
	
class RamCommander(Minion):
	Class, race, name = "Neutral", "", "Ram Commander"
	mana, attack, health = 2, 2, 2
	numTargets, Effects, description = 0, "", "Battlecry: Add two 1/1 Rams with Rush to your hand"
	name_CN = "群羊指挥官"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.addCardtoHand([BattleRam]*2, self.ID)
		
	
class BattleRam(Minion):
	Class, race, name = "Neutral", "Beast", "Battle Ram"
	mana, attack, health = 1, 1, 1
	name_CN = "作战山羊"
	numTargets, Effects, description = 0, "Rush", "Rush"
	index = "Uncollectible"
	
	
class Corporal(Minion):
	Class, race, name = "Neutral", "", "Corporal"
	mana, attack, health = 2, 2, 3
	numTargets, Effects, description = 0, "", "Honorable Kill: Give your other minions Divine Shield"
	name_CN = "下士"
	trigBoard = Trig_Corporal
	
	
class SneakyScout(Minion):
	Class, race, name = "Neutral", "", "Sneaky Scout"
	mana, attack, health = 2, 3, 2
	numTargets, Effects, description = 0, "Stealth", "Stealth. Honorable Kill: Your next Hero Power costs (0)"
	name_CN = "潜匿斥候"
	trigBoard, trigEffect = Trig_SneakyScout, GameManaAura_SneakyScout
	
	
class StormpikeQuartermaster(Minion):
	Class, race, name = "Neutral", "", "Stormpike Quartermaster"
	mana, attack, health = 2, 2, 2
	numTargets, Effects, description = 0, "", "After you cast a spell, give a random minion in your hand +1/+1"
	name_CN = "雷矛军需官"
	trigBoard = Trig_StormpikeQuartermaster
	
	
class BunkerSergeant(Minion):
	Class, race, name = "Neutral", "", "Bunker Sergeant"
	mana, attack, health = 3, 2, 4
	numTargets, Effects, description = 0, "", "Battlecry: If your opponent has 2 or more minions, deal 1 damage to all enemy minions"
	name_CN = "碉堡中士"
	def effCanTrig(self):
		self.effectViable = len(self.Game.minionsonBoard(3-self.ID)) >= 2
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if len((objs := self.Game.minionsonBoard(3-self.ID))) >= 2:
			self.dealsDamage(objs, 1)
		
	
class DirewolfCommander(Minion):
	Class, race, name = "Neutral", "", "Direwolf Commander"
	mana, attack, health = 3, 2, 5
	numTargets, Effects, description = 0, "", "Honorable Kill: Summon a 2/2 Wolf with Stealth"
	name_CN = "恐狼指挥官"
	trigBoard = Trig_DirewolfCommander
	
	
class FrostwolfCub(Minion):
	Class, race, name = "Druid", "Beast", "Frostwolf Cub"
	mana, attack, health = 2, 2, 2
	name_CN = "霜狼宝宝"
	numTargets, Effects, description = 0, "Stealth", "Stealth"
	index = "Uncollectible"
	
	
class GrimtotemBountyHunter(Minion):
	Class, race, name = "Neutral", "", "Grimtotem Bounty Hunter"
	mana, attack, health = 3, 4, 2
	numTargets, Effects, description = 1, "", "Battlecry: Destroy an enemy Legendary minion"
	name_CN = "恐怖图腾赏金猎人"
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists(3 - self.ID)
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.ID != self.ID and "~Legendary" in obj.index and obj.onBoard
		
	def effCanTrig(self):
		self.effectViable = self.targetExists()
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.Game.kill(self, target)
		
	
class KoboldTaskmaster(Minion):
	Class, race, name = "Neutral", "", "Kobold Taskmaster"
	mana, attack, health = 3, 2, 4
	numTargets, Effects, description = 0, "", "Battlecry: Add 2 Armor Scraps to your hand that give +2 Health to a minion"
	name_CN = "狗头人监工"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.addCardtoHand([ArmorScrap]*2, self.ID)
		
	
class ArmorScrap(Spell):
	Class, school, name = "Neutral", "", "Armor Scrap"
	numTargets, mana, Effects = 1, 1, ""
	name_CN = "护甲碎片"
	description = "Give a minion +2 Health"
	index = "Uncollectible"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(target, 0, 2, source=ArmorScrap)
		
	
class PiggybackImp(Minion):
	Class, race, name = "Neutral", "Demon", "Piggyback Imp"
	mana, attack, health = 3, 4, 1
	numTargets, Effects, description = 0, "", "Deathrattle: Summon a 4/1 Imp"
	name_CN = "被背小鬼"
	deathrattle = Death_PiggybackImp
	
	
class BackpiggyImp(Minion):
	Class, race, name = "Neutral", "Demon", "Backpiggy Imp"
	mana, attack, health = 3, 4, 1
	name_CN = "背背小鬼"
	numTargets, Effects, description = 0, "", ""
	index = "Uncollectible"
	
	
class Popsicooler(Minion):
	Class, race, name = "Neutral", "Mech", "Popsicooler"
	mana, attack, health = 3, 3, 3
	numTargets, Effects, description = 0, "", "Deathrattle: Freeze two random enemy minions"
	name_CN = "冷饮制冰机"
	deathrattle = Death_Popsicooler
	
	
class ReflectoEngineer(Minion):
	Class, race, name = "Neutral", "", "Reflecto Engineer"
	mana, attack, health = 3, 2, 4
	numTargets, Effects, description = 0, "", "Battlecry: Swap the Attack and Health of all minions in both players' hands"
	name_CN = "反射工程师"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if cards := [card for card in self.Game.Hand_Deck.hands[1] if card.category == "Minion"]:
			self.setStat(cards, [(card.health, card.attack) for card in cards], source=ReflectoEngineer, add2EventinGUI=False)
		if cards := [card for card in self.Game.Hand_Deck.hands[2] if card.category == "Minion"]:
			self.setStat(cards, [(card.health, card.attack) for card in cards], source=ReflectoEngineer, add2EventinGUI=False)
		
	
class SnowblindHarpy(Minion):
	Class, race, name = "Neutral", "", "Snowblind Harpy"
	mana, attack, health = 3, 3, 4
	numTargets, Effects, description = 0, "", "Battlecry: If you're holding a Frost spell, gain 5 Armor"
	name_CN = "雪盲鹰身人"
	def effCanTrig(self):
		self.effectViable = any(card.school == "Frost" for card in self.Game.Hand_Deck.hands[self.ID])
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if any(card.school == "Frost" for card in self.Game.Hand_Deck.hands[self.ID]):
			self.giveHeroAttackArmor(self.ID, armor=5)
		
	
class DrekThar(Minion):
	Class, race, name = "Neutral", "", "Drek'Thar"
	mana, attack, health = 4, 4, 4
	name_CN = "德雷克萨尔"
	numTargets, Effects, description = 0, "", "Battlecry: If this costs more than every minion in your deck, summon 2 of them"
	index = "Battlecry~Legendary"
	def effCanTrig(self):
		mana, minions = self.mana, [card for card in self.Game.Hand_Deck.decks[self.ID] if card.category == "Minion"]
		self.effectViable = minions and all(mana > card.mana for card in minions)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		mana, minions = self.mana, [card for card in self.Game.Hand_Deck.decks[self.ID] if card.category == "Minion"]
		if minions and all(mana > card.mana for card in minions):
			if refMinion := self.try_SummonfromOwn():
				self.try_SummonfromOwn(position=refMinion.pos + 1)
		
	
class FrostwolfWarmaster(Minion):
	Class, race, name = "Neutral", "", "Frostwolf Warmaster"
	mana, attack, health = 4, 3, 3
	numTargets, Effects, description = 0, "", "Costs (1) less for each card you've played this turn"
	name_CN = "霜狼将领"
	trigHand = Trig_FrostwolfWarmaster
	def selfManaChange(self):
		self.mana -= self.Game.Counters.comboCounters[self.ID]
		
	
class FrozenMammoth(Minion):
	Class, race, name = "Neutral", "Beast", "Frozen Mammoth"
	mana, attack, health = 4, 6, 7
	numTargets, Effects, description = 0, "Frozen", "This is Frozen until you cast a Fire spell"
	name_CN = "冰封猛犸"
	trigBoard = Trig_FrozenMammoth
	def losesEffect(self, effect, amount=1, removeEnchant=False, loseAllEffects=False):
		if effect != "Frozen" or self.silenced or not any(isinstance(trig, Trig_FrozenMammoth) for trig in self.trigsBoard):
			super().losesEffect(effect, amount)
		
	
class HeraldofLokholar(Minion):
	Class, race, name = "Neutral", "", "Herald of Lokholar"
	mana, attack, health = 4, 3, 5
	numTargets, Effects, description = 0, "", "Battlecry: Draw a Frost spell"
	name_CN = "洛克霍拉的使者"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.drawCertainCard(cond=lambda card: card.school == "Frost")
		
	
class IceRevenant(Minion):
	Class, race, name = "Neutral", "Elemental", "Ice Revenant"
	mana, attack, health = 4, 4, 5
	numTargets, Effects, description = 0, "", "Whenever you cast a Frost spell, gain +2/+2"
	name_CN = "冰雪亡魂"
	trigBoard = Trig_IceRevenant
	
	
class KorraktheBloodrager(Minion):
	Class, race, name = "Neutral", "", "Korrak the Bloodrager"
	mana, attack, health = 4, 3, 5
	name_CN = "血怒者科尔拉克"
	numTargets, Effects, description = 0, "", "Deathrattle: If this wasn't Honorably Killed, resummon Korrak the Bloodrage"
	index = "Legendary"
	deathrattle = Death_KorraktheBloodrager
	
	
class StormpikeMarshal(Minion):
	Class, race, name = "Neutral", "", "Stormpike Marshal"
	mana, attack, health = 4, 2, 6
	numTargets, Effects, description = 0, "Taunt", "Taunt. If you took 5 or more damage on your opponent's turn, this costs (1)"
	name_CN = "雷矛元帅"
	trigHand = Trig_StormpikeMarshal
	def selfManaChange(self):
		turnInd = self.Game.pastTurnInd(3-self.ID) if self.ID == self.Game.turn else self.Game.turnInd
		if self.Game.Counters.examDmgonHero(self.ID, turnInd=turnInd, veri_sum=1) >= 5: self.mana = 1
		
	def effCanTrig(self):
		turnInd = self.Game.pastTurnInd(3 - self.ID) if self.ID == self.Game.turn else self.Game.turnInd
		self.effectViable = self.Game.Counters.examDmgonHero(self.ID, turnInd=turnInd, veri_sum=1) >= 5
		
	
class TowerSergeant(Minion):
	Class, race, name = "Neutral", "", "Tower Sergeant"
	mana, attack, health = 4, 4, 4
	numTargets, Effects, description = 0, "", "Battlecry: If you control at least 2 other minions, gain +2/+2"
	name_CN = "塔楼中士"
	def effCanTrig(self):
		self.effectViable = len(self.Game.minionsonBoard(self.ID)) > 1
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if len(self.Game.minionsonBoard(self.ID, exclude=self)) > 1:
			self.giveEnchant(self, 2, 2, source=TowerSergeant)
		
	
class VanndarStormpike(Minion):
	Class, race, name = "Neutral", "", "Vanndar Stormpike"
	mana, attack, health = 4, 4, 4
	name_CN = "范达尔·雷矛"
	numTargets, Effects, description = 0, "", "Battlecry: If this costs less than every minion in your deck, reduce their Cost by (3)"
	index = "Battlecry~Legendary"
	def effCanTrig(self):
		mana, minions = self.mana, [card for card in self.Game.Hand_Deck.decks[self.ID] if card.category == "Minion"]
		self.effectViable = minions and all(mana < card.mana for card in minions)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		mana, minions = self.mana, [card for card in self.Game.Hand_Deck.decks[self.ID] if card.category == "Minion"]
		if minions and all(mana < card.mana for card in minions):
			for card in minions: ManaMod(card, by=-3).applies()
		
	
class BloodGuard(Minion):
	Class, race, name = "Neutral", "", "Blood Guard"
	mana, attack, health = 5, 4, 7
	numTargets, Effects, description = 0, "", "Whenever this minion takes damage, give your minions +1 Attack"
	name_CN = "血卫士"
	trigBoard = Trig_BloodGuard
	
	
class FranticHippogryph(Minion):
	Class, race, name = "Neutral", "Beast", "Frantic Hippogryph"
	mana, attack, health = 5, 3, 7
	numTargets, Effects, description = 0, "Rush", "Rush. Honorable Kill: Gain Windfury"
	name_CN = "狂乱鹰角兽"
	trigBoard = Trig_FranticHippogryph
	
	
class KnightCaptain(Minion):
	Class, race, name = "Neutral", "", "Knight-Captain"
	mana, attack, health = 5, 3, 3
	numTargets, Effects, description = 1, "", "Battlecry: Deal 3 damage. Honorable Kill: Gain +3/+3"
	name_CN = "骑士队长"
	trigBoard = Trig_KnightCaptain
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(target, 3)
		
	
class SpammyArcanist(Minion):
	Class, race, name = "Neutral", "", "Spammy Arcanist"
	mana, attack, health = 5, 3, 4
	numTargets, Effects, description = 0, "", "Battlecry: Deal 1 damage to all other minions. If any die, repeat this"
	name_CN = "话痨奥术师"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for _ in range(14):
			if objs := self.Game.minionsonBoard(exclude=self):
				dmgTakers = self.dealsDamage(objs, 1)[0]
				anyKilled = any((obj.health < 1 or obj.dead) and obj.category == "Minion" for obj in dmgTakers)
				self.Game.gathertheDead()
				if not anyKilled: break
			else: break
		
	
class IcehoofProtector(Minion):
	Class, race, name = "Neutral", "", "Icehoof Protector"
	mana, attack, health = 6, 2, 10
	numTargets, Effects, description = 0, "Taunt", "Taunt. Freeze any character damaged by this minion"
	name_CN = "冰蹄护卫"
	trigBoard = Trig_FreezeDamaged
	
	
class Legionnaire(Minion):
	Class, race, name = "Neutral", "", "Legionnaire"
	mana, attack, health = 6, 9, 3
	numTargets, Effects, description = 0, "", "Deathrattle: Give all minions in your hand +2/+2"
	name_CN = "军团士兵"
	deathrattle = Death_Legionnaire
	
	
class HumongousOwl(Minion):
	Class, race, name = "Neutral", "Beast", "Humongous Owl"
	mana, attack, health = 7, 8, 4
	numTargets, Effects, description = 0, "", "Deathrattle: Deal 8 damage to a random enemy"
	name_CN = "巨型猫头鹰"
	deathrattle = Death_HumongousOwl
	
	
class AbominableLieutenant(Minion):
	Class, race, name = "Neutral", "", "Abominable Lieutenant"
	mana, attack, health = 8, 3, 5
	numTargets, Effects, description = 0, "", "At the end of your turn, eat a random enemy minion and gain its stats"
	name_CN = "憎恶军官"
	trigBoard = Trig_AbominableLieutenant
	
	
class TrollCenturion(Minion):
	Class, race, name = "Neutral", "", "Troll Centurion"
	mana, attack, health = 8, 8, 8
	numTargets, Effects, description = 0, "Rush", "Rush. Honorable Kill: Deal 8 damage to the enemy hero"
	name_CN = "巨魔百夫长"
	trigBoard = Trig_TrollCenturion
	
	
class LokholartheIceLord(Minion):
	Class, race, name = "Neutral", "Elemental", "Lokholar the Ice Lord"
	mana, attack, health = 10, 8, 8
	name_CN = "冰雪之王洛克霍拉"
	numTargets, Effects, description = 0, "Rush,Windfury", "Rush, Windfury. Costs (5) less if you have 15 Health or less"
	index = "Legendary"
	trigHand = Trig_LokholartheIceLord
	def selfManaChange(self):
		if self.Game.heroes[self.ID].health <= 15: self.mana -= 5
		
	
class DreadprisonGlaive(Weapon):
	Class, name, description = "Demon Hunter", "Dreadprison Glaive", "Honorable Kill: Deal damage equal to your hero's Attack to the enemy hero"
	mana, attack, durability, Effects = 1, 1, 3, ""
	name_CN = "恐惧牢笼战刃"
	trigBoard = Trig_DreadprisonGlaive
	
	
class BattlewornVanguard(Minion):
	Class, race, name = "Demon Hunter", "", "Battleworn Vanguard"
	mana, attack, health = 2, 2, 2
	numTargets, Effects, description = 0, "", "After your hero attacks, summon two 1/1 Felwings"
	name_CN = "历战先锋"
	trigBoard = Trig_BattlewornVanguard
	
	
class FieldofStrife(Spell):
	Class, school, name = "Demon Hunter", "", "Field of Strife"
	numTargets, mana, Effects = 0, 2, ""
	description = "Your minions have +1 Attack. Lasts 3 turns"
	name_CN = "征战平原"
	trigEffect = GameAura_FieldofStrife
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		GameAura_FieldofStrife(self.Game, self.ID).auraAppears()
		
	
class FlagRunner(Minion):
	Class, race, name = "Demon Hunter", "", "Flag Runner"
	mana, attack, health = 3, 1, 6
	numTargets, Effects, description = 0, "", "Whenever a friendly minion dies, gain +1 Attack"
	name_CN = "擎旗奔行者"
	trigBoard = Trig_FlagRunner
	
	
class FlankingManeuver(Spell):
	Class, school, name = "Demon Hunter", "", "Flanking Maneuver"
	numTargets, mana, Effects = 0, 4, ""
	description = "Summon a 4/2 Demon with Rush. If it dies this turn, summon another"
	name_CN = "侧翼合击"
	trigEffect = FlankingManeuver_Effect
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if minion := self.summon(SnowySatyr(self.Game, self.ID)):
			FlankingManeuver_Effect(self.Game, self.ID, minion).connect()
		
	
class SnowySatyr(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Snowy Satyr"
	mana, attack, health = 3, 4, 2
	name_CN = "落雪萨特"
	numTargets, Effects, description = 0, "Rush", "Rush"
	index = "Uncollectible"
	
	
class WardenofChains(Minion):
	Class, race, name = "Demon Hunter", "", "Warden of Chains"
	mana, attack, health = 4, 2, 6
	numTargets, Effects, description = 0, "Taunt", "Taunt. Battlecry: If you're holding a Demon that costs (5) or more, gain +1/+2"
	name_CN = "锁链守望者"
	def effCanTrig(self):
		self.effectViable = any("Demon" in card.race and card.mana >= 5 for card in self.Game.Hand_Deck.hands[self.ID])
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if any("Demon" in card.race and card.mana >= 5 for card in self.Game.Hand_Deck.hands[self.ID]):
			self.giveEnchant(self, 1, 2, source=WardenofChains)
		
	
class SigilofReckoning(Spell_Sigil):
	Class, school, name = "Demon Hunter", "Fel", "Sigil of Reckoning"
	numTargets, mana, Effects = 0, 5, ""
	description = "At the start of your next turn, summon a random Demon from your hand"
	name_CN = "清算咒符"
	trigEffect = SigilofReckoning_Effect
	
	
class CariaFelsoul(Minion):
	Class, race, name = "Demon Hunter", "", "Caria Felsoul"
	mana, attack, health = 6, 6, 6
	name_CN = "锁链守望者"
	numTargets, Effects, description = 0, "", "Battlecry: Transform into a copy of a Demon in your deck"
	index = "Battlecry~Legendary"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if not self.dead and self.Game.cardinPlay is self \
				and (demons := [card for card in self.Game.Hand_Deck.decks[self.ID] if "Demon" in card.race]):
			self.Game.transform(self, self.copyCard(numpyChoice(demons), self.ID, 6, 6))
		
	
class AshfallensFury(Power):
	mana, name, numTargets = 1, "Ashfallen‘s Fury", 0
	description = "+2 Attack this turn. After a friendly minion attacks, refresh this"
	name_CN = "陨烬之怒"
	trigBoard = Trig_AshfallensFury
	def effect(self, target=(), choice=0, comment=''):
		self.giveHeroAttackArmor(self.ID, statEnchant=Enchantment_Exclusive(AshfallensFury, 2, 0, until=0))
		
	
class KurtrusDemonRender(Hero):
	mana, description = 6, "Battlecry: Summon two 1/4 Demons with Rush. (Improved by your hero attacks this game)"
	Class, name, heroPower, armor = "Demon Hunter", "Kurtrus, Demon-Render", AshfallensFury, 5
	name_CN = "裂魔者库尔特鲁斯"
	index = "Battlecry~Legendary"
	def text(self): return self.Game.Counters.examHeroAtks(self.ID, veri_sum=1)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if numAtt := self.Game.Counters.examHeroAtks(self.ID, veri_sum=1):
			demon = type(FelbatShrieker.__name__ + '__%d'%numAtt, (FelbatShrieker,),
						{"index": FelbatShrieker.index+"~Uncollectible", "attack":1+numAtt, }
						)
		else: demon = FelbatShrieker
		self.summon([demon(self.Game, self.ID) for _ in (0, 1)])
		
	
class FelbatShrieker(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Felbat Shrieker"
	mana, attack, health = 3, 1, 4
	numTargets, Effects, description = 0, "Rush", "Rush"
	name_CN = "魔蝠尖啸者"
	index = "Uncollectible"
	
	
class UrzulGiant(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Ur'zul Giant"
	mana, attack, health = 13, 8, 8
	numTargets, Effects, description = 0, "", "Costs (1) less for each friendly minion that died this game"
	name_CN = "乌祖尔巨人"
	trigHand = Trig_UrzulGiant
	def selfManaChange(self):
		self.mana -= self.Game.Counters.examDeads(self.ID, veri_sum_ls=1)
		
	
class MoreResources(Spell):
	Class, school, name = "Druid", "", "More Resources"
	numTargets, mana, Effects = 0, 2, ""
	name_CN = "更多资源"
	description = "Draw your lowest Cost card"
	index = "Uncollectible"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if indices := pickInds_LowestAttr(self.Game.Hand_Deck.decks[self.ID]):
			self.Game.Hand_Deck.drawCard(self.ID, numpyChoice(indices))
		
	
class MoreSupplies(Spell):
	Class, school, name = "Druid", "", "More Supplies"
	numTargets, mana, Effects = 0, 2, ""
	name_CN = "更多补给"
	description = "Draw your highest Cost card"
	index = "Uncollectible"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if indices := pickInds_HighestAttr(self.Game.Hand_Deck.decks[self.ID]):
			self.Game.Hand_Deck.drawCard(self.ID, numpyChoice(indices))
		
	
class MoreResources_Option(Option):
	name, description = "More Resources", "Draw your lowest Cost card"
	mana, attack, health = 2, -1, -1
	spell = MoreResources
	
	
class MoreSupplies_Option(Option):
	name, description = "More Supplies", "Draw your highest Cost card"
	mana, attack, health = 2, -1, -1
	spell = MoreSupplies
	
	
class CaptureColdtoothMine(Spell):
	Class, school, name = "Druid", "", "Capture Coldtooth Mine"
	numTargets, mana, Effects = 0, 2, ""
	description = "Choose One - Draw your lowest Cost card; or Draw your highest Cost card"
	name_CN = "占领冷齿矿洞"
	options = (MoreResources_Option, MoreSupplies_Option)
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if choice < 1:
			if indices := pickInds_LowestAttr(self.Game.Hand_Deck.decks[self.ID]):
				self.Game.Hand_Deck.drawCard(self.ID, numpyChoice(indices))
		if choice:
			if indices := pickInds_HighestAttr(self.Game.Hand_Deck.decks[self.ID]):
				self.Game.Hand_Deck.drawCard(self.ID, numpyChoice(indices))
		
	
class ClawfuryAdept(Minion):
	Class, race, name = "Druid", "Beast", "Clawfury Adept"
	mana, attack, health = 2, 2, 3
	numTargets, Effects, description = 0, "", "Battlecry: Give all other friendly characters +1 Attack this turn"
	name_CN = "怒爪精锐"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(self.Game.charsonBoard(exclude=self),
						 statEnchant=Enchantment(ClawfuryAdept, 1, 0, until=0))
		
	
class FrostwolfKennels(Spell):
	Class, school, name = "Druid", "", "Frostwolf Kennels"
	numTargets, mana, Effects = 0, 3, ""
	description = "At the end of your turn, summon a 2/2 Wolf with Stealth. Lasts 3 turns"
	name_CN = "霜狼巢屋"
	trigEffect = FrostwolfKennels_Effect
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		FrostwolfKennels_Effect(self.Game, self.ID).connect()
		
	
class HeartoftheWild(Spell):
	Class, school, name = "Druid", "", "Heart of the Wild"
	numTargets, mana, Effects = 1, 3, ""
	description = "Give a minion +2/+2, then give your Beasts +1/+1"
	name_CN = "野性之心"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(target, 2, 2, source=HeartoftheWild)
		self.giveEnchant(self.Game.minionsonBoard(self.ID, race="Beast"), 1, 1)
		
	
class Pathmaker(Minion):
	Class, race, name = "Druid", "", "Pathmaker"
	mana, attack, health = 3, 3, 4
	numTargets, Effects, description = 0, "", "Battlecry: Cast the other choice from the last Choose One spell you've cast"
	name_CN = "开路者"
	@classmethod
	def checkTup_1ChoiceSpell(cls, tup):
		return (card := tup[0]).category == "Spell" and len(card.options) == 2 and tup[4] > -1
		
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.examCardPlays(self.ID, cond=Pathmaker.checkTup_1ChoiceSpell)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if tup := next(self.Game.Counters.iter_CardPlays(self.ID, backwards=True, cond=Pathmaker.checkTup_1ChoiceSpell), None):
			tup[0].options[1-tup[4]].spell(self.Game, self.ID).cast()
		
	
class PrideSeeker(Minion):
	Class, race, name = "Druid", "", "Pride Seeker"
	mana, attack, health = 3, 2, 4
	numTargets, Effects, description = 0, "", "Battlecry: Your next Choose One card costs (2) less"
	name_CN = "傲狮猎手"
	trigEffect = GameManaAura_PrideSeeker
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		GameManaAura_PrideSeeker(self.Game, self.ID).auraAppears()
		
	
class DireFrostwolf(Minion):
	Class, race, name = "Druid", "Beast", "Dire Frostwolf"
	mana, attack, health = 4, 4, 4
	numTargets, Effects, description = 0, "Stealth", "Stealth. Deathrattle: Summon a 2/2 Wolf with Stealth"
	name_CN = "凶恶霜狼"
	deathrattle = Death_DireFrostwolf
	
	
class WingCommanderMulverick(Minion):
	Class, race, name = "Druid", "", "Wing Commander Mulverick"
	mana, attack, health = 4, 2, 5
	numTargets, Effects, description = 0, "Rush", "Rush. You minion have 'Honorable Kill: Summon a 2/2 Wyvern with Rush'"
	name_CN = "空军指挥官穆维里克"
	trigBoard = Trig_WingCommanderMulverick
	index = "Legendary"
	
	
class StrikeWyvern(Minion):
	Class, race, name = "Druid", "Beast", "Strike Wyvern"
	mana, attack, health = 2, 2, 2
	numTargets, Effects, description = 0, "Rush", "Rush"
	name_CN = "突击双足飞龙"
	index ="Uncollectible"
	
	
class IceBlossom_Option(Option):
	name, description = "Ice Blossom", "Gain a Mana Crystal"
	mana, attack, health = 2, -1, -1
	
	
class ValleyRoot_Option(Option):
	name, description = "Valley Root", "Draw a card"
	mana, attack, health = 2, -1, -1
	
	
class Nurture(Power):
	mana, name, numTargets = 2, "Nurture", 0
	description = "Choose One: Summon a 6/6 Infernal"
	name_CN = "培育"
	options = (IceBlossom_Option, ValleyRoot_Option)
	def effect(self, target=(), choice=0, comment=''):
		if choice < 1: self.Game.Manas.gainManaCrystal(1, self.ID)
		if choice: self.Game.Hand_Deck.drawCard(self.ID, initiator=self)
		
	
class WildheartGuff(Hero):
	mana, description = 5, "Battlecry: Set your maximum Mana to 20. Gain a Mana Crystal. Draw a card"
	Class, name, heroPower, armor = "Druid", "Wildheart Guff", Nurture, 5
	name_CN = "野性之心古夫"
	index = "Battlecry~Legendary"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.Game.Manas.manas_UpperLimit[self.ID] = 20
		self.Game.Manas.gainManaCrystal(1, self.ID)
		self.Game.Hand_Deck.drawCard(self.ID)
		
	
class FrostsaberMatriarch(Minion):
	Class, race, name = "Druid", "Beast", "Frostsaber Matriarch"
	mana, attack, health = 7, 4, 5
	numTargets, Effects, description = 0, "Taunt", "Taunt. Costs (1) less for each Beast you've summoned this game"
	name_CN = "霜刃豹头领"
	trigHand = Trig_FrostsaberMatriarch
	def selfManaChange(self):
		self.mana -= sum(tup[0] == "Summon" and "Beast" in tup[1].race and tup[2] == self.ID
						 for tup in self.Game.Counters.iter_TupsSoFar("events"))
		
	
class Bloodseeker(Weapon):
	Class, name, description = "Hunter", "Bloodseeker", "Honorable Kill: Gain +1/+1"
	mana, attack, durability, Effects = 2, 2, 2, ""
	name_CN = "觅血者"
	trigBoard = Trig_Bloodseeker
	
	
class DunBaldarBunker(Spell):
	Class, school, name = "Hunter", "", "Dun Baldar Bunker"
	numTargets, mana, Effects = 0, 2, ""
	description = "At the end of your turn, draw a Secret and set its Cost to (1). Lasts 3 turns"
	name_CN = "丹巴达尔碉堡"
	trigEffect = DunBaldarBunker_Effect
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		DunBaldarBunker_Effect(self.Game, self.ID).connect()
		
	
class IceTrap(Secret):
	Class, school, name = "Hunter", "Frost", "Ice Trap"
	numTargets, mana, Effects = 0, 2, ""
	description = "Secret: When you opponent casts a spell, return it to their hand instead. It costs (1) more"
	name_CN = "冰霜陷阱"
	trigBoard = Trig_IceTrap
	num = 1
	
	
class RamTamer(Minion):
	Class, race, name = "Hunter", "", "Ram Tamer"
	mana, attack, health = 3, 4, 3
	numTargets, Effects, description = 0, "", "Battlecry: If you control a Secret, gain +1/+1 and Stealth"
	name_CN = "驯羊师"
	def effCanTrig(self):
		self.effectViable = self.Game.Secrets.secrets[self.ID]
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.Game.Secrets.secrets[self.ID]:
			self.giveEnchant(self, 1, 1, effGain="Stealth", source=RamTamer)
		
	
class RevivePet(Spell):
	Class, school, name = "Hunter", "Nature", "Revive Pet"
	numTargets, mana, Effects = 0, 3, ""
	description = "Discover a friendly Beast that died this game. Summon it"
	name_CN = "复活宠物"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.Game.space(self.ID) > 0:
			func = lambda : self.Game.Counters.examDeads(self.ID, veri_sum_ls=2, cond=lambda card: "Beast" in card.race)
			card, _ = self.discoverfrom(comment, tupsFunc=func)
			if card: self.summon(card)
		
	
class SpringtheTrap(Spell):
	Class, school, name = "Hunter", "", "Spring the Trap"
	numTargets, mana, Effects = 1, 4, ""
	description = "Deal 3 damage to a minion and cast a Secret from your deck. Honorable Kill: Cast 2"
	name_CN = "布置陷阱"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def text(self): return self.calcDamage(3)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		dmgTakers = self.dealsDamage(target, self.calcDamage(3))[0]
		num = 2 if self.ID == self.Game.turn and any(o.category == "Minion" and not o.health for o in dmgTakers) else 1
		self.Game.Secrets.deploySecretsfromDeck(self.ID, self, num=num)
		
	
class StormpikeBattleRam(Minion):
	Class, race, name = "Hunter", "Beast", "Stormpike Battle Ram"
	mana, attack, health = 4, 4, 3
	numTargets, Effects, description = 0, "Rush", "Rush. Deathrattle: Your next Beast costs (2) less"
	name_CN = "雷矛军用山羊"
	deathrattle, trigEffect = Death_StormpikeBattleRam, GameManaAura_StormpikeBattleRam
	
	
class MountainBear(Minion):
	Class, race, name = "Hunter", "Beast", "Mountain Bear"
	mana, attack, health = 7, 5, 6
	numTargets, Effects, description = 0, "Taunt", "Taunt. Deathrattle: Summon two 2/4 Cubs with Taunt"
	name_CN = "山岭野熊"
	deathrattle = Death_MountainBear
	
	
class MountainCub(Minion):
	Class, race, name = "Hunter", "Beast", "Mountain Cub"
	mana, attack, health = 3, 2, 4
	numTargets, Effects, description = 0, "Taunt", "Taunt"
	name_CN = "山熊宝宝"
	index = "Uncollectible"
	
	
class ImprovedExplosiveTrap(ExplosiveTrap):
	name_CN = "强化爆炸陷阱"
	description = "Secret: When your hero is attacked, deal 3 damage to all enemies"
	index = "Legendary~Uncollectible"
	num = 3
	def text(self): return self.calcDamage(3)
		
	
class ImprovedFreezingTrap(FreezingTrap):
	name_CN = "强化冰冻陷阱"
	description = "Secret: When an enemy minion attacks, return it to its owner's hand. It costs (4) more."
	index = "Legendary~Uncollectible"
	num = 4
	
	
class Snake_Alterac(Minion):
	Class, race, name = "Hunter", "Beast", "Snake"
	mana, attack, health = 2, 2, 2
	numTargets, Effects, description = 0, "", ""
	name_CN = "蛇"
	index = "Uncollectible"
	
	
class ImprovedSnakeTrap(SnakeTrap):
	name_CN = "强化毒蛇陷阱"
	description = "Secret: When one of your minions is attacked, summon three 2/2 Snakes"
	index = "Legendary~Uncollectible"
	snake = Snake_Alterac
	
	
class ImprovedPackTactics(PackTactics):
	name_CN = "强化集群战术"
	description = "Secret: When a friendly minion is attacked, summon a 3/3 copy"
	index = "Legendary~Uncollectible"
	num = 2
	
	
class ImprovedOpentheCages(OpentheCages):
	name_CN = "强化打开兽笼"
	description = "Secret: When your turn starts, if you control two minions, summon two Animal Companions"
	index = "Legendary~Uncollectible"
	num = 2
	
	
class ImprovedIceTrap(IceTrap):
	name_CN = "强化冰霜陷阱"
	description = "Secret: When you opponent casts a spell, return it to their hand instead. It costs (2) more"
	index = "Legendary~Uncollectible"
	num = 2
	
	
class SummonPet(Power):
	mana, name, numTargets = 2, "Summon Pet", 0
	description = "Summon an Animal Companion"
	name_CN = "召唤宠物"
	def available(self):
		return not self.chancesUsedUp() and self.Game.space(self.ID) > 0
		
	def effect(self, target=(), choice=0, comment=''):
		self.summon(numpyChoice((Huffer, Leokk, Misha))(self.Game, self.ID))
		
	
class BeaststalkerTavish(Hero):
	mana, description = 6, "Battlecry: Discover and cast 2 Improved Secrets"
	Class, name, heroPower, armor = "Hunter", "Beaststalker Tavish", SummonPet, 5
	name_CN = "野兽追猎者塔维什"
	index = "Battlecry~Legendary"
	improvedSecrets = (ImprovedExplosiveTrap, ImprovedFreezingTrap, ImprovedSnakeTrap,
				  		ImprovedPackTactics, ImprovedOpentheCages, ImprovedIceTrap)
	def decidePool(self):
		return [secret for secret in BeaststalkerTavish.improvedSecrets if not self.Game.Secrets.sameSecretExists(secret, self.ID)]
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for _ in (0, 1):
			secret, _ = self.discoverNew(comment, lambda : BeaststalkerTavish.decidePool(self), add2Hand=False)
			secret.creator = type(self)
			secret.playedEffect()
		
	
class WingCommanderIchman(Minion):
	Class, race, name = "Hunter", "", "Wing Commander Ichman"
	mana, attack, health = 9, 5, 4
	name_CN = "空军指挥官艾克曼"
	numTargets, Effects, description = 0, "", "Battlecry: Summon a Beast from your deck and give it Rush. If it kills a minion this turn, repeat"
	index = "Battlecry~Legendary"
	trigEffect = WingCommanderIchman_Effect
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if minion := self.try_SummonfromOwn(cond=lambda card: "Beast" in card.race):
			self.giveEnchant(minion, effGain="Rush", source=WingCommanderIchman)
			WingCommanderIchman_Effect(self.Game, self.ID, minion).connect()
		
	
class ShiveringSorceress(Minion):
	Class, race, name = "Mage", "", "Shivering Sorceress"
	mana, attack, health = 1, 2, 2
	numTargets, Effects, description = 0, "", "Battlecry: Reduce the Cost of the highest Cost spell in your hand by (1)"
	name_CN = "战栗的女巫"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if cards := pickObjs_HighestAttr(self.Game.Hand_Deck.hands[self.ID], cond=lambda card: card.category == "Spell"):
			ManaMod(numpyChoice(cards), by=-1).applies()
		
	
class AmplifiedSnowflurry(Minion):
	Class, race, name = "Mage", "Elemental", "Amplified Snowflurry"
	mana, attack, health = 2, 2, 3
	numTargets, Effects, description = 0, "", "Battlecry: Your next Hero Power costs (0) and Freezes the target"
	name_CN = "风雪增幅体"
	trigEffect = GameManaAura_AmplifiedSnowflurry
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		GameManaAura_AmplifiedSnowflurry(self.Game, self.ID).auraAppears()
		
	
class SiphonMana(Spell):
	Class, school, name = "Mage", "Arcane", "Siphon Mana"
	numTargets, mana, Effects = 1, 2, ""
	description = "Deal 2 damage. Honorable Kill: Reduce the Cost of the spells in your hand by (1)"
	name_CN = "法力虹吸"
	def text(self): return self.calcDamage(2)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		dmgTakers = self.dealsDamage(target, self.calcDamage(2))[0]
		if self.ID == self.Game.turn:
			for o in dmgTakers:
				if o.category == "Minion" and not o.health:
					for card in self.Game.Hand_Deck.hands[self.ID]:
						if card.category == "Spell": ManaMod(card, by=-1).applies()
		
	
class BuildaSnowman(Spell):
	Class, school, name = "Mage", "Frost", "Build a Snowman"
	numTargets, mana, Effects = 0, 3, ""
	description = "Summon a 3/3 Snowman that Freezes. Add 'Build a Snowbrute' to your hand"
	name_CN = "堆塑雪人"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon(Snowman(self.Game, self.ID))
		self.addCardtoHand(BuildaSnowbrute, self.ID)
		
	
class BuildaSnowbrute(Spell):
	Class, school, name = "Mage", "Frost", "Build a Snowman"
	numTargets, mana, Effects = 0, 6, ""
	name_CN = "堆塑雪怪"
	description = "Summon a 6/6 Snowman that Freezes. Add 'Build a Snowgre' to your hand"
	index = "Uncollectible"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon(Snowbrute(self.Game, self.ID))
		self.addCardtoHand(BuildaSnowgre, self.ID)
		
	
class BuildaSnowgre(Spell):
	Class, school, name = "Mage", "Frost", "Build a Snowgre"
	numTargets, mana, Effects = 0, 9, ""
	name_CN = "堆塑巨怪"
	description = "Summon a 9/9 Snowman that Freezes"
	index = "Uncollectible"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon(Snowgre(self.Game, self.ID))
		
	
class Snowman(Minion):
	Class, race, name = "Mage", "Elemental", "Snowman"
	mana, attack, health = 3, 3, 3
	name_CN = "雪人"
	numTargets, Effects, description = 0, "", "Freeze any character damaged by this minion"
	index = "Uncollectible"
	trigBoard = Trig_FreezeDamaged
	
	
class Snowbrute(Minion):
	Class, race, name = "Mage", "Elemental", "Snowbrute"
	mana, attack, health = 6, 6, 6
	name_CN = "雪怪"
	numTargets, Effects, description = 0, "", "Freeze any character damaged by this minion"
	index = "Uncollectible"
	trigBoard = Trig_FreezeDamaged
	
	
class Snowgre(Minion):
	Class, race, name = "Mage", "Elemental", "Snowgre"
	mana, attack, health = 9, 9, 9
	name_CN = "冰雪巨怪"
	numTargets, Effects, description = 0, "", "Freeze any character damaged by this minion"
	index = "Uncollectible"
	trigBoard = Trig_FreezeDamaged
	
	
class ArcaneBrilliance(Spell):
	Class, school, name = "Mage", "Arcane", "Arcane Brilliance"
	numTargets, mana, Effects = 0, 4, ""
	description = "Add a copy of a 7, 8, 9, and 10-Cost spell in your deck to your hand"
	name_CN = "奥术光辉"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.Game.Hand_Deck.handNotFull(self.ID):
			copies, deck = [], self.Game.Hand_Deck.decks[self.ID]
			for cost in (7, 8, 9, 10):
				if cards := [card for card in deck if card.category == "Spell" and card.mana == cost]:
					copies.append(self.copyCard(numpyChoice(cards), self.ID))
			if copies: self.addCardtoHand(copies, self.ID)
		
	
class BalindaStonehearth(Minion):
	Class, race, name = "Mage", "", "Balinda Stonehearth"
	mana, attack, health = 6, 5, 5
	name_CN = "巴林达·斯通赫尔斯"
	numTargets, Effects, description = 0, "", "Battlecry: Draw 2 spells. Swap their Costs with this minion's stats"
	index = "Battlecry~Legendary"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		#Assume milled spells doesn't swap. If the minion is dead or inDeck, the original stats would be used
		spell1, mana1, entersHand = self.drawCertainCard(lambda card: card.category == "Spell")
		if entersHand:
			spell2, mana2, entersHand = self.drawCertainCard(lambda card: card.category == "Spell")
			if self.onBoard or self.inHand:
				att, health = max(0, self.attack), max(0, self.health) #Cannot be negative
				self.setStat(self, (mana1, mana2 if entersHand else None), source=BalindaStonehearth)
			else: att, health = self.attack_0, self.health_0
			ManaMod(spell1, to=att).applies()
			if entersHand: ManaMod(spell2, to=health).applies()
		
	
class MassPolymorph(Spell):
	Class, school, name = "Mage", "Arcane", "Mass Polymorph"
	numTargets, mana, Effects = 0, 7, ""
	description = "Transform all minions into 1/1 Sheep"
	name_CN = "群体变形"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.transform(minions := self.Game.minionsonBoard(), [Sheep_Alterac(self.Game, obj.ID) for obj in minions])
		
	
class Sheep_Alterac(Minion):
	Class, race, name = "Mage", "Beast", "Sheep"
	mana, attack, health = 1, 1, 1
	name_CN = "绵羊"
	numTargets, Effects, description = 0, "", ""
	index = "Uncollectible"
	
	
class ArcaneBurst(Power):
	mana, name, numTargets = 2, "Arcane Burst", 1
	description = "Deal 1 damage. Honorable Kill: Gain +2 damage"
	name_CN = "奥术爆裂"
	def dealsDmg(self): return True
		
	def text(self): return self.calcDamage(self.progress)
		
	def effect(self, target=(), choice=0, comment=''):
		damage, ownTurn = self.calcDamage(self.progress), self.ID == self.Game.turn
		for obj in target:
			dmgTakers = self.dealsDamage(target, damage)[0]
			if ownTurn and (n := sum(o.category == "Minion" and not o.health for o in dmgTakers)):
				self.giveEnchant(self, effGain="Damage Boost", effNum=2*n, source=ArcaneBurst)
		
	
class MagisterDawngrasp(Hero):
	mana, description = 8, "Battlecry: Recast a spell from each spell school you've cast this game"
	Class, name, heroPower, armor = "Mage", "Magister Dawngrasp", ArcaneBurst, 5
	name_CN = "魔导师晨拥"
	index = "Battlecry~Legendary"
	def text(self): return len(set(school for tup in self.Game.Counters.iter_CardPlaysSoFar(self.ID) if (school := tup[0].school)))
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		spells = {}
		for tup in self.Game.Counters.iter_CardPlaysSoFar(self.ID):
			if tup[0].school: add2ListinDict(tup[:2], spells, tup[0].school)
		for school, ls in spells.items(): #ls = [(Ignite, (2, 0, 0, 3, None)), (Shadow, (4, 0, 0, ElvenArcher, None))]
			self.Game.fabCard(numpyChoice(ls), self.ID, self).cast()
		
	
class IcebloodTower(Spell):
	Class, school, name = "Mage", "", "Iceblood Tower"
	numTargets, mana, Effects = 0, 10, ""
	description = "At the end of your turn, cast another spell from your deck. Lasts 3 turn"
	name_CN = "冰血哨塔"
	trigEffect = IcebloodTower_Effect
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		IcebloodTower_Effect(self.Game, self.ID).connect()
		
	
class VitalitySurge(Spell):
	Class, school, name = "Paladin", "Holy", "Vitality Surge"
	numTargets, mana, Effects = 0, 2, ""
	description = "Draw a minion. Restore Health to your hero equal to its Cost"
	name_CN = "活力涌现"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		card, mana, entersHand = self.drawCertainCard(cond=lambda card: card.category == "Minion")
		if card: self.heals(self.Game.heroes[self.ID], self.calcHeal(mana))
		
	
class HoldtheBridge(Spell):
	Class, school, name = "Paladin", "Holy", "Hold the Bridge"
	numTargets, mana, Effects = 1, 3, ""
	description = "Give a minion +2/+1 and Divine Shield. It gains Lifesteal until end of turn"
	name_CN = "坚守桥梁"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(target, 2, 1, multipleEffGains=(("", 1, Enchantment(HoldtheBridge, effGain="Divine Shield")),
											   			("", 1, Enchantment(HoldtheBridge, effGain="Lifesteal", until=0))),
						source=HoldtheBridge)
		
	
class SaidantheScarlet(Minion):
	Class, race, name = "Paladin", "", "Saidan the Scarlet"
	mana, attack, health = 3, 2, 2
	name_CN = "血色骑士赛丹"
	numTargets, Effects, description = 0, "Rush", "Rush. Whenever this minion gains Attack or Health, double that amount"
	index = "Legendary"
	def getsBuffDebuff(self, attackGain=0, healthGain=0, source=None, enchant=None, add2EventinGUI=True):
		super().getsBuffDebuff(attackGain, healthGain, source, enchant, add2EventinGUI)
		if not self.silenced and (attackGain > 0 or healthGain > 0):
			super().getsBuffDebuff(max(0, attackGain), max(0, healthGain), source, enchant, add2EventinGUI=False)
		
	def getsBuffDebuff_inDeck(self, attackGain, healthGain, source=None):
		super().getsBuffDebuff_inDeck(attackGain, healthGain, source)
		if not self.silenced and (attackGain > 0 or healthGain > 0):
			super().getsBuffDebuff_inDeck(attackGain, healthGain, source)
		
	
class StonehearthVindicator(Minion):
	Class, race, name = "Paladin", "", "Stonehearth Vindicator"
	mana, attack, health = 3, 3, 1
	numTargets, Effects, description = 0, "", "Battlecry: Draw a spell that costs (3) or less. It costs (0) this turn"
	name_CN = "石炉守备官"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		card, mana, entersHand = self.drawCertainCard(cond=lambda card: card.category == "Spell" and card.mana <= 3)
		if entersHand: ManaMod(card, to=0, until=0).applies()
		
	
class DunBaldarBridge(Spell):
	Class, school, name = "Paladin", "", "Dun Baldar Bridge"
	numTargets, mana, Effects = 0, 4, ""
	description = "After you summon a minion, give it +2/+2. Lasts 3 turns"
	name_CN = "丹巴达尔桥"
	trigEffect = DunBaldarBridge_Effect
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		DunBaldarBridge_Effect(self.Game, self.ID).connect()
		
	
class CavalryHorn(Weapon):
	Class, name, description = "Paladin", "Cavalry Horn", "Deathrattle: Summon the lowest Cost minion in your hand"
	mana, attack, durability, Effects = 5, 3, 2, ""
	name_CN = "骑兵号角"
	deathrattle = Death_CavalryHorn
	
	
class ProtecttheInnocent(Spell):
	Class, school, name = "Paladin", "", "Protect the Innocent"
	numTargets, mana, Effects = 0, 5, ""
	description = "Summon a 5/5 Defender with Taunt. If your hero was healed this turn"
	name_CN = "舍己为人"
	def effCanTrig(self):
		self.effectViable = any(tup[0] == "Heal" and tup[3] % 100 == 10 + self.ID for tup in self.Game.Counters.events[-1])
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon(StormpikeDefender(self.Game, self.ID))
		if any(tup[0] == "Heal" and tup[3] % 100 == 10 + self.ID for tup in self.Game.Counters.events[-1]):
			self.summon(StormpikeDefender(self.Game, self.ID))
		
	
class StormpikeDefender(Minion):
	Class, race, name = "Paladin", "", "Stormpike Defender"
	mana, attack, health = 5, 5, 5
	name_CN = "雷矛防御者"
	numTargets, Effects, description = 0, "Taunt", "Taunt"
	index = "Uncollectible"
	
	
class BlessingofQueens(Power):
	mana, name, numTargets = 2, "Blessing of Queens", 0
	description = "Give a random minion in your hand +4/+4"
	name_CN = "女王的祝福"
	def effect(self, target=(), choice=0, comment=''):
		if minions := [card for card in self.Game.Hand_Deck.hands[self.ID] if card.category == "Minion"]:
			self.giveEnchant(numpyChoice(minions), 4, 4, source=BlessingofQueens, add2EventinGUI=False)
		
	
class LightforgedCariel(Hero):
	mana, description = 7, "Battlecry: Deal 2 damage to all enemies. Equip a 2/5 Immovable Object"
	Class, name, heroPower, armor = "Paladin", "Lightforged Cariel", BlessingofQueens, 5
	name_CN = "光铸凯瑞尔"
	index = "Battlecry~Legendary"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(self.Game.charsonBoard(3-self.ID), 2)
		self.equipWeapon(TheImmovableObject(self.Game, self.ID))
		
	
class TheImmovableObject(Weapon):
	Class, name, description = "Paladin", "The Immovable Object", "This doesn't lose Durability. Your hero takes half damage, rounded up"
	mana, attack, durability, Effects = 7, 2, 5, "Immune"
	name_CN = "无法撼动之物"
	index = "Legendary~Uncollectible"
	trigBoard = Trig_TheImmovableObject
	def losesDurability(self): pass
		
	
class Brasswing(Minion):
	Class, race, name = "Paladin", "Dragon", "Brasswing"
	mana, attack, health = 8, 9, 7
	numTargets, Effects, description = 0, "", "At the end of your turn, deal 2 damage to all enemies. Honorable Kill: Restore 4 Health to your hero"
	name_CN = "亮铜之翼"
	trigBoard = Trig_Brasswing
	
	
class TemplarCaptain(Minion):
	Class, race, name = "Paladin", "", "Templar Captain"
	mana, attack, health = 8, 8, 8
	numTargets, Effects, description = 0, "Rush", "Rush. After this attacks a minion, summon a 5/5 Defender with Taunt"
	name_CN = "圣殿骑士队长"
	trigBoard = Trig_TemplarCaptain
	
	
class GiftoftheNaaru(Spell):
	Class, school, name = "Priest", "Holy", "Gift of the Naaru"
	numTargets, mana, Effects = 0, 1, ""
	description = "Restore 3 Health to all characters. If any are still damaged, draw a card"
	name_CN = "纳鲁的赐福"
	def text(self): return self.calcHeal(3)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.heals(objs := self.Game.charsonBoard(), self.calcHeal(3))
		if any(obj.dmgTaken > 0 for obj in objs): self.Game.Hand_Deck.drawCard(self.ID)
		
	
class ShadowWordDevour(Spell):
	Class, school, name = "Priest", "Shadow", "Shadow Word: Devour"
	numTargets, mana, Effects = 1, 1, ""
	description = "Choose a minion. It steals 1 Health from ALL other minions"
	name_CN = "暗言术：噬"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for obj in target:
			for minion in (others := self.Game.minionsonBoard(exclude=obj)):
				minion.enchantments.append(Enchantment(ShadowWordDevour, -1, -1))
				minion.calcStat()
			if num := len(others): self.giveEnchant(obj, num, num, source=ShadowWordDevour)
		
	
class Bless(Spell):
	Class, school, name = "Priest", "Holy", "Bless"
	numTargets, mana, Effects = 1, 2, ""
	description = "Give a minion +2 Health. Then set its Attack to be equal to its Health"
	name_CN = "祝福"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(target, 0, 2, source=Bless)
		self.setStat(target, [(None, obj.health) for obj in target], source=Bless)
		
	
class Deliverance(Spell):
	Class, school, name = "Priest", "Holy", "Deliverance"
	numTargets, mana, Effects = 1, 3, ""
	description = "Deal 3 damage to a minion. Honorable Kill: Summon a new 3/3 copy of it"
	name_CN = "超脱"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def text(self): return self.calcDamage(3)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		damage, ownTurn = self.calcDamage(3), self.ID == self.Game.turn
		for obj in target:
			dmgTakers = self.dealsDamage(obj, damage)[0]
			if ownTurn and (honorableKilled := [o for o in dmgTakers if o.category == "Minion" and not o.health]):
				self.summon([self.copyCard(o, self.ID, 3, 3, bareCopy=True) for o in honorableKilled])
		
	
class LuminousGeode(Minion):
	Class, race, name = "Priest", "Elemental", "Luminous Geode"
	mana, attack, health = 2, 1, 4
	numTargets, Effects, description = 0, "", "After a friendly minion is healed, give +2 Attack"
	name_CN = "光辉晶簇"
	trigBoard = Trig_LuminousGeode
	
	
class StormpikeAidStation(Spell):
	Class, school, name = "Priest", "", "Stormpike Aid Station"
	numTargets, mana, Effects = 0, 3, ""
	description = "At the end of your turn, give your minions +2 Health. Lasts 3 turns"
	name_CN = "雷矛求援站"
	trigEffect = StormpikeAidStation_Effect
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		StormpikeAidStation_Effect(self.Game, self.ID).connect()
		
	
class NajakHexxen(Minion):
	Class, race, name = "Priest", "", "Najak Hexxen"
	mana, attack, health = 4, 1, 4
	name_CN = "纳亚克·海克森"
	numTargets, Effects, description = 1, "", "Battlecry: Take control of an enemy minion. Deathrattle: Give the minion back"
	index = "Battlecry~Legendary"
	deathrattle = Death_NajakHexxen
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists(3 - self.ID)
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.ID != self.ID and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		oppoID, turnInd = 3-self.ID, self.Game.turnInd
		for obj in target:
			#Assume only take minion if its ID is different.
			if obj.ID == oppoID:
				self.Game.minionSwitchSide(obj)
				if obj.aliveonBoard() and (trig := next((trig for trig in self.deathrattles if isinstance(trig, Death_NajakHexxen)), None)):
					trig.memory.append((obj, oppoID, turnInd))
		
	
class SpiritGuide(Minion):
	Class, race, name = "Priest", "", "Spirit Guide"
	mana, attack, health = 5, 5, 5
	numTargets, Effects, description = 0, "Taunt", "Taunt. Deathrattle: Draw a Holy spell and a Shadow spell"
	name_CN = "灵魂向导"
	deathrattle = Death_SpiritGuide
	
	
class UndyingDisciple(Minion):
	Class, race, name = "Priest", "", "Undying Disciple"
	mana, attack, health = 6, 3, 7
	numTargets, Effects, description = 0, "Taunt", "Taunt. Deathrattle: Deal damage equal to this minion's Attack to all enemy minions"
	name_CN = "不死信徒"
	deathrattle = Death_UndyingDisciple
	
	
class HolyTouch(Power):
	mana, name, numTargets = 2, "Holy Touch", 1
	description = "Restores 5 Health. Flips each turn"
	name_CN = "神圣之触"
	trigBoard = Trig_HolyTouch
	def text(self): return self.calcHeal(5)
		
	def effect(self, target=(), choice=0, comment=''):
		self.heals(target, self.calcHeal(5))
		
	
class VoidSpike(Power):
	mana, name, numTargets = 2, "Void Spike", 1
	description = "Deals 5 damage. Flips each turn"
	name_CN = "虚空之刺"
	trigBoard = Trig_VoidSpike
	def dealsDmg(self): return True
		
	def text(self): return self.calcDamage(5)
		
	def effect(self, target=(), choice=0, comment=''):
		self.dealsDamage(target, self.calcDamage(5))
		
	
class XyrellatheDevout(Hero):
	mana, description = 8, "Battlecry: Trigger the Deathrattle of every friendly minion that died this game"
	Class, name, heroPower, armor = "Priest", "Xyrella, the Devout", HolyTouch, 5
	name_CN = "虔诚祭司泽瑞拉"
	index = "Battlecry~Legendary"
	def text(self): return self.Game.Counters.examDeads(self.ID, veri_sum_ls=1, cond=lambda card: card.deathrattle is not None)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		game, ID = self.Game, self.ID
		if tups := game.Counters.examDeads(self.ID, veri_sum_ls=2, cond=lambda card: card.deathrattle):
			numpyShuffle(tups)
			GUI, deads = self.Game.GUI, [game.fabCard(tup, ID, self) for tup in tups]
			for minion in deads:
				if GUI: GUI.showOffBoardTrig(minion)
				for trig in minion.deathrattles: trig.trig("TrigDeathrattle", self.ID, None, minion)
		
	
class ForsakenLieutenant(Minion):
	Class, race, name = "Rogue", "", "Forsaken Lieutenant"
	mana, attack, health = 2, 2, 2
	numTargets, Effects, description = 0, "Stealth", "Stealth. After you play a Deathrattle minion, become a 2/2 copy of it with Rush"
	name_CN = "被遗忘者军官"
	trigBoard = Trig_ForsakenLieutenant
	
	
class Reconnaissance(Spell):
	Class, school, name = "Rogue", "", "Reconnaissance"
	numTargets, mana, Effects = 0, 2, ""
	description = "Discover a Deathrattle minion from another class. It costs (2) less"
	name_CN = "侦察"
	poolIdentifier = "Class Deathrattle Minions"
	@classmethod
	def generatePool(cls, pools):
		return "Class Deathrattle Minions", [card for cards in pools.ClassCards.values() for card in cards
													if card.category == "Minion" and card.deathrattle]
		
	def decidePools(self):
		HeroClass = self.Game.heroes[self.ID].Class
		return [card for card in self.rngPool("Class Deathrattle Minions") if HeroClass not in card.Class]
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.Game.Hand_Deck.spaceinHand(self.ID) > 0:
			card = self.discoverNew_MultiPools(comment, lambda : Reconnaissance.decidePools(self))
			ManaMod(card, by=-2).applies()
		
	
class TheLobotomizer(Weapon):
	Class, name, description = "Rogue", "The Lobotomizer", "Honorable Kill: Get a copy of the top card in your opponent's deck"
	mana, attack, durability, Effects = 2, 2, 2, ""
	name_CN = "剥夺者"
	trigBoard = Trig_TheLobotomizer
	
	
class ColdtoothYeti(Minion):
	Class, race, name = "Rogue", "", "Coldtooth Yeti"
	mana, attack, health = 3, 1, 5
	numTargets, Effects, description = 0, "", "Combo: Gain +3 Attack"
	name_CN = "冷齿雪人"
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.comboCounters[self.ID] > 0
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.Game.Counters.comboCounters[self.ID] > 0:
			self.giveEnchant(self, 3, 0, source=ColdtoothYeti)
		
	
class DoubleAgent(Minion):
	Class, race, name = "Rogue", "", "Double Agent"
	mana, attack, health = 3, 3, 3
	numTargets, Effects, description = 0, "", "Battlecry: If you're holding a card from another class, summon a copy of this"
	name_CN = "双面间谍"
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.holdingCardfromAnotherClass(self.ID, exclude=self)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if not self.dead and self.Game.Hand_Deck.holdingCardfromAnotherClass(self.ID):
			self.summon(self.copyCard(self, self.ID))
		
	
class SnowfallGraveyard(Spell):
	Class, school, name = "Rogue", "", "Snowfall Graveyard"
	numTargets, mana, Effects = 0, 3, ""
	description = "Your Deathrattles trigger twice. Lasts 3 turns"
	name_CN = "雪落墓地"
	trigEffect = SnowfallGraveyard_Effect
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		SnowfallGraveyard_Effect(self.Game, self.ID).connect()
		
	
class CerathineFleetrunner(Minion):
	Class, race, name = "Rogue", "", "Cera'thine Fleetrunner"
	mana, attack, health = 5, 5, 5
	name_CN = "赛拉辛·疾行"
	numTargets, Effects, description = 0, "", "Battlecry: Replace your minions in hand and deck with ones from other classes. They cost (2) less"
	index = "Battlecry~Legendary"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		game = self.Game
		ownHand, ownDeck = game.Hand_Deck.hands[self.ID], game.Hand_Deck.decks[self.ID]
		if ownHand or ownDeck:
			HeroClass = game.heroes[self.ID].Class
			minions = [card for Class in self.rngPool("Classes") if Class != HeroClass for card in self.rngPool(Class)]
			inds_Hand = [i for i, card in enumerate(ownHand) if card.category == "Minion"]
			inds_Deck = [i for i, card in enumerate(ownDeck) if card.category == "Minion"]
			if ownHand:
				minions_Hand = [card(game, self.ID) for card in numpyChoice(minions, len(inds_Hand), replace=True)]
				game.Hand_Deck.replaceCardsinHand(self.ID, inds_Hand, minions_Hand)
			if ownDeck:
				Hand_Deck = [card(game, self.ID) for card in numpyChoice(minions, len(inds_Deck), replace=True)]
				game.Hand_Deck.replaceCardsinDeck(self.ID, inds_Hand, Hand_Deck)
		
	
class ContrabandStash(Spell):
	Class, school, name = "Rogue", "", "Contraband Stash"
	numTargets, mana, Effects = 0, 5, ""
	description = "Replay 5 cards from other classes you've played this game"
	name_CN = "珍藏私货"
	def text(self):
		HeroClass = self.Game.heroes[self.ID].Class
		return self.Game.Counters.examCardPlays(self.ID, veri_sum_ls=1, cond=lambda tup: HeroClass not in tup[0].Class)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		HeroClass = self.Game.heroes[self.ID].Class
		if tups := self.Game.Counters.examCardPlays(self.ID, veri_sum_ls=2, cond=lambda tup: HeroClass not in tup[0].Class):
			for tup in numpyChoice(tups, min(5, len(tups)), replace=False):
				self.replayCard_fromTup(tup)
		
	
class WildpawGnoll(Minion):
	Class, race, name = "Rogue", "", "Wildpaw Gnoll"
	mana, attack, health = 5, 4, 5
	numTargets, Effects, description = 0, "Rush", "Rush. Costs (1) less for each card you've added to your hand from another class"
	name_CN = "蛮爪豺狼人"
	trigHand = Trig_WildpawGnoll
	@classmethod
	def checkTup(cls, tup, HeroClass, ID):
		return tup[0] == "AddCard2Hand" and HeroClass not in tup[1].Class and tup[2] == ID
		
	def selfManaChange(self):
		HeroClass = self.Game.heroes[self.ID].Class
		self.mana -= sum(WildpawGnoll.checkTup(tup, HeroClass, self.ID) for tup in self.Game.Counters.iter_TupsSoFar("events"))
		
	
class SleightofHand(Power):
	mana, name, numTargets = 0, "Sleight of Hand", 0
	description = "The next card you play this turn costs (2) less"
	name_CN = "手法娴熟"
	trigEffect = GameManaAura_SleightofHand
	def effect(self, target=(), choice=0, comment=''):
		GameManaAura_SleightofHand(self.Game, self.ID).auraAppears()
		
	
class ShadowcrafterScabbs(Hero):
	mana, description = 7, "Battlecry: Return all minions to their owner's hands. Summon two 4/2 Shadows with Steath"
	Class, name, heroPower, armor = "Rogue", "Shadowcrafter Scabbs", SleightofHand, 5
	name_CN = "塑影匠师斯卡布斯"
	index = "Battlecry~Legendary"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		game, ID = self.Game, self.ID
		for obj in self.Game.minionsonBoard(): game.returnObj2Hand(self, obj)
		self.summon([Shadow(game, ID) for _ in (0, 1)])
		
	
class Shadow(Minion):
	Class, race, name = "Rogue", "", "Shadow"
	mana, attack, health = 3, 4, 2
	name_CN = "影子"
	numTargets, Effects, description = 0, "Stealth", "Stealth"
	index = "Uncollectible"
	
	
class Windchill(Spell):
	Class, school, name = "Shaman", "Frost", "Windchill"
	numTargets, mana, Effects = 1, 1, ""
	description = "Freeze a minion. Draw a card"
	name_CN = "冷风"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.freeze(target)
		self.Game.Hand_Deck.drawCard(self.ID)
		
	
class Sleetbreaker(Minion):
	Class, race, name = "Shaman", "Elemental", "Sleetbreaker"
	mana, attack, health = 2, 3, 2
	numTargets, Effects, description = 0, "", "Battlecry: Add a Windchill to your hand"
	name_CN = "破霰元素"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.addCardtoHand(Windchill, self.ID)
		
	
class Frostbite(Spell):
	Class, school, name = "Shaman", "Frost", "Frostbite"
	numTargets, mana, Effects = 1, 2, ""
	description = "Deal 3 damage. Honorable Kill: Your opponent's next spell costs (2) more"
	name_CN = "冰霜嘶咬"
	trigEffect = GameManaAura_Frostbite
	def text(self): return self.calcDamage(3)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		damage, ownTurn = self.calcDamage(3), self.ID == self.Game.turn
		for obj in target:
			dmgTakers = self.dealsDamage(obj, damage)[0]
			if ownTurn and (n := sum(o.category == "Minion" and not o.health for o in dmgTakers)):
				for _ in range(n): GameManaAura_Frostbite(self.Game, 3-self.ID).auraAppears()
		
	
class CheatySnobold(Minion):
	Class, race, name = "Shaman", "", "Cheaty Snobold"
	mana, attack, health = 3, 3, 4
	numTargets, Effects, description = 0, "", "After an enemy is Frozen, deal 3 damage to it"
	name_CN = "作弊的狗头人"
	trigBoard = Trig_CheatySnobold
	
	
class SnowballFight(Spell):
	Class, school, name = "Shaman", "Frost", "Snowball Fight!"
	numTargets, mana, Effects = 1, 3, ""
	description = "Deal 1 damage to a minion and Freeze it. If it survives, repeat this on another minion"
	name_CN = "雪球大战"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def text(self): return self.calcDamage(1)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for obj in target:
			self.dealsDamage(obj, self.calcDamage(1))
			self.freeze(obj)
			minion = obj
			while minion.health > 0 and not minion.dead and (minions := self.Game.minionsAlive(exclude=minion)):
				minion = numpyChoice(minions)
				self.dealsDamage(obj, self.calcDamage(1))
				self.freeze(obj)
		
	
class WildpawCavern(Spell):
	Class, school, name = "Shaman", "", "Wildpaw Cavern"
	numTargets, mana, Effects = 0, 4, ""
	description = "At the end of your turn, summon a 3/4 Elemental that Freezes. Lasts 3 turns"
	name_CN = "蛮爪洞穴"
	trigEffect = WildpawCavern_Effect
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		WildpawCavern_Effect(self.Game, self.ID).connect()
		
	
class FrozenStagguard(Minion):
	Class, race, name = "Shaman", "Elemental", "Frozen Stagguard"
	mana, attack, health = 3, 3, 4
	name_CN = "冰封雄鹿守卫"
	numTargets, Effects, description = 0, "", "Freeze any character damaged by this minion"
	index = "Uncollectible"
	trigBoard = Trig_FreezeDamaged
	
	
class SnowfallGuardian(Minion):
	Class, race, name = "Shaman", "Elemental", "Snowfall Guardian"
	mana, attack, health = 5, 3, 3
	numTargets, Effects, description = 0, "", "Battlecry: Freeze all other minions. Gain +1/+1 for each Frozen minion"
	name_CN = "雪落守护者"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		objs = self.Game.minionsonBoard(exclude=self)
		self.freeze(objs)
		if objs: self.giveEnchant(self, len(objs), len(objs), source=SnowfallGuardian)
		
	
class Glaciate(Spell):
	Class, school, name = "Shaman", "Frost", "Glaciate"
	numTargets, mana, Effects = 0, 6, ""
	description = "Discover an 8-Cost minion. Summon and Freeze it"
	name_CN = "冰川急冻"
	poolIdentifier = "8-Cost Minions as Shaman to Summon"
	@classmethod
	def generatePool(cls, pools):
		classes = ["8-Cost Minions as %s to Summon" % Class for Class in pools.Classes]
		classCards = {s: [] for s in pools.ClassesandNeutral}
		for card in pools.MinionsofCost[6]:
			for Class in card.Class.split(','):
				classCards[Class].append(card)
		return classes, [classCards[Class] + classCards["Neutral"] for Class in pools.Classes]
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		minion, _ = self.discoverNew(comment, lambda : self.rngPool("8-Cost Minions as %s to Summon"%class4Discover(self)),
								  	add2Hand=False)
		self.summon(minion)
		self.freeze(minion)
		
	
class BearonGlashear(Minion):
	Class, race, name = "Shaman", "Elemental", "Bearon Gla'shear"
	mana, attack, health = 7, 6, 6
	name_CN = "熊男爵格雷希尔"
	numTargets, Effects, description = 0, "", "Battlecry: For each Frost spell you've cast this game, summon a 3/4 Elemental that Freezes"
	index = "Battlecry~Legendary"
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.examCardPlays(self.ID, veri_sum_ls=1, cond=lambda tup: tup[0].school == "Frost")
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if num := self.Game.Counters.examCardPlays(self.ID, veri_sum_ls=1, cond=lambda tup: tup[0].school == "Frost"):
			self.summon([FrozenStagguard(self.Game, self.ID) for _ in range(num)], relative='<>')
		
	
class EarthInvocation(Power):
	mana, name, numTargets = 2, "Earth Invocation", 0
	description = "Summon two 2/3 Elementals with Taunt. Swap each turn"
	name_CN = "大地祈咒"
	trigBoard = Trig_EarthInvocation
	def effect(self, target=(), choice=0, comment=''):
		self.summon([EarthenGuardian(self.Game, self.ID) for _ in (0, 1)])
		
	
class EarthenGuardian(Minion):
	Class, race, name = "Shaman", "Elemental", "Earthen Guardian"
	mana, attack, health = 2, 2, 3
	name_CN = "土灵守护者"
	numTargets, Effects, description = 0, "Taunt", "Taunt"
	index = "Uncollectible"
	
	
class FireInvocation(SteadyShot):
	name = "Fire Invocation"
	description = "Deal 6 damage to the enemy hero. Swap each turn"
	name_CN = "火焰祈咒"
	trigBoard = Trig_EarthInvocation
	def text(self): return self.calcDamage(6)
		
	def effect(self, target=(), choice=0, comment=''):
		if not target: target = (self.Game.heroes[3-self.ID],)
		self.dealsDamage(target, self.calcDamage(6))
		
	
class LightningInvocation(Power):
	mana, name, numTargets = 2, "Lightning Invocation", 0
	description = "Deal 2 damage to all enemy minions. Swap each turn"
	name_CN = "闪电祈咒"
	trigBoard = Trig_EarthInvocation
	def dealsDmg(self): return True
		
	def text(self): return self.calcDamage(2)
		
	def effect(self, target=(), choice=0, comment=''):
		self.dealsDamage(self.Game.minionsonBoard(3-self.ID), self.calcDamage(2))
		
	
class WaterInvocation(Power):
	mana, name, numTargets = 2, "Water Invocation", 0
	description = "Restor 6 Health to all friendly characters. Swap each turn"
	name_CN = "流水祈咒"
	trigBoard = Trig_EarthInvocation
	def text(self): return self.calcHeal(6)
		
	def effect(self, target=(), choice=0, comment=''):
		self.heals(self.Game.charsonBoard(self.ID), self.calcHeal(6))
		
	
class ElementalMastery(Power):
	mana, name, numTargets = 2, "Elemental Mastery", 0
	description = "Call upon a different Element every turn"
	name_CN = "元素精通"
	invocations = (EarthInvocation, FireInvocation, LightningInvocation, WaterInvocation)
	def appears(self):
		numpyChoice(ElementalMastery.invocations)(self.Game, self.ID).replacePower()
		
	
class BrukanoftheElements(Hero):
	mana, description = 8, "Battlecry: Call upon the power of two Elements"
	Class, name, heroPower, armor = "Shaman", "Bru'kan of the Elements", ElementalMastery, 5
	name_CN = "元素使者布鲁坎"
	index = "Battlecry~Legendary"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		options = [power(self.Game, self.ID) for power in ElementalMastery.invocations]
		for _ in (0, 1):
			options.remove(chosen := self.chooseFixedOptions(comment, options))
			cardType = type(chosen)
			if cardType == EarthInvocation: self.summon([EarthenGuardian(self.Game, self.ID) for _ in (0, 1)])
			elif cardType == FireInvocation: self.dealsDamage(self.Game.heroes[3-self.ID], 6)
			elif cardType == LightningInvocation: self.dealsDamage(self.Game.minionsonBoard(3-self.ID), 2)
			else: self.heals(self.Game.charsonBoard(self.ID), self.calcHeal(6))
		#剩下的两个英雄技能之一会是技能的初始形态
		numpyChoice(options).replacePower()
		
	
class GraveDefiler(Minion):
	Class, race, name = "Warlock", "", "Grave Defiler"
	mana, attack, health = 1, 2, 1
	numTargets, Effects, description = 0, "", "Battlecry: Copy a Fel spell in your hand"
	name_CN = "墓地污染者"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if spells := [card for card in self.Game.Hand_Deck.hands[self.ID] if card.school == "Fel"]:
			self.addCardtoHand(self.copyCard(numpyChoice(spells), self.ID), self.ID)
		
	
class SeedsofDestruction(Spell):
	Class, school, name = "Warlock", "Fel", "Seeds of Destruction"
	numTargets, mana, Effects = 0, 2, ""
	description = "Shuffle four Rifts into your deck. They summon a 3/3 Dread Imp when drawn"
	name_CN = "毁灭之种"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.shuffleintoDeck([FelRift(self.Game, self.ID) for _ in (0, 1, 2, 3)])
		
	
class DesecratedGraveyard(Spell):
	Class, school, name = "Warlock", "", "Desecrated Graveyard"
	numTargets, mana, Effects = 0, 3, ""
	description = "At the end of your turn, destroy your lowest Attack minion to summon a 4/4 Shade. Lasts 3 turns"
	name_CN = "被亵渎的墓园"
	trigEffect = DesecratedGraveyard_Effect
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		DesecratedGraveyard_Effect(self.Game, self.ID).connect()
		
	
class DesecratedShade(Minion):
	Class, race, name = "Warlock", "", "Desecrated Shade"
	mana, attack, health = 4, 4, 4
	numTargets, Effects, description = 0, "", ""
	name_CN = "亵渎影魔"
	index = "Uncollectible"
	
	
class FelRift(Spell):
	Class, school, name = "Warlock", "Fel", "Fel Rift"
	numTargets, mana, Effects = 0, 3, ""
	description = "Casts When Drawn. Summon a 3/3 Dread Imp"
	name_CN = "邪能裂缝"
	index = "Uncollectible"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon(DreadImp(self.Game, self.ID))
		
	
class DreadImp(Minion):
	Class, race, name = "Warlock", "", "Dread Imp"
	mana, attack, health = 3, 3, 3
	numTargets, Effects, description = 0, "", ""
	name_CN = "恐惧小鬼"
	index = "Uncollectible"
	
	
class FullBlownEvil(Spell):
	Class, school, name = "Warlock", "Fel", "Full-Blown Evil"
	numTargets, mana, Effects = 0, 3, ""
	description = "Deal 5 damage randomly split among all enemy minion. Repeatable this turn"
	name_CN = "邪恶入骨"
	def text(self): return self.calcDamage(5)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for _ in range(self.calcDamage(5)):
			if minions := self.Game.minionsAlive(3-self.ID):
				self.dealsDamage(numpyChoice(minions), 1)
			else: break
		echo = FullBlownEvil(self.Game, self.ID)
		echo.trigsHand.append(Trig_Echo(echo))
		self.addCardtoHand(echo, self.ID)
		
	
class SacrificialSummoner(Minion):
	Class, race, name = "Warlock", "", "Sacrificial Summoner"
	mana, attack, health = 3, 3, 3
	numTargets, Effects, description = 1, "", "Battlecry: Destroy a friendly minion. Summon a minion from your deck that costs (1) more"
	name_CN = "献祭召唤者"
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists(self.ID)
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.ID == self.ID and obj is not self and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for obj in target:
			if not obj.dead:
				pos, cost = obj.pos, obj.mana
				self.Game.kill(self, obj)
				self.Game.gathertheDead()  # 强制死亡需要在此插入死亡结算，并让随从离场
				self.try_SummonfromOwn(position=pos, cond=lambda card: card.category == "Minion" and card.mana == cost + 1)
		
	
class TamsinsPhylactery(Spell):
	Class, school, name = "Warlock", "Shadow", "Tamsin's Phylactery"
	numTargets, mana, Effects = 0, 4, ""
	name_CN = "塔姆辛的咒瓶"
	description = "Discover a friendly Deathrattle minion that died this game. Give your minions its Deathrattle"
	index = "Legendary"
	def available(self):
		self.effectViable = self.Game.Hand_Deck.Counters.examDeads(self.ID, cond=lambda card: card.deathrattle is not None)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		card, _ = self.discoverfrom(comment, tupsFunc=lambda : self.Game.Hand_Deck.Counters.examDeads(self.ID, veri_sum_ls=2, cond=lambda card: card.deathrattle))
		if card: self.giveEnchant(self.Game.minionsonBoard(self.ID), trig=type(card).deathrattle, trigType="Deathrattle")
		
	
class FelfireintheHole(Spell):
	Class, school, name = "Warlock", "Fel", "Felfire in the Hole!"
	numTargets, mana, Effects = 0, 5, ""
	description = "Draw a spell and deal 2 damage to all enemies. If it's a Fel spell, deal 1 more"
	name_CN = "邪火爆弹"
	def text(self): return self.calcDamage(2)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		spell, mana, entersHand = self.drawCertainCard(cond=lambda card: card.category == "Spell")
		damage = self.calcDamage(3 if spell and spell.school == "Fel" else 2)
		self.dealsDamage(self.Game.minionsonBoard(), damage)
		
	
class HollowAbomination(Minion):
	Class, race, name = "Warlock", "", "Hollow Abomination"
	mana, attack, health = 5, 2, 8
	numTargets, Effects, description = 0, "", "Battlecry: Deal 1 damage to all enemy minions. Honorable Kill: Gain the minion's Attack"
	name_CN = "可怕的憎恶"
	trigBoard = Trig_HollowAbomination
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(self.Game.minionsonBoard(3-self.ID), 1)
		
	
class ChainsofDread(Power):
	mana, name, numTargets = 2, "Chains of Dread", 0
	description = "Shuffle a Rift into your deck. Draw a card"
	name_CN = "恐惧之链"
	def effect(self, target=(), choice=0, comment=''):
		self.shuffleintoDeck(FelRift(self.Game, self.ID))
		self.Game.Hand_Deck.drawCard(self.ID, initiator=self)
		
	
class DreadlichTamsin(Hero):
	mana, description = 6, "Battlecry: Deal 3 damage to all minions. Shuffle 3 Rifts into your deck. Draw 3 cards"
	Class, name, heroPower, armor = "Warlock", "Dreadlich Tamsin", ChainsofDread, 5
	name_CN = "恐惧巫妖塔姆辛"
	index = "Battlecry~Legendary"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(self.Game.minionsonBoard(), 3)
		self.shuffleintoDeck([FelRift(self.Game, self.ID) for _ in (0, 1, 2)])
		for _ in (0, 1, 2): self.Game.Hand_Deck.drawCard(self.ID)
		
	
class Felwalker(Minion):
	Class, race, name = "Warlock", "Demon", "Felwalker"
	mana, attack, health = 6, 3, 7
	numTargets, Effects, description = 0, "Taunt", "Taunt. Battlecry: Cast the highest Cost Fel spell from your hand"
	name_CN = "邪火行者"
	def effCanTrig(self):
		self.effectViable = any(card.school == "Fel" for card in self.Game.Hand_Deck.hands[self.ID])
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if indices := pickInds_HighestAttr(self.Game.Hand_Deck.hands[self.ID], cond=lambda card: card.school == "Fel"):
			self.Game.Hand_Deck.extractfromHand(numpyChoice(indices), self.ID)[0].cast()
		
	
class FrozenBuckler(Spell):
	Class, school, name = "Warrior", "Frost", "Frozen Buckler"
	numTargets, mana, Effects = 0, 2, ""
	description = "Gain 10 Armor. At the start of your next turn, lose 5 Armor"
	name_CN = "凝冰护盾"
	trigEffect = FrozenBuckler_Effect
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveHeroAttackArmor(self.ID, armor=10)
		FrozenBuckler_Effect(self.Game, self.ID).connect()
		
	
class IcebloodGarrison(Spell):
	Class, school, name = "Warrior", "", "Iceblood Garrison"
	numTargets, mana, Effects = 0, 2, ""
	description = "At the end of your turn, deal 1 damage to all minions. Lasts 3 turn"
	name_CN = "冰血要塞"
	trigEffect = IcebloodGarrison_Effect
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		IcebloodGarrison_Effect(self.Game, self.ID).connect()
		
	
class TotheFront(Spell):
	Class, school, name = "Warrior", "", "To the Front!"
	numTargets, mana, Effects = 0, 2, ""
	description = "Your minions cost (2) less this turn (but not less than 1)"
	name_CN = "奔赴前线"
	trigEffect = GameManaAura_TotheFront
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		GameManaAura_TotheFront(self.Game, self.ID).auraAppears()
		
	
class GloryChaser(Minion):
	Class, race, name = "Warrior", "", "Glory Chaser"
	mana, attack, health = 3, 4, 3
	numTargets, Effects, description = 0, "", "After you play a Taunt minion, draw a card"
	name_CN = "荣耀追逐者"
	trigBoard = Trig_GloryChaser
	
	
class Scrapsmith(Minion):
	Class, race, name = "Warrior", "", "Scrapsmith"
	mana, attack, health = 3, 2, 4
	numTargets, Effects, description = 0, "Taunt", "Taunt. Battlecry: Add two 2/4 Grunts with Taunt to your hand"
	name_CN = "废料铁匠"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.addCardtoHand((ScrappyGrunt, ScrappyGrunt), self.ID)
		
	
class ScrappyGrunt(Minion):
	Class, race, name = "Warrior", "", "Scrappy Grunt"
	mana, attack, health = 3, 2, 4
	name_CN = "废铁步兵"
	numTargets, Effects, description = 0, "Taunt", "Taunt"
	index = "Uncollectible"
	
	
class SnowedIn(Spell):
	Class, school, name = "Warrior", "Frost", "Snowed In"
	numTargets, mana, Effects = 1, 3, ""
	description = "Destroy a damaged minion. Freeze all other minions"
	name_CN = "冰雪围困"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard and obj.health < obj.health
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for obj in target:
			self.Game.kill(self, obj)
			self.freeze(self.Game.minionsonBoard(exclude=obj))
		
	
class AxeBerserker(Minion):
	Class, race, name = "Warrior", "", "Axe Berserker"
	mana, attack, health = 4, 3, 5
	numTargets, Effects, description = 0, "Rush", "Rush. Honorable Kill: Draw a weapon"
	name_CN = "执斧狂战士"
	trigBoard = Trig_AxeBerserker
	
	
class CaptainGalvangar(Minion):
	Class, race, name = "Warrior", "", "Captain Galvangar"
	mana, attack, health = 6, 6, 6
	name_CN = "加尔范上尉"
	numTargets, Effects, description = 0, "", "Battlecry: If you have gained 15 or more Armor this game, gain +3/+3 and Charge"
	index = "Battlecry~Legendary"
	def effCanTrig(self):
		self.effectViable = 15 <= sum(tup[2] for tup in self.Game.Counters.iter_TupsSoFar("events") if tup[0] == ["GainArmor"] and tup[1] == self.ID)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if 15 <= sum(tup[2] for tup in self.Game.Counters.iter_TupsSoFar("events") if tup[0] == ["GainArmor"] and tup[1] == self.ID):
			self.giveEnchant(self, 3, 3, effGain="Charge", source=CaptainGalvangar)
		
	
class GrandSlam(Power):
	mana, name, numTargets = 2, "Grand Slam", 1
	description = "Deal 2 damage. Honorable Kill: Gain 4 Armor"
	name_CN = "巨力猛击"
	def dealsDmg(self): return True
		
	def text(self): return self.calcDamage(2)
		
	def effect(self, target=(), choice=0, comment=''):
		damage, ownTurn = self.calcDamage(2), self.ID == self.Game.turn
		for obj in target:
			dmgTakers = self.dealsDamage(target, damage)[0]
			if ownTurn and (n := sum(o.category == "Minion" and not o.health for o in dmgTakers)):
				for _ in range(n): self.giveHeroAttackArmor(self.ID, armor=4)
		
	
class RokaratheValorous(Hero):
	mana, description = 7, "Battlecry: Equip a 5/2 Unstoppable Force"
	Class, name, heroPower, armor = "Warrior", "Rokara, the Valorous", GrandSlam, 5
	name_CN = "勇猛战将洛卡拉"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.equipWeapon(TheUnstoppableForce(self.Game, self.ID))
		
	
class TheUnstoppableForce(Weapon):
	Class, name, description = "Warrior", "The Unstoppable Force", "After you attack a minion, smash it into the enemy hero"
	mana, attack, durability, Effects = 7, 5, 2, ""
	name_CN = "无坚不摧之力"
	index = "Legendary~Uncollectible"
	trigBoard = Trig_TheUnstoppableForce
	
	
class ShieldShatter(Spell):
	Class, school, name = "Warrior", "Frost", "Shield Shatter"
	numTargets, mana, Effects = 0, 10, ""
	description = "Deal 5 damage to all minions. Costs (1) less for each Armor you have"
	name_CN = "裂盾一击"
	trigHand = Trig_ShieldShatter
	def selfManaChange(self):
		self.mana -= self.Game.heroes[self.ID].armor
		
	def text(self): return self.calcDamage(5)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(self.Game.minionsonBoard(), self.calcDamage(5))
		
	


AllClasses_Alterac = [
	Death_Popsicooler, Death_DireFrostwolf, Death_PiggybackImp, Death_KorraktheBloodrager, Death_Legionnaire, Death_HumongousOwl,
	Death_StormpikeBattleRam, Death_MountainBear, Death_CavalryHorn, Death_NajakHexxen, Death_SpiritGuide, Death_UndyingDisciple,
	HonorableKill, Trig_GnomePrivate, Trig_IrondeepTrogg, Trig_Gankster, Trig_Corporal, Trig_SneakyScout, Trig_StormpikeQuartermaster,
	Trig_DirewolfCommander, Trig_FrostwolfWarmaster, Trig_FrozenMammoth, Trig_IceRevenant, Trig_StormpikeMarshal,
	Trig_BloodGuard, Trig_FranticHippogryph, Trig_KnightCaptain, Trig_AbominableLieutenant, Trig_TrollCenturion, Trig_LokholartheIceLord,
	Trig_DreadprisonGlaive, Trig_BattlewornVanguard, Trig_FlagRunner, Trig_AshfallensFury, Trig_UrzulGiant, Trig_WingCommanderMulverick,
	Trig_FrostsaberMatriarch, Trig_Bloodseeker, Trig_IceTrap, Trig_TheImmovableObject, Trig_Brasswing, Trig_TemplarCaptain,
	Trig_LuminousGeode, Trig_HolyTouch, Trig_VoidSpike, Trig_ForsakenLieutenant, Trig_TheLobotomizer, Trig_WildpawGnoll,
	Trig_CheatySnobold, Trig_EarthInvocation, Trig_HollowAbomination, Trig_GloryChaser, Trig_AxeBerserker, Trig_TheUnstoppableForce,
	Trig_ShieldShatter, GameManaAura_SneakyScout, GameAura_FieldofStrife, FlankingManeuver_Effect, SigilofReckoning_Effect,
	GameManaAura_PrideSeeker, FrostwolfKennels_Effect, DunBaldarBunker_Effect, GameManaAura_StormpikeBattleRam, WingCommanderIchman_Effect,
	GameManaAura_AmplifiedSnowflurry, IcebloodTower_Effect, DunBaldarBridge_Effect, StormpikeAidStation_Effect, SnowfallGraveyard_Effect,
	GameManaAura_SleightofHand, GameManaAura_Frostbite, WildpawCavern_Effect, DesecratedGraveyard_Effect, FrozenBuckler_Effect,
	GameManaAura_TotheFront, IcebloodGarrison_Effect, GnomePrivate, IrondeepTrogg, IvustheForestLord, Gankster, RamCommander,
	BattleRam, Corporal, SneakyScout, StormpikeQuartermaster, BunkerSergeant, DirewolfCommander, FrostwolfCub, GrimtotemBountyHunter,
	KoboldTaskmaster, ArmorScrap, PiggybackImp, BackpiggyImp, Popsicooler, ReflectoEngineer, SnowblindHarpy, DrekThar,
	FrostwolfWarmaster, FrozenMammoth, HeraldofLokholar, IceRevenant, KorraktheBloodrager, StormpikeMarshal, TowerSergeant,
	VanndarStormpike, BloodGuard, FranticHippogryph, KnightCaptain, SpammyArcanist, IcehoofProtector, Legionnaire,
	HumongousOwl, AbominableLieutenant, TrollCenturion, LokholartheIceLord, DreadprisonGlaive, BattlewornVanguard,
	FieldofStrife, FlagRunner, FlankingManeuver, SnowySatyr, WardenofChains, SigilofReckoning, CariaFelsoul, AshfallensFury,
	KurtrusDemonRender, FelbatShrieker, UrzulGiant, MoreResources, MoreSupplies, MoreResources_Option, MoreSupplies_Option,
	CaptureColdtoothMine, ClawfuryAdept, FrostwolfKennels, HeartoftheWild, Pathmaker, PrideSeeker, DireFrostwolf,
	WingCommanderMulverick, StrikeWyvern, IceBlossom_Option, ValleyRoot_Option, Nurture, WildheartGuff, FrostsaberMatriarch,
	Bloodseeker, DunBaldarBunker, IceTrap, RamTamer, RevivePet, SpringtheTrap, StormpikeBattleRam, MountainBear, MountainCub,
	ImprovedExplosiveTrap, ImprovedFreezingTrap, Snake_Alterac, ImprovedSnakeTrap, ImprovedPackTactics, ImprovedOpentheCages,
	ImprovedIceTrap, SummonPet, BeaststalkerTavish, WingCommanderIchman, ShiveringSorceress, AmplifiedSnowflurry,
	SiphonMana, BuildaSnowman, BuildaSnowbrute, BuildaSnowgre, Snowman, Snowbrute, Snowgre, ArcaneBrilliance, BalindaStonehearth,
	MassPolymorph, Sheep_Alterac, ArcaneBurst, MagisterDawngrasp, IcebloodTower, VitalitySurge, HoldtheBridge, SaidantheScarlet,
	StonehearthVindicator, DunBaldarBridge, CavalryHorn, ProtecttheInnocent, StormpikeDefender, BlessingofQueens,
	LightforgedCariel, TheImmovableObject, Brasswing, TemplarCaptain, GiftoftheNaaru, ShadowWordDevour, Bless, Deliverance,
	LuminousGeode, StormpikeAidStation, NajakHexxen, SpiritGuide, UndyingDisciple, HolyTouch, VoidSpike, XyrellatheDevout,
	ForsakenLieutenant, Reconnaissance, TheLobotomizer, ColdtoothYeti, DoubleAgent, SnowfallGraveyard, CerathineFleetrunner,
	ContrabandStash, WildpawGnoll, SleightofHand, ShadowcrafterScabbs, Shadow, Windchill, Sleetbreaker, Frostbite,
	CheatySnobold, SnowballFight, WildpawCavern, FrozenStagguard, SnowfallGuardian, Glaciate, BearonGlashear, EarthInvocation,
	EarthenGuardian, FireInvocation, LightningInvocation, WaterInvocation, ElementalMastery, BrukanoftheElements,
	GraveDefiler, SeedsofDestruction, DesecratedGraveyard, DesecratedShade, FelRift, DreadImp, FullBlownEvil, SacrificialSummoner,
	TamsinsPhylactery, FelfireintheHole, HollowAbomination, ChainsofDread, DreadlichTamsin, Felwalker, FrozenBuckler,
	IcebloodGarrison, TotheFront, GloryChaser, Scrapsmith, ScrappyGrunt, SnowedIn, AxeBerserker, CaptainGalvangar,
	GrandSlam, RokaratheValorous, TheUnstoppableForce, ShieldShatter, 
]

for class_ in AllClasses_Alterac:
	if issubclass(class_, Card):
		class_.index = "ALTERAC_VALLEY" + ("~" if class_.index else '') + class_.index