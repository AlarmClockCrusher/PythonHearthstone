from Parts.CardTypes import *
from Parts.TrigsAuras import *
from HS_Cards.AcrossPacks import TheCoin, Claw, ArcaneMissiles
from HS_Cards.Core import TruesilverChampion
from HS_Cards.Shadows import EVILCableRat


class Aura_SkyClaw(Aura_AlwaysOn):
	attGain = 1
	def applicable(self, target): return "Mech" in target.race
		
	
class GameRuleAura_LivingDragonbreath(GameRuleAura):
	def auraAppears(self):
		self.keeper.Game.rules[self.keeper.ID]["Minions Can't Be Frozen"] += 1
		for minion in self.keeper.Game.minionsonBoard(self.keeper.ID):
			if minion.effects["Frozen"] > 0: minion.losesEffect("Frozen", amount=-1)
		
	def auraDisappears(self): self.keeper.Game.rules[self.keeper.ID]["Minions Can't Be Frozen"] -= 1
		
	
class GameRuleAura_DwarvenSharpshooter(GameRuleAura):
	def auraAppears(self): self.keeper.Game.powers[self.keeper.ID].getsEffect("Power Can Target Minions")
		
	def auraDisappears(self): self.keeper.Game.powers[self.keeper.ID].losesEffect("Power Can Target Minions")
		
	
class Death_TastyFlyfish(Deathrattle):
	description = "Deathrattle: Give a random Dragon in your hand +2/+2"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		if dragons := [card for card in kpr.Game.Hand_Deck.hands[kpr.ID] if "Dragon" in card.race]:
			kpr.giveEnchant(numpyChoice(dragons), 2, 2, source=TastyFlyfish, add2EventinGUI=False)
		
	
class Death_BadLuckAlbatross(Deathrattle):
	description = "Deathrattle: Shuffle two 1/1 Albatross into your opponent's deck"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		game, ID = (kpr := self.keeper).Game, 3-kpr.ID
		kpr.shuffleintoDeck([Albatross(game, ID) for _ in (0, 1)])
		
	
class Death_ChromaticEgg(Deathrattle):
	description, forceLeave = "Deathrattle: Hatch!", True
	def effect(self, signal, ID, subject, target, num, comment, choice):
		game, ID = (kpr := self.keeper).Game, kpr.ID
		if (m := self.memory) and kpr.category == "Minion" and kpr in game.minions[ID]:
			minion = m(game, ID)
			if kpr.onBoard: kpr.transform(kpr, minion)
			else: kpr.summon(minion)
		
	
class Death_LeperGnome_Dragons(Deathrattle):
	description = "Deathrattle: Deal 2 damage to the enemy hero"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).dealsDamage(kpr.Game.heroes[3 - kpr.ID], 2)
		
	
class Death_VioletSpellwing(Deathrattle):
	description = "Deathrattle: Add an 'Arcane Missile' to your hand"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.addCardtoHand(ArcaneMissiles, self.keeper.ID)
		
	
class Death_DragonriderTalritha(Deathrattle):
	description = "Deathrattle: Give a Dragon in your hand +3/+3 and this Deathrattle"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		if dragons := [card for card in kpr.Game.Hand_Deck.hands[kpr.ID] if "Dragon" in card.race]:
			kpr.giveEnchant(numpyChoice(dragons), 3, 3, source=DragonriderTalritha, trig=Death_DragonriderTalritha, trigType="Deathrattle", add2EventinGUI=False)
		
	
class Death_MindflayerKaahrj(Deathrattle):
	description = "Deathrattle: Summon a new copy of the chosen minion"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		if self.memory:
			game, ID = (kpr := self.keeper).Game, kpr.ID
			kpr.summon([game.fabCard(tup, ID, kpr) for tup in self.memory])
		
	
class Death_GraveRune(Deathrattle):
	description = "Deathrattle: Summon 2 copies of this"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		ID = (kpr := self.keeper).ID
		kpr.summon([kpr.copyCard(kpr, ID) for _ in (0, 1)])
		
	
class Death_Chronobreaker(Deathrattle):
	description = "Deathrattle: If you're holding a Dragon, deal 3 damage to all enemy minions"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		if (kpr := self.keeper).Game.Hand_Deck.holdingDragon(kpr.ID):
			kpr.dealsDamage(kpr.Game.minionsonBoard(3-kpr.ID), 3)
		
	
class Death_Waxadred(Deathrattle):
	description = "Deathrattle: Shuffle a Candle into your deck that resummons Waxadred when drawn"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).shuffleintoDeck(WaxadredsCandle(kpr.Game, kpr.ID))
		
	
class Trig_DepthCharge(TrigBoard):
	signals = ("TurnStarts",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).dealsDamage(kpr.Game.minionsonBoard(), 5)
		
	
class Trig_HotAirBalloon(TrigBoard):
	signals = ("TurnStarts",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).giveEnchant(kpr, statEnchant=Enchantment_Exclusive(HotAirBalloon, 0, 1))
		
	
