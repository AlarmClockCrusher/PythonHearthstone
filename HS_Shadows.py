from Parts_ConstsFuncsImports import *
from Parts_CardTypes import *
from Parts_TrigsAuras import *

from HS_AcrossPacks import Classes, TheCoin, Lackeys, MurlocScout, PatientAssassin, GoldenKobold, \
						TolinsGoblet, WondrousWand, ZarogsCrown, Bomb, BoomBot


FantasticTreasures = [GoldenKobold, TolinsGoblet, WondrousWand, ZarogsCrown]


"""Auras"""
class Aura_WhirlwindTempest(Aura_AlwaysOn):
	effGain, targets = "Mega Windfury", "All"
	def applicable(self, target): return target.effects["Windfury"] > 0


"""Deathrattles"""
class Death_HenchClanHogsteed(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.summon(HenchClanSquire(self.keeper.Game, self.keeper.ID))

class Death_RecurringVillain(Deathrattle_Minion):
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.Game.effects[self.keeper.ID]["Deathrattle X"] < 1 and target == self.keeper and number > 3

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.summon(type(self.keeper)(self.keeper.Game, self.keeper.ID))

class Death_EccentricScribe(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.keeper
		minion.summon([VengefulScroll(minion.Game, minion.ID) for i in (0, 1, 2, 3)], relative="<>")

class Death_Safeguard(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.summon(VaultSafe(self.keeper.Game, self.keeper.ID))

class Death_TunnelBlaster(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		targets = self.keeper.Game.minionsonBoard(1) + self.keeper.Game.minionsonBoard(2)
		self.keeper.AOE_Damage(targets, [3] * len(targets))

class Death_Acornbearer(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.addCardtoHand([Squirrel_Shadows, Squirrel_Shadows], self.keeper.ID)

class Death_Lucentbark(Deathrattle_Minion):
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return target == self.keeper and self.keeper.Game.space(self.keeper.ID) > 0

	# 这个变形亡语只能触发一次。
	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrig(signal, ID, subject, target, number, comment):
			minion = self.keeper
			if minion.Game.GUI:
				minion.Game.GUI.deathrattleAni(minion)
			minion.Game.Counters.deathrattlesTriggered[minion.ID].append(Death_Lucentbark)
			dormant = SpiritofLucentbark(minion.Game, minion.ID)
			minion.Game.transform(minion, dormant)

class Death_Shimmerfly(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.addCardtoHand(numpyChoice(self.rngPool("Hunter Spells")), self.keeper.ID)

class Death_Ursatron(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.drawCertainCard(lambda card: "Mech" in card.race)
		
class Death_Oblivitron(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if mech := self.keeper.try_SummonfromHand(func=lambda card: "Mech" in card.race):
			for trig in mech.deathrattles: trig.trig("TrigDeathrattle", mech.ID, None, mech, mech.attack, "")

class Death_BronzeHerald(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.addCardtoHand([BronzeDragon, BronzeDragon], self.keeper.ID)

class Death_EVILConscripter(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.addCardtoHand(numpyChoice(Lackeys), self.keeper.ID)

class Death_HenchClanShadequill(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.restoresHealth(self.keeper.Game.heroes[3 - self.keeper.ID], self.keeper.calcHeal(5))

class Death_ConvincingInfiltrator(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.keeper
		minions = minion.Game.minionsAlive(3 - minion.ID)
		if minions: minion.Game.killMinion(minion, minions)

# There are minions who also have this deathrattle.
class Death_WagglePick(Deathrattle_Weapon):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if minions := self.keeper.Game.minionsonBoard(self.keeper.ID):
			minion = numpyChoice(minions)
			# 假设那张随从在进入手牌前接受-2费效果。可以被娜迦海巫覆盖。
			self.keeper.Game.returnObj2Hand(minion, deathrattlesStayArmed=False, manaMod=ManaMod(minion, by=-2))

class Death_SouloftheMurloc(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.summon(MurlocScout(self.keeper.Game, self.keeper.ID))

class Death_EagerUnderling(Deathrattle_Weapon):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if minions := self.keeper.Game.minionsonBoard(self.keeper.ID):
			self.keeper.AOE_GiveEnchant(numpyChoice(minions, min(len(minions), 2), replace=False), 2, 2, name=EagerUnderling)
			
			
"""Triggers"""
class Trig_MagicCarpet(TrigBoard):
	signals = ("MinionBeenPlayed", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject != self.keeper and subject.ID == self.keeper.ID and number == 1

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.giveEnchant(subject, 1, 0, effGain="Rush", name=MagicCarpet)
		
		
class Trig_ArchmageVargoth(TrigBoard):
	signals = ("TurnEnds", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		spells = [card for card in self.keeper.Game.Counters.cardsPlayedEachTurn[self.keeper.ID][-1] if card.category == "Spell"]
		if spells: numpyChoice(spells)(self.keeper.Game, self.keeper.ID).cast()
			
			
class Trig_ProudDefender(Trig_SelfAura):
	signals = ("MinionAppears", "MinionDisappears")
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and (subject if 'A' in signal else target).ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.calcStat()


class Trig_SoldierofFortune(TrigBoard):
	signals = ("MinionAttackingMinion", "MinionAttackingHero", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject == self.keeper

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.addCardtoHand(TheCoin, 3-self.keeper.ID)
		
		
class Trig_AzeriteElemental(TrigBoard):
	signals = ("TurnStarts", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.giveEnchant(self.keeper, effectEnchant=Enchantment_Cumulative(effGain="Spell Damage", effNum=2,
																				  name=AzeriteElemental))


class Trig_ExoticMountseller(TrigBoard):
	signals = ("SpellPlayed", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject.ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.keeper
		minion.summon(numpyChoice(self.rngPool("3-Cost Beasts to Summon"))(minion.Game, minion.ID))
		

class Trig_UnderbellyOoze(TrigBoard):
	signals = ("MinionTakesDmg", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and target == self.keeper and self.keeper.health > 0 and self.keeper.dead == False

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.summon(self.keeper.selfCopy(self.keeper.ID, self.keeper))
		

class Trig_Batterhead(TrigBoard):
	signals = ("MinionAttackedMinion", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject == self.keeper and self.keeper.health > 0 and self.keeper.dead == False and (target.health < 1 or target.dead == True)

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.attChances_extra += 1
		

class Trig_BigBadArchmage(TrigBoard):
	signals = ("TurnEnds", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.keeper
		minion.summon(numpyChoice(self.rngPool("6-Cost Minions to Summon"))(minion.Game, minion.ID))
		

class Trig_KeeperStalladris(TrigBoard):
	signals = ("SpellBeenPlayed", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject.ID == self.keeper.ID and subject.options

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.addCardtoHand(type(subject).options, self.keeper.ID)

			
class Trig_Lifeweaver(TrigBoard):
	signals = ("MinionGetsHealed", "HeroGetsHealed", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject.ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.addCardtoHand(numpyChoice(self.rngPool("Druid Spells")), self.keeper.ID)
			

class Trig_SpiritofLucentbark(Trig_Countdown):
	signals, counter = ("MinionGetsHealed", "HeroGetsHealed", ), 5
	def increment(self, number):
		return number
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject.ID == self.keeper.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if self.counter < 1:
			self.keeper.Game.transform(self.keeper, Lucentbark(self.keeper.Game, self.keeper.ID))
			

class Trig_ArcaneFletcher(TrigBoard):
	signals = ("MinionPlayed", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject != self.keeper and subject.ID == self.keeper.ID and number == 1

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.drawCertainCard(lambda card: card.category == "Spell")
		

class Trig_ThoridaltheStarsFury(TrigBoard):
	signals = ("HeroAttackedMinion", "HeroAttackedHero", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.keeper.ID and self.keeper.onBoard

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.Game.heroes[self.keeper.ID].getsEffect("Spell Damage", 2)
		ThoridaltheStarsFury_Effect(self.keeper.Game, self.keeper.ID).connect()
		

#卡德加在场时，连续从手牌或者牌库中召唤随从时，会一个一个的召唤，然后根据卡德加的效果进行双倍，如果双倍召唤提前填满了随从池，则后面的被招募随从就不再离开牌库或者手牌。，
#两个卡德加在场时，召唤数量会变成4倍。（卡牌的描述是翻倍）
#两个卡德加时，打出鱼人猎潮者，召唤一个1/1鱼人。会发现那个1/1鱼人召唤之后会在那个鱼人右侧再召唤一个（第一个卡德加的翻倍），然后第二个卡德加的翻倍触发，在最最左边的鱼人的右边召唤两个鱼人。
#当场上有卡德加的时候，灰熊守护者的亡语招募两个4费以下随从，第一个随从召唤出来时被翻倍，然后第二召唤出来的随从会出现在第一个随从的右边，然后翻倍，结果是后面出现的一对随从夹在第一对随从之间。
#对一次性召唤多个随从的机制的猜测应该是每一个新出来的随从都会盯紧之前出现的那个随从，然后召唤在那个随从的右边。如果之前召唤那个随从引起了新的随从召唤，无视之。
#目前没有在连续召唤随从之间出现随从提前离场的情况。上面提到的始终紧盯是可以实现的。
class GameRuleAura_Khadgar(GameRuleAura):
	def auraAppears(self): self.keeper.Game.effects[self.keeper.ID]["Summon x2"] += 1
	def auraDisappears(self): self.keeper.Game.effects[self.keeper.ID]["Summon x2"] -= 1


class Trig_MagicDartFrog(TrigBoard):
	signals = ("SpellBeenPlayed", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject.ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minions = self.keeper.Game.minionsAlive(3-self.keeper.ID)
		if minions: self.keeper.dealsDamage(numpyChoice(minions), 1)
		
		
class ManaAura_KirinTorTricaster(ManaAura):
	by = 1
	def applicable(self, target): target.ID == self.keeper.ID and target.category == "Spell"


class ManaAura_Kalecgos(ManaAura_1UsageEachTurn):
	def auraAppears(self):
		game, ID = self.keeper.Game, self.keeper.ID
		if game.turn == ID and game.Counters.numSpellsPlayedThisTurn[ID] < 1:
			self.aura = GameManaAura_Kalecgos(game, ID)
			game.Manas.CardAuras.append(self.aura)
			self.aura.auraAppears()
		add2ListinDict(self, game.trigsBoard[ID], "TurnStarts")


class Trig_NeverSurrender(Trig_Secret):
	signals = ("SpellPlayed", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.ID != self.keeper.Game.turn and subject.ID != self.keeper.ID and self.keeper.Game.minionsonBoard(self.keeper.ID) != []
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.AOE_GiveEnchant(self.keeper.Game.minionsonBoard(self.keeper.ID), 0, 2, name=NeverSurrender)
		

class GameRuleAura_CommanderRhyssa(GameRuleAura):
	def auraAppears(self): self.keeper.Game.effects[self.keeper.ID]["Secrets x2"] += 1
	def auraDisappears(self): self.keeper.Game.effects[self.keeper.ID]["Secrets x2"] -= 1


class Trig_Upgrade(TrigHand):
	signals = ("TurnEnds", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.inHand and ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.progress += 1
		
		
class Trig_CatrinaMuerte(TrigBoard):
	signals = ("TurnEnds", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.keeper
		minions = minion.Game.Counters.minionsDiedThisGame[minion.ID]
		if minions:
			minion.summon(numpyChoice(minions)(minion.Game, minion.ID))
			

class Trig_Vendetta(TrigHand):
	signals = ("CardLeavesHand", "CardEntersHand", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		#Only cards with a different class than your hero class will trigger this
		card = target[0] if signal == "CardEntersHand" else target
		return self.keeper.inHand and card.ID == self.keeper.ID and self.keeper.Game.heroes[self.keeper.ID].Class not in card.Class

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.Game.Manas.calcMana_Single(self.keeper)
		

class Trig_TakNozwhisker(TrigBoard):
	signals = ("CardShuffled", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		#Only triggers if the player is the initiator
		return self.keeper.onBoard and ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if isinstance(target, (list, numpy.ndarray)):
			for card in target:
				if self.keeper.Game.Hand_Deck.handNotFull(self.keeper.ID):
					Copy = card.selfCopy(self.keeper.ID, self.keeper)
					self.keeper.addCardtoHand(Copy, self.keeper.ID)
				else:
					break
		else: #A single card is shuffled.
			Copy = target.selfCopy(self.keeper.ID, self.keeper)
			self.keeper.addCardtoHand(Copy, self.keeper.ID)
			

class Trig_UnderbellyAngler(TrigBoard):
	signals = ("MinionBeenSummoned", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject.ID == self.keeper.ID and subject != self.keeper and "Murloc" in subject.race

	#Assume if Murloc gets controlled by the enemy, this won't trigger
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.addCardtoHand(numpyChoice(self.rngPool("Murlocs")), self.keeper.ID)
		
		
class ManaAura_Scargil(ManaAura):
	to = 1
	def applicable(self, target): target.ID == self.keeper.ID and "Murloc" in target.race


class Trig_JumboImp(TrigHand):
	signals = ("MinionDies", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.inHand and target.ID == self.keeper.ID and "Demon" in target.race

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		ManaMod(self.keeper, by=-1).applies()
		
		
class Trig_FelLordBetrug(TrigBoard):
	signals = ("CardDrawn", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and target[0].category == "Minion" and target[0].ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = target[0].selfCopy(self.keeper.ID, self.keeper)
		minion.trigsBoard.append(Trig_DieatEndofTurn(minion))
		self.keeper.summon(minion)
		if minion.onBoard: self.keeper.giveEnchant(minion, effGain="Rush", name=FelLordBetrug)
			

class Trig_ViciousScraphound(TrigBoard):
	signals = ("MinionTakesDmg", "HeroTakesDmg", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.keeper

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.giveHeroAttackArmor(self.keeper.ID, armor=number)
		
		
class Trig_Wrenchcalibur(TrigBoard):
	signals = ("HeroAttackedMinion", "HeroAttackedHero", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		#The target can't be dying to trigger this
		return subject == self.keeper.Game.heroes[self.keeper.ID] and self.keeper.onBoard

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		weapon = self.keeper
		weapon.shuffleintoDeck(Bomb(weapon.Game, 3-weapon.ID), enemyCanSee=True)
		
		
class Twinspell(Spell):
	twinspellCopy = None
	def cast(self, target=None, func=None):
		game, GUI = self.Game, self.Game.GUI
		# 由其他卡牌释放的法术结算相对玩家打出要简单，只需要结算过载，双生法术， 重复释放和使用后的扳机步骤即可。
		# 因为这个法术是由其他序列产生的，所有结束时不会进行死亡处理。
		repeatTimes = 2 if game.effects[self.ID]["Spells x2"] > 0 else 1
		# 多次选择的法术，如分岔路口等会有自己专有的cast方法。
		if not type(self).options: choice = 0
		else: choice = -1 if game.effects[self.ID]["Choose Both"] else numpyRandint(len(self.options))
		if self.needTarget(choice):
			if target and self.targetCorrect(target, choice): pass
			else:  # 如果没有选择目标或者目标实际上不可符合法术的要求，则需要重新选取
				if targets := self.findTargets(choice):
					if func and (preferedTargets := [obj for obj in targets if func(obj, choice)]):
						target = numpyChoice(preferedTargets)
					else: target = numpyChoice(targets)
				else: target = None
		else: target = None

		if GUI:
			GUI.showOffBoardTrig(self)
			GUI.resetSubTarColor(self, target)
		# 在法术要施放两次的情况下，第二次的目标仍然是第一次时随机决定的
		twinspellCopy = type(self).twinspellCopy
		for i in range(repeatTimes):
			if twinspellCopy: self.addCardtoHand(twinspellCopy, self.ID)
			# 指向性法术如果没有目标也可以释放，只是没有效果而已
			target = self.whenEffective(target, "byOthers", choice, posinHand=-2)
		# 使用后步骤，但是此时的扳机只会触发星界密使和风潮的状态移除。这个信号不是“使用一张xx牌之后”的扳机。
		game.sendSignal("SpellBeenCast", self.ID, self, target, 0, "byOthers", choice=0)
		return target

	def played(self, target=None, choice=0, mana=0, posinHand=-2, comment=""):
		game, ID, GUI = self.Game, self.ID, self.Game.GUI
		# 使用阶段
		# 判定该法术是否会因为风潮的光环存在而释放两次。发现的子游戏中不会两次触发，直接跳过
		repeatTimes = 2 if game.effects[ID]["Spells x2"] > 0 else 1
		if GUI: GUI.showOffBoardTrig(self)
		# 使用时步骤，触发伊利丹和紫罗兰老师等“每当你使用一张xx牌”的扳机
		game.sendSignal("SpellPlayed", ID, self, target if not isinstance(target, list) else None, mana, "", choice)
		game.sendSignal("Spellboost", ID, self, None, mana, "", choice)
		# 使用阶段结束，进行死亡结算。不处理胜负裁定。
		game.gathertheDead()  # At this point, the minion might be removed/controlled by Illidan/Juggler combo.
		# 进行目标的随机选择和扰咒术的目标改向判定。
		if target:
			holder = [target]
			game.sendSignal("SpellTargetDecision", ID, self, holder, 0, choice)
			target = holder[0]
			if GUI: GUI.resetSubTarColor(None, target)
			
		if target and target.ID == ID: game.Counters.spellsonFriendliesThisGame[ID].append(type(self))
		# Zentimo's effect actually an aura. As long as it's onBoard the moment the spell starts being resolved,
		# the effect will last even if Zentimo leaves board early.
		sweep, twinspellCopy = game.effects[ID]["Spells Sweep"], type(self).twinspellCopy
		# 没有法术目标，且法术本身是点了需要目标的选项的抉择法术或者需要目标的普通法术。
		for i in range(repeatTimes):
			#两次施放时都获得双生法术牌。
			if twinspellCopy: self.addCardtoHand(twinspellCopy, self.ID)
			# When the target is an onBoard minion, Zentimo is still onBoard and has adjacent minions next to it.
			if target and target.category == "Minion" and target.onBoard and sweep > 0 and game.neighbors2(target)[0]:
				neighbors = game.neighbors2(target)[0]
				# 只对中间的目标随从返回法术释放之后的新目标。
				# 用于变形等会让随从提前离场的法术。需要知道后面的再次生效目标。
				target.history["Spells Cast on This"].append(self.index)
				target = self.whenEffective(target, comment, choice, posinHand)
				for minion in neighbors:  # 对相邻的随从也释放该法术。
					minion.history["Spells Cast on This"].append(self.index)
					self.whenEffective(minion, comment, choice, posinHand)
			else:  # The target isn't minion or Zentimo can't apply to the situation. Be the target hero, minion onBoard or inDeck or None.
				# 如果目标不为空而且是在场上的随从，则这个随从的历史记录中会添加此法术的index。
				if target and (target.category == "Minion" or target.category == "Amulet") and target.onBoard:
					target.history["Spells Cast on This"].append(self.index)
				target = self.whenEffective(target, comment, choice, posinHand)

		# 仅触发风潮，星界密使等的光环移除扳机。“使用一张xx牌之后”的扳机不在这里触发，而是在Game的playSpell函数中结算。
		game.sendSignal("SpellBeenCast", game.turn, self, target, 0, "", choice)
		# 使用阶段结束，进行死亡结算，暂不处理胜负裁定。
		game.gathertheDead()  # At this point, the minion might be removed/controlled by Illidan/Juggler combo.
		# 完成阶段：
		# 如果法术具有回响，则将回响牌置入手牌中。因为没有牌可以让法术获得回响，所以可以直接在法术played()方法中处理echo
		# if "~Echo" in self.index:
		#	echoCard = type(minion)(self, game.turn)
		#	trig = Trig_Echo(echoCard)
		#	echoCard.trigsHand.append(trig)
		#	game.Hand_Deck.addCardtoHand(echoCard, ID)


class PotionVendor(Minion):
	Class, race, name = "Neutral", "", "Potion Vendor"
	mana, attack, health = 1, 1, 1
	index = "DALARAN~Neutral~Minion~1~1~1~~Potion Vendor~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Restore 2 Health to all friendly characters"
	name_CN = "药水商人"
	def text(self): return self.calcHeal(2)
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		heal = self.calcHeal(2)
		targets = [self.Game.heroes[self.ID]] + self.Game.minions[self.ID]
		self.AOE_Heal(targets, [heal] * len(targets))
		
		
class Toxfin(Minion):
	Class, race, name = "Neutral", "Murloc", "Toxfin"
	mana, attack, health = 1, 1, 2
	index = "DALARAN~Neutral~Minion~1~1~2~Murloc~Toxfin~Battlecry"
	requireTarget, effects, description = True, "", "Battlecry: Give a friendly Murloc Poisonous"
	name_CN = "毒鳍鱼人"
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and "Murloc" in target.race and target.ID == self.ID and target != self and target.onBoard
		
	def effCanTrig(self):
		self.effectViable = any("Murloc" in minion.race for minion in self.Game.minionsonBoard(self.ID))
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.giveEnchant(target, effGain="Poisonous", name=Toxfin)
		return target
		

class ArcaneServant(Minion):
	Class, race, name = "Neutral", "Elemental", "Arcane Servant"
	mana, attack, health = 2, 2, 3
	index = "DALARAN~Neutral~Minion~2~2~3~Elemental~Arcane Servant"
	requireTarget, effects, description = False, "", ""
	name_CN = "奥术仆从"
	
	
class DalaranLibrarian(Minion):
	Class, race, name = "Neutral", "", "Dalaran Librarian"
	mana, attack, health = 2, 2, 3
	index = "DALARAN~Neutral~Minion~2~2~3~~Dalaran Librarian~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Silences adjacent minions"
	name_CN = "达拉然图书管理员"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.onBoard:
			for minion in self.Game.neighbors2(self)[0]:
				minion.getsSilenced()
		
		
class EVILCableRat(Minion):
	Class, race, name = "Neutral", "Beast", "EVIL Cable Rat"
	mana, attack, health = 2, 1, 1
	index = "DALARAN~Neutral~Minion~2~1~1~Beast~EVIL Cable Rat~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Add a Lackey to your hand"
	name_CN = "怪盗布缆鼠"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.addCardtoHand(numpyChoice(Lackeys), self.ID)
		
		
class HenchClanHogsteed(Minion):
	Class, race, name = "Neutral", "Beast", "Hench-Clan Hogsteed"
	mana, attack, health = 2, 2, 1
	index = "DALARAN~Neutral~Minion~2~2~1~Beast~Hench-Clan Hogsteed~Rush~Deathrattle"
	requireTarget, effects, description = False, "Rush", "Rush. Deathrattle: Summon a 1/1 Murloc"
	name_CN = "荆棘帮斗猪"
	deathrattle = Death_HenchClanHogsteed


class HenchClanSquire(Minion):
	Class, race, name = "Neutral", "Murloc", "Hench-Clan Squire"
	mana, attack, health = 1, 1, 1
	index = "DALARAN~Neutral~Minion~1~1~1~Murloc~Hench-Clan Squire~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "荆棘帮马仔"
	
	
class ManaReservoir(Minion):
	Class, race, name = "Neutral", "Elemental", "Mana Reservoir"
	mana, attack, health = 2, 0, 6
	index = "DALARAN~Neutral~Minion~2~0~6~Elemental~Mana Reservoir~Spell Damage"
	requireTarget, effects, description = False, "Spell Damage", "Spell Damage +1"
	name_CN = "法力之池"
	
	
class SpellbookBinder(Minion):
	Class, race, name = "Neutral", "", "Spellbook Binder"
	mana, attack, health = 2, 3, 2
	index = "DALARAN~Neutral~Minion~2~3~2~~Spellbook Binder~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: If you have Spell Damage, draw a card"
	name_CN = "魔法订书匠"
	def effCanTrig(self):
		self.effectViable = self.countSpellDamage() > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.countSpellDamage() > 0: self.Game.Hand_Deck.drawCard(self.ID)
		
		
class SunreaverSpy(Minion):
	Class, race, name = "Neutral", "", "Sunreaver Spy"
	mana, attack, health = 2, 2, 3
	index = "DALARAN~Neutral~Minion~2~2~3~~Sunreaver Spy~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: If you control a Secret, gain +1/+1"
	name_CN = "夺日者间谍"
	
	def effCanTrig(self):
		self.effectViable = self.Game.Secrets.secrets[self.ID] != []
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Secrets.secrets[self.ID]: self.giveEnchant(self, 1, 1, name=SunreaverSpy)
		

class ZayleShadowCloak(Minion):
	Class, race, name = "Neutral", "", "Zayle, Shadow Cloak"
	mana, attack, health = 2, 3, 2
	index = "DALARAN~Neutral~Minion~2~3~2~~Zayle, Shadow Cloak~Legendary"
	requireTarget, effects, description = False, "", "You start the game with one of Zayle's EVIL Decks!"
	name_CN = "泽尔， 暗影斗篷"
	

class ArcaneWatcher(Minion):
	Class, race, name = "Neutral", "", "Arcane Watcher"
	mana, attack, health = 3, 5, 6
	index = "DALARAN~Neutral~Minion~3~5~6~~Arcane Watcher"
	requireTarget, effects, description = False, "Can't Attack", "Can't attack unless you have Spell Damage"
	name_CN = "奥术守望者"
	def hasSpellDamage(self):
		return self.Game.effects[self.ID]["Spell Damage"] > 0 \
				or any(minion.effects["Spell Damage"] > 0 for minion in self.Game.minions[self.ID])
				
	def canAttack(self):
		return self.actionable() and self.attack > 0 and self.effects["Frozen"] < 1 \
				and self.attChances_base + self.attChances_extra <= self.usageCount \
				and (self.silenced or self.hasSpellDamage())
				
				
class FacelessRager(Minion):
	Class, race, name = "Neutral", "", "Faceless Rager"
	mana, attack, health = 3, 5, 1
	index = "DALARAN~Neutral~Minion~3~5~1~~Faceless Rager~Battlecry"
	requireTarget, effects, description = True, "", "Battlecry: Copy a friendly minion's Health"
	name_CN = "无面暴怒者"
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.ID == self.ID and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.statReset(-1, target.health, source=type(self))
		return target
		
		
class FlightMaster(Minion):
	Class, race, name = "Neutral", "", "Flight Master"
	mana, attack, health = 3, 3, 4
	index = "DALARAN~Neutral~Minion~3~3~4~~Flight Master~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Summon a 2/2 Gryphon for each player"
	name_CN = "飞行管理员"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon(Gryphon(self.Game, self.ID))
		self.summon(Gryphon(self.Game, 3-self.ID))
		

class Gryphon(Minion):
	Class, race, name = "Neutral", "Beast", "Gryphon"
	mana, attack, health = 2, 2, 2
	index = "DALARAN~Neutral~Minion~2~2~2~Beast~Gryphon~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "狮鹫"
	
	
class HenchClanSneak(Minion):
	Class, race, name = "Neutral", "", "Hench-Clan Sneak"
	mana, attack, health = 3, 3, 3
	index = "DALARAN~Neutral~Minion~3~3~3~~Hench-Clan Sneak~Stealth"
	requireTarget, effects, description = False, "Stealth", "Stealth"
	name_CN = "荆棘帮小偷"
	
	
class MagicCarpet(Minion):
	Class, race, name = "Neutral", "", "Magic Carpet"
	mana, attack, health = 3, 1, 6
	index = "DALARAN~Neutral~Minion~3~1~6~~Magic Carpet"
	requireTarget, effects, description = False, "", "After you play a 1-Cost minion, give it +1 Attack and Rush"
	name_CN = "魔法飞毯"
	trigBoard = Trig_MagicCarpet		


class SpellwardJeweler(Minion):
	Class, race, name = "Neutral", "", "Spellward Jeweler"
	mana, attack, health = 3, 3, 4
	index = "DALARAN~Neutral~Minion~3~3~4~~Spellward Jeweler~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Your hero can't be targeted by spells or Hero Powers until your next turn"
	name_CN = "破咒珠宝师"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.effects[self.ID]["Evasive"] += 1
		self.Game.effects[self.ID]["Evasive2NextTurn"] += 1
		
#随机放言的法术不能对潜行随从施放，同时如果没有目标，则指向性法术整体失效，没有任何效果会结算


#随机放言的法术不能对潜行随从施放，同时如果没有目标，则指向性法术整体失效，没有任何效果会结算
class ArchmageVargoth(Minion):
	Class, race, name = "Neutral", "", "Archmage Vargoth"
	mana, attack, health = 4, 2, 6
	index = "DALARAN~Neutral~Minion~4~2~6~~Archmage Vargoth~Legendary"
	requireTarget, effects, description = False, "", "At the end of your turn, cast a spell you've cast this turn (targets chosen randomly)"
	name_CN = "大法师瓦格斯"
	trigBoard = Trig_ArchmageVargoth		


class Hecklebot(Minion):
	Class, race, name = "Neutral", "Mech", "Hecklebot"
	mana, attack, health = 4, 3, 8
	index = "DALARAN~Neutral~Minion~4~3~8~Mech~Hecklebot~Taunt~Battlecry"
	requireTarget, effects, description = False, "Taunt", "Taunt. Battlecry: Your opponent summons a minion from their deck"
	name_CN = "机械拷问者"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.space(3-self.ID) and \
			(indices := [i for i, card in enumerate(self.Game.Hand_Deck.decks[3-self.ID]) if card.category == "Minion"]):
			self.Game.summonfrom(numpyChoice(indices), 3-self.ID, -1, summoner=self, source='D')
		
		
class HenchClanHag(Minion):
	Class, race, name = "Neutral", "", "Hench-Clan Hag"
	mana, attack, health = 4, 3, 3
	index = "DALARAN~Neutral~Minion~4~3~3~~Hench-Clan Hag~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Summon two 1/1 Amalgams with all minions types"
	name_CN = "荆棘帮巫婆"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon([Amalgam(self.Game, self.ID) for _ in (0, 1)], relative="<>")
		

class Amalgam(Minion):
	Class, race, name = "Neutral", "Elemental,Mech,Demon,Murloc,Dragon,Beast,Pirate,Totem", "Amalgam"
	mana, attack, health = 1, 1, 1
	index = "DALARAN~Neutral~Minion~1~1~1~Elemental,Mech,Demon,Murloc,Dragon,Beast,Pirate,Totem~Amalgam~Uncollectible"
	requireTarget, effects, description = False, "", "This is an Elemental, Mech, Demon, Murloc, Dragon, Beast, Pirate and Totem"
	name_CN = "融合怪"
	
	
class PortalKeeper(Minion):
	Class, race, name = "Neutral", "Demon", "Portal Keeper"
	mana, attack, health = 4, 5, 2
	index = "DALARAN~Neutral~Minion~4~5~2~Demon~Portal Keeper~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Shuffle 3 Portals into your deck. When drawn, summon a 2/2 Demon with Rush"
	name_CN = "传送门守护者"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		portals = [FelhoundPortal(self.Game, self.ID) for _ in (0, 1, 2)]
		self.shuffleintoDeck(portals, enemyCanSee=True)
		

class FelhoundPortal(Spell):
	Class, school, name = "Neutral", "", "Felhound Portal"
	requireTarget, mana, effects = False, 2, ""
	index = "DALARAN~Neutral~Spell~2~~Felhound Portal~Casts When Drawn~Uncollectible"
	description = "Casts When Drawn. Summon a 2/2 Felhound with Rush"
	name_CN = "地狱犬传送门"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon(Felhound(self.Game, self.ID))
		

class Felhound(Minion):
	Class, race, name = "Neutral", "Demon", "Felhound"
	mana, attack, health = 2, 2, 2
	index = "DALARAN~Neutral~Minion~2~2~2~Demon~Felhound~Rush~Uncollectible"
	requireTarget, effects, description = False, "Rush", "Rush"
	name_CN = "地狱犬"


class ProudDefender(Minion):
	Class, race, name = "Neutral", "", "Proud Defender"
	mana, attack, health = 4, 2, 6
	index = "DALARAN~Neutral~Minion~4~2~6~~Proud Defender~Taunt"
	requireTarget, effects, description = False, "Taunt", "Taunt. Has +2 Attack while you have no other minions"
	name_CN = "骄傲的防御者"
	trigBoard = Trig_ProudDefender
	def statCheckResponse(self):
		if self.onBoard and not self.silenced and not self.Game.minionsonBoard(self.ID, self):
			self.attack += 2

			
class SoldierofFortune(Minion):
	Class, race, name = "Neutral", "Elemental", "Soldier of Fortune"
	mana, attack, health = 4, 5, 6
	index = "DALARAN~Neutral~Minion~4~5~6~Elemental~Soldier of Fortune"
	requireTarget, effects, description = False, "", "Whenever this minion attacks, give your opponent a coin"
	name_CN = "散财军士"
	trigBoard = Trig_SoldierofFortune		


class TravelingHealer(Minion):
	Class, race, name = "Neutral", "", "Traveling Healer"
	mana, attack, health = 4, 3, 2
	index = "DALARAN~Neutral~Minion~4~3~2~~Traveling Healer~Battlecry~Divine Shield"
	requireTarget, effects, description = True, "Divine Shield", "Divine Shield. Battlecry: Restore 3 Health."
	name_CN = "旅行医者"
	def text(self): return self.calcHeal(3)
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.restoresHealth(target, self.calcHeal(3))
		return target
		
		
class VioletSpellsword(Minion):
	Class, race, name = "Neutral", "", "Violet Spellsword"
	mana, attack, health = 4, 1, 6
	index = "DALARAN~Neutral~Minion~4~1~6~~Violet Spellsword~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Gain +1 Attack for each spell in your hand"
	name_CN = "紫罗兰 魔剑士"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if num := sum(card.category == "Spell" for card in self.Game.Hand_Deck.hands[self.ID]):
			self.giveEnchant(self, num, 0, name=VioletSpellsword)
		

class AzeriteElemental(Minion):
	Class, race, name = "Neutral", "Elemental", "Azerite Elemental"
	mana, attack, health = 5, 2, 7
	index = "DALARAN~Neutral~Minion~5~2~7~Elemental~Azerite Elemental"
	requireTarget, effects, description = False, "", "At the start of your turn, gain Spell Damage +2"
	name_CN = "艾泽里特元素"
	trigBoard = Trig_AzeriteElemental		


class BaristaLynchen(Minion):
	Class, race, name = "Neutral", "", "Barista Lynchen"
	mana, attack, health = 5, 4, 5
	index = "DALARAN~Neutral~Minion~5~4~5~~Barista Lynchen~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: Add a copy of each of your other Battlecry minions to your hand"
	name_CN = "咖啡师林彻"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		battlecryMinions = [minion for minion in self.Game.minions[self.ID] if "~Battlecry" in minion.index and minion != self]
		for minion in battlecryMinions:
			self.addCardtoHand(type(minion), self.ID)
		
		
class DalaranCrusader(Minion):
	Class, race, name = "Neutral", "", "Dalaran Crusader"
	mana, attack, health = 5, 5, 4
	index = "DALARAN~Neutral~Minion~5~5~4~~Dalaran Crusader~Divine Shield"
	requireTarget, effects, description = False, "Divine Shield", "Divine Shield"
	name_CN = "达拉然圣剑士"
	
	
class RecurringVillain(Minion):
	Class, race, name = "Neutral", "", "Recurring Villain"
	mana, attack, health = 5, 3, 6
	index = "DALARAN~Neutral~Minion~5~3~6~~Recurring Villain~Deathrattle"
	requireTarget, effects, description = False, "", "Deathrattle: If this minion has 4 or more Attack, resummon it"
	name_CN = "再生大盗"
	deathrattle = Death_RecurringVillain


class SunreaverWarmage(Minion):
	Class, race, name = "Neutral", "", "Sunreaver Warmage"
	mana, attack, health = 5, 4, 4
	index = "DALARAN~Neutral~Minion~5~4~4~~Sunreaver Warmage~Battlecry"
	requireTarget, effects, description = True, "", "Battlecry: If you're holding a spell costs (5) or more, deal 4 damage"
	name_CN = "夺日者战斗法师"
	
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.holdingSpellwith5CostorMore(self.ID)
		
	def needTarget(self, choice=0):
		return self.Game.Hand_Deck.holdingSpellwith5CostorMore(self.ID)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and self.Game.Hand_Deck.holdingSpellwith5CostorMore(self.ID):
			self.dealsDamage(target, 4)
		return target
		

class EccentricScribe(Minion):
	Class, race, name = "Neutral", "", "Eccentric Scribe"
	mana, attack, health = 6, 6, 4
	index = "DALARAN~Neutral~Minion~6~6~4~~Eccentric Scribe~Deathrattle"
	requireTarget, effects, description = False, "", "Deathrattle: Summon four 1/1 Vengeful Scrolls"
	name_CN = "古怪的铭文师"
	deathrattle = Death_EccentricScribe


class VengefulScroll(Minion):
	Class, race, name = "Neutral", "", "Vengeful Scroll"
	mana, attack, health = 1, 1, 1
	index = "DALARAN~Neutral~Minion~1~1~1~~Vengeful Scroll~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "复仇卷轴"
	
	
class MadSummoner(Minion):
	Class, race, name = "Neutral", "Demon", "Mad Summoner"
	mana, attack, health = 6, 4, 4
	index = "DALARAN~Neutral~Minion~6~4~4~Demon~Mad Summoner~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Fill each player's board with 1/1 Imps"
	name_CN = "疯狂召唤师"
	#假设是轮流为我方和对方召唤两个小鬼
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon([Imp_Shadows(self.Game, self.ID) for _ in range(7)])
		self.summon([Imp_Shadows(self.Game, 3-self.ID) for _ in range(7)], position=-1)
		

class Imp_Shadows(Minion):
	Class, race, name = "Neutral", "Demon", "Imp"
	mana, attack, health = 1, 1, 1
	index = "DALARAN~Neutral~Minion~1~1~1~Demon~Imp~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "小鬼"
	
	
class PortalOverfiend(Minion):
	Class, race, name = "Neutral", "Demon", "Portal Overfiend"
	mana, attack, health = 6, 5, 6
	index = "DALARAN~Neutral~Minion~6~5~6~Demon~Portal Overfiend~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Shuffle 3 Portals into your deck. When drawn, summon a 2/2 Demon with Rush"
	name_CN = "传送门大恶魔"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		portals = [FelhoundPortal(self.Game, self.ID) for _ in (0, 1, 2)]
		self.shuffleintoDeck(portals, enemyCanSee=True)
		
		
class Safeguard(Minion):
	Class, race, name = "Neutral", "Mech", "Safeguard"
	mana, attack, health = 6, 4, 5
	index = "DALARAN~Neutral~Minion~6~4~5~Mech~Safeguard~Taunt~Deathrattle"
	requireTarget, effects, description = False, "Taunt", "Taunt. Deathrattle: Summon a 0/5 Vault Safe with Taunt"
	name_CN = "机械保险箱"
	deathrattle = Death_Safeguard


class VaultSafe(Minion):
	Class, race, name = "Neutral", "Mech", "Vault Safe"
	mana, attack, health = 2, 0, 5
	index = "DALARAN~Neutral~Minion~2~0~5~Mech~Vault Safe~Taunt~Uncollectible"
	requireTarget, effects, description = False, "Taunt", "Taunt"
	name_CN = "保险柜"
	
	
class UnseenSaboteur(Minion):
	Class, race, name = "Neutral", "", "Unseen Saboteur"
	mana, attack, health = 6, 5, 6
	index = "DALARAN~Neutral~Minion~6~5~6~~Unseen Saboteur~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Your opponent casts a random spell from their hand (targets chosen randomly)"
	name_CN = "隐秘破坏者"
	#不知道是否会拉出不能使用的法术
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if indices := [i for i, card in enumerate(self.Game.Hand_Deck.hands[3-self.ID]) if card.category == "Spell"]:
			self.Game.Hand_Deck.extractfromHand(numpyChoice(indices), 3-self.ID)[0].cast()
		
		
class VioletWarden(Minion):
	Class, race, name = "Neutral", "", "Violet Warden"
	mana, attack, health = 6, 4, 7
	index = "DALARAN~Neutral~Minion~6~4~7~~Violet Warden~Taunt~Spell Damage"
	requireTarget, effects, description = False, "Taunt,Spell Damage", "Taunt, Spell Damage +1"
	name_CN = "紫罗兰典狱官"
	

class ChefNomi(Minion):
	Class, race, name = "Neutral", "", "Chef Nomi"
	mana, attack, health = 7, 6, 6
	index = "DALARAN~Neutral~Minion~7~6~6~~Chef Nomi~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: If your deck is empty, summon six 6/6 Greasefire Elementals"
	name_CN = "大厨诺米"
	
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.decks[self.ID] == []
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if not self.Game.Hand_Deck.decks[self.ID]:
			self.summon([GreasefireElemental(self.Game, self.ID) for i in range(7)], relative="<>")
		
class GreasefireElemental(Minion):
	Class, race, name = "Neutral", "Elemental", "Greasefire Elemental"
	mana, attack, health = 6, 6, 6
	index = "DALARAN~Neutral~Minion~6~6~6~Elemental~Greasefire Elemental~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "猛火元素"
	
	
class ExoticMountseller(Minion):
	Class, race, name = "Neutral", "", "Exotic Mountseller"
	mana, attack, health = 7, 5, 8
	index = "DALARAN~Neutral~Minion~7~5~8~~Exotic Mountseller"
	requireTarget, effects, description = False, "", "Whenever you cast a spell, summon a random 3-Cost Beast"
	name_CN = "特殊坐骑商人"
	trigBoard = Trig_ExoticMountseller
	poolIdentifier = "3-Cost Beasts to Summon"
	@classmethod
	def generatePool(cls, pools):
		return "3-Cost Beasts to Summon", [value for key, value in pools.MinionswithRace["Beast"].items() if key.split('~')[3] == "3"]
		


class TunnelBlaster(Minion):
	Class, race, name = "Neutral", "", "Tunnel Blaster"
	mana, attack, health = 7, 3, 7
	index = "DALARAN~Neutral~Minion~7~3~7~~Tunnel Blaster~Taunt~Deathrattle"
	requireTarget, effects, description = False, "Taunt", "Taunt. Deathrattle: Deal 3 damage to all minions"
	name_CN = "坑道爆破手"
	deathrattle = Death_TunnelBlaster


class UnderbellyOoze(Minion):
	Class, race, name = "Neutral", "", "Underbelly Ooze"
	mana, attack, health = 7, 3, 5
	index = "DALARAN~Neutral~Minion~7~3~5~~Underbelly Ooze"
	requireTarget, effects, description = False, "", "After this minion survives damage, summon a copy of it"
	name_CN = "下水道软泥怪"
	trigBoard = Trig_UnderbellyOoze		


class Batterhead(Minion):
	Class, race, name = "Neutral", "", "Batterhead"
	mana, attack, health = 8, 3, 12
	index = "DALARAN~Neutral~Minion~8~3~12~~Batterhead~Rush"
	requireTarget, effects, description = False, "Rush", "Rush. After this attacks and kills a minion, it may attack again"
	name_CN = "莽头食人魔"
	trigBoard = Trig_Batterhead		


class HeroicInnkeeper(Minion):
	Class, race, name = "Neutral", "", "Heroic Innkeeper"
	mana, attack, health = 8, 4, 4
	index = "DALARAN~Neutral~Minion~8~4~4~~Heroic Innkeeper~Taunt~Battlecry"
	requireTarget, effects, description = False, "Taunt", "Taunt. Battlecry: Gain +2/+2 for each other friendly minion"
	name_CN = "霸气的旅店老板娘"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.onBoard or self.inHand:
			if buff := 2 * len(self.Game.minionsonBoard(self.ID, self)): self.giveEnchant(self, buff, buff, name=HeroicInnkeeper)
		
		
class JepettoJoybuzz(Minion):
	Class, race, name = "Neutral", "", "Jepetto Joybuzz"
	mana, attack, health = 8, 6, 6
	index = "DALARAN~Neutral~Minion~8~6~6~~Jepetto Joybuzz~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: Draw 2 minions from your deck. Set their Attack, Health, and Cost to 1"
	name_CN = "耶比托·乔巴斯"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for _ in (0, 1):
			card, mana, entersHand = self.drawCertainCard(conditional=lambda card: card.category == "Minion")
			if not card: break
			elif entersHand:
				card.statReset(1, 1, source=type(self))
				ManaMod(card, to=1).applies()
		

class WhirlwindTempest(Minion):
	Class, race, name = "Neutral", "Elemental", "Whirlwind Tempest"
	mana, attack, health = 8, 6, 6
	index = "DALARAN~Neutral~Minion~8~6~6~Elemental~Whirlwind Tempest"
	requireTarget, effects, description = False, "", "Your Windfury minions have Mega Windfury"
	name_CN = "暴走旋风"
	aura = Aura_WhirlwindTempest


class BurlyShovelfist(Minion):
	Class, race, name = "Neutral", "", "Burly Shovelfist"
	mana, attack, health = 9, 9, 9
	index = "DALARAN~Neutral~Minion~9~9~9~~Burly Shovelfist~Rush"
	requireTarget, effects, description = False, "Rush", "Rush"
	name_CN = "推土壮汉"
	
	
class ArchivistElysiana(Minion):
	Class, race, name = "Neutral", "", "Archivist Elysiana"
	mana, attack, health = 9, 7, 7
	index = "DALARAN~Neutral~Minion~9~7~7~~Archivist Elysiana~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: Discover 5 cards. Replace your deck with 2 copies of each"
	name_CN = "档案员艾丽西娜"
	poolIdentifier = "Cards as Druid"
	@classmethod
	def generatePool(cls, pools):
		return ["Cards as "+Class for Class in pools.Classes], [list(pools.ClassCards[Class].values())+list(pools.NeutralCards.values()) for Class in pools.Classes]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.ID == self.Game.turn: self.Game.Hand_Deck.extractfromDeck(None, self.ID, True)
		for i in range(5):
			self.discoverandGenerate(ArchivistElysiana, comment, poolFunc=lambda : self.rngPool("Cards as "+classforDiscover(self)))
		numpyShuffle(self.Game.Hand_Deck.decks[self.ID]) #Need to shuffle the discovered cards
		
	def put2CardsintoDeck(self, cardType):
		ownDeck = self.Game.Hand_Deck.decks[self.ID]
		ownDeck += [cardType(self.Game, self.ID) for _ in (0, 1)]
		ownDeck[-2].entersDeck()
		ownDeck[-1].entersDeck()
		
	def discoverDecided(self, option, case, info_RNGSync=None, info_GUISync=None):
		self.handleDiscoverGeneratedCard(option, case, info_RNGSync, info_GUISync,
										 func=lambda cardType, card: ArchivistElysiana.put2CardsintoDeck(self, cardType))
		

class BigBadArchmage(Minion):
	Class, race, name = "Neutral", "", "Big Bad Archmage"
	mana, attack, health = 10, 6, 6
	index = "DALARAN~Neutral~Minion~10~6~6~~Big Bad Archmage"
	requireTarget, effects, description = False, "", "At the end of your turn, summon a random 6-Cost minion"
	name_CN = "恶狼大法师"
	trigBoard = Trig_BigBadArchmage		
	poolIdentifier = "6-Cost Minions to Summon"
	@classmethod
	def generatePool(cls, pools):
		return "6-Cost Minions to Summon", list(pools.MinionsofCost[6].values())
		
		
class Acornbearer(Minion):
	Class, race, name = "Druid", "", "Acornbearer"
	mana, attack, health = 1, 2, 1
	index = "DALARAN~Druid~Minion~1~2~1~~Acornbearer~Deathrattle"
	requireTarget, effects, description = False, "", "Deathrattle: Add two 1/1 Squirrels to your hand"
	name_CN = "橡果人"
	deathrattle = Death_Acornbearer

class Squirrel_Shadows(Minion):
	Class, race, name = "Druid", "Beast", "Squirrel"
	mana, attack, health = 1, 1, 1
	index = "DALARAN~Druid~Minion~1~1~1~Beast~Squirrel~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "松鼠"


class PiercingThorns(Spell):
	Class, school, name = "Druid", "Nature", "Piercing Thorns"
	requireTarget, mana, effects = True, 1, ""
	index = "DALARAN~Druid~Spell~1~Nature~Piercing Thorns~Uncollectible"
	description = "Deal 2 damage to a minion"
	name_CN = "利刺荆棘"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard
		
	def text(self): return self.calcDamage(2)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.dealsDamage(target, self.calcDamage(2))
		return target
		
class HealingBlossom(Spell):
	Class, school, name = "Druid", "Nature", "Healing Blossom"
	requireTarget, mana, effects = True, 1, ""
	index = "DALARAN~Druid~Spell~1~Nature~Healing Blossom~Uncollectible"
	description = "Restore 5 Health"
	name_CN = "愈合之花"
	def text(self): return self.calcHeal(5)
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.restoresHealth(target, self.calcHeal(5))
		return target
		
class PiercingThorns_Option(Option):
	name, description = "Piercing Thorns", "Deal 2 damage to minion"
	mana, attack, health = 1, -1, -1
	spell = PiercingThorns
	def available(self):
		return self.keeper.selectableMinionExists(0)

class HealingBlossom_Option(Option):
	name, description = "Healing Blossom", "Restore 5 Health"
	mana, attack, health = 1, -1, -1
	spell = HealingBlossom
	def available(self):
		return self.keeper.selectableCharacterExists(1)

class CrystalPower(Spell):
	Class, school, name = "Druid", "Nature", "Crystal Power"
	requireTarget, mana, effects = True, 1, ""
	index = "DALARAN~Druid~Spell~1~Nature~Crystal Power~Choose One"
	description = "Choose One - Deal 2 damage to a minion; or Restore 5 Health"
	name_CN = "水晶之力"
	options = (PiercingThorns_Option, HealingBlossom_Option)
	def available(self):
		return self.selectableCharacterExists(1)
		
	#available() only needs to check selectableCharacterExists
	def targetCorrect(self, target, choice=0):
		return target.onBoard and (target.category == "Minion" or (choice != 0 and target.category == "Hero"))
		
	def text(self): return "%d, %d"%(self.calcDamage(2), self.calcHeal(5))
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			if choice < 0: #如果目标是一个随从，先对其造成伤害，如果目标存活，才能造成治疗
				if target.category == "Minion": #只会对随从造成伤害
					self.dealsDamage(target, self.calcDamage(2))
				if target.health > 0 and target.dead == False: #法术造成伤害之后，那个随从必须活着才能接受治疗，不然就打2无论如何都变得没有意义
					self.restoresHealth(target, self.calcHeal(5))
			elif choice == 0:
				if target.category == "Minion": self.dealsDamage(target, self.calcDamage(2))
			else: #Choice == 1
				self.restoresHealth(target, self.calcHeal(5))
		return target
		
		
class CrystalsongPortal(Spell):
	Class, school, name = "Druid", "Nature", "Crystalsong Portal"
	requireTarget, mana, effects = False, 2, ""
	index = "DALARAN~Druid~Spell~2~Nature~Crystalsong Portal"
	description = "Discover a Druid minion. If your hand has no minions, keep all 3"
	name_CN = "晶歌传送门"
	poolIdentifier = "Druid Minions"
	@classmethod
	def generatePool(cls, pools):
		return "Druid Minions", [value for key, value in pools.ClassCards["Druid"].items() if "~Minion~" in key]
		
	def effCanTrig(self):
		return all(card.category != "Minion" for card in self.Game.Hand_Deck.hands[self.ID])
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if all(card.category != "Minion" for card in curGame.Hand_Deck.hands[self.ID]):
				self.addCardtoHand(numpyChoice(self.rngPool("Druid Minions"), 3, replace=False), self.ID)
			else:
				self.discoverandGenerate(CrystalsongPortal, comment, lambda : self.rngPool("Druid Minions"))
		
		
class DreamwayGuardians(Spell):
	Class, school, name = "Druid", "", "Dreamway Guardians"
	requireTarget, mana, effects = False, 2, ""
	index = "DALARAN~Druid~Spell~2~~Dreamway Guardians"
	description = "Summon two 1/2 Dryads with Lifesteal"
	name_CN = "守卫梦境之路"
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon([CrystalDryad(self.Game, self.ID) for _ in (0, 1)])
		
class CrystalDryad(Minion):
	Class, race, name = "Druid", "", "Crystal Dryad"
	mana, attack, health = 1, 1, 2
	index = "DALARAN~Druid~Minion~1~1~2~~Crystal Dryad~Lifesteal~Uncollectible"
	requireTarget, effects, description = False, "Lifesteal", "Lifesteal"
	name_CN = "水晶树妖"
	
	
class KeeperStalladris(Minion):
	Class, race, name = "Druid", "", "Keeper Stalladris"
	mana, attack, health = 2, 2, 3
	index = "DALARAN~Druid~Minion~2~2~3~~Keeper Stalladris~Legendary"
	requireTarget, effects, description = False, "", "After you cast a Choose One spell, add copies of both choices to your hand"
	name_CN = "守护者斯塔拉蒂斯"
	trigBoard = Trig_KeeperStalladris		


class Lifeweaver(Minion):
	Class, race, name = "Druid", "", "Lifeweaver"
	mana, attack, health = 3, 2, 5
	index = "DALARAN~Druid~Minion~3~2~5~~Lifeweaver"
	requireTarget, effects, description = False, "", "Whenever you restore Health, add a random Druid spell to your hand"
	name_CN = "织命者"
	poolIdentifier = "Druid Spells"
	@classmethod
	def generatePool(cls, pools):
		return "Druid Spells", [value for key, value in pools.ClassCards["Druid"].items() if "~Spell~" in key]
		
	trigBoard = Trig_Lifeweaver			


class CrystalStag(Minion):
	Class, race, name = "Druid", "Beast", "Crystal Stag"
	mana, attack, health = 5, 4, 4
	index = "DALARAN~Druid~Minion~5~4~4~Beast~Crystal Stag~Rush~Battlecry"
	requireTarget, effects, description = False, "Rush", "Rush. Battlecry: If you've restored 5 Health this game, summon a copy of this"
	name_CN = "晶角雄鹿"
	
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.healthRestoredThisGame[self.ID] > 4
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Counters.healthRestoredThisGame[self.ID] > 4:
			self.summon(self.selfCopy(self.ID, self))


class BlessingoftheAncients2(Twinspell):
	Class, school, name = "Druid", "Nature", "Blessing of the Ancients"
	requireTarget, mana, effects = False, 3, ""
	index = "DALARAN~Druid~Spell~3~Nature~Blessing of the Ancients~Uncollectible"
	description = "Give your minions +1/+1"
	name_CN = "远古祝福"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.AOE_GiveEnchant(self.Game.minionsonBoard(self.ID), 1, 1, name=BlessingoftheAncients)

class BlessingoftheAncients(BlessingoftheAncients2):
	index = "DALARAN~Druid~Spell~3~Nature~Blessing of the Ancients~Twinspell"
	description = "Twinspell. Give your minions +1/+1"
	twinspellCopy = BlessingoftheAncients2

	
class Lucentbark(Minion):
	Class, race, name = "Druid", "", "Lucentbark"
	mana, attack, health = 8, 4, 8
	index = "DALARAN~Druid~Minion~8~4~8~~Lucentbark~Taunt~Deathrattle~Legendary"
	requireTarget, effects, description = False, "Taunt", "Taunt. Deathrattle: Go dormant. Restore 5 Health to awaken this minion"
	name_CN = "卢森巴克"
	deathrattle = Death_Lucentbark

class SpiritofLucentbark(Dormant):
	Class, school, name = "Druid", "", "Spirit of Lucentbark"
	description = "Restore 5 Health to awaken"
	name_CN = "卢森巴克之魂"
	trigBoard = Trig_SpiritofLucentbark


class TheForestsAid2(Twinspell):
	Class, school, name = "Druid", "Nature", "The Forest's Aid"
	requireTarget, mana, effects = False, 8, ""
	index = "DALARAN~Druid~Spell~8~Nature~The Forest's Aid~Uncollectible"
	description = "Summon five 2/2 Treants"
	name_CN = "森林的援助"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon([Treant_Shadows(self.Game, self.ID) for i in range(5)])

class TheForestsAid(TheForestsAid2):
	index = "DALARAN~Druid~Spell~8~Nature~The Forest's Aid~Twinspell"
	description = "Twinspell. Summon five 2/2 Treants"
	twinspellCopy = TheForestsAid2

class Treant_Shadows(Minion):
	Class, race, name = "Druid", "", "Treant"
	mana, attack, health = 2, 2, 2
	index = "DALARAN~Druid~Minion~2~2~2~~Treant~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "树人"
	


class RapidFire2(Twinspell):
	Class, school, name = "Hunter", "", "Rapid Fire"
	requireTarget, mana, effects = True, 1, ""
	index = "DALARAN~Hunter~Spell~1~~Rapid Fire~Uncollectible"
	description = "Deal 1 damage"
	name_CN = "急速射击"
	def text(self): return self.calcDamage(1)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.dealsDamage(target, self.calcDamage(1))
		return target

class RapidFire(RapidFire2):
	index = "DALARAN~Hunter~Spell~1~~Rapid Fire~Twinspell"
	description = "Twinspell. Deal 1 damage"
	twinspellCopy = RapidFire2


class Shimmerfly(Minion):
	Class, race, name = "Hunter", "Beast", "Shimmerfly"
	mana, attack, health = 1, 1, 1
	index = "DALARAN~Hunter~Minion~1~1~1~Beast~Shimmerfly~Deathrattle"
	requireTarget, effects, description = False, "", "Deathrattle: Add a random Hunter spell to your hand"
	name_CN = "闪光蝴蝶"
	deathrattle = Death_Shimmerfly
	poolIdentifier = "Hunter Spells"
	@classmethod
	def generatePool(cls, pools):
		return "Hunter Spells", [value for key, value in pools.ClassCards["Hunter"].items() if "~Spell~" in key]


class NineLives(Spell):
	Class, school, name = "Hunter", "", "Nine Lives"
	requireTarget, mana, effects = False, 3, ""
	index = "DALARAN~Hunter~Spell~3~~Nine Lives"
	description = "Discover a friendly Deathrattle minion that died this game. Also trigger its Deathrattle"
	name_CN = "九命兽魂"
	def decidePool(self):
		return [card for card in self.Game.Counters.minionsDiedThisGame[self.ID] if "~Deathrattle" in card.index]
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverandGenerate_Types(NineLives, comment, typePoolFunc=lambda : NineLives.decidePool(self))
		
	def addDiscoveredCard_TrigDeathrattle(self, card):
		self.addCardtoHand(card, self.ID, byDiscover=True)
		if card.inHand:
			for trig in card.deathrattles: trig.trig("TrigDeathrattle", self.ID, None, card, card.attack, "")
			
	def discoverDecided(self, option, case, info_RNGSync=None, info_GUISync=None):
		self.handleDiscoverGeneratedCard(option, case, info_RNGSync, info_GUISync,
										 func=lambda cardType, card: NineLives.addDiscoveredCard_TrigDeathrattle(self, option))
		
			
class Ursatron(Minion):
	Class, race, name = "Hunter", "Mech", "Ursatron"
	mana, attack, health = 3, 3, 3
	index = "DALARAN~Hunter~Minion~3~3~3~Mech~Ursatron~Deathrattle"
	requireTarget, effects, description = False, "", "Deathrattle: Draw a Mech from your deck"
	name_CN = "机械巨熊"
	deathrattle = Death_Ursatron


class ArcaneFletcher(Minion):
	Class, race, name = "Hunter", "", "Arcane Fletcher"
	mana, attack, health = 4, 3, 3
	index = "DALARAN~Hunter~Minion~4~3~3~~Arcane Fletcher"
	requireTarget, effects, description = False, "", "Whenever you play a 1-Cost minion, draw a spell from your deck"
	name_CN = "奥术弓箭手"
	trigBoard = Trig_ArcaneFletcher		


class MarkedShot(Spell):
	Class, school, name = "Hunter", "", "Marked Shot"
	requireTarget, mana, effects = True, 4, ""
	index = "DALARAN~Hunter~Spell~4~~Marked Shot"
	description = "Deal 4 damage to a minion. Discover a Spell"
	name_CN = "标记射击"
	poolIdentifier = "Hunter Spells"
	@classmethod
	def generatePool(cls, pools):
		return [Class+" Spells" for Class in pools.Classes], \
				[[value for key, value in pools.ClassCards[Class].items() if "~Spell~" in key] for Class in pools.Classes]
				
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard
		
	def text(self): return self.calcDamage(4)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.dealsDamage(target, self.calcDamage(4))
			self.discoverandGenerate(MarkedShot, comment, lambda: self.rngPool("Hunter Spells"))
		return target
	
		
class HuntingParty(Spell):
	Class, school, name = "Hunter", "", "Hunting Party"
	requireTarget, mana, effects = False, 5, ""
	index = "DALARAN~Hunter~Spell~5~~Hunting Party"
	description = "Copy all Beasts in your hand"
	name_CN = "狩猎盛宴"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Hand_Deck.handNotFull(self.ID):
			if copies := [card.selfCopy(self.ID, self) for card in self.Game.Hand_Deck.hands[self.ID] \
				if "Beast" in card.race]:
				self.addCardtoHand(copies, self.ID)
		

class Oblivitron(Minion):
	Class, race, name = "Hunter", "Mech", "Oblivitron"
	mana, attack, health = 6, 3, 4
	index = "DALARAN~Hunter~Minion~6~3~4~Mech~Oblivitron~Deathrattle~Legendary"
	requireTarget, effects, description = False, "", "Deathrattle: Summon a Mech from your hand and trigger its Deathrattle"
	name_CN = "湮灭战车"
	deathrattle = Death_Oblivitron


class UnleashtheBeast2(Twinspell):
	Class, school, name = "Hunter", "", "Unleash the Beast"
	requireTarget, mana, effects = False, 6, ""
	index = "DALARAN~Hunter~Spell~6~~Unleash the Beast~Uncollectible"
	description = "Summon a 5/5 Wyvern with Rush"
	name_CN = "猛兽出笼"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon(Wyvern(self.Game, self.ID))

class UnleashtheBeast(UnleashtheBeast2):
	index = "DALARAN~Hunter~Spell~6~~Unleash the Beast~Twinspell"
	description = "Twinspell. Summon a 5/5 Wyvern with Rush"
	twinspellCopy = UnleashtheBeast2

class Wyvern(Minion):
	Class, race, name = "Hunter", "Beast", "Wyvern"
	mana, attack, health = 5, 5, 5
	index = "DALARAN~Hunter~Minion~5~5~5~Beast~Wyvern~Rush~Uncollectible"
	requireTarget, effects, description = False, "Rush", "Rush"
	name_CN = "双足飞龙"
	
	
class VereesaWindrunner(Minion):
	Class, race, name = "Hunter", "", "Vereesa Windrunner"
	mana, attack, health = 7, 5, 6
	index = "DALARAN~Hunter~Minion~7~5~6~~Vereesa Windrunner~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: Equip Thori'dal, the Stars' Fury"
	name_CN = "温蕾萨·风行者"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.equipWeapon(ThoridaltheStarsFury(self.Game, self.ID))

class ThoridaltheStarsFury(Weapon):
	Class, name, description = "Hunter", "Thori'dal, the Stars' Fury", "After your hero attacks, gain Spell Damage +2 this turn"
	mana, attack, durability, effects = 3, 2, 3, ""
	index = "DALARAN~Hunter~Weapon~3~2~3~Thori'dal, the Stars' Fury~Legendary~Uncollectible"
	name_CN = "索利达尔，群星之怒"
	trigBoard = Trig_ThoridaltheStarsFury


class RayofFrost2(Twinspell):
	Class, school, name = "Mage", "Frost", "Ray of Frost"
	requireTarget, mana, effects = True, 1, ""
	index = "DALARAN~Mage~Spell~1~Frost~Ray of Frost~Uncollectible"
	description = "Freeze a minion. If it's already Frozen, deal 2 damage to it"
	name_CN = "霜冻射线"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard
		
	def text(self): return self.calcDamage(2)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			if target.effects["Frozen"]: self.dealsDamage(target, self.calcDamage(2))
			else: self.freeze(target)
		return target

class RayofFrost(RayofFrost2):
	index = "DALARAN~Mage~Spell~1~Frost~Ray of Frost~Twinspell"
	description = "Twinspell. Freeze a minion. If it's already Frozen, deal 2 damage to it"
	twinSpellCopy = RayofFrost2

#卡德加在场时，连续从手牌或者牌库中召唤随从时，会一个一个的召唤，然后根据卡德加的效果进行双倍，如果双倍召唤提前填满了随从池，则后面的被招募随从就不再离开牌库或者手牌。，
#两个卡德加在场时，召唤数量会变成4倍。（卡牌的描述是翻倍）
#两个卡德加时，打出鱼人猎潮者，召唤一个1/1鱼人。会发现那个1/1鱼人召唤之后会在那个鱼人右侧再召唤一个（第一个卡德加的翻倍），然后第二个卡德加的翻倍触发，在最最左边的鱼人的右边召唤两个鱼人。
#当场上有卡德加的时候，灰熊守护者的亡语招募两个4费以下随从，第一个随从召唤出来时被翻倍，然后第二召唤出来的随从会出现在第一个随从的右边，然后翻倍，结果是后面出现的一对随从夹在第一对随从之间。
#对一次性召唤多个随从的机制的猜测应该是每一个新出来的随从都会盯紧之前出现的那个随从，然后召唤在那个随从的右边。如果之前召唤那个随从引起了新的随从召唤，无视之。
#目前没有在连续召唤随从之间出现随从提前离场的情况。上面提到的始终紧盯是可以实现的。
class Khadgar(Minion):
	Class, race, name = "Mage", "", "Khadgar"
	mana, attack, health = 2, 2, 2
	index = "DALARAN~Mage~Minion~2~2~2~~Khadgar~Legendary"
	requireTarget, effects, description = False, "", "Your cards that summon minions summon twice as many"
	name_CN = "卡德加"
	aura = GameRuleAura_Khadgar

		
class MagicDartFrog(Minion):
	Class, race, name = "Mage", "Beast", "Magic Dart Frog"
	mana, attack, health = 2, 1, 3
	index = "DALARAN~Mage~Minion~2~1~3~Beast~Magic Dart Frog"
	requireTarget, effects, description = False, "", "After you cast a spell, deal 1 damage to a random enemy minion"
	name_CN = "魔法蓝蛙"
	trigBoard = Trig_MagicDartFrog		


class MessengerRaven(Minion):
	Class, race, name = "Mage", "Beast", "Messenger Raven"
	mana, attack, health = 3, 3, 2
	index = "DALARAN~Mage~Minion~3~3~2~Beast~Messenger Raven~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Discover a Mage minion"
	name_CN = "渡鸦信使"
	poolIdentifier = "Mage Minions"
	@classmethod
	def generatePool(cls, pools):
		return "Mage Minions", [value for key, value in pools.ClassCards["Mage"].items() if "~Minion~" in key]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverandGenerate(MessengerRaven, comment, lambda: self.rngPool("Mage Minions"))
		return target
	
		
class MagicTrick(Spell):
	Class, school, name = "Mage", "Arcane", "Magic Trick"
	requireTarget, mana, effects = False, 1, ""
	index = "DALARAN~Mage~Spell~1~Arcane~Magic Trick"
	description = "Discover a spell that costs (3) or less"
	name_CN = "魔术戏法"
	poolIdentifier = "Spells 3-Cost or less as Mage"
	@classmethod
	def generatePool(cls, pools):
		return ["Spells 3-Cost or less as %s"%Class for Class in pools.Classes], \
				[[value for key, value in pools.ClassCards[Class].items() if "~Spell~" in key and int(key.split('~')[3]) < 4] for Class in pools.Classes]
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverandGenerate(MagicTrick, comment, lambda: self.rngPool("Spells 3-Cost or less as "+classforDiscover(self)))
		

class ConjurersCalling2(Twinspell):
	Class, school, name = "Mage", "Arcane", "Conjurer's Calling"
	requireTarget, mana, effects = True, 4, ""
	index = "DALARAN~Mage~Spell~4~Arcane~Conjurer's Calling~Uncollectible"
	description = "Destroy a minion. Summon 2 minions of the same Cost to replace it"
	name_CN = "咒术师的召唤"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			game = self.Game
			cost = type(target).mana
			key = "%d-Cost Minions to Summon" % cost
			targetID, position = target.ID, target.pos
			if target.onBoard:
				game.killMinion(self, target)
			elif target.inHand:
				self.Game.Hand_Deck.discard(target)  #如果随从在手牌中则将其丢弃
			#强制死亡需要在此插入死亡结算，并让随从离场
			game.gathertheDead()
			minions = numpyChoice(self.rngPool(key), 2, replace=True)
			if position == 0:
				pos = (-1, ">")  #Summon to the leftmost
			#如果目标之前是第4个(position=3)，则场上最后只要有3个随从或者以下，就会召唤到最右边。
			#如果目标不在场上或者是第二次生效时已经死亡等被初始化，则position=-2会让新召唤的随从在场上最右边。
			elif position < 0 or position >= len(game.minionsonBoard(targetID)):
				pos = (-1, ">>")
			else:
				pos = (position, ">")
			self.summon([minion(game, target.ID) for minion in minions], position=pos)
		return target

class ConjurersCalling(ConjurersCalling2):
	index = "DALARAN~Mage~Spell~4~Arcane~Conjurer's Calling~Twinspell"
	description = "Twinspell. Destroy a minion. Summon 2 minions of the same Cost to replace it"
	twinSpellCopy = ConjurersCalling2
	poolIdentifier = "1-Cost Minions to Summon"
	@classmethod
	def generatePool(cls, pools):
		return ["%d-Cost Minions to Summon" % cost for cost in pools.MinionsofCost.keys()], \
			   [list(pools.MinionsofCost[cost].values()) for cost in pools.MinionsofCost.keys()]


class KirinTorTricaster(Minion):
	Class, race, name = "Mage", "", "Kirin Tor Tricaster"
	mana, attack, health = 4, 3, 3
	index = "DALARAN~Mage~Minion~4~3~3~~Kirin Tor Tricaster"
	requireTarget, effects, description = False, "Spell Damage_3", "Spell Damage +3. Your spells cost (1) more"
	name_CN = "肯瑞托三修法师"
	aura = ManaAura_KirinTorTricaster

		
class ManaCyclone(Minion):
	Class, race, name = "Mage", "Elemental", "Mana Cyclone"
	mana, attack, health = 2, 2, 2
	index = "DALARAN~Mage~Minion~2~2~2~Elemental~Mana Cyclone~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: For each spell you've cast this turn, add a random Mage spell to your hand"
	name_CN = "法力飓风"
	poolIdentifier = "Mage Spells"
	@classmethod
	def generatePool(cls, pools):
		return "Mage Spells", [value for key, value in pools.ClassCards["Mage"].items() if "~Spell~" in key]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		num = min(self.Game.Hand_Deck.spaceinHand(self.ID), self.Game.Counters.numSpellsPlayedThisTurn[self.ID])
		spells = tuple(numpyChoice(self.rngPool("Mage Spells"), num, replace=True))
		if spells: self.addCardtoHand(spells, self.ID)
		
		
class PowerofCreation(Spell):
	Class, school, name = "Mage", "Arcane", "Power of Creation"
	requireTarget, mana, effects = False, 8, ""
	index = "DALARAN~Mage~Spell~8~Arcane~Power of Creation"
	description = "Discover a 6-Cost minion. Summon two copies of it"
	name_CN = "创世之力"
	poolIdentifier = "6-Cost Minions as Mage to Summon"
	@classmethod
	def generatePool(cls, pools):
		classes = ["6-Cost Minions as %s to Summon"%Class for Class in pools.Classes]
		classCards = {s : [] for s in pools.ClassesandNeutral}
		for key, value in pools.MinionsofCost[6].items():
			for Class in key.split('~')[1].split(','):
				classCards[Class].append(value)
		return classes, [classCards[Class]+classCards["Neutral"] for Class in pools.Classes]
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverandGenerate(PowerofCreation, comment,
								 lambda: self.rngPool("6-Cost Minions as %s to Summon"%classforDiscover(self)))
		
	def discoverDecided(self, option, case, info_RNGSync=None, info_GUISync=None):
		self.handleDiscoverGeneratedCard(option, case, info_RNGSync, info_GUISync,
										 func=lambda cardType, card: self.summon([cardType(self.Game, self.ID) for _ in (0, 1)])
										 )


class Kalecgos(Minion):
	Class, race, name = "Mage", "Dragon", "Kalecgos"
	mana, attack, health = 10, 4, 12
	index = "DALARAN~Mage~Minion~10~4~12~Dragon~Kalecgos~Legendary"
	requireTarget, effects, description = False, "", "Your first spell costs (0) each turn. Battlecry: Discover a spell"
	name_CN = "卡雷苟斯"
	aura = ManaAura_Kalecgos
	poolIdentifier = "Mage Spells"
	@classmethod
	def generatePool(cls, pools):
		return [Class+" Spells" for Class in pools.Classes], \
				[[value for key, value in pools.ClassCards[Class].items() if "~Spell~" in key] for Class in pools.Classes]

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverandGenerate(Kalecgos, comment, lambda: self.rngPool(classforDiscover(self) + " Spells"))
		
		
class NeverSurrender(Secret):
	Class, school, name = "Paladin", "", "Never Surrender!"
	requireTarget, mana, effects = False, 1, ""
	index = "DALARAN~Paladin~Spell~1~Never Surrender!~~Secret"
	description = "Secret: Whenever your opponent casts a spell, give your minions +2 Health"
	name_CN = "永不屈服"
	trigBoard = Trig_NeverSurrender		


class LightforgedBlessing2(Twinspell):
	Class, school, name = "Paladin", "", "Lightforged Blessing"
	requireTarget, mana, effects = True, 2, ""
	index = "DALARAN~Paladin~Spell~2~Holy~Lightforged Blessing~Uncollectible"
	description = "Give a friendly minion Lifesteal"
	name_CN = "光铸祝福"
	def available(self):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.ID == self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.giveEnchant(target, effGain="Lifesteal", name=LightforgedBlessing)
		return target

class LightforgedBlessing(LightforgedBlessing2):
	index = "DALARAN~Paladin~Spell~2~Holy~Lightforged Blessing~Twinspell"
	description = "Twinspell. Give a friendly minion Lifesteal"
	twinSpellCopy = LightforgedBlessing2


class BronzeHerald(Minion):
	Class, race, name = "Paladin", "Dragon", "Bronze Herald"
	mana, attack, health = 3, 3, 2
	index = "DALARAN~Paladin~Minion~3~3~2~Dragon~Bronze Herald~Deathrattle"
	requireTarget, effects, description = False, "", "Deathrattle: Add two 4/4 Dragons to your hand"
	name_CN = "青铜传令官"
	deathrattle = Death_BronzeHerald

class BronzeDragon(Minion):
	Class, race, name = "Paladin", "Dragon", "Bronze Dragon"
	mana, attack, health = 4, 4, 4
	index = "DALARAN~Paladin~Minion~4~4~4~Dragon~Bronze Dragon~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "青铜龙"


class DesperateMeasures2(Twinspell):
	Class, school, name = "Paladin", "", "Desperate Measures"
	requireTarget, mana, effects = False, 1, ""
	index = "DALARAN~Paladin~Spell~1~~Desperate Measures~Uncollectible"
	description = "Cast a random Paladin Secrets"
	name_CN = "孤注一掷"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		func = self.Game.Secrets.sameSecretExists
		secrets = [value for value in self.rngPool("Paladin Secrets") if not func(value, self.ID)]
		if secrets: numpyChoice(secrets)(self.Game, self.ID).cast()

class DesperateMeasures(DesperateMeasures2):
	index = "DALARAN~Paladin~Spell~1~~Desperate Measures~Twinspell"
	description = "Twinspell. Cast a random Paladin Secrets"
	twinspellCopy = DesperateMeasures2
	poolIdentifier = "Paladin Secrets"
	@classmethod
	def generatePool(cls, pools):
		return "Paladin Secrets", [value for key, value in pools.ClassCards["Paladin"].items() if value.race == "Secret"]


class MysteriousBlade(Weapon):
	Class, name, description = "Paladin", "Mysterious Blade", "Battlecry: If you control a Secret, gain +1 Attack"
	mana, attack, durability, effects = 2, 2, 2, ""
	index = "DALARAN~Paladin~Weapon~2~2~2~Mysterious Blade~Battlecry"
	name_CN = "神秘之刃"
	def effCanTrig(self):
		self.effectViable = self.Game.Secrets.secrets[self.ID] != []
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Secrets.secrets[self.ID]: self.giveEnchant(self, 1, 0, name=MysteriousBlade)
		
		
class CalltoAdventure(Spell):
	Class, school, name = "Paladin", "", "Call to Adventure"
	requireTarget, mana, effects = False, 3, ""
	index = "DALARAN~Paladin~Spell~3~~Call to Adventure"
	description = "Draw the lowest Cost minion from your deck. Give it +2/+2"
	name_CN = "冒险号角"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if indices := pickLowestCostIndices(self.Game.Hand_Deck.decks[self.ID],
											func=lambda card: card.category == "Minion"):
			card, mana, entersHand = self.Game.Hand_Deck.drawCard(self.ID, numpyChoice(indices))
			if entersHand: self.giveEnchant(card, 2, 2, name=CalltoAdventure)
		
		
class DragonSpeaker(Minion):
	Class, race, name = "Paladin", "", "Dragon Speaker"
	mana, attack, health = 5, 3, 5
	index = "DALARAN~Paladin~Minion~5~3~5~~Dragon Speaker~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Give all Dragons in your hand +3/+3"
	name_CN = "龙语者"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.AOE_GiveEnchant([card for card in self.Game.Hand_Deck.hands[self.ID] if "Dragon" in card.race], 
							3, 3, name=DragonSpeaker, add2EventinGUI=False)
		
#Friendly minion attacks. If the the minion has "Can't Attack", then it won't attack.
#Attackchances won't be consumed. If it survives, it can attack again. triggers["DealsDamage"] functions can trigger.


#Friendly minion attacks. If the the minion has "Can't Attack", then it won't attack.
#Attackchances won't be consumed. If it survives, it can attack again. triggers["DealsDamage"] functions can trigger.
class Duel(Spell):
	Class, school, name = "Paladin", "", "Duel!"
	requireTarget, mana, effects = False, 5, ""
	index = "DALARAN~Paladin~Spell~5~~Duel!"
	description = "Summon a minion from each player's deck. They fight"
	name_CN = "决斗"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		enemy, enemyDeck = None, self.Game.Hand_Deck.decks[3-self.ID]
		friendly = self.try_SummonfromDeck()
		if self.Game.space(3-self.ID) and (indices := [i for i, card in enumerate(enemyDeck) if card.category == "Minion"]):
			enemy = self.Game.summonfrom(numpyChoice(indices), 3-self.ID, -1, summoner=self, source='D')
		#如果我方随从有不能攻击的限制，如Ancient Watcher之类，不能攻击。
		#攻击不消耗攻击机会
		#需要测试有条件限制才能攻击的随从，如UnpoweredMauler
		if friendly and enemy and friendly.effects["Can't Attack"] < 1:
			self.Game.battle(friendly, enemy, verifySelectable=False, useAttChance=False, resolveDeath=False)


class CommanderRhyssa(Minion):
	Class, race, name = "Paladin", "", "Commander Rhyssa"
	mana, attack, health = 3, 4, 3
	index = "DALARAN~Paladin~Minion~3~4~3~~Commander Rhyssa~Legendary"
	requireTarget, effects, description = False, "", "Your Secrets trigger twice"
	name_CN = "指挥官蕾撒"
	aura = GameRuleAura_CommanderRhyssa

		
class Nozari(Minion):
	Class, race, name = "Paladin", "Dragon", "Nozari"
	mana, attack, health = 10, 4, 12
	index = "DALARAN~Paladin~Minion~10~4~12~Dragon~Nozari~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: Restore both heroes to full Health"
	name_CN = "诺萨莉"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		heal1, heal2 = self.calcHeal(self.Game.heroes[1].health_max), self.calcHeal(self.Game.heroes[2].health_max)
		self.AOE_Heal([self.Game.heroes[1], self.Game.heroes[2]], [heal1, heal2])
		

class EVILConscripter(Minion):
	Class, race, name = "Priest", "", "EVIL Conscripter"
	mana, attack, health = 2, 2, 2
	index = "DALARAN~Priest~Minion~2~2~2~~EVIL Conscripter~Deathrattle"
	requireTarget, effects, description = False, "", "Deathrattle: Add a Lackey to your hand"
	name_CN = "怪盗征募员"
	deathrattle = Death_EVILConscripter


class HenchClanShadequill(Minion):
	Class, race, name = "Priest", "", "Hench-Clan Shadequill"
	mana, attack, health = 4, 4, 7
	index = "DALARAN~Priest~Minion~4~4~7~~Hench-Clan Shadequill~Deathrattle"
	requireTarget, effects, description = False, "", "Deathrattle: Restore 5 Health to the enemy hero"
	name_CN = "荆棘帮箭猪"
	deathrattle = Death_HenchClanShadequill


#If the target minion is killed due to Teacher/Juggler combo, summon a fresh new minion without enchantment.
class UnsleepingSoul(Spell):
	Class, school, name = "Priest", "Shadow", "Unsleeping Soul"
	requireTarget, mana, effects = True, 4, ""
	index = "DALARAN~Priest~Spell~4~Shadow~Unsleeping Soul"
	description = "Silence a friendly minion, then summon a copy of it"
	name_CN = "不眠之魂"
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.ID == self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.getsSilenced()
			Copy = target.selfCopy(target.ID, self) if target.onBoard else type(target)(self.Game, target.ID)
			self.summon(Copy, position=target.pos+1)
		return target
		
		
class ForbiddenWords(Spell):
	Class, school, name = "Priest", "Shadow", "Forbidden Words"
	requireTarget, mana, effects = True, 0, ""
	index = "DALARAN~Priest~Spell~0~Shadow~Forbidden Words"
	description = "Spell all your Mana. Destroy a minion with that much Attack or less"
	name_CN = "禁忌咒文"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.attack <= self.Game.Manas.manas[self.ID] and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		#假设如果没有指定目标则不会消耗法力值
		if target:
			self.Game.Counters.manaSpentonSpells[self.ID] += self.Game.Manas.manas[self.ID]
			self.Game.Manas.manas[self.ID] = 0
			self.Game.killMinion(self, target)
		return target
		
		
class ConvincingInfiltrator(Minion):
	Class, race, name = "Priest", "", "Convincing Infiltrator"
	mana, attack, health = 5, 2, 6
	index = "DALARAN~Priest~Minion~5~2~6~~Convincing Infiltrator~Taunt~Deathrattle"
	requireTarget, effects, description = False, "Taunt", "Taunt. Deathrattle: Destroy a random enemy minion"
	name_CN = "无面渗透者"
	deathrattle = Death_ConvincingInfiltrator


class MassResurrection(Spell):
	Class, school, name = "Priest", "Holy", "Mass Resurrection"
	requireTarget, mana, effects = False, 9, ""
	index = "DALARAN~Priest~Spell~9~Holy~Mass Resurrection"
	description = "Summon 3 friendly minions that died this game"
	name_CN = "群体复活"
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		minionsDied = self.Game.Counters.minionsDiedThisGame[self.ID]
		minions = numpyChoice(minionsDied, min(3, len(minionsDied)), replace=False) if minionsDied else []
		if minions: self.summon([minion(self.Game, self.ID) for minion in minions])

#Upgrades at the end of turn.
class LazulsScheme(Spell):
	Class, school, name = "Priest", "Shadow", "Lazul's Scheme"
	requireTarget, mana, effects = True, 0, ""
	index = "DALARAN~Priest~Spell~0~Shadow~Lazul's Scheme"
	name_CN = "拉祖尔的阴谋"
	trigHand = Trig_Upgrade
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.giveEnchant(target, statEnchant=Enchantment(-self.progress, 0, until=self.ID, name=LazulsScheme))
		return target


class ShadowyFigure(Minion):
	Class, race, name = "Priest", "", "Shadowy Figure"
	mana, attack, health = 2, 2, 2
	index = "DALARAN~Priest~Minion~2~2~2~~Shadowy Figure~Battlecry"
	requireTarget, effects, description = True, "", "Battlecry: Transform into a 2/2 copy of a friendly Deathrattle minion"
	name_CN = "阴暗的人影"
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target != self and target.ID == self.ID and target.deathrattles != [] and target.onBoard
		
	def effCanTrig(self):
		self.effectViable = self.targetExists()
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		#目前只有打随从从手牌打出或者被沙德沃克调用可以触发随从的战吼。这些手段都要涉及self.Game.minionPlayed
		#如果self.Game.minionPlayed不再等于自己，说明这个随从的已经触发了变形而不会再继续变形。
		if target and self.dead == False and self.Game.minionPlayed == self: #战吼触发时自己不能死亡。
			if self.onBoard or self.inHand:
				if target.onBoard:
					Copy = target.selfCopy(self.ID, self, 2, 2)
				else: #target not on board. This Shadowy Figure becomes a base copy of it.
					Copy = type(target)(self.Game, self.ID)
					Copy.statReset(2, 2, source=type(self))
				self.transform(self, Copy)
		return target
		
		
class MadameLazul(Minion):
	Class, race, name = "Priest", "", "Madame Lazul"
	mana, attack, health = 3, 3, 2
	index = "DALARAN~Priest~Minion~3~3~2~~Madame Lazul~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: Discover a copy of a card in your opponent's hand"
	name_CN = "拉祖尔女士"
	#暂时假定无视手牌中的牌的名字相同的规则，发现中可以出现名字相同的牌
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverfromList(MadameLazul, comment, ls=self.Game.Hand_Deck.hands[3-self.ID])
		
	def discoverDecided(self, option, case, info_RNGSync=None, info_GUISync=None):
		self.handleDiscoveredCardfromList(option, case, ls=self.Game.Hand_Deck.hands[3-self.ID],
										  func=lambda index, card: self.addCardtoHand(option.selfCopy(self.ID, self), self.ID, byDiscover=True),
										  info_RNGSync=info_RNGSync, info_GUISync=info_GUISync)
		
		
class CatrinaMuerte(Minion):
	Class, race, name = "Priest", "", "Catrina Muerte"
	mana, attack, health = 8, 6, 8
	index = "DALARAN~Priest~Minion~8~6~8~~Catrina Muerte~Legendary"
	requireTarget, effects, description = False, "", "At the end of your turn, summon a friendly minion that died this game"
	name_CN = "亡者卡特林娜"
	trigBoard = Trig_CatrinaMuerte		


class DaringEscape(Spell):
	Class, school, name = "Rogue", "", "Daring Escape"
	requireTarget, mana, effects = False, 1, ""
	index = "DALARAN~Rogue~Spell~1~~Daring Escape"
	description = "Return all friendly minions to your hand"
	name_CN = "战略转移"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for minion in self.Game.minionsonBoard(self.ID):
			self.Game.returnObj2Hand(minion)
		
		
class EVILMiscreant(Minion):
	Class, race, name = "Rogue", "", "EVIL Miscreant"
	mana, attack, health = 3, 1, 4
	index = "DALARAN~Rogue~Minion~3~1~4~~EVIL Miscreant~Combo"
	requireTarget, effects, description = False, "", "Combo: Add two 1/1 Lackeys to your hand"
	name_CN = "怪盗恶霸"
	
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0
		
	#Will only be invoked if self.effCanTrig() returns True in self.played()
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0:
			self.addCardtoHand(numpyChoice(Lackeys, 2, replace=True), self.ID)
		
		
class HenchClanBurglar(Minion):
	Class, race, name = "Rogue", "Pirate", "Hench-Clan Burglar"
	mana, attack, health = 4, 4, 3
	index = "DALARAN~Rogue~Minion~4~4~3~Pirate~Hench-Clan Burglar~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Discover a spell from another class"
	name_CN = "荆棘帮蟊贼"
	poolIdentifier = "Druid Spells"
	@classmethod
	def generatePool(cls, pools):
		return [Class+" Spells" for Class in pools.Classes], \
				[[value for key, value in pools.ClassCards[Class].items() if "~Spell~" in key] for Class in pools.Classes]
		
	def decideSpellPool(self):
		heroClass = self.Game.heroes[self.ID].Class
		classes = [Class for Class in Classes if Class != heroClass]
		return self.rngPool("%s Spells"%datetime.now().microsecond % len(classes))

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverandGenerate(HenchClanBurglar, comment, lambda : HenchClanBurglar.decideSpellPool(self))
		
		
class TogwagglesScheme(Spell):
	Class, school, name = "Rogue", "", "Togwaggle's Scheme"
	requireTarget, mana, effects = True, 1, ""
	index = "DALARAN~Rogue~Spell~1~~Togwaggle's Scheme"
	name_CN = "托瓦格尔的阴谋"
	trigHand = Trig_Upgrade
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.ID == self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			copies = [type(target)(self.Game, self.ID) for i in range(self.progress)]
			self.shuffleintoDeck(copies, enemyCanSee=True)
		return target
		
		
class UnderbellyFence(Minion):
	Class, race, name = "Rogue", "", "Underbelly Fence"
	mana, attack, health = 2, 2, 3
	index = "DALARAN~Rogue~Minion~2~2~3~~Underbelly Fence~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: If you're holding a card from another class, gain +1/+1 and Rush"
	name_CN = "下水道销赃人"
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.holdingCardfromAnotherClass(self.ID, exclude=self)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Hand_Deck.holdingCardfromAnotherClass(self.ID, exclude=self):
			self.giveEnchant(self, 1, 1, effGain="Rush", name=UnderbellyFence)
		
		
class Vendetta(Spell):
	Class, school, name = "Rogue", "", "Vendetta"
	requireTarget, mana, effects = True, 4, ""
	index = "DALARAN~Rogue~Spell~4~~Vendetta"
	description = "Deal 4 damage to a minion. Costs (0) if you're holding a card from another class"
	name_CN = "宿敌"
	trigHand = Trig_Vendetta		
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard
		
	def selfManaChange(self):
		if self.inHand and self.Game.Hand_Deck.holdingCardfromAnotherClass(self.ID):
			self.mana = 0
			
	def text(self):
		damage = self.calcDamage(4)
		return "对一个随从造成%d点伤害。如果你的手牌中有另一职业的卡牌，则法力值消耗为(0)点"%damage if CHN \
				else "Deal %d damage to a minion. Costs (0) if you're holding a card from another class"%damage
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = self.calcDamage(4)
			self.dealsDamage(target, damage)
		return target
		

class WagglePick(Weapon):
	Class, name, description = "Rogue", "Waggle Pick", "Deathrattle: Return a random friendly minion to your hand. It costs (2) less"
	mana, attack, durability, effects = 4, 4, 2, ""
	index = "DALARAN~Rogue~Weapon~4~4~2~Waggle Pick~Deathrattle"
	name_CN = "摇摆矿锄"
	deathrattle = Death_WagglePick
#There are minions who also have this deathrattle.


class UnidentifiedContract(Spell):
	Class, school, name = "Rogue", "", "Unidentified Contract"
	requireTarget, mana, effects = True, 6, ""
	index = "DALARAN~Rogue~Spell~6~~Unidentified Contract"
	description = "Destroy a minion. Gain a bonus effect in your hand"
	name_CN = "未鉴定的合约"
	def entersHand(self):
		#本牌进入手牌的结果是本卡消失，变成其他的牌
		self.onBoard = self.inHand = self.inDeck = False
		card = numpyChoice((AssassinsContract, LucrativeContract, RecruitmentContract, TurncoatContract))(self.Game, self.ID)
		card.inHand = True
		card.onBoard = card.inDeck = False
		card.enterHandTurn = card.Game.numTurn
		return card
		
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.Game.killMinion(self, target)
		return target
		

class AssassinsContract(Spell):
	Class, school, name = "Rogue", "", "Assassin's Contract"
	requireTarget, mana, effects = True, 6, ""
	index = "DALARAN~Rogue~Spell~6~~Assassin's Contract~Uncollectible"
	description = "Destroy a minion. Summon a 1/1 Patient Assassin"
	name_CN = "刺客合约"
	
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.Game.killMinion(self, target)
			self.summon(PatientAssassin(self.Game, self.ID))
		return target
		

class LucrativeContract(Spell):
	Class, school, name = "Rogue", "", "Lucrative Contract"
	requireTarget, mana, effects = True, 6, ""
	index = "DALARAN~Rogue~Spell~6~~Lucrative Contract~Uncollectible"
	description = "Destroy a minion. Add two Coins to your hand"
	name_CN = "赏金合约"
	
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.Game.killMinion(self, target)
		self.addCardtoHand([TheCoin, TheCoin], self.ID)
		return target
		

class RecruitmentContract(Spell):
	Class, school, name = "Rogue", "", "Recruitment Contract"
	requireTarget, mana, effects = True, 6, ""
	index = "DALARAN~Rogue~Spell~6~~Recruitment Contract~Uncollectible"
	description = "Destroy a minion. Add a copy of it to your hand"
	name_CN = "招募合约"
	
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.Game.killMinion(self, target)
		self.addCardtoHand(type(target), self.ID)
		return target
		

class TurncoatContract(Spell):
	Class, school, name = "Rogue", "", "Turncoat Contract"
	requireTarget, mana, effects = True, 6, ""
	index = "DALARAN~Rogue~Spell~6~~Turncoat Contract~Uncollectible"
	description = "Destroy a minion. It deals damage to adjacent minions"
	name_CN = "叛变合约"
	
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.Game.killMinion(self, target)
			if target.onBoard and (adjacentMinions := self.Game.neighbors2(target)[0]):
				target.AOE_Damage(adjacentMinions, [target.attack]*len(adjacentMinions))
		return target
		
		
class HeistbaronTogwaggle(Minion):
	Class, race, name = "Rogue", "", "Heistbaron Togwaggle"
	mana, attack, health = 6, 5, 5
	index = "DALARAN~Rogue~Minion~6~5~5~~Heistbaron Togwaggle~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: If you control a Lackey, choose a fantastic treasure"
	name_CN = "劫匪之王托瓦格尔"
	
	def effCanTrig(self):
		self.effectViable = False
		for minion in self.Game.minionsonBoard(self.ID):
			if minion.name.endswith("Lackey"):
				self.effectViable = True
				break
				
	#Will only be invoked if self.effCanTrig() returns True in self.played()
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if any([minion.name.endswith("Lackey") for minion in self.Game.minionsonBoard(self.ID)]):
			self.discoverandGenerate(HeistbaronTogwaggle, comment, lambda : FantasticTreasures)
		
		
class TakNozwhisker(Minion):
	Class, race, name = "Rogue", "", "Tak Nozwhisker"
	mana, attack, health = 7, 6, 6
	index = "DALARAN~Rogue~Minion~7~6~6~~Tak Nozwhisker"
	requireTarget, effects, description = False, "", "Whenever you shuffle a card into your deck, add a copy to your hand"
	name_CN = "塔克·诺兹维克"
	trigBoard = Trig_TakNozwhisker		


class Mutate(Spell):
	Class, school, name = "Shaman", "", "Mutate"
	requireTarget, mana, effects = True, 0, ""
	index = "DALARAN~Shaman~Spell~0~~Mutate"
	description = "Transf a friendly minion to a random one that costs (1) more"
	name_CN = "突变"
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
		if target: target = self.transform(target, self.newEvolved(type(target).mana, by=1, ID=target.ID))
		return target
		
		
class SludgeSlurper(Minion):
	Class, race, name = "Shaman", "Murloc", "Sludge Slurper"
	mana, attack, health = 1, 2, 1
	index = "DALARAN~Shaman~Minion~1~2~1~Murloc~Sludge Slurper~Battlecry~Overload"
	requireTarget, effects, description = False, "", "Battlecry: Add a Lackey to your hand. Overload: (1)"
	name_CN = "淤泥吞食者"
	overload = 1
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.addCardtoHand(numpyChoice(Lackeys), self.ID)
		
		
class SouloftheMurloc(Spell):
	Class, school, name = "Shaman", "", "Soul of the Murloc"
	requireTarget, mana, effects = False, 2, ""
	index = "DALARAN~Shaman~Spell~2~~Soul of the Murloc"
	description = "Give your minions 'Deathrattle: Summon a 1/1 Murloc'"
	name_CN = "鱼人之魂"
	def available(self):
		return self.Game.minionsonBoard(self.ID) != []
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.AOE_GiveEnchant(self.Game.minionsonBoard(self.ID), trig=Death_SouloftheMurloc, trigType="Deathrattle")
		

class UnderbellyAngler(Minion):
	Class, race, name = "Shaman", "Murloc", "Underbelly Angler"
	mana, attack, health = 2, 2, 3
	index = "DALARAN~Shaman~Minion~2~2~3~Murloc~Underbelly Angler"
	requireTarget, effects, description = False, "", "After you play a Murloc, add a random Murloc to your hand"
	name_CN = "下水道渔人"
	poolIdentifier = "Murlocs"
	@classmethod
	def generatePool(cls, pools):
		return "Murlocs", list(pools.MinionswithRace["Murloc"].values())
		
	trigBoard = Trig_UnderbellyAngler		


class HagathasScheme(Spell):
	Class, school, name = "Shaman", "Nature", "Hagatha's Scheme"
	requireTarget, mana, effects = False, 5, ""
	index = "DALARAN~Shaman~Spell~5~~Nature~Hagatha's Scheme"
	description = "Deal 1 damage to all minions. (Upgrades each turn)!"
	name_CN = "哈加莎的阴谋"
	trigHand = Trig_Upgrade
	def text(self): return self.calcDamage(self.progress)
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = self.calcDamage(self.progress)
		targets = self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)
		self.AOE_Damage(targets, [damage]*len(targets))
		
		
class WalkingFountain(Minion):
	Class, race, name = "Shaman", "Elemental", "Walking Fountain"
	mana, attack, health = 8, 4, 8
	index = "DALARAN~Shaman~Minion~8~4~8~Elemental~Walking Fountain~Rush~Lifesteal~Windfury"
	requireTarget, effects, description = False, "Rush,Windfury,Lifesteal", "Rush, Windfury, Lifesteal"
	name_CN = "活动喷泉"
	
	
class WitchsBrew(Spell):
	Class, school, name = "Shaman", "Nature", "Witch's Brew"
	requireTarget, mana, effects = True, 2, ""
	index = "DALARAN~Shaman~Spell~2~Nature~Witch's Brew"
	description = "Restore 4 Health. Repeatable this turn"
	name_CN = "女巫杂酿"
	def text(self): return self.calcHeal(4)
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.restoresHealth(target, self.calcHeal(4))
			echo = WitchsBrew(self.Game, self.ID)
			echo.trigsHand.append(Trig_Echo(echo))
			self.addCardtoHand(echo, self.ID)
		return target
		
		
class Muckmorpher(Minion):
	Class, race, name = "Shaman", "", "Muckmorpher"
	mana, attack, health = 5, 4, 4
	index = "DALARAN~Shaman~Minion~5~4~4~~Muckmorpher~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Transform in to a 4/4 copy of a different minion in your deck"
	name_CN = "泥泽变形怪"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		#目前只有打随从从手牌打出或者被沙德沃克调用可以触发随从的战吼。这些手段都要涉及self.Game.minionPlayed
		#如果self.Game.minionPlayed不再等于自己，说明这个随从的已经触发了变形而不会再继续变形。
		if not self.dead and (self.onBoard or self.inHand) and self.Game.minionPlayed == self: #战吼触发时自己不能死亡。
			if minions := [card for card in self.Game.Hand_Deck.decks[self.ID] if card.category == "Minion" and type(card) != type(self)]:
				self.transform(self, numpyChoice(minions).selfCopy(self.ID, self, 4, 4))
		

class Scargil(Minion):
	Class, race, name = "Shaman", "Murloc", "Scargil"
	mana, attack, health = 4, 4, 4
	index = "DALARAN~Shaman~Minion~4~4~4~Murloc~Scargil~Legendary"
	requireTarget, effects, description = False, "", "Your Murlocs cost (1)"
	name_CN = "斯卡基尔"
	aura = ManaAura_Scargil


class SwampqueenHagatha(Minion):
	Class, race, name = "Shaman", "", "Swampqueen Hagatha"
	mana, attack, health = 7, 5, 5
	index = "DALARAN~Shaman~Minion~7~5~5~~Swampqueen Hagatha~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: Add a 5/5 Horror to your hand. Teach it two Shaman spells"
	name_CN = "沼泽女王哈加莎"
	poolIdentifier = "Shaman Spells"
	@classmethod
	def generatePool(cls, pools):
		spells, targetingSpells, nontargetingSpells = [], [], []
		for key, value in pools.ClassCards["Shaman"].items():
			if "~Spell~" in key:
				spells.append(value)
				if value.requireTarget: targetingSpells.append(value)
				else: nontargetingSpells.append(value)
		return ["Shaman Spells", "Targeting Shaman Spells", "Non-targeting Shaman Spells"], [spells, targetingSpells, nontargetingSpells]

	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.firstSpellneedsTarget = False
		self.spell1, self.spell2 = None, None

	#有可能发现两个相同的非指向性法术。
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.spell1, self.spell2 = None, None
		curGame = self.Game
		if self.ID == curGame.turn:
			if curGame.mode == 0:
				if curGame.picks:
					spell1, spell2 = curGame.picks.pop(0)
				else:
					if "byOthers" in comment:
						spell1 = numpyChoice(self.rngPool("Shaman Spells"))
						#If the first spell is not a targeting spell, then the 2nd has no restrictions
						spell2 = numpyChoice(self.rngPool("Non-targeting Shaman Spells")) if spell1.requireTarget else numpyChoice(self.rngPool("Shaman Spells"))
						curGame.picks_Backup.append((spell1, spell2))
					else:
						spells = numpyChoice(self.rngPool("Shaman Spells"), 3, replace=False)
						curGame.options = [spell(curGame, self.ID) for spell in spells]
						curGame.Discover.startDiscover(self)
						if self.spell1.requireTarget: spells = numpyChoice(self.rngPool("Non-targeting Shaman Spells"), 3, replace=False)
						else: spells = numpyChoice(self.rngPool("Shaman Spells"), 3, replace=False)
						curGame.options = [spell(curGame, self.ID) for spell in spells]
						curGame.Discover.startDiscover(self)
						spell1, spell2 = self.spell1, self.spell2
						self.spell1, self.spell2 = None, None
						curGame.picks_Backup.append((spell1, spell2))
				#The 2 spells are both class types, whether they come from Discover or random
				spell1ClassName, spell2ClassName = spell1.__name__, spell2.__name__
				requireTarget = spell1.requireTarget or spell2.requireTarget
				newIndex = "DALARAN~Shaman~5~5~5~Minion~~Drustvar Horror_%s_%s~Battlecry~Uncollectible"%(spell1.name, spell2.name)
				subclass = type("DrustvarHorror__"+spell1ClassName+spell2ClassName, (DrustvarHorror, ),
								{"requireTarget": requireTarget, "learnedSpell1": spell1, "learnedSpell2":spell2,
								"index": newIndex
								}
								)
				self.addCardtoHand(subclass(curGame, self.ID), self.ID)
		
	def discoverDecided(self, option, case, info_RNGSync=None, info_GUISync=None):
		if self.spell1 is None: self.spell1 = type(option)
		else: self.spell2 = type(option)
		

class DrustvarHorror(Minion):
	Class, race, name = "Shaman", "", "Drustvar Horror"
	mana, attack, health = 5, 5, 5
	index = "DALARAN~Shaman~Minion~5~5~5~~Drustvar Horror~Battlecry~Uncollectible"
	requireTarget, effects, description = True, "", "Battlecry: Cast (0) and (1)"
	name_CN = "德鲁斯瓦恐魔"
	learnedSpell1, learnedSpell2 = None, None
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.learnedSpell1 = type(self).learnedSpell1(self.Game, self.ID)
		self.learnedSpell2 = type(self).learnedSpell2(self.Game, self.ID)
		self.description = "Battlecry: Cast %s and %s"%(self.learnedSpell1.name, self.learnedSpell2.name)
		
	#无指向的法术的available一般都会返回True，不返回True的时候一般是场上没有格子了，但是这种情况本来就不能打出随从，不会影响判定。
	#有指向的法术的available会真正决定可指向目标是否存在。
	def targetExists(self, choice=0): #假设可以指向魔免随从
		#这里调用携带的法术类的available函数的同时需要向其传导self，从而让其知道self.selectableCharacterExists用的是什么实例的方法
		self.learnedSpell1.ID, self.learnedSpell2.ID = self.ID, self.ID
		return self.learnedSpell1.available() and self.learnedSpell2.available()
		
	def targetCorrect(self, target, choice=0):
		if self == target: return False
		self.learnedSpell1.ID, self.learnedSpell2.ID = self.ID, self.ID
		if self.learnedSpell1.needTarget():
			return self.learnedSpell1.targetCorrect(target)
		if self.learnedSpell2.needTarget():
			return self.learnedSpell2.targetCorrect(target)
		return True
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		#不知道施放的法术是否会触发发现，还是直接随机选取一个发生选项
		#假设是随机选取一个选项。
		self.learnedSpell1.cast(target)
		self.learnedSpell2.cast(target)
		return target
		

class EVILGenius(Minion):
	Class, race, name = "Warlock", "", "EVIL Genius"
	mana, attack, health = 2, 2, 2
	index = "DALARAN~Warlock~Minion~2~2~2~~EVIL Genius~Battlecry"
	requireTarget, effects, description = True, "", "Battlecry: Destroy a friendly minion to add 2 random Lackeys to your hand"
	name_CN = "怪盗天才"
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.ID == self.ID and target != self and target.onBoard 
		
	def effCanTrig(self):
		self.effectViable = self.targetExists()
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.Game.killMinion(self, target)
			self.addCardtoHand(numpyChoice(Lackeys, 2, replace=True), self.ID)
		return target
		
		
class RafaamsScheme(Spell):
	Class, school, name = "Warlock", "Fire", "Rafaam's Scheme"
	requireTarget, mana, effects = False, 3, ""
	index = "DALARAN~Warlock~Spell~3~Fire~Rafaam's Scheme"
	description = "Summon 1 1/1 Imp(Upgrades each turn!)"
	name_CN = "拉法姆的阴谋"
	trigHand = Trig_Upgrade
	def text(self): return self.progress

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon([Imp_Shadows(self.Game, self.ID) for i in range(self.progress)])
		
		
class AranasiBroodmother(Minion):
	Class, race, name = "Warlock", "Demon", "Aranasi Broodmother"
	mana, attack, health = 6, 4, 6
	index = "DALARAN~Warlock~Minion~6~4~6~Demon~Aranasi Broodmother~Taunt~Triggers when Drawn"
	requireTarget, effects, description = False, "Taunt", "Taunt. When you draw this, restore 4 Health to your hero"
	name_CN = "阿兰纳斯蛛后"
	def whenDrawn(self):
		self.restoresHealth(self.Game.heroes[self.ID], self.calcHeal(4))
		
#把随从洗回牌库会消除其上的身材buff（+2、+2的飞刀杂耍者的buff消失）
#卡牌上的费用效果也会全部消失(大帝的-1效果)
#被祈求升级过一次的迦拉克隆也会失去进度。
#说明这个动作是把手牌中所有牌初始化洗回去


#把随从洗回牌库会消除其上的身材buff（+2、+2的飞刀杂耍者的buff消失）
#卡牌上的费用效果也会全部消失(大帝的-1效果)
#被祈求升级过一次的迦拉克隆也会失去进度。
#说明这个动作是把手牌中所有牌初始化洗回去
class PlotTwist(Spell):
	Class, school, name = "Warlock", "", "Plot Twist"
	requireTarget, mana, effects = False, 2, ""
	index = "DALARAN~Warlock~Spell~2~~Plot Twist"
	description = "Shuffle your hand into your deck. Draw that many cards"
	name_CN = "情势反转"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		handSize = len(self.Game.Hand_Deck.hands[self.ID])
		self.Game.Hand_Deck.shuffle_Hand2Deck(0, self.ID, initiatorID=self.ID, shuffleAll=True)
		for i in range(handSize): self.Game.Hand_Deck.drawCard(self.ID)
		
		
class Impferno(Spell):
	Class, school, name = "Warlock", "Fire", "Impferno"
	requireTarget, mana, effects = False, 3, ""
	index = "DALARAN~Warlock~Spell~3~Fire~Impferno"
	description = "Give your Demons +1 Attack. Deal 1 damage to all enemy minions"
	name_CN = "小鬼狱火"
	def text(self): return self.calcDamage(1)
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.AOE_GiveEnchant(self.Game.minionsonBoard(self.ID, race="Demon"), 1, 1, name=Impferno)
		damage = self.calcDamage(1)
		targets = self.Game.minionsonBoard(3-self.ID)
		self.AOE_Damage(targets, [damage]*len(targets))
		
		
class EagerUnderling(Minion):
	Class, race, name = "Warlock", "", "Eager Underling"
	mana, attack, health = 4, 2, 2
	index = "DALARAN~Warlock~Minion~4~2~2~~Eager Underling~Deathrattle"
	requireTarget, effects, description = False, "", "Deathrattle: Give two random friendly minions +2/+2"
	name_CN = "性急的杂兵"
	deathrattle = Death_EagerUnderling


class DarkestHour(Spell):
	Class, school, name = "Warlock", "Shadow", "Darkest Hour"
	requireTarget, mana, effects = False, 6, ""
	index = "DALARAN~Warlock~Spell~6~Shadow~Darkest Hour"
	description = "Destroy all friendly minions. For each one, summon a random minion from your deck"
	name_CN = "至暗时刻"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		game = self.Game
		friendlyMinions = game.minionsonBoard(self.ID)
		boardSize = len(friendlyMinions)
		game.killMinion(self, friendlyMinions)
		#对于所有友方随从强制死亡，并令其离场，因为召唤的随从是在场上右边，不用记录死亡随从的位置
		game.gathertheDead()
		for _ in range(boardSize):
			if not self.try_SummonfromDeck(): break
		
#For now, assume the mana change is on the mana and shuffling this card back into deck won't change its counter.


#For now, assume the mana change is on the mana and shuffling this card back into deck won't change its counter.
class JumboImp(Minion):
	Class, race, name = "Warlock", "Demon", "Jumbo Imp"
	mana, attack, health = 10, 8, 8
	index = "DALARAN~Warlock~Minion~10~8~8~Demon~Jumbo Imp"
	requireTarget, effects, description = False, "", "Costs (1) less whenever a friendly minion dies while this is in your hand"
	name_CN = "巨型小鬼"
	trigHand = Trig_JumboImp


class ArchVillainRafaam(Minion):
	Class, race, name = "Warlock", "", "Arch-Villain Rafaam"
	mana, attack, health = 7, 7, 8
	index = "DALARAN~Warlock~Minion~7~7~8~~Arch-Villain Rafaam~Taunt~Battlecry~Legendary"
	requireTarget, effects, description = False, "Taunt", "Battlecry: Replace your hand and deck with Legendary minions"
	name_CN = "至尊盗王拉法姆"
	poolIdentifier = "Legendary Minions"
	@classmethod
	def generatePool(cls, pools):
		return "Legendary Minions", list(pools.LegendaryMinions.values())
	#不知道拉法姆的替换手牌、牌库和迦拉克隆会有什么互动。假设不影响主迦拉克隆。
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		game = self.Game
		minions = self.rngPool("Legendary Minions")
		hand = tuple(numpyChoice(minions, len(game.Hand_Deck.hands[self.ID]), replace=True))
		deck = tuple(numpyChoice(minions, len(game.Hand_Deck.dekcs[self.ID]), replace=True))
		if hand or deck:
			game.Hand_Deck.extractfromHand(None, self.ID, getAll=True)
			self.addCardtoHand(hand, self.ID)
			game.Hand_Deck.replaceWholeDeck(self.ID, [card(game, self.ID) for card in deck])
		
		
class FelLordBetrug(Minion):
	Class, race, name = "Warlock", "Demon", "Fel Lord Betrug"
	mana, attack, health = 8, 5, 7
	index = "DALARAN~Warlock~Minion~8~5~7~Demon~Fel Lord Betrug~Legendary"
	requireTarget, effects, description = False, "", "Whenever you draw a minion, summon a copy with Rush that dies at end of turn"
	name_CN = "邪能领主贝图格"
	trigBoard = Trig_FelLordBetrug		


class ImproveMorale(Spell):
	Class, school, name = "Warrior", "", "Improve Morale"
	requireTarget, mana, effects = True, 1, ""
	index = "DALARAN~Warrior~Spell~1~~Improve Morale"
	description = "Deal 1 damage to a minion. If it survives, add a Lackey to your hand"
	name_CN = "提振士气"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard
		
	def text(self):
		damage = self.calcDamage(1)
		return "对一个随从造成%d点伤害,如果它仍然存活，则将一张随从牌置入你的手牌"%damage if CHN \
				else "Deal %d damage to a minion. If it survives, add a Lackey to your hand"%damage
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = self.calcDamage(1)
			self.dealsDamage(target, damage)
			if target.health > 0 and not target.dead: self.addCardtoHand(numpyChoice(Lackeys), self.ID)
		return target
		
		
class ViciousScraphound(Minion):
	Class, race, name = "Warrior", "Mech", "Vicious Scraphound"
	mana, attack, health = 2, 2, 2
	index = "DALARAN~Warrior~Minion~2~2~2~Mech~Vicious Scraphound"
	requireTarget, effects, description = False, "", "Whenever this minion deals damage, gain that much Armor"
	name_CN = "凶恶的废钢猎犬"
	trigBoard = Trig_ViciousScraphound		


class DrBoomsScheme(Spell):
	Class, school, name = "Warrior", "", "Dr. Boom's Scheme"
	requireTarget, mana, effects = False, 4, ""
	index = "DALARAN~Warrior~Spell~4~~Dr. Boom's Scheme"
	description = "Gain 1 Armor. (Upgrades each turn!)"
	name_CN = "砰砰博士的阴谋"
	trigHand = Trig_Upgrade
	def text(self): return self.progress

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.giveHeroAttackArmor(self.ID, armor=self.progress)
		
		
class SweepingStrikes(Spell):
	Class, school, name = "Warrior", "", "Sweeping Strikes"
	requireTarget, mana, effects = True, 2, ""
	index = "DALARAN~Warrior~Spell~2~~Sweeping Strikes"
	description = "Give a minion 'Also damages minions next to whoever this attacks'"
	name_CN = "横扫攻击"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.effects["Sweep"] += 1
		return target
		
		
class ClockworkGoblin(Minion):
	Class, race, name = "Warrior", "Mech", "Clockwork Goblin"
	mana, attack, health = 3, 3, 3
	index = "DALARAN~Warrior~Minion~3~3~3~Mech~Clockwork Goblin~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Shuffle a Bomb in to your opponent's deck. When drawn, it explodes for 5 damage"
	name_CN = "发条地精"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.shuffleintoDeck(Bomb(self.Game, 3-self.ID), enemyCanSee=True)
		
		
class OmegaDevastator(Minion):
	Class, race, name = "Warrior", "Mech", "Omega Devastator"
	mana, attack, health = 4, 4, 5
	index = "DALARAN~Warrior~Minion~4~4~5~Mech~Omega Devastator~Battlecry"
	requireTarget, effects, description = True, "", "Battlecry: If you have 10 Mana Crystals, deal 10 damage to a minion"
	name_CN = "欧米茄毁灭者"
	
	def needTarget(self, choice=0):
		return self.Game.Manas.manasUpper[self.ID] >= 10
		
	def effCanTrig(self):
		self.effectViable = self.Game.Manas.manasUpper[self.ID] >= 10 and self.targetExists()
		
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and self.Game.Manas.manasUpper[self.ID] >= 10:
			self.dealsDamage(target, 10)
		return target
		
		
class Wrenchcalibur(Weapon):
	Class, name, description = "Warrior", "Wrenchcalibur", "After your hero attacks, shuffle a Bomb into your Opponent's deck"
	mana, attack, durability, effects = 4, 3, 2, ""
	index = "DALARAN~Warrior~Weapon~4~3~2~Wrenchcalibur"
	name_CN = "圣剑扳手"
	trigBoard = Trig_Wrenchcalibur		


class BlastmasterBoom(Minion):
	Class, race, name = "Warrior", "", "Blastmaster Boom"
	mana, attack, health = 7, 7, 7
	index = "DALARAN~Warrior~Minion~7~7~7~~Blastmaster Boom~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: Summon two 1/1 Boom Bots for each Bomb in your opponent's deck"
	name_CN = "爆破之王砰砰"
	
	def effCanTrig(self):
		self.effectViable = any(card.name == "Bomb" for card in self.Game.Hand_Deck.decks[3-self.ID])
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if numSummon := min(8, 2 * sum(card.name == "Bomb" for card in self.Game.Hand_Deck.decks[3-self.ID])):
			self.summon([BoomBot(self.Game, self.ID) for i in range(numSummon)], relative="<>")
		
		
class DimensionalRipper(Spell):
	Class, school, name = "Warrior", "", "Dimensional Ripper"
	requireTarget, mana, effects = False, 10, ""
	index = "DALARAN~Warrior~Spell~10~~Dimensional Ripper"
	description = "Summon 2 copies of a minion in your deck"
	name_CN = "空间撕裂器"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if minions := [card for card in self.Game.Hand_Deck.decks[self.ID] if card.category == "Minion"]:
			minion = numpyChoice(minions)
			self.summon([minion.selfCopy(self.ID, self) for _ in (0, 1)])
		
		
class TheBoomReaver(Minion):
	Class, race, name = "Warrior", "Mech", "The Boom Reaver"
	mana, attack, health = 10, 7, 9
	index = "DALARAN~Warrior~Minion~10~7~9~Mech~The Boom Reaver~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: Summon a copy of a minion in your deck. Give it Rush"
	name_CN = "砰砰机甲"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.space(self.ID) > 0 and \
				(minions := [card for card in self.Game.Hand_Deck.decks[self.ID] if card.category == "Minion"]):
			if Copy := self.summon(numpyChoice(minions).selfCopy(self.ID, self)):
				self.giveEnchant(Copy, effGain="Rush", name=TheBoomReaver)
		
		
"""Game TrigEffects and Game Aura"""
class ThoridaltheStarsFury_Effect(TrigEffect):
	card, counter, trigType = ThoridaltheStarsFury, 2, "TurnEnd&OnlyKeepOne"
	def trigEffect(self):
		self.Game.heroes[self.ID].loeseEffect("Spell Damage", amount=self.counter)

class GameManaAura_Kalecgos(GameManaAura_OneTime):
	card, to = Kalecgos, 0
	def applicable(self, target): return target.ID == self.ID and target.category == "Spell"


Shadows_Cards = [
		#Neutral
		PotionVendor, Toxfin, ArcaneServant, DalaranLibrarian, EVILCableRat, HenchClanHogsteed, HenchClanSquire,
		ManaReservoir, SpellbookBinder, SunreaverSpy, ZayleShadowCloak, ArcaneWatcher, FacelessRager, FlightMaster, Gryphon,
		HenchClanSneak, MagicCarpet, SpellwardJeweler, ArchmageVargoth, Hecklebot, HenchClanHag, Amalgam, PortalKeeper,
		FelhoundPortal, Felhound, ProudDefender, SoldierofFortune, TravelingHealer, VioletSpellsword, AzeriteElemental,
		BaristaLynchen, DalaranCrusader, RecurringVillain, SunreaverWarmage, EccentricScribe, VengefulScroll, MadSummoner,
		Imp_Shadows, PortalOverfiend, Safeguard, VaultSafe, UnseenSaboteur, VioletWarden, ChefNomi, GreasefireElemental,
		ExoticMountseller, TunnelBlaster, UnderbellyOoze, Batterhead, HeroicInnkeeper, JepettoJoybuzz, WhirlwindTempest,
		BurlyShovelfist, ArchivistElysiana, BigBadArchmage,
		#Druid
		Acornbearer, Squirrel_Shadows, CrystalPower, PiercingThorns, HealingBlossom, CrystalsongPortal, DreamwayGuardians,
		CrystalDryad, KeeperStalladris, Lifeweaver, CrystalStag, BlessingoftheAncients, BlessingoftheAncients2, Lucentbark,
		TheForestsAid, TheForestsAid2, Treant_Shadows,
		#Hunter
		RapidFire, RapidFire2, Shimmerfly, NineLives, Ursatron, ArcaneFletcher, MarkedShot, HuntingParty, Oblivitron,
		UnleashtheBeast, UnleashtheBeast2, Wyvern, VereesaWindrunner, ThoridaltheStarsFury,
		#Mage
		RayofFrost, RayofFrost2, Khadgar, MagicDartFrog, MessengerRaven, MagicTrick, ConjurersCalling, ConjurersCalling2,
		KirinTorTricaster, ManaCyclone, PowerofCreation, Kalecgos,
		#Paladin
		NeverSurrender, LightforgedBlessing, LightforgedBlessing2, BronzeHerald, BronzeDragon, DesperateMeasures,
		DesperateMeasures2, MysteriousBlade, CalltoAdventure, DragonSpeaker, Duel, CommanderRhyssa, Nozari,
		#Priest
		EVILConscripter, HenchClanShadequill, UnsleepingSoul, ForbiddenWords, ConvincingInfiltrator, MassResurrection,
		LazulsScheme, ShadowyFigure, MadameLazul, CatrinaMuerte,
		#Rogue
		DaringEscape, EVILMiscreant, HenchClanBurglar, TogwagglesScheme, UnderbellyFence, Vendetta, WagglePick,
		UnidentifiedContract, AssassinsContract, LucrativeContract, RecruitmentContract, TurncoatContract,
		HeistbaronTogwaggle, TakNozwhisker,
		#Shaman
		Mutate, SludgeSlurper, SouloftheMurloc, UnderbellyAngler, HagathasScheme, WalkingFountain, WitchsBrew, Muckmorpher,
		Scargil, SwampqueenHagatha, DrustvarHorror,
		#Warlock
		EVILGenius, RafaamsScheme, AranasiBroodmother, PlotTwist, Impferno, EagerUnderling, DarkestHour, JumboImp,
		ArchVillainRafaam, FelLordBetrug,
		#Warrior
		ImproveMorale, ViciousScraphound, DrBoomsScheme, SweepingStrikes, ClockworkGoblin, OmegaDevastator, Wrenchcalibur,
		BlastmasterBoom, DimensionalRipper, TheBoomReaver,
]

Shadows_Cards_Collectible = [
		#Neutral
		PotionVendor, Toxfin, ArcaneServant, DalaranLibrarian, EVILCableRat, HenchClanHogsteed, ManaReservoir,
		SpellbookBinder, SunreaverSpy, ZayleShadowCloak, ArcaneWatcher, FacelessRager, FlightMaster, HenchClanSneak,
		MagicCarpet, SpellwardJeweler, ArchmageVargoth, Hecklebot, HenchClanHag, PortalKeeper, ProudDefender,
		SoldierofFortune, TravelingHealer, VioletSpellsword, AzeriteElemental, BaristaLynchen, DalaranCrusader,
		RecurringVillain, SunreaverWarmage, EccentricScribe, MadSummoner, PortalOverfiend, Safeguard, UnseenSaboteur,
		VioletWarden, ChefNomi, ExoticMountseller, TunnelBlaster, UnderbellyOoze, Batterhead, HeroicInnkeeper,
		JepettoJoybuzz, WhirlwindTempest, BurlyShovelfist, ArchivistElysiana, BigBadArchmage,
		#Druid
		Acornbearer, CrystalPower, CrystalsongPortal, DreamwayGuardians, KeeperStalladris, Lifeweaver, CrystalStag,
		BlessingoftheAncients, Lucentbark, TheForestsAid,
		#Hunter
		RapidFire, Shimmerfly, NineLives, Ursatron, ArcaneFletcher, MarkedShot, HuntingParty, Oblivitron, UnleashtheBeast,
		VereesaWindrunner,
		#Mage
		RayofFrost, Khadgar, MagicDartFrog, MessengerRaven, MagicTrick, ConjurersCalling, KirinTorTricaster, ManaCyclone,
		PowerofCreation, Kalecgos,
		#Paladin
		NeverSurrender, LightforgedBlessing, BronzeHerald, DesperateMeasures, MysteriousBlade, CalltoAdventure,
		DragonSpeaker, Duel, CommanderRhyssa, Nozari,
		#Priest
		EVILConscripter, HenchClanShadequill, UnsleepingSoul, ForbiddenWords, ConvincingInfiltrator, MassResurrection,
		LazulsScheme, ShadowyFigure, MadameLazul, CatrinaMuerte,
		#Rogue
		DaringEscape, EVILMiscreant, HenchClanBurglar, TogwagglesScheme, UnderbellyFence, Vendetta, WagglePick,
		UnidentifiedContract, HeistbaronTogwaggle, TakNozwhisker,
		#Shaman
		Mutate, SludgeSlurper, SouloftheMurloc, UnderbellyAngler, HagathasScheme, WalkingFountain, WitchsBrew, Muckmorpher,
		Scargil, SwampqueenHagatha,
		#Warlock
		EVILGenius, RafaamsScheme, AranasiBroodmother, PlotTwist, Impferno, EagerUnderling, DarkestHour, JumboImp,
		ArchVillainRafaam, FelLordBetrug,
		#Warrior
		ImproveMorale, ViciousScraphound, DrBoomsScheme, SweepingStrikes, ClockworkGoblin, OmegaDevastator, Wrenchcalibur,
		BlastmasterBoom, DimensionalRipper, TheBoomReaver,
]


TrigsDeaths_Shadows = {Death_HenchClanHogsteed: (HenchClanHogsteed, "Deathrattle: Summon a 1/1 Murloc"),
					   Death_RecurringVillain: (RecurringVillain, "Deathrattle: If this minion has 4 or more Attack, resummon it"),
					   Death_EccentricScribe: (EccentricScribe, "Deathrattle: Summon four 1/1 Vengeful Scrolls"),
					   Death_Safeguard: (Safeguard, "Deathrattle: Summon a 0/5 Vault Safe with Taunt"),
					   Death_TunnelBlaster: (TunnelBlaster, "Deathrattle: Deal 3 damage to all minions"),
					   Death_Acornbearer: (Acornbearer, "Deathrattle: Add two 1/1 Squirrels to your hand"),
					   Death_Lucentbark: (Lucentbark, "Deathrattle: Go dormant. Restore 5 Health to awaken this minion"),
					   Death_Shimmerfly: (Shimmerfly, "Deathrattle: Add a random Hunter spell to your hand"),
					   Death_Ursatron: (Ursatron, "Deathrattle: Draw a Mech from your deck"),
					   Death_Oblivitron: (Oblivitron, "Deathrattle: Summon a Mech from your hand and trigger its Deathrattle"),
					   Death_BronzeHerald: (BronzeHerald, "Deathrattle: Add Two 4/4 Bronze Dragons to your hand"),
					   Death_EVILConscripter: (EVILConscripter, "Deathrattle: Add A random Lackey to your hand"),
					   Death_HenchClanShadequill: (HenchClanShadequill, "Deathrattle: Restore 5 Health to the opponent hero"),
					   Death_ConvincingInfiltrator: (ConvincingInfiltrator, "Deathrattle: Destroy a random enemy minion"),
					   Death_WagglePick: (WagglePick, "Deathrattle: Return a random friendly minion to your hand. It costs (2) less"),
					   Death_SouloftheMurloc: (SouloftheMurloc, "Deathrattle: Summon a 1/1 Murloc"),
					   Death_EagerUnderling: (EagerUnderling, "Deathrattle: Give Two Random Friendly Minions +2/+2"),
					   }