from Parts.CardTypes import *
from Parts.TrigsAuras import *
from HS_Cards.AcrossPacks import TheCoin, GoldenKobold, \
						TolinsGoblet, WondrousWand, ZarogsCrown, Bomb, BoomBot
from HS_Cards.Core import PatientAssassin, MurlocScout


class Twinspell(Spell):
	twinspellCopy = None
	def beforeSpellEffective(self):
		if twinspellCopy := type(self).twinspellCopy: self.addCardtoHand(twinspellCopy, self.ID)
		
	
class Aura_WhirlwindTempest(Aura_AlwaysOn):
	effGain, targets = "Mega Windfury", "All"
	def applicable(self, target): return target.effects["Windfury"] > 0
		
	
class ManaAura_KirinTorTricaster(ManaAura):
	by = 1
	def applicable(self, target): target.ID == self.keeper.ID and target.category == "Spell"
		
	
class ManaAura_Kalecgos(ManaAura_1UsageEachTurn):
	def auraAppears(self):
		game, ID = self.keeper.Game, self.keeper.ID
		if game.turn == ID and not any(game.Counters.examCardPlays(ID, turnInd=game.turnInd, cond=lambda tup: tup[0].category == "Spell")):
			self.aura = GameManaAura_Kalecgos(game, ID)
			game.Manas.CardAuras.append(self.aura)
			self.aura.auraAppears()
		add2ListinDict(self, game.trigsBoard[ID], "TurnStarts")
		
	
class Death_HenchClanHogsteed(Deathrattle):
	description = "Deathrattle: Summon a 1/1 Murloc"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).summon(HenchClanSquire(kpr.Game, kpr.ID))
		
	
class Death_RecurringVillain(Deathrattle):
	description = "Deathrattle: If this minion has 4 or more Attack, resummon it"
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return self.keeper.Game.rules[self.keeper.ID]["Deathrattle X"] < 1 and target is self.keeper and target.attack > 3
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).summon(type(kpr)(kpr.Game, kpr.ID))
		
	
class Death_EccentricScribe(Deathrattle):
	description = "Deathrattle: Summon four 1/1 Vengeful Scrolls"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		game, ID = (kpr := self.keeper).Game, kpr.ID
		kpr.summon([VengefulScroll(game, ID) for i in (0, 1, 2, 3)], relative="<>")
		
	
class Death_Safeguard(Deathrattle):
	description = "Deathrattle: Summon a 0/5 Vault Safe with Taunt"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).summon(VaultSafe(kpr.Game, kpr.ID))
		
	
class Death_TunnelBlaster(Deathrattle):
	description = "Deathrattle: Deal 3 damage to all minions"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.dealsDamage(self.keeper.Game.minionsonBoard(), 3)
		
	
class Death_Acornbearer(Deathrattle):
	description = "Deathrattle: Add two 1/1 Squirrels to your hand"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.addCardtoHand([Squirrel_Shadows, Squirrel_Shadows], self.keeper.ID)
		
	
class Death_Lucentbark(Deathrattle):
	description, forceLeave = "Deathrattle: Go dormant. Restore 5 Health to awaken this minion", True
	def effect(self, signal, ID, subject, target, num, comment, choice):
		game, ID = self.keeper.Game, self.keeper.ID
		if self.keeper.category == "Minion" and self.keeper in game.minions[ID]:
			if self.keeper.onBoard:
				self.keeper.goDormant(Trig_SpiritofLucentbark(self.keeper))
			elif game.space(ID) > 0:
				dormant = Lucentbark(game, ID)
				dormant.category = "Dormant"
				dormant.trigsBoard.append(Trig_SpiritofLucentbark(dormant))
				game.summonSingle(dormant)
		
	
class Death_Shimmerfly(Deathrattle):
	description = "Deathrattle: Add a random Hunter spell to your hand"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.addCardtoHand(numpyChoice(self.rngPool("Hunter Spells")), self.keeper.ID)
		
	
class Death_Ursatron(Deathrattle):
	description = "Deathrattle: Draw a Mech from your deck"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.drawCertainCard(lambda card: "Mech" in card.race)
		
	
class Death_Oblivitron(Deathrattle):
	description = "Deathrattle: Summon a Mech from your hand and trigger its Deathrattle"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		if mech := self.keeper.try_SummonfromOwn(hand_deck=0, cond=lambda card: "Mech" in card.race):
			for trig in mech.deathrattles: trig.trig("TrigDeathrattle", mech.ID, None, mech, 0, "", 0)
		
	
class Death_BronzeHerald(Deathrattle):
	description = "Deathrattle: Add Two 4/4 Bronze Dragons to your hand"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.addCardtoHand([BronzeDragon, BronzeDragon], self.keeper.ID)
		
	
class Death_EVILConscripter(Deathrattle):
	description = "Deathrattle: Add A random Lackey to your hand"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.addCardtoHand(numpyChoice(EVILCableRat.lackeys), self.keeper.ID)
		
	
class Death_HenchClanShadequill(Deathrattle):
	description = "Deathrattle: Restore 5 Health to the opponent hero"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).heals(kpr.Game.heroes[3 - kpr.ID], kpr.calcHeal(5))
		
	
class Death_ConvincingInfiltrator(Deathrattle):
	description = "Deathrattle: Destroy a random enemy minion"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		if minions := (kpr := self.keeper).Game.minionsAlive(3-kpr.ID):
			kpr.Game.Game.kill(kpr, numpyChoice(minions))
		
	
class Death_WagglePick(Deathrattle):
	description = "Deathrattle: Return a random friendly minion to your hand. It costs (2) less"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		if minions := (kpr := self.keeper).Game.minionsonBoard(self.keeper.ID):
			kpr.Game.returnObj2Hand(kpr, obj := numpyChoice(minions), manaMod=ManaMod(obj, by=-2))
		
	
class Death_SouloftheMurloc(Deathrattle):
	description = "Deathrattle: Summon a 1/1 Murloc"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).summon(MurlocScout(kpr.Game, kpr.ID))
		
	
class Death_EagerUnderling(Deathrattle):
	description = "Deathrattle: Give Two Random Friendly Minions +2/+2"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		if minions := (kpr := self.keeper).Game.minionsonBoard(kpr.ID):
			kpr.giveEnchant(numpyChoice(minions, min(len(minions), 2), replace=False), 2, 2, source=EagerUnderling)
		
	
class Trig_MagicCarpet(TrigBoard):
	signals = ("CardBeenPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		kpr, cardinPlay = kpr, kpr.Game.cardinPlay
		return cardinPlay.category == "Minion" and ID == kpr.ID and num[0] == 1 and cardinPlay is not kpr and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).giveEnchant(kpr.Game.cardinPlay, 1, 0, effGain="Rush", source=MagicCarpet)
		
	
