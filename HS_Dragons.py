from Parts_ConstsFuncsImports import *
from Parts_CardTypes import *
from Parts_TrigsAuras import *

from HS_AcrossPacks import Lackeys, TheCoin, Claw, ArcaneMissiles, TruesilverChampion

#迦拉克隆通常不能携带多张，但是如果起始卡组中有多张的话，则尽量选择与玩家职业一致的迦拉克隆为主迦拉克隆；如果不能如此，则第一个检测到的为主迦拉克隆
#迦拉克隆如果被变形为其他随从，（通过咒术师等），只要对应卡的职业有迦拉克隆，会触发那个新职业的迦拉克隆的效果。
#视频链接https://www.bilibili.com/video/av80010478?from=search&seid=3438568171430047785
#迦拉克隆只有在我方这边的时候被祈求才能升级，之前的祈求对于刚刚从对方那里获得的迦拉克隆复制没有升级作用。
#牧师的迦拉克隆被两个幻术师先变成贼随从然后变成中立随从，祈求不再生效。
#牧师的加拉克隆被两个幻术师先变成中立随从，然后变成萨满随从，祈求会召唤2/1元素。
#牧师的迦拉克隆被一个幻术师变成中立 随从，然后从对方手牌中偷到术士的迦拉克隆，然后祈求没有任何事情发生。变身成为术士迦拉克隆之后主迦拉克隆刷新成为术士的迦拉克隆。
#不管迦拉克隆的技能有没有被使用过，祈求都会让技能生效。

#假设主迦拉克隆只有在使用迦拉克隆变身的情况下会重置。
#假设主迦拉克隆变成加基森三职业卡时，卡扎库斯视为牧师卡，艾雅黑掌视为盗贼卡，唐汉古视为战士卡
#不知道挖宝把迦拉克隆变成其他牌的话,主迦拉克隆是否会发生变化。
def invokeGalakrond(Game, ID):
	primaryGalakrond = Game.Counters.primaryGalakronds[ID]
	if primaryGalakrond:
		Class = primaryGalakrond.Class
		if "Priest" in Class:
			if Game.GUI: Game.GUI.showOffBoardTrig(GalakrondtheUnbreakable(Game, ID))
			primaryGalakrond.addCardtoHand(numpyChoice(Game.RNGPools["Priest Minions"]), ID, byType=True)
		elif "Rogue" in Class:
			if Game.GUI: Game.GUI.showOffBoardTrig(GalakrondtheNightmare(Game, ID))
			primaryGalakrond.addCardtoHand(numpyChoice(Lackeys), ID, byType=True)
		elif "Shaman" in Class:
			if Game.GUI: Game.GUI.showOffBoardTrig(GalakrondtheTempest(Game, ID))
			primaryGalakrond.summon(WindsweptElemental(Game, ID))
		elif "Warlock" in Class:
			if Game.GUI: Game.GUI.showOffBoardTrig(GalakrondtheWretched(Game, ID))
			primaryGalakrond.summon([DraconicImp(Game, ID) for _ in (0, 1)])
		elif "Warrior" in Class:
			if Game.GUI: Game.GUI.showOffBoardTrig(GalakrondtheUnbreakable(Game, ID))
			primaryGalakrond.giveHeroAttackArmor(ID, attGain=3, name=GalakrondtheUnbreakable)
	#invocation counter increases and upgrade the galakronds
	Game.Counters.invokes[ID] += 1
	for card in Game.Hand_Deck.hands[ID][:]:
		if "Galakrond, " in card.name:
			upgrade = card.upgradedGalakrond
			isPrimaryGalakrond = (card == primaryGalakrond)
			if hasattr(card, "progress"):
				card.progress += 1
				if upgrade and card.progress > 1:
					Game.Hand_Deck.replaceCardinHand(card, upgrade(Game, ID))
					if isPrimaryGalakrond:
						Game.Counters.primaryGalakronds[ID] = upgrade
	for card in Game.Hand_Deck.decks[ID][:]:
		if "Galakrond, " in card.name:
			upgrade = card.upgradedGalakrond
			isPrimaryGalakrond = (card == primaryGalakrond)
			if hasattr(card, "progress"):
				card.progress += 1
				if upgrade and card.progress > 1:
					Game.Hand_Deck.replaceCardinDeck(card, upgrade(Game, ID))
					if isPrimaryGalakrond:
						Game.Counters.primaryGalakronds[ID] = upgrade
						

"""Auras"""
class Aura_SkyClaw(Aura_AlwaysOn):
	attGain = 1
	def applicable(self, target): return "Mech" in target.race


class GameRuleAura_LivingDragonbreath(GameRuleAura):
	def auraAppears(self):
		self.keeper.Game.effects[self.keeper.ID]["Minions Can't Be Frozen"] += 1
		for minion in self.keeper.Game.minionsonBoard(self.keeper.ID):
			if minion.effects["Frozen"] > 0: minion.losesEffect("Frozen", amount=-1)

	def auraDisappears(self): self.keeper.Game.effects[self.keeper.ID]["Minions Can't Be Frozen"] -= 1

class GameRuleAura_DwarvenSharpshooter(GameRuleAura):
	def auraAppears(self): self.keeper.Game.powers[self.keeper.ID].getsEffect("Power Can Target Minions")
	def auraDisappears(self): self.keeper.Game.powers[self.keeper.ID].losesEffect("Power Can Target Minions")


