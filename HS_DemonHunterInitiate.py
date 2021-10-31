from Parts_ConstsFuncsImports import numpyChoice
from Parts_CardTypes import *
from Parts_TrigsAuras import *

from HS_AcrossPacks import IllidariInitiate


"""Deathrattles"""
class Death_UrzulHorror(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.addCardtoHand(LostSoul, self.keeper.ID)

"""Triggers"""
class Trig_Battlefiend(TrigBoard):
	signals = ("HeroAttackedMinion", "HeroAttackedHero", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject == self.keeper.Game.heroes[self.keeper.ID]

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.giveEnchant(self.keeper, statEnchant=Enchantment_Cumulative(1, 0, name=Battlefiend))
		

class Trig_AltruistheOutcast(TrigBoard):
	signals = ("MinionBeenPlayed", "SpellBeenPlayed", "WeaponBeenPlayed", "HeroCardBeenPlayed", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject.ID == self.keeper.ID and subject != self.keeper and (comment == -1 or comment == 0)

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		targets = [self.keeper.Game.heroes[3-self.keeper.ID]] + self.keeper.Game.minionsonBoard(3-self.keeper.ID)
		self.keeper.AOE_Damage(targets, [1] * len(targets))
		
		
class Trig_EyeBeam(TrigHand):
	signals = ("CardLeavesHand", "CardEntersHand", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.inHand and (target[0] if "E" in signal else target).ID == self.keeper.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.Game.Manas.calcMana_Single(self.keeper)
		
		
class Trig_WrathscaleNaga(TrigBoard):
	signals = ("MinionDied", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and target != self.keeper and target.ID == self.keeper.ID #Technically, minion has to disappear before dies. But just in case.

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if targets := self.keeper.Game.charsAlive(3-self.keeper.ID):
			self.keeper.dealsDamage(numpyChoice(targets), 1)
			

class Trig_WrathspikeBrute(TrigBoard):
	signals = ("MinionAttackedMinion", "HeroAttackedMinion", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and target == self.keeper

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		targets = [self.keeper.Game.heroes[3-self.keeper.ID]] + self.keeper.Game.minionsonBoard(3-self.keeper.ID)
		self.keeper.AOE_Damage(targets, [1] * len(targets))
		

class Trig_HulkingOverfiend(TrigBoard):
	signals = ("MinionAttackedMinion", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject == self.keeper and self.keeper.health > 0 \
				and self.keeper.dead == False and (target.health < 1 or target.dead == True)

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.attChances_extra += 1
		
		
class Trig_Nethrandamus(TrigHand):
	signals = ("MinionDies", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.inHand and target.ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.progress += 1
		
		
class Blur(Spell):
	Class, school, name = "Demon Hunter", "", "Blur"
	requireTarget, mana, effects = False, 0, ""
	index = "DEMON_HUNTER_INITIATE~Demon Hunter~Spell~0~~Blur"
	description = "Your hero can't take damage this turn"
	name_CN = "疾影"
	#不知道与博尔碎盾的结算是如何进行的。
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		Blur_Effect(self.Game, self.ID).connect()


class TwinSlice(Spell):
	Class, school, name = "Demon Hunter", "", "Twin Slice"
	requireTarget, mana, effects = False, 1, ""
	index = "DEMON_HUNTER_INITIATE~Demon Hunter~Spell~1~~Twin Slice"
	description = "Give your hero +2 Attack this turn. Add 'Second Slice' to your hand"
	name_CN = "双刃斩击"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.giveHeroAttackArmor(self.ID, attGain=2, name=TwinSlice)
		self.addCardtoHand(SecondSlice, self.ID)
		

class SecondSlice(Spell):
	Class, school, name = "Demon Hunter", "", "Second Slice"
	requireTarget, mana, effects = False, 1, ""
	index = "DEMON_HUNTER_INITIATE~Demon Hunter~Spell~1~~Second Slice~Uncollectible"
	description = "Give your hero +2 Attack this turn"
	name_CN = "二次斩击"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.giveHeroAttackArmor(self.ID, attGain=2, name=SecondSlice)
		
		
class Battlefiend(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Battlefiend"
	mana, attack, health = 1, 1, 2
	index = "DEMON_HUNTER_INITIATE~Demon Hunter~Minion~1~1~2~Demon~Battlefiend"
	requireTarget, effects, description = False, "", "After your hero attacks, gain +1 Attack"
	name_CN = "战斗邪犬"
	trigBoard = Trig_Battlefiend		


class ConsumeMagic(Spell):
	Class, school, name = "Demon Hunter", "Shadow", "Consume Magic"
	requireTarget, mana, effects = True, 1, ""
	index = "DEMON_HUNTER_INITIATE~Demon Hunter~Spell~1~Shadow~Consume Magic~Outcast"
	description = "Silence an enemy minion. Outcast: Draw a card"
	name_CN = "吞噬魔法"
	def available(self):
		return self.selectableEnemyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.ID != self.ID and target.onBoard
		
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.outcastcanTrig(self)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.getsSilenced()
			if posinHand == 0 or posinHand == -1:
				self.Game.Hand_Deck.drawCard(self.ID)
		return target
		
		
class ManaBurn(Spell):
	Class, school, name = "Demon Hunter", "Fel", "Mana Burn"
	requireTarget, mana, effects = False, 1, ""
	index = "DEMON_HUNTER_INITIATE~Demon Hunter~Spell~1~Fel~Mana Burn"
	description = "Your opponent has 2 fewer Mana Crystals next turn"
	name_CN = "法力燃烧"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.Manas.manas_withheld[3-self.ID] += 2
		ManaBurn_Effect(self.Game, 3-self.ID).connect()
		

class UrzulHorror(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Ur'zul Horror"
	mana, attack, health = 1, 2, 1
	index = "DEMON_HUNTER_INITIATE~Demon Hunter~Minion~1~2~1~Demon~Ur'zul Horror~Deathrattle"
	requireTarget, effects, description = False, "", "Deathrattle: Add a 2/1 Lost Soul to your hand"
	name_CN = "乌祖尔恐魔"
	deathrattle = Death_UrzulHorror

class LostSoul(Minion):
	Class, race, name = "Demon Hunter", "", "Lost Soul"
	mana, attack, health = 1, 2, 1
	index = "DEMON_HUNTER_INITIATE~Demon Hunter~Minion~1~2~1~~Lost Soul~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "迷失之魂"
	
	
class BladeDance(Spell):
	Class, school, name = "Demon Hunter", "", "Blade Dance"
	requireTarget, mana, effects = False, 3, ""
	index = "DEMON_HUNTER_INITIATE~Demon Hunter~Spell~3~~Blade Dance"
	description = "Deal damage equal to your hero's Attack to 3 random enemy minions"
	name_CN = "刃舞"
	def available(self):
		return self.Game.heroes[self.ID].attack > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = self.calcDamage(self.Game.heroes[self.ID].attack)
		if damage > 0 and (minions := self.Game.minionsAlive(3-self.ID)):
			minions = numpyChoice(minions, min(3, len(minions)), replace=False)
			self.AOE_Damage(minions, [damage]*len(minions))
		
		
class FeastofSouls(Spell):
	Class, school, name = "Demon Hunter", "Shadow", "Feast of Souls"
	requireTarget, mana, effects = False, 2, ""
	index = "DEMON_HUNTER_INITIATE~Demon Hunter~Spell~2~Shadow~Feast of Souls"
	description = "Draw a card for each friendly minion that died this turn"
	name_CN = "灵魂盛宴"
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.minionsDiedThisTurn[self.ID] != []
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		num = len(self.Game.Counters.minionsDiedThisTurn[self.ID])
		for i in range(num): self.Game.Hand_Deck.drawCard(self.ID)
		
		
class Umberwing(Weapon):
	Class, name, description = "Demon Hunter", "Umberwing", "Battlecry: Summon two 1/1 Felwings"
	mana, attack, durability, effects = 2, 1, 2, ""
	index = "DEMON_HUNTER_INITIATE~Demon Hunter~Weapon~2~1~2~Umberwing~Battlecry"
	name_CN = "棕红之翼"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon([Felwing(self.Game, self.ID) for _ in (0, 1)])
		

class Felwing(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Felwing"
	mana, attack, health = 1, 1, 1
	index = "DEMON_HUNTER_INITIATE~Demon Hunter~Minion~1~1~1~Demon~Felwing~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "邪翼蝠"
	
	
class AltruistheOutcast(Minion):
	Class, race, name = "Demon Hunter", "", "Altruis the Outcast"
	mana, attack, health = 4, 4, 2
	index = "DEMON_HUNTER_INITIATE~Demon Hunter~Minion~4~4~2~~Altruis the Outcast~Legendary"
	requireTarget, effects, description = False, "", "After you play the left- or right-most card in your hand, deal 1 damage to all enemies"
	name_CN = "流放者奥图里斯"
	trigBoard = Trig_AltruistheOutcast		


class EyeBeam(Spell):
	Class, school, name = "Demon Hunter", "Fel", "Eye Beam"
	requireTarget, mana, effects = True, 3, "Lifesteal"
	index = "DEMON_HUNTER_INITIATE~Demon Hunter~Spell~3~Fel~Eye Beam~Outcast"
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
		

class WrathscaleNaga(Minion):
	Class, race, name = "Demon Hunter", "", "Wrathscale Naga"
	mana, attack, health = 3, 3, 1
	index = "DEMON_HUNTER_INITIATE~Demon Hunter~Minion~3~3~1~~Wrathscale Naga"
	requireTarget, effects, description = False, "", "After a friendly minion dies, deal 3 damage to a random enemy"
	name_CN = "怒鳞纳迦"
	trigBoard = Trig_WrathscaleNaga


class IllidariFelblade(Minion):
	Class, race, name = "Demon Hunter", "", "Illidari Felblade"
	mana, attack, health = 4, 5, 3
	index = "DEMON_HUNTER_INITIATE~Demon Hunter~Minion~4~5~3~~Illidari Felblade~Rush~Outcast"
	requireTarget, effects, description = False, "Rush", "Rush. Outcast: Gain Immune this turn"
	name_CN = "伊利达雷邪刃武士"
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.outcastcanTrig(self)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if posinHand == 0 or posinHand == -1:
			self.giveEnchant(self, effectEnchant=Enchantment(effGain="Immune", until=0, name=IllidariFelblade))
		
		
class SoulSplit(Spell):
	Class, school, name = "Demon Hunter", "Shadow~", "Soul Split"
	requireTarget, mana, effects = True, 4, ""
	index = "DEMON_HUNTER_INITIATE~Demon Hunter~Spell~4~Shadow~Soul Split"
	description = "Choose a friendly Demon. Summon a copy of it"
	name_CN = "灵魂分裂"
	
	def available(self):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and "Demon" in target.race and target.ID == self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and self.Game.space(self.ID) > 0:
			Copy = target.selfCopy(self.ID, self) if target.onBoard else type(target)(self.Game, self.ID)
			self.summon(Copy, position=target.pos+1)
		return target
		

class CommandtheIllidari(Spell):
	Class, school, name = "Demon Hunter", "", "Command the Illidari"
	requireTarget, mana, effects = False, 5, ""
	index = "DEMON_HUNTER_INITIATE~Demon Hunter~Spell~5~~Command the Illidari"
	description = "Summon six 1/1 Illidari with Rush"
	name_CN = "统率伊利达雷"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon([IllidariInitiate(self.Game, self.ID) for i in range(6)])
		

class WrathspikeBrute(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Wrathspike Brute"
	mana, attack, health = 5, 2, 6
	index = "DEMON_HUNTER_INITIATE~Demon Hunter~Minion~5~2~6~Demon~Wrathspike Brute~Taunt"
	requireTarget, effects, description = False, "Taunt", "Taunt. After this is attacked, deal 1 damage to all enemies"
	name_CN = "怒刺蛮兵"
	trigBoard = Trig_WrathspikeBrute		


class Flamereaper(Weapon):
	Class, name, description = "Demon Hunter", "Flamereaper", "Also damages the minions next to whomever your hero attacks"
	mana, attack, durability, effects = 7, 4 ,3, "Sweep"
	index = "DEMON_HUNTER_INITIATE~Demon Hunter~Weapon~7~4~3~Flamereaper"
	name_CN = "斩炎"


class HulkingOverfiend(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Hulking Overfiend"
	mana, attack, health = 8, 5, 10
	index = "DEMON_HUNTER_INITIATE~Demon Hunter~Minion~8~5~10~Demon~Hulking Overfiend~Rush"
	requireTarget, effects, description = False, "Rush", "Rush. After this attacks and kills a minion, it may attack again"
	name_CN = "巨型大恶魔"
	trigBoard = Trig_HulkingOverfiend		


class Nethrandamus(Minion):
	Class, race, name = "Demon Hunter", "Dragon", "Nethrandamus"
	mana, attack, health = 9, 8, 8
	index = "DEMON_HUNTER_INITIATE~Demon Hunter~Minion~9~8~8~Dragon~Nethrandamus~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: Summon two random 0-Cost minions. (Upgrades each time a friendly minion dies!)"
	name_CN = "奈瑟兰达姆斯"
	trigHand = Trig_Nethrandamus
	poolIdentifier = "0-Cost Minions to Summon"
	@classmethod
	def generatePool(cls, pools):
		return ["%d-Cost Minions to Summon"%cost for cost in pools.MinionsofCost.keys()], \
				[list(pools.MinionsofCost[cost].values()) for cost in pools.MinionsofCost.keys()]
				
	def text(self): return self.progress
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon([self.newEvolved(self.progress-1, by=1, ID=self.ID) for _ in (0, 1)], relative="<>")
		
	
"""Game TrigEffects and Game Auras"""
class Blur_Effect(TrigEffect):
	card, signals, trigType = Blur, ("FinalDmgonHero?",), "Conn&TurnEnd&OnlyKeepOne"
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return target.ID == self.ID and target.onBoard

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		number[0] = 0

class ManaBurn_Effect(TrigEffect):
	card, counter, trigType = ManaBurn, 2, "TurnStart&OnlyKeepOne"
	def trigEffect(self): self.Game.Manas.manas_withheld[self.ID] -= self.counter


DemonHunterInit_Cards = []

TrigDeaths_DemonHunterInitiate = {Death_UrzulHorror: (UrzulHorror, "Deathrattle: Add a 2/1 Lost Soul to your hand"),
								}