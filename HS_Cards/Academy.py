from Parts.CardTypes import *
from Parts.TrigsAuras import *
from HS_Cards.AcrossPacks import HealingTotem, SearingTotem, StoneclawTotem, StrengthTotem, ManaWyrm
from HS_Cards.Shadows import EVILCableRat
from HS_Cards.Uldum import PlagueofDeath, PlagueofMadness, PlagueofMurlocs, PlagueofFlames, PlagueofWrath
from HS_Cards.Outlands import Minion_Dormantfor2turns
from HS_Cards.Barrens import FuryRank1, LivingSeedRank1, TameBeastRank1, FlurryRank1, ConvictionRank1, CondemnRank1,\
								WickedStabRank1, ChainLightningRank1, ImpSwarmRank1, ConditioningRank1
from Panda.CustomWidgets import posHandsTable, hprHandsTable, HandZone1_Y, HandZone2_Y, HandZone_Z, scale_Hand


class Aura_RobesofProtection(Aura_AlwaysOn):
	effGain, targets = "Evasive", "All"
	
	
class Aura_Kolek(Aura_AlwaysOn):
	attGain = 1
	
	
class Aura_VulperaToxinblade(Aura_AlwaysOn):
	attGain, targets = 2, "Weapon"
	
	
class Trig_Corrupt(TrigHand):
	signals = ("ManaPaid", "CardBeenPlayed",)
	def __init__(self, keeper):
		super().__init__(keeper)
		self.on = False
		
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper #在打出一张牌的时候先支付法力值，根据费用决定这个扳机是否激活。然后在实际发出一张牌已经被打出的信号时，决定是否应该实际腐化
		if signal == "ManaPaid": return num[0] > 0 and ID == kpr.ID and kpr.Game.kprinPlay.category != "Power" and kpr.inHand
		else: return self.on and ID == kpr.ID and kpr.inHand
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		if signal == "ManaPaid": self.on = num[0] > self.keeper.mana
		else:
			self.on = False
			(newkpr := type(kpr).corruptedType(kpr.Game, kpr.ID)).inheritEnchantmentsfrom(kpr)
			kpr.Game.Hand_Deck.replace1kprinHand(kpr, newkpr)
		#When the trig is copied, new trigCopy.on is always False
		
	
class Spellburst(TrigBoard):
	signals, oneTime = ("CardBeenPlayed",), True
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return comment == "Spell" and ID == self.keeper.ID and self.keeper.onBoard
		
	def trig(self, signal, ID, subject, target, num, comment, choice):
		if self.canTrig(signal, ID, subject, target, num, comment, choice):
			btn, GUI = self.keeper.btn, self.keeper.Game.GUI
			if btn and "SpecTrig" in btn.icons:
				btn.icons["SpecTrig"].trigAni()
			self.keeper.losesTrig(self)
			self.effect(signal, ID, subject, target, num, comment, 0)
		
	
