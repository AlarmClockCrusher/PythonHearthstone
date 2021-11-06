from Parts_CardTypes import *
from Parts_TrigsAuras import *

from HS_AcrossPacks import ExcessMana, WaterElemental_Basic, FieryWarAxe_Basic

#休眠的随从在打出之后2回合本来时会触发你“召唤一张随从”

"""Auras"""
class GameRuleAura_KaynSunfury(GameRuleAura):
	def auraAppears(self): self.keeper.Game.effects[self.keeper.ID]["Ignore Taunt"] += 1
	def auraDisappears(self): self.keeper.Game.effects[self.keeper.ID]["Ignore Taunt"] -= 1

class ManaAura_YsielWindsinger(ManaAura):
	to = 1
	def applicable(self, target): target.category == "Spell" and target.ID == self.keeper.ID

class ManaAura_KanrethadEbonlocke(ManaAura):
	by = -1
	def applicable(self, target): return target.ID == self.keeper.ID and "Demon" in target.race


"""Deathrattles"""
class Death_RustswornInitiate(Deathrattle_Minion):
	description = "Deathrattle: Summon a 1/1 Impcaster with Spell Damage +1"
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.summon(Impcaster(self.keeper.Game, self.keeper.ID))

class Death_TeronGorefiend(Deathrattle_Minion):
	description = "Deathrattle: Resummon all destroyed minions with +1/+1"
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		keeper = self.keeper
		if self.savedObjs:
			keeper.AOE_GiveEnchant((minions := [minion(keeper.Game, keeper.ID) for minion in self.savedObjs]),
								   1, 1, name=TeronGorefiend, add2EventinGUI=False)
			keeper.summon(minions)

	def selfCopy(self, recipient):
		trig = type(self)(recipient)
		trig.minionsDestroyed = self.savedObjs[:]
		return trig

	def assistCreateCopy(self, Copy):
		Copy.savedObjs = self.savedObjs[:]

class Death_DisguisedWanderer(Deathrattle_Minion):
	description = "Deathrattle: Summon a 9/1 Inquisitor"
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.summon(RustswornInquisitor(self.keeper.Game, self.keeper.ID))

class Death_RustswornCultist(Deathrattle_Minion):
	description = "Deathrattle: Summon a 1/1 Demon"
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.summon(RustedDevil(self.keeper.Game, self.keeper.ID))

class Death_Alar(Deathrattle_Minion):
	description = "Deathrattle: Summon a 0/3 Ashes of Al'ar that resurrects this minion on your next turn"
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.summon(AshesofAlar(self.keeper.Game, self.keeper.ID))

class Death_DragonmawSkyStalker(Deathrattle_Minion):
	description = "Deathrattle: Summon a 3/4 Dragonrider"
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.summon(Dragonrider(self.keeper.Game, self.keeper.ID))

class Death_ScrapyardColossus(Deathrattle_Minion):
	description = "Deathrattle: Summon a 7/7 Felcracked Colossus with Taunt"
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.summon(FelcrackedColossus(self.keeper.Game, self.keeper.ID))

class Death_FelSummoner(Deathrattle_Minion):
	description = "Deathrattle: Summon a random Demon from your hand"
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.try_SummonfromHand(self.keeper.pos + 1, func=lambda card: "Demon" in card.race)

class Death_CoilfangWarlord(Deathrattle_Minion):
	description = "Deathrattle: Summon a 5/9 Warlord with Taunt"
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.summon(ConchguardWarlord(self.keeper.Game, self.keeper.ID))

class Death_ArchsporeMsshifn(Deathrattle_Minion):
	description = "Deathrattle: Shuffle 'Msshi'fn Prime' into your deck"
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.shuffleintoDeck(MsshifnPrime(self.keeper.Game, self.keeper.ID))

class Death_Helboar(Deathrattle_Minion):
	description = "Deathrattle: Give a random Beast in your hand +1/+1"
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if beasts := [card for card in self.keeper.Game.Hand_Deck.hands[self.keeper.ID] \
					  if "Beast" in card.race and card.mana > 0]:
			self.keeper.giveEnchant(numpyChoice(beasts), 1, 1, name=Helboar, add2EventinGUI=False)

class Death_AugmentedPorcupine(Deathrattle_Minion):
	description = "Deathrattle: Deal this minion's Attack damage randomly split among all enemies"
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion, side = self.keeper, 3 - self.keeper.ID
		for _ in range(number):
			if minions := self.keeper.Game.charsAlive(side):
				minion.dealsDamage(numpyChoice(minions), 1)
			else: break

class Death_ZixorApexPredator(Deathrattle_Minion):
	description = "Deathrattle: Shuffle 'Zixor Prime' into your deck"
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.shuffleintoDeck(ZixorPrime(self.keeper.Game, self.keeper.ID))

class Death_AstromancerSolarian(Deathrattle_Minion):
	description = "Deathrattle: Shuffle 'Solarian Prime' into your deck"
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.shuffleintoDeck(SolarianPrime(self.keeper.Game, self.keeper.ID))

class Death_Starscryer(Deathrattle_Minion):
	description = "Deathrattle: Draw a spell"
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.drawCertainCard(lambda card: card.category == "Spell")

class Death_MurgurMurgurgle(Deathrattle_Minion):
	description = "Deathrattle: Shuffle 'Murgurgle Prime' into your deck"
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.shuffleintoDeck(MurgurglePrime(self.keeper.Game, self.keeper.ID))

class Death_LibramofWisdom(Deathrattle_Minion):
	description = "Deathrattle: 'Libram of Wisdom' spell to your hand'"
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.addCardtoHand(LibramofWisdom, self.keeper.ID)

class Death_ReliquaryofSouls(Deathrattle_Minion):
	description = "Deathrattle: Shuffle 'Reliquary Prime' into your deck"
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.shuffleintoDeck(ReliquaryPrime(self.keeper.Game, self.keeper.ID))

class Death_Akama(Deathrattle_Minion):
	description = "Deathrattle: Shuffle 'Akama Prime' into your deck"
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.shuffleintoDeck(AkamaPrime(self.keeper.Game, self.keeper.ID))

class Death_CursedVagrant(Deathrattle_Minion):
	description = "Deathrattle: Summon a 7/5 Shadow with Stealth"
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.summon(CursedShadow(self.keeper.Game, self.keeper.ID))

class Death_LadyVashj(Deathrattle_Minion):
	description = "Deathrattle: Shuffle 'Vashj Prime' into your deck"
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.shuffleintoDeck(VashjPrime(self.keeper.Game, self.keeper.ID))

class Death_VividSpores(Deathrattle_Minion):
	description = "Deathrattle: Resummon this minion'"
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		# This Deathrattle can't possibly be triggered in hand
		self.keeper.summon(type(self.keeper)(self.keeper.Game, self.keeper.ID))

class Death_KanrethadEbonlocke(Deathrattle_Minion):
	description = "Deathrattle: Shuffle 'Kanrethad Prime' into your deck"
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.shuffleintoDeck(KanrethadPrime(self.keeper.Game, self.keeper.ID))

class Death_EnhancedDreadlord(Deathrattle_Minion):
	description = "Deathrattle: Summon a 5/5 Dreadlord with Lifesteal"
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.summon(DesperateDreadlord(self.keeper.Game, self.keeper.ID))

class Death_KargathBladefist(Deathrattle_Minion):
	description = "Deathrattle: Shuffle 'Kargath Prime' into your deck"
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.shuffleintoDeck(KargathPrime(self.keeper.Game, self.keeper.ID))

class Death_ScrapGolem(Deathrattle_Minion):
	description = "Deathrattle: Gain Armor equal to this minion's Attack"
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.giveHeroAttackArmor(self.keeper.ID, armor=number)


"""Trigs"""
class Trig_ImprisonedDormantForm(Trig_Countdown):
	signals, counter = ("TurnStarts",), 2
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and ID == self.keeper.ID  # 会在我方回合开始时进行苏醒

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if self.counter < 1:
			# 假设唤醒的Imprisoned Vanilla可以携带buff
			self.keeper.Game.transform(self.keeper, self.keeper.minionInside, firstTime=False)
			if hasattr(self.keeper.minionInside, "awakenEffect"):
				self.keeper.minionInside.awakenEffect()


class Trig_InfectiousSporeling(TrigBoard):
	signals = ("MinionTookDamage",)
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject == self.keeper and target.onBoard and target.health > 0 and target.dead == False

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.transform(target, InfectiousSporeling(self.keeper.Game, target.ID))


