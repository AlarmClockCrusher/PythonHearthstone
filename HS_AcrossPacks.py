from Parts_ConstsFuncsImports import *
from Parts_CardTypes import *
from Parts_TrigsAuras import *

"""Animations"""
def panda_ShootArrow(GUI, power, target):
	x_0, y_0, z_0 = power.btn.np.getPos()
	x_1, y_1, z_1 = target.btn.np.getPos()
	degree = GUI.getDegreeDistance_fromCoors(x_0, y_0, x_1, y_1)[0]
	arrow = GUI.prepareaRetexturedModel("Models\\ForCards\\HunterArrow.glb", "Models\\ForCards\\HunterArrow.png", hpr=(degree, 10, 0))

	seq_Holder = GUI.seqHolder[-1]
	seq_Holder.append(GUI.LERP_PosHpr(arrow, duration=0.05, startPos=(x_0, y_0, z_0),
											 pos=((x_0+x_1)/2, (y_0+y_1)/2, z_1+0.2), hpr=(degree, 0, 0)))
	seq_Holder.append(GUI.LERP_PosHpr(arrow, duration=0.05, pos=(x_1, y_1, z_1), hpr=(degree, -10, 0)))
	seq_Holder.append(GUI.FUNC(GUI.SEQUENCE(GUI.WAIT(0.2), GUI.FUNC(arrow.removeNode)).start) )


"""Auras"""
class Aura_Leokk(Aura_AlwaysOn):
	attGain = 1

