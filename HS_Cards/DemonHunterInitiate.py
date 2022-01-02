from Parts.CardTypes import *
from Parts.TrigsAuras import *
from HS_Cards.AcrossPacks import IllidariInitiate


class Death_UrzulHorror(Deathrattle):
	description = "Deathrattle: Add a 2/1 Lost Soul to your hand"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.addCardtoHand(LostSoul, self.keeper.ID)
		
	
class Trig_Battlefiend(TrigBoard):
	signals = ("HeroAttackedMinion", "HeroAttackedHero",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and subject is kpr.Game.heroes[kpr.ID]
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).giveEnchant(kpr, statEnchant=Enchantment_Exclusive(Battlefiend, 1, 0))
		
	
class Trig_AltruistheOutcast(TrigBoard):
	signals = ("CardBeenPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID and kpr is not kpr.Game.cardinPlay and num[1] in (-1, 0)
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).dealsDamage(kpr.Game.charsonBoard(3-kpr.ID), 1)
		
	
class Trig_EyeBeam(TrigHand):
	signals = ("HandCheck",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.inHand and target.ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).Game.Manas.calcMana_Single(kpr)
		
	
class Trig_WrathscaleNaga(TrigBoard):
	signals = ("ObjDied",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return target.category == "Minion" and kpr.onBoard and target is not kpr and target.ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		if objs := (kpr := self.keeper).Game.charsAlive(3-kpr.ID): kpr.dealsDamage(numpyChoice(objs), 1)
		
	
class Trig_WrathspikeBrute(TrigBoard):
	signals = ("MinionAttackedMinion", "HeroAttackedMinion",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and target is kpr
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).dealsDamage(kpr.Game.charsonBoard(3-kpr.ID), 1)
		
	
class Trig_HulkingOverfiend(TrigBoard):
	signals = ("MinionAttackedMinion",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and subject is kpr and (target.health < 1 or target.dead) and kpr.aliveonBoard()
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.attChances_extra += 1
		
	
class Trig_Nethrandamus(TrigHand):
	signals = ("ObjDied",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return target.category == "Minion" and kpr.inHand and target.ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.progress += 1
		
	
class Blur_Effect(TrigEffect):
	signals, trigType = ("FinalDmgonHero?",), "Conn&TurnEnd&OnlyKeepOne"
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return target.ID == self.ID and target.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		num[0] = 0
		
	
class ManaBurn_Effect(TrigEffect):
	counter, trigType = 2, "TurnStart&OnlyKeepOne"
	def trigEffect(self): self.Game.Manas.manas_withheld[self.ID] -= self.counter
		
	
class Blur(Spell):
	Class, school, name = "Demon Hunter", "", "Blur"
	numTargets, mana, Effects = 0, 0, ""
	description = "Your hero can't take damage this turn"
	name_CN = "疾影"
	trigEffect = Blur_Effect
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		#不知道与博尔碎盾的结算是如何进行的。
		Blur_Effect(self.Game, self.ID).connect()
		
	
class TwinSlice(Spell):
	Class, school, name = "Demon Hunter", "", "Twin Slice"
	numTargets, mana, Effects = 0, 1, ""
	description = "Give your hero +2 Attack this turn. Add 'Second Slice' to your hand"
	name_CN = "双刃斩击"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveHeroAttackArmor(self.ID, attGain=2, source=TwinSlice)
		self.addCardtoHand(SecondSlice, self.ID)
		
	
class SecondSlice(Spell):
	Class, school, name = "Demon Hunter", "", "Second Slice"
	numTargets, mana, Effects = 0, 1, ""
	description = "Give your hero +2 Attack this turn"
	name_CN = "二次斩击"
	index = "Uncollectible"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveHeroAttackArmor(self.ID, attGain=2, source=SecondSlice)
		
	
class Battlefiend(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Battlefiend"
	mana, attack, health = 1, 1, 2
	numTargets, Effects, description = 0, "", "After your hero attacks, gain +1 Attack"
	name_CN = "战斗邪犬"
	trigBoard = Trig_Battlefiend		
	
	
class ConsumeMagic(Spell):
	Class, school, name = "Demon Hunter", "Shadow", "Consume Magic"
	numTargets, mana, Effects = 1, 1, ""
	description = "Silence an enemy minion. Outcast: Draw a card"
	name_CN = "吞噬魔法"
	index = "Outcast"
	def available(self):
		return self.selectableMinionExists(3 - self.ID)
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.ID != self.ID and obj.onBoard
		
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.outcastcanTrig(self)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.Game.silenceMinions(target)
		if posinHand in (-1, 0): self.Game.Hand_Deck.drawCard(self.ID)
		
	
class ManaBurn(Spell):
	Class, school, name = "Demon Hunter", "Fel", "Mana Burn"
	numTargets, mana, Effects = 0, 1, ""
	description = "Your opponent has 2 fewer Mana Crystals next turn"
	name_CN = "法力燃烧"
	trigEffect = ManaBurn_Effect
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.Game.Manas.manas_withheld[3-self.ID] += 2
		ManaBurn_Effect(self.Game, 3-self.ID).connect()
		
	
class UrzulHorror(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Ur'zul Horror"
	mana, attack, health = 1, 2, 1
	numTargets, Effects, description = 0, "", "Deathrattle: Add a 2/1 Lost Soul to your hand"
	name_CN = "乌祖尔恐魔"
	deathrattle = Death_UrzulHorror
	
	
class LostSoul(Minion):
	Class, race, name = "Demon Hunter", "", "Lost Soul"
	mana, attack, health = 1, 2, 1
	numTargets, Effects, description = 0, "", ""
	name_CN = "迷失之魂"
	index = "Uncollectible"
	
	
class BladeDance(Spell):
	Class, school, name = "Demon Hunter", "", "Blade Dance"
	numTargets, mana, Effects = 0, 3, ""
	description = "Deal damage equal to your hero's Attack to 3 random enemy minions"
	name_CN = "刃舞"
	def available(self):
		return self.Game.heroes[self.ID].attack > 0
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if (atk := self.Game.heroes[self.ID].attack) > 0 and (minions := self.Game.minionsAlive(3-self.ID)):
			self.dealsDamage(numpyChoice(minions, min(3, len(minions)), replace=False), self.calcDamage(atk))
		
	
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
		
	
class Umberwing(Weapon):
	Class, name, description = "Demon Hunter", "Umberwing", "Battlecry: Summon two 1/1 Felwings"
	mana, attack, durability, Effects = 2, 1, 2, ""
	name_CN = "棕红之翼"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon([Felwing(self.Game, self.ID) for _ in (0, 1)])
		
	
class Felwing(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Felwing"
	mana, attack, health = 1, 1, 1
	numTargets, Effects, description = 0, "", ""
	name_CN = "邪翼蝠"
	index = "Uncollectible"
	
	
class AltruistheOutcast(Minion):
	Class, race, name = "Demon Hunter", "", "Altruis the Outcast"
	mana, attack, health = 4, 4, 2
	numTargets, Effects, description = 0, "", "After you play the left- or right-most card in your hand, deal 1 damage to all enemies"
	name_CN = "流放者奥图里斯"
	trigBoard = Trig_AltruistheOutcast
	index = "Legendary"
	
	
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
		
	
class WrathscaleNaga(Minion):
	Class, race, name = "Demon Hunter", "", "Wrathscale Naga"
	mana, attack, health = 3, 3, 1
	numTargets, Effects, description = 0, "", "After a friendly minion dies, deal 3 damage to a random enemy"
	name_CN = "怒鳞纳迦"
	trigBoard = Trig_WrathscaleNaga
	
	
class IllidariFelblade(Minion):
	Class, race, name = "Demon Hunter", "", "Illidari Felblade"
	mana, attack, health = 4, 5, 3
	numTargets, Effects, description = 0, "Rush", "Rush. Outcast: Gain Immune this turn"
	name_CN = "伊利达雷邪刃武士"
	index = "Outcast"
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.outcastcanTrig(self)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if posinHand in (-1, 0):
			self.giveEnchant(self, effectEnchant=Enchantment(IllidariFelblade, effGain="Immune", until=0))
		
	
class SoulSplit(Spell):
	Class, school, name = "Demon Hunter", "Shadow~", "Soul Split"
	numTargets, mana, Effects = 1, 4, ""
	description = "Choose a friendly Demon. Summon a copy of it"
	name_CN = "灵魂分裂"
	def available(self):
		return self.selectableMinionExists(self.ID)
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and "Demon" in obj.race and obj.ID == self.ID and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for obj in target: self.summon(self.copyCard(obj, self.ID), position=obj.pos+1)
		
	
class CommandtheIllidari(Spell):
	Class, school, name = "Demon Hunter", "", "Command the Illidari"
	numTargets, mana, Effects = 0, 5, ""
	description = "Summon six 1/1 Illidari with Rush"
	name_CN = "统率伊利达雷"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon([IllidariInitiate(self.Game, self.ID) for i in range(6)])
		
	
class WrathspikeBrute(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Wrathspike Brute"
	mana, attack, health = 5, 2, 6
	numTargets, Effects, description = 0, "Taunt", "Taunt. After this is attacked, deal 1 damage to all enemies"
	name_CN = "怒刺蛮兵"
	trigBoard = Trig_WrathspikeBrute		
	
	
class Flamereaper(Weapon):
	Class, name, description = "Demon Hunter", "Flamereaper", "Also damages the minions next to whomever your hero attacks"
	mana, attack, durability, Effects = 7, 4 ,3, "Sweep"
	name_CN = "斩炎"
	
	
class HulkingOverfiend(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Hulking Overfiend"
	mana, attack, health = 8, 5, 10
	numTargets, Effects, description = 0, "Rush", "Rush. After this attacks and kills a minion, it may attack again"
	name_CN = "巨型大恶魔"
	trigBoard = Trig_HulkingOverfiend		
	
	
class Nethrandamus(Minion):
	Class, race, name = "Demon Hunter", "Dragon", "Nethrandamus"
	mana, attack, health = 9, 8, 8
	numTargets, Effects, description = 0, "", "Battlecry: Summon two random 0-Cost minions. (Upgrades each time a friendly minion dies!)"
	name_CN = "奈瑟兰达姆斯"
	index = "Battlecry~Legendary"
	trigHand = Trig_Nethrandamus
	def text(self): return self.progress
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon([self.newEvolved(self.progress-1, by=1, ID=self.ID) for _ in (0, 1)], relative="<>")
		
	


AllClasses_DemonHunterInitiate = [
	Death_UrzulHorror, Trig_Battlefiend, Trig_AltruistheOutcast, Trig_EyeBeam, Trig_WrathscaleNaga, Trig_WrathspikeBrute,
	Trig_HulkingOverfiend, Trig_Nethrandamus, Blur_Effect, ManaBurn_Effect, Blur, TwinSlice, SecondSlice, Battlefiend,
	ConsumeMagic, ManaBurn, UrzulHorror, LostSoul, BladeDance, FeastofSouls, Umberwing, Felwing, AltruistheOutcast,
	EyeBeam, WrathscaleNaga, IllidariFelblade, SoulSplit, CommandtheIllidari, WrathspikeBrute, Flamereaper, HulkingOverfiend,
	Nethrandamus, 
]

for class_ in AllClasses_DemonHunterInitiate:
	if issubclass(class_, Card):
		class_.index = "DEMON_HUNTER_INITIATE" + ("~" if class_.index else '') + class_.index