class Trig_SoulboundAshtongue(TrigBoard):
	signals = ("MinionTakesDmg", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return target == self.keeper

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.dealsDamage(self.keeper.Game.heroes[self.keeper.ID], number)
		
		
class Trig_BonechewerBrawler(TrigBoard):
	signals = ("MinionTakesDmg", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return target == self.keeper and self.keeper.onBoard

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.giveEnchant(self.keeper, statEnchant=Enchantment_Cumulative(2, 0, name=BonechewerBrawler))
		

class Trig_MoargArtificer(TrigBoard):
	signals = ("FinalDmgonMinion?",)
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and target.category == "Minion" and subject.category == "Spell" and number[0] > 0

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		number[0] += number[0]


class Trig_BlisteringRot(TrigBoard):
	signals = ("TurnEnds", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and ID == self.keeper.ID and self.keeper.health > 0
	#假设召唤的Rot只是一个1/1，然后接受buff.而且该随从生命值低于1时不能触发
	#假设攻击力为负数时，召唤物的攻击力为0
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if minion := self.keeper.summon(LivingRot(self.keeper.Game, self.keeper.ID)):
			self.keeper.setStat(minion, max(0, self.keeper.attack), self.keeper.health, name=BlisteringRot)
			

class Trig_Magtheridon_Dormant(Trig_Countdown):
	signals, counter = ("MinionDied", ), 3
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and isinstance(target, HellfireWarder) and target.ID != self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		game = self.keeper.Game
		if self.counter < 1:
			game.kill(self.keeper, game.minionsonBoard(1) + game.minionsonBoard(2))
			game.transform(self.keeper, self.keeper.minionInside, firstTime=False)


class Trig_Replicatotron(TrigBoard):
	signals = ("TurnEnds", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if neighbors := self.keeper.Game.neighbors2(self.keeper)[0]:
			self.keeper.transform(numpyChoice(neighbors), self.keeper.selfCopy(self.keeper.ID, self.keeper))
		

class Trig_AshesofAlar(TrigBoard):
	signals = ("TurnStarts", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.transform(self.keeper, Alar(self.keeper.Game, self.keeper.ID))
		

class Trig_BonechewerVanguard(TrigBoard):
	signals = ("MinionTakesDmg", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return target == self.keeper and self.keeper.onBoard

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.giveEnchant(self.keeper, statEnchant=Enchantment_Cumulative(2, 0, name=BonechewerVanguard))


class Trig_KaelthasSunstrider(Trig_Countdown):
	signals, counter = ("SpellBeenPlayed", "NewTurnStarts"), 2
	def resetCount(self, useOrig=True):
		self.counter = 2 - self.keeper.Game.Counters.numSpellsPlayedThisTurn[self.keeper.ID] % 3
		if not self.counter: self.startAura() #只会在满足条件的时候启动光环，但是光环被消耗或过期时不会有反应，而由生成的一次性光环处理，然后通知这个扳机

	def disconnect(self):
		trigs = self.keeper.Game.trigsBoard[self.keeper.ID]
		for sig in self.signals: removefromListinDict(self, trigs, sig)
		self.removeAura()

	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and (signal == "NewTurnStarts" or subject.ID == self.keeper.ID)

	#产生一次性的光环时，需要让那个光环携带凯尔萨斯这个随从的reference，从而那个光环因使用或者过期而消失时可以抒随从身上的光环也去掉
	def startAura(self):
		self.keeper.auras.append(aura := GameManaAura_KaelthasSunstrider(self.keeper.Game, self.keeper.ID, self.keeper))
		aura.auraAppears()
		self.keeper.btn.effectChangeAni("Aura")

	#只会在随从自己disappear从而扳机取消时引用。这个光环被法术消耗掉的时候由GameManaAura_KaelthasSunstrider自行处理
	def removeAura(self):
		for aura in self.keeper.auras[:]:
			if isinstance(aura, GameManaAura_KaelthasSunstrider):
				aura.auraDisappears()
				removefrom(aura, self.keeper.auras)
		self.keeper.btn.effectChangeAni("Aura")

	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrig(signal, ID, subject, target, number, comment):
			counter = self.counter
			self.resetCount()
			if counter != self.counter and (btn := self.keeper.btn):
				btn.GUI.seqHolder[-1].append(btn.icons["Hourglass"].seqUpdateText())


class Trig_DemonicBlast(Trig_Countdown):
	signals, counter = ("HeroUsedAbility",), 2
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.keeper

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		power_Old = self.keeper
		if self.counter < 1:
			power = power_Old.powerReplaced
			power.ID = power_Old.ID
			power.replacePower()
		elif power_Old.btn:
			GUI = power_Old.btn.GUI
			texture = GUI.loader.loadTexture("Images\\HeroesandPowers\\DemonicBlast.png")
			np_CardImage, np_Card = power_Old.btn.models["cardImage"], power_Old.btn.models["card"]
			GUI.seqHolder[-1].append(GUI.FUNC(np_CardImage.setTexture, np_CardImage.findTextureStage('*'), texture, 1))
			GUI.seqHolder[-1].append(GUI.FUNC(np_Card.setTexture, np_Card.findTextureStage('*'), texture, 1))


class Trig_PriestessofFury(TrigBoard):
	signals = ("TurnEnds", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion, side = self.keeper, 3 - self.keeper.ID
		for _ in range(6):
			if objs := minion.Game.charsAlive(side): minion.dealsDamage(numpyChoice(objs), 1)
			else: break


class Trig_PitCommander(TrigBoard):
	signals = ("TurnEnds", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.try_SummonfromDeck(self.keeper.pos + 1, func=lambda card: "Demon" in card.race)
		
		
class Trig_Ironbark(TrigHand):
	signals = ("ManaXtlsCheck",)
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.inHand and ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.Game.Manas.calcMana_Single(self.keeper)


class Trig_Bogbeam(TrigHand):
	signals = ("ManaXtlsCheck",)
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.inHand and ID == self.keeper.ID
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.Game.Manas.calcMana_Single(self.keeper)


class Trig_MarshHydra(TrigBoard):
	signals = ("MinionAttackedMinion", "MinionAttackedHero", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject == self.keeper

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.addCardtoHand(numpyChoice(self.rngPool("8-Cost Minions")), self.keeper.ID)


class Trig_PackTactics(Trig_Secret):
	signals = ("MinionAttacksMinion", "HeroAttacksMinion", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.ID != self.keeper.Game.turn and target[0].ID == self.keeper.ID and self.keeper.Game.space(self.keeper.ID) > 0
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.summon(target[0].selfCopy(self.keeper.ID, self.keeper, 3, 3), position=target[0].pos+1)
		

class Trig_Evocation(TrigHand):
	signals, changesCard, description = ("TurnEnds",), True, "At the end of your turn, discard this"
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.inHand #They will be discarded at the end of any turn

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.Game.Hand_Deck.discard(self.keeper.ID, self.keeper)
		
		
class Trig_ApexisSmuggler(TrigBoard):
	signals = ("SpellBeenPlayed",)
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject.ID == self.keeper.ID and subject.race == "Secret"

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.discoverandGenerate(ApexisSmuggler, '',
										poolFunc=lambda: self.rngPool(classforDiscover(self.keeper) + " Spells"))


class Trig_NetherwindPortal(Trig_Secret):
	signals = ("SpellBeenPlayed",)
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.ID != self.keeper.Game.turn == self.keeper.ID and self.keeper.Game.space(self.keeper.ID) > 0

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.summon(numpyChoice(self.rngPool("4-Cost Minions to Summon"))(self.keeper.Game, self.keeper.ID))


class Trig_UnderlightAnglingRod(TrigBoard):
	signals = ("HeroAttackedMinion", "HeroAttackedHero", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.keeper.Game.heroes[self.keeper.ID] and self.keeper.onBoard

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.addCardtoHand(numpyChoice(self.rngPool("Murlocs")), self.keeper.ID)
			

class Trig_SethekkVeilweaver(TrigBoard):
	signals = ("SpellBeenPlayed", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject.ID == self.keeper.ID and target and target.category == "Minion"

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.addCardtoHand(numpyChoice(self.rngPool("Priest Spells")), self.keeper.ID)
			
			
class Trig_DragonmawOverseer(TrigBoard):
	signals = ("TurnEnds", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if minions := self.keeper.Game.minionsonBoard(self.keeper.ID, exclude=self.keeper):
			self.keeper.giveEnchant(numpyChoice(minions), statEnchant=Enchantment_Cumulative(2, 2, name=DragonmawOverseer))
			
			
class Trig_SkeletalDragon(TrigBoard):
	signals = ("TurnEnds", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.addCardtoHand(numpyChoice(self.rngPool("Dragons")), self.keeper.ID)
			
			
class Trig_Ambush(Trig_Secret):
	signals = ("MinionBeenPlayed", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.ID != self.keeper.Game.turn and subject.ID != self.keeper.ID and self.keeper.Game.space(self.keeper.ID) > 0
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.summon(BrokenAmbusher(self.keeper.Game, self.keeper.ID))


class Trig_Bamboozle(Trig_Secret):
	signals = ("MinionAttacksMinion", "HeroAttacksMinion",)
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.ID != self.keeper.Game.turn and target[0].ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		newMinion = self.keeper.newEvolved(type(target[0]).mana, by=3, ID=self.keeper.ID)
		self.keeper.transform(target[0], newMinion)
		if target[0] == target[1]: target[0] = target[1] = newMinion
		else: target[0] = newMinion


class Trig_DirtyTricks(Trig_Secret):
	signals = ("SpellBeenPlayed", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.ID != self.keeper.Game.turn and subject.ID != self.keeper.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.Game.Hand_Deck.drawCard(self.keeper.ID)
		self.keeper.Game.Hand_Deck.drawCard(self.keeper.ID)
		

class Trig_ShadowjewelerHanar(TrigBoard):
	signals = ("SpellBeenPlayed", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.onBoard and subject.ID == self.keeper.ID and subject.race == "Secret"

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.discoverandGenerate_MultiplePools(ShadowjewelerHanar, '',
													  poolsFunc=lambda : ShadowjewelerHanar.decidePools(self.keeper, subject.Class))


class Trig_BoggspineKnuckles(TrigBoard):
	signals = ("HeroAttackedMinion", "HeroAttackedHero", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.keeper.Game.heroes[self.keeper.ID] and self.keeper.onBoard

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		keeper = self.keeper
		func, ID = keeper.newEvolved, keeper.ID
		for minion in keeper.minionsonBoard(ID):
			keeper.transform(minion, func(type(minion).mana, by=1, ID=ID))


class Trig_Darkglare(TrigBoard):
	signals = ("HeroTookDmg",)
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return target == self.keeper.Game.heroes[self.keeper.ID]

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.Game.Manas.restoreManaCrystal(1, self.keeper.ID)


class Trig_KelidantheBreaker(TrigHand):
	signals = ("TurnEnds", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.inHand and self.keeper.justDrawn and ID == self.keeper.ID

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.justDrawn = False
		self.disconnect() #只需要触发一次
		

#不知道与博尔夫碎盾和Blur的结算顺序
class Trig_BulwarkofAzzinoth(TrigBoard):
	signals = ("FinalDmgonHero?", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		#Can only prevent damage if there is still durability left
		print("Testing the Bulwark of Azzinoth",  target == self.keeper.Game.heroes[self.keeper.ID] and self.keeper.onBoard)
		print(target == self.keeper.Game.heroes[self.keeper.ID], self.keeper.onBoard)
		return target == self.keeper.Game.heroes[self.keeper.ID] and self.keeper.onBoard

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		number[0] = 0
		self.keeper.losesDurability()
		

class Trig_KargathPrime(TrigBoard):
	signals = ("MinionAttackedMinion", )
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.keeper and self.keeper.onBoard and (target.health < 1 or target.dead == True)

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.giveHeroAttackArmor(self.keeper.ID, armor=10)


class Trig_BloodboilBrute(TrigHand):
	signals = ("MinionAppears", "MinionDisappears", "MinionTakesDmg",)
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.keeper.inHand

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.keeper.Game.Manas.calcMana_Single(self.keeper)


"""Game TrigEffects and Game Auras"""
class GameManaAura_KaelthasSunstrider(GameManaAura_OneTime):
	to = 1
	def __init__(self, Game, ID, keeper):
		super().__init__(Game, ID)
		self.keeper = keeper

	def applicable(self, target): return target.ID == self.ID and target.category == "Spell"
	def auraDisappears(self):
		super().auraDisappears()
		removefrom(self, self.keeper.auras)
		self.keeper.btn.effectChangeAni("Aura")

	def createCopy(self, game):
		if self not in game.copiedObjs:  # 这个光环没有被复制过
			game.copiedObjs[self] = auraCopy = type(self)(game, self.ID, None)
			auraCopy.keeper = self.keeper.createCopy(game)
			for receiver in self.receivers:
				auraCopy.receivers.append((receiverCopy := receiver.createCopy(game, auraCopy)))
				receiverCopy.recipient = receiver.recipient.createCopy(game)
			return auraCopy
		else: return game.copiedObjs[self]


class GameManaAura_AldorAttendant(GameManaAura_OneTime):
	signals, by, temporary = ("CardEntersHand",), -1, False
	def applicable(self, target): return target.ID == self.ID and "Libram of " in target.name

class GameManaAura_AldorTruthseeker(GameManaAura_OneTime):
	signals, by, temporary = ("CardEntersHand",), -2, False
	def applicable(self, target): return target.ID == self.ID and "Libram of " in target.name


"""Neutral Cards"""
#休眠的随从在打出之后2回合本来时会触发你“召唤一张随从”
class Minion_Dormantfor2turns(Minion):
	Class, race, name = "Neutral", "", "Imprisoned Vanilla"
	mana, attack, health = 5, 5, 5
	index = "Vanilla~Neutral~Minion~5~5~5~~Imprisoned Vanilla"
	requireTarget, effects, description = False, "", "Dormant for 2 turns. When this awakens, do something"
	#出现即休眠的随从的played过程非常简单
	def played(self, target=None, choice=0, mana=0, posinHand=-2, comment=""):
		self.health = self.health_max
		self.appears(firstTime=True) #打出时一定会休眠，同时会把Game.minionPlayed变为None
		
	def appears(self, firstTime=True):
		self.onBoard = True
		self.inHand = self.inDeck = self.dead = False
		self.enterBoardTurn = self.Game.numTurn
		self.mana = type(self).mana #Restore the minion's mana to original value.
		self.decideAttChances_base() #Decide base att chances, given Windfury and Mega Windfury
		#没有光环，目前炉石没有给随从人为添加光环的效果, 不可能在把手牌中获得的扳机带入场上，因为会在变形中丢失
		#The buffAuras/hasAuras will react to this signal.
		if firstTime: #首次出场时会进行休眠，而且休眠状态会保持之前的随从buff
			self.Game.transform(self, ImprisonedDormantForm(self.Game, self.ID, self), firstTime=True)
		else: #只有不是第一次出现在场上时才会执行这些函数
			if self.btn:
				self.btn.isPlayed, self.btn.card = True, self
				self.btn.placeIcons()
				self.btn.statChangeAni()
				self.btn.effectChangeAni()
			for aura in self.auras: aura.auraAppears()
			for trig in self.trigsBoard + self.deathrattles: trig.connect()
			self.Game.sendSignal("MinionAppears", self.ID, self, None, 0, comment=firstTime)
			
	def awakenEffect(self):
		pass

class ImprisonedDormantForm(Dormant):
	Class, school, name = "Neutral", "", "Imprisoned Vanilla"
	description = "Awakens after 2 turns"
	trigBoard = Trig_ImprisonedDormantForm
	def assistCreateCopy(self, Copy):
		Copy.minionInside = self.minionInside.createCopy(Copy.Game)
		Copy.name, Copy.Class, Copy.description = self.name, self.Class, self.description
		

class EtherealAugmerchant(Minion):
	Class, race, name = "Neutral", "", "Ethereal Augmerchant"
	mana, attack, health = 1, 2, 1
	index = "BLACK_TEMPLE~Neutral~Minion~1~2~1~~Ethereal Augmerchant~Battlecry"
	requireTarget, effects, description = True, "", "Battlecry: Deal 1 damage to a minion and give it Spell Damage +1"
	name_CN = "虚灵改装师"
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		#需要随从在场并且还是随从形态
		if target and (target.onBoard or target.inHand):
			self.dealsDamage(target, 1)
			self.giveEnchant(target, effGain="Spell Damage", name=EtherealAugmerchant)
		return target
		
		
class GuardianAugmerchant(Minion):
	Class, race, name = "Neutral", "", "Guardian Augmerchant"
	mana, attack, health = 1, 2, 1
	index = "BLACK_TEMPLE~Neutral~Minion~1~2~1~~Guardian Augmerchant~Battlecry"
	requireTarget, effects, description = True, "", "Battlecry: Deal 1 damage to a minion and give it Divine Shield"
	name_CN = "防护改装师"
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and (target.onBoard or target.inHand):
			self.dealsDamage(target, 1)
			self.giveEnchant(target, effGain="Divine Shield", name=GuardianAugmerchant)
		return target


class InfectiousSporeling(Minion):
	Class, race, name = "Neutral", "", "Infectious Sporeling"
	mana, attack, health = 1, 1, 2
	index = "BLACK_TEMPLE~Neutral~Minion~1~1~2~~Infectious Sporeling"
	requireTarget, effects, description = False, "", "After this damages a minion, turn it into an Infectious Sporeling"
	name_CN = "传染孢子"
	trigBoard = Trig_InfectiousSporeling		

		
class RocketAugmerchant(Minion):
	Class, race, name = "Neutral", "", "Rocket Augmerchant"
	mana, attack, health = 1, 2, 1
	index = "BLACK_TEMPLE~Neutral~Minion~1~2~1~~Rocket Augmerchant~Battlecry"
	requireTarget, effects, description = True, "", "Battlecry: Deal 1 damage to a minion and give it Rush"
	name_CN = "火箭改装师"
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and (target.onBoard or target.inHand):
			self.dealsDamage(target, 1)
			self.giveEnchant(target, effGain="Rush", name=RocketAugmerchant)
		return target
		
		
class SoulboundAshtongue(Minion):
	Class, race, name = "Neutral", "", "Soulbound Ashtongue"
	mana, attack, health = 1, 1, 4
	index = "BLACK_TEMPLE~Neutral~Minion~1~1~4~~Soulbound Ashtongue"
	requireTarget, effects, description = False, "", "Whenever this minion takes damage, also deal that amount to your hero"
	name_CN = "魂缚灰舌"
	trigBoard = Trig_SoulboundAshtongue		


class BonechewerBrawler(Minion):
	Class, race, name = "Neutral", "", "Bonechewer Brawler"
	mana, attack, health = 2, 2, 3
	index = "BLACK_TEMPLE~Neutral~Minion~2~2~3~~Bonechewer Brawler~Taunt"
	requireTarget, effects, description = False, "Taunt", "Taunt. Whenever this minion takes damage, gain +2 Attack"
	name_CN = "噬骨殴斗者"
	trigBoard = Trig_BonechewerBrawler


class ImprisonedVilefiend(Minion_Dormantfor2turns):
	Class, race, name = "Neutral", "Demon", "Imprisoned Vilefiend"
	mana, attack, health = 2, 3, 5
	index = "BLACK_TEMPLE~Neutral~Minion~2~3~5~Demon~Imprisoned Vilefiend~Rush"
	requireTarget, effects, description = False, "Rush", "Dormant for 2 turns. Rush"
	name_CN = "被禁锢的邪犬"


class MoargArtificer(Minion):
	Class, race, name = "Neutral", "Demon", "Mo'arg Artificer"
	mana, attack, health = 2, 2, 4
	index = "BLACK_TEMPLE~Neutral~Minion~2~2~4~Demon~Mo'arg Artificer"
	requireTarget, effects, description = False, "", "All minions take double damage from spells"
	name_CN = "莫尔葛工匠"
	trigBoard = Trig_MoargArtificer		


class RustswornInitiate(Minion):
	Class, race, name = "Neutral", "", "Rustsworn Initiate"
	mana, attack, health = 2, 2, 2
	index = "BLACK_TEMPLE~Neutral~Minion~2~2~2~~Rustsworn Initiate~Deathrattle"
	requireTarget, effects, description = False, "", "Deathrattle: Summon a 1/1 Impcaster with Spell Damage +1"
	name_CN = "锈誓新兵"
	deathrattle = Death_RustswornInitiate


class Impcaster(Minion):
	Class, race, name = "Neutral", "Demon", "Impcaster"
	mana, attack, health = 1, 1, 1
	index = "BLACK_TEMPLE~Neutral~Minion~1~1~1~Demon~Impcaster~Spell Damage~Uncollectible"
	requireTarget, effects, description = False, "Spell Damage", "Spell Damage +1"
	name_CN = "小鬼施法者"
	

class BlisteringRot(Minion):
	Class, race, name = "Neutral", "", "Blistering Rot"
	mana, attack, health = 3, 1, 2
	index = "BLACK_TEMPLE~Neutral~Minion~3~1~2~~Blistering Rot"
	requireTarget, effects, description = False, "", "At the end of your turn, summon a Rot with stats equal to this minion's"
	name_CN = "起泡的腐泥怪"
	trigBoard = Trig_BlisteringRot		


class LivingRot(Minion):
	Class, race, name = "Neutral", "", "Living Rot"
	mana, attack, health = 1, 1, 1
	index = "BLACK_TEMPLE~Neutral~Minion~1~1~1~~Living Rot~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "生命腐质"
	
	
class FrozenShadoweaver(Minion):
	Class, race, name = "Neutral", "", "Frozen Shadoweaver"
	mana, attack, health = 3, 4, 3
	index = "BLACK_TEMPLE~Neutral~Minion~3~4~3~~Frozen Shadoweaver~Battlecry"
	requireTarget, effects, description = True, "", "Battlecry: Freeze an enemy"
	name_CN = "冰霜织影者"
	def targetExists(self, choice=0):
		return self.selectableEnemyExists()
		
	def targetCorrect(self, target, choice=0):
		return (target.category == "Minion" or target.category == "Hero") and target.ID != self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.freeze(target)
		return target
		
		
class OverconfidentOrc(Minion):
	Class, race, name = "Neutral", "", "Overconfident Orc"
	mana, attack, health = 3, 1, 6
	index = "BLACK_TEMPLE~Neutral~Minion~3~1~6~~Overconfident Orc~Taunt"
	requireTarget, effects, description = False, "Taunt", "Taunt. While at full Health, this has +2 Attack"
	name_CN = "狂傲的兽人"
	def statCheckResponse(self):
		if self.onBoard and  not self.silenced and self.dmgTaken < 1: self.attack += 2

	
class TerrorguardEscapee(Minion):
	Class, race, name = "Neutral", "Demon", "Terrorguard Escapee"
	mana, attack, health = 3, 3, 7
	index = "BLACK_TEMPLE~Neutral~Minion~3~3~7~Demon~Terrorguard Escapee~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Summon three 1/1 Huntresses for your opponent"
	name_CN = "逃脱的恐惧卫士"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon([Huntress(self.Game, 3-self.ID) for _ in (0, 1, 2)], position=-1)
		

class Huntress(Minion):
	Class, race, name = "Neutral", "", "Huntress"
	mana, attack, health = 1, 1, 1
	index = "BLACK_TEMPLE~Neutral~Minion~1~1~1~~Huntress~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "女猎手"


class TeronGorefiend(Minion):
	Class, race, name = "Neutral", "", "Teron Gorefiend"
	mana, attack, health = 3, 3, 4
	index = "BLACK_TEMPLE~Neutral~Minion~3~3~4~~Teron Gorefiend~Battlecry~Deathrattle~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: Destroy all friendly minions. Deathrattle: Resummon all of them with +1/+1"
	name_CN = "塔隆血魔"
	deathrattle = Death_TeronGorefiend	#不知道两次触发战吼时亡语是否会记录两份，假设会
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		minionsDestroyed = [minion for minion in self.Game.minionsonBoard(self.ID) if minion != self]
		if minionsDestroyed:
			self.Game.kill(self, minionsDestroyed)
			minionsDestroyed = [type(minion) for minion in minionsDestroyed]
			for trig in self.deathrattles:
				if isinstance(trig, Death_TeronGorefiend):
					trig.savedObjs += minionsDestroyed


class BurrowingScorpid(Minion):
	Class, race, name = "Neutral", "Beast", "Burrowing Scorpid"
	mana, attack, health = 4, 5, 2
	index = "BLACK_TEMPLE~Neutral~Minion~4~5~2~Beast~Burrowing Scorpid~Battlecry"
	requireTarget, effects, description = True, "", "Battlecry: Deal 2 damage. If that kills the target, gain Stealth"
	name_CN = "潜地蝎"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.dealsDamage(target, 2)
			if target.health < 1 or target.dead == True: self.giveEnchant(self, effGain="Stealth", name=BurrowingScorpid)
		return target


class DisguisedWanderer(Minion):
	Class, race, name = "Neutral", "Demon", "Disguised Wanderer"
	mana, attack, health = 4, 3, 3
	index = "BLACK_TEMPLE~Neutral~Minion~4~3~3~Demon~Disguised Wanderer~Deathrattle"
	requireTarget, effects, description = False, "", "Deathrattle: Summon a 9/1 Inquisitor"
	name_CN = "变装游荡者"
	deathrattle = Death_DisguisedWanderer


class RustswornInquisitor(Minion):
	Class, race, name = "Neutral", "Demon", "Rustsworn Inquisitor"
	mana, attack, health = 4, 9, 1
	index = "BLACK_TEMPLE~Neutral~Minion~4~9~1~Demon~Rustsworn Inquisitor~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "锈誓审判官"
	
	
class FelfinNavigator(Minion):
	Class, race, name = "Neutral", "Murloc", "Felfin Navigator"
	mana, attack, health = 4, 4, 4
	index = "BLACK_TEMPLE~Neutral~Minion~4~4~4~Murloc~Felfin Navigator~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Give your other Murlocs +1/+1"
	name_CN = "邪鳍导航员"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.AOE_GiveEnchant(self.Game.minionsonBoard(self.ID, self, race="Murloc"), 1, 1, name=FelfinNavigator)
		
		
class Magtheridon(Minion):
	Class, race, name = "Neutral", "Demon", "Magtheridon"
	mana, attack, health = 4, 12, 12
	index = "BLACK_TEMPLE~Neutral~Minion~4~12~12~Demon~Magtheridon~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Dormant. Battlecry: Summon three 1/3 enemy Warders. When they die, destroy all minions and awaken"
	name_CN = "玛瑟里顿"
	
	def played(self, target=None, choice=0, mana=0, posinHand=-2, comment=""):
		self.health = self.health_max
		self.appears(firstTime=True)
		#理论上不会有任何角色死亡,可以跳过死亡结算
		for i in range(2 if "~Battlecry" in self.index and self.Game.effects[self.ID]["Battlecry x2"]> 0 else 1):
			self.whenEffective(target, "", choice, posinHand)
		self.Game.gathertheDead()
		
	def appears(self, firstTime=True):
		self.onBoard = True
		self.inHand = self.inDeck = self.dead = False
		self.enterBoardTurn = self.Game.numTurn
		self.mana = type(self).mana #Restore the minion's mana to original value.
		self.decideAttChances_base() #Decide base att chances, given Windfury and Mega Windfury
		if firstTime: #首次出场时会进行休眠，而且休眠状态会保持之前的随从buff。休眠体由每个不同的随从自己定义
			self.Game.transform(self, Magtheridon_Dormant(self.Game, self.ID, self), firstTime=True)
		else: #只有不是第一次出现在场上时才会执行这些函数
			if self.btn:
				self.btn.isPlayed, self.btn.card = True, self
				self.btn.placeIcons()
				self.btn.statChangeAni()
				self.btn.effectChangeAni()
			for trig in self.trigsBoard + self.deathrattles:
				trig.connect() #把(obj, signal)放入Game.trigsBoard中
			self.Game.sendSignal("MinionAppears", self.ID, self, None, 0, comment=firstTime)
			
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon([HellfireWarder(self.Game, 3-self.ID) for _ in (0, 1, 2)], position=-1)


class Magtheridon_Dormant(Dormant):
	Class, school, name = "Neutral", "", "Dormant Magtheridon"
	description = "Destroy 3 Warders to destroy all minions and awaken this"
	trigBoard = Trig_Magtheridon_Dormant


class HellfireWarder(Minion):
	Class, race, name = "Neutral", "", "Hellfire Warder"
	mana, attack, health = 1, 1, 3
	index = "BLACK_TEMPLE~Neutral~Minion~1~1~3~~Hellfire Warder~Uncollectible"
	requireTarget, effects, description = False, "", "(Magtheridon will destroy all minions and awaken after 3 Warders die)"
	name_CN = "地狱火典狱官"
	
	
class MaievShadowsong(Minion):
	Class, race, name = "Neutral", "", "Maiev Shadowsong"
	mana, attack, health = 4, 4, 3
	index = "BLACK_TEMPLE~Neutral~Minion~4~4~3~~Maiev Shadowsong~Battlecry~Legendary"
	requireTarget, effects, description = True, "", "Battlecry: Choose a minion. It goes Dormant for 2 turns"
	name_CN = "玛维影歌"
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		#需要随从在场并且还是随从形态
		if target and target.onBoard and target.category == "Minion":
			dormantForm = ImprisonedDormantForm(self.Game, target.ID, target) #假设让随从休眠可以保留其初始状态
			return self.Game.transform(target, dormantForm, firstTime=True)
		else: return target
		
		
class Replicatotron(Minion):
	Class, race, name = "Neutral", "Mech", "Replicat-o-tron"
	mana, attack, health = 4, 3, 3
	index = "BLACK_TEMPLE~Neutral~Minion~4~3~3~Mech~Replicat-o-tron"
	requireTarget, effects, description = False, "", "At the end of your turn, transform a neighbor into a copy of this"
	name_CN = "复制机器人"
	trigBoard = Trig_Replicatotron		


class RustswornCultist(Minion):
	Class, race, name = "Neutral", "", "Rustsworn Cultist"
	mana, attack, health = 4, 3, 3
	index = "BLACK_TEMPLE~Neutral~Minion~4~3~3~~Rustsworn Cultist~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Give your other minions 'Deathrattle: Summon a 1/1 Demon'"
	name_CN = "锈誓信徒"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.giveEnchant(self.Game.minionsonBoard(self.ID), trig=Death_RustswornCultist, trigType="Deathrattle")
		

class RustedDevil(Minion):
	Class, race, name = "Neutral", "Demon", "Rusted Devil"
	mana, attack, health = 1, 1, 1
	index = "BLACK_TEMPLE~Neutral~Minion~1~1~1~Demon~Rusted Devil~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "铁锈恶鬼"
	
	
class Alar(Minion):
	Class, race, name = "Neutral", "Elemental", "Al'ar"
	mana, attack, health = 5, 7, 3
	index = "BLACK_TEMPLE~Neutral~Minion~5~7~3~Elemental~Al'ar~Deathrattle~Legendary"
	requireTarget, effects, description = False, "", "Deathrattle: Summon a 0/3 Ashes of Al'ar that resurrects this minion on your next turn"
	name_CN = "奥"
	deathrattle = Death_Alar


class AshesofAlar(Minion):
	Class, race, name = "Neutral", "", "Ashes of Al'ar"
	mana, attack, health = 1, 0, 3
	index = "BLACK_TEMPLE~Neutral~Minion~1~0~3~~Ashes of Al'ar~Legendary~Uncollectible"
	requireTarget, effects, description = False, "", "At the start of your turn, transform this into Al'ar"
	name_CN = "奥的灰烬”"
	trigBoard = Trig_AshesofAlar		


class RuststeedRaider(Minion):
	Class, race, name = "Neutral", "", "Ruststeed Raider"
	mana, attack, health = 5, 1, 8
	index = "BLACK_TEMPLE~Neutral~Minion~5~1~8~~Ruststeed Raider~Taunt~Rush~Battlecry"
	requireTarget, effects, description = False, "Taunt,Rush", "Taunt, Rush. Battlecry: Gain +4 Attack this turn"
	name_CN = "锈骑劫匪"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.giveEnchant(self, statEnchant=Enchantment(4, 0, until=0, name=RuststeedRaider))
		
		
class WasteWarden(Minion):
	Class, race, name = "Neutral", "", "Waste Warden"
	mana, attack, health = 5, 3, 3
	index = "BLACK_TEMPLE~Neutral~Minion~5~3~3~~Waste Warden~Battlecry"
	requireTarget, effects, description = True, "", "Battlecry: Deal 3 damage to a minion and all others of the same minion category"
	name_CN = "废土守望者"
	
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.race != "" and target.onBoard
		
	#假设指定梦魇融合怪的时候会把场上所有有种族的随从都打一遍
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			if target.race == "":
				self.dealsDamage(target, 3)
			else: #Minion has category
				minionsoftheSameType = [target] #不重复计算目标和对一个随从的伤害
				for race in target.race.split(','): #A bunch of All category minions should be considered 
					for minion in self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2):
						if race in minion.race and minion != target and minion not in minionsoftheSameType:
							minionsoftheSameType.append(minion)
				self.AOE_Damage(minionsoftheSameType, [3 for minion in minionsoftheSameType])
		return target
		
		
class DragonmawSkyStalker(Minion):
	Class, race, name = "Neutral", "Dragon", "Dragonmaw Sky Stalker"
	mana, attack, health = 6, 5, 6
	index = "BLACK_TEMPLE~Neutral~Minion~6~5~6~Dragon~Dragonmaw Sky Stalker~Deathrattle"
	requireTarget, effects, description = False, "", "Deathrattle: Summon a 3/4 Dragonrider"
	name_CN = "龙喉巡天者"
	deathrattle = Death_DragonmawSkyStalker


class Dragonrider(Minion):
	Class, race, name = "Neutral", "", "Dragonrider"
	mana, attack, health = 3, 3, 4
	index = "BLACK_TEMPLE~Neutral~Minion~3~3~4~~Dragonrider~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "龙骑士"


#Assume spells countered by Counterspell still count as spells played
class KaelthasSunstrider(Minion):
	Class, race, name = "Neutral", "", "Kael'thas Sunstrider"
	mana, attack, health = 7, 4, 7
	index = "BLACK_TEMPLE~Neutral~Minion~7~4~7~~Kael'thas Sunstrider~Legendary"
	requireTarget, effects, description = False, "", "Every third spell you cast each turn costs (1)"
	name_CN = "凯尔萨斯·逐日者"
	trigBoard = Trig_KaelthasSunstrider
	

class ScavengingShivarra(Minion):
	Class, race, name = "Neutral", "Demon", "Scavenging Shivarra"
	mana, attack, health = 6, 6, 3
	index = "BLACK_TEMPLE~Neutral~Minion~6~6~3~Demon~Scavenging Shivarra~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Deal 6 damage randomly split among all other minions"
	name_CN = "食腐破坏魔"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for _ in range(6):
			if minions := self.Game.minionsAlive(1, exclude=self) + self.Game.minionsAlive(2, exclude=self):
				self.dealsDamage(numpyChoice(minions), 1)
			else: break
		
		
class BonechewerVanguard(Minion):
	Class, race, name = "Neutral", "", "Bonechewer Vanguard"
	mana, attack, health = 7, 4, 10
	index = "BLACK_TEMPLE~Neutral~Minion~7~4~10~~Bonechewer Vanguard~Taunt"
	requireTarget, effects, description = False, "Taunt", "Taunt. Whenever this minion takes damage, gain +2 Attack"
	name_CN = "噬骨先锋"
	trigBoard = Trig_BonechewerVanguard		


class SupremeAbyssal(Minion):
	Class, race, name = "Neutral", "Demon", "Supreme Abyssal"
	mana, attack, health = 8, 12, 12
	index = "BLACK_TEMPLE~Neutral~Minion~8~12~12~Demon~Supreme Abyssal"
	requireTarget, effects, description = False, "Can't Attack Hero", "Can't attack heroes"
	name_CN = "深渊至尊"
		
		
class ScrapyardColossus(Minion):
	Class, race, name = "Neutral", "Elemental", "Scrapyard Colossus"
	mana, attack, health = 10, 7, 7
	index = "BLACK_TEMPLE~Neutral~Minion~10~7~7~Elemental~Scrapyard Colossus~Taunt~Deathrattle"
	requireTarget, effects, description = False, "Taunt", "Taunt. Deathrattle: Summon a 7/7 Felcracked Colossus with Taunt"
	name_CN = "废料场巨像"
	deathrattle = Death_ScrapyardColossus


class FelcrackedColossus(Minion):
	Class, race, name = "Neutral", "Elemental", "Felcracked Colossus"
	mana, attack, health = 7, 7, 7
	index = "BLACK_TEMPLE~Neutral~Minion~7~7~7~Elemental~Felcracked Colossus~Taunt~Uncollectible"
	requireTarget, effects, description = False, "Taunt", "Taunt"
	name_CN = "邪爆巨像"
	

"""Demon Hunter Cards"""
class FuriousFelfin(Minion):
	Class, race, name = "Demon Hunter", "Murloc", "Furious Felfin"
	mana, attack, health = 2, 3, 2
	index = "BLACK_TEMPLE~Demon Hunter~Minion~2~3~2~Murloc~Furious Felfin~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: If your hero attacked this turn, gain +1 Attack and Rush"
	name_CN = "暴怒的邪鳍"
	
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.heroAtkTimesThisTurn[self.ID] > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Counters.heroAtkTimesThisTurn[self.ID] > 0:
			self.giveEnchant(self, 1, 0, effGain="Rush", name=FuriousFelfin)


class ImmolationAura(Spell):
	Class, school, name = "Demon Hunter", "Fel", "Immolation Aura"
	requireTarget, mana, effects = False, 2, ""
	index = "BLACK_TEMPLE~Demon Hunter~Spell~2~Fel~Immolation Aura"
	description = "Deal 1 damage to all minions twice"
	name_CN = "献祭光环"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		# 不知道法强随从中途死亡是否会影响伤害，假设不会
		damage = self.calcDamage(1)
		# 中间会结算强制死亡
		targets = self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)
		self.AOE_Damage(targets, [damage]*len(targets))
		self.Game.gathertheDead()
		targets = self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)
		self.AOE_Damage(targets, [damage]*len(targets))


class Netherwalker(Minion):
	Class, race, name = "Demon Hunter", "", "Netherwalker"
	mana, attack, health = 2, 2, 2
	index = "BLACK_TEMPLE~Demon Hunter~Minion~2~2~2~~Netherwalker~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Discover a Demon"
	name_CN = "虚无行者"
	poolIdentifier = "Demons as Demon Hunter"
	@classmethod
	def generatePool(cls, pools):
		classCards = {s : [] for s in pools.ClassesandNeutral}
		for card in pools.MinionswithRace["Demon"]:
			for Class in card.Class.split(','):
				classCards[Class].append(card)
		return ["Demons as "+Class for Class in pools.Classes], \
				[classCards[Class]+classCards["Neutral"] for Class in pools.Classes]
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverandGenerate(Netherwalker, comment, lambda : self.rngPool("Demons as " + classforDiscover(self)))


class FelSummoner(Minion):
	Class, race, name = "Demon Hunter", "", "Fel Summoner"
	mana, attack, health = 6, 8, 3
	index = "BLACK_TEMPLE~Demon Hunter~Minion~6~8~3~~Fel Summoner~Deathrattle"
	requireTarget, effects, description = False, "", "Deathrattle: Summon a random Demon from your hand"
	name_CN = "邪能召唤师"
	deathrattle = Death_FelSummoner


class KaynSunfury(Minion):
	Class, race, name = "Demon Hunter", "", "Kayn Sunfury"
	mana, attack, health = 4, 3, 4
	index = "BLACK_TEMPLE~Demon Hunter~Minion~4~3~4~~Kayn Sunfury~Charge~Legendary"
	requireTarget, effects, description = False, "Charge", "Charge. All friendly attacks ignore Taunt"
	name_CN = "凯恩日怒"
	aura = GameRuleAura_KaynSunfury
	
	
class Metamorphosis(Spell):
	Class, school, name = "Demon Hunter", "Fel", "Metamorphosis"
	requireTarget, mana, effects = False, 5, ""
	index = "BLACK_TEMPLE~Demon Hunter~Spell~5~Fel~Metamorphosis~Legendary"
	description = "Swap your Hero Power to 'Deal 4 damage'. After 2 uses, swap it back"
	name_CN = "恶魔变形"
	#不知道是否只是对使用两次英雄技能计数，而不一定要是那个特定的英雄技能
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		DemonicBlast(self.Game, self.ID, self.Game.powers[self.ID]).replacePower()


class DemonicBlast(Power):
	mana, name, requireTarget = 1, "Demonic Blast", True
	index = "Demon Hunter~Hero Power~1~Demonic Blast"
	description = "Deal 4 damage. (Two uses left!)"
	name_CN = "恶魔冲击"
	trigBoard = Trig_DemonicBlast
	def text(self): return self.calcDamage(4)
		
	def effect(self, target, choice=0):
		dmgTaker, damageActual = self.dealsDamage(target, self.calcDamage(4))
		if dmgTaker.health < 1 or dmgTaker.dead: return 1
		return 0


class ImprisonedAntaen(Minion_Dormantfor2turns):
	Class, race, name = "Demon Hunter", "Demon", "Imprisoned Antaen"
	mana, attack, health = 6, 10, 6
	index = "BLACK_TEMPLE~Demon Hunter~Minion~6~10~6~Demon~Imprisoned Antaen"
	requireTarget, effects, description = False, "", "Dormant for 2 turns. When this awakens, deal 10 damage randomly split among all enemies"
	name_CN = "被禁锢的安塔恩"
	def awakenEffect(self):
		side = 3 - self.ID
		for num in range(10):
			if objs := self.Game.charsAlive(side): self.dealsDamage(numpyChoice(objs), 1)
			else: break


class SkullofGuldan(Spell):
	Class, school, name = "Demon Hunter", "", "Skull of Gul'dan"
	requireTarget, mana, effects = False, 6, ""
	index = "BLACK_TEMPLE~Demon Hunter~Spell~6~~Skull of Gul'dan~Outcast"
	description = "Draw 3 cards. Outscast: Reduce their Cost by (3)"
	name_CN = "古尔丹之颅"
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.outcastcanTrig(self)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		outcastcanTrig = posinHand == 0 or posinHand == -1
		for _ in (0, 1, 2):
			card, mana, entersHand = self.Game.Hand_Deck.drawCard(self.ID)
			if outcastcanTrig and entersHand: ManaMod(card, by=-3).applies()
		
		
class PriestessofFury(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Priestess of Fury"
	mana, attack, health = 7, 6, 5
	index = "BLACK_TEMPLE~Demon Hunter~Minion~7~6~5~Demon~Priestess of Fury"
	requireTarget, effects, description = False, "", "At the end of your turn, deal 6 damage randomly split among all enemies"
	name_CN = "愤怒的女祭司"
	trigBoard = Trig_PriestessofFury


class CoilfangWarlord(Minion):
	Class, race, name = "Demon Hunter", "", "Coilfang Warlord"
	mana, attack, health = 8, 9, 5
	index = "BLACK_TEMPLE~Demon Hunter~Minion~8~9~5~~Coilfang Warlord~Rush~Deathrattle"
	requireTarget, effects, description = False, "Rush", "Rush. Deathrattle: Summon a 5/9 Warlord with Taunt"
	name_CN = "盘牙督军"
	deathrattle = Death_CoilfangWarlord

class ConchguardWarlord(Minion):
	Class, race, name = "Demon Hunter", "", "Conchguard Warlord"
	mana, attack, health = 8, 5, 9
	index = "BLACK_TEMPLE~Demon Hunter~Minion~8~5~9~~Conchguard Warlord~Taunt~Uncollectible"
	requireTarget, effects, description = False, "Taunt", "Taunt"
	name_CN = "螺盾督军"
	
	
class PitCommander(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Pit Commander"
	mana, attack, health = 9, 7, 9
	index = "BLACK_TEMPLE~Demon Hunter~Minion~9~7~9~Demon~Pit Commander~Taunt"
	requireTarget, effects, description = False, "Taunt", "Taunt. At the end of your turn, summon a Demon from your deck"
	name_CN = "深渊指挥官"
	trigBoard = Trig_PitCommander		


class FungalFortunes(Spell):
	Class, school, name = "Druid", "Nature", "Fungal Fortunes"
	requireTarget, mana, effects = False, 3, ""
	index = "BLACK_TEMPLE~Druid~Spell~3~Nature~Fungal Fortunes"
	description = "Draw 3 cards. Discard any minions drawn"
	name_CN = "真菌宝藏"
	#The minions will be discarded immediately before drawing the next card.
	#The discarding triggers triggers["Discarded"] and send signals.
	#If the hand is full, then no discard at all. The drawn cards vanish.	
	#The "cast when drawn" spells can take effect as usual
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		HD = self.Game.Hand_Deck
		ownDeck = HD.decks[self.ID]
		for _ in (0, 1, 2):
			if ownDeck:
				if ownDeck[-1].category == "Minion": HD.extractfromDeck(-1, self.ID)
				else: HD.drawCard(self.ID)
			else: break


class Ironbark(Spell):
	Class, school, name = "Druid", "Nature", "Ironbark"
	requireTarget, mana, effects = True, 2, ""
	index = "BLACK_TEMPLE~Druid~Spell~2~Nature~Ironbark"
	description = "Give a minion +1/+3 and Taunt. Costs (0) if you have at least 7 Mana Crystals"
	name_CN = "铁木树皮"
	trigHand = Trig_Ironbark		
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard
		
	def selfManaChange(self):
		#假设需要的是空水晶，暂时获得的水晶不算
		if self.inHand and self.Game.Manas.manasUpper[self.ID] > 6:
			self.mana = 0
			
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.giveEnchant(target, 1, 3, effGain="Taunt", name=Ironbark)
		return target


class ArchsporeMsshifn(Minion):
	Class, race, name = "Druid", "", "Archspore Msshi'fn"
	mana, attack, health = 3, 3, 4
	index = "BLACK_TEMPLE~Druid~Minion~3~3~4~~Archspore Msshi'fn~Taunt~Deathrattle~Legendary"
	requireTarget, effects, description = False, "Taunt", "Taunt. Deathrattle: Shuffle 'Msshi'fn Prime' into your deck"
	name_CN = "孢子首领姆希菲"
	deathrattle = Death_ArchsporeMsshifn


class MsshifnAttac_Option(Option):
	name, description = "Msshi'fn At'tac", "Summon a 9/9 with Taunt"
	mana, attack, health = 10, -1, -1
	isLegendary = True
	def available(self):
		return self.keeper.Game.space(self.keeper.ID) > 0

class MsshifnProtec_Option(Option):
	name, description = "Msshi'fn Pro'tec", "Summon a 9/9 with Rush"
	mana, attack, health = 10, -1, -1
	isLegendary = True
	def available(self):
		return self.keeper.Game.space(self.keeper.ID) > 0

class MsshifnPrime(Minion):
	Class, race, name = "Druid", "", "Msshi'fn Prime"
	mana, attack, health = 10, 9, 9
	index = "BLACK_TEMPLE~Druid~Minion~10~9~9~~Msshi'fn Prime~Taunt~Choose One~Legendary~Uncollectible"
	requireTarget, effects, description = False, "Taunt", "Taunt. Choose One- Summon a 9/9 Fungal Giant with Taunt; or Rush"
	name_CN = "终极姆希菲"
	options = (MsshifnAttac_Option, MsshifnProtec_Option)
	#如果有全选光环，只有一个9/9，其同时拥有突袭和嘲讽
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if choice == 0:
			self.summon(FungalGuardian(self.Game, self.ID))
		elif choice == 1:
			self.summon(FungalBruiser(self.Game, self.ID))
		elif choice < 0:
			self.summon(FungalGargantuan(self.Game, self.ID))
		

class FungalGuardian(Minion):
	Class, race, name = "Druid", "", "Fungal Guardian"
	mana, attack, health = 10, 9, 9
	index = "BLACK_TEMPLE~Druid~Minion~10~9~9~~Fungal Guardian~Taunt~Uncollectible"
	requireTarget, effects, description = False, "Taunt", "Taunt"
	

class FungalBruiser(Minion):
	Class, race, name = "Druid", "", "Fungal Bruiser"
	mana, attack, health = 10, 9, 9
	index = "BLACK_TEMPLE~Druid~Minion~10~9~9~~Fungal Bruiser~Rush~Uncollectible"
	requireTarget, effects, description = False, "Rush", "Rush"
	

class FungalGargantuan(Minion):
	Class, race, name = "Druid", "", "Fungal Gargantuan"
	mana, attack, health = 10, 9, 9
	index = "BLACK_TEMPLE~Druid~Minion~10~9~9~~Fungal Gargantuan~Taunt~Rush~Uncollectible"
	requireTarget, effects, description = False, "Taunt,Rush", "Taunt, Rush"


class Bogbeam(Spell):
	Class, school, name = "Druid", "", "Bogbeam"
	requireTarget, mana, effects = True, 3, ""
	index = "BLACK_TEMPLE~Druid~Spell~3~~Bogbeam"
	description = "Deal 3 damage to a minion. Costs (0) if you have at least 7 Mana Crystals"
	name_CN = "沼泽射线"
	trigHand = Trig_Bogbeam		
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard
		
	def selfManaChange(self):
		#假设需要的是空水晶，暂时获得的水晶不算
		if self.inHand and self.Game.Manas.manasUpper[self.ID] > 6:
			self.mana = 0
			
	def effCanTrig(self):
		self.effectViable = self.Game.Manas.manasUpper[self.ID] > 6
		
	def text(self): return self.calcDamage(3)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.dealsDamage(target, self.calcDamage(3))
		return target


class ImprisonedSatyr(Minion_Dormantfor2turns):
	Class, race, name = "Druid", "Demon", "Imprisoned Satyr"
	mana, attack, health = 3, 3, 3
	index = "BLACK_TEMPLE~Druid~Minion~3~3~3~Demon~Imprisoned Satyr"
	requireTarget, effects, description = False, "", "Dormant for 2 turns. When this awakens, reduce the Cost of a random minion in your hand by (5)"
	name_CN = "被禁锢的萨特"
	
	def awakenEffect(self):
		if cards := self.findCards4ManaReduction(lambda card: card.category == "Minion"):
			ManaMod(numpyChoice(cards), by=-5).applies()
		
		
class Germination(Spell):
	Class, school, name = "Druid", "Nature", "Germination"
	requireTarget, mana, effects = True, 4, ""
	index = "BLACK_TEMPLE~Druid~Spell~4~Nature~Germination"
	description = "Summon a copy of a friendly minion. Give the copy Taunt"
	name_CN = "萌芽分裂"
	def available(self):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.ID == self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.summon((Copy := target.selfCopy(target.ID, self)), position=target.pos+1)
			self.giveEnchant(Copy, effGain="Taunt", name=Germination)
		return target
		
		
class Overgrowth(Spell):
	Class, school, name = "Druid", "Nature", "Overgrowth"
	requireTarget, mana, effects = False, 4, ""
	index = "BLACK_TEMPLE~Druid~Spell~4~Nature~Overgrowth"
	description = "Gain two empty Mana Crystals"
	name_CN = "过度生长"
	#不知道满费用和9费时如何结算,假设不会给抽牌的衍生物
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if not self.Game.Manas.gainEmptyManaCrystal(2, self.ID):
			self.addCardtoHand(ExcessMana, self.ID)
		
		
class GlowflySwarm(Spell):
	Class, school, name = "Druid", "", "Glowfly Swarm"
	requireTarget, mana, effects = False, 5, ""
	index = "BLACK_TEMPLE~Druid~Spell~5~~Glowfly Swarm"
	description = "Summon a 2/2 Glowfly for each spell in your hand"
	name_CN = "萤火成群"
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def effCanTrig(self):
		self.effectViable = any(card.category == "Spell" and card != self for card in self.Game.Hand_Deck.hands[self.ID])
			
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		num = sum(card.category == "Spell" for card in self.Game.Hand_Deck.hands[self.ID])
		if num > 0: self.summon([Glowfly(self.Game, self.ID) for i in range(num)])
		

class Glowfly(Minion):
	Class, race, name = "Druid", "Beast", "Glowfly"
	mana, attack, health = 2, 2, 2
	index = "BLACK_TEMPLE~Druid~Minion~2~2~2~Beast~Glowfly~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "萤火虫"
	

class MarshHydra(Minion):
	Class, race, name = "Druid", "Beast", "Marsh Hydra"
	mana, attack, health = 7, 7, 7
	index = "BLACK_TEMPLE~Druid~Minion~7~7~7~Beast~Marsh Hydra~Rush"
	requireTarget, effects, description = False, "Rush", "Rush. After this attacks, add a random 8-Cost minion to your hand"
	name_CN = "沼泽多头蛇"
	trigBoard = Trig_MarshHydra
	poolIdentifier = "8-Cost Minions"
	@classmethod
	def generatePool(cls, pools):
		return "8-Cost Minions", pools.MinionsofCost[8]


class YsielWindsinger(Minion):
	Class, race, name = "Druid", "", "Ysiel Windsinger"
	mana, attack, health = 9, 5, 5
	index = "BLACK_TEMPLE~Druid~Minion~9~5~5~~Ysiel Windsinger~Legendary"
	requireTarget, effects, description = False, "", "Your spells cost (1)"
	name_CN = "伊谢尔风歌"
	aura = ManaAura_YsielWindsinger
	

"""Hunter Cards"""
class Helboar(Minion):
	Class, race, name = "Hunter", "Beast", "Helboar"
	mana, attack, health = 1, 2, 1
	index = "BLACK_TEMPLE~Hunter~Minion~1~2~1~Beast~Helboar~Deathrattle"
	requireTarget, effects, description = False, "", "Deathrattle: Give a random Beast in your hand +1/+1"
	name_CN = "地狱野猪"
	deathrattle = Death_Helboar


class ImprisonedFelmaw(Minion_Dormantfor2turns):
	Class, race, name = "Hunter", "Demon", "Imprisoned Felmaw"
	mana, attack, health = 2, 5, 4
	index = "BLACK_TEMPLE~Hunter~Minion~2~5~4~Demon~Imprisoned Felmaw"
	requireTarget, effects, description = False, "", "Dormant for 2 turns. When this awakens, attack a random enemy"
	name_CN = "被禁锢的魔喉"
	#假设这个攻击不会消耗随从的攻击机会
	def awakenEffect(self):
		targets = self.Game.charsAlive(3-self.ID)
		if targets: self.Game.battle(self, numpyChoice(targets), verifySelectable=False, useAttChance=False, resolveDeath=False)


class PackTactics(Secret):
	Class, school, name = "Hunter", "", "Pack Tactics"
	requireTarget, mana, effects = False, 2, ""
	index = "BLACK_TEMPLE~Hunter~Spell~2~~Pack Tactics~~Secret"
	description = "Secret: When a friendly minion is attacked, summon a 3/3 copy"
	name_CN = "集群战术"
	trigBoard = Trig_PackTactics


class ScavengersIngenuity(Spell):
	Class, school, name = "Hunter", "", "Scavenger's Ingenuity"
	requireTarget, mana, effects = False, 2, ""
	index = "BLACK_TEMPLE~Hunter~Spell~2~~Scavenger's Ingenuity"
	description = "Draw a Beast. Give it +2/+2"
	name_CN = "拾荒者的智慧"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		beast, mana, entersHand = self.drawCertainCard(lambda card: "Beast" in card.race)
		if entersHand: self.giveEnchant(beast, 2, 2, name=ScavengersIngenuity, add2EventinGUI=False)
		
		
class AugmentedPorcupine(Minion):
	Class, race, name = "Hunter", "Beast", "Augmented Porcupine"
	mana, attack, health = 3, 2, 4
	index = "BLACK_TEMPLE~Hunter~Minion~3~2~4~Beast~Augmented Porcupine~Deathrattle"
	requireTarget, effects, description = False, "", "Deathrattle: Deals this minion's Attack damage randomly split among all enemies"
	name_CN = "强能箭猪"
	deathrattle = Death_AugmentedPorcupine


class ZixorApexPredator(Minion):
	Class, race, name = "Hunter", "Beast", "Zixor, Apex Predator"
	mana, attack, health = 3, 2, 4
	index = "BLACK_TEMPLE~Hunter~Minion~3~2~4~Beast~Zixor, Apex Predator~Rush~Deathrattle~Legendary"
	requireTarget, effects, description = False, "Rush", "Rush. Deathrattle: Shuffle 'Zixor Prime' into your deck"
	name_CN = "顶级捕食者兹克索尔"
	deathrattle = Death_ZixorApexPredator


class ZixorPrime(Minion):
	Class, race, name = "Hunter", "Beast", "Zixor Prime"
	mana, attack, health = 8, 4, 4
	index = "BLACK_TEMPLE~Hunter~Minion~8~4~4~Beast~Zixor Prime~Rush~Battlecry~Legendary~Uncollectible"
	requireTarget, effects, description = False, "Rush", "Rush. Battlecry: Summon 3 copies of this minion"
	name_CN = "终极兹克索尔"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.onBoard or self.inHand: #假设已经死亡时不会召唤复制
			self.summon([self.selfCopy(self.ID, self) for _ in (0, 1, 2)])
		
		
class MokNathalLion(Minion):
	Class, race, name = "Hunter", "Beast", "Mok'Nathal Lion"
	mana, attack, health = 4, 5, 2
	index = "BLACK_TEMPLE~Hunter~Minion~4~5~2~Beast~Mok'Nathal Lion~Rush~Battlecry"
	requireTarget, effects, description = True, "Rush", "Rush. Battlecry: Choose a friendly minion. Gain a copy of its Deathrattle"
	name_CN = "莫克纳萨将狮"
	def effCanTrig(self):
		self.effectViable = self.targetExists()
		
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.ID == self.ID and target != self and target.onBoard and target.deathrattles != []
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			for trig in target.deathrattles: self.getsTrig(trig.selfCopy(self), trigType="Deathrattle", connect=self.onBoard)
		return target
		
		
class ScrapShot(Spell):
	Class, school, name = "Hunter", "", "Scrap Shot"
	requireTarget, mana, effects = True, 4, ""
	index = "BLACK_TEMPLE~Hunter~Spell~4~~Scrap Shot"
	description = "Deal 3 damage. Give a random Beast in your hand +3/+3"
	name_CN = "废铁射击"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.dealsDamage(target, self.calcDamage(3))
			if beasts := [card for card in self.Game.Hand_Deck.hands[self.ID] if "Beast" in card.race]:
				self.giveEnchant(numpyChoice(beasts), 3, 3, name=ScrapShot, add2EventinGUI=False)
		return target
		
		
class BeastmasterLeoroxx(Minion):
	Class, race, name = "Hunter", "", "Beastmaster Leoroxx"
	mana, attack, health = 8, 5, 5
	index = "BLACK_TEMPLE~Hunter~Minion~8~5~5~~Beastmaster Leoroxx~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: Summon 3 Beasts from your hand"
	name_CN = "兽王莱欧洛克斯"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		refMinion = self
		for _ in (0, 1, 2):
			if not (refMinion := self.try_SummonfromHand(refMinion.pos + 1, func=lambda card: "Beast" in card.race)): break
		
		
class NagrandSlam(Spell):
	Class, school, name = "Hunter", "", "Nagrand Slam"
	requireTarget, mana, effects = False, 10, ""
	index = "BLACK_TEMPLE~Hunter~Spell~10~~Nagrand Slam"
	description = "Summon four 3/5 Clefthoofs that attack random enemies"
	name_CN = "纳格兰大冲撞"
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		game = self.Game
		clefthoofs = [Clefthoof(game, self.ID) for _ in (0, 1, 2, 3)]
		self.summon(clefthoofs)
		for clefthoof in clefthoofs:
			#Clefthoofs must be living to initiate attacks
			if clefthoof.onBoard and clefthoof.health > 0 and not clefthoof.dead:
				if targets := game.charsAlive(3-self.ID):
					game.battle(clefthoof, numpyChoice(targets), verifySelectable=False, useAttChance=True, resolveDeath=False) #攻击会消耗攻击机会
				else: break
		

class Clefthoof(Minion):
	Class, race, name = "Hunter", "Beast", "Clefthoof"
	mana, attack, health = 4, 3, 5
	index = "BLACK_TEMPLE~Hunter~Minion~4~3~5~Beast~Clefthoof~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "裂蹄牛"
	

"""Mage Cards"""
class Evocation(Spell):
	Class, school, name = "Mage", "Arcane", "Evocation"
	requireTarget, mana, effects = False, 2, ""
	index = "BLACK_TEMPLE~Mage~Spell~2~Arcane~Evocation~Legendary"
	description = "Fill your hand with random Mage spells. At the end of your turn, discard them"
	name_CN = "唤醒"
	poolIdentifier = "Mage Spells"
	@classmethod
	def generatePool(cls, pools):
		return "Mage Spells", [card for card in pools.ClassCards["Mage"] if card.category == "Spell"]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		pool = tuple(self.rngPool("Mage Spells"))
		while curGame.Hand_Deck.handNotFull(self.ID):
			spell = numpyChoice(pool)(curGame, self.ID)
			spell.trigsHand.append(Trig_Evocation(spell))
			self.addCardtoHand(spell, self.ID)
		

class FontofPower(Spell):
	Class, school, name = "Mage", "Arcane", "Font of Power"
	requireTarget, mana, effects = False, 1, ""
	index = "BLACK_TEMPLE~Mage~Spell~1~Arcane~Font of Power"
	description = "Discover a Mage minion. If your deck has no minions, keep all 3"
	name_CN = "能量之泉"
	poolIdentifier = "Mage Minions"
	@classmethod
	def generatePool(cls, pools):
		return "Mage Minions", [card for card in pools.ClassCards["Mage"] if card.category == "Minion"]
		
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.noMinionsinDeck(self.ID)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		pool = self.rngPool("Mage Minions")
		if curGame.Hand_Deck.noMinionsinDeck(self.ID):
			self.addCardtoHand(numpyChoice(pool, 3, replace=False), self.ID, byDiscover=True)
		else: self.discoverandGenerate(FontofPower, comment, lambda : pool)


class ApexisSmuggler(Minion):
	Class, race, name = "Mage", "", "Apexis Smuggler"
	mana, attack, health = 2, 2, 3
	index = "BLACK_TEMPLE~Mage~Minion~2~2~3~~Apexis Smuggler"
	requireTarget, effects, description = False, "", "After you play a Secret, Discover a spell"
	name_CN = "埃匹希斯走私犯"
	trigBoard = Trig_ApexisSmuggler
	poolIdentifier = "Mage Spells"
	@classmethod
	def generatePool(cls, pools):
		return [Class + " Spells" for Class in pools.Classes], \
			   [[card for card in pools.ClassCards[Class] if card.category == "Spell"] for Class in pools.Classes]


class AstromancerSolarian(Minion):
	Class, race, name = "Mage", "", "Astromancer Solarian"
	mana, attack, health = 2, 3, 2
	index = "BLACK_TEMPLE~Mage~Minion~2~3~2~~Astromancer Solarian~Spell Damage~Deathrattle~Legendary"
	requireTarget, effects, description = False, "Spell Damage", "Spell Damage +1. Deathrattle: Shuffle 'Solarian Prime' into your deck"
	name_CN = "星术师索兰莉安"
	deathrattle = Death_AstromancerSolarian


class SolarianPrime(Minion):
	Class, race, name = "Mage", "Demon", "Solarian Prime"
	mana, attack, health = 9, 7, 7
	index = "BLACK_TEMPLE~Mage~Minion~9~7~7~Demon~Solarian Prime~Spell Damage~Battlecry~Legendary~Uncollectible"
	requireTarget, effects, description = False, "Spell Damage", "Spell Damage +1. Battlecry: Cast 5 random Mage spells (target enemies if possible)"
	name_CN = "终极索兰莉安"
	poolIdentifier = "Mage Spells"
	@classmethod
	def generatePool(cls, pools):
		return "Mage Spells", [card for card in pools.ClassCards["Mage"] if card.category == "Spell"]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for i in range(5):
			numpyChoice(self.rngPool("Mage Spells"))(self.Game, self.ID).cast(func=lambda obj: obj.ID != self.ID)
			self.Game.gathertheDead(decideWinner=True)
		
		
class IncantersFlow(Spell):
	Class, school, name = "Mage", "Arcane", "Incanter's Flow"
	requireTarget, mana, effects = False, 3, ""
	index = "BLACK_TEMPLE~Mage~Spell~3~Arcane~Incanter's Flow"
	description = "Reduce the Cost of spells in your deck by (1)"
	name_CN = "咒术洪流"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for card in self.Game.Hand_Deck.decks[self.ID][:]:
			if card.category == "Spell": ManaMod(card, by=-1).applies()


class Starscryer(Minion):
	Class, race, name = "Mage", "", "Starscryer"
	mana, attack, health = 2, 3, 1
	index = "BLACK_TEMPLE~Mage~Minion~2~3~1~~Starscryer~Deathrattle"
	requireTarget, effects, description = False, "", "Deathrattle: Draw a spell"
	name_CN = "星占师"
	deathrattle = Death_Starscryer


class ImprisonedObserver(Minion_Dormantfor2turns):
	Class, race, name = "Mage", "Demon", "Imprisoned Observer"
	mana, attack, health = 3, 4, 5
	index = "BLACK_TEMPLE~Mage~Minion~3~4~5~Demon~Imprisoned Observer"
	requireTarget, effects, description = False, "", "Dormant for 2 turns. When this awakens, deal 2 damage to all enemy minions"
	name_CN = "被禁锢的眼魔"
	
	def awakenEffect(self):
		targets = self.Game.minionsonBoard(3-self.ID)
		self.AOE_Damage(targets, [2]*len(targets))


class NetherwindPortal(Secret):
	Class, school, name = "Mage", "Arcane", "Netherwind Portal"
	requireTarget, mana, effects = False, 3, ""
	index = "BLACK_TEMPLE~Mage~Spell~3~Arcane~Netherwind Portal~~Secret"
	description = "Secret: After your opponent casts a spell, summon a random 4-Cost minion"
	name_CN = "虚空之风传送门"
	trigBoard = Trig_NetherwindPortal
	poolIdentifier = "4-Cost Minions to Summon"
	@classmethod
	def generatePool(cls, pools):
		return "4-Cost Minions to Summon", pools.MinionsofCost[4]

		
class ApexisBlast(Spell):
	Class, school, name = "Mage", "", "Apexis Blast"
	requireTarget, mana, effects = True, 5, ""
	index = "BLACK_TEMPLE~Mage~Spell~5~~Apexis Blast"
	description = "Deal 5 damage. If your deck has no minions, summon a random 5-Cost minion"
	name_CN = "埃匹希斯冲击"
	poolIdentifier = "5-Cost Minions to Summon"
	@classmethod
	def generatePool(cls, pools):
		return "5-Cost Minions to Summon", pools.MinionsofCost[5]
		
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.noMinionsinDeck(self.ID)
		
	def text(self): return self.calcDamage(5)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.dealsDamage(target, self.calcDamage(5))
			if self.Game.Hand_Deck.noMinionsinDeck(self.ID):
				self.summon(numpyChoice(self.rngPool("5-Cost Minions to Summon"))(self.Game, self.ID))
		return target
		
		
class DeepFreeze(Spell):
	Class, school, name = "Mage", "Frost", "Deep Freeze"
	requireTarget, mana, effects = True, 8, ""
	index = "BLACK_TEMPLE~Mage~Spell~8~Frost~Deep Freeze"
	description = "Freeze an enemy. Summon two 3/6 Water Elementals"
	name_CN = "深度冻结"
	def available(self):
		return self.selectableEnemyExists()
		
	def targetCorrect(self, target, choice=0):
		return (target.category == "Minion" or target.category == "Hero") and target.ID != self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.freeze(target)
			self.summon([WaterElemental_Basic(self.Game, self.ID) for _ in (0, 1)])
		return target
		

"""Paladin Cards"""
class ImprisonedSungill(Minion_Dormantfor2turns):
	Class, race, name = "Paladin", "Murloc", "Imprisoned Sungill"
	mana, attack, health = 1, 2, 1
	index = "BLACK_TEMPLE~Paladin~Minion~1~2~1~Murloc~Imprisoned Sungill"
	requireTarget, effects, description = False, "", "Dormant for 2 turns. When this awakens, Summon two 1/1 Murlocs"
	name_CN = "被禁锢的阳鳃鱼人"
	
	def awakenEffect(self):
		self.summon([SungillStreamrunner(self.Game, self.ID) for _ in (0, 1)], relative="<>")

class SungillStreamrunner(Minion):
	Class, race, name = "Paladin", "Murloc", "Sungill Streamrunner"
	mana, attack, health = 1, 1, 1
	index = "BLACK_TEMPLE~Paladin~Minion~1~1~1~Murloc~Sungill Streamrunner~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "阳鳃士兵"
	
	
class AldorAttendant(Minion):
	Class, race, name = "Paladin", "", "Aldor Attendant"
	mana, attack, health = 1, 1, 3
	index = "BLACK_TEMPLE~Paladin~Minion~1~1~3~~Aldor Attendant~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Reduce the Cost of your Librams by (1) this game"
	name_CN = "奥尔多侍从"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		GameManaAura_AldorAttendant(self.Game, self.ID).auraAppears()
		
		
class HandofAdal(Spell):
	Class, school, name = "Paladin", "Holy",  "Hand of A'dal"
	requireTarget, mana, effects = True, 2, ""
	index = "BLACK_TEMPLE~Paladin~Spell~2~Holy~Hand of A'dal"
	description = "Give a minion +2/+1. Draw a card"
	name_CN = "阿达尔之手"
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.giveEnchant(target, 2, 1, name=HandofAdal)
			self.Game.Hand_Deck.drawCard(self.ID)
		return target


class MurgurMurgurgle(Minion):
	Class, race, name = "Paladin", "Murloc", "Murgur Murgurgle"
	mana, attack, health = 2, 2, 1
	index = "BLACK_TEMPLE~Paladin~Minion~2~2~1~Murloc~Murgur Murgurgle~Divine Shield~Deathrattle~Legendary"
	requireTarget, effects, description = False, "Divine Shield", "Divine Shield. Deathrattle: Shuffle 'Murgurgle Prime' into your deck"
	name_CN = "莫戈尔·莫戈尔格"
	deathrattle = Death_MurgurMurgurgle

class MurgurglePrime(Minion):
	Class, race, name = "Paladin", "Murloc", "Murgurgle Prime"
	mana, attack, health = 8, 6, 3
	index = "BLACK_TEMPLE~Paladin~Minion~8~6~3~Murloc~Murgurgle Prime~Divine Shield~Battlecry~Legendary~Uncollectible"
	requireTarget, effects, description = False, "Divine Shield", "Divine Shield. Battlecry: Summon 4 random Murlocs. Give them Divine Shield"
	name_CN = "终极莫戈尔格"
	poolIdentifier = "Murlocs to Summon"
	@classmethod
	def generatePool(cls, pools):
		return "Murlocs to Summon", pools.MinionswithRace["Murloc"]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		murlocs = [murloc(self.Game, self.ID) for murloc in numpyChoice(self.rngPool("Murlocs to Summon"), 4, replace=True)]
		self.summon(murlocs, relative="<>")
		self.AOE_GiveEnchant(murlocs, effGain="Divine Shield", name=MurgurglePrime)
		
		
class LibramofWisdom(Spell):
	Class, school, name = "Paladin", "Holy",  "Libram of Wisdom"
	requireTarget, mana, effects = True, 2, ""
	index = "BLACK_TEMPLE~Paladin~Spell~2~Holy~Libram of Wisdom"
	description = "Give a minion +1/+1 and 'Deathrattle: Add a 'Libram of Wisdom' spell to your hand'"
	name_CN = "智慧圣契"
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and (target.onBoard or target.inHand):
			self.giveEnchant(target, 1, 1, trig=Death_LibramofWisdom, trigType="Deathrattle", connect=target.onBoard, name=LibramofWisdom)
		return target
		

class UnderlightAnglingRod(Weapon):
	Class, name, description = "Paladin", "Underlight Angling Rod", "After your hero attacks, add a random Murloc to your hand"
	mana, attack, durability, effects = 3, 3, 2, ""
	index = "BLACK_TEMPLE~Paladin~Weapon~3~3~2~Underlight Angling Rod"
	name_CN = "幽光鱼竿"
	trigBoard = Trig_UnderlightAnglingRod
	poolIdentifier = "Murlocs"
	@classmethod
	def generatePool(cls, pools):
		return "Murlocs", pools.MinionswithRace["Murloc"]


class AldorTruthseeker(Minion):
	Class, race, name = "Paladin", "", "Aldor Truthseeker"
	mana, attack, health = 5, 4, 6
	index = "BLACK_TEMPLE~Paladin~Minion~5~4~6~~Aldor Truthseeker~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Reduce the Cost of your Librams by (2) this game"
	name_CN = "奥尔多真理追寻者"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		GameManaAura_AldorTruthseeker(self.Game, self.ID).auraAppears()
		
		
class LibramofJustice(Spell):
	Class, school, name = "Paladin", "Holy",  "Libram of Justice"
	requireTarget, mana, effects = False, 5, ""
	index = "BLACK_TEMPLE~Paladin~Spell~5~Holy~Libram of Justice"
	description = "Equip a 1/4 weapon. Change the Health of all enemy minions to 1"
	name_CN = "正义圣契"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.equipWeapon(OverdueJustice(self.Game, self.ID))
		self.AOE_SetStat(self.Game.minionsonBoard(3-self.ID), newHealth=1, name=LibramofJustice)
		

class OverdueJustice(Weapon):
	Class, name, description = "Paladin", "Overdue Justice", ""
	mana, attack, durability, effects = 1, 1, 4, ""
	index = "BLACK_TEMPLE~Paladin~Weapon~1~1~4~Overdue Justice~Uncollectible"
	name_CN = "迟到的正义"
	

class LadyLiadrin(Minion):
	Class, race, name = "Paladin", "", "Lady Liadrin"
	mana, attack, health = 7, 4, 6
	index = "BLACK_TEMPLE~Paladin~Minion~7~4~6~~Lady Liadrin~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: Add a copy of each spell you cast on friendly characters this game to your hand"
	name_CN = "女伯爵莉亚德琳"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		pool = self.Game.Counters.spellsonFriendliesThisGame[self.ID]
		spells = list(numpyChoice(pool, min(self.Game.Hand_Deck.spaceinHand(self.ID), len(pool)), replace=False))
		if spells: self.addCardtoHand(spells, self.ID)
		
		
class LibramofHope(Spell):
	Class, school, name = "Paladin", "Holy", "Libram of Hope"
	requireTarget, mana, effects = True, 9, ""
	index = "BLACK_TEMPLE~Paladin~Spell~9~Holy~Libram of Hope"
	description = "Restore 8 Health. Summon an 8/8 with Guardian with Taunt and Divine Shield"
	name_CN = "希望圣契"
	def text(self): return self.calcHeal(8)
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.restoresHealth(target, self.calcHeal(8))
			self.summon(AncientGuardian(self.Game, self.ID))
		return target
		

class AncientGuardian(Minion):
	Class, race, name = "Paladin", "", "Ancient Guardian"
	mana, attack, health = 8, 8, 8
	index = "BLACK_TEMPLE~Paladin~Minion~8~8~8~~Ancient Guardian~Taunt~Divine Shield~Uncollectible"
	requireTarget, effects, description = False, "Taunt,Divine Shield", "Taunt, Divine Shield"
	name_CN = "远古守卫"
	

"""Priest Cards"""
class ImprisonedHomunculus(Minion_Dormantfor2turns):
	Class, race, name = "Priest", "Demon", "Imprisoned Homunculus"
	mana, attack, health = 1, 2, 5
	index = "BLACK_TEMPLE~Priest~Minion~1~2~5~Demon~Imprisoned Homunculus~Taunt"
	requireTarget, effects, description = False, "Taunt", "Dormant for 2 turns. Taunt"
	name_CN = "被禁锢的矮劣魔"

	
class ReliquaryofSouls(Minion):
	Class, race, name = "Priest", "", "Reliquary of Souls"
	mana, attack, health = 1, 1, 3
	index = "BLACK_TEMPLE~Priest~Minion~1~1~3~~Reliquary of Souls~Lifesteal~Deathrattle~Legendary"
	requireTarget, effects, description = False, "Lifesteal", "Lifesteal. Deathrattle: Shuffle 'Leliquary Prime' into your deck"
	name_CN = "灵魂之匣"
	deathrattle = Death_ReliquaryofSouls

class ReliquaryPrime(Minion):
	Class, race, name = "Priest", "", "Reliquary Prime"
	mana, attack, health = 7, 6, 8
	index = "BLACK_TEMPLE~Priest~Minion~7~6~8~~Reliquary Prime~Taunt~Lifesteal~Legendary~Uncollectible"
	requireTarget, effects, description = False, "Taunt,Lifesteal,Enemy Evasive", "Taunt, Lifesteal. Only you can target this with spells and Hero Powers"
	name_CN = "终极魂匣"
	
	
class Renew(Spell):
	Class, school, name = "Priest", "Holy", "Renew"
	requireTarget, mana, effects = True, 2, ""
	index = "BLACK_TEMPLE~Priest~Spell~2~Holy~Renew"
	description = "Restore 3 Health. Discover a spell"
	name_CN = "复苏"
	poolIdentifier = "Priest Spells"
	@classmethod
	def generatePool(cls, pools):
		return [Class+" Spells" for Class in pools.Classes], \
				[[card for card in pools.ClassCards[Class] if card.category == "Spell"] for Class in pools.Classes]
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.restoresHealth(target, self.calcHeal(3))
			self.discoverandGenerate(Renew, comment, lambda : self.rngPool(classforDiscover(self) + " Spells"))
		return target
		
		
class DragonmawSentinel(Minion):
	Class, race, name = "Priest", "", "Dragonmaw Sentinel"
	mana, attack, health = 2, 1, 4
	index = "BLACK_TEMPLE~Priest~Minion~2~1~4~~Dragonmaw Sentinel~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: If you're holding a Dragon, gain +1 Attack and Lifesteal"
	name_CN = "龙喉哨兵"
	
	def effCanTrig(self): #Friendly characters are always selectable.
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Hand_Deck.holdingDragon(self.ID):
			self.giveEnchant(self, 1, 0, effGain="Lifesteal", name=DragonmawSentinel)
		
		
class SethekkVeilweaver(Minion):
	Class, race, name = "Priest", "", "Sethekk Veilweaver"
	mana, attack, health = 2, 2, 3
	index = "BLACK_TEMPLE~Priest~Minion~2~2~3~~Sethekk Veilweaver"
	requireTarget, effects, description = False, "", "After you cast a spell on a minion, add a Priest spell to your hand"
	name_CN = "塞泰克织巢者"
	poolIdentifier = "Priest Spells"
	@classmethod
	def generatePool(cls, pools):
		return "Priest Spells", [card for card in pools.ClassCards["Priest"] if card.category == "Spell"]
		
	trigBoard = Trig_SethekkVeilweaver		


class Apotheosis(Spell):
	Class, school, name = "Priest", "Holy", "Apotheosis"
	requireTarget, mana, effects = True, 3, ""
	index = "BLACK_TEMPLE~Priest~Spell~3~Holy~Apotheosis"
	description = "Give a minion +2/+3 and Lifesteal"
	name_CN = "神圣化身"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.giveEnchant(target, 2, 3, effGain="Lifesteal", name=Apotheosis)
		return target
		
		
class DragonmawOverseer(Minion):
	Class, race, name = "Priest", "", "Dragonmaw Overseer"
	mana, attack, health = 3, 2, 2
	index = "BLACK_TEMPLE~Priest~Minion~3~2~2~~Dragonmaw Overseer"
	requireTarget, effects, description = False, "", "At the end of your turn, give another friendly minion +2/+2"
	name_CN = "龙喉监工"
	trigBoard = Trig_DragonmawOverseer		


class PsycheSplit(Spell):
	Class, school, name = "Priest", "Shadow", "Psyche Split"
	requireTarget, mana, effects = True, 5, ""
	index = "BLACK_TEMPLE~Priest~Spell~5~Shadow~Psyche Split"
	description = "Give a minion +1/+2. Summon a copy of it"
	name_CN = "心灵分裂"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.giveEnchant(target, 1, 2, name=PsycheSplit)
			self.summon(target.selfCopy(target.ID, self), position=target.pos+1)
		return target
		
		
class SkeletalDragon(Minion):
	Class, race, name = "Priest", "Dragon", "Skeletal Dragon"
	mana, attack, health = 7, 4, 9
	index = "BLACK_TEMPLE~Priest~Minion~7~4~9~Dragon~Skeletal Dragon~Taunt"
	requireTarget, effects, description = False, "Taunt", "Taunt. At the end of your turn, add a Dragon to your hand"
	name_CN = "骸骨巨龙"
	poolIdentifier = "Dragons"
	@classmethod
	def generatePool(cls, pools):
		return "Dragons", pools.MinionswithRace["Dragon"]
		
	trigBoard = Trig_SkeletalDragon		


class SoulMirror(Spell):
	Class, school, name = "Priest", "Shadow", "Soul Mirror"
	requireTarget, mana, effects = False, 7, ""
	index = "BLACK_TEMPLE~Priest~Spell~7~Shadow~Soul Mirror~Legendary"
	description = "Summon copies of enemy minions. They attack their copies"
	name_CN = "灵魂之镜"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if minions := self.Game.minionsonBoard(3-self.ID):
			pairs = [minions, [minion.selfCopy(self.ID, self) for minion in minions]]
			if self.summon(pairs[1]):
				for minion, Copy in zip(pairs[0], pairs[1]):
					if minion.onBoard and minion.health > 0 and not minion.dead and Copy.onBoard and Copy.health > 0 and not Copy.dead:
						#def battle(self, subject, target, verifySelectable=True, useAttChance=True, resolveDeath=True, resetRedirTrig=True)
						self.Game.battle(Copy, minion, verifySelectable=False, useAttChance=False, resolveDeath=False, resetRedirTrig=True)
		

"""Rogue Cards"""
class BlackjackStunner(Minion):
	Class, race, name = "Rogue", "", "Blackjack Stunner"
	mana, attack, health = 1, 1, 2
	index = "BLACK_TEMPLE~Rogue~Minion~1~1~2~~Blackjack Stunner~Battlecry"
	requireTarget, effects, description = True, "", "Battlecry: If you control a Secret, return a minion to its owner's hand. It costs (1) more"
	name_CN = "钉棍终结者"
	def effCanTrig(self):
		self.effectViable = self.Game.Secrets.secrets[self.ID] != []
		
	def needTarget(self, choice=0):
		return self.Game.Secrets.secrets[self.ID] != []
		
	def targetExists(self, choice=0):
		return self.selectableMinionExists(choice)
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		#假设第二次生效时不会不在场上的随从生效
		if target and target.onBoard:
			#假设那张随从在进入手牌前接受-2费效果。可以被娜迦海巫覆盖。
			manaMod = ManaMod(target, by=+1)
			self.Game.returnObj2Hand(target, deathrattlesStayArmed=False, manaMod=manaMod)
		return target
		
		
class Spymistress(Minion):
	Class, race, name = "Rogue", "", "Spymistress"
	mana, attack, health = 1, 3, 1
	index = "BLACK_TEMPLE~Rogue~Minion~1~3~1~~Spymistress~Stealth"
	requireTarget, effects, description = False, "Stealth", "Stealth"
	name_CN = "间谍女郎"
	

class Ambush(Secret):
	Class, school, name = "Rogue", "", "Ambush"
	requireTarget, mana, effects = False, 2, ""
	index = "BLACK_TEMPLE~Rogue~Spell~2~~Ambush~~Secret"
	description = "Secret: After your opponent plays a minion, summon a 2/3 Ambusher with Poisonous"
	name_CN = "伏击"
	trigBoard = Trig_Ambush

class BrokenAmbusher(Minion):
	Class, race, name = "Rogue", "", "Broken Ambusher"
	mana, attack, health = 2, 2, 3
	index = "BLACK_TEMPLE~Rogue~Minion~2~2~3~~Broken Ambusher~Poisonous~Uncollectible"
	requireTarget, effects, description = False, "Poisonous", "Poisonous"
	name_CN = "破碎者伏兵"
	

class AshtongueSlayer(Minion):
	Class, race, name = "Rogue", "", "Ashtongue Slayer"
	mana, attack, health = 2, 3, 2
	index = "BLACK_TEMPLE~Rogue~Minion~2~3~2~~Ashtongue Slayer~Battlecry"
	requireTarget, effects, description = True, "", "Battlecry: Give a Stealthed minion +3 Attack and Immune this turn"
	name_CN = "灰舌杀手"
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists(choice)
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target != self and (target.effects["Stealth"] > 0 or target.effects["Temp Stealth"] > 0) and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: self.giveEnchant(target, statEnchant=Enchantment(3, 0, until=0, name=AshtongueSlayer),
							 				effectEnchant=Enchantment(effGain="Immune", until=0, name=AshtongueSlayer))
		return target


class Bamboozle(Secret):
	Class, school, name = "Rogue", "", "Bamboozle"
	requireTarget, mana, effects = False, 2, ""
	index = "BLACK_TEMPLE~Rogue~Spell~2~~Bamboozle~~Secret"
	description = "Secret: When one of your minions is attacked, transform it into a random one that costs (3) more"
	name_CN = "偷天换日"
	trigBoard = Trig_Bamboozle
	poolIdentifier = "3-Cost Minions to Summon"
	@classmethod
	def generatePool(cls, pools):
		return ["%d-Cost Minions to Summon" % cost for cost in pools.MinionsofCost.keys()], \
			   list(pools.MinionsofCost.values())
	

class DirtyTricks(Secret):
	Class, school, name = "Rogue", "", "Dirty Tricks"
	requireTarget, mana, effects = False, 2, ""
	index = "BLACK_TEMPLE~Rogue~Spell~2~~Dirty Tricks~~Secret"
	description = "Secret: After your opponent casts a spell, draw 2 cards"
	name_CN = "邪恶计谋"
	trigBoard = Trig_DirtyTricks


class ShadowjewelerHanar(Minion):
	Class, race, name = "Rogue", "", "Shadowjeweler Hanar"
	mana, attack, health = 2, 1, 4
	index = "BLACK_TEMPLE~Rogue~Minion~2~1~4~~Shadowjeweler Hanar~Legendary"
	requireTarget, effects, description = False, "", "After you play a Secret, Discover a Secret from a different class"
	name_CN = "暗影珠宝师汉纳尔"
	trigBoard = Trig_ShadowjewelerHanar
	poolIdentifier = "Rogue Secrets"
	@classmethod
	def generatePool(cls, pools):
		classes, lists = [], []
		for Class in pools.Classes:
			secrets = [card for card in pools.ClassCards[Class] if card.race == "Secret"]
			if secrets:
				classes.append(Class + " Secrets")
				lists.append(secrets)
		return classes, lists

	def decidePools(self, Class2Exclude):
		classes = (Class for Class in ("Hunter", "Mage", "Paladin", "Rogue") if Class != Class2Exclude)
		return [self.rngPool(Class + " Secrets") for Class in classes]


class Akama(Minion):
	Class, race, name = "Rogue", "", "Akama"
	mana, attack, health = 3, 3, 4
	index = "BLACK_TEMPLE~Rogue~Minion~3~3~4~~Akama~Stealth~Deathrattle~Legendary"
	requireTarget, effects, description = False, "Stealth", "Stealth. Deathrattle: Shuffle 'Akama Prime' into your deck"
	name_CN = "阿卡玛"
	deathrattle = Death_Akama


class AkamaPrime(Minion):
	Class, race, name = "Rogue", "", "Akama Prime"
	mana, attack, health = 6, 6, 5
	index = "BLACK_TEMPLE~Rogue~Minion~6~6~5~~Akama Prime~Stealth~Legendary~Uncollectible"
	requireTarget, effects, description = False, "Stealth", "Permanently Stealthed"
	name_CN = "终极阿卡玛"
	
	def losesEffect(self, name, amount=1, removeEnchant=False, loseAllEffects=False):
		if name != "Stealth" or self.silenced:
			super().losesEffect(name, amount)


class GreyheartSage(Minion):
	Class, race, name = "Rogue", "", "Greyheart Sage"
	mana, attack, health = 3, 3, 3
	index = "BLACK_TEMPLE~Rogue~Minion~3~3~3~~Greyheart Sage~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: If you control a Stealth minion, draw 2 cards"
	name_CN = "暗心贤者"
	def effCanTrig(self):
		self.effectViable = False
		for minion in self.Game.minionsonBoard(self.ID):
			if minion.effects["Stealth"] > 0 or minion.effects["Temp Stealth"] > 0:
				self.effectViable = True
				break
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		controlStealthMinion = False
		for minion in self.Game.minionsonBoard(self.ID):
			if minion.effects["Stealth"] > 0 or minion.effects["Temp Stealth"] > 0:
				controlStealthMinion = True
				break
		if controlStealthMinion:
			self.Game.Hand_Deck.drawCard(self.ID)
			self.Game.Hand_Deck.drawCard(self.ID)
		

class CursedVagrant(Minion):
	Class, race, name = "Rogue", "", "Cursed Vagrant"
	mana, attack, health = 7, 7, 5
	index = "BLACK_TEMPLE~Rogue~Minion~7~7~5~~Cursed Vagrant~Deathrattle"
	requireTarget, effects, description = False, "", "Deathrattle: Summon a 7/5 Shadow with Stealth"
	name_CN = "被诅咒的 流浪者"
	deathrattle = Death_CursedVagrant

class CursedShadow(Minion):
	Class, race, name = "Rogue", "", "Cursed Shadow"
	mana, attack, health = 7, 7, 5
	index = "BLACK_TEMPLE~Rogue~Minion~7~7~5~~Cursed Shadow~Stealth~Uncollectible"
	requireTarget, effects, description = False, "Stealth", "Stealth"
	name_CN = "被诅咒的阴影"
	

"""Shaman Cards"""
class BogstrokClacker(Minion):
	Class, race, name = "Shaman", "", "Bogstrok Clacker"
	mana, attack, health = 3, 3, 3
	index = "BLACK_TEMPLE~Shaman~Minion~3~3~3~~Bogstrok Clacker~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Transform adjacent minions into random minions that cost (1) more"
	name_CN = "泥泽巨拳龙虾人"
	poolIdentifier = "1-Cost Minions to Summon"
	@classmethod
	def generatePool(cls, pools):
		return ["%d-Cost Minions to Summon" % cost for cost in pools.MinionsofCost.keys()], \
			   list(pools.MinionsofCost.values())
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.onBoard:
			minions, newMinions = self.Game.neighbors2(self)[0], []
			for minion in minions:
				newMinions.append(self.newEvolved(type(minion).mana, by=1, ID=self.ID))
			for minion, newMinion in zip(minions, newMinions):
				self.transform(minion, newMinion(self.Game, self.ID))


class LadyVashj(Minion):
	Class, race, name = "Shaman", "", "Lady Vashj"
	mana, attack, health = 3, 4, 3
	index = "BLACK_TEMPLE~Shaman~Minion~3~4~3~~Lady Vashj~Spell Damage~Deathrattle~Legendary"
	requireTarget, effects, description = False, "Spell Damage", "Spell Damage +1. Deathrattle: Shuffle 'Vashj Prime' into your deck"
	name_CN = "瓦斯琪女士"
	deathrattle = Death_LadyVashj

class VashjPrime(Minion):
	Class, race, name = "Shaman", "", "Vashj Prime"
	mana, attack, health = 7, 5, 4
	index = "BLACK_TEMPLE~Shaman~Minion~7~5~4~~Vashj Prime~Spell Damage~Battlecry~Legendary~Uncollectible"
	requireTarget, effects, description = False, "Spell Damage", "Spell Damage +1. Battlecry: Draw 3 spells. Reduce their Cost by (3)"
	name_CN = "终极瓦斯琪"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for _ in (0, 1, 2):
			spell, mana, entersHand = self.drawCertainCard(lambda card: card.category == "Spell")
			if not spell: break
			elif entersHand: ManaMod(spell, by=-3).applies()
		
		
class Marshspawn(Minion):
	Class, race, name = "Shaman", "Elemental", "Marshspawn"
	mana, attack, health = 3, 3, 4
	index = "BLACK_TEMPLE~Shaman~Minion~3~3~4~Elemental~Marshspawn~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: If you cast a spell last turn, Discover a spell"
	name_CN = "沼泽之子"
	poolIdentifier = "Shaman Spells"
	@classmethod
	def generatePool(cls, pools):
		return [Class+" Spells" for Class in pools.Classes], \
				[[card for card in pools.ClassCards[Class] if card.category == "Spell"] for Class in pools.Classes]
				
	def effCanTrig(self):
		cardsEachTurn = any(card.category == "Spell" for card in self.Game.Counters.cardsPlayedEachTurn[self.ID][-2])
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if any(card.category == "Spell" for card in self.Game.Counters.cardsPlayedEachTurn[self.ID][-2]):
			self.discoverandGenerate(Marshspawn, comment, lambda : self.rngPool(classforDiscover(self) + " Spells"))
		
		
class SerpentshrinePortal(Spell):
	Class, school, name = "Shaman", "Nature", "Serpentshrine Portal"
	requireTarget, mana, effects = True, 3, ""
	index = "BLACK_TEMPLE~Shaman~Spell~3~Nature~Serpentshrine Portal~Overload"
	description = "Deal 3 damage. Summon a random 3-Cost minion. Overload: (1)"
	name_CN = "毒蛇神殿传送门"
	overload = 1
	poolIdentifier = "3-Cost Minions to Summon"
	@classmethod
	def generatePool(cls, pools):
		return "3-Cost Minions to Summon", pools.MinionsofCost[3]

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = self.calcDamage(3)
			self.dealsDamage(target, damage)
			self.summon(numpyChoice(self.rngPool("3-Cost Minions to Summon"))(self.Game, self.ID))
		return target
		
		
class TotemicReflection(Spell):
	Class, school, name = "Shaman", "", "Totemic Reflection"
	requireTarget, mana, effects = True, 3, ""
	index = "BLACK_TEMPLE~Shaman~Spell~3~~Totemic Reflection"
	description = "Give a minion +2/2. If it's a Totem, summon a copy of it"
	name_CN = "图腾映像"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.giveEnchant(target, 2, 2, name=TotemicReflection)
			if "Totem" in target.race: self.summon(target.selfCopy(target.ID, self), position=target.pos+1)
		return target
		
		
class Torrent(Spell):
	Class, school, name = "Shaman", "Nature", "Torrent"
	requireTarget, mana, effects = True, 4, ""
	index = "BLACK_TEMPLE~Shaman~Spell~4~Nature~Torrent"
	description = "Deal 8 damage to a minion. Costs (3) less if you cast a spell last turn"
	name_CN = "洪流"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard
		
	def effCanTrig(self):
		self.effectViable = any(card.category == "Spell" for card in self.Game.Counters.cardsPlayedEachTurn[self.ID][-2])
		
	def selfManaChange(self):
		if self.inHand and any(card.category == "Spell" for card in self.Game.Counters.cardsPlayedEachTurn[self.ID][-2]):
			self.mana -= 3
			self.mana = max(self.mana, 0)
			
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = self.calcDamage(8)
			self.dealsDamage(target, damage)
		return target
		
		
class VividSpores(Spell):
	Class, school, name = "Shaman", "Nature", "Vivid Spores"
	requireTarget, mana, effects = False, 4, ""
	index = "BLACK_TEMPLE~Shaman~Spell~4~Nature~Vivid Spores"
	description = "Give your minions 'Deathrattle: Resummon this minion'"
	name_CN = "鲜活孢子"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.AOE_GiveEnchant(self.Game.minionsonBoard(self.ID), trig=Death_VividSpores, trigType="Deathrattle")
		

class BoggspineKnuckles(Weapon):
	Class, name, description = "Shaman", "Boggspine Knuckles", "After your hero attacks, transform your minions into ones that cost (1) more"
	mana, attack, durability, effects = 5, 3, 2, ""
	index = "BLACK_TEMPLE~Shaman~Weapon~5~3~2~Boggspine Knuckles"
	name_CN = "沼泽拳刺"
	trigBoard = Trig_BoggspineKnuckles
	poolIdentifier = "1-Cost Minions to Summon"
	@classmethod
	def generatePool(cls, pools):
		return ["%d-Cost Minions to Summon" % cost for cost in pools.MinionsofCost.keys()], \
			   list(pools.MinionsofCost.values())


class ShatteredRumbler(Minion):
	Class, race, name = "Shaman", "Elemental", "Shattered Rumbler"
	mana, attack, health = 5, 5, 6
	index = "BLACK_TEMPLE~Shaman~Minion~5~5~6~Elemental~Shattered Rumbler~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: If you cast a spell last turn, deal 2 damage to all other minions"
	name_CN = "破碎奔行者"
	
	def effCanTrig(self):
		cardsEachTurn = any(card.category == "Spell" for card in self.Game.Counters.cardsPlayedEachTurn[self.ID][-2])
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if any(card.category == "Spell" for card in self.Game.Counters.cardsPlayedEachTurn[self.ID][-2]):
			targets = self.Game.minionsonBoard(self.ID, self) + self.Game.minionsonBoard(3-self.ID)
			self.AOE_Damage(targets, [2]*len(targets))
		
		
class TheLurkerBelow(Minion):
	Class, race, name = "Shaman", "Beast", "The Lurker Below"
	mana, attack, health = 6, 6, 5
	index = "BLACK_TEMPLE~Shaman~Minion~6~6~5~Beast~The Lurker Below~Battlecry~Legendary"
	requireTarget, effects, description = True, "", "Battlecry: Deal 3 damage to an enemy minion, it dies, repeat on one of its neighbors"
	name_CN = "鱼斯拉"
	def targetExists(self, choice=0):
		return self.selectableEnemyMinionExists(choice)
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.ID != self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		#假设战吼触发时目标随从已经死亡并离场，则不会触发接下来的伤害
		#假设不涉及强制死亡
		if target:
			self.dealsDamage(target, 3)
			minion, direction = None, ''
			if target.onBoard and (target.health < 1 or target.dead):
				neighbors, dist = self.Game.neighbors2(target)
				if dist == 1:
					if numpyRandint(2): minion, direction = neighbors[1], 1
					else: minion, direction = neighbors[0], 0
				elif dist < 0: minion, direction = neighbors[0], 0
				elif dist == 2: minion, direction = neighbors[0], 1
			#开始循环
			while minion: #如果下个目标没有随从了，则停止循环
				self.dealsDamage(minion, 3)
				if minion.health < 1 or minion.dead:
					neighbors, dist = self.Game.neighbors2(minion)
					minion = None
					if direction:
						if dist > 0: minion = neighbors[2-dist]
						else: break
					else:
						if dist == 1 or dist == -1: minion = neighbors[0]
						else: break
				else: break
		return target
		

"""Warlock Cards"""
class ShadowCouncil(Spell):
	Class, school, name = "Warlock", "Fel", "Shadow Council"
	requireTarget, mana, effects = False, 1, ""
	index = "BLACK_TEMPLE~Warlock~Spell~1~Fel~Shadow Council"
	description = "Replace your hand with random Demons. Give them +2/+2"
	name_CN = "暗影议会"
	poolIdentifier = "Demons"
	@classmethod
	def generatePool(cls, pools):
		return "Demons", pools.MinionswithRace["Demon"]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		game, ID = self.Game, self.ID
		if ownHand := game.Hand_Deck.hands[self.ID]:
			pool = self.rngPool("Demons")
			demons = [card(game, ID) for card in numpyChoice(pool, len(ownHand), replace=True)]
			game.Hand_Deck.extractfromHand(None, self.ID, getAll=True, enemyCanSee=False)
			self.addCardtoHand(demons, ID)
			self.AOE_GiveEnchant(demons, 2, 2, name=ShadowCouncil, add2EventinGUI=False)
		
		
class UnstableFelbolt(Spell):
	Class, school, name = "Warlock", "Fel", "Unstable Felbolt"
	requireTarget, mana, effects = True, 1, ""
	index = "BLACK_TEMPLE~Warlock~Spell~1~Fel~Unstable Felbolt"
	description = "Deal 3 damage to an enemy minion and a random friendly one"
	name_CN = "不稳定的邪能箭"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = self.calcDamage(3)
			self.dealsDamage(target, damage)
			ownMinions = self.Game.minionsonBoard(self.ID)
			if ownMinions: self.dealsDamage(numpyChoice(ownMinions), damage)
		return target
		
		
class ImprisonedScrapImp(Minion_Dormantfor2turns):
	Class, race, name = "Warlock", "Demon", "Imprisoned Scrap Imp"
	mana, attack, health = 2, 3, 3
	index = "BLACK_TEMPLE~Warlock~Minion~2~3~3~Demon~Imprisoned Scrap Imp"
	requireTarget, effects, description = False, "", "Dormant for 2 turns. When this awakens, give all minions in your hand +2/+1"
	name_CN = "被禁锢的拾荒小鬼"
	
	def awakenEffect(self):
		self.AOE_GiveEnchant([card for card in self.Game.Hand_Deck.hands[self.ID] if card.category == "Minion"],
							2, 1, name=ImprisonedScrapImp, add2EventinGUI=False)
		
		
class KanrethadEbonlocke(Minion):
	Class, race, name = "Warlock", "", "Kanrethad Ebonlocke"
	mana, attack, health = 2, 3, 2
	index = "BLACK_TEMPLE~Warlock~Minion~2~3~2~~Kanrethad Ebonlocke~Deathrattle~Legendary"
	requireTarget, effects, description = False, "", "Your Demons cost (1) less. Deathrattle: Shuffle 'Kanrethad Prime' into your deck"
	name_CN = "坎雷萨德·埃伯洛克"
	aura, deathrattle = ManaAura_KanrethadEbonlocke, Death_KanrethadEbonlocke

class KanrethadPrime(Minion):
	Class, race, name = "Warlock", "Demon", "Kanrethad Prime"
	mana, attack, health = 8, 7, 6
	index = "BLACK_TEMPLE~Warlock~Minion~8~7~6~Demon~Kanrethad Prime~Battlecry~Legendary~Uncollectible"
	requireTarget, effects, description = False, "", "Battlecry: Summon 3 friendly Demons that died this game"
	name_CN = "终极坎雷萨德"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		demonsDied = [card for card in self.Game.Counters.minionsDiedThisGame[self.ID] if "Demon" in card.race]
		if numSummon := min(len(demonsDied), 3):
			self.summon([demon(self.Game, self.ID) for demon in numpyChoice(demonsDied, numSummon, replace=True)])


class Darkglare(Minion):
	Class, race, name = "Warlock", "Demon", "Darkglare"
	mana, attack, health = 3, 3, 4
	index = "BLACK_TEMPLE~Warlock~Minion~3~3~4~Demon~Darkglare"
	requireTarget, effects, description = False, "", "After your hero takes damage, refresh a Mana Crystals"
	name_CN = "黑眼"
	trigBoard = Trig_Darkglare		

		
class NightshadeMatron(Minion):
	Class, race, name = "Warlock", "Demon", "Nightshade Matron"
	mana, attack, health = 4, 5, 5
	index = "BLACK_TEMPLE~Warlock~Minion~4~5~5~Demon~Nightshade Matron~Rush~Battlecry"
	requireTarget, effects, description = False, "Rush", "Rush. Battlecry: Discard your highest Cost card"
	name_CN = "夜影主母"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if indices := pickHighestCostIndices(self.Game.Hand_Deck.hands[self.ID]):
			self.Game.Hand_Deck.discard(self.ID, numpyChoice(indices))
		
		
class TheDarkPortal(Spell):
	Class, school, name = "Warlock", "Fel", "The Dark Portal"
	requireTarget, mana, effects = False, 4, ""
	index = "BLACK_TEMPLE~Warlock~Spell~4~Fel~The Dark Portal"
	description = "Draw a minion. If you have at least 8 cards in hand, it costs (5) less"
	name_CN = "黑暗之门"
	def effCanTrig(self):
		self.effectViable = len(self.Game.Hand_Deck.hands[self.ID]) > 7
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		minion, mana, entersHand = self.drawCertainCard(lambda card: card.category == "Minion")
		if entersHand and len(self.Game.Hand_Deck.hands[self.ID]) > 7: ManaMod(minion, by=-5).applies()
		
		
class HandofGuldan(Spell):
	Class, school, name = "Warlock", "Shadow", "Hand of Gul'dan"
	requireTarget, mana, effects = False, 6, ""
	index = "BLACK_TEMPLE~Warlock~Spell~6~Shadow~Hand of Gul'dan"
	description = "When you play or discard this, draw 3 cards"
	name_CN = "古尔丹之手"
	def whenDiscarded(self):
		for _ in (0, 1, 2): self.Game.Hand_Deck.drawCard(self.ID)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for _ in (0, 1, 2): self.Game.Hand_Deck.drawCard(self.ID)
		
		
class KelidantheBreaker(Minion):
	Class, race, name = "Warlock", "", "Keli'dan the Breaker"
	mana, attack, health = 6, 3, 3
	index = "BLACK_TEMPLE~Warlock~Minion~6~3~3~~Keli'dan the Breaker~Battlecry~Legendary"
	requireTarget, effects, description = True, "", "Battlecry: Destroy a minion. If drawn this turn, instead destroy all minions except this one"
	name_CN = "击碎者克里丹"
	def needTarget(self, choice=0):
		return self.enterHandTurn < self.Game.numTurn
		
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target != self and target.onBoard
		
	def effCanTrig(self):
		self.effectViable = self.enterHandTurn >= self.Game.numTurn
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.enterHandTurn >= self.Game.numTurn:
			self.Game.kill(self, self.Game.minionsonBoard(self.ID, exclude=self) + self.Game.minionsonBoard(3 - self.ID))
		elif target: #Not just drawn this turn and target is designated
			self.Game.kill(self, target)
		return target


class EnhancedDreadlord(Minion):
	Class, race, name = "Warlock", "Demon", "Enhanced Dreadlord"
	mana, attack, health = 8, 5, 7
	index = "BLACK_TEMPLE~Warlock~Minion~8~5~7~Demon~Enhanced Dreadlord~Taunt~Deathrattle"
	requireTarget, effects, description = False, "Taunt", "Taunt. Deathrattle: Summon a 5/5 Dreadlord with Lifesteal"
	name_CN = "改进型恐惧魔王"
	deathrattle = Death_EnhancedDreadlord


class DesperateDreadlord(Minion):
	Class, race, name = "Warlock", "Demon", "Desperate Dreadlord"
	mana, attack, health = 5, 5, 5
	index = "BLACK_TEMPLE~Warlock~Minion~5~5~5~Demon~Desperate Dreadlord~Lifesteal~Uncollectible"
	requireTarget, effects, description = False, "Lifesteal", "Lifesteal"
	name_CN = "绝望的恐惧魔王"
	

"""Warrior Cards"""
class ImprisonedGanarg(Minion_Dormantfor2turns):
	Class, race, name = "Warrior", "Demon", "Imprisoned Gan'arg"
	mana, attack, health = 1, 2, 2
	index = "BLACK_TEMPLE~Warrior~Minion~1~2~2~Demon~Imprisoned Gan'arg"
	requireTarget, effects, description = False, "", "Dormant for 2 turns. When this awakens, equip a 3/2 Axe"
	name_CN = "被禁锢的 甘尔葛"
	def awakenEffect(self):
		self.equipWeapon(FieryWarAxe_Basic(self.Game, self.ID))
		
		
class SwordandBoard(Spell):
	Class, school, name = "Warrior", "", "Sword and Board"
	requireTarget, mana, effects = True, 1, ""
	index = "BLACK_TEMPLE~Warrior~Spell~1~~Sword and Board"
	description = "Deal 2 damage to a minion. Gain 2 Armor"
	name_CN = "剑盾猛攻"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.dealsDamage(target, self.calcDamage(2))
			self.giveHeroAttackArmor(self.ID, armor=2)
		return target
		
		
class CorsairCache(Spell):
	Class, school, name = "Warrior", "", "Corsair Cache"
	requireTarget, mana, effects = False, 2, ""
	index = "BLACK_TEMPLE~Warrior~Spell~2~~Corsair Cache"
	description = "Draw a weapon. Give it +1 Durability"
	name_CN = "海盗藏品"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		weapon, mana, entersHand = self.drawCertainCard(lambda card: card.category == "Weapon")
		if entersHand: self.giveEnchant(weapon, 0, 1, name=CorsairCache)
		
		
class Bladestorm(Spell):
	Class, school, name = "Warrior", "", "Bladestorm"
	requireTarget, mana, effects = False, 3, ""
	index = "BLACK_TEMPLE~Warrior~Spell~3~~Bladestorm"
	description = "Deal 1 damage to all minions. Repeat until one dies"
	name_CN = "剑刃风暴"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = self.calcDamage(1)
		for i in range(14):
			if targets := self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2):
				targets_damaged = self.AOE_Damage(targets, [damage] * len(targets))[0]
				if any(minion.health < 1 or minion.dead for minion in targets_damaged):
					break
			else: break
		
		
class BonechewerRaider(Minion):
	Class, race, name = "Warrior", "", "Bonechewer Raider"
	mana, attack, health = 3, 3, 3
	index = "BLACK_TEMPLE~Warrior~Minion~3~3~3~~Bonechewer Raider~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: If there is a damaged minion, gain +1/+1 and Rush"
	name_CN = "噬骨骑兵"
	
	def effCanTrig(self):
		self.effectViable = any(minion.dmgTaken > 0 for minion in self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2))

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if any(minion.dmgTaken > 0 for minion in self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)):
			self.giveEnchant(self, 1, 1, effGain="Rush", name=BonechewerRaider)
		
		
#不知道与博尔夫碎盾和Blur的结算顺序
class BulwarkofAzzinoth(Weapon):
	Class, name, description = "Warrior", "Bulwark of Azzinoth", "Whenever your hero would take damage, this loses 1 Durability instead"
	mana, attack, durability, effects = 3, 1, 4, ""
	index = "BLACK_TEMPLE~Warrior~Weapon~3~1~4~Bulwark of Azzinoth~Legendary"
	name_CN = "埃辛诺斯壁垒"
	trigBoard = Trig_BulwarkofAzzinoth


class WarmaulChallenger(Minion):
	Class, race, name = "Warrior", "", "Warmaul Challenger"
	mana, attack, health = 3, 1, 10
	index = "BLACK_TEMPLE~Warrior~Minion~3~1~10~~Warmaul Challenger~Battlecry"
	requireTarget, effects, description = True, "", "Battlecry: Choose an enemy minion. Battle it to the death!"
	name_CN = "战槌挑战者"
	
	def targetExists(self, choice=0):
		return self.selectableEnemyMinionExists(choice)
		
	def targetCorrect(self, target, choice=0):
		return target.category == "Minion" and target.ID != self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			#该随从会连续攻击那个目标直到一方死亡
			while self.onBoard and self.health > 0 and not self.dead and target.onBoard and target.health > 0 and not target.dead:
				self.Game.battle(self, target, verifySelectable=False, useAttChance=False, resolveDeath=False, resetRedirTrig=False)
		return target


class KargathBladefist(Minion):
	Class, race, name = "Warrior", "", "Kargath Bladefist"
	mana, attack, health = 4, 4, 4
	index = "BLACK_TEMPLE~Warrior~Minion~4~4~4~~Kargath Bladefist~Rush~Deathrattle~Legendary"
	requireTarget, effects, description = False, "Rush", "Rush. Deathrattle: Shuffle 'Kargath Prime' into your deck"
	name_CN = "卡加斯刃拳"
	deathrattle = Death_KargathBladefist


class KargathPrime(Minion):
	Class, race, name = "Warrior", "", "Kargath Prime"
	mana, attack, health = 8, 10, 10
	index = "BLACK_TEMPLE~Warrior~Minion~8~10~10~~Kargath Prime~Rush~Legendary~Uncollectible"
	requireTarget, effects, description = False, "Rush", "Rush. Whenever this attacks and kills a minion, gain 10 Armor"
	name_CN = "终极卡加斯"
	trigBoard = Trig_KargathPrime


class ScrapGolem(Minion):
	Class, race, name = "Warrior", "Mech", "Scrap Golem"
	mana, attack, health = 5, 4, 5
	index = "BLACK_TEMPLE~Warrior~Minion~5~4~5~Mech~Scrap Golem~Taunt~Deathrattle"
	requireTarget, effects, description = False, "Taunt", "Taunt. Deathrattle: Gain Armor equal to this minion's Attack"
	name_CN = "废铁魔像"
	deathrattle = Death_ScrapGolem


class BloodboilBrute(Minion):
	Class, race, name = "Warrior", "", "Bloodboil Brute"
	mana, attack, health = 7, 5, 8
	index = "BLACK_TEMPLE~Warrior~Minion~7~5~8~~Bloodboil Brute~Rush"
	requireTarget, effects, description = False, "Rush", "Rush. Costs (1) less for each damaged minion"
	name_CN = "沸血蛮兵"
	trigHand = Trig_BloodboilBrute		
	def selfManaChange(self):
		if self.inHand:
			numDamagedMinion = sum(minion.health < minion.health_max for minion in self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2))
			self.mana -= numDamagedMinion
			self.mana = max(0, self.mana)
			

""""""
Death_RustswornInitiate.cardType = RustswornInitiate
Death_TeronGorefiend.cardType = TeronGorefiend
Death_DisguisedWanderer.cardType = DisguisedWanderer
Death_RustswornCultist.cardType = RustswornCultist
Death_Alar.cardType = Alar
Death_DragonmawSkyStalker.cardType = DragonmawSkyStalker
Death_ScrapyardColossus.cardType = ScrapyardColossus
Death_FelSummoner.cardType = FelSummoner
Death_CoilfangWarlord.cardType = CoilfangWarlord
Death_ArchsporeMsshifn.cardType = ArchsporeMsshifn
Death_AugmentedPorcupine.cardType = AugmentedPorcupine
Death_ZixorApexPredator.cardType = ZixorApexPredator
Death_AstromancerSolarian.cardType = AstromancerSolarian
Death_Starscryer.cardType = Starscryer
Death_LibramofWisdom.cardType = LibramofWisdom
Death_MurgurMurgurgle.cardType = MurgurMurgurgle
Death_ReliquaryofSouls.cardType = ReliquaryofSouls
Death_Akama.cardType = Akama
Death_CursedVagrant.cardType = CursedVagrant
Death_LadyVashj.cardType = LadyVashj
Death_VividSpores.cardType = VividSpores
Death_KanrethadEbonlocke.cardType = KanrethadEbonlocke
Death_EnhancedDreadlord.cardType = EnhancedDreadlord
Death_KargathBladefist.cardType = KargathBladefist
Death_ScrapGolem.cardType = ScrapGolem
Trig_Evocation.cardType = Evocation

GameManaAura_KaelthasSunstrider.cardType = KaelthasSunstrider
GameManaAura_AldorAttendant.cardType = AldorAttendant
GameManaAura_AldorTruthseeker.cardType = AldorTruthseeker



Outlands_Cards = [
		#Neutral
		EtherealAugmerchant, GuardianAugmerchant, InfectiousSporeling, RocketAugmerchant, SoulboundAshtongue,
		BonechewerBrawler, ImprisonedVilefiend, MoargArtificer, RustswornInitiate, Impcaster, BlisteringRot, LivingRot,
		FrozenShadoweaver, OverconfidentOrc, TerrorguardEscapee, Huntress, TeronGorefiend, BurrowingScorpid,
		DisguisedWanderer, RustswornInquisitor, FelfinNavigator, Magtheridon, HellfireWarder, MaievShadowsong, Replicatotron,
		RustswornCultist, RustedDevil, Alar, AshesofAlar, RuststeedRaider, WasteWarden, DragonmawSkyStalker, Dragonrider,
		ScavengingShivarra, BonechewerVanguard, KaelthasSunstrider, SupremeAbyssal, ScrapyardColossus, FelcrackedColossus,
		#Demon Hunter
		FuriousFelfin, ImmolationAura, Netherwalker, FelSummoner, KaynSunfury, Metamorphosis, ImprisonedAntaen,
		SkullofGuldan, PriestessofFury, CoilfangWarlord, ConchguardWarlord, PitCommander,
		#Druid
		FungalFortunes, Ironbark, ArchsporeMsshifn, MsshifnPrime, FungalGuardian, FungalBruiser, FungalGargantuan, Bogbeam,
		ImprisonedSatyr, Germination, Overgrowth, GlowflySwarm, Glowfly, MarshHydra, YsielWindsinger,
		#Hunter
		Helboar, ImprisonedFelmaw, PackTactics, ScavengersIngenuity, AugmentedPorcupine, ZixorApexPredator, ZixorPrime,
		MokNathalLion, ScrapShot, BeastmasterLeoroxx, NagrandSlam, Clefthoof,
		#Mage
		Evocation, FontofPower, ApexisSmuggler, AstromancerSolarian, SolarianPrime, IncantersFlow, Starscryer,
		ImprisonedObserver, NetherwindPortal, ApexisBlast, DeepFreeze,
		#Paladin
		ImprisonedSungill, SungillStreamrunner, AldorAttendant, HandofAdal, MurgurMurgurgle, MurgurglePrime, LibramofWisdom,
		UnderlightAnglingRod, AldorTruthseeker, LibramofJustice, OverdueJustice, LadyLiadrin, LibramofHope, AncientGuardian,
		#Priest
		ImprisonedHomunculus, ReliquaryofSouls, ReliquaryPrime, Renew, DragonmawSentinel, SethekkVeilweaver, Apotheosis,
		DragonmawOverseer, PsycheSplit, SkeletalDragon, SoulMirror,
		#Rogue
		BlackjackStunner, Spymistress, Ambush, BrokenAmbusher, AshtongueSlayer, Bamboozle, DirtyTricks, ShadowjewelerHanar,
		Akama, AkamaPrime, GreyheartSage, CursedVagrant, CursedShadow,
		#Shaman
		BogstrokClacker, LadyVashj, VashjPrime, Marshspawn, SerpentshrinePortal, TotemicReflection, VividSpores,
		BoggspineKnuckles, ShatteredRumbler, Torrent, TheLurkerBelow,
		#Warlock
		ShadowCouncil, UnstableFelbolt, ImprisonedScrapImp, KanrethadEbonlocke, KanrethadPrime, Darkglare, NightshadeMatron,
		TheDarkPortal, HandofGuldan, KelidantheBreaker, EnhancedDreadlord, DesperateDreadlord,
		#Warrior
		ImprisonedGanarg, SwordandBoard, CorsairCache, Bladestorm, BonechewerRaider, BulwarkofAzzinoth, WarmaulChallenger,
		KargathBladefist, KargathPrime, ScrapGolem, BloodboilBrute,
]

Outlands_Cards_Collectible = [
		#Neutral
		EtherealAugmerchant, GuardianAugmerchant, InfectiousSporeling, RocketAugmerchant, SoulboundAshtongue,
		BonechewerBrawler, ImprisonedVilefiend, MoargArtificer, RustswornInitiate, BlisteringRot, FrozenShadoweaver,
		OverconfidentOrc, TerrorguardEscapee, TeronGorefiend, BurrowingScorpid, DisguisedWanderer, FelfinNavigator,
		Magtheridon, MaievShadowsong, Replicatotron, RustswornCultist, Alar, RuststeedRaider, WasteWarden,
		DragonmawSkyStalker, ScavengingShivarra, BonechewerVanguard, KaelthasSunstrider, SupremeAbyssal, ScrapyardColossus,
		#Demon Hunter
		FuriousFelfin, ImmolationAura, Netherwalker, FelSummoner, KaynSunfury, Metamorphosis, ImprisonedAntaen,
		SkullofGuldan, PriestessofFury, CoilfangWarlord, PitCommander,
		#Druid
		FungalFortunes, Ironbark, ArchsporeMsshifn, Bogbeam, ImprisonedSatyr, Germination, Overgrowth, GlowflySwarm,
		MarshHydra, YsielWindsinger,
		#Hunter
		Helboar, ImprisonedFelmaw, PackTactics, ScavengersIngenuity, AugmentedPorcupine, ZixorApexPredator, MokNathalLion,
		ScrapShot, BeastmasterLeoroxx, NagrandSlam,
		#Mage
		Evocation, FontofPower, ApexisSmuggler, AstromancerSolarian, IncantersFlow, Starscryer, ImprisonedObserver,
		NetherwindPortal, ApexisBlast, DeepFreeze,
		#Paladin
		ImprisonedSungill, AldorAttendant, HandofAdal, MurgurMurgurgle, LibramofWisdom, UnderlightAnglingRod,
		AldorTruthseeker, LibramofJustice, LadyLiadrin, LibramofHope,
		#Priest
		ImprisonedHomunculus, ReliquaryofSouls, Renew, DragonmawSentinel, SethekkVeilweaver, Apotheosis, DragonmawOverseer,
		PsycheSplit, SkeletalDragon, SoulMirror,
		#Rogue
		BlackjackStunner, Spymistress, Ambush, AshtongueSlayer, Bamboozle, DirtyTricks, ShadowjewelerHanar, Akama,
		GreyheartSage, CursedVagrant,
		#Shaman
		BogstrokClacker, LadyVashj, Marshspawn, SerpentshrinePortal, TotemicReflection, VividSpores, BoggspineKnuckles,
		ShatteredRumbler, Torrent, TheLurkerBelow,
		#Warlock
		ShadowCouncil, UnstableFelbolt, ImprisonedScrapImp, KanrethadEbonlocke, Darkglare, NightshadeMatron, TheDarkPortal,
		HandofGuldan, KelidantheBreaker, EnhancedDreadlord,
		#Warrior
		ImprisonedGanarg, SwordandBoard, CorsairCache, Bladestorm, BonechewerRaider, BulwarkofAzzinoth, WarmaulChallenger,
		KargathBladefist, ScrapGolem, BloodboilBrute,
]