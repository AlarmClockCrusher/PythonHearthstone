from Parts.CardTypes import *
"""Auras"""



"""Deathrattles"""



"""Trigs"""



"""Game TrigEffects and Game auras"""



"""Cards"""
#Neutral Cards
class TestSpell(Spell):
	Class, school, name = "Neutral", "Fire", "Test Spell"
	numTargets, mana, Effects = 3, 0, ""
	description = "Select 3 minions. Deal 3 damage to each"
	name_CN = "测试用法术"
	index = "DIY_Cards"
	def available(self):
		return self.canFindTargetsNeeded()
		#return any(self.canSelect(obj) for obj in self.Game.minionsonBoard())

	def effectNeedsAllTargets(self, choice=0): False
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard

	def text(self): return self.calcDamage(3)

	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if target: self.dealsDamage(target, self.calcDamage(3))


class CheckSpell(Spell):
	Class, school, name = "Neutral", "Arcane", "Check Spell"
	numTargets, mana, Effects = 3, 0, ""
	description = "Select a Pirate, a Mech and a Murloc. Give each of them +1/+1"
	name_CN = "测试用法术"
	index = "DIY_Cards"
	def available(self):
		return self.canFindTargetsNeeded()
		#return sum(self.canSelect(obj) for obj in self.Game.minionsonBoard()) > 1

	def effectNeedsAllTargets(self, choice=0): return False
	def targetCorrect(self, obj, choice=0, ith=0):
		return ("Pirate", "Mech", "Murloc")[ith] in obj.race and obj.onBoard

	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(target, 1, 1, source=CheckSpell)


class ExperimentalSpell(Spell):
	Class, school, name = "Neutral", "Fel", "Experimental Spell"
	numTargets, mana, Effects = 2, 0, ""
	description = "Choose a friendly minion and an enemy one. Your minion attacks the enemy one"
	name_CN = "测试用法术"
	index = "DIY_Cards"
	def available(self):
		return self.canFindTargetsNeeded()
		#return sum(self.canSelect(obj) for obj in self.Game.minionsonBoard()) > 1

	def effectNeedsAllTargets(self, choice=0): return True
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard and not (ith == 0 - obj.ID == self.ID)

	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(target, 1, 1, source=CheckSpell)

#Demon Hunter Cards

#Druid Cards

#Hunter Cards

#Mage Cards

#Paladin Cards

#Priest Cards

#Rogue Cards

#Shaman Cards

#Warlock Cards

#Warrior Cards


"""Trigs&Deathrattles cardType assignment"""


AllClasses_DIY = [TestSpell, CheckSpell, ExperimentalSpell,
]