from Parts_ConstsFuncsImports import *
from Parts_CardTypes import *
from Parts_TrigsAuras import *

from HS_AcrossPacks import Lackeys


"""Auras"""
class ManaAura_GenerousMummy(ManaAura):
	by = -1
	def applicable(self, target): return target.ID != self.keeper.ID


class Aura_PhalanxCommander(Aura_AlwaysOn):
	signals, attGain, targets = ("MinionAppears", "CharEffectCheck"), 2, "All"
	def applicable(self, target): return target.effects["Taunt"] > 0

	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject.category == "Minion" and subject.ID == self.keeper.ID

	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrig(signal, ID, subject, target, number, comment):
			if signal.startswith("Char"):
				if subject.keyWords["Taunt"] > 0 and all(receiver.recipient != subject for receiver in self.receivers):
					Aura_Receiver(subject, self, 2, 0).effectStart()
				elif subject.keyWords["Taunt"] < 1 and \
					(receiver := next((receiver for receiver in self.receivers if receiver.recipient == subject), None)):
					receiver.effectClear()
			elif subject.keyWords["Taunt"] > 0: Aura_Receiver(subject, self, 2, 0).effectStart()


class Aura_Vessina(Aura_Conditional):
	signals, attGain, targets = ("MinionAppears", "OverloadCheck"), 2, "Others"
	def whichWay(self):
		keeper = self.keeper
		isOverloaded = keeper.Game.Manas.manasOverloaded[keeper.ID] > 0 or keeper.Game.Manas.manasLocked[keeper.ID] > 0
		if not isOverloaded and self.on: return -1
		elif isOverloaded and not self.on: return 1
		else: return 0

	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		if signal[0] == 'M': return self.keeper.onBoard and subject.ID == self.keeper.ID and self.on
		else: return self.keeper.onBoard and ID == self.keeper.ID