class Trig_ArchmageVargoth(TrigBoard):
	signals = ("TurnEnds",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		game = (kpr := self.keeper).Game
		if tups := game.Counters.examCardPlays(self.keeper.ID, turnInd=game.turnInd, veri_sum_ls=2,
											   cond=lambda tup: tup[0].category == "Spell"):
			game.fabCard(numpyChoice(tups), kpr.ID, kpr).cast()
		
	
class Trig_ProudDefender(Trig_SelfAura):
	signals = ("MinionAppears", "MinionDisappears")
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and target.ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.calcStat()
		
	
class Trig_SoldierofFortune(TrigBoard):
	signals = ("MinionAttackingMinion", "MinionAttackingHero",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and subject is kpr
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).addCardtoHand(TheCoin, 3-kpr.ID)
		
	
class Trig_AzeriteElemental(TrigBoard):
	signals = ("TurnStarts",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).giveEnchant(kpr, effectEnchant=Enchantment_Exclusive(AzeriteElemental, effGain="Spell Damage", effNum=2))
		
	
class Trig_ExoticMountseller(TrigBoard):
	signals = ("CardPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return comment == "Spell" and ID == kpr.ID and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).summon(numpyChoice(self.rngPool("3-Cost Beasts to Summon"))(kpr.Game, kpr.ID))
		
	
class Trig_UnderbellyOoze(TrigBoard):
	signals = ("MinionTakesDmg",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return target is self.keeper and target.onBoard and target.health > 0 and not target.dead
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).summon(kpr.copyCard(kpr, kpr.ID))
		
	
class Trig_Batterhead(TrigBoard):
	signals = ("MinionAttackedMinion",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and subject is kpr and (target.health < 1 or target.dead) and kpr.aliveonBoard()
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.attChances_extra += 1
		
	
class Trig_BigBadArchmage(TrigBoard):
	signals = ("TurnEnds",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.summon(numpyChoice(self.rngPool("6-Cost self.keepers to Summon"))(self.keeper.Game, self.keeper.ID))
		
	
class Trig_KeeperStalladris(TrigBoard):
	signals = ("CardBeenPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return comment == "Spell" and ID == kpr.ID and kpr.Game.cardinPlay.options and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).addCardtoHand([option.spell for option in type(kpr.Game.cardinPlay).options], kpr.ID)
		
	
class Trig_Lifeweaver(TrigBoard):
	signals = ("MinionGetsHealed", "HeroGetsHealed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).addCardtoHand(numpyChoice(self.rngPool("Druid Spells")), kpr.ID)
		
	
class Trig_SpiritofLucentbark(Trig_Countdown):
	signals, counter = ("MinionGetsHealed", "HeroGetsHealed",), 5
	def increment(self, signal, ID, subject, target, num, comment, choice):
		return num
		
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		if self.counter < 1: self.keeper.awaken()
		
	
class Trig_ArcaneFletcher(TrigBoard):
	signals = ("CardPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return comment == "Minion" and ID == kpr.ID and num[0] == 1 and kpr.Game.cardinPlay is not kpr and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.drawCertainCard(lambda card: card.category == "Spell")
		
	
class Trig_ThoridaltheStarsFury(TrigBoard):
	signals = ("HeroAttackedMinion", "HeroAttackedHero",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return ID == kpr.ID and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		kpr.Game.heroes[kpr.ID].getsEffect("Spell Damage", 2)
		ThoridaltheStarsFury_Effect(kpr.Game, kpr.ID).connect()
		
	
class GameRuleAura_Khadgar(GameRuleAura):
	def auraAppears(self):
		#卡德加在场时，连续从手牌或者牌库中召唤随从时，会一个一个的召唤，然后根据卡德加的效果进行双倍，如果双倍召唤提前填满了随从池，则后面的被招募随从就不再离开牌库或者手牌。，
		#两个卡德加在场时，召唤数量会变成4倍。（卡牌的描述是翻倍）
		#两个卡德加时，打出鱼人猎潮者，召唤一个1/1鱼人。会发现那个1/1鱼人召唤之后会在那个鱼人右侧再召唤一个（第一个卡德加的翻倍），然后第二个卡德加的翻倍触发，在最最左边的鱼人的右边召唤两个鱼人。
		#当场上有卡德加的时候，灰熊守护者的亡语招募两个4费以下随从，第一个随从召唤出来时被翻倍，然后第二召唤出来的随从会出现在第一个随从的右边，然后翻倍，结果是后面出现的一对随从夹在第一对随从之间。
		#对一次性召唤多个随从的机制的猜测应该是每一个新出来的随从都会盯紧之前出现的那个随从，然后召唤在那个随从的右边。如果之前召唤那个随从引起了新的随从召唤，无视之。
		#目前没有在连续召唤随从之间出现随从提前离场的情况。上面提到的始终紧盯是可以实现的。
		self.keeper.Game.rules[self.keeper.ID]["Summon x2"] += 1
		
	def auraDisappears(self): self.keeper.Game.rules[self.keeper.ID]["Summon x2"] -= 1
		
	
class Trig_MagicDartFrog(TrigBoard):
	signals = ("CardBeenPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return comment == "Spell" and ID == kpr.ID and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		if minions := kpr.Game.minionsAlive(3-kpr.ID):
			self.keeper.dealsDamage(numpyChoice(minions), 1)
		
	
class Trig_NeverSurrender(Trig_Secret):
	signals = ("CardPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return comment == "Spell" and kpr.ID != kpr.Game.turn == ID and kpr.Game.minionsonBoard(kpr.ID)
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).giveEnchant(kpr.Game.minionsonBoard(kpr.ID), 0, 2, source=NeverSurrender)
		
	
class GameRuleAura_CommanderRhyssa(GameRuleAura):
	def auraAppears(self): self.keeper.Game.rules[self.keeper.ID]["Secrets x2"] += 1
		
	def auraDisappears(self): self.keeper.Game.rules[self.keeper.ID]["Secrets x2"] -= 1
		
	
class Trig_Upgrade(TrigHand):
	signals = ("TurnEnds",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.inHand and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.progress += 1
		
	
class Trig_CatrinaMuerte(TrigBoard):
	signals = ("TurnEnds",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		if tups := kpr.Game.Counters.examDeads(kpr.ID, veri_sum_ls=2):
			kpr.summon(kpr.Game.fabCard(numpyChoice(tups), kpr.ID, kpr))
		
	
class Trig_Vendetta(TrigHand):
	signals = ("HandCheck",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.inHand and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).Game.Manas.calcMana_Single(kpr)
		
	
class Trig_TakNozwhisker(TrigBoard):
	signals = ("CardShuffled",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		#Only triggers if the player is the initiator
		return kpr.onBoard and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		keeper = self.keeper
		if isinstance(target, (list, tuple)):
			keeper.addCardtoHand([keeper.copyCard(card, keeper.ID) for card in target], keeper.ID)
		else: keeper.addCardtoHand(keeper.copyCard(target, keeper.ID), keeper.ID)
		
	
class Trig_UnderbellyAngler(TrigBoard):
	signals = ("ObjBeenSummoned",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return "Murloc" in subject.race and ID == kpr.ID and subject is not kpr and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).addCardtoHand(numpyChoice(self.rngPool("Murlocs")), kpr.ID)
		
	
class ManaAura_Scargil(ManaAura):
	to = 1
	def applicable(self, target): target.ID == self.keeper.ID and "Murloc" in target.race
		
	
class Trig_JumboImp(TrigHand):
	signals = ("ObjDied",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return "Demon" in target.race and kpr.inHand and target.ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		ManaMod(self.keeper, by=-1).applies()
		
	
class Trig_FelLordBetrug(TrigBoard):
	signals = ("CardDrawn",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and target[0].category == "Minion" and target[0].ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		minion = kpr.copyCard(target[0], kpr.ID)
		minion.trigsBoard.append(Trig_DieatEndofTurn(minion))
		self.keeper.summon(minion)
		if minion.onBoard: self.keeper.giveEnchant(minion, effGain="Rush", source=FelLordBetrug)
		
	
class Trig_ViciousScraphound(TrigBoard):
	signals = ("MinionTakesDmg", "HeroTakesDmg",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return subject is self.keeper
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).giveHeroAttackArmor(kpr.ID, armor=num)
		
	
class Trig_Wrenchcalibur(TrigBoard):
	signals = ("HeroAttackedMinion", "HeroAttackedHero",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		#The target can't be dying to trigger this
		return subject is kpr.Game.heroes[kpr.ID] and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		weapon = self.keeper
		weapon.shuffleintoDeck(Bomb(weapon.Game, 3-weapon.ID), enemyCanSee=True)
		
	
class ThoridaltheStarsFury_Effect(TrigEffect):
	counter, trigType = 2, "TurnEnd&OnlyKeepOne"
	def trigEffect(self):
		self.Game.heroes[self.ID].loeseEffect("Spell Damage", amount=self.counter)
		
	
class GameManaAura_Kalecgos(GameManaAura_OneTime):
	to = 0
	def applicable(self, target): return target.ID == self.ID and target.category == "Spell"
		
	
class PotionVendor(Minion):
	Class, race, name = "Neutral", "", "Potion Vendor"
	mana, attack, health = 1, 1, 1
	name_CN = "药水商人"
	numTargets, Effects, description = 0, "", "Battlecry: Restore 2 Health to all friendly characters"
	index = "Battlecry"
	def text(self): return self.calcHeal(2)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.heals(self.Game.charsonBoard(self.ID), self.calcHeal(2))
		
	
class Toxfin(Minion):
	Class, race, name = "Neutral", "Murloc", "Toxfin"
	mana, attack, health = 1, 1, 2
	name_CN = "毒鳍鱼人"
	numTargets, Effects, description = 1, "", "Battlecry: Give a friendly Murloc Poisonous"
	index = "Battlecry"
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists(self.ID)
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return "Murloc" in obj.race and obj.ID == self.ID and obj is not self and obj.onBoard
		
	def effCanTrig(self):
		self.effectViable = any("Murloc" in minion.race for minion in self.Game.minionsonBoard(self.ID))
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(target, effGain="Poisonous", source=Toxfin)
		
	
class ArcaneServant(Minion):
	Class, race, name = "Neutral", "Elemental", "Arcane Servant"
	mana, attack, health = 2, 2, 3
	numTargets, Effects, description = 0, "", ""
	name_CN = "奥术仆从"
	
	
class DalaranLibrarian(Minion):
	Class, race, name = "Neutral", "", "Dalaran Librarian"
	mana, attack, health = 2, 2, 3
	name_CN = "达拉然图书管理员"
	numTargets, Effects, description = 0, "", "Battlecry: Silences adjacent minions"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.Game.silenceMinions(self.Game.neighbors2(self)[0])
		
	
class EtherealLackey(Minion):
	Class, race, name = "Neutral", "", "Ethereal Lackey"
	mana, attack, health = 1, 1, 1
	index = "DALARAN~Battlecry~Uncollectible"
	numTargets, Effects, description = 0, "", "Battlecry: Discover a spell"
	name_CN = "虚灵跟班"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.discoverNew(comment, lambda : self.rngPool(class4Discover(self) + " Spells"))
		
	
class FacelessLackey(Minion):
	Class, race, name = "Neutral", "", "Faceless Lackey"
	mana, attack, health = 1, 1, 1
	index = "DALARAN~Battlecry~Uncollectible"
	numTargets, Effects, description = 0, "", "Battlecry: Summon a 2-Cost minion"
	name_CN = "无面跟班"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon(self.rngPool("2-Cost Minions to Summon")(self.Game, self.ID))
		
	
class GoblinLackey(Minion):
	Class, race, name = "Neutral", "", "Goblin Lackey"
	mana, attack, health = 1, 1, 1
	index = "DALARAN~Battlecry~Uncollectible"
	numTargets, Effects, description = 1, "", "Battlecry: Give a friendly minion +1 Attack and Rush"
	name_CN = "地精跟班"
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists(self.ID)
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.ID == self.ID and obj is not self and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(target, 1, 0, effGain="Rush", source=GoblinLackey)
		
	
class KoboldLackey(Minion):
	Class, race, name = "Neutral", "", "Kobold Lackey"
	mana, attack, health = 1, 1, 1
	index = "DALARAN~Battlecry~Uncollectible"
	numTargets, Effects, description = 1, "", "Battlecry: Deal 2 damage"
	name_CN = "狗头人跟班"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(target, 2)
		
	
class WitchyLackey(Minion):
	Class, race, name = "Neutral", "", "Witchy Lackey"
	mana, attack, health = 1, 1, 1
	index = "DALARAN~Battlecry~Uncollectible"
	numTargets, Effects, description = 1, "", "Battlecry: Transform a friendly minion into one that costs (1) more"
	name_CN = "女巫跟班"
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists(self.ID)
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.ID == self.ID and obj is not self and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.transform(target, [self.newEvolved(obj.mana_0, by=1, ID=obj.ID) for obj in target])
		
	
class TitanicLackey(Minion):
	Class, race, name = "Neutral", "", "Titanic Lackey"
	mana, attack, health = 1, 1, 1
	index = "ULDUM~Battlecry~Uncollectible"
	numTargets, Effects, description = 1, "", "Battlecry: Give a friendly minion +2 Health"
	name_CN = "泰坦跟班"
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists(self.ID, choice)
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.ID == self.ID and obj is not self and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(target, 0, 2, effGain="Taunt", source=TitanicLackey)
		
	
class DraconicLackey(Minion):
	Class, race, name = "Neutral", "", "Draconic Lackey"
	mana, attack, health = 1, 1, 1
	index = "DRAGONS~Battlecry~Uncollectible"
	numTargets, Effects, description = 0, "", "Battlecry: Discover a Dragon"
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
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.discoverNew(comment, lambda : self.rngPool("Dragons as " + class4Discover(self)))
		
	
class EVILCableRat(Minion):
	Class, race, name = "Neutral", "Beast", "EVIL Cable Rat"
	mana, attack, health = 2, 1, 1
	name_CN = "怪盗布缆鼠"
	numTargets, Effects, description = 0, "", "Battlecry: Add a Lackey to your hand"
	index = "Battlecry"
	lackeys = (DraconicLackey, EtherealLackey, FacelessLackey, GoblinLackey, KoboldLackey, TitanicLackey, WitchyLackey)
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.addCardtoHand(numpyChoice(EVILCableRat.lackeys), self.ID)
		
	
class HenchClanHogsteed(Minion):
	Class, race, name = "Neutral", "Beast", "Hench-Clan Hogsteed"
	mana, attack, health = 2, 2, 1
	numTargets, Effects, description = 0, "Rush", "Rush. Deathrattle: Summon a 1/1 Murloc"
	name_CN = "荆棘帮斗猪"
	deathrattle = Death_HenchClanHogsteed
	
	
class HenchClanSquire(Minion):
	Class, race, name = "Neutral", "Murloc", "Hench-Clan Squire"
	mana, attack, health = 1, 1, 1
	name_CN = "荆棘帮马仔"
	numTargets, Effects, description = 0, "", ""
	index = "Uncollectible"
	
	
class ManaReservoir(Minion):
	Class, race, name = "Neutral", "Elemental", "Mana Reservoir"
	mana, attack, health = 2, 0, 6
	numTargets, Effects, description = 0, "Spell Damage", "Spell Damage +1"
	name_CN = "法力之池"
	
	
class SpellbookBinder(Minion):
	Class, race, name = "Neutral", "", "Spellbook Binder"
	mana, attack, health = 2, 3, 2
	name_CN = "魔法订书匠"
	numTargets, Effects, description = 0, "", "Battlecry: If you have Spell Damage, draw a card"
	index = "Battlecry"
	def effCanTrig(self):
		self.effectViable = self.countSpellDamage() > 0
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.countSpellDamage() > 0: self.Game.Hand_Deck.drawCard(self.ID)
		
	
class SunreaverSpy(Minion):
	Class, race, name = "Neutral", "", "Sunreaver Spy"
	mana, attack, health = 2, 2, 3
	name_CN = "夺日者间谍"
	numTargets, Effects, description = 0, "", "Battlecry: If you control a Secret, gain +1/+1"
	index = "Battlecry"
	def effCanTrig(self):
		self.effectViable = self.Game.Secrets.secrets[self.ID]
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.Game.Secrets.secrets[self.ID]: self.giveEnchant(self, 1, 1, source=SunreaverSpy)
		
	
class ZayleShadowCloak(Minion):
	Class, race, name = "Neutral", "", "Zayle, Shadow Cloak"
	mana, attack, health = 2, 3, 2
	name_CN = "泽尔， 暗影斗篷"
	numTargets, Effects, description = 0, "", "You start the game with one of Zayle's EVIL Decks!"
	index = "Legendary"
	
	
class ArcaneWatcher(Minion):
	Class, race, name = "Neutral", "", "Arcane Watcher"
	mana, attack, health = 3, 5, 6
	numTargets, Effects, description = 0, "Can't Attack", "Can't attack unless you have Spell Damage"
	name_CN = "奥术守望者"
	def attackAllowedbyEffect(self):
		return self.effects["Can't Attack"] < 1 or \
			   (self.effects["Can't Attack"] == 1 and not self.silenced and self.countSpellDamage() > 0)
		
	
class FacelessRager(Minion):
	Class, race, name = "Neutral", "", "Faceless Rager"
	mana, attack, health = 3, 5, 1
	name_CN = "无面暴怒者"
	numTargets, Effects, description = 1, "", "Battlecry: Copy a friendly minion's Health"
	index = "Battlecry"
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists(self.ID)
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.ID == self.ID and obj is not self and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for obj in target: self.setStat(self, (None, obj.health), source=FacelessRager)
		
	
class FlightMaster(Minion):
	Class, race, name = "Neutral", "", "Flight Master"
	mana, attack, health = 3, 3, 4
	name_CN = "飞行管理员"
	numTargets, Effects, description = 0, "", "Battlecry: Summon a 2/2 Gryphon for each player"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon(Gryphon(self.Game, self.ID))
		self.summon(Gryphon(self.Game, 3-self.ID))
		
	
class Gryphon(Minion):
	Class, race, name = "Neutral", "Beast", "Gryphon"
	mana, attack, health = 2, 2, 2
	name_CN = "狮鹫"
	numTargets, Effects, description = 0, "", ""
	index = "Uncollectible"
	
	
class HenchClanSneak(Minion):
	Class, race, name = "Neutral", "", "Hench-Clan Sneak"
	mana, attack, health = 3, 3, 3
	numTargets, Effects, description = 0, "Stealth", "Stealth"
	name_CN = "荆棘帮小偷"
	
	
class MagicCarpet(Minion):
	Class, race, name = "Neutral", "", "Magic Carpet"
	mana, attack, health = 3, 1, 6
	numTargets, Effects, description = 0, "", "After you play a 1-Cost minion, give it +1 Attack and Rush"
	name_CN = "魔法飞毯"
	trigBoard = Trig_MagicCarpet		
	
	
class SpellwardJeweler(Minion):
	Class, race, name = "Neutral", "", "Spellward Jeweler"
	mana, attack, health = 3, 3, 4
	name_CN = "破咒珠宝师"
	numTargets, Effects, description = 0, "", "Battlecry: Your hero can't be targeted by spells or Hero Powers until your next turn"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.Game.rules[self.ID]["Evasive"] += 1
		self.Game.rules[self.ID]["Evasive2NextTurn"] += 1
		
	
class ArchmageVargoth(Minion):
	Class, race, name = "Neutral", "", "Archmage Vargoth"
	mana, attack, health = 4, 2, 6
	name_CN = "大法师瓦格斯"
	numTargets, Effects, description = 0, "", "At the end of your turn, cast a spell you've cast this turn (targets chosen randomly)"
	index = "Legendary"
	trigBoard = Trig_ArchmageVargoth		
	
	
class Hecklebot(Minion):
	Class, race, name = "Neutral", "Mech", "Hecklebot"
	mana, attack, health = 4, 3, 8
	name_CN = "机械拷问者"
	numTargets, Effects, description = 0, "Taunt", "Taunt. Battlecry: Your opponent summons a minion from their deck"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.Game.space(3-self.ID) and \
			(indices := [i for i, card in enumerate(self.Game.Hand_Deck.decks[3-self.ID]) if card.category == "Minion"]):
			self.Game.summonfrom(numpyChoice(indices), 3-self.ID, -1, summoner=self, hand_deck=1)
		
	
class HenchClanHag(Minion):
	Class, race, name = "Neutral", "", "Hench-Clan Hag"
	mana, attack, health = 4, 3, 3
	name_CN = "荆棘帮巫婆"
	numTargets, Effects, description = 0, "", "Battlecry: Summon two 1/1 Amalgams with all minions types"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon([Amalgam(self.Game, self.ID) for _ in (0, 1)], relative="<>")
		
	
class Amalgam(Minion):
	Class, race, name = "Neutral", "Elemental,Mech,Demon,Murloc,Dragon,Beast,Pirate,Totem", "Amalgam"
	mana, attack, health = 1, 1, 1
	name_CN = "融合怪"
	numTargets, Effects, description = 0, "", "This is an Elemental, Mech, Demon, Murloc, Dragon, Beast, Pirate and Totem"
	index = "Uncollectible"
	
	
class PortalKeeper(Minion):
	Class, race, name = "Neutral", "Demon", "Portal Keeper"
	mana, attack, health = 4, 5, 2
	name_CN = "传送门守护者"
	numTargets, Effects, description = 0, "", "Battlecry: Shuffle 3 Portals into your deck. When drawn, summon a 2/2 Demon with Rush"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		portals = [FelhoundPortal(self.Game, self.ID) for _ in (0, 1, 2)]
		self.shuffleintoDeck(portals, enemyCanSee=True)
		
	
class FelhoundPortal(Spell):
	Class, school, name = "Neutral", "", "Felhound Portal"
	numTargets, mana, Effects = 0, 2, ""
	name_CN = "地狱犬传送门"
	description = "Casts When Drawn. Summon a 2/2 Felhound with Rush"
	index = "Uncollectible"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon(Felhound(self.Game, self.ID))
		
	
class Felhound(Minion):
	Class, race, name = "Neutral", "Demon", "Felhound"
	mana, attack, health = 2, 2, 2
	name_CN = "地狱犬"
	numTargets, Effects, description = 0, "Rush", "Rush"
	index = "Uncollectible"
	
	
class ProudDefender(Minion):
	Class, race, name = "Neutral", "", "Proud Defender"
	mana, attack, health = 4, 2, 6
	numTargets, Effects, description = 0, "Taunt", "Taunt. Has +2 Attack while you have no other minions"
	name_CN = "骄傲的防御者"
	trigBoard = Trig_ProudDefender
	def statCheckResponse(self):
		if self.onBoard and not self.silenced and not self.Game.minionsonBoard(self.ID, exclude=self):
			self.attack += 2
		
	
class SoldierofFortune(Minion):
	Class, race, name = "Neutral", "Elemental", "Soldier of Fortune"
	mana, attack, health = 4, 5, 6
	numTargets, Effects, description = 0, "", "Whenever this minion attacks, give your opponent a coin"
	name_CN = "散财军士"
	trigBoard = Trig_SoldierofFortune		
	
	
class TravelingHealer(Minion):
	Class, race, name = "Neutral", "", "Traveling Healer"
	mana, attack, health = 4, 3, 2
	name_CN = "旅行医者"
	numTargets, Effects, description = 1, "Divine Shield", "Divine Shield. Battlecry: Restore 3 Health."
	index = "Battlecry"
	def text(self): return self.calcHeal(3)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.heals(target, self.calcHeal(3))
		
	
class VioletSpellsword(Minion):
	Class, race, name = "Neutral", "", "Violet Spellsword"
	mana, attack, health = 4, 1, 6
	name_CN = "紫罗兰 魔剑士"
	numTargets, Effects, description = 0, "", "Battlecry: Gain +1 Attack for each spell in your hand"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if num := sum(card.category == "Spell" for card in self.Game.Hand_Deck.hands[self.ID]):
			self.giveEnchant(self, num, 0, source=VioletSpellsword)
		
	
class AzeriteElemental(Minion):
	Class, race, name = "Neutral", "Elemental", "Azerite Elemental"
	mana, attack, health = 5, 2, 7
	numTargets, Effects, description = 0, "", "At the start of your turn, gain Spell Damage +2"
	name_CN = "艾泽里特元素"
	trigBoard = Trig_AzeriteElemental		
	
	
class BaristaLynchen(Minion):
	Class, race, name = "Neutral", "", "Barista Lynchen"
	mana, attack, health = 5, 4, 5
	name_CN = "咖啡师林彻"
	numTargets, Effects, description = 0, "", "Battlecry: Add a copy of each of your other Battlecry minions to your hand"
	index = "Battlecry~Legendary"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		battlecryMinions = [minion for minion in self.Game.minions[self.ID] if "~Battlecry" in minion.index and minion is not self]
		for minion in battlecryMinions:
			self.addCardtoHand(type(minion), self.ID)
		
	
class DalaranCrusader(Minion):
	Class, race, name = "Neutral", "", "Dalaran Crusader"
	mana, attack, health = 5, 5, 4
	numTargets, Effects, description = 0, "Divine Shield", "Divine Shield"
	name_CN = "达拉然圣剑士"
	
	
class RecurringVillain(Minion):
	Class, race, name = "Neutral", "", "Recurring Villain"
	mana, attack, health = 5, 3, 6
	numTargets, Effects, description = 0, "", "Deathrattle: If this minion has 4 or more Attack, resummon it"
	name_CN = "再生大盗"
	deathrattle = Death_RecurringVillain
	
	
class SunreaverWarmage(Minion):
	Class, race, name = "Neutral", "", "Sunreaver Warmage"
	mana, attack, health = 5, 4, 4
	name_CN = "夺日者战斗法师"
	numTargets, Effects, description = 1, "", "Battlecry: If you're holding a spell costs (5) or more, deal 4 damage"
	index = "Battlecry"
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.holdingBigSpell(self.ID)
		
	def numTargetsNeeded(self, choice=0):
		return 1 if self.Game.Hand_Deck.holdingBigSpell(self.ID) else 0
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.Game.Hand_Deck.holdingBigSpell(self.ID): self.dealsDamage(target, 4)
		
	
class EccentricScribe(Minion):
	Class, race, name = "Neutral", "", "Eccentric Scribe"
	mana, attack, health = 6, 6, 4
	numTargets, Effects, description = 0, "", "Deathrattle: Summon four 1/1 Vengeful Scrolls"
	name_CN = "古怪的铭文师"
	deathrattle = Death_EccentricScribe
	
	
class VengefulScroll(Minion):
	Class, race, name = "Neutral", "", "Vengeful Scroll"
	mana, attack, health = 1, 1, 1
	name_CN = "复仇卷轴"
	numTargets, Effects, description = 0, "", ""
	index = "Uncollectible"
	
	
class MadSummoner(Minion):
	Class, race, name = "Neutral", "Demon", "Mad Summoner"
	mana, attack, health = 6, 4, 4
	name_CN = "疯狂召唤师"
	numTargets, Effects, description = 0, "", "Battlecry: Fill each player's board with 1/1 Imps"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		game, ID = self.Game, self.ID
		while (ownSpace := game.space(ID)) + (oppoSpace := game.space(3-ID)) > 0:
			if ownSpace: self.summon(Imp_Shadows(game, ID))
			if oppoSpace: self.summon(Imp_Shadows(game, 3-ID))
		
	
class Imp_Shadows(Minion):
	Class, race, name = "Neutral", "Demon", "Imp"
	mana, attack, health = 1, 1, 1
	name_CN = "小鬼"
	numTargets, Effects, description = 0, "", ""
	index = "Uncollectible"
	
	
class PortalOverfiend(Minion):
	Class, race, name = "Neutral", "Demon", "Portal Overfiend"
	mana, attack, health = 6, 5, 6
	name_CN = "传送门大恶魔"
	numTargets, Effects, description = 0, "", "Battlecry: Shuffle 3 Portals into your deck. When drawn, summon a 2/2 Demon with Rush"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		portals = [FelhoundPortal(self.Game, self.ID) for _ in (0, 1, 2)]
		self.shuffleintoDeck(portals, enemyCanSee=True)
		
	
class Safeguard(Minion):
	Class, race, name = "Neutral", "Mech", "Safeguard"
	mana, attack, health = 6, 4, 5
	numTargets, Effects, description = 0, "Taunt", "Taunt. Deathrattle: Summon a 0/5 Vault Safe with Taunt"
	name_CN = "机械保险箱"
	deathrattle = Death_Safeguard
	
	
class VaultSafe(Minion):
	Class, race, name = "Neutral", "Mech", "Vault Safe"
	mana, attack, health = 2, 0, 5
	name_CN = "保险柜"
	numTargets, Effects, description = 0, "Taunt", "Taunt"
	index = "Uncollectible"
	
	
class UnseenSaboteur(Minion):
	Class, race, name = "Neutral", "", "Unseen Saboteur"
	mana, attack, health = 6, 5, 6
	name_CN = "隐秘破坏者"
	numTargets, Effects, description = 0, "", "Battlecry: Your opponent casts a random spell from their hand (targets chosen randomly)"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if indices := [i for i, card in enumerate(self.Game.Hand_Deck.hands[3-self.ID]) if card.category == "Spell"]:
			self.Game.Hand_Deck.extractfromHand(numpyChoice(indices), 3 - self.ID)[0].cast()
		
	
class VioletWarden(Minion):
	Class, race, name = "Neutral", "", "Violet Warden"
	mana, attack, health = 6, 4, 7
	numTargets, Effects, description = 0, "Taunt,Spell Damage", "Taunt, Spell Damage +1"
	name_CN = "紫罗兰典狱官"
	
	
class ChefNomi(Minion):
	Class, race, name = "Neutral", "", "Chef Nomi"
	mana, attack, health = 7, 6, 6
	name_CN = "大厨诺米"
	numTargets, Effects, description = 0, "", "Battlecry: If your deck is empty, summon six 6/6 Greasefire Elementals"
	index = "Battlecry~Legendary"
	def effCanTrig(self):
		self.effectViable = not self.Game.Hand_Deck.decks[self.ID]
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if not self.Game.Hand_Deck.decks[self.ID]:
			self.summon([GreasefireElemental(self.Game, self.ID) for i in range(7)], relative="<>")
		
	
class GreasefireElemental(Minion):
	Class, race, name = "Neutral", "Elemental", "Greasefire Elemental"
	mana, attack, health = 6, 6, 6
	name_CN = "猛火元素"
	numTargets, Effects, description = 0, "", ""
	index = "Uncollectible"
	
	
class ExoticMountseller(Minion):
	Class, race, name = "Neutral", "", "Exotic Mountseller"
	mana, attack, health = 7, 5, 8
	numTargets, Effects, description = 0, "", "Whenever you cast a spell, summon a random 3-Cost Beast"
	name_CN = "特殊坐骑商人"
	trigBoard = Trig_ExoticMountseller
	poolIdentifier = "3-Cost Beasts to Summon"
	@classmethod
	def generatePool(cls, pools):
		return "3-Cost Beasts to Summon", [card for card in pools.MinionswithRace["Beast"] if card.mana == 3]
		
	
class TunnelBlaster(Minion):
	Class, race, name = "Neutral", "", "Tunnel Blaster"
	mana, attack, health = 7, 3, 7
	numTargets, Effects, description = 0, "Taunt", "Taunt. Deathrattle: Deal 3 damage to all minions"
	name_CN = "坑道爆破手"
	deathrattle = Death_TunnelBlaster
	
	
class UnderbellyOoze(Minion):
	Class, race, name = "Neutral", "", "Underbelly Ooze"
	mana, attack, health = 7, 3, 5
	numTargets, Effects, description = 0, "", "After this minion survives damage, summon a copy of it"
	name_CN = "下水道软泥怪"
	trigBoard = Trig_UnderbellyOoze		
	
	
class Batterhead(Minion):
	Class, race, name = "Neutral", "", "Batterhead"
	mana, attack, health = 8, 3, 12
	numTargets, Effects, description = 0, "Rush", "Rush. After this attacks and kills a minion, it may attack again"
	name_CN = "莽头食人魔"
	trigBoard = Trig_Batterhead		
	
	
class HeroicInnkeeper(Minion):
	Class, race, name = "Neutral", "", "Heroic Innkeeper"
	mana, attack, health = 8, 4, 4
	name_CN = "霸气的旅店老板娘"
	numTargets, Effects, description = 0, "Taunt", "Taunt. Battlecry: Gain +2/+2 for each other friendly minion"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.onBoard or self.inHand:
			if buff := 2 * len(self.Game.minionsonBoard(self.ID, exclude=self)): self.giveEnchant(self, buff, buff, source=HeroicInnkeeper)
		
	
class JepettoJoybuzz(Minion):
	Class, race, name = "Neutral", "", "Jepetto Joybuzz"
	mana, attack, health = 8, 6, 6
	name_CN = "耶比托·乔巴斯"
	numTargets, Effects, description = 0, "", "Battlecry: Draw 2 minions from your deck. Set their Attack, Health, and Cost to 1"
	index = "Battlecry~Legendary"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for _ in (0, 1):
			minion, mana, entersHand = self.drawCertainCard(cond=lambda card: card.category == "Minion")
			if not minion: break
			elif entersHand:
				self.setStat(minion, (1, 1), source=JepettoJoybuzz)
				ManaMod(minion, to=1).applies()
		
	
class WhirlwindTempest(Minion):
	Class, race, name = "Neutral", "Elemental", "Whirlwind Tempest"
	mana, attack, health = 8, 6, 6
	numTargets, Effects, description = 0, "", "Your Windfury minions have Mega Windfury"
	name_CN = "暴走旋风"
	aura = Aura_WhirlwindTempest
	
	
class BurlyShovelfist(Minion):
	Class, race, name = "Neutral", "", "Burly Shovelfist"
	mana, attack, health = 9, 9, 9
	numTargets, Effects, description = 0, "Rush", "Rush"
	name_CN = "推土壮汉"
	
	
class ArchivistElysiana(Minion):
	Class, race, name = "Neutral", "", "Archivist Elysiana"
	mana, attack, health = 9, 7, 7
	name_CN = "档案员艾丽西娜"
	numTargets, Effects, description = 0, "", "Battlecry: Discover 5 cards. Replace your deck with 2 copies of each"
	index = "Battlecry~Legendary"
	poolIdentifier = "Cards as Druid"
	@classmethod
	def generatePool(cls, pools):
		return genPool_CardsasClass(pools)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.Game.Hand_Deck.extractfromDeck(ID=self.ID, getAll=True)
		deck = self.Game.Hand_Deck.decks[self.ID]
		for _ in (0, 1, 2, 3, 4):
			card, _ = self.discoverNew(comment, lambda : self.rngPool("Cards as "+class4Discover(self)), add2Hand=False)
			deck.append(card.entersDeck())
			deck.append(type(card)(self.Game, self.ID).entersDeck())
		numpyShuffle(deck) #Need to shuffle the discovered cards
		
	
class BigBadArchmage(Minion):
	Class, race, name = "Neutral", "", "Big Bad Archmage"
	mana, attack, health = 10, 6, 6
	numTargets, Effects, description = 0, "", "At the end of your turn, summon a random 6-Cost minion"
	name_CN = "恶狼大法师"
	trigBoard = Trig_BigBadArchmage		
	
	
class Acornbearer(Minion):
	Class, race, name = "Druid", "", "Acornbearer"
	mana, attack, health = 1, 2, 1
	numTargets, Effects, description = 0, "", "Deathrattle: Add two 1/1 Squirrels to your hand"
	name_CN = "橡果人"
	deathrattle = Death_Acornbearer
	
	
class Squirrel_Shadows(Minion):
	Class, race, name = "Druid", "Beast", "Squirrel"
	mana, attack, health = 1, 1, 1
	name_CN = "松鼠"
	numTargets, Effects, description = 0, "", ""
	index = "Uncollectible"
	
	
class PiercingThorns(Spell):
	Class, school, name = "Druid", "Nature", "Piercing Thorns"
	numTargets, mana, Effects = 1, 1, ""
	name_CN = "利刺荆棘"
	description = "Deal 2 damage to a minion"
	index = "Uncollectible"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def text(self): return self.calcDamage(2)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(target, self.calcDamage(2))
		
	
class HealingBlossom(Spell):
	Class, school, name = "Druid", "Nature", "Healing Blossom"
	numTargets, mana, Effects = 1, 1, ""
	name_CN = "愈合之花"
	description = "Restore 5 Health"
	index = "Uncollectible"
	def text(self): return self.calcHeal(5)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.heals(target, self.calcHeal(5))
		
	
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
		return self.keeper.selectableCharExists(1)
		
	
class CrystalPower(Spell):
	Class, school, name = "Druid", "Nature", "Crystal Power"
	numTargets, mana, Effects = 1, 1, ""
	name_CN = "水晶之力"
	description = "Choose One - Deal 2 damage to a minion; or Restore 5 Health"
	options = (PiercingThorns_Option, HealingBlossom_Option)
	def available(self):
		return self.selectableCharExists(1)
		
	def targetCorrect(self, obj, choice=0, ith=0):
		#available() only needs to check selectableCharExists
		return obj.onBoard and (obj.category == "Minion" or (choice and obj.category == "Hero"))
		
	def text(self): return "%d, %d"%(self.calcDamage(2), self.calcHeal(5))
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		damage, heal = self.calcDamage(2), self.calcHeal(5)
		for obj in target:
			if choice < 0: #如果目标是一个随从，先对其造成伤害，如果目标存活，才能造成治疗
				if obj.category == "Minion": #只会对随从造成伤害
					self.dealsDamage(obj, damage)
				if obj.health > 0 and not obj.dead: #法术造成伤害之后，那个随从必须活着才能接受治疗，不然就打2无论如何都变得没有意义
					self.heals(obj, heal)
			elif not choice:
				if obj.category == "Minion": self.dealsDamage(obj, damage)
			else: self.heals(obj, heal)
		
	
class CrystalsongPortal(Spell):
	Class, school, name = "Druid", "Nature", "Crystalsong Portal"
	numTargets, mana, Effects = 0, 2, ""
	description = "Discover a Druid minion. If your hand has no minions, keep all 3"
	name_CN = "晶歌传送门"
	def effCanTrig(self):
		return all(card.category != "Minion" for card in self.Game.Hand_Deck.hands[self.ID])
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if all(card.category != "Minion" for card in self.Game.Hand_Deck.hands[self.ID]):
			self.addCardtoHand(numpyChoice(self.rngPool("Druid Minions"), 3, replace=False), self.ID)
		else: self.discoverNew(comment, lambda : self.rngPool("Druid Minions"))
		
	
class DreamwayGuardians(Spell):
	Class, school, name = "Druid", "", "Dreamway Guardians"
	numTargets, mana, Effects = 0, 2, ""
	description = "Summon two 1/2 Dryads with Lifesteal"
	name_CN = "守卫梦境之路"
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon([CrystalDryad(self.Game, self.ID) for _ in (0, 1)])
		
	
class CrystalDryad(Minion):
	Class, race, name = "Druid", "", "Crystal Dryad"
	mana, attack, health = 1, 1, 2
	name_CN = "水晶树妖"
	numTargets, Effects, description = 0, "Lifesteal", "Lifesteal"
	index = "Uncollectible"
	
	
class KeeperStalladris(Minion):
	Class, race, name = "Druid", "", "Keeper Stalladris"
	mana, attack, health = 2, 2, 3
	name_CN = "守护者斯塔拉蒂斯"
	numTargets, Effects, description = 0, "", "After you cast a Choose One spell, add copies of both choices to your hand"
	index = "Legendary"
	trigBoard = Trig_KeeperStalladris		
	
	
class Lifeweaver(Minion):
	Class, race, name = "Druid", "", "Lifeweaver"
	mana, attack, health = 3, 2, 5
	numTargets, Effects, description = 0, "", "Whenever you restore Health, add a random Druid spell to your hand"
	name_CN = "织命者"
	trigBoard = Trig_Lifeweaver
	
	
class CrystalStag(Minion):
	Class, race, name = "Druid", "Beast", "Crystal Stag"
	mana, attack, health = 5, 4, 4
	name_CN = "晶角雄鹿"
	numTargets, Effects, description = 0, "Rush", "Rush. Battlecry: If you've restored 5 Health this game, summon a copy of this"
	index = "Battlecry"
	def effCanTrig(self):
		self.effectViable = 5 <= sum(tup[2] for tup in self.Game.Counters.iter_TupsSoFar("events") if tup[0] == "Heal" and tup[1] == self.ID)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if not self.dead and 5 <= sum(tup[2] for tup in self.Game.Counters.iter_TupsSoFar("events") if tup[0] == "Heal" and tup[1] == self.ID):
			self.summon(self.copyCard(self, self.ID))
		
	
class BlessingoftheAncients2(Twinspell):
	Class, school, name = "Druid", "Nature", "Blessing of the Ancients"
	numTargets, mana, Effects = 0, 3, ""
	name_CN = "远古祝福"
	description = "Give your minions +1/+1"
	index = "Uncollectible"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(self.Game.minionsonBoard(self.ID), 1, 1, source=BlessingoftheAncients)
		
	
class BlessingoftheAncients(BlessingoftheAncients2):
	description = "Twinspell. Give your minions +1/+1"
	twinspellCopy = BlessingoftheAncients2
	
	
class Lucentbark(Minion):
	Class, race, name = "Druid", "", "Lucentbark"
	mana, attack, health = 8, 4, 8
	name_CN = "卢森巴克"
	numTargets, Effects, description = 0, "Taunt", "Taunt. Deathrattle: Go dormant. Restore 5 Health to awaken this minion"
	index = "Legendary"
	deathrattle = Death_Lucentbark
	
	
class TheForestsAid2(Twinspell):
	Class, school, name = "Druid", "Nature", "The Forest's Aid"
	numTargets, mana, Effects = 0, 8, ""
	name_CN = "森林的援助"
	description = "Summon five 2/2 Treants"
	index = "Uncollectible"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon([Treant_Shadows(self.Game, self.ID) for i in range(5)])
		
	
class TheForestsAid(TheForestsAid2):
	description = "Twinspell. Summon five 2/2 Treants"
	twinspellCopy = TheForestsAid2
	
	
class Treant_Shadows(Minion):
	Class, race, name = "Druid", "", "Treant"
	mana, attack, health = 2, 2, 2
	name_CN = "树人"
	numTargets, Effects, description = 0, "", ""
	index = "Uncollectible"
	
	
class RapidFire2(Twinspell):
	Class, school, name = "Hunter", "", "Rapid Fire"
	numTargets, mana, Effects = 1, 1, ""
	name_CN = "急速射击"
	description = "Deal 1 damage"
	index = "Uncollectible"
	def text(self): return self.calcDamage(1)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(target, self.calcDamage(1))
		
	
class RapidFire(RapidFire2):
	description = "Twinspell. Deal 1 damage"
	twinspellCopy = RapidFire2
	
	
class Shimmerfly(Minion):
	Class, race, name = "Hunter", "Beast", "Shimmerfly"
	mana, attack, health = 1, 1, 1
	numTargets, Effects, description = 0, "", "Deathrattle: Add a random Hunter spell to your hand"
	name_CN = "闪光蝴蝶"
	deathrattle = Death_Shimmerfly
	
	
class NineLives(Spell):
	Class, school, name = "Hunter", "", "Nine Lives"
	numTargets, mana, Effects = 0, 3, ""
	description = "Discover a friendly Deathrattle minion that died this game. Also trigger its Deathrattle"
	name_CN = "九命兽魂"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		func = lambda: self.Game.Counters.examDeads(self.ID, veri_sum_ls=2, cond=lambda card: card.deathrattle)
		card, _ = self.discoverfrom(comment, tupsFunc=func)
		if card:
			self.addCardtoHand(card, self.ID, byDiscover=True)
			for trig in card.deathrattles: trig.trig("TrigDeathrattle", self.ID, None, card)
		
	
class Ursatron(Minion):
	Class, race, name = "Hunter", "Mech", "Ursatron"
	mana, attack, health = 3, 3, 3
	numTargets, Effects, description = 0, "", "Deathrattle: Draw a Mech from your deck"
	name_CN = "机械巨熊"
	deathrattle = Death_Ursatron
	
	
class ArcaneFletcher(Minion):
	Class, race, name = "Hunter", "", "Arcane Fletcher"
	mana, attack, health = 4, 3, 3
	numTargets, Effects, description = 0, "", "Whenever you play a 1-Cost minion, draw a spell from your deck"
	name_CN = "奥术弓箭手"
	trigBoard = Trig_ArcaneFletcher		
	
	
class MarkedShot(Spell):
	Class, school, name = "Hunter", "", "Marked Shot"
	numTargets, mana, Effects = 1, 4, ""
	description = "Deal 4 damage to a minion. Discover a Spell"
	name_CN = "标记射击"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def text(self): return self.calcDamage(4)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(target, self.calcDamage(4))
		self.discoverNew(comment, lambda: self.rngPool("Hunter Spells"))
		
	
class HuntingParty(Spell):
	Class, school, name = "Hunter", "", "Hunting Party"
	numTargets, mana, Effects = 0, 5, ""
	description = "Copy all Beasts in your hand"
	name_CN = "狩猎盛宴"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if copies := [self.copyCard(card, self) for card in self.Game.Hand_Deck.hands[self.ID] if "Beast" in card.race]:
			self.addCardtoHand(copies, self.ID)
		
	
class Oblivitron(Minion):
	Class, race, name = "Hunter", "Mech", "Oblivitron"
	mana, attack, health = 6, 3, 4
	name_CN = "湮灭战车"
	numTargets, Effects, description = 0, "", "Deathrattle: Summon a Mech from your hand and trigger its Deathrattle"
	index = "Legendary"
	deathrattle = Death_Oblivitron
	
	
class UnleashtheBeast2(Twinspell):
	Class, school, name = "Hunter", "", "Unleash the Beast"
	numTargets, mana, Effects = 0, 6, ""
	name_CN = "猛兽出笼"
	description = "Summon a 5/5 Wyvern with Rush"
	index = "Uncollectible"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon(Wyvern(self.Game, self.ID))
		
	
class UnleashtheBeast(UnleashtheBeast2):
	description = "Twinspell. Summon a 5/5 Wyvern with Rush"
	twinspellCopy = UnleashtheBeast2
	
	
class Wyvern(Minion):
	Class, race, name = "Hunter", "Beast", "Wyvern"
	mana, attack, health = 5, 5, 5
	name_CN = "双足飞龙"
	numTargets, Effects, description = 0, "Rush", "Rush"
	index = "Uncollectible"
	
	
class VereesaWindrunner(Minion):
	Class, race, name = "Hunter", "", "Vereesa Windrunner"
	mana, attack, health = 7, 5, 6
	name_CN = "温蕾萨·风行者"
	numTargets, Effects, description = 0, "", "Battlecry: Equip Thori'dal, the Stars' Fury"
	index = "Battlecry~Legendary"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.equipWeapon(ThoridaltheStarsFury(self.Game, self.ID))
		
	
class ThoridaltheStarsFury(Weapon):
	Class, name, description = "Hunter", "Thori'dal, the Stars' Fury", "After your hero attacks, gain Spell Damage +2 this turn"
	mana, attack, durability, Effects = 3, 2, 3, ""
	name_CN = "索利达尔，群星之怒"
	index = "Legendary~Uncollectible"
	trigBoard, trigEffect = Trig_ThoridaltheStarsFury, ThoridaltheStarsFury_Effect
	
	
class RayofFrost2(Twinspell):
	Class, school, name = "Mage", "Frost", "Ray of Frost"
	numTargets, mana, Effects = 1, 1, ""
	name_CN = "霜冻射线"
	description = "Freeze a minion. If it's already Frozen, deal 2 damage to it"
	index = "Uncollectible"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def text(self): return self.calcDamage(2)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		damage = self.calcDamage(2)
		for obj in target:
			if obj.effects["Frozen"]: self.dealsDamage(target, damage)
			else: self.freeze(obj)
		
	
class RayofFrost(RayofFrost2):
	description = "Twinspell. Freeze a minion. If it's already Frozen, deal 2 damage to it"
	twinSpellCopy = RayofFrost2
	
	
class Khadgar(Minion):
	Class, race, name = "Mage", "", "Khadgar"
	mana, attack, health = 2, 2, 2
	name_CN = "卡德加"
	numTargets, Effects, description = 0, "", "Your cards that summon minions summon twice as many"
	index = "Legendary"
	aura = GameRuleAura_Khadgar
	
	
class MagicDartFrog(Minion):
	Class, race, name = "Mage", "Beast", "Magic Dart Frog"
	mana, attack, health = 2, 1, 3
	numTargets, Effects, description = 0, "", "After you cast a spell, deal 1 damage to a random enemy minion"
	name_CN = "魔法蓝蛙"
	trigBoard = Trig_MagicDartFrog		
	
	
class MessengerRaven(Minion):
	Class, race, name = "Mage", "Beast", "Messenger Raven"
	mana, attack, health = 3, 3, 2
	name_CN = "渡鸦信使"
	numTargets, Effects, description = 0, "", "Battlecry: Discover a Mage minion"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.discoverNew(comment, lambda: self.rngPool("Mage Minions"))
		
	
class MagicTrick(Spell):
	Class, school, name = "Mage", "Arcane", "Magic Trick"
	numTargets, mana, Effects = 0, 1, ""
	description = "Discover a spell that costs (3) or less"
	name_CN = "魔术戏法"
	poolIdentifier = "Mage Spells Cost <=3"
	@classmethod
	def generatePool(cls, pools):
		return [Class+" Spells Cost <=3" for Class in pools.Classes], \
				[[card for card in pools.ClassSpells[Class] if card.mana < 4] for Class in pools.Classes]
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.discoverNew(comment, lambda: self.rngPool(class4Discover(self)+" Spells Cost <=3"))
		
	
class ConjurersCalling2(Twinspell):
	Class, school, name = "Mage", "Arcane", "Conjurer's Calling"
	numTargets, mana, Effects = 1, 4, ""
	name_CN = "咒术师的召唤"
	description = "Destroy a minion. Summon 2 minions of the same Cost to replace it"
	index = "Uncollectible"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for obj in target:
			game, ID = self.Game, obj.ID
			key = "%d-Cost Minions to Summon"%obj.mana
			minions = numpyChoice(self.rngPool(key), 2, replace=True) if key in game.RNGPools else []
			self.killandSummon(obj, [minion(game, ID) for minion in minions])
		
	
class ConjurersCalling(ConjurersCalling2):
	description = "Twinspell. Destroy a minion. Summon 2 minions of the same Cost to replace it"
	twinSpellCopy = ConjurersCalling2
	
	
class KirinTorTricaster(Minion):
	Class, race, name = "Mage", "", "Kirin Tor Tricaster"
	mana, attack, health = 4, 3, 3
	numTargets, Effects, description = 0, "Spell Damage_3", "Spell Damage +3. Your spells cost (1) more"
	name_CN = "肯瑞托三修法师"
	aura = ManaAura_KirinTorTricaster
	
	
class ManaCyclone(Minion):
	Class, race, name = "Mage", "Elemental", "Mana Cyclone"
	mana, attack, health = 2, 2, 2
	name_CN = "法力飓风"
	numTargets, Effects, description = 0, "", "Battlecry: For each spell you've cast this turn, add a random Mage spell to your hand"
	index = "Battlecry"
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.examCardPlays(self.ID, turnInd=self.Game.turnInd, cond=lambda tup: tup[0].category == "Spell")
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		num = self.Game.Counters.examCardPlays(self.ID, turnInd=self.Game.turnInd, veri_sum_ls=1, cond=lambda tup: tup[0].category == "Spell")
		if spells := tuple(numpyChoice(self.rngPool("Mage Spells"), min(self.Game.Hand_Deck.spaceinHand(self.ID), num), replace=True)):
			self.addCardtoHand(spells, self.ID)
		
	
class PowerofCreation(Spell):
	Class, school, name = "Mage", "Arcane", "Power of Creation"
	numTargets, mana, Effects = 0, 8, ""
	description = "Discover a 6-Cost minion. Summon two copies of it"
	name_CN = "创世之力"
	poolIdentifier = "6-Cost Minions as Mage to Summon"
	@classmethod
	def generatePool(cls, pools):
		return genPool_CertainMinionsasClass(pools, "6-Cost", cond=lambda card: card.mana == 6)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		card, _ = self.discoverNew(comment, lambda: self.rngPool("6-Cost Minions as %s to Summon"%class4Discover(self)), add2Hand=False)
		if card: self.summon([card, type(card)(self.Game, self.ID)])
		
	
class Kalecgos(Minion):
	Class, race, name = "Mage", "Dragon", "Kalecgos"
	mana, attack, health = 10, 4, 12
	name_CN = "卡雷苟斯"
	numTargets, Effects, description = 0, "", "Your first spell costs (0) each turn. Battlecry: Discover a spell"
	index = "Legendary"
	aura, trigEffect = ManaAura_Kalecgos, GameManaAura_Kalecgos
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.discoverNew(comment, lambda: self.rngPool(class4Discover(self) + " Spells"))
		
	
class NeverSurrender(Secret):
	Class, school, name = "Paladin", "", "Never Surrender!"
	numTargets, mana, Effects = 0, 1, ""
	description = "Secret: Whenever your opponent casts a spell, give your minions +2 Health"
	name_CN = "永不屈服"
	trigBoard = Trig_NeverSurrender		
	
	
class LightforgedBlessing2(Twinspell):
	Class, school, name = "Paladin", "", "Lightforged Blessing"
	numTargets, mana, Effects = 1, 2, ""
	name_CN = "光铸祝福"
	description = "Give a friendly minion Lifesteal"
	index = "Uncollectible"
	def available(self):
		return self.selectableMinionExists(self.ID)
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.ID == self.ID and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(target, effGain="Lifesteal", source=LightforgedBlessing)
		
	
class LightforgedBlessing(LightforgedBlessing2):
	description = "Twinspell. Give a friendly minion Lifesteal"
	twinSpellCopy = LightforgedBlessing2
	
	
class BronzeHerald(Minion):
	Class, race, name = "Paladin", "Dragon", "Bronze Herald"
	mana, attack, health = 3, 3, 2
	numTargets, Effects, description = 0, "", "Deathrattle: Add two 4/4 Dragons to your hand"
	name_CN = "青铜传令官"
	deathrattle = Death_BronzeHerald
	
	
class BronzeDragon(Minion):
	Class, race, name = "Paladin", "Dragon", "Bronze Dragon"
	mana, attack, health = 4, 4, 4
	name_CN = "青铜龙"
	numTargets, Effects, description = 0, "", ""
	index = "Uncollectible"
	
	
class DesperateMeasures2(Twinspell):
	Class, school, name = "Paladin", "", "Desperate Measures"
	numTargets, mana, Effects = 0, 1, ""
	name_CN = "孤注一掷"
	description = "Cast a random Paladin Secrets"
	index = "Uncollectible"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		func = self.Game.Secrets.sameSecretExists
		secrets = [value for value in self.rngPool("Paladin Secrets") if not func(value, self.ID)]
		if secrets: numpyChoice(secrets)(self.Game, self.ID).cast()
		
	
class DesperateMeasures(DesperateMeasures2):
	description = "Twinspell. Cast a random Paladin Secrets"
	twinspellCopy = DesperateMeasures2
	
	
class MysteriousBlade(Weapon):
	Class, name, description = "Paladin", "Mysterious Blade", "Battlecry: If you control a Secret, gain +1 Attack"
	mana, attack, durability, Effects = 2, 2, 2, ""
	name_CN = "神秘之刃"
	index = "Battlecry"
	def effCanTrig(self):
		self.effectViable = self.Game.Secrets.secrets[self.ID]
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.Game.Secrets.secrets[self.ID]: self.giveEnchant(self, 1, 0, source=MysteriousBlade)
		
	
class CalltoAdventure(Spell):
	Class, school, name = "Paladin", "", "Call to Adventure"
	numTargets, mana, Effects = 0, 3, ""
	description = "Draw the lowest Cost minion from your deck. Give it +2/+2"
	name_CN = "冒险号角"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if indices := pickInds_LowestAttr(self.Game.Hand_Deck.decks[self.ID],
										  cond=lambda card: card.category == "Minion"):
			minion, mana, entersHand = self.Game.Hand_Deck.drawCard(self.ID, numpyChoice(indices))
			if entersHand: self.giveEnchant(minion, 2, 2, source=CalltoAdventure)
		
	
class DragonSpeaker(Minion):
	Class, race, name = "Paladin", "", "Dragon Speaker"
	mana, attack, health = 5, 3, 5
	name_CN = "龙语者"
	numTargets, Effects, description = 0, "", "Battlecry: Give all Dragons in your hand +3/+3"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant([card for card in self.Game.Hand_Deck.hands[self.ID] if "Dragon" in card.race],
						 3, 3, source=DragonSpeaker, add2EventinGUI=False)
		
	
class Duel(Spell):
	Class, school, name = "Paladin", "", "Duel!"
	numTargets, mana, Effects = 0, 5, ""
	description = "Summon a minion from each player's deck. They fight"
	name_CN = "决斗"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		enemy, enemyDeck = None, self.Game.Hand_Deck.decks[3-self.ID]
		friendly = self.try_SummonfromOwn()
		if self.Game.space(3-self.ID) and (indices := [i for i, card in enumerate(enemyDeck) if card.category == "Minion"]):
			enemy = self.Game.summonfrom(numpyChoice(indices), 3-self.ID, -1, summoner=self, hand_deck=1)
		#如果我方随从有不能攻击的限制，如Ancient Watcher之类，不能攻击。
		if friendly.effects["Can't Attack"] < 1 and friendly.canBattle() and enemy.canBattle():
			self.Game.battle(friendly, enemy)
		
	
class CommanderRhyssa(Minion):
	Class, race, name = "Paladin", "", "Commander Rhyssa"
	mana, attack, health = 3, 4, 3
	name_CN = "指挥官蕾撒"
	numTargets, Effects, description = 0, "", "Your Secrets trigger twice"
	index = "Legendary"
	aura = GameRuleAura_CommanderRhyssa
	
	
class Nozari(Minion):
	Class, race, name = "Paladin", "Dragon", "Nozari"
	mana, attack, health = 10, 4, 12
	name_CN = "诺萨莉"
	numTargets, Effects, description = 0, "", "Battlecry: Restore both heroes to full Health"
	index = "Battlecry~Legendary"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		heal1, heal2 = self.calcHeal(self.Game.heroes[1].health_max), self.calcHeal(self.Game.heroes[2].health_max)
		self.heals([self.Game.heroes[1], self.Game.heroes[2]], [heal1, heal2])
		
	
class EVILConscripter(Minion):
	Class, race, name = "Priest", "", "EVIL Conscripter"
	mana, attack, health = 2, 2, 2
	numTargets, Effects, description = 0, "", "Deathrattle: Add a Lackey to your hand"
	name_CN = "怪盗征募员"
	deathrattle = Death_EVILConscripter
	
	
class HenchClanShadequill(Minion):
	Class, race, name = "Priest", "", "Hench-Clan Shadequill"
	mana, attack, health = 4, 4, 7
	numTargets, Effects, description = 0, "", "Deathrattle: Restore 5 Health to the enemy hero"
	name_CN = "荆棘帮箭猪"
	deathrattle = Death_HenchClanShadequill
	
	
class UnsleepingSoul(Spell):
	Class, school, name = "Priest", "Shadow", "Unsleeping Soul"
	numTargets, mana, Effects = 1, 4, ""
	description = "Silence a friendly minion, then summon a copy of it"
	name_CN = "不眠之魂"
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists(self.ID)
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.ID == self.ID and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for obj in target:
			obj.getsSilenced()
			self.summon(self.copyCard(obj, self.ID), position=obj.pos+1)
		
	
class ForbiddenWords(Spell):
	Class, school, name = "Priest", "Shadow", "Forbidden Words"
	numTargets, mana, Effects = 1, 0, ""
	description = "Spend all your Mana. Destroy a minion with that much Attack or less"
	name_CN = "禁忌咒文"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.attack <= self.Game.Manas.manas[self.ID] and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.Game.Manas.manas[self.ID] = 0
		self.Game.kill(self, target)
		
	
class ConvincingInfiltrator(Minion):
	Class, race, name = "Priest", "", "Convincing Infiltrator"
	mana, attack, health = 5, 2, 6
	numTargets, Effects, description = 0, "Taunt", "Taunt. Deathrattle: Destroy a random enemy minion"
	name_CN = "无面渗透者"
	deathrattle = Death_ConvincingInfiltrator
	
	
class MassResurrection(Spell):
	Class, school, name = "Priest", "Holy", "Mass Resurrection"
	numTargets, mana, Effects = 0, 9, ""
	description = "Summon 3 friendly minions that died this game"
	name_CN = "群体复活"
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if tups := self.Game.Counters.examDeads(self.ID, veri_sum_ls=2):
			tups = numpyChoice(tups, min(3, len(tups)), replace=False)
			self.summon([self.Game.fabCard(tup, self.ID, self) for tup in tups])
		
	
class LazulsScheme(Spell):
	Class, school, name = "Priest", "Shadow", "Lazul's Scheme"
	numTargets, mana, Effects = 1, 0, ""
	name_CN = "拉祖尔的阴谋"
	trigHand = Trig_Upgrade
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(target, statEnchant=Enchantment(LazulsScheme, -self.progress, 0, until=self.ID))
		
	
class ShadowyFigure(Minion):
	Class, race, name = "Priest", "", "Shadowy Figure"
	mana, attack, health = 2, 2, 2
	name_CN = "阴暗的人影"
	numTargets, Effects, description = 1, "", "Battlecry: Transform into a 2/2 copy of a friendly Deathrattle minion"
	index = "Battlecry"
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists(self.ID)
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj is not self and obj.ID == self.ID and obj.deathrattles and obj.onBoard
		
	def effCanTrig(self):
		self.effectViable = self.targetExists()
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		#如果self.Game.cardinPlay不再等于自己，说明这个随从的已经触发了变形而不会再继续变形。战吼触发时自己不能死亡。
		if self.Game.cardinPlay is self and not self.dead and (self.onBoard or self.inHand):
			self.transform(self, self.copyCard(target[0], self.ID, 2, 2))
		
	
class MadameLazul(Minion):
	Class, race, name = "Priest", "", "Madame Lazul"
	mana, attack, health = 3, 3, 2
	name_CN = "拉祖尔女士"
	numTargets, Effects, description = 0, "", "Battlecry: Discover a copy of a card in your opponent's hand"
	index = "Battlecry~Legendary"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		card, _ = self.discoverfrom(comment, ls=self.Game.Hand_Deck.hands[3-self.ID])
		if card: self.addCardtoHand(self.copyCard(card, self.ID), self.ID, byDiscover=True)
		
	
class CatrinaMuerte(Minion):
	Class, race, name = "Priest", "", "Catrina Muerte"
	mana, attack, health = 8, 6, 8
	name_CN = "亡者卡特林娜"
	numTargets, Effects, description = 0, "", "At the end of your turn, summon a friendly minion that died this game"
	index = "Legendary"
	trigBoard = Trig_CatrinaMuerte		
	
	
class DaringEscape(Spell):
	Class, school, name = "Rogue", "", "Daring Escape"
	numTargets, mana, Effects = 0, 1, ""
	description = "Return all friendly minions to your hand"
	name_CN = "战略转移"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for minion in self.Game.minionsonBoard(self.ID):
			self.Game.returnObj2Hand(self, minion)
		
	
class EVILMiscreant(Minion):
	Class, race, name = "Rogue", "", "EVIL Miscreant"
	mana, attack, health = 3, 1, 4
	name_CN = "怪盗恶霸"
	numTargets, Effects, description = 0, "", "Combo: Add two 1/1 Lackeys to your hand"
	index = "Combo"
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.comboCounters[self.ID] > 0
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if self.Game.Counters.comboCounters[self.ID] > 0:
			self.addCardtoHand(numpyChoice(EVILCableRat.lackeys, 2, replace=True), self.ID)
		
	
class HenchClanBurglar(Minion):
	Class, race, name = "Rogue", "Pirate", "Hench-Clan Burglar"
	mana, attack, health = 4, 4, 3
	name_CN = "荆棘帮蟊贼"
	numTargets, Effects, description = 0, "", "Battlecry: Discover a spell from another class"
	index = "Battlecry"
	def decideSpellPool(self):
		heroClass = self.Game.heroes[self.ID].Class
		classes = [Class for Class in self.rngPool("Classes") if Class != heroClass]
		return self.rngPool("%s Spells"%datetime.now().microsecond % len(classes))
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.discoverNew(comment, lambda : HenchClanBurglar.decideSpellPool(self))
		
	
class TogwagglesScheme(Spell):
	Class, school, name = "Rogue", "", "Togwaggle's Scheme"
	numTargets, mana, Effects = 1, 1, ""
	name_CN = "托瓦格尔的阴谋"
	trigHand = Trig_Upgrade
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.ID == self.ID and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for obj in target:
			self.shuffleintoDeck([self.copyCard(obj, self.ID) for _ in range(self.progress)], enemyCanSee=True)
		
	
class UnderbellyFence(Minion):
	Class, race, name = "Rogue", "", "Underbelly Fence"
	mana, attack, health = 2, 2, 3
	name_CN = "下水道销赃人"
	numTargets, Effects, description = 0, "", "Battlecry: If you're holding a card from another class, gain +1/+1 and Rush"
	index = "Battlecry"
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.holdingCardfromAnotherClass(self.ID, exclude=self)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.Game.Hand_Deck.holdingCardfromAnotherClass(self.ID):
			self.giveEnchant(self, 1, 1, effGain="Rush", source=UnderbellyFence)
		
	
class Vendetta(Spell):
	Class, school, name = "Rogue", "", "Vendetta"
	numTargets, mana, Effects = 1, 4, ""
	description = "Deal 4 damage to a minion. Costs (0) if you're holding a card from another class"
	name_CN = "宿敌"
	trigHand = Trig_Vendetta
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def selfManaChange(self):
		if self.Game.Hand_Deck.holdingCardfromAnotherClass(self.ID):
			self.mana = 0
		
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.holdingCardfromAnotherClass(self.ID)
		
	def text(self): return self.calcDamage(4)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(target, self.calcDamage(4))
		
	
class WagglePick(Weapon):
	Class, name, description = "Rogue", "Waggle Pick", "Deathrattle: Return a random friendly minion to your hand. It costs (2) less"
	mana, attack, durability, Effects = 4, 4, 2, ""
	name_CN = "摇摆矿锄"
	deathrattle = Death_WagglePick
	
	
class UnidentifiedContract(Spell):
	Class, school, name = "Rogue", "", "Unidentified Contract"
	numTargets, mana, Effects = 1, 6, ""
	description = "Destroy a minion. Gain a bonus effect in your hand"
	name_CN = "未鉴定的合约"
	def entersHand(self, isGameEvent=True):
		#本牌进入手牌的结果是本卡消失，变成其他的牌
		self.onBoard = self.inHand = self.inDeck = False
		card = numpyChoice((AssassinsContract, LucrativeContract, RecruitmentContract, TurncoatContract))(self.Game, self.ID)
		card.inHand = True
		card.onBoard = card.inDeck = False
		card.enterHandTurn = card.Game.turnInd
		card.creator = self.creator
		return card
		
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.Game.kill(self, target)
		
	
class AssassinsContract(Spell):
	Class, school, name = "Rogue", "", "Assassin's Contract"
	numTargets, mana, Effects = 1, 6, ""
	name_CN = "刺客合约"
	description = "Destroy a minion. Summon a 1/2 Patient Assassin"
	index = "Uncollectible"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.Game.kill(self, target)
		self.summon(PatientAssassin(self.Game, self.ID))
		
	
class LucrativeContract(Spell):
	Class, school, name = "Rogue", "", "Lucrative Contract"
	numTargets, mana, Effects = 1, 6, ""
	name_CN = "赏金合约"
	description = "Destroy a minion. Add two Coins to your hand"
	index = "Uncollectible"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.Game.kill(self, target)
		self.addCardtoHand((TheCoin, TheCoin), self.ID)
		
	
class RecruitmentContract(Spell):
	Class, school, name = "Rogue", "", "Recruitment Contract"
	numTargets, mana, Effects = 1, 6, ""
	name_CN = "招募合约"
	description = "Destroy a minion. Add a copy of it to your hand"
	index = "Uncollectible"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.Game.kill(self, target)
		self.addCardtoHand([self.copyCard(obj, self.ID, bareCopy=True) for obj in target], self.ID)
		
	
class TurncoatContract(Spell):
	Class, school, name = "Rogue", "", "Turncoat Contract"
	numTargets, mana, Effects = 1, 6, ""
	name_CN = "叛变合约"
	description = "Destroy a minion. It deals damage to adjacent minions"
	index = "Uncollectible"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for obj in target:
			self.Game.kill(self, obj)
			obj.dealsDamage(self.Game.neighbors2(obj)[0], obj.attack)
		
	
class HeistbaronTogwaggle(Minion):
	Class, race, name = "Rogue", "", "Heistbaron Togwaggle"
	mana, attack, health = 6, 5, 5
	name_CN = "劫匪之王托瓦格尔"
	numTargets, Effects, description = 0, "", "Battlecry: If you control a Lackey, choose a fantastic treasure"
	index = "Battlecry"
	def effCanTrig(self):
		self.effectViable = any([minion.name.endswith("Lackey") for minion in self.Game.minionsonBoard(self.ID)])
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if any([minion.name.endswith("Lackey") for minion in self.Game.minionsonBoard(self.ID)]):
			options = [card(self.Game, self.ID) for card in (GoldenKobold, TolinsGoblet, WondrousWand, ZarogsCrown)]
			option = self.chooseFixedOptions(comment, options=options)
			self.addCardtoHand(option, self.ID)
		
	
class TakNozwhisker(Minion):
	Class, race, name = "Rogue", "", "Tak Nozwhisker"
	mana, attack, health = 7, 6, 6
	numTargets, Effects, description = 0, "", "Whenever you shuffle a card into your deck, add a copy to your hand"
	name_CN = "塔克·诺兹维克"
	trigBoard = Trig_TakNozwhisker		
	
	
class Mutate(Spell):
	Class, school, name = "Shaman", "", "Mutate"
	numTargets, mana, Effects = 1, 0, ""
	description = "Transform a friendly minion into a random one that costs (1) more"
	name_CN = "突变"
	def available(self):
		return self.selectableMinionExists(self.ID)
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.ID == self.ID and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.transform(target, [self.newEvolved(obj.mana_0, by=1, ID=obj.ID) for obj in target])
		
	
class SludgeSlurper(Minion):
	Class, race, name = "Shaman", "Murloc", "Sludge Slurper"
	mana, attack, health = 1, 2, 1
	name_CN = "淤泥吞食者"
	numTargets, Effects, description = 0, "", "Battlecry: Add a Lackey to your hand. Overload: (1)"
	index = "Battlecry"
	overload = 1
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.addCardtoHand(numpyChoice(EVILCableRat.lackeys), self.ID)
		
	
class SouloftheMurloc(Spell):
	Class, school, name = "Shaman", "", "Soul of the Murloc"
	numTargets, mana, Effects = 0, 2, ""
	description = "Give your minions 'Deathrattle: Summon a 1/1 Murloc'"
	name_CN = "鱼人之魂"
	trigEffect = Death_SouloftheMurloc
	def available(self):
		return self.Game.minionsonBoard(self.ID)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(self.Game.minionsonBoard(self.ID), trig=Death_SouloftheMurloc, trigType="Deathrattle")
		
	
class UnderbellyAngler(Minion):
	Class, race, name = "Shaman", "Murloc", "Underbelly Angler"
	mana, attack, health = 2, 2, 3
	numTargets, Effects, description = 0, "", "After you play a Murloc, add a random Murloc to your hand"
	name_CN = "下水道渔人"
	trigBoard = Trig_UnderbellyAngler
	
	
class HagathasScheme(Spell):
	Class, school, name = "Shaman", "Nature", "Hagatha's Scheme"
	numTargets, mana, Effects = 0, 5, ""
	description = "Deal 1 damage to all minions. (Upgrades each turn)!"
	name_CN = "哈加莎的阴谋"
	trigHand = Trig_Upgrade
	def text(self): return self.calcDamage(self.progress)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(self.Game.minionsonBoard(), self.calcDamage(self.progress))
		
	
class WalkingFountain(Minion):
	Class, race, name = "Shaman", "Elemental", "Walking Fountain"
	mana, attack, health = 8, 4, 8
	numTargets, Effects, description = 0, "Rush,Windfury,Lifesteal", "Rush, Windfury, Lifesteal"
	name_CN = "活动喷泉"
	
	
class WitchsBrew(Spell):
	Class, school, name = "Shaman", "Nature", "Witch's Brew"
	numTargets, mana, Effects = 1, 2, ""
	description = "Restore 4 Health. Repeatable this turn"
	name_CN = "女巫杂酿"
	def text(self): return self.calcHeal(4)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.heals(target, self.calcHeal(4))
		echo = WitchsBrew(self.Game, self.ID)
		echo.trigsHand.append(Trig_Echo(echo))
		self.addCardtoHand(echo, self.ID)
		
	
class Muckmorpher(Minion):
	Class, race, name = "Shaman", "", "Muckmorpher"
	mana, attack, health = 5, 4, 4
	name_CN = "泥泽变形怪"
	numTargets, Effects, description = 0, "", "Battlecry: Transform in to a 4/4 copy of a different minion in your deck"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		#目前只有打随从从手牌打出或者被沙德沃克调用可以触发随从的战吼。这些手段都要涉及self.Game.CardPlayed
		#如果self.Game.CardPlayed不再等于自己，说明这个随从的已经触发了变形而不会再继续变形。
		if not self.dead and (self.onBoard or self.inHand) and self.Game.cardinPlay is self: #战吼触发时自己不能死亡。
			cardID = self.cardID
			if minions := [card for card in self.Game.Hand_Deck.decks[self.ID] if card.category == "Minion" and card.cardID != cardID]:
				self.transform(self, self.copyCard(numpyChoice(minions), self.ID, 4, 4))
		
	
class Scargil(Minion):
	Class, race, name = "Shaman", "Murloc", "Scargil"
	mana, attack, health = 4, 4, 4
	name_CN = "斯卡基尔"
	numTargets, Effects, description = 0, "", "Your Murlocs cost (1)"
	index = "Legendary"
	aura = ManaAura_Scargil
	
	
class SwampqueenHagatha(Minion):
	Class, race, name = "Shaman", "", "Swampqueen Hagatha"
	mana, attack, health = 7, 5, 5
	name_CN = "沼泽女王哈加莎"
	numTargets, Effects, description = 0, "", "Battlecry: Add a 5/5 Horror to your hand. Teach it two Shaman spells"
	index = "Battlecry~Legendary"
	poolIdentifier = "Non-targeting Shaman Spells"
	@classmethod
	def generatePool(cls, pools):
		return "Non-targeting Shaman Spells", \
				[card for card in pools.ClassCards["Shaman"] if card.category == "Spell" and not card.numTargets]
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		spell1, _ = self.discoverNew(comment, lambda : self.rngPool("Shaman Spells"), add2Hand=False)
		spell1 = type(spell1)
		if spell1.numTargets:
			spell2, _ = self.discoverNew(comment, lambda: self.rngPool("Non-targeting Shaman Spells"), add2Hand=False)
		else: spell2, _ = self.discoverNew(comment, lambda: [card for card in self.rngPool("Shaman Spells") if card is not spell1], add2Hand=False)
		#Create Horror
		name1, name2 = spell1.__name__, (spell2 := type(spell2)).__name__
		horror = type("DrustvarHorror__%s_%s"%(name1, name1), (DrustvarHorror,),
						{"numTargets": spell1.numTargets or spell2.numTargets,
						 "info1": spell1, "info2": spell2,
						}
					)
		self.addCardtoHand(horror, self.ID)
		
	
class DrustvarHorror(Minion):
	Class, race, name = "Shaman", "", "Drustvar Horror"
	mana, attack, health = 5, 5, 5
	name_CN = "德鲁斯瓦恐魔"
	numTargets, Effects, description = 0, "", "Battlecry: Cast (0) and (1)"
	index = "Battlecry~Uncollectible"
	def text(self): return "%s\n%s"%(type(self).info1.name_CN, type(self).info2.name_CN)
		
	def targetExists(self, choice=0, ith=0):
		# 有指向的法术的available才会真正决定可指向目标是否存在。#假设可以指向魔免随从
		#这里调用携带的法术类的available函数的同时需要向其传导self，从而让其知道self.selectableCharExists用的是什么实例的方法
		return type(self).info1.available(self) and type(self).info2.available(self)
		
	def targetCorrect(self, obj, choice=0, ith=0):
		if obj == self: return False
		typeSelf = type(self)
		if typeSelf.info1.numTargetsNeeded(): return typeSelf.info1.targetCorrect(obj)
		if typeSelf.info2.numTargetsNeeded(): return typeSelf.info2.targetCorrect(obj)
		return True
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		#假设是随机选取一个发现选项。
		typeSelf = type(self)
		typeSelf.info1(self.Game, self.ID).cast(target)
		typeSelf.info2(self.Game, self.ID).cast(target)
		
	
class EVILGenius(Minion):
	Class, race, name = "Warlock", "", "EVIL Genius"
	mana, attack, health = 2, 2, 2
	name_CN = "怪盗天才"
	numTargets, Effects, description = 1, "", "Battlecry: Destroy a friendly minion to add 2 random Lackeys to your hand"
	index = "Battlecry"
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists(self.ID)
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.ID == self.ID and obj is not self and obj.onBoard 
		
	def effCanTrig(self):
		self.effectViable = self.targetExists()
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for obj in target:
			self.Game.kill(self, obj)
			self.addCardtoHand(numpyChoice(EVILCableRat.lackeys, 2, replace=True), self.ID)
		
	
class RafaamsScheme(Spell):
	Class, school, name = "Warlock", "Fire", "Rafaam's Scheme"
	numTargets, mana, Effects = 0, 3, ""
	description = "Summon 1 1/1 Imp(Upgrades each turn!)"
	name_CN = "拉法姆的阴谋"
	trigHand = Trig_Upgrade
	def text(self): return self.progress
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon([Imp_Shadows(self.Game, self.ID) for i in range(self.progress)])
		
	
class AranasiBroodmother(Minion):
	Class, race, name = "Warlock", "Demon", "Aranasi Broodmother"
	mana, attack, health = 6, 4, 6
	numTargets, Effects, description = 0, "Taunt", "Taunt. When you draw this, restore 4 Health to your hero"
	name_CN = "阿兰纳斯蛛后"
	def whenDrawn(self):
		self.heals(self.Game.heroes[self.ID], self.calcHeal(4))
		
	
class PlotTwist(Spell):
	Class, school, name = "Warlock", "", "Plot Twist"
	numTargets, mana, Effects = 0, 2, ""
	description = "Shuffle your hand into your deck. Draw that many cards"
	name_CN = "情势反转"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		#把随从洗回牌库会消除其上的身材buff,费用效果以及卡牌升级进度（如迦拉克隆的升级）
		handSize = len(self.Game.Hand_Deck.hands[self.ID])
		self.Game.Hand_Deck.shuffle_Hand2Deck(0, self.ID, initiatorID=self.ID, getAll=True)
		for i in range(handSize): self.Game.Hand_Deck.drawCard(self.ID)
		
	
class Impferno(Spell):
	Class, school, name = "Warlock", "Fire", "Impferno"
	numTargets, mana, Effects = 0, 3, ""
	description = "Give your Demons +1 Attack. Deal 1 damage to all enemy minions"
	name_CN = "小鬼狱火"
	def text(self): return self.calcDamage(1)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(self.Game.minionsonBoard(self.ID, race="Demon"), 1, 1, source=Impferno)
		self.dealsDamage(self.Game.minionsonBoard(3-self.ID), self.calcDamage(1))
		
	
class EagerUnderling(Minion):
	Class, race, name = "Warlock", "", "Eager Underling"
	mana, attack, health = 4, 2, 2
	numTargets, Effects, description = 0, "", "Deathrattle: Give two random friendly minions +2/+2"
	name_CN = "性急的杂兵"
	deathrattle = Death_EagerUnderling
	
	
class DarkestHour(Spell):
	Class, school, name = "Warlock", "Shadow", "Darkest Hour"
	numTargets, mana, Effects = 0, 6, ""
	description = "Destroy all friendly minions. For each one, summon a random minion from your deck"
	name_CN = "至暗时刻"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		game = self.Game
		friendlyMinions = game.minionsonBoard(self.ID)
		boardSize = len(friendlyMinions)
		game.kill(self, friendlyMinions)
		#对于所有友方随从强制死亡，并令其离场，因为召唤的随从是在场上右边，不用记录死亡随从的位置
		game.gathertheDead()
		for _ in range(boardSize):
			if not self.try_SummonfromOwn(): break
		
	
class JumboImp(Minion):
	Class, race, name = "Warlock", "Demon", "Jumbo Imp"
	mana, attack, health = 10, 8, 8
	numTargets, Effects, description = 0, "", "Costs (1) less whenever a friendly minion dies while this is in your hand"
	name_CN = "巨型小鬼"
	trigHand = Trig_JumboImp
	
	
class ArchVillainRafaam(Minion):
	Class, race, name = "Warlock", "", "Arch-Villain Rafaam"
	mana, attack, health = 7, 7, 8
	name_CN = "至尊盗王拉法姆"
	numTargets, Effects, description = 0, "Taunt", "Battlecry: Replace your hand and deck with Legendary minions"
	index = "Battlecry~Legendary"
	poolIdentifier = "Legendary Minions"
	@classmethod
	def generatePool(cls, pools):
		return "Legendary Minions", pools.LegendaryMinions
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		#不知道拉法姆的替换手牌、牌库和迦拉克隆会有什么互动。假设不影响主迦拉克隆。
		game = self.Game
		minions = self.rngPool("Legendary Minions")
		hand = tuple(numpyChoice(minions, len(game.Hand_Deck.hands[self.ID]), replace=True))
		deck = tuple(numpyChoice(minions, len(game.Hand_Deck.dekcs[self.ID]), replace=True))
		typeSelf = type(self)
		if hand:
			self
		if deck:
			newDeck = [card(self.Game, self.ID) for card in deck]
			game.Hand_Deck.replaceCardsinDeck(self.ID, range(len(deck)), newDeck, creator=typeSelf)
		
	
class FelLordBetrug(Minion):
	Class, race, name = "Warlock", "Demon", "Fel Lord Betrug"
	mana, attack, health = 8, 5, 7
	name_CN = "邪能领主贝图格"
	numTargets, Effects, description = 0, "", "Whenever you draw a minion, summon a copy with Rush that dies at end of turn"
	index = "Legendary"
	trigBoard = Trig_FelLordBetrug		
	
	
class ImproveMorale(Spell):
	Class, school, name = "Warrior", "", "Improve Morale"
	numTargets, mana, Effects = 1, 1, ""
	description = "Deal 1 damage to a minion. If it survives, add a Lackey to your hand"
	name_CN = "提振士气"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def text(self): return self.calcDamage(1)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		damage = self.calcDamage(1)
		for obj in target:
			self.dealsDamage(obj, damage)
			if obj.health > 0 and not obj.dead: self.addCardtoHand(numpyChoice(EVILCableRat.lackeys), self.ID)
		
	
class ViciousScraphound(Minion):
	Class, race, name = "Warrior", "Mech", "Vicious Scraphound"
	mana, attack, health = 2, 2, 2
	numTargets, Effects, description = 0, "", "Whenever this minion deals damage, gain that much Armor"
	name_CN = "凶恶的废钢猎犬"
	trigBoard = Trig_ViciousScraphound		
	
	
class DrBoomsScheme(Spell):
	Class, school, name = "Warrior", "", "Dr. Boom's Scheme"
	numTargets, mana, Effects = 0, 4, ""
	description = "Gain 1 Armor. (Upgrades each turn!)"
	name_CN = "砰砰博士的阴谋"
	trigHand = Trig_Upgrade
	def text(self): return self.progress
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveHeroAttackArmor(self.ID, armor=self.progress)
		
	
class SweepingStrikes(Spell):
	Class, school, name = "Warrior", "", "Sweeping Strikes"
	numTargets, mana, Effects = 1, 2, ""
	description = "Give a minion 'Also damages minions next to whoever this attacks'"
	name_CN = "横扫攻击"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(target, effGain="Sweep", source=SweepingStrikes)
		
	
class ClockworkGoblin(Minion):
	Class, race, name = "Warrior", "Mech", "Clockwork Goblin"
	mana, attack, health = 3, 3, 3
	name_CN = "发条地精"
	numTargets, Effects, description = 0, "", "Battlecry: Shuffle a Bomb in to your opponent's deck. When drawn, it explodes for 5 damage"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.shuffleintoDeck(Bomb(self.Game, 3-self.ID), enemyCanSee=True)
		
	
class OmegaDevastator(Minion):
	Class, race, name = "Warrior", "Mech", "Omega Devastator"
	mana, attack, health = 4, 4, 5
	name_CN = "欧米茄毁灭者"
	numTargets, Effects, description = 1, "", "Battlecry: If you have 10 Mana Crystals, deal 10 damage to a minion"
	index = "Battlecry"
	def numTargetsNeeded(self, choice=0):
		return 1 if self.Game.Manas.manasUpper[self.ID] >= 10 else 0
		
	def effCanTrig(self):
		self.effectViable = self.Game.Manas.manasUpper[self.ID] >= 10 and self.targetExists()
		
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj is not self and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.Game.Manas.manasUpper[self.ID] >= 10: self.dealsDamage(target, 10)
		
	
class Wrenchcalibur(Weapon):
	Class, name, description = "Warrior", "Wrenchcalibur", "After your hero attacks, shuffle a Bomb into your Opponent's deck"
	mana, attack, durability, Effects = 4, 3, 2, ""
	name_CN = "圣剑扳手"
	trigBoard = Trig_Wrenchcalibur		
	
	
class BlastmasterBoom(Minion):
	Class, race, name = "Warrior", "", "Blastmaster Boom"
	mana, attack, health = 7, 7, 7
	name_CN = "爆破之王砰砰"
	numTargets, Effects, description = 0, "", "Battlecry: Summon two 1/1 Boom Bots for each Bomb in your opponent's deck"
	index = "Battlecry~Legendary"
	def effCanTrig(self):
		self.effectViable = any(card.name == "Bomb" for card in self.Game.Hand_Deck.decks[3-self.ID])
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if numSummon := min(8, 2 * sum(card.name == "Bomb" for card in self.Game.Hand_Deck.decks[3-self.ID])):
			self.summon([BoomBot(self.Game, self.ID) for i in range(numSummon)], relative="<>")
		
	
class DimensionalRipper(Spell):
	Class, school, name = "Warrior", "", "Dimensional Ripper"
	numTargets, mana, Effects = 0, 10, ""
	description = "Summon 2 copies of a minion in your deck"
	name_CN = "空间撕裂器"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if minions := [card for card in self.Game.Hand_Deck.decks[self.ID] if card.category == "Minion"]:
			minion = numpyChoice(minions)
			self.summon([self.copyCard(minion, self.ID) for _ in (0, 1)])
		
	
class TheBoomReaver(Minion):
	Class, race, name = "Warrior", "Mech", "The Boom Reaver"
	mana, attack, health = 10, 7, 9
	name_CN = "砰砰机甲"
	numTargets, Effects, description = 0, "", "Battlecry: Summon a copy of a minion in your deck. Give it Rush"
	index = "Battlecry~Legendary"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.Game.space(self.ID) > 0 and \
				(minions := [card for card in self.Game.Hand_Deck.decks[self.ID] if card.category == "Minion"]):
			if Copy := self.summon(self.copyCard(numpyChoice(minions), self.ID)):
				self.giveEnchant(Copy, effGain="Rush", source=TheBoomReaver)
		
	


AllClasses_Shadows = [
	Twinspell, Aura_WhirlwindTempest, ManaAura_KirinTorTricaster, ManaAura_Kalecgos, Death_HenchClanHogsteed, Death_RecurringVillain,
	Death_EccentricScribe, Death_Safeguard, Death_TunnelBlaster, Death_Acornbearer, Death_Lucentbark, Death_Shimmerfly,
	Death_Ursatron, Death_Oblivitron, Death_BronzeHerald, Death_EVILConscripter, Death_HenchClanShadequill, Death_ConvincingInfiltrator,
	Death_WagglePick, Death_SouloftheMurloc, Death_EagerUnderling, Trig_MagicCarpet, Trig_ArchmageVargoth, Trig_ProudDefender,
	Trig_SoldierofFortune, Trig_AzeriteElemental, Trig_ExoticMountseller, Trig_UnderbellyOoze, Trig_Batterhead, Trig_BigBadArchmage,
	Trig_KeeperStalladris, Trig_Lifeweaver, Trig_SpiritofLucentbark, Trig_ArcaneFletcher, Trig_ThoridaltheStarsFury,
	GameRuleAura_Khadgar, Trig_MagicDartFrog, Trig_NeverSurrender, GameRuleAura_CommanderRhyssa, Trig_Upgrade, Trig_CatrinaMuerte,
	Trig_Vendetta, Trig_TakNozwhisker, Trig_UnderbellyAngler, ManaAura_Scargil, Trig_JumboImp, Trig_FelLordBetrug,
	Trig_ViciousScraphound, Trig_Wrenchcalibur, ThoridaltheStarsFury_Effect, GameManaAura_Kalecgos, PotionVendor,
	Toxfin, ArcaneServant, DalaranLibrarian, EtherealLackey, FacelessLackey, GoblinLackey, KoboldLackey, WitchyLackey,
	TitanicLackey, DraconicLackey, EVILCableRat, HenchClanHogsteed, HenchClanSquire, ManaReservoir, SpellbookBinder,
	SunreaverSpy, ZayleShadowCloak, ArcaneWatcher, FacelessRager, FlightMaster, Gryphon, HenchClanSneak, MagicCarpet,
	SpellwardJeweler, ArchmageVargoth, Hecklebot, HenchClanHag, Amalgam, PortalKeeper, FelhoundPortal, Felhound, ProudDefender,
	SoldierofFortune, TravelingHealer, VioletSpellsword, AzeriteElemental, BaristaLynchen, DalaranCrusader, RecurringVillain,
	SunreaverWarmage, EccentricScribe, VengefulScroll, MadSummoner, Imp_Shadows, PortalOverfiend, Safeguard, VaultSafe,
	UnseenSaboteur, VioletWarden, ChefNomi, GreasefireElemental, ExoticMountseller, TunnelBlaster, UnderbellyOoze,
	Batterhead, HeroicInnkeeper, JepettoJoybuzz, WhirlwindTempest, BurlyShovelfist, ArchivistElysiana, BigBadArchmage,
	Acornbearer, Squirrel_Shadows, PiercingThorns, HealingBlossom, PiercingThorns_Option, HealingBlossom_Option, CrystalPower,
	CrystalsongPortal, DreamwayGuardians, CrystalDryad, KeeperStalladris, Lifeweaver, CrystalStag, BlessingoftheAncients2,
	BlessingoftheAncients, Lucentbark, TheForestsAid2, TheForestsAid, Treant_Shadows, RapidFire2, RapidFire, Shimmerfly,
	NineLives, Ursatron, ArcaneFletcher, MarkedShot, HuntingParty, Oblivitron, UnleashtheBeast2, UnleashtheBeast,
	Wyvern, VereesaWindrunner, ThoridaltheStarsFury, RayofFrost2, RayofFrost, Khadgar, MagicDartFrog, MessengerRaven,
	MagicTrick, ConjurersCalling2, ConjurersCalling, KirinTorTricaster, ManaCyclone, PowerofCreation, Kalecgos, NeverSurrender,
	LightforgedBlessing2, LightforgedBlessing, BronzeHerald, BronzeDragon, DesperateMeasures2, DesperateMeasures,
	MysteriousBlade, CalltoAdventure, DragonSpeaker, Duel, CommanderRhyssa, Nozari, EVILConscripter, HenchClanShadequill,
	UnsleepingSoul, ForbiddenWords, ConvincingInfiltrator, MassResurrection, LazulsScheme, ShadowyFigure, MadameLazul,
	CatrinaMuerte, DaringEscape, EVILMiscreant, HenchClanBurglar, TogwagglesScheme, UnderbellyFence, Vendetta, WagglePick,
	UnidentifiedContract, AssassinsContract, LucrativeContract, RecruitmentContract, TurncoatContract, HeistbaronTogwaggle,
	TakNozwhisker, Mutate, SludgeSlurper, SouloftheMurloc, UnderbellyAngler, HagathasScheme, WalkingFountain, WitchsBrew,
	Muckmorpher, Scargil, SwampqueenHagatha, DrustvarHorror, EVILGenius, RafaamsScheme, AranasiBroodmother, PlotTwist,
	Impferno, EagerUnderling, DarkestHour, JumboImp, ArchVillainRafaam, FelLordBetrug, ImproveMorale, ViciousScraphound,
	DrBoomsScheme, SweepingStrikes, ClockworkGoblin, OmegaDevastator, Wrenchcalibur, BlastmasterBoom, DimensionalRipper,
	TheBoomReaver, 
]

for class_ in AllClasses_Shadows:
	if issubclass(class_, Card):
		class_.index = "DALARAN" + ("~" if class_.index else '') + class_.index