from Parts.CardTypes import *
from Parts.TrigsAuras import *
from HS_Cards.AcrossPacks import TheCoin, SilverHandRecruit, BoomBot
from HS_Cards.Shadows import Twinspell, EVILCableRat


class Death_Skyvateer(Deathrattle):
	description = "Deathrattle: Draw a card"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.Game.Hand_Deck.drawCard(self.keeper.ID)
		
	
class Death_FiendishServant(Deathrattle):
	description = "Deathrattle: Give this minion's Attack to a random friendly minion"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		if (kpr := self.keeper).attack > 0 and (minions := kpr.Game.minionsonBoard(kpr.ID)):
			kpr.giveEnchant(numpyChoice(minions), kpr.attack, 0, source=FiendishServant)
		
	
class Trig_IceShard(TrigBoard):
	signals = ("MinionTakesDmg", "HeroTakesDmg",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return subject is self.keeper
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.freeze(target)
		
	
class Trig_FrenziedFelwing(TrigHand):
	signals = ("HeroTakesDmg",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.inHand and target is kpr.Game.heroes[3-kpr.ID]
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).Game.Manas.calcMana_Single(kpr)
		
	
class Trig_EscapedManasaber(TrigBoard):
	signals = ("MinionAttackingMinion", "MinionAttackingHero",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return subject is kpr and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		if kpr.Game.Manas.manas[kpr.ID] < 10:
			kpr.Game.Manas.manas[kpr.ID] += 1
		
	
class Trig_GrandLackeyErkh(TrigBoard):
	signals = ("CardBeenPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID and kpr.Game.cardinPlay.name.endswith(" Lackey")
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).addCardtoHand(numpyChoice(EVILCableRat.lackeys), kpr.ID)
		
	
class Trig_ChopshopCopter(TrigBoard):
	signals = ("ObjDied",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return "Mech" in target.race and kpr.onBoard and target.ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).addCardtoHand(numpyChoice(self.rngPool("Mechs")), kpr.ID)
		
	
class GameRuleAura_ArcaneAmplifier(GameRuleAura):
	def auraAppears(self): self.keeper.Game.powers[self.keeper.ID].getsEffect("Power Damage", 2)
		
	def auraDisappears(self): self.keeper.Game.powers[self.keeper.ID].losesEffect("Power Damage", 2)
		
	
class Trig_WhatDoesThisDo(TrigBoard):
	signals = ("TurnStarts",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return ID == self.keeper.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		numpyChoice(self.rngPool("Spells"))((kpr := self.keeper).Game, kpr.ID).cast()
		
	
class Trig_TheFistofRaden(TrigBoard):
	signals = ("CardBeenPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return comment == "Spell" and ID == kpr.ID and kpr.onBoard and kpr.health > 0
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		#莱登之拳对于费用不在随机池中的法术不会响应；埃提耶什会消耗一个耐久度，但是不会召唤随从
		key = "%d-Cost Legendary Minions to Summon" % num[0]
		minions = numpyChoice(self.rngPool(key)) if key in self.rngPool(key) and kpr.Game.space(kpr.ID) > 0 else None
		if minions:
			kpr.summon(numpyChoice(minions)(kpr.Game, kpr.ID))
			self.keeper.losesDurability()
		
	
class Trig_CorruptedHand(TrigHand):
	signals, description = ("TurnEnds",), "At the end of turn, discard this"
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.inHand and kpr.ID == ID #被腐蚀的卡只会在其拥有者的回合结束时才会被丢弃
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).Game.Hand_Deck.discard(kpr.ID, kpr)
		
	
class Trig_RiskySkipper(TrigBoard):
	signals = ("CardBeenPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return comment == "Minion" and ID == kpr.ID and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).dealsDamage(kpr.Game.minionsonBoard(), 1)
		
	
class Trig_BombWrangler(TrigBoard):
	signals = ("MinionTakesDmg",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and target is kpr
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).summon(BoomBot(kpr.Game, kpr.ID))
		
	
class GameManaAura_BoompistolBully(GameManaAura_OneTime):
	signals, by, nextTurn = ("HandCheck",), +5, True
	def applicable(self, target): return target.ID == self.ID and "~Battlecry" in target.index
		
	
class SkydivingInstructor(Minion):
	Class, race, name = "Neutral", "", "Skydiving Instructor"
	mana, attack, health = 3, 2, 2
	name_CN = "伞降教官"
	numTargets, Effects, description = 0, "", "Battlecry: Summon a 1-Cost minion from your deck"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.try_SummonfromOwn(self.pos + 1, cond=lambda card: card.category == "Minion" and card.mana == 1)
		
	
class Hailbringer(Minion):
	Class, race, name = "Neutral", "Elemental", "Hailbringer"
	mana, attack, health = 5, 3, 4
	name_CN = "冰雹使者"
	numTargets, Effects, description = 0, "", "Battlecry: Summon two 1/1 Ice Shards that Freeze"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon([IceShard(self.Game, self.ID) for _ in (0, 1)], relative="<>")
		
	
class IceShard(Minion):
	Class, race, name = "Neutral", "Elemental", "Ice Shard"
	mana, attack, health = 1, 1, 1
	name_CN = "寒冰碎片"
	numTargets, Effects, description = 0, "", "Freeze any character damaged by this minion"
	index = "Uncollectible"
	trigBoard = Trig_IceShard		
	
	
class LicensedAdventurer(Minion):
	Class, race, name = "Neutral", "", "Licensed Adventurer"
	mana, attack, health = 2, 3, 2
	name_CN = "资深探险者"
	numTargets, Effects, description = 0, "", "Battlecry: If you control a Quest, add a Coin to your hand"
	index = "Battlecry"
	def effCanTrig(self):
		self.effectViable = self.Game.Secrets.mainQuests[self.ID] or self.Game.Secrets.sideQuests[self.ID]
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.Game.Secrets.mainQuests[self.ID] or self.Game.Secrets.sideQuests[self.ID]:
			self.addCardtoHand(TheCoin, self.ID)
		
	
class FrenziedFelwing(Minion):
	Class, race, name = "Neutral", "Demon", "Frenzied Felwing"
	mana, attack, health = 4, 3, 2
	numTargets, Effects, description = 0, "", "Costs (1) less for each damage dealt to your opponent this turn"
	name_CN = "狂暴邪翼蝠"
	trigHand = Trig_FrenziedFelwing
	def selfManaChange(self):
		self.mana -= self.Game.Counters.examDmgonHero(3-self.ID, turnInd=self.Game.turnInd, veri_sum=1)
		
	
class EscapedManasaber(Minion):
	Class, race, name = "Neutral", "Beast", "Escaped Manasaber"
	mana, attack, health = 4, 3, 5
	numTargets, Effects, description = 0, "Stealth", "Stealth. Whenever this attacks, gain 1 Mana Crystal this turn only"
	name_CN = "奔逃的魔晶豹"
	trigBoard = Trig_EscapedManasaber		
	
	
class BoompistolBully(Minion):
	Class, race, name = "Neutral", "", "Boompistol Bully"
	mana, attack, health = 5, 5, 5
	name_CN = "持枪恶霸"
	numTargets, Effects, description = 0, "", "Battlecry: Enemy Battlecry cards cost (5) more next turn"
	index = "Battlecry"
	trigEffect = GameManaAura_BoompistolBully
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		GameManaAura_BoompistolBully(self.Game, 3-self.ID).auraAppears()
		
	
class GrandLackeyErkh(Minion):
	Class, race, name = "Neutral", "", "Grand Lackey Erkh"
	mana, attack, health = 4, 2, 3
	name_CN = "高级跟班厄尔克"
	numTargets, Effects, description = 0, "", "After you play a Lackey, add a Lackey to your hand"
	index = "Legendary"
	trigBoard = Trig_GrandLackeyErkh		
	
	
class SkyGenralKragg(Minion):
	Class, race, name = "Neutral", "Pirate", "Sky Gen'ral Kragg"
	mana, attack, health = 4, 2, 3
	name_CN = "天空上将库拉格"
	numTargets, Effects, description = 0, "Taunt", "Taunt. Battlecry: If you've played a Quest this game, summon a 4/2 Parrot with Rush"
	index = "Battlecry~Legendary"
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.examCardPlays(self.ID, cond=lambda tup: tup[0].race == "Quest")
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.Game.Counters.examCardPlays(self.ID, cond=lambda tup: tup[0].race == "Quest"):
			self.summon(Sharkbait(self.Game, self.ID))
		
	
class Sharkbait(Minion):
	Class, race, name = "Neutral", "Beast", "Sharkbait"
	mana, attack, health = 4, 4, 2
	name_CN = "鲨鱼饵"
	numTargets, Effects, description = 0, "Rush", "Rush"
	index = "Legendary~Uncollectible"
	
	
class TakeFlight(Spell):
	Class, school, name = "Druid", "", "Take Flight"
	numTargets, mana, Effects = 0, 2, ""
	name_CN = "雏鹰起飞"
	description = "Draw a card"
	index = "Uncollectible"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.Game.Hand_Deck.drawCard(self.ID)
		
	
class SwoopIn(Spell):
	Class, school, name = "Druid", "", "Swoop In"
	numTargets, mana, Effects = 0, 2, ""
	name_CN = "猛禽飞掠"
	description = "Summon a 3/2 Eagle"
	index = "Uncollectible"
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
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
	numTargets, mana, Effects = 0, 2, ""
	name_CN = "乘风而起"
	description = "Choose One- Draw a card; or Summon a 3/2 Eagle"
	index = "Uncollectible"
	options = (TakeFlight_Option, SwoopIn_Option)
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if choice < 1:
			self.Game.Hand_Deck.drawCard(self.ID)
		if choice:
			self.summon(Eagle(self.Game, self.ID))
		
	
class RisingWinds(RisingWinds2):
	description = "Twinspell. Choose One- Draw a card; or Summon a 3/2 Eagle"
	twinspellCopy = RisingWinds2
	
	
class Eagle(Minion):
	Class, race, name = "Druid", "Beast", "Eagle"
	mana, attack, health = 2, 3, 2
	name_CN = "鹰"
	numTargets, Effects, description = 0, "", ""
	index = "Uncollectible"
	
	
class SteelBeetle(Minion):
	Class, race, name = "Druid", "Beast", "Steel Beetle"
	mana, attack, health = 2, 2, 3
	name_CN = "钢铁甲虫"
	numTargets, Effects, description = 0, "", "Battlecry: If you're holding a spell that costs (5) or more, gain 5 Armor"
	index = "Battlecry"
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.holdingBigSpell(self.ID)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.Game.Hand_Deck.holdingBigSpell(self.ID):
			self.giveHeroAttackArmor(self.ID, armor=5)
		
	
class WingedGuardian(Minion):
	Class, race, name = "Druid", "Beast", "Winged Guardian"
	mana, attack, health = 7, 6, 8
	name_CN = "飞翼守护者"
	numTargets, Effects, description = 0, "Taunt,Reborn,Evasive", "Taunt, Reborn. Can't be targeted by spells or Hero Powers"
	
	
class FreshScent2(Twinspell):
	Class, school, name = "Hunter", "", "Fresh Scent"
	numTargets, mana, Effects = 1, 2, ""
	name_CN = "新鲜气息"
	description = "Given a Beast +2/+2"
	index = "Uncollectible"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and "Beast" in obj.race and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(target, 2, 2, source=FreshScent)
		
	
class FreshScent(FreshScent2):
	description = "Twinspell. Given a Beast +2/+2"
	twinspellCopy = FreshScent2
	
	
class ChopshopCopter(Minion):
	Class, race, name = "Hunter", "Mech", "Chopshop Copter"
	mana, attack, health = 3, 2, 4
	numTargets, Effects, description = 0, "", "After a friendly Mech dies, add a random Mech to your hand"
	name_CN = "拆件旋翼机"
	trigBoard = Trig_ChopshopCopter
	
	
class RotnestDrake(Minion):
	Class, race, name = "Hunter", "Dragon", "Rotnest Drake"
	mana, attack, health = 5, 6, 5
	name_CN = "腐巢幼龙"
	numTargets, Effects, description = 0, "", "Battlecry: If you're holding a Dragon, destroy a random enemy minion"
	index = "Battlecry"
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID, self)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.Game.Hand_Deck.holdingDragon(self.ID) and (minions := self.Game.minionsAlive(3-self.ID)):
			self.Game.kill(self, numpyChoice(minions))
		
	
class ArcaneAmplifier(Minion):
	Class, race, name = "Mage", "Elemental", "Arcane Amplifier"
	mana, attack, health = 3, 2, 5
	numTargets, Effects, description = 0, "", "Your Hero Power deals 2 extra damage"
	name_CN = "奥术增幅体"
	aura = GameRuleAura_ArcaneAmplifier
	
	
class AnimatedAvalanche(Minion):
	Class, race, name = "Mage", "Elemental", "Animated Avalanche"
	mana, attack, health = 7, 7, 6
	name_CN = "活化雪崩"
	numTargets, Effects, description = 0, "", "Battlecry: If you played an Elemental last turn, summon a copy of this"
	index = "Battlecry"
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.examElementalsLastTurn(self.ID)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if not self.dead and self.Game.Counters.examElementalsLastTurn(self.ID):
			self.summon(self.copyCard(self, self.ID))
		
	
class WhatDoesThisDo(Power):
	mana, name, numTargets = 0, "What Does This Do?", 0
	description = "Passive Hero Power. At the start of your turn, cast a random spell"
	name_CN = "这是什么？"
	trigBoard = Trig_WhatDoesThisDo		
	def available(self, choice=0): return False
		
	def use(self, target=None, choice=0, sendthruServer=True): pass
		
	def effect_wrapper(self, target=(), choice=0): pass
		
	
class TheAmazingReno(Hero):
	mana, description = 10, "Battlecry: Make all minions disappear. *Poof!*"
	Class, name, heroPower, armor = "Mage", "The Amazing Reno", WhatDoesThisDo, 5
	name_CN = "神奇的雷诺"
	index = "Battlecry~Legendary"
	poolIdentifier = "Spells"
	@classmethod
	def generatePool(cls, pools):
		return "Spells", [card for cards in pools.ClassSpells.values() for card in cards]
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for minion in self.Game.minionsonBoard():
			self.Game.banishMinion(self, minion)
		
	
class Shotbot(Minion):
	Class, race, name = "Paladin", "Mech", "Shotbot"
	mana, attack, health = 2, 2, 2
	name_CN = "炮火机甲"
	numTargets, Effects, description = 0, "Reborn", "Reborn"
	
	
class AirRaid2(Twinspell):
	Class, school, name = "Paladin", "", "Air Raid"
	numTargets, mana, Effects = 0, 2, ""
	name_CN = "空中团战"
	description = "Summon two 1/1 Silver Hand Recruits with Taunt"
	index = "Uncollectible"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		minions = [SilverHandRecruit(self.Game, self.ID) for _ in (0, 1)]
		self.giveEnchant(minions, effGain="Taunt", source=AirRaid, add2EventinGUI=False)
		self.summon(minions)
		
	
class AirRaid(Spell):
	description = "Twinspell. Summon two 1/1 Silver Hand Recruits with Taunt"
	twinspellCopy = AirRaid2
	
	
class Scalelord(Minion):
	Class, race, name = "Paladin", "Dragon", "Scalelord"
	mana, attack, health = 5, 5, 6
	name_CN = "鳞甲领主"
	numTargets, Effects, description = 0, "", "Battlecry: Give your Murlocs Divine Shield"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(self.Game.minionsonBoard(self.ID, race="Murloc"), effGain="Divine Shield", source=Scalelord)
		
	
class AeonReaver(Minion):
	Class, race, name = "Priest", "Dragon", "Aeon Reaver"
	mana, attack, health = 6, 4, 4
	name_CN = "永恒掠夺者"
	numTargets, Effects, description = 1, "", "Battlecry: Deal damage to a minion equal to its Attack"
	index = "Battlecry"
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj is not self and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(target, [obj.attack for obj in target])
		
	
class ClericofScales(Minion):
	Class, race, name = "Priest", "", "Cleric of Scales"
	mana, attack, health = 1, 1, 1
	name_CN = "龙鳞祭司"
	numTargets, Effects, description = 0, "", "Battlecry: If you're holding a Dragon, Discover a spell from your deck"
	index = "Battlecry"
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.Game.Hand_Deck.holdingDragon(self.ID):
			_, i = self.discoverfrom(comment, cond=lambda card: card.category == "Spell")
			if i > -1: self.Game.Hand_Deck.drawCard(self.ID, i)
		
	
class DarkProphecy(Spell):
	Class, school, name = "Priest", "Shadow", "Dark Prophecy"
	numTargets, mana, Effects = 0, 3, ""
	description = "Discover a 2-Cost minion. Summon it and give it +3 Health"
	name_CN = "黑暗预兆"
	poolIdentifier = "2-Cost Minions as Priest"
	@classmethod
	def generatePool(cls, pools):
		return genPool_CertainMinionsasClass(pools, "2-Cost", cond=lambda card: card.mana == 2)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		card, _ = self.discoverNew(comment, lambda : self.rngPool("2-Cost Minions as "+class4Discover(self)), add2Hand=False)
		if card:
			self.giveEnchant(card, 0, 3, source=DarkProphecy)
			self.summon(card)
		
	
class Skyvateer(Minion):
	Class, race, name = "Rogue", "Pirate", "Skyvateer"
	mana, attack, health = 2, 1, 3
	numTargets, Effects, description = 0, "Stealth", "Stealth. Deathrattle: Draw a card"
	name_CN = "空中私掠者"
	deathrattle = Death_Skyvateer
	
	
class Waxmancy(Spell):
	Class, school, name = "Rogue", "", "Waxmancy"
	numTargets, mana, Effects = 0, 2, ""
	description = "Discover a Battlecry minion. Reduce its Cost by (2)"
	name_CN = "蜡烛学"
	poolIdentifier = "Battlecry Minions as Rogue"
	@classmethod
	def generatePool(cls, pools):
		return genPool_CertainMinionsasClass(pools, "Battlecry", cond=lambda card: "Battlecry" in card.index)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		card, _ = self.discoverNew(comment, lambda: self.rngPool("Battlecry Minions as"+class4Discover(self)))
		if card: ManaMod(card, by=-2).applies()
		
	
class ShadowSculptor(Minion):
	Class, race, name = "Rogue", "", "Shadow Sculptor"
	mana, attack, health = 5, 3, 2
	name_CN = "暗影塑形师"
	numTargets, Effects, description = 0, "", "Combo: Draw a card for each card you've played this turn"
	index = "Combo"
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.comboCounters[self.ID] > 0
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for _ in range(self.Game.Counters.comboCounters[self.ID]): self.Game.Hand_Deck.drawCard(self.ID)
		
	
class ExplosiveEvolution(Spell):
	Class, school, name = "Shaman", "Nature", "Explosive Evolution"
	numTargets, mana, Effects = 1, 2, ""
	description = "Transform a friendly minion into a random one that costs (3) more"
	name_CN = "惊爆异变"
	def available(self):
		return self.selectableMinionExists(self.ID)
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.ID == self.ID and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.transform(target, [self.newEvolved(obj.mana_0, by=3, ID=obj.ID) for obj in target])
		
	
class EyeoftheStorm(Spell):
	Class, school, name = "Shaman", "Nature", "Eye of the Storm"
	numTargets, mana, Effects = 0, 10, ""
	description = "Summon three 5/6 Elementals with Taunt. Overload: (3)"
	name_CN = "风暴之眼"
	overload = 3
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon([Stormblocker(self.Game, self.ID) for _ in (0, 1, 2)])
		
	
class Stormblocker(Minion):
	Class, race, name = "Shaman", "Elemental", "Stormblocker"
	mana, attack, health = 5, 5, 6
	name_CN = "拦路风暴"
	numTargets, Effects, description = 0, "Taunt", "Taunt"
	index = "Uncollectible"
	
	
class TheFistofRaden(Weapon):
	Class, name, description = "Shaman", "The Fist of Ra-den", "After you cast a spell, summon a Legendary minion of that Cost. Lose 1 Durability"
	mana, attack, durability, Effects = 4, 1, 4, ""
	name_CN = "莱登之拳"
	index = "Legendary"
	trigBoard = Trig_TheFistofRaden
	poolIdentifier = "1-Cost Legendary Minions to Summon"
	@classmethod
	def generatePool(cls, pools):
		minions = {mana: [card for card in cards if "~Legendary" in card.index] for mana, cards in pools.MinionsofCost.items()}
		return ["%d-Cost Legendary Minions to Summon"%mana for mana in minions], list(minions.values())
		
	
class FiendishServant(Minion):
	Class, race, name = "Warlock", "Demon", "Fiendish Servant"
	mana, attack, health = 1, 2, 1
	numTargets, Effects, description = 0, "", "Deathrattle: Give this minion's Attack to a random friendly minion"
	name_CN = "邪魔仆人"
	deathrattle = Death_FiendishServant
	
	
class TwistedKnowledge(Spell):
	Class, school, name = "Warlock", "Shadow", "Twisted Knowledge"
	numTargets, mana, Effects = 0, 2, ""
	description = "Discover 2 Warlock cards"
	name_CN = "扭曲学识"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.discoverNew(comment, lambda : self.rngPool("Warlock Cards"))
		self.discoverNew(comment, lambda : self.rngPool("Warlock Cards"))
		
	
class ChaosGazer(Minion):
	Class, race, name = "Warlock", "Demon", "Chaos Gazer"
	mana, attack, health = 3, 4, 3
	name_CN = "混乱凝视者"
	numTargets, Effects, description = 0, "", "Battlecry: Corrupt a playable card in your opponent's hand. They have 1 turn to play it!"
	index = "Battlecry"
	trigEffect = Trig_CorruptedHand
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		#只会考虑当前的费用，寻找下回合法力值以下的牌。延时生效的法力值效果不会被考虑。
		#如果被战吼触发前被对方控制了，则也会根据我方下个回合的水晶进行腐化。但是这个回合结束时就会丢弃（因为也算是一个回合。）
		#https://www.bilibili.com/video/av92443139?from=search&seid=7929483619040209451
		manaNextTurn = max(0, min(10, self.Game.Manas.manasUpper[3 - self.ID] + 1) - self.Game.Manas.manasOverloaded[3 - self.ID])
		if cards := [card for card in self.Game.Hand_Deck.hands[3 - self.ID] \
				if card.mana <= manaNextTurn and not any(isinstance(trig, Trig_CorruptedHand) for trig in card.trigsHand)]:
			self.giveEnchant(numpyChoice(cards), trig=Trig_CorruptedHand, trigType="TrigHand")
		
	
class BoomSquad(Spell):
	Class, school, name = "Warrior", "", "Boom Squad"
	numTargets, mana, Effects = 0, 1, ""
	description = "Discover a Lackey, Mech, or a Dragon"
	name_CN = "砰砰战队"
	poolIdentifier = "Mechs as Warrior"
	@classmethod
	def generatePool(cls, pools):
		identifers_Mech, cards_Mech = genPool_MinionsofRaceasClass(pools, "Mech")
		identifers_Dragon, cards_Dragon = genPool_MinionsofRaceasClass(pools, "Dragon")
		return identifers_Mech + identifers_Dragon, cards_Mech + cards_Dragon
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		Class = class4Discover(self)
		self.discoverNew_MultiPools(comment, lambda : [EVILCableRat.lackeys, self.rngPool("Mechs as "+Class), self.rngPool("Dragons as "+Class)])
		
	
class RiskySkipper(Minion):
	Class, race, name = "Warrior", "Pirate", "Risky Skipper"
	mana, attack, health = 1, 1, 3
	numTargets, Effects, description = 0, "", "After you play a minion, deal 1 damage to all minions"
	name_CN = "冒进的艇长"
	trigBoard = Trig_RiskySkipper		
	
	
class BombWrangler(Minion):
	Class, race, name = "Warrior", "", "Bomb Wrangler"
	mana, attack, health = 3, 2, 3
	numTargets, Effects, description = 0, "", "Whenever this minion takes damage, summon a 1/1 Boom Bot"
	name_CN = "炸弹牛仔"
	trigBoard = Trig_BombWrangler
	
	


AllClasses_Galakrond = [
	Death_Skyvateer, Death_FiendishServant, Trig_IceShard, Trig_FrenziedFelwing, Trig_EscapedManasaber, Trig_GrandLackeyErkh,
	Trig_ChopshopCopter, GameRuleAura_ArcaneAmplifier, Trig_WhatDoesThisDo, Trig_TheFistofRaden, Trig_CorruptedHand,
	Trig_RiskySkipper, Trig_BombWrangler, GameManaAura_BoompistolBully, SkydivingInstructor, Hailbringer, IceShard,
	LicensedAdventurer, FrenziedFelwing, EscapedManasaber, BoompistolBully, GrandLackeyErkh, SkyGenralKragg, Sharkbait,
	TakeFlight, SwoopIn, TakeFlight_Option, SwoopIn_Option, RisingWinds2, RisingWinds, Eagle, SteelBeetle, WingedGuardian,
	FreshScent2, FreshScent, ChopshopCopter, RotnestDrake, ArcaneAmplifier, AnimatedAvalanche, WhatDoesThisDo, TheAmazingReno,
	Shotbot, AirRaid2, AirRaid, Scalelord, AeonReaver, ClericofScales, DarkProphecy, Skyvateer, Waxmancy, ShadowSculptor,
	ExplosiveEvolution, EyeoftheStorm, Stormblocker, TheFistofRaden, FiendishServant, TwistedKnowledge, ChaosGazer,
	BoomSquad, RiskySkipper, BombWrangler, 
]

for class_ in AllClasses_Galakrond:
	if issubclass(class_, Card):
		class_.index = "YEAR_OF_THE_DRAGON" + ("~" if class_.index else '') + class_.index