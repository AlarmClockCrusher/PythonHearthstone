from Parts_ConstsFuncsImports import *
from Parts_CardTypes import *
from Parts_TrigsAuras import *

from HS_AcrossPacks import TheCoin, SilverHandRecruit, LeaderofthePack, SummonaPanther, EvolveScales, EvolveSpines, \
						RampantGrowth, Enrich, Treant_Classic, Treant_Classic_Taunt, \
						Frog, SpiritWolf, BloodFury, Infernal, Panther, \
						Snake, IllidariInitiate, ExcessMana, Bananas, Nerubian, \
						VioletApprentice, Hyena_Classic, BaineBloodhoof, Whelp, DruidoftheClaw_Charge, \
						DruidoftheClaw_Taunt, DruidoftheClaw_Both, Skeleton, Shadowbeast, Defender, Ashbringer, \
						Dream, Nightmare, YseraAwakens, LaughingSister, EmeraldDrake, Trig_WaterElemental


"""Auras"""
class Aura_Cogmaster(Aura_Conditional):
	signals, attGain, targets = ("MinionAppears", "MinionDisappears"), 2, "Self"
	def whichWay(self): #Decide the aura turns on(1) or off(-1), or does nothing(0)
		hasMech = any("Mech" in obj.race for obj in self.keeper.Game.minionsonBoard(self.keeper.ID))
		if not hasMech and self.on: return -1
		elif hasMech and not self.on: return 1
		else: return 0

	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		obj = subject if signal == "MinionAppears" else target
		return self.keeper.onBoard and obj.ID == self.keeper.ID and "Mech" in obj.race


class Aura_DireWolfAlpha(Aura_AlwaysOn):
	attGain, targets = 1, "Neighbors"

class Aura_RaidLeader(Aura_AlwaysOn):
	attGain = 1

class Aura_SouthseaCaptain(Aura_AlwaysOn):
	attGain = healthGain = 1
	def applicable(self, target): return "Pirate" in target.race

class GameRuleAura_BaronRivendare(GameRuleAura):
	def auraAppears(self): self.keeper.Game.effects[self.keeper.ID]["Deathrattle x2"] += 1
	def auraDisappears(self): self.keeper.Game.effects[self.keeper.ID]["Deathrattle x2"] -= 1

class Aura_StormwindChampion(Aura_AlwaysOn):
	attGain = healthGain = 1

class GameRuleAura_FallenHero(GameRuleAura):
	def auraAppears(self): self.keeper.Game.powers[self.keeper.ID].getsEffect("Power Damage")
	def auraDisappears(self): self.keeper.Game.powers[self.keeper.ID].losesEffect("Power Damage")

class GameRuleAura_ColdarraDrake(GameRuleAura):
	def auraAppears(self):
		self.keeper.Game.effects[self.keeper.ID]["Power Chance Inf"] += 1
		if btn := self.keeper.Game.powers[self.keeper.ID].btn: btn.checkHpr()

	def auraDisappears(self):
		self.keeper.Game.effects[self.keeper.ID]["Power Chance Inf"] -= 1
		if btn := self.keeper.Game.powers[self.keeper.ID].btn: btn.checkHpr()


class Aura_WarhorseTrainer(Aura_AlwaysOn):
	attGain = 1
	def applicable(self, target): return target.name == "Silver Hand Recruit"


