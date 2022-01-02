from Parts.CardTypes import *
from Parts.TrigsAuras import *
from HS_Cards.AcrossPacks import TheCoin, SilverHandRecruit, LeaderofthePack, SummonaPanther, EvolveScales, EvolveSpines, \
						RampantGrowth, Enrich, Treant_Classic, Treant_Classic_Taunt, \
						Frog, SpiritWolf, BloodFury, Infernal, Panther, \
						Snake, IllidariInitiate, ExcessMana, Bananas, Nerubian, \
						VioletApprentice, Hyena_Classic, BaineBloodhoof, Whelp, DruidoftheClaw_Rush, \
						DruidoftheClaw_Taunt, DruidoftheClaw_Both, Skeleton, Shadowbeast, Defender, Ashbringer, \
						Dream, Nightmare, YseraAwakens, LaughingSister, EmeraldDrake


class Aura_DireWolfAlpha(Aura_AlwaysOn):
	attGain, targets = 1, "Neighbors"
	
	
class Aura_RaidLeader(Aura_AlwaysOn):
	attGain = 1
	
	
class Aura_SouthseaCaptain(Aura_AlwaysOn):
	attGain = healthGain = 1
	def applicable(self, target): return "Pirate" in target.race
		
	
class GameRuleAura_BaronRivendare(GameRuleAura):
	def auraAppears(self): self.keeper.Game.rules[self.keeper.ID]["Minion Deathrattle x2"] += 1
		
	def auraDisappears(self): self.keeper.Game.rules[self.keeper.ID]["Minion Deathrattle x2"] -= 1
		
	
class Aura_StormwindChampion(Aura_AlwaysOn):
	attGain = healthGain = 1
	
	
class GameRuleAura_FallenHero(GameRuleAura):
	def auraAppears(self): self.keeper.Game.powers[self.keeper.ID].getsEffect("Power Damage")
		
	def auraDisappears(self): self.keeper.Game.powers[self.keeper.ID].losesEffect("Power Damage")
		
	
class GameRuleAura_ColdarraDrake(GameRuleAura):
	def auraAppears(self):
		self.keeper.Game.rules[self.keeper.ID]["Power Chance Inf"] += 1
		if btn := self.keeper.Game.powers[self.keeper.ID].btn: btn.checkHpr()
		
	def auraDisappears(self):
		self.keeper.Game.rules[self.keeper.ID]["Power Chance Inf"] -= 1
		if btn := self.keeper.Game.powers[self.keeper.ID].btn: btn.checkHpr()
		
	
class Aura_WarhorseTrainer(Aura_AlwaysOn):
	attGain = 1
	def applicable(self, target): return target.name == "Silver Hand Recruit"
		
	
class Death_BloodmageThalnos(Deathrattle):
	description = "Deathrattle: Draw a card"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.Game.Hand_Deck.drawCard(self.keeper.ID)
		
	
class Death_ExplosiveSheep(Deathrattle):
	description = "Deathrattle: Deal 2 damage to all minions"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.dealsDamage(self.keeper.Game.minionsonBoard(), 2)
		
	
class Death_LootHoarder(Deathrattle):
	description = "Deathrattle: Draw a card"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.Game.Hand_Deck.drawCard(self.keeper.ID)
		
	
class Death_NerubianEgg(Deathrattle):
	description = "Deathrattle: Summon a 4/4 Nerubian"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).summon(Nerubian(kpr.Game, kpr.ID))
		
	
class Death_TaelanFordring(Deathrattle):
	description = "Deathrattle: Draw your hightest-Cost minion"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		if indices := pickInds_HighestAttr(self.keeper.Game.Hand_Deck.decks[self.keeper.ID],
										   cond=lambda card: card.category == "Minion"):
			self.keeper.Game.Hand_Deck.drawCard(self.keeper.ID, numpyChoice(indices))
		
	
class Death_CairneBloodhoof(Deathrattle):
	description = "Deathrattle: Summon a 4/5 Baine Bloodhoof"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).summon(BaineBloodhoof(kpr.Game, kpr.ID))
		
	
class Death_SouloftheForest(Deathrattle):
	description = "Deathrattle: Summon a 2/2 Treant"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		# This Deathrattle can't possibly be triggered in hand
		(kpr := self.keeper).summon(Treant_Classic(kpr.Game, kpr.ID))
		
	
class Death_Webspinner(Deathrattle):
	description = "Deathrattle: Add a random Beast to your hand"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.addCardtoHand(numpyChoice(self.rngPool("Beasts")), self.keeper.ID)
		
	
class Death_SavannahHighmane(Deathrattle):
	description = "Deathrattle: Summon two 2/2 Hyenas"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		game, ID = (kpr := self.keeper).Game, kpr.ID
		kpr.summon([Hyena_Classic(game, ID) for _ in (0, 1)], relative="<>")
		
	
class Death_AegwynntheGuardian(Deathrattle):
	description = "Deathrattle: The next minion your draw inherits the power of the Guardian"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		AegwynntheGuardian_Effect(self.keeper.Game, self.keeper.ID).connect()
		
	
class Death_TirionFordring(Deathrattle):
	description = "Deathrattle: Equip a 5/3 Ashbringer"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).equipWeapon(Ashbringer(kpr.Game, kpr.ID))
		
	
class Death_ShadowedSpirit(Deathrattle):
	description = "Deathrattle: Deal 3 damage to the enemy hero"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).dealsDamage(kpr.Game.heroes[3-kpr.ID], 3)
		
	
class Death_TombPillager(Deathrattle):
	description = "Deathrattle: Add a Coin to your hand"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).addCardtoHand(TheCoin(kpr.Game, kpr.ID), kpr.ID)
		
	
class Death_PossessedVillager(Deathrattle):
	description = "Deathrattle: Summon a 1/1 Shadow Beast"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).summon(Shadowbeast(kpr.Game, kpr.ID))
		
	
class Death_FelsoulJailer(Deathrattle):
	description = "Deathrattle: Return the discarded card to opponent's hand"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).addCardtoHand(self.memory, 3-kpr.ID)
		
	