class Trig_IntrepidInitiate(Spellburst):
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).giveEnchant(kpr, 2, 0, source=IntrepidInitiate)
		
	
class Trig_PenFlinger(Spellburst):
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).Game.returnObj2Hand(kpr, kpr)
		
	
class Trig_SphereofSapience(TrigBoard):
	signals = ("TurnStarts",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return ID == kpr.ID and kpr.onBoard and kpr.health > 0
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		if len(ownDeck := kpr.Game.Hand_Deck.decks[kpr.ID]) > 1:
			option = self.keeper.chooseFixedOptions('', options=[ownDeck[-1], NewFate()])
			if isinstance(option, NewFate):
				ownDeck.insert(0, ownDeck.pop())
				self.keeper.losesDurability()
		
	
class Trig_VoraciousReader(TrigBoard):
	signals = ("TurnEnds",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		#不知道疲劳的时候是否会一直抽牌，假设不会
		HD = self.keeper.Game.Hand_Deck
		while len(HD.hands[self.keeper.ID]) < 3:
			if HD.drawCard(self.keeper.ID)[0] is None: break # 假设疲劳1次的时候会停止抽牌
		
	
class Trig_EducatedElekk(TrigBoard):
	signals = ("CardPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return comment == "Spell" and self.keeper.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		for trig in self.keeper.deathrattles:
			if isinstance(trig, Death_EducatedElekk):
				trig.memory.append(subject.getBareInfo())
		
	
class Trig_EnchantedCauldron(Spellburst):
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		if spells := self.rngPool("%d-Cost Spells"%num[0]):
			numpyChoice(spells)(kpr.Game, kpr.ID).cast()
		
	
class Trig_CrimsonHothead(Spellburst):
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).giveEnchant(kpr, 1, 0, effGain="Taunt", source=CrimsonHothead)
		
	
class Trig_WretchedTutor(Spellburst):
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).dealsDamage(kpr.Game.minionsonBoard(exclude=kpr), 2)
		
	
class Trig_HeadmasterKelThuzad(TrigBoard):
	signals, oneTime = ("CardPlayed", "CardBeenPlayed", "ObjDied",), True
	def __init__(self, keeper):
		super().__init__(keeper)
		self.on = False
		
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		#假设检测方式是在一张法术打出时开始记录直到可以触发法术迸发之前的两次死亡结算中所有死亡随从
		if signal == "ObjDied": return self.on and target.category == "Minion"
		else: return comment == "Spell" and ID == kpr.ID and kpr.onBoard
		
	def trig(self, signal, ID, subject, target, num, comment, choice):
		if self.canTrig(signal, ID, subject, target, num, comment, choice):
			if signal == "CardPlayed": self.on = True
			elif signal == "ObjDied":
				if target.category == "Minion": self.memory.append(target.getBareInfo())
			else:
				game, ID = (kpr := self.keeper).Game, kpr.ID
				btn, GUI = kpr.btn, game.GUI
				if btn and "SpecTrig" in btn.icons: btn.icons["SpecTrig"].trigAni()
				kpr.losesTrig(self)
				if self.memory: kpr.summon([game.fabCard(tup, ID, kpr) for tup in self.memory])
		
	
class Trig_Ogremancer(TrigBoard):
	signals = ("CardPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return comment == "Spell" and ID != kpr.ID and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).summon(RisenSkeleton(kpr.Game, kpr.ID))
		
	
class Trig_OnyxMagescribe(Spellburst):
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		pool = self.rngPool(kpr.Game.heroes[kpr.ID].Class + " Spells")
		kpr.addCardtoHand(numpyChoice(pool, 2, replace=True), kpr.ID)
		

class Trig_KeymasterAlabaster(TrigBoard):
	signals = ("CardDrawn",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and target[0].ID != kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		Copy = kpr.copyCard(target[0], kpr.ID)
		Copy.manaMods.append(ManaMod(Copy, to=1))
		kpr.addCardtoHand(Copy, kpr.ID)
		
	
class Trig_TrueaimCrescent(TrigBoard):
	signals = ("HeroAttackedMinion",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		#The target can't be dying to trigger this
		return ID == kpr.ID and kpr.onBoard and not target.dead and target.health > 0
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		#随从的攻击顺序与它们的登场顺序一致
		#即使是被冰冻的随从也可以因为这个效果进行攻击，同时攻击不浪费攻击机会，同时可以触发巨型沙虫等随从的获得额外的攻击机会
		game = self.keeper.Game
		if minions := game.minionsAlive(self.keeper.ID):
			for minion in objs_SeqSorted(minions)[0]:
				if target.canBattle():
					if subject.canBattle: game.battle(minion, target)
				else: break
		
	
class Trig_AceHunterKreen(TrigBoard):
	signals, nextAniWaits = ("BattleStarted", "BattleFinished",), True
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return ID == kpr.ID and subject is not kpr and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		#目前的写法是这个战斗结束信号触发在受伤之后
		if signal == "BattleStarted": subject.getsEffect("Immune")
		else: subject.losesEffect("Immune")
		
	
class Trig_Magehunter(TrigBoard):
	signals = ("MinionAttackingMinion",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return subject is kpr and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		target.getsSilenced()
		
	
class Trig_BloodHerald(TrigHand):
	signals = ("ObjDied",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return target.category == "Minion" and kpr.inHand and target.ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).giveEnchant(kpr, 1, 1, source=BloodHerald, add2EventinGUI=False)
		
	
class Trig_FelGuardians(TrigHand):
	signals = ("ObjDied",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return target.category == "Minion" and kpr.inHand and target.ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		ManaMod(self.keeper, by=-1).applies()
		
	
class Trig_AncientVoidHound(TrigBoard):
	signals = ("TurnEnds",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return ID == kpr.ID and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		enemyMinions = kpr.Game.minionsonBoard(3-kpr.ID)
		for minion in enemyMinions:
			minion.enchantments.append(Enchantment(AncientVoidHound, -1, -1))
			minion.calcStat()
		if num := len(enemyMinions): kpr.giveEnchant(kpr, num, num, source=AncientVoidHound)
		
	
class Trig_Gibberling(Spellburst):
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.summon(Gibberling(self.keeper.Game, self.keeper.ID))
		
	
class Trig_SpeakerGidra(Spellburst):
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).giveEnchant(kpr, num[0], num[0], source=SpeakerGidra)
		
	
class Trig_TwilightRunner(TrigBoard):
	signals = ("MinionAttackingMinion", "MinionAttackingHero",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and subject is kpr
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		kpr.Game.Hand_Deck.drawCard(kpr.ID)
		kpr.Game.Hand_Deck.drawCard(kpr.ID)
		
	
class Trig_ForestWardenOmu(Spellburst):
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).Game.Manas.restoreManaCrystal(0, kpr.ID, restoreAll=True)
		
	
class GameRuleAura_ProfessorSlate(GameRuleAura):
	def auraAppears(self): self.keeper.Game.rules[self.keeper.ID]["Spells Poisonous"] += 1
		
	def auraDisappears(self): self.keeper.Game.rules[self.keeper.ID]["Spells Poisonous"] -= 1
		
	
class Trig_KroluskBarkstripper(Spellburst):
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		minions = kpr.Game.minionsAlive(3-kpr.ID)
		if minions: kpr.Game.kill(kpr, numpyChoice(minions))
		
	
class Trig_Firebrand(Spellburst):
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		minion, side = kpr, 3 - kpr.ID
		for _ in (1, 2, 3, 4):
			if minions := minion.Game.minionsAlive(side): minion.dealsDamage(numpyChoice(minions), 1)
			else: break
		
	
class Trig_JandiceBarov(TrigBoard):
	signals, description = ("MinionTakesDmg",), "This minion dies when it takes damage"
	def __init__(self, keeper):
		super().__init__(keeper)
		self.show = False
		
	def connect(self):
		if GUI := self.keeper.Game.GUI: self.show = not GUI.need2Hide(self.keeper)
		super().connect()
		
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and target is kpr
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).Game.kill(None, kpr)
		
	
class Trig_MozakiMasterDuelist(TrigBoard):
	signals = ("CardBeenPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return comment == "Spell" and ID == kpr.ID and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).giveEnchant(kpr, effGain="Spell Damage", source=MozakiMasterDuelist)
		
	
class Trig_WyrmWeaver(Spellburst):
	def effect(self, signal, ID, subject, target, num, comment, choice):
		game, ID = (kpr := self.keeper).Game, kpr.ID
		kpr.summon([ManaWyrm(game, ID) for _ in (0, 1)], relative="<>")
		
	
class Trig_GoodyTwoShields(Spellburst):
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).giveEnchant(kpr, effGain="Divine Shield", source=GoodyTwoShields)
		
	
class Trig_HighAbbessAlura(Spellburst):
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		HD = self.keeper.Game.Hand_Deck
		if indices := [i for i, card in enumerate(HD.decks[self.keeper.ID]) if card.category == "Spell"]:
			HD.extractfromDeck(numpyChoice(indices), kpr.ID).cast(prefered=lambda obj: obj == kpr)
			self.keeper.Game.gathertheDead()
		
	
class Trig_DevoutPupil(TrigHand):
	signals = ("CardBeenPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return comment == "Spell" and len(target) == 1 and ID == target[0].ID == kpr.ID and kpr.inHand
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).Game.Manas.calcMana_Single(kpr)
		
	
class Trig_TuralyontheTenured(TrigBoard):
	signals = ("MinionAttackingMinion",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and subject is kpr
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.setStat(target, (3, 3), source=TuralyontheTenured)
		
	
class Trig_PowerWordFeast(TrigBoard):
	signals, description = ("TurnEnds",), "Restore this minion to full health at the end of this turn"
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return self.keeper.onBoard #Even if the current turn is not minion's owner's turn
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		self.keeper.losesTrig(self, trigType="TrigBoard")
		heal = kpr.calcHeal(kpr.health_max)
		PowerWordFeast(kpr.Game, kpr.ID).heals(kpr, heal)
		
	
class Trig_CabalAcolyte(Spellburst):
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		if minions := [minion for minion in kpr.Game.minionsAlive(3-kpr.ID) if minion.attack < 3]:
			self.keeper.Game.minionSwitchSide(numpyChoice(minions))
		
	
class Trig_DisciplinarianGandling(TrigBoard):
	signals = ("CardBeenPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.Game.cardinPlay.category == "Minion" and ID == kpr.ID and kpr.onBoard and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).killandSummon(kpr.Game.cardinPlay, FailedStudent(kpr.Game, kpr.ID))
		
	
class Trig_FleshGiant(TrigHand):
	signals = ("HeroChangedHealthinTurn",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.inHand and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).Game.Manas.calcMana_Single(kpr)
		
	
class Trig_Plagiarize(Trig_Secret):
	signals = ("TurnEnds",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.ID != ID and kpr.Game.Counters.examCardPlays(ID, turnInd=kpr.Game.turnInd)
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		game, ownID = (kpr := self.keeper).Game, kpr.ID
		cards = [game.fabCard(tup, ownID, self.keeper) for tup in game.Counters.iter_CardPlays(ID, turnInd=game.turnInd)]
		kpr.addCardtoHand(cards, ownID)
		
	
class Trig_SelfSharpeningSword(TrigBoard):
	signals = ("HeroAttackedMinion", "HeroAttackedHero",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return ID == kpr.ID and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).giveEnchant(kpr, statEnchant=Enchantment_Exclusive(SelfSharpeningSword, 1, 0))
		
	
class Trig_ShiftySophomore(Spellburst):
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).addCardtoHand(numpyChoice(self.rngPool("Combo Cards")), kpr.ID)
		
	
class Trig_CuttingClass(TrigHand):
	signals = ("WeaponAppears", "WeaponDisappears", "WeaponStatCheck",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.inHand and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).Game.Manas.calcMana_Single(kpr)
		
	
class Trig_DoctorKrastinov(TrigBoard):
	signals = ("MinionAttackingMinion", "MinionAttackingHero",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return subject is kpr and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		weapon = kpr.Game.availableWeapon(kpr.ID)
		if weapon: kpr.giveEnchant(weapon, statEnchant=Enchantment_Exclusive(DoctorKrastinov, 1, 1))
		
	
class Trig_DiligentNotetaker(Spellburst):
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).addCardtoHand(type(kpr.Game.cardinPlay), kpr.ID)
		
	
class Trig_RuneDagger(TrigBoard):
	signals = ("HeroAttackedHero", "HeroAttackedMinion",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and subject is kpr.Game.heroes[kpr.ID]
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		kpr.giveEnchant(kpr.Game.heroes[kpr.ID], effGain="Spell Damage", source=RuneDagger)
		RuneDagger_Effect(kpr.Game, kpr.ID).connect()
		
	
class Trig_TrickTotem(TrigBoard):
	signals = ("TurnEnds",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		numpyChoice(self.rngPool("Spells Cost <=3"))((kpr := self.keeper).Game, kpr.ID).cast()
		
	
class Trig_RasFrostwhisper(TrigBoard):
	signals = ("TurnEnds",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).dealsDamage(kpr.Game.charsonBoard(3-kpr.ID), 1+kpr.countSpellDamage())
		
	
class Trig_CeremonialMaul(Spellburst):
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		if num[0] > 0 and kpr.Game.space(kpr.ID) > 0:
			minion = HonorStudent(kpr.Game, kpr.ID)
			minion.mana = min(num[0], 10)
			minion.attack_0 = minion.health_0 = minion.attack = minion.health = num[0]
			self.keeper.summon(minion)
		
	
class Trig_Playmaker(TrigBoard):
	signals = ("CardBeenPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return ID == kpr.ID and kpr.Game.cardinPlay.category == "Minion" and kpr.onBoard and kpr.effects["Rush"] > 0
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		Copy = kpr.copyCard(kpr.Game.cardinPlay, kpr.ID)
		for enchant in Copy.enchantments: enchant.handleStatMax(Copy)
		Copy.dmgTaken = Copy.health_max - 1
		self.keeper.summon(Copy)
		
	
class Trig_ReapersScythe(Spellburst):
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).giveEnchant(kpr, effectEnchant=Enchantment(ReapersScythe, effGain="Sweep", until=0))
		
	
class Trig_Troublemaker(TrigBoard):
	signals = ("TurnEnds",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		game = self.keeper.Game
		ruffians = [Ruffian(game, self.keeper.ID) for _ in (0, 1)]
		self.keeper.summon(ruffians, relative="<>")
		for ruffian in ruffians:
			if objs := game.charsAlive(3-self.keeper.ID):
				if ruffian.canBattle(): game.battle(ruffian, numpyChoice(objs))
			else: break
		
	
class Death_SneakyDelinquent(Deathrattle):
	description = "Deathrattle: Add a 3/1 Ghost with Stealth to your hand"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.addCardtoHand(SpectralDelinquent, self.keeper.ID)
		
	
class Death_EducatedElekk(Deathrattle):
	description = "Deathrattle: Shuffle remembered spells into your deck"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		game, ID = (kpr := self.keeper).Game, kpr.ID
		kpr.shuffleintoDeck([game.fabCard(tup, ID, kpr) for tup in self.memory])
		
	
class Death_FishyFlyer(Deathrattle):
	description = "Deathrattle: Add a 4/3 Ghost with Rush to your hand"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.addCardtoHand(SpectralFlyer, self.keeper.ID)
		
	
class Death_SmugSenior(Deathrattle):
	description = "Deathrattle: Add a 5/7 Ghost with Taunt to your hand"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.addCardtoHand(SpectralSenior, self.keeper.ID)
		
	
class Death_PlaguedProtodrake(Deathrattle):
	description = "Deathrattle: Summon a random 7-Cost minion"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).summon(numpyChoice(self.rngPool("7-Cost Minions to Summon"))(kpr.Game, kpr.ID))
		
	
class Death_BloatedPython(Deathrattle):
	description = "Deathrattle: Summon a 4/4 Hapless Handler"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).summon(HaplessHandler(kpr.Game, kpr.ID))
		
	
class Death_TeachersPet(Deathrattle):
	description = "Deathrattle: Summon a random 3-Cost Beast"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).summon(numpyChoice(self.rngPool("3-Cost Beasts to Summon"))(kpr.Game, kpr.ID))
		
	
class Death_InfiltratorLilian(Deathrattle):
	description = "Deathrattle: Summon a 4/2 Forsaken Lilian that attacks a random enemy"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		minion = ForsakenLilian(self.keeper.Game, self.keeper.ID)
		self.keeper.summon(minion)
		if objs := self.keeper.Game.charsAlive(3-self.keeper.ID) and minion.canBattle():
			self.keeper.Game.battle(minion, numpyChoice(objs))
		
	
class Death_TotemGoliath(Deathrattle):
	description = "Deathrattle: Summon all four basic totems"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		minion, game = self.keeper, self.keeper.Game
		minion.summon([totem(game, minion.ID) for totem in (HealingTotem, SearingTotem, StoneclawTotem, StrengthTotem)])
		
	
class Death_BonewebEgg(Deathrattle):
	description = "Deathrattle: Summon two 2/1 Spiders"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		game, ID = (kpr := self.keeper).Game, kpr.ID
		kpr.summon([BonewebSpider(game, ID) for _ in (0, 1)])
		
	
class Death_LordBarov(Deathrattle):
	description = "Deathrattle: Deal 1 damage to all minions"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.dealsDamage(self.keeper.Game.minionsonBoard(), 1)
		
	
class Death_Rattlegore(Deathrattle):
	def effect(self, signal, ID, subject, target, num, comment, choice):
		#https://www.bilibili.com/video/BV1Uy4y1C73o 机制测试
		#血骨傀儡的亡语的实质是在随从死亡并进行了身材重置之后检测其身材，计算得到-1/-1后的身材，然后召唤一个与原来相同身材的随从。之后再把这个随从的身材白字改为计算得到的那个身材
		#召唤的3/3血骨傀儡在场上有卡德加的时候会召唤2/2和3/3（卡德加复制得到的那个随从不执行-1/-1）
		#buff得到的身材在进入墓地时会清除，但是场上的随从因为装死等效果直接触发时是可以直接检测到buff的身材的，比如20/19的血骨傀儡可以因为装死召唤一个19/18
		#其他随从获得了血骨傀儡的身材之后可以召唤自身而不是血骨傀儡，如送葬者
		#与水晶核心的互动：4/4的血骨傀儡在死亡后先召唤4/4的血骨傀儡，与水晶核心作用，然后被这个亡语-1/-1,形成一个3/3。这个3/3死亡后被检测，预定最终 被变成2/2先召唤3/3
		#血骨傀儡的亡语只会处理第一个召唤出来的随从的身材，如果有翻倍召唤，则其他复制是原身材
		#在场上触发亡语时，检测的是满状态的生命值，即使受伤也是从最大生命值计算
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
			subclass = type(cardType.__name__ + "__%d_%d"%(attack_0, health_0), (cardType,),
							{"mana": cost, "attack": attack_0, "health": health_0,
							 "index": index}
							)
			minion.summon(subclass(minion.Game, minion.ID))
		
	
class GameManaAura_TourGuide(GameManaAura_OneTime):
	to, temporary, targets = 0, False, "Power"
	def applicable(self, target): return target.ID == self.ID and target.category == "Power"
		
	
class GameManaAura_CultNeophyte(GameManaAura_OneTime):
	signals, by = ("HandCheck",), +1
	def applicable(self, target): return target.ID == self.ID and target.category == "Spell"
		
	
class GameManaAura_NatureStudies(GameManaAura_OneTime):
	by, temporary = -1, False
	def applicable(self, target): return target.ID == self.ID and target.category == "Spell"
		
	
class GameManaAura_CarrionStudies(GameManaAura_OneTime):
	by, temporary = -1, False
	def applicable(self, target): return target.ID == self.ID and target.category == "Minion" and target.deathrattles
		
	
class GameManaAura_DraconicStudies(GameManaAura_OneTime):
	by, temporary = -1, False
	def applicable(self, target): return target.ID == self.ID and "Dragon" in target.race
		
	
class MindrenderIllucia_Effect(TrigEffect):
	trigType = "TurnEnd&OnlyKeepOne"
	def __init__(self, Game, ID, memory=()):
		super().__init__(Game, ID)
		self.memory = memory
		
	def trigEffect(self):
		self.Game.Hand_Deck.extractfromHand(None, self.ID, getAll=True)
		if self.memory: self.Game.Hand_Deck.addCardtoHand(self.memory, self.ID)
		
	def assistCreateCopy(self, Copy):
		Copy.memory = [card.createCopy(Copy.Game) for card in self.memory]
		
	
class SecretPassage_Effect(TrigEffect):
	trigType = "TurnEnd"
	def __init__(self, Game, ID, memory=((), ())):
		super().__init__(Game, ID)
		self.memory, self.counter = memory, len(memory[0])

	def trigEffect(self):
		HD, *(fromHand, fromDeck) = self.Game.Hand_Deck, self.memory
		cards2Return2Deck = [card for card in HD.hands[self.ID] if card in fromDeck]
		for card in cards2Return2Deck:
			HD.extractfromHand(card, self.ID, getAll=False, enemyCanSee=False, animate=False)
			card.reset(self.ID)
		GUI = self.Game.GUI
		if GUI:
			SecretPassage.panda_CardsLeaveHand(self.Game, GUI, cards2Return2Deck)
			Y = HandZone1_Y if self.ID == self.Game.GUI.ID else HandZone2_Y
			poses, hprs = posHandsTable[Y][len(cards2Return2Deck)], hprHandsTable[Y][len(cards2Return2Deck)]
			SecretPassage.panda_BackfromPassage(self.Game, GUI, fromHand, poses, hprs)
		HD.decks[self.ID] += cards2Return2Deck
		for card in cards2Return2Deck:
			card.entersDeck()
		numpyShuffle(HD.decks[self.ID])
		if GUI: GUI.deckZones[self.ID].draw(len(HD.decks[self.ID]), len(HD.hands[self.ID]))
		HD.addCardtoHand(fromHand, self.ID)
		self.Game.turnEndTrigger.remove(self)
		if GUI: GUI.heroZones[self.ID].removeaTrig(self.card)
		
	def assistCreateCopy(self, Copy):
		Copy.memory = tuple(tuple(card.createCopy(Copy.Game) for card in tup) for tup in self.memory)

	
class GameManaAura_PrimordialStudies(GameManaAura_OneTime):
	by, temporary = -1, False
	def applicable(self, target): return target.ID == self.ID and target.category == "Minion" and target.effects["Spell Damage"] > 0
		
	
class RuneDagger_Effect(TrigEffect):
	counter, trigType = 1, "TurnEnd&OnlyKeepOne"
	def trigEffect(self): self.Game.heroes[self.ID].losesEffect("Spell Damage")
		
	
class InstructorFireheart_Effect(TrigEffect):
	signals, trigType = ("CardBeenPlayed",), "Conn&TurnEnd"
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return subject is self.memory
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		HeroClass = class4Discover(self.card)
		card, _ = self.card.discoverNew('', lambda : self.card.rngPool(HeroClass+" Spells Cost >=1"))
		self.memory = card
		
	
class GameManaAura_DemonicStudies(GameManaAura_OneTime):
	by, temporary = -1, False
	def applicable(self, target): return target.ID == self.ID and "Demon" in target.race
		
	
class GameManaAura_AthleticStudies(GameManaAura_OneTime):
	by, temporary = -1, False
	def applicable(self, target): return target.ID == self.ID and target.category == "Minion" and target.effects["Rush"] > 0
		
	
class Variant_TransferStudent(Minion):
	Class, race, name = "Neutral", "", "Transfer Student"
	mana, attack, health = 2, 2, 2
	name_CN = "转校生"
	
	
class TransferStudent_Ogrimmar(Variant_TransferStudent):
	index = "Battlecry"
	numTargets, Effects, description = 1, "", "Battlecry: Deal 2 damage"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(target, 2)
		
	
class TransferStudent_Stormwind(Variant_TransferStudent):
	numTargets, Effects, description = 0, "Divine Shield", "Divine Shield"
	
	
class TransferStudent_Stranglethorn(Variant_TransferStudent):
	numTargets, Effects, description = 0, "Stealth,Poisonous", "Stealth, Poisonous"
	
	
class TransferStudent_FourWindValley(Variant_TransferStudent):
	index = "Battlecry"
	numTargets, Effects, description = 1, "", "Battlecry: Give a friendly minion +1/+2"
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists(self.ID, choice)
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.ID == self.ID and obj is not self and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(target, 1, 2, source=TransferStudent_FourWindValley)
		
	
class TransferStudent_Shadows(Variant_TransferStudent):
	index = "Battlecry"
	numTargets, Effects, description = 0, "", "Battlecry: Add a Lackey to your hand"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.addCardtoHand(numpyChoice(EVILCableRat.lackeys), self.ID)
		
	
class TransferStudent_UldumDesert(Variant_TransferStudent):
	numTargets, Effects, description = 0, "Reborn", "Reborn"
	
	
class TransferStudent_UldumOasis(Variant_TransferStudent):
	index = "Battlecry"
	numTargets, Effects, description = 0, "", "Battlecry: Add a Uldum plague card to your hand"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.addCardtoHand(numpyChoice((PlagueofDeath, PlagueofMadness, PlagueofMurlocs, PlagueofFlames, PlagueofWrath)), self.ID)
		
	
class TransferStudent_Dragons(Variant_TransferStudent):
	index = "Battlecry"
	numTargets, Effects, description = 0, "", "Battlecry: Discover a Dragon"
	poolIdentifier = "Dragons as Druid"
	@classmethod
	def generatePool(cls, pools):
		return genPool_MinionsofRaceasClass(pools, "Dragon")
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.discoverNew(comment, lambda : self.rngPool("Dragons as "+class4Discover(self)))
		
	
class TransferStudent_Outlands(Minion_Dormantfor2turns):
	Class, race, name = "Neutral", "", "Transfer Student"
	mana, attack, health = 2, 2, 2
	numTargets, Effects, description = 0, "", "Dormant for 2 turns. When this awakens, deal 3 damage to 2 random enemy minions"
	name_CN = "转校生"
	def awakenEffect(self):
		if minions := self.Game.minionsAlive(3-self.ID):
			self.dealsDamage(numpyChoice(minions, min(len(minions), 2), replace=False), 3)
		
	
class TransferStudent_Academy(Variant_TransferStudent):
	index = "Battlecry"
	numTargets, Effects, description = 0, "", "Battlecry: Add a random Dual Class card to your hand"
	poolIdentifier = "Dual Class Cards"
	@classmethod
	def generatePool(cls, pools):
		return "Dual Class Cards", [card for cards in pools.ClassCards.values() for card in cards if card.Class.count(",") == 1]
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.addCardtoHand(numpyChoice(self.rngPool("Dual Class Cards")), self.ID)
		
	
class TransferStudent_Darkmoon_Corrupt(Minion):
	Class, race, name = "Neutral", "", "Transfer Student"
	mana, attack, health = 2, 4, 4
	name_CN = "转校生"
	numTargets, Effects, description = 0, "", ""
	index = "Uncollectible"
	
	
class TransferStudent_Darkmoon(Variant_TransferStudent):
	numTargets, Effects, description = 0, "", "Corrupt: Gain +2/+2"
	trigHand, corruptedType = Trig_Corrupt, TransferStudent_Darkmoon_Corrupt
	
	
class TransferStudent_Barrens(Variant_TransferStudent):
	index = "Battlecry"
	numTargets, Effects, description = 0, "", "Battlecry: Add a random Ranked Spell to your hand"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.addCardtoHand(numpyChoice((FuryRank1, LivingSeedRank1, TameBeastRank1, FlurryRank1, ConvictionRank1, CondemnRank1,
										WickedStabRank1, ChainLightningRank1, ImpSwarmRank1, ConditioningRank1)), self.ID)
		
	
class TransferStudent_UnitedinStormwind(Variant_TransferStudent):
	index = "Battlecry"
	numTargets, Effects, description = 1, "", "Tradeable. Battlecry: Give a friendly minion Divine Shield"
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists(self.ID)
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.ID == self and obj is not self and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(target, effGain="Divine Shield", source=TransferStudent_UnitedinStormwind)
		
	
class TransferStudent(Minion):
	Class, race, name = "Neutral", "", "Transfer Student"
	mana, attack, health = 2, 2, 2
	numTargets, Effects, description = 0, "", "This has different effects based on which game board you're on"
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
	numTargets, Effects, description = 0, "", ""
	name_CN = "课桌小鬼"
	
	
class AnimatedBroomstick(Minion):
	Class, race, name = "Neutral", "", "Animated Broomstick"
	mana, attack, health = 1, 1, 1
	name_CN = "活化扫帚"
	numTargets, Effects, description = 0, "Rush", "Rush. Battlecry: Give your other minions Rush"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(self.Game.minionsonBoard(self.ID, exclude=self), effGain="Rush", source=AnimatedBroomstick)
		
	
class IntrepidInitiate(Minion):
	Class, race, name = "Neutral", "", "Intrepid Initiate"
	mana, attack, health = 1, 1, 2
	numTargets, Effects, description = 0, "", "Spellburst: Gain +2 Attack"
	name_CN = "新生刺头"
	trigBoard = Trig_IntrepidInitiate		
	
	
class PenFlinger(Minion):
	Class, race, name = "Neutral", "", "Pen Flinger"
	mana, attack, health = 1, 1, 1
	name_CN = "甩笔侏儒"
	numTargets, Effects, description = 1, "", "Battlecry: Deal 1 damage. Spellburst: Return this to your hand"
	index = "Battlecry"
	trigBoard = Trig_PenFlinger		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(target, 1)
		
	
class SphereofSapience(Weapon):
	Class, name, description = "Neutral", "Sphere of Sapience", "At the start of your turn, look at your top card. You can put it on the bottom and lose 1 Durability"
	mana, attack, durability, Effects = 1, 0, 4, ""
	name_CN = "感知宝珠"
	index = "Legendary"
	trigBoard = Trig_SphereofSapience		
	
	
class NewFate(Option):
	name, description = "New Fate", "Draw a new card"
	mana, attack, health = 0, -1, -1
	
	
class TourGuide(Minion):
	Class, race, name = "Neutral", "", "Tour Guide"
	mana, attack, health = 1, 1, 1
	name_CN = "巡游向导"
	numTargets, Effects, description = 0, "", "Battlecry: Your next Hero Power costs (0)"
	index = "Battlecry"
	trigEffect = GameManaAura_TourGuide
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		GameManaAura_TourGuide(self.Game, self.ID).auraAppears()
		
	
class CultNeophyte(Minion):
	Class, race, name = "Neutral", "", "Cult Neophyte"
	mana, attack, health = 2, 3, 2
	name_CN = "异教低阶牧师"
	numTargets, Effects, description = 0, "", "Battlecry: Your opponent's spells cost (1) more next turn"
	index = "Battlecry"
	trigEffect = GameManaAura_CultNeophyte
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		GameManaAura_CultNeophyte(self.Game, 3-self.ID).auraAppears()
		
	
class ManafeederPanthara(Minion):
	Class, race, name = "Neutral", "Beast", "Manafeeder Panthara"
	mana, attack, health = 2, 2, 3
	name_CN = "食魔影豹"
	numTargets, Effects, description = 0, "", "Battlecry: If you've used your Hero Power this turn, draw a card"
	index = "Battlecry"
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.examCardPlays(self.ID, turnInd=self.Game.turnInd, cond=lambda tup: tup[0].category == "Power")
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.Game.Counters.examCardPlays(self.ID, turnInd=self.Game.turnInd, cond=lambda tup: tup[0].category == "Power"):
			self.Game.Hand_Deck.drawCard(self.ID)
		
	
class SneakyDelinquent(Minion):
	Class, race, name = "Neutral", "", "Sneaky Delinquent"
	mana, attack, health = 2, 3, 1
	numTargets, Effects, description = 0, "Stealth", "Stealth. Deathrattle: Add a 3/1 Ghost with Stealth to your hand"
	name_CN = "少年惯偷"
	deathrattle = Death_SneakyDelinquent
	
	
class SpectralDelinquent(Minion):
	Class, race, name = "Neutral", "", "Spectral Delinquent"
	mana, attack, health = 2, 3, 1
	name_CN = "鬼灵惯偷"
	numTargets, Effects, description = 0, "Stealth", "Stealth"
	index = "Uncollectible"
	
	
class VoraciousReader(Minion):
	Class, race, name = "Neutral", "", "Voracious Reader"
	mana, attack, health = 3, 1, 3
	numTargets, Effects, description = 0, "", "At the end of your turn, draw until you have 3 cards"
	name_CN = "贪婪的书虫"
	trigBoard = Trig_VoraciousReader		
	
	
class Wandmaker(Minion):
	Class, race, name = "Neutral", "", "Wandmaker"
	mana, attack, health = 2, 2, 2
	name_CN = "魔杖工匠"
	numTargets, Effects, description = 0, "", "Battlecry: Add a 1-Cost spell from your class to your hand"
	index = "Battlecry"
	poolIdentifier = "1-Cost Spells as Druid"
	@classmethod
	def generatePool(cls, pools):
		return ["1-Cost Spells as %s"%Class for Class in pools.Classes], \
				[[card for card in pools.ClassCards[Class] if card.category == "Spell" and card.mana == 1] for Class in pools.Classes]
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.addCardtoHand(numpyChoice(self.rngPool("1-Cost Spells as "+self.Game.heroes[self.ID].Class)), self.ID)
		
	
class EducatedElekk(Minion):
	Class, race, name = "Neutral", "Beast", "Educated Elekk"
	mana, attack, health = 3, 3, 4
	numTargets, Effects, description = 0, "", "Whenever a spell is played, this minion remembers it. Deathrattle: Shuffle the spells into your deck"
	name_CN = "驯化的雷象"
	trigBoard, deathrattle = Trig_EducatedElekk, Death_EducatedElekk
	
	
class EnchantedCauldron(Minion):
	Class, race, name = "Neutral", "", "Enchanted Cauldron"
	mana, attack, health = 3, 1, 6
	numTargets, Effects, description = 0, "", "Spellburst: Cast a random spell of the same Cost"
	name_CN = "魔化大锅"
	trigBoard = Trig_EnchantedCauldron
	
	
class RobesofProtection(Minion):
	Class, race, name = "Neutral", "", "Robes of Protection"
	mana, attack, health = 3, 2, 4
	numTargets, Effects, description = 0, "", "Your minions have 'Can't be targeted by spells or Hero Powers'"
	name_CN = "防护长袍"
	aura = Aura_RobesofProtection
	
	
class CrimsonHothead(Minion):
	Class, race, name = "Neutral", "Dragon", "Crimson Hothead"
	mana, attack, health = 4, 3, 6
	numTargets, Effects, description = 0, "", "Spellburst: Gain +1 Attack and Taunt"
	name_CN = "赤红急先锋"
	trigBoard = Trig_CrimsonHothead
	
	
class DivineRager(Minion):
	Class, race, name = "Neutral", "Elemental", "Divine Rager"
	mana, attack, health = 4, 5, 1
	numTargets, Effects, description = 0, "Divine Shield", "Divine Shield"
	name_CN = "神圣暴怒者"
	
	
class FishyFlyer(Minion):
	Class, race, name = "Neutral", "Murloc", "Fishy Flyer"
	mana, attack, health = 4, 4, 3
	numTargets, Effects, description = 0, "Rush", "Rush. Deathrattle: Add a 4/3 Ghost with Rush to your hand"
	name_CN = "鱼人飞骑"
	deathrattle = Death_FishyFlyer
	
	
class SpectralFlyer(Minion):
	Class, race, name = "Neutral", "Murloc", "Spectral Flyer"
	mana, attack, health = 4, 4, 3
	name_CN = "鬼灵飞骑"
	numTargets, Effects, description = 0, "Rush", "Rush"
	index = "Uncollectible"
	
	
class LorekeeperPolkelt(Minion):
	Class, race, name = "Neutral", "", "Lorekeeper Polkelt"
	mana, attack, health = 5, 4, 5
	name_CN = "博学者普克尔特"
	numTargets, Effects, description = 0, "", "Battlecry: Reorder your deck from the highest Cost card to the lowest Cost card"
	index = "Battlecry~Legendary"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		cardDict = {}
		for card in self.Game.Hand_Deck.decks[self.ID]:
			add2ListinDict(card, cardDict, card.mana)
		self.Game.Hand_Deck.decks[self.ID] = [] #After sorting using np, the 1st mana is the lowest
		(manas := list(cardDict.keys())).sort() #Doesn't reorder the card of same Cost
		for mana in manas: self.Game.Hand_Deck.decks[self.ID] += cardDict[mana]
		
	
class WretchedTutor(Minion):
	Class, race, name = "Neutral", "", "Wretched Tutor"
	mana, attack, health = 4, 2, 5
	numTargets, Effects, description = 0, "", "Spellburst: Deal 2 damage to all other minions"
	name_CN = "失心辅导员"
	trigBoard = Trig_WretchedTutor
	
	
class HeadmasterKelThuzad(Minion):
	Class, race, name = "Neutral", "", "Headmaster Kel'Thuzad"
	mana, attack, health = 5, 4, 6
	name_CN = "校长克尔苏加德"
	numTargets, Effects, description = 0, "", "Spellburst: If the spell destroys any minions, summon them"
	index = "Legendary"
	trigBoard = Trig_HeadmasterKelThuzad
	
	
class LakeThresher(Minion):
	Class, race, name = "Neutral", "Beast", "Lake Thresher"
	mana, attack, health = 5, 4, 6
	numTargets, Effects, description = 0, "Sweep", "Also damages the minions next to whomever this attacks"
	name_CN = "止水湖蛇颈龙"
	
	
class Ogremancer(Minion):
	Class, race, name = "Neutral", "", "Ogremancer"
	mana, attack, health = 5, 3, 7
	numTargets, Effects, description = 0, "", "Whenever your opponent casts a spell, summon a 2/2 Skeleton with Taunt"
	name_CN = "食人魔巫术师"
	trigBoard = Trig_Ogremancer
	
	
class RisenSkeleton(Minion):
	Class, race, name = "Neutral", "", "Risen Skeleton"
	mana, attack, health = 2, 2, 2
	name_CN = "复活的骷髅"
	numTargets, Effects, description = 0, "Taunt", "Taunt"
	index = "Uncollectible"
	
	
class StewardofScrolls(Minion):
	Class, race, name = "Neutral", "Elemental", "Steward of Scrolls"
	mana, attack, health = 5, 4, 4
	name_CN = "卷轴管理者"
	numTargets, Effects, description = 0, "Spell Damage", "Spell Damage +1. Battlecry: Discover a spell"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.discoverNew(comment, lambda : self.rngPool(class4Discover(self) + " Spells"))
		
	
class Vectus(Minion):
	Class, race, name = "Neutral", "", "Vectus"
	mana, attack, health = 5, 4, 4
	name_CN = "维克图斯"
	numTargets, Effects, description = 0, "", "Battlecry: Summon two 1/1 Whelps. Each gains a Deathrattle from your minions that died this game"
	index = "Battlecry~Legendary"
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.examDeads(self.ID, cond=lambda card: card.deathrattle is not None)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		whelp1, whelp2 = PlaguedHatchling(self.Game, self.ID), PlaguedHatchling(self.Game, self.ID)
		deathrattle1 = deathrattle2 = None
		if tups := self.Game.Counters.examDeads(self.ID, veri_sum_ls=2, cond=lambda card: card.deathrattle):
			deathrattle1, deathrattle2 = [numpyChoice(tups)[0].deathrattle, numpyChoice(tups)[0].deathrattle]
		self.summon((whelp1, whelp2), relative="<>")
		if deathrattle1:
			self.giveEnchant(whelp1, trig=deathrattle1, trigType="Deathrattle")
			self.giveEnchant(whelp2, trig=deathrattle2, trigType="Deathrattle")
		
	
class PlaguedHatchling(Minion):
	Class, race, name = "Neutral", "Dragon", "Plagued Hatchling"
	mana, attack, health = 1, 1, 1
	name_CN = "魔药龙崽"
	numTargets, Effects, description = 0, "", ""
	index = "Uncollectible"
	
	
class OnyxMagescribe(Minion):
	Class, race, name = "Neutral", "Dragon", "Onyx Magescribe"
	mana, attack, health = 6, 4, 9
	numTargets, Effects, description = 0, "", "Spellburst: Add 2 random spells from your class to your hand"
	name_CN = "黑岩法术抄写员"
	trigBoard = Trig_OnyxMagescribe
	
	
class SmugSenior(Minion):
	Class, race, name = "Neutral", "", "Smug Senior"
	mana, attack, health = 6, 5, 7
	numTargets, Effects, description = 0, "Taunt", "Taunt. Deathrattle: Add a 5/7 Ghost with Taunt to your hand"
	name_CN = "浮夸的大四学长"
	deathrattle = Death_SmugSenior
	
	
class SpectralSenior(Minion):
	Class, race, name = "Neutral", "", "Spectral Senior"
	mana, attack, health = 6, 5, 7
	name_CN = "鬼灵学长"
	numTargets, Effects, description = 0, "Taunt", "Taunt"
	index = "Uncollectible"
	
	
class SorcerousSubstitute(Minion):
	Class, race, name = "Neutral", "", "Sorcerous Substitute"
	mana, attack, health = 6, 6, 6
	name_CN = "巫术替身"
	numTargets, Effects, description = 0, "", "Battlecry: If you have Spell Damage, summon a copy of this"
	index = "Battlecry"
	def effCanTrig(self):
		self.effectViable = self.countSpellDamage() > 0
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if not self.dead and self.countSpellDamage() > 0: self.summon(self.copyCard(self, self.ID))
		
	
class KeymasterAlabaster(Minion):
	Class, race, name = "Neutral", "", "Keymaster Alabaster"
	mana, attack, health = 7, 6, 8
	name_CN = "钥匙专家阿拉巴斯特"
	numTargets, Effects, description = 0, "", "Whenever your opponent draws a card, add a copy to your hand that costs (1)"
	index = "Legendary"
	trigBoard = Trig_KeymasterAlabaster
	
	
class PlaguedProtodrake(Minion):
	Class, race, name = "Neutral", "Dragon", "Plagued Protodrake"
	mana, attack, health = 8, 8, 8
	numTargets, Effects, description = 0, "", "Deathrattle: Summon a random 7-Cost minion"
	name_CN = "魔药始祖龙"
	deathrattle = Death_PlaguedProtodrake
	
	
class DemonCompanion(Spell):
	Class, school, name = "Demon Hunter,Hunter", "", "Demon Companion"
	numTargets, mana, Effects = 0, 1, ""
	description = "Summon a random Demon Companion"
	name_CN = "恶魔伙伴"
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon(numpyChoice((Reffuh, Kolek, Shima))(self.Game, self.ID))
		
	
class Reffuh(Minion):
	Class, race, name = "Demon Hunter,Hunter", "Demon", "Reffuh"
	mana, attack, health = 1, 2, 1
	name_CN = "弗霍"
	numTargets, Effects, description = 0, "Charge", "Charge"
	index = "Uncollectible"
	
	
class Kolek(Minion):
	Class, race, name = "Demon Hunter,Hunter", "Demon", "Kolek"
	mana, attack, health = 1, 1, 2
	name_CN = "克欧雷"
	numTargets, Effects, description = 0, "", "Your other minions have +1 Attack"
	index = "Uncollectible"
	aura = Aura_Kolek
	
	
class Shima(Minion):
	Class, race, name = "Demon Hunter,Hunter", "Demon", "Shima"
	mana, attack, health = 1, 2, 2
	name_CN = "莎米"
	numTargets, Effects, description = 0, "Taunt", "Taunt"
	index = "Uncollectible"
	
	
class DoubleJump(Spell):
	Class, school, name = "Demon Hunter", "", "Double Jump"
	numTargets, mana, Effects = 0, 1, ""
	description = "Draw an Outcast card from your deck"
	name_CN = "二段跳"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.drawCertainCard(lambda card: "~Outcast" in card.index)
		
	
class TrueaimCrescent(Weapon):
	Class, name, description = "Demon Hunter,Hunter", "Trueaim Crescent", "After your hero attacks a minion, your minions attack it too"
	mana, attack, durability, Effects = 1, 1, 4, ""
	name_CN = "引月长弓"
	trigBoard = Trig_TrueaimCrescent
	
	
class AceHunterKreen(Minion):
	Class, race, name = "Demon Hunter,Hunter", "", "Ace Hunter Kreen"
	mana, attack, health = 3, 2, 4
	name_CN = "金牌猎手克里"
	numTargets, Effects, description = 0, "", "Your other characters are Immune while attacking"
	index = "Legendary"
	trigBoard = Trig_AceHunterKreen
	
	
class Magehunter(Minion):
	Class, race, name = "Demon Hunter", "", "Magehunter"
	mana, attack, health = 3, 2, 3
	numTargets, Effects, description = 0, "Rush", "Rush. Whenever this attacks a minion, Silence it"
	name_CN = "法师猎手"
	trigBoard = Trig_Magehunter
	
	
class ShardshatterMystic(Minion):
	Class, race, name = "Demon Hunter", "", "Shardshatter Mystic"
	mana, attack, health = 4, 3, 2
	name_CN = "残片震爆秘术师"
	numTargets, Effects, description = 0, "", "Battlecry: Destroy a Soul Fragment in your deck to deal 3 damage to all other minions"
	index = "Battlecry"
	def effCanTrig(self):
		self.effectViable = any(isinstance(card, SoulFragment) for card in self.Game.Hand_Deck.decks[self.ID])
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if SoulFragment.destroyOne(self.Game, self.ID):
			self.dealsDamage(self.Game.minionsonBoard(exclude=self), 3)
		
	
class Glide(Spell):
	Class, school, name = "Demon Hunter", "", "Glide"
	numTargets, mana, Effects = 0, 4, ""
	description = "Shuffle your hand into your deck. Draw 4 cards. Outcast: Your opponent does the same"
	name_CN = "滑翔"
	index = "Outcast"
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.outcastcanTrig(self)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.Game.Hand_Deck.shuffle_Hand2Deck(0, self.ID, initiatorID=self.ID, getAll=True)
		for _ in (0, 1, 2, 3): self.Game.Hand_Deck.drawCard(self.ID)
		if posinHand in (-1, 0):
			self.Game.Hand_Deck.shuffle_Hand2Deck(0, 3 - self.ID, initiatorID=self.ID, getAll=True)
			for _ in (0, 1, 2, 3): self.Game.Hand_Deck.drawCard(3-self.ID)
		
	
class Marrowslicer(Weapon):
	Class, name, description = "Demon Hunter", "Marrowslicer", "Battlecry: Shuffle 2 Soul Fragments into your deck"
	mana, attack, durability, Effects = 4, 4, 2, ""
	name_CN = "切髓之刃"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.shuffleintoDeck([SoulFragment(self.Game, self.ID) for _ in (0, 1)])
		
	
class SoulFragment(Spell):
	Class, school, name = "Warlock,Demon Hunter", "", "Soul Fragment"
	numTargets, mana, Effects = 0, 0, ""
	name_CN = "灵魂残片"
	description = "Restore 2 Health to your hero"
	index = "Uncollectible"
	@classmethod
	def destroyOne(cls, game, ID):
		# Assuming always destroy the Soul Fragment near the bottom of the deck
		for i, card in enumerate(game.Hand_Deck.decks[ID]):
			if isinstance(card, SoulFragment):
				game.Hand_Deck.extractfromDeck(i, ID)
				return True
		return False
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.heals(self.Game.heroes[self.ID], self.calcHeal(2))
		
	
class StarStudentStelina(Minion):
	Class, race, name = "Demon Hunter", "", "Star Student Stelina"
	mana, attack, health = 4, 4, 3
	name_CN = "明星学员斯特里娜"
	numTargets, Effects, description = 0, "", "Outcast: Look at 3 cards in your opponent's hand. Shuffle one of them into their deck"
	index = "Outcast~Legendary"
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.outcastcanTrig(self)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if posinHand in (-1, 0):
			_, i = self.discoverfrom('', ls=self.Game.Hand_Deck.hands[3 - self.ID])
			self.Game.Hand_Deck.shuffle_Hand2Deck(i, 3-self.ID, initiatorID=self.ID, getAll=False)
		
	
class VilefiendTrainer(Minion):
	Class, race, name = "Demon Hunter", "", "Vilefiend Trainer"
	mana, attack, health = 4, 5, 4
	numTargets, Effects, description = 0, "", "Outcast: Summon two 1/1 Demons"
	name_CN = "邪犬训练师"
	index = "Outcast"
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.outcastcanTrig(self)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if posinHand in (-1, 0):
			self.summon([SnarlingVilefiend(self.Game, self.ID) for _ in (0, 1)], relative="<>")
		
	
class SnarlingVilefiend(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Snarling Vilefiend"
	mana, attack, health = 1, 1, 1
	name_CN = "咆哮的邪犬"
	numTargets, Effects, description = 0, "", ""
	index = "Uncollectible"
	
	
class BloodHerald(Minion):
	Class, race, name = "Demon Hunter,Hunter", "", "Blood Herald"
	mana, attack, health = 5, 1, 1
	numTargets, Effects, description = 0, "", "Whenever a friendly minion dies while this is in your hand, gain +1/+1"
	trigHand = Trig_BloodHerald
	name_CN = "嗜血传令官"
	
	
class SoulshardLapidary(Minion):
	Class, race, name = "Demon Hunter", "", "Soulshard Lapidary"
	mana, attack, health = 5, 5, 5
	name_CN = "铸魂宝石匠"
	numTargets, Effects, description = 0, "", "Battlecry: Destroy a Soul Fragment in your deck to give your hero +5 Attack this turn"
	index = "Battlecry"
	def effCanTrig(self):
		self.effectViable = any(isinstance(card, SoulFragment) for card in self.Game.Hand_Deck.decks[self.ID])
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if SoulFragment.destroyOne(self.Game, self.ID):
			self.giveHeroAttackArmor(self.ID, attGain=5, source=SoulshardLapidary)
		
	
class CycleofHatred(Spell):
	Class, school, name = "Demon Hunter", "", "Cycle of Hatred"
	numTargets, mana, Effects = 0, 7, ""
	description = "Deal 3 damage to all minions. Summon a 3/3 Spirit for every minion killed"
	name_CN = "仇恨之轮"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if num := sum(obj.dead or obj.health < 1 for obj in self.dealsDamage(self.Game.minionsonBoard(), self.calcDamage(3))[0]):
			self.summon([SpiritofVengeance(self.Game, self.ID) for _ in range(num)])
		
	
class SpiritofVengeance(Minion):
	Class, race, name = "Demon Hunter", "", "Spirit of Vengeance"
	mana, attack, health = 3, 3, 3
	name_CN = "复仇之魂"
	numTargets, Effects, description = 0, "", ""
	index = "Uncollectible"
	
	
class FelGuardians(Spell):
	Class, school, name = "Demon Hunter", "Fel", "Fel Guardians"
	numTargets, mana, Effects = 0, 7, ""
	description = "Summon three 1/2 Demons with Taunt. Costs (1) less whenever a friendly minion dies"
	trigHand = Trig_FelGuardians
	name_CN = "邪能护卫"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon([SoulfedFelhound(self.Game, self.ID) for _ in (0, 1, 2)])
		
	
class SoulfedFelhound(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Soulfed Felhound"
	mana, attack, health = 1, 1, 2
	name_CN = "食魂地狱犬"
	numTargets, Effects, description = 0, "Taunt", "Taunt"
	index = "Uncollectible"
	
	
class AncientVoidHound(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Ancient Void Hound"
	mana, attack, health = 9, 10, 10
	numTargets, Effects, description = 0, "", "At the end of your turn, steal 1 Attack and Health from all enemy minions"
	name_CN = "上古虚空恶犬"
	trigBoard = Trig_AncientVoidHound
	
	
class LightningBloom(Spell):
	Class, school, name = "Druid,Shaman", "Nature", "Lightning Bloom"
	numTargets, mana, Effects = 0, 0, ""
	description = "Gain 2 Mana Crystals this turn only. Overload: (2)"
	name_CN = "雷霆绽放"
	overload = 2
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.Game.Manas.gainTempManaCrystal(2, ID=self.ID)
		
	
class Gibberling(Minion):
	Class, race, name = "Druid", "", "Gibberling"
	mana, attack, health = 2, 1, 1
	numTargets, Effects, description = 0, "", "Spellburst: Summon a Gibberling"
	name_CN = "聒噪怪"
	trigBoard = Trig_Gibberling
	
	
class NatureStudies(Spell):
	Class, school, name = "Druid", "Nature", "Nature Studies"
	numTargets, mana, Effects = 0, 1, ""
	description = "Discover a spell. Your next one costs (1) less"
	name_CN = "自然研习"
	trigEffect = GameManaAura_NatureStudies
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.discoverNew(comment, lambda : self.rngPool(class4Discover(self) + " Spells"))
		GameManaAura_NatureStudies(self.Game, self.ID).auraAppears()
		
	
class PartnerAssignment(Spell):
	Class, school, name = "Druid", "", "Partner Assignment"
	numTargets, mana, Effects = 0, 1, ""
	description = "Add a random 2-Cost and 3-Cost Beast to your hand"
	name_CN = "分配组员"
	poolIdentifier = "2-Cost Beasts"
	@classmethod
	def generatePool(cls, pools):
		return ["2-Cost Beasts", "3-Cost Beasts"], \
				[[card for card in pools.MinionswithRace["Beast"] if card.mana == 2],
					[card for card in pools.MinionswithRace["Beast"] if card.mana == 3]]
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		beasts = [numpyChoice(self.rngPool("2-Cost Beasts")), numpyChoice(self.rngPool("3-Cost Beasts"))]
		self.addCardtoHand(beasts, self.ID)
		
	
class SpeakerGidra(Minion):
	Class, race, name = "Druid", "", "Speaker Gidra"
	mana, attack, health = 3, 1, 4
	name_CN = "演讲者吉德拉"
	numTargets, Effects, description = 0, "Rush,Windfury", "Rush, Windfury. Spellburst: Gain Attack and Health equal to the spell's Cost"
	index = "Legendary"
	trigBoard = Trig_SpeakerGidra		
	
	
class Groundskeeper(Minion):
	Class, race, name = "Druid,Shaman", "", "Groundskeeper"
	mana, attack, health = 4, 4, 5
	name_CN = "园地管理员"
	numTargets, Effects, description = 1, "Taunt", "Taunt. Battlecry: If you're holding a spell that costs (5) or more, restore 5 Health"
	index = "Battlecry"
	def numTargetsNeeded(self, choice=0):
		return 1 if self.Game.Hand_Deck.holdingBigSpell(self.ID) else 0
		
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.holdingBigSpell(self.ID)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.Game.Hand_Deck.holdingBigSpell(self.ID): self.heals(target, self.calcHeal(5))
		
	
class TwilightRunner(Minion):
	Class, race, name = "Druid", "Beast", "Twilight Runner"
	mana, attack, health = 5, 5, 4
	numTargets, Effects, description = 0, "Stealth", "Stealth. Whenever this attacks, draw 2 cards"
	name_CN = "夜行虎"
	trigBoard = Trig_TwilightRunner		
	
	
class ForestWardenOmu(Minion):
	Class, race, name = "Druid", "", "Forest Warden Omu"
	mana, attack, health = 6, 5, 4
	name_CN = "林地守护者欧穆"
	numTargets, Effects, description = 0, "", "Spellburst: Refresh your Mana Crystals"
	index = "Legendary"
	trigBoard = Trig_ForestWardenOmu		
	
	
class CalltoAid(Spell):
	Class, school, name = "Druid,Shaman", "Nature", "Call to Aid"
	numTargets, mana, Effects = 0, 6, ""
	name_CN = "呼叫增援"
	description = "Summon four 2/2 Treant Totems"
	index = "Uncollectible"
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		game, ID = self.Game, self.ID
		self.summon([TreantTotem(game, ID) for _ in (0, 1, 2, 3)])
		
	
class AlarmtheForest(Spell):
	Class, school, name = "Druid,Shaman", "Nature", "Alarm the Forest"
	numTargets, mana, Effects = 0, 6, ""
	name_CN = "警醒森林"
	description = "Summon four 2/2 Treant Totems with Rush. Overload: (2)"
	index = "Uncollectible"
	overload = 2
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		game, ID = self.Game, self.ID
		self.summon(minions := [TreantTotem(game, ID) for i in (0, 1, 2, 3)])
		self.giveEnchant([minion for minion in minions if minion.onBoard], effGain="Rush", source=AlarmtheForest)
		
	
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
	numTargets, mana, Effects = 0, 6, ""
	name_CN = "雕琢符文"
	description = "Choose One - Summon four 2/2 Treant Totems; or Overload: (2) to given them Rush"
	options = (CalltoAid_Option, AlarmtheForest_Option)
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		game, ID = self.Game, self.ID
		self.summon(minions := [TreantTotem(game, ID) for _ in (0, 1, 2, 3)])
		if choice:
			self.Game.Manas.overloadMana(2, self.ID)
			self.giveEnchant([minion for minion in minions if minion.onBoard], effGain="Rush", source=AlarmtheForest)
		
	
class TreantTotem(Minion):
	Class, race, name = "Druid,Shaman", "Totem", "Treant Totem"
	mana, attack, health = 2, 2, 2
	name_CN = "树人图腾"
	numTargets, Effects, description = 0, "", ""
	index = "Uncollectible"
	
	
class SurvivaloftheFittest(Spell):
	Class, school, name = "Druid", "", "Survival of the Fittest"
	numTargets, mana, Effects = 0, 10, ""
	description = "Give +4/+4 to all minions in your hand, deck, and battlefield"
	name_CN = "优胜劣汰"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant([card for card in self.Game.Hand_Deck.hands[self.ID] if card.category == "Minion"], 
						4, 4, source=SurvivaloftheFittest, add2EventinGUI=False)
		typeSelf = type(self)
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if card.category == "Minion": card.getsBuffDebuff_inDeck(4, 4, source=SurvivaloftheFittest)
		self.giveEnchant(self.Game.minionsonBoard(self.ID), 4, 4, source=SurvivaloftheFittest)
		
	
class AdorableInfestation(Spell):
	Class, school, name = "Hunter,Druid", "", "Adorable Infestation"
	numTargets, mana, Effects = 1, 1, ""
	description = "Give a minion +1/+1. Summon a 1/1 Cub. Add a Cub to your hand"
	name_CN = "萌物来袭"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(target, 1, 1, source=AdorableInfestation)
		self.summon(MarsuulCub(self.Game, self.ID))
		self.addCardtoHand(MarsuulCub, self.ID)
		
	
class MarsuulCub(Minion):
	Class, race, name = "Hunter,Druid", "Beast", "Marsuul Cub"
	mana, attack, health = 1, 1, 1
	name_CN = "魔鼠宝宝"
	numTargets, Effects, description = 0, "", ""
	index = "Uncollectible"
	
	
class CarrionStudies(Spell):
	Class, school, name = "Hunter", "", "Carrion Studies"
	numTargets, mana, Effects = 0, 1, ""
	description = "Discover a Deathrattle minion. Your next one costs (1) less"
	name_CN = "腐食研习"
	trigEffect = GameManaAura_CarrionStudies
	poolIdentifier = "Deathrattle Minions as Hunter"
	@classmethod
	def generatePool(cls, pools):
		return genPool_CertainMinionsasClass(pools, "Deathrattle", cond=lambda card: card.deathrattle)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.discoverNew(comment, lambda : self.rngPool("Deathrattle Minions as " + class4Discover(self)))
		GameManaAura_CarrionStudies(self.Game, self.ID).auraAppears()
		
	
class Overwhelm(Spell):
	Class, school, name = "Hunter", "", "Overwhelm"
	numTargets, mana, Effects = 1, 1, ""
	description = "Deal 2 damage to a minion. Deal one more damage for each Beast you control"
	name_CN = "数量压制"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def text(self): return self.calcDamage(2+len(self.Game.minionsonBoard(self.ID, race="Beast")))
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(target, self.calcDamage(2+len(self.Game.minionsonBoard(self.ID, race="Beast"))))
		
	
class Wolpertinger(Minion):
	Class, race, name = "Hunter", "Beast", "Wolpertinger"
	mana, attack, health = 1, 1, 1
	name_CN = "鹿角小飞兔"
	numTargets, Effects, description = 0, "", "Battlecry: Summon a copy of this"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if not self.dead: self.summon(self.copyCard(self, self.ID))
		
	
class BloatedPython(Minion):
	Class, race, name = "Hunter", "Beast", "Bloated Python"
	mana, attack, health = 3, 1, 2
	numTargets, Effects, description = 0, "", "Deathrattle: Summon a 4/4 Hapless Handler"
	name_CN = "饱腹巨蟒"
	deathrattle = Death_BloatedPython
	
	
class HaplessHandler(Minion):
	Class, race, name = "Hunter", "", "Hapless Handler"
	mana, attack, health = 4, 4, 4
	name_CN = "倒霉的管理员"
	numTargets, Effects, description = 0, "", ""
	index = "Uncollectible"
	
	
class ProfessorSlate(Minion):
	Class, race, name = "Hunter", "", "Professor Slate"
	mana, attack, health = 3, 3, 4
	name_CN = "斯雷特教授"
	numTargets, Effects, description = 0, "", "Your spells are Poisonous"
	index = "Legendary"
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
	name_CN = "大导师野爪"
	numTargets, Effects, description = 1, "", "Choose One- Give Beasts in your deck +1/+1; or Transform into a copy of a friendly Beast"
	index = "Legendary"
	options = (RiletheHerd_Option, Transfiguration_Option)
	def numTargetsNeeded(self, choice=0):
		return 1 if choice else 0
		
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists(self.ID)
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and "Beast" in obj.race and obj.ID == self.ID and obj is not self and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		#对于抉择随从而言，应以与战吼类似的方式处理，打出时抉择可以保持到最终结算。但是打出时，如果因为鹿盔和发掘潜力而没有选择抉择，视为到对方场上之后仍然可以而没有如果没有
		if choice < 1:
			typeSelf = type(self)
			for card in self.Game.Hand_Deck.decks[self.ID]:
				if "Beast" in card.race: card.getsBuffDebuff_inDeck(1, 1, source=ShandoWildclaw)
		if choice and target[0] and not self.dead and self.Game.cardinPlay is self:
			self.transform(self, self.copyCard(target[0], self.ID))
		
	
class KroluskBarkstripper(Minion):
	Class, race, name = "Hunter", "Beast", "Krolusk Barkstripper"
	mana, attack, health = 4, 3, 5
	numTargets, Effects, description = 0, "", "Spellburst: Destroy a random enemy minion"
	name_CN = "裂树三叶虫"
	trigBoard = Trig_KroluskBarkstripper
	
	
class TeachersPet(Minion):
	Class, race, name = "Hunter,Druid", "Beast", "Teacher's Pet"
	mana, attack, health = 5, 4, 5
	numTargets, Effects, description = 0, "Taunt", "Taunt. Deathrattle: Summon a 3-Cost Beast"
	name_CN = "教师的爱宠"
	deathrattle = Death_TeachersPet
	poolIdentifier = "3-Cost Beasts to Summon"
	@classmethod
	def generatePool(cls, pools):
		return "3-Cost Beasts to Summon", [card for card in pools.MinionswithRace["Beast"] if card.mana == 3]
		
	
class GuardianAnimals(Spell):
	Class, school, name = "Hunter,Druid", "", "Guardian Animals"
	numTargets, mana, Effects = 0, 8, ""
	description = "Summon two Beasts that cost (5) or less from your deck. Give them Rush"
	name_CN = "动物保镖"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for _ in (0, 1):
			if beast := self.try_SummonfromOwn(cond=lambda card: "Beast" in card.race and card.mana < 6):
				self.giveEnchant(beast, effGain="Rush", source=GuardianAnimals)
			else: break
		
	
class BrainFreeze(Spell):
	Class, school, name = "Mage,Rogue", "Frost", "Brain Freeze"
	numTargets, mana, Effects = 1, 1, ""
	name_CN = "冰冷智慧"
	description = "Freeze a minion. Combo: Also deal 3 damage to it"
	index = "Combo"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.comboCounters[self.ID] > 0
		
	def text(self): return self.calcDamage(3)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		combo, damage = self.Game.Counters.comboCounters[self.ID], self.calcDamage(3)
		for obj in target:
			self.freeze(obj)
			if combo: self.dealsDamage(obj, damage)
		
	
class DevolvingMissiles(Spell):
	Class, school, name = "Shaman,Mage", "Arcane", "Devolving Missiles"
	numTargets, mana, Effects = 0, 1, ""
	description = "Shoot three missiles at random enemy minions that transform them into ones that cost (1) less"
	name_CN = "衰变飞弹"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		side, game = 3 - self.ID, self.Game
		for _ in (0, 1, 2):
			if minions := game.minionsonBoard(side):
				self.transform(minion := numpyChoice(minions), self.newEvolved(minion.mana_0, by=-1, ID=side))
			else: break
		
	
class LabPartner(Minion):
	Class, race, name = "Mage", "", "Lab Partner"
	mana, attack, health = 1, 1, 3
	numTargets, Effects, description = 0, "Spell Damage", "Spell Damage +1"
	name_CN = "研究伙伴"
	
	
class WandThief(Minion):
	Class, race, name = "Mage,Rogue", "", "Wand Thief"
	mana, attack, health = 1, 1, 2
	name_CN = "魔杖窃贼"
	numTargets, Effects, description = 0, "", "Combo: Discover a Mage spell"
	index = "Combo"
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.comboCounters[self.ID] > 0
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.Game.Counters.comboCounters[self.ID] > 0:
			self.discoverNew('', lambda : self.rngPool("Mage Spells"))
		
	
class CramSession(Spell):
	Class, school, name = "Mage", "Arcane", "Cram Session"
	numTargets, mana, Effects = 0, 2, ""
	description = "Draw 1 card (improved by Spell Damage)"
	name_CN = "考前刷夜"
	def text(self): return 1 + self.countSpellDamage()
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for _ in range(1 + self.countSpellDamage()): self.Game.Hand_Deck.drawCard(self.ID)
		
	
class Combustion(Spell):
	Class, school, name = "Mage", "Fire", "Combustion"
	numTargets, mana, Effects = 1, 3, ""
	description = "Deal 4 damage to a minion. Any excess damages both neighbors"
	name_CN = "燃烧"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		damage = self.calcDamage(4)
		for obj in target:
			dmgExcess = damage - (dmgReal := min(damage, max(obj.health, 0)))
			if dmgExcess and (neighbors := self.Game.neighbors2(obj)[0]):
				self.dealsDamage([obj]+neighbors, [dmgReal]+[dmgExcess]*len(neighbors))
			elif dmgReal: self.dealsDamage(obj, dmgReal)
		
	
class Firebrand(Minion):
	Class, race, name = "Mage", "", "Firebrand"
	mana, attack, health = 3, 3, 4
	numTargets, Effects, description = 0, "", "Spellburst: Deal 4 damage randomly split among all enemy minions"
	name_CN = "火印火妖"
	trigBoard = Trig_Firebrand
	
	
class PotionofIllusion(Spell):
	Class, school, name = "Mage,Rogue", "Arcane", "Potion of Illusion"
	numTargets, mana, Effects = 0, 4, ""
	description = "Add 1/1 copies of your minions to your hand. They cost (1)"
	name_CN = "幻觉药水"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.addCardtoHand([self.copyCard(minion, self.ID, 1, 1, 1, bareCopy=True) for minion in self.Game.minionsonBoard(self.ID)], self.ID)
		
	
class JandiceBarov(Minion):
	Class, race, name = "Mage,Rogue", "", "Jandice Barov"
	mana, attack, health = 6, 2, 1
	name_CN = "詹迪斯·巴罗夫"
	numTargets, Effects, description = 0, "", "Battlecry: Summon two random 5-Cost minions. Secretly pick one that dies when it takes damage"
	index = "Battlecry~Legendary"
	trigEffect = Trig_JandiceBarov
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		minion1, minion2 = [minion(self.Game, self.ID) for minion in numpyChoice(self.rngPool("5-Cost Minions to Summon"), 2, replace=False)]
		self.summon([minion1, minion2], relative="<>")
		if minion1.onBoard and minion2.onBoard:
			minion = self.chooseFixedOptions(comment, options=[minion1, minion2])
			minion.getsTrig(Trig_JandiceBarov(minion))
		
	
class MozakiMasterDuelist(Minion):
	Class, race, name = "Mage", "", "Mozaki, Master Duelist"
	mana, attack, health = 5, 3, 8
	name_CN = "决斗大师 莫扎奇"
	numTargets, Effects, description = 0, "", "After you cast a spell, gain Spell Damage +1"
	index = "Legendary"
	trigBoard = Trig_MozakiMasterDuelist
	def text(self): return '' if self.silenced else self.effects["Spell Damage"]
		
	
class WyrmWeaver(Minion):
	Class, race, name = "Mage", "", "Wyrm Weaver"
	mana, attack, health = 4, 3, 5
	numTargets, Effects, description = 0, "", "Spellburst: Summon two 1/2 Mana Wyrms"
	name_CN = "浮龙培养师"
	trigBoard = Trig_WyrmWeaver
	
	
class FirstDayofSchool(Spell):
	Class, school, name = "Paladin", "", "First Day of School"
	numTargets, mana, Effects = 0, 1, ""
	description = "Add 2 random 1-Cost minions to your hand"
	name_CN = "新生入学"
	poolIdentifier = "1-Cost Minions"
	@classmethod
	def generatePool(cls, pools):
		return "1-Cost Minions", pools.MinionsofCost[1]
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.addCardtoHand(numpyChoice(self.rngPool("1-Cost Minions"), 2, replace=False), self.ID)
		
	
class WaveofApathy(Spell):
	Class, school, name = "Paladin,Priest", "", "Wave of Apathy"
	numTargets, mana, Effects = 0, 1, ""
	description = "Set the Attack of all enemy minions to 1 until your next turn"
	name_CN = "倦怠光波"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.setStat_Enchant(self.Game.minionsonBoard(3-self.ID), enchant=Enchantment(WaveofApathy, attSet=1, until=self.ID))
		
	
class ArgentBraggart(Minion):
	Class, race, name = "Paladin", "", "Argent Braggart"
	mana, attack, health = 2, 1, 1
	name_CN = "银色自大狂"
	numTargets, Effects, description = 0, "", "Battlecry: Gain Attack and Health to match the highest in the battlefield"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if not self.dead:
			minions = self.Game.minionsonBoard()
			highestAtt, highestHealth = max(minion.attack for minion in minions), max(minion.health for minion in minions)
			attChange, healthChange = highestAtt - self.attack, highestHealth - self.health
			if attChange or healthChange: self.giveEnchant(self, attChange, healthChange, source=ArgentBraggart)
		
	
class GiftofLuminance(Spell):
	Class, school, name = "Paladin,Priest", "Holy", "Gift of Luminance"
	numTargets, mana, Effects = 1, 3, ""
	description = "Give a minion Divine Shield, then summon a 1/1 copy of it"
	name_CN = "流光之赐"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for obj in target:
			self.giveEnchant(obj, effGain="Divine Shield", source=GiftofLuminance)
			self.summon(self.copyCard(obj, self.ID, 1, 1), position=obj.pos+1)
		
	
class GoodyTwoShields(Minion):
	Class, race, name = "Paladin", "", "Goody Two-Shields"
	mana, attack, health = 3, 4, 2
	numTargets, Effects, description = 0, "Divine Shield", "Spellburst: Gain Divine Shield"
	name_CN = "双盾优等生"
	trigBoard = Trig_GoodyTwoShields
	
	
class HighAbbessAlura(Minion):
	Class, race, name = "Paladin,Priest", "", "High Abbess Alura"
	mana, attack, health = 5, 3, 6
	name_CN = "高阶修士奥露拉"
	numTargets, Effects, description = 0, "", "Spellburst: Cast a spell from your deck (targets this if possible)"
	index = "Legendary"
	trigBoard = Trig_HighAbbessAlura
	
	
class BlessingofAuthority(Spell):
	Class, school, name = "Paladin", "Holy", "Blessing of Authority"
	numTargets, mana, Effects = 1, 5, ""
	description = "Give a minion +8/+8. It can't attack heroes this turn"
	name_CN = "威能祝福"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(target, 8, 8, effGain="Can't Attack Hero", source=BlessingofAuthority)
		
	
class DevoutPupil(Minion):
	Class, race, name = "Paladin,Priest", "", "Devout Pupil"
	mana, attack, health = 6, 4, 5
	numTargets, Effects, description = 0, "Divine Shield,Taunt", "Divine Shield,Taunt. Costs (1) less for each spell you've cast on friendly characters this game"
	name_CN = "虔诚的学徒"
	trigHand = Trig_DevoutPupil
	def selfManaChange(self):
		self.mana -= len(list(self.Game.Counters.iter_SpellsonFriendly(self.ID)))
		
	
class JudiciousJunior(Minion):
	Class, race, name = "Paladin", "", "Judicious Junior"
	mana, attack, health = 6, 4, 9
	numTargets, Effects, description = 0, "Lifesteal", "Lifesteal"
	name_CN = "踏实的大三学姐"
	
	
class TuralyontheTenured(Minion):
	Class, race, name = "Paladin", "", "Turalyon, the Tenured"
	mana, attack, health = 8, 3, 12
	name_CN = "终身教授图拉扬"
	numTargets, Effects, description = 0, "Rush", "Rush. Whenever this attacks a minion, set the defender's Attack and Health to 3"
	index = "Legendary"
	trigBoard = Trig_TuralyontheTenured
	
	
class RaiseDead(Spell):
	Class, school, name = "Priest,Warlock", "Shadow", "Raise Dead"
	numTargets, mana, Effects = 0, 0, ""
	description = "Deal 3 damage to your hero. Return two friendly minions that died this game to your hand"
	name_CN = "亡者复生"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(self.Game.heroes[self.ID], self.calcDamage(3))
		if tups := self.Game.Counters.examDeads(self.ID, veri_sum_ls=2):
			tups = numpyChoice(tups, min(2, len(tups)), replace=False)
			self.addCardtoHand([self.Game.fabCard(tup[:2], self.ID, self) for tup in tups], self.ID)
		
	
class DraconicStudies(Spell):
	Class, school, name = "Priest", "", "Draconic Studies"
	numTargets, mana, Effects = 0, 1, ""
	description = "Discover a Dragon. Your next one costs (1) less"
	name_CN = "龙族研习"
	trigEffect = GameManaAura_DraconicStudies
	poolIdentifier = "Dragons as Priest"
	@classmethod
	def generatePool(cls, pools):
		return genPool_MinionsofRaceasClass(pools, "Dragon")
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.discoverNew(comment, lambda : self.rngPool("Dragons as " + class4Discover(self)))
		GameManaAura_DraconicStudies(self.Game, self.ID).auraAppears()
		
	
class FrazzledFreshman(Minion):
	Class, race, name = "Priest", "", "Frazzled Freshman"
	mana, attack, health = 1, 1, 4
	numTargets, Effects, description = 0, "", ""
	name_CN = "疲倦的大一新生"
	
	
class MindrenderIllucia(Minion):
	Class, race, name = "Priest", "", "Mindrender Illucia"
	mana, attack, health = 3, 1, 3
	name_CN = "裂心者伊露希亚"
	numTargets, Effects, description = 0, "", "Battlecry: Swap hands and decks with your opponent until your next turn"
	index = "Battlecry~Legendary"
	trigEffect = MindrenderIllucia_Effect
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if enemyHand := self.Game.Hand_Deck.hands[3 - self.ID]:
			hand_Orig = self.Game.Hand_Deck.extractfromHand(None, self.ID, getAll=True)[0]
			self.addCardtoHand([self.copyCard(card, self.ID) for card in enemyHand], self.ID)
			MindrenderIllucia_Effect(self.Game, self.ID, hand_Orig).connect()
		
	
class PowerWordFeast(Spell):
	Class, school, name = "Priest", "", "Power Word: Feast"
	numTargets, mana, Effects = 1, 2, ""
	description = "Give a minion +2/+2. Restore it to full health at the end of this turn"
	name_CN = "真言术：宴"
	trigEffect = Trig_PowerWordFeast
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(target, 2, 2, source=PowerWordFeast, trig=Trig_PowerWordFeast)
		
	
class BrittleboneDestroyer(Minion):
	Class, race, name = "Priest,Warlock", "", "Brittlebone Destroyer"
	mana, attack, health = 4, 3, 3
	name_CN = "脆骨破坏者"
	numTargets, Effects, description = 1, "", "Battlecry: If your hero's Health changed this turn, destroy a minion"
	index = "Battlecry"
	def numTargetsNeeded(self, choice=0):
		return 1 if any(tup[0] == "HeroHealthChange" and tup[1] == self.ID for tup in self.Game.Counters.events[-1]) else 0
		
	def effCanTrig(self):
		self.effectViable = any(tup[0] == "HeroHealthChange" and tup[1] == self.ID for tup in self.Game.Counters.events[-1])
		
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj is not self and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if any(tup[0] == "HeroHealthChange" and tup[1] == self.ID for tup in self.Game.Counters.events[-1]):
			self.Game.kill(self, target)
		
	
class CabalAcolyte(Minion):
	Class, race, name = "Priest", "", "Cabal Acolyte"
	mana, attack, health = 4, 2, 4
	numTargets, Effects, description = 0, "Taunt", "Taunt. Spellburst: Gain control of a random enemy minion with 2 or less Attack"
	name_CN = "秘教侍僧"
	trigBoard = Trig_CabalAcolyte
	
	
class DisciplinarianGandling(Minion):
	Class, race, name = "Priest,Warlock", "", "Disciplinarian Gandling"
	mana, attack, health = 4, 3, 6
	name_CN = "教导主任加丁"
	numTargets, Effects, description = 0, "", "After you play a minion, destroy it and summon a 4/4 Failed Student"
	index = "Legendary"
	trigBoard = Trig_DisciplinarianGandling
	
	
class FailedStudent(Minion):
	Class, race, name = "Priest,Warlock", "", "Failed Student"
	mana, attack, health = 4, 4, 4
	name_CN = "挂掉的学生"
	numTargets, Effects, description = 0, "", ""
	index = "Uncollectible"
	
	
class Initiation(Spell):
	Class, school, name = "Priest", "Shadow", "Initiation"
	numTargets, mana, Effects = 1, 6, ""
	description = "Deal 4 damage to a minion. If that kills it, summons a new copy"
	name_CN = "通窍"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def text(self): return self.calcDamage(4)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		damage = self.calcDamage(4)
		for obj in target:
			self.dealsDamage(obj, damage)
			if obj.health < 1 or obj.dead: self.summon(self.copyCard(obj, self.ID, bareCopy=True))
		
	
class FleshGiant(Minion):
	Class, race, name = "Priest,Warlock", "", "Flesh Giant"
	mana, attack, health = 10, 8, 8
	numTargets, Effects, description = 0, "", "Costs (1) less for each time your Hero's Health changed during your turn"
	name_CN = "血肉巨人"
	trigHand = Trig_FleshGiant
	def selfManaChange(self):
		self.mana -= sum(tup[0] == "HeroHealthChange" and tup[1] == self.ID for tup in self.Game.Counters.iter_TupsSoFar("events"))
		
	
class SecretPassage(Spell):
	Class, school, name = "Rogue", "", "Secret Passage"
	numTargets, mana, Effects = 0, 1, ""
	description = "Replace your hand with 4 cards from your deck. Swap back next turn"
	name_CN = "秘密通道"
	trigEffect = SecretPassage_Effect
	@classmethod
	def panda_CardsLeaveHand(cls, game, GUI, cards):
		if not cards: return  #If no cards removed from hand, nothing happens
		para = GUI.PARALLEL()
		for i, card in zip(range(len(cards)), reversed(cards)):
			btn, nodepath = card.btn, card.btn.np
			x, y, z = nodepath.getPos()
			para.append(GUI.SEQUENCE(GUI.WAIT(0.4*i), GUI.LERP_PosHpr(nodepath, duration=0.4, pos=(x, 1.5, 2.5), hpr=(0, 0, 0)),
									GUI.WAIT(0.2), GUI.LERP_Pos(nodepath, duration=0.3, pos=(30, 1.5, z)))
						)
		GUI.seqHolder[-1].append(para)
		
	@classmethod
	def panda_BackfromPassage(cls, game, GUI, cards, poses, hprs):
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
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		game, ID = self.Game, self.ID
		deckSize = len(deck := game.Hand_Deck.decks[ID])
		(indices := list(numpyChoice(range(deckSize), min(deckSize, 4), replace=False))).sort() #Smallest index becomes first element
		if indices:
			fromHand = game.Hand_Deck.extractfromHand(None, ID, getAll=True, enemyCanSee=False, animate=False)[0]
			fromDeck = [game.Hand_Deck.extractfromDeck(i, ID, enemyCanSee=False, animate=False) for i in reversed(indices)]
			if game.GUI:
				SecretPassage.panda_CardsLeaveHand(game, game.GUI, fromHand)
				game.GUI.deckZones[ID].draw(len(game.Hand_Deck.decks[ID]), len(game.Hand_Deck.hands[ID]))
			SecretPassage_Effect(game, ID, (fromHand, fromDeck)).connect()
			game.Hand_Deck.addCardtoHand(fromDeck, ID)
		
	
class Plagiarize(Secret):
	Class, school, name = "Rogue", "", "Plagiarize"
	numTargets, mana, Effects = 0, 2, ""
	description = "Secret: At the end of your opponent's turn, add copies of the cards they played this turn"
	name_CN = "抄袭"
	trigBoard = Trig_Plagiarize
	
	
class Coerce(Spell):
	Class, school, name = "Rogue,Warrior", "", "Coerce"
	numTargets, mana, Effects = 1, 3, ""
	name_CN = "胁迫"
	description = "Destroy a damaged minion. Combo: Destroy any minion"
	index = "Combo"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard and \
				(obj.health < obj.health_max or self.Game.Counters.comboCounters[self.ID] > 0)
		
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.comboCounters[self.ID] > 0
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.Game.kill(self, target)
		
	
class SelfSharpeningSword(Weapon):
	Class, name, description = "Rogue", "Self-Sharpening Sword", "After your hero attacks, gain +1 Attack"
	mana, attack, durability, Effects = 3, 1, 4, ""
	name_CN = "自砺之锋"
	trigBoard = Trig_SelfSharpeningSword
	
	
class VulperaToxinblade(Minion):
	Class, race, name = "Rogue", "", "Vulpera Toxinblade"
	mana, attack, health = 3, 3, 3
	numTargets, Effects, description = 0, "", "Your weapon has +2 Attack"
	name_CN = "狐人淬毒师"
	aura = Aura_VulperaToxinblade
	
	
class InfiltratorLilian(Minion):
	Class, race, name = "Rogue", "", "Infiltrator Lilian"
	mana, attack, health = 4, 4, 2
	name_CN = "渗透者莉莉安"
	numTargets, Effects, description = 0, "Stealth", "Stealth. Deathrattle: Summon a 4/2 Forsaken Lilian that attacks a random enemy"
	index = "Legendary"
	deathrattle = Death_InfiltratorLilian
	
	
class ForsakenLilian(Minion):
	Class, race, name = "Rogue", "", "Forsaken Lilian"
	mana, attack, health = 4, 4, 2
	name_CN = "被遗忘者莉莉安"
	numTargets, Effects, description = 0, "", ""
	index = "Legendary~Uncollectible"
	
	
class ShiftySophomore(Minion):
	Class, race, name = "Rogue", "", "Shifty Sophomore"
	mana, attack, health = 4, 4, 4
	numTargets, Effects, description = 0, "Stealth", "Stealth. Spellburst: Add a Combo card to your hand"
	name_CN = "调皮的大二学妹"
	trigBoard = Trig_ShiftySophomore
	poolIdentifier = "Combo Cards"
	@classmethod
	def generatePool(cls, pools):
		return "Combo Cards", [card for card in pools.ClassCards["Rogue"] if "~Combo" in card.index]
		
	
class Steeldancer(Minion):
	Class, race, name = "Rogue,Warrior", "", "Steeldancer"
	mana, attack, health = 4, 4, 4
	name_CN = "钢铁舞者"
	numTargets, Effects, description = 0, "", "Battlecry: Summon a random minion with Cost equal to your weapons's Attack"
	index = "Battlecry"
	def effCanTrig(self):
		self.effectViable = self.Game.availableWeapon(self.ID) is not None
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if weapon := self.Game.availableWeapon(self.ID):
			self.summon(self.newEvolved(max(weapon.attack, 0)-1, by=1, ID=self.ID))
		
	
class CuttingClass(Spell):
	Class, school, name = "Rogue,Warrior", "", "Cutting Class"
	numTargets, mana, Effects = 0, 5, ""
	description = "Draw 2 cards. Costs (1) less per Attack of your weapon"
	name_CN = "劈砍课程"
	trigHand = Trig_CuttingClass
	def selfManaChange(self):
		if weapon := self.Game.availableWeapon(self.ID): self.mana -= max(0, weapon.attack)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.Game.Hand_Deck.drawCard(self.ID)
		self.Game.Hand_Deck.drawCard(self.ID)
		
	
class DoctorKrastinov(Minion):
	Class, race, name = "Rogue,Warrior", "", "Doctor Krastinov"
	mana, attack, health = 5, 4, 4
	name_CN = "卡斯迪诺夫教授"
	numTargets, Effects, description = 0, "Rush", "Rush. Whenever this attacks, give your weapon +1/+1"
	index = "Legendary"
	trigBoard = Trig_DoctorKrastinov		
	
	
class PrimordialStudies(Spell):
	Class, school, name = "Shaman,Mage", "Arcane", "Primordial Studies"
	numTargets, mana, Effects = 0, 1, ""
	description = "Discover a Spell Damage minion. Your next one costs (1) less"
	name_CN = "始生研习"
	trigEffect = GameManaAura_PrimordialStudies
	poolIdentifier = "Spell Damage Minions as Mage"
	@classmethod
	def generatePool(cls, pools):
		return genPool_CertainMinionsasClass(pools, "Spell Damage", cond=lambda card: "Spell Damage" in card.Effects)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.discoverNew(comment, lambda : self.rngPool("Spell Damage Minions as " + class4Discover(self)))
		GameManaAura_PrimordialStudies(self.Game, self.ID).auraAppears()
		
	
class DiligentNotetaker(Minion):
	Class, race, name = "Shaman", "", "Diligent Notetaker"
	mana, attack, health = 2, 2, 3
	numTargets, Effects, description = 0, "", "Spellburst: Return the spell to your hand"
	name_CN = "笔记能手"
	trigBoard = Trig_DiligentNotetaker
	
	
class RuneDagger(Weapon):
	Class, name, description = "Shaman", "Rune Dagger", "After your hero attacks, gain Spell Damage +1 this turn"
	mana, attack, durability, Effects = 2, 1, 3, ""
	name_CN = "符文匕首"
	trigBoard, trigEffect = Trig_RuneDagger, RuneDagger_Effect
	
	
class TrickTotem(Minion):
	Class, race, name = "Shaman,Mage", "Totem", "Trick Totem"
	mana, attack, health = 2, 0, 3
	numTargets, Effects, description = 0, "", "At the end of your turn, cast a random spell that costs (3) or less"
	name_CN = "戏法图腾"
	trigBoard = Trig_TrickTotem
	poolIdentifier = "Spells Cost <=3"
	@classmethod
	def generatePool(cls, pools):
		return "Spells of <=3 Cost", [card for cards in pools.ClassCards.values() for card in cards
									  if card.category == "Spell" and card.mana < 4]
		
	
class InstructorFireheart(Minion):
	Class, race, name = "Shaman", "", "Instructor Fireheart"
	mana, attack, health = 3, 3, 3
	name_CN = "导师火心"
	numTargets, Effects, description = 0, "", "Battlecry: Discover a spell that costs (1) or more. If you play it this turn, repeat this effect"
	index = "Battlecry~Legendary"
	trigEffect = InstructorFireheart_Effect
	poolIdentifier = "Shaman Spells Cost >=1"
	@classmethod
	def generatePool(cls, pools):
		return [Class+" Spells Cost >=1" for Class in pools.Classes], \
				[[card for card in pools.ClassCards[Class] if card.category == "Spell" and card.mana > 0] for Class in pools.Classes]
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.ID == self.Game.turn:
			(trig := InstructorFireheart_Effect(self.Game, self.ID)).connect()
			trig.effect('', 0, None, None, 0, comment, 0)
		
	
class MoltenBlast(Spell):
	Class, school, name = "Shaman", "Fire", "Molten Blast"
	numTargets, mana, Effects = 1, 3, ""
	description = "Deal 2 damage. Summon that many 1/1 Elementals"
	name_CN = "岩浆爆裂"
	def text(self): return self.calcDamage(2)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(target, damage := self.calcDamage(2))
		self.summon([MoltenElemental(self.Game, self.ID) for _ in range(damage)])
		
	
class MoltenElemental(Minion):
	Class, race, name = "Shaman", "Elemental", "Molten Elemental"
	mana, attack, health = 1, 1, 1
	name_CN = "熔岩元素"
	numTargets, Effects, description = 0, "", ""
	index = "Uncollectible"
	
	
class RasFrostwhisper(Minion):
	Class, race, name = "Shaman,Mage", "", "Ras Frostwhisper"
	mana, attack, health = 5, 3, 6
	name_CN = "莱斯霜语"
	numTargets, Effects, description = 0, "", "At the end of turn, deal 1 damage to all enemies (improved by Spell Damage)"
	index = "Legendary"
	trigBoard = Trig_RasFrostwhisper
	def text(self): return 1 + self.countSpellDamage()
		
	
class TotemGoliath(Minion):
	Class, race, name = "Shaman", "Totem", "Totem Goliath"
	mana, attack, health = 5, 5, 5
	numTargets, Effects, description = 0, "", "Deathrattle: Summon all four basic totems. Overload: (1)"
	name_CN = "图腾巨像"
	overload, deathrattle = 1, Death_TotemGoliath
	
	
class TidalWave(Spell):
	Class, school, name = "Shaman", "Nature", "Tidal Wave"
	numTargets, mana, Effects = 0, 8, "Lifesteal"
	description = "Lifesteal. Deal 3 damage to all minions"
	name_CN = "潮汐奔涌"
	def text(self): return self.calcDamage(3)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(self.Game.minionsonBoard(), self.calcDamage(3))
		
	
class DemonicStudies(Spell):
	Class, school, name = "Warlock", "Shadow", "Demonic Studies"
	numTargets, mana, Effects = 0, 1, ""
	description = "Discover a Demon. Your next one costs (1) less"
	name_CN = "恶魔研习"
	trigEffect = GameManaAura_DemonicStudies
	poolIdentifier = "Demons as Warlock"
	@classmethod
	def generatePool(cls, pools):
		return genPool_MinionsofRaceasClass(pools, "Demon")
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.discoverNew(comment, lambda: self.rngPool("Demons as " + class4Discover(self)))
		GameManaAura_DemonicStudies(self.Game, self.ID).auraAppears()
		
	
class Felosophy(Spell):
	Class, school, name = "Warlock,Demon Hunter", "Fel", "Felosophy"
	numTargets, mana, Effects = 0, 1, ""
	description = "Copy the lowest Cost Demon in your hand. Outcast: Give both +1/+1"
	name_CN = "邪能学说"
	index = "Outcast"
	def effCanTrig(self):
		self.effectViable = any("Demon" in card.race for card in self.Game.Hand_Deck.hands[self.ID]) \
							and self.Game.Hand_Deck.outcastcanTrig(self)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if demons := pickObjs_LowestAttr(self.Game.Hand_Deck.hands[self.ID], cond=lambda card : "Demon" in card.race):
			Copy = self.copyCard((demon := numpyChoice(demons)), self.ID)
			self.addCardtoHand(Copy, self.ID)
			if posinHand in (-1, 0):
				self.giveEnchant((demon, Copy), 1, 1, source=Felosophy, add2EventinGUI=False)
		
	
class SpiritJailer(Minion):
	Class, race, name = "Warlock,Demon Hunter", "Demon", "Spirit Jailer"
	mana, attack, health = 1, 1, 3
	name_CN = "精魂狱卒"
	numTargets, Effects, description = 0, "", "Battlecry: Shuffle 2 Soul Fragments into your deck"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.shuffleintoDeck([SoulFragment(self.Game, self.ID) for _ in (0, 1)])
		
	
class BonewebEgg(Minion):
	Class, race, name = "Warlock", "", "Boneweb Egg"
	mana, attack, health = 2, 0, 2
	numTargets, Effects, description = 0, "", "Deathrattle: Summon two 2/1 Spiders. If you discard this, trigger it Deathrattle"
	name_CN = "骨网之卵"
	deathrattle = Death_BonewebEgg
	def whenDiscarded(self):
		for trig in self.deathrattles:
			trig.trig("TrigDeathrattle", self.ID, None, self, 0, "", 0)
		
	
class BonewebSpider(Minion):
	Class, race, name = "Warlock", "Beast", "Boneweb Spider"
	mana, attack, health = 1, 2, 1
	name_CN = "骨网蜘蛛"
	numTargets, Effects, description = 0, "", ""
	index = "Uncollectible"
	
	
class SoulShear(Spell):
	Class, school, name = "Warlock,Demon Hunter", "Shadow", "Soul Shear"
	numTargets, mana, Effects = 1, 2, ""
	description = "Deal 3 damage to a minion. Shuffle 2 Soul Fragments into your deck"
	name_CN = "灵魂剥离"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(target, self.calcDamage(3))
		self.shuffleintoDeck([SoulFragment(self.Game, self.ID) for _ in (0, 1)])
		
	
class SchoolSpirits(Spell):
	Class, school, name = "Warlock", "Shadow", "School Spirits"
	numTargets, mana, Effects = 0, 3, ""
	description = "Deal 2 damage to all minions. Shuffle 2 Soul Fragments into your deck"
	name_CN = "校园精魂"
	def text(self): return self.calcDamage(2)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(self.Game.minionsonBoard(), self.calcDamage(2))
		self.shuffleintoDeck([SoulFragment(self.Game, self.ID) for _ in (0, 1)])
		
	
class ShadowlightScholar(Minion):
	Class, race, name = "Warlock", "", "Shadowlight Scholar"
	mana, attack, health = 3, 3, 4
	name_CN = "影光学者"
	numTargets, Effects, description = 1, "", "Battlecry: Destroy a Soul Fragment in your deck to deal 3 damage"
	index = "Battlecry"
	def numTargetsNeeded(self, choice=0):
		return 1 if any(isinstance(card, SoulFragment) for card in self.Game.Hand_Deck.decks[self.ID]) else 0
		
	def effCanTrig(self):
		self.effectViable = any(isinstance(card, SoulFragment) for card in self.Game.Hand_Deck.decks[self.ID])
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for obj in target:
			if SoulFragment.destroyOne(self.Game, self.ID): self.dealsDamage(obj, 3)
			else: break
		
	
class VoidDrinker(Minion):
	Class, race, name = "Warlock", "Demon", "Void Drinker"
	mana, attack, health = 5, 4, 5
	name_CN = "虚空吸食者"
	numTargets, Effects, description = 0, "Taunt", "Taunt. Battlecry: Destroy a Soul Fragment in your deck to gain +3/+3"
	index = "Battlecry"
	def effCanTrig(self):
		self.effectViable = any(isinstance(card, SoulFragment) for card in self.Game.Hand_Deck.decks[self.ID])
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if SoulFragment.destroyOne(self.Game, self.ID): self.giveEnchant(self, 3, 3, source=VoidDrinker)
		
	
class SoulciologistMalicia(Minion):
	Class, race, name = "Warlock,Demon Hunter", "", "Soulciologist Malicia"
	mana, attack, health = 7, 5, 5
	name_CN = "灵魂学家玛丽希亚"
	numTargets, Effects, description = 0, "", "Battlecry: For each Soul Fragment in your deck, summon a 3/3 Soul with Rush"
	index = "Battlecry~Legendary"
	def text(self): return sum(isinstance(card, SoulFragment) for card in self.Game.Hand_Deck.decks[self.ID])
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if num := sum(isinstance(card, SoulFragment) for card in self.Game.Hand_Deck.decks[self.ID]):
			game, ID = self.Game, self.ID
			self.summon([ReleasedSoul(game, ID) for _ in range(num)])
		
	
class ReleasedSoul(Minion):
	Class, race, name = "Warlock,Demon Hunter", "", "Released Soul"
	mana, attack, health = 3, 3, 3
	name_CN = "被释放的灵魂"
	numTargets, Effects, description = 0, "Rush", "Rush"
	index = "Uncollectible"
	
	
class ArchwitchWillow(Minion):
	Class, race, name = "Warlock", "", "Archwitch Willow"
	mana, attack, health = 8, 5, 5
	name_CN = "高阶女巫维洛"
	numTargets, Effects, description = 0, "", "Battlecry: Summon a random Demon from your hand and deck"
	index = "Battlecry~Legendary"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		minion = self.try_SummonfromOwn(hand_deck=0, cond=lambda card: "Demon" in card.race)
		self.try_SummonfromOwn(position=(minion if minion else self).position + 1, cond=lambda card: "Demon" in card.race)
		
	
class AthleticStudies(Spell):
	Class, school, name = "Warrior", "", "Athletic Studies"
	numTargets, mana, Effects = 0, 1, ""
	description = "Discover a Rush minion. Your next one costs (1) less"
	name_CN = "体能研习"
	trigEffect = GameManaAura_AthleticStudies
	poolIdentifier = "Rush Minions as Warrior"
	@classmethod
	def generatePool(cls, pools):
		return genPool_CertainMinionsasClass(pools, "Rush", cond=lambda card: "Rush" in card.Effects)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.discoverNew(comment, lambda : self.rngPool("Rush Minions as " + class4Discover(self)))
		GameManaAura_AthleticStudies(self.Game, self.ID).auraAppears()
		
	
class ShieldofHonor(Spell):
	Class, school, name = "Warrior,Paladin", "Holy", "Shield of Honor"
	numTargets, mana, Effects = 1, 1, ""
	description = "Give a damaged minion +3 Attack and Divine Shield"
	name_CN = "荣誉护盾"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard and obj.health < obj.health_max
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(target, 3, 0, effGain="Divine Shield", source=ShieldofHonor)
		
	
class InFormation(Spell):
	Class, school, name = "Warrior", "", "In Formation!"
	numTargets, mana, Effects = 0, 2, ""
	description = "Add 2 random Taunt minions to your hand"
	name_CN = "保持阵型"
	poolIdentifier = "Taunt Minions"
	@classmethod
	def generatePool(cls, pools):
		return "Taunt Minions", [card for card in pools.NeutralMinions if "Taunt" in card.Effects]
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.addCardtoHand(numpyChoice(self.rngPool("Taunt Minions"), 2, replace=True), self.ID)
		
	
class CeremonialMaul(Weapon):
	Class, name, description = "Warrior,Paladin", "Ceremonial Maul", "Spellburst: Summon a student with Taunt and stats equal to the spell's Cost"
	mana, attack, durability, Effects = 3, 2, 2, ""
	name_CN = "仪式重槌"
	trigBoard = Trig_CeremonialMaul
	
	
class HonorStudent(Minion):
	Class, race, name = "Warrior,Paladin", "", "Honor Student"
	mana, attack, health = 1, 1, 1
	name_CN = "仪仗学员"
	numTargets, Effects, description = 0, "Taunt", "Taunt"
	index = "Uncollectible"
	
	
class LordBarov(Minion):
	Class, race, name = "Warrior,Paladin", "", "Lord Barov"
	mana, attack, health = 3, 3, 2
	name_CN = "巴罗夫领主"
	numTargets, Effects, description = 0, "", "Battlecry: Set the Health of all other minions to 1. Deathrattle: Deal 1 damage to all other minions"
	index = "Battlecry~Legendary"
	deathrattle = Death_LordBarov
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.setStat(self.Game.minionsonBoard(exclude=self), (None, 1), source=LordBarov)
		
	
class Playmaker(Minion):
	Class, race, name = "Warrior", "", "Playmaker"
	mana, attack, health = 3, 4, 3
	numTargets, Effects, description = 0, "", "After you play a Rush minion, summon a copy with 1 Health remaining"
	name_CN = "团队核心"
	trigBoard = Trig_Playmaker
	
	
class ReapersScythe(Weapon):
	Class, name, description = "Warrior", "Reaper's Scythe", "Spellburst: Also damages adjacent minions this turn"
	mana, attack, durability, Effects = 4, 4, 2, ""
	name_CN = "收割之镰"
	trigBoard = Trig_ReapersScythe
	
	
class Commencement(Spell):
	Class, school, name = "Warrior,Paladin", "", "Commencement"
	numTargets, mana, Effects = 0, 7, ""
	description = "Summon a minion from your deck. Give it Taunt and Divine Shield"
	name_CN = "毕业仪式"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if minion := self.try_SummonfromOwn():
			self.giveEnchant(minion, multipleEffGains=(("Taunt", 1, None), ("Divine Shield", 1, None)),
							 source=Commencement)
		
	
class Troublemaker(Minion):
	Class, race, name = "Warrior", "", "Troublemaker"
	mana, attack, health = 8, 6, 8
	numTargets, Effects, description = 0, "", "At the end of your turn, summon two 3/3 Ruffians that attack random enemies"
	name_CN = "问题学生"
	trigBoard = Trig_Troublemaker
	
	
class Ruffian(Minion):
	Class, race, name = "Warrior", "", "Ruffian"
	mana, attack, health = 3, 3, 3
	name_CN = "无赖"
	numTargets, Effects, description = 0, "", ""
	index = "Uncollectible"
	
	
class Rattlegore(Minion):
	Class, race, name = "Warrior", "", "Rattlegore"
	mana, attack, health = 9, 9, 9
	name_CN = "血骨傀儡"
	numTargets, Effects, description = 0, "", "Deathrattle: Resummon this with -1/-1"
	index = "Legendary"
	deathrattle = Death_Rattlegore
	
	


AllClasses_Academy = [
	Aura_RobesofProtection, Aura_Kolek, Aura_VulperaToxinblade, Trig_Corrupt, Spellburst, Trig_IntrepidInitiate, Trig_PenFlinger,
	Trig_SphereofSapience, Trig_VoraciousReader, Trig_EducatedElekk, Trig_EnchantedCauldron, Trig_CrimsonHothead,
	Trig_WretchedTutor, Trig_HeadmasterKelThuzad, Trig_Ogremancer, Trig_OnyxMagescribe, Trig_KeymasterAlabaster, Trig_TrueaimCrescent,
	Trig_AceHunterKreen, Trig_Magehunter, Trig_BloodHerald, Trig_FelGuardians, Trig_AncientVoidHound, Trig_Gibberling,
	Trig_SpeakerGidra, Trig_TwilightRunner, Trig_ForestWardenOmu, GameRuleAura_ProfessorSlate, Trig_KroluskBarkstripper,
	Trig_Firebrand, Trig_JandiceBarov, Trig_MozakiMasterDuelist, Trig_WyrmWeaver, Trig_GoodyTwoShields, Trig_HighAbbessAlura,
	Trig_DevoutPupil, Trig_TuralyontheTenured, Trig_PowerWordFeast, Trig_CabalAcolyte, Trig_DisciplinarianGandling,
	Trig_FleshGiant, Trig_Plagiarize, Trig_SelfSharpeningSword, Trig_ShiftySophomore, Trig_CuttingClass, Trig_DoctorKrastinov,
	Trig_DiligentNotetaker, Trig_RuneDagger, Trig_TrickTotem, Trig_RasFrostwhisper, Trig_CeremonialMaul, Trig_Playmaker,
	Trig_ReapersScythe, Trig_Troublemaker, Death_SneakyDelinquent, Death_EducatedElekk, Death_FishyFlyer, Death_SmugSenior,
	Death_PlaguedProtodrake, Death_BloatedPython, Death_TeachersPet, Death_InfiltratorLilian, Death_TotemGoliath,
	Death_BonewebEgg, Death_LordBarov, Death_Rattlegore, GameManaAura_TourGuide, GameManaAura_CultNeophyte, GameManaAura_NatureStudies,
	GameManaAura_CarrionStudies, GameManaAura_DraconicStudies, MindrenderIllucia_Effect, SecretPassage_Effect, GameManaAura_PrimordialStudies,
	RuneDagger_Effect, InstructorFireheart_Effect, GameManaAura_DemonicStudies, GameManaAura_AthleticStudies, Variant_TransferStudent,
	TransferStudent_Ogrimmar, TransferStudent_Stormwind, TransferStudent_Stranglethorn, TransferStudent_FourWindValley,
	TransferStudent_Shadows, TransferStudent_UldumDesert, TransferStudent_UldumOasis, TransferStudent_Dragons, TransferStudent_Outlands,
	TransferStudent_Academy, TransferStudent_Darkmoon_Corrupt, TransferStudent_Darkmoon, TransferStudent_Barrens,
	TransferStudent_UnitedinStormwind, TransferStudent, DeskImp, AnimatedBroomstick, IntrepidInitiate, PenFlinger,
	SphereofSapience, NewFate, TourGuide, CultNeophyte, ManafeederPanthara, SneakyDelinquent, SpectralDelinquent,
	VoraciousReader, Wandmaker, EducatedElekk, EnchantedCauldron, RobesofProtection, CrimsonHothead, DivineRager,
	FishyFlyer, SpectralFlyer, LorekeeperPolkelt, WretchedTutor, HeadmasterKelThuzad, LakeThresher, Ogremancer, RisenSkeleton,
	StewardofScrolls, Vectus, PlaguedHatchling, OnyxMagescribe, SmugSenior, SpectralSenior, SorcerousSubstitute, KeymasterAlabaster,
	PlaguedProtodrake, DemonCompanion, Reffuh, Kolek, Shima, DoubleJump, TrueaimCrescent, AceHunterKreen, Magehunter,
	ShardshatterMystic, Glide, Marrowslicer, SoulFragment, StarStudentStelina, VilefiendTrainer, SnarlingVilefiend,
	BloodHerald, SoulshardLapidary, CycleofHatred, SpiritofVengeance, FelGuardians, SoulfedFelhound, AncientVoidHound,
	LightningBloom, Gibberling, NatureStudies, PartnerAssignment, SpeakerGidra, Groundskeeper, TwilightRunner, ForestWardenOmu,
	CalltoAid, AlarmtheForest, CalltoAid_Option, AlarmtheForest_Option, RunicCarvings, TreantTotem, SurvivaloftheFittest,
	AdorableInfestation, MarsuulCub, CarrionStudies, Overwhelm, Wolpertinger, BloatedPython, HaplessHandler, ProfessorSlate,
	RiletheHerd_Option, Transfiguration_Option, ShandoWildclaw, KroluskBarkstripper, TeachersPet, GuardianAnimals,
	BrainFreeze, DevolvingMissiles, LabPartner, WandThief, CramSession, Combustion, Firebrand, PotionofIllusion, JandiceBarov,
	MozakiMasterDuelist, WyrmWeaver, FirstDayofSchool, WaveofApathy, ArgentBraggart, GiftofLuminance, GoodyTwoShields,
	HighAbbessAlura, BlessingofAuthority, DevoutPupil, JudiciousJunior, TuralyontheTenured, RaiseDead, DraconicStudies,
	FrazzledFreshman, MindrenderIllucia, PowerWordFeast, BrittleboneDestroyer, CabalAcolyte, DisciplinarianGandling,
	FailedStudent, Initiation, FleshGiant, SecretPassage, Plagiarize, Coerce, SelfSharpeningSword, VulperaToxinblade,
	InfiltratorLilian, ForsakenLilian, ShiftySophomore, Steeldancer, CuttingClass, DoctorKrastinov, PrimordialStudies,
	DiligentNotetaker, RuneDagger, TrickTotem, InstructorFireheart, MoltenBlast, MoltenElemental, RasFrostwhisper,
	TotemGoliath, TidalWave, DemonicStudies, Felosophy, SpiritJailer, BonewebEgg, BonewebSpider, SoulShear, SchoolSpirits,
	ShadowlightScholar, VoidDrinker, SoulciologistMalicia, ReleasedSoul, ArchwitchWillow, AthleticStudies, ShieldofHonor,
	InFormation, CeremonialMaul, HonorStudent, LordBarov, Playmaker, ReapersScythe, Commencement, Troublemaker, Ruffian,
	Rattlegore, 
]

for class_ in AllClasses_Academy:
	if issubclass(class_, Card):
		class_.index = "SCHOLOMANCE" + ("~" if class_.index else '') + class_.index