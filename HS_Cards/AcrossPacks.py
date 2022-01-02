from Parts.CardTypes import *
from Parts.TrigsAuras import *


class Aura_Leokk(Aura_AlwaysOn):
	attGain = 1
	
	
class Death_BoomBot(Deathrattle):
	description = "Deathrattle: Deal 1~4 damage to a random enemy"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		if objs := (kpr := self.keeper).Game.charsAlive(3-kpr.ID):
			kpr.dealsDamage(numpyChoice(objs), numpyRandint(1, 5))
		
	
class Trig_HealingTotem(TrigBoard):
	signals = ("TurnEnds",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).heals(kpr.Game.minionsonBoard(kpr.ID), kpr.calcHeal(1))
		
	
class Trig_StrengthTotem(TrigBoard):
	signals = ("TurnEnds",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		if minions := kpr.Game.minionsonBoard(kpr.ID, exclude=kpr):
			kpr.giveEnchant(numpyChoice(minions), statEnchant=Enchantment_Exclusive(StrengthTotem, 1, 0))
		
	
class Trig_Nightmare(TrigBoard):
	signals, description = ("TurnStarts",), "Die at the start of caster's turn"
	def __init__(self, keeper, ID=1):
		super().__init__(keeper)
		self.memory = ID
		
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return self.keeper.onBoard and ID == self.memory
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).Game.kill(kpr, kpr)
		
	
class Trig_ManaWyrm(TrigBoard):
	signals = ("CardPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return comment == "Spell" and ID == kpr.ID and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).giveEnchant(kpr, statEnchant=Enchantment_Exclusive(ManaWyrm, 1, 0))
		
	
class TheCoin(Spell):
	Class, school, name = "Neutral", "", "The Coin"
	numTargets, mana, Effects = 0, 0, ""
	index = "LEGACY~Uncollectible"
	description = "Gain 1 mana crystal for this turn."
	name_CN = "幸运币"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.Game.Manas.gainTempManaCrystal(1, ID=self.ID)
		
	
class SilverHandRecruit(Minion):
	Class, race, name = "Paladin", "", "Silver Hand Recruit"
	mana, attack, health = 1, 1, 1
	index = "LEGACY~Uncollectible"
	numTargets, Effects, description = 0, "", ""
	name_CN = "白银之手新兵"
	
	
class WickedKnife(Weapon):
	Class, name, description = "Rogue", "Wicked Knife", ""
	mana, attack, durability, Effects = 1, 1, 2, ""
	index = "LEGACY~Uncollectible"
	name_CN = "邪恶短刀"
	
	
class PoisonedDagger(Weapon):
	Class, name, description = "Rogue", "Poisoned Dagger", ""
	mana, attack, durability, Effects = 1, 2, 2, ""
	index = "TGT~Uncollectible"
	name_CN = "浸毒匕首"
	
	
class SearingTotem(Minion):
	Class, race, name = "Shaman", "Totem", "Searing Totem"
	mana, attack, health = 1, 1, 1
	index = "LEGACY~Uncollectible"
	numTargets, Effects, description = 0, "", ""
	name_CN = "灼热图腾"
	
	
class StoneclawTotem(Minion):
	Class, race, name = "Shaman", "Totem", "Stoneclaw Totem"
	mana, attack, health = 1, 0, 2
	index = "LEGACY~Uncollectible"
	numTargets, Effects, description = 0, "Taunt", "Taunt"
	name_CN = "石爪图腾"
	
	
class HealingTotem(Minion):
	Class, race, name = "Shaman", "Totem", "Healing Totem"
	mana, attack, health = 1, 0, 2
	index = "LEGACY~Uncollectible"
	numTargets, Effects, description = 0, "", "At the end of your turn, restore 1 health to all friendly minions"
	name_CN = "治疗图腾"
	trigBoard = Trig_HealingTotem
	def text(self): return self.calcHeal(1)
		
	
class StrengthTotem(Minion):
	Class, race, name = "Shaman", "Totem", "Strength Totem"
	mana, attack, health = 1, 0, 2
	index = "LEGACY~Uncollectible"
	numTargets, Effects, description = 0, "", "At the end of your turn, give another friendly minion +1 Attack"
	name_CN = "力量图腾"
	trigBoard = Trig_StrengthTotem
	
	
class DemonsBite(Power):
	mana, name, numTargets = 1, "Demon's Bite", 0
	description = "+2 Attack this turn"
	name_CN = "恶魔之咬"
	index = "Upgraded Hero Power"
	def effect(self, target=(), choice=0, comment=''):
		self.giveHeroAttackArmor(self.ID, attGain=2, source=DemonsBite)
		
	
class DemonClaws(Power):
	mana, name, numTargets = 1, "Demon Claws", 0
	description = "+1 Attack this turn"
	name_CN = "恶魔之爪"
	index = "Basic Hero Power"
	upgrade = DemonsBite
	def effect(self, target=(), choice=0, comment=''):
		self.giveHeroAttackArmor(self.ID, attGain=1, source=DemonClaws)
		
	
class DireShapeshift(Power):
	mana, name, numTargets = 2, "Dire Shapeshift", 0
	description = "+2 Attack this turn. +2 Armor"
	name_CN = "恐怖变形"
	index = "Upgraded Hero Power"
	def effect(self, target=(), choice=0, comment=''):
		self.giveHeroAttackArmor(self.ID, attGain=2, armor=2, source=DireShapeshift)
		
	
class Shapeshift(Power):
	mana, name, numTargets = 2, "Shapeshift", 0
	description = "+1 Attack this turn. +1 Armor"
	name_CN = "变形"
	index = "Basic Hero Power"
	upgrade = DireShapeshift
	def effect(self, target=(), choice=0, comment=''):
		self.giveHeroAttackArmor(self.ID, attGain=1, armor=1, source=Shapeshift)
		
	
class BallistaShot(Power):
	name = "Ballista Shot"
	description = "Deal 3 damage to the enemy hero"
	name_CN = "弩炮射击"
	index = "Upgraded Hero Power"
	@classmethod
	def panda_ShootArrow(cls, GUI, power, target):
		x_0, y_0, z_0 = power.btn.np.getPos()
		x_1, y_1, z_1 = target.btn.np.getPos()
		degree = GUI.getDegreeDistance_fromCoors(x_0, y_0, x_1, y_1)[0]
		arrow = GUI.loadaRetexturedModel("Models\\ForCards\\HunterArrow.glb", "Models\\ForCards\\HunterArrow.png",
										 hpr=(degree, 10, 0))
		seq_Holder = GUI.seqHolder[-1]
		seq_Holder.append(GUI.LERP_PosHpr(arrow, duration=0.05, startPos=(x_0, y_0, z_0),
										  pos=((x_0 + x_1) / 2, (y_0 + y_1) / 2, z_1 + 0.2), hpr=(degree, 0, 0)))
		seq_Holder.append(GUI.LERP_PosHpr(arrow, duration=0.05, pos=(x_1, y_1, z_1), hpr=(degree, -10, 0)))
		seq_Holder.append(GUI.FUNC(GUI.SEQUENCE(GUI.WAIT(0.2), GUI.FUNC(arrow.removeNode)).start))
		
	def dealsDmg(self): return True
		
	def likeSteadyShot(self): return True
		
	def numTargetsNeeded(self, choice=0):
		return 1 if self.effects["Can Target Minions"] > 0 or self.Game.rules[self.ID]["Power Can Target Minions"] > 0 else 0
		
	def targetCorrect(self, obj, choice=0, ith=0):
		if obj.onBoard:
			return obj.category == "Hero" or (obj.category == "Minion" and self.effects["Can Target Minions"] > 0
											  	or self.Game.rules[self.ID]["Power Can Target Minions"] > 0)
		return False
		
	def text(self): return self.calcDamage(3)
		
	def effect(self, target=(), choice=0, comment=''):
		if not target: target = (self.Game.heroes[3 - self.ID],)
		if GUI := self.Game.GUI:
			for obj in target:
				if obj.btn: BallistaShot.panda_ShootArrow(GUI, self, obj)
		self.dealsDamage(target, self.calcDamage(3))
		
	
class SteadyShot(BallistaShot):
	mana, name, numTargets = 2, "Steady Shot", 0
	description = "Deal 2 damage to the enemy hero"
	name_CN = "稳固射击"
	index = "Basic Hero Power"
	upgrade = BallistaShot
	def text(self): return self.calcDamage(2)
		
	def effect(self, target=(), choice=0, comment=''):
		if not target: target = (self.Game.heroes[3 - self.ID],)
		if GUI := self.Game.GUI:
			for obj in target:
				if obj.btn: BallistaShot.panda_ShootArrow(GUI, self, obj)
		self.dealsDamage(target, self.calcDamage(3))
		
	
class FireblastRank2(Power):
	mana, name, numTargets = 2, "Fireblast Rank 2", 1
	description = "Deal 2 damage"
	name_CN = "二级火焰冲击"
	index = "Upgraded Hero Power"
	def dealsDmg(self): return True
		
	def text(self): return self.calcDamage(2)
		
	def effect(self, target=(), choice=0, comment=''):
		self.dealsDamage(target, self.calcDamage(2))
		
	
class Fireblast(Power):
	mana, name, numTargets = 2, "Fireblast", 1
	description = "Deal 1 damage"
	name_CN = "火焰冲击"
	index = "Basic Hero Power"
	upgrade = FireblastRank2
	def dealsDmg(self): return True
		
	def text(self): return self.calcDamage(1)
		
	def effect(self, target=(), choice=0, comment=''):
		self.dealsDamage(target, self.calcDamage(1))
		
	
class TheSilverHand(Power):
	mana, name, numTargets = 2, "The Silver Hand", 0
	description = "Summon two 1/1 Silver Hand Recruits"
	name_CN = "白银之手"
	index = "Upgraded Hero Power"
	def available(self):
		return not self.chancesUsedUp() and self.Game.space(self.ID)
		
	def effect(self, target=(), choice=0, comment=''):
		self.summon([SilverHandRecruit(self.Game, self.ID) for _ in (0, 1)])
		
	
class Reinforce(Power):
	mana, name, numTargets = 2, "Reinforce", 0
	description = "Summon a 1/1 Silver Hand Recruit"
	name_CN = "增援"
	index = "Basic Hero Power"
	upgrade = TheSilverHand
	def available(self):
		return not self.chancesUsedUp() and self.Game.space(self.ID)
		
	def effect(self, target=(), choice=0, comment=''):
		self.summon(SilverHandRecruit(self.Game, self.ID))
		
	
class Heal(Power):
	mana, name, numTargets = 2, "Heal", 1
	description = "Restore 4 Health"
	name_CN = "治疗术"
	index = "Upgraded Hero Power"
	def text(self): return self.calcHeal(4)
		
	def effect(self, target=(), choice=0, comment=''):
		self.heals(target, self.calcHeal(4))
		
	
class LesserHeal(Power):
	mana, name, numTargets = 2, "Lesser Heal", 1
	description = "Restore 2 Health"
	name_CN = "次级治疗术"
	index = "Basic Hero Power"
	upgrade = Heal
	def text(self): return self.calcHeal(2)
		
	def effect(self, target=(), choice=0, comment=''):
		self.heals(target, self.calcHeal(2))
		
	
class PoisonedDaggers(Power):
	mana, name, numTargets = 2, "Poisoned Daggers", 0
	description = "Equip a 2/2 Weapon"
	name_CN = "浸毒匕首"
	index = "Upgraded Hero Power"
	def effect(self, target=(), choice=0, comment=''):
		self.equipWeapon(PoisonedDagger(self.Game, self.ID))
		
	
class DaggerMastery(Power):
	mana, name, numTargets = 2, "Dagger Mastery", 0
	description = "Equip a 1/2 Weapon"
	name_CN = "匕首精通"
	index = "Basic Hero Power"
	upgrade = PoisonedDaggers
	def effect(self, target=(), choice=0, comment=''):
		self.equipWeapon(WickedKnife(self.Game, self.ID))
		
	
class TotemicSlam(Power):
	mana, name, numTargets = 2, "Totemic Slam", 0
	description = "Summon a totem of your choice"
	name_CN = "图腾崇拜"
	index = "Upgraded Hero Power"
	def available(self):
		return not self.chancesUsedUp() and self.Game.space(self.ID) > 0
		
	def effect(self, target=(), choice=0, comment=''):
		totem = self.chooseFixedOptions(comment, options=[SearingTotem(self.Game, self.ID), StoneclawTotem(self.Game, self.ID),
															HealingTotem(self.Game, self.ID), StrengthTotem(self.Game, self.ID)])
		self.summon(totem)
		
	
class TotemicCall(Power):
	mana, name, numTargets = 2, "Totemic Call", 0
	description = "Summon a random totem"
	name_CN = "图腾召唤"
	index = "Basic Hero Power"
	upgrade = TotemicSlam
	def available(self):
		return not self.chancesUsedUp() and self.Game.space(self.ID) and self.viableTotems()[0]
		
	def effect(self, target=(), choice=0, comment=''):
		if totems := self.viableTotems(): self.summon(numpyChoice(totems)(self.Game, self.ID))
		
	def viableTotems(self):
		viableTotems = [SearingTotem, StoneclawTotem, HealingTotem, StrengthTotem]
		for minion in self.Game.minionsonBoard(self.ID): removefrom(type(minion), viableTotems)
		return viableTotems
		
	
class SoulTap(Power):
	mana, name, numTargets = 2, "Soul Tap", 0
	description = "Draw a card"
	name_CN = "灵魂分流"
	index = "Upgraded Hero Power"
	def effect(self, target=(), choice=0, comment=''):
		self.Game.Hand_Deck.drawCard(self.ID, initiator=self)
		
	
class LifeTap(Power):
	mana, name, numTargets = 2, "Life Tap", 0
	description = "Draw a card and take 2 damage"
	name_CN = "生命分流"
	index = "Basic Hero Power"
	upgrade = SoulTap
	def dealsDmg(self): return True
		
	def text(self): return self.calcDamage(2)
		
	def effect(self, target=(), choice=0, comment=''):
		self.dealsDamage(self.Game.heroes[self.ID], self.calcDamage(2))
		self.Game.Hand_Deck.drawCard(self.ID, initiator=self)
		
	
class TankUp(Power):
	mana, name, numTargets = 2, "Tank Up!", 0
	description = "Gain 4 Armor"
	name_CN = "铜墙铁壁！"
	index = "Upgraded Hero Power"
	def effect(self, target=(), choice=0, comment=''):
		self.giveHeroAttackArmor(self.ID, armor=4)
		
	
class ArmorUp(Power):
	mana, name, numTargets = 2, "Armor Up!", 0
	description = "Gain 2 Armor"
	name_CN = "全副武装！"
	index = "Basic Hero Power"
	upgrade = TankUp
	def effect(self, target=(), choice=0, comment=''):
		self.giveHeroAttackArmor(self.ID, armor=2)
		
	
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
	
	
class IllidariInitiate(Minion):
	Class, race, name = "Demon Hunter", "", "Illidari Initiate"
	mana, attack, health = 1, 1, 1
	index = "LEGACY~Uncollectible"
	numTargets, Effects, description = 0, "Rush", "Rush"
	name_CN = "伊利达雷新兵"
	
	
class ExcessMana(Spell):
	Class, school, name = "Druid", "", "Excess Mana"
	numTargets, mana, Effects = 0, 0, ""
	index = "LEGACY~Uncollectible"
	description = "Draw a card"
	name_CN = "法力过剩"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.Game.Hand_Deck.drawCard(self.ID)
		
	
class Claw(Spell):
	Class, school, name = "Druid", "", "Claw"
	numTargets, mana, Effects = 0, 1, ""
	description = "Give your hero +2 Attack this turn. Gain 2 Armor"
	name_CN = "爪击"
	index = "LEGACY"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveHeroAttackArmor(self.ID, attGain=2, armor=2, source=Claw)
		
	
class ArcaneMissiles(Spell):
	Class, school, name = "Mage", "Arcane", "Arcane Missiles"
	numTargets, mana, Effects = 0, 1, ""
	description = "Deal 3 damage randomly split among all enemies"
	name_CN = "奥术飞弹"
	index = "LEGACY"
	def text(self): return self.calcDamage(3)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		ID = 3 - self.ID
		for _ in range(self.calcDamage(3)):
			if objs := self.Game.charsAlive(ID): self.dealsDamage(numpyChoice(objs), 1)
			else: break
		
	
class Pyroblast(Spell):
	Class, school, name = "Mage", "Fire", "Pyroblast"
	numTargets, mana, Effects = 1, 10, ""
	description = "Deal 10 damage"
	name_CN = "炎爆术"
	index = "EXPERT1"
	def text(self): return self.calcDamage(10)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(target, self.calcDamage(10))
		
	
class LightsJustice(Weapon):
	Class, name, description = "Paladin", "Light's Justice", ""
	mana, attack, durability, Effects = 1, 1, 4, ""
	name_CN = "圣光的正义"
	index = "LEGACY"
	
	
class Voidwalker(Minion):
	Class, race, name = "Warlock", "", "Voidwalker"
	mana, attack, health = 1, 1, 3
	numTargets, Effects, description = 0, "Taunt", "Taunt"
	name_CN = "虚空行者"
	index = "LEGACY"
	
	
class Bananas(Spell):
	Class, school, name = "Neutral", "", "Bananas"
	numTargets, mana, Effects = 1, 1, ""
	index = "EXPERT1~Uncollectible"
	description = "Give a minion +1/+1"
	name_CN = "香蕉"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(target, 1, 1, source=Bananas)
		
	
class DamagedGolem(Minion):
	Class, race, name = "Neutral", "Mech", "Damaged Golem"
	mana, attack, health = 1, 2, 1
	index = "EXPERT1~Uncollectible"
	numTargets, Effects, description = 0, "", ""
	name_CN = "损坏的傀儡"
	
	
class Skeleton(Minion):
	Class, race, name = "Neutral", "", "Skeleton"
	mana, attack, health = 1, 1, 1
	index = "ICECROWN~Uncollectible"
	numTargets, Effects, description = 0, "", ""
	name_CN = "骷髅"
	
	
class VioletApprentice(Minion):
	Class, race, name = "Neutral", "", "Violet Apprentice"
	mana, attack, health = 1, 1, 1
	index = "EXPERT1~Uncollectible"
	numTargets, Effects, description = 0, "", ""
	name_CN = "紫罗兰学徒"
	
	
class Whelp(Minion):
	Class, race, name = "Neutral", "Dragon", "Whelp"
	mana, attack, health = 1, 1, 1
	index = "EXPERT1~Uncollectible"
	numTargets, Effects, description = 0, "", ""
	name_CN = "雏龙"
	
	
class BaineBloodhoof(Minion):
	Class, race, name = "Neutral", "", "Baine Bloodhoof"
	mana, attack, health = 5, 5, 5
	index = "EXPERT1~Legendary~Uncollectible"
	numTargets, Effects, description = 0, "", ""
	name_CN = "贝恩·血蹄"
	
	
class Dream(Spell):
	Class, school, name = "DreamCard", "Nature", "Dream"
	numTargets, mana, Effects = 1, 1, ""
	index = "EXPERT1~Uncollectible"
	description = "Return an enemy minion to its owner's hand"
	name_CN = "梦境"
	def available(self):
		return self.selectableMinionExists(3 - self.ID)
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard and obj.ID != self.ID
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for obj in target: self.Game.returnObj2Hand(self, obj)
		
	
class Nightmare(Spell):
	Class, school, name = "DreamCard", "Shadow", "Nightmare"
	numTargets, mana, Effects = 1, 0, ""
	index = "EXPERT1~Uncollectible"
	description = "Give a minion +4/+4. At the start of your next turn, destroy it."
	name_CN = "噩梦"
	trigEffect = Trig_Nightmare
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for obj in target:
			if obj.onBoard:
				self.giveEnchant(obj, 4, 4, source=Nightmare)
				obj.getsTrig(Trig_Nightmare(obj, self.ID))
		
	
class YseraAwakens(Spell):
	Class, school, name = "DreamCard", "Nature", "Ysera Awakens"
	numTargets, mana, Effects = 0, 3, ""
	index = "EXPERT1~Uncollectible"
	description = "Deal 5 damage to all minions except Ysera"
	name_CN = "伊瑟拉苏醒"
	def text(self): return self.calcDamage(5)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage([o for o in self.Game.minionsonBoard() if "Ysera" not in o.name], self.calcDamage(5))
		
	
class LaughingSister(Minion):
	Class, race, name = "DreamCard", "", "Laughing Sister"
	mana, attack, health = 2, 3, 5
	index = "EXPERT1~Uncollectible"
	numTargets, Effects, description = 0, "Evasive", "Can't targeted by spells or Hero Powers"
	name_CN = "欢笑的姐妹"
	
	
class EmeraldDrake(Minion):
	Class, race, name = "DreamCard", "Dragon", "Emerald Drake"
	mana, attack, health = 4, 7, 6
	index = "EXPERT1~Uncollectible"
	numTargets, Effects, description = 0, "", ""
	name_CN = "翡翠幼龙"
	
	
class LeaderofthePack(Spell):
	Class, school, name = "Druid", "", "Leader of the Pack"
	numTargets, mana, Effects = 0, 2, ""
	index = "EXPERT1~Uncollectible"
	description = "Give your minions +1/+1"
	name_CN = "兽群领袖"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.Game.giveEnchant(self.Game.minionsonBoard(self.ID), 1, 1, source=LeaderofthePack)
		
	
class SummonaPanther(Spell):
	Class, school, name = "Druid", "", "Summon a Panther"
	numTargets, mana, Effects = 0, 2, ""
	index = "EXPERT1~Uncollectible"
	description = "Summon a 3/2 Panther"
	name_CN = "召唤猎豹"
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon(Panther(self.Game, self.ID))
		
	
class Panther(Minion):
	Class, race, name = "Druid", "Beast", "Panther"
	mana, attack, health = 2, 3, 2
	index = "EXPERT1~Uncollectible"
	numTargets, Effects, description = 0, "", ""
	name_CN = "猎豹"
	
	
class Treant_Classic(Minion):
	Class, race, name = "Druid", "", "Treant"
	mana, attack, health = 2, 2, 2
	index = "EXPERT1~Uncollectible"
	numTargets, Effects, description = 0, "", ""
	name_CN = "树人"
	
	
class Treant_Classic_Taunt(Minion):
	Class, race, name = "Druid", "", "Treant"
	mana, attack, health = 2, 2, 2
	index = "EXPERT1~Uncollectible"
	numTargets, Effects, description = 0, "Taunt", "Taunt"
	name_CN = "树人"
	
	
class EvolveSpines(Spell):
	Class, school, name = "Druid", "", "Evolve Spines"
	numTargets, mana, Effects = 0, 3, ""
	index = "OG~Uncollectible"
	description = "Give your hero +4 Attack this turn"
	name_CN = "脊刺异变"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveHeroAttackArmor(self.ID, attGain=4, source=EvolveSpines)
		
	
class EvolveScales(Spell):
	Class, school, name = "Druid", "", "Evolve Scales"
	numTargets, mana, Effects = 0, 3, ""
	index = "OG~Uncollectible"
	description = "Gain 8 Armor"
	name_CN = "鳞甲异变"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveHeroAttackArmor(self.ID, armor=8)
		
	
class DruidoftheClaw_Rush(Minion):
	Class, race, name = "Druid", "Beast", "Druid of the Claw"
	mana, attack, health = 5, 5, 4
	index = "EXPERT1~Uncollectible"
	numTargets, Effects, description = 0, "Rush", "Rush"
	name_CN = "利爪德鲁伊"
	
	
class DruidoftheClaw_Taunt(Minion):
	Class, race, name = "Druid", "Beast", "Druid of the Claw"
	mana, attack, health = 5, 5, 6
	index = "EXPERT1~Uncollectible"
	numTargets, Effects, description = 0, "Taunt", "Taunt"
	name_CN = "利爪德鲁伊"
	
	
class DruidoftheClaw_Both(Minion):
	Class, race, name = "Druid", "Beast", "Druid of the Claw"
	mana, attack, health = 5, 5, 6
	index = "EXPERT1~Uncollectible"
	numTargets, Effects, description = 0, "Taunt,Rush", "Taunt, Rush"
	name_CN = "利爪德鲁伊"
	
	
class RampantGrowth(Spell):
	Class, school, name = "Druid", "Nature", "Rampant Growth"
	numTargets, mana, Effects = 0, 6, ""
	index = "EXPERT1~Uncollectible"
	description = "Gain 2 Mana Crystals"
	name_CN = "快速生长"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.Game.Manas.gainManaCrystal(2, self.ID)
		
	
class Enrich(Spell):
	Class, school, name = "Druid", "Nature", "Enrich"
	numTargets, mana, Effects = 0, 6, ""
	index = "EXPERT1~Uncollectible"
	description = "Draw 3 cards"
	name_CN = "摄取养分"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.Game.Hand_Deck.drawCard(self.ID)
		self.Game.Hand_Deck.drawCard(self.ID)
		self.Game.Hand_Deck.drawCard(self.ID)
		
	
class Snake(Minion):
	Class, race, name = "Hunter", "Beast", "Snake"
	mana, attack, health = 1, 1, 1
	index = "EXPERT1~Uncollectible"
	numTargets, Effects, description = 0, "", ""
	name_CN = "蛇"
	
	
class Huffer(Minion):
	Class, race, name = "Hunter", "Beast", "Huffer"
	mana, attack, health = 3, 4, 2
	index = "LEGACY~Uncollectible"
	numTargets, Effects, description = 0, "Charge", "Charge"
	name_CN = "霍弗"
	
	
class Leokk(Minion):
	Class, race, name = "Hunter", "Beast", "Leokk"
	mana, attack, health = 3, 2, 4
	index = "LEGACY~Uncollectible"
	numTargets, Effects, description = 0, "", "Your other minions have +1 Attack"
	name_CN = "雷欧克"
	aura = Aura_Leokk
	
	
class Misha(Minion):
	Class, race, name = "Hunter", "Beast", "Misha"
	mana, attack, health = 3, 4, 4
	index = "LEGACY~Uncollectible"
	numTargets, Effects, description = 0, "Taunt", "Taunt"
	name_CN = "米莎"
	
	
class Hyena_Classic(Minion):
	Class, race, name = "Hunter", "Beast", "Hyena"
	mana, attack, health = 2, 2, 2
	index = "EXPERT1~Uncollectible"
	numTargets, Effects, description = 0, "", ""
	name_CN = "土狼"
	
	
class ManaWyrm(Minion):
	Class, race, name = "Mage", "", "Mana Wyrm"
	mana, attack, health = 1, 1, 2
	numTargets, Effects, description = 0, "", "Whenever you cast a spell, gain 1 Attack"
	name_CN = "法力浮龙"
	index = "EXPERT1"
	trigBoard = Trig_ManaWyrm
	
	
class Defender(Minion):
	Class, race, name = "Paladin", "", "Defender"
	mana, attack, health = 1, 2, 1
	numTargets, Effects, description = 0, "", ""
	name_CN = "防御者"
	index = "EXPERT1~Uncollectible"
	
	
class Ashbringer(Weapon):
	Class, name, description = "Paladin", "Ashbringer", ""
	mana, attack, durability, Effects = 5, 5, 3, ""
	index = "EXPERT1~Legendary~Uncollectible"
	name_CN = "灰烬使者"
	
	
class SpiritWolf(Minion):
	Class, race, name = "Shaman", "", "Spirit Wolf"
	mana, attack, health = 2, 2, 3
	index = "EXPERT1~Uncollectible"
	numTargets, Effects, description = 0, "Taunt", "Taunt"
	name_CN = "幽灵狼"
	
	
class Frog(Minion):
	Class, race, name = "Neutral", "Beast", "Frog"
	mana, attack, health = 0, 0, 1
	index = "LEGACY~Uncollectible"
	numTargets, Effects, description = 0, "Taunt", "Taunt"
	name_CN = "青蛙"
	
	
class Shadowbeast(Minion):
	Class, race, name = "Warlock", "", "Shadowbeast"
	mana, attack, health = 1, 1, 1
	index = "OG~Uncollectible"
	numTargets, Effects, description = 0, "", ""
	name_CN = "暗影兽"
	
	
class BloodFury(Weapon):
	Class, name, description = "Warlock", "Blood Fury", ""
	mana, attack, durability, Effects = 3, 3, 8, ""
	index = "EXPERT1~Uncollectible"
	name_CN = "血怒"
	
	
class Infernal(Minion):
	Class, race, name = "Warlock", "Demon", "Infernal"
	mana, attack, health = 6, 6, 6
	index = "EXPERT1~Uncollectible"
	numTargets, Effects, description = 0, "", ""
	name_CN = "地狱火"
	
	
class Nerubian(Minion):
	Class, race, name = "Neutral", "", "Nerubian"
	mana, attack, health = 4, 4, 4
	index = "NAXX~Uncollectible"
	numTargets, Effects, description = 0, "", ""
	name_CN = "蛛魔"
	
	
class BoomBot(Minion):
	Class, race, name = "Neutral", "Mech", "Boom Bot"
	mana, attack, health = 1, 1, 1
	index = "GVG~Uncollectible"
	numTargets, Effects, description = 0, "", "Deathrattle: Deal 1~4 damage to a random enemy"
	deathrattle = Death_BoomBot
	
	
class GoldenKobold(Minion):
	Class, race, name = "Neutral", "", "Golden Kobold"
	mana, attack, health = 3, 6, 6
	index = "LOOTAPALOOZA~Battlecry~Legendary~Uncollectible"
	numTargets, Effects, description = 0, "Taunt", "Taunt. Battlecry: Replace your hand with Legendary minions"
	name_CN = "黄金狗头人"
	poolIdentifier = "Legendary Minions"
	@classmethod
	def generatePool(cls, pools):
		return "Legendary Minions", pools.LegendaryMinions
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if hand := self.Game.Hand_Deck.hands[self.ID]:
			self.Game.Hand_Deck.extractfromHand(None, self.ID, getAll=True)
			self.addCardtoHand(numpyChoice(self.rngPool("Legendary Minions"), len(hand), replace=True), self.ID)
		
	
class TolinsGoblet(Spell):
	Class, school, name = "Neutral", "", "Tolin's Goblet"
	numTargets, mana, Effects = 0, 3, ""
	index = "LOOTAPALOOZA~Uncollectible"
	description = "Draw a card. Fill your hand with copies of it"
	name_CN = "托林的酒杯"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		HD = self.Game.Hand_Deck
		card, mana, entersHand = HD.drawCard(self.ID)
		if entersHand and HD.handNotFull(self.ID):
			self.addCardtoHand([self.copyCard(card, self.ID) for _ in range(HD.spaceinHand(self.ID))], self.ID)
		
	
class WondrousWand(Spell):
	Class, school, name = "Neutral", "", "Wondrous Wand"
	numTargets, mana, Effects = 0, 3, ""
	index = "LOOTAPALOOZA~Uncollectible"
	description = "Draw 3 cards. Reduce their costs to (0)"
	name_CN = "奇迹之杖"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for _ in (0, 1, 2):
			card, mana, entersHand = self.Game.Hand_Deck.drawCard(self.ID)
			if entersHand: ManaMod(card, to=0).applies()
		
	
class ZarogsCrown(Spell):
	Class, school, name = "Neutral", "", "Zarog's Crown"
	numTargets, mana, Effects = 0, 3, ""
	index = "LOOTAPALOOZA~Uncollectible"
	description = "Discover a Legendary minion. Summon two copies of it"
	name_CN = "扎罗格的王冠"
	poolIdentifier = "Legendary Minions as Druid to Summon"
	@classmethod
	def generatePool(cls, pools):
		return genPool_CertainMinionsasClass(pools, "Legendary", cond=lambda card: "~Legendary" in card.index)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.Game.space(self.ID) > 0:
			minion, _ = self.discoverNew(comment, lambda : self.rngPool("Legendary Minions as %s to Summon" % class4Discover(self)),
									  	add2Hand=False)
			self.summon([minion, type(minion)(self.Game, self.ID)])
		
	
class Bomb(Spell):
	Class, school, name = "Neutral", "", "Bomb"
	numTargets, mana, Effects = 0, 5, ""
	index = "BOOMSDAY~Uncollectible"
	description = "Casts When Drawn. Deal 5 damage to your hero"
	name_CN = "炸弹"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(self.Game.heroes[self.ID], 5)
		
	


AllClasses_AcrossPacks = [
	Aura_Leokk, Death_BoomBot, Trig_HealingTotem, Trig_StrengthTotem, Trig_Nightmare, Trig_ManaWyrm, TheCoin, SilverHandRecruit,
	WickedKnife, PoisonedDagger, SearingTotem, StoneclawTotem, HealingTotem, StrengthTotem, DemonsBite, DemonClaws,
	DireShapeshift, Shapeshift, BallistaShot, SteadyShot, FireblastRank2, Fireblast, TheSilverHand, Reinforce, Heal,
	LesserHeal, PoisonedDaggers, DaggerMastery, TotemicSlam, TotemicCall, SoulTap, LifeTap, TankUp, ArmorUp, Illidan,
	Rexxar, Valeera, Malfurion, Garrosh, Uther, Thrall, Jaina, Anduin, Guldan, IllidariInitiate, ExcessMana, Claw,
	ArcaneMissiles, Pyroblast, LightsJustice, Voidwalker, Bananas, DamagedGolem, Skeleton, VioletApprentice, Whelp,
	BaineBloodhoof, Dream, Nightmare, YseraAwakens, LaughingSister, EmeraldDrake, LeaderofthePack, SummonaPanther,
	Panther, Treant_Classic, Treant_Classic_Taunt, EvolveSpines, EvolveScales, DruidoftheClaw_Rush, DruidoftheClaw_Taunt,
	DruidoftheClaw_Both, RampantGrowth, Enrich, Snake, Huffer, Leokk, Misha, Hyena_Classic, ManaWyrm, Defender, Ashbringer,
	SpiritWolf, Frog, Shadowbeast, BloodFury, Infernal, Nerubian, BoomBot, GoldenKobold, TolinsGoblet, WondrousWand,
	ZarogsCrown, Bomb, 
]