"""Deathrattles"""
class Death_TastyFlyfish(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if dragons := [card for card in self.keeper.Game.Hand_Deck.hands[self.keeper.ID] if "Dragon" in card.race]:
			self.keeper.giveEnchant(numpyChoice(dragons), 2, 2, name=TastyFlyfish, add2EventinGUI=False)

class Death_BadLuckAlbatross(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.keeper
		minion.shuffleintoDeck([Albatross(minion.Game, 3-minion.ID) for _ in (0, 1)])

class Death_ChromaticEgg(Deathrattle_Minion):
	# 变形亡语只能触发一次。
	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrig(signal, ID, subject, target, number, comment):
			if self.savedObj:
				minion = self.keeper
				if minion.Game.GUI: minion.Game.GUI.deathrattleAni(minion)
				minion.Game.Counters.deathrattlesTriggered[minion.ID].append(Death_ChromaticEgg)
				minion.Game.transform(minion, self.savedObj(minion.Game, minion.ID))

	def selfCopy(self, recipient):
		trig = type(self)(recipient)
		trig.savedObj = self.savedObj
		return trig

	def assistCreateCopy(self, Copy):
		Copy.savedObj = self.savedObj

class Death_LeperGnome_Dragons(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.dealsDamage(self.keeper.Game.heroes[3 - self.keeper.ID], 2)

class Death_VioletSpellwing(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.addCardtoHand(ArcaneMissiles, self.keeper.ID)

class Death_DragonriderTalritha(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if dragons := [card for card in self.keeper.Game.Hand_Deck.hands[self.keeper.ID] if "Dragon" in card.race]:
			self.keeper.giveEnchant(numpyChoice(dragons), 3, 3, trig=Death_DragonriderTalritha, trigType="Deathrattle", connect=False,
									name=DragonriderTalritha, add2EventinGUI=False)

class Death_MindflayerKaahrj(Deathrattle_Minion):
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return target == self.keeper and self.savedObj

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.summon(self.savedObj(self.keeper.Game, self.keeper.ID))

	def selfCopy(self, recipient):
		trig = type(self)(recipient)
		trig.chosenMinionType = self.savedObj
		return trig

	def assistCreateCopy(self, Copy):
		Copy.savedObj = self.savedObj

class Death_GraveRune(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.summon([type(self.keeper)(self.keeper.Game, self.keeper.ID) for _ in (0, 1)])


class Death_Chronobreaker(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if self.keeper.Game.Hand_Deck.holdingDragon(self.keeper.ID):
			targets = self.keeper.Game.minionsonBoard(3 - self.keeper.ID)
			self.keeper.AOE_Damage(targets, [3 for minion in targets])

class Death_Waxadred(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.shuffleintoDeck(WaxadredsCandle(self.keeper.Game, self.keeper.ID))


"""Triggers"""
class Trig_DepthCharge(TrigBoard):
	signals = ("TurnStarts", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		targets = self.keeper.Game.minionsonBoard(self.keeper.ID) + self.keeper.Game.minionsonBoard(3-self.keeper.ID)
		self.keeper.AOE_Damage(targets, [5 for minion in targets])
		
		
class Trig_HotAirBalloon(TrigBoard):
	signals = ("TurnStarts", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.giveEnchant(self.keeper, statEnchant=Enchantment_Cumulative(0, 1, name=HotAirBalloon))
		

class Trig_ParachuteBrigand(TrigHand):
	signals = ("MinionBeenPlayed", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.inHand and subject.ID == self.keeper.ID and "Pirate" in subject.race

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.keeper
		#不知道会召唤在最右边还是打出的海盗的右边。假设在最右边
		if minion.Game.space(minion.ID) > 0:
			minion.Game.summonfrom(minion.Game.Hand_Deck.hands[minion.ID].index(minion), minion.ID, -1, minion, source='H')
			

#需要测试法术和随从的抽到时触发效果与这个孰先孰后。以及变形后的加拉克隆的效果触发。
#测试时阿兰纳斯蛛后不会触发其加血效果。场上同时有多个幻术师的时候，会依次发生多冷变形。https://www.bilibili.com/video/av79078930?from=search&seid=4964775667793261235
#源生宝典和远古谜团等卡牌抽到一张牌然后为期费用赋值等效果都会在变形效果生效之后进行赋值。
#与其他“每当你抽一张xx牌”的扳机（如狂野兽王）共同在场时，是按照登场的先后顺序（扳机的正常顺序结算）。
#不太清楚与阿鲁高如果结算，据说是阿鲁高始终都会复制初始随从。不考虑这个所谓特例的可能性
#抽到“抽到时施放”的法术时，不会触发其效果，直接变成传说随从，然后也不追加抽牌。
class Trig_Transmogrifier(TrigBoard):
	signals = ("CardDrawn", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and target[0].ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.Game.Hand_Deck.replaceCardDrawn(target, numpyChoice(self.rngPool("Legendary Minions"))(self.keeper.Game, self.keeper.ID))
			

class Trig_DreadRaven(Trig_SelfAura):
	signals = ("MinionAppears", "MinionDisappears")
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and (('A' in signal or subject.ID == self.keeper.ID and subject.name == "Dread Raven") or
										('D' in signal or target.ID == self.keeper.ID and target.name == "Dread Raven"))

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.calcStat()

class Trig_WingCommander(Trig_SelfAura):
	signals = ("CardEntersHand", "CardLeavesHand")
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and ID == self.keeper.ID and \
			   (('E' in signal and "Dragon" in target[0].race) or ('L' in signal and "Dragon" in target.race))

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.calcStat()

		
class Trig_Shuma(TrigBoard):
	signals = ("TurnEnds", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.summon([Tentacle_Dragons(self.keeper.Game, self.keeper.ID) for i in range(6)], relative="<>")
		

class Trig_SecuretheDeck(Trig_Quest):
	signals = ("HeroAttackedHero", "HeroAttackedMinion", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.keeper.Game.heroes[self.keeper.ID]

		
class Trig_StrengthinNumbers(Trig_Quest):
	signals = ("MinionBeenPlayed", )
	def handleCounter(self, signal, ID, subject, target, number, comment, choice=0):
		self.counter += number
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.keeper.ID

				
class Trig_Aeroponics(TrigHand):
	signals = ("MinionAppears", "MinionDisappears", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.inHand and ((signal[6] == 'A' and subject.name == "Treant")
										or (signal[6] == 'D' and target.name == "Treant"))

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.Game.Manas.calcMana_Single(self.keeper)


class Trig_CleartheWay(Trig_Quest):
	signals = ("MinionBeenSummoned", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		#不知道召唤随从因为突袭光环而具有突袭是否可以算作任务进度
		return subject.ID == self.keeper.ID and subject.effects["Rush"] > 0


class Trig_ToxicReinforcement(Trig_Quest):
	signals = ("HeroUsedAbility", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return ID == self.keeper.ID


class Trig_PhaseStalker(TrigBoard):
	signals = ("HeroUsedAbility", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.Game.Secrets.deploySecretsfromDeck(self.keeper.ID, initiator=self.keeper)
		
		
class Trig_Dragonbane(TrigBoard):
	signals = ("HeroUsedAbility", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		chars = self.keeper.Game.charsAlive(3-self.keeper.ID)
		if chars: self.keeper.dealsDamage(numpyChoice(chars), 5)
		
		
class Trig_ElementalAllies(Trig_Quest):
	signals = ("MinionBeenPlayed", "TurnEnds", )
	def handleCounter(self, signal, ID, subject, target, number, comment, choice=0):
		if signal.startswith('T'): self.counter = 0
		else: self.counter += 1
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		quest = self.keeper
		playedElementsThisTurn = any("Elemental" in card.race for card in quest.Game.Counters.cardsEachTurn_Players[quest.ID][-1])
		if signal == "TurnEnds": return quest.ID == ID and not playedElementsThisTurn
		else: return subject.ID == quest.ID and "Elemental" in subject.race and not playedElementsThisTurn

			
class Trig_LearnDraconic(Trig_Quest):
	signals = ("SpellBeenPlayed", )
	def handleCounter(self, signal, ID, subject, target, number, comment, choice=0):
		self.counter += number
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.keeper.ID and self.keeper != subject


class Trig_Chenvaala(Trig_Countdown):
	signals, counter = ("SpellBeenPlayed", "NewTurnStarts"), 3
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and (signal == "NewTurnStarts" or subject.ID == self.keeper.ID)

	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrig(signal, ID, subject, target, number, comment):
			counter = self.counter
			if signal == "NewTurnStarts": self.counter = 3
			else: self.counter -= 1
			if counter != self.counter and (btn := self.keeper.btn) and "Hourglass" in btn.icons:
				btn.GUI.seqHolder[-1].append(btn.icons["Hourglass"].seqUpdateText())
			if self.counter < 1: self.keeper.summon(SnowElemental(self.keeper.Game, self.keeper.ID))


class Trig_ManaGiant(TrigHand):
	signals = ("SpellBeenPlayed", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.inHand and subject.ID == self.keeper.ID and subject.creator

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.Game.Manas.calcMana_Single(self.keeper)
		
		
class Trig_RighteousCause(Trig_Quest):
	signals = ("MinionBeenSummoned", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.keeper.ID

			
class Trig_Sanctuary(Trig_Quest):
	signals = ("TurnStarts", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return ID == self.keeper.ID and self.keeper.Game.Counters.dmgHeroTookLastTurn[ID] < 1


class Trig_CandleBreath(TrigHand):
	signals = ("CardLeavesHand", "CardEntersHand", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		#Only cards with a different class than your hero class will trigger this
		card = target[0] if signal == "CardEntersHand" else target
		return self.keeper.inHand and card.ID == self.keeper.ID and card.category == "Minion" and "Dragon" in card.race
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.Game.Manas.calcMana_Single(self.keeper)
		

class Trig_SurgingTempest(TrigBoard):
	signals = ("OverloadCheck", )
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.calcStat()

class Trig_Bandersmosh_PreShifting(TrigHand):
	signals = ("TurnStarts", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.inHand and ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = numpyChoice(self.rngPool("Legendary Minions"))(self.keeper.Game, self.keeper.ID)
		minion.statReset(5, 5, source=type(self.keeper))
		ManaMod(minion, to=5).applies()
		trig = Trig_Bandersmosh_KeepShifting(minion)
		trig.connect()
		minion.trigsBoard.append(trig)
		self.keeper.Game.Hand_Deck.replaceCardinHand(self.keeper, minion)

class Trig_Bandersmosh_KeepShifting(TrigBoard):
	signals = ("TurnStarts", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.inHand and ID == self.keeper.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = numpyChoice(self.rngPool("Legendary Minions"))(self.keeper.Game, self.keeper.ID)
		minion.statReset(5, 5, source=type(self.keeper))
		ManaMod(minion, to=5).applies()
		trig = Trig_Bandersmosh_KeepShifting(minion) #新的扳机保留这个变色龙的原有reference.在对方无手牌时会变回起始的变色龙。
		trig.connect()
		minion.trigsBoard.append(trig)
		self.keeper.Game.Hand_Deck.replaceCardinHand(self.keeper, minion)
			
			
class Trig_StormEgg(TrigBoard):
	signals = ("TurnStarts", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.Game.transform(self.keeper, StormDrake(self.keeper.Game, self.keeper.ID))
		

class Trig_ZzerakutheWarped(TrigBoard):
	signals = ("HeroTakesDmg", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return target == self.keeper.Game.heroes[self.keeper.ID]

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.summon(NetherDrake(self.keeper.Game, self.keeper.ID))
		

class Trig_Ancharrr(TrigBoard):
	signals = ("BattleFinished", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.keeper.Game.heroes[self.keeper.ID] and self.keeper.onBoard

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.drawCertainCard(lambda card: "Pirate" in card.race)
		
		
class Trig_Skybarge(TrigBoard):
	signals = ("MinionBeenSummoned", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject.ID == self.keeper.ID and "Pirate" in subject.race

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		chars = self.keeper.Game.charsAlive(3-self.keeper.ID)
		if chars: self.keeper.dealsDamage(numpyChoice(chars), 2)
		
		
#迦拉克隆通常不能携带多张，但是如果起始卡组中有多张的话，则尽量选择与玩家职业一致的迦拉克隆为主迦拉克隆；如果不能如此，则第一个检测到的为主迦拉克隆
#迦拉克隆如果被变形为其他随从，（通过咒术师等），只要对应卡的职业有迦拉克隆，会触发那个新职业的迦拉克隆的效果。
#视频链接https://www.bilibili.com/video/av80010478?from=search&seid=3438568171430047785
#迦拉克隆只有在我方这边的时候被祈求才能升级，之前的祈求对于刚刚从对方那里获得的迦拉克隆复制没有升级作用。
#牧师的迦拉克隆被两个幻术师先变成贼随从然后变成中立随从，祈求不再生效。
#牧师的加拉克隆被两个幻术师先变成中立随从，然后变成萨满随从，祈求会召唤2/1元素。
#牧师的迦拉克隆被一个幻术师变成中立 随从，然后从对方手牌中偷到术士的迦拉克隆，然后祈求没有任何事情发生。变身成为术士迦拉克隆之后主迦拉克隆刷新成为术士的迦拉克隆。
#不管迦拉克隆的技能有没有被使用过，祈求都会让技能生效。
#假设主迦拉克隆只有在使用迦拉克隆变身的情况下会重置。
#假设主迦拉克隆变成加基森三职业卡时，卡扎库斯视为牧师卡，艾雅黑掌视为盗贼卡，唐汉古视为战士卡
#不知道挖宝把迦拉克隆变成其他牌的话,主迦拉克隆是否会发生变化。
class Galakrond_Hero(Hero):
	def entersHand(self):
		self.inHand = True
		self.onBoard = self.inDeck = False
		self.enterHandTurn = self.Game.numTurn
		if self.Game.Counters.primaryGalakronds[self.ID] is None:
			self.Game.Counters.primaryGalakronds[self.ID] = self
		for trig in self.trigsHand: trig.connect()
		return self
		
	def entersDeck(self):
		self.onBoard, self.inHand, self.inDeck = False, False, True
		self.Game.Manas.calcMana_Single(self)
		if self.Game.Counters.primaryGalakronds[self.ID] is None:
			self.Game.Counters.primaryGalakronds[self.ID] = self
		for trig in self.trigsDeck: trig.connect()
		
	def replaceHero(self, fromHeroCard=False):
		if (galakronds := self.Game.Counters.primaryGalakronds)[self.ID]:
			galakronds[self.ID] = self
		super(Galakrond_Hero, self).replaceHero(fromHeroCard)

	def played(self, target=None, choice=0, mana=0, posinHand=0, comment=""): #英雄牌使用不存在触发发现的情况
		if (galakronds := self.Game.Counters.primaryGalakronds)[self.ID]:
			galakronds[self.ID] = self
		super(Galakrond_Hero, self).played()

		
class BlazingBattlemage(Minion):
	Class, race, name = "Neutral", "", "Blazing Battlemage"
	mana, attack, health = 1, 2, 2
	index = "DRAGONS~Neutral~Minion~1~2~2~~Blazing Battlemage"
	requireTarget, effects, description = False, "", ""
	name_CN = "灼光战斗法师"
	
	
class DepthCharge(Minion):
	Class, race, name = "Neutral", "", "Depth Charge"
	mana, attack, health = 1, 0, 5
	index = "DRAGONS~Neutral~Minion~1~0~5~~Depth Charge"
	requireTarget, effects, description = False, "", "At the start of your turn, deal 5 damage to all minions"
	name_CN = "深潜炸弹"
	trigBoard = Trig_DepthCharge		


class HotAirBalloon(Minion):
	Class, race, name = "Neutral", "Mech", "Hot Air Balloon"
	mana, attack, health = 1, 1, 2
	index = "DRAGONS~Neutral~Minion~1~1~2~Mech~Hot Air Balloon"
	requireTarget, effects, description = False, "", "At the start of your turn, gain +1 Health"
	name_CN = "热气球"
	trigBoard = Trig_HotAirBalloon		


class EvasiveChimaera(Minion):
	Class, race, name = "Neutral", "Beast", "Evasive Chimaera"
	mana, attack, health = 2, 2, 1
	index = "DRAGONS~Neutral~Minion~2~2~1~Beast~Evasive Chimaera~Poisonous"
	requireTarget, effects, description = False, "Poisonous,Evasive", "Poisonous. Can't be targeted by spells or Hero Powers"
	name_CN = "辟法奇美拉"
		
		
class DragonBreeder(Minion):
	Class, race, name = "Neutral", "", "Dragon Breeder"
	mana, attack, health = 2, 2, 3
	index = "DRAGONS~Neutral~Minion~2~2~3~~Dragon Breeder~Battlecry"
	requireTarget, effects, description = True, "", "Battlecry: Choose a friendly Dragon. Add a copy of it to your hand"
	name_CN = "幼龙饲养员"
	def effCanTrig(self):
		self.effectViable = False
		for minion in self.Game.minionsonBoard(self.ID):
			if "Dragon" in minion.race:
				self.effectViable = True
				break
				
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.ID == self.ID and "Dragon" in target.race and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.addCardtoHand(type(target), self.ID)
		return target
		
		
class GrizzledWizard(Minion):
	Class, race, name = "Neutral", "", "Grizzled Wizard"
	mana, attack, health = 2, 3, 2
	index = "DRAGONS~Neutral~Minion~2~3~2~~Grizzled Wizard~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Swap Hero Powers with your opponent until next turn"
	name_CN = "灰发巫师"
	
	def swapHeroPowers(self):
		temp = self.Game.powers[1]
		self.Game.powers[1].disappears()
		self.Game.powers[2].disappears()
		self.Game.powers[1] = self.Game.powers[2]
		self.Game.powers[2] = temp
		self.Game.powers[1].appears()
		self.Game.powers[2].appears()
		self.Game.powers[1].ID, self.Game.powers[2].ID = 1, 2
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		#The Hero Powers are swapped at the start of your next turn
		GrizzledWizard.swapHeroPowers(self)
		SwapHeroPowersBack(self.Game, self.ID).connect()


class ParachuteBrigand(Minion):
	Class, race, name = "Neutral", "Pirate", "Parachute Brigand"
	mana, attack, health = 2, 2, 2
	index = "DRAGONS~Neutral~Minion~2~2~2~Pirate~Parachute Brigand"
	requireTarget, effects, description = False, "", "After you play a Pirate, summon this minion from your hand"
	name_CN = "空降歹徒"
	trigHand = Trig_ParachuteBrigand


class TastyFlyfish(Minion):
	Class, race, name = "Neutral", "Murloc", "Tasty Flyfish"
	mana, attack, health = 2, 2, 2
	index = "DRAGONS~Neutral~Minion~2~2~2~Murloc~Tasty Flyfish~Deathrattle"
	requireTarget, effects, description = False, "", "Deathrattle: Give a Dragon in your hand +2/+2"
	name_CN = "美味飞鱼"
	deathrattle = Death_TastyFlyfish

#需要测试法术和随从的抽到时触发效果与这个孰先孰后。以及变形后的加拉克隆的效果触发。
#测试时阿兰纳斯蛛后不会触发其加血效果。场上同时有多个幻术师的时候，会依次发生多冷变形。https://www.bilibili.com/video/av79078930?from=search&seid=4964775667793261235
#源生宝典和远古谜团等卡牌抽到一张牌然后为期费用赋值等效果都会在变形效果生效之后进行赋值。
#与其他“每当你抽一张xx牌”的扳机（如狂野兽王）共同在场时，是按照登场的先后顺序（扳机的正常顺序结算）。
#不太清楚与阿鲁高如果结算，据说是阿鲁高始终都会复制初始随从。不考虑这个所谓特例的可能性
#抽到“抽到时施放”的法术时，不会触发其效果，直接变成传说随从，然后也不追加抽牌。
class Transmogrifier(Minion):
	Class, race, name = "Neutral", "", "Transmogrifier"
	mana, attack, health = 2, 2, 3
	index = "DRAGONS~Neutral~Minion~2~2~3~~Transmogrifier"
	requireTarget, effects, description = False, "", "Whenever you draw a card, transform it into a random Legendary minion"
	name_CN = "幻化师"
	trigBoard = Trig_Transmogrifier		
	poolIdentifier = "Legendary Minions"
	@classmethod
	def generatePool(cls, pools):
		return "Legendary Minions", list(pools.LegendaryMinions.values())
		


class WyrmrestPurifier(Minion):
	Class, race, name = "Neutral", "", "Wyrmrest Purifier"
	mana, attack, health = 2, 3, 2
	index = "DRAGONS~Neutral~Minion~2~3~2~~Wyrmrest Purifier~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Transform all Neutral cards in your deck into random cards from your class"
	name_CN = "龙眠净化者"
	poolIdentifier = "Druid Cards"
	@classmethod
	def generatePool(cls, pools):
		return [Class+" Cards" for Class in pools.Classes], [list(pools.ClassCards[Class].values()) for Class in pools.Classes]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		game = self.Game
		ownDeck = game.Hand_Deck.decks[self.ID]
		neutralIndices = [i for i, card in enumerate(ownDeck) if card.Class == "Neutral"]
		if neutralIndices:
			#不知道如果我方英雄没有职业时，变形成的牌是否会是中立。假设会变形成为随机职业
			newCards = numpyChoice(self.rngPool(classforDiscover(self) + " Cards"), len(neutralIndices), replace=True)
			for i, newCard in zip(neutralIndices, newCards):
				game.Hand_Deck.extractfromDeck(i, self.ID)
				card = newCard(game, self.ID)
				ownDeck.insert(i, card)
				card.entersDeck()
		

class BlowtorchSaboteur(Minion):
	Class, race, name = "Neutral", "", "Blowtorch Saboteur"
	mana, attack, health = 3, 3, 4
	index = "DRAGONS~Neutral~Minion~3~3~4~~Blowtorch Saboteur~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Your opponent's next Hero Power costs (3)"
	name_CN = "喷灯破坏者"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.Manas.PowerAuras_Backup.append(GameManaAura_BlowtorchSaboteur(self.Game, 3-self.ID))
		

class DreadRaven(Minion):
	Class, race, name = "Neutral", "Beast", "Dread Raven"
	mana, attack, health = 3, 3, 4
	index = "DRAGONS~Neutral~Minion~3~3~4~Beast~Dread Raven"
	requireTarget, effects, description = False, "", "Has +3 Attack for each other Dread Raven you control"
	name_CN = "恐惧渡鸦"
	trigBoard = Trig_DreadRaven
	def statCheckResponse(self):
		if self.onBoard and not self.silenced:
			self.attack += 3 * sum(minion.name == "Dread Raven" for minion in self.Game.minionsonBoard(self.ID, exclude=self))

			
class FireHawk(Minion):
	Class, race, name = "Neutral", "Elemental", "Fire Hawk"
	mana, attack, health = 3, 1, 3
	index = "DRAGONS~Neutral~Minion~3~1~3~Elemental~Fire Hawk~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Gain +1 Attack for each card in your opponent's hand"
	name_CN = "火鹰"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.giveEnchant(self, len(self.Game.Hand_Deck.hands[3-self.ID]), 0, name=FireHawk)
		
		
class GoboglideTech(Minion):
	Class, race, name = "Neutral", "", "Goboglide Tech"
	mana, attack, health = 3, 3, 3
	index = "DRAGONS~Neutral~Minion~3~3~3~~Goboglide Tech~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: If you control a Mech, gain +1/+1 and Rush"
	name_CN = "地精滑翔技师"
	def effCanTrig(self):
		self.effectViable = any("Mech" in minion.race for minion in self.Game.minionsonBoard(self.ID))
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if any("Mech" in minion.race for minion in self.Game.minionsonBoard(self.ID)):
			self.giveEnchant(self, 1, 1, effGain="Rush", name=GoboglideTech)


class LivingDragonbreath(Minion):
	Class, race, name = "Neutral", "Elemental", "Living Dragonbreath"
	mana, attack, health = 3, 3, 4
	index = "DRAGONS~Neutral~Minion~3~3~4~Elemental~Living Dragonbreath"
	requireTarget, effects, description = False, "", "Your minions can't be Frozen"
	name_CN = "活化龙息"
	aura = GameRuleAura_LivingDragonbreath

		
class Scalerider(Minion):
	Class, race, name = "Neutral", "", "Scalerider"
	mana, attack, health = 3, 3, 3
	index = "DRAGONS~Neutral~Minion~3~3~3~~Scalerider~Battlecry"
	requireTarget, effects, description = True, "", "Battlecry: If you're holding a Dragon, deal 2 damage"
	name_CN = "锐鳞骑士"
	
	def needTarget(self, choice=0):
		return self.Game.Hand_Deck.holdingDragon(self.ID)
		
	def effCanTrig(self): #Friendly characters are always selectable.
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and self.Game.Hand_Deck.holdingDragon(self.ID):
			self.dealsDamage(target, 2)
		return target
		
		
class BadLuckAlbatross(Minion):
	Class, race, name = "Neutral", "Beast", "Bad Luck Albatross"
	mana, attack, health = 4, 4, 3
	index = "DRAGONS~Neutral~Minion~4~4~3~Beast~Bad Luck Albatross~Deathrattle"
	requireTarget, effects, description = False, "", "Deathrattle: Shuffle two 1/1 Albatross into your opponent's deck"
	name_CN = "厄运信天翁"
	deathrattle = Death_BadLuckAlbatross


class Albatross(Minion):
	Class, race, name = "Neutral", "Beast", "Albatross"
	mana, attack, health = 1, 1, 1
	index = "DRAGONS~Neutral~Minion~1~1~1~Beast~Albatross~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "信天翁"
	
	
class DevotedManiac(Minion):
	Class, race, name = "Neutral", "", "Devoted Maniac"
	mana, attack, health = 4, 2, 2
	index = "DRAGONS~Neutral~Minion~4~2~2~~Devoted Maniac~Rush~Battlecry"
	requireTarget, effects, description = False, "Rush", "Rush. Battlecry: Invoke Galakrond"
	name_CN = "虔诚信徒"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		invokeGalakrond(self.Game, self.ID)
		
		
class DragonmawPoacher(Minion):
	Class, race, name = "Neutral", "", "Dragonmaw Poacher"
	mana, attack, health = 4, 4, 4
	index = "DRAGONS~Neutral~Minion~4~4~4~~Dragonmaw Poacher~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: If your opponent controls a Dragon, gain +4/+4 and Rush"
	name_CN = "龙喉偷猎者"
	
	def effCanTrig(self):
		self.effectViable = any("Dragon" in minion.race for minion in self.Game.minionsonBoard(3-self.ID))
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if any("Dragon" in minion.race for minion in self.Game.minionsonBoard(3-self.ID)):
			self.giveEnchant(self, 4, 4, effGain="Rush", name=DragonmawPoacher)
		
		
class EvasiveFeywing(Minion):
	Class, race, name = "Neutral", "Dragon", "Evasive Feywing"
	mana, attack, health = 4, 5, 4
	index = "DRAGONS~Neutral~Minion~4~5~4~Dragon~Evasive Feywing"
	requireTarget, effects, description = False, "Evasive", "Can't be targeted by spells or Hero Powers"
	name_CN = "辟法灵龙"
		
		
class FrizzKindleroost(Minion):
	Class, race, name = "Neutral", "", "Frizz Kindleroost"
	mana, attack, health = 4, 5, 4
	index = "DRAGONS~Neutral~Minion~4~5~4~~Frizz Kindleroost~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: Reduce the Cost of Dragons in your deck by (2)"
	name_CN = "弗瑞兹光巢"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if card.category == "Minion" and "Dragon" in card.race:
				ManaMod(card, by=-2).applies()
		
		
class Hippogryph(Minion):
	Class, race, name = "Neutral", "Beast", "Hippogryph"
	mana, attack, health = 4, 2, 6
	index = "DRAGONS~Neutral~Minion~4~2~6~Beast~Hippogryph~Rush~Taunt"
	requireTarget, effects, description = False, "Rush,Taunt", "Rush, Taunt"
	name_CN = "角鹰兽"
	
	
class HoardPillager(Minion):
	Class, race, name = "Neutral", "Pirate", "Hoard Pillager"
	mana, attack, health = 4, 4, 2
	index = "DRAGONS~Neutral~Minion~4~4~2~Pirate~Hoard Pillager~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Equip one of your destroyed weapons"
	name_CN = "藏宝匪贼"
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.weaponsDestroyedThisGame[self.ID] != []
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		weapons = self.Game.Counters.weaponsDestroyedThisGame[self.ID]
		if weapons: self.equipWeapon(numpyChoice(weapons)(self.Game, self.ID))
		
		
class TrollBatrider(Minion):
	Class, race, name = "Neutral", "", "Troll Batrider"
	mana, attack, health = 4, 3, 3
	index = "DRAGONS~Neutral~Minion~4~3~3~~Troll Batrider~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Deal 3 damage to a random enemy minion"
	name_CN = "巨魔蝙蝠骑士"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		minions = self.Game.minionsAlive(3-self.ID)
		if minions: self.dealsDamage(numpyChoice(minions), 3)
		

class WingCommander(Minion):
	Class, race, name = "Neutral", "", "Wing Commander"
	mana, attack, health = 4, 2, 5
	index = "DRAGONS~Neutral~Minion~4~2~5~~Wing Commander"
	requireTarget, effects, description = False, "", "Has +2 Attack for each Dragon in your hand"
	name_CN = "空军指挥官"
	trigBoard = Trig_WingCommander
	def statCheckResponse(self):
		if self.onBoard and not self.silenced:
			self.attack += 2 * sum("Dragon" in minion.race for minion in self.Game.Hand_Deck.hands[self.ID])


class ZulDrakRitualist(Minion):
	Class, race, name = "Neutral", "", "Zul'Drak Ritualist"
	mana, attack, health = 4, 3, 9
	index = "DRAGONS~Neutral~Minion~4~3~9~~Zul'Drak Ritualist~Taunt~Battlecry"
	requireTarget, effects, description = False, "Taunt", "Taunt. Battlecry: Summon three random 1-Cost minions for your opponent"
	name_CN = "祖达克仪祭师"
	poolIdentifier = "1-Cost Minions to Summon"
	@classmethod
	def generatePool(cls, pools):
		return "1-Cost Minion to Summon", list(pools.MinionsofCost[1].values())
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		minions = numpyChoice(self.rngPool("1-Cost Minions to Summon"), 3, replace=True)
		self.summon([minion(self.Game, 3-self.ID) for minion in minions])
		
		
class BigOlWhelp(Minion):
	Class, race, name = "Neutral", "Dragon", "Big Ol' Whelp"
	mana, attack, health = 5, 5, 5
	index = "DRAGONS~Neutral~Minion~5~5~5~Dragon~Big Ol' Whelp~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Draw a card"
	name_CN = "雏龙巨婴"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.Hand_Deck.drawCard(self.ID)
		
		
class ChromaticEgg(Minion):
	Class, race, name = "Neutral", "", "Chromatic Egg"
	mana, attack, health = 5, 0, 3
	index = "DRAGONS~Neutral~Minion~5~0~3~~Chromatic Egg~Battlecry~Deathrattle"
	requireTarget, effects, description = False, "", "Battlecry: Secretly Discover a Dragon to hatch into. Deathrattle: Hatch!"
	name_CN = "多彩龙蛋"
	deathrattle = Death_ChromaticEgg
	poolIdentifier = "Dragons as Druid to Summon"
	@classmethod
	def generatePool(cls, pools):
		classCards = {s : [] for s in pools.ClassesandNeutral}
		for key, value in pools.MinionswithRace["Dragon"].items():
			for Class in key.split('~')[1].split(','):
				classCards[Class].append(value)
		return ["Dragons as %s to Summon"+Class for Class in pools.Classes], \
				[classCards[Class]+classCards["Neutral"] for Class in pools.Classes]

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverandGenerate(ChromaticEgg, comment, poolFunc=lambda : self.rngPool("Dragons as %s to Summon"%classforDiscover(self)))
		
	def setDragontoHatch(self, cardType):
		for trig in self.deathrattles:
			if isinstance(trig, cardType): trig.savedObj = cardType
	
	def discoverDecided(self, option, case, info_RNGSync=None, info_GUISync=None):
		self.handleDiscoverGeneratedCard(option, case, info_RNGSync, info_GUISync,
										 func=lambda cardType, card: ChromaticEgg.setDragontoHatch(self, cardType))
		
		
class CobaltSpellkin(Minion):
	Class, race, name = "Neutral", "Dragon", "Cobalt Spellkin"
	mana, attack, health = 5, 3, 5
	index = "DRAGONS~Neutral~Minion~5~3~5~Dragon~Cobalt Spellkin~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Add two 1-Cost spells from your class to your hand"
	name_CN = "深蓝系咒师"
	poolIdentifier = "1-Cost Spells as Druid"
	@classmethod
	def generatePool(cls, pools):
		return ["1-Cost Spells as %s"%Class for Class in pools.Classes], \
				[[value for key, value in pools.ClassCards[Class].items() if "~Spell~" in key and key.split('~')[3] == '1'] for Class in pools.Classes]
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.addCardtoHand(numpyChoice(self.rngPool("1-Cost Spells as "+self.Game.heroes[self.ID].Class), 2, replace=False), self.ID)
		
		
class FacelessCorruptor(Minion):
	Class, race, name = "Neutral", "", "Faceless Corruptor"
	mana, attack, health = 5, 4, 4
	index = "DRAGONS~Neutral~Minion~5~4~4~~Faceless Corruptor~Rush~Battlecry"
	requireTarget, effects, description = True, "Rush", "Rush. Battlecry: Transform one of your friendly minions into a copy of this"
	name_CN = "无面腐蚀者"
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.ID == self.ID and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			Copy = self.selfCopy(self.ID, self) if self.onBoard or self.inHand else type(self)(self.Game, self.ID)
			return self.Game.transform(target, Copy)
		else: return target
		
		
class KoboldStickyfinger(Minion):
	Class, race, name = "Neutral", "Pirate", "Kobold Stickyfinger"
	mana, attack, health = 5, 4, 4
	index = "DRAGONS~Neutral~Minion~5~4~4~Pirate~Kobold Stickyfinger~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Steal your opponent's weapon"
	name_CN = "黏指狗头人"
	
	def effCanTrig(self):
		self.effectViable = self.Game.availableWeapon(3-self.ID)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		weapon = self.Game.availableWeapon(3-self.ID)
		if weapon:
			weapon.disappears()
			self.Game.weapons[3-self.ID].remove(weapon)
			weapon.ID = self.ID
			self.Game.equipWeapon(weapon)
		
	
class Platebreaker(Minion):
	Class, race, name = "Neutral", "", "Platebreaker"
	mana, attack, health = 5, 5, 5
	index = "DRAGONS~Neutral~Minion~5~5~5~~Platebreaker~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Destroy your opponent's Armor"
	name_CN = "破甲骑士"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.heroes[3-self.ID].armor = 0
		
		
class ShieldofGalakrond(Minion):
	Class, race, name = "Neutral", "", "Shield of Galakrond"
	mana, attack, health = 5, 4, 5
	index = "DRAGONS~Neutral~Minion~5~4~5~~Shield of Galakrond~Taunt~Battlecry"
	requireTarget, effects, description = False, "Taunt", "Taunt. Battlecry: Invoke Galakrond"
	name_CN = "迦拉克隆之盾"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		invokeGalakrond(self.Game, self.ID)
		
		
class Skyfin(Minion):
	Class, race, name = "Neutral", "Murloc", "Skyfin"
	mana, attack, health = 5, 3, 3
	index = "DRAGONS~Neutral~Minion~5~3~3~Murloc~Skyfin~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: If you're holding a Dragon, summon 2 random Murlocs"
	name_CN = "飞天鱼人"
	poolIdentifier = "Murlocs to Summon"
	@classmethod
	def generatePool(cls, pools):
		return "Murlocs to Summon", list(pools.MinionswithRace["Murloc"].values())
		
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Hand_Deck.holdingDragon(self.ID):
			murlocs = numpyChoice(self.rngPool("Murlocs to Summon"), 2, replace=True)
			self.summon([murloc(self.Game, self.ID) for murloc in murlocs], relative="<>")
		
		
class TentacledMenace(Minion):
	Class, race, name = "Neutral", "", "Tentacled Menace"
	mana, attack, health = 5, 6, 5
	index = "DRAGONS~Neutral~Minion~5~6~5~~Tentacled Menace~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Each player draws a card. Swap their Costs"
	name_CN = "触手恐吓者"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		card1, mana = self.Game.Hand_Deck.drawCard(self.ID)
		card2, mana = self.Game.Hand_Deck.drawCard(3-self.ID)
		if card1 and card2:
			mana1, mana2 = card1.mana, card2.mana
			ManaMod(card1, to=mana2).applies()
			ManaMod(card2, to=mana1).applies()
			self.Game.Manas.calcMana_Single(card1)
			self.Game.Manas.calcMana_Single(card2)
		
		
class CamouflagedDirigible(Minion):
	Class, race, name = "Neutral", "Mech", "Camouflaged Dirigible"
	mana, attack, health = 6, 6, 6
	index = "DRAGONS~Neutral~Minion~6~6~6~Mech~Camouflaged Dirigible~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Give your other Mechs Stealth until your next turn"
	name_CN = "迷彩飞艇"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for minion in self.Game.minionsonBoard(self.ID):
			if "Mech" in minion.race: minion.effects["Temp Stealth"] += 1
		
		
class EvasiveWyrm(Minion):
	Class, race, name = "Neutral", "Dragon", "Evasive Wyrm"
	mana, attack, health = 6, 5, 3
	index = "DRAGONS~Neutral~Minion~6~5~3~Dragon~Evasive Wyrm~Divine Shield~Rush"
	requireTarget, effects, description = False, "Divine Shield,Rush,Evasive", "Divine Shield, Rush. Can't be targeted by spells or Hero Powers"
	name_CN = "辟法巨龙"
		
		
class Gyrocopter(Minion):
	Class, race, name = "Neutral", "Mech", "Gyrocopter"
	mana, attack, health = 6, 4, 5
	index = "DRAGONS~Neutral~Minion~6~4~5~Mech~Gyrocopter~Rush~Windfury"
	requireTarget, effects, description = False, "Rush,Windfury", "Rush, Windfury"
	name_CN = "旋翼机"
	
	
class KronxDragonhoof(Minion):
	Class, race, name = "Neutral", "", "Kronx Dragonhoof"
	mana, attack, health = 6, 6, 6
	index = "DRAGONS~Neutral~Minion~6~6~6~~Kronx Dragonhoof~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: Draw Galakrond. If you're alread Galakrond, unleash a Devastation"
	name_CN = "克罗斯龙蹄"
	
	def effCanTrig(self):
		self.effectViable = "Galakrond" in self.Game.heroes[self.ID].name
	#迦拉克隆有主迦拉克隆机制，祈求时只有主迦拉克隆会响应
	#主迦拉克隆会尽量与玩家职业匹配，如果不能匹配，则系统检测到的第一张迦拉克隆会被触发技能
	#http://nga.178.com/read.php?tid=19587242&rand=356
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if not self.Game.heroes[self.ID].name.startswith("Galakrond"):
			self.drawCertainCard(lambda card: card.name.startswith("Galakrond, "))
		else: self.chooseFixedOptions(KronxDragonhoof, comment, 
										options=[Annihilation(ID=self.ID), Decimation(ID=self.ID), Domination(ID=self.ID), Reanimation(ID=self.ID)])
	
	#option here can be either category or object
	def discoverDecided(self, option, case, info_RNGSync=None, info_GUISync=None):
		game = self.Game
		if case == "Discovered" or case == "Random":
			game.picks_Backup.append((info_RNGSync, info_GUISync, False, type(option)))
		if option.name == "Annihilation":
			targets = game.minionsonBoard(self.ID, self) + game.minionsonBoard(3-self.ID)
			self.AOE_Damage(targets, [5]*len(targets))
		elif option.name == "Decimation":
			self.dealsDamage(game.heroes[3-self.ID], 5)
			self.restoresHealth(game.heroes[self.ID], self.calcHeal(5))
		elif option.name == "Domination":
			self.AOE_GiveEnchant(self.Game.minionsonBoard(self.ID, self), 2, 2, name=KronxDragonhoof)
		else: self.summon(ReanimatedDragon(game, self.ID))
		

class Annihilation(Option):
	name, description = "Annihilation", "Deal 5 damage to all other minions"
	mana, attack, health = 0, -1, -1

class Decimation(Option):
	name, description = "Decimation", "Deal 5 damage to the enemy hero. Restore 5 Health to your hero"
	mana, attack, health = 0, -1, -1

class Domination(Option):
	name, description = "Domination", "Give your other minions +2/+2"
	mana, attack, health = 0, -1, -1

class Reanimation(Option):
	name, description = "Reanimation", "Summon an 8/8 Dragon with Taunt"
	mana, attack, health = 0, -1, -1

class ReanimatedDragon(Minion):
	Class, race, name = "Neutral", "Dragon", "Reanimated Dragon"
	mana, attack, health = 8, 8, 8
	index = "DRAGONS~Neutral~Minion~8~8~8~Dragon~Reanimated Dragon~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "重生的巨龙"
	
	
class UtgardeGrapplesniper(Minion):
	Class, race, name = "Neutral", "", "Utgarde Grapplesniper"
	mana, attack, health = 6, 5, 5
	index = "DRAGONS~Neutral~Minion~6~5~5~~Utgarde Grapplesniper~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Both players draw a card. If it's a Dragon, summon it"
	name_CN = "乌特加德鱼叉射手"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		game = self.Game
		card1, mana, entersHand1 = game.Hand_Deck.drawCard(self.ID)
		card2, mana, entersHand2 = game.Hand_Deck.drawCard(3-self.ID)
		hands = game.Hand_Deck.hands
		if entersHand1 and "Dragon" in card1.race and card1 in hands[self.ID]:
			game.summonfrom(hands[self.ID].index(card1), self.ID, -1, self, source='H') #不知道我方随从是会召唤到这个随从的右边还是场上最右边。
		if entersHand2 and "Dragon" in card2.race and card2 in hands[3-self.ID]:
			game.summonfrom(hands[3-self.ID].index(card2), 3-self.ID, -1, self, source='H')
		

class EvasiveDrakonid(Minion):
	Class, race, name = "Neutral", "Dragon", "Evasive Drakonid"
	mana, attack, health = 7, 7, 7
	index = "DRAGONS~Neutral~Minion~7~7~7~Dragon~Evasive Drakonid~Taunt"
	requireTarget, effects, description = False, "Taunt,Evasive", "Taunt. Can't be targeted by spells or Hero Powers"
	name_CN = "辟法龙人"
	
	
class Shuma(Minion):
	Class, race, name = "Neutral", "", "Shu'ma"
	mana, attack, health = 7, 1, 7
	index = "DRAGONS~Neutral~Minion~7~1~7~~Shu'ma~Legendary"
	requireTarget, effects, description = False, "", "At the end of your turn, fill your board with 1/1 Tentacles"
	name_CN = "舒玛"
	trigBoard = Trig_Shuma		


class Tentacle_Dragons(Minion):
	Class, race, name = "Neutral", "", "Tentacle"
	mana, attack, health = 1, 1, 1
	index = "DRAGONS~Neutral~Minion~1~1~1~~Tentacle~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "触手"
	

class TwinTyrant(Minion):
	Class, race, name = "Neutral", "Dragon", "Twin Tyrant"
	mana, attack, health = 8, 4, 10
	index = "DRAGONS~Neutral~Minion~8~4~10~Dragon~Twin Tyrant~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Deal 4 damage to two random enemy minions"
	name_CN = "双头暴虐龙"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		minions = self.Game.minionsAlive(3-self.ID)
		if minions:
			targets = numpyChoice(minions, min(2, len(minions)), replace=False)
			self.AOE_Damage(targets, [4]*len(targets))
		

class DragonqueenAlexstrasza(Minion):
	Class, race, name = "Neutral", "Dragon", "Dragonqueen Alexstrasza"
	mana, attack, health = 9, 8, 8
	index = "DRAGONS~Neutral~Minion~9~8~8~Dragon~Dragonqueen Alexstrasza~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: If your deck has no duplicates, add two Dragons to your hand. They cost (1)"
	name_CN = "红龙女王阿莱克丝塔萨"
	poolIdentifier = "Dragons except Dragonqueen Alexstrasza"
	@classmethod
	def generatePool(cls, pools):
		dragons = list(pools.MinionswithRace["Dragon"].values())
		dragons.remove(DragonqueenAlexstrasza)
		return "Dragons except Dragonqueen Alexstrasza", dragons
		
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.noDuplicatesinDeck(self.ID)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		game = self.Game
		if game.Hand_Deck.noDuplicatesinDeck(self.ID):
			dragon1, dragon2 = numpyChoice(self.rngPool("Dragons except Dragonqueen Alexstrasza"), 2, replace=False)
			dragon1, dragon2 = dragon1(game, self.ID), dragon2(game, self.ID)
			self.addCardtoHand([dragon1, dragon2], self.ID)
			if dragon1.inHand:
				ManaMod(dragon1, to=1).applies()
				game.Manas.calcMana_Single(dragon1)
			if dragon2.inHand:
				ManaMod(dragon2, to=1).applies()
				game.Manas.calcMana_Single(dragon2)
		
		
class Sathrovarr(Minion):
	Class, race, name = "Neutral", "Demon", "Sathrovarr"
	mana, attack, health = 9, 5, 5
	index = "DRAGONS~Neutral~Minion~9~5~5~Demon~Sathrovarr~Battlecry~Legendary"
	requireTarget, effects, description = True, "", "Battlecry: Choose a friendly minion. Add a copy of it to your hand, deck and battlefield"
	name_CN = "萨索瓦尔"
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.ID == self.ID and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.addCardtoHand(type(target), self.ID)
			#不知道这个加入牌库是否算作洗入牌库，从而可以触发强能雷象等扳机
			self.shuffleintoDeck(type(target)(self.Game, self.ID))
			#不知道这个召唤的复制是会出现在这个随从右边还是目标随从右边
			Copy = target.selfCopy(self.ID, self) if target.onBoard else type(target)(self.Game, self.ID)
			self.summon(Copy)
		return target
		

class Embiggen(Spell):
	Class, school, name = "Druid", "Nature", "Embiggen"
	requireTarget, mana, effects = False, 0, ""
	index = "DRAGONS~Druid~Spell~0~Nature~Embiggen"
	description = "Give all minions in your deck +2/+2. They cost (1) more (up to 10)"
	name_CN = "森然巨化"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		typeSelf = type(self)
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if card.category == "Minion":
				card.getsBuffDebuff_inDeck(2, 2, source=typeSelf, name=Embiggen)
				if card.mana < 10: ManaMod(card, by=+1).applies()
		
		
class SecuretheDeck(Quest):
	Class, school, name = "Druid", "", "Secure the Deck"
	requireTarget, mana, effects = False, 1, ""
	index = "DRAGONS~Druid~Spell~1~~Secure the Deck~~Quest"
	description = "Sidequest: Attack twice with your hero. Reward: Add 3 'Claw' to your hand"
	name_CN = "保护甲板"
	race, trigBoard = "Sidequest", Trig_SecuretheDeck
	def questEffect(self, game, ID):
		self.addCardtoHand((Claw, Claw, Claw), ID)


class StrengthinNumbers(Quest):
	Class, school, name = "Druid", "", "Strength in Numbers"
	requireTarget, mana, effects = False, 1, ""
	index = "DRAGONS~Druid~Spell~1~~Strength in Numbers~~Quest"
	description = "Sidequest: Spend 10 Mana on minions. Rewards: Summon a minion from your deck"
	name_CN = "人多势众"
	race, trigBoard = "Sidequest", Trig_StrengthinNumbers
	def questEffect(self, game, ID):
		self.try_SummonfromDeck()
		
		
class SmallRepairs(Spell):
	Class, school, name = "Druid", "Nature", "Small Repairs"
	requireTarget, mana, effects = True, 1, ""
	index = "DRAGONS~Druid~Spell~1~Nature~Small Repairs~Uncollectible"
	description = "Give a minion +2 Health and Taunt"
	name_CN = "简单维修"
	def available(self):
		return self.selectableMinionExists(0)
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.giveEnchant(target, 0, 2, effGain="Taunt", name=SmallRepairs)
		return target
		
class SpinemUp(Spell):
	Class, school, name = "Druid", "Nature", "Spin 'em Up"
	requireTarget, mana, effects = False, 1, ""
	index = "DRAGONS~Druid~Spell~1~Nature~Spin 'em Up~Uncollectible"
	description = "Summon a 2/2 Treant"
	name_CN = "旋叶起飞"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon(Treant_Dragons(self.Game, self.ID))
		
class SmallRepairs_Option(Option):
	name, description = "Small Repairs", "Give a minion +2 Health and Taunt"
	mana, attack, health = 1, -1, -1
	spell = SmallRepairs
	def available(self):
		return self.keeper.selectableMinionExists(0)
		
class SpinemUp_Option(Option):
	name, description = "Spin 'em Up", "Summon a Treant"
	mana, attack, health = 1, -1, -1
	spell = SpinemUp
	def available(self):
		return self.keeper.Game.space(self.keeper.ID)
		
class Treenforcements(Spell):
	Class, school, name = "Druid", "Nature", "Treenforcements"
	requireTarget, mana, effects = True, 1, ""
	index = "DRAGONS~Druid~Spell~1~Nature~Treenforcements~Choose One"
	description = "Choose One - Give a minion +2 Health and Taunt; or Summon a 2/2 Taunt"
	name_CN = "树木增援"
	options = (SmallRepairs_Option, SpinemUp_Option)
	def needTarget(self, choice=0):
		return choice < 1
		
	def available(self): #当场上有全选光环时，变成了一个指向性法术，必须要有一个目标可以施放。
		if self.Game.effects[self.ID]["Choose Both"] > 0: return self.selectableMinionExists()
		else: return self.selectableMinionExists() or self.Game.space(self.ID) > 0
			
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if choice < 1 and target: self.giveEnchant(target, 0, 2, effGain="Taunt", name=Treenforcements)
		if choice != 0: self.summon(Treant_Dragons(self.Game, self.ID))
		return target
		

class BreathofDreams(Spell):
	Class, school, name = "Druid", "Nature", "Breath of Dreams"
	requireTarget, mana, effects = False, 2, ""
	index = "DRAGONS~Druid~Spell~2~Nature~Breath of Dreams"
	description = "Draw a card. If you're holding a Dragon, gain an empty Mana Crystal"
	name_CN = "梦境吐息"
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.Hand_Deck.drawCard(self.ID)
		if self.Game.Hand_Deck.holdingDragon(self.ID):
			self.Game.Manas.gainEmptyManaCrystal(1, self.ID)
		
		
class Shrubadier(Minion):
	Class, race, name = "Druid", "", "Shrubadier"
	mana, attack, health = 2, 1, 1
	index = "DRAGONS~Druid~Minion~2~1~1~~Shrubadier~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Summon a 2/2 Treant"
	name_CN = "盆栽投手"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon(Treant_Dragons(self.Game, self.ID))
		

class Treant_Dragons(Minion):
	Class, race, name = "Druid", "", "Treant"
	mana, attack, health = 2, 2, 2
	index = "DRAGONS~Druid~Minion~2~2~2~~Treant~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "树人"
	
	
class Aeroponics(Spell):
	Class, school, name = "Druid", "Nature", "Aeroponics"
	requireTarget, mana, effects = False, 5, ""
	index = "DRAGONS~Druid~Spell~5~Nature~Aeroponics"
	description = "Draw 2 cards. Costs (2) less for each Treant you control"
	name_CN = "空气栽培"
	trigHand = Trig_Aeroponics
	def selfManaChange(self):
		if self.inHand:
			numTreants = 0
			for minion in self.Game.minionsonBoard(self.ID):
				if minion.name == "Treant":
					numTreants += 1
					
			self.mana -= 2 * numTreants
			self.mana = max(0, self.mana)
			
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.Hand_Deck.drawCard(self.ID)
		self.Game.Hand_Deck.drawCard(self.ID)
		

class EmeraldExplorer(Minion):
	Class, race, name = "Druid", "Dragon", "Emerald Explorer"
	mana, attack, health = 6, 4, 8
	index = "DRAGONS~Druid~Minion~6~4~8~Dragon~Emerald Explorer~Taunt~Battlecry"
	requireTarget, effects, description = False, "Taunt", "Taunt. Battlecry: Discover a Dragon"
	name_CN = "翡翠龙探险者"
	poolIdentifier = "Dragons as Druid"
	@classmethod
	def generatePool(cls, pools):
		classCards = {s : [] for s in pools.ClassesandNeutral}
		for key, value in pools.MinionswithRace["Dragon"].items():
			classCards[key.split('~')[1]].append(value)
		return ["Dragons as "+Class for Class in pools.Classes], \
				[classCards[Class]+classCards["Neutral"] for Class in pools.Classes]
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverandGenerate(EmeraldExplorer, comment, poolFunc=lambda: self.rngPool("Dragons as "+classforDiscover(self)))
		
		
class GorutheMightree(Minion):
	Class, race, name = "Druid", "", "Goru the Mightree"
	mana, attack, health = 7, 5, 10
	index = "DRAGONS~Druid~Minion~7~5~10~~Goru the Mightree~Taunt~Battlecry~Legendary"
	requireTarget, effects, description = False, "Taunt", "Taunt. Battlecry: For the rest of the game, your Treants have +1/+1"
	name_CN = "强力巨树格鲁"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		GameAura_GorutheMightree(self.Game, self.ID).auraAppears()
		

class YseraUnleashed(Minion):
	Class, race, name = "Druid", "Dragon", "Ysera, Unleashed"
	mana, attack, health = 9, 4, 12
	index = "DRAGONS~Druid~Minion~9~4~12~Dragon~Ysera, Unleashed~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: Shuffle 7 Dream Portals into your deck. When drawn, summon a random Dragon"
	name_CN = "觉醒巨龙伊瑟拉"
	poolIdentifier = "Dragons to Summon"
	@classmethod
	def generatePool(cls, pools):
		return "Dragons to Summon", list(pools.MinionswithRace["Dragon"].values())
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.shuffleintoDeck([DreamPortal(self.Game, self.ID) for _ in range(7)])
		
class DreamPortal(Spell):
	Class, school, name = "Druid", "", "Dream Portal"
	requireTarget, mana, effects = False, 9, ""
	index = "DRAGONS~Druid~Spell~9~~Dream Portal~Casts When Drawn~Uncollectible"
	description = "Casts When Drawn. Summon a random Dragon"
	name_CN = "梦境之门"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon(numpyChoice(self.rngPool("Dragons to Summon"))(self.Game, self.ID))
		
		
class CleartheWay(Quest):
	Class, school, name = "Hunter", "", "Clear the Way"
	requireTarget, mana, effects = False, 1, ""
	index = "DRAGONS~Hunter~Spell~1~~Clear the Way~~Quest"
	description = "Sidequest: Summon 3 Rush minions. Reward: Summon a 4/4 Gryphon with Rush"
	name_CN = "扫清道路"
	race, trigBoard = "Sidequest", Trig_CleartheWay
	def questEffect(self, game, ID):
		self.summon(Gryphon_Dragons(game, ID))


class Gryphon_Dragons(Minion):
	Class, race, name = "Hunter", "Beast", "Gryphon"
	mana, attack, health = 4, 4, 4
	index = "DRAGONS~Hunter~Minion~4~4~4~Beast~Gryphon~Rush~Uncollectible"
	requireTarget, effects, description = False, "Rush", "Rush"
	name_CN = "狮鹫"


class DwarvenSharpshooter(Minion):
	Class, race, name = "Hunter", "", "Dwarven Sharpshooter"
	mana, attack, health = 1, 1, 3
	index = "DRAGONS~Hunter~Minion~1~1~3~~Dwarven Sharpshooter"
	requireTarget, effects, description = False, "", "Your Hero Power can target minions"
	name_CN = "矮人神射手"
	aura = GameRuleAura_DwarvenSharpshooter

		
class ToxicReinforcements(Quest):
	Class, school, name = "Hunter", "", "Toxic Reinforcements"
	requireTarget, mana, effects = False, 1, ""
	index = "DRAGONS~Hunter~Spell~1~~Toxic Reinforcements~~Quest"
	description = "Sidequest: Use your Hero Power three times. Reward: Summon three 1/1 Leper Gnomes"
	name_CN = "病毒增援"
	race, trigBoard = "Sidequest", Trig_ToxicReinforcement
	def questEffect(self, game, ID):
		self.summon([LeperGnome_Dragons(game, ID) for _ in (0, 1, 2)])


class LeperGnome_Dragons(Minion):
	Class, race, name = "Neutral", "", "Leper Gnome"
	mana, attack, health = 1, 2, 1
	index = "DRAGONS~Neutral~Minion~1~2~1~~Leper Gnome~Deathrattle~Uncollectible"
	requireTarget, effects, description = False, "", "Deathrattle: Deal 2 damage to the enemy hero"
	name_CN = "麻风侏儒"
	deathrattle = Death_LeperGnome_Dragons


class CorrosiveBreath(Spell):
	Class, school, name = "Hunter", "Nature", "Corrosive Breath"
	requireTarget, mana, effects = True, 2, ""
	index = "DRAGONS~Hunter~Spell~2~~Nature~Corrosive Breath"
	description = "Deal 3 damage to a minion. If you're holding a Dragon, it also hits the enemy hero"
	name_CN = "腐蚀吐息"
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID)
		
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = self.calcDamage(3)
			self.dealsDamage(target, damage)
			if self.Game.Hand_Deck.holdingDragon(self.ID):
				self.dealsDamage(self.Game.heroes[3-self.ID], damage)
		return target
		
		
class PhaseStalker(Minion):
	Class, race, name = "Hunter", "Beast", "Phase Stalker"
	mana, attack, health = 2, 2, 3
	index = "DRAGONS~Hunter~Minion~2~2~3~Beast~Phase Stalker"
	requireTarget, effects, description = False, "", "After you use your Hero Power, cast a Secret from your deck"
	name_CN = "相位追踪者"
	trigBoard = Trig_PhaseStalker		


class DivingGryphon(Minion):
	Class, race, name = "Hunter", "Beast", "Diving Gryphon"
	mana, attack, health = 3, 4, 1
	index = "DRAGONS~Hunter~Minion~3~4~1~Beast~Diving Gryphon~Rush~Battlecry"
	requireTarget, effects, description = False, "Rush", "Rush. Battlecry: Draw a Rush minion from your deck"
	name_CN = "俯冲狮鹫"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.drawCertainCard(lambda card: card.category == "Minion" and card.effects["Rush"] > 0)
		
		
class PrimordialExplorer(Minion):
	Class, race, name = "Hunter", "Dragon", "Primordial Explorer"
	mana, attack, health = 3, 2, 3
	index = "DRAGONS~Hunter~Minion~3~2~3~Dragon~Primordial Explorer~Poisonous~Battlecry"
	requireTarget, effects, description = False, "Poisonous", "Poisonous. Battlecry: Discover a Dragon"
	name_CN = "始生龙探险者"
	poolIdentifier = "Dragons as Hunter"
	@classmethod
	def generatePool(cls, pools):
		classCards = {s : [] for s in pools.ClassesandNeutral}
		for key, value in pools.MinionswithRace["Dragon"].items():
			classCards[key.split('~')[1]].append(value)
		return ["Dragons as "+Class for Class in pools.Classes], \
				[classCards[Class]+classCards["Neutral"] for Class in pools.Classes]
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverandGenerate(PrimordialExplorer, comment, poolFunc=lambda: self.rngPool("Dragons as "+classforDiscover(self)))
		
		
class Stormhammer(Weapon):
	Class, name, description = "Hunter", "Stormhammer", "Doesn't lose Durability while you control a Dragon"
	mana, attack, durability, effects = 3, 3, 2, ""
	index = "DRAGONS~Hunter~Weapon~3~3~2~Stormhammer"
	name_CN = "风暴之锤"
	def losesDurability(self):
		if not any("Dragon" in minion.race for minion in self.Game.minionsonBoard(self.ID)):
			self.health -= 1
			
			
class Dragonbane(Minion):
	Class, race, name = "Hunter", "Mech", "Dragonbane"
	mana, attack, health = 4, 3, 5
	index = "DRAGONS~Hunter~Minion~4~3~5~Mech~Dragonbane~Legendary"
	requireTarget, effects, description = False, "", "After you use your Hero Power, deal 5 damage to a random enemy"
	name_CN = "灭龙弩炮"
	trigBoard = Trig_Dragonbane		


class Veranus(Minion):
	Class, race, name = "Hunter", "Dragon", "Veranus"
	mana, attack, health = 6, 7, 6
	index = "DRAGONS~Hunter~Minion~6~7~6~Dragon~Veranus~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: Change the Health of all enemy minions to 1"
	name_CN = "维拉努斯"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for minion in self.Game.minionsonBoard(3-self.ID):
			minion.statReset(False, 1, source=type(self))
		
		
class ArcaneBreath(Spell):
	Class, school, name = "Mage", "Arcane", "Arcane Breath"
	requireTarget, mana, effects = True, 1, ""
	index = "DRAGONS~Mage~Spell~1~~Arcane~Arcane Breath"
	description = "Deal 2 damage to a minion. If you're holding a Dragon, Discover a spell"
	name_CN = "奥术吐息"
	poolIdentifier = "Mage Spells"
	@classmethod
	def generatePool(cls, pools):
		return [Class+" Spells" for Class in pools.Classes], \
				[[value for key, value in pools.ClassCards[Class].items() if "~Spell~" in key] for Class in pools.Classes]
				
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID)
		
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard
		
	def text(self): return self.calcDamage(2)
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.dealsDamage(target, self.calcDamage(2))
			if self.Game.Hand_Deck.holdingDragon(self.ID):
				self.discoverandGenerate(ArcaneBreath, comment, poolFunc=lambda: self.rngPool(classforDiscover(self)+" Spells"))
		return target
	
		
class ElementalAllies(Quest):
	Class, school, name = "Mage", "", "Elemental Allies"
	requireTarget, mana, effects = False, 1, ""
	index = "DRAGONS~Mage~Spell~1~~Elemental Allies~~Quest"
	description = "Sidequest: Play an Elemental two turns in a row. Reward: Draw 3 spells from your deck"
	name_CN = "元素盟军"
	race, trigBoard = "Sidequest", Trig_ElementalAllies
	def questEffect(self, game, ID):
		for _ in (0, 1, 2):
			if not self.drawCertainCard(lambda card: card.category == "Spell")[0]: break


class LearnDraconic(Quest):
	Class, school, name = "Mage", "", "Learn Draconic"
	requireTarget, mana, effects = False, 1, ""
	index = "DRAGONS~Mage~Spell~1~~Learn Draconic~~Quest"
	description = "Sidequest: Spend 8 Mana on spells. Reward: Summon a 6/6 Dragon"
	name_CN = "学习龙语"
	race, trigBoard = "Sidequest", Trig_LearnDraconic
	def questEffect(self, game, ID):
		self.summon(DraconicEmissary(game, ID))


class DraconicEmissary(Minion):
	Class, race, name = "Mage", "Dragon", "Draconic Emissary"
	mana, attack, health = 6, 6, 6
	index = "DRAGONS~Mage~Minion~6~6~6~Dragon~Draconic Emissary~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "龙族使者"
	
	
class VioletSpellwing(Minion):
	Class, race, name = "Mage", "Elemental", "Violet Spellwing"
	mana, attack, health = 1, 1, 1
	index = "DRAGONS~Mage~Minion~1~1~1~Elemental~Violet Spellwing~Deathrattle"
	requireTarget, effects, description = False, "", "Deathrattle: Add an 'Arcane Missile' to your hand"
	name_CN = "紫罗兰魔翼鸦"
	deathrattle = Death_VioletSpellwing#这个奥术飞弹是属于基础卡（无标志）


class Chenvaala(Minion):
	Class, race, name = "Mage", "Elemental", "Chenvaala"
	mana, attack, health = 3, 2, 5
	index = "DRAGONS~Mage~Minion~3~2~5~Elemental~Chenvaala~Legendary"
	requireTarget, effects, description = False, "", "After you cast three spells in a turn, summon a 5/5 Elemental"
	name_CN = "齐恩瓦拉"
	trigBoard = Trig_Chenvaala		


class SnowElemental(Minion):
	Class, race, name = "Mage", "Elemental", "Snow Elemental"
	mana, attack, health = 5, 5, 5
	index = "DRAGONS~Mage~Minion~5~5~5~Elemental~Snow Elemental~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "冰雪元素"
	
	
class AzureExplorer(Minion):
	Class, race, name = "Mage", "Dragon", "Azure Explorer"
	mana, attack, health = 4, 2, 3
	index = "DRAGONS~Mage~Minion~4~2~3~Dragon~Azure Explorer~Spell Damage~Battlecry"
	requireTarget, effects, description = False, "Spell Damage_2", "Spell Damage +2. Battlecry: Discover a Dragon"
	name_CN = "碧蓝龙探险者"
	poolIdentifier = "Dragons as Mage"
	@classmethod
	def generatePool(cls, pools):
		classCards = {s : [] for s in pools.ClassesandNeutral}
		for key, value in pools.MinionswithRace["Dragon"].items():
			classCards[key.split('~')[1]].append(value)
		return ["Dragons as "+Class for Class in pools.Classes], \
				[classCards[Class]+classCards["Neutral"] for Class in pools.Classes]
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverandGenerate(AzureExplorer, comment, poolFunc=lambda: self.rngPool("Dragons as " + classforDiscover(self)))
		
		
class MalygossFrostbolt(Spell):
	Class, school, name = "Mage", "Arcane", "Malygos's Frostbolt"
	requireTarget, mana, effects = True, 0, ""
	index = "DRAGONS~Mage~Spell~0~Arcane~Malygos's Frostbolt~Legendary~Uncollectible"
	description = "Deal 3 damage to a character and Freeze it"
	name_CN = "玛里苟斯的寒冰箭"
	def text(self): return self.calcDamage(3)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.dealsDamage(target, self.calcDamage(3))
			self.freeze(target)
		return target

class MalygossMissiles(Spell):
	Class, school, name = "Mage", "Arcane", "Malygos's Missiles"
	requireTarget, mana, effects = False, 1, ""
	index = "DRAGONS~Mage~Spell~1~Arcane~Malygos's Missiles~Legendary~Uncollectible"
	description = "Deal 6 damage randomly split among all enemies"
	name_CN = "玛里苟斯的奥术飞弹"
	def text(self): return self.calcDamage(6)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		side, game = 3-self.ID, self.Game
		for _ in range(self.calcDamage(6)):
			if objs := game.charsAlive(side): self.dealsDamage(numpyChoice(objs), 1)
			else: break
		
		
class MalygossNova(Spell):
	Class, school, name = "Mage", "Frost", "Malygos's Nova"
	requireTarget, mana, effects = False, 1, ""
	index = "DRAGONS~Mage~Spell~1~Frost~Malygos's Nova~Legendary~Uncollectible"
	description = "Freeze all enemy minions"
	name_CN = "玛里苟斯的霜冻新星"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.AOE_Freeze(self.Game.minionsonBoard(3-self.ID))
		

class MalygossPolymorph(Spell):
	Class, school, name = "Mage", "Arcane", "Malygos's Polymorph"
	requireTarget, mana, effects = True, 1, ""
	index = "DRAGONS~Mage~Spell~1~Arcane~Malygos's Polymorph~Legendary~Uncollectible"
	description = "Transform a minion into a 1/1 Sheep"
	name_CN = "玛里苟斯的变形术"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: target = self.Game.transform(target, MalygossSheep(self.Game, target.ID))
		return target
		

class MalygossTome(Spell):
	Class, school, name = "Mage", "Arcane", "Malygos's Tome"
	requireTarget, mana, effects = False, 1, ""
	index = "DRAGONS~Mage~Spell~1~Arcane~Malygos's Tome~Legendary~Uncollectible"
	description = "Add 3 random Mage spells to your hand"
	name_CN = "玛里苟斯的智慧秘典"
	poolIdentifier = "Mage Spells"
	@classmethod
	def generatePool(cls, pools):
		return "Mage Spells", [value for key, value in pools.ClassCards["Mage"].items() if "~Spell~" in key]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.addCardtoHand(numpyChoice(self.rngPool("Mage Spells"), 3, replace=True), self.ID)
		

class MalygossExplosion(Spell):
	Class, school, name = "Mage", "Arcane", "Malygos's Explosion"
	requireTarget, mana, effects = False, 2, ""
	index = "DRAGONS~Mage~Spell~2~Arcane~Malygos's Explosion~Legendary~Uncollectible"
	description = "Deal 2 damage to all enemy minions"
	name_CN = "玛里苟斯的魔爆术"
	def text(self): return self.calcDamage(2)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = self.calcDamage(2)
		targets = self.Game.minionsonBoard(3-self.ID)
		self.AOE_Damage(targets, [damage]*len(targets))
		

class MalygossIntellect(Spell):
	Class, school, name = "Mage", "Arcane", "Malygos's Intellect"
	requireTarget, mana, effects = False, 3, ""
	index = "DRAGONS~Mage~Spell~3~Arcane~Malygos's Intellect~Legendary~Uncollectible"
	description = "Draw 4 cards"
	name_CN = "玛里苟斯的奥术智慧"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for i in (0, 1, 2, 3): self.Game.Hand_Deck.drawCard(self.ID)
		

class MalygossFireball(Spell):
	Class, school, name = "Mage", "Fire", "Malygos's Fireball"
	requireTarget, mana, effects = True, 4, ""
	index = "DRAGONS~Mage~Spell~4~Fire~Malygos's Fireball~Legendary~Uncollectible"
	description = "Deal 8 damage"
	name_CN = "玛里苟斯的火球术"
	def text(self): return self.calcDamage(8)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.dealsDamage(target, self.calcDamage(8))
		return target
		

class MalygossFlamestrike(Spell):
	Class, school, name = "Mage", "Fire", "Malygos's Flamestrike"
	requireTarget, mana, effects = False, 7, ""
	index = "DRAGONS~Mage~Spell~7~Fire~Malygos's Flamestrike~Legendary~Uncollectible"
	description = "Deal 8 damage to all enemy minions"
	name_CN = "玛里苟斯的烈焰风暴"
	def text(self): return self.calcDamage(8)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = self.calcDamage(8)
		targets = self.Game.minionsonBoard(3-self.ID)
		self.AOE_Damage(targets, [damage]*len(targets))
		

class MalygossSheep(Minion):
	Class, race, name = "Mage", "Beast", "Malygos's Sheep"
	mana, attack, health = 1, 1, 1
	index = "DRAGONS~Mage~Minion~1~1~1~Beast~Malygos's Sheep~Legendary~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "玛里苟斯的绵羊"
	

MalygosUpgradedSpells = [MalygossFrostbolt, MalygossMissiles, MalygossNova, MalygossPolymorph, MalygossTome,
						MalygossExplosion, MalygossIntellect, MalygossFireball, MalygossFlamestrike
						]

class MalygosAspectofMagic(Minion):
	Class, race, name = "Mage", "Dragon", "Malygos, Aspect of Magic"
	mana, attack, health = 5, 2, 8
	index = "DRAGONS~Mage~Minion~5~2~8~Dragon~Malygos, Aspect of Magic~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: If you're holding a Dragon, Discover an upgraded Mage spell"
	name_CN = "织法巨龙玛里苟斯"
	
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID, self)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Hand_Deck.holdingDragon(self.ID):
			self.discoverandGenerate(MalygosAspectofMagic, comment, poolFunc=lambda: MalygosUpgradedSpells)
	
		
#火球滚滚会越过休眠物。直接打在相隔的其他随从上。圣盾随从会分担等于自己当前生命值的伤害。


#火球滚滚会越过休眠物。直接打在相隔的其他随从上。圣盾随从会分担等于自己当前生命值的伤害。
class RollingFireball(Spell):
	Class, school, name = "Mage", "Fire", "Rolling Fireball"
	requireTarget, mana, effects = True, 5, ""
	index = "DRAGONS~Mage~Spell~5~Fire~Rolling Fireball"
	description = "Deal 8 damage to a minion. Any excess damage continues to the left or right"
	name_CN = "火球滚滚"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard
		
	def text(self): return self.calcDamage(8)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = self.calcDamage(8)
			game = self.Game
			minion, direction, damageleft = None, "", damage
			damageDealt = min(target.health, damageleft) if target.health > 0 else 0
			damageleft -= damageDealt
			#火球滚滚打到牌库中的随从是没有任何后续效果的。不知道目标随从提前死亡的话会如何
			if target.onBoard:
				neighbors, dist = game.neighbors2(target, True) #对目标进行伤害之后，在场上寻找其相邻随从，决定滚动方向。
				#direction = 1 means fireball rolls right, direction = 1 is left
				if dist == 1:
					ran = numpyRandint(2) #ran == 1: roll right, 0: roll left
					minion, direction = neighbors[ran], ran
				elif dist < 0: minion, direction = neighbors[0], 0
				elif dist == 2: minion, direction = neighbors[0], 1
			else: #如果可以在手牌中找到那个随从时
				#火球滚滚打到手牌中的随从时，会判断目前那个随从在手牌中位置，如果在从左数第3张的话，那么会将过量伤害传递给场上的2号或者4号随从。
				try: i = game.Hand_Deck.hands[target.ID].index(target)
				except: i = -1
				if i > -1:
					minions = game.minionsonBoard(3-self.ID) #对手牌中的随从进行伤害之后，寻找场上合适的随从并确定滚动方向。
					if minions:
						if i == 0: minion, direction = minions[1] if len(minions) > 1 else None, 1
						elif i + 1 < len(minions): #手牌中第4张（编号3），如果场上有5张随从，仍然随机
							if numpyRandint(2): minion, direction = minions[i+1], 1
							else: minion, direction = minions[i-1], 0
						#如果随从在手牌中的编号很大，如手牌中第5张（编号4），则如果场上有5张或者以下随从，则都会向左滚
						else: minion, direction = minions[-1], 0
			self.dealsDamage(target, damageDealt)
			#当已经决定了要往哪个方向走之后
			while minion and damageleft > 0: #如果下个随从不存在或者没有剩余伤害则停止循环
				if minion.category == "Minion":
					damageDealt = min(minion.health, damageleft) if minion.health > 0 else 0
					self.dealsDamage(minion, damageDealt)
				else: damageDealt = 0 #休眠物可以被直接跳过，伤害为0
				damageleft -= damageDealt
				neighbors, dist = game.neighbors2(minion, True)
				if direction: #roll towards right
					minion = neighbors[2-dist] if dist > 0 else None
				else:
					minion = neighbors[0] if dist == 1 or dist == -1 else None
		return target
		
		
class Dragoncaster(Minion):
	Class, race, name = "Mage", "", "Dragoncaster"
	mana, attack, health = 7, 4, 4
	index = "DRAGONS~Mage~Minion~7~4~4~~Dragoncaster~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: If you're holding a Dragon, your next spell this turn costs (0)"
	name_CN = "乘龙法师"
	
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Hand_Deck.holdingDragon(self.ID):
			GameManaAura_Dragoncaster(self.Game, self.ID).auraAppears()
		

class ManaGiant(Minion):
	Class, race, name = "Mage", "Elemental", "Mana Giant"
	mana, attack, health = 8, 8, 8
	index = "DRAGONS~Mage~Minion~8~8~8~Elemental~Mana Giant"
	requireTarget, effects, description = False, "", "Costs (1) less for each card you've played this game that didn't start in your deck"
	name_CN = "法力巨人"
	trigHand = Trig_ManaGiant
	def selfManaChange(self):
		if self.inHand:
			self.mana -= self.Game.Counters.createdCardsPlayedThisGame[self.ID]
			self.mana = max(self.mana, 0)
			

class RighteousCause(Quest):
	Class, school, name = "Paladin", "", "Righteous Cause"
	requireTarget, mana, effects = False, 1, ""
	index = "DRAGONS~Paladin~Spell~1~~Righteous Cause~~Quest"
	description = "Sidequest: Summon 5 minions. Reward: Give your minions +1/+1"
	name_CN = "正义感召"
	race, trigBoard = "Sidequest", Trig_RighteousCause
	def questEffect(self, game, ID):
		self.AOE_GiveEnchant(self.Game.minionsonBoard(self.ID), 1, 1, name=RighteousCause)
		

class SandBreath(Spell):
	Class, school, name = "Paladin", "", "Sand Breath"
	requireTarget, mana, effects = True, 1, ""
	index = "DRAGONS~Paladin~Spell~1~~Sand Breath"
	description = "Give a minion +1/+2. Give it Divine Shield if you're holding a Dragon"
	name_CN = "沙尘吐息"
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID)
		
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.giveEnchant(target, 1, 2, effGain="Divine Shield" if self.Game.Hand_Deck.holdingDragon(self.ID) else '',
									name=SandBreath)
		return target	
		
		
class Sanctuary(Quest):
	Class, school, name = "Paladin", "", "Sanctuary"
	requireTarget, mana, effects = False, 2, ""
	index = "DRAGONS~Paladin~Spell~2~~Sanctuary~~Quest"
	description = "Sidequest: Take no damage for a turn. Reward: Summon a 3/6 minion with Taunt"
	name_CN = "庇护"
	race, trigBoard = "Sidequest", Trig_Sanctuary
	def questEffect(self, game, ID):
		self.summon(IndomitableChampion(game, ID))


class IndomitableChampion(Minion):
	Class, race, name = "Paladin", "", "Indomitable Champion"
	mana, attack, health = 4, 3, 6
	index = "DRAGONS~Paladin~Minion~4~3~6~~Indomitable Champion~Taunt~Uncollectible"
	requireTarget, effects, description = False, "Taunt", "Taunt"
	name_CN = "不屈的勇士"
	
	
class BronzeExplorer(Minion):
	Class, race, name = "Paladin", "Dragon", "Bronze Explorer"
	mana, attack, health = 3, 2, 3
	index = "DRAGONS~Paladin~Minion~3~2~3~Dragon~Bronze Explorer~Lifesteal~Battlecry"
	requireTarget, effects, description = False, "Lifesteal", "Lifesteal. Battlecry: Discover a Dragon"
	name_CN = "青铜龙探险者"
	poolIdentifier = "Dragons as Paladin"
	@classmethod
	def generatePool(cls, pools):
		classCards = {s : [] for s in pools.ClassesandNeutral}
		for key, value in pools.MinionswithRace["Dragon"].items():
			classCards[key.split('~')[1]].append(value)
		return ["Dragons as "+Class for Class in pools.Classes], \
				[classCards[Class]+classCards["Neutral"] for Class in pools.Classes]
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverandGenerate(ChromaticEgg, comment, poolFunc=lambda: self.rngPool("Dragons as "+classforDiscover(self)))
		

class SkyClaw(Minion):
	Class, race, name = "Paladin", "Mech", "Sky Claw"
	mana, attack, health = 3, 1, 2
	index = "DRAGONS~Paladin~Minion~3~1~2~Mech~Sky Claw~Battlecry"
	requireTarget, effects, description = False, "", "Your other Mechs have +1 Attack. Battlecry: Summon two 1/1 Microcopters"
	name_CN = "空中飞爪"
	aura = Aura_SkyClaw
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon([Microcopter(self.Game, self.ID) for _ in (0, 1)], relative="<>")
		

class Microcopter(Minion):
	Class, race, name = "Paladin", "Mech", "Microcopter"
	mana, attack, health = 1, 1, 1
	index = "DRAGONS~Paladin~Minion~1~1~1~Mech~Microcopter~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "微型旋翼机"
	
	
class DragonriderTalritha(Minion):
	Class, race, name = "Paladin", "", "Dragonrider Talritha"
	mana, attack, health = 3, 3, 3
	index = "DRAGONS~Paladin~Minion~3~3~3~~Dragonrider Talritha~Deathrattle~Legendary"
	requireTarget, effects, description = False, "", "Deathrattle: Give a Dragon in your hand +3/+3 and this Deathrattle"
	name_CN = "龙骑士塔瑞萨"
	deathrattle = Death_DragonriderTalritha


class LightforgedZealot(Minion):
	Class, race, name = "Paladin", "", "Lightforged Zealot"
	mana, attack, health = 4, 4, 2
	index = "DRAGONS~Paladin~Minion~4~4~2~~Lightforged Zealot~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: If your deck has no Neutral cards, equip a 4/2 Truesilver Champion"
	name_CN = "光铸狂热者"
	
	def effCanTrig(self):
		self.effectViable = all(card.Class != "Neutral" for card in self.Game.Hand_Deck.decks[self.ID])
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if all(card.Class != "Neutral" for card in self.Game.Hand_Deck.decks[self.ID]):
			self.equipWeapon(TruesilverChampion(self.Game, self.ID))
		
		
class NozdormutheTimeless(Minion):
	Class, race, name = "Paladin", "Dragon", "Nozdormu the Timeless"
	mana, attack, health = 4, 8, 8
	index = "DRAGONS~Paladin~Minion~4~8~8~Dragon~Nozdormu the Timeless~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: Set each player to 10 Mana Crystals"
	name_CN = "时光巨龙诺兹多姆"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.Manas.setManaCrystal(10, 1)
		self.Game.Manas.setManaCrystal(10, 2)
		
		
class AmberWatcher(Minion):
	Class, race, name = "Paladin", "Dragon", "Amber Watcher"
	mana, attack, health = 5, 4, 6
	index = "DRAGONS~Paladin~Minion~5~4~6~Dragon~Amber Watcher~Battlecry"
	requireTarget, effects, description = True, "", "Battlecry: Restore 8 Health"
	name_CN = "琥珀看守者"
	def text(self): return self.calcHeal(8)
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.restoresHealth(target, self.calcHeal(8))
		return target
		
		
class LightforgedCrusader(Minion):
	Class, race, name = "Paladin", "", "Lightforged Crusader"
	mana, attack, health = 7, 7, 7
	index = "DRAGONS~Paladin~Minion~7~7~7~~Lightforged Crusader~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: If your deck has no Neutral cards, add 5 random Paladin cards to your hand"
	name_CN = "光铸远征军"
	poolIdentifier = "Paladin Cards"
	@classmethod
	def generatePool(cls, pools):
		return "Paladin Cards", list(pools.ClassCards["Paladin"].values())
		
	def effCanTrig(self):
		self.effectViable = True
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if card.Class == "Neutral":
				self.effectViable = False
				break
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if all(card.Class != "Neutral" for card in self.Game.Hand_Deck.decks[self.ID]):
			self.addCardtoHand(numpyChoice(self.rngPool("Paladin Cards"), 5, replace=True), self.ID)
		
		
class WhispersofEVIL(Spell):
	Class, school, name = "Priest", "", "Whispers of EVIL"
	requireTarget, mana, effects = False, 0, ""
	index = "DRAGONS~Priest~Spell~0~~Whispers of EVIL"
	description = "Add a Lackey to your hand"
	name_CN = "怪盗低语"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.addCardtoHand(numpyChoice(Lackeys), self.ID)
		
		
class DiscipleofGalakrond(Minion):
	Class, race, name = "Priest", "", "Disciple of Galakrond"
	mana, attack, health = 1, 1, 2
	index = "DRAGONS~Priest~Minion~1~1~2~~Disciple of Galakrond~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Invoke Galakrond"
	name_CN = "迦拉克隆的信徒"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		invokeGalakrond(self.Game, self.ID)
		
		
class EnvoyofLazul(Minion):
	Class, race, name = "Priest", "", "Envoy of Lazul"
	mana, attack, health = 2, 2, 2
	index = "DRAGONS~Priest~Minion~2~2~2~~Envoy of Lazul~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Look at 3 cards. Guess which one is in your opponent's hand to get a copy of it"
	name_CN = "拉祖尔的信使"
	
	#One card current in opponent's hand( can be created card). Two other cards are the ones currently in opponent's deck but not in hand.
	#If less than two cards left in opponent's deck, two copies of cards in opponent's starting deck is given.
	
					
class BreathoftheInfinite(Spell):
	Class, school, name = "Priest", "", "Breath of the Infinite"
	requireTarget, mana, effects = False, 3, ""
	index = "DRAGONS~Priest~Spell~3~~Breath of the Infinite"
	description = "Deal 2 damage to all minions. If you're holding a Dragon, only damage enemies"
	name_CN = "永恒吐息"
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID)
		
	def text(self): return self.calcDamage(2)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = self.calcDamage(2)
		if self.Game.Hand_Deck.holdingDragon(self.ID): targets = self.Game.minionsonBoard(3-self.ID)
		else: targets = self.Game.minionsonBoard(self.ID) + self.Game.minionsonBoard(3-self.ID)
		self.AOE_Damage(targets, [damage for minion in targets])
		
		
class MindflayerKaahrj(Minion):
	Class, race, name = "Priest", "", "Mindflayer Kaahrj"
	mana, attack, health = 3, 3, 3
	index = "DRAGONS~Priest~Minion~3~3~3~~Mindflayer Kaahrj~Battlecry~Deathrattle~Legendary"
	requireTarget, effects, description = True, "", "Battlecry: Choose an enemy minion. Deathrattle: Summon a new copy of it"
	name_CN = "夺心者卡什"
	deathrattle = Death_MindflayerKaahrj
	def targetExists(self, choice=0):
		return self.selectableEnemyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.ID != self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			for trig in self.deathrattles:
				if isinstance(trig, Death_MindflayerKaahrj): trig.savedObj = type(target)
		return target
		

class FateWeaver(Minion):
	Class, race, name = "Priest", "Dragon", "Fate Weaver"
	mana, attack, health = 4, 3, 6
	index = "DRAGONS~Priest~Minion~4~3~6~Dragon~Fate Weaver~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: If you've Invoked twice, reduce the Cost of cards in your hand by (1)"
	name_CN = "命运编织者"
	
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.invokes[self.ID] > 1
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Counters.invokes[self.ID] > 1:
			for card in self.Game.Hand_Deck.hands[self.ID]:
				ManaMod(card, by=-1).applies()
			self.Game.Manas.calcMana_All()
		
		
class GraveRune(Spell):
	Class, school, name = "Priest", "Shadow", "Grave Rune"
	requireTarget, mana, effects = True, 4, ""
	index = "DRAGONS~Priest~Spell~4~Shadow~Grave Rune"
	description = "Give a minion 'Deathrattle: Summon 2 copies of this'"
	name_CN = "墓地符文"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.giveEnchant(target, trig=Death_GraveRune, trigType="Deathrattle", connect=target.onBoard)
		return target
		

class Chronobreaker(Minion):
	Class, race, name = "Priest", "Dragon", "Chronobreaker"
	mana, attack, health = 5, 4, 5
	index = "DRAGONS~Priest~Minion~5~4~5~Dragon~Chronobreaker~Deathrattle"
	requireTarget, effects, description = False, "", "Deathrattle: If you're holding a Dragon, deal 3 damage to all enemy minions"
	name_CN = "时空破坏者"
	deathrattle = Death_Chronobreaker


class TimeRip(Spell):
	Class, school, name = "Priest", "", "Time Rip"
	requireTarget, mana, effects = True, 5, ""
	index = "DRAGONS~Priest~Spell~5~~Time Rip"
	description = "Destroy a minion. Invoke Galakrond"
	name_CN = "时空裂痕"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			if target.onBoard: target.dead = True
			elif target.inHand: self.Game.Hand_Deck.discard(target) #如果随从在手牌中则将其丢弃
		invokeGalakrond(self.Game, self.ID)
		return target
		
		
#加基森的三职业卡可以被迦拉克隆生成。


#加基森的三职业卡可以被迦拉克隆生成。
class GalakrondsWit(Power):
	mana, name, requireTarget = 2, "Galakrond's Wit", False
	index = "Priest~Hero Power~2~Galakrond's Wit"
	description = "Add a random Priest minion to your hand"
	name_CN = "迦拉克隆的智识"
	def available(self, choice=0):
		return not (self.chancesUsedUp() or self.Game.Hand_Deck.handNotFull(self.ID))
		
	def effect(self, target=None, choice=0, comment=''):
		self.addCardtoHand(numpyChoice(self.rngPool("Priest Minions")), self.ID)
		return 0
		
		
class GalakrondtheUnspeakable(Galakrond_Hero):
	mana, weapon, description = 7, None, "Battlecry: Destroy a random enemy minion. (Invoke twice to upgrade)"
	Class, name, heroPower, health, armor = "Priest", "Galakrond, the Unspeakable", GalakrondsWit, 30, 5
	index = "DRAGONS~Priest~Hero Card~7~Galakrond, the Unspeakable~Battlecry~Legendary"
	name_CN = "讳言巨龙迦拉克隆"
	poolIdentifier = "Priest Minions"
	@classmethod
	def generatePool(cls, pools):
		return "Priest Minions", [value for key, value in pools.ClassCards["Priest"].items() if "~Minion~" in key]
		
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.upgradedGalakrond = GalakrondtheApocalypes_Priest
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		minions = self.Game.minionsAlive(3-self.ID)
		if minions: self.Game.killMinion(self, numpyChoice(minions))
		
		
class GalakrondtheApocalypes_Priest(Galakrond_Hero):
	mana, weapon, description = 7, None, "Battlecry: Destroy 2 random enemy minions. (Invoke twice to upgrade)"
	Class, name, heroPower, health, armor = "Priest", "Galakrond, the Apocalypes", GalakrondsWit, 30, 5
	index = "DRAGONS~Priest~Hero Card~7~Galakrond, the Apocalypes~Battlecry~Legendary~Uncollectible"
	name_CN = "天降浩劫迦拉克隆"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.upgradedGalakrond = GalakrondAzerothsEnd_Priest
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		minions = self.Game.minionsAlive(3 - self.ID)
		if minions:
			targets = numpyChoice(minions, min(2, len(minions)), replace=False)
			self.Game.killMinion(self, targets)
		
	
class GalakrondAzerothsEnd_Priest(Galakrond_Hero):
	mana, weapon, description = 7, None, "Battlecry: Destroy 4 random enemy minions. Equip a 5/2 Claw"
	Class, name, heroPower, health, armor = "Priest", "Galakrond, Azeroth's End", GalakrondsWit, 30, 5
	index = "DRAGONS~Priest~Hero Card~7~Galakrond, Azeroth's End~Battlecry~Legendary~Uncollectible"
	name_CN = "世界末日迦拉克隆"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.upgradedGalakrond = None
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		minions = self.Game.minionsAlive(3 - self.ID)
		if minions:
			targets = numpyChoice(minions, min(4, len(minions)), replace=False)
			self.Game.killMinion(self, targets)
		self.equipWeapon(DragonClaw(self.Game, self.ID))
		

class DragonClaw(Weapon):
	Class, name, description = "Neutral", "Dragon Claw", ""
	mana, attack, durability, effects = 5, 5, 2, ""
	index = "DRAGONS~Neutral~Weapon~5~5~2~Dragon Claw~Uncollectible"
	name_CN = "巨龙之爪"
	
#施放顺序是随机的。在姆诺兹多死亡之后，依然可以进行施放。如果姆诺兹多被对方控制，则改为施放我方上回合打出的牌。
#https://www.bilibili.com/video/av87286050?from=search&seid=5979238121000536259
#当我方拥有Choose Both光环的时候，复制对方打出的单个抉择的随从和法术： 随从仍然是单个抉择的结果，但是法术是拥有全选效果的。
#如果对方打出了全选抉择的随从，但是我方没有Choose Both光环，那么我方复制会得到全抉择的随从，而法术则是随机抉择。
#与苔丝的效果类似，对于随从是直接复制其打出结果。
#姆诺兹多的战吼没有打出牌的张数的限制。
#无法复制被法反掉的法术，因为那个法术不算作对方打出过的牌（被直接取消）。
#打出一个元素被对方的变形药水奥秘变形为绵羊后，下个回合仍然可以触发元素链。说明打出一张牌人记录是在最终“打出一张随从后”扳机结算前
#同时姆诺兹多能复制抉择变形随从的变形目标说明打出随从牌的记录是在战吼/抉择等之后。


#施放顺序是随机的。在姆诺兹多死亡之后，依然可以进行施放。如果姆诺兹多被对方控制，则改为施放我方上回合打出的牌。
#https://www.bilibili.com/video/av87286050?from=search&seid=5979238121000536259
#当我方拥有Choose Both光环的时候，复制对方打出的单个抉择的随从和法术： 随从仍然是单个抉择的结果，但是法术是拥有全选效果的。
#如果对方打出了全选抉择的随从，但是我方没有Choose Both光环，那么我方复制会得到全抉择的随从，而法术则是随机抉择。
#与苔丝的效果类似，对于随从是直接复制其打出结果。
#姆诺兹多的战吼没有打出牌的张数的限制。
#无法复制被法反掉的法术，因为那个法术不算作对方打出过的牌（被直接取消）。
#打出一个元素被对方的变形药水奥秘变形为绵羊后，下个回合仍然可以触发元素链。说明打出一张牌人记录是在最终“打出一张随从后”扳机结算前
#同时姆诺兹多能复制抉择变形随从的变形目标说明打出随从牌的记录是在战吼/抉择等之后。
class MurozondtheInfinite(Minion):
	Class, race, name = "Priest", "Dragon", "Murozond the Infinite"
	mana, attack, health = 8, 8, 8
	index = "DRAGONS~Priest~Minion~8~8~8~Dragon~Murozond the Infinite~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: Play all cards your opponent played last turn"
	name_CN = "永恒巨龙姆诺兹多"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		game = self.Game
		cardsEachTurn_Players = game.Counters.cardsPlayedLastTurn
		curTurn = game.turn
		cardstoReplay = {curTurn: cardsEachTurn_Players[curTurn][-2][:] if len(cardsEachTurn_Players[curTurn]) > 1 else [],
						3-curTurn: cardsEachTurn_Players[3-curTurn][-1][:] if cardsEachTurn_Players[3-curTurn] else []}
		numpyShuffle(cardstoReplay[1])
		numpyShuffle(cardstoReplay[2])
		#应该是每当打出一张卡后将index从原有列表中移除。
		while cardstoReplay[3-self.ID]:
			card = cardstoReplay[3-self.ID].pop()(game, self.ID)
			if card.category == "Minion": self.summon(card)
			elif card.category == "Spell": card.cast()
			elif card.category == "Weapon": self.equipWeapon(card)
			else: #Hero cards. And the HeroClass will change accordingly
				#Replaying Hero Cards can only replace your hero and Hero Power, no battlecry will be triggered
				card.replaceHero(fromHeroCard=True)
			game.gathertheDead(decideWinner=True)
		

class BloodsailFlybooter(Minion):
	Class, race, name = "Rogue", "Pirate", "Bloodsail Flybooter"
	mana, attack, health = 1, 1, 1
	index = "DRAGONS~Rogue~Minion~1~1~1~Pirate~Bloodsail Flybooter~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Add two 1/1 Pirates to your hand"
	name_CN = "血帆飞贼"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.addCardtoHand([SkyPirate, SkyPirate], self.ID)
		
class SkyPirate(Minion):
	Class, race, name = "Rogue", "Pirate", "Sky Pirate"
	mana, attack, health = 1, 1, 1
	index = "DRAGONS~Rogue~Minion~1~1~1~Pirate~Sky Pirate~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "空中海盗"
	
	
class DragonsHoard(Spell):
	Class, school, name = "Rogue", "", "Dragon's Hoard"
	requireTarget, mana, effects = False, 1, ""
	index = "DRAGONS~Rogue~Spell~1~~Dragon's Hoard"
	description = "Discover a Legendary minion from another class"
	name_CN = "巨龙宝藏"
	poolIdentifier = "Druid Legendary Minions"
	@classmethod
	def generatePool(cls, pools):
		return ["%s Legendary Minions"%Class for Class in pools.Classes], \
				[[value for key, value in pools.ClassCards[Class].items() if "~Minion~" in key and "~Legendary" in key] for Class in pools.Classes]
				
	def decideLegendaryPool(self):
		heroClass = self.Game.heroes[self.ID].Class
		classes = [Class for Class in self.rngPool("Classes") if Class != heroClass]
		Class = classes[datetime.now().microsecond % len(classes)]
		return self.rngPool(Class+" Legendary Minions")
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverandGenerate(DragonsHoard, comment, poolFunc=lambda : DragonsHoard.decideLegendaryPool(self))
		
		
class PraiseGalakrond(Spell):
	Class, school, name = "Rogue", "", "Praise Galakrond!"
	requireTarget, mana, effects = True, 1, ""
	index = "DRAGONS~Rogue~Spell~1~~Praise Galakrond!"
	description = "Give a minion +1 Attack. Invoke Galakrond"
	name_CN = "赞美迦拉克隆"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.giveEnchant(target, 1, 0, name=PraiseGalakrond)
			invokeGalakrond(self.Game, self.ID)
		return target
		
		
class SealFate(Spell):
	Class, school, name = "Rogue", "", "Seal Fate"
	requireTarget, mana, effects = True, 3, ""
	index = "DRAGONS~Rogue~Spell~3~~Seal Fate"
	description = "Deal 3 damage to an undamaged character. Invoke Galakrond"
	name_CN = "封印命运"
	def text(self): return self.calcDamage(3)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.dealsDamage(target, self.calcDamage(3))
			invokeGalakrond(self.Game, self.ID)
		return target
		
		
class UmbralSkulker(Minion):
	Class, race, name = "Rogue", "", "Umbral Skulker"
	mana, attack, health = 4, 3, 3
	index = "DRAGONS~Rogue~Minion~4~3~3~~Umbral Skulker~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: If you've Invoked twice, add 3 Coins to your hand"
	name_CN = "幽影潜藏者"
	
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.invokes[self.ID] > 1
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Counters.invokes[self.ID] > 1: self.addCardtoHand([TheCoin, TheCoin, TheCoin], self.ID)
		
		
class NecriumApothecary(Minion):
	Class, race, name = "Rogue", "", "Necrium Apothecary"
	mana, attack, health = 5, 2, 5
	index = "DRAGONS~Rogue~Minion~5~2~5~~Necrium Apothecary~Combo"
	requireTarget, effects, description = False, "", "Combo: Draw a Deathrattle minion from your deck and gain its Deathrattle"
	name_CN = "死金药剂师"
	
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0:
			if card := self.drawCertainCard(lambda card: card.category == "Minion")[0]:
				self.giveEnchant(self, trigs=(type(trig) for trig in card.deathrattles), trigType="Deathrattle", connect=self.onBoard)
		
		
class Stowaway(Minion):
	Class, race, name = "Rogue", "", "Stowaway"
	mana, attack, health = 5, 4, 4
	index = "DRAGONS~Rogue~Minion~5~4~4~~Stowaway~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: If there are cards in your deck that didn't start there, draw 2 of them"
	name_CN = "偷渡者"
	def effCanTrig(self):
		return any(card.creator for card in self.Game.Hand_Deck.decks[self.ID])
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for _ in (0, 1):
			if not self.drawCertainCard(lambda card: card.creator)[0]: break
		
		
class Waxadred(Minion):
	Class, race, name = "Rogue", "Dragon", "Waxadred"
	mana, attack, health = 5, 7, 5
	index = "DRAGONS~Rogue~Minion~5~7~5~Dragon~Waxadred~Deathrattle~Legendary"
	requireTarget, effects, description = False, "", "Deathrattle: Shuffle a Candle into your deck that resummons Waxadred when drawn"
	name_CN = "蜡烛巨龙"
	deathrattle = Death_Waxadred


class WaxadredsCandle(Spell):
	Class, school, name = "Rogue", "", "Waxadred's Candle"
	requireTarget, mana, effects = False, 5, ""
	index = "DRAGONS~Rogue~Spell~5~~Waxadred's Candle~Casts When Drawn~Uncollectible"
	description = "Casts When Drawn. Summon Waxadred"
	name_CN = "巨龙的蜡烛"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon(Waxadred(self.Game, self.ID))
		
		
class CandleBreath(Spell):
	Class, school, name = "Rogue", "Fire", "Candle Breath"
	requireTarget, mana, effects = False, 6, ""
	index = "DRAGONS~Rogue~Spell~6~Fire~Candle Breath"
	description = "Draw 3 cards. Costs (3) less while you're holding a Dragon"
	name_CN = "烛火吐息"
	trigHand = Trig_CandleBreath
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID)
		
	def selfManaChange(self):
		if self.inHand and self.Game.Hand_Deck.holdingDragon(self.ID):
			self.mana -= 3
			self.mana = max(0, self.mana)
			
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for _ in (0, 1, 2): self.Game.Hand_Deck.drawCard(self.ID)
		

class FlikSkyshiv(Minion):
	Class, race, name = "Rogue", "", "Flik Skyshiv"
	mana, attack, health = 6, 4, 4
	index = "DRAGONS~Rogue~Minion~6~4~4~~Flik Skyshiv~Battlecry~Legendary"
	requireTarget, effects, description = True, "", "Battlecry: Destroy a minion and all copies of it (wherever they are)"
	name_CN = "菲里克·飞刺"
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target != self and target.onBoard
		
	#飞刺的战吼会摧毁所有同名卡，即使有些不是随从，如法师的扰咒术奥秘和随从，镜像法术和其衍生物
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			HD = self.Game.Hand_Deck
			for ID in (1, 2):
				for minion in self.Game.minionsonBoard(ID):
					if minion.name == target.name: minion.dead = True
				for i in reversed(range(len(HD.decks[ID]))):
					if HD.decks[ID][i].name == target.name: HD.extractfromDeck(i, ID)
				for i in reversed(range(len(HD.hands[ID]))):
					if HD.hands[ID][i].name == target.name: HD.extractfromHand(i, ID, enemyCanSee=True)
		return target
		
		
class GalakrondsGuile(Power):
	mana, name, requireTarget = 2, "Galakrond's Guile", False
	index = "Rogue~Hero Power~2~Galakrond's Guile"
	description = "Add a Lackey to your hand"
	name_CN = "迦拉克隆的诡计"
	def available(self, choice=0):
		return not (self.chancesUsedUp() or self.Game.Hand_Deck.handNotFull(self.ID))
				
	def effect(self, target=None, choice=0, comment=''):
		self.addCardtoHand(numpyChoice(Lackeys), self.ID)
		return 0
		
class GalakrondtheNightmare(Galakrond_Hero):
	mana, weapon, description = 7, None, "Battlecry: Draw a card. It costs (1). (Invoke twice to upgrade)"
	Class, name, heroPower, health, armor = "Rogue", "Galakrond, the Nightmare", GalakrondsGuile, 30, 5
	index = "DRAGONS~Rogue~Hero Card~7~Galakrond, the Nightmare~Battlecry~Legendary"
	name_CN = "梦魇巨龙迦拉克隆"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.upgradedGalakrond = GalakrondtheApocalypes_Rogue
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		card, mana, entersHand = self.Game.Hand_Deck.drawCard(self.ID)
		if entersHand: ManaMod(card, to=1).applies()
		
class GalakrondtheApocalypes_Rogue(Galakrond_Hero):
	mana, weapon, description = 7, None, "Battlecry: Draw 2 cards. They cost (1). (Invoke twice to upgrade)"
	Class, name, heroPower, health, armor = "Rogue", "Galakrond, the Apocalypes", GalakrondsGuile, 30, 5
	index = "DRAGONS~Rogue~Hero Card~7~Galakrond, the Apocalypes~Battlecry~Legendary~Uncollectible"
	name_CN = "天降浩劫迦拉克隆"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.upgradedGalakrond = GalakrondAzerothsEnd_Rogue
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for _ in (0, 1):
			card, mana, entersHand = self.Game.Hand_Deck.drawCard(self.ID)
			if entersHand: ManaMod(card, to=1).applies()
			
class GalakrondAzerothsEnd_Rogue(Galakrond_Hero):
	mana, weapon, description = 7, None, "Battlecry: Draw 4 cards. They cost (1). Equip a 5/2 Claw"
	Class, name, heroPower, health, armor = "Rogue", "Galakrond, Azeroth's End", GalakrondsGuile, 30, 5
	index = "DRAGONS~Rogue~Hero Card~7~Galakrond, Azeroth's End~Battlecry~Legendary~Uncollectible"
	name_CN = "世界末日迦拉克隆"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.upgradedGalakrond = None
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for i in (0, 1, 2, 3):
			card, mana, entersHand = self.Game.Hand_Deck.drawCard(self.ID)
			if entersHand: ManaMod(card, to=1).applies()
		self.equipWeapon(DragonClaw(self.Game, self.ID))
		

class InvocationofFrost(Spell):
	Class, school, name = "Shaman", "Frost", "Invocation of Frost"
	requireTarget, mana, effects = True, 2, ""
	index = "DRAGONS~Shaman~Spell~2~Frost~Invocation of Frost"
	description = "Freeze a minion. Invoke Galakrond"
	name_CN = "霜之祈咒"
	def available(self):
		return self.selectableEnemyExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" or target.category == "Hero" and target.onBoard and target.ID != self.ID
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.freeze(target)
			invokeGalakrond(self.Game, self.ID)
		return target


class SurgingTempest(Minion):
	Class, race, name = "Shaman", "Elemental", "Surging Tempest"
	mana, attack, health = 1, 1, 3
	index = "DRAGONS~Shaman~Minion~1~1~3~Elemental~Surging Tempest"
	requireTarget, effects, description = False, "", "Has +1 Attack while you have Overloaded Mana Crystals"
	name_CN = "电涌风暴"
	trigBoard = Trig_SurgingTempest
	def statCheckResponse(self):
		if self.onBoard and not self.silenced and \
				(self.Game.Manas.manasOverloaded[self.ID] > 0 or self.Game.Manas.manasLocked[self.ID] > 0):
			self.attack += 1

			
class Squallhunter(Minion):
	Class, race, name = "Shaman", "Dragon", "Squallhunter"
	mana, attack, health = 4, 5, 7
	index = "DRAGONS~Shaman~Minion~4~5~7~Dragon~Squallhunter~Spell Damage~Overload"
	requireTarget, effects, description = False, "Spell Damage_2", "Spell Damage +2, Overload: (2)"
	name_CN = "猎风巨龙"
	overload = 2
	
	
class StormsWrath(Spell):
	Class, school, name = "Shaman", "Nature", "Storm's Wrath"
	requireTarget, mana, effects = False, 1, ""
	index = "DRAGONS~Shaman~Spell~1~Nature~Storm's Wrath~Overload"
	description = "Give your minions +1/+1. Overload: (1)"
	name_CN = "风暴之怒"
	overload = 2
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.AOE_GiveEnchant(self.Game.minionsonBoard(self.ID), 1, 1, name=StormsWrath)
		
		
class LightningBreath(Spell):
	Class, school, name = "Shaman", "Nature", "Lightning Breath"
	requireTarget, mana, effects = True, 3, ""
	index = "DRAGONS~Shaman~Spell~3~Nature~Lightning Breath"
	description = "Deal 4 damage to a minion. If you're holding a Dragon, also damage its neighbors"
	name_CN = "闪电吐息"
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID)
		
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard
		
	def text(self): return self.calcDamage(4)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = self.calcDamage(4)
			if target.onBoard and self.Game.Hand_Deck.holdingDragon(self.ID) and self.Game.neighbors2(target)[0] != []:
				targets = [target] + self.Game.neighbors2(target)[0]
				self.AOE_Damage(targets, [damage for minion in targets])
			else: self.dealsDamage(target, damage)
		return target
		
		
class Bandersmosh(Minion):
	Class, race, name = "Shaman", "", "Bandersmosh"
	mana, attack, health = 5, 5, 5
	index = "DRAGONS~Shaman~Minion~5~5~5~~Bandersmosh"
	requireTarget, effects, description = False, "", "Each turn this is in your hand, transform it into a 5/5 random Legendary minion"
	name_CN = "班德斯莫什"
	trigHand = Trig_Bandersmosh_PreShifting
	poolIdentifier = "Legendary Minions"
	@classmethod
	def generatePool(cls, pools):
		return "Legendary Minions", list(pools.LegendaryMinions.values())
		

class CumuloMaximus(Minion):
	Class, race, name = "Shaman", "Elemental", "Cumulo-Maximus"
	mana, attack, health = 5, 5, 5
	index = "DRAGONS~Shaman~Minion~5~5~5~Elemental~Cumulo-Maximus~Battlecry"
	requireTarget, effects, description = True, "", "Battlecry: If you have Overloaded Mana Crystals, deal 5 damage"
	name_CN = "遮天雨云"
	def needTarget(self, choice=0):
		return self.Game.Manas.manasLocked[self.ID] + self.Game.Manas.manasOverloaded[self.ID] > 0
		
	def effCanTrig(self):
		self.effectViable = self.Game.Manas.manasLocked[self.ID] + self.Game.Manas.manasOverloaded[self.ID] > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and self.Game.Manas.manasLocked[self.ID] + self.Game.Manas.manasOverloaded[self.ID] > 0:
			self.dealsDamage(target, 5)
		return target
		
		
class DragonsPack(Spell):
	Class, school, name = "Shaman", "Nature", "Dragon's Pack"
	requireTarget, mana, effects = False, 5, ""
	index = "DRAGONS~Shaman~Spell~5~Nature~Dragon's Pack"
	description = "Summon two 2/3 Spirit Wolves with Taunt. If you've Invoked Galakrond twice, give them +2/+2"
	name_CN = "巨龙的兽群"
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def effCanTrig(self): #法术先检测是否可以使用才判断是否显示黄色
		self.effectViable = self.Game.Counters.invokes[self.ID] > 1
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon((minions := [SpiritWolf_Dragons(self.Game, self.ID) for _ in (0, 1)]))
		if self.Game.Counters.invokes[self.ID] > 1: self.AOE_GiveEnchant(minions, 2, 2, name=DragonsPack)
		

class SpiritWolf_Dragons(Minion):
	Class, race, name = "Shaman", "", "Spirit Wolf"
	mana, attack, health = 2, 2, 3
	index = "DRAGONS~Shaman~Minion~2~2~3~~Spirit Wolf~Taunt~Uncollectible"
	requireTarget, effects, description = False, "Taunt", "Taunt"
	name_CN = "幽灵狼"
	
	
class CorruptElementalist(Minion):
	Class, race, name = "Shaman", "", "Corrupt Elementalist"
	mana, attack, health = 6, 3, 3
	index = "DRAGONS~Shaman~Minion~6~3~3~~Corrupt Elementalist~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Invoke Galakrond twice"
	name_CN = "堕落的元素师"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		invokeGalakrond(self.Game, self.ID)
		invokeGalakrond(self.Game, self.ID)
		
		
class Nithogg(Minion):
	Class, race, name = "Shaman", "Dragon", "Nithogg"
	mana, attack, health = 6, 5, 5
	index = "DRAGONS~Shaman~Minion~6~5~5~Dragon~Nithogg~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: Summon two 0/3 Eggs. Next turn they hatch into 4/4 Drakes with Rush"
	name_CN = "尼索格"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon([StormEgg(self.Game, self.ID) for _ in (0, 1)], relative="<>")
		
class StormEgg(Minion):
	Class, race, name = "Shaman", "", "Storm Egg"
	mana, attack, health = 1, 0, 3
	index = "DRAGONS~Shaman~Minion~1~0~3~~Storm Egg~Uncollectible"
	requireTarget, effects, description = False, "", "At the start of your turn, transform into a 4/4 Storm Drake with Rush"
	name_CN = "风暴龙卵"
	trigBoard = Trig_StormEgg		


class StormDrake(Minion):
	Class, race, name = "Shaman", "Dragon", "Storm Drake"
	mana, attack, health = 4, 4, 4
	index = "DRAGONS~Shaman~Minion~4~4~4~Dragon~Storm Drake~Rush~Uncollectible"
	requireTarget, effects, description = False, "Rush", "Rush"
	name_CN = "风暴幼龙"
	
	
class GalakrondsFury(Power):
	mana, name, requireTarget = 2, "Galakrond's Fury", False
	index = "Shaman~Hero Power~2~Galakrond's Fury"
	description = "Summon a 2/1 Elemental with Rush"
	name_CN = "迦拉克隆的愤怒"
	def available(self):
		return not self.chancesUsedUp() and self.Game.space(self.ID)
		
	def effect(self, target=None, choice=0, comment=''):
		self.summon(WindsweptElemental(self.Game, self.ID))
		return 0
		
class WindsweptElemental(Minion):
	Class, race, name = "Shaman", "Elemental", "Windswept Elemental"
	mana, attack, health = 2, 2, 1
	index = "DRAGONS~Shaman~Minion~2~2~1~Elemental~Windswept Elemental~Rush~Uncollectible"
	requireTarget, effects, description = False, "Rush", "Rush"
	name_CN = "风啸元素"
	

class GalakrondtheTempest(Galakrond_Hero):
	mana, weapon, description = 7, None, "Battlecry: Summon two 2/2 Storms with Rush. (Invoke twice to upgrade)"
	Class, name, heroPower, health, armor = "Shaman", "Galakrond, the Tempest", GalakrondsFury, 30, 5
	index = "DRAGONS~Shaman~Hero Card~7~Galakrond, the Tempest~Battlecry~Legendary"
	name_CN = "风暴巨龙迦拉克隆"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.upgradedGalakrond = GalakrondtheApocalypes_Shaman
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon([BrewingStorm(self.Game, self.ID) for _ in (0, 1)])
		
class GalakrondtheApocalypes_Shaman(Galakrond_Hero):
	mana, weapon, description = 7, None, "Battlecry: Summon two 4/4 Storms with Rush. (Invoke twice to upgrade)"
	Class, name, heroPower, health, armor = "Shaman", "Galakrond, the Apocalypes", GalakrondsFury, 30, 5
	index = "DRAGONS~Shaman~Hero Card~7~Galakrond, the Apocalypes~Battlecry~Legendary~Uncollectible"
	name_CN = "天降浩劫迦拉克隆"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.upgradedGalakrond = GalakrondAzerothsEnd_Shaman
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon([LivingStorm(self.Game, self.ID) for _ in (0, 1)])
		
class GalakrondAzerothsEnd_Shaman(Galakrond_Hero):
	mana, weapon, description = 7, None, "Battlecry: Summon two 8/8 Storms with Rush. Equip a 5/2 Claw"
	Class, name, heroPower, health, armor = "Shaman", "Galakrond, Azeroth's End", GalakrondsFury, 30, 5
	index = "DRAGONS~Shaman~Hero Card~7~Galakrond, Azeroth's End~Battlecry~Legendary~Uncollectible"
	name_CN = "世界末日迦拉克隆"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.upgradedGalakrond = None
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon([RagingStorm(self.Game, self.ID) for _ in (0, 1)])
		self.equipWeapon(DragonClaw(self.Game, self.ID))
		
class BrewingStorm(Minion):
	Class, race, name = "Shaman", "Elemental", "Brewing Storm"
	mana, attack, health = 2, 2, 2
	index = "DRAGONS~Shaman~Minion~2~2~2~Elemental~Brewing Storm~Rush~Uncollectible"
	requireTarget, effects, description = False, "Rush", "Rush"
	name_CN = "成型风暴"
	
class LivingStorm(Minion):
	Class, race, name = "Shaman", "Elemental", "Living Storm"
	mana, attack, health = 4, 4, 4
	index = "DRAGONS~Shaman~Minion~4~4~4~Elemental~Living Storm~Rush~Uncollectible"
	requireTarget, effects, description = False, "Rush", "Rush"
	name_CN = "活体风暴"
	
class RagingStorm(Minion):
	Class, race, name = "Shaman", "Elemental", "Raging Storm"
	mana, attack, health = 8, 8, 8
	index = "DRAGONS~Shaman~Minion~8~8~8~Elemental~Raging Storm~Rush~Uncollectible"
	requireTarget, effects, description = False, "Rush", "Rush"
	name_CN = "狂怒风暴"
	

class RainofFire(Spell):
	Class, school, name = "Warlock", "Fel", "Rain of Fire"
	requireTarget, mana, effects = False, 1, ""
	index = "DRAGONS~Warlock~Spell~1~Fel~Rain of Fire"
	description = "Deal 1 damage to all characters"
	name_CN = "火焰之雨"
	def text(self): return self.calcDamage(1)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = self.calcDamage(1)
		targets = self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)
		self.AOE_Damage(targets, [damage] * len(targets))
		
		
class NetherBreath(Spell):
	Class, school, name = "Warlock", "Fel", "Nether Breath"
	requireTarget, mana, effects = True, 2, ""
	index = "DRAGONS~Warlock~Spell~2~Fel~Nether Breath"
	description = "Deal 2 damage. If you're holding a Dragon, deal 4 damage with Lifesteal instead"
	name_CN = "虚空吐息"
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID)
		
	def text(self): return "%d, %d"%(self.calcDamage(2), self.calcDamage(4))
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			if self.Game.Hand_Deck.holdingDragon(self.ID):
				damage = self.calcDamage(4)
				self.effects["Lifesteal"] = 1
			else: damage = self.calcDamage(2)
			self.dealsDamage(target, damage)
		

class DarkSkies(Spell):
	Class, school, name = "Warlock", "Fel", "Dark Skies"
	requireTarget, mana, effects = False, 3, ""
	index = "DRAGONS~Warlock~Spell~3~Fel~Dark Skies"
	description = "Deal 1 damage to a random minion. Repeat for each card in your hand"
	name_CN = "黑暗天际"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = self.calcDamage(1)
		game = self.Game
		#在使用这个法术后先打一次，然后检测手牌数。总伤害个数是手牌数+1
		if minions := game.minionsAlive(1) + game.minionsAlive(2):
			self.dealsDamage(numpyChoice(minions), damage)
			for _ in range(len(game.Hand_Deck.hands[self.ID])):
				if minions := self.Game.minionsAlive(1) + self.Game.minionsAlive(2): self.dealsDamage(numpyChoice(minions), damage)
				else: break
		
		
class DragonblightCultist(Minion):
	Class, race, name = "Warlock", "", "Dragonblight Cultist"
	mana, attack, health = 3, 1, 1
	index = "DRAGONS~Warlock~Minion~3~1~1~~Dragonblight Cultist~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Invoke Galakrond. Gain +1 Attack for each other friendly minion"
	name_CN = "龙骨荒野异教徒"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		invokeGalakrond(self.Game, self.ID)
		if (self.onBoard or self.inHand) and (num := len(self.Game.minionsAlive(self.ID, self))):
			self.giveEnchant(self, num, 0, name=DragonblightCultist)
		
		
class FiendishRites(Spell):
	Class, school, name = "Warlock", "", "Fiendish Rites"
	requireTarget, mana, effects = False, 4, ""
	index = "DRAGONS~Warlock~Spell~4~~Fiendish Rites"
	description = "Invoke Galakrond. Give your minions +1 Attack"
	name_CN = "邪鬼仪式"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		invokeGalakrond(self.Game, self.ID)
		self.AOE_GiveEnchant(self.Game.minionsonBoard(self.ID), 1, 0, name=FiendishRites)
		
		
class VeiledWorshipper(Minion):
	Class, race, name = "Warlock", "", "Veiled Worshipper"
	mana, attack, health = 4, 5, 4
	index = "DRAGONS~Warlock~Minion~4~5~4~~Veiled Worshipper~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: If you've Invoked twice, draw 3 cards"
	name_CN = "暗藏的信徒"
	
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.invokes[self.ID] > 1
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Counters.invokes[self.ID] > 1:
			self.Game.Hand_Deck.drawCard(self.ID)
			self.Game.Hand_Deck.drawCard(self.ID)
			self.Game.Hand_Deck.drawCard(self.ID)
		
		
class CrazedNetherwing(Minion):
	Class, race, name = "Warlock", "Dragon", "Crazed Netherwing"
	mana, attack, health = 5, 5, 5
	index = "DRAGONS~Warlock~Minion~5~5~5~Dragon~Crazed Netherwing~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: If you're holding a Dragon, deal 3 dammage to all other characters"
	name_CN = "疯狂的灵翼龙"
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID, self)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Hand_Deck.holdingDragon(self.ID):
			targets = [self.Game.heroes[1], self.Game.heroes[2]] + self.Game.minionsonBoard(self.ID, self) + self.Game.minionsonBoard(3-self.ID)
			self.AOE_Damage(targets, [3 for minion in targets])
		
		
class AbyssalSummoner(Minion):
	Class, race, name = "Warlock", "", "Abyssal Summoner"
	mana, attack, health = 6, 2, 2
	index = "DRAGONS~Warlock~Minion~6~2~2~~Abyssal Summoner~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Summon a Demon with Taunt and stats equal to your hand size"
	name_CN = "深渊召唤者"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		handSize = len(self.Game.Hand_Deck.hands[self.ID])
		if handSize == 1: self.summon(AbyssalDestroyer(self.Game, self.ID))
		elif handSize > 1:
			cost = min(handSize, 10)
			newIndex = "DRAGONS~Warlock~Minion~%d~%d~%d~Demon~Abyssal Destroyer~Taunt~Uncollectible"%(cost, handSize, handSize)
			subclass = type("AbyssalDestroyer__"+str(handSize), (AbyssalDestroyer, ),
							{"mana": cost, "attack": handSize, "health": handSize,
							"index": newIndex}
							)
			self.summon(subclass(self.Game, self.ID))
		

class AbyssalDestroyer(Minion):
	Class, race, name = "Warlock", "Demon", "Abyssal Destroyer"
	mana, attack, health = 1, 1, 1
	index = "DRAGONS~Warlock~Minion~1~1~1~Demon~Abyssal Destroyer~Taunt~Uncollectible"
	requireTarget, effects, description = False, "Taunt", "Taunt"
	name_CN = "深渊毁灭者"
	
	
class GalakrondsMalice(Power):
	mana, name, requireTarget = 2, "Galakrond's Malice", False
	index = "Shaman~Hero Power~2~Galakrond's Malice"
	description = "Summon two 1/1 Imps"
	name_CN = "迦拉克隆的恶意"
	def available(self):
		return not self.chancesUsedUp() and self.Game.space(self.ID)
		
	def effect(self, target=None, choice=0, comment=''):
		self.summon([DraconicImp(self.Game, self.ID) for _ in (0, 1)])
		return 0
		

class GalakrondtheWretched(Galakrond_Hero):
	mana, weapon, description = 7, None, "Battlecry: Summon a random Demon. (Invoke twice to upgrade)"
	Class, name, heroPower, health, armor = "Warlock", "Galakrond, the Wretched", GalakrondsMalice, 30, 5
	index = "DRAGONS~Warlock~Hero Card~7~Galakrond, the Wretched~Battlecry~Legendary"
	name_CN = "邪火巨龙迦拉克隆"
	poolIdentifier = "Demons to Summon"
	@classmethod
	def generatePool(cls, pools):
		return "Demons to Summon", list(pools.MinionswithRace["Demon"].values())
		
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.upgradedGalakrond = GalakrondtheApocalypes_Warlock
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon(numpyChoice(self.rngPool("Demons to Summon"))(self.Game, self.ID))
		
class GalakrondtheApocalypes_Warlock(Galakrond_Hero):
	mana, weapon, description = 7, None, "Battlecry: Summon 2 random Demons. (Invoke twice to upgrade)"
	Class, name, heroPower, health, armor = "Warlock", "Galakrond, the Apocalypes", GalakrondsMalice, 30, 5
	index = "DRAGONS~Warlock~Hero Card~7~Galakrond, the Apocalypes~Battlecry~Legendary~Uncollectible"
	name_CN = "天降浩劫迦拉克隆"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.upgradedGalakrond = GalakrondAzerothsEnd_Warlock
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon([demon(self.Game, self.ID) for demon in numpyChoice(self.rngPool("Demons to Summon"), 2, replace=False)])
		
class GalakrondAzerothsEnd_Warlock(Galakrond_Hero):
	mana, weapon, description = 7, None, "Battlecry: Summon 4 random Demons. Equip a 5/2 Claw"
	Class, name, heroPower, health, armor = "Warlock", "Galakrond, Azeroth's End", GalakrondsMalice, 30, 5
	index = "DRAGONS~Warlock~Hero Card~7~Galakrond, Azeroth's End~Battlecry~Legendary~Uncollectible"
	name_CN = "世界末日迦拉克隆"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.upgradedGalakrond = None
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		demons = numpyChoice(self.rngPool("Demons to Summon"), 4, replace=True)
		self.summon([demon(self.Game, self.ID) for demon in demons])
		self.equipWeapon(DragonClaw(self.Game, self.ID))
		
class DraconicImp(Minion):
	Class, race, name = "Warlock", "Demon", "Draconic Imp"
	mana, attack, health = 1, 1, 1
	index = "DRAGONS~Warlock~Minion~1~1~1~Demon~Draconic Imp~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "龙裔小鬼"
	
	
class ValdrisFelgorge(Minion):
	Class, race, name = "Warlock", "", "Valdris Felgorge"
	mana, attack, health = 7, 4, 4
	index = "DRAGONS~Warlock~Minion~7~4~4~~Valdris Felgorge~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: Increase your maximum hand size to 12. Draw 4 cards"
	name_CN = "瓦迪瑞斯·邪噬"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.Hand_Deck.handUpperLimit[self.ID] = 12
		self.Game.sendSignal("HandUpperLimitChange", self.ID, None, None, 0, "")
		for i in (0, 1, 2, 3): self.Game.Hand_Deck.drawCard(self.ID)
		
		
class ZzerakutheWarped(Minion):
	Class, race, name = "Warlock", "Dragon", "Zzeraku the Warped"
	mana, attack, health = 8, 4, 12
	index = "DRAGONS~Warlock~Minion~8~4~12~Dragon~Zzeraku the Warped~Legendary"
	requireTarget, effects, description = False, "", "Whenever your hero takes damage, summon a 6/6 Nether Drake"
	name_CN = "扭曲巨龙泽拉库"
	trigBoard = Trig_ZzerakutheWarped		


class NetherDrake(Minion):
	Class, race, name = "Warlock", "Dragon", "Nether Drake"
	mana, attack, health = 6, 6, 6
	index = "DRAGONS~Warlock~Minion~6~6~6~Dragon~Nether Drake~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "虚空幼龙"
	

class SkyRaider(Minion):
	Class, race, name = "Warrior", "Pirate", "Sky Raider"
	mana, attack, health = 1, 1, 2
	index = "DRAGONS~Warrior~Minion~1~1~2~Pirate~Sky Raider~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Add a random Pirate to your hand"
	name_CN = "空中悍匪"
	poolIdentifier = "Pirates"
	@classmethod
	def generatePool(cls, pools):
		return "Pirates", list(pools.MinionswithRace["Pirate"].values())
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.addCardtoHand(numpyChoice(self.rngPool("Pirates")), self.ID, byType=True)
		
		
class RitualChopper(Weapon):
	Class, name, description = "Warrior", "Ritual Chopper", "Battlecry: Invoke Galakrond"
	mana, attack, durability, effects = 2, 1, 2, ""
	index = "DRAGONS~Warrior~Weapon~2~1~2~Ritual Chopper~Battlecry"
	name_CN = "仪式斩斧"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		invokeGalakrond(self.Game, self.ID)
		
		
class Awaken(Spell):
	Class, school, name = "Warrior", "", "Awaken!"
	requireTarget, mana, effects = False, 3, ""
	index = "DRAGONS~Warrior~Spell~3~~Awaken!"
	description = "Invoke Galakrond. Deal 1 damage to all minions"
	name_CN = "祈求觉醒"
	def text(self): return self.calcDamage(1)
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		invokeGalakrond(self.Game, self.ID)
		damage = self.calcDamage(1)
		targets = self.Game.minionsonBoard(self.ID) + self.Game.minionsonBoard(3-self.ID)
		self.AOE_Damage(targets, [damage for minion in targets])
		
		
class Ancharrr(Weapon):
	Class, name, description = "Warrior", "Ancharrr", "After your hero attacks, draw a Pirate from your deck"
	mana, attack, durability, effects = 3, 2, 2, ""
	index = "DRAGONS~Warrior~Weapon~3~2~2~Ancharrr~Legendary"
	name_CN = "海盗之锚"
	trigBoard = Trig_Ancharrr		


class EVILQuartermaster(Minion):
	Class, race, name = "Warrior", "", "EVIL Quartermaster"
	mana, attack, health = 3, 2, 3
	index = "DRAGONS~Warrior~Minion~3~2~3~~EVIL Quartermaster~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Add a Lackey to your hand. Gain 3 Armor"
	name_CN = "怪盗军需官"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.addCardtoHand(numpyChoice(Lackeys), self.ID)
		self.giveHeroAttackArmor(self.ID, armor=3)
		
		
class RammingSpeed(Spell):
	Class, school, name = "Warrior", "", "Ramming Speed"
	requireTarget, mana, effects = True, 3, ""
	index = "DRAGONS~Warrior~Spell~3~~Ramming Speed"
	description = "Force a minion to attack one of its neighbors"
	name_CN = "横冲直撞"
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard and target.health > 0 and target.dead == False
		
	#不知道目标随从不在手牌中时是否会有任何事情发生
	#不会消耗随从的攻击机会
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and target.onBoard and target.health > 0 and not target.dead:
			neighbors = [minion for minion in self.Game.neighbors2(target)[0] if minion.health > 0 and not minion.dead]
			if neighbors: self.Game.battle(target, numpyChoice(neighbors), verifySelectable=False, useAttChance=False, resolveDeath=False)
		return target
		
		
class ScionofRuin(Minion):
	Class, race, name = "Warrior", "Dragon", "Scion of Ruin"
	mana, attack, health = 4, 3, 2
	index = "DRAGONS~Warrior~Minion~4~3~2~Dragon~Scion of Ruin~Rush~Battlecry"
	requireTarget, effects, description = False, "Rush", "Rush. Battlecry: If you've Invoked twice, summon two copies of this"
	name_CN = "废墟之子"
	
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.invokes[self.ID] > 1
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if not self.dead and self.Game.Counters.invokes[self.ID] > 1:
			if self.onBoard: self.summon([self.selfCopy(self.ID, self), self.selfCopy(self.ID, self)], relative="<>")
			else: self.summon([ScionofRuin(self.Game, self.ID) for _ in (0, 1)]) #假设废墟之子在战吼前死亡或者离场，则召唤基础复制
		
		
class Skybarge(Minion):
	Class, race, name = "Warrior", "Mech", "Skybarge"
	mana, attack, health = 3, 2, 5
	index = "DRAGONS~Warrior~Minion~3~2~5~Mech~Skybarge"
	requireTarget, effects, description = False, "", "After you summon a Pirate, deal 2 damage to a random enemy"
	name_CN = "空中炮艇"
	trigBoard = Trig_Skybarge		


class MoltenBreath(Spell):
	Class, school, name = "Warrior", "Fire", "Molten Breath"
	requireTarget, mana, effects = True, 4, ""
	index = "DRAGONS~Warrior~Spell~4~Fire~Molten Breath"
	description = "Deal 5 damage to a minion. If you're holding Dragon, gain 5 Armor"
	name_CN = "熔火吐息"
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID)
		
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard
		
	def text(self): return self.calcDamage(5)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.dealsDamage(target, self.calcDamage(5))
			if self.Game.Hand_Deck.holdingDragon(self.ID) and self.Game.Hand_Deck.handNotFull(self.ID):
				self.giveHeroAttackArmor(self.ID, armor=5)
		return target
		
		
class GalakrondsMight(Power):
	mana, name, requireTarget = 2, "Galakrond's Might", False
	index = "Rogue~Hero Power~2~Galakrond's Might"
	description = "Give your hero +3 Attack this turn"
	name_CN = "迦拉克隆之力"
	def effect(self, target=None, choice=0, comment=''):
		self.giveHeroAttackArmor(self.ID, attGain=3, name=GalakrondsMight)
		return 0
		
class GalakrondtheUnbreakable(Galakrond_Hero):
	mana, weapon, description = 7, None, "Battlecry: Draw 1 minion. Give it +4/+4. (Invoke twice to upgrade)"
	Class, name, heroPower, health, armor = "Warrior", "Galakrond, the Unbreakable", GalakrondsMight, 30, 5
	index = "DRAGONS~Warrior~Hero Card~7~Galakrond, the Unbreakable~Battlecry~Legendary"
	name_CN = "无敌巨龙迦拉克隆"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.upgradedGalakrond = GalakrondtheApocalypes_Warrior
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		card, mana, entersHand = self.drawCertainCard(lambda card: card.category == "Minion")
		if entersHand: self.giveEnchant(card, 4, 4, name=GalakrondtheUnbreakable, add2EventinGUI=False)
		
class GalakrondtheApocalypes_Warrior(Galakrond_Hero):
	mana, weapon, description = 7, None, "Battlecry: Draw 2 minions. Give them +4/+4. (Invoke twice to upgrade)"
	Class, name, heroPower, health, armor = "Warrior", "Galakrond, the Apocalypes", GalakrondsMight, 30, 5
	index = "DRAGONS~Warrior~Hero Card~7~Galakrond, the Apocalypes~Battlecry~Legendary~Uncollectible"
	name_CN = "天降浩劫迦拉克隆"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.upgradedGalakrond = GalakrondAzerothsEnd_Warrior
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for _ in (0, 1):
			card, mana, entersHand = self.drawCertainCard(lambda card: card.category == "Minion")
			if not card: break
			elif entersHand: self.giveEnchant(card, 4, 4, name=GalakrondtheUnbreakable, add2EventinGUI=False)
		
class GalakrondAzerothsEnd_Warrior(Galakrond_Hero):
	mana, weapon, description = 7, None, "Battlecry: Draw 4 minions. Give them +4/+4. Equip a 5/2 Claw"
	Class, name, heroPower, health, armor = "Warrior", "Galakrond, Azeroth's End", GalakrondsMight, 30, 5
	index = "DRAGONS~Warrior~Hero Card~7~Galakrond, Azeroth's End~Battlecry~Legendary~Uncollectible"
	name_CN = "世界末日迦拉克隆"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.upgradedGalakrond = None
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for _ in (0, 1, 2, 3):
			card, mana, entersHand = self.drawCertainCard(lambda card: card.category == "Minion")
			if not card: break
			elif entersHand: self.giveEnchant(card, 4, 4, name=GalakrondtheUnbreakable, add2EventinGUI=False)
		self.equipWeapon(DragonClaw(self.Game, self.ID))
		
		
#这个战吼的攻击会消耗随从的攻击次数。在战吼结束后给其加上冲锋或者突袭时，其不能攻击
#战吼的攻击可以正常触发奥秘和攻击目标指向扳机
#攻击过程中死亡之翼濒死会停止攻击，但是如果中途被冰冻是不会停止攻击的。即用战斗不检查攻击的合法性。
#战吼结束之后才会进行战斗的死亡结算，期间被攻击的随从可以降到负血量还留在场上。
class DeathwingMadAspect(Minion):
	Class, race, name = "Warrior", "Dragon", "Deathwing, Mad Aspect"
	mana, attack, health = 8, 12, 12
	index = "DRAGONS~Warrior~Minion~8~12~12~Dragon~Deathwing, Mad Aspect~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: Attack ALL other minions"
	name_CN = "疯狂巨龙死亡之翼"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		game = self.Game
		minions = game.minionsAlive(self.ID, game.minionPlayed) + game.minionsAlive(3-self.ID)
		numpyShuffle(minions)
		while minions:
			minion = minions.pop()
			if minion.onBoard and minion.health > 0 and not minion.dead:
				game.battle(game.minionPlayed, minion, verifySelectable=False, useAttChance=True, resolveDeath=False, resetRedirTrig=False)
		

"""Game TrigEffects and Game Auras"""
class SwapHeroPowersBack(TrigEffect):
	card, trigType = GrizzledWizard, "TurnStart"
	def trigEffect(self): self.card.swapHeroPowers()

class GameManaAura_BlowtorchSaboteur(GameManaAura_OneTime):
	card, to, temporary = BlowtorchSaboteur, 3, True
	def applicable(self, target): return target.ID == self.ID

class GameAura_GorutheMightree(GameAura_AlwaysOn):
	card, attGain, healthGain, counter = GorutheMightree, 1, 1, 1
	def applicable(self, target): return target.name == "True"

	def upgrade(self):
		self.attGain = self.healthGain = self.counter = self.counter + 1
		for receiver in self.receivers:
			receiver.attGain, receiver.healthGain = self.attGain, self.healthGain
			receiver.recipient.calcStat()
		if self.counter and self.card.btn: self.card.btn.trigAni(self.counter)


class GameManaAura_Dragoncaster(GameManaAura_OneTime):
	card, to = Dragoncaster, 0
	def applicable(self, target): return target.ID == self.ID and target.category == "Spell"
	
	
Dragons_Cards = [
		#Neutral
		EvasiveFeywing, FrizzKindleroost, Hippogryph, HoardPillager, TrollBatrider, WingCommander, ZulDrakRitualist,
		BigOlWhelp, ChromaticEgg, CobaltSpellkin, FacelessCorruptor, KoboldStickyfinger, Platebreaker, ShieldofGalakrond,
		Skyfin, TentacledMenace, CamouflagedDirigible, EvasiveWyrm, Gyrocopter, KronxDragonhoof, ReanimatedDragon,
		UtgardeGrapplesniper, EvasiveDrakonid, Shuma, Tentacle_Dragons, TwinTyrant, DragonqueenAlexstrasza, Sathrovarr,
		DragonClaw,
		#Druid
		Embiggen, SecuretheDeck, StrengthinNumbers, Treenforcements, SmallRepairs, SpinemUp, BreathofDreams, Shrubadier,
		Treant_Dragons, Aeroponics, EmeraldExplorer, GorutheMightree, YseraUnleashed, DreamPortal,
		#Hunter
		CleartheWay, Gryphon_Dragons, DwarvenSharpshooter, ToxicReinforcements,
		#Neutral
		LeperGnome_Dragons,
		#Hunter
		CorrosiveBreath, PhaseStalker, DivingGryphon, PrimordialExplorer, Stormhammer, Dragonbane, Veranus,
		#Mage
		ArcaneBreath, ElementalAllies, LearnDraconic, DraconicEmissary, VioletSpellwing, Chenvaala, SnowElemental,
		AzureExplorer, MalygossFrostbolt, MalygossMissiles, MalygossNova, MalygossPolymorph, MalygossTome, MalygossExplosion,
		MalygossIntellect, MalygossFireball, MalygossFlamestrike, MalygossSheep, MalygosAspectofMagic, RollingFireball,
		Dragoncaster, ManaGiant,
		#Paladin
		RighteousCause, SandBreath, Sanctuary, IndomitableChampion, BronzeExplorer, SkyClaw, Microcopter,
		DragonriderTalritha, LightforgedZealot, NozdormutheTimeless, AmberWatcher, LightforgedCrusader,
		#Priest
		WhispersofEVIL, DiscipleofGalakrond, EnvoyofLazul, BreathoftheInfinite, MindflayerKaahrj, FateWeaver, GraveRune,
		Chronobreaker, TimeRip, GalakrondtheUnspeakable, GalakrondtheApocalypes_Priest, GalakrondAzerothsEnd_Priest, MurozondtheInfinite,
		#Rogue
		BloodsailFlybooter, SkyPirate, DragonsHoard, PraiseGalakrond, SealFate, UmbralSkulker, NecriumApothecary, Stowaway,
		Waxadred, WaxadredsCandle, CandleBreath, FlikSkyshiv, GalakrondtheNightmare, GalakrondtheApocalypes_Rogue,
		GalakrondAzerothsEnd_Rogue,
		#Shaman
		InvocationofFrost, SurgingTempest, Squallhunter, StormsWrath, LightningBreath, Bandersmosh, CumuloMaximus,
		DragonsPack, SpiritWolf_Dragons, CorruptElementalist, Nithogg, StormEgg, StormDrake, WindsweptElemental,
		GalakrondtheTempest, GalakrondtheApocalypes_Shaman, GalakrondAzerothsEnd_Shaman, BrewingStorm, LivingStorm,
		RagingStorm,
		#Warlock
		RainofFire, NetherBreath, DarkSkies, DragonblightCultist, FiendishRites, VeiledWorshipper, CrazedNetherwing,
		AbyssalSummoner, AbyssalDestroyer, GalakrondtheWretched, GalakrondtheApocalypes_Warlock,
		GalakrondAzerothsEnd_Warlock, DraconicImp, ValdrisFelgorge, ZzerakutheWarped, NetherDrake,
		#Warrior
		SkyRaider, RitualChopper, Awaken, Ancharrr, EVILQuartermaster, RammingSpeed, ScionofRuin, Skybarge, MoltenBreath,
		GalakrondtheUnbreakable, GalakrondtheApocalypes_Warrior, GalakrondAzerothsEnd_Warrior, DeathwingMadAspect,
]

Dragons_Cards_Collectible = [
		#Neutral
		EvasiveFeywing, FrizzKindleroost, Hippogryph, HoardPillager, TrollBatrider, WingCommander, ZulDrakRitualist,
		BigOlWhelp, ChromaticEgg, CobaltSpellkin, FacelessCorruptor, KoboldStickyfinger, Platebreaker, ShieldofGalakrond,
		Skyfin, TentacledMenace, CamouflagedDirigible, EvasiveWyrm, Gyrocopter, KronxDragonhoof, UtgardeGrapplesniper,
		EvasiveDrakonid, Shuma, TwinTyrant, DragonqueenAlexstrasza, Sathrovarr,
		#Druid
		Embiggen, SecuretheDeck, StrengthinNumbers, Treenforcements, BreathofDreams, Shrubadier, Aeroponics, EmeraldExplorer,
		GorutheMightree, YseraUnleashed,
		#Hunter
		CleartheWay, DwarvenSharpshooter, ToxicReinforcements, CorrosiveBreath, PhaseStalker, DivingGryphon,
		PrimordialExplorer, Stormhammer, Dragonbane, Veranus,
		#Mage
		ArcaneBreath, ElementalAllies, LearnDraconic, VioletSpellwing, Chenvaala, AzureExplorer, MalygosAspectofMagic,
		RollingFireball, Dragoncaster, ManaGiant,
		#Paladin
		RighteousCause, SandBreath, Sanctuary, BronzeExplorer, SkyClaw, DragonriderTalritha, LightforgedZealot,
		NozdormutheTimeless, AmberWatcher, LightforgedCrusader,
		#Priest
		WhispersofEVIL, DiscipleofGalakrond, EnvoyofLazul, BreathoftheInfinite, MindflayerKaahrj, FateWeaver, GraveRune,
		Chronobreaker, TimeRip, GalakrondtheUnspeakable, MurozondtheInfinite,
		#Rogue
		BloodsailFlybooter, DragonsHoard, PraiseGalakrond, SealFate, UmbralSkulker, NecriumApothecary, Stowaway, Waxadred,
		CandleBreath, FlikSkyshiv, GalakrondtheNightmare,
		#Shaman
		InvocationofFrost, SurgingTempest, Squallhunter, StormsWrath, LightningBreath, Bandersmosh, CumuloMaximus,
		DragonsPack, CorruptElementalist, Nithogg, GalakrondtheTempest,
		#Warlock
		RainofFire, NetherBreath, DarkSkies, DragonblightCultist, FiendishRites, VeiledWorshipper, CrazedNetherwing,
		AbyssalSummoner, GalakrondtheWretched, ValdrisFelgorge, ZzerakutheWarped,
		#Warrior
		SkyRaider, RitualChopper, Awaken, Ancharrr, EVILQuartermaster, RammingSpeed, ScionofRuin, Skybarge, MoltenBreath,
		GalakrondtheUnbreakable, DeathwingMadAspect,
]


TrigsDeaths_Dragons = {Death_TastyFlyfish: (TastyFlyfish, "Deathrattle: Give a random Dragon in your hand +2/+2"),
					   Death_BadLuckAlbatross: (BadLuckAlbatross, "Deathrattle: Shuffle two 1/1 Albatross into your opponent's deck"),
					   Death_ChromaticEgg: (ChromaticEgg, "Deathrattle: Hatch"),
					   Death_LeperGnome_Dragons: (LeperGnome_Dragons, "Deathrattle: Deal 2 damage to the enemy hero"),
					   Death_VioletSpellwing: (VioletSpellwing, "Deathrattle: Add an 'Arcane Missile' to your hand"),
					   Death_DragonriderTalritha: (DragonriderTalritha, "Deathrattle: Give a Dragon in your hand +3/+3 and this Deathrattle"),
					   Death_MindflayerKaahrj: (MindflayerKaahrj, "Deathrattle: Summon a new copy of the chosen minion"),
					   Death_GraveRune: (GraveRune, "Deathrattle: Summon 2 copies of this"),
					   Death_Chronobreaker: (Chronobreaker, "Deathrattle: If you're holding a Dragon, deal 3 damage to all enemy minions"),
					   Death_Waxadred: (Waxadred, "Deathrattle: Shuffle a Candle into your deck that resummons Waxadred when drawn"),
					   }