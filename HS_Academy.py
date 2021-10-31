from Parts_ConstsFuncsImports import *
from Parts_CardTypes import *
from Parts_TrigsAuras import *

from HS_AcrossPacks import Lackeys, HealingTotem, SearingTotem, StoneclawTotem, StrengthTotem, ManaWyrm
from HS_Uldum import PlagueofDeath, PlagueofMadness, PlagueofMurlocs, PlagueofFlames, PlagueofWrath
from HS_Outlands import Minion_Dormantfor2turns
from HS_Barrens import RankedSpells
from Panda_CustomWidgets import posHandsTable, hprHandsTable, HandZone1_Y, HandZone2_Y, HandZone_Z, scale_Hand

#可以通过宣传牌确认是施放法术之后触发
#经典-奥格瑞玛	战吼：造成2点伤害
#经典-暴风城	圣盾
#经典-荆棘谷	潜行，剧毒
#经典-潘达利亚四风谷	战吼：使一个友方随从获得+1/+2
#纳克萨玛斯的诅咒	亡语：随机将一个具有亡语的随从置入你的手牌
#地精大战侏儒	战吼,亡语：将一张零件牌置入你的手牌
#黑石山的火焰	在你的回合结束 时随机使你的一张手牌法力值消耗减少(2)点
#冠军的试炼	激励：抽一张牌
#探险者协会-博物馆		战吼：发现一个新的基础英雄技能
#探险者协会-废墟之城	战吼：随机将一张武器牌置入你的手牌
#上古之神的低语-腐化的暴风城	战吼：消耗你所有的法力值，随机召唤一个法力值消耗相同的随从
#卡拉赞之夜	战吼：随机将一张卡拉赞传送六法术牌置入你的手牌（大漩涡传送门，银月城传送门，铁炉堡传送门，月光林地传送门，火焰之地传送门
#）
#龙争虎斗加基森 战吼：随机使你手牌中的一张随从牌获得+2/+2
#勇闯安戈洛	战吼：进化
#冰封王府的骑士	亡语：随机将一张死亡骑士牌置入你的手牌
#狗头人与地下世界	战吼：招募一个法力值消耗小于或等于（2）点的随从
#女巫森林	回响，突袭
#砰砰计划	嘲讽，战吼：如果你有十个法力水晶，获得+5/+5
#拉斯塔哈大乱斗	突袭，超杀：抽一张牌
#暗影崛起	战吼：将一张跟班牌置入你的手牌
#
#奥丹姆奇兵-沙漠	复生
#奥丹姆奇兵-绿洲	战吼：将一张奥丹姆灾祸法术牌置入你的手牌
#巨龙降临	战吼：发现一张龙牌
#外域的灰烬	休眠两回合。唤醒时，随机对两个敌方随从造成3点伤害。
#通灵学园	战吼：将一张双职业卡牌置入你的手牌
#暗月马戏团 腐蚀： 获得+2/+2

#Assuming always destroy the Soul Fragment near the bottom of the deck
def destroyaSoulFragment(game, ID):
	for i, card in enumerate(game.Hand_Deck.decks[ID]):
		if isinstance(card, SoulFragment):
			game.Hand_Deck.extractfromDeck(i, ID)
			return True
	return False
	
"""Animation"""
def panda_SecretPassage_LeaveHand(game, GUI, cards):
	if not cards: return  #If no cards removed from hand, nothing happens
	para = GUI.PARALLEL()
	for i, card in zip(range(len(cards)), reversed(cards)):
		btn, nodepath = card.btn, card.btn.np
		x, y, z = nodepath.getPos()
		para.append(GUI.SEQUENCE(GUI.WAIT(0.4*i), GUI.LERP_PosHpr(nodepath, duration=0.4, pos=(x, 1.5, 2.5), hpr=(0, 0, 0)),
								 GUI.WAIT(0.2), GUI.LERP_Pos(nodepath, duration=0.3, pos=(30, 1.5, z)))
					)
	GUI.seqHolder[-1].append(para)
	
def panda_SecretPassage_BackfromPassage(game, GUI, cards, poses, hprs):
	if not cards: return #If no cards removed from hand, nothing happens
	para = GUI.PARALLEL()
	spaceinHand = game.Hand_Deck.spaceinHand(cards[0].ID)
	for i, card, pos, hpr in zip(range(len(cards)), cards, poses, hprs):
		if card.btn and card.btn.np:
			nodepath, btn = card.btn.np, card.btn
			if i + 1 > spaceinHand and btn.np:
				print("i greater than space in hand", i+1, spaceinHand)
				para.append(GUI.FUNC(nodepath.removeNode))
			else:
				para.append(GUI.SEQUENCE(GUI.WAIT(i*0.3), GUI.LERP_Pos(nodepath, duration=0.3, startPos=(-30, 1.5, HandZone_Z), pos=(0, 1.5, 2.5)),
										GUI.WAIT(0.2), GUI.LERP_PosHpr(nodepath, duration=0.3, pos=pos, hpr=hpr)))
		else:
			nodepath, btn = GUI.genCard(GUI, card, isPlayed=True, pickable=True, pos=(-30, 1.5, HandZone_Z), scale=scale_Hand,
										onlyShowCardBack=GUI.sock and card.ID != GUI.ID and not GUI.showEnemyHand)
			para.append(GUI.SEQUENCE(GUI.WAIT(i * 0.3),
									 GUI.LERP_Pos(nodepath, duration=0.3, pos=(0, 1.5, 2.5)), GUI.WAIT(0.2),
									 GUI.LERP_PosHpr(nodepath, duration=0.3, pos=pos, hpr=hpr)))
	GUI.seqHolder[-1].append(para)
	

"""Auras"""
class Aura_RobesofProtection(Aura_AlwaysOn):
	effGain, targets = "Evasive", "All"

class Aura_Kolek(Aura_AlwaysOn):
	attGain = 1

class Aura_VulperaToxinblade(Aura_AlwaysOn):
	attGain, targets = 2, "Weapon"

"""Trigs"""
class Trig_Corrupt(TrigHand):
	signals = ("ManaPaid", "MinionBeenPlayed", "SpellBeenPlayed", "WeaponBeenPlayed", "HeroBeenPlayed")
	def __init__(self, keeper):
		super().__init__(keeper)
		self.on = False

	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		#在打出一张牌的时候先支付法力值，根据费用决定这个扳机是否激活。然后在实际发出一张牌已经被打出的信号时，决定是否应该实际腐化
		card = self.keeper
		if signal == "ManaPaid": return card.inHand and ID == card.ID and subject.category != "Power"
		else: return card.inHand and self.on and ID == card.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if signal == "ManaPaid": self.on = number > self.keeper.mana
		else:
			card, self.on = self.keeper, False
			newCard = type(card).corruptedType(card.Game, card.ID)
			newCard.inheritEnchantmentsfrom(card)
			card.Game.Hand_Deck.replaceCardinHand(card, newCard, calcMana=True)
	#When the trig is copied, new trigCopy.on is always False


#可以通过宣传牌确认是施放法术之后触发
class Spellburst(TrigBoard):
	signals, oneTime = ("SpellBeenPlayed", ), True
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject.ID == self.keeper.ID
		
	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrig(signal, ID, subject, target, number, comment):
			btn, GUI = self.keeper.btn, self.keeper.Game.GUI
			if btn and "SpecTrig" in btn.icons:
				btn.icons["SpecTrig"].trigAni()
			self.keeper.losesTrig(self)
			self.effect(signal, ID, subject, target, number, comment)


class Trig_IntrepidInitiate(Spellburst):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.giveEnchant(self.keeper, 2, 0, name=IntrepidInitiate)


class Trig_PenFlinger(Spellburst):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.Game.returnObj2Hand(self.keeper, deathrattlesStayArmed=False)


class Trig_SphereofSapience(TrigBoard):
	signals = ("TurnStarts",)

	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return ID == self.keeper.ID and self.keeper.onBoard and self.keeper.health > 0

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		ownDeck = self.keeper.Game.Hand_Deck.decks[self.keeper.ID]
		if len(ownDeck) > 1: self.keeper.chooseFixedOptions(SphereofSapience, '', options=[ownDeck[-1], NewFate(ID=self.keeper.ID)])


# 不知道疲劳的时候是否会一直抽牌，假设不会
class Trig_VoraciousReader(TrigBoard):
	signals = ("TurnEnds",)
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		HD = self.keeper.Game.Hand_Deck
		while len(HD.hands[self.keeper.ID]) < 3:
			if HD.drawCard(self.keeper.ID)[0] is None: break # 假设疲劳1次的时候会停止抽牌
			

class Trig_EducatedElekk(TrigBoard):
	signals = ("SpellPlayed",)
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.keeper
		for trig in self.keeper.deathrattles:
			if isinstance(trig, Death_EducatedElekk):
				trig.savedObjs.append(type(subject))


class Trig_EnchantedCauldron(Spellburst):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if spells := self.rngPool("%d-Cost Spells" % number):
			numpyChoice(spells)(self.keeper.Game, self.keeper.ID).cast()

class Trig_CrimsonHothead(Spellburst):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.giveEnchant(self.keeper, 1, 0, effGain="Taunt", name=CrimsonHothead)

class Trig_WretchedTutor(Spellburst):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.keeper
		targets = minion.Game.minionsonBoard(minion.ID, minion) + minion.Game.minionsonBoard(3-minion.ID)
		minion.AOE_Damage(targets, [2 for minion in targets])
		

#假设检测方式是在一张法术打出时开始记录直到可以触发法术迸发之前的两次死亡结算中所有死亡随从
class Trig_HeadmasterKelThuzad(TrigBoard):
	signals, oneTime = ("SpellPlayed", "SpellBeenPlayed", "MinionDied", ), True
	def __init__(self, keeper):
		super().__init__(keeper)
		self.on = False

	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		if signal == "MinionDied": return self.on
		else: return self.keeper.onBoard and subject.ID == self.keeper.ID

	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrig(signal, ID, subject, target, number, comment):
			if signal == "SpellPlayed": self.on = True
			elif signal == "MinionDied": self.savedObjs.append(type(target))
			else:
				btn, GUI = self.keeper.btn, self.keeper.Game.GUI
				if btn and "SpecTrig" in btn.icons: btn.icons["SpecTrig"].trigAni()
				(minion := self.keeper).losesTrig(self)
				if self.savedObjs:
					minion.summon([minionKilled(minion.Game, minion.ID) for minionKilled in self.savedObjs])