"""Trigs"""
class Trig_HealingTotem(TrigBoard):
	signals = ("TurnEnds", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		targets, heal = self.keeper.Game.minionsonBoard(self.keeper.ID), self.keeper.calcHeal(1)
		self.keeper.AOE_Heal(targets, [heal]*len(targets))


class Trig_StrengthTotem(TrigBoard):
	signals = ("TurnEnds", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if minions := self.keeper.Game.minionsonBoard(self.keeper.ID, self.keeper):
			self.keeper.giveEnchant(numpyChoice(minions), statEnchant=Enchantment_Cumulative(1, 0, name=StrengthTotem))
			

class Trig_WaterElemental(TrigBoard):
	signals = ("MinionTakesDmg", "HeroTakesDmg", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.keeper
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.freeze(target)


class Trig_TruesilverChampion(TrigBoard):
	signals = ("HeroAttackingMinion", "HeroAttackingHero", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.keeper.Game.heroes[self.keeper.ID] and self.keeper.onBoard
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.restoresHealth(self.keeper.Game.heroes[self.keeper.ID], self.keeper.calcHeal(2))


class Trig_Nightmare_1(TrigBoard):
	signals = ("TurnStarts", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and ID == 1
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.Game.killMinion(self.keeper, self.keeper)

class Trig_Nightmare_2(TrigBoard):
	signals = ("TurnStarts",)
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and ID == 2

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.Game.killMinion(self.keeper, self.keeper)


class Trig_ManaWyrm(TrigBoard):
	signals = ("SpellPlayed", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject.ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.giveEnchant(self.keeper, statEnchant=Enchantment_Cumulative(1, 0, name=ManaWyrm))


"""Deathrattles"""
class Death_BoomBot(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if objs := self.keeper.Game.charsAlive(3 - self.keeper.ID):
			self.keeper.dealsDamage(numpyChoice(objs), numpyRandint(1, 5))
		

"""Cards"""
class TheCoin(Spell):
	Class, school, name = "Neutral", "", "The Coin"
	requireTarget, mana, effects = False, 0, ""
	index = "LEGACY~Neutral~Spell~0~~The Coin~Uncollectible"
	description = "Gain 1 mana crystal for this turn."
	name_CN = "幸运币"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.Manas.gainTempManaCrystal(1, ID=self.ID)


class SilverHandRecruit(Minion):
	Class, race, name = "Paladin", "", "Silver Hand Recruit"
	mana, attack, health = 1, 1, 1
	index = "LEGACY~Paladin~Minion~1~1~1~~Silver Hand Recruit~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "白银之手新兵"


class WickedKnife(Weapon):
	Class, name, description = "Rogue", "Wicked Knife", ""
	mana, attack, durability, effects = 1, 1, 2, ""
	index = "LEGACY~Rogue~Weapon~1~1~2~Wicked Knife~Uncollectible"
	name_CN = "邪恶短刀"


class PoisonedDagger(Weapon):
	Class, name, description = "Rogue", "Poisoned Dagger", ""
	mana, attack, durability, effects = 1, 2, 2, ""
	index = "TGT~Rogue~Weapon~1~2~2~Poisoned Dagger~Uncollectible"
	name_CN = "浸毒匕首"


class SearingTotem(Minion):
	Class, race, name = "Shaman", "Totem", "Searing Totem"
	mana, attack, health = 1, 1, 1
	index = "LEGACY~Shaman~Minion~1~1~1~Totem~Searing Totem~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "灼热图腾"


class StoneclawTotem(Minion):
	Class, race, name = "Shaman", "Totem", "Stoneclaw Totem"
	mana, attack, health = 1, 0, 2
	index = "LEGACY~Shaman~Minion~1~0~2~Totem~Stoneclaw Totem~Taunt~Uncollectible"
	requireTarget, effects, description = False, "Taunt", "Taunt"
	name_CN = "石爪图腾"


class HealingTotem(Minion):
	Class, race, name = "Shaman", "Totem", "Healing Totem"
	mana, attack, health = 1, 0, 2
	index = "LEGACY~Shaman~Minion~1~0~2~Totem~Healing Totem~Uncollectible"
	requireTarget, effects, description = False, "", "At the end of your turn, restore 1 health to all friendly minions"
	name_CN = "治疗图腾"
	trigBoard = Trig_HealingTotem
	def text(self): return self.calcHeal(1)
	
class StrengthTotem(Minion):
	Class, race, name = "Shaman", "Totem", "Strength Totem"
	mana, attack, health = 1, 0, 2
	index = "LEGACY~Shaman~Minion~1~0~2~Totem~Strength Totem~Uncollectible"
	requireTarget, effects, description = False, "", "At the end of your turn, give another friendly minion +1 Attack"
	name_CN = "力量图腾"
	trigBoard = Trig_StrengthTotem

BasicTotems = [SearingTotem, StoneclawTotem, HealingTotem, StrengthTotem]


"""Basic and Upgraded Hero Powers"""
class DemonClaws(Power):
	mana, name, requireTarget = 1, "Demon Claws", False
	index = "Demon Hunter~Basic Hero Power~1~Demon Claws"
	description = "+1 Attack this turn"
	name_CN = "恶魔之爪"
	
	def effect(self, target=None, choice=0, comment=''):
		self.giveHeroAttackArmor(self.ID, attGain=1, name=DemonClaws)
		return 0

class DemonsBite(Power):
	mana, name, requireTarget = 1, "Demon's Bite", False
	index = "Demon Hunter~Upgraded Hero Power~1~Demon's Bite"
	description = "+2 Attack this turn"
	name_CN = "恶魔之咬"
	
	def effect(self, target=None, choice=0, comment=''):
		self.giveHeroAttackArmor(self.ID, attGain=2, name=DemonsBite)
		return 0


#Basic and upgraded powers
class Shapeshift(Power):
	mana, name, requireTarget = 2, "Shapeshift", False
	index = "Druid~Basic Hero Power~2~Shapeshift"
	description = "+1 Attack this turn. +1 Armor"
	name_CN = "变形"
	
	def effect(self, target=None, choice=0, comment=''):
		self.giveHeroAttackArmor(self.ID, attGain=1, armor=1, name=Shapeshift)
		return 0

class DireShapeshift(Power):
	mana, name, requireTarget = 2, "Dire Shapeshift", False
	index = "Druid~Upgraded Hero Power~2~Dire Shapeshift"
	description = "+2 Attack this turn. +2 Armor"
	name_CN = "恐怖变形"
	
	def effect(self, target=None, choice=0, comment=''):
		self.giveHeroAttackArmor(self.ID, attGain=2, armor=2, name=DireShapeshift)
		return 0


class SteadyShot(Power):
	mana, name, requireTarget = 2, "Steady Shot", False
	index = "Hunter~Basic Hero Power~2~Steady Shot"
	description = "Deal 2 damage to the enemy hero"
	name_CN = "稳固射击"
	def canDealDmg(self): return True
	def likeSteadyShot(self): return True
	def needTarget(self, choice=0):
		return self.effects["Can Target Minions"] > 0 or self.Game.effects[self.ID]["Power Can Target Minions"] > 0

	def targetCorrect(self, target, choice=0):
		if self.effects["Can Target Minions"] > 0 or self.Game.effects[self.ID]["Power Can Target Minions"] > 0:
			return (target.category == "Minion" or target.category == "Hero") and target.onBoard
		else: return target.category == "Hero" and target.ID != self.ID and target.onBoard

	def text(self): return self.calcDamage(2)

	def powerAni(self):
		GUI = self.Game.GUI
		if GUI:
			pos_0, pos_1 = GUI.heroZones[self.ID].powerPos, GUI.heroZones[3-self.ID].heroPos
			angle = 360 * numpy.arctan((pos_1[2]-pos_0[2]) / (pos_1[0]-pos_0[0])) / numpy.pi
			if pos_1[2] < pos_0[2]: angle = 360 - angle
			
			arrow = GUI.loader.loadModel("TexCards\\ForPowers\\Arrow.glb")
			arrow.reparentTo(GUI.render)
			GUI.seqHolder[-1].append(GUI.LERP_PosHpr(arrow, duration=0.2, startPos=(pos_0[0], pos_0[1]-0.2, pos_0[2]),
													  pos=(pos_1[0], pos_1[1]-0.2, pos_1[2]), startHpr=()),
									 GUI.WAIT(0.5), GUI.FUNC(arrow.removeNode))
			
	def effect(self, target=None, choice=0, comment=''):
		target = target if target else self.Game.heroes[3 - self.ID]
		if target and target.onBoard and (GUI := self.Game.GUI):
			panda_ShootArrow(GUI, self, target)
		dmgTaker, damageActual = self.dealsDamage(target, self.calcDamage(2))
		if dmgTaker.health < 1 or dmgTaker.dead: return 1
		return 0


class BallistaShot(SteadyShot):
	name = "Ballista Shot"
	index = "Hunter~Upgraded Hero Power~2~Ballista Shot"
	description = "Deal 3 damage to the enemy hero"
	name_CN = "弩炮射击"
	def text(self): return self.calcDamage(3)

	def effect(self, target=None, choice=0, comment=''):
		target = target if target else self.Game.heroes[3 - self.ID]
		if target and target.onBoard and (GUI := self.Game.GUI):
			panda_ShootArrow(GUI, self, target)
		dmgTaker, damageActual = self.dealsDamage(target, self.calcDamage(3))
		if dmgTaker.health < 1 or dmgTaker.dead: return 1
		return 0


class Fireblast(Power):
	mana, name, requireTarget = 2, "Fireblast", True
	index = "Mage~Basic Hero Power~2~Fireblast"
	description = "Deal 1 damage"
	name_CN = "火焰冲击"
	def canDealDmg(self): return True

	def text(self): return self.calcDamage(1)

	def effect(self, target=None, choice=0, comment=''):
		dmgTaker, damageActual = self.dealsDamage(target, self.calcDamage(1))
		if dmgTaker.health < 1 or dmgTaker.dead: return 1
		return 0


class FireblastRank2(Power):
	mana, name, requireTarget = 2, "Fireblast Rank 2", True
	index = "Mage~Upgraded Hero Power~2~Fireblast Rank 2"
	description = "Deal 2 damage"
	name_CN = "二级火焰冲击"
	def canDealDmg(self): return True

	def text(self): return self.calcDamage(2)

	def effect(self, target=None, choice=0, comment=''):
		dmgTaker, damageActual = self.dealsDamage(target, self.calcDamage(2))
		if dmgTaker.health < 1 or dmgTaker.dead: return 1
		return 0


class Reinforce(Power):
	mana, name, requireTarget = 2, "Reinforce", False
	index = "Paladin~Basic Hero Power~2~Reinforce"
	description = "Summon a 1/1 Silver Hand Recruit"
	name_CN = "增援"
	
	def available(self):
		return not self.chancesUsedUp() and self.Game.space(self.ID)
	
	def effect(self, target=None, choice=0, comment=''):
		self.summon(SilverHandRecruit(self.Game, self.ID))
		return 0


class TheSilverHand(Power):
	mana, name, requireTarget = 2, "The Silver Hand", False
	index = "Paladin~Upgraded Hero Power~2~The Silver Hand"
	description = "Summon two 1/1 Silver Hand Recruits"
	name_CN = "白银之手"
	
	def available(self):
		return not self.chancesUsedUp() and self.Game.space(self.ID)
	
	def effect(self, target=None, choice=0, comment=''):
		self.summon([SilverHandRecruit(self.Game, self.ID) for _ in (0, 1)])
		return 0


class LesserHeal(Power):
	mana, name, requireTarget = 2, "Lesser Heal", True
	index = "Priest~Basic Hero Power~2~Lesser Heal"
	description = "Restore 2 Health"
	name_CN = "次级治疗术"
	def text(self): return self.calcHeal(2)
	
	def effect(self, target=None, choice=0, comment=''):
		obj, healActual = self.restoresHealth(target, self.calcHeal(2))
		if healActual < 0 and (obj.health < 1 or obj.dead): return 1
		return 0


class Heal(Power):
	mana, name, requireTarget = 2, "Heal", True
	index = "Priest~Upgraded Hero Power~2~Heal"
	description = "Restore 4 Health"
	name_CN = "治疗术"
	def text(self): return self.calcHeal(4)
	
	def effect(self, target=None, choice=0, comment=''):
		obj, healActual = self.restoresHealth(target, self.calcHeal(4))
		if healActual < 0 and (obj.health < 1 or obj.dead): return 1
		return 0


class DaggerMastery(Power):
	mana, name, requireTarget = 2, "Dagger Mastery", False
	index = "Rogue~Basic Hero Power~2~Dagger Mastery"
	description = "Equip a 1/2 Weapon"
	name_CN = "匕首精通"
	
	def effect(self, target=None, choice=0, comment=''):
		self.equipWeapon(WickedKnife(self.Game, self.ID))
		return 0


class PoisonedDaggers(Power):
	mana, name, requireTarget = 2, "Poisoned Daggers", False
	index = "Rogue~Upgraded Hero Power~2~Poisoned Daggers"
	description = "Equip a 2/2 Weapon"
	name_CN = "浸毒匕首"
	
	def effect(self, target=None, choice=0, comment=''):
		self.equipWeapon(PoisonedDagger(self.Game, self.ID))
		return 0


class TotemicCall(Power):
	mana, name, requireTarget = 2, "Totemic Call", False
	index = "Shaman~Basic Hero Power~2~Totemic Call"
	description = "Summon a random totem"
	name_CN = "图腾召唤"
	def available(self):
		return not self.chancesUsedUp() and self.Game.space(self.ID) and self.viableTotems()[0]
	
	def effect(self, target=None, choice=0, comment=''):
		if totems := self.viableTotems(): self.summon(numpyChoice(totems)(self.Game, self.ID))
		return 0
	
	def viableTotems(self):
		viableTotems = [SearingTotem, StoneclawTotem, HealingTotem, StrengthTotem]
		for minion in self.Game.minionsonBoard(self.ID): removefrom(type(minion), viableTotems)
		return viableTotems


class TotemicSlam(Power):
	mana, name, requireTarget = 2, "Totemic Slam", False
	index = "Shaman~Upgraded Hero Power~2~Totemic Call"
	description = "Summon a totem of your choice"
	name_CN = "图腾崇拜"
	def available(self):
		return not self.chancesUsedUp() and self.Game.space(self.ID)
	
	def effect(self, target=None, choice=0, comment=''):
		self.chooseFixedOptions(TotemicSlam, comment, options=[SearingTotem(self.Game, self.ID), StoneclawTotem(self.Game, self.ID), 
															   HealingTotem(self.Game, self.ID), StrengthTotem(self.Game, self.ID)])
		return 0
	
	def discoverDecided(self, option, case, info_RNGSync=None, info_GUISync=None):
		self.handleDiscoverGeneratedCard(option, case, info_RNGSync, info_GUISync,
										 func=lambda cardType, card: self.summon(card))
		

class LifeTap(Power):
	mana, name, requireTarget = 2, "Life Tap", False
	index = "Warlock~Basic Hero Power~2~Life Tap"
	description = "Draw a card and take 2 damage"
	name_CN = "生命分流"
	def canDealDmg(self): return True

	def text(self): return self.calcDamage(2)

	def effect(self, target=None, choice=0, comment=''):
		self.dealsDamage(self.Game.heroes[self.ID], self.calcDamage(2))
		card, mana, entersHand = self.Game.Hand_Deck.drawCard(self.ID)
		if entersHand: self.Game.sendSignal("CardDrawnfromHeroPower", self.ID, self, card, mana, "")
		return 0


class SoulTap(Power):
	mana, name, requireTarget = 2, "Soul Tap", False
	index = "Warlock~Upgraded Hero Power~2~Soul Tap"
	description = "Draw a card"
	name_CN = "灵魂分流"
	
	def effect(self, target=None, choice=0, comment=''):
		card, mana, entersHand = self.Game.Hand_Deck.drawCard(self.ID)
		if entersHand: self.Game.sendSignal("CardDrawnfromHeroPower", self.ID, self, card, mana, "")
		return 0


class ArmorUp(Power):
	mana, name, requireTarget = 2, "Armor Up!", False
	index = "Warrior~Basic Hero Power~2~Armor Up!"
	description = "Gain 2 Armor"
	name_CN = "全副武装！"
	def effect(self, target=None, choice=0, comment=''):
		self.giveHeroAttackArmor(self.ID, armor=2)
		return 0


class TankUp(Power):
	mana, name, requireTarget = 2, "Tank Up!", False
	index = "Warrior~Upgraded Hero Power~2~Tank Up!"
	description = "Gain 4 Armor"
	name_CN = "铜墙铁壁！"
	def effect(self, target=None, choice=0, comment=''):
		self.giveHeroAttackArmor(self.ID, armor=4)
		return 0

Basicpowers = [DemonClaws, Shapeshift, SteadyShot, Fireblast, Reinforce, LesserHeal, DaggerMastery, TotemicCall, LifeTap, ArmorUp]
Upgradedpowers = [DemonsBite, DireShapeshift, BallistaShot, FireblastRank2, TheSilverHand, Heal, PoisonedDaggers, TotemicSlam, SoulTap, TankUp]


"""Heroes"""
class Illidan(Hero):
	Class, name, heroPower, health = "Demon Hunter", "Illidan", DemonClaws, 30
	name_CN = "伊利丹"
	index = "LEGACY"

class Rexxar(Hero):
	Class, name, heroPower, health = "Hunter", "Rexxar", SteadyShot, 30
	name_CN = "雷克萨"
	index = "LEGACY"

class Valeera(Hero):
	Class, name, heroPower, health = "Rogue", "Valeera", DaggerMastery, 30
	name_CN = "瓦莉拉"
	index = "LEGACY"

class Malfurion(Hero):
	Class, name, heroPower, health = "Druid", "Malfurion", Shapeshift, 30
	name_CN = "玛法里奥"
	index = "LEGACY"

class Garrosh(Hero):
	Class, name, heroPower, health = "Warrior", "Garrosh", ArmorUp, 30
	name_CN = "加尔鲁什"
	index = "LEGACY"

class Uther(Hero):
	Class, name, heroPower, health = "Paladin", "Uther", Reinforce, 30
	name_CN = "乌瑟尔"
	index = "LEGACY"

class Thrall(Hero):
	Class, name, heroPower, health = "Shaman", "Thrall", TotemicCall, 30
	name_CN = "萨尔"
	index = "LEGACY"

class Jaina(Hero):
	Class, name, heroPower, health = "Mage", "Jaina", Fireblast, 30
	name_CN = "吉安娜"
	index = "LEGACY"

class Anduin(Hero):
	Class, name, heroPower, health = "Priest", "Anduin", LesserHeal, 30
	name_CN = "安度因"
	index = "LEGACY"

class Guldan(Hero):
	Class, name, heroPower, health = "Warlock", "Gul'dan", LifeTap, 30
	name_CN = "古尔丹"
	index = "LEGACY"


class MurlocScout(Minion):
	Class, race, name = "Neutral", "Murloc", "Murloc Scout"
	mana, attack, health = 1, 1, 1
	index = "LEGACY~Neutral~Minion~1~1~1~Murloc~Murloc Scout~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "鱼人斥侯"
	
	
class IllidariInitiate(Minion):
	Class, race, name = "Demon Hunter", "", "Illidari Initiate"
	mana, attack, health = 1, 1, 1
	index = "LEGACY~Demon Hunter~Minion~1~1~1~~Illidari Initiate~Rush~Uncollectible"
	requireTarget, effects, description = False, "Rush", "Rush"
	name_CN = "伊利达雷新兵"


class ExcessMana(Spell):
	Class, school, name = "Druid", "", "Excess Mana"
	requireTarget, mana, effects = False, 0, ""
	index = "LEGACY~Druid~Spell~0~~Excess Mana~Uncollectible"
	description = "Draw a card"
	name_CN = "法力过剩"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.Hand_Deck.drawCard(self.ID)


class Claw(Spell):
	Class, school, name = "Druid", "", "Claw"
	requireTarget, mana, effects = False, 1, ""
	index = "LEGACY~Druid~Spell~1~~Claw"
	description = "Give your hero +2 Attack this turn. Gain 2 Armor"
	name_CN = "爪击"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.giveHeroAttackArmor(self.ID, attGain=2, armor=2, name=Claw)


class ArcaneMissiles(Spell):
	Class, school, name = "Mage", "Arcane", "Arcane Missiles"
	requireTarget, mana, effects = False, 1, ""
	index = "LEGACY~Mage~Spell~1~Arcane~Arcane Missiles"
	description = "Deal 3 damage randomly split among all enemies"
	name_CN = "奥术飞弹"
	def text(self): return self.calcDamage(3)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		ID = 3 - self.ID
		for i in range(self.calcDamage(3)):
			if objs := self.Game.charsAlive(ID): self.dealsDamage(numpyChoice(objs), 1)
			else: break


class WaterElemental_Basic(Minion):
	Class, race, name = "Mage", "Elemental", "Water Elemental"
	mana, attack, health = 4, 3, 6
	index = "LEGACY~Mage~Minion~4~3~6~Elemental~Water Elemental"
	requireTarget, effects, description = False, "", "Freeze any character damaged by this minion"
	name_CN = "水元素"
	trigBoard = Trig_WaterElemental


class Pyroblast(Spell):
	Class, school, name = "Mage", "Fire", "Pyroblast"
	requireTarget, mana, effects = True, 10, ""
	index = "EXPERT1~Mage~Spell~10~Fire~Pyroblast"
	description = "Deal 10 damage"
	name_CN = "炎爆术"
	def text(self): return self.calcDamage(10)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.dealsDamage(target, self.calcDamage(10))
		return target


class LightsJustice(Weapon):
	Class, name, description = "Paladin", "Light's Justice", ""
	mana, attack, durability, effects = 1, 1, 4, ""
	index = "LEGACY~Paladin~Weapon~1~1~4~Light's Justice"
	name_CN = "圣光的正义"
	
	
class TruesilverChampion(Weapon):
	Class, name, description = "Paladin", "Truesilver Champion", "Whenever your hero attacks, restore 2 Health to it"
	mana, attack, durability, effects = 4, 4, 2, ""
	index = "LEGACY~Paladin~Weapon~4~4~2~Truesilver Champion"
	name_CN = "真银圣剑"
	trigBoard = Trig_TruesilverChampion	
	def text(self): return self.calcHeal(2)
	

class PatientAssassin(Minion):
	Class, race, name = "Rogue", "", "Patient Assassin"
	mana, attack, health = 2, 1, 2
	index = "EXPERT1~Rogue~Minion~2~1~2~~Patient Assassin~Poisonous~Stealth"
	requireTarget, effects, description = False, "Stealth,Poisonous", "Stealth, Poisonous"
	name_CN = "耐心的刺客"


class Voidwalker(Minion):
	Class, race, name = "Warlock", "", "Voidwalker"
	mana, attack, health = 1, 1, 3
	index = "LEGACY~Warlock~Minion~1~1~3~~Voidwalker~Taunt"
	requireTarget, effects, description = False, "Taunt", "Taunt"
	name_CN = "虚空行者"


class FieryWarAxe_Basic(Weapon):
	Class, name, description = "Warrior", "Fiery War Axe", ""
	mana, attack, durability, effects = 3, 3, 2, ""
	index = "LEGACY~Warrior~Weapon~3~3~2~Fiery War Axe"
	name_CN = "炽炎战斧"
	

class Bananas(Spell):
	Class, school, name = "Neutral", "", "Bananas"
	requireTarget, mana, effects = True, 1, ""
	index = "EXPERT1~Neutral~Spell~1~~Bananas~Uncollectible"
	description = "Give a minion +1/+1"
	name_CN = "香蕉"
	def available(self):
		return self.selectableMinionExists()
	
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.giveEnchant(target, 1, 1, name=Bananas)
		return target


class DamagedGolem(Minion):
	Class, race, name = "Neutral", "Mech", "Damaged Golem"
	mana, attack, health = 1, 2, 1
	index = "EXPERT1~Neutral~Minion~1~2~1~Mech~Damaged Golem~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "损坏的傀儡"
	
	
class Skeleton(Minion):
	Class, race, name = "Neutral", "", "Skeleton"
	mana, attack, health = 1, 1, 1
	index = "ICECROWN~Neutral~Minion~1~1~1~~Skeleton~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "骷髅"


class VioletApprentice(Minion):
	Class, race, name = "Neutral", "", "Violet Apprentice"
	mana, attack, health = 1, 1, 1
	index = "EXPERT1~Neutral~Minion~1~1~1~~Violet Apprentice~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "紫罗兰学徒"


class Whelp(Minion):
	Class, race, name = "Neutral", "Dragon", "Whelp"
	mana, attack, health = 1, 1, 1
	index = "EXPERT1~Neutral~Minion~1~1~1~Dragon~Whelp~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "雏龙"


class BaineBloodhoof(Minion):
	Class, race, name = "Neutral", "", "Baine Bloodhoof"
	mana, attack, health = 5, 5, 5
	index = "EXPERT1~Neutral~Minion~5~5~5~~Baine Bloodhoof~Legendary~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "贝恩·血蹄"


class Dream(Spell):
	Class, school, name = "DreamCard", "Nature", "Dream"
	requireTarget, mana, effects = True, 1, ""
	index = "EXPERT1~DreamCard~Spell~1~Nature~Dream~Uncollectible"
	description = "Return an enemy minion to its owner's hand"
	name_CN = "梦境"
	def available(self):
		return self.selectableEnemyMinionExists()
	
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard and target.ID != self.ID
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.Game.returnObj2Hand(target)
		return target


class Nightmare(Spell):
	Class, school, name = "DreamCard", "Shadow", "Nightmare"
	requireTarget, mana, effects = True, 0, ""
	index = "EXPERT1~DreamCard~Spell~0~Shadow~Nightmare~Uncollectible"
	description = "Give a minion +4/+4. At the start of your next turn, destroy it."
	name_CN = "噩梦"
	def available(self):
		return self.selectableMinionExists()
	
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and target.onBoard:
			self.giveEnchant(target, 4, 4, trig=(Trig_Nightmare_1 if self.ID else Trig_Nightmare_2), name=Nightmare)
		return target


class YseraAwakens(Spell):
	Class, school, name = "DreamCard", "Nature", "Ysera Awakens"
	requireTarget, mana, effects = False, 3, ""
	index = "EXPERT1~DreamCard~Spell~3~Nature~Ysera Awakens~Uncollectible"
	description = "Deal 5 damage to all minions except Ysera"
	name_CN = "伊瑟拉苏醒"
	def text(self): return self.calcDamage(5)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = self.calcDamage(5)
		targets = [minion for minion in self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2) if "Ysera" not in minion.name]
		self.AOE_Damage(targets, [damage] *len(targets))


class LaughingSister(Minion):
	Class, race, name = "DreamCard", "", "Laughing Sister"
	mana, attack, health = 2, 3, 5
	index = "EXPERT1~DreamCard~Minion~2~3~5~~Laughing Sister~Uncollectible"
	requireTarget, effects, description = False, "Evasive", "Can't targeted by spells or Hero Powers"
	name_CN = "欢笑的姐妹"
	

class EmeraldDrake(Minion):
	Class, race, name = "DreamCard", "Dragon", "Emerald Drake"
	mana, attack, health = 4, 7, 6
	index = "EXPERT1~DreamCard~Minion~4~7~6~Dragon~Emerald Drake~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "翡翠幼龙"

DreamCards = [Dream, Nightmare, YseraAwakens, LaughingSister, EmeraldDrake]


class LeaderofthePack(Spell):
	Class, school, name = "Druid", "", "Leader of the Pack"
	requireTarget, mana, effects = False, 2, ""
	index = "EXPERT1~Druid~Spell~2~~Leader of the Pack~Uncollectible"
	description = "Give your minions +1/+1"
	name_CN = "兽群领袖"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.AOE_GiveEnchant(self.Game.minionsonBoard(self.ID), 1, 1, name=LeaderofthePack)

class SummonaPanther(Spell):
	Class, school, name = "Druid", "", "Summon a Panther"
	requireTarget, mana, effects = False, 2, ""
	index = "EXPERT1~Druid~Spell~2~~Summon a Panther~Uncollectible"
	description = "Summon a 3/2 Panther"
	name_CN = "召唤猎豹"
	def available(self):
		return self.Game.space(self.ID) > 0
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon(Panther(self.Game, self.ID))


class Panther(Minion):
	Class, race, name = "Druid", "Beast", "Panther"
	mana, attack, health = 2, 3, 2
	index = "EXPERT1~Druid~Minion~2~3~2~Beast~Panther~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "猎豹"


class Treant_Classic(Minion):
	Class, race, name = "Druid", "", "Treant"
	mana, attack, health = 2, 2, 2
	index = "EXPERT1~Druid~Minion~2~2~2~~Treant~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "树人"


class Treant_Classic_Taunt(Minion):
	Class, race, name = "Druid", "", "Treant"
	mana, attack, health = 2, 2, 2
	index = "EXPERT1~Druid~Minion~2~2~2~~Treant~Taunt~Uncollectible"
	requireTarget, effects, description = False, "Taunt", "Taunt"
	name_CN = "树人"


class EvolveSpines(Spell):
	Class, school, name = "Druid", "", "Evolve Spines"
	requireTarget, mana, effects = False, 3, ""
	index = "OG~Druid~Spell~3~~Evolve Spines~Uncollectible"
	description = "Give your hero +4 Attack this turn"
	name_CN = "脊刺异变"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.giveHeroAttackArmor(self.ID, attGain=4, name=EvolveScales)


class EvolveScales(Spell):
	Class, school, name = "Druid", "", "Evolve Scales"
	requireTarget, mana, effects = False, 3, ""
	index = "OG~Druid~Spell~3~~Evolve Scales~Uncollectible"
	description = "Gain 8 Armor"
	name_CN = "鳞甲异变"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.giveHeroAttackArmor(self.ID, armor=8)


class DruidoftheClaw_Charge(Minion):
	Class, race, name = "Druid", "Beast", "Druid of the Claw"
	mana, attack, health = 5, 5, 4
	index = "EXPERT1~Druid~Minion~5~5~4~Beast~Druid of the Claw~Rush~Uncollectible"
	requireTarget, effects, description = False, "Rush", "Rush"
	name_CN = "利爪德鲁伊"


class DruidoftheClaw_Taunt(Minion):
	Class, race, name = "Druid", "Beast", "Druid of the Claw"
	mana, attack, health = 5, 5, 6
	index = "EXPERT1~Druid~Minion~5~5~6~Beast~Druid of the Claw~Taunt~Uncollectible"
	requireTarget, effects, description = False, "Taunt", "Taunt"
	name_CN = "利爪德鲁伊"


class DruidoftheClaw_Both(Minion):
	Class, race, name = "Druid", "Beast", "Druid of the Claw"
	mana, attack, health = 5, 5, 6
	index = "EXPERT1~Druid~Minion~5~5~6~Beast~Druid of the Claw~Taunt~Rush~Uncollectible"
	requireTarget, effects, description = False, "Taunt,Rush", "Taunt, Rush"
	name_CN = "利爪德鲁伊"


class RampantGrowth(Spell):
	Class, school, name = "Druid", "Nature", "Rampant Growth"
	requireTarget, mana, effects = False, 6, ""
	index = "EXPERT1~Druid~Spell~6~Nature~Rampant Growth~Uncollectible"
	description = "Gain 2 Mana Crystals"
	name_CN = "快速生长"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.Manas.gainManaCrystal(2, self.ID)


class Enrich(Spell):
	Class, school, name = "Druid", "Nature", "Enrich"
	requireTarget, mana, effects = False, 6, ""
	index = "EXPERT1~Druid~Spell~6~Nature~Enrich~Uncollectible"
	description = "Draw 3 cards"
	name_CN = "摄取养分"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.Hand_Deck.drawCard(self.ID)
		self.Game.Hand_Deck.drawCard(self.ID)
		self.Game.Hand_Deck.drawCard(self.ID)


class Snake(Minion):
	Class, race, name = "Hunter", "Beast", "Snake"
	mana, attack, health = 1, 1, 1
	index = "EXPERT1~Hunter~Minion~1~1~1~Beast~Snake~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "蛇"


class Huffer(Minion):
	Class, race, name = "Hunter", "Beast", "Huffer"
	mana, attack, health = 3, 4, 2
	index = "LEGACY~Hunter~Minion~3~4~2~Beast~Huffer~Charge~Uncollectible"
	requireTarget, effects, description = False, "Charge", "Charge"
	name_CN = "霍弗"


class Leokk(Minion):
	Class, race, name = "Hunter", "Beast", "Leokk"
	mana, attack, health = 3, 2, 4
	index = "LEGACY~Hunter~Minion~3~2~4~Beast~Leokk~Uncollectible"
	requireTarget, effects, description = False, "", "Your other minions have +1 Attack"
	name_CN = "雷欧克"
	aura = Aura_Leokk


class Misha(Minion):
	Class, race, name = "Hunter", "Beast", "Misha"
	mana, attack, health = 3, 4, 4
	index = "LEGACY~Hunter~Minion~3~4~4~Beast~Misha~Taunt~Uncollectible"
	requireTarget, effects, description = False, "Taunt", "Taunt"
	name_CN = "米莎"


class Hyena_Classic(Minion):
	Class, race, name = "Hunter", "Beast", "Hyena"
	mana, attack, health = 2, 2, 2
	index = "EXPERT1~Hunter~Minion~2~2~2~Beast~Hyena~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "土狼"


class ManaWyrm(Minion):
	Class, race, name = "Mage", "", "Mana Wyrm"
	mana, attack, health = 1, 1, 2
	index = "EXPERT1~Mage~Minion~1~1~2~~Mana Wyrm"
	requireTarget, effects, description = False, "", "Whenever you cast a spell, gain 1 Attack"
	name_CN = "法力浮龙"
	trigBoard = Trig_ManaWyrm


class Defender(Minion):
	Class, race, name = "Paladin", "", "Defender"
	mana, attack, health = 1, 2, 1
	index = "EXPERT1~Paladin~Minion~1~2~1~~Defender~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "防御者"


class Ashbringer(Weapon):
	Class, name, description = "Paladin", "Ashbringer", ""
	mana, attack, durability, effects = 5, 5, 3, ""
	index = "EXPERT1~Paladin~Weapon~5~5~3~Ashbringer~Legendary~Uncollectible"
	name_CN = "灰烬使者"


class SpiritWolf(Minion):
	Class, race, name = "Shaman", "", "Spirit Wolf"
	mana, attack, health = 2, 2, 3
	index = "EXPERT1~Shaman~Minion~2~2~3~~Spirit Wolf~Taunt~Uncollectible"
	requireTarget, effects, description = False, "Taunt", "Taunt"
	name_CN = "幽灵狼"


class Frog(Minion):
	Class, race, name = "Neutral", "Beast", "Frog"
	mana, attack, health = 0, 0, 1
	index = "LEGACY~Neutral~Minion~0~0~1~Beast~Frog~Taunt~Uncollectible"
	requireTarget, effects, description = False, "Taunt", "Taunt"
	name_CN = "青蛙"


class Shadowbeast(Minion):
	Class, race, name = "Warlock", "", "Shadowbeast"
	mana, attack, health = 1, 1, 1
	index = "OG~Warlock~Minion~1~1~1~~Shadowbeast~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "暗影兽"


class BloodFury(Weapon):
	Class, name, description = "Warlock", "Blood Fury", ""
	mana, attack, durability, effects = 3, 3, 8, ""
	index = "EXPERT1~Warlock~Weapon~3~3~8~Blood Fury~Uncollectible"
	name_CN = "血怒"
	
	
class Infernal(Minion):
	Class, race, name = "Warlock", "Demon", "Infernal"
	mana, attack, health = 6, 6, 6
	index = "EXPERT1~Warlock~Minion~6~6~6~Demon~Infernal~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "地狱火"


class Nerubian(Minion):
	Class, race, name = "Neutral", "", "Nerubian"
	mana, attack, health = 4, 4, 4
	index = "NAXX~Neutral~Minion~4~4~4~~Nerubian~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "蛛魔"


class BoomBot(Minion):
	Class, race, name = "Neutral", "Mech", "Boom Bot"
	mana, attack, health = 1, 1, 1
	index = "GVG~Neutral~Minion~1~1~1~Mech~Boom Bot~Deathrattle~Uncollectible"
	requireTarget, effects, description = False, "", "Deathrattle: Deal 1~4 damage to a random enemy"
	deathrattle = Death_BoomBot


class GoldenKobold(Minion):
	Class, race, name = "Neutral", "", "Golden Kobold"
	mana, attack, health = 3, 6, 6
	index = "LOOTAPALOOZA~Neutral~Minion~3~6~6~~Golden Kobold~Taunt~Battlecry~Legendary~Uncollectible"
	requireTarget, effects, description = False, "Taunt", "Taunt. Battlecry: Replace your hand with Legendary minions"
	name_CN = "黄金狗头人"
	poolIdentifier = "Legendary Minions"
	@classmethod
	def generatePool(cls, pools):
		return "Legendary Minions", pools.LegendaryMinions
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		hand = numpyChoice(self.rngPool("Legendary Minions"), len(self.Game.Hand_Deck.hands[self.ID]), replace=True)
		if hand:
			self.Game.Hand_Deck.extractfromHand(None, self.ID, getAll=True)
			self.addCardtoHand(hand, self.ID)
		

class TolinsGoblet(Spell):
	Class, school, name = "Neutral", "", "Tolin's Goblet"
	requireTarget, mana, effects = False, 3, ""
	index = "LOOTAPALOOZA~Neutral~Spell~3~~Tolin's Goblet~Uncollectible"
	description = "Draw a card. Fill your hand with copies of it"
	name_CN = "托林的酒杯"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		card, mana, entersHand = self.Game.Hand_Deck.drawCard(self.ID)
		if entersHand and self.Game.Hand_Deck.handNotFull(self.ID):
			copies = [card.selfCopy(self.ID, self) for i in range(self.Game.Hand_Deck.spaceinHand(self.ID))]
			self.addCardtoHand(copies, self.ID)
		

class WondrousWand(Spell):
	Class, school, name = "Neutral", "", "Wondrous Wand"
	requireTarget, mana, effects = False, 3, ""
	index = "LOOTAPALOOZA~Neutral~Spell~3~~Wondrous Wand~Uncollectible"
	description = "Draw 3 cards. Reduce their costs to (0)"
	name_CN = "奇迹之杖"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for _ in (0, 1, 2):
			card, mana, entersHand = self.Game.Hand_Deck.drawCard(self.ID)
			if entersHand: ManaMod(card, to=0).applies()
			

class ZarogsCrown(Spell):
	Class, school, name = "Neutral", "", "Zarog's Crown"
	requireTarget, mana, effects = False, 3, ""
	index = "LOOTAPALOOZA~Neutral~Spell~3~~Zarog's Crown~Uncollectible"
	description = "Discover a Legendary minion. Summon two copies of it"
	name_CN = "扎罗格的王冠"
	poolIdentifier = "Legendary Minions as Druid to Summon"
	@classmethod
	def generatePool(cls, pools):
		classCards = {s : [] for s in pools.ClassesandNeutral}
		for card in pools.LegendaryMinions:
			for Class in card.Class.split(','):
				classCards[Class].append(card)
		return ["Legendary Minions as %s to Summon"%Class for Class in pools.Classes], \
			[classCards[Class]+classCards["Neutral"] for Class in pools.Classes]
			
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.space(self.ID) > 0:
			self.discoverandGenerate(ZarogsCrown, comment, lambda : self.rngPool("Legendary Minions as %s to Summon" % classforDiscover(self)))
		
	def discoverDecided(self, option, case, info_RNGSync=None, info_GUISync=None):
		self.handleDiscoverGeneratedCard(option, case, info_RNGSync, info_GUISync,
										 func=lambda cardType, card: self.summon([cardType(self.Game, self.ID) for _ in (0, 1)])
										 )


class Bomb(Spell):
	Class, school, name = "Neutral", "", "Bomb"
	requireTarget, mana, effects = False, 5, ""
	index = "BOOMSDAY~Neutral~Spell~5~~Bomb~Casts When Drawn~Uncollectible"
	description = "Casts When Drawn. Deal 5 damage to your hero"
	name_CN = "炸弹"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.dealsDamage(self.Game.heroes[self.ID], self.calcDamage(5))


class EtherealLackey(Minion):
	Class, race, name = "Neutral", "", "Ethereal Lackey"
	mana, attack, health = 1, 1, 1
	index = "DALARAN~Neutral~Minion~1~1~1~~Ethereal Lackey~Battlecry~Uncollectible"
	requireTarget, effects, description = False, "", "Battlecry: Discover a spell"
	name_CN = "虚灵跟班"
	poolIdentifier = "Druid Spells"
	@classmethod
	def generatePool(cls, pools):
		return [Class + " Spells" for Class in pools.Classes], \
			   [[card for card in pools.ClassCards[Class] if card.category == "Spell"] for Class in pools.Classes]

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverandGenerate(EtherealLackey, comment, lambda : self.rngPool(classforDiscover(self) + " Spells"))


class FacelessLackey(Minion):
	Class, race, name = "Neutral", "", "Faceless Lackey"
	mana, attack, health = 1, 1, 1
	index = "DALARAN~Neutral~Minion~1~1~1~~Faceless Lackey~Battlecry~Uncollectible"
	requireTarget, effects, description = False, "", "Battlecry: Summon a 2-Cost minion"
	name_CN = "无面跟班"
	poolIdentifier = "2-Cost Minions to Summon"
	@classmethod
	def generatePool(cls, pools):
		return "2-Cost Minions to Summon", pools.MinionsofCost[2]

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon(self.rngPool("2-Cost Minions to Summon")(self.Game, self.ID))


class GoblinLackey(Minion):
	Class, race, name = "Neutral", "", "Goblin Lackey"
	mana, attack, health = 1, 1, 1
	index = "DALARAN~Neutral~Minion~1~1~1~~Goblin Lackey~Battlecry~Uncollectible"
	requireTarget, effects, description = True, "", "Battlecry: Give a friendly minion +1 Attack and Rush"
	name_CN = "地精跟班"
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()

	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.ID == self.ID and target != self and target.onBoard

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.giveEnchant(target, 1, 0, effGain="Rush", name=GoblinLackey)
		return target


class KoboldLackey(Minion):
	Class, race, name = "Neutral", "", "Kobold Lackey"
	mana, attack, health = 1, 1, 1
	index = "DALARAN~Neutral~Minion~1~1~1~~Kobold Lackey~Battlecry~Uncollectible"
	requireTarget, effects, description = True, "", "Battlecry: Deal 2 damage"
	name_CN = "狗头人跟班"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.dealsDamage(target, 2)
		return target


class WitchyLackey(Minion):
	Class, race, name = "Neutral", "", "Witchy Lackey"
	mana, attack, health = 1, 1, 1
	index = "DALARAN~Neutral~Minion~1~1~1~~Witchy Lackey~Battlecry~Uncollectible"
	requireTarget, effects, description = True, "", "Battlecry: Transform a friendly minion into one that costs (1) more"
	name_CN = "女巫跟班"
	poolIdentifier = "1-Cost Minions to Summon"
	@classmethod
	def generatePool(cls, pools):
		return ["%d-Cost Minions to Summon" % cost for cost in pools.MinionsofCost], \
			   list(pools.MinionsofCost.values())
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()

	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.ID == self.ID and target != self and target.onBoard

	# 不知道如果目标随从被返回我方手牌会有什么结算，可能是在手牌中被进化
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: target = self.transform(target, self.newEvolved(type(target).mana, by=1, ID=self.ID))
		return target


class TitanicLackey(Minion):
	Class, race, name = "Neutral", "", "Titanic Lackey"
	mana, attack, health = 1, 1, 1
	index = "ULDUM~Neutral~Minion~1~1~1~~Titanic Lackey~Battlecry~Uncollectible"
	requireTarget, effects, description = True, "", "Battlecry: Give a friendly minion +2 Health"
	name_CN = "泰坦跟班"
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists(choice)

	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.ID == self.ID and target != self and target.onBoard

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.giveEnchant(target, 0, 2, effGain="Taunt", name=TitanicLackey)
		return target


class DraconicLackey(Minion):
	Class, race, name = "Neutral", "", "Draconic Lackey"
	mana, attack, health = 1, 1, 1
	index = "DRAGONS~Neutral~Minion~1~1~1~~Draconic Lackey~Battlecry~Uncollectible"
	requireTarget, effects, description = False, "", "Battlecry: Discover a Dragon"
	name_CN = "龙族跟班"
	poolIdentifier = "Dragons as Druid"
	@classmethod
	def generatePool(cls, pools):
		classCards = {s: [] for s in pools.ClassesandNeutral}
		for card in pools.MinionswithRace["Dragon"]:
			for Class in card.Class.split(','):
				classCards[Class].append(card)
		return ["Dragons as " + Class for Class in pools.Classes], \
			   [classCards[Class] + classCards["Neutral"] for Class in pools.Classes]

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverandGenerate(DraconicLackey, comment, lambda : self.rngPool("Dragons as " + classforDiscover(self)))

Lackeys = [DraconicLackey, EtherealLackey, FacelessLackey, GoblinLackey, KoboldLackey, TitanicLackey, WitchyLackey]


class DeadlyAdventurer(Minion):
	Class, race, name = "Neutral", "", "Deadly Adventurer"
	mana, attack, health = 2, 2, 2
	index = "THE_BARRENS~Neutral~Minion~2~2~2~~Deadly Adventurer~Poisonous~Uncollectible"
	requireTarget, effects, description = False, "Poisonous", "Poisonous"
	name_CN = "致命的冒险者"

class BurlyAdventurer(Minion):
	Class, race, name = "Neutral", "", "Burly Adventurer"
	mana, attack, health = 2, 2, 2
	index = "THE_BARRENS~Neutral~Minion~2~2~2~~Burly Adventurer~Taunt~Uncollectible"
	requireTarget, effects, description = False, "Taunt", "Taunt"
	name_CN = "健壮的冒险者"

class DevoutAdventurer(Minion):
	Class, race, name = "Neutral", "", "Devout Adventurer"
	mana, attack, health = 2, 2, 2
	index = "THE_BARRENS~Neutral~Minion~2~2~2~~Devout Adventurer~Divine Shield~Uncollectible"
	requireTarget, effects, description = False, "Divine Shield", "Divine Shield"
	name_CN = "虔诚的冒险者"

class RelentlessAdventurer(Minion):
	Class, race, name = "Neutral", "", "Relentless Adventurer"
	mana, attack, health = 2, 2, 2
	index = "THE_BARRENS~Neutral~Minion~2~2~2~~Relentless Adventurer~Windfury~Uncollectible"
	requireTarget, effects, description = False, "Windfury", "Windfury"
	name_CN = "无情的冒险者"

class ArcaneAdventurer(Minion):
	Class, race, name = "Neutral", "", "Arcane Adventurer"
	mana, attack, health = 2, 2, 2
	index = "THE_BARRENS~Neutral~Minion~2~2~2~~Arcane Adventurer~Spell Damage~Uncollectible"
	requireTarget, effects, description = False, "Spell Damage", "Spell Damage+1"
	name_CN = "奥术冒险者"

class SneakyAdventurer(Minion):
	Class, race, name = "Neutral", "", "Sneaky Adventurer"
	mana, attack, health = 2, 2, 2
	index = "THE_BARRENS~Neutral~Minion~2~2~2~~Sneaky Adventurer~Stealth~Uncollectible"
	requireTarget, effects, description = False, "Stealth", "Stealth"
	name_CN = "鬼祟的冒险者"

class VitalAdventurer(Minion):
	Class, race, name = "Neutral", "", "Vital Adventurer"
	mana, attack, health = 2, 2, 2
	index = "THE_BARRENS~Neutral~Minion~2~2~2~~Vital Adventurer~Lifesteal~Uncollectible"
	requireTarget, effects, description = False, "Lifesteal", "Lifesteal"
	name_CN = "活跃的冒险者"

class SwiftAdventurer(Minion):
	Class, race, name = "Neutral", "", "Swift Adventurer"
	mana, attack, health = 2, 2, 2
	index = "THE_BARRENS~Neutral~Minion~2~2~2~~Swift Adventurer~Rush~Uncollectible"
	requireTarget, effects, description = False, "Rush", "Rush"
	name_CN = "迅捷的冒险者"

Adventurers = [DeadlyAdventurer, BurlyAdventurer, DevoutAdventurer, RelentlessAdventurer,
			   ArcaneAdventurer, SneakyAdventurer, VitalAdventurer, SwiftAdventurer]


AcrossPacks_Cards = [
	TheCoin, SilverHandRecruit, WickedKnife, PoisonedDagger, SearingTotem, StoneclawTotem, HealingTotem, StrengthTotem,
	DemonClaws, DemonsBite, Shapeshift, DireShapeshift, SteadyShot, BallistaShot, Fireblast, FireblastRank2, Reinforce,
	TheSilverHand, LesserHeal, Heal, DaggerMastery, PoisonedDaggers, TotemicCall, TotemicSlam, LifeTap, SoulTap, ArmorUp, TankUp,
	Illidan, Rexxar, Valeera, Malfurion, Garrosh, Uther, Thrall, Jaina, Anduin, Guldan,

	MurlocScout, IllidariInitiate, ExcessMana, Claw, ArcaneMissiles, WaterElemental_Basic, Pyroblast, LightsJustice,
	TruesilverChampion, PatientAssassin, Voidwalker, FieryWarAxe_Basic, Bananas, DamagedGolem, Skeleton, VioletApprentice,
	Whelp, BaineBloodhoof, Dream, Nightmare, YseraAwakens, LaughingSister, EmeraldDrake, LeaderofthePack, SummonaPanther,
	Panther, Treant_Classic, Treant_Classic_Taunt, EvolveSpines, EvolveScales, DruidoftheClaw_Charge, DruidoftheClaw_Taunt,
	DruidoftheClaw_Both, RampantGrowth, Enrich, Snake, Huffer, Leokk, Misha, Hyena_Classic, ManaWyrm, Defender, Ashbringer,
	SpiritWolf, Frog, Shadowbeast, BloodFury, Infernal, Nerubian, BoomBot, GoldenKobold, TolinsGoblet, WondrousWand,
	ZarogsCrown, Bomb,
	#Lackeys
	EtherealLackey, FacelessLackey, GoblinLackey, KoboldLackey, WitchyLackey, TitanicLackey, DraconicLackey,
	#Adventurers from Barrens
	DeadlyAdventurer, BurlyAdventurer, DevoutAdventurer, RelentlessAdventurer, ArcaneAdventurer, SneakyAdventurer, VitalAdventurer, SwiftAdventurer,
]

AcrossPacks_Cards_Collectible = [
		#Basic&Upgraded hero powers
		DemonClaws, DemonsBite, Shapeshift, DireShapeshift, SteadyShot, BallistaShot, Fireblast, FireblastRank2, Reinforce,
		TheSilverHand, LesserHeal, Heal, DaggerMastery, PoisonedDaggers, TotemicCall, TotemicSlam, LifeTap, SoulTap, ArmorUp,
		TankUp,
		#Heroes
		Illidan, Rexxar, Valeera, Malfurion, Garrosh, Uther, Thrall, Jaina, Anduin, Guldan,
]

TrigsDeaths_AcrossPacks = {Death_BoomBot: (BoomBot, "Deathrattle: Deal 1~4 damage to a random enemy"),
							Trig_Nightmare_1: (Nightmare, "Die at the start of player 1's turn"),
							Trig_Nightmare_2: (Nightmare, "Die at the start of player 2's turn"),
							}