"""Deathrattles"""
class Death_BloodmageThalnos(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.Game.Hand_Deck.drawCard(self.keeper.ID)

class Death_ExplosiveSheep(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		targets = self.keeper.Game.minionsonBoard(1) + self.keeper.Game.minionsonBoard(2)
		self.keeper.AOE_Damage(targets, [2] * len(targets))

class Death_LootHoarder(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.Game.Hand_Deck.drawCard(self.keeper.ID)

class Death_NerubianEgg(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.summon(Nerubian(self.keeper.Game, self.keeper.ID))

class Death_TaelanFordring(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if indices := pickHighestCostIndices(self.keeper.Game.Hand_Deck.decks[self.keeper.ID],
											 func=lambda card: card.category == "Minion"):
			self.keeper.Game.Hand_Deck.drawCard(self.keeper.ID, numpyChoice(indices))

class Death_CairneBloodhoof(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.summon(BaineBloodhoof(self.keeper.Game, self.keeper.ID))

class Death_SouloftheForest(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		# This Deathrattle can't possibly be triggered in hand
		self.keeper.summon(Treant_Classic(self.keeper.Game, self.keeper.ID))

class Death_Webspinner(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.addCardtoHand(numpyChoice(self.rngPool("Beasts")), self.keeper.ID)

class Death_SavannahHighmane(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.summon([Hyena_Classic(self.keeper.Game, self.keeper.ID) for _ in (0, 1)], relative="<>")

class Death_AegwynntheGuardian(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		AegwynntheGuardian_Effect(self.keeper.Game, self.keeper.ID).connect()

class Death_TirionFordring(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.equipWeapon(Ashbringer(self.keeper.Game, self.keeper.ID))

class Death_ShadowedSpirit(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.dealsDamage(self.keeper.Game.heroes[3-self.keeper.ID], 3)

class Death_TombPillager(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.addCardtoHand(TheCoin(self.keeper.Game, self.keeper.ID), self.keeper.ID)

class Death_PossessedVillager(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.summon(Shadowbeast(self.keeper.Game, self.keeper.ID))

class Death_FelsoulJailer(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if self.savedObj: self.keeper.addCardtoHand(self.savedObj, 3 - self.keeper.ID)

	def selfCopy(self, recipient):
		trig = type(self)(recipient)
		trig.savedObj = self.savedObj
		return trig

	def assistCreateCopy(self, Copy):
		Copy.savedObj = self.savedObj


"""Trigs"""
class Trig_Cogmaster(Trig_SelfAura):
	signals = ("MinionAppears", "MinionDisappears")
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and (('A' in signal or subject.ID == self.keeper.ID and "Mech" in subject.race) or
										('D' in signal or target.ID == self.keeper.ID and "Mech" in target.race))

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.calcStat()


class Trig_ArcaneAnomaly(TrigBoard):
	signals = ("SpellBeenPlayed", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject.ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.giveEnchant(self.keeper, statEnchant=Enchantment_Cumulative(0, 1, name=ArcaneAnomaly))


class Trig_MurlocTidecaller(TrigBoard):
	signals = ("MinionSummoned", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject.ID == self.keeper.ID and "Murloc" in subject.race and subject != self.keeper

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.giveEnchant(self.keeper, statEnchant=Enchantment_Cumulative(1, 0, name=MurlocTidecaller))


class Trig_YoungPriestess(TrigBoard):
	signals = ("TurnEnds", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if minions := self.keeper.Game.minionsonBoard(self.keeper.ID, exclude=self.keeper):
			self.keeper.giveEnchant(numpyChoice(minions), statEnchant=Enchantment_Cumulative(0, 1, name=YoungPriestess))


class Trig_FlesheatingGhoul(TrigBoard):
	signals = ("MinionDies", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and target != self.keeper #Technically, minion has to disappear before dies. But just in case.

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.giveEnchant(self.keeper, statEnchant=Enchantment_Cumulative(1, 0, name=FlesheatingGhoul))


class Trig_VioletTeacher(TrigBoard):
	signals = ("SpellPlayed", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject.ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.summon(VioletApprentice(self.keeper.Game, self.keeper.ID))


class Trig_GurubashiBerserker(TrigBoard):
	signals = ("MinionTakesDmg", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return target == self.keeper and self.keeper.onBoard

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.giveEnchant(self.keeper, statEnchant=Enchantment_Cumulative(3, 0, name=GurubashiBerserker))


class Trig_OverlordRunthak(TrigBoard):
	signals = ("MinionAttackingMinion", "MinionAttackingHero", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.keeper and self.keeper.onBoard

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.AOE_GiveEnchant([card for card in self.keeper.Game.Hand_Deck.hands[self.keeper.ID] if card.category == "Minion"], 
									statEnchant=Enchantment_Cumulative(1, 1, name=OverlordRunthak), add2EventinGUI=False)


class Trig_GadgetzanAuctioneer(TrigBoard):
	signals = ("SpellPlayed",)
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject.ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.Game.Hand_Deck.drawCard(self.keeper.ID)


class Trig_BaronGeddon(TrigBoard):
	signals = ("TurnEnds", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.keeper
		targets = list(minion.Game.heroes.values()) + minion.Game.minionsonBoard(minion.ID, minion) + minion.Game.minionsonBoard(3-minion.ID)
		minion.AOE_Damage(targets, [2]*len(targets))


class Trig_ArcaneDevourer(TrigBoard):
	signals = ("SpellPlayed", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject.ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.giveEnchant(self.keeper, statEnchant=Enchantment_Cumulative(2, 2, name=ArcaneDevourer))


class Trig_OnyxiatheBroodmother(TrigBoard):
	signals = ("TurnEnds", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.keeper
		minion.summon([Whelp(minion.Game, minion.ID) for i in range(6)], relative="<>")


class Trig_ClockworkGiant(TrigHand):
	signals = ("CardLeavesHand", "CardEntersHand", )
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.inHand and ID != self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.Game.Manas.calcMana_Single(self.keeper)


class Trig_Battlefiend(TrigBoard):
	signals = ("HeroAttackedMinion", "HeroAttackedHero", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject == self.keeper.Game.heroes[self.keeper.ID]

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.giveEnchant(self.keeper, statEnchant=Enchantment_Cumulative(1, 0, name=Battlefiend))


class Trig_KorvasBloodthorn(TrigBoard):
	signals = ("MinionBeenPlayed", "SpellBeenPlayed", "WeaponBeenPlayed", "HeroBeenPlayed", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject.ID == self.keeper.ID and "~Outcast" in subject.index and not self.keeper.dead and self.keeper.health > 0

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.Game.returnObj2Hand(self.keeper, deathrattlesStayArmed=False)


class Trig_EyeBeam(TrigHand):
	signals = ("CardLeavesHand", "CardEntersHand", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.inHand and (target[0] if "E" in signal else target).ID == self.keeper.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.Game.Manas.calcMana_Single(self.keeper)


class Trig_WarglaivesofAzzinoth(TrigBoard):
	signals = ("HeroAttackedMinion", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.keeper.Game.heroes[self.keeper.ID] and target.category == "Minion" and self.keeper.onBoard

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.Game.heroes[self.keeper.ID].attChances_extra +=1


class Trig_IllidariInquisitor(TrigBoard):
	signals = ("HeroAttackedMinion", "HeroAttackedHero", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.keeper #The target and this minion can't be dying to trigger this
		return subject.ID == minion.ID and minion.onBoard and not minion.dead and minion.health > 0 and not target.dead and target.health > 0

	#随从的攻击顺序与它们的登场顺序一致
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.Game.battle(self.keeper, target, verifySelectable=False, useAttChance=False, resolveDeath=False, resetRedirTrig=True)


class Trig_ExplosiveTrap(Trig_Secret):
	signals = ("HeroAttacksHero", "MinionAttacksHero", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0): #target here holds the actual target object
		return self.keeper.ID != self.keeper.Game.turn and target[0] == self.keeper.Game.heroes[self.keeper.ID]

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		damage = self.keeper.calcDamage(2)
		enemies = [self.keeper.Game.heroes[3-self.keeper.ID]] + self.keeper.Game.minionsonBoard(3-self.keeper.ID)
		self.keeper.AOE_Damage(enemies, [damage]*len(enemies))


class Trig_FreezingTrap(Trig_Secret):
	signals = ("MinionAttacksMinion", "MinionAttacksHero", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.ID != self.keeper.Game.turn and subject.category == "Minion" and subject.ID != self.keeper.ID \
				and subject.onBoard and subject.health > 0 and not subject.dead #The attacker must be onBoard and alive to be returned to hand

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		# 假设那张随从在进入手牌前接受+2费效果。可以被娜迦海巫覆盖。
		self.keeper.func(subject, func=lambda minion: self.keeper.Game.returnObj2Hand(subject, deathrattlesStayArmed=False,
																					  manaMod=ManaMod(subject, by=+2)),
						 text="+2", color=red)


class Trig_ScavengingHyena(TrigBoard):
	signals = ("MinionDies", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		#Technically, minion has to disappear before dies. But just in case.
		return self.keeper.onBoard and target != self.keeper and target.ID == self.keeper.ID and "Beast" in target.race

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.giveEnchant(self.keeper, statEnchant=Enchantment_Cumulative(2, 1, name=ScavengingHyena))


class Trig_SnakeTrap(Trig_Secret):
	signals = ("MinionAttacksMinion", "HeroAttacksMinion", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0): #target here holds the actual target object
		#The target has to a friendly minion and there is space on board to summon minions.
		return self.keeper.ID != self.keeper.Game.turn and target[0].category == "Minion" and target[0].ID == self.keeper.ID and self.keeper.Game.space(self.keeper.ID) > 0

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.summon([Snake(self.keeper.Game, self.keeper.ID) for _ in (0, 1, 2)])


class Trig_Counterspell(Trig_Secret):
	signals = ("SpellOKtoCast?", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return ID != self.keeper.ID and subject

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.Game.add2EventinGUI(self.keeper, subject[0], textTarget="X", colorTarget=red)
		subject.pop()


class Trig_IceBarrier(Trig_Secret):
	signals = ("HeroAttacksHero", "MinionAttacksHero", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):  #target here holds the actual target object
		return self.keeper.ID != self.keeper.Game.turn and target[0] == self.keeper.Game.heroes[self.keeper.ID]

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.giveHeroAttackArmor(self.keeper.ID, armor=8)
		

class Trig_MirrorEntity(Trig_Secret):
	signals = ("MinionBeenPlayed", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.ID != self.keeper.Game.turn and subject.ID != self.keeper.ID and self.keeper.Game.space(self.keeper.ID) > 0 and subject.health > 0 and subject.dead == False

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.summon(subject.selfCopy(self.keeper.ID, self.keeper))


class Trig_Avenge(Trig_Secret):
	signals = ("MinionDies", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.ID != self.keeper.Game.turn and target.ID == self.keeper.ID and self.keeper.Game.minionsonBoard(target.ID)

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if minions := self.keeper.Game.minionsonBoard(self.keeper.ID):
			self.keeper.giveEnchant(numpyChoice(minions), 3, 2, name=Avenge)


class Trig_NobleSacrifice(Trig_Secret):
	signals = ("MinionAttacksHero", "MinionAttacksMinion", "HeroAttacksHero", "HeroAttacksMinion", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.ID != self.keeper.Game.turn and subject.ID != self.keeper.ID and self.keeper.Game.space(self.keeper.ID) > 0

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		newTarget = Defender(self.keeper.Game, self.keeper.ID)
		self.keeper.summon(newTarget)
		target[1] = newTarget


#假设是被随从一次性造成3点或以上的伤害触发，单发或者AOE伤害均可
class Trig_Reckoning(Trig_Secret):
	signals = ("DealtDmg", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.ID != self.keeper.Game.turn and number > 2 and not self.on\
			and subject.ID != self.keeper.ID and subject.category == "Minion" and not subject.dead and subject.health > 0

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.Game.kill(self.keeper, subject)
		self.on = True


class Trig_TruesilverChampion(TrigBoard):
	signals, nextAniWaits = ("HeroAttackingMinion", "HeroAttackingHero", ), True
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.keeper.Game.heroes[self.keeper.ID] and self.keeper.onBoard

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.restoresHealth(self.keeper.Game.heroes[self.keeper.ID], self.keeper.calcHeal(2))


class Trig_CrimsonClergy(TrigBoard):
	signals = ("MinionGotHealed", "HeroGotHealed", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject.ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.giveEnchant(self.keeper, statEnchant=Enchantment_Cumulative(1, 0, name=CrimsonClergy))


class Trig_ManaTideTotem(TrigBoard):
	signals = ("TurnEnds", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.Game.Hand_Deck.drawCard(self.keeper.ID)


class Trig_UnboundElemental(TrigBoard):
	signals = ("MinionPlayed", "SpellPlayed", "WeaponPlayed", "HeroCardPlayed", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject.ID == self.keeper.ID and subject.overload > 0

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.giveEnchant(self.keeper, statEnchant=Enchantment_Cumulative(1, 1, name=UnboundElemental))


class Trig_TinyKnightofEvil(TrigBoard):
	signals = ("CardDiscarded", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.giveEnchant(self.keeper, statEnchant=Enchantment_Cumulative(1, 1, name=TinyKnightofEvil))


class Trig_WarsongCommander(TrigBoard):
	signals = ("MinionSummoned", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject.ID == self.keeper.ID and subject != self.keeper

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.giveEnchant(subject, effectEnchant=Enchantment_Cumulative(effGain="Rush", name=WarsongCommander))


class Trig_Armorsmith(TrigBoard):
	signals = ("MinionTakesDmg", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and target.ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.giveHeroAttackArmor(self.keeper.ID, armor=1)
		
		
class Trig_FrothingBerserker(TrigBoard):
	signals = ("MinionTakesDmg", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.giveEnchant(self.keeper, statEnchant=Enchantment_Cumulative(1, 0, name=FrothingBerserker))


class Trig_Gorehowl(TrigBoard):
	signals = ("HeroAttackingMinion", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.keeper.Game.heroes[self.keeper.ID] and target.category == "Minion" and self.keeper.onBoard and self.keeper.attack > 1

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.losesAtkInstead = True


"""Neutral Cards"""
class MurlocTinyfin(Minion):
	Class, race, name = "Neutral", "Murloc", "Murloc Tinyfin"
	mana, attack, health = 0, 1, 1
	index = "CORE~Neutral~Minion~0~1~1~Murloc~Murloc Tinyfin"
	requireTarget, effects, description = False, "", ""
	name_CN = "鱼人宝宝"


class AbusiveSergeant(Minion):
	Class, race, name = "Neutral", "", "Abusive Sergeant"
	mana, attack, health = 1, 1, 1
	index = "CORE~Neutral~Minion~1~1~1~~Abusive Sergeant~Battlecry"
	requireTarget, effects, description = True, "", "Battlecry: Give a minion +2 Attack this turn"
	name_CN = "叫嚣的中士"

	def targetExists(self, choice=0):
		return self.selectableMinionExists()

	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target != self and target.onBoard

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.giveEnchant(target, statEnchant=Enchantment(2, 0, until=0, name=AbusiveSergeant))
		return target


class ArcaneAnomaly(Minion):
	Class, race, name = "Neutral", "Elemental", "Arcane Anomaly"
	mana, attack, health = 1, 2, 1
	index = "CORE~Neutral~Minion~1~2~1~Elemental~Arcane Anomaly"
	requireTarget, effects, description = False, "", "After you cast a spell, give this minion +1 Health"
	name_CN = "奥术畸体"
	trigBoard = Trig_ArcaneAnomaly


class ArgentSquire(Minion):
	Class, race, name = "Neutral", "", "Argent Squire"
	mana, attack, health = 1, 1, 1
	index = "CORE~Neutral~Minion~1~1~1~~Argent Squire~Divine Shield"
	requireTarget, effects, description = False, "Divine Shield", "Divine Shield"
	name_CN = "银色侍从"


class Cogmaster(Minion):
	Class, race, name = "Neutral", "", "Cogmaster"
	mana, attack, health = 1, 1, 2
	index = "CORE~Neutral~Minion~1~1~2~~Cogmaster"
	requireTarget, effects, description = False, "", "Has +2 Attack while you have a Mech"
	name_CN = "齿轮大师"
	trigBoard = Trig_Cogmaster
	def statCheckResponse(self):
		if self.onBoard and not self.silenced and any("Mech" in minion.race for minion in self.Game.minionsonBoard(self.ID)):
			self.attack += 2


class ElvenArcher(Minion):
	Class, race, name = "Neutral", "", "Elven Archer"
	mana, attack, health = 1, 1, 1
	index = "CORE~Neutral~Minion~1~1~1~~Elven Archer~Battlecry"
	requireTarget, effects, description = True, "", "Battlecry: Deal 1 damamge"
	name_CN = "精灵弓箭手"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.dealsDamage(target, 1)
		return target


class MurlocTidecaller(Minion):
	Class, race, name = "Neutral", "Murloc", "Murloc Tidecaller"
	mana, attack, health = 1, 1, 2
	index = "CORE~Neutral~Minion~1~1~2~Murloc~Murloc Tidecaller"
	requireTarget, effects, description = False, "", "Whenever you summon a Murloc, gain +1 Attack"
	name_CN = "鱼人招潮者"
	trigBoard = Trig_MurlocTidecaller


class EmeraldSkytalon(Minion):
	Class, race, name = "Neutral", "Beast", "Emerald Skytalon"
	mana, attack, health = 1, 2, 1
	index = "CORE~Neutral~Minion~1~2~1~Beast~Emerald Skytalon~Rush"
	requireTarget, effects, description = False, "Rush", "Rush"
	name_CN = "翡翠天爪枭"


class VoodooDoctor(Minion):
	Class, race, name = "Neutral", "", "Voodoo Doctor"
	mana, attack, health = 1, 2, 1
	index = "CORE~Neutral~Minion~1~2~1~~Voodoo Doctor~Battlecry"
	requireTarget, effects, description = True, "", "Battlecry: Restore 2 health"
	name_CN = "巫医"
	def text(self): return self.calcHeal(2)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.restoresHealth(target, self.calcHeal(2))
		return target


class WorgenInfiltrator(Minion):
	Class, race, name = "Neutral", "", "Worgen Infiltrator"
	mana, attack, health = 1, 2, 1
	index = "CORE~Neutral~Minion~1~2~1~~Worgen Infiltrator~Stealth"
	requireTarget, effects, description = False, "Stealth", "Stealth"
	name_CN = "狼人渗透者"


class YoungPriestess(Minion):
	Class, race, name = "Neutral", "", "Young Priestess"
	mana, attack, health = 1, 2, 1
	index = "CORE~Neutral~Minion~1~2~1~~Young Priestess"
	requireTarget, effects, description = False, "", "At the end of your turn, give another random friendly minion +1 Health"
	name_CN = "年轻的女祭司"
	trigBoard = Trig_YoungPriestess


class AcidicSwampOoze(Minion):
	Class, race, name = "Neutral", "", "Acidic Swamp Ooze"
	mana, attack, health = 2, 3, 2
	index = "CORE~Neutral~Minion~2~3~2~~Acidic Swamp Ooze~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Destroy you opponent's weapon"
	name_CN = "酸性沼泽软泥怪"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.kill(self, self.Game.weapons[3 - self.ID])
		

class AnnoyoTron(Minion):
	Class, race, name = "Neutral", "Mech", "Annoy-o-Tron"
	mana, attack, health = 2, 1, 2
	index = "CORE~Neutral~Minion~2~1~2~Mech~Annoy-o-Tron~Taunt~Divine Shield"
	requireTarget, effects, description = False, "Taunt,Divine Shield", "Taunt. Divine Shield"
	name_CN = "吵吵机器人"


class BloodmageThalnos(Minion):
	Class, race, name = "Neutral", "", "Bloodmage Thalnos"
	mana, attack, health = 2, 1, 1
	index = "CORE~Neutral~Minion~2~1~1~~Bloodmage Thalnos~Deathrattle~Spell Damage~Legendary"
	requireTarget, effects, description = False, "Spell Damage", "Spell Damage +1. Deathrattle: Draw a card"
	name_CN = "血法师萨尔诺斯"
	deathrattle = Death_BloodmageThalnos


class BloodsailRaider(Minion):
	Class, race, name = "Neutral", "Pirate", "Bloodsail Raider"
	mana, attack, health = 2, 2, 3
	index = "CORE~Neutral~Minion~2~2~3~Pirate~Bloodsail Raider~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Gain Attack equal to the Attack of your weapon"
	name_CN = "血帆袭击者"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if weapon := self.Game.availableWeapon(self.ID): self.giveEnchant(self, weapon.attack, 0, name=BloodsailRaider)


class CrazedAlchemist(Minion):
	Class, race, name = "Neutral", "", "Crazed Alchemist"
	mana, attack, health = 2, 2, 2
	index = "CORE~Neutral~Minion~2~2~2~~Crazed Alchemist~Battlecry"
	requireTarget, effects, description = True, "", "Battlecry: Swap the Attack and Health of a minion"
	name_CN = "疯狂的炼金师"

	def targetExists(self, choice=0):
		return self.selectableMinionExists()

	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target != self and target.onBoard

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.setStat(target, target.health, target.attack, name=CrazedAlchemist)
		return target


class DireWolfAlpha(Minion):
	Class, race, name = "Neutral", "Beast", "Dire Wolf Alpha"
	mana, attack, health = 2, 2, 2
	index = "CORE~Neutral~Minion~2~2~2~Beast~Dire Wolf Alpha"
	requireTarget, effects, description = False, "", "Adjacent minions have +1 Attack"
	name_CN = "恐狼先锋"
	aura = Aura_DireWolfAlpha


class ExplosiveSheep(Minion):
	Class, race, name = "Neutral", "Mech", "Explosive Sheep"
	mana, attack, health = 2, 1, 1
	index = "CORE~Neutral~Minion~2~1~1~Mech~Explosive Sheep~Deathrattle"
	requireTarget, effects, description = False, "", "Deathrattle: Deal 2 damage to all minions"
	name_CN = "自爆绵羊"
	deathrattle = Death_ExplosiveSheep


class FogsailFreebooter(Minion):
	Class, race, name = "Neutral", "Pirate", "Fogsail Freebooter"
	mana, attack, health = 2, 2, 2
	index = "CORE~Neutral~Minion~2~2~2~Pirate~Fogsail Freebooter~Battlecry"
	requireTarget, effects, description = True, "", "Battlecry: If you have a weapon equipped, deal 2 damage"
	name_CN = "雾帆劫掠者"

	def needTarget(self, choice=0):
		return self.Game.availableWeapon(self.ID) is not None

	def effCanTrig(self):
		self.effectViable = self.Game.availableWeapon(self.ID) is not None

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and self.Game.availableWeapon(self.ID): self.dealsDamage(target, 2)
		return target


class KoboldGeomancer(Minion):
	Class, race, name = "Neutral", "", "Kobold Geomancer"
	mana, attack, health = 2, 2, 2
	index = "CORE~Neutral~Minion~2~2~2~~Kobold Geomancer~Spell Damage"
	requireTarget, effects, description = False, "Spell Damage", "Spell Damage +1"
	name_CN = "狗头人地卜师"


class LootHoarder(Minion):
	Class, race, name = "Neutral", "", "Loot Hoarder"
	mana, attack, health = 2, 2, 1
	index = "CORE~Neutral~Minion~2~2~1~~Loot Hoarder~Deathrattle"
	requireTarget, effects, description = False, "", "Deathrattle: Draw a card"
	name_CN = "战利品贮藏者"
	deathrattle = Death_LootHoarder


class MadBomber(Minion):
	Class, race, name = "Neutral", "", "Mad Bomber"
	mana, attack, health = 2, 3, 2
	index = "CORE~Neutral~Minion~2~3~2~~Mad Bomber~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Deal 3 damage randomly split among all other characters"
	name_CN = "疯狂投弹者"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for _ in (0, 1, 2):
			if chars := self.Game.charsAlive(self.ID, self) + self.Game.charsAlive(3-self.ID):
				self.dealsDamage(numpyChoice(chars), 1)
			else: break


class MurlocTidehunter(Minion):
	Class, race, name = "Neutral", "Murloc", "Murloc Tidehunter"
	mana, attack, health = 2, 2, 1
	index = "CORE~Neutral~Minion~2~2~1~Murloc~Murloc Tidehunter~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Summon a 1/1 Murloc Scout"
	name_CN = "鱼人猎潮者"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon(MurlocScout(self.Game, self.ID))
		
class MurlocScout(Minion):
	Class, race, name = "Neutral", "Murloc", "Murloc Scout"
	mana, attack, health = 1, 1, 1
	index = "CORE~Neutral~Minion~1~1~1~Murloc~Murloc Scout~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "鱼人斥候"


class NerubianEgg(Minion):
	Class, race, name = "Neutral", "", "Nerubian Egg"
	mana, attack, health = 2, 0, 2
	index = "CORE~Neutral~Minion~2~0~2~~Nerubian Egg~Deathrattle"
	requireTarget, effects, description = False, "", "Deathrattle: Summon a 4/4 Nerubian"
	name_CN = "蛛魔之卵"
	deathrattle = Death_NerubianEgg


class RedgillRazorjaw(Minion):
	Class, race, name = "Neutral", "Murloc", "Redgill Razorjaw"
	mana, attack, health = 2, 3, 1
	index = "CORE~Neutral~Minion~2~3~1~Murloc~Redgill Razorjaw~Rush"
	requireTarget, effects, description = False, "Rush", "Rush"
	name_CN = "红鳃锋颚战士"


class RiverCrocolisk(Minion):
	Class, race, name = "Neutral", "Beast", "River Crocolisk"
	mana, attack, health = 2, 2, 3
	index = "CORE~Neutral~Minion~2~2~3~Beast~River Crocolisk"
	requireTarget, effects, description = False, "", ""
	name_CN = "淡水鳄"


class SunreaverSpy(Minion):
	Class, race, name = "Neutral", "", "Sunreaver Spy"
	mana, attack, health = 2, 2, 3
	index = "CORE~Neutral~Minion~2~2~3~~Sunreaver Spy~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: If you control a Secret, gain +1/+1"
	name_CN = "夺日者间谍"

	def effCanTrig(self):
		self.effectViable = self.Game.Secrets.secrets[self.ID] != []

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Secrets.secrets[self.ID]: self.giveEnchant(self, 1, 1, name=SunreaverSpy)


class Toxicologist(Minion):
	Class, race, name = "Neutral", "", "Toxicologist"
	mana, attack, health = 2, 2, 2
	index = "CORE~Neutral~Minion~2~2~2~~Toxicologist~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Give your weapon +1 Attack"
	name_CN = "毒物学家"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if weapon := self.Game.availableWeapon(self.ID): self.giveEnchant(weapon, 1, 0, name=Toxicologist)


class YouthfulBrewmaster(Minion):
	Class, race, name = "Neutral", "", "Youthful Brewmaster"
	mana, attack, health = 2, 3, 2
	index = "CORE~Neutral~Minion~2~3~2~~Youthful Brewmaster~Battlecry"
	requireTarget, effects, description = True, "", "Battlecry: Return a friendly minion from the battlefield to you hand"
	name_CN = "年轻的酒仙"

	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()

	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.ID == self.ID and target != self and target.onBoard

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and target.onBoard: self.Game.returnObj2Hand(target)
		return target


class Brightwing(Minion):
	Class, race, name = "Neutral", "Dragon", "Brightwing"
	mana, attack, health = 3, 3, 2
	index = "CORE~Neutral~Minion~3~3~2~Dragon~Brightwing~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: Add a random Legendary minion to your hand"
	name_CN = "光明之翼"
	poolIdentifier = "Legendary Minions"
	@classmethod
	def generatePool(cls, pools):
		return "Legendary Minions", pools.LegendaryMinions

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.addCardtoHand(numpyChoice(self.rngPool("Legendary Minions")), self.ID)


class ColdlightSeer(Minion):
	Class, race, name = "Neutral", "Murloc", "Coldlight Seer"
	mana, attack, health = 3, 2, 3
	index = "CORE~Neutral~Minion~3~2~3~Murloc~Coldlight Seer~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Give your other Murlocs +2 Health"
	name_CN = "寒光先知"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.AOE_GiveEnchant(self.Game.minionsonBoard(self.ID, self, race="Murloc"), 0, 2, name=ColdlightSeer)


class EarthenRingFarseer(Minion):
	Class, race, name = "Neutral", "", "Earthen Ring Farseer"
	mana, attack, health = 3, 3, 3
	index = "CORE~Neutral~Minion~3~3~3~~Earthen Ring Farseer~Battlecry"
	requireTarget, effects, description = True, "", "Battlecry: Restore 3 health"
	name_CN = "大地之环先知"
	def text(self): return self.calcHeal(3)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.restoresHealth(target, self.calcHeal(3))
		return target


class FlesheatingGhoul(Minion):
	Class, race, name = "Neutral", "", "Flesheating Ghoul"
	mana, attack, health = 3, 3, 3
	index = "CORE~Neutral~Minion~3~3~3~~Flesheating Ghoul"
	requireTarget, effects, description = False, "", "Whenever a minion dies, gain +1 Attack"
	name_CN = "腐肉食尸鬼"
	trigBoard = Trig_FlesheatingGhoul


class HumongousRazorleaf(Minion):
	Class, race, name = "Neutral", "", "Humongous Razorleaf"
	mana, attack, health = 3, 4, 8
	index = "CORE~Neutral~Minion~3~4~8~~Humongous Razorleaf"
	requireTarget, effects, description = False, "Can't Attack", "Can't Attack"
	name_CN = "巨齿刀叶"


class IceRager(Minion):
	Class, race, name = "Neutral", "Elemental", "Ice Rager"
	mana, attack, health = 3, 5, 2
	index = "CORE~Neutral~Minion~3~5~2~Elemental~Ice Rager"
	requireTarget, effects, description = False, "", ""
	name_CN = "冰霜暴怒者"


class InjuredBlademaster(Minion):
	Class, race, name = "Neutral", "", "Injured Blademaster"
	mana, attack, health = 3, 4, 7
	index = "CORE~Neutral~Minion~3~4~7~~Injured Blademaster~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Deal 4 damage to HIMSELF"
	name_CN = "负伤剑圣"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.dealsDamage(self, 4)


class IronbeakOwl(Minion):
	Class, race, name = "Neutral", "Beast", "Ironbeak Owl"
	mana, attack, health = 3, 2, 1
	index = "CORE~Neutral~Minion~3~2~1~Beast~Ironbeak Owl~Battlecry"
	requireTarget, effects, description = True, "", "Battlecry: Silence a minion"
	name_CN = "铁喙猫头鹰"

	def targetExists(self, choice=0):
		return self.selectableMinionExists()

	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target != self and target.onBoard

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.getsSilenced()
		return target


class JunglePanther(Minion):
	Class, race, name = "Neutral", "Beast", "Jungle Panther"
	mana, attack, health = 3, 4, 2
	index = "CORE~Neutral~Minion~3~4~2~Beast~Jungle Panther~Stealth"
	requireTarget, effects, description = False, "Stealth", "Stealth"
	name_CN = "丛林猎豹"


class KingMukla(Minion):
	Class, race, name = "Neutral", "Beast", "King Mukla"
	mana, attack, health = 3, 5, 5
	index = "CORE~Neutral~Minion~3~5~5~Beast~King Mukla~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: Give your opponent 2 Bananas"
	name_CN = "穆克拉"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.addCardtoHand([Bananas, Bananas], 3-self.ID)


class LoneChampion(Minion):
	Class, race, name = "Neutral", "", "Lone Champion"
	mana, attack, health = 3, 2, 4
	index = "CORE~Neutral~Minion~3~2~4~~Lone Champion~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: If you control no other minions, gain Taunt and Divine Shield"
	name_CN = "孤胆英雄"

	def effCanTrig(self):
		self.effectViable = self.Game.minionsonBoard(self.ID) == []

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if len(self.Game.minionsonBoard(self.ID)) < 2:
			self.giveEnchant(self, multipleEffGains=(("Taunt", 1, None), ("Divine Shield", 1, None)), name=LoneChampion)


class MiniMage(Minion):
	Class, race, name = "Neutral", "", "Mini-Mage"
	mana, attack, health = 3, 3, 1
	index = "CORE~Neutral~Minion~3~3~1~~Mini-Mage~Stealth~Spell Damage"
	requireTarget, effects, description = False, "Stealth,Spell Damage", "Stealth, Spell Damage +1"
	name_CN = "小个子法师"


class RaidLeader(Minion):
	Class, race, name = "Neutral", "", "Raid Leader"
	mana, attack, health = 3, 2, 3
	index = "CORE~Neutral~Minion~3~2~3~~Raid Leader"
	requireTarget, effects, description = False, "", "Your other minions have +1 Attack"
	name_CN = "团队领袖"
	aura = Aura_RaidLeader


class SouthseaCaptain(Minion):
	Class, race, name = "Neutral", "Pirate", "Southsea Captain"
	mana, attack, health = 3, 3, 3
	index = "CORE~Neutral~Minion~3~3~3~Pirate~Southsea Captain"
	requireTarget, effects, description = False, "", "Your other Pirates have +1/+1"
	name_CN = "南海船长"
	aura = Aura_SouthseaCaptain


class SpiderTank(Minion):
	Class, race, name = "Neutral", "Mech", "Spider Tank"
	mana, attack, health = 3, 3, 4
	index = "CORE~Neutral~Minion~3~3~4~Mech~Spider Tank"
	requireTarget, effects, description = False, "", ""
	name_CN = "蜘蛛坦克"


class StoneskinBasilisk(Minion):
	Class, race, name = "Neutral", "Beast", "Stoneskin Basilisk"
	mana, attack, health = 3, 1, 1
	index = "CORE~Neutral~Minion~3~1~1~Beast~Stoneskin Basilisk~Divine Shield~Poisonous"
	requireTarget, effects, description = False, "Divine Shield,Poisonous", "Divine Shield, Poisonous"
	name_CN = "石皮蜥蜴"


class BaronRivendare(Minion):
	Class, race, name = "Neutral", "", "Baron Rivendare"
	mana, attack, health = 4, 1, 7
	index = "CORE~Neutral~Minion~4~1~7~~Baron Rivendare~Legendary"
	requireTarget, effects, description = False, "", "Your minions trigger their Deathrattles twice"
	name_CN = "瑞文戴尔男爵"
	aura = GameRuleAura_BaronRivendare


class BigGameHunter(Minion):
	Class, race, name = "Neutral", "", "Big Game Hunter"
	mana, attack, health = 4, 4, 2
	index = "CORE~Neutral~Minion~4~4~2~~Big Game Hunter~Battlecry"
	requireTarget, effects, description = True, "", "Battlecry: Destroy a minion with 7 or more Attack"
	name_CN = "王牌猎人"

	def targetExists(self, choice=0):
		return self.selectableMinionExists()

	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target != self and target.attack > 6 and target.onBoard

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.Game.kill(self, target)
		return target


class ChillwindYeti(Minion):
	Class, race, name = "Neutral", "", "Chillwind Yeti"
	mana, attack, health = 4, 4, 5
	index = "CORE~Neutral~Minion~4~4~5~~Chillwind Yeti"
	requireTarget, effects, description = False, "", ""
	name_CN = "冰风雪人"


class DarkIronDwarf(Minion):
	Class, race, name = "Neutral", "", "Dark Iron Dwarf"
	mana, attack, health = 4, 4, 4
	index = "CORE~Neutral~Minion~4~4~4~~Dark Iron Dwarf~Battlecry"
	requireTarget, effects, description = True, "", "Battlecry: Give a minion +2 Attack"
	name_CN = "黑铁矮人"

	def targetExists(self, choice=0):
		return self.selectableMinionExists()

	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target != self and target.onBoard

	#手牌中的随从也会受到临时一回合的加攻，回合结束时消失。
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.giveEnchant(target, 2, 0, statEnchant=Enchantment(2, 0, until=0, name=DarkIronDwarf))
		return target


class DefenderofArgus(Minion):
	Class, race, name = "Neutral", "", "Defender of Argus"
	mana, attack, health = 4, 3, 3
	index = "CORE~Neutral~Minion~4~3~3~~Defender of Argus~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Given adjacent minions +1/+1 and Taunt"
	name_CN = "阿古斯防御者"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.onBoard: self.AOE_GiveEnchant(self.Game.neighbors2(self)[0], 1, 1, effGain="Taunt", name=DefenderofArgus)


class GrimNecromancer(Minion):
	Class, race, name = "Neutral", "", "Grim Necromancer"
	mana, attack, health = 4, 2, 4
	index = "CORE~Neutral~Minion~4~2~4~~Grim Necromancer~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Summon two 1/1 Skeletons"
	name_CN = "冷酷的死灵法师"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon([Skeleton(self.Game, self.ID) for _ in (0, 1)], relative="<>")


class SenjinShieldmasta(Minion):
	Class, race, name = "Neutral", "", "Sen'jin Shieldmasta"
	mana, attack, health = 4, 3, 5
	index = "CORE~Neutral~Minion~4~3~5~~Sen'jin Shieldmasta~Taunt"
	requireTarget, effects, description = False, "Taunt", "Taunt"
	name_CN = "森金持盾卫士"


class SI7Infiltrator(Minion):
	Class, race, name = "Neutral", "", "SI:7 Infiltrator"
	mana, attack, health = 4, 5, 4
	index = "CORE~Neutral~Minion~4~5~4~~SI:7 Infiltrator~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Destroy a random enemy Secret"
	name_CN = "军情七处渗透者"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if numSecrets := len(self.Game.Secrets.secrets[3-self.ID]):
			self.Game.Secrets.extractSecrets(3-self.ID, numpyRandint(numSecrets), initiator=self)


class VioletTeacher(Minion):
	Class, race, name = "Neutral", "", "Violet Teacher"
	mana, attack, health = 4, 3, 5
	index = "CORE~Neutral~Minion~4~3~5~~Violet Teacher"
	requireTarget, effects, description = False, "", "Whenever you cast a spell, summon a 1/1 Violet Apperentice"
	name_CN = "紫罗兰教师"
	trigBoard = Trig_VioletTeacher


class FacelessManipulator(Minion):
	Class, race, name = "Neutral", "", "Faceless Manipulator"
	mana, attack, health = 5, 3, 3
	index = "CORE~Neutral~Minion~5~3~3~~Faceless Manipulator~Battlecry"
	requireTarget, effects, description = True, "", "Battlecry: Choose a minion and become a copy of it"
	name_CN = "无面操纵者"

	def targetExists(self, choice=0):
		return self.selectableMinionExists()

	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target != self and target.onBoard

	#无面上场时，先不变形，正常触发Illidan的召唤，以及飞刀。之后进行判定。如果无面在战吼触发前死亡，则没有变形发生。
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		#目前只有打随从从手牌打出或者被沙德沃克调用可以触发随从的战吼。这些手段都要涉及self.Game.minionPlayed
		#如果self.Game.minionPlayed不再等于自己，说明这个随从的已经触发了变形而不会再继续变形。
		if target and not self.dead and self.Game.minionPlayed == self and (self.onBoard or self.inHand): #战吼触发时自己不能死亡。
			Copy = target.selfCopy(self.ID, self) if (target.onBoard or target.inHand) and self.onBoard else type(target)(self.Game, self.ID)
			self.Game.transform(self, Copy)
		return target


class GurubashiBerserker(Minion):
	Class, race, name = "Neutral", "", "Gurubashi Berserker"
	mana, attack, health = 5, 2, 8
	index = "CORE~Neutral~Minion~5~2~8~~Gurubashi Berserker"
	requireTarget, effects, description = False, "", "Whenever this minion takes damage, gain +3 Attack"
	name_CN = "古拉巴什狂暴者"
	trigBoard = Trig_GurubashiBerserker


class OverlordRunthak(Minion):
	Class, race, name = "Neutral", "", "Overlord Runthak"
	mana, attack, health = 5, 3, 6
	index = "CORE~Neutral~Minion~5~3~6~~Overlord Runthak~Rush~Legendary"
	requireTarget, effects, description = False, "Rush", "Rush. Whenever this minion attacks, give +1/+1 to all minions in your hand"
	name_CN = "伦萨克大王"
	trigBoard = Trig_OverlordRunthak


class StranglethornTiger(Minion):
	Class, race, name = "Neutral", "Beast", "Stranglethorn Tiger"
	mana, attack, health = 5, 5, 5
	index = "CORE~Neutral~Minion~5~5~5~Beast~Stranglethorn Tiger~Stealth"
	requireTarget, effects, description = False, "Stealth", "Stealth"
	name_CN = "荆棘谷猛虎"


class TaelanFordring(Minion):
	Class, race, name = "Neutral", "", "Taelan Fordring"
	mana, attack, health = 5, 3, 3
	index = "CORE~Neutral~Minion~5~3~3~~Taelan Fordring~Taunt~Divine Shield~Deathrattle~Legendary"
	requireTarget, effects, description = False, "Taunt,Divine Shield", "Taunt, Divine Shield. Deathrattle: Draw your hightest-Cost minion"
	name_CN = "泰兰·弗丁"
	deathrattle = Death_TaelanFordring


class CairneBloodhoof(Minion):
	Class, race, name = "Neutral", "", "Cairne Bloodhoof"
	mana, attack, health = 6, 5, 5
	index = "CORE~Neutral~Minion~6~5~5~~Cairne Bloodhoof~Deathrattle~Legendary"
	requireTarget, effects, description = False, "", "Deathrattle: Summon a 4/5 Baine Bloodhoof"
	name_CN = "凯恩·血蹄"
	deathrattle = Death_CairneBloodhoof


class GadgetzanAuctioneer(Minion):
	Class, race, name = "Neutral", "", "Gadgetzan Auctioneer"
	mana, attack, health = 6, 4, 4
	index = "CORE~Neutral~Minion~6~4~4~~Gadgetzan Auctioneer"
	requireTarget, effects, description = False, "", "Whenever you cast a spell, draw a card"
	name_CN = "加基森拍卖师"
	trigBoard = Trig_GadgetzanAuctioneer


class HighInquisitorWhitemane(Minion):
	Class, race, name = "Neutral", "", "High Inquisitor Whitemane"
	mana, attack, health = 6, 5, 7
	index = "CORE~Neutral~Minion~6~5~7~~High Inquisitor Whitemane~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: Summon all friendly minions that died this turn"
	name_CN = "大检察官怀特迈恩"

	def effCanTrig(self):
		self.effectViable = self.Game.Counters.minionsDiedThisTurn[self.ID] != []

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		minionsDied = self.Game.Counters.minionsDiedThisTurn[self.ID]
		if numSummon := min(self.Game.space(self.ID), len(minionsDied)):  #假设召唤顺序是随机的
			self.summon([minion(self.Game, self.ID) for minion in numpyChoice(minionsDied, numSummon, replace=False)])


class BaronGeddon(Minion):
	Class, race, name = "Neutral", "Elemental", "Baron Geddon"
	mana, attack, health = 7, 7, 7
	index = "CORE~Neutral~Minion~7~7~7~Elemental~Baron Geddon~Legendary"
	requireTarget, effects, description = False, "", "At the end of turn, deal 2 damage to ALL other characters"
	name_CN = "迦顿男爵"
	trigBoard = Trig_BaronGeddon


class BarrensStablehand(Minion):
	Class, race, name = "Neutral", "", "Barrens Stablehand"
	mana, attack, health = 7, 5, 5
	index = "CORE~Neutral~Minion~7~5~5~~Barrens Stablehand~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Summon a random Beast"
	name_CN = "贫瘠之地饲养员"
	poolIdentifier = "Beasts to Summon"
	@classmethod
	def generatePool(cls, pools):
		return "Beasts to Summon", pools.MinionswithRace["Beast"]

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon(numpyChoice(self.rngPool("Beasts to Summon"))(self.Game, self.ID))


class NozdormutheEternal(Minion):
	Class, race, name = "Neutral", "Dragon", "Nozdormu the Eternal"
	mana, attack, health = 7, 8, 8
	index = "CORE~Neutral~Minion~7~8~8~Dragon~Nozdormu the Eternal~Legendary"
	requireTarget, effects, description = False, "", "Start of Game: If this is in BOTH players' decks, turns are only 15 seconds long"
	name_CN = "永恒者诺兹多姆"


class Stormwatcher(Minion):
	Class, race, name = "Neutral", "Elemental", "Stormwatcher"
	mana, attack, health = 7, 4, 8
	index = "CORE~Neutral~Minion~7~4~8~Elemental~Stormwatcher~Windfury"
	requireTarget, effects, description = False, "Windfury", "Windfury"
	name_CN = "风暴看守"


class StormwindChampion(Minion):
	Class, race, name = "Neutral", "", "Stormwind Champion"
	mana, attack, health = 7, 7, 7
	index = "CORE~Neutral~Minion~7~7~7~~Stormwind Champion"
	requireTarget, effects, description = False, "", "Your other minions have +1/+1"
	name_CN = "暴风城勇士"
	aura = Aura_StormwindChampion


class ArcaneDevourer(Minion):
	Class, race, name = "Neutral", "Elemental", "Arcane Devourer"
	mana, attack, health = 8, 4, 8
	index = "CORE~Neutral~Minion~8~4~8~Elemental~Arcane Devourer"
	requireTarget, effects, description = False, "", "Whenever you cast a spell, gain +2/+2"
	name_CN = "奥术吞噬者"
	trigBoard = Trig_ArcaneDevourer


class AlexstraszatheLifeBinder(Minion):
	Class, race, name = "Neutral", "Dragon", "Alexstrasza the Life-Binder"
	mana, attack, health = 9, 8, 8
	index = "CORE~Neutral~Minion~9~8~8~Dragon~Alexstrasza the Life-Binder~Battlecry~Legendary"
	requireTarget, effects, description = True, "", "Battlecry: Choose a character. If it's friendly, restore 8 Health. If it's an enemy, deal 8 damage"
	name_CN = "生命的缚誓者阿莱克丝塔萨"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			if target.ID == self.ID: self.restoresHealth(target, self.calcHeal(8))
			else: self.dealsDamage(target, 8)
		return target


class MalygostheSpellweaver(Minion):
	Class, race, name = "Neutral", "Dragon", "Malygos the Spellweaver"
	mana, attack, health = 9, 4, 12
	index = "CORE~Neutral~Minion~9~4~12~Dragon~Malygos the Spellweaver~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: Draw spells until your hand is full"
	name_CN = "织法者玛里苟斯"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		while self.Game.Hand_Deck.handNotFull(self.ID):
			if not self.drawCertainCard(lambda card: card.category == "Spell")[0]: break


class OnyxiatheBroodmother(Minion):
	Class, race, name = "Neutral", "Dragon", "Onyxia the Broodmother"
	mana, attack, health = 9, 8, 8
	index = "CORE~Neutral~Minion~9~8~8~Dragon~Onyxia the Broodmother~Legendary"
	requireTarget, effects, description = False, "", "At the end of your turn, fill your board with 1/1 Whelps"
	name_CN = "龙巢之母奥妮克希亚"
	trigBoard = Trig_OnyxiatheBroodmother


class SleepyDragon(Minion):
	Class, race, name = "Neutral", "Dragon", "Sleepy Dragon"
	mana, attack, health = 9, 4, 12
	index = "CORE~Neutral~Minion~9~4~12~Dragon~Sleepy Dragon~Taunt"
	requireTarget, effects, description = False, "Taunt", "Taunt"
	name_CN = "贪睡巨龙"


class YseratheDreamer(Minion):
	Class, race, name = "Neutral", "Dragon", "Ysera the Dreamer"
	mana, attack, health = 9, 4, 12
	index = "CORE~Neutral~Minion~9~4~12~Dragon~Ysera the Dreamer~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: Add one of each Dream card to your hand"
	name_CN = "沉睡者伊瑟拉"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.addCardtoHand([Dream, Nightmare, YseraAwakens, LaughingSister, EmeraldDrake], self.ID)


class DeathwingtheDestroyer(Minion):
	Class, race, name = "Neutral", "Dragon", "Deathwing the Destroyer"
	mana, attack, health = 10, 12, 12
	index = "CORE~Neutral~Minion~10~12~12~Dragon~Deathwing the Destroyer~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: Destroy all other minions. Discard a card for each destroyed"
	name_CN = "灭世者死亡之翼"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		ID, game = self.ID, self.Game
		game.kill(self, (minions := game.minionsAlive(ID, self) + game.minionsAlive(3 - ID)))
		ownHand = game.Hand_Deck.hands[ID]
		for num in range(len(minions)):
			if ownHand: game.Hand_Deck.discard(ID, numpyRandint(len(ownHand)))
			else: break


class ClockworkGiant(Minion):
	Class, race, name = "Neutral", "Mech", "Clockwork Giant"
	mana, attack, health = 12, 8, 8
	index = "CORE~Neutral~Minion~12~8~8~Mech~Clockwork Giant"
	requireTarget, effects, description = False, "", "Costs (1) less for each other card in your opponent's hand"
	name_CN = "发条巨人"
	trigHand = Trig_ClockworkGiant
	def selfManaChange(self):
		if self.inHand:
			self.mana -= len(self.Game.Hand_Deck.hands[3-self.ID])
			self.mana = max(0, self.mana)


"""Demon Hunter Cards"""
class Battlefiend(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Battlefiend"
	mana, attack, health = 1, 1, 2
	index = "CORE~Demon Hunter~Minion~1~1~2~Demon~Battlefiend"
	requireTarget, effects, description = False, "", "After your hero attacks, gain +1 Attack"
	name_CN = "战斗邪犬"
	trigBoard = Trig_Battlefiend


class ChaosStrike(Spell):
	Class, school, name = "Demon Hunter", "Fel", "Chaos Strike"
	requireTarget, mana, effects = False, 2, ""
	index = "CORE~Demon Hunter~Spell~2~Fel~Chaos Strike"
	description = "Give your hero +2 Attack this turn. Draw a card"
	name_CN = "混乱打击"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.giveHeroAttackArmor(self.ID, attGain=2, name=ChaosStrike)
		self.Game.Hand_Deck.drawCard(self.ID)


class CrimsonSigilRunner(Minion):
	Class, race, name = "Demon Hunter", "", "Crimson Sigil Runner"
	mana, attack, health = 1, 1, 1
	index = "CORE~Demon Hunter~Minion~1~1~1~~Crimson Sigil Runner~Outcast"
	requireTarget, effects, description = False, "", "Outcast: Draw a card"
	name_CN = "火色魔印奔行者"

	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.outcastcanTrig(self)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if posinHand == 0 or posinHand == -1:
			self.Game.Hand_Deck.drawCard(self.ID)


class FeastofSouls(Spell):
	Class, school, name = "Demon Hunter", "Shadow", "Feast of Souls"
	requireTarget, mana, effects = False, 2, ""
	index = "CORE~Demon Hunter~Spell~2~Shadow~Feast of Souls"
	description = "Draw a card for each friendly minion that died this turn"
	name_CN = "灵魂盛宴"
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.minionsDiedThisTurn[self.ID] != []

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		num = len(self.Game.Counters.minionsDiedThisTurn[self.ID])
		for i in range(num): self.Game.Hand_Deck.drawCard(self.ID)


class KorvasBloodthorn(Minion):
	Class, race, name = "Demon Hunter", "", "Kor'vas Bloodthorn"
	mana, attack, health = 2, 2, 2
	index = "CORE~Demon Hunter~Minion~2~2~2~~Kor'vas Bloodthorn~Charge~Lifesteal~Legendary"
	requireTarget, effects, description = False, "Charge,Lifesteal", "Charge, Lifesteal. After you play a card with Outcast, return this to your hand"
	name_CN = "考瓦斯·血棘"
	trigBoard = Trig_KorvasBloodthorn


class SightlessWatcher(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Sightless Watcher"
	mana, attack, health = 2, 3, 2
	index = "CORE~Demon Hunter~Minion~2~3~2~Demon~Sightless Watcher~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Look at 3 cards in your deck. Choose one to put on top"
	name_CN = "盲眼观察者"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverfromCardList(SightlessWatcher, comment)

	def discoverDecided(self, option, case, info_RNGSync=None, info_GUISync=None):
		ownDeck = self.Game.Hand_Deck.decks[self.ID]
		self.handleDiscoveredCardfromList(option, case, ls=ownDeck,
										  func=lambda index, card: ownDeck.append(ownDeck.pop(index)),
										  info_RNGSync=info_RNGSync, info_GUISync=info_GUISync)


class SpectralSight(Spell):
	Class, school, name = "Demon Hunter", "", "Spectral Sight"
	requireTarget, mana, effects = False, 2, ""
	index = "CORE~Demon Hunter~Spell~2~~Spectral Sight~Outcast"
	description = "Draw a cards. Outscast: Draw another"
	name_CN = "幽灵视觉"
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.outcastcanTrig(self)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.Hand_Deck.drawCard(self.ID)
		if posinHand == 0 or posinHand == -1:
			self.Game.Hand_Deck.drawCard(self.ID)


class AldrachiWarblades(Weapon):
	Class, name, description = "Demon Hunter", "Aldrachi Warblades", "Lifesteal"
	mana, attack, durability, effects = 3, 2, 2, "Lifesteal"
	index = "CORE~Demon Hunter~Weapon~3~2~2~Aldrachi Warblades~Lifesteal"
	name_CN = "奥达奇战刃"


class CoordinatedStrike(Spell):
	Class, school, name = "Demon Hunter", "", "Coordinated Strike"
	requireTarget, mana, effects = False, 3, ""
	index = "CORE~Demon Hunter~Spell~3~~Coordinated Strike"
	description = "Summon three 1/1 Illidari with Rush"
	name_CN = "协同打击"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon([IllidariInitiate(self.Game, self.ID) for _ in (0, 1, 2)])


class EyeBeam(Spell):
	Class, school, name = "Demon Hunter", "Fel", "Eye Beam"
	requireTarget, mana, effects = True, 3, "Lifesteal"
	index = "CORE~Demon Hunter~Spell~3~Fel~Eye Beam~Outcast"
	description = "Lifesteal. Deal 3 damage to a minion. Outcast: This costs (1)"
	name_CN = "眼棱"
	trigHand = Trig_EyeBeam
	def available(self):
		return self.selectableMinionExists()

	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard

	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.outcastcanTrig(self)

	def selfManaChange(self):
		if self.inHand:
			posinHand = self.Game.Hand_Deck.hands[self.ID].index(self)
			if posinHand == 0 or posinHand == len(self.Game.Hand_Deck.hands[self.ID]) - 1:
				self.mana = 1

	def text(self): return self.calcDamage(3)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.dealsDamage(target, self.calcDamage(3))
		return target


class GanargGlaivesmith(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Gan'arg Glaivesmith"
	mana, attack, health = 3, 3, 2
	index = "CORE~Demon Hunter~Minion~3~3~2~Demon~Gan'arg Glaivesmith~Outcast"
	requireTarget, effects, description = False, "", "Outcast: Give your hero +3 Attack this turn"
	name_CN = "甘尔葛战刃铸造师"

	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.outcastcanTrig(self)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if posinHand == 0 or posinHand == -1:
			self.giveHeroAttackArmor(self.ID, attGain=3, name=GanargGlaivesmith)


class AshtongueBattlelord(Minion):
	Class, race, name = "Demon Hunter", "", "Ashtongue Battlelord"
	mana, attack, health = 4, 3, 5
	index = "CORE~Demon Hunter~Minion~4~3~5~~Ashtongue Battlelord~Taunt~Lifesteal"
	requireTarget, effects, description = False, "Taunt,Lifesteal", "Taunt, Lifesteal"
	name_CN = "灰舌将领"


class RagingFelscreamer(Minion):
	Class, race, name = "Demon Hunter", "", "Raging Felscreamer"
	mana, attack, health = 4, 4, 4
	index = "CORE~Demon Hunter~Minion~4~4~4~~Raging Felscreamer~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: The next Demon you play costs (2) less"
	name_CN = "暴怒邪吼者"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		GamaManaAura_RagingFelscreamer(self.Game, self.ID).auraAppears()


class ChaosNova(Spell):
	Class, school, name = "Demon Hunter", "Fel", "Chaos Nova"
	requireTarget, mana, effects = False, 5, ""
	index = "CORE~Demon Hunter~Spell~5~Fel~Chaos Nova"
	description = "Deal 4 damage to all minions"
	name_CN = "混乱新星"
	def text(self): return self.calcDamage(4)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		targets, damage = self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2), self.calcDamage(4)
		self.AOE_Damage(targets, [damage]*len(targets))


class WarglaivesofAzzinoth(Weapon):
	Class, name, description = "Demon Hunter", "Warglaives of Azzinoth", "After attacking a minion, your hero may attack again"
	mana, attack, durability, effects = 5, 3, 3, ""
	index = "CORE~Demon Hunter~Weapon~5~3~3~Warglaives of Azzinoth"
	name_CN = "埃辛诺斯战刃"
	trigBoard = Trig_WarglaivesofAzzinoth


class IllidariInquisitor(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Illidari Inquisitor"
	mana, attack, health = 8, 8, 8
	index = "CORE~Demon Hunter~Minion~8~8~8~Demon~Illidari Inquisitor~Rush"
	requireTarget, effects, description = False, "Rush", "Rush. After your hero attacks an enemy, this attacks it too"
	name_CN = "伊利达雷审判官"
	trigBoard = Trig_IllidariInquisitor


class Innervate(Spell):
	Class, school, name = "Druid", "Nature", "Innervate"
	requireTarget, mana, effects = False, 0, ""
	index = "CORE~Druid~Spell~0~Nature~Innervate"
	description = "Gain 1 Mana Crystal this turn only"
	description_CN = "在本回合中，获得一个法力水晶。"
	name_CN = "激活"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.Manas.gainTempManaCrystal(1, self.ID)


class Pounce(Spell):
	Class, school, name = "Druid", "", "Pounce"
	requireTarget, mana, effects = False, 0, ""
	index = "CORE~Druid~Spell~0~~Pounce"
	description = "Give your hero +2 Attack this turn"
	description_CN = "在本回合中，使你的英雄获得+2攻击力"
	name_CN = "飞扑"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		self.giveHeroAttackArmor(self.ID, attGain=2, name=Pounce)


class EnchantedRaven(Minion):
	Class, race, name = "Druid", "Beast", "Enchanted Raven"
	mana, attack, health = 1, 2, 2
	index = "CORE~Druid~Minion~1~2~2~Beast~Enchanted Raven"
	requireTarget, effects, description = False, "", ""
	description_CN = ""
	name_CN = "魔法乌鸦"


class MarkoftheWild(Spell):
	Class, school, name = "Druid", "Nature", "Mark of the Wild"
	requireTarget, mana, effects = True, 2, ""
	index = "CORE~Druid~Spell~2~Nature~Mark of the Wild"
	description = "Give a minion +2/+3 and Taunt"
	name_CN = "野性印记"
	def available(self):
		return self.selectableMinionExists()

	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.giveEnchant(target, 2, 3, effGain="Taunt", name=MarkoftheWild)
		return target


class LeaderofthePack_Option(Option):
	name, description = "Leader of the Pack", "Give your minions +1/+1"
	mana, attack, health = 2, -1, -1
	spell = LeaderofthePack
	
class SummonaPanther_Option(Option):
	name, description = "Summon a Panther", "Summon a 3/2 Panther"
	mana, attack, health = 2, -1, -1
	spell = SummonaPanther
	def available(self):
		return self.keeper.Game.space(self.keeper.ID) > 0

class PoweroftheWild(Spell):
	Class, school, name = "Druid", "", "Power of the Wild"
	requireTarget, mana, effects = False, 2, ""
	index = "CORE~Druid~Spell~2~~Power of the Wild~Choose One"
	description = "Choose One - Give your minions +1/+1; or Summon a 3/2 Panther"
	name_CN = "野性之力"
	options = (LeaderofthePack_Option, SummonaPanther_Option)
	#needTarget() always returns False
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if choice != 0: self.summon(Panther(self.Game, self.ID))
		if choice < 1: self.AOE_GiveEnchant(self.Game.minionsonBoard(self.ID), 1, 1, name=PoweroftheWild)


class EvolveSpines_Option(Option):
	name, description = "Evolve Spines", "Give your hero +4 Attack this turn"
	mana, attack, health = 3, -1, -1
	spell = EvolveSpines
	
class EvolveScales_Option(Option):
	name, description = "Evolve Scales", "Gain 8 Armor"
	mana, attack, health = 3, -1, -1
	spell = EvolveScales
	
class FeralRage(Spell):
	Class, school, name = "Druid", "", "Feral Rage"
	requireTarget, mana, effects = False, 3, ""
	index = "CORE~Druid~Spell~3~~Feral Rage~Choose One"
	description = "Choose One - Give your hero +4 Attack this turn; or Give your hero 8 Armor"
	name_CN = "野性之怒"
	options = (EvolveSpines_Option, EvolveScales_Option)
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.giveHeroAttackArmor(self.ID, attGain=4 if choice < 1 else 0, armor=8 if choice != 0 else 0, name=FeralRage)


class Landscaping(Spell):
	Class, school, name = "Druid", "Nature", "Landscaping"
	requireTarget, mana, effects = False, 3, ""
	index = "CORE~Druid~Spell~3~Nature~Landscaping"
	description = "Summon two 2/2 Treants"
	name_CN = "植树造林"
	def available(self):
		return self.Game.space(self.ID) > 0

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon([Treant_Classic(self.Game, self.ID) for _ in (0, 1)])


class WildGrowth(Spell):
	Class, school, name = "Druid", "Nature", "Wild Growth"
	requireTarget, mana, effects = False, 3, ""
	index = "CORE~Druid~Spell~3~Nature~Wild Growth"
	description = "Gain an empty Mana Crystal"
	name_CN = "野性成长"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if not self.Game.Manas.gainEmptyManaCrystal(1, self.ID):
			self.addCardtoHand(ExcessMana, self.ID)


class NordrassilDruid(Minion):
	Class, race, name = "Druid", "", "Nordrassil Druid"
	mana, attack, health = 4, 3, 5
	index = "CORE~Druid~Minion~4~3~5~~Nordrassil Druid~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Your next spell this turn costs (3) less"
	name_CN = "诺达希尔德鲁伊"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		GameManaAura_NordrassilDruid(self.Game, self.ID).auraAppears()

class SouloftheForest(Spell):
	Class, school, name = "Druid", "Nature", "Soul of the Forest"
	requireTarget, mana, effects = False, 4, ""
	index = "CORE~Druid~Spell~4~Nature~Soul of the Forest"
	description = "Give your minions 'Deathrattle: Summon a 2/2 Treant'"
	name_CN = "丛林之魂"
	def available(self):
		return self.Game.minionsonBoard(self.ID) != []

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.AOE_GiveEnchant(self.Game.minionsonBoard(self.ID), trig=Death_SouloftheForest, trigType="Deathrattle", connect=True)


class CatForm_Option(Option):
	name, category, description = "Cat Form", "Option_Minion", "Rush"
	mana, attack, health = 5, 5, 4

class BearForm_Option(Option):
	name, category, description = "Bear Form", "Option_Minion", "+2 health and Taunt"
	mana, attack, health = 5, 5, 6

class DruidoftheClaw(Minion):
	Class, race, name = "Druid", "", "Druid of the Claw"
	mana, attack, health = 5, 5, 4
	index = "CORE~Druid~Minion~5~5~4~~Druid of the Claw~Choose One"
	requireTarget, effects, description = False, "", "Choose One - Transform into a 5/4 with Rush; or a 5/6 with Taunt"
	name_CN = "利爪德鲁伊"
	options = (CatForm_Option, BearForm_Option)

	def played(self, target=None, choice=0, mana=0, posinHand=0, comment=""):
		self.health = self.health_max
		self.appears(firstTime=True)
		if choice < 0: minion = DruidoftheClaw_Both(self.Game, self.ID)
		elif choice == 0: minion = DruidoftheClaw_Charge(self.Game, self.ID)
		else: minion = DruidoftheClaw_Taunt(self.Game, self.ID)
		#抉择变形类随从的入场后立刻变形。
		self.Game.transform(self, minion)
		#在此之后就要引用self.Game.minionPlayed
		self.Game.sendSignal("MinionPlayed", self.ID, self.Game.minionPlayed, None, mana, "", choice)
		self.Game.sendSignal("MinionSummoned", self.ID, self.Game.minionPlayed, None, mana, "")
		self.Game.gathertheDead()


class ForceofNature(Spell):
	Class, school, name = "Druid", "Nature", "Force of Nature"
	requireTarget, mana, effects = False, 5, ""
	index = "CORE~Druid~Spell~5~Nature~Force of Nature"
	description = "Summon three 2/2 Treants"
	name_CN = "自然之力"
	def available(self):
		return self.Game.space(self.ID) > 0

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon([Treant_Classic(self.Game, self.ID) for _ in (0, 1, 2)])


class MenagerieWarden(Minion):
	Class, race, name = "Druid", "", "Menagerie Warden"
	mana, attack, health = 5, 4, 4
	index = "CORE~Druid~Minion~5~4~4~~Menagerie Warden~Battlecry"
	requireTarget, effects, description = True, "", "Battlecry: Choose a friendly Beast. Summon a copy of it"
	name_CN = "展览馆守卫"

	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()

	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.ID == self.ID and "Beast" in target.race and target.onBoard

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			Copy = target.selfCopy(self.ID, self) if target.onBoard else type(target)(self.Game, self.ID)
			self.summon(Copy, position=target.pos+1)
		return target


class RampantGrowth_Option(Option):
	name, description = "Rampant Growth", "Gain 2 Mana Crystals"
	mana, attack, health = 6, -1, -1
	spell = RampantGrowth
	
class Enrich_Option(Option):
	name, description = "Enrich", "Draw 3 cards"
	mana, attack, health = 6, -1, -1
	spell = Enrich
	
class Nourish(Spell):
	Class, school, name = "Druid", "Nature", "Nourish"
	requireTarget, mana, effects = False, 6, ""
	index = "CORE~Druid~Spell~6~Nature~Nourish~Choose One"
	description = "Choose One - Gain 2 Mana Crystals; or Draw 3 cards"
	name_CN = "滋养"
	options = (RampantGrowth_Option, Enrich_Option)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if choice < 1:
			self.Game.Manas.gainManaCrystal(2, self.ID)
		if choice != 0:
			self.Game.Hand_Deck.drawCard(self.ID)
			self.Game.Hand_Deck.drawCard(self.ID)
			self.Game.Hand_Deck.drawCard(self.ID)


class Uproot_Option(Option):
	name, description = "Uproot", "+5 attack"
	mana, attack, health = 7, -1, -1

class Rooted_Option(Option):
	name, description = "Rooted", "+5 health and Taunt"
	mana, attack, health = 7, -1, -1

class AncientofWar(Minion):
	Class, race, name = "Druid", "", "Ancient of War"
	mana, attack, health = 7, 5, 5
	index = "CORE~Druid~Minion~7~5~5~~Ancient of War~Choose One"
	requireTarget, effects, description = False, "", "Choose One - +5 Attack; or +5 Health and Taunt"
	name_CN = "战争古树"
	options = (Uproot_Option, Rooted_Option)
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if choice < 1: self.giveEnchant(self, 5, 0, name=AncientofWar)
		if choice != 0: self.giveEnchant(self, 0, 5, effGain="Taunt", name=AncientofWar)


class DemigodsFavor_Option(Option):
	name, description = "Demigod's Favor", "Give your other minions +2/+2"
	mana, attack, health = 9, -1, -1

class ShandosLesson_Option(Option):
	name, description = "Shan'do's Lesson", "Summon two 2/2 Treants with Taunt"
	mana, attack, health = 9, -1, -1
	def available(self):
		return self.keeper.Game.space(self.keeper.ID) > 0

class Cenarius(Minion):
	Class, race, name = "Druid", "", "Cenarius"
	mana, attack, health = 8, 5, 8
	index = "CORE~Druid~Minion~8~5~8~~Cenarius~Choose One~Legendary"
	requireTarget, effects, description = False, "", "Choose One- Give your other minions +2/+2; or Summon two 2/2 Treants with Taunt"
	name_CN = "塞纳留斯"
	options = (DemigodsFavor_Option, ShandosLesson_Option)
	#对于抉择随从而言，应以与战吼类似的方式处理，打出时抉择可以保持到最终结算。但是打出时，如果因为鹿盔和发掘潜力而没有选择抉择，视为到对方场上之后仍然可以而没有如果没有
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if choice != 0: self.summon([Treant_Classic_Taunt(self.Game, self.ID) for _ in (0, 1)], relative="<>")
		if choice < 1: self.AOE_GiveEnchant(self.Game.minionsonBoard(self.ID, self), 2, 2, name=Cenarius)


"""Hunter Cards"""
class ArcaneShot(Spell):
	Class, school, name = "Hunter", "Arcane", "Arcane Shot"
	requireTarget, mana, effects = True, 1, ""
	index = "CORE~Hunter~Spell~1~Arcane~Arcane Shot"
	description = "Deal 2 damage"
	name_CN = "奥术射击"
	def text(self): return self.calcDamage(2)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.dealsDamage(target, self.calcDamage(2))
		return target


class LockandLoad(Spell):
	Class, school, name = "Hunter", "", "Lock and Load"
	requireTarget, mana, effects = False, 1, ""
	index = "CORE~Hunter~Spell~1~~Lock and Load"
	description = "Each time you cast a spell this turn, add a random Hunter card to your hand"
	name_CN = "子弹上膛"
	poolIdentifier = "Hunter Cards"
	@classmethod
	def generatePool(cls, pools):
		return "Hunter Cards", pools.ClassCards["Hunter"]

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		LockandLoad_Effect(self.Game, self.ID).connect()


class Tracking(Spell):
	Class, school, name = "Hunter", "", "Tracking"
	requireTarget, mana, effects = False, 1, ""
	index = "CORE~Hunter~Spell~1~~Tracking"
	description = "Discover a card from your deck"
	name_CN = "追踪术"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverfromCardList(Tracking, comment)

	def discoverDecided(self, option, case, info_RNGSync=None, info_GUISync=None):
		self.handleDiscoveredCardfromList(option, case, ls=self.Game.Hand_Deck.decks[self.ID],
										  func=lambda index, card: self.Game.Hand_Deck.drawCard(self.ID, index),
										  info_RNGSync=info_RNGSync, info_GUISync=info_GUISync)


class Webspinner(Minion):
	Class, race, name = "Hunter", "Beast", "Webspinner"
	mana, attack, health = 1, 1, 1
	index = "CORE~Hunter~Minion~1~1~1~Beast~Webspinner~Deathrattle"
	requireTarget, effects, description = False, "", "Deathrattle: Add a random Beast to your hand"
	name_CN = "结网蛛"
	deathrattle = Death_Webspinner
	poolIdentifier = "Beasts"
	@classmethod
	def generatePool(cls, pools):
		return "Beasts", pools.MinionswithRace["Beast"]


class ExplosiveTrap(Secret):
	Class, school, name = "Hunter", "Fire", "Explosive Trap"
	requireTarget, mana, effects = False, 2, ""
	index = "CORE~Hunter~Spell~2~Fire~Explosive Trap~~Secret"
	description = "Secret: When your hero is attacked, deal 2 damage to all enemies"
	name_CN = "爆炸陷阱"
	trigBoard = Trig_ExplosiveTrap
	def text(self): return self.calcDamage(2)


class FreezingTrap(Secret):
	Class, school, name = "Hunter", "Frost", "Freezing Trap"
	requireTarget, mana, effects = False, 2, ""
	index = "CORE~Hunter~Spell~2~Frost~Freezing Trap~~Secret"
	description = "Secret: When an enemy minion attacks, return it to its owner's hand. It costs (2) more."
	name_CN = "冰冻陷阱"
	trigBoard = Trig_FreezingTrap


class HeadhuntersHatchet(Weapon):
	Class, name, description = "Hunter", "Headhunter's Hatchet", "Battlecry: If you control a Beast, gain +1 Durability"
	mana, attack, durability, effects = 2, 2, 2, ""
	index = "CORE~Hunter~Weapon~2~2~2~Headhunter's Hatchet~Battlecry"
	name_CN = "猎头者之斧"
	def effCanTrig(self):
		self.effectViable = any("Beast" in minion.race for minion in self.Game.minionsonBoard(self.ID))

	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		#Invoker must be a weapon in order to gain Durability
		if self.Game.minionsonBoard(self.ID, race="Beast") and self.category == "Weapon":
			self.giveEnchant(self, 0, 1, name=HeadhuntersHatchet)


class QuickShot(Spell):
	Class, school, name = "Hunter", "", "Quick Shot"
	requireTarget, mana, effects = True, 2, ""
	index = "CORE~Hunter~Spell~2~~Quick Shot"
	description = "Deal 3 damage. If your hand is empty, draw a card"
	name_CN = "快速射击"
	def effCanTrig(self):
		self.effectViable = len(self.Game.Hand_Deck.hands[self.ID]) < 2

	def text(self): return self.calcDamage(3)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.dealsDamage(target, self.calcDamage(3))
			if not self.Game.Hand_Deck.hands[self.ID]: self.Game.Hand_Deck.drawCard(self.ID)
		return target


class ScavengingHyena(Minion):
	Class, race, name = "Hunter", "Beast", "Scavenging Hyena"
	mana, attack, health = 2, 2, 2
	index = "CORE~Hunter~Minion~2~2~2~Beast~Scavenging Hyena"
	requireTarget, effects, description = False, "", "Whenever a friendly Beast dies, gain +2/+1"
	name_CN = "食腐土狼"
	trigBoard = Trig_ScavengingHyena


class SelectiveBreeder(Minion):
	Class, race, name = "Hunter", "", "Selective Breeder"
	mana, attack, health = 2, 1, 3
	index = "CORE~Hunter~Minion~2~1~3~~Selective Breeder~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Discover a copy of a Beast in your deck"
	name_CN = "选种饲养员"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverfromCardList(SelectiveBreeder, comment, conditional=lambda card: "Beast" in card.race)

	def discoverDecided(self, option, case, info_RNGSync=None, info_GUISync=None):
		self.handleDiscoveredCardfromList(option, case, ls=self.Game.Hand_Deck.decks[self.ID],
										  func=lambda index, card: self.addCardtoHand(card.selfCopy(self.ID, self), self.ID, byDiscover=True),
										  info_RNGSync=info_RNGSync, info_GUISync=info_GUISync)


class SnakeTrap(Secret):
	Class, school, name = "Hunter", "", "Snake Trap"
	requireTarget, mana, effects = False, 2, ""
	index = "CORE~Hunter~Spell~2~~Snake Trap~~Secret"
	description = "Secret: When one of your minions is attacked, summon three 1/1 Snakes"
	name_CN = "毒蛇陷阱"
	trigBoard = Trig_SnakeTrap


class Bearshark(Minion):
	Class, race, name = "Hunter", "Beast", "Bearshark"
	mana, attack, health = 3, 4, 3
	index = "CORE~Hunter~Minion~3~4~3~Beast~Bearshark"
	requireTarget, effects, description = False, "Evasive", "Can't be targeted by spells or Hero Powers"
	name_CN = "熊鲨"


class DeadlyShot(Spell):
	Class, school, name = "Hunter", "", "Deadly Shot"
	requireTarget, mana, effects = False, 3, ""
	index = "CORE~Hunter~Spell~3~~Deadly Shot"
	description = "Destroy a random enemy minion"
	name_CN = "致命射击"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		minions = self.Game.minionsAlive(3 - self.ID)
		if minions: self.Game.kill(self, numpyChoice(minions))


class DireFrenzy(Spell):
	Class, school, name = "Hunter", "", "Dire Frenzy"
	requireTarget, mana, effects = True, 4, ""
	index = "CORE~Hunter~Spell~4~~Dire Frenzy"
	description = "Give a Beast +3/+3. Shuffle three copies into your deck with +3/+3"
	name_CN = "凶猛狂暴"
	def available(self):
		return self.selectableMinionExists()

	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and "Beast" in target.race and target.onBoard

	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target:
			self.giveEnchant(target, 3, 3, name=DireFrenzy)
			beast = type(target)
			self.AOE_GiveEnchant((cards := [beast(self.Game, self.ID) for _ in (0, 1, 2)]), 3, 3, name=DireFrenzy)
			self.shuffleintoDeck(cards)
		return target


class SavannahHighmane(Minion):
	Class, race, name = "Hunter", "Beast", "Savannah Highmane"
	mana, attack, health = 6, 6, 5
	index = "CORE~Hunter~Minion~6~6~5~Beast~Savannah Highmane~Deathrattle"
	requireTarget, effects, description = False, "", "Deathrattle: Summon two 2/2 Hyenas"
	name_CN = "长鬃草原狮"
	deathrattle = Death_SavannahHighmane


class KingKrush(Minion):
	Class, race, name = "Hunter", "Beast", "King Krush"
	mana, attack, health = 9, 8, 8
	index = "CORE~Hunter~Minion~9~8~8~Beast~King Krush~Charge~Legendary"
	requireTarget, effects, description = False, "Charge", "Charge"
	name_CN = "暴龙王克鲁什"


"""Mage Cards"""
class BabblingBook(Minion):
	Class, race, name = "Mage", "", "Babbling Book"
	mana, attack, health = 1, 1, 1
	index = "CORE~Mage~Minion~1~1~1~~Babbling Book~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Add a random Mage spell to your hand"
	name_CN = "呓语魔典"
	poolIdentifier = "Mage Spells"
	@classmethod
	def generatePool(cls, pools):
		return "Mage Spells", [card for card in pools.ClassCards["Mage"] if card.category == "Spell"]

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.addCardtoHand(numpyChoice(self.rngPool("Mage Spells")), self.ID)


class ShootingStar(Spell):
	Class, school, name = "Mage", "Arcane", "Shooting Star"
	requireTarget, mana, effects = True, 1, ""
	index = "CORE~Mage~Spell~1~Arcane~Shooting Star"
	description = "Deal 1 damage to a minion and its neighbors"
	name_CN = "迸射流星"
	def available(self):
		return self.selectableMinionExists()

	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard

	def text(self): self.calcDamage(1)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = self.calcDamage(1)
			neighbors = self.Game.neighbors2(target)[0]
			if target.onBoard and neighbors:
				self.AOE_Damage([target] + neighbors, [damage] * (1 + len(neighbors)))
			else:
				self.dealsDamage(target, damage)
		return target


class SnapFreeze(Spell):
	Class, school, name = "Mage", "Frost", "Snap Freeze"
	requireTarget, mana, effects = True, 1, ""
	index = "CORE~Mage~Spell~1~Frost~Snap Freeze"
	description = "Freeze a minion. If it's already Frozen, destroy it"
	name_CN = "急速冷冻"
	def available(self):
		return self.selectableMinionExists()

	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard

	def effCanTrig(self):
		self.effectViable = any(minion.effects["Frozen"] > 0 for minion in self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2))

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			if target.effects["Frozen"] > 0: self.Game.kill(self, target)
			else: self.freeze(target)
		return target


class Arcanologist(Minion):
	Class, race, name = "Mage", "", "Arcanologist"
	mana, attack, health = 2, 2, 3
	index = "CORE~Mage~Minion~2~2~3~~Arcanologist~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Draw a Secret"
	name_CN = "秘法学家"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.drawCertainCard(lambda card: card.race == "Secret")


class FallenHero(Minion):
	Class, race, name = "Mage", "", "Fallen Hero"
	mana, attack, health = 2, 3, 2
	index = "CORE~Mage~Minion~2~3~2~~Fallen Hero"
	requireTarget, effects, description = False, "", "Your Hero Power deals 1 extra damage"
	name_CN = "英雄之魂"
	aura = GameRuleAura_FallenHero


class ArcaneIntellect(Spell):
	Class, school, name = "Mage", "Arcane", "Arcane Intellect"
	requireTarget, mana, effects = False, 3, ""
	index = "CORE~Mage~Spell~3~Arcane~Arcane Intellect"
	description = "Draw 2 cards"
	name_CN = "奥术智慧"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.Hand_Deck.drawCard(self.ID)
		self.Game.Hand_Deck.drawCard(self.ID)


class ConeofCold(Spell):
	Class, school, name = "Mage", "Frost", "Cone of Cold"
	requireTarget, mana, effects = True, 3, ""
	index = "CORE~Mage~Spell~3~Frost~Cone of Cold"
	description = "Freeze a minion and the minions next to it, and deal 1 damage to them"
	name_CN = "冰锥术"
	def available(self):
		return self.selectableMinionExists()

	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard

	def text(self): return self.calcDamage(1)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = self.calcDamage(1)
			neighbors = self.Game.neighbors2(target)[0]
			if target.onBoard and neighbors:
				targets = [target] + neighbors
				self.AOE_Damage(targets, [damage] * len(targets))
				self.AOE_Freeze(targets)
			else:
				self.dealsDamage(target, damage)
				self.freeze(target)
		return target


class Counterspell(Secret):
	Class, school, name = "Mage", "Arcane", "Counterspell"
	requireTarget, mana, effects = False, 3, ""
	index = "CORE~Mage~Spell~3~Arcane~Counterspell~~Secret"
	description = "Secret: When your opponent casts a spell, Counter it."
	name_CN = "法术反制"
	trigBoard = Trig_Counterspell


class IceBarrier(Secret):
	Class, school, name = "Mage", "Frost", "Ice Barrier"
	requireTarget, mana, effects = False, 3, ""
	index = "CORE~Mage~Spell~3~Frost~Ice Barrier~~Secret"
	description = "Secret: When your hero is attacked, gain 8 Armor"
	name_CN = "寒冰护体"
	trigBoard = Trig_IceBarrier


class MirrorEntity(Secret):
	Class, school, name = "Mage", "Arcane", "Mirror Entity"
	requireTarget, mana, effects = False, 3, ""
	index = "CORE~Mage~Spell~3~Arcane~Mirror Entity~~Secret"
	description = "Secret: After your opponent plays a minion, summon a copy of it"
	name_CN = "镜像实体"
	trigBoard = Trig_MirrorEntity


class Fireball(Spell):
	Class, school, name = "Mage", "Fire", "Fireball"
	requireTarget, mana, effects = True, 4, ""
	index = "CORE~Mage~Spell~4~Fire~Fireball"
	description = "Deal 6 damage"
	name_CN = "火球术"
	def text(self): return self.calcDamage(6)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.dealsDamage(target, self.calcDamage(6))
		return target


class WaterElemental_Core(Minion):
	Class, race, name = "Mage", "Elemental", "Water Elemental"
	mana, attack, health = 4, 3, 6
	index = "CORE~Mage~Minion~4~3~6~Elemental~Water Elemental"
	requireTarget, effects, description = False, "", "Freeze any character damaged by this minion"
	name_CN = "水元素"
	trigBoard = Trig_WaterElemental


class AegwynntheGuardian(Minion):
	Class, race, name = "Mage", "", "Aegwynn, the Guardian"
	mana, attack, health = 5, 5, 5
	index = "CORE~Mage~Minion~5~5~5~~Aegwynn, the Guardian~Spell Damage~Deathrattle~Legendary"
	requireTarget, effects, description = False, "Spell Damage_2", "Spell Damage +2. Deathrattle: The next minion your draw inherits these powers"
	name_CN = "守护者艾格文"
	deathrattle = Death_AegwynntheGuardian


class EtherealConjurer(Minion):
	Class, race, name = "Mage", "", "Ethereal Conjurer"
	mana, attack, health = 5, 6, 4
	index = "CORE~Mage~Minion~5~6~4~~Ethereal Conjurer~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Discover a spell"
	name_CN = "虚灵巫师"
	poolIdentifier = "Mage Spells"
	@classmethod
	def generatePool(cls, pools):
		return [Class + " Spells" for Class in pools.Classes], \
			   [[card for card in pools.ClassCards[Class] if card.category == "Spell"] for Class in pools.Classes]

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverandGenerate(EtherealConjurer, comment, poolFunc=lambda : self.rngPool(classforDiscover(self)+" Spells"))
		

class ColdarraDrake(Minion):
	Class, race, name = "Mage", "Dragon", "Coldarra Drake"
	mana, attack, health = 6, 6, 7
	index = "CORE~Mage~Minion~6~6~7~Dragon~Coldarra Drake"
	requireTarget, effects, description = False, "", "You can use your Hero Power any number of times"
	name_CN = "考达拉幼龙"
	aura = GameRuleAura_ColdarraDrake


class Flamestrike(Spell):
	Class, school, name = "Mage", "Fire", "Flamestrike"
	requireTarget, mana, effects = False, 7, ""
	index = "CORE~Mage~Spell~7~Fire~Flamestrike"
	description = "Deal 5 damage to all enemy minions"
	name_CN = "烈焰风暴"
	def text(self): return self.calcDamage(5)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = self.calcDamage(5)
		targets = self.Game.minionsonBoard(3-self.ID)
		self.AOE_Damage(targets, [damage for minion in targets])


"""Paladin Cards"""
class Avenge(Secret):
	Class, school, name = "Paladin", "Holy", "Avenge"
	requireTarget, mana, effects = False, 1, ""
	index = "CORE~Paladin~Spell~1~Holy~Avenge~~Secret"
	description = "Secret: When one of your minion dies, give a random friendly minion +3/+2"
	name_CN = "复仇"
	trigBoard = Trig_Avenge


class NobleSacrifice(Secret):
	Class, school, name = "Paladin", "", "Noble Sacrifice"
	requireTarget, mana, effects = False, 1, ""
	index = "CORE~Paladin~Spell~1~~Noble Sacrifice~~Secret"
	description = "Secret: When an enemy attacks, summon a 2/1 Defender as the new target"
	name_CN = "崇高牺牲"
	trigBoard = Trig_NobleSacrifice


class Reckoning(Secret):
	Class, school, name = "Paladin", "Holy", "Reckoning"
	requireTarget, mana, effects = False, 1, ""
	index = "CORE~Paladin~Spell~1~Holy~Reckoning~~Secret"
	description = "Secret: When an enemy minion deals 3 or more damage, destroy it"
	name_CN = "清算"
	trigBoard = Trig_Reckoning
#假设是被随从一次性造成3点或以上的伤害触发，单发或者AOE伤害均可


class RighteousProtector(Minion):
	Class, race, name = "Paladin", "", "Righteous Protector"
	mana, attack, health = 1, 1, 1
	index = "CORE~Paladin~Minion~1~1~1~~Righteous Protector~Taunt~Divine Shield"
	requireTarget, effects, description = False, "Taunt,Divine Shield", "Taunt, Divine Shield"
	name_CN = "正义保护者"


class ArgentProtector(Minion):
	Class, race, name = "Paladin", "", "Argent Protector"
	mana, attack, health = 2, 3, 2
	index = "CORE~Paladin~Minion~2~3~2~~Argent Protector~Battlecry"
	requireTarget, effects, description = True, "", "Battlecry: Give a friendly minion Divine Shield"
	name_CN = "银色保卫者"

	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()

	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.ID == self.ID and target != self and target.onBoard

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.giveEnchant(target, effGain="Divine Shield", name=ArgentProtector)
		return target


class HolyLight(Spell):
	Class, school, name = "Paladin", "Holy", "Holy Light"
	requireTarget, mana, effects = True, 2, ""
	index = "CORE~Paladin~Spell~2~Holy~Holy Light"
	description = "Restore 8 health"
	name_CN = "圣光术"
	def text(self): return self.calcHeal(8)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.restoresHealth(target, self.calcHeal(8))
		return target


class PursuitofJustice(Spell):
	Class, school, name = "Paladin", "Holy", "Pursuit of Justice"
	requireTarget, mana, effects = False, 2, ""
	index = "CORE~Paladin~Spell~2~Holy~Pursuit of Justice"
	description = "Give +1 Attack to Silver Hand Recruits you summon this game"
	name_CN = "正义追击"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		GameAura_PursuitofJustice(self.Game, self.ID).auraAppears()


class AldorPeacekeeper(Minion):
	Class, race, name = "Paladin", "", "Aldor Peacekeeper"
	mana, attack, health = 3, 3, 3
	index = "CORE~Paladin~Minion~3~3~3~~Aldor Peacekeeper~Battlecry"
	requireTarget, effects, description = True, "", "Battlecry: Change an enemy minion's Attack to 1"
	name_CN = "奥尔多卫士"

	def targetExists(self, choice=0):
		return self.selectableEnemyMinionExists()

	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.ID != self.ID and target.onBoard and target != self

	#Infer from Houndmaster: Buff can apply on targets on board, in hand, in deck.
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.setStat(target, 1, name=AldorPeacekeeper)
		return target


class Equality(Spell):
	Class, school, name = "Paladin", "Holy", "Equality"
	requireTarget, mana, effects = False, 3, ""
	index = "CORE~Paladin~Spell~3~Holy~Equality"
	description = "Change the Health of ALL minions to 1"
	name_CN = "生而平等"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.AOE_SetStat(self.Game.minionsonBoard(self.ID) + self.Game.minionsonBoard(3-self.ID),
						newHealth=1, name=Equality)
		
		
class WarhorseTrainer(Minion):
	Class, race, name = "Paladin", "", "Warhorse Trainer"
	mana, attack, health = 3, 3, 4
	index = "CORE~Paladin~Minion~3~3~4~~Warhorse Trainer"
	requireTarget, effects, description = False, "", "Your Silver Hand Recruits have +1 Attack"
	name_CN = "战马训练师"
	aura = Aura_WarhorseTrainer


class BlessingofKings(Spell):
	Class, school, name = "Paladin", "Holy", "Blessing of Kings"
	requireTarget, mana, effects = True, 4, ""
	index = "CORE~Paladin~Spell~4~Holy~Blessing of Kings"
	description = "Give a minion +4/+4"
	name_CN = "王者祝福"
	def available(self):
		return self.selectableMinionExists()

	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.giveEnchant(target, 4, 4, name=BlessingofKings)
		return target


class Consecration(Spell):
	Class, school, name = "Paladin", "Holy", "Consecration"
	requireTarget, mana, effects = False, 4, ""
	index = "CORE~Paladin~Spell~4~Holy~Consecration"
	description = "Deal 2 damage to all enemies"
	name_CN = "奉献"
	def text(self): return self.calcDamage(2)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = self.calcDamage(2)
		targets = [self.Game.heroes[3-self.ID]] + self.Game.minionsonBoard(3-self.ID)
		self.AOE_Damage(targets, [damage for obj in targets])


class TruesilverChampion(Weapon):
	Class, name, description = "Paladin", "Truesilver Champion", "Whenever your hero attacks, restore 2 Health to it"
	mana, attack, durability, effects = 4, 4, 2, ""
	index = "CORE~Paladin~Weapon~4~4~2~Truesilver Champion"
	name_CN = "真银圣剑"
	trigBoard = Trig_TruesilverChampion
	def text(self): return self.calcHeal(2)


class StandAgainstDarkness(Spell):
	Class, school, name = "Paladin", "", "Stand Against Darkness"
	requireTarget, mana, effects = False, 5, ""
	index = "CORE~Paladin~Spell~5~~Stand Against Darkness"
	description = "Summon five 1/1 Silver Hand Recruits"
	name_CN = "惩黑除恶"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon([SilverHandRecruit(self.Game, self.ID) for i in range(5)])


class GuardianofKings(Minion):
	Class, race, name = "Paladin", "", "Guardian of Kings"
	mana, attack, health = 7, 5, 7
	index = "CORE~Paladin~Minion~7~5~7~~Guardian of Kings~Taunt~Battlecry"
	requireTarget, effects, description = False, "Taunt", "Taunt. Battlecry: Restore 6 health to your hero"
	name_CN = "列王守卫"
	def text(self): return self.calcHeal(6)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.restoresHealth(self.Game.heroes[self.ID], self.calcHeal(6))


class TirionFordring(Minion):
	Class, race, name = "Paladin", "", "Tirion Fordring"
	mana, attack, health = 8, 6, 6
	index = "CORE~Paladin~Minion~8~6~6~~Tirion Fordring~Taunt~Divine Shield~Deathrattle~Legendary"
	requireTarget, effects, description = False, "Divine Shield,Taunt", "Divine Shield, Taunt. Deathrattle: Equip a 5/3 Ashbringer"
	name_CN = "提里昂弗丁"
	deathrattle = Death_TirionFordring


"""Priest Cards"""
class CrimsonClergy(Minion):
	Class, race, name = "Priest", "", "Crimson Clergy"
	mana, attack, health = 1, 1 ,3
	index = "CORE~Priest~Minion~1~1~3~~Crimson Clergy"
	requireTarget, effects, description = False, "", "After a friendly character is healed, gain +1 Attack"
	name_CN = "赤红教士"
	trigBoard = Trig_CrimsonClergy


class FlashHeal(Spell):
	Class, school, name = "Priest", "Holy", "Flash Heal"
	requireTarget, mana, effects = True, 1, ""
	index = "CORE~Priest~Spell~1~Holy~Flash Heal"
	description = "Restore 5 Health"
	name_CN = "快速治疗"
	def text(self): return self.calcHeal(5)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.restoresHealth(target, self.calcHeal(5))
		return target


class FocusedWill(Spell):
	Class, school, name = "Priest", "", "Focused Will"
	requireTarget, mana, effects = True, 1, ""
	index = "CORE~Priest~Spell~1~~Focused Will"
	description = "Silence a minion, then give it +3 Health"
	name_CN = "专注意志"
	def available(self):
		return self.selectableMinionExists()

	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.getsSilenced()
			self.giveEnchant(target, 0, 3, name=FocusedWill)
		return target


class HolySmite(Spell):
	Class, school, name = "Priest", "Holy", "Holy Smite"
	requireTarget, mana, effects = True, 1, ""
	index = "CORE~Priest~Spell~1~Holy~Holy Smite"
	description = "Deal 3 damage to a minion"
	name_CN = "神圣惩击"
	def available(self):
		return self.selectableMinionExists()

	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard

	def text(self): return self.calcDamage(3)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.dealsDamage(target, self.calcDamage(3))
		return target


class PsychicConjurer(Minion):
	Class, race, name = "Priest", "", "Psychic Conjurer"
	mana, attack, health = 1, 1, 1
	index = "CORE~Priest~Minion~1~1~1~~Psychic Conjurer~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Copy a card in your opponent's deck and add it to your hand"
	name_CN = "心灵咒术师"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		enemyDeck = self.Game.Hand_Deck.decks[3-self.ID]
		if enemyDeck: self.addCardtoHand(numpyChoice(enemyDeck).selfCopy(self.ID, self), self.ID)


class KulTiranChaplain(Minion):
	Class, race, name = "Priest", "", "Kul Tiran Chaplain"
	mana, attack, health = 2, 2, 3
	index = "CORE~Priest~Minion~2~2~3~~Kul Tiran Chaplain~Battlecry"
	requireTarget, effects, description = True, "", "Battlecry: Give a friendly minion +2 Health"
	name_CN = "库尔提拉斯教士"

	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists(choice)

	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.ID == self.ID and target != self and target.onBoard

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.giveEnchant(target, 0, 2, name=KulTiranChaplain)
		return target


class ShadowWordDeath(Spell):
	Class, school, name = "Priest", "Shadow", "Shadow Word: Death"
	requireTarget, mana, effects = True, 2, ""
	index = "CORE~Priest~Spell~2~Shadow~Shadow Word: Death"
	description = "Destroy a minion with 5 or more Attack"
	name_CN = "暗言术：灭"
	def available(self):
		return self.selectableMinionExists()

	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.attack > 4 and target.onBoard

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.Game.kill(self, target)
		return target


class ThriveintheShadows(Spell):
	Class, school, name = "Priest", "Shadow", "Thrive in the Shadows"
	requireTarget, mana, effects = False, 2, ""
	index = "CORE~Priest~Spell~2~Shadow~Thrive in the Shadows"
	description = "Discover a spell from your deck"
	name_CN = "暗中生长"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverfromCardList(ThriveintheShadows, comment, conditional=lambda card: card.category == "Spell")

	def discoverDecided(self, option, case, info_RNGSync=None, info_GUISync=None):
		self.handleDiscoveredCardfromList(option, case, ls=self.Game.Hand_Deck.decks[self.ID],
										  func=lambda index, card: self.Game.Hand_Deck.drawCard(self.ID, index),
										  info_RNGSync=info_RNGSync, info_GUISync=info_GUISync)


#Even the latest aura can't change the attack. This effect is not an aura effect
class Lightspawn(Minion):
	Class, race, name = "Priest", "Elemental", "Lightspawn"
	mana, attack, health = 3, 0, 4
	index = "CORE~Priest~Minion~3~0~4~Elemental~Lightspawn"
	requireTarget, effects, description = False, "", "This minion's Attack is always equal to its Health"
	name_CN = "光耀之子"
	def statCheckResponse(self):
		if self.onBoard and not self.silenced: self.attack = self.health


class ShadowedSpirit(Minion):
	Class, race, name = "Priest", "", "Shadowed Spirit"
	mana, attack, health = 3, 4, 3
	index = "CORE~Priest~Minion~3~4~3~~Shadowed Spirit~Deathrattle"
	requireTarget, effects, description = False, "", "Deathrattle: Deal 3 damage to the enemy hero"
	name_CN = "暗影之灵"
	deathrattle = Death_ShadowedSpirit


class Shadowform(Spell):
	Class, school, name = "Priest", "Shadow", "Shadowform"
	requireTarget, mana, effects = False, 2, ""
	index = "CORE~Priest~Spell~2~Shadow~Shadowform"
	description = "Your Hero Power becomes 'Deal 2 damage'"
	name_CN = "暗影形态"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		MindSpike(self.Game, self.ID).replacePower()

class MindSpike(Power):
	mana, name, requireTarget = 2, "Mind Spike", True
	index = "Priest~Hero Power~2~Mind Spike"
	description = "Deal 2 damage"
	name_CN = "心灵尖刺"
	def canDealDmg(self): return True
	def text(self): return self.calcDamage(2)

	def effect(self, target=None, choice=0, comment=''):
		dmgTaker, damageActual = self.dealsDamage(target, self.calcDamage(2))
		if dmgTaker.health < 1 or dmgTaker.dead: return 1
		return 0


class HolyNova(Spell):
	Class, school, name = "Priest", "Holy", "Holy Nova"
	requireTarget, mana, effects = False, 4, ""
	index = "CORE~Priest~Spell~4~Holy~Holy Nova"
	description = "Deal 2 damage to all enemy minions. Restore 2 Health to all friendly characters"
	name_CN = "神圣新星"
	def text(self): return "-%d, +%d"%(self.calcDamage(2), self.calcHeal(2))

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage, heal = self.calcDamage(2), self.calcHeal(2)
		enemies = self.Game.minionsonBoard(3-self.ID)
		friendlies = [self.Game.heroes[self.ID]] + self.Game.minionsonBoard(self.ID)
		self.AOE_Damage(enemies, [damage]*len(enemies))
		self.AOE_Heal(friendlies, [heal]*len(friendlies))


class PowerInfusion(Spell):
	Class, school, name = "Priest", "Holy", "Power Infusion"
	requireTarget, mana, effects = True, 4, ""
	index = "CORE~Priest~Spell~4~Holy~Power Infusion"
	description = "Give a minion +2/+6"
	name_CN = "能量灌注"
	def available(self):
		return self.selectableMinionExists()

	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.giveEnchant(target, 2, 6, name=PowerInfusion)
		return target


class ShadowWordRuin(Spell):
	Class, school, name = "Priest", "Shadow", "Shadow Word: Ruin"
	requireTarget, mana, effects = False, 4, ""
	index = "CORE~Priest~Spell~4~Shadow~Shadow Word: Ruin"
	description = "Destroy all minions with 5 or more Attack"
	name_CN = "暗言术：毁"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.kill(self, [minion for minion in self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2) if minion.attack > 4])


class TempleEnforcer(Minion):
	Class, race, name = "Priest", "", "Temple Enforcer"
	mana, attack, health = 5, 5, 6
	index = "CORE~Priest~Minion~5~5~6~~Temple Enforcer~Battlecry"
	requireTarget, effects, description = True, "", "Battlecry: Give a friendly minion +3 health"
	name_CN = "圣殿执行者"
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists(choice)

	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.ID == self.ID and target != self and target.onBoard

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.giveEnchant(target, 0, 3, name=TempleEnforcer)
		return target


class NatalieSeline(Minion):
	Class, race, name = "Priest", "", "Natalie Seline"
	mana, attack, health = 8, 8, 1
	index = "CORE~Priest~Minion~8~8~1~~Natalie Seline~Battlecry~Legendary"
	requireTarget, effects, description = True, "", "Battlecry: Destroy a minion and gain its Health"
	name_CN = "娜塔莉塞林"

	def targetExists(self, choice=0):
		return self.selectableMinionExists()

	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target != self and target.onBoard

	#If the minion is shuffled into deck already, then nothing happens.
	#If the minion is returned to hand, move it from enemy hand into our hand.
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			healthGain = max(0, target.health)
			self.Game.kill(self, target)
			self.giveEnchant(self, 0, healthGain, name=NatalieSeline)
		return target


"""Rogue Cards"""
class Backstab(Spell):
	Class, school, name = "Rogue", "", "Backstab"
	requireTarget, mana, effects = True, 0, ""
	index = "CORE~Rogue~Spell~0~~Backstab"
	description = "Deal 2 damage to an undamage minion"
	name_CN = "背刺"
	def available(self):
		return self.selectableMinionExists()

	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.health == target.health_max and target.onBoard

	def text(self): return self.calcDamage(2)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.dealsDamage(target, self.calcDamage(2))
		return target


class Preparation(Spell):
	Class, school, name = "Rogue", "", "Preparation"
	requireTarget, mana, effects = False, 0, ""
	index = "CORE~Rogue~Spell~0~~Preparation"
	description = "The next spell you cast this turn costs (2) less"
	name_CN = "伺机待发"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		GameManaAura_Preparation(self.Game, self.ID).auraAppears()

class Shadowstep(Spell):
	Class, school, name = "Rogue", "Shadow", "Shadowstep"
	requireTarget, mana, effects = True, 0, ""
	index = "CORE~Rogue~Spell~0~Shadow~Shadowstep"
	description = "Return a friendly minion to your hand. It costs (2) less"
	name_CN = "暗影步"
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()

	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.ID == self.ID and target.onBoard

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		#假设暗影步第二次生效时不会不在场上的随从生效
		if target and target.onBoard:
			#假设那张随从在进入手牌前接受-2费效果。可以被娜迦海巫覆盖。
			self.Game.returnObj2Hand(target, deathrattlesStayArmed=False, manaMod=ManaMod(target, by=-2))
		return target


class BladedCultist(Minion):
	Class, race, name = "Rogue", "", "Bladed Cultist"
	mana, attack, health = 1, 1, 2
	index = "CORE~Rogue~Minion~1~1~2~~Bladed Cultist~Combo"
	requireTarget, effects, description = False, "", "Combo: Gain +1/+1"
	name_CN = "执刃教徒"

	def effCanTrig(self):
		self.effectViable = self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		#Dead minions or minions in deck can't be buffed or reset.
		if self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0:
			self.giveEnchant(self, 1, 1, name=BladedCultist)


class DeadlyPoison(Spell):
	Class, school, name = "Rogue", "Nature", "Deadly Poison"
	requireTarget, mana, effects = False, 1, ""
	index = "CORE~Rogue~Spell~1~Nature~Deadly Poison"
	description = "Give your weapon +2 Attack"
	name_CN = "致命药膏"
	def available(self):
		return self.Game.availableWeapon(self.ID) is not None

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		weapon = self.Game.availableWeapon(self.ID)
		if weapon: self.giveEnchant(weapon, 2, 0, name=DeadlyPoison)


class SinisterStrike(Spell):
	Class, school, name = "Rogue", "", "Sinister Strike"
	requireTarget, mana, effects = False, 1, ""
	index = "CORE~Rogue~Spell~1~~Sinister Strike"
	description = "Deal 3 damage to the enemy hero"
	name_CN = "影袭"
	def text(self): return self.calcDamage(3)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.dealsDamage(self.Game.heroes[3-self.ID], self.calcDamage(3))


class Swashburglar(Minion):
	Class, race, name = "Rogue", "Pirate", "Swashburglar"
	mana, attack, health = 1, 1, 1
	index = "CORE~Rogue~Minion~1~1~1~Pirate~Swashburglar~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Add a random card from another class to your hand"
	name_CN = "吹嘘海盗"
	poolIdentifier = "Rogue Cards"
	@classmethod
	def generatePool(cls, pools):
		return ["%s Cards"%Class for Class in pools.Classes], \
				[pools.ClassCards[Class] for Class in pools.Classes]

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curClass = self.Game.heroes[self.ID].Class
		classes = [Class for Class in self.rngPool("Classes") if Class != curClass]
		self.addCardtoHand(numpyChoice(self.rngPool("%s Cards" % numpyChoice(classes))), self.ID)


class ColdBlood(Spell):
	Class, school, name = "Rogue", "", "Cold Blood"
	requireTarget, mana, effects = True, 2, ""
	index = "CORE~Rogue~Spell~2~~Cold Blood~Combo"
	description = "Give a minion +2 Attack. Combo: +4 Attack instead"
	name_CN = "冷血"
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0

	def available(self):
		return self.selectableMinionExists()

	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.giveEnchant(target, 4 if self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0 else 2, 0, name=ColdBlood)
		return target


class PatientAssassin(Minion):
	Class, race, name = "Rogue", "", "Patient Assassin"
	mana, attack, health = 2, 1, 2
	index = "CORE~Rogue~Minion~2~1~2~~Patient Assassin~Poisonous~Stealth"
	requireTarget, effects, description = False, "Stealth,Poisonous", "Stealth, Poisonous"
	name_CN = "耐心的刺客"


class VanessaVanCleef(Minion):
	Class, race, name = "Rogue", "", "Vanessa VanCleef"
	mana, attack, health = 2, 2, 3
	index = "CORE~Rogue~Minion~2~2~3~~Vanessa VanCleef~Combo~Legendary"
	requireTarget, effects, description = False, "", "Combo: Add a copy of the last card your opponent played to your hand"
	name_CN = "梵妮莎·范克里夫"

	def effCanTrig(self):
		self.effectViable = self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0 and len(cardsPlayed := self.Game.Counters.cardsPlayedThisGame[3-self.ID]):
			self.addCardtoHand(cardsPlayed[-1], self.ID)


class PlagueScientist(Minion):
	Class, race, name = "Rogue", "", "Plague Scientist"
	mana, attack, health = 3, 2, 3
	index = "CORE~Rogue~Minion~3~2~3~~Plague Scientist~Combo"
	requireTarget, effects, description = True, "", "Combo: Give a friendly minion Poisonous"
	name_CN = "瘟疫科学家"
	def needTarget(self, choice=0):
		return self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0

	def effCanTrig(self):
		self.effectViable = self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0 and self.Game.minionsonBoard(self.ID)

	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.ID == self.ID and target != self and target.onBoard

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0:
			self.giveEnchant(target, effGain="Poisonous", name=PlagueScientist)
		return target


class SI7Agent(Minion):
	Class, race, name = "Rogue", "", "SI:7 Agent"
	mana, attack, health = 3, 3, 3
	index = "CORE~Rogue~Minion~3~3~3~~SI:7 Agent~Combo"
	requireTarget, effects, description = True, "", "Combo: Deal 2 damage"
	name_CN = "军情七处特工"
	def needTarget(self, choice=0):
		return self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0

	def effCanTrig(self):
		self.effectViable = self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0:
			self.dealsDamage(target, 2)
		return target


class Assassinate(Spell):
	Class, school, name = "Rogue", "", "Assassinate"
	requireTarget, mana, effects = True, 4, ""
	index = "CORE~Rogue~Spell~4~~Assassinate"
	description = "Destroy an enemy minion"
	name_CN = "刺杀"
	def available(self):
		return self.selectableEnemyMinionExists()

	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.ID != self.ID and target.onBoard

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.Game.kill(self, target)
		return target


class AssassinsBlade(Weapon):
	Class, name, description = "Rogue", "Assassin's Blade", ""
	mana, attack, durability, effects = 4, 2, 5, ""
	index = "CORE~Rogue~Weapon~4~2~5~Assassin's Blade"
	name_CN = "刺客之刃"


class TombPillager(Minion):
	Class, race, name = "Rogue", "", "Tomb Pillager"
	mana, attack, health = 4, 5, 4
	index = "CORE~Rogue~Minion~4~5~4~~Tomb Pillager~Deathrattle"
	requireTarget, effects, description = False, "", "Deathrattle: Add a Coin to your hand"
	name_CN = "盗墓匪贼"
	deathrattle = Death_TombPillager


class Sprint(Spell):
	Class, school, name = "Rogue", "", "Sprint"
	requireTarget, mana, effects = False, 6, ""
	index = "CORE~Rogue~Spell~6~~Sprint"
	description = "Draw 4 cards"
	name_CN = "疾跑"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for num in (0, 1, 2, 3): self.Game.Hand_Deck.drawCard(self.ID)


"""Shaman Cards"""
class LightningBolt(Spell):
	Class, school, name = "Shaman", "Nature", "Lightning Bolt"
	requireTarget, mana, effects = True, 1, ""
	index = "CORE~Shaman~Spell~1~Nature~Lightning Bolt~Overload"
	description = "Deal 3 damage. Overload: (1)"
	name_CN = "闪电箭"
	overload = 1
	def text(self): return self.calcDamage(3)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.dealsDamage(target, self.calcDamage(3))
		return target


class MenacingNimbus(Minion):
	Class, race, name = "Shaman", "Elemental", "Menacing Nimbus"
	mana, attack, health = 2, 2, 2
	index = "CORE~Shaman~Minion~2~2~2~Elemental~Menacing Nimbus~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Add a random Elemental minion to your hand"
	name_CN = "凶恶的雨云"
	poolIdentifier = "Elementals"
	@classmethod
	def generatePool(cls, pools):
		return "Elementals", pools.MinionswithRace["Elemental"]

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.addCardtoHand(numpyChoice(self.rngPool("Elementals")), self.ID)


class NoviceZapper(Minion):
	Class, race, name = "Shaman", "", "Novice Zapper"
	mana, attack, health = 1, 3, 2
	index = "CORE~Shaman~Minion~1~3~2~~Novice Zapper~Spell Damage~Overload"
	requireTarget, effects, description = False, "Spell Damage", "Spell Damage +1. Overload: (1)"
	name_CN = "电击学徒"
	overload = 1


class RockbiterWeapon(Spell):
	Class, school, name = "Shaman", "Nature", "Rockbiter Weapon"
	requireTarget, mana, effects = True, 2, ""
	index = "CORE~Shaman~Spell~2~Nature~Rockbiter Weapon"
	description = "Give a friendly character +3 Attack this turn"
	name_CN = "石化武器"
	def available(self):
		return self.selectableFriendlyExists()

	def targetCorrect(self, target, choice=0):
		return (target.category == "Minion" or target.category == "Hero") and target.ID == self.ID and target.onBoard

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			if target.category == "Hero": self.giveHeroAttackArmor(target.ID, attGain=3, name=RockbiterWeapon)
			else: self.giveEnchant(target, 3, 0, statEnchant=Enchantment(3, 0, until=0, name=RockbiterWeapon))
		return target


class Windfury(Spell):
	Class, school, name = "Shaman", "Nature", "Windfury"
	requireTarget, mana, effects = True, 2, ""
	index = "CORE~Shaman~Spell~2~Nature~Windfury"
	description = "Give a minion Windfury"
	name_CN = "风怒"
	def available(self):
		return self.selectableMinionExists()

	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.giveEnchant(target, effGain="Windfury", name=Windfury)
		return target


class FeralSpirit(Spell):
	Class, school, name = "Shaman", "", "Feral Spirit"
	requireTarget, mana, effects = False, 3, ""
	index = "CORE~Shaman~Spell~3~~Feral Spirit~Overload"
	description = "Summon two 2/3 Spirit Wolves with Taunt. Overload: (1)"
	name_CN = "野性狼魂"
	overload = 1
	def available(self):
		return self.Game.space(self.ID) > 0

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon([SpiritWolf(self.Game, self.ID) for _ in (0, 1)])


class LightningStorm(Spell):
	Class, school, name = "Shaman", "Nature", "Lightning Storm"
	requireTarget, mana, effects = False, 3, ""
	index = "CORE~Shaman~Spell~3~Nature~Lightning Storm~Overload"
	description = "Deal 3 damage to all enemy minions. Overload: (2)"
	name_CN = "闪电风暴"
	overload = 2
	def text(self): return self.calcDamage(3)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = self.calcDamage(3)
		targets = self.Game.minionsonBoard(3-self.ID)
		self.AOE_Damage(targets, [damage]*len(targets))


class ManaTideTotem(Minion):
	Class, race, name = "Shaman", "Totem", "Mana Tide Totem"
	mana, attack, health = 3, 0, 3
	index = "CORE~Shaman~Minion~3~0~3~Totem~Mana Tide Totem"
	requireTarget, effects, description = False, "", "At the end of your turn, draw a card"
	name_CN = "法力之潮图腾"
	trigBoard = Trig_ManaTideTotem


class UnboundElemental(Minion):
	Class, race, name = "Shaman", "Elemental", "Unbound Elemental"
	mana, attack, health = 3, 3, 4
	index = "CORE~Shaman~Minion~3~3~4~Elemental~Unbound Elemental"
	requireTarget, effects, description = False, "", "Whenever you play a card with Overload, gain +1/+1"
	name_CN = "无羁元素"
	trigBoard = Trig_UnboundElemental


class DraeneiTotemcarver(Minion):
	Class, race, name = "Shaman", "", "Draenei Totemcarver"
	mana, attack, health = 4, 4, 5
	index = "CORE~Shaman~Minion~4~4~5~~Draenei Totemcarver~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Gain +1/+1 for each friendly Totem"
	name_CN = "德莱尼图腾师"

	#For self buffing effects, being dead and removed before battlecry will prevent the battlecry resolution.
	#If this minion is returned hand before battlecry, it can still buff it self according to living friendly minions.
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if (self.onBoard or self.inHand) and (num := len(self.Game.minionsonBoard(self.ID, race="Totem"))):
			self.giveEnchant(self, num, num, name=DraeneiTotemcarver)


class Hex(Spell):
	Class, school, name = "Shaman", "Nature", "Hex"
	requireTarget, mana, effects = True, 4, ""
	index = "CORE~Shaman~Spell~4~Nature~Hex"
	description = "Transform a minion into a 0/1 Frog with Taunt"
	name_CN = "妖术"
	def available(self):
		return self.selectableMinionExists()

	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: target = self.Game.transform(target, Frog(self.Game, target.ID))
		return target


class TidalSurge(Spell):
	Class, school, name = "Shaman", "Nature", "Tidal Surge"
	requireTarget, mana, effects = True, 3, "Lifesteal"
	index = "CORE~Shaman~Spell~3~Nature~Tidal Surge"
	description = "Lifesteal. Deal 4 damage to a minion"
	name_CN = "海潮涌动"
	def targetExists(self, choice=0):
		return self.selectableMinionExists()

	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard

	def text(self): return self.calcDamage(4)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.dealsDamage(target, self.calcDamage(4))
		return target


class Doomhammer(Weapon):
	Class, name, description = "Shaman", "Doomhammer", "Windfury, Overload: (2)"
	mana, attack, durability, effects = 5, 2, 8, "Windfury"
	index = "CORE~Shaman~Weapon~5~2~8~Doomhammer~Windfury~Overload"
	name_CN = "毁灭之锤"
	overload = 2


class EarthElemental(Minion):
	Class, race, name = "Shaman", "Elemental", "Earth Elemental"
	mana, attack, health = 5, 7, 8
	index = "CORE~Shaman~Minion~5~7~8~Elemental~Earth Elemental~Taunt~Overload"
	requireTarget, effects, description = False, "Taunt", "Taunt. Overload: (2)"
	name_CN = "土元素"
	overload = 2


class FireElemental(Minion):
	Class, race, name = "Shaman", "Elemental", "Fire Elemental"
	mana, attack, health = 6, 6, 5
	index = "CORE~Shaman~Minion~6~6~5~Elemental~Fire Elemental~Battlecry"
	requireTarget, effects, description = True, "", "Battlecry: Deal 4 damage"
	name_CN = "火元素"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.dealsDamage(target, 4)
		return target


class AlAkirtheWindlord(Minion):
	Class, race, name = "Shaman", "Elemental", "Al'Akir the Windlord"
	mana, attack, health = 8, 3, 6
	index = "CORE~Shaman~Minion~8~3~6~Elemental~Al'Akir the Windlord~Taunt~Charge~Windfury~Divine Shield~Legendary"
	requireTarget, effects, description = False, "Taunt,Charge,Divine Shield,Windfury", "Taunt,Charge,Divine Shield,Windfury"
	name_CN = "风领主奥拉基尔"


"""Warlock Cards"""
class RitualofDoom(Spell):
	Class, school, name = "Warlock", "Shadow", "Ritual of Doom"
	requireTarget, mana, effects = True, 0, ""
	index = "CORE~Warlock~Spell~0~Shadow~Ritual of Doom"
	description = "Destroy a friendly minion. If you had 5 or more, summon a 5/5 Demon"
	name_CN = "末日仪式"
	def available(self):
		return self.selectableFriendlyMinionExists()

	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.ID == self.ID

	def effCanTrig(self):
		self.effectViable = len(self.Game.minionsonBoard(self.ID)) > 4

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			hadEnoughMinions = len(self.Game.minionsonBoard(self.ID)) > 4
			self.Game.kill(self, target)
			self.Game.gathertheDead()
			if hadEnoughMinions: self.summon(DemonicTyrant(self.Game, self.ID))
		return target


class DemonicTyrant(Minion):
	Class, race, name = "Warlock", "Demon", "Demonic Tyrant"
	mana, attack, health = 5, 5, 5
	index = "CORE~Warlock~Minion~5~5~5~Demon~Demonic Tyrant~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "恶魔暴君"


class FlameImp(Minion):
	Class, race, name = "Warlock", "Demon", "Flame Imp"
	mana, attack, health = 1, 3, 2
	index = "CORE~Warlock~Minion~1~3~2~Demon~Flame Imp~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Deal 3 damage to your hero"
	name_CN = "烈焰小鬼"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.dealsDamage(self.Game.heroes[self.ID], 3)


class MortalCoil(Spell):
	Class, school, name = "Warlock", "Shadow", "Mortal Coil"
	requireTarget, mana, effects = True, 1, ""
	index = "CORE~Warlock~Spell~1~Shadow~Mortal Coil"
	description = "Deal 1 damage to a minion. If that kills it, draw a card"
	name_CN = "死亡缠绕"
	def available(self):
		return self.selectableMinionExists()

	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard

	def text(self): return self.calcDamage(1)

	#When cast by Archmage Vargoth, this spell can target minions with health <=0 and automatically meet the requirement of killing.
	#If the target minion dies before this spell takes effect, due to being killed by Violet Teacher/Knife Juggler, Mortal Coil still lets
	#player draw a card.
	#If the target is None due to Mayor Noggenfogger's randomization, nothing happens.
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			dmgTaker, damageActual = self.dealsDamage(target, self.calcDamage(1))
			if dmgTaker.health < 1 or dmgTaker.dead: self.Game.Hand_Deck.drawCard(self.ID)
		return target


class PossessedVillager(Minion):
	Class, race, name = "Warlock", "", "Possessed Villager"
	mana, attack, health = 1, 1, 1
	index = "CORE~Warlock~Minion~1~1~1~~Possessed Villager~Deathrattle"
	requireTarget, effects, description = False, "", "Deathrattle: Summon a 1/1 Shadow Beast"
	name_CN = "着魔村民"
	deathrattle = Death_PossessedVillager


class DrainSoul(Spell):
	Class, school, name = "Warlock", "Shadow", "Drain Soul"
	requireTarget, mana, effects = True, 2, "Lifesteal"
	index = "CORE~Warlock~Spell~2~Shadow~Drain Soul"
	description = "Lifesteal. Deal 3 damage to a minion"
	name_CN = "吸取灵魂"
	def targetExists(self, choice=0):
		return self.selectableMinionExists()

	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard

	def text(self): return self.calcDamage(3)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.dealsDamage(target, self.calcDamage(3))
		return target


class TinyKnightofEvil(Minion):
	Class, race, name = "Warlock", "Demon", "Tiny Knight of Evil"
	mana, attack, health = 2, 3, 2
	index = "CORE~Warlock~Minion~2~3~2~Demon~Tiny Knight of Evil"
	requireTarget, effects, description = False, "", "Whenever your discard a card, gain +1/+1"
	name_CN = "小鬼骑士"
	trigBoard = Trig_TinyKnightofEvil


class VoidTerror(Minion):
	Class, race, name = "Warlock", "Demon", "Void Terror"
	mana, attack, health = 3, 3, 4
	index = "CORE~Warlock~Minion~3~3~4~Demon~Void Terror~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Destroy both adjacent minions and gain their Attack and Health"
	name_CN = "虚空恐魔"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.onBoard: #Can't trigger if returned to hand already, since cards in hand don't have adjacent minions on board.
			neighbors, distribution = self.Game.neighbors2(self)
			if neighbors:
				attackGain, healthGain = 0, 0
				for minion in neighbors:
					attackGain += max(0, minion.attack)
					healthGain += max(0, minion.health)
				self.Game.kill(self, neighbors)
				self.giveEnchant(self, attackGain, healthGain, name=VoidTerror)


class FiendishCircle(Spell):
	Class, school, name = "Warlock", "Fel", "Fiendish Circle"
	requireTarget, mana, effects = False, 3, ""
	index = "CORE~Warlock~Spell~3~Fel~Fiendish Circle"
	description = "Summon four 1/1 Imps"
	name_CN = "恶魔法阵"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon([Imp(self.Game, self.ID) for i in (0, 1, 2, 3)])

class Imp(Minion):
	Class, race, name = "Warlock", "Demon", "Imp"
	mana, attack, health = 1, 1, 1
	index = "CORE~Warlock~Minion~1~1~1~Demon~Imp~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "小鬼"


class Hellfire(Spell):
	Class, school, name = "Warlock", "Fire", "Hellfire"
	requireTarget, mana, effects = False, 4, ""
	index = "CORE~Warlock~Spell~4~Fire~Hellfire"
	description = "Deal 3 damage to ALL characters"
	name_CN = "地狱烈焰"
	def text(self): return self.calcDamage(3)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = self.calcDamage(3)
		targets = [self.Game.heroes[1], self.Game.heroes[2]] + self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)
		self.AOE_Damage(targets, [damage for obj in targets])


class LakkariFelhound(Minion):
	Class, race, name = "Warlock", "Demon", "Lakkari Felhound"
	mana, attack, health = 4, 3, 8
	index = "CORE~Warlock~Minion~4~3~8~Demon~Lakkari Felhound~Taunt~Battlecry"
	requireTarget, effects, description = False, "Taunt", "Taunt. Battlecry: Discard your two lowest-Cost cards"
	name_CN = "拉卡利地狱犬"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		inds, i, j = {}, -1, -1
		for i, card in enumerate(self.Game.Hand_Deck.hands[self.ID]):
			add2ListinDict(i, inds, card.mana)
		manas = sorted(list(inds.keys()))
		if len(inds[manas[0]]) > 1:  #Two cards share the same lowest cost
			i, j = numpyChoice(inds[manas[0]], 2, replace=False)
		elif len(inds[manas[0]]) == 1:  #Only one card with the lowest cost
			#If there is a 2nd card in hand with a higher cost, then pick as j, else pick -2 as j
			i, j = numpyChoice(inds[manas[0]]), numpyChoice(inds[manas[1]]) if len(manas) > 1 else -1

		if i > -1 and j > -1: self.Game.Hand_Deck.discard(self.ID, (i, j))
		elif i > -1: self.Game.Hand_Deck.discard(self.ID, i)


class FelsoulJailer(Minion):
	Class, race, name = "Warlock", "Demon", "Felsoul Jailer"
	mana, attack, health = 5, 4, 6
	index = "CORE~Shaman~Minion~5~4~6~Demon~Felsoul Jailer~Battlecry~Deathrattle"
	requireTarget, effects, description = False, "", "Battlecry: Your opponent discards a minion. Deathrattle: Return it"
	name_CN = "邪魂狱卒"
	deathrattle = Death_FelsoulJailer
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if indices := [i for i, card in enumerate(self.Game.Hand_Deck.hands[3-self.ID]) if card.category == "Minion"]:
			minion = self.Game.Hand_Deck.discard(3 - self.ID, numpyChoice(indices))
			for trig in self.deathrattles:
				if isinstance(trig, Death_FelsoulJailer): trig.savedObj = type(minion)


class SiphonSoul(Spell):
	Class, school, name = "Warlock", "Shadow", "Siphon Soul"
	requireTarget, mana, effects = True, 5, ""
	index = "CORE~Warlock~Spell~5~Shadow~Siphon Soul"
	description = "Destroy a minion. Restore 3 Health to your hero"
	name_CN = "灵魂虹吸"
	def targetExists(self, choice=0):
		return self.selectableMinionExists()

	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard

	def text(self): return self.calcHeal(3)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.Game.kill(self, target)
			self.restoresHealth(self.Game.heroes[self.ID], self.calcHeal(3))
		return target


class DreadInfernal(Minion):
	Class, race, name = "Warlock", "Demon", "Dread Infernal"
	mana, attack, health = 6, 6, 6
	index = "CORE~Warlock~Minion~6~6~6~Demon~Dread Infernal~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Deal 1 damage to ALL other characters"
	name_CN = "恐惧地狱火"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		targets = [self.Game.heroes[1], self.Game.heroes[2]] + self.Game.minionsonBoard(self.ID, self) + self.Game.minionsonBoard(3-self.ID)
		self.AOE_Damage(targets, [1]*len(targets))


class EnslavedFelLord(Minion):
	Class, race, name = "Warlock", "Demon", "Enslaved Fel Lord"
	mana, attack, health = 7, 4, 10
	index = "CORE~Warlock~Minion~7~4~10~Demon~Enslaved Fel Lord~Taunt"
	requireTarget, effects, description = False, "Taunt,Sweep", "Taunt. Also damages the minions next to whomever this attacks"
	name_CN = "被奴役的邪能领主"


class TwistingNether(Spell):
	Class, school, name = "Warlock", "Shadow", "Twisting Nether"
	requireTarget, mana, effects = False, 8, ""
	index = "CORE~Warlock~Spell~8~Shadow~Twisting Nether"
	description = "Destroy all minions"
	name_CN = "扭曲虚空"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.kill(self, self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2))


class INFERNO(Power):
	mana, name, requireTarget = 2, "INFERNO!", False
	index = "Warlock~Hero Power~2~INFERNO!"
	description = "Summon a 6/6 Infernal"
	name_CN = "地狱火！"
	def available(self, choice=0):
		return not self.chancesUsedUp() and self.Game.space(self.ID)

	def effect(self, target=None, choice=0, comment=''):
		self.summon(Infernal(self.Game, self.ID))
		return 0


class LordJaraxxus(Hero):
	mana, weapon, description = 9, None, "Battlecry: Equip a 3/8 Bloodfury"
	Class, name, heroPower, armor = "Warlock", "Lord Jaraxxus", INFERNO, 5
	index = "CORE~Warlock~Hero Card~9~Lord Jaraxxus~Battlecry~Legendary"
	name_CN = "加拉克苏斯大王"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.equipWeapon(BloodFury(self.Game, self.ID))


"""Warrior Cards"""
class BloodsailDeckhand(Minion):
	Class, race, name = "Warrior", "Pirate", "Bloodsail Deckhand"
	mana, attack, health = 1, 2, 2
	index = "CORE~Warrior~Minion~1~2~2~Pirate~Bloodsail Deckhand~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: The next weapon you play costs (1) less"
	name_CN = "血帆桨手"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		GameManaAura_BloodsailDeckhand(self.Game, self.ID).auraAppears()


class ShieldSlam(Spell):
	Class, school, name = "Warrior", "", "Shield Slam"
	requireTarget, mana, effects = True, 1, ""
	index = "CORE~Warrior~Spell~1~~Shield Slam"
	description = "Deal 1 damage to a minion for each Armor you have"
	name_CN = "盾牌猛击"
	def available(self):
		return self.selectableMinionExists()

	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard

	def text(self): return self.calcDamage(self.Game.heroes[self.ID].armor)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and (armor := self.Game.heroes[self.ID].armor): self.dealsDamage(target, self.calcDamage(armor))
		return target


class Whirlwind(Spell):
	Class, school, name = "Warrior", "", "Whirlwind"
	requireTarget, mana, effects = False, 1, ""
	index = "CORE~Warrior~Spell~1~~Whirlwind"
	description = "Deal 1 damage to ALL minions"
	name_CN = "旋风斩"
	def text(self): return self.calcDamage(1)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = self.calcDamage(1)
		targets = self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)
		self.AOE_Damage(targets, [damage for minion in targets])


class CruelTaskmaster(Minion):
	Class, race, name = "Warrior", "", "Cruel Taskmaster"
	mana, attack, health = 2, 2, 2
	index = "CORE~Warrior~Minion~2~2~2~~Cruel Taskmaster~Battlecry"
	requireTarget, effects, description = True, "", "Battlecry: Deal 1 damage to a minion and give it +2 Attack"
	name_CN = "严酷的监工"

	def targetExists(self, choice=0):
		return self.selectableMinionExists()

	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard

	#Minion in deck can't get buff/reset.
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.dealsDamage(target, 1)
			self.giveEnchant(target, 2, 0, name=CruelTaskmaster)
		return target


class Execute(Spell):
	Class, school, name = "Warrior", "", "Execute"
	requireTarget, mana, effects = True, 2, ""
	index = "CORE~Warrior~Spell~2~~Execute"
	description = "Destroy a damaged enemy minion"
	name_CN = "斩杀"

	def available(self):
		return self.selectableEnemyMinionExists()

	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.ID != self.ID and target.health < target.health_max and target.onBoard

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.Game.kill(self, target)
		return target


class Slam(Spell):
	Class, school, name = "Warrior", "", "Slam"
	requireTarget, mana, effects = True, 2, ""
	index = "CORE~Warrior~Spell~2~~Slam"
	description = "Deal 2 damage to a minion. If it survives, draw a card"
	name_CN = "猛击"
	def available(self):
		return self.selectableMinionExists()

	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard

	def text(self): return self.calcDamage(2)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.dealsDamage(target, self.calcDamage(2))
			if not target.dead and target.health > 0: self.Game.Hand_Deck.drawCard(self.ID)
		return target


class FieryWarAxe_Core(Weapon):
	Class, name, description = "Warrior", "Fiery War Axe", ""
	mana, attack, durability, effects = 3, 3, 2, ""
	index = "CORE~Warrior~Weapon~3~3~2~Fiery War Axe"
	name_CN = "炽炎战斧"


#Charge gained by enchantment and aura can also be buffed by this Aura.
class WarsongCommander(Minion):
	Class, race, name = "Warrior", "", "Warsong Commander"
	mana, attack, health = 3, 2, 3
	index = "CORE~Warrior~Minion~3~2~3~~Warsong Commander"
	requireTarget, effects, description = False, "", "After you summon another minion, give it Rush"
	name_CN = "战歌指挥官"
	trigBoard = Trig_WarsongCommander


class Armorsmith(Minion):
	Class, race, name = "Warrior", "", "Armorsmith"
	mana, attack, health = 2, 1, 4
	index = "CORE~Warrior~Minion~2~1~4~~Armorsmith"
	requireTarget, effects, description = False, "", "Whenever a friendly minion takes damage, gain +1 Armor"
	name_CN = "铸甲师"
	trigBoard = Trig_Armorsmith


class FrothingBerserker(Minion):
	Class, race, name = "Warrior", "", "Frothing Berserker"
	mana, attack, health = 3, 2, 4
	index = "CORE~Warrior~Minion~3~2~4~~Frothing Berserker"
	requireTarget, effects, description = False, "", "Whenever a minion takes damage, gain +1 Attack"
	name_CN = "暴乱狂战士"
	trigBoard = Trig_FrothingBerserker


class WarCache(Spell):
	Class, school, name = "Warrior", "", "War Cache"
	requireTarget, mana, effects = False, 3, ""
	index = "CORE~Warrior~Spell~3~~War Cache"
	description = "Add a random Hunter Minion, Spell, and Weapon to your hand"
	name_CN = "战争储备箱"
	poolIdentifier = "Warrior Minions"
	@classmethod
	def generatePool(cls, pools):
		minions, spells, weapons = [], [], []
		for card in pools.ClassCards["Warrior"]:
			if card.category == "Minion": minions.append(card)
			elif card.category == "Spell": spells.append(card)
			elif card.category == "Weapon": weapons.append(card)
		return ["Warrior Minions", "Warrior Spells", "Warrior Weapons"], [minions, spells, weapons]

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for identifier in ("Warrior Minions", "Warrior Spells", "Warrior Weapons"):
			self.addCardtoHand(numpyChoice(self.rngPool(identifier)), self.ID)


class WarsongOutrider(Minion):
	Class, race, name = "Warrior", "", "Warsong Outrider"
	mana, attack, health = 4, 5, 4
	index = "CORE~Warrior~Minion~4~5~4~~Warsong Outrider~Rush"
	requireTarget, effects, description = False, "Rush", "Rush"
	name_CN = "战歌侦察骑兵"


class Brawl(Spell):
	Class, school, name = "Warrior", "", "Brawl"
	requireTarget, mana, effects = False, 5, ""
	index = "CORE~Warrior~Spell~5~~Brawl"
	description = "Destroy all minions except one. (Chosen randomly)"
	name_CN = "绝命乱斗"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		minions = self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)
		if len(minions) > 1:
			survivor = numpyChoice(minions)
			self.Game.kill(self, [minion for minion in minions if minion != survivor])


class Shieldmaiden(Minion):
	Class, race, name = "Warrior", "", "Shieldmaiden"
	mana, attack, health = 5, 5, 5
	index = "CORE~Warrior~Minion~5~5~5~~Shieldmaiden~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Gain 5 Armor"
	name_CN = "盾甲侍女"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.giveHeroAttackArmor(self.ID, armor=5)


class Gorehowl(Weapon):
	Class, name, description = "Warrior", "Gorehowl", "Attacking a minion costs 1 Attack instead of 1 Durability"
	mana, attack, durability, effects = 7, 7, 1, ""
	index = "CORE~Warrior~Weapon~7~7~1~Gorehowl"
	name_CN = "血吼"
	trigBoard = Trig_Gorehowl
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.losesAtkInstead = False

	def losesDurability(self):
		if self.losesAtkInstead:
			self.losesAtkInstead = False
			self.giveEnchant(self, -1, 0, name=Gorehowl)
			if self.attack < 1: self.dead = True
		else:
			self.health -= 1
			self.dmgTaken += 1
			if self.btn: self.btn.statChangeAni(action="damage")


class GrommashHellscream(Minion):
	Class, race, name = "Warrior", "", "Grommash Hellscream"
	mana, attack, health = 8, 4, 9
	index = "CORE~Warrior~Minion~8~4~9~~Grommash Hellscream~Charge~Legendary"
	requireTarget, effects, description = False, "Charge", "Charge. Has +6 attack while damaged"
	name_CN = "格罗玛什·地狱咆哮"
	def statCheckResponse(self):
		if self.onBoard and not self.silenced and self.dmgTaken > 0: self.attack += 6


"""Game TrigEffects & Game Auras"""
class GamaManaAura_RagingFelscreamer(GameManaAura_OneTime):
	card, by = RagingFelscreamer, -2
	def applicable(self, target): return target.ID == self.ID and "Demon" in target.race

class GameManaAura_NordrassilDruid(GameManaAura_OneTime):
	card, by = NordrassilDruid, -3
	def applicable(self, target): return target.ID == self.ID and target.category == "Spell"

class LockandLoad_Effect(TrigEffect):
	card, signals, trigType = LockandLoad, ("SpellBeenPlayed",), "Conn&TurnEnd"
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.card.addCardtoHand(numpyChoice(self.card.rngPool("Hunter Cards")), self.ID)

	def turnEndTrigger(self):
		self.disconnect()


class AegwynntheGuardian_Effect(TrigEffect):
	card, signals, trigType = AegwynntheGuardian, ("CardDrawn",), "Conn&TrigAura"
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return target[0].ID == self.ID and target[0].category == "Minion"

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.disconnect()
		self.card.giveEnchant(target[0], effGain="Spell Damage", effNum=2,
								trig=Death_AegwynntheGuardian, trigType="Deathrattle", connect=False, name=AegwynntheGuardian)
		
class GameAura_PursuitofJustice(GameAura_AlwaysOn):
	card, attGain, counter = PursuitofJustice, 1, 1
	def applicable(self, target): return target.name == "Silver Hand Recruit"
	def upgrade(self):
		self.attGain = self.counter = self.counter + 1
		for receiver in self.receivers:
			receiver.attGain = self.attGain
			receiver.recipient.calcStat()
		if self.counter and self.card.btn: self.card.btn.trigAni(self.counter)


class GameManaAura_Preparation(GameManaAura_OneTime):
	card, by = Preparation, -2
	def applicable(self, target): return target.ID == self.ID and target.category == "Spell"

class GameManaAura_BloodsailDeckhand(GameManaAura_OneTime):
	card, by, temporary = BloodsailDeckhand, -1, False
	def applicable(self, target): return target.ID == self.ID and target.category == "Weapon"


TrigsDeaths_Core = {Death_BloodmageThalnos: (BloodmageThalnos, "Deathrattle: Draw a card"),
					Death_ExplosiveSheep: (ExplosiveSheep, "Deathrattle: Deal 2 damage to all minions"),
					Death_LootHoarder: (LootHoarder, "Deathrattle: Draw a card"),
					Death_NerubianEgg: (NerubianEgg, "Deathrattle: Summon a 4/4 Nerubian"),
					Death_TaelanFordring: (TaelanFordring, "Deathrattle: Draw your hightest-Cost minion"),
					Death_CairneBloodhoof: (CairneBloodhoof, "Deathrattle: Summon a 4/5 Baine Bloodhoof"),
					Death_SouloftheForest: (SouloftheForest, "Deathrattle: Summon a 2/2 Treant"),
					Death_Webspinner: (Webspinner, "Deathrattle: Add a random Beast to your hand"),
					Death_SavannahHighmane: (SavannahHighmane, "Deathrattle: Summon two 2/2 Hyenas"),
					Death_AegwynntheGuardian: (AegwynntheGuardian, "Deathrattle: The next minion your draw inherits the power of the Guardian"),
					Death_TirionFordring: (TirionFordring, "Deathrattle: Equip a 5/3 Ashbringer"),
					Death_ShadowedSpirit: (ShadowedSpirit, "Deathrattle: Deal 3 damage to the enemy hero"),
					Death_TombPillager: (TombPillager, "Deathrattle: Add a Coin to your hand"),
					Death_PossessedVillager: (PossessedVillager, "Deathrattle: Summon a 1/1 Shadow Beast"),
					Death_FelsoulJailer: (FelsoulJailer, "Deathrattle: Return the discarded card to opponent's hand"),
					}


Core_Cards = [
		#Neutral
		MurlocTinyfin, AbusiveSergeant, ArcaneAnomaly, ArgentSquire, Cogmaster, ElvenArcher, MurlocTidecaller,
		EmeraldSkytalon, VoodooDoctor, WorgenInfiltrator, YoungPriestess, AcidicSwampOoze, AnnoyoTron, BloodmageThalnos,
		BloodsailRaider, CrazedAlchemist, DireWolfAlpha, ExplosiveSheep, FogsailFreebooter, KoboldGeomancer, LootHoarder,
		MadBomber, MurlocTidehunter, MurlocScout, NerubianEgg, RedgillRazorjaw, RiverCrocolisk, SunreaverSpy, Toxicologist,
		YouthfulBrewmaster, Brightwing, ColdlightSeer, EarthenRingFarseer, FlesheatingGhoul, HumongousRazorleaf, IceRager,
		InjuredBlademaster, IronbeakOwl, JunglePanther, KingMukla, LoneChampion, MiniMage, RaidLeader, SouthseaCaptain,
		SpiderTank, StoneskinBasilisk, BaronRivendare, BigGameHunter, ChillwindYeti, DarkIronDwarf, DefenderofArgus,
		GrimNecromancer, SenjinShieldmasta, SI7Infiltrator, VioletTeacher, FacelessManipulator, GurubashiBerserker,
		OverlordRunthak, StranglethornTiger, TaelanFordring, CairneBloodhoof, GadgetzanAuctioneer, HighInquisitorWhitemane, BaronGeddon,
		BarrensStablehand, NozdormutheEternal, Stormwatcher, StormwindChampion, ArcaneDevourer, AlexstraszatheLifeBinder,
		MalygostheSpellweaver, OnyxiatheBroodmother, SleepyDragon, YseratheDreamer, DeathwingtheDestroyer, ClockworkGiant,
		#Demon Hunter
		Battlefiend, ChaosStrike, CrimsonSigilRunner, FeastofSouls, KorvasBloodthorn, SightlessWatcher, SpectralSight,
		AldrachiWarblades, CoordinatedStrike, EyeBeam, GanargGlaivesmith, AshtongueBattlelord, RagingFelscreamer, ChaosNova,
		WarglaivesofAzzinoth, IllidariInquisitor,
		#Druid
		Innervate, Pounce, EnchantedRaven, MarkoftheWild, PoweroftheWild, FeralRage, Landscaping, WildGrowth,
		NordrassilDruid, SouloftheForest, DruidoftheClaw, ForceofNature, MenagerieWarden, Nourish, AncientofWar, Cenarius,
		#Hunter
		ArcaneShot, LockandLoad, Tracking, Webspinner, ExplosiveTrap, FreezingTrap, HeadhuntersHatchet, QuickShot,
		ScavengingHyena, SelectiveBreeder, SnakeTrap, Bearshark, DeadlyShot, DireFrenzy, SavannahHighmane, KingKrush,
		#Mage
		BabblingBook, ShootingStar, SnapFreeze, Arcanologist, FallenHero, ArcaneIntellect, ConeofCold, Counterspell,
		IceBarrier, MirrorEntity, Fireball, WaterElemental_Core, AegwynntheGuardian, EtherealConjurer, ColdarraDrake,
		Flamestrike,
		#Paladin
		Avenge, NobleSacrifice, Reckoning, RighteousProtector, ArgentProtector, HolyLight, PursuitofJustice,
		AldorPeacekeeper, Equality, WarhorseTrainer, BlessingofKings, Consecration, TruesilverChampion, StandAgainstDarkness,
		GuardianofKings, TirionFordring,
		#Priest
		CrimsonClergy, FlashHeal, FocusedWill, HolySmite, PsychicConjurer, KulTiranChaplain, ShadowWordDeath,
		ThriveintheShadows, Lightspawn, ShadowedSpirit, Shadowform, HolyNova, PowerInfusion, ShadowWordRuin, TempleEnforcer,
		NatalieSeline,
		#Rogue
		Backstab, Preparation, Shadowstep, BladedCultist, DeadlyPoison, SinisterStrike, Swashburglar, ColdBlood,
		PatientAssassin, VanessaVanCleef, PlagueScientist, SI7Agent, Assassinate, AssassinsBlade, TombPillager, Sprint,
		#Shaman
		LightningBolt, MenacingNimbus, NoviceZapper, RockbiterWeapon, Windfury, FeralSpirit, LightningStorm, ManaTideTotem,
		UnboundElemental, DraeneiTotemcarver, Hex, TidalSurge, Doomhammer, EarthElemental, FireElemental, AlAkirtheWindlord,
		#Warlock
		RitualofDoom, DemonicTyrant, FlameImp, MortalCoil, PossessedVillager, DrainSoul, TinyKnightofEvil, VoidTerror,
		FiendishCircle, Imp, Hellfire, LakkariFelhound, FelsoulJailer, SiphonSoul, DreadInfernal, EnslavedFelLord,
		TwistingNether, LordJaraxxus,
		#Warrior
		BloodsailDeckhand, ShieldSlam, Whirlwind, CruelTaskmaster, Execute, Slam, FieryWarAxe_Core, WarsongCommander,
		Armorsmith, FrothingBerserker, WarCache, WarsongOutrider, Brawl, Shieldmaiden, Gorehowl, GrommashHellscream,
]

Core_Cards_Collectible = [
		#Neutral
		MurlocTinyfin, AbusiveSergeant, ArcaneAnomaly, ArgentSquire, Cogmaster, ElvenArcher, MurlocTidecaller,
		EmeraldSkytalon, VoodooDoctor, WorgenInfiltrator, YoungPriestess, AcidicSwampOoze, AnnoyoTron, BloodmageThalnos,
		BloodsailRaider, CrazedAlchemist, DireWolfAlpha, ExplosiveSheep, FogsailFreebooter, KoboldGeomancer, LootHoarder,
		MadBomber, MurlocTidehunter, NerubianEgg, RedgillRazorjaw, RiverCrocolisk, SunreaverSpy, Toxicologist,
		YouthfulBrewmaster, Brightwing, ColdlightSeer, EarthenRingFarseer, FlesheatingGhoul, HumongousRazorleaf, IceRager,
		InjuredBlademaster, IronbeakOwl, JunglePanther, KingMukla, LoneChampion, MiniMage, RaidLeader, SouthseaCaptain,
		SpiderTank, StoneskinBasilisk, BaronRivendare, BigGameHunter, ChillwindYeti, DarkIronDwarf, DefenderofArgus,
		GrimNecromancer, SenjinShieldmasta, SI7Infiltrator, VioletTeacher, FacelessManipulator, GurubashiBerserker,
		OverlordRunthak, StranglethornTiger, TaelanFordring, CairneBloodhoof, GadgetzanAuctioneer, HighInquisitorWhitemane, BaronGeddon,
		BarrensStablehand, NozdormutheEternal, Stormwatcher, StormwindChampion, ArcaneDevourer, AlexstraszatheLifeBinder,
		MalygostheSpellweaver, OnyxiatheBroodmother, SleepyDragon, YseratheDreamer, DeathwingtheDestroyer, ClockworkGiant,
		#Demon Hunter
		Battlefiend, ChaosStrike, CrimsonSigilRunner, FeastofSouls, KorvasBloodthorn, SightlessWatcher, SpectralSight,
		AldrachiWarblades, CoordinatedStrike, EyeBeam, GanargGlaivesmith, AshtongueBattlelord, RagingFelscreamer, ChaosNova,
		WarglaivesofAzzinoth, IllidariInquisitor,
		#Druid
		Innervate, Pounce, EnchantedRaven, MarkoftheWild, PoweroftheWild, FeralRage, Landscaping, WildGrowth,
		NordrassilDruid, SouloftheForest, DruidoftheClaw, ForceofNature, MenagerieWarden, Nourish, AncientofWar, Cenarius,
		#Hunter
		ArcaneShot, LockandLoad, Tracking, Webspinner, ExplosiveTrap, FreezingTrap, HeadhuntersHatchet, QuickShot,
		ScavengingHyena, SelectiveBreeder, SnakeTrap, Bearshark, DeadlyShot, DireFrenzy, SavannahHighmane, KingKrush,
		#Mage
		BabblingBook, ShootingStar, SnapFreeze, Arcanologist, FallenHero, ArcaneIntellect, ConeofCold, Counterspell,
		IceBarrier, MirrorEntity, Fireball, WaterElemental_Core, AegwynntheGuardian, EtherealConjurer, ColdarraDrake,
		Flamestrike,
		#Paladin
		Avenge, NobleSacrifice, Reckoning, RighteousProtector, ArgentProtector, HolyLight, PursuitofJustice,
		AldorPeacekeeper, Equality, WarhorseTrainer, BlessingofKings, Consecration, TruesilverChampion, StandAgainstDarkness,
		GuardianofKings, TirionFordring,
		#Priest
		CrimsonClergy, FlashHeal, FocusedWill, HolySmite, PsychicConjurer, KulTiranChaplain, ShadowWordDeath,
		ThriveintheShadows, Lightspawn, ShadowedSpirit, Shadowform, HolyNova, PowerInfusion, ShadowWordRuin, TempleEnforcer,
		NatalieSeline,
		#Rogue
		Backstab, Preparation, Shadowstep, BladedCultist, DeadlyPoison, SinisterStrike, Swashburglar, ColdBlood,
		PatientAssassin, VanessaVanCleef, PlagueScientist, SI7Agent, Assassinate, AssassinsBlade, TombPillager, Sprint,
		#Shaman
		LightningBolt, MenacingNimbus, NoviceZapper, RockbiterWeapon, Windfury, FeralSpirit, LightningStorm, ManaTideTotem,
		UnboundElemental, DraeneiTotemcarver, Hex, TidalSurge, Doomhammer, EarthElemental, FireElemental, AlAkirtheWindlord,
		#Warlock
		RitualofDoom, FlameImp, MortalCoil, PossessedVillager, DrainSoul, TinyKnightofEvil, VoidTerror, FiendishCircle,
		Hellfire, LakkariFelhound, FelsoulJailer, SiphonSoul, DreadInfernal, EnslavedFelLord, TwistingNether, LordJaraxxus,
		#Warrior
		BloodsailDeckhand, ShieldSlam, Whirlwind, CruelTaskmaster, Execute, Slam, FieryWarAxe_Core, WarsongCommander,
		Armorsmith, FrothingBerserker, WarCache, WarsongOutrider, Brawl, Shieldmaiden, Gorehowl, GrommashHellscream,
]