class Trig_Cogmaster(Trig_SelfAura):
	signals = ("MinionAppears", "MinionDisappears",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and target.ID == kpr.ID and "Mech" in target.race
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.calcStat()
		
	
class Trig_ArcaneAnomaly(TrigBoard):
	signals = ("CardBeenPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return comment == "Spell" and ID == kpr.ID and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).giveEnchant(kpr, statEnchant=Enchantment_Exclusive(ArcaneAnomaly, 0, 1))
		
	
class Trig_MurlocTidecaller(TrigBoard):
	signals = ("ObjSummoned",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return "Murloc" in subject.race and ID == kpr.ID and subject is not kpr and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).giveEnchant(kpr, statEnchant=Enchantment_Exclusive(MurlocTidecaller, 1, 0))
		
	
class Trig_YoungPriestess(TrigBoard):
	signals = ("TurnEnds",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		if minions := kpr.Game.minionsonBoard(kpr.ID, exclude=kpr):
			kpr.giveEnchant(numpyChoice(minions), statEnchant=Enchantment_Exclusive(YoungPriestess, 0, 1))
		
	
class Trig_FlesheatingGhoul(TrigBoard):
	signals = ("ObjDies",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and target is not kpr and target.category == "Minion"
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).giveEnchant(kpr, statEnchant=Enchantment_Exclusive(FlesheatingGhoul, 1, 0))
		
	
class Trig_VioletTeacher(TrigBoard):
	signals = ("CardPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return comment == "Spell" and ID == kpr.ID and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).summon(VioletApprentice(kpr.Game, kpr.ID))
		
	
class Trig_GurubashiBerserker(TrigBoard):
	signals = ("MinionTakesDmg",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return target is kpr and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).giveEnchant(kpr, statEnchant=Enchantment_Exclusive(GurubashiBerserker, 3, 0))
		
	
class Trig_OverlordRunthak(TrigBoard):
	signals = ("MinionAttackingMinion", "MinionAttackingHero",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return subject is kpr and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).giveEnchant([card for card in kpr.Game.Hand_Deck.hands[kpr.ID] if card.category == "Minion"],
										statEnchant=Enchantment(OverlordRunthak, 1, 1), add2EventinGUI=False)
		
	
class Trig_GadgetzanAuctioneer(TrigBoard):
	signals = ("CardPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return comment == "Spell" and ID == kpr.ID and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).Game.Hand_Deck.drawCard(kpr.ID)
		
	
class Trig_BaronGeddon(TrigBoard):
	signals = ("TurnEnds",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).dealsDamage(kpr.Game.charsonBoard(exclude=kpr), 2)
		
	
class Trig_ArcaneDevourer(TrigBoard):
	signals = ("CardPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return comment == "Spell" and ID == kpr.ID and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).giveEnchant(kpr, statEnchant=Enchantment_Exclusive(ArcaneDevourer, 2, 2))
		
	
class Trig_OnyxiatheBroodmother(TrigBoard):
	signals = ("TurnEnds",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.summon([Whelp(self.keeper.Game, self.keeper.ID) for _ in range(6)], relative="<>")
		
	
class Trig_ClockworkGiant(TrigHand):
	signals = ("HandCheck",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.inHand and ID != kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).Game.Manas.calcMana_Single(kpr)
		
	
class Trig_Battlefiend(TrigBoard):
	signals = ("HeroAttackedMinion", "HeroAttackedHero",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and subject is kpr.Game.heroes[kpr.ID]
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).giveEnchant(kpr, statEnchant=Enchantment_Exclusive(Battlefiend, 1, 0))
		
	
class Trig_KorvasBloodthorn(TrigBoard):
	signals = ("CardBeenPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return ID == kpr.ID and "~Outcast" in kpr.Game.cardinPlay.index and kpr.aliveonBoard()
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).Game.returnObj2Hand(kpr, kpr)
		
	
class Trig_EyeBeam(TrigHand):
	signals = ("HandCheck",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.inHand and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).Game.Manas.calcMana_Single(kpr)
		
	
class Trig_WarglaivesofAzzinoth(TrigBoard):
	signals = ("HeroAttackedMinion",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return subject is kpr.Game.heroes[kpr.ID] and target.category == "Minion" and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).Game.heroes[kpr.ID].attChances_extra +=1
		
	
class Trig_IllidariInquisitor(TrigBoard):
	signals = ("HeroAttackedMinion", "HeroAttackedHero",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return ID == kpr.ID and kpr.canBattle() and target.canBattle()
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).Game.battle(kpr, target)
		
	
class Trig_ExplosiveTrap(Trig_Secret):
	signals = ("HeroAttacksHero", "MinionAttacksHero",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice): #target here holds the actual target object
		kpr = self.keeper
		return kpr.ID != kpr.Game.turn and target[0] is kpr.Game.heroes[kpr.ID]
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).dealsDamage(kpr.Game.charsonBoard(3-kpr.ID), kpr.calcDamage(2))
		
	
class Trig_FreezingTrap(Trig_Secret):
	signals = ("MinionAttacksMinion", "MinionAttacksHero",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.ID != kpr.Game.turn == ID and subject.aliveonBoard()
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).Game.returnObj2Hand(kpr, subject, manaMod=ManaMod(subject, by=kpr.num))
		
	
class Trig_ScavengingHyena(TrigBoard):
	signals = ("ObjDies",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		#Technically, minion has to disappear before dies. But just in case.
		return kpr.onBoard and target is not kpr and target.ID == kpr.ID and "Beast" in target.race
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).giveEnchant(kpr, statEnchant=Enchantment_Exclusive(ScavengingHyena, 2, 1))
		
	
class Trig_SnakeTrap(Trig_Secret):
	signals = ("MinionAttacksMinion", "HeroAttacksMinion",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice): #target here holds the actual target object
		kpr = self.keeper
		#The target has to a friendly minion and there is space on board to summon minions.
		return kpr.ID != kpr.Game.turn and target[0].category == "Minion" and target[0].ID == kpr.ID and kpr.Game.space(kpr.ID) > 0
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		game, ID, snake = (kpr := self.keeper).Game, kpr.ID, kpr.snake
		kpr.summon([snake(game, ID) for _ in (0, 1, 2)])
		
	
class Trig_Counterspell(Trig_Secret):
	signals = ("SpellOK2Play?",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return ID != self.keeper.ID and subject[0] > -1
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		if subject[0] > -1:
			spellOrig = self.keeper.Game.cardinPlay
			kpr.Game.add2EventinGUI(kpr, spellOrig, textTarget="X", colorTarget=red)
			subject[0] = -1
		
	
class Trig_IceBarrier(Trig_Secret):
	signals = ("HeroAttacksHero", "MinionAttacksHero",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):  #target here holds the actual target object
		kpr = self.keeper
		return kpr.ID != kpr.Game.turn and target[0] is kpr.Game.heroes[kpr.ID]
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).giveHeroAttackArmor(kpr.ID, armor=8)
		
	
class Trig_MirrorEntity(Trig_Secret):
	signals = ("CardBeenPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		game, Id = kpr.Game, kpr.ID
		return game.cardinPlay.category == "Minion" and Id != game.turn == ID and game.space(Id) > 0
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).summon(kpr.copyCard(kpr.Game.cardinPlay, kpr.ID))
		
	
class Trig_Avenge(Trig_Secret):
	signals = ("ObjDies",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return target.category == "Minion" and target.ID == kpr.ID != kpr.Game.turn and kpr.Game.minionsonBoard(target.ID)
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		if minions := kpr.Game.minionsonBoard(kpr.ID):
			self.keeper.giveEnchant(numpyChoice(minions), 3, 2, source=Avenge)
		
	
class Trig_NobleSacrifice(Trig_Secret):
	signals = ("MinionAttacksHero", "MinionAttacksMinion", "HeroAttacksHero", "HeroAttacksMinion",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.ID != kpr.Game.turn == ID and kpr.Game.space(kpr.ID) > 0
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		newTarget = Defender(kpr.Game, kpr.ID)
		self.keeper.summon(newTarget)
		target[1] = newTarget
		
	
class Trig_Reckoning(Trig_Secret):
	signals = ("DealtDmg",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		#假设是被随从一次性造成3点或以上的伤害触发，单发或者AOE伤害均可
		return kpr.ID != kpr.Game.turn == ID and num > 2 and not self.on\
			and subject.category == "Minion" and not subject.dead and subject.health > 0
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		kpr.Game.kill(kpr, subject)
		self.on = True
		
	
class Trig_TruesilverChampion(TrigBoard):
	signals, nextAniWaits = ("HeroAttackingMinion", "HeroAttackingHero",), True
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return subject is kpr.Game.heroes[kpr.ID] and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).heals(kpr.Game.heroes[kpr.ID], kpr.calcHeal(2))
		
	
class Trig_CrimsonClergy(TrigBoard):
	signals = ("MinionGotHealed", "HeroGotHealed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).giveEnchant(kpr, statEnchant=Enchantment_Exclusive(CrimsonClergy, 1, 0))
		
	
class Trig_ManaTideTotem(TrigBoard):
	signals = ("TurnEnds",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).Game.Hand_Deck.drawCard(kpr.ID)
		
	
class Trig_UnboundElemental(TrigBoard):
	signals = ("CardPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return ID == kpr.ID and kpr.Game.cardinPlay.overload and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).giveEnchant(kpr, statEnchant=Enchantment_Exclusive(UnboundElemental, 1, 1))
		
	
class Trig_TinyKnightofEvil(TrigBoard):
	signals = ("Discard",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).giveEnchant(kpr, statEnchant=Enchantment_Exclusive(TinyKnightofEvil, n := len(target), n))
		
	
class Trig_WarsongCommander(TrigBoard):
	signals = ("ObjBeenSummoned",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return subject.category == "Minion" and ID == kpr.ID and subject is not kpr and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.giveEnchant(subject, effGain="Rush", source=WarsongCommander)
		
	
class Trig_Armorsmith(TrigBoard):
	signals = ("MinionTakesDmg",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and target.ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).giveHeroAttackArmor(kpr.ID, armor=1)
		
	
class Trig_FrothingBerserker(TrigBoard):
	signals = ("MinionTakesDmg",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return self.keeper.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).giveEnchant(kpr, statEnchant=Enchantment_Exclusive(FrothingBerserker, 1, 0))
		
	
class Trig_Gorehowl(TrigBoard):
	signals = ("HeroAttackingMinion",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return subject is kpr.Game.heroes[kpr.ID] and target.category == "Minion" and kpr.onBoard and kpr.attack > 1
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.losesAtkInstead = True
		
	
class GamaManaAura_RagingFelscreamer(GameManaAura_OneTime):
	by = -2
	def applicable(self, target): return target.ID == self.ID and "Demon" in target.race
		
	
class GameManaAura_NordrassilDruid(GameManaAura_OneTime):
	by = -3
	def applicable(self, target): return target.ID == self.ID and target.category == "Spell"
		
	
class LockandLoad_Effect(TrigEffect):
	signals, trigType = ("CardBeenPlayed",), "Conn&TurnEnd"
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return comment == "Spell" and ID == self.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.card.addCardtoHand(numpyChoice(self.card.rngPool("Hunter Cards")), self.ID)
		
	def turnEndTrigger(self):
		self.disconnect()
		
	
class AegwynntheGuardian_Effect(TrigEffect):
	signals, trigType = ("CardDrawn",), "Conn&TrigAura"
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return ID == self.ID and target[0].category == "Minion"
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.disconnect()
		self.card.giveEnchant(target[0], effGain="Spell Damage", effNum=2, source=AegwynntheGuardian, trig=Death_AegwynntheGuardian, trigType="Deathrattle")
		
	
class GameAura_PursuitofJustice(GameAura_AlwaysOn):
	attGain, counter = 1, 1
	def applicable(self, target): return target.name == "Silver Hand Recruit"
		
	def upgrade(self):
		self.attGain = self.counter = self.counter + 1
		for receiver in self.receivers:
			receiver.attGain = self.attGain
			receiver.recipient.calcStat()
		if self.counter and self.card.btn: self.card.btn.trigAni(self.counter)
		
	
class GameManaAura_Preparation(GameManaAura_OneTime):
	by = -2
	def applicable(self, target): return target.ID == self.ID and target.category == "Spell"
		
	
class GameManaAura_BloodsailDeckhand(GameManaAura_OneTime):
	by, temporary = -1, False
	def applicable(self, target): return target.ID == self.ID and target.category == "Weapon"
		
	
class MurlocTinyfin(Minion):
	Class, race, name = "Neutral", "Murloc", "Murloc Tinyfin"
	mana, attack, health = 0, 1, 1
	numTargets, Effects, description = 0, "", ""
	name_CN = "鱼人宝宝"
	
	
class AbusiveSergeant(Minion):
	Class, race, name = "Neutral", "", "Abusive Sergeant"
	mana, attack, health = 1, 1, 1
	name_CN = "叫嚣的中士"
	numTargets, Effects, description = 1, "", "Battlecry: Give a minion +2 Attack this turn"
	index = "Battlecry"
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj is not self and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(target, statEnchant=Enchantment(AbusiveSergeant, 2, 0, until=0))
		
	
class ArcaneAnomaly(Minion):
	Class, race, name = "Neutral", "Elemental", "Arcane Anomaly"
	mana, attack, health = 1, 2, 1
	numTargets, Effects, description = 0, "", "After you cast a spell, give this minion +1 Health"
	name_CN = "奥术畸体"
	trigBoard = Trig_ArcaneAnomaly
	
	
class ArgentSquire(Minion):
	Class, race, name = "Neutral", "", "Argent Squire"
	mana, attack, health = 1, 1, 1
	numTargets, Effects, description = 0, "Divine Shield", "Divine Shield"
	name_CN = "银色侍从"
	
	
class Cogmaster(Minion):
	Class, race, name = "Neutral", "", "Cogmaster"
	mana, attack, health = 1, 1, 2
	numTargets, Effects, description = 0, "", "Has +2 Attack while you have a Mech"
	name_CN = "齿轮大师"
	trigBoard = Trig_Cogmaster
	def statCheckResponse(self):
		if self.onBoard and not self.silenced and self.Game.minionsonBoard(self.ID, race="Mech"):
			self.attack += 2
		
	
class ElvenArcher(Minion):
	Class, race, name = "Neutral", "", "Elven Archer"
	mana, attack, health = 1, 1, 1
	name_CN = "精灵弓箭手"
	numTargets, Effects, description = 1, "", "Battlecry: Deal 1 damamge"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(target, 1)
		
	
class MurlocTidecaller(Minion):
	Class, race, name = "Neutral", "Murloc", "Murloc Tidecaller"
	mana, attack, health = 1, 1, 2
	numTargets, Effects, description = 0, "", "Whenever you summon a Murloc, gain +1 Attack"
	name_CN = "鱼人招潮者"
	trigBoard = Trig_MurlocTidecaller
	
	
class EmeraldSkytalon(Minion):
	Class, race, name = "Neutral", "Beast", "Emerald Skytalon"
	mana, attack, health = 1, 2, 1
	numTargets, Effects, description = 0, "Rush", "Rush"
	name_CN = "翡翠天爪枭"
	
	
class VoodooDoctor(Minion):
	Class, race, name = "Neutral", "", "Voodoo Doctor"
	mana, attack, health = 1, 2, 1
	name_CN = "巫医"
	numTargets, Effects, description = 1, "", "Battlecry: Restore 2 health"
	index = "Battlecry"
	def text(self): return self.calcHeal(2)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.heals(target, self.calcHeal(2))
		
	
class WorgenInfiltrator(Minion):
	Class, race, name = "Neutral", "", "Worgen Infiltrator"
	mana, attack, health = 1, 2, 1
	numTargets, Effects, description = 0, "Stealth", "Stealth"
	name_CN = "狼人渗透者"
	
	
class YoungPriestess(Minion):
	Class, race, name = "Neutral", "", "Young Priestess"
	mana, attack, health = 1, 2, 1
	numTargets, Effects, description = 0, "", "At the end of your turn, give another random friendly minion +1 Health"
	name_CN = "年轻的女祭司"
	trigBoard = Trig_YoungPriestess
	
	
class AcidicSwampOoze(Minion):
	Class, race, name = "Neutral", "", "Acidic Swamp Ooze"
	mana, attack, health = 2, 3, 2
	name_CN = "酸性沼泽软泥怪"
	numTargets, Effects, description = 0, "", "Battlecry: Destroy you opponent's weapon"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.Game.kill(self, self.Game.weapons[3 - self.ID])
		
	
class AnnoyoTron(Minion):
	Class, race, name = "Neutral", "Mech", "Annoy-o-Tron"
	mana, attack, health = 2, 1, 2
	numTargets, Effects, description = 0, "Taunt,Divine Shield", "Taunt. Divine Shield"
	name_CN = "吵吵机器人"
	
	
class BloodmageThalnos(Minion):
	Class, race, name = "Neutral", "", "Bloodmage Thalnos"
	mana, attack, health = 2, 1, 1
	name_CN = "血法师萨尔诺斯"
	numTargets, Effects, description = 0, "Spell Damage", "Spell Damage +1. Deathrattle: Draw a card"
	index = "Legendary"
	deathrattle = Death_BloodmageThalnos
	
	
class BloodsailRaider(Minion):
	Class, race, name = "Neutral", "Pirate", "Bloodsail Raider"
	mana, attack, health = 2, 2, 3
	name_CN = "血帆袭击者"
	numTargets, Effects, description = 0, "", "Battlecry: Gain Attack equal to the Attack of your weapon"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if weapon := self.Game.availableWeapon(self.ID): self.giveEnchant(self, weapon.attack, 0, source=BloodsailRaider)
		
	
class CrazedAlchemist(Minion):
	Class, race, name = "Neutral", "", "Crazed Alchemist"
	mana, attack, health = 2, 2, 2
	name_CN = "疯狂的炼金师"
	numTargets, Effects, description = 1, "", "Battlecry: Swap the Attack and Health of a minion"
	index = "Battlecry"
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj is not self and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.setStat(target, [(obj.health, obj.attack) for obj in target], source=CrazedAlchemist)
		
	
class DireWolfAlpha(Minion):
	Class, race, name = "Neutral", "Beast", "Dire Wolf Alpha"
	mana, attack, health = 2, 2, 2
	numTargets, Effects, description = 0, "", "Adjacent minions have +1 Attack"
	name_CN = "恐狼先锋"
	aura = Aura_DireWolfAlpha
	
	
class ExplosiveSheep(Minion):
	Class, race, name = "Neutral", "Mech", "Explosive Sheep"
	mana, attack, health = 2, 1, 1
	numTargets, Effects, description = 0, "", "Deathrattle: Deal 2 damage to all minions"
	name_CN = "自爆绵羊"
	deathrattle = Death_ExplosiveSheep
	
	
class FogsailFreebooter(Minion):
	Class, race, name = "Neutral", "Pirate", "Fogsail Freebooter"
	mana, attack, health = 2, 2, 2
	name_CN = "雾帆劫掠者"
	numTargets, Effects, description = 1, "", "Battlecry: If you have a weapon equipped, deal 2 damage"
	index = "Battlecry"
	def numTargetsNeeded(self, choice=0):
		return 1 if self.Game.availableWeapon(self.ID) else 0
		
	def effCanTrig(self):
		self.effectViable = self.Game.availableWeapon(self.ID) is not None
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.Game.availableWeapon(self.ID): self.dealsDamage(target, 2)
		
	
class KoboldGeomancer(Minion):
	Class, race, name = "Neutral", "", "Kobold Geomancer"
	mana, attack, health = 2, 2, 2
	numTargets, Effects, description = 0, "Spell Damage", "Spell Damage +1"
	name_CN = "狗头人地卜师"
	
	
class LootHoarder(Minion):
	Class, race, name = "Neutral", "", "Loot Hoarder"
	mana, attack, health = 2, 2, 1
	numTargets, Effects, description = 0, "", "Deathrattle: Draw a card"
	name_CN = "战利品贮藏者"
	deathrattle = Death_LootHoarder
	
	
class MadBomber(Minion):
	Class, race, name = "Neutral", "", "Mad Bomber"
	mana, attack, health = 2, 3, 2
	name_CN = "疯狂投弹者"
	numTargets, Effects, description = 0, "", "Battlecry: Deal 3 damage randomly split among all other characters"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for _ in (0, 1, 2):
			if chars := self.Game.charsAlive(exclude=self): self.dealsDamage(numpyChoice(chars), 1)
			else: break
		
	
class MurlocTidehunter(Minion):
	Class, race, name = "Neutral", "Murloc", "Murloc Tidehunter"
	mana, attack, health = 2, 2, 1
	name_CN = "鱼人猎潮者"
	numTargets, Effects, description = 0, "", "Battlecry: Summon a 1/1 Murloc Scout"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon(MurlocScout(self.Game, self.ID))
		
	
class MurlocScout(Minion):
	Class, race, name = "Neutral", "Murloc", "Murloc Scout"
	mana, attack, health = 1, 1, 1
	name_CN = "鱼人斥候"
	numTargets, Effects, description = 0, "", ""
	index = "Uncollectible"
	
	
class NerubianEgg(Minion):
	Class, race, name = "Neutral", "", "Nerubian Egg"
	mana, attack, health = 2, 0, 2
	numTargets, Effects, description = 0, "", "Deathrattle: Summon a 4/4 Nerubian"
	name_CN = "蛛魔之卵"
	deathrattle = Death_NerubianEgg
	
	
class RedgillRazorjaw(Minion):
	Class, race, name = "Neutral", "Murloc", "Redgill Razorjaw"
	mana, attack, health = 2, 3, 1
	numTargets, Effects, description = 0, "Rush", "Rush"
	name_CN = "红鳃锋颚战士"
	
	
class RiverCrocolisk(Minion):
	Class, race, name = "Neutral", "Beast", "River Crocolisk"
	mana, attack, health = 2, 2, 3
	numTargets, Effects, description = 0, "", ""
	name_CN = "淡水鳄"
	
	
class SunreaverSpy(Minion):
	Class, race, name = "Neutral", "", "Sunreaver Spy"
	mana, attack, health = 2, 2, 3
	name_CN = "夺日者间谍"
	numTargets, Effects, description = 0, "", "Battlecry: If you control a Secret, gain +1/+1"
	index = "Battlecry"
	def effCanTrig(self):
		self.effectViable = self.Game.Secrets.secrets[self.ID]
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.Game.Secrets.secrets[self.ID]: self.giveEnchant(self, 1, 1, source=SunreaverSpy)
		
	
class Toxicologist(Minion):
	Class, race, name = "Neutral", "", "Toxicologist"
	mana, attack, health = 2, 2, 2
	name_CN = "毒物学家"
	numTargets, Effects, description = 0, "", "Battlecry: Give your weapon +1 Attack"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if weapon := self.Game.availableWeapon(self.ID): self.giveEnchant(weapon, 1, 0, source=Toxicologist)
		
	
class YouthfulBrewmaster(Minion):
	Class, race, name = "Neutral", "", "Youthful Brewmaster"
	mana, attack, health = 2, 3, 2
	name_CN = "年轻的酒仙"
	numTargets, Effects, description = 1, "", "Battlecry: Return a friendly minion from the battlefield to you hand"
	index = "Battlecry"
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists(self.ID)
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.ID == self.ID and obj is not self and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for obj in target: self.Game.returnObj2Hand(self, obj)
		
	
class Brightwing(Minion):
	Class, race, name = "Neutral", "Dragon", "Brightwing"
	mana, attack, health = 3, 3, 2
	name_CN = "光明之翼"
	numTargets, Effects, description = 0, "", "Battlecry: Add a random Legendary minion to your hand"
	index = "Battlecry~Legendary"
	poolIdentifier = "Legendary Minions"
	@classmethod
	def generatePool(cls, pools):
		return "Legendary Minions", pools.LegendaryMinions
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.addCardtoHand(numpyChoice(self.rngPool("Legendary Minions")), self.ID)
		
	
class ColdlightSeer(Minion):
	Class, race, name = "Neutral", "Murloc", "Coldlight Seer"
	mana, attack, health = 3, 2, 3
	name_CN = "寒光先知"
	numTargets, Effects, description = 0, "", "Battlecry: Give your other Murlocs +2 Health"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(self.Game.minionsonBoard(self.ID, exclude=self, race="Murloc"), 0, 2, source=ColdlightSeer)
		
	
class EarthenRingFarseer(Minion):
	Class, race, name = "Neutral", "", "Earthen Ring Farseer"
	mana, attack, health = 3, 3, 3
	name_CN = "大地之环先知"
	numTargets, Effects, description = 1, "", "Battlecry: Restore 3 health"
	index = "Battlecry"
	def text(self): return self.calcHeal(3)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.heals(target, self.calcHeal(3))
		
	
class FlesheatingGhoul(Minion):
	Class, race, name = "Neutral", "", "Flesheating Ghoul"
	mana, attack, health = 3, 3, 3
	numTargets, Effects, description = 0, "", "Whenever a minion dies, gain +1 Attack"
	name_CN = "腐肉食尸鬼"
	trigBoard = Trig_FlesheatingGhoul
	
	
class HumongousRazorleaf(Minion):
	Class, race, name = "Neutral", "", "Humongous Razorleaf"
	mana, attack, health = 3, 4, 8
	numTargets, Effects, description = 0, "Can't Attack", "Can't Attack"
	name_CN = "巨齿刀叶"
	
	
class IceRager(Minion):
	Class, race, name = "Neutral", "Elemental", "Ice Rager"
	mana, attack, health = 3, 5, 2
	numTargets, Effects, description = 0, "", ""
	name_CN = "冰霜暴怒者"
	
	
class InjuredBlademaster(Minion):
	Class, race, name = "Neutral", "", "Injured Blademaster"
	mana, attack, health = 3, 4, 7
	name_CN = "负伤剑圣"
	numTargets, Effects, description = 0, "", "Battlecry: Deal 4 damage to HIMSELF"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(self, 4)
		
	
class IronbeakOwl(Minion):
	Class, race, name = "Neutral", "Beast", "Ironbeak Owl"
	mana, attack, health = 3, 2, 1
	name_CN = "铁喙猫头鹰"
	numTargets, Effects, description = 1, "", "Battlecry: Silence a minion"
	index = "Battlecry"
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj is not self and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.Game.silenceMinions(target)
		
	
class JunglePanther(Minion):
	Class, race, name = "Neutral", "Beast", "Jungle Panther"
	mana, attack, health = 3, 4, 2
	numTargets, Effects, description = 0, "Stealth", "Stealth"
	name_CN = "丛林猎豹"
	
	
class KingMukla(Minion):
	Class, race, name = "Neutral", "Beast", "King Mukla"
	mana, attack, health = 3, 5, 5
	name_CN = "穆克拉"
	numTargets, Effects, description = 0, "", "Battlecry: Give your opponent 2 Bananas"
	index = "Battlecry~Legendary"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.addCardtoHand([Bananas, Bananas], 3-self.ID)
		
	
class LoneChampion(Minion):
	Class, race, name = "Neutral", "", "Lone Champion"
	mana, attack, health = 3, 2, 4
	name_CN = "孤胆英雄"
	numTargets, Effects, description = 0, "", "Battlecry: If you control no other minions, gain Taunt and Divine Shield"
	index = "Battlecry"
	def effCanTrig(self):
		self.effectViable = not self.Game.minionsonBoard(self.ID)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if len(self.Game.minionsonBoard(self.ID)) < 2:
			self.giveEnchant(self, multipleEffGains=(("Taunt", 1, None), ("Divine Shield", 1, None)), source=LoneChampion)
		
	
class MiniMage(Minion):
	Class, race, name = "Neutral", "", "Mini-Mage"
	mana, attack, health = 3, 3, 1
	numTargets, Effects, description = 0, "Stealth,Spell Damage", "Stealth, Spell Damage +1"
	name_CN = "小个子法师"
	
	
class RaidLeader(Minion):
	Class, race, name = "Neutral", "", "Raid Leader"
	mana, attack, health = 3, 2, 3
	numTargets, Effects, description = 0, "", "Your other minions have +1 Attack"
	name_CN = "团队领袖"
	aura = Aura_RaidLeader
	
	
class SouthseaCaptain(Minion):
	Class, race, name = "Neutral", "Pirate", "Southsea Captain"
	mana, attack, health = 3, 3, 3
	numTargets, Effects, description = 0, "", "Your other Pirates have +1/+1"
	name_CN = "南海船长"
	aura = Aura_SouthseaCaptain
	
	
class SpiderTank(Minion):
	Class, race, name = "Neutral", "Mech", "Spider Tank"
	mana, attack, health = 3, 3, 4
	numTargets, Effects, description = 0, "", ""
	name_CN = "蜘蛛坦克"
	
	
class StoneskinBasilisk(Minion):
	Class, race, name = "Neutral", "Beast", "Stoneskin Basilisk"
	mana, attack, health = 3, 1, 1
	numTargets, Effects, description = 0, "Divine Shield,Poisonous", "Divine Shield, Poisonous"
	name_CN = "石皮蜥蜴"
	
	
class BaronRivendare(Minion):
	Class, race, name = "Neutral", "", "Baron Rivendare"
	mana, attack, health = 4, 1, 7
	name_CN = "瑞文戴尔男爵"
	numTargets, Effects, description = 0, "", "Your minions trigger their Deathrattles twice"
	index = "Legendary"
	aura = GameRuleAura_BaronRivendare
	
	
class BigGameHunter(Minion):
	Class, race, name = "Neutral", "", "Big Game Hunter"
	mana, attack, health = 4, 4, 2
	name_CN = "王牌猎人"
	numTargets, Effects, description = 1, "", "Battlecry: Destroy a minion with 7 or more Attack"
	index = "Battlecry"
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj is not self and obj.attack > 6 and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.Game.kill(self, target)
		
	
class ChillwindYeti(Minion):
	Class, race, name = "Neutral", "", "Chillwind Yeti"
	mana, attack, health = 4, 4, 5
	numTargets, Effects, description = 0, "", ""
	name_CN = "冰风雪人"
	
	
class DarkIronDwarf(Minion):
	Class, race, name = "Neutral", "", "Dark Iron Dwarf"
	mana, attack, health = 4, 4, 4
	name_CN = "黑铁矮人"
	numTargets, Effects, description = 1, "", "Battlecry: Give a minion +2 Attack"
	index = "Battlecry"
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj is not self and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(target, 2, 0, statEnchant=Enchantment(DarkIronDwarf, 2, 0, until=0))
		
	
class DefenderofArgus(Minion):
	Class, race, name = "Neutral", "", "Defender of Argus"
	mana, attack, health = 4, 3, 3
	name_CN = "阿古斯防御者"
	numTargets, Effects, description = 0, "", "Battlecry: Given adjacent minions +1/+1 and Taunt"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.onBoard: self.giveEnchant(self.Game.neighbors2(self)[0], 1, 1, effGain="Taunt", source=DefenderofArgus)
		
	
class GrimNecromancer(Minion):
	Class, race, name = "Neutral", "", "Grim Necromancer"
	mana, attack, health = 4, 2, 4
	name_CN = "冷酷的死灵法师"
	numTargets, Effects, description = 0, "", "Battlecry: Summon two 1/1 Skeletons"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon([Skeleton(self.Game, self.ID) for _ in (0, 1)], relative="<>")
		
	
class SenjinShieldmasta(Minion):
	Class, race, name = "Neutral", "", "Sen'jin Shieldmasta"
	mana, attack, health = 4, 3, 5
	numTargets, Effects, description = 0, "Taunt", "Taunt"
	name_CN = "森金持盾卫士"
	
	
class SI7Infiltrator(Minion):
	Class, race, name = "Neutral", "", "SI:7 Infiltrator"
	mana, attack, health = 4, 5, 4
	name_CN = "军情七处渗透者"
	numTargets, Effects, description = 0, "", "Battlecry: Destroy a random enemy Secret"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if numSecrets := len(self.Game.Secrets.secrets[3-self.ID]):
			self.Game.Secrets.extractSecrets(3-self.ID, numpyRandint(numSecrets), initiator=self)
		
	
class VioletTeacher(Minion):
	Class, race, name = "Neutral", "", "Violet Teacher"
	mana, attack, health = 4, 3, 5
	numTargets, Effects, description = 0, "", "Whenever you cast a spell, summon a 1/1 Violet Apperentice"
	name_CN = "紫罗兰教师"
	trigBoard = Trig_VioletTeacher
	
	
class FacelessManipulator(Minion):
	Class, race, name = "Neutral", "", "Faceless Manipulator"
	mana, attack, health = 5, 3, 3
	name_CN = "无面操纵者"
	numTargets, Effects, description = 1, "", "Battlecry: Choose a minion and become a copy of it"
	index = "Battlecry"
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj is not self and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		#如果self.Game.cardinPlay不再等于自己，说明这个随从的已经触发了变形而不会再继续变形。战吼触发时自己不能死亡。
		if not self.dead and self.Game.cardinPlay is self:
			self.Game.transform(self, self.copyCard(target[0], self.ID))
		
	
class GurubashiBerserker(Minion):
	Class, race, name = "Neutral", "", "Gurubashi Berserker"
	mana, attack, health = 5, 2, 8
	numTargets, Effects, description = 0, "", "Whenever this minion takes damage, gain +3 Attack"
	name_CN = "古拉巴什狂暴者"
	trigBoard = Trig_GurubashiBerserker
	
	
class OverlordRunthak(Minion):
	Class, race, name = "Neutral", "", "Overlord Runthak"
	mana, attack, health = 5, 3, 6
	name_CN = "伦萨克大王"
	numTargets, Effects, description = 0, "Rush", "Rush. Whenever this minion attacks, give +1/+1 to all minions in your hand"
	index = "Legendary"
	trigBoard = Trig_OverlordRunthak
	
	
class StranglethornTiger(Minion):
	Class, race, name = "Neutral", "Beast", "Stranglethorn Tiger"
	mana, attack, health = 5, 5, 5
	numTargets, Effects, description = 0, "Stealth", "Stealth"
	name_CN = "荆棘谷猛虎"
	
	
class TaelanFordring(Minion):
	Class, race, name = "Neutral", "", "Taelan Fordring"
	mana, attack, health = 5, 3, 3
	name_CN = "泰兰·弗丁"
	numTargets, Effects, description = 0, "Taunt,Divine Shield", "Taunt, Divine Shield. Deathrattle: Draw your hightest-Cost minion"
	index = "Legendary"
	deathrattle = Death_TaelanFordring
	
	
class CairneBloodhoof(Minion):
	Class, race, name = "Neutral", "", "Cairne Bloodhoof"
	mana, attack, health = 6, 5, 5
	name_CN = "凯恩·血蹄"
	numTargets, Effects, description = 0, "", "Deathrattle: Summon a 4/5 Baine Bloodhoof"
	index = "Legendary"
	deathrattle = Death_CairneBloodhoof
	
	
class GadgetzanAuctioneer(Minion):
	Class, race, name = "Neutral", "", "Gadgetzan Auctioneer"
	mana, attack, health = 6, 4, 4
	numTargets, Effects, description = 0, "", "Whenever you cast a spell, draw a card"
	name_CN = "加基森拍卖师"
	trigBoard = Trig_GadgetzanAuctioneer
	
	
class HighInquisitorWhitemane(Minion):
	Class, race, name = "Neutral", "", "High Inquisitor Whitemane"
	mana, attack, health = 6, 5, 7
	name_CN = "大检察官怀特迈恩"
	numTargets, Effects, description = 0, "", "Battlecry: Summon all friendly minions that died this turn"
	index = "Battlecry~Legendary"
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.examDeads(self.ID, turnInd=self.Game.turnInd)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if tups := self.Game.Counters.examDeads(self.ID, turnInd=self.Game.turnInd, veri_sum_ls=2):
			numpyShuffle(tups)
			self.summon([self.Game.fabCard(tup, self.ID, self) for tup in tups])

	
class BaronGeddon(Minion):
	Class, race, name = "Neutral", "Elemental", "Baron Geddon"
	mana, attack, health = 7, 7, 7
	name_CN = "迦顿男爵"
	numTargets, Effects, description = 0, "", "At the end of turn, deal 2 damage to ALL other characters"
	index = "Legendary"
	trigBoard = Trig_BaronGeddon
	
	
class BarrensStablehand(Minion):
	Class, race, name = "Neutral", "", "Barrens Stablehand"
	mana, attack, health = 7, 5, 5
	name_CN = "贫瘠之地饲养员"
	numTargets, Effects, description = 0, "", "Battlecry: Summon a random Beast"
	index = "Battlecry"
	poolIdentifier = "Beasts to Summon"
	@classmethod
	def generatePool(cls, pools):
		return "Beasts to Summon", pools.MinionswithRace["Beast"]
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon(numpyChoice(self.rngPool("Beasts to Summon"))(self.Game, self.ID))
		
	
class NozdormutheEternal(Minion):
	Class, race, name = "Neutral", "Dragon", "Nozdormu the Eternal"
	mana, attack, health = 7, 8, 8
	name_CN = "永恒者诺兹多姆"
	numTargets, Effects, description = 0, "", "Start of Game: If this is in BOTH players' decks, turns are only 15 seconds long"
	index = "Legendary"
	
	
class Stormwatcher(Minion):
	Class, race, name = "Neutral", "Elemental", "Stormwatcher"
	mana, attack, health = 7, 4, 8
	numTargets, Effects, description = 0, "Windfury", "Windfury"
	name_CN = "风暴看守"
	
	
class StormwindChampion(Minion):
	Class, race, name = "Neutral", "", "Stormwind Champion"
	mana, attack, health = 7, 7, 7
	numTargets, Effects, description = 0, "", "Your other minions have +1/+1"
	name_CN = "暴风城勇士"
	aura = Aura_StormwindChampion
	
	
class ArcaneDevourer(Minion):
	Class, race, name = "Neutral", "Elemental", "Arcane Devourer"
	mana, attack, health = 8, 4, 8
	numTargets, Effects, description = 0, "", "Whenever you cast a spell, gain +2/+2"
	name_CN = "奥术吞噬者"
	trigBoard = Trig_ArcaneDevourer
	
	
class AlexstraszatheLifeBinder(Minion):
	Class, race, name = "Neutral", "Dragon", "Alexstrasza the Life-Binder"
	mana, attack, health = 9, 8, 8
	name_CN = "生命的缚誓者阿莱克丝塔萨"
	numTargets, Effects, description = 1, "", "Battlecry: Choose a character. If it's friendly, restore 8 Health. If it's an enemy, deal 8 damage"
	index = "Battlecry~Legendary"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for obj in target:
			if obj.ID == self.ID: self.heals(obj, self.calcHeal(8))
			else: self.dealsDamage(obj, 8)
		
	
class MalygostheSpellweaver(Minion):
	Class, race, name = "Neutral", "Dragon", "Malygos the Spellweaver"
	mana, attack, health = 9, 4, 12
	name_CN = "织法者玛里苟斯"
	numTargets, Effects, description = 0, "", "Battlecry: Draw spells until your hand is full"
	index = "Battlecry~Legendary"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		while self.Game.Hand_Deck.handNotFull(self.ID):
			if not self.drawCertainCard(lambda card: card.category == "Spell")[0]: break
		
	
class OnyxiatheBroodmother(Minion):
	Class, race, name = "Neutral", "Dragon", "Onyxia the Broodmother"
	mana, attack, health = 9, 8, 8
	name_CN = "龙巢之母奥妮克希亚"
	numTargets, Effects, description = 0, "", "At the end of your turn, fill your board with 1/1 Whelps"
	index = "Legendary"
	trigBoard = Trig_OnyxiatheBroodmother
	
	
class SleepyDragon(Minion):
	Class, race, name = "Neutral", "Dragon", "Sleepy Dragon"
	mana, attack, health = 9, 4, 12
	numTargets, Effects, description = 0, "Taunt", "Taunt"
	name_CN = "贪睡巨龙"
	
	
class YseratheDreamer(Minion):
	Class, race, name = "Neutral", "Dragon", "Ysera the Dreamer"
	mana, attack, health = 9, 4, 12
	name_CN = "沉睡者伊瑟拉"
	numTargets, Effects, description = 0, "", "Battlecry: Add one of each Dream card to your hand"
	index = "Battlecry~Legendary"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.addCardtoHand([Dream, Nightmare, YseraAwakens, LaughingSister, EmeraldDrake], self.ID)
		
	
class DeathwingtheDestroyer(Minion):
	Class, race, name = "Neutral", "Dragon", "Deathwing the Destroyer"
	mana, attack, health = 10, 12, 12
	name_CN = "灭世者死亡之翼"
	numTargets, Effects, description = 0, "", "Battlecry: Destroy all other minions. Discard a card for each destroyed"
	index = "Battlecry~Legendary"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		ID, game = self.ID, self.Game
		game.kill(self, (minions := game.minionsAlive(exclude=self)))
		if (handSize := len(game.Hand_Deck.hands[ID])) and minions:
			game.Hand_Deck.discard(self.ID, numpyChoice(range(handSize), min(handSize, len(minions)), replace=False))
		
	
class ClockworkGiant(Minion):
	Class, race, name = "Neutral", "Mech", "Clockwork Giant"
	mana, attack, health = 12, 8, 8
	numTargets, Effects, description = 0, "", "Costs (1) less for each other card in your opponent's hand"
	name_CN = "发条巨人"
	trigHand = Trig_ClockworkGiant
	def selfManaChange(self):
		self.mana -= len(self.Game.Hand_Deck.hands[3-self.ID])
		
	
class Battlefiend(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Battlefiend"
	mana, attack, health = 1, 1, 2
	numTargets, Effects, description = 0, "", "After your hero attacks, gain +1 Attack"
	name_CN = "战斗邪犬"
	trigBoard = Trig_Battlefiend
	
	
class ChaosStrike(Spell):
	Class, school, name = "Demon Hunter", "Fel", "Chaos Strike"
	numTargets, mana, Effects = 0, 2, ""
	description = "Give your hero +2 Attack this turn. Draw a card"
	name_CN = "混乱打击"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveHeroAttackArmor(self.ID, attGain=2, source=ChaosStrike)
		self.Game.Hand_Deck.drawCard(self.ID)
		
	
class CrimsonSigilRunner(Minion):
	Class, race, name = "Demon Hunter", "", "Crimson Sigil Runner"
	mana, attack, health = 1, 1, 1
	numTargets, Effects, description = 0, "", "Outcast: Draw a card"
	name_CN = "火色魔印奔行者"
	index = "Outcast"
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.outcastcanTrig(self)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if posinHand in (-1, 0):
			self.Game.Hand_Deck.drawCard(self.ID)
		
	
class FeastofSouls(Spell):
	Class, school, name = "Demon Hunter", "Shadow", "Feast of Souls"
	numTargets, mana, Effects = 0, 2, ""
	description = "Draw a card for each friendly minion that died this turn"
	name_CN = "灵魂盛宴"
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.examDeads(self.ID, turnInd=self.Game.turnInd)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for _ in self.Game.Counters.examDeads(self.ID, turnInd=self.Game.turnInd, veri_sum_ls=2):
			self.Game.Hand_Deck.drawCard(self.ID)
		
	
class KorvasBloodthorn(Minion):
	Class, race, name = "Demon Hunter", "", "Kor'vas Bloodthorn"
	mana, attack, health = 2, 2, 2
	name_CN = "考瓦斯·血棘"
	numTargets, Effects, description = 0, "Charge,Lifesteal", "Charge, Lifesteal. After you play a card with Outcast, return this to your hand"
	index = "Legendary"
	trigBoard = Trig_KorvasBloodthorn
	
	
class SightlessWatcher(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Sightless Watcher"
	mana, attack, health = 2, 3, 2
	name_CN = "盲眼观察者"
	numTargets, Effects, description = 0, "", "Battlecry: Look at 3 cards in your deck. Choose one to put on top"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		_, i = self.discoverfrom(comment)
		if i > -1:
			deck = self.Game.Hand_Deck.decks[self.ID]
			deck.append(deck.pop(i))
		
	
class SpectralSight(Spell):
	Class, school, name = "Demon Hunter", "", "Spectral Sight"
	numTargets, mana, Effects = 0, 2, ""
	description = "Draw a cards. Outscast: Draw another"
	name_CN = "幽灵视觉"
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.outcastcanTrig(self)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.Game.Hand_Deck.drawCard(self.ID)
		if posinHand in (-1, 0):
			self.Game.Hand_Deck.drawCard(self.ID)
		
	
class AldrachiWarblades(Weapon):
	Class, name, description = "Demon Hunter", "Aldrachi Warblades", "Lifesteal"
	mana, attack, durability, Effects = 3, 2, 2, "Lifesteal"
	name_CN = "奥达奇战刃"
	
	
class CoordinatedStrike(Spell):
	Class, school, name = "Demon Hunter", "", "Coordinated Strike"
	numTargets, mana, Effects = 0, 3, ""
	description = "Summon three 1/1 Illidari with Rush"
	name_CN = "协同打击"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon([IllidariInitiate(self.Game, self.ID) for _ in (0, 1, 2)])
		
	
class EyeBeam(Spell):
	Class, school, name = "Demon Hunter", "Fel", "Eye Beam"
	numTargets, mana, Effects = 1, 3, "Lifesteal"
	description = "Lifesteal. Deal 3 damage to a minion. Outcast: This costs (1)"
	name_CN = "眼棱"
	index = "Outcast"
	trigHand = Trig_EyeBeam
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.outcastcanTrig(self)
		
	def selfManaChange(self):
		if self.Game.Hand_Deck.outcastcanTrig(self): self.mana = 1
		
	def text(self): return self.calcDamage(3)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(target, self.calcDamage(3))
		
	
class GanargGlaivesmith(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Gan'arg Glaivesmith"
	mana, attack, health = 3, 3, 2
	numTargets, Effects, description = 0, "", "Outcast: Give your hero +3 Attack this turn"
	name_CN = "甘尔葛战刃铸造师"
	index = "Outcast"
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.outcastcanTrig(self)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if posinHand in (-1, 0):
			self.giveHeroAttackArmor(self.ID, attGain=3, source=GanargGlaivesmith)
		
	
class AshtongueBattlelord(Minion):
	Class, race, name = "Demon Hunter", "", "Ashtongue Battlelord"
	mana, attack, health = 4, 3, 5
	numTargets, Effects, description = 0, "Taunt,Lifesteal", "Taunt, Lifesteal"
	name_CN = "灰舌将领"
	
	
class RagingFelscreamer(Minion):
	Class, race, name = "Demon Hunter", "", "Raging Felscreamer"
	mana, attack, health = 4, 4, 4
	name_CN = "暴怒邪吼者"
	numTargets, Effects, description = 0, "", "Battlecry: The next Demon you play costs (2) less"
	index = "Battlecry"
	trigEffect = GamaManaAura_RagingFelscreamer
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		GamaManaAura_RagingFelscreamer(self.Game, self.ID).auraAppears()
		
	
class ChaosNova(Spell):
	Class, school, name = "Demon Hunter", "Fel", "Chaos Nova"
	numTargets, mana, Effects = 0, 5, ""
	description = "Deal 4 damage to all minions"
	name_CN = "混乱新星"
	def text(self): return self.calcDamage(4)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(self.Game.minionsonBoard(), self.calcDamage(4))
		
	
class WarglaivesofAzzinoth(Weapon):
	Class, name, description = "Demon Hunter", "Warglaives of Azzinoth", "After attacking a minion, your hero may attack again"
	mana, attack, durability, Effects = 5, 3, 3, ""
	name_CN = "埃辛诺斯战刃"
	trigBoard = Trig_WarglaivesofAzzinoth
	
	
class IllidariInquisitor(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Illidari Inquisitor"
	mana, attack, health = 8, 8, 8
	numTargets, Effects, description = 0, "Rush", "Rush. After your hero attacks an enemy, this attacks it too"
	name_CN = "伊利达雷审判官"
	trigBoard = Trig_IllidariInquisitor
	
	
class Innervate(Spell):
	Class, school, name = "Druid", "Nature", "Innervate"
	numTargets, mana, Effects = 0, 0, ""
	description = "Gain 1 Mana Crystal this turn only"
	description_CN = "在本回合中，获得一个法力水晶。"
	name_CN = "激活"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.Game.Manas.gainTempManaCrystal(1, self.ID)
		
	
class Pounce(Spell):
	Class, school, name = "Druid", "", "Pounce"
	numTargets, mana, Effects = 0, 0, ""
	description = "Give your hero +2 Attack this turn"
	description_CN = "在本回合中，使你的英雄获得+2攻击力"
	name_CN = "飞扑"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveHeroAttackArmor(self.ID, attGain=2, source=Pounce)
		
	
class EnchantedRaven(Minion):
	Class, race, name = "Druid", "Beast", "Enchanted Raven"
	mana, attack, health = 1, 2, 2
	numTargets, Effects, description = 0, "", ""
	description_CN = ""
	name_CN = "魔法乌鸦"
	
	
class MarkoftheWild(Spell):
	Class, school, name = "Druid", "Nature", "Mark of the Wild"
	numTargets, mana, Effects = 1, 2, ""
	description = "Give a minion +2/+3 and Taunt"
	name_CN = "野性印记"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(target, 2, 3, effGain="Taunt", source=MarkoftheWild)
		
	
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
	numTargets, mana, Effects = 0, 2, ""
	name_CN = "野性之力"
	description = "Choose One - Give your minions +1/+1; or Summon a 3/2 Panther"
	options = (LeaderofthePack_Option, SummonaPanther_Option)
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if choice: self.summon(Panther(self.Game, self.ID))
		if choice < 1: self.giveEnchant(self.Game.minionsonBoard(self.ID), 1, 1, source=PoweroftheWild)
		
	
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
	numTargets, mana, Effects = 0, 3, ""
	name_CN = "野性之怒"
	description = "Choose One - Give your hero +4 Attack this turn; or Give your hero 8 Armor"
	options = (EvolveSpines_Option, EvolveScales_Option)
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveHeroAttackArmor(self.ID, attGain=4*(choice<1), armor=8*(choice!=0), source=FeralRage)
		
	
class Landscaping(Spell):
	Class, school, name = "Druid", "Nature", "Landscaping"
	numTargets, mana, Effects = 0, 3, ""
	description = "Summon two 2/2 Treants"
	name_CN = "植树造林"
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon([Treant_Classic(self.Game, self.ID) for _ in (0, 1)])
		
	
class WildGrowth(Spell):
	Class, school, name = "Druid", "Nature", "Wild Growth"
	numTargets, mana, Effects = 0, 3, ""
	description = "Gain an empty Mana Crystal"
	name_CN = "野性成长"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if not self.Game.Manas.gainEmptyManaCrystal(1, self.ID):
			self.addCardtoHand(ExcessMana, self.ID)
		
	
class NordrassilDruid(Minion):
	Class, race, name = "Druid", "", "Nordrassil Druid"
	mana, attack, health = 4, 3, 5
	name_CN = "诺达希尔德鲁伊"
	numTargets, Effects, description = 0, "", "Battlecry: Your next spell this turn costs (3) less"
	index = "Battlecry"
	trigEffect = GameManaAura_NordrassilDruid
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		GameManaAura_NordrassilDruid(self.Game, self.ID).auraAppears()
		
	
class SouloftheForest(Spell):
	Class, school, name = "Druid", "Nature", "Soul of the Forest"
	numTargets, mana, Effects = 0, 4, ""
	description = "Give your minions 'Deathrattle: Summon a 2/2 Treant'"
	name_CN = "丛林之魂"
	trigEffect = Death_SouloftheForest
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(self.Game.minionsonBoard(self.ID), trig=Death_SouloftheForest, trigType="Deathrattle")
		
	
class CatForm_Option(Option):
	name, category, description = "Cat Form", "Option_Minion", "Rush"
	mana, attack, health = 5, 5, 4
	
	
class BearForm_Option(Option):
	name, category, description = "Bear Form", "Option_Minion", "+2 health and Taunt"
	mana, attack, health = 5, 5, 6
	
	
class DruidoftheClaw(Minion):
	Class, race, name = "Druid", "", "Druid of the Claw"
	mana, attack, health = 5, 5, 4
	name_CN = "利爪德鲁伊"
	numTargets, Effects, description = 0, "", "Choose One - Transform into a 5/4 with Rush; or a 5/6 with Taunt"
	options = (CatForm_Option, BearForm_Option)
	def appears_fromPlay(self, choice):
		return appears_fromPlay_Druid(self, choice, (DruidoftheClaw_Rush, DruidoftheClaw_Taunt, DruidoftheClaw_Both))
		
	
class ForceofNature(Spell):
	Class, school, name = "Druid", "Nature", "Force of Nature"
	numTargets, mana, Effects = 0, 5, ""
	description = "Summon three 2/2 Treants"
	name_CN = "自然之力"
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon([Treant_Classic(self.Game, self.ID) for _ in (0, 1, 2)])
		
	
class MenagerieWarden(Minion):
	Class, race, name = "Druid", "", "Menagerie Warden"
	mana, attack, health = 5, 4, 4
	name_CN = "展览馆守卫"
	numTargets, Effects, description = 1, "", "Battlecry: Choose a friendly Beast. Summon a copy of it"
	index = "Battlecry"
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists(self.ID)
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.ID == self.ID and "Beast" in obj.race and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for obj in target: self.summon(self.copyCard(obj, self.ID), position=obj.pos+1)
		
	
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
	numTargets, mana, Effects = 0, 6, ""
	name_CN = "滋养"
	description = "Choose One - Gain 2 Mana Crystals; or Draw 3 cards"
	options = (RampantGrowth_Option, Enrich_Option)
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if choice < 1:
			self.Game.Manas.gainManaCrystal(2, self.ID)
		if choice:
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
	name_CN = "战争古树"
	numTargets, Effects, description = 0, "", "Choose One - +5 Attack; or +5 Health and Taunt"
	options = (Uproot_Option, Rooted_Option)
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if choice < 1: self.giveEnchant(self, 5, 0, source=AncientofWar)
		if choice: self.giveEnchant(self, 0, 5, effGain="Taunt", source=AncientofWar)
		
	
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
	name_CN = "塞纳留斯"
	numTargets, Effects, description = 0, "", "Choose One- Give your other minions +2/+2; or Summon two 2/2 Treants with Taunt"
	index = "Legendary"
	options = (DemigodsFavor_Option, ShandosLesson_Option)
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if choice: self.summon([Treant_Classic_Taunt(self.Game, self.ID) for _ in (0, 1)], relative="<>")
		if choice < 1: self.giveEnchant(self.Game.minionsonBoard(self.ID, exclude=self), 2, 2, source=Cenarius)
		
	
class ArcaneShot(Spell):
	Class, school, name = "Hunter", "Arcane", "Arcane Shot"
	numTargets, mana, Effects = 1, 1, ""
	description = "Deal 2 damage"
	name_CN = "奥术射击"
	def text(self): return self.calcDamage(2)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(target, self.calcDamage(2))
		
	
class LockandLoad(Spell):
	Class, school, name = "Hunter", "", "Lock and Load"
	numTargets, mana, Effects = 0, 1, ""
	description = "Each time you cast a spell this turn, add a random Hunter card to your hand"
	name_CN = "子弹上膛"
	trigEffect = LockandLoad_Effect
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		LockandLoad_Effect(self.Game, self.ID).connect()
		
	
class Tracking(Spell):
	Class, school, name = "Hunter", "", "Tracking"
	numTargets, mana, Effects = 0, 1, ""
	description = "Discover a card from your deck"
	name_CN = "追踪术"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		_, i = self.discoverfrom(comment)
		if i > -1: self.Game.Hand_Deck.drawCard(self.ID, i)
		
	
class Webspinner(Minion):
	Class, race, name = "Hunter", "Beast", "Webspinner"
	mana, attack, health = 1, 1, 1
	numTargets, Effects, description = 0, "", "Deathrattle: Add a random Beast to your hand"
	name_CN = "结网蛛"
	deathrattle = Death_Webspinner
	
	
class ExplosiveTrap(Secret):
	Class, school, name = "Hunter", "Fire", "Explosive Trap"
	numTargets, mana, Effects = 0, 2, ""
	description = "Secret: When your hero is attacked, deal 2 damage to all enemies"
	name_CN = "爆炸陷阱"
	trigBoard = Trig_ExplosiveTrap
	def text(self): return self.calcDamage(2)
		
	
class FreezingTrap(Secret):
	Class, school, name = "Hunter", "Frost", "Freezing Trap"
	numTargets, mana, Effects = 0, 2, ""
	description = "Secret: When an enemy minion attacks, return it to its owner's hand. It costs (2) more."
	name_CN = "冰冻陷阱"
	trigBoard = Trig_FreezingTrap
	num = 2
	
	
class HeadhuntersHatchet(Weapon):
	Class, name, description = "Hunter", "Headhunter's Hatchet", "Battlecry: If you control a Beast, gain +1 Durability"
	mana, attack, durability, Effects = 2, 2, 2, ""
	name_CN = "猎头者之斧"
	index = "Battlecry"
	def effCanTrig(self):
		self.effectViable = any("Beast" in minion.race for minion in self.Game.minionsonBoard(self.ID))
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		#Invoker must be a weapon in order to gain Durability
		if self.Game.minionsonBoard(self.ID, race="Beast") and self.category == "Weapon":
			self.giveEnchant(self, 0, 1, source=HeadhuntersHatchet)
		
	
class QuickShot(Spell):
	Class, school, name = "Hunter", "", "Quick Shot"
	numTargets, mana, Effects = 1, 2, ""
	description = "Deal 3 damage. If your hand is empty, draw a card"
	name_CN = "快速射击"
	def effCanTrig(self):
		self.effectViable = len(self.Game.Hand_Deck.hands[self.ID]) < 2
		
	def text(self): return self.calcDamage(3)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(target, self.calcDamage(3))
		if not self.Game.Hand_Deck.hands[self.ID]: self.Game.Hand_Deck.drawCard(self.ID)
		
	
class ScavengingHyena(Minion):
	Class, race, name = "Hunter", "Beast", "Scavenging Hyena"
	mana, attack, health = 2, 2, 2
	numTargets, Effects, description = 0, "", "Whenever a friendly Beast dies, gain +2/+1"
	name_CN = "食腐土狼"
	trigBoard = Trig_ScavengingHyena
	
	
class SelectiveBreeder(Minion):
	Class, race, name = "Hunter", "", "Selective Breeder"
	mana, attack, health = 2, 1, 3
	name_CN = "选种饲养员"
	numTargets, Effects, description = 0, "", "Battlecry: Discover a copy of a Beast in your deck"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		card, _ = self.discoverfrom(comment, cond=lambda card: "Beast" in card.race)
		if card: self.addCardtoHand(self.copyCard(card, self.ID), self.ID, byDiscover=True)
		
	
class SnakeTrap(Secret):
	Class, school, name = "Hunter", "", "Snake Trap"
	numTargets, mana, Effects = 0, 2, ""
	description = "Secret: When one of your minions is attacked, summon three 1/1 Snakes"
	name_CN = "毒蛇陷阱"
	trigBoard = Trig_SnakeTrap
	snake = Snake
	
	
class Bearshark(Minion):
	Class, race, name = "Hunter", "Beast", "Bearshark"
	mana, attack, health = 3, 4, 3
	numTargets, Effects, description = 0, "Evasive", "Can't be targeted by spells or Hero Powers"
	name_CN = "熊鲨"
	
	
class DeadlyShot(Spell):
	Class, school, name = "Hunter", "", "Deadly Shot"
	numTargets, mana, Effects = 0, 3, ""
	description = "Destroy a random enemy minion"
	name_CN = "致命射击"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		minions = self.Game.minionsAlive(3 - self.ID)
		if minions: self.Game.kill(self, numpyChoice(minions))
		
	
class DireFrenzy(Spell):
	Class, school, name = "Hunter", "", "Dire Frenzy"
	numTargets, mana, Effects = 1, 4, ""
	description = "Give a Beast +3/+3. Shuffle three copies into your deck with +3/+3"
	name_CN = "凶猛狂暴"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and "Beast" in obj.race and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for obj in target:
			self.giveEnchant(obj, 3, 3, source=DireFrenzy)
			beast, game, ID = type(obj), self.Game, self.ID
			self.giveEnchant((cards := [beast(game, ID) for _ in (0, 1, 2)]), 3, 3, source=DireFrenzy)
			self.shuffleintoDeck(cards)
		
	
class SavannahHighmane(Minion):
	Class, race, name = "Hunter", "Beast", "Savannah Highmane"
	mana, attack, health = 6, 6, 5
	numTargets, Effects, description = 0, "", "Deathrattle: Summon two 2/2 Hyenas"
	name_CN = "长鬃草原狮"
	deathrattle = Death_SavannahHighmane
	
	
class KingKrush(Minion):
	Class, race, name = "Hunter", "Beast", "King Krush"
	mana, attack, health = 9, 8, 8
	name_CN = "暴龙王克鲁什"
	numTargets, Effects, description = 0, "Charge", "Charge"
	index = "Legendary"
	
	
class BabblingBook(Minion):
	Class, race, name = "Mage", "", "Babbling Book"
	mana, attack, health = 1, 1, 1
	name_CN = "呓语魔典"
	numTargets, Effects, description = 0, "", "Battlecry: Add a random Mage spell to your hand"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.addCardtoHand(numpyChoice(self.rngPool("Mage Spells")), self.ID)
		
	
class ShootingStar(Spell):
	Class, school, name = "Mage", "Arcane", "Shooting Star"
	numTargets, mana, Effects = 1, 1, ""
	description = "Deal 1 damage to a minion and its neighbors"
	name_CN = "迸射流星"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def text(self): return self.calcDamage(1)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for obj in target:
			self.dealsDamage([obj]+self.Game.neighbors2(obj)[0], self.calcDamage(1))
		
	
class SnapFreeze(Spell):
	Class, school, name = "Mage", "Frost", "Snap Freeze"
	numTargets, mana, Effects = 1, 1, ""
	description = "Freeze a minion. If it's already Frozen, destroy it"
	name_CN = "急速冷冻"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def effCanTrig(self):
		self.effectViable = any(minion.effects["Frozen"] > 0 for minion in self.Game.minionsonBoard())
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for obj in target:
			if obj.effects["Frozen"]: self.Game.kill(self, obj)
			else: self.freeze(obj)
		
	
class Arcanologist(Minion):
	Class, race, name = "Mage", "", "Arcanologist"
	mana, attack, health = 2, 2, 3
	name_CN = "秘法学家"
	numTargets, Effects, description = 0, "", "Battlecry: Draw a Secret"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.drawCertainCard(lambda card: card.race == "Secret")
		
	
class FallenHero(Minion):
	Class, race, name = "Mage", "", "Fallen Hero"
	mana, attack, health = 2, 3, 2
	numTargets, Effects, description = 0, "", "Your Hero Power deals 1 extra damage"
	name_CN = "英雄之魂"
	aura = GameRuleAura_FallenHero
	
	
class ArcaneIntellect(Spell):
	Class, school, name = "Mage", "Arcane", "Arcane Intellect"
	numTargets, mana, Effects = 0, 3, ""
	description = "Draw 2 cards"
	name_CN = "奥术智慧"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.Game.Hand_Deck.drawCard(self.ID)
		self.Game.Hand_Deck.drawCard(self.ID)
		
	
class ConeofCold(Spell):
	Class, school, name = "Mage", "Frost", "Cone of Cold"
	numTargets, mana, Effects = 1, 3, ""
	description = "Freeze a minion and the minions next to it, and deal 1 damage to them"
	name_CN = "冰锥术"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def text(self): return self.calcDamage(1)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		damage = self.calcDamage(1)
		for obj in target:
			self.dealsDamage(objs := [obj]+self.Game.neighbors2(obj)[0], damage)
			self.freeze(objs)
		
	
class Counterspell(Secret):
	Class, school, name = "Mage", "Arcane", "Counterspell"
	numTargets, mana, Effects = 0, 3, ""
	description = "Secret: When your opponent casts a spell, Counter it."
	name_CN = "法术反制"
	trigBoard = Trig_Counterspell
	
	
class IceBarrier(Secret):
	Class, school, name = "Mage", "Frost", "Ice Barrier"
	numTargets, mana, Effects = 0, 3, ""
	description = "Secret: When your hero is attacked, gain 8 Armor"
	name_CN = "寒冰护体"
	trigBoard = Trig_IceBarrier
	
	
class MirrorEntity(Secret):
	Class, school, name = "Mage", "Arcane", "Mirror Entity"
	numTargets, mana, Effects = 0, 3, ""
	description = "Secret: After your opponent plays a minion, summon a copy of it"
	name_CN = "镜像实体"
	trigBoard = Trig_MirrorEntity
	
	
class Fireball(Spell):
	Class, school, name = "Mage", "Fire", "Fireball"
	numTargets, mana, Effects = 1, 4, ""
	description = "Deal 6 damage"
	name_CN = "火球术"
	def text(self): return self.calcDamage(6)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(target, self.calcDamage(6))
		
	
class WaterElemental(Minion):
	Class, race, name = "Mage", "Elemental", "Water Elemental"
	mana, attack, health = 4, 3, 6
	numTargets, Effects, description = 0, "", "Freeze any character damaged by this minion"
	name_CN = "水元素"
	trigBoard = Trig_FreezeDamaged
	
	
class AegwynntheGuardian(Minion):
	Class, race, name = "Mage", "", "Aegwynn, the Guardian"
	mana, attack, health = 5, 5, 5
	name_CN = "守护者艾格文"
	numTargets, Effects, description = 0, "Spell Damage_2", "Spell Damage +2. Deathrattle: The next minion your draw inherits these powers"
	index = "Legendary"
	deathrattle, trigEffect = Death_AegwynntheGuardian, AegwynntheGuardian_Effect
	
	
class EtherealConjurer(Minion):
	Class, race, name = "Mage", "", "Ethereal Conjurer"
	mana, attack, health = 5, 6, 4
	name_CN = "虚灵巫师"
	numTargets, Effects, description = 0, "", "Battlecry: Discover a spell"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.discoverNew(comment, lambda : self.rngPool(class4Discover(self)+" Spells"))
		
	
class ColdarraDrake(Minion):
	Class, race, name = "Mage", "Dragon", "Coldarra Drake"
	mana, attack, health = 6, 6, 7
	numTargets, Effects, description = 0, "", "You can use your Hero Power any number of times"
	name_CN = "考达拉幼龙"
	aura = GameRuleAura_ColdarraDrake
	
	
class Flamestrike(Spell):
	Class, school, name = "Mage", "Fire", "Flamestrike"
	numTargets, mana, Effects = 0, 7, ""
	description = "Deal 5 damage to all enemy minions"
	name_CN = "烈焰风暴"
	def text(self): return self.calcDamage(5)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(self.Game.minionsonBoard(3-self.ID), self.calcDamage(5))
		
	
class Avenge(Secret):
	Class, school, name = "Paladin", "Holy", "Avenge"
	numTargets, mana, Effects = 0, 1, ""
	description = "Secret: When one of your minion dies, give a random friendly minion +3/+2"
	name_CN = "复仇"
	trigBoard = Trig_Avenge
	
	
class NobleSacrifice(Secret):
	Class, school, name = "Paladin", "", "Noble Sacrifice"
	numTargets, mana, Effects = 0, 1, ""
	description = "Secret: When an enemy attacks, summon a 2/1 Defender as the new target"
	name_CN = "崇高牺牲"
	trigBoard = Trig_NobleSacrifice
	
	
class Reckoning(Secret):
	Class, school, name = "Paladin", "Holy", "Reckoning"
	numTargets, mana, Effects = 0, 1, ""
	description = "Secret: When an enemy minion deals 3 or more damage, destroy it"
	name_CN = "清算"
	trigBoard = Trig_Reckoning
	
	
class RighteousProtector(Minion):
	Class, race, name = "Paladin", "", "Righteous Protector"
	mana, attack, health = 1, 1, 1
	numTargets, Effects, description = 0, "Taunt,Divine Shield", "Taunt, Divine Shield"
	name_CN = "正义保护者"
	
	
class ArgentProtector(Minion):
	Class, race, name = "Paladin", "", "Argent Protector"
	mana, attack, health = 2, 3, 2
	name_CN = "银色保卫者"
	numTargets, Effects, description = 1, "", "Battlecry: Give a friendly minion Divine Shield"
	index = "Battlecry"
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists(self.ID)
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.ID == self.ID and obj is not self and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(target, effGain="Divine Shield", source=ArgentProtector)
		
	
class HolyLight(Spell):
	Class, school, name = "Paladin", "Holy", "Holy Light"
	numTargets, mana, Effects = 1, 2, ""
	description = "Restore 8 health"
	name_CN = "圣光术"
	def text(self): return self.calcHeal(8)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.heals(target, self.calcHeal(8))
		
	
class PursuitofJustice(Spell):
	Class, school, name = "Paladin", "Holy", "Pursuit of Justice"
	numTargets, mana, Effects = 0, 2, ""
	description = "Give +1 Attack to Silver Hand Recruits you summon this game"
	name_CN = "正义追击"
	trigEffect = GameAura_PursuitofJustice
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		GameAura_PursuitofJustice(self.Game, self.ID).auraAppears()
		
	
class AldorPeacekeeper(Minion):
	Class, race, name = "Paladin", "", "Aldor Peacekeeper"
	mana, attack, health = 3, 3, 3
	name_CN = "奥尔多卫士"
	numTargets, Effects, description = 1, "", "Battlecry: Change an enemy minion's Attack to 1"
	index = "Battlecry"
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists(3 - self.ID)
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.ID != self.ID and obj.onBoard and obj is not self
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.setStat(target, (1, None), source=AldorPeacekeeper)
		
	
class Equality(Spell):
	Class, school, name = "Paladin", "Holy", "Equality"
	numTargets, mana, Effects = 0, 3, ""
	description = "Change the Health of ALL minions to 1"
	name_CN = "生而平等"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.setStat(self.Game.minionsonBoard(), (None, 1), source=Equality)
		
	
class WarhorseTrainer(Minion):
	Class, race, name = "Paladin", "", "Warhorse Trainer"
	mana, attack, health = 3, 3, 4
	numTargets, Effects, description = 0, "", "Your Silver Hand Recruits have +1 Attack"
	name_CN = "战马训练师"
	aura = Aura_WarhorseTrainer
	
	
class BlessingofKings(Spell):
	Class, school, name = "Paladin", "Holy", "Blessing of Kings"
	numTargets, mana, Effects = 1, 4, ""
	description = "Give a minion +4/+4"
	name_CN = "王者祝福"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(target, 4, 4, source=BlessingofKings)
		
	
class Consecration(Spell):
	Class, school, name = "Paladin", "Holy", "Consecration"
	numTargets, mana, Effects = 0, 4, ""
	description = "Deal 2 damage to all enemies"
	name_CN = "奉献"
	def text(self): return self.calcDamage(2)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(self.Game.charsonBoard(3-self.ID), self.calcDamage(2))
		
	
class TruesilverChampion(Weapon):
	Class, name, description = "Paladin", "Truesilver Champion", "Whenever your hero attacks, restore 2 Health to it"
	mana, attack, durability, Effects = 4, 4, 2, ""
	name_CN = "真银圣剑"
	trigBoard = Trig_TruesilverChampion
	def text(self): return self.calcHeal(2)
		
	
class StandAgainstDarkness(Spell):
	Class, school, name = "Paladin", "", "Stand Against Darkness"
	numTargets, mana, Effects = 0, 5, ""
	description = "Summon five 1/1 Silver Hand Recruits"
	name_CN = "惩黑除恶"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon([SilverHandRecruit(self.Game, self.ID) for _ in range(5)])
		
	
class GuardianofKings(Minion):
	Class, race, name = "Paladin", "", "Guardian of Kings"
	mana, attack, health = 7, 5, 7
	name_CN = "列王守卫"
	numTargets, Effects, description = 0, "Taunt", "Taunt. Battlecry: Restore 6 health to your hero"
	index = "Battlecry"
	def text(self): return self.calcHeal(6)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.heals(self.Game.heroes[self.ID], self.calcHeal(6))
		
	
class TirionFordring(Minion):
	Class, race, name = "Paladin", "", "Tirion Fordring"
	mana, attack, health = 8, 6, 6
	name_CN = "提里昂弗丁"
	numTargets, Effects, description = 0, "Divine Shield,Taunt", "Divine Shield, Taunt. Deathrattle: Equip a 5/3 Ashbringer"
	index = "Legendary"
	deathrattle = Death_TirionFordring
	
	
class CrimsonClergy(Minion):
	Class, race, name = "Priest", "", "Crimson Clergy"
	mana, attack, health = 1, 1 ,3
	numTargets, Effects, description = 0, "", "After a friendly character is healed, gain +1 Attack"
	name_CN = "赤红教士"
	trigBoard = Trig_CrimsonClergy
	
	
class FlashHeal(Spell):
	Class, school, name = "Priest", "Holy", "Flash Heal"
	numTargets, mana, Effects = 1, 1, ""
	description = "Restore 5 Health"
	name_CN = "快速治疗"
	def text(self): return self.calcHeal(5)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.heals(target, self.calcHeal(5))
		
	
class FocusedWill(Spell):
	Class, school, name = "Priest", "", "Focused Will"
	numTargets, mana, Effects = 1, 1, ""
	description = "Silence a minion, then give it +3 Health"
	name_CN = "专注意志"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.Game.silenceMinions(target)
		self.giveEnchant(target, 0, 3, source=FocusedWill)
		
	
class HolySmite(Spell):
	Class, school, name = "Priest", "Holy", "Holy Smite"
	numTargets, mana, Effects = 1, 1, ""
	description = "Deal 3 damage to a minion"
	name_CN = "神圣惩击"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def text(self): return self.calcDamage(3)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(target, self.calcDamage(3))
		
	
class PsychicConjurer(Minion):
	Class, race, name = "Priest", "", "Psychic Conjurer"
	mana, attack, health = 1, 1, 1
	name_CN = "心灵咒术师"
	numTargets, Effects, description = 0, "", "Battlecry: Copy a card in your opponent's deck and add it to your hand"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if deck := self.Game.Hand_Deck.decks[3-self.ID]:
			self.addCardtoHand(self.copyCard(numpyChoice(deck), self.ID), self.ID)
		
	
class KulTiranChaplain(Minion):
	Class, race, name = "Priest", "", "Kul Tiran Chaplain"
	mana, attack, health = 2, 2, 3
	name_CN = "库尔提拉斯教士"
	numTargets, Effects, description = 1, "", "Battlecry: Give a friendly minion +2 Health"
	index = "Battlecry"
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists(self.ID, choice)
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.ID == self.ID and obj is not self and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(target, 0, 2, source=KulTiranChaplain)
		
	
class ShadowWordDeath(Spell):
	Class, school, name = "Priest", "Shadow", "Shadow Word: Death"
	numTargets, mana, Effects = 1, 2, ""
	description = "Destroy a minion with 5 or more Attack"
	name_CN = "暗言术：灭"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.attack > 4 and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.Game.kill(self, target)
		
	
class ThriveintheShadows(Spell):
	Class, school, name = "Priest", "Shadow", "Thrive in the Shadows"
	numTargets, mana, Effects = 0, 2, ""
	description = "Discover a spell from your deck"
	name_CN = "暗中生长"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		_, i = self.discoverfrom(comment, cond=lambda card: card.category == "Spell")
		if i > -1: self.Game.Hand_Deck.drawCard(self.ID, i)
		
	
class Lightspawn(Minion):
	Class, race, name = "Priest", "Elemental", "Lightspawn"
	mana, attack, health = 3, 0, 4
	numTargets, Effects, description = 0, "", "This minion's Attack is always equal to its Health"
	name_CN = "光耀之子"
	def statCheckResponse(self):
		#Even the latest aura can't change the attack. This effect is not an aura effect
		if self.onBoard and not self.silenced: self.attack = self.health
		
	
class ShadowedSpirit(Minion):
	Class, race, name = "Priest", "", "Shadowed Spirit"
	mana, attack, health = 3, 4, 3
	numTargets, Effects, description = 0, "", "Deathrattle: Deal 3 damage to the enemy hero"
	name_CN = "暗影之灵"
	deathrattle = Death_ShadowedSpirit
	
	
class Shadowform(Spell):
	Class, school, name = "Priest", "Shadow", "Shadowform"
	numTargets, mana, Effects = 0, 2, ""
	description = "Your Hero Power becomes 'Deal 2 damage'"
	name_CN = "暗影形态"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		MindSpike(self.Game, self.ID).replacePower()
		
	
class MindSpike(Power):
	mana, name, numTargets = 2, "Mind Spike", 1
	description = "Deal 2 damage"
	name_CN = "心灵尖刺"
	def dealsDmg(self): return True
		
	def text(self): return self.calcDamage(2)
		
	def effect(self, target=(), choice=0, comment=''):
		self.dealsDamage(target, self.calcDamage(2))
		
	
class HolyNova(Spell):
	Class, school, name = "Priest", "Holy", "Holy Nova"
	numTargets, mana, Effects = 0, 4, ""
	description = "Deal 2 damage to all enemy minions. Restore 2 Health to all friendly characters"
	name_CN = "神圣新星"
	def text(self): return "-%d, +%d"%(self.calcDamage(2), self.calcHeal(2))
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(self.Game.minionsonBoard(3-self.ID), self.calcDamage(2))
		self.heals(self.Game.charsonBoard(self.ID), self.calcHeal(2))
		
	
class PowerInfusion(Spell):
	Class, school, name = "Priest", "Holy", "Power Infusion"
	numTargets, mana, Effects = 1, 4, ""
	description = "Give a minion +2/+6"
	name_CN = "能量灌注"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(target, 2, 6, source=PowerInfusion)
		
	
class ShadowWordRuin(Spell):
	Class, school, name = "Priest", "Shadow", "Shadow Word: Ruin"
	numTargets, mana, Effects = 0, 4, ""
	description = "Destroy all minions with 5 or more Attack"
	name_CN = "暗言术：毁"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.Game.kill(self, [minion for minion in self.Game.minionsonBoard() if minion.attack > 4])
		
	
class TempleEnforcer(Minion):
	Class, race, name = "Priest", "", "Temple Enforcer"
	mana, attack, health = 5, 5, 6
	name_CN = "圣殿执行者"
	numTargets, Effects, description = 1, "", "Battlecry: Give a friendly minion +3 health"
	index = "Battlecry"
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists(self.ID, choice)
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.ID == self.ID and obj is not self and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(target, 0, 3, source=TempleEnforcer)
		
	
class NatalieSeline(Minion):
	Class, race, name = "Priest", "", "Natalie Seline"
	mana, attack, health = 8, 8, 1
	name_CN = "娜塔莉塞林"
	numTargets, Effects, description = 1, "", "Battlecry: Destroy a minion and gain its Health"
	index = "Battlecry~Legendary"
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj is not self and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for obj in target:
			healthGain = max(0, obj.health)
			self.Game.kill(self, obj)
			self.giveEnchant(self, 0, healthGain, source=NatalieSeline)
		
	
class Backstab(Spell):
	Class, school, name = "Rogue", "", "Backstab"
	numTargets, mana, Effects = 1, 0, ""
	description = "Deal 2 damage to an undamage minion"
	name_CN = "背刺"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.health == obj.health_max and obj.onBoard
		
	def text(self): return self.calcDamage(2)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(target, self.calcDamage(2))
		
	
class Preparation(Spell):
	Class, school, name = "Rogue", "", "Preparation"
	numTargets, mana, Effects = 0, 0, ""
	description = "The next spell you cast this turn costs (2) less"
	name_CN = "伺机待发"
	trigEffect = GameManaAura_Preparation
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		GameManaAura_Preparation(self.Game, self.ID).auraAppears()
		
	
class Shadowstep(Spell):
	Class, school, name = "Rogue", "Shadow", "Shadowstep"
	numTargets, mana, Effects = 1, 0, ""
	description = "Return a friendly minion to your hand. It costs (2) less"
	name_CN = "暗影步"
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists(self.ID)
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.ID == self.ID and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for obj in target: self.Game.returnObj2Hand(self, obj, manaMod=ManaMod(obj, by=-2))
		
	
class BladedCultist(Minion):
	Class, race, name = "Rogue", "", "Bladed Cultist"
	mana, attack, health = 1, 1, 2
	name_CN = "执刃教徒"
	numTargets, Effects, description = 0, "", "Combo: Gain +1/+1"
	index = "Combo"
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.comboCounters[self.ID] > 0
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.Game.Counters.comboCounters[self.ID] > 0: self.giveEnchant(self, 1, 1, source=BladedCultist)
		
	
class DeadlyPoison(Spell):
	Class, school, name = "Rogue", "Nature", "Deadly Poison"
	numTargets, mana, Effects = 0, 1, ""
	description = "Give your weapon +2 Attack"
	name_CN = "致命药膏"
	def available(self):
		return self.Game.availableWeapon(self.ID) is not None
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		weapon = self.Game.availableWeapon(self.ID)
		if weapon: self.giveEnchant(weapon, 2, 0, source=DeadlyPoison)
		
	
class SinisterStrike(Spell):
	Class, school, name = "Rogue", "", "Sinister Strike"
	numTargets, mana, Effects = 0, 1, ""
	description = "Deal 3 damage to the enemy hero"
	name_CN = "影袭"
	def text(self): return self.calcDamage(3)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(self.Game.heroes[3-self.ID], self.calcDamage(3))
		
	
class Swashburglar(Minion):
	Class, race, name = "Rogue", "Pirate", "Swashburglar"
	mana, attack, health = 1, 1, 1
	name_CN = "吹嘘海盗"
	numTargets, Effects, description = 0, "", "Battlecry: Add a random card from another class to your hand"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		heroClass = self.Game.heroes[self.ID].Class
		classes = [Class for Class in self.rngPool("Classes") if Class != heroClass]
		self.addCardtoHand(numpyChoice(self.rngPool(numpyChoice(classes)+" Cards")), self.ID)
		
	
class ColdBlood(Spell):
	Class, school, name = "Rogue", "", "Cold Blood"
	numTargets, mana, Effects = 1, 2, ""
	name_CN = "冷血"
	description = "Give a minion +2 Attack. Combo: +4 Attack instead"
	index = "Combo"
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.comboCounters[self.ID] > 0
		
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(target, 4 if self.Game.Counters.comboCounters[self.ID] > 0 else 2, 0, source=ColdBlood)
		
	
class PatientAssassin(Minion):
	Class, race, name = "Rogue", "", "Patient Assassin"
	mana, attack, health = 2, 1, 2
	numTargets, Effects, description = 0, "Stealth,Poisonous", "Stealth, Poisonous"
	name_CN = "耐心的刺客"
	
	
class VanessaVanCleef(Minion):
	Class, race, name = "Rogue", "", "Vanessa VanCleef"
	mana, attack, health = 2, 2, 3
	name_CN = "梵妮莎·范克里夫"
	numTargets, Effects, description = 0, "", "Combo: Add a copy of the last card your opponent played to your hand"
	index = "Combo~Legendary"
	def effCanTrig(self):
		self.effectViable = not self.Game.Counters.comboCounters[self.ID]
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.Game.Counters.comboCounters[self.ID] \
				and (tup := next(self.Game.Counters.iter_CardPlays(3-self.ID, backwards=True), None)):
			self.addCardtoHand(self.Game.fabCard(tup, self.ID, self), self.ID)
		
	
class PlagueScientist(Minion):
	Class, race, name = "Rogue", "", "Plague Scientist"
	mana, attack, health = 3, 2, 3
	name_CN = "瘟疫科学家"
	numTargets, Effects, description = 1, "", "Combo: Give a friendly minion Poisonous"
	index = "Combo"
	def numTargetsNeeded(self, choice=0):
		return 1 if self.Game.Counters.comboCounters[self.ID] > 0 else 0
		
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.comboCounters[self.ID] > 0 and self.Game.minionsonBoard(self.ID)
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.ID == self.ID and obj is not self and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.Game.Counters.comboCounters[self.ID] > 0:
			self.giveEnchant(target, effGain="Poisonous", source=PlagueScientist)
		
	
class SI7Agent(Minion):
	Class, race, name = "Rogue", "", "SI:7 Agent"
	mana, attack, health = 3, 3, 3
	name_CN = "军情七处特工"
	numTargets, Effects, description = 1, "", "Combo: Deal 2 damage"
	index = "Combo"
	def numTargetsNeeded(self, choice=0):
		return 1 if self.Game.Counters.comboCounters[self.ID] > 0 else 0
		
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.comboCounters[self.ID] > 0
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.Game.Counters.comboCounters[self.ID] > 0: self.dealsDamage(target, 2)
		
	
class Assassinate(Spell):
	Class, school, name = "Rogue", "", "Assassinate"
	numTargets, mana, Effects = 1, 4, ""
	description = "Destroy an enemy minion"
	name_CN = "刺杀"
	def available(self):
		return self.selectableMinionExists(3 - self.ID)
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.ID != self.ID and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.Game.kill(self, target)
		
	
class AssassinsBlade(Weapon):
	Class, name, description = "Rogue", "Assassin's Blade", ""
	mana, attack, durability, Effects = 4, 2, 5, ""
	name_CN = "刺客之刃"
	
	
class TombPillager(Minion):
	Class, race, name = "Rogue", "", "Tomb Pillager"
	mana, attack, health = 4, 5, 4
	numTargets, Effects, description = 0, "", "Deathrattle: Add a Coin to your hand"
	name_CN = "盗墓匪贼"
	deathrattle = Death_TombPillager
	
	
class Sprint(Spell):
	Class, school, name = "Rogue", "", "Sprint"
	numTargets, mana, Effects = 0, 6, ""
	description = "Draw 4 cards"
	name_CN = "疾跑"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for _ in (0, 1, 2, 3): self.Game.Hand_Deck.drawCard(self.ID)
		
	
class LightningBolt(Spell):
	Class, school, name = "Shaman", "Nature", "Lightning Bolt"
	numTargets, mana, Effects = 1, 1, ""
	description = "Deal 3 damage. Overload: (1)"
	name_CN = "闪电箭"
	overload = 1
	def text(self): return self.calcDamage(3)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(target, self.calcDamage(3))
		
	
class MenacingNimbus(Minion):
	Class, race, name = "Shaman", "Elemental", "Menacing Nimbus"
	mana, attack, health = 2, 2, 2
	name_CN = "凶恶的雨云"
	numTargets, Effects, description = 0, "", "Battlecry: Add a random Elemental minion to your hand"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.addCardtoHand(numpyChoice(self.rngPool("Elementals")), self.ID)
		
	
class NoviceZapper(Minion):
	Class, race, name = "Shaman", "", "Novice Zapper"
	mana, attack, health = 1, 3, 2
	numTargets, Effects, description = 0, "Spell Damage", "Spell Damage +1. Overload: (1)"
	name_CN = "电击学徒"
	overload = 1
	
	
class RockbiterWeapon(Spell):
	Class, school, name = "Shaman", "Nature", "Rockbiter Weapon"
	numTargets, mana, Effects = 1, 2, ""
	description = "Give a friendly character +3 Attack this turn"
	name_CN = "石化武器"
	def available(self):
		return self.selectableCharExists(self.ID)
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category in ("Minion", "Hero") and obj.ID == self.ID and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for obj in target:
			if obj.category == "Hero": self.giveHeroAttackArmor(obj.ID, attGain=3, source=RockbiterWeapon)
			else: self.giveEnchant(target, statEnchant=Enchantment(RockbiterWeapon, 3, 0, until=0))
		
	
class Windfury(Spell):
	Class, school, name = "Shaman", "Nature", "Windfury"
	numTargets, mana, Effects = 1, 2, ""
	description = "Give a minion Windfury"
	name_CN = "风怒"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(target, effGain="Windfury", source=Windfury)
		
	
class FeralSpirit(Spell):
	Class, school, name = "Shaman", "", "Feral Spirit"
	numTargets, mana, Effects = 0, 3, ""
	description = "Summon two 2/3 Spirit Wolves with Taunt. Overload: (1)"
	name_CN = "野性狼魂"
	overload = 1
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon([SpiritWolf(self.Game, self.ID) for _ in (0, 1)])
		
	
class LightningStorm(Spell):
	Class, school, name = "Shaman", "Nature", "Lightning Storm"
	numTargets, mana, Effects = 0, 3, ""
	description = "Deal 3 damage to all enemy minions. Overload: (2)"
	name_CN = "闪电风暴"
	overload = 2
	def text(self): return self.calcDamage(3)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(self.Game.minionsonBoard(3-self.ID), self.calcDamage(3))
		
	
class ManaTideTotem(Minion):
	Class, race, name = "Shaman", "Totem", "Mana Tide Totem"
	mana, attack, health = 3, 0, 3
	numTargets, Effects, description = 0, "", "At the end of your turn, draw a card"
	name_CN = "法力之潮图腾"
	trigBoard = Trig_ManaTideTotem
	
	
class UnboundElemental(Minion):
	Class, race, name = "Shaman", "Elemental", "Unbound Elemental"
	mana, attack, health = 3, 3, 4
	numTargets, Effects, description = 0, "", "Whenever you play a card with Overload, gain +1/+1"
	name_CN = "无羁元素"
	trigBoard = Trig_UnboundElemental
	
	
class DraeneiTotemcarver(Minion):
	Class, race, name = "Shaman", "", "Draenei Totemcarver"
	mana, attack, health = 4, 4, 5
	name_CN = "德莱尼图腾师"
	numTargets, Effects, description = 0, "", "Battlecry: Gain +1/+1 for each friendly Totem"
	index = "Battlecry"
	def effCanTrig(self):
		self.effectViable = self.Game.minionsonBoard(self.ID, race="Totem")

	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		#For self buffing effects, being dead and removed before battlecry will prevent the battlecry resolution.
		#If this minion is returned hand before battlecry, it can still buff it self according to living friendly minions.
		if (self.onBoard or self.inHand) and (num := len(self.Game.minionsonBoard(self.ID, race="Totem"))):
			self.giveEnchant(self, num, num, source=DraeneiTotemcarver)
		
	
class Hex(Spell):
	Class, school, name = "Shaman", "Nature", "Hex"
	numTargets, mana, Effects = 1, 4, ""
	description = "Transform a minion into a 0/1 Frog with Taunt"
	name_CN = "妖术"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.transform(target, [Frog(self.Game, obj.ID) for obj in target])
		
	
class TidalSurge(Spell):
	Class, school, name = "Shaman", "Nature", "Tidal Surge"
	numTargets, mana, Effects = 1, 3, "Lifesteal"
	description = "Lifesteal. Deal 4 damage to a minion"
	name_CN = "海潮涌动"
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def text(self): return self.calcDamage(4)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(target, self.calcDamage(4))
		
	
class Doomhammer(Weapon):
	Class, name, description = "Shaman", "Doomhammer", "Windfury, Overload: (2)"
	mana, attack, durability, Effects = 5, 2, 8, "Windfury"
	name_CN = "毁灭之锤"
	overload = 2
	
	
class EarthElemental(Minion):
	Class, race, name = "Shaman", "Elemental", "Earth Elemental"
	mana, attack, health = 5, 7, 8
	numTargets, Effects, description = 0, "Taunt", "Taunt. Overload: (2)"
	name_CN = "土元素"
	overload = 2
	
	
class FireElemental(Minion):
	Class, race, name = "Shaman", "Elemental", "Fire Elemental"
	mana, attack, health = 6, 6, 5
	name_CN = "火元素"
	numTargets, Effects, description = 1, "", "Battlecry: Deal 4 damage"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(target, 4)
		
	
class AlAkirtheWindlord(Minion):
	Class, race, name = "Shaman", "Elemental", "Al'Akir the Windlord"
	mana, attack, health = 8, 3, 6
	name_CN = "风领主奥拉基尔"
	numTargets, Effects, description = 0, "Taunt,Charge,Divine Shield,Windfury", "Taunt,Charge,Divine Shield,Windfury"
	index = "Legendary"
	
	
class RitualofDoom(Spell):
	Class, school, name = "Warlock", "Shadow", "Ritual of Doom"
	numTargets, mana, Effects = 1, 0, ""
	description = "Destroy a friendly minion. If you had 5 or more, summon a 5/5 Demon"
	name_CN = "末日仪式"
	def available(self):
		return self.selectableMinionExists(self.ID)
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.ID == self.ID
		
	def effCanTrig(self):
		self.effectViable = len(self.Game.minionsonBoard(self.ID)) > 4
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for obj in target:
			pos, enoughMinions = obj.pos, len(self.Game.minionsonBoard(self.ID)) > 4
			self.Game.kill(self, obj)
			self.Game.gathertheDead()
			if enoughMinions: self.summon(DemonicTyrant(self.Game, self.ID), position=pos)
		
	
class DemonicTyrant(Minion):
	Class, race, name = "Warlock", "Demon", "Demonic Tyrant"
	mana, attack, health = 5, 5, 5
	name_CN = "恶魔暴君"
	numTargets, Effects, description = 0, "", ""
	index = "Uncollectible"
	
	
class FlameImp(Minion):
	Class, race, name = "Warlock", "Demon", "Flame Imp"
	mana, attack, health = 1, 3, 2
	name_CN = "烈焰小鬼"
	numTargets, Effects, description = 0, "", "Battlecry: Deal 3 damage to your hero"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(self.Game.heroes[self.ID], 3)
		
	
class MortalCoil(Spell):
	Class, school, name = "Warlock", "Shadow", "Mortal Coil"
	numTargets, mana, Effects = 1, 1, ""
	description = "Deal 1 damage to a minion. If that kills it, draw a card"
	name_CN = "死亡缠绕"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def text(self): return self.calcDamage(1)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		damage = self.calcDamage(1)
		for obj in target:
			self.dealsDamage(obj, damage)
			if obj.health < 1 or obj.dead: self.Game.Hand_Deck.drawCard(self.ID)
		
	
class PossessedVillager(Minion):
	Class, race, name = "Warlock", "", "Possessed Villager"
	mana, attack, health = 1, 1, 1
	numTargets, Effects, description = 0, "", "Deathrattle: Summon a 1/1 Shadow Beast"
	name_CN = "着魔村民"
	deathrattle = Death_PossessedVillager
	
	
class DrainSoul(Spell):
	Class, school, name = "Warlock", "Shadow", "Drain Soul"
	numTargets, mana, Effects = 1, 2, "Lifesteal"
	description = "Lifesteal. Deal 3 damage to a minion"
	name_CN = "吸取灵魂"
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def text(self): return self.calcDamage(3)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(target, self.calcDamage(3))
		
	
class TinyKnightofEvil(Minion):
	Class, race, name = "Warlock", "Demon", "Tiny Knight of Evil"
	mana, attack, health = 2, 3, 2
	numTargets, Effects, description = 0, "", "Whenever your discard a card, gain +1/+1"
	name_CN = "小鬼骑士"
	trigBoard = Trig_TinyKnightofEvil
	
	
class VoidTerror(Minion):
	Class, race, name = "Warlock", "Demon", "Void Terror"
	mana, attack, health = 3, 3, 4
	name_CN = "虚空恐魔"
	numTargets, Effects, description = 0, "", "Battlecry: Destroy both adjacent minions and gain their Attack and Health"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.onBoard: #Can't trigger if returned to hand already, since cards in hand don't have adjacent minions on board.
			neighbors, distribution = self.Game.neighbors2(self)
			if neighbors:
				attackGain, healthGain = 0, 0
				for minion in neighbors:
					attackGain += max(0, minion.attack)
					healthGain += max(0, minion.health)
				self.Game.kill(self, neighbors)
				self.giveEnchant(self, attackGain, healthGain, source=VoidTerror)
		
	
class FiendishCircle(Spell):
	Class, school, name = "Warlock", "Fel", "Fiendish Circle"
	numTargets, mana, Effects = 0, 3, ""
	description = "Summon four 1/1 Imps"
	name_CN = "恶魔法阵"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon([Imp(self.Game, self.ID) for i in (0, 1, 2, 3)])
		
	
class Imp(Minion):
	Class, race, name = "Warlock", "Demon", "Imp"
	mana, attack, health = 1, 1, 1
	name_CN = "小鬼"
	numTargets, Effects, description = 0, "", ""
	index = "Uncollectible"
	
	
class Hellfire(Spell):
	Class, school, name = "Warlock", "Fire", "Hellfire"
	numTargets, mana, Effects = 0, 4, ""
	description = "Deal 3 damage to ALL characters"
	name_CN = "地狱烈焰"
	def text(self): return self.calcDamage(3)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(self.Game.charsonBoard(), self.calcDamage(3))
		
	
class LakkariFelhound(Minion):
	Class, race, name = "Warlock", "Demon", "Lakkari Felhound"
	mana, attack, health = 4, 3, 8
	name_CN = "拉卡利地狱犬"
	numTargets, Effects, description = 0, "Taunt", "Taunt. Battlecry: Discard your two lowest-Cost cards"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		inds, i, j = {}, -1, -1
		for i, card in enumerate(self.Game.Hand_Deck.hands[self.ID]):
			add2ListinDict(i, inds, card.mana)
		manas = sorted(list(inds.keys()))
		if len(inds[manas[0]]) > 1:  #Two cards share the same lowest cost
			i, j = numpyChoice(inds[manas[0]], 2, replace=False)
		elif len(inds[manas[0]]) == 1:  #Only one card with the lowest cost
			#If there is a 2nd card in hand with a higher cost, then pick as j, else pick -2 as j
			i, j = numpyChoice(inds[manas[0]]), numpyChoice(inds[manas[1]]) if len(manas) > 1 else -1
		if i > -1 and j > -1:
			self.Game.Hand_Deck.discard(self.ID, (i, j))
		elif i > -1:
			self.Game.Hand_Deck.discard(self.ID, i)
		
	
class FelsoulJailer(Minion):
	Class, race, name = "Warlock", "Demon", "Felsoul Jailer"
	mana, attack, health = 5, 4, 6
	name_CN = "邪魂狱卒"
	numTargets, Effects, description = 0, "", "Battlecry: Your opponent discards a minion. Deathrattle: Return it"
	index = "Battlecry"
	deathrattle = Death_FelsoulJailer
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if indices := [i for i, card in enumerate(self.Game.Hand_Deck.hands[3-self.ID]) if card.category == "Minion"]:
			minion = self.Game.Hand_Deck.discard(3 - self.ID, numpyChoice(indices))[0]
			for trig in self.deathrattles:
				if isinstance(trig, Death_FelsoulJailer): trig.memory = minion
		
	
class SiphonSoul(Spell):
	Class, school, name = "Warlock", "Shadow", "Siphon Soul"
	numTargets, mana, Effects = 1, 5, ""
	description = "Destroy a minion. Restore 3 Health to your hero"
	name_CN = "灵魂虹吸"
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def text(self): return self.calcHeal(3)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.Game.kill(self, target)
		self.heals(self.Game.heroes[self.ID], self.calcHeal(3))
		
	
class DreadInfernal(Minion):
	Class, race, name = "Warlock", "Demon", "Dread Infernal"
	mana, attack, health = 6, 6, 6
	name_CN = "恐惧地狱火"
	numTargets, Effects, description = 0, "", "Battlecry: Deal 1 damage to ALL other characters"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(self.Game.charsonBoard(exclude=self), 1)
		
	
class EnslavedFelLord(Minion):
	Class, race, name = "Warlock", "Demon", "Enslaved Fel Lord"
	mana, attack, health = 7, 4, 10
	numTargets, Effects, description = 0, "Taunt,Sweep", "Taunt. Also damages the minions next to whomever this attacks"
	name_CN = "被奴役的邪能领主"
	
	
class TwistingNether(Spell):
	Class, school, name = "Warlock", "Shadow", "Twisting Nether"
	numTargets, mana, Effects = 0, 8, ""
	description = "Destroy all minions"
	name_CN = "扭曲虚空"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.Game.kill(self, self.Game.minionsonBoard())
		
	
class INFERNO(Power):
	mana, name, numTargets = 2, "INFERNO!", 0
	description = "Summon a 6/6 Infernal"
	name_CN = "地狱火！"
	def available(self, choice=0):
		return not self.chancesUsedUp() and self.Game.space(self.ID)
		
	def effect(self, target=(), choice=0, comment=''):
		self.summon(Infernal(self.Game, self.ID))
		
	
class LordJaraxxus(Hero):
	mana, description = 9, "Battlecry: Equip a 3/8 Bloodfury"
	Class, name, heroPower, armor = "Warlock", "Lord Jaraxxus", INFERNO, 5
	name_CN = "加拉克苏斯大王"
	index = "Battlecry~Legendary"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.equipWeapon(BloodFury(self.Game, self.ID))
		
	
class BloodsailDeckhand(Minion):
	Class, race, name = "Warrior", "Pirate", "Bloodsail Deckhand"
	mana, attack, health = 1, 2, 2
	name_CN = "血帆桨手"
	numTargets, Effects, description = 0, "", "Battlecry: The next weapon you play costs (1) less"
	index = "Battlecry"
	trigEffect = GameManaAura_BloodsailDeckhand
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		GameManaAura_BloodsailDeckhand(self.Game, self.ID).auraAppears()
		
	
class ShieldSlam(Spell):
	Class, school, name = "Warrior", "", "Shield Slam"
	numTargets, mana, Effects = 1, 1, ""
	description = "Deal 1 damage to a minion for each Armor you have"
	name_CN = "盾牌猛击"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def text(self): return self.calcDamage(self.Game.heroes[self.ID].armor)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if armor := self.Game.heroes[self.ID].armor: self.dealsDamage(target, self.calcDamage(armor))
		
	
class Whirlwind(Spell):
	Class, school, name = "Warrior", "", "Whirlwind"
	numTargets, mana, Effects = 0, 1, ""
	description = "Deal 1 damage to ALL minions"
	name_CN = "旋风斩"
	def text(self): return self.calcDamage(1)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(self.Game.minionsonBoard(), self.calcDamage(1))
		
	
class CruelTaskmaster(Minion):
	Class, race, name = "Warrior", "", "Cruel Taskmaster"
	mana, attack, health = 2, 2, 2
	name_CN = "严酷的监工"
	numTargets, Effects, description = 1, "", "Battlecry: Deal 1 damage to a minion and give it +2 Attack"
	index = "Battlecry"
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for obj in target:
			self.dealsDamage(obj, 1)
			self.giveEnchant(obj, 2, 0, source=CruelTaskmaster)
		
	
class Execute(Spell):
	Class, school, name = "Warrior", "", "Execute"
	numTargets, mana, Effects = 1, 2, ""
	description = "Destroy a damaged enemy minion"
	name_CN = "斩杀"
	def available(self):
		return self.selectableMinionExists(3 - self.ID)
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.ID != self.ID and obj.health < obj.health_max and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.Game.kill(self, target[0])
		
	
class Slam(Spell):
	Class, school, name = "Warrior", "", "Slam"
	numTargets, mana, Effects = 1, 2, ""
	description = "Deal 2 damage to a minion. If it survives, draw a card"
	name_CN = "猛击"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def text(self): return self.calcDamage(2)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		damage = self.calcDamage(2)
		for obj in target:
			self.dealsDamage(obj, damage)
			if not obj.dead and obj.health > 0: self.Game.Hand_Deck.drawCard(self.ID)
		
	
class FieryWarAxe(Weapon):
	Class, name, description = "Warrior", "Fiery War Axe", ""
	mana, attack, durability, Effects = 3, 3, 2, ""
	name_CN = "炽炎战斧"
	
	
class WarsongCommander(Minion):
	Class, race, name = "Warrior", "", "Warsong Commander"
	mana, attack, health = 3, 2, 3
	numTargets, Effects, description = 0, "", "After you summon another minion, give it Rush"
	name_CN = "战歌指挥官"
	trigBoard = Trig_WarsongCommander
	
	
class Armorsmith(Minion):
	Class, race, name = "Warrior", "", "Armorsmith"
	mana, attack, health = 2, 1, 4
	numTargets, Effects, description = 0, "", "Whenever a friendly minion takes damage, gain +1 Armor"
	name_CN = "铸甲师"
	trigBoard = Trig_Armorsmith
	
	
class FrothingBerserker(Minion):
	Class, race, name = "Warrior", "", "Frothing Berserker"
	mana, attack, health = 3, 2, 4
	numTargets, Effects, description = 0, "", "Whenever a minion takes damage, gain +1 Attack"
	name_CN = "暴乱狂战士"
	trigBoard = Trig_FrothingBerserker
	
	
class WarCache(Spell):
	Class, school, name = "Warrior", "", "War Cache"
	numTargets, mana, Effects = 0, 3, ""
	description = "Add a random Warrior Minion, Spell, and Weapon to your hand"
	name_CN = "战争储备箱"
	poolIdentifier = "Warrior Weapons"
	@classmethod
	def generatePool(cls, pools):
		return "Warrior Weapons", [card for card in pools.ClassCards["Warrior"] if card.category == "Weapon"]
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for identifier in ("Warrior Minions", "Warrior Spells", "Warrior Weapons"):
			self.addCardtoHand(numpyChoice(self.rngPool(identifier)), self.ID)
		
	
class WarsongOutrider(Minion):
	Class, race, name = "Warrior", "", "Warsong Outrider"
	mana, attack, health = 4, 5, 4
	numTargets, Effects, description = 0, "Rush", "Rush"
	name_CN = "战歌侦察骑兵"
	
	
class Brawl(Spell):
	Class, school, name = "Warrior", "", "Brawl"
	numTargets, mana, Effects = 0, 5, ""
	description = "Destroy all minions except one. (Chosen randomly)"
	name_CN = "绝命乱斗"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if len(minions := self.Game.minionsonBoard()) > 1:
			survivor = numpyChoice(minions)
			self.Game.kill(self, [minion for minion in minions if minion is not survivor])
		
	
class Shieldmaiden(Minion):
	Class, race, name = "Warrior", "", "Shieldmaiden"
	mana, attack, health = 5, 5, 5
	name_CN = "盾甲侍女"
	numTargets, Effects, description = 0, "", "Battlecry: Gain 5 Armor"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveHeroAttackArmor(self.ID, armor=5)
		
	
class Gorehowl(Weapon):
	Class, name, description = "Warrior", "Gorehowl", "Attacking a minion costs 1 Attack instead of 1 Durability"
	mana, attack, durability, Effects = 7, 2, 1, ""
	name_CN = "血吼"
	trigBoard = Trig_Gorehowl
	def __init__(self, Game, ID, statsEffects=''):
		super().__init__(Game, ID)
		self.losesAtkInstead = False
		
	def losesDurability(self):
		if self.losesAtkInstead:
			self.losesAtkInstead = False
			self.giveEnchant(self, -1, 0, source=Gorehowl)
			if self.attack < 1: self.dead = True
		else:
			self.health -= 1
			self.dmgTaken += 1
			if self.btn: self.btn.statChangeAni(action="damage")
		
	
class GrommashHellscream(Minion):
	Class, race, name = "Warrior", "", "Grommash Hellscream"
	mana, attack, health = 8, 4, 9
	name_CN = "格罗玛什·地狱咆哮"
	numTargets, Effects, description = 0, "Charge", "Charge. Has +6 attack while damaged"
	index = "Legendary"
	def statCheckResponse(self):
		if self.onBoard and not self.silenced and self.dmgTaken > 0: self.attack += 6
		
	


AllClasses_Core = [
	Aura_DireWolfAlpha, Aura_RaidLeader, Aura_SouthseaCaptain, GameRuleAura_BaronRivendare, Aura_StormwindChampion,
	GameRuleAura_FallenHero, GameRuleAura_ColdarraDrake, Aura_WarhorseTrainer, Death_BloodmageThalnos, Death_ExplosiveSheep,
	Death_LootHoarder, Death_NerubianEgg, Death_TaelanFordring, Death_CairneBloodhoof, Death_SouloftheForest, Death_Webspinner,
	Death_SavannahHighmane, Death_AegwynntheGuardian, Death_TirionFordring, Death_ShadowedSpirit, Death_TombPillager,
	Death_PossessedVillager, Death_FelsoulJailer, Trig_Cogmaster, Trig_ArcaneAnomaly, Trig_MurlocTidecaller, Trig_YoungPriestess,
	Trig_FlesheatingGhoul, Trig_VioletTeacher, Trig_GurubashiBerserker, Trig_OverlordRunthak, Trig_GadgetzanAuctioneer,
	Trig_BaronGeddon, Trig_ArcaneDevourer, Trig_OnyxiatheBroodmother, Trig_ClockworkGiant, Trig_Battlefiend, Trig_KorvasBloodthorn,
	Trig_EyeBeam, Trig_WarglaivesofAzzinoth, Trig_IllidariInquisitor, Trig_ExplosiveTrap, Trig_FreezingTrap, Trig_ScavengingHyena,
	Trig_SnakeTrap, Trig_Counterspell, Trig_IceBarrier, Trig_MirrorEntity, Trig_Avenge, Trig_NobleSacrifice, Trig_Reckoning,
	Trig_TruesilverChampion, Trig_CrimsonClergy, Trig_ManaTideTotem, Trig_UnboundElemental, Trig_TinyKnightofEvil,
	Trig_WarsongCommander, Trig_Armorsmith, Trig_FrothingBerserker, Trig_Gorehowl, GamaManaAura_RagingFelscreamer,
	GameManaAura_NordrassilDruid, LockandLoad_Effect, AegwynntheGuardian_Effect, GameAura_PursuitofJustice, GameManaAura_Preparation,
	GameManaAura_BloodsailDeckhand, MurlocTinyfin, AbusiveSergeant, ArcaneAnomaly, ArgentSquire, Cogmaster, ElvenArcher,
	MurlocTidecaller, EmeraldSkytalon, VoodooDoctor, WorgenInfiltrator, YoungPriestess, AcidicSwampOoze, AnnoyoTron,
	BloodmageThalnos, BloodsailRaider, CrazedAlchemist, DireWolfAlpha, ExplosiveSheep, FogsailFreebooter, KoboldGeomancer,
	LootHoarder, MadBomber, MurlocTidehunter, MurlocScout, NerubianEgg, RedgillRazorjaw, RiverCrocolisk, SunreaverSpy,
	Toxicologist, YouthfulBrewmaster, Brightwing, ColdlightSeer, EarthenRingFarseer, FlesheatingGhoul, HumongousRazorleaf,
	IceRager, InjuredBlademaster, IronbeakOwl, JunglePanther, KingMukla, LoneChampion, MiniMage, RaidLeader, SouthseaCaptain,
	SpiderTank, StoneskinBasilisk, BaronRivendare, BigGameHunter, ChillwindYeti, DarkIronDwarf, DefenderofArgus, GrimNecromancer,
	SenjinShieldmasta, SI7Infiltrator, VioletTeacher, FacelessManipulator, GurubashiBerserker, OverlordRunthak, StranglethornTiger,
	TaelanFordring, CairneBloodhoof, GadgetzanAuctioneer, HighInquisitorWhitemane, BaronGeddon, BarrensStablehand,
	NozdormutheEternal, Stormwatcher, StormwindChampion, ArcaneDevourer, AlexstraszatheLifeBinder, MalygostheSpellweaver,
	OnyxiatheBroodmother, SleepyDragon, YseratheDreamer, DeathwingtheDestroyer, ClockworkGiant, Battlefiend, ChaosStrike,
	CrimsonSigilRunner, FeastofSouls, KorvasBloodthorn, SightlessWatcher, SpectralSight, AldrachiWarblades, CoordinatedStrike,
	EyeBeam, GanargGlaivesmith, AshtongueBattlelord, RagingFelscreamer, ChaosNova, WarglaivesofAzzinoth, IllidariInquisitor,
	Innervate, Pounce, EnchantedRaven, MarkoftheWild, LeaderofthePack_Option, SummonaPanther_Option, PoweroftheWild,
	EvolveSpines_Option, EvolveScales_Option, FeralRage, Landscaping, WildGrowth, NordrassilDruid, SouloftheForest,
	CatForm_Option, BearForm_Option, DruidoftheClaw, ForceofNature, MenagerieWarden, RampantGrowth_Option, Enrich_Option,
	Nourish, Uproot_Option, Rooted_Option, AncientofWar, DemigodsFavor_Option, ShandosLesson_Option, Cenarius, ArcaneShot,
	LockandLoad, Tracking, Webspinner, ExplosiveTrap, FreezingTrap, HeadhuntersHatchet, QuickShot, ScavengingHyena,
	SelectiveBreeder, SnakeTrap, Bearshark, DeadlyShot, DireFrenzy, SavannahHighmane, KingKrush, BabblingBook, ShootingStar,
	SnapFreeze, Arcanologist, FallenHero, ArcaneIntellect, ConeofCold, Counterspell, IceBarrier, MirrorEntity, Fireball,
	WaterElemental, AegwynntheGuardian, EtherealConjurer, ColdarraDrake, Flamestrike, Avenge, NobleSacrifice, Reckoning,
	RighteousProtector, ArgentProtector, HolyLight, PursuitofJustice, AldorPeacekeeper, Equality, WarhorseTrainer,
	BlessingofKings, Consecration, TruesilverChampion, StandAgainstDarkness, GuardianofKings, TirionFordring, CrimsonClergy,
	FlashHeal, FocusedWill, HolySmite, PsychicConjurer, KulTiranChaplain, ShadowWordDeath, ThriveintheShadows, Lightspawn,
	ShadowedSpirit, Shadowform, MindSpike, HolyNova, PowerInfusion, ShadowWordRuin, TempleEnforcer, NatalieSeline,
	Backstab, Preparation, Shadowstep, BladedCultist, DeadlyPoison, SinisterStrike, Swashburglar, ColdBlood, PatientAssassin,
	VanessaVanCleef, PlagueScientist, SI7Agent, Assassinate, AssassinsBlade, TombPillager, Sprint, LightningBolt,
	MenacingNimbus, NoviceZapper, RockbiterWeapon, Windfury, FeralSpirit, LightningStorm, ManaTideTotem, UnboundElemental,
	DraeneiTotemcarver, Hex, TidalSurge, Doomhammer, EarthElemental, FireElemental, AlAkirtheWindlord, RitualofDoom,
	DemonicTyrant, FlameImp, MortalCoil, PossessedVillager, DrainSoul, TinyKnightofEvil, VoidTerror, FiendishCircle,
	Imp, Hellfire, LakkariFelhound, FelsoulJailer, SiphonSoul, DreadInfernal, EnslavedFelLord, TwistingNether, INFERNO,
	LordJaraxxus, BloodsailDeckhand, ShieldSlam, Whirlwind, CruelTaskmaster, Execute, Slam, FieryWarAxe, WarsongCommander,
	Armorsmith, FrothingBerserker, WarCache, WarsongOutrider, Brawl, Shieldmaiden, Gorehowl, GrommashHellscream, 
]

for class_ in AllClasses_Core:
	if issubclass(class_, Card):
		class_.index = "CORE" + ("~" if class_.index else '') + class_.index