"""Deathrattles"""
class Death_JarDealer(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.addCardtoHand(numpyChoice(self.rngPool("1-Cost Minions")), self.keeper.ID)

class Death_KoboldSandtrooper(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.dealsDamage(self.keeper.Game.heroes[3 - self.keeper.ID], 3)

class Death_SerpentEgg(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.summon(SeaSerpent(self.keeper.Game, self.keeper.ID))

class Death_InfestedGoblin(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.addCardtoHand([Scarab_Uldum, Scarab_Uldum], self.keeper.ID)

class Death_BlatantDecoy(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.keeper
		for ID in (1, 2):
			if minion.Game.space(minion.ID) and (indices := pickLowestCostIndices(minion.Game.Hand_Deck.hands[ID],
																				  func=lambda card: card.category == "Minion")):
				minion.Game.summonfrom(numpyChoice(indices), ID, -1, summoner=minion, source='H')

class Death_KhartutDefender(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.restoresHealth(self.keeper.Game.heroes[self.keeper.ID], self.keeper.calcHeal(4))

class Death_Octosari(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		for i in range(8): self.keeper.Game.Hand_Deck.drawCard(self.keeper.ID)

class Death_AnubisathWarbringer(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.AOE_GiveEnchant([card for card in self.keeper.Game.Hand_Deck.hands[self.keeper.ID] if card.category == "Minion"],
									3, 3, name=AnubisathWarbringer, add2EventinGUI=False)
		
class Death_SalhetsPride(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		for _ in (0, 1):
			if not self.keeper.drawCertainCard(lambda card: card.category == "Minion" and card.health == 1)[0]: break

class Death_Grandmummy(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if minions := self.keeper.Game.minionsonBoard(self.keeper.ID): self.keeper.giveEnchant(numpyChoice(minions), 1, 1, name=Grandmummy)

class Death_SahketSapper(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minions = self.keeper.Game.minionsonBoard(3 - self.keeper.ID)
		if minions: self.keeper.Game.returnObj2Hand(numpyChoice(minions))  # minion是在场上的，所以不需要询问是否保留亡语注册

class Death_ExpiredMerchant(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if self.savedObj: self.keeper.addCardtoHand([self.savedObj]*2, self.keeper.ID)

	def selfCopy(self, recipient):
		trig = type(self)(recipient)
		trig.savedObj = self.savedObj
		return trig

	def assistCreateCopy(self, Copy):
		Copy.savedObj = self.savedObj


"""Triggers"""
class Trig_HighkeeperRa(TrigBoard):
	signals = ("TurnEnds", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		targets = [self.keeper.Game.heroes[3-self.keeper.ID]] + self.keeper.Game.minionsonBoard(3-self.keeper.ID)
		self.keeper.AOE_Damage(targets, [20 for obj in targets])
		
		
class Trig_DwarvenArchaeologist(TrigBoard):
	signals = ("PutinHandbyDiscover", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and ID == self.keeper.ID and target.ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		ManaMod(target, by=-1).applies()
		self.keeper.Game.Manas.calcMana_Single(target)
		

class Trig_SpittingCamel(TrigBoard):
	signals = ("TurnEnds", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minions = self.keeper.Game.minionsAlive(self.keeper.ID, self.keeper)
		if minions: self.keeper.dealsDamage(numpyChoice(minions), 1)


class Trig_HistoryBuff(TrigBoard):
	signals = ("MinionPlayed", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject.ID == self.keeper.ID and subject != self.keeper

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if minions := [card for card in self.keeper.Game.Hand_Deck.hands[self.keeper.ID] if card.category == "Minion"]:
			self.keeper.giveEnchant(numpyChoice(minions), statEnchant=Enchantment_Cumulative(1, 1, name=HistoryBuff), add2EventinGUI=False)
		

class Trig_ConjuredMirage(TrigBoard):
	signals = ("TurnStarts", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		#随从在可以触发回合开始扳机的时机一定是不结算其亡语的。可以安全地注销其死亡扳机
		self.keeper.Game.returnMiniontoDeck(self.keeper, self.keeper.ID, self.keeper.ID, deathrattlesStayArmed=False)
		
		
class Trig_SunstruckHenchman(TrigBoard):
	signals = ("TurnStarts", "TurnEnds", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if signal == "TurnStarts":
			if numpyRandint(2): self.keeper.effects["Can't Attack"] += 1
		else: self.keeper.effects["Can't Attack"] -= 1 #signal == "TurnEnds"
		
		
class Trig_DesertObelisk(TrigBoard):
	signals = ("TurnEnds", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and ID == self.keeper.ID and \
			   sum(minion.name == "Desert Obelisk" for minion in self.keeper.Game.minionsonBoard(self.keeper.ID)) > 2

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if objs := self.keeper.Game.charsAlive(3-self.keeper.ID): self.keeper.dealsDamage(numpyChoice(objs), 5)

			
class Trig_MortuaryMachine(TrigBoard):
	signals = ("MinionBeenPlayed", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject.ID != self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.giveEnchant(subject, effGain="Reborn", name=MortuaryMachine)

		
class Trig_WrappedGolem(TrigBoard):
	signals = ("TurnEnds", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.summon(Scarab_Uldum(self.keeper.Game, self.keeper.ID))
		

class Trig_UntappedPotential(Trig_Quest):
	signals = ("TurnEnds", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return ID == self.keeper.ID and self.keeper.Game.Manas.manas[self.keeper.ID] > 0


class Trig_CrystalMerchant(TrigBoard):
	signals = ("TurnEnds", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if self.keeper.Game.Manas.manas[self.keeper.ID] > 0:
			self.keeper.Game.Hand_Deck.drawCard(self.keeper.ID)
			
			
class Trig_AnubisathDefender(TrigHand):
	signals = ("SpellBeenPlayed", "TurnStarts", "TurnEnds", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.inHand and (signal[0] == 'T' or (number > 4 and subject.ID == self.keeper.ID))

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.Game.Manas.calcMana_Single(self.keeper)
		
		
class Trig_UnsealtheVault(Trig_Quest):
	signals = ("MinionBeenSummoned", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.keeper.ID


class Trig_PressurePlate(Trig_Secret):
	signals = ("SpellBeenPlayed", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.ID != self.keeper.Game.turn and subject.ID != self.keeper.ID and self.keeper.Game.minionsAlive(3-self.keeper.ID)
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minions = self.keeper.Game.minionsAlive(3-self.keeper.ID)
		if minions: self.keeper.Game.kill(self.keeper, numpyChoice(minions))
		
		
class Trig_DesertSpear(TrigBoard):
	signals = ("HeroAttackedMinion", "HeroAttackedHero", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		#The target can't be dying to trigger this
		return subject == self.keeper.Game.heroes[self.keeper.ID] and self.keeper.onBoard

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.summon(Locust(self.keeper.Game, self.keeper.ID))
		
		
class Trig_RaidtheSkyTemple(Trig_Quest):
	signals = ("SpellPlayed", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.keeper.ID


class Trig_FlameWard(Trig_Secret):
	signals = ("MinionAttackedHero", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.ID != self.keeper.Game.turn and target == self.keeper.Game.heroes[self.keeper.ID]
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		damage = self.keeper.calcDamage(3)
		targets = self.keeper.Game.minionsonBoard(3-self.keeper.ID)
		self.keeper.AOE_Damage(targets, [damage for minion in targets])
		
		
class Trig_ArcaneFlakmage(TrigBoard):
	signals = ("SpellBeenPlayed", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject.ID == self.keeper.ID and subject.race == "Secret"

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		targets = self.keeper.Game.minionsonBoard(3-self.keeper.ID)
		self.keeper.AOE_Damage(targets, [2 for minion in targets])
		
		
class Trig_DuneSculptor(TrigBoard):
	signals = ("SpellPlayed", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject.ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.addCardtoHand(numpyChoice(self.rngPool("Mage Minions")), self.keeper.ID)
			
			
class Trig_MakingMummies(Trig_Quest):
	signals = ("MinionBeenPlayed", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		#假设扳机的判定条件是打出的随从在检测时有复生就可以，如果在打出过程中获得复生，则依然算作任务进度
		return subject.ID == self.keeper.ID and subject.effects["Reborn"] > 0


class Trig_BrazenZealot(TrigBoard):
	signals = ("MinionSummoned", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject.ID == self.keeper.ID and subject != self.keeper

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.giveEnchant(self.keeper, statEnchant=Enchantment_Cumulative(1, 0, name=BrazenZealot))
		
		
class Trig_MicroMummy(TrigBoard):
	signals = ("TurnEnds", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if minions := self.keeper.Game.minionsonBoard(self.keeper.ID, self.keeper):
			self.keeper.giveEnchant(numpyChoice(minions), statEnchant=Enchantment_Cumulative(1, 0, name=MicroMummy))
		

class Trig_ActivatetheObelisk(Trig_Quest):
	signals = ("MinionGetsHealed", "HeroGetsHealed", )
	def handleCounter(self, signal, ID, subject, target, number, comment, choice=0):
		self.counter += number

	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.keeper.ID


class Trig_SandhoofWaterbearer(TrigBoard):
	signals = ("TurnEnds", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and ID == self.keeper.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		chars = [char for char in self.keeper.Game.charsAlive(self.keeper.ID) if char.health < char.health_max]
		if chars: self.keeper.restoresHealth(numpyChoice(chars), self.keeper.calcHeal(5))
		

class Trig_HighPriestAmet(TrigBoard):
	signals = ("MinionSummoned", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject.ID == self.keeper.ID and subject != self.keeper and self.keeper.health > 0

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.setStat(subject, newHealth=self.keeper.health, name=HighPriestAmet)
		
		
class Trig_BazaarBurglary(Trig_Quest):
	signals = ("CardEntersHand", "SpellCastWhenDrawn", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return target[0].ID == self.keeper.ID and target[0].Class != "Neutral" and self.keeper.Game.heroes[self.keeper.ID].Class not in target[0].Class


class Trig_MirageBlade(TrigBoard):
	signals = ("BattleStarted", "BattleFinished", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.keeper.Game.heroes[self.keeper.ID] and self.keeper.onBoard
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if signal == "BattleStarted": subject.getsEffect("Immune")
		else: subject.losesEffect("Immune")
		
		
class Trig_WhirlkickMaster(TrigBoard):
	signals = ("MinionPlayed", "SpellPlayed", "WeaponPlayed", "HeroCardPlayed", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		#这个随从本身是没有连击的。同时目前没有名字中带有Combo的牌。
		return self.keeper.onBoard and subject.ID == self.keeper.ID and "~Combo" in subject.index

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.addCardtoHand(numpyChoice(self.rngPool("Combo Cards")), self.keeper.ID)
			

class Trig_CorrupttheWaters(Trig_Quest):
	signals = ("MinionBeenPlayed", "WeaponBeenPlayed", "HeroCardBeenPlayed", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.keeper.ID and "~Battlecry" in subject.index


class Trig_EVILTotem(TrigBoard):
	signals = ("TurnEnds", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.addCardtoHand(numpyChoice(Lackeys), self.keeper.ID)


class Trig_MoguFleshshaper(TrigHand):
	signals = ("MinionAppears", "MinionDisappears", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.inHand

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.Game.Manas.calcMana_Single(self.keeper)
		
		
class Trig_SupremeArchaeology(Trig_Quest):
	signals = ("CardDrawn", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return ID == self.keeper.ID


class Trig_NefersetThrasher(TrigBoard):
	signals = ("MinionAttackingMinion", "MinionAttackingHero", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.keeper and self.keeper.onBoard

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.dealsDamage(self.keeper.Game.heroes[self.keeper.ID], 3)
		
		
class Trig_DiseasedVulture(TrigBoard):
	signals = ("HeroTookDmg", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return target == self.keeper.Game.heroes[self.keeper.ID] and self.keeper.ID == self.keeper.Game.turn

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.summon(numpyChoice(self.rngPool("3-Cost Minions to Summon"))(self.keeper.Game, self.keeper.ID))


class Trig_HacktheSystem(Trig_Quest):
	signals = ("HeroAttackedHero", "HeroAttackedMinion", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.keeper.Game.heroes[self.keeper.ID]


class Trig_AnraphetsCore(TrigBoard):
	signals = ("HeroAttackedHero", "HeroAttackedMinion", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.keeper.Game.heroes[self.keeper.ID] and self.keeper.chancesUsedUp()
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.usageCount -= 1
		

class Trig_LivewireLance(TrigBoard):
	signals = ("HeroAttackedMinion", "HeroAttackedHero", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		#The target can't be dying to trigger this
		return subject == self.keeper.Game.heroes[self.keeper.ID] and self.keeper.onBoard

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.addCardtoHand(numpyChoice(Lackeys), self.keeper.ID)
			
			
class Trig_Armagedillo(TrigBoard):
	signals = ("TurnEnds", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.AOE_GiveEnchant([card for card in self.keeper.Game.Hand_Deck.hands[self.keeper.ID] if card.category == "Minion" and card.effects["Taunt"] > 0], 
									statEnchant=Enchantment_Cumulative(2, 2, name=Armagedillo), add2EventinGUI=False)
				
				
class Trig_ArmoredGoon(TrigBoard):
	signals = ("HeroAttackingHero", "HeroAttackingMinion", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject == self.keeper.Game.heroes[self.keeper.ID]

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.giveHeroAttackArmor(self.keeper.ID, armor=5)
		
		
class BeamingSidekick(Minion):
	Class, race, name = "Neutral", "", "Beaming Sidekick"
	mana, attack, health = 1, 1, 2
	index = "ULDUM~Neutral~Minion~1~1~2~~Beaming Sidekick~Battlecry"
	requireTarget, effects, description = True, "", "Battlecry: Give a friendly minion +2 Health"
	name_CN = "欢快的同伴"
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists(choice)
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.ID == self.ID and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.giveEnchant(target, 0, 2, name=BeamingSidekick)
		return target
		
		
class JarDealer(Minion):
	Class, race, name = "Neutral", "", "Jar Dealer"
	mana, attack, health = 1, 1, 1
	index = "ULDUM~Neutral~Minion~1~1~1~~Jar Dealer~Deathrattle"
	requireTarget, effects, description = False, "", "Deathrattle: Add a random 1-cost minion to your hand"
	name_CN = "陶罐商人"
	deathrattle = Death_JarDealer
	poolIdentifier = "1-Cost Minions"
	@classmethod
	def generatePool(cls, pools):
		return "1-Cost Minions", list(pools.MinionsofCost[1].values())


class MoguCultist(Minion):
	Class, race, name = "Neutral", "", "Mogu Cultist"
	mana, attack, health = 1, 1, 1
	index = "ULDUM~Neutral~Minion~1~1~1~~Mogu Cultist~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: If your board is full of Mogu Cultists, sacrifice them all and summon Highkeeper Ra"
	name_CN = "魔古信徒"
	#强制要求场上有总共有7个魔古信徒，休眠物会让其效果无法触发
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		minions = self.Game.minionsonBoard(self.ID)
		if len(minions) == 7 and all(minion.name == "Mogu Cultist" for minion in minions):
			self.Game.kill(None, minions)
			self.Game.gathertheDead()
			self.summon(HighkeeperRa(self.Game, self.ID))
		

class HighkeeperRa(Minion):
	Class, race, name = "Neutral", "", "Highkeeper Ra"
	mana, attack, health = 10, 20, 20
	index = "ULDUM~Neutral~Minion~10~20~20~~Highkeeper Ra~Legendary~Uncollectible"
	requireTarget, effects, description = False, "", "At the end of your turn, deal 20 damage to all enemies"
	name_CN = "莱，至高守护者"
	trigBoard = Trig_HighkeeperRa		


class Murmy(Minion):
	Class, race, name = "Neutral", "Murloc", "Murmy"
	mana, attack, health = 1, 1, 1
	index = "ULDUM~Neutral~Minion~1~1~1~Murloc~Murmy~Reborn"
	requireTarget, effects, description = False, "Reborn", "Reborn"
	name_CN = "鱼人木乃伊"
	
	
class BugCollector(Minion):
	Class, race, name = "Neutral", "", "Bug Collector"
	mana, attack, health = 2, 2, 1
	index = "ULDUM~Neutral~Minion~2~2~1~~Bug Collector~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Summon a 1/1 Locust with Rush"
	name_CN = "昆虫收藏家"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon(Locust(self.Game, self.ID))
		

class Locust(Minion):
	Class, race, name = "Neutral", "Beast", "Locust"
	mana, attack, health = 1, 1, 1
	index = "ULDUM~Neutral~Minion~1~1~1~Beast~Locust~Rush~Uncollectible"
	requireTarget, effects, description = False, "Rush", "Rush"
	name_CN = "蝗虫"
	
	
class DwarvenArchaeologist(Minion):
	Class, race, name = "Neutral", "", "Dwarven Archaeologist"
	mana, attack, health = 2, 2, 3
	index = "ULDUM~Neutral~Minion~2~2~3~~Dwarven Archaeologist"
	requireTarget, effects, description = False, "", "After you Discover a card, reduce its cost by (1)"
	name_CN = "矮人历史学家"
	trigBoard = Trig_DwarvenArchaeologist		


class Fishflinger(Minion):
	Class, race, name = "Neutral", "Murloc", "Fishflinger"
	mana, attack, health = 2, 3, 2
	index = "ULDUM~Neutral~Minion~2~3~2~Murloc~Fishflinger~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Add a random Murloc to each player's hand"
	name_CN = "鱼人投手"
	poolIdentifier = "Murlocs"
	@classmethod
	def generatePool(cls, pools):
		return "Murlocs", list(pools.MinionswithRace["Murloc"].values())
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		murloc1, murloc2 = numpyChoice(self.rngPool("Murlocs"), 2, replace=False)
		self.addCardtoHand(murloc1, self.ID)
		self.addCardtoHand(murloc2, 3-self.ID)
		
		
class InjuredTolvir(Minion):
	Class, race, name = "Neutral", "", "Injured Tol'vir"
	mana, attack, health = 2, 2, 6
	index = "ULDUM~Neutral~Minion~2~2~6~~Injured Tol'vir~Taunt~Battlecry"
	requireTarget, effects, description = False, "Taunt", "Taunt. Battlecry: Deal 3 damage to this minion"
	name_CN = "受伤的托维尔人"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.dealsDamage(self, 3)
		
		
class KoboldSandtrooper(Minion):
	Class, race, name = "Neutral", "", "Kobold Sandtrooper"
	mana, attack, health = 2, 2, 1
	index = "ULDUM~Neutral~Minion~2~2~1~~Kobold Sandtrooper~Deathrattle"
	requireTarget, effects, description = False, "", "Deathrattle: Deal 3 damage to the enemy hero"
	name_CN = "狗头人沙漠步兵"
	deathrattle = Death_KoboldSandtrooper


class NefersetRitualist(Minion):
	Class, race, name = "Neutral", "", "Neferset Ritualist"
	mana, attack, health = 2, 2, 3
	index = "ULDUM~Neutral~Minion~2~2~3~~Neferset Ritualist~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Restore adjacent minions to full Health"
	name_CN = "尼斐塞特仪祭师"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.onBoard:
			for minion in self.Game.neighbors2(self)[0]:
				heal = self.calcHeal(minion.health_max)
				self.restoresHealth(minion, heal)
		
		
class QuestingExplorer(Minion):
	Class, race, name = "Neutral", "", "Questing Explorer"
	mana, attack, health = 2, 2, 3
	index = "ULDUM~Neutral~Minion~2~2~3~~Questing Explorer~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: If you control a Quest, draw a card"
	name_CN = "奋进的探险者"
	def effCanTrig(self):
		self.effectViable = self.Game.Secrets.mainQuests[self.ID] != [] or self.Game.Secrets.sideQuests[self.ID] != []
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Secrets.mainQuests[self.ID] != [] or self.Game.Secrets.sideQuests[self.ID] != []:
			self.Game.Hand_Deck.drawCard(self.ID)
		

class QuicksandElemental(Minion):
	Class, race, name = "Neutral", "Elemental", "Quicksand Elemental"
	mana, attack, health = 2, 3, 2
	index = "ULDUM~Neutral~Minion~2~3~2~Elemental~Quicksand Elemental~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Give all enemy minions -2 Attack this turn"
	name_CN = "流沙元素"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.AOE_GiveEnchant(self.Game.minionsonBoard(3-self.ID),
							 statEnchant=Enchantment(-2, 0, until=0, name=QuicksandElemental))
		
		
class SerpentEgg(Minion):
	Class, race, name = "Neutral", "", "Serpent Egg"
	mana, attack, health = 2, 0, 3
	index = "ULDUM~Neutral~Minion~2~0~3~~Serpent Egg~Deathrattle"
	requireTarget, effects, description = False, "", "Deathrattle: Summon a 3/4 Sea Serpent"
	name_CN = "海蛇蛋"
	deathrattle = Death_SerpentEgg


class SeaSerpent(Minion):
	Class, race, name = "Neutral", "Beast", "Sea Serpent"
	mana, attack, health = 3, 3, 4
	index = "ULDUM~Neutral~Minion~3~3~4~Beast~Sea Serpent~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "海蛇"
	
	
class SpittingCamel(Minion):
	Class, race, name = "Neutral", "Beast", "Spitting Camel"
	mana, attack, health = 2, 2, 4
	index = "ULDUM~Neutral~Minion~2~2~4~Beast~Spitting Camel"
	requireTarget, effects, description = False, "", "At the end of your turn, deal 1 damage to another random friendly minion"
	name_CN = "乱喷的骆驼"
	trigBoard = Trig_SpittingCamel		


class TempleBerserker(Minion):
	Class, race, name = "Neutral", "", "Temple Berserker"
	mana, attack, health = 2, 1, 2
	index = "ULDUM~Neutral~Minion~2~1~2~~Temple Berserker~Reborn"
	requireTarget, effects, description = False, "Reborn", "Reborn. Has +2 Attack while damaged"
	name_CN = "神殿狂战士"
	def statCheckResponse(self):
		if self.onBoard and not self.silenced and self.dmgTaken > 0: self.attack += 2
	
	
class Vilefiend(Minion):
	Class, race, name = "Neutral", "Demon", "Vilefiend"
	mana, attack, health = 2, 2, 2
	index = "ULDUM~Neutral~Minion~2~2~2~Demon~Vilefiend~Lifesteal"
	requireTarget, effects, description = False, "Lifesteal", "Lifesteal"
	name_CN = "邪犬"
	
	
class ZephrystheGreat(Minion):
	Class, race, name = "Neutral", "Elemental", "Zephrys the Great"
	mana, attack, health = 2, 3, 2
	index = "ULDUM~Neutral~Minion~2~3~2~Elemental~Zephrys the Great~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: If your deck has no duplicates, wish for the perfect card"
	name_CN = "了不起的杰弗里斯"
	poolIdentifier = "Basic and Classic Cards"
	@classmethod
	def generatePool(cls, pools):
		basicandClassicCards = [value for key, value in pools.cardPool.items() if (key.startswith("Basic") or key.startswith("Classic")) and "~Uncollectible" not in key]
		return "Basic and Classic Cards", basicandClassicCards
		
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.noDuplicatesinDeck(self.ID)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		HD = curGame.Hand_Deck
		if HD.noDuplicatesinDeck(self.ID) and self.ID == curGame.turn:
			if curGame.mode == 0:
				if curGame.picks:
					HD.addCardtoHand(curGame.picks.pop(0), self.ID)
				else:
					if "byOthers" in comment:
						card = numpyChoice(self.rngPool("Basic and Classic Cards"))
						curGame.picks_Backup(card)
						self.addCardtoHand(card, self.ID)
					else:
						curGame.Discover.typeCardName(self)
		

class Candletaker(Minion):
	Class, race, name = "Neutral", "", "Candletaker"
	mana, attack, health = 3, 3, 2
	index = "ULDUM~Neutral~Minion~3~3~2~~Candletaker~Reborn"
	requireTarget, effects, description = False, "Reborn", "Reborn"
	name_CN = "夺烛木乃伊"
	
	
class DesertHare(Minion):
	Class, race, name = "Neutral", "Beast", "Desert Hare"
	mana, attack, health = 3, 1, 1
	index = "ULDUM~Neutral~Minion~3~1~1~Beast~Desert Hare~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Summon two 1/1 Desert Hares"
	name_CN = "沙漠野兔"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon([DesertHare(self.Game, self.ID) for _ in (0, 1)], relative="<>")
		
		
class GenerousMummy(Minion):
	Class, race, name = "Neutral", "", "Generous Mummy"
	mana, attack, health = 3, 5, 4
	index = "ULDUM~Neutral~Minion~3~5~4~~Generous Mummy~Reborn"
	requireTarget, effects, description = False, "Reborn", "Reborn. Your opponent's cards cost (1) less"
	name_CN = "慷慨的木乃伊"
	aura = ManaAura_GenerousMummy
	
	
class GoldenScarab(Minion):
	Class, race, name = "Neutral", "Beast", "Golden Scarab"
	mana, attack, health = 3, 2, 2
	index = "ULDUM~Neutral~Minion~3~2~2~Beast~Golden Scarab~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Discover a 4-cost card"
	name_CN = "金甲虫"
	poolIdentifier = "4-Cost Cards as Druid"
	@classmethod
	def generatePool(cls, pools):
		classCards = {s : [value for key, value in pools.ClassCards[s].items() if key.split('~')[3] == '4'] for s in pools.Classes}
		classCards["Neutral"] = [value for key, value in pools.NeutralCards.items() if key.split('~')[3] == '4']
		return ["4-Cost Cards as %s"%Class for Class in pools.Classes], \
			[classCards[Class]+classCards["Neutral"] for Class in pools.Classes]
			
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverandGenerate(GoldenScarab, comment, poolFunc=lambda : self.rngPool("4-Cost Cards as "+classforDiscover(self)))
		
		
class HistoryBuff(Minion):
	Class, race, name = "Neutral", "", "History Buff"
	mana, attack, health = 3, 3, 4
	index = "ULDUM~Neutral~Minion~3~3~4~~History Buff"
	requireTarget, effects, description = False, "", "Whenever you play a minion, give a random minion in your hand +1/+1"
	name_CN = "历史爱好者"
	trigBoard = Trig_HistoryBuff		


class InfestedGoblin(Minion):
	Class, race, name = "Neutral", "", "Infested Goblin"
	mana, attack, health = 3, 2, 3
	index = "ULDUM~Neutral~Minion~3~2~3~~Infested Goblin~Taunt~Deathrattle"
	requireTarget, effects, description = False, "Taunt", "Taunt. Deathrattle: Add two 1/1 Scarabs with Taunt to your hand"
	name_CN = "招虫的地精"
	deathrattle = Death_InfestedGoblin


class Scarab_Uldum(Minion):
	Class, race, name = "Neutral", "Beast", "Scarab"
	mana, attack, health = 1, 1, 1
	index = "ULDUM~Neutral~Minion~1~1~1~Beast~Scarab~Taunt~Uncollectible"
	requireTarget, effects, description = False, "Taunt", "Taunt"
	name_CN = "甲虫"
	
	
class MischiefMaker(Minion):
	Class, race, name = "Neutral", "", "Mischief Maker"
	mana, attack, health = 3, 3, 3
	index = "ULDUM~Neutral~Minion~3~3~3~~Mischief Maker~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Swap the top deck of your deck with your opponent's"
	name_CN = "捣蛋鬼"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		#不知道如果一方牌库为空时会如何,假设一方牌库为空时不触发效果
		if self.Game.Hand_Deck.decks[1] != [] and self.Game.Hand_Deck.decks[2] != []:
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
	index = "ULDUM~Neutral~Minion~3~2~3~~Vulpera Scoundrel~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Discover a spell or pick a mystery choice"
	name_CN = "狐人恶棍"
	poolIdentifier = "Druid Spells"
	@classmethod
	def generatePool(cls, pools):
		return [Class+" Spells" for Class in pools.Classes], \
				[[value for key, value in pools.ClassCards[Class].items() if "~Spell~" in key] for Class in pools.Classes]
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		game = self.Game
		if game.mode == 0:
			if game.picks:
				info_RNGSync, info_GUISync, isRandom, option = game.picks.pop(0)
				numpyChoice(range(info_RNGSync), 3, replace=False)
				#option is (card1, card2, choice=0/1/2/3)
				card1, card2, card3, i = option
				cards_Real = [card1(game, self.ID), card2(game, self.ID)]
				if game.GUI: game.GUI.discoverDecideAni(isRandom=isRandom, numOption=info_GUISync[0], indexOption=info_GUISync[1],
														options=cards_Real + [MysteryChoice(ID=self.ID)])
				VulperaScoundrel.discoverDecided(self, cards_Real + [i],
										 case="Guided", info_RNGSync=info_RNGSync, info_GUISync=info_GUISync)
			else:
				pool = self.rngPool(classforDiscover(self) + " Spells")
				options = [option(game, self.ID) for option in numpyChoice(pool, 3, replace=False)] + [MysteryChoice(ID=self.ID)]
				if self.ID != game.turn or "byOthers" in comment:
					i = datetime.now().microsecond % 4
					if game.GUI: game.UI.discoverDecideAni(isRandom=True, numOption=4, indexOption=i, options=options)
					VulperaScoundrel.discoverDecided(self, options[0:3] + [i], case="Random", info_RNGSync=len(pool), info_GUISync=(4, i))
				else:
					game.options = options
					game.Discover.startDiscover(self, effectType=VulperaScoundrel, info_RNGSync=len(pool), info_GUISync=[4])
	
	def discoverDecided(self, option, case, info_RNGSync=None, info_GUISync=None):
		if case == "Discovered":  #option is one of the real cards or SpiritPath(self.Game, self.ID)
			card1, card2, card3 = self.Game.options[0:3]
			i = self.Game.options.index(option)
			self.Game.picks_Backup((info_RNGSync, info_GUISync, False, (type(card1), type(card2), type(card3), i)))
		else:  #option is (card1, card2, card3, i)
			card1, card2, card3, i = option
			if case == "Random": self.Game.picks_Backup((info_RNGSync, info_GUISync, True, (type(card1), type(card2), type(card3), i)))
		
		if i == 3: self.addCardtoHand(numpyChoice(self.rngPool(classforDiscover(self) + " Spells")), self.ID, byDiscover=True)
		else: self.addCardtoHand((card1, card2, card3)[i], self.ID, byDiscover=True)
	

class MysteryChoice(Option):
	name, description = "Mystery Choice!", "Add a random spell to your hand"
	mana, attack, health = 0, -1, -1
	
	
class BoneWraith(Minion):
	Class, race, name = "Neutral", "", "Bone Wraith"
	mana, attack, health = 4, 2, 5
	index = "ULDUM~Neutral~Minion~4~2~5~~Bone Wraith~Reborn~Taunt"
	requireTarget, effects, description = False, "Reborn,Taunt", "Reborn, Taunt"
	name_CN = "白骨怨灵"
	
	
class BodyWrapper(Minion):
	Class, race, name = "Neutral", "", "Body Wrapper"
	mana, attack, health = 4, 4, 4
	index = "ULDUM~Neutral~Minion~4~4~4~~Body Wrapper~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Discover a friendly minion that died this game. Shuffle it into your deck"
	name_CN = "裹尸匠"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverandGenerate_Types(BodyWrapper, comment,
									   typePoolFunc=lambda : [card for card in self.Game.Counters.minionsDiedThisGame[self.ID]])
		
	def discoverDecided(self, option, case, info_RNGSync=None, info_GUISync=None):
		self.handleDiscoverGeneratedCard(option, case, info_RNGSync, info_GUISync,
										 func=lambda cardType, card: self.shuffleintoDeck(card, enemyCanSee=False))
		
		
class ConjuredMirage(Minion):
	Class, race, name = "Neutral", "", "Conjured Mirage"
	mana, attack, health = 4, 3, 10
	index = "ULDUM~Neutral~Minion~4~3~10~~Conjured Mirage~Taunt"
	requireTarget, effects, description = False, "Taunt", "Taunt. At the start of your turn, shuffle this minion into your deck"
	name_CN = "魔法幻象"
	trigBoard = Trig_ConjuredMirage		


class SunstruckHenchman(Minion):
	Class, race, name = "Neutral", "", "Sunstruck Henchman"
	mana, attack, health = 4, 6, 5
	index = "ULDUM~Neutral~Minion~4~6~5~~Sunstruck Henchman"
	requireTarget, effects, description = False, "", "At the start of your turn, this has a 50% chance to fall asleep"
	name_CN = "中暑的匪徒"
	trigBoard = Trig_SunstruckHenchman		


class FacelessLurker(Minion):
	Class, race, name = "Neutral", "", "Faceless Lurker"
	mana, attack, health = 5, 3, 3
	index = "ULDUM~Neutral~Minion~5~3~3~~Faceless Lurker~Taunt~Battlecry"
	requireTarget, effects, description = False, "Taunt", "Taunt. Battlecry: Double this minion's Health"
	name_CN = "无面潜伏者"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.setStat(self, newHealth=self.health*2, name=FacelessLurker)
		
		
class DesertObelisk(Minion):
	Class, race, name = "Neutral", "", "Desert Obelisk"
	mana, attack, health = 5, 0, 5
	index = "ULDUM~Neutral~Minion~5~0~5~~Desert Obelisk"
	requireTarget, effects, description = False, "", "If your control 3 of these at the end of your turn, deal 5 damage to a random enemy"
	name_CN = "沙漠方尖碑"
	trigBoard = Trig_DesertObelisk		


class MortuaryMachine(Minion):
	Class, race, name = "Neutral", "Mech", "Mortuary Machine"
	mana, attack, health = 5, 8, 8
	index = "ULDUM~Neutral~Minion~5~8~8~Mech~Mortuary Machine"
	requireTarget, effects, description = False, "", "After your opponent plays a minion, give it Reborn"
	name_CN = "机械法医"
	trigBoard = Trig_MortuaryMachine		


class PhalanxCommander(Minion):
	Class, race, name = "Neutral", "", "Phalanx Commander"
	mana, attack, health = 5, 4, 5
	index = "ULDUM~Neutral~Minion~5~4~5~~Phalanx Commander"
	requireTarget, effects, description = False, "", "Your Taunt minions have +2 Attack"
	name_CN = "方阵指挥官"
	aura = Aura_PhalanxCommander
	
	
class WastelandAssassin(Minion):
	Class, race, name = "Neutral", "", "Wasteland Assassin"
	mana, attack, health = 5, 4, 2
	index = "ULDUM~Neutral~Minion~5~4~2~~Wasteland Assassin~Stealth~Reborn"
	requireTarget, effects, description = False, "Stealth,Reborn", "Stealth, Reborn"
	name_CN = "废土刺客"
	

class BlatantDecoy(Minion):
	Class, race, name = "Neutral", "", "Blatant Decoy"
	mana, attack, health = 6, 5, 5
	index = "ULDUM~Neutral~Minion~6~5~5~~Blatant Decoy~Deathrattle"
	requireTarget, effects, description = False, "", "Deathrattle: Each player summons the lowest Cost minion from their hand"
	name_CN = "显眼的诱饵"
	deathrattle = Death_BlatantDecoy


class KhartutDefender(Minion):
	Class, race, name = "Neutral", "", "Khartut Defender"
	mana, attack, health = 6, 3, 4
	index = "ULDUM~Neutral~Minion~6~3~4~~Khartut Defender~Taunt~Reborn~Deathrattle"
	requireTarget, effects, description = False, "Taunt,Reborn", "Taunt, Reborn. Deathrattle: Restore 4 Health to your hero"
	name_CN = "卡塔图防御者"
	deathrattle = Death_KhartutDefender


class Siamat(Minion):
	Class, race, name = "Neutral", "Elemental", "Siamat"
	mana, attack, health = 7, 6, 6
	index = "ULDUM~Neutral~Minion~7~6~6~Elemental~Siamat~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: Gain 2 of Rush, Taunt, Divine Shield, or Windfury (your choice)"
	name_CN = "希亚玛特"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.choices = []
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		options = [option(ID=self.ID) for option in (SiamatsHeart, SiamatsShield, SiamatsSpeed, SiamatsWind)]
		for num in range(2):
			for option in reversed(options):
				if self.effects[option.effect] > 0: options.remove(option)
			if options: self.chooseFixedOptions(Siamat, comment, options=options)
			else: break
	
	#option here can be either category or object
	def discoverDecided(self, option, case, info_RNGSync=None, info_GUISync=None):
		if case != "Guided": self.Game.picks_Backup((info_RNGSync, info_GUISync, case == "Random", type(option)))
		self.giveEnchant(self, effGain=option.effect, name=Siamat)
		

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
	index = "ULDUM~Neutral~Minion~7~3~9~Beast~Wasteland Scorpid~Poisonous"
	requireTarget, effects, description = False, "Poisonous", "Poisonous"
	name_CN = "废土巨蝎"
	
	
class WrappedGolem(Minion):
	Class, race, name = "Neutral", "", "Wrapped Golem"
	mana, attack, health = 7, 7, 5
	index = "ULDUM~Neutral~Minion~7~7~5~~Wrapped Golem~Reborn"
	requireTarget, effects, description = False, "Reborn", "Reborn. At the end of your turn, summon a 1/1 Scarab with Taunt"
	name_CN = "被缚的魔像"
	trigBoard = Trig_WrappedGolem		


class Octosari(Minion):
	Class, race, name = "Neutral", "Beast", "Octosari"
	mana, attack, health = 8, 8, 8
	index = "ULDUM~Neutral~Minion~8~8~8~Beast~Octosari~Deathrattle~Legendary"
	requireTarget, effects, description = False, "", "Deathrattle: Draw 8 cards"
	name_CN = "八爪巨怪"
	deathrattle = Death_Octosari


class PitCrocolisk(Minion):
	Class, race, name = "Neutral", "Beast", "Pit Crocolisk"
	mana, attack, health = 8, 5, 6
	index = "ULDUM~Neutral~Minion~8~5~6~Beast~Pit Crocolisk~Battlecry"
	requireTarget, effects, description = True, "", "Battlecry: Deal 5 damage"
	name_CN = "深坑鳄鱼"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.dealsDamage(target, 5)
		return target
		
		
class AnubisathWarbringer(Minion):
	Class, race, name = "Neutral", "", "Anubisath Warbringer"
	mana, attack, health = 9, 9, 6
	index = "ULDUM~Neutral~Minion~9~9~6~~Anubisath Warbringer~Deathrattle"
	requireTarget, effects, description = False, "", "Deathrattle: Give all minions in your hand +3/+3"
	name_CN = "阿努比萨斯战争使者"
	deathrattle = Death_AnubisathWarbringer


class ColossusoftheMoon(Minion):
	Class, race, name = "Neutral", "", "Colossus of the Moon"
	mana, attack, health = 10, 10, 10
	index = "ULDUM~Neutral~Minion~10~10~10~~Colossus of the Moon~Divine Shield~Reborn~Legendary"
	requireTarget, effects, description = False, "Divine Shield,Reborn", "Divine Shield, Reborn"
	
	
class KingPhaoris(Minion):
	Class, race, name = "Neutral", "", "King Phaoris"
	mana, attack, health = 10, 5, 5
	index = "ULDUM~Neutral~Minion~10~5~5~~King Phaoris~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: For each spell in your hand, summon a minion of the same Cost"
	name_CN = "法奥瑞斯国王"
	poolIdentifier = "0-Cost Minions to Summon"
	@classmethod
	def generatePool(cls, pools):
		return ["%d-Cost Minions to Summon"%cost for cost in pools.MinionsofCost.keys()], \
				[list(pools.MinionsofCost[cost].values()) for cost in pools.MinionsofCost.keys()]
	#不知道如果手中法术的法力值没有对应随从时会如何
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		game, minions = self.Game, []
		for card in self.Game.Hand_Deck.hands[self.ID]:
			if card.category == "Spell": minions.append(self.newEvolved(card.mana-1, by=1, ID=self.ID))
		if minions: self.summon(minions)
		
		
class LivingMonument(Minion):
	Class, race, name = "Neutral", "", "Living Monument"
	mana, attack, health = 10, 10, 10
	index = "ULDUM~Neutral~Minion~10~10~10~~Living Monument~Taunt"
	requireTarget, effects, description = False, "Taunt", "Taunt"
	name_CN = "活化方尖碑"
	
	
class UntappedPotential(Quest):
	Class, school, name = "Druid", "", "Untapped Potential"
	requireTarget, mana, effects = False, 1, ""
	index = "ULDUM~Druid~Spell~1~~Untapped Potential~~Quest~Legendary"
	description = "Quest: End 4 turns with any unspent Mana. Reward: Orissian Tear"
	name_CN = "发掘潜力"
	trigBoard = Trig_UntappedPotential
	def questEffect(self, game, ID):
		OssirianTear(game, ID).replacePower()

class OssirianTear(Power):
	mana, name, requireTarget = 0, "Ossirian Tear", False
	index = "Druid~Hero Power~0~Ossirian Tear"
	description = "Passive Hero Power. Your Choose One cards have both effects combined"
	name_CN = "奥斯里安之泪"
	def available(self, choice=0):
		return False
		
	def use(self, target=None, choice=0, sendthruServer=True):
		return 0
		
	def appears(self):
		self.Game.effects[self.ID]["Choose Both"] += 1
		
	def disappears(self):
		if self.Game.effects[self.ID]["Choose Both"] > 0:
			self.Game.effects[self.ID]["Choose Both"] -= 1
			
			
class WorthyExpedition(Spell):
	Class, school, name = "Druid", "", "Worthy Expedition"
	requireTarget, mana, effects = False, 1, ""
	index = "ULDUM~Druid~Spell~1~~Worthy Expedition"
	description = "Discover a Choose One card"
	name_CN = "不虚此行"
	poolIdentifier = "Choose One Cards"
	@classmethod
	def generatePool(cls, pools):
		return "Choose One Cards", [value for key, value in pools.ClassCards["Druid"].items() if "~Choose One" in key]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverandGenerate(WorthyExpedition, comment, poolFunc=lambda : self.rngPool("Choose One Cards"))
		
		
class CrystalMerchant(Minion):
	Class, race, name = "Druid", "", "Crystal Merchant"
	mana, attack, health = 2, 1, 4
	index = "ULDUM~Druid~Minion~2~1~4~~Crystal Merchant"
	requireTarget, effects, description = False, "", "If you have any unspent Mana at the end of your turn, draw a card"
	name_CN = "水晶商人"
	trigBoard = Trig_CrystalMerchant		


class BEEEES(Spell):
	Class, school, name = "Druid", "", "BEEEES!!!"
	requireTarget, mana, effects = True, 3, ""
	index = "ULDUM~Druid~Spell~3~~BEEEES!!!"
	description = "Choose a minion. Summon four 1/1 Bees that attack it"
	name_CN = "蜜蜂"
	def available(self):
		return self.selectableMinionExists() and self.Game.space(self.ID) > 0
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			bees = [Bee_Uldum(self.Game, self.ID) for i in (0, 1, 2, 3)]
			self.summon(bees)
			for bee in bees: #召唤的蜜蜂需要在场上且存活，同时目标也需要在场且存活
				if bee.onBoard and bee.health > 0 and bee.dead == False and target.onBoard and target.health > 0 and target.dead == False:
					self.Game.battle(bee, target, verifySelectable=False, useAttChance=False, resolveDeath=False)
		return target
		
class Bee_Uldum(Minion):
	Class, race, name = "Druid", "Beast", "Bee"
	mana, attack, health = 1, 1, 1
	index = "ULDUM~Druid~Minion~1~1~1~Beast~Bee~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "蜜蜂"
	
	
class GardenGnome(Minion):
	Class, race, name = "Druid", "", "Garden Gnome"
	mana, attack, health = 4, 2, 3
	index = "ULDUM~Druid~Minion~4~2~3~~Garden Gnome~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: If you're holding a spell that costs (5) or more, summon two 2/2 Treants"
	name_CN = "园艺侏儒"
	
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.holdingSpellwith5CostorMore(self.ID)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Hand_Deck.holdingSpellwith5CostorMore(self.ID):
			self.summon([Treant_Uldum(self.Game, self.ID) for _ in (0, 1)], relative="<>")
		
		
class Treant_Uldum(Minion):
	Class, race, name = "Druid", "", "Treant"
	mana, attack, health = 2, 2, 2
	index = "ULDUM~Druid~Minion~2~2~2~~Treant~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "树人"
	
	
class AnubisathDefender(Minion):
	Class, race, name = "Druid", "", "Anubisath Defender"
	mana, attack, health = 5, 3, 5
	index = "ULDUM~Druid~Minion~5~3~5~~Anubisath Defender~Taunt"
	requireTarget, effects, description = False, "Taunt", "Taunt. Costs (0) if you've cast a spell this turn that costs (5) or more"
	name_CN = "阿努比萨斯防御者"
	trigHand = Trig_AnubisathDefender
	def selfManaChange(self):
		if self.inHand and self.ID == self.Game.turn:
			if any(card.category == "Spell" and mana > 4 for card, mana in \
						zip(self.Game.Counters.cardsPlayedEachTurn[self.ID][-1],
							self.Game.Counters.manas4CardsEachTurn[self.ID][-1])):
				self.mana = 0
			

class ElisetheEnlightened(Minion):
	Class, race, name = "Druid", "", "Elise the Enlightened"
	mana, attack, health = 5, 5, 5
	index = "ULDUM~Druid~Minion~5~5~5~~Elise the Enlightened~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: If your deck has no duplicates, duplicate your hand"
	name_CN = "启迪者伊莉斯"
	
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.noDuplicatesinDeck(self.ID)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		HD = self.Game.Hand_Deck
		if HD.noDuplicatesinDeck(self.ID):
			for card in HD.hands[self.ID][:]:
				HD.addCardtoHand(card.selfCopy(self.ID, self), self.ID)


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
	index = "ULDUM~Druid~Minion~5~3~3~Elemental~Oasis Surger~Rush~Choose One"
	requireTarget, effects, description = False, "Rush", "Rush. Choose One: Gain +2/+2; or Summon a copy of this minion"
	name_CN = "绿洲涌动者"
	options = (FocusedBurst_Option, DivideandConquer_Option)
	#对于抉择随从而言，应以与战吼类似的方式处理，打出时抉择可以保持到最终结算。但是打出时，如果因为鹿盔和发掘潜力而没有选择抉择，视为到对方场上之后仍然可以而没有如果没有
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if choice < 1: self.giveEnchant(self, 2, 2, name=OasisSurger)
		if choice != 0:
			Copy = self.selfCopy(self.ID, self) if self.onBoard else type(self)(self.Game, self.ID)
			self.summon(Copy)


class BefriendtheAncient(Spell):
	Class, school, name = "Druid", "", "Befriend the Ancient"
	requireTarget, mana, effects = False, 6, ""
	index = "ULDUM~Druid~Spell~6~Nature~Befriend the Ancient~Uncollectible"
	description = "Summon a 6/6 Ancient with Taunt"
	name_CN = "结识古树"
	def available(self):
		return self.Game.space(self.ID)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon(VirnaalAncient(self.Game, self.ID))
		
class DrinktheWater(Spell):
	Class, school, name = "Druid", "", "Drink the Water"
	requireTarget, mana, effects = True, 6, ""
	index = "ULDUM~Druid~Spell~6~Nature~Drink the Water~Uncollectible"
	description = "Restore 12 Health"
	name_CN = "饮用泉水"
	def text(self): return self.calcHeal(12)
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.restoresHealth(target, self.calcHeal(12))
		return target
		
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
		return self.keeper.selectableCharacterExists(1)

class HiddenOasis(Spell):
	Class, school, name = "Druid", "Nature", "Hidden Oasis"
	requireTarget, mana, effects = True, 6, ""
	index = "ULDUM~Druid~Spell~6~Nature~Hidden Oasis~Choose One"
	description = "Choose One: Summon a 6/6 Ancient with Taunt; or Restore 12 Health"
	name_CN = "隐秘绿洲"
	options = (BefriendtheAncient_Option, DrinktheWater_Option)
	def needTarget(self, choice=0):
		return choice != 0
		
	def available(self):
		#当场上有全选光环时，变成了一个指向性法术，必须要有一个目标可以施放。
		if self.Game.effects[self.ID]["Choose Both"] > 0:
			return self.selectableCharacterExists(1)
		else: return self.Game.space(self.ID) > 0 or self.selectableCharacterExists(1)
			
	def text(self): return self.calcHeal(12)
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if choice != 0 and target: self.restoresHealth(target, self.calcHeal(12))
		if choice < 1: self.summon(VirnaalAncient(self.Game, self.ID))
		return target

class VirnaalAncient(Minion):
	Class, race, name = "Druid", "", "Vir'naal Ancient"
	mana, attack, health = 6, 6, 6
	index = "ULDUM~Druid~Minion~6~6~6~~Vir'naal Ancient~Taunt~Uncollectible"
	requireTarget, effects, description = False, "Taunt", "Taunt"
	name_CN = "维尔纳尔古树"
	
	
class Overflow(Spell):
	Class, school, name = "Druid", "Nature", "Overflow"
	requireTarget, mana, effects = False, 7, ""
	index = "ULDUM~Druid~Spell~7~Nature~Overflow"
	description = "Restore 5 Health to all characters. Draw 5 cards"
	name_CN = "溢流"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		heal = self.calcHeal(5)
		targets = [self.Game.heroes[self.ID], self.Game.heroes[3-self.ID]] + self.Game.minionsonBoard(self.ID) + self.Game.minionsonBoard(3-self.ID)
		self.AOE_Heal(targets, [heal for obj in targets])
		for _ in range(5): self.Game.Hand_Deck.drawCard(self.ID)
		

class UnsealtheVault(Quest):
	Class, school, name = "Hunter", "", "Unseal the Vault"
	requireTarget, mana, effects = False, 1, ""
	index = "ULDUM~Hunter~Spell~1~~Unseal the Vault~~Quest~Legendary"
	description = "Quest: Summon 20 minions. Reward: Ramkahen Roar"
	name_CN = "打开宝库"
	trigBoard = Trig_UnsealtheVault
	def questEffect(self, game, ID):
		PharaohsWarmask(game, ID).replacePower()

class PharaohsWarmask(Power):
	mana, name, requireTarget = 2, "Pharaoh's Warmask", False
	index = "Hunter~Hero Power~2~Pharaoh's Warmask"
	description = "Give your minions +2 Attack"
	name_CN = "法老的面盔"
	def effect(self, target=None, choice=0, comment=''):
		self.AOE_GiveEnchant(self.Game.minionsonBoard(self.ID), 2, 0, name=PharaohsWarmask)
		return 0
		
		
class PressurePlate(Secret):
	Class, school, name = "Hunter", "", "Pressure Plate"
	requireTarget, mana, effects = False, 2, ""
	index = "ULDUM~Hunter~Spell~2~~Pressure Plate~~Secret"
	description = "Secret: After your opponent casts a spell, destroy a random enemy minion"
	name_CN = "压感陷阱"
	trigBoard = Trig_PressurePlate		


class DesertSpear(Weapon):
	Class, name, description = "Hunter", "Desert Spear", "After your hero Attacks, summon a 1/1 Locust with Rush"
	mana, attack, durability, effects = 3, 1, 3, ""
	index = "ULDUM~Hunter~Weapon~3~1~3~Desert Spear"
	name_CN = "沙漠之矛"
	trigBoard = Trig_DesertSpear		


class HuntersPack(Spell):
	Class, school, name = "Hunter", "", "Hunter's Pack"
	requireTarget, mana, effects = False, 3, ""
	index = "ULDUM~Hunter~Spell~3~~Hunter's Pack"
	description = "Add a random Hunter Beast, Secret, and Weapon to your hand"
	name_CN = "猎人工具包"
	poolIdentifier = "Hunter Beasts"
	@classmethod
	def generatePool(cls, pools):
		beasts, secrets, weapons = [], [], []
		for key, value in pools.ClassCards["Hunter"].items():
			if "~Beast~" in key: beasts.append(value)
			elif value.race == "Secret": secrets.append(value)
			elif "~Weapon~" in key: weapons.append(value)
		return ["Hunter Beasts", "Hunter Secrets", "Hunter Weapons"], [beasts, secrets, weapons]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.addCardtoHand(numpyChoice(self.rngPool("Hunter Beasts")),
							 numpyChoice(self.rngPool("Hunter Secrets")),
							 numpyChoice(self.rngPool("Hunter Weapons")), self.ID)
		
		
class HyenaAlpha(Minion):
	Class, race, name = "Hunter", "Beast", "Hyena Alpha"
	mana, attack, health = 4, 3, 3
	index = "ULDUM~Hunter~Minion~4~3~3~Beast~Hyena Alpha~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: If you control a Secret, summon two 2/2 Hyenas"
	name_CN = "土狼头领"
	
	def effCanTrig(self):
		self.effectViable = self.Game.Secrets.secrets[self.ID] != []
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Secrets.secrets[self.ID]: self.summon([Hyena_Uldum(self.Game, self.ID) for _ in (0, 1)], relative="<>")
		

class Hyena_Uldum(Minion):
	Class, race, name = "Hunter", "Beast", "Hyena"
	mana, attack, health = 2, 2, 2
	index = "ULDUM~Hunter~Minion~2~2~2~Beast~Hyena~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "土狼"
	
	
class RamkahenWildtamer(Minion):
	Class, race, name = "Hunter", "", "Ramkahen Wildtamer"
	mana, attack, health = 3, 4, 3
	index = "ULDUM~Hunter~Minion~3~4~3~~Ramkahen Wildtamer~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Copy a random Beast in your hand"
	name_CN = "拉穆卡恒驯兽师"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if beasts := [card for card in self.Game.Hand_Deck.hands[self.ID] if "Beast" in card.race]:
			self.addCardtoHand(numpyChoice(beasts).selfCopy(self.ID, self), self.ID)
		
		
class SwarmofLocusts(Spell):
	Class, school, name = "Hunter", "", "Swarm of Locusts"
	requireTarget, mana, effects = False, 6, ""
	index = "ULDUM~Hunter~Spell~6~~Swarm of Locusts"
	description = "Summon seven 1/1 Locusts with Rush"
	name_CN = "飞蝗虫群"
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon([Locust(self.Game, self.ID) for i in range(7)])
		
		
class ScarletWebweaver(Minion):
	Class, race, name = "Hunter", "Beast", "Scarlet Webweaver"
	mana, attack, health = 6, 5, 5
	index = "ULDUM~Hunter~Minion~6~5~5~Beast~Scarlet Webweaver~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Reduce the Cost of a random Beast in your hand by (5)"
	name_CN = "猩红织网蛛"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if cards := self.findCards4ManaReduction(lambda card: "Beast" in card.race):
			ManaMod(numpyChoice(cards), by=-5).applies()

		
class WildBloodstinger(Minion):
	Class, race, name = "Hunter", "Beast", "Wild Bloodstinger"
	mana, attack, health = 6, 6, 9
	index = "ULDUM~Hunter~Minion~6~6~9~Beast~Wild Bloodstinger~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Summon a minion from your opponent's hand. Attack it"
	name_CN = "刺血狂蝎"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.space(3-self.ID) and \
			(indices := [i for i, card in enumerate(self.Game.Hand_Deck.hands[3-self.ID] ) if card.category == "Minion"]):
			minion = self.Game.summonfrom(numpyChoice(indices), 3-self.ID, -1, summoner=self, source='H')
			if minion.onBoard: self.Game.battle(self, minion, verifySelectable=False, useAttChance=False, resolveDeath=False)
		
		
class DinotamerBrann(Minion):
	Class, race, name = "Hunter", "", "Dinotamer Brann"
	mana, attack, health = 7, 2, 4
	index = "ULDUM~Hunter~Minion~7~2~4~~Dinotamer Brann~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: If your deck has no duplicates, summon King Krush"
	name_CN = "恐龙大师布莱恩"
	
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.noDuplicatesinDeck(self.ID)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Hand_Deck.noDuplicatesinDeck(self.ID): self.summon(KingKrush_Uldum(self.Game, self.ID))
		

class KingKrush_Uldum(Minion):
	Class, race, name = "Hunter", "Beast", "King Krush"
	mana, attack, health = 9, 8, 8
	index = "ULDUM~Hunter~Minion~9~8~8~Beast~King Krush~Charge~Legendary~Uncollectible"
	requireTarget, effects, description = False, "Charge", "Charge"
	name_CN = "暴龙王克鲁什"
	
	
class RaidtheSkyTemple(Quest):
	Class, school, name = "Mage", "", "Raid the Sky Temple"
	requireTarget, mana, effects = False, 1, ""
	index = "ULDUM~Mage~Spell~1~~Raid the Sky Temple~~Quest~Legendary"
	description = "Quest: Cast 10 spell. Reward: Ascendant Scroll"
	name_CN = "洗劫天空殿"
	trigBoard = Trig_RaidtheSkyTemple
	poolIdentifier = "Mage Spells"
	@classmethod
	def generatePool(cls, pools):
		return "Mage Spells", [value for key, value in pools.ClassCards["Mage"].items() if "~Spell~" in key]

	def questEffect(self, game, ID):
		AscendantScroll(game, ID).replacePower()

class AscendantScroll(Power):
	mana, name, requireTarget = 2, "Ascendant Scroll", False
	index = "Mage~Hero Power~2~Ascendant Scroll"
	description = "Add a random Mage spell to your hand. It costs (2) less"
	name_CN = "升腾卷轴"
	def effect(self, target=None, choice=0, comment=''):
		spell = numpyChoice(self.rngPool("Mage Spells"))(self.Game, self.ID)
		spell.manaMods.append(ManaMod(spell, by=-2))
		self.addCardtoHand(spell, self.ID)
		return 0
		
		
class AncientMysteries(Spell):
	Class, school, name = "Mage", "Arcane", "Ancient Mysteries"
	requireTarget, mana, effects = False, 2, ""
	index = "ULDUM~Mage~Spell~2~Arcane~Ancient Mysteries"
	description = "Draw a Secret from your deck. It costs (0)"
	name_CN = "远古谜团"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		card, mana, entersHand = self.drawCertainCard(lambda card: card.race == "Secret")
		if entersHand: ManaMod(card, to=0).applies()
		
		
class FlameWard(Secret):
	Class, school, name = "Mage", "Fire", "Flame Ward"
	requireTarget, mana, effects = False, 3, ""
	index = "ULDUM~Mage~Spell~3~Fire~Flame Ward~~Secret"
	description = "Secret: After a minion attacks your hero, deal 3 damage to all enemy minions"
	name_CN = "火焰结界"
	trigBoard = Trig_FlameWard		


class CloudPrince(Minion):
	Class, race, name = "Mage", "Elemental", "Cloud Prince"
	mana, attack, health = 5, 4, 4
	index = "ULDUM~Mage~Minion~5~4~4~Elemental~Cloud Prince~Battlecry"
	requireTarget, effects, description = True, "", "Battlecry: If you control a Secret, deal 6 damage"
	name_CN = "云雾王子"
	
	def needTarget(self, choice=0):
		return self.Game.Secrets.secrets[self.ID] != []
		
	def effCanTrig(self):
		self.effectViable = self.Game.Secrets.secrets[self.ID] != []
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and self.Game.Secrets.secrets[self.ID] != []:
			self.dealsDamage(target, 6)
		return target
		
	
class ArcaneFlakmage(Minion):
	Class, race, name = "Mage", "", "Arcane Flakmage"
	mana, attack, health = 2, 3, 2
	index = "ULDUM~Mage~Minion~2~3~2~~Arcane Flakmage"
	requireTarget, effects, description = False, "", "After you play a Secret, deal 2 damage to all enemy minions"
	name_CN = "对空奥术法师"
	trigBoard = Trig_ArcaneFlakmage		


class DuneSculptor(Minion):
	Class, race, name = "Mage", "", "Dune Sculptor"
	mana, attack, health = 3, 3, 3
	index = "ULDUM~Mage~Minion~3~3~3~~Dune Sculptor"
	requireTarget, effects, description = False, "", "After you cast a spell, add a random Mage minion to your hand"
	name_CN = "沙丘塑形者"
	poolIdentifier = "Mage Minions"
	@classmethod
	def generatePool(cls, pools):
		return "Mage Minions", [value for key, value in pools.ClassCards["Mage"].items() if "~Minion~" in key]
		
	trigBoard = Trig_DuneSculptor		


class NagaSandWitch(Minion):
	Class, race, name = "Mage", "", "Naga Sand Witch"
	mana, attack, health = 5, 5, 5
	index = "ULDUM~Mage~Minion~5~5~5~~Naga Sand Witch~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Change the Cost of spells in your hand to (5)"
	name_CN = "纳迦沙漠女巫"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for spell in [card for card in self.Game.Hand_Deck.hands[self.ID] if card.category == "Spell"]:
			ManaMod(spell, to=5).applies()
		self.Game.Manas.calcMana_All()
		
		
class TortollanPilgrim(Minion):
	Class, race, name = "Mage", "", "Tortollan Pilgrim"
	mana, attack, health = 8, 5, 5
	index = "ULDUM~Mage~Minion~8~5~5~~Tortollan Pilgrim~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Discover a spell in your deck and cast it with random targets"
	name_CN = "始祖龟朝圣者"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverfromCardList(TortollanPilgrim, comment, conditional=lambda card: card.category == "Spell")
		
	def discoverDecided(self, option, case, info_RNGSync=None, info_GUISync=None):
		self.handleDiscoveredCardfromList(option, case, ls=self.Game.Hand_Deck.decks[self.ID],
										  func=lambda index, card: self.Game.Hand_Deck.extractfromHand(index, ID=self.ID, getAll=False, enemyCanSee=True)[0].cast(),
										  info_RNGSync=info_RNGSync, info_GUISync=info_GUISync)
		
		
class RenotheRelicologist(Minion):
	Class, race, name = "Mage", "", "Reno the Relicologist"
	mana, attack, health = 6, 4, 6
	index = "ULDUM~Mage~Minion~6~4~6~~Reno the Relicologist~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: If your deck has no duplicates, deal 10 damage randomly split among all enemy minions"
	name_CN = "考古学家 雷诺"
	
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.noDuplicatesinDeck(self.ID)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		game, side = self.Game, 3 - self.ID
		if game.Hand_Deck.noDuplicatesinDeck(self.ID):
			for _ in range(10):
				if minions := game.minionsAlive(side): self.dealsDamage(numpyChoice(minions), 1)
				else: break
		
		
class PuzzleBoxofYoggSaron(Spell):
	Class, school, name = "Mage", "", "Puzzle Box of Yogg-Saron"
	requireTarget, mana, effects = False, 10, ""
	index = "ULDUM~Mage~Spell~10~~Puzzle Box of Yogg-Saron"
	description = "Cast 10 random spells (targets chosen randomly)"
	name_CN = "尤格-萨隆的谜之匣"
	poolIdentifier = "Spells"
	@classmethod
	def generatePool(cls, pools):
		spells = []
		for Class in pools.Classes:
			spells += [value for key, value in pools.ClassCards[Class].items() if "~Spell~" in key]
		return "Spells", spells
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		game = self.Game
		game.sendSignal("SpellBeenCast", self.ID, self, None, 0, "", choice)
		for i in range(10):
			numpyChoice(self.rngPool("Spells"))(game, self.ID).cast()
			game.gathertheDead(decideWinner=True)
		
		
class MakingMummies(Quest):
	Class, school, name = "Paladin", "", "Making Mummies"
	requireTarget, mana, effects = False, 1, ""
	index = "ULDUM~Paladin~Spell~1~~Making Mummies~~Quest~Legendary"
	description = "Quest: Play 5 Reborn minions. Reward: Emperor Wraps"
	name_CN = "制作木乃伊"
	trigBoard = Trig_MakingMummies
	def questEffect(self, game, ID):
		EmperorWraps(game, ID).replacePower()

class EmperorWraps(Power):
	mana, name, requireTarget = 2, "Emperor Wraps", True
	index = "Paladin~Hero Power~2~Emperor Wraps"
	description = "Summon a 2/2 copy of a friendly minion"
	name_CN = "帝王裹布"
	def available(self, choice=0):
		return not self.chancesUsedUp() and self.Game.space(self.ID) and self.selectableFriendlyMinionExists()
		
	def effect(self, target=None, choice=0, comment=''):
		if target: self.summon(target.selfCopy(self.ID, self, 2, 2))
		return 0
		
		
class BrazenZealot(Minion):
	Class, race, name = "Paladin", "", "Brazen Zealot"
	mana, attack, health = 1, 2, 1
	index = "ULDUM~Paladin~Minion~1~2~1~~Brazen Zealot"
	requireTarget, effects, description = False, "", "Whenever you summon a minion, gain +1 Attack"
	name_CN = "英勇狂热者"
	trigBoard = Trig_BrazenZealot		


class MicroMummy(Minion):
	Class, race, name = "Paladin", "Mech", "Micro Mummy"
	mana, attack, health = 2, 1, 2
	index = "ULDUM~Paladin~Minion~2~1~2~Mech~Micro Mummy~Reborn"
	requireTarget, effects, description = False, "Reborn", "Reborn. At the end of your turn, give another random friendly minion +1 Attack"
	name_CN = "微型木乃伊"
	trigBoard = Trig_MicroMummy		


class SandwaspQueen(Minion):
	Class, race, name = "Paladin", "Beast", "Sandwasp Queen"
	mana, attack, health = 2, 3, 1
	index = "ULDUM~Paladin~Minion~2~3~1~Beast~Sandwasp Queen~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Add two 2/1 Sandwasps to your hand"
	name_CN = "沙漠蜂后"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.addCardtoHand([Sandwasp, Sandwasp], self.ID)
		

class Sandwasp(Minion):
	Class, race, name = "Paladin", "Beast", "Sandwasp"
	mana, attack, health = 1, 2, 1
	index = "ULDUM~Paladin~Minion~1~2~1~Beast~Sandwasp~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "沙漠胡蜂"
	
	
class SirFinleyoftheSands(Minion):
	Class, race, name = "Paladin", "Murloc", "Sir Finley of the Sands"
	mana, attack, health = 2, 2, 3
	index = "ULDUM~Paladin~Minion~2~2~3~Murloc~Sir Finley of the Sands~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: If your deck has no duplicates, Discover an upgraded Hero Power"
	name_CN = "沙漠爵士芬利"
	poolIdentifier = "Upgraded Powers"
	@classmethod
	def generatePool(cls, pools):
		return "Upgraded Powers", pools.upgradedPowers
		
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.noDuplicatesinDeck(self.ID)
		
	def decideUpgradedPowerPool(self):
		powerType = type(self.Game.powers[self.ID])
		return [power for power in self.rngPool("Upgraded Powers") if power != powerType]
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverandGenerate(SirFinleyoftheSands, comment, poolFunc=lambda : SirFinleyoftheSands.decideUpgradedPowerPool(self))
		
	def discoverDecided(self, option, case, info_RNGSync=None, info_GUISync=None):
		self.handleDiscoverGeneratedCard(option, case, info_RNGSync, info_GUISync,
										 func=lambda cardType, card: option.replacePower())
		
		
class Subdue(Spell):
	Class, school, name = "Paladin", "", "Subdue"
	requireTarget, mana, effects = True, 2, ""
	index = "ULDUM~Paladin~Spell~2~~Subdue"
	description = "Change a minion's Attack and Health to 1"
	name_CN = "制伏"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.setStat(target, 1, 1, name=Subdue)
		return target
		
		
class SalhetsPride(Minion):
	Class, race, name = "Paladin", "Beast", "Salhet's Pride"
	mana, attack, health = 3, 3, 1
	index = "ULDUM~Paladin~Minion~3~3~1~Beast~Salhet's Pride~Deathrattle"
	requireTarget, effects, description = False, "", "Deathrattle: Draw two 1-Health minions from your deck"
	name_CN = "萨赫特的傲狮"
	deathrattle = Death_SalhetsPride


class AncestralGuardian(Minion):
	Class, race, name = "Paladin", "", "Ancestral Guardian"
	mana, attack, health = 4, 4, 2
	index = "ULDUM~Paladin~Minion~4~4~2~~Ancestral Guardian~Lifesteal~Reborn"
	requireTarget, effects, description = False, "Lifesteal,Reborn", "Lifesteal, Reborn"
	name_CN = "先祖守护者"
	
	
class PharaohsBlessing(Spell):
	Class, school, name = "Paladin", "Holy", "Pharaoh's Blessing"
	requireTarget, mana, effects = True, 6, ""
	index = "ULDUM~Paladin~Spell~6~Holy~Pharaoh's Blessing"
	description = "Give a minion +4/+4, Divine Shield, and Taunt"
	name_CN = "法老祝福"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.giveEnchant(target, 4, 4, multipleEffGains=(("Divine Shield", 1, None), ("Taunt", 1, None)), name=PharaohsBlessing)
		return target
		
		
class TiptheScales(Spell):
	Class, school, name = "Paladin", "", "Tip the Scales"
	requireTarget, mana, effects = False, 8, ""
	index = "ULDUM~Paladin~Spell~8~~Tip the Scales"
	description = "Summon 7 Murlocs from your deck"
	name_CN = "鱼人为王"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for _ in range(7):
			if not self.try_SummonfromDeck(func=lambda card: "Murloc" in card.race): break
		
		
class ActivatetheObelisk(Quest):
	Class, school, name = "Priest", "", "Activate the Obelisk"
	requireTarget, mana, effects = False, 1, ""
	index = "ULDUM~Priest~Spell~1~~Activate the Obelisk~~Quest~Legendary"
	description = "Quest: Restore 15 Health. Reward: Obelisk's Eye"
	name_CN = "激活方尖碑"
	trigBoard = Trig_ActivatetheObelisk
	def questEffect(self, game, ID):
		ObelisksEye(game, ID).replacePower()

class ObelisksEye(Power):
	mana, name, requireTarget = 2, "Obelisk's Eye", True
	index = "Priest~Hero Power~2~Obelisk's Eye"
	description = "Restore 3 Health. If you target a minion, also give it +3/+3"
	name_CN = "方尖碑之眼"
	def text(self): return self.calcHeal(3)
	
	def effect(self, target=None, choice=0, comment=''):
		self.restoresHealth(target, self.calcHeal(3))
		if target.category == "Minion": self.giveEnchant(target, 3, 3, name=ObelisksEye)
		if target.health < 1 or target.dead:
			return 1
		return 0
		
		
class EmbalmingRitual(Spell):
	Class, school, name = "Priest", "", "Embalming Ritual"
	requireTarget, mana, effects = True, 1, ""
	index = "ULDUM~Priest~Spell~1~~Embalming Ritual"
	description = "Give a minion Reborn"
	name_CN = "防腐仪式"
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.giveEnchant(target, effGain="Reborn", name=EmbalmingRitual)
		return target
		
		
class Penance(Spell):
	Class, school, name = "Priest", "Holy", "Penance"
	requireTarget, mana, effects = True, 2, "Lifesteal"
	index = "ULDUM~Priest~Spell~2~Holy~Penance~Lifesteal"
	description = "Lifesteal. Deal 3 damage to a minion"
	name_CN = "苦修"
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = self.calcDamage(3)
			self.dealsDamage(target, damage)
		return target
		
		
class SandhoofWaterbearer(Minion):
	Class, race, name = "Priest", "", "Sandhoof Waterbearer"
	mana, attack, health = 5, 5, 5
	index = "ULDUM~Priest~Minion~5~5~5~~Sandhoof Waterbearer"
	requireTarget, effects, description = False, "", "At the end of your turn, restore 5 Health to a damaged friendly character"
	name_CN = "沙蹄搬水工"
	trigBoard = Trig_SandhoofWaterbearer		


class Grandmummy(Minion):
	Class, race, name = "Priest", "", "Grandmummy"
	mana, attack, health = 2, 1, 2
	index = "ULDUM~Priest~Minion~2~1~2~~Grandmummy~Reborn~Deathrattle"
	requireTarget, effects, description = False, "Reborn", "Reborn. Deathrattle: Give a random friendly minion +1/+1"
	name_CN = "木奶伊"
	deathrattle = Death_Grandmummy


class HolyRipple(Spell):
	Class, school, name = "Priest", "Holy", "Holy Ripple"
	requireTarget, mana, effects = False, 2, ""
	index = "ULDUM~Priest~Spell~2~Holy~Holy Ripple"
	description = "Deal 1 damage to all enemies. Restore 1 Health to all friendly characters"
	name_CN = "神圣涟漪"
	def text(self): return "%d, %d"%(self.calcDamage(1), self.calcHeal(1))
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage, heal = self.calcDamage(1), self.calcHeal(1)
		enemies = [self.Game.heroes[3-self.ID]] + self.Game.minionsonBoard(3-self.ID)
		friendlies = [self.Game.heroes[self.ID]] + self.Game.minionsonBoard(self.ID)
		self.AOE_Damage(enemies, [damage for obj in enemies])
		self.AOE_Heal(friendlies, [heal for obj in friendlies])
		
		
class WretchedReclaimer(Minion):
	Class, race, name = "Priest", "", "Wretched Reclaimer"
	mana, attack, health = 3, 3, 3
	index = "ULDUM~Priest~Minion~3~3~3~~Wretched Reclaimer~Battlecry"
	requireTarget, effects, description = True, "", "Battlecry: Destroy a friendly minion, then return it to life with full Health"
	name_CN = "卑劣的回收者"
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists(choice)
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			minion = type(target)(self.Game, target.ID)
			targetID, pos = target.ID, target.pos
			self.Game.kill(self, target)
			self.Game.gathertheDead() #强制死亡需要在此插入死亡结算，并让随从离场
			#如果目标之前是第4个(pos=3)，则场上最后只要有3个随从或者以下，就会召唤到最右边。
			#如果目标不在场上或者是第二次生效时已经死亡等被初始化，则position=-2会让新召唤的随从在场上最右边。
			self.summon(minion, position=pos if pos >= 0 else -1)
		return target
		
		
class Psychopomp(Minion):
	Class, race, name = "Priest", "", "Psychopomp"
	mana, attack, health = 4, 3, 1
	index = "ULDUM~Priest~Minion~4~3~1~~Psychopomp~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Summon a random friendly minion that died this game. Give it Reborn"
	name_CN = "接引冥神"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if minions := self.Game.Counters.minionsDiedThisGame[self.ID]:
			minion = numpyChoice(minions)(self.Game, self.ID)
			self.giveEnchant(minion, effGain="Reborn", name=Psychopomp)
			self.summon(minion)
		
		
class HighPriestAmet(Minion):
	Class, race, name = "Priest", "", "High Priest Amet"
	mana, attack, health = 4, 2, 7
	index = "ULDUM~Priest~Minion~4~2~7~~High Priest Amet~Legendary"
	requireTarget, effects, description = False, "", "Whenever you summon a minion, set its Health equal to this minion's"
	name_CN = "高阶祭司阿门特"
	trigBoard = Trig_HighPriestAmet		


class PlagueofDeath(Spell):
	Class, school, name = "Priest", "Shadow", "Plague of Death"
	requireTarget, mana, effects = False, 9, ""
	index = "ULDUM~Priest~Spell~9~Shadow~Plague of Death"
	description = "Silence and destroy all minions"
	name_CN = "死亡之灾祸"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		minions = self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)
		for minion in minions:
			minion.getsSilenced()
		self.Game.kill(self, minions)
		
		
class BazaarBurglary(Quest):
	Class, school, name = "Rogue", "", "Bazaar Burglary"
	requireTarget, mana, effects = False, 1, ""
	index = "ULDUM~Rogue~Spell~1~~Bazaar Burglary~~Quest~Legendary"
	description = "Quest: Add 4 cards from other classes to your hand. Reward: Ancient Blades"
	name_CN = "劫掠集市"
	trigBoard = Trig_BazaarBurglary
	def questEffect(self, game, ID):
		AncientBlades(game, ID).replacePower()

class AncientBlades(Power):
	mana, name, requireTarget = 2, "Ancient Blades", False
	index = "Rogue~Hero Power~2~Ancient Blades"
	description = "Equip a 3/2 Blade with Immune while attacking"
	name_CN = "远古刀锋"
	def effect(self, target=None, choice=0, comment=''):
		self.equipWeapon(MirageBlade(self.Game, self.ID))
		return 0
	

class MirageBlade(Weapon):
	Class, name, description = "Rogue", "Mirage Blade", "Your hero is Immune while attacking"
	mana, attack, durability, effects = 2, 3, 2, ""
	index = "ULDUM~Rogue~Weapon~2~3~2~Mirage Blade~Uncollectible"
	name_CN = "幻象之刃"
	trigBoard = Trig_MirageBlade		


class PharaohCat(Minion):
	Class, race, name = "Rogue", "Beast", "Pharaoh Cat"
	mana, attack, health = 1, 1, 2
	index = "ULDUM~Rogue~Minion~1~1~2~Beast~Pharaoh Cat~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Add a random Reborn minion to your hand"
	name_CN = "法老御猫"
	poolIdentifier = "Reborn Minions"
	@classmethod
	def generatePool(cls, pools):
		minions = []
		for Cost in pools.MinionsofCost.keys():
			minions += [value for key, value in pools.MinionsofCost[Cost].items() if "~Reborn" in key]
		return "Reborn Minions", minions
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.addCardtoHand(numpyChoice(self.rngPool("Reborn Minions")), self.ID)
		
		
class PlagueofMadness(Spell):
	Class, school, name = "Rogue", "Shadow", "Plague of Madness"
	requireTarget, mana, effects = False, 1, ""
	index = "ULDUM~Rogue~Spell~1~Shadow~Plague of Madness"
	description = "Each player equips a 2/2 Knife with Poisonous"
	name_CN = "疯狂之灾祸"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.equipWeapon(PlaguedKnife(self.Game, self.ID))
		self.equipWeapon(PlaguedKnife(self.Game, 3-self.ID))
		

class PlaguedKnife(Weapon):
	Class, name, description = "Rogue", "Plagued Knife", "Poisonous"
	mana, attack, durability, effects = 1, 2, 2, "Poisonous"
	index = "ULDUM~Rogue~Weapon~1~2~2~Plagued Knife~Poisonous~Uncollectible"
	name_CN = "灾祸狂刀"
		
		
class CleverDisguise(Spell):
	Class, school, name = "Rogue", "", "Clever Disguise"
	requireTarget, mana, effects = False, 2, ""
	index = "ULDUM~Rogue~Spell~2~~Clever Disguise"
	description = "Add 2 random spells from another Class to your hand"
	name_CN = "聪明的伪装"
	poolIdentifier = "Druid Spells"
	@classmethod
	def generatePool(cls, pools):
		return [Class+" Spells" for Class in pools.Classes], \
				[[value for key, value in pools.ClassCards[Class].items() if "~Spell~" in key] for Class in pools.Classes]
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		classes = self.rngPool("Classes")[:]
		removefrom(self.Game.heroes[self.ID].Class, classes)
		self.addCardtoHand(numpyChoice(self.rngPool("%s Spells"%numpyChoice(classes)), 2, replace=True), self.ID)
		
		
class WhirlkickMaster(Minion):
	Class, race, name = "Rogue", "", "Whirlkick Master"
	mana, attack, health = 2, 1, 2
	index = "ULDUM~Rogue~Minion~2~1~2~~Whirlkick Master"
	requireTarget, effects, description = False, "", "Whenever you play a Combo card, add a random Combo card to your hand"
	name_CN = "连环腿大师"
	poolIdentifier = "Combo Cards"
	@classmethod
	def generatePool(cls, pools):
		return "Combo Cards", [value for key, value in pools.ClassCards["Rogue"].items() if "~Combo~" in key or key.endswith("~Combo")]
		
	trigBoard = Trig_WhirlkickMaster		


class HookedScimitar(Weapon):
	Class, name, description = "Rogue", "Hooked Scimitar", "Combo: Gain +2 Attack"
	mana, attack, durability, effects = 3, 2, 2, ""
	index = "ULDUM~Rogue~Weapon~3~2~2~Hooked Scimitar~Combo"
	name_CN = "钩镰弯刀"
	
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0: self.giveEnchant(self, 2, 0, name=HookedScimitar)
		
		
class SahketSapper(Minion):
	Class, race, name = "Rogue", "Pirate", "Sahket Sapper"
	mana, attack, health = 4, 4, 4
	index = "ULDUM~Rogue~Minion~4~4~4~Pirate~Sahket Sapper~Deathrattle"
	requireTarget, effects, description = False, "", "Deathrattle: Return a random enemy minion to your opponent's hand"
	name_CN = "萨赫柯特工兵"
	deathrattle = Death_SahketSapper


class BazaarMugger(Minion):
	Class, race, name = "Rogue", "", "Bazaar Mugger"
	mana, attack, health = 5, 3, 5
	index = "ULDUM~Rogue~Minion~5~3~5~~Bazaar Mugger~Rush~Battlecry"
	requireTarget, effects, description = False, "Rush", "Rush. Battlecry: Add a random minion from another class to your hand"
	name_CN = "集市恶痞"
	poolIdentifier = "Druid Minions"
	@classmethod
	def generatePool(cls, pools):
		return list(pools.Classes), [[value for key, value in pools.ClassCards[Class].items() if "~Minion~" in key] for Class in pools.Classes]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		heroClass = self.Game.heroes[self.ID].Class
		classes = [Class for Class in self.rngPool("Classes") if Class != heroClass]
		self.addCardtoHand(numpyChoice(self.rngPool(numpyChoice(classes)+" Minions")), self.ID)
		
		
class ShadowofDeath(Spell):
	Class, school, name = "Rogue", "Shadow", "Shadow of Death"
	requireTarget, mana, effects = True, 4, ""
	index = "ULDUM~Rogue~Spell~4~Shadow~Shadow of Death"
	description = "Choose a minion. Shuffle 3 'Shadows' into your deck that summon a copy when drawn"
	name_CN = "死亡之影"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			typeName = type(target).__name__
			newIndex = "ULDUM~Rogue~4~Spell~Shadow~Casts When Drawn~Summon %s~Uncollectible"%typeName
			subclass = type("Shadow__"+typeName, (Shadow, ),
							{"index": newIndex, "description": "Casts When Drawn. Summon a "+typeName,
							"miniontoSummon": type(target)}
							)
			self.shuffleintoDeck([subclass(self.Game, self.ID) for _ in (0, 1, 2)])
		return target
		

class Shadow(Spell):
	Class, school, name = "Rogue", "", "Shadow"
	requireTarget, mana, effects = False, 4, ""
	index = "ULDUM~Rogue~Spell~4~Shadow~Casts When Drawn~Uncollectible"
	description = "Casts When Drawn. Summon a (0)"
	name_CN = "阴影"
	miniontoSummon = None
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if minion := type(self).miniontoSummon: self.summon(minion(self.Game, self.ID))
		
		
class AnkatheBuried(Minion):
	Class, race, name = "Rogue", "", "Anka, the Buried"
	mana, attack, health = 5, 5, 5
	index = "ULDUM~Rogue~Minion~5~5~5~~Anka, the Buried~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: Change each Deathrattle minion in your hand into a 1/1 that costs (1)"
	name_CN = "被埋葬的安卡"
	#不知道安卡的战吼是否会把手牌中的亡语随从变成新的牌还是只会修改它们的身材
	def effCanTrig(self):
		return any(card.category == "Minion" and card.deathrattles and card != self for card in self.Game.Hand_Deck.hands[self.ID])
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for card in self.Game.Hand_Deck.hands[self.ID][:]:
			if card.category == "Minion" and card.deathrattles:
				self.setStat(card, 1, 1, name=AnkatheBuried)
				ManaMod(card, to=1).applies()
		

class CorrupttheWaters(Quest):
	Class, school, name = "Shaman", "", "Corrupt the Waters"
	requireTarget, mana, effects = False, 1, ""
	index = "ULDUM~Shaman~Spell~1~~Corrupt the Waters~~Quest~Legendary"
	description = "Quest: Play 6 Battlecry cards. Reward: Heart of Vir'naal"
	name_CN = "腐化水源"
	trigBoard = Trig_CorrupttheWaters
	def questEffect(self, game, ID):
		HeartofVirnaal(game, ID).replacePower()

class HeartofVirnaal(Power):
	mana, name, requireTarget = 2, "Heart of Vir'naal", False
	index = "Shaman~Hero Power~2~Heart of Vir'naal"
	description = "Your Battlecries trigger twice this turn"
	name_CN = "维尔纳尔之心"
	def effect(self, target=None, choice=0, comment=''):
		self.Game.effects[self.ID]["Battlecry x2"] += 1
		self.Game.turnEndTrigger.append(HeartofVirnaal_Effect(self.Game, self.ID))
		return 0


class TotemicSurge(Spell):
	Class, school, name = "Shaman", "Nature", "Totemic Surge"
	requireTarget, mana, effects = False, 0, ""
	index = "ULDUM~Shaman~Spell~0~Nature~Totemic Surge"
	description = "Give your Totems +2 Attack"
	name_CN = "图腾潮涌"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.AOE_GiveEnchant(self.Game.minionsonBoard(self.ID, race="Totem"), 2, 2, name=TotemicSurge)
		
		
class EVILTotem(Minion):
	Class, race, name = "Shaman", "Totem", "EVIL Totem"
	mana, attack, health = 2, 0, 2
	index = "ULDUM~Shaman~Minion~2~0~2~Totem~EVIL Totem"
	requireTarget, effects, description = False, "", "At the end of your turn, add a Lackey to your hand"
	name_CN = "怪盗图腾"
	trigBoard = Trig_EVILTotem		


class SandstormElemental(Minion):
	Class, race, name = "Shaman", "Elemental", "Sandstorm Elemental"
	mana, attack, health = 2, 2, 2
	index = "ULDUM~Shaman~Minion~2~2~2~Elemental~Sandstorm Elemental~Overload~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Deal 1 damage to all enemy minions. Overload: (1)"
	name_CN = "沙暴元素"
	overload = 1
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		targets = self.Game.minionsonBoard(3-self.ID)
		self.AOE_Damage(targets, [1 for minion in targets])
		
		
class PlagueofMurlocs(Spell):
	Class, school, name = "Shaman", "", "Plague of Murlocs"
	requireTarget, mana, effects = False, 3, ""
	index = "ULDUM~Shaman~Spell~3~~Plague of Murlocs"
	description = "Transform all minions into random Murlocs"
	name_CN = "鱼人之灾祸"
	poolIdentifier = "Murlocs"
	@classmethod
	def generatePool(cls, pools):
		return "Murlocs", list(pools.MinionswithRace["Murloc"].values())
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		game = self.Game
		minions = game.minionsonBoard(1) + game.minionsonBoard(2)
		murlocs = tuple(numpyChoice(self.rngPool("Murlocs"), len(minions), replace=True))
		for minion, murloc in zip(minions, murlocs):
			self.transform(minion, murloc(game, minion.ID))
		
		
class WeaponizedWasp(Minion):
	Class, race, name = "Shaman", "Beast", "Weaponized Wasp"
	mana, attack, health = 3, 3, 3
	index = "ULDUM~Shaman~Minion~3~3~3~Beast~Weaponized Wasp~Battlecry"
	requireTarget, effects, description = True, "", "Battlecry: If you control a Lackey, deal 3 damage"
	name_CN = "武装黄蜂"
	def needTarget(self, choice=0):
		return any(minion.name.endswith("Lackey") for minion in self.Game.minionsonBoard(self.ID))
		
	def effCanTrig(self):
		self.effectViable =  self.targetExists() \
							and any(minion.name.endswith("Lackey") for minion in self.Game.minionsonBoard(self.ID))
							
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and any(minion.name.endswith("Lackey") for minion in self.Game.minionsonBoard(self.ID)):
			self.dealsDamage(target, 3)
		return target
		
		
class SplittingAxe(Weapon):
	Class, name, description = "Shaman", "Splitting Axe", "Battlecry: Summon copies of your Totems"
	mana, attack, durability, effects = 4, 3, 2, ""
	index = "ULDUM~Shaman~Weapon~4~3~2~Splitting Axe~Battlecry"
	name_CN = "分裂战斧"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for minion in self.Game.minionsonBoard(self.ID, race="Totem"):
			self.summon(minion.selfCopy(minion.ID, self), position=minion.pos+1)
		
		
class Vessina(Minion):
	Class, race, name = "Shaman", "", "Vessina"
	mana, attack, health = 4, 2, 6
	index = "ULDUM~Shaman~Minion~4~2~6~~Vessina~Legendary"
	requireTarget, effects, description = False, "", "While you're Overloaded, your other minions have +2 Attack"
	name_CN = "维西纳"
	aura = Aura_Vessina
	
	
class Earthquake(Spell):
	Class, school, name = "Shaman", "Nature", "Earthquake"
	requireTarget, mana, effects = False, 7, ""
	index = "ULDUM~Shaman~Spell~7~Nature~Earthquake"
	description = "Deal 5 damage to all minions, then deal 2 damage to all minions"
	name_CN = "地震术"
	def text(self): return "%d, %d"%(self.calcDamage(5), self.calcDamage(2))
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = self.calcDamage(5)
		targets = self.Game.minionsonBoard(self.ID) + self.Game.minionsonBoard(3-self.ID)
		self.AOE_Damage(targets, [damage]*len(targets))
		#地震术在第一次AOE后会让所有随从结算死亡事件，然后再次对全场随从打2.
		self.Game.gathertheDead()
		#假设法强随从如果在这个过程中死亡并被移除，则法强等数值会随之变化。
		damage = self.calcDamage(2)
		targets = self.Game.minionsonBoard(self.ID) + self.Game.minionsonBoard(3-self.ID)
		self.AOE_Damage(targets, [damage]*len(targets))
		
		
class MoguFleshshaper(Minion):
	Class, race, name = "Shaman", "", "Mogu Fleshshaper"
	mana, attack, health = 9, 3, 4
	index = "ULDUM~Shaman~Minion~9~3~4~~Mogu Fleshshaper~Rush"
	requireTarget, effects, description = False, "Rush", "Rush. Costs (1) less for each minion on the battlefield"
	name_CN = "魔古血肉塑造者"
	trigHand = Trig_MoguFleshshaper
	def selfManaChange(self):
		if self.inHand:
			num = len(self.Game.minionsonBoard(1)) + len(self.Game.minionsonBoard(2))
			self.mana -= num
			self.mana = max(0, self.mana)
			

class PlagueofFlames(Spell):
	Class, school, name = "Warlock", "Fire", "Plague of Flames"
	requireTarget, mana, effects = False, 1, ""
	index = "ULDUM~Warlock~Spell~1~Fire~Plague of Flames"
	description = "Destroy all your minions. For each one, destroy a random enemy minion"
	name_CN = "火焰之灾祸"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		num = len((ownMinions := self.Game.minionsonBoard(self.ID)))
		self.Game.kill(self, ownMinions)
		if num > 0 and (enemyMinions := self.Game.minionsonBoard(3-self.ID)):
			minions = numpyChoice(enemyMinions, min(num, len(enemyMinions)), replace=False)
			self.Game.kill(self, minions)
		
		
class SinisterDeal(Spell):
	Class, school, name = "Warlock", "", "Sinister Deal"
	requireTarget, mana, effects = False, 1, ""
	index = "ULDUM~Warlock~Spell~1~~Sinister Deal"
	description = "Discover a Lackey"
	name_CN = "邪恶交易"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverandGenerate(SinisterDeal, comment, poolFunc=lambda: Lackeys)
		
		
class SupremeArchaeology(Quest):
	Class, school, name = "Warlock", "", "Supreme Archaeology"
	requireTarget, mana, effects = False, 1, ""
	index = "ULDUM~Warlock~Spell~1~~Supreme Archaeology~~Quest~Legendary"
	description = "Quest: Draw 20 cards. Reward: Tome of Origination"
	name_CN = "最最伟大的考古学"
	trigBoard = Trig_SupremeArchaeology
	def questEffect(self, game, ID):
		TomeofOrigination(game, ID).replacePower()

class TomeofOrigination(Power):
	mana, name, requireTarget = 2, "Tome of Origination", False
	index = "Warlock~Hero Power~2~Tome of Origination"
	description = "Draw a card. It costs (0)"
	name_CN = "源生魔典"
	def effect(self, target=None, choice=0, comment=''):
		card, mana, entersHand = self.Game.Hand_Deck.drawCard(self.ID)
		if entersHand:
			self.Game.sendSignal("CardDrawnfromHeroPower", self.ID, self, card, mana, "")
			ManaMod(card, to=0).applies()
		return 0
		
		
class ExpiredMerchant(Minion):
	Class, race, name = "Warlock", "", "Expired Merchant"
	mana, attack, health = 2, 2, 1
	index = "ULDUM~Warlock~Minion~2~2~1~~Expired Merchant~Battlecry~Deathrattle"
	requireTarget, effects, description = False, "", "Battlecry: Discard your highest Cost card. Deathrattle: Add 2 copies of it to your hand"
	name_CN = "过期货物专卖商"
	deathrattle = Death_ExpiredMerchant
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if indices := pickHighestCostIndices(self.Game.Hand_Deck.hands[self.ID]):
			card = self.Game.Hand_Deck.discard(self.ID, numpyChoice(indices))
			for trig in self.deathrattles:
				if isinstance(trig, Death_ExpiredMerchant): trig.savedObj = type(card)
		

class EVILRecruiter(Minion):
	Class, race, name = "Warlock", "", "EVIL Recruiter"
	mana, attack, health = 3, 3, 3
	index = "ULDUM~Warlock~Minion~3~3~3~~EVIL Recruiter~Battlecry"
	requireTarget, effects, description = True, "", "Battlecry: Destroy a friendly Lackey to summon a 5/5 Demon"
	name_CN = "怪盗征募官"
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.ID == self.ID and "Lackey" in target.name and "~Uncollectible" in target.index and target.onBoard
		
	def effCanTrig(self): #Friendly minions are always selectable.
		self.effectViable = False
		for minion in self.Game.minionsonBoard(self.ID):
			if minion.name.endswith("Lackey"):
				self.effectViable = True
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			#假设消灭跟班之后会进行强制死亡结算，把跟班移除之后才召唤
			#假设召唤的恶魔是在EVIL Recruiter的右边，而非死亡的跟班的原有位置
			self.Game.kill(self, target)
			self.Game.gathertheDead()
			self.summon(EVILDemon(self.Game, self.ID))
		return target
		

class EVILDemon(Minion):
	Class, race, name = "Warlock", "Demon", "EVIL Demon"
	mana, attack, health = 5, 5, 5
	index = "ULDUM~Warlock~Minion~5~5~5~Demon~EVIL Demon~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "怪盗恶魔"
	
	
class NefersetThrasher(Minion):
	Class, race, name = "Warlock", "", "Neferset Thrasher"
	mana, attack, health = 3, 4, 5
	index = "ULDUM~Warlock~Minion~3~4~5~~Neferset Thrasher"
	requireTarget, effects, description = False, "", "Whenever this attacks, deal 3 damage to your hero"
	name_CN = "尼斐塞特鞭笞者"
	trigBoard = Trig_NefersetThrasher		


class Impbalming(Spell):
	Class, school, name = "Warlock", "Fel", "Impbalming"
	requireTarget, mana, effects = True, 4, ""
	index = "ULDUM~Warlock~Spell~4~Fel~Impbalming"
	description = "Destroy a minion. Shuffle 3 Worthless Imps into your deck"
	name_CN = "小鬼油膏"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.Game.kill(self, target)
			self.shuffleintoDeck([WorthlessImp_Uldum(self.Game, self.ID) for _ in (0, 1, 2)])
		return target
		

class WorthlessImp_Uldum(Minion):
	Class, race, name = "Warlock", "Demon", "Worthless Imp"
	mana, attack, health = 1, 1, 1
	index = "ULDUM~Warlock~Minion~1~1~1~Demon~Worthless Imp~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "游荡小鬼"
	
	
class DiseasedVulture(Minion):
	Class, race, name = "Warlock", "Beast", "Diseased Vulture"
	mana, attack, health = 4, 3, 5
	index = "ULDUM~Warlock~Minion~4~3~5~Beast~Diseased Vulture"
	requireTarget, effects, description = False, "", "After your hero takes damage on your turn, summon a random 3-Cost minion"
	name_CN = "染病的兀鹫"
	trigBoard = Trig_DiseasedVulture
	poolIdentifier = "3-Cost Minions to Summon"
	@classmethod
	def generatePool(cls, pools):
		return "3-Cost Minions to Summon", list(pools.MinionsofCost[3].values())
		


class Riftcleaver(Minion):
	Class, race, name = "Warlock", "Demon", "Riftcleaver"
	mana, attack, health = 6, 7, 5
	index = "ULDUM~Warlock~Minion~6~7~5~Demon~Riftcleaver~Battlecry"
	requireTarget, effects, description = True, "", "Battlecry: Destroy a minion. Your hero takes damage equal to its health"
	name_CN = "裂隙屠夫"
	
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target != self and target.onBoard
		#不知道连续触发战吼时，第二次是否还会让玩家受到伤害
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and not target.dead == False:
			damage, target.dead = max(0, target.health), True
			#不知道这个对于英雄的伤害有无伤害来源。假设没有，和抽牌疲劳伤害类似
			dmgTaker = self.Game.scapegoat4(self.Game.heroes[self.ID])
			dmgTaker.takesDamage(None, damage, damageType="Ability") #假设伤害没有来源
		return target
		
#光环生效时跟班变成白字的4/4，可以在之后被buff，reset和光环buff。返回手牌中时也会是4/4的身材。沉默之后仍为4/4
#无面操纵者复制对方的4/4跟班也会得到4/4的跟班
#光环生效时的非光环buff会消失，然后成为4/4白字


#光环生效时跟班变成白字的4/4，可以在之后被buff，reset和光环buff。返回手牌中时也会是4/4的身材。沉默之后仍为4/4
#无面操纵者复制对方的4/4跟班也会得到4/4的跟班
#光环生效时的非光环buff会消失，然后成为4/4白字
class DarkPharaohTekahn(Minion):
	Class, race, name = "Warlock", "", "Dark Pharaoh Tekahn"
	mana, attack, health = 5, 4, 4
	index = "ULDUM~Warlock~Minion~5~4~4~~Dark Pharaoh Tekahn~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: For the rest of the game, your Lackeys are 4/4"
	name_CN = "黑暗法老塔卡恒"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		YourLackeysareAlways44(self.Game, self.ID).auraAppears()
		

class HacktheSystem(Quest):
	Class, school, name = "Warrior", "", "Hack the System"
	requireTarget, mana, effects = False, 1, ""
	index = "ULDUM~Warrior~Spell~1~~Hack the System~~Quest~Legendary"
	description = "Quest: Attack 5 times with your hero. Reward: Anraphet's Core"
	name_CN = "侵入系统"
	trigBoard = Trig_HacktheSystem
	def questEffect(self, game, ID):
		AnraphetsCore(game, ID).replacePower()

class AnraphetsCore(Power):
	mana, name, requireTarget = 2, "Anraphet's Core", False
	index = "Warrior~Hero Power~2~Anraphet's Core"
	description = "Summon a 4/3 Golem. After your hero attacks, refresh this"
	name_CN = "安拉斐特之核"
	trigBoard = Trig_AnraphetsCore		
	def available(self, choice=0):
		return not self.chancesUsedUp() and self.Game.space(self.ID)
		
	def effect(self, target=None, choice=0, comment=''):
		self.summon(StoneGolem(self.Game, self.ID))
		return 0
		

class StoneGolem(Minion):
	Class, race, name = "Warrior", "", "Stone Golem"
	mana, attack, health = 3, 4, 3
	index = "ULDUM~Warrior~Minion~3~4~3~~Stone Golem~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "石头魔像"
	
	
class IntotheFray(Spell):
	Class, school, name = "Warrior", "", "Into the Fray"
	requireTarget, mana, effects = False, 1, ""
	index = "ULDUM~Warrior~Spell~1~~Into the Fray"
	description = "Give all Taunt minions in your hand +2/+2"
	name_CN = "投入战斗"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.AOE_GiveEnchant([card for card in self.Game.Hand_Deck.hands[self.ID] if card.category == "Minion" and card.effects["Taunt"] > 0],
							2, 2, name=IntotheFray, add2EventinGUI=False)
		
		
class FrightenedFlunky(Minion):
	Class, race, name = "Warrior", "", "Frightened Flunky"
	mana, attack, health = 2, 2, 2
	index = "ULDUM~Warrior~Minion~2~2~2~~Frightened Flunky~Taunt~Battlecry"
	requireTarget, effects, description = False, "Taunt", "Taunt. Battlecry: Discover a Taunt minion"
	name_CN = "惊恐的仆从"
	poolIdentifier = "Taunt Minions as Warrior"
	@classmethod
	def generatePool(cls, pools):
		classCards = {s : [value for key, value in pools.ClassCards[s].items() if "~Taunt" in key] for s in pools.Classes}
		classCards["Neutral"] = [value for key, value in pools.NeutralCards.items() if "~Taunt" in key]
		return ["Taunt Minions as %s"%Class for Class in pools.Classes], \
				[classCards[Class]+classCards["Neutral"] for Class in pools.Classes]
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverandGenerate(FrightenedFlunky, comment, poolFunc=lambda : self.rngPool("Taunt Minions as "+classforDiscover(self)))
		
		
class BloodswornMercenary(Minion):
	Class, race, name = "Warrior", "", "Bloodsworn Mercenary"
	mana, attack, health = 3, 2, 2
	index = "ULDUM~Warrior~Minion~3~2~2~~Bloodsworn Mercenary~Battlecry"
	requireTarget, effects, description = True, "", "Battlecry: Choose a damaged friendly minion. Summon a copy of it"
	name_CN = "血誓雇佣兵"
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.ID == self.ID and target != self and target.onBoard and target.health < target.health_max
		
	def effCanTrig(self):
		self.effectViable = any(minion.dmgTaken > 0 for minion in self.Game.minionsonBoard(self.ID))
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			Copy = target.selfCopy(self.ID, self) if target.onBoard else type(target)(self.Game, self.ID)
			self.summon(Copy)
		return target
		
		
class LivewireLance(Weapon):
	Class, name, description = "Warrior", "Livewire Lance", "After your hero attacks, add a Lackey to your hand"
	mana, attack, durability, effects = 3, 2, 2, ""
	index = "ULDUM~Warrior~Weapon~3~2~2~Livewire Lance"
	name_CN = "电缆长枪"
	trigBoard = Trig_LivewireLance		


class RestlessMummy(Minion):
	Class, race, name = "Warrior", "", "Restless Mummy"
	mana, attack, health = 4, 3, 2
	index = "ULDUM~Warrior~Minion~4~3~2~~Restless Mummy~Rush~Reborn"
	requireTarget, effects, description = False, "Rush,Reborn", "Rush, Reborn"
	name_CN = "焦躁的木乃伊"
	
	
class PlagueofWrath(Spell):
	Class, school, name = "Warrior", "", "Plague of Wrath"
	requireTarget, mana, effects = False, 5, ""
	index = "ULDUM~Warrior~Spell~5~~Plague of Wrath"
	description = "Destroy all damaged minions"
	name_CN = "愤怒之灾祸"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.kill(self, [minion for minion in self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2) if minion.health < minion.health_max])
		
		
class Armagedillo(Minion):
	Class, race, name = "Warrior", "Beast", "Armagedillo"
	mana, attack, health = 6, 4, 7
	index = "ULDUM~Warrior~Minion~6~4~7~Beast~Armagedillo~Taunt~Legendary"
	requireTarget, effects, description = False, "Taunt", "Taunt. At the end of your turn, give all Taunt minions in your hand +2/+2"
	name_CN = "铠硕鼠"
	trigBoard = Trig_Armagedillo		


class ArmoredGoon(Minion):
	Class, race, name = "Warrior", "", "Armored Goon"
	mana, attack, health = 6, 6, 7
	index = "ULDUM~Warrior~Minion~6~6~7~~Armored Goon"
	requireTarget, effects, description = False, "", "Whenever your hero attacks, gain 5 Armor"
	name_CN = "重甲暴徒"
	trigBoard = Trig_ArmoredGoon		


class TombWarden(Minion):
	Class, race, name = "Warrior", "Mech", "Tomb Warden"
	mana, attack, health = 8, 3, 6
	index = "ULDUM~Warrior~Minion~8~3~6~Mech~Tomb Warden~Taunt~Battlecry"
	requireTarget, effects, description = False, "Taunt", "Taunt. Battlecry: Summon a copy of this minion"
	name_CN = "陵墓守望者"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		minion = self.selfCopy(self.ID, self) if self.onBoard else type(self)(self.Game, self.ID)
		self.summon(minion)
		

"""Game TrigEffects and game auras"""
class HeartofVirnaal_Effect(TrigEffect):
	card, trigType = HeartofVirnaal, "TurnEnd&OnlyKeepOne"
	def trigEffect(self): self.Game.effects[self.ID]["Battlecry x2"] -= 1


class YourLackeysareAlways44(GameAura_AlwaysOn):
	card = DarkPharaohTekahn
	def __init__(self, Game, ID):
		super().__init__(None, (), )
		self.Game, self.ID = Game, ID
		self.signals, self.receivers = ["MinionAppears", "CardEntersHand"], []

	def applicable(self, target):
		return target.ID == self.ID and target.name.endswith("Lackey")

	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		if signal[0] == 'M':  # "MinionAppears" #只有随从在从其他位置进入场上的时候可以进行修改，而从休眠中苏醒或者控制权改变不会触发改变
			return comment and self.applicable(subject)
		elif signal[0] == 'C':
			return self.applicable(target[0])  # The target here is a holder

	# else: #signal == "CardShuffled"
	#	if isinstance(target, (list, ndarray)):
	#		for card in target:
	#			self.applicable(card)
	#	else: #Shuffling a single card
	#		return self.applicable(target)

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if signal == "MinionAppears":
			self.applies(subject)
		elif signal == "CardEntersHand":
			self.applies(target[0])

	# else: #signal == "CardShuffled"
	#	self.applies(target)

	def applies(self, subject):
		if self.applicable(subject) and (subject.attack_0 != 4 or subject.health_0 != 4):
			subject.attack_0, subject.health_0 = 4, 4  # 需要先把随从的白字身材变为4/4
			self.card.setStat(subject, 4, 4, name=DarkPharaohTekahn)

	# 暂时假设跟班被对方控制后仍为4/4
	def auraAppears(self):
		game = self.Game
		if not any(isinstance(obj, YourLackeysareAlways44) for obj in game.trigAuras[self.ID]):
			game.trigAuras[self.ID].append(self)
			for card in game.minionsonBoard(self.ID) + game.Hand_Deck.hands[self.ID] + game.Hand_Deck.decks[self.ID]:
				self.applies(card)
			for sig in self.signals:
				try: game.trigsBoard[self.ID][sig].insert(0, self)  # 假设这种光环总是添加到最前面，保证它可以在其他的普通光环生效之前作用
				except: game.trigsBoard[self.ID][sig] = [self]


Uldum_Cards = [
		#Neutral
		BeamingSidekick, JarDealer, MoguCultist, HighkeeperRa, Murmy, BugCollector, Locust, DwarvenArchaeologist,
		Fishflinger, InjuredTolvir, KoboldSandtrooper, NefersetRitualist, QuestingExplorer, QuicksandElemental, SerpentEgg,
		SeaSerpent, SpittingCamel, TempleBerserker, Vilefiend, ZephrystheGreat, Candletaker, DesertHare, GenerousMummy,
		GoldenScarab, HistoryBuff, InfestedGoblin, Scarab_Uldum, MischiefMaker, VulperaScoundrel, BoneWraith, BodyWrapper,
		ConjuredMirage, SunstruckHenchman, FacelessLurker, DesertObelisk, MortuaryMachine, PhalanxCommander,
		WastelandAssassin, BlatantDecoy, KhartutDefender, Siamat, WastelandScorpid, WrappedGolem, Octosari, PitCrocolisk,
		AnubisathWarbringer, ColossusoftheMoon, KingPhaoris, LivingMonument,
		#Druid
		UntappedPotential, WorthyExpedition, CrystalMerchant, BEEEES, Bee_Uldum, GardenGnome, Treant_Uldum,
		AnubisathDefender, ElisetheEnlightened, OasisSurger, HiddenOasis, BefriendtheAncient, DrinktheWater, VirnaalAncient,
		Overflow,
		#Hunter
		UnsealtheVault, PressurePlate, DesertSpear, HuntersPack, HyenaAlpha, Hyena_Uldum, RamkahenWildtamer, SwarmofLocusts,
		ScarletWebweaver, WildBloodstinger, DinotamerBrann, KingKrush_Uldum,
		#Mage
		RaidtheSkyTemple, AncientMysteries, FlameWard, CloudPrince, ArcaneFlakmage, DuneSculptor, NagaSandWitch,
		TortollanPilgrim, RenotheRelicologist, PuzzleBoxofYoggSaron,
		#Paladin
		MakingMummies, BrazenZealot, MicroMummy, SandwaspQueen, Sandwasp, SirFinleyoftheSands, Subdue, SalhetsPride,
		AncestralGuardian, PharaohsBlessing, TiptheScales,
		#Priest
		ActivatetheObelisk, EmbalmingRitual, Penance, SandhoofWaterbearer, Grandmummy, HolyRipple, WretchedReclaimer,
		Psychopomp, HighPriestAmet, PlagueofDeath,
		#Rogue
		BazaarBurglary, MirageBlade, PharaohCat, PlagueofMadness, PlaguedKnife, CleverDisguise, WhirlkickMaster,
		HookedScimitar, SahketSapper, BazaarMugger, ShadowofDeath, Shadow, AnkatheBuried,
		#Shaman
		CorrupttheWaters, TotemicSurge, EVILTotem, SandstormElemental, PlagueofMurlocs, WeaponizedWasp, SplittingAxe,
		Vessina, Earthquake, MoguFleshshaper,
		#Warlock
		PlagueofFlames, SinisterDeal, SupremeArchaeology, ExpiredMerchant, EVILRecruiter, EVILDemon, NefersetThrasher,
		Impbalming, WorthlessImp_Uldum, DiseasedVulture, Riftcleaver, DarkPharaohTekahn,
		#Warrior
		HacktheSystem, StoneGolem, IntotheFray, FrightenedFlunky, BloodswornMercenary, LivewireLance, RestlessMummy,
		PlagueofWrath, Armagedillo, ArmoredGoon, TombWarden,
]

Uldum_Cards_Collectible = [
		#Neutral
		BeamingSidekick, JarDealer, MoguCultist, Murmy, BugCollector, DwarvenArchaeologist, Fishflinger, InjuredTolvir,
		KoboldSandtrooper, NefersetRitualist, QuestingExplorer, QuicksandElemental, SerpentEgg, SpittingCamel,
		TempleBerserker, Vilefiend, ZephrystheGreat, Candletaker, DesertHare, GenerousMummy, GoldenScarab, HistoryBuff,
		InfestedGoblin, MischiefMaker, VulperaScoundrel, BoneWraith, BodyWrapper, ConjuredMirage, SunstruckHenchman,
		FacelessLurker, DesertObelisk, MortuaryMachine, PhalanxCommander, WastelandAssassin, BlatantDecoy, KhartutDefender,
		Siamat, WastelandScorpid, WrappedGolem, Octosari, PitCrocolisk, AnubisathWarbringer, ColossusoftheMoon, KingPhaoris,
		LivingMonument,
		#Druid
		UntappedPotential, WorthyExpedition, CrystalMerchant, BEEEES, GardenGnome, AnubisathDefender, ElisetheEnlightened,
		OasisSurger, HiddenOasis, Overflow,
		#Hunter
		UnsealtheVault, PressurePlate, DesertSpear, HuntersPack, HyenaAlpha, RamkahenWildtamer, SwarmofLocusts,
		ScarletWebweaver, WildBloodstinger, DinotamerBrann,
		#Mage
		RaidtheSkyTemple, AncientMysteries, FlameWard, CloudPrince, ArcaneFlakmage, DuneSculptor, NagaSandWitch,
		TortollanPilgrim, RenotheRelicologist, PuzzleBoxofYoggSaron,
		#Paladin
		MakingMummies, BrazenZealot, MicroMummy, SandwaspQueen, SirFinleyoftheSands, Subdue, SalhetsPride, AncestralGuardian,
		PharaohsBlessing, TiptheScales,
		#Priest
		ActivatetheObelisk, EmbalmingRitual, Penance, SandhoofWaterbearer, Grandmummy, HolyRipple, WretchedReclaimer,
		Psychopomp, HighPriestAmet, PlagueofDeath,
		#Rogue
		BazaarBurglary, PharaohCat, PlagueofMadness, CleverDisguise, WhirlkickMaster, HookedScimitar, SahketSapper,
		BazaarMugger, ShadowofDeath, AnkatheBuried,
		#Shaman
		CorrupttheWaters, TotemicSurge, EVILTotem, SandstormElemental, PlagueofMurlocs, WeaponizedWasp, SplittingAxe,
		Vessina, Earthquake, MoguFleshshaper,
		#Warlock
		PlagueofFlames, SinisterDeal, SupremeArchaeology, ExpiredMerchant, EVILRecruiter, NefersetThrasher, Impbalming,
		DiseasedVulture, Riftcleaver, DarkPharaohTekahn,
		#Warrior
		HacktheSystem, IntotheFray, FrightenedFlunky, BloodswornMercenary, LivewireLance, RestlessMummy, PlagueofWrath,
		Armagedillo, ArmoredGoon, TombWarden,
]


TrigsDeaths_Uldum = {Death_JarDealer: (JarDealer, "Deathrattle: Add a random 1-cost minion to your hand"),
					Death_KoboldSandtrooper: (KoboldSandtrooper, "Deathrattle: Deal 3 damage to the enemy hero"),
					Death_SerpentEgg: (SerpentEgg, "Deathrattle: Summon a 3/4 Sea Serpent"),
					Death_InfestedGoblin: (InfestedGoblin, "Deathrattle: Add two 1/1 Scarabs with Taunt to your hand"),
					Death_BlatantDecoy: (BlatantDecoy, "Deathrattle: Each player summons the lowest Cost minion from their hand"),
					Death_KhartutDefender: (KhartutDefender, "Deathrattle: Restore 4 Health to your hero"),
					Death_Octosari: (Octosari, "Deathrattle: Draw 8 cards"),
					Death_AnubisathWarbringer: (AnubisathWarbringer, "Deathrattle: Give all minions in your hand +3/+3"),
					Death_SalhetsPride: (SalhetsPride, "Deathrattle: Draw two 1-Health minions from your deck"),
					Death_Grandmummy: (Grandmummy, "Deathrattle: Give a random friendly minion +1/+1"),
					Death_SahketSapper: (SahketSapper, "Deathrattle: Return a random enemy minion to your opponent's hand"),
					Death_ExpiredMerchant: (ExpiredMerchant, "Deathrattle: Add 2 copies of discarded cards to your hand"),
					}