class Trig_Ogremancer(TrigBoard):
	signals = ("SpellPlayed", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject.ID != self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.summon(RisenSkeleton(self.keeper.Game, self.keeper.ID))


class Trig_OnyxMagescribe(Spellburst):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		pool = self.rngPool(self.keeper.Game.heroes[self.keeper.ID].Class + " Spells")
		self.keeper.addCardtoHand(numpyChoice(pool, 2, replace=True), self.keeper.ID)


class Trig_KeymasterAlabaster(TrigBoard):
	signals = ("CardDrawn", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and target[0].ID != self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		Copy = target[0].selfCopy(self.keeper.ID, self.keeper)
		Copy.manaMods.append(ManaMod(Copy, to=1))
		self.keeper.addCardtoHand(Copy, self.keeper.ID)

#即使是被冰冻的随从也可以因为这个效果进行攻击，同时攻击不浪费攻击机会，同时可以触发巨型沙虫等随从的获得额外的攻击机会
class Trig_TrueaimCrescent(TrigBoard):
	signals = ("HeroAttackedMinion", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		#The target can't be dying to trigger this
		return subject.ID == self.keeper.ID and self.keeper.onBoard and not target.dead and target.health > 0

	#随从的攻击顺序与它们的登场顺序一致
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		game = self.keeper.Game
		if minions := game.minionsAlive(self.keeper.ID):
			for minion in game.objs_SeqSorted(minions)[0]:
				if target.onBoard and target.health > 0 and not target.dead:
					game.battle(minion, target, verifySelectable=False, useAttChance=False, resolveDeath=False, resetRedirTrig=True)
				else: break


class Trig_AceHunterKreen(TrigBoard):
	signals = ("BattleStarted", "BattleFinished", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.keeper.ID and subject != self.keeper and self.keeper.onBoard

	#不知道攻击具有受伤时召唤一个随从的扳机的随从时，飞刀能否对这个友方角色造成伤害
	#目前的写法是这个战斗结束信号触发在受伤之后
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if signal == "BattleStarted": subject.getsEffect("Immune")
		else: subject.losesEffect("Immune")


class Trig_Magehunter(TrigBoard):
	signals = ("MinionAttackingMinion", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.keeper and self.keeper.onBoard

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		target.getsSilenced()
		

class Trig_BloodHerald(TrigHand):
	signals = ("MinionDies", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.inHand and target.ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.giveEnchant(self.keeper, 1, 1, name=BloodHerald, add2EventinGUI=False)


class Trig_FelGuardians(TrigHand):
	signals = ("MinionDies",)
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.inHand and target.ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		ManaMod(self.keeper, by=-1).applies()


class Trig_AncientVoidHound(TrigBoard):
	signals = ("TurnEnds", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return ID == self.keeper.ID and self.keeper.onBoard

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		enemyMinions = self.keeper.Game.minionsonBoard(3-self.keeper.ID)
		keeperType = type(self.keeper)
		num = len(enemyMinions)
		for minion in enemyMinions:
			minion.dmgTaken += 1
			minion.enchantments.append(Enchantment(-1, 0, name=AncientVoidHound))
			minion.calcStat()
		if num: self.keeper.giveEnchant(self.keeper, num, num, name=AncientVoidHound)
		

class Trig_Gibberling(Spellburst):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.keeper
		minion.summon(Gibberling(minion.Game, minion.ID))
		

class Trig_SpeakerGidra(Spellburst):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.giveEnchant(self.keeper, number, number, name=SpeakerGidra)


class Trig_TwilightRunner(TrigBoard):
	signals = ("MinionAttackingMinion", "MinionAttackingHero",)
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject == self.keeper

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.Game.Hand_Deck.drawCard(self.keeper.ID)
		self.keeper.Game.Hand_Deck.drawCard(self.keeper.ID)


class Trig_ForestWardenOmu(Spellburst):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.Game.Manas.restoreManaCrystal(0, self.keeper.ID, restoreAll=True)


class GameRuleAura_ProfessorSlate(GameRuleAura):
	def auraAppears(self): self.keeper.Game.effects[self.keeper.ID]["Spells Poisonous"] += 1
	def auraDisappears(self): self.keeper.Game.effects[self.keeper.ID]["Spells Poisonous"] -= 1


class Trig_KroluskBarkstripper(Spellburst):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minions = self.keeper.Game.minionsAlive(3-self.keeper.ID)
		if minions: self.keeper.Game.killMinion(self.keeper, numpyChoice(minions))


class Trig_Firebrand(Spellburst):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion, side = self.keeper, 3 - self.keeper.ID
		for num in (1, 2, 3, 4):
			if minions := minion.Game.minionsAlive(side): minion.dealsDamage(numpyChoice(minions), 1)
			else: break
			

class Trig_JandiceBarov(TrigBoard):
	signals = ("MinionTakesDmg", )
	def __init__(self, keeper):
		super().__init__(keeper)
		self.show = False

	def connect(self):
		super().connect()
		if GUI := self.keeper.Game.GUI:
			self.show = not GUI.need2beHidden(self.keeper)
			self.keeper.btn.placeIcons()

	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and target == self.keeper
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.Game.killMinion(None, self.keeper)
		
		
class Trig_MozakiMasterDuelist(TrigBoard):
	signals = ("SpellBeenPlayed", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject.ID == self.keeper.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.giveEnchant(self.keeper, effGain="Spell Damage", name=MozakiMasterDuelist)


class Trig_WyrmWeaver(Spellburst):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.summon([ManaWyrm(self.keeper.Game, self.keeper.ID) for _ in (0, 1)], relative="<>")


class Trig_GoodyTwoShields(Spellburst):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.giveEnchant(self.keeper, effGain="Divine Shield", name=GoodyTwoShields)


class Trig_HighAbbessAlura(Spellburst):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		HD = self.keeper.Game.Hand_Deck
		if indices := [i for i, card in enumerate(HD.decks[self.keeper.ID]) if card.category == "Spell"]:
			HD.extractfromDeck(numpyChoice(indices), self.keeper.ID)[0].cast(self.keeper)
			self.keeper.Game.gathertheDead()


class Trig_DevoutPupil(TrigHand):
	signals = ("SpellBeenPlayed", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.inHand and target and subject.ID == target.ID and subject.ID == self.keeper.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.Game.Manas.calcMana_Single(self.keeper)


#可以通过宣传牌确认是施放法术之后触发
class Trig_TuralyontheTenured(TrigBoard):
	signals = ("MinionAttackingMinion", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject == self.keeper
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		target.statReset(3, 3, source=type(self.keeper))

		
class Trig_PowerWordFeast(TrigBoard):
	signals = ("TurnEnds", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard #Even if the current turn is not minion's owner's turn
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.losesTrig(self, trigType="TrigBoard")
		heal = self.keeper.calcHeal(self.keeper.health_max)
		PowerWordFeast(self.keeper.Game, self.keeper.ID).restoresHealth(self.keeper, heal)
		
		
class Trig_CabalAcolyte(Spellburst):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if minions := [minion for minion in self.keeper.Game.minionsAlive(3-self.keeper.ID) if minion.attack < 3]:
			self.keeper.Game.minionSwitchSide(numpyChoice(minions))
		

class Trig_DisciplinarianGandling(TrigBoard):
	signals = ("MinionBeenPlayed", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		print("Test Gandling's trigger", signal, ID, subject, target, number, comment, choice)
		print("Test Gandling's trigger 2", self.keeper.onBoard, subject.ID, self.keeper.ID, subject.onBoard)
		print("Can Gandling trigger?", self.keeper.onBoard and subject.ID == self.keeper.ID and subject.onBoard )
		return self.keeper.onBoard and subject.ID == self.keeper.ID and subject.onBoard
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		ID, game = self.keeper.ID, self.keeper.Game
		position, subject.dead = subject.pos, True
		game.gathertheDead()
		#Rule copied from Conjurer's Calling(Rise of Shadows)
		if position == 0: pos = -1 #Summon to the leftmost
		elif position < len(game.minionsonBoard(ID)): pos = position + 1
		else: pos = -1
		self.keeper.summon(FailedStudent(game, ID), position=pos)


class Trig_FleshGiant(TrigHand):
	signals = ("HeroChangedHealthinTurn", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.inHand and ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.Game.Manas.calcMana_Single(self.keeper)


class Trig_Plagiarize(Trig_Secret):
	signals = ("TurnEnds", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.ID != ID and self.keeper.Game.Counters.cardsPlayedEachTurn[3-self.keeper.ID][-1]
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		cards = self.keeper.Game.Counters.cardsPlayedEachTurn[3-self.keeper.ID][-1]
		self.keeper.addCardtoHand(cards, self.keeper.ID)
		

class Trig_SelfSharpeningSword(TrigBoard):
	signals = ("HeroAttackedMinion", "HeroAttackedHero", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.keeper.ID and self.keeper.onBoard
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.giveEnchant(self.keeper, statEnchant=Enchantment_Cumulative(1, 0, name=SelfSharpeningSword))


class Trig_ShiftySophomore(Spellburst):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.addCardtoHand(numpyChoice(self.rngPool("Combo Cards")), self.keeper.ID)


class Trig_CuttingClass(TrigHand):
	signals = ("WeaponAppears", "WeaponDisappears", "WeaponStatCheck", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.inHand and ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.Game.Manas.calcMana_Single(self.keeper)


class Trig_DoctorKrastinov(TrigBoard):
	signals = ("MinionAttackingMinion", "MinionAttackingHero",)
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.keeper and self.keeper.onBoard

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		weapon = self.keeper.Game.availableWeapon(self.keeper.ID)
		if weapon: self.keeper.giveEnchant(weapon, statEnchant=Enchantment_Cumulative(1, 1, name=DoctorKrastinov))


class Trig_DiligentNotetaker(Spellburst):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.addCardtoHand(type(subject), self.keeper.ID)
		

class Trig_RuneDagger(TrigBoard):
	signals = ("HeroAttackedHero", "HeroAttackedMinion", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject == self.keeper.Game.heroes[self.keeper.ID]

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.giveEnchant(self.keeper.Game.heroes[self.keeper.ID], effGain="Spell Damage", name=RuneDagger)
		RuneDagger_Effect(self.keeper.Game, self.keeper.ID).connect()
		

class Trig_TrickTotem(TrigBoard):
	signals = ("TurnEnds", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		numpyChoice(self.rngPool("Spells of <=3 Cost"))(self.keeper.Game, self.keeper.ID).cast()

			
class Trig_RasFrostwhisper(TrigBoard):
	signals = ("TurnEnds", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and ID == self.keeper.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.keeper
		damage = 1 + minion.countSpellDamage()
		targets = [minion.Game.heroes[3-minion.ID]] + minion.Game.minionsonBoard(3-minion.ID)
		minion.AOE_Damage(targets, [damage] * len(targets))


class Trig_CeremonialMaul(Spellburst):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		game, stat = self.keeper.Game, number
		if stat and game.space(self.keeper.ID):
			cost = min(stat, 10)
			newIndex = "SCHOLOMANCE~Warrior,Paladin~%d~%d~%d~Minion~~Honor Student~Taunt~Uncollectible"%(cost, stat, stat)
			subclass = type("HonorStudent__%d"%stat, (HonorStudent, ),
							{"mana": cost, "attack": stat, "health": stat,
							"index": newIndex}
							)
			self.keeper.summon(subclass(game, self.keeper.ID))


class Trig_Playmaker(TrigBoard):
	signals = ("MinionBeenPlayed", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject.ID == self.keeper.ID and subject.effects["Rush"] > 0

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		Copy = subject.selfCopy(self.keeper.ID, self.keeper)
		for enchant in Copy.enchantments: enchant.handleStatMax(Copy)
		Copy.dmgTaken = Copy.health_max - 1
		self.keeper.summon(Copy)
		

class Trig_ReapersScythe(Spellburst):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.giveEnchant(self.keeper, effectEnchant=Enchantment(effGain="Sweep", until=0, name=ReapersScythe))


class Trig_Troublemaker(TrigBoard):
	signals = ("TurnEnds", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and ID == self.keeper.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		game = self.keeper.Game
		ruffians = [Ruffian(game, self.keeper.ID) for _ in (0, 1)]
		self.keeper.summon(ruffians, relative="<>")
		for ruffian in ruffians:
			if objs := game.charsAlive(3-self.keeper.ID):
				if ruffian.onBoard and not ruffian.dead and ruffian.health > 0:
					game.battle(ruffian, numpyChoice(objs), verifySelectable=False, resolveDeath=False)
			else: break

"""Deathrattles"""
class Death_SneakyDelinquent(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.addCardtoHand(SpectralDelinquent, self.keeper.ID)

class Death_EducatedElekk(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.keeper
		minion.shuffleintoDeck([spell(minion.Game, minion.ID) for spell in self.savedObjs])

	def selfCopy(self, recipient):
		trig = type(self)(recipient)
		trig.savedObjs = self.savedObjs[:]
		return trig

	def assistCreateCopy(self, Copy):
		Copy.savedObjs = self.savedObjs[:]


class Death_FishyFlyer(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.addCardtoHand(SpectralFlyer, self.keeper.ID)

class Death_SmugSenior(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.addCardtoHand(SpectralSenior, self.keeper.ID)

class Death_PlaguedProtodrake(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.summon(numpyChoice(self.rngPool("7-Cost Minions to Summon"))(self.keeper.Game, self.keeper.ID),
						   self.keeper.pos + 1)

class Death_BloatedPython(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.summon(HaplessHandler(self.keeper.Game, self.keeper.ID))

class Death_TeachersPet(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.summon(numpyChoice(self.rngPool("3-Cost Beasts to Summon"))(self.keeper.Game, self.keeper.ID))

class Death_InfiltratorLilian(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = ForsakenLilian(self.keeper.Game, self.keeper.ID)
		self.keeper.summon(minion)
		objs = self.keeper.Game.charsAlive(3 - self.keeper.ID)
		if minion.onBoard and minion.health > 0 and not minion.dead and objs:
			self.keeper.Game.battle(minion, numpyChoice(objs), verifySelectable=False, resolveDeath=False)

class Death_TotemGoliath(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion, game = self.keeper, self.keeper.Game
		minion.summon([totem(game, minion.ID) for totem in (HealingTotem, SearingTotem, StoneclawTotem, StrengthTotem)])

class Death_BonewebEgg(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.summon([BonewebSpider(self.keeper.Game, self.keeper.ID) for _ in (0, 1)])

class Death_LordBarov(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minions = self.keeper.Game.minionsonBoard(self.keeper.ID) + self.keeper.Game.minionsonBoard(3 - self.keeper.ID)
		self.keeper.AOE_Damage(minions, [1 for i in range(len(minions))])

class Death_Rattlegore(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion, ID = self.keeper, self.keeper.ID
		if minion.Game.space(ID) > 0: #如果场上空间不足则直接跳过
			return
		cardType = type(minion)
		attack_0, health_0 = minion.attack_0, minion.health_0
		if signal[0] != "M":
			for enchant in minion.enchantments:
				if enchant.attGain: attack_0 += enchant.attGain
				elif enchant.attSet: attack_0 = enchant.attSet
				if enchant.healthGain: health_0 += enchant.healthGain
				elif enchant.healthSet: health_0 = enchant.healthSet
		if health_0 > 1:
			cost, attack_0, health_0 = max(0, cardType.mana-1),  attack_0 - 1, health_0 - 1
			index = minion.index
			if "Uncollectible" not in index: index.append("~Uncollectible")
			subclass = type(cardType.__name__ + "__%d_%d"%(attack_0, health_0), (cardType, ),
							{"mana": cost, "attack": attack_0, "health": health_0,
							 "index": index}
							)
			minion.summon(subclass(minion.Game, minion.ID))

"""Neutral Cards"""
class Variant_TransferStudent(Minion):
	Class, race, name = "Neutral", "", "Transfer Student"
	mana, attack, health = 2, 2, 2
	name_CN = "转校生"

class TransferStudent_Ogrimmar(Variant_TransferStudent):
	index = "SCHOLOMANCE~Neutral~Minion~2~2~2~~Transfer Student~Ogrimmar~Battlecry"
	requireTarget, effects, description = True, "", "Battlecry: Deal 2 damage"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.dealsDamage(target, 2)
		return target

class TransferStudent_Stormwind(Variant_TransferStudent):
	index = "SCHOLOMANCE~Neutral~Minion~2~2~2~~Transfer Student~Stormwind~Divine Shield"
	requireTarget, effects, description = False, "Divine Shield", "Divine Shield"

class TransferStudent_Stranglethorn(Variant_TransferStudent):
	index = "SCHOLOMANCE~Neutral~Minion~2~2~2~~Transfer Student~Stranglethorn~Stealth~Poisonous"
	requireTarget, effects, description = False, "Stealth,Poisonous", "Stealth, Poisonous"

class TransferStudent_FourWindValley(Variant_TransferStudent):
	index = "SCHOLOMANCE~Neutral~Minion~2~2~2~~Transfer Student~Pandaria~Battlecry"
	requireTarget, effects, description = True, "", "Battlecry: Give a friendly minion +1/+2"
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists(choice)
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.ID == self.ID and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.giveEnchant(target, 1, 2, name=TransferStudent_FourWindValley)
		return target

class TransferStudent_Shadows(Variant_TransferStudent):
	index = "SCHOLOMANCE~Neutral~Minion~2~2~2~~Transfer Student~Shadows~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Add a Lackey to your hand"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.addCardtoHand(numpyChoice(Lackeys), self.ID)

class TransferStudent_UldumDesert(Variant_TransferStudent):
	index = "SCHOLOMANCE~Neutral~Minion~2~2~2~~Transfer Student~Uldum~Reborn"
	requireTarget, effects, description = False, "Reborn", "Reborn"

class TransferStudent_UldumOasis(Variant_TransferStudent):
	index = "SCHOLOMANCE~Neutral~Minion~2~2~2~~Transfer Student~Uldum~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Add a Uldum plague card to your hand"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.addCardtoHand(numpyChoice((PlagueofDeath, PlagueofMadness, PlagueofMurlocs, PlagueofFlames, PlagueofWrath)), self.ID)

class TransferStudent_Dragons(Variant_TransferStudent):
	index = "SCHOLOMANCE~Neutral~Minion~2~2~2~~Transfer Student~Dragons~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Discover a Dragon"
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
		self.discoverandGenerate(TransferStudent_Dragons, comment, lambda : self.rngPool("Dragons as " + classforDiscover(self)))

class TransferStudent_Outlands(Minion_Dormantfor2turns):
	Class, race, name = "Neutral", "", "Transfer Student"
	mana, attack, health = 2, 2, 2
	index = "SCHOLOMANCE~Neutral~Minion~2~2~2~~Transfer Student~Outlands"
	requireTarget, effects, description = False, "", "Dormant for 2 turns. When this awakens, deal 3 damage to 2 random enemy minions"
	name_CN = "转校生"
	def awakenEffect(self):
		if minions := self.Game.minionsAlive(3-self.ID):
			self.AOE_Damage(numpyChoice(minions, min(len(minions), 2), replace=False), [3] * len(minions))

class TransferStudent_Academy(Variant_TransferStudent):
	index = "SCHOLOMANCE~Neutral~Minion~2~2~2~~Transfer Student~Academy~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Add a random Dual Class card to your hand"
	poolIdentifier = "Dual Class Cards"
	@classmethod
	def generatePool(cls, pools):
		cards = []
		for Class in pools.Classes:
			cards += [card for card in pools.ClassCards[Class] if "," in card.Class]
		return "Dual Class Cards", cards
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.addCardtoHand(numpyChoice(self.rngPool("Dual Class Cards")), self.ID)

class TransferStudent_Darkmoon_Corrupt(Minion):
	Class, race, name = "Neutral", "", "Transfer Student"
	mana, attack, health = 2, 4, 4
	index = "SCHOLOMANCE~Neutral~Minion~2~4~4~~Transfer Student~Darkmoon~Corrupted~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "转校生"

class TransferStudent_Darkmoon(Variant_TransferStudent):
	index = "SCHOLOMANCE~Neutral~Minion~2~2~2~~Transfer Student~Darkmoon~ToCorrupt"
	requireTarget, effects, description = False, "", "Corrupt: Gain +2/+2"
	trigHand, corruptedType = Trig_Corrupt, TransferStudent_Darkmoon_Corrupt

class TransferStudent_Barrens(Variant_TransferStudent):
	index = "SCHOLOMANCE~Neutral~Minion~2~2~2~~Transfer Student~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Add a random Ranked Spell to your hand"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.addCardtoHand(numpyChoice(RankedSpells), self.ID)

class TransferStudent_UnitedinStormwind(Variant_TransferStudent):
	index = "SCHOLOMANCE~Neutral~Minion~2~2~2~~Transfer Student~Battlecry~Tradeable"
	requireTarget, effects, description = True, "", "Tradeable. Battlecry: Give a friendly minion Divine Shield"
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()

	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.ID == self and target != self and target.onBoard

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.giveEnchant(target, effGain="Divine Shield", name=TransferStudent_UnitedinStormwind)

#The read transfer student
class TransferStudent(Minion):
	Class, race, name = "Neutral", "", "Transfer Student"
	mana, attack, health = 2, 2, 2
	index = "SCHOLOMANCE~Neutral~Minion~2~2~2~~Transfer Student~Vanilla"
	requireTarget, effects, description = False, "", "This has different effects based on which game board you're on"
	name_CN = "转校生"
	transferStudentPool = {"1 Classic Ogrimmar": TransferStudent_Ogrimmar,
			"2 Classic Stormwind": TransferStudent_Stormwind,
			"3 Classic Stranglethorn": TransferStudent_Stranglethorn,
			"4 Classic Four Wind Valley": TransferStudent_FourWindValley,
			#"5 Naxxramas": TransferStudent_Naxxramas,
			#"6 Goblins vs Gnomes": TransferStudent_GvG,
			#"7 Black Rock Mountain": TransferStudent_BlackRockM,
			#"8 The Grand Tournament": TransferStudent_Tournament,
			#"9 League of Explorers Museum": TransferStudent_LOEMuseum,
			#"10 League of Explorers Ruins": TransferStudent_LOERuins,
			#"11 Corrupted Stormwind": TransferStudent_OldGods,
			#"12 Karazhan": TransferStudent_Karazhan,
			#"13 Gadgetzan": TransferStudent_Gadgetzan,
			#"14 Un'Goro": TransferStudent_UnGoro,
			#"15 Frozen Throne": TransferStudent_FrozenThrone,
			#"16 Kobolds": TransferStudent_Kobold,
			#"17 Witchwood": TransferStudent_Witchwood,
			#"18 Boomsday Lab": TransferStudent_Boomsday,
			#"19 Rumble": TransferStudent_Rumble,
			#"20 Dalaran": TransferStudent_Shadows,
			#"21 Uldum Desert": TransferStudent_UldumDesert,
			#"22 Uldum Oasis": TransferStudent_UldumOasis,
			#"23 Dragons": TransferStudent_Dragons,
			"24 Outlands": TransferStudent_Outlands,
			"25 Scholomance Academy": TransferStudent_Academy,
			"26 Darkmoon Faire": TransferStudent_Darkmoon,
			"27 Barrens": TransferStudent_Barrens,
			"28 United in Stormwind": TransferStudent_UnitedinStormwind,
			}
	

class DeskImp(Minion):
	Class, race, name = "Neutral", "Demon", "Desk Imp"
	mana, attack, health = 0, 1, 1
	index = "SCHOLOMANCE~Neutral~Minion~0~1~1~Demon~Desk Imp"
	requireTarget, effects, description = False, "", ""
	name_CN = "课桌小鬼"
	

class AnimatedBroomstick(Minion):
	Class, race, name = "Neutral", "", "Animated Broomstick"
	mana, attack, health = 1, 1, 1
	index = "SCHOLOMANCE~Neutral~Minion~1~1~1~~Animated Broomstick~Rush~Battlecry"
	requireTarget, effects, description = False, "Rush", "Rush. Battlecry: Give your other minions Rush"
	name_CN = "活化扫帚"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.AOE_GiveEnchant(self.Game.minionsonBoard(self.ID, self), effGain="Rush", name=AnimatedBroomstick)


class IntrepidInitiate(Minion):
	Class, race, name = "Neutral", "", "Intrepid Initiate"
	mana, attack, health = 1, 1, 2
	index = "SCHOLOMANCE~Neutral~Minion~1~1~2~~Intrepid Initiate~Battlecry"
	requireTarget, effects, description = False, "", "Spellburst: Gain +2 Attack"
	name_CN = "新生刺头"
	trigBoard = Trig_IntrepidInitiate		


class PenFlinger(Minion):
	Class, race, name = "Neutral", "", "Pen Flinger"
	mana, attack, health = 1, 1, 1
	index = "SCHOLOMANCE~Neutral~Minion~1~1~1~~Pen Flinger~Battlecry"
	requireTarget, effects, description = True, "", "Battlecry: Deal 1 damage. Spellburst: Return this to your hand"
	name_CN = "甩笔侏儒"
	trigBoard = Trig_PenFlinger		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.dealsDamage(target, 1)
		return target


class SphereofSapience(Weapon):
	Class, name, description = "Neutral", "Sphere of Sapience", "At the start of your turn, look at your top card. You can put it on the bottom and lose 1 Durability"
	mana, attack, durability, effects = 1, 0, 4, ""
	index = "SCHOLOMANCE~Neutral~Weapon~1~0~4~Sphere of Sapience~Neutral~Legendary"
	name_CN = "感知宝珠"
	trigBoard = Trig_SphereofSapience		
	def discoverDecided(self, option, case, info_RNGSync=None, info_GUISync=None):
		if case != "Guided": self.Game.picks_Backup.append((info_RNGSync, info_GUISync, False, type(option)) )
		if isinstance(option, NewFate):
			ownDeck = self.Game.Hand_Deck.decks[self.ID]
			ownDeck.insert(0, ownDeck.pop())
			self.losesDurability()
		

class NewFate(Option):
	name, description = "New Fate", "Draw a new card"
	index = ""
	mana, attack, health = 0, -1, -1
	
		
class TourGuide(Minion):
	Class, race, name = "Neutral", "", "Tour Guide"
	mana, attack, health = 1, 1, 1
	index = "SCHOLOMANCE~Neutral~Minion~1~1~1~~Tour Guide~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Your next Hero Power costs (0)"
	name_CN = "巡游向导"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		GameManaAura_TourGuide(self.Game, self.ID).auraAppears()
		

class CultNeophyte(Minion):
	Class, race, name = "Neutral", "", "Cult Neophyte"
	mana, attack, health = 2, 3, 2
	index = "SCHOLOMANCE~Neutral~Minion~2~3~2~~Cult Neophyte~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Your opponent's spells cost (1) more next turn"
	name_CN = "异教低阶牧师"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		GameManaAura_CultNeophyte(self.Game, 3-self.ID).auraAppears()
		

class ManafeederPanthara(Minion):
	Class, race, name = "Neutral", "Beast", "Manafeeder Panthara"
	mana, attack, health = 2, 2, 3
	index = "SCHOLOMANCE~Neutral~Minion~2~2~3~Beast~Manafeeder Panthara~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: If you've used your Hero Power this turn, draw a card"
	name_CN = "食魔影豹"
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.powerUsagesThisTurn > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Counters.powerUsagesThisTurn > 0:
			self.Game.Hand_Deck.drawCard(self.ID)


class SneakyDelinquent(Minion):
	Class, race, name = "Neutral", "", "Sneaky Delinquent"
	mana, attack, health = 2, 3, 1
	index = "SCHOLOMANCE~Neutral~Minion~2~3~1~~Sneaky Delinquent~Stealth~Deathrattle"
	requireTarget, effects, description = False, "Stealth", "Stealth. Deathrattle: Add a 3/1 Ghost with Stealth to your hand"
	name_CN = "少年惯偷"
	deathrattle = Death_SneakyDelinquent


class SpectralDelinquent(Minion):
	Class, race, name = "Neutral", "", "Spectral Delinquent"
	mana, attack, health = 2, 3, 1
	index = "SCHOLOMANCE~Neutral~Minion~2~3~1~~Spectral Delinquent~Stealth~Uncollectible"
	requireTarget, effects, description = False, "Stealth", "Stealth"
	name_CN = "鬼灵惯偷"


# 不知道疲劳的时候是否会一直抽牌，假设不会


class VoraciousReader(Minion):
	Class, race, name = "Neutral", "", "Voracious Reader"
	mana, attack, health = 3, 1, 3
	index = "SCHOLOMANCE~Neutral~Minion~3~1~3~~Voracious Reader"
	requireTarget, effects, description = False, "", "At the end of your turn, draw until you have 3 cards"
	name_CN = "贪婪的书虫"
	trigBoard = Trig_VoraciousReader		

				
class Wandmaker(Minion):
	Class, race, name = "Neutral", "", "Wandmaker"
	mana, attack, health = 2, 2, 2
	index = "SCHOLOMANCE~Neutral~Minion~2~2~2~~Wandmaker~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Add a 1-Cost spell from your class to your hand"
	name_CN = "魔杖工匠"
	poolIdentifier = "1-Cost Spells as Druid"
	@classmethod
	def generatePool(cls, pools):
		return ["1-Cost Spells as %s"%Class for Class in pools.Classes], \
				[[card for card in pools.ClassCards[Class] if card.category == "Spell" and card.mana == 1] for Class in pools.Classes]
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.addCardtoHand(numpyChoice(self.rngPool("1-Cost Spells as "+self.Game.heroes[self.ID].Class)), self.ID)
		
		
class EducatedElekk(Minion):
	Class, race, name = "Neutral", "Beast", "Educated Elekk"
	mana, attack, health = 3, 3, 4
	index = "SCHOLOMANCE~Neutral~Minion~3~3~4~Beast~Educated Elekk~Deathrattle"
	requireTarget, effects, description = False, "", "Whenever a spell is played, this minion remembers it. Deathrattle: Shuffle the spells into your deck"
	name_CN = "驯化的雷象"
	trigBoard, deathrattle = Trig_EducatedElekk, Death_EducatedElekk


class EnchantedCauldron(Minion):
	Class, race, name = "Neutral", "", "Enchanted Cauldron"
	mana, attack, health = 3, 1, 6
	index = "SCHOLOMANCE~Neutral~Minion~3~1~6~~Enchanted Cauldron"
	requireTarget, effects, description = False, "", "Spellburst: Cast a random spell of the same Cost"
	name_CN = "魔化大锅"
	trigBoard = Trig_EnchantedCauldron
	poolIdentifier = "0-Cost Spells"
	@classmethod
	def generatePool(cls, pools):
		spells = {}
		for Class in pools.Classes:
			for card in pools.ClassCards[Class]:
				if card.category == "Spell": add2ListinDict(card, spells, card.mana)
		return ["%d-Cost Spells"%cost for cost in spells.keys()], list(spells.values())


class RobesofProtection(Minion):
	Class, race, name = "Neutral", "", "Robes of Protection"
	mana, attack, health = 3, 2, 4
	index = "SCHOLOMANCE~Neutral~Minion~3~2~4~~Robes of Protection"
	requireTarget, effects, description = False, "", "Your minions have 'Can't be targeted by spells or Hero Powers'"
	name_CN = "防护长袍"
	aura = Aura_RobesofProtection


class CrimsonHothead(Minion):
	Class, race, name = "Neutral", "Dragon", "Crimson Hothead"
	mana, attack, health = 4, 3, 6
	index = "SCHOLOMANCE~Neutral~Minion~4~3~6~Dragon~Crimson Hothead"
	requireTarget, effects, description = False, "", "Spellburst: Gain +1 Attack and Taunt"
	name_CN = "赤红急先锋"
	trigBoard = Trig_CrimsonHothead


class DivineRager(Minion):
	Class, race, name = "Neutral", "Elemental", "Divine Rager"
	mana, attack, health = 4, 5, 1
	index = "SCHOLOMANCE~Neutral~Minion~4~5~1~Elemental~Divine Rager~Divine Shield"
	requireTarget, effects, description = False, "Divine Shield", "Divine Shield"
	name_CN = "神圣暴怒者"
	

class FishyFlyer(Minion):
	Class, race, name = "Neutral", "Murloc", "Fishy Flyer"
	mana, attack, health = 4, 4, 3
	index = "SCHOLOMANCE~Neutral~Minion~4~4~3~Murloc~Fishy Flyer~Rush~Deathrattle"
	requireTarget, effects, description = False, "Rush", "Rush. Deathrattle: Add a 4/3 Ghost with Rush to your hand"
	name_CN = "鱼人飞骑"
	deathrattle = Death_FishyFlyer


class SpectralFlyer(Minion):
	Class, race, name = "Neutral", "Murloc", "Spectral Flyer"
	mana, attack, health = 4, 4, 3
	index = "SCHOLOMANCE~Neutral~Minion~4~4~3~Murloc~Spectral Flyer~Rush~Uncollectible"
	requireTarget, effects, description = False, "Rush", "Rush"
	name_CN = "鬼灵飞骑"
	
	
class LorekeeperPolkelt(Minion):
	Class, race, name = "Neutral", "", "Lorekeeper Polkelt"
	mana, attack, health = 5, 4, 5
	index = "SCHOLOMANCE~Neutral~Minion~5~4~5~~Lorekeeper Polkelt~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: Reorder your deck from the highest Cost card to the lowest Cost card"
	name_CN = "博学者普克尔特"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		cardDict = {}
		for card in self.Game.Hand_Deck.decks[self.ID]:
			add2ListinDict(card, cardDict, type(card).mana)
		self.Game.Hand_Deck.decks[self.ID] = [] #After sorting using np, the 1st mana is the lowest
		(manas := list(cardDict.keys())).sort() #Doesn't reorder the card of same Cost
		for mana in manas: self.Game.Hand_Deck.decks[self.ID] += cardDict[mana]
		

#可以通过宣传牌确认是施放法术之后触发


class WretchedTutor(Minion):
	Class, race, name = "Neutral", "", "Wretched Tutor"
	mana, attack, health = 4, 2, 5
	index = "SCHOLOMANCE~Neutral~Minion~4~2~5~~Wretched Tutor"
	requireTarget, effects, description = False, "", "Spellburst: Deal 2 damage to all other minions"
	name_CN = "失心辅导员"
	trigBoard = Trig_WretchedTutor


#假设检测方式是在一张法术打出时开始记录直到可以触发法术迸发之前的两次死亡结算中所有死亡随从


class HeadmasterKelThuzad(Minion):
	Class, race, name = "Neutral", "", "Headmaster Kel'Thuzad"
	mana, attack, health = 5, 4, 6
	index = "SCHOLOMANCE~Neutral~Minion~5~4~6~~Headmaster Kel'Thuzad~Legendary"
	requireTarget, effects, description = False, "", "Spellburst: If the spell destroys any minions, summon them"
	name_CN = "校长克尔苏加德"
	trigBoard = Trig_HeadmasterKelThuzad


class LakeThresher(Minion):
	Class, race, name = "Neutral", "Beast", "Lake Thresher"
	mana, attack, health = 5, 4, 6
	index = "SCHOLOMANCE~Neutral~Minion~5~4~6~Beast~Lake Thresher"
	requireTarget, effects, description = False, "Sweep", "Also damages the minions next to whomever this attacks"
	name_CN = "止水湖蛇颈龙"


class Ogremancer(Minion):
	Class, race, name = "Neutral", "", "Ogremancer"
	mana, attack, health = 5, 3, 7
	index = "SCHOLOMANCE~Neutral~Minion~5~3~7~~Ogremancer"
	requireTarget, effects, description = False, "", "Whenever your opponent casts a spell, summon a 2/2 Skeleton with Taunt"
	name_CN = "食人魔巫术师"
	trigBoard = Trig_Ogremancer


class RisenSkeleton(Minion):
	Class, race, name = "Neutral", "", "Risen Skeleton"
	mana, attack, health = 2, 2, 2
	index = "SCHOLOMANCE~Neutral~Minion~2~2~2~~Risen Skeleton~Taunt~Uncollectible"
	requireTarget, effects, description = False, "Taunt", "Taunt"
	name_CN = "复活的骷髅"
	
	
class StewardofScrolls(Minion):
	Class, race, name = "Neutral", "Elemental", "Steward of Scrolls"
	mana, attack, health = 5, 4, 4
	index = "SCHOLOMANCE~Neutral~Minion~5~4~4~Elemental~Steward of Scrolls~Spell Damage~Battlecry"
	requireTarget, effects, description = False, "Spell Damage", "Spell Damage +1. Battlecry: Discover a spell"
	name_CN = "卷轴管理者"
	poolIdentifier = "Demon Hunter Spells"
	@classmethod
	def generatePool(cls, pools):
		return [Class+" Spells" for Class in pools.Classes], \
				[[card for card in pools.ClassCards[Class] if card.category == "Spell"] for Class in pools.Classes]
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverandGenerate(StewardofScrolls, comment, lambda : self.rngPool(classforDiscover(self) + " Spells"))
		
		
class Vectus(Minion):
	Class, race, name = "Neutral", "", "Vectus"
	mana, attack, health = 5, 4, 4
	index = "SCHOLOMANCE~Neutral~Minion~5~4~4~~Vectus~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: Summon two 1/1 Whelps. Each gains a Deathrattle from your minions that died this game"
	name_CN = "维克图斯"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		whelp1, whelp2 = PlaguedHatchling(self.Game, self.ID), PlaguedHatchling(self.Game, self.ID)
		deathrattle1 = deathrattle2 = None
		if minions := [card for card in self.Game.Counters.minionsDiedThisGame[self.ID] if "~Deathrattle" in card.index]:
			deathrattle1, deathrattle2 = [numpyChoice(minions).deathrattle, numpyChoice(minions).deathrattle]
		self.summon((whelp1, whelp2), relative="<>")
		if deathrattle1:
			self.giveEnchant(whelp1, trig=deathrattle1, trigType="Deathrattle")
			self.giveEnchant(whelp2, trig=deathrattle2, trigType="Deathrattle")
		

class PlaguedHatchling(Minion):
	Class, race, name = "Neutral", "Dragon", "Plagued Hatchling"
	mana, attack, health = 1, 1, 1
	index = "SCHOLOMANCE~Neutral~Minion~1~1~1~Dragon~Plagued Hatchling~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "魔药龙崽"
	
	
class OnyxMagescribe(Minion):
	Class, race, name = "Neutral", "Dragon", "Onyx Magescribe"
	mana, attack, health = 6, 4, 9
	index = "SCHOLOMANCE~Neutral~Minion~6~4~9~Dragon~Onyx Magescribe"
	requireTarget, effects, description = False, "", "Spellburst: Add 2 random spells from your class to your hand"
	name_CN = "黑岩法术抄写员"
	trigBoard = Trig_OnyxMagescribe
	poolIdentifier = "Druid Spells"
	@classmethod
	def generatePool(cls, pools):
		return [Class + " Spells" for Class in pools.Classes], \
			   [[card for card in pools.ClassCards[Class] if card.category == "Spell"] for Class in pools.Classes]


class SmugSenior(Minion):
	Class, race, name = "Neutral", "", "Smug Senior"
	mana, attack, health = 6, 5, 7
	index = "SCHOLOMANCE~Neutral~Minion~6~5~7~~Smug Senior~Taunt~Deathrattle"
	requireTarget, effects, description = False, "Taunt", "Taunt. Deathrattle: Add a 5/7 Ghost with Taunt to your hand"
	name_CN = "浮夸的大四学长"
	deathrattle = Death_SmugSenior


class SpectralSenior(Minion):
	Class, race, name = "Neutral", "", "Spectral Senior"
	mana, attack, health = 6, 5, 7
	index = "SCHOLOMANCE~Neutral~Minion~6~5~7~~Spectral Senior~Taunt~Uncollectible"
	requireTarget, effects, description = False, "Taunt", "Taunt"
	name_CN = "鬼灵学长"
	
	
class SorcerousSubstitute(Minion):
	Class, race, name = "Neutral", "", "Sorcerous Substitute"
	mana, attack, health = 6, 6, 6
	index = "SCHOLOMANCE~Neutral~Minion~6~6~6~~Sorcerous Substitute~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: If you have Spell Damage, summon a copy of this"
	name_CN = "巫术替身"
	def effCanTrig(self):
		self.effectViable =  self.countSpellDamage() > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.countSpellDamage() > 0:
			Copy = self.selfCopy(self.ID, self) if self.onBoard else type(self)(self.Game, self.ID)
			self.summon(Copy)
		
		
class KeymasterAlabaster(Minion):
	Class, race, name = "Neutral", "", "Keymaster Alabaster"
	mana, attack, health = 7, 6, 8
	index = "SCHOLOMANCE~Neutral~Minion~7~6~8~~Keymaster Alabaster~Legendary"
	requireTarget, effects, description = False, "", "Whenever your opponent draws a card, add a copy to your hand that costs (1)"
	name_CN = "钥匙专家阿拉巴斯特"
	trigBoard = Trig_KeymasterAlabaster


class PlaguedProtodrake(Minion):
	Class, race, name = "Neutral", "Dragon", "Plagued Protodrake"
	mana, attack, health = 8, 8, 8
	index = "SCHOLOMANCE~Neutral~Minion~8~8~8~Dragon~Plagued Protodrake~Deathrattle"
	requireTarget, effects, description = False, "", "Deathrattle: Summon a random 7-Cost minion"
	name_CN = "魔药始祖龙"
	deathrattle = Death_PlaguedProtodrake
	poolIdentifier = "7-Cost Minions to Summon"
	@classmethod
	def generatePool(cls, pools):
		return "7-Cost Minions to Summon", pools.MinionsofCost[7]


"""Demon Hunter Cards"""
class DemonCompanion(Spell):
	Class, school, name = "Demon Hunter,Hunter", "", "Demon Companion"
	requireTarget, mana, effects = False, 1, ""
	index = "SCHOLOMANCE~Demon Hunter,Hunter~Spell~1~~Demon Companion"
	description = "Summon a random Demon Companion"
	name_CN = "恶魔伙伴"
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon(numpyChoice((Reffuh, Kolek, Shima))(self.Game, self.ID))

class Reffuh(Minion):
	Class, race, name = "Demon Hunter,Hunter", "Demon", "Reffuh"
	mana, attack, health = 1, 2, 1
	index = "SCHOLOMANCE~Demon Hunter,Hunter~Minion~1~2~1~Demon~Reffuh~Charge~Uncollectible"
	requireTarget, effects, description = False, "Charge", "Charge"
	name_CN = "弗霍"

class Kolek(Minion):
	Class, race, name = "Demon Hunter,Hunter", "Demon", "Kolek"
	mana, attack, health = 1, 1, 2
	index = "SCHOLOMANCE~Demon Hunter,Hunter~Minion~1~1~2~Demon~Kolek~Uncollectible"
	requireTarget, effects, description = False, "", "Your other minions have +1 Attack"
	name_CN = "克欧雷"
	aura = Aura_Kolek

class Shima(Minion):
	Class, race, name = "Demon Hunter,Hunter", "Demon", "Shima"
	mana, attack, health = 1, 2, 2
	index = "SCHOLOMANCE~Demon Hunter,Hunter~Minion~1~2~2~Demon~Shima~Taunt~Uncollectible"
	requireTarget, effects, description = False, "Taunt", "Taunt"
	name_CN = "莎米"
	
	
class DoubleJump(Spell):
	Class, school, name = "Demon Hunter", "", "Double Jump"
	requireTarget, mana, effects = False, 1, ""
	index = "SCHOLOMANCE~Demon Hunter~Spell~1~~Double Jump"
	description = "Draw an Outcast card from your deck"
	name_CN = "二段跳"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.drawCertainCard(lambda card: "~Outcast" in card.index)
		
		
#即使是被冰冻的随从也可以因为这个效果进行攻击，同时攻击不浪费攻击机会，同时可以触发巨型沙虫等随从的获得额外的攻击机会
class TrueaimCrescent(Weapon):
	Class, name, description = "Demon Hunter,Hunter", "Trueaim Crescent", "After your hero attacks a minion, your minions attack it too"
	mana, attack, durability, effects = 1, 1, 4, ""
	index = "SCHOLOMANCE~Demon Hunter,Hunter~Weapon~1~1~4~Trueaim Crescent"
	name_CN = "引月长弓"
	trigBoard = Trig_TrueaimCrescent


class AceHunterKreen(Minion):
	Class, race, name = "Demon Hunter,Hunter", "", "Ace Hunter Kreen"
	mana, attack, health = 3, 2, 4
	index = "SCHOLOMANCE~Demon Hunter,Hunter~Minion~3~2~4~~Ace Hunter Kreen~Legendary"
	requireTarget, effects, description = False, "", "Your other characters are Immune while attacking"
	name_CN = "金牌猎手克里"
	trigBoard = Trig_AceHunterKreen


class Magehunter(Minion):
	Class, race, name = "Demon Hunter", "", "Magehunter"
	mana, attack, health = 3, 2, 3
	index = "SCHOLOMANCE~Demon Hunter~Minion~3~2~3~~Magehunter~Rush"
	requireTarget, effects, description = False, "Rush", "Rush. Whenever this attacks a minion, Silence it"
	name_CN = "法师猎手"
	trigBoard = Trig_Magehunter


class ShardshatterMystic(Minion):
	Class, race, name = "Demon Hunter", "", "Shardshatter Mystic"
	mana, attack, health = 4, 3, 2
	index = "SCHOLOMANCE~Demon Hunter~Minion~4~3~2~~Shardshatter Mystic~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Destroy a Soul Fragment in your deck to deal 3 damage to all other minions"
	name_CN = "残片震爆秘术师"
	def effCanTrig(self):
		self.effectViable = any(isinstance(card, SoulFragment) for card in self.Game.Hand_Deck.decks[self.ID])
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if destroyaSoulFragment(self.Game, self.ID):
			minions = self.Game.minionsonBoard(self.ID, self) + self.Game.minionsonBoard(3-self.ID)
			self.AOE_Damage(minions, [3]*len(minions))
		
		
class Glide(Spell):
	Class, school, name = "Demon Hunter", "", "Glide"
	requireTarget, mana, effects = False, 4, ""
	index = "SCHOLOMANCE~Demon Hunter~Spell~4~~Glide~Outcast"
	description = "Shuffle your hand into your deck. Draw 4 cards. Outcast: Your opponent does the same"
	name_CN = "滑翔"
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.outcastcanTrig(self)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.Hand_Deck.shuffle_Hand2Deck(0, self.ID, initiatorID=self.ID, shuffleAll=True)
		for i in (0, 1, 2, 3): self.Game.Hand_Deck.drawCard(self.ID)
		if posinHand == 0 or posinHand == -1:
			self.Game.Hand_Deck.shuffle_Hand2Deck(0, 3 - self.ID, initiatorID=self.ID, shuffleAll=True)
			for i in (0, 1, 2, 3): self.Game.Hand_Deck.drawCard(3-self.ID)
		
		
class Marrowslicer(Weapon):
	Class, name, description = "Demon Hunter", "Marrowslicer", "Battlecry: Shuffle 2 Soul Fragments into your deck"
	mana, attack, durability, effects = 4, 4, 2, ""
	index = "SCHOLOMANCE~Demon Hunter~Weapon~4~4~2~Marrowslicer~Battlecry"
	name_CN = "切髓之刃"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.shuffleintoDeck([SoulFragment(self.Game, self.ID) for _ in (0, 1)])
		

class SoulFragment(Spell):
	Class, school, name = "Warlock,Demon Hunter", "", "Soul Fragment"
	requireTarget, mana, effects = False, 0, ""
	index = "SCHOLOMANCE~Warlock,Demon Hunter~Spell~0~~Soul Fragment~Casts When Drawn~Uncollectible"
	description = "Restore 2 Health to your hero"
	name_CN = "灵魂残片"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.restoresHealth(self.Game.heroes[self.ID], self.calcHeal(2))
		
		
class StarStudentStelina(Minion):
	Class, race, name = "Demon Hunter", "", "Star Student Stelina"
	mana, attack, health = 4, 4, 3
	index = "SCHOLOMANCE~Demon Hunter~Minion~4~4~3~~Star Student Stelina~Outcast~Legendary"
	requireTarget, effects, description = False, "", "Outcast: Look at 3 cards in your opponent's hand. Shuffle one of them into their deck"
	name_CN = "明星学员斯特里娜"

	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.outcastcanTrig(self)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if posinHand == 0 or posinHand == -1:
			self.discoverfromList(StarStudentStelina, '', ls=self.Game.Hand_Deck.hands[3-self.ID])

	def discoverDecided(self, option, case, info_RNGSync=None, info_GUISync=None):
		self.handleDiscoveredCardfromList(option, case, ls=self.Game.Hand_Deck.hands[3 - self.ID],
										  func=lambda index, card: self.Game.Hand_Deck.shuffle_Hand2Deck(index, 3 - self.ID, initiatorID=self.ID, shuffleAll=False),
										  info_RNGSync=info_RNGSync, info_GUISync=info_GUISync)
		
		
class VilefiendTrainer(Minion):
	Class, race, name = "Demon Hunter", "", "Vilefiend Trainer"
	mana, attack, health = 4, 5, 4
	index = "SCHOLOMANCE~Demon Hunter~Minion~4~5~4~~Vilefiend Trainer~Outcast"
	requireTarget, effects, description = False, "", "Outcast: Summon two 1/1 Demons"
	name_CN = "邪犬训练师"

	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.outcastcanTrig(self)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if posinHand == 0 or posinHand == -1:
			self.summon([SnarlingVilefiend(self.Game, self.ID) for _ in (0, 1)], relative="<>")
		

class SnarlingVilefiend(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Snarling Vilefiend"
	mana, attack, health = 1, 1, 1
	index = "SCHOLOMANCE~Demon Hunter~Minion~1~1~1~Demon~Snarling Vilefiend~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "咆哮的邪犬"


class BloodHerald(Minion):
	Class, race, name = "Demon Hunter,Hunter", "", "Blood Herald"
	mana, attack, health = 5, 1, 1
	index = "SCHOLOMANCE~Demon Hunter,Hunter~Minion~5~1~1~~Blood Herald"
	requireTarget, effects, description = False, "", "Whenever a friendly minion dies while this is in your hand, gain +1/+1"
	trigHand = Trig_BloodHerald
	name_CN = "嗜血传令官"


class SoulshardLapidary(Minion):
	Class, race, name = "Demon Hunter", "", "Soulshard Lapidary"
	mana, attack, health = 5, 5, 5
	index = "SCHOLOMANCE~Demon Hunter~Minion~5~5~5~~Soulshard Lapidary~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Destroy a Soul Fragment in your deck to give your hero +5 Attack this turn"
	name_CN = "铸魂宝石匠"
	
	def effCanTrig(self):
		self.effectViable = any(isinstance(card, SoulFragment) for card in self.Game.Hand_Deck.decks[self.ID])
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if destroyaSoulFragment(self.Game, self.ID): self.giveHeroAttackArmor(self.ID, attGain=5, name=SoulshardLapidary)
		
		
class CycleofHatred(Spell):
	Class, school, name = "Demon Hunter", "", "Cycle of Hatred"
	requireTarget, mana, effects = False, 7, ""
	index = "SCHOLOMANCE~Demon Hunter~Spell~7~~Cycle of Hatred"
	description = "Deal 3 damage to all minions. Summon a 3/3 Spirit for every minion killed"
	name_CN = "仇恨之轮"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = self.calcDamage(3)
		targets = self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)
		dmgTakers = self.AOE_Damage(targets, [damage]*len(targets))[0]
		num = 0
		for dmgTaker in dmgTakers:
			if dmgTaker.dead or dmgTaker.health < 1: num += 1
		if num > 0:
			self.summon([SpiritofVengeance(self.Game, self.ID) for i in range(num)])
		

class SpiritofVengeance(Minion):
	Class, race, name = "Demon Hunter", "", "Spirit of Vengeance"
	mana, attack, health = 3, 3, 3
	index = "SCHOLOMANCE~Demon Hunter~Minion~3~3~3~~Spirit of Vengeance~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "复仇之魂"


class FelGuardians(Spell):
	Class, school, name = "Demon Hunter", "Fel", "Fel Guardians"
	requireTarget, mana, effects = False, 7, ""
	index = "SCHOLOMANCE~Demon Hunter~Spell~7~Fel~Fel Guardians"
	description = "Summon three 1/2 Demons with Taunt. Costs (1) less whenever a friendly minion dies"
	trigHand = Trig_FelGuardians
	name_CN = "邪能护卫"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon([SoulfedFelhound(self.Game, self.ID) for _ in (0, 1, 2)])


class SoulfedFelhound(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Soulfed Felhound"
	mana, attack, health = 1, 1, 2
	index = "SCHOLOMANCE~Demon Hunter~Minion~1~1~2~Demon~Soulfed Felhound~Taunt~Uncollectible"
	requireTarget, effects, description = False, "Taunt", "Taunt"
	name_CN = "食魂地狱犬"
	
	
class AncientVoidHound(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Ancient Void Hound"
	mana, attack, health = 9, 10, 10
	index = "SCHOLOMANCE~Demon Hunter~Minion~9~10~10~Demon~Ancient Void Hound"
	requireTarget, effects, description = False, "", "At the end of your turn, steal 1 Attack and Health from all enemy minions"
	name_CN = "上古虚空恶犬"
	trigBoard = Trig_AncientVoidHound


"""Druid Cards"""
class LightningBloom(Spell):
	Class, school, name = "Druid,Shaman", "Nature", "Lightning Bloom"
	requireTarget, mana, effects = False, 0, ""
	index = "SCHOLOMANCE~Druid,Shaman~Spell~0~Nature~Lightning Bloom~Overload"
	description = "Gain 2 Mana Crystals this turn only. Overload: (2)"
	name_CN = "雷霆绽放"
	overload = 2

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.Manas.gainTempManaCrystal(2, ID=self.ID)
		

class Gibberling(Minion):
	Class, race, name = "Druid", "", "Gibberling"
	mana, attack, health = 2, 1, 1
	index = "SCHOLOMANCE~Druid~Minion~2~1~1~~Gibberling"
	requireTarget, effects, description = False, "", "Spellburst: Summon a Gibberling"
	name_CN = "聒噪怪"
	trigBoard = Trig_Gibberling


class NatureStudies(Spell):
	Class, school, name = "Druid", "Nature", "Nature Studies"
	requireTarget, mana, effects = False, 1, ""
	index = "SCHOLOMANCE~Druid~Spell~1~Nature~Nature Studies"
	description = "Discover a spell. Your next one costs (1) less"
	name_CN = "自然研习"
	poolIdentifier = "Druid Spells"
	@classmethod
	def generatePool(cls, pools):
		return [Class + " Spells" for Class in pools.Classes], \
			   [[card for card in pools.ClassCards[Class] if card.category == "Spell"] for Class in pools.Classes]
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverandGenerate(NatureStudies, comment, lambda : self.rngPool(classforDiscover(self) + " Spells"))
		GameManaAura_NatureStudies(self.Game, self.ID).auraAppears()
		

class PartnerAssignment(Spell):
	Class, school, name = "Druid", "", "Partner Assignment"
	requireTarget, mana, effects = False, 1, ""
	index = "SCHOLOMANCE~Druid~Spell~1~~Partner Assignment"
	description = "Add a random 2-Cost and 3-Cost Beast to your hand"
	name_CN = "分配组员"
	poolIdentifier = "2-Cost Beasts"
	@classmethod
	def generatePool(cls, pools):
		return ["2-Cost Beasts", "3-Cost Beasts"], \
				[[card for card in pools.MinionswithRace["Beast"] if card.mana == 2],
					[card for card in pools.MinionswithRace["Beast"] if card.mana == 3]]
					
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		beasts = [numpyChoice(self.rngPool("2-Cost Beasts")), numpyChoice(self.rngPool("3-Cost Beasts"))]
		self.addCardtoHand(beasts, self.ID)


class SpeakerGidra(Minion):
	Class, race, name = "Druid", "", "Speaker Gidra"
	mana, attack, health = 3, 1, 4
	index = "SCHOLOMANCE~Druid~Minion~3~1~4~~Speaker Gidra~Rush~Windfury~Legendary"
	requireTarget, effects, description = False, "Rush,Windfury", "Rush, Windfury. Spellburst: Gain Attack and Health equal to the spell's Cost"
	name_CN = "演讲者吉德拉"
	trigBoard = Trig_SpeakerGidra		

		
class Groundskeeper(Minion):
	Class, race, name = "Druid,Shaman", "", "Groundskeeper"
	mana, attack, health = 4, 4, 5
	index = "SCHOLOMANCE~Druid,Shaman~Minion~4~4~5~~Groundskeeper~Taunt~Battlecry"
	requireTarget, effects, description = True, "Taunt", "Taunt. Battlecry: If you're holding a spell that costs (5) or more, restore 5 Health"
	name_CN = "园地管理员"
	
	def needTarget(self, choice=0):
		return self.Game.Hand_Deck.holdingSpellwith5CostorMore(self.ID)
		
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.holdingSpellwith5CostorMore(self.ID)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and self.Game.Hand_Deck.holdingSpellwith5CostorMore(self.ID):
			self.restoresHealth(target, self.calcHeal(5))
		return target


class TwilightRunner(Minion):
	Class, race, name = "Druid", "Beast", "Twilight Runner"
	mana, attack, health = 5, 5, 4
	index = "SCHOLOMANCE~Druid~Minion~5~5~4~Beast~Twilight Runner~Stealth"
	requireTarget, effects, description = False, "Stealth", "Stealth. Whenever this attacks, draw 2 cards"
	name_CN = "夜行虎"
	trigBoard = Trig_TwilightRunner		


class ForestWardenOmu(Minion):
	Class, race, name = "Druid", "", "Forest Warden Omu"
	mana, attack, health = 6, 5, 4
	index = "SCHOLOMANCE~Druid~Minion~6~5~4~~Forest Warden Omu~Legendary"
	requireTarget, effects, description = False, "", "Spellburst: Refresh your Mana Crystals"
	name_CN = "林地守护者欧穆"
	trigBoard = Trig_ForestWardenOmu		


class CalltoAid(Spell):
	Class, school, name = "Druid,Shaman", "Nature", "Call to Aid"
	requireTarget, mana, effects = False, 6, ""
	index = "SCHOLOMANCE~Druid,Shaman~Spell~6~Nature~Call to Aid~Uncollectible"
	description = "Summon four 2/2 Treant Totems"
	name_CN = "呼叫增援"
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon([TreantTotem(self.Game, self.ID) for i in (0, 1, 2, 3)])
		
class AlarmtheForest(Spell):
	Class, school, name = "Druid,Shaman", "Nature", "Alarm the Forest"
	requireTarget, mana, effects = False, 6, ""
	index = "SCHOLOMANCE~Druid,Shaman~Spell~6~Nature~Alarm the Forest~Overload~Uncollectible"
	description = "Summon four 2/2 Treant Totems with Rush. Overload: (2)"
	name_CN = "警醒森林"
	overload = 2
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		minions = [TreantTotem(self.Game, self.ID) for i in (0, 1, 2, 3)]
		self.summon(minions)
		self.AOE_GiveEnchant([minion for minion in minions if minion.onBoard], effGain="Rush", name=AlarmtheForest)
		
class CalltoAid_Option(Option):
	name, description = "Call to Aid", "Summon four 2/2 Treant Totems"
	mana, attack, health = 6, -1, -1
	spell = CalltoAid
	def available(self):
		return self.keeper.Game.space(self.keeper.ID) > 0

class AlarmtheForest_Option(Option):
	name, description = "Alarm the Forest", "Summon four 2/2 Treant Totems with Rush. Overload: (2)"
	mana, attack, health = 6, -1, -1
	spell = AlarmtheForest
	def available(self):
		return self.keeper.Game.space(self.keeper.ID) > 0

class RunicCarvings(Spell):
	Class, school, name = "Druid,Shaman", "Nature", "Runic Carvings"
	requireTarget, mana, effects = False, 6, ""
	index = "SCHOLOMANCE~Druid,Shaman~Spell~6~Nature~Runic Carvings~Choose One"
	description = "Choose One - Summon four 2/2 Treant Totems; or Overload: (2) to given them Rush"
	name_CN = "雕琢符文"
	options = (CalltoAid_Option, AlarmtheForest_Option)
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		minions = [TreantTotem(self.Game, self.ID) for i in (0, 1, 2, 3)]
		self.summon(minions)
		if choice != 0:
			self.Game.Manas.overloadMana(2, self.ID)
			self.AOE_GiveEnchant([minion for minion in minions if minion.onBoard], effGain="Rush", name=AlarmtheForest)

class TreantTotem(Minion):
	Class, race, name = "Druid,Shaman", "Totem", "Treant Totem"
	mana, attack, health = 2, 2, 2
	index = "SCHOLOMANCE~Druid,Shaman~Minion~2~2~2~Totem~Treant Totem~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "树人图腾"
	
	
class SurvivaloftheFittest(Spell):
	Class, school, name = "Druid", "", "Survival of the Fittest"
	requireTarget, mana, effects = False, 10, ""
	index = "SCHOLOMANCE~Druid~Spell~10~~Survival of the Fittest"
	description = "Give +4/+4 to all minions in your hand, deck, and battlefield"
	name_CN = "优胜劣汰"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.AOE_GiveEnchant([card for card in self.Game.Hand_Deck.hands[self.ID] if card.category == "Minion"],
							 4, 4, name=SurvivaloftheFittest, add2EventinGUI=False)
		typeSelf = type(self)
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if card.category == "Minion": card.getsBuffDebuff_inDeck(4, 4, source=typeSelf, name=SurvivaloftheFittest)
		self.AOE_GiveEnchant(self.Game.minionsonBoard(self.ID), 4, 4, name=SurvivaloftheFittest)
		

"""Hunter Cards"""
class AdorableInfestation(Spell):
	Class, school, name = "Hunter,Druid", "", "Adorable Infestation"
	requireTarget, mana, effects = True, 1, ""
	index = "SCHOLOMANCE~Hunter,Druid~Spell~1~~Adorable Infestation"
	description = "Give a minion +1/+1. Summon a 1/1 Cub. Add a Cub to your hand"
	name_CN = "萌物来袭"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.giveEnchant(target, 1, 1, name=AdorableInfestation)
			self.summon(MarsuulCub(self.Game, self.ID))
			self.addCardtoHand(MarsuulCub, self.ID)
		return target
		

class MarsuulCub(Minion):
	Class, race, name = "Hunter,Druid", "Beast", "Marsuul Cub"
	mana, attack, health = 1, 1, 1
	index = "SCHOLOMANCE~Hunter,Druid~Minion~1~1~1~Beast~Marsuul Cub~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "魔鼠宝宝"
	
	
class CarrionStudies(Spell):
	Class, school, name = "Hunter", "", "Carrion Studies"
	requireTarget, mana, effects = False, 1, ""
	index = "SCHOLOMANCE~Hunter~Spell~1~~Carrion Studies"
	description = "Discover a Deathrattle minion. Your next one costs (1) less"
	name_CN = "腐食研习"
	poolIdentifier = "Deathrattle Minions as Hunter"
	@classmethod
	def generatePool(cls, pools):
		classCards = {s: [card for card in pools.ClassCards[s] if card.category == "Minion" and "~Deathrattle" in card.index] for s in pools.Classes}
		classCards["Neutral"] = [card for card in pools.NeutralCards if card.category == "Minion" and "~Deathrattle" in card.index]
		return ["Deathrattle Minions as "+Class for Class in pools.Classes], \
				[classCards[Class]+classCards["Neutral"] for Class in pools.Classes]
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverandGenerate(CarrionStudies, comment, lambda : self.rngPool("Deathrattle Minions as " + classforDiscover(self)))
		GameManaAura_CarrionStudies(self.Game, self.ID).auraAppears()
		

class Overwhelm(Spell):
	Class, school, name = "Hunter", "", "Overwhelm"
	requireTarget, mana, effects = True, 1, ""
	index = "SCHOLOMANCE~Hunter~Spell~1~~Overwhelm"
	description = "Deal 2 damage to a minion. Deal one more damage for each Beast you control"
	name_CN = "数量压制"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard
		
	def text(self): return self.calcDamage(2 + sum("Beast" in minion.race for minion in self.Game.minionsonBoard(self.ID)))
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = self.calcDamage(2 + sum("Beast" in minion.race for minion in self.Game.minionsonBoard(self.ID)))
			self.dealsDamage(target, damage)
		return target
		

class Wolpertinger(Minion):
	Class, race, name = "Hunter", "Beast", "Wolpertinger"
	mana, attack, health = 1, 1, 1
	index = "SCHOLOMANCE~Hunter~Minion~1~1~1~Beast~Wolpertinger~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Summon a copy of this"
	name_CN = "鹿角小飞兔"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		Copy = self.selfCopy(self.ID, self) if self.onBoard else type(self)(self.Game, self.ID)
		self.summon(Copy)
		
		
class BloatedPython(Minion):
	Class, race, name = "Hunter", "Beast", "Bloated Python"
	mana, attack, health = 3, 1, 2
	index = "SCHOLOMANCE~Hunter~Minion~3~1~2~Beast~Bloated Python~Deathrattle"
	requireTarget, effects, description = False, "", "Deathrattle: Summon a 4/4 Hapless Handler"
	name_CN = "饱腹巨蟒"
	deathrattle = Death_BloatedPython


class HaplessHandler(Minion):
	Class, race, name = "Hunter", "", "Hapless Handler"
	mana, attack, health = 4, 4, 4
	index = "SCHOLOMANCE~Hunter~Minion~4~4~4~~Hapless Handler~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "倒霉的管理员"


class ProfessorSlate(Minion):
	Class, race, name = "Hunter", "", "Professor Slate"
	mana, attack, health = 3, 3, 4
	index = "SCHOLOMANCE~Hunter~Minion~3~3~4~~Professor Slate~Legendary"
	requireTarget, effects, description = False, "", "Your spells are Poisonous"
	name_CN = "斯雷特教授"
	aura = GameRuleAura_ProfessorSlate


class RiletheHerd_Option(Option):
	name, description = "", "Give Beasts in your deck +1/+1"
	mana, attack, health = -1, -1, -1

class Transfiguration_Option(Option):
	name, description = "", "Transform into a copy of a friendly Beast"
	mana, attack, health = -1, -1, -1
	def available(self):
		return self.keeper.targetExists(1)

class ShandoWildclaw(Minion):
	Class, race, name = "Hunter,Druid", "", "Shan'do Wildclaw"
	mana, attack, health = 3, 3, 3
	index = "SCHOLOMANCE~Hunter,Druid~Minion~3~3~3~~Shan'do Wildclaw~Choose One~Legendary"
	requireTarget, effects, description = True, "", "Choose One- Give Beasts in your deck +1/+1; or Transform into a copy of a friendly Beast"
	name_CN = "大导师野爪"
	options = (RiletheHerd_Option, Transfiguration_Option)

	def needTarget(self, choice=0):
		return choice != 0
		
	def targetExists(self, choice=1):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=1):
		return target.category == "Minion" and "Beast" in target.race and target.ID == self.ID and target != self and target.onBoard
		
	#对于抉择随从而言，应以与战吼类似的方式处理，打出时抉择可以保持到最终结算。但是打出时，如果因为鹿盔和发掘潜力而没有选择抉择，视为到对方场上之后仍然可以而没有如果没有
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if choice < 1: #Choose Both aura on or choice == 0
			typeSelf = type(self)
			for card in self.Game.Hand_Deck.decks[self.ID]:
				if "Beast" in card.race: card.getsBuffDebuff_inDeck(1, 1, source=typeSelf, name=ShandoWildclaw)
		if choice != 0 and target:
			if target and self.dead == False and self.Game.minionPlayed == self and (self.onBoard or self.inHand): #战吼触发时自己不能死亡。
				Copy = target.selfCopy(self.ID, self) if target.onBoard else type(target)(self.Game, self.ID)
				self.transform(self, Copy)
		return target


class KroluskBarkstripper(Minion):
	Class, race, name = "Hunter", "Beast", "Krolusk Barkstripper"
	mana, attack, health = 4, 3, 5
	index = "SCHOLOMANCE~Hunter~Minion~4~3~5~Beast~Krolusk Barkstripper"
	requireTarget, effects, description = False, "", "Spellburst: Destroy a random enemy minion"
	name_CN = "裂树三叶虫"
	trigBoard = Trig_KroluskBarkstripper


class TeachersPet(Minion):
	Class, race, name = "Hunter,Druid", "Beast", "Teacher's Pet"
	mana, attack, health = 5, 4, 5
	index = "SCHOLOMANCE~Hunter,Druid~Minion~5~4~5~Beast~Teacher's Pet~Taunt~Deathrattle"
	requireTarget, effects, description = False, "Taunt", "Taunt. Deathrattle: Summon a 3-Cost Beast"
	name_CN = "教师的爱宠"
	deathrattle = Death_TeachersPet
	poolIdentifier = "3-Cost Beasts to Summon"
	@classmethod
	def generatePool(cls, pools):
		return "3-Cost Beasts to Summon", [card for card in pools.MinionswithRace["Beast"] if card.mana == 3]

		
class GuardianAnimals(Spell):
	Class, school, name = "Hunter,Druid", "", "Guardian Animals"
	requireTarget, mana, effects = False, 8, ""
	index = "SCHOLOMANCE~Hunter,Druid~Spell~8~~Guardian Animals"
	description = "Summon two Beasts that cost (5) or less from your deck. Give them Rush"
	name_CN = "动物保镖"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for _ in (0, 1):
			if beast := self.try_SummonfromDeck(func=lambda card: "Beast" in card.race and card.mana < 6):
				self.giveEnchant(beast, effGain="Rush", name=GuardianAnimals)
			else: break
		

"""Mage Cards"""
class BrainFreeze(Spell):
	Class, school, name = "Mage,Rogue", "Frost", "Brain Freeze"
	requireTarget, mana, effects = True, 1, ""
	index = "SCHOLOMANCE~Mage,Rogue~Spell~1~Frost~Brain Freeze~Combo"
	description = "Freeze a minion. Combo: Also deal 3 damage to it"
	name_CN = "冰冷智慧"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard
		
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0
		
	def text(self): return self.calcDamage(3)
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.freeze(target)
			if self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0:
				self.dealsDamage(target, self.calcDamage(3))
		return target
		
		
class DevolvingMissiles(Spell):
	Class, school, name = "Shaman,Mage", "Arcane", "Devolving Missiles"
	requireTarget, mana, effects = False, 1, ""
	index = "SCHOLOMANCE~Shaman,Mage~Spell~1~Arcane~Devolving Missiles"
	description = "Shoot three missiles at random enemy minions that transform them into ones that cost (1) less"
	name_CN = "衰变飞弹"
	poolIdentifier = "0-Cost Minions to summon"
	@classmethod
	def generatePool(cls, pools):
		return ["%d-Cost Minions to Summon" % cost for cost in pools.MinionsofCost.keys()], \
			   list(pools.MinionsofCost.values())
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		side, game = 3 - self.ID, self.Game
		for _ in (0, 1, 2):
			if minions := game.minionsonBoard(side):
				minion = numpyChoice(minions)
				self.transform(minion, self.newEvolved(type(minion).mana, by=-1, ID=side))
			else: break
			
		
		
class LabPartner(Minion):
	Class, race, name = "Mage", "", "Lab Partner"
	mana, attack, health = 1, 1, 3
	index = "SCHOLOMANCE~Mage~Minion~1~1~3~~Lab Partner~Spell Damage"
	requireTarget, effects, description = False, "Spell Damage", "Spell Damage +1"
	name_CN = "研究伙伴"
	
	
class WandThief(Minion):
	Class, race, name = "Mage,Rogue", "", "Wand Thief"
	mana, attack, health = 1, 1, 2
	index = "SCHOLOMANCE~Mage,Rogue~Minion~1~1~2~~Wand Thief~Combo"
	requireTarget, effects, description = False, "", "Combo: Discover a Mage spell"
	name_CN = "魔杖窃贼"
	poolIdentifier = "Mage Spells"
	@classmethod
	def generatePool(cls, pools):
		return "Mage Spells", [card for card in pools.ClassCards["Mage"] if card.category == "Spell"]
		
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0:
			self.discoverandGenerate(WandThief, '', lambda : self.rngPool("Mage Spells"))
		
	def discoverDecided(self, option, case, info_RNGSync=None, info_GUISync=None):
		self.handleDiscoverGeneratedCard(option, case, info_RNGSync, info_GUISync)
		
		
class CramSession(Spell):
	Class, school, name = "Mage", "Arcane", "Cram Session"
	requireTarget, mana, effects = False, 2, ""
	index = "SCHOLOMANCE~Mage~Spell~2~Arcane~Cram Session"
	description = "Draw 1 card (improved by Spell Damage)"
	name_CN = "考前刷夜"
	def text(self): return 1 + self.countSpellDamage()

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for i in range(1 + self.countSpellDamage()): self.Game.Hand_Deck.drawCard(self.ID)
		
		
class Combustion(Spell):
	Class, school, name = "Mage", "Fire", "Combustion"
	requireTarget, mana, effects = True, 3, ""
	index = "SCHOLOMANCE~Mage~Spell~3~Fire~Combustion"
	description = "Deal 4 damage to a minion. Any excess damages both neighbors"
	name_CN = "燃烧"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = self.calcDamage(4)
			damageUsed = max(0, min(target.health, damage))
			damageLeft = damage - damageUsed
			if target.onBoard and damageLeft:
				neighbors = self.Game.neighbors2(target)[0]
				targets = [target] + neighbors
				damages = [damageUsed] + [damageLeft] * len(neighbors)
				self.AOE_Damage(targets, damages)
			elif damageUsed:
				self.dealsDamage(target, damageUsed)
		return target
		
		
class Firebrand(Minion):
	Class, race, name = "Mage", "", "Firebrand"
	mana, attack, health = 3, 3, 4
	index = "SCHOLOMANCE~Mage~Minion~3~3~4~~Firebrand"
	requireTarget, effects, description = False, "", "Spellburst: Deal 4 damage randomly split among all enemy minions"
	name_CN = "火印火妖"
	trigBoard = Trig_Firebrand


class PotionofIllusion(Spell):
	Class, school, name = "Mage,Rogue", "Arcane", "Potion of Illusion"
	requireTarget, mana, effects = False, 4, ""
	index = "SCHOLOMANCE~Mage,Rogue~Spell~4~Arcane~Potion of Illusion"
	description = "Add 1/1 copies of your minions to your hand. They cost (1)"
	name_CN = "幻觉药水"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.addCardtoHand([minion.selfCopy(self.ID, self, 1, 1, 1) for minion in self.Game.minionsonBoard(self.ID)], self.ID)
		
		
class JandiceBarov(Minion):
	Class, race, name = "Mage,Rogue", "", "Jandice Barov"
	mana, attack, health = 6, 2, 1
	index = "SCHOLOMANCE~Mage,Rogue~Minion~6~2~1~~Jandice Barov~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: Summon two random 5-Cost minions. Secretly pick one that dies when it takes damage"
	name_CN = "詹迪斯·巴罗夫"
	poolIdentifier = "5-Cost Minions to Summon"
	@classmethod
	def generatePool(cls, pools):
		return "5-Cost Minions to Summon", pools.MinionsofCost[5]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		minion1, minion2 = [minion(self.Game, self.ID) for minion in numpyChoice(self.rngPool("5-Cost Minions to Summon"), 2, replace=False)]
		self.summon([minion1, minion2], relative="<>")
		if minion1.onBoard and minion2.onBoard:
			self.chooseFixedOptions(JandiceBarov, comment, options=[minion1, minion2])
		
	def discoverDecided(self, option, case, info_RNGSync=None, info_GUISync=None):
		self.handleDiscoverGeneratedCard(option, case, info_RNGSync, info_GUISync,
										 func=lambda cardType, card: card.getsTrig(Trig_JandiceBarov(card)))
		

class MozakiMasterDuelist(Minion):
	Class, race, name = "Mage", "", "Mozaki, Master Duelist"
	mana, attack, health = 5, 3, 8
	index = "SCHOLOMANCE~Mage~Minion~5~3~8~~Mozaki, Master Duelist~Legendary"
	requireTarget, effects, description = False, "", "After you cast a spell, gain Spell Damage +1"
	name_CN = "决斗大师 莫扎奇"
	trigBoard = Trig_MozakiMasterDuelist
	def text(self): return '' if self.silenced else self.effects["Spell Damage"]


class WyrmWeaver(Minion):
	Class, race, name = "Mage", "", "Wyrm Weaver"
	mana, attack, health = 4, 3, 5
	index = "SCHOLOMANCE~Mage~Minion~4~3~5~~Wyrm Weaver"
	requireTarget, effects, description = False, "", "Spellburst: Summon two 1/2 Mana Wyrms"
	name_CN = "浮龙培养师"
	trigBoard = Trig_WyrmWeaver


class FirstDayofSchool(Spell):
	Class, school, name = "Paladin", "", "First Day of School"
	requireTarget, mana, effects = False, 1, ""
	index = "SCHOLOMANCE~Paladin~Spell~1~~First Day of School"
	description = "Add 2 random 1-Cost minions to your hand"
	name_CN = "新生入学"
	poolIdentifier = "1-Cost Minions"
	@classmethod
	def generatePool(cls, pools):
		return "1-Cost Minions", pools.MinionsofCost[1]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.addCardtoHand(numpyChoice(self.rngPool("1-Cost Minions"), 2, replace=False), self.ID)
		

"""Paladin Cards"""
class WaveofApathy(Spell):
	Class, school, name = "Paladin,Priest", "", "Wave of Apathy"
	requireTarget, mana, effects = False, 1, ""
	index = "SCHOLOMANCE~Paladin,Priest~Spell~1~~Wave of Apathy"
	description = "Set the Attack of all enemy minions to 1 until your next turn"
	name_CN = "倦怠光波"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for minion in self.Game.minionsonBoard(3-self.ID):
			minion.statReset(1, -1, enchant=Enchantment(attSet=1, until=self.ID, name=WaveofApathy))

class ArgentBraggart(Minion):
	Class, race, name = "Paladin", "", "Argent Braggart"
	mana, attack, health = 2, 1, 1
	index = "SCHOLOMANCE~Paladin~Minion~2~1~1~~Argent Braggart~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Gain Attack and Health to match the highest in the battlefield"
	name_CN = "银色自大狂"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		highestAtt, highestHealth = 0, 0
		for minion in self.Game.minionsonBoard(self.ID) + self.Game.minionsonBoard(3-self.ID):
			highestAtt, highestHealth = max(highestAtt, minion.attack), max(highestHealth, minion.health)
		attChange, healthChange = highestAtt - self.attack, highestHealth - self.health
		if attChange or healthChange: self.giveEnchant(self, attChange, healthChange, name=ArgentBraggart)

class GiftofLuminance(Spell):
	Class, school, name = "Paladin,Priest", "Holy", "Gift of Luminance"
	requireTarget, mana, effects = True, 3, ""
	index = "SCHOLOMANCE~Paladin,Priest~Spell~3~Holy~Gift of Luminance"
	description = "Give a minion Divine Shield, then summon a 1/1 copy of it"
	name_CN = "流光之赐"
	def available(self):
		return self.selectableMinionExists()

	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.giveEnchant(target, effGain="Divine Shield", name=GiftofLuminance)
			Copy = target.selfCopy(target.ID, self) if target.onBoard or target.inHand else type(target)(self.Game, target.ID)
			Copy.statReset(1, 1, source=type(self))
			self.summon(Copy, position=target.pos+1)
		return target

		
class GoodyTwoShields(Minion):
	Class, race, name = "Paladin", "", "Goody Two-Shields"
	mana, attack, health = 3, 4, 2
	index = "SCHOLOMANCE~Paladin~Minion~3~4~2~~Goody Two-Shields~Divine Shield"
	requireTarget, effects, description = False, "Divine Shield", "Spellburst: Gain Divine Shield"
	name_CN = "双盾优等生"
	trigBoard = Trig_GoodyTwoShields


class HighAbbessAlura(Minion):
	Class, race, name = "Paladin,Priest", "", "High Abbess Alura"
	mana, attack, health = 5, 3, 6
	index = "SCHOLOMANCE~Paladin,Priest~Minion~5~3~6~~High Abbess Alura~Legendary"
	requireTarget, effects, description = False, "", "Spellburst: Cast a spell from your deck (targets this if possible)"
	name_CN = "高阶修士奥露拉"
	trigBoard = Trig_HighAbbessAlura


class BlessingofAuthority(Spell):
	Class, school, name = "Paladin", "Holy", "Blessing of Authority"
	requireTarget, mana, effects = True, 5, ""
	index = "SCHOLOMANCE~Paladin~Spell~5~Holy~Blessing of Authority"
	description = "Give a minion +8/+8. It can't attack heroes this turn"
	name_CN = "威能祝福"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.giveEnchant(target, 8, 8, effGain="Can't Attack Hero", name=BlessingofAuthority)
		return target


class DevoutPupil(Minion):
	Class, race, name = "Paladin,Priest", "", "Devout Pupil"
	mana, attack, health = 6, 4, 5
	index = "SCHOLOMANCE~Paladin,Priest~Minion~6~4~5~~Devout Pupil~Divine Shield~Taunt"
	requireTarget, effects, description = False, "Divine Shield,Taunt", "Divine Shield,Taunt. Costs (1) less for each spell you've cast on friendly characters this game"
	name_CN = "虔诚的学徒"
	trigHand = Trig_DevoutPupil
	def selfManaChange(self):
		if self.inHand:
			self.mana -= len(self.Game.Counters.spellsonFriendliesThisGame[self.ID])
			self.mana = max(self.mana, 0)


class JudiciousJunior(Minion):
	Class, race, name = "Paladin", "", "Judicious Junior"
	mana, attack, health = 6, 4, 9
	index = "SCHOLOMANCE~Paladin~Minion~6~4~9~~Judicious Junior~Lifesteal"
	requireTarget, effects, description = False, "Lifesteal", "Lifesteal"
	name_CN = "踏实的大三学姐"


class TuralyontheTenured(Minion):
	Class, race, name = "Paladin", "", "Turalyon, the Tenured"
	mana, attack, health = 8, 3, 12
	index = "SCHOLOMANCE~Paladin~Minion~8~3~12~~Turalyon, the Tenured~Rush~Legendary"
	requireTarget, effects, description = False, "Rush", "Rush. Whenever this attacks a minion, set the defender's Attack and Health to 3"
	name_CN = "终身教授图拉扬"
	trigBoard = Trig_TuralyontheTenured


"""Priest Cards"""
class RaiseDead(Spell):
	Class, school, name = "Priest,Warlock", "Shadow", "Raise Dead"
	requireTarget, mana, effects = False, 0, ""
	index = "SCHOLOMANCE~Priest,Warlock~Spell~0~Shadow~Raise Dead"
	description = "Deal 3 damage to your hero. Return two friendly minions that died this game to your hand"
	name_CN = "亡者复生"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = self.calcDamage(3)
		self.dealsDamage(self.Game.heroes[self.ID], damage)
		pool = self.Game.Counters.minionsDiedThisGame[self.ID]
		if pool: self.addCardtoHand(numpyChoice(pool, min(2, len(pool)), replace=False), self.ID)
		
		
class DraconicStudies(Spell):
	Class, school, name = "Priest", "", "Draconic Studies"
	requireTarget, mana, effects = False, 1, ""
	index = "SCHOLOMANCE~Priest~Spell~1~~Draconic Studies"
	description = "Discover a Dragon. Your next one costs (1) less"
	name_CN = "龙族研习"
	poolIdentifier = "Dragons as Priest"
	@classmethod
	def generatePool(cls, pools):
		classCards = {s: [] for s in pools.ClassesandNeutral}
		for card in pools.MinionswithRace["Dragon"]:
			for Class in card.Class.split(','):
				classCards[Class].append(card)
		return ["Dragons as " + Class for Class in pools.Classes], \
			   [classCards[Class] + classCards["Neutral"] for Class in pools.Classes]
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverandGenerate(DraconicStudies, comment, lambda : self.rngPool("Dragons as " + classforDiscover(self)))
		GameManaAura_DraconicStudies(self.Game, self.ID).auraAppears()
		

class FrazzledFreshman(Minion):
	Class, race, name = "Priest", "", "Frazzled Freshman"
	mana, attack, health = 1, 1, 4
	index = "SCHOLOMANCE~Priest~Minion~1~1~4~~Frazzled Freshman"
	requireTarget, effects, description = False, "", ""
	name_CN = "疲倦的大一新生"
	
	
class MindrenderIllucia(Minion):
	Class, race, name = "Priest", "", "Mindrender Illucia"
	mana, attack, health = 3, 1, 3
	index = "SCHOLOMANCE~Priest~Minion~3~1~3~~Mindrender Illucia~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: Swap hands and decks with your opponent until your next turn"
	name_CN = "裂心者伊露希亚"

	def swapHandDeck(self):
		HD = self.Game.Hand_Deck
		hand1, hand2 = HD.extractfromHand(None, 1, getAll=True, animate=False)[0], HD.extractfromHand(None, 2, getAll=True, animate=False)[0]
		deck1, deck2 = HD.extractfromDeck(None, 1, getAll=True, animate=False)[0], HD.extractfromDeck(None, 2, getAll=True, animate=False)[0]
		HD.decks[1], HD.decks[2] = deck2, deck1
		for ID in (1, 2):
			for card in HD.decks[ID]:
				card.ID = ID
				card.entersDeck()
		for card in hand1: card.ID = 2
		for card in hand2: card.ID = 1
		HD.hands[1], HD.hands[2] = [card.entersHand() for card in hand2], [card.entersHand() for card in hand1]
		GUI = self.Game.GUI
		if GUI:
			np_1, np_2 = GUI.deckZones[1].np_Deck, GUI.deckZones[2].np_Deck
			x1, y1, z1 = np_1.getPos()
			x2, y2, z2 = np_2.getPos()
			GUI.deckZones[1].np_Deck, GUI.deckZones[2].np_Deck = np_2, np_1
			sequence = GUI.SEQUENCE(GUI.PARALLEL(GUI.LERP_Pos(np_1, duration=0.35, pos=(x1, y1, z1 + 6)),
												 GUI.LERP_Pos(np_2, duration=0.35, pos=(x2, y2, z2 + 6))),
									GUI.PARALLEL(GUI.LERP_Pos(np_1, duration=0.35, pos=(x2, y2, z2 + 6)),
												 GUI.LERP_Pos(np_2, duration=0.35, pos=(x1, y1, z1 + 6))),
									GUI.PARALLEL(GUI.LERP_Pos(np_1, duration=0.35, pos=(x2, y2, z2)),
												 GUI.LERP_Pos(np_2, duration=0.35, pos=(x1, y1, z1)))
									)
			GUI.seqHolder[-1].append(GUI.PARALLEL(sequence, GUI.handZones[1].placeCards(add2Queue=False),
												  GUI.handZones[2].placeCards(add2Queue=False))
									 )
		for card in hand1: self.Game.sendSignal("CardEntersHand", 1, None, [card], 0, "")
		for card in hand2: self.Game.sendSignal("CardEntersHand", 2, None, [card], 0, "")
		self.Game.Manas.calcMana_All()
		if GUI:
			GUI.seqHolder[-1].append(GUI.FUNC(GUI.deckZones[1].draw, len(HD.decks[1]), len(HD.hands[1])) )
			GUI.seqHolder[-1].append(GUI.FUNC(GUI.deckZones[2].draw, len(HD.decks[2]), len(HD.hands[2])) )
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		enemyID = 3 - self.ID
		enemyHand = self.Game.Hand_Deck.hands[3-self.ID]
		if enemyHand:
			hand_Orig = self.Game.Hand_Deck.extractfromHand(None, self.ID, getAll=True)[0]
			self.addCardtoHand([card.selfCopy(enemyID, self) for card in enemyHand], self.ID)
			if hand_Orig: MindrenderIllucia_Effect(self.Game, self.ID, hand_Orig).connect()
		

class PowerWordFeast(Spell):
	Class, school, name = "Priest", "", "Power Word: Feast"
	requireTarget, mana, effects = True, 2, ""
	index = "SCHOLOMANCE~Priest~Spell~2~~Power Word: Feast"
	description = "Give a minion +2/+2. Restore it to full health at the end of this turn"
	name_CN = "真言术：宴"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.giveEnchant(target, 2, 2, trig=Trig_PowerWordFeast, connect=target.onBoard, name=PowerWordFeast)
		return target
		

class BrittleboneDestroyer(Minion):
	Class, race, name = "Priest,Warlock", "", "Brittlebone Destroyer"
	mana, attack, health = 4, 3, 3
	index = "SCHOLOMANCE~Priest,Warlock~Minion~4~3~3~~Brittlebone Destroyer~Battlecry"
	requireTarget, effects, description = True, "", "Battlecry: If your hero's Health changed this turn, destroy a minion"
	name_CN = "脆骨破坏者"
	def needTarget(self, choice=0):
		return self.Game.Counters.heroChangedHealthThisTurn[self.ID]
		
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.heroChangedHealthThisTurn[self.ID]
		
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target != self and target.onBoard
		
	#If the minion is shuffled into deck already, then nothing happens.
	#If the minion is returned to hand, move it from enemy hand into our hand.
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and self.Game.Counters.heroChangedHealthThisTurn[self.ID]:
			self.Game.killMinion(self, target)
		return target
		

class CabalAcolyte(Minion):
	Class, race, name = "Priest", "", "Cabal Acolyte"
	mana, attack, health = 4, 2, 4
	index = "SCHOLOMANCE~Priest~Minion~4~2~4~~Cabal Acolyte~Taunt"
	requireTarget, effects, description = False, "Taunt", "Taunt. Spellburst: Gain control of a random enemy minion with 2 or less Attack"
	name_CN = "秘教侍僧"
	trigBoard = Trig_CabalAcolyte


class DisciplinarianGandling(Minion):
	Class, race, name = "Priest,Warlock", "", "Disciplinarian Gandling"
	mana, attack, health = 4, 3, 6
	index = "SCHOLOMANCE~Priest,Warlock~Minion~4~3~6~~Disciplinarian Gandling~Legendary"
	requireTarget, effects, description = False, "", "After you play a minion, destroy it and summon a 4/4 Failed Student"
	name_CN = "教导主任加丁"
	trigBoard = Trig_DisciplinarianGandling


class FailedStudent(Minion):
	Class, race, name = "Priest,Warlock", "", "Failed Student"
	mana, attack, health = 4, 4, 4
	index = "SCHOLOMANCE~Priest,Warlock~Minion~4~4~4~~Failed Student~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "挂掉的学生"
	
	
class Initiation(Spell):
	Class, school, name = "Priest", "Shadow", "Initiation"
	requireTarget, mana, effects = True, 6, ""
	index = "SCHOLOMANCE~Priest~Spell~6~Shadow~Initiation"
	description = "Deal 4 damage to a minion. If that kills it, summons a new copy"
	name_CN = "通窍"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard

	def text(self): return self.calcDamage(4)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			dmgTaker, damageActual = self.dealsDamage(target, self.calcDamage(4))
			if dmgTaker.health < 1 or dmgTaker.dead: self.summon(type(dmgTaker)(self.Game, self.ID))
		return target
		

class FleshGiant(Minion):
	Class, race, name = "Priest,Warlock", "", "Flesh Giant"
	mana, attack, health = 10, 8, 8
	index = "SCHOLOMANCE~Priest,Warlock~Minion~10~8~8~~Flesh Giant"
	requireTarget, effects, description = False, "", "Costs (1) less for each time your Hero's Health changed during your turn"
	name_CN = "血肉巨人"
	trigHand = Trig_FleshGiant
	def selfManaChange(self):
		if self.inHand:
			self.mana -= self.Game.Counters.timesHeroChangedHealth_inOwnTurn[self.ID]
			self.mana = max(self.mana, 0)


"""Rogue Cards"""
class SecretPassage(Spell):
	Class, school, name = "Rogue", "", "Secret Passage"
	requireTarget, mana, effects = False, 1, ""
	index = "SCHOLOMANCE~Rogue~Spell~1~~Secret Passage"
	description = "Replace your hand with 4 cards from your deck. Swap back next turn"
	name_CN = "秘密通道"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		game, ID = self.Game, self.ID
		deck = game.Hand_Deck.decks[ID]
		deckSize = len(deck)
		indices = list(numpyChoice(range(deckSize), min(deckSize, 4), replace=False))
		indices.sort() #Smallest index becomes first element
		if indices:
			cardsfromHand = game.Hand_Deck.extractfromHand(None, ID, getAll=True, enemyCanSee=False, animate=False)[0]
			cardsfromDeck = [game.Hand_Deck.extractfromDeck(i, ID, enemyCanSee=False, animate=False)[0] for i in reversed(indices)]
			if game.GUI:
				panda_SecretPassage_LeaveHand(game, game.GUI, cardsfromHand)
				game.GUI.deckZones[ID].draw(len(game.Hand_Deck.decks[ID]), len(game.Hand_Deck.hands[ID]))
			SecretPassage_Effect(game, ID, cardsfromHand, cardsfromDeck).connect()
			game.Hand_Deck.addCardtoHand(cardsfromDeck, ID)


class Plagiarize(Secret):
	Class, school, name = "Rogue", "", "Plagiarize"
	requireTarget, mana, effects = False, 2, ""
	index = "SCHOLOMANCE~Rogue~Spell~2~~Plagiarize~~Secret"
	description = "Secret: At the end of your opponent's turn, add copies of the cards they played this turn"
	name_CN = "抄袭"
	trigBoard = Trig_Plagiarize


class Coerce(Spell):
	Class, school, name = "Rogue,Warrior", "", "Coerce"
	requireTarget, mana, effects = True, 3, ""
	index = "SCHOLOMANCE~Rogue,Warrior~Spell~3~~Coerce~Combo"
	description = "Destroy a damaged minion. Combo: Destroy any minion"
	name_CN = "胁迫"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard and \
				(target.health < target.health_max or self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0)
				
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.Game.killMinion(self, target)
		return target
		
		
class SelfSharpeningSword(Weapon):
	Class, name, description = "Rogue", "Self-Sharpening Sword", "After your hero attacks, gain +1 Attack"
	mana, attack, durability, effects = 3, 1, 4, ""
	index = "SCHOLOMANCE~Rogue~Weapon~3~1~4~Self-Sharpening Sword"
	name_CN = "自砺之锋"
	trigBoard = Trig_SelfSharpeningSword


class VulperaToxinblade(Minion):
	Class, race, name = "Rogue", "", "Vulpera Toxinblade"
	mana, attack, health = 3, 3, 3
	index = "SCHOLOMANCE~Rogue~Minion~3~3~3~~Vulpera Toxinblade"
	requireTarget, effects, description = False, "", "Your weapon has +2 Attack"
	name_CN = "狐人淬毒师"
	aura = Aura_VulperaToxinblade


class InfiltratorLilian(Minion):
	Class, race, name = "Rogue", "", "Infiltrator Lilian"
	mana, attack, health = 4, 4, 2
	index = "SCHOLOMANCE~Rogue~Minion~4~4~2~~Infiltrator Lilian~Stealth~Deathrattle~Legendary"
	requireTarget, effects, description = False, "Stealth", "Stealth. Deathrattle: Summon a 4/2 Forsaken Lilian that attacks a random enemy"
	name_CN = "渗透者莉莉安"
	deathrattle = Death_InfiltratorLilian


class ForsakenLilian(Minion):
	Class, race, name = "Rogue", "", "Forsaken Lilian"
	mana, attack, health = 4, 4, 2
	index = "SCHOLOMANCE~Rogue~Minion~4~4~2~~Forsaken Lilian~Legendary~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "被遗忘者莉莉安"


class ShiftySophomore(Minion):
	Class, race, name = "Rogue", "", "Shifty Sophomore"
	mana, attack, health = 4, 4, 4
	index = "SCHOLOMANCE~Rogue~Minion~4~4~4~~Shifty Sophomore~Stealth"
	requireTarget, effects, description = False, "Stealth", "Stealth. Spellburst: Add a Combo card to your hand"
	name_CN = "调皮的大二学妹"
	trigBoard = Trig_ShiftySophomore
	poolIdentifier = "Combo Cards"
	@classmethod
	def generatePool(cls, pools):
		return "Combo Cards", [card for card in pools.ClassCards["Rogue"] if "~Combo~" in card.index]


class Steeldancer(Minion):
	Class, race, name = "Rogue,Warrior", "", "Steeldancer"
	mana, attack, health = 4, 4, 4
	index = "SCHOLOMANCE~Rogue,Warrior~Minion~4~4~4~~Steeldancer~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Summon a random minion with Cost equal to your weapons's Attack"
	name_CN = "钢铁舞者"
	poolIdentifier = "0-Cost Minions to summon"
	@classmethod
	def generatePool(cls, pools):
		return ["%d-Cost Minions to Summon" % cost for cost in pools.MinionsofCost.keys()], \
			   list(pools.MinionsofCost.values())
	
	def effCanTrig(self):
		self.effectViable = self.Game.availableWeapon(self.ID) is not None
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if weapon := self.Game.availableWeapon(self.ID):
			self.summon(self.newEvolved(max(weapon.attack, 0)-1, by=1, ID=self.ID))
		
		
class CuttingClass(Spell):
	Class, school, name = "Rogue,Warrior", "", "Cutting Class"
	requireTarget, mana, effects = False, 5, ""
	index = "SCHOLOMANCE~Rogue,Warrior~Spell~5~~Cutting Class"
	description = "Draw 2 cards. Costs (1) less per Attack of your weapon"
	name_CN = "劈砍课程"
	trigHand = Trig_CuttingClass
	def selfManaChange(self):
		weapon = self.Game.availableWeapon(self.ID)
		if self.inHand and weapon:
			self.mana -= max(0, weapon.attack)
			self.mana = max(0, self.mana)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.Hand_Deck.drawCard(self.ID)
		self.Game.Hand_Deck.drawCard(self.ID)


class DoctorKrastinov(Minion):
	Class, race, name = "Rogue,Warrior", "", "Doctor Krastinov"
	mana, attack, health = 5, 4, 4
	index = "SCHOLOMANCE~Rogue,Warrior~Minion~5~4~4~~Doctor Krastinov~Rush~Legendary"
	requireTarget, effects, description = False, "Rush", "Rush. Whenever this attacks, give your weapon +1/+1"
	name_CN = "卡斯迪诺夫教授"
	trigBoard = Trig_DoctorKrastinov		


"""Shaman Cards"""
class PrimordialStudies(Spell):
	Class, school, name = "Shaman,Mage", "Arcane", "Primordial Studies"
	requireTarget, mana, effects = False, 1, ""
	index = "SCHOLOMANCE~Shaman,Mage~Spell~1~Arcane~Primordial Studies"
	description = "Discover a Spell Damage minion. Your next one costs (1) less"
	name_CN = "始生研习"
	poolIdentifier = "Spell Damage Minions as Mage"
	@classmethod
	def generatePool(cls, pools):
		classCards = {s: [card for card in pools.ClassCards[s] if "~Spell Damage" in card.index] for s in pools.Classes}
		classCards["Neutral"] = [card for card in pools.NeutralCards if "~Spell Damage" in card.index]
		return ["Spell Damage Minions as "+Class for Class in pools.Classes], \
				[classCards[Class]+classCards["Neutral"] for Class in pools.Classes]
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverandGenerate(PrimordialStudies, comment, lambda : self.rngPool("Spell Damage Minions as " + classforDiscover(self)))
		GameManaAura_PrimordialStudies(self.Game, self.ID).auraAppears()
		

class DiligentNotetaker(Minion):
	Class, race, name = "Shaman", "", "Diligent Notetaker"
	mana, attack, health = 2, 2, 3
	index = "SCHOLOMANCE~Shaman~Minion~2~2~3~~Diligent Notetaker"
	requireTarget, effects, description = False, "", "Spellburst: Return the spell to your hand"
	name_CN = "笔记能手"
	trigBoard = Trig_DiligentNotetaker


class RuneDagger(Weapon):
	Class, name, description = "Shaman", "Rune Dagger", "After your hero attacks, gain Spell Damage +1 this turn"
	mana, attack, durability, effects = 2, 1, 3, ""
	index = "SCHOLOMANCE~Shaman~Weapon~2~1~3~Rune Dagger"
	name_CN = "符文匕首"
	trigBoard = Trig_RuneDagger


class TrickTotem(Minion):
	Class, race, name = "Shaman,Mage", "Totem", "Trick Totem"
	mana, attack, health = 2, 0, 3
	index = "SCHOLOMANCE~Shaman,Mage~Minion~2~0~3~Totem~Trick Totem"
	requireTarget, effects, description = False, "", "At the end of your turn, cast a random spell that costs (3) or less"
	name_CN = "戏法图腾"
	trigBoard = Trig_TrickTotem
	poolIdentifier = "Spells of <=3 Cost"
	@classmethod
	def generatePool(cls, pools):
		spells = []
		for Class in pools.Classes:
			spells += [card for card in pools.ClassCards[Class] if card.category == "Spell" and card.mana < 4]
		return "Spells of <=3 Cost", spells


class InstructorFireheart(Minion):
	Class, race, name = "Shaman", "", "Instructor Fireheart"
	mana, attack, health = 3, 3, 3
	index = "SCHOLOMANCE~Shaman~Minion~3~3~3~~Instructor Fireheart~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: Discover a spell that costs (1) or more. If you play it this turn, repeat this effect"
	name_CN = "导师火心"
	poolIdentifier = "Shaman Spells with 1 or more Cost"
	@classmethod
	def generatePool(cls, pools):
		return [Class+" Spells with 1 or more Cost" for Class in pools.Classes], \
				[[card for card in pools.ClassCards[Class] if card.category == "Spell" and card.mana > 0] for Class in pools.Classes]

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.ID == self.Game.turn:
			trig = InstructorFireheart_Effect(self.Game, self.ID)
			trig.connect()
			trig.effect(signal='', ID=0, subject=None, target=None, number=0, comment=comment, choice=0)



class MoltenBlast(Spell):
	Class, school, name = "Shaman", "Fire", "Molten Blast"
	requireTarget, mana, effects = True, 3, ""
	index = "SCHOLOMANCE~Shaman~Spell~3~Fire~Molten Blast"
	description = "Deal 2 damage. Summon that many 1/1 Elementals"
	name_CN = "岩浆爆裂"
	def text(self): return self.calcDamage(2)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.dealsDamage(target, damage := self.calcDamage(2))
			self.summon([MoltenElemental(self.Game, self.ID) for i in range(damage)])
		return target

class MoltenElemental(Minion):
	Class, race, name = "Shaman", "Elemental", "Molten Elemental"
	mana, attack, health = 1, 1, 1
	index = "SCHOLOMANCE~Shaman~Minion~1~1~1~Elemental~Molten Elemental~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "熔岩元素"
	
	
class RasFrostwhisper(Minion):
	Class, race, name = "Shaman,Mage", "", "Ras Frostwhisper"
	mana, attack, health = 5, 3, 6
	index = "SCHOLOMANCE~Shaman,Mage~Minion~5~3~6~~Ras Frostwhisper~Legendary"
	requireTarget, effects, description = False, "", "At the end of turn, deal 1 damage to all enemies (improved by Spell Damage)"
	name_CN = "莱斯霜语"
	trigBoard = Trig_RasFrostwhisper
	def text(self): return 1 + self.countSpellDamage()


class TotemGoliath(Minion):
	Class, race, name = "Shaman", "Totem", "Totem Goliath"
	mana, attack, health = 5, 5, 5
	index = "SCHOLOMANCE~Shaman~Minion~5~5~5~Totem~Totem Goliath~Deathrattle"
	requireTarget, effects, description = False, "", "Deathrattle: Summon all four basic totems. Overload: (1)"
	name_CN = "图腾巨像"
	overload, deathrattle = 1, Death_TotemGoliath


class TidalWave(Spell):
	Class, school, name = "Shaman", "Nature", "Tidal Wave"
	requireTarget, mana, effects = False, 8, "Lifesteal"
	index = "SCHOLOMANCE~Shaman~Spell~8~Nature~Tidal Wave"
	description = "Lifesteal. Deal 3 damage to all minions"
	name_CN = "潮汐奔涌"
	def text(self): return self.calcDamage(3)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = self.calcDamage(3)
		minions = self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)
		self.AOE_Damage(minions, [damage]*len(minions))
		

"""Warlock Cards"""
class DemonicStudies(Spell):
	Class, school, name = "Warlock", "Shadow", "Demonic Studies"
	requireTarget, mana, effects = False, 1, ""
	index = "SCHOLOMANCE~Warlock~Spell~1~Shadow~Demonic Studies"
	description = "Discover a Demon. Your next one costs (1) less"
	name_CN = "恶魔研习"
	poolIdentifier = "Demons as Warlock"
	@classmethod
	def generatePool(cls, pools):
		classCards = {s: [] for s in pools.ClassesandNeutral}
		for card in pools.MinionswithRace["Demon"]:
			for Class in card.Class.split(','):
				classCards[Class].append(card)
		return ["Demons as " + Class for Class in pools.Classes], \
			   [classCards[Class] + classCards["Neutral"] for Class in pools.Classes]
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverandGenerate(DemonicStudies, comment, lambda: self.rngPool("Demons as " + classforDiscover(self)))
		GameManaAura_DemonicStudies(self.Game, self.ID).auraAppears()
		

class Felosophy(Spell):
	Class, school, name = "Warlock,Demon Hunter", "Fel", "Felosophy"
	requireTarget, mana, effects = False, 1, ""
	index = "SCHOLOMANCE~Warlock,Demon Hunter~Spell~1~Fel~Felosophy~Outcast"
	description = "Copy the lowest Cost Demon in your hand. Outcast: Give both +1/+1"
	name_CN = "邪能学说"
	def effCanTrig(self):
		self.effectViable = any("Demon" in card.race for card in self.Game.Hand_Deck.hands[self.ID]) \
							and self.Game.Hand_Deck.outcastcanTrig(self)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if demons := pickLowestCost((card for card in self.Game.Hand_Deck.hands[self.ID] if "Demon" in card.race)):
			Copy = (demon := numpyChoice(demons)).selfCopy(self.ID, self)
			self.addCardtoHand(Copy, self.ID)
			if posinHand == 0 or posinHand == -1:
				self.AOE_GiveEnchant((demon, Copy), 1, 1, name=Felosophy, add2EventinGUI=False)
		
		
class SpiritJailer(Minion):
	Class, race, name = "Warlock,Demon Hunter", "Demon", "Spirit Jailer"
	mana, attack, health = 1, 1, 3
	index = "SCHOLOMANCE~Warlock,Demon Hunter~Minion~1~1~3~Demon~Spirit Jailer~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Shuffle 2 Soul Fragments into your deck"
	name_CN = "精魂狱卒"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.shuffleintoDeck([SoulFragment(self.Game, self.ID) for _ in (0, 1)])
		
		
class BonewebEgg(Minion):
	Class, race, name = "Warlock", "", "Boneweb Egg"
	mana, attack, health = 2, 0, 2
	index = "SCHOLOMANCE~Warlock~Minion~2~0~2~~Boneweb Egg~Deathrattle"
	requireTarget, effects, description = False, "", "Deathrattle: Summon two 2/1 Spiders. If you discard this, trigger it Deathrattle"
	name_CN = "骨网之卵"
	deathrattle = Death_BonewebEgg
	def whenDiscarded(self):
		for trig in self.deathrattles:
			trig.trig("TrigDeathrattle", self.ID, None, self, self.attack, "")

	def trigDeathrattles(self):
		for trig in self.deathrattles:
			trig.trig("TrigDeathrattle", self.ID, None, self, self.attack, "")

class BonewebSpider(Minion):
	Class, race, name = "Warlock", "Beast", "Boneweb Spider"
	mana, attack, health = 1, 2, 1
	index = "SCHOLOMANCE~Warlock~Minion~1~2~1~Beast~Boneweb Spider~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "骨网蜘蛛"
	
	
class SoulShear(Spell):
	Class, school, name = "Warlock,Demon Hunter", "Shadow", "Soul Shear"
	requireTarget, mana, effects = True, 2, ""
	index = "SCHOLOMANCE~Warlock,Demon Hunter~Spell~2~Shadow~Soul Shear"
	description = "Deal 3 damage to a minion. Shuffle 2 Soul Fragments into your deck"
	name_CN = "灵魂剥离"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = self.calcDamage(3)
			self.dealsDamage(target, damage)
			self.shuffleintoDeck([SoulFragment(self.Game, self.ID) for _ in (0, 1)])
		return target
		
		
class SchoolSpirits(Spell):
	Class, school, name = "Warlock", "Shadow", "School Spirits"
	requireTarget, mana, effects = False, 3, ""
	index = "SCHOLOMANCE~Warlock~Spell~3~Shadow~School Spirits"
	description = "Deal 2 damage to all minions. Shuffle 2 Soul Fragments into your deck"
	name_CN = "校园精魂"
	def text(self): return self.calcDamage(2)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = self.calcDamage(2)
		minions = self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)
		self.AOE_Damage(minions, [damage]*len(minions))
		self.shuffleintoDeck([SoulFragment(self.Game, self.ID) for _ in (0, 1)])
		
		
class ShadowlightScholar(Minion):
	Class, race, name = "Warlock", "", "Shadowlight Scholar"
	mana, attack, health = 3, 3, 4
	index = "SCHOLOMANCE~Warlock~Minion~3~3~4~~Shadowlight Scholar~Battlecry"
	requireTarget, effects, description = True, "", "Battlecry: Destroy a Soul Fragment in your deck to deal 3 damage"
	name_CN = "影光学者"
	def needTarget(self, choice=0):
		return any(isinstance(card, SoulFragment) for card in self.Game.Hand_Deck.decks[self.ID])
		
	def effCanTrig(self):
		self.effectViable = any(isinstance(card, SoulFragment) for card in self.Game.Hand_Deck.decks[self.ID])
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and destroyaSoulFragment(self.Game, self.ID): self.dealsDamage(target, 3)
		return target
		
		
class VoidDrinker(Minion):
	Class, race, name = "Warlock", "Demon", "Void Drinker"
	mana, attack, health = 5, 4, 5
	index = "SCHOLOMANCE~Warlock~Minion~5~4~5~Demon~Void Drinker~Taunt~Battlecry"
	requireTarget, effects, description = False, "Taunt", "Taunt. Battlecry: Destroy a Soul Fragment in your deck to gain +3/+3"
	name_CN = "虚空吸食者"
	
	def effCanTrig(self):
		self.effectViable = any(isinstance(card, SoulFragment) for card in self.Game.Hand_Deck.decks[self.ID])

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if destroyaSoulFragment(self.Game, self.ID): self.giveEnchant(self, 3, 3, name=VoidDrinker)
		
		
class SoulciologistMalicia(Minion):
	Class, race, name = "Warlock,Demon Hunter", "", "Soulciologist Malicia"
	mana, attack, health = 7, 5, 5
	index = "SCHOLOMANCE~Warlock,Demon Hunter~Minion~7~5~5~~Soulciologist Malicia~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: For each Soul Fragment in your deck, summon a 3/3 Soul with Rush"
	name_CN = "灵魂学家玛丽希亚"
	
	def effCanTrig(self):
		self.effectViable = False
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if isinstance(card, SoulFragment): self.effectViable = True
			
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if num := sum(isinstance(card, SoulFragment) for card in self.Game.Hand_Deck.decks[self.ID]):
			self.summon([ReleasedSoul(self.Game, self.ID) for i in range(num)])
	

class ReleasedSoul(Minion):
	Class, race, name = "Warlock,Demon Hunter", "", "Released Soul"
	mana, attack, health = 3, 3, 3
	index = "SCHOLOMANCE~Warlock,Demon Hunter~Minion~3~3~3~~Released Soul~Rush~Uncollectible"
	requireTarget, effects, description = False, "Rush", "Rush"
	name_CN = "被释放的灵魂"
	
	
class ArchwitchWillow(Minion):
	Class, race, name = "Warlock", "", "Archwitch Willow"
	mana, attack, health = 8, 5, 5
	index = "SCHOLOMANCE~Warlock~Minion~8~5~5~~Archwitch Willow~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: Summon a random Demon from your hand and deck"
	name_CN = "高阶女巫维洛"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		minion = self.try_SummonfromHand(func=lambda card: "Demon" in card.race)
		self.try_SummonfromDeck(position=(minion if minion else self).position + 1, func=lambda card: "Demon" in card.race)
		

"""Warrior Cards"""
class AthleticStudies(Spell):
	Class, school, name = "Warrior", "", "Athletic Studies"
	requireTarget, mana, effects = False, 1, ""
	index = "SCHOLOMANCE~Warrior~Spell~1~~Athletic Studies"
	description = "Discover a Rush minion. Your next one costs (1) less"
	name_CN = "体能研习"
	poolIdentifier = "Rush Minions as Warrior"
	@classmethod
	def generatePool(cls, pools):
		classCards = {s: [card for card in pools.ClassCards[s] if "~Rush" in card.index] for s in pools.Classes}
		classCards["Neutral"] = [card for card in pools.NeutralCards if "~Rush" in card.index]
		return ["Rush Minions as "+Class for Class in pools.Classes], \
				[classCards[Class]+classCards["Neutral"] for Class in pools.Classes]
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverandGenerate(AthleticStudies, comment, lambda : self.rngPool("Rush Minions as " + classforDiscover(self)))
		GameManaAura_AthleticStudies(self.Game, self.ID).auraAppears()
		

class ShieldofHonor(Spell):
	Class, school, name = "Warrior,Paladin", "Holy", "Shield of Honor"
	requireTarget, mana, effects = True, 1, ""
	index = "SCHOLOMANCE~Warrior,Paladin~Spell~1~Holy~Shield of Honor"
	description = "Give a damaged minion +3 Attack and Divine Shield"
	name_CN = "荣誉护盾"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard and target.health < target.health_max
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.giveEnchant(target, 3, 0, effGain="Divine Shield", name=ShieldofHonor)
		return target
		
		
class InFormation(Spell):
	Class, school, name = "Warrior", "", "In Formation!"
	requireTarget, mana, effects = False, 2, ""
	index = "SCHOLOMANCE~Warrior~Spell~2~~In Formation!"
	description = "Add 2 random Taunt minions to your hand"
	name_CN = "保持阵型"
	poolIdentifier = "Taunt Minions"
	@classmethod
	def generatePool(cls, pools):
		minions = [card for card in pools.NeutralCards if "~Taunt" in card.index]
		for Class in pools.Classes:
			minions += [card for card in pools.ClassCards[Class] if "~Taunt" in card.index]
		return "Taunt Minions", minions
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.addCardtoHand(numpyChoice(self.rngPool("Taunt Minions"), 2, replace=True), self.ID)
		

class CeremonialMaul(Weapon):
	Class, name, description = "Warrior,Paladin", "Ceremonial Maul", "Spellburst: Summon a student with Taunt and stats equal to the spell's Cost"
	mana, attack, durability, effects = 3, 2, 2, ""
	index = "SCHOLOMANCE~Warrior,Paladin~Weapon~3~2~2~Ceremonial Maul"
	name_CN = "仪式重槌"
	trigBoard = Trig_CeremonialMaul


class HonorStudent(Minion):
	Class, race, name = "Warrior,Paladin", "", "Honor Student"
	mana, attack, health = 1, 1, 1
	index = "SCHOLOMANCE~Warrior,Paladin~Minion~1~1~1~~Honor Student~Taunt~Uncollectible"
	requireTarget, effects, description = False, "Taunt", "Taunt"
	name_CN = "仪仗学员"


class LordBarov(Minion):
	Class, race, name = "Warrior,Paladin", "", "Lord Barov"
	mana, attack, health = 3, 3, 2
	index = "SCHOLOMANCE~Warrior,Paladin~Minion~3~3~2~~Lord Barov~Battlecry~Deathrattle~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: Set the Health of all other minions to 1. Deathrattle: Deal 1 damage to all other minions"
	name_CN = "巴罗夫领主"
	deathrattle = Death_LordBarov
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for minion in self.Game.minionsonBoard(self.ID, self) + self.Game.minionsonBoard(3-self.ID):
			minion.statReset(newHealth=1, source=type(self))
		

class Playmaker(Minion):
	Class, race, name = "Warrior", "", "Playmaker"
	mana, attack, health = 3, 4, 3
	index = "SCHOLOMANCE~Warrior~Minion~3~4~3~~Playmaker"
	requireTarget, effects, description = False, "", "After you play a Rush minion, summon a copy with 1 Health remaining"
	name_CN = "团队核心"
	trigBoard = Trig_Playmaker


class ReapersScythe(Weapon):
	Class, name, description = "Warrior", "Reaper's Scythe", "Spellburst: Also damages adjacent minions this turn"
	mana, attack, durability, effects = 4, 4, 2, ""
	index = "SCHOLOMANCE~Warrior~Weapon~4~4~2~Reaper's Scythe"
	name_CN = "收割之镰"
	trigBoard = Trig_ReapersScythe


class Commencement(Spell):
	Class, school, name = "Warrior,Paladin", "", "Commencement"
	requireTarget, mana, effects = False, 7, ""
	index = "SCHOLOMANCE~Warrior,Paladin~Spell~7~~Commencement"
	description = "Summon a minion from your deck. Give it Taunt and Divine Shield"
	name_CN = "毕业仪式"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if minion := self.try_SummonfromDeck():
			self.giveEnchant(minion, multipleEffGains=(("Taunt", 1, None), ("Divine Shield", 1, None)), name=Commencement)
		

class Troublemaker(Minion):
	Class, race, name = "Warrior", "", "Troublemaker"
	mana, attack, health = 8, 6, 8
	index = "SCHOLOMANCE~Warrior~Minion~8~6~8~~Troublemaker"
	requireTarget, effects, description = False, "", "At the end of your turn, summon two 3/3 Ruffians that attack random enemies"
	name_CN = "问题学生"
	trigBoard = Trig_Troublemaker


class Ruffian(Minion):
	Class, race, name = "Warrior", "", "Ruffian"
	mana, attack, health = 3, 3, 3
	index = "SCHOLOMANCE~Warrior~Minion~3~3~3~~Ruffian~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "无赖"
	
#https://www.bilibili.com/video/BV1Uy4y1C73o 机制测试
#血骨傀儡的亡语的实质是在随从死亡并进行了身材重置之后检测其身材，然后召唤一个相同的身材的随从。之后再把这个随从的身材白字改为检测 到的身材的-1/-1
#召唤的3/3血骨傀儡在场上有卡德加的时候会召唤2/2和3/3（卡德加复制得到的那个随从没有来得及再执行-1/-1）
#buff得到的身材在进入墓地时会清除，但是场上的随从因为装死等效果直接触发时是可以直接检测到buff的身材的，比如20/19的血骨傀儡可以因为装死召唤一个19/18
#其他随从获得了血骨傀儡的身材之后可以召唤自身而不是血骨傀儡，如送葬者
#与水晶核心的互动：4/4的血骨傀儡在死亡后先召唤4/4的血骨傀儡，与水晶核心作用，然后被这个亡语-1/-1,形成一个3/3。这个3/3死亡后被检测，预定最终 被变成2/2先召唤3/3
	#这个3/3被水晶核心变成4/4然后再被调成2/2
#血骨傀儡的亡语只会处理第一个召唤出来的随从的身材，如果有翻倍召唤，则其他复制是原身材
#在场上触发亡语时，检测的是满状态的生命值，即使受伤也是从最大生命值计算


#https://www.bilibili.com/video/BV1Uy4y1C73o 机制测试
#血骨傀儡的亡语的实质是在随从死亡并进行了身材重置之后检测其身材，计算得到-1/-1后的身材，然后召唤一个与原来相同身材的随从。之后再把这个随从的身材白字改为计算得到的那个身材
#召唤的3/3血骨傀儡在场上有卡德加的时候会召唤2/2和3/3（卡德加复制得到的那个随从不执行-1/-1）
#buff得到的身材在进入墓地时会清除，但是场上的随从因为装死等效果直接触发时是可以直接检测到buff的身材的，比如20/19的血骨傀儡可以因为装死召唤一个19/18
#其他随从获得了血骨傀儡的身材之后可以召唤自身而不是血骨傀儡，如送葬者
#与水晶核心的互动：4/4的血骨傀儡在死亡后先召唤4/4的血骨傀儡，与水晶核心作用，然后被这个亡语-1/-1,形成一个3/3。这个3/3死亡后被检测，预定最终 被变成2/2先召唤3/3
#血骨傀儡的亡语只会处理第一个召唤出来的随从的身材，如果有翻倍召唤，则其他复制是原身材
#在场上触发亡语时，检测的是满状态的生命值，即使受伤也是从最大生命值计算
class Rattlegore(Minion):
	Class, race, name = "Warrior", "", "Rattlegore"
	mana, attack, health = 9, 9, 9
	index = "SCHOLOMANCE~Warrior~Minion~9~9~9~~Rattlegore~Deathrattle~Legendary"
	requireTarget, effects, description = False, "", "Deathrattle: Resummon this with -1/-1"
	name_CN = "血骨傀儡"
	deathrattle = Death_Rattlegore


"""Game Trigeffects and Game auras"""
class GameManaAura_TourGuide(GameManaAura_OneTime):
	card, to, temporary, targets = TourGuide, 0, False, "Power"
	def applicable(self, target): return target.ID == self.ID and target.category == "Power"

class GameManaAura_CultNeophyte(GameManaAura_OneTime):
	card, signals, by = CultNeophyte, ("CardEntersHand",), +1
	def applicable(self, target): return target.ID == self.ID and target.category == "Spell"

class GameManaAura_NatureStudies(GameManaAura_OneTime):
	card, by, temporary = NatureStudies, -1, False
	def applicable(self, target): return target.ID == self.ID and target.category == "Spell"

class GameManaAura_CarrionStudies(GameManaAura_OneTime):
	card, by, temporary = CarrionStudies, -1, False
	def applicable(self, target): return target.ID == self.ID and target.category == "Minion" and target.deathrattles

class GameManaAura_DraconicStudies(GameManaAura_OneTime):
	card, by, temporary = DraconicStudies, -1, False
	def applicable(self, target): return target.ID == self.ID and "Dragon" in target.race

class MindrenderIllucia_Effect(TrigEffect):
	card, trigType = MindrenderIllucia, "TurnEnd&OnlyKeepOne"
	def __init__(self, Game, ID, cardsReplaced):
		super().__init__(Game, ID)
		self.savedObjs = cardsReplaced

	def trigEffect(self):
		self.Game.Hand_Deck.extractfromHand(None, self.ID, getAll=True)
		if self.savedObjs: self.Game.Hand_Deck.addCardtoHand(self.savedObjs, self.ID)

	def assistCreateCopy(self, Copy):
		Copy.savedObjs = [card.createCopy(Copy.Game) for card in self.savedObjs]


class SecretPassage_Effect(TrigEffect):
	card, trigType = SecretPassage, "TurnEnd"
	def __init__(self, Game, ID, cardsfromHand, cardsfromDeck):
		super().__init__(Game, ID)
		self.counter = len(cardsfromHand)
		self.cardsfromHand, self.cardsfromDeck = cardsfromHand, cardsfromDeck

	def trigEffect(self):
		HD = self.Game.Hand_Deck
		cards2Return2Deck = [card for card in HD.hands[self.ID] if card in self.cardsfromDeck]
		for card in cards2Return2Deck:
			HD.extractfromHand(card, self.ID, getAll=False, enemyCanSee=False, animate=False)
			card.reset(self.ID)
		GUI = self.Game.GUI
		if GUI:
			panda_SecretPassage_LeaveHand(self.Game, GUI, cards2Return2Deck)
			Y = HandZone1_Y if self.ID == self.Game.GUI.ID else HandZone2_Y
			poses, hprs = posHandsTable[Y][len(cards2Return2Deck)], hprHandsTable[Y][len(cards2Return2Deck)]
			panda_SecretPassage_BackfromPassage(self.Game, GUI, self.cardsfromHand, poses, hprs)

		HD.decks[self.ID] += cards2Return2Deck
		for card in cards2Return2Deck:
			card.entersDeck()
		numpyShuffle(HD.decks[self.ID])
		if GUI: GUI.deckZones[self.ID].draw(len(HD.decks[self.ID]), len(HD.hands[self.ID]))
		HD.addCardtoHand(self.cardsfromHand, self.ID)

		self.Game.turnEndTrigger.remove(self)
		if GUI: GUI.heroZones[self.ID].removeaTrig(self.card)

	def assistCreateCopy(self, Copy):
		Copy.cardsfromHand = [card.createCopy(Copy.Game) for card in self.cardsfromHand]
		Copy.cardsfromDeck = [card.createCopy(Copy.Game) for card in self.cardsfromDeck]


class GameManaAura_PrimordialStudies(GameManaAura_OneTime):
	card, by, temporary = PrimordialStudies, -1, False
	def applicable(self, target): return target.ID == self.ID and target.category == "Minion" and target.effects["Spell Damage"] > 0

class RuneDagger_Effect(TrigEffect):
	card, counter, trigType = RuneDagger, 1, "TurnEnd&OnlyKeepOne"
	def trigEffect(self): self.Game.heroes[self.ID].losesEffect("Spell Damage")

class InstructorFireheart_Effect(TrigEffect):
	card, signals, trigType = InstructorFireheart, ("SpellBeenPlayed",), "Conn&TurnEnd"
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.ID and subject == self.savedObj

	def decideSpellPool(self):
		hero = self.Game.heroes[self.ID]
		Class = hero.Class if hero.Class != "Neutral" else "Shaman"
		pool = self.Game.RNGPools["%s Spells with 1 or more Cost" % Class]
		return pool

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		#initiator of the discover should be InstructorFireheart_Effect(), not a real card
		#effectType=InstructorFireheart_Effect保证发现后调用的discoverDecided依然是InstructorFireheart_Effect的
		InstructorFireheart.discoverandGenerate(self, effectType=InstructorFireheart_Effect, comment='',
									  			poolFunc=lambda: self.decideSpellPool())

	#The initiator is this InstructorFireheart_Effect
	def discoverDecided(self, option, case, info_RNGSync=None, info_GUISync=None):
		self.card.handleDiscoverGeneratedCard(option, case, info_RNGSync, info_GUISync)
		self.savedObj = option

	def assistCreateCopy(self, Copy):
		if self.savedObj: Copy.savedObj = self.savedObj.createCopy(Copy.Game)


class GameManaAura_DemonicStudies(GameManaAura_OneTime):
	card, by, temporary = DemonicStudies, -1, False
	def applicable(self, target): return target.ID == self.ID and "Demon" in target.race

class GameManaAura_AthleticStudies(GameManaAura_OneTime):
	card, by, temporary = AthleticStudies, -1, False
	def applicable(self, target): return target.ID == self.ID and target.category == "Minion" and target.effects["Rush"] > 0


TrigsDeaths_Academy = {Death_SneakyDelinquent: (SneakyDelinquent, "Deathrattle: Add a 3/1 Ghost with Stealth to your hand"),
						Death_EducatedElekk: (EducatedElekk, "Deathrattle: Shuffle remembered spells into your deck"),
						Death_FishyFlyer: (FishyFlyer, "Deathrattle: Add a 4/3 Ghost with Rush to your hand"),
						Death_SmugSenior: (SmugSenior, "Deathrattle: Add a 5/7 Ghost with Taunt to your hand"),
						Death_PlaguedProtodrake: (PlaguedProtodrake, "Deathrattle: Summon a random 7-Cost minion"),
						Death_BloatedPython: (BloatedPython, "Deathrattle: Summon a 4/4 Hapless Handler"),
						Death_TeachersPet: (TeachersPet, "Deathrattle: Summon a random 3-Cost Beast"),
						Trig_JandiceBarov: (JandiceBarov, "This minion dies when it takes damage"),
						Trig_PowerWordFeast: (PowerWordFeast, "Restore this minion to full health at the end of this turn"),
						Death_InfiltratorLilian: (InfiltratorLilian, "Deathrattle: Summon a 4/2 Forsaken Lilian that attacks a random enemy"),
						Death_TotemGoliath: (TotemGoliath, "Deathrattle: Summon all four basic totems"),
						Death_BonewebEgg: (BonewebEgg, "Deathrattle: Summon two 2/1 Spiders"),
						Death_LordBarov: (LordBarov, "Deathrattle: Deal 1 damage to all minions"),
						}

Academy_Cards = [
		#Neutral
		TransferStudent, TransferStudent_Ogrimmar, TransferStudent_Stormwind, TransferStudent_FourWindValley,
		TransferStudent_Stranglethorn, TransferStudent_Outlands, TransferStudent_Academy, TransferStudent_Darkmoon,
		TransferStudent_Darkmoon_Corrupt, DeskImp, AnimatedBroomstick, IntrepidInitiate, PenFlinger, SphereofSapience,
		TourGuide, CultNeophyte, ManafeederPanthara, SneakyDelinquent, SpectralDelinquent, VoraciousReader, Wandmaker,
		EducatedElekk, EnchantedCauldron, RobesofProtection, CrimsonHothead, DivineRager, FishyFlyer, SpectralFlyer,
		LorekeeperPolkelt, WretchedTutor, HeadmasterKelThuzad, LakeThresher, Ogremancer, RisenSkeleton, StewardofScrolls,
		Vectus, PlaguedHatchling, OnyxMagescribe, SmugSenior, SpectralSenior, SorcerousSubstitute, KeymasterAlabaster,
		PlaguedProtodrake,
		#Demon Hunter
		DemonCompanion, Reffuh, Kolek, Shima, DoubleJump, TrueaimCrescent, AceHunterKreen, Magehunter, ShardshatterMystic,
		Glide, Marrowslicer, StarStudentStelina, VilefiendTrainer, SnarlingVilefiend, BloodHerald, SoulshardLapidary,
		CycleofHatred, SpiritofVengeance, FelGuardians, SoulfedFelhound, AncientVoidHound,
		#Druid
		LightningBloom, Gibberling, NatureStudies, PartnerAssignment, SpeakerGidra, Groundskeeper, TwilightRunner,
		ForestWardenOmu, RunicCarvings, TreantTotem, SurvivaloftheFittest,
		#Hunter
		AdorableInfestation, MarsuulCub, CarrionStudies, Overwhelm, Wolpertinger, BloatedPython, HaplessHandler,
		ProfessorSlate, ShandoWildclaw, KroluskBarkstripper, TeachersPet, GuardianAnimals,
		#Mage
		BrainFreeze, LabPartner, WandThief, CramSession, Combustion, Firebrand, PotionofIllusion, JandiceBarov,
		MozakiMasterDuelist, WyrmWeaver,
		#Paladin
		FirstDayofSchool, WaveofApathy, ArgentBraggart, GiftofLuminance, GoodyTwoShields, HighAbbessAlura,
		BlessingofAuthority, DevoutPupil, JudiciousJunior, TuralyontheTenured,
		#Priest
		RaiseDead, DraconicStudies, FrazzledFreshman, MindrenderIllucia, PowerWordFeast, BrittleboneDestroyer, CabalAcolyte,
		DisciplinarianGandling, FailedStudent, Initiation, FleshGiant,
		#Rogue
		SecretPassage, Plagiarize, Coerce, SelfSharpeningSword, VulperaToxinblade, InfiltratorLilian, ForsakenLilian,
		ShiftySophomore, Steeldancer, CuttingClass, DoctorKrastinov,
		#Shaman
		DevolvingMissiles, PrimordialStudies, DiligentNotetaker, RuneDagger, TrickTotem, InstructorFireheart, MoltenBlast,
		MoltenElemental, RasFrostwhisper, TotemGoliath, TidalWave,
		#Warlock
		SoulFragment, DemonicStudies, Felosophy, SpiritJailer, BonewebEgg, BonewebSpider, SoulShear, SchoolSpirits,
		ShadowlightScholar, VoidDrinker, SoulciologistMalicia, ReleasedSoul, ArchwitchWillow,
		#Warrior
		AthleticStudies, ShieldofHonor, InFormation, CeremonialMaul, HonorStudent, LordBarov, Playmaker, ReapersScythe,
		Commencement, Troublemaker, Ruffian, Rattlegore,
]

Academy_Cards_Collectible = [
		#Neutral #TransferStudent is not here
		DeskImp, TransferStudent,
		AnimatedBroomstick, IntrepidInitiate, PenFlinger, SphereofSapience, TourGuide, CultNeophyte, ManafeederPanthara,
		SneakyDelinquent, VoraciousReader, Wandmaker, EducatedElekk, EnchantedCauldron, RobesofProtection, CrimsonHothead,
		DivineRager, FishyFlyer, LorekeeperPolkelt, WretchedTutor, HeadmasterKelThuzad, LakeThresher, Ogremancer,
		StewardofScrolls, Vectus, OnyxMagescribe, SmugSenior, SorcerousSubstitute, KeymasterAlabaster, PlaguedProtodrake,
		#Demon Hunter
		DemonCompanion, DoubleJump, TrueaimCrescent, AceHunterKreen, Magehunter, ShardshatterMystic, Glide, Marrowslicer,
		StarStudentStelina, VilefiendTrainer, BloodHerald, SoulshardLapidary, CycleofHatred, FelGuardians, AncientVoidHound,
		#Druid
		LightningBloom, Gibberling, NatureStudies, PartnerAssignment, SpeakerGidra, Groundskeeper, TwilightRunner,
		ForestWardenOmu, RunicCarvings, SurvivaloftheFittest,
		#Hunter
		AdorableInfestation, CarrionStudies, Overwhelm, Wolpertinger, BloatedPython, ProfessorSlate, ShandoWildclaw,
		KroluskBarkstripper, TeachersPet, GuardianAnimals,
		#Mage
		BrainFreeze, LabPartner, WandThief, CramSession, Combustion, Firebrand, PotionofIllusion, JandiceBarov,
		MozakiMasterDuelist, WyrmWeaver,
		#Paladin
		FirstDayofSchool, WaveofApathy, ArgentBraggart, GiftofLuminance, GoodyTwoShields, HighAbbessAlura,
		BlessingofAuthority, DevoutPupil, JudiciousJunior, TuralyontheTenured,
		#Priest
		RaiseDead, DraconicStudies, FrazzledFreshman, MindrenderIllucia, PowerWordFeast, BrittleboneDestroyer, CabalAcolyte,
		DisciplinarianGandling, Initiation, FleshGiant,
		#Rogue
		SecretPassage, Plagiarize, Coerce, SelfSharpeningSword, VulperaToxinblade, InfiltratorLilian, ShiftySophomore,
		Steeldancer, CuttingClass, DoctorKrastinov,
		#Shaman
		DevolvingMissiles, PrimordialStudies, DiligentNotetaker, RuneDagger, TrickTotem, InstructorFireheart, MoltenBlast,
		RasFrostwhisper, TotemGoliath, TidalWave,
		#Warlock
		DemonicStudies, Felosophy, SpiritJailer, BonewebEgg, SoulShear, SchoolSpirits, ShadowlightScholar, VoidDrinker,
		SoulciologistMalicia, ArchwitchWillow,
		#Warrior
		AthleticStudies, ShieldofHonor, InFormation, CeremonialMaul, LordBarov, Playmaker, ReapersScythe, Commencement,
		Troublemaker, Rattlegore,
]