class Trig_ParachuteBrigand(TrigHand):
	signals = ("CardBeenPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.inHand and ID == kpr.ID and "Pirate" in kpr.Game.cardinPlay.race
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		if self.keeper.Game.space(self.keeper.ID) > 0:
			self.keeper.Game.summonfrom(self.keeper.Game.Hand_Deck.hands[self.keeper.ID].index(self.keeper), self.keeper.ID, -1, self.keeper, hand_deck=0)
		
	
class Trig_Transmogrifier(TrigBoard):
	signals = ("CardDrawn",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and target[0].ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		#抽到“抽到时”触发的效果卡牌时，这个效果不会触发，直接变成传说随从，同时不会追加抽牌
		#源生宝典和远古谜团等卡牌抽到一张牌然后为期费用赋值等效果都会在变形效果生效之后进行赋值。
		#与其他“每当你抽一张xx牌”的扳机（如狂野兽王）共同在场时，是按照登场的先后顺序（扳机的正常顺序结算）。
		kpr.Game.Hand_Deck.replaceCardDrawn(target, numpyChoice(self.rngPool("Legendary Minions"))(kpr.Game, kpr.ID), kpr)
		
	
class Trig_DreadRaven(Trig_SelfAura):
	signals = ("MinionAppears", "MinionDisappears")
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and target.ID == kpr.ID and target.name == "Dread Raven"
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.calcStat()
		
	
class Trig_WingCommander(Trig_SelfAura):
	signals = ("HandCheck",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.calcStat()
		
	
class Trig_Shuma(TrigBoard):
	signals = ("TurnEnds",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		game, ID = (kpr := self.keeper).Game, kpr.ID
		kpr.summon([Tentacle_Dragons(game, ID) for i in range(6)], relative="<>")
		
	
class Trig_SecuretheDeck(Trig_Quest):
	signals = ("HeroAttackedHero", "HeroAttackedMinion",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return subject is kpr.Game.heroes[kpr.ID]
		
	
class Trig_StrengthinNumbers(Trig_Quest):
	signals = ("CardBeenPlayed",)
	def handleCounter(self, signal, ID, subject, target, num, comment, choice):
		self.counter += num[0]
		
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return comment == "Minion" and ID == self.keeper.ID and num[0] > 0
		
	
class Trig_Aeroponics(TrigHand):
	signals = ("MinionAppears", "MinionDisappears",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return self.keeper.inHand and target.name == "Treant"
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).Game.Manas.calcMana_Single(kpr)
		
	
class Trig_CleartheWay(Trig_Quest):
	signals = ("ObjBeenSummoned",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		#不知道召唤随从因为突袭光环而具有突袭是否可以算作任务进度
		return comment == "Minion" and ID == self.keeper.ID and subject.effects["Rush"] > 0
		
	
class Trig_ToxicReinforcement(Trig_Quest):
	signals = ("HeroUsedAbility",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return ID == self.keeper.ID
		
	
class Trig_PhaseStalker(TrigBoard):
	signals = ("HeroUsedAbility",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).Game.Secrets.deploySecretsfromDeck(kpr.ID, initiator=kpr)
		
	
class Trig_Stormhammer(Trig_SelfAura):
	signals = ("MinionAppears", "MinionDisappears")
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and target.ID == kpr.ID and "Dragon" in target.race
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.calcStat()
		
	
class Trig_Dragonbane(TrigBoard):
	signals = ("HeroUsedAbility",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		chars = kpr.Game.charsAlive(3-kpr.ID)
		if chars: self.keeper.dealsDamage(numpyChoice(chars), 5)
		
	
class Trig_ElementalAllies(Trig_Quest):
	signals = ("CardBeenPlayed", "TurnEnds",)
	def handleCounter(self, signal, ID, subject, target, num, comment, choice):
		if signal.startswith('T'): self.counter = 0
		else: self.counter += 1
		
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		elementalsThisTurn = kpr.Game.Counters.examCardPlays(kpr.ID, turnInd=kpr.Game.turnInd, cond=lambda tup: "Elemental" in tup[0])
		if signal == "TurnEnds": return kpr.ID == ID and not elementalsThisTurn
		else: return ID == kpr.ID and "Elemental" in kpr.Game.cardinPlay.race and not elementalsThisTurn
		
	
class Trig_LearnDraconic(Trig_Quest):
	signals = ("CardBeenPlayed",)
	def handleCounter(self, signal, ID, subject, target, num, comment, choice):
		self.counter += num[0]
		
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return comment == "Spell" and ID == kpr.ID and kpr is not kpr.Game.cardinPlay
		
	
class Trig_Chenvaala(Trig_Countdown):
	signals, counter = ("CardBeenPlayed", "NewTurnStarts"), 3
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and (signal == "NewTurnStarts" or (comment == "Spell" and ID == kpr.ID))
		
	def trig(self, signal, ID, subject, target, num, comment, choice):
		if self.canTrig(signal, ID, subject, target, num, comment, choice):
			counter = self.counter
			if signal == "NewTurnStarts": self.counter = 3
			else: self.counter -= 1
			if counter != self.counter and (btn := self.keeper.btn):
				btn.GUI.seqHolder[-1].append(btn.icons["Hourglass"].seqUpdateText())
			if self.counter < 1: self.keeper.summon(SnowElemental(self.keeper.Game, self.keeper.ID))
		
	
class Trig_ManaGiant(TrigHand):
	signals = ("CardBeenPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.inHand and ID == kpr.ID and kpr.Game.cardinPlay.creator
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).Game.Manas.calcMana_Single(kpr)
		
	
class Trig_RighteousCause(Trig_Quest):
	signals = ("ObjBeenSummoned",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return comment == "Minion" and ID == self.keeper.ID
		
	
class Trig_Sanctuary(Trig_Quest):
	signals = ("TurnStarts", "TurnEnds")
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr, turnInd = self.keeper, self.keeper.Game.turnInd
		return ID == kpr.ID and turnInd > 0 and kpr.Game.Counters.examDmgonHero(kpr.ID, turnInd=turnInd-1)
		
	
class Trig_CandleBreath(TrigHand):
	signals = ("HandCheck",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.inHand and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).Game.Manas.calcMana_Single(kpr)
		
	
class Trig_SurgingTempest(TrigBoard):
	signals = ("OverloadCheck",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.calcStat()
		
	
class Trig_Bandersmosh_PreShifting(TrigHand):
	signals = ("TurnStarts",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.inHand and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		minion = numpyChoice(self.rngPool("Legendary Minions"))(kpr.Game, kpr.ID)
		self.keeper.setStat(minion, (5, 5), source=Bandersmosh)
		ManaMod(minion, to=5).applies()
		(trig := Trig_Bandersmosh_KeepShifting(minion)).connect()  # 新的扳机保留这个变色龙的原有reference.在对方无手牌时会变回起始的变色龙。
		minion.trigsBoard.append(trig)
		kpr.Game.Hand_Deck.replace1CardinHand(kpr, minion)  # 只会注册手牌扳机，所以这个场上扳机需要自己注册
		
	
class Trig_Bandersmosh_KeepShifting(TrigBoard):
	signals = ("TurnStarts",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.inHand and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		minion = numpyChoice(self.rngPool("Legendary Minions"))(kpr.Game, kpr.ID)
		kpr.setStat(minion, (5, 5), source=Bandersmosh)
		ManaMod(minion, to=5).applies()
		(trig := Trig_Bandersmosh_KeepShifting(minion)).connect() #新的扳机保留这个变色龙的原有reference.在对方无手牌时会变回起始的变色龙。
		minion.trigsBoard.append(trig)
		kpr.Game.Hand_Deck.replace1CardinHand(kpr, minion) #只会注册手牌扳机，所以这个场上扳机需要自己注册
		
	
class Trig_StormEgg(TrigBoard):
	signals = ("TurnStarts",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).Game.transform(kpr, StormDrake(kpr.Game, kpr.ID))
		
	
class Trig_ZzerakutheWarped(TrigBoard):
	signals = ("HeroTakesDmg",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return ID == self.keeper.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).summon(NetherDrake(kpr.Game, kpr.ID))
		
	
class Trig_Ancharrr(TrigBoard):
	signals = ("BattleFinished",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return subject is kpr.Game.heroes[kpr.ID] and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.drawCertainCard(lambda card: "Pirate" in card.race)
		
	
class Trig_Skybarge(TrigBoard):
	signals = ("ObjBeenSummoned",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return "Pirate" in subject.race and ID == kpr.ID and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		chars = kpr.Game.charsAlive(3-kpr.ID)
		if chars: self.keeper.dealsDamage(numpyChoice(chars), 2)
		
	
class SwapHeroPowersBack(TrigEffect):
	trigType = "TurnStart"
	def trigEffect(self): self.card.swapHeroPowers()
		
	
class GameManaAura_BlowtorchSaboteur(GameManaAura_OneTime):
	to, temporary = 3, True
	def applicable(self, target): return target.ID == self.ID
		
	
class GameAura_GorutheMightree(GameAura_AlwaysOn):
	attGain, healthGain, counter = 1, 1, 1
	def applicable(self, target): return target.name == "True"
		
	def upgrade(self):
		self.attGain = self.healthGain = self.counter = self.counter + 1
		for receiver in self.receivers:
			receiver.attGain, receiver.healthGain = self.attGain, self.healthGain
			receiver.recipient.calcStat()
		if self.counter and self.card.btn: self.card.btn.trigAni(self.counter)
		
	
class GameManaAura_Dragoncaster(GameManaAura_OneTime):
	to = 0
	def applicable(self, target): return target.ID == self.ID and target.category == "Spell"
		
	
class Galakrond(Hero):
	mana, health, armor, upgrade = 7, 30, 5, None
	index = "Battlecry~Legendary~Uncollectible"
	@classmethod
	def getsInvoked(cls, card):
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
		Game, ID = card.Game, card.ID
		primaryGalakronds = Game.Counters.primGala
		gala = primaryGalakronds[ID]
		if gala:
			Class = gala.Class
			if "Priest" in Class:
				if Game.GUI: Game.GUI.showOffBoardTrig(GalakrondtheUnbreakable(Game, ID))
				gala.addCardtoHand(numpyChoice(Game.RNGPools["Priest Minions"]), ID, byType=True)
			elif "Rogue" in Class:
				if Game.GUI: Game.GUI.showOffBoardTrig(GalakrondtheNightmare(Game, ID))
				gala.addCardtoHand(numpyChoice(EVILCableRat.lackeys), ID, byType=True)
			elif "Shaman" in Class:
				if Game.GUI: Game.GUI.showOffBoardTrig(GalakrondtheTempest(Game, ID))
				gala.summon(WindsweptElemental(Game, ID))
			elif "Warlock" in Class:
				if Game.GUI: Game.GUI.showOffBoardTrig(GalakrondtheWretched(Game, ID))
				gala.summon([DraconicImp(Game, ID) for _ in (0, 1)])
			elif "Warrior" in Class:
				if Game.GUI: Game.GUI.showOffBoardTrig(GalakrondtheUnbreakable(Game, ID))
				gala.giveHeroAttackArmor(ID, attGain=3, source=GalakrondtheUnbreakable)
		#invocation counter increases and upgrade the galakronds
		Game.Counters.handleGameEvent("InvokeGalakrond", ID)
		for card in Game.Hand_Deck.hands[ID][:]:
			if "Galakrond, " in card.name:
				upgrade = card.upgradedGalakrond
				isPrimaryGalakrond = (card == gala)
				if hasattr(card, "progress"):
					card.progress += 1
					if upgrade and card.progress > 1:
						Game.Hand_Deck.replace1CardinHand(card, upgrade(Game, ID))
						if isPrimaryGalakrond:
							Game.Counters.primGala[ID] = upgrade
		inds, newCards = [], []
		for i, card in enumerate(Game.Hand_Deck.decks[ID]):
			if card.name.startswith("Galakrond, "):
				card.progress +=1
				if card.progress > 1 and (upgrade := type(card).upgrade):
					inds.append(i)
					up = upgrade(Game, ID)
					newCards.append(up)
					if card is gala: primaryGalakronds[ID] = up
		Game.Hand_Deck.replaceCardsinDeck(ID, inds, newCards)
		
	@classmethod
	def invokeTimes(cls, card):
		game, ID = card.Game, card.ID
		return sum(tup[0] == "InvokeGalakrond" and tup[1] == ID for tup in game.Counters.iter_TupsSoFar("events"))
		
	def entersHand(self, isGameEvent=True):
		if not (primGala := self.Game.Counters.primGala)[self.ID]:
			primGala[self.ID] = self
		return Card.entersHand(self, isGameEvent)
		
	def entersDeck(self):
		if not (primGala := self.Game.Counters.primGala)[self.ID]:
			primGala[self.ID] = self
		return Card.entersDeck(self)
		
	def replaceHero(self, fromHeroCard=False):
		self.Game.Counters.primGala[self.ID] = self
		super().replaceHero(True)
		
	def played(self, target=None, choice=0, mana=0, posinHand=0, comment=""): #英雄牌使用不存在触发发现的情况
		self.Game.Counters.primGala[self.ID] = self
		super().replaceHero(True)
		
	
class BlazingBattlemage(Minion):
	Class, race, name = "Neutral", "", "Blazing Battlemage"
	mana, attack, health = 1, 2, 2
	numTargets, Effects, description = 0, "", ""
	name_CN = "灼光战斗法师"
	
	
class DepthCharge(Minion):
	Class, race, name = "Neutral", "", "Depth Charge"
	mana, attack, health = 1, 0, 5
	numTargets, Effects, description = 0, "", "At the start of your turn, deal 5 damage to all minions"
	name_CN = "深潜炸弹"
	trigBoard = Trig_DepthCharge		
	
	
class HotAirBalloon(Minion):
	Class, race, name = "Neutral", "Mech", "Hot Air Balloon"
	mana, attack, health = 1, 1, 2
	numTargets, Effects, description = 0, "", "At the start of your turn, gain +1 Health"
	name_CN = "热气球"
	trigBoard = Trig_HotAirBalloon		
	
	
class EvasiveChimaera(Minion):
	Class, race, name = "Neutral", "Beast", "Evasive Chimaera"
	mana, attack, health = 2, 2, 1
	numTargets, Effects, description = 0, "Poisonous,Evasive", "Poisonous. Can't be targeted by spells or Hero Powers"
	name_CN = "辟法奇美拉"
	
	
class DragonBreeder(Minion):
	Class, race, name = "Neutral", "", "Dragon Breeder"
	mana, attack, health = 2, 2, 3
	numTargets, Effects, description = 1, "", "Battlecry: Choose a friendly Dragon. Add a copy of it to your hand"
	name_CN = "幼龙饲养员"
	index = "Battlecry"
	def effCanTrig(self):
		self.effectViable = False
		for minion in self.Game.minionsonBoard(self.ID):
			if "Dragon" in minion.race:
				self.effectViable = True
				break
		
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists(self.ID)
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.ID == self.ID and "Dragon" in obj.race and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.addCardtoHand(type(target[0]), self.ID)
		
	
class GrizzledWizard(Minion):
	Class, race, name = "Neutral", "", "Grizzled Wizard"
	mana, attack, health = 2, 3, 2
	name_CN = "灰发巫师"
	numTargets, Effects, description = 0, "", "Battlecry: Swap Hero Powers with your opponent until next turn"
	index = "Battlecry"
	trigEffect = SwapHeroPowersBack
	def swapHeroPowers(self):
		temp = self.Game.powers[1]
		self.Game.powers[1].disappears()
		self.Game.powers[2].disappears()
		self.Game.powers[1] = self.Game.powers[2]
		self.Game.powers[2] = temp
		self.Game.powers[1].appears()
		self.Game.powers[2].appears()
		self.Game.powers[1].ID, self.Game.powers[2].ID = 1, 2
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		#The Hero Powers are swapped at the start of your next turn
		GrizzledWizard.swapHeroPowers(self)
		SwapHeroPowersBack(self.Game, self.ID).connect()
		
	
class ParachuteBrigand(Minion):
	Class, race, name = "Neutral", "Pirate", "Parachute Brigand"
	mana, attack, health = 2, 2, 2
	numTargets, Effects, description = 0, "", "After you play a Pirate, summon this minion from your hand"
	name_CN = "空降歹徒"
	trigHand = Trig_ParachuteBrigand
	
	
class TastyFlyfish(Minion):
	Class, race, name = "Neutral", "Murloc", "Tasty Flyfish"
	mana, attack, health = 2, 2, 2
	numTargets, Effects, description = 0, "", "Deathrattle: Give a Dragon in your hand +2/+2"
	name_CN = "美味飞鱼"
	deathrattle = Death_TastyFlyfish
	
	
class Transmogrifier(Minion):
	Class, race, name = "Neutral", "", "Transmogrifier"
	mana, attack, health = 2, 2, 3
	numTargets, Effects, description = 0, "", "Whenever you draw a card, transform it into a random Legendary minion"
	name_CN = "幻化师"
	trigBoard = Trig_Transmogrifier
	poolIdentifier = "Legendary Minions"
	@classmethod
	def generatePool(cls, pools):
		return "Legendary Minions", pools.LegendaryMinions
		
	
class WyrmrestPurifier(Minion):
	Class, race, name = "Neutral", "", "Wyrmrest Purifier"
	mana, attack, health = 2, 3, 2
	name_CN = "龙眠净化者"
	numTargets, Effects, description = 0, "", "Battlecry: Transform all Neutral cards in your deck into random cards from your class"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		game = self.Game
		ownDeck = game.Hand_Deck.decks[self.ID]
		neutralIndices = [i for i, card in enumerate(ownDeck) if card.Class == "Neutral"]
		if neutralIndices:
			#不知道如果我方英雄没有职业时，变形成的牌是否会是中立。假设会变形成为随机职业
			newCards = numpyChoice(self.rngPool(class4Discover(self) + " Cards"), len(neutralIndices), replace=True)
			for i, newCard in zip(neutralIndices, newCards):
				game.Hand_Deck.extractfromDeck(i, self.ID)
				card = newCard(game, self.ID)
				ownDeck.insert(i, card)
				card.entersDeck()
		
	
class BlowtorchSaboteur(Minion):
	Class, race, name = "Neutral", "", "Blowtorch Saboteur"
	mana, attack, health = 3, 3, 4
	name_CN = "喷灯破坏者"
	numTargets, Effects, description = 0, "", "Battlecry: Your opponent's next Hero Power costs (3)"
	index = "Battlecry"
	trigEffect = GameManaAura_BlowtorchSaboteur
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.Game.Manas.PowerAuras_Backup.append(GameManaAura_BlowtorchSaboteur(self.Game, 3-self.ID))
		
	
class DreadRaven(Minion):
	Class, race, name = "Neutral", "Beast", "Dread Raven"
	mana, attack, health = 3, 3, 4
	numTargets, Effects, description = 0, "", "Has +3 Attack for each other Dread Raven you control"
	name_CN = "恐惧渡鸦"
	trigBoard = Trig_DreadRaven
	def statCheckResponse(self):
		if self.onBoard and not self.silenced:
			self.attack += 3 * sum(minion.name == "Dread Raven" for minion in self.Game.minionsonBoard(self.ID, exclude=self))
		
	
class FireHawk(Minion):
	Class, race, name = "Neutral", "Elemental", "Fire Hawk"
	mana, attack, health = 3, 1, 3
	name_CN = "火鹰"
	numTargets, Effects, description = 0, "", "Battlecry: Gain +1 Attack for each card in your opponent's hand"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(self, len(self.Game.Hand_Deck.hands[3 - self.ID]), 0, source=FireHawk)
		
	
class GoboglideTech(Minion):
	Class, race, name = "Neutral", "", "Goboglide Tech"
	mana, attack, health = 3, 3, 3
	name_CN = "地精滑翔技师"
	numTargets, Effects, description = 0, "", "Battlecry: If you control a Mech, gain +1/+1 and Rush"
	index = "Battlecry"
	def effCanTrig(self):
		self.effectViable = any("Mech" in minion.race for minion in self.Game.minionsonBoard(self.ID))
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if any("Mech" in minion.race for minion in self.Game.minionsonBoard(self.ID)):
			self.giveEnchant(self, 1, 1, effGain="Rush", source=GoboglideTech)
		
	
class LivingDragonbreath(Minion):
	Class, race, name = "Neutral", "Elemental", "Living Dragonbreath"
	mana, attack, health = 3, 3, 4
	numTargets, Effects, description = 0, "", "Your minions can't be Frozen"
	name_CN = "活化龙息"
	aura = GameRuleAura_LivingDragonbreath
	
	
class Scalerider(Minion):
	Class, race, name = "Neutral", "", "Scalerider"
	mana, attack, health = 3, 3, 3
	name_CN = "锐鳞骑士"
	numTargets, Effects, description = 1, "", "Battlecry: If you're holding a Dragon, deal 2 damage"
	index = "Battlecry"
	def numTargetsNeeded(self, choice=0):
		return 1 if self.Game.Hand_Deck.holdingDragon(self.ID) else 0
		
	def effCanTrig(self): #Friendly characters are always selectable.
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.Game.Hand_Deck.holdingDragon(self.ID): self.dealsDamage(target, 2)
		
	
class BadLuckAlbatross(Minion):
	Class, race, name = "Neutral", "Beast", "Bad Luck Albatross"
	mana, attack, health = 4, 4, 3
	numTargets, Effects, description = 0, "", "Deathrattle: Shuffle two 1/1 Albatross into your opponent's deck"
	name_CN = "厄运信天翁"
	deathrattle = Death_BadLuckAlbatross
	
	
class Albatross(Minion):
	Class, race, name = "Neutral", "Beast", "Albatross"
	mana, attack, health = 1, 1, 1
	name_CN = "信天翁"
	numTargets, Effects, description = 0, "", ""
	index = "Uncollectible"
	
	
class DevotedManiac(Minion):
	Class, race, name = "Neutral", "", "Devoted Maniac"
	mana, attack, health = 4, 2, 2
	name_CN = "虔诚信徒"
	numTargets, Effects, description = 0, "Rush", "Rush. Battlecry: Invoke Galakrond"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		Galakrond.getsInvoked(self)
		
	
class DragonmawPoacher(Minion):
	Class, race, name = "Neutral", "", "Dragonmaw Poacher"
	mana, attack, health = 4, 4, 4
	name_CN = "龙喉偷猎者"
	numTargets, Effects, description = 0, "", "Battlecry: If your opponent controls a Dragon, gain +4/+4 and Rush"
	index = "Battlecry"
	def effCanTrig(self):
		self.effectViable = any("Dragon" in minion.race for minion in self.Game.minionsonBoard(3-self.ID))
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if any("Dragon" in minion.race for minion in self.Game.minionsonBoard(3-self.ID)):
			self.giveEnchant(self, 4, 4, effGain="Rush", source=DragonmawPoacher)
		
	
class EvasiveFeywing(Minion):
	Class, race, name = "Neutral", "Dragon", "Evasive Feywing"
	mana, attack, health = 4, 5, 4
	numTargets, Effects, description = 0, "Evasive", "Can't be targeted by spells or Hero Powers"
	name_CN = "辟法灵龙"
	
	
class FrizzKindleroost(Minion):
	Class, race, name = "Neutral", "", "Frizz Kindleroost"
	mana, attack, health = 4, 5, 4
	name_CN = "弗瑞兹光巢"
	numTargets, Effects, description = 0, "", "Battlecry: Reduce the Cost of Dragons in your deck by (2)"
	index = "Battlecry~Legendary"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if card.category == "Minion" and "Dragon" in card.race:
				ManaMod(card, by=-2).applies()
		
	
class Hippogryph(Minion):
	Class, race, name = "Neutral", "Beast", "Hippogryph"
	mana, attack, health = 4, 2, 6
	numTargets, Effects, description = 0, "Rush,Taunt", "Rush, Taunt"
	name_CN = "角鹰兽"
	
	
class HoardPillager(Minion):
	Class, race, name = "Neutral", "Pirate", "Hoard Pillager"
	mana, attack, health = 4, 4, 2
	name_CN = "藏宝匪贼"
	numTargets, Effects, description = 0, "", "Battlecry: Equip one of your destroyed weapons"
	index = "Battlecry"
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.examDeads(self.ID, category="Weapon")
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if tups := self.Game.Counters.examDeads(self.ID, category="Weapon", veri_sum_ls=2):
			self.equipWeapon(self.Game.fabCard(numpyChoice(tups), self.ID, self))
		
	
class TrollBatrider(Minion):
	Class, race, name = "Neutral", "", "Troll Batrider"
	mana, attack, health = 4, 3, 3
	name_CN = "巨魔蝙蝠骑士"
	numTargets, Effects, description = 0, "", "Battlecry: Deal 3 damage to a random enemy minion"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		minions = self.Game.minionsAlive(3-self.ID)
		if minions: self.dealsDamage(numpyChoice(minions), 3)
		
	
class WingCommander(Minion):
	Class, race, name = "Neutral", "", "Wing Commander"
	mana, attack, health = 4, 2, 5
	numTargets, Effects, description = 0, "", "Has +2 Attack for each Dragon in your hand"
	name_CN = "空军指挥官"
	trigBoard = Trig_WingCommander
	def statCheckResponse(self):
		if self.onBoard and not self.silenced:
			self.attack += 2 * sum("Dragon" in minion.race for minion in self.Game.Hand_Deck.hands[self.ID])
		
	
class ZulDrakRitualist(Minion):
	Class, race, name = "Neutral", "", "Zul'Drak Ritualist"
	mana, attack, health = 4, 3, 9
	name_CN = "祖达克仪祭师"
	numTargets, Effects, description = 0, "Taunt", "Taunt. Battlecry: Summon three random 1-Cost minions for your opponent"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		minions = numpyChoice(self.rngPool("1-Cost Minions to Summon"), 3, replace=True)
		self.summon([minion(self.Game, 3-self.ID) for minion in minions])
		
	
class BigOlWhelp(Minion):
	Class, race, name = "Neutral", "Dragon", "Big Ol' Whelp"
	mana, attack, health = 5, 5, 5
	name_CN = "雏龙巨婴"
	numTargets, Effects, description = 0, "", "Battlecry: Draw a card"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.Game.Hand_Deck.drawCard(self.ID)
		
	
class ChromaticEgg(Minion):
	Class, race, name = "Neutral", "", "Chromatic Egg"
	mana, attack, health = 5, 0, 3
	name_CN = "多彩龙蛋"
	numTargets, Effects, description = 0, "", "Battlecry: Secretly Discover a Dragon to hatch into. Deathrattle: Hatch!"
	index = "Battlecry"
	deathrattle = Death_ChromaticEgg
	poolIdentifier = "Dragons as Druid to Summon"
	@classmethod
	def generatePool(cls, pools):
		identifiers, lists = genPool_MinionsofRaceasClass(pools, "Dragon")
		return [identifier+" to Summon" for identifier in identifiers], lists
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		card, _ = self.discoverNew(comment, lambda : self.rngPool("Dragons as %s to Summon"%class4Discover(self)), add2Hand=False)
		if card:
			for trig in self.deathrattles:
				if isinstance(trig, Death_ChromaticEgg): trig.memory = card
		
	
class CobaltSpellkin(Minion):
	Class, race, name = "Neutral", "Dragon", "Cobalt Spellkin"
	mana, attack, health = 5, 3, 5
	name_CN = "深蓝系咒师"
	numTargets, Effects, description = 0, "", "Battlecry: Add two 1-Cost spells from your class to your hand"
	index = "Battlecry"
	poolIdentifier = "1-Cost Druid Spells"
	@classmethod
	def generatePool(cls, pools):
		return ["1-Cost %s Spells"%Class for Class in pools.ClassCards], \
				[[card for card in cards if card.category == "Spell" and card.mana == 1] for cards in pools.ClassCards.values()]
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.addCardtoHand(numpyChoice(self.rngPool("1-Cost %s Spells"%self.Game.heroes[self.ID].Class), 2, replace=False), self.ID)
		
	
class FacelessCorruptor(Minion):
	Class, race, name = "Neutral", "", "Faceless Corruptor"
	mana, attack, health = 5, 4, 4
	name_CN = "无面腐蚀者"
	numTargets, Effects, description = 1, "Rush", "Rush. Battlecry: Transform one of your friendly minions into a copy of this"
	index = "Battlecry"
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists(self.ID)
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.ID == self.ID and obj is not self and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.transform(target, [self.copyCard(self, self.ID) for _ in target])
		
	
class KoboldStickyfinger(Minion):
	Class, race, name = "Neutral", "Pirate", "Kobold Stickyfinger"
	mana, attack, health = 5, 4, 4
	name_CN = "黏指狗头人"
	numTargets, Effects, description = 0, "", "Battlecry: Steal your opponent's weapon"
	index = "Battlecry"
	def effCanTrig(self):
		self.effectViable = self.Game.availableWeapon(3-self.ID)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		weapon = self.Game.availableWeapon(3-self.ID)
		if weapon:
			weapon.disappears()
			self.Game.weapons[3-self.ID].remove(weapon)
			weapon.ID = self.ID
			self.Game.equipWeapon(weapon)
		
	
class Platebreaker(Minion):
	Class, race, name = "Neutral", "", "Platebreaker"
	mana, attack, health = 5, 5, 5
	name_CN = "破甲骑士"
	numTargets, Effects, description = 0, "", "Battlecry: Destroy your opponent's Armor"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.Game.heroes[3-self.ID].armor = 0
		
	
class ShieldofGalakrond(Minion):
	Class, race, name = "Neutral", "", "Shield of Galakrond"
	mana, attack, health = 5, 4, 5
	name_CN = "迦拉克隆之盾"
	numTargets, Effects, description = 0, "Taunt", "Taunt. Battlecry: Invoke Galakrond"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		Galakrond.getsInvoked(self)
		
	
class Skyfin(Minion):
	Class, race, name = "Neutral", "Murloc", "Skyfin"
	mana, attack, health = 5, 3, 3
	name_CN = "飞天鱼人"
	numTargets, Effects, description = 0, "", "Battlecry: If you're holding a Dragon, summon 2 random Murlocs"
	index = "Battlecry"
	poolIdentifier = "Murlocs to Summon"
	@classmethod
	def generatePool(cls, pools):
		return "Murlocs to Summon", pools.MinionswithRace["Murloc"]
		
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.Game.Hand_Deck.holdingDragon(self.ID):
			murlocs = numpyChoice(self.rngPool("Murlocs to Summon"), 2, replace=True)
			self.summon([murloc(self.Game, self.ID) for murloc in murlocs], relative="<>")
		
	
class TentacledMenace(Minion):
	Class, race, name = "Neutral", "", "Tentacled Menace"
	mana, attack, health = 5, 6, 5
	name_CN = "触手恐吓者"
	numTargets, Effects, description = 0, "", "Battlecry: Each player draws a card. Swap their Costs"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		card1, mana1, entersHand1 = self.Game.Hand_Deck.drawCard(self.ID)
		card2, mana2, entersHand2 = self.Game.Hand_Deck.drawCard(3-self.ID)
		if card1 and card2:
			if entersHand1:
				ManaMod(card1, to=mana2).applies()
				self.Game.Manas.calcMana_Single(card1)
			if entersHand2:
				ManaMod(card2, to=mana1).applies()
				self.Game.Manas.calcMana_Single(card2)
		
	
class CamouflagedDirigible(Minion):
	Class, race, name = "Neutral", "Mech", "Camouflaged Dirigible"
	mana, attack, health = 6, 6, 6
	name_CN = "迷彩飞艇"
	numTargets, Effects, description = 0, "", "Battlecry: Give your other Mechs Stealth until your next turn"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for minion in self.Game.minionsonBoard(self.ID):
			if "Mech" in minion.race: minion.effects["Temp Stealth"] += 1
		
	
class EvasiveWyrm(Minion):
	Class, race, name = "Neutral", "Dragon", "Evasive Wyrm"
	mana, attack, health = 6, 5, 3
	numTargets, Effects, description = 0, "Divine Shield,Rush,Evasive", "Divine Shield, Rush. Can't be targeted by spells or Hero Powers"
	name_CN = "辟法巨龙"
	
	
class Gyrocopter(Minion):
	Class, race, name = "Neutral", "Mech", "Gyrocopter"
	mana, attack, health = 6, 4, 5
	numTargets, Effects, description = 0, "Rush,Windfury", "Rush, Windfury"
	name_CN = "旋翼机"
	
	
class KronxDragonhoof(Minion):
	Class, race, name = "Neutral", "", "Kronx Dragonhoof"
	mana, attack, health = 6, 6, 6
	name_CN = "克罗斯龙蹄"
	numTargets, Effects, description = 0, "", "Battlecry: Draw Galakrond. If you're alread Galakrond, unleash a Devastation"
	index = "Battlecry~Legendary"
	def effCanTrig(self):
		self.effectViable = "Galakrond" in self.Game.heroes[self.ID].name
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		#迦拉克隆有主迦拉克隆机制，祈求时只有主迦拉克隆会响应
		#主迦拉克隆会尽量与玩家职业匹配，如果不能匹配，则系统检测到的第一张迦拉克隆会被触发技能
		#http://nga.178.com/read.php?tid=19587242&rand=356
		game = self.Game
		if not game.heroes[self.ID].name.startswith("Galakrond"):
			self.drawCertainCard(lambda card: card.name.startswith("Galakrond, "))
		else:
			option = self.chooseFixedOptions(comment, options=[Annihilation(), Decimation(), Domination(), Reanimation()])
			if option.name == "Annihilation":
				self.dealsDamage(game.minionsonBoard(exclude=self), 5)
			elif option.name == "Decimation":
				self.dealsDamage(game.heroes[3-self.ID], 5)
				self.heals(game.heroes[self.ID], self.calcHeal(5))
			elif option.name == "Domination":
				self.giveEnchant(self.Game.minionsonBoard(self.ID, exclude=self), 2, 2, source=KronxDragonhoof)
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
	name_CN = "重生的巨龙"
	numTargets, Effects, description = 0, "", ""
	index = "Uncollectible"
	
	
class UtgardeGrapplesniper(Minion):
	Class, race, name = "Neutral", "", "Utgarde Grapplesniper"
	mana, attack, health = 6, 5, 5
	name_CN = "乌特加德鱼叉射手"
	numTargets, Effects, description = 0, "", "Battlecry: Both players draw a card. If it's a Dragon, summon it"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		game = self.Game
		card1, mana, entersHand1 = game.Hand_Deck.drawCard(self.ID)
		card2, mana, entersHand2 = game.Hand_Deck.drawCard(3-self.ID)
		hands = game.Hand_Deck.hands
		if entersHand1 and "Dragon" in card1.race and card1 in hands[self.ID]:
			game.summonfrom(hands[self.ID].index(card1), self.ID, -1, self, hand_deck=0) #不知道我方随从是会召唤到这个随从的右边还是场上最右边。
		if entersHand2 and "Dragon" in card2.race and card2 in hands[3-self.ID]:
			game.summonfrom(hands[3-self.ID].index(card2), 3-self.ID, -1, self, hand_deck=0)
		
	
class EvasiveDrakonid(Minion):
	Class, race, name = "Neutral", "Dragon", "Evasive Drakonid"
	mana, attack, health = 7, 7, 7
	numTargets, Effects, description = 0, "Taunt,Evasive", "Taunt. Can't be targeted by spells or Hero Powers"
	name_CN = "辟法龙人"
	
	
class Shuma(Minion):
	Class, race, name = "Neutral", "", "Shu'ma"
	mana, attack, health = 7, 1, 7
	name_CN = "舒玛"
	numTargets, Effects, description = 0, "", "At the end of your turn, fill your board with 1/1 Tentacles"
	index = "Legendary"
	trigBoard = Trig_Shuma		
	
	
class Tentacle_Dragons(Minion):
	Class, race, name = "Neutral", "", "Tentacle"
	mana, attack, health = 1, 1, 1
	name_CN = "触手"
	numTargets, Effects, description = 0, "", ""
	index = "Uncollectible"
	
	
class TwinTyrant(Minion):
	Class, race, name = "Neutral", "Dragon", "Twin Tyrant"
	mana, attack, health = 8, 4, 10
	name_CN = "双头暴虐龙"
	numTargets, Effects, description = 0, "", "Battlecry: Deal 4 damage to two random enemy minions"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if minions := self.Game.minionsAlive(3-self.ID):
			self.dealsDamage(numpyChoice(minions, min(2, len(minions)), replace=False), 4)
		
	
class DragonqueenAlexstrasza(Minion):
	Class, race, name = "Neutral", "Dragon", "Dragonqueen Alexstrasza"
	mana, attack, health = 9, 8, 8
	name_CN = "红龙女王阿莱克丝塔萨"
	numTargets, Effects, description = 0, "", "Battlecry: If your deck has no duplicates, add two Dragons to your hand. They cost (1)"
	index = "Battlecry~Legendary"
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.noDuplicatesinDeck(self.ID)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
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
	name_CN = "萨索瓦尔"
	numTargets, Effects, description = 1, "", "Battlecry: Choose a friendly minion. Add a copy of it to your hand, deck and battlefield"
	index = "Battlecry~Legendary"
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists(self.ID)
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.ID == self.ID and obj is not self and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for obj in target:
			self.addCardtoHand(self.copyCard(obj, self.ID, bareCopy=True), self.ID)
			self.shuffleintoDeck(self.copyCard(obj, self.ID, bareCopy=True))
			self.summon(self.copyCard(obj, self.ID), position=obj.pos+1)
		
	
class Embiggen(Spell):
	Class, school, name = "Druid", "Nature", "Embiggen"
	numTargets, mana, Effects = 0, 0, ""
	description = "Give all minions in your deck +2/+2. They cost (1) more (up to 10)"
	name_CN = "森然巨化"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		typeSelf = type(self)
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if card.category == "Minion":
				card.getsBuffDebuff_inDeck(2, 2, source=Embiggen)
				if card.mana < 10: ManaMod(card, by=+1).applies()
		
	
class SecuretheDeck(Quest):
	Class, school, name = "Druid", "", "Secure the Deck"
	numTargets, mana, Effects = 0, 1, ""
	description = "Sidequest: Attack twice with your hero. Reward: Add 3 'Claw' to your hand"
	name_CN = "保护甲板"
	numNeeded = 2
	race, trigBoard = "Sidequest", Trig_SecuretheDeck
	def questEffect(self, game, ID):
		self.addCardtoHand((Claw, Claw, Claw), ID)
		
	
class StrengthinNumbers(Quest):
	Class, school, name = "Druid", "", "Strength in Numbers"
	numTargets, mana, Effects = 0, 1, ""
	description = "Sidequest: Spend 10 Mana on minions. Rewards: Summon a minion from your deck"
	name_CN = "人多势众"
	numNeeded = 10
	race, trigBoard = "Sidequest", Trig_StrengthinNumbers
	def questEffect(self, game, ID):
		self.try_SummonfromOwn()
		
	
class SmallRepairs(Spell):
	Class, school, name = "Druid", "Nature", "Small Repairs"
	numTargets, mana, Effects = 1, 1, ""
	name_CN = "简单维修"
	description = "Give a minion +2 Health and Taunt"
	index = "Uncollectible"
	def available(self):
		return self.selectableMinionExists(0)
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(target, 0, 2, effGain="Taunt", source=SmallRepairs)
		
	
class SpinemUp(Spell):
	Class, school, name = "Druid", "Nature", "Spin 'em Up"
	numTargets, mana, Effects = 0, 1, ""
	name_CN = "旋叶起飞"
	description = "Summon a 2/2 Treant"
	index = "Uncollectible"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
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
	numTargets, mana, Effects = 1, 1, ""
	name_CN = "树木增援"
	description = "Choose One - Give a minion +2 Health and Taunt; or Summon a 2/2 Taunt"
	options = (SmallRepairs_Option, SpinemUp_Option)
	def numTargetsNeeded(self, choice=0):
		return 1 if choice < 1 else 0
		
	def available(self): #当场上有全选光环时，变成了一个指向性法术，必须要有一个目标可以施放。
		if self.Game.rules[self.ID]["Choose Both"] > 0: return self.selectableMinionExists()
		else: return self.selectableMinionExists() or self.Game.space(self.ID) > 0
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if choice < 1 and target: self.giveEnchant(target, 0, 2, effGain="Taunt", source=Treenforcements)
		if choice: self.summon(Treant_Dragons(self.Game, self.ID))
		
	
class BreathofDreams(Spell):
	Class, school, name = "Druid", "Nature", "Breath of Dreams"
	numTargets, mana, Effects = 0, 2, ""
	description = "Draw a card. If you're holding a Dragon, gain an empty Mana Crystal"
	name_CN = "梦境吐息"
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.Game.Hand_Deck.drawCard(self.ID)
		if self.Game.Hand_Deck.holdingDragon(self.ID):
			self.Game.Manas.gainEmptyManaCrystal(1, self.ID)
		
	
class Shrubadier(Minion):
	Class, race, name = "Druid", "", "Shrubadier"
	mana, attack, health = 2, 1, 1
	name_CN = "盆栽投手"
	numTargets, Effects, description = 0, "", "Battlecry: Summon a 2/2 Treant"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon(Treant_Dragons(self.Game, self.ID))
		
	
class Treant_Dragons(Minion):
	Class, race, name = "Druid", "", "Treant"
	mana, attack, health = 2, 2, 2
	name_CN = "树人"
	numTargets, Effects, description = 0, "", ""
	index = "Uncollectible"
	
	
class Aeroponics(Spell):
	Class, school, name = "Druid", "Nature", "Aeroponics"
	numTargets, mana, Effects = 0, 5, ""
	description = "Draw 2 cards. Costs (2) less for each Treant you control"
	name_CN = "空气栽培"
	trigHand = Trig_Aeroponics
	def selfManaChange(self):
		self.mana -= 2 * sum(minion.name == "Treant" for minion in self.Game.minionsonBoard(self.ID))
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.Game.Hand_Deck.drawCard(self.ID)
		self.Game.Hand_Deck.drawCard(self.ID)
		
	
class EmeraldExplorer(Minion):
	Class, race, name = "Druid", "Dragon", "Emerald Explorer"
	mana, attack, health = 6, 4, 8
	name_CN = "翡翠龙探险者"
	numTargets, Effects, description = 0, "Taunt", "Taunt. Battlecry: Discover a Dragon"
	index = "Battlecry"
	poolIdentifier = "Dragons as Druid"
	@classmethod
	def generatePool(cls, pools):
		return genPool_MinionsofRaceasClass(pools, "Dragon")
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.discoverNew(comment, lambda: self.rngPool("Dragons as "+class4Discover(self)))
		
	
class GorutheMightree(Minion):
	Class, race, name = "Druid", "", "Goru the Mightree"
	mana, attack, health = 7, 5, 10
	name_CN = "强力巨树格鲁"
	numTargets, Effects, description = 0, "Taunt", "Taunt. Battlecry: For the rest of the game, your Treants have +1/+1"
	index = "Battlecry~Legendary"
	trigEffect = GameAura_GorutheMightree
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		GameAura_GorutheMightree(self.Game, self.ID).auraAppears()
		
	
class YseraUnleashed(Minion):
	Class, race, name = "Druid", "Dragon", "Ysera, Unleashed"
	mana, attack, health = 9, 4, 12
	name_CN = "觉醒巨龙伊瑟拉"
	numTargets, Effects, description = 0, "", "Battlecry: Shuffle 7 Dream Portals into your deck. When drawn, summon a random Dragon"
	index = "Battlecry~Legendary"
	poolIdentifier = "Dragons to Summon"
	@classmethod
	def generatePool(cls, pools):
		return "Dragons to Summon", pools.MinionswithRace["Dragon"]
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.shuffleintoDeck([DreamPortal(self.Game, self.ID) for _ in range(7)])
		
	
class DreamPortal(Spell):
	Class, school, name = "Druid", "", "Dream Portal"
	numTargets, mana, Effects = 0, 9, ""
	name_CN = "梦境之门"
	description = "Casts When Drawn. Summon a random Dragon"
	index = "Uncollectible"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon(numpyChoice(self.rngPool("Dragons to Summon"))(self.Game, self.ID))
		
	
class CleartheWay(Quest):
	Class, school, name = "Hunter", "", "Clear the Way"
	numTargets, mana, Effects = 0, 1, ""
	description = "Sidequest: Summon 3 Rush minions. Reward: Summon a 4/4 Gryphon with Rush"
	name_CN = "扫清道路"
	numNeeded = 3
	race, trigBoard = "Sidequest", Trig_CleartheWay
	def questEffect(self, game, ID):
		self.summon(Gryphon_Dragons(game, ID))
		
	
class Gryphon_Dragons(Minion):
	Class, race, name = "Hunter", "Beast", "Gryphon"
	mana, attack, health = 4, 4, 4
	name_CN = "狮鹫"
	numTargets, Effects, description = 0, "Rush", "Rush"
	index = "Uncollectible"
	
	
class DwarvenSharpshooter(Minion):
	Class, race, name = "Hunter", "", "Dwarven Sharpshooter"
	mana, attack, health = 1, 1, 3
	numTargets, Effects, description = 0, "", "Your Hero Power can target minions"
	name_CN = "矮人神射手"
	aura = GameRuleAura_DwarvenSharpshooter
	
	
class ToxicReinforcements(Quest):
	Class, school, name = "Hunter", "", "Toxic Reinforcements"
	numTargets, mana, Effects = 0, 1, ""
	description = "Sidequest: Use your Hero Power three times. Reward: Summon three 1/1 Leper Gnomes"
	name_CN = "病毒增援"
	numNeeded = 3
	race, trigBoard = "Sidequest", Trig_ToxicReinforcement
	def questEffect(self, game, ID):
		self.summon([LeperGnome_Dragons(game, ID) for _ in (0, 1, 2)])
		
	
class LeperGnome_Dragons(Minion):
	Class, race, name = "Neutral", "", "Leper Gnome"
	mana, attack, health = 1, 2, 1
	name_CN = "麻风侏儒"
	numTargets, Effects, description = 0, "", "Deathrattle: Deal 2 damage to the enemy hero"
	index = "Uncollectible"
	deathrattle = Death_LeperGnome_Dragons
	
	
class CorrosiveBreath(Spell):
	Class, school, name = "Hunter", "Nature", "Corrosive Breath"
	numTargets, mana, Effects = 1, 2, ""
	description = "Deal 3 damage to a minion. If you're holding a Dragon, it also hits the enemy hero"
	name_CN = "腐蚀吐息"
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID)
		
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(target, damage := self.calcDamage(3))
		if self.Game.Hand_Deck.holdingDragon(self.ID):
			self.dealsDamage(self.Game.heroes[3-self.ID], damage)
		
	
class PhaseStalker(Minion):
	Class, race, name = "Hunter", "Beast", "Phase Stalker"
	mana, attack, health = 2, 2, 3
	numTargets, Effects, description = 0, "", "After you use your Hero Power, cast a Secret from your deck"
	name_CN = "相位追踪者"
	trigBoard = Trig_PhaseStalker		
	
	
class DivingGryphon(Minion):
	Class, race, name = "Hunter", "Beast", "Diving Gryphon"
	mana, attack, health = 3, 4, 1
	name_CN = "俯冲狮鹫"
	numTargets, Effects, description = 0, "Rush", "Rush. Battlecry: Draw a Rush minion from your deck"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.drawCertainCard(lambda card: card.category == "Minion" and card.effects["Rush"] > 0)
		
	
class PrimordialExplorer(Minion):
	Class, race, name = "Hunter", "Dragon", "Primordial Explorer"
	mana, attack, health = 3, 2, 3
	name_CN = "始生龙探险者"
	numTargets, Effects, description = 0, "Poisonous", "Poisonous. Battlecry: Discover a Dragon"
	index = "Battlecry"
	poolIdentifier = "Dragons as Hunter"
	@classmethod
	def generatePool(cls, pools):
		return genPool_MinionsofRaceasClass(pools, "Dragon")
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.discoverNew(comment, lambda: self.rngPool("Dragons as "+class4Discover(self)))
		
	
class Stormhammer(Weapon):
	Class, name, description = "Hunter", "Stormhammer", "Doesn't lose Durability while you control a Dragon"
	mana, attack, durability, Effects = 3, 3, 2, ""
	name_CN = "风暴之锤"
	trigBoard = Trig_Stormhammer
	def statCheckResponse(self):
		if self.onBoard and self.Game.minionsonBoard(self.ID, race="Dragon"):
			self.effects["Immune"] = 1
		else: self.effects["Immune"] = 0
		self.btn.effectChangeAni("Immune")
		
	
class Dragonbane(Minion):
	Class, race, name = "Hunter", "Mech", "Dragonbane"
	mana, attack, health = 4, 3, 5
	name_CN = "灭龙弩炮"
	numTargets, Effects, description = 0, "", "After you use your Hero Power, deal 5 damage to a random enemy"
	index = "Legendary"
	trigBoard = Trig_Dragonbane		
	
	
class Veranus(Minion):
	Class, race, name = "Hunter", "Dragon", "Veranus"
	mana, attack, health = 6, 7, 6
	name_CN = "维拉努斯"
	numTargets, Effects, description = 0, "", "Battlecry: Change the Health of all enemy minions to 1"
	index = "Battlecry~Legendary"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.setStat(self.Game.minionsonBoard(3 - self.ID), (None, 1), source=Veranus)
		
	
class ArcaneBreath(Spell):
	Class, school, name = "Mage", "Arcane", "Arcane Breath"
	numTargets, mana, Effects = 1, 1, ""
	description = "Deal 2 damage to a minion. If you're holding a Dragon, Discover a spell"
	name_CN = "奥术吐息"
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID)
		
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def text(self): return self.calcDamage(2)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(target, self.calcDamage(2))
		if self.Game.Hand_Deck.holdingDragon(self.ID):
			self.discoverNew(comment, lambda: self.rngPool(class4Discover(self)+" Spells"))
		
	
class ElementalAllies(Quest):
	Class, school, name = "Mage", "", "Elemental Allies"
	numTargets, mana, Effects = 0, 1, ""
	description = "Sidequest: Play an Elemental two turns in a row. Reward: Draw 3 spells from your deck"
	name_CN = "元素盟军"
	numNeeded = 2
	race, trigBoard = "Sidequest", Trig_ElementalAllies
	def questEffect(self, game, ID):
		for _ in (0, 1, 2):
			if not self.drawCertainCard(lambda card: card.category == "Spell")[0]: break
		
	
class LearnDraconic(Quest):
	Class, school, name = "Mage", "", "Learn Draconic"
	numTargets, mana, Effects = 0, 1, ""
	description = "Sidequest: Spend 8 Mana on spells. Reward: Summon a 6/6 Dragon"
	name_CN = "学习龙语"
	numNeeded = 8
	race, trigBoard = "Sidequest", Trig_LearnDraconic
	def questEffect(self, game, ID):
		self.summon(DraconicEmissary(game, ID))
		
	
class DraconicEmissary(Minion):
	Class, race, name = "Mage", "Dragon", "Draconic Emissary"
	mana, attack, health = 6, 6, 6
	name_CN = "龙族使者"
	numTargets, Effects, description = 0, "", ""
	index = "Uncollectible"
	
	
class VioletSpellwing(Minion):
	Class, race, name = "Mage", "Elemental", "Violet Spellwing"
	mana, attack, health = 1, 1, 1
	numTargets, Effects, description = 0, "", "Deathrattle: Add an 'Arcane Missile' to your hand"
	name_CN = "紫罗兰魔翼鸦"
	deathrattle = Death_VioletSpellwing#这个奥术飞弹是属于基础卡（无标志）
	
	
class Chenvaala(Minion):
	Class, race, name = "Mage", "Elemental", "Chenvaala"
	mana, attack, health = 3, 2, 5
	name_CN = "齐恩瓦拉"
	numTargets, Effects, description = 0, "", "After you cast three spells in a turn, summon a 5/5 Elemental"
	index = "Legendary"
	trigBoard = Trig_Chenvaala		
	
	
class SnowElemental(Minion):
	Class, race, name = "Mage", "Elemental", "Snow Elemental"
	mana, attack, health = 5, 5, 5
	name_CN = "冰雪元素"
	numTargets, Effects, description = 0, "", ""
	index = "Uncollectible"
	
	
class AzureExplorer(Minion):
	Class, race, name = "Mage", "Dragon", "Azure Explorer"
	mana, attack, health = 4, 2, 3
	name_CN = "碧蓝龙探险者"
	numTargets, Effects, description = 0, "Spell Damage_2", "Spell Damage +2. Battlecry: Discover a Dragon"
	index = "Battlecry"
	poolIdentifier = "Dragons as Mage"
	@classmethod
	def generatePool(cls, pools):
		return genPool_MinionsofRaceasClass(pools, "Dragon")
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.discoverNew(comment, lambda: self.rngPool("Dragons as " + class4Discover(self)))
		
	
class MalygossFrostbolt(Spell):
	Class, school, name = "Mage", "Arcane", "Malygos's Frostbolt"
	numTargets, mana, Effects = 1, 0, ""
	name_CN = "玛里苟斯的寒冰箭"
	description = "Deal 3 damage to a character and Freeze it"
	index = "Legendary~Uncollectible"
	def text(self): return self.calcDamage(3)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(target, self.calcDamage(3))
		self.freeze(target)
		
	
class MalygossMissiles(Spell):
	Class, school, name = "Mage", "Arcane", "Malygos's Missiles"
	numTargets, mana, Effects = 0, 1, ""
	name_CN = "玛里苟斯的奥术飞弹"
	description = "Deal 6 damage randomly split among all enemies"
	index = "Legendary~Uncollectible"
	def text(self): return self.calcDamage(6)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		side, game = 3-self.ID, self.Game
		for _ in range(self.calcDamage(6)):
			if objs := game.charsAlive(side): self.dealsDamage(numpyChoice(objs), 1)
			else: break
		
	
class MalygossNova(Spell):
	Class, school, name = "Mage", "Frost", "Malygos's Nova"
	numTargets, mana, Effects = 0, 1, ""
	name_CN = "玛里苟斯的霜冻新星"
	description = "Freeze all enemy minions"
	index = "Legendary~Uncollectible"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.freeze(self.Game.minionsonBoard(3-self.ID))
		
	
class MalygossPolymorph(Spell):
	Class, school, name = "Mage", "Arcane", "Malygos's Polymorph"
	numTargets, mana, Effects = 1, 1, ""
	name_CN = "玛里苟斯的变形术"
	description = "Transform a minion into a 1/1 Sheep"
	index = "Legendary~Uncollectible"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.Game.transform(target, [MalygossSheep(self.Game, obj.ID) for obj in target])
		
	
class MalygossTome(Spell):
	Class, school, name = "Mage", "Arcane", "Malygos's Tome"
	numTargets, mana, Effects = 0, 1, ""
	name_CN = "玛里苟斯的智慧秘典"
	description = "Add 3 random Mage spells to your hand"
	index = "Legendary~Uncollectible"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.addCardtoHand(numpyChoice(self.rngPool("Mage Spells"), 3, replace=True), self.ID)
		
	
class MalygossExplosion(Spell):
	Class, school, name = "Mage", "Arcane", "Malygos's Explosion"
	numTargets, mana, Effects = 0, 2, ""
	name_CN = "玛里苟斯的魔爆术"
	description = "Deal 2 damage to all enemy minions"
	index = "Legendary~Uncollectible"
	def text(self): return self.calcDamage(2)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(self.Game.minionsonBoard(3-self.ID), self.calcDamage(2))
		
	
class MalygossIntellect(Spell):
	Class, school, name = "Mage", "Arcane", "Malygos's Intellect"
	numTargets, mana, Effects = 0, 3, ""
	name_CN = "玛里苟斯的奥术智慧"
	description = "Draw 4 cards"
	index = "Legendary~Uncollectible"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for i in (0, 1, 2, 3): self.Game.Hand_Deck.drawCard(self.ID)
		
	
class MalygossFireball(Spell):
	Class, school, name = "Mage", "Fire", "Malygos's Fireball"
	numTargets, mana, Effects = 1, 4, ""
	name_CN = "玛里苟斯的火球术"
	description = "Deal 8 damage"
	index = "Legendary~Uncollectible"
	def text(self): return self.calcDamage(8)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(target, self.calcDamage(8))
		
	
class MalygossFlamestrike(Spell):
	Class, school, name = "Mage", "Fire", "Malygos's Flamestrike"
	numTargets, mana, Effects = 0, 7, ""
	name_CN = "玛里苟斯的烈焰风暴"
	description = "Deal 8 damage to all enemy minions"
	index = "Legendary~Uncollectible"
	def text(self): return self.calcDamage(8)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(self.Game.minionsonBoard(3-self.ID), self.calcDamage(8))
		
	
class MalygossSheep(Minion):
	Class, race, name = "Mage", "Beast", "Malygos's Sheep"
	mana, attack, health = 1, 1, 1
	name_CN = "玛里苟斯的绵羊"
	numTargets, Effects, description = 0, "", ""
	index = "Legendary~Uncollectible"
	
	
class MalygosAspectofMagic(Minion):
	Class, race, name = "Mage", "Dragon", "Malygos, Aspect of Magic"
	mana, attack, health = 5, 2, 8
	name_CN = "织法巨龙玛里苟斯"
	numTargets, Effects, description = 0, "", "Battlecry: If you're holding a Dragon, Discover an upgraded Mage spell"
	index = "Battlecry~Legendary"
	upgradedSpells = (MalygossFrostbolt, MalygossMissiles, MalygossNova, MalygossPolymorph, MalygossTome, MalygossExplosion, MalygossIntellect, MalygossFireball, MalygossFlamestrike)
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID, self)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.Game.Hand_Deck.holdingDragon(self.ID):
			self.discoverNew(comment, lambda: MalygosAspectofMagic.upgradedSpells)
		
	
class RollingFireball(Spell):
	Class, school, name = "Mage", "Fire", "Rolling Fireball"
	numTargets, mana, Effects = 1, 5, ""
	description = "Deal 8 damage to a minion. Any excess damage continues to the left or right"
	name_CN = "火球滚滚"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def text(self): return self.calcDamage(8)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for obj in target:
			obj, damage = obj, self.calcDamage(8)
			game = self.Game
			minion, direction, damageleft = None, "", damage
			damageDealt = min(obj.health, damageleft) if obj.health > 0 else 0
			damageleft -= damageDealt
			#火球滚滚会越过休眠物。直接打在相隔的其他随从上。圣盾随从会分担等于自己当前生命值的伤害。
			#火球滚滚打到牌库中的随从是没有任何后续效果的。不知道目标随从提前死亡的话会如何
			if obj.onBoard:
				neighbors, dist = game.neighbors2(obj, True) #对目标进行伤害之后，在场上寻找其相邻随从，决定滚动方向。
				#direction = 1 means fireball rolls right, direction = 1 is left
				if dist == 1:
					ran = numpyRandint(2) #ran == 1: roll right, 0: roll left
					minion, direction = neighbors[ran], ran
				elif dist < 0: minion, direction = neighbors[0], 0
				elif dist == 2: minion, direction = neighbors[0], 1
			else: #如果可以在手牌中找到那个随从时
				#火球滚滚打到手牌中的随从时，会判断目前那个随从在手牌中位置，如果在从左数第3张的话，那么会将过量伤害传递给场上的2号或者4号随从。
				try: i = game.Hand_Deck.hands[obj.ID].index(obj)
				except ValueError: i = -1
				if i > -1:
					minions = game.minionsonBoard(3-self.ID) #对手牌中的随从进行伤害之后，寻找场上合适的随从并确定滚动方向。
					if minions:
						if not i: minion, direction = minions[1] if len(minions) > 1 else None, 1
						elif i + 1 < len(minions): #手牌中第4张（编号3），如果场上有5张随从，仍然随机
							if numpyRandint(2): minion, direction = minions[i+1], 1
							else: minion, direction = minions[i-1], 0
						#如果随从在手牌中的编号很大，如手牌中第5张（编号4），则如果场上有5张或者以下随从，则都会向左滚
						else: minion, direction = minions[-1], 0
			self.dealsDamage(obj, damageDealt)
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
					minion = neighbors[0] if dist in (1, -1) else None
		
	
class Dragoncaster(Minion):
	Class, race, name = "Mage", "", "Dragoncaster"
	mana, attack, health = 7, 4, 4
	name_CN = "乘龙法师"
	numTargets, Effects, description = 0, "", "Battlecry: If you're holding a Dragon, your next spell this turn costs (0)"
	index = "Battlecry"
	trigEffect = GameManaAura_Dragoncaster
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.Game.Hand_Deck.holdingDragon(self.ID):
			GameManaAura_Dragoncaster(self.Game, self.ID).auraAppears()
		
	
class ManaGiant(Minion):
	Class, race, name = "Mage", "Elemental", "Mana Giant"
	mana, attack, health = 8, 8, 8
	numTargets, Effects, description = 0, "", "Costs (1) less for each card you've played this game that didn't start in your deck"
	name_CN = "法力巨人"
	trigHand = Trig_ManaGiant
	def selfManaChange(self):
		self.mana -= self.Game.Counters.examCardPlays(self.ID, veri_sum_ls=1, cond=lambda tup: tup[6])
		
	
class RighteousCause(Quest):
	Class, school, name = "Paladin", "", "Righteous Cause"
	numTargets, mana, Effects = 0, 1, ""
	description = "Sidequest: Summon 5 minions. Reward: Give your minions +1/+1"
	name_CN = "正义感召"
	numNeeded = 5
	race, trigBoard = "Sidequest", Trig_RighteousCause
	def questEffect(self, game, ID):
		self.giveEnchant(self.Game.minionsonBoard(self.ID), 1, 1, source=RighteousCause)
		
	
class SandBreath(Spell):
	Class, school, name = "Paladin", "", "Sand Breath"
	numTargets, mana, Effects = 1, 1, ""
	description = "Give a minion +1/+2. Give it Divine Shield if you're holding a Dragon"
	name_CN = "沙尘吐息"
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID)
		
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		effGain = "Divine Shield" if self.Game.Hand_Deck.holdingDragon(self.ID) else ''
		self.giveEnchant(target, 1, 2, effGain=effGain, source=SandBreath)
		
	
class Sanctuary(Quest):
	Class, school, name = "Paladin", "", "Sanctuary"
	numTargets, mana, Effects = 0, 2, ""
	description = "Sidequest: Take no damage for a turn. Reward: Summon a 3/6 minion with Taunt"
	name_CN = "庇护"
	numNeeded = 1
	race, trigBoard = "Sidequest", Trig_Sanctuary
	def questEffect(self, game, ID):
		self.summon(IndomitableChampion(game, ID))
		
	
class IndomitableChampion(Minion):
	Class, race, name = "Paladin", "", "Indomitable Champion"
	mana, attack, health = 4, 3, 6
	name_CN = "不屈的勇士"
	numTargets, Effects, description = 0, "Taunt", "Taunt"
	index = "Uncollectible"
	
	
class BronzeExplorer(Minion):
	Class, race, name = "Paladin", "Dragon", "Bronze Explorer"
	mana, attack, health = 3, 2, 3
	name_CN = "青铜龙探险者"
	numTargets, Effects, description = 0, "Lifesteal", "Lifesteal. Battlecry: Discover a Dragon"
	index = "Battlecry"
	poolIdentifier = "Dragons as Paladin"
	@classmethod
	def generatePool(cls, pools):
		return genPool_MinionsofRaceasClass(pools, "Dragon")
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.discoverNew(comment, lambda: self.rngPool("Dragons as "+class4Discover(self)))
		
	
class SkyClaw(Minion):
	Class, race, name = "Paladin", "Mech", "Sky Claw"
	mana, attack, health = 3, 1, 2
	name_CN = "空中飞爪"
	numTargets, Effects, description = 0, "", "Your other Mechs have +1 Attack. Battlecry: Summon two 1/1 Microcopters"
	index = "Battlecry"
	aura = Aura_SkyClaw
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon([Microcopter(self.Game, self.ID) for _ in (0, 1)], relative="<>")
		
	
class Microcopter(Minion):
	Class, race, name = "Paladin", "Mech", "Microcopter"
	mana, attack, health = 1, 1, 1
	name_CN = "微型旋翼机"
	numTargets, Effects, description = 0, "", ""
	index = "Uncollectible"
	
	
class DragonriderTalritha(Minion):
	Class, race, name = "Paladin", "", "Dragonrider Talritha"
	mana, attack, health = 3, 3, 3
	name_CN = "龙骑士塔瑞萨"
	numTargets, Effects, description = 0, "", "Deathrattle: Give a Dragon in your hand +3/+3 and this Deathrattle"
	index = "Legendary"
	deathrattle = Death_DragonriderTalritha
	
	
class LightforgedZealot(Minion):
	Class, race, name = "Paladin", "", "Lightforged Zealot"
	mana, attack, health = 4, 4, 2
	name_CN = "光铸狂热者"
	numTargets, Effects, description = 0, "", "Battlecry: If your deck has no Neutral cards, equip a 4/2 Truesilver Champion"
	index = "Battlecry"
	def effCanTrig(self):
		self.effectViable = all(card.Class != "Neutral" for card in self.Game.Hand_Deck.decks[self.ID])
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if all(card.Class != "Neutral" for card in self.Game.Hand_Deck.decks[self.ID]):
			self.equipWeapon(TruesilverChampion(self.Game, self.ID))
		
	
class NozdormutheTimeless(Minion):
	Class, race, name = "Paladin", "Dragon", "Nozdormu the Timeless"
	mana, attack, health = 4, 8, 8
	name_CN = "时光巨龙诺兹多姆"
	numTargets, Effects, description = 0, "", "Battlecry: Set each player to 10 Mana Crystals"
	index = "Battlecry~Legendary"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.Game.Manas.setManaCrystal(10, 1)
		self.Game.Manas.setManaCrystal(10, 2)
		
	
class AmberWatcher(Minion):
	Class, race, name = "Paladin", "Dragon", "Amber Watcher"
	mana, attack, health = 5, 4, 6
	name_CN = "琥珀看守者"
	numTargets, Effects, description = 1, "", "Battlecry: Restore 8 Health"
	index = "Battlecry"
	def text(self): return self.calcHeal(8)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.heals(target, self.calcHeal(8))
		
	
class LightforgedCrusader(Minion):
	Class, race, name = "Paladin", "", "Lightforged Crusader"
	mana, attack, health = 7, 7, 7
	name_CN = "光铸远征军"
	numTargets, Effects, description = 0, "", "Battlecry: If your deck has no Neutral cards, add 5 random Paladin cards to your hand"
	index = "Battlecry"
	def effCanTrig(self):
		self.effectViable = True
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if card.Class == "Neutral":
				self.effectViable = False
				break
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if all(card.Class != "Neutral" for card in self.Game.Hand_Deck.decks[self.ID]):
			self.addCardtoHand(numpyChoice(self.rngPool("Paladin Cards"), 5, replace=True), self.ID)
		
	
class WhispersofEVIL(Spell):
	Class, school, name = "Priest", "", "Whispers of EVIL"
	numTargets, mana, Effects = 0, 0, ""
	description = "Add a Lackey to your hand"
	name_CN = "怪盗低语"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.addCardtoHand(numpyChoice(EVILCableRat.lackeys), self.ID)
		
	
class DiscipleofGalakrond(Minion):
	Class, race, name = "Priest", "", "Disciple of Galakrond"
	mana, attack, health = 1, 1, 2
	name_CN = "迦拉克隆的信徒"
	numTargets, Effects, description = 0, "", "Battlecry: Invoke Galakrond"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		Galakrond.getsInvoked(self)
		
	
class EnvoyofLazul(Minion):
	Class, race, name = "Priest", "", "Envoy of Lazul"
	mana, attack, health = 2, 2, 2
	name_CN = "拉祖尔的信使"
	numTargets, Effects, description = 0, "", "Battlecry: Look at 3 cards. Guess which one is in your opponent's hand to get a copy of it"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		#One card current in opponent's hand( can be created card). Two other cards are the ones currently in opponent's deck but not in hand.
		#If less than two cards left in opponent's deck, two copies of cards in opponent's starting deck is given.
		pass
		
	
class BreathoftheInfinite(Spell):
	Class, school, name = "Priest", "", "Breath of the Infinite"
	numTargets, mana, Effects = 0, 3, ""
	description = "Deal 2 damage to all minions. If you're holding a Dragon, only damage enemies"
	name_CN = "永恒吐息"
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID)
		
	def text(self): return self.calcDamage(2)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		objs = self.Game.minionsonBoard(3-self.ID if self.Game.Hand_Deck.holdingDragon(self.ID) else 0)
		self.dealsDamage(objs, self.calcDamage(2))
		
	
class MindflayerKaahrj(Minion):
	Class, race, name = "Priest", "", "Mindflayer Kaahrj"
	mana, attack, health = 3, 3, 3
	name_CN = "夺心者卡什"
	numTargets, Effects, description = 1, "", "Battlecry: Choose an enemy minion. Deathrattle: Summon a new copy of it"
	index = "Battlecry~Legendary"
	deathrattle = Death_MindflayerKaahrj
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists(3 - self.ID)
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.ID != self.ID and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for obj in target:
			tup = obj.getBareInfo()
			for trig in self.deathrattles:
				if isinstance(trig, Death_MindflayerKaahrj): trig.memory.append(tup)
		
	
class FateWeaver(Minion):
	Class, race, name = "Priest", "Dragon", "Fate Weaver"
	mana, attack, health = 4, 3, 6
	name_CN = "命运编织者"
	numTargets, Effects, description = 0, "", "Battlecry: If you've Invoked twice, reduce the Cost of cards in your hand by (1)"
	index = "Battlecry"
	def effCanTrig(self):
		self.effectViable = Galakrond.invokeTimes(self) > 1
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if Galakrond.invokeTimes(self) > 1:
			for card in self.Game.Hand_Deck.hands[self.ID]: ManaMod(card, by=-1).applies()
		
	
class GraveRune(Spell):
	Class, school, name = "Priest", "Shadow", "Grave Rune"
	numTargets, mana, Effects = 1, 4, ""
	description = "Give a minion 'Deathrattle: Summon 2 copies of this'"
	name_CN = "墓地符文"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(target, trig=Death_GraveRune, trigType="Deathrattle")
		
	
class Chronobreaker(Minion):
	Class, race, name = "Priest", "Dragon", "Chronobreaker"
	mana, attack, health = 5, 4, 5
	numTargets, Effects, description = 0, "", "Deathrattle: If you're holding a Dragon, deal 3 damage to all enemy minions"
	name_CN = "时空破坏者"
	deathrattle = Death_Chronobreaker
	
	
class TimeRip(Spell):
	Class, school, name = "Priest", "", "Time Rip"
	numTargets, mana, Effects = 1, 5, ""
	description = "Destroy a minion. Invoke Galakrond"
	name_CN = "时空裂痕"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.Game.kill(self, target)
		Galakrond.getsInvoked(self)
		
	
class GalakrondsWit(Power):
	mana, name, numTargets = 2, "Galakrond's Wit", 0
	description = "Add a random Priest minion to your hand"
	name_CN = "迦拉克隆的智识"
	def available(self, choice=0):
		return not (self.chancesUsedUp() or self.Game.Hand_Deck.handNotFull(self.ID))
		
	def effect(self, target=(), choice=0, comment=''):
		self.addCardtoHand(numpyChoice(self.rngPool("Priest Minions")), self.ID)
		
	
class GalakrondAzerothsEnd_Priest(Galakrond):
	Class, heroPower = "Priest", GalakrondsWit
	name, description = "Galakrond, Azeroth's End", "Battlecry: Destroy 4 random enemy minions. Equip a 5/2 Claw"
	name_CN = "世界末日迦拉克隆"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if minions := self.Game.minionsAlive(3 - self.ID):
			objs = numpyChoice(minions, min(4, len(minions)), replace=False)
			self.Game.kill(self, objs)
		self.equipWeapon(DragonClaw(self.Game, self.ID))
		
	
class GalakrondtheApocalypes_Priest(GalakrondAzerothsEnd_Priest):
	name, description = "Galakrond, the Apocalypes", "Battlecry: Destroy 2 random enemy minions. (Invoke twice to upgrade)"
	name_CN = "天降浩劫迦拉克隆"
	upgrade = GalakrondAzerothsEnd_Priest
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if minions := self.Game.minionsAlive(3 - self.ID):
			objs = numpyChoice(minions, min(2, len(minions)), replace=False)
			self.Game.kill(self, objs)
		
	
class GalakrondtheUnspeakable(GalakrondAzerothsEnd_Priest):
	name, description = "Galakrond, the Unspeakable", "Battlecry: Destroy a random enemy minion. (Invoke twice to upgrade)"
	name_CN = "讳言巨龙迦拉克隆"
	index = "Battlecry~Legendary"
	upgrade = GalakrondtheApocalypes_Priest
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if minions := self.Game.minionsAlive(3-self.ID): self.Game.kill(self, numpyChoice(minions))
		
	
class DragonClaw(Weapon):
	Class, name, description = "Neutral", "Dragon Claw", ""
	mana, attack, durability, Effects = 5, 5, 2, ""
	name_CN = "巨龙之爪"
	index = "Uncollectible"
	
	
class MurozondtheInfinite(Minion):
	Class, race, name = "Priest", "Dragon", "Murozond the Infinite"
	mana, attack, health = 8, 8, 8
	name_CN = "永恒巨龙姆诺兹多"
	numTargets, Effects, description = 0, "", "Battlecry: Play all cards your opponent played last turn"
	index = "Battlecry~Legendary"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		#施放顺序是随机的。在姆诺兹多死亡之后，依然可以进行施放。如果姆诺兹多被对方控制，则改为施放我方上回合打出的牌。
		#https://www.bilibili.com/video/av87286050?from=search&seid=5979238121000536259
		#当我方拥有Choose Both光环的时候，复制对方打出的单个抉择的随从和法术： 随从仍然是单个抉择的结果，但是法术是拥有全选效果的。
		#如果对方打出了全选抉择的随从，但是我方没有Choose Both光环，那么我方复制会得到全抉择的随从，而法术则是随机抉择。
		#与苔丝的效果类似，对于随从是直接复制其打出结果。
		#姆诺兹多的战吼没有打出牌的张数的限制。
		#无法复制被法反掉的法术，因为那个法术不算作对方打出过的牌（被直接取消）。
		#打出一个元素被对方的变形药水奥秘变形为绵羊后，下个回合仍然可以触发元素链。说明打出一张牌人记录是在最终“打出一张随从后”扳机结算前
		#同时姆诺兹多能复制抉择变形随从的变形目标说明打出随从牌的记录是在战吼/抉择等之后。
		game = self.Game
		curTurn = game.turn
		tupstoReplay = {curTurn: game.Counters.examCardPlays(curTurn, veri_sum_ls=2, turnInd=game.pastTurnInd(3-curTurn)),
						3-curTurn: game.Counters.examCardPlays(curTurn, veri_sum_ls=2, turnInd=game.pastTurnInd(curTurn))}
		numpyShuffle(tupstoReplay[1])
		numpyShuffle(tupstoReplay[2])
		while tupstoReplay[3-self.ID]:
			self.replayCard_fromTup(tupstoReplay[3-self.ID].pop())
		
	
class BloodsailFlybooter(Minion):
	Class, race, name = "Rogue", "Pirate", "Bloodsail Flybooter"
	mana, attack, health = 1, 1, 1
	name_CN = "血帆飞贼"
	numTargets, Effects, description = 0, "", "Battlecry: Add two 1/1 Pirates to your hand"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.addCardtoHand([SkyPirate, SkyPirate], self.ID)
		
	
class SkyPirate(Minion):
	Class, race, name = "Rogue", "Pirate", "Sky Pirate"
	mana, attack, health = 1, 1, 1
	name_CN = "空中海盗"
	numTargets, Effects, description = 0, "", ""
	index = "Uncollectible"
	
	
class DragonsHoard(Spell):
	Class, school, name = "Rogue", "", "Dragon's Hoard"
	numTargets, mana, Effects = 0, 1, ""
	description = "Discover a Legendary minion from another class"
	name_CN = "巨龙宝藏"
	poolIdentifier = "Class Legendary Minions"
	@classmethod
	def generatePool(cls, pools):
		return "Class Legendary Minions", [card for card in pools.LegendaryMinions if card.Class != "Neutral"]
		
	def decideLegendaryPool(self):
		heroClass = self.Game.heroes[self.ID].Class
		return [card for card in self.rngPool("Class Legendary Minions") if heroClass not in card.Class]
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		#可以发现相同职业的随机，所以发现池是在一起的
		self.discoverNew(comment, lambda : DragonsHoard.decideLegendaryPool(self))
		
	
class PraiseGalakrond(Spell):
	Class, school, name = "Rogue", "", "Praise Galakrond!"
	numTargets, mana, Effects = 1, 1, ""
	description = "Give a minion +1 Attack. Invoke Galakrond"
	name_CN = "赞美迦拉克隆"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(target, 1, 0, source=PraiseGalakrond)
		Galakrond.getsInvoked(self)
		
	
class SealFate(Spell):
	Class, school, name = "Rogue", "", "Seal Fate"
	numTargets, mana, Effects = 1, 3, ""
	description = "Deal 3 damage to an undamaged character. Invoke Galakrond"
	name_CN = "封印命运"
	def text(self): return self.calcDamage(3)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(target, self.calcDamage(3))
		Galakrond.getsInvoked(self)
		
	
class UmbralSkulker(Minion):
	Class, race, name = "Rogue", "", "Umbral Skulker"
	mana, attack, health = 4, 3, 3
	name_CN = "幽影潜藏者"
	numTargets, Effects, description = 0, "", "Battlecry: If you've Invoked twice, add 3 Coins to your hand"
	index = "Battlecry"
	def effCanTrig(self):
		self.effectViable = Galakrond.invokeTimes(self) > 1
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if Galakrond.invokeTimes(self) > 1: self.addCardtoHand([TheCoin]*3, self.ID)
		
	
class NecriumApothecary(Minion):
	Class, race, name = "Rogue", "", "Necrium Apothecary"
	mana, attack, health = 5, 2, 5
	name_CN = "死金药剂师"
	numTargets, Effects, description = 0, "", "Combo: Draw a Deathrattle minion from your deck and gain its Deathrattle"
	index = "Combo"
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.comboCounters[self.ID] > 0
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.Game.Counters.comboCounters[self.ID] > 0:
			if minion := self.drawCertainCard(lambda card: card.category == "Minion" and card.deathrattles)[0]:
				self.giveEnchant(self, trigs=[(type(trig), "Deathrattle") for trig in minion.deathrattles])
		
	
class Stowaway(Minion):
	Class, race, name = "Rogue", "", "Stowaway"
	mana, attack, health = 5, 4, 4
	name_CN = "偷渡者"
	numTargets, Effects, description = 0, "", "Battlecry: If there are cards in your deck that didn't start there, draw 2 of them"
	index = "Battlecry"
	def effCanTrig(self):
		return any(card.creator for card in self.Game.Hand_Deck.decks[self.ID])
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for _ in (0, 1):
			if not self.drawCertainCard(lambda card: card.creator)[0]: break
		
	
class Waxadred(Minion):
	Class, race, name = "Rogue", "Dragon", "Waxadred"
	mana, attack, health = 5, 7, 5
	name_CN = "蜡烛巨龙"
	numTargets, Effects, description = 0, "", "Deathrattle: Shuffle a Candle into your deck that resummons Waxadred when drawn"
	index = "Legendary"
	deathrattle = Death_Waxadred
	
	
class WaxadredsCandle(Spell):
	Class, school, name = "Rogue", "", "Waxadred's Candle"
	numTargets, mana, Effects = 0, 5, ""
	name_CN = "巨龙的蜡烛"
	description = "Casts When Drawn. Summon Waxadred"
	index = "Uncollectible"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon(Waxadred(self.Game, self.ID))
		
	
class CandleBreath(Spell):
	Class, school, name = "Rogue", "Fire", "Candle Breath"
	numTargets, mana, Effects = 0, 6, ""
	description = "Draw 3 cards. Costs (3) less while you're holding a Dragon"
	name_CN = "烛火吐息"
	trigHand = Trig_CandleBreath
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID)
		
	def selfManaChange(self):
		if self.Game.Hand_Deck.holdingDragon(self.ID): self.mana -= 3
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for _ in (0, 1, 2): self.Game.Hand_Deck.drawCard(self.ID)
		
	
class FlikSkyshiv(Minion):
	Class, race, name = "Rogue", "", "Flik Skyshiv"
	mana, attack, health = 6, 4, 4
	name_CN = "菲里克·飞刺"
	numTargets, Effects, description = 1, "", "Battlecry: Destroy a minion and all copies of it (wherever they are)"
	index = "Battlecry~Legendary"
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj is not self and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		#飞刺的战吼会摧毁所有同名卡，即使有些不是随从，如法师的扰咒术奥秘和随从，镜像法术和其衍生物
		HD = self.Game.Hand_Deck
		for obj in target:
			for ID in (1, 2):
				self.Game.kill(self, [o for o in self.Game.minionsonBoard(ID) if o.name == obj.name])
				for i in reversed(range(len(HD.decks[ID]))):
					if HD.decks[ID][i].name == obj.name: HD.extractfromDeck(i, ID, animate=False)
				for i in reversed(range(len(HD.hands[ID]))):
					if HD.hands[ID][i].name == obj.name: HD.extractfromHand(i, ID, enemyCanSee=True)
		
	
class GalakrondsGuile(Power):
	mana, name, numTargets = 2, "Galakrond's Guile", 0
	description = "Add a Lackey to your hand"
	name_CN = "迦拉克隆的诡计"
	def available(self, choice=0):
		return not (self.chancesUsedUp() or self.Game.Hand_Deck.handNotFull(self.ID))
		
	def effect(self, target=(), choice=0, comment=''):
		self.addCardtoHand(numpyChoice(EVILCableRat.lackeys), self.ID)
		
	
class GalakrondAzerothsEnd_Rogue(Galakrond):
	Class, heroPower = "Rogue", GalakrondsGuile
	name, description = "Galakrond, Azeroth's End", "Battlecry: Draw 4 cards. They cost (1). Equip a 5/2 Claw"
	name_CN = "世界末日迦拉克隆"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for i in (0, 1, 2, 3):
			card, mana, entersHand = self.Game.Hand_Deck.drawCard(self.ID)
			if entersHand: ManaMod(card, to=1).applies()
		self.equipWeapon(DragonClaw(self.Game, self.ID))
		
	
class GalakrondtheApocalypes_Rogue(GalakrondAzerothsEnd_Rogue):
	name, description = "Galakrond, the Apocalypes", "Battlecry: Draw 2 cards. They cost (1). (Invoke twice to upgrade)"
	name_CN = "天降浩劫迦拉克隆"
	upgrade = GalakrondAzerothsEnd_Rogue
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for _ in (0, 1):
			card, mana, entersHand = self.Game.Hand_Deck.drawCard(self.ID)
			if entersHand: ManaMod(card, to=1).applies()
		
	
class GalakrondtheNightmare(GalakrondAzerothsEnd_Rogue):
	name, description = "Galakrond, the Nightmare", "Battlecry: Draw 2 cards. They cost (1). (Invoke twice to upgrade)"
	name_CN = "天降浩劫迦拉克隆"
	index = "Battlecry~Legendary"
	upgrade = GalakrondtheApocalypes_Rogue
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		card, mana, entersHand = self.Game.Hand_Deck.drawCard(self.ID)
		if entersHand: ManaMod(card, to=1).applies()
		
	
class InvocationofFrost(Spell):
	Class, school, name = "Shaman", "Frost", "Invocation of Frost"
	numTargets, mana, Effects = 1, 2, ""
	description = "Freeze a minion. Invoke Galakrond"
	name_CN = "霜之祈咒"
	def available(self):
		return self.selectableCharExists(3 - self.ID)
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" or obj.category == "Hero" and obj.onBoard and obj.ID != self.ID
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.freeze(target)
		Galakrond.getsInvoked(self)
		
	
class SurgingTempest(Minion):
	Class, race, name = "Shaman", "Elemental", "Surging Tempest"
	mana, attack, health = 1, 1, 3
	numTargets, Effects, description = 0, "", "Has +1 Attack while you have Overloaded Mana Crystals"
	name_CN = "电涌风暴"
	trigBoard = Trig_SurgingTempest
	def statCheckResponse(self):
		if self.onBoard and not self.silenced and \
				(self.Game.Manas.manasOverloaded[self.ID] > 0 or self.Game.Manas.manasLocked[self.ID] > 0):
			self.attack += 1
		
	
class Squallhunter(Minion):
	Class, race, name = "Shaman", "Dragon", "Squallhunter"
	mana, attack, health = 4, 5, 7
	numTargets, Effects, description = 0, "Spell Damage_2", "Spell Damage +2, Overload: (2)"
	name_CN = "猎风巨龙"
	overload = 2
	
	
class StormsWrath(Spell):
	Class, school, name = "Shaman", "Nature", "Storm's Wrath"
	numTargets, mana, Effects = 0, 1, ""
	description = "Give your minions +1/+1. Overload: (1)"
	name_CN = "风暴之怒"
	overload = 2
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(self.Game.minionsonBoard(self.ID), 1, 1, source=StormsWrath)
		
	
class LightningBreath(Spell):
	Class, school, name = "Shaman", "Nature", "Lightning Breath"
	numTargets, mana, Effects = 1, 3, ""
	description = "Deal 4 damage to a minion. If you're holding a Dragon, also damage its neighbors"
	name_CN = "闪电吐息"
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID)
		
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def text(self): return self.calcDamage(4)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		damage = self.calcDamage(4)
		for obj in target:
			if self.Game.Hand_Deck.holdingDragon(self.ID): objs = [obj]+self.Game.neighbors2(obj)[0]
			else: objs = (obj,)
			self.dealsDamage(objs, damage)
		
	
class Bandersmosh(Minion):
	Class, race, name = "Shaman", "", "Bandersmosh"
	mana, attack, health = 5, 5, 5
	numTargets, Effects, description = 0, "", "Each turn this is in your hand, transform it into a 5/5 random Legendary minion"
	name_CN = "班德斯莫什"
	trigHand, trigEffect = Trig_Bandersmosh_PreShifting, Trig_Bandersmosh_KeepShifting
	poolIdentifier = "Legendary Minions"
	@classmethod
	def generatePool(cls, pools):
		return "Legendary Minions", pools.LegendaryMinions
		
	
class CumuloMaximus(Minion):
	Class, race, name = "Shaman", "Elemental", "Cumulo-Maximus"
	mana, attack, health = 5, 5, 5
	name_CN = "遮天雨云"
	numTargets, Effects, description = 1, "", "Battlecry: If you have Overloaded Mana Crystals, deal 5 damage"
	index = "Battlecry"
	def numTargetsNeeded(self, choice=0):
		return 1 if self.Game.Manas.manasLocked[self.ID] > 0 or self.Game.Manas.manasOverloaded[self.ID] > 0 else 0
		
	def effCanTrig(self):
		self.effectViable = self.Game.Manas.manasLocked[self.ID] + self.Game.Manas.manasOverloaded[self.ID] > 0
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.Game.Manas.manasLocked[self.ID] > 0 or self.Game.Manas.manasOverloaded[self.ID] > 0:
			self.dealsDamage(target, 5)
		
	
class DragonsPack(Spell):
	Class, school, name = "Shaman", "Nature", "Dragon's Pack"
	numTargets, mana, Effects = 0, 5, ""
	description = "Summon two 2/3 Spirit Wolves with Taunt. If you've Invoked Galakrond twice, give them +2/+2"
	name_CN = "巨龙的兽群"
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def effCanTrig(self): #法术先检测是否可以使用才判断是否显示黄色
		self.effectViable = Galakrond.invokeTimes(self) > 1
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon((minions := [SpiritWolf_Dragons(self.Game, self.ID) for _ in (0, 1)]))
		if Galakrond.invokeTimes(self) > 1: self.giveEnchant(minions, 2, 2, source=DragonsPack)
		
	
class SpiritWolf_Dragons(Minion):
	Class, race, name = "Shaman", "", "Spirit Wolf"
	mana, attack, health = 2, 2, 3
	name_CN = "幽灵狼"
	numTargets, Effects, description = 0, "Taunt", "Taunt"
	index = "Uncollectible"
	
	
class CorruptElementalist(Minion):
	Class, race, name = "Shaman", "", "Corrupt Elementalist"
	mana, attack, health = 6, 3, 3
	name_CN = "堕落的元素师"
	numTargets, Effects, description = 0, "", "Battlecry: Invoke Galakrond twice"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		Galakrond.getsInvoked(self)
		Galakrond.getsInvoked(self)
		
	
class Nithogg(Minion):
	Class, race, name = "Shaman", "Dragon", "Nithogg"
	mana, attack, health = 6, 5, 5
	name_CN = "尼索格"
	numTargets, Effects, description = 0, "", "Battlecry: Summon two 0/3 Eggs. Next turn they hatch into 4/4 Drakes with Rush"
	index = "Battlecry~Legendary"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon([StormEgg(self.Game, self.ID) for _ in (0, 1)], relative="<>")
		
	
class StormEgg(Minion):
	Class, race, name = "Shaman", "", "Storm Egg"
	mana, attack, health = 1, 0, 3
	name_CN = "风暴龙卵"
	numTargets, Effects, description = 0, "", "At the start of your turn, transform into a 4/4 Storm Drake with Rush"
	index = "Uncollectible"
	trigBoard = Trig_StormEgg		
	
	
class StormDrake(Minion):
	Class, race, name = "Shaman", "Dragon", "Storm Drake"
	mana, attack, health = 4, 4, 4
	name_CN = "风暴幼龙"
	numTargets, Effects, description = 0, "Rush", "Rush"
	index = "Uncollectible"
	
	
class GalakrondsFury(Power):
	mana, name, numTargets = 2, "Galakrond's Fury", 0
	description = "Summon a 2/1 Elemental with Rush"
	name_CN = "迦拉克隆的愤怒"
	def available(self):
		return not self.chancesUsedUp() and self.Game.space(self.ID)
		
	def effect(self, target=(), choice=0, comment=''):
		self.summon(WindsweptElemental(self.Game, self.ID))
		
	
class WindsweptElemental(Minion):
	Class, race, name = "Shaman", "Elemental", "Windswept Elemental"
	mana, attack, health = 2, 2, 1
	name_CN = "风啸元素"
	numTargets, Effects, description = 0, "Rush", "Rush"
	index = "Uncollectible"
	
	
class GalakrondAzerothsEnd_Shaman(Galakrond):
	Class, heroPower = "Shaman", GalakrondsFury
	name, description = "Galakrond, Azeroth's End", "Battlecry: Summon two 8/8 Storms with Rush. Equip a 5/2 Claw"
	name_CN = "世界末日迦拉克隆"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon([RagingStorm(self.Game, self.ID) for _ in (0, 1)])
		self.equipWeapon(DragonClaw(self.Game, self.ID))
		
	
class GalakrondtheApocalypes_Shaman(GalakrondAzerothsEnd_Shaman):
	name, description = "Galakrond, the Apocalypes", "Battlecry: Summon two 4/4 Storms with Rush. (Invoke twice to upgrade)"
	name_CN = "天降浩劫迦拉克隆"
	upgrade = GalakrondAzerothsEnd_Shaman
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon([LivingStorm(self.Game, self.ID) for _ in (0, 1)])
		
	
class GalakrondtheTempest(GalakrondAzerothsEnd_Shaman):
	name, description = "Galakrond, the Tempest", "Battlecry: Summon two 4/4 Storms with Rush. (Invoke twice to upgrade)"
	name_CN = "风暴巨龙迦拉克隆"
	index = "Battlecry~Legendary"
	upgrade = GalakrondtheApocalypes_Shaman
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon([BrewingStorm(self.Game, self.ID) for _ in (0, 1)])
		
	
class BrewingStorm(Minion):
	Class, race, name = "Shaman", "Elemental", "Brewing Storm"
	mana, attack, health = 2, 2, 2
	name_CN = "成型风暴"
	numTargets, Effects, description = 0, "Rush", "Rush"
	index = "Uncollectible"
	
	
class LivingStorm(Minion):
	Class, race, name = "Shaman", "Elemental", "Living Storm"
	mana, attack, health = 4, 4, 4
	name_CN = "活体风暴"
	numTargets, Effects, description = 0, "Rush", "Rush"
	index = "Uncollectible"
	
	
class RagingStorm(Minion):
	Class, race, name = "Shaman", "Elemental", "Raging Storm"
	mana, attack, health = 8, 8, 8
	name_CN = "狂怒风暴"
	numTargets, Effects, description = 0, "Rush", "Rush"
	index = "Uncollectible"
	
	
class RainofFire(Spell):
	Class, school, name = "Warlock", "Fel", "Rain of Fire"
	numTargets, mana, Effects = 0, 1, ""
	description = "Deal 1 damage to all characters"
	name_CN = "火焰之雨"
	def text(self): return self.calcDamage(1)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(self.Game.minionsonBoard(), self.calcDamage(1))
		
	
class NetherBreath(Spell):
	Class, school, name = "Warlock", "Fel", "Nether Breath"
	numTargets, mana, Effects = 1, 2, ""
	description = "Deal 2 damage. If you're holding a Dragon, deal 4 damage with Lifesteal instead"
	name_CN = "虚空吐息"
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID)
		
	def text(self): return "%d, %d"%(self.calcDamage(2), self.calcDamage(4))
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.Game.Hand_Deck.holdingDragon(self.ID): base, self.effects["Lifesteal"] = 4, 1
		else: base = 2
		self.dealsDamage(target, self.calcDamage(base))
		
	
class DarkSkies(Spell):
	Class, school, name = "Warlock", "Fel", "Dark Skies"
	numTargets, mana, Effects = 0, 3, ""
	description = "Deal 1 damage to a random minion. Repeat for each card in your hand"
	name_CN = "黑暗天际"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		damage = self.calcDamage(1)
		game = self.Game
		#在使用这个法术后先打一次，然后检测手牌数。总伤害个数是手牌数+1
		if minions := game.minionsAlive():
			self.dealsDamage(numpyChoice(minions), damage)
			for _ in range(len(game.Hand_Deck.hands[self.ID])):
				if minions := self.Game.minionsAlive(): self.dealsDamage(numpyChoice(minions), damage)
				else: break
		
	
class DragonblightCultist(Minion):
	Class, race, name = "Warlock", "", "Dragonblight Cultist"
	mana, attack, health = 3, 1, 1
	name_CN = "龙骨荒野异教徒"
	numTargets, Effects, description = 0, "", "Battlecry: Invoke Galakrond. Gain +1 Attack for each other friendly minion"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		Galakrond.getsInvoked(self)
		if (self.onBoard or self.inHand) and (num := len(self.Game.minionsAlive(self.ID, self))):
			self.giveEnchant(self, num, 0, source=DragonblightCultist)
		
	
class FiendishRites(Spell):
	Class, school, name = "Warlock", "", "Fiendish Rites"
	numTargets, mana, Effects = 0, 4, ""
	description = "Invoke Galakrond. Give your minions +1 Attack"
	name_CN = "邪鬼仪式"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		Galakrond.getsInvoked(self)
		self.giveEnchant(self.Game.minionsonBoard(self.ID), 1, 0, source=FiendishRites)
		
	
class VeiledWorshipper(Minion):
	Class, race, name = "Warlock", "", "Veiled Worshipper"
	mana, attack, health = 4, 5, 4
	name_CN = "暗藏的信徒"
	numTargets, Effects, description = 0, "", "Battlecry: If you've Invoked twice, draw 3 cards"
	index = "Battlecry"
	def effCanTrig(self):
		self.effectViable = Galakrond.invokeTimes(self) > 1
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if Galakrond.invokeTimes(self) > 1:
			for _ in (0, 1, 2): self.Game.Hand_Deck.drawCard(self.ID)
		
	
class CrazedNetherwing(Minion):
	Class, race, name = "Warlock", "Dragon", "Crazed Netherwing"
	mana, attack, health = 5, 5, 5
	name_CN = "疯狂的灵翼龙"
	numTargets, Effects, description = 0, "", "Battlecry: If you're holding a Dragon, deal 3 dammage to all other characters"
	index = "Battlecry"
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID, self)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.Game.Hand_Deck.holdingDragon(self.ID):
			self.dealsDamage(self.Game.charsonBoard(exclude=self), 3)
		
	
class AbyssalSummoner(Minion):
	Class, race, name = "Warlock", "", "Abyssal Summoner"
	mana, attack, health = 6, 2, 2
	name_CN = "深渊召唤者"
	numTargets, Effects, description = 0, "", "Battlecry: Summon a Demon with Taunt and stats equal to your hand size"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if size := len(self.Game.Hand_Deck.hands[self.ID]):
			minion = AbyssalDestroyer(self.Game, self.ID)
			minion.mana_0 = min(size, 10)
			minion.attack_0 = minion.health_0 = minion.attack = minion.health = size
			self.summon(minion)
		
	
class AbyssalDestroyer(Minion):
	Class, race, name = "Warlock", "Demon", "Abyssal Destroyer"
	mana, attack, health = 1, 1, 1
	name_CN = "深渊毁灭者"
	numTargets, Effects, description = 0, "Taunt", "Taunt"
	index = "Uncollectible"
	
	
class GalakrondsMalice(Power):
	mana, name, numTargets = 2, "Galakrond's Malice", 0
	description = "Summon two 1/1 Imps"
	name_CN = "迦拉克隆的恶意"
	def available(self):
		return not self.chancesUsedUp() and self.Game.space(self.ID) > 0
		
	def effect(self, target=(), choice=0, comment=''):
		self.summon([DraconicImp(self.Game, self.ID) for _ in (0, 1)])
		
	
class DraconicImp(Minion):
	Class, race, name = "Warlock", "Demon", "Draconic Imp"
	mana, attack, health = 1, 1, 1
	numTargets, Effects, description = 0, "", ""
	name_CN = "龙裔小鬼"
	index = "Uncollectible"
	
	
class GalakrondAzerothsEnd_Warlock(Galakrond):
	Class, heroPower = "Warlock", GalakrondsMalice
	name, description = "Galakrond, Azeroth's End", "Battlecry: Summon 4 random Demons. Equip a 5/2 Claw"
	name_CN = "世界末日迦拉克隆"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		demons = numpyChoice(self.rngPool("Demons to Summon"), 4, replace=True)
		self.summon([demon(self.Game, self.ID) for demon in demons])
		self.equipWeapon(DragonClaw(self.Game, self.ID))
		
	
class GalakrondtheApocalypes_Warlock(GalakrondAzerothsEnd_Warlock):
	name, description = "Galakrond, the Apocalypes", "Battlecry: Summon 2 random Demons. (Invoke twice to upgrade)"
	name_CN = "天降浩劫迦拉克隆"
	upgrade = GalakrondAzerothsEnd_Warlock
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		demons = numpyChoice(self.rngPool("Demons to Summon"), 2, replace=True)
		self.summon([demon(self.Game, self.ID) for demon in demons])
		
	
class GalakrondtheWretched(GalakrondAzerothsEnd_Warlock):
	name, description = "Galakrond, the Wretched", "Battlecry: Summon a random Demon. (Invoke twice to upgrade)"
	name_CN = "邪火巨龙迦拉克隆"
	index = "Battlecry~Legendary"
	upgrade = GalakrondtheApocalypes_Warlock
	poolIdentifier = "Demons to Summon"
	@classmethod
	def generatePool(cls, pools):
		return "Demons to Summon", pools.MinionswithRace["Demon"]
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon(numpyChoice(self.rngPool("Demons to Summon"))(self.Game, self.ID))
		
	
class ValdrisFelgorge(Minion):
	Class, race, name = "Warlock", "", "Valdris Felgorge"
	mana, attack, health = 7, 4, 4
	numTargets, Effects, description = 0, "", "Battlecry: Increase your maximum hand size to 12. Draw 4 cards"
	name_CN = "瓦迪瑞斯·邪噬"
	index = "Battlecry~Legendary"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.Game.Hand_Deck.handUpperLimits[self.ID] = 12
		self.Game.sendSignal("HandUpperLimitChange", self.ID)
		for i in (0, 1, 2, 3): self.Game.Hand_Deck.drawCard(self.ID)
		
	
class ZzerakutheWarped(Minion):
	Class, race, name = "Warlock", "Dragon", "Zzeraku the Warped"
	mana, attack, health = 8, 4, 12
	numTargets, Effects, description = 0, "", "Whenever your hero takes damage, summon a 6/6 Nether Drake"
	name_CN = "扭曲巨龙泽拉库"
	index = "Legendary"
	trigBoard = Trig_ZzerakutheWarped		
	
	
class NetherDrake(Minion):
	Class, race, name = "Warlock", "Dragon", "Nether Drake"
	mana, attack, health = 6, 6, 6
	name_CN = "虚空幼龙"
	numTargets, Effects, description = 0, "", ""
	index = "Uncollectible"
	
	
class SkyRaider(Minion):
	Class, race, name = "Warrior", "Pirate", "Sky Raider"
	mana, attack, health = 1, 1, 2
	numTargets, Effects, description = 0, "", "Battlecry: Add a random Pirate to your hand"
	name_CN = "空中悍匪"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.Game.addCardtoHand(numpyChoice(self.rngPool("Pirates")), self.ID, byType=True)
		
	
class RitualChopper(Weapon):
	Class, name, description = "Warrior", "Ritual Chopper", "Battlecry: Invoke Galakrond"
	mana, attack, durability, Effects = 2, 1, 2, ""
	name_CN = "仪式斩斧"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		Galakrond.getsInvoked(self)
		
	
class Awaken(Spell):
	Class, school, name = "Warrior", "", "Awaken!"
	numTargets, mana, Effects = 0, 3, ""
	description = "Invoke Galakrond. Deal 1 damage to all minions"
	name_CN = "祈求觉醒"
	def text(self): return self.calcDamage(1)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		Galakrond.getsInvoked(self)
		self.dealsDamage(objs := self.Game.minionsonBoard(), [self.calcDamage(1)] * len(objs))
		
	
class Ancharrr(Weapon):
	Class, name, description = "Warrior", "Ancharrr", "After your hero attacks, draw a Pirate from your deck"
	mana, attack, durability, Effects = 3, 2, 2, ""
	name_CN = "海盗之锚"
	index = "Legendary"
	trigBoard = Trig_Ancharrr		
	
	
class EVILQuartermaster(Minion):
	Class, race, name = "Warrior", "", "EVIL Quartermaster"
	mana, attack, health = 3, 2, 3
	numTargets, Effects, description = 0, "", "Battlecry: Add a Lackey to your hand. Gain 3 Armor"
	name_CN = "怪盗军需官"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.addCardtoHand(numpyChoice(EVILCableRat.lackeys), self.ID)
		self.giveHeroAttackArmor(self.ID, armor=3)
		
	
class RammingSpeed(Spell):
	Class, school, name = "Warrior", "", "Ramming Speed"
	numTargets, mana, Effects = 1, 3, ""
	description = "Force a minion to attack one of its neighbors"
	name_CN = "横冲直撞"
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.aliveonBoard()
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for obj in target:
			if obj.canBattle() and (neighbors := [o for o in self.Game.neighbors2(obj)[0] if o.health > 0 and not o.dead]):
				self.Game.battle(obj, numpyChoice(neighbors))
		
	
class ScionofRuin(Minion):
	Class, race, name = "Warrior", "Dragon", "Scion of Ruin"
	mana, attack, health = 4, 3, 2
	numTargets, Effects, description = 0, "Rush", "Rush. Battlecry: If you've Invoked twice, summon two copies of this"
	name_CN = "废墟之子"
	index = "Battlecry"
	def effCanTrig(self):
		self.effectViable = Galakrond.invokeTimes(self) > 1
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if not self.dead and Galakrond.invokeTimes(self) > 1:
			self.summon([self.copyCard(self, self.ID) for _ in (0, 1)], relative="<>")
		
	
class Skybarge(Minion):
	Class, race, name = "Warrior", "Mech", "Skybarge"
	mana, attack, health = 3, 2, 5
	numTargets, Effects, description = 0, "", "After you summon a Pirate, deal 2 damage to a random enemy"
	name_CN = "空中炮艇"
	trigBoard = Trig_Skybarge		
	
	
class MoltenBreath(Spell):
	Class, school, name = "Warrior", "Fire", "Molten Breath"
	numTargets, mana, Effects = 1, 4, ""
	description = "Deal 5 damage to a minion. If you're holding Dragon, gain 5 Armor"
	name_CN = "熔火吐息"
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID)
		
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def text(self): return self.calcDamage(5)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(target, self.calcDamage(5))
		if self.Game.Hand_Deck.holdingDragon(self.ID): self.giveHeroAttackArmor(self.ID, armor=5)
		
	
class GalakrondsMight(Power):
	mana, name, numTargets = 2, "Galakrond's Might", 0
	description = "Give your hero +3 Attack this turn"
	name_CN = "迦拉克隆之力"
	def effect(self, target=(), choice=0, comment=''):
		self.giveHeroAttackArmor(self.ID, attGain=3, source=GalakrondsMight)
		
	
class GalakrondAzerothsEnd_Warrior(Galakrond):
	Class, heroPower = "Warrior", GalakrondsMight
	name, description = "Galakrond, Azeroth's End", "Battlecry: Draw 4 minions. Give them +4/+4. Equip a 5/2 Claw"
	name_CN = "世界末日迦拉克隆"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for _ in (0, 1, 2, 3):
			minion, mana, entersHand = self.drawCertainCard(lambda card: card.category == "Minion")
			if not minion: break
			elif entersHand:
				self.giveEnchant(minion, 4, 4, source=GalakrondtheUnbreakable, add2EventinGUI=False)
		self.equipWeapon(DragonClaw(self.Game, self.ID))
		
	
class GalakrondtheApocalypes_Warrior(GalakrondAzerothsEnd_Warrior):
	name, description = "Galakrond, the Apocalypes", "Battlecry: Draw 2 minions. Give them +4/+4. (Invoke twice to upgrade)"
	name_CN = "天降浩劫迦拉克隆"
	upgrade = GalakrondAzerothsEnd_Warrior
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for _ in (0, 1):
			minion, mana, entersHand = self.drawCertainCard(lambda card: card.category == "Minion")
			if not minion: break
			elif entersHand:
				self.giveEnchant(minion, 4, 4, source=GalakrondtheUnbreakable, add2EventinGUI=False)
		
	
class GalakrondtheUnbreakable(GalakrondAzerothsEnd_Warrior):
	name, description = "Galakrond, the Unbreakable", "Battlecry: Draw 1 minion. Give it +4/+4. (Invoke twice to upgrade)"
	name_CN = "无敌巨龙迦拉克隆"
	index = "Battlecry~Legendary"
	upgrade = GalakrondtheApocalypes_Warrior
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		minion, mana, entersHand = self.drawCertainCard(lambda card: card.category == "Minion")
		if entersHand: self.giveEnchant(minion, 4, 4, source=GalakrondtheUnbreakable, add2EventinGUI=False)
		
	
class DeathwingMadAspect(Minion):
	Class, race, name = "Warrior", "Dragon", "Deathwing, Mad Aspect"
	mana, attack, health = 8, 12, 12
	numTargets, Effects, description = 0, "", "Battlecry: Attack ALL other minions"
	name_CN = "疯狂巨龙死亡之翼"
	index = "Battlecry~Legendary"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		#这个战吼的攻击会消耗随从的攻击次数。在战吼结束后给其加上冲锋或者突袭时，其不能攻击
		#战吼的攻击可以正常触发奥秘和攻击目标指向扳机
		#攻击过程中死亡之翼濒死会停止攻击，但是如果中途被冰冻是不会停止攻击的。即用战斗不检查攻击的合法性。
		#战吼结束之后才会进行战斗的死亡结算，期间被攻击的随从可以降到负血量还留在场上。
		game = self.Game
		minions = game.minionsAlive(exclude=game.cardinPlay)
		numpyShuffle(minions)
		while minions:
			minion = minions.pop()
			if minion.onBoard and minion.health > 0 and not minion.dead:
				game.battle(game.cardinPlay, minion, useAttChance=True, resetRedirTrig=False)
		game.sendSignal("BattleFinished", game.turn, self)
		
	


AllClasses_Dragons = [
	Aura_SkyClaw, GameRuleAura_LivingDragonbreath, GameRuleAura_DwarvenSharpshooter, Death_TastyFlyfish, Death_BadLuckAlbatross,
	Death_ChromaticEgg, Death_LeperGnome_Dragons, Death_VioletSpellwing, Death_DragonriderTalritha, Death_MindflayerKaahrj,
	Death_GraveRune, Death_Chronobreaker, Death_Waxadred, Trig_DepthCharge, Trig_HotAirBalloon, Trig_ParachuteBrigand,
	Trig_Transmogrifier, Trig_DreadRaven, Trig_WingCommander, Trig_Shuma, Trig_SecuretheDeck, Trig_StrengthinNumbers,
	Trig_Aeroponics, Trig_CleartheWay, Trig_ToxicReinforcement, Trig_PhaseStalker, Trig_Stormhammer, Trig_Dragonbane,
	Trig_ElementalAllies, Trig_LearnDraconic, Trig_Chenvaala, Trig_ManaGiant, Trig_RighteousCause, Trig_Sanctuary,
	Trig_CandleBreath, Trig_SurgingTempest, Trig_Bandersmosh_PreShifting, Trig_Bandersmosh_KeepShifting, Trig_StormEgg,
	Trig_ZzerakutheWarped, Trig_Ancharrr, Trig_Skybarge, SwapHeroPowersBack, GameManaAura_BlowtorchSaboteur, GameAura_GorutheMightree,
	GameManaAura_Dragoncaster, Galakrond, BlazingBattlemage, DepthCharge, HotAirBalloon, EvasiveChimaera, DragonBreeder,
	GrizzledWizard, ParachuteBrigand, TastyFlyfish, Transmogrifier, WyrmrestPurifier, BlowtorchSaboteur, DreadRaven,
	FireHawk, GoboglideTech, LivingDragonbreath, Scalerider, BadLuckAlbatross, Albatross, DevotedManiac, DragonmawPoacher,
	EvasiveFeywing, FrizzKindleroost, Hippogryph, HoardPillager, TrollBatrider, WingCommander, ZulDrakRitualist, BigOlWhelp,
	ChromaticEgg, CobaltSpellkin, FacelessCorruptor, KoboldStickyfinger, Platebreaker, ShieldofGalakrond, Skyfin,
	TentacledMenace, CamouflagedDirigible, EvasiveWyrm, Gyrocopter, KronxDragonhoof, Annihilation, Decimation, Domination,
	Reanimation, ReanimatedDragon, UtgardeGrapplesniper, EvasiveDrakonid, Shuma, Tentacle_Dragons, TwinTyrant, DragonqueenAlexstrasza,
	Sathrovarr, Embiggen, SecuretheDeck, StrengthinNumbers, SmallRepairs, SpinemUp, SmallRepairs_Option, SpinemUp_Option,
	Treenforcements, BreathofDreams, Shrubadier, Treant_Dragons, Aeroponics, EmeraldExplorer, GorutheMightree, YseraUnleashed,
	DreamPortal, CleartheWay, Gryphon_Dragons, DwarvenSharpshooter, ToxicReinforcements, LeperGnome_Dragons, CorrosiveBreath,
	PhaseStalker, DivingGryphon, PrimordialExplorer, Stormhammer, Dragonbane, Veranus, ArcaneBreath, ElementalAllies,
	LearnDraconic, DraconicEmissary, VioletSpellwing, Chenvaala, SnowElemental, AzureExplorer, MalygossFrostbolt,
	MalygossMissiles, MalygossNova, MalygossPolymorph, MalygossTome, MalygossExplosion, MalygossIntellect, MalygossFireball,
	MalygossFlamestrike, MalygossSheep, MalygosAspectofMagic, RollingFireball, Dragoncaster, ManaGiant, RighteousCause,
	SandBreath, Sanctuary, IndomitableChampion, BronzeExplorer, SkyClaw, Microcopter, DragonriderTalritha, LightforgedZealot,
	NozdormutheTimeless, AmberWatcher, LightforgedCrusader, WhispersofEVIL, DiscipleofGalakrond, EnvoyofLazul, BreathoftheInfinite,
	MindflayerKaahrj, FateWeaver, GraveRune, Chronobreaker, TimeRip, GalakrondsWit, GalakrondAzerothsEnd_Priest, GalakrondtheApocalypes_Priest,
	GalakrondtheUnspeakable, DragonClaw, MurozondtheInfinite, BloodsailFlybooter, SkyPirate, DragonsHoard, PraiseGalakrond,
	SealFate, UmbralSkulker, NecriumApothecary, Stowaway, Waxadred, WaxadredsCandle, CandleBreath, FlikSkyshiv, GalakrondsGuile,
	GalakrondAzerothsEnd_Rogue, GalakrondtheApocalypes_Rogue, GalakrondtheNightmare, InvocationofFrost, SurgingTempest,
	Squallhunter, StormsWrath, LightningBreath, Bandersmosh, CumuloMaximus, DragonsPack, SpiritWolf_Dragons, CorruptElementalist,
	Nithogg, StormEgg, StormDrake, GalakrondsFury, WindsweptElemental, GalakrondAzerothsEnd_Shaman, GalakrondtheApocalypes_Shaman,
	GalakrondtheTempest, BrewingStorm, LivingStorm, RagingStorm, RainofFire, NetherBreath, DarkSkies, DragonblightCultist,
	FiendishRites, VeiledWorshipper, CrazedNetherwing, AbyssalSummoner, AbyssalDestroyer, GalakrondsMalice, DraconicImp,
	GalakrondAzerothsEnd_Warlock, GalakrondtheApocalypes_Warlock, GalakrondtheWretched, ValdrisFelgorge, ZzerakutheWarped,
	NetherDrake, SkyRaider, RitualChopper, Awaken, Ancharrr, EVILQuartermaster, RammingSpeed, ScionofRuin, Skybarge,
	MoltenBreath, GalakrondsMight, GalakrondAzerothsEnd_Warrior, GalakrondtheApocalypes_Warrior, GalakrondtheUnbreakable,
	DeathwingMadAspect, 
]

for class_ in AllClasses_Dragons:
	if issubclass(class_, Card):
		class_.index = "DRAGONS" + ("~" if class_.index else '') + class_.index