from Parts_ConstsFuncsImports import *
from Parts_CardTypes import *
from Parts_TrigsAuras import *

from HS_AcrossPacks import TheCoin, SilverHandRecruit, BoomBot, Lackeys
from HS_Shadows import Twinspell


"""Deathrattles"""
class Death_Skyvateer(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.Game.Hand_Deck.drawCard(self.keeper.ID)

class Death_FiendishServant(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if minions := self.keeper.Game.minionsonBoard(self.keeper.ID):
			self.keeper.giveEnchant(numpyChoice(minions), number, 0, name=FiendishServant)


"""Triggers"""
class Trig_IceShard(TrigBoard):
	signals = ("MinionTakesDmg", "HeroTakesDmg", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.keeper

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.freeze(target)
		
		
class Trig_FrenziedFelwing(TrigHand):
	signals = ("HeroTakesDmg", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.inHand and target == self.keeper.Game.heroes[3-self.keeper.ID]
		
	def text(self):
		return "在本回合中，你的对手每受到1点伤害，该牌的法力值消耗便减少(1)点" if CHN \
				else "Costs (1) less for each damage dealt to your opponent this turn"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.Game.Manas.calcMana_Single(self.keeper)
		
		
class Trig_EscapedManasaber(TrigBoard):
	signals = ("MinionAttackingMinion", "MinionAttackingHero", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.keeper and self.keeper.onBoard

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if self.keeper.Game.Manas.manas[self.keeper.ID] < 10:
			self.keeper.Game.Manas.manas[self.keeper.ID] += 1
			
	
class Trig_GrandLackeyErkh(TrigBoard):
	signals = ("MinionBeenPlayed", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject.ID == self.keeper.ID and subject.name.endswith(" Lackey")

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.addCardtoHand(numpyChoice(Lackeys), self.keeper.ID)
		
		
class Trig_ChopshopCopter(TrigBoard):
	signals = ("MinionDied", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and target.ID == self.keeper.ID and "Mech" in target.race

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.addCardtoHand(numpyChoice(self.rngPool("Mechs")), self.keeper.ID)
			
			
class GameRuleAura_ArcaneAmplifier(GameRuleAura):
	def auraAppears(self): self.keeper.Game.powers[self.keeper.ID].getsEffect("Power Damage", 2)
	def auraDisappears(self): self.keeper.Game.powers[self.keeper.ID].losesEffect("Power Damage", 2)
		

class Trig_WhatDoesThisDo(TrigBoard):
	signals = ("TurnStarts", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return ID == self.keeper.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		numpyChoice(self.rngPool("Spells"))(self.keeper.Game, self.keeper.ID).cast()
		

class Trig_TheFistofRaden(TrigBoard):
	signals = ("SpellBeenPlayed", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.keeper.ID and self.keeper.onBoard and self.keeper.health > 0

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		key = "%d-Cost Legendary Minions to Summon" % number
		minions = numpyChoice(self.rngPool(key)) if key in self.rngPool(key) and self.keeper.Game.space(self.keeper.ID) > 0 else None
		if minions:
			self.keeper.summon(numpyChoice(minions)(self.keeper.Game, self.keeper.ID))
			self.keeper.losesDurability()
		

class Trig_CorruptedHand(TrigHand):
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.inHand and self.keeper.ID == ID #被腐蚀的卡只会在其拥有者的回合结束时才会被丢弃
		
	def text(self):
		return "你的回合结束时，弃掉这张手牌" if CHN else "At the end of this turn, discard this card"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.Game.Hand_Deck.discard(self.keeper.ID, self.keeper)
		
		
class Trig_RiskySkipper(TrigBoard):
	signals = ("MinionBeenPlayed", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject.ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		targets = self.keeper.Game.minionsonBoard(1) + self.keeper.Game.minionsonBoard(2)
		self.keeper.AOE_Damage(targets, [1 for minion in targets])
		
	
class Trig_BombWrangler(TrigBoard):
	signals = ("MinionTakesDmg", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and target == self.keeper

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.summon(BoomBot(self.keeper.Game, self.keeper.ID))
		
				
class SkydivingInstructor(Minion):
	Class, race, name = "Neutral", "", "Skydiving Instructor"
	mana, attack, health = 3, 2, 2
	index = "YEAR_OF_THE_DRAGON~Neutral~Minion~3~2~2~~Skydiving Instructor~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Summon a 1-Cost minion from your deck"
	name_CN = "伞降教官"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.try_SummonfromDeck(self.pos + 1, func=lambda card: card.category == "Minion" and card.mana == 1)
		
		
class Hailbringer(Minion):
	Class, race, name = "Neutral", "Elemental", "Hailbringer"
	mana, attack, health = 5, 3, 4
	index = "YEAR_OF_THE_DRAGON~Neutral~Minion~5~3~4~Elemental~Hailbringer~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Summon two 1/1 Ice Shards that Freeze"
	name_CN = "冰雹使者"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon([IceShard(self.Game, self.ID) for _ in (0, 1)], relative="<>")
		

class IceShard(Minion):
	Class, race, name = "Neutral", "Elemental", "Ice Shard"
	mana, attack, health = 1, 1, 1
	index = "YEAR_OF_THE_DRAGON~Neutral~Minion~1~1~1~Elemental~Ice Shard~Uncollectible"
	requireTarget, effects, description = False, "", "Freeze any character damaged by this minion"
	name_CN = "寒冰碎片"
	trigBoard = Trig_IceShard		


class LicensedAdventurer(Minion):
	Class, race, name = "Neutral", "", "Licensed Adventurer"
	mana, attack, health = 2, 3, 2
	index = "YEAR_OF_THE_DRAGON~Neutral~Minion~2~3~2~~Licensed Adventurer~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: If you control a Quest, add a Coin to your hand"
	name_CN = "资深探险者"
	def effCanTrig(self):
		self.effectViable = self.Game.Secrets.mainQuests[self.ID] != [] or self.Game.Secrets.sideQuests[self.ID] != []
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Secrets.mainQuests[self.ID] != [] or self.Game.Secrets.sideQuests[self.ID] != []:
			self.addCardtoHand(TheCoin, self.ID)
		

class FrenziedFelwing(Minion):
	Class, race, name = "Neutral", "Demon", "Frenzied Felwing"
	mana, attack, health = 4, 3, 2
	index = "YEAR_OF_THE_DRAGON~Neutral~Minion~4~3~2~Demon~Frenzied Felwing"
	requireTarget, effects, description = False, "", "Costs (1) less for each damage dealt to your opponent this turn"
	name_CN = "狂暴邪翼蝠"
	trigHand = Trig_FrenziedFelwing
	def selfManaChange(self):
		if self.inHand:
			manaReduction = self.Game.Counters.dmgHeroTookThisTurn[3 - self.ID]
			self.mana -= manaReduction
			self.mana = max(0, self.mana)
			

class EscapedManasaber(Minion):
	Class, race, name = "Neutral", "Beast", "Escaped Manasaber"
	mana, attack, health = 4, 3, 5
	index = "YEAR_OF_THE_DRAGON~Neutral~Minion~4~3~5~Beast~Escaped Manasaber~Stealth"
	requireTarget, effects, description = False, "Stealth", "Stealth. Whenever this attacks, gain 1 Mana Crystal this turn only"
	name_CN = "奔逃的魔晶豹"
	trigBoard = Trig_EscapedManasaber		


class BoompistolBully(Minion):
	Class, race, name = "Neutral", "", "Boompistol Bully"
	mana, attack, health = 5, 5, 5
	index = "YEAR_OF_THE_DRAGON~Neutral~Minion~5~5~5~~Boompistol Bully~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Enemy Battlecry cards cost (5) more next turn"
	name_CN = "持枪恶霸"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		GameManaAura_BoompistolBully(self.Game, 3-self.ID).auraAppears()
		

class GrandLackeyErkh(Minion):
	Class, race, name = "Neutral", "", "Grand Lackey Erkh"
	mana, attack, health = 4, 2, 3
	index = "YEAR_OF_THE_DRAGON~Neutral~Minion~4~2~3~~Grand Lackey Erkh~Legendary"
	requireTarget, effects, description = False, "", "After you play a Lackey, add a Lackey to your hand"
	name_CN = "高级跟班厄尔克"
	trigBoard = Trig_GrandLackeyErkh		


class SkyGenralKragg(Minion):
	Class, race, name = "Neutral", "Pirate", "Sky Gen'ral Kragg"
	mana, attack, health = 4, 2, 3
	index = "YEAR_OF_THE_DRAGON~Neutral~Minion~4~2~3~Pirate~Sky Gen'ral Kragg~Taunt~Battlecry~Legendary"
	requireTarget, effects, description = False, "Taunt", "Taunt. Battlecry: If you've played a Quest this game, summon a 4/2 Parrot with Rush"
	name_CN = "天空上将库拉格"
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.hasPlayedQuestThisGame[self.ID]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Counters.hasPlayedQuestThisGame[self.ID]:
			self.summon(Sharkbait(self.Game, self.ID))
		

class Sharkbait(Minion):
	Class, race, name = "Neutral", "Beast", "Sharkbait"
	mana, attack, health = 4, 4, 2
	index = "YEAR_OF_THE_DRAGON~Neutral~Minion~4~4~2~Beast~Sharkbait~Rush~Legendary~Uncollectible"
	requireTarget, effects, description = False, "Rush", "Rush"
	name_CN = "鲨鱼饵"
	
	
class TakeFlight(Spell):
	Class, school, name = "Druid", "", "Take Flight"
	requireTarget, mana, effects = False, 2, ""
	index = "YEAR_OF_THE_DRAGON~Druid~Spell~2~Take Flight~Uncollectible"
	description = "Draw a card"
	name_CN = "雏鹰起飞"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.Hand_Deck.drawCard(self.ID)
		
class SwoopIn(Spell):
	Class, school, name = "Druid", "", "Swoop In"
	requireTarget, mana, effects = False, 2, ""
	index = "YEAR_OF_THE_DRAGON~Druid~Spell~2~Swoop In~Uncollectible"
	description = "Summon a 3/2 Eagle"
	name_CN = "猛禽飞掠"
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon(Eagle(self.Game, self.ID))
		
class TakeFlight_Option(Option):
	name, description = "Take Flight", "Draw a card"
	mana, attack, health = 2, -1, -1
	spell = TakeFlight
	
class SwoopIn_Option(Option):
	name, description = "Swoop In", "Summon a 3/2 Eagle"
	mana, attack, health = 2, -1, -1
	spell = SwoopIn
	def available(self):
		return self.keeper.Game.space(self.keeper.ID) > 0
		
class RisingWinds2(Twinspell):
	Class, school, name = "Druid", "", "Rising Winds"
	requireTarget, mana, effects = False, 2, ""
	index = "YEAR_OF_THE_DRAGON~Druid~Spell~2~Rising Winds~Choose One~Uncollectible"
	description = "Choose One- Draw a card; or Summon a 3/2 Eagle"
	name_CN = "乘风而起"
	options = (TakeFlight_Option, SwoopIn_Option)
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if choice < 1:
			self.Game.Hand_Deck.drawCard(self.ID)
		if choice != 0:
			self.summon(Eagle(self.Game, self.ID))
		
class RisingWinds(RisingWinds2):
	index = "YEAR_OF_THE_DRAGON~Druid~Spell~2~Rising Winds~Twinspell~Choose One"
	description = "Twinspell. Choose One- Draw a card; or Summon a 3/2 Eagle"
	twinspellCopy = RisingWinds2
	
class Eagle(Minion):
	Class, race, name = "Druid", "Beast", "Eagle"
	mana, attack, health = 2, 3, 2
	index = "YEAR_OF_THE_DRAGON~Druid~Minion~2~3~2~Beast~Eagle~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "鹰"
	
	
class SteelBeetle(Minion):
	Class, race, name = "Druid", "Beast", "Steel Beetle"
	mana, attack, health = 2, 2, 3
	index = "YEAR_OF_THE_DRAGON~Druid~Minion~2~2~3~Beast~Steel Beetle~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: If you're holding a spell that costs (5) or more, gain 5 Armor"
	name_CN = "钢铁甲虫"
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.holdingSpellwith5CostorMore(self.ID)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Hand_Deck.holdingSpellwith5CostorMore(self.ID):
			self.giveHeroAttackArmor(self.ID, armor=5)
		
		
class WingedGuardian(Minion):
	Class, race, name = "Druid", "Beast", "Winged Guardian"
	mana, attack, health = 7, 6, 8
	index = "YEAR_OF_THE_DRAGON~Druid~Minion~7~6~8~Beast~Winged Guardian~Taunt~Reborn"
	requireTarget, effects, description = False, "Taunt,Reborn,Evasive", "Taunt, Reborn. Can't be targeted by spells or Hero Powers"
	name_CN = "飞翼守护者"
		
		
class FreshScent2(Twinspell):
	Class, school, name = "Hunter", "", "Fresh Scent"
	requireTarget, mana, effects = True, 2, ""
	index = "YEAR_OF_THE_DRAGON~Hunter~Spell~2~Fresh Scent~Uncollectible"
	description = "Given a Beast +2/+2"
	name_CN = "新鲜气息"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and "Beast" in target.race and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.giveEnchant(target, 2, 2, name=FreshScent)
		return target
		
class FreshScent(FreshScent2):
	index = "YEAR_OF_THE_DRAGON~Hunter~Spell~2~Fresh Scent~Twinspell"
	description = "Twinspell. Given a Beast +2/+2"
	twinspellCopy = FreshScent2
	
	
class ChopshopCopter(Minion):
	Class, race, name = "Hunter", "Mech", "Chopshop Copter"
	mana, attack, health = 3, 2, 4
	index = "YEAR_OF_THE_DRAGON~Hunter~Minion~3~2~4~Mech~Chopshop Copter"
	requireTarget, effects, description = False, "", "After a friendly Mech dies, add a random Mech to your hand"
	name_CN = "拆件旋翼机"
	poolIdentifier = "Mechs"
	@classmethod
	def generatePool(cls, pools):
		return "Mechs", list(pools.MinionswithRace["Mech"].values())
		
	trigBoard = Trig_ChopshopCopter		


class RotnestDrake(Minion):
	Class, race, name = "Hunter", "Dragon", "Rotnest Drake"
	mana, attack, health = 5, 6, 5
	index = "YEAR_OF_THE_DRAGON~Hunter~Minion~5~6~5~Dragon~Rotnest Drake~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: If you're holding a Dragon, destroy a random enemy minion"
	name_CN = "腐巢幼龙"
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID, self)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		minions = self.Game.minionsAlive(3-self.ID)
		if minions: self.Game.killMinion(self, numpyChoice(minions))
		
		
class ArcaneAmplifier(Minion):
	Class, race, name = "Mage", "Elemental", "Arcane Amplifier"
	mana, attack, health = 3, 2, 5
	index = "YEAR_OF_THE_DRAGON~Mage~Minion~3~2~5~Elemental~Arcane Amplifier"
	requireTarget, effects, description = False, "", "Your Hero Power deals 2 extra damage"
	name_CN = "奥术增幅体"
	aura = GameRuleAura_ArcaneAmplifier
	
		
class AnimatedAvalanche(Minion):
	Class, race, name = "Mage", "Elemental", "Animated Avalanche"
	mana, attack, health = 7, 7, 6
	index = "YEAR_OF_THE_DRAGON~Mage~Minion~7~7~6~Elemental~Animated Avalanche~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: If you played an Elemental last turn, summon a copy of this"
	name_CN = "活化雪崩"
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.numElementalsPlayedLastTurn[self.ID] > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Counters.numElementalsPlayedLastTurn[self.ID] > 0:
			Copy = self.selfCopy(self.ID, self) if self.onBoard else type(self)(self.Game, self.ID)
			self.summon(Copy)
		
		
class WhatDoesThisDo(Power):
	mana, name, requireTarget = 0, "What Does This Do?", False
	index = "Mage~Hero Power~0~What Does This Do?"
	description = "Passive Hero Power. At the start of your turn, cast a random spell"
	name_CN = "这是什么？"
	trigBoard = Trig_WhatDoesThisDo		
	def available(self, choice=0):
		return False
		
	def use(self, target=None, choice=0, comment=''):
		return 0
		
	def appears(self):
		for trig in self.trigsBoard: trig.connect()
		self.Game.sendSignal("PowerAppears", self.ID, self, None, 0, "")
		
	def disappears(self):
		for trig in self.trigsBoard: trig.disconnect()
		

class TheAmazingReno(Hero):
	mana, description = 10, "Battlecry: Make all minions disappear. *Poof!*"
	Class, name, heroPower, armor = "Mage", "The Amazing Reno", WhatDoesThisDo, 5
	index = "YEAR_OF_THE_DRAGON~Mage~Hero Card~10~The Amazing Reno~Battlecry~Legendary"
	name_CN = "神奇的雷诺"
	poolIdentifier = "Spells"
	@classmethod
	def generatePool(cls, pools):
		spells = []
		for Class in pools.Classes:
			spells += [value for key, value in pools.ClassCards[Class].items() if "~Spell~" in key]
		return "Spells", spells
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for minion in self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2):
			self.Game.banishMinion(self, minion)
		
		
class Shotbot(Minion):
	Class, race, name = "Paladin", "Mech", "Shotbot"
	mana, attack, health = 2, 2, 2
	index = "YEAR_OF_THE_DRAGON~Paladin~Minion~2~2~2~Mech~Shotbot~Reborn"
	requireTarget, effects, description = False, "Reborn", "Reborn"
	name_CN = "炮火机甲"
	
	
class AirRaid2(Twinspell):
	Class, school, name = "Paladin", "", "Air Raid"
	requireTarget, mana, effects = False, 2, ""
	index = "YEAR_OF_THE_DRAGON~Paladin~Spell~2~Air Raid~Uncollectible"
	description = "Summon two 1/1 Silver Hand Recruits with Taunt"
	name_CN = "空中团战"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		minions = [SilverHandRecruit(self.Game, self.ID) for _ in (0, 1)]
		self.AOE_GiveEnchant(minions, effGain="Taunt", name=AirRaid, add2EventinGUI=False)
		self.summon(minions)
		
class AirRaid(Spell):
	index = "YEAR_OF_THE_DRAGON~Paladin~Spell~2~Air Raid~Twinspell"
	description = "Twinspell. Summon two 1/1 Silver Hand Recruits with Taunt"
	twinspellCopy = AirRaid2
	
	
class Scalelord(Minion):
	Class, race, name = "Paladin", "Dragon", "Scalelord"
	mana, attack, health = 5, 5, 6
	index = "YEAR_OF_THE_DRAGON~Paladin~Minion~5~5~6~Dragon~Scalelord~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Give your Murlocs Divine Shield"
	name_CN = "鳞甲领主"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.AOE_GiveEnchant(self.Game.minionsonBoard(self.ID, race="Murloc"), effGain="Divine Shield", name=Scalelord)
		
		
class AeonReaver(Minion):
	Class, race, name = "Priest", "Dragon", "Aeon Reaver"
	mana, attack, health = 6, 4, 4
	index = "YEAR_OF_THE_DRAGON~Priest~Minion~6~4~4~Dragon~Aeon Reaver~Battlecry"
	requireTarget, effects, description = True, "", "Battlecry: Deal damage to a minion equal to its Attack"
	name_CN = "永恒掠夺者"
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.dealsDamage(target, target.attack)
		return target
		
		
class ClericofScales(Minion):
	Class, race, name = "Priest", "", "Cleric of Scales"
	mana, attack, health = 1, 1, 1
	index = "YEAR_OF_THE_DRAGON~Priest~Minion~1~1~1~~Cleric of Scales~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: If you're holding a Dragon, Discover a spell from your deck"
	name_CN = "龙鳞祭司"
	
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Hand_Deck.holdingDragon(self.ID):
			self.discoverfromList(ClericofScales, comment, conditional=lambda card: card.category == "Spell")
		
	def discoverDecided(self, option, case, info_RNGSync=None, info_GUISync=None):
		self.handleDiscoveredCardfromList(option, case, ls=self.Game.Hand_Deck.hands[self.ID],
										  func=lambda index, card: self.Game.Hand_Deck.drawCard(self.ID, index),
										  info_RNGSync=info_RNGSync, info_GUISync=info_GUISync)
		
		
class DarkProphecy(Spell):
	Class, school, name = "Priest", "Shadow", "Dark Prophecy"
	requireTarget, mana, effects = False, 3, ""
	index = "YEAR_OF_THE_DRAGON~Priest~Spell~3~Shadow~Dark Prophecy"
	description = "Discover a 2-Cost minion. Summon it and give it +3 Health"
	name_CN = "黑暗预兆"
	poolIdentifier = "2-Cost Minions as Priest"
	@classmethod
	def generatePool(cls, pools):
		classCards = {s : [] for s in pools.ClassesandNeutral}
		for key, value in pools.MinionsofCost[2].items():
			for Class in key.split('~')[1].split(','):
				classCards[Class].append(value)
		return ["2-Cost Minions as "+Class for Class in pools.Classes], \
			[classCards[Class]+classCards["Neutral"] for Class in pools.Classes]
			
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverandGenerate(DarkProphecy, comment, poolFunc=lambda : self.rngPool("2-Cost Minions as "+classforDiscover(self)))
		
	def summonDiscoveredMinion(self, card):
		self.giveEnchant(card, 0, 3, name=DarkProphecy)
		self.summon(card)
	
	def discoverDecided(self, option, case, info_RNGSync=None, info_GUISync=None):
		self.handleDiscoverGeneratedCard(option, case, info_RNGSync, info_GUISync,
										 func=lambda cardType, card: DarkProphecy.summonDiscoveredMinion(self, card))
		
		
class Skyvateer(Minion):
	Class, race, name = "Rogue", "Pirate", "Skyvateer"
	mana, attack, health = 2, 1, 3
	index = "YEAR_OF_THE_DRAGON~Rogue~Minion~2~1~3~Pirate~Skyvateer~Stealth~Deathrattle"
	requireTarget, effects, description = False, "Stealth", "Stealth. Deathrattle: Draw a card"
	name_CN = "空中私掠者"
	deathrattle = Death_Skyvateer


class Waxmancy(Spell):
	Class, school, name = "Rogue", "", "Waxmancy"
	requireTarget, mana, effects = False, 2, ""
	index = "YEAR_OF_THE_DRAGON~Rogue~Spell~2~Waxmancy"
	description = "Discover a Battlecry minion. Reduce its Cost by (2)"
	name_CN = "蜡烛学"
	poolIdentifier = "Battlecry Minions as Rogue"
	@classmethod
	def generatePool(cls, pools):
		classCards = {s : [value for key, value in pools.ClassCards[s].items() if "~Minion~" in key and "~Battlecry" in key] for s in pools.Classes}
		classCards["Neutral"] = [value for key, value in pools.NeutralCards.items() if "~Minion~" in key and "~Battlecry" in key]
		return ["Battlecry Minions as "+Class for Class in pools.Classes], \
			[classCards[Class]+classCards["Neutral"] for Class in pools.Classes]
			
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverandGenerate(Waxmancy, comment, poolFunc=lambda: self.rngPool("Battlecry Minions as"+classforDiscover(self)))
		
	def addCard_Cost2Less(self, card):
		ManaMod(card, by=-2).applies()
		self.addCardtoHand(card, self.ID, byDiscover=True)
	
	def discoverDecided(self, option, case, info_RNGSync=None, info_GUISync=None):
		self.handleDiscoverGeneratedCard(option, case, info_RNGSync, info_GUISync,
										 func=lambda cardType, card: Waxmancy.addCard_Cost2Less(self, card))
		
		
class ShadowSculptor(Minion):
	Class, race, name = "Rogue", "", "Shadow Sculptor"
	mana, attack, health = 5, 3, 2
	index = "YEAR_OF_THE_DRAGON~Rogue~Minion~5~3~2~~Shadow Sculptor~Combo"
	requireTarget, effects, description = False, "", "Combo: Draw a card for each card you've played this turn"
	name_CN = "暗影塑形师"
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0:
			numCardsPlayed = self.Game.combCards(self.ID)
			for i in range(numCardsPlayed): self.Game.Hand_Deck.drawCard(self.ID)
		

class ExplosiveEvolution(Spell):
	Class, school, name = "Shaman", "Nature", "Explosive Evolution"
	requireTarget, mana, effects = True, 2, ""
	index = "YEAR_OF_THE_DRAGON~Shaman~Spell~2~Nature~Explosive Evolution"
	description = "Transform a friendly minion into a random one that costs (3) more"
	name_CN = "惊爆异变"
	poolIdentifier = "1-Cost Minions to Summon"
	@classmethod
	def generatePool(cls, pools):
		return ["%d-Cost Minions to Summon"%cost for cost in pools.MinionsofCost.keys()], \
				[list(pools.MinionsofCost[cost].values()) for cost in pools.MinionsofCost.keys()]
				
	def available(self):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.ID == self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: target = self.transform(target, self.newEvolved(type(target).mana, by=3, ID=target.ID))
		return target
		
		
class EyeoftheStorm(Spell):
	Class, school, name = "Shaman", "Nature", "Eye of the Storm"
	requireTarget, mana, effects = False, 10, ""
	index = "YEAR_OF_THE_DRAGON~Shaman~Spell~10~Nature~Eye of the Storm~Overload"
	description = "Summon three 5/6 Elementals with Taunt. Overload: (3)"
	name_CN = "风暴之眼"
	overload = 3
	
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon([Stormblocker(self.Game, self.ID) for _ in (0, 1, 2)])
		

class Stormblocker(Minion):
	Class, race, name = "Shaman", "Elemental", "Stormblocker"
	mana, attack, health = 5, 5, 6
	index = "YEAR_OF_THE_DRAGON~Shaman~Minion~5~5~6~Elemental~Stormblocker~Taunt~Uncollectible"
	requireTarget, effects, description = False, "Taunt", "Taunt"
	name_CN = "拦路风暴"
	
	
#莱登之拳对于费用不在随机池中的法术不会响应，但是埃提耶什会消耗一个耐久度，但是不会召唤随从


#莱登之拳对于费用不在随机池中的法术不会响应，但是埃提耶什会消耗一个耐久度，但是不会召唤随从
class TheFistofRaden(Weapon):
	Class, name, description = "Shaman", "The Fist of Ra-den", "After you cast a spell, summon a Legendary minion of that Cost. Lose 1 Durability"
	mana, attack, durability, effects = 4, 1, 4, ""
	index = "YEAR_OF_THE_DRAGON~Shaman~Weapon~4~1~4~The Fist of Ra-den~Legendary"
	name_CN = "莱登之拳"
	poolIdentifier = "1-Cost Legendary Minions to Summon"
	@classmethod
	def generatePool(cls, pools):
		minions = {}
		for key, value in pools.LegendaryMinions.items():
			s = key.split('~')[3] + "-Cost Legendary Minions to Summon"
			add2ListinDict(value, minions, s)
		return list(minions.keys()), list(minions.values())
		
	trigBoard = Trig_TheFistofRaden		


class FiendishServant(Minion):
	Class, race, name = "Warlock", "Demon", "Fiendish Servant"
	mana, attack, health = 1, 2, 1
	index = "YEAR_OF_THE_DRAGON~Warlock~Minion~1~2~1~Demon~Fiendish Servant~Deathrattle"
	requireTarget, effects, description = False, "", "Deathrattle: Give this minion's Attack to a random friendly minion"
	name_CN = "邪魔仆人"
	deathrattle = Death_FiendishServant


class TwistedKnowledge(Spell):
	Class, school, name = "Warlock", "Shadow", "Twisted Knowledge"
	requireTarget, mana, effects = False, 2, ""
	index = "YEAR_OF_THE_DRAGON~Warlock~Spell~2~Shadow~Twisted Knowledge"
	description = "Discover 2 Warlock cards"
	name_CN = "扭曲学识"
	poolIdentifier = "Warlock Cards"
	@classmethod
	def generatePool(cls, pools):
		return "Warlock Cards", list(pools.ClassCards["Warlock"].values())
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverandGenerate(TwistedKnowledge, comment, poolFunc=lambda : self.rngPool("Warlock Cards"))
		self.discoverandGenerate(TwistedKnowledge, comment, poolFunc=lambda : self.rngPool("Warlock Cards"))
		
#只会考虑当前的费用，寻找下回合法力值以下的牌。延时生效的法力值效果不会被考虑。
#如果被战吼触发前被对方控制了，则也会根据我方下个回合的水晶进行腐化。但是这个回合结束时就会丢弃（因为也算是一个回合。）
#https://www.bilibili.com/video/av92443139?from=search&seid=7929483619040209451


#只会考虑当前的费用，寻找下回合法力值以下的牌。延时生效的法力值效果不会被考虑。
#如果被战吼触发前被对方控制了，则也会根据我方下个回合的水晶进行腐化。但是这个回合结束时就会丢弃（因为也算是一个回合。）
#https://www.bilibili.com/video/av92443139?from=search&seid=7929483619040209451
class ChaosGazer(Minion):
	Class, race, name = "Warlock", "Demon", "Chaos Gazer"
	mana, attack, health = 3, 4, 3
	index = "YEAR_OF_THE_DRAGON~Warlock~Minion~3~4~3~Demon~Chaos Gazer~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Corrupt a playable card in your opponent's hand. They have 1 turn to play it!"
	name_CN = "混乱凝视者"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		manaNextTurn = max(0, min(10, self.Game.Manas.manasUpper[3 - self.ID] + 1) - self.Game.Manas.manasOverloaded[3 - self.ID])
		if cards := [card for card in self.Game.Hand_Deck.hands[3 - self.ID] \
				if card.mana <= manaNextTurn and not any(isinstance(trig, Trig_CorruptedHand) for trig in card.trigsHand)]:
			self.giveEnchant(numpyChoice(cards), trig=Trig_CorruptedHand, trigType="TrigHand")
		

class BoomSquad(Spell):
	Class, school, name = "Warrior", "", "Boom Squad"
	requireTarget, mana, effects = False, 1, ""
	index = "YEAR_OF_THE_DRAGON~Warrior~Spell~1~Boom Squad"
	description = "Discover a Lackey, Mech, or a Dragon"
	name_CN = "砰砰战队"
	poolIdentifier = "Mechs as Warrior"
	@classmethod
	def generatePool(cls, pools):
		classes_Mech = ["Mechs as %s"+Class for Class in pools.Classes]
		classCards = {s : [] for s in pools.ClassesandNeutral}
		for key, value in pools.MinionswithRace["Mech"].items():
			for Class in key.split('~')[1].split(','):
				classCards[Class].append(value)
		mechs = [classCards[Class]+classCards["Neutral"] for Class in pools.Classes]
		classes_Dragon = ["Dragons as %s"+Class for Class in pools.Classes]
		classCards = {s : [] for s in pools.ClassesandNeutral}
		for key, value in pools.MinionswithRace["Dragon"].items():
			for Class in key.split('~')[1].split(','):
				classCards[Class].append(value)
		dragons = [classCards[Class]+classCards["Neutral"] for Class in pools.Classes]
		return classes_Mech+classes_Dragon, mechs+dragons
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		Class = classforDiscover(self)
		self.discoverandGenerate_MultiplePools(BoomSquad, comment,
											   poolsFunc=lambda : [Lackeys, self.rngPool("Mechs as "+Class),
																   self.rngPool("Dragons as "+Class)]
												)
		
		
class RiskySkipper(Minion):
	Class, race, name = "Warrior", "Pirate", "Risky Skipper"
	mana, attack, health = 1, 1, 3
	index = "YEAR_OF_THE_DRAGON~Warrior~Minion~1~1~3~Pirate~Risky Skipper"
	requireTarget, effects, description = False, "", "After you play a minion, deal 1 damage to all minions"
	name_CN = "冒进的艇长"
	trigBoard = Trig_RiskySkipper		


class BombWrangler(Minion):
	Class, race, name = "Warrior", "", "Bomb Wrangler"
	mana, attack, health = 3, 2, 3
	index = "YEAR_OF_THE_DRAGON~Warrior~Minion~3~2~3~~Bomb Wrangler"
	requireTarget, effects, description = False, "", "Whenever this minion takes damage, summon a 1/1 Boom Bot"
	name_CN = "炸弹牛仔"
	trigBoard = Trig_BombWrangler		


"""Game TrigEffects and Game Aura"""
class GameManaAura_BoompistolBully(GameManaAura_OneTime):
	card, signals, by, nextTurn = BoompistolBully, ("CardEntersHand",), +5, True
	def applicable(self, subject): return subject.ID == self.ID and "~Battlecry" in subject.index
	
	
Galakrond_Cards = [
		#Neutral
		SkydivingInstructor, Hailbringer, IceShard, LicensedAdventurer, FrenziedFelwing, EscapedManasaber, BoompistolBully,
		GrandLackeyErkh, SkyGenralKragg, Sharkbait,
		#Druid
		RisingWinds, RisingWinds2, TakeFlight, SwoopIn, Eagle, SteelBeetle, WingedGuardian,
		#Hunter
		FreshScent, FreshScent2, ChopshopCopter, RotnestDrake,
		#Mage
		ArcaneAmplifier, AnimatedAvalanche, TheAmazingReno,
		#Paladin
		Shotbot, AirRaid, AirRaid2, Scalelord,
		#Priest
		AeonReaver, ClericofScales, DarkProphecy,
		#Rogue
		Skyvateer, Waxmancy, ShadowSculptor,
		#Shaman
		ExplosiveEvolution, EyeoftheStorm, Stormblocker, TheFistofRaden,
		#Warlock
		FiendishServant, TwistedKnowledge, ChaosGazer,
		#Warrior
		BoomSquad, RiskySkipper, BombWrangler,
]

Galakrond_Cards_Collectible = [
		#Neutral
		SkydivingInstructor, Hailbringer, LicensedAdventurer, FrenziedFelwing, EscapedManasaber, BoompistolBully,
		GrandLackeyErkh, SkyGenralKragg,
		#Druid
		RisingWinds, SteelBeetle, WingedGuardian,
		#Hunter
		FreshScent, ChopshopCopter, RotnestDrake,
		#Mage
		ArcaneAmplifier, AnimatedAvalanche, TheAmazingReno,
		#Paladin
		Shotbot, AirRaid, Scalelord,
		#Priest
		AeonReaver, ClericofScales, DarkProphecy,
		#Rogue
		Skyvateer, Waxmancy, ShadowSculptor,
		#Shaman
		ExplosiveEvolution, EyeoftheStorm, TheFistofRaden,
		#Warlock
		FiendishServant, TwistedKnowledge, ChaosGazer,
		#Warrior
		BoomSquad, RiskySkipper, BombWrangler,
]


TrigDeaths_Galakrond = {Death_Skyvateer: (Skyvateer, "Deathrattle: Draw a card"),
						Death_FiendishServant: (FiendishServant, "Deathrattle: Give this minion's Attack to a random friendly minion"),
						}